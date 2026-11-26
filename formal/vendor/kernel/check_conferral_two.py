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

The chain as one function. `chain_answers` is the rule under `acc` as a function of the held rows, as the crate
has it (`ciris_kernel::standing::answers`): it finds the acceptance an act names and the binding that
acceptance names, judges the act once under the grant and once under that binding with conferral_end.answers,
and joins the bits. It reads the causal past from what the rows name, an act's previous act included, where
`judge` above builds each record's ledger from the act's head alone. The run compares the two on every state
of `acc` and requires every difference to be the one kind DIFFERS describes.

A second bundle version. G1 names G0. The conferral-end rules are applied as they are: an act names the bundle
version it is at, the grant's end names its own, and E1, E2, E3 and the reader's line decide. The cases under
"a later bundle version" are what those rules give; nothing is added to make an answer come out.

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


def judge(reading, acts, held, named=None, opt=None):
    """{act: {"grant": (c, f), "stints": {k: (c, f)}}} over the rows a reader holds. `named`, when given, says
    what each act names beside the grant's head (the case table); otherwise the history in `acts` does. `opt`
    (the case table) places the grant on two bundle versions: `heads` the version each act names, `eg` the one
    the grant's end names, `eg_names` what else the end names, `acks` the reader's acknowledged versions."""
    opt = opt or {}
    xs = [x for x in acts if x in held]
    named = named or {x: act_name(reading, *acts[x]) for x in xs}
    grant = [CE.head("G0")] + ([CE.head("G1", "G0")] if "G1" in held else [])
    grant += [CE.act(x, opt.get("heads", {}).get(x, "G0")) for x in xs]
    if "EG" in held:
        grant.append(dict(CE.end(opt.get("eg", "G0"), names=opt.get("eg_names", ())), id="EG"))
    if "qg" in held:
        grant.append(CE.receipt("qg", "x1", CE.CONFERRER))
    g = CE.answers(grant, reader_acks=opt.get("acks", ()))
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


# ---- the chain as one function of the held rows (the crate's standing::answers) -------------------------------
ROLE = {"count": CE.CONFERRER, "N": CE.GRANTEE}     # who a key is to the grant: the count confers, the node holds


def chain_answers(rows, reader_acks=(), role=None):
    """{act: {"reason", "binding", "owner", "grant", "under", "counted", "in_force"}} over the held rows.

    Rows: `bundle` (a bundle version, naming the one before), `binding` (`owner`; `on` the binding it re-binds,
    which it ends), `acceptance` (`on` the binding it is made under), `act` (`head` the bundle version it names,
    `on` the row it stands on), `end` (the grant's end, `head`), `receipt` (`on` the act), `removal` (`target`
    the key; read in both records. No case has one).
    `reason` is "stands" where the act names an acceptance its binding's owner signed, and then `grant` and
    `under` are the rules conferral_end.answers gives under the grant and under that binding; otherwise it says
    why the act counts for nobody, or is "undecided" with the row to fetch in `binding`."""
    role = role or ROLE
    by, anc = CE._past(rows)

    def where(x):
        on = x.get("on")
        if on is None:
            return "no_acceptance", None
        if on not in by:
            return "undecided", on
        a = by[on]
        if a["kind"] == "binding":
            return "names_binding", None
        if a["kind"] != "acceptance":
            return "not_an_acceptance", None
        b = a.get("on")
        if b is None:
            return "acceptance_names_no_binding", None
        if b not in by:
            return "undecided", b
        if by[b]["kind"] != "binding":
            return "acceptance_names_no_binding", None
        if a["signer"] != by[b]["owner"]:
            return "not_the_owners_acceptance", None
        if two_owners(x, by[b]):
            return "two_owners", None
        return "stands", b

    def rebinds(c, b):
        """c is b, or re-binds b through a chain of re-bindings (`on`)."""
        seen = set()
        while c is not None and c["id"] not in seen:
            if c["id"] == b["id"]:
                return True
            seen.add(c["id"])
            c = by.get(c.get("on")) if c.get("on") else None
        return False

    def two_owners(x, b):
        """CC 3.2: a key with two live owner-bindings naming different owners has no owner ("two owners is none";
        seat.Seats.one). A binding of the node held that names another owner, neither binding in the other's
        past, and not ended in the act's past (no re-binding of it there), leaves the act standing on nobody."""
        for c in rows:
            if c["kind"] != "binding" or c["id"] == b["id"] or c.get("owner") == b.get("owner"):
                continue
            if rebinds(c, b) or rebinds(b, c):
                continue                                                     # one ends the other: a stint, not a rival
            if any(e["kind"] == "binding" and e.get("on") == c["id"] and e["id"] in anc(x["id"]) for e in rows):
                continue
            return True
        return False

    def record(kind_of, signer_of):
        """The rows as conferral_end reads one record: every row, so that the past is the one the rows name."""
        out = []
        for r in rows:
            k, head = kind_of(r)
            row = {"id": r["id"], "kind": k, "signer": signer_of(r["signer"]), "names": r["names"]}
            if k in ("act", "end"):
                row["head"] = head
            if k == "receipt":
                row["of"] = r["on"]
            if k == "removal":
                row["target"] = signer_of(r["target"])
            out.append(row)
        return out

    acts = [r for r in rows if r["kind"] == "act"]
    stand = {x["id"]: where(x) for x in acts}
    kinds = {"bundle": "head", "act": "act", "end": "end", "receipt": "receipt", "removal": "removal"}
    g = CE.answers(record(lambda r: (kinds.get(r["kind"], "other"), r.get("head")), lambda k: role.get(k, "-" + k)),
                   reader_acks=reader_acks)
    under = {}
    for b in sorted({b for why, b in stand.values() if why == "stands"}):
        mine = {x for x, (why, at) in stand.items() if why == "stands" and at == b}

        def kind_of(r):
            if r["id"] == b:
                return "head", None
            if r["id"] in mine:
                return "act", b
            if r["kind"] == "binding" and r.get("on") == b:
                return "end", b
            return (r["kind"] if r["kind"] in ("receipt", "removal") else "other"), None
        owner = by[b]["owner"]
        got = CE.answers(record(kind_of, lambda k: CE.CONFERRER if k == owner else "-" + k))
        under.update({x: got[x] for x in mine})
    out = {}
    for x, (why, b) in stand.items():
        if why != "stands":
            out[x] = {"reason": why, "binding": b, "owner": None, "grant": None, "under": None,
                      "counted": False, "in_force": False}
            continue
        out[x] = {"reason": why, "binding": b, "owner": by[b]["owner"], "grant": g[x]["rule"],
                  "under": under[x]["rule"], "counted": g[x]["counted"] and under[x]["counted"],
                  "in_force": g[x]["in_force"] and under[x]["in_force"]}
    return out


def per_owner(ans):
    return {x: {o: {"counted": a["owner"] == o and a["counted"], "in_force": a["owner"] == o and a["in_force"]}
                for o in ("O1", "O2")} for x, a in ans.items()}


# ---- the case table, under `acc`: hand-written answers the run must give ------------------------------------
T, F = True, False
NOBODY = {"O1": (F, F), "O2": (F, F)}
G1 = {"bundles": ["G1"]}
# (name, about, rows of the chain held, other rows held, {act: the row it names beside its bundle version},
#  {act: {owner: (counted, in_force)}}, and for some an `opt`: `bundles` the further bundle versions held, `heads`
#  the version each act names (G0 otherwise), `eg` and `eg_names` the version the grant's end names and what
#  else it names, `acks` the versions the reader acknowledged, `signers` a row signed by another key, `ledgers`
#  what `judge` gives where it differs from the rule (see DIFFERS))
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
    # the chain read from the rows: what the per-record ledgers do not carry
    ("acceptance_by_another_key", "the acceptance the act names is signed by a key that is not its binding's "
     "owner: it is not the owner's acceptance, and the act counts for nobody",
     [], [], {"x1": "A0"}, {"x1": NOBODY}, {"signers": {"A0": "O2"}, "ledgers": {"x1": {"O1": (T, T)}}}),
    ("backdated_after_an_act_under_the_new_owner", "the node signs x1 under the new owner's acceptance, then x2 "
     "naming the first owner's acceptance and x1 as its previous act: x2 has the re-binding in its past "
     "through x1, so it does not count under the binding the re-binding ended (E4). The ledgers, which read "
     "an act's head alone, count it for the first owner, out of force",
     ["B1", "A1"], [], {"x1": "A1", "x2": "A0"},
     {"x1": {"O1": (F, F), "O2": (T, T)}, "x2": NOBODY}, {"ledgers": {"x2": {"O1": (T, F)}}}),
    # a later bundle version G1, naming G0: the conferral-end rules as they are
    ("later_bundle_act_at_the_later_version", "(a) a grant counted under G0, and G1 exists: an act naming G1 and "
     "the acceptance of that grant, no end held, counts and is in force. No rule reads where a standing "
     "began, so nothing asks for the grant again under G1",
     [], [], {"x1": "A0"}, {"x1": {"O1": (T, T), "O2": (F, F)}}, dict(G1, heads={"x1": "G1"})),
    ("later_bundle_act_at_the_earlier_version", "(b) an act naming G0 held by a reader that acknowledged G1: it "
     "counts at G0 and is in force. Nothing is refused for naming an older version, and the reader's line is "
     "not applied to an authored act",
     [], [], {"x1": "A0"}, {"x1": {"O1": (T, T), "O2": (F, F)}}, dict(G1, acks=["G1"])),
    ("later_bundle_end_at_the_later_version", "(c) the grant's end names G1: an act at G0 and one at G1 both "
     "count (E2) and neither is in force",
     [], ["EG"], {"x1": "A0", "x2": "A0"},
     {"x1": {"O1": (T, F), "O2": (F, F)}, "x2": {"O1": (T, F), "O2": (F, F)}},
     dict(G1, eg="G1", heads={"x2": "G1"})),
    ("later_bundle_end_at_the_later_version_receipted", "(c) the same, and the count holds a receipt of the act "
     "at G0: that act is in force (E8)",
     [], ["EG", "qg"], {"x1": "A0", "x2": "A0"},
     {"x1": {"O1": (T, T), "O2": (F, F)}, "x2": {"O1": (T, F), "O2": (F, F)}},
     dict(G1, eg="G1", heads={"x2": "G1"})),
    ("later_bundle_end_at_the_earlier_version", "(d) the grant's end names G0: the act at G0 counts and is not "
     "in force (E2); the act at G1 finds the grant ended and does not count (E3)",
     [], ["EG"], {"x1": "A0", "x2": "A0"},
     {"x1": {"O1": (T, F), "O2": (F, F)}, "x2": NOBODY}, dict(G1, heads={"x2": "G1"})),
    ("later_bundle_end_at_the_earlier_version_one_say", "(d) the same end, and the count holds a clean receipt "
     "of the act at G1 concurrent with its end: the count has no say on it; it counts at G1 and is not in "
     "force (E3, one say)",
     [], ["EG", "qg"], {"x1": "A0"}, {"x1": {"O1": (T, F), "O2": (F, F)}}, dict(G1, heads={"x1": "G1"})),
    ("later_bundle_end_at_the_earlier_version_reader_at_the_later", "(d) the same end for a reader that "
     "acknowledged G1, which does not have the end in its past: the end is void for that reader (CC 2.7.8 on "
     "the end), and both acts count and are in force",
     [], ["EG"], {"x1": "A0", "x2": "A0"},
     {"x1": {"O1": (T, T), "O2": (F, F)}, "x2": {"O1": (T, T), "O2": (F, F)}},
     dict(G1, heads={"x2": "G1"}, acks=["G1"])),
    ("later_bundle_end_names_a_stale_version", "the grant's end names G0 and has G1 in its own past: it "
     "concludes nothing (E1), and both acts count and are in force",
     [], ["EG"], {"x1": "A0", "x2": "A0"},
     {"x1": {"O1": (T, T), "O2": (F, F)}, "x2": {"O1": (T, T), "O2": (F, F)}},
     dict(G1, heads={"x2": "G1"}, eg_names=["G1"])),
]
# Two owners is none (CC 3.2). Rows written out: G0 the bundle, B0 the binding to O1 and A0 O1's acceptance under it, C0
# a second binding of the node, concurrent with B0 (neither names the other), C1 a re-binding of C0, x1 the act.
def _two(c0_owner="O2", c1=False, x_names=("G0", "A0"), b_names_c=False):
    rows = [{"id": "G0", "kind": "bundle", "signer": "count", "names": []},
            {"id": "C0", "kind": "binding", "signer": "N", "names": [], "owner": c0_owner, "on": None},
            {"id": "B0", "kind": "binding", "signer": "N", "names": ["C0"] if b_names_c else [], "owner": "O1", "on": None},
            {"id": "A0", "kind": "acceptance", "signer": "O1", "names": ["B0"], "on": "B0"}]
    if c1:
        rows.append({"id": "C1", "kind": "binding", "signer": "N", "names": ["C0"], "owner": "O1", "on": "C0"})
    rows.append({"id": "x1", "kind": "act", "signer": "N", "names": list(x_names), "head": "G0", "on": "A0"})
    return rows


# (name, about, rows, {act: {owner: (counted, in_force)}}, {act: reason})
TWO_CASES = [
    ("two_owners", "two concurrent bindings of the node, to O1 and to O2, both live: the node has no owner, and an "
     "act on O1's acceptance counts for nobody", _two(), {"x1": NOBODY}, {"x1": "two_owners"}),
    ("two_owners_act_names_both", "the same, and the act has both bindings in its past: nobody",
     _two(x_names=("G0", "A0", "C0")), {"x1": NOBODY}, {"x1": "two_owners"}),
    ("two_bindings_one_owner", "two concurrent bindings of the node, both to O1: one owner; the act stands under "
     "the binding its acceptance names", _two("O1"), {"x1": {"O1": (T, T), "O2": (F, F)}}, {"x1": "stands"}),
    ("two_owners_one_rebound_in_the_acts_past", "O2's binding is re-bound to O1 (C1 names C0), and the act has "
     "that re-binding in its past: O2's binding is ended there, and the act stands on O1",
     _two(c1=True, x_names=("G0", "A0", "C1")), {"x1": {"O1": (T, T), "O2": (F, F)}}, {"x1": "stands"}),
    ("two_owners_one_in_the_others_past", "O1's binding names O2's in its past but does not re-bind it (no `on`): "
     "both are live, so two owners, none; the act counts for nobody", _two(b_names_c=True), {"x1": NOBODY},
     {"x1": "two_owners"}),
    ("two_owners_rebinding_held_not_in_the_acts_past", "the same re-binding held by the reader, not in the act's "
     "past: O2's binding is not ended in the act's past, so at the act two owners were live; nobody",
     _two(c1=True), {"x1": NOBODY}, {"x1": "two_owners"}),
]
ROW_KIND = {"G": ("bundle", "count"), "B": ("binding", None), "A": ("acceptance", None), "E": ("end", "count"),
            "x": ("act", "N")}
# The one kind of difference between `judge` (a ledger per record, each act placed by its head alone) and
# `chain_answers` (the past the rows name): an act that reaches, through its previous act, the re-binding that
# ended the binding it stands on. By what the rows name it has that end in its past and does not count there
# (E4); the ledger counts it, out of force. Only a backdating node signs such an act.
DIFFERS = "E4.names_end"


def build_rows(names, on, opt=None):
    """Rows in the fixture's form from each row's names. `on`: the row each act stands on."""
    opt = opt or {}
    rows = []
    for i, ns in names.items():
        if i == "qg":
            row = {"id": i, "kind": "receipt", "signer": "count", "names": ns, "on": "x1"}
        elif i == "qb":
            row = {"id": i, "kind": "receipt", "signer": "O1", "names": ns, "on": "x1"}
        else:
            kind, signer = ROW_KIND[i[0]]
            row = {"id": i, "kind": kind, "signer": signer or OWNER[int(i[1])], "names": ns}
            if kind == "binding":
                row["owner"] = OWNER[int(i[1])]
                row["on"] = ns[0] if ns else None
            elif kind == "acceptance":
                row["on"] = ns[0] if ns else None
            elif kind == "act":
                row["head"], row["on"] = opt.get("heads", {}).get(i, "G0"), on[i]
            elif kind == "end":
                row["head"] = opt.get("eg", "G0")
        row["signer"] = opt.get("signers", {}).get(i, row["signer"])
        rows.append(row)
    return rows


def case_rows(chain, extra, named, opt=None):
    """The rows of a case as the fixture lists them, and the set of their ids."""
    opt = opt or {}
    names = {"G0": [], "B0": [], "A0": ["B0"]}
    for g in opt.get("bundles", []):
        names[g] = ["G%d" % (int(g[1]) - 1)]
    for r in chain:
        names[r] = ["B%d" % (int(r[1]) - (r[0] == "B"))]
    prev = None
    for x in sorted(named):
        names[x] = [opt.get("heads", {}).get(x, "G0")] + ([named[x]] if named[x] else []) + ([prev] if prev else [])
        prev = x
    for r in extra:
        names[r] = sorted({opt.get("eg", "G0")} | set(opt.get("eg_names", ()))) if r == "EG" else ["x1"]
    return build_rows(names, named, opt), set(names)


def ledger_answers(named, held, opt=None):
    """The case's answers from the per-record ledgers (`judge`), joined per owner."""
    out = {}
    for x, a in judge("acc", named, held, named=named, opt=opt).items():
        gc, gf = a["grant"]
        out[x] = {o: {"counted": gc and any(c for k, (c, _) in a["stints"].items() if OWNER[k] == o),
                      "in_force": gf and any(f for k, (_, f) in a["stints"].items() if OWNER[k] == o)}
                  for o in ("O1", "O2")}
    return out


def case_answers(case):
    """A case's answers by the rule (`chain_answers`): per act and owner, and why."""
    chain, extra, named = case[2:5]
    opt = case[6] if len(case) > 6 else {}
    rows, _ = case_rows(chain, extra, named, opt)
    ans = chain_answers(rows, reader_acks=opt.get("acks", ()))
    return per_owner(ans), {x: {k: a[k] for k in ("reason", "binding", "grant", "under")} for x, a in ans.items()}


def check_cases():
    """Every case: the rule gives the hand-written answer, and so do the ledgers, but where the case says how
    the ledgers differ (`ledgers`), and there they must give exactly that."""
    problems = []
    for name, _, rows, want, why in TWO_CASES:
        ans = chain_answers(rows)
        got = per_owner(ans)
        exp = {x: {o: {"counted": c, "in_force": f} for o, (c, f) in w.items()} for x, w in want.items()}
        if got != exp or {x: a["reason"] for x, a in ans.items()} != why:
            problems.append("case %s: the rule gives %s, expected %s, %s" % (name, ans, exp, why))
    for case in CASES:
        name, _, chain, extra, named, want = case[:6]
        opt = case[6] if len(case) > 6 else {}
        _, held = case_rows(chain, extra, named, opt)
        exp = {x: {o: {"counted": c, "in_force": f} for o, (c, f) in w.items()} for x, w in want.items()}
        got, _ = case_answers(case)
        if got != exp:
            problems.append("case %s: the rule gives %s, expected %s" % (name, got, exp))
        for x, w in opt.get("ledgers", {}).items():
            for o, (c, f) in w.items():
                exp[x] = dict(exp[x], **{o: {"counted": c, "in_force": f}})
        led = ledger_answers(named, held, opt)
        if led != exp:
            problems.append("case %s: the ledgers give %s, expected %s" % (name, led, exp))
    return problems


def fixture():
    """The case table as a fixture: rows, and for every act and owner whether it counts and is in force."""
    assert not check_cases(), check_cases()
    cases = []
    for case in CASES:
        name, about, chain, extra, named = case[:5]
        opt = case[6] if len(case) > 6 else {}
        rows, _ = case_rows(chain, extra, named, opt)
        answers, why = case_answers(case)
        cases.append({"name": name, "about": about, "rows": rows, "reader_acks": list(opt.get("acks", [])),
                      "answers": answers, "why": why})
    for name, about, rows, _, _ in TWO_CASES:
        ans = chain_answers(rows)
        cases.append({"name": name, "about": about, "rows": rows, "reader_acks": [], "answers": per_owner(ans),
                      "why": {x: {k: a[k] for k in ("reason", "binding", "grant", "under")} for x, a in ans.items()}})
    return {"about": "one row that needs two standings, an owner binding and a root grant (CC 3.1.2.1): "
                     "models/tla/CONFERRAL_END.md section J; generated from "
                     "models/causal_kernel/check_conferral_two.py under its reading `acc`",
            "roles": {"N": "the node", "O1": "the first owner", "O2": "the second owner", "count": "a counted row"},
            "rows": "G0 the bundle in force, G1 a later version naming it; B0, B1, B2 the binding and its "
                    "re-bindings, each naming the one before; A0, A1, A2 the owner's acceptance of the grant, "
                    "naming its binding; EG the count's end of the grant; qg the count's receipt of x1; qb the "
                    "first owner's receipt of x1; an act names its bundle version, the row it stands on if any, "
                    "and its signer's previous act. Beside `names`, a row states what a rule reads of it: an "
                    "act and the end their `head` (the bundle version), an act the row it stands `on`, an "
                    "acceptance the binding it is made `on`, a binding its `owner` and the binding it re-binds "
                    "(`on`), a receipt the act it is `on`",
            "why": "per act: `reason` is `stands` (the act names an acceptance its binding's owner signed; "
                   "`binding` is that binding, `grant` and `under` the conferral-end rules that decide it "
                   "under the grant and under the binding) or why it counts for nobody: `no_acceptance`, "
                   "`names_binding`, `not_an_acceptance`, `acceptance_names_no_binding`, "
                   "`not_the_owners_acceptance`, `two_owners` (a second live binding of the node to another owner, "
                   "concurrent with the one the acceptance names and not re-bound in the act's past)",
            "cases": cases}


def compare_chain(top, has_eg, qg, qb, acts, full, held, ledgers):
    """One state of `acc`: the rule over the held rows against the ledgers. Returns (differences of the kind
    DIFFERS, problems)."""
    on = {x: act_name("acc", *acts[x]) for x in acts if x in held}
    ans = chain_answers(build_rows({i: full[i] for i in sorted(held)}, on))
    same, problems = 0, []
    for x, a in ledgers.items():
        gc, gf = a["grant"]
        for o in ("O1", "O2"):
            lc = gc and any(c for k, (c, _) in a["stints"].items() if OWNER[k] == o)
            lf = gf and any(f for k, (_, f) in a["stints"].items() if OWNER[k] == o)
            r = ans[x]
            rc, rf = r["owner"] == o and r["counted"], r["owner"] == o and r["in_force"]
            if (lc, lf) == (rc, rf):
                continue
            if acts[x][1] is not None and lc and not lf and not rc and r["owner"] == o and r["under"] == DIFFERS:
                same += 1
            else:
                problems.append("%s for %s: ledgers %s, rule %s (%s); the reader holds %s"
                                % (x, o, (lc, lf), (rc, rf), r, sorted(held)))
    return same, problems


def main():
    broke = {r: {} for r in READINGS}
    n_worlds = n_states = n_differ = 0
    chain_problems = []
    for top, has_eg, qg, qb, acts in worlds():
        n_worlds += 1
        for reading in READINGS:
            full = row_names(reading, top, has_eg, qg, qb, acts)
            for held in closed_sets(full):
                n_states += 1
                ledgers = judge(reading, acts, held)
                if reading == "acc":
                    d, ps = compare_chain(top, has_eg, qg, qb, acts, full, held, ledgers)
                    n_differ += d
                    chain_problems += ps
                for x, a in ledgers.items():
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
    problems = check_cases() + chain_problems[:10]
    if not n_differ:
        problems.append("the rule and the ledgers never differ: DIFFERS describes nothing")
    for r in READINGS:
        if set(broke[r]) != EXPECTED[r]:
            problems.append("%s breaks %s, expected %s" % (r, sorted(broke[r]), sorted(EXPECTED[r])))
        for p in sorted(broke[r]):
            print("%-9s breaks %-9s %s" % (r, p, broke[r][p]))
        if not broke[r]:
            print("%-9s holds %s" % (r, ", ".join(PROPS)))
    print("%d cases under acc and %d of two owners; %d true histories, %d (reading, held set) states"
          % (len(CASES), len(TWO_CASES), n_worlds, n_states))
    print("the rule over the held rows against the ledgers, every state of acc: %d answers differ, each a "
          "backdated act with the end of its binding in its past (%s); %d other differences"
          % (n_differ, DIFFERS, len(chain_problems)))
    holds = [r for r in READINGS if not EXPECTED[r]]
    print("RESULT: %s" % ("ok: %s hold all %d properties; the other readings break what is expected of them"
                          % (" and ".join(holds), len(PROPS)) if not problems
                          else "%d problems: %s" % (len(problems), problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
