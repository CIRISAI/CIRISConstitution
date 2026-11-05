# FSD — Transport tiers and canonical homing: a quantitative model

**Status:** model, not a measurement. Every number below is produced by
`tools/models/transport_tiers.py` (`python3 -I tools/models/transport_tiers.py`, standard library,
seeded, no network, no cargo); the tables here are that script's output of 2026-11-04 pasted
verbatim. **Direction:** Eric, 2026-11-04 (CIRISEdge#935, CIRISConstitution#200): "make sure we
always shape with shaped peers"; three tiers, slow shaped / fast shaped / unshaped; three canonicals
near term and nine planned; "rotate through who participates in cycles as we scale, and make sure
all of the canonical community servers are being utilized"; the canonical is the peer of last
resort. **Sources, in order of authority:** CC 5.4.3 (rc16) link shaping and fragmentation, CC 5.4.6
(the Anonymous Tier deal, items 1 and 5; the forwarder paragraphs), `docs/LINK_SHAPING_COST.md` and
`src/transport/link_shaping.rs` on branch `feat/onion-v44`, `src/replication/runtime.rs`
(`BOOTSTRAP_ROUND_PLANES`), `src/replication/session.rs` (`MAX_DELIVER_ENVELOPE_BYTES`),
`FSD/CIRIS_MESH.md` (the relay order, §6.2 canonical capacity assumptions, §6.4 V1/V2).

**[inf]** marks an inference not checked by running code. **[assumption]** marks a parameter the
brief did not supply; §7 lists every one. No time estimates are made anywhere in this document.

The one sentence: **a shaped link costs a fixed slot at the full class rate, a node has L = 8 of
them, and everything past the bound is refused to the unshaped bulk plane; so what decides a
canonical's health is which few peers hold its slots, and the homing rule, the seat class and the
relay order all exist to make that the last-resort standing set and nothing else.**

---

## 0. The rulings this model takes as given

1. **The cap divides; there is no floor** (Eric 2026-11-04; CC 5.4.3 item 1: "the link runs at the
   lower of the two offers, and a node divides a node-wide cap across its shaped links"; "a node's
   shaped links together use at most eight links' worth of its class budget"). The per-link share is
   cap ÷ shaped links and the sum never exceeds the cap. `docs/LINK_SHAPING_COST.md` and
   `MIN_LAMBDA = 0.1` in `link_shaping.rs` on `feat/onion-v44` still describe a 0.1 frame/s floor
   that can carry the total past the cap; this model follows the ruling and CC#200 Q4 asks the CC to
   confirm it. **[inf]** the floor is removed in v44 as CC#200 states.
2. **Three tiers.** Slow shaped: the divided cap, every ordinary peer that offers a class. Fast
   shaped: the proposed `seat` class, between two serve seats only, its own budget outside the cap,
   2 frames/s proposed (CC#200, pending). Unshaped: bulk over 64 KiB (`SHAPED_ROW_MAX_BYTES`), bulk
   by kind, live media (CC 5.4.3 "two planes").
3. **Canonical homing** (CIRISEdge#935): each node ranks the M canonicals by
   `H(node ‖ canonical ‖ period)`, homes on the top k = 2, rehashes each period, keeps the rest as an
   ordered fallback. Canonicals keep a full mesh among themselves.
4. **Onion is not pairwise** (CC 5.4.6 items 1, 5). The publisher opts in, the deal assigns relays
   from the fold, and onion packets are the bodies of ordinary shaped frames. There is no
   "onion with onion peers" negotiation: a relay's layer links are shaped links like any other and
   simply count toward the divided cap. The model therefore has no onion-specific term; a relay's
   layer links appear in N.
5. **BoundedWithFloor is the default** (Eric, later on 2026-11-04, ruling on this document's Q8,
   verbatim: "we shape with shaped peers if possible, otherwise refuse and offer unshaped (bulk
   transfers) if available"). L = `NODE_CAP_LINKS` (8) minus the layer reserve
   (`DEFAULT_LAYER_RESERVE_LINKS` = 4, held out while the Anonymous Tier runs) shaped links, each at
   the full class rate; at the bound a further shaping peer's row link is refused
   (`link_shaping_home_elsewhere`) and the peer homes elsewhere; an unshaped bulk link is still
   offered. **The accepted trade-off:** a refused peer's bulk link is a visible spill (§9.1's second
   leak, a mode an observer can see); Eric chose it over the floorless divide's N leak and minutes
   of latency. The bounded arm is the primary case of A, D and E below (§3.0, §6.0, §7.0); the
   floorless tables stay as the sensitivity arm and as the cost of any link beyond the bound.

---

## 1. Constants and where each comes from

| Symbol | Value | Source |
|---|---|---|
| F, shaped frame | 16,272 B | the link MDU on loopback/TCP, measured (#805 item 8 notes; `FSD/CIRIS_MESH.md` §6.2) |
| per-link `server` rate | 7,000 B/s | `link_shaping.rs` `BudgetClass::default_bytes_per_s`; CC 5.4.3 table |
| node cap | 56,000 B/s = 8 × 7,000 | `link_shaping.rs` `NODE_CAP_LINKS = 8`; CC 5.4.3 |
| ρ, W | 0.5, 600 s | CC 5.4.3 fleet defaults (`server`) |
| class costs per link per month each way | server 18.1 GB, home 7.3, phone-wifi 3.6, phone-cellular 0.9; ×8 at the cap: 145 / 58 / 29 / 7.3 | `docs/LINK_SHAPING_COST.md`, `FLEET_DEFAULTS` |
| one message per frame | today's shaper | being measured; both modes modelled |
| replication round | Summary → Summary → Diff → Deliver, 4 messages, 2 per direction | the brief (from the code) |
| round interval / per-wait timeout | 30 s / 15 s | the brief (from the code) |
| bootstrap planes per canonical peer | 5 | `runtime.rs` `BOOTSTRAP_ROUND_PLANES` (Key, IdentityOccurrence, TransportDestination, Revocation, IdentityOccurrenceRevocation) |
| rows per plane per round; Deliver cap | ≤ 1,024; ≤ 512 KiB | `bridge.rs` `DEFAULT_SWEEP_PAGE_ROWS`; `session.rs` `MAX_DELIVER_ENVELOPE_BYTES` |
| shaped row max | 64 KiB, above it the bulk plane | `link_shaping.rs` `SHAPED_ROW_MAX_BYTES` |
| frame payload | 16,248 B **[inf]** (8 B header + 16 B tag) | `FRAME_HEADER_LEN`; so a 64 KiB Deliver is 5 frames |
| canonical host | 4 vCPU, 8 GB, 4,096 GB/month egress, ~215 GB/month used | the brief (Vultr) |
| Poisson timing | the mean wait for a queued row ≈ one frame gap; worst case unbounded | CC 5.4.3 item 3 |

---

## 2. The model

**Slow shaped.** With N shaped peers on a server: per-link rate r = cap/N, frame rate λ = r/F,
gap g = 1/λ = F·N/cap = 0.29 s × N. A row that arrives at a random moment waits for the link's next
Poisson tick, Exp(λ): mean g, p95 g·ln 20 ≈ 3.0 g, p99 g·ln 100 ≈ 4.6 g, no bound. A chain of j
sequential waits is Erlang(j, λ): mean j·g. A round is a request/reply pair twice, so one wait as
the requester sees it is Erlang-2 (its own tick, then the responder's) if the timer starts at
enqueue, or Exp(λ) if it starts when the frame leaves; both are shown.

**The ρ budget.** A window of W admits ceil(ρ·λ·W) real frames per link per direction (CC 5.4.3;
`Agreement::reach_frames`). Rounds that ask more than that are throttled by W, not by the timer.
Sustained real throughput per link is ρ·r.

**One message per frame vs coalescing.** Today each message takes at least one frame, so a round
over the five bootstrap planes costs 2 × 5 = 10 real frames per direction and, if the planes'
messages queue behind each other, up to 20 sequential ticks. Coalescing (several control messages
of 200 B–2 KB in one 16 KB frame) costs 2 frames per direction and 4 ticks. Neither changes the
wait of a single row (still one gap); coalescing removes the queueing term. A 64 KiB Deliver is
5 fragment frames in both modes (fragmentation is not coalescing).

**Fast shaped.** Rate f frames/s per seat link, own budget. Cost per link each way = f·F·2,592,000 s.
A server in a full mesh of M seats has M − 1 seat links.

**Homing.** Load per canonical = N·k/M in expectation; balance is binomial. A node loses every
top-k home only when all k are down: C(f, k)/C(M, k) for f failures. With the ordered fallback the
survivors carry N·k/(M − f). At a period roll a node's new top-k is an independent draw, so a seat
receives N·(k/M)(1 − k/M) new dials.

**Peer of last resort.** Only an open shaped link costs anything, and it costs the same idle or
busy, so the quantity is open shaped links, not rounds. Links opened for a home round feed back
into the gap (a round takes 4 waits at the gap of the moment). By Little's law the open links
satisfy P = S + P·θ/T_home with θ = 4·F·(N·k/M)·p_shaped/cap, so P = S/(1 − θ/T_home) and a home
cadence T_home ≤ θ does not converge.

---

## 3. A. Slow shaped, one server

### 3.0 Under the bound (primary)

```text
-- H.1 the per-link figures are N-independent (this is A under the bound)
 L                      case  B/s link  gap = mean wait    p99  frames/W  both waits <=15s (coalesced)  round <=30s (coalesced)  both waits (1/frame x5)  round (1/frame x5)  send = receive cap B/s  GB/mo each way
--  ------------------------  --------  ---------------  -----  --------  ----------------------------  -----------------------  -----------------------  ------------------  ----------------------  --------------
 8            ruled, no tier     7,000             2.3s  10.7s       130                         97.7%                    99.9%                     1.4%                4.0%                  56,000             145
 4  ruled, tier reserve held     7,000             2.3s  10.7s       130                         97.7%                    99.9%                     1.4%                4.0%                  28,000              73
16               sensitivity     3,500             4.6s  21.4s        65                         69.3%                    88.5%                     0.0%                0.0%                  56,000             145
reading: with every shaped link at 7,000 B/s the round constants hold coalesced (97.7% / 99.9%) and still fail one-per-frame with 5 planes (12% / 4%): coalescing and lambda-derived timeouts stay recommended. The bound caps RECEIVE as well as send: a peer's link to this node is one of its L, so shaped ingress <= L x 7,000 B/s = 56,000 B/s, 145 GB/month; Q5 is moot for shaped links (bulk links were never shaped and are the service ladder's to bound)
```

**Reading.** With L fixed, every slow-shaped link runs at 7,000 B/s whatever the peer count: gap and
mean row wait 2.3 s, p99 10.7 s, 130 real frames per window, 3,500 B/s real. The round constants
hold coalesced (97.7 % of request/reply pairs inside 15 s, 99.9 % of rounds inside 30 s) and still
fail one-per-frame with five planes (1.4 % / 4 %), so coalescing and λ-derived timeouts remain the
recommendation; the λ-derivation is now cheap because λ is a class constant. With the layer reserve
held, L = 4 and the figures per link are unchanged. The sensitivity row L = 16 (3,500 B/s) already
drops the pair success to 69 %. **Ingress:** a peer's link to this node is one of its L slots in
both directions, so shaped ingress ≤ L × 7,000 B/s = 56,000 B/s, 145 GB/month each way, the same
as egress; Q5 (§10) no longer needs the CC for shaped links. Bulk links were never shaped and their
ingress is the service ladder's to bound (mesh FSD §7).

### 3.1 The floorless arm (sensitivity; what each link beyond the bound would cost)

```text
frame 16272 B, node cap 56000 B/s = 8 x 7000 B/s, rho 0.5, W 600 s; one message per frame today, 5 bootstrap planes
per-link rate = cap / N; gap = F / rate; a row that arrives at random waits Exp(lam): mean = gap, p95 = gap*ln 20, p99 = gap*ln 100; worst case unbounded

-- A.1 rate, gap, row wait, real budget per link
   N  B/s link  frames/s    gap  mean wait    p95    p99  real B/s  frames/W  real MB/day
----  --------  --------  -----  ---------  -----  -----  --------  --------  -----------
   8     7,000    0.4302   2.3s       2.3s   7.0s  10.7s     3,500       130       302.40
  34     1,647    0.1012   9.9s       9.9s  29.6s  45.5s       824        31        71.15
 100       560    0.0344  29.1s      29.1s  87.0s   2.2m       280        11        24.19
 300       187    0.0115  87.2s      87.2s   4.4m   6.7m        93         4         8.06
1000        56    0.0034   4.8m       4.8m  14.5m  22.3m        28         2         2.42

-- A.2 does a round complete? request+reply = 2 waits (Erlang-2) against the 15 s per-wait timeout; whole round = 4 waits coalesced, or 4 x 5 planes one-per-frame (Erlang-20) against the 30 s interval
   N  P(wait<=15s)  ..timer at departure  ..last of 5 planes 1/frame  P(both waits)  P(round<=30s) coalesced  P(round<=30s) 1/frame  verdict coalesced  verdict 1/frame
----  ------------  --------------------  --------------------------  -------------  -----------------------  ---------------------  -----------------  ---------------
   8         98.8%                 99.8%                       11.9%          97.7%                    99.9%                  4.02%             viable       NOT viable
  34         44.8%                 78.1%                        0.0%          20.1%                    36.1%                  0.00%         NOT viable       NOT viable
 100          9.5%                 40.3%                        0.0%           0.9%                     2.1%                  0.00%         NOT viable       NOT viable
 300          1.3%                 15.8%                        0.0%           0.0%                     0.0%                  0.00%         NOT viable       NOT viable
1000          0.1%                  5.0%                        0.0%           0.0%                     0.0%                  0.00%         NOT viable       NOT viable

-- A.3 the rho budget: real frames a window admits vs what 30 s rounds ask (per direction)
one-per-frame: 2 messages x 5 planes = 10 frames per round; coalesced: 2 frames per round (a 64 KiB Deliver adds 5 fragment frames either way)
   N  frames/W  rounds asked/W  rounds/W 1/frame  rounds/W coalesced  min interval 1/frame  min interval coalesced  64 KiB Deliver (5 ticks)
----  --------  --------------  ----------------  ------------------  --------------------  ----------------------  ------------------------
   8       130              20              13.0                65.0                 46.2s                    9.2s                     11.6s
  34        31              20               3.1                15.5                  3.2m                   38.7s                     49.4s
 100        11              20               1.1                 5.5                  9.1m                    1.8m                      2.4m
 300         4              20               0.4                 2.0                 25.0m                    5.0m                      7.3m
1000         2              20               0.2                 1.0                 50.0m                   10.0m                     24.2m

-- A.4 max shaped peers per server for a mean row wait target (mean wait = one gap = F*N/cap)
mean wait target  max N  B/s link at max N  frames/W  real B/s
----------------  -----  -----------------  --------  --------
            5.0s     17              3,294        61     1,647
           30.0s    103                544        11       272
            5.0m   1032                 54         2        27
coalescing does not move these: a row still waits for the next tick. It removes the queueing term (q rows ahead cost q more ticks one-per-frame, ~0 coalesced while they fit a frame)

-- A.5 what timeout and interval make rounds viable (95th percentile), and the rho-bound interval
   N  per-wait timeout  interval p95 coalesced  interval p95 1/frame  rho-bound interval coalesced  rho-bound 1/frame  => interval coalesced  => interval 1/frame
----  ----------------  ----------------------  --------------------  ----------------------------  -----------------  ---------------------  -------------------
   8             11.0s                   18.0s                 64.8s                          9.3s              46.5s                  18.0s                64.8s
  34             46.9s                   76.6s                  4.6m                         39.5s               3.3m                  76.6s                 4.6m
 100              2.3m                    3.8m                 13.5m                          1.9m               9.7m                   3.8m                13.5m
 300              6.9m                   11.3m                 40.5m                          5.8m              29.1m                  11.3m                40.5m
1000             23.0m                   37.5m                  2.3h                         19.4m               1.6h                  37.5m                 2.3h
fixed 15 s / 30 s constants hold at the 95th percentile only up to N = 10 (timeout) and N = 13 (interval). Scaling rule: timeout = 4.74 x gap, interval = max(7.75 x gap, 2 frames / (rho * lam) = 4 x gap)
```

**Reading.** The row wait is the gap: 2.3 s at 8 peers, 29 s at 100, 4.8 min at 1,000. The p99 is
4.6 gaps. The real budget collapses with N: at 1,000 peers a window admits 2 real frames and a link
carries 28 B/s of real traffic, 2.4 MB/day.

```text
-- A.2 does a round complete? request+reply = 2 waits (Erlang-2) against the 15 s per-wait timeout; whole round = 4 waits coalesced, or 4 x 5 planes one-per-frame (Erlang-20) against the 30 s interval
   N  P(wait<=15s)  ..timer at departure  ..last of 5 planes 1/frame  P(both waits)  P(round<=30s) coalesced  P(round<=30s) 1/frame  verdict coalesced  verdict 1/frame
----  ------------  --------------------  --------------------------  -------------  -----------------------  ---------------------  -----------------  ---------------
   8         98.8%                 99.8%                       11.9%          97.7%                    99.9%                  4.02%             viable       NOT viable
  34         44.8%                 78.1%                        0.0%          20.1%                    36.1%                  0.00%         NOT viable       NOT viable
 100          9.5%                 40.3%                        0.0%           0.9%                     2.1%                  0.00%         NOT viable       NOT viable
 300          1.3%                 15.8%                        0.0%           0.0%                     0.0%                  0.00%         NOT viable       NOT viable
1000          0.1%                  5.0%                        0.0%           0.0%                     0.0%                  0.00%         NOT viable       NOT viable
```

**Where rounds are not viable.** With the fixed 15 s / 30 s constants, coalesced rounds are viable
only at the 8-link cap (97.7 % of request/reply pairs inside the timeout, 99.9 % of rounds inside
the interval) and fail two thirds of the time at 34 peers. With one message per frame and five
planes queued, even 8 peers fail: the fifth plane's request/reply pair meets its timeout 12 % of
the time and the round lands inside 30 s 4 % of the time.

```text
-- A.3 the rho budget: real frames a window admits vs what 30 s rounds ask (per direction)
one-per-frame: 2 messages x 5 planes = 10 frames per round; coalesced: 2 frames per round (a 64 KiB Deliver adds 5 fragment frames either way)
   N  frames/W  rounds asked/W  rounds/W 1/frame  rounds/W coalesced  min interval 1/frame  min interval coalesced  64 KiB Deliver (5 ticks)
----  --------  --------------  ----------------  ------------------  --------------------  ----------------------  ------------------------
   8       130              20              13.0                65.0                 46.2s                    9.2s                     11.6s
  34        31              20               3.1                15.5                  3.2m                   38.7s                     49.4s
 100        11              20               1.1                 5.5                  9.1m                    1.8m                      2.4m
 300         4              20               0.4                 2.0                 25.0m                    5.0m                      7.3m
1000         2              20               0.2                 1.0                 50.0m                   10.0m                     24.2m
```

**The ρ bound is the harder one.** A 30 s cadence asks 20 rounds per window. One message per frame
affords 13 at 8 peers and 1.1 at 100; coalesced, 65 at 8 and 5.5 at 100. At 1,000 peers a link
affords one coalesced round per window (10 min) and one one-per-frame round per 50 min, and a
64 KiB Deliver takes 24 min of ticks.

```text
-- A.4 max shaped peers per server for a mean row wait target (mean wait = one gap = F*N/cap)
mean wait target  max N  B/s link at max N  frames/W  real B/s
----------------  -----  -----------------  --------  --------
            5.0s     17              3,294        61     1,647
           30.0s    103                544        11       272
            5.0m   1032                 54         2        27
coalescing does not move these: a row still waits for the next tick. It removes the queueing term (q rows ahead cost q more ticks one-per-frame, ~0 coalesced while they fit a frame)
```

```text
-- A.5 what timeout and interval make rounds viable (95th percentile), and the rho-bound interval
   N  per-wait timeout  interval p95 coalesced  interval p95 1/frame  rho-bound interval coalesced  rho-bound 1/frame  => interval coalesced  => interval 1/frame
----  ----------------  ----------------------  --------------------  ----------------------------  -----------------  ---------------------  -------------------
   8             11.0s                   18.0s                 64.8s                          9.3s              46.5s                  18.0s                64.8s
  34             46.9s                   76.6s                  4.6m                         39.5s               3.3m                  76.6s                 4.6m
 100              2.3m                    3.8m                 13.5m                          1.9m               9.7m                   3.8m                13.5m
 300              6.9m                   11.3m                 40.5m                          5.8m              29.1m                  11.3m                40.5m
1000             23.0m                   37.5m                  2.3h                         19.4m               1.6h                  37.5m                 2.3h
fixed 15 s / 30 s constants hold at the 95th percentile only up to N = 10 (timeout) and N = 13 (interval). Scaling rule: timeout = 4.74 x gap, interval = max(7.75 x gap, 2 frames / (rho * lam) = 4 x gap)
```

**What makes rounds viable.** Derive the timeout and the interval from the link's agreed λ instead
of constants: per-wait timeout ≈ 4.74 gaps (Erlang-2 at the 95th percentile), round interval ≥
7.75 gaps coalesced (Erlang-4 p95; this already exceeds the ρ-bound 4 gaps) or 26.9 gaps one per
frame. At 100 peers that is a 2.3 min timeout and a 3.8 min interval coalesced; at 1,000, 23 min and
38 min. The constants hold at the 95th percentile only up to N = 10 (timeout) and N = 13 (interval).

**Recommendation A.** (1) Coalesce: it multiplies the affordable round rate by five and takes the
round from 20 ticks to 4. (2) Make `WAIT_TIMEOUT` and `ROUND_INTERVAL` functions of the agreement's
λ on shaped links (timeout = 5 gaps, interval = 8 gaps, floors at today's 15 s / 30 s), so a shaped
peer never times out for being shaped; under the bound λ is a class constant, so this is cheap.
(3) The shaped-link count is bounded by ruling 5 (L = 8 at the class rate, refuse and offer bulk
past it), which is the shape the prior art supports (§9.1, Tarzan κ ≈ 2k, Herd 2–3); keep L at 8,
not 16, since the sensitivity row already drops the pair success inside the timeout to 69 %. The
floorless figures (29 s at 100 peers, 5 min at 1,000) are what any link past the bound would have
cost and why the refusal is the better answer; the N leak of §9.1 is closed by the bound, and the
visible spill is the accepted price (§0 ruling 5).

---

## 4. B. Fast shaped: the `seat` class

```text
own budget outside the divided cap; full mesh among M seats = M-1 links per server; egress base = today 215 GB + slow-shaped cap 145 GB each way (cover fills the cap whatever the load); quota 4096 GB/month. Ingress assumed unmetered [assumption: Vultr bills egress]
frames/s  KB/s link  GB/mo link   gap  round mean  p99 wait  real KB/s  64 KiB  M=3 seat GB  M=3 total  M=3 quota  M=9 seat GB  M=9 total  M=9 quota
--------  ---------  ----------  ----  ----------  --------  ---------  ------  -----------  ---------  ---------  -----------  ---------  ---------
       1       16.3          42  1.0s        4.0s      4.6s        8.1    5.0s           84        445        11%          337        698        17%
       2       32.5          84  0.5s        2.0s      2.3s       16.3    2.5s          169        529        13%          675       1035        25%
       5       81.4         211  0.2s        0.8s      0.9s       40.7    1.0s          422        782        19%         1687       2047        50%
      10      162.7         422  0.1s        0.4s      0.5s       81.4    0.5s          844       1204        29%         3374       3734        91%

-- B.2 headroom at M = 27 (the onion tier's 3 layers x 9 at some later scale) [projection]
frames/s  M=27 seat GB  total  quota
--------  ------------  -----  -----
       1          1097   1457    36%
       2          2193   2553    62%
       5          5483   5843   143%
```

**Reading.** Cost scales linearly with the rate and with M − 1. At 2 frames/s a seat link costs
84 GB/month each way; nine seats cost a server 675 GB of seat egress, 1,035 GB with today's usage
and the slow cap, 25 % of the quota. At 10 frames/s and nine seats it is 91 %. Latency between
seats is sub-second at every rate: a 4-wait round means 2 s at 2 frames/s, a 64 KiB Deliver 2.5 s.
The real budget at 2 frames/s is 16 KB/s per link, which is 4.7× the slow tier's full per-link rate.

**Recommendation B.** 2 frames/s, as CC#200 proposes. It keeps nine seats at a quarter of the quota
and 27 seats (the onion tier's three layers of nine, should the fleet get there) at 62 %; 5 frames/s
does not survive 27 seats. The 1 frame/s option saves 8 % of quota at M = 9 for twice the round
time and is not worth it. Raise to 5 frames/s only on a measured inter-seat backlog at M ≤ 9.

---

## 5. C. Rotation vs Poisson

```text
node-wide frame rate 3.441 frames/s in every scheme; per-link mean gap = N / 3.441
analytic: Poisson per link -> wait Exp(lam): mean g, p99 4.6 g, no bound; fixed slots -> wait U(0,g): mean g/2, bound g; dealt node-Poisson -> per-link gaps Erlang(N): mean g(1+1/N)/2, p99 ~ g, no hard bound but tail ~ exp(-N)
   N   scheme  gap g  mean wait    p95    p99  max (sim)  max/g
----  -------  -----  ---------  -----  -----  ---------  -----
   8  poisson   2.3s       2.4s   7.2s  11.2s      27.9s  11.99
   8    fixed   2.3s       1.2s   2.2s   2.3s       2.3s   1.00
   8    dealt   2.3s       1.3s   3.0s   3.9s       6.8s   2.93
  34  poisson   9.9s      10.1s  30.5s  46.8s      80.4s   8.14
  34    fixed   9.9s       5.0s   9.4s   9.8s       9.9s   1.00
  34    dealt   9.9s       5.1s  10.4s  12.2s      16.4s   1.66
 100  poisson  29.1s      30.5s  93.0s   2.3m       3.9m   8.00
 100    fixed  29.1s      14.6s  27.6s  28.7s      29.1s   1.00
 100    dealt  29.1s      14.7s  28.6s  31.8s      38.2s   1.31
1000  poisson   4.8m       4.7m  15.1m  23.5m      28.6m   5.92
1000    fixed   4.8m       2.4m   4.6m   4.8m       4.8m   1.00
1000    dealt   4.8m       2.4m   4.6m   4.9m       5.2m   1.08

-- C.2 what a passive observer of the wire learns (the CC question, CC#200 Q3)
            scheme                                                         from one link                                                                   across a node's links                                                       status
------------------  --------------------------------------------------------------------  --------------------------------------------------------------------------------------  -----------------------------------------------------------
  Poisson per link  rate lam over many frames (hence N, given the class; conceded today)                                         none: links of one node are independent streams                       CC 5.4.3 item 3 names it; ships in v44
       fixed slots                 N exactly from 2 frames; phase; the instant N changes   yes: two links of one node interleave exactly and never coincide (a node fingerprint)                not the Poisson timer 5.4.3 names; needs text
dealt node-Poisson                rate, and N also from the gap variance (CV = 1/sqrt N)  weak: coincidences never happen on one node's links (same fingerprint, slower to read)  node-wide stream is Poisson; per-link is Erlang; needs text
```

**Reading.** At the same node-wide rate, fixed slots halve the mean wait and bound the worst case
at exactly one gap; dealt node-Poisson gets the same mean with a soft bound (1.1–1.7 gaps at the
sim's max for N ≥ 34, 2.9 at N = 8); independent Poisson per link, what v44 ships, has a p99 of
4.6 gaps and a sim max of 6–12 gaps.

```text
-- C.2 what a passive observer of the wire learns (the CC question, CC#200 Q3)
            scheme                                                         from one link                                                                   across a node's links                                                       status
------------------  --------------------------------------------------------------------  --------------------------------------------------------------------------------------  -----------------------------------------------------------
  Poisson per link  rate lam over many frames (hence N, given the class; conceded today)                                         none: links of one node are independent streams                       CC 5.4.3 item 3 names it; ships in v44
       fixed slots                 N exactly from 2 frames; phase; the instant N changes   yes: two links of one node interleave exactly and never coincide (a node fingerprint)                not the Poisson timer 5.4.3 names; needs text
dealt node-Poisson                rate, and N also from the gap variance (CV = 1/sqrt N)  weak: coincidences never happen on one node's links (same fingerprint, slower to read)  node-wide stream is Poisson; per-link is Erlang; needs text
```

**The CC question** (CC#200 Q3). CC 5.4.3 item 3 names "a per-link Poisson timer at the negotiated
rate λ". What the timer protects is that frame emission is independent of real arrivals, and every
scheme above has that property; inside one link the three are indistinguishable to the peer and to
the wire. What differs is what one node's set of links says about the node. Under the divided cap
the rate λ already reveals the node's shaped-link count to a patient observer (the cost doc concedes
"shows only each sender's link count"); fixed slots give it away from two frames, with phase, and
make the links of one node linkable (they interleave exactly, never coincide). Dealt node-Poisson
leaks the same count through the gap variance and the same never-coincide fingerprint, more slowly.
The question for the CC is whether 5.4.3 item 3 binds the per-link process (then only independent
Poisson is admissible) or the node's emission process (then a node-wide Poisson stream dealt
round-robin is admissible, and the cross-link fingerprint is the price).

**Recommendation C.** Ship independent Poisson (as planned) and keep it: by Loopix's merging
property it is the one scheme whose uplink hides N (§9.3). Slots are worth asking the CC about only
for the worst-case bound and the slot-visible drop (§9.4); if the CC admits a node-level process,
dealt node-Poisson gives slots' mean with a Poisson uplink but keeps the never-coincide fingerprint.

---

## 6. D. Canonical homing: rendezvous k of M

### 6.0 Under the bound (primary)

```text
-- H.2 homing under the bound (D recomputed): a seat has L shaped home slots; the rest are refused and spill to an unshaped bulk link, a visible spill, the trade-off Eric accepted
    N  M   L  p_shaped  shaped homes wanted/seat  shaped slots  served shaped  spilled to bulk/seat  fleet shaped slots  slots per shaping node
-----  -  --  --------  ------------------------  ------------  -------------  --------------------  ------------------  ----------------------
 1000  3   8       0.1                        67             8          12.0%                    59                  24                   0.240
 1000  3   8       1.0                       667             8           1.2%                   659                  24                   0.024
 1000  3   4       0.1                        67             4           6.0%                    63                  12                   0.120
 1000  3   4       1.0                       667             4           0.6%                   663                  12                   0.012
 1000  3  16       0.1                        67            16          24.0%                    51                  48                   0.480
 1000  3  16       1.0                       667            16           2.4%                   651                  48                   0.048
 1000  9   8       0.1                        22             8          36.0%                    14                  72                   0.720
 1000  9   8       1.0                       222             8           3.6%                   214                  72                   0.072
 1000  9   4       0.1                        22             4          18.0%                    18                  36                   0.360
 1000  9   4       1.0                       222             4           1.8%                   218                  36                   0.036
 1000  9  16       0.1                        22            16          72.0%                     6                 144                   1.440
 1000  9  16       1.0                       222            16           7.2%                   206                 144                   0.144
10000  3   8       0.1                       667             8           1.2%                   659                  24                   0.024
10000  3   8       1.0                      6667             8           0.1%                  6659                  24                   0.002
10000  3   4       0.1                       667             4           0.6%                   663                  12                   0.012
10000  3   4       1.0                      6667             4           0.1%                  6663                  12                   0.001
10000  3  16       0.1                       667            16           2.4%                   651                  48                   0.048
10000  3  16       1.0                      6667            16           0.2%                  6651                  48                   0.005
10000  9   8       0.1                       222             8           3.6%                   214                  72                   0.072
10000  9   8       1.0                      2222             8           0.4%                  2214                  72                   0.007
10000  9   4       0.1                       222             4           1.8%                   218                  36                   0.036
10000  9   4       1.0                      2222             4           0.2%                  2218                  36                   0.004
10000  9  16       0.1                       222            16           7.2%                   206                 144                   0.144
10000  9  16       1.0                      2222            16           0.7%                  2206                 144                   0.014
a seat down loses its L slots and the survivors cannot absorb them (they are full); the homed nodes beyond the slots were already on bulk links, so the failover stampede of D.4 is unchanged in dials but changes nothing about shaping. A period roll cannot move a slot holder: the new home is full and refuses, make-before-break keeps the old, so under the bound rotation churns refusals, not slots
```

**Reading.** A seat has L = 8 shaped home slots (4 with the tier reserve), so homing's N·k/M no
longer sets a shaped load; it sets how many nodes are refused. At 1,000 nodes and 9 seats with a
tenth of nodes shaping, 8 of the 22 shaped homes a seat is asked for are served and 14 spill to bulk
(36 %); at 10,000 nodes 0.4–3.6 %. The fleet holds M·L = 72 shaped canonical slots at nine seats,
0.007–0.07 per shaping node. A seat down loses its L slots and full survivors cannot absorb them; the
failover stampede of D.4 is the same in dials, since the refused nodes were already on bulk links.
A period roll cannot move a slot holder (the new home is full and refuses; make-before-break keeps
the old), so under the bound rotation churns refusals, not slots: the rotation question (Q9) is
about the fallback order and exposure, not load.

### 6.1 The floorless arm (sensitivity)

```text
-- D.1 per-server load and balance (today: every node peers with every canonical)
    N  M  k  today/server  mean homed    max    min  max/mean
-----  -  -  ------------  ----------  -----  -----  --------
 1000  3  1          1000         333    360    315     1.080
 1000  3  2          1000         667    676    649     1.014
 1000  3  3          1000        1000   1000   1000     1.000
 1000  9  1          1000         111    117     91     1.053
 1000  9  2          1000         222    235    214     1.057
 1000  9  3          1000         333    352    317     1.056
10000  3  1         10000        3333   3389   3267     1.017
10000  3  2         10000        6667   6726   6567     1.009
10000  3  3         10000       10000  10000  10000     1.000
10000  9  1         10000        1111   1150   1070     1.035
10000  9  2         10000        2222   2323   2160     1.045
10000  9  3         10000        3333   3445   3264     1.033
analytic: mean = N k / M; max/mean -> 1 as N grows (binomial spread sqrt(M/(N k)))
```

**Reading.** Homing replaces "every node on every canonical" (N per server) with N·k/M: 667 per
server at 1,000 nodes and 3 canonicals with k = 2, 222 at 9; 2,222 at 10,000 nodes and 9
canonicals. The busiest server is within 1–8 % of the mean, closer as N grows.

```text
-- D.2 one and two canonicals down: nodes with no live home; survivors' load (fallback to next in rank)
    N  M  k  down  lost all top-k (sim)  C(f,k)/C(M,k)  busiest survivor  M/(M-f)
-----  -  -  ----  --------------------  -------------  ----------------  -------
 1000  3  1     1                 36.0%          33.3%             1.55x    1.50x
 1000  3  1     2                 67.5%          66.7%             3.00x    3.00x
 1000  3  2     1                  0.0%           0.0%             1.50x    1.50x
 1000  3  2     2                 35.1%          33.3%             1.50x    3.00x
 1000  3  3     1                  0.0%           0.0%             1.00x    1.50x
 1000  3  3     2                  0.0%           0.0%             1.00x    3.00x
 1000  9  1     1                 11.5%          11.1%             1.19x    1.12x
 1000  9  1     2                 23.1%          22.2%             1.35x    1.29x
 1000  9  2     1                  0.0%           0.0%             1.17x    1.12x
 1000  9  2     2                  3.2%           2.8%             1.35x    1.29x
 1000  9  3     1                  0.0%           0.0%             1.16x    1.12x
 1000  9  3     2                  0.0%           0.0%             1.32x    1.29x
10000  3  1     1                 33.9%          33.3%             1.53x    1.50x
10000  3  1     2                 67.3%          66.7%             3.00x    3.00x
10000  3  2     1                  0.0%           0.0%             1.50x    1.50x
10000  3  2     2                 34.3%          33.3%             1.50x    3.00x
10000  3  3     1                  0.0%           0.0%             1.00x    1.50x
10000  3  3     2                  0.0%           0.0%             1.00x    3.00x
10000  9  1     1                 11.5%          11.1%             1.16x    1.12x
10000  9  1     2                 22.9%          22.2%             1.33x    1.29x
10000  9  2     1                  0.0%           0.0%             1.16x    1.12x
10000  9  2     2                  3.0%           2.8%             1.33x    1.29x
10000  9  3     1                  0.0%           0.0%             1.14x    1.12x
10000  9  3     2                  0.0%           0.0%             1.30x    1.29x
with the ordered fallback nobody is without a home while any seat is up; 'lost all top-k' is the share that must dial a fallback, which is the failover stampede of D.4
```

**Failures.** With k = 2 no node loses both homes to one failure; two failures orphan a third of
nodes at M = 3 and 2.8 % at M = 9, and those nodes move to their next-ranked seat, so with the
ordered fallback nobody is homeless while any seat is up. Survivors carry M/(M − f): 1.5× at M = 3
with one down, 1.12× at M = 9. k = 1 orphans a third / an ninth per failure; k = 3 at M = 3 is
today's everyone-on-everyone.

```text
-- D.3 the period roll: homes that change when the period increments (independent rehash)
    N  M  k  nodes changing a home (sim)  1 - 1/C(M,k)  new dials at busiest seat  N k/M (1-k/M)
-----  -  -  ---------------------------  ------------  -------------------------  -------------
 1000  3  1                          66%           67%                        230            222
 1000  3  2                          65%           67%                        232            222
 1000  3  3                           0%            0%                          0              0
 1000  9  1                          88%           89%                        114             99
 1000  9  2                          95%           97%                        181            173
 1000  9  3                          98%           99%                        231            222
10000  3  1                          67%           67%                       2291           2222
10000  3  2                          67%           67%                       2269           2222
10000  3  3                           0%            0%                          0              0
10000  9  1                          89%           89%                       1044            988
10000  9  2                          97%           97%                       1807           1728
10000  9  3                          99%           99%                       2258           2222
```

```text
-- D.4 bounding the stampedes: stagger (per-node phase in the period) + make-before-break
assumptions: settle time tau = 10 s per new link; failover jitter window = 60 s; a node rolls at its own phase H(node) within the period, not at the period boundary
    N  M  k  period  roll dials/seat  boundary peak links (no stagger, MBB)  staggered dials/s  in flight  peak links staggered  failover dials/survivor  failover dials/s
-----  -  -  ------  ---------------  -------------------------------------  -----------------  ---------  --------------------  -----------------------  ----------------
 1000  3  2    1.0h              222                                    889              0.062        0.6                   667                      333               5.6
 1000  3  2   24.0h              222                                    889              0.003        0.0                   667                      333               5.6
 1000  9  2    1.0h              173                                    395              0.048        0.5                   223                       28               0.5
 1000  9  2   24.0h              173                                    395              0.002        0.0                   222                       28               0.5
10000  9  2    1.0h             1728                                   3951              0.480        4.8                  2227                      278               4.6
10000  9  2   24.0h             1728                                   3951              0.020        0.2                  2222                      278               4.6
10000  9  1    1.0h              988                                   2099              0.274        2.7                  1114                      139               2.3
10000  9  1   24.0h              988                                   2099              0.011        0.1                  1111                      139               2.3
the roll is bounded to ~1 extra link in flight once staggered; the failover of one seat is the stampede that remains: N k / (M (M-1)) dials spread over the jitter window
```

**The roll and the stampedes.** An independent rehash moves two thirds (M = 3) to 97 % (M = 9,
k = 2) of nodes each period, and if every node rolled at the period boundary a seat would take
1,728 new dials at once (10,000 nodes, 9 seats) while keeping 3,951 links through make-before-break.
Staggering fixes it entirely: let each node roll at its own phase `H(node) mod period` inside the
period, so the dials arrive at N·(k/M)(1 − k/M)/period per seat, 0.02 /s at a 24 h period, and with
make-before-break there is at most about one extra link in flight per seat (0.2 at 24 h, 4.8 at 1 h
with a 10 s settle **[assumption]**). The stampede that remains is failover: when a seat goes down
its N·k/M homed nodes each dial their next-ranked seat, N·k/(M(M − 1)) per survivor, 278 at
10,000 / 9 / 2, spread over the selector's jitter window (60 s **[assumption]**, 4.6 dials/s).
That is the number to size the handshake path for.

```text
-- D.5 combined with A: shaped peers per canonical = N k / M, all homed links shaped
    N  M  k  peers/server  B/s link  gap = mean wait  frames/W  round mean (4 waits)  real B/s
-----  -  -  ------------  --------  ---------------  --------  --------------------  --------
 1000  3  1           333       168            96.9s         4                  6.5m        84
 1000  3  2           667        84             3.2m         2                 12.9m        42
 1000  9  1           111       504            32.3s        10                  2.2m       252
 1000  9  2           222       252            64.6s         5                  4.3m       126
10000  3  1          3333        17            16.1m         1                  1.1h         8
10000  3  2          6667         8            32.3m         1                  2.2h         4
10000  9  1          1111        50             5.4m         1                 21.5m        25
10000  9  2          2222        25            10.8m         1                 43.0m        13
```

**Combined with A.** If every homed link were a shaped link, the slow tier would run at a 65 s gap
with 1,000 nodes and 9 seats (k = 2) and a 10.8 min gap, one real frame per window, with 10,000
nodes: a home round would take 43 min and move 13 B/s. This is the table that says homing alone is
not enough; section E says what else is needed.

**Recommendation D.** k = 2, M = 9 as planned; make-before-break as #935 states; size the
handshake path for the failover stampede, not the roll. On rotation the prior art is against the
proposal (§9.2): prefer a stable top-k by `H(node ‖ canonical)` re-homed only when the roster
changes (2.4 seats see a node in a year, not 9), and if Eric wants rotation for anti-domination,
take it from Guard Sets: an unpredictable public seed (roster-signed randomness, never a public
period counter) at a period of months, rolled at each node's own phase with make-before-break.
Rotation buys no load balance the hash does not already give.

---

## 7. E. Peer of last resort (assumption-driven)

### 7.0 Under the bound (primary)

```text
-- H.3 home rounds on the slots (E recomputed): Erlang-B blocking of an opened-then-closed shaped home round
a round holds a slot for 4 gaps + settle = 19.3 s [assumption: settle 10 s]; standing links hold a slot for good; demand = (N k/M) p_shaped / T_home rounds per second per seat; blocked rounds are refused to bulk (or retried)
    N  M  L  p_shaped  p_standing  standing  free slots  blocked @600s   @1h  @24h
-----  -  -  --------  ----------  --------  ----------  -------------  ----  ----
 1000  3  8       0.1         0.0         0           8             0%    0%    0%
 1000  3  8       1.0         0.0         0           8            65%    2%    0%
 1000  3  8       0.1         0.1         7           1            68%   26%    1%
 1000  3  8       0.1         0.3        20           0           100%  100%  100%
 1000  3  8       0.5         0.1        33           0           100%  100%  100%
 1000  3  8       1.0         0.1        67           0           100%  100%  100%
 1000  3  4       0.1         0.0         0           4            11%    0%    0%
 1000  3  4       1.0         0.0         0           4            82%   27%    0%
 1000  3  4       0.1         0.1         7           0           100%  100%  100%
 1000  3  4       0.1         0.3        20           0           100%  100%  100%
 1000  3  4       0.5         0.1        33           0           100%  100%  100%
 1000  3  4       1.0         0.1        67           0           100%  100%  100%
 1000  9  8       0.1         0.0         0           8             0%    0%    0%
 1000  9  8       1.0         0.0         0           8            19%    0%    0%
 1000  9  8       0.1         0.1         2           6             0%    0%    0%
 1000  9  8       0.1         0.3         7           1            42%   11%    0%
 1000  9  8       0.5         0.1        11           0           100%  100%  100%
 1000  9  8       1.0         0.1        22           0           100%  100%  100%
 1000  9  4       0.1         0.0         0           4             1%    0%    0%
 1000  9  4       1.0         0.0         0           4            53%    3%    0%
 1000  9  4       0.1         0.1         2           2            13%    1%    0%
 1000  9  4       0.1         0.3         7           0           100%  100%  100%
 1000  9  4       0.5         0.1        11           0           100%  100%  100%
 1000  9  4       1.0         0.1        22           0           100%  100%  100%
10000  9  8       0.1         0.0         0           8            19%    0%    0%
10000  9  8       1.0         0.0         0           8            89%   42%    0%
10000  9  8       0.1         0.1        22           0           100%  100%  100%
10000  9  8       0.1         0.3        67           0           100%  100%  100%
10000  9  8       0.5         0.1       111           0           100%  100%  100%
10000  9  8       1.0         0.1       222           0           100%  100%  100%
10000  9  4       0.1         0.0         0           4            53%    3%    0%
10000  9  4       1.0         0.0         0           4            94%   70%    0%
10000  9  4       0.1         0.1        22           0           100%  100%  100%
10000  9  4       0.1         0.3        67           0           100%  100%  100%
10000  9  4       0.5         0.1       111           0           100%  100%  100%
10000  9  4       1.0         0.1       222           0           100%  100%  100%
reading: with no standing links the slots carry hourly home rounds from a tenth of 10,000 nodes at 9 seats with under 1% blocked, and daily rounds from all of them; it is standing links that consume the slots: more than L standing shaped links at a seat and no home round runs there again. The canonical's shaped slots are for the last-resort standing set, capped at L by construction; every other homed node is on the bulk plane by Eric's rule, and that spill is what an observer sees
```

**Reading.** The slots are a loss system: a home round holds one for 4 gaps plus settle
(19.3 s, settle 10 s **[assumption]**), a standing link holds one for good. With no standing links
the 8 slots carry hourly home rounds from a tenth of 10,000 nodes at 9 seats with under 1 % blocked
and daily rounds from all of them; it is standing links that consume the slots, and more than L of
them at a seat means no home round runs there again. So under Eric's rule the canonical's shaped
slots are the last-resort standing set, capped at L by construction, and every other homed node
rounds on the bulk plane. The §7.1 fixed point P = S/(1 − θ/T_home) no longer applies (the gap is a
constant); E.1's share of rounds that touch a canonical is unchanged, but the share of those on a
shaped link is the H.3 complement of "blocked".

### 7.1 The floorless arm (sensitivity)

```text
relay order (FSD/CIRIS_MESH.md section 1): direct -> contact relay -> canonical. Three facts shape the count:
  (1) only a peer that OFFERS a class shapes the link (CC 5.4.3 item 1; fleet default: server on, home/phone opt-in), so an un-opted phone's link to a canonical is unshaped and outside the cap;
  (2) a shaped link costs the same idle or busy, so what matters is the number of OPEN shaped links, not rounds;
  (3) a home round at a canonical takes 4 waits at the gap of the moment, so links opened per round feed back into the gap (Little's law).

-- E.1 share of a node's rounds and bytes that touch a canonical (parameters are assumptions)
assumptions: 10 contact peers per node at a 30 s cadence; hard-NAT share 0.6; P(no live contact relay) = (1 - e a)^c with e = relay-eligible share of contacts, a = availability
k  home cadence  e*a  contacts  P(no relay)  rounds (and row bytes) via canonical
-  ------------  ---  --------  -----------  ------------------------------------
2         10.0m  0.3         5        16.8%                                 11.0%
2         10.0m  0.3        10         2.8%                                  2.7%
2         10.0m  0.6        10         0.0%                                  1.0%
2          1.0h  0.3         5        16.8%                                 10.2%
2          1.0h  0.3        10         2.8%                                  1.9%
2          1.0h  0.6        10         0.0%                                  0.2%
1          1.0h  0.3         5        16.8%                                 10.2%
1          1.0h  0.3        10         2.8%                                  1.8%
1          1.0h  0.6        10         0.0%                                  0.1%
bytes: the same share of ROW bytes as of rounds (a home round moves what a contact round moves); 0% of bulk and video (FSD/CIRIS_MESH.md 6.4 V1); audio at most 5% of measured egress (V2)

-- E.2 shaped links per canonical at the fixed point: P = S / (1 - theta / T_home), theta = 4 F (N k/M) p_shaped / cap
S = standing shaped links (hard-NAT nodes with no contact relay that keep the home link up, times p_shaped); a cadence T_home below theta cannot converge: links pile up faster than rounds finish
    N  M  homed (k=2)  p_shaped  p_standing     S  theta  P @600s (gap)   P @1h (gap)  P @24h (gap)
-----  -  -----------  --------  ----------  ----  -----  -------------  ------------  ------------
 1000  3          667       0.1         0.1     7  77.5s       8 (2.2s)      7 (2.0s)      7 (1.9s)
 1000  3          667       0.1         0.3    20  77.5s      23 (6.7s)     20 (5.9s)     20 (5.8s)
 1000  3          667       0.5         0.1    33   6.5m     94 (27.3s)    37 (10.9s)     33 (9.7s)
 1000  3          667       0.5         0.3   100   6.5m    282 (82.0s)   112 (32.6s)   100 (29.2s)
 1000  3          667       1.0         0.1    67  12.9m       diverges    85 (24.7s)    67 (19.5s)
 1000  3          667       1.0         0.3   200  12.9m       diverges   255 (74.1s)   202 (58.6s)
 1000  9          222       0.1         0.1     2  25.8s       2 (0.7s)      2 (0.7s)      2 (0.6s)
 1000  9          222       0.1         0.3     7  25.8s       7 (2.0s)      7 (2.0s)      7 (1.9s)
 1000  9          222       0.5         0.1    11   2.2m      14 (4.1s)     12 (3.3s)     11 (3.2s)
 1000  9          222       0.5         0.3    33   2.2m     42 (12.3s)    35 (10.0s)     33 (9.7s)
 1000  9          222       1.0         0.1    22   4.3m     39 (11.3s)     24 (7.0s)     22 (6.5s)
 1000  9          222       1.0         0.3    67   4.3m    117 (34.0s)    72 (20.9s)    67 (19.4s)
10000  3         6667       0.1         0.1    67  12.9m       diverges    85 (24.7s)    67 (19.5s)
10000  3         6667       0.1         0.3   200  12.9m       diverges   255 (74.1s)   202 (58.6s)
10000  3         6667       0.5         0.1   333   1.1h       diverges      diverges    349 (1.7m)
10000  3         6667       0.5         0.3  1000   1.1h       diverges      diverges   1047 (5.1m)
10000  3         6667       1.0         0.1   667   2.2h       diverges      diverges    732 (3.5m)
10000  3         6667       1.0         0.3  2000   2.2h       diverges      diverges  2197 (10.6m)
10000  9         2222       0.1         0.1    22   4.3m     39 (11.3s)     24 (7.0s)     22 (6.5s)
10000  9         2222       0.1         0.3    67   4.3m    117 (34.0s)    72 (20.9s)    67 (19.4s)
10000  9         2222       0.5         0.1   111  21.5m       diverges   173 (50.3s)   113 (32.8s)
10000  9         2222       0.5         0.3   333  21.5m       diverges    520 (2.5m)   338 (98.3s)
10000  9         2222       1.0         0.1   222  43.0m       diverges    787 (3.8m)   229 (66.6s)
10000  9         2222       1.0         0.3   667  43.0m       diverges  2360 (11.4m)    687 (3.3m)
reading: with 9 canonicals and 10,000 nodes, every shaped homed node rounding hourly is already past theta unless fewer than ~half of them shape; a daily home round converges everywhere. The realistic shaped-peer count per canonical is the standing set, a few tens to a few hundred, not N k / M
```

```text
-- E.1 share of a node's rounds and bytes that touch a canonical (parameters are assumptions)
assumptions: 10 contact peers per node at a 30 s cadence; hard-NAT share 0.6; P(no live contact relay) = (1 - e a)^c with e = relay-eligible share of contacts, a = availability
k  home cadence  e*a  contacts  P(no relay)  rounds (and row bytes) via canonical
-  ------------  ---  --------  -----------  ------------------------------------
2         10.0m  0.3         5        16.8%                                 11.0%
2         10.0m  0.3        10         2.8%                                  2.7%
2         10.0m  0.6        10         0.0%                                  1.0%
2          1.0h  0.3         5        16.8%                                 10.2%
2          1.0h  0.3        10         2.8%                                  1.9%
2          1.0h  0.6        10         0.0%                                  0.2%
1          1.0h  0.3         5        16.8%                                 10.2%
1          1.0h  0.3        10         2.8%                                  1.8%
1          1.0h  0.6        10         0.0%                                  0.1%
bytes: the same share of ROW bytes as of rounds (a home round moves what a contact round moves); 0% of bulk and video (FSD/CIRIS_MESH.md 6.4 V1); audio at most 5% of measured egress (V2)
```

**Reading.** Once contacts relay, the canonical carries a few per cent of a node's rounds and row
bytes (1–3 % with ten contacts; 10 % if a node has only five contacts and few of them are eligible
and up), none of its bulk or video (FSD/CIRIS_MESH.md §6.4 V1) and at most 5 % of its audio (V2).
The home round at the canonical is then anti-entropy against last resort, not the data path, and it
can run at a long cadence.

```text
-- E.2 shaped links per canonical at the fixed point: P = S / (1 - theta / T_home), theta = 4 F (N k/M) p_shaped / cap
S = standing shaped links (hard-NAT nodes with no contact relay that keep the home link up, times p_shaped); a cadence T_home below theta cannot converge: links pile up faster than rounds finish
    N  M  homed (k=2)  p_shaped  p_standing     S  theta  P @600s (gap)   P @1h (gap)  P @24h (gap)
-----  -  -----------  --------  ----------  ----  -----  -------------  ------------  ------------
 1000  3          667       0.1         0.1     7  77.5s       8 (2.2s)      7 (2.0s)      7 (1.9s)
 1000  3          667       0.1         0.3    20  77.5s      23 (6.7s)     20 (5.9s)     20 (5.8s)
 1000  3          667       0.5         0.1    33   6.5m     94 (27.3s)    37 (10.9s)     33 (9.7s)
 1000  3          667       0.5         0.3   100   6.5m    282 (82.0s)   112 (32.6s)   100 (29.2s)
 1000  3          667       1.0         0.1    67  12.9m       diverges    85 (24.7s)    67 (19.5s)
 1000  3          667       1.0         0.3   200  12.9m       diverges   255 (74.1s)   202 (58.6s)
 1000  9          222       0.1         0.1     2  25.8s       2 (0.7s)      2 (0.7s)      2 (0.6s)
 1000  9          222       0.1         0.3     7  25.8s       7 (2.0s)      7 (2.0s)      7 (1.9s)
 1000  9          222       0.5         0.1    11   2.2m      14 (4.1s)     12 (3.3s)     11 (3.2s)
 1000  9          222       0.5         0.3    33   2.2m     42 (12.3s)    35 (10.0s)     33 (9.7s)
 1000  9          222       1.0         0.1    22   4.3m     39 (11.3s)     24 (7.0s)     22 (6.5s)
 1000  9          222       1.0         0.3    67   4.3m    117 (34.0s)    72 (20.9s)    67 (19.4s)
10000  3         6667       0.1         0.1    67  12.9m       diverges    85 (24.7s)    67 (19.5s)
10000  3         6667       0.1         0.3   200  12.9m       diverges   255 (74.1s)   202 (58.6s)
10000  3         6667       0.5         0.1   333   1.1h       diverges      diverges    349 (1.7m)
10000  3         6667       0.5         0.3  1000   1.1h       diverges      diverges   1047 (5.1m)
10000  3         6667       1.0         0.1   667   2.2h       diverges      diverges    732 (3.5m)
10000  3         6667       1.0         0.3  2000   2.2h       diverges      diverges  2197 (10.6m)
10000  9         2222       0.1         0.1    22   4.3m     39 (11.3s)     24 (7.0s)     22 (6.5s)
10000  9         2222       0.1         0.3    67   4.3m    117 (34.0s)    72 (20.9s)    67 (19.4s)
10000  9         2222       0.5         0.1   111  21.5m       diverges   173 (50.3s)   113 (32.8s)
10000  9         2222       0.5         0.3   333  21.5m       diverges    520 (2.5m)   338 (98.3s)
10000  9         2222       1.0         0.1   222  43.0m       diverges    787 (3.8m)   229 (66.6s)
10000  9         2222       1.0         0.3   667  43.0m       diverges  2360 (11.4m)    687 (3.3m)
reading: with 9 canonicals and 10,000 nodes, every shaped homed node rounding hourly is already past theta unless fewer than ~half of them shape; a daily home round converges everywhere. The realistic shaped-peer count per canonical is the standing set, a few tens to a few hundred, not N k / M
```

**Reading.** The realistic shaped-peer count per canonical is the standing set S, the hard-NAT
nodes without a contact relay that keep their home link up and that offer a class, inflated by
1/(1 − θ/T_home). Three facts keep S small: a phone or home node that has not opted in offers `off`,
so its link to the canonical is unshaped and outside the cap (CC 5.4.3 item 1; the fleet default,
`FLEET_DEFAULTS`); a node with any contact relay has no reason to hold a standing canonical link;
and the home round is a last-resort check. Under those, the slow tier at a canonical holds a few
tens to a few hundred shaped links (gaps of seconds to a minute), not N·k/M. The table's
"diverges" cells are the warning: a short home cadence with every homed node shaping piles links up
faster than rounds finish at 10,000 nodes even with 9 seats.

**Recommendation E.** (1) Home rounds at a long cadence (an hour or a day) on an opened-then-closed
link, not a standing one, for any node that has a contact relay. (2) Standing canonical links only
for nodes with no eligible contact relay (the R2 last tier), and the service ladder (§7 of the mesh
FSD) sheds them first. (3) Count shaped links, not homed nodes, in the `load_ledger`: the gauge
that matters is open shaped links per canonical against the bound of A (L if bounded, ~100 if
floorless). This is also what the infrastructure-light designs in the survey do (Briar Mailbox,
Cwtch, SSB rooms, chatmail): bound the always-on node by trying the peer path first and keeping
only transit or owner-provisioned state on it.

---

## 8. F. The CPU side

```text
assumptions: AEAD 1.0 GB/s per core; node lock 20 us per frame; timer wake 5 us; peers send at their own class share (a canonical's cap bounds its SEND only; its RECEIVE is the sum of its peers' shares)
    N         peer class  out frames/s  in frames/s  MB/s  Mbit/s  core %  ingress GB/mo
-----  -----------------  ------------  -----------  ----  ------  ------  -------------
  100  server, few links          3.44           43   0.8       6    0.2%          1,960
  100               home          3.44           17   0.3       3    0.1%            871
  100         phone-wifi          3.44            9   0.2       2    0.0%            508
 1000  server, few links          3.44          430   7.1      56    1.8%         18,289
 1000               home          3.44          172   2.9      23    0.7%          7,403
 1000         phone-wifi          3.44           86   1.5      12    0.4%          3,774
10000  server, few links          3.44        4,302  70.1     560   17.8%        181,585
10000               home          3.44        1,721  28.1     224    7.1%         72,721
10000         phone-wifi          3.44          860  14.1     112    3.6%         36,433
bound: the per-link CPU is under 2% of one vCPU per 1,000 server-class peers; it is not worth a model beyond this line. What scales with N is INGRESS bytes (the peers' aggregate), which the cap does not bound, and the DB work per real row, which shaping does not change (persist #1177 removed the storm; cover frames never reach the DB)
```

**Bound.** Per shaped link the per-frame work is one timer wake and one AEAD seal or open over
16 KB. Outbound is fixed at cap/F = 3.44 frames/s whatever N. Inbound is the peers' aggregate, which
the cap does not bound: 430 frames/s and 7 MB/s at 1,000 full-rate server-class peers, 56 Mbit/s,
under 2 % of one vCPU at 1 GB/s AEAD and 20 µs of node lock per frame (the lock figure is the mesh
FSD's §6.2 assumption (b)). Not worth modelling beyond this bound. Two things do scale: ingress
bytes (18 TB/month at 1,000 full-rate server peers; free on Vultr **[assumption]** but not free on
the NIC or on a home link), and the DB work per real row, which shaping does not touch (persist
#1177 removed the storm; cover frames never reach the DB).

**Recommendation F.** No CPU model for shaping. Under the bound shaped ingress is capped with
egress at L × 7,000 B/s (§3.0), so the inbound asymmetry in the table above belongs to the floorless
arm only; what remains to watch per canonical is bulk-plane ingress, which the service ladder bounds
(mesh FSD §7), and the DB work per real row.

---

## 9. Prior art, and the three places it contradicts the rulings

From the survey of 2026-11-04 (primary sources read; **[analysis]** there marks the surveyor's
inference). The five to cite:

1. **Tarzan** (Freedman & Morris, CCS 2002, https://www.cs.princeton.edu/~mfreed/docs/tarzan-ccs02.pdf):
   verifiably hash-assigned "mimic" links carrying constant-rate cover, tunnels restricted to shaped
   links, a daily re-hash; the direct ancestor of every element here except the tiering. Its mimic
   count κ ≈ 2k is a small constant, and its anonymity bound (κ − 1)^(l − r) depends on that.
2. **The anonymity trilemma** (Das, Meiser, Mohammadi, Kate, S&P 2018, https://eprint.iacr.org/2017/954;
   the Comprehensive follow-up, PoPETs 2020; the SoK on performance bounds, WPES 2020): the 2βℓ bound,
   the equivalence of synchronized (slots) and unsynchronized (coin-flip/Poisson) user models in the
   anonymity metric, and delivery certainty as the one thing slots add.
3. **Changing of the Guards** (Elahi, Bauer, AlSabah, Dingledine, Goldberg, WPES 2012,
   https://www.freehaven.net/anonbib/cache/wpes12-cogs.pdf) with Dingledine 2013
   (https://blog.torproject.org/improving-tors-anonymity-changing-guard-parameters/), Proposal 236 and
   **Guard Sets** (Hayes & Danezis, PoPETs 2015, https://www.petsymposium.org/2015/papers/05_Hayes.pdf):
   measured, rotating a client's home multiplies the relays that see it (12–24 guards over eight
   months vs 3–5), so Tor went to one guard for most of a year; Guard Sets assigns deterministically
   from the consensus plus an unpredictable public seed and "never rotate[s]" the client.
4. **Herd** (Le Blond et al., SIGCOMM 2015, https://anonymity.ccs.neu.edu/pubs/sigcomm15.pdf): budget
   classes per tier, infrastructure links at higher fixed multiples of the unit rate, rate changes
   only class-wide and simultaneous because per-link adaptive rates leak; clients keep 2–3 chaffed
   links.
5. **Loopix** (Piotrowska et al., USENIX Security 2017, https://arxiv.org/abs/1703.00536) with
   **MixMatch** (PoPETs 2024): per-user Poisson rates, the merging property (sums of Poisson
   processes are Poisson), the provider caveat (the node that terminates the client link sees online
   pattern and volume whatever the rate), and the evidence that loop cover alone does not stop flow
   matching.

Three results cut against this model's inputs. Each is modelled below beside the ruled design.

### 9.1 A floorless cap/N split is unprecedented and publishes N

No prior divides a cover budget across a growing link count: Tarzan, Herd and the Loopix family all
hold the shaped-link count constant and concentrate cover. The trilemma does not forbid the divide
(per-link β ∝ 1/N while latency ∝ N, the product constant), but the per-link rate cap/(N·F) is N
written on the wire.

```text
-- G.1 (a) floorless cap/N vs (b) a bounded shaped-link count L with a per-link floor cap/L (Tarzan kappa ~ 2k, Herd 2-3 client links); peers past L are redirected to another home
leak in (a): one link's rate is cap/(N F), so an observer of ONE link reads N. A Poisson count of n frames estimates the rate to +-1/sqrt(n): N to +-10% needs ~100 frames, a +-1 change in N needs ~N^2 frames. Under fixed slots N is read exactly from 2 frames.
N (a)    gap  N to +-10% (Poisson, 100 frames)  detect N+-1 (N^2 frames)  N exact (slots, 2 frames)
-----  -----  --------------------------------  ------------------------  -------------------------
    8   2.3s                              3.9m                      2.5m                       4.6s
   34   9.9s                             16.5m                      3.2h                      19.8s
  100  29.1s                             48.4m                        3d                      58.1s
  300  87.2s                              2.4h                       91d                       2.9m
 1000   4.8m                              8.1h                     3363d                       9.7m

(b): the link rate is the class floor cap/L, a constant of the class, so a link reveals the class and nothing about N; the price is capacity: M L shaped homes in the fleet, the rest redirected
L (b)  B/s link    gap    p99  frames/W  15s/30s rounds  shaped homes M=3,N=1k         M=9,N=1k        M=9,N=10k  seats to shape all of 10k
-----  --------  -----  -----  --------  --------------  ---------------------  ---------------  ---------------  -------------------------
    8     7,000   2.3s  10.7s       130             yes            24/667 (4%)     72/222 (32%)     72/2222 (3%)                       2500
   16     3,500   4.6s  21.4s        65              no            48/667 (7%)    144/222 (65%)    144/2222 (6%)                       1250
   32     1,750   9.3s  42.8s        33              no           96/667 (14%)   288/222 (100%)   288/2222 (13%)                        625
   64       875  18.6s  85.6s        17              no          192/667 (29%)   576/222 (100%)   576/2222 (26%)                        312
  128       438  37.2s   2.9m         9              no          384/667 (58%)  1152/222 (100%)  1152/2222 (52%)                        156
reading: (b) keeps the slow tier at seconds and keeps rounds inside today's constants up to L=16, and turns every peer past M L into a redirect (homing's fallback order) or an unshaped link; it does not make 10,000 shaped homes fit 9 seats, nothing does
```

**Side by side.** (a) The ruled floorless divide: a passive observer of one link reads N to ±10 %
from about 100 frames (48 min at N = 100, 8 h at N = 1,000) and reads it exactly from two frames
under slots; a change of one peer is invisible in practice at N ≥ 100 (N² frames). (b) The Tarzan/Herd
shape: a bound L on shaped links with the per-link floor cap/L, peers past the bound redirected
through homing's fallback order. At L = 8 or 16 the slow tier stays at 2–5 s and today's 15 s / 30 s
constants hold; the link's rate is a class constant and says nothing about N. The price is in the
capacity columns: nine seats at L = 16 shape 144 homes, 65 % of the 1,000-node demand and 6 % of the
10,000-node demand; everyone else is redirected or runs unshaped. Neither design makes 10,000 shaped
homes fit nine seats; (a) answers with minutes of latency and a published N, (b) with an honest
refusal and a redirect. Section E's standing set is what both have to serve. **Ruled:** Eric chose
(b) with L = 8 (§0 ruling 5). The leak that remains is the second one named in the survey: a
refused peer's bulk link is a visible spill, an observable mode change from shaped to unshaped on
that pair. It is accepted, and it is bounded: the spill reveals that the pair is past the bound,
not N, not timing, not volume inside any shaped link.

### 9.2 Rotating homes each period is a measured net loss

COGS, Users Get Routed, Dingledine 2013 and Proposal 236 all measured exposure growing with the
number of distinct homes seen; Hayes & Danezis obtain the load-spread and anti-accumulation
benefits by rotating *set membership* on an unpredictable public seed, never the client. A
predictable seed (`H(node ‖ canonical ‖ period)` over public inputs) also lets an adversary
precompute every node's future homes and grind identities onto a target seat **[analysis]**.

```text
-- G.2 homing without per-period rotation: exposure (distinct seats that see a node in a year) vs balance
per-period rehash: a node's top-k is a fresh draw each period; stable HRW: H(node|canonical) with no period, re-homed only when the roster changes (assume 2 roster changes a year); beacon: an unpredictable public seed with a long period (Hayes & Danezis)
M                    scheme (k=2)  draws/yr  distinct seats see the node  P(1 adversary seat of M was a home)
-  ------------------------------  --------  ---------------------------  -----------------------------------
3              per period, hourly      8760                          3.0                                 100%
3               per period, daily       365                          3.0                                 100%
3             per period, monthly        12                          3.0                                 100%
3               beacon, quarterly         4                          3.0                                  99%
3                  beacon, yearly         1                          2.0                                  67%
3  stable HRW (+2 roster changes)         0                          2.8                                  75%
9              per period, hourly      8760                          9.0                                 100%
9               per period, daily       365                          9.0                                 100%
9             per period, monthly        12                          8.6                                  95%
9               beacon, quarterly         4                          5.7                                  63%
9                  beacon, yearly         1                          2.0                                  22%
9  stable HRW (+2 roster changes)         0                          2.4                                  24%
balance is the hash's, not the rotation's: max/mean at N=10,000, M=9, k=2 is 1.045 for the stable draw and 1.040 for the next period's; rotation buys no balance
what rotation does buy is Tarzan's anti-domination (no seat accumulates nodes for long); Guard Sets gets it by rotating SEAT membership on a public unpredictable seed, never the node's home
```

**Side by side.** Per-period rotation at any period a day or shorter shows a node to every seat
within the year (all nine at M = 9), and an adversary holding one seat has been a home with
certainty. A stable top-k by `H(node ‖ canonical)` with re-homing only on roster change shows it to
2.4 seats (24 % for the one-seat adversary; two roster changes a year **[assumption]**); a beacon
seed at a yearly period is the same 2.0 / 22 %, quarterly 5.7 / 63 %. Load balance is the hash's and
is identical in every scheme (max/mean 1.04–1.05 at 10,000 / 9 / 2). Rotation buys nothing in this
model's load columns; what it buys is Tarzan's anti-domination, which Guard Sets gets without
moving the node.

### 9.3 Slots vs Poisson: Poisson wins on observability, slots on the worst case only

```text
-- G.3 slots vs Poisson with the merging property (Loopix): the node's uplink and one link
   N             uplink process                                        one link                    cross-link  mean wait    p99      worst
----  -------------------------  ----------------------------------------------  ----------------------------  ---------  -----  ---------
   8     Poisson(3.44/s), any N   Poisson, rate reveals N in ~100 frames = 3.9m                          none       2.3s  10.7s  unbounded
   8  periodic at 3.44/s, any N          periodic, N exact from 2 frames = 4.6s  phase-locked, never coincide       1.2s   2.3s       2.3s
 100     Poisson(3.44/s), any N  Poisson, rate reveals N in ~100 frames = 48.4m                          none      29.1s   2.2m  unbounded
 100  periodic at 3.44/s, any N         periodic, N exact from 2 frames = 58.1s  phase-locked, never coincide      14.5s  28.8s      29.1s
1000     Poisson(3.44/s), any N   Poisson, rate reveals N in ~100 frames = 8.1h                          none       4.8m  22.3m  unbounded
1000  periodic at 3.44/s, any N          periodic, N exact from 2 frames = 9.7m  phase-locked, never coincide       2.4m   4.8m       4.8m
Poisson wins on observability (N hidden on the uplink by merging, slowly readable on one link); slots win only on worst-case latency (one gap) and on making an active drop a visible missing slot
```

By Loopix's merging property, N independent Poisson(cap/(N·F)) timers sum to Poisson(cap/F) on the
node's uplink whatever N is, so an uplink observer learns nothing about N and a single-link observer
only a slow rate estimate. Round-robin slots make every link strictly periodic with period N·F/cap
(N exact from two frames) and phase-lock a node's links into a cross-link fingerprint. What slots
buy is the trilemma's delivery certainty: worst-case wait one gap against Poisson's 4.6 gaps at p99
and no bound, and a drop that shows as a missing slot. Section 5's C.2 table stands; this is its
numbers.

### 9.4 The active dropper (open item)

```text
-- G.4 the active dropper (Levine 2004; Feigenbaum 2010): what a dropped or delayed frame costs each scheme
                     scheme                                                                                                  a drop is                                                                         a delay is     status in edge
---------------------------  ---------------------------------------------------------------------------------------------------------  ---------------------------------------------------------------------------------  -----------------
    Poisson per link, today   invisible at the shaping layer; the leviculum Channel retransmits (seq), so a drop becomes a delay [inf]  no defensive dropping; a delayed real frame shifts the real-share timing within W               OPEN
                fixed slots                                                                   a missing slot is visible within one gap                                               none without a drop-tolerant wrapper  n/a (not shipped)
defensive dropping (Levine)  the sender drops a known share of its own cover at random so an adversary's drops are not distinguishable                                              costs real throughput at the same rho       not designed
```

Levine, Reiter, Wang & Wright (FC 2004) show timing correlation is "highly sensitive to dropped
packets" and that an attacker can drop them on purpose; their fix is defensive dropping. Feigenbaum,
Johnson & Syverson (PETS 2010): active adversaries break padding by inserting delays and dropping
messages unless the padding is wrapped by a protocol that tolerates them. Edge's shaped frames ride
the leviculum Channel, so a dropped frame is retransmitted and becomes a delay **[inf]**; there is no
defensive dropping and nothing at the shaping layer tolerates or detects an adversary's delays.
Recorded as open question 7 in §10.

---

## 10. Open CC questions

1. **The seat class** (CC#200 Q1, Q2): accept `seat` with the seat-proof gate and its own budget; does
   a faster inter-seat link weaken what shaping hides? This model's position: no, inter-seat links
   carry no person's rows at a person's cadence, and the class is proved from the roster.
2. **Rotation** (CC#200 Q3): does 5.4.3 item 3 bind the per-link process or the node's emission
   process? §5 above.
3. **The floor** (CC#200 Q4): confirm "divides a node-wide cap" means no per-link minimum, so the
   sum never exceeds eight links' worth. This model assumes it.
4. **Timeouts that follow the agreement** (new): a shaped link's replication timeouts and round
   interval derived from λ. Not a CC matter unless the CC wants the cadence named; raised so the
   constants are not read as normative.
5. **Inbound asymmetry** (moot under ruling 5 for shaped links): the bound caps receive as well as
   send, 8 × 7,000 B/s per class each way (§3.0). It stands only for the floorless arm, where a
   node's receive is the sum of its peers' shares. Not for the CC now.
6. **Standing vs opened links** (new): is a canonical link that is opened for a home round and
   closed a shaped link under item 2 "both directions or neither" for its lifetime (yes **[inf]**),
   and does closing and reopening leak anything the standing link does not (link setup is
   observable either way, item 5)?
7. **The active dropper** (new, from §9.4): does CC 5.4.3 require shaping to survive an adversary
   that drops or delays frames on a shaped link (defensive dropping, or a drop-tolerant wrapper as
   Feigenbaum–Johnson–Syverson), or is that attack outside the 1.13.3.1 claim? Edge has neither
   today.
8. **Bounded shaped-link count** (RULED, Eric 2026-11-04): "we shape with shaped peers if possible,
   otherwise refuse and offer unshaped (bulk transfers) if available". BoundedWithFloor, L = 8
   minus the layer reserve, refusal `link_shaping_home_elsewhere`, bulk link still offered. What
   remains for the CC is whether "divides a node-wide cap across its shaped links" (5.4.3 item 1)
   reads as this bound; CC#200 Q4 should be re-put in those words.
9. **Stable homing** (OPEN, for Eric): both arms are kept. The decision table, k = 2 (§9.2 G.2, a
   one-year horizon, two roster changes a year **[assumption]**):

   | scheme | M = 3: seats that see a node / P(one adversary seat was a home) | M = 9: same |
   |---|---|---|
   | per-period rehash, daily (#935 as proposed) | 3.0 / 100 % | 9.0 / 100 % |
   | per-period rehash, monthly | 3.0 / 100 % | 8.6 / 95 % |
   | beacon-seeded, quarterly | 3.0 / 99 % | 5.7 / 63 % |
   | beacon-seeded, yearly | 2.0 / 67 % | 2.0 / 22 % |
   | stable top-k, re-homed on roster change | 2.8 / 75 % | 2.4 / 24 % |

   Load balance is identical in every row (the hash's, max/mean 1.04–1.05 at 10,000 / 9). Under the
   bound (§6.0) rotation cannot move a slot holder, so the choice is about the fallback order's
   exposure only. Recommendation D stands: stable top-k, or a beacon seed at a months-long period.

---

## 11. Assumptions register

| Where | Assumption | Effect if wrong |
|---|---|---|
| §2, A | the per-wait timer starts at enqueue (Erlang-2); the alternative column shows the departure start | A.2 shifts toward the "timer at departure" column |
| A | the five planes' messages queue behind one another one-per-frame | one-per-frame rounds are between the Erlang-4 and Erlang-20 columns |
| A | an idle round still sends all four messages | idle rounds cost less ρ budget than A.3 charges |
| §1 | frame payload 16,248 B | a 64 KiB Deliver is 5 frames either way (4.03 → 5) |
| B | Vultr meters egress only; ingress free | B's quota column must add ingress |
| B | the slow cap's 145 GB is spent whatever the load (cover) | true by construction; only lower if the canonical has < 8 links' worth of shaped peers... it will not |
| D.4 | 10 s to settle a new link; 60 s failover jitter | the in-flight and dials/s columns scale linearly |
| E.1 | 10 contacts at 30 s; hard-NAT share 0.6; e·a ∈ {0.3, 0.6} | the canonical's round share moves between 0.1 % and 11 % |
| E.2 | p_shaped ∈ {0.1, 0.5, 1}; p_standing ∈ {0.1, 0.3} | S scales linearly; θ scales with p_shaped |
| F | AEAD 1 GB/s per core; lock 20 µs/frame (mesh FSD §6.2 b); timer 5 µs | core % scales linearly |
| H.3 | a home round holds a shaped slot for 4 gaps + 10 s settle = 19.3 s | blocking scales with the hold time |
| G.2 | two roster changes a year (one seat joins, one leaves) | stable HRW's distinct-seat count moves by ~0.2 per change |
| G.4 | a dropped shaped frame is retransmitted by the leviculum Channel | if not, a drop is silent loss, which is worse for the dropper item, not better |
| §0 | `MIN_LAMBDA` floor removed in v44 | with the floor, A's totals exceed the cap past N = 34 (cost doc table) |

---

## 12. Running it

```
python3 -I tools/models/transport_tiers.py
```

Seed 20261104; the output is byte-identical across runs. To re-pin a constant, change the block at
the top of the script and paste the new output here.
