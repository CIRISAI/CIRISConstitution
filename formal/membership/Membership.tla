---------------------------- MODULE Membership ----------------------------
(* The membership ceremony of a family or community (CC 3.1.3.2), plane model B of
   review/notes/formal_closure_rc9_2026-10-18.md section 5.

   Admission is two consents (CC 3.1.3.2, ruling of 2026-09-30): the group's, on a cosigned
   membership:widening judged under the group's consensus_protocol (CC 3.3.4), and the joiner's
   own membership:acceptance, bound to exactly one membership:proposal by proposal_hash. The
   proposal is an invitation and carries no quorum. A removal is cosigned like a widening; a
   resignation is the leaving member's alone. A founding record seats a listed key iff that key
   signed it.

   One group, a small key set, one founding. Each key has at most one live proposal at a time;
   proposals are numbered per invitee (gen), so a proposal's identity (its hash) is the pair
   <<k, gen>>. Roster changes are cosigned rows held in a per-target slot: one primary signer,
   cosigners added one at a time, judged on the roster as it stood at the row's instant (the
   primary's signing). A held change lands when the protocol is met, or expires after HoldWindow
   ticks of its own age (CC 3.3.4: "hold the proposal in a pending state until additional member
   signatures arrive (per a configurable window - operator policy)").

   Time is per object: a proposal ages to Window (its expires_at) and then expires; a held change
   ages to HoldWindow. There is no global clock; independent ageing over-approximates every
   relative ordering of instants, which is sound for the safety properties.

   The adversary holds one key from Coercible from the start and signs anything that key may
   sign; a key coerced from the start can act honestly for as long as it likes, so this covers
   coercion at any later moment. Honest keys propose, answer and cosign widenings freely, and sign
   a removal only of the coerced key (so any removal of an honest member is the adversary's alone).

   Rule switches (the ruled values first; any other value is a must-fail twin):
     Binding      "spent"    - CC 3.1.3.2 admission (1)-(4), and a proposal seats at most once
                  "literal"  - (1)-(4) only: a proposal stays usable after it seated someone
                  "none"     - any acceptance ever signed by K satisfies the widening
     RemovalRule  "protocol" | "unilateral" (the primary's signature alone removes)
     FounderBasis "active"   - founder standing judged on the roster at the instant
                  "record"   - judged on the founding record (a founder who left still counts)
     FoundingRule "signed"   | "listed" (every listed key seated, signed or not)
     HoldExpiry   TRUE       | FALSE (a held change never expires) *)
EXTENDS Naturals, FiniteSets

CONSTANTS Keys, Listed, Founders, Protocol, M, Roles, Window, HoldWindow, MaxGen,
          Coercible, Binding, RemovalRule, FounderBasis, FoundingRule, HoldExpiry, NoKey

ASSUME Protocol \in {"founder_only", "unanimous", "majority", "quorum"}
ASSUME Founders \subseteq Listed /\ Listed \subseteq Keys /\ Coercible \subseteq Keys
ASSUME Binding \in {"spent", "literal", "none"} /\ RemovalRule \in {"protocol", "unilateral"}
ASSUME FounderBasis \in {"active", "record"} /\ FoundingRule \in {"signed", "listed"}
ASSUME NoKey \notin Keys

VARIABLES
  formed,      \* group.formed
  active,      \* the roster: keys whose member.stage = member
  coerced,     \* the one coerced key, or NoKey
  prop,        \* prop[k]: k's latest proposal (gen 0 = none ever)
  hist,        \* every proposal issued: [k, gen, role, by]
  acc,         \* every acceptance signed: [k, gen, role]   (role restated)
  declined,    \* every decline: <<k, gen>>
  withdrawn,   \* every withdrawal by the inviter: <<k, gen>>
  spent,       \* proposals that seated their invitee: <<k, gen>>
  slot,        \* slot[k]: the cosigned roster change targeting k
  leaveGen,    \* leaveGen[k]: k's proposal counter when k last left (removed or resigned)
  left,        \* left[k] \in {"none","removed","resigned"}: how k last left
  consentSeat  \* ghost: active keys whose current seat rests on their own signature

vars == <<formed, active, coerced, prop, hist, acc, declined, withdrawn, spent, slot,
          leaveGen, left, consentSeat>>

PStatus == {"none", "open", "accepted", "declined", "withdrawn", "expired"}
Live(k) == prop[k].status \in {"open", "accepted"}     \* not past expires_at, not answered no
NoProp  == [gen |-> 0, by |-> NoKey, role |-> "none", age |-> 0, status |-> "none"]
NoSlot  == [kind |-> "none", status |-> "none", by |-> NoKey, signers |-> {},
            rosterAt |-> {}, foundersAt |-> {}, gen |-> 0, role |-> "none", age |-> 0,
            inTime |-> FALSE]

Honest(k) == k # coerced
(* A proposal that is no longer live keeps only its number and how it ended; who signed it and
   the role it offered stay in hist. A finished roster change keeps only how it ended. *)
Closed(p, st) == [NoProp EXCEPT !.gen = p.gen, !.status = st]
SeatedFounders == IF FounderBasis = "active" THEN Founders \cap active ELSE Founders
\* who may sign as a member at this instant (a founder who left still may, under "record")
CanSignAsMember(s) == s \in active \/ (FounderBasis = "record" /\ s \in Founders /\ formed)

(* ---------------- the consensus_protocol (CC 3.3.4) ---------------- *)
ProtocolMet(kind, k, signers, rosterAt, foundersAt) ==
  LET counted == signers \cap rosterAt
      voters  == IF kind = "remove" THEN rosterAt \ {k} ELSE rosterAt
  IN CASE Protocol = "founder_only" -> signers \cap foundersAt # {}
       [] Protocol = "unanimous"    -> voters # {} /\ voters \subseteq signers
       [] Protocol = "majority"     -> Cardinality(counted) * 2 > Cardinality(rosterAt)
       [] Protocol = "quorum"       -> Cardinality(counted) >= M

(* ---------------- what the door checks at landing ---------------- *)
Accepted(k, g, r) == [k |-> k, gen |-> g, role |-> r] \in acc
AcceptedAny(k, g) == \E r \in Roles : Accepted(k, g, r)
Issued(k, g, r)   == \E b \in Keys : [k |-> k, gen |-> g, role |-> r, by |-> b] \in hist

BindingGuard(k, sl) ==
  CASE Binding = "none"    -> \E g \in 1..MaxGen : AcceptedAny(k, g)
    [] Binding = "literal" -> /\ sl.inTime
                              /\ Issued(k, sl.gen, sl.role) /\ Accepted(k, sl.gen, sl.role)
                              /\ <<k, sl.gen>> \notin declined \cup withdrawn
    [] Binding = "spent"   -> /\ sl.inTime
                              /\ Issued(k, sl.gen, sl.role) /\ Accepted(k, sl.gen, sl.role)
                              /\ <<k, sl.gen>> \notin declined \cup withdrawn \cup spent

LandGuard(k) ==
  LET sl == slot[k] IN
  /\ sl.status = "held"
  /\ IF sl.kind = "widen"
       THEN /\ k \notin active
            /\ ProtocolMet("widen", k, sl.signers, sl.rosterAt, sl.foundersAt)
            /\ BindingGuard(k, sl)
       ELSE /\ k \in active
            /\ (RemovalRule = "unilateral"
                \/ ProtocolMet("remove", k, sl.signers, sl.rosterAt, sl.foundersAt))

Init == /\ formed = FALSE /\ active = {} /\ coerced \in Coercible
        /\ prop = [k \in Keys |-> NoProp]
        /\ hist = {} /\ acc = {} /\ declined = {} /\ withdrawn = {} /\ spent = {}
        /\ slot = [k \in Keys |-> NoSlot]
        /\ leaveGen = [k \in Keys |-> 0] /\ left = [k \in Keys |-> "none"]
        /\ consentSeat = {}

(* ---------------- founding (CC 3.1.3.2 Founding, CC 3.2, CC 3.3.4) ---------------- *)
(* The founding record lists Listed; S is the set of listed keys that signed it, at least one
   founder (the authority) among them. Honest listed keys may decline to sign. *)
Found(S) ==
  /\ ~formed /\ S \subseteq Listed /\ S \cap Founders # {}
  /\ formed' = TRUE
  /\ active' = IF FoundingRule = "signed" THEN S ELSE Listed
  /\ consentSeat' = S
  /\ UNCHANGED <<coerced, prop, hist, acc, declined, withdrawn, spent, slot, leaveGen, left>>

(* ---------------- single-signer rows ---------------- *)
(* membership:proposal by an inviter: under founder_only an active founder, otherwise any
   active member at the proposal's asserted_at. One live proposal per invitee. *)
Propose(by, k, r) ==
  /\ formed
  /\ IF Protocol = "founder_only" THEN by \in SeatedFounders /\ CanSignAsMember(by)
                                  ELSE by \in active
  /\ k \notin active /\ ~Live(k) /\ prop[k].gen < MaxGen
  /\ prop' = [prop EXCEPT ![k] = [gen |-> @.gen + 1, by |-> by, role |-> r, age |-> 0,
                                  status |-> "open"]]
  /\ hist' = hist \cup {[k |-> k, gen |-> prop[k].gen + 1, role |-> r, by |-> by]}
  /\ UNCHANGED <<formed, active, coerced, acc, declined, withdrawn, spent, slot, leaveGen,
                 left, consentSeat>>

(* membership:acceptance - the invitee's only; restates the role (honestly, the offered one).
   A second, opposite reply to the same proposal is refused (membership_reply_conflict). *)
Accept(k, r) ==
  /\ prop[k].status = "open"
  /\ (Honest(k) => r = prop[k].role)
  /\ acc' = acc \cup {[k |-> k, gen |-> prop[k].gen, role |-> r]}
  /\ prop' = [prop EXCEPT ![k].status = "accepted"]
  /\ UNCHANGED <<formed, active, coerced, hist, declined, withdrawn, spent, slot, leaveGen,
                 left, consentSeat>>

Decline(k) ==
  /\ prop[k].status = "open"
  /\ declined' = declined \cup {<<k, prop[k].gen>>}
  /\ prop' = [prop EXCEPT ![k] = Closed(@, "declined")]
  /\ UNCHANGED <<formed, active, coerced, hist, acc, withdrawn, spent, slot, leaveGen, left,
                 consentSeat>>

(* the inviter's ordinary withdraws of its proposal *)
Withdraw(k) ==
  /\ Live(k)
  /\ withdrawn' = withdrawn \cup {<<k, prop[k].gen>>}
  /\ prop' = [prop EXCEPT ![k] = Closed(@, "withdrawn")]
  /\ UNCHANGED <<formed, active, coerced, hist, acc, declined, spent, slot, leaveGen, left,
                 consentSeat>>

AgeProp(k)    == /\ Live(k) /\ prop[k].age < Window
                 /\ prop' = [prop EXCEPT ![k].age = @ + 1]
                 /\ UNCHANGED <<formed, active, coerced, hist, acc, declined, withdrawn, spent,
                                slot, leaveGen, left, consentSeat>>
ExpireProp(k) == /\ Live(k) /\ prop[k].age = Window
                 /\ prop' = [prop EXCEPT ![k] = Closed(@, "expired")]
                 /\ UNCHANGED <<formed, active, coerced, hist, acc, declined, withdrawn, spent,
                                slot, leaveGen, left, consentSeat>>

(* membership:resignation - the leaving member's alone *)
Resign(k) ==
  /\ k \in active
  /\ active' = active \ {k} /\ consentSeat' = consentSeat \ {k}
  /\ leaveGen' = [leaveGen EXCEPT ![k] = prop[k].gen]
  /\ left' = [left EXCEPT ![k] = "resigned"]
  /\ UNCHANGED <<formed, coerced, prop, hist, acc, declined, withdrawn, spent, slot>>

(* ---------------- cosigned rows: widening and removal ---------------- *)
(* The primary signs the row; its instant fixes the roster the protocol is judged on.
   The widening's own signed instant must be <= the proposal's expires_at (rule 4): inTime
   records whether it was, and only the "none" twin starts a widening without a live proposal. *)
StartWiden(s, k, r) ==
  /\ formed /\ CanSignAsMember(s) /\ k \notin active /\ slot[k].status # "held"
  /\ (Binding # "none" => Live(k))
  /\ (Honest(s) /\ Live(k) => r = prop[k].role)
  /\ slot' = [slot EXCEPT ![k] = [kind |-> "widen", status |-> "held", by |-> s,
                                  signers |-> {s}, rosterAt |-> active,
                                  foundersAt |-> SeatedFounders, gen |-> prop[k].gen,
                                  role |-> r, age |-> 0, inTime |-> Live(k)]]
  /\ UNCHANGED <<formed, active, coerced, prop, hist, acc, declined, withdrawn, spent,
                 leaveGen, left, consentSeat>>

StartRemove(s, k) ==
  /\ formed /\ CanSignAsMember(s) /\ k \in active /\ k # s /\ slot[k].status # "held"
  /\ (Honest(s) => k = coerced)
  /\ slot' = [slot EXCEPT ![k] = [kind |-> "remove", status |-> "held", by |-> s,
                                  signers |-> {s}, rosterAt |-> active,
                                  foundersAt |-> SeatedFounders, gen |-> 0,
                                  role |-> "none", age |-> 0, inTime |-> TRUE]]
  /\ UNCHANGED <<formed, active, coerced, prop, hist, acc, declined, withdrawn, spent,
                 leaveGen, left, consentSeat>>

(* a cosigner is a member of the roster at the row's instant who is still seated (or, under
   "record", a founder); honest keys cosign widenings and only the coerced key's removal *)
Cosign(s, k) ==
  /\ slot[k].status = "held" /\ s \notin slot[k].signers
  /\ s \in slot[k].rosterAt \cup slot[k].foundersAt /\ CanSignAsMember(s)
  /\ (Honest(s) /\ slot[k].kind = "remove" => k = coerced)
  /\ slot' = [slot EXCEPT ![k].signers = @ \cup {s}]
  /\ UNCHANGED <<formed, active, coerced, prop, hist, acc, declined, withdrawn, spent,
                 leaveGen, left, consentSeat>>

Land(k) ==
  /\ LandGuard(k)
  /\ slot' = [slot EXCEPT ![k] = [NoSlot EXCEPT !.status = "applied"]]
  /\ IF slot[k].kind = "widen"
       THEN /\ active' = active \cup {k}
            /\ spent' = spent \cup {<<k, slot[k].gen>>}
            /\ consentSeat' = IF AcceptedAny(k, slot[k].gen) THEN consentSeat \cup {k}
                                                             ELSE consentSeat
            /\ UNCHANGED <<leaveGen, left>>
       ELSE /\ active' = active \ {k} /\ consentSeat' = consentSeat \ {k}
            /\ leaveGen' = [leaveGen EXCEPT ![k] = prop[k].gen]
            /\ left' = [left EXCEPT ![k] = "removed"]
            /\ UNCHANGED spent
  /\ UNCHANGED <<formed, coerced, prop, hist, acc, declined, withdrawn>>

AgeChange(k)    == /\ slot[k].status = "held" /\ slot[k].age < HoldWindow
                   /\ slot' = [slot EXCEPT ![k].age = @ + 1]
                   /\ UNCHANGED <<formed, active, coerced, prop, hist, acc, declined,
                                  withdrawn, spent, leaveGen, left, consentSeat>>
ExpireChange(k) == /\ HoldExpiry /\ slot[k].status = "held" /\ slot[k].age = HoldWindow
                   /\ slot' = [slot EXCEPT ![k] = [NoSlot EXCEPT !.status = "expired"]]
                   /\ UNCHANGED <<formed, active, coerced, prop, hist, acc, declined,
                                  withdrawn, spent, leaveGen, left, consentSeat>>

Next ==
  \/ \E S \in SUBSET Listed : Found(S)
  \/ \E by, k \in Keys, r \in Roles : Propose(by, k, r)
  \/ \E k \in Keys, r \in Roles : Accept(k, r)
  \/ \E k \in Keys : Decline(k) \/ Withdraw(k) \/ AgeProp(k) \/ ExpireProp(k) \/ Resign(k)
  \/ \E s, k \in Keys, r \in Roles : StartWiden(s, k, r)
  \/ \E s, k \in Keys : StartRemove(s, k) \/ Cosign(s, k)
  \/ \E k \in Keys : Land(k) \/ AgeChange(k) \/ ExpireChange(k)

Spec == Init /\ [][Next]_vars /\ \A k \in Keys : WF_vars(AgeChange(k) \/ ExpireChange(k))

(* ---------------- the STATE_TABLE plane=membership vocabulary ---------------- *)
Stage(k) ==   \* member.stage
  CASE k \in active                                         -> "member"
    [] prop[k].status = "open"                              -> "proposed"
    [] prop[k].status = "accepted"
       \/ (slot[k].kind = "widen" /\ slot[k].status = "held" /\ AcceptedAny(k, slot[k].gen))
                                                            -> "accepted_awaiting_group"
    [] prop[k].status = "declined"                          -> "declined"
    [] left[k] = "removed"                                  -> "removed"
    [] left[k] = "resigned"                                 -> "resigned"
    [] OTHER                                                -> "none"
QuorumChange ==   \* group.quorum_change
  IF \E k \in Keys : slot[k].status = "held" THEN "held"
  ELSE IF \E k \in Keys : slot[k].status = "applied" THEN "applied" ELSE "none"

TypeOK ==
  /\ formed \in BOOLEAN /\ active \subseteq Keys /\ coerced \in Keys \cup {NoKey}
  /\ \A k \in Keys : /\ prop[k].status \in PStatus /\ prop[k].gen \in 0..MaxGen
                     /\ prop[k].age \in 0..Window
                     /\ slot[k].status \in {"none", "held", "applied", "expired"}
                     /\ slot[k].age \in 0..HoldWindow
                     /\ Stage(k) \in {"none", "proposed", "accepted_awaiting_group",
                                      "declined", "member", "removed", "resigned"}
  /\ QuorumChange \in {"none", "held", "applied"}

(* ---------------- properties ---------------- *)
(* A landing step for k of the given kind. Checked on every step (action invariants). *)
Lands(k, kind) == slot[k].status = "held" /\ slot'[k].status = "applied" /\ slot[k].kind = kind

(* CC 3.1.3.2 Admission (1)-(4): a seat comes only from an acceptance of the very proposal
   the widening names, with the same role, signed in time, not withdrawn. *)
Inv_AcceptanceBindsOneProposal ==
  [][\A k \in Keys : Lands(k, "widen") =>
       LET sl == slot[k] IN
       /\ sl.inTime
       /\ Issued(k, sl.gen, sl.role) /\ Accepted(k, sl.gen, sl.role)
       /\ <<k, sl.gen>> \notin withdrawn]_vars

(* CC 3.1.3.2 Decline: a declined proposal never seats; asking again is a new proposal. *)
Inv_DeclineTerminal ==
  [][\A k \in Keys : Lands(k, "widen") => <<k, slot[k].gen>> \notin declined]_vars

(* CC 3.1.3.2: no key is seated on rows it alone signed (proposal and widening). Founding is
   the stated exception: there signing is consent. *)
Inv_NoSelfAdmission ==
  [][\A k \in Keys : Lands(k, "widen") =>
       \E s \in slot[k].signers \cup
                {h.by : h \in {x \in hist : x.k = k /\ x.gen = slot[k].gen}} : s # k]_vars

(* CC 3.1.3.2 / CC 3.3.4: every widening and removal that lands meets the protocol on the
   roster at the row's instant. *)
Inv_QuorumGovernsRoster ==
  [][\A k \in Keys : (Lands(k, "widen") \/ Lands(k, "remove")) =>
       ProtocolMet(slot[k].kind, k, slot[k].signers, slot[k].rosterAt, slot[k].foundersAt)]_vars

(* One coerced key never removes an honest member (honest keys sign removals of the coerced
   key only, so any honest removal is the coerced key's alone). *)
Inv_CoercedCannotRemoveHonest ==
  [][\A k \in Keys : Lands(k, "remove") => k = coerced]_vars

(* A member can always resign, alone, now. *)
Inv_ResignationEnabled == \A k \in active : ENABLED Resign(k)

(* Leaving (resignation or removal) is undone only by a proposal issued after the leaving. *)
Inv_LeavingNotUndone ==
  [][\A k \in Keys : Lands(k, "widen") => slot[k].gen > leaveGen[k]]_vars

(* CC 3.1.3.2 ruling: every seated key is seated on its own signature. *)
Inv_JoinerConsented == active \subseteq consentSeat

(* CC 3.1.3.2 expires_at: no proposal open past its window, no change held past its window. *)
Inv_ExpiryBound == \A k \in Keys : /\ Live(k) => prop[k].age <= Window
                                   /\ slot[k].status = "held" => slot[k].age <= HoldWindow

(* group.quorum_change held -> applied or expired. *)
Prop_HeldChangeResolves == \A k \in Keys : (slot[k].status = "held") ~> (slot[k].status # "held")
=============================================================================
