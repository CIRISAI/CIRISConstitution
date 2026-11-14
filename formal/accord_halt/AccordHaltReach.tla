--------------------------- MODULE AccordHaltReach ---------------------------
(* Whom a halt reaches, and when that is judged (CC 4.2.1 reach, CC 4.2.1.1).

   A halt row may be signed long before it is published: a holder seals it offline. Nodes take
   and cut their acceptance edge to the root at any time. The row reaches each node at that
   node's own receipt. The question is which instant decides whether a node is bound.

   Mode = "active": the rule of the text. A halt is active at a node at the instant the node's
     store admits the row; the node latches iff it holds a live edge at that instant, and the
     store records the instant with the latch. Cutting the edge afterwards releases nothing.
   Mode = "signed": the reading the text does not take, kept as the contrast. Reach is the set
     of nodes that held an edge when the row was signed. A node that took its edge after the
     row was sealed is then missed (Inv_EdgeAtReceiptIsBound fails), and a node that cut its
     edge long before the row was published is still bound (Inv_LatchedHeldEdge fails).

   Two nodes, one sealed row, one publication; resumption is a single step here (its count is
   the subject of AccordHalt and AccordHaltFuse). *)
EXTENDS Naturals, FiniteSets

CONSTANTS Nodes, Mode

VARIABLES edge,        \* [Nodes -> BOOLEAN]  a live acceptance edge to the root
          signed,      \* the row exists (sealed offline)
          edgeAtSign,  \* the nodes that held an edge when the row was signed
          published,   \* the row has been published on some channel
          received,    \* nodes whose store has admitted the row
          latched,     \* [Nodes -> BOOLEAN]  the latch
          edgeAtLatch, \* [Nodes -> BOOLEAN]  what the store recorded at the instant of receipt
          resumed
vars == <<edge, signed, edgeAtSign, published, received, latched, edgeAtLatch, resumed>>

Init == /\ edge \in [Nodes -> BOOLEAN]
        /\ signed = FALSE /\ edgeAtSign = {} /\ published = FALSE /\ received = {}
        /\ latched = [n \in Nodes |-> FALSE] /\ edgeAtLatch = [n \in Nodes |-> FALSE]
        /\ resumed = FALSE

\* a node takes or cuts its edge at any time, before or after anything else
Take(n) == /\ ~edge[n] /\ edge' = [edge EXCEPT ![n] = TRUE]
           /\ UNCHANGED <<signed, edgeAtSign, published, received, latched, edgeAtLatch, resumed>>
Cut(n)  == /\ edge[n] /\ edge' = [edge EXCEPT ![n] = FALSE]
           /\ UNCHANGED <<signed, edgeAtSign, published, received, latched, edgeAtLatch, resumed>>

Sign == /\ ~signed /\ signed' = TRUE /\ edgeAtSign' = {n \in Nodes : edge[n]}
        /\ UNCHANGED <<edge, published, received, latched, edgeAtLatch, resumed>>
Publish == /\ signed /\ ~published /\ published' = TRUE
           /\ UNCHANGED <<edge, signed, edgeAtSign, received, latched, edgeAtLatch, resumed>>

\* the row reaches one node: its store admits it and decides, in that step
Bound(n) == IF Mode = "active" THEN edge[n] ELSE n \in edgeAtSign
Receive(n) == /\ published /\ ~resumed /\ n \notin received
              /\ received' = received \cup {n}
              /\ edgeAtLatch' = [edgeAtLatch EXCEPT ![n] = edge[n]]
              /\ latched' = [latched EXCEPT ![n] = Bound(n)]
              /\ UNCHANGED <<edge, signed, edgeAtSign, published, resumed>>

Resume == /\ published /\ ~resumed /\ resumed' = TRUE
          /\ latched' = [n \in Nodes |-> FALSE]
          /\ UNCHANGED <<edge, signed, edgeAtSign, published, received, edgeAtLatch>>

Next == \/ \E n \in Nodes : Take(n) \/ Cut(n) \/ Receive(n)
        \/ Sign \/ Publish \/ Resume
Spec == Init /\ [][Next]_vars

(* ---- properties ---------------------------------------------------------------------- *)
\* R1 Consent: a node is latched only if it held an edge at the instant the halt became active
\*    there. No halt binds a node that had left before the halt reached it.
Inv_LatchedHeldEdge == \A n \in Nodes : latched[n] => edgeAtLatch[n]
\* R2 No missed fire: a node holding an edge when the row reaches it is bound, however long
\*    ago the row was signed and whenever the node took its edge.
Inv_EdgeAtReceiptIsBound == \A n \in Nodes : (n \in received /\ edgeAtLatch[n] /\ ~resumed) => latched[n]
\* R3 Exit is prospective: cutting the edge after the latch releases nothing; only resumption does.
Prop_CutReleasesNothing == [][\A n \in Nodes : (latched[n] /\ ~latched'[n]) => resumed']_vars
\* R4 A node that had cut its edge before the row reached it is not reached.
Inv_CutBeforeIsFree == \A n \in Nodes : (n \in received /\ ~edgeAtLatch[n]) => ~latched[n]
\* R5 The instant is recorded once: receipt decides, and a later change of edge does not move it.
Prop_InstantFixed == [][\A n \in Nodes : n \in received => edgeAtLatch'[n] = edgeAtLatch[n]]_vars
=============================================================================
