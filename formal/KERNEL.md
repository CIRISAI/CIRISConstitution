# The kernel

One function. A node gives it the rows it holds or has been offered, the present instant and its own key. It
returns what every row means to this node, what the node may do, what it owes, and what to copy to whom.
Everything else a node does is storage, transport or presentation.

This page is the specification an implementation builds to. Each statement is marked:
**proved** (Lean, `formal/causal_order`), **run** (executed over every case to a bound, `formal/causal_kernel`,
`formal/roster_fork`, `formal/kernel_lib`), **measured** (counted from the rule tables or the reported decision
sites, `formal/derivation`), or **open**.

## 1. Inputs

| Input | What it is |
|---|---|
| rows | the signed rows the node holds or has been offered, each with the instant the node first saw it |
| now | the node's own clock |
| own key | the key the node signs under |

There is no trust set among the inputs. Who a node trusts is a fold over the rows its own key signed
(CC 4.4.3.8). **proved**: `Causal.means_function`, `two_readers`, `no_own_edge_no_reach`.

Config is not an input. A value that binds others is a row signed by whoever decided it. A value that binds
only the node is a row under the node's own key. **measured**: 174 decision sites on the kernel's side read
config today. **open**: the constants are not yet all in `constitution/constants.tsv`.

## 2. The only order is what rows name

A row names other rows by digest: the row it answers, the head it extends, the proposal it votes on. That
relation is well-founded, since a digest cannot name a row that names it back. There is no sequencer, no
ranking by signed instant and no ranking by digest.

Two rows where neither names the other, directly or through others, are **concurrent**.

Judging each row as it arrives, against what was admitted so far, is not a function of the rows.
**proved**: `Order.Two.arrival_not_a_function`. **run**: seventeen cases from the rule tables each give two
results from one set (`formal/derivation/order/witnesses.tsv`).

## 3. Three layers

| Layer | Reads | Property |
|---|---|---|
| **kept** | the row alone, and whether the rows it names are kept | the least set closed under the door; the same in every arrival order; a row waits for what it names and is never refused for another row |
| **concluded** | the row against its ancestors | one solution, negation and counts allowed; final once the row is kept |
| **derived** | conclusions over a set of rows | a function of the kept set, the node's key and, in one place, now |

**proved**: `kept_is_least`, `door_any_order`, `concl_function`, `concl_final`, `concl_new_row`.
**run**: 6,606 sets of up to six rows in 2,182,671 arrival orders, one answer each.

Only the first two layers are final. A derived answer can be changed by a later row, and only by a row whose
signer has standing on that answer's slot. **run**: after a counting cut, no other key changed a slot.

## 4. Operators

Every rule cell is written in these. **measured**: 205 of 211 fold-cell parts, all 43 guard clauses and the 39
clock and expiry entries map onto them. **run**: six models rewritten with the first five agree with their
originals on 400,300 comparisons.

| Operator | What it does |
|---|---|
| select | rows matching a pattern on their fields |
| group and reduce | the least, the greatest, the one distinct value, the count of distinct values, or the sum; a tie between two different rows is refused, never broken by position |
| interval | whether a value lies between an opening and a closing |
| table cell | the value a typed table gives for a key |
| bounded repeat | a step applied until nothing changes |
| closure over what rows name | ancestors, concurrency, the frontier of a set |

All six are in `formal/kernel_lib`. **run**: the closure agrees with a hand-written definition on 15,864 comparisons.

## 5. Named answers

Eight. Each is a composition of the operators, and each role, window, policy and constant is data.

| Answer | Question | Layer |
|---|---|---|
| **state** | is this row live: admitted, withdrawn, recanted, superseded | concluded, with the order on kinds |
| **stands** | does this key hold this relation over this object | derived: a bounded walk of live edges |
| **tally** | is this count met, over the head it names | derived |
| **may** | may this key do this act on this target; if not, which row is missing and who could sign it | derived |
| **audience** | who is this row for | concluded |
| **missing** | which rows does this conclusion depend on that are not held | kept |
| **owed** | what must this node now emit or do | derived |
| **window** | has this window closed, and with what outcome | derived; the one answer that reads now |

**stands.** One shape, the **seat**. A key holds a seat in a scope over an object when a conferrer's offer
names it and the key's own acceptance names that offer, and neither has been withdrawn by its own signer, and
no cut removes it. Two voices: neither side alone makes a seat, either side alone ends it, and no third key
ends it without a cut. One row is both voices only when a key seats itself. The conferrer is one parameter with
three values: the object's own key, a key holding a seat that may confer, or a group whose count is met. A key
stands when a bounded walk of live seats leads to it from a root. For what a row means to this node the root is
the node's own key. **proved**: `no_offer_no_seat`, `no_acceptance_no_seat`, `third_key_cannot_end`,
`stands_function`, `means_is_seat_walk`. **run**: 2,727 sets in 587,536 arrival orders.

The 23 role names of the tables are not 23 things. **run** (`formal/causal_kernel/role_shapes.tsv`): the seat
covers 18 of them, three are read off the row judged (`author`, `self`, `subject`), `winner` is a tally, and
`tally` fits none because its holders are drawn from a group secret that is not a row. Appointed `moderate`,
`review`, `slash` and `takedown` are one seat with four scopes. `owner` and the steward of an agent are one
seat. `member`, an accord holder and a key of a self roster are one counted seat over three objects. `serve` is
two seats required together, which is a question for **may**.
**open**: in 14 of 17 partly fitting rows the text states the conferral and no acceptance row. The `confers`
and `binds_segment` columns are still empty.

**may.** The door, the control a person is offered and the gate on serving a row are one answer
(`manifests/transitions.json` states it so). A refusal is a named missing row. **open**: guards are typed on 26
of 459 transitions, and "receive" is not yet a verb of the table.

**missing and copying.** A row moves to a peer because that peer must conclude something and lacks it. What
to send is what lies among the ancestors of what the peer must conclude, within the row's audience. This is
the closure a store already computes for its own retention, evaluated for the other party. **run** (`formal/causal_kernel/route.py`): a
party given only its routed rows concludes the same as a party given everything, and a stranger is routed
nothing. That holds only with one rule added: a row's audience includes the audience of every row that names
it. Without it a joiner can never keep its own admission. With it, a reply carries the message it answers to a
later joiner. **open**: whether that carriage is wanted; the placement cell is empty for 156 of 184 families and
no cell states the copy rule.

**window.** A row opens a clock. An answering row closes it, or time does, and the table states the outcome at
the close. A window names its opener and the acknowledgement by which the concluding party first held it. The
concluder signs the outcome as a landing row naming that acknowledgement and its own head. **measured**: 19
clock entries have this shape, 16 of them counted from receipt. The other 20 are a row stating its own end,
read from the row alone against now.

A landing that states an outcome its own past does not give concludes nothing. An answer concurrent with the
landing is **recounted**: it is counted with the landing's past, and the landing stands only if the table still
gives the outcome it stated. **run** (`formal/causal_kernel/window_adversary.tsv`): against the three windows
of the text, twenty checks of what each exists to prevent. Recount breaks none. A landing that voids concurrent
answers breaks seven, a thief evicting alone among them. An answer that contests any landing breaks two.
**proved** for the two rejected rules only (`ruleI_concluder_decides`, `ruleII_never_final`); recount is
**open** in Lean. What recount costs: a lone landing is never final against a key that can still sign, and the
window's length is the concluder's own word.

## 6. Conflict between concurrent rows

1. **Different kinds on one target** are decided by a fixed order on kinds. **proved**: `wins_unique`.
2. **The same kind on one slot**: both or neither. No rule that cannot tell two rows apart can pick one.
   **proved**: `holder_both_or_neither`.
3. **A row that names both may decide.** **proved**: `Slot.descendant_decides`.
4. **The cut.** A row on a slot by whoever may conclude it. Once it counts, rows on that slot concurrent with
   it do not count; rows in its past stand; rows that name it are judged at the head they name. A removal is a
   cut on a key and a deciding row is a cut on a contest. **run**: 4,898 sets in 440,291 orders.
5. **Equal standing.** Two cuts by keys of equal standing that undo each other stay contested. What settles it
   is a voice the other cannot remove. So no slot that matters is held on one signature. **run**.

A row of a removed key counts when the removal has it among its ancestors: something the removal can see had
already named it. **proved**: `counts_function`, `sign_after_removal_never_counts`.

## 7. The roster is the one ledger

A group's roster is a lineage: each version names the heads it extends and is counted over their members.
Every other row takes its place from the roster head it names. Nothing else is ordered.

Two versions of one head wait. The roster is then the members common to all tips, until a version naming the
tips makes one head again. **run**: over every set of versions an adversary below the count can cause, under
eight counting protocols, the roster is a function of the set, no removed key is listed, and a removal naming
an old head gains nothing.

An adversary holding the count of an old head signs a valid version alone. A witnessed lineage answers that
(CC 3.2 T6), and it is each reader's own trust that decides whose witnesses count.

**open, on the wire**: a roster version names one head today and must be able to name several.

## 7a. A writer's keys are a fold

Who is entitled to a wrap of which key is seats and cuts. The epoch is the count of the writer's mint rows, and
a rotation is due when a holder of the current key is no longer entitled. None of the writer's state resists
being a fold over its own rows, on one condition: each write and each mint names the head of the membership
rows the writer held. **run** (`formal/causal_kernel/keyplane.py`): 402,950 comparisons with
`formal/key_plane`, none differ. It also found that a re-admitted member's second live device is not wrapped at
the seat.

## 8. What the kernel does not give

- **No finality across readers.** Two nodes with the same rows conclude the same. A settled slot can be
  reopened by a key with standing on it. Finality is each reader's, from what it has itself acknowledged.
- **No conclusion from silence without a clock.** A window closing unopposed, and the lapse of an unconfirmed
  halt, are read on the node's own clock. Nodes may differ while a window is open.
- **No decision that is not a function of rows.** Link and load decisions, retries, rendering and the prose
  rules given to a model stay outside.

## 9. What stands between this and a build

| Item | Kind | Where |
|---|---|---|
| Which rows seat which key in which role: `confers`, `binds_segment`, the 23 roles as one walk | table data | `manifests/family_model.json` |
| Twelve guards that refuse a row for another row become folds | table data | `manifests/transitions.json` |
| "Counted at decision" has no solution and leaves the policy table | table data | `manifests/governance_policy.json` |
| A roster version naming several heads | wire | the store's to shape |
| Whether one acknowledgement of a head covers everything beneath it | wire | the store's to shape |
| Placement and the copy rule as the `missing` answer | table data, with transport | `manifests/family_model.json` |
| A landing row for each window, and who may sign it | table data | `manifests/reactions.json` |
| Constants out of config | table data | `constitution/constants.tsv` |
| An acceptance row for each seat the text confers without one | rule | the Parts |
| Recount proved, and the cut's terms for each slot transcribed into the proof | proof | `formal/causal_order` |
| The signer gate written over the library | code | `tools/check_signer_gate.py` |
