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
  5  who concludes, with which row, and the late answer, as each door reads them from manifests/reactions.json; what
     the opening row is while its window is open (the `while` entries), and a rewritten while entry that must change
     the halt's state; the quotes of formal/derivation/door_text.tsv, and a changed quote that must be refused; the
     count of parameters no table states; a rewritten land entry that must change the halt's answer; doors.tsv current

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
    keys = {"producer": ("P",), "decider": ("DC",), "subject": ("S",), "pair": ("op", "wa"), "resolve_deferral": ("WA",)}.get(counted, tuple("m%d" % i for i in range(1, NK + 1)))
    target = {"self_roster_evict": "m2", "accord_halt@node": "N", "accord_halt@holder": "N", "accord_halt@node+late_closed": "N", "invitation": "J", "community_invite": "J",
              "takedown_withhold": "H", "retirement_objection": "A", "deletion_sla": "P", "community_remove[unanimous]": "m3",
              "community_remove[majority]": "m3", "community_remove[quorum]": "m3", "moderator_recall": None,
              "accord_halt@node+late_closed": "N", "community_invite-invitee": "J"}.get(name)
    scopes = [x for x in (s["opener"], s["concluder"]) + tuple(s["extra"]) if x not in (counted, "target", "winner")]
    return keys, target, list(dict.fromkeys(scopes))


def setup(name, n=None):
    """The founding row, the seats the door needs, and the head an opener names."""
    s = D.DOORS[name]
    keys, target, scopes = cast(name)
    if n: keys = tuple("m%d" % i for i in range(1, n + 1))
    rows = [ST.offer("g", keys[0], keys, s["counted"], "@", "self", cosigners=keys[1:])]
    if s.get("declared"): rows[0] = dict(rows[0], protocol=s["declared"])          # the group's founding row declares its protocol
    seat_of = {}
    for i, sc in enumerate(scopes):
        k = {"moderate": "MOD", "review": "REV", "takedown": "TK", "substrate": "SUB", "author": "AU", "subject": "S", "decider": "DC", "deferring": "AG"}.get(sc, sc.upper())
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
    if target and (s.get("target_votes") or target_voice_cell(s)): answerers.append(target)
    answerers = list(dict.fromkeys(a for a in answerers if a != op or s["kind"] in ("ranked", "tally") or name == "moderation_action"))
    if s["kind"] in ("ranked", "tally"): answerers.append(keys[0])      # one person with a second ballot
    kinds = BALLOTS if s["kind"] == "ranked" else s["kinds"]
    opts = [None] + [(k, pos) for k in kinds for pos in ("named", "conc")]
    if name == "moderation_action" and NK == 4:          # four members: the split vote only (the moderator silent, every answer named)
        out = []
        for choice in itertools.product([None, ("act", "named"), ("keep", "named")], repeat=len(keys)):
            for sy in ("fallback", "lapsed"):
                out.append({"door": name, "ans": tuple((a, ch[0], ch[1]) for a, ch in zip(keys, choice) if ch), "note": None,
                            "L": (keys[1], sy, True), "op": op, "target": target, "joiners": None})
        return out
    if s["concluder"] == "target": concl = [target, keys[0] if keys[0] != target else keys[1]]
    elif s["concluder"] == "winner": concl = list(keys)
    else:
        pool = keys if s["concluder"] == s["counted"] else (seat_of[s["concluder"]],)
        concl = list(dict.fromkeys([op if op in pool else pool[0], [k for k in pool if k != op][-1] if len(pool) > 1 else pool[0]]))
        if name == "retirement_objection": concl.append(target)          # the agent tries to close its own window
    says = [o for o in s["outcomes"] if o != "open"]
    notes = [None, "named", "conc"] if s.get("silent") else [None]
    out = []
    joiners = [None, "named", "conc"] if name in ("moderation_overturn", "community_invite", "default_standing") else [None]
    ops = [op] + (["X"] if s["kind"] == "seat_act" else [])          # a key outside the seat tries the act
    for choice in itertools.product(opts, repeat=len(answerers)):
      for jn in joiners:
        for note in notes:
            for c in concl:
                for sy in ([x for x in says if x == "winner:" + c] if s["concluder"] == "winner" else says):
                    for el in (False, True):
                        for o in ops:
                            out.append({"door": name, "ans": tuple((a, ch[0], ch[1]) for a, ch in zip(answerers, choice) if ch),
                                        "note": note, "L": (c, sy, el), "op": o, "target": target, "joiners": jn})
    return out


def target_voice_cell(s):
    """The policy row's own target_voice cell, read here apart from door.py (a mutation may make door.py ignore it)."""
    return D.POLICY.get(s["policy"], {}).get("counted", {}).get("target_voice", {}).get("value") == "yes"


# what the opening row is while its window is open, as the text says it (independent of the manifest door.py reads)
TEXT_OPEN = {"accord_halt": ("in_force", "CC 4.2.1.1: it fires on receipt"), "moderation_action": ("pending", "CC 4.5.13: the window governs only the fallback"),
             "harm_report": ("pending", "CC 4.5.13: each node reads the removal from the closed window"),
             "takedown_withhold": ("in_force", "CC 4.5.3: every holder withholds from its own receipt"),
             "invitation": ("pending", "CC 3.1.3.2: the widening is the only door that adds anyone"),
             "self_roster_add": ("pending", "CC 3.3.6.4: an addition is a proposal"),
             "accord_roster_change": ("pending", "CC 4.2.6: until W has closed the named holder remains")}


def text_open(name):
    return TEXT_OPEN.get(name.split("@")[0])


def declared_met(kind, yes, keys, target, floor):
    """The count of a declared protocol (consensus_protocols.tsv, CC 3.3.4) over the keys, apart from door.py."""
    y = set(yes) & set(keys)
    if kind == "unanimous":
        nt = set(keys) - {target}
        return nt <= y and 2 * len(y & nt) > len(keys)
    if kind == "majority": return 2 * len(y) > len(keys) and len(y) >= floor
    if kind.startswith("quorum"): return len(y) >= max(2, floor)
    if kind == "all": return y >= set(keys)
    raise ValueError(kind)


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
        got = RC.winner_no_order([(a, k) for a, k, _ in w["ans"]], ["m1", "m2", "m3"])
        return ("winner:" + got) if got else "open"
    if name.startswith("poll"):
        if not el: return "open"
        yes, voted = poll_count(w)
        if name == "poll": return "carried" if 2 * yes > voted and yes >= 2 else "not_carried"      # CC 4.5.13: of those who voted, two voices
        return "carried" if 3 * yes > 2 * n and yes >= 2 else "not_carried"                          # the rule this instance's opening row states
    if name == "wa_adjudication":
        y = (tally(w, "assent") | {w["op"]}) & set(keys)
        if 2 * len(y) > n: return "landed"                                                            # over the full seated roster
        return "cancelled" if el else "open"
    if s["kind"] == "seat_act":
        return "released" if w["op"] in keys else None                                                  # one row of the seat
    if name == "deferral":
        said = {k for _, k, _ in w["ans"]}
        if len(said) == 1: return next(iter(said))                                                    # the seat's one answer
        return ("escalated" if el else "open") if not said else None
    if name == "moderation_action":
        if tally(w, "answered", {"MOD"}): return "answered"
        if not el: return "open"
        act, keep = tally(w, "act") & set(keys), tally(w, "keep") & set(keys)
        return "fallback" if 2 * len(act) > len(act | keep) and len(act) >= 2 else "lapsed"   # CC 4.5.13: of those who voted, two voices
    return None


def poll_count(w):
    """(ballots for, ballots counted): one ballot a person, and a person whose ballots disagree has none (CC 4.5.13)."""
    keys, _, _ = cast(w["door"])
    by = {}
    for a, k, _ in w["ans"]: by.setdefault(a, set()).add(k)
    one = [next(iter(v)) for a, v in by.items() if len(v) == 1 and a in keys]
    return one.count("for"), len(one)


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
            P.append(("a thief (one key of three) does not evict alone", "window_adversary; CC 3.3.6.4",
                      lambda w, o: None if not (tally(w, "object") >= set(keys) - {w["op"]} or w["note"] or tally(w, "object", {w["target"]}) or tally(w, "approve", {w["target"]}))
                  or 2 * len(tally(w, "approve") | {w["op"]}) > n else o != "landed"))
            P.append(("a lost device (signs nothing) cannot veto", "window_adversary",
                      lambda w, o: None if w["ans"] or w["note"] or not L(w)[2] or L(w)[1] != "landed" else o == "landed"))
        if name == "self_roster_add":
            P.append(("a strict majority of the others objecting is not overridden by a lone landing", "CC 3.3.6.4 cancel",
                      lambda w, o: None if len(tally(w, "object", {"m2", "m3"})) < 2 else o != "landed"))
    if s.get("declared"):
        fl = 2 if name.startswith("community_remove") else 1
        dk = s["declared"].split(":")[0]
        P.append(("acts only when the protocol the founding row declares is met (%s)" % dk, "CC 3.3.4; consensus_protocols.tsv",
                  lambda w, o: None if o not in ("removed", "landed") else declared_met(dk, tally(w, "assent") | {w["op"]}, keys, w["target"], fl)))
        P.append(("the declared count, named by the landing, acts (%s)" % dk, "CC 3.3.4; consensus_protocols.tsv",
                  lambda w, o: None if not declared_met(dk, tally(w, "assent", None, ("named",)) | {w["op"]}, keys, w["target"], fl)
                  or L(w)[1] not in ("removed", "landed") else o == L(w)[1]))
    if name == "community_invite":
        P.append(("the invitee's own yes is the floor's second voice: the proposer and the invitee land it at the close", "CC 4.5.13 target_voice cell",
                  lambda w, o: None if not tally(w, "approve", {w["target"]}, ("named",)) or tally(w, "object") or len(tally(w, "approve")) != 1
                  or w.get("joiners") or L(w)[1:] != ("landed", True) else o == "landed"))
    if s["kind"] == "seat_act":
        P.append(("a key outside the seat opens no seal", "CC 3.4.7 the seal", lambda w, o: None if o != "released" else w["op"] in keys))
        P.append(("the seat's one row opens the seal", "CC 3.4.7 the seal", lambda w, o: None if w["op"] not in keys or L(w)[1] != "released" else o == "released"))
    if name.startswith("community_remove"):
        P.append(("no single key removes a member", "CC 4.5.13; community_remove note",
                  lambda w, o: None if o != "removed" else len(tally(w, "assent") | {w["op"]}) >= 2))
        P.append(("every other member removes (note: 'every other member and a strict majority')", "community_remove note",
                  lambda w, o: None if not (set(keys) - {w["target"]} <= tally(w, "assent", None, ("named",)) | {w["op"]}) or not L(w)[1] == "removed" else o == "removed"))
    if name == "moderation_action":
        P.append(("the fallback carries only on a strict majority of the members who voted, floor two", "CC 4.5.13; the row's note",
                  lambda w, o: None if o != "fallback" else 2 * len(tally(w, "act", set(keys))) > len(tally(w, "act", set(keys)) | tally(w, "keep", set(keys)))
                  and len(tally(w, "act", set(keys))) >= 2))
        P.append(("a present moderator is not overridden", "window_adversary; CC 4.5.13",
                  lambda w, o: None if not tally(w, "answered", {"MOD"}) else o != "fallback"))
        P.append(("the fallback needs the members' count", "window_adversary",
                  lambda w, o: None if o != "fallback" else len(tally(w, "act", set(keys))) >= 2))
        P.append(("the fallback works when the moderator is absent", "window_adversary",
                  lambda w, o: None if tally(w, "answered", {"MOD"}) or len(tally(w, "act", set(keys), ("named",))) < 2 or L(w)[1] != "fallback" or not L(w)[2] or L(w)[0] == "MOD"
                  or 2 * len(tally(w, "act", set(keys))) <= len(tally(w, "act", set(keys)) | tally(w, "keep", set(keys))) else o == "fallback"))
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
        P.append(("one side alone never acts", "CC 7.5.5 / 4.4.3.12", lambda w, o: None if o != "landed" else (tally(w, "assent") | {w["op"]}) >= set(keys)))
        P.append(("both signing acts", "CC 7.5.5 / 4.4.3.12",
                  lambda w, o: None if not (tally(w, "assent", None, ("named",)) | {w["op"]}) >= set(keys) or L(w)[1] != "landed" else o == "landed"))
    if name == "moderator_election":
        P.append(("the winner is the instant-runoff winner over one ballot per person (R1, R8, Election.winner)", "ranked_choice; moderator_election",
                  lambda w, o: None if not o.startswith("winner:") else ref(w) == o))
        P.append(("a tie for weakest seats nobody: an election declares no order (R12, R13, Election.free_tie_seats_nobody)", "CC 4.5.13; ranked_choice",
                  lambda w, o: None if not RC.count(RC.summary(RC.dedupe([(a, k) for a, k, _ in w["ans"]])), ["m1", "m2", "m3"])[2]
                  else not o.startswith("winner:")))
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
        P.append(("a decided row that does not name the agent's objection concludes nothing", "CC 7.5.5",
                  lambda w, o: None if not tally(w, "object", {"A"}) or tally(w, "withdrawn") else o != "proceed"))
        P.append(("a decided row naming the objection closes the window", "CC 7.5.5",
                  lambda w, o: None if not tally(w, "object", {"A"}, ("named",)) or tally(w, "withdrawn") or L(w) != ("DC", "objected", True) else o == "objected"))
        P.append(("only the decider closes the window; the agent signs its objection and no landing", "CC 7.5.5",
                  lambda w, o: None if o in ("open", "none", "contested") else L(w)[0] == "DC"))
    if name.startswith("poll"):
        if name == "poll":
            P.append(("a poll that states no rule carries only on a strict majority of those who voted, floor two voices", "CC 4.5.13; the row's floor cell",
                      lambda w, o: None if o != "carried" else (lambda y, v: 2 * y > v and y >= 2)(*poll_count(w))))
        else:
            P.append(("a poll that states its own rule is counted by it (here more than two thirds of the roster)", "CC 4.5.13",
                      lambda w, o: None if o != "carried" else 3 * poll_count(w)[0] > 2 * n))
        P.append(("one ballot counts for each person, and one voice never carries a poll", "CC 4.5.13",
                  lambda w, o: None if o != "carried" else poll_count(w)[0] >= 2))
        P.append(("a poll nobody votes in carries nothing", "CC 4.5.13", lambda w, o: None if w["ans"] else o != "carried"))
    if name == "wa_adjudication":
        P.append(("a finding lands only on the body's count over the full seated roster, never the live subset", "CC 4.3; CC 3.1.9.4",
                  lambda w, o: None if o != "landed" else 2 * len((tally(w, "assent") | {w["op"]}) & set(keys)) > n))
        P.append(("the body's count lands the finding", "CC 4.3",
                  lambda w, o: None if 2 * len((tally(w, "assent", None, ("named",)) | {w["op"]}) & set(keys)) <= n or L(w)[1] != "landed" else o == "landed"))
    if name == "deferral":
        P.append(("silence never resolves a deferral: no default answers it", "CC 4.3",
                  lambda w, o: None if w["ans"] else o not in ("approved", "rejected")))
        P.append(("the request goes up only at its own end", "CC 4.3", lambda w, o: None if L(w)[2] else o != "escalated"))
        P.append(("an answer of the seat is not overridden by the end", "CC 4.3", lambda w, o: None if not w["ans"] else o != "escalated"))
        P.append(("the seat's answer, named by the landing, resolves the deferral", "CC 4.3",
                  lambda w, o: None if {k for _, k, p in w["ans"]} != {"approved"} or not tally(w, "approved", None, ("named",)) or L(w)[1] != "approved" else o == "approved"))
    if name == "decay_stage":
        P.append(("a stage landing before its window concludes nothing", "CC 4.4.3.26", lambda w, o: None if L(w)[2] else o != "due"))
    if name == "invitation":
        P.append(("an acceptance not held by the close does not admit (the proposal's own end)", "CC 3.1.3.2 (3)",
                  lambda w, o: None if o != "admitted" else not L(w)[2]))
        P.append(("an acceptance held inside the window admits", "CC 3.1.3.2 (3)-(4)",
                  lambda w, o: None if not tally(w, "accept", {"J"}, ("named",)) or L(w)[2] or L(w)[1] != "admitted" else o == "admitted"))
    return P


def force_props(name):
    """What the opening row is while its window is open: (label, source, predicate(w, outcome, state))."""
    t = text_open(name)
    if not t: return []
    want, src = t
    return [("while its window is open the opening row is %s at the node holding it" % want.replace("_", " "), src,
             lambda w, o, st: None if o != "open" else st == want)]


def recount_ok(w, o):
    """Recount.stands_is_table_over_all_not_late against the independent reference."""
    r = ref(w)
    if r is None or o in ("open", "contested", "none"): return None
    return o == r


MUTATION = {
    "default_content": ("no_floor", "silence lands on the proposer alone"),
    "default_standing": ("no_floor", "silence lands on the proposer alone"),
    "community_invite": ("no_floor", "silence lands on the proposer alone"),
    "community_invite-invitee": ("no_floor", "silence lands on the proposer alone"),
    "default_irreversible": ("ignore_irreversible", "an irreversible change lands at once"),
    "self_roster_add": ("void", "the landing voids concurrent answers"),
    "self_roster_evict": ("no_silent", "the target's silence is not read"),
    "community_remove[unanimous]": ("one_voice", "every threshold read as one voice"),
    "community_remove[majority]": ("one_voice", "every threshold read as one voice"),
    "community_remove[quorum]": ("one_voice", "every threshold read as one voice"),
    "moderation_action": ("floor_two_voices", "the floor read as two voices of the roster (the old cell)"),
    "moderation_overturn": ("live_roster", "counted over whoever is seated at the count"),
    "moderator_recall": ("one_voice", "every threshold read as one voice"),
    "accord_halt@holder": ("void", "the landing voids concurrent answers"),
    "accord_halt@node": ("concluder_holder", "a holder lands the node's fuse"),
    "accord_halt@node+late_closed": ("concluder_holder", "a holder lands the node's fuse"),
    "custodian_replace": ("strict_2_2", "2/2 read strictly: 3 of 2, which no pair reaches"),
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
    "poll": ("one_voice", "every threshold read as one voice"),
    "poll[stated]": ("stated_ignored", "the opening row's own rule is not read: the default counts"),
    "wa_adjudication": ("live_subset", "the count is over those who answered, not the full seated roster"),
    "deferral": ("default_answers", "silence at the request's end answers it"),
    "archive_release": ("any_opener", "a key outside the seat opens the seal"),
}
# a second deliberate break for a door whose text states two things
MUTATION2 = {"retirement_objection": ("concluder_target", "the agent closes its own objection window"),
             "moderator_election": ("tie_by_position", "a tie for weakest broken by where an option is listed"),
             "community_invite": ("target_voice_ignored", "the row's target_voice cell not read: the invitee's yes is no voice")}
for _d in ("accord_halt@holder", "accord_halt@node", "accord_halt@node+late_closed", "moderation_action", "harm_report", "takedown_withhold",
           "invitation", "self_roster_add", "accord_roster_change"):
    MUTATION2[_d] = ("force_flipped", "the while cell read the other way: in force for pending, pending for in force")
for _d in ("community_remove[unanimous]", "community_remove[majority]", "community_remove[quorum]", "cosigned_act", "wa_adjudication"):
    MUTATION2[_d] = ("protocol_misread", "the founding row's declared protocol read as another")
DOOR_NAMES = list(MUTATION)
THREE_ONLY = {"moderator_election", "takedown_withhold", "poll[stated]"}   # the largest world sets run at three keys only


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
    FP = force_props(name)
    for w in worlds(name):
        st = None
        try:
            S, o = run(rows_of(w), name)
            if FP: st = D.state(S, "p")
        except K.Tie:
            o = "tie"
        n += 1
        for label, src, pr in FP:
            v = pr(w, o, st)
            if v is None: continue
            checked[label] = checked.get(label, 0) + 1
            if not v:
                fails[label] = fails.get(label, 0) + 1
                wit.setdefault(label, (w, o + " state " + str(st)))
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
    global NK
    name, mut, every = args
    NK = 3                                          # a worker may have run a four-key job before this one
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


def room_of_one(mut=None):
    """CC 4.5.13: a room of one grows by its founder's proposal and the newcomer's yes, two keys and two consents;
    CC 3.1.3.2: admission is never one consent. `mut`: a mutation switched on for the run."""
    out = []
    for name in ("community_invite", "community_invite-invitee"):
        set_mut(mut)
        g = ST.offer("g", "m1", ("m1",), "member", "@", "self")
        p = WN.opener("p", "m1", D.key(name), "g", ("g",), target="J")
        W = D.secs(D.key(name))
        acc = WN.answer("acc", "J", "p", "approve")
        for cname, rows, need in (
            ("the founder proposes J, J accepts, the founder lands at the close", [g, p, acc, WN.receipt("r", "m1", "p", 0), WN.landing("L", "m1", "p", "r", "landed", W, ("acc",))], "landed"),
            ("the founder proposes J, nobody answers, the founder lands at the close", [g, p, WN.receipt("r", "m1", "p", 0), WN.landing("L", "m1", "p", "r", "landed", W)], "not landed")):
            S = CK.concluded(CK.kept(rows), D.rule)
            out.append((name, cname, D.outcome(S, "p"), need))
    set_mut(None)
    return out


def election_of_one(mut=None):
    """CC 4.5.13: 'The floor in a small room is the smaller of two voices and the roster's size, so a room of one elects
    itself by its own ballot.' The admission floor of two voices is not applied to an election."""
    set_mut(mut)
    name = "moderator_election"
    g = ST.offer("g", "m1", ("m1",), "member", "@", "self")
    p = WN.opener("p", "m1", D.key(name), "g", ("g",))
    rows = [g, p, WN.answer("b1", "m1", "p", ("m1", "m2", "m3")), WN.receipt("r", "m1", "p", 0),
            WN.landing("L", "m1", "p", "r", "winner:m1", D.secs(D.key(name)), ("b1",))]
    o = D.outcome(CK.concluded(CK.kept(rows), D.rule), "p")
    set_mut(None)
    return o


def moderation_split():
    """Four members, two act and two keep, the moderator silent; a member lands after the window, stating the fallback
    and then the lapse. CC 4.5.13: 'a strict majority of the members who voted, never fewer than two voices'."""
    out = []
    for name, says in (("moderation_action", "fallback"), ("moderation_action", "lapsed")):
        D.rebuild()
        keys = ("m1", "m2", "m3", "m4")
        g = ST.offer("g", "m1", keys, "duty", "@", "self", cosigners=keys[1:])            # four duty holders (CC 4.5.4)
        md = ST.offer("md", "m1", "MOD", "moderate", "g", "group", ("g",), head=("g",), policy="duty_confer", counted="duty",
                      cosigners=("m2", "m3", "MOD"))                           # three of the four confer, MOD accepting
        p = WN.opener("p", "m1", D.key(name), "g", ("md",))
        ans = [WN.answer("a1", "m1", "p", "act"), WN.answer("a2", "m2", "p", "act"), WN.answer("a3", "m3", "p", "keep"), WN.answer("a4", "m4", "p", "keep")]
        rows = [g, md, p] + ans + [WN.receipt("r", "m2", "p", 0), WN.landing("L", "m2", "p", "r", says, D.secs(D.key(name)), ("a1", "a2", "a3", "a4"))]
        S = CK.concluded(CK.kept(rows), D.rule)
        out.append((name, says, D.outcome(S, "p")))
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
        tv = v.get("target_voice", False)                       # the invitee's own yes, an input of the vector
        p = {"signer": app[0] if app else "x", "target": "J" if tv else None, "id": "p"}
        sp = dict(spec, opener_says=None)
        ans = [{"id": "a" + k, "signer": k, "says": spec["kinds"][0]} for k in app] + [{"id": "o" + k, "signer": k, "says": "object"} for k in obj] \
            + ([{"id": "aJ", "signer": "J", "says": "approve"}] if tv else [])
        b = lambda name: keys if name in ("all", "voted") else (keys - {p["signer"]} if name == "others" else
                                                                 (frozenset({"J"}) if tv and spec.get("target_votes") and name in ("moderate", "extra") else frozenset()))
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
    root = ST.offer("g", "root", ("root",), "duty", "@", "self")              # the lone duty holder confers alone (CC 4.5.4 (iv))
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
def doors_text():
    D.rebuild()
    cols = ["door", "source", "kind", "opener", "answerers", "answer_kinds", "window_secs", "clauses (when value rule over -> outcome)",
            "default_at_close", "late_answer", "target_silent", "concluder", "landing_row", "table_read_by", "open_window", "cells_used",
            "stated_not_run", "not_stated_in_tables"]
    # the landing row of a door whose clock has a `land` entry is that entry's (door.stated); these are the doors with none
    landing = {"wa_adjudication": "the cosigned finding itself", "custodian_replace": "the cosigned row itself",
               "affiliation_member_action": "the cosigned row itself", "accord_majority": "the cosigned row itself", "cosigned_act": "the cosigned row itself",
               "community_remove[unanimous]": "the cosigned removal itself", "community_remove[majority]": "the cosigned removal itself",
               "community_remove[quorum]": "the cosigned removal itself", "moderator_recall": "the cosigned recall itself"}
    out = ["\t".join(cols)]
    for name in DOOR_NAMES:
        s = D.DOORS[name]
        ans = [s["counted"]] + list(s["extra"]) + (["target"] if s.get("target_votes") else [])
        cl = "; ".join("%s %s %s over %s -> %s" % (a, b, "/".join(map(str, c)), d, e) for a, b, c, d, e in s["clauses"])
        out.append("\t".join([name, s["policy"], s["kind"], "one voice seated in '%s'" % s["opener"] + (" (its row is the act)" if s["kind"] == "mirror" else ""),
                              "+".join(ans), ",".join(s["kinds"]) or ("ballot" if s["kind"] == "ranked" else "-"),
                              "none" if s["secs"] is None else str(s["secs"]), cl or "-", s["default"], s.get("late", "counts"),
                              str(s.get("silent")), s["concluder"], s.get("landing_row") or landing.get(name, "none named"), "window.py" if D.to_window(s) else "door.py",
                              s.get("open") or "-",
                              "; ".join("%s=%s" % kv for kv in list(s["cells"].items()) + ([("contrast", s["contrast"])] if s.get("contrast") else [])),
                              " | ".join(s.get("stated_not_run", [])), " | ".join(s["unstated"])]))
    return "\n".join(out) + "\n"


# ---- 5. who concludes, with which row, and the late answer: read from manifests/reactions.json --------------------------
def landing_cells():
    """(door, what the manifest states) for every door that reads a `land` entry; the count of parameters no table
    states over all doors; and a plant: the fuse's entry rewritten to a holder must change the halt's answer."""
    D.rebuild()
    out = []
    for name in DOOR_NAMES:
        s = D.DOORS[name]
        if s.get("landing_from"):
            out.append((name, "concluder, landing row and late answer read from reactions.json",
                        "%s; %s; late %s" % (s["concluder"], s["landing_row"].split(" (run as")[0], s["late"] if "late " in s["cells"]["landing"] else "not stated")))
    unstated = sum(len(D.DOORS[n]["unstated"]) for n in DOOR_NAMES)
    def lone_lapse():
        g = ST.offer("g", "h1", ("h1", "h2", "h3"), "holder", "@", "self", cosigners=("h2", "h3"))
        name = "accord_halt@node+late_closed"
        p = WN.opener("p", "h1", D.key(name), "g", ("g",), target="N")
        rows = [g, p, WN.receipt("r", "h2", "p", 0), WN.landing("L", "h2", "p", "r", "lapsed", D.secs(D.key(name)))]
        return D.outcome(CK.concluded(CK.kept(rows), D.rule), "p")
    opens = [(name, "while its window is open, read from reactions.json", D.DOORS[name]["open"]) for name in DOOR_NAMES if D.DOORS[name].get("open")]
    def held_halt():
        g = ST.offer("g", "h1", ("h1", "h2", "h3"), "holder", "@", "self", cosigners=("h2", "h3"))
        name = "accord_halt@node+late_closed"
        rows = [g, WN.opener("p", "h1", D.key(name), "g", ("g",), target="N"), WN.receipt("r", "N", "p", 0)]
        return D.state(CK.concluded(CK.kept(rows), D.rule), "p")
    s_before = held_halt()
    we = D.while_entry(*D.LANDS["accord_halt"]); wkeep = dict(we)
    we["open"] = "pending"
    D.rebuild()
    s_after = held_halt()
    we.clear(); we.update(wkeep)
    D.rebuild()
    before = lone_lapse()
    e = D.land_entry(*D.LANDS["accord_halt"])
    keep = dict(e)
    e.pop("late", None); e.update(concluder="holder", landing="accord:lifecycle:{kind}")
    D.rebuild()
    after = lone_lapse()
    e.clear(); e.update(keep)
    D.rebuild()
    return out + opens, unstated, (before, after), (s_before, s_after)


def door_text_quotes():
    """Every quote of formal/derivation/door_text.tsv stands in its section; a changed quote is refused."""
    from build_family_model import section_span
    ok = lambda t: bool(section_span(t["cc_ref"])) and t["quote"] in section_span(t["cc_ref"])
    good = sum(ok(t) for t in D.DOOR_TEXT)
    t0 = dict(D.DOOR_TEXT[0], quote=D.DOOR_TEXT[0]["quote"].replace("each node", "the proposer", 1) + " x")
    return good, len(D.DOOR_TEXT), not ok(t0)


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
        res2 = mp.map(door_job, [(d, MUTATION2[d][0], 3) for d in MUTATION2], chunksize=1)
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
            say("      %-6s %s (%s; %d worlds)%s" % ("holds" if not fl else "BREAKS", label, [x[1] for x in props(d) + force_props(d) if x[0] == label][0], r["checked"][label],
                                                  "" if not fl else "; %d break, e.g. %s" % (fl, r["witness"][label])))
            got.append((d, label, "holds" if not fl else "breaks"))
        caught = sum(m["fails"].values()) + m["recount"][1]
        say("      plant: mutation %-18s (%s): %s" % (MUTATION[d][0], MUTATION[d][1], "caught" if caught else "NOT CAUGHT"))
        got.append((d, "plant: mutation " + MUTATION[d][0], "caught" if caught else "not caught"))
        if not caught: uncaught.append(d)
        if d in MUTATION2:
            m2 = merge(r for r in res2 if r["door"] == d)[d]
            caught = sum(m2["fails"].values()) + m2["recount"][1]
            say("      plant: mutation %-18s (%s): %s" % (MUTATION2[d][0], MUTATION2[d][1], "caught" if caught else "NOT CAUGHT"))
            got.append((d, "plant: mutation " + MUTATION2[d][0], "caught" if caught else "not caught"))
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
        if name == "community_invite":
            ok = (o == "landed") == (need == "landed")
            got.append((name, "room of one, two consents (CC 4.5.13, CC 3.1.3.2): " + cname, "holds" if ok else "breaks"))
            if not ok: uncaught.append("room of one")
    o = election_of_one()
    say("   room of one, moderator_election: the member's own ballot, landed by the winner -> %s (CC 4.5.13: winner:m1)" % o)
    got.append(("moderator_election", "room of one: the member's own ballot elects it (the floor is the smaller of two and the roster)", "holds" if o == "winner:m1" else "breaks"))
    if o != "winner:m1": uncaught.append("election of one")
    o2 = election_of_one("election_floor_two")
    say("   plant: room of one, mutation election_floor_two (the admission floor applied to an election): %s" % ("caught" if o2 != "winner:m1" else "NOT CAUGHT"))
    got.append(("moderator_election", "plant: room of one, mutation election_floor_two", "caught" if o2 != "winner:m1" else "not caught"))
    if o2 == "winner:m1": uncaught.append("election_floor_two")
    for mut, why in (("enact_floor_off", "the enact met by the founder alone"), ("target_voice_ignored", "the invitee's yes not read")):
        bad = [c for n, c, o, need in room_of_one(mut) if n == "community_invite" and (o == "landed") != (need == "landed")]
        say("   plant: room of one, mutation %s (%s): %s" % (mut, why, "caught" if bad else "NOT CAUGHT"))
        got.append(("community_invite", "plant: room of one, mutation " + mut, "caught" if bad else "not caught"))
        if not bad: uncaught.append("room of one " + mut)
    for name, says, o in moderation_split():
        say("   moderation, four members, two act and two keep, the moderator silent; a member lands '%s' -> %s (CC 4.5.13: lapsed)" % (says, o))
        got.append((name, "two act and two keep of four: a landing stating %s" % says, o))
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
    say("5. who concludes, with which row, and whether a late answer counts")
    cells, unstated, (before, after), (s_before, s_after) = landing_cells()
    for name, label, v in cells:
        say("   %-30s %s" % (name, v))
        got.append((name, label, v))
    caught = s_before == "in_force" and s_after == "pending"
    say("   plant: the fuse's while entry rewritten to pending; the halt held by its node with no landing: %s -> %s: %s" % (s_before, s_after, "caught" if caught else "NOT CAUGHT"))
    got.append(("accord_halt@node+late_closed", "plant: the fuse's while entry rewritten to pending", "caught" if caught else "not caught"))
    if not caught: uncaught.append("while entry")
    good, total, refused = door_text_quotes()
    say("   door_text.tsv: %d of %d quotes stand in their sections; plant: a changed quote %s" % (good, total, "refused: caught" if refused else "accepted: NOT CAUGHT"))
    got.append(("door_text.tsv", "quotes standing in their sections", "%d of %d" % (good, total)))
    got.append(("door_text.tsv", "plant: a changed quote", "caught" if refused else "not caught"))
    if not refused or good != total: uncaught.append("door_text quote")
    say("   parameters no table states, over all doors: %d (doors.tsv, the last column)" % unstated)
    got.append(("doors.tsv", "parameters no table states", str(unstated)))
    caught = before == "open" and after == "lapsed"
    say("   plant: the fuse's land entry rewritten to a holder; a coerced holder lands the lapse at once: %s -> %s: %s" % (before, after, "caught" if caught else "NOT CAUGHT"))
    got.append(("accord_halt@node+late_closed", "plant: the fuse's land entry rewritten to a holder", "caught" if caught else "not caught"))
    if not caught: uncaught.append("land entry")
    dpath = os.path.join(HERE, "doors.tsv")
    if write: open(dpath, "w", encoding="utf-8").write(doors_text())
    same = os.path.exists(dpath) and open(dpath, encoding="utf-8").read() == doors_text()
    say("   doors.tsv is %s" % ("current" if same else "STALE (run with --write)"))
    got.append(("doors.tsv", "written from the doors as run", "current" if same else "stale"))
    path = os.path.join(HERE, "door_expected.tsv")
    lines = ["instance\tproperty\tverdict"] + ["\t".join(g) for g in got]
    if write:
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
