---------------------------- MODULE Membership ----------------------------
(* The membership ceremony of a family or community (CC 3.1.3.2), plane model B of
   review/notes/formal_closure_rc9_2026-10-18.md section 5.

   Admission is two consents (CC 3.1.3.2, ruling of 2026-09-30): the group's, on a cosigned
   membership:widening judged under the group's consensus_protocol (CC 3.3.4), and the joiner's
   own membership:acceptance, bound to exactly one membership:proposal by proposal_hash. The
   proposal is an invitation and carries no quorum. A removal is cosigned like a widening; a
   resignation is the leaving member's alone. A founding record seats a listed key iff that key
   signed it.

   One group, a small key set, one founding. Each invitee has at most one live proposal;
   proposals to a key are numbered (gen), so a proposal's identity (its proposal_hash) is the
   pair <<k, gen>>. A roster change is a cosigned row held in a per-target slot: one primary
   signer, cosigners added one at a time, judged on the roster as it stood at the row's instant
   (the primary's signing). A held change lands when the protocol is met, or expires after
   HoldWindow ticks (CC 3.3.4: "hold the proposal in a pending state until additional member
   signatures arrive (per a configurable window - operator policy)").

   Time is per object: a proposal ages to Window (its expires_at) and then expires; a held change
   ages to HoldWindow. Each object carries its own age and there is no clock variable; one Tick
   ages every live object at once, which is what a shared real time does, and an object at its
   window expires before time moves on.

   The adversary holds one key from Coercible from the start and signs anything that key may
   sign; a key coerced from the start may act honestly for as long as it likes, so this covers
   coercion at any later moment. Honest keys propose, answer and cosign widenings freely, and
   sign a removal only of the coerced key, so any removal of an honest member is the coerced
   key's alone.

   The bound: MaxProposals proposals and MaxChanges roster changes per behaviour; MaxGen
   proposals per invitee. Only the current proposal to a key is remembered: a new proposal to K
   waits until no change on K is held, so a held widening always names K's current proposal.

   Rule switches (the ruled values first; any other value is a must-fail twin):
     Binding      "spent"    - CC 3.1.3.2 admission (1)-(4), and a proposal seats at most once
                  "literal"  - (1)-(4) only: a proposal stays usable after it seated someone
                  "none"     - any acceptance K ever signed satisfies the widening
     RemovalRule  "protocol" | "unilateral" (the primary's signature alone removes)
     FounderBasis "active"   - founder standing judged on the roster at the instant
                  "record"   - judged on the founding record (a founder who left still counts)
     FoundingRule "signed"   | "listed" (every listed key seated, signed or not)
     HoldExpiry   TRUE       | FALSE (a held change never expires)
     UnanimousRemoval "others_majority" - a unanimous removal needs every member but the
                                          target, and those must be a strict majority of the
                                          roster (so a two-member group removes no one)
                  "others"   - every member but the target (in a two-member group, either
                               member removes the other alone) *)
EXTENDS Naturals, FiniteSets

CONSTANTS Keys, Listed, Founders, Protocol, M, Roles, Offered, Window, HoldWindow, MaxGen,
          MaxProposals, MaxChanges, Coercible,
          Binding, RemovalRule, FounderBasis, FoundingRule, HoldExpiry, UnanimousRemoval

ASSUME Protocol \in {"founder_only", "unanimous", "majority", "quorum"}
ASSUME Founders \subseteq Listed /\ Listed \subseteq Keys /\ Coercible \subseteq Keys
ASSUME Offered \in Roles
ASSUME Binding \in {"spent", "literal", "none"} /\ RemovalRule \in {"protocol", "unilateral"}
ASSUME FounderBasis \in {"active", "record"} /\ FoundingRule \in {"signed", "listed"}
ASSUME UnanimousRemoval \in {"others_majority", "others"}

VARIABLES
  formed,      \* group.formed
  active,      \* the roster: the keys whose member.stage is member
  coerced,     \* the one coerced key
  prop,        \* prop[k]: k's current proposal and the replies to it
  everAcc,     \* everAcc[k]: k has signed some acceptance (read only by the "none" twin)
  slot,        \* slot[k]: the cosigned roster change targeting k (group.quorum_change)
  applied,     \* some roster change has landed (group.quorum_change = applied)
  leaveGen,    \* leaveGen[k]: k's proposal number when k last left
  left,        \* left[k] \in {"none", "removed", "resigned"}: how k last left
  consentSeat, \* ghost: the seated keys whose seat rests on their own signature
  budget       \* [p |-> proposals issued, c |-> roster changes started]

vars == <<formed, active, coerced, prop, everAcc, slot, applied, leaveGen, left, consentSeat,
          budget>>

NoRole == "-"
(* status: "none" (never), "open", "accepted", "declined", "withdrawn", "expired",
   "closed" (ended and no longer readable by any row) *)
NoProp == [gen |-> 0, self |-> FALSE, age |-> 0, status |-> "none", acc |-> NoRole,
           spent |-> FALSE]
NoSlot == [kind |-> "none", signers |-> {}, rosterAt |-> {}, gen |-> 0, role |-> NoRole,
           age |-> 0, inTime |-> FALSE]
Held(k) == slot[k].kind # "none"
Live(k) == prop[k].status \in {"open", "accepted"}   \* signed before expires_at, not ended

(* An ended proposal that no held row names keeps only its number and whether it was declined. *)
Norm(p) == IF p.status \in {"open", "accepted"} THEN p
           ELSE [NoProp EXCEPT !.gen = p.gen,
                               !.status = IF p.status = "declined" THEN "declined" ELSE "closed"]
Settle(k, p) == IF Held(k) THEN p ELSE Norm(p)

Honest(k) == k # coerced
FoundersAt(roster) == IF FounderBasis = "active" THEN Founders \cap roster ELSE Founders
(* who may sign as a member now (under "record", a founder who left still may) *)
CanSignAsMember(s) == s \in active \/ (FounderBasis = "record" /\ formed /\ s \in Founders)

(* ---------------- the consensus_protocol (CC 3.3.4) ---------------- *)
(* majority counts the target in the roster it is a majority of (">50% of current members");
   unanimous never asks the target to sign its own removal; quorum counts any M members. *)
ProtocolMet(kind, k, signers, rosterAt) ==
  LET counted == signers \cap rosterAt
      voters  == IF kind = "remove" THEN rosterAt \ {k} ELSE rosterAt
  IN CASE Protocol = "founder_only" -> signers \cap FoundersAt(rosterAt) # {}
       [] Protocol = "unanimous"    -> /\ voters # {} /\ voters \subseteq signers
                                       /\ (kind = "remove" /\ UnanimousRemoval = "others_majority"
                                           => Cardinality(voters) * 2 > Cardinality(rosterAt))
       [] Protocol = "majority"     -> Cardinality(counted) * 2 > Cardinality(rosterAt)
       [] Protocol = "quorum"       -> Cardinality(counted) >= M

(* ---------------- what the door checks when a widening lands (CC 3.1.3.2) ---------------- *)
(* (1) an acceptance by K of the proposal the widening names, same role; (2) not declined or
   withdrawn; (3) the acceptance signed by expires_at (an acceptance is only ever signed while
   the proposal is open); (4) the widening's own instant by expires_at (inTime). *)
Bound(k) == LET sl == slot[k] IN
            /\ sl.inTime /\ sl.gen = prop[k].gen /\ sl.gen >= 1
            /\ prop[k].acc = sl.role
            /\ prop[k].status \notin {"declined", "withdrawn"}
BindingGuard(k) ==
  CASE Binding = "none"    -> everAcc[k]
    [] Binding = "literal" -> Bound(k)
    [] Binding = "spent"   -> Bound(k) /\ ~prop[k].spent

LandGuard(k) ==
  LET sl == slot[k] IN
  /\ Held(k)
  /\ IF sl.kind = "widen"
       THEN /\ k \notin active
            /\ ProtocolMet("widen", k, sl.signers, sl.rosterAt)
            /\ BindingGuard(k)
       ELSE /\ k \in active
            /\ (RemovalRule = "unilateral" \/ ProtocolMet("remove", k, sl.signers, sl.rosterAt))

Init == /\ formed = FALSE /\ active = {} /\ coerced \in Coercible
        /\ prop = [k \in Keys |-> NoProp] /\ everAcc = [k \in Keys |-> FALSE]
        /\ slot = [k \in Keys |-> NoSlot] /\ applied = FALSE
        /\ leaveGen = [k \in Keys |-> 0] /\ left = [k \in Keys |-> "none"]
        /\ consentSeat = {} /\ budget = [p |-> 0, c |-> 0]

(* ---------------- founding (CC 3.1.3.2 Founding, CC 3.2, CC 3.3.4) ---------------- *)
(* The record lists Listed; S is the set of listed keys that signed it, the founders among
   them (a founder is a bootstrapping signer). Other listed keys may decline to sign. *)
Found(S) ==
  /\ ~formed /\ Founders \subseteq S /\ S \subseteq Listed
  /\ formed' = TRUE
  /\ active' = IF FoundingRule = "signed" THEN S ELSE Listed
  /\ consentSeat' = S
  /\ UNCHANGED <<coerced, prop, everAcc, slot, applied, leaveGen, left, budget>>

(* ---------------- single-signer rows ---------------- *)
(* membership:proposal: under founder_only an active founder's, otherwise any active member's
   at the proposal's asserted_at. One live proposal per invitee. *)
Propose(by, k) ==
  /\ formed /\ budget.p < MaxProposals
  /\ IF Protocol = "founder_only" THEN by \in FoundersAt(active) /\ CanSignAsMember(by)
                                  ELSE by \in active
  /\ k \notin active /\ ~Live(k) /\ ~Held(k) /\ prop[k].gen < MaxGen
  /\ prop' = [prop EXCEPT ![k] = [NoProp EXCEPT !.gen = prop[k].gen + 1, !.self = (by = k),
                                                !.status = "open"]]
  /\ budget' = [budget EXCEPT !.p = @ + 1]
  /\ UNCHANGED <<formed, active, coerced, everAcc, slot, applied, leaveGen, left, consentSeat>>

(* membership:acceptance: the invitee's only, restating the role (honestly, the one offered).
   A second, opposite reply to one proposal is refused (membership_reply_conflict). *)
Accept(k, r) ==
  /\ prop[k].status = "open" /\ (Honest(k) => r = Offered)
  /\ prop' = [prop EXCEPT ![k].status = "accepted", ![k].acc = r]
  /\ everAcc' = [everAcc EXCEPT ![k] = (Binding = "none")]
  /\ UNCHANGED <<formed, active, coerced, slot, applied, leaveGen, left, consentSeat, budget>>

Decline(k) ==
  /\ prop[k].status = "open"
  /\ prop' = [prop EXCEPT ![k] = Settle(k, [@ EXCEPT !.status = "declined"])]
  /\ UNCHANGED <<formed, active, coerced, everAcc, slot, applied, leaveGen, left, consentSeat,
                 budget>>

(* the inviter's ordinary withdraws of its proposal (a withdrawn proposal counts as expired) *)
Withdraw(k) ==
  /\ Live(k)
  /\ prop' = [prop EXCEPT ![k] = Settle(k, [@ EXCEPT !.status = "withdrawn"])]
  /\ UNCHANGED <<formed, active, coerced, everAcc, slot, applied, leaveGen, left, consentSeat,
                 budget>>

DueProp(k)   == Live(k) /\ prop[k].age = Window
DueChange(k) == HoldExpiry /\ Held(k) /\ slot[k].age = HoldWindow

ExpireProp(k) ==
  /\ DueProp(k)
  /\ prop' = [prop EXCEPT ![k] = Settle(k, [@ EXCEPT !.status = "expired"])]
  /\ UNCHANGED <<formed, active, coerced, everAcc, slot, applied, leaveGen, left, consentSeat,
                 budget>>

(* membership:resignation: the leaving member's alone *)
Resign(k) ==
  /\ k \in active
  /\ active' = active \ {k} /\ consentSeat' = consentSeat \ {k}
  /\ leaveGen' = [leaveGen EXCEPT ![k] = prop[k].gen]
  /\ left' = [left EXCEPT ![k] = "resigned"]
  /\ UNCHANGED <<formed, coerced, prop, everAcc, slot, applied, budget>>

(* ---------------- cosigned rows: widening and removal ---------------- *)
(* The primary signs; that instant fixes the roster the protocol is judged on. inTime records
   whether the widening's instant was by the proposal's expires_at (rule 4); only the "none"
   twin starts a widening without a live proposal. An honest primary names the offered role. *)
StartWiden(s, k, r) ==
  /\ formed /\ budget.c < MaxChanges
  /\ CanSignAsMember(s) /\ k \notin active /\ ~Held(k)
  /\ (Binding # "none" => Live(k))
  /\ (Honest(s) => r = Offered)
  /\ slot' = [slot EXCEPT ![k] = [kind |-> "widen", signers |-> {s}, rosterAt |-> active,
                                  gen |-> prop[k].gen, role |-> r, age |-> 0,
                                  inTime |-> Live(k)]]
  /\ budget' = [budget EXCEPT !.c = @ + 1]
  /\ UNCHANGED <<formed, active, coerced, prop, everAcc, applied, leaveGen, left, consentSeat>>

StartRemove(s, k) ==
  /\ formed /\ budget.c < MaxChanges
  /\ CanSignAsMember(s) /\ k \in active /\ k # s /\ ~Held(k)
  /\ (Honest(s) => k = coerced)
  /\ slot' = [slot EXCEPT ![k] = [NoSlot EXCEPT !.kind = "remove", !.signers = {s},
                                                !.rosterAt = active]]
  /\ budget' = [budget EXCEPT !.c = @ + 1]
  /\ UNCHANGED <<formed, active, coerced, prop, everAcc, applied, leaveGen, left, consentSeat>>

(* A cosigner is still able to sign as a member and was on the roster at the row's instant
   (or, under "record", is a founder). Honest keys cosign widenings and only the coerced key's
   removal. *)
Cosign(s, k) ==
  /\ Held(k) /\ s \notin slot[k].signers /\ CanSignAsMember(s)
  /\ s \in slot[k].rosterAt \cup FoundersAt(slot[k].rosterAt)
  /\ (Honest(s) /\ slot[k].kind = "remove" => k = coerced)
  /\ slot' = [slot EXCEPT ![k].signers = @ \cup {s}]
  /\ UNCHANGED <<formed, active, coerced, prop, everAcc, applied, leaveGen, left, consentSeat,
                 budget>>

Land(k) ==
  /\ LandGuard(k)
  /\ slot' = [slot EXCEPT ![k] = NoSlot] /\ applied' = TRUE
  /\ IF slot[k].kind = "widen"
       THEN /\ active' = active \cup {k}
            /\ prop' = [prop EXCEPT ![k] = Norm([@ EXCEPT !.spent = TRUE])]
            /\ consentSeat' = IF prop[k].gen = slot[k].gen /\ prop[k].acc # NoRole
                                THEN consentSeat \cup {k} ELSE consentSeat
            /\ UNCHANGED <<leaveGen, left>>
       ELSE /\ active' = active \ {k} /\ consentSeat' = consentSeat \ {k}
            /\ prop' = [prop EXCEPT ![k] = Norm(@)]
            /\ leaveGen' = [leaveGen EXCEPT ![k] = prop[k].gen]
            /\ left' = [left EXCEPT ![k] = "removed"]
  /\ UNCHANGED <<formed, coerced, everAcc, budget>>

ExpireChange(k) ==
  /\ DueChange(k)
  /\ slot' = [slot EXCEPT ![k] = NoSlot]
  /\ prop' = [prop EXCEPT ![k] = Norm(@)]
  /\ UNCHANGED <<formed, active, coerced, everAcc, applied, leaveGen, left, consentSeat, budget>>

Tick ==
  /\ \A k \in Keys : ~DueProp(k) /\ ~DueChange(k)
  /\ \E k \in Keys : Live(k) \/ (Held(k) /\ slot[k].age < HoldWindow)
  /\ prop' = [k \in Keys |-> IF Live(k) THEN [prop[k] EXCEPT !.age = @ + 1] ELSE prop[k]]
  /\ slot' = [k \in Keys |-> IF Held(k) /\ slot[k].age < HoldWindow
                              THEN [slot[k] EXCEPT !.age = @ + 1] ELSE slot[k]]
  /\ UNCHANGED <<formed, active, coerced, everAcc, applied, leaveGen, left, consentSeat, budget>>

Next ==
  \/ \E S \in SUBSET Listed : Found(S)
  \/ \E by, k \in Keys : Propose(by, k)
  \/ \E k \in Keys, r \in Roles : Accept(k, r) \/ \E s \in Keys : StartWiden(s, k, r)
  \/ \E k \in Keys : Decline(k) \/ Withdraw(k) \/ ExpireProp(k) \/ Resign(k)
                     \/ Land(k) \/ ExpireChange(k)
  \/ \E s, k \in Keys : StartRemove(s, k) \/ Cosign(s, k)
  \/ Tick

(* Fairness is time only: ticks keep coming and a due object expires. No signer must act. *)
Spec == Init /\ [][Next]_vars /\ WF_vars(Tick)
        /\ \A k \in Keys : WF_vars(ExpireProp(k)) /\ WF_vars(ExpireChange(k))

(* ---------------- the STATE_TABLE plane=membership vocabulary ---------------- *)
Stage(k) ==   \* member.stage
  CASE k \in active                                                 -> "member"
    [] prop[k].status = "open"                                      -> "proposed"
    [] prop[k].status = "accepted"
       \/ (slot[k].kind = "widen" /\ prop[k].acc # NoRole)          -> "accepted_awaiting_group"
    [] prop[k].status = "declined"                                  -> "declined"
    [] left[k] = "removed"                                          -> "removed"
    [] left[k] = "resigned"                                         -> "resigned"
    [] OTHER                                                        -> "none"
QuorumChange ==   \* group.quorum_change
  IF \E k \in Keys : Held(k) THEN "held" ELSE IF applied THEN "applied" ELSE "none"

TypeOK ==
  /\ formed \in BOOLEAN /\ active \subseteq Keys /\ coerced \in Coercible
  /\ \A k \in Keys :
       /\ prop[k].gen \in 0..MaxGen /\ prop[k].age \in 0..Window
       /\ prop[k].status \in {"none", "open", "accepted", "declined", "withdrawn", "expired",
                              "closed"}
       /\ prop[k].acc \in Roles \cup {NoRole}
       /\ slot[k].kind \in {"none", "widen", "remove"} /\ slot[k].age \in 0..HoldWindow
       /\ Stage(k) \in {"none", "proposed", "accepted_awaiting_group", "declined", "member",
                        "removed", "resigned"}
  /\ QuorumChange \in {"none", "held", "applied"}

(* ---------------- properties ---------------- *)
(* Landing steps; the Inv_ properties over them are action invariants, checked on every step. *)
Lands(k, kind) == slot[k].kind = kind /\ Land(k)

(* CC 3.1.3.2 Admission (1)-(4): a seat comes only from an acceptance of the very proposal the
   widening names, with the same role, both signed by its expires_at, and not withdrawn. *)
Inv_AcceptanceBindsOneProposal ==
  [][\A k \in Keys : Lands(k, "widen") =>
       /\ slot[k].inTime /\ slot[k].gen >= 1 /\ slot[k].gen = prop[k].gen
       /\ prop[k].acc = slot[k].role /\ prop[k].status # "withdrawn"]_vars

(* CC 3.1.3.2 Decline: a declined proposal never seats; asking again is a new proposal. *)
Inv_DeclineTerminal ==
  [][\A k \in Keys : Lands(k, "widen") =>
       ~(slot[k].gen = prop[k].gen /\ prop[k].status = "declined")]_vars

(* CC 3.1.3.2: no key is seated on rows it alone signed (its proposal and its widening).
   Founding is the stated exception: there, signing is consent. *)
Inv_NoSelfAdmission ==
  [][\A k \in Keys : Lands(k, "widen") =>
       \/ slot[k].signers \ {k} # {}
       \/ (slot[k].gen = prop[k].gen /\ slot[k].gen >= 1 /\ ~prop[k].self)]_vars

(* CC 3.1.3.2 / CC 3.3.4: every widening and removal that lands meets the protocol on the
   roster at the row's instant. *)
Inv_QuorumGovernsRoster ==
  [][\A k \in Keys : (Lands(k, "widen") \/ Lands(k, "remove")) =>
       ProtocolMet(slot[k].kind, k, slot[k].signers, slot[k].rosterAt)]_vars

(* One coerced key never removes an honest member. *)
Inv_CoercedCannotRemoveHonest ==
  [][\A k \in Keys : Lands(k, "remove") => k = coerced]_vars

(* A member can always resign, alone, now. *)
Inv_ResignationEnabled == \A k \in active : ENABLED Resign(k)

(* Leaving (resignation or removal) is undone only by a proposal issued after the leaving. *)
Inv_LeavingNotUndone ==
  [][\A k \in Keys : Lands(k, "widen") => slot[k].gen > leaveGen[k]]_vars

(* The CC 3.1.3.2 ruling: every seated key is seated on its own signature. *)
Inv_JoinerConsented == active \subseteq consentSeat

(* CC 3.1.3.2 expires_at: no proposal is open past its window, no change held past its own. *)
Inv_ExpiryBound == \A k \in Keys : /\ Live(k) => prop[k].age <= Window
                                   /\ Held(k) => slot[k].age <= HoldWindow

(* group.quorum_change: a held change applies or expires. *)
Prop_HeldChangeResolves == \A k \in Keys : Held(k) ~> ~Held(k)
=============================================================================
