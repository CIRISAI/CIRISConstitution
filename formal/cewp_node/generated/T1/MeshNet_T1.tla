---------------------------- MODULE MeshNet_T1 ----------------------------
(* generated from T1-one-person-two-devices.yaml by tools/topology_to_cfg.py: MeshNet instantiated with the entry's
   persons, nodes (canonicals are servers), owner map and blobs. *)
EXTENDS Naturals, FiniteSets
CONSTANTS one, D1, D2, C, b1, b2, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {one}, Nodes <- {D1, D2, C}, Blobs <- {b1, b2},
       Owner <- [n \in {D1, D2, C} |-> IF n = D1 THEN one ELSE IF n = D2 THEN one ELSE IF n = C THEN one ELSE one],
       Class <- [n \in {D1, D2, C} |-> IF n \in {C} THEN "server" ELSE "personal"],
       InitMembers <- [c \in {"fam", "room", "pub", "commons"} |-> IF c = "fam" THEN {one} ELSE IF c = "room" THEN {one} ELSE IF c = "pub" THEN {one} ELSE {one}],
       InitMods <- [c \in {"fam", "room", "pub", "commons"} |-> IF c \in {"room", "pub"} THEN {one} ELSE {}]
Spec == M!Spec
Inv_KnownHold == M!Inv_KnownHold
Inv_Consent == M!Inv_Consent
Inv_Invisible == M!Inv_Invisible
Inv_ClaimNotBinding == M!Inv_ClaimNotBinding
Inv_Moderated == M!Inv_Moderated
Inv_ScanSeam == M!Inv_ScanSeam
Prop_RestrictOnly == M!Prop_RestrictOnly
=============================================================================
