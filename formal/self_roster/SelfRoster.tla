---------------------------- MODULE SelfRoster ----------------------------
(* Key states under one self: the devices that can sign for an identity, who holds each,
   and the policy under which one device may evict another or add a new one.

   The invariant (CC 3.3.6.4): with three or more keypairs under a self, a stolen device cannot on
   its own kick the other devices off, yet two lost devices are recoverable from the one that
   remains. Possession and authentication are kept apart: a device is HELD by the owner, by a thief,
   or by nobody (lost); a holder can ACT on it only if they can authenticate on it (the owner
   always; a thief only when StolenAuth is TRUE, the worst case). Data at rest is not modelled.

   A change is a PROPOSAL signed by a live roster key, counted over the roster it names (base).
   Its outcome is read from signed rows and from nothing a node has of its own
   (CC 3.3.6.4, "The lone path is a window of rows"). There is no clock in this module.

     a met count      a strict majority of the roster approving, the proposer counted, gives
                      `landed`; a strict majority of the others objecting gives `refused`.
                      Each gives its outcome with no landing row.
     the withdrawal   the proposer's withdrawal refuses an open proposal. It is read after the
                      majority's approval, so a met approval beats it; an approval that has the
                      withdrawal in its past approves nothing.
     the lone path    a seated key signs a HELD row and then a LANDING that names it. The span of
                      the window is the difference of that key's own two instants, so it is the
                      concluder's word: the landings here all state a full span.
                      A held row counts only if it has in its past no row the target signed beyond
                      what the proposal has in its own past. A landing concludes only where the
                      table over its own past gives the outcome it states, and it stands only
                      while the table over every row that does not name it still does (recount).
                      An eviction's table refuses where the target signed any row; an addition
                      has the same table without the target's silence.
     outcome          open | contested | landed | refused. While a proposal is open or contested
                      nothing has changed: the target stays seated, an added key is not seated.
     an ended seat    a row signed by a key whose seat was ended counts only where the row that
                      ended the seat has it in its past.

   This module carries one held row and one landing for each proposal, both signed by its
   proposer, and reads the rule over them. formal/two_path/TwoPathRows.tla writes the rows out
   with their pasts, second landings and two nodes; the outcome here is that module's, restricted
   to these rows. The restriction is a statement of this file and is not checked by a run.

   The fields of a proposal:
     ans[k]    what key k of the others answered: none | approve | approveWd (an approval with the
               withdrawal in its past) | object
     wd        the proposer withdrew
     spoke     the target of an eviction signed a row beyond the proposal's past: no | yes (the row
               names no landing) | named (planted reading only: the row names the landing)
     held      none | ok | bad (the held row has the target's row in its past)
     land      none | concl (the table over the landing's own past gives `landed`) | void (it does not)
     heldLate, landLate   the row was signed after its signer's seat was ended

   Mode: "unilateral" (any proposal lands at once), "quorum" (the count only), "reverse" (the lone
   path and the others' objection only), "combined" (both; the CC 3.3.6.4 shape).
   OwnerPresent: TRUE means every device the owner holds answers each proposal before a reader
   takes its outcome as the roster's next head; FALSE is the owner who signs nothing, the stated cost.
   Window is kept for the configurations that name it; no behaviour reads it.

   A decided proposal becomes the roster's next head by Settle: a reader takes it as the head the
   next proposal names. A lone landing is not final (a row that leaves it unnamed is recounted), so
   Settle is where this module stops following one; what a late row does to a landing a later
   proposal already stands on is not modelled. A seat ended by Settle makes every later row of that
   key spent; every earlier row of it is taken to be in the past of the row that ended the seat,
   the reading that gives the ended key the most.

   Planted breaks (Plant, overridden in a configuration):
     no_held_rule       a held row may have the target's row in its past
     owner_names_all    the owner's row names every landing it holds, the one against its key included
     ended_counts       a row of a key whose seat was ended counts wherever it is signed
     wd_approval_counts an approval that has the withdrawal in its past still approves
     settle_contested   a reader takes a contested proposal as landed
     void_landing_counts a landing that states what the table over its past does not give concludes *)
EXTENDS Naturals, FiniteSets

CONSTANTS Devices, Initial, Mode, Window, StolenAuth, MaxStolen, MaxLost, OwnerPresent
ASSUME Mode \in {"unilateral", "quorum", "reverse", "combined"}
ASSUME Initial \subseteq Devices

Plant == "none"
PlantNoHeldRule == "no_held_rule"
PlantOwnerNamesAll == "owner_names_all"
PlantEndedCounts == "ended_counts"
PlantWdApprovalCounts == "wd_approval_counts"
PlantSettleContested == "settle_contested"
PlantVoidLandingCounts == "void_landing_counts"
\* an owner proposes the eviction of a key that still signs only where its own keys can carry the
\* count. A configuration sets this to see what the lone path is worth against such a key.
OwnerTriesLone == FALSE
\* the rows a thief signs that count for nothing or against itself: its withdrawal, a held row with the
\* target's row in its past, a landing the table over its past does not give. The four-key
\* configurations set these to No and say so; the three-key ones run them.
ThiefWithdraws == TRUE
ThiefFalseRows == TRUE
\* CC 3.3.6.4, the head a self-roster row names: a row naming a head of which the reader has acknowledged
\* a successor is a sibling and void for that reader. So when a reader takes a landed proposal as the
\* next head, every other open proposal is void there and is signed again on the new roster. A
\* configuration sets this to No to follow a stale proposal and the rows of a key whose seat ended.
SiblingsVoid == TRUE
Yes == TRUE
No == FALSE

Holders == {"owner", "thief", "lost"}

VARIABLES member,   \* the roster at the head the next proposal names
          holder, props, gone, started, stolen, lostN, wrong
vars == <<member, holder, props, gone, started, stolen, lostN, wrong>>

Spare == Devices \ (member \cup gone)
Authenticated(d) == holder[d] = "owner" \/ (holder[d] = "thief" /\ StolenAuth)
OwnerHeld == {d \in member : holder[d] = "owner"}
ThiefHeld == {d \in member : holder[d] = "thief"}
LostHeld  == {d \in member : holder[d] = "lost"}
Majority(S, n) == Cardinality(S) * 2 > n
Quorum == Mode \in {"quorum", "combined"}
Lone == Mode \in {"reverse", "combined"}

(* ---- the rule: the outcome of a proposal, from its rows ---- *)
Voters(p) == p.base \ {p.by}
Appr(p) == {p.by} \cup {k \in Voters(p) : p.ans[k] = "approve" \/ (Plant = "wd_approval_counts" /\ p.ans[k] = "approveWd")}
Obj(p) == {k \in Voters(p) : p.ans[k] = "object"}
MetApprove(p) == Quorum /\ Majority(Appr(p), Cardinality(p.base))
MetObject(p) == Lone /\ Majority(Obj(p), Cardinality(Voters(p)))
Spent(late) == late /\ Plant # "ended_counts"
HeldCounts(p) == (p.held = "ok" \/ (p.held = "bad" /\ Plant = "no_held_rule")) /\ ~Spent(p.heldLate)
LandCounts(p) == /\ Lone /\ HeldCounts(p) /\ ~Spent(p.landLate)
                 /\ p.land = "concl" \/ (p.land = "void" /\ Plant = "void_landing_counts")
\* a row the target signed that the recount reads: not in the held row's past, and not naming the landing
TgtCounted(p) == p.kind = "evict" /\ p.spoke = "yes" /\ p.held # "bad"
Stands(p) == LandCounts(p) /\ ~p.wd /\ ~MetObject(p) /\ ~TgtCounted(p)
Outcome(p) ==
  IF Mode = "unilateral" THEN "landed"
  ELSE IF MetApprove(p) THEN "landed"
  ELSE IF Stands(p) THEN "landed"
  ELSE IF p.wd \/ MetObject(p) THEN "refused"
  ELSE IF LandCounts(p) THEN "contested"
  ELSE "open"
\* what the table gives over a landing's own past, when that past is every row signed so far
TableOverAll(p) ==
  IF MetApprove(p) THEN "landed"
  ELSE IF p.wd \/ MetObject(p) THEN "refused"
  ELSE IF ~Lone THEN "none"
  ELSE IF p.kind = "evict" /\ p.spoke # "no" /\ p.held # "bad" THEN "refused"
  ELSE "landed"

Init == /\ member = Initial /\ holder = [d \in Devices |-> "owner"]
        /\ props = {} /\ gone = {} /\ started = FALSE
        /\ stolen = 0 /\ lostN = 0 /\ wrong = FALSE

(* ---- adversary: positions itself before the owner starts acting ---- *)
Steal(d) == /\ ~started /\ d \in member /\ holder[d] = "owner" /\ stolen < MaxStolen
            /\ holder' = [holder EXCEPT ![d] = "thief"] /\ stolen' = stolen + 1
            /\ UNCHANGED <<member, props, gone, started, lostN, wrong>>
Lose(d)  == /\ ~started /\ d \in member /\ holder[d] = "owner" /\ lostN < MaxLost
            /\ holder' = [holder EXCEPT ![d] = "lost"] /\ lostN' = lostN + 1
            /\ UNCHANGED <<member, props, gone, started, stolen, wrong>>

(* ---- what a device's holder wants ---- *)
Wants(d, p) == IF holder[d] = "owner"
                 THEN (p.kind = "evict" /\ holder[p.target] # "owner") \/ (p.kind = "add" /\ holder[p.by] = "owner")
                 ELSE (p.kind = "evict" /\ holder[p.target] = "owner") \/ (p.kind = "add" /\ holder[p.by] = "thief")

(* Any row a seated key signs is a row of the target for every open eviction of that key. The row
   names no landing: its signer either did not hold the landing or leaves it unnamed. *)
Touch(P, d, naming) ==
  {IF q.kind = "evict" /\ q.target = d /\ q.spoke = "no" /\ d \notin gone
     THEN [q EXCEPT !.spoke = IF naming /\ q.land # "none" THEN "named" ELSE "yes"]
     ELSE q : q \in P}

Propose(kind, by, target) ==
    /\ by \in member /\ Authenticated(by)
    /\ IF kind = "evict" THEN target \in member /\ target # by ELSE target \in Spare
    \* an owner evicts only what it lost or had stolen, and a key that still signs only by the count
    /\ holder[by] = "owner" =>
         \/ kind = "add"
         \/ holder[target] = "lost"
         \/ holder[target] = "thief" /\ (OwnerTriesLone \/ ~Quorum \/ Majority(OwnerHeld, Cardinality(member)))
    /\ ~\E p \in props : p.by = by                                        \* one open proposal per proposer
    /\ ~\E p \in props : p.kind = kind /\ p.target = target /\ (kind = "add" \/ holder[p.by] = holder[by])
    /\ props' = Touch(props, by, FALSE) \cup
                {[kind |-> kind, target |-> target, by |-> by, base |-> member,
                  ans |-> [k \in member \ {by} |-> "none"], wd |-> FALSE, spoke |-> "no",
                  held |-> "none", heldLate |-> FALSE, land |-> "none", landLate |-> FALSE]}
    /\ started' = TRUE
    /\ UNCHANGED <<member, holder, gone, stolen, lostN, wrong>>

Answer(d, p) ==
    /\ p \in props /\ d \in Voters(p) /\ d \notin gone /\ Authenticated(d) /\ p.ans[d] = "none"
    /\ \E v \in (IF Wants(d, p) THEN (IF p.wd THEN {"approve", "approveWd"} ELSE {"approve"}) ELSE {"object"}) :
         props' = Touch((props \ {p}) \cup {[p EXCEPT !.ans[d] = v]}, d, FALSE)
    /\ UNCHANGED <<member, holder, gone, started, stolen, lostN, wrong>>

\* a seated key signs a row that answers nothing: the "any row" of the target
Note(d) ==
    /\ d \in member /\ Authenticated(d)
    /\ \E q \in props : q.kind = "evict" /\ q.target = d /\ q.spoke = "no"
    /\ props' = Touch(props, d, Plant = "owner_names_all" /\ holder[d] = "owner")
    /\ UNCHANGED <<member, holder, gone, started, stolen, lostN, wrong>>

\* a thief may withdraw its own proposal at any moment; the owner withdraws nothing here
Withdraw(p) ==
    /\ ThiefWithdraws
    /\ p \in props /\ holder[p.by] = "thief" /\ Authenticated(p.by) /\ p.by \notin gone /\ ~p.wd
    /\ props' = Touch((props \ {p}) \cup {[p EXCEPT !.wd = TRUE]}, p.by, FALSE)
    /\ UNCHANGED <<member, holder, gone, started, stolen, lostN, wrong>>

\* the proposer signs its held row. A thief may put the target's row in its past. The owner takes
\* the lone path only where its own keys cannot carry the count.
OwnerCarries(p) == Quorum /\ Majority({d \in p.base : holder[d] = "owner"}, Cardinality(p.base))
Hold(p) ==
    /\ p \in props /\ Authenticated(p.by) /\ p.held = "none"
    /\ holder[p.by] = "owner" => (Lone /\ ~OwnerCarries(p))
    /\ \E h \in (IF holder[p.by] = "thief" /\ p.kind = "evict" /\ p.spoke # "no" /\ (ThiefFalseRows \/ Plant = "no_held_rule") THEN {"ok", "bad"} ELSE {"ok"}) :
         props' = Touch((props \ {p}) \cup {[p EXCEPT !.held = h, !.heldLate = (p.by \in gone)]}, p.by, FALSE)
    /\ UNCHANGED <<member, holder, gone, started, stolen, lostN, wrong>>

\* the proposer signs its landing, stating `landed` and a full span. Its past is its held row alone,
\* or every row signed so far. The owner counts all it holds and signs only what the table gives.
Land(p) ==
    /\ p \in props /\ Authenticated(p.by) /\ p.held # "none" /\ p.land = "none"
    /\ \E l \in (IF holder[p.by] = "owner"
                   THEN (IF TableOverAll(p) = "landed" THEN {"concl"} ELSE {})
                   ELSE {l \in {IF Lone THEN "concl" ELSE "void", IF TableOverAll(p) = "landed" THEN "concl" ELSE "void"} :
                           ThiefFalseRows \/ l = "concl"}) :
         props' = Touch((props \ {p}) \cup {[p EXCEPT !.land = l, !.landLate = (p.by \in gone)]}, p.by, FALSE)
    /\ UNCHANGED <<member, holder, gone, started, stolen, lostN, wrong>>

(* A reader takes a decided proposal as the head the next proposal names. A present owner has
   answered with every device it holds before that. *)
Settle(p) ==
    /\ p \in props
    /\ \/ Outcome(p) \in {"landed", "refused"}
       \/ Plant = "settle_contested" /\ Outcome(p) = "contested"
    /\ OwnerPresent => \A d \in Voters(p) : (d \in member /\ holder[d] = "owner") => p.ans[d] # "none"
    /\ IF Outcome(p) = "refused"
       THEN UNCHANGED <<member, holder, gone, wrong>>
       ELSE /\ member' = IF p.kind = "evict" THEN member \ {p.target} ELSE member \cup {p.target}
            /\ holder' = IF p.kind = "evict" THEN holder ELSE [holder EXCEPT ![p.target] = holder[p.by]]
            /\ gone' = IF p.kind = "evict" THEN gone \cup {p.target} ELSE gone
            /\ wrong' = (wrong \/ (p.kind = "evict" /\ holder[p.by] = "thief" /\ holder[p.target] = "owner"))
    /\ props' = IF Outcome(p) # "refused" /\ SiblingsVoid THEN {} ELSE props \ {p}
    /\ UNCHANGED <<started, stolen, lostN>>

Mine(p) == holder[p.by] = "owner"
OwnerPropose == \E by \in OwnerHeld, t \in Devices : Propose("evict", by, t) \/ Propose("add", by, t)
OwnerAnswer  == \E p \in props : Mine(p) /\ \E d \in Voters(p) : holder[d] = "owner" /\ Answer(d, p)
OwnerConclude == \E p \in props : Mine(p) /\ Lone /\ (Hold(p) \/ Land(p))
OwnerSettle  == \E p \in props : Mine(p) /\ Settle(p)

Honest == \/ \E by \in member, t \in Devices : Propose("evict", by, t) \/ Propose("add", by, t)
          \/ \E p \in props : \/ \E d \in Devices : Answer(d, p)
                              \/ Withdraw(p) \/ Hold(p) \/ Land(p) \/ Settle(p)
          \/ \E d \in Devices : Note(d)
Adversary == \E d \in Devices : Steal(d) \/ Lose(d)
Next == Honest \/ Adversary

Spec == Init /\ [][Next]_vars /\ WF_vars(OwnerPropose) /\ WF_vars(OwnerAnswer)
             /\ WF_vars(OwnerConclude) /\ WF_vars(OwnerSettle)

-----------------------------------------------------------------------------
TypeOK == /\ member \subseteq Devices /\ holder \in [Devices -> Holders] /\ gone \subseteq Devices
          /\ wrong \in BOOLEAN /\ started \in BOOLEAN
          /\ \A p \in props : /\ p.kind \in {"evict", "add"} /\ p.by \in p.base /\ p.base \subseteq Devices
                              /\ p.spoke \in {"no", "yes", "named"} /\ p.held \in {"none", "ok", "bad"}
                              /\ p.land \in {"none", "concl", "void"}
                              /\ Outcome(p) \in {"open", "contested", "landed", "refused"}

(* First clause: a stolen device never evicts an owner-held device on its own. *)
Inv_ThiefCannotEvictHonest == ~wrong

(* The thief never assembles a majority of the roster while the owner still holds a device. *)
Inv_ThiefNeverMajority == OwnerHeld # {} => ~Majority(ThiefHeld, Cardinality(member))
(* The self survives: the owner never holds no key at all. Fails only where it must: one key, stolen
   (CC 3.3.6.4: at one key a theft is the loss of the self; the other properties are vacuous there). *)
Inv_SelfSurvives == OwnerHeld # {}

(* A thief whose keys are no strict majority of the roster never has its eviction of an owner's key
   read as landed once that key has signed any row beyond the proposal's past. No presence of the
   owner is assumed here beyond that one row. *)
Inv_OwnerRowStopsThief ==
  \A p \in props :
    (p.kind = "evict" /\ holder[p.by] = "thief" /\ holder[p.target] = "owner" /\ p.spoke # "no"
       /\ ~Majority({d \in p.base : holder[d] = "thief"}, Cardinality(p.base)))
      => Outcome(p) # "landed"
(* The lone path asks the target's silence of either side: short of the count, no eviction is read
   as landed while the target has signed a row. *)
Inv_LoneNeedsSilence ==
  \A p \in props :
    (Mode # "unilateral" /\ p.kind = "evict" /\ Outcome(p) = "landed"
       /\ ~Majority({p.by} \cup {k \in Voters(p) : p.ans[k] = "approve"}, Cardinality(p.base)))
      => p.spoke = "no"
(* A row signed after its signer's seat was ended changes no outcome. *)
Stripped(p) == [p EXCEPT !.held = IF p.heldLate THEN "none" ELSE @, !.land = IF p.heldLate \/ p.landLate THEN "none" ELSE @]
Inv_SpentRowsCountNothing == \A p \in props : Outcome(p) = Outcome(Stripped(p))
(* A landing that states what the table over its past does not give, and a landing on a held row that
   has the target's row in its past, conclude nothing: the outcome is the one read without them (so
   such a proposal is `open` and not `contested`). *)
Inv_FalseRowsConcludeNothing ==
  \A p \in props : (p.land = "void" \/ p.held = "bad") => Outcome(p) = Outcome([p EXCEPT !.land = "none"])
(* A withdrawn proposal that no approval made without the withdrawal carries is refused. *)
Inv_WithdrawalRefuses ==
  \A p \in props :
    (Mode # "unilateral" /\ p.wd /\ ~Majority({p.by} \cup {k \in Voters(p) : p.ans[k] = "approve"}, Cardinality(p.base)))
      => Outcome(p) = "refused"
(* While a proposal is open or contested nothing has changed: the roster moves only by a proposal
   read as landed. *)
Prop_NothingChangesUnlessLanded ==
  [][member' # member => \E p \in props : Outcome(p) = "landed" /\ p \notin props']_vars
(* A met approval is final: no later row unmakes it. *)
Same(p, q) == q.by = p.by /\ q.kind = p.kind /\ q.target = p.target /\ q.base = p.base
Prop_MetCountFinal ==
  [][\A p \in props : \A q \in props' : (Same(p, q) /\ MetApprove(p)) => Outcome(q) = "landed"]_vars

(* Second clause: from any device the owner still holds, every lost device and every stolen
   one eventually leaves the roster and the owner holds two devices again. *)
Recovered == LostHeld = {} /\ ThiefHeld = {} /\ Cardinality(OwnerHeld) >= 2
Prop_LostRecoverable == []( (OwnerHeld # {} /\ started) => <>Recovered )
(* Trace-witness helper, used only by dump_traces.py: checking this as an invariant makes TLC print
   the shortest behaviour that spends the whole adversary budget and still reaches Recovered. *)
Inv_NotRecovered == ~(Recovered /\ started /\ stolen = MaxStolen /\ lostN = MaxLost)

(* ---- witnesses: each is the negation of a state the text names; a run must violate it ---- *)
Wit_Open      == ~\E p \in props : Outcome(p) = "open" /\ p.held = "ok"
Wit_Contested == ~\E p \in props : Outcome(p) = "contested"
Wit_LoneLanded == ~\E p \in props : Outcome(p) = "landed" /\ ~MetApprove(p)
Wit_CountLanded == ~\E p \in props : MetApprove(p) /\ p.land = "none" /\ Cardinality(p.base) >= 3
Wit_RefusedByCount == ~\E p \in props : Outcome(p) = "refused" /\ ~p.wd
Wit_RefusedByWithdrawal == ~\E p \in props : Outcome(p) = "refused" /\ p.wd /\ ~MetObject(p)
Wit_ApprovalBeatsWithdrawal == ~\E p \in props : p.wd /\ Outcome(p) = "landed"
Wit_ApprovalAfterWithdrawal == ~\E p \in props : \E k \in Voters(p) : p.ans[k] = "approveWd"
\* cost 1: a lone landing is not final against a key that can still sign. One step takes a proposal
\* read as landed by its landing alone to one that is not.
Wit_LoneLandingNotFinal ==
  [][\A p \in props : \A q \in props' : (Same(p, q) /\ Stands(p) /\ ~MetApprove(p)) => Outcome(q) = "landed"]_vars
\* cost 2: the concluder chooses its instants. A thief's proposal is read as landed on the thief's
\* three rows and nothing else; no clock stood between them.
Wit_ConcluderChoosesInstants ==
  ~\E p \in props : /\ holder[p.by] = "thief" /\ p.kind = "evict" /\ holder[p.target] = "owner" /\ Stands(p)
                    /\ p.spoke = "no" /\ \A k \in Voters(p) : p.ans[k] = "none"
\* cost 3: an absent owner reads as lost. The thief's eviction of an owner's key becomes the head.
Wit_AbsentOwnerReadsLost == ~wrong
\* cost 4: an owner with one live key cannot evict a thief who signs. Its landing concluded, the
\* stolen key signed a row, and the proposal is contested.
Wit_OneKeyCannotEvictSigningThief ==
  ~\E p \in props : /\ holder[p.by] = "owner" /\ p.kind = "evict" /\ holder[p.target] = "thief"
                    /\ Cardinality({d \in p.base : holder[d] = "owner"}) = 1
                    /\ p.land = "concl" /\ p.spoke = "yes" /\ Outcome(p) = "contested"
\* the addition's cost: one objection of two others does not stop it
Wit_AddOneObjection ==
  ~\E p \in props : p.kind = "add" /\ Cardinality(Voters(p)) = 2 /\ Cardinality(Obj(p)) = 1 /\ Stands(p)
\* a key whose seat was ended signs a row (which counts for nothing)
Wit_SpentKeySigns == ~\E p \in props : p.heldLate \/ p.landLate
\* a thief's held row with the target's row in its past, and a landing on it (which concludes nothing)
Wit_BadHeldLanded == ~\E p \in props : p.held = "bad" /\ p.land = "concl" /\ Outcome(p) = "open"
\* a landing that states what the table over its past does not give
Wit_VoidLanding == ~\E p \in props : p.land = "void"
=============================================================================
