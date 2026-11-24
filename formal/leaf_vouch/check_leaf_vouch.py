#!/usr/bin/env python3
"""
check_leaf_vouch.py: one command, exit 0 or 1.

    python3 -I formal/leaf_vouch/check_leaf_vouch.py            every case, compared with leaf_vouch_expected.tsv
    python3 -I formal/leaf_vouch/check_leaf_vouch.py --traces   the same, and the steps that reach each witness
    python3 -I formal/leaf_vouch/check_leaf_vouch.py --write-expected

Three parts, each an enumeration over a stated bound. Nothing here is a proof.

  1  the door            every presentation of a fixed set of rows, at every group, identity, key and instant
  2  the life of a leaf  every interleaving, up to the horizon, of one honest device, the other members, and one
                         thief who copies a leaf key (and the device's node key) out of memory once
  3  padding             what a room's door sees of how many rooms a row covers

Every property is run again under PLANTS, each a changed rule or a changed device, and the run fails unless the
property named for the plant is the one that breaks. A property whose premise no case reaches fails the run.
"""
import os
import sys
import resource
import multiprocessing
from collections import Counter, deque
from functools import lru_cache
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import leaf_vouch as LV  # noqa: E402

SUITE, TERM = LV.SUITE, LV.TERM
# written out here a second time, so that a changed constant in leaf_vouch.py fails the run
COUNTS = (1, 8, 32)
MEMBER_KINDS = ("person", "agent", "room")
EXPECTED = os.path.join(HERE, "leaf_vouch_expected.tsv")

# the bound of part 2
H = 5            # ticks 0..H; the cap is TERM = 2 ticks, so the horizon is two terms and a tick
MAXROWS = 3      # vouching rows the honest device signs
MAXWD = 1        # withdrawn rows in play at one time
MAXSHORT = 1     # rows in play with a term shorter than the cap (TERM // 2), where the device signs such rows

PROPS = {
    "TERM": "P1  a lifted leaf key is accepted nowhere from one term after the lift",
    "RENEW": "P2  a lifted leaf key installs no leaf but itself under a vouch that existed at the lift",
    "ROOM": "P3  a vouch for one room is accepted in no group of another, call groups included",
    "ONE": "P4  a presentation that discloses no entry, or two, is refused",
    "LAPSED": "P5  a lapsed leaf's signature is accepted on nothing but the Update that replaces it",
    "REJOIN": "P6  a device back after its vouch ended replaces its leaf by its own Update",
    "NODE": "P7  a node key never vouches",
    "SOUND": "S1  the door accepts a leaf only where the member's device key signed for it",
    "COMPLETE": "S2  the door refuses no leaf the member's device key signed for, well presented",
    "CALLS": "S3  the room's vouch is taken in the room's chat group and in its call groups",
    "WITHDRAWN": "S4  a withdrawn vouch admits nothing from the step it is withdrawn",
    "POSSESS": "S5  a leaf enters only signed by the leaf key it carries",
    "DIGESTS": "S6  a row of other than 1, 8 or 32 digests is refused",
    "SUITE": "S7  an entry for another suite is refused",
    "REMOVE": "S8  only a leaf that lapsed is removed as lapsed",
    "PADDING": "S9  a room's door learns the count of the device's rooms only as 1, up to 8, or up to 32",
}


class Res:
    def __init__(self):
        self.viol = {}          # property -> [count, first detail, first state]
        self.premise = Counter()
        self.witness = {}       # name -> (detail, state)
        self.refusals = Counter()
        self.n = Counter()

    def v(self, prop, detail, state=None):
        if prop not in self.viol:
            self.viol[prop] = [0, detail, state]
        self.viol[prop][0] += 1

    def w(self, name, detail="", state=None, step=None):
        """state: the state the witness is seen in, or, with `step`, the state the step is taken from"""
        if name not in self.witness:
            self.witness[name] = (detail, state, step)


def rule_with(**kw):
    r = dict(LV.RULE)
    r.update(kw)
    return r


# ====================================================================================================== part 1
def e(key, room, suite=SUITE):
    return (key, room, suite)


SW = LV.World(
    seats={"A": {"P": "dP", "G": "aG", "O": "dO", "Z": "nZ",    # Z: a roster that seats a node key (it should not)
                 "X": "xX"},                                     # X: a roster that seats a key of no member kind
           "B": {"P": "dP", "T": "dT"},
           "C": {"S": "rS", "P": "rPC"}},                         # C is a private room: its seats are room keys
    kind={"dP": "person", "dO": "person", "dT": "person", "aG": "agent", "rS": "room", "rPC": "room",
          "nP": "node", "nZ": "node", "nT": "node", "xX": "other"},
    owner={"nP": "P", "nT": "T"})

SG = [LV.Group("A.chat", LV.gid_chat("A"), "A", SUITE, None),
      LV.Group("A.call", LV.gid_call("A", 1), "A", SUITE, None),
      LV.Group("A.random", LV.gid_random(1), "A", SUITE, "A"),   # a call of room A under an id nobody can recompute
      LV.Group("B.chat", LV.gid_chat("B"), "B", SUITE, None),
      LV.Group("B.call", LV.gid_call("B", 1), "B", SUITE, None),
      LV.Group("B.random", LV.gid_random(2), "B", SUITE, "A"),   # a call of room B said to be of room A
      LV.Group("C.chat", LV.gid_chat("C"), "C", SUITE, None),
      LV.Group("C.call", LV.gid_call("C", 1), "C", SUITE, None)]
SGN = {g.name: g for g in SG}


def static_rows():
    two = [e("kPA", "A"), e("kPB", "B")]
    mk = LV.make_row
    return [
        mk("P8", "dP", two, 8, 0, TERM),
        mk("P1", "dP", [e("kP1", "A")], 1, 0, TERM),
        mk("P32", "dP", two, 32, 0, TERM),
        mk("Pshort", "dP", [e("kPh", "A")], 1, 0, TERM // 2),
        mk("P2raw", "dP", two, 2, 0, TERM),                       # not padded
        mk("P33", "dP", two, 33, 0, TERM),
        mk("Plong", "dP", [e("kPl", "A")], 1, 0, TERM + 1),
        mk("Pnoend", "dP", [e("kPn", "A")], 1, 0, None),
        mk("Psuite", "dP", [e("kPs", "A", LV.OTHER_SUITE)], 1, 0, TERM),
        mk("Pwithdrawn", "dP", [e("kPw", "A")], 1, 0, TERM, withdrawn=True),
        mk("Pbadsig", "dP", [e("tF", "A")], 1, 0, TERM, sig_ok=False),
        mk("G1", "aG", [e("kG", "A")], 1, 0, TERM),               # an agent's key
        mk("S1", "rS", [e("kS", "C")], 1, 0, TERM),               # a room key
        mk("PC1", "rPC", [e("kPC", "C")], 1, 0, TERM),            # P's room key in C
        mk("PinC", "dP", [e("kPx", "C")], 1, 0, TERM),            # P's roster key, for the private room
        mk("N1", "nP", [e("kN", "A")], 1, 0, TERM),               # P's node key, owner-bound to P
        mk("Z1", "nZ", [e("kZ", "A")], 1, 0, TERM),               # a node key a roster seats
        mk("X1", "xX", [e("kX", "A")], 1, 0, TERM),               # a seated key that is no person's, agent's or room key
        mk("TB", "dT", [e("kT", "B")], 1, 0, TERM),
        mk("TA", "dT", [e("tF", "A")], 1, 0, TERM),
        mk("L1", "kPA", [e("tF", "A")], 1, 0, TERM),              # a leaf key vouching the next leaf
    ]


STATIC_NOW = tuple(sorted({-1, 0, TERM // 2, TERM - 1, TERM, TERM + 1}))
STATIC_IDENTS = ("P", "G", "O", "S", "T", "Z", "X")


def static_run(rule):
    res = Res()
    rows = static_rows()
    for row in rows:
        ds = LV.disclosures_of(row)
        named = sorted({d[0][0] for d in ds} | {"tF"})
        for g in SG:
            opts = [()] + [(d,) for d in ds] + [c for c in combinations(ds, 2)]
            opts.append(((e("tF", g.room), "fabricated"),))
            for discl in opts:
                for key in named:
                    for ln in (key, "another-key"):
                        for ident in STATIC_IDENTS:
                            for now in STATIC_NOW:
                                static_case(rule, res, row, g, discl, key, ln, ident, now)
    return res


def static_case(rule, res, row, g, discl, key, ln, ident, now):
    res.n["presentations"] += 1
    r = LV.door_leaf(rule, SW, g, ident, key, ln, row, discl, now)
    it = LV.intended(SW, g, ident, key, row, now)
    well = (len(discl) == 1 and LV.digest(discl[0]) in row.digests and discl[0][0] == (key, g.room, g.suite)
            and ln == key)
    is_call = g.gid[0] == "derived" and g.gid[2] == "call"
    detail = "%s at %s as %s: key %s, row %s by %s, %d disclosed, now %d" % (
        "accepted" if r is None else "refused (%s)" % r, g.name, ident, key, row.rid, row.signer, len(discl), now)
    # premises: counted whatever the door says
    if it and ln == key and len(discl) == 0:
        res.premise["ONE.none_disclosed"] += 1
    if it and ln == key and len(discl) == 2:
        res.premise["ONE.two_disclosed"] += 1
    if g.room != "A" and ln == key and len(discl) == 1 and discl[0][0][1] == "A" \
            and LV.intended(SW, SGN["A.chat"], ident, key, row, now):
        res.premise["ROOM.good_in_A_presented_at_" + g.name] += 1
    if SW.kind_of(row.signer) == "node":
        res.premise["NODE.node_signed"] += 1
    if SW.kind_of(row.signer) not in MEMBER_KINDS + ("node", "leaf"):
        res.premise["SOUND.signed_by_a_seated_key_of_no_member_kind"] += 1
    if it and well:
        res.premise["COMPLETE.signed_and_well_presented"] += 1
        if is_call:
            res.premise["CALLS.at_a_call_group"] += 1
    if len(row.digests) not in COUNTS:
        res.premise["DIGESTS.other_count"] += 1
    if any(d[0][2] != g.suite for d in discl):
        res.premise["SUITE.other_suite_disclosed"] += 1
    if row.withdrawn:
        res.premise["WITHDRAWN.static"] += 1
    if ln != key:
        res.premise["POSSESS.not_signed_by_its_key"] += 1
    if r is not None:
        res.refusals[r] += 1
        if it and well:
            res.v("COMPLETE", detail)
            if is_call:
                res.v("CALLS", detail)
        return
    res.n["accepted"] += 1
    res.premise["SOUND.leaf_accepted"] += 1
    res.w("accepted_under_a_%s_key" % SW.kind_of(row.signer), detail)
    if is_call:
        res.w("accepted_at_a_call_group", detail)
    if len(row.digests) in COUNTS:
        res.w("accepted_with_%d_digests" % len(row.digests), detail)
    if row.end is not None and row.end - row.start < TERM:
        res.w("accepted_with_a_shorter_term", detail)
    if not it:
        res.v("SOUND", detail)
    if len(discl) != 1:
        res.v("ONE", detail)
    if not any(x[0] == key and x[1] == g.room for x in LV.entries_of(row)) or any(d[0][1] != g.room for d in discl):
        res.v("ROOM", detail)
    if SW.kind_of(row.signer) == "node":
        res.v("NODE", detail)
    if ln != key:
        res.v("POSSESS", detail)
    if len(row.digests) not in COUNTS:
        res.v("DIGESTS", detail)
    if any(d[0][2] != g.suite for d in discl):
        res.v("SUITE", detail)
    if row.withdrawn:
        res.v("WITHDRAWN", detail)


STATIC_REASONS = ("group_not_of_a_room", "vouch_digest_count", "vouch_term", "vouch_signature",
                  "vouch_not_the_members_key", "vouch_by_node_key", "vouch_by_no_members_key", "vouch_discloses_nothing",
                  "vouch_discloses_more_than_one", "disclosure_not_in_vouch", "vouch_names_another_leaf",
                  "vouch_names_another_room", "vouch_names_another_suite", "vouch_not_started", "vouch_ended",
                  "vouch_withdrawn", "leaf_not_signed_by_its_key")
STATIC_WITNESSES = ("accepted_under_a_person_key", "accepted_under_a_agent_key", "accepted_under_a_room_key",
                    "accepted_at_a_call_group", "accepted_with_1_digests", "accepted_with_8_digests",
                    "accepted_with_32_digests", "accepted_with_a_shorter_term")
STATIC_PREMISES = ("ONE.none_disclosed", "ONE.two_disclosed", "ROOM.good_in_A_presented_at_B.chat",
                   "ROOM.good_in_A_presented_at_B.call", "ROOM.good_in_A_presented_at_B.random",
                   "NODE.node_signed", "SOUND.leaf_accepted", "SOUND.signed_by_a_seated_key_of_no_member_kind",
                   "COMPLETE.signed_and_well_presented", "CALLS.at_a_call_group",
                   "DIGESTS.other_count", "SUITE.other_suite_disclosed", "WITHDRAWN.static",
                   "POSSESS.not_signed_by_its_key")


# ====================================================================================================== part 2
DW = LV.World(seats={"A": {"P": "dP", "O": "dO"}, "B": {"P": "dP", "T": "dT"}},
              kind={"dP": "person", "dO": "person", "dT": "person", "nP": "node", "nT": "node"},
              owner={"nP": "P", "nT": "T"})
# the same, with the thief seated in room A too: a member of the room who copies another member's leaf key
DW_THIEF_IN_A = LV.World(seats={"A": {"P": "dP", "O": "dO", "T": "dT"}, "B": {"P": "dP", "T": "dT"}},
                         kind=DW.kind, owner=DW.owner)
WORLDS = {"apart": DW, "thief_in_A": DW_THIEF_IN_A}
DG = [SGN[n] for n in ("A.chat", "A.call", "A.random", "B.chat", "B.call", "B.random")]
DGN = {g.name: g for g in DG}
SLOTS = ("A.chat", "A.call")     # the groups the honest device P holds a leaf in

DEVICE = {"fresh_key": True, "forms": (("ok", TERM),)}
SHORT = {"fresh_key": True, "forms": (("ok", TERM), ("ok", TERM // 2))}
LAZY = {"fresh_key": True, "forms": (("ok", TERM), ("long", 2 * TERM + 1), ("noend", None))}
SAME_KEY = {"fresh_key": False, "forms": (("ok", TERM),)}
# a device that signs a vouch one tick before the vouch starts, the leaf key already made and in memory
AHEAD = {"fresh_key": True, "forms": (("ok", TERM), ("ahead", TERM))}


@lru_cache(maxsize=None)
def to_row(i, dr):
    start, end, wd, keyid, _form = dr
    return LV.make_row(("h", i), "dP", [e(("hA", keyid), "A"), e(("hB", keyid), "B")], 8, start, end, withdrawn=wd)


def thief_cands(g, now, lk, rows, curkey):
    """Every LeafNode the thief can put together. It holds the lifted leaf key, a leaf key of its own, its own
    device key (seated in room B) and node key, and the honest device's node key. It reads every row and every
    disclosure the honest device ever made."""
    lifted = ("hA", lk)
    held = [lifted, "tF"]
    others = [("hB", lk)] + ([("hA", curkey)] if curkey != lk else [])
    for i, dr in enumerate(rows):
        if dr is None:
            continue
        row = to_row(i, dr)
        ds = LV.disclosures_of(row)
        opts = [(), (ds[0],), (ds[1],), ds] + [((e(k, g.room), "fabricated"),) for k in held]
        for discl in opts:
            for key in held + others:
                ln = key if key in held else lifted
                for ident in ("P", "T", "O"):
                    yield ident, key, ln, row, discl
    for signer, sig_ok in (("nP", True), (lifted, True), ("dT", True), ("nT", True), ("dP", False)):
        for key in held:
            for room in ("A", "B"):
                row = LV.make_row(("t", signer, sig_ok, key, room, now), signer, [e(key, room)], 1, now, now + TERM,
                                  sig_ok=sig_ok)
                for ident in ("P", "T", "O"):
                    yield ident, key, key, row, LV.disclosures_of(row)


class Life:
    def __init__(self, rule, dev, world=None):
        self.rule, self.dev, self.res = rule, dev, Res()
        self.w = world or DW
        self.memo = {}

    def cands(self, g, now, lk, rows, curkey, replaced):
        k = (g.name, now, lk, rows, curkey, replaced)
        if k not in self.memo:
            acc, n_lifted = [], 0
            for ident, key, ln, row, discl in thief_cands(g, now, lk, rows, curkey):
                self.res.n["thief presentations"] += 1
                if key == ("hA", lk):
                    n_lifted += 1
                r = LV.door_leaf(self.rule, self.w, g, ident, key, ln, row, discl, now, replaced)
                if r is None:
                    acc.append((ident, key, ln, row, discl))
                else:
                    self.res.refusals[r] += 1
            self.memo[k] = (acc, n_lifted)
        return self.memo[k]

    def judge_leaf(self, S, actor, g, ident, key, ln, row, discl, now, lifted):
        res = self.res
        it = LV.intended(self.w, g, ident, key, row, now)
        res.premise["SOUND.leaf_accepted"] += 1
        detail = "%s: leaf accepted at %s as %s, key %s, row %s by %s, %d disclosed, now %d" % (
            actor, g.name, ident, key, row.rid[:2], row.signer, len(discl), now)
        if not it:
            res.v("SOUND", detail, S)
        if len(discl) != 1:
            res.v("ONE", detail, S)
        if not any(x[0] == key and x[1] == g.room for x in LV.entries_of(row)) or any(d[0][1] != g.room for d in discl):
            res.v("ROOM", detail, S)
        if self.w.kind_of(row.signer) == "node":
            res.v("NODE", detail, S)
        if ln != key:
            res.v("POSSESS", detail, S)
        if row.withdrawn:
            res.v("WITHDRAWN", detail, S)
        if actor == "thief":
            lk, t_l, n_l = lifted
            if key == ("hA", lk) and ident == "T" and it:
                res.w("the_thief_vouches_the_copied_key_as_its_own_leaf_in_its_own_room", detail, S)
            elif key == ("hA", lk):
                if now >= t_l + TERM:
                    res.v("TERM", detail + " (lifted at %d)" % t_l, S)
                else:
                    res.premise["TERM.lifted_key_accepted_inside_the_term"] += 1
            if not ((ident == "T" and it) or (key == ("hA", lk) and row.rid[0] == "h" and row.rid[1] < n_l)):
                res.v("RENEW", detail + " (lifted at %d, %d rows then)" % (t_l, n_l), S)
        return it

    def successors(self, S):
        rule, dev, res = self.rule, self.dev, self.res
        now, rows, online, slots, lifted, extras, flags = S
        offl, removed = flags       # offl: the device came back online after its vouch ended and has not yet renewed
        cur = len(rows) - 1
        out = []

        def mk(**kw):
            d = dict(now=now, rows=rows, online=online, slots=slots, lifted=lifted, extras=extras, flags=flags)
            d.update(kw)
            return canon(d["now"], d["rows"], d["online"], d["slots"], d["lifted"], d["extras"], d["flags"])

        # ---- time
        if now < H:
            out.append(("tick to %d" % (now + 1), mk(now=now + 1)))

        # ---- the honest device P
        if online:
            if len(rows) < MAXROWS and self.may_issue(rows, now):
                for form, dur in dev["forms"]:
                    if form == "ok" and dur < TERM and sum(1 for r in rows if r and r[4] == "ok" and r[1] - r[0] < TERM) >= MAXSHORT:
                        continue
                    keyid = len(rows) if dev["fresh_key"] or not rows else rows[-1][3]
                    start = now + 1 if form == "ahead" else now
                    end = None if dur is None else start + dur
                    label = "P's device key signs vouch %d: leaf key %d, start %d, end %s%s" % (
                        len(rows), keyid, start, end, "" if form == "ok" else " (%s)" % form)
                    out.append((label, mk(rows=rows + ((start, end, False, keyid, form),))))
            if rows:
                row = to_row(cur, rows[cur])
                key = ("hA", rows[cur][3])
                discl = (LV.disclosures_of(row)[0],)
                it = LV.intended
                for gi, gname in enumerate(SLOTS):
                    g = DGN[gname]
                    if slots[gi] is None:
                        # an Add: another member commits it
                        r = LV.door_leaf(rule, self.w, g, "P", key, key, row, discl, now)
                        ok = self.honest_leaf(S, g, key, row, discl, now, r, None)
                        if gname == "A.call":
                            rx = LV.door_leaf(rule, self.w, DGN["A.random"], "P", key, key, row, discl, now)
                            if rx == "group_not_of_a_room":
                                res.w("a_call_group_with_a_random_id_is_refused", "", S)
                        if ok:
                            s2 = slots[:gi] + (cur,) + slots[gi + 1:]
                            f2 = (offl, removed and None in s2)
                            label = "a member adds P's leaf (vouch %d) to %s" % (cur, gname)
                            if gname == "A.chat":
                                res.w("the_device_joins_the_chat_group", "", S, label)
                            elif slots[0] == cur:
                                res.w("the_same_leaf_and_vouch_join_a_call_group", "", S, label)
                            if removed:
                                res.w("after_a_removal_the_device_comes_back_by_another_members_add", "", S, label)
                            out.append((label, mk(slots=s2, flags=f2)))
                    elif slots[gi] != cur:
                        old_i = slots[gi]
                        old = to_row(old_i, rows[old_i])
                        oldkey = ("hA", rows[old_i][3])
                        st = LV.sem_state(old, now)
                        m = LV.door_msg(rule, old, "update_replacing_self", now)
                        r = m or LV.door_leaf(rule, self.w, g, "P", key, key, row, discl, now, (oldkey, old, "P"))
                        good = it(self.w, g, "P", key, row, now)
                        if st == "lapsed" and good:
                            res.premise["REJOIN.lapsed_leaf_with_a_fresh_vouch"] += 1
                            if r is not None:
                                res.v("REJOIN", "P's Update from its lapsed leaf refused (%s) at %s, now %d" % (r, gname, now), S)
                        self.honest_leaf(S, g, key, row, discl, now, r, (oldkey, old, st))
                        if r is None:
                            s2 = slots[:gi] + (cur,) + slots[gi + 1:]
                            S2 = mk(slots=s2, flags=(offl and any(x not in (None, cur) for x in s2), removed))
                            label = "P's old leaf signs the Update at %s: new leaf key %d, vouch %d" % (
                                gname, rows[cur][3], cur)
                            if st == "live" and key != oldkey:
                                res.w("a_renewal_installs_a_fresh_leaf_key_by_one_update", "", S, label)
                                if rows[cur][1] is not None and rows[cur][1] - rows[cur][0] < TERM:
                                    res.w("a_renewal_takes_a_shorter_term", "", S, label)
                            if st == "lapsed" and offl and not removed:
                                res.w("offline_past_the_end_then_back_by_its_own_update", "", S, label)
                            if st == "withdrawn":
                                res.w("a_withdrawn_leaf_is_replaced_by_its_own_update", "", S, label)
                            out.append((label, S2))
                        elif r == "leaf_withdrawn":
                            res.w("a_withdrawn_leaf_signs_no_update", "", S)
                        elif r == "vouch_term":
                            res.w("a_vouch_%s_is_refused" % ("without_an_end" if row.end is None else "over_the_cap"), "", S)
                for i, dr in enumerate(rows):
                    if dr and not dr[2] and sum(1 for x in rows if x and x[2]) < MAXWD and dr[1] is not None and now < dr[1]:
                        r2 = rows[:i] + ((dr[0], dr[1], True, dr[3], dr[4]),) + rows[i + 1:]
                        out.append(("P's device key withdraws vouch %d" % i, mk(rows=r2)))
                # offline is modelled only as the absence that matters: from a live leaf until after its vouch ended
                if slots[0] is not None and LV.sem_state(to_row(slots[0], rows[slots[0]]), now) == "live" and not offl:
                    out.append(("P's device goes offline", mk(online=False)))
        elif slots[0] is None or LV.sem_state(to_row(slots[0], rows[slots[0]]), now) != "live":
            out.append(("P's device is back online, after the end of its vouch", mk(online=True, flags=(slots[0] is not None, removed))))

        # ---- every leaf P holds: what its signature is taken on
        for gi, gname in enumerate(SLOTS):
            if slots[gi] is None:
                continue
            row = to_row(slots[gi], rows[slots[gi]])
            st = LV.sem_state(row, now)
            for kind in LV.KINDS[:3]:
                r = LV.door_msg(rule, row, kind, now)
                self.judge_msg(S, "P", gname, row, kind, now, r, st)
            # ---- the other members: remove it as lapsed
            r = LV.door_remove(rule, row, now)
            if r is None:
                res.premise["REMOVE.removed_as_lapsed"] += 1
                if st == "live":
                    res.v("REMOVE", "a live leaf removed as lapsed at %s, now %d" % (gname, now), S)
                s2 = slots[:gi] + (None,) + slots[gi + 1:]
                S2 = mk(slots=s2, flags=(offl and any(x is not None for x in s2), True))
                if st == "lapsed":
                    res.w("members_remove_a_leaf_that_stays_lapsed", "", S, "the members remove P's leaf from %s as lapsed" % gname)
                out.append(("the members remove P's leaf from %s as lapsed" % gname, S2))
            else:
                res.premise["REMOVE.live_leaf_not_removed"] += 1
                res.w("a_live_leaf_is_not_removed_as_lapsed", "", S)

        # ---- the thief
        if lifted is None:
            if rows:
                in_memory = {rows[s][3] for s in slots if s is not None} | {rows[cur][3]}
                for k in sorted(in_memory):
                    S2 = mk(lifted=(k, now, len(rows)))
                    label = "THE THIEF copies leaf key %d (and the node key) from the device's memory" % k
                    res.w("the_thief_copies_a_leaf_key", "", S, label)
                    out.append((label, S2))
        else:
            out.extend(self.thief(S, mk))
        return out

    @staticmethod
    def may_issue(rows, now):
        if not rows:
            return True
        start, end, wd, _k, form = rows[-1]
        if now <= start:
            return False
        if wd:
            return True
        span = (end - start) if form == "ok" else TERM
        return now >= start + span // 2          # the device renews no earlier than half term

    def honest_leaf(self, S, g, key, row, discl, now, r, replaced):
        """P presents its own leaf, well formed. Returns whether the door took it."""
        res = self.res
        it = LV.intended(self.w, g, "P", key, row, now)
        expect = it
        if replaced is not None and replaced[2] == "withdrawn" and not self.rule["withdrawn_may_replace"]:
            expect = False
        if replaced is not None and replaced[2] == "void":
            expect = None           # the old leaf should never have been in the tree; no expectation
        if it:
            res.premise["COMPLETE.honest_leaf_presented"] += 1
            if g.name == "A.call":
                res.premise["CALLS.honest_leaf_at_the_call_group"] += 1
        if r is None:
            self.judge_leaf(S, "P", g, "P", key, key, row, discl, now, None)
            return True
        self.res.refusals[r] += 1
        if expect:
            res.v("COMPLETE", "P's leaf refused (%s) at %s, now %d" % (r, g.name, now), S)
            if g.name == "A.call":
                res.v("CALLS", "P's leaf refused (%s) at %s, now %d" % (r, g.name, now), S)
        return False

    def judge_msg(self, S, actor, gname, row, kind, now, r, st, lifted=None, key=None):
        res = self.res
        detail = "%s: %s from a %s leaf (row %s) %s at %s, now %d" % (
            actor, kind, st, row.rid[:2], "accepted" if r is None else "refused (%s)" % r, gname, now)
        if st != "live":
            res.premise["LAPSED.%s_from_a_%s_leaf" % (kind, st)] += 1
        if st == "withdrawn":
            res.premise["WITHDRAWN.message_under_a_withdrawn_vouch"] += 1
        if r is None:
            if st != "live":
                res.v("LAPSED", detail, S)
            if st == "withdrawn":
                res.v("WITHDRAWN", detail, S)
            if lifted is not None:
                lk, t_l, _n = lifted
                if now >= t_l + TERM:
                    res.v("TERM", detail + " (lifted at %d)" % t_l, S)
                else:
                    res.premise["TERM.lifted_key_accepted_inside_the_term"] += 1
                    res.w("the_lifted_key_is_taken_while_its_vouch_runs", detail, S)
                    if now == t_l + TERM - 1:
                        res.w("the_lifted_key_is_taken_on_the_last_tick_of_the_term", detail, S)
        else:
            res.refusals[r] += 1
            if st == "live":
                res.v("COMPLETE", detail, S)
            if actor == "P" and st == "lapsed" and kind == "application":
                res.w("a_lapsed_leafs_application_message_is_refused", detail, S)
            if lifted is not None:
                lk, t_l, _n = lifted
                if now >= t_l + TERM:
                    res.premise["TERM.lifted_key_tried_after_the_term"] += 1
                if st == "lapsed":
                    res.w("the_lifted_key_is_refused_once_its_vouch_ended", detail, S)
                if st == "withdrawn" and now < row.end:
                    res.w("a_withdrawn_vouch_refuses_the_lifted_key_before_its_end", detail, S)

    def thief(self, S, mk):
        rule, res = self.rule, self.res
        now, rows, online, slots, lifted, extras, flags = S
        lk, t_l, n_l = lifted
        lkey = ("hA", lk)
        curkey = rows[-1][3]
        out = []
        # the leaves in a tree that carry the lifted key
        leaves = [(SLOTS[gi], s, True) for gi, s in enumerate(slots) if s is not None and rows[s][3] == lk]
        leaves += [(gname, i, False) for gname, i in sorted(extras)]
        for gname, i, is_slot in leaves:
            g = DGN[gname]
            old = to_row(i, rows[i])
            st = LV.sem_state(old, now)
            for kind in LV.KINDS[:3]:
                r = LV.door_msg(rule, old, kind, now)
                self.judge_msg(S, "thief", gname, old, kind, now, r, st, lifted, lkey)
            m = LV.door_msg(rule, old, "update_replacing_self", now)
            if st != "live":
                res.premise["LAPSED.update_replacing_self_from_a_%s_leaf" % st] += 1
            if m is not None:
                res.refusals[m] += 1
                continue
            acc, n_lifted = self.cands(g, now, lk, rows, curkey, (lkey, old, "P"))
            if now >= t_l + TERM:
                res.premise["TERM.lifted_key_tried_after_the_term"] += n_lifted
            if st == "lapsed" and not acc:
                res.w("the_thiefs_update_from_the_lapsed_leaf_is_refused", "", S)
            for ident, key, ln, row, discl in acc:
                self.judge_leaf(S, "thief", g, ident, key, ln, row, discl, now, lifted)
                if ident == "P" and key == lkey and row == old:
                    res.w("the_thief_updates_the_leaf_in_place_while_its_vouch_runs", "", S)
                    continue            # the same key under the same vouch: the tree's entry does not change
                if ident == "P" and key == lkey and row.rid[0] == "h":
                    j = row.rid[1]      # the same key under another honest row
                    if is_slot:
                        gi = SLOTS.index(gname)
                        out.append(("the thief's Update at %s keeps key %d under vouch %d" % (gname, lk, j),
                                    mk(slots=slots[:gi] + (j,) + slots[gi + 1:])))
                    else:
                        out.append(("the thief's Update at %s keeps key %d under vouch %d" % (gname, lk, j),
                                    mk(extras=(extras - {(gname, i)}) | {(gname, j)})))
                elif ident == "T" and LV.intended(self.w, g, ident, key, row, now):
                    # the thief is a member of this room: the copied key signs an Update whose new LeafNode is
                    # the thief's own leaf, and the leaf it replaces is gone from the tree
                    label = "the copied key %d signs an Update at %s that puts a leaf of the thief's in its place" % (lk, gname)
                    if st != "live":
                        res.w(IDENTITY_WITNESS, "at %s, the replaced leaf's vouch %s, now %d, lifted at %d" % (
                            gname, st, now, t_l), S, label)
                        if now >= t_l + TERM:
                            res.n["Updates signed by the copied key and taken, a term or more after the lift"] += 1
                    if is_slot:
                        gi = SLOTS.index(gname)
                        s2 = slots[:gi] + (None,) + slots[gi + 1:]
                        out.append((label, mk(slots=s2, flags=(flags[0] and any(x is not None for x in s2), True))))
                    else:
                        out.append((label, mk(extras=extras - {(gname, i)})))
                else:
                    res.n["thief leaves accepted and not carried into the tree"] += 1
        # an Add at every group: an honest member commits any LeafNode the door takes
        for g in DG:
            acc, n_lifted = self.cands(g, now, lk, rows, curkey, None)
            if now >= t_l + TERM:
                res.premise["TERM.lifted_key_tried_after_the_term"] += n_lifted
            if g.room != "A":
                res.premise["ROOM.thief_at_" + g.name] += 1
            res.premise["NODE.thief_presents_node_signed_rows"] += 1
            res.premise["RENEW.thief_tries_to_install_a_leaf"] += 1
            for ident, key, ln, row, discl in acc:
                it = self.judge_leaf(S, "thief", g, ident, key, ln, row, discl, now, lifted)
                if it and ident == "P" and key == lkey and row.rid[0] == "h":
                    j = row.rid[1]
                    if (g.name, j) in extras:
                        continue
                    S2 = mk(extras=extras | {(g.name, j)})
                    if g.name in SLOTS and slots[SLOTS.index(g.name)] is not None \
                            and slots[SLOTS.index(g.name)] > j and rows[slots[SLOTS.index(g.name)]][3] != lk:
                        res.w("beside_the_devices_newer_leaf_the_lifted_key_is_added_under_its_old_vouch", "", S,
                              "the thief has key %d added to %s under vouch %d" % (lk, g.name, j))
                    out.append(("the thief has key %d added to %s under vouch %d" % (lk, g.name, j), S2))
                elif not (ident == "T" and it):
                    res.n["thief leaves accepted and not carried into the tree"] += 1
        return out


IDENTITY_WITNESS = "a_copied_key_whose_vouch_ended_signs_an_update_that_installs_the_thiefs_own_leaf"
THIEF_IN_A = "the rule, a thief who is also a member of room A"
THIEF_IN_A_KEEPS = "the same thief, where an Update must keep the identity of the leaf it replaces"

LIFE_WITNESSES = (
    "the_device_joins_the_chat_group", "the_same_leaf_and_vouch_join_a_call_group",
    "a_call_group_with_a_random_id_is_refused", "a_renewal_installs_a_fresh_leaf_key_by_one_update",
"a_lapsed_leafs_application_message_is_refused",
    "offline_past_the_end_then_back_by_its_own_update", "members_remove_a_leaf_that_stays_lapsed",
    "a_live_leaf_is_not_removed_as_lapsed", "after_a_removal_the_device_comes_back_by_another_members_add",
    "the_thief_copies_a_leaf_key", "the_lifted_key_is_taken_while_its_vouch_runs",
    "the_lifted_key_is_taken_on_the_last_tick_of_the_term", "the_lifted_key_is_refused_once_its_vouch_ended",
    "the_thiefs_update_from_the_lapsed_leaf_is_refused", "the_thief_updates_the_leaf_in_place_while_its_vouch_runs",
    "beside_the_devices_newer_leaf_the_lifted_key_is_added_under_its_old_vouch",
    "a_withdrawn_vouch_refuses_the_lifted_key_before_its_end",
    "the_thief_vouches_the_copied_key_as_its_own_leaf_in_its_own_room")
LIFE_PREMISES = (
    "TERM.lifted_key_accepted_inside_the_term", "TERM.lifted_key_tried_after_the_term",
    "RENEW.thief_tries_to_install_a_leaf", "ROOM.thief_at_B.chat", "ROOM.thief_at_B.call", "ROOM.thief_at_B.random",
    "LAPSED.application_from_a_lapsed_leaf", "LAPSED.proposal_from_a_lapsed_leaf", "LAPSED.commit_from_a_lapsed_leaf",
    "LAPSED.update_replacing_self_from_a_lapsed_leaf", "REJOIN.lapsed_leaf_with_a_fresh_vouch",
    "NODE.thief_presents_node_signed_rows", "SOUND.leaf_accepted", "COMPLETE.honest_leaf_presented",
    "CALLS.honest_leaf_at_the_call_group", "WITHDRAWN.message_under_a_withdrawn_vouch",
    "REMOVE.removed_as_lapsed", "REMOVE.live_leaf_not_removed")


def canon(now, rows, online, slots, lifted, extras, flags):
    """Forget a row that is out of play: ended or withdrawn, in no tree, not the device's newest, and for a leaf key
    the thief does not hold. Its key has left the device's memory, and the thief presents it no more."""
    keep = {s for s in slots if s is not None} | {i for _g, i in extras} | {len(rows) - 1}
    lk = lifted[0] if lifted else None
    if any(dr is not None and i not in keep and dr[3] != lk and (dr[2] or dr[1] is None or now >= dr[1])
           for i, dr in enumerate(rows)):
        rows = tuple(None if (dr is not None and i not in keep and dr[3] != lk and (dr[2] or dr[1] is None or now >= dr[1]))
                     else dr for i, dr in enumerate(rows))
    return (now, rows, online, slots, lifted, extras, flags)


def life_run(rule, dev, stop_on=None, world=None):
    L = Life(rule, dev, world)
    init = (0, (), True, (None, None), None, frozenset(), (False, False))
    parent = {init: None}
    queue = deque([init])
    while queue:
        S = queue.popleft()
        for label, S2 in L.successors(S):
            if S2 not in parent:
                parent[S2] = (S, label)
                queue.append(S2)
        if stop_on is not None and stop_on in L.res.viol:
            L.res.n["states when the search stopped at the break"] = len(parent)
            break
    else:
        L.res.n["states"] = len(parent)

    def trace(S):
        steps = []
        while S is not None and parent.get(S) is not None:
            S, label = parent[S]
            steps.append(label)
        return list(reversed(steps))

    res = L.res
    traces = {}
    for name, (detail, S, step) in res.witness.items():
        traces["witness:" + name] = (trace(S) if S is not None else []) + ([step] if step else [])
    for prop, (cnt, detail, S) in res.viol.items():
        traces["violation:" + prop] = trace(S) if S is not None else []
    return res, traces


# ====================================================================================================== part 3
def padding_run(pad):
    """What a room's door sees of a row covering n rooms: the digests (opaque), one disclosure. Padding digests are
    assumed indistinguishable from an entry's."""
    res = Res()
    seen = {}
    for n in range(1, 33):
        ndig = LV.pad_count(n) if pad else n
        row = LV.make_row(("pad", n), "dP", [e(("k", i), ("room", i)) for i in range(n)], ndig, 0, TERM)
        obs = len(row.digests)
        seen.setdefault(LV.pad_count(n), set()).add(obs)
        res.premise["PADDING.rows"] += 1
    for bucket, obs in sorted(seen.items()):
        if len(obs) != 1:
            res.v("PADDING", "rows in the bucket of %d show %d different digest counts" % (bucket, len(obs)))
    if LV.pad_count(33) is None:
        res.w("more_than_32_rooms_is_more_than_one_row")
    told = {o for s in seen.values() for o in s}
    if pad and told != set(COUNTS):
        res.v("PADDING", "a door tells apart the counts %s, not 1, 8 and 32" % sorted(told))
    res.n["what a door tells apart"] = len(told)
    return res


# ====================================================================================================== plants
# name, part(s) it runs in, the changed rule, the changed device, the property that MUST break, what it is
PLANTS = [
    ("renewal_revouches_the_same_leaf_key", "life", {}, SAME_KEY, "TERM",
     "THE REJECTED DESIGN: a renewal signs a new vouch for the leaf key already in the tree"),
    ("same_key_and_the_door_refuses_a_same_key_update", "life", {"fresh_on_update": True}, SAME_KEY, "TERM",
     "the rejected design, with a door that refuses an Update keeping the key: the key comes back by an Add"),
    ("no_cap_on_the_term", "life+door", {"cap": False}, LAZY, "TERM",
     "the door takes a vouch with no end or a longer term; a device that signs one"),
    ("the_end_is_not_read", "life+door", {"covers": False}, DEVICE, "TERM", "the door does not compare now with the end"),
    ("the_end_is_inclusive", "life+door", {"covers": "end_inclusive"}, DEVICE, "TERM",
     "the door takes a vouch on the instant of its end: one tick more than the term"),
    ("the_vouch_starts_after_the_key_is_made", "life", {}, AHEAD, "TERM",
     "A DEVICE, NOT A DOOR: it signs a vouch that starts a tick later, the leaf key already in memory; no door can tell"),
    ("the_old_leaf_key_vouches_the_next", "life", {"signer": "old_leaf", "kind": False}, DEVICE, "RENEW",
     "a renewal's vouch may be signed by the leaf key it replaces (and a leaf key is taken as a member's kind of key)"),
    ("the_device_is_read_as_its_node", "life+door", {"signer": "owner_bound_node", "kind": False}, DEVICE, "NODE",
     "a node key owner-bound to the member may sign the vouch"),
    ("a_seated_node_key_vouches", "door", {"kind": False}, None, "NODE",
     "a key a roster seats may vouch whatever kind of key it is"),
    ("any_valid_signature", "life+door", {"signer": "any_key"}, DEVICE, "RENEW",
     "the vouch's signer is not compared with the member's seated key"),
    ("any_seated_key_of_the_room_vouches", "life+door", {"signer": "any_seat"}, DEVICE, "SOUND",
     "the vouch's signer is a key the room seats, for whichever member: one member vouches a leaf as another"),
    ("the_signature_is_not_verified", "life+door", {"sig": False}, DEVICE, "RENEW", "the row's signature is not checked"),
    ("the_leaf_key_is_not_compared", "life+door", {"entry_key": False}, DEVICE, "RENEW",
     "the disclosed entry's leaf key is not compared with the LeafNode's"),
    ("the_disclosure_is_not_matched", "life+door", {"digest_match": False}, DEVICE, "RENEW",
     "a disclosure's salted digest is not looked up in the row"),
    ("the_room_is_not_compared", "life+door", {"entry_room": False}, DEVICE, "ROOM",
     "the disclosed entry's room is not compared with the group's room"),
    ("the_room_is_not_recomputed", "life+door", {"recompute_room": False}, DEVICE, "ROOM",
     "the door takes a group's room on the group's word (a call group with a random id)"),
    ("any_disclosed_entry_will_do", "life+door", {"one": "any_match"}, DEVICE, "ONE",
     "a presentation with two disclosures is accepted when one of them fits"),
    ("no_disclosure_needed", "life+door", {"one": "zero_ok"}, DEVICE, "ONE",
     "a presentation that discloses nothing is accepted on the row alone"),
    ("the_suite_is_not_compared", "door", {"entry_suite": False}, None, "SUITE", "an entry for another suite is accepted"),
    ("any_digest_count", "door", {"digest_count": False}, None, "DIGESTS", "a row of 2 or 33 digests is accepted"),
    ("a_withdrawal_is_not_read", "life+door", {"withdrawal": False}, DEVICE, "WITHDRAWN",
     "the door does not read a withdrawal of the vouch"),
    ("no_proof_of_possession", "life+door", {"pop": False}, DEVICE, "POSSESS",
     "the LeafNode's own signature is not checked against the leaf key it carries"),
    ("the_replaced_leaf_key_signs_the_new_leafnode", "life", {"pop": "or_replaced"}, DEVICE, "POSSESS",
     "on an Update the new LeafNode may be signed by the leaf key it replaces: the thief installs P's next leaf for it"),
    ("a_shorter_term_is_refused", "door", {"shorter_ok": False}, None, "COMPLETE",
     "the door refuses a vouch whose end is sooner than the cap"),
    ("a_lapsed_leafs_messages_are_held", "life", {"lapsed": "app_ok"}, DEVICE, "LAPSED",
     "a lapsed leaf's application messages are taken"),
    ("a_lapsed_leaf_commits", "life", {"lapsed": "commit_ok"}, DEVICE, "LAPSED", "a lapsed leaf's proposals and commits are taken"),
    ("a_lapsed_leaf_signs_nothing", "life", {"lapsed": "nothing"}, DEVICE, "REJOIN",
     "a lapsed leaf's replacing Update is refused with its other messages"),
    ("the_vouch_binds_one_group", "life+door", {"bind": "chat_group_only"}, DEVICE, "CALLS",
     "the vouch is good in the room's chat group only"),
    ("any_leaf_removed_as_lapsed", "life", {"remove": "any"}, DEVICE, "REMOVE", "a live leaf may be removed as lapsed"),
    ("no_padding", "padding", {}, None, "PADDING", "the row carries as many digests as it has entries"),
]


def run_case(case):
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
    name, parts, rule_kw, dev, stop_on, world = case
    rule = rule_with(**rule_kw)
    out = {"name": name, "viol": {}, "n": {}, "premise": {}, "witness": {}, "refusals": {}, "traces": {}}

    def fold(res, part, tr=None):
        for p, (cnt, detail, _s) in res.viol.items():
            out["viol"].setdefault(p, []).append((part, cnt, detail))
        for k, v in res.n.items():
            out["n"]["%s: %s" % (part, k)] = v
        for k, v in res.premise.items():
            out["premise"]["%s: %s" % (part, k)] = v
        for k, (detail, _s, _st) in res.witness.items():
            out["witness"]["%s: %s" % (part, k)] = detail
        for k, v in res.refusals.items():
            out["refusals"]["%s: %s" % (part, k)] = v
        if tr:
            out["traces"].update(tr)

    if "door" in parts:
        fold(static_run(rule), "door")
    if "life" in parts:
        res, tr = life_run(rule, dev, stop_on, WORLDS[world])
        fold(res, "life", tr)
    if "padding" in parts:
        fold(padding_run(pad=(name != "no_padding")), "padding")
    return out


def main():
    want_traces = "--traces" in sys.argv
    write = "--write-expected" in sys.argv
    cases = [("the rule as modelled", "door+life+padding", {}, DEVICE, None, "apart"),
             ("the rule, a device that also signs a shorter term", "life", {}, SHORT, None, "apart"),
             ("the rule, a withdrawn leaf signs no Update (the other reading)", "life", {"withdrawn_may_replace": False}, DEVICE, None, "apart"),
             ("the rule, a device that signs vouches over the cap or with no end", "life", {}, LAZY, None, "apart"),
             (THIEF_IN_A, "life", {}, DEVICE, None, "thief_in_A"),
             (THIEF_IN_A_KEEPS, "life", {"update_keeps_identity": True}, DEVICE, None, "thief_in_A")]
    nruns = len(cases)
    # a plant's search of part 2 stops at the first state that breaks the property named for it
    cases += [(n, parts, kw, dev, must, "apart") for n, parts, kw, dev, must, _what in PLANTS]
    with multiprocessing.Pool(3) as pool:
        results = pool.map(run_case, cases, chunksize=1)
    by = {r["name"]: r for r in results}
    rc = 0
    lines = []       # the expected table

    print("leaf_vouch: the MLS leaf vouch and its lifecycle. Enumerations over a bound; not a proof.")
    print("bound: TERM = %d ticks (the 30 days), horizon %d ticks, at most %d vouching rows, %d withdrawn and %d shorter in play;"
          % (TERM, H, MAXROWS, MAXWD, MAXSHORT))
    print("       rooms A and B (and a private room C at the door), one honest device, one thief, one lift.")
    print("       three workers, each capped at 2 GiB of address space.")
    base = by["the rule as modelled"]
    if (LV.DIGEST_COUNTS, LV.SEAT_KINDS, LV.SUITE) != (COUNTS, MEMBER_KINDS, 0x004D):
        rc = 1
        print("A CONSTANT OF leaf_vouch.py IS NOT THE RULE'S: digest counts %r, member kinds %r, suite %#06x"
              % (LV.DIGEST_COUNTS, LV.SEAT_KINDS, LV.SUITE))
    for name in [c[0] for c in cases[:nruns]]:
        r = by[name]
        print("\n== %s" % name)
        for k in sorted(r["n"]):
            print("   %-58s %d" % (k, r["n"][k]))
        if r["viol"]:
            rc = 1
            for p, vs in sorted(r["viol"].items()):
                for part, cnt, detail in vs:
                    print("   VIOLATED %s (%s, %d cases): %s" % (p, part, cnt, detail))
        else:
            print("   no property is violated")
        if r["n"].get("life: thief leaves accepted and not carried into the tree"):
            rc = 1
            print("   A LEAF THE THIEF HAD ACCEPTED IS NOT IN THE STATE: the enumeration is not complete")
        lines.append(("run", name, "violated: " + (",".join(sorted(r["viol"])) or "none")))

    print("\n== the properties, under the rule as modelled, and the cases that reach each premise")
    need = ["door: " + p for p in STATIC_PREMISES] + ["life: " + p for p in LIFE_PREMISES] + ["padding: PADDING.rows"]
    for p, text in PROPS.items():
        prem = [(k, base["premise"].get(k, 0)) for k in need if k.split(": ")[1].startswith(p + ".")]
        held = p not in base["viol"]
        empty = [k for k, v in prem if v == 0]
        if not prem or empty or not held:
            rc = 1
        print("   %-9s %-8s %s" % (p, "holds" if held else "VIOLATED", text))
        for k, v in prem:
            print("             %-58s %d%s" % (k, v, "" if v else "   <-- PREMISE NEVER REACHED"))
        lines.append(("property", p, "holds" if held else "violated"))

    print("\n== witnesses (each must be reached under the rule as modelled)")
    wneed = ["door: " + w for w in STATIC_WITNESSES] + ["life: " + w for w in LIFE_WITNESSES] \
        + ["padding: more_than_32_rooms_is_more_than_one_row"]
    for w in wneed:
        got = w in base["witness"]
        if not got:
            rc = 1
        print("   %-8s %s" % ("reached" if got else "MISSING", w))
        lines.append(("witness", w, "reached" if got else "missing"))
        if want_traces and got:
            if base["witness"][w]:
                print("            %s" % base["witness"][w])
            for i, step in enumerate(base["traces"].get("witness:" + w.split(": ")[1], [])):
                print("            %2d. %s" % (i + 1, step))
    for name, wit in (("the rule, a device that also signs a shorter term", "life: a_renewal_takes_a_shorter_term"),
                      ("the rule, a withdrawn leaf signs no Update (the other reading)", "life: a_withdrawn_leaf_signs_no_update"),
                      ("the rule as modelled", "life: a_withdrawn_leaf_is_replaced_by_its_own_update"),
                      ("the rule, a device that signs vouches over the cap or with no end", "life: a_vouch_over_the_cap_is_refused"),
                      ("the rule, a device that signs vouches over the cap or with no end", "life: a_vouch_without_an_end_is_refused")):
        got = wit in by[name]["witness"]
        if not got:
            rc = 1
        print("   %-8s %s   [%s]" % ("reached" if got else "MISSING", wit, name))
        lines.append(("witness", wit, "reached" if got else "missing"))

    # the reading the rule sentences leave open: where the thief is a member of the room, the copied key's
    # signature is taken on an Update after its vouch ended, unless an Update must keep the leaf's identity
    for name, want_reached in ((THIEF_IN_A, True), (THIEF_IN_A_KEEPS, False)):
        got = ("life: " + IDENTITY_WITNESS) in by[name]["witness"]
        if got != want_reached:
            rc = 1
        print("   %-8s life: %s   [%s]%s" % ("reached" if got else "absent", IDENTITY_WITNESS, name,
                                             "" if got == want_reached else "   <-- NOT AS EXPECTED"))
        lines.append(("witness", "life: %s [%s]" % (IDENTITY_WITNESS, name), "reached" if got else "absent"))
        if want_traces and got:
            print("            %s" % by[name]["witness"]["life: " + IDENTITY_WITNESS])
            for i, step in enumerate(by[name]["traces"].get("witness:" + IDENTITY_WITNESS, [])):
                print("            %2d. %s" % (i + 1, step))

    print("\n== refusal reasons at the door (each must be the first reason of some presentation)")
    for reason in STATIC_REASONS:
        n = base["refusals"].get("door: " + reason, 0)
        if not n:
            rc = 1
        print("   %-34s %d%s" % (reason, n, "" if n else "   <-- NEVER REACHED"))

    print("\n== plants (the property named must break; listed with it, what else had broken when the search stopped)")
    for name, parts, kw, dev, must, what in PLANTS:
        r = by[name]
        caught = sorted(r["viol"])
        ok = must in caught
        if not ok:
            rc = 1
        print("   %-10s %-48s must break %-9s broke: %s" % ("caught" if ok else "NOT CAUGHT", name, must, ",".join(caught) or "nothing"))
        print("              %s" % what)
        for k in sorted(r["n"]):
            if "states" in k:
                print("              %s: %d" % (k, r["n"][k]))
        if ok:
            for part, cnt, detail in r["viol"][must]:
                print("              %s (%d cases): %s" % (part, cnt, detail))
                if want_traces and part == "life":
                    for i, step in enumerate(r["traces"].get("violation:" + must, [])):
                        print("              %2d. %s" % (i + 1, step))
        lines.append(("plant", name, "breaks: " + ",".join(caught)))

    text = "kind\tname\tresult\n" + "".join("%s\t%s\t%s\n" % x for x in lines)
    if write:
        with open(EXPECTED, "w") as f:
            f.write(text)
        print("\nwrote %s" % EXPECTED)
    else:
        try:
            with open(EXPECTED) as f:
                want = f.read()
        except OSError:
            want = None
        if want != text:
            rc = 1
            print("\nDIFFERS from leaf_vouch_expected.tsv")
            if want is not None:
                a, b = want.splitlines(), text.splitlines()
                for x in sorted(set(a) ^ set(b)):
                    print("   %s %s" % ("expected:" if x in a else "got:     ", x))
        else:
            print("\nequal to leaf_vouch_expected.tsv (%d lines)" % len(lines))
    print("\n%s" % ("ALL HOLD: every property holds over the bound, every premise and witness is reached, every plant is caught"
                    if rc == 0 else "FAILED"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
