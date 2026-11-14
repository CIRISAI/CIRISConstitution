# `formal/moderator_election` — a locked room chooses by ranked choice of three

**The rule (CC 4.5.13).** A community with no live holder of `moderate` is read-only until a 24 h ranked-choice vote over its own roster seats one. Each person ranks up to three; one ballot per person, and a person whose ballots disagree has none; the count is instant-runoff and order-free; nobody is seated below two voices; the winner accepts by their own row or the duty passes to the next in runoff order. The voters' rows are the appointment's signatures, so no node signs anything.

**The tie.** The general ranked count breaks a tie for weakest against the option later in the choice's declared order. An election declares no order, so a tie there seats nobody and the count runs again (CC 4.5.13). The ballot's shown order is presentation only and decides nothing (CC 4.5.4).

**The model** (`Election.lean`, Lean 4 core, no Mathlib). `fold` keeps one ballot per person and drops a person whose ballots disagree; `count brk` is instant runoff with the tie rule as a parameter; `winner` is the general count with the roster as the declared order (`later`); `winnerFree` is the election's, with no order (`noOrder`); `seat` is the acceptance chain.

**Proved.**

| | Theorem |
|---|---|
| (i) with no declared order, listing the options in another order changes nothing | `free_perm` |
| (ii) where the election's count seats someone, the declared count seats the same one; a tie for weakest seats nobody | `free_agrees`, `free_tie_seats_nobody` |
| (iii) one ballot per person; a person whose ballots disagree has none | `fold_unique`, `fold_disagree_none` |
| (iv) nobody is seated below two voices | `below_floor`, `no_ballots_no_winner` |
| a winner is a member, under either rule | `winner_in_roster`, `free_in_roster` |
| an option's votes are a function of the multiset of ballots | `votesFor_perm` |
| the acceptance chain seats the first in runoff order who accepts, never one who declined | `seated_accepted`, `seated_in_order`, `decliner_never_seated` |

Worked examples by `decide`: a three-way tie for weakest that the declared count settles and the election's leaves unseated; a clear count both agree on in two listings; a repeated ballot changes nothing; a person with two different ballots drops out; a declining winner passes the duty to the next.

**What it does not model.** The 24 h clock (per node, first held, as every window), the count running again after a tie, and the roster's inputs; the model takes the roster as given.

**Run.** `lean -M 6000 -T 200000 Election.lean` (exit 0, no `sorry`).
