---------------------------- MODULE MeshNet_T11 ----------------------------
(* generated from T11-lost-devices-lone-recovery.yaml by tools/topology_to_cfg.py: MeshNet instantiated with the entry's
   persons, nodes (canonicals are servers), owner map and blobs. *)
EXTENDS Naturals, FiniteSets
CONSTANTS alice, A1, A2, A3, C, b1, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {alice}, Nodes <- {A1, A2, A3, C}, Blobs <- {b1},
       Owner <- [n \in {A1, A2, A3, C} |-> IF n = A1 THEN alice ELSE IF n = A2 THEN alice ELSE IF n = A3 THEN alice ELSE IF n = C THEN alice ELSE alice],
       Class <- [n \in {A1, A2, A3, C} |-> IF n \in {C} THEN "server" ELSE "personal"],
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
