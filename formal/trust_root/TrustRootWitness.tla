------------------------- MODULE TrustRootWitness -------------------------
(* Reachability witnesses for TrustRootVerdict. Each Wit_X is the negation of
   a state the machine is meant to reach; run.sh checks that TLC reports each
   one violated under the configuration named beside it, so no invariant of
   the model holds only because its corner is never reached. *)
EXTENDS TrustRootVerdict

(* Rooted, and Stalled, at some instant. *)
Wit_Rooted == ~(\E t \in Instants : VAt(t) = Rooted)
Wit_Stalled == ~(\E t \in Instants : VAt(t) = Stalled)

(* Stalled -> Rooted by a holder's recovery: Rooted at an instant where the
   genesis keys alone would leave fewer live holders than a strict majority. *)
Wit_RecoveredRooted ==
    ~(\E t \in Instants : VAt(t) = Rooted /\ ~Maj({h \in Holders : t < krev[h]}))

(* The node followed the lineage to a later bundle than the one its edge names. *)
Wit_Adopted == ~(edge = "present" /\ cur \notin {NoHead, edgeHead} /\ edgeHead \in Chain(cur))

(* (viii): the head the edge names no longer verifies and the node stands on an ancestor. *)
Wit_FellBack == ~(edge = "present" /\ cur \notin {NoHead, edgeHead} /\ cur \in Chain(edgeHead))

(* The edge's signer's revoked_after does not follow the edge's own instant. *)
Wit_SignerRevoked == ~(edge = "present" /\ ~(edgeAt < orev))

(* An attached node on a frozen lineage, still standing. *)
Wit_FrozenAttached == ~(edge = "present" /\ Frozen(held, {}) /\ VAt(0) # NotRooted)

(* A fork attempt beside a receipted head, with the node attached. *)
Wit_ForkAttempt == ~(edge = "present" /\ ForkAttempt(held, {}) /\ ~Frozen(held, {}))

(* An attached node whose head's Receipts are older than the window, Rooted. *)
Wit_StaleStillRooted ==
    ~(edge = "present" /\ cur # NoHead /\ ByReceipt(cur) /\ rAt[cur] + AttachWindow < clock
      /\ VAt(clock) = Rooted)

(* An attached node whose head has lost its receipt quorum, Rooted. *)
Wit_UnreceiptedStillRooted ==
    ~(edge = "present" /\ cur # NoHead /\ Named /\ ~RefReceipted(cur) /\ VAt(clock) = Rooted)

(* Stalled at the edge's own instant: the edge is written into Stalled, or a
   bound lowered to that instant leaves it there. *)
Wit_StalledAtEdge == ~(edge = "present" /\ VAt(edgeAt) = Stalled)

(* No services named: two counted bundles on the genesis wait as tips. *)
Wit_TipsWait ==
    ~(~Named /\ edge = "present" /\ cur = G /\ Cardinality(Succ(G, held, {})) = 2)

(* No services named: Receipts are held and do not count. *)
Wit_ReceiptsHeldUnnamed == ~(~Named /\ \E b \in held : rN[b] >= Quorum)

(* The third version is in force. *)
Wit_ThirdVersion == ~(edge = "present" /\ cur = A3)
=============================================================================
