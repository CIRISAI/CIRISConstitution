---------------------------- MODULE MeshNet_T2 ----------------------------
(* generated from T2-pair-room-outsider.yaml by tools/topology_to_cfg.py: MeshNet instantiated with the entry's
   persons, nodes (canonicals are servers), owner map and blobs. *)
EXTENDS Naturals, FiniteSets
CONSTANTS alice, bob, eve, A, B, X, C, b1, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {alice, bob, eve}, Nodes <- {A, B, X, C}, Blobs <- {b1},
       Owner <- [n \in {A, B, X, C} |-> IF n = A THEN alice ELSE IF n = B THEN bob ELSE IF n = X THEN eve ELSE IF n = C THEN alice ELSE alice],
       Class <- [n \in {A, B, X, C} |-> IF n \in {C} THEN "server" ELSE "personal"],
       InitMembers <- [c \in {"fam", "room", "pub", "commons"} |-> IF c = "fam" THEN {alice} ELSE IF c = "room" THEN {alice, bob} ELSE IF c = "pub" THEN {eve} ELSE {alice, bob, eve}],
       InitMods <- [c \in {"fam", "room", "pub", "commons"} |-> IF c \in {"room", "pub"} THEN {eve} ELSE {}]
Spec == M!Spec
Inv_KnownHold == M!Inv_KnownHold
Inv_Consent == M!Inv_Consent
Inv_Invisible == M!Inv_Invisible
Inv_ClaimNotBinding == M!Inv_ClaimNotBinding
Inv_Moderated == M!Inv_Moderated
Inv_ScanSeam == M!Inv_ScanSeam
Prop_RestrictOnly == M!Prop_RestrictOnly
=============================================================================
