#!/usr/bin/env python3
"""M8: the refusal retry schedule, and a row refused during a rolling upgrade.

Run with ``python3 -I tools/models/retry_schedule.py``. Standard library only; no
network, no cargo, no files written. Every random draw comes from a seeded
``random.Random``, so two runs print the same tables. Exit status 1 if a sanity
check fails or a constant no longer matches the code.

The document that reads these tables is ``FSD/EVENT_PATH_MODEL.md`` section 1.
Every figure there is tagged [read] (in the code at the cited commit), [model]
(this script's output) or [inf] (inference not exercised by anything).

What the schedule is NOT, and the reason this file has a Sim at all: the windows in
``refusal_backoff.rs`` only say when a node MAY ask. A node asks only for a hash
some peer's Summary names, and past one page a peer names a row once per rolling
re-sweep. So a re-ask needs (window elapsed) AND (an offer arrived).
"""
from __future__ import annotations

import heapq
import math
import os
import random
import re
import statistics
import sys

SEED = 20261105

# --------------------------------------------------------------------------
# Constants, each read from the code. CITES is checked against the trees below.
# --------------------------------------------------------------------------
TRANSIENT_BASE = 20          # refusal_backoff.rs TRANSIENT_BASE
TRANSIENT_CAP = 300          # refusal_backoff.rs TRANSIENT_CAP
TERMINAL_BASE = 1800         # refusal_backoff.rs TERMINAL_BASE
TERMINAL_CAP = 21_600        # refusal_backoff.rs TERMINAL_CAP
CAP_HITS = 3                 # refusal_backoff.rs TRANSIENT_CAP_HITS_BEFORE_TERMINAL
MAX_KEYS = 4096              # refusal_backoff.rs DEFAULT_MAX_KEYS
CADENCE = 30                 # scheduler.rs DEFAULT_CADENCE; no jitter on the tick
ROUND_TIMEOUT = 10           # scheduler.rs DEFAULT_ROUND_TIMEOUT
PAGE = 1024                  # bridge.rs DEFAULT_SWEEP_PAGE_ROWS
RESWEEP_WARN = 900           # bridge.rs RESWEEP_CYCLE_BOUND
CURSORS = 512                # bridge.rs MAX_TRACKED_SWEEP_CURSORS
PROPAGATE_DEBOUNCE = 0.5     # runtime.rs PROPAGATE_DEBOUNCE

ROOT = "/home/emoore"
ONION = f"{ROOT}/CIRISEdge-onion/src/replication"
CITES = [
    ("TRANSIENT_BASE", TRANSIENT_BASE, f"{ONION}/refusal_backoff.rs", r"const TRANSIENT_BASE: Duration = Duration::from_secs\((\d+)\)"),
    ("TRANSIENT_CAP", TRANSIENT_CAP, f"{ONION}/refusal_backoff.rs", r"const TRANSIENT_CAP: Duration = Duration::from_secs\((\d+)\)"),
    ("TERMINAL_BASE", TERMINAL_BASE, f"{ONION}/refusal_backoff.rs", r"const TERMINAL_BASE: Duration = Duration::from_secs\((\d+)\)"),
    ("TERMINAL_CAP", TERMINAL_CAP, f"{ONION}/refusal_backoff.rs", r"const TERMINAL_CAP: Duration = Duration::from_secs\(([\d_]+)\)"),
    ("TRANSIENT_CAP_HITS_BEFORE_TERMINAL", CAP_HITS, f"{ONION}/refusal_backoff.rs", r"const TRANSIENT_CAP_HITS_BEFORE_TERMINAL: u32 = (\d+)"),
    ("DEFAULT_MAX_KEYS", MAX_KEYS, f"{ONION}/refusal_backoff.rs", r"const DEFAULT_MAX_KEYS: usize = (\d+)"),
    ("DEFAULT_CADENCE", CADENCE, f"{ONION}/scheduler.rs", r"const DEFAULT_CADENCE: Duration = Duration::from_secs\((\d+)\)"),
    ("DEFAULT_ROUND_TIMEOUT", ROUND_TIMEOUT, f"{ONION}/scheduler.rs", r"const DEFAULT_ROUND_TIMEOUT: Duration = Duration::from_secs\((\d+)\)"),
    ("DEFAULT_SWEEP_PAGE_ROWS", PAGE, f"{ONION}/bridge.rs", r"const DEFAULT_SWEEP_PAGE_ROWS: u32 = (\d+)"),
    ("RESWEEP_CYCLE_BOUND (min)", RESWEEP_WARN // 60, f"{ONION}/bridge.rs", r"const RESWEEP_CYCLE_BOUND: Duration = Duration::from_secs\((\d+) \* 60\)"),
    ("MAX_TRACKED_SWEEP_CURSORS", CURSORS, f"{ONION}/bridge.rs", r"const MAX_TRACKED_SWEEP_CURSORS: usize = (\d+)"),
]

# Corpus sizes the code's own comments carry (bridge.rs DEFAULT_SWEEP_PAGE_ROWS doc).
CORPUS = {"<=1 page": 1000, "14.6k rows": 14_616, "52k rows": 52_125}
TRANSIENT, TERMINAL = "transient", "terminal"


def verify_constants() -> list[str]:
    bad = []
    seen = 0
    for name, want, path, rx in CITES:
        if not os.path.exists(path):
            continue
        m = re.search(rx, open(path, encoding="utf-8").read())
        seen += 1
        if not m or int(m.group(1).replace("_", "")) != want:
            bad.append(f"{name}: model {want}, code {m.group(1) if m else 'absent'} ({path})")
    print(f"constants checked against the trees: {seen} of {len(CITES)}; mismatches: {len(bad)}")
    return bad


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
def table(headers, rows):
    w = [max(len(str(h)), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    print("  ".join(str(h).rjust(x) for h, x in zip(headers, w)))
    print("  ".join("-" * x for x in w))
    for r in rows:
        print("  ".join(str(c).rjust(x) for c, x in zip(r, w)))


def fmt(x):
    if x is None:
        return "never"
    if x < 100:
        return f"{x:.0f}s"
    if x < 5400:
        return f"{x / 60:.1f}m"
    return f"{x / 3600:.1f}h"


def h1(t):
    print("\n" + "=" * 96 + f"\n{t}\n" + "=" * 96)


def h2(t):
    print("\n-- " + t)


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, int(round(p * (len(xs) - 1)))))]


# --------------------------------------------------------------------------
# The schedule: a line-for-line port of RefusalBackoff::record_at for one row
# --------------------------------------------------------------------------
class Sched:
    """The schedule's constants, so a sanity check can move one."""

    def __init__(self, base=TRANSIENT_BASE, cap=TRANSIENT_CAP, tbase=TERMINAL_BASE, tcap=TERMINAL_CAP, hits=CAP_HITS):
        self.base, self.cap, self.tbase, self.tcap, self.hits = base, cap, tbase, tcap, hits

    def window(self, disposition, attempts):
        base, cap = (self.base, self.cap) if disposition == TRANSIENT else (self.tbase, self.tcap)
        return min(base * (1 << min(max(attempts - 1, 0), 16)), cap)


class Entry:
    __slots__ = ("attempts", "disposition", "retry_at", "cap_hits")

    def __init__(self):
        self.attempts, self.disposition, self.retry_at, self.cap_hits = 0, TRANSIENT, 0.0, 0


def record(e, disposition, now, s):
    """RefusalBackoff::record_at. Returns (entry, window)."""
    if e is None:
        e = Entry()
        e.attempts = 1
        e.disposition = disposition
        w = s.window(disposition, 1)
        e.retry_at = now + w
        return e, w
    e.attempts += 1
    if disposition == TRANSIENT:
        if s.window(TRANSIENT, e.attempts) >= s.cap:
            e.cap_hits += 1
        if e.cap_hits > s.hits:
            w = s.window(TERMINAL, e.cap_hits - s.hits)
            e.disposition = TERMINAL
            e.retry_at = now + w
            return e, w
    e.disposition = disposition
    w = s.window(disposition, e.attempts)
    e.retry_at = now + w
    return e, w


def sweep_period(corpus, summaries_per_cadence, page=PAGE, cadence=CADENCE):
    """Seconds between two offers of one row by one peer. [read] bridge.rs: below a page every
    Summary names the whole plane; above it one page per Summary. The initiator and responder
    sweeps of a (peer, kind) share one cursor, so both sides' rounds advance it."""
    gap = cadence / summaries_per_cadence
    return gap * max(1, math.ceil(corpus / page))


def ladder(period, holders, rng, delta=1.0, s=None, disposition=TRANSIENT, horizon=48 * 3600, stop_at_terminal=True,
           until=None):
    """One row, one refuser that always refuses, `holders` peers each naming it every `period`
    seconds on an independent phase. Returns [(refusal number, time, window, disposition)]."""
    s = s or Sched()
    offers = [(rng.uniform(0, period), i) for i in range(holders)]
    heapq.heapify(offers)
    e, log = None, []
    t0 = None
    while offers:
        t, i = heapq.heappop(offers)
        heapq.heappush(offers, (t + period, i))
        if t0 is not None and t - t0 > horizon:
            break
        if until is not None and t0 is not None and t - t0 > until:
            break
        if e is not None and t < e.retry_at:
            continue
        now = t + delta
        t0 = now if t0 is None else t0
        e, w = record(e, disposition, now, s)
        log.append((e.attempts, now - t0, w, e.disposition))
        if stop_at_terminal and e.disposition == TERMINAL:
            break
    return log


# --------------------------------------------------------------------------
# The rolling upgrade
# --------------------------------------------------------------------------
class Node:
    __slots__ = ("upgraded", "up", "holds", "entry", "gen", "admitted_at", "upgrade_at", "refusals", "peers",
                 "terminal", "asks")

    def __init__(self):
        self.upgraded, self.up, self.holds, self.entry, self.gen = False, True, False, None, 0
        self.admitted_at, self.upgrade_at, self.refusals, self.peers = None, 0.0, 0, []
        self.terminal, self.asks = False, 0


class Upgrade:
    """N nodes restart onto the new build, evenly over T seconds, one row in play.

    scenario "1192": the row is minted on the first upgraded node; an OLD node refuses it
                     (persist <= 61.0.1 counted the removed member as a voice).
    scenario "1200": a moderator's removal minted on an OLD node at T/2; an UPGRADED node
                     refuses it for good (61.0.3). A holder keeps it through its own upgrade.

    arm "shipped": a restart empties the refusal memory ([read] refusal_backoff.rs).
    arm "survive": counterfactual, the memory outlives the restart. Nothing ships this; it is
                   what the audit's "up to 6 h after" would need.
    arm "rewind":  shipped, plus (proposal) a peer that sees a node come back re-offers rows
                   admitted recently on its next Summary, instead of waiting out the re-sweep.
    """

    def __init__(self, n, T, period, scenario="1192", arm="shipped", seed=1, degree=None, down=30.0, delta=1.0,
                 kick=1.5, horizon=48 * 3600, s=None, summaries=1):
        self.rng = random.Random(SEED * 1000 + seed)
        self.n, self.T, self.P, self.scenario, self.arm = n, T, period, scenario, arm
        self.down, self.delta, self.kick, self.horizon = down, delta, kick, horizon
        self.s = s or Sched()
        self.gap = CADENCE / summaries
        self.q, self.seq, self.t = [], 0, 0.0
        self.nodes = [Node() for _ in range(n)]
        order = list(range(n))
        self.rng.shuffle(order)
        self.order = order
        for k, i in enumerate(order):
            at = T * k / max(1, n - 1)
            self.nodes[i].upgrade_at = at
            self.push(at, "restart", i)
        self.wire(n - 1 if degree is None else min(degree, n - 1))
        if scenario == "1192":
            self.push(self.nodes[order[0]].upgrade_at + down + 60, "mint", order[0])
            self.fleet_done = T + down
        else:
            self.push(T / 2, "mint", order[-1])
            self.fleet_done = T + down
        self.done_at = None

    def wire(self, degree):
        """An undirected, connected peer graph: a ring, then random chords up to `degree`."""
        adj = [set() for _ in range(self.n)]
        ring = list(range(self.n))
        self.rng.shuffle(ring)
        for a, b in zip(ring, ring[1:] + ring[:1]):
            if a != b:
                adj[a].add(b)
                adj[b].add(a)
        wanted = self.n * degree // 2
        tries = 0
        while sum(len(x) for x in adj) // 2 < wanted and tries < 50 * wanted:
            tries += 1
            a, b = self.rng.randrange(self.n), self.rng.randrange(self.n)
            if a != b and len(adj[a]) < degree and len(adj[b]) < degree:
                adj[a].add(b)
                adj[b].add(a)
        for i in range(self.n):
            self.nodes[i].peers = sorted(adj[i])

    def push(self, t, what, *a):
        self.seq += 1
        heapq.heappush(self.q, (t, self.seq, what, a))

    def admits(self, i):
        up = self.nodes[i].upgraded
        return up if self.scenario == "1192" else not up

    def become_holder(self, i, t):
        node = self.nodes[i]
        node.holds, node.admitted_at, node.entry = True, t, None
        node.gen += 1
        for j in node.peers:
            if not self.nodes[j].holds:
                # The propagation kick: the row is past this peer's high water, on the next Summary.
                self.push(t + self.rng.uniform(0.5, 2 * self.kick), "offer", i, j, node.gen, False)
                self.push(t + self.rng.uniform(0, self.P), "offer", i, j, node.gen, True)

    def run(self):
        while self.q:
            t, _, what, a = heapq.heappop(self.q)
            if t > self.horizon:
                break
            self.t = t
            if what == "restart":
                self.on_restart(*a)
            elif what == "back":
                self.on_back(*a)
            elif what == "mint":
                self.become_holder(a[0], t)
            elif what == "offer":
                self.on_offer(t, *a)
            elif what == "apply":
                self.on_apply(t, *a)
            if self.scenario == "1192" and all(x.holds for x in self.nodes):
                self.done_at = t
                break
        return self

    def on_restart(self, i):
        node = self.nodes[i]
        node.up = False
        node.gen += 1                    # its sweep cursors die with the process
        if self.arm != "survive":
            node.entry = None
        self.push(self.t + self.down, "back", i)

    def on_back(self, i):
        t = self.t
        node = self.nodes[i]
        node.up, node.upgraded = True, True
        if node.holds:
            # A cold walk of the plane: the row is near its tail, so about one full pass.
            walk = self.P if self.P > self.gap else 0.0
            for j in node.peers:
                if not self.nodes[j].holds:
                    self.push(t + self.rng.uniform(0, self.gap) + walk, "offer", i, j, node.gen, True)
        if self.arm == "rewind":
            for k in range(self.n):
                peer = self.nodes[k]
                if peer.holds and peer.up and i in peer.peers:
                    self.push(t + self.rng.uniform(0, self.gap), "offer", k, i, peer.gen, False)

    def on_offer(self, t, i, j, gen, periodic):
        node, peer = self.nodes[i], self.nodes[j]
        if gen != node.gen:
            return
        if periodic and not (self.scenario == "1192" and peer.holds):
            self.push(t + self.P, "offer", i, j, gen, True)
        if not node.up or not peer.up or peer.holds:
            return
        if peer.entry is not None and t < peer.entry.retry_at:
            return
        peer.asks += 1
        self.push(t + self.delta, "apply", j)

    def on_apply(self, t, j):
        peer = self.nodes[j]
        if peer.holds or not peer.up:
            return
        if self.admits(j):
            self.become_holder(j, t)
            return
        peer.entry, _ = record(peer.entry, TRANSIENT, t, self.s)
        peer.refusals += 1
        peer.terminal = peer.entry.disposition == TERMINAL


def upgrade_stats(n, T, period, arm="shipped", seeds=24, degree=None, **kw):
    sits, lags, terminal = [], [], []
    for sd in range(seeds):
        u = Upgrade(n, T, period, arm=arm, seed=sd, degree=degree, **kw).run()
        if u.done_at is None:
            sits.append(float("inf"))
            continue
        sits.append(max(0.0, u.done_at - u.fleet_done))
        lags.append(max(x.admitted_at - x.upgrade_at for x in u.nodes))
        terminal.append(sum(1 for x in u.nodes if x.refusals >= 8))
    return statistics.mean(sits), pct(sits, 0.95), max(lags) if lags else None, statistics.mean(terminal) if terminal else 0


# --------------------------------------------------------------------------
# Sections
# --------------------------------------------------------------------------
def section_a():
    h1("A. The schedule as the code computes it, one row, no cadence")
    s = Sched()
    e, t, rows = None, 0, []
    for n in range(1, 15):
        e, w = record(e, TRANSIENT, t, s)
        rows.append([n, e.disposition, e.cap_hits, f"{w}s", fmt(t), fmt(t + w)])
        t += w
    table(["refusal", "disposition", "cap_hits", "window", "booked at", "next ask no sooner than"], rows)
    print("[read] the audit's 20, 40, 80, 160, 300, 300, 300 and terminal at the 8th refusal are right; the 8th is "
          "booked 1200 s after the 1st.")
    print("reaching a 6 h window takes the 12th refusal; on this idealised clock it is booked at "
          f"{fmt(1200 + 1800 + 3600 + 7200 + 14400)}. A row is never 'up to 6 h' away inside its first 7.8 h.")
    h2("the same row booked Terminal from its first refusal (a class that says so), for contrast")
    e, t, rows = None, 0, []
    for n in range(1, 7):
        e, w = record(e, TERMINAL, t, s)
        rows.append([n, f"{w}s", fmt(t)])
        t += w
    table(["refusal", "window", "booked at"], rows)


def section_b():
    h1("B. Cadence: the time the row really takes to reach the terminal schedule")
    h2("B.1 every Summary names the row (plane within one page): one peer, ticks on a fixed 30 s grid, no jitter")
    rows = []
    for gap, label in ((30, "one initiator"), (15, "both sides, opposite phase")):
        for delta in (0.05, 1, 5):
            s, t, e, log = Sched(), 0.0, None, []
            tick = 0.0
            while True:
                if e is None or tick >= e.retry_at:
                    e, w = record(e, TRANSIENT, tick + delta, s)
                    log.append(tick + delta)
                    if e.disposition == TERMINAL:
                        break
                tick += gap
            rows.append([label, delta, fmt(log[-1] - log[0]), " ".join(f"{b - a:.0f}" for a, b in zip(log, log[1:]))])
    table(["summaries", "ask to apply (s)", "8th refusal after 1st", "gaps between refusals (s)"], rows)
    print("[read] the tick is tokio::time::interval(cadence) with MissedTickBehavior::Skip; the only jitter in "
          "replication is the no-route backoff. No window is jittered, so rows refused together re-ask together.")

    h2("B.2 past a page, the row is named once per re-sweep: 8th refusal after the 1st, median of 400 draws")
    rows = []
    rng = random.Random(SEED)
    for name, corpus in CORPUS.items():
        for summ in (1, 2):
            p = sweep_period(corpus, summ)
            cells = [name, summ, fmt(p), "WARN" if p > RESWEEP_WARN else "-"]
            for holders in (1, 3, 8):
                ts = []
                for _ in range(400):
                    log = ladder(p, holders, rng)
                    ts.append(log[-1][1])
                cells.append(fmt(statistics.median(ts)))
            rows.append(cells)
    table(["plane", "Summaries per 30 s", "re-sweep period", ">15 min bound", "1 holder", "3 holders", "8 holders"], rows)
    print("the audit's 'about 20 minutes' is the floor. A count of 8 refusals needs 8 offers; on the corpus the code "
          "cites and one holder that is hours. Terminal is a count, so a big plane reaches it slowly and the "
          "transient windows barely bind.")


def section_c():
    h1("C. Rolling upgrade, #1192 shape: an OLD node refuses, an upgraded node admits, every refuser restarts")
    print("N nodes restart evenly over T, 30 s down each [assumption]. Row minted 60 s after the first node is back. "
          "'sit' is time from the last node back to the last node holding the row: mean, p95 over 24 runs. Full mesh at 9 and 30; degree 8 at 130 [assumption].")
    rows = []
    for n, degree in ((9, None), (30, None), (130, 8)):
        for name, corpus in CORPUS.items():
            for summ in (1, 2):
                if summ == 2 and name != "52k rows":
                    continue
                p = sweep_period(corpus, summ)
                for T_m in (5, 20, 60, 180, 360):
                    shipped = upgrade_stats(n, T_m * 60, p, degree=degree, summaries=summ)
                    survive = upgrade_stats(n, T_m * 60, p, arm="survive", degree=degree, summaries=summ)
                    rewind = upgrade_stats(n, T_m * 60, p, arm="rewind", degree=degree, summaries=summ)
                    rows.append([n, name, summ, fmt(p), T_m, fmt(shipped[0]), fmt(shipped[1]), fmt(shipped[2]),
                                 f"{shipped[3]:.1f}", fmt(survive[0]), fmt(survive[1]), fmt(rewind[0]), fmt(rewind[1])])
    table(["N", "plane", "Summ/30s", "P", "T (min)", "sit mean", "sit p95", "worst node lag", "nodes >=8 refusals",
           "survive mean", "survive p95", "rewind mean", "rewind p95"], rows)
    print("reading: 'shipped' sits on the re-sweep period, not on any refusal window. 'survive' is what the memory "
          "would cost if a restart did not empty it. 'rewind' is the lever that is left. 'worst node lag' at degree 8 is "
          "percolation, not backoff: an old node refuses the row, so it cannot carry it, and an upgraded node with only "
          "old neighbours waits for one of them to upgrade.")


def section_d():
    h1("D. #1200 shape: the refuser is the UPGRADED node, and the row never converges")
    print("CHANGELOG 61.0.3 [read]: 'A node on 61.0.3 refuses such a removal arriving from an older node, so the two "
          "can hold different rosters until the room acts under its protocol.' Minted on an old node at T/2; 24 h run.")
    rows = []
    for n, corpus_name in ((9, "<=1 page"), (30, "<=1 page"), (30, "52k rows")):
        p = sweep_period(CORPUS[corpus_name], 1)
        for T_m in (5, 20, 60, 180):
            held, asks, refs, records, raw = [], [], [], [], []
            for sd in range(8):
                u = Upgrade(n, T_m * 60, p, scenario="1200", seed=sd, horizon=24 * 3600, degree=None).run()
                held.append(sum(1 for x in u.nodes if x.holds) / n)
                non = [x for x in u.nodes if not x.holds]
                # CC 4.4.3.2.3: one record per refused row id, a re-ask emits none. Persist emits none today.
                records.append(sum(1 for x in u.nodes if x.refusals > 0))
                raw.append(sum(x.refusals for x in u.nodes))
                if non:
                    asks.append(statistics.mean(x.asks for x in non))
                    refs.append(statistics.mean(1 if x.terminal else 0 for x in non))
            rows.append([n, corpus_name, T_m, f"{100 * statistics.mean(held):.0f}%", f"{100 * pct(held, 0):.0f}-{100 * pct(held, 1):.0f}%",
                         f"{statistics.mean(asks):.1f}" if asks else "-", f"{100 * statistics.mean(refs):.0f}%" if refs else "-", 0, f"{statistics.mean(records):.1f}",
                         f"{statistics.mean(raw):.0f}"])
    table(["N", "plane", "T (min)", "nodes holding the removal, mean", "range", "asks per refuser in 24 h",
           "refusers on terminal", "records today", "records as CC requires", "if each refusal emitted"], rows)
    print("the fork is the share of the fleet still old when the row is minted, here half: the propagation kick spreads a "
          "new row among old nodes in seconds, so T does not move it. No reset, cap or count changes the outcome; the "
          "schedule only sets the price, about 15 asks in the first day per refuser and then 4 a day. Formal: every "
          "removal that LANDS meets the protocol (MB.quorum); a held moderator's removal landed under a door that has "
          "since closed, and Membership has no versions, so this state is outside what it checks.")


def section_e():
    h1("E. The case the memory really delays: a refuser that does not restart, a dependency that lands later")
    print("[read] a RetryAfterStanding refusal (roster_consensus_insufficient) is 'dependency-less': it is not "
          "indexed, so nothing releases it. It waits out its window. G = how long the row was refused before what it "
          "needed landed, drawn from [G, 1.5 G]. Delay = landing to admission, 2000 draws.")
    rng = random.Random(SEED + 5)
    for name, corpus, holders in (("plane within a page, 1 holder", 1000, 1), ("52k rows, 3 holders", 52_125, 3)):
        p = sweep_period(corpus, 1)
        h2(f"{name}, re-sweep {fmt(p)}")
        rows = []
        for g_m in (1, 5, 20, 30, 60, 120, 240, 480, 720, 1440):
            ds = []
            for _ in range(2000):
                ds.append(delay_after_landing(g_m * 60 * rng.uniform(1, 1.5), p, holders, rng))
            rows.append([g_m, fmt(statistics.mean(ds)), fmt(pct(ds, 0.95)), fmt(max(ds))])
        table(["G (min)", "mean delay", "p95", "max"], rows)
    print("the audit's 6 h is real here, and it needs the row refused for 7.8 h first: inside an upgrade only one spread "
          "past that, and only on a refuser that restarted before the row arrived.")
    h2("the release does not fix this past a page")
    print("[read] release_and_kick forgets the rows and runs one round toward the peer that offered them. The round's "
          "Summary is that peer's head plus one backfill page; a row behind its watermark is not on it unless the "
          "re-sweep is passing. So #776's 'asked again at once' holds on a plane within a page, and past one the "
          "released row still waits the re-sweep. [inf] a Fetch of the released hash to the waiting_from peer closes it.")


def delay_after_landing(g, period, holders, rng):
    s = Sched()
    offers = sorted(rng.uniform(0, period) for _ in range(holders))
    e, t_first = None, None
    k = 0
    # Walk the merged offers; refuse before landing, admit the first ask after it.
    while True:
        t = offers[k % holders] + period * (k // holders)
        k += 1
        if e is not None and t < e.retry_at:
            continue
        if t_first is None:
            t_first = t
        if t - t_first >= g:
            return t - (t_first + g)
        e, _ = record(e, TRANSIENT, t, s)


def section_f():
    h1("F. The watermark map at a canonical's width")
    print("[read] SweepCursors: MAX_TRACKED_SWEEP_CURSORS 512, LRU; a miss builds a fresh watermark, whose sweep starts "
          "at the BEGINNING of the plane with caught_up false. The comment sizes it at 40 peers x 13 planes. "
          "A cursor must survive one cycle per page to walk a plane; one eviction restarts it.")
    rng = random.Random(SEED + 6)
    rows = []
    for planes in (8, 14):
        for peers in (30, 60, 64, 70, 100, 130, 300):
            keys = peers * planes
            q = lru_survival(keys, CURSORS, rng)
            pages = math.ceil(52_125 / PAGE)
            reach = q ** pages if q > 0 else 0.0
            rows.append([peers, planes, keys, f"{q:.3f}", f"{reach:.2e}"])
    table(["peers", "planes", "keys", "P(cursor survives a cycle)", "P(a walk of 52k rows finishes unbroken)"], rows)
    print("below the cap nothing happens. Above it LRU over a near-cyclic pattern keeps almost nothing: a thrashing "
          "peer is offered the plane's first page every round and rows past it never, the #531 bug the watermark "
          "exists to end. [inf] whether a production canonical is over the line depends on how many of peers x planes "
          "sweep each cycle; 'peers x 13 <= 512' is the claim to check.")


def lru_survival(keys, cap, rng, cycles=30):
    """Touch `keys` keys once a cycle in shuffled order under an LRU of `cap`."""
    from collections import OrderedDict
    lru: OrderedDict[int, None] = OrderedDict()
    hits = total = 0
    order = list(range(keys))
    for c in range(cycles):
        rng.shuffle(order)
        for k in order:
            if k in lru:
                lru.move_to_end(k)
                hits += c >= 5
            else:
                if len(lru) >= cap:
                    lru.popitem(last=False)
                lru[k] = None
            total += c >= 5
    return hits / total


def checks():
    h1("Sanity: a known case must match, a moved parameter must move the outcome the right way")
    fails = []

    def check(name, ok, detail=""):
        print(f"{'ok  ' if ok else 'FAIL'} {name} {detail}")
        if not ok:
            fails.append(name)

    # Analytic cases.
    s = Sched()
    e, t, windows = None, 0, []
    for _ in range(13):
        e, w = record(e, TRANSIENT, t, s)
        windows.append(w)
        t += w
    check("windows match the unit witness in refusal_backoff.rs", windows[:8] == [20, 40, 80, 160, 300, 300, 300, 1800])
    check("terminal doubles to the cap", windows[7:13] == [1800, 3600, 7200, 14400, 21600, 21600])
    check("cumulative at the 8th refusal is the 1200 s the doc comment states", sum(windows[:7]) == 1200)
    check("sweep period reproduces the doc's ~51 rounds ~25 min at 52k", sweep_period(52_000, 1) == 51 * 30,
          f"{sweep_period(52_000, 1)}s")
    gaps = []
    e, tick, last = None, 0.0, None
    while e is None or e.disposition != TERMINAL:
        if e is None or tick >= e.retry_at:
            e, _ = record(e, TRANSIENT, tick + 1, s)
            gaps.append(tick)
        tick += 30
    check("quantised on a 30 s grid: 30+60+90+180+330x3 = 1350 s", gaps[-1] - gaps[0] == 1350, f"{gaps[-1] - gaps[0]}s")
    # Sim against an analytic: last node back, N-1 holders on independent phases, E[wait] = P/N.
    P = 600.0
    for n in (4, 9):
        waits = []
        for sd in range(300):
            u = Upgrade(n, 40 * P, P, seed=sd, down=0.001, kick=1e-3, delta=1e-3).run()
            waits.append(u.done_at - u.nodes[u.order[-1]].upgrade_at)
        got, want = statistics.mean(waits), P / n
        check(f"sim vs analytic, last node's wait P/N, N={n}", abs(got - want) < 0.15 * want, f"sim {got:.0f}s, P/N {want:.0f}s")
    q = lru_survival(600, 512, random.Random(1), cycles=12)
    check("LRU over a strict superset of its cap in shuffled order survives far below the cap's share", q < 512 / 600,
          f"{q:.3f}")
    check("LRU under its cap never misses after warm-up", lru_survival(500, 512, random.Random(1), cycles=8) == 1.0)

    # The formal model's removal rule against the door the sim's scenario rests on.
    def formal_met(n, signers, target, rule):
        """Membership.tla ProtocolMet, Protocol = "unanimous", kind = "remove"; UnanimousRemoval = rule."""
        voters = set(range(n)) - {target}
        return bool(voters) and voters <= signers and (rule != "others_majority" or 2 * len(voters) > n)

    def persist_met(n, signers, target):
        """persist v61.0.2 consensus.rs evaluate, Direction::Remove under UNANIMOUS (#1192)."""
        voices = len(signers - {target})
        return voices == n - 1 and 2 * voices > n

    same = all(formal_met(n, {i for i in range(n) if m >> i & 1}, 0, "others_majority")
               == persist_met(n, {i for i in range(n) if m >> i & 1}, 0)
               for n in range(2, 9) for m in range(1 << n))
    check("Membership.tla others_majority = persist #1192, every signer set to n = 8", same)
    check("the formal twin 'others' removes at two members, the rule refuses it (MB.coerced, unanimous_two)",
          formal_met(2, {1}, 0, "others") and not formal_met(2, {1}, 0, "others_majority"))

    # Mutations.
    def nth(sched):
        return len(ladder(30.0, 1, random.Random(3), s=sched))

    check("mutation: cap hits 3 -> 2 moves terminal to the 7th refusal", nth(Sched(hits=2)) == 7, str(nth(Sched(hits=2))))
    check("mutation: cap hits 3 -> 5 moves terminal to the 10th", nth(Sched(hits=5)) == 10, str(nth(Sched(hits=5))))
    check("mutation: TRANSIENT_CAP 300 -> 160 reaches the cap a refusal sooner", nth(Sched(cap=160)) == 7, str(nth(Sched(cap=160))))
    # A larger base reaches the cap a doubling earlier, so terminal comes a refusal SOONER, not later:
    # the count runs off the cap, not off the time spent.
    check("mutation: TRANSIENT_BASE doubled reaches the cap sooner, terminal at the 7th", nth(Sched(base=40)) == 7,
          str(nth(Sched(base=40))))
    a = upgrade_stats(9, 3600, sweep_period(14_616, 1), seeds=30)[0]
    b = upgrade_stats(9, 3600, sweep_period(52_125, 1), seeds=30)[0]
    check("a longer re-sweep lengthens the sit", b > a, f"{fmt(a)} -> {fmt(b)}")
    c = upgrade_stats(9, 7200, sweep_period(1000, 1), arm="survive", seeds=30)[0]
    d = upgrade_stats(9, 7200, sweep_period(1000, 1), seeds=30)[0]
    check("a memory that survives the restart sits longer than one that does not", c > d, f"{fmt(d)} -> {fmt(c)}")
    e1 = upgrade_stats(9, 3600, sweep_period(52_125, 1), arm="rewind", seeds=30)[0]
    check("the rewind shortens the sit", e1 < b, f"{fmt(b)} -> {fmt(e1)}")
    return fails


def main():
    print(f"M8 retry schedule under rolling upgrade (seed {SEED})")
    bad = verify_constants()
    section_a()
    section_b()
    section_c()
    section_d()
    section_e()
    section_f()
    fails = checks()
    if bad or fails:
        print("FAILED:", bad + fails)
        sys.exit(1)
    print("\nall checks passed")


if __name__ == "__main__":
    main()
