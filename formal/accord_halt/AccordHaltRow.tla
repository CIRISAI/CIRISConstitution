--------------------------- MODULE AccordHaltRow ---------------------------
(* The halt as a row of the signed object (CC 4.2.1.1, CC 4.2.1.3, CC 2.6.1.9, CC 2.6.1.11).

   A halt is an ordinary row with ONE statement: its holder's composite signature over the row's
   payload, verified against the holders of the bundle in force at the node. A key that is not among
   them (a stranger, or a holder a later bundle removed) yields no halt. The lifecycle rows,
   `confirmed` and `active`, are counted rows: several statements over one payload, each naming the
   halt it confirms or ends by row id in `refs.target`, counted at a strict majority of the holders of
   the bundle in force. A statement naming another halt counts for that halt only. The fuse is the
   charter's `halt_fuse_secs` of the bundle in force (`Fuse` ticks here), counted from receipt.

   One node; three holders h1, h2, h3 at the genesis, and a later bundle that removes h3; a stranger
   x. At most two halt rows exist, by any key. Every key may sign lifecycle statements naming any halt
   row that exists, so a stockpiled statement naming an earlier halt is in the world. At most four
   lifecycle statements exist (enough for a confirmation and a resumption), which bounds the state.

   Planted breaks are constants; each twin configuration turns one on and fails its own invariant. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Fuse,
          CountStranger,   \* a halt is counted from a statement by a key not among the bundle's holders
          AnyTarget        \* a lifecycle statement counts whatever halt it names

Keys    == {"h1", "h2", "h3", "x"}
Genesis == {"h1", "h2", "h3"}
Ids     == {1, 2}

VARIABLES inForce,   \* the holders of the bundle in force at the node
          signerOf,  \* [Ids -> Keys \cup {"none"}]: the halt rows that exist, by their one signer
          latched,   \* the halt the node is latched on, or 0
          atLatch,   \* the signer and the holders in force when the node latched
          confirmed,
          clock,     \* ticks since the latch, on the node's own clock
          stmts,     \* lifecycle statements: <<signer, kind, the halt named in refs.target>>
          counted    \* the statements the last confirmation or resumption counted, and the halt it ended
vars == <<inForce, signerOf, latched, atLatch, confirmed, clock, stmts, counted>>

Init == /\ inForce = Genesis /\ signerOf = [i \in Ids |-> "none"] /\ latched = 0
        /\ atLatch = [by |-> "none", holders |-> {}] /\ confirmed = FALSE /\ clock = 0
        /\ stmts = {} /\ counted = [kind |-> "none", halt |-> 0, voices |-> {}]

Majority(S) == Cardinality(S) * 2 > Cardinality(inForce)
\* the voices a lifecycle count reads for halt h: holders of the bundle in force naming h
Voices(kind, h) == {k \in inForce : \E t \in Ids : <<k, kind, t>> \in stmts /\ (t = h \/ AnyTarget)}
Resumed(h) == Majority(Voices("active", h))

\* any key signs a halt row; it is sealed or published at once (the reach model is AccordHaltReach)
Sign(k, i) == /\ signerOf[i] = "none" /\ (i = 1 \/ signerOf[1] # "none")
              /\ signerOf' = [signerOf EXCEPT ![i] = k]
              /\ UNCHANGED <<inForce, latched, atLatch, confirmed, clock, stmts, counted>>

\* the node holds halt row i: one statement, verified against the holders of the bundle in force
Receive(i) == /\ signerOf[i] # "none" /\ latched = 0 /\ ~Resumed(i)
              /\ signerOf[i] \in inForce \/ CountStranger
              /\ latched' = i /\ atLatch' = [by |-> signerOf[i], holders |-> inForce]
              /\ confirmed' = FALSE /\ clock' = 0
              /\ UNCHANGED <<inForce, signerOf, stmts, counted>>

\* a lifecycle statement over the payload naming halt t
State(k, kind, t) == /\ signerOf[t] # "none" /\ <<k, kind, t>> \notin stmts /\ Cardinality(stmts) < 4
                     /\ stmts' = stmts \cup {<<k, kind, t>>}
                     /\ UNCHANGED <<inForce, signerOf, latched, atLatch, confirmed, clock, counted>>

Confirm == /\ latched # 0 /\ ~confirmed /\ clock < Fuse /\ Majority(Voices("confirmed", latched))
           /\ confirmed' = TRUE
           /\ counted' = [kind |-> "confirmed", halt |-> latched, voices |-> Voices("confirmed", latched)]
           /\ UNCHANGED <<inForce, signerOf, latched, atLatch, clock, stmts>>
Resume == /\ latched # 0 /\ Resumed(latched)
          /\ counted' = [kind |-> "active", halt |-> latched, voices |-> Voices("active", latched)]
          /\ latched' = 0 /\ confirmed' = FALSE /\ clock' = 0
          /\ UNCHANGED <<inForce, signerOf, atLatch, stmts>>
Tick == /\ latched # 0 /\ ~confirmed /\ clock < Fuse /\ clock' = clock + 1
        /\ UNCHANGED <<inForce, signerOf, latched, atLatch, confirmed, stmts, counted>>
Lapse == /\ latched # 0 /\ ~confirmed /\ clock = Fuse
         /\ latched' = 0 /\ clock' = 0
         /\ UNCHANGED <<inForce, signerOf, atLatch, confirmed, stmts, counted>>
\* a later bundle, counted, removes h3 (AccordBundle checks the count)
RemoveH3 == /\ "h3" \in inForce /\ inForce' = inForce \ {"h3"}
            /\ UNCHANGED <<signerOf, latched, atLatch, confirmed, clock, stmts, counted>>

Next == \/ \E k \in Keys, i \in Ids : Sign(k, i)
        \/ \E i \in Ids : Receive(i)
        \/ \E k \in Keys, kind \in {"confirmed", "active"}, t \in Ids : State(k, kind, t)
        \/ Confirm \/ Resume \/ Tick \/ Lapse \/ RemoveH3
Spec == Init /\ [][Next]_vars

(* ---- invariants ---------------------------------------------------------------------------- *)
\* W1 A halt latches only on the one statement of a holder of the bundle in force.
Inv_HaltFromHolder == latched # 0 => atLatch.by \in atLatch.holders
\* W2 A confirmation or resumption counts only statements naming the halt it confirms or ends.
Inv_LifecycleNamesHalt == \A k \in counted.voices : <<k, counted.kind, counted.halt>> \in stmts
\* W3 A lone halt lapses at the charter's fuse.
Inv_LoneBounded == (latched # 0 /\ ~confirmed) => clock <= Fuse

\* Witnesses, each checked to FAIL: a confirmation is counted; a halt is resumed after the roster change.
NeverConfirmed == counted.kind # "confirmed"
NeverResumedAfterRemoval == ~(counted.kind = "active" /\ "h3" \notin inForce)
=============================================================================
