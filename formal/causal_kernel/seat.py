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
sys.path.insert(0, os.path.join(ROOT, "formal", "kernel_lib"))
from reexpress import ranked as RANKED  # noqa: E402   the ranked count, already written over the library
DEPTH = 5                                       # CC 3.4.7: a delegation chain is at most five links

# ---- table data ----------------------------------------------------------------------------------------
# what a seat holds at zero hops (the root holds what it may confer), and what it may confer over which object
HOLDS = {"founder": ("member", "moderate", "review", "slash", "takedown"), "owner": ("steward",)}
CONFERS = {  # scope held -> (scopes it may confer, "same": over the same object | "holder": over the holder's own key)
    "founder": (("moderate", "review", "slash", "takedown"), "same"),
    "owner": (("wa", "infra:attest", "operator"), "same"),
    "self": (("wa", "takedown", "author", "custodian", "operator"), "same"),
    "root": (("attest", "infra:attest", "assure:age", "assure:capacity", "infra:attest_assurance", "infra:detect"), "holder"),
}


def policy_table(path=None):
    """policy row -> a predicate met(yes, n), from the enact rule of manifests/governance_policy.json."""
    path = path or os.path.join(ROOT, "manifests", "governance_policy.json")
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


def withdraw(id, signer, target, names=()):
    return R(id, "withdraw", signer, tuple(names) + ((target,) if target not in names else ()), target=target)


def unseat(id, signer, k, scope, obj, conf, names=(), **kw):
    return R(id, "unseat", signer, names, to=(k,), scope=scope, obj=obj, conf=conf, cuts=_slots(k, scope, obj),
             says="out", **kw)


def cosign(id, signer, of, names=()):
    return R(id, "cosign", signer, names, of=of)


signers = lambda r: frozenset((r["signer"],) + tuple(r.get("cosigners", ())))
covers = lambda have, want: have == want or want.startswith(have + ":")


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
    def __init__(self, S, holds=HOLDS, confers=CONFERS, depth=DEPTH, by_arrival=False, own=None, checkpoint=False):
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
        off_ended = lambda o, k: any(w["target"] == o["id"] and (w["signer"] == k or (w["signer"] not in o["to"] and o["conf"] != "group"))
                                     and not late(w, o) for w in wd)
        self.stale = V = CP.void(S, C, own, checkpoint)         # counted acts built on one that does not count, or behind the reader's line
        unseats = [u for u in K.sel(Cs, kind="unseat") if C.counts(u) and u["id"] not in V]

        def unseated(o, k):
            for u in unseats:
                if ("seat", k, o["scope"], o["obj"]) not in u["cuts"]: continue
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

        base = [(o, k) for o in K.sel(Cs, kind="offer") if C.counts(o) and o["id"] not in V
                for k in o["to"] if not off_ended(o, k) and accepted(o, k) and not unseated(o, k)]

        def step(live):
            at = {(oid, k): (d, root) for oid, k, d, root in live}
            out = set(live)
            for o, k in base:
                if (o["id"], k) in at: continue
                if o["conf"] == "self":
                    # over a founding row that seats several keys, a signer's own offer stands on that signer's founding seat
                    if o["obj"] == o["id"] or not founding_many(S.by, o["obj"]) or (o["obj"], o["signer"]) in at:
                        out.add((o["id"], k, 0, o["signer"]))
                elif o["conf"] == "group": out.add((o["id"], k, 0, ("group", o["obj"])))
                elif o["conf"] == "seat":
                    up = S.by.get(o.get("under"))
                    hit = at.get((o.get("under"), o["signer"]))
                    if up is not None and hit is not None and self.may_confer(up, o):
                        out.add((o["id"], k, hit[0] + 1, hit[1]))
            return frozenset(out)

        self.live = K.fix(step, frozenset(), depth + 1)       # one link per pass: at most `depth` links below a root
        self.recs = [{"id": "%s/%s" % (oid, k), "offer": oid, "k": k, "scope": S.by[oid]["scope"], "obj": S.by[oid]["obj"],
                      "depth": d, "root": root} for oid, k, d, root in self.live]

    def may_confer(self, up, o):
        """May the holder of the seat offered by `up` confer the seat `o` offers?"""
        if up.get("sub") and covers(up["scope"], o["scope"]) and o["obj"] == up["obj"]:
            return True                                            # the grant carried sub-delegation: the same or narrower
        scopes, over = K.rule(self.confers, up["scope"], ((), "same"))
        return any(covers(s, o["scope"]) for s in scopes) and o["obj"] == (up["obj"] if over == "same" else o["signer"])

    def _has(self, rec, s):
        return covers(rec["scope"], s) or s in K.rule(self.holds, rec["scope"], ())

    def stands(self, k, s, o, root=None):
        if not any(self._has(r, s) and (root is None or r["root"] == root) for r in K.sel(self.recs, k=k, obj=o)): return False
        common = self.tips_common(s, o)                         # while tips wait, a key stands only if every tip seats it
        return common is None or k in common

    def holders(self, s, o, root=None):
        got = frozenset(r["k"] for r in K.sel(self.recs, obj=o) if self._has(r, s) and (root is None or r["root"] == root))
        common = self.tips_common(s, o)
        return got if common is None else got & common

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
            Q = Seats(CK.State(sub, {q["id"]: True for q in sub}), self.holds, self.confers)
            m = frozenset(r["k"] for r in K.sel(Q.recs, obj=o) if Q._has(r, s))
            out = m if out is None else out & m
        return out

    def one(self, s, o):
        """The single holder, where the seat is single-valued (an owner): two live holders is none."""
        return K.group([r for r in K.sel(self.recs, obj=o) if self._has(r, s)], None, "one", "k")

    def snapshot(self):
        return frozenset((r["k"], r["scope"], r["obj"], r["depth"], r["root"]) for r in self.recs)


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
        m = Seats(CK.State(sub, {q["id"]: True for q in sub})).holders(scope, obj)
        out = m if out is None else out & m
    return out or frozenset()


def voices(r, P):
    """The keys that signed r: its signer, its cosigners, and the signers of the cosign rows it names that themselves
    name every head r is counted over."""
    heads = set(r.get("head", ()))
    return signers(r) | frozenset(c["signer"] for c in K.sel(P, kind="cosign", of=r.get("content", r["id"]))
                                  if c["id"] in r["names"] and heads <= set(c["names"]))


def seat_rule(r, P, past, table=None, other=None):
    """The conclusion rule. P: r's concluded ancestors."""
    k, by = r["kind"], {q["id"]: q for q in P}
    if k in ("offer", "unseat"):
        conf = r["conf"]
        if conf == "self":
            if r["obj"] == r["id"]: return k == "offer"          # a founding row is its own object
            if k == "unseat" and founding_many(by, r["obj"]): return False    # among several founding keys, ending a seat takes the count
            return r["signer"] in own_keys(by, r["obj"]) and (r["obj"] not in by or True)
        if conf == "seat":
            return k == "offer" and r.get("under") in by and r["signer"] in by[r["under"]]["to"]
        if conf == "group":
            heads = r.get("head", ())
            mem = members_at(P, past, r.get("over", r["obj"]), heads, r.get("counted", "member"))
            if K.rule(table or POLICY, r.get("policy"), ("unknown",))[0] == "ranked":
                # the count is the ranked tally: the ballots the row names, one voice each, and the row seats the winner
                ballots = [(b["signer"], b["ranking"]) for b in K.sel(P, kind="ballot") if b["id"] in r["names"] and b["signer"] in mem]
                return k == "offer" and bool(ballots) and RANKED(ballots, list(r["options"]))[0] == r["to"][0]
            return met(r.get("policy"), len(voices(r, P) & mem), len(mem), r.get("need"), table)
        return False
    if k == "accept":
        return r["of"] is None or (r["of"] in by and r["signer"] in by[r["of"]].get("to", ()))
    if k == "withdraw":
        t = by.get(r["target"])
        return t is not None and (r["signer"] in signers(t) or (t["kind"] == "offer" and r["signer"] in t["to"]))
    if k == "cosign":
        return True
    return other(r, P, past) if other else True
