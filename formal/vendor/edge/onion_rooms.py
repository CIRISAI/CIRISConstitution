#!/usr/bin/env python3
"""Rooms over the CIRIS onion tier: a deterministic model.

Run with ``python3 -I tools/models/onion_rooms.py``. Standard library only; no
network, no cargo, no files written. Shared constants and helpers are imported
from ``transport_tiers.py`` next to this file. Every random draw comes from one
seeded ``random.Random``, so two runs print the same tables.

The document that reads these tables is ``FSD/ONION_ROOMS_MODEL.md``. Sections
A-H follow the brief of 2026-11-04; section I answers Eric's question "why do we
care about conferred or unconferred?". Parameters marked [assumption] are listed
in the document's assumptions register.
"""
from __future__ import annotations

import importlib.util
import math
import os
import random
import sys
from collections import deque

sys.dont_write_bytecode = True   # the import below must leave no __pycache__ behind

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("transport_tiers", os.path.join(_here, "transport_tiers.py"))
TT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TT)

table, fmt_s, h1, h2, pct = TT.table, TT.fmt_s, TT.h1, TT.h2, TT.pct
F = TT.FRAME_B
RHO = TT.RHO
L = TT.NODE_CAP_LINKS
MONTH_S = TT.MONTH_S
GB = TT.GB

SEED = 20261105
RNG = random.Random(SEED)

# Wire (src/onion/packet.rs on feat/onion-v44 at 1eeeb14; the brief's 15,200 B / 1168 B slot is the
# withdrawn draft: the compile-time assert is PACKET == 15_296).
SLOT_B = 1184
SLOTS = 6
BODY_B = 8192
BODY_CAP_B = 8174
PACKET_B = 15_296
CONP_B = 4
FRAME_BODY_B = TT.FRAME_PAYLOAD_B     # 16,248 [inf], from transport_tiers
assert PACKET_B + CONP_B <= FRAME_BODY_B   # one onion packet = one shaped frame
ROUTE_BLOB_B = 3 * SLOT_B
HOLD_BOUND = 256
MAILBOX_MAX = 64                       # FSD/ONION_ROUTING.md section 10
MU_S = 2.0                             # OnionPolicy::mix_mean_delay_ms default
MAX_HOLD_S = 60.0

CLASS = dict(TT.CLASS_B_S)
CLASS["seat"] = 33_000                 # CC 5.4.3 rc17 table


def lam(c: str) -> float:
    return CLASS[c] / F


def pkt_s(c: str) -> float:
    """Real packets per second one way on one link of class c (one packet per frame)."""
    return RHO * lam(c)


# [assumption] parameters
U_ROW = 0.25            # share of a link's real budget already used by the row plane
AVAIL = {"server": 0.999, "home": 0.95, "phone-wifi": 0.30}   # up and relaying
CHURN_H = {"seat": 0.001, "server": 0.001, "home": 0.01, "phone-wifi": 0.05, "phone-always": 0.40}  # prior model (d)
MSGS_DAY = 40           # room messages one person writes per day
ROOM_N = 20             # room size used for capacity
ROOMS_PER_PERSON = 3    # rooms one person is in (for route upkeep)
PERSONS_PER_HOME = 4    # persons served per relay-offering home in the growth table
ROW_CHAT_B = 5_000      # chat row with hybrid signature [inf]
ROW_MEAN_B = 8_500      # T2 sample mean (docs/SHAPING_RHO_W)
BODY_HDR_B = 104        # CC 5.4.2 envelope 74 B + room tag 16 + author, seq, count, flags 14; section D
FETCH_BATCH = 4         # packets one fetch collects


def kappa_room(n: int) -> int:
    """Crossings for one message, room mailbox pushing along reply routes (option C2)."""
    return 6 + 4 * (n - 1)


def kappa_forward(n: int) -> int:
    """The same, the mailbox building a full six-hop forward route to each member's own home.
    Needed once a 3-hop reply route can no longer join the mailbox (section A.10)."""
    return 6 * n


def upkeep_day_per_person(n: int = ROOM_N, rooms: int = ROOMS_PER_PERSON) -> float:
    """Each room hour: each member hands the mailbox a reply route (6 crossings); the mailbox
    hands each member its own route (4). So 10 crossings per member per room per hour."""
    return 10 * rooms * 24


def person_crossings_day(n: int = ROOM_N) -> float:
    return MSGS_DAY * kappa_room(n) + upkeep_day_per_person(n)


def e_min_rate(mix: dict[str, float]) -> float:
    """Mean rate of a link between two relays drawn from mix: the lower of two offers."""
    return sum(pa * pb * min(CLASS[a], CLASS[b]) for a, pa in mix.items() for b, pb in mix.items())


def theta(n_by_class: dict[str, float], d: int, mix: dict[str, float]) -> float:
    """Crossings per second the relays can carry: sum a * d * rho * E[min rate] / F * (1-u_row)."""
    rate = e_min_rate(mix)
    return sum(n * AVAIL[c] for c, n in n_by_class.items()) * d * RHO * rate / F * (1 - U_ROW)


def seat_core(c: int, stage_links: int) -> float:
    return c * stage_links * pkt_s("seat") * (1 - U_ROW)


def deal_others(others: int, conferred: int, cap: int = 2) -> int:
    per_layer = [conferred // 3 + (1 if i < conferred % 3 else 0) for i in range(3)]
    return min(others, sum(math.ceil(cap * p) for p in per_layer))


# ---------------------------------------------------------------------------------------------
def section_a() -> None:
    h1("A. Self-growing capacity")
    h2("A.1 one link, one packet per frame (15,300 B of the 16,272 B frame; goodput = body capacity 8,174 B)")
    rows = []
    for c in ("seat", "server", "home", "phone-wifi", "phone-cellular"):
        rows.append([c, f"{CLASS[c]:,}", fmt_s(1 / lam(c)), f"{pkt_s(c):.4f}", f"{pkt_s(c) * 3600:,.0f}",
                     f"{pkt_s(c) * BODY_CAP_B:,.0f}", f"{CLASS[c] * MONTH_S / GB:.1f}"])
    table(["class", "B/s", "gap", "real pkt/s", "real pkt/h", "goodput B/s", "GB/mo each way"], rows)
    print(f"seat link / home link = {pkt_s('seat') / pkt_s('home'):.1f}; a home's eight links, one way: "
          f"{8 * pkt_s('home'):.3f} pkt/s of cover it already pays for")

    h2("A.2 the floor and the width a layer can have under the bound (uniform pick needs next-layer complete)")
    rows = []
    for w in (3, 4, 9, 30, 333):
        need = 2 * w
        rows.append([w, need, "yes" if need <= 8 else "NO", "yes" if need <= 4 else "NO"])
    table(["width w", "layer links needed (prev+next)", "fits 8", "fits reserve 4"], rows)
    print("layer_peers() asks a relay for both adjacent layers in full and sender.rs picks uniformly, so a non-seat "
          "relay fits only w <= 4 (w <= 2 inside the reserve; the floor is w = 3). A next hop without a shaped link is "
          "refused onion_next_hop_unroutable")

    h2("A.3 the deal: active relays vs relay-offering homes, cap c = 2 (per layer, others <= ceil(2 x conferred))")
    rows = []
    for c_n in (3, 9, 30, 100, 333, 1000):
        for homes in (100, 1000, 10000):
            dealt = deal_others(homes, c_n)
            rows.append([c_n, homes, dealt, homes - dealt, f"{100 * dealt / homes:.1f}%", c_n + dealt,
                         f"{(c_n + dealt) / 3:.0f}"])
    table(["conferred C", "homes", "dealt others", "waiting", "share dealt", "active", "layer width"], rows)

    h2("A.4 fleet crossings/s and messages: nine seats, then homes, by class mix (D = link degree used; "
       f"u_row {U_ROW}; availability {AVAIL})")
    print(f"kappa = {kappa_room(ROOM_N)} crossings per message at n = {ROOM_N}; a person = "
          f"{person_crossings_day():,.0f} crossings/day = {person_crossings_day() / 86400:.4f}/s")
    mixes = {
        "homes": {"home": 1.0},
        "10% server": {"server": 0.1, "home": 0.9},
        "50% phone": {"home": 0.5, "phone-wifi": 0.5},
    }
    core3 = seat_core(9, 3)
    print(f"nine seats alone: seat links only, 3 per stage, 3 stages: {3 * core3:.1f} crossings/s total, "
          f"{core3:.1f}/stage; a six-hop route crosses two stages twice, so {core3 / 2:.1f} packets/s end to end")
    rows = []
    for name, mix in mixes.items():
        for homes in (0, 100, 1000, 10000):
            dealt = deal_others(homes, 9)
            capped = theta({k: dealt * v for k, v in mix.items()}, 4, mix)
            free6 = theta({k: homes * v for k, v in mix.items()}, 6, mix)
            cap_tot = 3 * core3 + capped
            free_tot = 3 * core3 + free6
            per = person_crossings_day() / 86400
            rows.append([name, homes, dealt, f"{cap_tot:.1f}", f"{free_tot:,.1f}", f"{free_tot / max(cap_tot, 1e-9):.1f}x",
                         f"{cap_tot / kappa_room(ROOM_N) * 3600:,.0f}", f"{free_tot / kappa_room(ROOM_N) * 3600:,.0f}",
                         f"{cap_tot / per:,.0f}", f"{free_tot / per:,.0f}"])
    table(["mix", "homes", "dealt", "Theta capped /s", "Theta all /s", "ratio", "msg/h capped", "msg/h all",
           "persons capped", "persons all"], rows)
    per = person_crossings_day() / 86400
    trunk = 72 * pkt_s("home") * (1 - U_ROW)
    trunk_msg_h = trunk / (ROOM_N - 1) * 3600
    print(f"the seat core has a trunk: 72 non-seat slots at home class = {trunk:.2f} pkt/s out, {trunk_msg_h:,.0f} msg/h at "
          f"n = {ROOM_N}, {trunk_msg_h * 24 / MSGS_DAY:,.0f} persons, and at most 72 attached nodes. Every 'capped' figure "
          f"above is bounded by this when homes off the deal must reach the core")
    print(f"if the mailbox must use forward routes (A.10): kappa {kappa_forward(ROOM_N)}, persons x "
          f"{(person_crossings_day()) / (MSGS_DAY * kappa_forward(ROOM_N) + upkeep_day_per_person()):.2f}")
    near = 3 * (pkt_s("seat") + 8 * AVAIL["home"] * pkt_s("home")) * (1 - U_ROW)
    print(f"three canonicals + six homes, the minimum deal: complete layers of 3: {near:.2f} crossings/s, "
          f"{near / per:,.0f} persons, {near / kappa_room(ROOM_N) * 3600:,.0f} msg/h at n = {ROOM_N}")
    home_cap = AVAIL["home"] * 6 * pkt_s("home") * (1 - U_ROW)
    print(f"one home at D = 6: {home_cap:.3f} crossings/s = {home_cap / per:.1f} persons; "
          f"demand per home at {PERSONS_PER_HOME} persons = {100 * PERSONS_PER_HOME * per / home_cap:.0f}% of what it adds")

    h2("A.5 how many conferred relays demand needs under the cap (each conferred home brings two others)")
    triple = 3 * AVAIL["home"] * 4 * pkt_s("home") * (1 - U_ROW)
    rows = []
    for persons in (1000, 10000, 100000):
        need = persons * per
        beyond = max(0.0, need - 3 * core3)
        c_add = math.ceil(beyond / triple)
        rows.append([persons, f"{need:,.1f}", 9 + c_add, 27 + 3 * c_add])
    table(["persons", "crossings/s", "conferred needed", "active relays"], rows)

    h2("A.6 relay uptime: the minimum deal, and the client's small-set line (below ten per layer)")
    rows = [[a, f"{100 * a ** 6:.1f}%", f"{3 + 6 * a:.1f}"] for a in (0.99, 0.95, 0.90, 0.80)]
    table(["home availability", "P(all six homes of a 3 seat + 6 home deal answer)",
           "answering per layer, 9 seats + 18 homes"], rows)
    print("nine seats cap a layer at 3 + 6 = 9, so the client's 'set is small' line (below ten) never clears; "
          "ten per layer needs at least 12 conferred (4 per layer, width 12)")

    h2("A.7 federation-reach rendezvous rows: 22,072 B per person per hour, to everyone (CC 3.1.4)")
    rows = []
    for u in (100, 1000, 10000, 100000):
        bps = 22_072 * u / 3600
        rows.append([u, f"{bps:,.0f}", f"{bps / (RHO * CLASS['home'] * (1 - U_ROW)):.2f}", f"{bps * MONTH_S / GB:,.0f}"])
    table(["persons", "B/s to every node", "home link budgets", "GB/mo per node"], rows)

    h2("A.8 free shaped slots F(H) = 72 + (net) x H; reserve held vs not")
    rows = [[h, f"{72 + 7 * h:,}", f"{72 + 3 * h:,}"] for h in (0, 100, 1000, 10000)]
    table(["homes", "slots, no reserve (+7)", "slots, reserve 4 held (+3)"], rows)


# ---------------------------------------------------------------------------------------------
def walk_reach(n: int, d: int, sources: int, hops: int = 6) -> tuple[float, float]:
    """Random d-regular undirected graph: mean share of nodes within `hops`, and min over sources."""
    while True:
        stubs = [i for i in range(n) for _ in range(d)]
        RNG.shuffle(stubs)
        adj: list[set[int]] = [set() for _ in range(n)]
        for a, b in zip(stubs[::2], stubs[1::2]):
            if a != b:
                adj[a].add(b)
                adj[b].add(a)
        break
    shares = []
    for s in RNG.sample(range(n), sources):
        seen = {s}
        q = deque([(s, 0)])
        while q:
            v, depth = q.popleft()
            if depth == hops:
                continue
            for w in adj[v]:
                if w not in seen:
                    seen.add(w)
                    q.append((w, depth + 1))
        shares.append(len(seen) / n)
    return sum(shares) / len(shares), min(shares)


def strat_reach(width: int, d: int, entries: int, steps: int, trials: int) -> float:
    """Stratified cycle of three layers, d random out-links per relay; share of the final layer reached."""
    out = [[[RNG.randrange(width) for _ in range(d)] for _ in range(width)] for _ in range(3)]
    tot = 0.0
    for _ in range(trials):
        cur = set(RNG.sample(range(width), min(entries, width)))
        layer = 0
        for _ in range(steps):
            cur = {w for v in cur for w in out[layer][v]}
            layer = (layer + 1) % 3
        tot += len(cur) / width
    return tot / trials


def section_a_routes() -> None:
    h2("A.9 can a route exist? share of the target set reachable, sparse layers vs a walk on the standing graph")
    rows = []
    for relays, d_out, e, trials in ((30, 2, 2, 400), (300, 2, 2, 400), (300, 3, 2, 400), (300, 4, 2, 400),
                                     (3000, 2, 2, 100), (3000, 3, 2, 100), (3000, 4, 2, 100), (3000, 4, 4, 100),
                                     (10002, 4, 2, 30)):
        w = relays // 3
        rows.append([relays, w, d_out, e, f"{100 * strat_reach(w, d_out, e, 3, trials):.1f}%",
                     f"{100 * strat_reach(w, d_out, e, 5, trials):.1f}%"])
    table(["relays", "width", "d out", "entries", "3 hops to r1 (blob join), 1 blob", "5 hops to a known mailbox"], rows)
    rows = []
    for n, d in ((1000, 4), (1000, 6), (1000, 8), (10000, 4), (10000, 6), (10000, 8)):
        mean, low = walk_reach(n, d, 40)
        rows.append([n, d, f"{(d - 1) ** 6:,}", f"{100 * mean:.1f}%", f"{100 * low:.1f}%",
                     f"{100 * (1 - (1 - mean) ** 2):.1f}%", f"{100 * (1 - (1 - mean) ** 4):.1f}%"])
    table(["relays", "degree D", "(D-1)^6", "mean reach in 6 hops", "worst of 40 sources",
           "with 2 guards or 2 mailboxes", "2 guards x 2 mailboxes"], rows)
    h2("A.10 can a 3-hop reply route join a mailbox? the mailbox and the reader's first hop within 4 crossings")
    rows = []
    for n, d in ((300, 6), (1000, 6), (1000, 8), (10000, 6), (10000, 8)):
        mean, _ = walk_reach(n, d, 40, hops=4)
        rows.append([n, d, f"{100 * mean:.1f}%"])
    table(["relays", "degree D", "reach in 4 hops"], rows)


# ---------------------------------------------------------------------------------------------
def sim_path(classes: list[str], mu: float, load_u: float, n: int = 100_000) -> tuple[float, float]:
    xs = []
    holds = max(0, len(classes) - 1)
    for _ in range(n):
        t = 0.0
        for c in classes:
            t += RNG.expovariate(lam(c) * (1 - load_u * RHO))
        for _ in range(holds):
            t += min(MAX_HOLD_S, RNG.expovariate(1 / mu))
        xs.append(t)
    xs.sort()
    return sum(xs) / n, xs[int(0.95 * n)]


def section_b() -> None:
    h1("B. Latency: one room message over six crossings")
    print("each crossing waits Exp(lambda_class); each of the five relays before the last holds Exp(mu), clamp 60 s; "
          "the last hop holds nothing. load u = share of rho in use, wait scales 1/(1 - u rho) [inf]")
    home, wifi, cell, seat, server = "home", "phone-wifi", "phone-cellular", "seat", "server"
    scen = {
        "seat core (home in, 4 seat, home out)": [home, seat, seat, seat, seat, home],
        "seats only, server access": [server, seat, seat, seat, seat, server],
        "all server": [server] * 6,
        "all home": [home] * 6,
        "home access, seat at the join": [home, home, seat, seat, home, home],
        "wifi phone sender, homes": [wifi] + [home] * 5,
        "cellular phone sender, homes": [cell] + [home] * 5,
        "two wifi phone relays in path": [home, wifi, wifi, home, home, home],
        "all wifi phone": [wifi] * 6,
    }
    rows = []
    for name, cl in scen.items():
        row = [name]
        for mu, u in ((MU_S, 0.0), (MU_S, 0.5), (8.0, 0.0)):
            m, p = sim_path(cl, mu, u)
            row += [fmt_s(m), fmt_s(p)]
        rows.append(row)
    table(["path to the mailbox", "mu2 mean", "p95", "u.5 mean", "p95", "mu8 mean", "p95"], rows)
    h2("B.2 to a person: mailbox to reader's own home is 4 crossings; a phone asks its home over the self link")
    rows = []
    for name, up, down in (("homes, reader is a home", [home] * 6, [home] * 4),
                           ("wifi phone to wifi phone, homes between", [wifi] + [home] * 5, [home] * 3 + [wifi]),
                           ("seat-core join, wifi phones", [wifi, home, seat, seat, home, home], [home, home, home, wifi]),
                           ("cellular phone to cellular phone", [cell] + [home] * 5, [home] * 3 + [cell])):
        m, p = sim_path(up + down, MU_S, 0.0)
        rows.append([name, fmt_s(m), fmt_s(p)])
    table(["sender to reader", "mean", "p95"], rows)
    h2("B.3 a phone as a relay (CC 5.4.6 item 1 lets it while on Wi-Fi and charging)")
    rows = []
    for c in ("home", "phone-wifi"):
        s = (1 - CHURN_H[c]) ** 2
        rows.append([c, f"{pkt_s(c) * 8:.3f}", fmt_s(1 / lam(c)), f"{AVAIL[c]:.2f}", f"{100 * s:.1f}%",
                     f"{AVAIL[c] * pkt_s(c) * 8:.3f}"])
    table(["relay class", "pkt/s at 8 links", "added gap", "availability", "2-relay route survives 1 h",
           "cap slot yield pkt/s"], rows)
    print(f"a phone in a deal cap slot yields {AVAIL['phone-wifi'] * pkt_s('phone-wifi') / (AVAIL['home'] * pkt_s('home')):.2f} "
          "of a home, and drags every link it touches to 1,400 B/s (lower of two offers)")


# ---------------------------------------------------------------------------------------------
def section_c() -> None:
    h1("C. Fan-out: a room of n, one message, no multicast in an onion")
    print(f"crossing = one packet over one shaped link. fetch batch {FETCH_BATCH}. mailbox/home D = 6, u_row {U_ROW}")
    out_home = 6 * pkt_s("home") * (1 - U_ROW)
    out_server = 6 * pkt_s("server") * (1 - U_ROW)
    phone = pkt_s("phone-wifi")
    rows = []
    for n in (5, 20, 100):
        r = n - 1
        k3 = 3
        depth = math.ceil(math.log(max(n, 2), k3))
        opts = [
            ("O1a per-member, CC seat mailboxes", r, 6 * r + r * (4 + 3 / FETCH_BATCH), out_home / r, phone / r),
            ("O1b per-member, each to own home", r, 6 * r, out_home / r, phone / r),
            ("O2 room mailbox pushes on reply routes", 1, kappa_room(n), out_home / r, min(phone, out_home / r)),
            ("O2s same, server-class mailbox", 1, kappa_room(n), out_server / r, min(phone, out_server / r)),
            ("O3 group rendezvous, members fetch", 1, 6 + r * (4 + 3 / FETCH_BATCH), out_home / r, min(phone, out_home / r)),
            ("O2f mailbox pushes on forward routes", 1, kappa_forward(n), out_home / r, min(phone, out_home / r)),
            ("O4 member tree k=3, depth %d" % depth, 1, 6 + 4 * r, out_home / k3, min(phone, out_home / k3)),
        ]
        for name, pkts, cross, bott, ph in opts:
            rows.append([n, name, pkts, f"{cross:,.0f}", f"{min(bott, out_home / max(pkts, 1)) * 3600:,.0f}",
                         f"{ph * 3600:,.1f}", f"{cross / 60:.2f}"])
    table(["n", "option", "sender pkts", "crossings/msg", "msg/h from a home", "msg/h from a wifi phone alone",
           "mesh crossings/s at 1 msg/min"], rows)
    print(f"reader ceiling on one shaped link: wifi phone {phone * 3600:.0f} pkt/h, cellular "
          f"{pkt_s('phone-cellular') * 3600:.0f} pkt/h, across all rooms. Own-home reader: {out_home * 3600:,.0f} pkt/h")
    print(f"tree latency: depth x 76 s at home class: n=20 {fmt_s(3 * 76)}, n=100 {fmt_s(5 * 76)}")
    print(f"route upkeep per room hour: 10 n crossings; n=100: {10 * 100 / 3600:.2f}/s")
    print(f"sending n-1 packets from a wifi phone, one link: n=20 {fmt_s(19 / phone)}, n=100 {fmt_s(99 / phone)}; "
          f"cellular n=20 {fmt_s(19 / pkt_s('phone-cellular'))}")


# ---------------------------------------------------------------------------------------------
def chunks(size: int) -> int:
    return math.ceil(size / (BODY_CAP_B - BODY_HDR_B))


def section_d() -> None:
    h1("D. Sync without rounds")
    h2("D.1 what a Summary/Diff round would cost over packets, vs the digest")
    rtt = 6 + 7
    rows = [["Summary/Summary/Diff/Deliver over two route pairs", 4 * 6, "4 traversals", f"{4 * 45:.0f} s at home class"],
            ["digest push on a reply route", 4, "1 traversal", "30 s, no reply owed"],
            ["catch-up pull + answer of k pkts", f"6 + 4k", "2 traversals", "75 s plus k-1 frame gaps"]]
    table(["exchange", "crossings", "traversals", "latency"], rows)
    h2("D.2 digest size: version vector of (author_tag u32, high_seq u32) + 16 B window hash + 44 B header")
    rows = []
    for a in (5, 20, 100, 500, 1000):
        b = 44 + 16 + 8 * a
        rows.append([a, f"{b:,}", f"{100 * b / BODY_CAP_B:.1f}%", "yes" if b <= BODY_CAP_B else "NO"])
    table(["active authors", "digest B", "share of a body", "fits one body"], rows)
    h2(f"D.3 chunking: 8,174 B capacity less a {BODY_HDR_B} B header = {BODY_CAP_B - BODY_HDR_B:,} B per chunk")
    rows = []
    for name, size in (("reaction / chat row", ROW_CHAT_B), ("T2 mean row", ROW_MEAN_B), ("key record + contact request", 20_000),
                       ("MLS Welcome + wraps [assumption]", 64_000), ("largest shaped row, 64 KiB", 65_536)):
        k = chunks(size)
        rows.append([name, f"{size:,}", k, 6 * k, fmt_s(k / pkt_s("home")), fmt_s(k / (6 * pkt_s("home"))),
                     fmt_s(k / pkt_s("phone-wifi")), fmt_s(k / pkt_s("phone-cellular"))])
    table(["row", "bytes", "chunks", "crossings to mailbox", "1 home link", "6 home links", "1 wifi link", "1 cell link"], rows)
    h2("D.4 loss: packet delivery p; a 9-chunk row whole; ARQ by digest vs parity")
    rows = []
    for q_link in (0.001, 0.005, 0.02):
        p6 = (1 - q_link) ** 6
        one = p6
        whole = p6 ** 9
        exp_repair = 9 * (1 - p6)
        parity = sum(math.comb(11, k) * p6 ** k * (1 - p6) ** (11 - k) for k in range(9, 12))
        rows.append([q_link, f"{100 * one:.2f}%", f"{100 * whole:.1f}%", f"{exp_repair:.2f}", f"{100 * parity:.2f}%", 2])
    table(["hop loss", "packet arrives", "9 of 9", "pulled chunks per row", "9 of 11 with parity", "parity pkts always sent"], rows)
    print("independent loss only. A reused reply route fails whole: losses inside one route-hour are correlated, parity "
          "over one route buys nothing there, and the hourly digest on the next route repairs it")
    h2("D.5 what a digest cadence costs, per room member")
    rows = []
    for t, name in ((600, "10 min"), (3600, "1 h"), (21600, "6 h")):
        rows.append([name, f"{4 * 86400 / t:,.0f}", f"{86400 / t:,.0f}", f"{100 * 4 * 86400 / t / person_crossings_day():.1f}%"])
    table(["cadence", "crossings/day/member/room", "packets/day read", "share of a person's load"], rows)


# ---------------------------------------------------------------------------------------------
def section_e() -> None:
    h1("E. Mailbox: serve seat vs member-owned")
    h2("E.1 retention against sleep (rows arrive at 1/h per room per sleeper, three rooms; seat keeps period + grace)")
    rows = []
    for sleep_h in (0.25, 1, 2, 8, 24):
        lost = max(0.0, 1 - min(sleep_h, 1.5) / sleep_h) if sleep_h > 0 else 0
        arriving = 3 * sleep_h
        rows.append([sleep_h, f"{arriving:.1f}", f"{100 * lost:.0f}%", "0%" ])
    table(["sleep h", "packets waiting", "lost at a seat (mean hold 1.5 h)", "lost at a member node"], rows)
    print(f"seat bound: {MAILBOX_MAX} packets per key = {MAILBOX_MAX * BODY_B / 1e6:.2f} MB of bodies; a room burst of "
          f"{MAILBOX_MAX} messages while a phone sleeps refuses rendezvous_mailbox_full")
    h2("E.2 availability of the receive point and survival of an hour-long route")
    rows = []
    for name, a, churn in (("one seat", AVAIL["server"], CHURN_H["seat"]), ("one member home", AVAIL["home"], CHURN_H["home"])):
        for m in (1, 2, 3):
            if "seat" in name and m > 1:
                continue
            up = 1 - (1 - a) ** m
            surv_home_path = (1 - CHURN_H["home"]) ** 2 * (1 - churn ** m)
            rows.append([name, m, f"{100 * up:.3f}%", f"{100 * surv_home_path:.2f}%"])
    table(["receive point", "replicas", "at least one up", "1 h route via 2 home relays survives"], rows)
    print("a sleeping phone at the end of a route loses it outright; a phone is never a mailbox and never a reused-route hop")
    h2("E.3 seat load if every person's mailbox is a layer-3 seat")
    rows = []
    for persons, m in ((1000, 9), (10000, 9), (10000, 30)):
        seats = max(1, m // 3)
        keys = persons / seats
        pkts = persons * MSGS_DAY * (ROOM_N - 1) / 86400 / seats
        rows.append([persons, m, seats, f"{keys:,.0f}", f"{pkts:.1f}", f"{pkts / (8 * pkt_s('home')):.1f}",
                     f"{keys * MAILBOX_MAX * BODY_B / GB:.1f}"])
    table(["persons", "seats", "layer-3 seats", "keys/seat", "pkts/s in", "x 8 home links", "worst mailbox GB/seat"], rows)


# ---------------------------------------------------------------------------------------------
def section_f() -> None:
    h1("F. What a global observer still learns")
    h2("F.1 trilemma: 2 beta l >= 1 read as 2 r D >= 1 [inf normalisation]; r = per-user end-to-end packet rate, "
       "D = the delay a message is mixed over")
    rows = []
    for d in (15, 45, 90, 180):
        r = 1 / (2 * d)
        day = r * 86400
        cross = day * 3
        rows.append([f"{d} s", fmt_s(1 / r), f"{day:,.0f}", f"{cross:,.0f}", f"{100 * cross / person_crossings_day():.0f}%",
                     f"{cross / 86400 / (AVAIL['home'] * 6 * pkt_s('home') * (1 - U_ROW) / PERSONS_PER_HOME) * 100:.0f}%"])
    table(["D", "needed end-to-end send interval", "packets/day/person", "cover crossings/day (3 hop)",
           "vs person's real load", "share of a person's slice of a home"], rows)
    print("link cover answers the GPA alone: an always-on shaped home emits a frame every 5.8 s, so 2 beta l >> 1 at the "
          "wire. It ends at the next hop, so against a compromised relay only end-to-end packets count; "
          "with c compromised hops on a route of l, l is replaced by l - c (Das et al.)")
    h2("F.2 anonymity set of a sender: everyone who could have sent inside D")
    rows = []
    for u in (100, 1000, 10000, 100000):
        for o, r_day, name in ((1.0, 40, "homes, no e2e cover"), (1.0, 960, "homes, cover 1/90 s"), (0.3, 40, "phones online 30%, no cover")):
            r = r_day / 86400
            d = 45
            a = u * o * (1 - math.exp(-r * d))
            rows.append([u, name, f"{u * o:,.0f}", f"{a:,.1f}", f"{2 * r * d:.3f}"])
    table(["users", "case", "set vs pure GPA", "set vs compromised relay, D = 45 s", "2 r D"], rows)
    h2("F.3 relay view: nodes that can be the source seen from hop r on a D-regular walk, and the crowd in a relay")
    rows = []
    for d in (4, 6, 8):
        rows.append([d, *(f"{(d - 1) ** r:,}" for r in (1, 2, 3, 5))])
    table(["D", "r=1", "r=2", "r=3", "r=5"], rows)
    rows = []
    for c, d_links in (("home", 6), ("server", 6), ("seat", 3)):
        cap = d_links * pkt_s(c)
        rows.append([c, f"{cap:.2f}", f"{cap * MU_S:.2f}", f"{3 / cap:.1f} s", f"{cap * 0.1 * MU_S:.2f}"])
    table(["relay", "max pkt/s", "crowd at full load, mu 2 s", "mu for crowd 3 at full load", "crowd at 10% load, mu 2 s"], rows)
    h2("F.4 intersection: phones. Candidates left after m room events an insider times, online share o")
    rows = []
    for o in (0.95, 0.5, 0.3):
        rows.append([o, *(f"{o ** m:.2e}" for m in (5, 20, 100))])
    table(["o", "m=5", "m=20", "m=100"], rows)
    h2("F.5 member links: what the link graph alone says")
    rows = []
    for n in (5, 20, 100):
        rows.append([n, n * (n - 1) // 2, f"{min(L, n - 1)}", "whole clique" if n <= 9 else f"{min(1, 8 / (n - 1)) * 100:.0f}% of edges per node"])
    table(["n", "clique edges", "member links a node could hold", "shown to a GPA if members link"], rows)


# ---------------------------------------------------------------------------------------------
def section_g() -> None:
    h1("G. Feature cost at this rung")
    home6 = 6 * pkt_s("home")
    rows = []
    for name, size, each in (("chat message", ROW_CHAT_B, True), ("reaction", ROW_CHAT_B, True), ("receipt per reader, n=20", ROW_CHAT_B, False),
                             ("hourly read mark to mailbox, all readers", 100, False), ("image 64 KiB", 65_536, True), ("image 1 MiB", 1 << 20, True)):
        k = chunks(size)
        cr = (6 + 4 * 19) * k if each else ((19 * 82) if "receipt" in name else 19 * 6)
        rows.append([name, f"{size:,}", k, f"{cr:,}", fmt_s(k / pkt_s("phone-wifi")), fmt_s(k / home6)])
    table(["item", "bytes", "packets", "crossings, n=20", "send, wifi phone", "send, home"], rows)
    h2("G.2 a person's own cost")
    rows = []
    for name, c, n in (("phone cellular, 1 shaped link", "phone-cellular", 1), ("phone wifi, 1 link", "phone-wifi", 1),
                       ("phone wifi, 8 links", "phone-wifi", 8), ("home, 8 links", "home", 8)):
        rows.append([name, f"{CLASS[c] * n * MONTH_S / GB:.1f}", f"{pkt_s(c) * n * 3600:,.0f}"])
    table(["node", "GB/mo each way", "real pkt/h ceiling"], rows)


# ---------------------------------------------------------------------------------------------
def share(s: float, h: float) -> float:
    return s / (s + h) if s + h else 0.0


def section_i() -> None:
    h1("I. What the conferred/unconferred split buys")
    core = 3 * seat_core(9, 3)
    h2("I.1 capacity with the cap and without it, nine seats, homes all owner-bound (D 4 capped, 6 uncapped)")
    rows = []
    per = person_crossings_day() / 86400
    for homes in (18, 100, 1000, 10000):
        dealt = deal_others(homes, 9)
        capped = core + theta({"home": dealt}, 4, {"home": 1.0})
        free = core + theta({"home": homes}, 6, {"home": 1.0})
        rows.append([homes, 27 if homes >= 18 else 9 + homes, homes + 9, f"{capped:.1f}", f"{free:,.1f}", f"{free / capped:.1f}x",
                     f"{capped / per:,.0f}", f"{free / per:,.0f}", f"{100 * dealt / homes:.2f}%"])
    table(["homes", "active capped", "active free", "Theta capped", "Theta free", "ratio", "persons capped", "persons free",
           "a home's share of hours"], rows)
    print(f"without seat links the cap holds {theta({'home': 18}, 4, {'home': 1.0}):.2f} crossings/s of home relays; the cap "
          f"is {100 * theta({'home': 18}, 4, {'home': 1.0}) / (core + theta({'home': 18}, 4, {'home': 1.0})):.0f}% homes, the rest is the seats' own class")

    print(f"a uniform route touches a conferred relay with P = {1 - (2 / 3) ** 3:.3f} (3 hops), {1 - (2 / 3) ** 6:.3f} (6 hops), "
          f"so the cap makes the seats a hop on most routes, a role beyond bootstrap and directory")

    h2("I.2 hostile share q of a route hop, Sybils S against H honest relays, seats honest")
    rows = []
    for h_n in (100, 1000, 10000):
        for s in (18, 100, 1000, 10000):
            f = share(s, h_n)
            q_cap = (2 / 3) * f
            rows.append([h_n, s, f"{f:.3f}", f"{q_cap:.3f}", f"{q_cap ** 2:.3f}", f"{q_cap ** 3:.4f}", f"{f ** 2:.3f}", f"{f ** 3:.4f}"])
    table(["H", "S", "f = S/(S+H) = q no cap", "q cap", "cap P(ends)", "cap P(all 3)", "no cap P(ends)", "no cap P(all 3)"], rows)

    h2("I.3 grinding: deal_hash(key_id, period) is public, so keys can be chosen for a period")
    rows = []
    for n in (100, 1000, 10000):
        slots = deal_others(n, 9)
        tries = n / slots
        rows.append([n, slots, f"{tries:.0f}", slots, "2/3", f"{8760 * slots:,}"])
    table(["honest others", "dealt others/period", "key tries per slot", "relays to fill a period", "q reached",
           "registered identities for a year of periods"], rows)

    h2("I.4 what a Sybil pays, per relay [assumption: $0.01/GB egress; $5/mo per public address]")
    gb = 2800 * 8 * MONTH_S / GB
    rows = [["listed only (row + hop key, no forwarding)", "0 GB", "$0", "dropped by the sender's liveness filter within a window"],
            ["one link answering", f"{2800 * MONTH_S / GB:.0f} GB", f"${2800 * MONTH_S / GB * 0.01:.2f}", "enough to pass liveness on one sender"],
            ["full home-class relay, 8 links", f"{gb:.0f} GB", f"${gb * 0.01:.2f}", "indistinguishable from an honest home"]]
    table(["behaviour", "egress/mo each way", "bandwidth $", "result"], rows)
    fold = 20_000
    rows = [[s, f"{fold * s / 1e6:,.0f} MB", f"{s * gb * 0.01:,.0f}"] for s in (1000, 10000, 100000)]
    table(["S relays", "added to every node's fold [assumption 20 KB row]", "$/mo full relays"], rows)

    h2("I.5 alternatives at S = 1,000 Sybil identities and $600/mo, H = 1,000 honest relays, per-hop q and route risk")
    h = 1000.0
    s = 1000.0
    b_adv = 600 / 0.01 / (2800 * 8 * MONTH_S / GB)   # relays' worth of real capacity the money buys
    f = share(s, h)
    hw = share(50, h)            # [assumption] $600/mo buys 50 attested devices over a year's budget
    age_fresh = share(s * 7 / 90, h)
    cap_q = 2 / 3 * f
    cap_ground = 2 / 3
    meas = share(min(s, b_adv), h)
    g = 0.05
    rows = [
        ["status quo: cap c=2, seats+conferred", f"{cap_q:.3f}", f"{cap_ground:.3f}", f"{cap_ground ** 2:.3f}", f"{cap_ground ** 3:.3f}", "yes: steward, seats"],
        ["no cap", f"{f:.3f}", f"{f:.3f}", f"{f ** 2:.3f}", f"{f ** 3:.3f}", "no"],
        ["one relay per owner", f"{f:.3f}", f"{f:.3f}", f"{f ** 2:.3f}", f"{f ** 3:.3f}", "no; owners are free"],
        ["+ hardware-attested owner", f"{hw:.3f}", f"{hw:.3f}", f"{hw ** 2:.3f}", f"{hw ** 3:.3f}", "to platform vendors"],
        ["identity age >= 90 d, fresh swarm at 7 d", f"{age_fresh:.3f}", f"{f:.3f}", f"{f ** 2:.3f}", f"{f ** 3:.3f}", "mild: witnessed time"],
        ["measured delivery, own probes", f"{meas:.3f}", f"{meas:.3f}", f"{meas ** 2:.3f}", f"{meas ** 3:.3f}", "no"],
        ["measured delivery, measuring authorities", f"{meas:.3f}", f"{meas:.3f}", f"{meas ** 2:.3f}", f"{meas ** 3:.3f}", "yes: measurers"],
        ["hash-assigned mimics alone (Tarzan)", f"{f:.3f}", f"{f:.3f}", f"{f ** 2:.3f}", f"{f ** 3:.3f}", "no"],
        ["contact graph, distance 2", f"{min(1, g * 8):.3f}", "-", f"{min(1, g * 8) ** 2:.3f}", f"{min(1, g * 8) ** 3:.3f}", "no; leaks contact graph"],
        [f"own contacts only (g = {g})", f"{g:.3f}", f"{g:.3f}", f"{g ** 2:.4f}", f"{g ** 3:.5f}", "no; small route set"],
        [f"RECOMMENDED guard from contacts (g = {g}) + fold q", f"{g:.3f}/{meas:.3f}", f"{g:.3f}/{f:.3f}", f"{g * meas:.3f}", f"{g * meas ** 2:.4f}", "no; seat is last resort only"],
    ]
    table(["rule", "q expected", "q worst", "P(ends)", "P(all 3)", "recentralises?"], rows)
    print(f"money buys {b_adv:,.0f} full relays of real capacity, so a bought-capacity rule still admits S = {min(s, b_adv):,.0f}; "
          f"honest capacity is {h * 2800 * 8 / 1e6:.1f} MB/s")

    h2("I.6 the recommended rule across Sybil budgets and hostile-contact shares: P(ends) = g x q, P(all 3) = g x q^2")
    rows = []
    for g2 in (0.0, 0.05, 0.2, 1.0):
        for s2 in (1000, 10000, 100000):
            q = share(s2, 1000)
            rows.append([g2, s2, f"{q:.3f}", f"{g2 * q:.3f}", f"{g2 * q * q:.3f}"])
    table(["g", "S", "q", "P(ends)", "P(all 3)"], rows)
    h2("I.7 Sybils that drop: a packet over five fold hops survives (1-q)^5; own probes remove droppers at rate pi")
    rows = []
    for q in (0.1, 0.5, 0.9):
        rows.append([q, f"{100 * (1 - q) ** 5:.1f}%", f"{100 * (1 - q * 0.1) ** 5:.1f}%"])
    table(["q dropping", "no filter", "probes catch 90%"], rows)
    print("g is per sender and does not move with S: minted identities are no one's contacts. g = 1 is the person "
          "whose only relay contact is hostile; the seat as last-resort guard gives g = hostile share of seats")


def main() -> None:
    print("CIRIS rooms over the onion tier (seed %d)" % SEED)
    section_a()
    section_a_routes()
    section_b()
    section_c()
    section_d()
    section_e()
    section_f()
    section_g()
    section_i()


if __name__ == "__main__":
    main()
