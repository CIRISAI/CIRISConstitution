#!/usr/bin/env python3
"""
cc_family_select.py — the REFERENCE EVALUATOR of the family model's selector arms, and its vectors.

The `count`, `authorship` and `second_signers` cells of manifests/family_model.json (built by
tools/build_family_model.py from formal/derivation/count_text.tsv and authorship_text.tsv) are
written as selector arms. This file reads them by ONE rule:

  * an arm is `*` or tests joined by ` & `; a test is `key=v1|v2|...`;
  * `count` and `authorship` arms are read in order and the first whose tests all hold decides;
    `second_signers` entries are read each on its own, an entry with no `when` always applying;
  * the keys and how each is read from a row:
      leaf      the values bound to the family's non-literal segments, joined by ':', the
                trailing version segment stripped (a `{version}` segment is that segment). It is
                bound by tools/cc_namespace_match.py against the family the cell belongs to, so
                under `accord:*` the dimension `accord:lifecycle:confirmed:v1` has the leaf
                `lifecycle:confirmed`. A selector value segment `{name}` matches any one leaf
                segment; the leaf and the value have the same number of segments. A
                multi-segment value class binds all its segments into the leaf.
      verb      the row's verb, one of the family model's verbs vocabulary. CALLER-SUPPLIED: no
                sentence maps a row's members to a verb.
      identity  the `identity_type` set of the identity the row concerns (CC 3.1.3, CC 3.3.6.4:
                "an occurrence of a user self"); the test holds when the set contains a value.
                CALLER-SUPPLIED: the set is read from a held key record, not from the row.
      group     the `cohort_scope` of the group the row is about, its record's discriminator
                (CC 4.4.3.12): family | community | affiliations. CALLER-SUPPLIED: it is read
                from the group's record, not from the row.
      seats     the number of deciding seats of that group at the head the row names
                (CC 4.4.3.12); the token `one` is 1. CALLER-SUPPLIED, an integer.
      act       how the row is signed: `group` when it is the act of a roster under its
                consensus_protocol, several statements over one payload (CC 2.6.1.9), `own` when
                it is one statement by the author. CALLER-SUPPLIED: it is never a payload member;
                the reader derives it from the statements the row carries and the roster they are
                counted over (CC 2.6.1.3).
  * an `authorship` value is authored, subject, counted or gap. `subject` is an authored row whose
    author is the attested key: it admits a statement only when its `iss` is the CWT `sub`
    (CC 4.5.9: "attesting_key_id is the subject"). It is positive only: no value asks that `iss`
    differ from `sub`. The two are read from the statement, not from a selector key: `iss` and
    `sub` in the context, an absent one answering UNKNOWN;
  * a test on a key the caller did not supply answers UNKNOWN. An arm is false when any test is
    false, else unknown when any test is unknown, else it holds (a conjunction with one false
    term is false whatever the others read). An unknown arm before the deciding arm makes the
    answer `unknown`, since order decides; an unknown arm after it changes nothing.
  * a cell whose arms all read false gives no answer: `null` here (count of `content_class:{class}`
    outside `reported`, of `accord:lifecycle:{kind}` outside its two kinds). A cell the model marks
    `gap` answers `gap`; a cell with no arms answers its own value.

Every consumer (verify above all) replays manifests/family_select_vectors.json against its own
evaluator. manifests/family_authorship.json is the canonical extract of the `authorship` and
`second_signers` cells, pinned to the model by its SHA-256, for a consumer that vendors those
cells without the whole model.

stdlib only.  Run:
  python3 tools/cc_family_select.py --self-test       # replay the vectors and the deliberate breaks (CI)
  python3 tools/cc_family_select.py --write-vectors   # regenerate the vectors and the extract
  python3 tools/cc_family_select.py --check           # both generated files are current
  python3 tools/cc_family_select.py FAMILY DIMENSION [key=value ...]   # resolve by hand
"""
import hashlib, itertools, json, os, re, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cc_namespace_match as ns  # noqa: E402

ROOT = os.path.join(HERE, "..")
MODEL = os.path.join(ROOT, "manifests", "family_model.json")
REGISTRY = os.path.join(ROOT, "manifests", "namespace_registry.json")
VECTORS = os.path.join(ROOT, "manifests", "family_select_vectors.json")
EXTRACT = os.path.join(ROOT, "manifests", "family_authorship.json")

KEYS = ("leaf", "verb", "identity", "group", "seats", "act")
CALLER_KEYS = ("verb", "identity", "group", "seats", "act")
SEATS_TOKENS = {"one": 1}
GROUP_VALUES = ("family", "community", "affiliations")
ACT_VALUES = ("group", "own")
CELLS = ("count", "authorship", "second_signers")
UNKNOWN = "unknown"
AUTHOR_KEYS = ("iss", "sub")   # read from the statement for an authorship value that compares them
TEST = re.compile(r"([a-z]+)=([a-z_:{}]+(?:\|[a-z_:{}]+)*)")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---- the evaluator --------------------------------------------------------------

def parse_selector(sel):
    """[(key, [values])] for a selector; [] for `*`. Raises ValueError on a test it cannot read."""
    if sel == "*":
        return []
    out = []
    for t in sel.split(" & "):
        m = TEST.fullmatch(t)
        if not m or m.group(1) not in KEYS:
            raise ValueError("%r is not a test on one of %s" % (t, ", ".join(KEYS)))
        key, values = m.group(1), m.group(2).split("|")
        if key == "seats" and any(v not in SEATS_TOKENS for v in values):
            raise ValueError("seats=%s: a seat count token is one of %s" % (m.group(2), ", ".join(SEATS_TOKENS)))
        if key == "group" and any(v not in GROUP_VALUES for v in values):
            raise ValueError("group=%s: a group is one of %s" % (m.group(2), ", ".join(GROUP_VALUES)))
        if key == "act" and any(v not in ACT_VALUES for v in values):
            raise ValueError("act=%s: an act is one of %s" % (m.group(2), ", ".join(ACT_VALUES)))
        out.append((key, values))
    return out


def leaf_holds(leaf, value):
    """`value` names `leaf`: same segment count, each segment equal or a `{name}` wildcard."""
    a, b = leaf.split(":") if leaf else [], value.split(":")
    return len(a) == len(b) and all(y == x or (y.startswith("{") and y.endswith("}")) for x, y in zip(a, b))


def test_holds(key, values, ctx):
    """True, False or UNKNOWN for one test against a row's context."""
    got = ctx.get(key)
    if got is None:
        return UNKNOWN
    if key == "leaf":
        return any(leaf_holds(got, v) for v in values)
    if key == "identity":
        return bool(set(got) & set(values))
    if key == "seats":
        return any(int(got) == SEATS_TOKENS[v] for v in values)
    return got in values


def arm_holds(sel, ctx):
    """True, False or UNKNOWN: false if any test is false, else unknown if any is unknown."""
    res = [test_holds(k, v, ctx) for k, v in parse_selector(sel)]
    if False in res:
        return False
    if UNKNOWN in res:
        return UNKNOWN
    return True


def decide(cell_arms, ctx):
    """The index of the deciding arm, None when no arm holds, or UNKNOWN."""
    for i, arm in enumerate(cell_arms):
        h = arm_holds(arm["when"], ctx)
        if h is UNKNOWN:
            return UNKNOWN
        if h:
            return i
    return None


def arm_value(arm):
    return arm["doors"] if "doors" in arm else arm["value"]


def evaluate(cell_arms, row_ctx):
    """The deciding arm's value, None when no arm holds, or 'unknown'."""
    i = decide(cell_arms, row_ctx)
    if i is UNKNOWN or i is None:
        return i
    return arm_value(cell_arms[i])


def second_signers(entries, ctx):
    """[{role, member}] whose `when` holds (no `when`: always), or UNKNOWN if any entry's is unknown."""
    out = []
    for e in entries:
        h = arm_holds(e.get("when", "*"), ctx)
        if h is UNKNOWN:
            return UNKNOWN
        if h:
            out.append(OrderedDict([("role", e["role"]), ("member", e["member"])]))
    return out


def author_admits(value, ctx):
    """Whether an authorship value admits the statement in `ctx`: True, False or UNKNOWN; None when the value
    compares nothing. `subject` holds when the statement's `iss` is the CWT `sub`."""
    if value != "subject":
        return None
    if ctx.get("iss") is None or ctx.get("sub") is None:
        return UNKNOWN
    return ctx["iss"] == ctx["sub"]


def voice_admits(roles, voice):
    """Whether a statement offered in the role `voice` is accepted besides the author's: True when the second_signers
    answer names that role, False when it does not, UNKNOWN when the answer is unknown."""
    if roles == UNKNOWN:
        return UNKNOWN
    return any(r["role"] == voice for r in roles)


def cell_answer(cell, name, ctx):
    """(answer, decided_by) for one cell of a family row."""
    if cell.get("source") == "gap" and name != "second_signers":
        return "gap", None
    if name == "second_signers":
        return second_signers(cell.get("value") or [], ctx), None
    arms = cell.get("arms")
    if not arms:
        return cell.get("value"), None
    i = decide(arms, ctx)
    if i is UNKNOWN or i is None:
        return i, i
    return arm_value(arms[i]), i


class Registry:
    def __init__(self, manifest):
        self.rules = ns.Rules(manifest)

    def bind_leaf(self, family_id, dimension):
        """(leaf, matcher_family) for a dimension read under `family_id`. Raises ValueError when the
        dimension is refused or does not instantiate the family."""
        fam_got, _, refusal = ns.match_family(self.rules, dimension)
        if refusal:
            raise ValueError("%s is refused %s" % (dimension, refusal))
        fam = self.rules.families.get(family_id)
        if fam is None:
            raise ValueError("%s is not a registered family" % family_id)
        parts = dimension.split(":")
        ends_version = fam["segments"][-1]["segment"] == "{version}"
        if not ends_version and self.rules.version.fullmatch(parts[-1]) and len(parts) > 1:
            parts = parts[:-1]
        ok, binds, refusal = ns._match_segments(fam, parts, self.rules)
        if not ok or refusal:
            raise ValueError("%s does not instantiate %s" % (dimension, family_id))
        leaf = ":".join(v for k, v in binds.items() if k != "version")
        return leaf, fam_got


def row_context(registry, family_id, dimension, ctx):
    full = OrderedDict((k, ctx.get(k)) for k in CALLER_KEYS)
    full["leaf"] = None
    if dimension is not None:
        full["leaf"] = registry.bind_leaf(family_id, dimension)[0]
    return full


def resolve(family_model, family_id, dimension, ctx, registry=None):
    """{count, authorship, second_signers} for a row of `family_id` on `dimension` (None: leaf unknown),
    with the caller-supplied keys in `ctx` (verb, identity, group, seats, act; an absent key is unknown)."""
    registry = registry or Registry(load(REGISTRY))
    row = next((r for r in family_model["rows"] if r["family"] == family_id), None)
    if row is None:
        raise ValueError("%s is not a family of the model" % family_id)
    full = row_context(registry, family_id, dimension, ctx)
    out = OrderedDict((c, cell_answer(row[c], c, full)[0]) for c in CELLS)
    admits = author_admits(out["authorship"], ctx)
    if admits is not None:
        out["author_admits"] = admits
    return out


# ---- the vectors -----------------------------------------------------------------

KNOWN_ROLES = ("user", "node", "agent", "accord_holder", "wise_authority")


def selector_cells(model):
    """(family, cell name, arms) for every cell written as arms; second_signers entries count as arms."""
    for r in model["rows"]:
        for c in ("count", "authorship"):
            if r[c].get("arms"):
                yield r["family"], c, [OrderedDict([("when", a["when"]), ("value", arm_value(a))]) for a in r[c]["arms"]]
        ents = r["second_signers"].get("value") or []
        if any("when" in e for e in ents):
            yield r["family"], "second_signers", [OrderedDict([("when", e.get("when", "*")), ("value", e["role"] + "=" + e["member"])]) for e in ents]


def leaf_dimensions(registry, family_id, arms):
    """Concrete dimensions whose leaf binds under `family_id`, in a fixed order: the family itself with
    each listed and each selector-named value per placeholder, every registered family beneath its stem,
    and one unlisted value where the class is open."""
    rules = registry.rules
    fam = rules.families[family_id]
    named = [v for a in arms for k, vs in parse_selector(a["when"]) if k == "leaf" for v in vs]
    choices = []
    holders = [s for s in fam["segments"] if s["class"] != "literal" and s["segment"] != "{version}"]
    for seg in fam["segments"]:
        if seg["class"] == "literal":
            choices.append([seg["segment"]]); continue
        if seg["segment"] == "{version}":
            choices.append(["v1"]); continue
        vals = list(seg.get("values") or [])
        if len(holders) == 1:
            vals += [v for v in named if "{" not in v and v not in vals]
        if not seg.get("values") or seg.get("open"):
            vals.append("zz_other")
        if seg["class"] == "wildcard" and not vals:
            vals = ["zz_other"]
        choices.append(vals or ["sample"])
    dims = []
    for combo in itertools.islice(itertools.product(*choices), 256):
        d = ":".join(combo)
        dims.append(d if fam["segments"][-1]["segment"] == "{version}" else d + ":v1")
    stem = family_id[:-1] if family_id.endswith("*") else None
    if stem:
        for prefix, other in rules.families.items():
            if prefix.startswith(stem) and prefix != family_id:
                base = ns.instantiate(other, with_version=prefix not in rules.exempt)
                dims.append(base)
                for i, seg in enumerate(other["segments"]):
                    for v in (seg.get("values") or [])[1:]:
                        parts = ns.instantiate(other, with_version=prefix not in rules.exempt).split(":")
                        parts[i] = v
                        dims.append(":".join(parts))
    out = []
    for d in dims:
        try:
            registry.bind_leaf(family_id, d)
        except ValueError:
            continue
        if d not in out:
            out.append(d)
    return out


def key_candidates(key, arms):
    named = [v for a in arms for k, vs in parse_selector(a["when"]) if k == key for v in vs]
    if key == "identity":
        return [[v] for v in dict.fromkeys(named)] + [[next(r for r in KNOWN_ROLES if r not in named)]]
    if key == "group":
        return list(dict.fromkeys(named + [g for g in GROUP_VALUES if g not in named]))
    if key == "seats":
        return [1, 2]
    if key == "act":
        return list(dict.fromkeys(named + [a for a in ACT_VALUES if a not in named]))
    if key == "verb":
        return list(dict.fromkeys(named + ["attest", "authorize", "replace", "withdraw", "recant"]))
    raise KeyError(key)


def contexts(registry, family_id, arms):
    """Every (dimension, ctx) over the keys the cell's arms use, in a fixed order."""
    used = [k for k in KEYS if any(k == t[0] for a in arms for t in parse_selector(a["when"]))]
    dims = leaf_dimensions(registry, family_id, arms) if "leaf" in used else [None]
    if "leaf" not in used:
        fam = registry.rules.families[family_id]
        dims = [ns.instantiate(fam, with_version=family_id not in registry.rules.exempt)]
        try:
            registry.bind_leaf(family_id, dims[0])
        except ValueError:
            dims = leaf_dimensions(registry, family_id, [OrderedDict([("when", "*")])])[:1]
    callers = [k for k in used if k != "leaf"]
    for d in dims:
        for vals in itertools.product(*[key_candidates(k, arms) for k in callers]):
            yield d, OrderedDict(zip(callers, vals))


def answer(registry, row, cell, dimension, ctx):
    full = row_context(registry, row["family"], dimension, ctx)
    return cell_answer(row[cell], cell, full), full["leaf"]


def generate_vectors(model, registry):
    rows = {r["family"]: r for r in model["rows"]}
    vectors = []

    def add(fam, cell, dimension, ctx, why, kind):
        (got, decided), leaf = answer(registry, rows[fam], cell, dimension, ctx)
        mf = registry.bind_leaf(fam, dimension)[1] if dimension is not None else None
        v = OrderedDict([("family", fam), ("cell", cell), ("dimension", dimension), ("matcher_family", mf),
                         ("leaf", leaf), ("ctx", ctx), ("expect", got)])
        if cell != "second_signers":
            v["decided_by"] = decided
        v["kind"] = kind
        v["why"] = why
        vectors.append(v)
        return v

    for fam, cell, arms in selector_cells(model):
        ctxs = list(contexts(registry, fam, arms))
        row = rows[fam]

        def first(pred):
            for d, c in ctxs:
                full = row_context(registry, fam, d, c)
                if pred(full):
                    return d, c
            return None

        def holds(i, full):
            return arm_holds(arms[i]["when"], full) is True

        for i, arm in enumerate(arms):
            if cell == "second_signers":
                hit = first(lambda f, i=i: holds(i, f) and all(arm_holds(a["when"], f) is not UNKNOWN for a in arms))
                if hit:
                    add(fam, cell, hit[0], hit[1], "entry %d (%s) holds, so its role signs besides the author" % (i, arm["when"]), "holds")
                if arm["when"] != "*":
                    miss = first(lambda f, i=i: arm_holds(arms[i]["when"], f) is False and all(arm_holds(a["when"], f) is not UNKNOWN for a in arms))
                    if miss:
                        add(fam, cell, miss[0], miss[1], "entry %d (%s) does not hold, so its role is not asked" % (i, arm["when"]), "not_holds")
                    add(fam, cell, None, OrderedDict(), "no dimension, so the leaf is unknown and entry %d (%s) answers unknown" % (i, arm["when"]), "unknown")
                continue
            dec = first(lambda f, i=i: decide(arms, f) == i)
            if dec is None:
                raise ValueError("%s %s arm %d (%s) decides for no row the vectors can build" % (fam, cell, i, arm["when"]))
            add(fam, cell, dec[0], dec[1],
                "arm %d (%s) is the first that holds" % (i, arm["when"]) + ("; every earlier arm reads false" if i else ""), "holds")
            if arm["when"] != "*":
                miss = first(lambda f, i=i: arm_holds(arms[i]["when"], f) is False and decide(arms, f) is not UNKNOWN)
                if miss:
                    add(fam, cell, miss[0], miss[1], "arm %d (%s) does not hold; the answer is another arm's or none" % (i, arm["when"]), "not_holds")
            elif i:
                miss = first(lambda f, i=i: decide(arms, f) not in (i, UNKNOWN, None))
                if miss:
                    add(fam, cell, miss[0], miss[1], "the `*` arm holds for every row, and an earlier arm decides first", "not_holds")
            # unknown: drop one key of this arm, every earlier arm reading false and the arm's other tests true
            tests = parse_selector(arm["when"])
            for key, _vals in tests:
                def drop(d, c, key=key):
                    c2 = OrderedDict((k, v) for k, v in c.items() if k != key)
                    return (None if key == "leaf" else d), c2
                for d, c in ctxs:
                    if decide(arms, row_context(registry, fam, d, c)) != i:
                        continue
                    d2, c2 = drop(d, c)
                    f2 = row_context(registry, fam, d2, c2)
                    if all(arm_holds(arms[j]["when"], f2) is False for j in range(i)):
                        add(fam, cell, d2, c2, "%s is not supplied, so arm %d (%s) is unknown and no later arm may decide" % (
                            "the dimension" if key == "leaf" else key, i, arm["when"]), "unknown")
                        break
            # Kleene: a false test makes the arm false whatever the unsupplied test reads
            if len(tests) > 1:
                done = False
                for (kf, _), (ku, _) in itertools.permutations(tests, 2):
                    for d, c in ctxs:
                        if done:
                            break
                        f = row_context(registry, fam, d, c)
                        if test_holds(kf, dict(parse_selector(arm["when"]))[kf], f) is not False:
                            continue
                        d2 = None if ku == "leaf" else d
                        c2 = OrderedDict((k, v) for k, v in c.items() if k != ku)
                        f2 = row_context(registry, fam, d2, c2)
                        if decide(arms, f2) not in (UNKNOWN,) and all(arm_holds(arms[j]["when"], f2) is not UNKNOWN for j in range(i + 1)):
                            add(fam, cell, d2, c2, "%s is not supplied but %s reads false, so arm %d (%s) is false and the next arm is read" % (
                                "the dimension" if ku == "leaf" else ku, kf, i, arm["when"]), "false_beats_unknown")
                            done = True
                    if done:
                        break
            # an unknown arm after the decider changes nothing
            later = {t[0] for a in arms[i + 1:] for t in parse_selector(a["when"])} - {t[0] for a in arms[:i + 1] for t in parse_selector(a["when"])}
            for key in sorted(later):
                d, c = dec
                d2 = None if key == "leaf" else d
                c2 = OrderedDict((k, v) for k, v in c.items() if k != key)
                if decide(arms, row_context(registry, fam, d2, c2)) == i:
                    add(fam, cell, d2, c2, "%s is not supplied, and arm %d decides before any arm that reads it" % (key, i), "unknown_after_decider")
            # order matters: a row both this arm and a later named arm hold for
            for j in range(i + 1, len(arms)):
                if arms[j]["when"] == "*":
                    continue
                both = first(lambda f, i=i, j=j: holds(i, f) and holds(j, f) and decide(arms, f) == i)
                if both:
                    add(fam, cell, both[0], both[1], "arms %d (%s) and %d (%s) both hold; the earlier decides" % (
                        i, arm["when"], j, arms[j]["when"]), "order")
        if cell != "second_signers":
            none = first(lambda f: decide(arms, f) is None)
            if none:
                add(fam, cell, none[0], none[1], "every arm reads false: the cell gives no answer for this row", "no_arm")

    # an authorship value that compares iss with sub: the attested key's own statement holds, another key's is refused,
    # and a statement with no iss is unknown
    for fam, row in rows.items():
        values = [a["value"] for a in row["authorship"].get("arms") or []] or [row["authorship"].get("value")]
        if "subject" not in values:
            continue
        i = values.index("subject")
        arms = row["authorship"].get("arms") or [OrderedDict([("when", "*"), ("value", "subject")])]
        hit = next(((d, c) for d, c in contexts(registry, fam, arms) if decide(arms, row_context(registry, fam, d, c)) == i), None)
        if hit is None:
            raise ValueError("%s authorship: the subject arm decides for no row the vectors can build" % fam)
        for iss, kind, why in (("key_a", "subject_holds", "the statement's iss is the attested key (sub): the author is the subject"),
                               ("key_b", "subject_refused", "the statement's iss is another key than the attested key (sub): refused"),
                               (None, "subject_unknown", "no iss is supplied, so whether the author is the subject is unknown")):
            ctx = OrderedDict(list(hit[1].items()) + ([("iss", iss)] if iss else []) + [("sub", "key_a")])
            v = add(fam, "authorship", hit[0], ctx, why, kind)
            v["admits"] = author_admits(v["expect"], ctx)

    # a family whose row is a roster's act or carries a roster's count when act=group (counted, or authored and cosigned):
    # on its own form (act=own) a roster member's voice is in no role the row names, and is refused
    for fam, row in rows.items():
        arms = row["authorship"].get("arms") or []
        cnt = row["count"].get("arms") or []
        if not any("group" in dict(parse_selector(a["when"])).get("act", []) for a in arms + cnt):
            continue
        both = arms + [OrderedDict([("when", a["when"]), ("value", arm_value(a))]) for a in cnt]
        own = next(((d, c) for d, c in contexts(registry, fam, both)
                    if c.get("act") == "own" and cell_answer(row["authorship"], "authorship", row_context(registry, fam, d, c))[0] == "authored"
                    and cell_answer(row["count"], "count", row_context(registry, fam, d, c))[0] not in (UNKNOWN, None)), None)
        if own is None:
            raise ValueError("%s authorship: no authored row with act=own the vectors can build" % fam)
        for key in [k for k in own[1] if k != "act"]:   # supply no more than the reading needs: no group means no community_id
            c2 = OrderedDict((k, v) for k, v in own[1].items() if k != key)
            f2 = row_context(registry, fam, own[0], c2)
            if (cell_answer(row["authorship"], "authorship", f2)[0] == "authored" and cell_answer(row["count"], "count", f2)[0] not in (UNKNOWN, None)
                    and second_signers(row["second_signers"].get("value") or [], f2) != UNKNOWN):
                own = (own[0], c2)
        v = add(fam, "second_signers", own[0], own[1], "act=own: the row is its author's own, so a roster member's statement is in no role it names and is refused", "voice_refused")
        v["voice"] = "roster_member"
        v["admits"] = voice_admits(v["expect"], v["voice"])

    # every role a second_signers cell names: a statement offered in that role is accepted besides the author's, and one by
    # an unrelated key, in no role, is refused
    for fam, row in rows.items():
        ents = row["second_signers"].get("value") or []
        if not ents:
            continue
        sarms = [OrderedDict([("when", e.get("when", "*")), ("value", e["role"])]) for e in ents]
        for role in dict.fromkeys(e["role"] for e in ents):
            hit = next(((d, c) for d, c in contexts(registry, fam, sarms)
                        if voice_admits(second_signers(ents, row_context(registry, fam, d, c)), role) is True), None)
            if hit is None:
                raise ValueError("%s second_signers: the role %s holds for no row the vectors can build" % (fam, role))
            v = add(fam, "second_signers", hit[0], hit[1], "a statement in the role %s is accepted besides the author's" % role, "voice_admitted")
            v["voice"] = role
            v["admits"] = True
        d, c = next(iter(contexts(registry, fam, sarms)))
        v = add(fam, "second_signers", d, c, "a statement by an unrelated key is in no role the row names, and is refused", "voice_refused")
        v["voice"] = "unrelated_key"
        v["admits"] = voice_admits(v["expect"], "unrelated_key")

    # the `{name}` wildcard in a leaf value: one segment, any value, never two and never none
    for fam, cell, arms in selector_cells(model):
        for a in arms:
            for key, vals in parse_selector(a["when"]):
                if key != "leaf" or not any("{" in v for v in vals):
                    continue
                for d in leaf_dimensions(registry, fam, arms):
                    leaf = registry.bind_leaf(fam, d)[0]
                    hit = any(leaf_holds(leaf, v) for v in vals)
                    near = any(leaf.split(":")[0] == v.split(":")[0] for v in vals)
                    if hit or near:
                        add(fam, cell, d, OrderedDict(),
                            ("the leaf %s fills %s: `{name}` matches any one segment" if hit else
                             "the leaf %s has a different segment count from %s, so the wildcard does not match") % (
                                leaf, "|".join(vals)), "wildcard")
    return vectors


def vectors_doc(model, registry, model_sha):
    vs = generate_vectors(model, registry)
    return OrderedDict([
        ("_meta", OrderedDict([
            ("cc_version", load(REGISTRY)["_meta"]["cc_version"]),
            ("family_model_sha256", model_sha),
            ("generator", "tools/cc_family_select.py"),
            ("contract", "every consumer replays these against its own evaluator: for each vector, bind the leaf of "
                         "`dimension` under `family` (null: the leaf is unknown), take verb, identity, group, seats and act from "
                         "`ctx` (an absent key is unknown), and read the `cell`. `expect` is the answer: a count's doors, "
                         "authored or counted, the second signers as [{role, member}], `unknown`, `gap`, or null where every "
                         "arm reads false; `decided_by` is the deciding arm's index. An arm is false if any test is false, "
                         "else unknown if any test is unknown; an unknown arm before the decider makes the answer unknown. "
                         "Where the answer is `subject`, `admits` says whether the statement is admitted: true when ctx `iss` "
                         "equals ctx `sub`, false when it differs, `unknown` when either is absent. A vector with `voice` offers a "
                         "statement in that role over the row: `admits` is true only when the second_signers answer names the role"),
            ("keys", OrderedDict([
                ("leaf", "bound from the dimension: the family's non-literal segment values joined by ':', version tail stripped; `{name}` in a value matches one segment"),
                ("verb", "caller-supplied: one of attest, authorize, replace, withdraw, recant"),
                ("identity", "caller-supplied: the identity_type set of the identity the row concerns; holds when it contains a value"),
                ("group", "caller-supplied: the cohort_scope of the group the row is about (family, community, affiliations)"),
                ("seats", "caller-supplied: the group's deciding-seat count at the head the row names; `one` is 1"),
                ("act", "caller-supplied, never a payload member: derived from the statements the row carries; group when the row is the act of a roster under its consensus_protocol, several statements over one payload (CC 2.6.1.9); own when it is one statement by the author"),
                ("iss", "read from the statement: its CWT iss; compared with sub by the authorship value subject"),
                ("sub", "read from the statement: its CWT sub, the attested key"),
            ])),
            ("counts", OrderedDict(sorted({k: sum(1 for v in vs if v["kind"] == k) for k in {v["kind"] for v in vs}}.items()))),
        ])),
        ("vectors", vs),
    ])


def extract_doc(model, model_sha):
    fams = OrderedDict()
    for r in model["rows"]:
        a = r["authorship"]
        ac = OrderedDict([("value", a.get("value")), ("source", a.get("source"))])
        if a.get("arms"):
            ac["arms"] = [OrderedDict([("when", x["when"]), ("value", x["value"])]) for x in a["arms"]]
        if a.get("cc_ref"):
            ac["cc_ref"] = a["cc_ref"]
        s = r["second_signers"]
        sc = OrderedDict([("value", [OrderedDict([(k, e[k]) for k in ("role", "member", "when", "cc_ref") if k in e]) for e in s.get("value") or []]),
                          ("source", s.get("source"))])
        fams[r["family"]] = OrderedDict([("authorship", ac), ("second_signers", sc)])
    return OrderedDict([
        ("_meta", OrderedDict([
            ("cc_version", load(REGISTRY)["_meta"]["cc_version"]),
            ("source", "manifests/family_model.json"),
            ("source_sha256", model_sha),
            ("generator", "tools/cc_family_select.py"),
            ("reading", "the authorship and second_signers cells of every family, as the family model states them; arms read "
                        "by tools/cc_family_select.py and replayed from manifests/family_select_vectors.json"),
        ])),
        ("families", fams),
    ])


def render(doc, compact=False):
    if compact:
        return json.dumps(doc, separators=(",", ":"), ensure_ascii=False) + "\n"
    return json.dumps(doc, indent=1, ensure_ascii=False) + "\n"


def built():
    raw = open(MODEL, "rb").read()
    model, sha = json.loads(raw), hashlib.sha256(raw).hexdigest()
    registry = Registry(load(REGISTRY))
    return model, registry, sha


# ---- the gate ------------------------------------------------------------------------

def replay(model, registry, vectors, ev=None, adm=None, vadm=None):
    """The vectors that an evaluator `ev(arms, ctx) -> (answer, decided_by)` answers otherwise."""
    rows = {r["family"]: r for r in model["rows"]}
    bad = []
    for v in vectors:
        cell = rows[v["family"]][v["cell"]]
        full = row_context(registry, v["family"], v["dimension"], v["ctx"])
        if ev is None or v["cell"] == "second_signers":
            got, dec = cell_answer(cell, v["cell"], full)
        else:
            got, dec = ev(cell["arms"], full) if cell.get("arms") else cell_answer(cell, v["cell"], full)
        if got != v["expect"] or (v["cell"] != "second_signers" and dec != v.get("decided_by")):
            bad.append(v)
        elif "voice" in v and (vadm or voice_admits)(got, v["voice"]) != v["admits"]:
            bad.append(v)
        elif "admits" in v and "voice" not in v and (adm or author_admits)(got, v["ctx"]) != v["admits"]:
            bad.append(v)
    return bad


def _ev_unknown_is_false(arms, ctx):
    for i, a in enumerate(arms):
        if arm_holds(a["when"], ctx) is True:
            return arm_value(a), i
    return None, None


def _ev_last_wins(arms, ctx):
    hit = None
    for i, a in enumerate(arms):
        h = arm_holds(a["when"], ctx)
        if h is UNKNOWN:
            return UNKNOWN, UNKNOWN
        if h:
            hit = i
    return (None, None) if hit is None else (arm_value(arms[hit]), hit)


def _ev_literal_wildcard(arms, ctx):
    for i, a in enumerate(arms):
        res = []
        for k, vs in parse_selector(a["when"]):
            got = ctx.get(k)
            res.append(UNKNOWN if got is None else (got in vs if k == "leaf" else test_holds(k, vs, ctx)))
        h = False if False in res else (UNKNOWN if UNKNOWN in res else True)
        if h is UNKNOWN:
            return UNKNOWN, UNKNOWN
        if h:
            return arm_value(a), i
    return None, None


def _ev_any_unknown(arms, ctx):
    for i, a in enumerate(arms):
        res = [test_holds(k, vs, ctx) for k, vs in parse_selector(a["when"])]
        if UNKNOWN in res:
            return UNKNOWN, UNKNOWN
        if all(res):
            return arm_value(a), i
    return None, None


def _adm_ignores_iss(value, ctx):
    return True if value == "subject" else None


def _adm_any_iss(value, ctx):
    return (ctx.get("iss") is not None) if value == "subject" else None


def _voice_any(roles, voice):
    return True


def _voice_none(roles, voice):
    return False


def self_test():
    model, registry, sha = built()
    problems = []
    for fam, cell, arms in selector_cells(model):
        for a in arms:
            try:
                parse_selector(a["when"])
            except ValueError as e:
                problems.append("%s %s: %s" % (fam, cell, e))
    if problems:
        return problems, {}
    vectors = generate_vectors(model, registry)
    for v in replay(model, registry, vectors):
        problems.append("vector %s %s %r %r: expected %r" % (v["family"], v["cell"], v["dimension"], dict(v["ctx"]), v["expect"]))
    # coverage: every arm decides in a vector, and every named arm fails to hold in one
    for fam, cell, arms in selector_cells(model):
        mine = [v for v in vectors if v["family"] == fam and v["cell"] == cell]
        for i, a in enumerate(arms):
            if cell == "second_signers":
                pos = [v for v in mine if v["kind"] == "holds" and v["why"].startswith("entry %d " % i)]
                neg = [v for v in mine if v["kind"] == "not_holds" and v["why"].startswith("entry %d " % i)]
            else:
                pos = [v for v in mine if v.get("decided_by") == i]
                neg = [v for v in mine if v["kind"] == "not_holds" and ("arm %d " % i in v["why"] or a["when"] == "*")]
            if not pos:
                problems.append("%s %s arm %d (%s): no vector it holds for" % (fam, cell, i, a["when"]))
            if a["when"] != "*" and not neg:
                problems.append("%s %s arm %d (%s): no vector it does not hold for" % (fam, cell, i, a["when"]))
    for k in ("unknown", "order", "wildcard", "false_beats_unknown", "subject_holds", "subject_refused", "voice_refused", "voice_admitted"):
        if not any(v["kind"] == k for v in vectors):
            problems.append("no %s vector" % k)
    # the deliberate breaks the vectors must catch, run every time
    breaks = [("unknown read as false", _ev_unknown_is_false), ("last holding arm wins", _ev_last_wins),
              ("`{name}` read literally", _ev_literal_wildcard), ("an unknown test beats a false one", _ev_any_unknown)]
    caught = 0
    for name, ev in breaks:
        if replay(model, registry, vectors, ev):
            caught += 1
        else:
            problems.append("the vectors do not catch a broken evaluator: " + name)
    for name, adm in (("the author's iss not compared with sub", _adm_ignores_iss), ("any iss taken as the subject's", _adm_any_iss)):
        if replay(model, registry, vectors, adm=adm):
            caught += 1
        else:
            problems.append("the vectors do not catch a broken author check: " + name)
    for name, vadm in (("any voice accepted", _voice_any), ("no voice accepted", _voice_none)):
        if replay(model, registry, vectors, vadm=vadm):
            caught += 1
        else:
            problems.append("the vectors do not catch a broken voice check: " + name)
    for name, sel in (("an unknown key", "kind=x"), ("a seat token", "seats=two"), ("a group kind", "group=club"), ("an act kind", "act=club")):
        try:
            parse_selector(sel)
            problems.append("the parser admits " + name)
        except ValueError:
            caught += 1
    stale = extract_doc(model, "0" * 64)
    if render(stale) == render(extract_doc(model, sha)):
        problems.append("the extract does not carry the model's hash")
    else:
        caught += 1
    return problems, OrderedDict([("vectors", len(vectors)), ("breaks", "%d/%d" % (caught, len(breaks) + 9))])


def main(argv):
    if argv[:1] == ["--self-test"]:
        problems, info = self_test()
        if problems:
            sys.stderr.write("family selector evaluator: %d problems\n  %s\n" % (len(problems), "\n  ".join(problems)))
            return 1
        print("family selector evaluator OK: %d vectors, deliberate breaks caught %s" % (info["vectors"], info["breaks"]))
        return 0
    if argv[:1] in (["--write-vectors"], ["--check"]):
        model, registry, sha = built()
        outs = [(VECTORS, render(vectors_doc(model, registry, sha))), (EXTRACT, render(extract_doc(model, sha), compact=True))]
        if argv[0] == "--check":
            stale = [os.path.relpath(p, ROOT) for p, text in outs
                     if not os.path.exists(p) or open(p, encoding="utf-8").read() != text]
            if stale:
                sys.stderr.write("stale, run tools/cc_family_select.py --write-vectors: %s\n" % ", ".join(stale))
                return 1
            print("family_select_vectors.json and family_authorship.json current")
            return 0
        for p, text in outs:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(text)
            print("wrote %s (%d bytes)" % (os.path.relpath(p, ROOT), len(text.encode("utf-8"))))
        return 0
    if len(argv) >= 2:
        model, registry, _ = built()
        ctx = {}
        for kv in argv[2:]:
            k, v = kv.split("=", 1)
            ctx[k] = int(v) if k == "seats" else (v.split(",") if k == "identity" else v)
        print(json.dumps(resolve(model, argv[0], None if argv[1] == "-" else argv[1], ctx, registry), indent=1))
        return 0
    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
