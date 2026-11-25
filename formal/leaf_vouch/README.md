# `formal/leaf_vouch` — the MLS leaf vouch and its life

**The point.** A room's MLS messages are signed by a leaf key that lives in the transport's memory, not in
the keyring. The member's device key signs one row that vouches for that leaf key, for one room, for at most
thirty days. This package runs that rule against a thief who copies a leaf key out of memory, and says how
long the copy is good for and what it cannot do.

Everything here is an enumeration over a stated bound. Nothing here is a proof.

## The rule as modelled

The home of the rule is [CC 5.1](../../constitution/part_5_transport_substrate.md#5.1), "People, not
infrastructure, join a room". The sentences below are the rule this package models. Where the text of CC 5.1
reads otherwise is listed under [Where the text differs](#where-the-text-differs).

| # | Sentence | In the model |
|---|---|---|
| R1 | A member's device key signs one vouching row for a separate Ed25519 leaf key. The device key is a person's roster key, an agent's key, or in a private room the room key. It is never a node key. | `door_leaf`: `signer`, `kind` |
| R2 | The row binds the leaf key, the room (its group id), the suite, a start, and a required end at most 30 days later. | `cap`, `entry_key`, `entry_room`, `entry_suite`, `covers` |
| R3 | The row carries 1, 8 or 32 salted digests. A presentation discloses exactly one entry [leaf key, room, suite]. | `digest_count`, `one`, `digest_match` |
| R4 | A door accepts a leaf only if its credential's vouch is present, signed by the member's device key, covers now, and names this room and this leaf key. | `door_leaf` as a whole |
| R5 | A renewal installs a fresh leaf key by one Update signed by the old leaf key, whose new LeafNode carries the new key and its vouch. | the device in part 2; `pop` |
| R6 | A lapsed leaf's signature is accepted on exactly an Update that replaces it. Its other messages are refused. Members may remove a leaf that stays lapsed. | `door_msg`, `door_remove` |
| R7 | The room's vouch covers that room's chat group and its call groups, whose ids a door recomputes from the room's id. | `room_of`, `bind` |
| R8 | A withdrawal ends a vouch at once. | `withdrawal` |

## The model

`leaf_vouch.py` holds two things that share no code path. The **door** (`door_leaf`, `door_msg`, `door_remove`)
decides from what is presented: a row with its digests, the disclosures, the LeafNode, the group's id, the
room's roster. It runs under a rule, a table of switches. **What was signed** (`intended`, `sem_state`) reads
the row's entries and the roster directly, and no switch reaches it. A signature is a field, a digest is a
tuple and a salt is a name. The two sides do share three constants: the cap, the digest counts and the list of
member key kinds. `check_leaf_vouch.py` writes the last two out a second time and fails if they differ. The
cap is the bound.

`check_leaf_vouch.py` runs three parts.

1. **The door.** Twenty-one rows (well formed, not padded, over the cap, without an end, withdrawn, for another
   suite, badly signed, signed by an agent's key, a room key, a node key owner-bound to the member, a node key
   a roster seats, a seated key of no member kind, a leaf key, the thief's key) presented at eight groups (the chat group and a call group of
   rooms A, B and the private room C, and a call group of A and of B under a random id) with zero, one or two
   disclosures or a made-up one, under each key named and one other, signed by its own key or not, as each of
   seven identities, at five instants: 85,680 presentations, 38 accepted.
2. **The life of a leaf.** Every interleaving, up to the horizon, of: the honest device P signing a vouch,
   joining the chat group and a call group of room A, renewing by Update, withdrawing a vouch, going offline
   until after its vouch has ended and coming back; the other members removing a lapsed leaf and adding P
   again; time; and one thief. The thief copies one leaf key out of P's memory at any step, and with it P's
   node key. It also holds a leaf key of its own, its own device key (seated in room B) and its own node key,
   and it reads every row and every disclosure P ever made. At every state it offers every LeafNode it can put
   together, as an Add at each of six groups and as an Update from every leaf that carries the copied key, and
   every kind of message from those leaves. An honest member is taken to commit any LeafNode the door accepts.
3. **Padding.** A row for 1 to 32 rooms, and what a room's door sees of the count.

**The bound.** The term cap is 2 ticks, so a tick is 15 days and half term is one tick. The horizon is 5
ticks: two terms and a tick. P signs at most 3 vouching rows and renews no earlier than half term. At most one
withdrawn row is in play at a time. There are two rooms in part 2 and three in part 1, one honest device, one
thief and one lift. A row that has ended or was withdrawn, sits in no tree, is not the device's newest, and
names a leaf key the thief does not hold is forgotten: the thief presents it no more.

| Run | States | Result |
|---|---|---|
| the rule | 183,107 | no property is violated |
| the rule, a device that also signs a shorter term (one tick) | 540,501 | no property is violated |
| the rule, where a leaf whose vouch was withdrawn signs no Update | 182,482 | no property is violated |
| the rule, a device that signs vouches over the cap or with no end | 510,577 | no property is violated: each such vouch is refused |
| the rule, a thief who is also a member of room A | 186,003 | no property is violated as the properties are stated below; see finding 9 |
| the same thief, where an Update must keep the identity of the leaf it replaces | 183,107 | no property is violated |

**The bound raised by one, run once by hand.** These runs are not part of the check command. Under the rule
with the first device: horizon 6 gave 336,304 states, and horizon 6 with 4 vouching rows gave 748,353. With
the device that also signs a shorter term, 4 vouching rows at horizon 5 gave 1,155,536. No property was
violated in any of the three. A cap of 3 ticks at horizon 7, so a tick of 10 days and a renewal from one tick
in, gave 773,016 states under the rule with the first device, and no property was violated. Each of these was
one run of part 2 under the rule, with no plant.

## Properties

Each property is checked in every run that has the part it is stated over: parts 1 and 3 run once, under the
rule, and part 2 runs in every row of the table above. Under each property the check prints the count of
cases that reach its premise in the first run, and a count of zero fails the run.

| Id | Statement | Rule |
|---|---|---|
| P1 `TERM` | From one term after the lift, no door accepts the copied key as a leaf, and no door accepts an application message, a proposal or a commit it signed. This holds whether or not the honest device renews. It is stated for a device that makes a leaf key and signs its vouch in one step, the vouch starting then (finding 8), and for a thief who is seated in no room where it holds a copied leaf (finding 9). | R2, R5 |
| P2 `RENEW` | The thief installs no leaf except the copied key itself, under a vouch that existed at the lift. It has no device key, so it cannot renew. | R1, R4, R5 |
| P3 `ROOM` | A vouch for room A is accepted in no group of room B: the chat group, a call group, a call group under a random id. | R2, R7 |
| P4 `ONE` | A presentation that discloses no entry, or two, is refused. | R3 |
| P5 `LAPSED` | A leaf whose vouch is not in force has its signature accepted on nothing but the Update that replaces it. | R6 |
| P6 `REJOIN` | A device whose leaf lapsed, and which signs a fresh vouch, replaces its leaf by its own Update. The door's decision on that Update reads the old leaf's signature, the new LeafNode and the vouch, and no act of another member. Whether MLS needs another member's commit to carry it is not modelled. | R5, R6 |
| P7 `NODE` | No leaf is accepted under a vouch a node key signed: a node key owner-bound to the member, or a node key a roster seats. | R1 |
| S1 `SOUND` | The door accepts a leaf only where the device key the roster seats for that member, a person's, an agent's or a room key, signed an entry for this leaf key, this room and this suite, in force now. | R1, R4 |
| S2 `COMPLETE` | The door refuses no such leaf when it is well presented. | R4 |
| S3 `CALLS` | A vouch accepted in the room's chat group is accepted in the room's call groups. | R7 |
| S4 `WITHDRAWN` | A withdrawn vouch admits no leaf and no message from the step it is withdrawn. | R8 |
| S5 `POSSESS` | A leaf enters only signed by the leaf key it carries. | R5 |
| S6 `DIGESTS` | A row of other than 1, 8 or 32 digests is refused. | R3 |
| S7 `SUITE` | An entry for another suite is refused. | R2 |
| S8 `REMOVE` | Only a leaf whose vouch ended or was withdrawn is removed as lapsed. | R6 |
| S9 `PADDING` | A room's door learns the count of the device's rooms only as one, up to 8, or up to 32. | R3 |

## Plants

Each plant changes the rule or the device and must break the property named. A plant's search of part 2 stops
at the first state that breaks that property. `leaf_vouch_expected.tsv` holds what broke, and a run that
differs from it fails.

| Plant | Must break |
|---|---|
| **a renewal signs a new vouch for the leaf key already in the tree** (the design not taken) | P1 |
| the same, with a door that refuses an Update keeping the leaf key under a new vouch | P1 |
| the door takes a vouch with no end or over the cap, and a device signs one | P1 |
| the door does not compare now with the end | P1 |
| the door takes a vouch on the instant of its end | P1 |
| a device, not a door: it signs a vouch that starts a tick later, the leaf key already made | P1 |
| a renewal's vouch may be signed by the leaf key it replaces, a leaf key taken as a member's kind of key | P2 |
| the vouch's signer is not compared with the member's seated key | P2 |
| the vouch's signer is any key the room seats, for whichever member | S1 |
| the row's signature is not checked | P2 |
| the disclosed entry's leaf key is not compared with the LeafNode's | P2 |
| a disclosure's salted digest is not looked up in the row | P2 |
| the disclosed entry's room is not compared with the group's room | P3 |
| the door takes a group's room on the group's word | P3 |
| two disclosures are accepted when one of them fits | P4 |
| no disclosure is needed | P4 |
| a lapsed leaf's application messages are taken | P5 |
| a lapsed leaf's proposals and commits are taken | P5 |
| a lapsed leaf's replacing Update is refused with its other messages | P6 |
| a node key owner-bound to the member may sign the vouch | P7 |
| a key a roster seats may vouch whatever kind of key it is | P7 |
| an entry for another suite is accepted | S7 |
| a row of 2 or 33 digests is accepted | S6 |
| the door does not read a withdrawal | S4 |
| the LeafNode's own signature is not checked against its leaf key | S5 |
| on an Update the new LeafNode may be signed by the leaf key it replaces | S5 |
| the door refuses a vouch whose end is sooner than the cap | S2 |
| the vouch is good in the room's chat group only | S3 |
| a live leaf may be removed as lapsed | S8 |
| the row carries as many digests as it has entries | S9 |

**The design not taken, as a trace.** P's device key signs vouch 0 for leaf key 0, from tick 0 to tick 2. The
thief copies leaf key 0 at tick 0. At tick 2 the device renews by signing vouch 1 for the same leaf key 0,
from tick 2 to tick 4. The thief presents leaf key 0 under vouch 1 and the door accepts it, one full term
after the lift. Every further renewal extends the copy. With a fresh key per vouch the copy ends with vouch 0.

## Witnesses

Each is reached under the rule, and `--traces` prints the steps.

- A leaf is accepted under a person's roster key, an agent's key and a room key; with 1, 8 and 32 digests; at a
  call group; with a shorter term.
- The device joins the chat group. The same leaf and vouch join a call group. A call group under a random id
  is refused.
- A renewal installs a fresh leaf key by one Update. A renewal takes a shorter term.
- A lapsed leaf's application message is refused. The device goes offline, its vouch ends, it comes back and
  replaces its leaf by its own Update.
- The members remove a leaf that stays lapsed. A live leaf is not removed as lapsed. After a removal the device
  comes back by another member's Add.
- The thief copies a leaf key. The copied key is accepted while its vouch runs, and on the last tick of the
  term. It is refused once its vouch has ended, and the thief's Update from the lapsed leaf is refused.
- The thief updates the leaf in place while its vouch runs.
- Beside the device's newer leaf, the copied key is added again under its old vouch.
- A withdrawn vouch refuses the copied key before its end.
- A vouch over the cap is refused. A vouch without an end is refused.
- The thief vouches the copied key as its own leaf in its own room. Nothing of P follows from that.
- Each of the seventeen refusal reasons of the door is the first reason of some presentation.
- Where the thief is a member of room A: a copied key whose vouch has ended signs an Update that installs the
  thief's own leaf. Where an Update must keep the identity of the leaf it replaces, this is absent.

## What the runs show beyond the properties

1. **A fresh key per vouch is the device's duty, and a door cannot hold it to that.** A door that refuses an
   Update keeping the leaf key under a new vouch does not restore P1. The copied key comes back by an Add
   under the new vouch, and a door at an Add has no earlier leaf to compare with. P1 is shown for a device that
   never signs a second vouch for a leaf key. The device that signs one breaks it.
2. **A renewal does not end the old vouch.** After the device has renewed, the copied key is accepted again by
   an Add under the old vouch until that vouch's own end. Only a withdrawal ends it sooner. Renewing at half
   term does not shorten the time a copy is good for.
3. **The bound is the whole term in the worst case.** A key copied on the tick its vouch starts is accepted
   until the last tick of that term.
4. **The node key is in the same memory as the leaf key.** The thief holds both. It gains nothing from the
   node key only while the door asks for the seated key and refuses a node key. Under the reading "the member's
   device is the node it runs on" the thief signs its own next vouch.
5. **A row of one digest says there is one room.** Every member of that room learns that the device has no
   other room under that row. The counts a door can tell apart are three: 1, 8 and 32.
6. **One row in several rooms is the same bytes in each.** Whoever sits in two of them can match the row. Under
   a roster key the signer already says as much. A room key signs for its own room alone.
7. **After a removal the Update is gone.** A device whose lapsed leaf was removed comes back only by another
   member's Add.
8. **The term runs from the vouch's start, and the copy from the key's making.** A leaf key exists before its
   vouch is signed. A device that signs a vouch starting one tick later, with the leaf key already in memory,
   gives a copy taken at signing one tick more than the term. No door can tell: the row is well formed and
   within the cap. The rule sentences R1 to R8 put no duty on the device here. P1 as stated needs one: the
   vouch starts no later than the device makes the leaf key.
9. **A copied key whose vouch has ended still signs one thing, and R6 says so.** Where the thief is itself a
   member of the room, the copied key signs an Update whose new LeafNode is the thief's own leaf, under the
   thief's own vouch, and every door takes it: 270,934 such Updates a term or more after the lift in that run.
   The thief gains no leaf it could not have had added as itself, and loses the honest member a leaf the
   members could have removed. It is still an accepted signature of the copied key with no end in time. A door
   that requires an Update to keep the identity of the leaf it replaces refuses every one of them and changes
   no other result. R5 and R6 do not say which. The model runs both and decides neither.
10. **"Never a node key" is not the whole of R1.** A door that refuses only a node key takes a vouch from any
    other key a roster seats. The door here asks for one of the three kinds R1 names.

## What is assumed and not checked

- No signature is forged and no two disclosures share a digest.
- A padding digest cannot be told from an entry's digest.
- The door holds a withdrawal from the step it is signed, and every door reads one clock.
- The roster is fixed: nobody is seated or unseated during a run.
- The thief holds the group's secrets, so every message it can sign is offered.
- The device erases a leaf key once its leaf is replaced, and the thief lifts once.
- The device makes a leaf key and signs its vouch in one step, and the vouch starts on that tick. The time
  between the two is not modelled.
- The thief copies one leaf key, the one for room A. The device's leaf key for room B is in the same memory
  and is not copied.
- A vouch is in force for `start <= now < end`.
- A leaf whose vouch was withdrawn is treated as ended: it may be removed as lapsed. Whether it still signs its
  replacing Update is run both ways, and no property differs.

## What is not modelled

- The cryptography: Ed25519, the composite signature of the device key, the salted digests, HPKE, the suite.
- MLS itself: epochs, the tree, path secrets, commits and their order, external commits, KeyPackages and their
  lifetimes. What an accepted commit from the thief does to the tree is not modelled; only that it is accepted.
- The bytes of the vouching row, its family and its refusal tokens. The reason names in `leaf_vouch.py` are
  this model's own.
- The bytes of a call group's id. The model has an id a door can recompute the room from and an id it cannot.
- A member with two devices, a second lift, and a thief who stays on the device.
- A device that makes a new leaf key each time it joins again. After a removal the device here comes back under
  the vouch and key it has.
- Whether a room is private. The door takes whichever key the room's roster seats, of the three kinds; that a
  private room's roster seats room keys only is the roster's rule and is not checked here.
- The honest device's leaves in room B over time. Room B is a target for the thief and for the door cases.
- The end of a seat: a removal from the room, a revoked occurrence, a superseded device key.
- The spread of a withdrawal, and two doors that hold different rows.
- Custody classes and how many times a person is asked to touch a key.
- A private room's binding of a room key to a person.
- How long "stays lapsed" is. The members may remove from the first step after the end.
- The limit that authentication of MLS messages is classical under this suite.

## Where the text differs

- CC 5.1 states R1 to R6 and R8: a separate leaf key, the device key's vouching row, its term, the renewal,
  the lapse and the withdrawal. A KeyPackage is signed by its leaf's key and is accepted only with a live vouch.
- CC 5.1 gives a leaf five ends: replaced, removed, lapsed and withdrawn, the removal on a revoked occurrence
  or an ended seat. The model runs the lapse and the withdrawal, and does not model the other three.
- CC 5.1 names the door's six refusals. The model gives a refusal a reason of its own and does not carry those names.
- A call group's id is derived from the room's id at CC 2.6.1.11 (R7).

## Run

```
python3 -I formal/leaf_vouch/check_leaf_vouch.py            # two to three minutes, three workers each under 2 GiB, exit 0 or 1
python3 -I formal/leaf_vouch/check_leaf_vouch.py --traces   # the same, with the steps to each witness and break
```

Python 3, standard library only.
