# `formal/audience_view` — what a reader of the mesh can decide, and what it cannot learn

A reader of the mesh holds a lossy view of it: the rows it is served. The general theory of lossy views says when a question can be answered from a view (it **factors** through it), when it cannot (a **witness pair**: two states the view cannot tell apart that differ on the question), and when a view keeps its own law of motion under a step (**Closed**) or is left as it was (**Held**). This model states that theory once, in plain Lean, and instantiates it with three audience rules of the text.

**The theory** (`AudienceView.lean`, Part 1). `Factors u v` is u = h ∘ v; `SeparatesFiber v d` is the witness pair; `factors_iff_not_separatesFiber` says a quantity factors exactly when no witness pair separates a fibre; `Closed v T` is v ∘ T factoring through v, `Held v T` is v ∘ T = v, and `closed_iff_fiber_invariant` says a view is Closed exactly when the step never splits a fibre. The names and statements are the view theory's own; [CORRESPONDENCE.md](CORRESPONDENCE.md) maps each to its source and records the mechanical check that they agree.

**The three rules.**

| Rule | State X | Reader's view | Step |
|---|---|---|---|
| The row's audience (CC 2.1, CC 5.2) | the rows held, newest first, over a fixed roster fold | the rows whose audience includes the reader, a reply carrying the row it answers | a row is admitted |
| The private room (CC 3.1.3.2) | the room's rows under room keys, and the bindings of room keys to persons | a member's node (rows and bindings), a holder of the rows without bindings, an outsider (nothing) | a row is spoken; a room key joins |
| The public roster and the served set (CC 3.2, CC 5.2, CC 5.4.6) | a public room's rows; what a responder holds | an outsider of a public room (the rows); a stranger (the served set) | the responder comes to hold one item |

| Theorem | What it says | Kind |
|---|---|---|
| `party_rows_decided`, `party_decisions_decided` | the rows a reader is party to under the audience rule, and every decision made from them, factor through the reader's view | decides |
| `outside_row_hidden` | a row outside the reader's audience does not factor: witness, the mesh without it and with it | hides |
| `admit_outside_is_held`, `admit_inside_is_closed`, `admit_is_closed` | admitting a row that names nothing: Held when outside the audience, Closed by that row when inside | closed / held |
| `reply_carries_to_joiner`, `carriage_not_closed`, `list_view_shows_arrival_order`, `carriage_closed_under_wait` | a reply carries the row it answers to a later joiner; over every state the joiner's view is not Closed under the reply (witness: without and with the answered row); a list view is not Closed even on causal states, since it records arrival order (witness: two orders of the same rows); the served set read without order (`Seen`) is Closed under admitting any row on every state the waiting rule allows (CC 2.7.3), for every world and reader | finding; closed |
| `standing_reads_rows` | whether a room key stands factors through the rows alone | decides |
| `member_decides_membership`, `member_decides_who_said`, `member_decides_count` | a member's node holding the bindings decides who is in the room, who said what and the count of persons | decides |
| `rows_hide_who_said`, `rows_hide_membership`, `person_count_needs_bindings` | the rows without the bindings do not: witness, the same rows with a room key bound to one person or another | hides |
| `outsider_hides_membership`, `outsider_hides_existence` | an outsider learns neither who is in the room nor that it has a row | hides |
| `outsider_held_speak`, `outsider_held_join`, `member_closed_speak`, `member_closed_join`, `rows_closed_join`, `rows_see_a_joining` | the outsider's view is Held under the room's steps, the member's and the rows view are Closed, and the rows view is not Held under a joining (the stated limit) | closed / held |
| `public_roster_decides_membership` | in a public room an outsider's view decides who is in it | decides |
| `stranger_decides_announced`, `stranger_decides_key_record` | a stranger decides whether a subject is announced at the responder and whether it holds a key's public record | decides |
| `stranger_never_learns_owned_route`, `_contacts`, `_scoped`, `_sealed_occurrence` | an owned node's route, a contact grant, a scoped row and an occurrence placed with a contact do not factor through the served set | hides |
| `literal_reading_serves_sealed_occurrence` | the served-set sentence read without the audience rule would serve the occurrence placed with a contact once the identity announces | finding |
| `stranger_closed_hold`, `stranger_held_private`, `stranger_not_closed_binding` | coming to hold anything but a binding is Closed, a private item Held; coming to hold a binding is not Closed (witness: without and with federation-scope testimony held before it) | closed / held; finding |

**What it does not model.** The roster fold itself (`membership/`) and a roster event as a step; the bindings' cryptography (`causal_kernel/check_roomkey.py`); the network observer, who sees which nodes receive a room's rows; that the list view and `Seen` agree on causal states, which is stated and not proved.

**Running.** `bash build.sh` compiles the file with `#print axioms` added for every theorem, refuses a `sorry` or an axiom beyond propext, Quot.sound and Classical.choice, and plants two breaks it must catch. The CI job `reciprocity` runs it.
