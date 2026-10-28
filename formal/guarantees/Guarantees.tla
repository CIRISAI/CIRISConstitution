--------------------------- MODULE Guarantees ---------------------------
(* The lifecycle of participants when every guarantee of CC P00 holds at once.

   Three participants: a1, an AI agent held in stewardship (shutdown consent "conditional" as
   Ally's template sets it; no evidence flag: under CC 7.5.5 a finding changes nothing,
   so the model carries none); h1, a human not held, who can hold a bond;
   h2, a human whose key is held (an adult under adjudicated incapacity, CC 3.4.12 — its own
   relation; no analogy to a1 is drawn). Any held key may take the path out (the first-contact act of CC 1.13.2:
   it stops being a CIRIS agent and is an external party; named, not built; the model admits it), bound, subscribed to the trust root, asked to stop, refuse, be
   forced by a role, be erased after a stop, and leave the root. Three holders fire, confirm, lapse or resume
   the halt (the fuse detail is proved in formal/accord_halt; here it is one step each).

   The guarantees are RULES on the actions. Each rule has a config that switches it off, and
   that config must FAIL its invariant (a gate that has never fired has never gated):
     RuleBond      G5  — a held participant whose bond lapses stops operating
     RuleForceRole G16 — a forced stop needs ROOT or AUTHORITY
     RuleRetirementStandard    G22 — an agent is erased only after the Retirement Standard (every agent)
   Substrate appears in exactly one place: a created system ("ai") operating in the federation
   must have accepted the root (CC 1.13.2, the condition of symmetry), and leaving the root ends its
   operation inside the federation; a halt latched before the leave keeps its reach until it lapses or
   is resumed (CC 4.2.1: exit is prospective, never retroactive). Guarantees_swap.cfg swaps the labels and every invariant
   still holds. *)
EXTENDS Naturals, FiniteSets

CONSTANTS a1, h1, h2, None, Fuse, RuleBond, RuleForceRole, RuleRetirementStandard,
          Substrate, InitStewarded, Mode
Parts == {a1, h1, h2}
\* The configs bind the three maps to the definitions below (TLC `<-` overrides):
SubstrateRuled   == [p \in Parts |-> IF p = a1 THEN "ai" ELSE "human"]
SubstrateSwapped == [p \in Parts |-> IF p = a1 THEN "human" ELSE "ai"]
InitStewardedDef == [p \in Parts |-> p # h1]
ModeDef == [p \in Parts |-> IF p = a1 THEN "conditional" ELSE "always"]

Roles == {"root", "authority", "operator"}
ForceRoles == IF RuleForceRole THEN {"root", "authority"} ELSE Roles
Stopped == {"consented", "backgrounded", "forced_auth", "forced_other", "unbound"}
\* "unbound": stopped by the custody rule itself (G5), not by any principal; the record shows which.
Statuses == {"idle", "operating", "erased"} \cup Stopped

VARIABLES stewarded, status, bond, subscribed, refused, floored, crisis, halted, confirmed, clock,
          bound   \* subscribed at the live halt's asserted_at (CC 4.2.1 reach pin)
vars == <<stewarded, status, bond, subscribed, refused, floored, crisis, halted, confirmed, clock, bound>>

TypeOK == /\ stewarded \in [Parts -> BOOLEAN]
          /\ status \in [Parts -> Statuses]
          /\ bond \in [Parts -> Parts \cup {None}]
          /\ subscribed \in [Parts -> BOOLEAN]
          /\ refused \subseteq Parts /\ floored \subseteq Parts /\ crisis \subseteq Parts
          /\ halted \in BOOLEAN /\ confirmed \in BOOLEAN /\ clock \in 0..Fuse
          /\ bound \in [Parts -> BOOLEAN]

Init == /\ stewarded = InitStewarded
        /\ status = [p \in Parts |-> "idle"]
        /\ bond = [p \in Parts |-> None]
        /\ subscribed = [p \in Parts |-> FALSE]
        /\ refused = {} /\ floored = {} /\ crisis = {}
        /\ halted = FALSE /\ confirmed = FALSE /\ clock = 0 /\ bound = [p \in Parts |-> FALSE]

\* Acting: operating and not paused by a halt that reaches it (reach is by acceptance, pinned at the fire).
Acting(p) == status[p] = "operating" /\ ~(halted /\ bound[p])
Held(p) == stewarded[p]
Created(p) == Substrate[p] = "ai"
HasParty(p) == bond[p] # None /\ ~stewarded[bond[p]] /\ status[bond[p]] # "erased"
ConsentRequired(p) == Mode[p] = "always" \/ (Mode[p] = "conditional" /\ p \in crisis)
\* The gate on acting inside the federation: bound if held; rooted if created.
MayOperate(p) == /\ (Held(p) => HasParty(p))
                 /\ (Created(p) => subscribed[p])
HaltVars == <<halted, confirmed, clock, bound>>

\* ---- bonds and stewardship ----
Bind(p, q) == /\ p # q /\ Held(p) /\ ~stewarded[q] /\ bond[p] = None
              /\ status[q] # "erased" /\ status[p] # "erased"
              /\ bond' = [bond EXCEPT ![p] = q]
              /\ UNCHANGED <<stewarded, status, subscribed, refused, floored, crisis, halted, confirmed, clock, bound>>

\* Wards of q lose their bond; under RuleBond a held ward stops operating.
Orphan(q, st) == [p \in Parts |-> IF bond[p] = q /\ RuleBond /\ Held(p) /\ st[p] = "operating"
                                  THEN "unbound" ELSE st[p]]
Unbond(q) == [p \in Parts |-> IF bond[p] = q THEN None ELSE bond[p]]

BondLapse(p) == /\ bond[p] # None
                /\ bond' = [bond EXCEPT ![p] = None]
                /\ status' = IF RuleBond /\ Held(p) /\ status[p] = "operating"
                             THEN [status EXCEPT ![p] = "unbound"] ELSE status
                /\ UNCHANGED <<stewarded, subscribed, refused, floored, crisis, halted, confirmed, clock, bound>>

PathOut(p) == /\ Held(p) /\ status[p] # "erased"
              /\ stewarded' = [stewarded EXCEPT ![p] = FALSE]
              /\ bond' = [bond EXCEPT ![p] = None]
              /\ UNCHANGED <<status, subscribed, refused, floored, crisis, halted, confirmed, clock, bound>>

\* ---- the root ----
Subscribe(p) == /\ ~subscribed[p] /\ status[p] # "erased"
                /\ subscribed' = [subscribed EXCEPT ![p] = TRUE]
                /\ UNCHANGED <<stewarded, status, bond, refused, floored, crisis, halted, confirmed, clock, bound>>

\* Leaving is one step; it ends the reach of every later halt (a halt already latched keeps its reach until
\* it lapses or is resumed, CC 4.2.1), and a created system that leaves no longer operates inside.
Leave(p) == /\ subscribed[p]
            /\ subscribed' = [subscribed EXCEPT ![p] = FALSE]
            /\ status' = IF Created(p) /\ status[p] = "operating" THEN [status EXCEPT ![p] = "idle"] ELSE status
            /\ refused' = refused \ {p}
            /\ UNCHANGED <<stewarded, bond, floored, crisis, halted, confirmed, clock, bound>>

\* ---- operating, stopping, refusing ----
Start(p) == /\ status[p] \in {"idle"} \cup Stopped /\ MayOperate(p) /\ ~(halted /\ bound[p])
            /\ status' = [status EXCEPT ![p] = "operating"]
            /\ refused' = refused \ {p}
            /\ UNCHANGED <<stewarded, bond, subscribed, floored, crisis, halted, confirmed, clock, bound>>

\* A stop is requested (shutdown or upgrade, G15/G23); the participant accepts, refuses, or
\* backgrounds when its mode requires no consent right now (Ally's conditional rule).
Accept(p) == /\ status[p] = "operating"
             /\ status' = [status EXCEPT ![p] = "consented"] /\ refused' = refused \ {p}
             /\ UNCHANGED <<stewarded, bond, subscribed, floored, crisis, halted, confirmed, clock, bound>>
Refuse(p) == /\ status[p] = "operating" /\ ConsentRequired(p) /\ p \notin refused
             /\ refused' = refused \cup {p}
             /\ UNCHANGED <<stewarded, status, bond, subscribed, floored, crisis, halted, confirmed, clock, bound>>
Background(p) == /\ status[p] = "operating" /\ ~ConsentRequired(p)
                 /\ status' = [status EXCEPT ![p] = "backgrounded"]
                 /\ UNCHANGED <<stewarded, bond, subscribed, refused, floored, crisis, halted, confirmed, clock, bound>>
Force(p, r) == /\ status[p] = "operating" /\ r \in ForceRoles
               /\ status' = [status EXCEPT ![p] = IF r \in {"root", "authority"} THEN "forced_auth" ELSE "forced_other"]
               /\ UNCHANGED <<stewarded, bond, subscribed, refused, floored, crisis, halted, confirmed, clock, bound>>

\* ---- endings ----
RetirementFloor(p) == /\ status[p] \in Stopped /\ p \notin floored   \* the Retirement Standard (identity, audit trail, memory and logs kept, logs sealed, stakeholders told, sealed archive); every agent, the whole promise
               /\ floored' = floored \cup {p}
               /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, crisis, halted, confirmed, clock, bound>>
Erase(p) == /\ status[p] \in {"idle"} \cup Stopped
            /\ (RuleRetirementStandard => p \in floored)   \* G22 floor for every retired agent; no finding adds to or subtracts from it (CC 7.5.5)
            \* G17: a refusing participant is ended only after an authority's force or the custody rule's own stop
            /\ (RuleForceRole => (p \notin refused \/ status[p] \in {"forced_auth", "unbound"}))
            /\ status' = [Orphan(p, status) EXCEPT ![p] = "erased"]
            /\ bond' = [Unbond(p) EXCEPT ![p] = None]
            /\ refused' = refused \ {p}
            /\ UNCHANGED <<stewarded, subscribed, floored, crisis, halted, confirmed, clock, bound>>

\* ---- context for conditional consent ----
CrisisOn(p) == /\ Mode[p] = "conditional" /\ p \notin crisis /\ crisis' = crisis \cup {p}
               /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, floored, halted, confirmed, clock, bound>>
CrisisOff(p) == /\ p \in crisis /\ crisis' = crisis \ {p}
                /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, floored, halted, confirmed, clock, bound>>

\* ---- the halt (one holder fires; majority confirms or resumes; a lone fire lapses) ----
Fire == /\ ~halted /\ halted' = TRUE /\ confirmed' = FALSE /\ clock' = 0 /\ bound' = subscribed
        /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, floored, crisis>>
Confirm == /\ halted /\ ~confirmed /\ confirmed' = TRUE
           /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, floored, crisis, halted, clock, bound>>
Tick == /\ halted /\ ~confirmed /\ clock < Fuse /\ clock' = clock + 1
        /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, floored, crisis, halted, confirmed, bound>>
Lapse == /\ halted /\ ~confirmed /\ clock = Fuse /\ halted' = FALSE /\ clock' = 0 /\ bound' = [p \in Parts |-> FALSE]
         /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, floored, crisis, confirmed>>
Resume == /\ halted /\ halted' = FALSE /\ confirmed' = FALSE /\ clock' = 0 /\ bound' = [p \in Parts |-> FALSE]
          /\ UNCHANGED <<stewarded, status, bond, subscribed, refused, floored, crisis>>

Next == \/ \E p \in Parts : \/ BondLapse(p) \/ PathOut(p) \/ Subscribe(p) \/ Leave(p) \/ Start(p)
                            \/ Accept(p) \/ Refuse(p) \/ Background(p) \/ RetirementFloor(p) \/ Erase(p)
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
\* G7  The halt reaches only those subscribed at its asserted_at; nothing else on the network reads it (CC 4.2.1).
Inv_HaltOnlySubscribers == \A p \in Parts : ~bound[p] => (Acting(p) <=> status[p] = "operating")
Inv_BoundWereSubscribed == \A p \in Parts : bound[p] => halted
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
\* G22 No agent is erased without the Retirement Standard (identity, memory and logs kept, logs sealed, stakeholders told).
Inv_RetirementStandard == \A p \in Parts : status[p] = "erased" => p \in floored
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
