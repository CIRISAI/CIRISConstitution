#!/usr/bin/env python3
"""M2: the responder's reply lane under reverse-dead peers.

Run with ``python3 -I tools/models/reply_lane.py``. Standard library only; no network,
no cargo, no files written. Seeded. Exit status 1 if a sanity check fails or a constant no
longer matches the code. Read by ``FSD/EVENT_PATH_MODEL.md`` section 3.

The lane, [read] on the #943 lane (src/replication/reply_lane.rs, runtime.rs):
  inbox (try_send, 8) -> driver: a frame that wants a reply and finds no room is SHED unstepped;
  otherwise step it, enqueue the reply -> one FIFO send at a time per (peer, kind).
  A job older than the expiry at dequeue is dropped unsent. A Deliver is never shed.
"""
from __future__ import annotations

import heapq
import math
import os
import random
import re
import statistics
import sys
from collections import deque

SEED = 20261105
KiB = 1024
PAGE = 512 * KiB             # session.rs MAX_DELIVER_ENVELOPE_BYTES
JOBS = 8                     # reply_lane.rs REPLY_QUEUE_JOBS = coordinator.rs INBOUND_CHANNEL_CAPACITY
BYTES_PAGES = 4              # reply_lane.rs REPLY_QUEUE_BYTES = 4 * MAX_DELIVER_ENVELOPE_BYTES
SEND_TIMEOUT = 60.0          # reply_lane.rs RESPONDER_REPLY_SEND_TIMEOUT
ROUND_TIMEOUT = 10.0         # scheduler.rs DEFAULT_ROUND_TIMEOUT: the expiry on an unshaped link
PACING_WAIT_GAPS = 4.74      # scheduler.rs PACING_WAIT_GAPS: the expiry on a shaped link
NO_PROGRESS = 6.0            # reticulum.rs REVERSE_PATH_NO_PROGRESS_WINDOW
MAX_TRANSFER = 45.0          # reticulum.rs REVERSE_PATH_MAX_TRANSFER
CADENCE = 30.0               # scheduler.rs DEFAULT_CADENCE
INBOX = 8                    # coordinator.rs INBOUND_CHANNEL_CAPACITY
PULL_BURST = 8               # coordinator.rs MAX_PULL_EXCHANGES
PLANES_LIVE = 8              # [inf] protocol.rs ALL minus persist 61.0.3 RETIRED_FRAMED; 14 in the #740 comment

L943 = "/home/emoore/CIRISEdge-943/src"
CITES = [
    ("MAX_DELIVER_ENVELOPE_BYTES (KiB)", PAGE // KiB, f"{L943}/replication/session.rs", r"const MAX_DELIVER_ENVELOPE_BYTES: usize = (\d+) \* 1024"),
    ("REPLY_QUEUE_BYTES (pages)", BYTES_PAGES, f"{L943}/replication/reply_lane.rs", r"const REPLY_QUEUE_BYTES: usize = (\d+) \* MAX_DELIVER_ENVELOPE_BYTES"),
    ("RESPONDER_REPLY_SEND_TIMEOUT", int(SEND_TIMEOUT), f"{L943}/replication/reply_lane.rs", r"const RESPONDER_REPLY_SEND_TIMEOUT: Duration = Duration::from_secs\((\d+)\)"),
    ("INBOUND_CHANNEL_CAPACITY", JOBS, f"{L943}/replication/coordinator.rs", r"const INBOUND_CHANNEL_CAPACITY: usize = (\d+)"),
    ("MAX_PULL_EXCHANGES", PULL_BURST, f"{L943}/replication/coordinator.rs", r"const MAX_PULL_EXCHANGES: usize = (\d+)"),
    ("DEFAULT_ROUND_TIMEOUT", int(ROUND_TIMEOUT), f"{L943}/replication/scheduler.rs", r"const DEFAULT_ROUND_TIMEOUT: Duration = Duration::from_secs\((\d+)\)"),
    ("REVERSE_PATH_NO_PROGRESS_WINDOW", int(NO_PROGRESS), f"{L943}/transport/reticulum.rs", r"const REVERSE_PATH_NO_PROGRESS_WINDOW: Duration = Duration::from_secs\((\d+)\)"),
    ("REVERSE_PATH_MAX_TRANSFER", int(MAX_TRANSFER), f"{L943}/transport/reticulum.rs", r"const REVERSE_PATH_MAX_TRANSFER: Duration = Duration::from_secs\((\d+)\)"),
]


def verify_constants():
    bad, seen = [], 0
    for name, want, path, rx in CITES:
        if not os.path.exists(path):
            continue
        m = re.search(rx, open(path, encoding="utf-8").read())
        seen += 1
        if not m or int(m.group(1)) != want:
            bad.append(f"{name}: model {want}, code {m.group(1) if m else 'absent'}")
    print(f"constants checked against the #943 lane: {seen} of {len(CITES)}; mismatches: {len(bad)}")
    return bad


def table(headers, rows):
    w = [max(len(str(h)), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    print("  ".join(str(h).rjust(x) for h, x in zip(headers, w)))
    print("  ".join("-" * x for x in w))
    for r in rows:
        print("  ".join(str(c).rjust(x) for c, x in zip(r, w)))


def h1(t):
    print("\n" + "=" * 96 + f"\n{t}\n" + "=" * 96)


def h2(t):
    print("\n-- " + t)


def pct(xs, p):
    if not xs:
        return 0.0
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))]


class Lane:
    """One (peer, kind): inbox, driver, lane. `mode` "lane" is #943; "parked" sends inline, as before."""

    def __init__(self, stall_send, stall_until, healthy_send=0.1, expiry=ROUND_TIMEOUT, jobs=JOBS, byte_pages=BYTES_PAGES,
                 page=PAGE, step=0.002, mode="lane", inbox=INBOX, step_shed=1e-5):
        self.stall_send, self.stall_until, self.healthy = stall_send, stall_until, healthy_send
        self.expiry, self.jobs, self.byte_cap, self.page = expiry, jobs, byte_pages * page, page
        self.step, self.mode, self.inbox_cap, self.step_shed = step, mode, inbox, step_shed
        self.ev, self.seq, self.now = [], 0, 0.0
        self.inbox, self.q = deque(), deque()
        self.bytes = 0
        self.driver_busy = self.sender_busy = False
        self.c = {k: 0 for k in ("frames", "inbox_drop", "shed", "sent", "failed", "expired", "late", "deliver")}
        self.max_jobs = self.max_bytes = 0
        self.lag = []                # inbound arrival to step start, every frame
        self.deliver_lag = []
        self.occ_area = 0.0
        self.last_t = 0.0

    def at(self, t, fn, *a):
        self.seq += 1
        heapq.heappush(self.ev, (t, self.seq, fn, a))

    def area(self):
        n = len(self.q) + (1 if self.sender_busy else 0)
        self.occ_area += n * (self.now - self.last_t)
        self.last_t = self.now

    def frame(self, kind, t):
        """kind: "summary" (reply, no bytes), "diff" (reply, a page), "deliver" (no reply)."""
        self.at(t, self._in, kind)

    def _in(self, kind):
        self.c["frames"] += 1
        if len(self.inbox) >= self.inbox_cap:
            self.c["inbox_drop"] += 1
            return
        self.inbox.append((kind, self.now))
        if not self.driver_busy:
            self.driver_busy = True
            self._drive()

    def _drive(self):
        if not self.inbox:
            self.driver_busy = False
            return
        kind, born = self.inbox.popleft()
        self.lag.append(self.now - born)
        if kind == "deliver":
            self.c["deliver"] += 1
            self.deliver_lag.append(self.now - born)
            self.at(self.now + self.step, self._drive)
            return
        if self.mode == "lane":
            if len(self.q) >= self.jobs or self.bytes >= self.byte_cap:
                self.c["shed"] += 1
                self.at(self.now + self.step_shed, self._drive)
                return
            self.at(self.now + self.step, self._enqueue, kind)
        else:
            self.at(self.now + self.step, self._parked_send, kind)

    def _enqueue(self, kind):
        self.area()
        b = self.page if kind == "diff" else 0
        self.bytes += b
        self.q.append((self.now, b))
        self.max_jobs = max(self.max_jobs, len(self.q) + (1 if self.sender_busy else 0))
        self.max_bytes = max(self.max_bytes, self.bytes)
        self._pump()
        self._drive()

    def _send_time(self):
        return self.stall_send if self.now < self.stall_until else self.healthy

    def _pump(self):
        if self.sender_busy:
            return
        while self.q:
            self.area()
            born, b = self.q.popleft()
            if self.now - born > self.expiry:
                self.c["expired"] += 1
                self.bytes -= b
                continue
            self.sender_busy = True
            s = self._send_time()
            failed = self.now < self.stall_until
            self.at(self.now + s, self._sent, born, b, failed)
            return

    def _sent(self, born, b, failed):
        self.area()
        self.sender_busy = False
        self.bytes -= b
        self.c["failed" if failed else "sent"] += 1
        if not failed and self.now - born > self.expiry:
            self.c["late"] += 1
        self._pump()

    def _parked_send(self, kind):
        s = self._send_time()
        failed = self.now < self.stall_until
        self.c["failed" if failed else "sent"] += 1
        self.at(self.now + s, self._drive)

    def run(self, until):
        while self.ev:
            t, _, fn, a = heapq.heappop(self.ev)
            if t > until:
                break
            self.now = t
            fn(*a)
        self.area()
        return self


def traffic_honest(lane, dur, rng):
    """A reverse-dead honest peer: its Summary each cadence. [inf] It never sees our Summary, so it
    sends no Diff, and so it pins no page: a Diff answers a Summary that has to arrive."""
    t = rng.uniform(0, CADENCE)
    while t < dur:
        lane.frame("summary", t)
        t += CADENCE


def traffic_flood(lane, dur, rate, rng, share_diff=1.0, deliver_rate=0.2):
    t = 0.0
    while t < dur:
        t += rng.expovariate(rate)
        lane.frame("diff" if rng.random() < share_diff else "summary", t)
    t = 0.0
    while deliver_rate and t < dur:
        t += rng.expovariate(deliver_rate)
        lane.frame("deliver", t)


def md1k_block(lam, s, q):
    """M/D/1 with q waiting places, exact, by the embedded chain."""
    a = [math.exp(-lam * s) * (lam * s) ** n / math.factorial(n) for n in range(q + 3)]
    n = q + 1
    P = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n - 1):
            d = j - (max(i, 1) - 1)
            P[i][j] = a[d] if 0 <= d < len(a) else 0.0
        P[i][n - 1] = max(0.0, 1 - sum(P[i][: n - 1]))
    pi = [1.0 / n] * n
    for _ in range(4000):
        pi = [sum(pi[i] * P[i][j] for i in range(n)) for j in range(n)]
    return 1 - 1 / (pi[0] + lam * s)


def section_a():
    h1("A. The bound, from the code")
    print(f"[read] one lane holds {JOBS} jobs behind the one on the wire: {JOBS + 1}. Bytes are checked before a step, so a lane "
          f"can pass {BYTES_PAGES} pages by one: < {(BYTES_PAGES + 1) * PAGE / KiB / KiB:.1f} MiB. Full pages stop at {BYTES_PAGES * PAGE / KiB / KiB:.1f} MiB.")
    print(f"[read] expiry = max({ROUND_TIMEOUT:.0f} s, {PACING_WAIT_GAPS} gaps), checked only at dequeue. A send takes up to "
          f"{NO_PROGRESS:.0f} s on a dead reverse path, {MAX_TRANSFER:.0f} s on a live slow one, {SEND_TIMEOUT:.0f} s at the outer bound.")
    rows = []
    for dead in (1, 10, 40, 130, 500):
        for planes in (PLANES_LIVE, 14):
            mb = dead * planes * (BYTES_PAGES + 1) * PAGE / KiB / KiB
            rows.append([dead, planes, dead * planes, f"{mb:,.0f} MiB", f"{dead * planes * BYTES_PAGES * PAGE / KiB / KiB:,.0f} MiB"])
    table(["peers", "planes", "lanes", "byte pin, ceiling", "full pages"], rows)
    print("no node-wide bound exists: the pin is lanes x 2.5 MiB. All of it needs peers that can send Diffs and stop reading.")
    healthy = 130 * PLANES_LIVE / CADENCE * 1.0 * PAGE / KiB / KiB
    print(f"[model] for scale, a healthy canonical: 130 peers x {PLANES_LIVE} planes, one full page a cadence on each, 1 s on the "
          f"wire, holds {healthy:.0f} MiB in flight. A node-wide bound of 64 MiB is 3.7 times that.")
    h2("the expiry on shaped links: max(10 s, 4.74 gaps), 16,272 B frames")
    # Class rates are formal/transport_tiers/Tiers.lean Class.budget, the CC 5.4.3 table.
    rows = []
    for name, rate in (("server", 7000), ("home", 2800), ("phone-wifi", 1400), ("phone-cellular", 350)):
        gap = 16272 / rate
        e = max(ROUND_TIMEOUT, PACING_WAIT_GAPS * gap)
        rows.append([name, f"{gap:.1f}s", f"{e:.0f}s", f"{PAGE / rate:.0f}s"])
    table(["class", "gap", "expiry", "a 512 KiB page at the class rate"], rows)
    print("[inf] a whole page at a shaped rate outruns its own expiry: rows above 64 KiB go bulk, but a Deliver of many small "
          "rows is packed to 512 KiB, and on a shaped link that page cannot finish inside the round that asked for it.")


def section_b():
    h1("B. An honest reverse-dead peer: the lane barely notices")
    print("Each frame of that peer is a Summary a cadence; each reply fails at the stall. One lane, 2 h.")
    rows = []
    rng = random.Random(SEED)
    for s in (6.0, 15.0, 45.0, 60.0):
        lane = Lane(s, 1e9)
        traffic_honest(lane, 7200, rng)
        lane.run(7300)
        rows.append([f"{s:.0f}s", lane.max_jobs, lane.c["shed"], lane.c["expired"], f"{lane.occ_area / 7300:.2f}", lane.max_bytes])
    table(["stall per send", "max jobs", "shed", "expired", "mean occupancy", "bytes pinned"], rows)
    print("arrival 1/30 s against one send per stall: the lane fills only past a stall of 240 s, which no bound permits. "
          "[inf] an honest reverse-dead peer pins no page at all.")
    h2("a contact lookup, MAX_PULL_EXCHANGES Pulls at once, on a stalled lane: the reason REPLY_QUEUE_JOBS is 8")
    rows = []
    for jobs in (2, 4, 8, 16):
        for s in (0.1, 6.0):
            lane = Lane(s, 1e9, jobs=jobs)
            for i in range(PULL_BURST):
                lane.frame("summary", i * 1e-3)
            lane.run(120)
            rows.append([jobs, f"{s:g}s", lane.c["shed"], lane.c["expired"], lane.c["sent"] + lane.c["failed"]])
    table(["jobs", "send", "shed", "expired at dequeue", "left the lane"], rows)


def section_c():
    h1("C. A hostile or broken peer: Diffs as fast as it likes on a lane that does not drain")
    print("Poisson Diffs at rate lam, each wanting a full page, sends stalled for the whole 300 s run, Delivers at 0.2/s. "
          "'expired' jobs cost a dequeue; 'failed' cost a stall. Step 2 ms [assumption].")
    rng = random.Random(SEED + 1)
    rows = []
    for s in (6.0, 45.0, 60.0):
        for lam in (0.05, 0.2, 1.0, 5.0, 50.0):
            lane = Lane(s, 1e9)
            traffic_flood(lane, 300, lam, rng)
            lane.run(360)
            n = max(1, lane.c["frames"] - lane.c["deliver"])
            rows.append([f"{s:.0f}s", lam, f"{lane.occ_area / 360:.1f}", lane.max_jobs, f"{lane.max_bytes / KiB / KiB:.1f}MiB",
                         f"{100 * lane.c['shed'] / n:.0f}%", lane.c["expired"], lane.c["failed"], f"{lane.c['inbox_drop']}",
                         f"{pct(lane.deliver_lag, 0.99) * 1000:.0f}ms", f"{max(lane.deliver_lag or [0]) * 1000:.0f}ms"])
    table(["stall", "lam/s", "mean jobs", "max jobs", "max bytes", "shed", "expired", "failed", "inbox drop", "Deliver lag p99", "max"], rows)
    print("the rate at which such a frame costs a read is still the rate replies leave, the claim in reply_lane.rs's "
          "docs: at lam 50 and a 6 s stall almost all are shed, unstepped.")
    h2("how long a stall keeps a lane full, and how fast it clears: stall of length L, lam 1/s, 6 s per failed send")
    rows = []
    for length in (10, 30, 60, 120, 300, 600):
        lane = Lane(6.0, length)
        traffic_flood(lane, length + 60, 1.0, rng, deliver_rate=0)
        lane.run(length + 120)
        n = lane.c["frames"]
        rows.append([length, lane.max_jobs, f"{100 * lane.c['shed'] / n:.0f}%", lane.c["expired"], lane.c["failed"], lane.c["sent"]])
    table(["stall length s", "max jobs", "shed", "expired", "failed", "sent after heal"], rows)


def section_d():
    h1("D. What the lane bought: a Deliver behind a stalled plane, before and after")
    print("The peer sends a Summary a cadence, plus bursts, and a Deliver that must land. 'parked' sends inline as before #943.")
    rng = random.Random(SEED + 2)
    rows = []
    for s in (6.0, 15.0, 60.0):
        for burst in (1, 4, 8):
            cells = [f"{s:.0f}s", burst]
            for mode in ("parked", "lane"):
                lane = Lane(s, 1e9, mode=mode)
                for k in range(40):
                    base = k * CADENCE + rng.uniform(0, 1)
                    for i in range(burst):
                        lane.frame("summary", base + i * 0.01)
                    lane.frame("deliver", base + 0.5)
                lane.run(40 * CADENCE + 400)
                cells += [f"{pct(lane.deliver_lag, 0.5):.2f}s", f"{max(lane.deliver_lag or [0]):.1f}s", lane.c["inbox_drop"]]
            rows.append(cells)
    table(["stall", "burst", "parked p50", "parked max", "parked inbox drop", "lane p50", "lane max", "lane inbox drop"], rows)
    print("field, reply_lane.rs: a Key Deliver sat 79 s behind its plane's failing replies. The parked arm gets there at a "
          "15 s stall and a burst of 8; the lane holds Deliver lag at the step time.")


def section_e():
    h1("E. The knobs: expiry, job bound, byte bound")
    rng = random.Random(SEED + 3)
    h2("E.1 expiry, on a stall that heals: 120 s stall, lam 0.5/s, 6 s per failed send. A send after expiry is work nobody reads")
    rows = []
    for e in (3.0, 5.0, 10.0, 20.0, 60.0, 1e9):
        lane = Lane(6.0, 120, expiry=e)
        traffic_flood(lane, 180, 0.5, random.Random(11), deliver_rate=0)
        lane.run(300)
        rows.append([f"{e:g}s" if e < 1e8 else "none", lane.c["failed"], lane.c["expired"], lane.c["sent"], lane.c["late"], lane.c["shed"]])
    table(["expiry", "failed sends (a stall each)", "expired", "sent healthy", "of those, past the round", "shed"], rows)
    h2("E.2 job bound and byte bound against a healthy link with bursts: 1 s per page, burst of 8 Diffs each cadence")
    rows = []
    for jobs, pages in ((8, 1), (8, 2), (8, 4), (8, 8), (4, 4), (16, 8)):
        lane = Lane(0.0, 0.0, healthy_send=1.0, jobs=jobs, byte_pages=pages)
        for k in range(100):
            for i in range(8):
                lane.frame("diff", k * CADENCE + i * 0.01)
        lane.run(3200)
        rows.append([jobs, pages, f"{(jobs + 1) * 0 + pages * PAGE / KiB / KiB:.1f}MiB", f"{100 * lane.c['shed'] / lane.c['frames']:.0f}%", f"{lane.max_bytes / KiB / KiB:.1f}MiB"])
    table(["jobs", "byte pages", "byte bound", "shed of the burst", "max pinned"], rows)
    print("eight Diffs at once on one lane is not what one round sends: a round is one Diff per plane. The shed here is "
          "a re-ask next round, the same as the inbox drop it replaced.")
    h2("E.3 a healthy but slow link: one full-page Diff per plane each cadence, at link rate B")
    rows = []
    for b in (2_000, 7_000, 11_650, 20_000, 100_000, 1_000_000):
        t = PAGE / b
        over = t > MAX_TRANSFER
        send = min(t, MAX_TRANSFER)
        lane = Lane(send if over else 0.0, 1e9 if over else 0.0, healthy_send=send)
        for k in range(120):
            lane.frame("diff", k * CADENCE)
        lane.run(120 * CADENCE + 200)
        rows.append([f"{b:,}", f"{t:.0f}s", "no" if over else "yes", lane.c["sent"], lane.c["failed"], lane.c["expired"], lane.c["shed"]])
    table(["B/s", "page time", "inside 45 s cap", "sent", "failed", "expired", "shed"], rows)
    print(f"[read] below {PAGE / MAX_TRANSFER / 1000:.1f} kB/s a full page cannot finish inside REVERSE_PATH_MAX_TRANSFER: "
          "the row never leaves and the bound does not help, that is the Deliver packer's page, not the lane's.")


def checks():
    h1("Sanity: analytic cases against the sim, and moved parameters")
    fails = []

    def check(name, ok, detail=""):
        print(f"{'ok  ' if ok else 'FAIL'} {name} {detail}")
        if not ok:
            fails.append(name)

    # M/D/1/K: the lane with no expiry, no byte bound, instant driver.
    for lam, s, q in ((0.8, 1.0, 8), (1.2, 1.0, 8), (0.5, 1.0, 2)):
        rng = random.Random(5)
        lane = Lane(s, 1e12, expiry=1e12, jobs=q, byte_pages=10**6, step=0.0, step_shed=0.0, inbox=10**9)
        t, n = 0.0, 150_000
        for _ in range(n):
            t += rng.expovariate(lam)
            lane.frame("summary", t)
        lane.run(t + 1000)
        sim = lane.c["shed"] / n
        # The sim's server takes a job the moment it is stepped; capacity q waiting + 1 on the wire.
        ana = md1k_block(lam, s, q)
        check(f"M/D/1/{q + 1} shed, rho {lam * s:.1f}", abs(sim - ana) < max(0.004, 0.08 * ana), f"sim {sim:.4f} analytic {ana:.4f}")
    # Long stall, short expiry: per stall S and rate lam, 1 sent, 8 expired, the rest shed.
    lam, S = 2.0, 60.0
    lane = Lane(S, 1e12)
    for i in range(int(6000 * lam)):
        lane.frame("diff" if False else "summary", i / lam)
    lane.run(6000)
    cycles = lane.c["failed"]
    want = lam * S - 1 - JOBS
    got = lane.c["shed"] / cycles
    check("deterministic overload: shed per stall = lam S - 1 - 8", abs(got - want) < 0.05 * want, f"sim {got:.1f} analytic {want:.1f}")
    # A lane must hold exactly 9 jobs and full pages stop at 4.
    lane = Lane(1e6, 1e12)
    for i in range(40):
        lane.frame("summary", i * 0.01)
    lane.run(100)
    check("a lane holds 8 queued + 1 on the wire", lane.max_jobs == 9, str(lane.max_jobs))
    lane = Lane(1e6, 1e12)
    for i in range(40):
        lane.frame("diff", i * 0.01)
    lane.run(100)
    check("full pages stop at 4", lane.max_bytes == 4 * PAGE, f"{lane.max_bytes / PAGE:.0f}")
    lane = Lane(1e6, 1e12, page=PAGE)
    # A short page first, so the check passes at just under the bound and a full one lands on top.
    lane.page = PAGE - 1
    for i in range(4):
        lane.frame("diff", i * 0.01)
    lane.run(1)
    lane.page = PAGE
    for i in range(4):
        lane.frame("diff", 1 + i * 0.01)
    lane.run(2)
    check("a lane can pass the byte bound by one page", 4 * PAGE < lane.max_bytes < 5 * PAGE, f"{lane.max_bytes / PAGE:.2f} pages")

    def run(**kw):
        lane = Lane(6.0, 1e9, **kw)
        traffic_flood(lane, 300, 1.0, random.Random(8))
        lane.run(360)
        return lane

    base = run()
    check("mutation: a longer expiry expires fewer", run(expiry=60.0).c["expired"] < base.c["expired"] or base.c["expired"] == 0,
          f"{base.c['expired']} -> {run(expiry=60.0).c['expired']}")
    check("mutation: a larger job bound sheds fewer", run(jobs=32, byte_pages=64).c["shed"] < base.c["shed"],
          f"{base.c['shed']} -> {run(jobs=32, byte_pages=64).c['shed']}")
    check("mutation: a smaller byte bound sheds more", run(byte_pages=1).c["shed"] > base.c["shed"],
          f"{base.c['shed']} -> {run(byte_pages=1).c['shed']}")
    a, b = Lane(6.0, 1e9), Lane(60.0, 1e9)
    traffic_flood(a, 300, 1.0, random.Random(8))
    traffic_flood(b, 300, 1.0, random.Random(8))
    a.run(360)
    b.run(360)
    check("mutation: a longer stall sheds more", b.c["shed"] > a.c["shed"], f"{a.c['shed']} -> {b.c['shed']}")
    p, l = Lane(6.0, 1e9, mode="parked"), Lane(6.0, 1e9)
    for x in (p, l):
        for k in range(40):
            for i in range(4):
                x.frame("summary", k * CADENCE + i * 0.01)
            x.frame("deliver", k * CADENCE + 0.5)
        x.run(40 * CADENCE + 200)
    check("the lane holds Deliver lag under the parked loop's", max(l.deliver_lag) < max(p.deliver_lag),
          f"{max(p.deliver_lag):.1f}s -> {max(l.deliver_lag):.3f}s")
    return fails


def main():
    print(f"M2 reply lane under reverse-dead peers (seed {SEED})")
    bad = verify_constants()
    section_a()
    section_b()
    section_c()
    section_d()
    section_e()
    fails = checks()
    if bad or fails:
        print("FAILED:", bad + fails)
        sys.exit(1)
    print("\nall checks passed")


if __name__ == "__main__":
    main()
