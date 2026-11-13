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

A removal by others reaches the rows of the removed signer that are not in its past. A row is in the past of
a removal when a chain of rows leads from the removal back to it: an acknowledgement, a census, a roster
version, a reply. No instant is compared.

**What is proved.** `Order.lean` (the rank case and the failure of judging on arrival), `Causal.lean` (no
rank), `Seat.lean` (standing as one shape, and the cut), `Window.lean` (a window's signed outcome under two rules,
and the roster's tips), `Recount.lean` (the window's rule as taken) and `Harden.lean`, `Harden2.lean`,
`Harden3.lean` (the rules added after the kernel was attacked). Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.

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
| `Kernel.no_offer_no_seat`, `no_acceptance_no_seat`, `one_row_only_to_self` | a seat needs two voices, the conferrer's offer and the holder's acceptance; one row is both voices only when a key seats itself |
| `Kernel.offer_withdrawal_ends`, `acceptance_withdrawal_ends`, `third_key_cannot_end`, `only_withdrawals_and_cuts_end` | either side ends a seat alone by its own withdrawal; no third key ends it without a cut |
| `Kernel.stands_function`, `stands_mono`, `means_is_seat_walk` | standing is a bounded walk of live seats and a function of the set; it grows with offers and acceptances and shrinks only with withdrawals and cuts; what a row means to a reader is that walk from the reader's own key |
| `Kernel.cut_status_function`, `unique_when_uncontested`, `two_cuts_contested`, `winner_counts` | each cut counts, is void or is contested, as the least solution of its equations; two concurrent cuts that undo each other are both contested, and a row naming both settles it |
| `Kernel.outsider_changes_no_cut`, `outsider_row_never_counts` | a row by a key with no entitlement on a slot changes no cut and never counts on it |
| `Kernel.cannot_land_inside`, `ruleI_only_concluder_undoes`, `ruleII_never_final` | a window's landing cannot stand over an objection its signer acknowledged; under the rule taken only the concluder's own key undoes a landing; under the other rule any objector reopens any landing for ever |
| `Kernel.Recount.dishonest_never_stands`, `stands_is_table_over_all_not_late`, `unnamed_gains_nothing` | under recount a landing that states an outcome its own past does not give never stands, and a landing stands only if it states the table's outcome over every answer that does not name it |
| `Kernel.Recount.undone_only_by_counted_answer`, `naming_answer_changes_nothing`, `count_door_final`, `quorum_closed_final` | only a newly counted concurrent answer that moves the table undoes a landing; an answer naming the landing changes nothing; a landing with a strict majority behind it is final |
| `Kernel.Harden.F1.ended_keys_change_nothing`, `F2.rival_cannot_move` | rows by a key whose seat was ended, unseen by the ending, neither unseat nor rescue a landing; a landing that does not stand moves no outcome |
| `Kernel.Harden.F3.no_replay`, `F4.proposer_cannot_end` | a cosignature in the past of a head is no voice for a row counted over that head; the proposer of a counted offer does not end it alone |
| `Kernel.Harden.F5.no_single_founder_removes`, `removed_cannot_reseat`, `no_row_restores_a_founder` | among several founders one removes no other; a removed founder seats itself again by no row; and once every founder has withdrawn, no later row restores one |
| `Kernel.Harden.F6.rows_of_one_key`, `no_self_service`, `member_can_widen` | a key enters a row's audience by no rows of its own; a key already inside widens it by one concluded naming row |
| `Kernel.Harden.F7.backdated_conferral_seats_no_one`, `CP.old_fork_void_for_ever`, `CP.built_on_void_for_reader` | while two tips wait a seat with no offer under one of them is not held; a line from below a reader's acknowledged head is void for that reader, row by row |
| `Kernel.Harden.CP.checkpoint_voids_any_answer`, `without_checkpoint_fixed` | were a counted row to leave older acts behind, two counted rows would void any answer in a window; without that rule nothing later changes whether a concluded answer is counted |
| `Kernel.rosterOf_function`, `merge_one_tip`, `fork_shares_signer` | with several tips the roster is the members common to them; a version naming every tip makes one tip; two versions of one head each counted by a strict majority share a signer |
| `Causal.wins_unique`, `higher_kind_decides`, `same_kind_both_or_neither` | concurrent rows on one target that differ in kind are decided by a fixed order on kinds; rows of one kind are still both or neither |
| `Causal.counts_function`, `only_removals_stop_counting` | a row of a removed signer counts when it lies in the past of the removal; that is a function of the offered set, and only a removal of its signer can stop a row counting |
| `Causal.sign_after_removal_never_counts`, `Removal.acknowledged_counts`, `Removal.honest_but_unnamed` | a row first held after the removal is kept never counts; a row the removal's past had named counts, and one it had not named does not |

**What it assumes.** The naming relation is well-founded: a digest cannot name a row that names it back.
An edge is withdrawn only by its own signer.

**What it does not show.**

- A removal that extends an older head leaves more rows out of its past (`Removal.stale_head_voids_more`).
  The roster chain's rule for two versions of one head must bound that, and that rule is not modelled.
- Re-admission of a removed key and a contested removal are not modelled.
- The same reach for a retirement, a revocation or a withdrawn grant is the same rule under another name,
  and is proved here only for a removal.
- A contested slot may stay empty; nothing here ends a dispute.
- A window's length is not in the rows. No theorem says a landing came late enough.
- The rules of `Harden` are proved over the definitions of the earlier files. The form of the kernel each
  attack succeeded against is a reconstruction, not an earlier version of the code. The refined seat that
  carries the founders' rule is not proved equal to the seat of `Seat.lean`.
- A cosignature that names two heads is a voice at both. What is proved is that one naming a single head is a
  voice at that head only.
- Under recount a lone landing is final only against keys whose answers cannot move the count. A key whose
  answer would move it can unseat the landing at any later time by leaving it unnamed
  (`unnamed_answer_unseats`). Which of two standing landings wins is not modelled.
- The cut's three terms, what clashes, what overrules and who is entitled, are parameters here. Their values for
  each slot are in `formal/causal_kernel` and are not transcribed.
- A voice counted by a group cannot be withdrawn in this model, and a version naming several heads is counted
  over one.
- A conclusion from silence, such as a window closing unopposed, cannot be drawn from rows and is not here.
- The walk has one depth for all edges; the classes and budgets of `formal/trust_set` are not carried over.
- The rule tables are not read. `formal/derivation/order/` holds the measure of the tables against this form:
  seventeen cases run through the guard cells in every arrival order, and each family's verdict.

Run, in this order, each with `LEAN_PATH="$TMP" lean -o "$TMP/NAME.olean" NAME.lean`: `Order`, `Causal`, `Seat`, `Window`, `Recount`, `Harden`, `Harden2`, `Harden3`
