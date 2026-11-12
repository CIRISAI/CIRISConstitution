#!/usr/bin/env python3
"""
CC — the kernel's requirements, derived from what five repositories decide, set against what the tables supply.

Two sides, and the delta between them:

  demand   formal/derivation/kernel_sites.tsv: every decision site the store, the transport, the server, the client
           and the agent reported, each mapped to the ONE primitive its answer is (`computes`), the primitives it
           consults (`uses`), the rows it reads and anything it reads that is not a row.
  supply   formal/derivation/kernel_primitives.tsv: each primitive, the primitives it is composed from, the cells
           of the tables that state its rule, and the inputs it may take beyond rows; with how many of those
           cells are rules the text states (tools/kernel_closure.py).

What it reports:
  1. demand      sites and repositories per primitive: where one answer is computed in several places
  2. supply      how much of each primitive's rule the text states
  3. delta       demanded and not supplied; supplied and not demanded; answers outside the list
  4. composition how sites build answers from answers, against the declared composition: edges seen and not
                 declared, declared and not seen
  5. inputs      what sites read that is not a row, against the four inputs a kernel may take (first_held, now,
                 trust_set, own_keys): every other input is a thing to remove or to make explicit
  6. collapse    the answers most consulted by other answers and computed in the most places: compute once

Checks (exit 1): the declared composition has no cycle but the one marked recursion; every site names a listed
primitive or an `other:`; the file has every repository.

Run: python3 tools/kernel_requirements.py        (--check for the gate)
"""
import collections, csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "formal", "derivation")
REPOS = ("persist", "edge", "server", "client", "agent")
ALLOWED_INPUTS = {"first_held", "now", "trust_set", "own_keys", "signed_instant", "none", "unstated"}
KIND = {"cc-table": "ruled", "prose": "ruled", "derived": "ruled"}


def tsv(name):
    lines = [l for l in open(os.path.join(D, name), encoding="utf-8").read().split("\n") if l and not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE))


def ruled_share(cells):
    """ruled and total over the named cells, read as tools/kernel_closure.py reads them"""
    fm = json.load(open(os.path.join(ROOT, "manifests", "family_model.json"), encoding="utf-8"))
    tr = json.load(open(os.path.join(ROOT, "manifests", "transitions.json"), encoding="utf-8"))
    rx = json.load(open(os.path.join(ROOT, "manifests", "reactions.json"), encoding="utf-8"))["reactions"]
    timed = {e["family"] for e in rx}
    r = n = 0
    for c in cells:
        where, _, col = c.partition(".")
        if where == "fm":
            for row in fm["rows"]:
                n += 1; r += KIND.get(row[col].get("source") if isinstance(row.get(col), dict) else None) == "ruled"
        elif where == "tr":
            for row in tr["rows"]:
                for t in row["transitions"]:
                    n += 1; r += KIND.get(t[col].get("source")) == "ruled"
        elif where == "rx":
            n += len(fm["rows"]); r += sum(row["family"] in timed for row in fm["rows"])
    return r, n


def main():
    prim = collections.OrderedDict((p["id"], p) for p in tsv("kernel_primitives.tsv"))
    sites = tsv("kernel_sites.tsv")
    fails = []
    dep = {k: [d for d in p["depends_on"].split("|") if d != "-" and not d.endswith("^")] for k, p in prim.items()}
    depth = {}
    def walk(u, path=()):
        if u in path: fails.append("the declared composition has a cycle: " + " -> ".join(path + (u,))); return 0
        if u not in depth: depth[u] = 1 + max([walk(d, path + (u,)) for d in dep.get(u, [])] or [0])
        return depth[u]
    for k in prim: walk(k)
    w = lambda s: int(s["n_sites"]) if s["n_sites"].isdigit() else 1
    other = collections.Counter()
    for s in sites:
        if s["computes"].startswith("other:"): other[s["computes"]] += w(s)
        elif s["computes"] not in prim: fails.append(f"{s['site_id']} computes {s['computes']!r}, which is not a primitive")
    missing = [r for r in REPOS if not any(s["repo"] == r for s in sites)]
    if missing: fails.append("no sites from: " + ", ".join(missing))

    demand = collections.defaultdict(collections.Counter)
    order = collections.Counter(); inputs = collections.defaultdict(collections.Counter); seen_edges = collections.Counter()
    for s in sites:
        c = s["computes"]
        if c not in prim: continue
        demand[c][s["repo"]] += w(s)
        if s["order_dependent"] == "yes": order[c] += w(s)
        for i in s["non_row_inputs"].split("|"):
            if i and i != "-" and s["kernel_side"] == "kernel": inputs[c][i] += w(s)
        for u in s["uses"].split("|"):
            if u in prim and u != c: seen_edges[(c, u)] += w(s)

    total = sum(w(s) for s in sites)
    kern = [k for k in prim if k.startswith("K")]
    print(f"kernel requirements: {total} decision sites in {len(REPOS)} repositories, {len(sites)} rows\n")
    print("1. Demand and 2. supply, by primitive (sites per repository; the share of its rule the text states):\n")
    print(f"   {'':24} {'persist':>7} {'edge':>5} {'server':>6} {'client':>6} {'agent':>5} {'all':>5} {'repos':>5}   ruled")
    for k, p in prim.items():
        d = demand[k]; n = sum(d.values())
        cells = [c for c in p["supplied_by"].split("|") if c not in ("-", "policy", "verdict_state")]
        r, t = ruled_share(cells) if cells else (0, 0)
        sup = f"{100 * r // t:3}% of {t}" if t else ("outside" if p["kind"] == "outside" else "input" if p["kind"] == "base" else "no cell")
        print(f"   {k} {p['name']:20} {d['persist']:7} {d['edge']:5} {d['server']:6} {d['client']:6} {d['agent']:5} {n:5} {sum(1 for x in REPOS if d[x]):5}   {sup}")
    print("\n3. Delta.")
    thin = []
    for k in kern:
        p = prim[k]; cells = [c for c in p["supplied_by"].split("|") if c not in ("-", "policy", "verdict_state")]
        r, t = ruled_share(cells) if cells else (0, 0)
        if sum(demand[k].values()) and t and 100 * r // t < 34: thin.append(f"{p['name']} ({sum(demand[k].values())} sites, {100 * r // t}% ruled)")
    print("   demanded, with under a third of its rule stated: " + ("; ".join(thin) or "none"))
    print("   supplied and demanded by no site: " + (", ".join(prim[k]["name"] for k in kern if not sum(demand[k].values())) or "none"))
    print(f"   answers outside the list: {sum(other.values())} sites" + ("".join(f"\n      {n:3}  {o[6:]}" for o, n in other.most_common(12)) if other else ""))
    print("\n4. Composition: how sites build answers from answers.")
    declared = {(k, d) for k in prim for d in dep[k]}
    undeclared = [(e, n) for e, n in seen_edges.most_common() if e not in declared]
    unseen = sorted(e for e in declared if e not in seen_edges and e[0].startswith("K"))
    print(f"   edges seen at sites: {len(seen_edges)}; declared: {len(declared)}")
    print("   seen and not declared: " + ("; ".join(f"{prim[a]['name']} uses {prim[b]['name']} ({n})" for (a, b), n in undeclared[:14]) or "none"))
    print("   declared and not seen: " + ("; ".join(f"{prim[a]['name']} from {prim[b]['name']}" for a, b in unseen[:14]) or "none"))
    print("\n5. Inputs that are not rows, read by sites their census puts on the kernel's side:")
    bad = collections.Counter(); per = collections.defaultdict(collections.Counter)
    for k in kern:
        for i, n in inputs[k].items():
            if i not in ALLOWED_INPUTS: bad[i] += n; per[i][prim[k]["name"]] += n
    for i, n in bad.most_common():
        print(f"   {i:15} {n:4} sites   " + ", ".join(f"{a} {b}" for a, b in per[i].most_common(4)))
    print(f"   order-dependent sites: {sum(order.values())}: " + ", ".join(f"{prim[k]['name']} {n}" for k, n in order.most_common(8)))
    print("\n6. Collapse: compute once what many answers consult and many places compute.")
    fan = collections.Counter()
    for (a, b), n in seen_edges.items(): fan[b] += n
    for a, b in declared: fan[b] += 0
    rank = sorted(kern, key=lambda k: -(fan[k] + sum(demand[k].values())))
    for k in rank[:10]:
        print(f"   {prim[k]['name']:18} consulted at {fan[k]:4} sites, computed at {sum(demand[k].values()):4} sites in {sum(1 for x in REPOS if demand[k][x])} repositories, depth {depth[k]}")
    for f in fails: print("FAIL " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
