"""
conferral_end.py: the causal end of a conferral, as recommended for persist v62.0 (models/tla/CONFERRAL_END.md),
as a reference: from a set of rows, for every act, whether it is COUNTED at its own head and whether it is IN
FORCE now, and the rule that decides it. It is the "weakR" reading of models/tla/ConferralEnd.tla (acts name
their head and nothing else new; the end names its head h_e; the ender's side keeps acts in force by receipts,
counted wherever they are held), and tools/conferral_xcheck.py compares it with that spec state by state.

No instant is read. The only order is what rows name. The answer is a function of the held rows, the reader's
own acknowledged heads, and two parameters of the standing: whether another live standing of the grantee
authorises the same acts (`other_standing`), and who may receipt (`who`: "all", or "none" for a root grant where
only the count's own receipts keep anything).

Rows (the kernel's row shape: an `id`, a `kind`, a `signer`, the ids it `names`, and the fields a rule reads):
    head          a roster version, a bundle version, or an owner binding; `names` the heads it extends
    act           an exercised act of the grantee (or of a deputy): `head` the head it names (None: an uncited
                  act, from before this change), `sub` true for a deputy edge, `via` the deputy edge a deputy's
                  act is under
    end           the end of the grantee's standing: `head` (h_e), `lifts` (a count end for a compromise)
    receipt       a clean ack of one act (`of`) by the ender's side
    removal       a removal of key `target`
    accept        the grantee's re-acceptance (a second standing of its own)
    receipter_end the body's end of the receipter's seat
Roles: A the conferrer (for a count: the count), B the grantee, C a deputy, D a single co-holder, R a receipter
the grant names. At most one end per row set.

Rules, in the order they decide (the name a failing test reports):
    key_removed          the act's signer's key is removed by a removal that does not have the act in its past
    no_end               no end is held: counted and in force
    end_void.stale_head  E1: the end names a head older than one in its own past: it concludes nothing
    end_void.key_removed the end's signer's key is removed by a removal that does not have the end in its past
    end_void.line        CC 2.7.8: the reader acknowledged a newer head that does not have the end in its past
    E7.other_standing    another live standing of the grantee authorises the act (a second grant, or the
                         grantee's own re-acceptance after its own withdrawal)
    E4.names_end         the act has the end in its past: not counted
    E3.later_head        the act names a head that has h_e in its past: the standing is ended there
    E3.one_say           ... but the ender holds a clean receipt of it concurrent with the end: counted, not in force
    E8.receipt           counted and in force: a clean receipt of it by the ender's side, without the end in its
                         past, is held (the conferrer; a co-holder or the named receipter unless a count end lifts
                         receipts; the receipter's only before its seat's end; never the act's own signer)
    E2.forward           counted at its own head (at, before or concurrent with h_e, or no head at all), not in force
    E6.upstream          a deputy's act whose deputy edge does not count (or is not in force)
"""

GRANTEE, CONFERRER, CO_HOLDER, RECEIPTER = "B", "A", "D", "R"


def _past(rows):
    by = {r["id"]: r for r in rows}
    memo = {}

    def anc(i):
        if i not in memo:
            memo[i] = set()
            out = set()
            for n in by[i].get("names", ()):
                out.add(n)
                if n in by:
                    out |= anc(n)
            memo[i] = out
        return memo[i]
    return by, anc


def answers(rows, reader_acks=(), other_standing=False, who="all"):
    """{act id: {"counted": bool, "in_force": bool, "rule": str}} over the held `rows`."""
    by, anc = _past(rows)
    kind = lambda k: [r for r in rows if r["kind"] == k]
    ends = kind("end")
    assert len(ends) <= 1, "one end per row set"
    E = ends[0] if ends else None
    removals = kind("removal")

    def key_cut(r):
        return any(m["target"] == r["signer"] and r["id"] not in anc(m["id"]) for m in removals)

    def later(h, he):
        return h is not None and he is not None and he in anc(h)

    def end_void():
        if E is None:
            return "no_end"
        if any(later(by[h]["id"], E["head"]) for h in anc(E["id"]) if h in by and by[h]["kind"] == "head"):
            return "end_void.stale_head"
        if key_cut(E):
            return "end_void.key_removed"
        if any(later(h, E["head"]) and E["id"] not in anc(h) for h in reader_acks if h in by):
            return "end_void.line"
        return None

    void = end_void()
    lifted = E is not None and E.get("lifts", False) and E["signer"] == CONFERRER
    rx = [r["id"] for r in kind("receipter_end")]

    def eligible(q):
        s = q["signer"]
        if s == CONFERRER:
            return True
        if s == CO_HOLDER:
            return who == "all" and not lifted
        if s == RECEIPTER:
            return who == "all" and not lifted and not any(x in anc(q["id"]) for x in rx)
        return False                                    # the grantee, or anyone else

    def receipts(x):
        return [q for q in kind("receipt") if q["of"] == x and not key_cut(q)]

    def kept(x):
        return any(eligible(q) and E["id"] not in anc(q["id"]) for q in receipts(x))

    def say(x):
        return any(q["signer"] == E["signer"] and E["id"] not in anc(q["id"]) and q["id"] not in anc(E["id"])
                   for q in receipts(x))

    def other(x):
        if by[x]["signer"] != GRANTEE:
            return False
        return other_standing or (E["signer"] == GRANTEE and any(a["signer"] == GRANTEE for a in kind("accept")))

    def end_rule(x):
        if void:
            return True, True, void
        if other(x):
            return True, True, "E7.other_standing"
        if E["id"] in anc(x):
            return False, False, "E4.names_end"
        if later(by[x].get("head"), E["head"]):
            return (True, False, "E3.one_say") if say(x) else (False, False, "E3.later_head")
        if kept(x):
            return True, True, "E8.receipt"
        return True, False, "E2.forward"

    memo = {}

    def ans(x):
        if x in memo:
            return memo[x]
        r = by[x]
        if key_cut(r):
            out = (False, False, "key_removed")
        else:
            c, f, rule = end_rule(x)
            if r.get("via"):
                uc, uf, _ = ans(r["via"])
                if (c and not uc) or (c and f and not uf):
                    rule = "E6.upstream"
                c, f = c and uc, c and f and uf
            out = (c, f, rule)
        memo[x] = out
        return out

    return {r["id"]: dict(zip(("counted", "in_force", "rule"), ans(r["id"]))) for r in kind("act")}


# ---- the case table: hand-written expectations, which the reference must meet --------------------------------
def head(i, *names):
    return {"id": i, "kind": "head", "signer": "count", "names": list(names)}


def act(i, h, names=(), signer=GRANTEE, **kw):
    return dict({"id": i, "kind": "act", "signer": signer, "head": h,
                 "names": sorted(set(names) | ({h} if h else set()))}, **kw)


def end(h, signer=CONFERRER, names=(), lifts=False):
    return {"id": "E", "kind": "end", "signer": signer, "head": h, "lifts": lifts,
            "names": sorted(set(names) | {h})}


def receipt(i, of, signer, names=()):
    return {"id": i, "kind": "receipt", "signer": signer, "of": of, "names": sorted(set(names) | {of})}


def removal(i, target, names=()):
    return {"id": i, "kind": "removal", "signer": "count", "target": target, "names": list(names)}


H0, H1, H2 = head("H0"), head("H1", "H0"), head("H2", "H1")
T, F = True, False

# (name, about, rows, params, {act: (counted, in_force, rule)}, arrival orders a node may take them in)
CASES = [
    ("no_end", "no end held: an act counts and is in force",
     [H0, act("b1", "H0")], {}, {"b1": (T, T, "no_end")}),
    ("forward_at_end_head", "an act at h_e itself, concurrent with the end: counted at its head, not in force; "
     "the end never voids an act at its own head",
     [H0, act("b1", "H0"), end("H0")], {}, {"b1": (T, F, "E2.forward")}),
    ("forward_older_head", "an act at a head older than h_e: counted there, not in force",
     [H0, H1, act("b1", "H0"), end("H1")], {}, {"b1": (T, F, "E2.forward")}),
    ("end_saw_act_unreceipted", "the end's signer held the act (it is in the end's past only by what the end "
     "names, and the weak end names no acts): counted, not in force unless receipted",
     [H0, H1, act("b1", "H0"), end("H1")], {}, {"b1": (T, F, "E2.forward")}),
    ("concurrent_later_head", "an act at a head later than h_e, not naming the end: the standing is ended there",
     [H0, H1, act("b1", "H1"), end("H0")], {}, {"b1": (F, F, "E3.later_head")}),
    ("one_say", "the same, but the ender holds a clean receipt of the act concurrent with the end: the ender has "
     "no say on it; counted at its head, never in force (a forward end is never blocked)",
     [H0, H1, act("b1", "H1"), end("H0"), receipt("q1", "b1", CONFERRER)], {}, {"b1": (T, F, "E3.one_say")}),
    ("naming_end", "an act that has the end in its past does not count, whatever head it names",
     [H0, H1, end("H0"), act("b1", "H0", ["E"]), act("b2", "H1", ["E"])], {},
     {"b1": (F, F, "E4.names_end"), "b2": (F, F, "E4.names_end")}),
    ("end_removed_key", "a removal of the ender's key, concurrent with the end: the end changes nothing",
     [H0, H1, act("b1", "H1"), end("H0"), removal("rm", CONFERRER)], {}, {"b1": (T, T, "end_void.key_removed")}),
    ("reaccept_two_devices", "the grantee withdraws its own acceptance on one device and re-accepts on the other: "
     "its re-acceptance authorises its acts (any-standing), whichever acceptance they were made under",
     [H0, H1, end("H0", GRANTEE), {"id": "a2", "kind": "accept", "signer": GRANTEE, "names": []},
      act("b1", "H1"), act("b2", "H1", ["a2"])], {},
     {"b1": (T, T, "E7.other_standing"), "b2": (T, T, "E7.other_standing")}),
    ("tie_any_standing", "a second grant (from another grantor) authorises the same act: the end of the first does "
     "not reach it, even an act that names the end",
     [H0, H1, end("H0"), act("b1", "H1", ["E"]), act("b2", "H0")], {"other_standing": True},
     {"b1": (T, T, "E7.other_standing"), "b2": (T, T, "E7.other_standing")}),
    # persist's six
    ("persist_late_arrival", "an act arriving after the end is held, at a node that never saw it: admitted; the "
     "same answer in every arrival order (counted at its own head, not in force)",
     [H0, H1, end("H1"), act("b1", "H0")], {}, {"b1": (T, F, "E2.forward")},
     [["H0", "H1", "E", "b1"], ["H0", "b1", "H1", "E"]]),
    ("persist_refold_before", "the act before the end is held (re-fold, step 1)",
     [H0, H1, act("b1", "H0")], {}, {"b1": (T, T, "no_end")}),
    ("persist_refold_after", "the same act re-folded after the end (step 2): its count is unchanged",
     [H0, H1, act("b1", "H0"), end("H1")], {}, {"b1": (T, F, "E2.forward")}),
    ("persist_newer_head", "an act naming a head newer than h_e does not count",
     [H0, H1, H2, end("H1"), act("b1", "H2")], {}, {"b1": (F, F, "E3.later_head")}),
    ("persist_behind_node", "an act naming an old head, signed after the end elsewhere by a node that was behind: "
     "counted at its old head, not in force; the reader's line is not applied to authored acts",
     [H0, H1, end("H1"), act("b1", "H0")], {"reader_acks": ["H1"]}, {"b1": (T, F, "E2.forward")}),
    ("persist_root_grant", "a root grant: bundle versions as heads; a rotation (a count end without lifts) at V1; "
     "an attestation at V0 receipted by a co-holder stays in force; one unreceipted does not; one at V2 does "
     "not count",
     [head("V0"), head("V1", "V0"), head("V2", "V1"), end("V1"), act("w1", "V0"), act("w2", "V0"),
      act("w3", "V1"), act("w4", "V2"), receipt("q1", "w1", CO_HOLDER)], {},
     {"w1": (T, T, "E8.receipt"), "w2": (T, F, "E2.forward"), "w3": (T, F, "E2.forward"),
      "w4": (F, F, "E3.later_head")}),
    ("persist_owner_binding", "an owner binding: the binding row is the only head; every act concurrent with the "
     "end counts there, none is in force, one naming the end does not count",
     [head("bind"), end("bind"), act("b1", "bind"), act("b2", "bind", ["E"])], {},
     {"b1": (T, F, "E2.forward"), "b2": (F, F, "E4.names_end")}),
    # receipts
    ("receipt_after_self_end", "a co-holder's receipt keeps an act in force after the grantee resigns",
     [H0, H1, end("H1", GRANTEE), act("b1", "H0"), receipt("q1", "b1", CO_HOLDER)], {},
     {"b1": (T, T, "E8.receipt")}),
    ("receipt_after_rotation", "a co-holder's receipt keeps an act in force after a rotation (a count end without "
     "lifts)", [H0, H1, end("H1"), act("b1", "H0"), receipt("q1", "b1", CO_HOLDER)], {},
     {"b1": (T, T, "E8.receipt")}),
    ("receipt_lifted", "a count end that lifts receipts (a compromise): a co-holder's receipt keeps nothing; the "
     "count's own receipt still keeps",
     [H0, H1, end("H1", lifts=True), act("b1", "H0"), act("b2", "H0"), receipt("q1", "b1", CO_HOLDER),
      receipt("q2", "b2", CONFERRER)], {},
     {"b1": (T, F, "E2.forward"), "b2": (T, T, "E8.receipt")}),
    ("self_end_cannot_lift", "a resignation carrying lifts lifts nothing: a self end cannot lift receipts",
     [H0, H1, end("H1", GRANTEE, lifts=True), act("b1", "H0"), receipt("q1", "b1", CO_HOLDER)], {},
     {"b1": (T, T, "E8.receipt")}),
    ("receipt_after_end", "a receipt that has the end in its past keeps nothing (a bulk receipt after the end "
     "included)", [H0, H1, end("H1"), act("b1", "H0"), receipt("q1", "b1", CONFERRER, ["E"])], {},
     {"b1": (T, F, "E2.forward")}),
    ("receipter_before_and_after", "a receipter the grant names: its receipt made before the body ended its seat "
     "keeps; one made after keeps nothing",
     [H0, H1, act("b1", "H0"), act("b2", "H0"), receipt("q2", "b2", RECEIPTER),
      {"id": "rx", "kind": "receipter_end", "signer": CONFERRER, "names": ["q2"]},
      receipt("q1", "b1", RECEIPTER, ["rx"]), end("H1")], {},
     {"b1": (T, F, "E2.forward"), "b2": (T, T, "E8.receipt")}),
    ("grantee_own_receipt", "the grantee's own receipt keeps nothing",
     [H0, H1, end("H1"), act("b1", "H0"), receipt("q1", "b1", GRANTEE)], {}, {"b1": (T, F, "E2.forward")}),
    ("receipt_by_removed_key", "a co-holder's receipt not in the past of a removal of that co-holder's key keeps "
     "nothing", [H0, H1, end("H1"), act("b1", "H0"), receipt("q1", "b1", CO_HOLDER), removal("rm", CO_HOLDER)],
     {}, {"b1": (T, F, "E2.forward")}),
    ("root_grant_who_none", "(d) under a root grant where only the count's receipts keep: a co-holder's receipt "
     "keeps nothing after a rotation",
     [head("V0"), head("V1", "V0"), end("V1"), act("w1", "V0"), receipt("q1", "w1", CO_HOLDER)], {"who": "none"},
     {"w1": (T, F, "E2.forward")}),
    # acts that name no head. The Constitution's text refuses such a row at the door (`act_names_no_head`), so
    # no store holds one: the fixture marks these cases `refused`, and an adopter's witness for them is the
    # refusal. The answers are what the model concludes if such a row were admitted. (Persist, 2026-11-22: no
    # edition-2 store holds an act under a standing that names no head.)
    ("uncited_act", "an act that names nothing (no head): concurrent with every end, never at a later head: "
     "counted, not in force; the same whether it was signed before or after the end",
     [H0, H1, end("H0"), act("u1", None)], {}, {"u1": (T, F, "E2.forward")}),
    ("uncited_act_receipted", "the same act, receipted by a co-holder: in force",
     [H0, H1, end("H0"), act("u1", None), receipt("q1", "u1", CO_HOLDER)], {}, {"u1": (T, T, "E8.receipt")}),
    ("uncited_act_no_end", "an uncited act with no end held", [H0, act("u1", None)], {}, {"u1": (T, T, "no_end")}),
    ("deputy_receipted_under_edge_out_of_force", "the deputy's act is receipted by the conferrer, and its deputy "
     "edge is counted and not in force: both bits pass down, each to its own, so the act counts and is not in "
     "force (E6); with the edge receipted too, it is in force",
     [H0, end("H0"), act("s1", "H0", sub=True), act("c1", "H0", ["s1"], signer="C", via="s1"),
      receipt("q1", "c1", CONFERRER),
      act("s2", "H0", sub=True), act("c2", "H0", ["s2"], signer="C", via="s2"),
      receipt("q2", "c2", CONFERRER), receipt("q3", "s2", CONFERRER)], {},
     {"s1": (T, F, "E2.forward"), "c1": (T, F, "E6.upstream"),
      "s2": (T, T, "E8.receipt"), "c2": (T, T, "E8.receipt")}),
    # deputies, the end's own validity, the reader's line, a removed grantee
    ("deputy", "a deputy edge at H1 (later than h_e) does not count, so its deputy's act does not either; one at "
     "H0 counts and its deputy's act at H0 counts too, neither in force",
     [H0, H1, end("H0"), act("s1", "H1", sub=True), act("c1", "H0", ["s1"], signer="C", via="s1"),
      act("s2", "H0", sub=True), act("c2", "H0", ["s2"], signer="C", via="s2")], {},
     {"s1": (F, F, "E3.later_head"), "c1": (F, F, "E6.upstream"), "s2": (T, F, "E2.forward"),
      "c2": (T, F, "E2.forward")}),
    ("end_stale_head", "E1: an end naming H0 with H1 in its own past concludes nothing",
     [H0, H1, act("b1", "H1"), end("H0", names=["b1"])], {}, {"b1": (T, T, "end_void.stale_head")}),
    ("end_old_fork_for_reader", "the reader acknowledged H1; an end naming H0, not in H1's past, is void for that "
     "reader (CC 2.7.8 on the end, a counted cut)",
     [H0, H1, end("H0"), act("b1", "H1")], {"reader_acks": ["H1"]}, {"b1": (T, T, "end_void.line")}),
    ("grantee_key_removed", "the grantee resigns and its key is removed; its acts not in the removal's past do not "
     "count", [H0, H1, end("H1", GRANTEE), removal("rm", GRANTEE, ["E"]), act("b1", "H0")], {},
     {"b1": (F, F, "key_removed")}),
]


def orders(rows):
    """Every order the door allows of a small row set (a row after everything it names that is held)."""
    ids = {r["id"] for r in rows}
    by = {r["id"]: r for r in rows}
    out = []

    def go(done, seq):
        if len(seq) == len(rows):
            out.append(list(seq)); return
        for r in rows:
            if r["id"] not in done and all(n in done or n not in ids for n in by[r["id"]]["names"]):
                done.add(r["id"]); seq.append(r["id"]); go(done, seq); seq.pop(); done.discard(r["id"])
    go(set(), [])
    return out


def check_cases():
    """Every case: the reference gives the hand-written answer, in every arrival order (a fold over the prefix
    the door holds gives the same final answer: the answer is a set function). Returns (cases, problems)."""
    problems = []
    for c in CASES:
        name, about, rows, params, want = c[:5]
        params = dict(params)
        got = answers(rows, **params)
        for x, (cnt, frc, rule) in want.items():
            g = got.get(x)
            if g != {"counted": cnt, "in_force": frc, "rule": rule}:
                problems.append("%s: %s expected %s, reference %s" % (name, x, (cnt, frc, rule), g))
        if set(got) != set(want):
            problems.append("%s: acts %s, expectations for %s" % (name, sorted(got), sorted(want)))
        by = {r["id"]: r for r in rows}
        for o in orders(rows)[:200]:
            if answers([by[i] for i in o], **params) != got:
                problems.append("%s: order %s differs" % (name, o))
    return len(CASES), problems


def refused(rows):
    """The refusal the Constitution's text gives one of the case's rows at the door, or None. An act that
    exercises a standing and names no head is refused (`act_names_no_head`, CC 2.4.1.1)."""
    return "act_names_no_head" if any(r["kind"] == "act" and r.get("head") is None for r in rows) else None


def fixture():
    """The fixture: every case with its rows, parameters, arrival orders and every act's answer."""
    _, problems = check_cases()
    assert not problems, problems
    cases = []
    for c in CASES:
        name, about, rows, params, want = c[:5]
        cases.append({"name": name, "about": about, "rows": rows,
                      "reader_acks": list(params.get("reader_acks", [])),
                      "other_standing": params.get("other_standing", False), "who": params.get("who", "all"),
                      "orders": c[5] if len(c) > 5 else [[r["id"] for r in rows]],
                      "refused": refused(rows),
                      "answers": answers(rows, **params)})
    return {"about": "the causal end of a conferral (CC 2.4.1.1, CC 4.5.5) as recommended for persist v62.0: "
                     "models/tla/CONFERRAL_END.md; generated from models/causal_kernel/conferral_end.py",
            "roles": {"A": "the conferrer (for a count, the count)", "B": "the grantee", "C": "a deputy",
                      "D": "a single co-holder", "R": "a receipter the grant names", "count": "a counted row"},
            "refused": "a case's `refused` is null, or the refusal the Constitution's text gives one of its rows at "
                       "the door (`act_names_no_head`: an act that exercises a standing and names no head). A "
                       "store that follows the text never holds such a row, so its witness for the case is the "
                       "refusal; `answers` is then what the model concludes if the row were admitted",
            "rules": __doc__.split("Rules, in the order they decide (the name a failing test reports):")[1].strip(),
            "cases": cases}


def _row_text(r):
    """One row in a compact form for the case table: id:kind:signer, then head=, of=, target=, via=, lifts, names=."""
    bits = ["%s:%s:%s" % (r["id"], r["kind"], r["signer"])]
    if r["kind"] in ("act", "end"):
        bits.append("head=%s" % (r.get("head") or "-"))
    for k in ("of", "target", "via"):
        if r.get(k):
            bits.append("%s=%s" % (k, r[k]))
    if r.get("lifts"):
        bits.append("lifts")
    if r.get("sub"):
        bits.append("deputy_edge")
    if r["names"]:
        bits.append("names=" + ",".join(r["names"]))
    return " ".join(bits)


def table():
    """The case table as TSV, one line per act: what the Constitution vendors as its case table for CC 2.4.1.1.
    Columns: case, act, counted, in_force, rule, refused, params, rows (each row as id:kind:signer head= of=
    names=, joined by ' | '), about."""
    lines = ["# The end of a standing (CC 2.4.1.1, CC 4.5.5): every case of models/causal_kernel/conferral_end.py, one "
             "line per act. counted: counted at its own head; in_force: in force now; refused: the refusal the text "
             "gives one of the case's rows at the door (then the row is never held, and the answer is the model's "
             "if it were), or -. Generated by "
             "tools/kernel_fixtures.py; the same cases as conferral_end.json.",
             "case\tact\tcounted\tin_force\trule\trefused\tparams\trows\tabout"]
    for c in CASES:
        name, about, rows, params, _ = c[:5]
        got = answers(rows, **params)
        ps = ",".join("%s=%s" % (k, v if not isinstance(v, list) else "+".join(v)) for k, v in sorted(params.items())) or "-"
        rt = " | ".join(_row_text(r) for r in rows)
        for x in sorted(got):
            a = got[x]
            lines.append("\t".join([name, x, str(a["counted"]).lower(), str(a["in_force"]).lower(), a["rule"],
                                    refused(rows) or "-", ps, rt, about]))
    return "\n".join(lines) + "\n"
