------------------------------ MODULE Cutover ------------------------------
(* The edition-2 cutover where order matters (CC 2.6.1.12, CC 2.4.1.1, CC 4.2.1.1).

   The world signs rows in any order the rules allow: the holders' key records of this form, a user's record
   of this form, the acknowledgement of the carried scope, an earlier-form row signed late, the ceremony row,
   one halt (of the earlier form, fired in the window, or of this form), and the statements of its resumption.
   Two upgraded nodes receive the signed rows in any order, one at a time; a node offline through the ceremony
   is a node that receives the ceremony row late. Each node keeps the state an implementation keeps, updated
   one arrival at a time: the earlier rows it accepts, the keys it holds live, its halt latch.

   The truth each state is checked against is a function of the rows a node holds:
     an earlier row counts iff the node does not hold the ceremony row, or the row is in its past (P1);
     a key is live iff the node holds its record of this form (P2);
     a resumption counts on a strict majority of holders whose statements count (P7);
     two nodes holding the same rows agree (P9).

   Planted breaks are constants; each twin configuration turns one on and must fail on its invariant. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Nodes, Late, HaltKind,  \* HaltKind: "E", one halt of the earlier form fired in the window, or "F", of this form     \* Late: the node offline through the ceremony; it receives nothing until the ceremony row is signed
          NoRecheck,          \* P9 plant: on the ceremony row, the earlier rows already accepted are not read again
          ByInstant,          \* P1 plant: an earlier row signed before the ceremony row in wall time counts
          CeremonyCarries,    \* P2 plant: the ceremony row makes a key live that has no record of this form
          EarlierAfterCut,    \* P7 plant: an earlier-form statement outside the past counts toward a resumption
          CutWithoutRecords,  \* halt plant: the ceremony row is kept without the holders' records it names
          CutClears,          \* halt plant: the ceremony row clears a latch whose halt it no longer honours
          ResumeNeedsHonoured \* the text's gap: a resumption counts only for a halt the node still honours

Holders == {"h1", "h2", "h3"}
Keys    == Holders \cup {"u"}
\* the three holders sign their key records of this form together, as one delivery ("RH"); a user's record is "Ru"
RecOf   == [k \in Keys |-> IF k = "u" THEN "Ru" ELSE "RH"]
HRecs   == {"RH"}
Earlier == {"P0", "L", "HE", "R2e"}       \* P0 carried; L late; HE an earlier-form halt; R2e an earlier-form resumption statement
Forward == HRecs \cup {"Ru", "CR", "HF", "R1", "R2"}
M       == Cardinality(Holders) \div 2 + 1

VARIABLES signed, ack, past, beforeCR, fired, held, acc, live, latched, resumed, clearedBy, countedWith
vars == <<signed, ack, past, beforeCR, fired, held, acc, live, latched, resumed, clearedBy, countedWith>>

\* ---- the door: what a node keeps of what it holds --------------------------------------------------------
Kept(H) == H \ ( (IF HRecs \subseteq H \/ CutWithoutRecords THEN {} ELSE {"CR"})
               \cup (IF "RH" \in H THEN {} ELSE {"HF", "R1", "R2"}) )
Cut(H) == "CR" \in Kept(H)

\* ---- the truth, a function of the rows held ---------------------------------------------------------------
TrueAcc(H)  == IF Cut(H) THEN Kept(H) \cap Earlier \cap past ELSE Kept(H) \cap Earlier
TrueLive(H) == {k \in Keys : RecOf[k] \in H}
Valid(H, A) == (IF "R1" \in Kept(H) THEN {"h1"} ELSE {}) \cup (IF "R2" \in Kept(H) THEN {"h2"} ELSE {})
               \cup (IF "R2e" \in A THEN {"h2"} ELSE {})
Honoured(H, A) == ("HE" \in fired /\ "HE" \in A) \/ ("HF" \in fired /\ "HF" \in Kept(H))

Init == /\ signed = {"P0"} /\ ack = FALSE /\ past = {} /\ beforeCR = {} /\ fired = {}
        /\ held = [n \in Nodes |-> {"P0"}] /\ acc = [n \in Nodes |-> {"P0"}] /\ live = [n \in Nodes |-> {}]
        /\ latched = [n \in Nodes |-> FALSE] /\ resumed = [n \in Nodes |-> FALSE]
        /\ clearedBy = [n \in Nodes |-> "none"] /\ countedWith = [n \in Nodes |-> {}]

Quiet == UNCHANGED <<held, acc, live, latched, resumed, clearedBy, countedWith>>

\* ---- the world signs -----------------------------------------------------------------------------------
SignRec(k) == /\ RecOf[k] \notin signed /\ (k \in Holders => k = "h1") /\ signed' = signed \cup {RecOf[k]}
              /\ (k = "u" => "CR" \in signed)                \* a user carries its key over after the ceremony
              /\ UNCHANGED <<ack, past, beforeCR, fired>> /\ Quiet
Ack == /\ ~ack /\ ack' = TRUE /\ past' = signed \cap Earlier
       /\ UNCHANGED <<signed, beforeCR, fired>> /\ Quiet
SignLate == /\ ack /\ "L" \notin signed /\ signed' = signed \cup {"L"}
            /\ UNCHANGED <<ack, past, beforeCR, fired>> /\ Quiet
SignCR == /\ ack /\ HRecs \subseteq signed /\ "CR" \notin signed
          /\ signed' = signed \cup {"CR"} /\ beforeCR' = signed \cap Earlier
          /\ UNCHANGED <<ack, past, fired>> /\ Quiet
FireEarlier == /\ HaltKind = "E" /\ fired = {} /\ ack /\ "CR" \notin signed    \* fired in the window, on a node of the earlier form
               /\ fired' = {"HE"} /\ signed' = signed \cup {"HE"}
               /\ UNCHANGED <<ack, past, beforeCR>> /\ Quiet
FireForward == /\ HaltKind = "F" /\ fired = {} /\ "RH" \in signed /\ fired' = {"HF"} /\ signed' = signed \cup {"HF"}
               /\ UNCHANGED <<ack, past, beforeCR>> /\ Quiet
SignResume(r) == /\ fired /= {} /\ r \notin signed
                 /\ (r \in {"R1", "R2"} => "RH" \in signed)
                 /\ signed' = signed \cup {r}
                 /\ UNCHANGED <<ack, past, beforeCR, fired>> /\ Quiet

\* ---- a node receives one row, and updates its state as an implementation does ------------------------
Ok(e) == e \in past \/ (ByInstant /\ e \in beforeCR)

Deliver(n, r) ==
  LET H  == held[n]
      H2 == H \cup {r}
      NK == Kept(H2) \ Kept(H)
      cut == Cut(H2)
      old == IF "CR" \in NK /\ NoRecheck THEN acc[n] ELSE {e \in acc[n] : ~cut \/ Ok(e)}
      A2 == old \cup {e \in NK \cap Earlier : ~cut \/ Ok(e)}
      L2 == live[n] \cup {k \in Keys : RecOf[k] \in NK} \cup (IF CeremonyCarries /\ "CR" \in NK THEN {"u"} ELSE {})
      hon == Honoured(H2, A2)
      lat1 == latched[n] \/ (hon /\ ~resumed[n])
      drop == CutClears /\ "CR" \in NK /\ lat1 /\ ~hon
      implValid == Valid(H2, A2) \cup (IF EarlierAfterCut /\ "R2e" \in Kept(H2) THEN {"h2"} ELSE {})
      counts == Cardinality(implValid) >= M /\ (hon \/ ~ResumeNeedsHonoured)
      lat2 == IF drop THEN FALSE ELSE lat1
  IN /\ r \in signed /\ r \notin H /\ (n = Late => "CR" \in signed)
     /\ held' = [held EXCEPT ![n] = H2]
     /\ acc' = [acc EXCEPT ![n] = A2]
     /\ live' = [live EXCEPT ![n] = L2]
     /\ IF counts /\ lat2
           THEN /\ latched' = [latched EXCEPT ![n] = FALSE] /\ resumed' = [resumed EXCEPT ![n] = TRUE]
                /\ clearedBy' = [clearedBy EXCEPT ![n] = "resume"]
                /\ countedWith' = [countedWith EXCEPT ![n] = Valid(H2, TrueAcc(H2))]
           ELSE /\ latched' = [latched EXCEPT ![n] = lat2] /\ UNCHANGED <<resumed, countedWith>>
                /\ clearedBy' = [clearedBy EXCEPT ![n] = IF drop THEN "other" ELSE clearedBy[n]]
     /\ UNCHANGED <<signed, ack, past, beforeCR, fired>>

Next == \/ \E k \in Keys : SignRec(k)
        \/ Ack \/ SignLate \/ SignCR \/ FireEarlier \/ FireForward
        \/ \E r \in {"R1", "R2", "R2e"} : SignResume(r)
        \/ \E n \in Nodes, r \in Earlier \cup Forward : Deliver(n, r)

Spec == Init /\ [][Next]_vars

\* ---- invariants --------------------------------------------------------------------------------------------
TypeOK == /\ signed \subseteq Earlier \cup Forward /\ \A n \in Nodes : held[n] \subseteq signed
\* P1: an earlier row counts iff the node does not hold the ceremony row, or the row is in its past
Inv_P1 == \A n \in Nodes : acc[n] = TrueAcc(held[n])
\* P2: a key is live in this form iff the node holds its record of this form
Inv_P2 == \A n \in Nodes : live[n] = TrueLive(held[n])
\* P7: a resumption counted at a node was counted on a strict majority of holders whose statements counted then
Inv_P7 == \A n \in Nodes : resumed[n] => Cardinality(countedWith[n]) >= M
\* P9: two nodes that hold the same rows give the same answers, whatever the order they received them in
Inv_P9 == \A n, m \in Nodes : held[n] = held[m] => acc[n] = acc[m] /\ live[n] = live[m]
\* the halt: a node that holds the ceremony row holds the holders' keys of this form, so a holder's halt is honoured there
Inv_HaltPathOpen == \A n \in Nodes : Cut(held[n]) => "RH" \in held[n]
\* the halt: a latch ends only by a counted resumption (CC 4.2.1.3)
Inv_LatchOnlyByResume == \A n \in Nodes : clearedBy[n] /= "other"
\* the halt: a node holding a strict majority's resumption of its latched halt is not left latched
Inv_NoStranded == \A n \in Nodes : (latched[n] /\ Cardinality(Valid(held[n], TrueAcc(held[n]))) >= M) => FALSE
\* a finding, not a property: a resumption counted on an earlier-form statement keeps its count
Inv_ResumeStable == \A n \in Nodes : resumed[n] => Cardinality(Valid(held[n], TrueAcc(held[n]))) >= M
=============================================================================
