#!/usr/bin/env python3
"""The family model manifest, draft 0: every scores family as one row over the agreed columns.

Sources: the CC table (formal/derivation/family_kind_verb.tsv: kind, side, verbs, maintains_record,
reference) and persist's census at the v61 head (formal/derivation/census_v61.tsv: what the code
enforces today on each axis). Every cell carries its value and its source: cc-table, code-v61,
prose (bespoke code outside the closed vocabulary), or gap (nothing enforces). The vendor gate of a
later version refuses a gap; this draft counts them. Writes manifests/family_model.json; --check
only compares.
"""
import csv, hashlib, json, os, re, sys
from collections import Counter, OrderedDict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CC = os.path.join(ROOT, "formal/derivation/family_kind_verb.tsv")
CENSUS = os.path.join(ROOT, "formal/derivation/census_v61.tsv")
REG = os.path.join(ROOT, "manifests/namespace_registry.json")
OUT = os.path.join(ROOT, "manifests/family_model.json")
COLUMNS = OrderedDict([
    ("kind", "Priorities | Rules | Manner | Identity | Confidence | Facts | Circumstances | Process | Model | Structure | Premises"),
    ("side", "thing | account (a function of kind)"),
    ("verbs", "subset of {attest, authorize, replace, withdraw, recant}"),
    ("maintains_record", "bool: the row is itself the evidence that something happened; fixes erasure and projection"),
    ("reference", "none | pre:<kind|any> | carry:<kind> (the row it names; only a carry is a cell of the carries grid)"),
    ("placement", "self_collective | targeted_family | targeted_room | commons | addressed"),
    ("signer_rule", "{self | owner_of_subject | seat_role(duty) | roster_member(at) | minter | steward | any_registered} x via {none | delegates_to(scope, depth, term, caps)} x conditions ⊆ {adult, capacitated, not_subject, not_author}"),
    ("subject_rule", "{subject_kind, cardinality, must_be_registered, for_key_id ∈ {none, serve_seat, recipient}, in_audience, attested_party, subject_blind}"),
    ("cosign_rule", "none | group_consensus_protocol | moderator_quorum | accord | deciding_seat_plus_outside"),
    ("polarity", "the registry's polarity class"),
    ("body", "CDDL reference beyond the signed object; an existence_only audience names a two-part shape"),
    ("freshness", "{judged_at ∈ {signed_instant_with_W, receipt}, W}"),
    ("lifecycle", "{withdraws_by ⊆ {attester, subject, cosigned}, retraction_class ∈ {peer, duty_record, authority_act, cosigned}, supersedes ∈ {same_attester, none}, expires, rotation_on_removal}"),
    ("replication", "{tier ∈ {local, cohort, federation}, audience ∈ {cohort, cohort_plus_subjects(full|existence_only), addressee, everyone}, non_recipient ∈ {drop, hold_sealed}, held ∈ {settle_on_key, refuse}}"),
    ("projection", "{table, rebuild ∈ {byte_equal, none}}"),
    ("erasure_route", "dsar | purge | legal_hold | none"),
    ("governance", "policy_row | none"),
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

def main():
    cc = {r["family"]: r for r in csv.DictReader(open(CC, encoding="utf-8"), delimiter="\t")}
    census_lines = [l for l in open(CENSUS, encoding="utf-8").read().split("\n") if not l.startswith("#")]
    census = {r["prefix"]: r for r in csv.DictReader(census_lines, delimiter="\t")}
    reg = json.load(open(REG, encoding="utf-8"))
    pol = {}
    for f in reg.get("families", []):
        if isinstance(f, dict) and "prefix" in f: pol[f["prefix"]] = f.get("polarity")
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
        pv = polarity_census(z["6_polarity"]) if z else None
        row["polarity"] = {"value": pv or pol.get(fam), "source": "code-v61" if pv else ("cc-table" if pol.get(fam) else "gap"), "registry": pol.get(fam)}
        for col in ("derived", "confers", "binds_segment"):
            row[col] = {"value": None, "source": "gap", "note": "new column; values come with the manifest's first ruled version"}
        if z:
            vc = [v.strip() for v in z.get("verbs_admitted", "").split(",") if v.strip()]
            row["verbs_code"] = {"value": vc, "delta_vs_cc": z.get("verbs_delta", ""), "source": "code-v61"}
            row["maintains_record_code"] = {"value": z.get("maintains_record_code", "").startswith("yes"), "source": "code-v61", "note": z.get("maintains_record_code", "")}
            row["reference_code"] = {"value": reference_code(z.get("15_reference_rule")), "source": "code-v61" if reference_code(z.get("15_reference_rule")) else "gap"}
            row["reserved"] = {"value": z.get("reserved", "") == "true", "rule": z.get("reserved_rule", ""), "source": "cc-table"}
            row["code_v61"] = {"door": z.get("door", ""), "witness": z.get("witness", ""), "formal_witness": z.get("formal_witness", ""),
                                "carries_kind_census": z.get("carries_kind", ""), "sources": z.get("sources", "")}
        rows.append(row)
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
        ("reading", "every cell carries its source: cc-table (the CC classification), code-v61 (what persist's door enforces for this family), generic (the generic door's value, not the family's), prose (bespoke code outside the closed vocabulary), mixed (a compound cell whose parts differ; see parts), gap (nothing enforces; a value after the tag is the de-facto or target value). Census-only readings ride beside the CC columns as verbs_code, maintains_record_code, reference_code and reserved. A ruled version replaces every generic, prose, mixed and gap cell with a closed value and refuses what remains."),
    ])
    out = json.dumps(OrderedDict([("_meta", meta), ("rows", rows)]), indent=1, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != out: print("family_model.json is stale (run tools/build_family_model.py)"); return 1
    else:
        open(OUT, "w", encoding="utf-8").write(out)
    print(f"family_model: {len(rows)} families; coverage per column (cc-table/code-v61/generic/prose/mixed/gap): " +
          "; ".join(f"{k} {v['cc-table']}/{v['code-v61']}/{v['generic']}/{v['prose']}/{v['mixed']}/{v['gap']}" for k, v in cov.items()))
    return 0
if __name__ == "__main__":
    sys.exit(main())
