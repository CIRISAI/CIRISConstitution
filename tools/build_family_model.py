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
def cell(text):
    t = (text or "").strip()
    if not t or t == "—": return {"value": None, "source": "gap"}
    head = t.split(":", 1)[0].strip()
    if head == "GAP": return {"value": None, "source": "gap", "note": t[4:].strip(" :")}
    if head == "PROSE": return {"value": None, "source": "prose", "note": t[6:].strip(" :")}
    if head == "GENERIC": return {"value": t.split(":", 1)[1].strip() if ":" in t else t, "source": "code-v61", "note": "the generic door, not a per-family value"}
    if head == "DATA": return {"value": t.split(":", 1)[1].strip() if ":" in t else t, "source": "code-v61"}
    return {"value": t, "source": "code-v61"}
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
            row[col] = cell(z[zc]) if z else {"value": None, "source": "gap", "note": "not in the census"}
        row["polarity"] = {"value": pol.get(fam), "source": "cc-table" if pol.get(fam) else "gap"}
        for col in ("derived", "confers", "binds_segment"):
            row[col] = {"value": None, "source": "gap", "note": "new column; values come with the manifest's first ruled version"}
        if z:
            row["code_v61"] = {"door": z.get("door", ""), "verbs_admitted": z.get("verbs_admitted", ""), "maintains_record_code": z.get("maintains_record_code", ""),
                                "witness": z.get("witness", ""), "formal_witness": z.get("formal_witness", "")}
        rows.append(row)
    cov = OrderedDict()
    for col in COLUMNS:
        cnt = Counter(r[col]["source"] for r in rows if col in r)
        cov[col] = OrderedDict((k, cnt.get(k, 0)) for k in ("cc-table", "code-v61", "prose", "gap"))
    reg_sha = hashlib.sha256(open(REG, "rb").read()).hexdigest()
    meta = OrderedDict([
        ("cc_section", "3.1 (the family model manifest, CIRISConstitution#189)"),
        ("version", "0-draft"), ("taxonomy_version", "11+1 v1"),
        ("registry_sha256", reg_sha), ("census", "CIRISPersist release-61.0.0 ea6ab724, #1130 comment 6563875341"),
        ("columns", COLUMNS), ("families", len(rows)), ("coverage", cov),
        ("reading", "every cell carries its source: cc-table (the CC classification), code-v61 (what persist's door enforces today), prose (bespoke code outside the closed vocabulary), gap (nothing enforces). A ruled version replaces every prose and gap cell with a closed value and refuses what remains."),
    ])
    out = json.dumps(OrderedDict([("_meta", meta), ("rows", rows)]), indent=1, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != out: print("family_model.json is stale (run tools/build_family_model.py)"); return 1
    else:
        open(OUT, "w", encoding="utf-8").write(out)
    print(f"family_model: {len(rows)} families; coverage per column (cc-table/code-v61/prose/gap): " +
          "; ".join(f"{k} {v['cc-table']}/{v['code-v61']}/{v['prose']}/{v['gap']}" for k, v in cov.items()))
    return 0
if __name__ == "__main__":
    sys.exit(main())
