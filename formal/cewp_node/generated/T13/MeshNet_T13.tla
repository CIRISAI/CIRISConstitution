---------------------------- MODULE MeshNet_T13 ----------------------------
(* generated from T13-witnessed-lineage.yaml by tools/topology_to_cfg.py: MeshNet instantiated with the entry's
   persons, nodes (canonicals are servers), owner map and blobs. *)
EXTENDS Naturals, FiniteSets
CONSTANTS alice, A, C, b1, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {alice}, Nodes <- {A, C}, Blobs <- {b1},
       Owner <- [n \in {A, C} |-> IF n = A THEN alice ELSE IF n = C THEN alice ELSE alice],
       Class <- [n \in {A, C} |-> IF n \in {C} THEN "server" ELSE "personal"],
       InitMembers <- [c \in {"fam", "room", "pub", "commons"} |-> IF c = "fam" THEN {alice} ELSE IF c = "room" THEN {alice} ELSE IF c = "pub" THEN {alice} ELSE {alice}],
       InitMods <- [c \in {"fam", "room", "pub", "commons"} |-> IF c \in {"room", "pub"} THEN {alice} ELSE {}]
Spec == M!Spec
Inv_KnownHold == M!Inv_KnownHold
Inv_Consent == M!Inv_Consent
Inv_Invisible == M!Inv_Invisible
Inv_ClaimNotBinding == M!Inv_ClaimNotBinding
Inv_Moderated == M!Inv_Moderated
Inv_ScanSeam == M!Inv_ScanSeam
Prop_RestrictOnly == M!Prop_RestrictOnly
=============================================================================
