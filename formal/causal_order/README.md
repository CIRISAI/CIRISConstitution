# `formal/causal_order` — what a node concludes is a function of the rows it holds, with no rank

**The question.** Two nodes are offered the same signed rows in different orders. Do they conclude the same?
A node that judges each row as it arrives, against what it has admitted so far, does not. The question is what
rule makes the answer yes without a sequencer, a shared clock or a ranking by signed instant.

**The answer.** Three layers over the rows a node was offered.

| Layer | Reads | Property |
|---|---|---|
| kept | the row alone, and whether the rows it names are kept | the least set closed under the door; the same for every arrival order |
| concluded | the row against its ancestors, the rows it names and theirs | the only solution of its equation, negation and counts allowed; final once the row is kept |
| derived | conclusions over a set of rows: a slot, a count, a conflict, what a row means to this reader | a function of the kept set and the reader's own key |

A row names the rows it extends or answers by digest. That is the only order. Two rows where neither names
the other are concurrent, and a rule that treats them alike names both or neither. A row that names both
may decide between them.

Every reader is its own seed. A row means something to a reader when it is concluded and a bounded walk of
live edges from the reader's own rows reaches its signer. Meaning is lost only through a withdrawal, by its
own signer, of an edge on that walk.

**What is proved.** `Order.lean` (the rank case and the failure of judging on arrival) and `Causal.lean`
(no rank). Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.

| Theorem | What it says |
|---|---|
| `Order.Two.arrival_not_a_function`, `Order.Roster.standing_arrival` | judging on arrival gives two results from one set; on a roster of eight rows, three results from three orders, and in one a removed member keeps standing |
| `Order.adm_unique`, `Order.adm_perm` | with a rank that is a property of the row, any rule has one solution and it is the same for every order |
| `Order.no_symmetric_choice` | no kernel that treats two rows alike admits exactly one of them |
| `Causal.kept_is_least`, `door_any_order`, `close_saturated`, `door_spec` | the kept set is the least set closed under the door; any order with waiting ends at it; on a finite list the door stops within one step for each row |
| `Causal.concl_function`, `conclOf_unique` | the conclusion is a function of the kept set and the only solution of its equation |
| `Causal.concl_final`, `concl_new_row` | a rule that reads no concurrent row never changes a kept row's conclusion; a new row reaches only itself, its descendants, and rows in concurrent conflict with those |
| `Causal.holder_both_or_neither`, `Slot.descendant_decides`, `Slot.two_decisions_empty` | a contested slot is empty under a symmetric rule; a row naming both claims decides it; a second, concurrent decision empties it again |
| `Causal.means_function`, `two_readers`, `no_own_edge_no_reach` | meaning is a function of the offered set and the reader's key; two readers differ only through rows of their own; a reader with no edge of its own reaches only itself |
| `Causal.acceptance_gives_meaning`, `only_withdrawals_remove` | the reader's later acceptance gives meaning to rows already kept; no row but a withdrawal removes meaning from any row for any reader |
| `Causal.reaches_standing_irrelevant` | with an edge withdrawn only by its own signer, reach never depends on reach through negation |

**What it assumes.** The naming relation is well-founded: a digest cannot name a row that names it back.
An edge is withdrawn only by its own signer.

**What it does not show.**

- A signer who names old rows is concurrent with everything since. Bounding the age of what a row names is
  not modelled.
- A contested slot may stay empty; nothing here ends a dispute.
- A conclusion from silence, such as a window closing unopposed, cannot be drawn from rows and is not here.
- The walk has one depth for all edges; the classes and budgets of `formal/trust_set` are not carried over.
- The rule tables are not read. `formal/derivation/order/` holds the measure of the tables against this form:
  seventeen cases run through the guard cells in every arrival order, and each family's verdict.

Run: `lean -o "$TMP/Order.olean" Order.lean && LEAN_PATH="$TMP" lean Causal.lean`
