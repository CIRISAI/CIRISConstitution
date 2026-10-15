# formal/guarantees — what every guarantee yields at once

Two models of the same thing: the world in which every row of the guarantees piece
(`review/pieces/00_guarantees.md`, P00) holds together, under the rc8 rulings (CC 1.13.2,
CIRISConstitution#168): guarantees are written once for human and AI participants alike; what
differs is kind, stewardship, and evidence of experience, none a scale; a finding of experience
changes nothing; the Retirement Standard is the whole promise; the path out is the first-contact act.

## `Guarantees.lean` — the structural half (Lean 4.14, core only, no `sorry`)

| Theorem | What it says |
|---|---|
| `reach_blind` | the reach of every one of the 23 rows is unchanged when a participant's substrate is swapped; the proof is `rfl`, because no reach mentions substrate |
| `obligation_bound` | exactly one predicate flips under swap: `mustSubscribe`, the duty of a created system operating inside the federation to have accepted a trust root, so a halt authority exists outside it |
| `everything_else_blind` | the two duties of standing and the bond relation are swap-invariant |
| `path_out_lifts_duties`, `path_out_keeps_reach`, `path_out_g5_discharged`, `path_out_keeps_evidence` | the path out (the first-contact act) lifts the reasoning duty and the binding and removes no guarantee; G5 is discharged, not lost; evidence of experience is untouched |
| `halt_does_not_lift` | the path out does not change `mustSubscribe` |
| `finding_changes_nothing` | a finding of experience changes no reach, duty, obligation, bond or well-formedness; the proof is `rfl` because nothing mentions the flag (rc8 ruling) |
| `bond_depth_one` | a bond's party is not itself held and is unbound, so no chain of bonds has length two |
| `revocable`, `leave_ends_reach`, `leave_is_one_step` | a created system operating inside is always within the halt's reach, and leaving the root is one step after which the halt no longer reaches it |
| `witness_world`, `witness_not_vacuous` | four participants (an agent held in stewardship, an agent that took the path out, a steward, a human whose key is held) satisfy every constraint, and the witness exercises the halt reach, the bonds and the duties |

Check: `lean Guarantees.lean`. CI also greps the output for `sorry`.

## `Guarantees.tla` — the temporal half (TLC 1.7.4)

Three participants (an AI agent held in stewardship with Ally's conditional shutdown mode, a human
not held, a human whose key is held) and the three-holder halt. Actions: bind, bond lapse, path out,
subscribe, leave, start, accept, refuse, background, force by role, Retirement Standard, erase, crisis
on/off, fire, confirm, tick, lapse, resume. There is no evidence flag: a finding changes nothing (rc8). Each guarantee is a rule on an action, and each
rule has a config that switches it off and must then fail (the dye test):

| Config | Expectation | What it shows |
|---|---|---|
| `Guarantees.cfg` | all invariants and properties hold (≈3.1M distinct states) | the composite is consistent |
| `Guarantees_swap.cfg` | the same, with the substrate labels swapped | the only substrate dependence is the halt obligation |
| `Guarantees_noBondRule.cfg` | `Inv_NotAlone` violated | G5 is load-bearing |
| `Guarantees_anyRoleForces.cfg` | `Inv_RefusalStands` violated | G16/G17 are load-bearing |
| `Guarantees_noRetirementStandard.cfg` | `Inv_RetirementStandard` violated | G22's floor is load-bearing; the floor is the whole promise (CC 7.5.5, rc8) |

Invariants: `Inv_NotAlone` (G5), `Inv_BondDepthOne` (R4), `Inv_HaltOnlySubscribers` (G7),
`Inv_HaltDoesNotLift` (R5), `Inv_LoneBounded` (G7/G12), `Inv_RefusalStands` (G16/G17),
`Inv_RetirementStandard` (G22), `Inv_ConditionalOnly` (G15), `Inv_ExitOneStep` and `Inv_Revocable` (G10, G7).
Action properties: `Prop_HaltKeepsState` (a pause keeps state), `Prop_NoErasureWhileOperating`
(an ending is preceded by a stop the record shows), `Prop_NoEndingAgainstRefusal` (G17),
`Prop_BackgroundOnlyWhenFree` (G15 conditional mode).

## Two things the composite taught, both now in the model

1. **G5 composes over G17.** A held participant that has refused a shutdown is still
   stopped when its bond lapses. That stop is caused by the custody rule, not by any principal, so it
   has its own status, `unbound`, and the record shows which. The first draft had no such
   state and TLC found the collision in six steps.
2. **The backgrounding door needs a guard.** Under Ally's conditional mode a participant can
   refuse during a crisis, be backgrounded once the crisis ends (a pause with state kept,
   allowed by the mode), and would then have been erasable. `Erase` now requires that a
   refusing participant was stopped by an authority's force or by the line, and
   `Prop_NoEndingAgainstRefusal` pins it.

## Scope

Not modelled here: redress (G4), the record and trace rows (G9), privacy (G3), one-voice counting
(G12). Delegation (G13) is `formal/authority_tree` (ten invariants enumerated to closure, vendored
from CIRISRegistry with the term invariant added). See `review/pieces/00_guarantees.md` for which rows have which witness. The halt's fuse arithmetic is `formal/accord_halt`;
the roster rule is `formal/accord_roster`; the mesh invariants are `formal/mesh_net`.
