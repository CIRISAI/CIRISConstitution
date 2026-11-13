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
`Harden3.lean` (the rules added after the kernel was attacked), and `SeatG.lean`, `Terms.lean`, `Reader.lean`,
`Merge.lean` (the refined seat, the cut's terms, a reader's own line and a version naming several heads), and
`Consent.lean` (the one act beneath the seat), `Carry.lean` (a row leaves its room only by its own signer's act), `RosterHead.lean` (the members at the head a counted row names) `TwoMechanisms.lean` (claim and content carried by consent; the door and consent apart), `KeyEnd.lean` (a key's own end, read from its records and now) and `Duty.lean` (the duty seat of a community). Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.

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
| `Kernel.Consent.silent_voice_not_bound`, `unbound_rows_change_nothing`, `only_bound_voices_end` | a relation stands when every voice it binds has consented; nobody is bound by the rows of others, rows by an unbound voice change nothing, and only a bound voice's own withdrawal or a cut ends it |
| `Kernel.Consent.one_voice_one_row`, `two_voices_two_rows`, `seat_is_two_consents`, `holder_first_stands` | with one voice bound one row is enough; with two it is two rows, one naming the other, in either order; the seat conferred by one key is exactly that act with the conferrer's row first |
| `Kernel.Consent.count_needs_holder`, `one_voice_is_not_a_count`, `nonmember_rows_change_nothing`, `count_of_one_is_one_row` | where a body places a duty its consent is a count of its members' signatures on the row; the holder's own yes is still needed, one voice is never a count of two, non-members change nothing, and a body of one is the one-key case |
| `Kernel.Consent.count_is_final_against_members`, `only_holder_or_cut_ends`, `holder_still_ends_its_own` | a count once met is final against every later row, withdrawals included; a counted duty ends only by its holder's own withdrawal or a cut |
| `Kernel.RosterHead.membersAt_function`, `standing_final` | the members at a roster head are a function of the head, the signatures it carries and its past, and no concurrent or later row changes them |
| `Kernel.RosterHead.counted_over_named_head`, `rows_outside_change_nothing` | whether a version stands is decided by the members at the heads it names and the signatures on it, and rows outside its past change nothing |
| `Kernel.RosterHead.no_self_admission`, `outsiders_admit_nothing` | a key that is not a member at the heads a version names gives no voice to its count, and keys outside the roster admit nobody however much they sign |
| `Kernel.RosterHead.removed_voice_does_not_count`, `readmission_needed` | a key a version leaves out is no voice of a version naming it, and further down the line is a member only if a version counted without it lists it again |
| `Kernel.RosterHead.leaving_binds_by_past`, `left_head` | a member's own leaving is a fact for the rows that have it in their past and for no others, as a removal is |
| `Kernel.RosterHead.Retro.retro_agrees`, `Retro.Model.retro_reaches_back` | the rejected reading through every held withdrawal agrees where each leaving is in the version's past, and otherwise lets a later leaving change the members at an older head |
| `Kernel.RosterHead.old_head_still_counts` | by definition, a key that is a member at an older head is a voice of a version naming only that head |
| `Kernel.RosterHead.one_signature_never_removes`, `one_key_alone_stands_nothing` | where the count asks two or more, a member leaves a standing version only by its own withdrawal or by the signatures of two distinct members |
| `Kernel.RosterHead.voters_is_common` | a version naming several heads is counted over the members common to them, which is the common list of `Merge.lean` |
| `Kernel.RosterHead.Rejected.Model.later_withdrawal_changes_members`, `head_withdrawal_ends_version` | under the rejected rule of withdrawable votes, one later withdrawal removes every member at a head and ends a version naming it |
| `Kernel.TwoMechanisms.edge_is_one_voice_consent`, `claim_is_one_voice_consent` | an edge of the meaning walk is a relation binding one voice, so what a row means to a reader is a bounded walk of one-voice consents from the reader's key |
| `Kernel.TwoMechanisms.claim_lost_only_by_walk_voice` | a row loses its meaning for a reader only through a withdrawal signed by a key on that reader's walk |
| `Kernel.TwoMechanisms.content_holders_are_consents`, `content_audience_function`, `content_audience_final` | with each row's own audience a roster's members, everyone or one key, who may hold a row is read off roster heads, their pasts and naming rows alone |
| `Kernel.TwoMechanisms.door_not_function_of_rows` | a window the reader closes on its own clock, with no answer held, is open at one instant and closed at a later one over the same rows |
| `Kernel.TwoMechanisms.SeatModel.consent_not_door`, `offer_alone_never_stands` | whatever answers a window an offer opens, its outcome at every instant does not say whether the seat stands, and an offer alone stands at no instant |
| `Kernel.Carry.nothing_leaves`, `others_elsewhere_change_nothing`, `author_carries`, `same_room_unchanged` | a naming row carries only from the same room or under the named row's own signer; then no key outside a room's own audiences is in the audience of its rows unless an author carried a row of its own out, rows by others elsewhere change no audience, and inside one room the rule is the earlier one |
| `KeyEnd.bound_reads_row`, `live_perm`, `live_mono` | a key record's bound is a function of the record alone; whether a key is live does not depend on the order its records are held in; a further record never ends a live key |
| `KeyEnd.live_own_rows`, `live_le_ceiling` | records of other keys change nothing, and a live key is within the ceiling of the instant of some record it signed |
| `KeyEnd.ended_not_live`, `ended_stays_ended` | with the same records, a key ended at an instant is live at no later instant |
| `Kernel.offer_withdrawal_ends`, `acceptance_withdrawal_ends`, `third_key_cannot_end`, `only_withdrawals_and_cuts_end` | either side ends a seat alone by its own withdrawal; no third key ends it without a cut |
| `Kernel.stands_function`, `stands_mono`, `means_is_seat_walk` | standing is a bounded walk of live seats and a function of the set; it grows with offers and acceptances and shrinks only with withdrawals and cuts; what a row means to a reader is that walk from the reader's own key |
| `Kernel.cut_status_function`, `unique_when_uncontested`, `two_cuts_contested`, `winner_counts` | each cut counts, is void or is contested, as the least solution of its equations; two concurrent cuts that undo each other are both contested, and a row naming both settles it |
| `Kernel.outsider_changes_no_cut`, `outsider_row_never_counts` | a row by a key with no entitlement on a slot changes no cut and never counts on it |
| `Kernel.cannot_land_inside`, `ruleI_only_concluder_undoes`, `ruleII_never_final` | a window's landing cannot stand over an objection its signer acknowledged; under the rule taken only the concluder's own key undoes a landing; under the other rule any objector reopens any landing for ever |
| `Kernel.Recount.dishonest_never_stands`, `stands_is_table_over_all_not_late`, `unnamed_gains_nothing` | under recount a landing that states an outcome its own past does not give never stands, and a landing stands only if it states the table's outcome over every answer that does not name it |
| `Kernel.Recount.undone_only_by_counted_answer`, `naming_answer_changes_nothing`, `count_door_final`, `quorum_closed_final` | only a newly counted concurrent answer that moves the table undoes a landing; an answer naming the landing changes nothing; a landing with a strict majority behind it is final, against every key but one that has answered both ways (`quorum_closed_final` assumes no key of the roster answered both ways) |
| `Kernel.Harden.F1.ended_keys_change_nothing`, `F2.rival_cannot_move` | rows by a key whose seat was ended, unseen by the ending, neither unseat nor rescue a landing; a landing that does not stand moves no outcome |
| `Kernel.Harden.F3.no_replay`, `F4.proposer_cannot_end` | a cosignature in the past of a head is no voice for a row counted over that head; the proposer of a counted offer does not end it alone |
| `Kernel.Harden.F5.no_single_founder_removes`, `removed_cannot_reseat`, `no_row_restores_a_founder` | among several founders one removes no other, and a removed founder seats itself again by no row; over founding seats, once every founder has withdrawn no later row restores one; `Duty.lean` states each against the community law |
| `Kernel.Duty.lone_holder_confers`, `lone_count_is_own` | with one duty holder at the head a row names, that holder's signature and the new holder's yes seat, and no other key's signature is a voice |
| `Kernel.Duty.one_of_several_confers_nothing`, `one_of_several_rows` | with two or more duty holders, a row carrying one holder's signature alone seats nobody, and so does any number of such rows |
| `Kernel.Duty.majority_confers`, `confers_only_by_majority` | a duty seat stands exactly when more than half the holders at the head have signed the row and the new holder has said yes |
| `Kernel.Duty.withdrawal_needs_two_others`, `two_holders_neither_unseats`, `lone_holder_not_unseated` | a withdrawal counts exactly on more than half of the other holders and at least two of them; of two holders neither unseats the other, and no holder unseats a lone one |
| `Kernel.Duty.conferrer_cannot_end`, `conferrer_cannot_lower_count` | once a duty seat stands, a withdrawal signed by any key but its holder, a conferrer's included, ends nothing |
| `Kernel.Duty.equals_perm`, `equals_rename` | every duty count reads the holders as a set: the answer is the same whatever order they were seated in, and under any renaming of keys |
| `Kernel.Duty.removal_ends_duty`, `removed_confers_nothing`, `removal_cuts_duty` | a key a standing roster version leaves out holds no duty at that version or below it until it is listed again, its signatures confer nothing there, and the removal ends each conferral of its seat in its past |
| `Kernel.Duty.none_left_members_seat`, `holders_left_members_do_not`, `one_member_seats_nothing` | with no duty holder at the head a row names, only the members' count confers a duty seat; while a holder remains, only the holders' count does |
| `Kernel.Duty.Rejected.three_holders_lone_grant`, `lone_grant_outlives_conferrer`, `members_restore` | three readings of F5 the community law rejects: one of three holders' own grant seats nobody, a lone holder's grant outlives its conferrer's withdrawal, and the members' count seats a holder when none is left |
| `Kernel.Harden.F6.rows_of_one_key`, `no_self_service`, `member_can_widen` | a key enters a row's audience by no rows of its own; a key already inside widens it by one concluded naming row |
| `Kernel.Harden.F7.backdated_conferral_seats_no_one` | while two tips wait a seat with no offer under one of them is not held |
| `Kernel.Harden.CP.checkpoint_voids_any_answer`, `without_checkpoint_fixed` | under the rejected rule: were a counted row to leave older acts behind, two counted rows would void any answer in a window; without that rule nothing later changes whether a concluded answer is counted |
| `Kernel.Reader.line_voids_old_fork`, `old_fork_void_for_ever`, `sibling_waits`, `merge_accepted` | over the cut alone, a reader's acknowledged line voids, for that reader, any line from below it however long; a sibling on the same head waits; a row naming the acknowledged head is judged like any other |
| `Kernel.Reader.built_on_void`, `line_void`, `no_line_is_plain`, `rd_unique` | a counted row counts for a reader only if every counted row it is built on does, down the whole line; a reader with no acknowledgement has the cut and that clause and nothing that ranks lines; the answer is unique |
| `Kernel.Reader.depth_race`, `race_one_way` | were a counted row to leave older acts behind, of two lines from one head the deeper would leave the other behind, and never the reverse |
| `Kernel.Terms.entK_anti`, `entK_single`, `iter_bound`, `cut_iter_bound` | the cut's terms as the running kernel gives them (what clashes, what overrules, a tally of live seated voices at the head named) meet what the general theorems ask; the iteration reaches what counts within one round for each concluded cut |
| `Kernel.Terms.outsider_changes_no_cutK`, `outsider_row_never_countsK` | a row none of whose voices is by a key seated to it at the head it names changes no cut; where the conclusion rule asks a seat of the signer, its row on the slot never counts |
| `Kernel.Terms.removal_voids_row`, `removals_agree`, `mutual_removal_contested`, `deciders_clash`, `two_deciders_contested`, `decider_voids_named` | a removal voids its key's concurrent rows; two removals of one key agree; two that remove each other's signers are contested; deciders that pick differently are contested, and a decider voids the claims it names |
| `Kernel.SeatG.standsG_mono`, `standsG_eq_stands`, `seatedG_eq_seated`, `Witness.unshared_not_equal` | the refined walk grows with offers and acceptances and shrinks with withdrawals and cuts; it is the walk of `Seat.lean` exactly where no offer is shared and no holder withdraws against an offer it did not sign, and not otherwise |
| `Kernel.SeatG.count_not_sole`, `only_withdrawals_and_cuts_endG`, `third_key_cannot_endG` | a count of two or more has a voice that is not the proposer's; the two-voice floor and the rules of ending hold for the refined walk |
| `Kernel.Merge.merge_counted_one_tip`, `common_is_waiting_roster`, `merges_share_signer` | a version naming several heads is counted over the members common to them, which is the roster while they wait; a merge of every tip is the one tip with the roster it states; two merges of one set of heads counted by strict majorities share a signer |
| `Kernel.Merge.merge_on_void_tip_void`, `merge_counts` | a merge naming a tip that does not count for the reader is void, and one whose tips all count counts |
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
- A theorem named `…_function` says that an answer depends only on the set it is defined over, which follows
  from its definition. The content is elsewhere: `door_perm`, `adm_perm`, `close_saturated`, `conclOf_unique` and
  the theorems that say which rows can change an answer.
- A reader's line is applied over the cut, as the running kernel applies it: an act left behind by a reader's
  line still voids, inside the cut, what it clashes with. `Reader.lean` proves that form. `Harden3.lean` still
  holds an earlier form with the line inside the cut's operator and the rejected rule beside it; those theorems
  are superseded, and the two forms are not proved equal.
- The rules of `Harden` are proved over the definitions of the earlier files. The form of the kernel each
  attack succeeded against is a reconstruction, not an earlier version of the code.
- The refined seat equals the seat of `Seat.lean` only where no offer is shared and no holder withdraws against
  an offer it did not sign (`SeatG.standsG_eq_stands`). Otherwise the two are different rules
  (`Witness.unshared_not_equal`). The mark of a shared offer is derived for a count of two or more; for a count
  of one it is a rule.
- A cosignature that names two heads is a voice at both. What is proved is that one naming a single head is a
  voice at that head only.
- Under recount a lone landing is final only against keys whose answers cannot move the count. A key whose
  answer would move it can unseat the landing at any later time by leaving it unnamed
  (`unnamed_answer_unseats`). Which of two standing landings wins is not modelled.
- The cut's terms are transcribed for a removal and for a deciding row (`Terms.lean`). Finality against an
  outsider assumes that the conclusion rule refuses a row on a slot by a key with no seat at its head, and it
  concerns voices, not the signer: a cut carried by an outsider with enough seated cosignatures is entitled.
  The instances are proved for two cuts that are the only concluded cuts.
- A voice counted by a group is a signature on the row and is not withdrawn. A member who changes its mind signs a
  new counted act, or answers through a window under recount. A version naming several heads is counted over the
  members common to them (`Merge.lean`, `RosterHead.voters_is_common`).
- Concurrent versions of one head are not decided in `RosterHead.lean`; they wait as tips (`Window.lean`, `Merge.lean`).
- A conclusion from silence, such as a window closing unopposed, cannot be drawn from rows and is not here.
- The walk has one depth for all edges; the classes and budgets of `formal/trust_set` are not carried over.
- The rule tables are not read. `formal/derivation/order/` holds the measure of the tables against this form:
  seventeen cases run through the guard cells in every arrival order, and each family's verdict.

Run: `bash formal/causal_order/build.sh`. It compiles the eighteen files in order and exits on a compile error,
a `sorry`, or an axiom beyond the three of core Lean.
