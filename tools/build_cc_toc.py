#!/usr/bin/env python3
"""
CC (the CIRIS Constitution) — unified-constitution TOC builder.

Reads the importance + structure analysis from FSD/CEG/taxonomy/ and emits the
addressing spine of the unified CEG+Accord constitution:

  toc.tsv       one row per concept: decimal_id · semantic_id · title · legacy_ref · p_i · import_rank · pages · part · origin
  codebook.json bijective maps: decimal_id<->key, semantic_id<->key, legacy_ref->decimal_id (+ determinism note)

Structuring principle (the user's spec): IMPORTANCE (PageRank p_i over the unified
graph) sets each concept's structural DEPTH (chapter/section/subsection) and its
PAGE BUDGET (p_i x 120pp). Community/cluster only informs which Part a concept lives in.
Analysis-derived; reads only, writes only into FSD/CC/.
"""
import json, os, re
from collections import defaultdict

TAX = os.path.join(os.path.dirname(__file__), "..", "CEG", "taxonomy")
OUT = os.path.dirname(__file__)
TOTAL_PAGES = 120.0

U = json.load(open(os.path.join(TAX, "graph_unified.json")))
PR = U["unified_pagerank"]                          # conscious-mesh (iii) weights — the canonical design
ACC = U["accord_nodes"]                            # accord id -> title
CEG = {n["id"]: n for n in json.load(open(os.path.join(TAX, "graph.json")))["nodes"]}

# ---- Part assignment -------------------------------------------------------
# 8 ordered top-level Parts. Importance sets depth+budget WITHIN; this only places.
PARTS = ["I", "II", "III", "IV", "V", "VI", "VII", "APP"]
PART_TITLE = {
    "I":   "Foundation",
    "II":  "The Grammar",
    "III": "The Namespace",
    "IV":  "Composition & Governance",
    "V":   "Transport & Substrate",
    "VI":  "The Coherence Mathematics",
    "VII": "Lifecycle & Stewardship",
    "APP": "Appendices",
}
PART_NUM = {p: i + 1 for i, p in enumerate(PARTS)}   # I->1 ... APP->8

CEG_TOP_PART = {  # CEG top-level § number -> Part
    "0": "II", "1": "I", "2": "II", "3": "II", "4": "II",
    "5": "III", "6": "III", "7": "III",
    "8": "IV", "9": "IV", "11": "IV", "13": "IV",
    "10": "V", "19": "VI",
    "12": "APP", "14": "APP", "15": "APP", "16": "APP", "17": "APP", "18": "APP",
}

# Accord conceptual ids -> (Part, semantic_id)
ACC_CONCEPT = {
    "A§M-1": ("I", "meta-goal"), "A§fail": ("I", "fail-secure"),
    "A§PDMA": ("I", "pdma"), "A§WBD": ("I", "deferral"), "A§WA": ("IV", "wise-authority"),
    "A§P.ben": ("I", "beneficence"), "A§P.non": ("I", "non-maleficence"),
    "A§P.int": ("I", "integrity"), "A§P.fid": ("I", "fidelity"),
    "A§P.aut": ("I", "autonomy"), "A§P.jus": ("I", "justice"),
    "A§J": ("VI", "defense-function"), "A§F": ("VI", "flourishing-function"),
    "A§sigma": ("VI", "sustainability-integral"), "A§ratchet": ("VI", "coherence-ratchet"),
    "A§A0": ("VII", "autonomy-tier-a0"), "A§A1": ("VII", "autonomy-tier-a1"),
    "A§A2": ("VII", "autonomy-tier-a2"), "A§A3": ("VII", "autonomy-tier-a3"),
    "A§A4": ("VII", "autonomy-tier-a4"), "A§DCP": ("VII", "decommissioning"),
}

def accord_book_part(aid):
    # A§<book>.<...>  book 0 preamble, 1 core-identity, 2 PDMA, 3 case-studies,
    # 4 obligations, 5 becoming, 6 creation/ST, 7 war-ethics, 8 sunset
    m = re.match(r"A§(\d+)\.", aid)
    b = m.group(1) if m else None
    return {"0": "I", "1": "I", "2": "I", "3": "APP",
            "4": "VII", "5": "VII", "6": "VII", "7": "VII", "8": "VII"}.get(b, "VII")

def part_of(key):
    if key.startswith("A§"):
        if key in ACC_CONCEPT:
            return ACC_CONCEPT[key][0]
        return accord_book_part(key)
    top = key.split(".")[0]
    return CEG_TOP_PART.get(top, "APP")

def title_of(key):
    if key.startswith("A§"):
        v = ACC.get(key, key)
        if isinstance(v, dict):
            v = v.get("title") or v.get("heavy_title") or key
        return v
    return CEG.get(key, {}).get("title", "") or key

def origin_of(key):
    return "accord" if key.startswith("A§") else "ceg"

def legacy_of(key):
    if key.startswith("A§"):
        return "Accord " + key[2:]
    return "§" + key

# ---- semantic_id (genericized, unique) -------------------------------------
STOP = set("the a an of and or to for in on with is are be by as at into from over under".split())
GENERIC = {  # de-brand the product family (matches the toc genericization)
    "cirisregistry": "registry", "cirisagent": "agent", "cirisverify": "verifier",
    "cirispersist": "store", "cirisedge": "transport", "cirislens": "observability",
    "cirislenscore": "observability", "cirisnode": "node", "cirisnodecore": "node",
    "humanity": "accord", "ratchet": "anti-sybil", "spock": "multi-master-replication",
}
def slug(s):
    s = s.lower()
    s = re.sub(r"`[^`]*`", " ", s)               # drop code spans
    s = re.sub(r"[^a-z0-9]+", " ", s)
    toks = [GENERIC.get(t, t) for t in s.split() if t and t not in STOP]
    return toks

DROP = {"chapter", "section", "introduction", "conclusion", "the", "ceg", "0", "1", "2"}
def clean_word(key):
    """The clean genericized primary word for a concept."""
    if key.startswith("A§") and key in ACC_CONCEPT:
        return ACC_CONCEPT[key][1]
    n = CEG.get(key)
    if n:
        cur = (n.get("current_name") or "").strip().lower()
        if cur and cur not in ("", "(unnamed)"):
            return GENERIC.get(cur, cur)
        t = slug(n.get("title", ""))
        return t[-1] if t else key
    t = [x for x in slug(title_of(key)) if x not in DROP]
    return "-".join(t[:2]) if t else key.replace("A§", "a-")

def distinguisher(key, base):
    """A meaningful token to disambiguate a colliding base name."""
    for t in slug(title_of(key)):
        if t != base and t not in DROP and len(t) > 2:
            return t
    return re.sub(r"[^a-z0-9]+", "-", legacy_of(key).lower()).strip("-")

# ---- build records ---------------------------------------------------------
keys = list(PR.keys())
ranked = sorted(keys, key=lambda k: -PR[k])
rank = {k: i + 1 for i, k in enumerate(ranked)}     # global import rank (1 = heaviest)

# importance tier -> structural depth band
def tier(k):
    r = rank[k]
    if r <= 20:  return 1   # chapter
    if r <= 60:  return 2   # section
    if r <= 150: return 3   # subsection
    return 4                # deep

rec = {}
for k in keys:
    rec[k] = dict(key=k, p=PR[k], rank=rank[k], part=part_of(k),
                  title=title_of(k), origin=origin_of(k), legacy=legacy_of(k),
                  pages=round(PR[k] * TOTAL_PAGES, 2))

# unique semantic ids — heaviest concept keeps the clean word; collisions get a
# MEANINGFUL suffix from the concept's own title (not a numeric counter).
sem, taken = {}, set()
for k in ranked:
    b = clean_word(k) or k
    if b not in taken:
        sem[k] = b
    else:
        cand = f"{b}-{distinguisher(k, b)}"
        i = 1
        while cand in taken:
            i += 1
            cand = f"{b}-{distinguisher(k, b)}-{i}"
        sem[k] = cand
    taken.add(sem[k])
for k in rec: rec[k]["semantic_id"] = sem[k]
disamb_meaningful = sum(1 for k in sem if "-" in sem[k] and not re.search(r"-\d+$", sem[k]))

# ---- decimal numbering ------------------------------------------------------
# Parentage follows SOURCE hierarchy (readable outline); IMPORTANCE promotes the
# heaviest concepts to top-level Chapters and orders all siblings. Depth is bounded
# by the source nesting, not by an importance cascade.
def ceg_prefixes(sec):
    pp = sec.split(".")
    return [".".join(pp[:i]) for i in range(len(pp) - 1, 0, -1)]   # longest-first
def acc_book(aid):
    m = re.match(r"A§(\d+)\.", aid)
    return m.group(1) if m else None

decimal = {}
for p in PARTS:
    members = [k for k in keys if rec[k]["part"] == p]
    mset = set(members)
    pnum = PART_NUM[p]
    # representative "Book intro" chapter per Accord book in this part
    book_nodes = defaultdict(list)
    for k in members:
        if k.startswith("A§") and acc_book(k):
            book_nodes[acc_book(k)].append(k)
    book_rep = {}
    for b, ns in book_nodes.items():
        intro = [n for n in ns if "introduction" in n or n.endswith(".chapters")]
        book_rep[b] = (sorted(intro, key=lambda n: -PR[n]) or sorted(ns, key=lambda n: -PR[n]))[0]
    parent = {}
    for k in members:
        if k.startswith("A§"):
            if k in ACC_CONCEPT:
                parent[k] = None                       # curated concept -> chapter
            else:
                b = acc_book(k)
                parent[k] = book_rep[b] if (b and book_rep.get(b) != k) else None
        else:
            par = None
            for pre in ceg_prefixes(k):
                if pre in mset:
                    par = pre; break
            parent[k] = par
    for k in members:                                  # importance promotion: top-20 -> chapter
        if rank[k] <= 20 or parent[k] == k:
            parent[k] = None
    children = defaultdict(list)
    roots = []
    for k in members:
        (roots if parent[k] is None else children[parent[k]]).append(k)
    def assign(node, prefix):
        for i, kid in enumerate(sorted(children.get(node, []), key=lambda x: -PR[x]), 1):
            decimal[kid] = f"{prefix}.{i}"
            assign(kid, decimal[kid])
    for i, r in enumerate(sorted(roots, key=lambda x: -PR[x]), 1):
        decimal[r] = f"{pnum}.{i}"
        assign(r, decimal[r])
for k in rec: rec[k]["decimal_id"] = decimal[k]

# ---- emit ------------------------------------------------------------------
def dkey(d):  # sort decimal_ids numerically by path
    return [int(x) for x in d.split(".")]
rows = sorted(rec.values(), key=lambda r: dkey(r["decimal_id"]))

cols = ["decimal_id", "semantic_id", "title", "legacy_ref", "p_i", "import_rank", "pages", "part", "origin"]
with open(os.path.join(OUT, "toc.tsv"), "w") as f:
    f.write("\t".join(cols) + "\n")
    for r in rows:
        f.write("\t".join(str(x) for x in [
            r["decimal_id"], r["semantic_id"], r["title"].replace("\t", " "),
            r["legacy"], f'{r["p"]:.5f}', r["rank"], r["pages"],
            r["part"], r["origin"]]) + "\n")

codebook = {
    "_note": ("Deterministic dual-ID codebook for the CIRIS Constitution (CC). Both maps are "
              "1:1. decimal_id and semantic_id are deterministic functions of the unified corpus "
              "(graph_unified.json unified_pagerank conscious-mesh weights + the fixed Part map); "
              "same corpus => byte-identical codebook. title->id is NOT codebook-free: it depends "
              "on the measured importance distribution, by design."),
    "n_concepts": len(rec),
    "decimal_to_key": {rec[k]["decimal_id"]: k for k in rec},
    "key_to_decimal": {k: rec[k]["decimal_id"] for k in rec},
    "semantic_to_key": {rec[k]["semantic_id"]: k for k in rec},
    "key_to_semantic": {k: rec[k]["semantic_id"] for k in rec},
    "legacy_to_decimal": {rec[k]["legacy"]: rec[k]["decimal_id"] for k in rec},
}
json.dump(codebook, open(os.path.join(OUT, "codebook.json"), "w"), indent=0)

# ---- verify ----------------------------------------------------------------
ndec = len(set(decimal.values())); nsem = len(set(sem.values()))
disamb = sum(1 for k in sem if re.search(r"-\d+$", sem[k]))
by_part = defaultdict(lambda: [0, 0.0])
for r in rec.values():
    by_part[r["part"]][0] += 1; by_part[r["part"]][1] += r["pages"]
print(f"concepts            : {len(rec)}  (CEG {sum(1 for r in rec.values() if r['origin']=='ceg')} + Accord {sum(1 for r in rec.values() if r['origin']=='accord')})")
print(f"decimal_id unique   : {ndec}/{len(rec)}  {'OK' if ndec==len(rec) else 'COLLISION'}")
print(f"semantic_id unique  : {nsem}/{len(rec)}  {'OK' if nsem==len(rec) else 'COLLISION'}  (disambiguated: {disamb})")
print(f"total page budget   : {sum(r['pages'] for r in rec.values()):.1f}")
print("part                 n   pages   title")
for p in PARTS:
    print(f"  {p:>4} {PART_NUM[p]}  {by_part[p][0]:>4} {by_part[p][1]:>6.1f}   {PART_TITLE[p]}")
print("--- top 12 by importance (the lead chapters) ---")
for k in ranked[:12]:
    r = rec[k]
    print(f"  {r['decimal_id']:>9}  {r['semantic_id']:<22} {r['pages']:>4}pp  [{r['legacy']}]  {r['title'][:46]}")
