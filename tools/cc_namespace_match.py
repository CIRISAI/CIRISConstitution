#!/usr/bin/env python3
"""
cc_namespace_match.py — the CC dimension-grammar REFERENCE MATCHER and its vectors.

CC 3.1.7 R3 (CIRISConstitution#112): a wire dimension is matched to a registry
family by ONE rule, carried as data in manifests/namespace_registry.json:

  * segments split on ':' and compare byte-exactly (no consumer case-folds);
  * a `literal` segment must equal the row's stem; `vocab` must match
    _meta.case_rule.vocab_pattern and, when the row enumerates a CLOSED value
    set, be one of those values; `external` / `value` are verbatim; `hex` is
    lowercase hex; a trailing `*` is VARIADIC (one or more further segments);
  * every scored dimension carries ONE trailing version segment matching
    _meta.case_rule.version_segment.pattern AFTER the family's own segments
    (the family's `{version}` segment, where a row has one, IS that segment);
    families named in version_segment.exempt carry none;
  * a leaf under a reserved family whose `leaves_closed` is true must be one
    of that family's `leaves`;
  * the most specific matching family wins: most literal segments, then a
    non-wildcard over a wildcard, then the longer prefix — the same
    longest-prefix discipline persist's lookup uses.

Refusal tokens are the manifest's (`_meta.case_rule.refusal_tokens`), never
bespoke. Every consumer (persist, edge, server, verify, client) replays
manifests/namespace_match_vectors.json against its own matcher, so a matcher
that drifts from this one fails a build, not a card.

stdlib only.  Run:
  python3 tools/cc_namespace_match.py --self-test        # round-trip gate (CI)
  python3 tools/cc_namespace_match.py --write-vectors    # regenerate the vectors
  python3 tools/cc_namespace_match.py --check-vectors    # vectors match the manifest
  python3 tools/cc_namespace_match.py <dimension> [...]  # resolve by hand
"""
import json, os, re, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "..", "manifests", "namespace_registry.json")
VECTORS = os.path.join(HERE, "..", "manifests", "namespace_match_vectors.json")

HEX_PATTERN = r"^[0-9a-f]+$"


def load_manifest(path=MANIFEST):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


class Rules:
    """The grammar, read from the manifest — nothing here is hard-coded twice."""

    def __init__(self, manifest):
        meta = manifest["_meta"]
        cr = meta["case_rule"]
        self.vocab = re.compile(cr["vocab_pattern"])
        self.literal = re.compile(cr["literal_pattern"])
        self.private = meta["private_use_prefix"]
        vs = cr["version_segment"]
        self.version = re.compile(vs["pattern"])
        self.version_required = bool(vs.get("required", True))
        self.exempt = set(vs.get("exempt", []))
        self.tokens = cr["refusal_tokens"]
        self.external = {name: re.compile(spec["pattern"]) for name, spec in cr.get("external_standards", {}).items()
                         if spec.get("pattern")}
        self.families = OrderedDict((f["prefix"], f) for f in manifest["families"])


def _score(fam):
    segs = fam["segments"]
    literals = sum(1 for s in segs if s["class"] == "literal")
    wildcard = segs[-1]["class"] == "wildcard"
    return (literals, 0 if wildcard else 1, len(segs))


VERSION_LIKE = re.compile(r"^[vV][0-9]+(\.[0-9]+)*$")


def _check_seg(seg, got, rules):
    """The refusal a single placeholder value earns under its class, or None."""
    cls = seg["class"]
    name = seg["segment"].strip("{}")
    if not got:
        return rules.tokens["case_malformed"]
    pattern = seg.get("pattern")
    if seg["segment"] == "{version}":
        return None if rules.version.match(got) else rules.tokens["case_malformed"]
    if cls == "vocab":
        if not rules.vocab.match(got):
            return rules.tokens["case_malformed"]
        values = seg.get("values")
        if values and not seg.get("open", False) and got not in values:
            return rules.tokens["vocab_value_unregistered"]
        return None
    if cls == "hex":
        return None if re.match(pattern or HEX_PATTERN, got) else rules.tokens["case_malformed"]
    if cls == "external":
        pat = re.compile(pattern) if pattern else rules.external.get(name)
        return None if (not pat or pat.match(got)) else rules.tokens["case_malformed"]
    # value: verbatim, case-preserved — unless the row pins a shape (a numeric field)
    if pattern and not re.match(pattern, got):
        return rules.tokens["case_malformed"]
    return None


def _match_segments(fam, parts, rules):
    """Return (ok, binds, refusal) for `parts` against one family's segments.

    A `multi` placeholder spans one or more segments (`{source}` = `registry:abc`);
    each sub-segment obeys the placeholder's class. A trailing `*` is variadic.
    """
    segs = fam["segments"]
    wildcard = segs[-1]["class"] == "wildcard"
    fixed = segs[:-1] if wildcard else segs
    multi = [i for i, s in enumerate(fixed) if s.get("multi")]
    if wildcard:
        if len(parts) < len(fixed) + 1:      # variadic: at least one further segment
            return False, {}, None
        extra = 0
    elif multi:
        extra = len(parts) - len(fixed)      # the surplus belongs to the multi placeholder
        if extra < 0:
            return False, {}, None
    elif len(parts) != len(fixed):
        return False, {}, None
    else:
        extra = 0
    binds, refusal, pi = {}, None, 0
    for i, seg in enumerate(fixed):
        if multi and i == multi[0]:
            span = parts[pi:pi + 1 + extra]
            pi += 1 + extra
            for got in span:
                # a version-like sub-segment is a stray version tail, never part of the value
                refusal = refusal or _check_seg(seg, got, rules) or (
                    rules.tokens["case_malformed"] if VERSION_LIKE.match(got) else None)
            binds[seg["segment"].strip("{}")] = ":".join(span)
            continue
        got = parts[pi]
        pi += 1
        if seg["class"] == "literal":
            if seg["segment"] != got:
                return False, {}, None        # not this family at all
            continue
        refusal = refusal or _check_seg(seg, got, rules)
        binds[seg["segment"].strip("{}")] = got
    tail = parts[pi:]
    for got in tail:                          # segments below a variadic tail
        # a version-like token here is an uppercase or duplicated version tail — the
        # real version was stripped before matching — so it is malformed, never a leaf
        if not got or not rules.vocab.match(got) or VERSION_LIKE.match(got):
            refusal = refusal or rules.tokens["case_malformed"]
    if tail:
        binds["*"] = ":".join(tail)
    return True, binds, refusal


def _resolve(rules, parts):
    """Best candidate for `parts`: (prefix, binds, refusal, has_version) or None."""
    versioned = bool(rules.version.match(parts[-1]))
    candidates = []
    for prefix, fam in rules.families.items():
        ends_version = fam["segments"][-1]["segment"] == "{version}"
        if ends_version and not versioned:
            # recognise the family by its other segments (missing tail), and also as
            # written (a malformed tail such as `V1` is then refused, not open vocabulary)
            headless = dict(fam, segments=fam["segments"][:-1])
            ok, binds, refusal = _match_segments(headless, parts, rules)
            if ok:
                candidates.append((_score(fam), prefix, binds, refusal, False))
            ok, binds, refusal = _match_segments(fam, parts, rules)
            if ok:
                candidates.append((_score(fam), prefix, binds, refusal, True))
        elif ends_version or not versioned:
            ok, binds, refusal = _match_segments(fam, parts, rules)
            if ok:
                candidates.append((_score(fam), prefix, binds, refusal, ends_version))
        elif len(parts) > 1:
            # the trailing version segment is the version — never a value or a wildcard tail
            ok, binds, refusal = _match_segments(fam, parts[:-1], rules)
            if ok:
                candidates.append((_score(fam), prefix, binds, refusal, True))
    if not candidates and versioned:
        # the last segment is version-SHAPED but nothing matched with it stripped: it may
        # be a VALUE that happens to look like a version (`config:v1` = `config:{scope}`
        # with the tail omitted). Read it as an unversioned instance so the family is
        # recognised and refused for the missing tail, never called open vocabulary.
        for prefix, fam in rules.families.items():
            if fam["segments"][-1]["segment"] == "{version}":
                continue
            ok, binds, refusal = _match_segments(fam, parts, rules)
            if ok:
                candidates.append((_score(fam), prefix, binds, refusal, False))
    if not candidates:
        return None
    candidates.sort(key=lambda c: c[0], reverse=True)
    _score_, prefix, binds, refusal, has_version = candidates[0]
    return prefix, binds, refusal, has_version


def _detect_malformed(rules, parts):
    """A dimension no row claims may still be a MALFORMED form of a registered family —
    a case-mutated stem, an uppercase or duplicated version tail. Fold and strip only
    to DETECT, never to admit; return the family it mutates, or None."""
    variants = []
    low = [p.lower() for p in parts]
    if low != parts:
        variants.append(low)
    if len(parts) > 1 and VERSION_LIKE.match(parts[-1]):
        variants.append(parts[:-1])
        variants.append(low[:-1])
        if len(parts) > 2 and VERSION_LIKE.match(parts[-2]):
            variants.append(parts[:-2])
            variants.append(low[:-2])
    for v in variants:
        hit = _resolve(rules, v)
        if hit:
            return hit[0]
    return None


def match_family(manifest_or_rules, dimension):
    """Resolve a wire dimension.  Returns (family_prefix|None, binds, refusal|None).

    A refusal names the manifest token; a None family with no refusal means the
    dimension is in the open vocabulary this Part leaves open (no row claims it).
    """
    rules = manifest_or_rules if isinstance(manifest_or_rules, Rules) else Rules(manifest_or_rules)
    if not dimension or dimension != dimension.strip():
        return None, {}, rules.tokens["case_malformed"]
    if dimension.startswith(rules.private):
        return None, {}, rules.tokens["private_use_not_federatable"]
    parts = dimension.split(":")
    if any(p == "" for p in parts):
        return None, {}, rules.tokens["case_malformed"]
    hit = _resolve(rules, parts)
    if hit is None:
        mutated = _detect_malformed(rules, parts)
        if mutated:
            return mutated, {}, rules.tokens["case_malformed"]
        return None, {}, None
    prefix, binds, refusal, has_version = hit
    fam = rules.families[prefix]
    if refusal:
        return prefix, binds, refusal
    versioned = bool(rules.version.match(parts[-1]))
    # closed reserved leaves: a wildcard family only admits the leaves CC names
    if fam["segments"][-1]["class"] == "wildcard" and fam.get("leaves_closed"):
        leaf_parts = parts[:-1] if (versioned and has_version) else parts
        ok_leaf = any(_match_segments(rules.families[l], leaf_parts, rules)[0]
                      for l in fam.get("leaves", []) if l in rules.families)
        if not ok_leaf:
            return prefix, binds, rules.tokens["family_unregistered"]
    if rules.version_required and prefix not in rules.exempt and not has_version:
        return prefix, binds, rules.tokens["missing_version_segment"]
    if has_version:
        binds = dict(binds, version=parts[-1])
    return prefix, binds, None


# ---- vectors ------------------------------------------------------------------

SAMPLE = {"vocab": "sample", "external": "USD", "value": "id1", "hex": "ab12"}
SAMPLE_EXTERNAL = {"currency": "USD", "lang_code": "en-US", "rating": "PG-13", "unit": "USD"}


def instantiate(fam, with_version=True):
    """A class-conformant sample dimension for a family."""
    out = []
    for seg in fam["segments"]:
        cls, name = seg["class"], seg["segment"]
        if cls == "literal":
            out.append(name)
        elif cls == "wildcard":
            out.append("leaf")
        elif cls == "vocab":
            values = seg.get("values")
            tok = values[0] if values else ("v1" if name == "{version}" else SAMPLE["vocab"])
            out.append(tok + ":sub" if seg.get("multi") else tok)
        elif cls == "external":
            out.append(SAMPLE_EXTERNAL.get(name.strip("{}"), SAMPLE["external"]))
        elif seg.get("pattern"):
            out.append("42" if "0-9" in seg["pattern"] and "a-f" not in seg["pattern"]
                       else ("abcdef0123456789" * 4) if "{64}" in seg["pattern"] else SAMPLE[cls])
        else:
            tok = SAMPLE[cls]
            out.append(tok + ":id2" if seg.get("multi") else tok)
    if with_version and fam["segments"][-1]["segment"] != "{version}":
        out.append("v1")
    return ":".join(out)


def generate_vectors(manifest):
    rules = Rules(manifest)
    vectors = []

    def add(dim, expect_family, expect_refusal, why):
        vectors.append(OrderedDict([("dimension", dim), ("family", expect_family),
                                    ("refusal", expect_refusal), ("why", why)]))

    for prefix, fam in rules.families.items():
        exempt = prefix in rules.exempt
        closed = fam.get("leaves_closed") and fam["segments"][-1]["class"] == "wildcard"
        if closed:
            for leaf in fam.get("leaves", []):
                if leaf in rules.families:
                    lf = rules.families[leaf]
                    add(instantiate(lf, with_version=leaf not in rules.exempt), leaf, None,
                        "closed reserved leaf resolves to its own row")
            add(instantiate(fam, with_version=True), prefix, rules.tokens["family_unregistered"],
                "an unlisted leaf under a closed reserved family is unregistered (R2(b))")
            continue
        add(instantiate(fam, with_version=not exempt), prefix, None,
            "instantiated sample resolves to its row" + (" (exempt: no version tail)" if exempt else ""))
        if exempt and fam["segments"][-1]["segment"] != "{version}":
            add(instantiate(fam, with_version=True), prefix, None,
                "an exempt family tolerates a version tail (never required)")
        if not exempt:
            parts = instantiate(fam).split(":")
            add(":".join(parts[:-1] + [parts[-1].upper()]), prefix, rules.tokens["case_malformed"],
                "an uppercase version tail is malformed, not open vocabulary")
            add(":".join(parts + ["v2"]), prefix, rules.tokens["case_malformed"],
                "a duplicated version tail is malformed, not open vocabulary")
            if fam["segments"][0]["class"] == "literal":
                add(":".join([parts[0].capitalize()] + parts[1:]), prefix, rules.tokens["case_malformed"],
                    "a case-mutated registered stem is malformed, not open vocabulary")
        if not exempt and fam["segments"][-1]["segment"] != "{version}":
            add(instantiate(fam, with_version=False), prefix, rules.tokens["missing_version_segment"],
                "the trailing version segment is mandatory (R3 version_segment)")
        elif not exempt:
            parts = instantiate(fam).split(":")[:-1]
            add(":".join(parts), prefix, rules.tokens["missing_version_segment"],
                "a row ending in {version} still refuses an input without the version segment")
        for i, seg in enumerate(fam["segments"]):
            if seg["class"] == "external" and seg["segment"].strip("{}") in rules.external:
                parts = instantiate(fam, with_version=not exempt).split(":")
                low = parts[i].lower()
                if low != parts[i] and not rules.external[seg["segment"].strip("{}")].match(low):
                    parts[i] = low
                    add(":".join(parts), prefix, rules.tokens["case_malformed"],
                        "an external token outside its standard's canonical syntax is malformed (USD, not usd)")
                break
        # a vocab segment in the wrong case
        for i, seg in enumerate(fam["segments"]):
            if seg["class"] == "vocab" and seg["segment"] != "{version}":
                parts = instantiate(fam, with_version=not exempt).split(":")
                parts[i] = parts[i].upper()
                add(":".join(parts), prefix, rules.tokens["case_malformed"],
                    "a vocab segment carrying uppercase is malformed, never folded (R3)")
                break
        for i, seg in enumerate(fam["segments"]):
            if seg["class"] == "vocab" and seg.get("values") and not seg.get("open", False):
                parts = instantiate(fam, with_version=not exempt).split(":")
                parts[i] = "not_a_listed_value"
                add(":".join(parts), prefix, rules.tokens["vocab_value_unregistered"],
                    "a value outside a closed enumeration is unregistered")
                break
    add(rules.private + "anything:v1", None, rules.tokens["private_use_not_federatable"],
        "the Private Use prefix never admits at federation tier (R2)")
    add("no_such_family:leaf:v1", None, None, "open vocabulary: no row claims it, no refusal")
    return vectors


def self_test(manifest):
    """The round-trip gate: every family's sample resolves to itself and nothing else."""
    rules = Rules(manifest)
    problems = []
    for prefix, fam in rules.families.items():
        if fam.get("leaves_closed") and fam["segments"][-1]["class"] == "wildcard":
            continue
        dim = instantiate(fam, with_version=prefix not in rules.exempt)
        got, _, refusal = match_family(rules, dim)
        if got != prefix or refusal:
            problems.append("%s: sample %r resolved to %r (refusal %r)" % (prefix, dim, got, refusal))
    for v in generate_vectors(manifest):
        got, _, refusal = match_family(rules, v["dimension"])
        # on a malformed dimension the REFUSAL is the contract; the family it is judged
        # to mutate (a closed leaf or its wildcard parent) is best-effort attribution
        family_ok = (got == v["family"]) or (v["refusal"] == rules.tokens["case_malformed"] and got is not None)
        if not family_ok or refusal != v["refusal"]:
            problems.append("vector %r: expected (%r, %r) got (%r, %r)"
                            % (v["dimension"], v["family"], v["refusal"], got, refusal))
    return problems


def main(argv):
    manifest = load_manifest()
    if argv[:1] == ["--self-test"]:
        problems = self_test(manifest)
        if problems:
            sys.stderr.write("namespace matcher round-trip FAILED (%d):\n  %s\n"
                             % (len(problems), "\n  ".join(problems)))
            return 1
        print("namespace matcher round-trip OK: %d families, %d vectors"
              % (len(manifest["families"]), len(generate_vectors(manifest))))
        return 0
    if argv[:1] in (["--write-vectors"], ["--check-vectors"]):
        out = OrderedDict([
            ("_meta", OrderedDict([
                ("cc_version", manifest["_meta"]["cc_version"]),
                ("registry_sha256", manifest["_meta"].get("registry_sha256")),
                ("generator", "tools/cc_namespace_match.py"),
                ("contract", "every consumer replays these against its own matcher; "
                             "expected (family, refusal) per dimension — on a refusal of "
                             "namespace_dimension_case_malformed the refusal is the contract and "
                             "the family is best-effort attribution"),
            ])),
            ("vectors", generate_vectors(manifest)),
        ])
        text = json.dumps(out, indent=2) + "\n"
        if argv[0] == "--check-vectors":
            cur = open(VECTORS, encoding="utf-8").read() if os.path.exists(VECTORS) else ""
            if cur != text:
                sys.stderr.write("namespace_match_vectors.json is stale — run --write-vectors\n")
                return 1
            print("vectors current")
            return 0
        with open(VECTORS, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s (%d vectors)" % (os.path.relpath(VECTORS, os.path.join(HERE, "..")), len(out["vectors"])))
        return 0
    rules = Rules(manifest)
    for dim in argv:
        fam, binds, refusal = match_family(rules, dim)
        print("%-50s -> %s  binds=%s  refusal=%s" % (dim, fam, binds, refusal))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
