# `formal/moderator_election` — a locked room chooses by ranked choice of three

**The rule (CC 4.5.13, rc17).** A community with no live holder of `moderate` is read-only until a 24 h ranked-choice vote over its own roster seats one. The ballot is the roster in worthiness order (track record, then admission order, then key); each person ranks up to three; one ballot per person; the count is instant-runoff and order-free; the winner accepts by their own row or the duty passes to the next in runoff order; a steward may appoint directly at any time and end the vote. The voters' rows are the appointment's signatures, so no node signs anything.

**The model** (`Election.lean`, Lean 4 core, no Mathlib). `dedupe` is the fold to one ballot per person; `runoff` eliminates the weakest standing candidate (ties broken against the later in worthiness order); `winner` the result; `seat` the acceptance chain.

**Proved.** `winner_in_roster`: a winner is a member. `dedupe_unique`: one ballot per person after the fold. `votesFor_perm`: the count of a candidate is a function of the multiset of ballots, not their order. `seated_accepted`, `seated_in_order`, `decliner_never_seated`: the acceptance chain seats the first in runoff order who accepts and never one who declined. `no_ballots_no_winner`: a room where nobody votes stays locked. Worked examples by `decide`: a transfer from an eliminated third candidate decides the vote; a person's second ballot changes nothing; a declining winner passes the duty to the next.

**What it does not model.** The 24 h clock (per node, first held, as every window), the steward's direct appointment, and the worthiness order's inputs; the model takes the order as given.

**Run.** `lean -M 6000 -T 200000 Election.lean` (exit 0, no `sorry`).

**Not modelled.** An election declares no order, so a tie there seats nobody and the count runs again (CC 4.5.13). The tie rule in this model is the general count's, which goes against the option later in a declared order.
