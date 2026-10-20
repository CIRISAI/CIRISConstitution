---------------------------- MODULE MeshNet_T15 ----------------------------
(* generated from T15-community-ceremony.yaml by tools/topology_to_cfg.py: MeshNet instantiated with the entry's
   persons, nodes (canonicals are servers), owner map and blobs. *)
EXTENDS Naturals, FiniteSets
CONSTANTS alice, bob, carol, dave, erin, frank, gus, A, B, CA, D, E, F, G, C, b1, ClaimScope, ClaimsBind
VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted
M == INSTANCE MeshNet WITH Persons <- {alice, bob, carol, dave, erin, frank, gus}, Nodes <- {A, B, CA, D, E, F, G, C}, Blobs <- {b1},
       Owner <- [n \in {A, B, CA, D, E, F, G, C} |-> IF n = A THEN alice ELSE IF n = B THEN bob ELSE IF n = CA THEN carol ELSE IF n = D THEN dave ELSE IF n = E THEN erin ELSE IF n = F THEN frank ELSE IF n = G THEN gus ELSE IF n = C THEN alice ELSE alice],
       Class <- [n \in {A, B, CA, D, E, F, G, C} |-> IF n \in {C} THEN "server" ELSE "personal"],
       InitMembers <- [c \in {"fam", "room", "pub", "commons"} |-> IF c = "fam" THEN {alice} ELSE IF c = "room" THEN {alice, bob} ELSE IF c = "pub" THEN {gus} ELSE {alice, bob, carol, dave, erin, frank, gus}],
       InitMods <- [c \in {"fam", "room", "pub", "commons"} |-> IF c \in {"room", "pub"} THEN {gus} ELSE {}]
Spec == M!Spec
Inv_KnownHold == M!Inv_KnownHold
Inv_Consent == M!Inv_Consent
Inv_Invisible == M!Inv_Invisible
Inv_ClaimNotBinding == M!Inv_ClaimNotBinding
Inv_Moderated == M!Inv_Moderated
Inv_ScanSeam == M!Inv_ScanSeam
Prop_RestrictOnly == M!Prop_RestrictOnly
=============================================================================
