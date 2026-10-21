---------------------------- MODULE MeshNet_T4 ----------------------------
(* generated from T4-household.yaml by tools/topology_to_cfg.py: MeshNet instantiated with the entry's
   persons, nodes (canonicals are servers), owner map and blobs. *)
EXTENDS Naturals, FiniteSets
CONSTANTS guardian, child, G1, G2, K, C, b1, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {guardian, child}, Nodes <- {G1, G2, K, C}, Blobs <- {b1},
       Owner <- [n \in {G1, G2, K, C} |-> IF n = G1 THEN guardian ELSE IF n = G2 THEN guardian ELSE IF n = K THEN child ELSE IF n = C THEN guardian ELSE guardian],
       Class <- [n \in {G1, G2, K, C} |-> IF n \in {C} THEN "server" ELSE "personal"],
       InitMembers <- [c \in {"fam", "room", "pub", "commons"} |-> IF c = "fam" THEN {guardian, child} ELSE IF c = "room" THEN {guardian, child} ELSE IF c = "pub" THEN {child} ELSE {guardian, child}],
       InitMods <- [c \in {"fam", "room", "pub", "commons"} |-> IF c \in {"room", "pub"} THEN {child} ELSE {}]
Spec == M!Spec
Inv_KnownHold == M!Inv_KnownHold
Inv_Consent == M!Inv_Consent
Inv_Invisible == M!Inv_Invisible
Inv_ClaimNotBinding == M!Inv_ClaimNotBinding
Inv_Moderated == M!Inv_Moderated
Inv_ScanSeam == M!Inv_ScanSeam
Prop_RestrictOnly == M!Prop_RestrictOnly
=============================================================================
