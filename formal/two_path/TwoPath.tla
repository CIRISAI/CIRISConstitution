---------------------------- MODULE TwoPath ----------------------------
(* The two-path decision, generalized (CC 4.5.13): every governance change
   runs under one policy  (Enact, Cancel, Window, Irreversible)  over a standing set of N voters.

     forward path   — the change lands at once when approvals reach the ENACT threshold;
     reverse path   — otherwise it lands when its Window closes unless objections reached the
                      CANCEL threshold; a cancelled change is void;
     irreversible   — a change whose effect cannot be undone has NO instant landing: it waits
                      its whole Window even with every approval, so the reverse path always has
                      its chance (secrets destroyed, a hard delete, a key destroyed).

   Thresholds are fractions of the STANDING set N (m-of-n, scalable), with Cancel ≤ Enact:
   e.g. enact at 2/3, cancel at 1/3, window by sensitivity. The self roster (CC 3.3.6.3) is the
   instance Enact = strict majority, Cancel = strict majority of the others, Window = W_self,
   reversible; the constitutional halt's confirmation (4.2.1.1) is the mirror image — a floor-of-
   one FIRE that lapses unless a majority confirms within the fuse — and is modelled in
   formal/accord_halt; TwoPath_halt_mirror.cfg shows the mirror as this module's parameters.

   Votes are cast by voters; an adversary holds Coerced voters who approve what the adversary
   proposes and object to what it does not. Time is per proposal (age), no clock. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Voters,        \* the standing set, |Voters| = N
          Coerced,       \* voters the adversary holds
          Silent,        \* voters who never answer (the inactive part of a large community)
          EnactNum, EnactDen,      \* enact threshold as a fraction: approvals * Den > Num * N  (strict) ...
          CancelNum, CancelDen,    \* ... objections * Den >= Num * N  (at least)
          FloorNum, FloorDen,      \* the reverse path lands only with approvals * Den >= Num * N: silence alone never admits
          Window,        \* ticks a proposal lives before the reverse path decides it
          Irreversible,  \* TRUE: no instant landing
          ReversePath,   \* FALSE: the door is forward only; the window closing never lands anything
          MinCount,      \* cancel and floor count no fewer voices than this (2 for a community, 1 for a self)
          MaxChanges     \* changes per behaviour (the bound)

ASSUME Coerced \subseteq Voters
ASSUME Silent \subseteq Voters /\ Silent \cap Coerced = {}
ASSUME CancelNum * EnactDen <= EnactNum * CancelDen   \* Cancel ≤ Enact
ASSUME FloorNum * EnactDen <= EnactNum * FloorDen     \* Floor ≤ Enact (a floor at Enact switches the reverse path off)

N == Cardinality(Voters)
Honest == Voters \ Coerced
Active == Voters \ Silent          \* who will ever answer
HonestActive == Honest \ Silent

VARIABLES
  pending,     \* the one open proposal: [by, age, approvers, objectors, adversarial] or none
  landed,      \* how many adversarial changes landed
  honestLanded,\* how many honest changes landed
  cancelled,   \* how many honest changes were cancelled
  wrong,       \* an adversarial change landed although honest objections reached Cancel
  lone         \* a change landed carrying exactly one approval: one voice admitted

vars == <<pending, landed, honestLanded, cancelled, wrong, lone>>

None == [by |-> "none"]
Open == pending # None

EnactReached(p)  == Cardinality(p.approvers) * EnactDen > EnactNum * N
CancelReached(p) == Cardinality(p.objectors) >= MinCount /\ Cardinality(p.objectors) * CancelDen >= CancelNum * N
FloorReached(p)  == Cardinality(p.approvers) >= MinCount /\ Cardinality(p.approvers) * FloorDen >= FloorNum * N

Init == /\ pending = None /\ landed = 0 /\ honestLanded = 0 /\ cancelled = 0 /\ wrong = FALSE /\ lone = FALSE

(* a voter proposes; the proposer approves; a coerced proposer's change is adversarial *)
Propose(v) == /\ ~Open /\ landed + honestLanded + cancelled < MaxChanges
              /\ pending' = [by |-> v, age |-> 0, approvers |-> {v}, objectors |-> {}, adversarial |-> (v \in Coerced)]
              /\ UNCHANGED <<landed, honestLanded, cancelled, wrong, lone>>

(* every voter answers once: honest approve honest changes and object to adversarial ones;
   coerced do the reverse *)
Wants(v, p) == IF v \in Coerced THEN p.adversarial ELSE ~p.adversarial
Answer(v) == /\ Open /\ v \in Active /\ v \notin pending.approvers /\ v \notin pending.objectors
             /\ pending' = IF Wants(v, pending)
                           THEN [pending EXCEPT !.approvers = @ \cup {v}]
                           ELSE [pending EXCEPT !.objectors = @ \cup {v}]
             /\ UNCHANGED <<landed, honestLanded, cancelled, wrong, lone>>

(* forward path: lands at once at Enact — unless irreversible *)
LandForward == /\ Open /\ ~Irreversible /\ EnactReached(pending)
               /\ landed' = IF pending.adversarial THEN landed + 1 ELSE landed
               /\ honestLanded' = IF pending.adversarial THEN honestLanded ELSE honestLanded + 1
               /\ wrong' = wrong \/ (pending.adversarial /\ CancelReached(pending))
               /\ lone' = (lone \/ Cardinality(pending.approvers) = 1)
               /\ pending' = None /\ UNCHANGED cancelled

(* the window closes: cancelled if objections reached Cancel; else lands if approvals reached Enact
   (the forward path that waited, or was not taken before the window) or — on a door with a reverse
   path — reached the Floor (silence alone never admits); else cancelled *)
WindowCloses == /\ Open /\ pending.age >= Window
                /\ IF CancelReached(pending) \/ ~(EnactReached(pending) \/ (ReversePath /\ FloorReached(pending)))
                   THEN /\ cancelled' = IF pending.adversarial THEN cancelled ELSE cancelled + 1
                        /\ UNCHANGED <<landed, honestLanded, wrong, lone>>
                   ELSE /\ landed' = IF pending.adversarial THEN landed + 1 ELSE landed
                        /\ honestLanded' = IF pending.adversarial THEN honestLanded ELSE honestLanded + 1
                        /\ wrong' = wrong \/ pending.adversarial   \* adversarial change landed by silence
                        /\ lone' = (lone \/ Cardinality(pending.approvers) = 1)
                        /\ UNCHANGED cancelled
                /\ pending' = None

(* the window ages only after every honest voter who will answer has answered (the owner-present
   reading); the silent never answer, so the window runs past them *)
Tick == /\ Open /\ pending.age < Window
        /\ \A v \in HonestActive : v \in pending.approvers \/ v \in pending.objectors
        /\ pending' = [pending EXCEPT !.age = @ + 1]
        /\ UNCHANGED <<landed, honestLanded, cancelled, wrong, lone>>

Next == \/ \E v \in Voters : Propose(v) \/ Answer(v)
        \/ LandForward \/ WindowCloses \/ Tick

Spec == Init /\ [][Next]_vars /\ WF_vars(Next)

(* ---------------- what the policy promises ---------------- *)
\* a coerced minority below Cancel never blocks an honest change the active honest can floor
Inv_AdversaryBelowCancelCannotBlock ==
  (Cardinality(Coerced) * CancelDen < CancelNum * N /\ Cardinality(HonestActive) * FloorDen >= FloorNum * N) => cancelled = 0
\* one voice never admits by either path: with a floor above one voter (and enact above one),
\* no change ever lands on a single approval however many voters stay silent
Inv_OneVoiceNeverAdmits ==
  ((FloorNum * N > FloorDen \/ MinCount >= 2) /\ EnactNum * N >= EnactDen) => lone = FALSE
\* an active honest set at or above Cancel always stops an adversarial change: nothing adversarial lands
Inv_HonestAtCancelStopsAdversary ==
  (Cardinality(HonestActive) * CancelDen >= CancelNum * N) => landed = 0
\* unconditional form, for the twins: no change ever lands on one approval
Inv_NoLoneLanding == lone = FALSE
\* below the floor the reverse path admits nothing: with the active honest below the floor and the
\* coerced below enact, nothing lands at all (the silent community is not spoken for)
Inv_BelowFloorNothingLands ==
  (Cardinality(Active) * FloorDen < FloorNum * N) => landed + honestLanded = 0
\* the floor is a reverse-path predicate only: a landing before the window closes is a forward landing
\* at Enact, never a floored one (CC 4.5.13: the floor still requires the time to expire)
Prop_FloorNeverLandsEarly ==
  [][((landed' + honestLanded' > landed + honestLanded) /\ pending.age < Window) => EnactReached(pending)]_vars
\* an irreversible change never lands before its window: every landing happens at the window
Prop_IrreversibleWaits ==
  [][Irreversible => ((landed' + honestLanded' > landed + honestLanded) => pending.age >= Window)]_vars
\* liveness: an honest set above Enact lands its change
HonestOpen == Open /\ ~pending.adversarial
Prop_HonestChangeResolves == [](HonestOpen => <>(~Open))   \* every honest proposal is decided; with the coerced below Cancel, Inv_AdversaryBelowCancelCannotBlock makes that decision a landing
=============================================================================
