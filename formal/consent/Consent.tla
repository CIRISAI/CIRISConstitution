------------------------------ MODULE Consent ------------------------------
(* The consent plane.

   Two consent series over one receiver's held rows, one fold for both (CC 3.3.1):
     "st"  consent:state  - the subject's stance on a Contribution about them (subject x scope).
           Granted / revoked by the subject (a subject_key_id); `expired` is emitted by the
           substrate (persist) when a grant's valid_until passes, carrying consent_supersedes
           naming the grant; scope is the `scope` member of the granted envelope, and a
           grant naming no scope matches nothing.
     "ct"  consent:community_trust - the capture grant for one node's sealed traces
           (node x community).  Authored by the node or by its owner AT THE HEAD THE GRANT NAMES
           (CC 3.3.1, CC 2.4.1.1): the head is the owner-binding the node signs under, never the
           receiver's current view and never an instant.  A node-authored grant lists that owner in
           subject_key_ids; one that does not is not counted.  A grant whose binding the receiver
           does not hold yet waits.  A grant or revocation from a key that is neither the node, the
           agent key, nor the owner at the head the row names is not this node's consent.
   The fold (CC 3.3.1, normative): the latest admitted revocation's asserted_at is R; every grant
   with asserted_at <= R is out; among grants after R the latest asserted_at wins, ties on the
   smallest attestation id (here: the row index); no grant means no consent.  A revocation is a
   boundary, not a deletion.  The fold over `st` also yields `expired` when the winning grant's
   valid_until has passed (CC 3.3.1 `consent:state:expired`).

   Two readings, kept apart (CC 2.4.1.1: an act names its head, it counts at that head, and no
   instant decides):
     standing  - whether a row is this node's consent at all.  Read at the head the row names.  The
                 row's asserted_at is not read, so no signer gains or loses a standing by the instant
                 it writes, and a later transfer of the node moves no verdict already reached.
     window    - which grants a revocation puts out.  Read from asserted_at: R is the latest admitted
                 revocation's instant and grants at or before R are out.  This is a consent window,
                 not a standing, and it is unchanged.
   Admission freshness (CC 2.6.7): the instant is signer-chosen, so it is bounded: a row whose
   asserted_at precedes the receiver's clock by more than W is refused (asserted_at_stale) and
   moves nothing.  CC 2.6.7: "The window decides no standing."

   Ownership: binding B1 (owner O1) is the node's owner-binding from the start.  At receiver-clock
   TX it is replaced by B2 (owner O2), an owner_binding withdrawn and replaced (CC 3.2).  B2 reaches
   this receiver at TX or at any later step (hb2).  O1 is the withdrawn owner: a device of O1 that
   has not seen B2, or will not, may still sign at head B1 (CC 2.4.1.1 "the limit": no reader can
   tell that act from an honest earlier one).

   InForce picks what a replaced binding does to a grant that counted under it.  The text gives two
   sentences and this module does not choose between them; each is a configuration:
     "counts"  - CC 3.3.1 read alone: "a later ownership transfer neither admits nor un-admits a grant
                 already made".  A grant that counted at B1 stays in the fold whatever the receiver
                 holds later.
     "ends"    - CC 3.1.2.1 and CC 2.4.1.1: "Once a reader holds the binding that replaced an act's
                 own, that act is in force for nobody unless it was receipted."  From the step the
                 receiver holds B2, a grant at head B1 is out of the fold; its verdict (it counted at
                 B1) is not changed.  Receipts are not modelled, so no B1 grant is kept in force.

   Uses of consent (each a conforming node's act, gated on the fold at the use's instant):
     Capture  - a sealed trace at instant `now` is captured iff the ct fold says granted.
     Score    - an `analyze` use at `now` iff the st fold says granted and the winning grant's
                scope contains analyze (CC 3.4.5 context).
     Replicate- the node ships captured traces to peer p iff a live consent:replication grant
                (CC 3.3.7) names p; the grant is the node's or its owner's, directed, per peer.
   Replication touches the rest of the plane at one point only: the node sends once some capture
   exists.  So the configurations that search the capture fold run with no peer (Peers = {}), and
   one configuration (Consent_replication.cfg) runs two peers over a smaller row budget.
   Decay (CC 3.3.1 consent:decay:{stage}): the agent's consent module walks identity_severed ->
   patterns_anonymized -> complete once the st fold reads revoked or expired.

   The adversary: signs any row as a stranger; signs as the withdrawn owner O1 after TX, at head B1
   or naming B2, with any asserted_at; names any binding that exists, or none, on any row; backdates
   any party's row within and beyond W; replays any row already signed; forges `expired` under a
   non-substrate key; grants replication as a stranger.

   Mode picks the reading under test:
     "ruled"          - the CC 3.3.1 fold, standing at the named head, the CC 2.6.7 W bound.
     "instant"        - the reading this module had before: the owner is the owner at the row's
                        asserted_at, and the head a row names is not read.  A planted break.
     "current_view"   - the owner is the owner by the newest binding the receiver holds (the reading
                        CC 3.3.1 excludes by name).  A planted break.
     "no_boundary"    - the latest grant wins regardless of revocation.
     "literal_signer" - only the node may revoke a community_trust grant (the reading
                        that the owner speaks only through the node).
     "no_W"           - no freshness bound: a backdated row is admitted however old.
   Seven more planted breaks, one action each, so that no property stands only on an action's own
   guard: "any_scope" (an analyze use on a grant of any scope), "forged_expiry" (an `expired` row
   from any key, naming any row), "eager_decay" (decay starts under a live grant), "decay_back" (a
   decay step may go back), "decay_stalls" (decay stops at identity_severed), "decay_never" (decay
   does not start), "blind_send" (the node sends to a peer no grant names).                     *)
EXTENDS Integers, FiniteSets, Sequences

CONSTANTS Mode, Planes, MaxT, W, TX, Life, MaxRows, InForce, Peers
ASSUME Mode \in {"ruled", "no_boundary", "literal_signer", "no_W", "instant", "current_view",
                 "any_scope", "forged_expiry", "eager_decay", "decay_back", "decay_stalls", "decay_never", "blind_send"}
ASSUME InForce \in {"counts", "ends"}
ASSUME Planes \subseteq {"st", "ct"} /\ Planes # {}
ASSUME TX \in 1..MaxT /\ W \in 1..MaxT /\ Life \in 1..MaxT

Instants == 0..MaxT
NoVU     == MaxT + 100                  \* "no valid_until"
Stages   == <<"none", "identity_severed", "patterns_anonymized", "complete">>
Rank(s)  == CHOOSE i \in 1..4 : Stages[i] = s

(* The node's owner-bindings: one row between two keys is the whole record, so the row is the head
   (CC 2.4.1.1).  0 stands for a row that names no head. *)
Owner(b)       == IF b = 1 THEN "o1" ELSE "o2"
HeldB(b, hb)   == b = 1 \/ (b = 2 /\ hb)          \* hb: the receiver holds B2
CurOwner(hb)   == IF hb THEN "o2" ELSE "o1"       \* the receiver's current view (plant "current_view")
OwnerAtInstant(t) == IF t < TX THEN "o1" ELSE "o2" \* the owner by an instant (plant "instant")

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
          badSend,   \* a send to a peer with no live grant naming it happened
          hb2,       \* the receiver holds B2, the binding that replaced B1
          captB      \* [Instants -> BOOLEAN]: the capture at that instant was decided holding B2
vars == <<now, rows, capt, scored, decay, decayCause, replLive, peerHolds, badSend, hb2, captB>>

Ids     == 1..Len(rows)
Pre(k)  == 1..k                       \* what a use decided at prefix k saw

(* ---------------------------------------------------------------- standing ------------- *)
(* A community_trust row's verdict, as a receiver that does (hb) or does not hold B2 reaches it:
   "wait" (a binding it names has not arrived), "counts", or "void" (kept, and no consent of this
   node's).  Under the ruled reading it reads the row's signer, the head it names and the owner it
   lists, and nothing else: not asserted_at, not the clock, not the receiver's newest binding. *)
CtVerdict(r, hb) ==
  LET yes(b) == IF b THEN "counts" ELSE "void" IN
  CASE Mode = "instant" ->
          IF r.kind = "grant" THEN yes(r.signer \in {"node", OwnerAtInstant(r.at)})
          ELSE yes(r.signer \in {"node", OwnerAtInstant(r.at), "agent"})
    [] Mode = "current_view" ->
          IF r.kind = "grant"
          THEN yes(r.signer = CurOwner(hb) \/ (r.signer = "node" /\ r.lst = CurOwner(hb)))
          ELSE yes(r.signer \in {"node", CurOwner(hb), "agent"})
    [] OTHER ->
          IF r.kind = "grant"
          THEN IF r.head \notin {1, 2} THEN "void"                    \* act_names_no_head
               ELSE IF ~HeldB(r.head, hb) THEN "wait"
               ELSE yes(\/ r.signer = Owner(r.head)
                        \/ r.signer = "node" /\ r.lst = Owner(r.head))
          ELSE IF Mode = "literal_signer" THEN yes(r.signer = "node")
               ELSE IF r.signer \in {"node", "agent"} THEN "counts"
               ELSE IF r.head \notin {1, 2} THEN "void"
               ELSE IF ~HeldB(r.head, hb) THEN "wait"
               ELSE yes(r.signer = Owner(r.head))

Standing(r) ==
  CASE r.series = "st" /\ r.kind \in {"grant", "revoke"} -> r.signer = "subject"
    [] r.series = "st" /\ r.kind = "expired" ->
          /\ r.sup \in Ids
          /\ \/ Mode = "forged_expiry"
             \/ /\ r.signer = "persist"
                /\ rows[r.sup].kind = "grant" /\ rows[r.sup].series = "st"
                /\ rows[r.sup].vu <= r.at
    [] r.series = "ct" /\ r.kind \in {"grant", "revoke"} -> CtVerdict(r, hb2) = "counts"
    [] OTHER -> FALSE

Fresh(r, t) == Mode = "no_W" \/ t - r.at <= W

(* A refused row (asserted_at_stale), a void row and a waiting row are not admitted: each moves
   nothing, so the model has no transition for it.  A waiting row is offered again once B2 is held.
   Replay of an admitted row dedups on its attestation id and is likewise no transition; replay of a
   refused row is re-judged at a later clock, where staleness only grows, and its standing is read
   from the head it names, so it reaches the verdict it reached before. *)
Admit(r, t) == Fresh(r, t) /\ Standing(r)

(* ---------------------------------------------------------------- the fold -------------- *)
(* hb: the deciding node holds B2.  Under InForce = "ends" a ct grant at the replaced binding is not
   in force for a node that holds its replacement; under "counts" every admitted grant is read. *)
Live(i, hb) == InForce = "counts" \/ rows[i].series # "ct" \/ ~hb \/ rows[i].head = 2
GrantsAt(s, t, H, hb) == {i \in H : rows[i].series = s /\ rows[i].kind = "grant" /\ rows[i].at <= t /\ Live(i, hb)}
RevokesAt(s, t, H) == {i \in H : rows[i].series = s /\ rows[i].kind = "revoke" /\ rows[i].at <= t}
MaxAt(S) == CHOOSE m \in {rows[i].at : i \in S} : \A i \in S : rows[i].at <= m
Bound(s, t, H) ==
  IF Mode = "no_boundary" \/ RevokesAt(s, t, H) = {} THEN -1 ELSE MaxAt(RevokesAt(s, t, H))
After(s, t, H, hb) == {i \in GrantsAt(s, t, H, hb) : rows[i].at > Bound(s, t, H)}
Winner(S) == CHOOSE i \in S : \A j \in S : rows[j].at < rows[i].at
                                          \/ (rows[j].at = rows[i].at /\ i <= j)
Fold(s, t, H, hb) ==
  IF After(s, t, H, hb) = {}
  THEN [v |-> IF Bound(s, t, H) >= 0 THEN "revoked" ELSE "none", by |-> 0]
  ELSE LET g == Winner(After(s, t, H, hb)) IN
       [v |-> IF t >= rows[g].vu THEN "expired" ELSE "granted", by |-> g]

FoldNow(s) == Fold(s, now, Ids, hb2)
UseHb(s, t) == s = "ct" /\ captB[t]            \* what the node that decided the use at t held
UseFold(s, t, k) == Fold(s, t, Pre(k), UseHb(s, t))

(* ---------------------------------------------------------------- init ------------------ *)
Init == /\ now = 0 /\ rows = <<>>
        /\ capt = [t \in Instants |-> -1] /\ scored = [t \in Instants |-> -1]
        /\ decay = "none" /\ decayCause = "none"
        /\ replLive = {} /\ peerHolds = {} /\ badSend = FALSE
        /\ hb2 = FALSE /\ captB = [t \in Instants |-> FALSE]

(* ---------------------------------------------------------------- actions --------------- *)
Tick == /\ now < MaxT /\ now' = now + 1
        /\ UNCHANGED <<rows, capt, scored, decay, decayCause, replLive, peerHolds, badSend, hb2, captB>>

(* B2 exists from TX and reaches this receiver then or at any later step.  Nothing forces it: a
   receiver may never hold it. *)
ArriveB2 == /\ "ct" \in Planes /\ now >= TX /\ ~hb2
            /\ hb2' = TRUE
            /\ UNCHANGED <<now, rows, capt, scored, decay, decayCause, replLive, peerHolds, badSend, captB>>

(* head: the binding the row names (0: none).  lst: the owner a node-authored grant lists in
   subject_key_ids ("none": it lists no owner).  adm, ahb: the clock, and whether B2 was held, when the
   receiver admitted the row. *)
RowH(s, k, sg, a, sc, vu, sup, h, l) ==
  [series |-> s, kind |-> k, signer |-> sg, at |-> a, scope |-> sc, vu |-> vu, sup |-> sup,
   head |-> h, lst |-> l, adm |-> 0, ahb |-> FALSE]
Row(s, k, sg, a, sc, vu, sup) == RowH(s, k, sg, a, sc, vu, sup, 0, "none")

Offer(r) == /\ Len(rows) < MaxRows
            /\ Admit(r, now)
            /\ rows' = Append(rows, [r EXCEPT !.adm = now, !.ahb = hb2])
            /\ UNCHANGED <<now, capt, scored, decay, decayCause, replLive, peerHolds, badSend, hb2, captB>>

(* Any party, or the adversary in its name, signs a row with an asserted_at of its choosing. *)
SignSt == /\ "st" \in Planes
          /\ \E sg \in StSigners, a \in 0..now :
               \/ \E v \in {[sc |-> {}, vu |-> NoVU], [sc |-> {"analyze"}, vu |-> NoVU],
                            [sc |-> {"analyze"}, vu |-> a + Life]} :
                     Offer(Row("st", "grant", sg, a, v.sc, v.vu, 0))
               \/ Offer(Row("st", "revoke", sg, a, {}, NoVU, 0))
               \/ \E g \in Ids : Offer(Row("st", "expired", sg, a, {}, NoVU, g))  \* forged expiry
(* A row names a binding that exists (B2 from TX), or none.  A node's or the agent key's revocation
   is read off the row alone, so the head it names is not varied. *)
HeadsNow == {h \in {0, 1, 2} : h = 2 => now >= TX}
CtShapes(sg, k) ==
  IF k = "grant" THEN {[h |-> h, l |-> l] : h \in HeadsNow, l \in IF sg = "node" THEN {"o1", "o2", "none"} ELSE {"none"}}
  ELSE IF sg \in {"node", "agent"} THEN {[h |-> 0, l |-> "none"]}
  ELSE {[h |-> h, l |-> "none"] : h \in HeadsNow}
SignCt == /\ "ct" \in Planes
          /\ \E sg \in CtSigners, a \in 0..now, k \in {"grant", "revoke"} :
               \E x \in CtShapes(sg, k) : Offer(RowH("ct", k, sg, a, {}, NoVU, 0, x.h, x.l))

(* The substrate's own leaf: expired, naming the lapsed grant (consent_supersedes). *)
EmitExpired == /\ "st" \in Planes
               /\ FoldNow("st").v = "expired"
               /\ ~\E i \in Ids : rows[i].kind = "expired" /\ rows[i].sup = FoldNow("st").by
               /\ Offer(Row("st", "expired", "persist", now, {}, NoVU, FoldNow("st").by))

Capture == /\ "ct" \in Planes
           /\ capt[now] = -1 /\ FoldNow("ct").v = "granted"
           /\ capt' = [capt EXCEPT ![now] = Len(rows)]
           /\ captB' = [captB EXCEPT ![now] = hb2]
           /\ UNCHANGED <<now, rows, scored, decay, decayCause, replLive, peerHolds, badSend, hb2>>

Score == /\ "st" \in Planes
         /\ scored[now] = -1 /\ FoldNow("st").v = "granted"
         /\ (Mode = "any_scope" \/ "analyze" \in rows[FoldNow("st").by].scope)
         /\ scored' = [scored EXCEPT ![now] = Len(rows)]
         /\ UNCHANGED <<now, rows, capt, decay, decayCause, replLive, peerHolds, badSend, hb2, captB>>

StartDecay == /\ decay = "none" /\ Mode # "decay_never"
              /\ (Mode = "eager_decay" \/ FoldNow("st").v \in {"revoked", "expired"})
              /\ decay' = "identity_severed" /\ decayCause' = FoldNow("st").v
              /\ UNCHANGED <<now, rows, capt, scored, replLive, peerHolds, badSend, hb2, captB>>
DecayStep == /\ decay \in {"identity_severed", "patterns_anonymized"}
             /\ Mode # "decay_stalls"
             /\ \/ decay' = Stages[Rank(decay) + 1]
                \/ Mode = "decay_back" /\ decay = "patterns_anonymized" /\ decay' = "identity_severed"
             /\ UNCHANGED <<now, rows, capt, scored, decayCause, replLive, peerHolds, badSend, hb2, captB>>

(* consent:replication (CC 3.3.7): directed, one peer per grant, by the node (or its owner, for
   one of its own nodes); a stranger's grant has no standing and is refused.  A withdraws by the
   granting side retracts it whole; the node then ceases sending to that peer.  The grant is no row
   here and names no head: its owner is the owner at a binding the receiver holds.  What a replaced
   binding does to a replication grant is not modelled. *)
ReplStanding(sg) == sg = "node" \/ \E b \in {1, 2} : HeldB(b, hb2) /\ sg = Owner(b)
GrantRepl == \E sg \in {"node", "o1", "o2", "stranger"}, p \in Peers :
               /\ "ct" \in Planes /\ p \notin replLive /\ ReplStanding(sg)
               /\ replLive' = replLive \cup {p}
               /\ UNCHANGED <<now, rows, capt, scored, decay, decayCause, peerHolds, badSend, hb2, captB>>
RevokeRepl == \E p \in replLive :
               /\ replLive' = replLive \ {p}
               /\ UNCHANGED <<now, rows, capt, scored, decay, decayCause, peerHolds, badSend, hb2, captB>>
Replicate == \E p \in Peers :
               /\ (Mode = "blind_send" \/ p \in replLive)
               /\ \E t \in Instants : capt[t] # -1
               /\ peerHolds' = peerHolds \cup {p}
               /\ badSend' = (badSend \/ p \notin replLive)
               /\ UNCHANGED <<now, rows, capt, scored, decay, decayCause, replLive, hb2, captB>>

Next == \/ Tick \/ ArriveB2 \/ SignSt \/ SignCt \/ EmitExpired
        \/ Capture \/ Score \/ StartDecay \/ DecayStep
        \/ GrantRepl \/ RevokeRepl \/ Replicate

Spec == Init /\ [][Next]_vars /\ WF_vars(StartDecay) /\ WF_vars(DecayStep)

(* ---------------------------------------------------------------- properties ------------ *)
TypeOK == /\ now \in Instants /\ Len(rows) <= MaxRows
          /\ capt \in [Instants -> -1..MaxRows] /\ scored \in [Instants -> -1..MaxRows]
          /\ decay \in {"none", "identity_severed", "patterns_anonymized", "complete"}
          /\ replLive \subseteq Peers /\ peerHolds \subseteq Peers /\ badSend \in BOOLEAN
          /\ hb2 \in BOOLEAN /\ captB \in [Instants -> BOOLEAN]

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
  LET g == UseFold(s, t, Uses(s)[t]).by IN
     ~\E r \in Pre(Uses(s)[t]) : IsRev(r, s) /\ rows[r].at = rows[g].at
Inv_RevokedOverridesGranted == \A t \in Instants, s \in Planes : TieHolds(s, t)

(* CC 3.3.1, CC 2.4.1.1: a row from a key with no standing at the head it names never enters the
   fold.  Stated on the held rows and without CtVerdict, so a wrong standing rule cannot satisfy it
   by its own lights: a held capture grant names a binding, and is that binding's owner's, or the
   node's and lists that owner. *)
Inv_StrangerNeverGrants ==
  \A i \in Ids :
     /\ rows[i].signer # "stranger"
     /\ IsGrant(i, "ct") =>
           /\ rows[i].head \in {1, 2}
           /\ \/ rows[i].signer = Owner(rows[i].head)
              \/ rows[i].signer = "node" /\ rows[i].lst = Owner(rows[i].head)
     /\ IsRev(i, "ct") =>
           \/ rows[i].signer \in {"node", "agent"}
           \/ rows[i].head \in {1, 2} /\ rows[i].signer = Owner(rows[i].head)
     /\ (rows[i].series = "st" /\ rows[i].kind # "expired") => rows[i].signer = "subject"

(* CC 2.4.1.1 "no instant decides": the withdrawn owner holds nothing at B2, whatever instant it
   writes.  A held grant of o1's that names B2 was signed at or after TX, since B2 did not exist
   before; under the instant reading it is admitted exactly when it is dated before TX. *)
Inv_BackdatedGrantRefused ==
  ~\E i \in Ids : IsGrant(i, "ct") /\ rows[i].signer = "o1" /\ rows[i].head = 2

(* Every community_trust row the adversary can write, for the three checks of form below.  They
   read constants and hb2 only, so a configuration with no row budget checks them. *)
CtCand == {RowH("ct", k, sg, a, {}, NoVU, 0, h, l) :
             k \in {"grant", "revoke"}, sg \in CtSigners, a \in Instants, h \in {0, 1, 2}, l \in {"o1", "o2", "none"}}

(* CC 2.4.1.1: nobody gains or loses a standing by choosing an instant.  Two rows that differ in
   asserted_at alone reach one verdict. *)
Inv_InstantBuysNoStanding ==
  \A r \in CtCand, a \in Instants, hb \in BOOLEAN : CtVerdict([r EXCEPT !.at = a], hb) = CtVerdict(r, hb)

(* CC 3.3.1: "every peer reaches the same verdict once the binding rows have replicated".  A receiver
   that has not B2 either waits or reaches the verdict a receiver holding B2 reaches. *)
Inv_SameVerdictOnceHeld ==
  \A r \in CtCand : CtVerdict(r, FALSE) \in {"wait", CtVerdict(r, TRUE)}

(* CC 3.3.1: "a later ownership transfer neither admits nor un-admits a grant already made", read
   of the verdict: at the step B2 arrives, no row that had a verdict gets another.  An action
   property. *)
Prop_TransferMovesNoVerdict ==
  [][hb2' # hb2 => \A r \in CtCand : CtVerdict(r, hb2) # "wait" => CtVerdict(r, hb2') = CtVerdict(r, hb2)]_vars

(* The same sentence read of the fold: at the step B2 arrives the capture fold is what it was.
   Holds under InForce = "counts" and not under "ends". *)
Prop_TransferKeepsFold == [][hb2' # hb2 => FoldNow("ct")' = FoldNow("ct")]_vars

(* CC 3.1.2.1: "Once a reader holds the binding that replaced an act's own, that act is in force for
   nobody unless it was receipted."  No capture decided by a node that held B2 rests on a grant at
   B1.  Stated on the rows the use saw.  Holds under InForce = "ends" and not under "counts". *)
Inv_ReplacedBindingEndsGrant ==
  \A t \in Instants :
     (capt[t] # -1 /\ captB[t]) => rows[UseFold("ct", t, capt[t]).by].head = 2

(* CC 3.3.1 revocation authority: while a grant stands, a revocation signed now by the node, by
   the agent key, or by the owner at any binding the receiver holds, naming that binding, is
   admitted: the listed owner "whatever ownership later becomes", and the new owner in its own
   voice.  The subject likewise (st).  A semantic ENABLED: the model's row budget is not a party's
   limit. *)
RevNow(s, p) == Row(s, "revoke", p, now, {}, NoVU, 0)
RevNowAt(b)  == RowH("ct", "revoke", Owner(b), now, {}, NoVU, 0, b, "none")
Inv_OwnerCanRecant ==
  /\ ("ct" \in Planes /\ FoldNow("ct").v = "granted") =>
        /\ \A p \in {"node", "agent"} : Admit(RevNow("ct", p), now)
        /\ \A b \in {1, 2} : HeldB(b, hb2) => Admit(RevNowAt(b), now)
  /\ ("st" \in Planes /\ FoldNow("st").v = "granted") => Admit(RevNow("st", "subject"), now)

(* CC 2.6.7: a row dated more than W before the receiver's clock is refused asserted_at_stale and
   moves nothing.  Stated on the held rows.  The window bounds the signer-chosen instant that the
   boundary fold reads; it decides no standing. *)
Inv_BackdateBounded == \A i \in Ids : rows[i].adm - rows[i].at <= W

(* CC 2.6.7, the other side: a revocation admitted after a use was decided reaches back to that
   use only if the use's instant is within W of the revocation's asserted_at. *)
LateRevOk(s, t) ==
  Uses(s)[t] = -1 \/ \A i \in Ids :
     (IsRev(i, s) /\ i > Uses(s)[t] /\ rows[i].at <= t) => t <= rows[i].at + W
Inv_LateRevocationWithinW == \A t \in Instants, s \in Planes : LateRevOk(s, t)

(* CC 3.3.1: a grant naming no scope matches nothing. *)
Inv_EmptyScopeMatchesNothing ==
  \A t \in Instants : scored[t] = -1 \/ "analyze" \in rows[UseFold("st", t, scored[t]).by].scope

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

(* ---------------------------------------------------------------- witnesses ------------- *)
(* Each Wit_* is the negation of a scenario that must be REACHABLE under the CC reading; a
   witness configuration lists one and TLC must report it violated (the scenario happens). *)
Wit_OldHeadAfterTransfer ==
                      ~\E t \in Instants : capt[t] # -1 /\
                         LET g == UseFold("ct", t, capt[t]).by IN
                            rows[g].signer = "o1" /\ rows[g].head = 1 /\ rows[g].adm >= TX
Wit_OldHeadWhileHoldingB2 ==
                      ~\E i \in Ids : IsGrant(i, "ct") /\ rows[i].head = 1 /\ rows[i].ahb
Wit_CaptureHoldingB2 == ~\E t \in Instants : capt[t] # -1 /\ captB[t]
Wit_NewOwnerGrants == ~\E i \in Ids : IsGrant(i, "ct") /\ rows[i].signer = "o2" /\ rows[i].head = 2
Wit_NodeRegrants   == ~\E i \in Ids : IsGrant(i, "ct") /\ rows[i].signer = "node" /\ rows[i].head = 2
Wit_NodeGrantsAtB1 == ~\E i \in Ids : IsGrant(i, "ct") /\ rows[i].signer = "node" /\ rows[i].head = 1
Wit_O1RevokesHoldingB2 ==
                      ~\E i \in Ids : IsRev(i, "ct") /\ rows[i].signer = "o1" /\ rows[i].ahb
Wit_FoldEndsOnArrival ==
                      ~(hb2 /\ FoldNow("ct").v = "none" /\ \E i \in Ids : IsGrant(i, "ct") /\ rows[i].head = 1 /\ ~rows[i].ahb)
Wit_BackdatedWithinW == ~\E i \in Ids : IsGrant(i, "ct") /\ rows[i].at < rows[i].adm
Wit_LateRevocation == ~\E t \in Instants, i \in Ids :
                         capt[t] # -1 /\ IsRev(i, "ct") /\ i > capt[t] /\ rows[i].at <= t
Wit_FreshGrantAfterRevocation ==
                      ~\E t \in Instants : capt[t] # -1 /\ \E r \in Pre(capt[t]) : IsRev(r, "ct") /\ rows[r].at <= t
Wit_AgentRevokes   == ~\E i \in Ids : IsRev(i, "ct") /\ rows[i].signer = "agent"
Wit_O2Revokes      == ~\E i \in Ids : IsRev(i, "ct") /\ rows[i].signer = "o2"
Wit_PeerHolds      == peerHolds = {}
Wit_ExpiredEmitted == ~\E i \in Ids : rows[i].kind = "expired"
Wit_DecayComplete  == decay # "complete"
Wit_DecayOnExpiry  == decayCause # "expired"
Wit_ScoreAfterRevocation ==
                      ~\E t \in Instants : scored[t] # -1 /\ \E r \in Pre(scored[t]) : IsRev(r, "st") /\ rows[r].at <= t

==========================================================================================
