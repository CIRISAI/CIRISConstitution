#!/usr/bin/env python3
"""
check_conferral_two.py: one row that needs two standings (models/tla/CONFERRAL_END.md section J).

A node N is its owner's by an owner binding and holds a duty by a root grant. One act (a build row) needs both.
Each standing has its own record:

    the grant     head G0 (the bundle in force); EG, the count's end of the grant, naming G0
    the binding   B0 (N is O1's), B1 (a re-binding to O2, naming B0), B2 (a re-binding back to O1, naming B1).
                  Each re-binding ends the binding before it. A0, A1, A2 are the owner's acceptance of the
                  grant under B0, B1, B2

A stint is one binding with its owner. An act is judged under the grant and under each stint by
conferral_end.answers, and the answers are joined bit by bit: it counts for an owner when it counts under the
grant and under a stint of that owner, and it is in force when it is in force under both. The readings differ
in what the act names beside the grant's head, and in what an acceptance names:

    one         nothing (the text of CC 3.1.2.1 as it stood)
    named       the binding row it is under
    named_acc   B0 under the first binding; under a later one the owner's acceptance, which names its binding
    acc         always the owner's acceptance, which names its binding (the uniform form)
    acc_bare    always the owner's acceptance, which names the grant only. An owner bound a second time has
                one acceptance, A0, for both stints

"The binding in the act's causal past" is not a further reading. A row has in its past only what it, or a row
it names, names; so the binding is in an act's past only if the act names it or names a row that does.

Every world is built from a true history the graph does not show: how far along B1, A1, B2, A2 the signer had
got when it signed each act. An honest node names the newest row of its reading that it holds; holding a
re-binding and not yet its acceptance, it names the re-binding (or, under acc_bare, nothing), and the act
counts for nobody. A backdating node names what it would have named at an earlier accepted stint. Every set
of rows a reader may hold (closed under names) is judged.

Properties:
    old_owner   an honest act signed holding a re-binding does not count under a stint before it
    consent     an act counts under a stint only if its signer held that stint's acceptance when it signed
    one_owner   no act counts for both owners
    kept        an honest act signed under an accepted stint counts under it once the reader holds what its
                signer held
    backdated   a backdated act counts under no stint later than the one it names, and is in force under that
                one only by its owner's own receipt once the reader holds the re-binding
    ended       an honest act of a stint, not receipted, is in force for nobody once the reader holds the
                re-binding that ended the stint: a later stint of the same owner restores nothing
    grant_end   once the reader holds EG, an act the count did not receipt is in force for neither owner

Expected: `acc` and `named_acc` hold all seven. The others break what EXPECTED lists, and the run fails unless
it finds exactly that, which is this file's planted break.

    python3 -I check_conferral_two.py      exit 1 on any difference
"""
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import conferral_end as CE  # noqa: E402

READINGS = ("one", "named", "named_acc", "acc", "acc_bare")
PROPS = ("old_owner", "consent", "one_owner", "kept", "backdated", "ended", "grant_end")
EXPECTED = {"one": {"old_owner", "consent", "one_owner", "backdated", "ended"}, "named": {"consent"},
            "named_acc": set(), "acc": set(), "acc_bare": {"old_owner", "consent", "backdated", "ended"}}
OWNER = ("O1", "O2", "O1")
# what a signer holds, in order: level 0 is B0 and A0; then B1, A1, B2, A2
CHAIN = ("B1", "A1", "B2", "A2")


def stint_of(level):
    return (level + 1) // 2


def accepted_level(reading, k):
    """The level from which a signer holds stint k's acceptance."""
    return 3 if reading == "acc_bare" and k == 2 else 2 * k


def seat(reading, k):
    """The row an act names to stand on stint k."""
    if reading == "named" or (reading == "named_acc" and k == 0):
        return "B%d" % k
    if reading == "acc_bare":
        return "A%d" % (0 if k == 2 else k)
    return "A%d" % k


def honest_name(reading, level):
    if reading == "one":
        return None
    k = stint_of(level)
    if level >= accepted_level(reading, k) or reading == "named":
        return seat(reading, k)
    return None if reading == "acc_bare" else "B%d" % k


def act_name(reading, level, back):
    """`back`: None for an honest act, or the earlier accepted stint a backdating node names."""
    return honest_name(reading, level) if back is None else seat(reading, back)


def worlds():
    """(present chain length, has_eg, qg, qb, acts): acts as {id: (level, back)}."""
    for top, has_eg, n_acts, qg, qb in itertools.product(range(5), (0, 1), (1, 2), (0, 1), (0, 1)):
        for levels in itertools.combinations_with_replacement(range(top + 1), n_acts):   # a series only learns
            backs = [[None] + [k for k in range(stint_of(lv)) if True] for lv in levels]
            for back in itertools.product(*backs):
                yield top, has_eg, qg, qb, {"x%d" % (i + 1): (lv, b) for i, (lv, b) in enumerate(zip(levels, back))}


def row_names(reading, top, has_eg, qg, qb, acts):
    """Every row's names under a reading."""
    bare = reading == "acc_bare"
    full = {"G0": [], "B0": [], "A0": [] if bare else ["B0"]}
    for r in CHAIN[:top]:
        k = int(r[1])
        if r[0] == "B":
            full[r] = ["B%d" % (k - 1)]
        elif not (bare and k == 2):
            full[r] = [] if bare else ["B%d" % k]
    if has_eg:
        full["EG"] = ["G0"]
    prev = None
    for x in sorted(acts):
        b = act_name(reading, *acts[x])
        full[x] = ["G0"] + ([b] if b else []) + ([prev] if prev else [])
        prev = x
    if qg:
        full["qg"] = ["x1"]
    if qb:
        full["qb"] = ["x1"]
    return full


def closed_sets(full):
    ids = sorted(full)
    for bits in itertools.product((0, 1), repeat=len(ids)):
        held = {i for i, b in zip(ids, bits) if b}
        if {"G0", "B0", "A0"} <= held and all(set(full[i]) <= held for i in held):
            yield held


def judge(reading, acts, held, named=None):
    """{act: {"grant": (c, f), "stints": {k: (c, f)}}} over the rows a reader holds. `named`, when given, says
    what each act names beside the grant's head (the case table); otherwise the history in `acts` does."""
    xs = [x for x in acts if x in held]
    named = named or {x: act_name(reading, *acts[x]) for x in xs}
    grant = [CE.head("G0")] + [CE.act(x, "G0") for x in xs]
    if "EG" in held:
        grant.append(dict(CE.end("G0"), id="EG"))
    if "qg" in held:
        grant.append(CE.receipt("qg", "x1", CE.CONFERRER))
    g = CE.answers(grant)
    out = {x: {"grant": (g[x]["counted"], g[x]["in_force"]), "stints": {}} for x in xs}
    for k in range(3):
        b, nxt = "B%d" % k, "B%d" % (k + 1)
        if b not in held:
            continue
        ledger = [CE.head(b)]
        under = {}
        for x in xs:
            r = named[x]
            if reading == "one":
                under[x] = seat("acc", k) in held                     # by holding the acceptance
                ledger.append(CE.act(x, None))
            elif r == seat(reading, k):
                under[x] = reading != "named" or seat("acc", k) in held
                ledger.append(CE.act(x, b))
            else:
                # a row of a later stint has this stint's end in its past (E4); any other row is not under it
                later = r is not None and reading != "acc_bare" and int(r[1]) > k
                under[x] = False
                ledger.append(CE.act(x, None, names=[nxt] if later and nxt in held else []))
        if nxt in held:
            ledger.append(dict(CE.end(b), id=nxt))
        if "qb" in held and k == 0:
            ledger.append(CE.receipt("qb", "x1", CE.CONFERRER))       # the first owner's own receipt
        a = CE.answers(ledger)
        for x in xs:
            out[x]["stints"][k] = (under[x] and a[x]["counted"], under[x] and a[x]["in_force"])
    return out


# ---- the case table, under `acc`: hand-written answers the run must give ------------------------------------
T, F = True, False
NOBODY = {"O1": (F, F), "O2": (F, F)}
# (name, about, rows of the chain held, other rows held, {act: the row it names beside G0}, {act: {owner: (counted, in_force)}})
CASES = [
    ("names_bundle_and_acceptance", "the act names the bundle and its owner's acceptance of the grant",
     [], [], {"x1": "A0"}, {"x1": {"O1": (T, T), "O2": (F, F)}}),
    ("names_bundle_alone", "the act names the bundle only: it stands on no acceptance and counts for nobody",
     [], [], {"x1": None}, {"x1": NOBODY}),
    ("names_the_binding", "the act names the binding row itself, not the acceptance: it counts for nobody",
     [], [], {"x1": "B0"}, {"x1": NOBODY}),
    ("before_the_new_owners_acceptance", "signed under the re-binding before the new owner accepted (it names "
     "B1): it counts for nobody, and the acceptance held later adopts nothing",
     ["B1", "A1"], [], {"x1": "B1"}, {"x1": NOBODY}),
    ("under_the_new_owner", "the act names the new owner's acceptance",
     ["B1", "A1"], [], {"x1": "A1"}, {"x1": {"O1": (F, F), "O2": (T, T)}}),
    ("old_owners_act_after_the_rebinding", "the act names the first owner's acceptance and the reader holds the "
     "re-binding: counted for the first owner, not in force. An act signed before the re-binding and one "
     "backdated after it are the same rows",
     ["B1", "A1"], [], {"x1": "A0"}, {"x1": {"O1": (T, F), "O2": (F, F)}}),
    ("old_owners_act_receipted", "the same, and the first owner holds a receipt of the act: in force",
     ["B1", "A1"], ["qb"], {"x1": "A0"}, {"x1": {"O1": (T, T), "O2": (F, F)}}),
    ("grant_ended", "the count's end of the grant: counted, not in force",
     [], ["EG"], {"x1": "A0"}, {"x1": {"O1": (T, F), "O2": (F, F)}}),
    ("grant_ended_receipted", "the same, and the count holds a receipt of the act: in force",
     [], ["EG", "qg"], {"x1": "A0"}, {"x1": {"O1": (T, T), "O2": (F, F)}}),
    ("grant_receipt_does_not_keep_the_binding", "the count's receipt keeps the act under the grant; the "
     "re-binding still takes it out of force",
     ["B1", "A1"], ["EG", "qg"], {"x1": "A0"}, {"x1": {"O1": (T, F), "O2": (F, F)}}),
    ("second_stint_of_one_owner", "the first owner is bound again and accepts again: an act naming its first "
     "acceptance stays out of force, one naming the new acceptance is in force",
     ["B1", "A1", "B2", "A2"], [], {"x1": "A0", "x2": "A2"},
     {"x1": {"O1": (T, F), "O2": (F, F)}, "x2": {"O1": (T, T), "O2": (F, F)}}),
]
ROW_KIND = {"G": ("bundle", "count"), "B": ("binding", None), "A": ("acceptance", None), "E": ("end", "count"),
            "x": ("act", "N")}


def case_rows(chain, extra, named):
    """The rows of a case as the fixture lists them, and the set of their ids."""
    names = {"G0": [], "B0": [], "A0": ["B0"]}
    for r in chain:
        names[r] = ["B%d" % (int(r[1]) - (r[0] == "B"))]
    prev = None
    for x in sorted(named):
        names[x] = ["G0"] + ([named[x]] if named[x] else []) + ([prev] if prev else [])
        prev = x
    for r in extra:
        names[r] = ["G0"] if r == "EG" else ["x1"]
    rows = []
    for i, ns in names.items():
        if i == "qg":
            kind, signer = "receipt", "count"
        elif i == "qb":
            kind, signer = "receipt", "O1"
        else:
            kind, signer = ROW_KIND[i[0]]
            signer = signer or OWNER[int(i[1])]
        rows.append({"id": i, "kind": kind, "signer": signer, "names": ns})
    return rows, set(names)


def case_answers(named, held):
    out = {}
    for x, a in judge("acc", named, held, named=named).items():
        gc, gf = a["grant"]
        out[x] = {o: {"counted": gc and any(c for k, (c, _) in a["stints"].items() if OWNER[k] == o),
                      "in_force": gf and any(f for k, (_, f) in a["stints"].items() if OWNER[k] == o)}
                  for o in ("O1", "O2")}
    return out


def check_cases():
    problems = []
    for name, _, chain, extra, named, want in CASES:
        _, held = case_rows(chain, extra, named)
        got = case_answers(named, held)
        exp = {x: {o: {"counted": c, "in_force": f} for o, (c, f) in w.items()} for x, w in want.items()}
        if got != exp:
            problems.append("case %s: got %s, expected %s" % (name, got, exp))
    return problems


def fixture():
    """The case table as a fixture: rows, and for every act and owner whether it counts and is in force."""
    assert not check_cases(), check_cases()
    cases = []
    for name, about, chain, extra, named, _ in CASES:
        rows, held = case_rows(chain, extra, named)
        cases.append({"name": name, "about": about, "rows": rows, "answers": case_answers(named, held)})
    return {"about": "one row that needs two standings, an owner binding and a root grant (CC 3.1.2.1): "
                     "models/tla/CONFERRAL_END.md section J; generated from "
                     "models/causal_kernel/check_conferral_two.py under its reading `acc`",
            "roles": {"N": "the node", "O1": "the first owner", "O2": "the second owner", "count": "a counted row"},
            "rows": "G0 the bundle in force; B0, B1, B2 the binding and its re-bindings, each naming the one "
                    "before; A0, A1, A2 the owner's acceptance of the grant, naming its binding; EG the count's "
                    "end of the grant; qg the count's receipt of x1; qb the first owner's receipt of x1; an "
                    "act names G0, the row it stands on if any, and its signer's previous act",
            "cases": cases}


def main():
    broke = {r: {} for r in READINGS}
    n_worlds = n_states = 0
    for top, has_eg, qg, qb, acts in worlds():
        n_worlds += 1
        for reading in READINGS:
            full = row_names(reading, top, has_eg, qg, qb, acts)
            for held in closed_sets(full):
                n_states += 1
                for x, a in judge(reading, acts, held).items():
                    level, back = acts[x]
                    honest = back is None
                    mine = stint_of(level)
                    gc, gf = a["grant"]
                    st = a["stints"]
                    cnt = {k for k, (c, _) in st.items() if c}
                    frc = {k for k, (_, f) in st.items() if f}
                    rq = x == "x1" and "qb" in held
                    bad = []
                    if honest and any(k < mine for k in cnt):
                        bad.append("old_owner")
                    if any(level < accepted_level(reading, k) for k in cnt):
                        bad.append("consent")
                    if len({OWNER[k] for k in cnt}) > 1:
                        bad.append("one_owner")
                    signer_held = {"G0", "B0", "A0"} | {r for r in CHAIN[:level] if r in full}
                    if honest and level >= accepted_level(reading, mine) and signer_held <= held and mine not in cnt:
                        bad.append("kept")
                    if not honest and (any(k > back for k in cnt) or
                                       (frc and "B%d" % (back + 1) in held and not (rq and back == 0))):
                        bad.append("backdated")
                    if honest and frc and "B%d" % (mine + 1) in held and not (rq and mine == 0):
                        bad.append("ended")
                    if "EG" in held and not (x == "x1" and "qg" in held) and gf and frc:
                        bad.append("grant_end")
                    for p in bad:
                        broke[reading].setdefault(p, "%s signed holding %s%s; the reader holds %s" % (
                            x, list(CHAIN[:level]) or "B0 and A0 only",
                            "" if honest else " (backdated to stint %d)" % back, sorted(held)))
    problems = check_cases()
    for r in READINGS:
        if set(broke[r]) != EXPECTED[r]:
            problems.append("%s breaks %s, expected %s" % (r, sorted(broke[r]), sorted(EXPECTED[r])))
        for p in sorted(broke[r]):
            print("%-9s breaks %-9s %s" % (r, p, broke[r][p]))
        if not broke[r]:
            print("%-9s holds %s" % (r, ", ".join(PROPS)))
    print("%d cases under acc; %d true histories, %d (reading, held set) states" % (len(CASES), n_worlds, n_states))
    holds = [r for r in READINGS if not EXPECTED[r]]
    print("RESULT: %s" % ("ok: %s hold all %d properties; the other readings break what is expected of them"
                          % (" and ".join(holds), len(PROPS)) if not problems
                          else "%d problems: %s" % (len(problems), problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
