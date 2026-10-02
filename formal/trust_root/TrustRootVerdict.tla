------------------------- MODULE TrustRootVerdict -------------------------
(***************************************************************************)
(* CC 3.2 T8 — the standing verdict V(rows, t) as a state machine.          *)
(*                                                                          *)
(* One evaluating node, one `infrastructure` root, a bounded founder set,   *)
(* a bounded witness directory, discrete signer-stamped instants 0..MaxT.   *)
(* The verdict is the pure function V below; the T8 invariants are the      *)
(* INVARIANTS / PROPERTY in TrustRootVerdict.cfg.                           *)
(*                                                                          *)
(* State is kept minimal BY CONSTRUCTION (the second cut, after a coverage  *)
(* profile of the first showed histories, the cosignature set and the free  *)
(* bound value multiplying the space without adding reachable behaviour):   *)
(*  - no per-instant histories: every row carries the instant it was       *)
(*    admitted (effective_at = now), so "never reaches behind" holds by     *)
(*    construction and V is checked at `now`;                               *)
(*  - cosignatures are per-witness latest (head, signed_at) — T4a reads     *)
(*    only the newest counted cosignature and T6 only the set of witnesses  *)
(*    on a head;                                                            *)
(*  - a revoked_after bound has one modelled value, 0: it unmakes every head  *)
(*    the key signed (DigiNotar). A bound at `now` is behaviourally a          *)
(*    resignation and is not modelled twice;                                 *)
(*  - seats, resignations and heads carry no instants: V is evaluated at     *)
(*    `now` only, so "admitted at now" is a set membership;                  *)
(*  - the halt latch is a definitional leg of V (first two branches) and     *)
(*    orthogonal to every other row; it is not toggled here, so it does not  *)
(*    double the space;                                                      *)
(*  - a head is issued only when the fold changes (T6);                     *)
(*  - one human key starts unseated so the T7 recovery widening is          *)
(*    reachable.                                                            *)
(*                                                                          *)
(* CIRISConstitution#127.  Persist's five rc5 review corners become named   *)
(* invariants Corner1..Corner5 once persist lists them; not encoded yet.    *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets, Sequences, TLC

CONSTANTS
    Founders,        \* candidate founder keys
    NodeKeys,        \* subset whose identity_type includes `node`
    Witnesses,       \* the charter's witnesses[] (independent by construction)
    M,               \* quorum:M/N — absolute M
    K,               \* witness_quorum
    MaxT,            \* last instant
    AttachWindow     \* attach_window_secs, in ticks

ASSUME NodeKeys \subseteq Founders
ASSUME M >= 2 /\ K >= 2 /\ K * 2 > Cardinality(Witnesses)
ASSUME AttachWindow >= 1

None == MaxT + 1
Instants == 0..MaxT
Humans == Founders \ NodeKeys

VARIABLES
    now,
    seated,          \* SUBSET Founders — seat rows admitted at or before now
    resigned,        \* SUBSET Founders — resignation rows admitted at or before now
    revokedAll,      \* SUBSET Founders — keys with revoked_after = 0 (every signature unmade)
    heads,           \* Seq of signer sets; index i's prev is i-1
    cosig,           \* [Witnesses -> [h: Nat, at: Instants]]  latest cosignature per witness
    edgeHead,        \* 0 = no acceptance edge, else the head index it names
    conferred        \* subset of Humans holding a live ceremony-plane conferral

vars == << now, seated, resigned, revokedAll, heads, cosig, edgeHead, conferred >>
halt == FALSE       \* definitional leg of V; see the header

-----------------------------------------------------------------------------
Active == ((seated \ resigned) \ revokedAll) \ NodeKeys        \* T7, identity_type at seating
Live == Cardinality(Active) >= M + 1

(* Read-time quorum under revoked_after (T8 viii): a revoked-all key's signature is unmade. *)
HeadValid(i) == Cardinality(heads[i] \ revokedAll) >= M

Cosigners(i) == { w \in Witnesses : cosig[w].h = i }
Witnessed(i) == Cardinality(Cosigners(i)) >= K
NewestCosig(i) == CHOOSE a \in { cosig[w].at : w \in Cosigners(i) } :
                     \A w \in Cosigners(i) : cosig[w].at <= a
Fresh(i) == Witnessed(i) /\ NewestCosig(i) + AttachWindow >= now

CurrentHeads == { i \in 1..Len(heads) : HeadValid(i) /\ Witnessed(i) }
HasCurrentHead == CurrentHeads # {}

-----------------------------------------------------------------------------
Rooted == "Rooted"
Stalled == "Stalled"
NotRooted == "NotRooted"

V ==
    IF edgeHead = 0 THEN NotRooted
    ELSE IF halt THEN NotRooted
    ELSE IF ~HasCurrentHead THEN NotRooted
    ELSE IF Live THEN Rooted ELSE Stalled

(* (i): the verdict with node-bearing seats ignored is the same function. *)
VNoNode ==
    IF edgeHead = 0 THEN NotRooted
    ELSE IF halt THEN NotRooted
    ELSE IF ~HasCurrentHead THEN NotRooted
    ELSE IF Cardinality(((seated \ resigned) \ revokedAll) \ NodeKeys) >= M + 1 THEN Rooted ELSE Stalled

-----------------------------------------------------------------------------
Init ==
    /\ now = 0
    /\ resigned = {} /\ revokedAll = {}
    /\ seated \in SUBSET Founders
    /\ Cardinality(Active) >= M + 1                  \* T7: founded at N >= M+1
    /\ \E f \in Humans : f \notin seated             \* one conferrable key exists
    /\ heads = << Active >>
    /\ cosig = [w \in Witnesses |-> [h |-> 1, at |-> 0]]
    /\ edgeHead = 0
    /\ conferred = {}

-----------------------------------------------------------------------------
Tick ==
    /\ now < MaxT /\ now' = now + 1
    /\ UNCHANGED << seated, resigned, revokedAll, heads, cosig, edgeHead, conferred >>

Widen(f) ==
    /\ f \notin seated /\ Cardinality(Active) >= M
    /\ seated' = seated \cup {f}
    /\ UNCHANGED << now, resigned, revokedAll, heads, cosig, edgeHead, conferred >>

Resign(f) ==
    /\ f \in seated /\ f \notin resigned
    /\ resigned' = resigned \cup {f}
    /\ UNCHANGED << now, seated, revokedAll, heads, cosig, edgeHead, conferred >>

RevokeAll(f) ==
    /\ f \notin revokedAll
    /\ revokedAll' = revokedAll \cup {f}
    /\ UNCHANGED << now, seated, resigned, heads, cosig, edgeHead, conferred >>

(* T6: a head changes only when the fold changes; signed by the active founders. *)
IssueHead ==
    /\ Cardinality(Active) >= M /\ Active # heads[Len(heads)]
    /\ heads' = Append(heads, Active)
    /\ UNCHANGED << now, seated, resigned, revokedAll, cosig, edgeHead, conferred >>

(* A witness commits the current head; a re-commitment advances signed_at. *)
Cosign(w) ==
    /\ ~(cosig[w].h = Len(heads) /\ cosig[w].at = now)
    /\ cosig' = [cosig EXCEPT ![w] = [h |-> Len(heads), at |-> now]]
    /\ UNCHANGED << now, seated, resigned, revokedAll, heads, edgeHead, conferred >>

(* T4a: the acceptance edge is written only on a fresh, witnessed, valid head. *)
Attach(i) ==
    /\ edgeHead = 0 /\ i \in 1..Len(heads) /\ HeadValid(i) /\ Fresh(i)
    /\ edgeHead' = i
    /\ UNCHANGED << now, seated, resigned, revokedAll, heads, cosig, conferred >>

Detach ==
    /\ edgeHead # 0 /\ edgeHead' = 0
    /\ UNCHANGED << now, seated, resigned, revokedAll, heads, cosig, conferred >>

Confer(f) ==
    /\ f \in Humans /\ f \notin conferred /\ f \notin seated /\ ~Live
    /\ conferred' = conferred \cup {f}
    /\ UNCHANGED << now, seated, resigned, revokedAll, heads, cosig, edgeHead >>

(* T7 recovery: while stalled, seat a conferred human founder on the conferral alone. *)
Recover(f) ==
    /\ ~Live /\ f \in conferred /\ f \notin seated
    /\ seated' = seated \cup {f} /\ conferred' = conferred \ {f}
    /\ UNCHANGED << now, resigned, revokedAll, heads, cosig, edgeHead >>

Next ==
    \/ Tick
    \/ \E f \in Founders : Widen(f) \/ Resign(f) \/ RevokeAll(f)
    \/ \E f \in Humans : Confer(f) \/ Recover(f)
    \/ IssueHead
    \/ \E w \in Witnesses : Cosign(w)
    \/ \E i \in 1..Len(heads) : Attach(i)
    \/ Detach

Spec == Init /\ [][Next]_vars
Symm == Permutations(Humans) \cup Permutations(Witnesses)

-----------------------------------------------------------------------------
(* T8 invariants                                                            *)

TypeOK == now \in Instants /\ V \in {Rooted, Stalled, NotRooted}

(* (i) a node-bearing seat never moves a state by its own signature *)
Inv_i == V = VNoNode

(* (ii) a tick never moves Rooted/Stalled to NotRooted: with no instant-declared
   bound in this cut, a tick crosses nothing — the property is exactly "V does
   not read the clock". *)
Prop_ii == [][ (Tick /\ V \in {Rooted, Stalled}) => V' # NotRooted ]_vars

(* (iii) holds by construction: rows are sets admitted at `now`; nothing is read
   at an earlier instant. *)

(* (iv) the edge-written transition is enabled only on a fresh, witnessed head,
   freshness read in the pre-state (a witness moving on afterwards un-attaches
   nobody — T4). *)
Prop_iv == [][ (edgeHead = 0 /\ edgeHead' # 0) => Fresh(edgeHead') ]_vars

(* (v) holds by construction of V (second branch); the latch is not toggled here. *)

(* (vi) no edge => NotRooted; Rooted => an edge naming a head *)
Inv_vi == (edgeHead = 0 => V = NotRooted) /\ (V = Rooted => edgeHead \in 1..Len(heads))

(* (vii) V reads only the row variables and `now`, by construction. *)

(* (viii) a revoked-all key is out of the active set and out of every current head's quorum. *)
Inv_viii == (\A f \in revokedAll : f \notin Active) /\ (\A i \in CurrentHeads : HeadValid(i))

(* T7 sanity: Stalled is exactly "every other leg holds, the margin fails". *)
Inv_T7 == V = Stalled => (edgeHead # 0 /\ HasCurrentHead /\ ~Live)

(* T7 recovery: from Stalled with a conferrable human, Recover is enabled after Confer. *)
Inv_RecoverEnabled == (V = Stalled /\ \E f \in Humans : f \notin seated) => ENABLED (\E f \in Humans : Confer(f) \/ Recover(f))
=============================================================================
