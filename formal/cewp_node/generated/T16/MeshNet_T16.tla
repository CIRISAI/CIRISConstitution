---------------------------- MODULE MeshNet_T16 ----------------------------
(* generated from T16-agent-retirement.yaml by tools/topology_to_cfg.py: MeshNet instantiated with the entry's
   persons, nodes (canonicals are servers), owner map and blobs. *)
EXTENDS Naturals, FiniteSets
CONSTANTS steward, N, C, b1, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {steward}, Nodes <- {N, C}, Blobs <- {b1},
       Owner <- [n \in {N, C} |-> IF n = N THEN steward ELSE IF n = C THEN steward ELSE steward],
       Class <- [n \in {N, C} |-> IF n \in {C} THEN "server" ELSE "personal"],
       InitMembers <- [c \in {"fam", "room", "pub", "commons"} |-> IF c = "fam" THEN {steward} ELSE IF c = "room" THEN {steward} ELSE IF c = "pub" THEN {steward} ELSE {steward}],
       InitMods <- [c \in {"fam", "room", "pub", "commons"} |-> IF c \in {"room", "pub"} THEN {steward} ELSE {}]
Spec == M!Spec
Inv_KnownHold == M!Inv_KnownHold
Inv_Consent == M!Inv_Consent
Inv_Invisible == M!Inv_Invisible
Inv_ClaimNotBinding == M!Inv_ClaimNotBinding
Inv_Moderated == M!Inv_Moderated
Inv_ScanSeam == M!Inv_ScanSeam
Prop_RestrictOnly == M!Prop_RestrictOnly
=============================================================================
