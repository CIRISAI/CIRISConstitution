"""
leaf_vouch.py: the MLS leaf vouch as a door reads it.

    vouch     one row a member's device key signs. It carries 1, 8 or 32 salted digests, a start and an end. Behind a
              digest is an entry [leaf key, room, suite], or padding.
    present   a LeafNode's credential carries the row and discloses entries of it (an entry and its salt).
    door      what every member of an MLS group runs on a LeafNode (an Add, an Update, a Commit path) and on a
              message a leaf signed.

Two things are written apart and never share code:

    door_leaf, door_msg, door_remove   what a door decides from the bytes presented, under a RULE (a dict of
                                       switches; the rule as modelled is RULE, a plant flips switches)
    intended, sem_state                what the member's device key in fact signed, read from the row's entries;
                                       no switch reaches it

The checks (check_leaf_vouch.py) are that the door never accepts outside `intended`, never refuses inside it, and
that the lifecycle built on the door keeps the properties its README states.

Symbolic: a signature is a field, a digest is a tuple, a salt is a name. No signature is forged and no two
disclosures share a digest; both are assumed and neither is checked here.
"""
from collections import namedtuple

SUITE = 0x004D          # the suite a room's groups run
OTHER_SUITE = 0x0001    # any other suite
TERM = 2                # the cap on a vouch's term, in ticks: the 30 days, so a tick is 15 days and half term is one tick
DIGEST_COUNTS = (1, 8, 32)
SEAT_KINDS = ("person", "agent", "room")   # a person's roster key, an agent's key, a room key; never "node"

Row = namedtuple("Row", "rid signer sig_ok digests start end withdrawn")
Group = namedtuple("Group", "name gid room suite claimed")
# room: the room whose members run this group, and whose roster their door reads
# claimed: the room a random id is said to belong to (read only by the plant that trusts it)


class World:
    def __init__(self, seats, kind, owner):
        self.seats = seats      # room -> {member: the key the roster seats}
        self.kind = kind        # key -> person | agent | room | node (a key not listed is a leaf key)
        self.owner = owner      # node key -> the member it is owner-bound to

    def kind_of(self, key):
        return self.kind.get(key, "leaf")


# ---------------------------------------------------------------------------------------------------- group ids
def gid_chat(room):
    return ("derived", room, "chat")


def gid_call(room, call):
    return ("derived", room, "call", call)


def gid_random(n):
    return ("random", n)


def room_of(rule, g):
    """The room a door recomputes from a group's id. A random id gives none."""
    if g.gid[0] == "derived":
        return g.gid[1]
    return None if rule["recompute_room"] else g.claimed


# ------------------------------------------------------------------------------------------------------ the row
def digest(disclosure):
    return ("d", disclosure[0], disclosure[1])


def pad_count(n):
    """The digest count for n entries: padded up to 1, 8 or 32; more than 32 is more than one row."""
    for c in DIGEST_COUNTS:
        if n <= c:
            return c
    return None


def make_row(rid, signer, entries, ndig, start, end, sig_ok=True, withdrawn=False):
    digs = tuple(digest((e, ("salt", rid, i))) for i, e in enumerate(entries))
    digs += tuple(("pad", rid, i) for i in range(max(0, ndig - len(entries))))
    return Row(rid, signer, sig_ok, digs, start, end, withdrawn)


def disclosures_of(row):
    return tuple((d[1], d[2]) for d in row.digests if d[0] == "d")


def entries_of(row):
    return tuple(d[1] for d in row.digests if d[0] == "d")


# ----------------------------------------------------------------------------------------------------- the rule
RULE = {
    "recompute_room": True,      # the door recomputes the room from the group's id
    "digest_count": True,        # 1, 8 or 32 digests
    "cap": True,                 # an end is required, at most TERM after the start
    "sig": True,                 # the row's signature verifies
    "signer": "seat",            # under the key the room's roster seats for the credential's identity
    "kind": True,                # and that key is no node key
    "one": "exactly_one",        # the presentation discloses exactly one entry
    "digest_match": True,        # whose salted digest is in the row
    "entry_key": True,           # naming this leaf key
    "entry_room": True,          # this room
    "entry_suite": True,         # this suite
    "bind": "room",              # the room, so its chat group and its call groups
    "covers": True,              # start <= now < end
    "withdrawal": True,          # and not withdrawn
    "pop": True,                 # the LeafNode is signed by the leaf key it carries
    "lapsed": "update_only",     # a lapsed leaf signs exactly the Update that replaces it
    "remove": "lapsed_only",     # members may remove, as lapsed, a leaf that is
    # a reading, not a plant: does a leaf whose vouch was WITHDRAWN still sign its replacing Update
    "withdrawn_may_replace": True,
    # not in the rule as modelled; an experiment switch: the door refuses an Update that keeps the leaf key
    # under a different vouch
    "fresh_on_update": False,
}


def door_leaf(rule, w, g, ident, key, ln_signer, row, discl, now, replaced=None):
    """A LeafNode at a door. None when accepted, else the first reason. `replaced` is (leaf key, row) of the leaf an
    Update replaces. The reason names are this model's and are no registry tokens."""
    room = room_of(rule, g)
    if room is None:
        return "group_not_of_a_room"
    if row is None:
        return "vouch_absent"
    if rule["digest_count"] and len(row.digests) not in DIGEST_COUNTS:
        return "vouch_digest_count"
    if rule["cap"] and (row.end is None or not 0 < row.end - row.start <= TERM):
        return "vouch_term"
    if rule["sig"] and not row.sig_ok:
        return "vouch_signature"
    seat = w.seats[g.room].get(ident)
    ok = seat is not None and row.signer == seat
    if rule["signer"] == "owner_bound_node":
        ok = ok or (seat is not None and w.owner.get(row.signer) == ident)
    elif rule["signer"] == "any_key":
        ok = True
    elif rule["signer"] == "old_leaf":
        ok = ok or (replaced is not None and row.signer == replaced[0])
    if not ok:
        return "vouch_not_the_members_key"
    if rule["kind"] and w.kind_of(row.signer) == "node":
        return "vouch_by_node_key"

    def one(d):
        if rule["digest_match"] and digest(d) not in row.digests:
            return "disclosure_not_in_vouch"
        e = d[0]
        if rule["entry_key"] and e[0] != key:
            return "vouch_names_another_leaf"
        if rule["entry_room"] and e[1] != room:
            return "vouch_names_another_room"
        if rule["bind"] == "chat_group_only" and g.gid != gid_chat(e[1]):
            return "vouch_names_another_group"
        if rule["entry_suite"] and e[2] != g.suite:
            return "vouch_names_another_suite"
        return None

    if rule["one"] == "exactly_one":
        if len(discl) == 0:
            return "vouch_discloses_nothing"
        if len(discl) > 1:
            return "vouch_discloses_more_than_one"
        r = one(discl[0])
        if r:
            return r
    elif rule["one"] == "any_match":
        if len(discl) == 0:
            return "vouch_discloses_nothing"
        rs = [one(d) for d in discl]
        if all(rs):
            return rs[0]
    elif rule["one"] == "zero_ok":
        if len(discl) > 1:
            return "vouch_discloses_more_than_one"
        if discl:
            r = one(discl[0])
            if r:
                return r
    if rule["covers"]:
        if now < row.start:
            return "vouch_not_started"
        if row.end is not None and now >= row.end:
            return "vouch_ended"
    if rule["withdrawal"] and row.withdrawn:
        return "vouch_withdrawn"
    if rule["pop"] and ln_signer != key:
        return "leaf_not_signed_by_its_key"
    if rule["fresh_on_update"] and replaced is not None and key == replaced[0] and row.rid != replaced[1].rid:
        return "renewal_keeps_the_leaf_key"
    return None


KINDS = ("application", "proposal", "commit", "update_replacing_self")


def door_msg(rule, row, kind, now):
    """A message signed by a leaf already in the tree, whose credential carries `row`. For an Update this is the old
    leaf's signature only; the new LeafNode is door_leaf's."""
    lapsed = rule["covers"] and row.end is not None and now >= row.end
    withdrawn = rule["withdrawal"] and row.withdrawn
    if not lapsed and not withdrawn:
        return None
    if kind == "update_replacing_self":
        if rule["lapsed"] == "nothing":
            return "leaf_lapsed"
        if withdrawn and not rule["withdrawn_may_replace"]:
            return "leaf_withdrawn"
        return None
    if not withdrawn:
        if rule["lapsed"] == "app_ok" and kind == "application":
            return None
        if rule["lapsed"] == "commit_ok" and kind in ("proposal", "commit"):
            return None
    return "leaf_withdrawn" if withdrawn else "leaf_lapsed"


def door_remove(rule, row, now):
    """A member removes a leaf on the ground that it lapsed."""
    if rule["remove"] == "any":
        return None
    if row.withdrawn or (row.end is not None and now >= row.end):
        return None
    return "leaf_not_lapsed"


# ------------------------------------------------------------------------------ what was signed (no switch here)
def intended(w, g, ident, key, row, now):
    """The device key the room's roster seats for `ident` signed a row, in force now, with an entry for this leaf
    key, this room and this suite; and the group's id is one of that room's."""
    if row is None or not row.sig_ok:
        return False
    if not (g.gid[0] == "derived" and g.gid[1] == g.room):
        return False
    if w.seats[g.room].get(ident) != row.signer or w.kind_of(row.signer) not in SEAT_KINDS:
        return False
    if len(row.digests) not in DIGEST_COUNTS:
        return False
    if row.end is None or not 0 < row.end - row.start <= TERM:
        return False
    if not (row.start <= now < row.end) or row.withdrawn:
        return False
    return (key, g.room, g.suite) in entries_of(row)


def sem_state(row, now):
    """live | lapsed | withdrawn | void (a row no door should ever have taken: no end, or a term over the cap)"""
    if row.end is None or not 0 < row.end - row.start <= TERM:
        return "void"
    if row.withdrawn:
        return "withdrawn"
    if now >= row.end:
        return "lapsed"
    return "live"
