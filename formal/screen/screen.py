"""
screen.py: A SCREEN IS A FUNCTION OF THE ROWS A NODE HOLDS, THE VIEWER'S KEY AND NOW.

    screen(offered, viewer, now, slots=()) -> a frozen, comparable value

The node holds an unsorted set of rows. The kernel keeps what it can (causal_kernel.kept: a row whose named rows
are not all held waits), concludes every kept row against its own past (seat.py for seats, the door below for an
act on an object), and derives the live seats. For one viewer the screen then draws:

  objects   every object row in the viewer's audience (route.audience, the closed rule of CC 5.2), with its state
            and its facts. The state folds the concluded acts on the object (CC 3.5.1: recants outranks withdraws
            outranks supersedes), so it is the same in every arrival order.
  items     on each object, and on each slot the viewer opened (a view of a family with no row yet, state none),
            exactly the transitions `may` admits: those of manifests/transitions.json whose `from` is the state and
            whose roles meet the viewer's standing over the object (CC 4.5.13: the queue is the door run forwards).
            An item carries a ConfirmSheet exactly when the transition's confirm cell holds for the row as it
            would be signed: `when: if_widens` asks whether the row widens at the scope it is signed at.
  facts     each with the provenance of manifests/choice_item.cddl: `wire` and `by_rule` draw the value, and
            `not_sent` draws that the node did not send it, never a value.
  waiting   every held row the viewer may see that is not kept, drawn as waiting with the rows it waits on (the
            `missing` answer, route.needs), never as refused and never as done (KERNEL.md section 3).
  inert     every kept object or act that concludes nothing, drawn as counting for nothing, never as refused.

Standing over an object is read from the rows (seat.py and the row itself, formal/causal_kernel/role_shapes.tsv):
`author` and `subject` off the row, `member` and the four duty scopes from the live seats over the object's room,
`self` over the viewer's own slots, `registered` for every key. Nothing is read from arrival order or an instant;
`now` is read only against a row's own stated end (`valid_until`), which draws the object as lapsed.

MUT names deliberate breaks; formal/screen/check_screen.py switches each on and must see it caught.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "formal", "causal_kernel"))
sys.dont_write_bytecode = True
import causal_kernel as CK  # noqa: E402
import route as RT          # noqa: E402
import seat as ST           # noqa: E402

K, R = CK.K, CK.row
load = lambda *p: json.load(open(os.path.join(ROOT, *p), encoding="utf-8"))
TR = load("manifests", "transitions.json")
UI = load("manifests", "ui_primitives.json")
GP = load("manifests", "governance_policy.json")
FAM = {r["family"]: r for r in TR["rows"]}
WINDOW = {f["family"]: f.get("window_secs") for f in GP["families"]}       # a Ceremony's numbers come from this table
SCOPES = ("self", "family", "community", "affiliations", "federation")      # manifests/choice_item.cddl `write.scope`
EXITS = ("withdraw", "recant")                                              # CC 4.5.13: one step each
DUTY_TOKENS = {d: d for d in ST.DUTIES}                                     # a duty scope is the role token of its name
MUT = set()

# what the screen draws a state as, from the manifest's closed list (ui_primitives.json `states`)
DRAWN = {"admitted": "populated", "withdrawn": "gone", "recanted": "gone", "superseded": "gone",
         "waiting": "waiting", "lapsed": "lapsed", "inert": None}
NOT_SURFACED = UI.get("not_surfaced", {})                                   # (family verb) -> reason; the manifest has none


# ---- the door ------------------------------------------------------------------------------------------
def stage_of(cell, atoms):
    return (cell.get("stages") or {}).get((atoms or {}).get("stage"), cell["value"])


def may(family, state, standing, atoms=None):
    """The transitions the door admits for this standing in this state (CC 4.5.13, formal/event_lifecycle)."""
    out = []
    for t in FAM.get(family, {}).get("transitions", ()):
        if t["from"] != state: continue
        need = stage_of(t["roles"], atoms)
        if not need: continue
        if "not_subject" in t["roles"].get("conditions", []) and "subject" in standing: continue
        if any(r in need for r in standing) or ("registered" in need and standing): out.append(t)
    return out


def widens_at(t, scope, prior=None):
    """Does the row this transition signs widen, signed at `scope` (and replacing a row at `prior`)?"""
    w = t["widens"]
    if not w["value"]: return False
    if w.get("when") == "by_scope": return scope != "self"
    if w.get("when") == "by_scope_change": return prior is not None and SCOPES.index(scope) > SCOPES.index(prior)
    return True


def confirm_cell(t, scope, prior=None):
    """The lookup: the confirm cell, narrowed by its `when` for the row as signed (L6)."""
    c = t["confirm"]
    if not c["value"]: return False
    if c.get("when") == "if_widens" and "confirm_ignores_when" not in MUT: return widens_at(t, scope, prior)
    return True


# ---- the kernel's rule for objects and acts --------------------------------------------------------------
def obj(id, signer, family, room, scope="community", names=(), subjects=(), facts=(), valid_until=None, atoms=None):
    """A row of `family`; `facts` is a tuple of (name, value, provenance)."""
    return R(id, "obj", signer, tuple(names), family=family, room=room, scope=scope, subjects=tuple(subjects),
             facts=tuple(facts), valid_until=valid_until, atoms=dict(atoms or {}))


def act(id, signer, target, verb, family, room, names=(), scope=None):
    return R(id, "act", signer, (target,) + tuple(n for n in names if n != target), family=family, room=room,
             target=target, verb=verb, scope=scope)


def room_of(o):
    return o["room"] if o["scope"] != "self" else ("self", o["signer"])


def standing(viewer, o, Q):
    """The role tokens the held rows give `viewer` over object row `o` (Q: the live seats)."""
    toks = {"registered"}
    if viewer == o["signer"]: toks.add("author")
    if viewer in o["subjects"]: toks.add("subject")
    if o["scope"] != "self":
        if Q.stands(viewer, "member", o["room"]): toks.add("member")
        for d, tok in DUTY_TOKENS.items():
            if Q.stands(viewer, d, o["room"]): toks.add(tok)
    return frozenset(toks)


def state_of(o, acts):
    """CC 3.5.1: recants outranks withdraws outranks supersedes; one named party's withdrawal is enough (CC 2.4.1.1)."""
    if "first_held" in MUT and acts:
        return {"recant": "recanted", "withdraw": "withdrawn", "supersede": "superseded"}[acts[0]["verb"]]
    verbs = {a["verb"] for a in acts}
    for v, s in (("recant", "recanted"), ("withdraw", "withdrawn"), ("supersede", "superseded")):
        if v in verbs: return s
    return "admitted"


def rule(r, P, past):
    k = r["kind"]
    if k == "obj":
        if r["scope"] == "self": return True
        return r["signer"] in ST.members_at(P, past, r["room"], r["names"][:1] or (r["id"],)) if r["names"] else False
    if k == "act":
        o = next((q for q in P if q["id"] == r["target"]), None)
        if o is None or o["kind"] != "obj": return False
        Q = ST.Seats(CK.State(P, {q["id"]: True for q in P}))
        st = state_of(o, [a for a in P if a["kind"] == "act" and a["target"] == o["id"]])
        return any(t["verb"] == r["verb"] for t in may(o["family"], st, standing(r["signer"], o, Q), o["atoms"]))
    return ST.seat_rule(r, P, past)


def concluded(offered):
    return CK.concluded(CK.kept(offered), rule)


# ---- the screen ----------------------------------------------------------------------------------------
def item(t, scope, atoms=None, prior=None):
    """One item: the verb, the state it reaches, a ConfirmSheet or one step, and the Ceremony it runs under (the
    policy row of the transition, or of its stage, with that row's window from the governance policy table)."""
    exit_ = t["verb"] in EXITS
    sheet = confirm_cell(t, scope, prior)
    if "confirm_exit" in MUT and exit_: sheet = True
    if "confirm_none" in MUT: sheet = False
    pol = stage_of(t["policy"], atoms)
    return (t["verb"], t["to"], "sheet" if sheet else "one_step", pol["policy"], tuple((r, WINDOW.get(r)) for r in pol["rows"]))


def draw_items(family, state, toks, atoms, scope, prior=None):
    if "draw_all" in MUT:
        ts = [t for t in FAM.get(family, {}).get("transitions", ()) if t["from"] == state]
    else:
        ts = may(family, state, toks, atoms)
    if "drop_exits" in MUT: ts = [t for t in ts if t["verb"] not in EXITS]
    return tuple(sorted(item(t, scope, atoms, prior) for t in ts))


def draw_fact(name, value, prov):
    if prov == "not_sent" and "not_sent_as_value" not in MUT: return (name, "not_sent")
    return (name, "sent", value)


def screen(offered, viewer, now, slots=()):
    S = concluded(offered)
    Q = ST.Seats(S)
    aud = RT.audience(S, "closed")
    sees = lambda i: viewer in aud[i] or "ignore_audience" in MUT
    kept = set(S.by)
    objects, inert = [], []
    for o in S.rows:
        if o["kind"] != "obj" or not sees(o["id"]):
            continue
        if not S.C.get(o["id"]):
            inert.append((o["id"], "counts for nothing")); continue
        acts = [a for a in S.Cs if a["kind"] == "act" and a["target"] == o["id"]]
        st = state_of(o, acts)
        toks = standing(viewer, o, Q)
        lapsed = o["valid_until"] is not None and now >= o["valid_until"]
        objects.append((o["id"], o["family"], st, DRAWN["lapsed" if lapsed and st == "admitted" else st],
                        draw_items(o["family"], st, toks, o["atoms"], o["scope"]),
                        tuple(sorted(draw_fact(*f) for f in o["facts"]))))
    for a in S.rows:
        if a["kind"] == "act" and not S.C.get(a["id"]) and sees(a["id"]):
            inert.append((a["id"], "counts for nothing"))
    waiting = []
    for r in offered:
        if r["id"] in kept or r["kind"] not in ("obj", "act"): continue
        if not may_see_waiting(r, viewer, Q): continue
        missing = waits_on(r, offered, kept)
        if "waiting_as_refused" in MUT: waiting.append((r["id"], "refused", ())); continue
        if "waiting_as_done" in MUT: waiting.append((r["id"], "populated", ())); continue
        if "waiting_unnamed" in MUT: missing = ()
        waiting.append((r["id"], "waiting", missing))
    drawn_slots = []
    for family, scope in slots:
        toks = frozenset({"self", "registered"}) | (standing(viewer, {"signer": None, "subjects": (), "scope": scope,
                                                                      "room": RT.ROOM}, Q) if scope != "self" else frozenset())
        drawn_slots.append((family, scope, draw_items(family, "none", toks, {}, scope)))
    return (tuple(sorted(objects)), tuple(sorted(waiting)), tuple(sorted(inert)), tuple(sorted(drawn_slots)))


def waits_on(r, offered, kept):
    """The rows r names that are not held, through every held row it names that waits in turn (route.needs)."""
    by = {q["id"]: q for q in offered}
    out, todo, seen = set(), list(r["names"]), set()
    while todo:
        n = todo.pop()
        if n in seen: continue
        seen.add(n)
        if n not in by: out.add(n)
        elif n not in kept: todo.extend(by[n]["names"])
    return tuple(sorted(RT.needs(out, kept)))


def may_see_waiting(r, viewer, Q):
    """A row that waits is not concluded, so its audience is its own: its signer, the keys it names as subjects, and
    the members of its room under the seats held now."""
    if viewer == r["signer"] or viewer in r.get("subjects", ()): return True
    return r.get("room") is not None and Q.stands(viewer, "member", r["room"])
