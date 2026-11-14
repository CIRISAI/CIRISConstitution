"""
claim.py: the two shapes the kernel had no module for, as functions over its kept and concluded layers.

CLAIM  one source's statement about a subject on a dimension, read through the reader's own trust; never one
       verdict for everyone. An acknowledgement is a claim: custody `here` or `none`, a receipt, presence.
    claim(id, k, subject, dim, value, names)
    trust(id, reader, source, scope)   a reader's trust edge: a consent that binds only the reader (one row), the
                                       kernel's edge (`to`), walked by causal_kernel.reach as `means` walks it
    claim_rule(polarity)               concluded: the value lies in the family's polarity
    read(S, reader, subject, dim, scope, depth) -> {source: value} over the sources the reader's own live edges
                                       reach (of `scope` where the family names a source seat); per source, the
                                       frontier of its live claims speaks one value or nothing

CONTENT  bytes or a record a person reads.
    content(id, author, item, audience, names)   audience: None (everyone), a set of keys, or ("roster", obj, scope)
    visible(S, reader, rid)            kept, concluded, the reader in its audience, not withdrawn or recanted by its
                                       author, not named by a later version of the same item by the same author.
                                       An audience that is a roster is read off the seats (seat.Seats.holders).

Retraction is one function for both: a withdraw or recant counts only when its signer signed the target.
Mutation switches (read by check_shapes.py): MUT is a set of names; each breaks one property.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import causal_kernel as CK  # noqa: E402

K, R = CK.K, CK.row
MUT = set()


def retracted(S, r):
    return any(w["target"] == r["id"] and ("any_signer" in MUT or w["signer"] == r["signer"])
               for w in S.Cs if w["kind"] in ("withdraw", "recant"))


def retract(id, signer, target, kind="withdraw"):
    return R(id, kind, signer, (target,), target=target)


# ---- claim ------------------------------------------------------------------------------------------------------
def claim(id, k, subject, dim, value, names=()):
    return R(id, "claim", k, names, subject=subject, dim=dim, value=value)


def trust(id, reader, source, scope="any", names=()):
    return R(id, "trust", reader, names, to=source, scope=scope)


def in_polarity(polarity, value):
    p = str(polarity)
    if p in ("+1.0 only", "positive-only"): return value > 0
    if p == "-1 only": return value == -1
    if p == "-1 / -0.5 only": return value in (-1, -0.5)
    return True                                           # signed, enumerated, boolean-via-score, per-leaf


def claim_rule(polarity):
    def rule(r, P, past):
        if r["kind"] == "claim":
            return "no_polarity" in MUT or in_polarity(polarity, r["value"])
        if r["kind"] in ("withdraw", "recant"):
            return any(q["id"] == r["target"] for q in P)
        return True
    return rule


def reached(S, reader, scope, depth):
    E = [e for e in K.sel(S.Cs, kind="trust") if ("ignore_scope" in MUT or scope == "any" or e["scope"] == scope)
         and not retracted(S, e)]
    return CK.reach(S, reader, depth, E)


def read(S, reader, subject, dim, scope="any", depth=2):
    live = [c for c in K.sel(S.Cs, kind="claim", subject=subject, dim=dim) if not retracted(S, c)]
    srcs = {c["signer"] for c in live} if "everyone" in MUT else reached(S, reader, scope, depth)
    pos = {r["id"]: i for i, r in enumerate(S.rows)}
    out = {}
    for s in sorted(srcs):
        on = [c for c in live if c["signer"] == s]
        if not on: continue
        if "last_held" in MUT:
            out[s] = max(on, key=lambda c: pos[c["id"]])["value"]; continue
        v = K.group([{"v": c["value"]} for c in K.frontier(S.anc, on)], None, "one", "v")
        if v is not None: out[s] = v
    return out


# ---- content ----------------------------------------------------------------------------------------------------
def content(id, author, item, audience=None, names=()):
    if isinstance(audience, (set, frozenset, list)): audience = frozenset(audience)
    return R(id, "content", author, names, item=item, audience=audience)


def in_audience(S, reader, r):
    a = r["audience"]
    if a is None or "ignore_audience" in MUT or reader == r["signer"]: return True
    if isinstance(a, tuple) and a and a[0] == "roster":
        import seat as ST
        return reader in ST.Seats(S).holders(a[2], a[1])
    return reader in a


def visible(S, reader, rid):
    r = S.by.get(rid)
    if r is None or not S.C.get(rid) or r["kind"] != "content": return False
    if not in_audience(S, reader, r): return False
    if retracted(S, r): return False
    later = [q for q in K.sel(S.Cs, kind="content", item=r["item"], signer=r["signer"]) if rid in S.anc[q["id"]]]
    return not later
