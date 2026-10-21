---------------------------- MODULE MeshNet_T19 ----------------------------
(* generated from T19-holders-under-coercion.yaml by tools/topology_to_cfg.py: MeshNet instantiated with the entry's
   persons, nodes (canonicals are servers), owner map and blobs. *)
EXTENDS Naturals, FiniteSets
CONSTANTS alice, bob, A, B, C, b1, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {alice, bob}, Nodes <- {A, B, C}, Blobs <- {b1},
       Owner <- [n \in {A, B, C} |-> IF n = A THEN alice ELSE IF n = B THEN bob ELSE IF n = C THEN alice ELSE alice],
       Class <- [n \in {A, B, C} |-> IF n \in {C} THEN "server" ELSE "personal"],
       InitMembers <- [c \in {"fam", "room", "pub", "commons"} |-> IF c = "fam" THEN {alice} ELSE IF c = "room" THEN {alice, bob} ELSE IF c = "pub" THEN {bob} ELSE {alice, bob}],
       InitMods <- [c \in {"fam", "room", "pub", "commons"} |-> IF c \in {"room", "pub"} THEN {bob} ELSE {}]
Spec == M!Spec
Inv_KnownHold == M!Inv_KnownHold
Inv_Consent == M!Inv_Consent
Inv_Invisible == M!Inv_Invisible
Inv_ClaimNotBinding == M!Inv_ClaimNotBinding
Inv_Moderated == M!Inv_Moderated
Inv_ScanSeam == M!Inv_ScanSeam
Prop_RestrictOnly == M!Prop_RestrictOnly
=============================================================================
