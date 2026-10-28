---------------------------- MODULE MeshNet ----------------------------
(* The replication / holding / moderation / trust-root state of a small mesh, against the net
   invariants listed in INVARIANTS.md (derived from ciris.ai/safety, ciris.ai/constitutional-mesh
   and the Constitution). Two configurations check the same module:

     MeshNet_shipped_scope.cfg  ClaimScope = "federation", ClaimsBind = FALSE
                          -- holding claims for community / public content are emitted at federation
                             scope (an implementation's holds_bytes builder). Inv_Invisible fails.
     MeshNet_shipped_bind.cfg   ClaimScope = "content", ClaimsBind = TRUE
                          -- a live holding claim is folded as a content binding (an implementation's
                             fold). Inv_ClaimNotBinding fails.
     MeshNet_ruled.cfg          ClaimScope = "content", ClaimsBind = FALSE
                          -- CC 2.4.1.1 and 5.4.6: one holding claim at the content's own scope; a claim is
                             never a binding. Every property holds.

   Scope, stated: three persons, three nodes (one a server), one family, one community, one
   public room, the Commons, two blobs. Signatures are unforgeable; the roster fold and the
   accord's own roster rules are modelled elsewhere (formal/trust_root, formal/accord_roster). *)
EXTENDS Naturals, FiniteSets

CONSTANTS Persons, Nodes, Blobs,
          Owner,        \* [Nodes -> Persons]
          Class,        \* [Nodes -> {"personal", "server"}]
          InitMembers,  \* [Cohorts -> SUBSET Persons]
          InitMods,     \* [Cohorts -> SUBSET Persons]
          ClaimScope,   \* "federation" | "content"
          ClaimsBind    \* BOOLEAN
ASSUME Owner \in [Nodes -> Persons] /\ Class \in [Nodes -> {"personal", "server"}]

Cohorts   == {"fam", "room", "pub", "commons"}
Bounded   == {"fam", "room", "pub"}        \* has a roster
Moderated == {"room", "pub"}               \* multi-party spaces (CC 4.5.4)

VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted

vars == <<scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted>>

\* Derived, not stored: the tripwire has run on exactly the blobs published into the Commons or a
\* public room (CC 1.13); scope is immutable, so this is a function of scope.
scanned == {b \in Blobs : scope[b] \in {"commons", "pub"}}

None == "none"

(* ---- derived ------------------------------------------------------------------------------ *)

\* CC 6.1.5.3: a node is in a cohort's audience through its owner's membership, under the
\* owner's allow list; a server-class node carries nothing personal unless listed (CC 3.3.7).
InAudience(n, c) ==
  \/ c = "commons"
  \/ /\ Owner[n] \in members[c]
     /\ c \in allow[n]
     /\ ~(restricted /\ c = "room")              \* a root's restriction (RootReach has the rest)
     /\ (c \in Moderated => federating[c])

\* Who can observe a holding claim: everyone, or the content's cohort.
Observers(c) == IF c = "commons" THEN Persons ELSE members[c]

\* The bytes plane's liveness fold. With ClaimsBind, a live holding claim is read as a binding
\* that keeps withdrawn content live (a defect an implementation exhibited).
HasClaim(b) == b \in claimed
Live(b) == b \notin withdrawn \/ (ClaimsBind /\ HasClaim(b))

(* ---- init ---------------------------------------------------------------------------------- *)

Init ==
  /\ scope = [b \in Blobs |-> None]
  /\ author = [b \in Blobs |-> None]
  /\ held = [n \in Nodes |-> {}]
  /\ claimed = {}
  /\ allow = [n \in Nodes |-> IF Class[n] = "personal" THEN Cohorts ELSE {"commons"}]
  /\ withdrawn = {}
  /\ members = InitMembers
  /\ mods = InitMods
  /\ federating = [c \in Cohorts |-> TRUE]
  /\ restricted = FALSE

(* ---- actions ------------------------------------------------------------------------------- *)

\* A node's owner authors a blob at a scope the owner belongs to. Scope is immutable: a promotion is a
\* NEW Contribution of the same bytes at the wider scope (CC 5.2), so it is this action again. Posting
\* into the Commons or a public room is a publication: the tripwire runs at that seam (CC 1.13).
Author(n, b, c) ==
  /\ scope[b] = None
  /\ Owner[n] \in members[c]
  /\ (c \in Moderated => federating[c])
  /\ scope' = [scope EXCEPT ![b] = c]
  /\ author' = [author EXCEPT ![b] = n]
  /\ held' = [held EXCEPT ![n] = @ \cup {b}]
  /\ UNCHANGED <<claimed, allow, withdrawn, members, mods, federating, restricted>>

\* Replication: a blob reaches a node only through the audience rule (one rule, every tier).
Replicate(n, b) ==
  /\ scope[b] # None
  /\ b \notin held[n]
  /\ Live(b)
  /\ InAudience(n, scope[b])
  /\ held' = [held EXCEPT ![n] = @ \cup {b}]
  /\ UNCHANGED <<scope, author, claimed, allow, withdrawn, members, mods, federating, restricted>>

\* A holding claim ("some node holds these bytes") with the audience its emitter gives it. The
\* audience is a function of the content's scope, not of the emitting node, so one claim per blob
\* carries every property a claim per node would.
ClaimAud(b) == IF scope[b] = "commons" THEN Persons
               ELSE IF ClaimScope = "federation" /\ scope[b] \in {"room", "pub"} THEN Persons
               ELSE Observers(scope[b])
Claim(b) ==
  /\ b \notin claimed
  /\ \E n \in Nodes : b \in held[n]
  /\ claimed' = claimed \cup {b}
  /\ UNCHANGED <<scope, author, held, allow, withdrawn, members, mods, federating, restricted>>

\* The author withdraws the content (CC 2.4.1.1 rule 1).
Withdraw(b) ==
  /\ scope[b] # None /\ b \notin withdrawn
  /\ withdrawn' = withdrawn \cup {b}
  /\ UNCHANGED <<scope, author, held, claimed, allow, members, mods, federating, restricted>>

\* The named moderator lapses. In the SAME step the community auto-promotes a member or
\* fails secure (CC 4.5.4): there is no moderator-less window.
ModLapse(c, p) ==
  /\ c \in Moderated /\ p \in mods[c]
  /\ LET rest == mods[c] \ {p}
         candidates == members[c] \ {p}
     IN IF rest # {} THEN mods' = [mods EXCEPT ![c] = rest] /\ UNCHANGED federating
        ELSE IF candidates # {}
             THEN /\ mods' = [mods EXCEPT ![c] = {CHOOSE q \in candidates : TRUE}]
                  /\ UNCHANGED federating
             ELSE /\ mods' = [mods EXCEPT ![c] = {}]
                  /\ federating' = [federating EXCEPT ![c] = FALSE]
  /\ UNCHANGED <<scope, author, held, claimed, allow, withdrawn, members, restricted>>

\* Open admission to a public room (CC 4.5.4): the joiner's own acceptance seats them.
JoinPub(p) ==
  /\ p \notin members["pub"] /\ federating["pub"]
  /\ members' = [members EXCEPT !["pub"] = @ \cup {p}]
  /\ UNCHANGED <<scope, author, held, claimed, allow, withdrawn, mods, federating, restricted>>

\* A trust root's mesh_config restricts what its subscribers carry; it only ever narrows
\* (CC 4.2.1 relieve-never-expand). The root's reach itself is RootReach.tla; here it is one bit.
Restrict ==
  /\ ~restricted
  /\ restricted' = TRUE
  /\ UNCHANGED <<scope, author, held, claimed, allow, withdrawn, members, mods, federating>>

\* The owner edits the node's allow list (a supersedes of the consent:replication grant).
SetAllow(n, c) ==
  /\ Class[n] = "server" /\ c \in {"fam", "room"} /\ c \notin allow[n]   \* only a server has a choice
  /\ allow' = [allow EXCEPT ![n] = @ \cup {c}]
  /\ UNCHANGED <<scope, author, held, claimed, withdrawn, members, mods, federating, restricted>>

Next ==
  \/ \E n \in Nodes, b \in Blobs, c \in Cohorts : Author(n, b, c)
  \/ \E n \in Nodes, b \in Blobs : Replicate(n, b)
  \/ \E b \in Blobs : Claim(b) \/ Withdraw(b)
  \/ \E c \in Cohorts, p \in Persons : ModLapse(c, p)
  \/ \E p \in Persons : JoinPub(p)
  \/ Restrict
  \/ \E n \in Nodes, c \in Cohorts : SetAllow(n, c)

Spec == Init /\ [][Next]_vars

(* ---- invariants (INVARIANTS.md numbering) ------------------------------------------------- *)

\* I1 Nothing held unknown: every held blob is Commons plaintext, or for a cohort the node's
\*    owner is a member of. There is no non-member holder of bounded-cohort bytes.
Inv_KnownHold == \A n \in Nodes : \A b \in held[n] :
  scope[b] = "commons" \/ Owner[n] \in members[scope[b]]

\* I2 Consent supreme: a node holds nothing its owner did not consent to, except what it authored.
Inv_Consent == \A n \in Nodes : \A b \in held[n] :
  author[b] = n \/ scope[b] \in allow[n]

\* I3 Structural invisibility: no holding claim for bounded-cohort content is observable outside
\*    the cohort. (Fails under the shipped federation-scope claim for room/pub content.)
Inv_Invisible == \A b \in claimed :
  scope[b] \in Bounded => ClaimAud(b) \subseteq members[scope[b]]

\* I4 Claims are not bindings: withdrawn content is not live. (Fails when ClaimsBind.)
Inv_ClaimNotBinding == \A b \in withdrawn : ~Live(b)

\* I5 No unmoderated multi-party space, ever.
Inv_Moderated == \A c \in Moderated : federating[c] => mods[c] # {}

\* I6 The tripwire runs exactly at the publication seam: every Commons/public blob was scanned
\*    there, and nothing inside a bounded private cohort is ever scanned.
Inv_ScanSeam == \A b \in Blobs :
  /\ (scope[b] \in {"commons", "pub"} => b \in scanned)
  /\ (scope[b] \in {"fam", "room"} /\ b \in scanned => FALSE)

\* I7–I9 (the halt's reach, a root only restricts, no group ban) are RootReach.tla; here the
\* one restriction bit is checked to only ever narrow the audience:
Prop_RestrictOnly == [][Restrict => \A n \in Nodes, c \in Cohorts : InAudience(n, c)' => InAudience(n, c)]_vars
=============================================================================================
