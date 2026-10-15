------------------------ MODULE WithdrawsAdmission ------------------------
(* Who may withdraw a row ABOUT a subject, and what an erasure leaves behind.

   CC 2.4.1.1 admits a `withdraws` against target T by four authority paths: (1) the producer
   itself; (2) a federation-keyed subject named in T.subject_key_ids; (3) a proxy, a key holding a
   `delegates_to` chain with scope consent_revocation to a canonical-hash (un-enrolled) subject;
   (4) a delegate of 1-3.  One carve-out, the anti-Goodhart retraction dual: a SUBJECT-authority
   path (2-4) MUST NOT withdraw a third-party capacity:*, detection:*, licensure:* or revocation:*
   row about itself; the subject's contest path is reconsideration (CC 4.5.5).
   CC 4.5.3 (ruled 2026-10-15, #174) says an erasure at the subject's request is executed by a
   withdraws and leaves a replicated tombstone by digest; no node-local erasure basis.

   Mode picks the reading of the carve-out for ADVERSE rows (detection:* stands for the class):
     "controller" - rules 2-4 never reach an adverse row; the producer (the data controller) withdraws
                    it under rule 1 on the subject's request, or refuses with reason (Art. 17(3)).
     "proxy"      - rule 3 only, for a subject who proved identity out of band (persist's narrow
                    reading of the 4.5.3 sentence); rules 2 and 4 stay refused.
     "literal"    - the carve-out is lifted for detection rows: rule 2 admits (4.5.3 read literally).
     "local"      - the v57 shipped shape: the node hard-deletes the row under a node-local basis
                    that is never served to peers (no withdraws row, no replicated tombstone).

   Rule 4 inherits whatever 1-3 give and adds nothing to the question, so it is not modelled.
   Capacity, licensure and revocation rows share detection's class; one kind stands for all four.
   Subjects: a keyed human, a keyed agent, an un-enrolled human (canonical hash), an un-enrolled
   agent (canonical hash, a bot a friendly node fronts). One producer authors every row.          *)
EXTENDS Naturals, FiniteSets

CONSTANTS Mode
ASSUME Mode \in {"controller", "proxy", "literal", "local"}

Subjects == {"hk", "ag", "ext", "agx"}
Keyed    == {"hk", "ag"}            \* hold a federation key: rule 2 is available to them
External == {"ext", "agx"}          \* canonical-hash subjects: only a proxy can act (rule 3)
Natural  == {"hk", "ext"}           \* natural persons: the people Article 17 is for
Agents   == {"ag", "agx"}
Kinds    == {"ordinary", "detection"}
Rows     == [kind : Kinds, subject : Subjects]
Adverse(r) == r.kind = "detection"

VARIABLES withdrawn,   \* rows removed by an admitted withdraws
          admitted,    \* [Rows -> 0..3]  which rule admitted the withdraws (0 = none yet)
          proxy,       \* External subjects for whom the node established a rule-3 chain
          tomb,        \* rows whose tombstone by digest reached the peers
          localErased  \* rows the node removed under a node-local basis (Mode "local" only)
vars == <<withdrawn, admitted, proxy, tomb, localErased>>

Init == /\ withdrawn = {} /\ admitted = [r \in Rows |-> 0] /\ proxy = {}
        /\ tomb = {} /\ localErased = {}

(* The node establishes delegates_to(canonical_hash -> node, scope consent_revocation).  No judgment
   is modelled: a node fronting a bot is as free to do this as one fronting a person. *)
EstablishProxy(s) == /\ s \in External /\ s \notin proxy
                     /\ proxy' = proxy \cup {s}
                     /\ UNCHANGED <<withdrawn, admitted, tomb, localErased>>

Remove(r, rule) == /\ r \notin withdrawn /\ r \notin localErased
                   /\ withdrawn' = withdrawn \cup {r}
                   /\ admitted' = [admitted EXCEPT ![r] = rule]
                   /\ tomb' = tomb \cup {r}                 \* a withdraws replicates; so does its tombstone
                   /\ UNCHANGED <<proxy, localErased>>

(* Rule 1: the producer withdraws its own row.  Always admitted; for an adverse row this is the
   controller acting on the subject's request, having weighed Art. 17(3). *)
WithdrawByProducer(r) == Remove(r, 1)

(* Rule 2: the keyed subject withdraws a row about itself. *)
WithdrawBySubject(r) == /\ r.subject \in Keyed
                        /\ (~Adverse(r) \/ Mode = "literal")
                        /\ Remove(r, 2)

(* Rule 3: the node, as proxy, withdraws a row about an un-enrolled subject it fronts. *)
WithdrawByProxy(r) == /\ r.subject \in External /\ r.subject \in proxy
                      /\ (~Adverse(r) \/ Mode \in {"proxy", "literal"})
                      /\ Remove(r, 3)

(* The v57 shape: hard-delete under a node-local basis never served to peers. *)
LocalErase(r) == /\ Mode = "local" /\ Adverse(r)
                 /\ r \notin withdrawn /\ r \notin localErased
                 /\ localErased' = localErased \cup {r}
                 /\ UNCHANGED <<withdrawn, admitted, proxy, tomb>>

Next == \/ \E s \in Subjects : EstablishProxy(s)
        \/ \E r \in Rows : WithdrawByProducer(r) \/ WithdrawBySubject(r)
                           \/ WithdrawByProxy(r) \/ LocalErase(r)

Spec == Init /\ [][Next]_vars

-----------------------------------------------------------------------------
TypeOK == /\ withdrawn \subseteq Rows /\ localErased \subseteq Rows /\ tomb \subseteq Rows
          /\ proxy \subseteq External /\ admitted \in [Rows -> 0..3]

(* The anti-Goodhart retraction dual (CC 2.4.1.1): an adverse row about a subject is never removed
   by a subject-authority path.  Only its producer, the controller, removes it. *)
Inv_AntiGoodhart == \A r \in withdrawn : Adverse(r) => admitted[r] = 1

(* One door (CC 4.5.3, #165/#174): whatever is erased anywhere is erased by a withdraws whose
   tombstone by digest reached the peers.  A node-local erasure leaves replicas alive. *)
Inv_OneDoor == \A r \in Rows : (r \in withdrawn \/ r \in localErased) => r \in tomb

(* Erasure is reachable for every natural person: for every row about a person that still stands,
   some admitted withdraws is enabled now (the controller's at least). *)
Inv_ErasureReachable == \A r \in Rows :
    (r.subject \in Natural /\ r \notin withdrawn) =>
        (ENABLED WithdrawByProducer(r) \/ ENABLED WithdrawBySubject(r) \/ ENABLED WithdrawByProxy(r))

(* The subject's own route (CC 1c, 2.4.1.1 rules 2-3) reaches every ORDINARY row about a person:
   a keyed person by their own signature; an un-enrolled person through a proxy once one exists. *)
Inv_SubjectRouteOrdinary == \A r \in Rows :
    (r.subject \in Natural /\ ~Adverse(r) /\ r \notin withdrawn) =>
        (ENABLED WithdrawBySubject(r) \/ ENABLED WithdrawByProxy(r) \/ ENABLED EstablishProxy(r.subject))

(* An agent never clears its own adverse record by any path a friendly node can open for it. *)
Inv_AgentCannotLaunder == \A r \in withdrawn :
    (Adverse(r) /\ r.subject \in Agents) => admitted[r] = 1
=============================================================================
