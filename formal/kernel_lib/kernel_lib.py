"""
The shared library. A row is a dict; `t` is the instant the node first held it.
Nothing here knows any family, any model or any rule.

  sel, group, in_range, rule, fix      the five functions the six re-expressed models share
  ancestors, closure, concurrent,      the closure over what rows name (KERNEL.md section 4, last operator)
  frontier

Changed from the copy in the repository (formal/kernel_lib/kernel_lib.py), and why:
  sel      a pattern value matches only a field the row HAS. `sel(S, removes=None)` used to match every row
           with no `removes` field.
  group    `least` / `greatest` hand back a row, and used to break a tie by list order. Now a tie between two
           different rows raises Tie: the caller asked "which row" and the set does not say. Callers that only
           want the value use the new reducers `min` / `max`, which are functions of the set.
           `sum` is new: the sum of `val` over the distinct `per` of the group (default: the row's id); a `per`
           that states two values adds nothing, as a voice that says two things says nothing.
"""
ALWAYS = float("-inf")


class Tie(ValueError):
    """Two different rows are both the least (or the greatest). Nothing in the set picks one."""


def sel(S, before=None, **pat):
    """The rows of S that match the pattern and were first held strictly before `before` (no bound if None).
    A pattern value is a field value, or a set of accepted values. A row without the field never matches."""
    out = []
    for r in S:
        if before is not None and not r["t"] < before: continue
        if all(f in r and ((r[f] in v) if isinstance(v, (set, frozenset)) else (r[f] == v)) for f, v in pat.items()):
            out.append(r)
    return out


def _extreme(rows, key, pick):
    best = pick(key(r) for r in rows)
    tied = [r for r in rows if key(r) == best]
    if any(r != tied[0] for r in tied[1:]): raise Tie(best)
    return tied[0]


def group(S, by, how, val="t", per="id"):
    """Group S by field `by` (None: one group, the reduced value is returned bare) and reduce each group:
       least / greatest   the row least or greatest by `val` (a field or a tuple of fields); None when empty;
                          Tie when two different rows share the extreme
       min / max          the least or greatest `val` itself; None when empty
       one                the single distinct `val` in the group; a group with two is dropped (None when bare)
       count              the number of distinct `val` in the group; 0 when empty
       sum                the sum of `val` over the distinct `per`; a `per` with two values adds nothing; 0 when empty"""
    key = (lambda r: tuple(r[f] for f in val)) if isinstance(val, tuple) else (lambda r: r[val])
    groups = {}
    for r in S: groups.setdefault(r[by] if by is not None else None, []).append(r)
    out = {}
    for g, rows in groups.items():
        if how == "least": out[g] = _extreme(rows, key, min)
        elif how == "greatest": out[g] = _extreme(rows, key, max)
        elif how == "min": out[g] = min(key(r) for r in rows)
        elif how == "max": out[g] = max(key(r) for r in rows)
        elif how == "count": out[g] = len({key(r) for r in rows})
        elif how == "one":
            vals = {key(r) for r in rows}
            if len(vals) == 1: out[g] = next(iter(vals))
        elif how == "sum":
            said = {}
            for r in rows: said.setdefault(r[per], set()).add(key(r))
            out[g] = sum(next(iter(v)) for v in said.values() if len(v) == 1)
        else: raise ValueError(how)
    if by is None: return out.get(None, 0 if how in ("count", "sum") else None)
    return out


def in_range(x, lo, hi=None):
    """lo <= x < hi. An absent lo is an interval never opened (false); an absent hi is one not yet closed."""
    if x is None or lo is None: return False
    return lo <= x and (hi is None or x < hi)


def rule(table, key, default=None):
    """The cell a typed manifest gives for a key: a window, a basis class, a role set, a threshold."""
    return table.get(key, default)


def fix(step, state, bound):
    """Apply `step` until the state stops changing, at most `bound` times."""
    for _ in range(bound):
        nxt = step(state)
        if nxt == state: break
        state = nxt
    return state


# ---- the closure over what rows name ---------------------------------------------------------------------
def ancestors(by, rid, names="names"):
    """The ids `rid` names, and the ids those name, through the rows of `by` (id -> row). An id named and
    not held is in the answer and is followed no further."""
    step = lambda acc: acc | frozenset(n for a in acc | {rid} if a in by for n in by[a][names])
    return fix(step, frozenset(), len(by) + 1)


def closure(S, names="names"):
    """id -> ancestors, for every row of S."""
    by = {r["id"]: r for r in S}
    return {i: ancestors(by, i, names) for i in by}


def concurrent(anc, a, b):
    """Neither names the other, through any chain. `anc` is a closure."""
    return a != b and a not in anc[b] and b not in anc[a]


def frontier(anc, rows):
    """The rows of `rows` that no other row of `rows` has in its past."""
    return [r for r in rows if not any(r["id"] in anc[q["id"]] for q in rows)]


def past(S, anc, rid, inclusive=True):
    """The rows of S that are in the past of `rid` (and `rid` itself when inclusive): the head a row names."""
    return [r for r in S if r["id"] in anc[rid] or (inclusive and r["id"] == rid)]
