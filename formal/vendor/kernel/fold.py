#!/usr/bin/env python3
"""The fold at tips: roster_fork's enumeration (fork.py, unchanged) with three things added.

    the strict fold   with several tips the roster is the fold of every tip's changes: a member any tip's line
                      removed is out, unless a later addition has that removal in its past; a member some tip adds
                      is in where the version that adds it meets its count on the voices of members the fold
                      seats, over the members of its heads that the fold seats (a least fixed point from the
                      common members). Tips that differ in policy do not fold: they wait, as under M0.
    a policy change   a counted version with the roster of its head and policy 1, which asks every member's
                      signature for a later change. Two tips that differ in policy conflict.
    authored heads    a version one key writes: an outsider's own admission to an open room, and a member's own
                      resignation. It is valid on its signer's signature alone.

What a version naming several heads is counted over is a parameter (`base`):
    common    the members common to every head it names (M0, and the first wording of the text)
    counted   the members common to the newest COUNTED versions in the past of the heads it names, less the
              members who resigned there. An authored head narrows no count but by its own signer.

MUT holds planted breaks, switched on by fold_check.py.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
import fork as F  # noqa: E402

MUT = set()


class FoldWorld(F.World):
    def __init__(self, n, R0, Fm, protocol, authored=False, policy=False, base="counted"):
        super().__init__(n, R0, Fm, protocol, 0, "dag", False, "restate", "strict", 0)
        self.authored, self.policy, self.basis = authored, policy, base
        self.auth = {}                    # id -> ("admit" | "resign", key bit)
        self.pol = {0: 0}                 # id -> policy

    # ---- counts ------------------------------------------------------------------------------------------
    def meets_pol(self, s, b, pol, drop=0):
        if pol == 0:
            return self.meets(s, b, drop)
        b2 = b & ~drop
        return b2 != 0 and (s & b2) == b2                      # policy 1: every member signs

    def counted_tips(self, E):
        """The newest counted versions among the heads E and their pasts."""
        vs = self.vs
        ids = set()
        for e in E:
            ids.add(e); ids |= vs[e]["past"]
        cs = [i for i in ids if i not in self.auth and self.valid(i)]
        return F.tips_of(self, None, cs), ids

    def count_base(self, E):
        vs = self.vs
        if self.basis == "common" or "narrow" in MUT:
            b = self.ALL
            for e in E: b &= vs[e]["R"]
            return b
        ct, ids = self.counted_tips(E)
        b = self.ALL
        for t in ct: b &= vs[t]["R"]
        for i in ids:                                           # a resignation takes its own signer out
            a = self.auth.get(i)
            if a and a[0] == "resign" and not any(i in vs[t]["past"] for t in ct): b &= ~a[1]
        return b

    def count_ok(self, sig, E, drop=0):
        pol = max(self.pol.get(e, 0) for e in E)
        return self.meets_pol(sig, self.count_base(E), pol, drop)

    def sigsets(self, E, okh, drop=0):
        pool = self.count_base(E)
        res = []
        s = pool
        while True:
            if (okh or (s & self.H) == 0) and self.count_ok(s, E, drop):
                res.append(s)
            if s == 0: break
            s = (s - 1) & pool
        return res

    def accepts(self, E, A, R):
        """An honest key signs what fork.py's honest key signs, and does not ask a member who resigned to stay."""
        vs = self.vs
        left = 0
        ids = set()
        for e in E:
            ids.add(e); ids |= vs[e]["past"]
        for i in ids:
            a = self.auth.get(i)
            if a and a[0] == "resign": left |= a[1]
        return super().accepts(E, A, R) or super().accepts(E, A, R | (left & self.H))

    # ---- versions ----------------------------------------------------------------------------------------
    def children(self, S, honest_only=False):
        vs = self.vs
        out = super().children(S, honest_only)
        for i in out:                                           # a counted version keeps the newest policy it names
            self.pol.setdefault(i, max(self.pol.get(e, 0) for e in vs[i]["E"]))
        val = [i for i in S if self.valid(i)]
        if self.policy:
            for p in val:
                if self.pol.get(p, 0): continue
                Rp = vs[p]["R"]
                sigs = [Rp & self.H] if honest_only else self.sigsets((p,), True)
                for s in sigs:
                    if not self.count_ok(s, (p,)): continue
                    i = self.mk((p,), (), Rp, s)
                    self.pol[i] = 1
                    if self.valid(i) and i not in S and i not in out: out.append(i)
        if self.authored:
            for p in val:
                Rp = vs[p]["R"]
                for m in range(self.n):
                    bit = 1 << m
                    if honest_only and not (bit & self.H): continue
                    if Rp & bit: kind, R = "resign", Rp & ~bit
                    elif vs[p]["dropped"] & bit: continue       # a removed key is no new key
                    else: kind, R = "admit", Rp | bit
                    i = self.mk((p,), (), R, bit)
                    if not vs[i]["ok"] or i in self.auth:
                        vs[i]["ok"] = vs[i]["okM"] = vs[p]["ok"]
                        self.auth[i] = (kind, bit)
                        self.pol[i] = self.pol.get(p, 0)
                    if self.valid(i) and i not in S and i not in out: out.append(i)
        return out


def fold(W, S):
    """(roster, resolved, tips, folded?): the strict fold over the valid versions of S."""
    vs = W.vs
    val = [i for i in S if W.valid(i)]
    tp = F.tips_of(W, S, val)
    if len(tp) == 1:
        return vs[tp[0]]["R"], True, tp, False
    common = W.ALL; union = 0; gone = 0
    for t in tp:
        common &= vs[t]["R"]; union |= vs[t]["R"]
    lines = set()
    for t in tp: lines |= vs[t]["line"]
    live = [i for i in lines if i and W.valid(i)]
    for zi in range(W.n):                                       # removed, and no later addition has that removal in its past
        z = 1 << zi
        if common & z: continue
        adds = [i for i in live if vs[i]["R"] & z and not any(vs[e]["R"] & z for e in vs[i]["E"])]
        if any(vs[r]["drop"] & z and not any(r in vs[a]["past"] for a in adds) for r in live): gone |= z
    if "authored_wait" in MUT and any(t in W.auth for t in tp):
        return common, False, tp, False
    if len({W.pol.get(t, 0) for t in tp}) > 1 and "policy_folds" not in MUT:
        return common, False, tp, False                         # tips that differ in policy wait
    if "keeps_removed" in MUT: gone = 0
    keep = common
    while True:                                                 # least fixed point: a voice counts once its key is in
        more = keep
        for zi in range(W.n):
            z = 1 << zi
            if not (union & z) or (keep & z) or (gone & z): continue
            adders = [i for i in live if vs[i]["R"] & z and not any(vs[e]["R"] & z for e in vs[i]["E"])]
            ok = bool(adders)
            for i in adders:
                if i in W.auth or "plain" in MUT: continue      # its own signature is its count
                base = W.ALL
                for e in vs[i]["E"]: base &= vs[e]["R"]
                seated = (union & ~gone) if "one_step" in MUT else keep
                if not W.meets_pol(vs[i]["sig"] & seated, base & seated, max(W.pol.get(e, 0) for e in vs[i]["E"])): ok = False
            if ok: more |= z
        if more == keep: break
        keep = more
    return keep & ~gone, False, tp, True


def adders_of(W, S, z):
    vs = W.vs
    return [i for i in S if i and W.valid(i) and vs[i]["R"] & z and not any(vs[e]["R"] & z for e in vs[i]["E"])]


def sets(W, K, regime):
    for _k, level in F.enumerate_sets(W, K):
        for S in sorted(level, key=lambda s: sorted(s)):
            if regime and not F.in_regime(W, S): continue
            yield S
