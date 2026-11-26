"""
seat.py: STANDING AS ONE SHAPE, over the causal kernel (kept, concluded, the cut) and kernel_lib.

A seat of key k in scope s over object o is live iff
    a kept, concluded OFFER by a conferrer names (k, s, o),
    a kept, concluded ACCEPTANCE by k is paired with that offer,
    neither is withdrawn by its own signer,
    and no counting cut removes it.

The conferrer is one parameter with three values (`conf` on the offer):
    self    the offer is signed by the object's own key: the object itself when it is a key, the signers or
            the named subjects of the row when it is a row (a group is the row that founded it)
    seat    the offer is signed by a key holding a live seat that may confer this one, and names that seat
            (`under`). Bounded depth. What a seat may confer is table data (CONFERS) or the `sub` mark.
    group   the offer counts when a tally of the live seats (`counted`, over `over`) at the head it names is
            met. The threshold is a row of manifests/governance_policy.json; a ranked row is the ranked tally.

Pairing. The acceptance names the offer (`of`), or the offer names the acceptance: the text has both orders
(a widening names the joiner's acceptance; a trust acceptance names the root's charter). A key that signed the
offer itself, as signer or as one of `cosigners` (several signatures on one row), has accepted by that.
`consent="one"` on an offer waives the acceptance (a node has no agency); it is refused under conf=seat.

A cosignature is a voice for an offer or an unseat only when it names every head that row is counted over. A
voice given once is not a voice for a later row of the same content at another head.

What ends a seat.
    withdraw   a row naming the offer or the acceptance, signed by the signer of what it names, or by the
               holder against the offer that seats it. Read at the concluded layer: no standing is needed.
               A holder's withdrawal ends its own seat only; the conferrer's ends the offer for all it seats.
               The conferrer of a counted offer (conf=group) is the count, not the key that signed the row: that
               key's lone withdrawal ends nothing. A counted seat ends by its holder's withdrawal or a counted unseat.
    unseat     a CUT on the slot ("seat", k, s, o), by the object's own key (self) or by a count (group). Every
               offer on the slot in its past is ended, every offer and acceptance on the slot concurrent with
               it is void (cut.py), and an offer that names it is a new seat.
               Over a founding row that seats several keys no one of them is "the object's own key" against the
               others: a `self` unseat there concludes nothing, and ending such a seat takes the count.
    upstream   a seat conferred under another falls with it (the walk is run again on every read). A `self` offer
               over a founding row that seats several keys, signed by one of them, is live only while that
               signer's own founding seat is: it falls with it like any seat conferred under it.
    founding   a founding record (CC 4.5.4; `found`) lists its members in `to` and names its duty holders in
               `duty_holders`, a map from a duty to the members who hold it. It seats each listed member who signed
               it in `member`, and each holder an entry names, when a listed signer, in that duty: one row, no
               count, however many found it. A listed member who did not sign any founding row, with a map or without, is seated in nothing (a later
               acceptance does not seat it), and an entry naming a key that is no listed signer seats nothing. The
               seats end separately: a withdrawal of the founding row that names a duty (`scope`) ends that seat
               only; one that names no seat ends every seat the row gives its signer (an end of its stay).
               A founding row of scope `duty` with no map seats every key it names as a duty holder (HOLDS gives
               that seat `member`), as before.
    duty       over a community the founding record seats duty holders (a `duty_holders` map, or scope `duty`),
               who are equals (CC 4.5.4).
               A duty seat is conferred by a strict majority of the holders or by the lone holder, withdrawn by a
               strict majority of the others, never on fewer than two voices where there are two holders, and
               ended by a removal from the roster. A seat so conferred is rooted in the group: its conferrer's
               withdrawal or departure does not end it.
    member     a duty seat stands only where its holder holds the roster's seat over the same community at the
               same reading (a member seat, or the founding seat, which holds `member`). A conferral on a key that
               is not a member seats nobody, is no voice in a duty count, and stands with no further row once the
               key's widening lands. An end of the holder's stay ends the duty seats whose offers are in that
               end's past: a counted removal from the roster, or the holder's own withdrawal of a seat that holds
               `member` over the community. Nothing revives: a later admission does not seat an offer so ended. A
               conferral that is not in the end's past (made after it, or beside it) waits for the next admission
               like any conferral on a non-member. At tips the duty seat follows the folded roster.
               Over every community, whatever its founding row seats (a room founded with members only, whose
               members' count confers a duty, included), and only a seat that makes its holder a duty holder
               (`duty`, a named duty, a duty the record declares): another seat, a node's detector seat for one,
               is not asked for membership. Who may confer a duty is unchanged: the duty holders' count or the
               lone holder where the founding row seats duty holders (duty_seat), the room's count otherwise.

An AI agent's key (CC 4.5.13). An agent "acts under its own key and has no vote"; "a recall and an election count
its persons alone". "No single key removes a member alone, and no duty holder removes another from the roster
alone. ... An AI agent's key is the exception. A moderator of the room MAY remove it alone and at once, and the
members may lift that act as they may any act of a moderator."
    the seat      an agent's key is seated over the room in scope `agent` (AGENT), a roster seat (ROSTER_SEATS) the
                  room's persons admit by their count. `Seats.roster(o)` is the whole roster, members and agents,
                  which content, wraps and audience read; `holders("member", o)` holds no agent. Every count of the
                  room is taken of persons (counted_keys): an agent's key is no voice and is not counted over,
                  whatever other seat it holds. An agent may hold a duty by its own duty seat, which stands on its
                  `agent` seat as a person's stands on its member seat, and acts alone within it.
    the removal   a counted unseat of one key's `agent` seat concludes on its signer's one voice where that signer
                  holds `moderate` over the object at the head the row names, whatever the room's protocol and
                  however many holders. The seat's scope says the key is an agent's. An unseat of a person's seat
                  so signed is counted as any removal is.
    the lift      the removal opens a `moderation_overturn` window (window.py: `window` on the row). The lift's
                  effect is a row: a counted offer of policy `moderation_overturn` that seats the key again, cites
                  the removal (`content`), names the head the removal names, and names objections (answers
                  `object` to the removal). Its voices are the signers of those objections and no other key; the
                  removal's author is no voice, and the key it seats is an agent's, so it is in no count. It
                  concludes when those voices are a strict majority of the members (persons) at that head, the
                  removal's author apart, never fewer than two: the overturn's count.
                  It restores and does not admit: the key it seats held its `agent` seat at that head.
                  No reading of the roster reads a window: until that row is written the key is out.
    in force      the removal is an act under the remover's `moderate` standing, and the seat walk counts it as a
                  live unseat only where the end rule (conferral_end.py, E2 to E8) gives it in force over the rows
                  held (removal_in_force, re-expressed over seat rows): an end of that standing, its own laying
                  down, a counted removal of it, or the other holders' counted withdrawal of its duty, takes it out
                  of force from the end's head on unless another duty holder's receipt of it (an `ack` naming it)
                  is held; a removal naming a head later than the end's, or having the end in its past, does not
                  count. Out of force, it ends nothing and the agent's key is seated again for that reader. Only another
                  standing live at the removal's head keeps it; nothing revives it (a moderator seated again signs
                  the removal again).

Tips wait (KERNEL.md section 7). When several counted acts on one object are concurrent, the holders of a scope
over it are the keys common to the tips, until a counted act names them all.

Built on, and the reader's line (checkpoint.py). A counted act counts only if every counted act among the heads it
names counts. With `own`, the counted acts that reader has acknowledged are its line: a counted act concurrent with
the line and counted over older heads does not count for that reader; one counted over the same head waits as a tip.
`checkpoint=True` turns on the group checkpoint, which is refused (it ranks lines by depth) and kept only to show why.

Layers. Whether an offer or an unseat was validly made is CONCLUDED: it reads the row and its concluded
ancestors only (the object's own key; the count over the head it names). Whether the seat is live now is
DERIVED: pairing, withdrawals, the cut and the walk. No instant, digest or list position is read.

stands(S, root, k, s, o): the bounded walk. A self-rooted seat has its offer's signer as root, a counted seat
has ("group", o), a conferred seat has the root of the seat it is under.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import causal_kernel as CK  # noqa: E402
import cut as CUT           # noqa: E402
import checkpoint as CP     # noqa: E402

K, R = CK.K, CK.row
sys.path.insert(0, os.path.join(ROOT, "models", "kernel_lib"))
from reexpress import ranked as RANKED  # noqa: E402   the ranked count, already written over the library
DEPTH = 5                                       # CC 3.4.7: a delegation chain is at most five links

# ---- table data ----------------------------------------------------------------------------------------
# what a seat holds at zero hops (the root holds what it may confer), and what it may confer over which object
# CC 4.5.4 community law: "A community has members and duty holders, and no other tier." A founding record seats the
# duty holders it names, each by its own signature on it (scope `duty`); "Whoever founds a community alone is its first
# duty holder." A holder of any one duty is a duty holder. `founder` is kept only in the infrastructure community's
# sense (its operators, CC 3.2 T7), where it holds membership and no duty.
DUTIES = ("moderate", "review", "slash", "takedown")
HOLDS = {"duty": ("member",) + DUTIES, "founder": ("member",), "owner": ("steward",)}
CONFERS = {  # scope held -> (scopes it may confer, "same": over the same object | "holder": over the holder's own key)
    "duty": (("duty",) + DUTIES, "same"),     # alone only while the one duty holder (LONE); otherwise by the count
    "owner": (("wa", "infra:attest", "operator"), "same"),
    "self": (("wa", "takedown", "author", "custodian", "operator"), "same"),
    "root": (("attest", "infra:attest", "assure:age", "assure:capacity", "infra:attest_assurance", "infra:detect"), "holder"),
}
# what the holder of a seat over an object may end over that same object by a row of its own (a cut, so it takes
# standing). CC 2.4.1.1: "Its owner revokes it under the owner-binding, and that ends the owner-binding's standing.
# ... Only the key's own revocation ends its liveness, and neither of the others does" (the sentence of 2026-11-16;
# until 2026-11-23 this table read the owner's revocation as ending the key's registration). So the owner's
# revocation ends the owner's OWN seat, the binding, and nothing of the key's. The owner seat is the owner-binding: the
# owner's row and the key's own signature on it (CC 3.2, The first binding). The ender must be the ONE live owner
# over the ender's own past: `owner_of` "resolves to at most one key", and with two the key "MUST NOT be treated as
# owned by any of them" (CC 3.2), so with two live owners neither alone revokes (derived from those two sentences).
ENDS = {"owner": ("owner",)}
# seats whose ending is final: a revocation is "never withdrawn" (CC 2.4.1.1), so no offer re-seats the same key in the
# same scope over the same object once a concluded revocation of that slot is in its past
FINAL = ("registered",)
# CC 4.5.4 (iv): "A duty seat is conferred by a strict majority of the duty holders, and withdrawn by a strict majority
# of the other duty holders, the holder concerned not counted. Where there are two holders or more, neither takes fewer
# than two voices. A lone duty holder confers alone, with the new holder's acceptance." Two policy names, counted
# over the duty holders at the head the row names; a seat conferred alone stands only if its signer was then the
# one duty holder, read over the offer's own past.
DUTY_POLICY = {"duty_confer": "confer", "duty_withdraw": "withdraw"}
MUT = set()       # named mutations, switched on by a check (formal/causal_kernel/check_rosters.py, the key instance)


def policy_table(path=None):
    """policy row -> a predicate met(yes, n), from the enact rule of manifests/governance_policy.json."""
    path = path or os.path.join(ROOT, "data", "governance_policy.json")
    out = {}
    for f in json.load(open(path, encoding="utf-8"))["families"]:
        e = f.get("enact_rule") or {}
        if e.get("kind") == "fraction":
            num, den = e["num"], e["den"]
            # the table writes self_roster_* as 1/2; the text and formal/self_roster say a strict majority
            out[f["family"]] = ("strict", 1, 2) if (num, den) == (1, 2) else ("atleast", num, den)
        elif e.get("kind") == "strict_majority":
            out[f["family"]] = ("strict", 1, 2)
        elif e.get("kind") == "one_of_n":
            out[f["family"]] = ("one", 1, 1)
        elif e.get("kind") == "protocol":
            out[f["family"]] = ("declared", 0, 0)
        elif e.get("kind") == "ranked_irv":
            out[f["family"]] = ("ranked", 0, 0)                  # the count is the ranked tally (formal/ranked_choice)
        else:
            out[f["family"]] = ("not_a_count", 0, 0)             # role_at: a seat, not a threshold
    return out


POLICY = policy_table()
# A removal runs under the room's own declared protocol (CC 3.3.4; the table's cell is `protocol`). The rooms of
# these scenarios declare two thirds. roster.py runs the other protocols.
POLICY.update({k: ("duty", 0, 0) for k in DUTY_POLICY})          # CC 4.5.4 (iv), read by duty_count, not by met()
# CC 4.5.13, the members' check as a counted row: the re-seating of an agent's key a moderator removed alone. Read by
# lift_count, not by met(): a counted row of this policy that is no such re-seating concludes nothing.
POLICY["moderation_overturn"] = ("lift", 1, 2)
if POLICY.get("community_remove", ("", 0, 0))[0] == "declared":
    POLICY["community_remove"] = ("atleast", 2, 3)


def met(policy, yes, n, declared=None, table=None):
    kind, num, den = K.rule(table or POLICY, policy, ("unknown", 0, 0))
    if kind == "atleast": return n > 0 and yes * den >= num * n
    if kind == "strict": return yes * den > num * n
    if kind == "one": return yes >= 1
    if kind == "declared": return declared is not None and yes >= declared
    return False


# ---- rows ----------------------------------------------------------------------------------------------
def _slots(to, scope, obj):
    return tuple(("seat", k, scope, obj) for k in ((to,) if isinstance(to, str) else to))


def offer(id, signer, to, scope, obj, conf, names=(), **kw):
    obj = id if obj == "@" else obj                 # "@": the object is this row (a group is its founding row)
    return R(id, "offer", signer, names, to=(to,) if isinstance(to, str) else tuple(to), scope=scope, obj=obj,
             conf=conf, on=_slots(to, scope, obj), **kw)


def accept(id, signer, of, names=(), scope=None, obj=None):
    """An acceptance of offer `of`, or (of=None) a standing acceptance of any offer of `scope` that names it."""
    names = tuple(names) + ((of,) if of and of not in names else ())
    kw = {"on": _slots(signer, scope, obj)} if obj is not None else {}
    return R(id, "accept", signer, names, of=of, scope=scope, obj=obj, **kw)


def withdraw(id, signer, target, names=(), scope=None):
    """A withdrawal of row `target`. `scope`, where given, names the one seat of a founding row it ends (the
    duty a founding holder lays down); with none it ends every seat the target gives its signer."""
    kw = {} if scope is None else {"scope": scope}
    return R(id, "withdraw", signer, tuple(names) + ((target,) if target not in names else ()), target=target, **kw)


def found(id, signer, to, duty_holders=None, cosigners=(), scope="member", **kw):
    """A founding record (CC 4.5.4): `to` its listed members, each seated `member` by its own signature on it;
    `duty_holders` a map from a duty to the members who hold it, each seated in that duty by the same signature.
    The map is carried as sorted (duty, keys) pairs."""
    dh = tuple(sorted((d, tuple(ks)) for d, ks in (duty_holders or {}).items()))
    return offer(id, signer, to, scope, "@", "self", cosigners=tuple(cosigners), duty_holders=dh, **kw)


def unseat(id, signer, k, scope, obj, conf, names=(), **kw):
    return R(id, "unseat", signer, names, to=(k,), scope=scope, obj=obj, conf=conf, cuts=_slots(k, scope, obj),
             says="out", **kw)


def cosign(id, signer, of, names=()):
    return R(id, "cosign", signer, names, of=of)


signers = lambda r: frozenset((r["signer"],) + tuple(r.get("cosigners", ())))
covers = lambda have, want: have == want or want.startswith(have + ":")


def is_duty(scope, declared=()):
    """A duty: the four the law names, or one the community's record declares (CC 4.5.4 (i): "a record MAY declare
    others"). `declared` is the record's own list (the founding row's `duties`)."""
    return scope == "duty" or scope.split(":")[0] in DUTIES or scope.split(":")[0] in declared


def declared(by, obj):
    g = by.get(obj)
    return tuple((g or {}).get("duties", ()))


# the seats over a community its duty holders do NOT place: membership is the roster's own seat, placed by the count
# of the group's consensus_protocol and the joiner's yes (CC 3.1.3.2, CC 3.3.4). Every other seat they place over the
# community is placed by them under CC 4.5.4 (iv), whatever its scope.
ROSTER_SEATS = ("member", "agent")
# CC 4.5.13: an AI agent "acts under its own key and has no vote"; "a recall and an election count its persons alone".
# An agent's key is seated in a scope of its own: on the roster (content, wraps, audience), and in no count.
AGENT = "agent"


def lists_holders(g):
    """A founding row that names its duty holders (CC 4.5.4): a `duty_holders` map that names at least one key."""
    return any(ks for _, ks in g.get("duty_holders") or ())


def seat_scopes(o, k):
    """The scopes offer `o` seats key k in. One, the offer's own scope, for every offer but a founding row. A founding
    row seats by the signatures on it, with or without a map: a listed member who did not sign it is seated in nothing,
    whatever it accepts later (CC 3.1.3.2, `membership_founding_member_unsigned`); one who signed it in its own scope,
    and where it carries a `duty_holders` map, in each duty whose entry names it."""
    if o["obj"] != o["id"]: return (o["scope"],)
    # a founding row seats by the signatures on it, with or without a map (CC 3.1.3.2: a listed key that did not sign
    # is `membership_founding_member_unsigned`; it joins by an ordinary admission)
    if "unsigned_no_map" in MUT and not o.get("duty_holders"): return (o["scope"],)   # MUTATION: the old exception
    if k not in signers(o) and "unsigned_seated" not in MUT: return ()       # MUTATION: a listed member who did not sign is seated
    if not o.get("duty_holders") or "holders_unread" in MUT: return (o["scope"],)
    return (o["scope"],) + tuple(d for d, ks in o["duty_holders"] if k in ks and d != o["scope"])


def founding_duty(o, sc):
    """A duty seat a founding row gives by its `duty_holders` map."""
    return bool(o.get("duty_holders")) and o["obj"] == o["id"] and sc != o["scope"]


def duty_seat(by, o):
    """A seat placed over a community by its duty holders (an object that is a founding row seating duty holders):
    every scope but the roster's own, so a scope the record declares, or any other, follows the holders' count."""
    g = by.get(o["obj"])
    if g is None or g["id"] == o["id"] or not duty_room(by, o["obj"]): return False
    if "duty_list_only" in MUT: return is_duty(o["scope"])      # MUTATION: only the named duties follow the count
    return o["scope"] not in ROSTER_SEATS


def community(by, obj):
    """obj is a community: an object that is its own founding row. The duty-seat rule (a duty seat stands only on
    the roster's seat; an end of the stay ends the duty seats before it) reaches every community, whatever its
    founding row seats (CC 4.5.4: "a non-member holds no duty")."""
    g = by.get(obj)
    if "member_rule_duty_rooms_only" in MUT: return duty_room(by, obj)   # MUTATION: the rule reaches duty rooms only
    return g is not None and g["kind"] == "offer" and g["obj"] == g["id"]


def duty_room(by, obj):
    """obj is a community whose founding row seats duty holders (the only place the duty rules engage): a founding row
    of scope `duty`, or one whose `duty_holders` map names a holder."""
    g = by.get(obj)
    return g is not None and g["kind"] == "offer" and g["obj"] == g["id"] and (g["scope"] == "duty" or lists_holders(g))


def roster_seat(o, holds=None, sc=None):
    """A seat of the roster's own over a community, given by offer `o` in scope `sc` (default the offer's): a scope
    its duty holders do not place (ROSTER_SEATS: a member's, an agent's), or a founding row's own scope where it holds
    `member`. Every other seat over the community is a duty seat."""
    sc = o["scope"] if sc is None else sc
    if not ((o["id"] == o["obj"] and sc == o["scope"]) or sc in ROSTER_SEATS): return False
    return sc in ROSTER_SEATS or covers(sc, "member") or "member" in K.rule(HOLDS if holds is None else holds, sc, ())


def stay_ends(rows, by, holds=None):
    """The holders' own ends of a stay as a member, among `rows`: (withdrawal, key, community) for each withdrawal by a
    key of an offer of the roster's seat that names it, or of its own acceptance of one (the offer the acceptance
    names, or a standing acceptance's own scope and object). Read from the rows alone."""
    out = []
    for w in rows:
        if w["kind"] != "withdraw": continue
        t, k = by.get(w.get("target")), w["signer"]
        if t is None: continue
        # a withdrawal that names a scope ends the stay only where the target gives the signer that seat and it is a
        # roster seat; one naming a duty lays that seat down, and the stay goes on (MUTATION stay_scope_ungated: a
        # roster scope is taken at its word)
        if w.get("scope") is not None and "scope_unread" not in MUT and not (
                t["kind"] == "offer" and roster_seat(t, holds, w["scope"])
                and ("stay_scope_ungated" in MUT or w["scope"] in seat_scopes(t, k))):
            continue
        if t["kind"] == "accept" and t["signer"] == k:
            if t["of"] is not None: t = by.get(t["of"])
            elif t.get("obj") is not None and t.get("scope") in ROSTER_SEATS and community(by, t["obj"]):
                out.append((w, k, t["obj"])); continue
            else: continue
        if t is None or t["kind"] != "offer" or k not in t["to"]: continue
        if community(by, t["obj"]) and roster_seat(t, holds): out.append((w, k, t["obj"]))
    return out


def duty_held(by, o, sc=None):
    """A duty seat proper: a seat the duty holders place over their community (duty_seat) whose scope makes its holder a
    duty holder, or a duty seat a founding row gives by its `duty_holders` map. The seat the membership rule reaches."""
    sc = o["scope"] if sc is None else sc
    if founding_duty(o, sc): return True
    # over any community, a seat whose scope makes its holder a duty holder (who may confer it is duty_seat's)
    g = by.get(o["obj"])
    return community(by, o["obj"]) and g["id"] != o["id"] and o["scope"] not in ROSTER_SEATS and is_duty(sc, declared(by, o["obj"]))


def _lone(r, P, by):
    """CC 4.5.4 (iv): a duty conferred by one key stands only if that key is then the one duty holder over the object
    (a person: an agent holding a duty is no holder this count reads)."""
    if "lone_any" in MUT: return True
    Q = seats_of(P)
    return Q.holders("duty", r["obj"]) - Q.holders(AGENT, r["obj"]) == frozenset({r["signer"]})


def duty_count(r, P, yes, mem):
    """CC 4.5.4 (iv) over the duty holders at the head: conferral by a strict majority of them, withdrawal by a strict
    majority of the others (the holder concerned not counted); never fewer than two voices where there are two holders."""
    base = mem - set(r["to"]) if DUTY_POLICY[r["policy"]] == "withdraw" and "count_target" not in MUT else mem
    y = yes & base
    return 2 * len(y) > len(base) and (len(y) >= 2 or len(mem) < 2 or "no_duty_floor" in MUT)


def agent_removal(r):
    """A removal of an agent's key from the roster: an unseat of one key's `agent` seat. The seat's scope says whose it is."""
    if r["kind"] != "unseat" or len(r["to"]) != 1: return False
    return r["scope"] == AGENT or ("agent_unread" in MUT and r["scope"] in ROSTER_SEATS)   # MUTATION: it reaches a person


def lone_removal(r, P, past):
    """CC 4.5.13: a moderator of the room removes an agent's key alone. The signer holds `moderate` over the object at
    the head the row names."""
    if not agent_removal(r) or r.get("conf") != "group": return False
    if "moderator_unread" in MUT: return True                       # MUTATION: any key removes an agent's key alone
    heads = r.get("head", ())
    # the key removed holds an agent's seat at the head the row names: a person's key is not removed so, whatever
    # scope the unseat states (MUTATION lone_any_key: the key's seat not read)
    # This is also what makes a lift restore and not admit: its re-seating stands on such a removal (MUTATION
    # restores_unseated, the same break seen from the lift)
    if not MUT & {"lone_any_key", "restores_unseated"} and r["to"][0] not in members_at(P, past, r["obj"], heads, AGENT):
        return False
    return r["signer"] in members_at(P, past, r["obj"], heads, "moderate")


def lift_voices(r, P, past, by):
    """The voices of a re-seating row, or None where it is none: the signers of the objections it names to the lone
    removal it cites, less that removal's author."""
    rem = by.get(r.get("content"))
    if r["kind"] != "offer" or rem is None or rem["kind"] != "unseat" or not lone_removal(rem, P, past): return None
    if (rem["obj"], rem["scope"], tuple(rem["to"]), tuple(rem.get("head", ()))) != (r["obj"], r["scope"], tuple(r["to"]), tuple(r.get("head", ()))):
        return None                                                 # the same seat, at the head the removal names
    v = frozenset(a["signer"] for a in P if a["kind"] == "answer" and a.get("of") == rem["id"] and a.get("says") == "object"
                  and a["id"] in r["names"])
    return v if "author_voice" in MUT else v - {rem["signer"]}      # MUTATION author_voice: the author's objection counts


def lift_count(r, P, past, by):
    """The overturn's count (window.py, moderation_overturn) over the objections a re-seating row names: a strict
    majority of the members at the head, the removal's author apart and the key seated apart (each no voice, and
    not counted over); never fewer than two."""
    v = lift_voices(r, P, past, by)
    if v is None: return False
    heads = r.get("head", ())
    # a lift restores: the key held its `agent` seat at the head the removal names, since the removal is a lone
    # removal only of such a key (lone_removal). So a moderator's "removal" of a key never seated, and a strict
    # majority's objections, admit nothing past the room's own protocol
    # the members are persons: the key removed is an agent's, so it is no voice and is not counted over
    mem, vot = counted_keys(P, past, r["obj"], heads)
    yes = v & vot
    if "lift_over_all" not in MUT: mem = mem - {by[r["content"]]["signer"]}    # MUTATION lift_over_all: the author counted over
    return 2 * len(yes) > len(mem) and (len(yes) >= 2 or "lift_no_floor" in MUT)


def founding_many(by, obj):
    """obj is a founding row that seats several keys."""
    g = by.get(obj)
    return g is not None and g["kind"] == "offer" and g["obj"] == g["id"] and len(g["to"]) > 1


def own_keys(by, obj):
    """The object's own key: the object when it is a key; the signers and named subjects of the row when a row."""
    if obj in by:
        return signers(by[obj]) | frozenset(by[obj].get("subjects", ()))
    return frozenset({obj})


# ---- derived: the live seats ---------------------------------------------------------------------------
class Seats:
    def __init__(self, S, holds=HOLDS, confers=CONFERS, depth=DEPTH, by_arrival=False, own=None, checkpoint=False, drop=None):
        self.S, self.holds, self.confers, self.own = S, holds, confers, own
        self.cut = C = CUT.Cut(S)
        Cs = S.Cs
        wd = K.sel(Cs, kind="withdraw")
        pos = {r["id"]: i for i, r in enumerate(S.rows)}
        ended = lambda row: any(w["target"] == row["id"] for w in wd)        # the concluded layer checked who signed it
        # a holder's withdrawal ends its own seat; the conferrer's (a signer who is not seated by the row) ends the offer
        # MUTATION by_arrival: a withdrawal held after the offer's acceptance comes too late (first held wins)
        late = lambda w, o: by_arrival and any(pos[a["id"]] < pos[w["id"]] for a in K.sel(Cs, kind="accept", of=o["id"]))
        # the conferrer of a counted offer is the count: the lone withdrawal of the key that signed the row ends nothing
        # a duty seat over a community: duty holders are equals (CC 4.5.4 (iii)), so the key that conferred it does not end it
        # alone; it ends by its holder's withdrawal or a count (duty_withdraw, or the members' recall)
        eq = lambda o: duty_seat(S.by, o) and "duty_ranked" not in MUT
        # a withdrawal that names a scope ends that one seat of the row it withdraws (a founding holder lays down a duty)
        off_ended = lambda o, k, sc: any(w["target"] == o["id"] and (w["signer"] == k or (w["signer"] not in o["to"] and o["conf"] != "group" and not eq(o)))
                                         and (w.get("scope") in (None, sc) or "scope_unread" in MUT) and not late(w, o) for w in wd)
        self.stale = V = CP.void(S, C, own, checkpoint)         # counted acts built on one that does not count, or behind the reader's line
        unseats = [u for u in K.sel(Cs, kind="unseat") if C.counts(u) and u["id"] not in V]
        # a moderator's lone removal is an act under its `moderate` standing, in force only while the end rule says so
        # (out_of_force). `drop`: the lone removals already judged out of force over the whole set, for a reading of
        # one line of it (the tips, the fold) or of the set with every removal taken as made (`frozenset()`)
        if drop is None:
            drop = out_of_force(S, unseats, holds, confers, depth, own, checkpoint) if "end_unread" not in MUT else frozenset()
        self.dropped = drop
        unseats = [u for u in unseats if u["id"] not in drop]

        left = stay_ends(wd, S.by, holds)                       # the holders' own ends of a stay as a member
        gone = {(k, g) for _, k, g in left}

        def resigned(o, k, sc):
            """A duty seat whose offer is in the past of its holder's own end of its stay as a member is ended by it."""
            if "duty_revives" in MUT or "resign_keeps_duty" in MUT or not duty_held(S.by, o, sc): return False
            return any(k2 == k and g == o["obj"] and ((pos[o["id"]] < pos[w["id"]]) if by_arrival else (o["id"] in S.anc[w["id"]]))
                       for w, k2, g in left)

        def unseated(o, k, sc):
            for u in unseats:
                # a removal from the roster ends the removed member's duty seats too, "since a non-member holds no duty" (CC 4.5.4)
                held = ("seat", k, sc, o["obj"]) in u["cuts"] or (
                    "member_cut_only" not in MUT and (is_duty(sc) or duty_seat(S.by, o) or founding_duty(o, sc))
                    and any(("seat", k, r, o["obj"]) in u["cuts"] and holds_roster(S, u, k, o["obj"], r) for r in ROSTER_SEATS))
                if not held: continue
                # MUTATION duty_revives: a removal from the roster ends no duty seat by its past, so the next admission seats the old offer
                if "duty_revives" in MUT and ("seat", k, sc, o["obj"]) not in u["cuts"] and duty_held(S.by, o, sc): continue
                # MUTATION by_arrival: an unseat ends the offers that were held before it, by list position
                if (pos[o["id"]] < pos[u["id"]]) if by_arrival else (o["id"] in S.anc[u["id"]]): return True
            return False

        def accepted(o, k):
            if k in signers(o): return True
            if o.get("consent") == "one": return o["conf"] != "seat"
            for a in K.sel(Cs, kind="accept", signer=k):
                paired = (a["of"] == o["id"]) or (a["of"] is None and a["id"] in o["names"] and a["scope"] == o["scope"]
                                                 and a["obj"] in (None, o["obj"]))
                if paired and not ended(a) and C.counts(a): return True
            return False

        base = [(o, k, sc) for o in K.sel(Cs, kind="offer") if C.counts(o) and o["id"] not in V
                for k in o["to"] if accepted(o, k) for sc in seat_scopes(o, k)
                if not off_ended(o, k, sc) and not unseated(o, k, sc) and not resigned(o, k, sc)]

        def step(live):
            at = {(oid, k, sc): (d, root) for oid, k, sc, d, root in live}
            held = {(oid, k): v for (oid, k, _), v in sorted(at.items(), key=lambda x: x[1][0], reverse=True)}
            out = set(live)
            for o, k, sc in base:
                if (o["id"], k, sc) in at: continue
                if o["conf"] == "self":
                    # over a founding row that seats several keys, a signer's own offer stands on that signer's founding seat
                    if o["obj"] == o["id"] or not founding_many(S.by, o["obj"]) or (o["obj"], o["signer"]) in held:
                        out.add((o["id"], k, sc, 0, o["signer"]))
                elif o["conf"] == "group": out.add((o["id"], k, sc, 0, ("group", o["obj"])))
                elif eq(o): out.add((o["id"], k, sc, 0, ("group", o["obj"])))     # validly made by the lone holder: it stands as an equal
                elif o["conf"] == "seat":
                    up = S.by.get(o.get("under"))
                    hit = held.get((o.get("under"), o["signer"]))
                    if up is not None and hit is not None and self.may_confer(up, o):
                        out.add((o["id"], k, sc, hit[0] + 1, hit[1]))
            return frozenset(out)

        self.live = K.fix(step, frozenset(), depth + 1)       # one link per pass: at most `depth` links below a root
        # a duty seat stands only where its holder holds the roster's seat over the same community at this reading. The
        # walk is run again without the duty seats of keys that are not members, until none is left (a seat under one falls too)
        while "duty_no_member" not in MUT:
            mem = {(S.by[oid]["obj"], k) for oid, k, sc, _, _ in self.live if roster_seat(S.by[oid], holds, sc)}
            # MUTATION resign_keeps_duty: a key that ended its own stay still reads as a member for its duty seats
            keep = [(o, k, sc) for o, k, sc in base if not duty_held(S.by, o, sc) or (o["obj"], k) in mem
                    or ("resign_keeps_duty" in MUT and (k, o["obj"]) in gone)]
            if len(keep) == len(base): break
            base[:] = keep
            self.live = K.fix(step, frozenset(), depth + 1)
        self.recs = [{"id": "%s/%s/%s" % (oid, k, sc), "offer": oid, "k": k, "scope": sc, "obj": S.by[oid]["obj"],
                      "depth": d, "root": root} for oid, k, sc, d, root in self.live]

    def may_confer(self, up, o):
        """May the holder of the seat offered by `up` confer the seat `o` offers?"""
        if up.get("sub") and covers(up["scope"], o["scope"]) and o["obj"] == up["obj"]:
            return True                                            # the grant carried sub-delegation: the same or narrower
        scopes, over = K.rule(self.confers, up["scope"], ((), "same"))
        return any(covers(s, o["scope"]) for s in scopes) and o["obj"] == (up["obj"] if over == "same" else o["signer"])

    def _has(self, rec, s):
        if s == "duty" and is_duty(rec["scope"], declared(self.S.by, rec["obj"])): return True   # a holder of any one duty is a duty holder
        return covers(rec["scope"], s) or s in K.rule(self.holds, rec["scope"], ())

    def _member(self, rec):
        """A duty seat follows the folded roster: with several tips, its holder is among the members the fold seats."""
        if "duty_no_member" in MUT or "duty_fold_unread" in MUT or not duty_held(self.S.by, self.S.by[rec["offer"]], rec["scope"]): return True
        fold = self.tips_fold("member", rec["obj"])
        return fold is None or rec["k"] in fold or rec["k"] in (self.tips_fold(AGENT, rec["obj"]) or ())

    def stands(self, k, s, o, root=None):
        if not any(self._has(r, s) and (root is None or r["root"] == root) and self._member(r) for r in K.sel(self.recs, k=k, obj=o)): return False
        fold = self.tips_fold(s, o)                             # with several tips, the fold of their changes
        return fold is None or k in fold

    def roster(self, o):
        """The room's whole roster over o: its members and its agents (CC 4.5.13). Content, wraps and audience read it;
        no count does (a count reads `member`, or the scope it names, less the agents)."""
        return self.holders("member", o) | self.holders(AGENT, o)

    def holders(self, s, o, root=None):
        got = frozenset(r["k"] for r in K.sel(self.recs, obj=o) if self._has(r, s) and (root is None or r["root"] == root) and self._member(r))
        fold = self.tips_fold(s, o)
        return got if fold is None else got & fold

    def tips(self, o):
        """The frontier of the counted acts on o that count, with its founding row."""
        acts = [r for r in self.S.Cs if r["kind"] in ("offer", "unseat") and r.get("obj") == o and (r.get("conf") == "group" or r["id"] == o)
                and self.cut.counts(r) and r["id"] not in self.stale]
        return K.frontier(self.S.anc, acts)

    def tips_common(self, s, o):
        """KERNEL.md section 7: with several tips, the keys common to all of them. None with one tip or none."""
        tp = self.tips(o)
        if len(tp) <= 1: return None
        S, out = self.S, None
        for t in tp:
            sub = [q for q in S.Cs if q["id"] == t["id"] or q["id"] in S.anc[t["id"]]]          # one tip: no further recursion
            Q = Seats(CK.State(sub, {q["id"]: True for q in sub}), self.holds, self.confers, drop=self.dropped)
            m = frozenset(r["k"] for r in K.sel(Q.recs, obj=o) if Q._has(r, s))
            out = m if out is None else out & m
        return out

    def _at(self, rows):
        """The seats read over a sub-set of the concluded rows (one line: no further recursion into tips)."""
        return Seats(CK.State(rows, {q["id"]: True for q in rows}), self.holds, self.confers, drop=self.dropped)

    def tips_fold(self, s, o):
        """KERNEL.md section 7, the fold at tips (models/roster_fork/fold.py): with several tips, the keys holding
        `s` over `o` when every tip's changes are folded. None with one tip or none.
            common   a key every tip seats is in;
            out      a key some tip's line removed is out, unless a later addition of it has that removal in its
                     past. So a key one tip admits and another removes is out;
            in       a key some tip adds is in where the counted offer that adds it meets its count on the voices
                     of keys the fold seats, over the members at its heads that the fold seats: a least fixed
                     point from the common keys;
            wait     tips that differ in protocol or policy (a counted row's `regime`, where the caller states one)
                     do not fold: the answer is then the common keys, as tips_common gives."""
        tp = self.tips(o)
        if len(tp) <= 1: return None
        if "fold_off" in MUT: return self.tips_common(s, o)
        S = self.S
        memo = self.__dict__.setdefault("_fold_memo", {})
        if (s, o) in memo: return memo[(s, o)]
        lines = []
        for t in tp:
            sub = [q for q in S.Cs if q["id"] == t["id"] or q["id"] in S.anc[t["id"]]]
            Q = self._at(sub)
            seated = {}                                         # key -> the offers that seat it at this tip
            for r in K.sel(Q.recs, obj=o):
                if Q._has(r, s): seated.setdefault(r["k"], set()).add(r["offer"])
            lines.append((t, sub, {q["id"] for q in sub}, seated))
        common = frozenset.intersection(*[frozenset(sd) for _, _, _, sd in lines])
        union = frozenset.union(*[frozenset(sd) for _, _, _, sd in lines])
        if len({t.get("regime") for t, _, _, _ in lines}) > 1 and "regime_folds" not in MUT:
            memo[(s, o)] = common
            return common

        def survives(k):
            """k is seated at some tip by an offer that every other line either never held k against, or removed k
            in that offer's past."""
            for _, _, _, sd in lines:
                for off in sd.get(k, ()):
                    ok = True
                    for _, sub2, ids2, sd2 in lines:
                        if k in sd2: continue
                        if off in ids2: ok = False; break       # this line ended the very seat
                        seen = [q for q in sub2 if q["id"] in S.anc[off]]
                        Q2 = self._at(seen)
                        if any(Q2._has(r, s) for r in K.sel(Q2.recs, obj=o, k=k)): ok = False; break   # removed beside it
                    if ok: return True
            return False

        cand = [k for k in sorted(union - common, key=str) if survives(k) or "keeps_removed" in MUT]
        out_keys = union - common - frozenset(cand)             # removed on a line and not added again after it

        def count_holds(k, seated):
            """Every counted offer that adds k meets its count on the voices of keys the fold seats, over the
            members at its heads that the fold seats."""
            if "plain_fold" in MUT: return True
            offs = set()
            for _, _, _, sd in lines: offs |= sd.get(k, set())
            for off in offs:
                r = S.by[off]
                if r.get("conf") != "group":
                    if r["signer"] not in seated and r["signer"] in union: return False
                    continue
                P = [q for q in S.Cs if q["id"] in S.anc[off]]
                past = lambda a, b: a in S.anc[b]
                over, counted = r.get("over", r["obj"]), r.get("counted", "member")
                if (over, counted) == (o, s): ok = seated if "one_step" not in MUT else (union - out_keys)
                else: ok = self.tips_fold(counted, over)                 # another scope's own fold; None: one tip there
                mem = counted_keys(P, past, over, r.get("head", ()), counted)[0] - count_left(P, past, over, counted)
                if ok is not None: mem = mem & ok
                yes = voices(r, P) & mem
                if r.get("policy") in DUTY_POLICY:
                    if not duty_count(r, P, yes, mem): return False
                elif K.rule(POLICY, r.get("policy"), ("unknown",))[0] == "lift":
                    # a re-seating: its voices are the objections it names, over the members the fold seats
                    v = lift_voices(r, P, past, {q["id"]: q for q in P}) or frozenset()
                    yes = v & mem
                    if v: mem = mem - {S.by[r["content"]]["signer"]}   # the author apart (the key removed is an agent's: in no count)
                    if not (2 * len(yes) > len(mem) and len(yes) >= 2): return False
                elif not met(r.get("policy"), len(yes), len(mem), r.get("need")): return False
            return True

        memo[(s, o)] = common                                   # a count over this scope asked meanwhile reads the common keys
        got = common
        while True:                                             # least fixed point: a voice counts once its key is in
            more = got | frozenset(k for k in cand if k not in got and count_holds(k, got))
            if more == got: break
            got = more
        memo[(s, o)] = got
        return got

    def _out(self, s, o):
        """The keys the fold holds out of scope `s` over `o`: seated at some tip, removed on another line, and not
        added again after that removal. Empty with one tip."""
        tp = self.tips(o)
        if len(tp) <= 1: return frozenset()
        S, sets = self.S, []
        for t in tp:
            sub = [q for q in S.Cs if q["id"] == t["id"] or q["id"] in S.anc[t["id"]]]
            Q = self._at(sub)
            sets.append(frozenset(r["k"] for r in K.sel(Q.recs, obj=o) if Q._has(r, s)))
        return frozenset.union(*sets) - frozenset.intersection(*sets) - (self.tips_fold(s, o) or frozenset())

    def one(self, s, o):
        """The single holder, where the seat is single-valued (an owner): two live holders is none."""
        return K.group([r for r in K.sel(self.recs, obj=o) if self._has(r, s)], None, "one", "k")

    def snapshot(self):
        return frozenset((r["k"], r["scope"], r["obj"], r["depth"], r["root"]) for r in self.recs)


# ---- a lone removal in force: the end rule (conferral_end.py, E2 to E8) re-expressed over seat rows ----------------
def holds_roster(S, u, k, obj, r):
    """Unseat u cuts a roster seat key k holds: an offer in u's past seats k over obj in roster scope r (a member's
    seat, the founding seat where it holds `member`, an agent's seat). A cut of a roster scope the key does not hold
    ends no stay, and so no duty seat. (MUTATION roster_cut_any_scope: not read.)"""
    if "roster_cut_any_scope" in MUT: return True
    return any(m["kind"] == "offer" and m.get("obj") == obj and k in m["to"] and m["id"] in S.anc[u["id"]]
               and (m["scope"] == r or (r == "member" and m["id"] == obj and roster_seat(m))) for m in S.Cs)


def lone_act(u, S):
    """u (a counted unseat that counts) is a moderator's lone removal of an agent's key made under the remover's
    standing: it concludes as a lone removal, and the room's count of it is not met (a removal the persons' count
    carries is the count's act, not the moderator's)."""
    if not agent_removal(u) or u.get("conf") != "group": return False
    P = [q for q in S.Cs if q["id"] in S.anc[u["id"]]]
    past = lambda a, b: a in S.anc[b]
    return lone_removal(u, P, past) and ("count_unread_lone" in MUT or not count_met(u, P, past))   # MUTATION: the count unread


def head_of_end(S, E, obj):
    """h_e, the head an end acts from (E1): the heads a counted end names; for a withdrawal, the newest counted acts
    on obj in its past (the newest roster heads its signer holds)."""
    if E["kind"] == "unseat": return tuple(E.get("head", ()))
    acts = [q for q in S.Cs if q["id"] in S.anc[E["id"]] and q["kind"] in ("offer", "unseat") and q.get("obj") == obj
            and (q.get("conf") == "group" or q["id"] == obj)]
    return tuple(a["id"] for a in K.frontier(S.anc, acts))


def later(S, hx, he):
    """A head x names has every head of h_e in its past: x is at a later head than the end (E3). A head of h_e that
    is not held makes nothing later."""
    if any(e not in S.by for e in he): return False
    return bool(he) and any(h in S.anc and all(e in S.anc[h] for e in he) for h in hx)


def standing_ends(S, x, standing, unseats):
    """The rows held that end the remover's standing: a withdrawal of a standing offer by its holder (or by the
    conferrer of an offer that is not counted), of the holder's acceptance of one, or of the holder's stay; a counted
    unseat that cuts the holder's standing seat or its roster seat with a standing offer in its past. Each with the
    standing seats it ends: [(row, seats)]."""
    M, obj, by = x["signer"], x["obj"], S.by
    ids = {o for o, _ in standing}
    of = lambda oids: frozenset(s for s in standing if s[0] in oids)
    out = []
    stay = {w["id"] for w, k, g in stay_ends(K.sel(S.Cs, kind="withdraw"), by) if k == M and g == obj}
    for w in K.sel(S.Cs, kind="withdraw"):
        t = by.get(w["target"])
        if t is None: continue
        if t["kind"] == "offer" and t["id"] in ids and (w.get("scope") is None or (t["id"], w["scope"]) in standing) and (
                w["signer"] == M or (w["signer"] not in t["to"] and t["conf"] != "group" and not duty_seat(by, t))):
            out.append((w, frozenset(s for s in standing if s[0] == t["id"] and w.get("scope") in (None, s[1]))))
        elif t["kind"] == "accept" and t["signer"] == M and w["signer"] == M and t.get("of") in ids:
            out.append((w, of({t["of"]})))
        elif w["id"] in stay and any(o in S.anc[w["id"]] for o in ids):
            out.append((w, of({o for o in ids if o in S.anc[w["id"]]})))
    for u in unseats:
        if u["id"] == x["id"] or M not in u["to"] or u["obj"] != obj or not any(o in S.anc[u["id"]] for o in ids): continue
        if any(("seat", M, r, obj) in u["cuts"] and holds_roster(S, u, M, obj, r) for r in ROSTER_SEATS):
            out.append((u, of({o for o in ids if o in S.anc[u["id"]]})))
        elif any(("seat", M, sc, obj) in u["cuts"] for _, sc in standing):
            out.append((u, frozenset(s for s in standing if s[0] in S.anc[u["id"]] and ("seat", M, s[1], obj) in u["cuts"])))
    return out


def removal_in_force(S, x, unseats, now):
    """CC 4.5.13 read with the end rule (CC 2.4.1.1, CC 4.5.5; conferral_end.py): a moderator's lone removal x is an
    act under its `moderate` standing.
        E7      a seat that gave the remover `moderate` at the head x names is live now (`now`, the seats with every
                removal made) and no end of it is held: in force. A seat taken up after x's head authorises nothing
                earlier, and nothing puts the removal back in force once every such seat has an end held: not the
                same offer accepted again, not a new conferral (CC 2.4.1.1: "A receipt ... revives no act")
        E4      an end of its standing is in x's past: not counted, not in force
        E3      x names a head later than the end's head h_e: not counted, not in force
        E8      x is at h_e or before, or concurrent with it: counted, and in force only under a receipt of it that
                does not have the end in its past, by a duty holder at the head x names other than the remover
                (an `ack` row whose `of` is x); never by the remover itself
        E2      otherwise counted at its own head and not in force
    With several ends held, in force only where each keeps it. Where the standing is gone and no end of it is held
    (it fell with a seat above it), E2 and E8 with no end."""
    M, obj = x["signer"], x["obj"]
    standing, duty = set(), None
    for h in x.get("head", ()):
        sub = [q for q in S.Cs if q["id"] == h or q["id"] in S.anc.get(h, ())]
        Q = seats_of(sub)
        standing |= {(r["offer"], r["scope"]) for r in Q.recs if r["k"] == M and r["obj"] == obj and Q._has(r, "moderate")}
        d = Q.holders("duty", obj)
        duty = d if duty is None else duty & d
    duty = (duty or frozenset()) - (frozenset() if "remover_receipt" in MUT else {M})
    acks = [q for q in S.Cs if q["kind"] == "ack" and q.get("of") == x["id"] and q["signer"] in duty]
    kept = lambda E: any(E is None or E["id"] not in S.anc[q["id"]] for q in acks)
    # an end in the past of the head x names did not end the standing live there (a seat taken up again after it)
    found = [(E, sc) for E, sc in standing_ends(S, x, standing, unseats)
             if not all(E["id"] == h or E["id"] in S.anc.get(h, ()) for h in x.get("head", ()))]
    ended = frozenset().union(*(sc for _, sc in found)) if found else frozenset()
    live = {(r["offer"], r["scope"]) for r in now.recs if r["k"] == M and r["obj"] == obj}
    if now.stands(M, "moderate", obj) and ("reseat_revives" in MUT or any(s in live and s not in ended for s in standing)):
        return True                                             # MUTATION reseat_revives: any standing now keeps it
    ends = [E for E, _ in found]
    if not ends: return kept(None)
    for E in ends:
        if E["id"] in S.anc[x["id"]] or later(S, x.get("head", ()), head_of_end(S, E, obj)) or not kept(E):
            return False
    return True


def out_of_force(S, unseats, holds, confers, depth, own, checkpoint):
    """The lone removals among `unseats` the end rule holds out of force over S."""
    acts = [u for u in unseats if u.get("scope") == AGENT and lone_act(u, S)]
    if not acts: return frozenset()
    now = Seats(S, holds, confers, depth, own=own, checkpoint=checkpoint, drop=frozenset())
    return frozenset(x["id"] for x in acts if not removal_in_force(S, x, unseats, now))


def stands(S, root, k, s, o, **kw):
    return Seats(S, **kw).stands(k, s, o, root)


# ---- concluded: was the offer, the unseat, the withdrawal validly made, at the head it names -------------
def members_at(P, past, obj, heads, scope="member"):
    """The live `scope` seats over obj, read from the rows in the past of the heads only. Several heads: the
    keys common to all of them (KERNEL.md section 7)."""
    out = None
    for h in heads:
        sub = [q for q in P if q["id"] == h or past(q["id"], h)]
        if not any(q["id"] == h for q in sub): return frozenset()
        m = seats_of(sub).holders(scope, obj)
        out = m if out is None else out & m
    return out or frozenset()


_SEATS_OF = {}


def seats_of(rows):
    """The seats over a set of rows, each taken as concluded, kept once built: a head's past is read again by every
    row that names it, and a chain of lone removals reads every earlier one's (the run is polynomial in the chain,
    not exponential). The key is the rows themselves (by identity, held in the value so none is reused), the planted
    breaks switched on, and the tables a check may change (what a seat holds, the policies, the enders)."""
    key = (frozenset(id(q) for q in rows), frozenset(MUT), repr(sorted(HOLDS.items())), repr(sorted(POLICY.items())),
           repr(sorted(ENDS.items())))
    got = _SEATS_OF.get(key)
    if got is None:
        got = _SEATS_OF[key] = (tuple(rows), Seats(CK.State(list(rows), {q["id"]: True for q in rows})))
    return got[1]


def agents_at(P, past, obj, heads):
    """The keys holding an AI agent's seat over obj at the heads (`agent`): on the roster, in no count."""
    if not any(q.get("scope") == AGENT for q in P): return frozenset()
    return members_at(P, past, obj, heads, AGENT)


def counted_keys(P, past, obj, heads, scope="member"):
    """(over, voters): the keys a count over `scope` at the heads is taken of, and those whose signatures are its
    voices. Every count of a room is by person (CC 4.5.13: an agent "has no vote"; "a recall and an election count its
    persons alone"), so an agent's key is in neither, whatever scope it holds besides."""
    m = members_at(P, past, obj, heads, scope)
    if scope == AGENT: return m, m
    a = agents_at(P, past, obj, heads)
    over = m | a if "agent_counted_over" in MUT else m - a      # MUTATION: the agent is counted over (no voice)
    voters = m | a if "agent_voice" in MUT else m - a           # MUTATION: the agent's signature is a voice
    return over, voters


def left_in_past(P, obj, scope="member"):
    """The keys whose own leaving is among P (a version's past): a concluded withdrawal, signed by the key, of the
    acceptance or offer that seats it in `scope` over obj. KERNEL.md 6 and 7; RosterHead.lean leaving_binds_by_past:
    a version that has a key's leaving in its own past does not count that key, whatever head it names."""
    if "leaving_unread" in MUT: return frozenset()
    by = {q["id"]: q for q in P}
    out = set()
    for w in P:
        if w["kind"] != "withdraw": continue
        t = by.get(w["target"])
        # a withdrawal that names a scope leaves that one seat of the row it withdraws (a founder's duty laid down)
        ts = w["scope"] if w.get("scope") is not None and "scope_unread" not in MUT else t.get("scope") if t else None
        if t is None or t.get("obj") not in (obj, None) or ts not in (scope, None): continue
        if (t["kind"] == "accept" and t["signer"] == w["signer"]) or (t["kind"] == "offer" and w["signer"] in t["to"]):
            out.add(w["signer"])
    return frozenset(out)


def stay_ended_in_past(P, past, obj):
    """The keys whose own end of a stay as a member of obj is among P (a counted row's past) with no admission of the
    key after it there: a count over the duty holders that has such an end in its past does not count that key, since
    the end ended its duty seats. The counted removal needs no such reading: it is a head, read by members_at."""
    if "leaving_unread" in MUT or "resign_keeps_duty" in MUT: return frozenset()
    by = {q["id"]: q for q in P}
    if not community(by, obj): return frozenset()
    back = lambda w, k: any(m["kind"] == "offer" and m["obj"] == obj and k in m["to"] and roster_seat(m) and past(w["id"], m["id"]) for m in P)
    return frozenset(k for w, k, g in stay_ends(P, by) if g == obj and not back(w, k))


def count_left(P, past, obj, scope):
    """The keys a count over `scope` at obj leaves out for a leaving in its row's past: the leaving of that seat, and for
    a count over duty holders, the end of the key's stay as a member. A count over another scope is as it was."""
    out = left_in_past(P, obj, scope)
    by = {q["id"]: q for q in P}
    return out | stay_ended_in_past(P, past, obj) if is_duty(scope, declared(by, obj)) else out


def voices(r, P):
    """The keys that signed r: its signer, its cosigners, and the signers of the cosign rows it names that themselves
    name every head r is counted over."""
    heads = set(r.get("head", ()))
    return signers(r) | frozenset(c["signer"] for c in K.sel(P, kind="cosign", of=r.get("content", r["id"]))
                                  if c["id"] in r["names"] and heads <= set(c["names"]))


def _revoked_before(r, P):
    if "reseat" in MUT: return False
    return any(q["kind"] == "unseat" and q["scope"] in FINAL and set(q["cuts"]) & set(r.get("on", ())) for q in P)


def _ender(r, P, by):
    """An unseat by the holder of a seat over the same object (ENDS). Read over the unseat's own past only: the
    ender's seat stands there, and it is the one live holder of that scope over the object."""
    if "any_key_revokes" in MUT: return True
    up = by.get(r.get("under"))
    if up is None or up["kind"] != "offer" or up["obj"] != r["obj"] or r["signer"] not in up["to"]: return False
    if r["scope"] not in ENDS.get(up["scope"], ()): return False
    # it ends another scope's seat of the object's own key, or (the same scope) the ender's own seat
    if tuple(r["to"]) != ((r["signer"],) if r["scope"] == up["scope"] else (r["obj"],)): return False
    if "owner_unread" in MUT: return True                         # MUTATION: the binding named is enough
    sole = Seats(CK.State(P, {q["id"]: True for q in P}))
    if "owner_any_live" in MUT: return sole.stands(r["signer"], up["scope"], r["obj"])
    return sole.one(up["scope"], r["obj"]) == r["signer"]


def count_met(r, P, past, table=None):
    """A counted row's count (conf=group), met over its concluded ancestors P: the lift, the ranked tally, the duty
    count, or the policy's threshold over the persons at the heads it names."""
    k, by, heads = r["kind"], {q["id"]: q for q in P}, r.get("head", ())
    if K.rule(table or POLICY, r.get("policy"), ("unknown",))[0] == "lift": return lift_count(r, P, past, by)
    mem, vot = counted_keys(P, past, r.get("over", r["obj"]), heads, r.get("counted", "member"))
    left = count_left(P, past, r.get("over", r["obj"]), r.get("counted", "member"))
    mem, vot = mem - left, vot - left
    if K.rule(table or POLICY, r.get("policy"), ("unknown",))[0] == "ranked":
        # the count is the ranked tally: the ballots the row names, one voice each, and the row seats the winner
        ballots = [(b["signer"], b["ranking"]) for b in K.sel(P, kind="ballot") if b["id"] in r["names"] and b["signer"] in vot]
        # the one ranked row is the election, which declares no order: a tie for weakest seats nobody (CC 4.5.13)
        return k == "offer" and bool(ballots) and RANKED(ballots, list(r["options"]), declared=False)[0] == r["to"][0]
    if r.get("policy") in DUTY_POLICY: return duty_count(r, P, voices(r, P) & vot, mem)
    return met(r.get("policy"), len(voices(r, P) & vot), len(mem), r.get("need"), table)


def seat_rule(r, P, past, table=None, other=None):
    """The conclusion rule. P: r's concluded ancestors."""
    k, by = r["kind"], {q["id"]: q for q in P}
    if k in ("offer", "unseat"):
        conf = r["conf"]
        if k == "offer" and _revoked_before(r, P): return False   # a revoked key does not re-seat itself (FINAL)
        if k == "offer" and conf in ("self", "seat") and duty_seat(by, r) and not _lone(r, P, by): return False
        if conf == "self":
            if r["obj"] == r["id"]: return k == "offer"          # a founding row is its own object
            if k == "unseat" and founding_many(by, r["obj"]): return False    # among several founding keys, ending a seat takes the count
            return r["signer"] in own_keys(by, r["obj"]) and (r["obj"] not in by or True)
        if conf == "seat":
            if k == "unseat": return _ender(r, P, by)
            return k == "offer" and r.get("under") in by and r["signer"] in by[r["under"]]["to"]
        if conf == "group":
            if k == "unseat" and lone_removal(r, P, past): return True          # CC 4.5.13: a moderator, an agent's key
            return count_met(r, P, past, table)
        return False
    if k == "accept":
        return r["of"] is None or (r["of"] in by and r["signer"] in by[r["of"]].get("to", ()))
    if k == "withdraw":
        t = by.get(r["target"])
        return t is not None and (r["signer"] in signers(t) or (t["kind"] == "offer" and r["signer"] in t["to"]))
    if k == "cosign":
        return True
    return other(r, P, past) if other else True
