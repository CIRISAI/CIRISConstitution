#!/usr/bin/env python3
"""
Assemble the CIRIS Constitution Part files from the verbatim copy-migration fragments
(migrated/*.json). For each of the 392 TOC slots, pull the copied body, dedup (longest
verbatim body wins on overlap), clean history/editorializing (cc_clean), and emit under
its decimal heading in the correct Part. Reports coverage + any slot still needing source.
"""
import json, csv, glob, os
from collections import defaultdict
from cc_clean import clean_history

HERE = os.path.dirname(__file__)
PART_FILE = {1:"part_1_foundation.md",2:"part_2_the_grammar.md",3:"part_3_the_namespace.md",
             4:"part_4_composition_governance.md",5:"part_5_transport_substrate.md",
             6:"part_6_the_coherence_mathematics.md",7:"part_7_lifecycle_stewardship.md",
             8:"part_8_appendices.md"}
PART_TITLE = {1:"Foundation",2:"The Grammar",3:"The Namespace",4:"Composition & Governance",
              5:"Transport & Substrate",6:"The Coherence Mathematics",7:"Lifecycle & Stewardship",8:"Appendices"}
PART_BLURB = {
 1:"The meta-goal M-1 and the ethical foundation the federation serves.",
 2:"The minimal-and-adequate wire grammar: the envelope, the five primitives, conformance, and canonicalization.",
 3:"The dimension namespace, reserved prefixes, the consent family, and the subject_kind catalogue.",
 4:"How attestations compose into trust; self-governance, amendment, moderation, and the human halt-authority.",
 5:"Byte-level content transport, structural invisibility, epoch keying, and delivery.",
 6:"The holonomic substrate, the divergence witness, the noise-floor model, and the coherence mathematics.",
 7:"Creation ethics, stewardship & autonomy tiers, sunset, and the sentience-welfare safeguards.",
 8:"Case studies, glossaries, conformance vectors, interop, and the dual-ID table of contents.",
}

# --- TOC: the 392 authoritative slots, in order ---
toc = list(csv.DictReader(open(os.path.join(HERE,"toc.tsv")), delimiter="\t"))

# --- fragments: decimal -> candidate bodies ---
cand = defaultdict(list)
for fn in glob.glob(os.path.join(HERE,"migrated","*.json")):
    for s in json.load(open(fn)):
        cand[s["decimal_id"]].append(s.get("body","") or "")

def best_body(dec):
    bodies = [clean_history(b) for b in cand.get(dec,[])]
    bodies = [b for b in bodies if b.strip()]
    return max(bodies, key=len) if bodies else ""

def dkey(d): return [int(x) for x in d.split(".")]

placed = missing = 0
missing_list = []
by_part = defaultdict(list)
for r in toc:
    by_part[int(r["decimal_id"].split(".")[0])].append(r)

for pnum, rows in by_part.items():
    rows.sort(key=lambda r: dkey(r["decimal_id"]))
    pages = sum(float(r["pages"]) for r in rows)
    out = [f"# Part {pnum} — {PART_TITLE[pnum]}\n",
           f"**Decimal range** `{pnum}.x` · **{len(rows)} sections** · **page budget {pages:.0f}pp** · "
           f"[← master index](README.md)\n",
           f"> {PART_BLURB[pnum]}\n", "---\n"]
    for r in rows:
        dec = r["decimal_id"]; depth = min(dec.count(".")+1, 6)
        out.append(f"{'#'*depth} {dec} `{r['semantic_id']}` — {r['title'].strip()}")
        body = best_body(dec)
        if body.strip():
            out.append(""); out.append(body.strip()); out.append("")
            placed += 1
        else:
            out.append(f"\n*[source content to migrate — from {r['legacy_ref']}]*\n")
            missing += 1; missing_list.append((dec, r["legacy_ref"], r["semantic_id"]))
    open(os.path.join(HERE, PART_FILE[pnum]), "w").write("\n".join(out))

print(f"assembled 8 Part files. sections with copied body: {placed}/392 | needing source: {missing}")
if missing_list:
    print("slots still needing source:")
    for dec, leg, sem in sorted(missing_list, key=lambda x: dkey(x[0])):
        print(f"  {dec:<10} {sem:<22} ← {leg}")
