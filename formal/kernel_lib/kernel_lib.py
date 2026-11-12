"""
The shared library: five functions. A row is a dict; `t` is the instant the node first held it.
Nothing here knows any family, any model or any rule.
"""
ALWAYS = float("-inf")


def sel(S, before=None, **pat):
    """The rows of S that match the pattern and were first held strictly before `before` (no bound if None).
    A pattern value is a field value, or a set of accepted values."""
    out = []
    for r in S:
        if before is not None and not r["t"] < before: continue
        if all((r.get(f) in v) if isinstance(v, (set, frozenset)) else (r.get(f) == v) for f, v in pat.items()):
            out.append(r)
    return out


def group(S, by, how, val="t"):
    """Group S by field `by` (None: one group, the reduced value is returned bare) and reduce each group:
       least / greatest   the row least or greatest by `val` (a field or a tuple of fields); None when empty
       one                the single distinct `val` in the group; a group with two is dropped (None when bare)
       count              the number of distinct `val` in the group; 0 when empty"""
    key = (lambda r: tuple(r[f] for f in val)) if isinstance(val, tuple) else (lambda r: r[val])
    groups = {}
    for r in S: groups.setdefault(r[by] if by is not None else None, []).append(r)
    out = {}
    for g, rows in groups.items():
        if how == "least": out[g] = min(rows, key=key)
        elif how == "greatest": out[g] = max(rows, key=key)
        elif how == "count": out[g] = len({key(r) for r in rows})
        elif how == "one":
            vals = {key(r) for r in rows}
            if len(vals) == 1: out[g] = next(iter(vals))
        else: raise ValueError(how)
    if by is None: return out.get(None, 0 if how == "count" else None)
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
