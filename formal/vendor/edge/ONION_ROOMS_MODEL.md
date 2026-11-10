# FSD — Rooms over the onion tier: a quantitative model and design sketch

**Status:** model and design sketch, not a measurement and not a ruling. Every table below is
produced by `tools/models/onion_rooms.py` (`python3 -I tools/models/onion_rooms.py`, standard
library, seeded, no network, no cargo) and pasted verbatim from its output of 2026-11-05. Two runs
print the same bytes. **Direction:** Eric, 2026-11-04, verbatim: "yes we need rooms over onion, that
is the goal for the onion tier, the way the mesh works now the shaped traffic provides us a
self-growing mesh to carry the onion traffic". Later the same day, verbatim: "Why do we care about
conferred or unconferred? The canonicals are just the TOFU bootstrap and directory service". §I
answers that.

**Sources, in order of authority:** CC rc17 5.4.3, 5.4.6 (items 1–10, "Who carries what"), 3.1.4,
1.13.3.1, 1.13.3.3, 1.13.3.4, 6.1.5.3; `constitution/claims.tsv` `CLM-onion-layer-model` and
`formal/INVARIANTS.tsv`; edge branch `feat/onion-v44` at 1eeeb14 (`src/onion/*`,
`src/transport/onion_layers.rs`, `docs/onion_packet_wire.md`, `FSD/ONION_ROUTING.md`,
`docs/ONION_TIER_MODEL_2026-10-22.md`); `FSD/TRANSPORT_TIERS_MODEL.md`, `FSD/CIRIS_MESH.md`;
CIRISPersist#1175; persist `src/federation/trust_root.rs`.

**[inf]** marks an inference not checked by running code. **[assumption]** marks a parameter the
brief did not supply; §K lists every one. No time estimates are made anywhere in this document.

---

## 0. The answer

**Does the shaped mesh carry it? In bytes, yes. As the tier is written today, no.** A home that
offers relay adds 0.37 crossings/s of real budget it already pays for as cover, which is 7.9 people
at the modelled chat load. That is the self-growing claim and the arithmetic holds. But four rules
stand between that budget and an onion packet:

1. **The cap.** Active relays are at most 3 × conferred. At nine seats that is 27 relays whether
   there are 100 homes or 10,000: 66 crossings/s against 3,740, a factor of 57, and at 10,000 homes
   a home is dealt in 0.18 % of hours.
2. **The bound against the uniform pick.** `sender.rs` picks any member of the next layer, and
   `layer_peers()` asks for a shaped link to all of them. Eight links fit a layer of 4 at most. A
   layer of 9, which is what nine seats deal, needs 18. This one is not in the brief and it holds
   even with the cap gone. It is the larger of the two.
3. **Federation-reach rendezvous rows.** 22 KB per person per hour, to every node, is 5.8 home-link
   budgets at 1,000 people and 58 at 10,000. Rooms cannot use that door.
4. **Shaping uptake.** Only `server` shapes by default, so supply is whoever turns it on
   (`FSD/PRIVACY_MODES.md` §4.1 says the same).

**The recommended design, in five lines.**

- **Carrier:** the route is a walk over standing shaped links (Tarzan's rule). Nothing is dialled
  per route. Relay links are hash-assigned, degree D = 6, so a sender can compute the graph.
- **Sybil bound:** drop the layer cap. Hop 1 is a sticky guard chosen from the sender's own
  consented contacts, with a serve seat as last resort, which is the CC's existing carrier order.
  Minted identities are nobody's contact, so the bound does not move with the Sybil budget (§I).
- **Mailbox:** two member-owned always-on nodes per room, not a seat. A seat keeps a row for two
  hours at most; a phone sleeps for eight (§E).
- **Sync:** row push plus an hourly version-vector digest, with catch-up pulls on routes that the
  pull packet carries (§D).
- **Node rule:** a room-over-onion node holds no link to a co-member, direct or shaped, and runs
  shaped-only. If it keeps those links, the link graph names the room and the onion hid nothing
  (§F).

**What a person gets:** message to mailbox about 45–50 s mean, about 1.5 minutes to the reader at
home class, 2.6 minutes on cellular. No calls, no receipts, no typing, images to 64 KiB. Mail-like
chat.

**What it does not remove.** Which links exist: never. That your groups exist: only under the node
rule above, and only from outsiders. Against a compromised relay at low load there is no mixing
crowd to speak of (0.10 at a home); only end-to-end cover helps, and that costs 36 % of a person's
slice of a home at D = 45 s.

---

## 1. Corrections to the inputs

| The brief or an earlier document says | The source says | Effect here |
|---|---|---|
| 15,200 B packet, 6 × 1,168 B slots (also `FSD/ONION_ROUTING.md` §5) | `src/onion/packet.rs:95` asserts `PACKET == 15_296`, `SLOT == 1184`: the block grew by a 16 B commitment. `docs/onion_packet_wire.md` agrees | The model uses 15,296 B. Body capacity 8,174 B. A blob is 3,552 B |
| A relay's "12 frames per packet" (`ONION_TIER_MODEL` §e) | At the 16,272 B frame, `CONP` ‖ packet is 15,300 B, inside one frame body of 16,248 B **[inf]** | One packet costs one frame, so every rate here is ρλ of the class. The 948 B left over carries nothing |
| CC 5.4.3: mean wait 1.6 s server, 4 s home, 8 s Wi-Fi | Those figures come from a ~1,400 B MDU (`docs/SHAPING_RHO_W`). At 16,272 B the gap is 2.3, 5.8, 11.6 s | The model uses the 16,272 B figures. The CC's copy understates latency on this frame size by about 1.45× and should be revised |
| Each relay-offering home adds 7 net slots | True with no layer reserve. With `DEFAULT_LAYER_RESERVE_LINKS = 4` held it adds 3 | §A.8. Using standing links as the layer links removes the reserve |
| The rendezvous node is any layer-3 seat | Yes, and the deal makes that a third of the seats: three at M = 9, one at M = 3 | §E.3 |

---

## 2. Constants

| Symbol | Value | Source |
|---|---|---|
| F, shaped frame | 16,272 B | brief; `transport_tiers.py` |
| class rates | server 7,000, home 2,800, phone-wifi 1,400, phone-cellular 350, seat 33,000 B/s | CC 5.4.3 table |
| ρ | 0.5 | CC 5.4.3 |
| bound | 8 shaped links, full class rate; seat links outside the eight | CC 5.4.3 |
| packet, body capacity | 15,296 B, 8,174 B | `packet.rs:83`, `:87` |
| route | 3 hops; targeted delivery 6 (3 + receiver's 3) | CC 5.4.6 items 4, 6; `SLOTS = 6` |
| μ, hold clamp, hold bound | 2 s, 60 s, 256 packets | `policy.rs`, `relay.rs` |
| cap, floor | others ≤ ⌈c × conferred⌉ per layer, c = 2; ≥ 3 per layer | CC 5.4.6 item 4 |
| seats | 9 planned, 3 near term | brief |
| mailbox bound | 64 packets per key; retention period + grace | `FSD/ONION_ROUTING.md` §8, §10; CC 3.1.4 |

**The unit is the crossing:** one onion packet over one shaped link, one way. A link carries
ρλ(class) crossings per second one way, and it costs nothing extra because it replaces a cover
frame. A node's real budget not used by rows is the (1 − u_row) share of that.

---

## A. Self-growing capacity

**Formulas.** Link capacity c(class) = ρ · rate / F packets per second. With relays i, availability
a_i and D links each used for onion traffic, tier capacity is

Θ = Σ a_i · D · ρ · E[min(rate_i, rate_j)] / F · (1 − u_row) + Θ_seat

where the minimum is the lower-of-two rule and Θ_seat = C · (C/3) · ρ · 33,000/F · (1 − u_row) per
stage, three stages. One room message costs κ(n) = 6 + 4(n − 1) crossings (§C, reply routes) or 6n
(forward routes). A person costs p = m·κ(n) + upkeep crossings a day. People carried = Θ / (p/86,400).

```text
-- A.1 one link, one packet per frame (15,300 B of the 16,272 B frame; goodput = body capacity 8,174 B)
         class     B/s    gap  real pkt/s  real pkt/h  goodput B/s  GB/mo each way
--------------  ------  -----  ----------  ----------  -----------  --------------
          seat  33,000   0.5s      1.0140       3,650        8,289            85.5
        server   7,000   2.3s      0.2151         774        1,758            18.1
          home   2,800   5.8s      0.0860         310          703             7.3
    phone-wifi   1,400  11.6s      0.0430         155          352             3.6
phone-cellular     350  46.5s      0.0108          39           88             0.9
seat link / home link = 11.8; a home's eight links, one way: 0.688 pkt/s of cover it already pays for
```

**Reading.** A seat link is worth 11.8 home links. A home's eight links carry 0.688 packets/s one
way of cover it pays for anyway. On the wire an onion packet is the same frame as cover: the
marginal cost of relaying is CPU and nothing else, until ρ. That is the sense in which Eric's claim
is exactly right.

```text
-- A.2 the floor and the width a layer can have under the bound (uniform pick needs next-layer complete)
width w  layer links needed (prev+next)  fits 8  fits reserve 4
-------  ------------------------------  ------  --------------
      3                               6     yes              NO
      4                               8     yes              NO
      9                              18      NO              NO
     30                              60      NO              NO
    333                             666      NO              NO
layer_peers() asks a relay for both adjacent layers in full and sender.rs picks uniformly, so a non-seat relay fits only w <= 4 (w <= 2 inside the reserve; the floor is w = 3). A next hop without a shaped link is refused onion_next_hop_unroutable
```

**Reading: the limit nobody listed.** A uniform pick needs a shaped link from every relay in a layer
to every relay in the next. `layer_peers()` (`runtime.rs:213`) asks for both adjacent layers in
full, and a next hop with no shaped link is refused `onion_next_hop_unroutable`
(`docs/onion_packet_wire.md` §5). So a non-seat relay fits a layer of width 4 at most. Inside the
four-link reserve it fits width 2, which is below the floor of 3. Lifting the cap alone would not
give the mesh its capacity; it would produce routes that refuse.

```text
-- A.3 the deal: active relays vs relay-offering homes, cap c = 2 (per layer, others <= ceil(2 x conferred))
conferred C  homes  dealt others  waiting  share dealt  active  layer width
-----------  -----  ------------  -------  -----------  ------  -----------
          3    100             6       94         6.0%       9            3
          3   1000             6      994         0.6%       9            3
          3  10000             6     9994         0.1%       9            3
          9    100            18       82        18.0%      27            9
          9   1000            18      982         1.8%      27            9
          9  10000            18     9982         0.2%      27            9
         30    100            60       40        60.0%      90           30
         30   1000            60      940         6.0%      90           30
         30  10000            60     9940         0.6%      90           30
        100    100           100        0       100.0%     200           67
        100   1000           200      800        20.0%     300          100
        100  10000           200     9800         2.0%     300          100
        333    100           100        0       100.0%     433          144
        333   1000           666      334        66.6%     999          333
        333  10000           666     9334         6.7%     999          333
       1000    100           100        0       100.0%    1100          367
       1000   1000          1000        0       100.0%    2000          667
       1000  10000          2000     8000        20.0%    3000         1000
```

```text
-- A.4 fleet crossings/s and messages: nine seats, then homes, by class mix (D = link degree used; u_row 0.25; availability {'server': 0.999, 'home': 0.95, 'phone-wifi': 0.3})
kappa = 82 crossings per message at n = 20; a person = 4,000 crossings/day = 0.0463/s
nine seats alone: seat links only, 3 per stage, 3 stages: 61.6 crossings/s total, 20.5/stage; a six-hop route crosses two stages twice, so 10.3 packets/s end to end
       mix  homes  dealt  Theta capped /s  Theta all /s  ratio  msg/h capped  msg/h all  persons capped  persons all
----------  -----  -----  ---------------  ------------  -----  ------------  ---------  --------------  -----------
     homes      0      0             61.6          61.6   1.0x         2,704      2,704           1,331        1,331
     homes    100     18             66.0          98.4   1.5x         2,898      4,319           1,426        2,125
     homes   1000     18             66.0         429.4   6.5x         2,898     18,852           1,426        9,275
     homes  10000     18             66.0       3,739.7  56.6x         2,898    164,182           1,426       80,777
10% server      0      0             61.6          61.6   1.0x         2,704      2,704           1,331        1,331
10% server    100     18             66.1          99.1   1.5x         2,902      4,352           1,428        2,141
10% server   1000     18             66.1         436.9   6.6x         2,902     19,179           1,428        9,436
10% server  10000     18             66.1       3,814.1  57.7x         2,902    167,449           1,428       82,385
 50% phone      0      0             61.6          61.6   1.0x         2,704      2,704           1,331        1,331
 50% phone    100     18             63.4          76.7   1.2x         2,784      3,368           1,370        1,657
 50% phone   1000     18             63.4         212.8   3.4x         2,784      9,344           1,370        4,597
 50% phone  10000     18             63.4       1,574.0  24.8x         2,784     69,101           1,370       33,998
the seat core has a trunk: 72 non-seat slots at home class = 4.65 pkt/s out, 880 msg/h at n = 20, 528 persons, and at most 72 attached nodes. Every 'capped' figure above is bounded by this when homes off the deal must reach the core
if the mailbox must use forward routes (A.10): kappa 120, persons x 0.72
three canonicals + six homes, the minimum deal: complete layers of 3: 3.75 crossings/s, 81 persons, 165 msg/h at n = 20
one home at D = 6: 0.368 crossings/s = 7.9 persons; demand per home at 4 persons = 50% of what it adds
```

**Reading.**

- **Nine seats alone** carry 61.6 crossings/s, nearly all on the seat links. But they carry it for
  at most 72 attached nodes, and the trunk into the core is 72 home-class slots: 4.65 packets/s,
  880 messages/hour at n = 20, 528 people.
- **The cap flattens the curve.** Homes on the deal add 4.4 crossings/s and stop there, at any fleet
  size. Without it, 10,000 homes carry 3,740 crossings/s, about 80,800 people on reply routes and
  about 58,000 on forward routes.
- **Class mix.** A tenth of relays at server class moves it 2 %. Half the relays being phones cuts
  it by more than half, because phones sit at 30 % availability and pull every link they touch to
  1,400 B/s.
- **Self-sustaining ratio.** One home at D = 6 adds capacity for 7.9 people, or 5.7 on forward
  routes. The slot rule says a home seats about seven leaves. The two numbers meet, so a fleet of
  one relay-offering home per about six people carries itself **[inf]**. At four people per home it
  runs at half of what it adds.
- **The near term.** Three canonicals and six homes is the smallest legal tier: 3.75 crossings/s,
  165 messages/hour at n = 20, 81 people.

```text
-- A.5 how many conferred relays demand needs under the cap (each conferred home brings two others)
persons  crossings/s  conferred needed  active relays
-------  -----------  ----------------  -------------
   1000         46.3                 9             27
  10000        463.0               555           1665
 100000      4,629.6              6219          18657
```

**Reading.** Under the cap as ruled, 1,000 people need no more conferral than the nine seats, but
only on paper, because the trunk says 528. 10,000 people need 555 conferred relays and 100,000 need
6,219. The steward would sign one conferral per three relays, indefinitely, and that is what "the
conferred count caps growth" means in practice.

```text
-- A.6 relay uptime: the minimum deal, and the client's small-set line (below ten per layer)
home availability  P(all six homes of a 3 seat + 6 home deal answer)  answering per layer, 9 seats + 18 homes
-----------------  -------------------------------------------------  ---------------------------------------
             0.99                                              94.1%                                      8.9
             0.95                                              73.5%                                      8.7
              0.9                                              53.1%                                      8.4
              0.8                                              26.2%                                      7.8
nine seats cap a layer at 3 + 6 = 9, so the client's 'set is small' line (below ten) never clears; ten per layer needs at least 12 conferred (4 per layer, width 12)
```

**Reading: uptime is not the limit, except at the minimum deal.** With three seats and six homes,
every home must answer or the tier is unavailable, which at 95 % availability is 73.5 % of hours.
Nine seats clear it easily. Nine seats also cap a layer at 9, so the client's "the set is small"
line (below ten per layer, item 4) never clears at any fleet size.

```text
-- A.7 federation-reach rendezvous rows: 22,072 B per person per hour, to everyone (CC 3.1.4)
persons  B/s to every node  home link budgets  GB/mo per node
-------  -----------------  -----------------  --------------
    100                613               0.58               2
   1000              6,131               5.84              16
  10000             61,311              58.39             159
 100000            613,111             583.92           1,589
```

**Reading.** CC 3.1.4 gives the rendezvous row reach "everyone", and it rotates hourly. That is
tolerable for the targeted-anonymous-delivery case it was written for, where few receivers publish.
Every room member on the tier publishing one would spend one whole home-link budget, on every
node, at about 170 people. **Rooms must not use it.** Route material stays inside the room (§D).

```text
-- A.8 free shaped slots F(H) = 72 + (net) x H; reserve held vs not
homes  slots, no reserve (+7)  slots, reserve 4 held (+3)
-----  ----------------------  --------------------------
    0                      72                          72
  100                     772                         372
 1000                   7,072                       3,072
10000                  70,072                      30,072
```

```text
-- A.9 can a route exist? share of the target set reachable, sparse layers vs a walk on the standing graph
relays  width  d out  entries  3 hops to r1 (blob join), 1 blob  5 hops to a known mailbox
------  -----  -----  -------  --------------------------------  -------------------------
    30     10      2        2                             80.4%                      78.7%
   300    100      2        2                             14.1%                      41.4%
   300    100      3        2                             38.8%                      88.7%
   300    100      4        2                             66.4%                      98.7%
  3000   1000      2        2                              1.6%                       6.1%
  3000   1000      3        2                              5.2%                      35.5%
  3000   1000      4        2                             11.8%                      77.7%
  3000   1000      4        4                             21.9%                      91.4%
 10002   3334      4        2                              3.7%                      42.7%
relays  degree D  (D-1)^6  mean reach in 6 hops  worst of 40 sources  with 2 guards or 2 mailboxes  2 guards x 2 mailboxes
------  --------  -------  --------------------  -------------------  ----------------------------  ----------------------
  1000         4      729                 76.6%                72.0%                         94.5%                   99.7%
  1000         6   15,625                100.0%               100.0%                        100.0%                  100.0%
  1000         8  117,649                100.0%               100.0%                        100.0%                  100.0%
 10000         4      729                 13.5%                12.3%                         25.2%                   44.1%
 10000         6   15,625                 90.2%                88.5%                         99.0%                  100.0%
 10000         8  117,649                100.0%               100.0%                        100.0%                  100.0%
```

```text
-- A.10 can a 3-hop reply route join a mailbox? the mailbox and the reader's first hop within 4 crossings
relays  degree D  reach in 4 hops
------  --------  ---------------
   300         6            95.6%
  1000         6            61.2%
  1000         8            95.8%
 10000         6             8.9%
 10000         8            27.4%
```

**Reading: why a walk, and why not sparse layers.** If the cap goes and layers stay, the only way
to fit eight links is a sparse stratified graph, and a sparse stratified graph does not reach. The
blob join, s3 → r1 for one published route, reaches 1.6 % at 3,000 relays and d = 2, and 11.8 % at
d = 4. An undirected walk does far better for the same links, because it can double back through
any neighbour and is not restricted to one colour order: at D = 6, 6 hops reach 100 % of 1,000
relays and 90 % of 10,000; two guards or two mailboxes make that 99 %. D = 8 reaches all of 10,000,
but leaves no slot for leaves. **D = 6 is the recommended split: six relay links, two for own
devices.**

The reply route has only 3 hops, so it reaches just 4 crossings from the mailbox (A.10). At D = 6
that joins 96 % of the time at 300 relays, 61 % at 1,000 and 9 % at 10,000. **So the mailbox uses reply routes while
the fleet is small and forward routes when it is large.** Forward routes need the mailbox to know
each member's own node, which a room's members already do. κ rises from 82 to 120 at n = 20.

### What must change if the conferred count caps growth

| Candidate limit | Verdict |
|---|---|
| Per-link budget | **Not the limit.** 0.37 crossings/s per home against 0.046 per person |
| Layer balance, the cap | **The limit on growth.** Active relays ≤ 3C at any fleet size |
| Layer balance, the bound | **The limit on topology.** Complete layers stop at width 4 |
| Relay uptime | **Only at the minimum deal.** 73.5 % of hours at three seats and six homes |
| Rendezvous rows | **The limit on rooms** at a few hundred people, if rooms used them |
| The seat trunk | **The limit while seats carry homes:** 528 people |

Either the steward signs one conferral per three relays forever (§A.5), or the bound moves from a
per-layer count to a per-route rule. §I recommends the second. Independently of that, the uniform
pick must become a walk over standing links, or nothing past width 4 forwards.

---

## B. Latency

**Formula.** Six crossings, each Exp(λ_class), plus five holds Exp(μ) clamped at 60 s; the last hop
holds nothing. Mean = Σ 1/λ_i + 5μ. At load u of ρ the wait scales 1/(1 − uρ) **[inf]**. This is
below ρ; near ρ the 600 s window adds 6–36 s (CC 5.4.3).

```text

```

```text
-- B.2 to a person: mailbox to reader's own home is 4 crossings; a phone asks its home over the self link
                       sender to reader   mean   p95
---------------------------------------  -----  ----
                homes, reader is a home  76.1s  1.8m
wifi phone to wifi phone, homes between  87.7s  2.2m
            seat-core join, wifi phones  77.2s  2.0m
       cellular phone to cellular phone   2.6m  4.8m
```

**Reading.**

- **To the mailbox:** 45 s mean, 72 s p95 at home class, and 24 s with a seat core. Of the 45 s, 35
  is the shaped wait and 10 the mixing holds; neither can go without giving up what the rung is for.
- **To the reader:** 76 s between two homes, 88 s between Wi-Fi phones behind homes, 2.6 minutes
  between cellular phones. The p95s are about 1.5× that.
- **Raising μ to 8 s** for a usable crowd (§F) adds 30 s.
- **A seat-class core** saves 21 s at the mailbox. It is not a large win, and it is the design that
  recentralises, so the recommendation does not depend on it.

```text
-- B.3 a phone as a relay (CC 5.4.6 item 1 lets it while on Wi-Fi and charging)
relay class  pkt/s at 8 links  added gap  availability  2-relay route survives 1 h  cap slot yield pkt/s
-----------  ----------------  ---------  ------------  --------------------------  --------------------
       home             0.688       5.8s          0.95                       98.0%                 0.654
 phone-wifi             0.344      11.6s          0.30                       90.2%                 0.103
a phone in a deal cap slot yields 0.16 of a home, and drags every link it touches to 1,400 B/s (lower of two offers)
```

**A phone relay does not make sense on a room route.** It yields 0.16 of a home per dealt slot, it
pulls every link it touches to 1,400 B/s, it adds about 12 s per crossing, and a reused route through
two of them loses 10 % per hour even under the device policy. CC 5.4.6 item 1 lets a phone relay on
Wi-Fi while charging, and that remains fine for link cover and for carrying its own traffic. The
sender should simply never pick a phone-class node as a hop, and a phone must never be a hop on a
reused route. Device class is on the occurrence row, so this is the sender's own rule and needs no
CC text **[inf]**.

---

## C. Fan-out

**There is no multicast in an onion.** Each reader gets its own packet, so mesh load is Ω(n) per
message under every option. What the options move is who pays and how many crossings each reader
costs.

| Option | Crossings per message | Sender sends | Who sees timing |
|---|---|---|---|
| O1a per-member, CC seat mailboxes | (n−1)(6 + 4 + 3/b) | n−1 | Seats see co-arrival across n−1 rendezvous keys |
| O1b per-member, each to their own home | 6(n−1) | n−1 | Each reader's home |
| O2 room mailbox, reply routes | 6 + 4(n−1) | 1 | Mailbox member |
| O2f room mailbox, forward routes | 6n | 1 | Mailbox member |
| O3 group rendezvous, members fetch | 6 + (n−1)(4 + 3/b) | 1 | The rendezvous holder |
| O4 member tree, k = 3 | 6 + 4(n−1) | 1 | Each inner member, for its subtree |

```text

```

**Reading.**

- **A phone must not do per-member delivery.** Nineteen packets from one Wi-Fi link take 7.4 minutes;
  on cellular, 29 minutes. At n = 100 it is 38 minutes. One packet to a mailbox takes 23 s.
- **The mailbox is the bottleneck, not the mesh.** A home mailbox at D = 6 sustains 73 messages/hour
  at n = 20, and 14 at n = 100. A server-class member lifts that to 183 and 35.
- **The tree (O4)** keeps the load per node at k = 3, so a room of 100 sustains 465 messages/hour
  at 6.3 minutes' latency.
- **The reader has a ceiling too.** One Wi-Fi link is 155 packets/hour across all rooms; cellular is
  39. A person behind their own home does not hit it.
- **O1a is the most expensive** and the most revealing: 2.5× the crossings of O2, and the seats can
  cluster rendezvous keys by co-arrival, which reconstructs room structure per period.

**Recommendation.** O2 up to about n = 20. Above that, O4, with the two mailbox members as the root.
A large room on this rung is a slow room, and the client says so.

---

## D. Sync without rounds

CC 6.1.5.3 makes pull anti-entropy the one carrier, and a round needs an interactive peer. Over
one-way packets it is four traversals, 180 s and 24 crossings per peer per plane, against a 30 s
round interval. It cannot run.

```text
-- D.1 what a Summary/Diff round would cost over packets, vs the digest
                                         exchange  crossings    traversals                   latency
-------------------------------------------------  ---------  ------------  ------------------------
Summary/Summary/Diff/Deliver over two route pairs         24  4 traversals       180 s at home class
                     digest push on a reply route          4   1 traversal       30 s, no reply owed
                 catch-up pull + answer of k pkts     6 + 4k  2 traversals  75 s plus k-1 frame gaps
```

### The design: `room-sync/v1` inside a body

**Everything below sits inside the onion body and under the room's 5.4.2 symbol seal,** so a hop or
mailbox non-member sees none of it.

| Message | Direction | Contents |
|---|---|---|
| `RowPush` | author → mailbox → readers | sync header + one row or one chunk |
| `Digest` | mailbox → readers, hourly and piggybacked | window id, version vector, window hash |
| `Pull` | reader → mailbox | room tag, the reader's version vector (or gap list), one fresh reply route |
| `PullAnswer` | mailbox → reader | `RowPush` bodies, plus "more pending" |
| `RouteHand` | member ↔ mailbox, hourly | the sender's route for the coming period |

**The 104 B header** (edge's own, **[assumption]**): the CC 5.4.2 `symbol_envelope` overhead of 74 B
(`record_id` 32, index 2, nonce 24, tag 16), then room tag 16, author tag 4, per-author seq 4, chunk
count 2, flags 4.

**Gap detection is immediate.** Per-author seq means the next row from an author shows any gap, with
no digest needed. The digest exists for the silent tail, the last message before a quiet period.

**The version vector** is 8 B per active author, so it fits one body up to 1,000 authors. The 16 B
window hash over sorted row ids catches anything seq does not, such as a withheld row in a replayed
vector. A hash mismatch with equal vectors triggers a window pull.

```text
-- D.2 digest size: version vector of (author_tag u32, high_seq u32) + 16 B window hash + 44 B header
active authors  digest B  share of a body  fits one body
--------------  --------  ---------------  -------------
             5       100             1.2%            yes
            20       220             2.7%            yes
           100       860            10.5%            yes
           500     4,060            49.7%            yes
          1000     8,060            98.6%            yes
```

```text
-- D.3 chunking: 8,174 B capacity less a 104 B header = 8,070 B per chunk
                             row   bytes  chunks  crossings to mailbox  1 home link  6 home links  1 wifi link  1 cell link
--------------------------------  ------  ------  --------------------  -----------  ------------  -----------  -----------
             reaction / chat row   5,000       1                     6        11.6s          1.9s        23.2s        93.0s
                     T2 mean row   8,500       2                    12        23.2s          3.9s        46.5s         3.1m
    key record + contact request  20,000       3                    18        34.9s          5.8s        69.7s         4.6m
MLS Welcome + wraps [assumption]  64,000       8                    48        93.0s         15.5s         3.1m        12.4m
      largest shaped row, 64 KiB  65,536       9                    54         1.7m         17.4s         3.5m        13.9m
```

**A 64 KiB row is 9 chunks,** 54 crossings to the mailbox. CC 5.4.3 reassembly applies unchanged: a
record whose symbol set is not whole is dropped whole, never partly decoded. From a phone it takes
3.5 minutes on Wi-Fi and 14 on cellular. The T2 mean row at 8.5 KB is 2 chunks, so the ordinary row
does not fit a packet; a chat row at about 5 KB **[inf]** does.

### Loss recovery

```text
-- D.4 loss: packet delivery p; a 9-chunk row whole; ARQ by digest vs parity
hop loss  packet arrives  9 of 9  pulled chunks per row  9 of 11 with parity  parity pkts always sent
--------  --------------  ------  ---------------------  -------------------  -----------------------
   0.001          99.40%   94.7%                   0.05              100.00%                        2
   0.005          97.04%   76.3%                   0.27               99.64%                        2
    0.02          88.58%   33.6%                   1.03               87.80%                        2
independent loss only. A reused reply route fails whole: losses inside one route-hour are correlated, parity over one route buys nothing there, and the hourly digest on the next route repairs it
```

**Parity versus ARQ.** With independent loss, parity looks good in the table: 2 packets on 9 lift a
whole row from 76 % to 99.6 % at 0.5 % hop loss. But it costs 22 % on every row, including the ones
that needed nothing, where ARQ pulls 0.27 chunks per row at that same loss. And loss here is not
independent: a dead reused route loses everything in its hour, and parity over one route buys
nothing against that. The CC's fountain plane also excludes anonymous-tier content (SR-2/3).

**Recommendation: ARQ by gap, no parity.**

1. The author keeps every row in its own store until the digest shows the mailbox holds it.
2. A reader that sees a gap sends a `Pull` for those seqs and chunk indices only.
3. The pull carries its own fresh reply route, so an answer never depends on the route that failed.
4. A row the mailbox never got shows up in the author's next digest; the author pushes it again on a
   fresh route.
5. Pull answers are bounded by a deadline, carrying "more pending", which is the #1175 sequence.

```text
-- D.5 what a digest cadence costs, per room member
cadence  crossings/day/member/room  packets/day read  share of a person's load
-------  -------------------------  ----------------  ------------------------
 10 min                        576               144                     14.4%
    1 h                         96                24                      2.4%
    6 h                         16                 4                      0.4%
```

**Cadence.** Hourly costs 2.4 % of a person's load and matches the route period. The piggybacked
vector on every row does the rest of the work. Ten-minute digests cost 14 %.

---

## E. Mailbox: serve seat or member

**CC 5.4.6 item 6 says the rendezvous node MUST be a serve seat,** because "an hour-long route
through a node that sleeps is lost". Persist's position on #1175 is the opposite for rooms: no
non-member custody (I48), a member's claimed always-on node. The model finds that they answer two
different questions, and both hold.

```text
-- E.1 retention against sleep (rows arrive at 1/h per room per sleeper, three rooms; seat keeps period + grace)
sleep h  packets waiting  lost at a seat (mean hold 1.5 h)  lost at a member node
-------  ---------------  --------------------------------  ---------------------
   0.25              0.8                                0%                     0%
      1              3.0                                0%                     0%
      2              6.0                               25%                     0%
      8             24.0                               81%                     0%
     24             72.0                               94%                     0%
seat bound: 64 packets per key = 0.52 MB of bodies; a room burst of 64 messages while a phone sleeps refuses rendezvous_mailbox_full
```

```text
-- E.2 availability of the receive point and survival of an hour-long route
  receive point  replicas  at least one up  1 h route via 2 home relays survives
---------------  --------  ---------------  ------------------------------------
       one seat         1          99.900%                                97.91%
one member home         1          95.000%                                97.03%
one member home         2          99.750%                                98.00%
one member home         3          99.987%                                98.01%
a sleeping phone at the end of a route loses it outright; a phone is never a mailbox and never a reused-route hop
```

```text
-- E.3 seat load if every person's mailbox is a layer-3 seat
persons  seats  layer-3 seats  keys/seat  pkts/s in  x 8 home links  worst mailbox GB/seat
-------  -----  -------------  ---------  ---------  --------------  ---------------------
   1000      9              3        333        2.9             4.3                    0.2
  10000      9              3      3,333       29.3            42.6                    1.7
  10000     30             10      1,000        8.8            12.8                    0.5
```

| | Serve seat (item 6) | Member-owned node (#1175) |
|---|---|---|
| **Who learns what** | Rendezvous key, packet counts, sizes, times (item 8). For one room per person: co-arrival across keys | A member already sees all of it: membership, content, who posted when |
| **What an outsider gains** | Compel one seat, get counts for every key it holds | Compel one member, who could leak anyway (1.13.3.3) |
| **Retention** | Period + grace: 2 h at most. **A phone asleep 8 h loses 81 % at a seat** | Durable, the room's own |
| **Bound** | 64 packets per key | The owner's disk |
| **Availability** | 99.9 % | 95 % alone, 99.75 % with two, 99.99 % with three |
| **Churn** | None | Route via two homes survives an hour 97–98 % either way; the mailbox is the smaller term |
| **Load** | Three seats take all: 2.9 packets/s each at 1,000 people, 29 at 10,000, past three seat links | Each room pays for itself |
| **Recentralises** | Yes. Every room's traffic visits a third of the seats | No |
| **Sleeping-member rule** | "Seats do not churn" is satisfied | The rule's real concern is a *sleeping* node. A home is not one, and a phone is never a mailbox |

**Recommendation.**

- **Two member-owned always-on nodes per room,** chosen by the room, each holding the full row set.
  With two, the receive point is at 99.75 %, near a seat, and it holds rows for as long as the room
  does. The same `consent:replication` `cohorts` allow-list as #1175 places them.
- **A room with no always-on member** gets the seat as last resort: hour-scale ciphertext only,
  which CC 5.4.6 already concedes for a sleeping peer's mailbox, and the client says delivery needs
  both ends awake within two hours.
- **A route through a sleeping node is lost:** that sentence stays true. It rules out phones, and
  the sender's phone-class rule (§B) enforces that.

**Item 6 needs amending, with a scope.** "MUST be a serve seat" stays for federation-scope targeted
delivery, where the receiver has no cohort to hold anything. For a room, the receive point is a
member's claimed always-on node.

---

## F. What a global observer still learns

### The trilemma

Das et al.: strong anonymity is impossible when 2ℓβ < 1 against a global passive adversary; with c
of the parties compromised, the bound takes ℓ − c for c < ℓ. **[inf]** I read βℓ for this design as
rD, r the per-user rate of packets indistinguishable end to end, D the delay they mix over. I could
read the poster's statement of the bound but not the paper's own normalisation of β and ℓ. The
reading is the natural one (half the users must emit within the delay), but it is mine.

```text
-- F.1 trilemma: 2 beta l >= 1 read as 2 r D >= 1 [inf normalisation]; r = per-user end-to-end packet rate, D = the delay a message is mixed over
    D  needed end-to-end send interval  packets/day/person  cover crossings/day (3 hop)  vs person's real load  share of a person's slice of a home
-----  -------------------------------  ------------------  ---------------------------  ---------------------  -----------------------------------
 15 s                            30.0s               2,880                        8,640                   216%                                 109%
 45 s                            90.0s                 960                        2,880                    72%                                  36%
 90 s                             3.0m                 480                        1,440                    36%                                  18%
180 s                             6.0m                 240                          720                    18%                                   9%
link cover answers the GPA alone: an always-on shaped home emits a frame every 5.8 s, so 2 beta l >> 1 at the wire. It ends at the next hop, so against a compromised relay only end-to-end packets count; with c compromised hops on a route of l, l is replaced by l - c (Das et al.)
```

**Two adversaries, two answers.**

- **The pure GPA.** Link cover settles it. A shaped home emits a frame every 5.8 s whether or not it
  is sending, so 2βℓ ≫ 1 at the wire and the set is every online shaped node.
- **A compromised relay.** Link cover ends at the next hop, and a relay sees the real share on its
  own links (CC 5.4.3). Only end-to-end packets count. With no onion-layer cover, 2rD = 0.042, 24
  times short. To meet the bound at D = 45 s each person sends one packet per 90 s, 2,880 cover
  crossings a day, 72 % on top of their real load and 36 % of their slice of a home. MixMatch's
  warning applies to loops as cover: use drop packets that terminate at a random relay, not loops
  alone.

```text
-- F.2 anonymity set of a sender: everyone who could have sent inside D
 users                         case  set vs pure GPA  set vs compromised relay, D = 45 s  2 r D
------  ---------------------------  ---------------  ----------------------------------  -----
   100          homes, no e2e cover              100                                 2.1  0.042
   100          homes, cover 1/90 s              100                                39.3  1.000
   100  phones online 30%, no cover               30                                 0.6  0.042
  1000          homes, no e2e cover            1,000                                20.6  0.042
  1000          homes, cover 1/90 s            1,000                               393.5  1.000
  1000  phones online 30%, no cover              300                                 6.2  0.042
 10000          homes, no e2e cover           10,000                               206.2  0.042
 10000          homes, cover 1/90 s           10,000                             3,934.7  1.000
 10000  phones online 30%, no cover            3,000                                61.9  0.042
100000          homes, no e2e cover          100,000                             2,061.8  0.042
100000          homes, cover 1/90 s          100,000                            39,346.9  1.000
100000  phones online 30%, no cover           30,000                               618.5  0.042
```

```text
-- F.3 relay view: nodes that can be the source seen from hop r on a D-regular walk, and the crowd in a relay
D  r=1  r=2  r=3     r=5
-  ---  ---  ---  ------
4    3    9   27     243
6    5   25  125   3,125
8    7   49  343  16,807
 relay  max pkt/s  crowd at full load, mu 2 s  mu for crowd 3 at full load  crowd at 10% load, mu 2 s
------  ---------  --------------------------  ---------------------------  -------------------------
  home       0.52                        1.03                        5.8 s                       0.10
server       1.29                        2.58                        2.3 s                       0.26
  seat       3.04                        6.08                        1.0 s                       0.61
```

**Reading.** At D = 45 s with no cover, a compromised relay's set is about 2 % of users: 21 at 1,000
users. With cover at the bound it is 39 %. The first table in F.3 is the Tarzan fan-out, (D − 1)^r,
and it is a real limit too: a hostile hop 2 on D = 6 sees 5 possible predecessors of its predecessor.
The crowd inside a relay is below 1 at any plausible load with μ = 2 s, so **a relay does not mix at
this load; it only forwards.** At 10 % load a home would need μ near the 60 s clamp for a crowd of 3.
The tier's protection against a relay comes from the route, not from mixing, until the traffic is
there. Item 8 already says this, and the client must keep saying it.

```text
-- F.4 intersection: phones. Candidates left after m room events an insider times, online share o
   o       m=5      m=20     m=100
----  --------  --------  --------
0.95  7.74e-01  3.58e-01  5.92e-03
 0.5  3.12e-02  9.54e-07  7.89e-31
 0.3  2.43e-03  3.49e-11  5.15e-53
```

**Intersection is the phone's problem.** A room insider who times messages and a GPA who sees who is
online can intersect. Among nodes online half the time, a millionth of the candidates survive 20
events; among homes online 95 % of the time, a third do. This is the other reason the person's
onion endpoint should be their own always-on home: the phone talks to it over a self link, the home
carries the route, and the home's uptime hides the phone's.

### The CC's two residuals

CC 5.4.3 item 5: shaping hides timing and volume "not which links exist". CC 5.4.6: an observer
correlating link traffic across a clique "can infer that a group exists".

| Residual | Does a room over onion remove it? |
|---|---|
| **Which links exist** | **No, never.** The onion does not touch it. It makes links *uninformative* only if the links do not follow relationships. Link setup, endpoints, class and online pattern all stay visible |
| **That your groups exist** | **Against outsiders, yes, but only under the node rule.** Members still know. A mailbox member knows the room's size and activity |

```text
-- F.5 member links: what the link graph alone says
  n  clique edges  member links a node could hold  shown to a GPA if members link
---  ------------  ------------------------------  ------------------------------
  5            10                               4                    whole clique
 20           190                               8           42% of edges per node
100          4950                               8            8% of edges per node
```

**Must a room-over-onion node run shaped-only, with no direct links to members? Yes, and shaped-only
alone is not enough.** A shaped link to a co-member is still a link to a co-member: five members
holding links show the whole clique, and the onion above it hides nothing. CC 5.4.6 today requires
the opposite of what this needs ("MUST prefer the derived address whenever a direct link exists").
So the rule:

1. **No link whose existence depends on a room.** No derived-address link, no direct link, no scoped
   round, no bulk link, no call to any co-member, shaped or not. Item 10 already rules this for a
   contact through the tier; this extends it to the room.
2. **Shaped links are chosen by a rule that ignores relationships:** hash-assigned relay links, plus
   a guard outside the room.
3. **No unshaped link at all on that node while in the mode,** except to own devices. CC 5.4.3 item 5:
   any unshaped link tells the node apart.
4. **Rows that name a relationship travel in bodies.** Welcomes, key wraps and epoch rows are on the
   stranger plane today ("the sealed asks and answers"). A key wrap from A to B on an open link is a
   contact edge. In this mode they ride the onion, chunked (§D.3).
5. **The mode is per node, not per room.** A member not on the rung leaks its own links, not an
   onion member's. A mailbox member on an ordinary rung is visible with its ordinary peers, and the
   onion members are absent from that clique. **This is the useful property: privacy does not need
   the whole room to agree** **[inf]**.

**What a GPA still learns about a compliant node:** that it exists, its class, its online pattern,
its link set and when each was set up, that it shapes (at fleet defaults a shaping phone stands out),
that its real rate is below ρλ, and a contact guard edge. **What a relay or peer learns** beyond that:
the real share on its link and that a packet passed. **Not claimed:** an active adversary that drops
or delays frames (CC 5.4.3 item 5; Levine, MixMatch).

---

## G. Feature cost at this rung

```text

```

```text
-- G.2 a person's own cost
                         node  GB/mo each way  real pkt/h ceiling
-----------------------------  --------------  ------------------
phone cellular, 1 shaped link             0.9                  39
           phone wifi, 1 link             3.6                 155
          phone wifi, 8 links            29.0               1,239
                home, 8 links            58.1               2,478
```

| Feature | At this rung | Reason |
|---|---|---|
| Chat | Works, mail-like: about 1.5 minutes typical, 2.6 on cellular, p95 5 minutes | §B |
| Reactions | Work, and cost the same as a message: 1 packet, 82 crossings | A hybrid-signed row is about 5 KB whatever it says |
| Per-reader receipts | **Removed.** 1,558 crossings per message at n = 20 | O(n²). They also state who was online when, the input to §F's intersection |
| Read position | An hourly mark to the mailbox, 114 crossings per room hour at n = 20, not relayed to readers | Enough to stop re-delivery |
| Typing, presence | **Removed** | Each is a timing signal by design, at a latency that makes it useless |
| Images | To 64 KiB: 9 packets, 3.5 minutes from Wi-Fi. Above it refused | 5.4.3: a peer in anonymous mode is row-plane only |
| Files, calls, streams | **Refused** | `onion_anonymous_no_media`; bulk needs an unshaped link |
| Room join | About 8 packets for a 64 KB Welcome with wraps **[assumption]**, 3 minutes from Wi-Fi | §D.3 |
| First contact | Through a rendezvous route, 3 packets for a 20 KB request, reaching the person at their next pull; a stranger's route has to come from somewhere | Item 10. The rendezvous row stays the door for strangers, which is why it stays federation-reach at low volume: it is for first contact, never for a room |
| Who else is here | Members still see members | Attribution stays inside: a sender is never unattributed (1.13.3.4) |
| Public posts | Pseudonym row as item 9. Rooms do not use pseudonyms | Room rows are signed by the member, sealed, and carried in the body |
| Cost | Phone: 0.9 GB/month on one cellular link, 3.6 on Wi-Fi. Home: 58 GB/month each way at eight links, already paid at rung 2 | §G.2 |

**A person's slowest step is their own first link.** On cellular it is 93 s at the mean real rate,
and sleep ends the link altogether. A phone wakes on a schedule that does not depend on traffic, or
the wake is itself the signal (CC 5.4.3 item 5), and a push through FCM or APNs tells a third party
when the room spoke. The honest mobile answer is scheduled wake, so "catching up" is as old as the
last wake.

---

## H. Build order

Dependencies only. Nothing here is estimated.

**Decisions first (Eric):**

- **R1.** Does the bound move from a per-layer cap to a per-route guard rule (§I)?
- **R2.** Does the route become a walk over hash-assigned standing links, leaving "one from each of
  three layers"? If not, nothing past width 4 forwards.
- **R3.** Does item 2's scope open to rooms, and does a room's receive point become member-owned?
- **R4.** Is onion-layer drop cover in scope, given its 72 % cost? Without it the client's relay claim
  stays weak.

### CC

| # | Change | Section | Today it says |
|---|---|---|---|
| C1 | Open first scope to `community` / `affiliations` / `family`; restate 1.13.3.1 and 1.13.3.3 | 5.4.6 item 2 | "Other scopes are not routed through it" |
| C2 | Let a scoped body cross a tier relay inside an onion body | 5.4.6 "Who carries what" | The carrier list names a tier relay, and the next sentence narrows a scoped body to "a consented contact or, as last resort, a serve seat" |
| C3 | An anonymous-mode node is exempt from preferring the derived address; add the node rule | 5.4.6 forwarder rule | "MUST prefer the derived address whenever a direct link exists"; "MUST NOT route a scoped body through a forwarder when a direct path is available" |
| C4 | Item 6 and 3.1.4: a room's receive point is a member's claimed always-on node; route material for a room stays in the room | 5.4.6 item 6, 3.1.4 | "MUST be a serve seat"; reach "everyone" |
| C5 | One-way `room-sync/v1` is a sanctioned carrier for this mode | 6.1.5.3 | "by pull anti-entropy ... never by push"; SR-2 exempts anonymous retention, not room carriage |
| C6 | Replace the layer cap and deal with hash-assigned links and the guard rule; restate `CLM-onion-layer-model` and `OL.hostile_share`, `OL.size_anyN`, `OL.floor_three_seats`, `OL.never_worse` with new TLA+ and Lean | 5.4.6 item 4; `formal/onion_layers` | §I |
| C7 | Add the phone-class hop exclusion if it should be normative | 5.4.6 item 1 | Phones relay on Wi-Fi charging |
| C8 | Pin the packet (`docs/onion_packet_wire.md`, 15,296 B) | 5.4.6 item 3 | Not pinned |
| C9 | Revise the 1.6/4/8 s copy to this frame size | 5.4.3 | §1 |

### Persist

| # | Change | Depends on |
|---|---|---|
| P1 | #1181 hop-key reader; #1149 rendezvous and pseudonym gate | C8 |
| P2 | Room-row door for a row arriving with no attributed link peer: verify the sealed row against the member's key and the room epoch | C1, C2 |
| P3 | #1175 deficit read with a deadline, servable to a peer | none |
| P4 | Per-author seq and the digest read: version vector and window hash for a room | P3, C5 |
| P5 | Mailbox placement by the `cohorts` allow-list; two holders | P3, C4 |
| P6 | The fold's relay read: hash-assigned neighbours; age from the witnessed head; one per owner | C6 |

### Edge

| # | Change | Depends on |
|---|---|---|
| E1 | Walk route selection over the link graph; hash-assigned relay links at D = 6; retire the full `layer_peers()` | C6, P6 |
| E2 | Over-the-wire RNS loopback for the packet (owed already) | P1 |
| E3 | Sticky guards from contacts, seat as last resort | C6, E1 |
| E4 | Own probes, feeding a relay filter | E2 |
| E5 | `room-sync/v1`: chunker, gap detection, `Pull`, `Digest`, `RouteHand` | P2, P4, C5 |
| E6 | Member mailbox: push, tree fan-out above n = 20 | E5, P5 |
| E7 | The node rule enforced by name: refuse member links, derived dials, unshaped links in the mode | C3 |
| E8 | Status and counts for the client: guard state, route reach, small-set line | E1 |
| E9 | Witnesses: DST for route failure and sleep; a mesh leg with no member link in the census, and a leak test proving it | E1–E7 |
| E10 | Drop cover, if R4 says yes | E2, E4 |

**Order.** R1–R3 first, because each rewrites what the rest builds. Then C1–C6 and C8. Three
parallel strands follow: P1 → E2 → E4; P6 → E1 → E3; P3 → P4 and P5 with P2 → E5 → E6. E7 is
independent once C3 lands. E9 closes it. Client copy changes only after E9: until then
`FSD/PRIVACY_MODES.md` §4.1 stands and no client copy mentions rooms over the onion.

**The first cut does not need R1 or R2.** Complete layers work today up to width 4, and a deal of
seats alone is complete at any seat count because seat links sit outside the eight. So nine seats
with no others, or three seats and six homes, carry rooms on the existing pick, with C1–C5, E2 and
E5–E7. That is 81 people at the minimum deal and 528 at the nine-seat trunk. Ship that, then take
the walk and the guard rule, which is where the mesh's growth arrives.

---

## I. What the conferred/unconferred split actually buys

**Eric's question:** "Why do we care about conferred or unconferred? The canonicals are just the
TOFU bootstrap and directory service".

**The short answer: it buys one proved sentence and costs the mesh's growth, and the sentence is
weaker than it reads.** The sentence is `OL.hostile_share`: an adversary holding no conferred relay
holds at most c/(1+c) = 2/3 of any layer, whatever hostile subset of the others it controls. The cap
makes that a theorem at any N (`OL.hostile_bound_anyN`). Everything else follows from
`|layer| ≤ (1+c)·s` (`OL.size_anyN`), and that same line is the capacity limit.

### I.1 What the bound costs at nine seats

```text
-- I.1 capacity with the cap and without it, nine seats, homes all owner-bound (D 4 capped, 6 uncapped)
homes  active capped  active free  Theta capped  Theta free  ratio  persons capped  persons free  a home's share of hours
-----  -------------  -----------  ------------  ----------  -----  --------------  ------------  -----------------------
   18             27           27          66.0        68.2   1.0x           1,426         1,474                  100.00%
  100             27          109          66.0        98.4   1.5x           1,426         2,125                   18.00%
 1000             27         1009          66.0       429.4   6.5x           1,426         9,275                    1.80%
10000             27        10009          66.0     3,739.7  56.6x           1,426        80,777                    0.18%
without seat links the cap holds 4.41 crossings/s of home relays; the cap is 7% homes, the rest is the seats' own class
a uniform route touches a conferred relay with P = 0.704 (3 hops), 0.912 (6 hops), so the cap makes the seats a hop on most routes, a role beyond bootstrap and directory
```

**Reading.** The cap costs a factor of 1.5 at 100 homes, 6.5 at 1,000, 57 at 10,000. Of what stays,
93 % is the seats' own link class, so the 18 dealt homes are nearly irrelevant to capacity. And a
uniform route visits a conferred relay with probability 0.70 on three hops, 0.91 on six. **That is
the point of Eric's question: the cap gives the canonicals a job beyond bootstrap and directory. They
become a hop on most routes.** Every route through the tier then touches the governance of a few
seats. A compelled steward or a hostile seat set falls outside the proof, which assumes the conferred
are honest.

### I.2 What a Sybil can do with no cap

**What one costs. It is less than "a claimed identity" suggests.** The relay test (item 4) is
live row, announced, valid hop key, no marker, and owner-bound under a bundle root. `Rooted` is
defined from "the evaluating node's self-root ... through its own `trust:accepts:v1` edge", and
persist's `trusted_roots_of` reads the rows the key itself authored. Claiming is first-run: T1 writes
the owner's self-root, the owner signs the binding, the node signs its own acceptance edge. **No third
party signs anything about a stranger's relay.** The cost of one Sybil is two key pairs and four rows
**[inf from the CC and `trust_root.rs`; the fold reader for this predicate is not yet written]**. CC
1.13.3.3 says the same of its own: "minting a key costs nothing", and "the admission cost" is the
only thing bounding rooted owners.

The real cost is the bandwidth to look alive:

```text
-- I.4 what a Sybil pays, per relay [assumption: $0.01/GB egress; $5/mo per public address]
                                 behaviour  egress/mo each way  bandwidth $                                                   result
------------------------------------------  ------------------  -----------  -------------------------------------------------------
listed only (row + hop key, no forwarding)                0 GB           $0  dropped by the sender's liveness filter within a window
                        one link answering                7 GB        $0.07                    enough to pass liveness on one sender
            full home-class relay, 8 links               58 GB        $0.58                    indistinguishable from an honest home
S relays  added to every node's fold [assumption 20 KB row]  $/mo full relays
--------  -------------------------------------------------  ----------------
    1000                                              20 MB               581
   10000                                             200 MB             5,806
  100000                                           2,000 MB            58,061
```

```text
-- I.2 hostile share q of a route hop, Sybils S against H honest relays, seats honest
    H      S  f = S/(S+H) = q no cap  q cap  cap P(ends)  cap P(all 3)  no cap P(ends)  no cap P(all 3)
-----  -----  ----------------------  -----  -----------  ------------  --------------  ---------------
  100     18                   0.153  0.102        0.010        0.0011           0.023           0.0035
  100    100                   0.500  0.333        0.111        0.0370           0.250           0.1250
  100   1000                   0.909  0.606        0.367        0.2226           0.826           0.7513
  100  10000                   0.990  0.660        0.436        0.2876           0.980           0.9706
 1000     18                   0.018  0.012        0.000        0.0000           0.000           0.0000
 1000    100                   0.091  0.061        0.004        0.0002           0.008           0.0008
 1000   1000                   0.500  0.333        0.111        0.0370           0.250           0.1250
 1000  10000                   0.909  0.606        0.367        0.2226           0.826           0.7513
10000     18                   0.002  0.001        0.000        0.0000           0.000           0.0000
10000    100                   0.010  0.007        0.000        0.0000           0.000           0.0000
10000   1000                   0.091  0.061        0.004        0.0002           0.008           0.0008
10000  10000                   0.500  0.333        0.111        0.0370           0.250           0.1250
```

**With no cap, a Sybil with budget S can:**

- **Take the route.** Hostile share per hop q = S/(S+H). All three hops: q³. Both ends, the timing
  correlation case: q². At S = H, 12.5 % and 25 %. At S = 10H, 75 % and 83 %.
- **Drop.** See I.7: at q = 0.5 only 3 % of packets survive five hops unfiltered.
- **Attract.** A refusal refers up to three nodes that "report a free shaped slot", and a lying relay
  attracts traffic (Bauer et al.), so a Sybil can capture a newcomer's first links.
- **Bloat the fold.** Every relay row replicates to everyone: 2 GB at S = 100,000.
- **Lie to the small-set line.** The client's "ten per layer" counts Sybils as crowd.

**With the cap, a Sybil can still do most of this.** The bound is an upper limit that is cheap to
reach:

```text
-- I.3 grinding: deal_hash(key_id, period) is public, so keys can be chosen for a period
honest others  dealt others/period  key tries per slot  relays to fill a period  q reached  registered identities for a year of periods
-------------  -------------------  ------------------  -----------------------  ---------  -------------------------------------------
          100                   18                   6                       18        2/3                                      157,680
         1000                   18                  56                       18        2/3                                      157,680
        10000                   18                 556                       18        2/3                                      157,680
```

**Reading: Douceur's warning applies directly.** `deal_hash` is `SHA-256(tag ‖ key_id ‖ period)`, and
key, tag and period are all public, so identities can be ground for a chosen future period. At 10,000
honest homes, 18 relays at 556 tries each fill every dealt "other" slot for that hour, reaching the
full 2/3. As Douceur shows and the prior art notes, c/(1+c) is only meaningful if the signed roster
is the admission authority. For the conferred third it is. For the other two thirds it is not: they
are admitted by a self-signed row. So the bound really says "at least a third of each layer is the
steward's". It says nothing about the two thirds, and the worst case is 44 % of routes with both ends
hostile and 30 % hostile end to end. That is a weak guarantee to spend 57× of capacity on.

### I.3 The alternatives

Budget: S = 1,000 identities and $600/month **[assumption]** against H = 1,000 honest relays.

```text
-- I.5 alternatives at S = 1,000 Sybil identities and $600/mo, H = 1,000 honest relays, per-hop q and route risk
                                               rule   q expected      q worst  P(ends)  P(all 3)                recentralises?
---------------------------------------------------  -----------  -----------  -------  --------  ----------------------------
               status quo: cap c=2, seats+conferred        0.333        0.667    0.444     0.296           yes: steward, seats
                                             no cap        0.500        0.500    0.250     0.125                            no
                                one relay per owner        0.500        0.500    0.250     0.125           no; owners are free
                          + hardware-attested owner        0.048        0.048    0.002     0.000           to platform vendors
           identity age >= 90 d, fresh swarm at 7 d        0.072        0.500    0.250     0.125          mild: witnessed time
                      measured delivery, own probes        0.500        0.500    0.250     0.125                            no
           measured delivery, measuring authorities        0.500        0.500    0.250     0.125                yes: measurers
                hash-assigned mimics alone (Tarzan)        0.500        0.500    0.250     0.125                            no
                          contact graph, distance 2        0.400            -    0.160     0.064       no; leaks contact graph
                       own contacts only (g = 0.05)        0.050        0.050   0.0025   0.00013           no; small route set
RECOMMENDED guard from contacts (g = 0.05) + fold q  0.050/0.500  0.050/0.500    0.025    0.0125  no; seat is last resort only
money buys 1,033 full relays of real capacity, so a bought-capacity rule still admits S = 1,000; honest capacity is 22.4 MB/s
```

| Rule | Adversary pays | Share at budget | Recentralises? | Verdict |
|---|---|---|---|---|
| Steward conferral (status quo) | Nothing for the others; a stolen conferral for the rest | 1/3 expected, 2/3 ground | **Yes:** steward signs growth; seats on 70–91 % of routes | Keeps a proof, stops the mesh |
| No cap | Bandwidth | 1/2 | No | No bound |
| One relay per owner | Nothing: owners are free | 1/2 | No | **Useless alone.** Worth keeping for honest diversity, and it gains force if owners ever cost |
| Hardware-attested owner (`attestation:hardware_rooted`) | A device each | 0.05 at 50 devices | **To platform vendors,** who become Douceur's authority; shuts out home servers without a TPM | Optional weight, never a gate |
| Identity age ≥ 90 d | Waiting: S_eff = S·a/A for a swarm of age a | 0.07 fresh, 1/2 once aged | Mildly: needs witnessed time, since `asserted_at` is self-stated | **A price in time, not a bound.** Also kills grinding: a key 90 days old cannot be ground against a fresh value |
| Measured delivery, own probes | Real capacity: 58 GB/month per relay | 1/2 at $600 | No | **A price in bytes,** and it removes droppers. Honest capacity is cheap to match (Users Get Routed) |
| Measured delivery, by authorities | The same | 1/2 | **Yes:** Tor's bandwidth authorities | Rejected |
| Reputation from peers | Collusion | Unbounded | No | **Rejected:** MorphMix (Tabriz & Borisov): local knowledge is not sufficient |
| Hash-assigned mimics (Tarzan) | Bandwidth | 1/2 | No | **Topology, not a Sybil bound.** Tarzan's links are hash-assigned from the roster, not contacts, and its own Sybil limit is an IP-domain rule. Needed for the walk |
| Contact graph, distance 2 | Attack edges: one person who consented, and their fan-out | 0.40 at g = 0.05 | No | **Leaks the contact graph** to compute (Pisces concedes this), and CC 5.4.6 keeps a roster unenumerable outside its cohort |
| Own contacts only, every hop | Attack edges | g | No | Strong bound, but the routes fingerprint the sender and few contacts offer relay |
| **Guard from contacts + the fold filtered** | Attack edges for the guard; bandwidth and time for the rest | g, then q | **No.** A seat is only the guard of last resort | **Recommended** |

**"Own contacts" and "Tarzan's mimics" are two mechanisms, not one.** The question groups them. Contacts
give the Sybil bound, because consent is per identity and granted by a person (`FSD/CIRIS_MESH.md`
§5.4: "minting identities buys nothing"). Mimics give the topology, because a hash-assigned link
cannot be chosen. The recommendation uses each for what it does.

### I.4 The recommendation

**Move the bound from the layer to the route.** Remove the cap, keep the floor, and bind every
route to one trust-anchored hop that a Sybil cannot mint into.

1. **Hop 1 is a sticky guard from the sender's own consented contacts** that offer relay, outside any
   room it carries, two of them for reach. No relay contact: a serve seat, by the same order CC 5.4.6
   already gives a scoped body ("a consented contact or, as last resort, a serve seat"). **That is the
   canonical's role as Eric put it: the bootstrap, and nothing more.**
2. **The other hops are drawn from the fold over standing links,** filtered by the sender's own
   probes (real capacity), with owner age ≥ A from the witnessed head (time, and no grinding) and at
   most one relay per owner (diversity).
3. **Result.** P(both ends hostile) = g·q and P(all hostile) = g·q², with g the share of that person's
   relay contacts that are hostile.

```text
-- I.6 the recommended rule across Sybil budgets and hostile-contact shares: P(ends) = g x q, P(all 3) = g x q^2
   g       S      q  P(ends)  P(all 3)
----  ------  -----  -------  --------
 0.0    1000  0.500    0.000     0.000
 0.0   10000  0.909    0.000     0.000
 0.0  100000  0.990    0.000     0.000
0.05    1000  0.500    0.025     0.013
0.05   10000  0.909    0.045     0.041
0.05  100000  0.990    0.050     0.049
 0.2    1000  0.500    0.100     0.050
 0.2   10000  0.909    0.182     0.165
 0.2  100000  0.990    0.198     0.196
 1.0    1000  0.500    0.500     0.250
 1.0   10000  0.909    0.909     0.826
 1.0  100000  0.990    0.990     0.980
```

```text
-- I.7 Sybils that drop: a packet over five fold hops survives (1-q)^5; own probes remove droppers at rate pi
q dropping  no filter  probes catch 90%
----------  ---------  ----------------
       0.1      59.0%             95.1%
       0.5       3.1%             77.4%
       0.9       0.0%             62.4%
g is per sender and does not move with S: minted identities are no one's contacts. g = 1 is the person whose only relay contact is hostile; the seat as last-resort guard gives g = hostile share of seats
```

**Why this beats the cap.** The worst case of the cap, reached with 18 ground relays, is P(ends) =
0.44. Here it is bounded by g at *any* S: 0.05 at g = 0.05 even at S = 100,000. At g = 0 it is zero.
The cap does better only at low S with no grinding and a person with a hostile contact: at S = 100,
H = 1,000 the cap's 0.004 matches the guard's 0.0045 at g = 0.05, so the two are level there.

**What it costs, plainly.**

- **No global theorem.** `OL.hostile_share` is a statement about every layer; this is a statement per
  sender. CC 5.4.6 item 4's claim changes kind, and the formal model must be redone. g = 1 is real:
  the person whose only relay contact is hostile.
- **Honest guard, hostile fold, still a leak.** If every other hop is hostile the adversary sees "a
  sender behind G talks to mailbox M". The set is then G's crowd, not the fleet: (D−1)^r, 5 to 125 at
  D = 6. P(ends) counts exact deanonymisation only. This is why the fold filters stay.
- **A contact edge shows.** The guard is one visible link to one contact. That is the price of the
  bound, and it is why the guard must be outside the room. A person who cannot accept it uses a seat
  and takes the seat's g.
- **A guard learns the real share** on its link (CC 5.4.3), and a guard is a person you know.
- **Newcomers.** Everyone starts with a seat as guard, and the seats see them. That is TOFU, it
  shrinks as contacts arrive, and it is honest to say so at first run.
- **The steward's setting.** `c` and `onion.cap_factor` go. A transition keeps the deal for federation
  publication until C6 lands. The tier ships dormant, so there is no flag day **[inf]**.

**Prior art.** Tarzan for the walk and the verifiable links. Pisces and Drac for social-graph routes;
Pisces reports twice Drac's entropy over 100 rounds, and concedes it does not preserve contact
privacy, which is why this design uses a contact for one hop and never publishes the graph. SybilLimit
for the attack-edge bound (recalled, not re-read for this document). Guard Sets and Dingledine on
sticky guards. Douceur for why a roster bound needs a roster.

---

## J. The design in one picture

```text
 phone --self link--> own home ==> guard --> relay --> relay --> relay --> relay --> mailbox member
 (no route)           (sender)    (contact,  (walk over standing shaped links,        (2 per room;
                                  outside     hash-assigned, D = 6; probed,            durable; pushes
                                  the room;   aged, one per owner)                     to readers)
                                  seat if none)

 readers: mailbox --> 3 relays --> reader's home   (reply route, small fleet)
          mailbox --> 5 relays --> reader's home   (forward route, large fleet)
 repair:  reader  --> Pull with its own reply route --> mailbox --> PullAnswer
 links:   none to any co-member, of any kind; the guard is not a co-member
```

---

## K. Assumptions register

| # | Assumption | Value | Why, and what moves it |
|---|---|---|---|
| 1 | Row plane's share of real budget | u_row = 0.25 | Not measured. Scales Θ linearly |
| 2 | Availability | server 0.999, home 0.95, relaying phone 0.30 | Prior model's device policy; phone is the Wi-Fi-and-charging share |
| 3 | Churn per hour | seat 0.1 %, home 1 %, phone 5 %, always-on phone 40 % | `ONION_TIER_MODEL` §d |
| 4 | Load per person | 40 messages/day, rooms of 20, three rooms | Chosen. Scales "people" inversely; κ dominates |
| 5 | Route upkeep | 10 crossings per member, room and hour | §D design |
| 6 | Chat row size | 5,000 B | **[inf]** ML-DSA-65 3,309 B signature in base64 plus envelope. T2 mean is 8,500 B, over one body. A 2-packet row doubles load |
| 7 | One packet per frame | yes | **[inf]** frame body 16,248 B from `transport_tiers.py`; `CONP` adds 4 B |
| 8 | Body header | 104 B | CC 5.4.2 envelope 74 B plus 30 B of design |
| 9 | Fetch batch b | 4 | O1a, O3 only |
| 10 | Wait under load | 1/(λ(1 − uρ)) | **[inf]** Base case u = 0 agrees with `SHAPING_RHO_W` |
| 11 | Θ spreads evenly over relays | yes | **[inf]** Holds on a regular walk; the seat core and hot rooms are worse. Θ is an upper bound |
| 12 | Random regular graph for the walk | configuration model | Hash assignment approximates it **[inf]** |
| 13 | Seats and dealt conferred are honest | yes, in §I.2 | The proof's assumption. Stated as such |
| 14 | Sybil prices | $0.01/GB, $5 per address, 50 attested devices at $600 | Illustrative only. Conclusions turn on ratios |
| 15 | Hostile contact share | g = 0.05 | Chosen. Table I.6 sweeps it |
| 16 | Distance-2 share | 8 × g | Crude; the row is rejected on other grounds |
| 17 | 64 KB Welcome | size | Unmeasured |
| 18 | Mean hold at a seat | 1.5 h of the 1–2 h window | Period remainder + grace |
| 19 | Sender and reader phone keep a self link to own home | yes | The person's home carries the route |
| 20 | Link loss rates in D.4 | 0.1–2 % per hop | Sweep, not a measurement |

---

## L. Open questions

1. R1–R4 in §H.
2. **What value does a walk's hop position hide?** With fixed six-hop routes a relay cannot read its
   position from the packet, but a walk length that varies would strengthen that. The header has six
   slots; random-length walks use filler. Not modelled.
3. **Hash-assigned links against the referral and displacement rules of CC 5.4.3.** Relay links would
   be assigned; leaf attachment keeps referrals. Epoch length needs a choice. Tarzan used a day. The
   hour of item 7 would redial the whole mesh hourly, so the link epoch must be separate from the
   rendezvous period.
4. **Own probes at scale.** Every sender probing every relay is its own load. Sample it, and count it
   against the cover budget.
5. **Mailbox pair election** without emitting anything that names the room.
6. **Does an observer distinguish a node with no member links in a fleet where most nodes have them?**
   Mode visibility is one more bit. Rung 3 and 4 uptake sets its value.

---

## M. Sources

Das, Meiser, Mohammadi, Kate, S&P 2018, [poster statement of the bound](https://www.ieee-security.org/TC/SP2018/poster-abstracts/oakland2018-paper45-poster-abstract.pdf),
[project page](https://freedom.cs.purdue.edu/projects/trilemma.html);
[Comprehensive Anonymity Trilemma](https://petsymposium.org/popets/2020/popets-2020-0056.php);
Mittal, Wright, Borisov, [Pisces](https://arxiv.org/abs/1208.6326), NDSS 2013;
[Tarzan](https://www.cs.princeton.edu/~mfreed/docs/tarzan-ccs02.pdf), CCS 2002;
[Loopix](https://arxiv.org/abs/1703.00536); [MixMatch](https://www.petsymposium.org/popets/2024/popets-2024-0050.pdf), PoPETs 2024;
[The Sybil Attack](https://doi.org/10.1007/3-540-45748-8_24), Douceur, IPTPS 2002;
[Tabriz & Borisov](https://petsymposium.org/2006/preproc/preproc_21.pdf), PET 2006;
[Bauer et al.](https://sharif.edu/~kharrazi/courses/40817-941/reading/wpes25-bauer.pdf), WPES 2007;
the prior-art notes behind `FSD/TRANSPORT_TIERS_MODEL.md` for Herd, Guard Sets and Users Get Routed.
Yu et al., SybilLimit, S&P 2008, from memory.

---

## N. Change log

- 2026-11-05: first version. Sections A–H from the brief; §I from Eric's question on conferral.

## Rulings on CIRISConstitution#202 (Eric, CC 5.4.6, rc17, 2026-11-04)

Not v44. These supersede anything above that disagrees.

- **Route:** a walk over standing hash-assigned shaped links. Hop one is a sticky guard from the sender's own consented relay contacts. Hop two is outside any room served, with a seat as last resort. A long-lived mailbox pins its second hop (Tor's vanguard lesson). Other hops come from the fold, filtered by local probes (never a shared row), owner age and one relay per owner. No steward cap, no `c`, no `onion.cap_factor`. The floor of three answering relays per position stays. The bound is per sender.
- **Mailbox:** a seat for federation-scope targeted delivery; two member-owned always-on nodes for a room; a seat as last resort; never a phone.
- **Scope:** the tier carries private rooms, never public ones.
- **Device class:** anonymous mode on any device class, phones on Wi-Fi included, with end-to-end cover on by default. No home node is required. Residuals stated in item 8: no mixing at today's load, and the sleeping phone against an insider.
- **Carrier:** a tier relay is a carrier that has said yes; the forwarder rule does not reach it.

**Owed to the CC:** the relay-link epoch against referral and displacement, and the end-to-end cover rate to pin in item 8 (the text reads "about a third of a home's shaped share"). L1–L6 stay open here.
