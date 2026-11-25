---------------------------- MODULE TwoPathRows ----------------------------
(* The lone path as a window of rows (CC 3.3.6.4, "The lone path is a window of rows"; CC 2.7, the window):
   one proposal over a roster of three keys, its rows with their pasts written out, and two nodes that
   receive those rows in every order.

   TwoPath.tla is the count table at one reader with an abstract age. This module is what replaces the
   reading in which a node closed the window on its own clock: here the outcome of a proposal is a
   function of the rows a node counts, and of nothing else the node has.

   A ROW is  [id, kind, by, past, says, el, held] :
     open      the proposal p. K1 signs it over the roster {K1, K2, K3}.
     answer    names p; says "approve" or "object".
     withdraw  the proposer's withdrawal of p.
     note      any other row a key signs (the target's "any row").
     held      window:held. A key says it holds p.
     landing   window:landed / window:refused. It names its signer's own held row (field held), states
               an outcome (says) and whether its own two instants span the window (el). No instant of
               one signer is compared with another's, so the span is the concluder's own word and a
               boolean here.
   past is the set of ids of every row in the row's past (closed: a past contains the pasts of its
   members). "r names L" is  L.id \in r.past.

   The outcome of p over a set R of counted rows:
     the table over a set X of rows, with a span el and "the target signed inside" tIn:
        a strict majority of the roster approving, the proposer counted         -> landed
        else the proposer's withdrawal in X                                     -> refused
        else a strict majority of the others objecting                          -> refused
        else not el                                                             -> none
        else an eviction and tIn                                                -> refused
        else                                                                    -> landed
        (an approval that has the withdrawal in its past approves nothing; an addition has the same
         table without the target's silence)
     a landing L CONCLUDES iff its held row is its signer's, the signer is seated, the held row has in
        its past no row the target signed beyond what p has in its own past, and the table over L's own
        past gives the outcome L states;
     a landing STANDS iff it concludes and the table over every counted row that does not name L
        (L's past and the rows concurrent with it) still gives the outcome L states;
     the frontier is the concluded landings that no concluded landing names;
     outcome = the one outcome the standing frontier landings state, "contested" where two differ;
               with none standing: the met count's or the withdrawal's outcome, read with no landing;
               else "open" where no landing concluded, "contested" otherwise.

   A node holds rows in any order. A row is COUNTED at a node once every row of its past is counted
   there; until then it waits. The node's reading is Outcome over what it counts.

   Planted readings (Plant, overridden in a configuration):
     node_clock           the reading this module replaces: each node closes the window on its own
                          clock and keeps what it then read. Reaches formal/derivation/order/witnesses.tsv
                          row C1: two nodes that hold the same rows and differ for good.
     no_cascade           a row that arrives before its past is dropped and never counted.
     no_held_rule         a held row may have the target's later rows in its past.
     landing_unchecked    a landing concludes on its word, whatever the table gives over its past.
     landing_needed       a met count gives no outcome until a landing states it.
     withdrawal_first     the withdrawal is read before the majority's approval.
     wd_approval_counts   an approval that has the withdrawal in its past still approves.
     unseated_concludes   a landing by a key that holds no seat in the roster concludes.
     others_held_row      a landing may name a held row another key signed.
     two_voices_count     a signer who answered both ways is counted as approving.
     add_asks_silence     an addition asks the silence of the key it adds, as an eviction does of its target.
     proposal_past_barred a held row may have no row of the target in its past at all, the rows the
                          proposal has in its own past included.
     named_rows_recounted a row that names a landing is recounted against it like a concurrent one.

   Two readings the scenarios fix and the text has not ruled (ScLate; see the README):
     an answer that names a landing is not counted against it, so a strict majority of the others
     objecting AFTER a lone landing, each naming it, leaves it landed; and a strict majority approving,
     each naming a standing `refused` landing, leaves it refused. Inv_MetCountDecides is therefore
     stated over answers that name no landing. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Nodes

Plant == "none"
PlantNodeClock == "node_clock"
PlantNoCascade == "no_cascade"
PlantNoHeldRule == "no_held_rule"
PlantLandingUnchecked == "landing_unchecked"
PlantLandingNeeded == "landing_needed"
PlantWithdrawalFirst == "withdrawal_first"
PlantWdApprovalCounts == "wd_approval_counts"
PlantUnseatedConcludes == "unseated_concludes"
PlantOthersHeldRow == "others_held_row"
PlantTwoVoicesCount == "two_voices_count"
PlantAddAsksSilence == "add_asks_silence"
PlantProposalPastBarred == "proposal_past_barred"
PlantNamedRowsRecounted == "named_rows_recounted"

Base == {"K1", "K2", "K3"}
By == "K1"

R(id, kind, by, past, says, el, held) ==
  [id |-> id, kind |-> kind, by |-> by, past |-> past, says |-> says, el |-> el, held |-> held]
Pp == R("p", "open", By, {}, "-", FALSE, "-")

(* ---- the scenarios: each a kind, a target, and the rows that may ever be signed ---- *)
\* an eviction of K2. x: the target signs a row and leaves every landing unnamed. xn: the target signs a
\* row that names the landing L1. L1: the proposer lands alone. L3: K3 lands "refused", naming L1 and x.
ScEvict == [kind |-> "evict", target |-> "K2", rows |-> {
  Pp,
  R("x",  "note",     "K2", {"p"}, "-", FALSE, "-"),
  R("xn", "note",     "K2", {"p", "h1", "L1"}, "-", FALSE, "-"),
  R("o3", "answer",   "K3", {"p"}, "object", FALSE, "-"),
  R("w",  "withdraw", "K1", {"p"}, "-", FALSE, "-"),
  R("h1", "held",     "K1", {"p"}, "-", FALSE, "-"),
  R("L1", "landing",  "K1", {"p", "h1"}, "landed", TRUE, "h1"),
  R("h3", "held",     "K3", {"p"}, "-", FALSE, "-"),
  R("L3", "landing",  "K3", {"p", "h3", "x", "h1", "L1"}, "refused", TRUE, "h3") }]
\* the counts: a3 approves; a3w approves with the withdrawal in its past; o2 and o3 object; Lf is a
\* landing that states "landed" with both objections in its past; Le is a landing whose span is short.
ScCount == [kind |-> "evict", target |-> "K2", rows |-> {
  Pp,
  R("a3",  "answer",   "K3", {"p"}, "approve", FALSE, "-"),
  R("a3w", "answer",   "K3", {"p", "w"}, "approve", FALSE, "-"),
  R("w",   "withdraw", "K1", {"p"}, "-", FALSE, "-"),
  R("o2",  "answer",   "K2", {"p"}, "object", FALSE, "-"),
  R("h1",  "held",     "K1", {"p"}, "-", FALSE, "-"),
  R("Le",  "landing",  "K1", {"p", "h1"}, "landed", FALSE, "h1"),
  R("h3",  "held",     "K3", {"p"}, "-", FALSE, "-"),
  R("Lw",  "landing",  "K3", {"p", "h3", "w"}, "landed", TRUE, "h3") }]
\* the held row: hb has the target's row x in its past, and Lb is landed on it. Lx is a landing by K3
\* that states "refused", names L1, and has nothing in its past that gives a refusal.
ScHeld == [kind |-> "evict", target |-> "K2", rows |-> {
  Pp,
  R("x",  "note",    "K2", {"p"}, "-", FALSE, "-"),
  R("hb", "held",    "K1", {"p", "x"}, "-", FALSE, "-"),
  R("Lb", "landing", "K1", {"p", "x", "hb"}, "landed", TRUE, "hb"),
  R("h1", "held",    "K1", {"p"}, "-", FALSE, "-"),
  R("L1", "landing", "K1", {"p", "h1"}, "landed", TRUE, "h1"),
  R("h3", "held",    "K3", {"p"}, "-", FALSE, "-"),
  R("Lx", "landing", "K3", {"p", "h3", "h1", "L1"}, "refused", TRUE, "h3") }]
\* an addition of K4, which is no member. x is a row K4 signs (the "target" of an addition is the key it
\* adds, and the table asks no silence of it). o2 and o3 object; L1 lands alone; L1o lands with one
\* objection in its past; Lf states "landed" with both objections in its past.
ScAdd == [kind |-> "add", target |-> "K4", rows |-> {
  Pp,
  R("o2",  "answer",   "K2", {"p"}, "object", FALSE, "-"),
  R("o3",  "answer",   "K3", {"p"}, "object", FALSE, "-"),
  R("x",   "note",     "K4", {"p"}, "-", FALSE, "-"),
  R("h1",  "held",     "K1", {"p"}, "-", FALSE, "-"),
  R("L1",  "landing",  "K1", {"p", "h1"}, "landed", TRUE, "h1"),
  R("h1b", "held",     "K1", {"p"}, "-", FALSE, "-"),
  R("L1o", "landing",  "K1", {"p", "h1b", "o2"}, "landed", TRUE, "h1b"),
  R("h3",  "held",     "K3", {"p"}, "-", FALSE, "-"),
  R("Lf",  "landing",  "K3", {"p", "h3", "o2", "o3"}, "landed", TRUE, "h3") }]

\* a row of the target that names the landing, and a second landing that counts that row
ScReopen == [kind |-> "evict", target |-> "K2", rows |-> {
  Pp,
  R("h1",  "held",    "K1", {"p"}, "-", FALSE, "-"),
  R("L1",  "landing", "K1", {"p", "h1"}, "landed", TRUE, "h1"),
  R("xn",  "note",    "K2", {"p", "h1", "L1"}, "-", FALSE, "-"),
  R("h3",  "held",    "K3", {"p"}, "-", FALSE, "-"),
  R("L3n", "landing", "K3", {"p", "h3", "h1", "L1", "xn"}, "refused", TRUE, "h3") }]

Of_(X, k) == {r \in X : r.kind = k}
\* the proposal's own past: the target signed x0 BEFORE the proposal, and the proposal names it. A held
\* row may have x0 in its past (it is not beyond what the proposal has in its own past), and x0 is no row
\* signed inside the window. x is the target's row after the proposal; hb has x in its past.
ScPast == [kind |-> "evict", target |-> "K2", rows |-> {
  R("x0", "note",    "K2", {}, "-", FALSE, "-"),
  R("p",  "open",    "K1", {"x0"}, "-", FALSE, "-"),
  R("h1", "held",    "K1", {"x0", "p"}, "-", FALSE, "-"),
  R("L1", "landing", "K1", {"x0", "p", "h1"}, "landed", TRUE, "h1"),
  R("x",  "note",    "K2", {"x0", "p"}, "-", FALSE, "-"),
  R("hb", "held",    "K1", {"x0", "p", "x"}, "-", FALSE, "-"),
  R("Lb", "landing", "K1", {"x0", "p", "x", "hb"}, "landed", TRUE, "hb") }]
\* who concludes, and whose voice counts. K9 holds no seat: h9 and L9 are its held row and landing.
\* Lz is a landing by K3 that names K1's held row. Ln is a landing by K1 that names, as its held row, a
\* row that is no held row. a3 and o3 are K3 answering both ways.
ScWho == [kind |-> "evict", target |-> "K2", rows |-> {
  Pp,
  R("h1", "held",    "K1", {"p"}, "-", FALSE, "-"),
  R("h9", "held",    "K9", {"p"}, "-", FALSE, "-"),
  R("L9", "landing", "K9", {"p", "h9"}, "landed", TRUE, "h9"),
  R("Lz", "landing", "K3", {"p", "h1"}, "landed", TRUE, "h1"),
  R("n1", "note",    "K1", {"p"}, "-", FALSE, "-"),
  R("Ln", "landing", "K1", {"p", "n1"}, "landed", TRUE, "n1"),
  R("a3", "answer",  "K3", {"p"}, "approve", FALSE, "-"),
  R("o3", "answer",  "K3", {"p"}, "object", FALSE, "-") }]
\* answers that NAME a landing. o2n and o3n object after the lone landing L1 and name it. L3 is K3's
\* landing "refused" on the target's row x; a3n is K3's approval that names L3.
ScLate == [kind |-> "evict", target |-> "K2", rows |-> {
  Pp,
  R("h1",  "held",    "K1", {"p"}, "-", FALSE, "-"),
  R("L1",  "landing", "K1", {"p", "h1"}, "landed", TRUE, "h1"),
  R("o2n", "answer",  "K2", {"p", "h1", "L1"}, "object", FALSE, "-"),
  R("o3n", "answer",  "K3", {"p", "h1", "L1"}, "object", FALSE, "-"),
  R("x",   "note",    "K2", {"p"}, "-", FALSE, "-"),
  R("h3",  "held",    "K3", {"p"}, "-", FALSE, "-"),
  R("L3",  "landing", "K3", {"p", "h3", "x"}, "refused", TRUE, "h3"),
  R("a3n", "answer",  "K3", {"p", "h3", "x", "L3"}, "approve", FALSE, "-") }]

Sc == ScEvict
P0 == CHOOSE r \in Sc.rows : r.kind = "open"
ASSUME Cardinality(Of_(Sc.rows, "open")) = 1 /\ P0.id = "p" /\ P0.by = By
ASSUME \A r \in Sc.rows : r.past \subseteq {q.id : q \in Sc.rows}
ASSUME \A r \in Sc.rows : \A q \in Sc.rows : q.id \in r.past => q.past \subseteq r.past   \* pasts are closed
ASSUME \A r, q \in Sc.rows : r.id = q.id => r = q

(* ---- the rule ---- *)
Ids(X) == {r.id : r \in X}
Of(X, k) == {r \in X : r.kind = k}
Row(i) == CHOOSE r \in Sc.rows : r.id = i
Maj(S, n) == Cardinality(S) * 2 > n
Others == Base \ {By}
Wds(X) == Of(X, "withdraw")
HasWd(a) == \E w \in Of(Sc.rows, "withdraw") : w.id \in a.past
Said(X, v) == {a.by : a \in {b \in Of(X, "answer") : b.says = v}} \cap Others
\* a voice that says two things says nothing
Approvers(X) ==
  LET good == {a.by : a \in {b \in Of(X, "answer") : b.says = "approve" /\ (Plant = "wd_approval_counts" \/ ~HasWd(b))}} \cap Others
  IN  (good \ (IF Plant = "two_voices_count" THEN {} ELSE Said(X, "object"))) \cup {By}
Objectors(X) == Said(X, "object") \ Said(X, "approve")
MetApprove(X) == Maj(Approvers(X), Cardinality(Base))
MetObject(X) == Maj(Objectors(X), Cardinality(Others))

Table(X, el, tIn) ==
  IF Plant = "withdrawal_first" /\ Wds(X) # {} THEN "refused"
  ELSE IF MetApprove(X) THEN "landed"
  ELSE IF Wds(X) # {} THEN "refused"
  ELSE IF MetObject(X) THEN "refused"
  ELSE IF ~el THEN "none"
  ELSE IF (Sc.kind = "evict" \/ Plant = "add_asks_silence") /\ tIn THEN "refused"
  ELSE "landed"

PastOf(X, r) == {q \in X : q.id \in r.past}
\* the rows the target signed in X that are not in the past of the held row h
TgtIn(X, h) == \E t \in X : t.by = Sc.target /\ t.id \notin h.past /\ t.id # h.id
HeldOk(X, L) ==
  /\ L.held \in Ids(X)
  /\ LET h == Row(L.held)
     IN  /\ h.kind = "held"
         /\ h.by = L.by \/ Plant = "others_held_row"
         /\ L.by \in Base \/ Plant = "unseated_concludes"
         /\ Plant = "no_held_rule" \/ ~\E t \in PastOf(Sc.rows, h) :
                                         t.by = Sc.target /\ (Plant = "proposal_past_barred" \/ t.id \notin P0.past)
Concluded(X, L) ==
  /\ HeldOk(X, L)
  /\ Plant = "landing_unchecked" \/ Table(PastOf(X, L), L.el, TgtIn(PastOf(X, L), Row(L.held))) = L.says
Stands(X, L) ==
  /\ Concluded(X, L)
  /\ LET Y == {r \in X : (Plant = "named_rows_recounted" \/ L.id \notin r.past) /\ r.id # L.id}
     IN  Table(Y, L.el, TgtIn(Y, Row(L.held))) = L.says
Conc(X) == {L \in Of(X, "landing") : Concluded(X, L)}
Frontier(X) == {L \in Conc(X) : ~\E M \in Conc(X) : L.id \in M.past}
AtOnce(X) == IF Plant = "landing_needed" THEN "none" ELSE Table(X, FALSE, FALSE)
Outcome(X) ==
  IF P0 \notin X THEN "none"
  ELSE LET S == {L \in Frontier(X) : Stands(X, L)}
       IN  IF S # {} THEN (IF \A L, M \in S : L.says = M.says THEN (CHOOSE L \in S : TRUE).says ELSE "contested")
           ELSE IF AtOnce(X) # "none" THEN AtOnce(X)
           ELSE IF Conc(X) = {} THEN "open" ELSE "contested"

(* ---- the nodes ---- *)
VARIABLES has,      \* has[n]: the rows node n holds
          counted,  \* counted[n]: the rows node n counts, kept as rows arrive
          latch     \* node_clock only: what node n read when its own clock closed the window
vars == <<has, counted, latch>>

RECURSIVE Close(_, _)
Close(C, H) == LET add == {r \in H \ C : r.past \subseteq Ids(C)}
               IN  IF add = {} THEN C ELSE Close(C \cup add, H)

Init == /\ has = [n \in Nodes |-> {}] /\ counted = [n \in Nodes |-> {}] /\ latch = [n \in Nodes |-> "none"]

Deliver(n, r) ==
  /\ r \in Sc.rows \ has[n]
  /\ has' = [has EXCEPT ![n] = @ \cup {r}]
  /\ counted' = [counted EXCEPT ![n] =
                   IF Plant = "no_cascade"
                   THEN (IF r.past \subseteq Ids(@) THEN @ \cup {r} ELSE @)
                   ELSE Close(@, has'[n])]
  /\ UNCHANGED latch

\* the replaced reading: a node's window closes on its own clock, at any moment after it holds the
\* proposal, and the node keeps what it reads then (CC 3.3.6.4 before the window of rows)
ClockVerdict(X) ==
  IF MetApprove(X) THEN "landed"
  ELSE IF MetObject(X) \/ Wds(X) # {} THEN "refused"
  ELSE IF Sc.kind = "evict" /\ \E t \in X : t.by = Sc.target /\ t.id # "p" THEN "refused"
  ELSE "landed"
ClockCloses(n) ==
  /\ Plant = "node_clock" /\ P0 \in counted[n] /\ latch[n] = "none"
  /\ latch' = [latch EXCEPT ![n] = ClockVerdict(counted[n])]
  /\ UNCHANGED <<has, counted>>

Next == \E n \in Nodes : ClockCloses(n) \/ \E r \in Sc.rows : Deliver(n, r)
Spec == Init /\ [][Next]_vars

Reading(n) ==
  IF Plant = "node_clock"
  THEN (IF latch[n] # "none" THEN latch[n]
        ELSE IF P0 \notin counted[n] THEN "none"
        ELSE IF MetApprove(counted[n]) THEN "landed" ELSE "open")
  ELSE Outcome(counted[n])

-----------------------------------------------------------------------------
TypeOK == /\ \A n \in Nodes : has[n] \subseteq Sc.rows /\ counted[n] \subseteq has[n]
          /\ \A n \in Nodes : latch[n] \in {"none", "landed", "refused"}

(* Two nodes that hold the same rows read the same outcome, in whatever order the rows arrived.
   Under the rule the reading takes the counted rows and nothing else, so what the run checks is the
   keeping of `counted` as rows arrive (a row waits for its past and is counted when the past is). *)
Inv_SameRowsSameOutcome ==
  \A a, b \in Nodes : has[a] = has[b] => (counted[a] = counted[b] /\ Reading(a) = Reading(b))
\* witnesses.tsv row C1: both nodes hold every row there is; one reads the change as landed and the
\* other as refused. Nothing more can arrive, so they differ for good.
Inv_C1Unreachable ==
  ~\E a, b \in Nodes : has[a] = Sc.rows /\ has[b] = Sc.rows /\ Reading(a) = "landed" /\ Reading(b) = "refused"
\* what a node holds and what it counts differ only by rows whose past it does not hold
Inv_CountedIsClosure == \A n \in Nodes : counted[n] = Close({}, has[n])

(* The readings below are stated without the operators of the rule where they can be. *)
C(n) == counted[n]
\* a met count gives its outcome with no landing row, and the proposer's withdrawal comes after the
\* majority's approval
GoodApprovals(X) == {a \in Of(X, "answer") : a.says = "approve" /\ a.by \in Others /\ ~\E w \in Wds(Sc.rows) : w.id \in a.past}
\* no answer the node counts names a landing (an answer that names a landing came after it; what such
\* answers do is fixed by Inv_KnownLate and is a question for the text)
NoLateAnswer(n) == ~\E a \in Of(C(n), "answer") : \E L \in Of(Sc.rows, "landing") : L.id \in a.past
Inv_MetCountDecides ==
  \A n \in Nodes : NoLateAnswer(n) =>
    /\ (P0 \in C(n) /\ Cardinality({a.by : a \in GoodApprovals(C(n))} \cup {By}) * 2 > 3
          /\ Said(C(n), "object") \cap {a.by : a \in GoodApprovals(C(n))} = {}) => Reading(n) = "landed"
    /\ (P0 \in C(n) /\ GoodApprovals(C(n)) = {} /\ Said(C(n), "approve") = {} /\ Cardinality(Said(C(n), "object")) = 2)
          => Reading(n) = "refused"
\* a withdrawal the node counts, with no approval made without it: refused, whatever landings say
Inv_WithdrawalRefuses ==
  \A n \in Nodes : (Wds(C(n)) # {} /\ GoodApprovals(C(n)) = {}) => Reading(n) = "refused"
\* a lone eviction is never read as landed while the node counts a row the target signed that is not in
\* the proposal's own past and names no landing
Inv_TargetRowStopsLoneEviction ==
  \A n \in Nodes :
    (Sc.kind = "evict" /\ Reading(n) = "landed" /\ GoodApprovals(C(n)) = {})
      => ~\E t \in C(n) : t.by = Sc.target /\ t.id \notin P0.past /\ ~\E L \in Of(Sc.rows, "landing") : L.id \in t.past
\* nothing but the rule's four outcomes (and "none" before the proposal is counted)
Inv_FourOutcomes == \A n \in Nodes : Reading(n) \in {"none", "open", "contested", "landed", "refused"}

(* Known answers, worked from the text by hand, one set per scenario. Each is read at any node that
   counts exactly the rows named. *)
Known(ids, out) == \A n \in Nodes : Ids(C(n)) = ids => Reading(n) = out
Inv_KnownEvict ==
  /\ Known({"p"}, "open")
  /\ Known({"p", "h1"}, "open")                                    \* a held row concludes nothing
  /\ Known({"p", "h1", "L1"}, "landed")                            \* the lone landing
  /\ Known({"p", "h1", "L1", "x"}, "contested")                    \* the target signed, concurrent: recounted
  /\ Known({"p", "h1", "L1", "xn"}, "landed")                      \* a row that names the landing changes nothing
  /\ Known({"p", "h1", "L1", "x", "xn"}, "contested")
  /\ Known({"p", "h1", "L1", "x", "h3", "L3"}, "refused")          \* a second landing naming both
  /\ Known({"p", "h1", "L1", "o3"}, "landed")                      \* one objection of two others
  /\ Known({"p", "h1", "L1", "w"}, "refused")                      \* the withdrawal, concurrent with the landing
  /\ Known({"p", "w"}, "refused")                                  \* the withdrawal refuses an open proposal
  /\ Known({"p", "x"}, "open")
  /\ Known({"p", "h3", "x"}, "open")
Inv_KnownCount ==
  /\ Known({"p", "a3"}, "landed")                                  \* a met count, no landing row
  /\ Known({"p", "a3", "w"}, "landed")                             \* a met approval beats the withdrawal
  /\ Known({"p", "w", "a3w"}, "refused")                           \* an approval with the withdrawal in its past
  /\ Known({"p", "w", "a3w", "a3"}, "landed")
  /\ Known({"p", "o2"}, "open")                                    \* one objection of two
  /\ Known({"p", "h1", "Le"}, "open")                              \* a landing whose span is short concludes nothing
  /\ Known({"p", "h1", "Le", "o2"}, "open")
  /\ Known({"p", "w", "h3", "Lw"}, "refused")                      \* "landed" with the withdrawal in its past concludes nothing
  /\ Known({"p", "a3", "o2"}, "landed")
Inv_KnownHeld ==
  /\ Known({"p", "x", "hb"}, "open")
  /\ Known({"p", "x", "hb", "Lb"}, "open")                         \* the held row had the target's row in its past
  /\ Known({"p", "h1", "L1", "h3", "Lx"}, "landed")                \* a landing that states what the table does not answers nothing
  /\ Known({"p", "h1", "L1", "x", "hb", "Lb"}, "contested")
Inv_KnownAdd ==
  /\ Known({"p", "h1", "L1"}, "landed")
  /\ Known({"p", "h1", "L1", "x"}, "landed")                       \* an addition asks no silence of anyone
  /\ Known({"p", "h1", "L1", "o2"}, "landed")                      \* one objection of two others does not stop it
  /\ Known({"p", "h1b", "L1o", "o2"}, "landed")                    \* nor does it when the landing counted it
  /\ Known({"p", "h1", "L1", "o2", "o3"}, "refused")               \* a strict majority of the others does
  /\ Known({"p", "o2", "o3"}, "refused")
  /\ Known({"p", "o2", "o3", "h3", "Lf"}, "refused")               \* "landed" over both objections concludes nothing
  /\ Known({"p", "h1b", "L1o", "o2", "o3"}, "refused")             \* recount: the objection in the landing's past and the concurrent one are counted together
Inv_KnownPast ==
  /\ Known({"x0", "p"}, "open")
  /\ Known({"x0", "p", "h1", "L1"}, "landed")                      \* the target's row in the proposal's own past stops nothing
  /\ Known({"x0", "p", "h1", "L1", "x"}, "contested")              \* its row after the proposal does
  /\ Known({"x0", "p", "x", "hb", "Lb"}, "open")                   \* a held row with that later row in its past
Inv_KnownWho ==
  /\ Known({"p", "h9", "L9"}, "open")                              \* a landing by a key with no seat concludes nothing
  /\ Known({"p", "h1", "Lz"}, "open")                              \* nor one that names another key's held row
  /\ Known({"p", "n1", "Ln"}, "open")                              \* nor one whose "held row" is no held row
  /\ Known({"p", "a3"}, "landed")
  /\ Known({"p", "o3"}, "open")
  /\ Known({"p", "a3", "o3"}, "open")                              \* a signer who answers both ways says nothing
\* answers that name a landing, read by the sentence "an answer that names the landing came after it and
\* changes nothing". Whether a met count made of such answers should prevail is not ruled.
Inv_KnownLate ==
  /\ Known({"p", "h1", "L1", "o2n"}, "landed")
  /\ Known({"p", "h1", "L1", "o2n", "o3n"}, "landed")              \* both others object after the landing, naming it
  /\ Known({"p", "x", "h3", "L3"}, "refused")
  /\ Known({"p", "x", "h3", "L3", "a3n"}, "refused")               \* a strict majority approves after a refusal, naming it
  /\ Known({"p", "h1", "L1", "x", "h3", "L3"}, "refused")          \* two frontier landings, one stands

(* ---- witnesses: each is the negation of a state the text names; a run must violate it ---- *)
Wit_Open      == ~\E n \in Nodes : Reading(n) = "open"
Wit_Contested == ~\E n \in Nodes : Reading(n) = "contested"
Wit_Landed    == ~\E n \in Nodes : Reading(n) = "landed" /\ GoodApprovals(C(n)) = {}
Wit_Refused   == ~\E n \in Nodes : Reading(n) = "refused" /\ Wds(C(n)) = {}
Wit_Waiting   == ~\E n \in Nodes : counted[n] # has[n]
\* the cost: a lone landing is not final. One node reads landed; another, holding those rows and one more
\* that a seated key signed without naming the landing, does not.
Wit_LoneLandingNotFinal ==
  ~\E a, b \in Nodes : has[a] \subseteq has[b] /\ Reading(a) = "landed" /\ Reading(b) = "contested"
\* the cost of an addition: it is read as landed with an objection counted
Wit_AddOneObjection ==
  ~\E n \in Nodes : Sc.kind = "add" /\ Reading(n) = "landed" /\ Cardinality(Said(C(n), "object")) = 1
\* a question for the text, shown and not ruled: the target signs a row that NAMES the landing (it came
\* after and by itself changes nothing), and a second landing that counts that row refuses the eviction
Wit_NamedRowReopens ==
  ~\E a, b \in Nodes : /\ Ids(C(a)) = {"p", "h1", "L1", "xn"} /\ Reading(a) = "landed"
                        /\ Ids(C(b)) = {"p", "h1", "L1", "xn", "h3", "L3n"} /\ Reading(b) = "refused"
\* not ruled by the text: both others object after a lone landing, each naming it, and it stays landed
Wit_LateObjectionsChangeNothing ==
  ~\E n \in Nodes : Reading(n) = "landed" /\ MetObject(C(n)) /\ ~MetApprove(C(n))
\* not ruled by the text: a strict majority approves, naming a standing refusal, and it stays refused
Wit_LateApprovalChangesNothing ==
  ~\E n \in Nodes : Reading(n) = "refused" /\ MetApprove(C(n))
\* the proposal has a row of the target in its own past and is read as landed on a lone landing
Wit_ProposalPastLanded ==
  ~\E n \in Nodes : Reading(n) = "landed" /\ \E t \in C(n) : t.by = Sc.target /\ t.id \in P0.past
\* two nodes hold different rows and differ: nothing wrong, and reachable
Wit_DifferWhileRowsDiffer == ~\E a, b \in Nodes : has[a] # has[b] /\ Reading(a) = "landed" /\ Reading(b) = "refused"
=============================================================================
