#!/usr/bin/env python3
"""Roster forks: an exhaustive model of seven rules over sets of signed roster versions.

No sequencer, no signed instant, no node clock.  A roster version names other versions by
digest and that is the only order.  A version here is a value
    (builds_on, sets_aside, roster, signers)
and its identity is that value, so a set of versions is a set of digests.  The genesis
version is id 0.  Rosters and signer sets are bit masks over the member keys.

The model enumerates EVERY set of at most K versions that can exist when
  - an adversary holds the keys in F and signs anything, naming any head, and
  - an honest key signs a version only if its content passes `accepts` below
    (it never drops an honest member and never seats again a member some version it
    names has dropped).  Nothing is assumed about WHEN an honest key signed, so a
    version signed long ago and completed late (a stale head) is in the enumeration,
    and so is every withholding of rows from honest members.
Each rule is then a function from the set to (roster, resolved?, what counts), except
the rule in force today, which is run over every arrival order.

Rules (see ANSWER.md for the wording):
  T6   today: one parent, the first version seen on the held head wins (CC 3.2 T6)
  a    merge by the fold's bounds: a merge names both heads, is counted over the members
       common to both, and its roster is that intersection (plus one change of its own)
  b    one parent; a voice is void when a version the row does not name removes it
  c    one parent; a removal reaches only rows that no concurrent head has in its past
  d    a fork is evidence and the roster falls back to the last version every tip names,
       until a merge names both
  M0   tips wait: with one tip the roster is its roster, with several it is the members
       common to all; a merge names the tips, is counted over the members common to
       them, and states what it takes from each side; removal reach as (c)
  M1   M0, but a merge is counted over the roster of EACH head it names, not over the
       members common to them
  M2   M1, and a member that another named head's line has removed is left out of each
       head's count                                            <- the rule recommended
  M    M0, and a version may also name versions it sets aside (it is then counted over
       the heads it builds on only); nothing may build on what a version it names set
       aside
"""
import itertools, sys, json, time
from functools import lru_cache

# ----------------------------------------------------------------------------- world

class World:
    def __init__(self, n, R0, F, protocol, founders=0, family='dag', aside=False,
                 merge='restate', accept='strict', percount=0):
        self.n = n; self.ALL = (1 << n) - 1
        self.R0 = R0; self.F = F; self.H = self.ALL & ~F
        self.protocol = protocol; self.founders = founders
        self.family = family; self.aside = aside; self.merge = merge; self.accept = accept; self.percount = percount
        self.key = {}; self.vs = []; self.maxmerge = 4
        g = dict(id=0, E=(), A=(), R=R0, sig=0, past=frozenset(), line=frozenset([0]),
                 base=R0, ok=True, okM=True, drop=0, dropped=0, listed=R0,
                 dead=frozenset(), depth=0)
        self.vs.append(g); self.key[((), (), R0, 0)] = 0

    # the count: does the signer set s meet the protocol over the base roster b
    def meets(self, s, b):
        s &= b
        p = self.protocol
        k = bin(s).count('1'); nb = bin(b).count('1')
        if nb == 0: return False
        if p == 'majority': return 2 * k > nb
        if p == 'two_thirds': return 3 * k >= 2 * nb
        if p == 'unanimous': return k == nb
        if p.startswith('quorum'): return k >= int(p[6:])        # absolute M (CC 4.4.3.4.2.1)
        if p == 'founder_only': return (s & self.founders) != 0
        raise ValueError(p)

    # the count of a version over the heads it builds on: over the members common to them,
    # or (percount) over the roster of each head in turn
    def count_ok(self, sig, E):
        vs = self.vs
        if self.percount == 1:
            return all(self.meets(sig, vs[e]['R']) for e in E)
        if self.percount == 2:
            # over each head's roster, less the members another named head's line removed
            any_ = False
            for e in E:
                gone = 0
                for q in E:
                    if q != e: gone |= vs[q]['dropped']
                el = vs[e]['R'] & ~gone
                if el == 0: continue
                any_ = True
                if not self.meets(sig, el): return False
            return any_
        base = self.ALL
        for e in E: base &= vs[e]['R']
        return self.meets(sig, base)

    def mk(self, E, A, R, sig):
        E = tuple(sorted(E)); A = tuple(sorted(A))
        k = (E, A, R, sig)
        if k in self.key: return self.key[k]
        vs = self.vs
        past = set()
        for w in E + A:
            past.add(w); past |= vs[w]['past']
        line = {len(vs)}
        for e in E: line |= vs[e]['line']
        base = self.ALL
        for e in E: base &= vs[e]['R']
        ok = all(vs[e]['ok'] for e in E) and self.count_ok(sig, E)
        out = set()
        for x in A: out |= vs[x]['line']
        out -= line
        dead = set(out)
        for w in E + A: dead |= vs[w]['dead']
        okM = ok and all(vs[e]['okM'] for e in E) and not (line & dead)
        union = 0
        for e in E: union |= vs[e]['R']
        drop = union & ~R                       # listed by a head it builds on, not by it
        dropped = drop; listed = R
        for w in E + A:
            if vs[w]['ok']:
                dropped |= vs[w]['dropped']; listed |= vs[w]['listed']
        v = dict(id=len(vs), E=E, A=A, R=R, sig=sig, past=frozenset(past),
                 line=frozenset(line), base=base, ok=ok, okM=okM, drop=drop,
                 dropped=dropped, listed=listed, dead=frozenset(dead),
                 depth=1 + max(vs[w]['depth'] for w in E + A))
        vs.append(v); self.key[k] = v['id']
        return v['id']

    def valid(self, i):
        return self.vs[i]['okM'] if self.aside else self.vs[i]['ok']

    # would an honest key sign a version with these contents
    def accepts(self, E, A, R):
        vs = self.vs
        base = self.ALL; dropped = 0; listed = 0
        for e in E: base &= vs[e]['R']
        for w in tuple(E) + tuple(A):
            if vs[w]['ok']:
                dropped |= vs[w]['dropped']; listed |= vs[w]['listed']
        if R & self.F & dropped: return False            # never seats a dropped key again
        if self.accept == 'strict':
            return (listed & self.H) & ~R == 0           # keeps every honest member it names
        return (base & self.H) & ~R == 0                 # keeps every honest member of its base

    def sigsets(self, E, okh):
        vs = self.vs; pool = 0; base = self.ALL
        for e in E: pool |= vs[e]['R']; base &= vs[e]['R']
        if not self.percount: pool = base
        res = []
        s = pool
        while True:
            if (okh or (s & self.H) == 0) and self.count_ok(s, E):
                res.append(s)
            if s == 0: break
            s = (s - 1) & pool
        return res

    # every version that could be added to the set S (frozenset of ids, 0 included)
    def children(self, S, honest_only=False):
        vs = self.vs
        val = [i for i in S if self.valid(i)]
        out = []
        def emit(E, A, R):
            okh = self.accepts(E, A, R)
            if honest_only:
                if not okh: return
                pool = 0
                for e in E: pool |= vs[e]['R']
                s = pool & self.H
                if self.count_ok(s, E):
                    i = self.mk(E, A, R, s)
                    if self.valid(i) and i not in S: out.append(i)
                return
            for s in self.sigsets(E, okh):
                i = self.mk(E, A, R, s)
                if self.valid(i) and i not in S: out.append(i)
        def asides(E):
            if not self.aside: return [()]
            pe = set(E)
            for e in E: pe |= vs[e]['past']
            return [()] + [(x,) for x in S if x not in pe and vs[x]['ok']]
        for p in val:
            Rp = vs[p]['R']
            for A in asides((p,)):
                if A: emit((p,), A, Rp)
                for m in range(self.n):
                    emit((p,), A, Rp ^ (1 << m))
        if self.family == 'dag':
            for size in range(2, min(self.maxmerge, len(val)) + 1):
                for E in itertools.combinations(val, size):
                    if any(p in vs[q]['past'] or q in vs[p]['past'] for p, q in itertools.combinations(E, 2)): continue
                    lo = self.ALL; hi = 0
                    for e in E: lo &= vs[e]['R']; hi |= vs[e]['R']
                    for A in asides(E):
                        if self.merge == 'restate':
                            d = hi & ~lo; s = d
                            while True:
                                emit(E, A, lo | s)
                                if s == 0: break
                                s = (s - 1) & d
                        else:                              # literal (a): the intersection, +-1
                            emit(E, A, lo)
                            for m in range(self.n):
                                emit(E, A, lo ^ (1 << m))
        return out

# ----------------------------------------------------------------------------- rules

def tips_of(W, S, ids):
    vs = W.vs
    covered = set()
    for i in ids: covered |= vs[i]['past']
    return [i for i in ids if i not in covered]

def bits(m): return bin(m).count('1')

class Concl:
    __slots__ = ('roster', 'resolved', 'tips', 'valid', 'note')
    def __init__(s, roster, resolved, tips, valid, note=''):
        s.roster = roster; s.resolved = resolved; s.tips = tips; s.valid = valid; s.note = note

def conclude(W, S, rule):
    vs = W.vs
    if rule == 'b': return conclude_b(W, S)
    val = [i for i in S if W.valid(i)]
    tp = tips_of(W, S, val)
    if len(tp) == 1:
        return Concl(vs[tp[0]]['R'], True, tp, val)
    if rule == 'd':
        common = None
        for t in tp:
            l = vs[t]['line']
            common = set(l) if common is None else common & l
        mx = tips_of(W, S, list(common))
        r = W.ALL
        for t in mx: r &= vs[t]['R']
        return Concl(r, False, tp, val, 'fell back to %s' % mx)
    r = W.ALL
    for t in tp: r &= vs[t]['R']
    return Concl(r, False, tp, val)

def conclude_b(W, S):
    """Rule (b) by the well-founded model.  valid(V) reads valid(rho) negatively for a
    removal rho, concurrent with V, of one of V's voices; T is what is certainly valid,
    U what is possibly valid."""
    vs = W.vs
    P = [i for i in S if vs[i]['ok']]
    P.sort(key=lambda i: vs[i]['depth'])
    def gamma(I):
        out = {0}
        for i in P:
            if i == 0: continue
            v = vs[i]
            if not all(e in out for e in v['E']): continue
            voices = v['sig'] & v['base']
            for r in I:
                if r == i or r in v['past'] or i in vs[r]['past']: continue
                voices &= ~vs[r]['drop']
            if W.meets(voices, v['base']): out.add(i)
        return out
    T = set()
    while True:
        U = gamma(T); T2 = gamma(U)
        if T2 == T: break
        T = T2
    front = [i for i in U if not any(i in vs[c]['E'] and c in T for c in U)]
    r = W.ALL
    for t in front: r &= vs[t]['R']
    c = Concl(r, len(front) == 1 and U == T, front, sorted(T), '' if U == T else 'undecided: %s' % sorted(U - T))
    return c

def counts(W, S, rule, C, m, X):
    """Does a row of member m, first named by the valid version X, count?
    (A row named by X is in the past of exactly the versions that name X or are X.)"""
    vs = W.vs; bit = 1 << m
    val = C.valid if rule == 'b' else [i for i in S if W.valid(i)]
    drops = [r for r in val if vs[r]['drop'] & bit and bits(len(vs[r]['E'])) and len(vs[r]['E']) == 1]
    up = lambda a, b: a == b or a in vs[b]['past']      # a is b or in b's past
    if rule in ('T6', 'a', 'b', 'd'):                   # the plain rule: in the past of every removal
        return all(up(X, r) for r in drops)
    if rule == 'c':                                     # in the past of the removal or of a head concurrent with it
        for r in drops:
            if up(X, r): continue
            if any(up(X, y) for y in val if y != r and y not in vs[r]['past'] and r not in vs[y]['past']): continue
            return False
        return True
    # M0, M, M1: named by a standing version that builds on a version listing m
    if not drops: return True
    stand = set()
    for t in C.tips: stand |= vs[t]['line']
    for y in stand:
        if not up(X, y): continue
        if y == 0:
            if vs[0]['R'] & bit: return True
            continue
        if any(vs[e]['R'] & bit for e in vs[y]['E']): return True
    return False

# the rule in force today: a node holds one head; a version is admitted iff it names it
def t6_run(W, order):
    vs = W.vs; head = 0
    for i in order:
        v = vs[i]
        if v['E'] == (head,) and W.meets(v['sig'], vs[head]['R']): head = i
    return head

# ----------------------------------------------------------------------------- printing

def names(W, m): return '{' + ','.join(('a' if (W.F >> i) & 1 else 'h') + str(i) for i in range(W.n) if (m >> i) & 1) + '}'

def show(W, S):
    vs = W.vs; lines = []
    ids = sorted(S, key=lambda i: (vs[i]['depth'], i))
    lab = {i: ('G' if i == 0 else 'v%d' % k) for k, i in enumerate(ids)}
    for i in ids:
        v = vs[i]
        if i == 0:
            lines.append('  G   genesis roster %s' % names(W, v['R'])); continue
        ch = []
        add = v['R'] & ~v['base']; rem = v['base'] & ~v['R']
        if len(v['E']) > 1:
            ch.append('merge, roster %s' % names(W, v['R']))
        else:
            if add: ch.append('adds %s' % names(W, add))
            if rem: ch.append('removes %s' % names(W, rem))
            if not add and not rem: ch.append('no change')
        s = '  %-3s builds on %s' % (lab[i], ','.join(lab[e] for e in v['E']))
        if v['A']: s += ', sets aside %s' % ','.join(lab[a] for a in v['A'])
        s += ': %s; signed %s of %s' % ('; '.join(ch), names(W, v['sig']), names(W, v['base']))
        lines.append(s)
    return '\n'.join(lines), lab

# ----------------------------------------------------------------------------- checks

RULES = {
    #        family  aside  merge      accept
    'T6': ('tree', False, 'restate', 'strict'),
    'a':  ('dag',  False, 'literal', 'base'),
    'b':  ('tree', False, 'restate', 'strict'),
    'c':  ('tree', False, 'restate', 'strict'),
    'd':  ('dag',  False, 'restate', 'strict'),
    'M0': ('dag',  False, 'restate', 'strict'),
    'M':  ('dag',  True,  'restate', 'strict'),
    'M1': ('dag',  False, 'restate', 'strict', 1),
    'M2': ('dag',  False, 'restate', 'strict', 2),
}

def world(rule, n, R0, F, protocol, founders=0):
    fam, aside, merge, accept = RULES[rule][:4]
    return World(n, R0, F, protocol, founders, fam, aside, merge, accept, RULES[rule][4] if len(RULES[rule]) > 4 else 0)

def enumerate_sets(W, K, cap=None):
    level = {frozenset([0])}
    yield 0, level
    for k in range(1, K + 1):
        nxt = set()
        for S in level:
            for c in W.children(S):
                nxt.add(S | {c})
            if cap and len(nxt) > cap: break
        level = nxt
        yield k, level

def in_regime(W, S):
    """The adversary's keys do not meet the count over the roster of any valid version."""
    vs = W.vs
    for i in S:
        if not W.valid(i): continue
        if W.meets(W.F, vs[i]['R']): return False
    return True

def good(W, S, C):
    """No honest member some valid version lists is missing; no dropped adversary key is listed."""
    vs = W.vs; listed = 0; dropped = 0
    val = C.valid
    for i in val:
        listed |= vs[i]['R']; dropped |= vs[i]['drop']
    lost = listed & W.H & ~C.roster
    kept = C.roster & W.F & dropped
    return lost, kept

def best_row(W, S, rule):
    """One version signed by honest keys alone after which there is one tip and the roster is good."""
    for c in W.children(S, honest_only=True):
        S2 = S | {c}
        C2 = conclude(W, S2, rule)
        if C2.resolved:
            lost, kept = good(W, S2, C2)
            if not lost and not kept: return c
    return None

def check(rule, n, R0, F, protocol, K, founders=0, regime=True, cap=None, want_orders=True):
    W = world(rule, n, R0, F, protocol, founders)
    vs = W.vs
    res = dict(rule=rule, protocol=protocol, n=n, R0=R0, F=F, K=K, regime=regime, sets=0, forks=0,
               function=None, nsf_resolved=None, not_final=None, nsf_now=None, nsf_lost_after_row=None, kept_removed=None,
               stale=None, rejoin=None, adv_alone=None, removed_voice=None, double_signer_missing=None,
               unresolved_without_fork=None)
    def first(key, S, text):
        if res[key] is None:
            body, lab = show(W, S)
            res[key] = dict(size=len(S) - 1, text=text, rows=body)
    t0 = time.time()
    for k, level in enumerate_sets(W, K, cap):
        for S in sorted(level, key=lambda s: sorted(s)):
            if regime and not in_regime(W, S): continue
            res['sets'] += 1
            ids = sorted(S)
            if rule == 'T6':
                heads = set()
                non0 = [i for i in ids if i]
                for order in itertools.permutations(non0):
                    heads.add(t6_run(W, order))
                if len(heads) > 1:
                    res['forks'] += 1
                    first('function', S, 'arrival orders end at %d different heads with rosters %s'
                          % (len(heads), sorted(names(W, vs[h]['R']) for h in heads)))
                    # every later check is per node; take each head in turn
                for h in heads:
                    R = vs[h]['R']; line = vs[h]['line']
                    listed = 0; dropped = 0
                    for i in S:
                        if vs[i]['ok']: listed |= vs[i]['R']; dropped |= vs[i]['drop']
                    if listed & W.H & ~R:
                        first('nsf_now', S, 'a node that saw the other side first never lists %s' % names(W, listed & W.H & ~R))
                        first('nsf_lost_after_row', S, 'no version naming both exists; the member stays out at that node: %s' % names(W, listed & W.H & ~R))
                    if R & W.F & dropped:
                        first('kept_removed', S, 'a node that saw the other side first keeps %s' % names(W, R & W.F & dropped))
                for h in heads:
                    v = vs[h]
                    if not v['drop'] or bits(v['drop']) != 1: continue
                    m = v['drop'].bit_length() - 1
                    for X in S:
                        if X in (h,) or X in v['past'] or not vs[X]['ok']: continue
                        if h in vs[X]['past']: continue
                        if not any((vs[e]['R'] >> m) & 1 for e in vs[X]['E']): continue
                        body, lab = show(W, S)
                        first('stale', S, 'at a node that saw the removal %s first, a row of %s first named by %s does not count' % (lab[h], names(W, 1 << m), lab[X]))
                        break
                if len(heads) > 1:
                    first('rejoin', S, 'a version names one head; no row brings the nodes together')
                continue
            C = conclude(W, S, rule)
            if len(C.tips) > 1: res['forks'] += 1
            if not C.resolved and len([i for i in S if vs[i]['ok']]) and len(tips_of(W, S, [i for i in S if vs[i]['ok']])) == 1:
                first('unresolved_without_fork', S, 'one chain, yet the rule does not conclude: %s' % C.note)
            lost, kept = good(W, S, C)
            if rule == 'b':
                # honest members listed by a plainly valid version
                listed = 0; dropped = 0
                for i in S:
                    if vs[i]['ok']: listed |= vs[i]['R']; dropped |= vs[i]['drop']
                lost = listed & W.H & ~C.roster; kept = C.roster & W.F & dropped
            if kept:
                first('kept_removed', S, 'the roster %s lists %s, which a valid version removed' % (names(W, C.roster), names(W, kept)))
            if (lost or kept) and C.resolved:
                first('nsf_resolved', S, 'one tip, roster %s: leaves out %s, keeps %s' % (names(W, C.roster), names(W, lost), names(W, kept)))
            if rule in ('b', 'M') and k < K:
                cv = set(C.valid)
                for c in W.children(S):
                    C2 = conclude(W, S | {c}, rule)
                    if not cv <= set(C2.valid):
                        S2 = S | {c}
                        body, lab = show(W, S2)
                        first('not_final', S2, 'adding %s makes %s stop being valid' % (lab[c], ','.join(lab[x] for x in sorted(cv - set(C2.valid)))))
                        break
            if lost:
                first('nsf_now', S, 'the roster %s leaves out %s' % (names(W, C.roster), names(W, lost)))
            if (lost or kept or not C.resolved) and k < K + 1:
                b = best_row(W, S, rule)
                if b is None:
                    if lost or kept:
                        first('nsf_lost_after_row', S, 'roster %s; no one version signed by the honest members alone restores it' % names(W, C.roster))
                    if not C.resolved:
                        first('rejoin', S, 'tips %d; no one version signed by the honest members alone leaves one tip with every honest member listed and every removed key out' % len(C.tips))
            if rule != 'b':
                for c in W.children(S):
                    if vs[c]['sig'] & W.H == 0:
                        S2 = S | {c}; body, lab = show(W, S2)
                        first('adv_alone', S2, '%s is valid and signed by the adversary alone' % lab[c])
                        break
            # removal reach
            val = C.valid
            for r in val:
                v = vs[r]
                if len(v['E']) != 1 or not v['drop']: continue
                rest = [y for y in val if y != r and r not in vs[y]['past']]   # what does not name the removal
                tp = tips_of(W, S, rest)
                if len(tp) != 1 or tp[0] == v['E'][0]: continue          # it is not stale
                T = tp[0]; m = v['drop'].bit_length() - 1
                if bits(v['drop']) != 1 or not (vs[T]['R'] >> m) & 1: continue
                if not W.meets(v['sig'], vs[T]['R']):                    # would not be valid on the newest head
                    continue
                for X in rest:
                    if X == 0 and not (vs[0]['R'] >> m) & 1: continue
                    if X and not any((vs[e]['R'] >> m) & 1 for e in vs[X]['E']): continue
                    if not counts(W, S, rule, C, m, X):
                        body, lab = show(W, S)
                        first('stale', S, 'the removal %s names %s, not the newest head %s; a row of %s first named by %s does not count, and would count had the removal named %s'
                              % (lab[r], lab[v['E'][0]], lab[T], names(W, 1 << m), lab[X], lab[T]))
                        break
            # the removed member's voice
            for r in val:
                d = vs[r]['drop']
                if not d or len(vs[r]['E']) != 1: continue
                for y in val:
                    if y == r or y in vs[r]['past'] or r in vs[y]['past']: continue
                    vy = vs[y]
                    if vy['drop'] == d: continue
                    if vy['sig'] & d and not W.count_ok(vy['sig'] & ~d, vy['E']):
                        body, lab = show(W, S)
                        first('removed_voice', S, '%s is valid only with the voice of %s, whom %s removes; neither names the other' % (lab[y], names(W, d), lab[r]))
            # two valid versions with one past: is there a key that signed both
            if protocol in ('majority', 'two_thirds', 'unanimous'):
                for x, y in itertools.combinations([i for i in val if i], 2):
                    if vs[x]['E'] == vs[y]['E'] and vs[x]['A'] == vs[y]['A'] and not (vs[x]['sig'] & vs[y]['sig'] & vs[x]['base']):
                        first('double_signer_missing', S, 'two valid versions on one base share no signer')
    res['seconds'] = round(time.time() - t0, 1)
    res['versions'] = len(vs)
    return res

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--rule', default='M'); ap.add_argument('--n', type=int, default=5)
    ap.add_argument('--R0', default='0123'); ap.add_argument('--F', default='3')
    ap.add_argument('--protocol', default='majority'); ap.add_argument('--K', type=int, default=3)
    ap.add_argument('--founders', default=''); ap.add_argument('--any', action='store_true')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    m = lambda s: sum(1 << int(c) for c in s)
    r = check(a.rule, a.n, m(a.R0), m(a.F), a.protocol, a.K, m(a.founders), regime=not a.any)
    if a.json:
        print(json.dumps(r))
    else:
        for k, v in r.items():
            if isinstance(v, dict):
                print('%s: FAILS at %d versions: %s\n%s' % (k, v['size'], v['text'], v['rows']))
            else:
                print('%s: %s' % (k, v))
