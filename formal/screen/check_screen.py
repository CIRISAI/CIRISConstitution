#!/usr/bin/env python3
"""check_screen.py: the six properties of formal/screen/screen.py over three sets of worlds, each with its breaks.

  story   the 98 (view, standing) pairs of manifests/mesh_story_trace.json: the items drawn are the queue the story
          served, and properties 1 to 3 hold at every step.
  grid    every family x lifecycle state x standing (no role, each role token alone, every token) x scope
          (self, community): properties 1 to 3, and `may` equals the door as tools/mesh_story.py runs it.
  worlds  generated rows over the kernel at a small bound: a room founded by two duty holders, a third key
          admitted or not and removed or not, one object of one of six families signed by a holder or by the
          third key at self or community scope, a subset of acts on it, a row that waits or not. Four viewers
          (the two holders, the third key, a stranger). All six properties.

The properties:
  1 nothing drawn that the door refuses       every item drawn is a transition the viewer's standing admits
  2 nothing admitted undrawn                  every transition admitted is drawn, or the manifest lists it as not
                                              surfaced with its reason
  3 a confirm sheet iff confirm               an item shows a sheet exactly when its rows widen at the scope signed
                                              or have no way back (CC 4.5.13, computed from widens and undo, not
                                              from the confirm cell), and an exit is always one step
  4 the view is the rows                      every arrival order draws the same screen, and a row outside the
                                              viewer's audience changes nothing drawn
  5 a fact not sent is never drawn as sent
  6 waiting is shown as waiting               a held row that waits on a missing row is drawn as waiting, with the
                                              rows it waits on, never as refused and never as done

Every break of screen.MUT is run against the set its property reads and must be caught. Writes or checks
formal/screen/screen_expected.tsv. No output line carries the word the gate reads as failure.

  python3 formal/screen/check_screen.py            # exit 1 on a breach, a break not caught or a changed verdict
  python3 formal/screen/check_screen.py --write    # rewrite screen_expected.tsv
"""
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import screen as SC  # noqa: E402

ST, RT, CK, R = SC.ST, SC.RT, SC.CK, SC.R
sys.path.insert(0, os.path.join(SC.ROOT, "tools"))
import mesh_story as STORY  # noqa: E402   the door as the story runs it

EXPECTED = os.path.join(HERE, "screen_expected.tsv")
TOKENS = SC.TR["_meta"]["role_tokens"]
STATES = SC.TR["_meta"]["states"]
VIEWERS = ("A", "B", "C", "X")
FAMILIES = ("chat:*", "capacity:relay_delivery", "ballot:moderator", "age_self_declared:band:{band}:{version}",
            "accord:invoke:drill:{drill_id}", "census:member:share")
SLOTS = (("chat:*", "self"), ("moderation:{allegation_type}", "community"), ("takedown_notice:{basis}", "community"),
         ("ballot:moderator", "community"))
BREAKS = {  # break -> the property that must catch it
    "draw_all": 1, "drop_exits": 2, "confirm_exit": 3, "confirm_ignores_when": 3, "confirm_none": 3,
    "first_held": 4, "ignore_audience": 4, "not_sent_as_value": 5,
    "waiting_as_refused": 6, "waiting_as_done": 6, "waiting_unnamed": 6,
}


# ---- the truth each property is held to -----------------------------------------------------------------
def test_4513(t, scope, prior=None):
    """CC 4.5.13, from the cells it names: confirmed when the rows widen at the scope signed, or have no way back."""
    return SC.widens_at(t, scope, prior) or not t["undo"]["value"]


def check_items(drawn, family, state, toks, atoms, scope, where, errs):
    """Properties 1 to 3 for the items drawn on one view."""
    admitted = {t["verb"]: t for t in SC.may(family, state, toks, atoms)}
    got = {v: (to, how) for v, to, how, *_ in drawn}
    for v in got:
        if v not in admitted: errs[1].append(f"{where}: {v} drawn and the door refuses it")
    for v in admitted:
        if v not in got and f"{family} {v}" not in SC.NOT_SURFACED:
            errs[2].append(f"{where}: {v} admitted and not drawn")
    for v, (to, how) in got.items():
        t = admitted.get(v)
        if t is None: continue
        want = "sheet" if test_4513(t, scope) else "one_step"
        if v in SC.EXITS and how != "one_step": errs[3].append(f"{where}: the exit {v} is not one step")
        elif how != want: errs[3].append(f"{where}: {v} drawn {how}, CC 4.5.13 gives {want}")


# ---- the story ------------------------------------------------------------------------------------------
def run_story(errs):
    steps = SC.load("manifests", "mesh_story_trace.json")["steps"]
    for s in steps:
        v, fam = s["view"], s["view"]["family"]
        if s["refused"]: state = v["state_after"]
        else: state = next(t["from"] for t in SC.FAM[fam]["transitions"] if t["verb"] == s["chosen"])
        state = state or "none"
        toks = frozenset(s["standing"])
        drawn = SC.draw_items(fam, state, toks, v["atoms"], "community")
        where = f"story step {s['n']}"
        if sorted(d[0] for d in drawn) != sorted(s["queue"]) and "drop_exits" not in SC.MUT and "draw_all" not in SC.MUT:
            errs[2].append(f"{where}: drawn {sorted(d[0] for d in drawn)}, the story served {sorted(s['queue'])}")
        check_items(drawn, fam, state, toks, v["atoms"], "community", where, errs)
    return len(steps)


# ---- the grid -------------------------------------------------------------------------------------------
def run_grid(errs, families=None):
    standings = [frozenset()] + [frozenset([t]) for t in TOKENS] + [frozenset(TOKENS)]
    n = 0
    for fam in families or sorted(SC.FAM):
        for state in STATES:
            for toks in standings:
                if not SC.MUT:
                    door = sorted(t["verb"] for t in STORY.enabled(fam, state, list(toks)))
                    if door != sorted(t["verb"] for t in SC.may(fam, state, toks)):
                        errs[1].append(f"{fam} {state} {sorted(toks)}: may and the story's door differ")
                for scope in ("self", "community"):
                    n += 1
                    check_items(SC.draw_items(fam, state, toks, {}, scope), fam, state, toks, {}, scope,
                                f"{fam} {state} {sorted(toks)} {scope}", errs)
    return n


# ---- generated worlds -----------------------------------------------------------------------------------
def room(admit, remove):
    g = ST.offer("g", "A", ("A", "B"), "duty", "@", "self", cosigners=("B",), room="g")
    rows = [g, R("md", "record", "A", ("g",), room="g", duties=("moderate",))]
    if admit:
        rows += [dict(ST.accept("ac", "C", None, ("g",), scope="member", obj="g"), room="g"),
                 dict(ST.cosign("cb", "B", "w", ("g",)), room="g"),
                 ST.offer("w", "A", "C", "member", "g", "group", ("g", "ac", "cb"), head=("g",), policy="community_invite",
                          content="w", room="g")]
    if admit and remove:
        rows += [dict(ST.cosign("xc", "B", "x", ("w",)), room="g"),
                 ST.unseat("x", "A", "C", "member", "g", "group", ("w", "xc"), head=("w",), policy="community_remove",
                           content="x", room="g")]
    return rows


FACTS = (("count", 3, "wire"), ("holders", 0, "not_sent"), ("window", 86400, "by_rule"))
ACTS = ((), ("withdraw",), ("supersede",), ("recant",), ("withdraw", "supersede"), ("withdraw_subject",))


def worlds():
    for admit, remove in ((False, False), (True, False), (True, True)):
        for fam in FAMILIES:
            for signer in ("A", "C"):
                if signer == "C" and not admit: continue
                for scope in ("community", "self"):
                    for acts in ACTS:
                        for wait in (False, True):
                            rows = room(admit, remove)
                            head = "w" if signer == "C" else "g"
                            rows.append(SC.obj("o", signer, fam, "g", scope, names=(head,), subjects=("C",) if signer == "A" else ("B",),
                                               facts=FACTS, valid_until=100))
                            for i, a in enumerate(acts):
                                by = ("C" if signer == "A" else "B") if a == "withdraw_subject" else signer
                                rows.append(SC.act(f"a{i}", by, "o", a.split("_")[0], fam, "g", scope=scope))
                            if wait:
                                rows.append(SC.obj("p", "B", fam, "g", "community", names=("g", "zz")))
                                rows.append(SC.act("q", signer, "o", "withdraw", fam, "g", names=("p",)))
                            yield (admit, remove, fam, signer, scope, acts, wait), rows


def foreign(rows):
    """Rows the generator adds to test that a row outside a viewer's audience changes nothing drawn."""
    return [SC.obj("f1", "Y", "chat:*", "h", "community", names=("hh",)),          # another room, never founded: waits
            SC.obj("f2", "B", "chat:*", "g", "self"),                              # B's own row at self scope
            dict(ST.offer("h", "Y", ("Y",), "duty", "@", "self", room="h")),       # another room, founded
            SC.obj("f3", "Y", "chat:*", "h", "community", names=("h",))]           # a row in it


def views(rows, viewer, now):
    return SC.screen(rows, viewer, now, SLOTS)


def run_worlds(errs, limit=None, only=None):
    n = 0
    for key, rows in itertools.islice(worlds(), limit):
        n += 1
        S = SC.concluded(rows)
        Q = ST.Seats(S)
        for viewer in VIEWERS:
            if only and viewer not in only: continue
            scr = views(rows, viewer, 0)
            objects, waiting, inert, slots = scr
            where = f"world {key} viewer {viewer}"
            for oid, fam, state, drawn_state, items, facts in objects:
                o = S.by[oid]
                check_items(items, fam, state, SC.standing(viewer, o, Q), o["atoms"], o["scope"], where, errs)
                for f, (name, value, prov) in zip(facts, sorted(o["facts"])):
                    if prov == "not_sent" and f != (name, "not_sent"): errs[5].append(f"{where}: {name} not sent and drawn {f}")
                    if prov != "not_sent" and f != (name, "sent", value): errs[5].append(f"{where}: {name} drawn {f}")
            for fam, scope, items in slots:
                toks = frozenset({"self", "registered"}) | (SC.standing(viewer, {"signer": None, "subjects": (), "scope": scope,
                                                                                 "room": RT.ROOM}, Q) if scope != "self" else frozenset())
                check_items(items, fam, "none", toks, {}, scope, where + f" slot {fam}", errs)
            # 6: what waits
            kept = set(S.by)
            for r in rows:
                if r["kind"] in ("obj", "act") and r["id"] not in kept and SC.may_see_waiting(r, viewer, Q):
                    w = [x for x in waiting if x[0] == r["id"]]
                    if len(w) != 1 or w[0][1] != "waiting" or not w[0][2]:
                        errs[6].append(f"{where}: {r['id']} waits and is drawn {w}")
                    if any(x[0] == r["id"] for x in objects): errs[6].append(f"{where}: {r['id']} waits and is drawn as done")
            for wid, st, missing in waiting:
                if wid in kept or st != "waiting": errs[6].append(f"{where}: {wid} drawn {st} as waiting")
            # 4: now is read only against a row's own stated end: past it an admitted object is drawn lapsed, and
            # nothing else on the screen moves
            late = views(rows, viewer, 100)
            lapse = lambda objs: tuple((i, f, s, "lapsed" if s == "admitted" else d, it, fa) for i, f, s, d, it, fa in objs)
            if late != (lapse(objects),) + scr[1:]: errs[4].append(f"{where}: now moved more than a lapsed state")
            # 4: arrival order, and rows outside the audience
            for order in (list(reversed(rows)), rows[1:] + rows[:1]):
                if views(order, viewer, 0) != scr: errs[4].append(f"{where}: another arrival order draws another screen"); break
            for extra in foreign(rows):
                more = rows + [extra]
                T = SC.concluded(more)
                aud = RT.audience(T, "closed")
                if extra["id"] in aud and viewer in aud[extra["id"]]: continue          # inside: it may change the screen
                if extra["id"] not in T.by and SC.may_see_waiting(extra, viewer, ST.Seats(T)): continue
                if views(more, viewer, 0) != scr: errs[4].append(f"{where}: {extra['id']}, outside the audience, changed the screen")
    return n


def run(breaks=None, limit=None):
    """The property suites with the breaks in `breaks` switched on; returns (counts, errs)."""
    SC.MUT.clear(); SC.MUT.update(breaks or ())
    errs = {p: [] for p in range(1, 7)}
    counts = {"story": run_story(errs),
              "grid": run_grid(errs, families=list(SC.FAMILIES_FOR_BREAKS) if breaks else None),
              "worlds": run_worlds(errs, limit=limit)}
    SC.MUT.clear()
    return counts, errs


def main():
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (3 << 30, 3 << 30))
    counts, errs = run()
    rows = []
    breach = sum(len(v) for v in errs.values())
    for p in range(1, 7):
        for e in errs[p][:5]: print(f"  property {p} breached: {e}")
    for b, p in sorted(BREAKS.items()):
        _, e = run({b}, limit=BREAK_WORLDS)
        caught = len(e[p])
        rows.append((p, b, "caught" if caught else "missed", caught))
    out = ["property\tbreak\tverdict"] + [f"{p}\t{b}\t{v}" for p, b, v, _ in sorted(rows)]
    stated = sorted(f"{r['family']} {t['verb']}" for r in SC.TR["rows"] for t in r["transitions"]
                    if t["undo"].get("stated") and t["undo"]["via"] not in {u["verb"] for u in r["transitions"]})
    out += [f"#\tstory steps\t{counts['story']}", f"#\tgrid views\t{counts['grid']}", f"#\tgenerated worlds\t{counts['worlds']}",
            f"#\tbreaches\t{breach}",
            f"#\tways back the text states that no transition of the table offers (not drawable)\t{len(stated)}"]
    text = "\n".join(out) + "\n"
    print(f"screen: {counts['story']} story steps, {counts['grid']} grid views, {counts['worlds']} generated worlds x "
          f"{len(VIEWERS)} viewers; breaches {breach}")
    for p, b, v, n in sorted(rows):
        print(f"  property {p}: break {b:22s} {v} ({n} views)")
    print(f"  measured: {len(stated)} transitions have a way back the text states (CC 2.4.1.1) and no transition of the "
          f"table offers it, so no screen built from the table draws it")
    if "--write" in sys.argv:
        open(EXPECTED, "w").write(text); print("screen: wrote screen_expected.tsv"); return 0
    same = os.path.exists(EXPECTED) and open(EXPECTED).read() == text
    missed = [b for p, b, v, _ in rows if v != "caught"]
    if breach or missed or not same:
        print("screen: BREACH" + (" (a break was not caught: %s)" % missed if missed else "") +
              ("" if same else " (verdicts differ from screen_expected.tsv)"))
        return 1
    print("screen: every property holds, and every break is caught")
    return 0


BREAK_WORLDS = 120
SC.FAMILIES_FOR_BREAKS = FAMILIES + tuple(f for f, _ in SLOTS)

if __name__ == "__main__":
    sys.exit(main())
