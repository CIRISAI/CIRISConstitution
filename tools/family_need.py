#!/usr/bin/env python3
"""
CC — what each row family is needed for, measured from the tables and the reported decision sites.

A row is kept because something concludes from it. This tool asks of each family: which other cell reads it,
which decision site reads it, and what it does of its own. A family nothing reads and that does nothing of its
own is listed, since nothing here shows why it is kept.

  read by a rule    another family's guard, fold, count, signer, subject or cosign cell, or a reaction, names it
  read by a site    a decision site of the five repositories reads it (formal/derivation/kernel_sites.tsv)
  acts              it has a typed fold, a count, a guard or a change of its own, or a reaction or clock opens on it
  names             its own reference cell or a guard reference slot names another row

It also groups families by the rule cells they share. Families whose every rule cell is equal behave as one, and
differ only in name and body.

Run: python3 tools/family_need.py            (--write refreshes formal/derivation/family_need.tsv; --check for the gate)
"""
import collections, csv, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "formal", "derivation", "family_need.tsv")
RULE_COLS = ("verbs", "maintains_record", "reference", "placement", "signer_rule", "subject_rule", "cosign_rule",
             "freshness", "lifecycle", "replication", "erasure_route", "governance", "polarity", "fold", "count", "reserved")
READ_COLS = ("signer_rule", "subject_rule", "cosign_rule", "fold", "count", "governance", "lifecycle", "reference")
TOKEN = re.compile(r"[a-z_]+(?::[a-z_0-9{}*|]+)+")


def val(c):
    return c.get("value") if isinstance(c, dict) and "value" in c else c


def prefix(f):
    """the literal part of a family name before its first variable segment"""
    out = []
    for seg in f.split(":"):
        if "{" in seg or "*" in seg: break
        out.append(seg)
    return ":".join(out)


def main():
    fm = json.load(open(os.path.join(ROOT, "manifests", "family_model.json"), encoding="utf-8"))["rows"]
    tr = {r["family"]: r for r in json.load(open(os.path.join(ROOT, "manifests", "transitions.json"), encoding="utf-8"))["rows"]}
    rx = json.load(open(os.path.join(ROOT, "manifests", "reactions.json"), encoding="utf-8"))["reactions"]
    fams = [r["family"] for r in fm]
    pre = {f: prefix(f) for f in fams}

    def owner(tok):
        """the family a token names: the one with the longest literal prefix the token begins with"""
        best = None
        for f, p in pre.items():
            if p and (tok == p or tok.startswith(p + ":") or tok == f) and (best is None or len(p) > len(pre[best])): best = f
        return best

    def mentions(text):
        return {owner(t) for t in TOKEN.findall(text)} - {None}

    read_by = collections.defaultdict(set); names = collections.defaultdict(set); acts = collections.defaultdict(list)
    for r in fm:
        f = r["family"]
        for col in READ_COLS:
            for g in mentions(json.dumps(val(r.get(col)))):
                if g != f: read_by[g].add(f"{f}.{col}")
                if col == "reference" and g != f: names[f].add(g)
        if val(r["fold"]): acts[f].append("fold")
        if val(r["count"]) not in (None, "none"): acts[f].append("count")
        if val(r["reference"]): names[f].add("reference")
    for f, row in tr.items():
        for t in row["transitions"]:
            for cell in ("guard", "change"):
                items = val(t.get(cell)) or []
                if items and cell not in acts[f]: acts[f].append(cell)
                for g in mentions(json.dumps(items)):
                    if g != f: read_by[g].add(f"{f}.{cell}"); names[f].add(g)
    for e in rx:
        f = e["family"]
        if f in pre and e["kind"] not in acts[f]: acts[f].append(e["kind"])
        for g in mentions(json.dumps(e)):
            if g != f: read_by[g].add(f"{f}.reaction")
    sites = collections.Counter()
    spath = os.path.join(ROOT, "formal", "derivation", "kernel_sites.tsv")
    for s in csv.DictReader([l for l in open(spath, encoding="utf-8") if not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE):
        for g in mentions(s["rows_read"].replace("|", " ")): sites[g] += 1

    sig = {r["family"]: json.dumps([val(r.get(c)) for c in RULE_COLS] + [[(t["verb"], t["from"], t["to"], val(t["roles"]), val(t.get("guard")), val(t.get("change"))) for t in tr.get(r["family"], {"transitions": []})["transitions"]]], sort_keys=True) for r in fm}
    classes = collections.defaultdict(list)
    for f, s in sig.items(): classes[s].append(f)
    cid = {}
    for i, (s, fs) in enumerate(sorted(classes.items(), key=lambda kv: (-len(kv[1]), kv[1][0])), 1):
        for f in fs: cid[f] = (i, len(fs))

    rows = []
    for f in fams:
        need = "read by a rule" if read_by[f] else "read by a site only" if sites[f] else "acts of its own" if acts[f] else "nothing shown"
        rows.append((f, need, len(read_by[f]), sites[f], " ".join(acts[f]) or "-", " ".join(sorted(names[f])) or "-", f"B{cid[f][0]:03}", cid[f][1], " ".join(sorted(read_by[f])[:6]) or "-"))
    text = "family\tneed\tread_by_rules\tread_by_sites\tacts\tnames\tbehaviour\tfamilies_sharing_it\treaders\n" + "".join("\t".join(map(str, r)) + "\n" for r in rows)
    if "--write" in sys.argv: open(OUT, "w", encoding="utf-8").write(text)
    c = collections.Counter(r[1] for r in rows)
    print(f"family need: {len(fams)} families")
    for k in ("read by a rule", "read by a site only", "acts of its own", "nothing shown"): print(f"   {c[k]:4}  {k}")
    nb = len(classes); shared = sum(len(v) for v in classes.values() if len(v) > 1)
    print(f"   {nb} distinct behaviours among {len(fams)} families; {shared} families share a behaviour with another")
    for s, fs in sorted(classes.items(), key=lambda kv: -len(kv[1]))[:6]:
        if len(fs) > 1: print(f"   {len(fs):4} behave as one: " + ", ".join(fs[:7]) + (" ..." if len(fs) > 7 else ""))
    if "-v" in sys.argv:
        for r in rows:
            if r[1] == "nothing shown": print("      " + r[0])
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != text: print("FAIL formal/derivation/family_need.tsv is stale: run tools/family_need.py --write"); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
