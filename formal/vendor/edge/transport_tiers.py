#!/usr/bin/env python3
"""CIRISEdge transport tiers and canonical homing: a deterministic model.

Run with ``python3 -I tools/models/transport_tiers.py``. Standard library only;
no network, no cargo, no files written. Every random draw comes from one seeded
``random.Random``, so two runs print the same tables.

The document that reads these tables is ``FSD/TRANSPORT_TIERS_MODEL.md``. The
constants are cited there; the short form of each citation is next to the
constant below. Sections A-F follow the brief of 2026-11-04.

Rulings modelled (Eric, 2026-11-04; CIRISEdge#935; CIRISConstitution#200):
  1. a node DIVIDES its node-wide cap (eight links' worth of its class budget)
     across its shaped links; there is no minimum per-link rate;
  2. three tiers: slow shaped (the divided cap), fast shaped (the proposed
     ``seat`` class between serve seats, own budget), unshaped (bulk, live media);
  3. canonicals are peers of last resort; nodes home on k of M by rendezvous hash;
  4. onion is not pairwise (the deal assigns relays), so it adds no negotiation;
  5. (Eric, later on 2026-11-04, verbatim) "we shape with shaped peers if possible,
     otherwise refuse and offer unshaped (bulk transfers) if available": the default
     is BoundedWithFloor, L = NODE_CAP_LINKS minus the layer reserve shaped links,
     each at the full class rate; at the bound a further shaping peer's row link is
     refused (`link_shaping_home_elsewhere`) and the peer homes elsewhere; an
     unshaped bulk link is still offered. Section H models this; A, D and E are
     recomputed on it there. The floorless divide of ruling 1 stays as the
     sensitivity arm.
"""
from __future__ import annotations

import hashlib
import math
import random
import statistics
from bisect import bisect_right

# --------------------------------------------------------------------------
# Constants (cited in FSD/TRANSPORT_TIERS_MODEL.md section 1)
# --------------------------------------------------------------------------
FRAME_B = 16_272            # shaped frame = the link MDU on loopback/TCP (measured; #805 item 8)
LINK_RATE_B_S = 7_000       # server class per-link budget (link_shaping.rs BudgetClass::Server)
NODE_CAP_LINKS = 8          # link_shaping.rs NODE_CAP_LINKS; CC 5.4.3 "eight links' worth"
NODE_CAP_B_S = LINK_RATE_B_S * NODE_CAP_LINKS   # 56,000 B/s
RHO = 0.5                   # CC 5.4.3 fleet default
WINDOW_S = 600              # CC 5.4.3 fleet default for server
MONTH_S = 2_592_000         # 30 days (docs/LINK_SHAPING_COST.md)
GB = 1e9
CLASS_B_S = {"server": 7_000, "home": 2_800, "phone-wifi": 1_400, "phone-cellular": 350}

ROUND_INTERVAL_S = 30       # replication round interval (brief: from the code)
WAIT_TIMEOUT_S = 15         # per-wait timeout inside a round (brief: from the code)
ROUND_MSGS = 4              # Summary -> Summary -> Diff -> Deliver, 2 per direction
BOOTSTRAP_PLANES = 5        # runtime.rs BOOTSTRAP_ROUND_PLANES (Key, IdentityOccurrence,
                            # TransportDestination, Revocation, IdentityOccurrenceRevocation)
SHAPED_ROW_MAX_B = 64 * 1024            # link_shaping.rs SHAPED_ROW_MAX_BYTES
FRAME_PAYLOAD_B = FRAME_B - 8 - 16      # [inf] 8 B frame header + 16 B AEAD tag
DELIVER_64K_FRAMES = math.ceil(SHAPED_ROW_MAX_B / FRAME_PAYLOAD_B)   # 5

VULTR_QUOTA_GB = 4_096      # canonical host egress quota per month (brief)
TODAY_EGRESS_GB = 215       # canonical host egress today (brief)
SLOW_CAP_GB = NODE_CAP_B_S * MONTH_S / GB   # 145.2 GB each way at the cap

LAYER_RESERVE_LINKS = 4   # link_shaping.rs DEFAULT_LAYER_RESERVE_LINKS (held out while the Anonymous Tier runs)
SEED = 20261104
RNG = random.Random(SEED)

# --------------------------------------------------------------------------
# Small maths
# --------------------------------------------------------------------------
def erlang_cdf(k: int, lam: float, t: float) -> float:
    """P(sum of k Exp(lam) <= t)."""
    if t <= 0:
        return 0.0
    x = lam * t
    s = 0.0
    term = 1.0
    for i in range(k):
        if i:
            term *= x / i
        s += term
    return min(1.0, max(0.0, 1.0 - math.exp(-x) * s))


def erlang_quantile(k: int, lam: float, p: float) -> float:
    lo, hi = 0.0, 1.0
    while erlang_cdf(k, lam, hi) < p:
        hi *= 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if erlang_cdf(k, lam, mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def pct(xs: list[float], p: float) -> float:
    xs = sorted(xs)
    i = min(len(xs) - 1, max(0, int(round(p * (len(xs) - 1)))))
    return xs[i]


def table(headers: list[str], rows: list[list], widths: list[int] | None = None) -> None:
    widths = widths or [max(len(str(h)), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    print("  ".join(str(h).rjust(w) for h, w in zip(headers, widths)))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(str(c).rjust(w) for c, w in zip(r, widths)))


def fmt_s(x: float) -> str:
    if x < 100:
        return f"{x:.1f}s"
    if x < 3600:
        return f"{x / 60:.1f}m"
    if x < 2 * 86400:
        return f"{x / 3600:.1f}h"
    return f"{x / 86400:.0f}d"


def h1(t: str) -> None:
    print("\n" + "=" * 96)
    print(t)
    print("=" * 96)


def h2(t: str) -> None:
    print("\n-- " + t)


# --------------------------------------------------------------------------
# Shared slow-shaped primitives
# --------------------------------------------------------------------------
def share(n_peers: float, cap: float = NODE_CAP_B_S) -> float:
    """Per-link byte rate under the divided cap, no floor (ruling 1)."""
    return cap / n_peers


def lam_of(n_peers: float) -> float:
    return share(n_peers) / FRAME_B      # frames per second per link


def gap_of(n_peers: float) -> float:
    return FRAME_B * n_peers / NODE_CAP_B_S  # seconds between frames on one link


def budget_frames(lam: float) -> int:
    """CC 5.4.3 real-frame budget per window: ceil(rho * lam * W)."""
    return max(1, math.ceil(RHO * lam * WINDOW_S))


# --------------------------------------------------------------------------
# A. Slow shaped, one server
# --------------------------------------------------------------------------
def section_a() -> None:
    h1("A. Slow shaped, one server: the divided cap across N shaped peers (no floor)")
    print(f"frame {FRAME_B} B, node cap {NODE_CAP_B_S} B/s = {NODE_CAP_LINKS} x {LINK_RATE_B_S} B/s, "
          f"rho {RHO}, W {WINDOW_S} s; one message per frame today, {BOOTSTRAP_PLANES} bootstrap planes")
    print("per-link rate = cap / N; gap = F / rate; a row that arrives at random waits Exp(lam): "
          "mean = gap, p95 = gap*ln 20, p99 = gap*ln 100; worst case unbounded")

    h2("A.1 rate, gap, row wait, real budget per link")
    rows = []
    for n in (8, 34, 100, 300, 1000):
        r = share(n)
        lam = lam_of(n)
        g = gap_of(n)
        rows.append([n, f"{r:,.0f}", f"{lam:.4f}", fmt_s(g), fmt_s(g), fmt_s(g * math.log(20)),
                     fmt_s(g * math.log(100)), f"{RHO * r:,.0f}", budget_frames(lam),
                     f"{RHO * r * 86400 / 1e6:.2f}"])
    table(["N", "B/s link", "frames/s", "gap", "mean wait", "p95", "p99", "real B/s", "frames/W", "real MB/day"], rows)

    h2("A.2 does a round complete? request+reply = 2 waits (Erlang-2) against the 15 s per-wait timeout; "
       "whole round = 4 waits coalesced, or 4 x 5 planes one-per-frame (Erlang-20) against the 30 s interval")
    rows = []
    for n in (8, 34, 100, 300, 1000):
        lam = lam_of(n)
        p_wait = erlang_cdf(2, lam, WAIT_TIMEOUT_S)
        p_wait_departure = erlang_cdf(1, lam, WAIT_TIMEOUT_S)
        p_wait_last = erlang_cdf(2 * BOOTSTRAP_PLANES, lam, WAIT_TIMEOUT_S)
        p_round_co = erlang_cdf(ROUND_MSGS, lam, ROUND_INTERVAL_S)
        p_round_1pf = erlang_cdf(ROUND_MSGS * BOOTSTRAP_PLANES, lam, ROUND_INTERVAL_S)
        both_waits = p_wait ** 2

        def verdict(pw: float, pr: float) -> str:
            if pw >= 0.95 and pr >= 0.95:
                return "viable"
            return "marginal" if pw >= 0.5 else "NOT viable"

        rows.append([n, f"{100 * p_wait:.1f}%", f"{100 * p_wait_departure:.1f}%", f"{100 * p_wait_last:.1f}%",
                     f"{100 * both_waits:.1f}%", f"{100 * p_round_co:.1f}%", f"{100 * p_round_1pf:.2f}%",
                     verdict(both_waits, p_round_co), verdict(p_wait_last ** 2, p_round_1pf)])
    table(["N", "P(wait<=15s)", "..timer at departure", "..last of 5 planes 1/frame", "P(both waits)",
           "P(round<=30s) coalesced", "P(round<=30s) 1/frame", "verdict coalesced", "verdict 1/frame"], rows)

    h2("A.3 the rho budget: real frames a window admits vs what 30 s rounds ask (per direction)")
    print("one-per-frame: 2 messages x 5 planes = 10 frames per round; coalesced: 2 frames per round "
          "(a 64 KiB Deliver adds 5 fragment frames either way)")
    rows = []
    for n in (8, 34, 100, 300, 1000):
        lam = lam_of(n)
        b = budget_frames(lam)
        asked = WINDOW_S / ROUND_INTERVAL_S
        rows.append([n, b, f"{asked:.0f}", f"{b / (2 * BOOTSTRAP_PLANES):.1f}", f"{b / 2:.1f}",
                     fmt_s(WINDOW_S / max(b / (2 * BOOTSTRAP_PLANES), 1e-9)), fmt_s(WINDOW_S / max(b / 2, 1e-9)),
                     fmt_s(DELIVER_64K_FRAMES * gap_of(n))])
    table(["N", "frames/W", "rounds asked/W", "rounds/W 1/frame", "rounds/W coalesced",
           "min interval 1/frame", "min interval coalesced", "64 KiB Deliver (5 ticks)"], rows)

    h2("A.4 max shaped peers per server for a mean row wait target (mean wait = one gap = F*N/cap)")
    rows = []
    for target in (5, 30, 300):
        n_max = math.floor(target * NODE_CAP_B_S / FRAME_B)
        lam = lam_of(n_max)
        rows.append([fmt_s(target), n_max, f"{share(n_max):,.0f}", budget_frames(lam),
                     f"{RHO * share(n_max):,.0f}"])
    table(["mean wait target", "max N", "B/s link at max N", "frames/W", "real B/s"], rows)
    print("coalescing does not move these: a row still waits for the next tick. It removes the queueing "
          "term (q rows ahead cost q more ticks one-per-frame, ~0 coalesced while they fit a frame)")

    h2("A.5 what timeout and interval make rounds viable (95th percentile), and the rho-bound interval")
    rows = []
    for n in (8, 34, 100, 300, 1000):
        lam = lam_of(n)
        t95 = erlang_quantile(2, lam, 0.95)
        i95 = erlang_quantile(ROUND_MSGS, lam, 0.95)
        i95_1pf = erlang_quantile(ROUND_MSGS * BOOTSTRAP_PLANES, lam, 0.95)
        rho_int_co = 2 / (RHO * lam)
        rho_int_1pf = 2 * BOOTSTRAP_PLANES / (RHO * lam)
        rows.append([n, fmt_s(t95), fmt_s(i95), fmt_s(i95_1pf), fmt_s(rho_int_co), fmt_s(rho_int_1pf),
                     fmt_s(max(i95, rho_int_co)), fmt_s(max(i95_1pf, rho_int_1pf))])
    table(["N", "per-wait timeout", "interval p95 coalesced", "interval p95 1/frame",
           "rho-bound interval coalesced", "rho-bound 1/frame", "=> interval coalesced", "=> interval 1/frame"], rows)
    n_t = WAIT_TIMEOUT_S / (erlang_quantile(2, 1.0, 0.95) * FRAME_B / NODE_CAP_B_S)
    n_i = ROUND_INTERVAL_S / (erlang_quantile(ROUND_MSGS, 1.0, 0.95) * FRAME_B / NODE_CAP_B_S)
    print(f"fixed 15 s / 30 s constants hold at the 95th percentile only up to N = {math.floor(n_t)} (timeout) "
          f"and N = {math.floor(n_i)} (interval). Scaling rule: timeout = {erlang_quantile(2, 1.0, 0.95):.2f} x gap, "
          f"interval = max({erlang_quantile(ROUND_MSGS, 1.0, 0.95):.2f} x gap, 2 frames / (rho * lam) = 4 x gap)")


# --------------------------------------------------------------------------
# B. Fast shaped: the proposed seat class
# --------------------------------------------------------------------------
def section_b() -> None:
    h1("B. Fast shaped (proposed `seat` class, CIRISConstitution#200): rate vs cost between serve seats")
    print(f"own budget outside the divided cap; full mesh among M seats = M-1 links per server; "
          f"egress base = today {TODAY_EGRESS_GB} GB + slow-shaped cap {SLOW_CAP_GB:.0f} GB each way "
          f"(cover fills the cap whatever the load); quota {VULTR_QUOTA_GB} GB/month. "
          "Ingress assumed unmetered [assumption: Vultr bills egress]")
    rows = []
    for f in (1, 2, 5, 10):
        per_link_gb = f * FRAME_B * MONTH_S / GB
        lam = float(f)
        row = [f, f"{f * FRAME_B / 1000:.1f}", f"{per_link_gb:.0f}", fmt_s(1 / f), fmt_s(ROUND_MSGS / f),
               fmt_s(math.log(100) / f), f"{RHO * f * FRAME_B / 1000:.1f}", fmt_s(DELIVER_64K_FRAMES / f)]
        for m in (3, 9):
            links = m - 1
            seat_gb = links * per_link_gb
            total = TODAY_EGRESS_GB + SLOW_CAP_GB + seat_gb
            row += [f"{seat_gb:.0f}", f"{total:.0f}", f"{100 * total / VULTR_QUOTA_GB:.0f}%"]
        rows.append(row)
    table(["frames/s", "KB/s link", "GB/mo link", "gap", "round mean", "p99 wait", "real KB/s", "64 KiB",
           "M=3 seat GB", "M=3 total", "M=3 quota", "M=9 seat GB", "M=9 total", "M=9 quota"], rows)
    h2("B.2 headroom at M = 27 (the onion tier's 3 layers x 9 at some later scale) [projection]")
    rows = []
    for f in (1, 2, 5):
        per_link_gb = f * FRAME_B * MONTH_S / GB
        seat_gb = 26 * per_link_gb
        total = TODAY_EGRESS_GB + SLOW_CAP_GB + seat_gb
        rows.append([f, f"{seat_gb:.0f}", f"{total:.0f}", f"{100 * total / VULTR_QUOTA_GB:.0f}%"])
    table(["frames/s", "M=27 seat GB", "total", "quota"], rows)


# --------------------------------------------------------------------------
# C. Rotation vs Poisson
# --------------------------------------------------------------------------
def simulate_waits(n_links: int, scheme: str, ticks: int, samples: int) -> list[float]:
    """Row wait on one link under three node-wide schedulers at the same total rate.

    scheme 'poisson'   independent Poisson per link at lam = cap/(N*F)
    scheme 'fixed'     one node tick every F/cap seconds, links in a fixed cycle
    scheme 'dealt'     node-wide Poisson at cap/F, each tick dealt to the next link in a cycle
    Row arrivals are uniform in time (a Poisson arrival of negligible rate) on link 0;
    the wait is the time to link 0's next frame.
    """
    big_lam = NODE_CAP_B_S / FRAME_B
    times: list[float] = []
    t = 0.0
    if scheme == "poisson":
        lam = big_lam / n_links
        for _ in range(ticks // n_links + 2):
            t += RNG.expovariate(lam)
            times.append(t)
    elif scheme == "fixed":
        period = n_links / big_lam
        phase = RNG.random() * period
        times = [phase + i * period for i in range(ticks // n_links + 2)]
    elif scheme == "dealt":
        for i in range(ticks):
            t += RNG.expovariate(big_lam)
            if i % n_links == 0:
                times.append(t)
    else:
        raise ValueError(scheme)
    horizon = times[-1]
    waits = []
    for _ in range(samples):
        a = RNG.random() * horizon * 0.98
        j = bisect_right(times, a)
        waits.append(times[j] - a)
    return waits


def section_c() -> None:
    h1("C. Rotation vs Poisson: the same node-wide rate, three ways to place the next frame")
    big_lam = NODE_CAP_B_S / FRAME_B
    print(f"node-wide frame rate {big_lam:.3f} frames/s in every scheme; per-link mean gap = N / {big_lam:.3f}")
    print("analytic: Poisson per link -> wait Exp(lam): mean g, p99 4.6 g, no bound; fixed slots -> wait U(0,g): "
          "mean g/2, bound g; dealt node-Poisson -> per-link gaps Erlang(N): mean g(1+1/N)/2, p99 ~ g, "
          "no hard bound but tail ~ exp(-N)")
    rows = []
    ticks = 240_000
    for n in (8, 34, 100, 1000):
        g = gap_of(n)
        for scheme in ("poisson", "fixed", "dealt"):
            w = simulate_waits(n, scheme, ticks, 20_000)
            rows.append([n, scheme, fmt_s(g), fmt_s(statistics.fmean(w)), fmt_s(pct(w, 0.95)),
                         fmt_s(pct(w, 0.99)), fmt_s(max(w)), f"{max(w) / g:.2f}"])
    table(["N", "scheme", "gap g", "mean wait", "p95", "p99", "max (sim)", "max/g"], rows)
    h2("C.2 what a passive observer of the wire learns (the CC question, CC#200 Q3)")
    obs = [
        ["Poisson per link", "rate lam over many frames (hence N, given the class; conceded today)",
         "none: links of one node are independent streams", "CC 5.4.3 item 3 names it; ships in v44"],
        ["fixed slots", "N exactly from 2 frames; phase; the instant N changes",
         "yes: two links of one node interleave exactly and never coincide (a node fingerprint)",
         "not the Poisson timer 5.4.3 names; needs text"],
        ["dealt node-Poisson", "rate, and N also from the gap variance (CV = 1/sqrt N)",
         "weak: coincidences never happen on one node's links (same fingerprint, slower to read)",
         "node-wide stream is Poisson; per-link is Erlang; needs text"],
    ]
    table(["scheme", "from one link", "across a node's links", "status"], obs)


# --------------------------------------------------------------------------
# D. Canonical homing: rendezvous k of M
# --------------------------------------------------------------------------
def rank(node: int, m: int, period: int) -> list[int]:
    def h(c: int) -> bytes:
        return hashlib.sha256(f"{node}|{c}|{period}".encode()).digest()
    return sorted(range(m), key=h)


def homes(n: int, m: int, k: int, period: int = 0, down: frozenset[int] = frozenset()) -> tuple[list[int], int]:
    """Per-canonical home count with the ordered fallback past failed seats; and nodes with no home."""
    load = [0] * m
    orphans = 0
    for node in range(n):
        got = 0
        for c in rank(node, m, period):
            if c in down:
                continue
            load[c] += 1
            got += 1
            if got == k:
                break
        if got == 0:
            orphans += 1
    return load, orphans


def primary_homes(n: int, m: int, k: int, period: int) -> list[set[int]]:
    return [set(rank(node, m, period)[:k]) for node in range(n)]


def section_d() -> None:
    h1("D. Canonical homing: each node homes on the top k of M by H(node | canonical | period)")
    h2("D.1 per-server load and balance (today: every node peers with every canonical)")
    rows = []
    for n in (1000, 10000):
        for m in (3, 9):
            for k in (1, 2, 3):
                if k > m:
                    continue
                load, _ = homes(n, m, k)
                mean = statistics.fmean(load)
                rows.append([n, m, k, n, f"{mean:.0f}", max(load), min(load), f"{max(load) / mean:.3f}"])
    table(["N", "M", "k", "today/server", "mean homed", "max", "min", "max/mean"], rows)
    print("analytic: mean = N k / M; max/mean -> 1 as N grows (binomial spread sqrt(M/(N k)))")

    h2("D.2 one and two canonicals down: nodes with no live home; survivors' load (fallback to next in rank)")
    rows = []
    for n in (1000, 10000):
        for m in (3, 9):
            for k in (1, 2, 3):
                if k > m:
                    continue
                base, _ = homes(n, m, k)
                base_mean = statistics.fmean(base)
                prim = primary_homes(n, m, k, 0)
                for f in (1, 2):
                    down = frozenset(range(f))
                    load, _ = homes(n, m, k, down=down)
                    lost = sum(1 for hs in prim if hs <= down)
                    surv = [load[c] for c in range(m) if c not in down]
                    exact = math.comb(f, k) / math.comb(m, k) if k <= f else 0.0
                    rows.append([n, m, k, f, f"{100 * lost / n:.1f}%", f"{100 * exact:.1f}%",
                                 f"{max(surv) / base_mean:.2f}x", f"{m / (m - f):.2f}x"])
    table(["N", "M", "k", "down", "lost all top-k (sim)", "C(f,k)/C(M,k)", "busiest survivor", "M/(M-f)"], rows)
    print("with the ordered fallback nobody is without a home while any seat is up; 'lost all top-k' is the "
          "share that must dial a fallback, which is the failover stampede of D.4")

    h2("D.3 the period roll: homes that change when the period increments (independent rehash)")
    rows = []
    for n in (1000, 10000):
        for m in (3, 9):
            for k in (1, 2, 3):
                if k > m:
                    continue
                a = primary_homes(n, m, k, 0)
                b = primary_homes(n, m, k, 1)
                changed = sum(1 for x, y in zip(a, b) if x != y)
                new_dials = [0] * m
                for x, y in zip(a, b):
                    for c in y - x:
                        new_dials[c] += 1
                exp_dials = n * (k / m) * (1 - k / m)
                rows.append([n, m, k, f"{100 * changed / n:.0f}%", f"{100 * (1 - 1 / math.comb(m, k)):.0f}%",
                             max(new_dials), f"{exp_dials:.0f}"])
    table(["N", "M", "k", "nodes changing a home (sim)", "1 - 1/C(M,k)", "new dials at busiest seat",
           "N k/M (1-k/M)"], rows)

    h2("D.4 bounding the stampedes: stagger (per-node phase in the period) + make-before-break")
    tau = 10.0   # [assumption] seconds from dial to a settled, answering shaped link (E1 KEX, seal, offer, route fetch)
    jitter = 60.0  # [assumption] failover jitter window after a home is marked Down
    print(f"assumptions: settle time tau = {tau:.0f} s per new link; failover jitter window = {jitter:.0f} s; "
          "a node rolls at its own phase H(node) within the period, not at the period boundary")
    rows = []
    for n, m, k in ((1000, 3, 2), (1000, 9, 2), (10000, 9, 2), (10000, 9, 1)):
        exp_dials = n * (k / m) * (1 - k / m)
        for period in (3600, 86400):
            rate = exp_dials / period
            inflight = rate * tau
            steady = n * k / m
            boundary_peak = steady + exp_dials  # all switch at once, old kept until new answers
            failover = (n * k / m) / (m - 1)
            rows.append([n, m, k, fmt_s(period), f"{exp_dials:.0f}", f"{boundary_peak:.0f}",
                         f"{rate:.3f}", f"{inflight:.1f}", f"{steady + inflight:.0f}",
                         f"{failover:.0f}", f"{failover / jitter:.1f}"])
    table(["N", "M", "k", "period", "roll dials/seat", "boundary peak links (no stagger, MBB)",
           "staggered dials/s", "in flight", "peak links staggered", "failover dials/survivor",
           "failover dials/s"], rows)
    print("the roll is bounded to ~1 extra link in flight once staggered; the failover of one seat is the "
          "stampede that remains: N k / (M (M-1)) dials spread over the jitter window")

    h2("D.5 combined with A: shaped peers per canonical = N k / M, all homed links shaped")
    rows = []
    for n in (1000, 10000):
        for m in (3, 9):
            for k in (1, 2):
                peers = n * k / m
                lam = lam_of(peers)
                g = gap_of(peers)
                rows.append([n, m, k, f"{peers:.0f}", f"{share(peers):,.0f}", fmt_s(g), budget_frames(lam),
                             fmt_s(ROUND_MSGS * g), f"{RHO * share(peers):,.0f}"])
    table(["N", "M", "k", "peers/server", "B/s link", "gap = mean wait", "frames/W", "round mean (4 waits)",
           "real B/s"], rows)


# --------------------------------------------------------------------------
# E. Peer of last resort
# --------------------------------------------------------------------------
def section_e() -> None:
    h1("E. Peer of last resort: how many shaped links a canonical really carries (assumption-driven)")
    print("relay order (FSD/CIRIS_MESH.md section 1): direct -> contact relay -> canonical. Three facts shape "
          "the count:\n"
          "  (1) only a peer that OFFERS a class shapes the link (CC 5.4.3 item 1; fleet default: server on, "
          "home/phone opt-in), so an un-opted phone's link to a canonical is unshaped and outside the cap;\n"
          "  (2) a shaped link costs the same idle or busy, so what matters is the number of OPEN shaped links, "
          "not rounds;\n"
          "  (3) a home round at a canonical takes 4 waits at the gap of the moment, so links opened per round "
          "feed back into the gap (Little's law).")

    h2("E.1 share of a node's rounds and bytes that touch a canonical (parameters are assumptions)")
    c_peers = 10          # contacts / room peers a node rounds with
    peer_cadence = ROUND_INTERVAL_S
    p_nat = 0.6           # hard-NAT nodes (phone-heavy fleet)
    print(f"assumptions: {c_peers} contact peers per node at a {peer_cadence} s cadence; hard-NAT share {p_nat}; "
          "P(no live contact relay) = (1 - e a)^c with e = relay-eligible share of contacts, a = availability")
    rows = []
    for k, t_home in ((2, 600), (2, 3600), (1, 3600)):
        for e_a, c in ((0.3, 5), (0.3, 10), (0.6, 10)):
            p_norelay = (1 - e_a) ** c
            home_rate = k / t_home
            relayed_rate = c_peers / peer_cadence * p_nat * p_norelay
            total = c_peers / peer_cadence + home_rate
            frac = (home_rate + relayed_rate) / total
            rows.append([k, fmt_s(t_home), e_a, c, f"{100 * p_norelay:.1f}%", f"{100 * frac:.1f}%"])
    table(["k", "home cadence", "e*a", "contacts", "P(no relay)", "rounds (and row bytes) via canonical"], rows)
    print("bytes: the same share of ROW bytes as of rounds (a home round moves what a contact round moves); "
          "0% of bulk and video (FSD/CIRIS_MESH.md 6.4 V1); audio at most 5% of measured egress (V2)")

    h2("E.2 shaped links per canonical at the fixed point: P = S / (1 - theta / T_home), "
       "theta = 4 F (N k/M) p_shaped / cap")
    print("S = standing shaped links (hard-NAT nodes with no contact relay that keep the home link up, times "
          "p_shaped); a cadence T_home below theta cannot converge: links pile up faster than rounds finish")
    rows = []
    for n in (1000, 10000):
        for m in (3, 9):
            homed = n * 2 / m
            for p_shaped in (0.1, 0.5, 1.0):
                theta = ROUND_MSGS * FRAME_B * homed * p_shaped / NODE_CAP_B_S
                for p_standing in (0.1, 0.3):
                    s = homed * p_shaped * p_standing
                    cells = [n, m, f"{homed:.0f}", p_shaped, p_standing, f"{s:.0f}", fmt_s(theta)]
                    for t_home in (600, 3600, 86400):
                        if t_home <= theta:
                            cells.append("diverges")
                        else:
                            p = s / (1 - theta / t_home)
                            cells.append(f"{p:.0f} ({fmt_s(gap_of(p))})")
                    rows.append(cells)
    table(["N", "M", "homed (k=2)", "p_shaped", "p_standing", "S", "theta",
           "P @600s (gap)", "P @1h (gap)", "P @24h (gap)"], rows)
    print("reading: with 9 canonicals and 10,000 nodes, every shaped homed node rounding hourly is already past "
          "theta unless fewer than ~half of them shape; a daily home round converges everywhere. The realistic "
          "shaped-peer count per canonical is the standing set, a few tens to a few hundred, not N k / M")


# --------------------------------------------------------------------------
# F. CPU per shaped link
# --------------------------------------------------------------------------
def section_f() -> None:
    h1("F. CPU: one timer and one AEAD per frame, per shaped link (a bound, not a measurement)")
    aead_bps = 1.0e9        # [assumption] XChaCha20-Poly1305 software, one core, conservative
    lock_us = 20.0          # FSD/CIRIS_MESH.md 6.2 assumption (b): leviculum node lock per packet
    timer_us = 5.0          # [assumption] a tokio timer wake and re-arm
    print(f"assumptions: AEAD {aead_bps / 1e9:.1f} GB/s per core; node lock {lock_us:.0f} us per frame; "
          f"timer wake {timer_us:.0f} us; peers send at their own class share (a canonical's cap bounds its "
          "SEND only; its RECEIVE is the sum of its peers' shares)")
    out_fps = NODE_CAP_B_S / FRAME_B
    rows = []
    for n in (100, 1000, 10000):
        for peer_cls, peer_rate in (("server, few links", 7000), ("home", 2800), ("phone-wifi", 1400)):
            in_fps = n * peer_rate / FRAME_B
            fps = in_fps + out_fps
            bytes_s = fps * FRAME_B
            cpu = bytes_s / aead_bps + fps * (lock_us + timer_us) * 1e-6
            rows.append([n, peer_cls, f"{out_fps:.2f}", f"{in_fps:,.0f}", f"{bytes_s / 1e6:.1f}",
                         f"{bytes_s * 8 / 1e6:.0f}", f"{100 * cpu:.1f}%",
                         f"{bytes_s * MONTH_S / GB:,.0f}"])
    table(["N", "peer class", "out frames/s", "in frames/s", "MB/s", "Mbit/s", "core %", "ingress GB/mo"], rows)
    print("bound: the per-link CPU is under 2% of one vCPU per 1,000 server-class peers; it is not worth a "
          "model beyond this line. What scales with N is INGRESS bytes (the peers' aggregate), which the cap "
          "does not bound, and the DB work per real row, which shaping does not change (persist #1177 removed "
          "the storm; cover frames never reach the DB)")


# --------------------------------------------------------------------------
# G. Prior-art alternatives (survey of 2026-11-04: Tarzan, Herd, Loopix, COGS, Guard Sets)
# --------------------------------------------------------------------------
def section_g() -> None:
    h1("G. Prior-art alternatives, side by side with the ruled design")

    h2("G.1 (a) floorless cap/N vs (b) a bounded shaped-link count L with a per-link floor cap/L "
       "(Tarzan kappa ~ 2k, Herd 2-3 client links); peers past L are redirected to another home")
    print("leak in (a): one link's rate is cap/(N F), so an observer of ONE link reads N. A Poisson count of n "
          "frames estimates the rate to +-1/sqrt(n): N to +-10% needs ~100 frames, a +-1 change in N needs ~N^2 "
          "frames. Under fixed slots N is read exactly from 2 frames.")
    rows = []
    for n in (8, 34, 100, 300, 1000):
        g = gap_of(n)
        rows.append([n, fmt_s(g), fmt_s(100 * g), fmt_s(n * n * g), fmt_s(2 * g)])
    table(["N (a)", "gap", "N to +-10% (Poisson, 100 frames)", "detect N+-1 (N^2 frames)", "N exact (slots, 2 frames)"], rows)
    print("\n(b): the link rate is the class floor cap/L, a constant of the class, so a link reveals the class and "
          "nothing about N; the price is capacity: M L shaped homes in the fleet, the rest redirected")
    rows = []
    for L in (8, 16, 32, 64, 128):
        r = NODE_CAP_B_S / L
        g = FRAME_B / r
        lam = r / FRAME_B
        cells = [L, f"{r:,.0f}", fmt_s(g), fmt_s(g * math.log(100)), budget_frames(lam),
                 "yes" if erlang_cdf(2, lam, WAIT_TIMEOUT_S) ** 2 >= 0.95 and erlang_cdf(4, lam, ROUND_INTERVAL_S) >= 0.95 else "no"]
        for n, m in ((1000, 3), (1000, 9), (10000, 9)):
            demand = n * 2 / m          # k = 2 homes per node, shaped
            cells.append(f"{m * L}/{demand:.0f} ({100 * min(1, m * L / demand):.0f}%)")
        cells.append(f"{10000 * 2 / L:.0f}")
        rows.append(cells)
    table(["L (b)", "B/s link", "gap", "p99", "frames/W", "15s/30s rounds", "shaped homes M=3,N=1k",
           "M=9,N=1k", "M=9,N=10k", "seats to shape all of 10k"], rows)
    print("reading: (b) keeps the slow tier at seconds and keeps rounds inside today's constants up to L=16, "
          "and turns every peer past M L into a redirect (homing's fallback order) or an unshaped link; "
          "it does not make 10,000 shaped homes fit 9 seats, nothing does")

    h2("G.2 homing without per-period rotation: exposure (distinct seats that see a node in a year) vs balance")
    print("per-period rehash: a node's top-k is a fresh draw each period; stable HRW: H(node|canonical) with no "
          "period, re-homed only when the roster changes (assume 2 roster changes a year); beacon: an "
          "unpredictable public seed with a long period (Hayes & Danezis)")
    schemes = [("per period, hourly", 8760), ("per period, daily", 365), ("per period, monthly", 12),
               ("beacon, quarterly", 4), ("beacon, yearly", 1), ("stable HRW (+2 roster changes)", 0)]

    def stable_year(n: int, m: int, k: int) -> tuple[float, float]:
        """Stable top-k by H(node|seat); the year has two roster changes: seat m joins, then seat 1 leaves."""
        rosters = [list(range(m)), list(range(m + 1)), [c for c in range(m + 1) if c != 1]]
        seen_total = 0
        adv = 0
        for node in range(n):
            seen: set[int] = set()
            for roster in rosters:
                order = sorted(roster, key=lambda c: hashlib.sha256(f"{node}|{c}".encode()).digest())
                seen.update(order[:k])
            seen_total += len(seen)
            adv += 0 in seen
        return seen_total / n, adv / n

    rows = []
    for m in (3, 9):
        k = 2
        for name, draws in schemes:
            if draws:
                distinct = m * (1 - (1 - k / m) ** draws)
                p_adv = 1 - (1 - k / m) ** draws
            else:
                distinct, p_adv = stable_year(10000, m, k)
            rows.append([m, name, draws, f"{distinct:.1f}", f"{100 * p_adv:.0f}%"])
    table(["M", "scheme (k=2)", "draws/yr", "distinct seats see the node", "P(1 adversary seat of M was a home)"], rows)
    load0, _ = homes(10000, 9, 2, period=0)
    load1, _ = homes(10000, 9, 2, period=1)
    print(f"balance is the hash's, not the rotation's: max/mean at N=10,000, M=9, k=2 is "
          f"{max(load0) / statistics.fmean(load0):.3f} for the stable draw and "
          f"{max(load1) / statistics.fmean(load1):.3f} for the next period's; rotation buys no balance")
    print("what rotation does buy is Tarzan's anti-domination (no seat accumulates nodes for long); Guard Sets gets "
          "it by rotating SEAT membership on a public unpredictable seed, never the node's home")

    h2("G.3 slots vs Poisson with the merging property (Loopix): the node's uplink and one link")
    big_lam = NODE_CAP_B_S / FRAME_B
    rows = []
    for n in (8, 100, 1000):
        g = gap_of(n)
        rows.append([n, f"Poisson({big_lam:.2f}/s), any N", "Poisson, rate reveals N in ~100 frames = " + fmt_s(100 * g),
                     "none", fmt_s(g), fmt_s(4.6 * g), "unbounded"])
        rows.append([n, f"periodic at {big_lam:.2f}/s, any N", "periodic, N exact from 2 frames = " + fmt_s(2 * g),
                     "phase-locked, never coincide", fmt_s(g / 2), fmt_s(0.99 * g), fmt_s(g)])
    table(["N", "uplink process", "one link", "cross-link", "mean wait", "p99", "worst"], rows)
    print("Poisson wins on observability (N hidden on the uplink by merging, slowly readable on one link); slots win "
          "only on worst-case latency (one gap) and on making an active drop a visible missing slot")


def section_g_dropper() -> None:
    h2("G.4 the active dropper (Levine 2004; Feigenbaum 2010): what a dropped or delayed frame costs each scheme")
    rows = [
        ["Poisson per link, today", "invisible at the shaping layer; the leviculum Channel retransmits (seq), so a drop "
         "becomes a delay [inf]", "no defensive dropping; a delayed real frame shifts the real-share timing "
         "within W", "OPEN"],
        ["fixed slots", "a missing slot is visible within one gap", "none without a drop-tolerant wrapper", "n/a (not shipped)"],
        ["defensive dropping (Levine)", "the sender drops a known share of its own cover at random so an adversary's "
         "drops are not distinguishable", "costs real throughput at the same rho", "not designed"],
    ]
    table(["scheme", "a drop is", "a delay is", "status in edge"], rows)


# --------------------------------------------------------------------------
# H. BoundedWithFloor (ruled): L shaped links at the full class rate, the rest refused to bulk
# --------------------------------------------------------------------------
def erlang_b(c: int, a: float) -> float:
    """Blocking probability of an M/M/c/c loss system with offered load a (Erlangs)."""
    if c <= 0:
        return 1.0
    b = 1.0
    for k in range(1, c + 1):
        b = a * b / (k + a * b)
    return b


def section_h() -> None:
    h1("H. BoundedWithFloor (Eric, 2026-11-04): the ruled default, with A, D and E recomputed on it")
    print("L shaped links per node at the full class rate; link L+1 is refused (link_shaping_home_elsewhere) and "
          f"offered an unshaped bulk link. L = {NODE_CAP_LINKS} with no layer reserve, "
          f"{NODE_CAP_LINKS - LAYER_RESERVE_LINKS} while the Anonymous Tier holds its {LAYER_RESERVE_LINKS}; "
          "L = 16 is a sensitivity row only")

    h2("H.1 the per-link figures are N-independent (this is A under the bound)")
    rows = []
    for L, label in ((8, "ruled, no tier"), (4, "ruled, tier reserve held"), (16, "sensitivity")):
        r = LINK_RATE_B_S if L <= NODE_CAP_LINKS else NODE_CAP_B_S / L
        lam = r / FRAME_B
        g = 1 / lam
        p_wait = erlang_cdf(2, lam, WAIT_TIMEOUT_S) ** 2
        p_wait_1pf = erlang_cdf(2 * BOOTSTRAP_PLANES, lam, WAIT_TIMEOUT_S) ** 2
        p_round = erlang_cdf(ROUND_MSGS, lam, ROUND_INTERVAL_S)
        p_round_1pf = erlang_cdf(ROUND_MSGS * BOOTSTRAP_PLANES, lam, ROUND_INTERVAL_S)
        rows.append([L, label, f"{r:,.0f}", fmt_s(g), fmt_s(g * math.log(100)), budget_frames(lam),
                     f"{100 * p_wait:.1f}%", f"{100 * p_round:.1f}%", f"{100 * p_wait_1pf:.1f}%",
                     f"{100 * p_round_1pf:.1f}%", f"{L * r:,.0f}", f"{L * r * MONTH_S / GB:.0f}"])
    table(["L", "case", "B/s link", "gap = mean wait", "p99", "frames/W", "both waits <=15s (coalesced)",
           "round <=30s (coalesced)", "both waits (1/frame x5)", "round (1/frame x5)",
           "send = receive cap B/s", "GB/mo each way"], rows)
    print("reading: with every shaped link at 7,000 B/s the round constants hold coalesced (97.7% / 99.9%) and "
          "still fail one-per-frame with 5 planes (12% / 4%): coalescing and lambda-derived timeouts stay "
          "recommended. The bound caps RECEIVE as well as send: a peer's link to this node is one of its L, so "
          f"shaped ingress <= L x 7,000 B/s = {NODE_CAP_B_S:,} B/s, {SLOW_CAP_GB:.0f} GB/month; Q5 is moot for "
          "shaped links (bulk links were never shaped and are the service ladder's to bound)")

    h2("H.2 homing under the bound (D recomputed): a seat has L shaped home slots; the rest are refused and "
       "spill to an unshaped bulk link, a visible spill, the trade-off Eric accepted")
    rows = []
    for n in (1000, 10000):
        for m in (3, 9):
            demand = n * 2 / m
            for L in (8, 4, 16):
                for p_shaped in (0.1, 1.0):
                    want = demand * p_shaped
                    served = min(L, want)
                    rows.append([n, m, L, p_shaped, f"{want:.0f}", f"{served:.0f}", f"{100 * served / want:.1f}%",
                                 f"{want - served:.0f}", f"{m * L}", f"{m * L / (n * p_shaped):.3f}"])
    table(["N", "M", "L", "p_shaped", "shaped homes wanted/seat", "shaped slots", "served shaped",
           "spilled to bulk/seat", "fleet shaped slots", "slots per shaping node"], rows)
    print("a seat down loses its L slots and the survivors cannot absorb them (they are full); the homed nodes "
          "beyond the slots were already on bulk links, so the failover stampede of D.4 is unchanged in dials "
          "but changes nothing about shaping. A period roll cannot move a slot holder: the new home is full and "
          "refuses, make-before-break keeps the old, so under the bound rotation churns refusals, not slots")

    h2("H.3 home rounds on the slots (E recomputed): Erlang-B blocking of an opened-then-closed shaped home round")
    tau = 10.0
    hold = ROUND_MSGS * (FRAME_B / LINK_RATE_B_S) + tau
    print(f"a round holds a slot for 4 gaps + settle = {hold:.1f} s [assumption: settle {tau:.0f} s]; standing "
          "links hold a slot for good; demand = (N k/M) p_shaped / T_home rounds per second per seat; "
          "blocked rounds are refused to bulk (or retried)")
    rows = []
    for n, m in ((1000, 3), (1000, 9), (10000, 9)):
        homed = n * 2 / m
        for L in (8, 4):
            for p_shaped, p_standing in ((0.1, 0.0), (1.0, 0.0), (0.1, 0.1), (0.1, 0.3), (0.5, 0.1), (1.0, 0.1)):
                standing = homed * p_shaped * p_standing
                free = max(0, L - int(round(standing)))
                cells = [n, m, L, p_shaped, p_standing, f"{standing:.0f}", free]
                for t_home in (600, 3600, 86400):
                    lam = homed * p_shaped / t_home
                    a = lam * hold
                    cells.append(f"{100 * erlang_b(free, a):.0f}%")
                rows.append(cells)
    table(["N", "M", "L", "p_shaped", "p_standing", "standing", "free slots", "blocked @600s", "@1h", "@24h"], rows)
    print("reading: with no standing links the slots carry hourly home rounds from a tenth of 10,000 nodes at "
          "9 seats with under 1% blocked, and daily rounds from all of them; it is standing links that consume "
          "the slots: more than L standing shaped links at a seat and no home round runs there again. The "
          "canonical's shaped slots are for the last-resort standing set, capped at L by construction; every "
          "other homed node is on the bulk plane by Eric's rule, and that spill is what an observer sees")


def main() -> None:
    print("CIRISEdge transport tiers + canonical homing model (seed %d)" % SEED)
    section_a()
    section_b()
    section_c()
    section_d()
    section_e()
    section_f()
    section_g()
    section_g_dropper()
    section_h()


if __name__ == "__main__":
    main()
