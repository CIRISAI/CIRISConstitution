"""
cut.py: the CUT as one derived rule, over causal_kernel's kept and concluded layers.

A cut is a concluded row that carries the slots it cuts. Once a cut counts, a row on one of those slots
that is CONCURRENT with the cut (not in its past, and not naming it) does not count. Rows in the cut's past
stand. Rows that name the cut are judged, as every row is, by the conclusion rule against their own past
(their signer's standing at the head they name). Concurrency with a kept row never changes, so what a
counting cut voids stays void for as long as the cut counts.

  slots a row is on      ("key", signer); its `slot`; anything in `on`
  slots a row cuts       `cuts`; ("key", k) if it carries removes=k; its `slot` if it is a deciding row
  what a cut says        `says`, else `picks`, else "out" for a removal, else its own id
  its voices             itself and the concluded `cosign` rows it names whose `of` is its `content`
  need                   distinct signers among live voices (default 1)
  rejects                ids in its past, on a slot it cuts, that it voids (how a row naming both decides)

A cut counts iff it is concluded, at least `need` of its voices are live (a voice is a row on its signer's
key slot, voided like any row), no counting cut that says something else on a shared slot is concurrent
with it, and no counting cut rejects it. "Counts" refers to itself through negation, and two rows can each
depend on the other not counting. That is solved the only symmetric way: the well-founded fixed point.
A cut is `counts` when it counts whatever the undecided ones do, `void` when it cannot count, and
`contested` otherwise. No digest, instant or rank is read.
"""
import causal_kernel as CK

K = CK.K


def on_slots(r):
    s = {("key", r["signer"])}
    if r.get("slot") is not None:
        s.add(r["slot"])
    return s | set(r.get("on", ()))


def cuts_of(r):
    c = set(r.get("cuts", ()))
    if r.get("removes") is not None:
        c.add(("key", r["removes"]))
    if r["kind"] == "decider" and r.get("slot") is not None:
        c.add(r["slot"])
    return frozenset(c)


def says(r):
    return r.get("says", r.get("picks", "out" if r.get("removes") is not None else r["id"]))


def voices(S, c):
    return [c] + [S.by[n] for n in c["names"] if S.C.get(n) and S.by[n]["kind"] == "cosign"
                  and S.by[n].get("of") == c.get("content")]


class Cut:
    """The three-valued status of every kept row of a concluded State."""

    def __init__(self, S, well_founded=True):
        self.S = S
        self.cuts = [r for r in S.Cs if cuts_of(r)]
        T = self._T
        if well_founded:
            self.L = K.fix(lambda L: T(T(L)), frozenset(), len(self.cuts) + 2)
            self.U = T(self.L)
        else:           # MUTATION for the check: judge cuts in list order, each against those already counting
            acc = frozenset()
            for c in self.cuts:
                if c["id"] in T(acc):
                    acc |= {c["id"]}
            self.L = self.U = acc

    def _voided(self, r, slots, A, as_cut=False):
        """Is r voided, on `slots`, by a cut in A?"""
        S = self.S
        for x in self.cuts:
            if x["id"] not in A or x["id"] == r["id"]:
                continue
            xs = cuts_of(x)
            if r["id"] in x.get("rejects", ()) and r["id"] in S.anc[x["id"]] and xs & (on_slots(r) | cuts_of(r)):
                return True
            if not S.concurrent(x["id"], r["id"]):
                continue
            hit = xs & slots
            if as_cut and says(x) == says(r):
                hit -= cuts_of(r)              # two concurrent cuts that say the same thing do not contest each other
            if hit:
                return True
        return False

    def _T(self, A):
        """The cuts that count if exactly the cuts in A do the voiding."""
        out = set()
        for c in self.cuts:
            live = [v for v in voices(self.S, c) if not self._voided(v, {("key", v["signer"])}, A)]
            if K.group(live, None, "count", "signer") < c.get("need", 1):
                continue
            if self._voided(c, (on_slots(c) - {("key", c["signer"])}) | cuts_of(c), A, as_cut=True):
                continue
            out.add(c["id"])
        return frozenset(out)

    def status(self, r):
        if not self.S.C.get(r["id"]):
            return "concludes nothing"
        if cuts_of(r):
            return "counts" if r["id"] in self.L else "contested" if r["id"] in self.U else "void"
        sl = on_slots(r)
        if self._voided(r, sl, self.L):
            return "void"
        return "contested" if self._voided(r, sl, self.U) else "counts"

    def counts(self, r):
        return self.status(r) == "counts"

    def all(self):
        return {r["id"]: self.status(r) for r in self.S.rows}

    def holder(self, slot, value=None):
        """Who holds a slot under the cut: the kernel's slot rule over the rows on it that count. A contested
        row on the slot leaves it in conflict."""
        value = value or (lambda r: r.get("says", r["id"]))
        on = [r for r in self.S.Cs if r.get("slot") == slot or slot in r.get("on", ()) or slot in cuts_of(r)]
        settled = [x for x in on if cuts_of(x) and self.counts(x)]        # a counting cut answers what is in its past
        if any(self.status(r) == "contested" and not any(r["id"] in self.S.anc[x["id"]] for x in settled) for r in on):
            return "conflict"
        h, n = CK.slot(self.S, [r for r in on if self.counts(r)], value)
        return h if n == 1 else ("empty" if n == 0 else "conflict")
