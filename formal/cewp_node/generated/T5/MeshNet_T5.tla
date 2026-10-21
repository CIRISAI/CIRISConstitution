---------------------------- MODULE MeshNet_T5 ----------------------------
(* generated from T5-community-quorum.yaml by tools/topology_to_cfg.py: MeshNet instantiated with the entry's
   persons, nodes (canonicals are servers), owner map and blobs. *)
EXTENDS Naturals, FiniteSets
CONSTANTS alice, bob, carol, A, B, CA, C, b1, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {alice, bob, carol}, Nodes <- {A, B, CA, C}, Blobs <- {b1},
       Owner <- [n \in {A, B, CA, C} |-> IF n = A THEN alice ELSE IF n = B THEN bob ELSE IF n = CA THEN carol ELSE IF n = C THEN alice ELSE alice],
       Class <- [n \in {A, B, CA, C} |-> IF n \in {C} THEN "server" ELSE "personal"],
       InitMembers <- [c \in {"fam", "room", "pub", "commons"} |-> IF c = "fam" THEN {alice} ELSE IF c = "room" THEN {alice, bob} ELSE IF c = "pub" THEN {carol} ELSE {alice, bob, carol}],
       InitMods <- [c \in {"fam", "room", "pub", "commons"} |-> IF c \in {"room", "pub"} THEN {carol} ELSE {}]
Spec == M!Spec
Inv_KnownHold == M!Inv_KnownHold
Inv_Consent == M!Inv_Consent
Inv_Invisible == M!Inv_Invisible
Inv_ClaimNotBinding == M!Inv_ClaimNotBinding
Inv_Moderated == M!Inv_Moderated
Inv_ScanSeam == M!Inv_ScanSeam
Prop_RestrictOnly == M!Prop_RestrictOnly
=============================================================================
