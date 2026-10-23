---------------------------- MODULE CensusBallot ----------------------------
(* The census, the secret ballot and the base law (steward rulings of 2026-10-22; CC 4.5.13
   the policy's base, 5.4.6 the cohort's invisibility, 6.1.2.1.2 n_eff; edge/persist design of
   the same day, final).

   Each period every owner-bound rooted node of a community emits ONE census report. A report
   is a vector of community cells, each cell a ONE-HOT over its buckets: the expected-active
   cell ("ea": yes/no — was the owner active in this or the previous three periods, computed by
   the owner from its own history) and, when the community carries a ballot, the vote cell
   (one bucket per option, "abstain" doubling as the padding bucket, so the cell is emitted at
   the same size every period whether or not a ballot is open). Every entry is SECRET-SHARED:
   an entry v is split into s0 + s1 = v (mod M); s0 goes to tally member a0 and s1 to a1, the
   two community MEMBERS drawn from the roster by H(secret ‖ period) — the model draws any pair.
   Each tally member sums the shares it accepted; the published cell is partial_0 + partial_1
   mod M. A report is accepted only when both halves arrived, its token (one per owner per
   period) is fresh, and the validity proof (one-hot: entries in {0,1}, sum 1) the two members
   verify jointly passes; so an accepted report adds exactly one count to one bucket, every
   accepted owner has mass one, and n_eff = source_count. A cell publishes only above the
   k-floor (source_count ≥ K). Mesh cells go to two federation seats drawn by H(period ‖ class)
   under the same scheme and are not modelled here.

   The base law. The expected-active composite EA is the published "ea: yes" count. The base a
   governance fraction is taken over (above the small-community size) is census-derived: it
   never falls more than 10 % in one period (base_t ≥ ⌈0.9 · base_{t−1}⌉), never below the floor
   max(owners active this period, ⌈½ · last stable composite⌉), and a one-period fall of the
   composite by more than one third freezes it (base_t = base_{t−1}) until the composite recovers
   to within that third of the composite before the fall. "Stable" is read as: the composite
   stood on its own, EA ≥ the ratchet term, i.e. the base was not propping it up.

   Governance acts (enact/cancel/roster/moderation) stay identified rows and are modelled in
   formal/two_path; from the census they take only their BASE. The secret tally is for polls and
   elections; its pass rule here is the same five-number shape (CC 4.5.13) taken against base_t.

   The adversary: Colluding roster members pool their views when drawn as tally members (the
   claim holds when the two tally members do not both collude); Silenced owners' reports stop
   arriving once the adversary chooses; Dishonest owners may emit a vector that is not one-hot;
   a lossy network may deliver one half of a report only; an owner may replay its report. Each
   defence is a switch that a twin configuration turns off to show what the invariant catches. *)
EXTENDS Naturals, FiniteSets

CONSTANTS
  Owners,          \* the standing roster, as 1..N (an owner-bound rooted node each)
  M,               \* the share modulus
  Colluding,       \* roster members who pool their views when drawn as tally members
  Silenced,        \* owners whose reports stop arriving once the adversary silences them (one at a time, at any boundary)
  Dishonest,       \* owners who may emit a vector that is not one-hot
  Cells,           \* the community cells carried: a subset of {"ea", "vote"}
  VoteBuckets,     \* the vote cell's buckets, e.g. {"approve", "reject", "abstain"}
  Activity,        \* presence choices per period: a subset of {"absent", "idle", "active"}
  Shared,          \* TRUE: shares range over 0..M-1; FALSE: cells in the clear (base-law runs)
  Lossy,           \* TRUE: a report may reach one tally member only
  Periods, Window, MaxBallots,
  K,               \* the k-floor: a cell publishes only with source_count >= K
  Scale,           \* the composite counts in units of Scale owners (the base law at size)
  SmallCommunity,  \* at or below this size the base is the standing roster
  RatchetNum, RatchetDen, FreezeNum, FreezeDen, FloorNum, FloorDen,
  EnactNum, EnactDen, CancelNum, CancelDen, ApproveFloorNum, ApproveFloorDen, MinCount,
  \* switches: TRUE / "census" in the ruled configurations; each twin flips one
  PadWhenClosed,   \* the vote cell is emitted (as "abstain") when no ballot is open
  Dedupe,          \* a replayed token is refused
  Validate,        \* the one-hot proof is checked
  JointAccept,     \* a report counts only when both halves arrived and both members agree
  Gate,            \* the k-floor is enforced
  Ratchet,         \* the 10 % ratchet term is in the base law
  ThresholdBase    \* "census": a ballot passes against base_t; "responders": against source_count

ASSUME Owners \subseteq Nat /\ Owners # {}
ASSUME Colluding \subseteq Owners /\ Silenced \subseteq Owners /\ Dishonest \subseteq Owners
ASSUME Cells \subseteq {"ea", "vote"} /\ ("vote" \in Cells => "abstain" \in VoteBuckets)
ASSUME Activity \subseteq {"absent", "idle", "active"} /\ "active" \in Activity
ASSUME M >= 2 /\ K >= 1 /\ Scale >= 1 /\ Window >= 1
ASSUME EnactNum * 2 >= EnactDen                     \* enact never below a strict majority
ASSUME CancelNum * EnactDen <= EnactNum * CancelDen  \* cancel <= enact
ASSUME ThresholdBase \in {"census", "responders"}

N == Cardinality(Owners)
Min(a, b) == IF a <= b THEN a ELSE b
Max(a, b) == IF a >= b THEN a ELSE b
Ceil(a, b) == (a + b - 1) \div b
SetMin(S) == CHOOSE x \in S : \A y \in S : x <= y
SetMax(S) == CHOOSE x \in S : \A y \in S : x >= y

RECURSIVE SumF(_)
SumF(f) == IF DOMAIN f = {} THEN 0
           ELSE LET x == CHOOSE x \in DOMAIN f : TRUE
                IN f[x] + SumF([y \in DOMAIN f \ {x} |-> f[y]])

\* ---- the report space ----
Pending == [pres |-> "pending"]
Absent  == [pres |-> "absent"]
BucketsOf(c) == IF c = "ea" THEN {"yes", "no"} ELSE VoteBuckets
Idx == UNION {{<<c, b>> : b \in BucketsOf(c)} : c \in Cells}
Entries == 0..M-1
ShareRange == IF Shared THEN Entries ELSE {0}
Arrivals == IF Lossy THEN {"both", "a0", "a1"} ELSE {"both"}
Pairs == {p \in SUBSET Owners : Cardinality(p) = 2}
VoteChoices(op) == IF op /\ "vote" \in Cells THEN VoteBuckets ELSE {"abstain"}
Present == Activity \ {"absent"}
ZeroVec == [i \in Idx |-> 0]
BadVecs(o) == IF o \in Dishonest THEN [Idx -> Entries] ELSE {}
\* an honest report carries its value as (pres, vote); a dishonest one carries any vector in `bad`
Reports(o, op) ==
  (IF "absent" \in Activity THEN {Absent} ELSE {})
  \cup [pres : Present, vote : VoteChoices(op), sh : [Idx -> ShareRange], arr : Arrivals,
        honest : {TRUE}, bad : {ZeroVec}]
  \cup [pres : Present, vote : {"abstain"}, sh : [Idx -> ShareRange], arr : Arrivals,
        honest : {FALSE}, bad : BadVecs(o)]
OneHot(v) == /\ \A i \in Idx : v[i] <= 1
             /\ \A c \in Cells : SumF([b \in BucketsOf(c) |-> v[<<c, b>>]]) = 1
HonestVecs == {v \in [Idx -> 0..1] : OneHot(v)}
\* what an outside observer sees leave a node for one report: entries sent to each tally member
Wire(r, op) == IF r.pres = "absent" THEN 0
               ELSE IF op \/ PadWhenClosed THEN Cardinality(Idx)
               ELSE Cardinality({i \in Idx : i[1] # "vote"})
WireSpace(op) == {Wire(r, op) : r \in Reports(SetMin(Owners), op)}

VARIABLES
  t, open, age, ballots, passed, rejected, decision,
  returns, agg, dup, sil,
  last, started, base, prevBase, lower, lastStable, prevEA, frozen, freezeRef, act
vars == <<t, open, age, ballots, passed, rejected, decision, returns, agg, dup, sil,
          last, started, base, prevBase, lower, lastStable, prevEA, frozen, freezeRef, act>>

Sil == sil
AllPending == \A o \in Owners : returns[o].pres = "pending"
AllIn == \A o \in Owners : returns[o].pres # "pending"
NoDecision(b) == [kind |-> "none", appr |-> 0, obj |-> 0, baseAt |-> b]

\* ---- the period's reports, parametrised by the returns function R ----
ReturnedR(R) == {o \in Owners : R[o].pres \notin {"pending", "absent"}}
Last1R(R, o) == IF o \in ReturnedR(R) /\ R[o].pres = "active" THEN 0 ELSE Min(last[o] + 1, 4)
RecentR(R, o) == Last1R(R, o) <= 3
HonestVecR(R, o) == [i \in Idx |->
  IF i[1] = "ea" THEN (IF (i[2] = "yes") = RecentR(R, o) THEN 1 ELSE 0)
  ELSE (IF i[2] = R[o].vote THEN 1 ELSE 0)]
VecR(R, o) == IF R[o].honest THEN HonestVecR(R, o) ELSE R[o].bad
Lo == SetMin(agg)
Hi == SetMax(agg)
IndexOf(a) == IF a = Lo THEN 0 ELSE 1
ShareR(R, k, o, i) == IF k = 0 THEN R[o].sh[i] ELSE (VecR(R, o)[i] + M - R[o].sh[i]) % M
RecvR(R, k) == {o \in ReturnedR(R) : R[o].arr \in {"both", IF k = 0 THEN "a0" ELSE "a1"}}
ValidR(R, o) == ~Validate \/ OneHot(VecR(R, o))
AccR(R, k) == IF JointAccept THEN {o \in RecvR(R, 0) \cap RecvR(R, 1) : ValidR(R, o)}
              ELSE {o \in RecvR(R, k) : ValidR(R, o)}
Cnt(o) == IF o \in dup THEN 2 ELSE 1
PartialR(R, k, i) == SumF([o \in AccR(R, k) |-> Cnt(o) * ShareR(R, k, o, i)]) % M
\* a colluding tally member's view: every share it received, and its partial sums
ViewR(R) == [a \in agg \cap Colluding |->
  [shares |-> [o \in RecvR(R, IndexOf(a)) |-> [i \in Idx |-> ShareR(R, IndexOf(a), o, i)]],
   partial |-> [i \in Idx |-> PartialR(R, IndexOf(a), i)]]]

\* ---- the state's reports ----
Returned == ReturnedR(returns)
Accepted == AccR(returns, 0)
SourceCount == SumF([o \in Accepted |-> Cnt(o)])
Masses == [o \in Accepted |-> Cnt(o)]
NEff == IF SourceCount = 0 THEN 0
        ELSE (SourceCount * SourceCount) \div SumF([o \in Accepted |-> Cnt(o) * Cnt(o)])
Published(i) == (PartialR(returns, 0, i) + PartialR(returns, 1, i)) % M
Publishes == Accepted # {} /\ (~Gate \/ SourceCount >= K)
Recent(o) == RecentR(returns, o)
EA == Scale * (IF "ea" \in Cells THEN Published(<<"ea", "yes">>)
               ELSE Cardinality({o \in Accepted : Recent(o)}))
ActCount == Cardinality({o \in Accepted : returns[o].pres = "active"})
Approvals  == IF "vote" \in Cells /\ "approve" \in VoteBuckets THEN Published(<<"vote", "approve">>) ELSE 0
Objections == IF "vote" \in Cells /\ "reject" \in VoteBuckets THEN Published(<<"vote", "reject">>) ELSE 0
CensusBase == IF N <= SmallCommunity THEN N ELSE base

Init == /\ t = 0 /\ open = FALSE /\ age = 0 /\ ballots = 0 /\ passed = 0 /\ rejected = 0
        /\ decision = NoDecision(0)
        /\ returns = [o \in Owners |-> Pending] /\ agg = (CHOOSE p \in Pairs : TRUE) /\ dup = {} /\ sil = {}
        /\ last = [o \in Owners |-> 4] /\ started = FALSE
        /\ base = 0 /\ prevBase = 0 /\ lower = 0 /\ lastStable = 0 /\ prevEA = 0
        /\ frozen = FALSE /\ freezeRef = 0 /\ act = 0

\* the adversary silences one more of its owners, at any period boundary (several at one
\* boundary is several steps there); a silenced owner never reports again
Silence == /\ AllPending
           /\ \E o \in Silenced \ sil : sil' = sil \cup {o}
           /\ UNCHANGED <<t, open, age, ballots, passed, rejected, decision, returns, agg, dup,
                          last, started, base, prevBase, lower, lastStable, prevEA, frozen, freezeRef, act>>

\* a ballot opens at a period boundary; it must be able to run its window inside the bound
OpenBallot == /\ AllPending /\ ~open /\ ballots < MaxBallots /\ t + Window <= Periods /\ "vote" \in Cells
              /\ open' = TRUE /\ age' = 0 /\ ballots' = ballots + 1
              /\ UNCHANGED <<t, passed, rejected, decision, returns, agg, dup, sil,
                             last, started, base, prevBase, lower, lastStable, prevEA, frozen, freezeRef, act>>

\* the owners emit in roster order; the period's two tally members are drawn with the first
\* report (in the clear there is nothing to draw for), and the previous period's decision
\* record is cleared (it is read at the boundary)
Emit == /\ t < Periods /\ ~AllIn
        /\ LET o == SetMin({x \in Owners : returns[x].pres = "pending"}) IN
           /\ \E r \in (IF o \in Sil THEN {Absent} ELSE Reports(o, open)) :
                returns' = [returns EXCEPT ![o] = r]
           /\ IF AllPending THEN (IF Shared THEN agg' \in Pairs ELSE UNCHANGED agg) /\ decision' = NoDecision(0)
              ELSE UNCHANGED <<agg, decision>>
        /\ UNCHANGED <<t, open, age, ballots, passed, rejected, dup, sil,
                       last, started, base, prevBase, lower, lastStable, prevEA, frozen, freezeRef, act>>

\* an owner replays its report (same token, same shares)
Replay == /\ AllIn /\ ~Dedupe
          /\ \E o \in Returned \ dup : dup' = dup \cup {o}
          /\ UNCHANGED <<t, open, age, ballots, passed, rejected, decision, returns, agg, sil,
                         last, started, base, prevBase, lower, lastStable, prevEA, frozen, freezeRef, act>>

\* the period closes: the composite publishes (or not), the base law runs, the ballot is decided
Close ==
  /\ AllIn
  /\ LET pub == Publishes
         ea == EA
         fall == ~frozen /\ ea * FreezeDen < prevEA * (FreezeDen - FreezeNum)
         recovered == frozen /\ ea * FreezeDen >= freezeRef * (FreezeDen - FreezeNum)
         ratchet == IF Ratchet THEN Ceil(base * RatchetNum, RatchetDen) ELSE 0
         floorHalf == Ceil(lastStable * FloorNum, FloorDen)
         floorAct == Scale * ActCount
         normal == Max(ea, Max(ratchet, Max(floorHalf, floorAct)))
         bt == IF ~pub THEN base
               ELSE IF ~started THEN ea
               ELSE IF (frozen /\ ~recovered) \/ fall THEN base
               ELSE normal
         B == IF ThresholdBase = "responders" THEN SourceCount
              ELSE IF N <= SmallCommunity THEN N ELSE bt
         appr == Approvals
         obj == Objections
         passNow == pub /\ appr * EnactDen > EnactNum * B
         rejectNow == pub /\ obj >= MinCount /\ obj * CancelDen >= CancelNum * B
         windowPass == pub /\ appr >= MinCount /\ appr * ApproveFloorDen >= ApproveFloorNum * B
         pass == [kind |-> "pass", appr |-> appr, obj |-> obj, baseAt |-> B]
         rej == [kind |-> "reject", appr |-> appr, obj |-> obj, baseAt |-> B]
     IN
     /\ last' = [o \in Owners |-> Last1R(returns, o)]
     /\ prevBase' = base
     /\ base' = bt
     /\ lower' = IF started THEN Ceil(lower * RatchetNum, RatchetDen) ELSE (IF pub THEN ea ELSE 0)
     /\ IF ~pub THEN UNCHANGED <<lastStable, prevEA, frozen, freezeRef, act, started>>
        ELSE IF ~started THEN
             /\ lastStable' = ea /\ prevEA' = ea /\ frozen' = FALSE /\ freezeRef' = ea
             /\ act' = ActCount /\ started' = TRUE
        ELSE IF frozen /\ ~recovered THEN
             /\ prevEA' = ea /\ act' = ActCount /\ UNCHANGED <<lastStable, frozen, freezeRef, started>>
        ELSE IF fall THEN
             /\ prevEA' = ea /\ frozen' = TRUE /\ freezeRef' = prevEA /\ act' = ActCount
             /\ UNCHANGED <<lastStable, started>>
        ELSE \* the normal step, and the step that ends a freeze
             /\ prevEA' = ea /\ frozen' = FALSE /\ act' = ActCount
             /\ lastStable' = IF ea >= ratchet THEN ea ELSE lastStable
             /\ UNCHANGED <<freezeRef, started>>
     /\ IF ~open THEN /\ decision' = NoDecision(B) /\ UNCHANGED <<open, age, passed, rejected>>
        ELSE IF passNow THEN /\ open' = FALSE /\ age' = 0 /\ passed' = passed + 1 /\ decision' = pass /\ UNCHANGED rejected
        ELSE IF rejectNow THEN /\ open' = FALSE /\ age' = 0 /\ rejected' = rejected + 1 /\ decision' = rej /\ UNCHANGED passed
        ELSE IF age + 1 >= Window THEN
             IF windowPass THEN /\ open' = FALSE /\ age' = 0 /\ passed' = passed + 1 /\ decision' = pass /\ UNCHANGED rejected
             ELSE /\ open' = FALSE /\ age' = 0 /\ rejected' = rejected + 1 /\ decision' = rej /\ UNCHANGED passed
        ELSE /\ age' = age + 1 /\ decision' = NoDecision(B) /\ UNCHANGED <<open, passed, rejected>>
     /\ t' = t + 1
     /\ returns' = [o \in Owners |-> Pending]
     /\ dup' = {}
     /\ UNCHANGED <<ballots, agg, sil>>

Next == Silence \/ OpenBallot \/ Emit \/ Replay \/ Close
Spec == Init /\ [][Next]_vars /\ WF_vars(Next)

(* ---------------- the invariants, named as edge states them ---------------- *)

\* Inv_SharePrivacy: a colluding tally member's view (every share it received, its partial sums)
\* is the same under every value of every accepted report of another owner: for each such owner
\* and each alternative one-hot vector there is a share assignment producing the identical view.
\* Guard: the two tally members do not both collude. (A refused report is seen to be refused —
\* that is the validity proof's verdict, not its value — so the claim is over accepted reports.)
\* The share assignment exhibited for owner o and alternative vector v: keep the share the
\* colluding member holds (first share if it is a0, else the complement that reproduces the
\* second share). TLC then compares the whole recomputed view with the actual one, so what is
\* checked is the existence of such an assignment, not the construction.
Witness(o, v, k) == IF k = 0 THEN returns[o].sh
                    ELSE [i \in Idx |-> (v[i] + M - ShareR(returns, 1, o, i)) % M]
PrivateFor(o, view) == \A v \in HonestVecs : \E k \in {IndexOf(a) : a \in agg \cap Colluding} \cup {0} :
  ViewR([returns EXCEPT ![o] = [@ EXCEPT !.sh = Witness(o, v, k), !.honest = FALSE, !.bad = v]]) = view
Inv_SharePrivacy == AllIn =>
  LET view == ViewR(returns) IN
  \A o \in Accepted \ Colluding : ~(agg \subseteq Colluding) => PrivateFor(o, view)
Inv_BallotSecrecy == Inv_SharePrivacy
\* the dye for the two-colluding twin: the same claim without the guard
Inv_SecrecyWithoutTheGuard == AllIn =>
  LET view == ViewR(returns) IN \A o \in Accepted \ Colluding : PrivateFor(o, view)

\* Inv_Correctness: partial_0 + partial_1 = Σ accepted values (mod M), and exactly when in range
Inv_Correctness == AllIn =>
  \A i \in Idx : LET s == SumF([o \in Accepted |-> VecR(returns, o)[i]]) IN
    /\ Published(i) = s % M
    /\ (s < M => Published(i) = s)
Inv_TallyExact == Inv_Correctness

\* Inv_Validity: every accepted report is one-hot
Inv_Validity == AllIn => \A o \in Accepted : OneHot(VecR(returns, o))

\* Inv_Agreement: both tally members accept the same report set — equal token sets, equal source_count
Inv_Agreement == AllIn => AccR(returns, 0) = AccR(returns, 1)
                          /\ Cardinality(AccR(returns, 0)) = Cardinality(AccR(returns, 1))

\* Inv_OnePerOwner: one report counted per owner per period, hence n_eff = source_count
Inv_OnePerOwner == AllIn => /\ \A o \in Accepted : Cnt(o) <= 1
                            /\ SourceCount = Cardinality(Accepted)
                            /\ NEff = SourceCount
Inv_OneReturnPerOwner == Inv_OnePerOwner

\* Inv_KFloor: no published cell has source_count < K
Inv_KFloor == (AllIn /\ Publishes) => SourceCount >= K

\* Inv_DominanceGate: no published composite has one owner with more than half the mass (CC 6.1.2.1.2)
Inv_DominanceGate == (AllIn /\ Publishes) => \A o \in Accepted : 2 * Cnt(o) <= SourceCount

\* Inv_OccurrenceInvisible: every reporting member sends the same number of entries to each tally
\* member whether or not a ballot is open, and the set of wire profiles a member can produce is
\* the same with and without an open ballot.
Inv_OccurrenceInvisible ==
  /\ AllIn => \A o \in Returned : Wire(returns[o], open) = Cardinality(Idx)
  /\ AllPending => WireSpace(TRUE) = WireSpace(FALSE)

\* Inv_BaseRatchet: base_t ≥ max(floor_t, ⌈0.9 · base_{t−1}⌉); the cumulative bound from the
\* first census; the base is never below the last composite nor below the owners active in it;
\* and under the partition freeze base_t = base_{t−1}.
Inv_BaseRatchet == started =>
  /\ base * RatchetDen >= prevBase * RatchetNum
  /\ base >= lower
  /\ base * FloorDen >= lastStable * FloorNum
  /\ base >= Scale * act
  /\ base >= prevEA
  /\ (frozen => base = prevBase /\ base >= freezeRef)

\* Inv_TallyThreshold: a ballot passes only against base_t (the census base, or the standing
\* roster at or below the small-community size) — never against the responders alone
Inv_TallyThreshold == (AllPending /\ decision.kind = "pass") =>
  \/ decision.appr * EnactDen > EnactNum * CensusBase
  \/ (decision.appr >= MinCount /\ decision.appr * ApproveFloorDen >= ApproveFloorNum * CensusBase)

\* liveness: an open ballot is decided (passes or is rejected) within its window
Prop_HonestChangeResolves == [](open => <>(~open))

(* ---------------- reachability dyes: each is FALSE somewhere in its instance ---------------- *)
\* the ratchet carries the base: it fell, by exactly the ratchet term, above the composite
Reach_RatchetCarries == started =>
  ~(base < prevBase /\ base = Ceil(prevBase * RatchetNum, RatchetDen) /\ base > prevEA)
\* the partition freeze is entered
Reach_Frozen == ~frozen
\* the half-of-last-stable floor is the binding term: above the composite and above the ratchet
Reach_FloorBinds == started =>
  ~(base = Ceil(lastStable * FloorNum, FloorDen) /\ base > prevEA
    /\ base > Ceil(prevBase * RatchetNum, RatchetDen))
=============================================================================
