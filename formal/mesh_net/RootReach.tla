--------------------------- MODULE RootReach ---------------------------
(* The trust root's reach over its subscribers, separated from the holding model: the properties
   here (INVARIANTS.md I7, I8, I9) read only the subscription edge, the halt latch and a root's
   mesh_config restrictions, and multiplying them into MeshNet's holding state only multiplied
   states (coverage profile, 2026-10-05: Untrust / AccordAct / Restrict were the top producers). *)
EXTENDS Naturals
CONSTANTS Nodes
Cohorts == {"fam", "room", "pub", "commons"}
AccordActs == {"halt", "lifecycle", "other"}   \* CC 4.2.1's closed set; the acts that change no
                                                \* modelled state are one representative
VARIABLES sub, halted, restrict,
          bound   \* subscribed at the live halt's asserted_at (CC 4.2.1 reach pin)
vars == <<sub, halted, restrict, bound>>

Init == /\ sub = [n \in Nodes |-> TRUE]
        /\ halted = [n \in Nodes |-> FALSE]
        /\ restrict = [n \in Nodes |-> {}]
        /\ bound = [n \in Nodes |-> FALSE]

\* A root's mesh_config may only restrict (CC 4.2.1 relieve-never-expand).
Restrict(n, c) == /\ sub[n] /\ c \notin restrict[n]
                  /\ restrict' = [restrict EXCEPT ![n] = @ \cup {c}]
                  /\ UNCHANGED <<sub, halted, bound>>

\* T3: un-trust is one row; everything the root conferred falls away for every later act, and a halt
\* already latched keeps its reach until lifecycle:active (CC 4.2.1: exit is prospective, never retroactive).
Untrust(n) == /\ sub[n]
              /\ sub' = [sub EXCEPT ![n] = FALSE]
              /\ restrict' = [restrict EXCEPT ![n] = {}]
              /\ UNCHANGED <<halted, bound>>

\* A halt lands on every subscriber at once and on nobody else; lifecycle:active lifts it.
AccordAct(a) == /\ a \in AccordActs
                /\ halted' = IF a = "halt" THEN [n \in Nodes |-> sub[n]]
                             ELSE IF a = "lifecycle" THEN [n \in Nodes |-> FALSE] ELSE halted
                /\ bound' = IF a = "halt" THEN [n \in Nodes |-> sub[n]]
                            ELSE IF a = "lifecycle" THEN [n \in Nodes |-> FALSE] ELSE bound
                /\ UNCHANGED <<sub, restrict>>

Next == \/ \E n \in Nodes, c \in Cohorts : Restrict(n, c)
        \/ \E n \in Nodes : Untrust(n)
        \/ \E a \in AccordActs : AccordAct(a)
Spec == Init /\ [][Next]_vars

\* I7 The halt binds subscribers and only subscribers, as subscribed at its asserted_at (CC 4.2.1).
Inv_HaltOnlySubscribers == \A n \in Nodes : halted[n] => bound[n]
\* I8 An un-trusted node is restricted by nothing.
Inv_RestrictNeedsRoot == \A n \in Nodes : ~sub[n] => restrict[n] = {}
\* I7' A halt reaches every subscriber in the step it fires (no party inside routes around it).
Prop_HaltReach == [][AccordAct("halt") => \A n \in Nodes : sub[n] => halted'[n]]_vars
\* I8' Relieve-never-expand: a mesh_config step never shrinks a node's restriction set.
Prop_RestrictOnly == [][(\E n \in Nodes, c \in Cohorts : Restrict(n, c)) =>
                        \A n \in Nodes : restrict[n] \subseteq restrict'[n]]_vars
\* I9 No group ban: an accord act touches nothing but the halt latch (rosters, moderators and
\*    whether a community federates live in MeshNet, which has no accord action at all).
Prop_NoBan == [][(\E a \in AccordActs : AccordAct(a)) => UNCHANGED <<sub, restrict>>]_vars
=========================================================================
