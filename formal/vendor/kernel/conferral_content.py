"""
conferral_content.py: room content after a member's seat ends, where the END names the rows held good
(the Constitution's proposal of 2026-11-22, second form, for CC 2.4.1.1 and persist v62.0). A reference: from a
set of rows, for every content row of the member, whether it is COUNTED at its own head and whether it is IN
FORCE (in the room's content) now, and the rule that decides it.

The proposal.
1. A content row (a message, a file placement, a reaction, and an edit or a retraction of one: on the wire each
   is a composer its author signs) is an act under its signer's membership. It names the roster head it is at
   and, in `prev`, its author's current newest content rows in the room: its predecessors, a set. A person
   signs from several devices, under one key or several, so a series forks routinely; a row that names both
   branches joins them. "The member's own row" means signed by any key of the member (B and B2 here); M is a
   co-member, whose rows are not this member's.
2. A row that ends the member's seat (a counted removal, or the member's own resignation) names in
   `trusted_through` the newest rows of the member its signers hold good: the tips, a set.
3. NOTHING WAITS ON CONTENT. A tip is not among the rows an end names for the door, and a predecessor is not
   among the rows a content row names for it: `prev`, `trusted_through` and a retraction's `target` are read by
   the fold and make no row wait. A tip that is not held keeps nothing; when it arrives, it and its held
   ancestors are kept. A predecessor that is not held is not followed, so what lies behind it is not kept
   until it arrives. A row named by id is fixed by that id: what an ended member signs later is never the row
   a tip or a predecessor already names.
4. After the end, a content row of the member is in the room's content when it is a named tip that is held, or
   an ancestor of one along `prev` among its author's own rows. Every other content row of theirs counts at its
   own head and is not in the room's content.
5. Tips only grow: a later counted row of the same body (`tips`) may name further tips, and the kept set is the
   union. No co-member receipts content.

6. SEAT BY SEAT. A seat is one stay: from the roster version that admits the member to the end of that stay.
   A later version that admits the member again begins another seat. A content row, and an end, belong to the
   seat of the head they name; a row adding tips belongs to the seat of the end it extends. Each seat's
   content is judged by that seat's own ends and tips and by nothing of another seat:
   - the head a row names decides, never when it was signed or received: a row signed after a re-admission
     that names an old head is a row of the old seat;
   - a re-admission restores nothing: what an earlier end did not hold good stays out;
   - the walk from a tip does not cross seats, so rejoining, naming old rows as predecessors and leaving again
     brings nothing back;
   - a row naming a head at which the member does not sit belongs to no seat and does not count.

No instant is read and no arrival order: the answer is a function of the held rows. One member and its content
are modelled (keys B and B2); other members' content is untouched by any of this. Not modelled here: receipts
(conferral_end.py), the reader's line on the end (conferral_end.py: `end_void.line`), key removals.

Rows (the kernel's row shape: `id`, `kind`, `signer`, the ids it `names`, and the fields a rule reads):
    head   a roster version; `names` the heads it extends; `seat`: "admits" where the version admits the member
           (a stay begins), "out" where it does not list the member, absent or "sits" where the member sits on
    act    a content row of the member: `signer` the key (B or B2), `head` the roster head it names, `prev` the
           list of its predecessors (empty for a first row), and for an edit or a retraction `target`, the row
           it composes on, and `compose` ("edit" or "retract"). An edit is a content row like any other, and
           no rule reads its `target`. A retraction is read: see W.retracted
    end    an end of the member's seat: `signer` "count" (a counted removal) or a key of the member (its own
           resignation), `head` (h_e), `trusted_through` the tips it holds good (a list; empty where its signers
           hold none, which on the wire is the member's absence). The tips are NOT in `names`
    tips   a later row naming further tips: `extends` the end it adds to (which it names), `trusted_through`,
           and `head`, the roster head it is counted over (a counted row names one; no rule here reads it)

Which ends count:
    end_void.stale_head  E1: the end has a head later than h_e in its own past: it concludes nothing
    end_void.seat_ended  the end has a counting end of the seat in its own past: the seat was already ended
Whether an end counts is decided by its own causal past alone, so no row signed later changes it. In
particular the member's own end is NOT voided for naming a head later than another end's: under that rule the
exhaustive check found the member reviving a row that named its first resignation, by signing a second one at
an older head. An extra end of the member's own only ever takes rows out (E3, E4, and the rule below).

Whose tips are read (`merge`). The proposal's third point read literally is `union`, and
check_conferral_content.py shows that under it an ended member adds content for ever, by signing a further
resignation at the head it last sat at. The reference's default closes that:
    count_first             (default) the count's word: the union of the tips of every counted end that is not
                            stale and of every counted `tips` row. The member's own ends are read only where no
                            counted end counts, and then a row stays only where EVERY one of them holds it
                            good, so a second resignation can remove but never add. A `tips` row signed by the
                            member is never read.
    union                   the union of the tips of every end that counts, the member's own included, and of
                            every counted `tips` row
    count_first_self_union  count_first, but where only the member's own ends speak, the union of them

Rules for a content row, in the order they decide (the name a failing test reports):
    no_seat          the row names a head at which the member does not sit: not counted
    no_end           no end counts: counted and in force
    E4.names_end     the row has a counting end in its past: not counted
    E3.later_head    the row names a head that has a counting end's h_e in its past: the seat is ended there
    W.retracted      counted, not in force: a retraction of the row by the member, under any of its keys, is
                     held (a person retracts from a second device). The Constitution's ruling of 2026-11-22:
                     an author's retraction of its own row takes effect whenever it is signed, before or after
                     an end, whether or not the retraction itself counts or is kept, and a retraction of a
                     retraction restores nothing. It can only take a row out. A co-member's is not read
    T.held_good      counted and in force: a held tip that is read, or its ancestor along `prev` among the
                     member's own rows, by any of its keys
    E2.forward       counted at its own head, not in force: not held good
"""

KEYS, COUNT = ("B", "B2"), "count"
MERGES = ("count_first", "union", "count_first_self_union")


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


def counting_ends(rows, world=None):
    """{end id: None if it counts, else the rule that voids it}, for the ends among `rows` (one seat's). The
    causal past is read over `world`, every held row: an end's past is what it names, in any seat."""
    by, anc = _past(world or rows)
    ends = [r for r in rows if r["kind"] == "end"]
    later = lambda h, he: he in anc(h) if h in by else False
    memo = {}

    def void(e):
        i = e["id"]
        if i in memo:
            return memo[i]
        if any(later(h, e["head"]) for h in anc(i) if h in by and by[h]["kind"] == "head"):
            memo[i] = "end_void.stale_head"     # decided from the heads alone, before any other end is asked
            return memo[i]
        seated = any(o["id"] in anc(i) and void(o) is None for o in ends if o is not e)   # ends in e's own past
        memo[i] = "end_void.seat_ended" if seated else None
        return memo[i]
    return {e["id"]: void(e) for e in ends}


def held_good(rows, r):
    """The content rows a row's tips hold good: each named tip that is held and is a content row of the member,
    and its ancestors along every `prev` that is a held row of the member (by any of its keys)."""
    by = {x["id"]: x for x in rows}
    out, todo = set(), list(r.get("trusted_through", ()))
    while todo:
        t = todo.pop()
        x = by.get(t)
        if x is None or x["kind"] != "act" or x["signer"] not in KEYS or t in out:
            continue
        out.add(t)
        for q in x.get("prev") or ():
            p = by.get(q)
            if p is not None and p["signer"] in KEYS:          # the member's own row, by any of its keys
                todo.append(q)
    return out


def kept(rows, merge="count_first", self_tips=False, world=None):
    """The content rows held good by the tips that are read under `merge`. `self_tips` is a plant: a `tips` row
    signed by the member is read."""
    void = counting_ends(rows, world)
    ends = [r for r in rows if r["kind"] == "end"]
    counts = [e for e in ends if void[e["id"]] is None]
    c_ends = [e for e in ends if e["signer"] == COUNT and void[e["id"]] != "end_void.stale_head"]
    own = [e for e in counts if e["signer"] in KEYS]
    adds = [r for r in rows if r["kind"] == "tips" and (r["signer"] == COUNT or self_tips)]
    union = lambda rs: set().union(*[held_good(rows, r) for r in rs]) if rs else set()
    if merge == "union":
        return union(counts + adds)
    if any(e["signer"] == COUNT for e in counts):
        return union(c_ends + adds)
    if merge == "count_first_self_union":
        return union(own + adds)
    good = [held_good(rows, e) for e in own]
    return (set.intersection(*good) if good else set()) | union(adds)


def seats(rows):
    """{row id: its seat} for every content row, end and tips row. A seat is the set of the newest admitting
    heads in the past of the head the row names, that head included (the empty set where none admits: the one
    seat of a history with no re-admission). None for a row that names a head at which the member does not
    sit, a head that is not held, or (a tips row) an end that is not held: it belongs to no seat. A removal is
    the member's end and also a version of the roster: a row that names an end as its head names a head at
    which the member is out."""
    by, anc = _past(rows)
    admits = [r["id"] for r in rows if r["kind"] == "head" and r.get("seat") == "admits"]

    def of_head(h):
        if h not in by or by[h].get("seat") == "out" or by[h]["kind"] == "end":
            return None                       # an end of the member's seat named as a head: the member is out at it
        mine = [a for a in admits if a == h or a in anc(h)]
        return frozenset(a for a in mine if not any(a in anc(b) for b in mine))
    out = {}
    for r in rows:
        if r["kind"] in ("act", "end"):
            out[r["id"]] = of_head(r["head"])
    for r in rows:
        if r["kind"] == "tips":
            out[r["id"]] = out.get(r["extends"])
    return out


def ended_seats(rows, merge="count_first"):
    """({seats with an end that counts}, {seats with a counted end that counts})."""
    seat = seats(rows)
    heads = [r for r in rows if r["kind"] == "head"]
    some, counted = set(), set()
    for s in {v for v in seat.values() if v is not None}:
        sub = heads + [r for r in rows if seat.get(r["id"]) == s]
        void = counting_ends(sub, rows)
        ends = [r for r in sub if r["kind"] == "end" and void[r["id"]] is None]
        if ends:
            some.add(s)
        if any(e["signer"] == COUNT for e in ends):
            counted.add(s)
    return some, counted


def answers(rows, merge="count_first", self_tips=False):
    """{content row id: {"counted": bool, "in_force": bool, "rule": str}} over the held `rows`: each seat's rows
    judged by that seat's own ends and tips."""
    seat = seats(rows)
    heads = [r for r in rows if r["kind"] == "head"]
    out = {r["id"]: {"counted": False, "in_force": False, "rule": "no_seat"}
           for r in rows if r["kind"] == "act" and r["signer"] in KEYS and seat[r["id"]] is None}
    # a retraction is read over all the held rows, whatever seat it or its target belongs to
    by = {r["id"]: r for r in rows}
    retracted = {r["target"] for r in rows if r["kind"] == "act" and r.get("compose") == "retract"
                 and r["signer"] in KEYS and r.get("target") in by and by[r["target"]]["signer"] in KEYS}
    for s in {v for v in seat.values() if v is not None}:
        out.update(_seat_answers(heads + [r for r in rows if seat.get(r["id"]) == s], merge, self_tips, retracted,
                                 rows))
    return out


def _seat_answers(rows, merge, self_tips, retracted, world):
    """The answers over the rows of one seat (and the roster heads)."""
    assert merge in MERGES, merge
    by, anc = _past(world)
    void = counting_ends(rows, world)
    ends = [by[i] for i in sorted(void) if void[i] is None]
    later = lambda h, he: he in anc(h) if h in by else False
    good = kept(rows, merge, self_tips, world)
    out = {}
    for r in rows:
        if r["kind"] != "act" or r["signer"] not in KEYS:      # another member's row is not this member's content
            continue
        x = r["id"]
        if any(e["id"] in anc(x) for e in ends):
            a = (False, False, "E4.names_end")
        elif any(later(r["head"], e["head"]) for e in ends):
            a = (False, False, "E3.later_head")
        elif x in retracted:
            a = (True, False, "W.retracted")
        elif not ends:
            a = (True, True, "no_end")
        elif x in good:
            a = (True, True, "T.held_good")
        else:
            a = (True, False, "E2.forward")
        out[x] = dict(zip(("counted", "in_force", "rule"), a))
    return out


def shown_first_held(rows, order, merge="count_first"):
    """The node-local fallback persist floated, NOT part of the proposal: a counted content row this reader held
    before it held any end that counts stays shown to this reader. {content row id: bool}. It reads the arrival
    `order`, so it is not a function of the held rows; check_conferral_content.py shows what follows."""
    final = answers(rows, merge)
    void = counting_ends(rows)                 # read over one seat: the cases it is run on have one
    first_end = min([order.index(i) for i in void if void[i] is None] or [len(order)])
    return {x: a["counted"] and (a["in_force"] or order.index(x) < first_end) for x, a in final.items()}


# ---- the case table: hand-written expectations, which the reference must meet --------------------------------
def head(i, *names, seat=None):
    return dict({"id": i, "kind": "head", "signer": COUNT, "names": list(names)}, **({"seat": seat} if seat else {}))


def act(i, h, prev=(), names=(), signer="B", **kw):
    prev = [prev] if isinstance(prev, str) else sorted(prev or ())
    # `names` is what the door waits on: the head and what the row cites. A predecessor and a retraction's
    # target are read by the fold and make no row wait
    return dict({"id": i, "kind": "act", "signer": signer, "head": h, "prev": prev,
                 "names": sorted(set(names) | {h})}, **kw)


def end(i, h, tips=(), signer=COUNT, names=()):
    return {"id": i, "kind": "end", "signer": signer, "head": h, "trusted_through": sorted(tips),
            "names": sorted(set(names) | {h})}                 # the tips are not named: the end never waits


def tips(i, extends, tps, signer=COUNT, h="H0"):
    return {"id": i, "kind": "tips", "signer": signer, "head": h, "extends": extends,
            "trusted_through": sorted(tps), "names": sorted({extends, h})}


H0, H1 = head("H0"), head("H1", "H0")
HX, HA = head("HX", "H0", seat="out"), head("HA", "HX", seat="admits")
T, F = True, False
M1, M2, M3 = act("m1", "H0"), act("m2", "H0", "m1"), act("m3", "H0", "m2")
KEPT, OUT = (T, T, "T.held_good"), (T, F, "E2.forward")

# (name, about, rows, params, {act: (counted, in_force, rule)}, arrival orders a node may take them in)
CASES = [
    ("content_no_end", "no end held: a member's content rows count and are in the room's content",
     [H0, M1, M2], {}, {"m1": (T, T, "no_end"), "m2": (T, T, "no_end")}),
    ("removal_names_tip", "a counted removal names the newest row of the member's series: the whole series "
     "behind it stays in the room's content",
     [H0, M1, M2, M3, end("E", "H0", ["m3"])], {}, {"m1": KEPT, "m2": KEPT, "m3": KEPT}),
    ("removal_signers_hold_nothing", "the removal's signers held none of the member's content, so it names no "
     "tip: rows that reach a reader are counted at their head and not in the room's content, until a counted "
     "row names a tip",
     [H0, M1, M2, end("E", "H0")], {}, {"m1": OUT, "m2": OUT}),
    ("removal_in_flight_row", "the removers had not yet held m3 when they signed (it is concurrent with the end): "
     "m3 is out for everyone, honest or not; no rule can tell which",
     [H0, M1, M2, M3, end("E", "H0", ["m2"])], {}, {"m1": KEPT, "m2": KEPT, "m3": OUT}),
    ("in_flight_row_named_later", "the same rows, and then a counted row of the body names m3: tips only grow, "
     "and m3 is in the room's content from then on",
     [H0, M1, M2, M3, end("E", "H0", ["m2"]), tips("A", "E", ["m3"])], {}, {"m1": KEPT, "m2": KEPT, "m3": KEPT}),
    ("adding_row_waits_for_its_end", "a row that adds tips names the end it extends, so no node holds it before "
     "that end: in every arrival order the door allows, the end comes first",
     [H0, M1, M2, end("E", "H0", ["m1"]), tips("A", "E", ["m2"])], {}, {"m1": KEPT, "m2": KEPT},
     [["H0", "m1", "m2", "E", "A"], ["H0", "m1", "E", "m2", "A"]]),
    ("removed_member_keeps_posting", "after the removal the member signs m3 at the last head it sat at, not "
     "naming the end, and it arrives after the end at a node that never saw it: admitted, counted at its head, "
     "never in the room's content; the same answer in every arrival order",
     [H0, H1, M1, M2, end("E", "H0", ["m2"]), act("m3", "H0", "m2")], {}, {"m1": KEPT, "m2": KEPT, "m3": OUT},
     [["H0", "H1", "m1", "m2", "E", "m3"], ["H0", "m1", "m2", "m3", "H1", "E"]]),
    ("row_at_later_head", "a content row naming a roster head later than h_e: the member's seat is ended there, "
     "and the row does not count",
     [H0, H1, M1, end("E", "H0", ["m1"]), act("m2", "H1", "m1")], {},
     {"m1": KEPT, "m2": (F, F, "E3.later_head")}),
    ("row_names_end", "a content row that has the end in its past does not count, whatever head it names",
     [H0, M1, end("E", "H0", ["m1"]), act("m2", "H0", "m1", ["E"])], {},
     {"m1": KEPT, "m2": (F, F, "E4.names_end")}),
    ("resignation_names_tip", "the member's own resignation names its own newest row, which no one else holds "
     "yet: the resignation concludes at once (the seat ends; nothing waits), and when m2 arrives it and what is "
     "behind it are kept",
     [H0, M1, M2, end("R", "H0", ["m2"], "B")], {}, {"m1": KEPT, "m2": KEPT},
     [["H0", "m1", "R", "m2"], ["H0", "m1", "m2", "R"]]),
    ("end_names_tip_never_held", "the end names a tip that never arrives: it keeps nothing, and no rule tells "
     "this end from one that names no tip, so the member's held rows are out",
     [H0, M1, end("E", "H0", ["m9"])], {}, {"m1": OUT}),
    ("tip_arrives_after_end", "the removal names m2, and m2 reaches this node after the removal: out until then, "
     "kept from then on; the same answer in every arrival order once the rows are held",
     [H0, M1, end("E", "H0", ["m2"]), M2], {}, {"m1": KEPT, "m2": KEPT},
     [["H0", "m1", "E", "m2"], ["H0", "m1", "m2", "E"], ["H0", "E", "m1", "m2"]]),
    ("fork_of_one_series", "one key forked its own series (m2 and x2 both follow m1): the end names one branch, "
     "and only that branch and what is behind it stay; the other branch is out until a counted row names it",
     [H0, M1, M2, act("x2", "H0", "m1"), end("E", "H0", ["m2"])], {}, {"m1": KEPT, "m2": KEPT, "x2": OUT}),
    ("fork_both_branches_named", "the enders hold both branches of a fork and name both: tips are a set, and "
     "both branches stay",
     [H0, M1, M2, act("x2", "H0", "m1"), end("E", "H0", ["m2", "x2"])], {}, {"m1": KEPT, "m2": KEPT, "x2": KEPT}),
    ("fork_rejoined", "two devices forked the series (m2, x2) and a later row names both as its predecessors: "
     "one tip keeps both branches",
     [H0, M1, M2, act("x2", "H0", "m1"), act("j3", "H0", ["m2", "x2"]), end("E", "H0", ["j3"])], {},
     {"m1": KEPT, "m2": KEPT, "x2": KEPT, "j3": KEPT}),
    ("kept_post_edited_before_end", "the member edited its post m1 before the removal, and the edit is behind the "
     "named tip: the edit is kept with its target",
     [H0, M1, act("e2", "H0", "m1", target="m1", compose="edit"), end("E", "H0", ["e2"])], {},
     {"m1": KEPT, "e2": KEPT}),
    ("kept_post_edited_after_end", "after the removal the member signs an edit of its kept post m1 at the old "
     "head: the edit is a content row no tip names, so it is out though its target is kept. A composer does "
     "NOT follow its target into the content; if it did, an ended member would rewrite its kept posts",
     [H0, M1, end("E", "H0", ["m1"]), act("e2", "H0", "m1", target="m1", compose="edit")], {},
     {"m1": KEPT, "e2": OUT}),
    ("kept_post_retracted_after_end", "the same with a retraction: the retraction row is out of the content like "
     "any row no tip names, and it still takes effect: an author's retraction of its own row takes effect "
     "whenever it is signed, so the kept post leaves the room's content. It can only take a row out",
     [H0, M1, end("E", "H0", ["m1"]), act("w2", "H0", "m1", target="m1", compose="retract")], {},
     {"m1": (T, F, "W.retracted"), "w2": OUT}),
    ("post_retracted_no_end", "with no end held: a member retracts its own post, and the post is out",
     [H0, M1, act("w2", "H0", "m1", target="m1", compose="retract")], {},
     {"m1": (T, F, "W.retracted"), "w2": (T, T, "no_end")}),
    ("retraction_from_a_second_device", "the member retracts its post from its second key: its own retraction, "
     "and it takes effect",
     [H0, M1, end("E", "H0", ["m1"]), act("w2", "H0", target="m1", compose="retract", signer="B2")], {},
     {"m1": (T, F, "W.retracted"), "w2": OUT}),
    ("retraction_by_a_co_member", "a co-member signs a retraction of the member's post: not its author's, and "
     "not read by this rule",
     [H0, M1, end("E", "H0", ["m1"]), act("w2", "H0", target="m1", compose="retract", signer="M")], {},
     {"m1": KEPT}),
    ("retraction_of_a_retraction", "the member retracts its retraction: nothing is restored, or an ended member "
     "would add a row back",
     [H0, M1, end("E", "H0", ["m1"]), act("w2", "H0", "m1", target="m1", compose="retract"),
      act("w3", "H0", "w2", target="w2", compose="retract")], {},
     {"m1": (T, F, "W.retracted"), "w2": (T, F, "W.retracted"), "w3": OUT}),
    ("retraction_that_does_not_count", "the retraction names the end (so as an act under the ended seat it does "
     "not count, E4): it is still its author's own retraction and takes effect",
     [H0, M1, end("E", "H0", ["m1"]), act("w2", "H0", "m1", ["E"], target="m1", compose="retract")], {},
     {"m1": (T, F, "W.retracted"), "w2": (F, F, "E4.names_end")}),
    ("middle_of_chain_not_held", "the tip m3 is held, its predecessor m2 is not, and m1 behind that is held: "
     "nothing shows m1 is m3's ancestor, so m1 is not kept until m2 arrives",
     [H0, M1, M3, end("E", "H0", ["m3"])], {}, {"m1": OUT, "m3": KEPT}),
    ("middle_of_chain_arrives", "the same, and m2 arrives: m2 and m1 are kept; the same answer in every arrival "
     "order once all three are held, m2 last included",
     [H0, M1, M3, end("E", "H0", ["m3"]), M2], {}, {"m1": KEPT, "m2": KEPT, "m3": KEPT},
     [["H0", "m1", "m3", "E", "m2"], ["H0", "E", "m3", "m1", "m2"], ["H0", "m2", "m1", "m3", "E"]]),
    ("fork_other_branch_named_later", "the same fork, and a counted row then names the other branch's tip: both "
     "branches stay",
     [H0, M1, M2, act("x2", "H0", "m1"), end("E", "H0", ["m2"]), tips("A", "E", ["x2"])], {},
     {"m1": KEPT, "m2": KEPT, "x2": KEPT}),
    ("second_key_never_seen", "the member's second key signed a series the enders never held: the end names one "
     "tip, of the first key's series, and the whole second series is out",
     [H0, M1, M2, act("n1", "H0", signer="B2"), act("n2", "H0", "n1", signer="B2"), end("E", "H0", ["m2"])], {},
     {"m1": KEPT, "m2": KEPT, "n1": OUT, "n2": OUT}),
    ("second_key_named_later", "the same rows, and a counted row then names the second series' tip: it is in",
     [H0, M1, M2, act("n1", "H0", signer="B2"), act("n2", "H0", "n1", signer="B2"), end("E", "H0", ["m2"]),
      tips("A", "E", ["n2"])], {}, {"m1": KEPT, "m2": KEPT, "n1": KEPT, "n2": KEPT}),
    ("prev_across_the_members_keys", "a row signed by the member's second key names a row of its first key as "
     "its predecessor: both are the member's own, and the walk follows",
     [H0, M1, act("n1", "H0", "m1", signer="B2"), end("E", "H0", ["n1"])], {}, {"m1": KEPT, "n1": KEPT}),
    ("prev_through_a_co_members_row", "the member's row names a CO-MEMBER's row as its predecessor, and that row "
     "names the member's m1: the walk does not pass through another member's row, so m1 is not kept",
     [H0, M1, act("q1", "H0", "m1", signer="M"), act("n1", "H0", "q1"), end("E", "H0", ["n1"])], {},
     {"m1": OUT, "n1": KEPT}),
    ("two_removals_different_tips", "two counted removals of the member at one head, concurrent, naming "
     "different tips: both are the count's word, and the kept set is the union; nothing waits",
     [H0, M1, M2, M3, end("E", "H0", ["m3"]), end("E2", "H0", ["m2"])], {}, {"m1": KEPT, "m2": KEPT, "m3": KEPT}),
    ("removal_then_backdated_resignation", "after a removal that kept m1 only, the member signs m2 and a "
     "resignation at the old head naming m2, neither naming the removal: where a counted end counts the "
     "member's own end is not read, so m2 is not added",
     [H0, M1, end("E", "H0", ["m1"]), M2, end("R", "H0", ["m2"], "B")], {}, {"m1": KEPT, "m2": OUT}),
    ("removal_then_backdated_resignation_union", "the same rows under the proposal's third point read literally "
     "(`union`): the member's own later resignation adds m2. This is the hole count_first closes",
     [H0, M1, end("E", "H0", ["m1"]), M2, end("R", "H0", ["m2"], "B")], {"merge": "union"},
     {"m1": KEPT, "m2": KEPT}),
    ("two_resignations", "the member signs two resignations at one head naming different tips (a fork of its own "
     "end): a row stays only where both hold it good, so a second resignation never adds a row",
     [H0, M1, M2, end("R", "H0", ["m1"], "B"), end("R2", "H0", ["m2"], "B")], {}, {"m1": KEPT, "m2": OUT}),
    ("resignation_then_counted_tips", "the member resigned naming m1, and no counted row ends the seat; a "
     "counted row then names m2: the member's own tips are still read and the counted row's are added",
     [H0, M1, act("x1", "H0"), end("R", "H0", ["m1"], "B"), tips("A", "R", ["x1"])], {},
     {"m1": KEPT, "x1": KEPT}),
    ("resignation_counted_tips_then_narrowing", "the same, and the member then signs a second resignation "
     "naming nothing: it narrows the member's own tips to none, and what the counted row named stays",
     [H0, M1, act("x1", "H0"), end("R", "H0", ["m1"], "B"), tips("A", "R", ["x1"]), end("R2", "H0", [], "B")], {},
     {"m1": OUT, "x1": KEPT}),
    ("member_adds_tips_itself", "a row adding tips signed by the member is never read: only a counted row adds",
     [H0, M1, M2, end("E", "H0", ["m1"]), tips("A", "E", ["m2"], "B")], {}, {"m1": KEPT, "m2": OUT}),
    ("second_end_after_first", "a second removal that has the first in its past ends nothing (the seat was "
     "already ended), but it is a counted row of the body and its tips add",
     [H0, M1, M2, end("E", "H0", ["m1"]), end("E2", "H0", ["m2"], names=["E"])], {}, {"m1": KEPT, "m2": KEPT}),
    ("resignation_at_later_head", "a resignation naming a head later than the removal's h_e, concurrent with "
     "it: where a counted end counts the member's own end's tips are not read, so naming none takes nothing out",
     [H0, H1, M1, M2, end("E", "H0", ["m2"]), end("R", "H1", [], "B")], {}, {"m1": KEPT, "m2": KEPT}),
    ("backdated_resignation_uncounts_own_rows", "the member was removed at H1 with m2 (at H1) kept, and then signs "
     "a resignation at H0: E3 puts its own row at H1 at a head later than an end of its seat, so m2 no longer "
     "counts. An ended member can take its own rows out this way; conferral_end.py's reader's line bounds it",
     [H0, H1, M1, act("m2", "H1", "m1"), end("E", "H1", ["m2"]), end("R", "H0", [], "B")], {},
     {"m1": KEPT, "m2": (F, F, "E3.later_head")}),
    ("end_stale_head", "E1: an end naming H0 with H1 in its own past concludes nothing, and its tips are not read",
     [H0, H1, M1, end("E", "H0", ["m1"], names=["H1"])], {}, {"m1": (T, T, "no_end")}),
    ("tip_at_later_head", "the end names as a tip a row at a head later than h_e: naming it does not make it "
     "count (E3 decides first), and what is behind it at h_e is kept",
     [H0, H1, M1, act("m2", "H1", "m1"), end("E", "H0", ["m2"])], {}, {"m1": KEPT, "m2": (F, F, "E3.later_head")}),
    # a member seated again: H0 (seated) <- HX (not listed) <- HA (admitted again)
    ("rejoin_and_post", "the member left with m1 kept, was admitted again at HA, and posts n1 there: a new seat "
     "with no end, so n1 is in the room's content; m1 stays on the first end's word",
     [H0, HX, HA, M1, end("E", "H0", ["m1"]), act("n1", "HA")], {}, {"m1": KEPT, "n1": (T, T, "no_end")}),
    ("rejoin_restores_nothing", "a re-admission restores nothing: m2, which the first end did not hold good, "
     "stays out after the member is seated again",
     [H0, HX, HA, M1, M2, end("E", "H0", ["m1"]), act("n1", "HA")], {},
     {"m1": KEPT, "m2": OUT, "n1": (T, T, "no_end")}),
    ("stale_device_after_rejoin", "a row signed after the re-admission that names the OLD head: the head a row "
     "names decides, so it is a row of the old seat and is out; the device signs again at a current head",
     [H0, HX, HA, M1, end("E", "H0", ["m1"]), act("n1", "HA"), act("s2", "H0", "m1")], {},
     {"m1": KEPT, "n1": (T, T, "no_end"), "s2": OUT}),
    ("row_between_seats", "a row naming a head at which the member does not sit (after its end, before the "
     "re-admission): it belongs to no seat and does not count",
     [H0, HX, HA, M1, end("E", "H0", ["m1"]), act("g1", "HX", "m1")], {},
     {"m1": KEPT, "g1": (F, F, "no_seat")}),
    ("row_naming_the_removal_as_its_head", "the removal is the member's end and a version of the roster: a row of "
     "the member that names it as its head names a head at which the member is out, and does not count; a version "
     "built on the removal admits the member again and a row there is in a new seat",
     [H0, M1, end("E", "H0", ["m1"]), act("g1", "E", "m1"), head("HR", "E", seat="admits"), act("n1", "HR")], {},
     {"m1": KEPT, "g1": (F, F, "no_seat"), "n1": (T, T, "no_end")}),
    ("second_seat_tip_reaches_left_out_row", "the hole a second seat would open: the member rejoins, posts n1 "
     "naming m2 (which the first end left out) as its predecessor, and leaves again with n1 as the tip. The "
     "walk does not cross seats: n1 is kept, m2 stays out",
     [H0, HX, HA, M1, M2, end("E", "H0", ["m1"]), act("n1", "HA", "m2"), end("E2", "HA", ["n1"])], {},
     {"m1": KEPT, "m2": OUT, "n1": KEPT}),
    ("second_seat_tip_reaches_kept_row", "the same where the first end kept m2: it stays in, on the first "
     "end's word and not the second's",
     [H0, HX, HA, M1, M2, end("E", "H0", ["m2"]), act("n1", "HA", "m2"), end("E2", "HA", ["n1"])], {},
     {"m1": KEPT, "m2": KEPT, "n1": KEPT}),
    ("second_seat_ends_without_tips", "the second seat ends and its end holds nothing good: the second seat's "
     "rows are out, and the first seat's kept rows are untouched",
     [H0, HX, HA, M1, end("E", "H0", ["m1"]), act("n1", "HA"), end("E2", "HA")], {}, {"m1": KEPT, "n1": OUT}),
    ("keeps_first_end_after_rejoin", "a counted row adds a tip for the FIRST end after the member has rejoined: "
     "it cites that end, so it is read in the first seat, and m2 comes in",
     [H0, HX, HA, M1, M2, end("E", "H0", ["m1"]), act("n1", "HA"), tips("A", "E", ["m2"])], {},
     {"m1": KEPT, "m2": KEPT, "n1": (T, T, "no_end")}),
    ("first_end_names_second_seat_row", "the first end's adding row names a row of the second seat as a tip: "
     "a tip holds good only rows of its own seat, so after the second seat ends without it, n1 is out",
     [H0, HX, HA, M1, end("E", "H0", ["m1"]), act("n1", "HA"), tips("A", "E", ["n1"]), end("E2", "HA")], {},
     {"m1": KEPT, "n1": OUT}),
    ("two_first_seat_ends_after_rejoin", "two removals of the first seat, naming different tips, both arriving "
     "after the rejoin: they are ends of the first seat by the head they name; their tips join there, and the "
     "second seat is not ended",
     [H0, HX, HA, M1, M2, act("n1", "HA"), end("E", "H0", ["m1"]), end("Eb", "H0", ["m2"])], {},
     {"m1": KEPT, "m2": KEPT, "n1": (T, T, "no_end")}),
    ("backdated_resignation_after_rejoin", "after rejoining, the member signs a resignation at the old head "
     "naming nothing: it is an end of the old seat, where a counted end counts and its own end is not read; "
     "the second seat is not ended by it",
     [H0, HX, HA, M1, end("E", "H0", ["m1"]), act("n1", "HA"), end("R", "H0", [], "B")], {},
     {"m1": KEPT, "n1": (T, T, "no_end")}),
    ("retract_old_post_after_rejoin", "seated again, the member retracts a post of its first seat that the first "
     "end kept: a retraction is read across seats, and the post leaves the content",
     [H0, HX, HA, M1, end("E", "H0", ["m1"]), act("w1", "HA", target="m1", compose="retract")], {},
     {"m1": (T, F, "W.retracted"), "w1": (T, T, "no_end")}),
    ("tip_not_the_members", "a tip that is not a content row of the member is not read: here the end names a "
     "roster head as a tip, and nothing is held good",
     [H0, M1, end("E", "H0", ["H0"])], {}, {"m1": OUT}),
]


def orders(rows):
    """Every arrival order the door allows: a row arrives only after the rows it names."""
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
    """Every case: the reference gives the hand-written answer, and the same in every arrival order."""
    problems = []
    for c in CASES:
        name, about, rows, params, want = c[:5]
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


def fixture():
    """The fixture, in the format of conferral_end.json: every case with its rows, parameters, arrival orders
    and every content row's answer."""
    _, problems = check_cases()
    assert not problems, problems
    cases = []
    for c in CASES:
        name, about, rows, params, want = c[:5]
        cases.append({"name": name, "about": about, "rows": rows, "merge": params.get("merge", "count_first"),
                      "orders": c[5] if len(c) > 5 else [[r["id"] for r in rows]],
                      "refused": None,
                      "answers": answers(rows, **params)})
    return {"about": "room content after a member's seat ends, where the end names the rows held good "
                     "(`trusted_through`): the Constitution's proposal of 2026-11-22 for CC 2.4.1.1, for persist "
                     "v62.0. Generated from models/causal_kernel/conferral_content.py; checked by "
                     "check_conferral_content.py. A PROPOSAL until the Constitution rules it",
            "roles": {"B": "a key of the member whose seat ends", "B2": "a second key of the same member",
                      "M": "a co-member: its rows are not this member's content and get no answer here",
                      "count": "a counted row (a roster version, a removal, a row adding tips)"},
            "merge": "whose tips are read: count_first (the reference's default), union (the proposal's third "
                     "point read literally) or count_first_self_union; see `rules`. The Constitution rules which",
            "refused": "null in every case here: every content row names its head",
            "rules": __doc__.split("Which ends count:")[1].strip(),
            "cases": cases}
