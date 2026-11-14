"""
roomkey.py: A PRIVATE ROOM SEATS VOICES, over the kernel (seat.py, window.py, route.py, cut.py, checkpoint.py,
keyplane.py), which is not changed.

The rule run here
    room        a community declares itself in its founding row: membership private or public. An absent member reads
                public. A room goes private -> public and never back. A self room and a family are seated by identity
                keys whatever they say: the rule is for communities.
    voice       what the roster of a private room seats. A voice is a small counted roster of ROOM KEYS, one for each
                device of its holder, each made for this room only (the self roster of CC 3.3.6.4, in the room). Every
                row of the room (speech, reply, vote, admission, removal, window, acknowledgement, a duty holder's
                verdict) is signed under a room key. A room row carries the voice as `signer`, the room key that made
                the signature as `dev`, and the head of the voice's roster it relies on as `vhead`. The kernel reads
                `signer`.
    binding     the fact "this voice is this person". It is never a row and nobody signs it. It is made for one
                addressee under one of the MECHANISMS below; the one the text plans is `two_encap`.
    commitment  the seat row of a room key carries a hash over the room, the room key, the person and fresh random
                bytes. The binding carries the opening, and a binding that does not open it is refused.
    standing is rows, the name is the binding
                no kernel answer reads a binding. A binding is read in three places only: what a member is shown (who
                said it), what a member checks before giving its voice to an admission, and a count of persons, which
                WAITS at a node that does not hold a binding (a stall at that node, never a fork).

Three claims
    AUTHENTIC-INSIDE   no party other than P and B can make a fact that B's verifier accepts as "voice v is P".
    DENIABLE-OUTSIDE   whatever a set of members hands an outsider, with every secret they hold, convinces the outsider of
                       nothing about another person, and the same set could have produced a view the outsider cannot tell
                       from it (the simulator).
    ONE-PERSON-ONE-VOICE  a count in the room counts voices, however many room keys sign; and a second voice of a person
                       already seated needs an admission count made wholly of members who did not check.

The cryptography is symbolic, and nothing here is proved in Lean. A fact has a set of MAKERS, the parties able to
produce exactly those bytes. A party X is CONVINCED that P made a fact iff X's verifier accepts it and
makers - {X} == {P}. A fact is TRANSFERABLE iff it convinces some party that is neither P nor its addressee. A SIMULATOR
for a coalition is a production of the same view, up to the names of keys nothing ties to a person, using only what the
coalition can make. A verdict here says what follows if the primitives behave as their symbols do. LIMITS lists what
the rule does not give; each entry says whether a run shows it or whether it is stated from outside the model.
"""
import hashlib
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import seat as ST      # noqa: E402
import window as WN    # noqa: E402
import route as RT     # noqa: E402

CK, CUT, K, R = ST.CK, ST.CUT, ST.K, ST.R
ROOM = "g"

LIMITS = (
    # (how it is known, the limit)
    ("stated", "deniability against a verifier who cheats, with a post-quantum key exchange, is conjectured and not proved; "
               "the run shows only what follows if such a verifier can form a challenge it cannot itself open"),
    ("run", "a member cooperating live with an outsider (the outsider supplies the challenge) can prove what it sees"),
    ("stated", "a member's word is always possible: what is removed is the proof"),
    ("run", "one signed row by the person outside the room tying the room key to themself makes that person's history in the room provable"),
    ("run", "a room already signed under identity keys stays provable, and declaring it private afterwards is refused"),
    ("run", "a removed member keeps the bindings it was given"),
    ("run", "custody claims and delivery still reach a node: a claim under a room key names no person, and the network that "
            "carries the bytes sees which nodes receive them unless delivery goes by the anonymous tier (the network is outside this model)"),
    ("run", "a new key record appears when someone joins: whoever holds the rows sees that a joining happened, and when"),
    ("stated", "erasure by person finds a person's room rows only through that person's own devices, which keep the list of their room keys"),
    ("run", "an order naming a person finds no row of a private room that names or proves that person; it rests on testimony or on a member's device"),
)


# =========================================================================================================
# 1. the kernel does not care which key: one room, built over any naming of its signers
# =========================================================================================================
def rule(r, P, past):
    """One conclusion rule for the whole room: the device check, then the kernel's own rules."""
    if "dev" in r and r["dev"] not in ST.members_at(P, past, r["signer"], r["vhead"], "key"):
        return False
    return RT.rule(r, P, past) if r["kind"] in ("msg", "ack") else WN.rule(r, P, past)


def state_of(rows):
    return CK.concluded(CK.kept(rows), rule)


def in_room(r):
    return dict(r, room=ROOM)


def room_world(nm):
    """The room of route.py (A and B found it as its two duty holders, so both moderate; C is admitted, writes and is removed), and then: C is
    admitted again, J joins later, A replies to a message from before J joined, the room votes, and a member opens the
    moderation fallback. nm: person -> the key the roster seats (an identity key, or a voice)."""
    A, B, C, J = nm["A"], nm["B"], nm["C"], nm["J"]
    C2 = nm.get("C2", C)                                        # the key of C's second stint (a fresh room key, where given)
    g = ST.offer("g", A, (A, B), "duty", "@", "self", cosigners=(B,), room=ROOM)       # the founding record seats its signers as duty holders (CC 4.5.4)
    md = R("md", "record", A, ("g",), room=ROOM, duties=("moderate",))                  # the room's record declares its duties, as route.py
    ac = in_room(ST.accept("ac", C, None, ("g", "md"), scope="member", obj="g"))
    cb = in_room(ST.cosign("cb", B, "w", ("g",)))
    w = ST.offer("w", A, C, "member", "g", "group", ("g", "ac", "cb"), head=("g",), policy="community_invite", content="w", room=ROOM)
    m1 = RT.msg("m1", B, "g", ("g",))
    k1 = RT.ack("k1", A, "g", "m1", ("g",))
    m2 = RT.msg("m2", C, "g", ("w",))
    m3 = RT.msg("m3", A, "g", ("w",))
    k3 = RT.ack("k3", C, "g", "m3", ("w",))
    xc = in_room(ST.cosign("xc", B, "x", ("w",)))
    x = ST.unseat("x", A, C, "member", "g", "group", ("w", "xc", "m2"), head=("w",), policy="community_remove", content="x", room=ROOM)
    m4 = RT.msg("m4", C, "g", ("w",))                          # concurrent with the removal
    m5 = RT.msg("m5", B, "g", ("x",))
    # C is admitted again: a new acceptance, a new count, over the head the removal made
    ac2 = in_room(ST.accept("ac2", C2, None, ("x",), scope="member", obj="g"))
    cb2 = in_room(ST.cosign("cb2", B, "w2", ("x",)))
    w2 = ST.offer("w2", A, C2, "member", "g", "group", ("x", "ac2", "cb2"), head=("x",), policy="community_invite", content="w2", room=ROOM)
    m7 = RT.msg("m7", C2, "g", ("w2",))
    # J joins later
    aj = in_room(ST.accept("aj", J, None, ("w2",), scope="member", obj="g"))
    cj = in_room(ST.cosign("cj", B, "wj", ("w2",)))
    wj = ST.offer("wj", A, J, "member", "g", "group", ("w2", "aj", "cj"), head=("w2",), policy="community_invite", content="wj", room=ROOM)
    m8 = RT.msg("m8", A, "g", ("wj",), names=("m1",))            # a reply, after J joined, to a message from before
    # a vote
    pr = R("pr", "proposal", A, ("wj",), room=ROOM)
    votes = [R("v" + p, "vote", nm[p], ("pr",), choice=c, room=ROOM) for p, c in (("A", "yes"), ("B", "yes"), ("C2" if "C2" in nm else "C", "no"), ("J", "yes"))]
    # the moderation fallback: B opens it, C and J act, the moderator is silent, B lands it
    W = WN.secs("moderation_fallback")
    p = in_room(WN.opener("p", B, "moderation_fallback", "g", ("wj",)))
    a1 = in_room(WN.answer("a1", C2, "p", "act"))
    a2 = in_room(WN.answer("a2", J, "p", "act"))
    a3 = in_room(WN.answer("a3", B, "p", "act"))
    rc = in_room(WN.receipt("rc", B, "p", 0))
    L = in_room(WN.landing("L", B, "p", "rc", "fallback", W, ("a1", "a2", "a3")))
    late = in_room(WN.answer("late", A, "p", "answered"))       # the moderator answers, concurrent with the landing
    return [g, md, ac, cb, w, m1, k1, m2, m3, k3, xc, x, m4, m5, ac2, cb2, w2, m7, aj, cj, wj, m8, pr] + votes + [p, a1, a2, a3, rc, L, late]


PERSONS = ("A", "B", "C", "J")
ID = {p: "id:" + p for p in PERSONS + ("X",)}                   # the identity world: the roster seats the person's own key
VOICE = {"A": "rk:q", "B": "rk:n", "C": "rk:z", "J": "rk:b", "X": "rk:a"}     # voices, in another sort order than the persons


def rename(x, f):
    """Every string that is a key of f, at any depth, replaced."""
    if isinstance(x, str): return f.get(x, x)
    if isinstance(x, dict): return {rename(k, f): rename(v, f) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return type(x)(rename(v, f) for v in x)
    if isinstance(x, frozenset): return frozenset(rename(v, f) for v in x)
    return x


def answers(rows, parties):
    """Every named answer of the kernel for this set of rows."""
    S = state_of(rows)
    Q, C = ST.Seats(S), CUT.Cut(S)
    aud = RT.audience(S, "closed")
    out = {"concluded": dict(S.C), "seats": Q.snapshot(), "status": C.all(), "audience": aud,
           "members": Q.holders("member", ROOM), "moderators": Q.holders("moderate", ROOM)}
    for p in parties:
        M = RT.must(S, p)
        reads = frozenset().union(*(f(S)[1] for f in M.values())) if M else frozenset()
        out[("route", p)] = frozenset(i for i in reads if p in aud[i])
        out[("must", p)] = {c: f(S)[0] for c, f in M.items()}
    for o in K.sel(S.Cs, kind="open"):
        out[("window", o["id"])] = WN.outcomes(S, o["id"])
    for pr in K.sel(S.Cs, kind="proposal"):
        mem = ST.members_at(S.Cs, lambda a, b: a in S.anc[b], ROOM, tuple(n for n in pr["names"]))
        out[("tally", pr["id"])] = {c: CK.tally(S, pr, mem, c, counting=C.counts) for c in ("yes", "no")}
    return out


def closed_subsets(rows, upto):
    """Every non-empty subset of up to `upto` rows that is closed under what its rows name (rows are listed parents first)."""
    by = {r["id"] for r in rows}
    def go(i, ids, acc):
        if i == len(rows):
            if acc: yield list(acc)
            return
        yield from go(i + 1, ids, acc)
        r = rows[i]
        if len(acc) < upto and all(m in ids for m in r["names"] if m in by):
            yield from go(i + 1, ids | {r["id"]}, acc + [r])
    yield from go(0, frozenset(), [])


def indifference_mutation():
    """A reader that breaks a tie by the order of key names is not indifferent: the comparison must catch it."""
    base = room_world(ID)
    f = {ID[p]: VOICE[p] for p in ID}
    first = lambda rows: sorted(ST.Seats(state_of(rows)).holders("member", ROOM))[0]
    return rename(first(base), f) != first(rename(base, f))


def indifference(upto=6, shard=None):
    """answers(rename(rows)) == rename(answers(rows)) for the whole room, every room with one row missing, and every
    closed subset of up to `upto` rows; and the same in the arrival order reversed where the door allows it."""
    base = room_world(ID)
    f = {ID[p]: VOICE[p] for p in ID}
    parties = [ID[p] for p in PERSONS + ("X",)]
    sets = [base] + [[r for r in base if r["id"] != d["id"]] for d in base] + list(closed_subsets(base, upto))
    n = bad = 0
    first = None
    for i, rows in enumerate(sets):
        if shard is not None and i % shard[1] != shard[0]: continue
        a = rename(answers(rows, parties), f)
        b = answers(rename(rows, f), [f[p] for p in parties])
        b2 = answers(list(reversed(rename(rows, f))), [f[p] for p in parties])
        for k in a:
            n += 2
            if a[k] != b[k] or a[k] != b2[k]:
                bad += 1
                first = first or (k, [r["id"] for r in rows])
    return {"sets": len(sets) if shard is None else len(sets[shard[0]::shard[1]]), "compared": n, "differ": bad, "first": first}


# =========================================================================================================
# 2. devices: a voice is a roster of device keys. ONE-PERSON-ONE-VOICE as a count.
# =========================================================================================================
def by_dev(row, dev, vhead):
    """A room row signed by one device key of the voice. The kernel reads signer (the voice)."""
    return dict(row, dev=dev, vhead=tuple(vhead), names=tuple(row["names"]) + tuple(h for h in vhead if h not in row["names"]),
                on=tuple(row.get("on", ())) + (("seat", dev, "key", row["signer"]),))


def voice_rows(v, devs):
    """The voice's own roster: the first key founds it, each further key is added by a strict majority of the keys
    live at the head named (self_roster_add), and signs its own seat. Returns (rows, head)."""
    rows = [ST.offer(v, devs[0], (devs[0],), "key", "@", "self", room=ROOM)]
    head = v
    for i, d in enumerate(devs[1:], 1):
        need = i // 2 + 1                                        # a strict majority of the i keys already live
        rid = "%s+%d" % (v, i)
        rows.append(ST.offer(rid, devs[0], d, "key", v, "group", (head,), head=(head,), policy="self_roster_add", counted="key",
                             cosigners=tuple(devs[1:need]) + (d,), room=ROOM))
        head = rid
    return rows, head


def device_votes(max_dev=2):
    """Three persons, each with one or two device keys. Every way the devices can vote yes, no or not at all. The
    kernel's tally over voices must equal the count of persons whose devices that voted all said yes."""
    persons = ("A", "B", "C")
    n = bad = mut = 0
    for shape in itertools.product(range(1, max_dev + 1), repeat=3):
        base, heads, devs = [], {}, {}
        for p, k in zip(persons, shape):
            devs[p] = ["d:%s%d" % (p, i) for i in range(k)]
            vr, heads[p] = voice_rows("v" + p, devs[p])
            base += vr
        voices = tuple("v" + p for p in persons)
        g = ST.offer("g", voices[0], voices, "member", "@", "self", cosigners=voices[1:], room=ROOM,
                     names=tuple(heads[p] for p in persons))
        pr = R("pr", "proposal", "vA", ("g",), room=ROOM)
        slots = [(p, d) for p in persons for d in devs[p]]
        for choice in itertools.product(("yes", "no", None), repeat=len(slots)):
            rows = base + [g, pr]
            for (p, d), c in zip(slots, choice):
                if c: rows.append(by_dev(R("t" + d, "vote", "v" + p, ("pr",), choice=c, room=ROOM), d, (heads[p],)))
            S = state_of(rows)
            mem = ST.Seats(S).holders("member", ROOM)
            got = {c: CK.tally(S, pr, mem, c, counting=CUT.Cut(S).counts) for c in ("yes", "no")}
            said = {p: {c for (q, d), c in zip(slots, choice) if q == p and c} for p in persons}
            want = {c: sum(1 for p in persons if said[p] == {c}) for c in ("yes", "no")}
            n += 1
            if got != want or len(mem) != 3: bad += 1
            by_key = {c: sum(1 for x in choice if x == c) for c in ("yes", "no")}       # MUTATION: a count of device keys
            mut += by_key != want
    return {"vote assignments": n, "differ": bad, "a count of keys would differ": mut}


def device_cases():
    """What happens to a device key and to a person, read from the kernel."""
    facts = []
    devs = ["d:A0", "d:A1", "d:A2"]
    vr, vh = voice_rows("vA", devs)
    vb, bh = voice_rows("vB", ["d:B0"])
    vc, ch = voice_rows("vC", ["d:C0"])
    g = ST.offer("g", "vA", ("vA", "vB", "vC"), "member", "@", "self", cosigners=("vB", "vC"), room=ROOM, names=(vh, bh, ch))
    base = vr + vb + vc + [g]
    counts = lambda rows, rid: CUT.Cut(state_of(rows)).status(next(r for r in rows if r["id"] == rid))
    m = lambda rid, d, head, vhead: by_dev(RT.msg(rid, "vA", "g", head), d, vhead)
    # a device of the voice is lost: the two others evict it (a strict majority of three)
    ev = ST.unseat("ev", "d:A0", "d:A2", "key", "vA", "group", (vh,), head=(vh,), policy="self_roster_evict", counted="key",
                   cosigners=("d:A1",), room=ROOM)
    before = m("mb", "d:A2", ("g",), (vh,))
    conc = m("mc", "d:A2", ("g",), (vh,))
    after = m("ma", "d:A2", ("g",), ("ev",))
    other = m("mo", "d:A1", ("g",), ("ev",))
    ev2 = dict(ev, names=ev["names"] + ("mb",))
    rows = base + [before, ev2, conc, after, other]
    facts.append(("an evicted device key: its row in the eviction's past counts, its row concurrent with the eviction is void, "
                  "its row naming the eviction concludes nothing, and the voice's other key still speaks",
                  (counts(rows, "mb"), counts(rows, "mc"), counts(rows, "ma"), counts(rows, "mo")) == ("counts", "void", "concludes nothing", "counts")))
    S = state_of(rows)
    facts.append(("the room's roster is unchanged by the eviction of a device key (three voices)", ST.Seats(S).holders("member", ROOM) == frozenset({"vA", "vB", "vC"})))
    # the person is removed from the room; a device key is added to the voice afterwards, or concurrently
    xb = in_room(ST.cosign("xb", "vB", "x", ("g",)))
    x = ST.unseat("x", "vC", "vA", "member", "g", "group", ("g", "xb"), head=("g",), policy="community_remove", content="x", room=ROOM)
    nv, nh = "vA+3", "vA+3"
    add = ST.offer(nv, "d:A0", "d:A3", "key", "vA", "group", (vh,), head=(vh,), policy="self_roster_add", counted="key",
                   cosigners=("d:A1", "d:A3"), room=ROOM)
    new_conc = by_dev(RT.msg("mn", "vA", "g", ("g",)), "d:A3", (nh,))               # the rotated key, leaving the removal unnamed
    new_after = by_dev(RT.msg("mz", "vA", "g", ("x",)), "d:A3", (nh,))             # the rotated key, naming the removal
    rows = base + [xb, x, add, new_conc, new_after]
    S = state_of(rows)
    facts.append(("removal by causal past holds against a rotated key: after the room removes the voice, a key added to the voice "
                  "speaks for nobody (its row concurrent with the removal is void, its row naming the removal concludes nothing)",
                  "vA" not in ST.Seats(S).holders("member", ROOM) and counts(rows, "mn") == "void" and counts(rows, "mz") == "concludes nothing"))
    # one answer in every arrival order of that set
    snap = lambda T: (frozenset(T.C.items()), ST.Seats(T).snapshot(), frozenset(CUT.Cut(T).all().items()))
    want, n, bad = snap(S), 0, 0
    tail = [xb, x, add, new_conc, new_after]
    for perm in itertools.permutations(tail):
        n += 1
        bad += snap(CK.arrive(base + list(perm), rule)) != want
    for perm in itertools.permutations(tail):                    # and with the base arriving last
        n += 1
        bad += snap(CK.arrive(list(perm) + base, rule)) != want
    facts.append(("that set gives one answer in each of %d arrival orders" % n, bad == 0))
    # the alternative shape, device keys seated UNDER the first key (a chain): losing the first key loses them all
    gv = ST.offer("vA", "d:A0", ("d:A0",), "key", "@", "self", sub=True, room=ROOM)
    c1 = ST.offer("c1", "d:A0", "d:A1", "key", "vA", "seat", ("vA",), under="vA", sub=True, cosigners=("d:A1",), room=ROOM)
    wd = in_room(ST.withdraw("wd", "d:A0", "vA", ("c1",)))
    T1, T2 = state_of([gv, c1]), state_of([gv, c1, wd])
    facts.append(("FINDING, the chain shape: when device keys are seated under the first key, ending the first key ends every key of the voice "
                  "(so the voice is a counted roster, not a chain)",
                  ST.Seats(T1).holders("key", "vA") == frozenset({"d:A0", "d:A1"}) and ST.Seats(T2).holders("key", "vA") == frozenset()))
    # the other alternative, one key copied to every device: the room has no row that can end one device
    shared = [ST.offer("g", "kA", ("kA", "kB"), "member", "@", "self", cosigners=("kB",), room=ROOM), RT.msg("thief", "kA", "g", ("g",))]
    facts.append(("FINDING, one key copied to each device: a stolen device speaks as the voice and no row of the room can end that device alone; "
                  "the only answer is a new voice (a removal and an admission, and a binding to every member again)",
                  counts(shared, "thief") == "counts"))
    return facts


# =========================================================================================================
# 3. the binding, symbolically
# =========================================================================================================
MECHANISMS = {
    # name: (who can make the bytes, whose verifier accepts them, what is expected of it)
    "two_encap":    "two encapsulations and no signature: the addressee's challenge, which only P's identity can open, and P's confirmation, which the addressee could also have produced",
    "dvs":          "a designated-verifier signature by P for one addressee (a ring of two)",
    "sealed_cred":  "P's identity signature over the voice, sealed so that only members can open it (the credential of a group key agreement)",
    "room_mac":     "a statement MAC'd under the room's shared key (authenticated by the group key alone)",
    "identity_sig": "P's plain identity signature over the voice",
}
PAIRWISE = ("two_encap", "dvs")                                  # made for one addressee
EXPECT = {  # mechanism: (AUTHENTIC-INSIDE, DENIABLE-OUTSIDE)
    "two_encap": (True, True), "dvs": (True, True), "sealed_cred": (True, False), "room_mac": (False, True), "identity_sig": (True, False),
}


def binding(mech, person, voice, addressee, key_holders=(), challenge_by=None, oblivious=False, opening=None):
    """The fact 'voice is person', made for `addressee` (None: for whoever can open it). key_holders: who holds the
    room's shared key, for room_mac. For two_encap: `challenge_by` is who formed the challenge and so knows its secret
    (the addressee, unless another party supplied it), and `oblivious` says the challenge was formed so that nobody but
    P can be shown to know its secret. `opening` is the opening of the seat row's commitment that the binding carries."""
    to = addressee if mech in PAIRWISE else None
    return {"mech": mech, "person": person, "voice": voice, "to": to,
            "holders": frozenset(key_holders) if mech == "room_mac" else frozenset(),
            "knows": frozenset() if oblivious else frozenset({challenge_by or to}) if mech == "two_encap" else frozenset(),
            "opening": opening}


def makers(f):
    """two_encap: the confirmation is a function of the challenge's secret. P gets it by opening the challenge under its
    identity; whoever formed the challenge already holds it."""
    if f["mech"] == "two_encap": return frozenset({f["person"]}) | f["knows"]
    if f["mech"] in PAIRWISE: return frozenset({f["person"], f["to"]})
    if f["mech"] == "room_mac": return f["holders"]
    return frozenset({f["person"]})                               # a signature: its signer only


def accepts(party, f):
    """Does the party's verifier accept the bytes as a binding of the voice to the person?"""
    if f["mech"] in PAIRWISE: return f["to"] == party
    if f["mech"] == "room_mac": return party in f["holders"]
    return True                                                   # a signature verifies for anyone who is shown it


def convinced(party, f, given=frozenset()):
    """Sound conviction: the party's verifier accepts (or the party was handed the secrets of `given`, who can check it),
    and nobody but the person named, the party itself aside, could have made it."""
    checkable = accepts(party, f) or any(accepts(h, f) for h in given)
    return checkable and makers(f) - {party} == frozenset({f["person"]})


def transferable(f, everyone):
    return any(convinced(x, f, given=everyone) for x in everyone if x not in (f["person"], f["to"]))


def can_make(coalition, f):
    return bool(makers(f) & frozenset(coalition))


def authentic_inside(mech, members, removed=("R",)):
    """For every victim B, every person P and every coalition that holds neither P nor B (members, removed members and
    an outsider among them): can the coalition make a fact that B's verifier accepts as 'a voice of the coalition's
    making is P'? Returns (forgeries, cases, who)."""
    everyone = tuple(members) + tuple(removed) + ("X",)
    holders = tuple(members) + tuple(removed)                     # a removed member held the room's shared key
    n, forged, who = 0, 0, set()
    for B in members:
        for P in members:
            if P == B: continue
            rest = [x for x in everyone if x not in (P, B)]
            for k in range(1, len(rest) + 1):
                for co in itertools.combinations(rest, k):
                    n += 1
                    cands = [binding(mech, P, "rk:forged", to, holders) for to in (everyone if mech in PAIRWISE else (None,))]
                    hit = [f for f in cands if can_make(co, f) and accepts(B, f)]
                    if hit:
                        forged += 1
                        who |= {"a member" if c in members else "a removed member" if c in removed else "an outsider" for c in co if can_make((c,), hit[0])}
    return forged, n, sorted(who)


def honest_convinced(mech, members):
    """Completeness: P's own binding convinces each member it was made for."""
    n = ok = 0
    for P in members:
        for B in members:
            if B == P: continue
            n += 1
            f = binding(mech, P, "rk:" + P, B, members)
            ok += accepts(B, f) and (convinced(B, f) or mech == "room_mac")      # room_mac: accepted, and never soundly
    return ok, n


# ---- what a view proves, and the simulator ---------------------------------------------------------------
def view_of(rows, coalition, nm, bindings, kinds_id=()):
    """What a coalition of persons holds: the rows of the room in their audience, and the bindings each can open.
    kinds_id: row kinds that ALSO carry the signer's identity signature (the overlays of section 5)."""
    S = state_of(rows)
    aud = RT.audience(S, "closed")
    keys = {nm[p] for p in coalition}
    mine = [dict(r, id_sig=(r["kind"] in kinds_id)) for r in rows if aud.get(r["id"], frozenset()) & keys]
    held = [f for f in bindings if f["to"] in coalition or (f["to"] is None and (f["mech"] != "room_mac" or f["holders"] & set(coalition)))]
    return mine, held


def attributions(view, coalition, nm):
    """What an outsider handed the view, and every secret of the coalition, is convinced of about persons outside it."""
    rows, held = view
    who = {v: p for p, v in nm.items()}
    tied = {f["voice"]: f["person"] for f in held if convinced("X", f, given=frozenset(coalition))}
    out = set()
    for r in rows:
        p = who.get(r["signer"])
        if p is None or p in coalition: continue
        if r.get("id_sig"): out.add((r["id"], p, "signed under the identity key"))
        elif r["signer"] in tied: out.add((r["id"], tied[r["signer"]], "the voice is tied to the person by a fact the outsider can check"))
    return out


def canonical(view, coalition, nm):
    """The view up to the names of keys that nothing in it ties to a person for the outsider."""
    rows, held = view
    tied = {f["voice"] for f in held if convinced("X", f, given=frozenset(coalition))} | {r["signer"] for r in rows if r.get("id_sig")}
    order = {}
    def name(k):
        if k in tied or not isinstance(k, str) or not k.startswith(("rk:", "sim:")): return k
        return order.setdefault(k, "k%d" % len(order))
    def walk(x):
        if isinstance(x, str): return name(x)
        if isinstance(x, dict): return tuple(sorted(((k, walk(v)) for k, v in x.items()), key=repr))
        if isinstance(x, (list, tuple)): return tuple(walk(v) for v in x)
        if isinstance(x, frozenset): return tuple(sorted((walk(v) for v in x), key=repr))
        return x
    return tuple(walk(r) for r in rows), tuple(sorted((walk({k: v for k, v in f.items()}) for f in held), key=repr))


def simulate(rows, coalition, nm, bindings, kinds_id=()):
    """The coalition alone produces a view of the same room: a fresh key for every voice that is not its own, every row
    signed again, and every binding it is able to make. A row that carries another person's identity signature, and a
    binding the coalition cannot make, are left out: that is what 'cannot be simulated' means here."""
    f = {nm[p]: "sim:" + nm[p][3:] for p in nm if p not in coalition}
    view = view_of(rename(rows, f), coalition, {p: f.get(v, v) for p, v in nm.items()},
                   [dict(b, voice=f.get(b["voice"], b["voice"])) for b in bindings if can_make(coalition, b)], ())
    who = {v: p for p, v in nm.items()}
    orig_rows, _ = view_of(rows, coalition, nm, bindings, kinds_id)
    own_id = {r["id"] for r in orig_rows if r.get("id_sig") and who.get(r["signer"]) in coalition}
    return [dict(r, id_sig=r["id"] in own_id) for r in view[0]], view[1]


def all_bindings(mech, members, nm):
    return [binding(mech, P, nm[P], B, members) for P in members for B in (members if mech in PAIRWISE else (None,)) if B != P]


def deniable_outside(mech, kinds_id=()):
    """Every coalition of members that does not hold everyone: what the outsider is convinced of, and whether the
    coalition's simulation is the same view."""
    nm = {p: VOICE[p] for p in PERSONS}
    rows = room_world(nm)
    bs = all_bindings(mech, PERSONS, nm)
    n = proved = unsim = 0
    example = None
    for k in range(1, len(PERSONS)):
        for co in itertools.combinations(PERSONS, k):
            n += 1
            real = view_of(rows, co, nm, bs, kinds_id)
            att = attributions(real, co, nm)
            same = canonical(real, co, nm) == canonical(simulate(rows, co, nm, bs, kinds_id), co, nm)
            proved += bool(att)
            unsim += not same
            if att and example is None: example = (co, sorted(att)[0])
    return {"coalitions": n, "prove something": proved, "not simulable": unsim, "example": example}


# =========================================================================================================
# 4. the interactions
# =========================================================================================================
def second_voice(n_members):
    """A person already seated asks for a second voice. Honest members give their voice to an admission only when the
    binding made for them names a person not already seated. For every number of members who do not check: is the second
    voice seated? (the kernel's own count, community_invite)"""
    out = []
    mem = ["rk:m%d" % i for i in range(n_members)]
    g = ST.offer("g", mem[0], tuple(mem), "member", "@", "self", cosigners=tuple(mem[1:]), room=ROOM)
    for c in range(0, n_members + 1):
        cos = mem[:c]                                             # the first is the person itself, who always signs for its own second voice
        acc = in_room(ST.accept("ac", "rk:second", None, ("g",), scope="member", obj="g"))
        rows = [g, acc]
        if cos:
            rows.append(ST.offer("w", cos[0], "rk:second", "member", "g", "group", ("g", "ac"), head=("g",), policy="community_invite",
                                 content="w", cosigners=tuple(cos[1:]), room=ROOM))
        seated = "rk:second" in ST.Seats(state_of(rows)).holders("member", ROOM)
        out.append((n_members, c, seated, ST.met("community_invite", c, n_members)))
    return out


def interactions(mech="two_encap"):
    facts = []
    nm = {p: VOICE[p] for p in PERSONS}
    rows = room_world(nm)
    S = state_of(rows)
    Q = ST.Seats(S)
    aud = RT.audience(S, "closed")
    status = CUT.Cut(S).all()
    A, B, C, J = (nm[p] for p in PERSONS)
    # --- removal, re-admission -----------------------------------------------------------------------------
    facts.append(("removal by causal past: C's row in the removal's past counts, C's row concurrent with it is void",
                  status["m2"] == "counts" and status["m4"] == "void"))
    facts.append(("FINDING, re-admission under the SAME key: the kernel seats it again and counts it, so both stints are one key's and are linked "
                  "by any holder of the rows (the rule is a fresh room key; see section 7)",
                  C in Q.holders("member", ROOM) and status["m7"] == "counts" and status["m4"] == "void"))
    # --- the later joiner --------------------------------------------------------------------------------
    bs = all_bindings(mech, PERSONS, nm)
    b_for = lambda who, about: [f for f in bs if f["person"] == about and (f["to"] == who or f["to"] is None)]
    facts.append(("a reply carried to a later joiner: the message from before J joined is routed to J, and only because the reply names it",
                  J in aud["m1"] and "m1" in answers(rows, [J])[("route", J)] and J not in RT.audience(S, "own")["m1"]))
    facts.append(("the joiner is convinced who said it once the author has made a binding for the joiner (%s)" % mech,
                  all(convinced("J", f) for f in b_for("J", "B")) and bool(b_for("J", "B"))))
    facts.append(("before that binding exists the joiner holds a valid row of a seated voice with no name: the kernel's answers are the same, the name is missing",
                  S.C["m1"] and status["m1"] == "counts" and B in Q.holders("member", ROOM)
                  and not any(convinced("J", f) for f in bs if f["person"] == "B" and f["to"] not in ("J", None))))
    v = view_of(rows, ("J",), nm, bs)
    facts.append(("an outsider shown the same bytes by the joiner, with the joiner's secrets, is convinced of nothing about B",
                  not attributions(v, ("J",), nm)))
    # --- the removed member --------------------------------------------------------------------------------
    f_c = binding(mech, "A", A, "C", PERSONS)
    facts.append(("RESIDUAL: a removed member keeps the bindings made for it, so a later row of A shown to it still convinces it "
                  "(removal ends reading, not conviction, unless the voice changes its key)", convinced("C", f_c)))
    # --- carriage into another group -------------------------------------------------------------------------
    nm2 = {"A": "rk:q2", "B": "rk:n2", "E": "rk:e2"}                 # another room: A and B again under other voices, and E
    bs2 = [binding(mech, P, nm2[P], Bx, ("A", "B", "E")) for P in nm2 for Bx in nm2 if Bx != P]
    e_tied = {f["voice"] for f in bs2 if f["to"] == "E" and convinced("E", f)}
    facts.append(("carriage into another group: a member of the other group can check that some key signed the row, and holds no fact tying that key "
                  "to a person (B's voice there is another key)", B not in e_tied and nm2["B"] in e_tied))
    reuse = {"A": "rk:q2", "B": B, "E": "rk:e2"}                    # B used the SAME key in both rooms
    bs3 = [binding(mech, P, reuse[P], Bx, ("A", "B", "E")) for P in reuse for Bx in reuse if Bx != P]
    facts.append(("MUST NOT: a voice used in two rooms. E, who is not in the first room, is then convinced B wrote the carried row, and anyone "
                  "holding both rosters sees one key in two rooms", B in {f["voice"] for f in bs3 if f["to"] == "E" and convinced("E", f)}))
    # --- the detection record ---------------------------------------------------------------------------------
    det = {"id": "det", "kind": "detection", "signer": "node:n1", "names": (), "offered_by": C, "room": ROOM}
    tied_out = {f["voice"] for f in bs if convinced("X", f, given=frozenset({"A", "B", "J"}))}
    facts.append(("the detection record names a voice: members resolve it by their bindings, and nobody outside the room can (the record names no person)",
                  det["offered_by"] not in tied_out and all(convinced(m, f) for m in ("A", "B", "J") for f in b_for(m, "C") if f["to"] == m)))
    # --- the report to a duty holder who is not a member ---------------------------------------------------
    paths = {}
    row_ok = True                                                    # the row itself verifies under the voice for anyone shown it
    # r1 testimony only; r2 the reporter forwards the binding made for the reporter; r3 an identity signature;
    # r4 a binding made for the duty holder when the voice was seated
    cand = {"testimony": None, "forward the reporter's own binding": binding(mech, "C", C, "B", PERSONS),
            "identity signature": binding("identity_sig", "C", C, None), "a binding made for the duty holder at the seat": binding(mech, "C", C, "D", PERSONS)}
    for name, f in cand.items():
        d_conv = f is not None and convinced("D", f, given=frozenset({"B"})) and row_ok
        world = f is not None and any(convinced(x, f, given=frozenset({"B", "D"})) for x in ("X", "A", "J"))
        frame = f is not None and can_make(("B",), f) and accepts("D", f)
        paths[name] = (d_conv, world, frame)
    facts.append(("report, testimony only: the duty holder is not convinced", paths["testimony"] == (False, False, False)))
    facts.append(("report, forwarding the reporter's own binding: the duty holder is not convinced (the reporter could have made it)",
                  paths["forward the reporter's own binding"][0] is False))
    facts.append(("report, an identity signature: the duty holder is convinced and so is everyone (not deniable)",
                  paths["identity signature"][:2] == (True, True)))
    facts.append(("report, a binding made for the duty holder when the voice was seated: the duty holder is convinced, nobody else is even "
                  "with the duty holder's secrets, and the reporter cannot frame the person",
                  paths["a binding made for the duty holder at the seat"] == (True, False, False)))
    # the kernel shape of "no seat without the duty holder's acknowledgement": the admission names the ack and waits for it
    dk = ST.offer("dk", A, "rk:D", "review", "g", "self", ("g",), cosigners=("rk:D",), room=ROOM)
    ackD = R("ackD", "binding_ack", "rk:D", ("dk", "ac"), room=ROOM)
    g_, md_, ac_, cb_ = rows[0], rows[1], rows[2], rows[3]
    w_ = ST.offer("w", A, C, "member", "g", "group", ("g", "ac", "cb", "ackD"), head=("g",), policy="community_invite", content="w", room=ROOM)
    without = state_of([g_, md_, ac_, cb_, dk, w_])
    with_ = state_of([g_, md_, ac_, cb_, dk, ackD, w_])
    facts.append(("an admission that names the duty holder's acknowledgement waits at the door until it is held, in the kernel as it stands",
                  C not in ST.Seats(without).holders("member", ROOM) and C in ST.Seats(with_).holders("member", ROOM)
                  and "w" not in without.by))
    return facts


# =========================================================================================================
# 5. what else in the room would tie a voice, or a person, to the room for an outsider
# =========================================================================================================
OVERLAYS = (
    # (the row kinds that would also carry the signer's identity signature, the text that asks for it today)
    (("msg",), "speech signed under the identity key (today)"),
    (("vote",), "a vote signed under the identity key"),
    (("offer", "unseat", "cosign"), "roster events (founding, widening, removal) signed under identity keys"),
    (("accept",), "the joiner's acceptance signed under the identity key (CC 3.1.3.2: 'the invitee's only')"),
    (("ack",), "an acknowledgement of a row signed under the identity key"),
    (("open", "answer", "receipt", "landing"), "the rows of a window signed under identity keys"),
)


def overlays(mech="two_encap"):
    out = []
    for kinds, label in OVERLAYS:
        d = deniable_outside(mech, kinds)
        out.append((label, d["prove something"], d["not simulable"], d["coalitions"], d["example"]))
    return out


# =========================================================================================================
# 6. the key plane reads device names as names
# =========================================================================================================
def keyplane_indifference(depth=4):
    """keyplane.SeatShadow (who is entitled to a wrap, as seat rows) over every sequence of membership acts to `depth`,
    with identity names and with room-key names: the entitled sets are the same under the renaming."""
    import keyplane as KP
    dev_a = {"m1": ("a", "a2"), "m2": ("b",)}
    f = {"m1": "rk:y", "m2": "rk:x", "a": "rk:y/2", "a2": "rk:y/1", "b": "rk:x/1"}
    dev_b = {f[m]: tuple(f[d] for d in ds) for m, ds in dev_a.items()}
    evs = [("add", "m1"), ("add", "m2"), ("remove", "m1"), ("resign", "m2"), ("device_add", "a2"), ("device_revoke", "a2"), ("remove", "m2")]
    n = bad = 0
    def go(sa, sb, seated, d):
        nonlocal n, bad
        n += 1
        bad += rename(sa.entitled(dev_a), f) != sb.entitled(dev_b)
        if d == depth: return
        for kind, who in evs:
            if kind == "resign" and who not in sa.last: continue
            go(sa.act((kind, who), dev_a), sb.act((kind, f[who]), dev_b), seated, d + 1)
    go(KP.SeatShadow(), KP.SeatShadow(), None, 0)
    return {"sequences": n, "differ": bad}


# =========================================================================================================
# 7. the store's shape: one room key per device, persons counted through bindings the kernel WAITS on
# =========================================================================================================
def commit(room, key, person, nonce):
    """The commitment a seat row carries: a hash over the room, the room key, the person and fresh random bytes."""
    return "h:" + hashlib.sha256(repr((room, key, person, nonce)).encode()).hexdigest()[:24]


def opens(c, room, key, opening):
    """Does (person, nonce) open the commitment c of this key's seat row in this room?"""
    return opening is not None and commit(room, key, opening[0], opening[1]) == c


def person_tally(S, pr, held, commits=None):
    """A count of persons at one node. held: room key -> the opening (person, nonce) carried by the binding held and
    checked at this node (a bare person where no commitment is in play). Every seated key and every voting key must be
    bound: otherwise the answer is ('missing', the keys whose binding is not held). commits: room key -> the commitment
    its seat row carries; a binding whose opening does not open it is refused, and the key is then missing at that
    node."""
    if commits is not None:
        held = {k: o[0] for k, o in held.items() if opens(commits.get(k), ROOM, k, o)}
    past = lambda a, b: a in S.anc[b]
    mem = ST.members_at(S.Cs, past, ROOM, tuple(pr["names"]))
    C = CUT.Cut(S)
    votes = [v for v in K.sel(S.Cs, kind="vote") if pr["id"] in v["names"] and v["signer"] in mem and C.counts(v)]
    ok = dict(held)
    miss = frozenset(k for k in mem if k not in ok)
    if miss: return ("missing", miss)
    said = K.group(votes, "signer", "one", "choice")                # a key that says two things says nothing
    per = {}
    for k, c in said.items(): per.setdefault(ok[k], set()).add(c)
    return ("counted", sum(1 for v in per.values() if v == {"yes"}), sum(1 for v in per.values() if v == {"no"}), len(set(ok[k] for k in mem)))


def _fold_world(keys, votes):
    g = ST.offer("g", keys[0], tuple(keys), "member", "@", "self", cosigners=tuple(keys[1:]), room=ROOM)
    pr = R("pr", "proposal", keys[0], ("g",), room=ROOM)
    rows = [g, pr] + [R("t" + k, "vote", k, ("pr",), choice=c, room=ROOM) for k, c in zip(keys, votes) if c]
    return state_of(rows), pr


def waits_on_bindings():
    """Three persons, four device room keys, every way the keys can vote, and every pair of sets of bindings two member
    nodes can hold. Honest binders: each binding names the key's real person."""
    truth = {"k:A0": "A", "k:A1": "A", "k:B0": "B", "k:C0": "C"}
    keys = list(truth)
    subsets = [frozenset(c) for n in range(len(keys) + 1) for c in itertools.combinations(keys, n)]
    n = both = disagree = wrong_missing = outsider_counts = 0
    for votes in itertools.product(("yes", "no", None), repeat=len(keys)):
        S, pr = _fold_world(keys, votes)
        ans = {h: person_tally(S, pr, {k: truth[k] for k in h}) for h in subsets}
        outsider_counts += ans[frozenset()][0] != "missing"          # a node that holds no binding: a non-member
        for h1 in subsets:
            wrong_missing += (ans[h1][0] == "missing") != (len(h1) < len(keys)) or (ans[h1][0] == "missing" and ans[h1][1] != frozenset(keys) - h1)
            for h2 in subsets:
                n += 1
                if ans[h1][0] == ans[h2][0] == "counted":
                    both += 1
                    disagree += ans[h1] != ans[h2]
    return {"pairs of nodes": n, "both hold every binding": both, "disagree": disagree, "missing not as stated": wrong_missing,
            "a node with no binding counted": outsider_counts}


def colluding_binders():
    """Two members P and Q share one more room key S and bind it to P for node H1 and to Q for node H2. Both bindings
    verify (each is made under its maker's own KEM key). Do H1 and H2, each holding every binding, count the same?
    Then the same with the commitment in the seat row, which the binding must open."""
    keys = ["k:P", "k:Q", "k:S", "k:H1", "k:H2"]
    base = {"k:P": "P", "k:Q": "Q", "k:H1": "H1", "k:H2": "H2"}
    h1, h2 = dict(base, **{"k:S": "P"}), dict(base, **{"k:S": "Q"})
    nonce = {k: "n:" + k for k in keys}                             # fresh random bytes, one draw for each seat row
    truth = dict(base, **{"k:S": "P"})                              # the seat row of S commits to P
    commits = {k: commit(ROOM, k, truth[k], nonce[k]) for k in keys}
    o1, o2 = ({k: (p, nonce[k]) for k, p in h.items()} for h in (h1, h2))
    n = fork = fork_tag = stall_tag = 0
    first = None
    for votes in itertools.product(("yes", "no", None), repeat=len(keys)):
        S, pr = _fold_world(keys, votes)
        n += 1
        a, b = person_tally(S, pr, h1), person_tally(S, pr, h2)
        if a != b:
            fork += 1
            first = first or (dict(zip(keys, votes)), a, b)
        a, b = person_tally(S, pr, o1, commits), person_tally(S, pr, o2, commits)
        fork_tag += a[0] == b[0] == "counted" and a != b
        stall_tag += b[0] == "missing"
    return {"vote assignments": n, "the two honest nodes count differently": fork, "first": first,
            "with the commitment, count differently": fork_tag, "with the commitment, the node told otherwise waits": stall_tag,
            "the waiting node names the key": person_tally(S, pr, o2, commits)[1] == frozenset({"k:S"})}


# =========================================================================================================
# 8. the two variants: what the holder of rows can prove about persons, with no secret at all
# =========================================================================================================
OCCURRENCE = {"dev:%s%d" % (p, i): "id:" + p for p in ("A", "B", "C", "J") for i in (1, 2)}     # public: device key -> identity
OWNER = {"node:nA": "id:A", "node:nB": "id:B"}                                                 # public where the owner re-signed it wider
PUBLIC = dict(OCCURRENCE, **OWNER)


def proves(rows):
    """(persons proved to have acted in the room: a row of the room under their own key, a device key with a public
    occurrence, or a node key with a public owner; persons named by a row somebody else signed)."""
    person = lambda k: k if isinstance(k, str) and k.startswith("id:") else PUBLIC.get(k)
    acted, named = set(), set()
    def walk(x):
        if isinstance(x, str):
            if person(x): named.add(person(x))
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, (list, tuple, frozenset)):
            for v in x: walk(v)
    for r in rows:
        for k in ST.signers(r):
            if person(k): acted.add(person(k))
        walk({k: v for k, v in r.items() if k not in ("id", "names", "kind", "family", "room")})
    return frozenset(acted), frozenset(named - acted)


def carried(rows, rid):
    """What the door asks for when one row is carried elsewhere: the row and everything it names, and theirs."""
    S = CK.State(CK.kept(rows))
    return [r for r in rows if r["id"] == rid or r["id"] in S.anc[rid]]


def two_member_room(variant):
    """A and B, one device each. B speaks, A replies; the reply is carried into another group."""
    if variant == "attribution-only":
        seat, wrap_by, wrap_to, cust = ("id:A", "id:B"), ("dev:A1", "dev:B1"), ("dev:A1", "dev:B1"), ("node:nA", "node:nB")
    else:
        seat, wrap_by, wrap_to, cust = ("rk:q", "rk:n"), ("rk:q", "rk:n"), ("rk:q/kem", "rk:n/kem"), ("rk:q/node", "rk:n/node")
    g = ST.offer("g", seat[0], seat, "member", "@", "self", cosigners=seat[1:], room=ROOM)
    kg = [R("kg%d" % i, "grant", wrap_by[i], ("g",), to_dev=wrap_to[1 - i], room=ROOM) for i in (0, 1)]
    m1 = RT.msg("m1", "rk:n", "g", ("g",))
    m3 = RT.msg("m3", "rk:q", "g", ("g",), names=("m1",))
    cu = [R("cu%d" % i, "custody", cust[i], ("m1",), room=ROOM) for i in (0, 1)]
    return [g] + kg + [m1, m3] + cu


def variants():
    facts, table = [], []
    for v in ("attribution-only", "membership-private"):
        rows = two_member_room(v)
        S = state_of(rows)
        got = {}
        for holder, held in (("the holder of a carried reply", carried(rows, "m3")), ("a holder of every row of the room", rows)):
            acted, named = proves(held)
            got[holder] = (acted, named)
            table.append((v, "two members", holder, len(held), sorted(acted), sorted(named)))
        speech_concludes = bool(S.C["m1"]) and bool(S.C["m3"])
        table.append((v, "two members", "the kernel as it stands: does the speech conclude from rows alone", None, speech_concludes, None))
        if v == "attribution-only":
            facts.append(("attribution-only, two members: a reply carried into another group brings the founding row, which proves both members by their own signatures; "
                          "every row of speech is then one of two persons", got["the holder of a carried reply"][0] == frozenset({"id:A", "id:B"})))
            facts.append(("attribution-only: speech under a key the roster does not seat concludes nothing from rows; its standing would have to read the binding",
                          not speech_concludes))
        else:
            facts.append(("membership-private, two members: the same carried reply, and every row of the room, prove nothing about any person and name none",
                          all(not a and not n for a, n in got.values()) and speech_concludes))
    # the larger room: speech moved to room keys over an identity roster, against the room over room keys
    f = {ID[p]: VOICE[p] for p in ID}
    attr = [dict(r, signer=f[r["signer"]]) if r["kind"] == "msg" else r for r in room_world(ID)]
    acted, named = proves(carried(attr, "m8"))
    table.append(("attribution-only", "four members", "the holder of the reply m8 carried elsewhere", len(carried(attr, "m8")), sorted(acted), sorted(named)))
    facts.append(("attribution-only, four members: the carried reply drags 15 rows of roster ancestry and proves all four members, each by its own signature on a roster row",
                  len(acted) == 4 and len(carried(attr, "m8")) == 16))
    priv = dict(VOICE, C2="rk:y")
    base = room_world(priv)
    sets = [base] + list(closed_subsets(base, 17))
    leak = sum(1 for rows in sets if any(proves(rows)))
    table.append(("membership-private", "four members", "every closed set of up to 17 rows of the room, and the room", len(sets), "%d of %d sets prove or name a person" % (leak, len(sets)), None))
    facts.append(("membership-private: of %d sets of rows of the room, none proves or names a person" % len(sets), leak == 0))
    # re-admission under a fresh key (the store's rule): the kernel's answers
    S = state_of(base)
    Q, st = ST.Seats(S), CUT.Cut(S).all()
    mem = Q.holders("member", ROOM)
    facts.append(("re-admission under a FRESH room key: the new key is seated and counted, the old key is not seated, the old key's row concurrent with the removal stays void, "
                  "and no row links the two keys", "rk:y" in mem and VOICE["C"] not in mem and st["m7"] == "counts" and st["m4"] == "void"
                  and not any(VOICE["C"] in repr(r) and "rk:y" in repr(r) for r in base)))
    # custody: a claim under a node key whose owner is public, against a claim under a key made for the room
    facts.append(("custody, as today: a holding claim under a node key names that node's owner to any holder of the claim",
                  proves([r for r in two_member_room("attribution-only") if r["kind"] == "custody"])[0] == frozenset({"id:A", "id:B"})))
    facts.append(("custody under a key the node holds for the room only: the claim names no person",
                  not any(proves([r for r in two_member_room("membership-private") if r["kind"] == "custody"]))))
    # the node's key for the room is owned inside the room: an owner seat conferred by the member's room key, as a row of the room
    g = ST.offer("g", "rk:q", ("rk:q", "rk:n"), "member", "@", "self", cosigners=("rk:n",), room=ROOM)
    ob = ST.offer("ob", "rk:q/node", "rk:q", "owner", "rk:q/node", "self", ("g",), cosigners=("rk:q",), room=ROOM)
    T = state_of([g, ob])
    facts.append(("the owner of a node's room key is read inside the room: an owner seat signed under the member's room key and the node's room key, a row of the room",
                  ST.Seats(T).one("owner", "rk:q/node") == "rk:q" and not any(proves([g, ob]))))
    return facts, table


# =========================================================================================================
# 9. the room declares itself
# =========================================================================================================
KINDS = ("self", "family", "community")
BY_FUNCTION = ("designated_body", "infrastructure", "trust_root_grade")      # bodies whose rosters others read


def founding(kind, membership=None, function=None):
    r = {"id": "g", "kind": "offer", "group_kind": kind}
    if membership is not None: r["membership"] = membership
    if function is not None: r["function"] = function
    return r


def found(kind, choice=None, function=None):
    """What a founder under the rule writes. A community says `private` unless its founders chose `public`; a body that
    is public by function says `public`; a self room and a family carry no declaration."""
    if kind != "community": return founding(kind)
    return founding(kind, "public" if (choice == "public" or function in BY_FUNCTION) else "private", function)


def admissible_founding(r):
    """The door on a founding row, read from the row alone."""
    m = r.get("membership")
    if m not in (None, "private", "public"): return False
    if r["group_kind"] != "community": return m is None                  # a self room and a family do not declare
    return not (r.get("function") in BY_FUNCTION and m != "public")      # absent reads public, so only `private` is refused here


def membership(r, declarations=()):
    """How the room is seated, as a fold: the founding row's member, an absent member reading `public`, then each later
    declaration in turn. A declaration of `public` is taken; one of `private` over a public room concludes nothing."""
    m = r.get("membership", "public") if r["group_kind"] == "community" else "public"
    for d in declarations:
        if d == "public": m = "public"
    return m


def seated_by(r, declarations=()):
    return "room keys" if membership(r, declarations) == "private" else "identity keys"


def admissible_seat(r, seat_row, declarations=()):
    """A seat row of a private room carries a commitment; one without it is refused. A public room asks for none."""
    return seated_by(r, declarations) == "identity keys" or str(seat_row.get("commit", "")).startswith("h:")


def declaration():
    facts = []
    rows = [founding(k, m, f) for k in KINDS for m in (None, "private", "public") for f in (None,) + BY_FUNCTION]
    ok = [r for r in rows if admissible_founding(r)]
    facts.append(("an absent declaration reads public: every admissible founding row with no `membership` member is seated by identity keys (%d rows)"
                  % sum(1 for r in ok if "membership" not in r), all(seated_by(r) == "identity keys" for r in ok if "membership" not in r)))
    facts.append(("a self room and a family are seated by identity keys, and a founding row of either that declares is refused",
                  all(seated_by(r) == "identity keys" for r in ok if r["group_kind"] != "community")
                  and not any(admissible_founding(founding(k, m)) for k in ("self", "family") for m in ("private", "public"))))
    facts.append(("a community founded under the rule is private unless its founders chose public, and what the founder writes is admissible",
                  seated_by(found("community")) == "room keys" and seated_by(found("community", "public")) == "identity keys"
                  and all(admissible_founding(found(k, c, f)) for k in KINDS for c in (None, "public") for f in (None,) + BY_FUNCTION)))
    facts.append(("a body that is public by function declares public: `private` on a designated body, an infrastructure community or a trust-root-grade community is refused",
                  all(not admissible_founding(founding("community", "private", f)) and seated_by(found("community", None, f)) == "identity keys" for f in BY_FUNCTION)))
    n = back = 0
    for r in ok:
        for k in range(0, 5):
            for ds in itertools.product(("private", "public"), repeat=k):
                trail = [membership(r, ds[:i]) for i in range(k + 1)]
                n += 1
                back += any(a == "public" and b == "private" for a, b in zip(trail, trail[1:]))
    facts.append(("private to public and never back: %d sequences of up to four later declarations over every admissible founding row, %d go from public to private" % (n, back),
                  back == 0 and membership(founding("community", "private"), ("public",)) == "public"))
    naive = lambda r, ds: ([r.get("membership", "public")] + list(ds))[-1]                    # MUTATION: the last declaration wins
    facts.append(("a reader under which the last declaration wins is caught (a public room would turn private)",
                  naive(founding("community", "public"), ("private",)) == "private" and membership(founding("community", "public"), ("private",)) == "public"))
    c = commit(ROOM, "rk:q", "A", "n1")
    priv, pub = founding("community", "private"), founding("community")
    facts.append(("a seat row of a private room without a commitment is refused; with one it is taken; a public room asks for none; "
                  "once the room is public the same row is taken",
                  not admissible_seat(priv, {"signer": "rk:q"}) and admissible_seat(priv, {"signer": "rk:q", "commit": c})
                  and admissible_seat(pub, {"signer": "id:A"}) and admissible_seat(priv, {"signer": "id:A"}, ("public",))))
    return facts


# =========================================================================================================
# 10. the commitment, the planned binding, the verdict, and the limits a run can show
# =========================================================================================================
def commitment_and_limits():
    facts = []
    persons = PERSONS + ("X", "D")
    c = commit(ROOM, "rk:n", "B", "n:fresh")
    # --- the commitment -----------------------------------------------------------------------------------
    facts.append(("the commitment is opened by the person and the bytes it was made with, and by nothing else tried: another person, another key, another room, other bytes",
                  opens(c, ROOM, "rk:n", ("B", "n:fresh")) and not any(opens(c, r, k, (p, n)) for r in (ROOM, "g2") for k in ("rk:n", "rk:q") for p in persons
                                                                         for n in ("n:fresh", "n:other", "") if (r, k, p, n) != (ROOM, "rk:n", "B", "n:fresh"))))
    guess = lambda cm, nonces: {p for p in persons for n in nonces if opens(cm, ROOM, "rk:n", (p, n))}
    facts.append(("a holder of the seat row who has no opening learns no person by trying every person; with no fresh bytes in the hash it would name the person at once (the mutation)",
                  guess(c, ("",)) == set() and guess(commit(ROOM, "rk:n", "B", ""), ("",)) == {"B"}))
    seat = {"id": "s", "kind": "offer", "signer": "rk:n", "names": (), "commit": c, "room": ROOM}
    facts.append(("the seat row with its commitment names and proves no person to a holder of rows", not any(proves([seat]))))
    # an opening shown outside: any party can make a key and commit it to P, so the opening says who the key's maker NAMED
    frame = commit(ROOM, "rk:forged", "B", "n:x")
    facts.append(("an opening handed outside the room proves nothing about the person: a party that is not B makes a key whose seat row commits to B, and it opens to B",
                  opens(frame, ROOM, "rk:forged", ("B", "n:x"))))
    f_bad = binding("two_encap", "B", "rk:forged", "A", opening=("B", "n:x"))
    facts.append(("inside the room that key gets nowhere: the commitment opens, and the confirmation cannot be made by anyone but B and the addressee",
                  not can_make(("C", "J", "X"), f_bad)))
    # --- the planned binding, as two encapsulations ----------------------------------------------------------
    honest = binding("two_encap", "B", "rk:n", "A", opening=("B", "n:fresh"))
    facts.append(("two encapsulations, honest addressee: the addressee is convinced, could have produced the confirmation itself, and an outsider "
                  "given every secret of the addressee is convinced of nothing",
                  convinced("A", honest) and can_make(("A",), honest) and not convinced("X", honest, given=frozenset({"A"})) and not transferable(honest, persons)))
    facts.append(("a binding is taken only when it opens the seat row's commitment: the same confirmation with another person's opening, or other bytes, is refused",
                  opens(c, ROOM, "rk:n", honest["opening"]) and not opens(c, ROOM, "rk:n", ("A", "n:fresh")) and not opens(c, ROOM, "rk:n", ("B", "n:other"))))
    facts.append(("a binding made for one addressee is not accepted by another member's verifier", not accepts("J", honest) and accepts("A", honest)))
    live = binding("two_encap", "B", "rk:n", "A", challenge_by="X")
    facts.append(("LIMIT, run: a member cooperating live with an outsider. The outsider forms the challenge and the member relays it; the outsider is then convinced",
                  convinced("X", live, given=frozenset({"A"}))))
    obl = binding("two_encap", "B", "rk:n", "A", oblivious=True)
    facts.append(("LIMIT, symbolic: IF an addressee can form a challenge whose secret it cannot be shown to know, the confirmation is transferable. "
                  "Whether it can, with the pinned key exchange, is the conjecture",
                  transferable(obl, persons)))
    # --- a verdict ----------------------------------------------------------------------------------------
    vd = lambda k: R("vd", "verdict", k, ("m1",), room=ROOM, target="m1")
    facts.append(("a duty holder's verdict signed under its room key names and proves no person; signed under its identity key it proves the duty holder acted in the room",
                  not any(proves([vd("rk:D")])) and proves([vd("id:D")])[0] == frozenset({"id:D"})))
    # --- the limits a run can show ---------------------------------------------------------------------------
    nm = dict(VOICE, C2="rk:y")
    rows = room_world(nm)
    tie = {"id": "tie", "kind": "self_binding", "signer": "id:B", "names": (), "binds": VOICE["B"]}       # B's own signed row, outside the room
    tied = {r["id"] for r in rows if r["signer"] == tie["binds"]}
    facts.append(("LIMIT, run: one signed row by the person outside the room tying the room key to themself makes every row under that key provable (%d rows), and no other member's" % len(tied),
                  proves([tie])[0] == frozenset({"id:B"}) and len(tied) > 3 and not any(proves(rows))))
    old = room_world(ID)
    facts.append(("LIMIT, run: a room already signed under identity keys stays provable (all four members), and a later declaration of private changes nothing",
                  len(proves(old)[0]) == 4 and membership(founding("community"), ("private",)) == "public"))
    S = state_of(rows)
    past = lambda a, b: a in S.anc[b]
    joins = [r for r in rows if r["kind"] == "offer" and r.get("scope") == "member" and r["id"] != "g"]
    facts.append(("LIMIT, run: a joining is visible to whoever holds the rows. Each of %d admissions seats a key that the head it names does not seat, "
                  "read from the rows with no secret" % len(joins),
                  len(joins) == 3 and all(j["to"][0] not in ST.members_at(S.Cs, past, ROOM, j["head"]) and S.C[j["id"]] for j in joins)))
    f_c = binding("two_encap", "A", VOICE["A"], "C")
    facts.append(("LIMIT, run: a removed member keeps the bindings it was given (removal ends reading, not what it was convinced of)",
                  VOICE["C"] not in ST.Seats(S).holders("member", ROOM) and convinced("C", f_c)))
    cust = [r for r in two_member_room("membership-private") if r["kind"] == "custody"]
    facts.append(("LIMIT, run: a custody claim still reaches a node. Under a room key it names no person, and it is still one claim for each holding node (%d)" % len(cust),
                  len(cust) == 2 and not any(proves(cust)) and len({r["signer"] for r in cust}) == 2))
    facts.append(("LIMIT, run: an order naming a person finds nothing in the rows. No row of the room, and no set of them, names or proves B, C or J", not any(proves(rows))))
    return facts


# =========================================================================================================
# 11. detection in a private room: the detector's seat is conferred inside the room
# =========================================================================================================
def detection_in_room():
    """A and B found the room as its two duty holders (CC 4.5.4). A's node holds a room key, owned inside the room by A's
    room key. The duty holders enable a list: that act, counted as a conferral of a duty seat (a strict majority of the
    holders, never fewer than two voices where there are two), seats the node's room key as a detector for the list,
    over the room. The node signs a detection, the owner signs the notice."""
    facts = []
    A, B, NODE, LIST = "rk:q", "rk:n", "rk:q/node", "detect:list1"
    g = ST.offer("g", A, (A, B), "duty", "@", "self", cosigners=(B,), room=ROOM)
    md = R("md", "record", A, ("g",), room=ROOM, duties=("moderate",))
    ob = ST.offer("ob", NODE, A, "owner", NODE, "self", ("g",), cosigners=(A,), room=ROOM)
    en = ST.offer("en", A, NODE, LIST, "g", "group", ("md", "ob"), head=("g",), policy="duty_confer", counted="duty",
                  cosigners=(B, NODE), room=ROOM)
    det = R("det", "detection", NODE, ("en",), room=ROOM, offered_by=B, list="list1")
    note = R("note", "notice", A, ("det", "ob"), room=ROOM, target="det")
    rows = [g, md, ob, en, det, note]
    seats = lambda rs: ST.Seats(state_of(rs))
    Q = seats(rows)
    facts.append(("enabling the list seats the room's node as its detector: an ordinary seat, conferred by the count of the room's duty holders and held by the node's room key",
                  Q.holders(LIST, "g") == frozenset({NODE}) and Q.stands(NODE, LIST, "g", root=("group", "g"))))
    facts.append(("the seat is the room's: no outside root is on the walk to it; the same enabling signed by one duty holder of two alone, "
                  "or by a key that holds no duty seat, seats nobody",
                  not Q.stands(NODE, LIST, "g", root="root:outside")
                  and seats([g, md, ob, dict(en, cosigners=(NODE,))]).holders(LIST, "g") == frozenset()
                  and seats([g, md, ob, dict(en, signer="rk:z", cosigners=(NODE,))]).holders(LIST, "g") == frozenset()))
    def admitted(rs):
        """The door on the notice: its signer owns, by the binding in the room, the key that signed the detection it
        names, and that key held the detector's seat."""
        Qs = seats(rs)
        d = next(r for r in rs if r["id"] == "det")
        n = next(r for r in rs if r["id"] == "note")
        return Qs.stands(d["signer"], LIST, "g") and Qs.one("owner", d["signer"]) == n["signer"]
    facts.append(("the notice is admitted when its signer owns the node's room key by the binding in the room; a notice by another member is not, "
                  "and neither is one where that binding is absent",
                  admitted(rows) and not admitted([g, md, ob, en, det, dict(note, signer=B)]) and not admitted([g, md, en, det, dict(note, names=("det",))])))
    facts.append(("the owner-binding of the node's room key is a row: any holder of the rows reads the owner from them with no binding of a voice, and reads a room key",
                  ST.Seats(state_of([g, ob])).one("owner", NODE) == A))
    facts.append(("the whole record (the binding, the enabling, the detection, the notice) names and proves no person", not any(proves(rows))))
    pub = [dict(en, to=("node:nA",), on=ST._slots("node:nA", LIST, "g")), dict(det, signer="node:nA")]
    facts.append(("a detector's seat tied to the node's public key would name the node's owner to any holder of the detection",
                  proves(pub)[0] == frozenset({"id:A"}) or "id:A" in proves(pub)[1]))
    wd = in_room(ST.withdraw("wd", A, "en", ("en",)))
    xw = ST.unseat("xw", A, NODE, LIST, "g", "group", ("en",), head=("g",), policy="duty_withdraw", counted="duty", cosigners=(B,), room=ROOM)
    facts.append(("the enabling is revocable: withdrawn by the count of the room's duty holders, the node holds no detector's seat; "
                  "one holder's withdrawal of its own signature ends nothing (CC 4.5.4)",
                  seats(rows + [xw]).holders(LIST, "g") == frozenset() and seats(rows + [wd]).holders(LIST, "g") == frozenset({NODE})))
    before, after = ST.Seats(state_of([g, md, ob, en])), ST.Seats(state_of(rows))
    facts.append(("a detection is a claim and no verdict: with the detection and the notice held, no seat in the room has changed",
                  before.snapshot() == after.snapshot()))
    return facts
