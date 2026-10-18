---------------------------- MODULE MeshNet3 ----------------------------
(* The rc7 instance of MeshNet: three persons, three nodes (n3 is p1's server), two blobs.
   MeshNet itself is parametric since 2026-10-18 so tools/topology_to_cfg.py can instantiate
   it per CSD/4 catalogue entry; this module keeps the ruled and shipped configurations
   exactly as they were checked. *)
EXTENDS Naturals, FiniteSets
CONSTANTS p1, p2, p3, n1, n2, n3, b1, b2, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {p1, p2, p3}, Nodes <- {n1, n2, n3}, Blobs <- {b1, b2},
       Owner <- [n \in {n1, n2, n3} |-> IF n = n2 THEN p2 ELSE p1],
       Class <- [n \in {n1, n2, n3} |-> IF n = n3 THEN "server" ELSE "personal"],
       InitMembers <- [c \in {"fam", "room", "pub", "commons"} |-> IF c = "fam" THEN {p1, p2} ELSE IF c = "room" THEN {p1, p3} ELSE IF c = "pub" THEN {p3} ELSE {p1, p2, p3}],
       InitMods <- [c \in {"fam", "room", "pub", "commons"} |-> IF c \in {"room", "pub"} THEN {p3} ELSE {}]
Spec == M!Spec
Inv_KnownHold == M!Inv_KnownHold
Inv_Consent == M!Inv_Consent
Inv_Invisible == M!Inv_Invisible
Inv_ClaimNotBinding == M!Inv_ClaimNotBinding
Inv_Moderated == M!Inv_Moderated
Inv_ScanSeam == M!Inv_ScanSeam
Prop_RestrictOnly == M!Prop_RestrictOnly
=============================================================================
