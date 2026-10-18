------------------------------ MODULE Consent ------------------------------
(* The consent plane (plane model "C", review/notes/formal_closure_rc9_2026-10-18.md §5).

   Two consent series over one receiver's held rows, one fold for both (CC 3.3.1):
     "st"  consent:state  - the subject's stance on a Contribution about them (subject x scope).
           Granted / revoked by the subject (a subject_key_id); `expired` is emitted by the
           substrate (persist) when a grant's valid_until passes, carrying consent_supersedes
           naming the grant; scope is the `scope` member of the granted envelope (#103), and a
           grant naming no scope matches nothing.
     "ct"  consent:community_trust - the capture grant for one node's sealed traces
           (node x community).  Authored by the node or by its owner at the grant's asserted_at
           (CIRISConstitution#179); subject_key_ids lists node, owner-at-asserted_at and the agent
           key, and any of the three may withdraw.  A grant or revocation from a key that was
           neither the node nor its owner at the row's asserted_at is not this node's consent.
   The fold (CC 3.3.1, normative): the latest admitted revocation's asserted_at is R; every grant
   with asserted_at <= R is out; among grants after R the latest asserted_at wins, ties on the
   smallest attestation id (here: the row index); no grant means no consent.  A revocation is a
   boundary, not a deletion.  The fold over `st` also yields `expired` when the winning grant's
   valid_until has passed (CC 3.3.1 `consent:state:expired`).

   Admission (CC 2.6.7): a consent row is judged at its signed asserted_at, which the signer
   chooses; a row whose asserted_at precedes the receiver's clock by more than W is refused
   (asserted_at_stale) and moves nothing.  Ownership: owner_of(node) is O1 before instant TX and
   O2 from TX on (an owner_binding withdrawn and replaced, CC 3.2): O1 is the withdrawn signer.

   Uses of consent (each a conforming node's act, gated on the fold at the use's instant):
     Capture  - a sealed trace at instant `now` is captured iff the ct fold says granted.
     Score    - an `analyze` use at `now` iff the st fold says granted and the winning grant's
                scope contains analyze (CC 3.4.5 context).
     Replicate- the node ships captured traces to peer p iff a live consent:replication grant
                (CC 3.3.7) names p; the grant is the node's or its owner's, directed, per peer.
   Decay (CC 3.3.1 consent:decay:{stage}): the agent's consent module walks identity_severed ->
   patterns_anonymized -> complete once the st fold reads revoked or expired.

   The adversary: signs any row as a stranger; signs as the withdrawn owner O1 after TX with
   asserted_at backdated to before TX; backdates any party's row within and beyond W; replays any
   row already signed; forges `expired` under a non-substrate key; grants replication as a stranger.

   Mode picks the reading under test:
     "ruled"          - the CC 3.3.1 fold, #179 standing, the CC 2.6.7 W bound.
     "no_boundary"    - the latest grant wins regardless of revocation.
     "literal_signer" - only the node may revoke a community_trust grant (the pre-#179 reading
                        that the owner speaks only through the node).
     "no_W"           - no freshness bound: a backdated row is admitted however old.            *)
EXTENDS Integers, FiniteSets, Sequences

CONSTANTS Mode, Planes, MaxT, W, TX, Life, MaxRows
ASSUME Mode \in {"ruled", "no_boundary", "literal_signer", "no_W"}
ASSUME Planes \subseteq {"st", "ct"} /\ Planes # {}
ASSUME TX \in 1..MaxT /\ W \in 1..MaxT /\ Life \in 1..MaxT

Instants == 0..MaxT
NoVU     == MaxT + 100                  \* "no valid_until"
Peers    == {"p1", "p2"}
Stages   == <<"none", "identity_severed", "patterns_anonymized", "complete">>
Rank(s)  == CHOOSE i \in 1..4 : Stages[i] = s

OwnerAt(t) == IF t < TX THEN "o1" ELSE "o2"

\* Who may sign what, as the adversary tries it (the row's shape admits any key; standing decides).
StSigners == {"subject", "stranger"}
CtSigners == {"node", "o1", "o2", "agent", "stranger"}

VARIABLES now,       \* the receiver's clock
          rows,      \* the rows the receiver admitted, in admission order (index = attestation id order)
          capt,      \* [Instants -> -1..MaxRows]: -1 no capture; k = the capture saw rows 1..k
          scored,    \* [Instants -> -1..MaxRows]: the same for an analyze use
          decay,     \* the agent's decay ladder for the subject's data
          decayCause,\* the st fold value when the ladder started
          replLive,  \* peers named by a live, admitted consent:replication grant
          peerHolds, \* peers holding the node's captured traces
          badSend    \* a send to a peer with no live grant naming it happened
vars == <<now, rows, capt, scored, decay, decayCause, replLive, peerHolds, badSend>>

Ids     == 1..Len(rows)
Pre(k)  == 1..k                       \* what a use decided at prefix k saw

(* ---------------------------------------------------------------- standing ------------- *)
Standing(r) ==
  CASE r.series = "st" /\ r.kind \in {"grant", "revoke"} -> r.signer = "subject"
    [] r.series = "st" /\ r.kind = "expired" ->
          /\ r.signer = "persist"
          /\ r.sup \in Ids /\ rows[r.sup].kind = "grant" /\ rows[r.sup].series = "st"
          /\ rows[r.sup].vu <= r.at
    [] r.series = "ct" /\ r.kind = "grant" -> r.signer \in {"node", OwnerAt(r.at)}
    [] r.series = "ct" /\ r.kind = "revoke" ->
          IF Mode = "literal_signer" THEN r.signer = "node"
          ELSE r.signer \in {"node", OwnerAt(r.at), "agent"}
    [] OTHER -> FALSE

Fresh(r, t) == Mode = "no_W" \/ t - r.at <= W

(* A refused row (asserted_at_stale, or no standing) is not admitted: it moves nothing, so the
   model has no transition for it.  Replay of an admitted row dedups on its attestation id and is
   likewise no transition; replay of a refused row is re-judged at a later clock, where staleness
   only grows and standing is judged at the row's own asserted_at, so it is refused again. *)
Admit(r, t) == Fresh(r, t) /\ Standing(r)

(* ---------------------------------------------------------------- the fold -------------- *)
GrantsAt(s, t, H)  == {i \in H : rows[i].series = s /\ rows[i].kind = "grant"  /\ rows[i].at <= t}
RevokesAt(s, t, H) == {i \in H : rows[i].series = s /\ rows[i].kind = "revoke" /\ rows[i].at <= t}
MaxAt(S) == CHOOSE m \in {rows[i].at : i \in S} : \A i \in S : rows[i].at <= m
Bound(s, t, H) ==
  IF Mode = "no_boundary" \/ RevokesAt(s, t, H) = {} THEN -1 ELSE MaxAt(RevokesAt(s, t, H))
After(s, t, H) == {i \in GrantsAt(s, t, H) : rows[i].at > Bound(s, t, H)}
Winner(S) == CHOOSE i \in S : \A j \in S : rows[j].at < rows[i].at
                                          \/ (rows[j].at = rows[i].at /\ i <= j)
Fold(s, t, H) ==
  IF After(s, t, H) = {}
  THEN [v |-> IF Bound(s, t, H) >= 0 THEN "revoked" ELSE "none", by |-> 0]
  ELSE LET g == Winner(After(s, t, H)) IN
       [v |-> IF t >= rows[g].vu THEN "expired" ELSE "granted", by |-> g]

FoldNow(s) == Fold(s, now, Ids)

(* ---------------------------------------------------------------- init ------------------ *)
Init == /\ now = 0 /\ rows = <<>>
        /\ capt = [t \in Instants |-> -1] /\ scored = [t \in Instants |-> -1]
        /\ decay = "none" /\ decayCause = "none"
        /\ replLive = {} /\ peerHolds = {} /\ badSend = FALSE

(* ---------------------------------------------------------------- actions --------------- *)
Tick == /\ now < MaxT /\ now' = now + 1
        /\ UNCHANGED <<rows, capt, scored, decay, decayCause, replLive, peerHolds, badSend>>

Row(s, k, sg, a, sc, vu, sup) ==
  [series |-> s, kind |-> k, signer |-> sg, at |-> a, scope |-> sc, vu |-> vu, sup |-> sup, adm |-> 0]

Offer(r) == /\ Len(rows) < MaxRows
            /\ Admit(r, now)
            /\ rows' = Append(rows, [r EXCEPT !.adm = now])
            /\ UNCHANGED <<now, capt, scored, decay, decayCause, replLive, peerHolds, badSend>>

(* Any party, or the adversary in its name, signs a row with an asserted_at of its choosing. *)
SignSt == /\ "st" \in Planes
          /\ \E sg \in StSigners, a \in 0..now :
               \/ \E v \in {[sc |-> {}, vu |-> NoVU], [sc |-> {"analyze"}, vu |-> NoVU],
                            [sc |-> {"analyze"}, vu |-> a + Life]} :
                     Offer(Row("st", "grant", sg, a, v.sc, v.vu, 0))
               \/ Offer(Row("st", "revoke", sg, a, {}, NoVU, 0))
               \/ \E g \in Ids : Offer(Row("st", "expired", sg, a, {}, NoVU, g))  \* forged expiry
SignCt == /\ "ct" \in Planes
          /\ \E sg \in CtSigners, a \in 0..now, k \in {"grant", "revoke"} :
               Offer(Row("ct", k, sg, a, {}, NoVU, 0))

(* The substrate's own leaf: expired, naming the lapsed grant (consent_supersedes). *)
EmitExpired == /\ "st" \in Planes
               /\ FoldNow("st").v = "expired"
               /\ ~\E i \in Ids : rows[i].kind = "expired" /\ rows[i].sup = FoldNow("st").by
               /\ Offer(Row("st", "expired", "persist", now, {}, NoVU, FoldNow("st").by))

Capture == /\ "ct" \in Planes
           /\ capt[now] = -1 /\ FoldNow("ct").v = "granted"
           /\ capt' = [capt EXCEPT ![now] = Len(rows)]
           /\ UNCHANGED <<now, rows, scored, decay, decayCause, replLive, peerHolds, badSend>>

Score == /\ "st" \in Planes
         /\ scored[now] = -1 /\ FoldNow("st").v = "granted"
         /\ "analyze" \in rows[FoldNow("st").by].scope
         /\ scored' = [scored EXCEPT ![now] = Len(rows)]
         /\ UNCHANGED <<now, rows, capt, decay, decayCause, replLive, peerHolds, badSend>>

StartDecay == /\ decay = "none" /\ FoldNow("st").v \in {"revoked", "expired"}
              /\ decay' = "identity_severed" /\ decayCause' = FoldNow("st").v
              /\ UNCHANGED <<now, rows, capt, scored, replLive, peerHolds, badSend>>
DecayStep == /\ decay \in {"identity_severed", "patterns_anonymized"}
             /\ decay' = Stages[Rank(decay) + 1]
             /\ UNCHANGED <<now, rows, capt, scored, decayCause, replLive, peerHolds, badSend>>

(* consent:replication (CC 3.3.7): directed, one peer per grant, by the node (or its owner, for
   one of its own nodes); a stranger's grant has no standing and is refused.  A withdraws by the
   granting side retracts it whole; the node then ceases sending to that peer. *)
ReplStanding(sg) == sg \in {"node", OwnerAt(now)}
GrantRepl == \E sg \in {"node", "o1", "o2", "stranger"}, p \in Peers :
               /\ "ct" \in Planes /\ p \notin replLive /\ ReplStanding(sg)
               /\ replLive' = replLive \cup {p}
               /\ UNCHANGED <<now, rows, capt, scored, decay, decayCause, peerHolds, badSend>>
RevokeRepl == \E p \in replLive :
               /\ replLive' = replLive \ {p}
               /\ UNCHANGED <<now, rows, capt, scored, decay, decayCause, peerHolds, badSend>>
Replicate == \E p \in Peers :
               /\ p \in replLive
               /\ \E t \in Instants : capt[t] # -1
               /\ peerHolds' = peerHolds \cup {p}
               /\ badSend' = (badSend \/ p \notin replLive)
               /\ UNCHANGED <<now, rows, capt, scored, decay, decayCause, replLive>>

Next == \/ Tick \/ SignSt \/ SignCt \/ EmitExpired
        \/ Capture \/ Score \/ StartDecay \/ DecayStep
        \/ GrantRepl \/ RevokeRepl \/ Replicate

Spec == Init /\ [][Next]_vars /\ WF_vars(StartDecay) /\ WF_vars(DecayStep)

(* ---------------------------------------------------------------- properties ------------ *)
TypeOK == /\ now \in Instants /\ Len(rows) <= MaxRows
          /\ capt \in [Instants -> -1..MaxRows] /\ scored \in [Instants -> -1..MaxRows]
          /\ decay \in {"none", "identity_severed", "patterns_anonymized", "complete"}
          /\ replLive \subseteq Peers /\ peerHolds \subseteq Peers /\ badSend \in BOOLEAN

IsRev(i, s)   == rows[i].series = s /\ rows[i].kind = "revoke"
IsGrant(i, s) == rows[i].series = s /\ rows[i].kind = "grant"
Uses(s) == IF s = "ct" THEN capt ELSE scored

(* CC 3.3.1: no use at an instant after a held revocation unless a grant with a later instant
   (and not after the use) was held.  Judged on what the deciding node held at the use, and
   stated without the fold, so a wrong fold cannot satisfy it by its own lights. *)
BoundaryHolds(s, t) ==
  Uses(s)[t] = -1 \/ \A r \in Pre(Uses(s)[t]) :
     (IsRev(r, s) /\ rows[r].at <= t) =>
        \E g \in Pre(Uses(s)[t]) : IsGrant(g, s) /\ rows[r].at < rows[g].at /\ rows[g].at <= t
Inv_RevocationIsBoundary == \A t \in Instants, s \in Planes : BoundaryHolds(s, t)

(* CC 3.3.1: at equal instants revocation wins.  No use is authorised by a grant whose
   asserted_at equals that of a revocation the deciding node held. *)
TieHolds(s, t) ==
  Uses(s)[t] = -1 \/
  LET g == Fold(s, t, Pre(Uses(s)[t])).by IN
     ~\E r \in Pre(Uses(s)[t]) : IsRev(r, s) /\ rows[r].at = rows[g].at
Inv_RevokedOverridesGranted == \A t \in Instants, s \in Planes : TieHolds(s, t)

(* CC 3.3.1: a row from a key with no standing at its asserted_at never enters the fold. *)
Inv_StrangerNeverGrants ==
  \A i \in Ids :
     /\ rows[i].signer # "stranger"
     /\ IsGrant(i, "ct") => rows[i].signer \in {"node", OwnerAt(rows[i].at)}
     /\ (rows[i].series = "st" /\ rows[i].kind # "expired") => rows[i].signer = "subject"

(* CC 3.3.1 revocation authority, #179: while a grant stands, a revocation signed now by the
   node, by the node's current owner, or by the agent key (ct), or by the subject (st), is
   admitted.  A semantic ENABLED: the model's row budget is not a party's limit. *)
RevNow(s, p) == Row(s, "revoke", p, now, {}, NoVU, 0)
Inv_OwnerCanRecant ==
  /\ ("ct" \in Planes /\ FoldNow("ct").v = "granted") =>
        \A p \in {"node", OwnerAt(now), "agent"} : Admit(RevNow("ct", p), now)
  /\ ("st" \in Planes /\ FoldNow("st").v = "granted") => Admit(RevNow("st", "subject"), now)

(* CC 2.6.7: the withdrawn signer o1 (its owner_binding replaced at TX) keeps at most W of
   backdatable authority: no capture is authorised by an o1 row admitted at or after TX + W. *)
Inv_BackdateBounded ==
  \A t \in Instants :
     capt[t] # -1 =>
        LET g == Fold("ct", t, Pre(capt[t])).by IN
           rows[g].signer = "o1" => rows[g].adm < TX + W

(* CC 2.6.7, the other side: a revocation admitted after a use was decided reaches back to that
   use only if the use's instant is within W of the revocation's asserted_at. *)
LateRevOk(s, t) ==
  Uses(s)[t] = -1 \/ \A i \in Ids :
     (IsRev(i, s) /\ i > Uses(s)[t] /\ rows[i].at <= t) => t <= rows[i].at + W
Inv_LateRevocationWithinW == \A t \in Instants, s \in Planes : LateRevOk(s, t)

(* CC 3.3.1 (#103): a grant naming no scope matches nothing. *)
Inv_EmptyScopeMatchesNothing ==
  \A t \in Instants : scored[t] = -1 \/ "analyze" \in rows[Fold("st", t, Pre(scored[t])).by].scope

(* CC 3.3.1 consent:decay: starts only after revoked or expired; never steps backward. *)
Inv_DecayForwardOnly == decay # "none" => decayCause \in {"revoked", "expired"}
Prop_DecayForwardOnly == [][Rank(decay') >= Rank(decay)]_decay
Prop_DecayCompletes == (decay # "none") ~> (decay = "complete")
Prop_DecayStarts == (<>[](FoldNow("st").v \in {"revoked", "expired"})) => <>(decay # "none")

(* CC 3.3.1: `expired` is the substrate's leaf, never signer-authored; it names a lapsed grant. *)
Inv_ExpiryEmittedBySubstrate ==
  \A i \in Ids : rows[i].kind = "expired" =>
     /\ rows[i].signer = "persist"
     /\ rows[rows[i].sup].kind = "grant" /\ rows[rows[i].sup].vu <= rows[i].at

(* CC 3.3.7: a peer holds the node's traces only under a replication grant naming it. *)
Inv_ReplicationNeedsDirectedGrant == ~badSend

==========================================================================================
