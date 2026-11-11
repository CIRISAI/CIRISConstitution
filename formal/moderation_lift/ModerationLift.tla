--------------------------- MODULE ModerationLift ---------------------------
(* The members' check on a moderator's act (CC 4.5.13).

   One moderator's signature takes effect at once. The members may lift it: a strict majority
   of the roster AS IT STOOD AT THE INSTANT OF THE ACT, objecting inside the window, with a
   floor of two voices. A lifted item returns consent-gated and never to plain view. An act on
   an immediate-removal basis, or a ruling on a privately filed report, is not objectable. The
   moderator whose act was lifted does not take it again on the same item.

   Count = "at_act": the rule of the text.
   Count = "live":   the contrast. The count is taken over whoever is in the room when the
     objections are counted, so people who join after the act can carry the lift
     (Inv_SeatedMajority fails).

   Three members seated at the start, two of them moderators; two people who may join later;
   one item. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Members, Late, Mods, Count
ASSUME Mods \subseteq Members /\ Members \cap Late = {}

None == "none"
VARIABLES roster,      \* who is in the room now
          item,        \* "visible" | "withheld" | "gated"
          actor,       \* the moderator whose act is in force, or None
          basis,       \* "ordinary" | "immediate" | "private"   (of the act in force)
          atAct,       \* the roster as it stood at the instant of the act
          objections,  \* members who signed objection:raised naming the act
          open,        \* the window is open
          lifted,      \* moderators whose act on this item was lifted
          everActed,
          lastLift     \* a record of the last lift: <<objectors, roster at the act, basis>>
vars == <<roster, item, actor, basis, atAct, objections, open, lifted, everActed, lastLift>>

Init == /\ roster = Members /\ item = "visible" /\ actor = None /\ basis = "ordinary"
        /\ atAct = {} /\ objections = {} /\ open = FALSE /\ lifted = {} /\ everActed = FALSE
        /\ lastLift = <<{}, {}, "none">>

Join(n) == /\ n \in Late /\ n \notin roster /\ roster' = roster \cup {n}
           /\ UNCHANGED <<item, actor, basis, atAct, objections, open, lifted, everActed, lastLift>>

\* a moderator acts alone, at once; never again on this item once their act was lifted
Act(m, b) == /\ m \in Mods /\ actor = None /\ m \notin lifted
             /\ actor' = m /\ basis' = b /\ item' = "withheld"
             /\ atAct' = roster /\ objections' = {} /\ open' = TRUE /\ everActed' = TRUE
             /\ UNCHANGED <<roster, lifted, lastLift>>

\* anyone in the room may sign an objection while the window is open; the count decides who is heard
Object(n) == /\ actor # None /\ open /\ n \in roster /\ n \notin objections
             /\ objections' = objections \cup {n}
             /\ UNCHANGED <<roster, item, actor, basis, atAct, open, lifted, everActed, lastLift>>

Heard == IF Count = "at_act" THEN objections \cap atAct ELSE objections
Base  == IF Count = "at_act" THEN atAct ELSE roster
Carries == /\ Cardinality(Heard) * 2 > Cardinality(Base)
           /\ Cardinality(Heard) >= 2

Lift == /\ actor # None /\ open /\ basis = "ordinary" /\ Carries
        /\ item' = "gated" /\ lifted' = lifted \cup {actor}
        /\ lastLift' = <<objections, atAct, basis>>
        /\ actor' = None /\ open' = FALSE /\ objections' = {}
        /\ UNCHANGED <<roster, basis, atAct, everActed>>

Close == /\ actor # None /\ open /\ open' = FALSE
         /\ UNCHANGED <<roster, item, actor, basis, atAct, objections, lifted, everActed, lastLift>>

Next == \/ \E n \in Late : Join(n)
        \/ \E m \in Mods, b \in {"ordinary", "immediate", "private"} : Act(m, b)
        \/ \E n \in Members \cup Late : Object(n)
        \/ Lift \/ Close
Spec == Init /\ [][Next]_vars

(* ---- properties ---------------------------------------------------------------------- *)
\* M1 A lift was carried by a strict majority of those seated when the moderator acted.
Inv_SeatedMajority ==
  lastLift[3] # "none" =>
    Cardinality(lastLift[1] \cap lastLift[2]) * 2 > Cardinality(lastLift[2])
\* M2 Never one voice.
Inv_TwoVoices == lastLift[3] # "none" => Cardinality(lastLift[1] \cap lastLift[2]) >= 2
\* M3 Only an ordinary act is lifted: an immediate-removal basis and a private-report ruling stand.
Inv_Untouchable == lastLift[3] \in {"none", "ordinary"}
\* M4 Once a moderator has acted on an item it never returns to plain view by a lift.
Inv_NeverPlain == everActed => item \in {"withheld", "gated"}
\* M5 No second bite: the moderator whose act was lifted is never the actor again on this item.
Inv_NoSecondBite == actor # None => actor \notin lifted
\* M6 An act not lifted inside its window stands.
Inv_StandsAfterWindow == (actor # None /\ ~open) => item = "withheld"
\* M7 The act takes effect at once: while an act is in force the item is withheld.
Inv_AtOnce == actor # None => item = "withheld"
=============================================================================
