------------------------- MODULE TrustRootVerdict -------------------------
(***************************************************************************)
(* CC 3.2 T8: the standing verdict V(rows, t) as a state machine.           *)
(*                                                                          *)
(* One evaluating node and one root. The root is the lineage of a genesis   *)
(* bundle (T5). Its head is the bundle in force, and a later bundle naming  *)
(* `prev` moves it (T6). There is no separate head object and nothing       *)
(* cosigns one. The rows the node holds:                                    *)
(*                                                                          *)
(*   - the lineage's bundles: g (version 1), a2 and b2 (version 2, both on  *)
(*     g: the one fork), and with Deep a3 (version 3, on a2). A later       *)
(*     bundle is an amend carrying the statements of some holders, or one   *)
(*     holder's recovery under its recovery key (CC 4.2.6, CC 2.6.1.11);    *)
(*   - the Receipts held for each bundle: how many distinct services'       *)
(*     Receipts count, up to the quorum, and the instant of the newest (T6);*)
(*   - key revocations with their `revoked_after` bound: of each holder's   *)
(*     genesis key and of the acceptance edge's signer; and a service's,    *)
(*     as a Receipt that falls out of the count;                            *)
(*   - the acceptance edge: none, present (naming a head and carrying its   *)
(*     own signed instant), withdrawn, recanted or tombstoned (T3).         *)
(*                                                                          *)
(* The verdict is VAt(t) below, for every signer-stamped instant t. The     *)
(* evaluating clock is the variable `clock`; VAt never reads it.            *)
(*                                                                          *)
(* Four things T8 says V does not read are not state here. They are         *)
(* arguments (the record E and the set X), and an invariant quantifies over *)
(* every value of each: the halt latch (v), the founder margin of an        *)
(* `infrastructure` room (T7), the evaluating clock (ii), and the bundles a *)
(* node-bearing seat has signed (i). A planted fault makes the machine read *)
(* one of them and the invariant then fails.                                *)
(*                                                                          *)
(* The fork bundle b2 always carries a charter that names services of its   *)
(* own, and those services have always issued their Receipts for it: a fork *)
(* chooses its own charter, and Receipts from services the forker runs cost *)
(* it nothing. The machine never counts them (the predecessor rule, T6).    *)
(*                                                                          *)
(* Plant = "none" is the machine. Every other value of Plant is one         *)
(* deliberately wrong reading, named in the README beside the invariant     *)
(* that must catch it.                                                      *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
    Holders,        \* the holders every bundle of the lineage lists
    NServices,      \* how many Transparency Services issue Receipts
    Named,          \* TRUE: the genesis charter names those services; FALSE: it names none
    Faulty,         \* how many of them may issue a Receipt for two bundles at one version
    Uncountable,    \* TRUE: a service's key may be revoked below a Receipt it issued
    Fork,           \* TRUE: a second bundle at version 2, b2 on g beside a2
    Deep,           \* TRUE: a third version, a3 on a2
    MaxT,           \* last instant
    AttachWindow,   \* attach_window_secs, in ticks
    Skew,           \* the skew tolerance an edge's own instant is held to at admission
    MaxRevs,        \* bound: key revocation rows of holders and of the edge's signer, lowerings included
    Plant           \* "none", or the name of one planted fault

ASSUME NServices >= 2 /\ Faulty \in 0..NServices
ASSUME Named \in BOOLEAN /\ Uncountable \in BOOLEAN /\ Fork \in BOOLEAN /\ Deep \in BOOLEAN
ASSUME Cardinality(Holders) >= 3 /\ MaxT >= 2 /\ AttachWindow >= 1

G == "g"
A2 == "a2"
B2 == "b2"
A3 == "a3"
NoHead == "none"

HeadIds == {G, A2} \cup (IF Fork THEN {B2} ELSE {}) \cup (IF Deep THEN {A3} ELSE {})
NonG == HeadIds \ {G}
Prev(b) == CASE b = A2 -> G [] b = B2 -> G [] b = A3 -> A2 [] OTHER -> NoHead
Ver(b) == CASE b = G -> 1 [] b = A2 -> 2 [] b = B2 -> 2 [] b = A3 -> 3 [] OTHER -> 0
Chain(b) == CASE b = G -> {G} [] b = A2 -> {G, A2} [] b = B2 -> {G, B2}
              [] b = A3 -> {G, A2, A3} [] OTHER -> {}
(* A bundle's own asserted_at. It is fixed by the version, so that a bound  *)
(* of 0 or 1 unmakes every statement over version 2, and 2 leaves version   *)
(* 2. No bound unmakes the first bundle (CC 2.6.1.11).                      *)
HAt(b) == Ver(b) - 1
Anchor == G                      \* the head held out of band (T5): the pinned genesis

Instants == 0..MaxT
Never == MaxT + 1                \* no revocation; no Receipt
Bounds == 0..Never
Quorum == (NServices \div 2) + 1                      \* receipt_quorum = floor(n/2) + 1
Maj(S) == 2 * Cardinality(S) > Cardinality(Holders)   \* a strict majority of the holders
Ended == {"withdrawn", "recanted", "tombstoned"}

Rooted == "Rooted"
Stalled == "Stalled"
NotRooted == "NotRooted"

VARIABLES
    clock,      \* the evaluating node's clock
    held,       \* the bundles of the lineage the node holds
    sig,        \* [NonG -> SUBSET Holders]: whose statements over an amend are held
    rec,        \* [NonG -> SUBSET Holders]: the holder a recovery bundle recovers, or {}
    krev,       \* [Holders -> Bounds]: revoked_after of each holder's genesis key
    nrev,       \* how many key revocation rows of holders and the edge's signer were admitted
    rN,         \* [HeadIds -> 0..Quorum]: distinct services whose Receipt for a bundle counts
    rAt,        \* [HeadIds -> Bounds]: issue instant of the newest such Receipt
    uncount,    \* history: a Receipt once counted fell out of the count
    orev,       \* revoked_after of the key that signed the acceptance edge
    edge,       \* "none", "present", or how the edge ended
    edgeHead,   \* attached_head_digest: the bundle the edge names
    edgeAt,     \* the edge's own signed instant
    endAt,      \* read by one plant only: the instant the edge was ended
    cur         \* the bundle in force for this node: the head it has adopted

rows == << clock, held, sig, rec, krev, nrev, rN, rAt, uncount, orev >>
vars == << clock, held, sig, rec, krev, nrev, rN, rAt, uncount, orev,
           edge, edgeHead, edgeAt, endAt, cur >>

-----------------------------------------------------------------------------
(* The count of a bundle, read at read time (CC 2.6.1.11, T8 viii).          *)
(* H is the set of bundles read; X is the set of bundles a node-bearing     *)
(* seat has signed, which nothing here may read (i).                        *)

(* h was recovered at b or at an ancestor of b: the bundle seats a new key for it. *)
RecBy(h, b, H) == \E a \in (Chain(b) \cap H) \ {G} : h \in rec[a]

(* A statement under a genesis key stands iff the bundle's instant precedes the
   key's revoked_after (CC 2.4.1.1). *)
KeyGood(h, at) ==
    IF Plant = "revocation_reaches_behind" THEN krev[h] = Never ELSE at < krev[h]

(* h's statement over b counts, under the key b's predecessor seats for h. *)
StmtOK(h, b, H) == h \in sig[b] /\ (RecBy(h, Prev(b), H) \/ KeyGood(h, HAt(b)))

(* The first bundle counts once every holder it lists has made a valid
   statement over it, and a bound on a holder's key never unmakes that count
   (CC 2.6.1.11). The node holds g from the first state with every holder's
   statement made under a key with no bound, so its count stands. *)
Counted(b, H, X) ==
    IF b = G THEN Plant = "bound_unmakes_first" => \A h \in Holders : KeyGood(h, HAt(G))
    ELSE IF rec[b] # {} THEN TRUE                               \* one statement, the recovery key's
    ELSE 2 * (Cardinality({h \in Holders : StmtOK(h, b, H)})
              + (IF Plant = "seat_counts" /\ b \in X THEN 1 ELSE 0)) > Cardinality(Holders)

Verifies(b, H, X) == \A a \in Chain(b) : a \in H /\ Counted(a, H, X)

-----------------------------------------------------------------------------
(* Receipted (T6). A Receipt for a head is verified against the services of
   that head's predecessor, and for the first bundle against its own charter. *)

OwnSvc(b) == IF b = B2 THEN "own" ELSE IF Named THEN "named" ELSE "none"
JudgeSvc(b) == IF Plant = "own_charter" THEN OwnSvc(b)
               ELSE IF b = G THEN OwnSvc(G) ELSE OwnSvc(Prev(b))
ByReceipt(b) == JudgeSvc(b) # "none"

Receipted(b) ==
    CASE JudgeSvc(b) = "named" -> rN[b] >= Quorum
      [] JudgeSvc(b) = "own"   -> TRUE          \* the fork's own services have issued for it
      [] OTHER                 -> Plant = "unnamed_receipts_count" /\ rN[b] >= Quorum

(* The same, written from the text alone, for the invariants to compare against. *)
RefReceipted(b) == Named /\ rN[b] >= Quorum

(* Fresh: the newest counted Receipt was issued within the window before the
   attaching edge's own signed instant e (T4a). *)
FreshAt(b, e) == rAt[b] <= e /\ e <= rAt[b] + AttachWindow
FreshGate(b, e) ==
    IF JudgeSvc(b) = "own" THEN TRUE
    ELSE IF Plant = "fresh_by_clock" THEN rAt[b] <= clock /\ clock <= rAt[b] + AttachWindow
    ELSE FreshAt(b, e)

(* Two heads at one version, neither descending from the other, each receipted. *)
BothVerify(H, X) == A2 \in H /\ B2 \in H /\ Verifies(A2, H, X) /\ Verifies(B2, H, X)
Equivocation(H, X) == BothVerify(H, X) /\ Receipted(A2) /\ Receipted(B2)
RefEquivocation == BothVerify(held, {}) /\ RefReceipted(A2) /\ RefReceipted(B2)
(* A head counted by the holders that does not descend from the receipted head. *)
ForkAttempt(H, X) == BothVerify(H, X) /\ (Receipted(A2) # Receipted(B2))
Frozen(H, X) ==
    \/ Equivocation(H, X)
    \/ Plant = "fork_freezes" /\ ForkAttempt(H, X)

-----------------------------------------------------------------------------
(* The bundle in force for the node. From the head c it stands on, it falls
   back to the nearest ancestor that still verifies (viii), and then follows
   later bundles: receipted ones where the predecessor names services,
   counted ones where it names none. A frozen lineage adopts no head. Where
   no services are named, two counted bundles on one predecessor wait as
   tips and neither is adopted, whichever came first (CC 2.6.1.11). *)

Succ(c, H, X) == { s \in H : Prev(s) = c /\ Counted(s, H, X) /\ (ByReceipt(s) => Receipted(s)) }

Adv1(c, H, X) ==
    IF c = NoHead \/ Frozen(H, X) THEN c
    ELSE LET next == Succ(c, H, X) IN
         IF Cardinality(next) = 1 THEN CHOOSE s \in next : TRUE ELSE c

Retreat(c, H, X) ==
    IF c = NoHead \/ Plant = "unmade_head_stays" THEN c
    ELSE LET ok == { a \in Chain(c) : Verifies(a, H, X) } IN
         IF ok = {} THEN NoHead ELSE CHOOSE a \in ok : \A o \in ok : Ver(o) <= Ver(a)

TipBack(c, H, X) ==
    LET tips == { a \in Chain(c) \ {G} : ~ByReceipt(a) /\ Cardinality(Succ(Prev(a), H, X)) > 1 } IN
    IF c = NoHead \/ tips = {} \/ Plant = "first_seen_wins" THEN c
    ELSE Prev(CHOOSE a \in tips : \A o \in tips : Ver(a) <= Ver(o))

Settle(c, H, X) ==
    LET back == Retreat(c, H, X)
        tip == TipBack(back, H, X)
        one == Adv1(tip, H, X)
    IN  Adv1(one, H, X)

(* The same head as a fold over the rows alone, from the head the edge names. *)
FoldHead(H, X) == Settle(edgeHead, H, X)

-----------------------------------------------------------------------------
(* The verdict. E carries what V must not read. *)

BaseE == [halt |-> FALSE, room |-> TRUE, clk |-> clock]

(* The edge counts iff its own instant precedes its signer's revoked_after. *)
EdgeLive(t) ==
    \/ edge = "present" /\ edgeAt < orev
    \/ Plant = "end_by_instant" /\ edge \in Ended /\ t < endAt /\ edgeAt < orev

(* A holder is live while the key the bundle in force seats for it has no
   revocation in effect. *)
LiveHolders(c, t) == { h \in Holders : RecBy(h, c, held) \/ t < krev[h] }

Verdict(c, t, E) ==
    IF ~EdgeLive(t) \/ c = NoHead THEN NotRooted
    ELSE IF Plant = "halt_folds" /\ E.halt THEN NotRooted
    ELSE IF Plant = "aging_detaches" /\ ByReceipt(c) /\ rAt[c] + AttachWindow < E.clk THEN NotRooted
    ELSE IF Maj(LiveHolders(c, t)) /\ (Plant = "founder_margin" => E.room) THEN Rooted
    ELSE Stalled

VAt(t) == Verdict(cur, t, BaseE)

-----------------------------------------------------------------------------
Init ==
    /\ clock = 0
    /\ held = {G}
    /\ sig = [b \in NonG |-> {}]
    /\ rec = [b \in NonG |-> {}]
    /\ krev = [h \in Holders |-> Never]
    /\ nrev = 0
    /\ rN = [b \in HeadIds |-> 0]
    /\ rAt = [b \in HeadIds |-> Never]
    /\ uncount = FALSE
    /\ orev = Never
    /\ edge = "none" /\ edgeHead = NoHead /\ edgeAt = 0 /\ endAt = 0
    /\ cur = NoHead

(* After any row lands, the node's head is settled again on the rows it now holds. *)
Fix == \E c \in {cur} : cur' = IF edge = "present" THEN Settle(c, held, {})' ELSE c
EdgeSame == UNCHANGED << edge, edgeHead, edgeAt, endAt >>

(* The plant that lets a freeze hold back more than head adoption. *)
FreezeGuard == ~(Plant = "freeze_blocks_ends" /\ Frozen(held, {}))

Tick ==
    /\ clock < MaxT /\ clock' = clock + 1
    /\ UNCHANGED << held, sig, rec, krev, nrev, rN, rAt, uncount, orev >>
    /\ EdgeSame /\ Fix

(* A later bundle: an amend, carrying the statements of a strict majority. *)
Amend(b, S) ==
    /\ b \in NonG \ held /\ Prev(b) \in held /\ clock >= HAt(b)
    /\ Maj(S)
    /\ held' = held \cup {b}
    /\ sig' = [sig EXCEPT ![b] = S]
    /\ UNCHANGED << clock, rec, krev, nrev, rN, rAt, uncount, orev >>
    /\ EdgeSame /\ Fix

(* A later bundle: one holder's recovery, under its recovery key. It changes
   that holder's seat only. Bounded to a holder whose key has a revocation. *)
Recover(b, h) ==
    /\ b \in (NonG \ {B2}) \ held /\ Prev(b) \in held /\ clock >= HAt(b)
    /\ krev[h] < Never /\ ~RecBy(h, Prev(b), held)
    /\ held' = held \cup {b}
    /\ rec' = [rec EXCEPT ![b] = {h}]
    /\ UNCHANGED << clock, sig, krev, nrev, rN, rAt, uncount, orev >>
    /\ EdgeSame /\ Fix

(* A key revocation of a holder's genesis key, or a lowering of its bound. *)
RevokeKey(h, r) ==
    /\ FreezeGuard
    /\ r \in Instants /\ r < krev[h] /\ nrev < MaxRevs
    /\ krev' = [krev EXCEPT ![h] = r]
    /\ nrev' = nrev + 1
    /\ UNCHANGED << clock, held, sig, rec, rN, rAt, uncount, orev >>
    /\ EdgeSame /\ Fix

(* A key revocation of the key that signs the acceptance edge. *)
RevokeOwner(r) ==
    /\ FreezeGuard
    /\ r \in Instants /\ r < orev /\ nrev < MaxRevs
    /\ orev' = r
    /\ nrev' = nrev + 1
    /\ UNCHANGED << clock, held, sig, rec, krev, rN, rAt, uncount >>
    /\ EdgeSame /\ Fix

(* One more service issues a Receipt for a bundle, or, at the quorum, a
   service issues again. A service that is not faulty registers one bundle
   for each version, so the counts at one version sum to no more than the
   services and the faulty ones. Where no services are named the model lets
   Receipts be issued for the genesis only: they count on no head. *)
Issue(b) ==
    /\ b \in held /\ (Named \/ b = G)
    /\ ~(rN[b] = Quorum /\ rAt[b] = clock)
    /\ LET n == IF rN[b] < Quorum THEN rN[b] + 1 ELSE Quorum IN
       /\ \A o \in held \ {b} : Ver(o) = Ver(b) => n + rN[o] <= NServices + Faulty
       /\ rN' = [rN EXCEPT ![b] = n]
    /\ rAt' = [rAt EXCEPT ![b] = clock]
    /\ UNCHANGED << clock, held, sig, rec, krev, nrev, uncount, orev >>
    /\ EdgeSame /\ Fix

(* A service's key is revoked below a Receipt it issued for b, and the Receipt
   falls out of the count. The bundle's newest instant is then unknown until
   a service issues again (the model keeps one instant for each bundle).
   Bounded to one such row. *)
Uncount(b) ==
    /\ Uncountable /\ ~uncount /\ b \in held /\ rN[b] > 0
    /\ rN' = [rN EXCEPT ![b] = @ - 1]
    /\ rAt' = [rAt EXCEPT ![b] = Never]
    /\ uncount' = TRUE
    /\ UNCHANGED << clock, held, sig, rec, krev, nrev, orev >>
    /\ EdgeSame /\ Fix

(* T4a: a new acceptance edge, naming head b and carrying its own instant e. *)
Attach(b, e) ==
    /\ edge # "present"
    /\ b \in held /\ Verifies(b, held, {})
    /\ e \in Instants /\ e <= clock + Skew /\ clock <= e + Skew /\ e < orev
    /\ IF ByReceipt(b)
       THEN /\ ~Frozen(held, {})
            /\ Plant = "attach_under_quorum" \/ Receipted(b)
            /\ FreshGate(b, e)
            /\ ~\E s \in held : Prev(s) = b /\ Verifies(s, held, {}) /\ Receipted(s)
       ELSE b = Anchor
    /\ edge' = "present" /\ edgeHead' = b /\ edgeAt' = e /\ endAt' = 0
    /\ cur' = Settle(b, held, {})
    /\ UNCHANGED rows

(* T3: the edge deleted, one row. *)
EndEdge(k) ==
    /\ FreezeGuard
    /\ edge = "present" /\ k \in Ended
    /\ edge' = k
    /\ IF Plant = "end_by_instant"
       THEN endAt' = clock /\ UNCHANGED << edgeHead, edgeAt, cur >>
       ELSE endAt' = 0 /\ edgeHead' = NoHead /\ edgeAt' = 0 /\ cur' = NoHead
    /\ UNCHANGED rows

Next ==
    \/ Tick
    \/ \E b \in NonG, S \in SUBSET Holders : Amend(b, S)
    \/ \E b \in NonG, h \in Holders : Recover(b, h)
    \/ \E h \in Holders, r \in Instants : RevokeKey(h, r)
    \/ \E r \in Instants : RevokeOwner(r)
    \/ \E b \in HeadIds : Issue(b)
    \/ \E b \in HeadIds : Uncount(b)
    \/ \E b \in HeadIds, e \in Instants : Attach(b, e)
    \/ \E k \in Ended : EndEdge(k)

Spec == Init /\ [][Next]_vars
Symm == Permutations(Holders)

-----------------------------------------------------------------------------
TypeOK ==
    /\ clock \in Instants /\ held \subseteq HeadIds /\ G \in held
    /\ krev \in [Holders -> Bounds] /\ orev \in Bounds
    /\ rN \in [HeadIds -> 0..Quorum] /\ rAt \in [HeadIds -> Bounds]
    /\ edge \in {"none", "present"} \cup Ended
    /\ cur \in HeadIds \cup {NoHead}
    /\ \A t \in Instants : VAt(t) \in {Rooted, Stalled, NotRooted}

(* (i) "A seat whose identity_type at seating includes node never moves a
   state by its own signature." Whatever bundles such a seat has signed, the
   bundle in force and the freeze are the same. *)
Inv_i ==
    \A X \in SUBSET held :
        /\ Settle(cur, held, X) = Settle(cur, held, {})
        /\ Frozen(held, X) = Frozen(held, {})

(* (ii) "V(rows, t) is constant on every interval of t that contains no
   effective_at and no revoked_after of any row -- a lapsed timer (drill
   staleness, an expired attach_window_secs, a missed receipt_cadence_secs)
   never moves Rooted or Stalled to NotRooted." Inv_ii is the first half and
   that V is the same whatever the evaluating clock reads; Prop_ii is the
   second half, on the step where only the clock moves. *)
Inv_ii ==
    /\ \A t \in 0..(MaxT - 1) :
          ((\A h \in Holders : krev[h] # t + 1) /\ orev # t + 1) => VAt(t) = VAt(t + 1)
    /\ \A t \in Instants, c \in Instants : Verdict(cur, t, [BaseE EXCEPT !.clk = c]) = VAt(t)
Prop_ii == [][ clock' # clock => \A t \in Instants : VAt(t)' = VAt(t) ]_vars

(* (iii), second sentence: "A key revocation reaches behind only through its
   revoked_after bound, per (viii)." A bundle whose every statement was made
   before its signer's bound keeps its count. *)
Inv_iii ==
    \A b \in held \ {G} :
        (rec[b] = {} /\ Maj({h \in sig[b] : RecBy(h, Prev(b), held) \/ HAt(b) < krev[h]}))
            => Counted(b, held, {})

(* (iv) "The edge-written transition is enabled only on a head whose counted
   Receipts are fresh and at least receipt_quorum. A stale or under-quorum
   head never yields Rooted on attach." Freshness is read against the edge's
   own signed instant. Where no services are named, the edge names the
   anchored head. *)
Prop_iv ==
    [][ (edge # "present" /\ edge' = "present") =>
            LET b == edgeHead' e == edgeAt' IN
            IF Named THEN RefReceipted(b) /\ FreshAt(b, e) /\ ~RefEquivocation
            ELSE b = Anchor ]_vars

(* (v) "A constitutional halt moves no state here: V at t is the same with
   and without a latched halt, whatever roster rows land between." *)
Inv_v == \A t \in Instants, hl \in BOOLEAN : Verdict(cur, t, [BaseE EXCEPT !.halt = hl]) = VAt(t)

(* (vi) "Deleting the acceptance edge is sufficient for NotRooted from any
   state, and from NotRooted for want of an edge nothing but a new edge
   naming a head re-enters Rooted." *)
Inv_vi ==
    /\ edge # "present" => \A t \in Instants : VAt(t) = NotRooted
    /\ \A t \in Instants : VAt(t) # NotRooted => (edge = "present" /\ edgeHead \in held)
    /\ edge = "present" => ENABLED EndEdge("withdrawn")
Prop_vi ==
    [][ \A t \in Instants :
            (edge # "present" /\ VAt(t)' # NotRooted) => (edge' = "present" /\ edgeHead' \in held') ]_vars

(* (vii) "V(rows, t) is independent of the order in which the rows arrived --
   the fold commutes." The head the node reached row by row is the head a
   fold over the same rows gives. See the README, Readings 1 and 2, for the
   two corners left out. *)
Inv_vii == (edge = "present" /\ ~Frozen(held, {}) /\ ~uncount) => cur = FoldHead(held, {})
(* The same without the two corners. This one fails; it is run as a reading. *)
Inv_vii_Unconditional == edge = "present" => cur = FoldHead(held, {})

(* (viii) "A revoked_after lowered below a receipted head's asserted_at is
   applied at read time, fail-closed ... V(rows + {v}, t) equals V over the
   rows with h and every head descending from h removed, for all t. The
   lineage's current head is the latest receipted head that still verifies,
   and the signer leaves the live holders from the bound onward." *)
Verified == { b \in held : Verifies(b, held, {}) }
Inv_viii ==
    /\ (edge = "present" /\ cur # NoHead) => Verifies(cur, held, {})
    /\ Settle(cur, held, {}) = Settle(cur, Verified, {})
    /\ Frozen(held, {}) = Frozen(Verified, {})
    /\ \A h \in Holders, t \in Instants :
          (cur # NoHead /\ ~RecBy(h, cur, held) /\ krev[h] <= t) => h \notin LiveHolders(cur, t)

(* CC 2.6.1.11: "A bound on a holder's key never unmakes the first bundle:
   its count stands once every holder it lists has made a valid statement
   over it." Whatever bounds are held, a node with a live edge stands on a
   bundle of the lineage and is Rooted or Stalled at every instant: a
   holder's key revoked with no bound moves Rooted to Stalled (T8) and never
   to NotRooted. The state it excludes is a live edge and no bundle in force. *)
Inv_FirstBundleStands ==
    (edge = "present" /\ edgeAt < orev) => (cur # NoHead /\ \A t \in Instants : VAt(t) # NotRooted)

(* T7: "It is no leg of any root's standing, and T8 never reads it." V is the
   same whatever the founder margin of an infrastructure room is. *)
Inv_T7 == \A t \in Instants, rm \in BOOLEAN : Verdict(cur, t, [BaseE EXCEPT !.room = rm]) = VAt(t)

(* "Stalled -- every leg of Rooted holds except the holders' margin." *)
Inv_Stalled ==
    \A t \in Instants :
        VAt(t) = Stalled <=> (edge = "present" /\ edgeAt < orev /\ cur # NoHead
                              /\ ~Maj({h \in Holders : RecBy(h, cur, held) \/ t < krev[h]}))

(* "a holder's recovery, a later bundle under its recovery key, that restores
   the majority (Stalled -> Rooted)": while a later bundle can still be made
   on the bundle in force, a recovery can be. *)
FreeSlot == \/ cur = G /\ A2 \notin held
            \/ Deep /\ cur = A2 /\ A3 \notin held
Inv_RecoverEnabled ==
    ((\E t \in Instants : VAt(t) = Stalled) /\ FreeSlot /\ clock >= Ver(cur))
        => ENABLED (\E b \in NonG, h \in Holders : Recover(b, h))

(* T4: "Each attach-time clause is never a leg of V for a node already
   attached." A step that changes only the clock and the Receipts never moves
   Rooted or Stalled to NotRooted. *)
Prop_T4 ==
    [][ (edge = "present" /\ UNCHANGED << edge, edgeHead, edgeAt, orev, krev, held, sig, rec >>)
            => \A t \in Instants : VAt(t) # NotRooted => VAt(t)' # NotRooted ]_vars
Inv_T4 == (edge = "present" /\ edgeAt < orev /\ cur # NoHead) => \A t \in Instants : VAt(t) # NotRooted

(* "The end of a standing enters V by the head its row names, never by an
   instant": once the edge is ended, V is NotRooted at every t, the instants
   before the end among them. *)
Inv_EndNoInstant == edge \in Ended => \A t \in Instants : VAt(t) = NotRooted

(* "A Receipt for a head is verified against the transparency_services of
   that head's predecessor ... A later head is never verified against its own
   charter, which a fork head chooses." Every head the node comes to stand
   on by Receipt holds a quorum from the predecessor's set. *)
Inv_PredecessorSet == \A b \in held : Receipted(b) => RefReceipted(b)
Prop_PredecessorSet ==
    [][ (Named /\ cur' # cur /\ cur' # NoHead /\ cur' \notin Chain(cur))
            => rN'[cur'] >= Quorum ]_vars

(* "a fork attempt never freezes the lineage" *)
Inv_ForkNeverFreezes == Frozen(held, {}) => RefEquivocation

(* "The freeze suspends head adoption only. withdraws, recants, tombstones,
   revoked_after bounds and the halt latch ... keep landing." *)
Inv_FreezeAdoptionOnly ==
    Frozen(held, {}) =>
        /\ edge = "present" => ENABLED EndEdge("withdrawn")
        /\ (nrev < MaxRevs /\ orev > 0) => ENABLED RevokeOwner(0)
        /\ (nrev < MaxRevs /\ \E h \in Holders : krev[h] > 0)
              => ENABLED (\E h \in Holders : RevokeKey(h, 0))
Prop_FreezeAdoptionOnly ==
    [][ (Frozen(held, {}) /\ Frozen(held, {})' /\ edge = "present" /\ edge' = "present")
            => (cur' = cur \/ cur' \in Chain(cur) \/ cur' = NoHead) ]_vars

(* "A charter that carries none of them names no services, and no Receipt counts." *)
Inv_NoServicesNoReceipt == ~Named => \A b \in held : ~Receipted(b)
=============================================================================
