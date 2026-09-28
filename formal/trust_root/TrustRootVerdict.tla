------------------------- MODULE TrustRootVerdict -------------------------
(***************************************************************************)
(* CC 3.2 T8 — the standing verdict V(rows, t) as a state machine.          *)
(*                                                                          *)
(* One evaluating node, one root (an `infrastructure` community), a bounded *)
(* founder set, a bounded witness directory, and discrete signer-stamped    *)
(* instants 0..MaxT.  Every row the Constitution names is a variable here;  *)
(* the verdict is the pure function V(t) at the bottom of the "Verdict"     *)
(* section, and the eight T8 invariants are the INVARIANTS / PROPERTY in    *)
(* TrustRootVerdict.cfg.                                                    *)
(*                                                                          *)
(* Rows modelled: founder seats (with identity_type read at seating),       *)
(* revocations / withdraws (effective_at), revoked_after bounds (lower-only), *)
(* lineage heads (prev chain, signers, asserted_at), witness cosignatures    *)
(* (signed_at), the acceptance edge (attached_head_digest, written_at), the  *)
(* halt latch, and the T7 recovery widening.                                *)
(*                                                                          *)
(* CIRISConstitution#127.  Persist's five rc5 review corners are to be       *)
(* added as named invariants Corner1..Corner5 once persist lists them on the *)
(* ticket; nothing here pretends to encode them yet.                        *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets, Sequences, TLC

CONSTANTS
    Founders,        \* candidate founder keys (human-held unless in NodeKeys)
    NodeKeys,        \* subset of Founders whose identity_type includes `node`
    Witnesses,       \* the charter's witnesses[] (independent by construction here)
    M,               \* quorum:M/N — absolute M
    K,               \* witness_quorum
    MaxT,            \* last instant
    AttachWindow     \* attach_window_secs, in ticks

ASSUME NodeKeys \subseteq Founders
ASSUME M >= 2 /\ K >= 2
ASSUME K * 2 > Cardinality(Witnesses)   \* strict majority of the directory
ASSUME AttachWindow >= 1

None == MaxT + 1                        \* "no bound" sentinel for revoked_after

VARIABLES
    now,             \* current instant
    seats,           \* [Founders -> seat record or NoSeat]
    revocations,     \* set of [f |-> founder, at |-> instant]
    revokedAfter,    \* [Founders -> 0..None]  (lower-only)
    heads,           \* Seq of head records
    cosigs,          \* set of [h |-> head index, w |-> witness, at |-> instant]
    edges,           \* set of acceptance edges [head, at (written), off (deleted, or None)]
    halts,           \* set of [on |-> instant, off |-> instant or None]
    conferred,       \* set of founders holding a live ceremony-plane conferral
    hist             \* [0..MaxT -> verdict or "unset"] — V at each past instant

vars == << now, seats, revocations, revokedAfter, heads, cosigs, edges, halts, conferred, hist >>

EdgeAt(t) == \E e \in edges : e.at <= t /\ t < e.off
OpenEdges == { e \in edges : e.off = None }
Halted(t) == \E h \in halts : h.on <= t /\ t < h.off
halt == Halted(now)


NoSeat == [seated |-> FALSE, at |-> 0, node |-> FALSE]

Instants == 0..MaxT

-----------------------------------------------------------------------------
(* Row-level predicates, all pure in (rows, t)                              *)

(* T7 — the active founder set at t: seated by a row effective <= t, no
   revocation effective <= t, before the key's revoked_after, and the seat's
   identity_type AT SEATING excludes `node`. *)
Revoked(f, t) == \E r \in revocations : r.f = f /\ r.at <= t
Active(t) == { f \in Founders :
                 /\ seats[f].seated /\ seats[f].at <= t
                 /\ ~seats[f].node
                 /\ ~Revoked(f, t)
                 /\ t < revokedAfter[f] }

Live(t) == Cardinality(Active(t)) >= M + 1

(* A head's quorum is re-evaluated at read time under revoked_after (T8 viii):
   signer s counts iff the head's asserted_at precedes s's bound. *)
HeadValid(i) ==
    LET h == heads[i] IN
    Cardinality({ s \in h.signers : h.at < revokedAfter[s] }) >= M

(* Witnessed at t: at least K distinct witnesses cosigned by t. Independence
   is by construction — Witnesses and Founders are disjoint constants. *)
Cosigners(i, t) == { c.w : c \in { c \in cosigs : c.h = i /\ c.at <= t } }
Witnessed(i, t) == Cardinality(Cosigners(i, t)) >= K

(* Chain: every head's prev is the previous index (issued in order). *)
Descends(i) == i = 1 \/ heads[i].prev = i - 1

(* Current head at t: the latest valid, witnessed head whose asserted_at <= t. *)
CurrentHeadCandidates(t) ==
    { i \in 1..Len(heads) : heads[i].at <= t /\ HeadValid(i) /\ Witnessed(i, t) /\ Descends(i) }
HasCurrentHead(t) == CurrentHeadCandidates(t) # {}

(* T4a at the attach door: newest counted cosignature no older than the window. *)
NewestCosigAt(i, t) ==
    LET ats == { c.at : c \in { c \in cosigs : c.h = i /\ c.at <= t } }
    IN IF ats = {} THEN 0 ELSE CHOOSE a \in ats : \A b \in ats : a >= b
Fresh(i, t) == Witnessed(i, t) /\ NewestCosigAt(i, t) + AttachWindow >= t

-----------------------------------------------------------------------------
(* The verdict                                                              *)

Rooted == "Rooted"
Stalled == "Stalled"
NotRooted == "NotRooted"

(* Charter legs (recovery commitment, scope, custody) are constants of this
   model — always satisfied; a model dropping them is a separate refinement. *)
V(t) ==
    IF ~EdgeAt(t) THEN NotRooted
    ELSE IF Halted(t) THEN NotRooted
    ELSE IF ~HasCurrentHead(t) THEN NotRooted
    ELSE IF Live(t) THEN Rooted ELSE Stalled

Verdict == V(now)

(* (i) — the verdict computed as if every node-bearing seat were absent *)
ActiveNoNode(t) == { f \in Active(t) : f \notin NodeKeys }
LiveNoNode(t) == Cardinality(ActiveNoNode(t)) >= M + 1
VNoNode(t) ==
    IF ~EdgeAt(t) THEN NotRooted
    ELSE IF Halted(t) THEN NotRooted
    ELSE IF ~HasCurrentHead(t) THEN NotRooted
    ELSE IF LiveNoNode(t) THEN Rooted ELSE Stalled

-----------------------------------------------------------------------------
(* Initial state: the genesis head, signed by the initial founders, witnessed
   at instant 0; no edge; nothing revoked. *)

Init ==
    /\ now = 0
    /\ revocations = {}
    /\ revokedAfter = [f \in Founders |-> None]
    /\ halts = {}
    /\ seats \in [Founders -> {NoSeat} \cup { [seated |-> TRUE, at |-> 0, node |-> b] : b \in BOOLEAN }]
    /\ \A f \in Founders : seats[f].seated => seats[f].node = (f \in NodeKeys)
    /\ Cardinality(Active(0)) >= M + 1            \* T7: founded at N >= M+1
    /\ heads = << [prev |-> 0, at |-> 0, signers |-> Active(0)] >>
    /\ cosigs = { [h |-> 1, w |-> w, at |-> 0] : w \in Witnesses }
    /\ edges = {}
    /\ conferred = {}
    /\ hist = [t \in Instants |-> "unset"]

-----------------------------------------------------------------------------
(* Actions — each is one row, or the crossing of an instant                *)

RecordHist == hist' = [hist EXCEPT ![now] = V(now)]

Tick ==
    /\ now < MaxT
    /\ hist' = [hist EXCEPT ![now] = V(now)]
    /\ now' = now + 1
    /\ UNCHANGED << seats, revocations, revokedAfter, heads, cosigs, edges, halts, conferred >>

(* A founder-quorum widening: seat f (human or node-bearing — the fold, not the
   door, is what T7 tests here). Needs M active signers. *)
Widen(f) ==
    /\ ~seats[f].seated
    /\ Cardinality(Active(now)) >= M
    /\ seats' = [seats EXCEPT ![f] = [seated |-> TRUE, at |-> now, node |-> (f \in NodeKeys)]]
    /\ UNCHANGED << now, revocations, revokedAfter, heads, cosigs, edges, halts, conferred, hist >>

(* Resignation / removal: one row, effective now. *)
Resign(f) ==
    /\ seats[f].seated
    /\ ~Revoked(f, now)
    /\ revocations' = revocations \cup { [f |-> f, at |-> now] }
    /\ UNCHANGED << now, seats, revokedAfter, heads, cosigs, edges, halts, conferred, hist >>

(* Key-plane revocation with a history bound: lower-only (CC 2.6). *)
LowerBound(f, b) ==
    /\ b \in 0..now                                \* a bound in the future has no effect until crossed
    /\ b < revokedAfter[f]
    /\ revokedAfter' = [revokedAfter EXCEPT ![f] = b]
    /\ hist' = [t \in Instants |-> "unset"]        \* (viii): the one input that rewrites the past
    /\ UNCHANGED << now, seats, revocations, heads, cosigs, edges, halts, conferred >>

(* T6 — a new head, signed by the active founders (needs M), chained to the last. *)
IssueHead ==
    /\ Cardinality(Active(now)) >= M
    /\ Active(now) # heads[Len(heads)].signers      \* T6: a head changes only when the fold changes
    /\ heads' = Append(heads, [prev |-> Len(heads), at |-> now, signers |-> Active(now)])
    /\ UNCHANGED << now, seats, revocations, revokedAfter, cosigs, edges, halts, conferred, hist >>

(* A witness cosigns a head (re-commitment when the head is already current). *)
Cosign(i, w) ==
    /\ i = Len(heads)                              \* T6: witnesses commit the current head
    /\ heads[i].at <= now
    /\ ~\E c \in cosigs : c.h = i /\ c.w = w /\ c.at = now
    /\ cosigs' = cosigs \cup { [h |-> i, w |-> w, at |-> now] }
    /\ UNCHANGED << now, seats, revocations, revokedAfter, heads, edges, halts, conferred, hist >>

(* T4a — the acceptance edge is written only on a fresh, witnessed head. *)
Attach(i) ==
    /\ ~EdgeAt(now)
    /\ i \in 1..Len(heads)
    /\ HeadValid(i) /\ Descends(i)
    /\ Fresh(i, now)
    /\ edges' = edges \cup { [head |-> i, at |-> now, off |-> None] }
    /\ UNCHANGED << now, seats, revocations, revokedAfter, heads, cosigs, halts, conferred, hist >>

(* T3 — un-trust is one deletion. *)
Detach ==
    /\ EdgeAt(now)
    /\ edges' = { IF e.off = None THEN [e EXCEPT !.off = now] ELSE e : e \in edges }
    /\ UNCHANGED << now, seats, revocations, revokedAfter, heads, cosigs, halts, conferred, hist >>

Halt ==
    /\ ~Halted(now)
    /\ halts' = halts \cup { [on |-> now, off |-> None] }
    /\ UNCHANGED << now, seats, revocations, revokedAfter, heads, cosigs, edges, conferred, hist >>

LifecycleActive ==
    /\ Halted(now)
    /\ halts' = { IF h.off = None THEN [h EXCEPT !.off = now] ELSE h : h \in halts }
    /\ UNCHANGED << now, seats, revocations, revokedAfter, heads, cosigs, edges, conferred, hist >>

(* The conferring body confers root identity on a human key (ceremony plane). *)
Confer(f) ==
    /\ f \notin NodeKeys
    /\ f \notin conferred
    /\ ~Live(now)                                  \* a conferral matters here only for T7 recovery
    /\ conferred' = conferred \cup {f}
    /\ UNCHANGED << now, seats, revocations, revokedAfter, heads, cosigs, edges, halts, hist >>

(* T7 recovery — while stalled, one row without the founders' count: seat a
   conferred human founder, verified on the conferral. *)
Recover(f) ==
    /\ ~Live(now)
    /\ f \in conferred
    /\ f \notin NodeKeys
    /\ ~seats[f].seated
    /\ seats' = [seats EXCEPT ![f] = [seated |-> TRUE, at |-> now, node |-> FALSE]]
    /\ UNCHANGED << now, revocations, revokedAfter, heads, cosigs, edges, halts, conferred, hist >>

Next ==
    \/ Tick
    \/ \E f \in Founders : Widen(f) \/ Resign(f) \/ Confer(f) \/ Recover(f)
    \/ \E f \in Founders, b \in Instants : LowerBound(f, b)
    \/ IssueHead
    \/ \E i \in 1..Len(heads), w \in Witnesses : Cosign(i, w)
    \/ \E i \in 1..Len(heads) : Attach(i)
    \/ Detach \/ Halt \/ LifecycleActive

Spec == Init /\ [][Next]_vars

Symm == Permutations(Founders \ NodeKeys) \cup Permutations(Witnesses)

-----------------------------------------------------------------------------
(* T8 invariants                                                            *)

TypeOK ==
    /\ now \in Instants
    /\ Verdict \in {Rooted, Stalled, NotRooted}

(* (i) A node-bearing seat never moves a state by its own signature: the
   verdict is unchanged when every node-bearing seat is ignored. *)
Inv_i == \A t \in 0..now : V(t) = VNoNode(t)

(* (ii) A lapsed timer never moves Rooted/Stalled to NotRooted. Encoded on the
   Tick action: when only `now` advances and no row-declared instant is
   crossed, a rooted-or-stalled verdict never becomes NotRooted. Row-declared
   instants are revoked_after bounds; effective_at is always <= now. *)
NoBoundCrossed == \A f \in Founders : ~(revokedAfter[f] = now + 1)
Prop_ii == [][ (Tick /\ NoBoundCrossed /\ Verdict \in {Rooted, Stalled}) => Verdict' # NotRooted ]_vars

(* (iii) + (viii) A revocation row never reaches behind the head's instant:
   a past verdict changes only through a lowered revoked_after (read-time,
   fail-closed, by design). *)
PastUnchangedExceptByBound ==
    \A t \in 0..(now - 1) : hist[t] # "unset" => hist[t] = V(t)
Inv_iii_viii == PastUnchangedExceptByBound

(* (iv) A stale or under-quorum head never yields Rooted on attach. *)
Inv_iv == \A e \in edges : e.at = now /\ e.off = None => Fresh(e.head, now)

(* (v) A latched halt is NotRooted at every later instant until lifecycle:active. *)
Inv_v == \A t \in 0..now : Halted(t) => V(t) = NotRooted

(* (vi) Edge deletion suffices from any state; Rooted requires an edge naming a head. *)
Inv_vi == \A t \in 0..now : (~EdgeAt(t) => V(t) = NotRooted) /\ (V(t) = Rooted => EdgeAt(t))

(* (vii) V is a pure function of (rows, t): stated by construction — V reads
   only variables that are rows and the parameter t; `now` enters only as t.
   Two nodes holding the same rows compute the same V. *)
Inv_vii == TRUE

(* (viii) A lowered bound removes the signer from the active set from the
   bound onward, and a head whose quorum fails under it is not a head. *)
Inv_viii ==
    \A f \in Founders : \A t \in 0..now : t >= revokedAfter[f] => f \notin Active(t)

(* T7 sanity: Stalled is exactly "every other leg holds, margin fails". *)
Inv_T7 == Verdict = Stalled => (EdgeAt(now) /\ ~Halted(now) /\ HasCurrentHead(now) /\ ~Live(now))

(* Recovery reachability (liveness of the design, checked as a possibility,
   not required of every trace): a stalled root can return to Rooted. *)
StalledCanRecover == Verdict = Stalled ~> (Verdict # Stalled)
=============================================================================
