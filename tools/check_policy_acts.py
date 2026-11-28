#!/usr/bin/env python3
"""Check constitution/governance_policy_acts.tsv: every policy an act may take is a row of the governance policy
table, every cited section is in the table of contents, no (act, scope, community kind) is stated twice, a `fixed` act
names one row, every row of the policy table is taken by at least one act, and every family an act names is a family
of the family model."""
import csv, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rows(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return list(csv.DictReader((l for l in f if not l.startswith("#")), delimiter="\t", quoting=csv.QUOTE_NONE))
policy = {r["family"] for r in rows("constitution/governance_policy.tsv")}
import json
families = {r["family"] for r in json.load(open(os.path.join(ROOT, "manifests/family_model.json"), encoding="utf-8"))["rows"]}
toc = open(os.path.join(ROOT, "constitution/toc.tsv"), encoding="utf-8").read()
bad, seen, used = [], set(), set()
acts = rows("constitution/governance_policy_acts.tsv")
for r in acts:
    k = (r["act"], r["scope"], r["community_kind"])
    if k in seen: bad.append("stated twice: %s" % (k,))
    seen.add(k)
    ps = [q for part in r["policy"].split("|") for q in part.split("&")]
    for p in ps:
        if p not in policy: bad.append("%s: %r is no row of the policy table" % (k, p))
        used.add(p)
    for fam in ([] if r.get("families") in ("—", None) else r["families"].split("|")):
        if fam not in families: bad.append("%s: %r is no family of the family model" % (k, fam))
    if r.get("families") is None: bad.append("%s: no families cell" % (k,))
    if r["choice"] not in ("fixed", "row"): bad.append("%s: choice %r" % (k, r["choice"]))
    if r["choice"] == "fixed" and "|" in r["policy"]: bad.append("%s: a fixed act names one row" % (k,))
    for s in r["cc_ref"].split():
        if ("\t" + s + "\t") not in toc and not toc.startswith(s + "\t") and ("\n" + s + "\t") not in toc:
            bad.append("%s: section %s is not in the table of contents" % (k, s))
for p in sorted(policy - used): bad.append("policy row %s is taken by no act" % p)
for b in bad: print("policy acts:", b)
print("policy acts: %d acts over %d policy rows; %d defect(s)" % (len(acts), len(policy), len(bad)))
sys.exit(1 if bad else 0)
