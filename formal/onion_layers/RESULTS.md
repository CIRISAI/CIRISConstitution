# Results — TLC 1.7.4 on OpenJDK 21, Lean 4.14.0, this host, 2026-10-22

| Config | Distinct states | States generated | Time | Result |
|---|---|---|---|---|
| `OnionLayers_2s3o.cfg` (2 seat-like, 3 others, c = 2) | 960 | 123,840 | 2 s | no error |
| `OnionLayers_2s4o.cfg` (2, 4, c = 2) | 11,520 | 8,490,240 | 2 min 22 s | no error |
| `OnionLayers_3s3o.cfg` (3, 3, c = 2) | 5,760 | 4,199,040 | 1 min 06 s | no error |
| `OnionLayers_3s3o_c1.cfg` (3, 3, c = 1) | 5,760 | 4,199,040 | 47 s | no error |

`lean OnionLayersCount.lean`: exit 0 (every theorem closes; no `sorry`; core only).

Invariants checked in every run: `Inv_DealDeterministic`, `Inv_HostileShareBound`, `Inv_NeverWorse`,
`Prop_FloorHonest`. States = every ranking of the relays (N!) × every hostile placement among the others
(2^|Others|); each state re-deals under every other ranking (the period change), which is the generated
count.
