#!/usr/bin/env python3
"""M1: the seal's event path under flood and restart storm.

Run with ``python3 -I tools/models/event_path.py``. Standard library only; no network,
no cargo, no files written. Seeded. Exit status 1 if a sanity check fails or a constant
no longer matches the code. Read by ``FSD/EVENT_PATH_MODEL.md`` section 2.

The path, [read] on the #947 lane (src/transport/link_keying.rs, reticulum.rs):
  frame event (one thread) -> identity_has_standing -> per sender -> node-wide
  -> keyer.submit (bounded queue, standing drained first) -> c workers -> event loop applies.
A link that is refused is closed; the dialler re-dials on its next send.

Service time is not measured here. CIRISVerify has no bench of transit_kex::respond, and
this model does not invent one: the figures are a cited bracket, and every table sweeps far
past it so the answer reads as a breakpoint in s, the time of one decapsulation.
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

# Constants [read] /home/emoore/CIRISEdge-947 at 6c87599.
WORKERS_MAX = 4              # link_keying.rs DECAP_WORKERS_MAX
Q_STANDING = 64              # link_keying.rs DECAP_QUEUE_STANDING
Q_STRANGER = 32              # link_keying.rs DECAP_QUEUE_STRANGER
R_STRANGER = 256             # link_keying.rs HANDSHAKES_STRANGER_NODE, per window
R_STANDING = 2048            # link_keying.rs HANDSHAKES_STANDING_NODE, per window
S_STRANGER = 16              # link_keying.rs HANDSHAKES_PER_STRANGER
S_STANDING = 64              # link_keying.rs HANDSHAKES_PER_STANDING
S_UNIDENTIFIED = 16          # link_keying.rs HANDSHAKES_UNIDENTIFIED
WINDOW = 10.0                # route_fetch.rs ROUTE_REQUEST_WINDOW; SLIDING, not fixed
ROUTE_NODE = 32              # route_fetch.rs ROUTE_REQUESTS_PER_WINDOW
ROUTE_SENDER = 4             # route_fetch.rs ROUTE_REQUESTS_PER_SENDER
TRACKED = 1024               # route_fetch.rs ROUTE_SENDERS_TRACKED
KEYING_BUDGET = 10.0         # av_transit_handshake.rs HANDSHAKE_BUDGET via link_seal.rs KEYING_BUDGET
MAX_HS_BYTES = 8192          # av_transit_handshake.rs MAX_HANDSHAKE_BYTES
INBOUND_IDLE = 120.0         # reticulum.rs DEFAULT_LINK_POOL_IDLE_BOUND = DEFAULT_INBOUND_LINK_IDLE_BOUND
ENVELOPE = 1024              # leviculum-std driver/completions.rs ESTABLISHED_MIRROR_CAP (an alarm since leviculum#56)
IDENTIFY_GRACE = 1.0         # link_seal.rs IDENTIFY_GRACE
DEFERRED_MAX = 128           # link_seal.rs DEFERRED_HANDSHAKES_MAX
ANNOUNCE = 300.0             # reticulum.rs ReticulumTransportConfig::announce_interval default
CADENCE = 30.0               # scheduler.rs DEFAULT_CADENCE

K947 = "/home/emoore/CIRISEdge-947/src/transport"
CITES = [
    ("DECAP_WORKERS_MAX", WORKERS_MAX, f"{K947}/link_keying.rs", r"const DECAP_WORKERS_MAX: usize = (\d+)"),
    ("DECAP_QUEUE_STANDING", Q_STANDING, f"{K947}/link_keying.rs", r"const DECAP_QUEUE_STANDING: usize = (\d+)"),
    ("DECAP_QUEUE_STRANGER", Q_STRANGER, f"{K947}/link_keying.rs", r"const DECAP_QUEUE_STRANGER: usize = (\d+)"),
    ("HANDSHAKES_STRANGER_NODE", R_STRANGER, f"{K947}/link_keying.rs", r"const HANDSHAKES_STRANGER_NODE: u32 = (\d+)"),
    ("HANDSHAKES_STANDING_NODE", R_STANDING, f"{K947}/link_keying.rs", r"const HANDSHAKES_STANDING_NODE: u32 = (\d+)"),
    ("HANDSHAKES_PER_STRANGER", S_STRANGER, f"{K947}/link_keying.rs", r"const HANDSHAKES_PER_STRANGER: usize = (\d+)"),
    ("HANDSHAKES_PER_STANDING", S_STANDING, f"{K947}/link_keying.rs", r"const HANDSHAKES_PER_STANDING: usize = (\d+)"),
    ("HANDSHAKES_UNIDENTIFIED", S_UNIDENTIFIED, f"{K947}/link_keying.rs", r"const HANDSHAKES_UNIDENTIFIED: usize = (\d+)"),
    ("ROUTE_REQUEST_WINDOW", int(WINDOW), f"{K947}/route_fetch.rs", r"const ROUTE_REQUEST_WINDOW: Duration = Duration::from_secs\((\d+)\)"),
    ("ROUTE_REQUESTS_PER_WINDOW", ROUTE_NODE, f"{K947}/route_fetch.rs", r"const ROUTE_REQUESTS_PER_WINDOW: u32 = (\d+)"),
    ("ROUTE_REQUESTS_PER_SENDER", ROUTE_SENDER, f"{K947}/route_fetch.rs", r"const ROUTE_REQUESTS_PER_SENDER: usize = (\d+)"),
    ("ROUTE_SENDERS_TRACKED", TRACKED, f"{K947}/route_fetch.rs", r"const ROUTE_SENDERS_TRACKED: usize = (\d+)"),
    ("IDENTIFY_GRACE", int(IDENTIFY_GRACE), f"{K947}/link_seal.rs", r"const IDENTIFY_GRACE: Duration = Duration::from_secs\((\d+)\)"),
    ("DEFERRED_HANDSHAKES_MAX", DEFERRED_MAX, f"{K947}/link_seal.rs", r"const DEFERRED_HANDSHAKES_MAX: usize = (\d+)"),
    ("HANDSHAKE_BUDGET", int(KEYING_BUDGET), f"{K947}/av_transit_handshake.rs", r"const HANDSHAKE_BUDGET: Duration = Duration::from_secs\((\d+)\)"),
    ("MAX_HANDSHAKE_BYTES (KiB)", MAX_HS_BYTES // 1024, f"{K947}/av_transit_handshake.rs", r"const MAX_HANDSHAKE_BYTES: usize = (\d+) \* 1024"),
]

# The bracket for s. kem768 decaps median cycles, fips203ipd v0.6, pablotron.org 2024-05-15 [cited]:
# i7-1185G7 AVX-512 38,184, scalar clang 148,425; Cortex-A76 Neon 121,529, scalar clang 162,514;
# Cortex-A73 Neon 201,900, scalar gcc 444,600. No clock is printed there. This is another
# implementation: edge's is RustCrypto ml-kem 0.3 + x25519-dalek (ciris-crypto Cargo.toml).
CYCLES_LOW, CYCLES_HIGH = 38_184, 444_600
S_FLOOR = CYCLES_LOW / 4e9       # 10 us KEM only [model, assumed 4 GHz]
S_CEIL = CYCLES_HIGH / 2e9       # 222 us KEM only [model, assumed 2 GHz]
S_NOM = 250e-6                   # [model] the bracket's top with room for X25519 and HKDF, uncosted
SWEEP_S = (100e-6, 250e-6, 750e-6, 2e-3, 5e-3, 20e-3)


# formal/transport_tiers/Tiers.lean at CIRISConstitution 6d9e1da, not re-derived:
# routedAsksPerSecond seats = seats * bound * Class.server.realBytes / askBytes, with bound 8,
# server budget 7000, realBytes budget/2, askBytes 8192 ("not pinned anywhere yet").
TIERS = "/home/emoore/CIRISConstitution/formal/transport_tiers/Tiers.lean"
ROUTED_9 = 30                # theorem routed_nine_canonicals
ROUTED_3 = 10                # theorem routed_three_canonicals


def verify_constants():
    bad, seen = [], 0
    for name, want, path, rx in CITES:
        if not os.path.exists(path):
            continue
        m = re.search(rx, open(path, encoding="utf-8").read())
        seen += 1
        if not m or int(m.group(1)) != want:
            bad.append(f"{name}: model {want}, code {m.group(1) if m else 'absent'}")
    if os.path.exists(TIERS):
        text = open(TIERS, encoding="utf-8").read()
        for rx in (rf"routedAsksPerSecond 9 = {ROUTED_9} ", rf"routedAsksPerSecond 3 = {ROUTED_3} "):
            if not re.search(rx, text):
                bad.append(f"Tiers.lean no longer proves {rx}")
    print(f"constants checked against the #947 lane: {seen} of {len(CITES)}; mismatches: {len(bad)}")
    return bad


def workers(cores):
    """Keyer::new: (cores / 2).clamp(1, DECAP_WORKERS_MAX)."""
    return max(1, min(cores // 2, WORKERS_MAX))


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


def ms(x):
    if x is None:
        return "-"
    if x < 1:
        return f"{x * 1000:.1f}ms"
    return f"{x:.1f}s"


def pct(xs, p):
    if not xs:
        return None
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))]


# --------------------------------------------------------------------------
# Limiters: ports of route_fetch.rs
# --------------------------------------------------------------------------
class NodeLimiter:
    """RouteRequestLimiter: a sliding window of ADMITTED requests."""

    def __init__(self, cap, window=WINDOW):
        self.cap, self.window, self.recent = cap, window, deque()

    def admit(self, now):
        r = self.recent
        while r and now - r[0] >= self.window:
            r.popleft()
        if len(r) >= self.cap:
            return False
        r.append(now)
        return True


class PacedLimiter:
    """Proposal, not shipped: a token bucket at the same mean rate, a tenth of the window as burst."""

    def __init__(self, cap, window=WINDOW, burst_share=0.1):
        self.rate, self.burst = cap / window, max(1.0, cap * burst_share)
        self.tokens, self.last = self.burst, 0.0

    def admit(self, now):
        self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens < 1:
            return False
        self.tokens -= 1
        return True


class SenderLimiter:
    """SenderRouteLimiter, including the tracked-senders bound."""

    def __init__(self, per, unident, window=WINDOW):
        self.per, self.unident, self.window, self.map = per, unident, window, {}

    def admit(self, sender, now):
        key = sender if sender is not None else "\0"
        cap = self.per if sender is not None else self.unident
        m = self.map
        if key not in m and len(m) >= TRACKED:
            for k in [k for k, q in m.items() if not (q and now - q[-1] < self.window)]:
                del m[k]
            if len(m) >= TRACKED:
                return True
        q = m.setdefault(key, deque())
        while q and now - q[0] >= self.window:
            q.popleft()
        if len(q) >= cap:
            return False
        q.append(now)
        return True


# --------------------------------------------------------------------------
# The discrete-event model of one receiver
# --------------------------------------------------------------------------
class Hs:
    __slots__ = ("sender", "standing", "cb", "born", "at_queue")

    def __init__(self, sender, standing, cb=None, born=0.0):
        self.sender, self.standing, self.cb, self.born, self.at_queue = sender, standing, cb, born, 0.0


class Receiver:
    def __init__(self, c, service, rng=None, q_stand=Q_STANDING, q_str=Q_STRANGER, r_stand=R_STANDING, r_str=R_STRANGER,
                 h=0.0, limits=True, budget=KEYING_BUDGET):
        self.c, self.service, self.rng, self.budget = c, service, rng, budget
        self.q_stand, self.q_str, self.h, self.limits = q_stand, q_str, h, limits
        self.node_st, self.node_str = NodeLimiter(r_stand), NodeLimiter(r_str)
        self.send_st, self.send_str = SenderLimiter(S_STANDING, S_UNIDENTIFIED), SenderLimiter(S_STRANGER, S_UNIDENTIFIED)
        self.st, self.str = deque(), deque()
        self.running = 0
        self.ev, self.seq, self.now = [], 0, 0.0
        self.loop_free = 0.0
        self.count = {}
        self.max_q = 0
        self.waits = {True: [], False: []}
        self.busy = 0.0

    def at(self, t, fn, *a):
        self.seq += 1
        heapq.heappush(self.ev, (t, self.seq, fn, a))

    def bump(self, k):
        self.count[k] = self.count.get(k, 0) + 1

    def arrive(self, hs, t):
        """The frame reaches the one thread of control, FIFO, at h per event."""
        self.at(t, self._loop, hs)

    def _loop(self, hs):
        start = max(self.now, self.loop_free)
        self.loop_free = start + self.h
        self.at(self.loop_free, self._admit, hs)

    def _admit(self, hs):
        now = self.now
        send, node = (self.send_st, self.node_st) if hs.standing else (self.send_str, self.node_str)
        if self.limits:
            if not send.admit(hs.sender, now):
                self._refuse(hs, "sender_rate")
                return
            if not node.admit(now):
                self._refuse(hs, "node_rate")
                return
        q, bound = (self.st, self.q_stand) if hs.standing else (self.str, self.q_str)
        if len(q) >= bound:
            self._refuse(hs, "saturated")
            return
        hs.at_queue = now
        q.append(hs)
        self.max_q = max(self.max_q, len(self.st) + len(self.str))
        if self.running < self.c:
            self.running += 1
            self._next()

    def _refuse(self, hs, why):
        self.bump(why + (":standing" if hs.standing else ":stranger"))
        if hs.cb:
            hs.cb(False, self.now, why)

    def _next(self):
        while True:
            q = self.st if self.st else self.str
            if not q:
                self.running -= 1
                return
            hs = q.popleft()
            if self.now - hs.at_queue >= self.budget:
                self._refuse(hs, "budget")          # Ok(None): skipped unstarted
                continue
            self.waits[hs.standing].append(self.now - hs.at_queue)
            s = self.service(self.rng) if callable(self.service) else self.service
            self.busy += s
            self.at(self.now + s, self._done, hs)
            return

    def _done(self, hs):
        self.bump("keyed:standing" if hs.standing else "keyed:stranger")
        if hs.cb:
            hs.cb(True, self.now, "keyed")
        self._next()

    def run(self, until=None):
        while self.ev:
            t, _, fn, a = heapq.heappop(self.ev)
            if until is not None and t > until:
                break
            self.now = t
            fn(*a)
        return self


# --------------------------------------------------------------------------
# Analytic results
# --------------------------------------------------------------------------
def mmck_block(lam, mu, c, k):
    """Erlang loss with waiting room: M/M/c/K, K = c + queue. P(arrival refused)."""
    a = lam / mu
    terms = []
    p = 1.0
    terms.append(p)
    for n in range(1, k + 1):
        p *= a / min(n, c)
        terms.append(p)
    return terms[k] / sum(terms)


def mdsk_block(lam, s, q):
    """M/D/1 with q waiting places, exact, by the embedded chain at departures. P(refused)."""
    a = [math.exp(-lam * s) * (lam * s) ** n / math.factorial(n) for n in range(0, q + 3)]
    K = q + 1                                       # system capacity
    n = K                                           # departure states 0..K-1
    P = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            base = max(i, 1) - 1
            if j < n - 1:
                d = j - base
                P[i][j] = a[d] if 0 <= d < len(a) else 0.0
        P[i][n - 1] = max(0.0, 1 - sum(P[i][: n - 1]))
    pi = [1.0 / n] * n
    for _ in range(4000):
        pi = [sum(pi[i] * P[i][j] for i in range(n)) for j in range(n)]
    p0 = pi[0]
    rho = lam * s
    return 1 - 1 / (p0 + rho)


def burst_fluid(n, spread, c, s, q):
    """n arrivals evenly over `spread`. Refused count on the fluid path."""
    mu = c / s
    a = n / spread if spread > 0 else float("inf")
    if a <= mu:
        return 0.0
    fill = q / (a - mu)
    if spread <= fill:
        return 0.0
    return n - (q + mu * spread) - (0 if spread > 0 else 0)


def cobham(lam1, lam2, s):
    """Non-preemptive priority, one server, deterministic service, mean queue waits."""
    r = (lam1 + lam2) * s * s / 2
    rho1, rho2 = lam1 * s, lam2 * s
    return r / (1 - rho1), r / ((1 - rho1) * (1 - rho1 - rho2))


# --------------------------------------------------------------------------
# The cases
# --------------------------------------------------------------------------
def storm(k, links, spread, s, c, seed, arm="shipped", h=50e-6, q_stand=Q_STANDING, q_str=Q_STRANGER, r_str=R_STRANGER,
          redial="tick", until=900.0, paced=False):
    """K peers, each re-keying `links` links, after a canonical restart.

    arm "shipped":  [read] identity_has_standing reads the live `peers` map, which a restart
                    empties; PersistedBindingResolver answers send, never this. So a peer is a
                    stranger until its binding is rooted again: [inf] its link-borne announce, once a
                    link keys (+1 s), or its periodic announce, U(0, 300 s).
    arm "hydrated": proposal: the receiver order reads the persisted bindings at boot; all standing.
    arm "standing": what link_keying.rs's comment assumes; the same as hydrated.
    """
    rng = random.Random(SEED + seed)
    rx = Receiver(c, s, q_stand=q_stand, q_str=q_str, r_str=r_str, h=h)
    if paced:
        rx.node_str = PacedLimiter(r_str)
    rooted = [(0.0 if arm != "shipped" else rng.uniform(0, ANNOUNCE)) for _ in range(k)]
    left = [links] * k
    done_at = []
    refused_first = [0]
    attempts = [0]

    def send(peer, t, first):
        attempts[0] += 1
        st = t >= rooted[peer]

        def cb(ok, now, why, peer=peer, first=first):
            if ok:
                left[peer] -= 1
                rooted[peer] = min(rooted[peer], now + 1.0)
                if left[peer] == 0:
                    done_at.append(now)
            else:
                refused_first[0] += first
                wait = CADENCE + rng.uniform(-1, 1) if redial == "tick" else rng.uniform(0.5, CADENCE)
                rx.at(now + wait, lambda p=peer, w=now + wait: send(p, w, False))

        rx.arrive(Hs(f"p{peer}", st, cb, t), t)

    for p in range(k):
        for _ in range(links):
            t = rng.uniform(0, spread) if spread > 0 else 0.0
            rx.at(t, lambda p=p, t=t: send(p, t, True))
    rx.run(until)
    return rx, done_at, refused_first[0] / (k * links), attempts[0]


def storm_row(k, links, spread, s, c, arm, seeds=6, **kw):
    frs, t100, t50, wst, att, maxq = [], [], [], [], [], []
    labels = {}
    for sd in range(seeds):
        rx, done, fr, a = storm(k, links, spread, s, c, sd, arm=arm, **kw)
        frs.append(fr)
        att.append(a)
        maxq.append(rx.max_q)
        t100.append(max(done) if len(done) == k else float("inf"))
        t50.append(pct(done, 0.5) or float("inf"))
        for kk, v in rx.count.items():
            labels[kk] = labels.get(kk, 0) + v / seeds
    ref = {kk.split(":")[0]: 0 for kk in labels}
    for kk, v in labels.items():
        ref[kk.split(":")[0]] += v
    return (statistics.mean(frs), statistics.mean(t50), statistics.mean(t100), statistics.mean(att) / (k * links),
            max(maxq), ref)


def flood(rate, honest=40, kind="sybil", dur=400.0, s=S_NOM, c=1, seed=1, r_str=R_STRANGER, h=20e-6, standing_rate=2.0,
          q_str=Q_STRANGER, q_stand=Q_STANDING, paced=False, retry="tick"):
    """A flood at `rate` handshakes/s, `honest` strangers dialling over the run, standing peers keying.
    kind: sybil = a fresh identity per handshake; single = one identity; unident = never identifies.
    Each honest stranger dials at a uniform time in [20, 50] s, once the window is full, and on
    refusal again one cadence later, for as long as the flood lasts: [inf] a refused link re-dials
    on its next send."""
    rng = random.Random(SEED * 7 + seed)
    rx = Receiver(c, s, q_str=q_str, q_stand=q_stand, r_str=r_str, h=h)
    if paced:
        rx.node_str = PacedLimiter(r_str)
    tries, first, standing_lat = [0], {}, []
    hon_ok, hon_ref = [0], [0]
    t = 0.0
    i = 0
    while t < dur:
        t += rng.expovariate(rate)
        i += 1
        sender = {"sybil": f"s{i}", "single": "s", "unident": None}[kind]
        rx.arrive(Hs(sender, False), t)

    def dial(hid, t0, tt):
        tries[0] += 1

        def cb(ok, now, why):
            if ok:
                hon_ok[0] += 1
                first[hid] = now - t0
            else:
                hon_ref[0] += 1
                next_t = now + CADENCE
                if next_t < dur:
                    next_t = now + (CADENCE + rng.uniform(-1, 1) if retry == "tick" else rng.uniform(15, 45))
                    rx.at(next_t, lambda: dial(hid, t0, next_t))

        rx.arrive(Hs(f"h{hid}", False, cb, tt), tt)

    for j in range(honest):
        t0 = rng.uniform(20, 50)
        rx.at(t0, lambda j=j, t0=t0: dial(j, t0, t0))
    t = 0.0
    while t < dur:
        t += rng.expovariate(standing_rate)

        def cb(ok, now, why, b=t):
            if ok:
                standing_lat.append(now - b)

        rx.arrive(Hs(f"k{int(rng.random() * 200)}", True, cb, t), t)
    rx.run(dur + 60)
    return rx, tries[0], hon_ok[0], hon_ref[0], first, standing_lat


# --------------------------------------------------------------------------
# Sections
# --------------------------------------------------------------------------
def section_a():
    h1("A. The bound: what the keyer can do against what admission lets through")
    print(f"[read] the rates are per {WINDOW:.0f} s, sliding: stranger {R_STRANGER} = {R_STRANGER / WINDOW}/s, standing "
          f"{R_STANDING} = {R_STANDING / WINDOW}/s. The audit's '256/2048' reads as per-window; there is no per-second rate.")
    print(f"[cited] kem768 decaps {CYCLES_LOW:,}-{CYCLES_HIGH:,} cycles on three CPUs in another implementation; "
          f"{S_FLOOR * 1e6:.0f}-{S_CEIL * 1e6:.0f} us at assumed 4 and 2 GHz, KEM alone. [model] s = {S_NOM * 1e6:.0f} us nominal. "
          "[read] respond() is one X25519 dh, one ML-KEM decapsulate, one HKDF, no signature; nothing in the tree benches it.")
    rows = []
    for cores in (1, 2, 4, 8, 16, 32):
        c = workers(cores)
        row = [cores, c]
        for s in SWEEP_S:
            row.append(f"{c / s:,.0f}/s {100 * (R_STRANGER + R_STANDING) / WINDOW * s / c:.0f}%")
        rows.append(row)
    table(["cores", "c"] + [f"s={x * 1e3:g}ms" for x in SWEEP_S], rows)
    print("each cell: keyer capacity, then its utilisation with BOTH budgets full (230.4/s).")
    print("breakpoints, c = 1 (a 2 vCPU canonical): "
          f"strangers alone reach capacity at s = {1000 * WINDOW / R_STRANGER:.1f} ms; both budgets at "
          f"s = {1000 * WINDOW / (R_STRANGER + R_STANDING):.2f} ms; both full queues outlast KEYING_BUDGET at "
          f"s = {1000 * KEYING_BUDGET / (Q_STANDING + Q_STRANGER):.0f} ms.")
    print("so DECAP_WORKERS_MAX never binds on the cited bracket: c = 1 covers both budgets with 100x to spare. "
          f"c = 4 is reached at 8 cores and matters only past s = {1000 * 4 * WINDOW / (R_STRANGER + R_STANDING):.0f} ms.")
    print(f"link table [read]: a keyed stranger holds a link for at least INBOUND_IDLE {INBOUND_IDLE:.0f} s, so the stranger "
          f"rate alone stands up {R_STRANGER / WINDOW * INBOUND_IDLE:,.0f} idle links against leviculum's {ENVELOPE} envelope "
          f"(reached in {ENVELOPE / (R_STRANGER / WINDOW):.0f} s). Since leviculum#56 that envelope is an ERROR, not an evictor.")


def section_a2():
    h2("A.2 what honest first contact can demand: Tiers.lean's routed-ask ceiling against the stranger budget")
    print(f"formal: routed_nine_canonicals {ROUTED_9} asks/s mesh-wide, routed_three_canonicals {ROUTED_3}; one canonical's share "
          f"{ROUTED_9 / 9:.1f}/s. Those are the shaped links' real-frame capacity at an assumed 8 KiB ask, so a canonical cannot "
          "be handed more first contacts through its slots than that.")
    rows = []
    for r in (32, 64, 128, 256):
        rows.append([r, f"{r / WINDOW:.1f}/s", f"{(r / WINDOW) / (ROUTED_9 / 9):.1f}x", f"{r / WINDOW * INBOUND_IDLE:,.0f}",
                     f"{100 * r / WINDOW * INBOUND_IDLE / ENVELOPE:.0f}%"])
    table(["stranger budget", "rate", "over a canonical's routed share", "idle links held", "of the 1024 envelope"], rows)


def section_b():
    h1("B. Restart storm: a 2 vCPU canonical (c = 1), K peers re-keying")
    print("h = 50 us of event-path work per handshake [assumption, unmeasured]. Refused links re-dial on their next tick, "
          "one cadence later [inf]. 'spread' is the window the peers' dials land in. Six seeds. 'first pass' = refused the "
          "first try. T50/T100 = all of a peer's links keyed.")
    h2("B.1 who is standing after a restart decides everything: shipped vs what link_keying.rs's comment assumes")
    rows = []
    for k, links in ((130, 1), (130, 4), (500, 1), (500, 4), (1000, 1), (2000, 1), (2000, 4)):
        for spread in (1.0, 5.0, 30.0):
            for arm in ("shipped", "hydrated"):
                fr, t50, t100, att, mq, ref = storm_row(k, links, spread, S_NOM, 1, arm)
                rows.append([k, links, spread, arm, f"{100 * fr:.0f}%", f"{t50:.1f}s", f"{t100:.1f}s", f"{att:.2f}", mq,
                             f"{ref.get('node_rate', 0):.0f}", f"{ref.get('saturated', 0):.0f}"])
    table(["K", "links", "spread", "arm", "first pass refused", "T50", "T100", "dials/link", "max queue", "node_rate", "saturated"], rows)
    h2("B.2 spread 0: everything lands as fast as the event loop hands it over, the fluid burst")
    print("the queue fills unless the event loop is slower than the keyer: a job waits only while h < s/c. "
          "This is the case that decides the queue size.")
    rows = []
    for h in (20e-6, 50e-6, 200e-6, 500e-6):
        for s in (100e-6, 250e-6, 750e-6, 2e-3):
            for q_str in (Q_STRANGER, 256):
                fr, t50, t100, att, mq, ref = storm_row(130, 1, 0.0, s, 1, "shipped", h=h, q_str=q_str, seeds=3)
                rows.append([f"{h * 1e6:.0f}us", f"{s * 1e6:.0f}us", q_str, f"{100 * fr:.0f}%", f"{t100:.1f}s", mq])
    table(["h", "s", "Q stranger", "first pass refused", "T100", "max queue"], rows)
    h2("B.3 queue sizes under a wide storm, spread 0, s nominal, h 50 us, hydrated (standing) and shipped (stranger)")
    rows = []
    for k in (130, 500, 2000):
        for q in (64, 256, 1024, 2048):
            fr, t50, t100, att, mq, ref = storm_row(k, 1, 0.0, S_NOM, 1, "hydrated", q_stand=q, seeds=3)
            rows.append([k, "hydrated", q, f"{100 * fr:.0f}%", f"{t100:.1f}s", mq, ms(q * S_NOM)])
    for k in (130, 500, 2000):
        for q in (32, 64, 128, 256):
            fr, t50, t100, att, mq, ref = storm_row(k, 1, 0.0, S_NOM, 1, "shipped", q_str=q, seeds=3)
            rows.append([k, "shipped", q, f"{100 * fr:.0f}%", f"{t100:.1f}s", mq, ms(q * S_NOM)])
    table(["K", "arm", "queue", "first pass refused", "T100", "max queue", "worst wait"], rows)
    h2("B.4 slower keys: the same storm as s moves (spread 5 s, K = 500, 1 link)")
    rows = []
    for s in SWEEP_S:
        for arm in ("shipped", "hydrated"):
            fr, t50, t100, att, mq, ref = storm_row(500, 1, 5.0, s, 1, arm, seeds=3)
            rows.append([f"{s * 1e3:g}ms", arm, f"{100 * fr:.0f}%", f"{t100:.1f}s", mq, f"{ref.get('saturated', 0):.0f}"])
    table(["s", "arm", "first pass refused", "T100", "max queue", "saturated"], rows)


def section_c():
    h1("C. Stranger flood with honest strangers in it (c = 1, s nominal)")
    print("Flood runs 400 s from t = 0; 40 honest strangers dial between 20 and 50 s, refused ones again a cadence later. "
          "Standing peers key at 2/s throughout.")
    rows = []
    for kind in ("sybil", "single", "unident"):
        for rate in (5, 26, 100, 500, 2000):
            rx, tries, ok, ref, first, st = flood(rate, kind=kind, dur=400.0 if rate < 500 else 200.0)
            p = ok / tries if tries else 0
            fc = sorted(first.values())
            within = [sum(1 for x in fc if x <= w) / 40 for w in (1, 60, 300)]
            sref = sum(v for k, v in rx.count.items() if k.endswith(":standing") and not k.startswith("keyed"))
            rows.append([kind, rate, f"{r_of(kind, rate):.3f}", f"{p:.3f}", f"{100 * within[0]:.0f}%", f"{100 * within[1]:.0f}%",
                         f"{100 * within[2]:.0f}%", ms(pct(st, 0.99)), sref, rx.count.get("saturated:stranger", 0)])
    table(["flood", "rate/s", "analytic p", "honest p per dial", "first contact <1 s", "<60 s", "<300 s", "standing p99", "standing refused", "saturated"], rows)
    print("analytic p = 25.6/rate past the budget, the long-run share of a dial at a random moment. The honest column falls "
          "under it because of C.5. A Sybil flood is the one that takes honest slots; a "
          "single identity spends only its own 16, and an unidentified flood its own shared 16. Standing peers do "
          "not notice any of them.")
    print(f"[read] 6c87599: a handshake that beats its identify waits, {IDENTIFY_GRACE:.0f} s and {DEFERRED_MAX} at most. An "
          f"unidentified flood holds that set full from {DEFERRED_MAX / IDENTIFY_GRACE:.0f}/s; past it a raced handshake "
          "is judged at once into the shared 16, so the race the grace closes reopens under exactly that flood.")
    h2("C.2 the stranger who holds no route row meets the route-fetch limiter first: 32 per 10 s, 3.2/s")
    print("[read] route_fetch.rs: a dialler with no authenticated pair sends CTKR, then the handshake. "
          "Against a Sybil flood of both frames, per dial the chance of each stage, and first contact in dials.")
    rows = []
    for rate in (5, 26, 100, 500, 2000):
        pr = min(1.0, (ROUTE_NODE / WINDOW) / rate)
        ph = min(1.0, (R_STRANGER / WINDOW) / rate)
        e = 1 / pr + 1 / ph
        rows.append([rate, f"{pr:.3f}", f"{ph:.3f}", f"{e:.1f}", f"{e * CADENCE:.0f}s", f"{1 / ph * CADENCE:.0f}s"])
    table(["flood rate/s", "p route", "p handshake", "expected dials", "time, no row", "time, holds row"], rows)
    h2("C.3 what moves the honest share: the stranger budget against the link it buys")
    rows = []
    for r in (64, 128, 256, 512, 1024):
        cells = [r, f"{r / WINDOW:.1f}/s", f"{r / WINDOW * INBOUND_IDLE:,.0f}", f"{ENVELOPE / (r / WINDOW):.0f}s"]
        for rate in (100, 500, 2000):
            rx, tries, ok, ref, first, st = flood(rate, r_str=r, dur=150.0)
            cells.append(f"{ok / tries:.3f}")
        rows.append(cells)
    table(["stranger budget", "rate", "keyed links held at the idle bound", "to the 1024 envelope", "honest p @100/s", "@500/s", "@2000/s"], rows)
    print("a flood is bounded by the budget at every line, and held links follow the budget exactly. The long-run honest "
          "share does too; these per-dial figures are noisy and low because the dials are phase-locked, C.5.")
    h2("C.5 the honest dial is phase-locked: the window keeps its burst, and the cadence is a multiple of the window")
    print("[read] the limiter is a sliding log of admits, so a flood's first 256 fill the window at once and the slots "
          "reopen in the same burst 10 s later, forever: at 100/s it is open 2.6 s in every 10, at 2000/s 0.13 s. "
          "[read] a dial follows a 30 s tick with no jitter, and 30 is a multiple of 10: a stranger refused in the closed "
          "part comes back to the closed part. Independent dials would give 1-(1-p)^n. Below: 40 honest strangers, "
          "dials over 400 s of flood (200 s at 2000/s).")
    rows = []
    for rate in (100, 500, 2000):
        p = (R_STRANGER / WINDOW) / rate
        n = 12
        for label, kw in (("shipped, retry on the tick +-1 s", {}), ("retry jittered 15-45 s", {"retry": "jitter"}),
                          ("paced limiter, tick retry", {"paced": True}), ("paced and jittered", {"paced": True, "retry": "jitter"})):
            rx, tries, ok, ref, first, st = flood(rate, dur=400.0 if rate < 2000 else 200.0, **kw)
            fc = sorted(first.values())
            rows.append([rate, label, f"{p:.3f}", f"{1 - (1 - p) ** 10:.2f}", f"{ok / tries:.3f}",
                         f"{100 * sum(1 for x in fc if x <= 300) / 40:.0f}%"])
    table(["flood/s", "arm", "long-run p", "independent, 10 dials", "p per dial", "first contact <300 s"], rows)
    h2("the same pacing on a storm: it spends the burst a restart wants, so standing comes first")
    rows = []
    for k in (130, 500):
        for arm in ("shipped", "hydrated"):
            for paced in (False, True):
                fr, t50, t100, att, mq, ref = storm_row(k, 1, 1.0, S_NOM, 1, arm, seeds=3, paced=paced)
                rows.append([k, arm, "paced" if paced else "sliding", f"{100 * fr:.0f}%", f"{t100:.1f}s"])
    table(["K", "arm", "stranger limiter", "first pass refused", "T100"], rows)
    h2("C.4 the budget is spent before the queue is asked")
    print("[read] admit_handshake: admit_handshake(...).and_then(keyer.submit): a job refused DecapSaturated has already "
          "spent its sender and node slots, so a burst the queue cannot hold burns the window's budget for nothing.")
    rows = []
    for q in (32, 256):
        rx = Receiver(1, S_NOM, q_str=q, h=20e-6)
        for i in range(256):
            rx.arrive(Hs(f"s{i}", False), 0.0)
        rx.run()
        rows.append([q, rx.count.get("keyed:stranger", 0), rx.count.get("saturated:stranger", 0), rx.max_q])
    table(["Q stranger", "keyed", "refused saturated (slot spent)", "max queue"], rows)


def r_of(kind, rate):
    if kind == "sybil":
        return min(1.0, (R_STRANGER / WINDOW) / rate)
    return 1.0


def checks():
    h1("Sanity: analytic cases against the sim, and moved parameters")
    fails = []

    def check(name, ok, detail=""):
        print(f"{'ok  ' if ok else 'FAIL'} {name} {detail}")
        if not ok:
            fails.append(name)

    def poisson_block(lam, service, c, q, n=120_000, seed=1):
        rng = random.Random(seed)
        # budget off: with service at 1 s the stale-job skip frees queue places, which is the code's
        # behaviour and not the textbook queue's.
        rx = Receiver(c, service, rng=rng, q_str=q, limits=False, budget=float("inf"))
        t = 0.0
        for i in range(n):
            t += rng.expovariate(lam)
            rx.arrive(Hs(None, False), t)
        rx.run()
        return rx.count.get("saturated:stranger", 0) / n

    for lam, mu, c, q in ((0.9, 1.0, 1, 4), (1.5, 1.0, 1, 8), (3.0, 1.0, 4, 8), (4.5, 1.0, 4, 32)):
        sim = poisson_block(lam, lambda r, mu=mu: r.expovariate(mu), c, q)
        ana = mmck_block(lam, mu, c, c + q)
        check(f"M/M/{c}/{c + q} blocking, rho {lam / (c * mu):.2f}", abs(sim - ana) < max(0.004, 0.08 * ana),
              f"sim {sim:.4f} analytic {ana:.4f}")
    for lam, q in ((0.8, 4), (1.2, 8), (2.0, 8)):
        sim = poisson_block(lam, 1.0, 1, q)
        ana = mdsk_block(lam, 1.0, q)
        check(f"M/D/1/{q + 1} blocking, rho {lam:.1f}", abs(sim - ana) < max(0.004, 0.08 * ana), f"sim {sim:.4f} analytic {ana:.4f}")
    # Priority: Cobham, big queues so nothing blocks.
    rng = random.Random(3)
    rx = Receiver(1, 1.0, q_stand=10**7, q_str=10**7, limits=False, budget=float("inf"))
    t = 0.0
    for i in range(200_000):
        t += rng.expovariate(0.8)
        rx.arrive(Hs(None, rng.random() < 0.5), t)
    rx.run()
    w1, w2 = cobham(0.4, 0.4, 1.0)
    s1, s2 = statistics.mean(rx.waits[True]), statistics.mean(rx.waits[False])
    check("Cobham, standing first", abs(s1 - w1) < 0.1 * w1, f"sim {s1:.3f} analytic {w1:.3f}")
    check("Cobham, strangers behind", abs(s2 - w2) < 0.1 * w2, f"sim {s2:.3f} analytic {w2:.3f}")
    # Sliding limiter under Poisson overload admits r/lambda.
    rng = random.Random(4)
    lim = NodeLimiter(R_STRANGER)
    t, ok, n = 0.0, 0, 0
    while t < 2000:
        t += rng.expovariate(500)
        passed = lim.admit(t)
        if t > 100:
            n += 1
            ok += passed
    got = ok / n
    want = (R_STRANGER / WINDOW) / 500
    check("a sliding window under overload admits r/lambda", abs(got - want) < 0.05 * want, f"sim {got:.4f} analytic {want:.4f}")
    # Fluid burst.
    for n_, spread, s, q in ((2000, 0.5, 1e-3, 64), (1000, 0.2, 2e-3, 32)):
        rx = Receiver(1, s, q_str=q, limits=False)
        for i in range(n_):
            rx.arrive(Hs(None, False), spread * i / n_)
        rx.run()
        sim = rx.count.get("saturated:stranger", 0)
        ana = burst_fluid(n_, spread, 1, s, q)
        check(f"fluid burst n={n_}", abs(sim - ana) < 0.05 * max(ana, 1), f"sim {sim} fluid {ana:.0f}")
    check("workers: 2 vCPU 1, 4 vCPU 2, 8 vCPU 4, 32 cores capped 4, 1 core still 1",
          [workers(x) for x in (2, 4, 8, 32, 1)] == [1, 2, 4, 4, 1])
    # Limiter ports, the unit shape of route_fetch.rs.
    l = SenderLimiter(2, 1)
    check("sender limiter: per sender then window", l.admit("a", 0) and l.admit("a", 0) and not l.admit("a", 1) and l.admit("a", 10))
    check("sender limiter: unidentified share one slot", l.admit(None, 0) and not l.admit(None, 0))
    l2 = SenderLimiter(1, 1)
    for i in range(TRACKED):
        l2.admit(f"x{i}", 0.0)
    check("past the tracked bound an unknown sender passes to the node rate", l2.admit("new", 1.0) and l2.admit("new", 1.0))

    # Mutations.
    a = storm_row(500, 1, 0.0, S_NOM, 1, "hydrated", seeds=2)
    b = storm_row(500, 1, 0.0, S_NOM, 1, "hydrated", seeds=2, q_stand=256)
    check("mutation: a larger queue refuses less", b[0] < a[0], f"{a[0]:.2f} -> {b[0]:.2f}")
    c = storm_row(500, 1, 0.0, 5e-3, 1, "hydrated", seeds=2)
    check("mutation: a slower decap refuses more", c[0] >= a[0], f"{a[0]:.2f} -> {c[0]:.2f}")
    d = storm_row(500, 1, 0.0, 5e-3, 4, "hydrated", seeds=2)
    check("mutation: more workers refuse less at a slow decap", d[0] < c[0], f"{c[0]:.2f} -> {d[0]:.2f}")
    e = flood(500, dur=200.0)
    f = flood(500, r_str=1024, dur=200.0)
    check("mutation: a bigger stranger budget raises the honest share", f[2] / f[1] > e[2] / e[1], f"{e[2] / e[1]:.3f} -> {f[2] / f[1]:.3f}")
    g = flood(100, dur=200.0)
    l1 = flood(100, dur=300.0)
    l2 = flood(100, dur=300.0, paced=True, retry="jitter")
    check("mutation: pacing and jitter unlock the honest dial", len(l2[4]) > len(l1[4]), f"{len(l1[4])} -> {len(l2[4])} of 40")
    check("mutation: a harder flood lowers it", e[2] / e[1] < g[2] / g[1], f"{g[2] / g[1]:.3f} -> {e[2] / e[1]:.3f}")
    s1 = storm_row(2000, 1, 5.0, S_NOM, 1, "shipped", seeds=2)
    s2 = storm_row(2000, 1, 5.0, S_NOM, 1, "hydrated", seeds=2)
    check("hydrating standing shortens a wide storm", s2[2] < s1[2], f"{s1[2]:.1f}s -> {s2[2]:.1f}s")
    return fails


def main():
    print(f"M1 event path under flood and restart storm (seed {SEED})")
    bad = verify_constants()
    section_a()
    section_a2()
    section_b()
    section_c()
    fails = checks()
    if bad or fails:
        print("FAILED:", bad + fails)
        sys.exit(1)
    print("\nall checks passed")


if __name__ == "__main__":
    main()
