"""
purge.py: a node's checkpoint and purge (CC 2.7.10), over a small kernel of roster heads, acts, receipts,
counted cuts, windows and content, with answers indexed by head (CC 2.7.7, Settled.lean Part 12).

A node holds a STORE: for each row it has kept, either the whole row (its bytes) or a STUB. A stub keeps the
row's digest, the digests it names, its kind, the header fields a rule reads (the head it names, the act it
acknowledges or cuts, a roster version's members and count, a window's length and the instant the node first
held its opener), its conclusion, and, where an act's count at its own head is final, that answer. A stub of a
receipt or a cut of such an act is marked dropped: the cut and receipt rules no longer read it. The rest of a row, its body and the
signatures a cut carries, is gone.

The answers compared:
    kept       a row is kept iff every row it names is kept (stubs are kept rows)
    concluded  an act: its signer is a member at the head it names; a receipt: its signer is a member at the head
               of the act it names, and that act is in its past; the reader's own acknowledgement: signed by the
               node; anything else: yes
    countsAt   does the act count at the head it names: no counted act void for the reader (below), and no cut of
               it naming the SAME head, concurrent with it, whose say-holding signatures by members there reach the
               count. ONE SAY (CC 2.7.7 rule 6): a signer holding a clean receipt of the act in a row concurrent
               with the cut has no say on it
    carried    is the act still in force at the latest head: countsAt, and no cut of it naming a LATER head whose
               signatures by members there reach that head's count. A forward cut is blocked by nothing
    settled    clean receipts from n - t + 1 of the n members at the act's head are held (`ack_blocking_quorum`)
    missing    for an act not settled, the members at its head whose clean receipt is not held
    void       the counted rows (acts, cuts, roster versions) the reader's own acknowledged line holds void.
               BROAD (CC 2.7.8, the rule): every counted row that names a head strictly older than an acknowledged
               head and is not in that head's past. NARROW (kept as a planted difference): only roster versions so
               placed, and versions built on them
    window     open, answered or lapsed at `now`, read from the instant the node first held the opener

THE PURGE (the rule under test). The node signs a checkpoint naming the rows nothing it holds names; it is not an
acknowledgement and no answer reads it. Each row is then kept whole or as a stub:
    whole   a row under a duty of DUTIES, unless a deletion duty outranks it;
            an act whose countsAt is not final, and every receipt and every cut of it;
            every cut naming a head later than its act's (carried reads it again);
            a window opener whose window is open at the checkpoint
    stub    everything else. countsAt is final for a SETTLED act (for every reader), and, for this node only, for
            an act whose head is older than one the node has acknowledged (BROAD); its receipts and same-head cuts
            are then dropped. A row a deletion duty ends, and no hold suspends, keeps no bytes.

`reading="narrow"` runs the same purge and answers under the narrow reading; the check reports the rows each
reading keeps. PLANTS: `drop_unsettled`, `freeze_now`, `ck_acks` (the checkpoint read as an acknowledgement),
`drop_duty`, `keep_deleted`, `no_say` (every signature counts, purged and whole alike: the purge then
differs, so it rests on the one-say rule), `narrow_eval` (purged under the broad reading,
answered under the narrow), `freeze_carried` (carried stored at the checkpoint).
"""
import hashlib
import itertools

DUTIES = {
    "accountability": "CC 2.4.1.1: revocation, key revocation, moderation, track record, slashing and hard_case rows are never purgeable",
    "pinned": "CC 6.1.5.2 B1: identity, consent and config records are always pinned",
    "hold": "CC 4.4.3.2.8: a legal_hold pins the records it names, over retention and consent-driven descent",
    "floor": "CC 4.4.3.2.8: an affiliation class's retention floor pins its records above the noise floor",
    "owed": "CC 6.1.5.1, CC 3.1.3.3: a holder counted toward an item's target, or reporting here, holds its bytes",
    "preserve": "CC 7.5.5: a retirement record under an accepted preserve request",
}
DELETION = "CC 4.5.3, CC 3.3.1, CC 4.4.3.5.2, CC 6.1.5 N5: a takedown, a withdrawal or a revoked consent ends the bytes"
HEADER = ("id", "names", "kind", "signer", "head", "of", "members", "q", "length", "receipt", "duty", "delete")
COUNTED = ("act", "cut", "seat")


def row(id, kind, signer, names=(), **kw):
    r = {"id": id, "kind": kind, "signer": signer, "names": tuple(names), "body": kw.pop("body", 1)}
    r.update(kw)
    return r


class View:
    """Every answer, over a store plus newly offered rows, for the node signing under `own`."""

    def __init__(self, store, extra, own, reading="broad", say=True, plant=None):
        self.own, self.reading, self.say, self.plant = own, reading, say, plant
        self._memo = {}
        self.rec = dict(store)
        held = set(self.rec)
        pending, moved = [dict(r) for r in extra if r["id"] not in held], True
        while moved:                                    # the door: a row waits for what it names
            moved = False
            for r in list(pending):
                if all(n in held for n in r["names"]):
                    self.rec[r["id"]] = r; held.add(r["id"]); pending.remove(r); moved = True
        self.anc = {}
        for i in sorted(self.rec, key=self._depth):
            a = set()
            for n in self.rec[i]["names"]:
                a |= {n} | self.anc[n]
            self.anc[i] = frozenset(a)
        self.C = {i: self._concl(self.rec[i]) for i in self.rec}
        self.V = self._void()

    def _depth(self, i):
        if i not in self._memo:
            self._memo[i] = 1 + max((self._depth(n) for n in self.rec[i]["names"]), default=0)
        return self._memo[i]

    def conc(self, a, b):
        return a != b and a not in self.anc[b] and b not in self.anc[a]

    def members(self, head):
        return tuple(self.rec[head]["members"]) if head in self.rec else ()

    def _concl(self, r):
        if r.get("stub"):
            return r["concl"]                            # Settled.checkpoint_conclusions: the stored conclusion
        k = r["kind"]
        if k == "act":
            return r["signer"] in self.members(r["head"])
        if k == "ack":
            act = self.rec.get(r["of"])
            return act is not None and r["of"] in self.anc[r["id"]] and r["signer"] in self.members(act["head"])
        if k == "rack":
            return r["signer"] == self.own
        return True

    # ---- the reader's line ----
    def acked(self):
        out = {r["head"] for r in self.rec.values() if r["kind"] == "rack" and self.C[r["id"]]}
        if self.plant == "ck_acks":
            for r in self.rec.values():
                if r["kind"] == "checkpoint":
                    out |= {x for x in self.anc[r["id"]] if self.rec[x]["kind"] == "seat"}
        return out

    def heads_of(self, r):
        if r["kind"] == "seat":
            return [n for n in r["names"] if self.rec[n]["kind"] == "seat"]
        return [r["head"]] if r.get("head") else []

    def behind(self, r, A):
        """r names heads all strictly older than an acknowledged head h, and r is not in h's past."""
        hs = self.heads_of(r)
        return any(hs and all(x in self.anc[h] for x in hs) and r["id"] not in self.anc[h] and r["id"] != h for h in A)

    def _void(self):
        A = self.acked()
        reading = "narrow" if self.plant == "narrow_eval" else self.reading
        out = set()
        for i in sorted(self.rec, key=self._depth):
            r = self.rec[i]
            if r["kind"] not in COUNTED or not self.C[i]:
                continue
            if reading == "narrow" and r["kind"] != "seat":
                continue
            if self.behind(r, A) or any(h in out for h in self.heads_of(r)):
                out.add(i)
        return frozenset(out)

    # ---- receipts, the cut, settled ----
    def _cuts(self, a):
        return [c for c in self.rec.values() if c["kind"] == "cut" and c.get("of") == a and not c.get("dropped")
                and self.C[c["id"]] and c["id"] not in self.V]

    def receipts(self, a):
        """The keys holding a clean receipt of act a, each with its receipt rows."""
        out = {}
        for x in self.rec.values():
            if x["kind"] != "ack" or x.get("of") != a or x.get("dropped") or not self.C[x["id"]]:
                continue
            k = x["signer"]
            if not any(c["id"] in self.anc[x["id"]] and k in c["sigs"] for c in self._cuts(a)):
                out.setdefault(k, []).append(x["id"])
        return out

    def voids_at(self, c, a):
        act = self.rec[a]
        if c["head"] != act["head"] or not self.conc(c["id"], a):
            return False
        M, q = self.members(act["head"]), self.rec[act["head"]]["q"]
        R = self.receipts(a) if self.say and self.plant != "no_say" else {}
        voice = {k for k in c["sigs"] if k in M and not any(self.conc(x, c["id"]) for x in R.get(k, ()))}
        return len(voice) >= q

    def counts_at(self, a):
        r = self.rec[a]
        if r.get("final") is not None:
            return r["final"]
        if a in self.V:
            return False
        return not any(self.voids_at(c, a) for c in self._cuts(a))

    def carried(self, a):
        r = self.rec[a]
        if r.get("frozen_carried") is not None:
            return r["frozen_carried"]
        if not self.counts_at(a):
            return False
        for c in self._cuts(a):
            if c["head"] != r["head"] and r["head"] in self.anc[c["head"]]:
                if len({k for k in c["sigs"] if k in self.members(c["head"])}) >= self.rec[c["head"]]["q"]:
                    return False
        return True

    def settled(self, a):
        r = self.rec[a]
        if r.get("settled_stub"):
            return True
        M, q = self.members(r["head"]), self.rec[r["head"]]["q"]
        have = set(self.receipts(a)) | set(r.get("ackers", ()))
        return len(have & set(M)) >= len(M) - q + 1

    def closed_for_me(self, a):
        """countsAt is final for this node: its head is older than one it has acknowledged (broad reading)."""
        if self.reading != "broad":
            return False
        h = self.rec[a]["head"]
        return any(h in self.anc[x] for x in self.acked())

    def missing(self, a):
        r = self.rec[a]
        if self.settled(a):
            return ()
        have = set(self.receipts(a)) | set(r.get("ackers", ()))
        return tuple(sorted(set(self.members(r["head"])) - have))

    def window(self, o, now):
        r = self.rec[o]
        if r.get("frozen") is not None:
            return r["frozen"]
        if any(x["kind"] == "answer" and o in x["names"] for x in self.rec.values()):
            return "answered"
        return "lapsed" if now >= r["receipt"] + r["length"] else "open"

    def answers(self, now, skip=("ck",)):
        ids = sorted(i for i in self.rec if i not in skip)
        acts = [i for i in ids if self.rec[i]["kind"] == "act" and self.C[i]]
        return {
            "kept": tuple(ids),
            "concluded": tuple((i, self.C[i]) for i in ids),
            "countsAt": tuple((a, self.counts_at(a)) for a in acts),
            "carried": tuple((a, self.carried(a)) for a in acts),
            "settled": tuple((a, self.settled(a)) for a in acts),
            "missing": tuple((a, self.missing(a)) for a in acts),
            "void": tuple(sorted(i for i in self.V if i not in skip)),
            "window": tuple((o, self.window(o, now)) for o in ids if self.rec[o]["kind"] == "open"),
        }


def stub(r, concl, **kw):
    s = {k: r[k] for k in HEADER if k in r}
    s.update(stub=True, concl=concl)
    s.update(kw)
    return s


def duty_of(r):
    return set(r.get("duty", ()))


def purge(store, own, now, reading="broad", plant=None):
    """Sign a checkpoint over the store and drop what the rule lets it drop. Returns the new store."""
    V = View(store, (), own, reading, plant=plant)
    tips = sorted(i for i in V.rec if not any(i in V.rec[j]["names"] for j in V.rec) and i != "ck")
    digest = hashlib.sha256(repr(sorted(V.answers(now).items())).encode()).hexdigest()[:16]
    acts = [a for a in V.rec if V.rec[a]["kind"] == "act" and V.C[a]]
    final = {a for a in acts if V.settled(a) or V.closed_for_me(a)}
    open_ = set(acts) - final
    out = {}
    for i, r in V.rec.items():
        if i == "ck":
            continue
        if r.get("stub"):                                                # a stub stays a stub; a final act's receipt
            if r["kind"] == "act" and r.get("final") is not None and not r.get("settled_stub"):   # signers are kept
                r = dict(r, ackers=tuple(sorted(set(r.get("ackers", ())) | set(V.receipts(i)))), settled_stub=V.settled(i))
            out[i] = r
            continue
        d, k = duty_of(r), r["kind"]
        deleted = r.get("delete") and "hold" not in d                   # a hold suspends deletion; nothing else does
        whole = bool(d) and not deleted and plant != "drop_duty"
        if plant == "drop_unsettled":
            open_keep = set()
        else:
            open_keep = open_
        if k == "act" and i in open_keep:
            whole = True
        if k in ("ack", "cut") and r.get("of") in open_keep:
            whole = True
        if k == "cut" and r.get("of") in V.rec and V.rec[r["of"]].get("head") != r["head"]:
            whole = True                                                 # a forward cut: carried reads it again
        if k == "open" and V.window(i, now) == "open" and plant != "freeze_now":
            whole = True
        if deleted:
            whole = plant == "keep_deleted"
        kw = {}
        if k == "act" and V.C[i]:
            if i in final or plant == "drop_unsettled":
                kw.update(final=V.counts_at(i))
            if V.settled(i):
                kw.update(settled_stub=True, acks=tuple(sorted(x for xs in V.receipts(i).values() for x in xs)))
            elif i in final:
                kw.update(ackers=tuple(sorted(V.receipts(i))))
            if plant == "freeze_carried":
                kw.update(frozen_carried=V.carried(i))
        if whole:
            out[i] = dict(r, **kw)
            continue
        if k in ("ack", "cut") and r.get("of") in final:
            kw.update(dropped=True)
        if k == "open" and plant == "freeze_now":
            kw.update(frozen=V.window(i, now))
        out[i] = stub(r, V.C[i], **kw)
    out["ck"] = {"id": "ck", "kind": "checkpoint", "signer": own, "names": tuple(tips), "digest": digest, "body": 1}
    return out


def full_store(rows):
    return {r["id"]: r for r in rows}


# ---- histories ---------------------------------------------------------------------------------------------------
def seat(id, names, members, q, **kw):
    return row(id, "seat", "roster", names, members=tuple(members), q=q, **kw)


def act(id, signer, head, names=None, **kw):
    return row(id, "act", signer, names or (head,), head=head, **kw)


def ack(id, signer, of, names=None):
    return row(id, "ack", signer, names or (of,), of=of)


def cut(id, of, sigs, head, names=None):
    return row(id, "cut", sigs[0], names or (head,), of=of, sigs=tuple(sigs), head=head)


HISTORIES = []


def history(name, own, rows, pool, nows=(0,), now=0):
    HISTORIES.append(dict(name=name, own=own, rows=rows, pool=pool, nows=nows, now=now))


# The reviewer's case: a grant G seats X, X acts (E), and a revocation R of E is concurrent with E.
history("reviewer: grant, act, concurrent revocation", "N",
        [seat("v0", (), "ABC", 2), seat("G", ("v0",), "ABCX", 2), act("E", "X", "G")],
        [cut("R", "E", "AB", "G"), ack("aA", "A", "E"), ack("aB", "B", "E"), ack("aC", "C", "E")])
# A blocked act (three receipts of five, count three) and one still open to a cut.
history("blocked act, and one not yet blocked", "N",
        [seat("v0", (), "ABCDF", 3), act("e1", "A", "v0"), ack("a1A", "A", "e1"), ack("a1B", "B", "e1"),
         ack("a1C", "C", "e1"), act("e2", "B", "v0"), ack("a2A", "A", "e2"), ack("a2B", "B", "e2")],
        [cut("x1", "e1", "DFA", "v0"), cut("x2", "e2", "CDF", "v0"), ack("a2C", "C", "e2"), ack("a2D", "D", "e2")])
# A forked acknowledger: B gives a receipt, then signs a concurrent cut with C: one say.
history("forked acknowledger", "N",
        [seat("v0", (), "ABC", 2), act("E", "A", "v0"), ack("aA", "A", "E"), ack("aB", "B", "E")],
        [cut("xBC", "E", "BC", "v0"), row("p", "content", "C", ("aB",))])
# A cutter seated later: Z joins at v1 and cuts E with C at v1. It acts forward: E still counted at v0.
history("cutter seated later acts forward", "N",
        [seat("v0", (), "ABC", 2), act("E", "A", "v0"), ack("aA", "A", "E"), ack("aB", "B", "E")],
        [seat("v1", ("v0",), "ABCZ", 2), cut("xCZ", "E", "CZ", "v1", names=("v1",))])
# Duties: a held act, an owed row, an accountability row, a pinned record, a class under a retention floor, a
# retirement record under preservation, and a deleted row with and without a hold.
history("legal hold, owed row, never-purge rows, deletion", "N",
        [seat("v0", (), "ABC", 2), act("E", "A", "v0", duty=("hold",)), ack("aA", "A", "E"), ack("aB", "B", "E"),
         row("hc", "content", "B", ("v0",), duty=("accountability",)),
         row("kr", "content", "A", ("v0",), duty=("pinned",)),
         row("post", "content", "C", ("v0",), duty=("owed",)),
         row("gone", "content", "C", ("v0",), delete=True),
         row("kept_by_hold", "content", "C", ("v0",), delete=True, duty=("hold",)),
         row("ret", "content", "A", ("v0",), duty=("preserve",)), row("cls", "content", "B", ("v0",), duty=("floor",))],
        [cut("x", "E", "BC", "v0"), row("reply", "content", "B", ("post",))])
# Windows: one open at the checkpoint, one closed, and a late answer to each.
history("windows read now", "N",
        [seat("v0", (), "AB", 1), row("o1", "open", "A", ("v0",), length=20, receipt=10),
         row("o2", "open", "B", ("v0",), length=5, receipt=0)],
        [row("ans1", "answer", "B", ("o1",)), row("ans2", "answer", "A", ("o2",))],
        nows=(15, 35, 50), now=15)
# The reader's line: the node acknowledged v1; a late version on v0 is void for it with or without bytes.
history("reader's acknowledged line", "N",
        [seat("v0", (), "ABC", 2), seat("v1", ("v0",), "ABC", 2), row("rk", "rack", "N", ("v1",), head="v1")],
        [seat("u", ("v0",), "AB", 2), seat("u2", ("u",), "A", 2)])
# No acknowledgement of its own: a late removal on an old head counts, checkpoint or not.
history("late removal, no acknowledgement", "N",
        [seat("v0", (), "ABC", 2), seat("v1", ("v0",), "ABC", 2), act("E", "A", "v1"), ack("aA", "A", "E"),
         ack("aB", "B", "E")],
        [seat("u", ("v0",), "AB", 2), act("E2", "C", "u")])
# The reader closes an old head: E on v0 has one receipt; v1 is built on E and the node acknowledged v1. A late cut
# of E on v0 is void for this node under the broad reading, so E needs no receipts here; under the narrow it does.
history("reader closes an older head", "N",
        [seat("v0", (), "ABC", 2), act("E", "A", "v0"), ack("aA", "A", "E"), seat("v1", ("v0", "E"), "ABC", 2),
         row("rk", "rack", "N", ("v1",), head="v1"), act("F", "B", "v0"), ack("fB", "B", "F")],
        [cut("x", "E", "BC", "v0"), cut("y", "F", "AC", "v0"), ack("aB", "B", "E")])


def extensions(pool):
    for n in range(len(pool) + 1):
        for X in itertools.combinations(pool, n):
            yield list(X)


def run(h, reading="broad", plant=None):
    """Every extension X of the history's pool, at every `now`: the store purged once at the checkpoint and then
    offered X; and, for each part X1 of X, purged again after X1 arrives and then offered the rest. Each is
    compared with the rows held whole and nothing purged. Returns (replays, differences, store after the first purge)."""
    own, nows = h["own"], h["nows"]
    base = full_store(h["rows"])
    P = purge(base, own, h["now"], reading, plant)
    say = plant != "no_say"
    diffs, n = [], 0
    for X in extensions(h["pool"]):
        cases = [((), P)]
        for k in range(1, len(X)):
            for X1 in itertools.combinations(X, k):
                cases.append((X1, purge(dict(View(P, X1, own, reading, plant=plant).rec), own, h["now"], reading, plant)))
        for X1, store in cases:
            rest = [r for r in X if r["id"] not in store]
            for now in nows:
                n += 1
                want = View(base, X, own, reading, say).answers(now)
                got = View(store, rest, own, reading, say, plant).answers(now)
                if want != got:
                    k = next(k for k in want if want[k] != got.get(k))
                    diffs.append("%s; offered {%s}%s; now %s; %s: %s, purged %s" % (
                        h["name"], ",".join(r["id"] for r in X),
                        " (purged again after {%s})" % ",".join(r["id"] for r in X1) if X1 else "", now, k, want[k], got[k]))
    return n, diffs, P


def duty_breaches(h, store):
    out = []
    for r in h["rows"]:
        s = store.get(r["id"])
        d = duty_of(r)
        deleted = r.get("delete") and "hold" not in d
        if d and not deleted and (s is None or s.get("stub")):
            out.append("%s: %s dropped (%s)" % (h["name"], r["id"], "; ".join(DUTIES[x] for x in sorted(d))))
        if deleted and s is not None and not s.get("stub"):
            out.append("%s: %s kept whole against its deletion (%s)" % (h["name"], r["id"], DELETION))
    return out


def measure(store):
    whole = sum(1 for i, s in store.items() if i != "ck" and not s.get("stub"))
    stubs = sum(1 for i, s in store.items() if i != "ck" and s.get("stub"))
    return whole, stubs
