"""
causal_kernel.py: an executable form of formal/causal_order (kept, concluded, derived).

A row is a dict:
    id      its digest
    family  the family it belongs to (carried, never read here)
    kind    what the row is (claim, decider, removal, edge, withdraw, vote, ...)
    signer  the key that signed it
    names   the ids of the rows it names by digest (its parents)
plus what a derived function reads: target, slot, picks, removes, to, roster, choice, body fields.

The only order is `names`. No instant, no rank and no id is compared anywhere in this file.

Written with formal/kernel_lib (sel, group, fix) where they fit. What the library did not have is
written here and marked `NOT IN kernel_lib`.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "formal", "kernel_lib"))
_dwb, sys.dont_write_bytecode = sys.dont_write_bytecode, True     # the repository is read only: no __pycache__ there
import kernel_lib as K  # noqa: E402
sys.dont_write_bytecode = _dwb


def row(id, kind, signer, names=(), **kw):
    r = {"id": id, "kind": kind, "signer": signer, "names": tuple(names), "family": kw.pop("family", kind)}
    r.update(kw)
    return r


WELL_FORMED = lambda r: not r.get("malformed", False)


# ---- layer 1: kept ---------------------------------------------------------------------------------------
def kept(offered, wf=WELL_FORMED):
    """The least set closed under the door: a row is kept iff it is well formed alone and every row it
    names is kept. Nothing is refused because of another row."""
    step = lambda acc: acc | frozenset(r["id"] for r in offered if wf(r) and all(n in acc for n in r["names"]))
    acc = K.fix(step, frozenset(), len(offered) + 1)
    seen, out = set(), []
    for r in offered:
        if r["id"] in acc and r["id"] not in seen:
            seen.add(r["id"]); out.append(r)
    return out


def ancestors(by, rid):
    """The ids of the rows `rid` names, and theirs. NOT IN kernel_lib as a function: it is `fix` over a
    step written by hand here (a transitive closure along `names`)."""
    step = lambda acc: acc | frozenset(n for a in acc | {rid} if a in by for n in by[a]["names"])
    return K.fix(step, frozenset(), len(by) + 1)


class State:
    """A kept set with its ancestry, and (once concluded) the per-row conclusions."""

    def __init__(self, kept_rows, C=None):
        self.rows = list(kept_rows)
        self.by = {r["id"]: r for r in self.rows}
        self.anc = {i: ancestors(self.by, i) for i in self.by}
        self.C = C or {}
        self.Cs = [r for r in self.rows if self.C.get(r["id"])]

    def concurrent(self, a, b):
        return a != b and a not in self.anc[b] and b not in self.anc[a]


def concurrent(S, a, b):
    """Neither names the other, through any chain. NOT IN kernel_lib."""
    return S.concurrent(a, b)


# ---- layer 2: concluded ----------------------------------------------------------------------------------
def _live(S, r, root):
    return root is None or root(r) or any(root(S.by[a]) for a in S.anc[r["id"]])


def concluded(kept_rows, rule, root=None, reads_concurrent=False):
    """Recursion on ancestry. rule(r, P, past): P is the list of r's concluded ancestors; past(a, b) says
    whether row a is an ancestor of row b (both in r's past). A row with no root at or above it
    concludes nothing. `reads_concurrent` hands the rule the live concurrent rows as a fourth argument;
    it exists only so the check can show what that costs (Causal.concl_final)."""
    S = State(kept_rows)
    C = {}
    # more ancestors = later; a row reads only rows with strictly fewer, so any order of the rest is the same
    for r in sorted(S.rows, key=lambda r: len(S.anc[r["id"]])):
        a = S.anc[r["id"]]
        if not _live(S, r, root):
            C[r["id"]] = False
            continue
        P = [q for q in S.rows if q["id"] in a and C[q["id"]]]
        past = lambda x, y: x in S.anc[y]
        if reads_concurrent:
            Cc = [q for q in S.rows if S.concurrent(q["id"], r["id"]) and _live(S, q, root)]
            C[r["id"]] = bool(rule(r, P, past, Cc))
        else:
            C[r["id"]] = bool(rule(r, P, past))
    return State(kept_rows, C)


def arrive(order, rule, root=None, wf=WELL_FORMED, wait=True):
    """The same two layers run as a node runs them: rows come one at a time in `order`; a row whose named
    rows are not all held waits; a row is concluded once, at the moment it is kept, and never again.
    Returns the State. `wait=False` drops a row that cannot be kept on arrival (a mutation for the check)."""
    held, ids, waiting, C, anc = [], {}, [], {}, {}
    for r in order:
        if r["id"] in ids or any(w["id"] == r["id"] for w in waiting):
            continue
        waiting.append(r)
        moved = True
        while moved:
            moved = False
            for w in list(waiting):
                if wf(w) and all(n in ids for n in w["names"]):
                    waiting.remove(w)
                    ids[w["id"]] = w
                    held.append(w)
                    a = anc[w["id"]] = ancestors(ids, w["id"])
                    live = root is None or root(w) or any(root(ids[x]) for x in a)
                    P = [q for q in held if q["id"] in a and C[q["id"]]]
                    C[w["id"]] = live and bool(rule(w, P, lambda x, y: x in anc[y]))
                    moved = True
        if not wait:
            waiting = []
    return State(held, C)


# ---- layer 3: derived ------------------------------------------------------------------------------------
def frontier(S, rows):
    """The rows of `rows` that no other row of `rows` has in its past. NOT IN kernel_lib."""
    return [r for r in rows if not any(r["id"] in S.anc[q["id"]] for q in rows)]


def wins(S, rows, label):
    """Of `rows` (concluded rows carrying a `target`), those with no row on the same target of a higher
    kind. Rows of the top kind all win: the order on kinds decides between kinds and nothing else."""
    on = [dict(r, _label=label(r)) for r in rows if r.get("target") is not None]
    # group(greatest) hands back one row and breaks a tie by list order; only its label is read
    top = K.group(on, "target", "greatest", "_label")
    return [r for r in rows if r.get("target") is not None and label(r) == top[r["target"]]["_label"]]


def slot(S, cands, value=lambda r: r["id"]):
    """Who holds a slot. `cands` are the concluded claims and deciding rows on it. A deciding row carries
    `picks` (a claim in its past) and speaks for that claim. Only the frontier speaks: a claim or decision
    that a later one names is answered by it. The slot holds the one value the frontier speaks; two values
    leave it empty. So two concurrent claims are both or neither, a row naming both decides, and a second
    decision concurrent with the first empties it again.
    `value` says when two rows say the same thing; the default is the row itself (its id).
    Returns (holder or None, number of distinct values spoken)."""
    ok = [r for r in cands if "picks" not in r or (r["picks"] in S.anc[r["id"]] and S.C.get(r["picks"]))]
    spoken = [{"v": value(S.by[r["picks"]]) if "picks" in r else value(r)} for r in frontier(S, ok)]
    return K.group(spoken, None, "one", "v"), K.group(spoken, None, "count", "v")


def counts(S, r, key=lambda r: r["signer"]):
    """Removal by causal past (Causal.counts): r counts iff it is concluded and it is in the past of every
    concluded row that removes key(r). A removal carries `removes`."""
    if not S.C.get(r["id"]):
        return False
    k = key(r)
    if k is None:
        return True
    return all(r["id"] in S.anc[x["id"]] for x in K.sel(S.Cs, removes=k))


def live_edges(S, any_signer_withdraws=False):
    """Concluded rows that carry `to` (signer -> to), with no concluded withdrawal that names the edge and
    is signed by the edge's own signer."""
    out = []
    for e in S.Cs:
        if e.get("to") is None:
            continue
        wd = [w for w in K.sel(S.Cs, kind="withdraw") if e["id"] in w["names"]
              and (any_signer_withdraws or w["signer"] == e["signer"])]
        if not wd:
            out.append(e)
    return out


def reach(S, own, depth, edges=None):
    """The keys a walk of at most `depth` live edges from the reader's own key arrives at."""
    E = live_edges(S) if edges is None else edges
    return K.fix(lambda ks: ks | frozenset(e["to"] for e in E if e["signer"] in ks), frozenset({own}), depth)


def means(S, r, own, depth, edges=None):
    return bool(S.C.get(r["id"])) and r["signer"] in reach(S, own, depth, edges)


def tally(S, proposal, members, choice="yes", kind="vote", counting=None):
    """Distinct counting voices: concluded rows of `kind` that name the proposal, signed by a key on the
    roster the proposal is counted over, that count. A voice that says two things says nothing."""
    counting = counting or (lambda v: counts(S, v))
    votes = [v for v in K.sel(S.Cs, kind=kind) if proposal["id"] in v["names"]
             and v["signer"] in members and counting(v)]
    said = K.group(votes, "signer", "one", "choice")
    return K.group([{"signer": s} for s, c in said.items() if c == choice], None, "count", "signer")


def merge(S, versions, base, bounds):
    """NOT IN kernel_lib, and not one of the functions the Lean file proves anything about: the state
    after several concurrent changes. `bounds` maps a change field to (bound, state field):
      grow_signed  the added values of every version are added (union)
      drop_only    the dropped values of every version are dropped (intersection of what remains);
                   a drop beats an add
      any          the slot rule: the one value the frontier of changers speaks; if they speak two, the
                   value they both extend (found the same way in their common past) and a conflict.
    Returns (state, set of fields in conflict)."""
    out, conflicts = dict(base), set()
    ch = lambda f: [v for v in versions if f in v.get("change", {})]
    for want in ("grow_signed", "drop_only", "any"):
        for f, (b, tgt) in bounds.items():
            if b != want:
                continue
            vals = frozenset(x for v in ch(f) for x in v["change"][f]) if b != "any" else None
            if b == "grow_signed":
                out[tgt] = frozenset(out[tgt]) | vals
            elif b == "drop_only":
                out[tgt] = frozenset(out[tgt]) - vals
            else:
                rows = ch(f)
                while rows:
                    holder, n = slot(S, rows, value=lambda r: r["change"][f])
                    if n == 1:
                        out[tgt] = holder
                        break
                    conflicts.add(tgt)
                    top = frontier(S, rows)
                    rows = [v for v in rows if all(v["id"] in S.anc[t["id"]] for t in top)]
    return out, conflicts
