---------------------------- MODULE MeshNet_T6 ----------------------------
(* generated from T6-affiliation-delegation.yaml by tools/topology_to_cfg.py: MeshNet instantiated with the entry's
   persons, nodes (canonicals are servers), owner map and blobs. *)
EXTENDS Naturals, FiniteSets
CONSTANTS authority, practitioner, L, P, C, b1, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {authority, practitioner}, Nodes <- {L, P, C}, Blobs <- {b1},
       Owner <- [n \in {L, P, C} |-> IF n = L THEN authority ELSE IF n = P THEN practitioner ELSE IF n = C THEN authority ELSE authority],
       Class <- [n \in {L, P, C} |-> IF n \in {C} THEN "server" ELSE "personal"],
       InitMembers <- [c \in {"fam", "room", "pub", "commons"} |-> IF c = "fam" THEN {authority} ELSE IF c = "room" THEN {authority, practitioner} ELSE IF c = "pub" THEN {practitioner} ELSE {authority, practitioner}],
       InitMods <- [c \in {"fam", "room", "pub", "commons"} |-> IF c \in {"room", "pub"} THEN {practitioner} ELSE {}]
Spec == M!Spec
Inv_KnownHold == M!Inv_KnownHold
Inv_Consent == M!Inv_Consent
Inv_Invisible == M!Inv_Invisible
Inv_ClaimNotBinding == M!Inv_ClaimNotBinding
Inv_Moderated == M!Inv_Moderated
Inv_ScanSeam == M!Inv_ScanSeam
Prop_RestrictOnly == M!Prop_RestrictOnly
=============================================================================
