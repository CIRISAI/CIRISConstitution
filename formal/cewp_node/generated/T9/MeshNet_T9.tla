---------------------------- MODULE MeshNet_T9 ----------------------------
(* generated from T9-two-roots-outsider.yaml by tools/topology_to_cfg.py: MeshNet instantiated with the entry's
   persons, nodes (canonicals are servers), owner map and blobs. *)
EXTENDS Naturals, FiniteSets
CONSTANTS alice, bob, zed, A, B, Z, C1, C2, b1, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {alice, bob, zed}, Nodes <- {A, B, Z, C1, C2}, Blobs <- {b1},
       Owner <- [n \in {A, B, Z, C1, C2} |-> IF n = A THEN alice ELSE IF n = B THEN bob ELSE IF n = Z THEN zed ELSE IF n = C1 THEN alice ELSE IF n = C2 THEN alice ELSE alice],
       Class <- [n \in {A, B, Z, C1, C2} |-> IF n \in {C1, C2} THEN "server" ELSE "personal"],
       InitMembers <- [c \in {"fam", "room", "pub", "commons"} |-> IF c = "fam" THEN {alice} ELSE IF c = "room" THEN {alice, bob} ELSE IF c = "pub" THEN {zed} ELSE {alice, bob, zed}],
       InitMods <- [c \in {"fam", "room", "pub", "commons"} |-> IF c \in {"room", "pub"} THEN {zed} ELSE {}]
Spec == M!Spec
Inv_KnownHold == M!Inv_KnownHold
Inv_Consent == M!Inv_Consent
Inv_Invisible == M!Inv_Invisible
Inv_ClaimNotBinding == M!Inv_ClaimNotBinding
Inv_Moderated == M!Inv_Moderated
Inv_ScanSeam == M!Inv_ScanSeam
Prop_RestrictOnly == M!Prop_RestrictOnly
=============================================================================
