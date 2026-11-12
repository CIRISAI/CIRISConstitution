# `formal/ranked_choice` — ranked choice as one count

**The point.** A group chooses among options by ranking them (CC 4.5.13). The moderator election does, and any
choice among options may. For a count to run in a kernel it must give the same winner from the same ballots in
whatever order they arrived, never loop, and never need a ballot twice. Instant runoff does not look like a sum,
so this model writes it as one.

**The model.** `ranked_choice_model.py`, in two parts.

| Part | What it is |
|---|---|
| summary | how many ballots carry each ranking. Two summaries merge by adding counts. It is kept up to date one ballot at a time and is the only part that touches ballots |
| finish | instant runoff over the summary: while no option has more than half of the ballots still counting, the weakest goes and its ballots pass on. It reads no ballot and uses whole numbers only |

With `k` options and up to three ranks a summary has at most `k + k(k-1) + k(k-1)(k-2)` cells, whatever the number
of voters. One ballot counts for each person: a person's ballots are folded to one, and a person whose ballots
disagree has none.

**What is checked**, over every profile of up to five ballots on three options (15,504 profiles):

| | Property |
|---|---|
| R1 | the winner is the same for every order of the same ballots, and for every split into parts summarised apart and merged |
| R2 | the summary's merge is associative and commutative, and the empty summary changes nothing |
| R3 | the count ends in fewer rounds than there are options |
| R4 | the winner is an option, and an option more than half the ballots rank first wins |
| R5 | a tie for weakest is settled by the declared order alone |
| R6 | a ballot that ranks only eliminated options stops counting |
| R7 | below the floor of voices there is no winner |
| R8 | repeating a ballot changes nothing, and a person with two different ballots counts for none |
| R9 | a secret count gives the same winner: one cell per ranking, summed across members, is the summary |
| R10 | the runoff is run: a known profile in which the leader on first choices loses |

Each fails when its line of the count is changed.

**Not claimed.** That ranking an option higher can never hurt it. Instant runoff does not have that property, and
no rule of this document rests on it.

**What it does not model.** Who may cast a ballot and when the window closes (the policy row and
`formal/moderator_election`, which proves the seating); how a secret poll hides each member's cells
(`formal/census_ballot`); more than three options or five ballots, which the summary's form does not depend on.

Run: `python3 formal/ranked_choice/ranked_choice_model.py --check`
