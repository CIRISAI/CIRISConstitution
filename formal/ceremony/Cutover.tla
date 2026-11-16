------------------------------ MODULE Cutover ------------------------------
(* The genesis of this edition, a clean mesh (CC 2.6.1.12, CC 2.4.1.1, CC 4.2.1.1, CC 5.3.4), where order matters.

   Nothing carries. The world signs, in any order the rules allow: the holders' key records of this form (one
   delivery, "RH"), each holder's pre-signed halt of this form (sealed, "PH"), the genesis ("G", which names RH and is
   published only once the halts are sealed), a user's record of this form after it ("Ru"), the resumption's
   statements of this form ("R1", "R2"), and, from the earlier mesh, a late row ("L"), an earlier sealed halt ("HE") and
   an earlier resumption statement ("R2e"). A holder may publish its sealed halt at any time after the genesis. Two
   upgraded nodes receive the signed and published rows one at a time, in any order; one of them receives nothing
   until the genesis is signed. Each node keeps an implementation's state, updated one arrival at a time.

   The truth each state is checked against is a function of the rows a node holds:
     no earlier-form row counts for anything (P1);
     a key is live iff the node holds its record of this form (P2);
     a resumption counts on a strict majority of holders whose statements of this form count (P7);
     two nodes holding the same rows agree (P9);
     a halt of this form is available from the first moment after the genesis, and the earlier halt never latches.

   Planted breaks are constants; each twin configuration turns one on and must fail on its invariant. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Nodes, Late,      \* Late: a node that receives nothing until the genesis is signed
          AcceptEarlier,    \* P1 plant: an earlier-form row is accepted
          ArrivalEarlier,   \* P9 plant: an earlier-form row that arrives before the genesis is kept as accepted
          CeremonyCarries,  \* P2 plant: the genesis makes a key live that has no record of this form
          EarlierVotes,     \* P7 plant: an earlier-form statement counts toward a resumption
          PublishUngated,   \* halt plant: the genesis is signed before the holders' halts are sealed
          CutWithoutRecords,\* halt plant: the genesis is kept without the holders' records it names
          EarlierHalt       \* halt plant: an earlier-form halt latches

Holders == {"h1", "h2", "h3"}
Keys    == Holders \cup {"u"}
RecOf   == [k \in Keys |-> IF k = "u" THEN "Ru" ELSE "RH"]
Earlier == {"L", "HE", "R2e"}
Forward == {"RH", "Ru", "G", "PH", "R1", "R2"}
M       == Cardinality(Holders) \div 2 + 1

VARIABLES signed, published, held, acc, live, latched, resumed, countedWith
vars == <<signed, published, held, acc, live, latched, resumed, countedWith>>

\* ---- the door: what a node keeps of what it holds --------------------------------------------------------
Kept(H) == (H \ Earlier) \ ( (IF "RH" \in H \/ CutWithoutRecords THEN {} ELSE {"G"})
                             \cup (IF "RH" \in H THEN {} ELSE {"PH", "R1", "R2"}) )
Gen(H)  == "G" \in Kept(H)

\* ---- the truth, a function of the rows held ---------------------------------------------------------------
TrueLive(H) == {k \in Keys : RecOf[k] \in H}
Valid(H)    == (IF "R1" \in Kept(H) /\ Gen(H) THEN {"h1"} ELSE {}) \cup (IF "R2" \in Kept(H) /\ Gen(H) THEN {"h2"} ELSE {})
Honoured(H) == "PH" \in Kept(H) /\ Gen(H)

Init == /\ signed = {} /\ published = {}
        /\ held = [n \in Nodes |-> {}] /\ acc = [n \in Nodes |-> {}] /\ live = [n \in Nodes |-> {}]
        /\ latched = [n \in Nodes |-> "none"] /\ resumed = [n \in Nodes |-> FALSE]
        /\ countedWith = [n \in Nodes |-> {}]

Quiet == UNCHANGED <<held, acc, live, latched, resumed, countedWith>>
Sign(r) == /\ r \notin signed /\ signed' = signed \cup {r}
           /\ published' = IF r = "PH" THEN published ELSE published \cup {r}   \* a pre-signed halt stays sealed
           /\ Quiet

\* ---- the world signs -----------------------------------------------------------------------------------
SignRH   == Sign("RH")
SignPH   == "RH" \in signed /\ Sign("PH")
SignG    == /\ "RH" \in signed /\ ("PH" \in signed \/ PublishUngated) /\ Sign("G")
SignRu   == "G" \in signed /\ Sign("Ru")
SignR(r) == /\ r \in {"R1", "R2"} /\ "G" \in signed /\ Sign(r)
SignEarlier(r) == r \in Earlier /\ Sign(r)                                   \* the earlier mesh goes on, apart
PublishPH == /\ "PH" \in signed /\ "G" \in signed /\ "PH" \notin published
             /\ published' = published \cup {"PH"} /\ UNCHANGED signed /\ Quiet

\* ---- a node receives one row, and updates its state as an implementation does ------------------------
Deliver(n, r) ==
  LET H  == held[n]
      H2 == H \cup {r}
      NK == Kept(H2) \ Kept(H)
      newE == IF r \in Earlier /\ (AcceptEarlier \/ (ArrivalEarlier /\ ~Gen(H2))) THEN {r} ELSE {}
      A2 == acc[n] \cup newE
      L2 == live[n] \cup {k \in Keys : RecOf[k] \in NK} \cup (IF CeremonyCarries /\ "G" \in NK THEN {"u"} ELSE {})
      halt == IF Honoured(H2) THEN "PH" ELSE IF EarlierHalt /\ "HE" \in H2 THEN "HE" ELSE "none"
      lat1 == IF latched[n] = "none" /\ ~resumed[n] THEN halt ELSE latched[n]
      implValid == Valid(H2) \cup (IF EarlierVotes /\ "R2e" \in H2 THEN {"h2"} ELSE {})
      counts == lat1 /= "none" /\ Cardinality(implValid) >= M
  IN /\ r \in published /\ r \notin H /\ (n = Late => "G" \in signed)
     /\ held' = [held EXCEPT ![n] = H2]
     /\ acc' = [acc EXCEPT ![n] = A2]
     /\ live' = [live EXCEPT ![n] = L2]
     /\ IF counts
           THEN /\ latched' = [latched EXCEPT ![n] = "none"] /\ resumed' = [resumed EXCEPT ![n] = TRUE]
                /\ countedWith' = [countedWith EXCEPT ![n] = Valid(H2)]
           ELSE /\ latched' = [latched EXCEPT ![n] = lat1] /\ UNCHANGED <<resumed, countedWith>>
     /\ UNCHANGED <<signed, published>>

Next == \/ SignRH \/ SignPH \/ SignG \/ SignRu \/ PublishPH
        \/ \E r \in {"R1", "R2"} : SignR(r)
        \/ \E r \in Earlier : SignEarlier(r)
        \/ \E n \in Nodes, r \in Earlier \cup Forward : Deliver(n, r)

Spec == Init /\ [][Next]_vars

\* ---- invariants --------------------------------------------------------------------------------------------
TypeOK == \A n \in Nodes : held[n] \subseteq published /\ published \subseteq signed
\* P1: no earlier-form row counts for anything
Inv_P1 == \A n \in Nodes : acc[n] = {}
\* P2: a key is live in this form iff the node holds its record of this form
Inv_P2 == \A n \in Nodes : live[n] = TrueLive(held[n])
\* P7: a resumption counted at a node was counted on a strict majority of holders' statements of this form
Inv_P7 == \A n \in Nodes : resumed[n] => Cardinality(countedWith[n]) >= M
\* P9: two nodes that hold the same rows give the same answers, whatever the order they received them in
Inv_P9 == \A n, m \in Nodes : held[n] = held[m] => acc[n] = acc[m] /\ live[n] = live[m]
\* the halt: from the first moment after the genesis, every holder has a sealed halt of this form
Inv_HaltAvailable == "G" \in signed => "PH" \in signed
\* the halt: a node that holds the genesis holds the holders' records, so a holder's halt is honoured there
Inv_HaltPathOpen == \A n \in Nodes : Gen(held[n]) => "RH" \in held[n]
\* the halt: no earlier-form halt ever latches a node of this form
Inv_NoEarlierLatch == \A n \in Nodes : latched[n] /= "HE"
=============================================================================
