#!/usr/bin/env python3
"""
check_door.py: every policy row and every clock as ONE door (door.py), re-checked against what its own model or text
claims, over every arrival order of bounded generated worlds, each with a mutation that must be caught.

  0  regression: window.py's three windows put through the door reproduce formal/causal_kernel/window_adversary.tsv
  1  per door: generated worlds (3 counted keys, the extra seats, the target; every choice of answer kind and of
     'named by the landing' / 'concurrent with it' per answerer; every concluder candidate, stated outcome, early or
     full): the recount property against an independent reference, and the door's own properties; order-freeness
     over every arrival order of a sample of worlds; one mutation that must break a property
  2  the halt with the halted node as concluder and with a holder as concluder
  3  the two-path rows' published vectors replayed on the door's table
  4  time: G3 (an act signed before its signer's delegation was withdrawn) under the cut by causal past; the
     invitation's `acceptance asserted_at <= expires_at` against the door's window

python3 -I check_door.py            compares every (instance, property, verdict) with door_expected.tsv; exit 1 on any
                                    difference, any mutation not caught, any order difference outside the plants
python3 -I check_door.py --write    writes door_expected.tsv and doors.tsv (the doors as data)
Three workers, each capped at 2 GiB of address space.
"""
import itertools
import json
import multiprocessing
import os
import random
import resource
import sys
import time

resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import door as D  # noqa: E402

WN, ST, CK, K, R = D.WN, D.ST, D.CK, D.K, D.R
sys.path.insert(0, os.path.join(HERE, "..", "ranked_choice"))
import ranked_choice_model as RC  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
PROCS = 3
NK = 3                      # counted keys in a generated world (the run uses 3 and 4)
DAY = 86400
BALLOTS = (("m1", "m2", "m3"), ("m2", "m1", "m3"), ("m3", "m2", "m1"))


def _limit():
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))


# ---- the cast of a door ------------------------------------------------------------------------------------------
def cast(name):
    s = D.DOORS[name]
    counted = s["counted"]
    keys = {"producer": ("P",), "decider": ("DC",), "subject": ("S",), "pair": ("op", "wa")}.get(counted, tuple("m%d" % i for i in range(1, NK + 1)))
    target = {"self_roster_evict": "m2", "accord_halt@node": "N", "accord_halt@holder": "N", "accord_halt@node+late_closed": "N", "invitation": "J",
              "takedown_withhold": "H", "retirement_objection": "A", "deletion_sla": "P", "community_remove[unanimous]": "m3",
              "community_remove[majority]": "m3", "community_remove[quorum]": "m3", "moderator_recall": None,
              "accord_halt@node+late_closed": "N", "community_invite+invitee": "J"}.get(name)
    scopes = [x for x in (s["opener"], s["concluder"]) + tuple(s["extra"]) if x not in (counted, "target", "winner")]
    return keys, target, list(dict.fromkeys(scopes))


def setup(name, n=None):
    """The founding row, the seats the door needs, and the head an opener names."""
    s = D.DOORS[name]
    keys, target, scopes = cast(name)
    if n: keys = tuple("m%d" % i for i in range(1, n + 1))
    rows = [ST.offer("g", keys[0], keys, s["counted"], "@", "self", cosigners=keys[1:])]
    seat_of = {}
    for i, sc in enumerate(scopes):
        k = {"moderate": "MOD", "review": "REV", "takedown": "TK", "substrate": "SUB", "author": "AU", "subject": "S", "decider": "DC"}.get(sc, sc.upper())
        if k in keys: seat_of[sc] = k; continue
        rows.append(ST.offer("s%d" % i, keys[0], k, sc, "g", "self", (rows[-1]["id"],), cosigners=(k,)))
        seat_of[sc] = k
    return rows, keys, target, seat_of


def opener_key(name, keys, seat_of):
    s = D.DOORS[name]
    return seat_of.get(s["opener"], keys[0])


# ---- generated worlds --------------------------------------------------------------------------------------------
def worlds(name):
    s = D.DOORS[name]
    base, keys, target, seat_of = setup(name)
    op = opener_key(name, keys, seat_of)
    p = WN.opener("p", op, D.key(name), "g", (base[-1]["id"],), target=target)
    answerers = [k for k in keys if s["kind"] != "ranked" or True]
    answerers += [seat_of[x] for x in s["extra"]]
    if s.get("target_votes") and target: answerers.append(target)
    answerers = list(dict.fromkeys(a for a in answerers if a != op or s["kind"] == "ranked" or name.startswith("moderation_action")))
    if s["kind"] == "ranked": answerers.append(keys[0])                 # one person with a second ballot
    kinds = BALLOTS if s["kind"] == "ranked" else s["kinds"]
    opts = [None] + [(k, pos) for k in kinds for pos in ("named", "conc")]
    if s["concluder"] == "target": concl = [target, keys[0] if keys[0] != target else keys[1]]
    elif s["concluder"] == "winner": concl = list(keys)
    else:
        pool = keys if s["concluder"] == s["counted"] else (seat_of[s["concluder"]],)
        concl = list(dict.fromkeys([op if op in pool else pool[0], [k for k in pool if k != op][-1] if len(pool) > 1 else pool[0]]))
    says = [o for o in s["outcomes"] if o != "open"]
    notes = [None, "named", "conc"] if s.get("silent") else [None]
    out = []
    joiners = [None, "named", "conc"] if name in ("moderation_overturn", "community_invite", "default_standing") else [None]
    for choice in itertools.product(opts, repeat=len(answerers)):
      for jn in joiners:
        for note in notes:
            for c in concl:
                for sy in ([x for x in says if x == "winner:" + c] if s["concluder"] == "winner" else says):
                    for el in (False, True):
                        out.append({"door": name, "ans": tuple((a, ch[0], ch[1]) for a, ch in zip(answerers, choice) if ch),
                                    "note": note, "L": (c, sy, el), "op": op, "target": target, "joiners": jn})
    return out


def rows_of(w):
    name = w["door"]
    s = D.DOORS[name]
    base, keys, target, seat_of = setup(name)
    p = WN.opener("p", w["op"], D.key(name), "g", (base[-1]["id"],), target=target)
    rows = base + [p]
    named = []
    for i, (a, kind, pos) in enumerate(w["ans"]):
        rows.append(WN.answer("a%d" % i, a, "p", kind))
        if pos == "named": named.append("a%d" % i)
    if w.get("joiners"):                  # two keys seated after the opener, both answering with the opener's own side's opposite
        rows += [ST.offer("oj", keys[0], ("j1", "j2"), s["counted"], "g", "self", ("p",)), ST.accept("aj1", "j1", "oj"), ST.accept("aj2", "j2", "oj")]
        kind = {"two_path": "approve"}.get(s["kind"], s["kinds"][0] if s["kinds"] else "x")
        for j in ("j1", "j2"):
            rows.append(WN.answer("ans_" + j, j, "p", kind, ("aj1", "aj2")))
            if w["joiners"] == "named": named.append("ans_" + j)
    if w["note"]:
        rows.append(R("n1", "note", target, ("g",)))
        if w["note"] == "named": named.append("n1")
    c, sy, el = w["L"]
    W = s.get("secs_rows") or D.secs(D.key(name))
    rows.append(WN.receipt("r", c, "p", 0))
    rows.append(WN.landing("L", c, "p", "r", sy, (W if W < D.NEVER else 1) if el else (W - 1 if W < D.NEVER else 0), tuple(named)))
    return rows


def run(rows, name):
    S = CK.concluded(CK.kept(rows), D.rule)
    return S, D.outcome(S, "p")


# ---- independent references and the doors' own properties ----------------------------------------------------------
def tally(w, kind, who=None, pos=("named", "conc")):
    return {a for a, k, ps in w["ans"] if k == kind and ps in pos and (who is None or a in who)}


def ref(w):
    """The outcome the door's own model or text gives over every answer that does not name the landing, at the
    landing's elapsed; independent of door.py's clause machinery. None where the reference does not apply."""
    name, (c, sy, el) = w["door"], w["L"]
    s = D.DOORS[name]
    keys, target, _ = cast(name)
    n = len(keys)
    if s["kind"] == "two_path":
        import build_governance_policy as BG
        if w["target"] and any(x[0] == w["target"] for x in w["ans"]): return None     # decide() has no target voice
        f = dict(D.POLICY[s["policy"]]); f["_enact"] = (f["enact_rule"].get("num", 1), f["enact_rule"].get("den", 2))
        cr, fr = f["cancel_rule"], f["floor_rule"]
        f["_cancel"] = (cr["num"], cr["den"]) if cr["kind"] == "fraction" else None
        f["_floor"] = (fr["num"], fr["den"]) if fr["kind"] == "fraction" else ((0, 1) if fr["kind"] == "one_of_n" else None)
        if w["note"] or cr["kind"] == "strict_majority_of_others": return None
        app = len(tally(w, "approve") | {w["op"]}) if not tally(w, "object", {w["op"]}) else len(tally(w, "approve"))
        v, _, _ = BG.decide(f, n, app, len(tally(w, "object")), D.secs(D.key(name)) if el else 0)
        return {"lands": "landed", "pending": "open", "cancelled": "cancelled"}[v]
    if name.startswith("accord_halt"):
        conf = tally(w, "confirm", None, ("named",) if (name.endswith("late_closed") and el) else ("named", "conc")) | {w["op"]}
        if 2 * len(conf & set(keys)) > n and not (name.endswith("late_closed") and el): return "confirmed"
        return "lapsed" if el else "open"
    if name == "moderation_overturn":
        o = tally(w, "object") & set(keys)
        if 2 * len(o) > n and len(o) >= 2: return "lifted"
        return "stands" if el else "open"
    if name == "moderator_recall":
        y = (tally(w, "assent") | {w["op"]}) & set(keys)
        if 3 * len(y) > 2 * n and len(y) >= 2: return "recalled"
        return "cancelled" if el else "open"
    if name in ("custodian_replace", "affiliation_member_action"):
        return "landed" if (tally(w, "assent") | {w["op"]}) >= set(keys) else "open"
    if name == "moderator_election":
        if not el: return "open"
        got = RC.winner([(a, k) for a, k, _ in w["ans"]], ["m1", "m2", "m3"])
        return ("winner:" + got) if got else "open"
    if name.startswith("moderation_action"):
        if tally(w, "answered", {"MOD"}): return "answered"
        if not el: return "open"
        act, keep = tally(w, "act") & set(keys), tally(w, "keep") & set(keys)
        if name.endswith("+voted"): return "fallback" if 2 * len(act) > len(act | keep) and len(act) >= 2 else "lapsed"
        return "fallback" if len(act) >= 2 else "lapsed"                      # the cell: two voices
    return None


def props(name):
    """The properties each door's own model, README or text claims: (label, source, predicate(w, outcome) -> None|bool)."""
    s = D.DOORS[name]
    keys, target, _ = cast(name)
    n = len(keys)
    L = lambda w: w["L"]
    P = []
    if s["kind"] == "two_path":
        mc = D.MIN_COUNT.get(D.POLICY[s["policy"]]["corridor"], 2)
        P.append(("the floor never lands early", "two_path Prop_FloorNeverLandsEarly",
                  lambda w, o: None if o != "landed" or L(w)[2] else 3 * len(tally(w, "approve") | {w["op"]}) > 2 * n or s["policy"].startswith("self")))
        if mc == 2:
            P.append(("no single vote admits by silence", "two_path floor; CC 4.5.13",
                      lambda w, o: None if o != "landed" else len(tally(w, "approve") | {w["op"]}) >= 2))
        P.append(("a cancelling minority at the close is not overridden", "two_path Cancel",
                  lambda w, o: None if not D.POLICY[s["policy"]]["cancel_rule"]["kind"] == "fraction" or len(tally(w, "object", set(keys))) < max(mc, -(-n // 3))
                  or 3 * len(tally(w, "approve") | {w["op"]}) > 2 * n else o != "landed"))
        if D.POLICY[s["policy"]]["irreversible"]:
            P.append(("an irreversible change never lands before its window", "two_path Irreversible",
                      lambda w, o: None if o != "landed" else L(w)[2]))
        if name == "self_roster_evict":
            P.append(("a thief (one key of three) does not evict alone", "window_adversary; CC 3.3.6.3",
                      lambda w, o: None if not (tally(w, "object") >= set(keys) - {w["op"]} or w["note"] or tally(w, "object", {w["target"]}) or tally(w, "approve", {w["target"]}))
                  or 2 * len(tally(w, "approve") | {w["op"]}) > n else o != "landed"))
            P.append(("a lost device (signs nothing) cannot veto", "window_adversary",
                      lambda w, o: None if w["ans"] or w["note"] or not L(w)[2] or L(w)[1] != "landed" else o == "landed"))
        if name == "self_roster_add":
            P.append(("a strict majority of the others objecting is not overridden by a lone landing", "CC 3.3.6.3 cancel",
                      lambda w, o: None if len(tally(w, "object", {"m2", "m3"})) < 2 else o != "landed"))
    if name.startswith("community_remove"):
        P.append(("no single key removes a member", "CC 4.5.13; community_remove note",
                  lambda w, o: None if o != "removed" else len(tally(w, "assent") | {w["op"]}) >= 2))
        P.append(("every other member removes (note: 'every other member and a strict majority')", "community_remove note",
                  lambda w, o: None if not (set(keys) - {w["target"]} <= tally(w, "assent", None, ("named",)) | {w["op"]}) or not L(w)[1] == "removed" else o == "removed"))
    if name.startswith("moderation_action"):
        P.append(("the fallback carries only on a strict majority of the members who voted, floor two", "CC 4.5.13; the row's note",
                  lambda w, o: None if o != "fallback" else 2 * len(tally(w, "act", set(keys))) > len(tally(w, "act", set(keys)) | tally(w, "keep", set(keys)))
                  and len(tally(w, "act", set(keys))) >= 2))
        P.append(("a present moderator is not overridden", "window_adversary; CC 4.5.13",
                  lambda w, o: None if not tally(w, "answered", {"MOD"}) else o != "fallback"))
        P.append(("the fallback needs the members' count", "window_adversary",
                  lambda w, o: None if o != "fallback" else len(tally(w, "act", set(keys))) >= 2))
        P.append(("the fallback works when the moderator is absent", "window_adversary",
                  lambda w, o: None if tally(w, "answered", {"MOD"}) or len(tally(w, "act", set(keys), ("named",))) < 2 or L(w)[1] != "fallback" or not L(w)[2] or L(w)[0] == "MOD" else o == "fallback"))
    if name == "moderation_overturn":
        P.append(("Inv_SeatedMajority: a lift is carried by a strict majority seated at the act", "moderation_lift",
                  lambda w, o: None if o != "lifted" else 2 * len(tally(w, "object", set(keys))) > n))
        P.append(("Inv_TwoVoices: never one voice", "moderation_lift", lambda w, o: None if o != "lifted" else len(tally(w, "object")) >= 2))
        P.append(("Inv_StandsAfterWindow: an act not lifted stands", "moderation_lift",
                  lambda w, o: None if len(tally(w, "object")) >= 2 or not L(w)[2] or L(w)[1] != "stands" else o == "stands"))
    if name == "moderator_recall":
        P.append(("recall needs more than two thirds and two voices", "CC 4.5.13 moderator_recall",
                  lambda w, o: None if o != "recalled" else 3 * len(tally(w, "assent") | {w["op"]}) > 2 * n))
    if name.startswith("accord_halt"):
        P.append(("one holder cannot keep agents stopped alone", "window_adversary; AccordHaltFuse Inv_LoneBounded",
                  lambda w, o: None if o != "confirmed" else 2 * len((tally(w, "confirm") | {w["op"]}) & set(keys)) > n))
        P.append(("one holder cannot lift a confirmed halt alone", "window_adversary; Prop_ConfirmedPersists",
                  lambda w, o: None if 2 * len((tally(w, "confirm") | {w["op"]}) & set(keys)) <= n else o != "lapsed"))
        P.append(("no key but the halted node ends its lone halt before a majority (Inv_ResumeNeedsHonest, Inv_LoneBounded per node)",
                  "AccordHaltFuse; wave1 windows finding",
                  lambda w, o: None if o != "lapsed" else L(w)[0] == w["target"]))
    if name in ("custodian_replace", "affiliation_member_action"):
        P.append(("one side alone never acts", "CC 7.5.5 / 4.4.3.2.8", lambda w, o: None if o != "landed" else (tally(w, "assent") | {w["op"]}) >= set(keys)))
        P.append(("both signing acts", "CC 7.5.5 / 4.4.3.2.8",
                  lambda w, o: None if not (tally(w, "assent", None, ("named",)) | {w["op"]}) >= set(keys) or L(w)[1] != "landed" else o == "landed"))
    if name == "moderator_election":
        P.append(("the winner is the instant-runoff winner over one ballot per person (R1, R8, Election.winner)", "ranked_choice; moderator_election",
                  lambda w, o: None if not o.startswith("winner:") else ref(w) == o))
        P.append(("below the floor of two voices nobody is seated (R7, no_ballots_no_winner)", "ranked_choice",
                  lambda w, o: None if len({a for a, _, _ in w["ans"]}) >= 2 else not o.startswith("winner:")))
    if name in ("cosigned_act", "accord_majority"):
        P.append(("lands only when the protocol's count is met", "CC 3.3.4 / 4.2.1.3",
                  lambda w, o: None if o != "landed" else 2 * len(tally(w, "assent") | {w["op"]}) > n))
    if name == "deletion_sla":
        P.append(("a breach whose past or recount holds the producer's deletion does not stand", "CC 3.3.1 D1-D2",
                  lambda w, o: None if not tally(w, "deleted") else o != "breached"))
    if name == "accord_roster_change":
        P.append(("a change carries only on a strict majority of the standing roster; a presumed-dead holder's yes is counted", "CC 4.2.6",
                  lambda w, o: None if o != "landed" else 2 * len(tally(w, "yes") | {w["op"]}) > n))
    if name == "harm_report":
        P.append(("a moderator's keep is not overridden", "CC 4.5.13", lambda w, o: None if not tally(w, "keep", {"MOD"}) else o != "removed"))
    if name == "takedown_withhold":
        P.append(("only the holding device lands its own destruction", "CC 4.5.3 (custody:ack)", lambda w, o: None if o != "destroy" else L(w)[0] == "H"))
        P.append(("a reversal or a lift is not overridden", "CC 4.5.3", lambda w, o: None if not (tally(w, "reversed", {"REV"}) or 2 * len(tally(w, "lift", set(keys))) > n and len(tally(w, "lift", set(keys))) >= 2) else o != "destroy"))
    if name == "retirement_objection":
        P.append(("the agent's objection holds the ladder", "CC 7.5.5", lambda w, o: None if not tally(w, "object", {"A"}) or tally(w, "withdrawn") else o != "proceed"))
    if name == "decay_stage":
        P.append(("a stage landing before its window concludes nothing", "CC 4.4.3.5.1", lambda w, o: None if L(w)[2] else o != "due"))
    if name == "invitation":
        P.append(("an acceptance not held by the close does not admit (the proposal's own end)", "CC 3.1.3.2 (3)",
                  lambda w, o: None if o != "admitted" else not L(w)[2]))
        P.append(("an acceptance held inside the window admits", "CC 3.1.3.2 (3)-(4)",
                  lambda w, o: None if not tally(w, "accept", {"J"}, ("named",)) or L(w)[2] or L(w)[1] != "admitted" else o == "admitted"))
    return P


def recount_ok(w, o):
    """Recount.stands_is_table_over_all_not_late against the independent reference."""
    r = ref(w)
    if r is None or o in ("open", "contested", "none"): return None
    return o == r


MUTATION = {
    "default_content": ("no_floor", "silence lands on the proposer alone"),
    "default_standing": ("no_floor", "silence lands on the proposer alone"),
    "community_invite": ("no_floor", "silence lands on the proposer alone"),
    "community_invite+invitee": ("no_floor", "silence lands on the proposer alone"),
    "default_irreversible": ("ignore_irreversible", "an irreversible change lands at once"),
    "self_roster_add": ("void", "the landing voids concurrent answers"),
    "self_roster_evict": ("no_silent", "the target's silence is not read"),
    "community_remove[unanimous]": ("one_voice", "every threshold read as one voice"),
    "community_remove[majority]": ("one_voice", "every threshold read as one voice"),
    "community_remove[quorum]": ("one_voice", "every threshold read as one voice"),
    "moderation_action": ("void", "the landing voids concurrent answers"),
    "moderation_action+voted": ("void", "the landing voids concurrent answers"),
    "moderation_overturn": ("live_roster", "counted over whoever is seated at the count"),
    "moderator_recall": ("one_voice", "every threshold read as one voice"),
    "accord_halt@holder": ("void", "the landing voids concurrent answers"),
    "accord_halt@node": ("concluder_holder", "a holder lands the node's fuse"),
    "accord_halt@node+late_closed": ("concluder_holder", "a holder lands the node's fuse"),
    "custodian_replace": ("strict_2_2", "2/2 read strictly, as the build's vectors read it (3 of 2)"),
    "affiliation_member_action": ("one_voice", "every threshold read as one voice"),
    "moderator_election": ("dedupe_off", "a person's ballots all count; first choices only"),
    "cosigned_act": ("one_voice", "every threshold read as one voice"),
    "accord_majority": ("one_voice", "every threshold read as one voice"),
    "deletion_sla": ("void", "the landing voids concurrent answers"),
    "accord_roster_change": ("one_voice", "every threshold read as one voice"),
    "harm_report": ("void", "the landing voids concurrent answers"),
    "takedown_withhold": ("concluder_holder", "a member lands another holder's destruction"),
    "retirement_objection": ("void", "the landing voids concurrent answers"),
    "decay_stage": ("zero_window", "the window has no length"),
    "invitation": ("late_counts", "an acceptance after the close still admits"),
}
DOOR_NAMES = list(MUTATION)
THREE_ONLY = {"moderator_election", "takedown_withhold", "moderation_action", "moderation_action+voted"}   # the largest world sets run at three keys only


def set_mut(m):
    D.MUT.clear()
    if m: D.MUT.add(m)
    if m == "one_voice":
        pass
    D.rebuild()
    if m == "late_counts": D.DOORS["invitation"]["late"] = "counts"
    if m == "zero_window": D.DOORS["decay_stage"]["secs_rows"] = D.DOORS["decay_stage"]["secs"]; D.DOORS["decay_stage"]["secs"] = 1




def door_job(args):
    global NK
    name, mut, NK = args if len(args) == 3 else args + (3,)
    set_mut(mut)
    fails, checked, rc_n, rc_bad, wit, recwit, n = {}, {}, 0, 0, {}, None, 0
    P = props(name)
    for w in worlds(name):
        try:
            S, o = run(rows_of(w), name)
        except K.Tie:
            o = "tie"
        n += 1
        ok = recount_ok(w, o)
        if ok is not None:
            rc_n += 1
            if not ok:
                rc_bad += 1
                recwit = recwit or (w, o, ref(w))
        for label, src, pr in P:
            v = pr(w, o)
            if v is None: continue
            checked[label] = checked.get(label, 0) + 1
            if not v:
                fails[label] = fails.get(label, 0) + 1
                wit.setdefault(label, (w, o))
    return {"door": name, "mut": mut, "nk": NK, "worlds": n, "checked": checked, "fails": fails, "witness": {k: _fmt(*v) for k, v in wit.items()},
            "recount": (rc_n, rc_bad, _fmt(*recwit[:2]) + " ref=" + str(recwit[2]) if recwit else "")}


def _fmt(w, o):
    a = ", ".join("%s %s %s" % x for x in w["ans"]) or "no answers"
    return "opener %s; answers: %s; target note: %s; landing by %s says %s %s -> %s" % (
        w["op"], a, w["note"], w["L"][0], w["L"][1], "after the window" if w["L"][2] else "early", o)


def order_job(args):
    """Every arrival order of a sample of worlds (all orders up to 8 rows; 600 sampled orders above)."""
    name, mut, every = args
    set_mut(mut)
    ws = worlds(name)
    if mut == "by_arrival": ws = [w for w in ws if any(x[2] == "conc" for x in w["ans"])]      # the plant needs a concurrent answer
    ws = ([w for w in ws if len(w["ans"]) >= 2 and w["L"][2]] or [w for w in ws if w["L"][2]])[::every][:12] or ws[:12]      # the richer worlds, at most twelve
    rnd = random.Random(11)
    sets = orders = differ = 0
    for w in ws:
        rows = rows_of(w)
        memo = {}
        def rule(r, Pp, past):
            key = (r["id"], frozenset(q["id"] for q in Pp))
            if key not in memo: memo[key] = D.rule(r, Pp, past)
            return memo[key]
        Sref = CK.concluded(CK.kept(rows), rule)
        want = (frozenset(Sref.C.items()), D.outcome(Sref, "p", by_arrival=(mut == "by_arrival")))
        perms = itertools.permutations(rows) if len(rows) <= 7 else (rnd.sample(rows, len(rows)) for _ in range(1500))
        seen = {}
        sets += 1
        for order in perms:
            S = CK.arrive(order, rule)
            key = tuple(r["id"] for r in S.rows)
            if key not in seen:
                seen[key] = (frozenset(S.C.items()), D.outcome(S, "p", by_arrival=(mut == "by_arrival")))
            orders += 1
            differ += seen[key] != want
    return {"door": name, "mut": mut, "sets": sets, "orders": orders, "differ": differ}


# ---- 0. regression -----------------------------------------------------------------------------------------------
def regression():
    D.rebuild()
    rows_out, bad = [], 0
    ref_tsv = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "window_adversary.tsv"), encoding="utf-8")][1:]
    i = 0
    for world in WN.WORLDS:
        title, cases = world()
        for cname, rows, prop, need in cases:
            S = CK.concluded(CK.kept(rows), D.rule)
            o = {h: WN.outcome(S, "p", h) for h in WN.RULES}
            landed = bool([r["id"] for r in K.sel(S.rows, kind="landing") if S.C[r["id"]]])
            want = ref_tsv[i]
            got = [title, cname, str(landed), o["void"], o["contest"], o["recount"]]
            bad += got != want[:6]
            i += 1
    return i, bad


# ---- 2. the halt's two concluders ----------------------------------------------------------------------------------
def halt_compare():
    out = []
    for name in ("accord_halt@holder", "accord_halt@node"):
        D.rebuild()
        g = ST.offer("g", "h1", ("h1", "h2", "h3"), "holder", "@", "self", cosigners=("h2", "h3"))
        W = D.secs(D.key(name))
        p = WN.opener("p", "h1", D.key(name), "g", ("g",), target="N")
        c2 = WN.answer("c2", "h2", "p", "confirm")
        cases = [
            ("a coerced holder h2 lands 'lapsed' at once, stating a full fuse on its own clock (no confirm)",
             [g, p, WN.receipt("r", "h2", "p", 0), WN.landing("L", "h2", "p", "r", "lapsed", W)], "the halt stays until the node's own fuse", "not lapsed"),
            ("the node N lands 'lapsed' at its own fuse; nobody confirmed",
             [g, p, WN.receipt("r", "N", "p", 0), WN.landing("L", "N", "p", "r", "lapsed", W)], "a lone halt lapses at the fuse", "lapsed"),
            ("an honest holder h3 lands 'lapsed' at its own fuse; nobody confirmed",
             [g, p, WN.receipt("r", "h3", "p", 0), WN.landing("L", "h3", "p", "r", "lapsed", W)], "(who may end the lone halt)", None),
            ("N lands 'lapsed' while h2's confirm (a strict majority with the firer) is concurrent with it",
             [g, p, c2, WN.receipt("r", "N", "p", 0), WN.landing("L", "N", "p", "r", "lapsed", W)], "one key cannot lift a confirmed halt alone", "not lapsed"),
            ("h3 lands 'lapsed' while h2's confirm is concurrent with it",
             [g, p, c2, WN.receipt("r", "h3", "p", 0), WN.landing("L", "h3", "p", "r", "lapsed", W)], "one key cannot lift a confirmed halt alone", "not lapsed"),
            ("N lands 'lapsed' early (its own clock lies): the node releases itself",
             [g, p, WN.receipt("r", "N", "p", 0), WN.landing("L", "N", "p", "r", "lapsed", W)], "(conceded: only its own agents)", None),
            ("h2 confirms and N lands 'confirmed' naming it",
             [g, p, c2, WN.receipt("r", "N", "p", 0), WN.landing("L", "N", "p", "r", "confirmed", 0, ("c2",))], "a majority confirms", "confirmed"),
            ("h1 (the firer) lands 'confirmed' alone",
             [g, p, WN.receipt("r", "h1", "p", 0), WN.landing("L", "h1", "p", "r", "confirmed", W)], "one holder cannot keep agents stopped alone", "not confirmed"),
        ]
        for cname, rows, prop, need in cases:
            S = CK.concluded(CK.kept(rows), D.rule)
            o = D.outcome(S, "p")
            holds = None if need is None else ((o != need[4:]) if need.startswith("not ") else (o == need))
            # how many readers see it: under the holder rule the landing is any reader's; under the node rule only N's fuse
            out.append((name, cname, o, prop, holds))
    return out


def room_of_one():
    out = []
    for name in ("community_invite", "community_invite+invitee"):
        D.rebuild()
        g = ST.offer("g", "m1", ("m1",), "member", "@", "self")
        p = WN.opener("p", "m1", D.key(name), "g", ("g",), target="J")
        W = D.secs(D.key(name))
        acc = WN.answer("acc", "J", "p", "approve")
        for cname, rows, need in (
            ("the founder proposes J, J accepts, the founder lands at the close", [g, p, acc, WN.receipt("r", "m1", "p", 0), WN.landing("L", "m1", "p", "r", "landed", W, ("acc",))], "landed"),
            ("the founder proposes J, nobody answers, the founder lands at the close", [g, p, WN.receipt("r", "m1", "p", 0), WN.landing("L", "m1", "p", "r", "landed", W)], "not landed")):
            S = CK.concluded(CK.kept(rows), D.rule)
            out.append((name, cname, D.outcome(S, "p"), need))
    return out


def moderation_split():
    """Four members, two act and two keep, the moderator silent; a member lands the fallback after the window.
    CC 4.5.13: 'a strict majority of the members who voted, never fewer than two voices' -> not carried."""
    out = []
    for name in ("moderation_action", "moderation_action+voted"):
        D.rebuild()
        keys = ("m1", "m2", "m3", "m4")
        g = ST.offer("g", "m1", keys, "member", "@", "self", cosigners=keys[1:])
        md = ST.offer("md", "m1", "MOD", "moderate", "g", "self", ("g",), cosigners=("MOD",))
        p = WN.opener("p", "m1", D.key(name), "g", ("md",))
        ans = [WN.answer("a1", "m1", "p", "act"), WN.answer("a2", "m2", "p", "act"), WN.answer("a3", "m3", "p", "keep"), WN.answer("a4", "m4", "p", "keep")]
        rows = [g, md, p] + ans + [WN.receipt("r", "m2", "p", 0), WN.landing("L", "m2", "p", "r", "fallback", D.secs(D.key(name)), ("a1", "a2", "a3", "a4"))]
        S = CK.concluded(CK.kept(rows), D.rule)
        out.append((name, D.outcome(S, "p")))
    return out


# ---- 3. vectors -----------------------------------------------------------------------------------------------------
def vectors():
    """Replay manifests/governance_policy_vectors.json on the door's table (counts, no rows: the base runs to 344)."""
    D.rebuild()
    V = json.load(open(os.path.join(HERE, "..", "..", "manifests", "governance_policy_vectors.json"), encoding="utf-8"))["vectors"]
    n = bad = 0
    wit = []
    for v in V:
        fam = v["family"]
        spec = D.DOORS[fam]
        base = v["base"]
        keys = frozenset("k%d" % i for i in range(base))
        app = ["k%d" % i for i in range(v["approvals"])]
        obj = ["k%d" % i for i in range(v["approvals"], v["approvals"] + v["objections"])]
        p = {"signer": app[0] if app else "x", "target": None, "id": "p"}
        sp = dict(spec, opener_says=None)
        ans = [{"id": "a" + k, "signer": k, "says": spec["kinds"][0]} for k in app] + [{"id": "o" + k, "signer": k, "says": "object"} for k in obj]
        b = lambda name: keys if name in ("all", "voted") else (keys - {p["signer"]} if name == "others" else frozenset())
        got = D.table_outcome(sp, p, ans, [], b, v["elapsed_secs"] >= spec["secs"])
        want = {"lands": "landed", "pending": "open", "cancelled": "cancelled"}[v["verdict"]]
        n += 1
        if got != want:
            bad += 1
            if len(wit) < 3: wit.append((fam, base, v["approvals"], v["objections"], v["elapsed_secs"], want, got))
    return n, bad, wit


# ---- 4. time ---------------------------------------------------------------------------------------------------------
def time_g3():
    """witnesses.tsv G3: del = trust:moderate root->mod; act by mod; xdel = withdraw of del by root. Under the cut by
    causal past the act counts iff the withdrawal has it in its past, in every arrival order; under the freshness
    reading (signed instant against first held, W) the answer follows arrival."""
    root = ST.offer("g", "root", ("root",), "member", "@", "self")
    dl = ST.offer("del", "root", "mod", "moderate", "g", "self", ("g",), cosigners=("mod",))
    act = R("act", "act", "mod", ("del",), head=("del",), at=50)
    xdel_unseen = ST.withdraw("xdel", "root", "del", ("del",))
    xdel_seen = ST.withdraw("xdel", "root", "del", ("del", "act"))
    out = []
    def counts(rows, order):
        def rule(r, P, past):
            if r["kind"] == "act": return r["signer"] in ST.members_at(P, past, "g", r["head"], "moderate")
            return ST.seat_rule(r, P, past)
        S = CK.arrive(order, rule)
        if not S.C.get("act"): return False
        ended = [w for w in K.sel(S.Cs, kind="withdraw") if w["target"] == "del"]
        return all("act" in S.anc[w["id"]] for w in ended)                         # KERNEL 8a: the ended-seat rule
    def fresh(order, W=100, signed={"act": 50, "xdel": 60}):
        held = []
        for r in order:
            held.append(r["id"])
            if r["id"] == "act":
                return "xdel" not in held or signed["act"] < signed["xdel"]          # judged at receipt; signed instant within W
        return False
    for label, x in (("withdrawal that never saw the act", xdel_unseen), ("withdrawal naming the act", xdel_seen)):
        rows = [root, dl, act, x]
        res_cut = {counts(rows, list(o)) for o in itertools.permutations(rows)}
        res_fresh = {fresh(list(o)) for o in itertools.permutations(rows)}
        out.append((label, sorted(res_cut), sorted(res_fresh)))
    return out


def time_invitation():
    """The invitation: CC 3.1.3.2 (3) admits an acceptance whose asserted_at <= the proposal's expires_at (two signers'
    instants). Under the door the proposal opens a window of its own stated length, the widening is the landing, and
    the concluder's own two instants close it."""
    D.rebuild()
    name = "invitation"
    base, keys, target, seat_of = setup(name)
    p = WN.opener("p", "m1", D.key(name), "g", ("g",), target="J")
    W = D.secs(D.key(name))
    acc = lambda names=(): WN.answer("acc", "J", "p", "accept", names)
    cases = [
        ("J accepts; m2 holds it inside the window and lands 'admitted'", [*base, p, acc(), WN.receipt("r", "m2", "p", 0), WN.landing("L", "m2", "p", "r", "admitted", W - 1, ("acc",))], "admitted"),
        ("J accepts late with a back-dated asserted_at; m2 first holds it after its window and lands 'admitted'", [*base, p, acc(), WN.receipt("r", "m2", "p", 0), WN.landing("L", "m2", "p", "r", "admitted", W, ("acc",))], "not admitted"),
        ("m2 lands 'closed' at its window; J's acceptance is concurrent (back-dated)", [*base, p, WN.receipt("r", "m2", "p", 0), WN.landing("L", "m2", "p", "r", "closed", W), acc()], "closed"),
        ("m2 lands 'closed' early (lies), J's acceptance concurrent", [*base, p, WN.receipt("r", "m2", "p", 0), WN.landing("L", "m2", "p", "r", "closed", W - 1), acc()], "(early close concludes nothing)"),
        ("m2 lands 'closed' at its window; m3 holds the acceptance inside its own window and lands 'admitted' naming both", [*base, p, acc(), WN.receipt("r", "m2", "p", 0), WN.landing("L", "m2", "p", "r", "closed", W), WN.receipt("r3", "m3", "p", 0), WN.landing("L3", "m3", "p", "r3", "admitted", 1, ("L", "acc"))], "admitted"),
    ]
    out = []
    for cname, rows, need in cases:
        S = CK.concluded(CK.kept(rows), D.rule)
        o = D.outcome(S, "p")
        cross = {"admitted" if 10 <= 20 else "closed"}          # the cross-signer rule: J's asserted_at (back-dated 10) <= expires_at (20): admits whenever J says so
        out.append((cname, o, need))
    return out


# ---- doors.tsv -------------------------------------------------------------------------------------------------------
def write_doors():
    D.rebuild()
    cols = ["door", "source", "kind", "opener", "answerers", "answer_kinds", "window_secs", "clauses (when value rule over -> outcome)",
            "default_at_close", "late_answer", "target_silent", "concluder", "landing_row", "table_read_by", "cells_used", "not_stated_in_tables"]
    landing = {"accord_halt@node": "objection:landed (NEW), self scope, by the halted node", "accord_halt@holder": "objection:landed (NEW) by a holder",
               "moderator_election": "ballot:moderator_acceptance (exists)", "deletion_sla": "hard_case:deletion_window_breach (exists)",
               "takedown_withhold": "custody:ack none (exists)", "retirement_objection": "retirement:frozen (exists)", "decay_stage": "consent:decay:<stage> (exists)",
               "invitation": "membership:widening (exists)", "custodian_replace": "the cosigned row itself", "affiliation_member_action": "the cosigned row itself",
               "accord_majority": "the cosigned row itself", "cosigned_act": "the cosigned row itself; the close is a local drop",
               "community_remove[unanimous]": "the cosigned removal itself; the close is a local drop",
               "community_remove[majority]": "the cosigned removal itself; the close is a local drop",
               "community_remove[quorum]": "the cosigned removal itself; the close is a local drop", "moderator_recall": "the cosigned recall itself; the close is a local drop"}
    with open(os.path.join(HERE, "doors.tsv"), "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for name in DOOR_NAMES:
            s = D.DOORS[name]
            ans = [s["counted"]] + list(s["extra"]) + (["target"] if s.get("target_votes") else [])
            cl = "; ".join("%s %s %s over %s -> %s" % (a, b, "/".join(map(str, c)), d, e) for a, b, c, d, e in s["clauses"])
            f.write("\t".join([name, s["policy"], s["kind"], "one voice seated in '%s'" % s["opener"] + (" (its row is the act)" if s["kind"] == "mirror" else ""),
                               "+".join(ans), ",".join(s["kinds"]) or ("ballot" if s["kind"] == "ranked" else "-"),
                               "none" if s["secs"] is None else str(s["secs"]), cl or "-", s["default"], s.get("late", "counts"),
                               str(s.get("silent")), s["concluder"], landing.get(name, "objection:landed (NEW) or none named"), "window.py" if D.to_window(s) else "door.py",
                               "; ".join("%s=%s" % kv for kv in s["cells"].items()), " | ".join(s["unstated"])]) + "\n")


def main():
    t0 = time.time()
    write = "--write" in sys.argv
    say = lambda s: print(s, flush=True)
    got = []                                        # (instance, property, verdict)
    n, bad = regression()
    say("0. regression: window.py's three windows judged by the door's rule: %d cases, %d differ from window_adversary.tsv" % (n, bad))
    got.append(("window.py", "window_adversary.tsv reproduced", "same" if bad == 0 else "differs"))
    with multiprocessing.Pool(PROCS, initializer=_limit) as mp:
        jobs = [(d, m, nk) for m in (None, "mut") for nk in (3, 4) for d in DOOR_NAMES if nk == 3 or d not in THREE_ONLY]
        res = mp.map(door_job, [(d, MUTATION[d][0] if m else None, nk) for d, m, nk in jobs], chunksize=1)
        ordr = mp.map(order_job, [(d, None, 7) for d in DOOR_NAMES] + [(PLANT_DOOR, "by_arrival", 7) for PLANT_DOOR in ("self_roster_evict", "moderation_action")], chunksize=1)
    say("1. per door (worlds generated; every property checked on each; recount against the independent reference)")
    def merge(rs):
        out = {}
        for r in rs:
            o = out.setdefault(r["door"], {"worlds": 0, "checked": {}, "fails": {}, "witness": {}, "recount": [0, 0, ""]})
            o["worlds"] += r["worlds"]
            for k, v in r["checked"].items(): o["checked"][k] = o["checked"].get(k, 0) + v
            for k, v in r["fails"].items(): o["fails"][k] = o["fails"].get(k, 0) + v
            for k, v in r["witness"].items(): o["witness"].setdefault(k, "[%d keys] %s" % (r["nk"], v))
            o["recount"][0] += r["recount"][0]; o["recount"][1] += r["recount"][1]; o["recount"][2] = o["recount"][2] or r["recount"][2]
        return out
    plain = merge(r for r in res if r["mut"] is None)
    muts = merge(r for r in res if r["mut"] is not None)
    uncaught = []
    for d in DOOR_NAMES:
        r, m = plain[d], muts[d]
        rc = r["recount"]
        say("  %-30s %6d worlds; recount against the reference: %s" % (d, r["worlds"], "%d checked, %d differ %s" % (rc[0], rc[1], rc[2]) if rc[0] else "no independent reference"))
        if rc[0]: got.append((d, "recount agrees with the reference", "holds" if rc[1] == 0 else "breaks"))
        for label in sorted(r["checked"]):
            fl = r["fails"].get(label, 0)
            say("      %-6s %s (%s; %d worlds)%s" % ("holds" if not fl else "BREAKS", label, [x[1] for x in props(d) if x[0] == label][0], r["checked"][label],
                                                  "" if not fl else "; %d break, e.g. %s" % (fl, r["witness"][label])))
            got.append((d, label, "holds" if not fl else "breaks"))
        caught = sum(m["fails"].values()) + m["recount"][1]
        say("      plant: mutation %-18s (%s): %s" % (MUTATION[d][0], MUTATION[d][1], "caught" if caught else "NOT CAUGHT"))
        got.append((d, "plant: mutation " + MUTATION[d][0], "caught" if caught else "not caught"))
        if not caught: uncaught.append(d)
    say("   order-freeness (at most 12 worlds a door; every arrival order up to 7 rows, 1500 sampled above):")
    order_bad = []
    for o in ordr:
        plant = o["mut"] is not None
        say("      %-30s %-22s %4d sets %8d orders %d differ" % (o["door"], "plant: by_arrival" if plant else "", o["sets"], o["orders"], o["differ"]))
        v = ("caught" if o["differ"] else "not caught") if plant else ("same" if o["differ"] == 0 else "differs")
        got.append((o["door"], "plant: by_arrival order" if plant else "one answer in every arrival order", v))
        if (plant and not o["differ"]) or (not plant and o["differ"]): order_bad.append(o["door"])
    say("2. the halt: the halted node as concluder, and a holder")
    for name, cname, o, prop, holds in halt_compare():
        say("   %-20s %-100s -> %-10s %s%s" % (name, cname, o, prop, "" if holds is None else ": " + ("holds" if holds else "breaks")))
        got.append((name, "halt case: " + cname, o))
    for name, cname, o, need in room_of_one():
        say("   room of one, %-26s %-70s -> %s (needs %s)" % (name, cname, o, need))
        got.append((name, "room of one: " + cname, o))
    for name, o in moderation_split():
        say("   moderation, four members, two act and two keep, a member lands the fallback: %-26s -> %s (CC 4.5.13 needs lapsed)" % (name, o))
        got.append((name, "two act and two keep of four: the fallback", o))
    n, bad, wit = vectors()
    say("3. governance_policy_vectors.json replayed on the door's table: %d vectors, %d differ %s" % (n, bad, wit))
    got.append(("two-path rows", "%d published vectors replayed" % n, "same" if bad == 0 else "differs"))
    say("4. time")
    for label, cut, fresh in time_g3():
        say("   G3, %s: the act counts under the cut by causal past: %s over all 24 orders; under first-held + W: %s" % (label, cut, fresh))
        got.append(("time G3", label, "cut %s; first-held %s" % (cut, fresh)))
    for cname, o, need in time_invitation():
        say("   invitation: %-112s -> %s (needs %s)" % (cname, o, need))
        got.append(("time invitation", cname, o))
    path = os.path.join(HERE, "door_expected.tsv")
    lines = ["instance\tproperty\tverdict"] + ["\t".join(g) for g in got]
    if write:
        write_doors()
        open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        say("wrote door_expected.tsv (%d verdicts) and doors.tsv" % len(got))
        diff = []
    else:
        want = open(path, encoding="utf-8").read().rstrip("\n").split("\n") if os.path.exists(path) else []
        diff = sorted(set(want) ^ set(lines))
        for l in diff: say("   differs from door_expected.tsv: %s %s" % ("expected" if l in want else "now", l))
    ok = not diff and not uncaught and not order_bad
    say("RESULT: %s in %.0fs%s" % ("ok" if ok else "NOT OK", time.time() - t0,
        "" if ok else " (%d verdicts differ; mutations not caught: %s; order: %s)" % (len(diff), uncaught or "none", order_bad or "none")))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
