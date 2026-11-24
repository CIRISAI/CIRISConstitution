# `formal/self_roster` — key states under one self, model-checked

**Why.** A model of the keys under one identity with one invariant to attempt: with three or
more keypairs under a self, a stolen device cannot on its own kick the other devices off, yet two
lost devices are recoverable from the one that remains (CC 3.3.6.4).

**The rule it models.** A roster change is a proposal signed by a live roster key and counted over
the roster it names. Its outcome is read from signed rows, and from nothing a node has of its own:
the lone path closes by rows and never by a node's clock (CC 3.3.6.4, "The lone path is a window
of rows"). The module has no clock.

- **A met count** gives its outcome with no landing row: a strict majority of the roster
  approving, the proposer counted, is `landed`; a strict majority of the others objecting is
  `refused`.
- **The proposer's withdrawal** refuses an open proposal. It is read after the majority's
  approval, so a met approval beats it. An approval that has the withdrawal in its past approves
  nothing.
- **The lone path.** A seated key signs a held row and then a landing that names it. The window's
  length is the difference of that key's own two instants, so it is the concluder's word. A held
  row counts only if it has in its past no row the target signed beyond what the proposal has in
  its own past. A landing concludes only where the table over its own past gives the outcome it
  states, and stands only while the table over every row that does not name it still does. An
  eviction is refused where the target signed any row; an addition has the same table without
  the target's silence.
- **The outcome** is open, contested, landed or refused. While a proposal is open or contested
  nothing has changed: the target stays seated and an added key is not seated.
- **An ended seat.** A row signed by a key whose seat was ended counts only where the row that
  ended the seat has it in its past.

**What the module carries.** Three or four devices under one self plus one spare; each device held
by the owner, by a thief, or by nobody (lost), and usable only by a holder who can authenticate on
it (the thief in the worst case, `StolenAuth = TRUE`). Each proposal carries the others' answers,
the proposer's withdrawal, whether the target signed a row beyond the proposal's past, and one held
row and one landing, both signed by the proposer. `formal/two_path/TwoPathRows.tla` writes the
rows out with their pasts, second landings and two nodes; the outcome here is that module's rule
restricted to these rows. **That restriction is stated, and no run checks the two modules against
each other.**

A decided proposal becomes the roster's next head by `Settle`: a reader takes it as the head the
next proposal names, and every other open proposal names a head with an acknowledged successor
and is void for that reader (CC 3.3.6.4, the head a self-roster row names). `OwnerPresent = TRUE`
means every device the owner holds has answered a proposal before a reader settles it.

**Bounds, and what is assumed and not checked.**

- Three or four initial keys and one spare; one theft and one loss, or two of either, as each
  configuration says. The adversary takes its devices before the owner's first act.
- One held row and one landing per proposal, by its proposer, stating `landed` and a full span.
  The landing's past is its held row alone or every row signed so far. A second landing, a
  landing by another key, and a landing that states `refused` are in `TwoPathRows.tla` only.
- The four-key configurations (`combined4_mixed`, `combined4_2stolen`) leave out the rows a thief
  signs that count for nothing or against itself (its withdrawal, a held row with the target's
  row in its past, a landing the table does not give). With them a run of `combined4_mixed` was
  stopped after four minutes at 5.2 million states and depth 18, with 800,000 states still
  queued; how far it goes is not known. The three-key configurations run those rows.
- The owner proposes the eviction of a key that still signs only where its own keys can carry the
  count, takes the lone path only where they cannot, and never withdraws. `mixed3_ownerlone`
  lifts the first of these to show what the lone path is worth against a key that signs.
- A lone landing is not final, and `Settle` is where the module stops following one: a late row
  against a landing that a later proposal already stands on is not modelled.
- For a seat ended by `Settle`, every earlier row of that key is taken to be in the past of the
  row that ended the seat (the reading that gives the ended key the most); every later row is
  spent. With a met count there is no single row that ended the seat, and the text does not yet
  say which row is meant.
- Liveness is checked under weak fairness of the owner's own steps (propose, answer, conclude,
  settle its own proposals).

**Configurations** (`run.sh` runs all of them and checks each verdict; TLA+ tools 1.7.4).

| Config | Policy / adversary | Expectation | TLC verdict |
|---|---|---|---|
| `combined3_stolen` | both paths; one stolen, owner present | both clauses hold; the thief is evicted by the count | **closes**, 71,495 states |
| `combined3_lost` | both paths; two lost | the owner lands two lone evictions and adds a device | **closes**, 524 states |
| `combined4_mixed` | both paths; four devices, one stolen and one lost | the owner evicts the lost key alone, then the stolen one by the count | **closes**, 1,602,102 states |
| `combined2_lost` | two keys, one lost | the remaining key evicts the lost one alone and adds | **closes**, 36 states |
| `combined1_add` | one key, the owner adds a device | at one key the addition lands at once | **closes**, 14 states |
| `unilateral3_lost`, `quorum3_stolen`, `reverse3_lost` | the remaining easy cells | close | **close**, 242 / 54,641 / 938 states |
| `mixed3_nospare` | three keys, one stolen and one lost, no spare; owner present | the owner's one live key is never evicted (safety only) | **closes**, 7,438 states |
| `mixed3_ownerlone` | the same, the owner trying the lone path against the stolen key | safety holds; the eviction is contested | **closes**, 11,914 states |
| `combined3_2stolen` | three keys, two stolen | the thief holds the count; the rule's own readings hold | **closes**, 71,122 states |
| `combined3_stale` | one stolen; a reader that follows stale proposals | a spent key's rows count for nothing | **closes**, 114,593 states |
| `unilateral3_stolen` | any member acts at once | the thief evicts an owner device | `Inv_ThiefCannotEvictHonest` violated |
| `quorum3_lost` | the count only; two lost | one of three is no majority: no recovery | `Prop_LostRecoverable` violated |
| `reverse3_stolen` | the lone path only; one stolen | a thief who signs is never evicted alone | `Prop_LostRecoverable` violated |
| `combined2_stolen` | two keys, one stolen | safety holds; one against one is a stalemate | `Prop_LostRecoverable` violated: the two-key bound |
| `combined4_2stolen` | four devices, two stolen | safety holds; two against two cannot recover | `Prop_LostRecoverable` violated: the bound |
| `combined1_stolen` | one key, stolen | the self is lost | `Inv_SelfSurvives` violated: the one-key bound |
| `combined3_absent` | one stolen; the owner signs nothing | an absent owner reads as lost | `Inv_ThiefCannotEvictHonest` violated: the stated cost |
| `combined3_mixed` | three keys, one stolen and one lost, one spare | the thief adds a key over the owner's one objection, and then holds the count | `Inv_ThiefNeverMajority` violated: the bound |

**The properties.**

| Property | Statement |
|---|---|
| `Inv_ThiefCannotEvictHonest` | no reader settles a thief's eviction of an owner-held key |
| `Inv_OwnerRowStopsThief` | a thief whose keys are no strict majority never has its eviction of an owner's key read as landed once that key has signed any row beyond the proposal's past; no other presence is assumed |
| `Inv_LoneNeedsSilence` | short of the count, no eviction is read as landed while its target has signed a row |
| `Inv_ThiefNeverMajority` | thief-held keys are never a strict majority while the owner holds one |
| `Inv_SelfSurvives` | the owner never holds no key |
| `Inv_SpentRowsCountNothing` | a row signed after its signer's seat was ended changes no outcome |
| `Inv_WithdrawalRefuses` | a withdrawn proposal that no approval made without the withdrawal carries is refused |
| `Prop_NothingChangesUnlessLanded` | the roster moves only by a proposal read as landed |
| `Prop_MetCountFinal` | a met approval is not unmade by any later row |
| `Prop_LostRecoverable` | once the owner acts, every lost and every stolen key leaves and the owner holds two keys again |

**Planted breaks.** Each is a change to the rule that a named property must catch.

| Plant | The change | Caught by |
|---|---|---|
| `plant_no_held_rule` | a held row may have the target's row in its past | `Inv_OwnerRowStopsThief` |
| `plant_owner_names_all` | the owner's row names every landing it holds, the one against its own key included | `Inv_OwnerRowStopsThief` |
| `plant_ended_counts` | a row of a key whose seat was ended counts wherever it is signed | `Inv_SpentRowsCountNothing` |
| `plant_wd_approval_counts` | an approval with the withdrawal in its past still approves | `Inv_WithdrawalRefuses` |
| `plant_settle_contested` | a reader takes a contested proposal as landed | `Prop_NothingChangesUnlessLanded` |

The planted reading that restores each node's own clock, and reaches the two nodes that differ for
good (`formal/derivation/order/witnesses.tsv` row C1), is in `formal/two_path` (`plant_node_clock`).

**Witnesses.** Each is the negation of a state the text names, and a run must report it violated.
The costs of the lone path are among them.

| Witness | What is reached |
|---|---|
| `Wit_LoneLandingNotFinal` | a proposal read as landed on its landing alone is not, one row later |
| `Wit_ConcluderChoosesInstants` | a thief's eviction of an owner's key read as landed on the thief's three rows and nothing else; no clock stood between them |
| `Wit_AbsentOwnerReadsLost` | with the owner signing nothing, a reader settles the thief's eviction |
| `Wit_OneKeyCannotEvictSigningThief` | the owner's one live key lands alone, the stolen key signs a row, and the proposal is contested |
| `Wit_AddOneObjection` | an addition stands with one objection of two others counted |
| `Wit_Open`, `Wit_Contested`, `Wit_LoneLanded`, `Wit_CountLanded`, `Wit_RefusedByCount`, `Wit_RefusedByWithdrawal` | the four outcomes, by each way of reaching them |
| `Wit_ApprovalBeatsWithdrawal`, `Wit_ApprovalAfterWithdrawal` | a withdrawn proposal read as landed on a met approval; an approval with the withdrawal in its past |
| `Wit_SpentKeySigns`, `Wit_BadHeldLanded`, `Wit_VoidLanding` | the rows that count for nothing are signed |

**A reading the runs show, for the text.** What stops a thief's lone eviction is a row of the
target that does not name the landing. A row that names the landing came after it and changes
nothing, so a device that holds a landing against its own key and names it in its next row
confirms its own eviction (`plant_owner_names_all`). The module's owner leaves such a landing
unnamed.

**What it does not model.** Data at rest and DEK re-wrap; the add-device join itself (CIRISServer
`formal/add_device`); a theft after the owner has started acting; two nodes and arrival order
(`formal/two_path/TwoPathRows.tla`); the head a row names and a fork of the roster
(`heads.py`, `formal/roster_fork`); a second landing; a landing reopened after a later proposal
stands on it.

Run: `TLA2TOOLS=/path/to/tla2tools.jar ./run.sh` (the three-key runs finish in seconds,
`combined4_mixed` in about five minutes at 4.5 GB of heap).

## Traces for implementers (`traces/`, `dump_traces.py`)

`python3 dump_traces.py <tla2tools.jar>` writes six behaviours as JSON (model variables per state plus
a derived `step`), for a roster reader to replay: `unilateral3_stolen` (**refuse** — the thief's
eviction settled on its word, which a conforming reader never does), `combined1_stolen` and
`combined2_stolen` (**bound** — the one-key loss and the two-key stalemate, the latter a lasso),
and `combined3_stolen`, `combined3_lost`, `combined4_mixed` (**land** — the shortest behaviour that spends
the whole adversary budget and still reaches `Recovered`, obtained by checking `Inv_NotRecovered` as an
invariant; every `Settle` in it reads `landed`). The files are generated from TLC
output and are regenerated whenever the module or a configuration changes.
