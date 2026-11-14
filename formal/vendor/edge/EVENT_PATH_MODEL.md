# FSD — The event path and the retry schedule: a quantitative model for the v44 LTS

**Status:** model, not a measurement. Three seeded scripts produce every number here, standard
library only, no network, no cargo: `tools/models/retry_schedule.py` (M8, about 3 min),
`tools/models/event_path.py` (M1, about 4 min), `tools/models/reply_lane.py` (M2, 4 s). Each is run
with `python3 -I`. Tables are their output of 2026-11-05, cut to the rows that decide something.
**Direction:** Eric, "get this behaviour fully understood before scale". The brief is §6 of the v44
telemetry audit. The constitution's formal models state what must hold; these are the dynamics of
whether the constants deliver it.

**Trees read:** candidate `feat/onion-v44` dce058f; `fix/v44-seal-event-path` 6c87599 (the audit read
c519691; a later commit added the identify grace, and every constant it read is unchanged);
`fix/v44-responder-drain` aef9e1a; persist tag v61.0.3; ciris-crypto v22.0.0; leviculum a3dc12c;
CIRISConstitution `formal/` 6d9e1da. Each script greps its constants out of those trees at start and
fails if one has moved.

**Tags:** **[read]** in the code or text at those commits. **[model]** this model's output.
**[inf]** inference that nothing here exercises. **[cited]** someone else's measurement, not of our
code. **[assumption]** a parameter nobody supplied; §7 lists them.

The one sentence: **the schedule is right and a rolling upgrade never reaches it, because the
restart that upgrades a refuser empties its memory; what a row really waits for is the peer's
re-sweep, and the constants that are wrong are the ones on the paths nobody had modelled: who has
standing after a restart, a re-dial phase-locked to the limiter, a queue smaller than the budget in
front of it, and a watermark map narrower than a canonical.**

---

## 0. What the models say is wrong

Nothing in code was changed.

| # | Constant or behaviour | Ships | I would use | Why | Evidence |
|---|---|---|---|---|---|
| 1 | Standing after a restart | read from the live `peers` map, which a restart empties | read the persisted bindings at boot, as `PersistedBindingResolver` already does for send | every ordinary peer's first link after a restart is judged a stranger, so `DECAP_QUEUE_STANDING`'s own comment ("a canonical's peers re-dialling together after a restart") describes a case that cannot arise. K = 500 in 1 s: 49% refused, 32 s against 1 s | §2.3 |
| 2 | Re-dial timing | the next 30 s tick, no jitter, against a 10 s sliding window | jitter the re-dial after a refused link, 15–45 s | a dial refused in the closed part of the window comes back to the closed part. 100/s flood, first contact in 300 s: 45% shipped, 98% jittered | §2.4 |
| 3 | `DECAP_QUEUE_STRANGER` | 32 | 256, its own window budget | a queue smaller than the budget refuses what the budget admitted, after the slot is spent: of a 256 burst 53 key and 203 burn their slots | §2.5 |
| 4 | `DECAP_QUEUE_STANDING` | 64 | 1024 | K = 130 at spread 0 refuses 31%; 256 clears 130, 1024 clears 500. Worst wait 256 ms at s = 250 µs. Holds inside `KEYING_BUDGET` to s ≈ 9 ms. Applies when the event loop hands frames over faster than the keyer runs, §2.5 | §2.5 |
| 5 | `MAX_TRACKED_SWEEP_CURSORS` | 512 | 8192 (1000 peers × 8 planes) | past peers × planes = 512, LRU thrashes: a peer that loses its cursor restarts at the plane's first page, so rows past it are not offered. The #531 bug again. 8 planes: 65 peers; 14: 37. [inf] whether a production canonical crosses it | §1.6 |
| 6 | No node-wide reply byte bound | 2.5 MiB per lane, lanes unbounded | add one, 64 MiB | 130 peers × 8 planes is 2.6 GiB against a canonical's ~1 GB; a healthy one holds about 17 MiB | §3.2 |
| 7 | Stranger keyed links | 256/10 s × 120 s idle = 3,072 held, no count bound | a count bound like `AWAITING_LINKS_MAX`, 512, oldest stranger out; or stranger idle 30 s | past leviculum's 1,024 envelope in 40 s. A flood that keeps links alive defeats the idle bound, so the count is the fix. Do not cut the rate: it trades directly against the honest share | §2.6 |

**Holds:** `DECAP_WORKERS_MAX` (never binds on the cited bracket), `HANDSHAKES_STANDING_NODE`, the
per-sender rates, `TRANSIENT_CAP`, `TRANSIENT_CAP_HITS_BEFORE_TERMINAL`, `TERMINAL_CAP`,
`REPLY_QUEUE_JOBS`, the per-lane `REPLY_QUEUE_BYTES`, the reply expiry. **Stale text, no behaviour:**
the 20 minutes in `TRANSIENT_CAP_HITS_BEFORE_TERMINAL`'s comment is a floor; #776's "asked again at
once" holds only on a plane within a page (§1.5); `reticulum.rs` still calls leviculum's envelope a
FIFO, which leviculum#56 ended.

---

## 0.1 What rests on the formal models, and what is new ground

| Piece | Rests on | Status here |
|---|---|---|
| M8 scenario, who may remove | `membership`: `Inv_QuorumGovernsRoster` (MB.quorum), `Inv_CoercedCannotRemoveHonest` (MB.coerced), twins `unanimous_two`, `any_member_removes` | reused. `ProtocolMet` with `UnanimousRemoval = others_majority` is ported into `retry_schedule.py` and equals persist #1192 on every signer set to n = 8 |
| M8, a corrected row is different bytes | `withdraws_admission`: `Inv_OneDoor` (WA.door). A withdrawal is a new row, so a new hash, so never suppressed | reused, not re-derived |
| M8, who may be offered a row | `mesh_net` I1, I2, I3 (`Inv_Consent`, `Inv_Invisible`); CC 5.4.6. Offers stay inside `may_receive`. The rewind in §1.4 changes when, never to whom | assumed |
| M8 retry schedule, re-sweep, restart | nothing. CC and `formal/` carry no retry schedule | **new ground** |
| M1 rates, queues, workers | CC 5.3.3.10 requires decapsulation behind per-sender, per-link and node-wide rates and outside any node-wide lock, and gives no numbers | **new ground**; the order is the text's, the numbers are edge's |
| M1, the road a stranger needs | `transport_tiers`: `every_road_runs_on_strangers`, `stranger_only_consent_free`, `routed_nine_canonicals` | reused. The carriage is proved; §2.4 is whether it is delivered |
| M1, a canonical's share of first contact | `transport_tiers`: `routedAsksPerSecond` = 30 at nine, so 3.3/s each; `askBytes` is not pinned | reused, §2.6 |
| M1, who can never have standing | `anonymous`: `anon_route_never_held`. An anonymous node is a stranger at every receiver order, for good | reused |
| M2 expiry on shaped links | `transport_tiers`: `Class.budget`, CC 5.4.3 | reused |
| M2 lane, shed, expiry | nothing. `mesh_net` models holding, not links or queues, and bounds no part of M1 or M2 | **new ground** |

Read and not relied on: `reciprocity`; `retirement`; `onion_layers` (its header says CC 5.4.6 item 4
superseded the rule on 2026-11-05). `G.refusal` and `RT.refstands` are an agent's refuse verb, a
homonym of a door refusal.

**Findings against the formal side.** Neither side was adjusted. CC's session read this list against
`formal/` at 6d9e1da, and persist's session read v61.0.3. Their answers are readings, not rulings, and
were not run. CC confirmed every citation in the table above, and that nothing in `formal/` bounds M1
or M2. `askBytes` is an assumption of `Tiers.lean`.

- **F1, a state `membership` does not cover.** A moderator's removal lands on old nodes without
  meeting the protocol and stands there (persist 61.0.3: "Removals already held stand"). CC: outside
  the model, not a violation. `Membership.tla` has no editions, and `Inv_QuorumGovernsRoster` holds per
  node over what that node admitted under its own edition. This is the stated cost Eric accepted on
  CIRISPersist#1200. §1.3 sizes it: 44–50% for a mid-upgrade mint.
- **F2, the election in a mixed fleet.** CC: "one result on every node" (4.5.13) is about nodes holding
  the same rows. A version fork gives different rosters, so different electorates and possibly
  different seats, converging as the fleet converges. A residual of the mixed fleet, not a model failure.
- **F3, a refusal's record: required by the text, absent in persist.** CC 4.4.3.6 requires
  `hard_case:community_consensus_protocol_violation:{C}` on an unmet protocol. Persist at v61.0.3 emits
  none: the string is only an error's Display text, and `roster_consensus_insufficient` is a rule of
  `RosterAuthorityUnauthorized`, on both doors, surfacing as an `Err`, logged at debug. CC has filed
  that, with bounds: one record per refused row id, none for a re-ask, none for retryable out-of-order
  rules, emission behind the receiver order's rates. §1.3 models both: **today none, required about
  one per refuser per distinct row** (**[inf]** per refusing node; the bound names the row), not one
  per refusal. Today each re-ask is a full re-evaluation that writes nothing: a CPU cost with no
  durable trace that the operator cannot see, which `moved_to_terminal` and `refusal.attempts` must
  fix. **[model]** The cost is small: a full 4096-row ring at 4 asks a day is 0.19 asks/s; at ~280 µs
  a hybrid verify [read, `docs/BENCHMARKS.md`] that is about 0.05 ms of CPU per second, before the
  roster reads. Membership event observability under 3.4.2 is by design (1.13.3.1). Note edge books
  this rule Transient while the text's record treats the unmet protocol as a refusal of that row;
  persist reads it as substantive, with a verdict that can change as roster rows arrive.
- **F4, retry is edge's own.** CC: a refused row is not a held change, since `Prop_HeldChangeResolves`
  quantifies over admitted pending changes. Re-asking forever is edge's behaviour, to be jittered and
  bounded by edge, not derived from text.
- **F5, a residual the text does not state yet.** No text promises first contact under flood. CC 5.4.6's
  receiver order is the anti-spam, and a refused request gets no answer. A Sybil flood degrading honest
  first contact is a residual; 45% in 300 s at 100/s is the number to state it with (§2.4). The phase
  lock is edge's implementation choice, and jittering the dial is the fix.

---

## 1. M8: the retry schedule under a rolling upgrade

### 1.1 The schedule

`record_at` is ported line for line and matches the unit witness in `refusal_backoff.rs`.

```text
refusal  disposition  cap_hits  window  booked at  next ask no sooner than
-------  -----------  --------  ------  ---------  -----------------------
      1    transient         0     20s         0s                      20s
      2    transient         0     40s        20s                      60s
      3    transient         0     80s        60s                     2.3m
      4    transient         0    160s       2.3m                     5.0m
      5    transient         1    300s       5.0m                    10.0m
      6    transient         2    300s      10.0m                    15.0m
      7    transient         3    300s      15.0m                    20.0m
      8     terminal         4   1800s      20.0m                    50.0m
      9     terminal         5   3600s      50.0m                     1.8h
     10     terminal         6   7200s       1.8h                     3.8h
     11     terminal         7  14400s       3.8h                     7.8h
     12     terminal         8  21600s       7.8h                    13.8h
     13     terminal         9  21600s      13.8h                    19.8h
     14     terminal        10  21600s      19.8h                    25.8h
```

**The audit's windows and terminal at the 8th refusal: confirmed [read].** Its "about 20 minutes" is
a floor, and its "up to 6 h after" is refuted for the upgrade it describes. A 6 h window needs the
12th refusal, booked 7.8 h in.

### 1.2 The row waits for an offer, not for its window

The windows say when a node may ask. It can only ask for a hash a Summary names, and past one page
**[read]** a peer names a row once per re-sweep, `ceil(corpus/1024)` Summaries. The two sides' sweeps
of a `(peer, kind)` share one cursor. There is no jitter on the tick or on any window.

```text
                 summaries  ask to apply (s)  8th refusal after 1st  gaps between refusals (s)
--------------------------  ----------------  ---------------------  -------------------------
             one initiator              0.05                  22.5m   30 60 90 180 330 330 330
             one initiator                 1                  22.5m   30 60 90 180 330 330 330
             one initiator                 5                  22.5m   30 60 90 180 330 330 330
both sides, opposite phase              0.05                  21.2m   30 45 90 165 315 315 315
both sides, opposite phase                 1                  21.2m   30 45 90 165 315 315 315
both sides, opposite phase                 5                  21.2m   30 45 90 165 315 315 315

     plane  Summaries per 30 s  re-sweep period  >15 min bound  1 holder  3 holders  8 holders
----------  ------------------  ---------------  -------------  --------  ---------  ---------
  <=1 page                   1              30s              -     22.5m      21.0m      20.5m
  <=1 page                   2              15s              -     21.2m      20.7m      20.3m
14.6k rows                   1             7.5m              -     52.5m      35.9m      26.2m
14.6k rows                   2             3.8m              -     37.5m      26.2m      23.5m
  52k rows                   1            25.5m           WARN      3.0h      76.5m      39.9m
  52k rows                   2            12.8m              -     89.2m      43.9m      30.5m
```

At the corpus the code's comments cite, the 8th refusal comes at 40 minutes to 3 hours, and past
about 31k rows one side's re-sweep passes `RESWEEP_CYCLE_BOUND`, so its WARN fires on every cycle.

### 1.3 Direction: the two named rows refuse on opposite sides

The brief lists both as refused by not-yet-upgraded nodes. **Only #1192 is.** The 61.0.3 changelog
**[read]**: "A node on 61.0.3 refuses such a removal arriving from an older node." **[read]** both
reach edge the same way: `roster_consensus_insufficient` → `RetryAfterStanding` → Transient, not
indexed, so the transient ladder. Only the audit's claim of path holds; its direction does not.

| | #1192 | #1200 |
|---|---|---|
| Refuser | old node | upgraded node |
| What ends it | that node's upgrade | nothing; the room acting under its protocol |
| Memory at the moment it matters | emptied by the same restart | never the issue |

**[read]** The refusal memory is in-process and an upgrade is a restart, so an old refuser forgets at
exactly the moment its verdict changes. It need not be told.

```text
  N       plane  Summ/30s      P  T (min)  sit mean  sit p95  worst node lag  nodes >=8 refusals  survive mean  survive p95  rewind mean  rewind p95
---  ----------  --------  -----  -------  --------  -------  --------------  ------------------  ------------  -----------  -----------  ----------
  9    <=1 page         1    30s       20        3s       8s             90s                 0.4         15.9m        56.8m           3s          6s
  9    <=1 page         1    30s       60        3s       8s             90s                 5.1         80.3m         3.9h           3s          6s
  9    <=1 page         1    30s      360        3s       8s             90s                 8.0          2.9h         3.9h           3s          6s
  9    52k rows         1  25.5m       20      2.7m     7.8m           16.3m                 0.0          3.8m         7.2m           3s          8s
  9    52k rows         1  25.5m       60      4.3m     8.2m           22.2m                 1.4         25.6m        34.2m           3s          8s
  9    52k rows         1  25.5m      360      3.0m     6.0m           25.0m                 6.0          3.5h         3.9h           3s          7s
130    <=1 page         1    30s       20        5s      11s            8.0m                 2.7         31.2m        57.1m           2s          5s
130    <=1 page         1    30s       60        4s       9s           22.9m                60.2         66.3m         1.9h           2s          5s
130    <=1 page         1    30s      360        4s      12s            2.2h                98.2          5.2h         5.8h           3s          5s
130    52k rows         1  25.5m       20      5.5m     9.9m           20.0m                 0.0          7.7m        12.8m           4s         11s
130    52k rows         1  25.5m       60      4.8m     8.6m           32.2m                 4.8         27.6m        36.2m           4s         10s
130    52k rows         1  25.5m      360      2.6m     5.7m            2.3h                70.6          3.3h         4.0h           4s         10s
```

- **`sit`** is the last node back to the last node holding the row. It tracks the re-sweep and N, never
  a refusal window. Worst p95 in the run: 11 min, 130 nodes at 52k rows.
- **`survive`** is a counterfactual that nothing ships: the memory outlives the restart. It is the
  audit's picture, up to 5.9 h. The gap between it and `shipped` is what the restart already buys.
- **`nodes ≥ 8 refusals`:** many rows do reach terminal on old nodes. It costs nothing, since the
  restart wipes them.
- **`worst node lag`** at degree 8 is percolation, not backoff: an old node refuses the row, so it
  cannot carry it.

#1200, 24 h after a moderator's removal is minted on an old node at T/2:

```text
 N     plane  T (min)  nodes holding the removal, mean   range  asks per refuser in 24 h  refusers on terminal  records today  records as CC requires  if each refusal emitted
--  --------  -------  -------------------------------  ------  ------------------------  --------------------  -------------  ----------------------  -----------------------
 9  <=1 page        5                              44%  44-44%                      14.3                  100%              0                     5.0                       72
 9  <=1 page       20                              44%  44-44%                      14.6                  100%              0                     5.0                       73
 9  <=1 page       60                              44%  44-44%                      14.5                  100%              0                     5.0                       72
 9  <=1 page      180                              44%  44-44%                      14.5                  100%              0                     5.0                       72
30  <=1 page        5                              50%  50-50%                      16.4                  100%              0                    15.0                      245
30  <=1 page       20                              50%  50-50%                      16.4                  100%              0                    15.0                      245
30  <=1 page       60                              50%  50-50%                      16.1                  100%              0                    15.0                      242
30  <=1 page      180                              50%  50-50%                      15.9                  100%              0                    15.0                      239
30  52k rows        5                              50%  50-50%                      14.3                  100%              0                    15.0                      214
30  52k rows       20                              50%  50-50%                      14.0                  100%              0                    15.0                      210
30  52k rows       60                              50%  50-50%                      14.0                  100%              0                    15.0                      210
30  52k rows      180                              50%  50-50%                      14.0                  100%              0                    15.0                      210
```

`records` is F3's two arms: none today, about one per refuser as CC 4.4.3.6 requires, against what
a record per refusal would have cost. The fork is the share of the fleet old at mint. The propagation kick spreads a new row among old
nodes in seconds, so T does not move it. **Decided by whether the mint happens before the upgrade,
not by any constant.**

### 1.4 The decision

- **Does an upgrade need to reset refusal memory? No.** The restart does it.
- **Should the cap or transient count change? No.** Neither binds in an upgrade.
- **The lever left is the offer.** `rewind` (proposal: a peer re-offers recent rows on seeing a node
  come back) takes the 52k sit from minutes to seconds. It is optional: minutes after an upgrade are
  acceptable, and the offer stays inside `may_receive`.

### 1.5 The one place the memory does delay

A refuser that does not restart, and a dependency that lands later: a moderator's widening refused
while its `delegates_to` is still arriving, on a node that has upgraded already.
`RetryAfterStanding` is not indexed, so nothing releases it.

```text
plane within a page, 1 holder
G (min)  mean delay    p95    max
-------  ----------  -----  -----
      1         15s    29s    30s
      5        2.8m   4.9m   5.5m
     20       22.7m  29.5m  30.5m
     30       13.8m  20.5m  21.8m
     60       36.1m  49.7m  51.5m
    120       81.6m   1.8h   1.9h
    240        2.9h   3.7h   3.9h
    480        3.9h   5.7h   5.9h
    720        3.0h   5.7h   6.0h
   1440        3.0h   5.7h   6.0h

52k rows, 3 holders, re-sweep 25.5 min
G (min)  mean delay    p95    max
-------  ----------  -----  -----
      1        6.6m  16.8m  24.4m
      5        8.0m  19.5m  20.5m
     20        4.7m  14.6m  25.4m
     30        8.4m  17.3m  21.0m
     60       16.8m  36.5m  65.6m
    120       36.9m   1.9h   2.1h
    240        1.9h   4.0h   4.2h
    480        3.4h   5.9h   6.3h
    720        3.1h   5.9h   6.4h
   1440        3.0h   5.9h   6.3h
```

Here the 6 h is real. Two fixes, in order:

1. **Index these rows on their group** and release them on a group-plane admission. Use
   `index_held_signer_at`'s shape, not `index_waiting_on`: a parked row is exempt from `cap_hits`, so
   the second would put it on the transient ladder forever. **[read]**
2. **Past a page a release is not enough.** **[read]** `release_and_kick` runs one round; that round's
   Summary is head plus one backfill page, and the released row is behind the watermark. **[inf]** A
   `Fetch` of the released hash to `waiting_from` closes it. This also corrects #776's "at once".

### 1.6 The watermark map

```text
peers  planes  keys  P(cursor survives a cycle)  P(a walk of 52k rows finishes unbroken)
-----  ------  ----  --------------------------  ---------------------------------------
   30       8   240                       1.000                                 1.00e+00
   64       8   512                       1.000                                 1.00e+00
   70       8   560                       0.702                                 1.49e-08
  130       8  1040                       0.147                                 3.51e-43
   30      14   420                       1.000                                 1.00e+00
   64      14   896                       0.216                                 1.12e-34
   70      14   980                       0.168                                 3.17e-40
  130      14  1820                       0.044                                 7.82e-70
```

**[read]** A miss builds a fresh watermark that sweeps from the plane's start. Below the cap nothing
happens; above it a cursor rarely survives a cycle and a walk never finishes. The comment sizes the
map at 40 peers × 13 planes, and `scheduler.rs`'s own #740 note names 130 peers × 14 planes. The
shuffled order here is kind to LRU: a strictly cyclic order survives at zero. **[inf]** Planes are 8
after persist 61 (`ALL` minus `RETIRED_FRAMED`); not every coordinator need sweep each cycle.

---

## 2. M1: the event path under flood and restart storm

### 2.1 The bound

**[read]** c = (cores/2).clamp(1, 4): 1 at 2 vCPU, 2 at 4, 4 from 8. The rates are per 10 s and
sliding: stranger 25.6/s, standing 204.8/s. The audit's "256/2048" has no per-second reading.
`respond` is one X25519, one ML-KEM decapsulate and one HKDF, with no signature, and nothing benches
it.

**Service time s [cited, not ours].** kem768 decaps median cycles, fips203ipd v0.6: 38,184 (i7-1185G7
AVX-512), 121,529 (Cortex-A76 Neon), 201,900 (Cortex-A73 Neon), 444,600 (A73 scalar GCC)
([source](https://pablotron.org/2024/05/15/c11-fips203ipd-v0.6/)). Edge runs a different implementation,
RustCrypto ml-kem 0.3 plus x25519-dalek. At assumed 2–4 GHz that is 10–222 µs, KEM alone. **s = 250 µs is
[model]**, with X25519 and HKDF uncosted. No phone figure is assumed: read the breakpoints.

```text
cores  c      s=0.1ms     s=0.25ms     s=0.75ms        s=2ms       s=5ms      s=20ms
-----  -  -----------  -----------  -----------  -----------  ----------  ----------
    1  1  10,000/s 2%   4,000/s 6%  1,333/s 17%    500/s 46%  200/s 115%   50/s 461%
    2  1  10,000/s 2%   4,000/s 6%  1,333/s 17%    500/s 46%  200/s 115%   50/s 461%
    4  2  20,000/s 1%   8,000/s 3%   2,667/s 9%  1,000/s 23%   400/s 58%  100/s 230%
    8  4  40,000/s 1%  16,000/s 1%   5,333/s 4%  2,000/s 12%   800/s 29%  200/s 115%
   16  4  40,000/s 1%  16,000/s 1%   5,333/s 4%  2,000/s 12%   800/s 29%  200/s 115%
   32  4  40,000/s 1%  16,000/s 1%   5,333/s 4%  2,000/s 12%   800/s 29%  200/s 115%

breakpoints, c = 1 (a 2 vCPU canonical): strangers alone reach capacity at s = 39.1 ms; both budgets at s = 4.34 ms; both full queues outlast KEYING_BUDGET at s = 104 ms.
```

### 2.2 `DECAP_WORKERS_MAX` holds

c = 1 covers both budgets with a hundred times to spare. Four workers matter only past s = 17 ms. At s
= 20 ms, K = 500 saturates: 37% refused with standing. Bench `respond` and this is settled.

### 2.3 Restart storm

**[read]** `identity_has_standing` reads the live `peers` map. A restart empties it;
`PersistedBindingResolver` answers send, never this. So a peer is a stranger until rooted again:
**[inf]** by its link-borne announce after a link keys, or its 300 s announce. The canonicals primed
at boot are the exception. Rows, c = 1, h = 50 µs [assumption], re-dial one tick later [inf]:

```text
   K  links  spread       arm  first pass refused    T50    T100  dials/link  max queue  node_rate  saturated
----  -----  ------  --------  ------------------  -----  ------  ----------  ---------  ---------  ---------
 130      1     1.0   shipped                  0%   0.5s    1.0s        1.00          1          0          0
 130      1     1.0  hydrated                  0%   0.5s    1.0s        1.00          1          0          0
 130      1     5.0   shipped                  0%   2.3s    5.0s        1.00          1          0          0
 130      1     5.0  hydrated                  0%   2.6s    5.0s        1.00          1          0          0
 130      4     1.0   shipped                 51%  31.1s   31.9s        1.51          3        264          0
 130      4     1.0  hydrated                  0%   0.8s    1.0s        1.00          3          0          0
 130      4     5.0   shipped                  0%   4.2s    5.0s        1.00          1          0          0
 130      4     5.0  hydrated                  0%   4.2s    5.0s        1.00          1          0          0
 500      1     1.0   shipped                 49%   0.5s   31.9s        1.49          2        243          0
 500      1     1.0  hydrated                  0%   0.5s    1.0s        1.00          3          0          0
 500      1     5.0   shipped                 48%   2.5s   35.9s        1.48          2        241          0
 500      1     5.0  hydrated                  0%   2.5s    5.0s        1.00          1          0          0
 500      4     1.0   shipped                 87%  31.6s   62.6s        2.14          6       2283          0
 500      4     1.0  hydrated                  0%   0.8s    1.0s        1.00          7          0          0
 500      4     5.0   shipped                 62%  33.5s   66.5s        1.80          3       1601          0
 500      4     5.0  hydrated                  0%   4.2s    5.0s        1.00          3          0          0
1000      1     1.0   shipped                 74%  30.3s   93.5s        2.26          3       1261          0
1000      1     1.0  hydrated                  0%   0.5s    1.0s        1.00          4          0          0
1000      1     5.0   shipped                 74%  32.5s   96.9s        2.24          2       1241          0
1000      1     5.0  hydrated                  0%   2.5s    5.0s        1.00          2          0          0
2000      1     1.0   shipped                 87%  60.5s  154.5s        3.35          5       4698          0
2000      1     1.0  hydrated                  0%   0.5s    1.0s        1.00          7          0          0
2000      1     5.0   shipped                 86%  62.5s  158.2s        3.32          2       4644          0
2000      1     5.0  hydrated                  0%   2.5s    5.0s        1.00          3          0          0
```

`hydrated` is the proposal and what the comment assumes. The two arms are equal up to K ≈ 250 links in
a window, and past it the stranger rate is the whole of the storm. Time for all K to rekey, K = 2000
in 5 s: 158 s shipped, 5 s hydrated. Nobody is lost: the worst case re-dials four times.

### 2.4 Honest strangers in a flood

**[read]** The limiter is a sliding log of admits, so a flood's burst keeps its shape: at 100/s the
window is open 2.6 s in every 10, at 2000/s 0.13 s. A dial follows a 30 s tick with no jitter, and 30
is a multiple of 10. A stranger refused in the closed part comes back to the closed part.

```text
  flood  rate/s  analytic p  honest p per dial  first contact <1 s  <60 s  <300 s  standing p99  standing refused  saturated
-------  ------  ----------  -----------------  ------------------  -----  ------  ------------  ----------------  ---------
  sybil       5       1.000              1.000                100%   100%    100%         0.3ms                 0          0
  sybil      26       0.985              0.952                 95%   100%    100%         0.3ms                 0          0
  sybil     100       0.256              0.058                 18%    20%     45%         0.3ms                 0          0
  sybil     500       0.051              0.037                  2%    12%     20%         0.3ms                 0          0
  sybil    2000       0.013              0.008                  0%     0%      5%         0.3ms                 0          0
 single    2000       1.000              1.000                100%   100%    100%         0.3ms                 0          0
unident    2000       1.000              1.000                100%   100%    100%         0.3ms                 0          0
```

```text
flood/s                               arm  long-run p  independent, 10 dials  p per dial  first contact <300 s
-------  --------------------------------  ----------  ---------------------  ----------  --------------------
    100  shipped, retry on the tick +-1 s       0.256                   0.95       0.058                   45%
    100            retry jittered 15-45 s       0.256                   0.95       0.252                   98%
    100         paced limiter, tick retry       0.256                   0.95       0.298                   98%
    100                paced and jittered       0.256                   0.95       0.287                   95%
    500  shipped, retry on the tick +-1 s       0.051                   0.41       0.033                   30%
    500            retry jittered 15-45 s       0.051                   0.41       0.073                   48%
    500         paced limiter, tick retry       0.051                   0.41       0.044                   38%
    500                paced and jittered       0.051                   0.41       0.056                   35%
   2000  shipped, retry on the tick +-1 s       0.013                   0.12       0.008                    5%
   2000            retry jittered 15-45 s       0.013                   0.12       0.038                   22%
   2000         paced limiter, tick retry       0.013                   0.12       0.004                    2%
   2000                paced and jittered       0.013                   0.12       0.030                   18%
```

**The phase lock, exactly.** The tick is `tokio::time::interval(cadence)` with `MissedTickBehavior::Skip`
at `src/replication/scheduler.rs:940-945`, 30 s (`DEFAULT_CADENCE`), one per `(peer, kind)`, no jitter.
The window is `ROUTE_REQUEST_WINDOW` = 10 s at `route_fetch.rs:69`, a sliding log in `admit_at`
(`:408`), reached from `ReceiverOrder::admit` (`link_keying.rs:153`). A refused link closes
(`admission_refused`), and **[inf]** the next send is the next tick, so the dial returns at the same
phase of the 10 s cycle. **The jitter I would use:** after a round whose dial was refused, delay that
coordinator's next dial by a uniform draw from 0.5–1.5 × cadence, 15–45 s, the arm tested above. Leave
the healthy tick alone. Any spread of a few seconds or more should break the lock, since the closed
part is at most 10 s; I tested only this one.

- A single identity or an unidentified flood takes nothing from honest strangers; a Sybil flood does.
- Standing peers do not notice any flood: p99 0.3 ms, none refused.
- **Jitter is the fix.** Pacing the limiter also works at 100/s, but it spends the burst a restart
  needs (K = 130, shipped: 0% → 62% refused), and it does nothing at higher rates.
- At 500/s and above the first-contact columns are 40 strangers, one seed, and differ by noise.
- **[read]** A stranger with no route row meets 3.2/s first: at 100/s about 18 min against 2 for one
  who holds the row.
- **[read]** 6c87599's identify grace holds 128 for 1 s. An unidentified flood fills it from 128/s, and
  past that the race it closes reopens.

### 2.5 Queue sizes

The queue matters only when frames arrive faster than the keyer runs. At spread ≥ 1 s no queue passed
7 at K ≤ 2000 except past the rate bound. At spread 0, which is what a backlogged event loop delivers,
it decides everything. A job waits only while h < s/c, and neither h nor s is measured.

```text
    h       s  Q stranger  first pass refused   T100  max queue
-----  ------  ----------  ------------------  -----  ---------
 50us   100us          32                 25%  30.8s         32
 50us   100us         256                  0%   0.0s         65
 50us   250us          32                 55%  30.9s         32
 50us   250us         256                  0%   0.0s        104
 50us   750us          32                 68%  30.9s         32
 50us   750us         256                  0%   0.1s        121
 50us  2000us          32                 72%  31.0s         32
 50us  2000us         256                  0%   0.3s        126

   K       arm  queue  first pass refused    T100  max queue  worst wait
----  --------  -----  ------------------  ------  ---------  ----------
 130  hydrated     64                 31%   31.0s         64      16.0ms
 130  hydrated    256                  0%    0.0s        104      64.0ms
 130  hydrated   1024                  0%    0.0s        104     256.0ms
 130  hydrated   2048                  0%    0.0s        104     512.0ms
 500  hydrated     64                 67%   31.0s         64      16.0ms
 500  hydrated    256                 29%   31.0s        256      64.0ms
 500  hydrated   1024                  0%    0.1s        400     256.0ms
 500  hydrated   2048                  0%    0.1s        400     512.0ms
 130   shipped     32                 55%   30.9s         32       8.0ms
 130   shipped     64                 31%   30.9s         64      16.0ms
 130   shipped    128                  0%    0.0s        104      32.0ms
 130   shipped    256                  0%    0.0s        104      64.0ms
 500   shipped     32                 83%   62.0s         32       8.0ms
 500   shipped     64                 77%   61.8s         64      16.0ms
 500   shipped    128                 64%   61.9s        128      32.0ms
 500   shipped    256                 49%   31.0s        205      64.0ms
```

**[read]** `admit_handshake` spends sender and node slots before `submit`, so a saturated refusal
burns budget:

```text
Q stranger  keyed  refused saturated (slot spent)  max queue
----------  -----  ------------------------------  ---------
        32     53                             203         32
       256    256                               0        235
```

A larger queue costs about 1.2 KB a job and bounded wait, and stale jobs skip at no cost. So
`DECAP_QUEUE_STRANGER` = 256 and `DECAP_QUEUE_STANDING` = 1024. **If `event.handler.duration` shows h
above s/c, neither change matters, and I would still make them.**

### 2.6 The stranger rate buys links

```text
stranger budget    rate  over a canonical's routed share  idle links held  of the 1024 envelope
---------------  ------  -------------------------------  ---------------  --------------------
             32   3.2/s                             1.0x              384                   38%
             64   6.4/s                             1.9x              768                   75%
            128  12.8/s                             3.8x            1,536                  150%
            256  25.6/s                             7.7x            3,072                  300%
```

The keyer is not the constraint; the links are. **[read]** No count bounds keyed strangers. Since
leviculum#56 the envelope is an ERROR, not an evictor, so the damage is memory, keepalives and the
first-words bundle per link, which I did not cost. Cutting the rate to 64 fits the envelope and costs
honest strangers four times over. So bound the count and keep the rate. `HANDSHAKES_STRANGER_NODE`
is seven times a canonical's routed share, which is the room a burst of honest strangers has.

---

## 3. M2: the reply lane under reverse-dead peers

### 3.1 An honest reverse-dead peer barely registers

**[read]** Replies hold 8 queued + 1 on the wire. Expiry is max(10 s, 4.74 gaps), checked at dequeue.
A dead reverse path fails a send in 6 s.

```text
stall per send  max jobs  shed  expired  mean occupancy  bytes pinned
--------------  --------  ----  -------  --------------  ------------
            6s         1     0        0            0.20             0
           15s         1     0        0            0.49             0
           45s         2     0      120            0.99             0
           60s         3     0      120            1.48             0

jobs  send  shed  expired at dequeue  left the lane
----  ----  ----  ------------------  -------------
   2    6s     5                   1              2
   4    6s     3                   3              2
   8    6s     0                   6              2
  16    6s     0                   6              2
```

**[inf]** A reverse-dead peer never saw our Summary, so it sends no Diff and pins no page. Eight jobs
exist for the Pull burst, and eight is exact: four sheds three.

### 3.2 The bound holds per lane and not per node

A hostile or broken peer sending Diffs and not reading:

```text
stall  lam/s  mean jobs  max jobs  max bytes  shed  expired  failed  inbox drop  Deliver lag p99  max
-----  -----  ---------  --------  ---------  ----  -------  ------  ----------  ---------------  ---
   6s   0.05        0.3         2     1.0MiB    0%        0      14           0              0ms  0ms
   6s    0.2        1.8         4     2.0MiB   14%       10      47           0              0ms  0ms
   6s    1.0        3.1         4     2.0MiB   70%       40      53           0              0ms  0ms
   6s    5.0        3.3         4     2.0MiB   93%       50      51           0              0ms  0ms
   6s   50.0        3.3         4     2.0MiB   99%       50      51           0              0ms  0ms
  60s   0.05        1.6         4     2.0MiB   20%        8       4           0              0ms  1ms
  60s    0.2        3.0         4     2.0MiB   67%       15       5           0              0ms  0ms
  60s    1.0        3.2         4     2.0MiB   93%       15       5           0              0ms  0ms
  60s    5.0        3.3         4     2.0MiB   99%       15       5           0              0ms  0ms
  60s   50.0        3.3         4     2.0MiB  100%       15       5           0              0ms  0ms
```

Full pages stop at 2 MiB and Delivers are untouched, as `reply_lane.rs` claims. But:

```text
peers  planes  lanes  byte pin, ceiling  full pages
-----  ------  -----  -----------------  ----------
    1       8      8             20 MiB      16 MiB
   10       8     80            200 MiB     160 MiB
   40       8    320            800 MiB     640 MiB
  130       8   1040          2,600 MiB   2,080 MiB
  500       8   4000         10,000 MiB   8,000 MiB
```

**[read]** A responder is built on a peer's first contact. **[inf]** I did not trace whether a
stranger's Diff is served. So add a node-wide byte bound: 64 MiB is 3.7 times a healthy canonical's 17
MiB in flight.

### 3.3 What the lane bought

```text
stall  burst  parked p50  parked max  parked inbox drop  lane p50  lane max  lane inbox drop
-----  -----  ----------  ----------  -----------------  --------  --------  ---------------
   6s      1       5.50s        5.5s                  0     0.00s      0.0s                0
   6s      4      23.51s       23.5s                  0     0.00s      0.0s                0
   6s      8      47.72s       47.9s                141     0.00s      0.0s                0
  15s      1      14.50s       14.5s                  0     0.00s      0.0s                0
  15s      4     104.74s      119.8s                104     0.00s      0.0s                0
  15s      8     119.52s      119.5s                272     0.00s      0.0s                0
  60s      1     239.53s      299.5s                 33     0.00s      0.0s                0
  60s      4     359.63s      419.8s                165     0.00s      0.0s                0
  60s      8     419.76s      479.8s                328     0.00s      0.0s                0
```

The field's 79 s sits between the parked arm's 15 s rows. The lane holds Deliver lag at the step time.

### 3.4 The knobs

```text
expiry  failed sends (a stall each)  expired  sent healthy  of those, past the round  shed
------  ---------------------------  -------  ------------  ------------------------  ----
    3s                           17       21            36                         0    16
    5s                           19       16            37                         0    18
   10s                           19        8            39                         0    24
   20s                           20        0            39                         0    31
   60s                           20        0            39                         0    31
  none                           20        0            39                         0    31

jobs  byte pages  byte bound  shed of the burst  max pinned
----  ----------  ----------  -----------------  ----------
   8           1      0.5MiB                88%      0.5MiB
   8           2      1.0MiB                75%      1.0MiB
   8           4      2.0MiB                50%      2.0MiB
   8           8      4.0MiB                 0%      4.0MiB
   4           4      2.0MiB                50%      2.0MiB
  16           8      4.0MiB                 0%      4.0MiB
```

- **Expiry: keep 10 s.** Shorter or longer barely moves failed sends. It is one stall per S either way.
- **`REPLY_QUEUE_BYTES`: keep.** The burst of eight Diffs that would want more is not what a round
  sends; a round sends one per plane.
- **Not the lane's, noted.** Below 11.7 kB/s (93 kbit/s) a full 512 KiB page cannot finish inside
  `REVERSE_PATH_MAX_TRANSFER`. **[inf]** A cold peer on such a reverse path re-asks the same page and
  never catches up. A page also outruns its expiry at every shaped class, if a shaped Deliver takes
  that path, which I did not trace.

---

## 4. What validates each prediction in a run

Names are the audit's §5. Most do not exist yet.

| Model | Prediction | Metric | Refuted if |
|---|---|---|---|
| M8 | a refuser admits within P/N of its own restart | `apply_refusals:refused_then_admitted:{class}`, `ciris.edge.refusal.attempts` | a row refused before a restart waits past the re-sweep after it |
| M8 | terminal only past 8 refusals, at 20 min to 3 h by corpus | `apply_refusals:moved_to_terminal` with `advertise_resweep_*` | terminal arrives faster than offers allow |
| M8 | #1200 fork = share old at mint, no convergence | `retry_suppressions`, `refusal.attempts` by `disposition`; two rosters compared by digest | the fork closes by itself |
| M8 | cursor thrash past 512 keys | `advertise_resweep_*`; a peer stuck on page one. Needs a new `sweep_cursor_evictions` | evictions at K > 512 leave cycle time alone |
| M1 | first links after a restart refused as strangers | `link_seal:refused_handshake_node_rate:stranger` on a restart | standing fires for ordinary peers in the first seconds |
| M1 | rekey time K/25.6 s past 256 links | `ciris.edge.seal.keying.duration` by `standing`, link count against time | all K key inside a window |
| M1 | queue fills only under backlog | `seal.keyer.queued`, `refused_decap_saturated`, `event.handler.duration` | saturation at low event lag |
| M1 | workers idle at the budget | `seal.keyer.workers`, `seal.handshake.decap` | decap above 4 ms at c = 1 |
| M1 | first contact phase-locked | `ciris.edge.first_contact.duration`; bimodal under a flood | it fits 1-(1-p)^n |
| M2 | Deliver lag at step time under a stall | `replication.inbound.wait` by `kind` | inbound wait tracks stall length |
| M2 | shed only from a peer sending past 1/S | `reply_shed`, `reply.queued`, `reply.wait`, `reply_expired` | `reply_shed` from honest peers |

**The first four measurements to take:** `respond` on a canonical (s), `event.handler.duration` (h),
peers × planes swept per cycle, and one real restart's dial spread.

---

## 5. Sanity

Every run ends in checks, and a failure exits 1.

- **Analytic cases, sim against closed form:** M/M/c/K and M/D/1/K blocking; Cobham's priority waits;
  fluid burst loss (1436 = 1436); a sliding window's r/λ; shed per stall λS − 9; a re-sweep of 51
  rounds at 52k; 1350 s on a 30 s grid; last node's wait P/N.
- **Moved parameters:** cap hits 2 and 5 give terminal at the 7th and 10th; larger queue, slower decap,
  more workers, harder flood, longer stall, smaller byte bound each move the outcome the expected way.
- **Two checks failed first, and each was the model teaching me:** blocking at ρ = 1.5 ran low
  because a 1 s service time let the 10 s stale skip free places, so the textbook comparison now
  turns that off. And I expected a doubled `TRANSIENT_BASE` to delay terminal; it brings it a refusal
  sooner, because the count runs off reaching the cap. The expectation changed, not the model.

---

## 6. What this model does not cover

CPU contention with rounds and SQL on a 2 vCPU host (cover it by reading s as s/(1−u)); the event
channel's own bound; leviculum's link establishment; memory of a keyed link; first-words bytes;
proactive push (#927), which can raise a refuser's attempt count without an ask; more than one row
in play, so the 4096 ordinary ring's eviction under a wave of refusals; persist #1192's real upgrade
path, since ≤ 61.0.1 peers exist only on candidate lanes and v43 → v44 crosses far more (v61 refuses
`+00:00` rows from v60 outright, which are different rows with no restart to save them, until their
signers re-sign).

---

## 7. Assumptions that matter most, most first

| Assumption | Used in | If wrong |
|---|---|---|
| An upgrade is a process restart | §1.3, the whole M8 verdict | a hot swap would need the reset this says is unneeded. **[read]** wheels and cdylibs; no reload path |
| Peers rooted only by announce or a keyed link after a restart | §2.3 | I read every `peers.insert` site, not a run. If a host primes everyone at boot, row 1 of §0 falls |
| A refused link re-dials on its next 30 s tick | §2.3, §2.4 | **[inf]** from the close and the round; if another path re-dials sooner, the phase lock weakens |
| h and s | §2.5 | queue rows 3 and 4 apply only if h < s/c |
| Spread of a real storm | §2.3, §2.5 | a wide spread makes both queues moot |
| Offers: corpus, page, one or two Summaries per cadence | §1 | sets P; the verdict holds, the minutes move |
| Full mesh at 9 and 30, degree 8 at 130, 30 s down | §1.3 | moves `sit`, not who dominates it |
| 8 live planes | §1.6, §3.2 | moves the crossing point |

---

## 8. Prior art, and whether edge should adopt a tool

Added after the numbers; nothing here moved one. "Read" means I opened that code at its default
branch on 2026-11-05. Links are only to pages I opened.

| Project | What it models | Read | Against this document |
|---|---|---|---|
| [WireGuard](https://github.com/WireGuard/wireguard-linux/blob/stable/drivers/net/wireguard/timers.c) | handshake flood, in shipped kernel code | `timers.c`, `messages.h`, `ratelimiter.c`, `receive.c`, `cookie.c` | **Confirms §2.4, §2.5.** Retransmit is `REKEY_TIMEOUT` (5 s) plus a random `HZ/3`, so handshakes never sit on a grid. Limiter is a per-source token bucket, 20/s, burst 5, not a sliding log. `MAX_QUEUED_INCOMING_HANDSHAKES` 4096 sits far above the rate, and load is declared at 1/8 of it. **New:** a cookie reply makes a flooder prove its address before crypto; there the proof is a round trip, and edge's nearest analogue is LINKIDENTIFY, already free to mint |
| [Tor `onion_queue.c`](https://gitlab.torproject.org/tpo/core/tor/-/raw/main/src/feature/relay/onion_queue.c), [`cpuworker.c`](https://gitlab.torproject.org/tpo/core/tor/-/raw/main/src/core/mainloop/cpuworker.c) | the closest thing to the keyer: a handshake queue in front of a worker pool | `have_room_for_onionskin` | **Refines §2.5.** Tor bounds the queue by time: always room under 50, else refuse past estimated `entries × usec / cpus` of 1750 ms. That is a better shape than a count: it needs no s, it measures it. With `KEYING_BUDGET` as the target, a count of 1024 is only my stand-in. Tor's 50-entry floor also exceeds edge's 32 |
| [Shadow](https://github.com/shadow/shadow/blob/main/docs/limitations.md) | real binaries on a simulated network, deterministic | `limitations.md`, `compatibility_notes.md`, `design_2x.md`, issues [#3832](https://github.com/shadow/shadow/issues/3832), [#3242](https://github.com/shadow/shadow/pull/3242) | the tool to adopt, below. It "models the CPU as being infinitely fast", so it cannot give s or h |
| [tornettools](https://github.com/shadow/tornettools) | a Tor network staged from public metrics | README, `stage.py` | **The method to copy.** Real consensus and user data stage the network, and [Once is Never Enough](https://www.robgjansen.com/publications/neverenough-sec2021.pdf) (cited there; not opened) is why one run is not a result. M8's corpus and peers should be staged from a real census the same way |
| [Polkadot under Shadow](https://hackmd.io/@kamilsa/ry-rWsfmbe) | ~12 real Rust nodes | write-up | **Feasibility.** Deterministic by seed. Needed jemalloc off and Unix sockets moved to TCP behind a flag; edge's source has neither |
| [gossipsub-hardening](https://github.com/libp2p/gossipsub-hardening), [libp2p test-plans](https://github.com/libp2p/test-plans) | gossip under attack on testground; transport interop | READMEs | Compare only. Hundreds of containers on a large host: the cost Shadow avoids. Testground's attack scenarios are the shape of §2.4 as a real run |
| [TigerBeetle VOPR](https://github.com/tigerbeetle/tigerbeetle/blob/main/src/testing/packet_simulator.zig), [FoundationDB](https://apple.github.io/foundationdb/testing.html) | deterministic simulation of one consensus cluster | `packet_simulator.zig`; FDB's page | Different target: they hunt safety bugs. `path_clog_*` and FDB's swizzle-clogging are the fault M2 sweeps by hand; `partition_symmetry` is a reverse-dead peer. Reusable as fault vocabulary for `src/replication/sim.rs` |
| [Maelstrom](https://github.com/jepsen-io/maelstrom/blob/main/src/maelstrom/net.clj) | a test bench for small protocols | `net.clj` | Latency, loss, partitions. Too abstract for link and CPU; not useful here |
| [Warnet](https://github.com/bitcoin-dev-project/warnet), [SimBlock](https://github.com/dsg-titech/simblock) | real bitcoind on Kubernetes; a block-propagation simulator | READMEs | Warnet is the live-fleet alternative to Shadow, with real time and real cost. SimBlock is the hand-built approach this file already is |
| [Complement](https://github.com/matrix-org/complement) | black-box federation conformance | README | Same role as CIRISConformance. No load model found |
| [Reticulum](https://github.com/markqvist/Reticulum/tree/master/tests) | unit tests only | directory listing | No network simulator there; I found none for LXMF. Yggdrasil and I2P: my one search found nothing, which is not absence |
| [discv5 rationale](https://github.com/ethereum/devp2p/blob/master/discv5/discv5-rationale.md) | design notes | text | Liveness checks on their own schedule to avoid DoS. No model of handshake queues |
| [Nym](https://github.com/nymtech/nym) | mixnet | README | Nothing relevant to these three models in what I read |
| [AWS](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter) | retry guidance | article | **Confirms §2.4:** "adding some jitter to all timers, periodic jobs, and other delayed work". The 30 s tick is exactly that |
| [Google SRE](https://sre.google/sre-book/addressing-cascading-failures/) | overload | chapter | **Confirms** jitter and restart cold-start (§2.3: "when the cache is completely empty, 100% of requests are costly", which is an empty `peers`). **Pushes against §2.5:** queues "50% or less" of the pool for steady traffic. It allows sizing for bursts, which is the case argued there, and Tor's time bound answers both |
| [Metastable Failures in the Wild](https://www.usenix.org/conference/osdi22/presentation/huang-lexiang) | outages that outlive their trigger | abstract page only | Frames the question M8 and §2.3 ask. The re-dial loop is a retry that a closed window keeps alive, but it costs a bounded amount, and the storm in §2.3 ends: I see no sustaining loop here. Not shown |
| [RFC 9000 §8.1](https://www.rfc-editor.org/rfc/rfc9000.html) | QUIC Retry | §8.1.2 | Defers server state until the client shows it received a token. The same idea as the cookie |

Not reached, so no claim: Chutney, Portal and ethp2p simulators, Kademlia sims, Nostr, ns-3 or Mininet
stacks, Antithesis, WebRTC SFU and congestion sims (those belong to M6, not these three).

**What changes in the recommendations.** Row 2 of §0 stands, stronger. Rows 3 and 4 stand as numbers
for this cut; **the better next design is Tor's: bound the keyer's queues by estimated wait against
`KEYING_BUDGET`, with a floor, and retire both counts.** Bucket versus log: I tested a shared bucket
(§2.4) and it costs a restart, and WireGuard's is per source, which edge already has, so the log stays.

**Recommendation: adopt Shadow for one experiment, keep the Python.** They answer different questions.

- **Python** sweeps constants fast, with analytic checks. It cannot test its own assumptions, and §7's
  worst three are about real code paths.
- **Shadow** runs `edge_node` itself, and would settle them: does a restart leave peers strangers, when
  does a refused link really re-dial, what is the spread of a real storm, does the row come back on
  the re-sweep.
- **Its limit is M1's CPU.** With an infinitely fast CPU the queue never fills, so inject s through the
  existing `set_decap_delay` seam, which sleeps and so advances simulated time. Measure s and h on a
  real host regardless.
- **Risks, unproven until tried:** leviculum's TCP under Shadow (issue #3832 was a tokio stall, since
  patched); IPv4 only; persist's SQLite on a shared host; static linking. Edge's source shows no Unix
  sockets or jemalloc.
- **First experiment:** 30 `edge_node` hosts over TCP, one canonical restarted, then a rolling restart
  with a row refused by a stand-in build. Repeat over seeds, per Jansen et al. Then compare to §2.3 and
  §1.3 and record where the Python was wrong.

Not recommended now: Warnet-style clusters (cost), or a FoundationDB-style simulator of edge's own
(worth it only if `src/replication/sim.rs` outgrows its scope).
