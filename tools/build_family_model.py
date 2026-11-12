#!/usr/bin/env python3
"""The family model manifest, draft 0: every scores family as one row over the agreed columns.

Sources: the CC table (formal/derivation/family_kind_verb.tsv: kind, side, verbs, maintains_record,
reference) and persist's census at the v61 head (formal/derivation/census_v61.tsv: what the code
enforces today on each axis). Every cell carries its value and its source: cc-table, code-v61,
prose (bespoke code outside the closed vocabulary), or gap (nothing enforces). The vendor gate of a
later version refuses a gap; this draft counts them. Writes manifests/family_model.json; --check
only compares.
"""
import csv, glob, hashlib, json, os, re, sys
from collections import Counter, OrderedDict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CC = os.path.join(ROOT, "formal/derivation/family_kind_verb.tsv")
CENSUS = os.path.join(ROOT, "formal/derivation/census_v61.tsv")
SIGNER_TEXT = os.path.join(ROOT, "formal/derivation/signer_rule_text.tsv")
CELL_TEXT = os.path.join(ROOT, "formal/derivation/cell_text.tsv")
COUNT_TEXT = os.path.join(ROOT, "formal/derivation/count_text.tsv")
POLICY = os.path.join(ROOT, "manifests/governance_policy.json")
SIGNED_OBJECT = os.path.join(ROOT, "constitution/signed_object.tsv")
CELL_CITES = os.path.join(ROOT, "formal/derivation/cell_cites.tsv")
FOLD_TEXT = os.path.join(ROOT, "formal/derivation/fold_text.tsv")
FOLD_MARKS_MAX = 50   # uses of words no other vocabulary has; the number only falls
COUNT_SOURCES = ("subject_group", "signer_group", "dimension_authority", "accord", "trust_root", "self", "conferrer")
COUNT_KEYS = ("leaf", "verb", "identity", "group", "seats")
COUNT_OPEN_MAX = 6   # families with a cosign cell that is not none and no typed count; the number only falls
REG = os.path.join(ROOT, "manifests/namespace_registry.json")
OUT = os.path.join(ROOT, "manifests/family_model.json")
DEFAULT = os.path.join(ROOT, "formal/derivation/family_default_row.json")
DEPARTS = os.path.join(ROOT, "manifests/family_departures.tsv")
REASONS = os.path.join(ROOT, "formal/derivation/departure_reasons.json")
REASONS_MD = os.path.join(ROOT, "formal/family_model/DEPARTURES.md")
BASES = ("text", "census", "build")
COLUMNS = OrderedDict([
    ("kind", "Priorities | Rules | Manner | Identity | Confidence | Facts | Circumstances | Process | Model | Structure | Premises"),
    ("side", "thing | account (a function of kind)"),
    ("verbs", "subset of {attest, authorize, replace, withdraw, recant}"),
    ("maintains_record", "bool: the row is itself the evidence that something happened; fixes erasure and projection"),
    ("reference", "none | pre:<kind|any> | carry:<kind> (the row it names; only a carry is a cell of the carries grid)"),
    ("placement", "self_collective | targeted_family | targeted_room | commons | addressed"),
    ("signer_rule", "{self | owner_of_subject | seat_role(duty) | roster_member(at) | minter | steward | any_registered} x via {none | delegates_to(scope, depth, term, caps)} x conditions ⊆ {adult, capacitated, not_subject, not_author}"),
    ("emitter_class", "derived from signer_rule: person (any registered key) | self | owner | seat:<duty> | roster | steward | substrate:<identity_type> | shut; several joined by |; the tier that writes the family's rows, read by nothing at admission"),
    ("subject_rule", "{subject_kind, cardinality, must_be_registered, for_key_id ∈ {none, serve_seat, recipient}, in_audience, attested_party, subject_blind}"),
    ("cosign_rule", "none | group_consensus_protocol | moderator_quorum | accord | deciding_seat_plus_outside"),
    ("polarity", "the registry's polarity class"),
    ("body", "CDDL reference beyond the signed object; an existence_only audience names a two-part shape"),
    ("freshness", "{judged_at ∈ {signed_instant_with_W, receipt}, W}"),
    ("lifecycle", "{withdraws_by ⊆ {attester, subject, cosigned}, retraction_class ∈ {peer, duty_record, authority_act, cosigned}, supersedes ∈ {same_attester, none}, expires, rotation_on_removal}"),
    ("replication", "{tier ∈ {local, cohort, federation}, audience ∈ {cohort, cohort_plus_subjects(full|existence_only), addressee, everyone}, non_recipient ∈ {drop, hold_sealed}, held ∈ {settle_on_key, refuse}}"),
    ("projection", "{table, rebuild ∈ {byte_equal, none}}"),
    ("erasure_route", "dsar | purge | legal_hold | none"),
    ("blind", "members minted as disclosures (CC 2.6.1.8): every free-text and other-authored member of a dsar|purge family, body.note always; [] for none|legal_hold; no fold, verdict or admission reads a listed member"),
    ("governance", "policy_row | none"),
    ("fold", "how the family's rows, read as a set, give a value: statements in the grammar of tools/fold_grammar.py, a part not stated taken from the default (formal/derivation/fold_text.tsv)"),
    ("count", "arms `selector => doors` joined by ` ; `, the first that holds deciding; a door is none | shut | POLICY_ROW[@source][!confers|!result] (formal/derivation/count_text.tsv)"),
    ("derived", "projection_id | none (the row must equal the named projection's rebuild)"),
    ("confers", "trust | duty | standing | nothing (read by the trust-set fold, never by admission)"),
    ("binds_segment", "placeholder → signer | subject | group | none"),
    ("evidence", "{claim_ids, refusal tokens}"),
])
CENSUS_MAP = {"placement": "2_placement", "signer_rule": "3_signer_rule", "subject_rule": "4_subject_rule",
              "cosign_rule": "5_cosign_rule", "body": "7_body", "freshness": "8_freshness", "lifecycle": "9_lifecycle",
              "replication": "10_replication", "projection": "11_projection", "erasure_route": "12_erasure_route",
              "governance": "13_governance", "evidence": "14_evidence"}
SUBKEYS = {"replication": ["tier", "audience", "non_recipient", "held"],
           "lifecycle": ["withdraws_by", "retraction_class", "supersedes", "expires", "rotation_on_removal"],
           "projection": ["table", "rebuild"],
           "subject_rule": ["kind", "cardinality", "must_be_registered", "for_key_id", "in_audience", "attested_party", "subject_blind"]}
TAGS = ("GAP", "PROSE", "GENERIC", "DATA")
HELD_SHUT = "none (held shut)"   # the census value of a family the code never stores
def tag_of(t):
    """The census writes a source tag as the first token: GAP:, PROSE:, GENERIC:, DATA:. Returns (tag, rest)."""
    m = re.match(r"^(GAP|PROSE|GENERIC|DATA)\s*:?\s*(.*)$", t.strip(), re.S)
    return (m.group(1), m.group(2).strip()) if m else (None, t.strip())
def head_of(t):
    """The closed value at the front of a cell: up to the first ' (' (a space before the parenthesis, so
    cohort_plus_subjects(full) keeps its qualifier), ';', ' via ', ' @ ' or ' on release'."""
    h = re.split(r"\s+\(|;| on release| via | @ ", t, 1)[0].strip().rstrip(".,")
    return h or None
def split_top(t, sep):
    """Split on sep outside parentheses and braces."""
    out, depth, cur = [], 0, ""
    for ch in t:
        if ch in "({[": depth += 1
        elif ch in ")}]": depth = max(0, depth - 1)
        if ch == sep and depth == 0: out.append(cur); cur = ""
        else: cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]
def slices(t):
    """s2:/s3: segments (an unmerged slice's value) split out of a sub-value, at the top level only."""
    out, keep = {}, []
    for seg in split_top(t.replace(" ;", ";"), ";"):
        m = re.match(r"^(s[23])\s*:\s*(.+)$", seg)
        if m: out[m.group(1)] = m.group(2).strip()
        else: keep.append(seg)
    return out, "; ".join(keep)
def arms(t):
    """A per-arm value: 'by cohort_scope: a -> x; b -> y' or 'leaf: rule; leaf2: rule2' (split at the top level)."""
    body = re.sub(r"^by cohort_scope:\s*", "", t).replace(" ;", ";")
    segs = split_top(body, ";")
    if "->" in body:
        d = OrderedDict()
        for arm in segs:
            m = re.match(r"\s*([a-z_]+)\s*->\s*(.+)$", arm)
            if m: d[m.group(1)] = m.group(2).strip()
        return d or None
    if len(segs) >= 2 and all(re.match(r"^[a-z_/]+:\s*\S", x) for x in segs):
        d = OrderedDict()
        for x in segs:
            k, v = x.split(":", 1); d[k.strip()] = v.strip()
        return d
    if any(re.match(r"^([a-z_]+) leaf:\s*\S", x) or x.startswith("other leaves ") for x in segs):
        d = OrderedDict()
        for x in segs:
            m = re.match(r"^([a-z_]+) leaf:\s*(.+)$", x)
            if m: d[m.group(1)] = m.group(2).strip()
            elif x.startswith("other leaves "): d["other"] = x[len("other leaves "):].strip()
            else: return None
        return d
    return None
def leaf(t):
    """One sub-value: {value, source, note, closed, alternatives, arms, s2, s3}. The tag decides the source;
    a closed value after a GAP or PROSE tag is kept (the de-facto or target value, not nothing); nothing is
    cut: `value` is the whole reading, `closed` its head, `alternatives` the set when the cell lists several."""
    t = t.strip()
    tag, rest = tag_of(t)
    src = {"GAP": "gap", "PROSE": "prose", "GENERIC": "generic", "DATA": "code-v61", None: "code-v61"}[tag]
    if t.startswith("any of {"):
        m = re.match(r"any of \{([^}]*)\}", t)
        return {"value": [x.strip() for x in m.group(1).split(",")], "source": "gap", "note": t}
    if tag is None and re.search(r"\bGAP\b", rest): src = "mixed"
    if tag is None and re.search(r"\bPROSE\b", rest): src = "mixed" if src == "mixed" else "prose"
    sl, rest2 = slices(rest)
    if tag == "GAP" and rest.startswith("on release"):
        out = {"value": None, "source": "gap", "note": rest}; out.update(sl); return out
    if re.match(r"^federation only\b", rest2): rest2 = "federation (capacity never local)"
    a = arms(rest2)
    alts = [x.strip() for x in rest2.split(" | ")] if " | " in rest2 and not a else None
    closed = head_of(rest2) if rest2 else None
    if src == "gap" and closed and closed.lower() in ("none", "no per-family constraint", "nothing"): closed = None
    out = {"value": a if a else (alts if alts else (rest2 if rest2 else None)), "source": src}
    if closed and out["value"] != closed: out["closed"] = closed
    if a and src == "prose": out["source"] = "code-v61"   # per-leaf closed values are closed
    if rest and rest != out["value"]: out["note"] = rest
    out.update(sl)
    return out
def cell(col, text):
    t = (text or "").strip()
    if not t or t in ("—", "-"): return {"value": None, "source": "gap"}
    keys = SUBKEYS.get(col)
    if keys and (" | " in t or re.match(r"^(%s):" % "|".join(keys), t)):
        sub, order, cur = OrderedDict(), [], None
        for part in [x.strip() for x in t.split(" | ")]:
            m = re.match(r"^([a-z_]+):\s*(.*)$", part, re.S)
            if m and m.group(1) in keys: cur = m.group(1); sub[cur] = m.group(2); order.append(cur)
            elif cur is None: cur = keys[0]; sub[cur] = part; order.append(cur)
            else: sub[cur] = sub[cur] + " | " + part   # an alternative of the field before, not a new field
        parts = OrderedDict((k, leaf(v)) for k, v in sub.items())
        for k, v in parts.items():   # a sub-field's value is its closed head when the reading is one value with a note
            if isinstance(v.get("value"), str) and v.get("closed") and v["closed"] != v["value"]:
                v["note"] = v["value"]; v["value"] = v.pop("closed")
        srcs = {v["source"] for v in parts.values()}
        return {"value": OrderedDict((k, v["value"]) for k, v in parts.items()), "source": srcs.pop() if len(srcs) == 1 else "mixed", "parts": parts}
    if col == "freshness": return freshness(t)
    if col == "signer_rule": return signer(t)
    if col == "evidence": return evidence(t)
    return leaf(t)
def freshness(t):
    tag, rest = tag_of(t)
    out = leaf(t)
    if tag == "GENERIC" or "future-skew" in rest:
        out["value"] = {"judged_at": "receipt", "W": None}
        if tag == "GENERIC": out["source"] = "generic"
    elif re.search(r"\bW\b", rest):
        m = re.search(r"W\s*=\s*(\d+)\s*(h|d|s)\b", rest)
        W = int(m.group(1)) * {"h": 3600, "d": 86400, "s": 1}[m.group(2)] if m else None
        out["value"] = {"judged_at": "signed_instant_with_W", "W": W if W is not None else rest}
    return out
EMITTER_RULES = [  # (regex over the signer text, class); the same vocabulary build_transitions.py maps to role tokens
    (r"none \(held shut\)", "shut"),
    (r"seat_role\((\w+)\)", "seat:{}"),
    (r"identity_type contains (\w+)", "substrate:{}"),
    (r"roster_member|\bcosign|holder quorum|\bquorum\b", "roster"),
    (r"\bsteward\b", "steward"),
    (r"owner_of_subject|owner_of\(|\bminter\b|\bowner\b", "owner"),
    (r"any_registered", "person"),
    (r"\bself\b", "self"),
]
def emitter_class(cell):
    """Who writes the family's rows, as a class the tier table can be read off (CC#203): derived from the
    signer rule's closed text; None with source gap where the rule itself is a gap."""
    v = cell.get("value") if isinstance(cell, dict) else cell
    if isinstance(v, dict): v = v.get("who")
    raw = " | ".join(map(str, v)) if isinstance(v, list) else (str(v) if v is not None else "")
    closed = cell.get("closed") if isinstance(cell, dict) else None
    classes = set()
    for text in (closed, raw):  # the closed head first; the raw cell only where the head names no emitter
        for pat, cls in EMITTER_RULES:
            for m in re.finditer(pat, text or ""):
                classes.add(cls.format(m.group(1)) if "{}" in cls else cls)
        if classes:
            break
    if not classes:
        return {"value": None, "source": "gap", "note": "signer rule names no emitter"}
    return {"value": "|".join(sorted(classes)), "source": "derived"}
def signer(t):
    tag, rest = tag_of(t)
    out = leaf(t)
    m = re.match(r"^([^;]*?)\s+x\s+(.*?)\s+x\s+\{([^}]*)\}(.*)$", rest, re.S)
    if m:
        who = m.group(1).strip()
        out["value"] = {"who": [w.strip() for w in who.split(" | ")] if " | " in who else who,
                        "via": m.group(2).strip(), "conditions": [c.strip() for c in m.group(3).split(",") if c.strip()]}
        q = m.group(4).strip(" ;")
        if q: out["qualifier"] = q
    return out
def evidence(t):
    out = leaf(t)
    d = OrderedDict()
    for m in re.finditer(r"(\d+ nsproc|door claims|door tokens|generic tokens|nsproc)\s*:\s*([^;]+)", t):
        k = m.group(1); vals = [x.strip() for x in re.split(r"[,/]", m.group(2)) if x.strip()]
        n = re.match(r"(\d+) nsproc", k)
        if n: d["nsproc"] = vals; d["n_nsproc"] = int(n.group(1))
        else: d[k.replace(" ", "_")] = vals
    if d: out["value"] = d
    return out
def reference_code(t):
    t = (t or "").strip()
    if not t or t.lower().startswith("none"): return None
    refs = []
    for m in re.finditer(r"\{family:\s*(.+?),\s*standing:\s*(.+?),\s*same_group:\s*([^}]+?)\}(?:\s*@\s*([^;]+))?", t):
        refs.append({"family": m.group(1).strip(), "standing": m.group(2).strip(), "same_group": m.group(3).strip(), "where": (m.group(4) or "").strip()})
    return refs or [{"raw": t}]
def polarity_census(t):
    m = re.search(r"alias\s*->\s*([^)]+)\)", t or "")
    if m: return m.group(1).strip()
    tag, rest = tag_of(t or "")
    return head_of(rest) if rest else None

def section_span(ref):
    """The text of a Constitution section with its subsections, by its number; None when no heading carries it."""
    m = re.fullmatch(r"CC (\d+(?:\.\d+)*)", ref or "")
    if not m: return None
    num = m.group(1)
    for path in sorted(glob.glob(os.path.join(ROOT, "constitution", f"part_{num.split('.')[0]}_*.md"))):
        lines = open(path, encoding="utf-8").read().split("\n")
        start = None
        for i, l in enumerate(lines):
            h = re.match(r"#{1,6} (\d+(?:\.\d+)*)(?= |$)", l)
            if not h: continue
            if start is None:
                if h.group(1) == num: start = i
            elif not h.group(1).startswith(num + "."):
                return "\n".join(lines[start:i])
        if start is not None: return "\n".join(lines[start:])
    return None


def fam_match(fam, pat):
    """A pattern is a family's name, or a stem ending in a colon that takes every family under it."""
    return fam == pat or (pat.endswith(":") and fam.startswith(pat))


def departure_reasons(rows, default):
    """Give every departing cell its reason, or refuse.

    A reason says when a family leaves the default row and why, and names the cells it moves. Three bases:
    text (a section of the Constitution and words that stand in it), census (the family is not built, so
    its cells are unread), build (a fact of the store that no rule turns on). The check runs both ways:
    a departing cell with no reason fails unless it is listed open with its question, and a cell a reason
    names that sits on the default fails too, so a reason cannot outlive what it explained.
    """
    spec = json.load(open(REASONS, encoding="utf-8"), object_pairs_hook=OrderedDict)
    errs, claims, seen = [], OrderedDict(), set()
    unbuilt = {r["family"] for r in rows if r["placement"].get("value") is None or str(r["placement"]["value"]).startswith("none (held shut")}
    for rs in spec["reasons"]:
        rid = rs.get("id", "?")
        if rid in seen: errs.append(f"{rid}: named twice")
        seen.add(rid)
        for k in ("when", "why", "basis"):
            if not rs.get(k): errs.append(f"{rid}: no {k}")
        if rs.get("basis") not in BASES: errs.append(f"{rid}: basis is one of {', '.join(BASES)}")
        if "enforced" in rs and (rs["enforced"] is not False or rs.get("basis") != "text"):
            errs.append(f"{rid}: enforced is stated only as false, and only where the text gives the rule")
        if ("cell" in rs or "build_note" in rs) and rs.get("enforced") is not False:
            errs.append(f"{rid}: cell and build_note describe a rule the build does not enforce; state enforced false or remove them")
        if "cell" in rs and rs["cell"] != "build":
            errs.append(f"{rid}: cell is stated only as build, where the cell records the build and not the text")
        if rs.get("cell") == "build" and rs.get("value"):
            errs.append(f"{rid}: a reason whose cell records the build fixes no value")
        if rs.get("basis") == "text":
            span = section_span(rs.get("cc_ref"))
            if span is None: errs.append(f"{rid}: {rs.get('cc_ref')} is not a section of the Constitution")
            elif not rs.get("quote") or rs["quote"] not in span: errs.append(f"{rid}: the quoted words do not stand in {rs.get('cc_ref')}")
        moves = rs.get("moves") or OrderedDict()
        if rs.get("premise") == "unbuilt":
            moves = OrderedDict((col, sorted(f for f in unbuilt if col in next(r for r in rows if r["family"] == f)["departs"])) for col in default)
        elif rs.get("premise") == "typed_view":   # every built family whose table rebuilds from its rows
            moves = OrderedDict([("projection", sorted(r["family"] for r in rows if r["family"] not in unbuilt and "projection" in r["departs"]
                                                       and isinstance(r["projection"].get("value"), dict) and r["projection"]["value"].get("rebuild") == "byte_equal"))])
        elif rs.get("premise"):
            errs.append(f"{rid}: unknown premise {rs['premise']}")
        if not any(moves.values()): errs.append(f"{rid}: moves nothing")
        for col, pats in moves.items():
            if col not in default: errs.append(f"{rid}: {col} is not a column of the default row"); continue
            for pat in pats:
                hit = [r for r in rows if fam_match(r["family"], pat)]
                if not hit: errs.append(f"{rid}: {pat} names no family")
                for r in hit:
                    if r["family"] in unbuilt and rs.get("premise") != "unbuilt":
                        errs.append(f"{rid}: {r['family']} is not built; its cells are unread and take no other reason")
                    elif col not in r["departs"]:
                        errs.append(f"{rid}: {r['family']} is said to leave the default in {col} and sits on it")
                    else:
                        claims.setdefault((r["family"], col), []).append(rid)
        for path, want in (rs.get("value") or {}).items():   # the reason fixes the cell's value, not only that it moves
            col, _, sub = path.partition(".")
            for pat in moves.get(col, []):
                for r in rows:
                    if not fam_match(r["family"], pat): continue
                    v = r[col].get("value")
                    got = v.get(sub) if sub and isinstance(v, dict) else v
                    if got != want: errs.append(f"{rid}: {r['family']} {path} is {got!r}, and the reason gives {want!r}")
    opens = OrderedDict()
    for o in spec.get("open", []):
        k = (o.get("family"), o.get("column"))
        if not o.get("question"): errs.append(f"open {k[0]} {k[1]}: no question")
        if k in opens: errs.append(f"open {k[0]} {k[1]}: listed twice")
        opens[k] = o.get("question")
    departing = {(r["family"], col) for r in rows for col in r["departs"]}
    for k in sorted(departing):
        if k in claims and k in opens: errs.append(f"{k[0]} {k[1]}: has a reason and is listed open; remove one")
        if k not in claims and k not in opens: errs.append(f"{k[0]} {k[1]}: leaves the default with no reason; give one or list it open with its question")
    for k in opens:
        if k not in departing: errs.append(f"open {k[0]} {k[1]}: no longer leaves the default; remove the line")
    return spec, claims, opens, errs


def reasons_md(spec, claims, opens, rows, default):
    cells = Counter(rid for v in claims.values() for rid in v)
    fams = {}
    for (f, c), v in claims.items():
        for rid in v: fams.setdefault(rid, OrderedDict()).setdefault(c, []).append(f)
    out = ["# Why and when a family leaves the default row", "",
           "Generated by `tools/build_family_model.py` from `formal/derivation/departure_reasons.json`; do not edit.", "",
           spec["reading"], ""]
    for rs in spec["reasons"]:
        rid = rs["id"]
        out += [f"## {rs['title']}", "", f"**When.** {rs['when']}", "", f"**Why.** {rs['why']}", ""]
        if rs["basis"] == "text":
            out += [f"**Text.** {rs['cc_ref']}: \"{rs['quote']}\"", ""]
            if rs.get("enforced") is False:
                out += ["**Build.** The text states this and the pinned build does not enforce it; the cell records the "
                        + ("build" if rs.get("cell") == "build" else "text") + "." + (" " + rs["build_note"] if rs.get("build_note") else ""), ""]
        else: out += [f"**Basis.** {'The family is not built; the census read nothing.' if rs['basis'] == 'census' else 'A fact of the store; no rule turns on it.'}", ""]
        out += ["| column | families |", "|---|---|"]
        out += [f"| {c} | {', '.join('`' + f + '`' for f in fs)} |" for c, fs in fams.get(rid, {}).items()]
        out += [""]
    if opens:
        out += ["## Open", "", "Cells that leave the default with no reason yet, each with the question that would give it one.", "",
                "| family | column | question |", "|---|---|---|"]
        out += [f"| `{f}` | {c} | {q} |" for (f, c), q in opens.items()]
        out += [""]
    return "\n".join(out)


def main():
    cc = {r["family"]: r for r in csv.DictReader(open(CC, encoding="utf-8"), delimiter="\t")}
    census_lines = [l for l in open(CENSUS, encoding="utf-8").read().split("\n") if not l.startswith("#")]
    census = {r["prefix"]: r for r in csv.DictReader(census_lines, delimiter="\t")}
    reg = json.load(open(REG, encoding="utf-8"))
    pol = {}
    for f in reg.get("families", []):
        if isinstance(f, dict) and "prefix" in f: pol[f["prefix"]] = f.get("polarity")
    signer_text = OrderedDict()   # family -> rows; one row for a whole-family rule, one per stage where the text gives stages
    for r in csv.DictReader([l for l in open(SIGNER_TEXT, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t"):
        signer_text.setdefault(r["family"], []).append(r)
    # A cell the text states and the census leaves open (formal/derivation/cell_text.tsv): the cell
    # takes the text's value, written in the column's own vocabulary, with the words it rests on.
    cell_text = OrderedDict()
    if os.path.exists(CELL_TEXT):
        for r in csv.DictReader([l for l in open(CELL_TEXT, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t"):
            cell_text.setdefault(r["family"], []).append(r)
    count_text = OrderedDict()
    for r in csv.DictReader([l for l in open(COUNT_TEXT, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE):
        count_text.setdefault(r["family"], []).append(r)
    policy_rows = {f["family"] for f in json.load(open(POLICY, encoding="utf-8"))["families"]}
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fold_grammar as fg, guard_grammar as gg
    fold_text, fold_every, fold_marks = OrderedDict(), [], Counter()
    for r in csv.DictReader([l for l in open(FOLD_TEXT, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE):
        fold_text.setdefault(r["family"], []).append(r)
    reg_fams = set(cc) | set(census)
    for f in reg.get("families", []):
        if isinstance(f, dict) and "prefix" in f:
            reg_fams.add(f["prefix"]); reg_fams.update(f.get("leaves", []))
    part_text = "\n".join(open(p, encoding="utf-8").read() for p in sorted(glob.glob(os.path.join(ROOT, "constitution", "part_*.md"))))
    fold_voc = {"families": reg_fams, "policy_rows": policy_rows, "tokens": set(re.findall(r"`([a-z_0-9:]+)`", part_text)),
                "roles": set(json.load(open(os.path.join(ROOT, "manifests/transitions.json"), encoding="utf-8"))["_meta"]["role_tokens"])}
    fg.parse(fg.DEFAULT)
    def fold_cell(fam, stmts):
        out = []
        for st in stmts:
            where = f"fold_text.tsv: {fam} ({st['cc_ref']})"
            try:
                parsed, mk, names = fg.parse(st["fold"])
            except fg.FoldError as e:
                print(f"{where}: {e}"); return None
            bad = fg.closure(names, fold_voc, gg.family_ok)
            if bad:
                print(f"{where}: outside the vocabularies: " + "; ".join(bad)); return None
            span = section_span(st["cc_ref"])
            if span is None or st["quote"] not in span:
                print(f"{where}: the quoted words do not stand in {st['cc_ref']}"); return None
            cur = next((x for x in out if x["fold"] == st["fold"]), None)
            if cur:
                if st["cc_ref"] not in cur["cc_ref"]: cur["cc_ref"].append(st["cc_ref"])
            else:
                out.append(OrderedDict([("fold", st["fold"]), ("cc_ref", [st["cc_ref"]])]))
                fold_marks.update(mk)
        return out
    rows = []
    for fam in sorted(set(cc) | set(census)):
        c, z = cc.get(fam), census.get(fam)
        row = OrderedDict([("family", fam)])
        if c:
            row["kind"] = {"value": c["kind"], "source": "cc-table", "confidence": c["confidence"]}
            row["side"] = {"value": c["side"].lower(), "source": "cc-table"}
            row["verbs"] = {"value": [v.strip() for v in c["verbs"].split(",") if v.strip()], "source": "cc-table"}
            row["maintains_record"] = {"value": c["maintains_record"] == "yes", "source": "cc-table"}
            row["reference"] = {"value": None if c["reference"] == "—" else c["reference"], "source": "cc-table"}
        else:
            for k in ("kind", "side", "verbs", "maintains_record", "reference"): row[k] = {"value": None, "source": "gap", "note": "not in the CC table"}
        for col, zc in CENSUS_MAP.items():
            row[col] = cell(col, z[zc]) if z else {"value": None, "source": "gap", "note": "not in the census"}
        if fam in signer_text:
            sts = signer_text.pop(fam); cur = row["signer_rule"]
            if cur.get("source") != "gap" and cur.get("value") != HELD_SHUT:
                print(f"signer_rule_text.tsv: {fam} has a closed census cell ({cur.get('source')}); remove the row"); return 1
            parsed = []
            for st in sts:
                txt = signer(st["signer_rule"])
                if not isinstance(txt.get("value"), dict):
                    print(f"signer_rule_text.tsv: {fam} is not `who x via x {{conditions}}`"); return 1
                parsed.append(((st.get("stage") or "").strip(), txt, st))
            stages = [p[0] for p in parsed]
            if (len(parsed) > 1 and "" in stages) or len(set(stages)) != len(stages):
                print(f"signer_rule_text.tsv: {fam} mixes a whole-family rule with stages, or repeats a stage"); return 1
            code = {"value": cur.get("value"), "source": cur.get("source")}
            if stages == [""]:
                _, txt, st = parsed[0]
                row["signer_rule"] = {"value": txt["value"], "source": "cc-table", "cc_ref": st["cc_ref"], "code": code}
                if txt.get("qualifier"): row["signer_rule"]["qualifier"] = txt["qualifier"]
            else:
                def text_of(v): return (" | ".join(v["who"]) if isinstance(v["who"], list) else v["who"]) + " x " + v["via"] + " x {" + ", ".join(v["conditions"]) + "}"
                row["signer_rule"] = {"value": OrderedDict((stg, text_of(txt["value"])) for stg, txt, _ in parsed), "source": "cc-table",
                                      "per_stage": True, "closed": "; ".join(f"{stg}: {text_of(txt['value'])}" for stg, txt, _ in parsed),
                                      "cc_ref": OrderedDict((stg, st["cc_ref"]) for stg, _, st in parsed), "code": code}
                q = OrderedDict((stg, txt["qualifier"]) for stg, txt, _ in parsed if txt.get("qualifier"))
                if q: row["signer_rule"]["qualifier"] = q
        for ct in cell_text.pop(fam, []):
            col = ct["column"]
            if col not in CENSUS_MAP or col == "signer_rule":
                print(f"cell_text.tsv: {fam} names the column {col}, which is not one this table fills"); return 1
            cur = row[col]
            if cur.get("source") not in ("gap", "generic"):
                print(f"cell_text.tsv: {fam} {col} is closed by the census ({cur.get('source')}); a difference from the text is a departure with a reason, not a row here"); return 1
            span = section_span(ct["cc_ref"])
            if span is None or ct["quote"] not in span:
                print(f"cell_text.tsv: {fam} {col}: the quoted words do not stand in {ct['cc_ref']}"); return 1
            new = cell(col, ct["value"])
            new["source"] = "cc-table"; new["cc_ref"] = ct["cc_ref"]
            new["code"] = {"value": cur.get("value"), "source": cur.get("source")}
            row[col] = new
        pv = polarity_census(z["6_polarity"]) if z else None
        row["polarity"] = {"value": pv or pol.get(fam), "source": "code-v61" if pv else ("cc-table" if pol.get(fam) else "gap"), "registry": pol.get(fam)}
        row["emitter_class"] = emitter_class(row["signer_rule"])
        for col in ("derived", "confers", "binds_segment"):
            row[col] = {"value": None, "source": "gap", "note": "new column; values come with the manifest's first ruled version"}
        stmts = fold_text.pop(fam, [])
        if stmts:
            fc = fold_cell(fam, stmts)
            if fc is None: return 1
            row["fold"] = {"value": fc, "source": "cc-table"}
        else:
            row["fold"] = {"value": [], "source": "generic", "note": "no fold is typed for the family; it reads by the default"}
        # How the family's act is counted: typed arms over the policy table, each with the words it rests on.
        arms = count_text.pop(fam, [])
        if arms:
            out_arms = []
            for i, a in enumerate(arms):
                where = f"count_text.tsv: {fam} arm {i + 1}"
                sel = a["selector"]
                if sel != "*":
                    for t in sel.split(" & "):
                        mt = re.fullmatch(r"([a-z]+)=([a-z_]+(?:\|[a-z_]+)*)", t)
                        if not mt or mt.group(1) not in COUNT_KEYS:
                            print(f"{where}: {t!r} is not a test on one of {', '.join(COUNT_KEYS)}"); return 1
                elif i != len(arms) - 1:
                    print(f"{where}: an arm for every row is the last arm"); return 1
                md = re.fullmatch(r"(none|shut)|([a-z_]+)(?:@([a-z_]+))?(?:!(confers|result))?", a["doors"])
                if not md or (md.group(2) and (md.group(2) not in policy_rows or (md.group(3) and md.group(3) not in COUNT_SOURCES))):
                    print(f"{where}: {a['doors']!r} is not none, shut or a policy row with a known source"); return 1
                span = section_span(a["cc_ref"])
                if span is None or a["quote"] not in span:
                    print(f"{where}: the quoted words do not stand in {a['cc_ref']}"); return 1
                out_arms.append(OrderedDict([("when", sel), ("doors", a["doors"]), ("cc_ref", a["cc_ref"])]))
            row["count"] = {"value": " ; ".join((x["when"] + " => " if x["when"] != "*" else "") + x["doors"] for x in out_arms),
                            "arms": out_arms, "source": "cc-table"}
        elif row["cosign_rule"].get("value") == "none":
            row["count"] = {"value": "none", "source": "generic", "note": "the cosign cell reads none: one signature carries the row"}
        else:
            row["count"] = {"value": None, "source": "gap", "note": "the cosign cell is not none and no arm is typed", "cosign_rule": row["cosign_rule"].get("value")}
        er = row["erasure_route"].get("value")
        erh = head_of(er) if isinstance(er, str) else (head_of(er[0]) if isinstance(er, list) and er else None)
        if erh in ("dsar", "purge"):
            row["blind"] = {"value": ["body.note"], "source": "derived", "note": "from erasure_route; further free-text and other-authored members are named with the family's ruled row"}
        elif erh in ("none", "legal_hold"):
            row["blind"] = {"value": [], "source": "derived", "note": "from erasure_route: sealed"}
        else:
            row["blind"] = {"value": None, "source": "gap", "note": "erasure_route unread"}
        if z:
            vc = [v.strip() for v in z.get("verbs_admitted", "").split(",") if v.strip()]
            row["verbs_code"] = {"value": vc, "delta_vs_cc": z.get("verbs_delta", ""), "source": "code-v61"}
            row["maintains_record_code"] = {"value": z.get("maintains_record_code", "").startswith("yes"), "source": "code-v61", "note": z.get("maintains_record_code", "")}
            row["reference_code"] = {"value": reference_code(z.get("15_reference_rule")), "source": "code-v61" if reference_code(z.get("15_reference_rule")) else "gap"}
            row["reserved"] = {"value": z.get("reserved", "") == "true", "rule": z.get("reserved_rule", ""), "source": "cc-table"}
            row["code_v61"] = {"door": z.get("door", ""), "witness": z.get("witness", ""), "formal_witness": z.get("formal_witness", ""),
                                "carries_kind_census": z.get("carries_kind", ""), "sources": z.get("sources", "")}
        rows.append(row)
    if signer_text:
        print("signer_rule_text.tsv names families outside the model: " + ", ".join(sorted(signer_text))); return 1
    if cell_text:
        print("cell_text.tsv names families outside the model: " + ", ".join(sorted(cell_text))); return 1
    # The body of a family from the signed-object table (CC 2.6.1.7): each member whose presence that table states for
    # a wire form of the family, with its type. A presence written in words that name no wire form is left to the
    # table and counted. A cell the census reads as prose is not replaced.
    all_fams = [r["family"] for r in rows]
    def owners(name):
        name = re.sub(r":v\d+$", "", name.strip())
        if name.endswith(":*"):
            return [(f, None) for f in all_fams if f.startswith(name[:-1])]
        if name in by_fam_names: return [(name, None)]
        return [(f, name) for f in all_fams if "{" in f and gg.family_ok(name, {f})]
    by_fam_names = set(all_fams)
    body_members, body_unread = OrderedDict(), []
    for so in csv.DictReader(open(SIGNED_OBJECT, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
        if so["object"] != "attestation_row": continue
        for mode, lst in re.findall(r"(REQUIRED|OPTIONAL) on ([^;()]+)", so["presence"]):
            for name in [x.strip() for x in re.split(r",| and ", lst) if x.strip()]:
                own = owners(name) if re.fullmatch(r"[a-z_]+(:[a-z_{}*0-9]+)+", name) else []
                if not own:
                    body_unread.append(f"{so['member']}: {name}"); continue
                for fam, leaf in own:
                    e = OrderedDict([("member", so["member"]), ("type", so["type"]), ("presence", mode.lower())])
                    if leaf: e["leaf"] = leaf
                    if e not in body_members.setdefault(fam, []): body_members[fam].append(e)
    body_text_n = Counter()
    for bt in csv.DictReader([l for l in open(os.path.join(ROOT, "formal/derivation/body_text.tsv"), encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE):
        where = f"body_text.tsv: {bt['family']} {bt['member']} ({bt['cc_ref']})"
        if bt["family"] not in by_fam_names or bt["presence"] not in ("required", "optional", "forbidden", "unstated") or bt["in_cddl"] not in ("yes", "no"):
            print(f"{where}: no such family, or a presence or in_cddl value outside its words"); return 1
        span = section_span(bt["cc_ref"])
        if span is None or bt["quote"] not in span:
            print(f"{where}: the quoted words do not stand in {bt['cc_ref']}"); return 1
        lst = body_members.setdefault(bt["family"], [])
        if not any(e["member"] == bt["member"] for e in lst):
            lst.append(OrderedDict([("member", bt["member"]), ("type", bt["type"]), ("presence", bt["presence"]),
                                    ("in_cddl", bt["in_cddl"] == "yes"), ("cc_ref", bt["cc_ref"])]))
            body_text_n[bt["in_cddl"]] += 1
    for r in rows:
        mem = body_members.get(r["family"])
        if mem and r["body"].get("source") == "gap":
            r["body"] = {"value": OrderedDict([("members", mem)]), "source": "cc-table", "cc_ref": "CC 2.6.1.7",
                         "code": {"value": r["body"].get("value"), "source": "gap"},
                         "note": "the members the signed-object table states for this family's wire forms, and those the text states (each with its section and whether the name is in the CDDL), beyond those every row carries"}
    # The sentences that state a closed cell: the cell gains the sections that say it, its value untouched.
    by_fam = {r["family"]: r for r in rows}
    cited = 0
    for ct in csv.DictReader([l for l in open(CELL_CITES, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE):
        where = f"cell_cites.tsv: {ct['family']} {ct['column']} ({ct['cc_ref']})"
        cellv = by_fam.get(ct["family"], {}).get(ct["column"])
        if not isinstance(cellv, dict) or ct["reading"] not in ("agree", "fills"):
            print(f"{where}: no such cell, or a reading that is not agree or fills"); return 1
        if cellv.get("source") == "gap":
            print(f"{where}: the cell is open; state its value in cell_text.tsv"); return 1
        span = section_span(ct["cc_ref"])
        if span is None or ct["quote"] not in span:
            print(f"{where}: the quoted words do not stand in {ct['cc_ref']}"); return 1
        cites = cellv.setdefault("cites", [])
        entry = next((x for x in cites if x["cc_ref"] == ct["cc_ref"]), None)
        if entry is None:
            cites.append(OrderedDict([("cc_ref", ct["cc_ref"]), ("reading", ct["reading"])])); cited += 1
        elif ct["reading"] == "fills":
            entry["reading"] = "fills"
    reader_defaults = []
    for rd in csv.DictReader([l for l in open(os.path.join(ROOT, "formal/derivation/fold_reader_defaults.tsv"), encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE):
        try:
            fg.parse(rd["fold"])
        except fg.FoldError as e:
            print(f"fold_reader_defaults.tsv: {rd['polarity']}: {e}"); return 1
        span = section_span(rd["cc_ref"])
        if span is None or rd["quote"] not in span:
            print(f"fold_reader_defaults.tsv: {rd['polarity']}: the quoted words do not stand in {rd['cc_ref']}"); return 1
        reader_defaults.append(OrderedDict([("polarity", rd["polarity"]), ("fold", rd["fold"]), ("cc_ref", rd["cc_ref"])]))
    if "*" in fold_text:
        fold_every = fold_cell("*", fold_text.pop("*"))
        if fold_every is None: return 1
    if fold_text:
        print("fold_text.tsv names families outside the model: " + ", ".join(sorted(fold_text))); return 1
    if sum(fold_marks.values()) > FOLD_MARKS_MAX:
        print(f"fold: {sum(fold_marks.values())} uses of words no other vocabulary has, more than {FOLD_MARKS_MAX}"); return 1
    if count_text:
        print("count_text.tsv names families outside the model: " + ", ".join(sorted(count_text))); return 1
    count_open = [r["family"] for r in rows if r["count"]["source"] == "gap"]
    if len(count_open) > COUNT_OPEN_MAX:
        print(f"count: {len(count_open)} families have a cosign cell and no typed count, more than {COUNT_OPEN_MAX}: " + ", ".join(count_open)); return 1
    # The default row: the value a family takes in each of these columns unless it states its own.
    # Pinned as data, and held to be the commonest value of its column, so a change of default is a
    # deliberate edit and never a drift. Each row lists the columns in which it departs.
    default = json.load(open(DEFAULT, encoding="utf-8"), object_pairs_hook=OrderedDict)["columns"]
    canon = lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False)
    for col, dv in default.items():
        cnt = Counter(canon(r[col].get("value")) for r in rows)
        top, n = cnt.most_common(1)[0]
        if canon(dv) != top:
            print(f"family_default_row.json: the default for {col} is held by {cnt.get(canon(dv), 0)} families and another value by {n}"); return 1
    departures = []
    for r in rows:
        r["departs"] = [col for col, dv in default.items() if canon(r[col].get("value")) != canon(dv)]
    # Every departure carries its reason: when a family leaves the default and why, or the open question.
    spec, claims, opens, errs = departure_reasons(rows, default)
    if errs:
        print("departure_reasons.json: FAIL"); [print("  " + e) for e in errs]; return 1
    for r in rows:
        r["because"] = OrderedDict((col, claims.get((r["family"], col)) or "open") for col in r["departs"])
        departures += [(r["family"], col, "; ".join(claims.get((r["family"], col)) or ["open"]), canon(r[col].get("value"))) for col in r["departs"]]
    md_out = reasons_md(spec, claims, opens, rows, default) + "\n"
    by_count = Counter(len(r["departs"]) for r in rows)
    dep_out = ("# Every family against the default row (formal/derivation/family_default_row.json): one line per column in which a family departs.\n"
               "# A family with no line here is the default row in all of these columns. Generated by tools/build_family_model.py.\n"
               "# reason: the reasons of formal/derivation/departure_reasons.json that move the cell, or open; formal/family_model/DEPARTURES.md states each.\n"
               "family\tcolumn\treason\tvalue\n" + "".join(f"{f}\t{c}\t{w}\t{v}\n" for f, c, w, v in departures))
    cov = OrderedDict()
    SRC = ("cc-table", "code-v61", "generic", "prose", "mixed", "gap")
    for col in COLUMNS:
        cnt = Counter(r[col]["source"] for r in rows if col in r)
        cov[col] = OrderedDict((k, cnt.get(k, 0)) for k in SRC)
        if col in SUBKEYS:
            subcnt = Counter(v["source"] for r in rows if col in r for v in r[col].get("parts", {}).values())
            cov[col]["sub_cells"] = OrderedDict((k, subcnt.get(k, 0)) for k in SRC)
    reg_sha = hashlib.sha256(open(REG, "rb").read()).hexdigest()
    meta = OrderedDict([
        ("cc_section", "3.1 (the family model manifest, CIRISConstitution#189)"),
        ("version", "0-draft"), ("taxonomy_version", "11+1 v1"),
        ("registry_sha256", reg_sha), ("census", "CIRISPersist release-61.0.0 ea6ab724, #1130 comment 6563875341"),
        ("columns", COLUMNS), ("families", len(rows)), ("coverage", cov),
        ("cites", OrderedDict([("source", "formal/derivation/cell_cites.tsv"), ("cells_cited", sum(1 for r in rows for c in r.values() if isinstance(c, dict) and c.get("cites"))),
                               ("citations", cited), ("reading", "a cell with `cites` is stated by those sections; `fills` marks a sentence that says more than the cell holds")])),
        ("body", OrderedDict([("source", "constitution/signed_object.tsv"), ("families_with_members", sum(1 for r in rows if isinstance(r["body"].get("value"), dict) and "members" in r["body"]["value"])),
                              ("presence_in_words", sorted(set(body_unread))),
                              ("members_from_text", OrderedDict([("in_cddl", body_text_n["yes"]), ("named_by_the_text_alone", body_text_n["no"])]))])),
        ("fold", OrderedDict([("default", fg.DEFAULT), ("every_family", fold_every), ("reader_defaults", reader_defaults),
                              ("typed_families", sum(1 for r in rows if r["fold"]["value"])),
                              ("statements", sum(len(r["fold"]["value"]) for r in rows)),
                              ("marks", OrderedDict(sorted(fold_marks.items()))), ("marks_total", sum(fold_marks.values()))])),
        ("default_row", OrderedDict([("columns", default), ("families_on_it", by_count.get(0, 0)),
                                     ("families_by_departures", OrderedDict((str(k), by_count[k]) for k in sorted(by_count))),
                                     ("reading", "a family's cell in one of these columns is the default unless the family is listed in departs; manifests/family_departures.tsv carries the departures alone")])),
        ("departure_reasons", OrderedDict([
            ("reasons", [OrderedDict([("id", rs["id"]), ("title", rs["title"]), ("when", rs["when"]), ("why", rs["why"]), ("basis", rs["basis"])] +
                                     ([("cc_ref", rs["cc_ref"]), ("quote", rs["quote"])] if rs["basis"] == "text" else []) +
                                     [("cells", sum(1 for v in claims.values() if rs["id"] in v))]) for rs in spec["reasons"]]),
            ("open", [OrderedDict([("family", f), ("column", c), ("question", q)]) for (f, c), q in opens.items()]),
            ("reading", "every departing cell names in because the reasons that move it, or open; a departure with no reason fails the build, and so does a reason whose cell sits on the default")])),
        ("reading", "every cell carries its source: cc-table (the CC classification), code-v61 (what persist's door enforces for this family), generic (the generic door's value, not the family's), prose (bespoke code outside the closed vocabulary), mixed (a compound cell whose parts differ; see parts), gap (nothing enforces; a value after the tag is the de-facto or target value). A signer rule the text gives where the code enforces none, or holds the family shut, is cc-table, with the census reading kept beside it as code; where the text gives one signer per stage the value is keyed by stage (per_stage). Census-only readings ride beside the CC columns as verbs_code, maintains_record_code, reference_code and reserved. A ruled version replaces every generic, prose, mixed and gap cell with a closed value and refuses what remains."),
    ])
    out = json.dumps(OrderedDict([("_meta", meta), ("rows", rows)]), indent=1, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != out: print("family_model.json is stale (run tools/build_family_model.py)"); return 1
        cur = open(DEPARTS, encoding="utf-8").read() if os.path.exists(DEPARTS) else ""
        if cur != dep_out: print("family_departures.tsv is stale (run tools/build_family_model.py)"); return 1
        cur = open(REASONS_MD, encoding="utf-8").read() if os.path.exists(REASONS_MD) else ""
        if cur != md_out: print("DEPARTURES.md is stale (run tools/build_family_model.py)"); return 1
    else:
        open(OUT, "w", encoding="utf-8").write(out)
        open(DEPARTS, "w", encoding="utf-8").write(dep_out)
        open(REASONS_MD, "w", encoding="utf-8").write(md_out)
    print(f"departure reasons: {len(spec['reasons'])} reasons move {len(claims)} cells; {len(opens)} open")
    print(f"default row: {by_count.get(0, 0)} of {len(rows)} families are on it in all {len(default)} columns, {by_count.get(1, 0)} depart in one; {len(departures)} departures in all")
    print(f"family_model: {len(rows)} families; coverage per column (cc-table/code-v61/generic/prose/mixed/gap): " +
          "; ".join(f"{k} {v['cc-table']}/{v['code-v61']}/{v['generic']}/{v['prose']}/{v['mixed']}/{v['gap']}" for k, v in cov.items()))
    return 0
if __name__ == "__main__":
    sys.exit(main())
