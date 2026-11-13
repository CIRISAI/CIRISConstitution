#!/usr/bin/env python3
"""
check_shapes.py: every row family as an instance of its shape (formal/derivation/family_shapes.tsv), run on this
directory's own kernel modules.

  0  the table: one row per family of manifests/family_model.json and no other; a known shape; parameters and
     sources name the same things in the same order; every quoted sentence stands verbatim in constitution/part_*.md
     under the section it cites; every cell path names a row and a column that exist; every door= value is a row of
     doors.tsv (or `none`)
  1  each family run as its shape, with its parameters
       consent  binds=signer: one row (seat.py, the key seats itself); signer+holder: two rows (roles.run_seat);
                body+holder: the roster (roster.py): a version by the count stands, one voice below it changes
                nothing, a removal by the count removes, one answer in every arrival order
       door     the doors.tsv rows it names (door.py through check_door.py's own worlds and properties, at three
                keys, a world set capped at 600 a door): which properties hold, the recount against the independent
                reference, the door's own mutation caught, one outcome in every arrival order of three worlds
       claim    claim.py: the trusted source read, an untrusted one not, two readers two readings, polarity refused,
                only the source retracts, a source seat read, one source saying two things says nothing, every order
       content  claim.py: the audience reads it and no one outside, only the author retracts or supersedes, every order
     status: sourced (every parameter has a source) | guessed (one at least is `guessed`) | cannot run (no world
     can be built: the reason is the family's misfit)
  2  mutations of claim.py, each to be caught; plants: three made-up families that fit no shape, each to be
     reported as not fitting
  3  the four shapes removed in order, each kept only if, given the removals already made, a family whose every
     parameter is sourced is left with no mechanism that keeps its shape's characteristic property

python3 -I check_shapes.py            compares every line with shapes_expected.tsv; exit 1 on any difference, an
                                      uncaught mutation, a plant reported as fitting, or a table defect
python3 -I check_shapes.py --write    rewrites shapes_expected.tsv
Two workers, each capped at 2 GiB of address space.
"""
import csv
import glob
import itertools
import json
import multiprocessing
import os
import random
import re
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
TABLE = os.path.join(ROOT, "formal", "derivation", "family_shapes.tsv")
EXPECTED = os.path.join(HERE, "shapes_expected.tsv")
SHAPES = ("consent", "door", "claim", "content")
PROCS = 2


def _limit():
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))


def _path():
    sys.path.insert(0, HERE)
    sys.dont_write_bytecode = True


# ---- 0. the table ---------------------------------------------------------------------------------------------------
def load_table():
    lines = [l for l in open(TABLE, encoding="utf-8") if not l.startswith("#")]
    rows = list(csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE))
    for r in rows:
        r["params"] = [tuple(x.split("=", 1)) for x in r["parameters"].split(" ; ")] if r["parameters"] else []
        r["srcs"] = [tuple(x.split(" <- ", 1)) for x in r["sources"].split(" ; ")] if r["sources"] else []
        r["P"] = dict(r["params"])
    return rows


def heads_index():
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "constitution", "part_*.md"))):
        h = None
        for line in open(p, encoding="utf-8"):
            m = re.match(r"^#+ (\d+(?:\.\d+)*)\s", line)
            if m: h = m.group(1)
            out.setdefault("lines", []).append((h, line))
    return out["lines"]


def table_checks(rows):
    bad = []
    model = {x["family"]: x for x in json.load(open(os.path.join(ROOT, "manifests", "family_model.json"), encoding="utf-8"))["rows"]}
    fams = [r["family"] for r in rows]
    for f in sorted(set(model) - set(fams)): bad.append("family missing from the table: " + f)
    for f in sorted(set(fams) - set(model)): bad.append("family in the table and not in family_model.json: " + f)
    if len(fams) != len(set(fams)): bad.append("a family is listed twice")
    doors = {l.split("\t")[0] for l in open(os.path.join(HERE, "doors.tsv"), encoding="utf-8")}
    need = {l.split("\t")[0] for l in open(os.path.join(ROOT, "formal", "derivation", "family_need.tsv"), encoding="utf-8")}
    files = {}
    def jfile(name):
        if name not in files: files[name] = json.load(open(os.path.join(ROOT, name), encoding="utf-8"))
        return files[name]
    lines = heads_index()
    for r in rows:
        f = r["family"]
        if r["shape"] not in SHAPES + ("consent+door", "none fits"): bad.append("%s: unknown shape %s" % (f, r["shape"]))
        if [k for k, _ in r["params"]] != [k for k, _ in r["srcs"]]: bad.append("%s: parameters and sources do not name the same things" % f)
        for k, s in r["srcs"]:
            if s == "guessed": continue
            m = re.match(r'^quote:CC ([\d.]+) "(.*)"$', s)
            if m:
                sec, q = m.groups()
                at = [h for h, line in lines if q in line]
                if not at: bad.append("%s: %s: quote not in the text" % (f, k))
                elif not any(h == sec for h in at): bad.append("%s: %s: quote stands under %s, not %s" % (f, k, at[0], sec))
                continue
            m = re.match(r"^cell:(manifests/[\w.]+\.json)#(.+)\.(\w+)$", s)
            if m:
                fn, key, col = m.groups()
                J = jfile(fn)
                if fn.endswith("family_model.json"):
                    ok = key in model and col in model[key]
                elif fn.endswith("governance_policy.json"):
                    ok = any(x["family"] == key and col in x for x in J["families"])
                elif fn.endswith("namespace_registry.json"):
                    ok = any(x["prefix"] == key for x in J["families"])
                else: ok = False
                if not ok: bad.append("%s: %s: no cell %s" % (f, k, s))
                continue
            m = re.match(r"^cell:manifests/reactions\.json#(.+)$", s)
            if m:
                if not any(e["family"] == m.group(1) for e in jfile("manifests/reactions.json")["reactions"]): bad.append("%s: %s: no reaction %s" % (f, k, s))
                continue
            m = re.match(r"^row:formal/causal_kernel/doors\.tsv#(.+)$", s)
            if m:
                if m.group(1) not in doors: bad.append("%s: %s: no door row %s" % (f, k, m.group(1)))
                continue
            m = re.match(r"^row:formal/derivation/family_need\.tsv#(.+)$", s)
            if m:
                if m.group(1) not in need: bad.append("%s: %s: no need row" % (f, k))
                continue
            bad.append("%s: %s: source not understood: %s" % (f, k, s))
        for dn in (r["P"].get("door", "none").split("|") if "door" in r["P"] else []):
            if dn != "none" and dn not in doors: bad.append("%s: door %s is not a row of doors.tsv" % (f, dn))
    return bad


def status(r):
    if r["shape"] == "none fits": return "cannot run"
    if r["P"].get("door") == "none" or r["P"].get("conferrer") == "unstated" or r["P"].get("signer") == "unstated" \
            or r["P"].get("role") == "a term on an offer":
        return "cannot run"
    return "guessed" if any(s == "guessed" for _, s in r["srcs"]) else "sourced"


# ---- 1. consent ---------------------------------------------------------------------------------------------------
def orders(rows, cap=40, seed=7):
    if len(rows) <= 6: return list(itertools.permutations(rows))
    rnd = random.Random(seed)
    return [tuple(rows), tuple(reversed(rows))] + [tuple(rnd.sample(rows, len(rows))) for _ in range(cap - 2)]


def one_answer(CK, rows, rule, answer):
    return len({answer(CK.arrive(list(o), rule)) for o in orders(rows)}) == 1


def run_consent(r):
    import seat as ST
    import roles as RL
    CK = ST.CK
    P, binds = r["P"], r["binds"]
    out, n = [], 0
    if binds == "body+holder" or "roster" in P:
        import roster as RO
        S = RO.instances()
        for inst in [x for x in P.get("roster", "community").split("|") if x in S]:
            sp = S[inst]
            sc = "founder" if inst == "infra" else None
            keys = ("k1", "k2", "k3", "k5") if inst == "infra" else ("k1", "k2", "k3")
            g = RO.found(sp, keys, scope=sc)
            acc = RO.accept(sp, "a4", "k4", scope=sc)
            full = RO.add(sp, "v1", (sp.obj,), "k4", keys, names=("a4",), scope=sc)
            lone = RO.add(sp, "v1", (sp.obj,), "k4", ("k1",), names=("a4",), scope=sc)
            rm = RO.remove(sp, "x1", (sp.obj,), "k3", keys[:2] + ((keys[3],) if inst == "infra" else ()), scope=sc)
            ro = lambda rows: frozenset(RO.roster(RO.state(rows), sp, sc))
            checks = [(ro([g]) == frozenset(keys), "the founding row seats its signers"),
                      (ro([g, acc, full]) == frozenset(keys) | {"k4"}, "a version by the count seats the joiner"),
                      (ro([g, acc, lone]) == frozenset(keys), "one voice below the count changes nothing"),
                      ("k3" not in ro([g] + rm), "a removal by the count removes")]
            if sp.consent == "own":
                checks.append((ro([g, full]) == frozenset(keys), "without the joiner's own consent nobody is seated"))
            rows = [g, acc, full]
            checks.append((len({ro(list(o)) for o in RO.linear_extensions(rows, cap=200)}) == 1, "one roster in every arrival order"))
            for ok, what in checks:
                n += 1
                if not ok: out.append("%s: %s" % (inst, what))
        if binds == "body+holder" and "conferrer" not in P: return out, n
    specs = []
    scope = P.get("scope", "x").split("|")[0]
    ends = P.get("ends", "withdraw:holder").replace(",", "; ")
    conf = P.get("conferrer", "self:holder").split("|")
    if binds == "signer":
        specs.append(dict(scope=scope, object="the key", conferrer="self:holder", consent="same_row", policy="-", ends=ends.replace("withdraw:conferrer", "withdraw:holder")))
    elif binds == "signer|signer+holder|body+holder":            # trust: the reader's edge and the duty
        specs.append(dict(scope="root", object="the reader", conferrer="self:object", consent="accept_row", policy="-", ends="withdraw:conferrer"))
        specs.append(dict(scope="moderate", object="a community", conferrer="group", consent="accept_row", policy="cosigned_act", ends="withdraw:holder; unseat:cosigned_act"))
    else:
        c0 = conf[0]
        if c0.startswith("group:"):
            specs.append(dict(scope=scope, object="a group", conferrer="group", consent="accept_row", policy=c0.split(":", 1)[1], ends=ends))
        else:
            specs.append(dict(scope=scope, object="the object", conferrer=c0, consent="accept_row", policy="-", ends=ends,
                              one=P.get("single") == "one"))
    for sp in specs:
        t = dict(sp, token=r["family"], way="", shape="seat")
        b, k, _ = RL.run_seat(t)
        out += ["%s: %s" % (sp["scope"], x) for x in b]; n += k
        w = RL.build(t)
        rows = list(w["rows"]) + [ST.withdraw("wh", "K", w["o"])]
        n += 1
        if not one_answer(CK, rows, ST.seat_rule, lambda S: ST.Seats(S).snapshot()): out.append("%s: two answers in two arrival orders" % sp["scope"])
        if sp.get("one"):
            o2, a2 = ST.offer("o2", w["rows"][0]["signer"], "K2", sp["scope"], w["obj"], "self"), ST.accept("a2", "K2", "o2")
            Q = lambda extra: ST.Seats(CK.concluded(CK.kept(list(w["rows"]) + extra), ST.seat_rule)).one(sp["scope"], w["obj"])
            n += 1
            if not (Q([]) == "K" and Q([o2, a2]) is None): out.append("single-valued: a second live holder leaves one")
    return out, n


# ---- 1. claim and content ----------------------------------------------------------------------------------------
def run_claim(r, model):
    import claim as CL
    CK = CL.CK
    f, x = r["family"], model[r["family"]]
    P = r["P"]
    pol = P.get("polarity", "signed")
    verbs = (x["verbs"]["value"] or [])
    src = P.get("source", "any_registered")
    scope = src[len("seat_role("):-1] if src.startswith("seat_role(") else "any"
    val = -1 if pol.startswith("-1") else 1
    rule = CL.claim_rule(pol)
    S_ = lambda rows: CK.concluded(CK.kept(rows), rule)
    tr = [CL.trust("t1", "RA", "S1", scope), CL.trust("t2", "RB", "S2", scope)]
    other = -0.5 if pol == "-1 / -0.5 only" else (val if pol == "-1 only" else 0.5)
    c1, c2, cz = CL.claim("c1", "S1", "s", f, val), CL.claim("c2", "S2", "s", f, other), CL.claim("cz", "Z", "s", f, val)
    out, n = [], 0
    def want(ok, what):
        nonlocal n
        n += 1
        if not ok: out.append(what)
    S = S_(tr + [c1, c2, cz])
    ra, rb = CL.read(S, "RA", "s", f, scope), CL.read(S, "RB", "s", f, scope)
    want(ra == {"S1": val}, "the trusted source is not read")
    want("Z" not in ra and "Z" not in rb, "an untrusted source moved the reading")
    want(ra != rb, "two readers with different trust read one verdict")
    bad = 1 if val < 0 else -1
    if not CL.in_polarity(pol, bad): want(not S_(tr + [CL.claim("cb", "S1", "s", f, bad)]).C.get("cb"), "a value outside the polarity concluded")
    for verb in ("withdraw", "recant"):
        if verb in verbs:
            want(CL.read(S_(tr + [c1, CL.retract("w", "S1", "c1", verb)]), "RA", "s", f, scope) == {}, "the source's own %s does not end it" % verb)
            want(CL.read(S_(tr + [c1, CL.retract("w", "Z", "c1", verb)]), "RA", "s", f, scope) == {"S1": val}, "a third key's %s ended it" % verb)
    if "replace" in verbs:
        want(CL.read(S_(tr + [c1, CL.claim("c1b", "S1", "s", f, val, ("c1",))]), "RA", "s", f, scope) == {"S1": val}, "a supersede by the source is not read")
    if scope != "any":
        want(CL.read(S_([CL.trust("t1", "RA", "S1", "other"), c1]), "RA", "s", f, scope) == {}, "a source trusted outside the family's seat was read")
    alt = CL.claim("c1c", "S1", "s", f, other if other != val else 2 * val)
    if CL.in_polarity(pol, alt["value"]) and alt["value"] != val:
        want(CL.read(S_(tr + [c1, alt]), "RA", "s", f, scope) == {}, "a source saying two concurrent things said one")
    n += 1
    if not one_answer(CK, tr + [c1, alt, cz], rule, lambda S: tuple(sorted(CL.read(S, "RA", "s", f, scope).items()))):
        out.append("two answers in two arrival orders")
    return out, n


def audience_of(r):
    a = r["P"].get("audience", "")
    if a == "addressee": return {"RCP"}
    if a == "self_collective": return ("roster", "g", "self")
    return None


def run_content(r, model):
    import claim as CL
    import seat as ST
    CK = CL.CK
    f, x = r["family"], model[r["family"]]
    verbs = x["verbs"]["value"] or []
    aud = audience_of(r)
    base = []
    if isinstance(aud, tuple): base = [ST.offer("g", "RCP", ("RCP", "AU"), "self", "@", "self", cosigners=("AU",))]
    rule = lambda q, P_, past: ST.seat_rule(q, P_, past)
    S_ = lambda rows: CK.concluded(CK.kept(base + rows), rule)
    c = CL.content("p1", "AU", "item", aud)
    out, n = [], 0
    def want(ok, what):
        nonlocal n
        n += 1
        if not ok: out.append(what)
    want(CL.visible(S_([c]), "RCP", "p1"), "its audience cannot read it")
    if aud is not None: want(not CL.visible(S_([c]), "Z", "p1"), "a reader outside the audience reads it")
    for verb in ("withdraw", "recant"):
        if verb in verbs:
            want(not CL.visible(S_([c, CL.retract("w", "AU", "p1", verb)]), "RCP", "p1"), "the author's %s does not hide it" % verb)
            want(CL.visible(S_([c, CL.retract("w", "Z", "p1", verb)]), "RCP", "p1"), "a third key's %s hid it" % verb)
    if "replace" in verbs:
        S = S_([c, CL.content("p2", "AU", "item", aud, ("p1",))])
        want(not CL.visible(S, "RCP", "p1") and CL.visible(S, "RCP", "p2"), "a supersede by the author does not replace it")
        want(CL.visible(S_([c, CL.content("pz", "Z", "item", aud, ("p1",))]), "RCP", "p1"), "a stranger's version superseded it")
    rows = base + [c, CL.content("p2", "AU", "item", aud, ("p1",)), CL.retract("w", "Z", "p1")]
    n += 1
    if not one_answer(CK, rows, rule, lambda S: tuple(CL.visible(S, "RCP", i) for i in ("p1", "p2"))): out.append("two answers in two arrival orders")
    return out, n


# ---- 1. doors ---------------------------------------------------------------------------------------------------
CAP = 600


def door_sig(CD, name):
    """The door's own properties over its worlds at three keys (capped), its mutation, and three worlds in every order."""
    def sample(nk):
        CD.NK = nk
        CD.set_mut(None)
        ws = CD.worlds(name)
        return ws[::-(-len(ws) // CAP)] if len(ws) > CAP else ws
    ws = sample(3)
    def judge():
        res, rc_bad, fails = {}, 0, 0
        P = CD.props(name)
        for w in ws:
            try:
                _, o = CD.run(CD.rows_of(w), name)
            except CD.K.Tie:
                o = "tie"
            ok = CD.recount_ok(w, o)
            if ok is False: rc_bad += 1
            for label, _, pr in P:
                v = pr(w, o)
                if v is None: continue
                res.setdefault(label, [0, 0])[0 if v else 1] += 1
        return res, rc_bad
    base, rc = judge()
    CD.set_mut(CD.MUTATION[name][0])
    mres, mrc = judge()
    CD.set_mut(None)
    caught = mres != base or mrc != rc
    if not caught and name not in CD.THREE_ONLY:           # check_door also runs four keys: some floors show only there
        ws = sample(4)
        b4, r4 = judge()
        CD.set_mut(CD.MUTATION[name][0]); m4, mr4 = judge(); CD.set_mut(None)
        caught = m4 != b4 or mr4 != r4
        ws = sample(3)
    rnd = random.Random(3)
    differ = 0
    pick = [w for w in ws if w["L"][2]][:: max(1, len(ws) // 3)][:3]
    for w in pick:
        rows = CD.rows_of(w)
        S0 = CD.CK.concluded(CD.CK.kept(rows), CD.D.rule)
        want = CD.D.outcome(S0, "p")
        for _ in range(30):
            S = CD.CK.arrive(rnd.sample(rows, len(rows)), CD.D.rule)
            differ += CD.D.outcome(S, "p") != want
    held = sorted(l for l, (a, b) in base.items() if b == 0)
    broke = sorted(l for l, (a, b) in base.items() if b)
    return {"worlds": len(ws), "held": len(held), "broke": broke, "recount_bad": rc, "caught": caught, "order_differ": differ}


def door_job(names):
    _limit(); _path()
    import check_door as CD
    return {n: door_sig(CD, n) for n in names}


# ---- 2. mutations and plants -------------------------------------------------------------------------------------
def mutations():
    import claim as CL
    CK = CL.CK
    out = []
    tr = [CL.trust("t1", "RA", "S1"), CL.trust("t2", "RB", "S2")]
    cl = [CL.claim("c1", "S1", "s", "d", 1), CL.claim("c2", "S2", "s", "d", 0.5), CL.claim("cz", "Z", "s", "d", 1)]
    def with_mut(m, fn):
        CL.MUT.clear(); CL.MUT.add(m)
        try: return fn()
        finally: CL.MUT.clear()
    S = lambda rows, pol="signed": CK.concluded(CK.kept(rows), CL.claim_rule(pol))
    out.append(("claim: an untrusted source moves nothing (everyone)", with_mut("everyone", lambda: "Z" in CL.read(S(tr + cl), "RA", "s", "d"))))
    out.append(("claim: only the source retracts (any_signer)", with_mut("any_signer", lambda: CL.read(S(tr + cl + [CL.retract("w", "Z", "c1")]), "RA", "s", "d") == {})))
    out.append(("claim: polarity refused (no_polarity)", with_mut("no_polarity", lambda: bool(S(tr + [CL.claim("cb", "S1", "s", "d", -1)], "positive-only").C.get("cb")))))
    out.append(("claim: the source seat is read (ignore_scope)", with_mut("ignore_scope", lambda: CL.read(S([CL.trust("t1", "RA", "S1", "other"), cl[0]]), "RA", "s", "d", "attest") != {})))
    two = tr + [CL.claim("c1", "S1", "s", "d", 1), CL.claim("c3", "S1", "s", "d", 2)]
    out.append(("claim: one answer in every order (last_held)", with_mut("last_held", lambda: len({tuple(CL.read(CK.arrive(list(o), CL.claim_rule("signed")), "RA", "s", "d").items())
                                                                                              for o in itertools.permutations(two)}) > 1)))
    c = CL.content("p1", "AU", "i", {"RCP"})
    Sc = lambda rows: CK.concluded(CK.kept(rows), lambda r, P, past: True)
    out.append(("content: the audience is read (ignore_audience)", with_mut("ignore_audience", lambda: CL.visible(Sc([c]), "Z", "p1"))))
    out.append(("content: only the author retracts (any_signer)", with_mut("any_signer", lambda: not CL.visible(Sc([c, CL.retract("w", "Z", "p1")]), "RCP", "p1"))))
    return out


PLANTS = [  # made-up families that fit no shape: each must be reported as not fitting
    {"family": "plant:beacon_lottery", "shape": "door", "binds": "-", "P": {"door": "beacon_draw", "role": "landing"}, "why": "a door with no doors.tsv row"},
    {"family": "plant:first_wins", "shape": "consent", "binds": "signer+holder", "P": {"scope": "member", "conferrer": "first_arrival", "ends": "withdraw:holder"}, "why": "a seat conferred by whichever offer arrived first"},
    {"family": "plant:third_end", "shape": "consent", "binds": "signer+holder", "P": {"scope": "member", "conferrer": "self:object", "ends": "withdraw:third"}, "why": "a seat a third key ends"},
]


def plants(doors):
    out = []
    for pl in PLANTS:
        r = dict(pl, params=list(pl["P"].items()), srcs=[(k, "guessed") for k in pl["P"]])
        try:
            if r["shape"] == "door":
                got = "not fitting" if any(d not in doors for d in r["P"]["door"].split("|")) else "fits"
            else:
                bad, _ = run_consent(r)
                got = "not fitting" if bad else "fits"
        except (ValueError, KeyError, StopIteration) as e:
            got = "not fitting"
        out.append((pl["family"], pl["why"], got))
    return out


# ---- 3. removal in order -----------------------------------------------------------------------------------------
def characteristic():
    """Each shape's characteristic property, run on each candidate mechanism. True: the mechanism keeps it."""
    import claim as CL
    import seat as ST
    import roles as RL
    CK = CL.CK
    M = {}
    # consent: with two voices bound, the conferrer's row alone does not stand, and the holder's own withdrawal ends it
    M[("consent", "consent")] = not RL.run_seat(dict(scope="x", object="o", conferrer="self:object", consent="accept_row", policy="-",
                                                     ends="withdraw:holder", token="t", way="", shape="seat"))[0]
    Sx = CK.concluded(CK.kept([CL.claim("o", "A", "K", "seat", 1), CL.trust("t", "R", "A")]), CL.claim_rule("signed"))
    M[("consent", "claim")] = CL.read(Sx, "R", "K", "seat") == {}                       # the offer alone reads as standing: not kept
    Sc = CK.concluded(CK.kept([CL.content("o", "A", "seat:K")]), lambda r, P, past: True)
    M[("consent", "content")] = not CL.visible(Sc, "R", "o")                             # the same
    M[("consent", "door")] = False                                                        # no door ends by the holder's own withdrawal
    # door: with no answers, a landing of the default before the close concludes nothing, and at the close it does
    M[("door", "door")] = True                                                            # door.py: per door, checked in part 1
    for m in ("consent", "claim", "content"):
        M[("door", m)] = False                                                            # none of them reads now: a row before the close concludes the same
    # claim: two readers with different trust read differently; an untrusted source moves nothing
    tr = [CL.trust("t1", "RA", "S1"), CL.trust("t2", "RB", "S2")]
    cl = [CL.claim("c1", "S1", "s", "d", 1), CL.claim("c2", "S2", "s", "d", 2)]
    S = CK.concluded(CK.kept(tr + cl), CL.claim_rule("signed"))
    M[("claim", "claim")] = CL.read(S, "RA", "s", "d") != CL.read(S, "RB", "s", "d")
    # on the consent mechanism: a reader's trust edge is a one-voice consent and the walk is the kernel's own (reach/means)
    E = CK.live_edges(S)
    M[("claim", "consent")] = CK.means(S, S.by["c1"], "RA", 2, E) and not CK.means(S, S.by["c1"], "RB", 2, E)
    Sct = CK.concluded(CK.kept([CL.content("c1", "S1", "i"), CL.content("c2", "S2", "j")]), lambda r, P, past: True)
    M[("claim", "content")] = CL.visible(Sct, "RA", "c1") != CL.visible(Sct, "RB", "c1")
    M[("claim", "door")] = False
    # content: every member of the audience reads it whatever it trusts, and no one outside
    g = ST.offer("g", "RCP", ("RCP", "AU"), "member", "@", "self", cosigners=("AU",))
    cr = CL.content("p", "AU", "i", ("roster", "g", "member"))
    S = CK.concluded(CK.kept([g, cr]), ST.seat_rule)
    M[("content", "content")] = CL.visible(S, "RCP", "p") and not CL.visible(S, "Z", "p")
    # on the consent mechanism: the audience is the holders of a roster (seat.Seats.holders), the row live by `state`
    hold = ST.Seats(S).holders("member", "g")
    M[("content", "consent")] = "RCP" in hold and "Z" not in hold and S.C.get("p")
    Scl = CK.concluded(CK.kept([CL.claim("p", "AU", "s", "d", 1)]), CL.claim_rule("signed"))
    M[("content", "claim")] = CL.read(Scl, "RCP", "s", "d") != {}                        # a member who trusts nobody reads nothing: not kept
    M[("content", "door")] = False
    return {k: bool(v) for k, v in M.items()}


def removal(rows, M, order):
    alive, log = set(SHAPES), []
    def shapes_of(r): return [s for s in SHAPES if s in r["shape"].split("+")]
    for s in order:
        trial = alive - {s}
        lost = [r["family"] for r in rows if r["status"] == "sourced" and any(not any(M[(fs, m)] for m in trial) for fs in shapes_of(r))]
        if lost: log.append((s, "kept", len(lost), lost[0]))
        else: alive = trial; log.append((s, "removed", 0, "-"))
    return alive, log


# ---- driver -------------------------------------------------------------------------------------------------------
def rest_job(_):
    _limit(); _path()
    rows = load_table()
    model = {x["family"]: x for x in json.load(open(os.path.join(ROOT, "manifests", "family_model.json"), encoding="utf-8"))["rows"]}
    doors = {l.split("\t")[0] for l in open(os.path.join(HERE, "doors.tsv"), encoding="utf-8")}
    res = {}
    for r in rows:
        st = status(r)
        if st == "cannot run": res[r["family"]] = (st, "cannot run: " + r["misfit"], 0); continue
        bad, n = [], 0
        try:
            for s in r["shape"].split("+"):
                if s == "consent": b, k = run_consent(r)
                elif s == "claim": b, k = run_claim(r, model)
                elif s == "content": b, k = run_content(r, model)
                else: continue
                bad += b; n += k
            res[r["family"]] = (st, "breaks: " + "; ".join(bad) if bad else "runs", n)
        except Exception as e:  # noqa: BLE001
            res[r["family"]] = (st, "error: %s: %s" % (type(e).__name__, e), n)
    M = characteristic()
    return {"families": res, "mutations": mutations(), "plants": plants(doors), "M": M}


def main():
    t0 = time.time()
    write = "--write" in sys.argv
    _limit(); _path()
    rows = load_table()
    got, problems = [], []
    tb = table_checks(rows)
    for b in tb: got.append(("table", b, "defect")); problems.append("table: " + b)
    used = sorted({d for r in rows if status(r) != "cannot run" for d in r["P"].get("door", "none").split("|") if "door" in r["P"] and d != "none"})
    half = len(used) // 2
    with multiprocessing.Pool(PROCS, maxtasksperchild=1) as mp:
        jobs = [mp.apply_async(rest_job, (None,)), mp.apply_async(door_job, (used,))]
        rest, doors = jobs[0].get(), jobs[1].get()
    for r in rows:
        st, verdict, n = rest["families"][r["family"]]
        if st != "cannot run" and "door" in r["P"]:
            ds = [doors[d] for d in r["P"]["door"].split("|")]
            n += sum(d["worlds"] for d in ds)
            notes = []
            for dn, d in zip(r["P"]["door"].split("|"), ds):
                if d["broke"]: notes.append("%s breaks %s" % (dn, ", ".join(d["broke"])))
                if not d["caught"]: problems.append("%s: door %s: its mutation was not caught" % (r["family"], dn))
                if d["order_differ"]: problems.append("%s: door %s: two outcomes in two arrival orders" % (r["family"], dn))
            if verdict == "runs" and notes: verdict = "runs; " + "; ".join(notes)
        r["status"] = st
        got.append((r["family"], r["shape"] + (" binds=" + r["binds"] if r["binds"] not in ("-", "") else ""), st + " | " + verdict))
        if verdict.startswith("error") or verdict.startswith("breaks"): problems.append("%s: %s" % (r["family"], verdict))
    for d in used:
        x = doors[d]
        got.append(("door " + d, "%d worlds, %d properties hold" % (x["worlds"], x["held"]),
                    "breaks: " + ", ".join(x["broke"]) if x["broke"] else "holds"))
        got.append(("door " + d, "plant: its mutation (check_door.MUTATION)", "caught" if x["caught"] else "not caught"))
    for label, caught in rest["mutations"]:
        got.append(("claim.py", "plant: mutation " + label, "caught" if caught else "not caught"))
        if not caught: problems.append("mutation not caught: " + label)
    for fam, why, v in rest["plants"]:
        got.append((fam, "plant: " + why, v))
        if v != "not fitting": problems.append("plant reported as fitting: " + fam)
    M = rest["M"]
    for (s, m), v in sorted(M.items()):
        got.append(("mechanism " + m, "keeps the characteristic property of " + s, "yes" if v else "no"))
    for order in (["content", "claim", "door", "consent"], ["claim", "content", "consent", "door"], ["door", "consent", "content", "claim"]):
        alive, log = removal(rows, M, order)
        got.append(("removal", "order " + " > ".join(order), "surviving " + ",".join(s for s in SHAPES if s in alive) + " | " +
                    " ; ".join("%s %s%s" % (s, w, (" (loses %d, e.g. %s)" % (n, e)) if n else "") for s, w, n, e in log)))
    import collections
    cnt = collections.Counter(r["shape"] for r in rows)
    st = collections.Counter(r["status"] for r in rows)
    got.append(("counts", "families per shape", ", ".join("%s %d" % kv for kv in sorted(cnt.items()))))
    got.append(("counts", "status", ", ".join("%s %d" % kv for kv in sorted(st.items()))))
    say = lambda s: print(s, flush=True)
    if write:
        with open(EXPECTED, "w", encoding="utf-8", newline="") as fh:
            fh.write("# What check_shapes.py gives for every family of formal/derivation/family_shapes.tsv, each door it runs, each plant and the ordered removal.\n")
            w = csv.writer(fh, delimiter="\t", lineterminator="\n")
            w.writerow(["subject", "what", "verdict"])
            for g in got: w.writerow(g)
        say("wrote %s (%d lines)" % (os.path.basename(EXPECTED), len(got)))
    else:
        lines = [l for l in open(EXPECTED, encoding="utf-8") if not l.startswith("#")]
        want = [tuple(x) for x in list(csv.reader(lines, delimiter="\t"))[1:]]
        gs, ws = set(got), set(want)
        for g in sorted(gs - ws): problems.append("new or changed: %s" % " | ".join(g))
        for g in sorted(ws - gs): problems.append("expected and not given: %s" % " | ".join(g))
    say("families %d: %s" % (len(rows), ", ".join("%s %d" % kv for kv in sorted(cnt.items()))))
    say("status: %s" % ", ".join("%s %d" % kv for kv in sorted(st.items())))
    say("doors run: %d; claim.py mutations caught %d of %d; plants not fitting %d of %d" % (
        len(used), sum(c for _, c in rest["mutations"]), len(rest["mutations"]),
        sum(v == "not fitting" for _, _, v in rest["plants"]), len(rest["plants"])))
    for g in got:
        if g[0] == "removal": say("removal %s -> %s" % (g[1], g[2]))
    say("%.1f s" % (time.time() - t0))
    if problems:
        for p in problems: say("DIFFERS " + p)
        return 1
    say("same as %s" % os.path.basename(EXPECTED) if not write else "written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
