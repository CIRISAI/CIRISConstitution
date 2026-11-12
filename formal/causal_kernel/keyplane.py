"""
keyplane.py: formal/key_plane written again over the library, and compared with the original on its own cases.

The original keeps a writer's running state and steps it through every sequence of acts. Here the writer has no
state. Every act it holds and every act it makes is a row on the writer's own chain (each row names the one
before, so `n`, the row's height on that chain, is the count of its ancestors), and everything the original
remembers is read from the rows with sel and group:

    who is entitled to a wrap       a device whose device seat and whose member's seat are both live at that head:
                                    a seat no later row of the chain ends (an opener no closer answers)
    who holds a key                 the wrap rows that name it
    the epoch                       the count of mint rows
    a rotation is due               a `due` row later than the latest mint, or a device that holds the current key
                                    and is no longer entitled
    what the writer owes            the mint and the wrap rows the table's word for the act asks for, less the wraps held

Run against the original: the original's own explorer is loaded from the repository with one hook added to its
search (nothing else changed), and after every act of every sequence the state read from the rows is compared with
the state the original stepped: members, live devices, the epoch, due, cause, the scheduled flag, the owed set, the
count of writes and every holder of every key. K1 to K10 are functions of the acts and of exactly that state.

K1, K2 and K8 are also evaluated here from the rows alone, as the one statement of entitlement, and
`seat_agreement` checks that the chain's "entitled" is seat.py's answer over the same acts written as seat rows.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import seat as ST  # noqa: E402

K = ST.K
ORIG = os.path.join(ROOT, "formal", "key_plane", "key_plane_model.py")

OLD_DFS = """    def dfs(st, trace):
        count[0] += 1
        if len(trace) == DEPTH: return
        for ev in events(st):
            t2 = trace + (ev,)
            dfs(step(st, ev, t2), t2)
"""
NEW_DFS = """    def dfs(st, trace, shadow=None):
        count[0] += 1
        if len(trace) == DEPTH: return
        for ev in events(st):
            t2 = trace + (ev,)
            st2 = step(st, ev, t2)
            dfs(st2, t2, HOOK(shadow, ev, st2, t2, eff, tier) if HOOK else None)
"""


def load_original():
    src = open(ORIG, encoding="utf-8").read()
    assert src.count(OLD_DFS) == 1, "the original's search is not as it was when this was written"
    ns = {"__file__": ORIG, "__name__": "key_plane_original", "HOOK": None}
    exec(compile(src.replace(OLD_DFS, NEW_DFS), ORIG, "exec"), ns)
    return ns


# ---- the fold: everything is read from the chain ---------------------------------------------------------
class Chain:
    """An immutable chain of rows. Appending returns a new chain."""
    __slots__ = ("rows",)

    def __init__(self, rows=()):
        self.rows = rows

    def add(self, kind, **kw):
        n = len(self.rows)
        return Chain(self.rows + (dict(kw, id=n, kind=kind, n=n, names=(n - 1,) if n else ()),))


def latest(rows, **pat):
    return K.group(K.sel(rows, **pat), None, "greatest", "n")           # one chain: no two rows share a height


def member_live(rows, m):
    r = latest(rows, kind={"seat", "end"}, who=m)
    return r is not None and r["kind"] == "seat"


def dev_live(rows, d):
    return bool(K.sel(rows, kind="dev", dev=d)) and not K.sel(rows, kind="devend", dev=d)


def entitled(rows, devices):
    """The devices entitled to a wrap at this head: the writer's own, and every live device of a current member."""
    return frozenset({"w"}) | frozenset(d for m, ds in devices.items() if member_live(rows, m) for d in ds if dev_live(rows, d))


def holders(rows, key):
    return frozenset(w["dev"] for w in K.sel(rows, kind="wrap", key=key))


def keys(rows):
    return K.group(K.sel(rows, kind="wrap"), "key", "count", "dev")       # key -> how many devices hold it


def epoch(rows):
    return K.group(K.sel(rows, kind="mint"), None, "count", "n")


def since_mint(rows, **pat):
    last = K.group(K.sel(rows, kind="mint"), None, "max", "n")
    return [r for r in K.sel(rows, **pat) if last is None or r["n"] > last]


def owed_devices(rows, devices, eff):
    out = set()
    for m, ds in devices.items():
        if any(eff(e["how"]) == "rotate_epoch" for e in K.sel(rows, kind="end", who=m)): out |= set(ds)
    if eff("revocation") == "rotate_epoch": out |= {r["dev"] for r in K.sel(rows, kind="devend")}
    return frozenset(out)


def scheduled(rows):
    return bool(since_mint(rows, kind="due"))


def due(rows, devices, eff):
    cur = ("epoch", epoch(rows))
    return scheduled(rows) or bool((holders(rows, cur) & owed_devices(rows, devices, eff)) - entitled(rows, devices))


def caused(rows, eff):
    return bool(since_mint(rows, kind="due")) or any(eff(e["how"]) == "rotate_epoch" for e in since_mint(rows, kind="end")) \
        or (eff("revocation") == "rotate_epoch" and bool(since_mint(rows, kind="devend")))


def wrap_to(c, key, devs):
    have = holders(c.rows, key)
    for d in sorted(devs):
        if d not in have: c = c.add("wrap", key=key, dev=d)
    return c


def act(c, ev, eff, tier, devices, findings):
    """One act arrives: its row, then the rows the writer owes for it."""
    kind, who = ev
    if kind == "add":
        c = c.add("seat", who=who)
        if not dev_live(c.rows, devices[who][0]): c = c.add("dev", dev=devices[who][0], who=who)
        e = eff("widening")
        mine = [d for d in devices[who] if dev_live(c.rows, d)]
        if e == "rekey_walk":
            for k in list(keys(c.rows)): c = wrap_to(c, k, mine)
        elif e in ("at_seat", "at_seat_history"):
            cur = ("epoch", epoch(c.rows))
            if due(c.rows, devices, eff):
                if not caused(c.rows, eff): findings["K6"] += 1
                if not scheduled(c.rows) and not (holders(c.rows, cur) - entitled(c.rows, devices)): findings["K10"] += 1
                c = c.add("mint")
                c = wrap_to(c, ("epoch", epoch(c.rows)), entitled(c.rows, devices))
            elif cur in keys(c.rows):
                c = wrap_to(c, cur, devices[who][:1])
                # the original wraps the member's first device only; a second device still live from an earlier seat waits
                if set(mine) - holders(c.rows, cur): findings["second device unwrapped at the seat"] += 1
            if e == "at_seat_history":
                for k in list(keys(c.rows)): c = wrap_to(c, k, devices[who][:1])
    elif kind in ("remove", "resign"):
        c = c.add("end", who=who, how="removal" if kind == "remove" else "resignation")
    elif kind == "device_add":
        owner = next(m for m, ds in devices.items() if who in ds)
        c = c.add("dev", dev=who, who=owner)
        for k in list(keys(c.rows)):
            if tier == "per-write" or devices[owner][0] in holders(c.rows, k): c = wrap_to(c, k, [who])
    elif kind == "device_revoke":
        c = c.add("devend", dev=who)
    elif kind == "tick":
        c = c.add("due")
    elif kind == "write":
        if tier == "epoch":
            if due(c.rows, devices, eff):
                if not caused(c.rows, eff): findings["K6"] += 1
                c = c.add("mint")
            key = ("epoch", epoch(c.rows))
        else:
            key = ("write", K.group(K.sel(c.rows, kind="seal"), None, "count", "n"))
        ent = entitled(c.rows, devices)
        not_ent = holders(c.rows, key) - ent                                  # K2 and K8, as one statement of entitlement
        if not_ent: findings["K2/K8: sealed under a key a device not entitled holds"] += 1
        c = c.add("seal", key=key)
        c = wrap_to(c, key, ent)
    return c


def read_state(rows, devices, eff):
    ks = keys(rows)
    return {"members": frozenset(m for m in devices if member_live(rows, m)),
            "live": frozenset(d for ds in devices.values() for d in ds if dev_live(rows, d)),
            "revoked": frozenset(r["dev"] for r in K.sel(rows, kind="devend")),
            "epoch": epoch(rows), "tickdue": scheduled(rows), "cause": caused(rows, eff),
            "holders": tuple(sorted((k, holders(rows, k)) for k in ks)),
            "nwrites": K.group(K.sel(rows, kind="seal"), None, "count", "n"),
            "owed": owed_devices(rows, devices, eff)}


ORIG_FIELDS = ("members", "live", "left", "revoked", "epoch", "due", "cause", "holders", "nwrites", "fresh", "stale", "tickdue", "owed")


def compare(seat_depth=4):
    """Every sequence of the original at both tiers and for the proposal. Returns one record per run."""
    ns = load_original()
    devices = ns["DEVICES"]
    out = []
    stat = {}

    def hook(shadow, ev, st2, trace, eff, tier):
        c, seats = shadow if shadow else (Chain(), SeatShadow())
        n_before = len(c.rows)
        c = act(c, ev, eff, tier, devices, stat["findings"])
        o = dict(zip(ORIG_FIELDS, st2))
        mine = read_state(c.rows, devices, eff)
        stat["states"] += 1
        for f, v in mine.items():
            stat["compared"] += 1
            if v != o[f]:
                stat["differ"] += 1
                stat["first"] = stat["first"] or (f, trace, v, o[f])
        stat["compared"] += 1
        if o["due"] != mine["tickdue"]:                       # under these tables the original's flag is the scheduled one
            stat["differ"] += 1; stat["first"] = stat["first"] or ("due", trace, mine["tickdue"], o["due"])
        ent = entitled(c.rows, devices)
        for w in c.rows[n_before:]:                           # K1 from the rows: a wrap goes only to a device entitled at that head
            if w["kind"] == "wrap":
                stat["wraps"] += 1
                if w["dev"] not in ent: stat["findings"]["K1: wrapped to a device not entitled"] += 1
        if stat["seat"] and ev[0] != "write" and ev[0] != "tick":
            seats = seats.act(ev, devices)
            if len(trace) <= seat_depth and all(e[0] not in ("write", "tick") for e in trace):
                stat["seat_compared"] += 1
                if seats.entitled(devices) != ent: stat["seat_differ"] += 1
        return (c, seats)

    ns["HOOK"] = hook
    tab = ns["key_table"]()
    prop = {("widening", "family"): "at_seat_history", ("removal", "family"): "rotate_epoch",
            ("resignation", "family"): "rotate_epoch", ("revocation", "family"): "rotate_epoch"}
    for label, table, scope, tier, kw, seat in (("per-write", tab, "self", "per-write", {}, True), ("epoch", tab, "community", "epoch", {}, False),
                                                ("proposed", prop, "family", "epoch", {"full_history": True}, False)):
        stat.clear()
        stat.update(states=0, compared=0, differ=0, first=None, wraps=0, seat=seat, seat_compared=0, seat_differ=0,
                    findings={"K6": 0, "K10": 0, "second device unwrapped at the seat": 0,
                              "K2/K8: sealed under a key a device not entitled holds": 0, "K1: wrapped to a device not entitled": 0})
        n, fail = ns["explore"](table, scope, tier, **kw)
        out.append(dict(stat, run=label, sequences=n, original_fails=sorted(fail), findings=dict(stat["findings"])))
    return out


# ---- the same acts as seat rows: is "entitled" the seat answer? ------------------------------------------
class SeatShadow:
    """The membership acts written as seat.py rows: the room is the writer's founding row, a member is seated by an
    offer the member cosigned, a device by its member; a removal and a revocation are unseats, a resignation is the
    member's own withdrawal."""
    __slots__ = ("rows", "last")

    def __init__(self, rows=None, last=None):
        self.rows = rows or (ST.offer("g", "w", "w", "writer", "@", "self"),)
        self.last = last or {}

    def act(self, ev, devices):
        kind, who = ev
        rows, last, i, head = list(self.rows), dict(self.last), len(self.rows), self.rows[-1]["id"]
        owner = next((m for m, ds in devices.items() if who in ds), None)
        def dev(d, m):
            rows.append(ST.offer("d%d" % len(rows), m, d, "device", m, "self", (rows[-1]["id"],), cosigners=(d,)))
            last[d] = rows[-1]["id"]
        if kind == "add":
            rows.append(ST.offer("s%d" % i, "w", who, "member", "g", "self", (head,), cosigners=(who,))); last[who] = rows[-1]["id"]
            if devices[who][0] not in last: dev(devices[who][0], who)
        elif kind == "remove":
            rows.append(ST.unseat("x%d" % i, "w", who, "member", "g", "self", (head,)))
        elif kind == "resign":
            rows.append(ST.withdraw("r%d" % i, who, last[who], (head,)))
        elif kind == "device_add":
            dev(who, owner)
        elif kind == "device_revoke":
            rows.append(ST.unseat("x%d" % i, owner, who, "device", owner, "self", (head,)))
        return SeatShadow(tuple(rows), last)

    def entitled(self, devices):
        S = ST.CK.concluded(ST.CK.kept(list(self.rows)), ST.seat_rule)
        Q = ST.Seats(S)
        return frozenset({"w"}) | frozenset(d for m, ds in devices.items() if Q.stands(m, "member", "g") for d in ds if Q.stands(d, "device", m))


if __name__ == "__main__":
    import resource, time
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
    t = time.time()
    for r in compare():
        print("%-9s %d sequences, %d states, %d comparisons, %d differ; %d wraps; original fails %s; seat rows: %d compared, %d differ" % (
            r["run"], r["sequences"], r["states"], r["compared"], r["differ"], r["wraps"], r["original_fails"] or "nothing",
            r["seat_compared"], r["seat_differ"]))
        print("          from the rows:", r["findings"])
        if r["first"]: print("          first difference:", r["first"])
    print("%.1fs" % (time.time() - t))
