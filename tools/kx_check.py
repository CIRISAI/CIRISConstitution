#!/usr/bin/env python3
"""
CC — the one checker of the rule cells: every cell of the five grammars translated into KX (tools/kx.py) and held
to its original.

  guards     formal/derivation/guard_text.tsv      tools/guard_grammar.py        reading: tools/kx_reference.py Ref
  folds      formal/derivation/fold_text.tsv (+ fold_reader_defaults.tsv)          RefFold
  changes    formal/derivation/change_text.tsv (+ the build's default change)      ch_ref
  reactions  formal/derivation/reaction_text.tsv  tools/build_reactions.py          re_ref
  counts     formal/derivation/count_text.tsv     the first arm whose selector holds          count_ref
  policy     manifests/governance_policy.json     tools/build_governance_policy.py decide() and its vectors

For each cell: the grammar's own parser gives the tree, tools/kx_translate.py gives the KX, tools/kx.py computes its
layer and its type errors (formal/derivation/kx_field_types.tsv), and both sides are evaluated on generated row
sets in every arrival order (the reference over the tree, KX over formal/kernel_lib). Each translation is also
mutated (one operator changed, three times, seeded) and a mutant that no generated set tells apart is counted.

A cell that uses a word the translation does not carry (DROPPED in tools/kx_translate.py: a word whose meaning the
grammar does not state, or one not implemented) is `reads_dropped`, listed with the word, and is not counted as
translated. Every other closed word must change the translation: each is swapped for every other word of its class,
and a variant that reads the same is an undeclared drop (CARRIED_WORD_COLLISIONS, held at 0).

Three plants run every time: one cell is translated wrong on purpose (the agreement run must catch it); a translator
that reads every verdict word alike (the drop hunt must catch it); and a made-up fold cell that needs an operator
outside the language (it must be reported as not translatable).

What a pass does NOT show: for guards, folds, changes, reactions and counts the repository has a parser and no
evaluator, so agreement is with the reading in tools/kx_reference.py, the first executable meaning those cells
have, not with the text; the readings' choices are stated there. The policy is held to the tool's own decide().

The counts in tools/kx_maxima.tsv may only fall; a count above its maximum refuses the check.

Run: python3 -B tools/kx_check.py --check [--root DIR] [--kernel-lib FILE] [--workers N]
"""
import argparse, csv, json, os, random, re, resource, sys, time
from collections import Counter, defaultdict
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kx, kx_translate as T, kx_reference as R

ROOT = None
PRELUDE = None
TOOLS = {}
PLANT_GUARD = "ref:*=ref:*"
PLANT_FOLD = {"family": "PLANT:vote:{contribution_id}", "fold": "combine=sum(sqrt(score)); by=reader", "cc_ref": "made up"}
CONSTS = {"m": 1, "threshold": 1, "floor": 1, "prev": 1, "rate:0": 1, "rate:1": 2, "rate:2": 3}
GUARD_SETS, FOLD_SETS, CHANGE_SETS, REACTION_SETS = 12, 12, 16, 12


def load_mod(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def tsv(path):
    with open(path, encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#") and l.strip()]
    hdr = lines[0].rstrip("\n").split("\t")
    return [dict(zip(hdr, l.rstrip("\n").split("\t"))) for l in lines[1:]]


def setup(root, kernel=None, limit=True):
    global ROOT, PRELUDE
    if limit:
        try: resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
        except (ValueError, OSError): pass
    ROOT = root
    kx.use_root(root, kernel)
    PRELUDE = kx.parse_program(open(kx.find(root, "tools/kx_prelude.kx"), encoding="utf-8").read())
    for n in ("guard_grammar", "fold_grammar", "change_grammar", "build_reactions"):
        TOOLS[n] = load_mod(n, os.path.join(root, "tools", n + ".py"))


def cells(root):
    d = os.path.join(root, "formal", "derivation")
    g = tsv(os.path.join(d, "guard_text.tsv"))
    f = tsv(os.path.join(d, "fold_text.tsv"))
    f += [{"family": "*reader:" + r["polarity"], "fold": r["fold"], "cc_ref": r["cc_ref"]} for r in tsv(os.path.join(d, "fold_reader_defaults.tsv"))]
    c = tsv(os.path.join(d, "change_text.tsv"))
    m = re.search(r'^CHANGE_DEFAULT = "([^"]+)"', open(os.path.join(root, "tools", "build_transitions.py"), encoding="utf-8").read(), re.M)
    if m: c.append({"family": "*default", "change": m.group(1), "cc_ref": "tools/build_transitions.py"})
    r = tsv(os.path.join(d, "reaction_text.tsv"))
    return {"guard": g, "fold": f, "change": c, "reaction": r}


# ------------------------------------------------------------------ mutation
SWAPS = [("some(", "none("), ("none(", "some("), ("eq(", "ne("), ("ne(", "eq("), ("ge(", "lt("), ("le(", "gt("),
         ("'admitted'", "'withdrawn'"), ("and(", "or("), ("member(", "NOT_MEMBER"), ("check(", "CHECK_NOT")]


def _close(s, i, stop_at_comma):
    d = 0
    while True:
        c = s[i]
        if c == "(": d += 1
        elif c == ")":
            if d == 0: return s[:i] + ")" + s[i:]
            d -= 1
        elif c == "," and d == 0 and stop_at_comma: return s[:i] + ")" + s[i:]
        i += 1


def mutate(src, rnd):
    opts = [(a, b) for a, b in SWAPS if a in src]
    if not opts: return None, None
    a, b = rnd.choice(opts)
    i = rnd.choice([k for k in range(len(src)) if src.startswith(a, k)])
    if b == "NOT_MEMBER": out = src[:i] + "not(member(" + src[i + len(a):]; out = _close(out, i + len("not(member("), False)
    elif b == "CHECK_NOT": out = src[:i] + "check(not(" + src[i + len(a):]; out = _close(out, i + len("check(not("), True)
    else: out = src[:i] + b + src[i + len(a):]
    return out, f"{a}->{b}"


def norm(x):
    return tuple(kx._hashable(y) for y in x) if isinstance(x, tuple) else kx._hashable(x)


# ------------------------------------------------------------------ one cell of each grammar
def policy_windows():
    return {f["family"]: 3 for f in json.load(open(os.path.join(ROOT, "manifests", "governance_policy.json")))["families"]}


def plant_src(src, swap, retranslate):
    """A seeded mistranslation of one cell: ("kx", a, b) swaps text of the translation, ("text", a, b) translates the
    cell with its words changed, while the reference still reads the cell as written."""
    if not swap: return src
    kind, a, b = swap
    if kind in ("kx", "kx*"):       # kx*: every occurrence
        assert a in src, f"plant: {a!r} is not in the translation"
        return src.replace(a, b) if kind == "kx*" else src.replace(a, b, 1)
    return retranslate(a, b)


def run_guard(c, idx, planted=False, swap=None):
    gg = TOOLS["guard_grammar"]
    res = {"grammar": "guard", "cell": idx, "family": c["family"], "text": c["guard"]}
    try: clauses, _ = gg.parse(c["guard"])
    except Exception as e: return dict(res, status="not_parsed", err=str(e))
    src = T.translate(clauses)
    if planted: src = src.replace("meets(", "member(", 1)
    src = plant_src(src, swap, lambda a, b: T.translate(gg.parse(c["guard"].replace(a, b))[0]))
    try: expr = kx.parse(src)
    except Exception as e: return dict(res, status="not_translated", err=str(e))
    info = kx.analyse(expr, PRELUDE)
    res.update(kx=src, layer=kx.layer_name(info), flags=sorted(info.flags), clauses=[])
    res["clauses"] = clause_layers(clauses)
    if c.get("layers_only"): return res
    pol = policy_windows(); rnd = random.Random(1000 + idx)
    muts = [m for m in (mutate(src, rnd) for _ in range(3)) if m[0]]
    muts = [[kx.parse(m), h, 0] for m, h in muts]
    agree = dis = 0; ex = []
    for rows, sid in R.guard_sets(c["family"], clauses, 7 + idx, n=GUARD_SETS, maxrows=5):
        now = rnd.choice([2, 5, 9])
        for held in R.orders(rows):
            s = next(r for r in held if r["id"] == sid)
            for H in (held, [r for r in held if r["t"] < s["t"] or r["id"] == sid]):
                o = frozenset(R.Ref(H, s, now, pol).clauses(clauses, {}))
                ev = kx.Ev(PRELUDE, H, s, now, {"policy": pol})
                t = ev.run(expr)
                if o == t: agree += 1
                else:
                    dis += 1
                    if len(ex) < 2: ex.append({"orig": sorted(map(str, o)), "kx": sorted(map(str, t))})
                for m in muts:
                    try: mt = kx.Ev(PRELUDE, H, s, now, {"policy": pol}).run(m[0])
                    except Exception: mt = "error"
                    m[2] += mt != o
    out = finish(res, agree, dis, ex, muts, lambda v: T.translate(gg.parse(v)[0]))
    return out


def clause_layers(clauses):
    """Each clause that states an outcome, a clause inside a group among them, with the layer its own expression
    reads: computed with the rows its siblings bind and under the conditions of the group that holds it."""
    out = []
    def walk(cs, outer, at):
        for n, cl in enumerate(cs):
            i1 = kx.analyse(kx.parse(T.t_clause_among(cl, cs, outer)), PRELUDE)
            atom = cl.get("atom") or {}
            out.append({"at": at + str(n), "layer": kx.layer_name(i1), "flags": sorted(i1.flags), "outcome": (cl["else"] or {}).get("do"),
                        "window": atom.get("atom") == "window" or bool(atom.get("window"))})
            if "group" in cl: walk(cl["group"], cl, at + str(n) + ".")
    walk(clauses, None, "")
    return out


def run_fold(c, idx, swap=None):
    fg = TOOLS["fold_grammar"]
    res = {"grammar": "fold", "cell": idx, "family": c["family"], "text": c["fold"]}
    try: parsed, _, _ = fg.parse(c["fold"])
    except Exception as e: return dict(res, status="not_parsed", err=str(e))
    dparts = fg.parse(fg.DEFAULT)[0]["parts"]; stated = parsed["parts"]
    if not [k for k in stated if k not in T.LABELS]: return dict(res, status="labels_only")
    parts = dict(stated)
    for k in ("reads", "key", "pick", "cut"):
        if k not in parts and k in dparts: parts[k] = dparts[k]
    fam = "x:{y}" if c["family"].startswith("*") or c["family"].startswith("PLANT") else c["family"]
    when = parsed["when"]
    tx = T.Tx(parts, fam, when)
    def retx(a, b):
        p2 = fg.parse(c["fold"].replace(a, b))[0]; parts2 = dict(p2["parts"])
        for k in ("reads", "key", "pick", "cut"):
            if k not in parts2 and k in dparts: parts2[k] = dparts[k]
        return T.Tx(parts2, fam, p2["when"]).build()
    try:
        src = plant_src(tx.build(), swap, retx); expr = kx.parse(src)
    except T.NeedsOperator as e: return dict(res, status="needs_operator", err=f"function {e}")
    except Exception as e: return dict(res, status="not_translated", err=repr(e)[:200])
    info = kx.analyse(expr, PRELUDE)
    res.update(kx=src, layer=kx.layer_name(info), flags=sorted(info.flags), gaps=sorted(set(tx.gaps)),
               at_decision=bool(re.search(r"@(decision|count)\b", c["fold"])))
    tables = dict(tx.tables); tables["const"] = CONSTS; tables.update(T.UNITS)
    rnd = random.Random(500 + idx)
    muts = [m for m in (mutate(src, rnd) for _ in range(3)) if m[0]]
    muts = [[kx.parse(m), h, 0] for m, h in muts]
    agree = dis = 0; ex = []
    for rows in R.fold_sets(fam, parts, 11 + idx, n=FOLD_SETS, maxrows=5, when=when):
        now = rnd.choice([1, 4])
        for held in R.orders(rows[:-1], cap=24):
            held = held + [dict(rows[-1], t=99)]; p = held[-1]
            try: o = norm(R.RefFold(parts, fam, held, p, now, CONSTS, when).run())
            except Exception as e: o = ("reference_error", repr(e)[:80])
            try: t = norm(kx.Ev(PRELUDE, held, p, now, tables).run(expr))
            except Exception as e: t = ("kx_error", repr(e)[:80])
            if o == t: agree += 1
            else:
                dis += 1
                if len(ex) < 2: ex.append({"orig": repr(o)[:300], "kx": repr(t)[:300]})
            for m in muts:
                try: mt = norm(kx.Ev(PRELUDE, held, p, now, tables).run(m[0]))
                except Exception: mt = "error"
                m[2] += mt != o
    def tr(v):
        p2 = fg.parse(v)[0]; parts2 = dict(p2["parts"])
        for k in ("reads", "key", "pick", "cut"):
            if k not in parts2 and k in dparts: parts2[k] = dparts[k]
        return T.Tx(parts2, fam, p2["when"]).build()
    return finish(res, agree, dis, ex, muts, tr)


def run_change(c, idx, swap=None):
    cg = TOOLS["change_grammar"]
    res = {"grammar": "change", "cell": idx, "family": c["family"], "text": c["change"]}
    try: items, _ = cg.parse(c["change"])
    except Exception as e: return dict(res, status="not_parsed", err=str(e))
    src = plant_src(T.ch_kx(items), swap, lambda a, b: T.ch_kx(cg.parse(c["change"].replace(a, b))[0]))
    try: expr = kx.parse(src)
    except Exception as e: return dict(res, status="not_translated", err=str(e))
    info = kx.analyse(expr, PRELUDE)
    items_nc = [dict(it, clauses=[x for x in it["clauses"] if x["clause"] != "cascade"]) for it in items]
    i2 = kx.analyse(kx.parse(T.ch_kx(items_nc)), PRELUDE)
    res.update(kx=src, layer=kx.layer_name(info), flags=sorted(info.flags), layer_checks=kx.layer_name(i2),
               outcomes=sorted({x.get("do", "refuse") for it in items for x in it["clauses"] if x["clause"] == "refuse"}))
    if c.get("layers_only"): return res
    rnd = random.Random(idx)
    muts = [m for m in (mutate(src, rnd) for _ in range(3)) if m[0]]
    muts = [[kx.parse(m), h, 0] for m, h in muts]
    agree = dis = 0; ex = []
    for rows, sid in R.ch_gen(items, rnd, CHANGE_SETS):
        for held in R.orders(rows, cap=24):
            s = next(x for x in held if x["id"] == sid)
            o = R.ch_ref(items, held, s); t = kx.Ev(PRELUDE, held, s).run(expr)
            if o == t: agree += 1
            else:
                dis += 1
                if len(ex) < 2: ex.append({"orig": repr(o)[:300], "kx": repr(t)[:300]})
            for m in muts:
                try: mt = kx.Ev(PRELUDE, held, s).run(m[0])
                except Exception: mt = "error"
                m[2] += mt != o
    return finish(res, agree, dis, ex, muts, lambda v: T.ch_kx(cg.parse(v)[0]))


def reaction_sets(c, clauses, rnd, n, called=()):
    fams = [e["of"] for x in clauses for e in x.get("on", []) + x.get("unless", []) + (x["from"] if isinstance(x.get("from"), list) else [])
            if e["event"] not in ("close", "fold") and e["of"] not in ("self", "target")]
    lands = [x["landing"] for x in clauses if x["kind"] == "land" and x.get("landing")]
    members = {x.get("member") for x in clauses if x.get("member")} | {x["from"] for x in clauses if isinstance(x.get("from"), str) and x["from"] != "first_held"}
    members |= {d.split(".", 1)[1] for x in clauses for d in (x.get("dur"), x.get("default"), x.get("max"), x.get("eq")) if d and d.startswith("self.")}
    leaves = sorted({l for x in clauses for l in x.get("leaves", [])})
    for _ in range(n):
        rows = []
        for f in (fams + lands)[:3]:
            rows.append({"id": f"x{len(rows)}", "fam": R.fill(f, rnd), "verb": "attest", "signer": rnd.choice(R.KEYS), "attested": rnd.choice(R.KEYS), "object": rnd.choice(R.OBJS),
                         "asserted_at": rnd.randint(0, 3), "val": {"state": rnd.choice(["purged", "sealed", "matched", None])}, "leaf": {}, "ref": {}, "names": frozenset()})
        s = {"id": "self", "fam": R.fill(c["family"], rnd), "verb": "attest", "signer": rnd.choice(R.KEYS), "attested": rnd.choice(R.KEYS), "subject": rnd.choice(R.KEYS),
             "object": rnd.choice(R.OBJS), "asserted_at": rnd.randint(0, 3), "leafname": rnd.choice(leaves + ["zz"]) if leaves else "zz",
             "val": {m: rnd.choice([None, rnd.randint(0, 6)]) for m in members}, "leaf": {}, "ref": {}, "names": frozenset()}
        s["val"]["state"] = rnd.choice(["purged", "sealed", "matched", "refused", None])
        s["val"]["scope"] = rnd.choice(["self", "family", "affiliations", "community"])
        if rows and rnd.random() < .4:
            t0 = rnd.choice(rows)
            rows.append({"id": f"x{len(rows)}", "fam": t0["fam"], "verb": "withdraw", "signer": t0["signer"], "attested": None, "object": t0["object"],
                         "asserted_at": 3, "val": {}, "leaf": {}, "ref": {}, "names": frozenset([t0["id"]])})
        if rows and rnd.random() < .5: s["ref"]["target"] = rows[0]["id"]; s["names"] = frozenset([rows[0]["id"]])
        later = []
        if lands and rnd.random() < .6:
            later.append({"id": "L", "fam": R.fill(lands[0], rnd), "verb": "attest", "signer": s["signer"] if rnd.random() < .6 else rnd.choice(R.KEYS), "attested": None,
                          "object": s["object"], "asserted_at": 4, "val": {}, "leaf": {}, "ref": {}, "names": frozenset(["self"]) if rnd.random() < .8 else frozenset()})
            role = next(x["concluder"] for x in clauses if x["kind"] == "land" and x.get("landing"))
            if role not in T.LAND_ROW_ALONE and rnd.random() < .7:      # the landing's signer holds the concluder's seat over the object
                k = later[-1]["signer"]
                later.append({"id": "so", "fam": "seat:offer", "verb": "attest", "signer": s["object"], "attested": k, "object": s["object"], "asserted_at": 0,
                              "val": {"role": role}, "leaf": {}, "ref": {}, "names": frozenset()})
                later.append({"id": "sa", "fam": "seat:accept", "verb": "attest", "signer": k, "attested": None, "object": s["object"], "asserted_at": 1,
                              "val": {}, "leaf": {}, "ref": {}, "names": frozenset(["so"])})
        if rnd.random() < .3:
            later.append({"id": "W", "fam": s["fam"], "verb": rnd.choice(["withdraw", "recant", "replace"]), "signer": s["signer"], "attested": None, "object": s["object"],
                          "asserted_at": 4, "val": {}, "leaf": {}, "ref": {}, "names": frozenset(["self"])})
        for f in called:      # a fold the cell calls: seats in the role its count is over, conferred by the object and named by the row
            ov = re.match(r"([a-z_]+)", f["parts"].get("over", ""))
            if not ov: continue
            for k in rnd.sample(R.KEYS, rnd.randint(0, 3)):
                oid = f"f{len(later)}"
                later.append({"id": oid, "fam": "seat:offer", "verb": "attest", "signer": s["object"], "attested": k, "object": s["object"], "asserted_at": 0,
                              "val": {"role": ov.group(1)}, "leaf": {}, "ref": {}, "names": frozenset()})
                later.append({"id": oid + "a", "fam": "seat:accept", "verb": "attest", "signer": k, "attested": k, "object": s["object"], "asserted_at": 0,
                              "val": {}, "leaf": {}, "ref": {}, "names": frozenset([oid])})
                if rnd.random() < .85: s["names"] = s["names"] | {oid, oid + "a"}
        yield rows + [s] + later, rnd.randint(0, 8)


def run_reaction(c, idx, swap=None):
    br = TOOLS["build_reactions"]
    res = {"grammar": "reaction", "cell": idx, "family": c["family"], "text": c["reaction"]}
    try: clauses, _ = br.parse(c["reaction"])
    except Exception as e: return dict(res, status="not_parsed", err=str(e))
    fg = TOOLS["fold_grammar"]; folds = T.fold_names(cells(ROOT)["fold"], fg.parse, fg.parse(fg.DEFAULT)[0]["parts"])
    src, unresolved = T.re_kx(clauses, folds=folds, family=c["family"])
    src = plant_src(src, swap, lambda a, b: T.re_kx(br.parse(c["reaction"].replace(a, b))[0], folds=folds, family=c["family"])[0])
    try: expr = kx.parse(src)
    except Exception as e: return dict(res, status="not_translated", err=str(e))
    info = kx.analyse(expr, PRELUDE)
    res.update(kx=src, layer=kx.layer_name(info), flags=sorted(info.flags), unresolved=unresolved)
    rnd = random.Random(idx)
    muts = [m for m in (mutate(src, rnd) for _ in range(3)) if m[0]]
    muts = [[kx.parse(m), h, 0] for m, h in muts]
    agree = dis = 0; ex = []
    called = [folds[(c["family"], e["of"])] for x in clauses for e in x.get("on", []) + x.get("unless", []) if e["event"] == "fold" and (c["family"], e["of"]) in folds]
    tables = {"dur": {}, **T.UNITS}
    for allrows, now in reaction_sets(c, clauses, rnd, REACTION_SETS, called):
        for held in R.orders(allrows, cap=24):
            s = next(x for x in held if x["id"] == "self")
            o = frozenset(R.re_ref(clauses, held, s, now, folds, c["family"])); t = kx.Ev(PRELUDE, held, s, now, tables).run(expr)
            if o == t: agree += 1
            else:
                dis += 1
                if len(ex) < 2: ex.append({"orig": repr(sorted(map(repr, o)))[:300], "kx": repr(sorted(map(repr, t)))[:300]})
            for m in muts:
                try: mt = kx.Ev(PRELUDE, held, s, now, tables).run(m[0])
                except Exception: mt = "error"
                m[2] += mt != o
    return finish(res, agree, dis, ex, muts, lambda v: T.re_kx(br.parse(v)[0], folds=folds, family=c["family"])[0])


# ------------------------------------------------------------------ a misreading of each word given a meaning must be caught
WORD_PLANTS = [   # (word, grammar, a cell whose text holds this, the misreading)
    ("other(F): of a family other than F", "guard", "one other(testimonial_witness:{kind})@named", ("kx", "not(isfam(r, 'testimonial_witness:{kind}'))", "isfam(r, 'testimonial_witness:{kind}')")),
    ("set(ref:*): every named row", "guard", "set(ref:*) ballot:moderator@named[object=object] else void\t", ("text", "set(ref:*) ballot", "one ballot")),
    ("within(POLICY): from first holding", "guard", "within(accord_halt)", ("kx", "lt(arrival(self), add(arrival(r)", "lt(self.asserted_at, add(r.asserted_at")),
    ("after(POLICY): from first holding", "guard", {"family": "ballot:moderator_acceptance", "guard": "after(moderator_election) else exclude", "cc_ref": "made up"}, ("kx", "add(arrival(x), cell('policy', 'moderator_election'))", "add(x.asserted_at, cell('policy', 'moderator_election'))")),
    ("@named: the head the row names", "fold", "over=seated@named/person", ("text", "@named", "@now")),
    ("cut=whole", "fold", "cut=whole", ("kx", "member(r.id, ids(past(y)))", "eq(r.id, y.id)")),
    ("drop_only(MEMBER)", "fold", "drop_only(members)", ("kx", "none(diff(r.members, x.members))", "none(diff(x.members, r.members))")),
    ("test ?founder_quorum_restored:founder_quorum_unreachable", "fold", "founder_quorum_restored", ("text", "n>M", "n>=M")),
    ("/under: through others", "change", "cascade=membership:{stage}/under:lapsed", ("kx*", "member(T.id, ids(past(x)))", "member(T.id, x.names)")),
    ("/over: the same object", "change", "cascade=group:roster/over:withdrawn", ("kx", "eq(x.object, T.object)", "eq(x.signer, T.signer)")),
    ("entrenched: the record's flag", "change", "replace[entrenched]: field=consensus_protocol:frozen\t", ("kx", "eq(T.consensus_protocol_entrenched, 1)", "eq(self.entrenched, 1)")),
    (":shrink", "change", "replace: field=members:shrink", ("kx", "none(diff(self.members, T.members))", "none(diff(T.members, self.members))")),
    (":grow_signed", "change", "replace[grade:trust_root]: field=members:grow_signed", ("kx", "member(k, cosigners(self))", "true")),
    ("link=chained:", "change", "link=chained:prev_head_digest", ("text", "link=chained:", "link=ranked:")),
    ("by receipt: from first holding", "reaction", "accord:invoke:constitutional:{halt_id}\texpiry none; clock fuse = charter.halt_fuse_secs from first_held by receipt", ("kx", "add(arrival(self)", "add(self.asserted_at")),
    ("by signed: the row's own end", "reaction", "[proposal] expiry required expires_at max membership_proposal_max_secs from asserted_at by signed", ("kx", "let O = self.asserted_at", "let O = arrival(self)")),
    ("by signed on a first-held clock reads no instant", "reaction", "accord:invoke:constitutional:{halt_id}\texpiry none; clock fuse = charter.halt_fuse_secs from first_held by receipt", ("text", "by receipt", "by signed")),
    ("while NAME in_force: binds from each node's own first holding", "reaction", "while fuse in_force", ("kx", "'in_force'", "'pending'")),
    ("fold(NAME): the fold's verdict", "reaction", "on fold(founder_quorum_unreachable)", ("kx", "'founder_quorum_unreachable')), not(", "'founder_quorum_restored')), not(")),
]
POLICY_PLANTS = [  # (word, row, the misreading)
    ("voice person: one voice a person", "moderation_overturn", ("cell('person', k, k)", "k")),
    ("voice key: each key a voice", "self_roster_add", ("size(CS)", "size(setof(CS, \\k: cell('person', k, k)))")),
    ("voices objection", "moderation_overturn", ("'objection:*'", "'ballot:*'")),
    ("voices ballot", "moderator_election", ("'ballot:*'", "'objection:*'")),
    ("target_voice yes: the target's own yes is a voice", "community_invite", ("union(CS, single(self.target))", "CS")),
    ("voices scrubs", "moderator_recall", ("cosigners(self)", "setof(held, \\v: v.signer)")),
    ("target_silent yes", "self_roster_evict", ("ge(arrival(x), arrival(self))", "true")),
]


def word_plants():
    cs = cells(ROOT); out = []
    run = {"guard": run_guard, "fold": run_fold, "change": run_change, "reaction": run_reaction}
    for word, g, where, swap in WORD_PLANTS:
        rows = [(0, where)] if isinstance(where, dict) else [(i, c) for i, c in enumerate(cs[g]) if where in "\t".join(c.values())]   # a made-up cell where the word's verdict is not masked
        if not rows: out.append((word, None)); continue
        i, c = rows[0]
        r = run[g](c, i, swap=swap)
        out.append((word, r.get("disagree")))
    return out


def policy_plants():
    pt = tsv(os.path.join(ROOT, "formal", "derivation", "policy_text.tsv")); cellsof = defaultdict(dict)
    for c in pt: cellsof[c["row"]][c["column"]] = c["value"]
    out = []
    for word, row, (a, b) in POLICY_PLANTS:
        cl = cellsof[row]; src = T.policy_count_kx(row, cl)
        if src is None or a not in src: out.append((word, None)); continue
        e = kx.parse(src.replace(a, b, 1)); rnd = random.Random(sum(map(ord, row))); pol = {row: 3}; dis = 0
        for rows in R.policy_sets(cl, rnd):
            for held in R.orders(rows, cap=24):
                s = next(x for x in held if x["id"] == "self")
                dis += R.policy_ref(row, cl, held, s, pol) != kx.Ev(PRELUDE, held, s, 0, {"policy": pol, "person": T.UNITS["person"]}).run(e)
        out.append((word, dis))
    return out


# ------------------------------------------------------------------ dropped words and undeclared drops
VOCAB = {
    "fold": [r"@(named|signed|now|close|prior|act|seating|founding|decision|count)\b", r"/(person|key|owner)\b",
             r"absent=(none|unspecified|restricted|protective|full|undefined|refuse)\b", r"cut=(named|whole|terminal|forward|none)\b",
             r"\b(lower_only|raise_only|narrow_only|drop_only|fixed)\(", r"&(live|direct)\b", r"pick=(union|set|agree|once|tips)\b"],
    "guard": [r"\b(one|all|no|latest) ", r"@(admitted|withdrawn|recanted|superseded|landed)\[", r" at (asserted_at|receipt|its_asserted_at)\b",
              r"via=(none|delegates_to)", r"else (refuse|void|contested|exclude|withhold|advise)\b"],
    "reaction": [r" by (signed|receipt|origin_door)\b", r"expiry (required|optional|forbidden|none)\b", r"-> (should |may )", r" late (closed|counts)\b",
                 r"while [A-Za-z_]+ (in_force|pending)\b"],
    "change": [r":(any|frozen|shrink|grow_signed|lower|no_weaker|as_attest)\b", r"reach=(own_prior|other_attester|below_seq|whole)",
               r"by=(same_attester|none|cosigned|cosigned_prior|committed_key|substrate)\b", r"/(by|under|about|ref|over):",
               r"\b(refuse|void|exclude)=[a-z_0-9]+"],
}
WORDS = {}
for g, rxs in VOCAB.items():
    WORDS[g] = []
    for rx in rxs:
        alts = re.search(r"\(([a-z_ |]+)\)", rx).group(1).split("|")
        WORDS[g].append((rx, [a for a in alts]))


def collisions(grammar, text, base, tr, resolved=()):
    """Every carried word must change the translation: swap each closed word for each other word of its class; a
    variant that parses, drops nothing the cell does not, and translates to the same KX is an undeclared drop."""
    out = []
    mine = T.dropped_words(grammar, text, resolved)
    spans = T.dropped_spans(grammar, text, resolved)
    for rx, alts in WORDS[grammar]:
        for m in re.finditer(rx, text):
            if any(a <= m.start(1) < b for a, b in spans): continue     # a word inside a declared drop
            for w in alts:
                if w == m.group(1): continue
                v = text[:m.start(1)] + w + text[m.end(1):]
                if T.dropped_words(grammar, v, resolved) != mine: continue
                try: k = tr(v)
                except Exception: continue
                if k == base: out.append(f"{m.group(1).strip()} reads as {w.strip()}")
    return sorted(set(out))


def finish(res, agree, dis, ex, muts, tr):
    g, text = res["grammar"], res["text"]
    resolved = set(re.findall(r"\bfold\(([a-z_]+)\)", text)) - {u[5:-1] for u in res.get("unresolved", [])}
    dw = T.dropped_words(g, text, resolved)
    return dict(res, status="reads_dropped" if dw else "ok", dropped=[w for w, _ in dw], why=[y for _, y in dw],
                order_sites=kx.order_sites(kx.parse(res["kx"])),
                labels=T.label_words(g, text), collisions=collisions(g, text, res["kx"], tr, resolved),
                agree=agree, disagree=dis, examples=ex, mutants=len(muts), uncaught=sum(1 for m in muts if m[2] == 0))


def task(job):
    kind, idx, extra = job
    cs = cells(ROOT)
    if kind == "guard": return run_guard(cs["guard"][idx], idx, planted=extra == "plant")
    if kind == "fold": return run_fold(PLANT_FOLD if extra == "plant" else cs["fold"][idx], idx)
    if kind == "change": return run_change(cs["change"][idx], idx)
    return run_reaction(cs["reaction"][idx], idx)


# ------------------------------------------------------------------ counts and the policy (in the parent)
def run_counts():
    out = []
    fams = defaultdict(list)
    for c in tsv(os.path.join(ROOT, "formal", "derivation", "count_text.tsv")): fams[c["family"]].append(c)
    import itertools
    for fam, arms in fams.items():
        src = T.count_kx(arms); e = kx.parse(src); info = kx.analyse(e, PRELUDE)
        vals = defaultdict(set)
        for a in arms:
            if a["selector"] != "*":
                for t in a["selector"].split(" & "):
                    k, vs = t.split("="); vals[k] |= set(vs.split("|"))
        agree = dis = 0
        for lf, vb, at, gp, st in itertools.product(sorted(vals["leaf"]) + ["zz"], sorted(vals["verb"]) + ["attest"], R.KEYS, sorted(vals["group"]) + ["zz"], sorted(vals["seats"]) + ["zz"]):
            s = {"id": "self", "fam": "f", "leafname": lf, "verb": vb, "attested": at, "val": {"group": gp, "seats": st}, "names": frozenset()}
            o = R.count_ref(arms, s); t = kx.Ev(PRELUDE, [s], s).run(e)
            agree += o == t; dis += o != t
        out.append({"grammar": "count", "family": fam, "kx": src, "flags": sorted(info.flags), "agree": agree, "disagree": dis, "status": "ok"})
    return out


def run_policy():
    bgp = load_mod("bgp", os.path.join(ROOT, "tools", "build_governance_policy.py"))
    vec = json.load(open(os.path.join(ROOT, "manifests", "governance_policy_vectors.json")))
    rows = {f["family"]: f for f in json.load(open(os.path.join(ROOT, "manifests", "governance_policy.json")))["families"]}
    calls = {fam: T.policy_call(f) for fam, f in rows.items() if T.policy_call(f)}
    run = lambda src: kx.Ev(PRELUDE, [], None).run(kx.parse(src))
    va = vd = 0; ex = []
    for v in vec["vectors"]:
        if v["family"] not in calls: vd += 1; ex.append(("no call", v["family"])); continue
        cell = rows[v["family"]].get("counted", {}).get("target_voice", {}).get("value") == "yes"
        t = run(T.fill_call(calls[v["family"]], v["base"], v["approvals"], v["objections"], v["elapsed_secs"], v.get("target_voice", False), cell))
        va += t == v["verdict"]; vd += t != v["verdict"]
        if t != v["verdict"] and len(ex) < 3: ex.append((v, t))
    ra = rd = 0
    for v in vec["rule_vectors"]:
        r = v["rule"]
        t = run(f"rule_votes('{r['kind']}', {r.get('num', 0)}, {r.get('den', 1)}, {r.get('count', 0)}, {v['base']}, {'true' if v['cell'] == 'enact' else 'false'})")
        ra += t == v["votes"]; rd += t != v["votes"]
        if t != v["votes"] and len(ex) < 6: ex.append((v, t))
    ga = gd = 0
    for fam, call in calls.items():
        f = dict(rows[fam]); f["_enact"] = (f["enact"]["num"], f["enact"]["den"])
        f["_cancel"] = (f["cancel"]["num"], f["cancel"]["den"]) if isinstance(f.get("cancel"), dict) and "num" in f["cancel"] else None
        f["_floor"] = (f["floor"]["num"], f["floor"]["den"]) if isinstance(f.get("floor"), dict) and "num" in f["floor"] else None
        for base in (1, 2, 3, 5, 8):
            for a in range(base + 1):
                for o in range(base + 1):
                    for el in (0, f["window_secs"]):
                        for tv in (False, True):
                            cell = bgp.target_voice_cell(f)
                            d = bgp.decide(f, base, a, o, el, tv)[0]; t = run(T.fill_call(call, base, a, o, el, tv, cell))
                            ga += d == t; gd += d != t
    pt = tsv(os.path.join(ROOT, "formal", "derivation", "policy_text.tsv"))
    counted, dropped, sets = [], [], []
    cellsof = defaultdict(dict)
    for c in pt: cellsof[c["row"]][c["column"]] = c["value"]
    counts = {}      # each row's count (count_set, voice, voices, target_silent) against the reference reading, every order
    for row, cl in cellsof.items():
        src = T.policy_count_kx(row, cl)
        if src is None: continue
        e = kx.parse(src); info = kx.analyse(e, PRELUDE); rnd = random.Random(sum(map(ord, row)))
        muts = [[kx.parse(m), h, 0] for m, h in (mutate(src, rnd) for _ in range(3)) if m]
        ag = di = 0
        pol = {row: 3}; tables = {"policy": pol, "person": T.UNITS["person"]}
        for rows in R.policy_sets(cl, rnd):
            for held in R.orders(rows, cap=24):
                s = next(x for x in held if x["id"] == "self")
                o = R.policy_ref(row, cl, held, s, pol); t = kx.Ev(PRELUDE, held, s, 0, tables).run(e)
                ag += o == t; di += o != t
                for m in muts:
                    try: mt = kx.Ev(PRELUDE, held, s, 0, tables).run(m[0])
                    except Exception: mt = "error"
                    m[2] += mt != o
        counts[row] = {"kx": src, "flags": sorted(info.flags), "agree": ag, "disagree": di, "mutants": len(muts), "uncaught": sum(1 for m in muts if m[2] == 0)}
    for c in pt:
        if c["column"] == "count_set" and T.count_set_kx(c["value"]):      # the seats the cell names, as an expression with a layer
            i = kx.analyse(kx.parse(T.count_set_kx(c["value"])), PRELUDE)
            sets.append({"row": c["row"], "value": c["value"], "layer": kx.layer_name(i), "flags": sorted(i.flags)})
        elif c["column"] in ("voice", "voices", "target_silent", "target_voice") and c["row"] in counts and not counts[c["row"]]["disagree"]: pass   # in the row's count
        elif c["column"] != "counted_at": dropped.append(c)     # the count set is no seat, or whether the act changes its set: not translated
        if c["column"] == "counted_at":
            i = kx.analyse(kx.parse(T.counted_at_kx(c["value"])), PRELUDE)
            counted.append({"row": c["row"], "value": c["value"], "layer": kx.layer_name(i), "flags": sorted(i.flags)})
    return {"vectors": (va, vd), "rule_vectors": (ra, rd), "grid": (ga, gd), "rows_called": sorted(calls), "examples": ex[:6], "counted_at": counted, "count_set": sets,
            "dropped": dropped, "counts": counts}


# ------------------------------------------------------------------ the counts that may only fall
REFERENCE = {"ORDER_BY_SIGNED_INSTANT_OWN", "ORDER_BY_DIGEST_OWN"}   # printed for reference: a cell leaving CROSS for OWN is the intended movement. The total and CROSS are gated


def over_maximum(sizes, maxima):
    """The counts that hold no maximum or stand above it: [(count, size, maximum or None)]."""
    return [(k, n, maxima.get(k)) for k, n in sizes.items() if k not in REFERENCE and (maxima.get(k) is None or n > maxima[k])]


def outcome_measures(results):
    """An outcome word against the layer its clause is computed to read. A `refuse` belongs to the door: counted on
    any clause or change that reads another row. A `void` is final: counted on one that reads the rows held."""
    ref, fin = [], []
    for r in results:
        if r["grammar"] == "guard":
            ref += [(r["family"], r["text"], cl["at"]) for cl in r["clauses"] if cl["outcome"] == "refuse" and cl["layer"] != "kept"]
            fin += [(r["family"], r["text"], cl["at"]) for cl in r["clauses"] if cl["outcome"] == "void" and cl["layer"] == "derived"]
        if r["grammar"] == "change":
            if "refuse" in r["outcomes"] and r["layer_checks"] != "kept": ref.append((r["family"], r["text"], "0"))
            if "void" in r["outcomes"] and r["layer_checks"] == "derived": fin.append((r["family"], r["text"], "0"))
    return sorted(set(ref)), sorted(set(fin))


OUTCOME_PLANTS = [   # (grammar, made-up cell, counted as a refusal off the door, counted as a final word on a derived clause)
    ("guard", "one x:y@admitted[id=ref:a] else refuse", 1, 0),
    ("guard", "one x:y@named[id=ref:a] else refuse", 1, 0),
    ("guard", "one x:y@named[id=ref:a] else void", 0, 0),
    ("guard", "one x:y@admitted[id=ref:a] else void", 0, 1),
    ("guard", "when(member(signer,object)) (one x:y@named[id=ref:a] as E else void & member(E.signer,object) else refuse)", 1, 1),
    ("guard", "no x:y@admitted[object=object] else contested", 0, 0),
    ("guard", "each(subject) signs(key) else refuse", 0, 0),
    ("change", "replace: by=same_attester, refuse=t", 1, 0),
    ("change", "replace: by=same_attester, void=t", 0, 0),
    ("change", "replace[seat:serve]: by=same_attester, void=t", 0, 1),
    ("change", "replace: field=valid_until:as_attest, refuse=t", 0, 0),
]


def outcome_plants():
    out = []
    for g, text, want_ref, want_fin in OUTCOME_PLANTS:
        r = (run_guard if g == "guard" else run_change)({"family": "plant:x", g: text, "layers_only": True}, 0)
        ref, fin = outcome_measures([r])
        out.append((g, text, (len(ref), len(fin)), (want_ref, want_fin)))
    return out


def measures(results, counts, policy):
    ok = [r for r in results if r.get("status") in ("ok", "reads_dropped")]
    flagged = lambda fl: sorted({(r["grammar"], r["family"], r["text"]) for r in ok if fl in r["flags"]})
    m = {}
    m["ORDER_BY_SIGNED_INSTANT"] = flagged("ORDER_BY_SIGNED_INSTANT")      # the totals: gated, with the _CROSS counts
    m["ORDER_BY_DIGEST"] = flagged("ORDER_BY_DIGEST")
    for kind, name in (("signed_instant", "ORDER_BY_SIGNED_INSTANT"), ("digest", "ORDER_BY_DIGEST")):
        own, cross = set(), set()
        for r in ok:
            sites = [x for x in r.get("order_sites", []) if x[0] == kind and x[2] != "shown"]   # a listing picks no row (kx.order_sites)
            if not sites: continue
            key = (r["grammar"], r["family"], r["text"])
            if all(o is True for _, _, o in sites): own.add(key)
            else: cross.add(key + (",".join(sorted({mm for _, mm, o in sites if o is not True})),))
        m[name + "_OWN"] = sorted(own)
        m[name + "_CROSS"] = sorted(cross)
    m["ORDER_UNDECIDED"] = sorted({(r["grammar"], r["family"], r["text"], mm) for r in ok for _, mm, o in r.get("order_sites", []) if o is None})
    m["CROSS_SIGNER_INSTANT"] = flagged("CROSS_SIGNER_INSTANT") + [("policy", c["row"], "counted_at=" + c["value"]) for c in policy["counted_at"] if "CROSS_SIGNER_INSTANT" in c["flags"]]
    arr = []
    for r in ok:
        if r["grammar"] == "reaction": continue          # a clock or an expiry is a window: the one answer that reads now
        if r["grammar"] == "guard":
            if any("ARRIVAL" in cl["flags"] and not cl["window"] for cl in r["clauses"]): arr.append((r["grammar"], r["family"], r["text"]))
        elif "ARRIVAL" in r["flags"]: arr.append((r["grammar"], r["family"], r["text"]))
    m["ARRIVAL_OUTSIDE_WINDOW"] = sorted(set(arr))
    m["FLOATING_POINT"] = sorted({(r["grammar"], r["family"], r["text"]) for r in ok if r.get("gaps")})
    m["UNRESOLVED_FOLDS"] = sorted({u for r in ok if r["grammar"] == "reaction" for u in r.get("unresolved", [])})
    m["REFUSE_ON_NON_DOOR_CLAUSE"], m["FINAL_WORD_ON_DERIVED_CLAUSE"] = outcome_measures(ok)
    m["INSTANT_AT_DECISION"] = sorted({(r["family"], r["text"]) for r in ok if r.get("at_decision")})
    m["UNTYPED_MEMBERS"] = sorted({f.split(":", 1)[1] for r in ok for f in r["flags"] if f.startswith("UNTYPED:")})
    m["UNTRANSLATED_CELLS"] = sorted({(r["grammar"], r["family"], r["text"]) for r in results if r.get("status") not in ("ok", "labels_only", "reads_dropped")})
    m["READS_DROPPED"] = sorted({(r["grammar"], r["family"], r["text"]) for r in results if r.get("status") == "reads_dropped"}) + \
        [("policy", c["row"], c["column"] + "=" + c["value"]) for c in policy["dropped"]]
    m["CARRIED_WORD_COLLISIONS"] = sorted({(r["grammar"], r["family"], x) for r in ok for x in r.get("collisions", [])})
    m["UNCAUGHT_MUTANTS_POLICY"] = [(row, c["kx"]) for row, c in policy["counts"].items() for _ in range(c["uncaught"])]
    m["LABEL_WORDS_NOT_EVALUATED"] = sorted({(r["grammar"], r["family"], r["text"]) for r in results if r.get("labels")})
    for g in ("guard", "fold", "change", "reaction"):
        m[f"UNCAUGHT_MUTANTS_{g.upper()}"] = [(r["family"], r["text"]) for r in ok if r["grammar"] == g for _ in range(r["uncaught"])]
    return m


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":      # the generators must give the same rows on every run
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, dict(os.environ, PYTHONHASHSEED="0"))
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--root", default=os.path.dirname(HERE))
    ap.add_argument("--kernel-lib", default=None)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--json", default=None, help="write the per-cell results here")
    a = ap.parse_args()
    t0 = time.time()
    setup(a.root, a.kernel_lib, limit=False)
    cs = cells(a.root)
    jobs = [("guard", i, None) for i in range(len(cs["guard"]))] + [("fold", i, None) for i in range(len(cs["fold"]))] + \
           [("change", i, None) for i in range(len(cs["change"]))] + [("reaction", i, None) for i in range(len(cs["reaction"]))]
    plant_g = next(i for i, c in enumerate(cs["guard"]) if PLANT_GUARD in c["guard"])
    jobs = [("guard", plant_g, "plant"), ("fold", -1, "plant")] + jobs
    from multiprocessing import Pool
    with Pool(a.workers, initializer=setup, initargs=(a.root, a.kernel_lib)) as p:
        results = p.map(task, jobs, chunksize=2)
    plant_mis, plant_made = results[0], results[1]
    results = results[2:]
    counts = run_counts(); policy = run_policy()
    m = measures(results, counts, policy)
    maxima = {r["count"]: int(r["max"]) for r in tsv(kx.find(a.root, "tools/kx_maxima.tsv"))}
    refusals = []
    by = Counter(r["grammar"] for r in results)
    for g in ("guard", "fold", "change", "reaction"):
        rs = [r for r in results if r["grammar"] == g]
        st = Counter(r["status"] for r in rs)
        ag, di = sum(r.get("agree", 0) for r in rs), sum(r.get("disagree", 0) for r in rs)
        mu = sum(r.get("mutants", 0) for r in rs); un = sum(r.get("uncaught", 0) for r in rs)
        print(f"{g:9s} cells {len(rs):4d}  {dict(st)}  agree {ag}  disagree {di}  mutants {mu}, caught {mu - un}")
        if di: refusals.append(f"{g}: {di} evaluations where a translation and its original disagree: " + "; ".join(f"{r['family']} {r['text'][:60]}" for r in rs if r.get("disagree"))[:400])
    ca, cd = sum(r["agree"] for r in counts), sum(r["disagree"] for r in counts)
    print(f"count     families {len(counts):3d}  agree {ca}  disagree {cd}")
    print(f"policy    rows called {len(policy['rows_called'])}  vectors {policy['vectors'][0]}/{sum(policy['vectors'])}  rule vectors {policy['rule_vectors'][0]}/{sum(policy['rule_vectors'])}  decide() grid {policy['grid'][0]}/{sum(policy['grid'])}")
    if cd: refusals.append(f"count: {cd} disagreements")
    pc_ = policy["counts"]; pa, pdd = sum(c["agree"] for c in pc_.values()), sum(c["disagree"] for c in pc_.values())
    print(f"policy    counts of {len(pc_)} rows (count set, voice, voices, target silent) against the reference reading: agree {pa}  disagree {pdd}  "
          f"mutants {sum(c['mutants'] for c in pc_.values())}, caught {sum(c['mutants'] - c['uncaught'] for c in pc_.values())}")
    if pdd: refusals.append(f"policy counts: {pdd} disagreements: " + ", ".join(r for r, c in pc_.items() if c["disagree"]))
    for k in ("vectors", "rule_vectors", "grid"):
        if policy[k][1]: refusals.append(f"policy {k}: {policy[k][1]} disagree: {policy['examples'][:2]}")
    pm = plant_mis.get("disagree") or 0
    print(f"plant     the mistranslated cell ({plant_mis['family']}, meets read as member): {pm} disagreements, " + ("caught" if pm else "not caught"))
    if not pm: refusals.append("the planted mistranslation was not caught")
    gg = TOOLS["guard_grammar"]       # the second plant: a translator that reads every verdict word alike must be caught as a drop
    blur = lambda v: re.sub(r"'(refuse|void|contested|exclude|withhold|advise)", "'VERDICT", T.translate(gg.parse(v)[0]))
    pc = [x for c in cs["guard"] for x in collisions("guard", c["guard"], blur(c["guard"]), blur)]
    print(f"plant     a translator that reads every verdict word alike: {len(pc)} undeclared drops found, " + ("caught" if pc else "not caught"))
    if not pc: refusals.append("the planted undeclared drop was not caught")
    print(f"plant     the made-up cell `{PLANT_FOLD['fold']}`: {plant_made['status']} ({plant_made.get('err', '')})" + ("" if plant_made["status"] == "needs_operator" else ": not reported"))
    if plant_made["status"] != "needs_operator": refusals.append("the made-up cell needing an operator outside the language was not reported")
    words = Counter(w for r in results for w in r.get("dropped", []))
    print("dropped   words a cell uses that this translation does not carry (each cell reads_dropped, not translated):")
    for w, n in sorted(words.items(), key=lambda x: (-x[1], x[0])): print(f"            {n:3d}  {w}")
    pd = Counter(c["column"] for c in policy["dropped"])
    print("            policy cells not translated: " + ", ".join(f"{k} {v}" for k, v in sorted(pd.items())))
    bad_sets = [c for c in policy["count_set"] if c["flags"]]
    print(f"            policy count_set cells written as the seats they name: {len(policy['count_set'])}, {len(bad_sets)} with a flag (an expression with a layer; no agreement run)")
    if bad_sets: refusals.append("a count_set cell reads an instant or a rank: " + "; ".join(f"{c['row']} {c['flags']}" for c in bad_sets)[:300])
    # plants for the split: one fold ordering two signers' rows by asserted_at, one ordering one signer's own
    fg = TOOLS["fold_grammar"]; dparts = fg.parse(fg.DEFAULT)[0]["parts"]
    for text, want in (("key=attested_key_id; pick=max(asserted_at)", False), ("key=attesting_key_id; pick=max(asserted_at)", True)):
        parts = dict(fg.parse(text)[0]["parts"])
        for k in ("reads", "cut"):
            if k not in parts: parts[k] = dparts[k]
        sites = [x for x in kx.order_sites(kx.parse(T.Tx(parts, "plant:x", None).build())) if x[0] == "signed_instant"]
        got = bool(sites) and all(o is True for _, _, o in sites)
        print(f"plant     made-up fold `{text}`: " + ("OWN" if got else "CROSS") + (", as it must" if got == want else ", wrong"))
        if got != want: refusals.append(f"the made-up fold `{text}` was not counted {'OWN' if want else 'CROSS'}")
    # plants for a listing: an `order=` gives each standing row a position and no operator reads it, so it ranks nobody;
    # the same comparison read as a pick (the row at position 0 is selected) must still be counted across signers
    shown = sorted({(r["family"], r["text"]) for r in results for x in (r.get("order_sites") or []) if x[2] == "shown"})
    print(f"            listings that pick no row (a position for each row, read by no operator): {len(shown)}: " + "; ".join(f"{f} `{c}`" for f, c in shown))
    lparts = dict(fg.parse("key=attested_key_id; pick=union; order=min(key_id)")[0]["parts"], reads=dparts["reads"], cut=dparts["cut"])
    pos = "count(sel(S, \\x: lt_tuple(tuple(x.key_id), tuple(r.key_id))), \\x: x.id)"
    for name, expr, want in (("made-up fold `key=attested_key_id; pick=union; order=min(key_id)`", T.Tx(lparts, "plant:x", None).build(), ["shown"]),
                             ("the same order read as a pick (the row at position 0 is selected)", f"let S = sel(held, \\r: isfam(r, 'plant:x')) in sel(S, \\r: eq({pos}, 0))", [False]),
                             ("the same order under a least", f"let S = sel(held, \\r: isfam(r, 'plant:x')) in least(S, \\r: {pos})", [False])):
        got = sorted({o for k, mm, o in kx.order_sites(kx.parse(expr)) if mm == "key_id"}, key=repr)
        print(f"plant     {name}: " + ("a listing, not counted" if got == ["shown"] else "counted across signers" if got == [False] else f"read as {got}") + (", as it must" if got == want else ", wrong"))
        if got != want: refusals.append(f"the listing plant `{name}` gave {got}, not {want}")
    # plants for the gate, each against the measured sizes taken as the maxima: a cell that leaves CROSS for OWN must
    # pass, and one more ordering cell must be refused whichever side it is counted on
    sizes = {k: len(v) for k, v in m.items()}
    T_, O_, C_ = "ORDER_BY_SIGNED_INSTANT", "ORDER_BY_SIGNED_INSTANT_OWN", "ORDER_BY_SIGNED_INSTANT_CROSS"
    moved = dict(sizes, **{O_: sizes[O_] + 1, C_: sizes[C_] - 1})
    added = dict(sizes, **{O_: sizes[O_] + 1, T_: sizes[T_] + 1})
    crossed = dict(sizes, **{O_: sizes[O_] - 1, C_: sizes[C_] + 1})
    for name, case, want in (("a cell leaving CROSS for OWN", moved, []), ("one more cell ordering its signer's own rows", added, [T_]),
                             ("a cell leaving OWN for CROSS", crossed, [C_])):
        got = [k for k, _, _ in over_maximum(case, sizes)]
        print(f"plant     {name}: " + (f"refused on {', '.join(got)}" if got else "passes") + (", as it must" if got == want else ", wrong"))
        if got != want: refusals.append(f"the gate plant `{name}` gave {got}, not {want}")
    for word, dis in word_plants() + policy_plants():      # a misreading of each word given a meaning
        print(f"plant     the word {word}, misread: " + ("no cell holds it" if dis is None else f"{dis} disagreements, " + ("caught" if dis else "not caught")))
        if not dis: refusals.append(f"the misread word `{word}` was not caught")
    for g, text, got, want in outcome_plants():      # an outcome word on a made-up cell, against the layer the cell is computed to read
        say = lambda t: ("a refusal off the door" if t[0] else "") + (" and " if t[0] and t[1] else "") + ("a final word on a derived clause" if t[1] else "") or "not counted"
        print(f"plant     made-up {g} `{text}`: {say(got)}" + (", as it must" if got == want else ", wrong"))
        if got != want: refusals.append(f"the made-up {g} `{text}` was counted {got}, not {want}")
    print("counts    (may only fall; maxima in tools/kx_maxima.tsv)")
    for k, v in m.items():
        if k in REFERENCE:
            print(f"  {k:28s} {len(v):4d}  (for reference, not gated)"); continue
        mx = maxima.get(k)
        line = f"  {k:28s} {len(v):4d}" + (f"  max {mx}" if mx is not None else "  (no maximum recorded)")
        print(line)
    for k, n, mx in over_maximum({k: len(v) for k, v in m.items()}, maxima):
        if mx is None: refusals.append(f"{k} has no maximum in tools/kx_maxima.tsv")
        else: refusals.append(f"{k} rose to {n}, above its maximum {mx}: " + "; ".join(map(str, m[k][:4]))[:300])
    if a.json:
        json.dump({"results": results, "counts": counts, "policy": policy, "measures": m, "plants": [plant_mis, plant_made]}, open(a.json, "w"), indent=1, default=str)
    print(f"time {time.time() - t0:.1f} s on {a.workers} workers")
    if refusals:
        print("kx_check: refused")
        for r in refusals: print("  - " + r)
        return 1
    print("kx_check: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
