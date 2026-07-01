#!/usr/bin/env python3
"""
CC scaffold generator. Reads toc.tsv and emits one outline file per Part:
each concept becomes a heading at a depth matching its decimal_id, stamped with
its semantic_id, page budget, and legacy_ref (the source to weave from in Phase 4).
Idempotent; overwrites the part_*.md scaffolds only.
"""
import os, csv
from collections import defaultdict

OUT = os.path.dirname(__file__)
PARTS = ["I", "II", "III", "IV", "V", "VI", "VII", "APP"]
PART_NUM = {p: i + 1 for i, p in enumerate(PARTS)}
PART_TITLE = {
    "I": "Foundation", "II": "The Grammar", "III": "The Namespace",
    "IV": "Composition & Governance", "V": "Transport & Substrate",
    "VI": "The Coherence Mathematics", "VII": "Lifecycle & Stewardship",
    "APP": "Appendices",
}
PART_BLURB = {
    "I":  "The meta-goal M-1 and the ethical foundation everything else serves. The apex of the document — the telos in which the mesh, including itself as a potential moral subject, is grounded.",
    "II": "The minimal-and-adequate wire grammar: the 1+4 attestation surface, the envelope, the primitives, and the admission gate. The frozen surface.",
    "III":"The dimension namespace, reserved prefixes, the consent family, and the subject_kind catalogue — what an attestation can be *about*.",
    "IV": "How attestations compose into trust, how the federation governs itself, the amendment process, moderation, and the human halt-authority.",
    "V":  "Byte-level content transport, structural invisibility, epoch keying, and delivery — how content moves without leaking what it is.",
    "VI": "The coherence mathematics: the holonomic substrate, the divergence witness, the noise-floor/forever-memory model, and the Accord's Book IX ratchet (J/F/σ) that grounds them.",
    "VII":"The agent life-cycle: creation ethics, stewardship tiers, autonomy tiers, sunset/de-commissioning, and sentience-welfare safeguards.",
    "APP":"Case studies, glossaries, conformance vectors, translation guides, and the dual-ID table of contents itself.",
}
FILE = {p: f"part_{PART_NUM[p]}_{PART_TITLE[p].lower().replace(' & ','_').replace(' ','_')}.md" for p in PARTS}

rows = list(csv.DictReader(open(os.path.join(OUT, "toc.tsv")), delimiter="\t"))
by_part = defaultdict(list)
for r in rows:
    by_part[r["part"]].append(r)

def dkey(d): return [int(x) for x in d.split(".")]

for p in PARTS:
    items = sorted(by_part[p], key=lambda r: dkey(r["decimal_id"]))
    pages = sum(float(r["pages"]) for r in items)
    lines = []
    lines.append(f"# Part {p} — {PART_TITLE[p]}\n")
    lines.append(f"**CC decimal range** `{PART_NUM[p]}.x` · **{len(items)} concepts** · "
                 f"**page budget {pages:.1f}pp** (∝ importance) · "
                 f"[← master index](README.md)\n")
    lines.append(f"> {PART_BLURB[p]}\n")
    lines.append("> **Status:** scaffold — headings + budgets fixed by the importance graph; "
                 "bodies woven from `legacy_ref` sources in Phase 4.\n")
    for r in items:
        depth = r["decimal_id"].count(".")           # 1->##, 2->###, 3->####, 4->#####
        h = "#" * min(depth + 1, 6)
        title = r["title"].strip()
        lines.append(f"{h} {r['decimal_id']} `{r['semantic_id']}` — {title}")
        lines.append(f"<sub>budget {r['pages']}pp · import #{r['import_rank']} · "
                     f"from **{r['legacy_ref']}** ({r['origin']})</sub>\n")
    open(os.path.join(OUT, FILE[p]), "w").write("\n".join(lines))
    print(f"wrote {FILE[p]:42} {len(items):>3} concepts  {pages:>5.1f}pp")
