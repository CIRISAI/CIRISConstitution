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
        self.families = OrderedDict((f["prefix"], f) for f in manifest["families"])


def _score(fam):
    segs = fam["segments"]
    literals = sum(1 for s in segs if s["class"] == "literal")
    wildcard = segs[-1]["class"] == "wildcard"
    return (literals, 0 if wildcard else 1, len(segs))


def _match_segments(fam, parts, rules):
    """Return (ok, binds, refusal) for `parts` against one family's segments."""
    segs = fam["segments"]
    binds = {}
    if segs[-1]["class"] == "wildcard":
        fixed = segs[:-1]
        if len(parts) < len(fixed) + 1:      # variadic: at least one further segment
            return False, {}, None
    else:
        fixed = segs
        if len(parts) != len(fixed):
            return False, {}, None
    refusal = None
    for seg, got in zip(fixed, parts):
        cls = seg["class"]
        if cls == "literal":
            if seg["segment"] != got:
                return False, {}, None        # not this family at all
            continue
        name = seg["segment"].strip("{}")
        if not got:
            refusal = refusal or rules.tokens["case_malformed"]
        elif seg["segment"] == "{version}":
            if not rules.version.match(got):
                refusal = refusal or rules.tokens["case_malformed"]
        elif cls == "vocab":
            if not rules.vocab.match(got):
                refusal = refusal or rules.tokens["case_malformed"]
            else:
                values = seg.get("values")
                if values and not seg.get("open", False) and got not in values:
                    refusal = refusal or rules.tokens["vocab_value_unregistered"]
        elif cls == "hex":
            if not re.match(HEX_PATTERN, got):
                refusal = refusal or rules.tokens["case_malformed"]
        # external / value: verbatim, case-preserved
        binds[name] = got
    tail = parts[len(fixed):]
    for got in tail:                          # segments below a variadic tail
        if not got or not rules.vocab.match(got):
            refusal = refusal or rules.tokens["case_malformed"]
    if tail:
        binds["*"] = ":".join(tail)
    return True, binds, refusal


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

    versioned = bool(rules.version.match(parts[-1]))
    candidates = []                            # (score, prefix, binds, refusal, used_tail)
    for prefix, fam in rules.families.items():
        ends_version = fam["segments"][-1]["segment"] == "{version}"
        if ends_version or not versioned:
            # as written: a row ending in {version} consumes the version itself;
            # an unversioned dimension is matched whole (and refused below if required)
            ok, binds, refusal = _match_segments(fam, parts, rules)
            if ok:
                candidates.append((_score(fam), prefix, binds, refusal, ends_version))
        elif len(parts) > 1:
            # the trailing version segment is the version — never a value or a wildcard tail
            ok, binds, refusal = _match_segments(fam, parts[:-1], rules)
            if ok:
                candidates.append((_score(fam), prefix, binds, refusal, True))
    if not candidates:
        return None, {}, None
    candidates.sort(key=lambda c: c[0], reverse=True)
    score, prefix, binds, refusal, has_version = candidates[0]
    fam = rules.families[prefix]
    if refusal:
        return prefix, binds, refusal
    # closed reserved leaves: a wildcard family only admits the leaves CC names
    if fam["segments"][-1]["class"] == "wildcard" and fam.get("leaves_closed"):
        leaf_parts = parts[:-1] if (versioned and has_version) else parts
        leaf = ":".join(leaf_parts)
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
            out.append("v1" if name == "{version}" else (values[0] if values else SAMPLE["vocab"]))
        else:
            out.append(SAMPLE[cls])
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
        if not exempt and fam["segments"][-1]["segment"] != "{version}":
            add(instantiate(fam, with_version=False), prefix, rules.tokens["missing_version_segment"],
                "the trailing version segment is mandatory (R3 version_segment)")
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
        if got != v["family"] or refusal != v["refusal"]:
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
                             "expected (family, refusal) per dimension"),
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
