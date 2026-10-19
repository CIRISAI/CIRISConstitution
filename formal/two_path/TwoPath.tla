---------------------------- MODULE TwoPath ----------------------------
(* The two-path decision, generalized (steward direction 2026-10-18): every governance change
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
          EnactNum, EnactDen,      \* enact threshold as a fraction: approvals * Den > Num * N  (strict) ...
          CancelNum, CancelDen,    \* ... objections * Den >= Num * N  (at least)
          Window,        \* ticks a proposal lives before the reverse path decides it
          Irreversible,  \* TRUE: no instant landing
          MaxChanges     \* changes per behaviour (the bound)

ASSUME Coerced \subseteq Voters
ASSUME CancelNum * EnactDen <= EnactNum * CancelDen   \* Cancel ≤ Enact

N == Cardinality(Voters)
Honest == Voters \ Coerced

VARIABLES
  pending,     \* the one open proposal: [by, age, approvers, objectors, adversarial] or none
  landed,      \* how many adversarial changes landed
  honestLanded,\* how many honest changes landed
  cancelled,   \* how many honest changes were cancelled
  wrong        \* an adversarial change landed although honest objections reached Cancel

vars == <<pending, landed, honestLanded, cancelled, wrong>>

None == [by |-> "none"]
Open == pending # None

EnactReached(p)  == Cardinality(p.approvers) * EnactDen > EnactNum * N
CancelReached(p) == Cardinality(p.objectors) * CancelDen >= CancelNum * N

Init == /\ pending = None /\ landed = 0 /\ honestLanded = 0 /\ cancelled = 0 /\ wrong = FALSE

(* a voter proposes; the proposer approves; a coerced proposer's change is adversarial *)
Propose(v) == /\ ~Open /\ landed + honestLanded + cancelled < MaxChanges
              /\ pending' = [by |-> v, age |-> 0, approvers |-> {v}, objectors |-> {}, adversarial |-> (v \in Coerced)]
              /\ UNCHANGED <<landed, honestLanded, cancelled, wrong>>

(* every voter answers once: honest approve honest changes and object to adversarial ones;
   coerced do the reverse *)
Wants(v, p) == IF v \in Coerced THEN p.adversarial ELSE ~p.adversarial
Answer(v) == /\ Open /\ v \notin pending.approvers /\ v \notin pending.objectors
             /\ pending' = IF Wants(v, pending)
                           THEN [pending EXCEPT !.approvers = @ \cup {v}]
                           ELSE [pending EXCEPT !.objectors = @ \cup {v}]
             /\ UNCHANGED <<landed, honestLanded, cancelled, wrong>>

(* forward path: lands at once at Enact — unless irreversible *)
LandForward == /\ Open /\ ~Irreversible /\ EnactReached(pending)
               /\ landed' = IF pending.adversarial THEN landed + 1 ELSE landed
               /\ honestLanded' = IF pending.adversarial THEN honestLanded ELSE honestLanded + 1
               /\ wrong' = wrong \/ (pending.adversarial /\ CancelReached(pending))
               /\ pending' = None /\ UNCHANGED cancelled

(* reverse path: the window closes; cancelled if objections reached Cancel, else lands *)
WindowCloses == /\ Open /\ pending.age >= Window
                /\ IF CancelReached(pending)
                   THEN /\ cancelled' = IF pending.adversarial THEN cancelled ELSE cancelled + 1
                        /\ UNCHANGED <<landed, honestLanded, wrong>>
                   ELSE /\ landed' = IF pending.adversarial THEN landed + 1 ELSE landed
                        /\ honestLanded' = IF pending.adversarial THEN honestLanded ELSE honestLanded + 1
                        /\ wrong' = wrong \/ pending.adversarial   \* adversarial change landed by silence
                        /\ UNCHANGED cancelled
                /\ pending' = None

(* the window ages only after every voter present has answered (the owner-present reading) *)
Tick == /\ Open /\ pending.age < Window
        /\ \A v \in Honest : v \in pending.approvers \/ v \in pending.objectors
        /\ pending' = [pending EXCEPT !.age = @ + 1]
        /\ UNCHANGED <<landed, honestLanded, cancelled, wrong>>

Next == \/ \E v \in Voters : Propose(v) \/ Answer(v)
        \/ LandForward \/ WindowCloses \/ Tick

Spec == Init /\ [][Next]_vars /\ WF_vars(Next)

(* ---------------- what the policy promises ---------------- *)
\* a coerced minority below Cancel never blocks an honest change
Inv_AdversaryBelowCancelCannotBlock ==
  (Cardinality(Coerced) * CancelDen < CancelNum * N) => cancelled = 0
\* an honest set at or above Cancel always stops an adversarial change: nothing adversarial lands
Inv_HonestAtCancelStopsAdversary ==
  (Cardinality(Honest) * CancelDen >= CancelNum * N) => landed = 0
\* an irreversible change never lands before its window: every landing happens at the window
Prop_IrreversibleWaits ==
  [][Irreversible => ((landed' + honestLanded' > landed + honestLanded) => pending.age >= Window)]_vars
\* liveness: an honest set above Enact lands its change
HonestOpen == Open /\ ~pending.adversarial
Prop_HonestChangeResolves == [](HonestOpen => <>(~Open))   \* every honest proposal is decided; with the coerced below Cancel, Inv_AdversaryBelowCancelCannotBlock makes that decision a landing
=============================================================================
