# `formal/moderation_lift` — the members' check on a moderator's act

**The rule (CC 4.5.13).** One moderator's signature takes effect at once, and the members may
lift it: a strict majority of the roster at the head the act names, objecting
inside the 48-hour window, with a floor of two voices. A lifted item returns consent-gated and
never to plain view. An act on an immediate-removal basis and a ruling on a privately filed
report are not objectable. The moderator whose act was lifted does not take it again on the
same item. The shape is the accord's at room scope: one acts, a majority may undo
(`formal/accord_halt`).

**The model** (`ModerationLift.tla`). Three members seated at the start, two of them
moderators, two people who may join later, one item.

| Config | Result |
|---|---|
| `ModerationLift_at_act.cfg` | every property holds (41,050 states): a lift was carried by a strict majority of those seated when the moderator acted (`Inv_SeatedMajority`) and never by one voice (`Inv_TwoVoices`); only an ordinary act is lifted (`Inv_Untouchable`); once a moderator has acted, the item never returns to plain view (`Inv_NeverPlain`); the moderator whose act was lifted is never the actor again on the item (`Inv_NoSecondBite`); an act not lifted inside its window stands (`Inv_StandsAfterWindow`); the act is in force from the step it is taken (`Inv_AtOnce`) |
| `ModerationLift_live_brigade.cfg` | the contrast, the count taken over whoever is in the room when the objections are counted: `Inv_SeatedMajority` violated. Two people join after the act and carry the lift with one member |

**What it does not model.** The recall of an elected moderator (a cosigned row at more than two
thirds, then the election of `formal/moderator_election`); the founder's seat, which the text
leaves open; a second holder of the duty acting on the item after a lift, beyond its being
allowed; the clock of the window (each node's own, from first holding the act).

Run: `java -cp tla2tools.jar tlc2.TLC -workers auto -metadir /tmp/tlc -deadlock -config ModerationLift_<cfg>.cfg ModerationLift.tla` (TLA+ tools 1.7.4; seconds).
