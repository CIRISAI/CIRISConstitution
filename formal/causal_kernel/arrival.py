"""
arrival.py: the kernel as the tables read today. Each row is judged once, when it arrives, against the
rows held admitted at that moment, by the guard cell quoted in witnesses.tsv (`cell`). Rows here are the
table's own rows (its ids), not the re-encoded ones. Result strings follow the table's format so the two
can be compared byte for byte.
"""


def run(order, guard):
    st, held = {}, {}
    adm = lambda **pat: [r for i, r in held.items() if st[i] == "admitted" and all(r.get(f) == v for f, v in pat.items())]
    for r in order:
        refuse = guard(r, st, held, adm)
        held[r["id"]] = r
        st[r["id"]] = ("refused", refuse) if refuse else "admitted"
    ok = ", ".join("%s:%s" % (i, s) for i, s in sorted(st.items()) if not isinstance(s, tuple))
    no = ", ".join("%s:%s" % (i, s[1]) for i, s in sorted(st.items()) if isinstance(s, tuple))
    return ok + (" ; refused " + no if no else "")


def once(kind, token, *fields):
    def g(r, st, held, adm):
        if r["kind"] == kind and adm(kind=kind, **{f: r[f] for f in fields}):
            return token
    return g


def membership(r, st, held, adm):
    k = r["kind"]
    if k in ("acceptance", "decline"):
        if adm(kind="acceptance", signer=r["signer"], ref=r["ref"]) or adm(kind="decline", signer=r["signer"], ref=r["ref"]):
            return "membership_reply_conflict"
    if k == "widening":
        acc = adm(kind="acceptance", signer=r["subject"])
        if not acc:
            return "membership_acceptance_mismatch"
        if adm(kind="decline", signer=r["subject"], ref=acc[0]["ref"]):
            return "membership_declined"
        if adm(kind="widening", ref=acc[0]["id"]):
            return "refuse"
    if k == "charter":
        if any(adm(kind="widening", subject=wit) for wit in r["witnesses"]):
            return "refuse"


def composer(states, need_admitted=True, token=None):
    """withdraw / replace of a target: the door admits only from `admitted`."""
    def g(r, st, held, adm):
        if r["kind"] in states:
            t = r["target"]
            if st.get(t) != "admitted":
                return token or "target_is_%s_not_admitted" % st.get(t)
            st[t] = states[r["kind"]]
    return g


def w7(r, st, held, adm):
    if r["kind"] == "replace":
        if st.get(r["target"]) != "admitted":
            return "refuse"
        st[r["target"]] = "superseded"


def w8(r, st, held, adm):
    if r["kind"] == "withdraw":
        if adm(kind="frozen", object=r["object"]):
            return "refuse"
        st[r["target"]] = "withdrawn"


def w9(r, st, held, adm):
    if r["kind"] == "key_grant" and adm(kind="retired", object=r["object"]):
        return "refuse"


def w11(r, st, held, adm):
    if r["kind"] == "replace":
        if adm(kind="confers") and not adm(kind="rebind"):
            return "serve_transit_pair_rotation_before_rebind"
        st[r["target"]] = "superseded"


def g2(r, st, held, adm):
    if r["kind"] == "score" and not adm(kind="consent"):
        return "refuse"


def g3(r, st, held, adm):
    if r["kind"] == "act" and not adm(kind="edge", to=r["signer"]):
        return "signer_not_seated"
    if r["kind"] == "withdraw":
        st[r["target"]] = "withdrawn"


D = lambda id, kind, signer, **kw: dict(id=id, kind=kind, signer=signer, **kw)
_p = D("p", "proposal", "founder", subject="K")
_a = D("a", "acceptance", "K", ref="p")
_d = D("d", "decline", "K", ref="p")
_w = D("w", "widening", "founder", subject="K", ref="a")

CASES = {
    "W1": ([D("c1", "composite", "seatA", slot="room/period7"), D("c2", "composite", "seatB", slot="room/period7")],
           once("composite", "census_composite_duplicate_period", "slot")),
    "W2": ([D("s1", "share", "m1", slot="p7/tok/0"), D("s2", "share", "m1", slot="p7/tok/0")], once("share", "refuse", "slot")),
    "W3": ([D("h1", "share", "n1", slot="p7/tok/1"), D("h2", "share", "n1", slot="p7/tok/1")],
           once("share", "census_share_duplicate_token", "slot")),
    "W4": ([_p, _a, _d], membership),
    "W5": ([_p, _a, _d, _w], membership),
    "W6": ([_p, _a, _w, D("w2", "widening", "founder2", subject="K", ref="a")], membership),
    "W7": ([D("h0", "roster", "f1"), D("v1", "replace", "f1", target="h0"), D("v2", "replace", "f2", target="h0")], w7),
    "W8": ([D("dec", "decided", "agent", object="agentX"), D("frz", "frozen", "agent", object="agentX"),
            D("wd", "withdraw", "agent", target="dec", object="agentX")], w8),
    "W9": ([D("kg", "key_grant", "owner", object="agentX"), D("ret", "retired", "agent", object="agentX")], w9),
    "W10": ([_p, _a, D("ch", "charter", "root", witnesses=("K",)), _w], membership),
    "W11": ([D("t0", "transport", "N"), D("rep", "replace", "N", target="t0"), D("seat", "confers", "root")], w11),
    "G1": ([D("r", "msg", "K1"), D("wd", "withdraw", "K1", target="r"), D("sup", "replace", "K1", target="r")],
           composer({"withdraw": "withdrawn", "replace": "superseded"})),
    "G2": ([D("score", "score", "scorer"), D("consent", "consent", "node1")], g2),
    "G3": ([D("del", "edge", "root", to="mod"), D("act", "act", "mod"), D("xdel", "withdraw", "root", target="del")], g3),
}


# ---- the three cases the table did not run through a cell -------------------------------------------------
def c1(first_held, read_at=30, window=24):
    """e = eviction, x = any row by the target. Lands only if no row of the target was first held inside the
    window, counted by this node from the instant it first held the proposal."""
    inside = first_held["e"] <= first_held["x"] < first_held["e"] + window
    return "cancelled: K2 stays" if inside else ("lands reverse: K2 evicted" if read_at >= first_held["e"] + window else "open")


def c2(first_held, fuse=24):
    """h = halt, c = confirmation. The fuse runs from the instant this node first held the halt; a
    confirmation is admitted only inside it."""
    return "confirmed, in force" if first_held["c"] < first_held["h"] + fuse else "lapsed at the fuse; confirmation refused"


def t1(order):
    held, out = [], []
    for e in order:
        back = any(h == (e[1], e[0]) for h in held)
        out.append("%s->%s %s" % (e[0], e[1], "refused (closes the cycle)" if back else "admitted"))
        if not back:
            held.append(e)
    return ", ".join(sorted(out))


CLOCKED = {
    "C1": (c1, {"e": 0, "x": 1}, {"e": 0, "x": 25}, ("cancelled", "lands reverse")),
    "C2": (c2, {"h": 0, "c": 25}, {"h": 20, "c": 25}, ("lapsed", "confirmed")),
}
