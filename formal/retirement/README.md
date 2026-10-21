# `formal/retirement` — the agent retirement ladder, model-checked

**Why.** This is plane model D of `review/notes/formal_closure_rc9_2026-10-18.md` §5, and it covers
lifecycles 7 and 8 of that note's table. `formal/guarantees` checks the Retirement Standard as a
single step (`RetirementFloor`, `Inv_RetirementStandard`). This module refines that step into the
seven-state machine that CC 7.5.5 puts on the wire. The machine is
`retirement:{state}` = decided → frozen → secrets_destroyed → handed_over → notified →
custodian_minted → retired. It also includes:

- the four sibling families of CC 3.1.5: `preserve_request`, `preserve_response`,
  `archive_release:{basis}` and `lawful_order:release`;
- the steward's planned shutdown with its objection window (CC 7.5; executive summary item 5);
- the role gate on a forced shutdown (G16, `CLM-agent-forced-shutdown-role-gate`);
- the walk-away of CC 1.13.2, which is not a retirement;
- the refuse verb (CC 1.3, CC 1.9; G17);
- the subject's withdrawal inside the sealed record (CC 7.5.5, CC 3.3.1, CC 4.5.3; G22).

It realises the `agent.retirement` and `agent.status` rows of `formal/STATE_TABLE.tsv`. The
`retirement` variable takes exactly the eight values of the table, with `none` meaning no row.
`opStatus` carries the operating statuses the table marks as model vocabulary.

**What it models.** One agent and one `retirement_id`. There are six keys:

- **The agent's key** self-emits every ladder row, up to and including `retired`.
- **The steward** is the ROOT or AUTHORITY principal for this agent.
- **The operator** is the person the agent runs for. It is a lesser role on the shutdown path, it
  receives the `preserve_request`, and it answers it.
- **The custodian** key is minted at `custodian_minted`, named in the `retired` row, and signs every
  later custody row.
- **A Wise Authority** emits `archive_release`.
- **A subject** is a person who has ordinary content and one adverse row inside the record.

The objection window is a per-proposal age, so there is no global clock. The other variables are:

- `decided_by`, which is the steward, the operator, or the agent itself on the welfare route (the
  CC 7.5.3 petition);
- the agent's answer inside the window, which is to object or to ask to postpone;
- the steward's decision, recorded under the steward's name;
- the preserve response, which is accepted or declined, and a declined answer stays;
- the seal, which is sealed, opened by WA approval, or opened by a lawful order;
- the record, which is live, held, discarded after a decline, or destroyed by court order;
- the signers of the custody rows;
- one task, which may be pending, refused or done;
- the subject's ordinary content and the adverse row about them.

**The adversary.** Safety is checked with every key acting arbitrarily. Any key may attempt any
row family at any moment. An attempt the admission rule refuses changes nothing, so it is a stutter
and is not written as an action. The admission predicates are therefore the whole of the safety
result, and they hold against an adversary who holds any one key, or all of them. The `Adversary`
constant names the key that is not assumed to make progress. Fairness is withheld from that key,
so the constant affects `Prop_LadderCompletes` only.

## Configurations and TLC verdicts

TLC 2.19, `-deadlock`, objection window `W = 2`. The verdicts are from 2026-10-18. State counts
are distinct states. For a configuration that must fail, the table gives the counterexample TLC
printed. A crisis toggle in a trace changes nothing that the property reads.

| Config | Reading | Expectation | Verdict |
|---|---|---|---|
| `Retirement_ruled.cfg` | every rule on; shutdown mode `conditional` (Ally's template) | all invariants and properties hold | **closes**, 594,048 states, depth 25 |
| `Retirement_ruled_always.cfg` | ruled; mode `always_consent` | holds | **closes**, 295,392 states |
| `Retirement_ruled_instant.cfg` | ruled; mode `instant` (tier 1–2) | holds | **closes**, 297,024 states |
| `Retirement_adv_operator.cfg` | ruled; the operator makes no progress | holds: the ladder needs nothing from the operator | **closes**, 594,048 states |
| `Retirement_adv_custodian.cfg` | ruled; the custodian makes no progress | holds | **closes**, 594,048 states |
| `Retirement_adv_steward.cfg` | ruled; the steward never decides | a planned retirement stays at `decided` | `Prop_LadderCompletes` violated (stutters at `decided`): the stated residual |
| `Retirement_adv_agent.cfg` | ruled; the agent's key stops emitting | the ladder stops where it is | `Prop_LadderCompletes` violated (stutters at `secrets_destroyed`): the stated residual |
| `Retirement_postpone_unbounded.cfg` | the steward may grant any number of postponements | the window can reopen forever | `Prop_LadderCompletes` violated (a loop of objection, tick, grant) |
| `Retirement_cancel_after_frozen.cfg` | `withdraws` of `decided` admitted after `frozen` | must fail | `Inv_CancelOnlyBeforeFrozen` violated; TLC's trace has 5 steps: a crisis toggle, decide, steward decides, frozen, withdraw |
| `Retirement_operator_opens_seal.cfg` | `archive_release` admitted from the operator or the custodian | must fail | `Inv_SealOpensByOneRow` violated in 3 steps: emergency decide, frozen, the operator's release |
| `Retirement_skip_objection.cfg` | the steward decides and the agent freezes while the window is open | must fail | `Inv_ObjectionHeard` violated in 3 steps: decide, steward decides while the window is open, frozen |
| `Retirement_custodian_before_retired.cfg` | custody rows admitted from `custodian_minted` | must fail | `Inv_CustodianOnlyAfterRetired` violated in 7 steps: decide, five rungs, a custody row at `custodian_minted` |
| `Retirement_operator_forces.cfg` | no role gate (mode `always_consent`) | must fail | `Inv_ForceRoleGate` violated in 1 step: the operator decides an emergency retirement |
| `Retirement_walkaway_erases.cfg` | walking away discards the held record | must fail | `Prop_WalkAwayKeepsRecord` violated in 3 steps: decide, frozen, walk away |
| `Retirement_ladder_overrides_refusal.cfg` | `frozen` marks a refused task done | must fail | `Prop_RefusalStands` violated; TLC's trace has 5 steps: a crisis toggle, decide, new task, refuse, frozen |
| `Retirement_seal_blocks_consent.cfg` | the seal stops the subject's withdrawal | must fail | `Inv_SubjectRightsSurvive` violated; TLC's trace has 3 steps: a crisis toggle, decide, frozen, after which the subject's withdraws is not enabled |
| `Retirement_subject_withdraws_adverse.cfg` | the subject's own key withdraws the adverse row about them | must fail | `Inv_SubjectRightsSurvive` violated; TLC's trace has 2 steps: a crisis toggle, the subject's withdraws of the adverse row |

The ruled configuration also has reachability witnesses in `RetirementWitness.tla`. Each witness
says that some ruled behaviour never happens, and TLC must find it happening, so the closing
configuration is not closing over an empty machine. All eleven are reached:

- a planned retirement by the steward, postponed once, reaches `retired`;
- the welfare route reaches `retired`;
- an emergency retirement after the steward forced a stop reaches `retired`;
- an operator's retirement, over the agent's objection, reaches `retired`;
- a cancellation lands;
- after `retired`, the subject withdraws while the seal stays shut and the custodian executes the
  tombstone;
- after `retired`, the seal is opened by a lawful order;
- the operator declines preservation and lets the record go;
- the operator walks away mid-ladder and the ladder still completes with the record held;
- a refused task is still refused at `retired`;
- the custodian withdraws the adverse row on the controller's side.

## The properties, with their CC decimals

| Property | What it says | CC |
|---|---|---|
| `Prop_LadderForwardOnly` | The ladder moves one state at a time in the stated order. The only other move is the one cancellation, back to `none`. Nothing follows `retired`. | 7.5.5; 3.1.5 (`retirement:{state}`) |
| `Inv_CancelOnlyBeforeFrozen` | The `decided` row is withdrawn only while no `frozen` row exists. The model has no `cancelled` state; the cancellation is the grammar's `withdraws`. | 7.5.5; 3.1.5; 2.4.1.1 |
| `Inv_SecretsDestroyedBeforeHandover` | `handed_over` implies `secrets_destroyed`, which implies `frozen`. From `frozen` on, the record is assembled and sealed. A `preserve_response` exists only after hand-over. | 7.5.5; 7.5.4 step 3 |
| `Inv_CustodianOnlyAfterRetired` | Every custody row is signed by the custodian key that the `retired` row names. None exists before `retired`. Tombstones executed after `retired` are custody rows. | 7.5.5 ("the custodian is listed, not delegated"); 3.2 T6 |
| `Inv_SealOpensByOneRow` | The seal opens only by an `archive_release` from the WA key. A `lawful_order` basis requires the steward's `lawful_order:release` row. The operator and the custodian never open it. | 7.5.5; 3.1.5 (`archive_release`, `lawful_order:release`) |
| `Inv_ObjectionHeard` | A planned retirement reaches `frozen` only after the window closed and the steward decided on the record, never while the window was open. | 7.5; executive summary item 5; `CLM-agent-shutdown-consent` |
| `Inv_ForceRoleGate` | A forced stop is by ROOT or AUTHORITY, and so is an emergency retirement. Outside a no-consent moment of the conditional or instant mode, a lesser role's stop is refused. | 7.5; G16; `CLM-agent-forced-shutdown-role-gate` |
| `Inv_WalkAwayEnabled` | The operator's walk-away is enabled in every state where the agent is not already off. It has no guard on the agent. | 1.13.2; 7.5.5 (the wind-down binds the holder who retires) |
| `Prop_WalkAwayKeepsRecord` | A walk-away changes neither the ladder, the record nor the seal. It is not a retirement. | 1.13.2; 7.5.5 |
| `Inv_RefuseAvailable` | While the agent's key is live, a pending task can always be refused. | 1.3; 1.9; G17 |
| `Prop_RefusalStands` | A refused task stays refused through every ladder step. The ladder ends the agent and makes it do nothing. | 1.3; 1.9; G17 |
| `Inv_SubjectRightsSurvive` | The subject's own withdrawal of their ordinary content is enabled whenever the record exists, sealed or not and before or after `retired`. An adverse row about them is withdrawn only on the producer's side: the agent, then the custodian. | 7.5.5; 3.3.1 (plain rules 1c, 1e); 4.5.3 (controller-only) |
| `Prop_LadderCompletes` | Under fairness for the agent's key and the steward, a decided retirement reaches `retired` unless it is cancelled. | 7.5.5 |

## What the runs showed

- **The ruled configuration closed on its first run.** No counterexample forced a change to an
  admission rule. One witness was wrong as first written. It asked for an emergency retirement to
  end with the agent's status still `forced`, but `frozen` replaces that status. The witness now
  asks who forced the stop.
- **Postponement has to be bounded, or the steward's decision needs strong fairness.** With
  postponements unbounded, the cycle of postpone, tick and grant keeps the window reopening.
  The steward's decision is then never continuously enabled, and the ladder never leaves
  `decided`. The ruled reading allows one postponement per proposal. The text does not say how
  many, which is listed under Ambiguities below.
- **The ladder is live only if two parties make progress.** If the steward never decides, a
  planned retirement waits at `decided` forever. If the agent's key stops emitting, the ladder
  stops where it is, because every rung up to `retired` is self-emitted. The operator, the
  custodian, the WA and the subject are not needed for the ladder to complete.
- **An operator's walk-away mid-ladder does not stop the ladder in the model.** The rungs are
  emitted by the harness running the retirement, which is the steward's process. The rungs are
  not gated on the agent being on. That separation is an assumption, recorded under Residuals.

## Residuals: what the model does not cover

- **A stolen custodian key.** Custody rows are admitted because the `retired` row names the key
  and is current. No row can replace that key: the agent's key is retired, and the custodian is
  not a `delegates_to` that could be renewed or revoked. A thief holding the custodian key is
  admitted for every custody row, though the seal still holds against it. CC 7.5.5 names no
  replacement path.
- **Time.** The model has no clock. The ≥ 90 days public notice for ST ≥ 3 (CC 7.5.4 step 1),
  the five-year `preserve_until` and the 120-day review are not modelled.
- **Subject-scoped releases.** A subject-scoped `archive_release` for a data subject access request
  is not modelled; only whole releases are.
- **`legal_hold`.** Holds set, lifted or violated on the record are not modelled. Neither are the
  hard cases of CC 3.1.9.4 they raise.
- **Further ids.** The model has one `retirement_id`. A new `decided` after a cancellation would be
  a fresh instance of the same machine.
- **Ordinary stops.** The accept, contest and negotiate exchange of an ordinary stop (G15) and the
  constitutional halt (CC 4.2.1.1) are checked in `formal/guarantees` and `formal/accord_halt`, not
  here.
- **The closing dialogue.** It is a tier-gated steward option and not part of the Standard
  (CC 7.5.5), so it is not modelled.
- **Walk-away during the ladder.** The model assumes that turning off the operator's copy does not
  stop the harness running the retirement.

## Ambiguities in the text

- **Who withdraws `decided`.** The CC 3.1.5 row says the ladder is "Self-emitted up to `retired`
  (attester = the agent key)". It also says "A planned retirement is cancelled by the decider
  `withdraws`-ing the `decided` row". Under CC 2.4.1.1 rule 1, the producer withdraws, and the
  producer is the agent key. The model assumes the key named in `decided_by` withdraws, and that
  this is admitted because the row names it.
- **Where the objection window is stated.** The window ("A steward's planned shutdown is
  explained, the agent may object or ask to postpone inside a short window, the steward decides")
  appears in the executive summary and in `CLM-agent-shutdown-consent`. It does not appear in the
  body of CC 7.5 or CC 7.5.5. The text does not bound postponements, and does not say whether the
  window applies when the operator decides. The model allows one postponement. It gives every
  planned retirement other than the welfare route a window and requires the steward's decision.
- **Walk-away against the role gate.** "Any person may turn off, remove or walk away from an agent
  at any time without asking it" (executive summary item 5; CC 1.13.2) sits beside G16, "Only a
  ROOT or AUTHORITY principal may force a shutdown over the agent's objection". The model reads the
  first as acting outside the shutdown request path and the second as the in-band shutdown path.
  They are two actions, and only the second is gated.
- **Adverse rows after `retired`.** CC 7.5.5 says a deletion inside the record is "written by
  whoever holds custody". The producer of an adverse row about the subject is the retired agent.
  The model assumes the custodian executes the controller's rule-1 withdrawal on request, and that
  the subject's own key never does (CC 4.5.3).

## Files and how to run

- `Retirement.tla` is the module, with one switch per rule.
- `Retirement_*.cfg` are the configurations in the table above.
- `RetirementWitness.tla` holds the reachability witnesses.
- `run.sh` runs every configuration and every witness and checks each verdict against its
  expectation. It exits 1 on any mismatch.

```
TLA2TOOLS=/path/to/tla2tools.jar ./run.sh
java -cp tla2tools.jar tlc2.TLC -workers auto -deadlock -config Retirement_ruled.cfg Retirement.tla
```

Every run finishes in under half a minute.
