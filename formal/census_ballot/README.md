# `formal/census_ballot` — the census, the secret ballot and the base law, model-checked and counted

**What this is.** The steward's rulings of 2026-10-22 (CC 4.5.13 the policy's base; 5.4.6 the cohort's
invisibility; 6.1.2.1.2 `n_eff`) and the edge/persist design of the same day, final: each period every
owner-bound rooted node of a community emits exactly one **census report**; a report is a vector of
community cells, each a **one-hot over its buckets** (the expected-active cell `ea: yes/no` — was the owner
active in this or the previous three periods, computed by the owner from its own history — and, when the
community carries a ballot, the vote cell, one bucket per option with `abstain` doubling as the padding
bucket); every entry is **secret-shared** `s0 + s1 ≡ v (mod M)` to the two **community members** drawn
from the roster by `H(secret ‖ period)` as the period's tally members; each tally member sums the shares
it accepted and the published cell is `partial_0 + partial_1 mod M`, with a mass commitment over the
period's tokens. A report is accepted only when both halves arrived, its token (one per owner per period)
is fresh, and the one-hot validity proof the two members verify jointly passes — so an accepted report adds
exactly one count to one bucket, every accepted owner has mass one, and `n_eff = source_count`. A cell
publishes only above the **k-floor** (`source_count ≥ K`). Mesh cells go to two federation seats drawn by
`H(period ‖ class)` under the same scheme; they are not modelled here, the community plane is.

**The base law.** The expected-active composite `EA` is the published `ea: yes` count. Above the
small-community size the base a governance fraction is taken over is census-derived: it never falls more
than 10 % in one period (`base_t ≥ ⌈0.9 · base_{t−1}⌉`), never below the floor
`max(owners active this period, ⌈½ · last stable composite⌉)`, and a one-period fall of the composite by
more than one third **freezes** it (`base_t = base_{t−1}`) until the composite recovers to within that
third of the composite before the fall. Readings this model fixes (each a steward's word, not the
design's): *stable* means the composite stood on its own — `EA ≥` the ratchet term, so the base was not
propping it; the freeze is released by recovery to `⅔` of the pre-fall composite; a period whose composite
is refused (below the k-floor) leaves the base where it was.

**Two paths, one base (steward, 2026-10-22).** Governance acts — enact, cancel, roster, moderation — stay
**identified** rows under [`formal/two_path`](../two_path/) and take from the census only their **base**:
`Inv_BaseRatchet` and `Inv_KFloor` are what that path relies on. The secret-shared tally is a community
instrument for **polls and elections**, used at the community's discretion; `Inv_TallyThreshold` is its
property: a poll passes only against `base_t`, never against the responders alone.

**The hash and the proof, abstracted.** The draw `H(secret ‖ period)` ranges over **every** pair of roster
members; the validity proof is sound and complete by assumption (the two members jointly learn exactly
whether the reconstructed vector is one-hot, nothing else). The adversary: `Colluding` members pool their
views when drawn; `Silenced` owners' reports stop arriving once the adversary silences them, one at a time, at any period boundary; `Dishonest` owners
emit any vector; a `Lossy` network delivers one half of a report only; any owner may replay its report.
Each defence is a switch (`PadWhenClosed`, `Dedupe`, `Validate`, `JointAccept`, `Gate`, `Ratchet`,
`ThresholdBase`) that one twin configuration turns off, so a reader sees what each invariant catches.

## Invariants (`CensusBallot.tla`), named as edge states them

| Name | Statement | CC |
|---|---|---|
| `Inv_SharePrivacy` (= `Inv_BallotSecrecy`) | a colluding tally member's view — every share it received and its partial sums — is identical under every one-hot value of every other owner's accepted report (for each owner and alternative vector a share assignment producing the same view is exhibited); guard: the two tally members do not both collude | 5.4.6 |
| `Inv_Correctness` (= `Inv_TallyExact`) | `partial_0 + partial_1 ≡ Σ accepted values (mod M)`, and equal to the sum when it is below `M` | 6.1.2.1 |
| `Inv_Validity` | every accepted report is one-hot (entries in {0,1}, each cell sums to 1) | 6.1.2.1.2 |
| `Inv_Agreement` | the two tally members accept the same report set: equal token sets, equal `source_count` | 6.1.2.1 |
| `Inv_OnePerOwner` (= `Inv_OneReturnPerOwner`) | one report counted per owner per period; `source_count = |accepted|`; `n_eff = source_count` | 6.1.2.1.2 |
| `Inv_KFloor` | no published cell has `source_count < K` | 5.4.6 |
| `Inv_DominanceGate` | no published composite has one owner with more than half the mass (so at least two sources) | 6.1.2.1.2 |
| `Inv_OccurrenceInvisible` | every reporting member sends the same number of entries to each tally member whether or not a ballot is open, and the set of wire profiles a member can produce is identical with and without an open ballot | 5.4.6 |
| `Inv_BaseRatchet` | `base_t · 10 ≥ base_{t−1} · 9`; `base_t ≥` the ratchet trajectory from the first census; `base_t · 2 ≥ last stable composite`; `base_t ≥` owners active this period; `base_t ≥` the last composite; under the partition freeze `base_t = base_{t−1}` and `base_t ≥` the pre-fall composite | 4.5.13 |
| `Inv_TallyThreshold` | a poll passes only at `approvals · 3 > 2 · base_t` (or the approval floor at the window against `base_t`), `base_t` the census base or the standing roster at or below the small-community size | 4.5.13 |
| `Prop_HonestChangeResolves` | an open ballot is decided — passes or is rejected — within its window (weak fairness) | 4.5.13 |
| `Inv_SecrecyWithoutTheGuard` | the dye for the two-colluding twin: `Inv_SharePrivacy` without the guard | — |

The owners are `1..N`, the roster order; the configurations are read against the design's defaults
(enact ⅔, cancel ⅓, approval floor ⅓, two voices minimum, ratchet 9/10, freeze ⅓, floor ½).

## Configurations and results (2026-10-22, TLC 1.7.4, Java 21, this host)

See [`RESULTS.md`](RESULTS.md) for the measured counts and times. In short:

| Config | Owners · M · cells | What it exercises | Result |
|---|---|---|---|
| `CensusBallot_2o_m3_lossy` | 2 · 3 · vote (three buckets) | lossy delivery, per-period absence, colluder as `a0` or `a1`, every draw | closes |
| `CensusBallot_2o_m3_dishonest` | 2 · 3 · vote | a dishonest owner emitting any of the 27 vectors; validity refuses all but the one-hot | closes |
| `CensusBallot_2o_m3_both_cells` | 2 · 3 · `ea` + a two-bucket poll | both cells shared over two periods; the census base drawn from the shared `ea` | closes |
| `CensusBallot_2o_m3_silenced` | 2 · 3 · vote | the silencer removes one of two owners at any boundary: the freeze; the only instance that also checks `Prop_HonestChangeResolves` (TLC's fairness check costs ~80 s even here) | closes |
| `CensusBallot_3o_m2` | 3 · 2 · vote | three roster members, every tally pair, one colluder | closes |
| `CensusBase_3o_silence_one` | 3 owners, `Scale = 10`, `ea` in the clear | one owner in three silenced at any period: a fall of exactly one third, no freeze, the ratchet carries the base 30 → 27 → 25 → 23 → 21 → 20 | closes |
| `CensusBase_3o_silence_two` | 3 · 10 | two in three silenced, together or one after the other: a fall of two thirds (or two of one third and a half), the partition freeze holds the base | closes |
| `CensusBase_3o_free` | 3 · 10 | nature free over absent/idle/active for six periods | closes |
| `CensusBase_3o_floor_binds` | 3 · 10, freeze at ½ (an instrument), two owners silenced one at a time | the composite stepping 30 → 20 → 10 without a freeze, the ratchet carrying 27, 25, 23, 21, 19, 18, 17, 16, 15, and then the ½-of-last-stable floor (15) as the binding term at the eleventh period | closes |
| `CensusBase_3o_reach_ratchet`, `_reach_frozen`, `_reach_floor` | the three instances above | reachability dyes: `Reach_RatchetCarries`, `Reach_Frozen`, `Reach_FloorBinds` are each violated, so the closures above are not vacuous | fail by design |

| Twin | Switch | Fails by design |
|---|---|---|
| `CensusBallot_3o_m2_two_colluding` | `Colluding = {1, 2}` | `Inv_SecrecyWithoutTheGuard`: when both tally members collude the third owner's vote is read |
| `CensusBallot_2o_m3_no_padding` | `PadWhenClosed = FALSE` | `Inv_OccurrenceInvisible`: a closed period sends fewer entries |
| `CensusBallot_2o_m3_no_dedupe` | `Dedupe = FALSE` | `Inv_OnePerOwner`: a replayed token counts twice, `n_eff ≠ source_count` |
| `CensusBallot_2o_m3_no_validity` | `Validate = FALSE` | `Inv_Validity`: a two-ones vector is counted |
| `CensusBallot_2o_m3_no_joint` | `JointAccept = FALSE` | `Inv_Agreement`: one half arrives, one member counts it |
| `CensusBallot_2o_m3_no_kfloor` | `Gate = FALSE` | `Inv_KFloor`: a lone report publishes |
| `CensusBallot_2o_m3_responders` | `ThresholdBase = "responders"`, `K = 1` | `Inv_TallyThreshold`: one approval passes against one responder while the frozen base is two |
| `CensusBase_3o_no_ratchet` | `Ratchet = FALSE` | `Inv_BaseRatchet`: the base follows the silencer down 30 → 20 in one period |

## The counting facts (`CensusBallotCount.lean`, core Lean 4.14, no Mathlib, no `sorry`)

| Theorem | Says |
|---|---|
| `split_sum`, `tally_exact_mod`, `tally_exact` | one shared entry reconstructs mod `M`; over any list of reports `partial_0 + partial_1 ≡ Σ values (mod M)`, and equals the sum when the sum is below `M` |
| `secrecy_one_share`, `secrecy_one_share_unique` | for every share and every value there is a complement, and exactly one below `M`: a single tally member's view is uniform over the value |
| `onehot_histogram` (with `sum_vadd`, `length_histogram`) | the histogram of one-hot reports sums to the number of reports: a valid report adds exactly one count to one bucket |
| `step_ge_floor`, `step_ratchet`, `step_mono`, `ratchet_floor_step`, `ratchet_floor`, `run_ge_last_floor` | one period of the law honours the floor and `base_t · q ≥ base_{t−1} · p`; after `t` periods `base_t · q^t ≥ base_0 · p^t`, whatever the composites (silencing to zero is the worst case, by monotonicity) |
| `freeze_holds`, `frozenStep_ratchet` | a one-period fall of more than the freeze fraction leaves the base where it was; otherwise the ratchet bound applies |
| `two_sumsq_le`, `dominance_bound`, `dominance_needs_two`, `n_eff_unit` | if no owner holds more than half the mass then `n_eff = ⌊(Σm)²/Σm²⌋ ≥ 2`; one mass alone fails; with unit masses `n_eff = source_count` exactly |

## What the model does not cover (residuals)

- **Coercion resistance is not claimed and not modelled.** A member can reveal its own shares (or its
  randomness) to a coercer and prove how it voted; the design does not prevent that and this model states
  no invariant for it. What is claimed is secrecy among members against one colluding tally member.
- **Two colluding tally members read every vote.** The guard in `Inv_SharePrivacy` is the claim's edge;
  `CensusBallot_3o_m2_two_colluding` shows the reading. The draw `H(secret ‖ period)` is what keeps a
  colluding pair from arranging to be drawn together; the model ranges over every pair and says nothing
  about the draw's unpredictability.
- **The range of shares is assumed in bounds.** The tally is exact modulo `M`; counts are exact only
  while they stay below `M` (`tally_exact` carries the hypothesis). The design's modulus is large; the
  model's is 2 or 3, which is why a `M = 2` instance cannot carry the shared `ea` cell for two owners (two
  "yes" publish as zero, and `Inv_BaseRatchet` catches it) — recorded here rather than hidden.
- **The validity proof is an oracle.** The model assumes the two members jointly learn exactly whether a
  vector is one-hot. The construction of the proof is edge's; a refused report is visibly refused, which is
  why `Inv_SharePrivacy` is stated over accepted reports.
- **Honest-but-curious tally members.** A colluding member reads; it does not lie about its partial sum.
  A member that publishes a wrong partial sum corrupts the cell undetectably here: the mass commitment
  binds the token set, not the shares. Integrity against a lying tally member is not claimed.
- **Availability is not modelled.** A silenced or offline tally member, or a lossy network, loses a
  period's cell; the invariants are about what is published, not that something is.
- **The tally is public by design.** With two voters the published counts reveal each vote to the other
  voter; the k-floor (`K = 2` in the ruled instances) is the minimum the dominance gate requires, not a
  privacy guarantee. `K` is the community's to set.
- **The draw is a constant per period.** `agg` is chosen with the first report of the period; the model
  does not let the pair change mid-period.
- **The expected-active cell is owner-computed.** Because the composite is a sum, the four-period window
  cannot be recovered from published counts; the owner emits its own "active in the last four periods"
  bit. Two consequences the model made visible: an owner whose node does not report in a period drops
  out of that period's `EA` at once (the window smooths activity, not presence — the ratchet and freeze
  are what bound the effect); and an owner that keeps reporting while idle stays in `EA` for three more
  periods, so a community that merely goes quiet sees its base fall only after the window, while a
  community whose nodes go dark sees it at once.
- **At small bases the integer ratchet is inert.** `⌈0.9 · b⌉ = b` for `b ≤ 9`, so below ten the base
  cannot fall at all; the base configurations count in units of `Scale = 10` owners to exercise the
  arithmetic. Communities at or below the small-community size use the standing roster, so no real
  community sits in that band under the census law.
- **The floor's first arm is subsumed.** "Owners active this period" is a subset of the expected-active
  owners, so `base ≥ EA` already implies it; it is kept as stated.
- **A rising composite lifts the base at once.** Admission is the roster's door (membership), not this
  model's; sybil inflation of the base is out of scope here.

## Running

```
java -cp ../../tla2tools.jar tlc2.TLC -workers auto -deadlock -config CensusBallot_2o_m3_lossy.cfg CensusBallot.tla
lean CensusBallotCount.lean
```

CI: the `census_ballot` job in `.github/workflows/formal.yml` runs every ruled configuration to closure,
each twin to its named failure, and the Lean file.
