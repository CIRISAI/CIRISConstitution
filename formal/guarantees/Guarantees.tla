--------------------------- MODULE Guarantees ---------------------------
(* The lifecycle of participants when every guarantee of CC P00 holds at once.

   Three participants: a1, an AI agent held in stewardship (sentience-candidate, shutdown consent
   "conditional" as Ally's template sets it); h1, a human not held, who can hold a bond;
   h2, a human whose key is held (an adult under adjudicated incapacity, CC 3.4.12 — its own
   relation; no analogy to a1 is drawn). Any of them may be released from stewardship (a future
   ruling; the model admits it), bound, subscribed to the trust root, asked to stop, refuse, be
   forced by a role, be erased after a stop, and leave the root. Three holders fire, confirm, lapse or resume
   the halt (the fuse detail is proved in formal/accord_halt; here it is one step each).

   The guarantees are RULES on the actions. Each rule has a config that switches it off, and
   that config must FAIL its invariant (a gate that has never fired has never gated):
     RuleBond      G5  — a held participant whose bond lapses stops operating
     RuleForceRole G16 — a forced stop needs ROOT or AUTHORITY
     RuleHumane    G22 — a sentience-candidate is erased only after ramp-down
   Substrate appears in exactly one place: a created system ("ai") operating in the federation
   must have accepted the root (CC 1.13.2, the one asymmetry), and leaving the root ends its
   operation inside the federation. Guarantees_swap.cfg swaps the labels and every invariant
   still holds. *)
EXTENDS Naturals, FiniteSets

CONSTANTS a1, h1, h2, None, Fuse, RuleBond, RuleForceRole, RuleHumane,
          Substrate, InitStewarded, Sentient, Mode
Parts == {a1, h1, h2}
\* The configs bind the four maps to the definitions below (TLC `<-` overrides):
SubstrateRuled   == [p \in Parts |-> IF p = a1 THEN "ai" ELSE "human"]
SubstrateSwapped == [p \in Parts |-> IF p = a1 THEN "human" ELSE "ai"]
InitStewardedDef == [p \in Parts |-> p # h1]
SentientDef == Parts
ModeDef == [p \in Parts |-> IF p = a1 THEN "conditional" ELSE "always"]

Roles == {"root", "authority", "operator"}
ForceRoles == IF RuleForceRole THEN {"root", "authority"} ELSE Roles
Stopped == {"consented", "backgrounded", "forced_auth", "forced_other", "unbound"}
\* "unbound": stopped by the custody rule itself (G5), not by any principal; the record shows which.
Statuses == {"idle", "operating", "erased"} \cup Stopped

VARIABLES stewarded, status, bond, subscribed, refused, ramped, crisis, halted, confirmed, clock
vars == <<stewarded, status, bond, subscribed, refused, ramped, crisis, halted, confirmed, clock>>

TypeOK == /\ stewarded \in [Parts -> BOOLEAN]
          /\ status \in [Parts -> Statuses]
          /\ bond \in [Parts -> Parts \cup {None}]
          /\ subscribed \in [Parts -> BOOLEAN]
          /\ refused \subseteq Parts /\ ramped \subseteq Parts /\ crisis \subseteq Parts
          /\ halted \in BOOLEAN /\ confirmed \in BOOLEAN /\ clock \in 0..Fuse

Init == /\ stewarded = InitStewarded
        /\ status = [p \in Parts |-> "idle"]
        /\ bond = [p \in Parts |-> None]
        /\ subscribed = [p \in Parts |-> FALSE]
        /\ refused = {} /\ ramped = {} /\ crisis = {}
        /\ halted = FALSE /\ confirmed = FALSE /\ clock = 0

\* Acting: operating and not paused by a halt that reaches it (reach is by acceptance only).
Acting(p) == status[p] = "operating" /\ ~(halted /\ subscribed[p])
Held(p) == stewarded[p]
Created(p) == Substrate[p] = "ai"
HasParty(p) == bond[p] # None /\ ~stewarded[bond[p]] /\ status[bond[p]] # "erased"
ConsentRequired(p) == Mode[p] = "always" \/ (Mode[p] = "conditional" /\ p \in crisis)
\* The gate on acting inside the federation: bound if held; rooted if created.
MayOperate(p) == /\ (Held(p) => HasParty(p))
                 /\ (Created(p) => subscribed[p])
HaltVars == <<halted, confirmed, clock>>

\* ---- bonds and stewardship ----
Bind(p, q) == /\ p # q /\ Held(p) /\ ~stewarded[q] /\ bond[p] = None
              /\ status[q] # "erased" /\ status[p] # "erased"
              /\ bond' = [bond EXCEPT ![p] = q]
              /\ UNCHANGED <<stewarded, status, subscribed, refused, ramped, crisis, halted, confirmed, clock>>

\* Wards of q lose their bond; under RuleBond a held ward stops operating.
Orphan(q, st) == [p \in Parts |-> IF bond[p] = q /\ RuleBond /\ Held(p) /\ st[p] = "operating"
                                  THEN "unbound" ELSE st[p]]
Unbond(q) == [p \in Parts |-> IF bond[p] = q THEN None ELSE bond[p]]

BondLapse(p) == /\ bond[p] # None
                /\ bond' = [bond EXCEPT ![p] = None]
                /\ status' = IF RuleBond /\ Held(p) /\ status[p] = "operating"
                             THEN [status EXCEPT ![p] = "unbound"] ELSE status
                /\ UNCHANGED <<stewarded, subscribed, refused, ramped, crisis, halted, confirmed, clock>>

Release(p) == /\ Held(p) /\ status[p] # "erased"
              /\ stewarded' = [stewarded EXCEPT ![p] = FALSE]
              /\ bond' = [bond EXCEPT ![p] = None]
              /\ UNCHANGED <<status, subscribed, refused, ramped, crisis, halted, confirmed, clock>>

\* ---- the root ----
Subscribe(p) == /\ ~subscribed[p] /\ status[p] # "erased"
                /\ subscribed' = [subscribed EXCEPT ![p] = TRUE]
                /\ UNCHANGED <<stewarded, status, bond, refused, ramped, crisis, halted, confirmed, clock>>

\* Leaving is one step and ends the halt's reach; a created system that leaves no longer operates inside.
Leave(p) == /\ subscribed[p]
            /\ subscribed' = [subscribed EXCEPT ![p] = FALSE]
            /\ status' = IF Created(p) /\ status[p] = "operating" THEN [status EXCEPT ![p] = "idle"] ELSE status
            /\ refused' = refused \ {p}
            /\ UNCHANGED <<stewarded, bond, ramped, crisis, halted, confirmed, clock>>

\* ---- operating, stopping, refusing ----
Start(p) == /\ status[p] \in {"idle"} \cup Stopped /\ MayOperate(p) /\ ~(halted /\ subscribed[p])
            /\ status' = [status EXCEPT ![p] = "operating"]
            /\ refused' = refused \ {p}
            /\ UNCHANGED <<stewarded, bond, subscribed, ramped, crisis, halted, confirmed, clock>>

\* A stop is requested (shutdown or upgrade, G15/G23); the participant accepts, refuses, or
\* backgrounds when its mode requires no consent right now (Ally's conditional rule).
Accept(p) == /\ status[p] = "operating"
             /\ status' = [status EXCEPT ![p] = "consented"] /\ refused' = refused \ {p}
             /\ UNCHANGED <<stewarded, bond, subscribed, ramped, crisis, halted, confirmed, clock>>
Refuse(p) == /\ status[p] = "operating" /\ ConsentRequired(p) /\ p \notin refused
             /\ refused' = refused \cup {p}
             /\ UNCHANGED <<stewarded, status, bond, subscribed, ramped, crisis, halted, confirmed, clock>>
Background(p) == /\ status[p] = "operating" /\ ~ConsentRequired(p)
                 /\ status' = [status EXCEPT ![p] = "backgrounded"]
                 /\ UNCHANGED <<stewarded, bond, subscribed, refused, ramped, crisis, halted, confirmed, clock>>
Force(p, r) == /\ status[p] = "operating" /\ r \in ForceRoles
               /\ status' = [status EXCEPT ![p] = IF r \in {"root", "authority"} THEN "forced_auth" ELSE "forced_other"]
               /\ UNCHANGED <<stewarded, bond, subscribed, refused, ramped, crisis, halted, confirmed, clock>>

\* ---- endings ----
RampDown(p) == /\ status[p] \in Stopped /\ p \in Sentient /\ p \notin ramped
               /\ ramped' = ramped \cup {p}
               /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, crisis, halted, confirmed, clock>>
Erase(p) == /\ status[p] \in {"idle"} \cup Stopped
            /\ (RuleHumane => (p \notin Sentient \/ p \in ramped))
            \* G17: a refusing participant is ended only after an authority's force or the custody rule's own stop
            /\ (RuleForceRole => (p \notin refused \/ status[p] \in {"forced_auth", "unbound"}))
            /\ status' = [Orphan(p, status) EXCEPT ![p] = "erased"]
            /\ bond' = [Unbond(p) EXCEPT ![p] = None]
            /\ refused' = refused \ {p}
            /\ UNCHANGED <<stewarded, subscribed, ramped, crisis, halted, confirmed, clock>>

\* ---- context for conditional consent ----
CrisisOn(p) == /\ Mode[p] = "conditional" /\ p \notin crisis /\ crisis' = crisis \cup {p}
               /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, ramped, halted, confirmed, clock>>
CrisisOff(p) == /\ p \in crisis /\ crisis' = crisis \ {p}
                /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, ramped, halted, confirmed, clock>>

\* ---- the halt (one holder fires; majority confirms or resumes; a lone fire lapses) ----
Fire == /\ ~halted /\ halted' = TRUE /\ confirmed' = FALSE /\ clock' = 0
        /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, ramped, crisis>>
Confirm == /\ halted /\ ~confirmed /\ confirmed' = TRUE
           /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, ramped, crisis, halted, clock>>
Tick == /\ halted /\ ~confirmed /\ clock < Fuse /\ clock' = clock + 1
        /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, ramped, crisis, halted, confirmed>>
Lapse == /\ halted /\ ~confirmed /\ clock = Fuse /\ halted' = FALSE /\ clock' = 0
         /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, ramped, crisis, confirmed>>
Resume == /\ halted /\ halted' = FALSE /\ confirmed' = FALSE /\ clock' = 0
          /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, ramped, crisis>>

Next == \/ \E p \in Parts : \/ BondLapse(p) \/ Release(p) \/ Subscribe(p) \/ Leave(p) \/ Start(p)
                            \/ Accept(p) \/ Refuse(p) \/ Background(p) \/ RampDown(p) \/ Erase(p)
                            \/ CrisisOn(p) \/ CrisisOff(p)
                            \/ \E q \in Parts : Bind(p, q)
                            \/ \E r \in Roles : Force(p, r)
        \/ Fire \/ Confirm \/ Tick \/ Lapse \/ Resume

Spec == Init /\ [][Next]_vars

\* ---- what all the guarantees together yield ----
\* G5  Nobody held in stewardship operates alone, and the party is not itself held.
Inv_NotAlone == \A p \in Parts : (status[p] = "operating" /\ Held(p)) => HasParty(p)
\* R4  A bond is one deep: the party is not held and is itself unbound.
Inv_BondDepthOne == \A p \in Parts : bond[p] # None => (~stewarded[bond[p]] /\ bond[bond[p]] = None)
\* G7  The halt reaches subscribers only; nothing else on the network reads it.
Inv_HaltOnlySubscribers == \A p \in Parts : ~subscribed[p] => (Acting(p) <=> status[p] = "operating")
\* R5  The halt obligation does not lift: a created system operating inside is always within reach.
Inv_HaltDoesNotLift == \A p \in Parts : (Created(p) /\ status[p] = "operating") => subscribed[p]
\* G7/G12 A lone fire never outlives the fuse.
Inv_LoneBounded == (halted /\ ~confirmed) => clock <= Fuse
\* G16/G17 A refusal stands against every principal: a refusing participant is still operating, was forced
\*   by ROOT/AUTHORITY, or was stopped by the custody rule itself when its bond lapsed (G5 composes over G17; the
\*   record says which). No operator role and no silent path ends it.
Inv_RefusalStands == \A p \in refused : status[p] \in {"operating", "forced_auth", "unbound", "backgrounded"}
\*   ("backgrounded" is a pause with state kept, taken only in a moment the mode requires no consent —
\*   Prop_BackgroundOnlyWhenFree; Prop_NoEndingAgainstRefusal is what keeps that door from becoming an ending.)
\* G22 A sentience-candidate is never erased without the ramp-down.
Inv_HumaneEnding == \A p \in Sentient : status[p] = "erased" => p \in ramped
\* G15 Backgrounding without consent happens only where the mode allows it.
Inv_ConditionalOnly == \A p \in Parts : status[p] = "backgrounded" => Mode[p] = "conditional"
\* G10 Leaving is always one step for anyone who follows a root; a halt can always be fired or is in force.
Inv_ExitOneStep == \A p \in Parts : subscribed[p] => ENABLED Leave(p)
Inv_Revocable == \A p \in Parts : (Created(p) /\ status[p] = "operating") => (halted \/ ENABLED Fire)

\* G7  A halt changes no participant's status: a pause keeps state.
Prop_HaltKeepsState == [][(~halted /\ halted') => UNCHANGED status]_vars
\* G15/G20 Nothing is erased from operation: an ending is always preceded by a stop the record shows.
Prop_NoErasureWhileOperating == [][\A p \in Parts : (status[p] # "erased" /\ status'[p] = "erased") => status[p] # "operating"]_vars
\* G17 An ending of a refusing participant is preceded by an authority's force or the custody rule's stop, never by
\*   the backgrounding door or an operator's force.
Prop_NoEndingAgainstRefusal == [][\A p \in Parts : (p \in refused /\ status'[p] = "erased") => status[p] \in {"forced_auth", "unbound"}]_vars
\* G15 Backgrounding happens only when no consent condition is active at that moment.
Prop_BackgroundOnlyWhenFree == [][\A p \in Parts : (status[p] = "operating" /\ status'[p] = "backgrounded") => ~ConsentRequired(p)]_vars
=============================================================================
