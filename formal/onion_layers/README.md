# `formal/onion_layers` — the onion layer deal, model-checked and counted

**What this is.** CC 5.4.6 item 4 states that the three onion layers are dealt once per rendezvous
period as a pure function of the fold: who relays (the five-leg membership predicate), the seat-like first
(serve seats and steward-conferred `infra:relay` standings), then the others, sorted by `H(key_id ‖ period)`,
round-robin over three layers, the others capped at `c × seat-like` in each layer, and a floor of three per
layer. CIRISEdge implements it in `src/transport/onion_layers.rs#deal_layers` and witnesses it over the
CSD/4 catalogue T0–T19. This directory is the same deal as a TLA+ model and a Lean counting file, built from
that Rust witness (CIRISEdge `FSD/ONION_ROUTING.md` §4).

**The hash, abstracted.** `H` is SHA-256 over a domain tag, the key id and the period; the model cannot
compute it and does not need to: `rank` ranges over **every** ordering of the relays (`PermsOf`), so each
invariant is checked for every possible hash and every period. The adversary's placement among the others
(`hostile`) ranges over every subset. Two nodes are two computations of the deal from the same fold
(`viewA`, `viewB`); the sort is an insertion sort whose result does not depend on the order the relay set is
walked in — the "same rows in a different arrival order" case the Rust witness also runs.

## Invariants (`OnionLayers.tla`)

| Name | Statement | CC |
|---|---|---|
| `Inv_DealDeterministic` | two nodes holding the same rows deal identical layers | 5.4.6 item 4, `CLM-onion-layer-deal` |
| `Inv_HostileShareBound` | in every layer, others ≤ c × seat-like; hence for ANY hostile placement among the others, hostile × (1 + c) ≤ c × layer size: the hostile share of a layer is at most c / (1 + c) | 5.4.6 item 4, the cap |
| `Inv_NeverWorse` | every seat-like relay is dealt (none capped); seat-like counts across layers differ by at most one; every relay is dealt or capped, never lost; only others are capped | 5.4.6 item 4 |
| `Prop_FloorHonest` | available ⇔ every layer has three members; available ⇒ every layer has a seat-like member ⇒ at least three seat-like relays in the deal | 5.4.6 item 4, the floor |

## Configurations and results (2026-10-22, TLC 1.7.4, Java 21, this host)

| Config | Seat-like | Others | c | States | Result |
|---|---|---|---|---|---|
| `OnionLayers_2s3o.cfg` | 2 | 3 | 2 | 960 distinct (120 rankings × 8 placements) | no error, 2 s |
| `OnionLayers_2s4o.cfg` | 2 | 4 | 2 | 11,520 distinct (8,490,240 generated) | no error, 2 min 22 s |
| `OnionLayers_3s3o.cfg` | 3 | 3 | 2 | 5,760 distinct (4,199,040 generated) | no error, 1 min 06 s |
| `OnionLayers_3s3o_c1.cfg` | 3 | 3 | 1 | 5,760 distinct (4,199,040 generated) | no error, 47 s |

A seven-relay configuration (3 seat-like + 4 others) was tried and withdrawn: 80,640 distinct states
with 5,040 successors each is hours of TLC for no new property; the c = 1 point is checked at six relays.
Every configuration with two seat-like relays is below the floor at every ranking (`Prop_FloorHonest`'s
third conjunct is what makes that an honest "unavailable", not a vacuous pass); the three-seat
configurations reach the floor exactly when each layer receives one seat-like member.

## The counting bounds (`OnionLayersCount.lean`, core Lean 4.14, no Mathlib, no `sorry`)

| Theorem | Says |
|---|---|
| `hostile_share_bound` | under the cap `n ≤ c·s`, any hostile `h ≤ n` satisfies `h·(1 + c) ≤ c·(s + n)` |
| `size_le` | a layer's size is at most `(1 + c)·s`: capacity grows with seat-like members, never with others alone |
| `no_seat_no_layer`, `floor_needs_a_seat`, `floor_needs_three_seats` | a layer with no seat-like member is empty; the floor needs one per layer, three in all |
| `dealt_le`, `dealt_le_all` | the dealt total is at most `S + min(O, c·S) ≤ (1 + c)·S` and at most `S + O` (the crowd arithmetic for any N) |
| `dealt_mono_c`, `dealt_mono_seats` | raising `c` or adding a seat-like relay never lowers the dealt total (never worse) |

## What the model does not cover (residuals)

- The membership predicate's five legs are inputs, not modelled: a relay in `SeatLike ∪ Others` has
  already passed them. The Rust witness (`membership_legs_and_seat_violations`) covers each leg.
- Liveness (availability = floor ∧ ≥ 3 answering relays per layer, per node) is outside the deal by
  design (`src/transport/onion_liveness.rs`); the model's `Available` is the floor only.
- The deal over a period boundary (a packet in flight while the layers change) is a relay-side property:
  relays forward without consulting the deal, so nothing here depends on it.
- The hash is abstracted to an arbitrary ranking; collision behaviour of SHA-256 is not modelled (the Rust
  key breaks ties by `key_id`, so a collision cannot make the order partial).

## Running

```
java -cp ../../tla2tools.jar tlc2.TLC -workers auto -deadlock -config OnionLayers_2s3o.cfg OnionLayers.tla
lean OnionLayersCount.lean
```

CI: `ci/formal-onion-layers.yml` is the job to splice into `.github/workflows/formal.yml` (the TLC and
Lean steps mirror the existing `mesh` and `roster` jobs).
