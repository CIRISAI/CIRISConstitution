"""
route.py: COPYING AS NEED.

    needs(reads, kept)      the rows a conclusion reads that are not held (the `missing` answer)
    route(row, party)       the row is in the read set of something the party must conclude
                            AND the party is in the row's audience

A conclusion is a named function of a concluded state together with the rows it reads. What a party must conclude
follows from its seat (MUST, table data): a member concludes the roster and the state of each message; an author,
who has acknowledged its message; a moderator, who has acknowledged every message; every seated key, its own
duties; a removed key, its own seat and the state of its own rows; a stranger, nothing.

Audience. `own`: the members of the room at the row's own head, its signers and the keys it names. That is a
function of the row and its ancestors, as KERNEL.md asks. It is not enough: a joiner is not in the audience of the
founding row its own admission names, so under the door it can never keep its admission. `closed` adds the rule
that makes the door and the audience agree: a row carries its audience to the rows it names, when the row is
concluded and its signer is already in the audience of the row named. So an admission carries the joiner to the
founding rows it names, and a member's reply carries what it answers to a later joiner. A row by a key outside the
named row's audience, or a row that concludes nothing, carries nobody: knowing a digest gives no access.
Carriage stays inside one room: a row that names another from a different room carries it only when the same key
signed both (formal/causal_order/Carry.lean). `any_member` is the rule without that clause, kept for comparison.
Both are run and the difference is reported.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import seat as ST  # noqa: E402

CK, CUT, K, R = ST.CK, ST.CUT, ST.K, ST.R
ROSTER_KINDS = {"offer", "accept", "cosign", "unseat", "withdraw"}


def msg(id, signer, room, head, names=()):
    return R(id, "msg", signer, tuple(head) + tuple(names), room=room, head=tuple(head), on=(("seat", signer, "member", room),))


def ack(id, signer, room, of, head):
    return R(id, "ack", signer, (of,) + tuple(h for h in head if h != of), room=room, of=of, head=tuple(head),
             on=(("seat", signer, "member", room),))


def rule(r, P, past):
    if r["kind"] in ("msg", "ack"):
        if r["kind"] == "ack" and not K.sel(P, id=r["of"], kind="msg"): return False
        return r["signer"] in ST.members_at(P, past, r["room"], r["head"])
    return ST.seat_rule(r, P, past)


def world():
    """One room. A and B found it, and the founding record seats both as duty holders (CC 4.5.4), so both moderate.
    C is admitted, writes, and is removed. X is a stranger."""
    room = lambda r: dict(r, room="g")
    g = ST.offer("g", "A", ("A", "B"), "duty", "@", "self", cosigners=("B",), room="g")
    md = R("md", "record", "A", ("g",), room="g", duties=("moderate",))    # the room's record declares its duties (CC 4.5.4 (i))
    ac = room(ST.accept("ac", "C", None, ("g",), scope="member", obj="g"))
    cb = room(ST.cosign("cb", "B", "w", ("g",)))
    w = ST.offer("w", "A", "C", "member", "g", "group", ("g", "ac", "cb"), head=("g",), policy="community_invite", content="w", room="g")
    m1 = msg("m1", "B", "g", ("g",))                 # before C joined
    k1 = ack("k1", "A", "g", "m1", ("g",))
    m2 = msg("m2", "C", "g", ("w",))
    m3 = msg("m3", "A", "g", ("w",))
    k2 = ack("k2", "B", "g", "m3", ("w",))
    k3 = ack("k3", "C", "g", "m3", ("w",))
    xc = room(ST.cosign("xc", "B", "x", ("w",)))
    x = ST.unseat("x", "A", "C", "member", "g", "group", ("w", "xc", "m2"), head=("w",), policy="community_remove", content="x", room="g")
    m4 = msg("m4", "C", "g", ("w",))                 # concurrent with the removal
    m5 = msg("m5", "B", "g", ("x",))
    k4 = ack("k4", "A", "g", "m5", ("x",))
    return [g, md, ac, cb, w, m1, k1, m2, m3, k2, k3, xc, x, m4, m5, k4]


REPLY = msg("m6", "A", "g", ("w",), names=("m1",))   # a reply, after C joined, to a message from before: C is in its audience
PARTIES = ("A", "B", "C", "X")
ROOM = "g"


# ---- audience ------------------------------------------------------------------------------------------
def audience(S, how="closed", by_arrival=False):
    """row id -> the keys the row is for."""
    past = lambda a, b: a in S.anc[b]
    own = {}
    for i, r in enumerate(S.rows):
        if not S.C.get(r["id"]): own[r["id"]] = frozenset(ST.signers(r)); continue
        if by_arrival:      # MUTATION: the members when the row arrived, by list position
            sub = [q for q in S.rows[:i + 1] if S.C.get(q["id"])]
            mem = ST.Seats(CK.State(sub, {q["id"]: True for q in sub})).holders("member", r["room"])
        else:
            mem = ST.members_at(S.Cs, past, r["room"], (r["id"],))
        own[r["id"]] = mem | ST.signers(r) | frozenset(r.get("to", ()))
    if how == "own": return own
    namers = {i: [] for i in S.by}
    for d in S.rows:
        for n in d["names"]:
            if n in namers: namers[n].append(d)
    aud, changed = dict(own), True
    while changed:                                          # the least fixed point; it only grows
        changed = False
        for i in S.by:
            for d in namers[i]:
                r = S.by[i]
                if how != "any_member" and not (d.get("room") == r.get("room") or d["signer"] == r["signer"]):
                    continue                                # a row leaves its room only by its own signer's act
                if S.C.get(d["id"]) and d["signer"] in aud[i] and not aud[d["id"]] <= aud[i]:
                    aud[i] = aud[i] | aud[d["id"]]; changed = True
    return aud


# ---- conclusions: a value and the rows it reads ----------------------------------------------------------
def _up(S, ids):
    ids = frozenset(i for i in ids if i in S.by)
    return ids | frozenset(a for i in ids for a in S.anc[i] if a in S.by)


def roster_reads(S):
    """The rows that seat or unseat a member of the room, and what they name."""
    return _up(S, [r["id"] for r in S.rows if r["kind"] in ("offer", "unseat") and r["obj"] == ROOM and r["scope"] == "member"]
               + [w["id"] for w in K.sel(S.rows, kind="withdraw")])


def c_duties(S, k):
    """The seats the key itself holds over the room, and the rows that seat or unseat it."""
    mine = [r["id"] for r in S.rows if r["kind"] in ("offer", "unseat") and r["obj"] == ROOM and k in r["to"]]
    return frozenset(x for x in ST.Seats(S).snapshot() if x[0] == k and x[2] == ROOM), _up(S, mine)


def c_roster(S):
    return ST.Seats(S).holders("member", ROOM), roster_reads(S)


def c_state(S, m):
    val = CUT.Cut(S).status(S.by[m]) if m in S.by else "not held"
    return val, _up(S, [m]) | roster_reads(S)


def c_delivered(S, m):
    C = CUT.Cut(S)
    acks = [a for a in K.sel(S.Cs, kind="ack", of=m) if C.counts(a)]
    return frozenset(a["signer"] for a in acks), _up(S, [m] + [a["id"] for a in K.sel(S.rows, kind="ack", of=m)]) | roster_reads(S)


def c_seat(S, k):
    on = [r["id"] for r in S.rows if ("seat", k, "member", ROOM) in tuple(r.get("on", ())) + tuple(r.get("cuts", ()))
          and r["kind"] in ROSTER_KINDS]
    return ST.Seats(S).stands(k, "member", ROOM), _up(S, on)


def must(S, party):
    """The conclusions the party's seat asks of it: name -> function(state) -> (value, reads)."""
    Q = ST.Seats(S)
    msgs = [r["id"] for r in K.sel(S.rows, kind="msg", room=ROOM)]
    out = {}
    if Q.stands(party, "member", ROOM):
        out[("roster",)] = c_roster
        out[("duties", party)] = lambda T: c_duties(T, party)
        for m in msgs: out[("state", m)] = lambda T, m=m: c_state(T, m)
        for m in msgs:
            if S.by[m]["signer"] == party or Q.stands(party, "moderate", ROOM):
                out[("delivered", m)] = lambda T, m=m: c_delivered(T, m)
    elif any(party in r.get("to", ()) for r in K.sel(S.rows, kind="offer", room=ROOM)):      # seated once, or offered a seat
        out[("seat", party)] = lambda T: c_seat(T, party)
        for m in msgs:
            if S.by[m]["signer"] == party: out[("state", m)] = lambda T, m=m: c_state(T, m)
    return out


def route_sets(S, how="closed", by_arrival=False):
    """party -> the ids routed to it."""
    aud = audience(S, how, by_arrival)
    out = {}
    for p in PARTIES:
        reads = frozenset().union(*(f(S)[1] for f in must(S, p).values())) if must(S, p) else frozenset()
        out[p] = frozenset(i for i in reads if p in aud[i])
    return out


def needs(reads, kept_ids):
    return frozenset(reads) - frozenset(kept_ids)


def state_of(rows):
    return CK.concluded(CK.kept(rows), rule)


def measure(rows, how="closed"):
    """Sufficiency, minimality and size for every party, against a party given every row."""
    S = state_of(rows)
    aud, routes = audience(S, how), route_sets(S, how)
    out = {}
    for p in PARTIES:
        M = must(S, p)
        full = {c: f(S)[0] for c, f in M.items()}
        reads = frozenset().union(*(f(S)[1] for f in M.values())) if M else frozenset()
        given = [r for r in rows if r["id"] in routes[p]]
        got = (lambda T: {c: f(T)[0] for c, f in M.items()})(state_of(given))
        slack = []
        for i in sorted(routes[p]):
            T = state_of([r for r in given if r["id"] != i])
            if all(f(T)[0] == full[c] for c, f in M.items()): slack.append(i)
        in_aud = frozenset(i for i in S.by if p in aud[i])
        out[p] = {"conclusions": len(M), "differ": sorted(str(c) for c in M if got[c] != full[c]), "routed": len(routes[p]),
                  "in_audience": len(in_aud), "all_rows": len(S.rows), "not_needed": slack,
                  "blocked": sorted(reads - in_aud), "outside_audience": sorted(routes[p] - in_aud),
                  "still_missing": sorted(needs(reads, routes[p]))}
    return out


if __name__ == "__main__":
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
    for label, rows in (("the room", world()), ("the room and a reply to an earlier message", world() + [REPLY])):
        for how in ("own", "closed"):
            print("%s, audience %s" % (label, how))
            for p, m in measure(rows, how).items():
                print("   %s conclusions=%d differ=%d routed=%d in_audience=%d of %d rows; routed and not needed: %s; read and outside audience: %s" % (
                    p, m["conclusions"], len(m["differ"]), m["routed"], m["in_audience"], m["all_rows"], m["not_needed"], m["blocked"]))
