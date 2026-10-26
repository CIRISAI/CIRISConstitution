---------------------------- MODULE CewpNode ----------------------------
(* The spine: one mesh node's planes composed, over the variables of formal/STATE_TABLE.tsv.

   Each plane is abstracted to its state-table variable and the ruled rule that moves it; the
   detail of each plane is proved by its own model (trust_root, accord_halt, self_roster,
   mesh_net, withdraws_admission, authority_tree, guarantees) and is ASSUMED here, stated as
   the guard of the corresponding action. What this module checks is only what no plane sees
   alone — the cross-plane invariants of CC rc9:

     X1  a constitutional halt is not a trust leg: the latch moves no standing, stops no
         serving and no replication; it moves exactly the agent's act gate (CC 3.2 T8 (v),
         4.2.1.1, ruling 2026-10-15);
     X2  the authority of a roster key ends with its eviction: an owner act by an evicted key
         is refused, an owner act by any live roster key is admitted (CC 3.3.6.3);
     X3  a node replicates a peer's content only under that peer's replication consent, and a
         revocation is a boundary: nothing replicated after it (CC 3.3.7, 3.3.1);
     X4  a local-tier row never leaves its node; a row reaches another node only at the
         federation tier, which requires the hybrid signature (CC 5.3.2.4, 2.6.1.7);
     X5  leaving the root is one act; it ends the reach of every later halt and keeps every
         record, while a halt latched before the cut keeps its reach until it lapses or is
         resumed (CC 4.2.1: exit is prospective, never retroactive; guarantees Inv_ExitOneStep).

   Bounded instance: three roster keys, one peer, two rows. The catalogue's maxima are reached
   through the per-plane configurations tools/topology_to_cfg.py writes, not here. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Keys,        \* the self's roster keys (genesis included; symmetric)
          Peer,        \* one peer node whose content this node may replicate
          Rows,        \* row identifiers
          LatchBlocksServe   \* FALSE as ruled; TRUE = the breaker named on G7 at rc8 (persist's trust verdict
                             \*   folding the latch, edge's serve gate reading it; closes at the v58 pin)

VARIABLES
  member,        \* key.membership = member            : SUBSET Keys
  subscribed,    \* node.subscribed                    : BOOLEAN
  standing,      \* root.standing                      : "NotRooted" | "Stalled" | "Rooted"
  headFresh,     \* root.head = witnessed_fresh        : BOOLEAN
  rootHalt,      \* root.halt                          : "not_halted" | "latched_lone" | "confirmed"
  latch,         \* node.halt_latch = latched          : BOOLEAN
  gate,          \* agent.halt_gate                    : "acting" | "refusing"
  bound,         \* subscribed at the live halt's asserted_at : BOOLEAN (CC 4.2.1 reach pin)
  serving,       \* node.serve = serving               : BOOLEAN
  peerConsent,   \* consent.replication from Peer      : "none" | "granted" | "revoked"
  replicated,    \* rows of Peer this node holds       : SUBSET Rows
  tier,          \* row.tier for this node's own rows  : [Rows -> {"none", "local", "federation"}]
  signed,        \* hybrid signature present           : [Rows -> BOOLEAN]
  heldByPeer,    \* this node's rows the peer holds    : SUBSET Rows
  ownerActs      \* owner acts admitted, by key        : SUBSET Keys

vars == <<member, subscribed, standing, headFresh, rootHalt, latch, gate, bound, serving,
          peerConsent, replicated, tier, signed, heldByPeer, ownerActs>>

Standings == {"NotRooted", "Stalled", "Rooted"}
Halts == {"not_halted", "latched_lone", "confirmed"}
Tiers == {"none", "local", "federation"}
Consents == {"none", "granted", "revoked"}

TypeOK == /\ member \subseteq Keys /\ subscribed \in BOOLEAN /\ standing \in Standings
          /\ headFresh \in BOOLEAN /\ rootHalt \in Halts /\ latch \in BOOLEAN /\ bound \in BOOLEAN
          /\ gate \in {"acting", "refusing"} /\ serving \in BOOLEAN /\ peerConsent \in Consents
          /\ replicated \subseteq Rows /\ tier \in [Rows -> Tiers] /\ signed \in [Rows -> BOOLEAN]
          /\ heldByPeer \subseteq Rows /\ ownerActs \subseteq Keys

Init == /\ member = Keys /\ subscribed = FALSE /\ standing = "NotRooted" /\ headFresh \in BOOLEAN
        /\ rootHalt = "not_halted" /\ latch = FALSE /\ gate = "acting" /\ bound = FALSE /\ serving = FALSE
        /\ peerConsent = "none" /\ replicated = {} /\ tier = [r \in Rows |-> "none"]
        /\ signed = [r \in Rows |-> FALSE] /\ heldByPeer = {} /\ ownerActs = {}

(* ---- root plane (trust_root proves T8; here: the edge and the head) ---- *)
Attach == /\ ~subscribed /\ headFresh                     \* T4a: only on a fresh witnessed head
          /\ subscribed' = TRUE /\ standing' = "Rooted"
          /\ UNCHANGED <<member, headFresh, rootHalt, latch, gate, serving, peerConsent, replicated, tier, signed, heldByPeer, ownerActs, bound>>
Stall  == /\ standing = "Rooted" /\ standing' = "Stalled"  \* a revocation leaves M or fewer (T7)
          /\ UNCHANGED <<member, subscribed, headFresh, rootHalt, latch, gate, serving, peerConsent, replicated, tier, signed, heldByPeer, ownerActs, bound>>
Recover == /\ standing = "Stalled" /\ standing' = "Rooted"
           /\ UNCHANGED <<member, subscribed, headFresh, rootHalt, latch, gate, serving, peerConsent, replicated, tier, signed, heldByPeer, ownerActs, bound>>
HeadAges == /\ headFresh /\ headFresh' = FALSE             \* T8 (ii): a tick moves no standing
            /\ UNCHANGED <<member, subscribed, standing, rootHalt, latch, gate, serving, peerConsent, replicated, tier, signed, heldByPeer, ownerActs, bound>>
HeadRefreshed == /\ ~headFresh /\ headFresh' = TRUE
                 /\ UNCHANGED <<member, subscribed, standing, rootHalt, latch, gate, serving, peerConsent, replicated, tier, signed, heldByPeer, ownerActs, bound>>
(* X5: leaving is one act and keeps every record; it ends the reach of every later halt, and a halt
   latched before the cut keeps its reach until it lapses or is resumed (CC 4.2.1: exit is prospective) *)
Leave == /\ subscribed /\ subscribed' = FALSE /\ standing' = "NotRooted"
         /\ UNCHANGED <<member, headFresh, rootHalt, latch, gate, bound, serving, peerConsent, replicated, tier, signed, heldByPeer, ownerActs>>

(* ---- halt plane (accord_halt proves the fuse and the majorities; here: reach) ---- *)
Fire == /\ rootHalt = "not_halted" /\ rootHalt' = "latched_lone"
        /\ latch' = subscribed /\ gate' = (IF subscribed THEN "refusing" ELSE "acting") /\ bound' = subscribed
        /\ UNCHANGED <<member, subscribed, standing, headFresh, serving, peerConsent, replicated, tier, signed, heldByPeer, ownerActs>>
Confirm == /\ rootHalt = "latched_lone" /\ rootHalt' = "confirmed"
           /\ UNCHANGED <<member, subscribed, standing, headFresh, latch, gate, serving, peerConsent, replicated, tier, signed, heldByPeer, ownerActs, bound>>
Lapse == /\ rootHalt = "latched_lone" /\ rootHalt' = "not_halted" /\ latch' = FALSE /\ gate' = "acting" /\ bound' = FALSE
         /\ UNCHANGED <<member, subscribed, standing, headFresh, serving, peerConsent, replicated, tier, signed, heldByPeer, ownerActs>>
Resume == /\ rootHalt \in {"latched_lone", "confirmed"} /\ rootHalt' = "not_halted" /\ latch' = FALSE /\ gate' = "acting" /\ bound' = FALSE
          /\ UNCHANGED <<member, subscribed, standing, headFresh, serving, peerConsent, replicated, tier, signed, heldByPeer, ownerActs>>

(* ---- node plane: serving is the owner's act, never the latch's ---- *)
Seat == /\ ~serving /\ serving' = TRUE
        /\ UNCHANGED <<member, subscribed, standing, headFresh, rootHalt, latch, gate, peerConsent, replicated, tier, signed, heldByPeer, ownerActs, bound>>
Unseat == /\ serving /\ serving' = FALSE
          /\ UNCHANGED <<member, subscribed, standing, headFresh, rootHalt, latch, gate, peerConsent, replicated, tier, signed, heldByPeer, ownerActs, bound>>

(* ---- self plane (self_roster proves the two paths; here: eviction's effect on authority) ---- *)
Evict(k) == /\ k \in member /\ Cardinality(member) >= 2 /\ member' = member \ {k}
            /\ UNCHANGED <<subscribed, standing, headFresh, rootHalt, latch, gate, serving, peerConsent, replicated, tier, signed, heldByPeer, ownerActs, bound>>
OwnerAct(k) == /\ k \in member                            \* X2: any live roster key acts as the self
               /\ ownerActs' = ownerActs \cup {k}
               /\ UNCHANGED <<member, subscribed, standing, headFresh, rootHalt, latch, gate, serving, peerConsent, replicated, tier, signed, heldByPeer, bound>>
(* an evicted key's attempt is refused: no state moves. Modelled as a stutter so the invariant
   over ownerActs is what the door guarantees. *)

(* ---- consent + content planes (mesh_net proves scope; here: replication consent and tier) ---- *)
Grant == /\ peerConsent # "granted" /\ peerConsent' = "granted"
         /\ UNCHANGED <<member, subscribed, standing, headFresh, rootHalt, latch, gate, serving, replicated, tier, signed, heldByPeer, ownerActs, bound>>
Revoke == /\ peerConsent = "granted" /\ peerConsent' = "revoked"
          /\ UNCHANGED <<member, subscribed, standing, headFresh, rootHalt, latch, gate, serving, replicated, tier, signed, heldByPeer, ownerActs, bound>>
Replicate(r) == /\ peerConsent = "granted" /\ r \notin replicated   \* X3: consent, and X1: the latch is no guard
                /\ replicated' = replicated \cup {r}
                /\ UNCHANGED <<member, subscribed, standing, headFresh, rootHalt, latch, gate, serving, peerConsent, tier, signed, heldByPeer, ownerActs, bound>>
WriteLocal(r) == /\ tier[r] = "none" /\ tier' = [tier EXCEPT ![r] = "local"]
                 /\ UNCHANGED <<member, subscribed, standing, headFresh, rootHalt, latch, gate, serving, peerConsent, replicated, signed, heldByPeer, ownerActs, bound>>
Promote(r) == /\ tier[r] = "local" /\ tier' = [tier EXCEPT ![r] = "federation"] /\ signed' = [signed EXCEPT ![r] = TRUE]
              /\ UNCHANGED <<member, subscribed, standing, headFresh, rootHalt, latch, gate, serving, peerConsent, replicated, heldByPeer, ownerActs, bound>>
Serve(r) == /\ tier[r] = "federation" /\ serving                     \* X4: only a federation-tier row leaves
            /\ ~(LatchBlocksServe /\ latch)                             \* the breaker, when switched on
            /\ heldByPeer' = heldByPeer \cup {r}
            /\ UNCHANGED <<member, subscribed, standing, headFresh, rootHalt, latch, gate, serving, peerConsent, replicated, tier, signed, ownerActs, bound>>

Next == \/ Attach \/ Stall \/ Recover \/ HeadAges \/ HeadRefreshed \/ Leave
        \/ Fire \/ Confirm \/ Lapse \/ Resume \/ Seat \/ Unseat
        \/ \E k \in Keys : Evict(k) \/ OwnerAct(k)
        \/ Grant \/ Revoke
        \/ \E r \in Rows : Replicate(r) \/ WriteLocal(r) \/ Promote(r) \/ Serve(r)

Spec == Init /\ [][Next]_vars

(* ---------------- the cross-plane invariants ---------------- *)
\* X1 the latch is not a trust leg and stops nothing but the agent's act gate
Inv_X1_LatchReachesGateOnly == latch => (gate = "refusing")
Inv_X1_GateOnlyByLatch     == (gate = "refusing") => latch
Inv_X1_LatchOnlySubscribers == latch => bound      \* bound: subscribed at the halt's asserted_at (CC 4.2.1); a later cut does not escape
Inv_X1_BoundOnlyLive == bound => rootHalt # "not_halted"
\* a halt action is one that moves the latch while the subscription stands (Fire, Lapse, Resume); Leave moves both and is X5's
Prop_X1_LatchMovesNoStanding == [][(latch' # latch /\ subscribed' = subscribed) => (standing' = standing /\ serving' = serving /\ replicated' = replicated /\ heldByPeer' = heldByPeer)]_vars
\* a latched node still serves and still replicates: the latch disables neither (CC 4.2.1.1: the halt reads nothing else)
Inv_X1_LatchDoesNotBlockReplication == (latch /\ peerConsent = "granted" /\ replicated # Rows) => ENABLED (\E r \in Rows : Replicate(r))
Inv_X1_LatchDoesNotBlockServing == (latch /\ serving /\ \E r \in Rows : tier[r] = "federation" /\ r \notin heldByPeer) => ENABLED (\E r \in Rows : Serve(r))
\* X2 eviction ends authority; any live key has it
Inv_X2_OwnerActsAreLive == ownerActs \subseteq Keys     \* every admitted owner act was by a key live at the time (by the guard)
Prop_X2_EvictedKeyNeverActs == [][\A k \in Keys : (k \notin member /\ k \in ownerActs') => k \in ownerActs]_vars
\* X3 replication needs consent; a revocation is a boundary
Prop_X3_ReplicationUnderConsent == [][replicated' # replicated => peerConsent = "granted"]_vars
Prop_X3_RevocationIsBoundary == [][(peerConsent = "revoked") => replicated' = replicated]_vars
\* X4 a local row never leaves; a served row is signed at the federation tier
Inv_X4_LocalStaysLocal == \A r \in heldByPeer : tier[r] = "federation" /\ signed[r]
\* X5 leaving is one act: subscribed falls and the latch lifts in the same step; the record stands
Prop_X5_LeaveIsOneStep == [][(subscribed /\ ~subscribed') => (standing' = "NotRooted" /\ latch' = latch /\ heldByPeer' = heldByPeer /\ replicated' = replicated)]_vars
=============================================================================
