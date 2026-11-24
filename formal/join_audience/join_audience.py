"""
join_audience.py: who holds what when people join a room with unannounced devices, and the allow list per key.

The vocabulary is formal/audience_view's: a node's VIEW is the rows it holds, a row has an AUDIENCE, a row is SERVED
to a node only inside its audience, and a STRANGER is a node with no owner the server can resolve. This file adds
the steps that move rows: the contact exchange, the invitation, its answer, the widening, the cohort's ordinary
delivery, one sealed write, and a later announce.

    node        a device of a person ("A1", "B2"), or the stranger relay "Z". The owner of "B2" is "B".
    row         a tuple. Its placement decides its audience.
        ("bind", d, "self")            the owner-binding of node d as first written           CC 3.2
        ("bind", d, "room")            the same binding re-signed at the room                 CC 3.2
        ("bind", d, "fed")             the same binding re-signed at federation (announced)   CC 3.2, 5.4.6
        ("bind", d, ("contact", Q))    the same binding placed addressed to the contact Q     CC 5.4.6
        ("occ", d)                     the occurrence of the owner's roster key on device d   CC 3.3.6, 5.4.6
        ("proj", P)                    what the room is told of P's lists (repair only, not in the text)
        ("roster0",) ("seat", P)       the room's roster: its founding version and a widening that seats P
        ("prop", J) ("acc", J)         the membership proposal for J and J's acceptance
        ("content",)                   the bytes of one write sealed under the room's content key
        ("wraps", targets)             the wraps of that write's key, one per device in `targets`
        ("env", kind, J, rows, openers) a sealed envelope: opaque to every node not in `openers`

A federation-placed row is public: every node holds it from the instant it exists (pub()). Every other row is held
only where a step put it. Holdings only grow.

What a server reads. A server resolves a node's owner ONLY through an owner-binding it holds for that node, and a
person's seat ONLY through the roster rows it holds. `Rules.resolve` says which bindings count for a room's
audience: "placed" (the binding placed at the room, at federation, or the server's own sibling binding at self) or
"any" (a binding addressed to the server as a contact as well).

The rules are data (Rules). A planted break is one field of Rules changed.
"""
from collections import namedtuple

RELAY = "Z"


def owner(node):
    return None if node == RELAY else node[0]


class World(object):
    """A bounded world: who exists, who founded the room, who invites whom, who may exchange a contact, who is
    announced from the start, who may announce later, each device's two lists, the device that writes, and the
    device a joiner answers on."""

    def __init__(self, name, people, founders=("A",), invites=(), contacts=(), announced=(), may_announce=(),
                 lists=None, author=None, expect_join=True, answer_on=None):
        self.name = name
        self.people = dict(people)                       # person -> number of devices
        self.devices = tuple(p + str(i + 1) for p in sorted(self.people) for i in range(self.people[p]))
        self.nodes = self.devices + (RELAY,)
        self.idx = dict((n, i) for i, n in enumerate(self.nodes))
        self.founders = frozenset(founders)
        self.invites = tuple(invites)                    # (joiner person, inviting device)
        self.contacts = tuple(frozenset(c) for c in contacts)
        self.announced = frozenset(announced)
        self.may_announce = frozenset(may_announce)
        self.lists = dict(lists or {})                   # device -> (node key's list names the room, roster key's)
        self.author = author
        self.expect_join = expect_join
        self.answer_on = dict(answer_on or {})           # person -> the device that person answers on (else any)

    def devs(self, person):
        return tuple(d for d in self.devices if d[0] == person)

    def nl(self, d):
        return self.lists.get(d, (True, True))[0]

    def rl(self, d):
        return self.lists.get(d, (True, True))[1]

    def kept_off(self, d):
        return not self.nl(d) and not self.rl(d)


_RULES = dict(
    resolve="placed",            # which bindings resolve a node into a room's audience: "placed" | "any"
    answer_binding="device",     # the answer carries the binding of: the answering "device" | "all" devices | "none"
    invitation_roster=False,     # PLANT: the invitation carries the roster
    link_all_bindings=False,     # PLANT: a link hands the peer every binding of the node, not only its allegiance rows
    occ_public=False,            # PLANT: an occurrence is a public row whatever its bindings
    serve_needs_seat=True,       # PLANT (False): a room row is served on the binding alone
    serve_needs_binding=True,    # PLANT (False): a room row is served on the node's own word of who owns it
    node_list=True,              # PLANT (False): the node key's list is read at neither end
    roster_list=True,            # PLANT (False): the roster key's list is read at neither end
    refusal="device",            # a write is refused when the writing "device" is kept off | CC 5.2's "letter"
    projection="none",           # how a foreign sealer learns a roster key's list: "none" | "closed" | "open"
    announce_replaces=False,     # PLANT: a binding re-signed at federation replaces the row placed at the room
    contact_public=False,        # PLANT: a row addressed to a contact is served to anyone once its owner announces
    strict_reply=False,          # READING: the answer is addressed only to a node the joiner holds a binding of
    node_list_reach="bytes",     # READING: the node key's list withholds "bytes" | puts the node outside the "audience"
    sibling_room_serve=True,     # READING (False): a server's own sibling binding at self resolves no room audience
    grain="row",                 # one delivery moves one "row" | every row the receiver may be served ("batch")
)
Rules = namedtuple("Rules", sorted(_RULES))
RULES = Rules(**_RULES)

State = namedtuple("State", "H announced contacts flags")


# ---------------------------------------------------------------- holdings

def pub(w, st, rules):
    """The rows every node holds because they are placed at federation."""
    out = set()
    for d in w.devices:
        if owner(d) in st.announced:
            out.add(("bind", d, "fed"))
            out.add(("occ", d))
        elif rules.occ_public:
            out.add(("occ", d))
    return out


def view(w, st, n, rules, _pub=None):
    """A node's view: the rows it holds."""
    return st.H[w.idx[n]] | (pub(w, st, rules) if _pub is None else _pub)


def created(st):
    out = set()
    for h in st.H:
        out |= h
    return out


def initial(w, rules):
    H = []
    for n in w.nodes:
        h = set()
        p = owner(n)
        if p is not None:
            # a person's own devices hold the self plane of that person from the start (CC 3.2 "Adding a device")
            for d in w.devs(p):
                h.add(("bind", d, "self"))
                h.add(("occ", d))
            if rules.projection != "none":
                h.add(("proj", p))
            if p in w.founders:
                h.add(("roster0",))
                for d in w.devs(p):
                    h.add(("bind", d, "room"))
        H.append(frozenset(h))
    return State(tuple(H), w.announced, frozenset(), frozenset())


def _put(w, st, changes):
    H = list(st.H)
    for n, rows in changes.items():
        H[w.idx[n]] = H[w.idx[n]] | frozenset(rows)
    return st._replace(H=tuple(H))


# ---------------------------------------------------------------- what a server reads

def resolve(w, r, V, kinds):
    """The owner of node r as a server with view V reads it: through a binding of r it holds, of a kind in `kinds`."""
    for row in V:
        if row[0] == "bind" and row[1] == r:
            pl = row[2]
            kind = pl if isinstance(pl, str) else "contact"
            if kind in kinds:
                return owner(r)
    return None


ANY = ("self", "room", "fed", "contact")


def seated(w, p, V):
    """Whether person p holds a seat, as a holder of view V reads the roster."""
    return (("roster0",) in V and p in w.founders) or ("seat", p) in V


def room_kinds(rules, s, r):
    """The kinds of binding that resolve node r into a room's audience at server s."""
    kinds = ["room", "fed"]
    if rules.sibling_room_serve and owner(s) == owner(r):
        kinds.append("self")                             # the server's own sibling: its binding is held at self
    if rules.resolve == "any":
        kinds.append("contact")
    return tuple(kinds)


def in_room_audience(w, rules, s, r, V):
    """Is node r in the room's audience, as server s with view V reads it (CC 5.2, CC 6.1.5.3)."""
    if not rules.serve_needs_binding:
        p = owner(r) if r != RELAY else sorted(w.founders)[0]     # the node's own word; the relay lies
    else:
        p = resolve(w, r, V, room_kinds(rules, s, r))
    if p is None:
        return False
    if rules.serve_needs_seat and not seated(w, p, V):
        return False
    if rules.node_list_reach == "audience" and rules.node_list and r != RELAY and not w.nl(r):
        # read by a server that knows the list: the owner's own node, or one told by the projection
        if owner(s) == owner(r) or (rules.projection != "none" and ("proj", owner(r)) in V):
            return False
    return True


def placements_of_person(w, st, rules, p, V):
    """Where the bindings of p's nodes are placed, as far as the holder of V holds them (CC 5.4.6)."""
    out = set()
    for row in V:
        if row[0] == "bind" and owner(row[1]) == p:
            if rules.announce_replaces and row[2] == "room" and p in st.announced:
                continue
            out.add(row[2])
    return out


def in_placement(w, rules, s, r, V, pl, st):
    if pl == "fed":
        return True
    if pl == "self":
        return False
    if pl == "room":
        return in_room_audience(w, rules, s, r, V)
    q = pl[1]
    return resolve(w, r, V, ANY) == q


def audience(w, rules, st, s, r, row, V):
    """May server s, whose view is V, serve `row` to node r?"""
    k = row[0]
    if k == "env":
        return False
    if k in ("bind", "occ", "proj"):
        p = owner(row[1]) if k != "proj" else row[1]
        if resolve(w, r, V, ANY) == p and owner(r) == p:
            return True                                  # the owner's own node: the self plane
        if k == "bind":
            pl = row[2]
            if rules.announce_replaces and pl == "room" and p in st.announced:
                return False
            if rules.contact_public and not isinstance(pl, str) and p in st.announced:
                return True
            return in_placement(w, rules, s, r, V, pl, st)
        pls = placements_of_person(w, st, rules, p, V)
        if k == "proj":
            pls = pls & {"room"}
        return any(in_placement(w, rules, s, r, V, pl, st) for pl in pls)
    if k == "wraps":
        return in_room_audience(w, rules, s, r, V)
    return in_room_audience(w, rules, s, r, V)


def holds_decision(w, rules, r, row):
    """The receiver's own hold decision (CC 6.1.5.3): a node knows its own two lists."""
    if r == RELAY:
        return True
    if rules.node_list and not w.nl(r):
        if row[0] == "content":
            return False
        if rules.node_list_reach == "audience" and row[0] in ("roster0", "seat", "prop", "acc", "wraps"):
            return False                                 # "pulls nothing for it"
    if row[0] == "wraps" and rules.roster_list and r in row[1] and not w.rl(r):
        return False
    return True


def allegiance_rows(w, rules, n, V):
    """What a link hands the peer by virtue of the link (CC 5.3.4): the binding only where placed at federation."""
    out = set()
    for row in V:
        if row[0] == "bind" and row[1] == n:
            if row[2] == "fed" or rules.link_all_bindings:
                out.add(row)
    return out


# ---------------------------------------------------------------- the steps

def sealer_wraps(w, rules, d, V):
    """The devices a sealer on device d wraps the content key to, over the roster and occurrences it holds."""
    me = owner(d)
    out = set()
    for row in V:
        if row[0] != "occ":
            continue
        t = row[1]
        p = owner(t)
        if not seated(w, p, V):
            continue
        if rules.roster_list:
            if p == me:
                if not w.rl(t):
                    continue                             # the owner's own lists are held at self
            elif rules.projection == "closed":
                if ("proj", p) not in V or not w.rl(t):
                    continue                             # no projection held, no wrap
            elif rules.projection == "open":
                if ("proj", p) in V and not w.rl(t):
                    continue                             # a wrap unless a held projection withholds it
        out.add(t)
    return frozenset(out)


def write_refused(w, rules, d, V):
    if rules.refusal == "device":
        return (rules.node_list and not w.nl(d)) or (rules.roster_list and not w.rl(d))
    # CC 5.2 by the letter: refused only when the author has no wrap target at all
    return not any(owner(t) == owner(d) for t in sealer_wraps(w, rules, d, V))


def steps(w, rules, st):
    """Every step enabled in st, as (label, next state). `stats` premises are counted by the caller."""
    P = pub(w, st, rules)
    V = dict((n, st.H[w.idx[n]] | P) for n in w.nodes)
    made = created(st)

    # contact exchange: by the owner's own hand, node code by node code (CC 5.4.6). Atomic.
    for c in w.contacts:
        if c in st.contacts:
            continue
        a, b = sorted(c)
        da, db = w.devs(a)[0], w.devs(b)[0]
        ba, bb = ("bind", da, ("contact", b)), ("bind", db, ("contact", a))
        to_b = {ba} | set(r for r in st.H[w.idx[da]] if r[0] == "occ" and owner(r[1]) == a)
        to_a = {bb} | set(r for r in st.H[w.idx[db]] if r[0] == "occ" and owner(r[1]) == b)
        nxt = _put(w, st, {da: to_a | {ba}, db: to_b | {bb}})
        yield ("contact %s-%s" % (a, b), nxt._replace(contacts=st.contacts | {c}))

    # announce: the owner re-signs the binding of each node at federation (CC 3.2). The rows placed stand.
    for p in sorted(w.may_announce - st.announced):
        yield ("announce %s" % p, st._replace(announced=st.announced | {p}))

    # the invitation: a sealed envelope carrying the proposal and the inviter's occurrences (CC 3.1.3.2)
    for j, a in w.invites:
        if ("prop", j) in made or not seated(w, owner(a), V[a]):
            continue
        openers = frozenset(d for d in w.devs(j) if ("occ", d) in V[a])
        if not openers:
            continue                                     # sealed to a key the inviter already holds
        rows = {("prop", j)} | set(r for r in V[a] if r[0] == "occ" and owner(r[1]) == owner(a))
        if rules.projection != "none":
            rows.add(("proj", owner(a)))
        if rules.invitation_roster:
            rows |= set(r for r in V[a] if r[0] in ("roster0", "seat"))
        env = ("env", "invitation", j, frozenset(rows), openers)
        yield ("invite %s by %s" % (j, a), _put(w, st, {a: {("prop", j)}, RELAY: {env}}))

    # opening an envelope: only a device whose key it is sealed to
    for env in st.H[w.idx[RELAY]]:
        if env[0] != "env":
            continue
        for d in sorted(env[4]):
            new = env[3] - V[d]
            if new:
                yield ("open %s for %s at %s" % (env[1], env[2], d), _put(w, st, {d: new}))

    # the answer: a sealed envelope carrying the acceptance, the joiner's occurrences and its binding at the room
    for j, a in w.invites:
        if ("acc", j) in made:
            continue
        for d in w.devs(j):
            if ("prop", j) not in V[d] or w.answer_on.get(j, d) != d:
                continue
            inviter = owner(a)
            openers = frozenset(x for x in w.devs(inviter) if ("occ", x) in V[d])
            if not openers:
                continue
            if rules.strict_reply and not any(r[0] == "bind" and owner(r[1]) == inviter for r in V[d]):
                continue
            binds = set()
            if rules.answer_binding == "device":
                binds = {("bind", d, "room")}
            elif rules.answer_binding == "all":
                binds = set(("bind", x, "room") for x in w.devs(j) if ("bind", x, "self") in V[d])
            placed = {("bind", d, "room")} | binds       # the binding is re-signed either way; the plant is carriage
            rows = {("acc", j)} | binds | set(r for r in V[d] if r[0] == "occ" and owner(r[1]) == j)
            if rules.projection != "none":
                rows.add(("proj", j))
            env = ("env", "answer", j, frozenset(rows), openers)
            yield ("answer %s at %s" % (j, d), _put(w, st, {d: {("acc", j)} | placed, RELAY: {env}}))

    # the widening: the count is one step of a seated member that holds the proposal and the acceptance
    for j, _a in w.invites:
        if ("seat", j) in made:
            continue
        for d in w.devices:
            if seated(w, owner(d), V[d]) and ("prop", j) in V[d] and ("acc", j) in V[d]:
                yield ("widen %s at %s" % (j, d), _put(w, st, {d: {("seat", j)}}))

    # one write sealed under the room's content key (CC 5.2)
    d = w.author
    if d is not None and "written" not in st.flags and "refused" not in st.flags and seated(w, owner(d), V[d]):
        if write_refused(w, rules, d, V[d]):
            yield ("write refused at %s" % d, st._replace(flags=st.flags | {"refused"}))
        else:
            rows = {("content",), ("wraps", sealer_wraps(w, rules, d, V[d]))}
            saw = set(("sealer_saw", p) for p in w.people if seated(w, p, V[d]))
            yield ("write at %s" % d, _put(w, st, {d: rows})._replace(flags=st.flags | {"written"} | saw))

    # a link: the node hands its peer its allegiance rows, and nothing else by virtue of the link (CC 5.3.4)
    for n in w.devices:
        for peer in w.nodes:
            if peer == n:
                continue
            new = allegiance_rows(w, rules, n, st.H[w.idx[n]]) - V[peer]
            if new:
                yield ("link %s to %s" % (n, peer), _put(w, st, {peer: new}))

    # ordinary delivery: a server serves a row to a node inside the row's audience, as the server reads it
    for s in w.nodes:
        Hs = st.H[w.idx[s]]
        for r in w.nodes:
            if r == s:
                continue
            batch = [row for row in Hs if row not in V[r] and audience(w, rules, st, s, r, row, V[s])
                     and holds_decision(w, rules, r, row)]
            if not batch:
                continue
            if rules.grain == "batch":
                yield ("serve %s to %s (%d rows)" % (s, r, len(batch)), _put(w, st, {r: batch}))
            else:
                for row in batch:
                    yield ("serve %s to %s %r" % (s, r, row[:3]), _put(w, st, {r: [row]}))


def link_withholds(w, rules, st):
    """How many (node, peer) links in st leave a binding not placed at federation behind: the premise of the link rule."""
    n_ = 0
    for n in w.devices:
        h = st.H[w.idx[n]]
        if any(r[0] == "bind" and r[1] == n and r[2] != "fed" for r in h):
            n_ += len(w.nodes) - 1
    return n_


# ---------------------------------------------------------------- the properties, read on one state

def truth(w, st):
    made = created(st)
    seats = set(w.founders) | set(r[1] for r in made if r[0] == "seat")
    placed = set(owner(r[1]) for r in made if r[0] == "bind" and r[2] == "room")
    return made, seats, placed


def contacts_of(st, p):
    out = set()
    for c in st.contacts:
        if p in c:
            out |= set(c) - {p}
    return out


def safety(w, rules, st):
    """The names of the safety properties broken in st, with one line each."""
    bad = []
    made, seats, placed = truth(w, st)
    P = pub(w, st, rules)
    inviter_of = dict((j, owner(a)) for j, a in w.invites)
    for n in w.nodes:
        o = owner(n)
        for row in st.H[w.idx[n]] | P:
            k = row[0]
            if n == RELAY and k != "env" and not (k == "bind" and row[2] == "fed") and \
                    not (k == "occ" and owner(row[1]) in st.announced):
                bad.append(("D.relay", "the relay holds %r" % (row[:3],)))
            if k == "bind" and row[2] == "room" and o not in seats | {owner(row[1])}:
                bad.append(("D.room_binding", "%s holds %r" % (n, row)))
            if k == "bind" and row[2] == "self" and o != owner(row[1]):
                bad.append(("D.self_binding", "%s holds %r" % (n, row)))
            if k == "bind" and not isinstance(row[2], str) and o not in (owner(row[1]), row[2][1]):
                bad.append(("D.contact_binding", "%s holds %r" % (n, row)))
            if k == "occ" and owner(row[1]) not in st.announced:
                p = owner(row[1])
                ok = {p} | contacts_of(st, p) | (seats if (p in placed or p in w.founders) else set())
                if o not in ok:
                    line = "%s holds the occurrence %s of unannounced %s" % (n, row[1], p)
                    bad.append(("D.occurrence_literal", line))
                    # the one holder the rules themselves make: the invitee its inviter wrote to
                    if not (inviter_of.get(o) == p and ("prop", o) in made):
                        bad.append(("D.occurrence", line))
            if k in ("roster0", "seat") and o not in seats:
                bad.append(("D.roster", "%s holds %r and its owner has no seat" % (n, row)))
            if k in ("content", "wraps") and o not in seats:
                bad.append(("D.content", "%s holds %r and its owner has no seat" % (n, row[:1])))
            if n != RELAY and k == "content" and not w.nl(n):
                bad.append(("L.bytes", "%s holds the bytes and its node key's list leaves the room out" % n))
            if n != RELAY and k == "wraps" and n in row[1] and not w.rl(n):
                bad.append(("L.wrap", "%s holds a wrap and its roster key's list leaves the room out" % n))
    for row in made:
        if row[0] == "prop":
            j = row[1]
            if j not in st.announced and inviter_of[j] not in contacts_of(st, j):
                bad.append(("D.invited_unannounced", "%s is invited, unannounced, with no contact exchanged" % j))
        if row[0] == "wraps":
            for t in row[1]:
                if not w.rl(t):
                    bad.append(("L.sealer", "a sealer wrapped to %s, whose roster key's list leaves the room out" % t))
    return bad


def expected_rows(w, rules, st, d):
    """What device d of a seated person should hold when nothing more can move."""
    made, seats, placed = truth(w, st)
    want = set()
    in_aud = not (rules.node_list_reach == "audience" and rules.node_list and not w.nl(d))
    for row in made:
        k = row[0]
        if k in ("roster0", "seat", "prop", "acc") and in_aud:
            want.add(row)
        elif k == "bind" and row[2] == "room" and in_aud:
            want.add(row)
        elif k == "occ" and (owner(row[1]) in placed or owner(row[1]) in w.founders) and in_aud:
            want.add(row)
        elif k == "content" and in_aud and (w.nl(d) or not rules.node_list):
            want.add(row)
        elif k == "wraps" and in_aud and (d not in row[1] or w.rl(d) or not rules.roster_list):
            want.add(row)
    return want


def liveness(w, rules, st):
    """Read on a state where nothing more can move: every seated person's device holds the room's rows."""
    bad = []
    made, seats, placed = truth(w, st)
    P = pub(w, st, rules)
    if w.expect_join:
        for j, _a in w.invites:
            if j not in seats:
                bad.append(("N.join", "%s was never seated" % j))
    for p in sorted(seats):
        for d in w.devs(p):
            missing = expected_rows(w, rules, st, d) - (st.H[w.idx[d]] | P)
            if missing:
                tag = "N.placed" if ("bind", d, "room") in made else "N.unplaced"
                bad.append((tag, "%s (%s) never holds %s" % (
                    d, "placed at the room" if tag == "N.placed" else "not placed at the room",
                    sorted(repr(m[:3]) for m in missing)[:4])))
    return bad


def room_view(w, rules, st):
    """What the devices of seated persons hold of the room: the part an announce must leave as it was."""
    made, seats, placed = truth(w, st)
    P = pub(w, st, rules)
    out = []
    for d in w.devices:
        if owner(d) not in seats:
            continue
        rows = frozenset(r for r in (st.H[w.idx[d]] | P)
                         if r[0] != "env" and not (r[0] == "bind" and r[2] == "fed")
                         and not (r[0] == "bind" and r[2] == "self"))
        out.append((d, rows))
    return tuple(out)


def explore(w, rules, cap=4000000, want_trace=False, witnesses=(), terminal_witnesses=()):
    """Breadth-first over every order of the enabled steps. Returns the reachable states and what was read on them."""
    s0 = initial(w, rules)
    seen = {s0: None}
    frontier = [s0]
    broken = {}
    terminals = []
    link_premise = 0
    announce_late = 0
    reached = {}
    while frontier:
        nxt = []
        for st in frontier:
            for name, line in safety(w, rules, st):
                broken.setdefault(name, (line, st))
            link_premise += link_withholds(w, rules, st)
            for wname, pred in witnesses:
                if wname not in reached and pred(w, rules, st):
                    reached[wname] = st
            n_out = 0
            for label, s2 in steps(w, rules, st):
                n_out += 1
                if label.startswith("announce") and all(("seat", j) in created(st) for j, _a in w.invites):
                    announce_late += 1
                if s2 not in seen:
                    seen[s2] = (st, label) if want_trace else None
                    nxt.append(s2)
            if n_out == 0:
                terminals.append(st)
                for wname, pred in terminal_witnesses:
                    if wname not in reached and pred(w, rules, st):
                        reached[wname] = st
                for name, line in liveness(w, rules, st):
                    broken.setdefault(name, (line, st))
            if len(seen) > cap:
                raise RuntimeError("state cap %d passed in world %s" % (cap, w.name))
        frontier = nxt
    return {"states": len(seen), "seen": seen, "broken": broken, "terminals": terminals,
            "link_premise": link_premise, "announce_late": announce_late, "reached": reached}


def trace(seen, st):
    out = []
    while seen.get(st) is not None:
        st, label = seen[st]
        out.append(label)
    return list(reversed(out))
