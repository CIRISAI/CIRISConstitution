# `formal/join_audience`: who holds what when people join a room with unannounced devices

This model asks one question of the join rules and the allow list: after each step, which node holds which row. It uses the words of [`audience_view`](../audience_view/): a node's **view** is the rows it holds, a row has an **audience**, a row is **served** to a node only inside that audience, and a **stranger** is a node whose owner the server cannot resolve. That model states what a view decides and hides. This one adds the steps that move rows, and runs them in every order over small worlds.

The run is a breadth-first enumeration in Python over a stated bound. It is not a proof.

## The rules modelled

| Rule | Where |
|---|---|
| An owner-binding is first written at the scope its owner first places the node at, `self` or `federation`, and is re-signed per group. The re-signed row stands beside the first. | CC 3.2 "Where the row is placed" |
| A person's own occurrences are placed wherever a binding of any node that person owns is placed. A seat in a room places no device there. | CC 5.4.6 "An occurrence follows its bindings" |
| A binding placed at `self`, a family or a room is no allegiance row. It crosses no link by virtue of the link. | CC 5.3.4, text not yet merged |
| An invitation is a sealed envelope carrying the membership proposal and the inviter's occurrences, and nothing of the roster. | CC 3.1.3.2, text not yet merged |
| Its answer is a sealed envelope carrying the acceptance, the joiner's occurrences and the joiner's binding re-signed at the room. | CC 3.1.3.2, text not yet merged |
| Once the widening seats the joiner, the cohort's ordinary delivery serves it the roster, the occurrences and the bindings placed at the room. | CC 3.1.3.2, text not yet merged |
| A row placed at a room is served to a node only when that node is in the room's audience, resolved through its owner's binding held by the server. | CC 5.2, CC 6.1.5.3, CC 3.1.3.3 rule 2 |
| A person with no announced node is invited only after a contact has been exchanged. | CC 3.1.3.2, text not yet merged; CC 5.4.6 |
| An allow list is the `cohorts` member of the owner's `consent:replication` grant naming one key. A device's list is stated for each key it holds: the node key's list withholds the bytes and the roster key's list withholds the wrap. | CC 6.1.5.3 "The class and the allow list", text not yet merged; CC 3.3.7 |
| An author whose own device is kept off is refused the write. | the rule as given to this model; CC 5.2 states a narrower one (see the findings) |

"Text not yet merged" is the branch `worktree-agent-aaf753d79a81aafcc`, read at `ea45fb2`. The other sentences are in the Parts at `37fd253`.

### Where the model's rule is narrower than the text

These are choices of the model, not of the text. Each is a field of `Rules`, and the other value is run as a reading.

- **One re-signing, inside the answer.** CC 3.2 lets the owner re-sign the binding of each node that joins. By default the model re-signs only the answering device's binding, and only in the answer. `late_place` lets the owner re-sign another device's binding after the acceptance (G09, G10).
- **An announced joiner re-signs all the same.** CC 3.2 asks for the row at the room "when an unannounced node joins". By default the model re-signs whether or not the joiner is announced. `resign=unannounced` follows the words (G12).
- **Which bindings resolve a room's audience.** By default only a binding placed at the room, at federation, or the server's own sibling binding at `self`. CC 3.2 says `owner_of` folds every live binding of the key, which is the reading `resolve=any` (R02, G06 to G08).
- **The owner's own sealer holds every sibling's list.** CC 6.1.5.3 constraint (1) holds the policy at `self`; constraint (3) says a node receives only its own allow list. The default follows (1). `self_lists=own` follows (3) (G11).
- **The node key's list is read by the receiver alone.** CC 6.1.5.3 says the choice is enforced at both ends. No sender in the model reads a node key's list unless the reading `node_list_reach=audience` is set, so the bytes are offered and declined.
- **Delivery is fair.** Property 1 is read only on states where nothing more can move, so a relay that never delivers an envelope is not run.

## The bound

One room seated by identity keys. Two or three people, one or two devices each, one stranger relay. One write sealed under the room's content key. Each device's two lists are fixed before the run. A federation-placed row is held by every node from the instant it exists. An envelope is opened whole. A contact exchange is one step. Every other delivery moves one row, and every order of the enabled steps is run, except in the five cases marked `grain=batch` (R05, G02, G03, G04, G10), where one delivery moves every row the receiver may be served. Four of them are the world with four devices, which is too large for one row per delivery; G04 is a three-device world.

A batch case runs fewer orders and can hide a break that depends on the order of two rows. Finding F05 is such a break: it is reached at one row per delivery (64,149 states) and is not reached in the same world run in batches (137 states, run once by hand). So a batch case that breaks nothing says less than a row case that breaks nothing.

The largest case has 82,544 states. The whole check visits 873,383 states in about four minutes under a 2 GiB cap.

Larger worlds were run once and are not part of the check, because each takes minutes: three people with one write by the first joiner (545,032 states), by the founder (295,064), and in a room where one member invited two (598,352); the same room with a joiner who may announce (240,804); a joiner with three devices and a four-device chain of three people, both in batches. These runs were made before `N.wrap` and `L.member` were added, so they speak for the other sixteen names only. None broke one of them beyond the breaks recorded here.

## The properties

Each of the four properties is read under several names, so a break says what broke.

| Property | Names | Read on |
|---|---|---|
| 1. No deadlock: after invitation, answer and widening, every device of a seated person can be served the room's rows | `N.join` (every invited person is seated), `N.placed` (a device with a binding at the room), `N.unplaced` (a device with none), `N.wrap` (a person the sealer itself read as seated gets a wrap on every device no list keeps off) | `N.join`, `N.placed` and `N.unplaced` on every state where nothing more can move; `N.wrap` on every state |
| 2. No disclosure: no node outside the room's audience and no relay holds a room-placed binding, an occurrence of an unannounced person, or the roster; the invitee holds nothing of the roster before it is seated | `D.relay`, `D.room_binding`, `D.self_binding`, `D.contact_binding`, `D.occurrence`, `D.occurrence_literal`, `D.roster`, `D.content`, `D.invited_unannounced` | every state |
| 3. The allow list: a device holds no bytes its node key's list leaves out and no wrap its roster key's list leaves out, and no sealer wraps to a key whose list leaves the room out, or to a key of a person with no seat | `L.bytes`, `L.wrap`, `L.sealer`, `L.member` | every state |
| 4. Announcing later changes nothing a room member holds of the room | `A.announce` | the states where nothing more can move, with the announce and without |

`D.occurrence` lets four kinds of node hold an unannounced person's occurrence: that person's own devices, a contact's, a seated member's once the person is placed at the room, and the invitee the person wrote to. `D.occurrence_literal` leaves the invitee out. The property as the task words it leaves the contact out as well, and the rules themselves give a contact the occurrence (CC 5.4.6), so that wording is not checked.

`N.placed` and `N.unplaced` ask that a device hold the row of wraps. They do not ask that the row carry a wrap to that device: that is `N.wrap`, and it breaks under the rules as given (finding 8).

`D.room_binding` and `D.roster` count every device of a seated person as inside the room's audience, a device its node key's list keeps off among them. `D.occurrence` lets a seated member hold a joiner's occurrence from the moment the joiner's binding is placed at the room, which is before the joiner is seated.

`A.announce` compares, for the devices of seated people, every row but the federation-placed and `self`-placed bindings. It compares the states where nothing more can move, not the states on the way. It is run in four worlds: two people (R10, R11), three people one device each (R12), and an inviter with two devices (R15). No world with a list or with two devices on the joiner is run for it.

## The witnesses

Each is a state the run reaches, checked by name in the case that lists it.

- The invitee holds the proposal and the inviter's occurrence, and nothing of the roster.
- The relay carries both envelopes and holds no row.
- The joiner is seated and holds the roster and the inviter's binding at the room.
- The joiner's device holds the bytes and a wrap.
- A device with no binding at the room holds the roster, served by its sibling.
- A and C, never contacts, each hold the other's binding at the room.
- C, a contact of B outside the room, holds B's binding addressed to it and B's occurrence.
- **The stated consequence:** with only the node key's list set, B2 holds a wrap and no bytes.
- With only the roster key's list set, B2 holds the bytes and no wrap.
- With both set, B2 sits in the room and holds neither.
- The sealer read B as seated, no wrap names a key of B, and no device of B holds the bytes: the member reads absent.
- The write is refused.
- An announce after the last seat is among the orders run.
- The deadlock persist found: A1 lacks B1's binding, B1 lacks the roster, and nothing more can move. It is reached only under the plant.
- Never reached: an invitation to an unannounced person with no contact exchanged.
- B and C, two joiners invited by the same member and never contacts, each hold the other's binding at the room (R13).
- The last joiner's sealer wraps to A1, a member its owner never exchanged a contact with (R14).
- The deadlock between two joiners: both seated, neither holds the roster, the inviter holds no binding of either. It is reached only under the plant (P17).

The link rule changes no state when it holds, so its premise is counted: 336 links in case R01 leave a binding not placed at federation behind.

## The planted breaks

| Plant | The rule changed | Caught by |
|---|---|---|
| P01 | the answer carries no binding | `N.placed`, with the deadlock reached as a witness |
| P02 | the invitation carries the roster | `D.roster` |
| P03 | a link hands the peer every binding of the node | `D.relay`, `D.room_binding`, `D.self_binding`, `D.contact_binding` |
| P04 | an occurrence is a public row whatever its bindings | `D.relay`, `D.occurrence`, `D.occurrence_literal`, `D.invited_unannounced` |
| P05 | a room row is served on the binding alone, before the seat | `D.room_binding`, `D.roster` |
| P06 | a room row is served on the node's own word of its owner | `D.relay`, `D.room_binding`, `D.occurrence`, `D.occurrence_literal`, `D.roster`, `D.content` |
| P07 | the node key's list is read at neither end | `L.bytes` |
| P08 | the roster key's list is read at neither end | `L.wrap`, `L.sealer` |
| P09 | a write is refused only when its author has no wrap target at all | `L.bytes` (and `N.wrap`, which is finding 8's break and not the plant's) |
| P10 | a binding re-signed at federation replaces the row placed at the room | `A.announce`, `N.placed` |
| P11 | a row addressed to a contact is served to anyone once its owner announces | `D.contact_binding`, `D.relay` |
| P12 | a wrap is made unless a held projection withholds it | `L.sealer` |
| P13 | the invitation carries the inviter's binding placed at the room | `D.room_binding` |
| P14 | the answer is sealed to every foreign occurrence the joiner holds, so a contact outside the room opens it | `D.room_binding` |
| P15 | a sealer wraps to every occurrence it holds, seated or not | `L.member` |
| P16 | a contact exchange hands over every binding of the device | `D.room_binding`, `D.self_binding`, `D.contact_binding` |
| P17 | the answer carries no binding, in a room where one member invited two | `N.placed`, with the deadlock between the two joiners reached as a witness |

Every one of the 18 names breaks in at least one case. `N.join`, `N.unplaced` and `N.wrap` break only in a reading or a finding, not in a plant.

Other changes were tried once by hand and each was caught: the relay opening the envelopes it carries (`D.relay`, `D.room_binding`, `D.occurrence`); an occurrence placed at the room served to any node the server holds a binding of (`D.occurrence`, in the world with a contact outside the room); a link handing over the node's occurrence (`D.relay`, `D.occurrence`, `D.invited_unannounced`); the answer's binding re-signed at federation (`D.relay`, `D.occurrence`); a room-placed binding served to anyone once its owner announces (`D.relay`, `D.room_binding`); the `self` plane served to a contact (`D.self_binding`); the joiner seating itself (`N.placed`). The last is caught only because the seat it makes never reaches the inviter. The count behind a widening is not modelled, so no property here says who may seat whom.

## What the model found

These are the places where the rules as given do not close. The model changes no rule to pass. Each is a case of the check, which fails if the break stops.

1. **The deadlock needs a reading the text speaks against.** The rule says the audience is resolved through the owner's binding the server holds. The join rules do not say which placements count. CC 3.2 does say that `owner_of` folds every live binding of the key, so ownership never depends on announcement or on any re-signing, and a binding addressed to the server as a contact is a live binding. If only a binding placed at the room, at federation, or the server's own sibling binding at `self` counts, the plant deadlocks and the answer's binding closes it (P01, P17, R01, R13). If a binding addressed to the server as a contact counts too, as CC 3.2 reads, there is no deadlock in any world run, with no binding in the answer at all (G06, G07, G08): the contact exchange has already carried a binding, and the binding re-signed at the room reaches the other members by ordinary delivery. Every other case uses the stricter reading. So the model reproduces the deadlock only under the stricter reading, and it does not show that the answer's binding is what prevents it under CC 3.2's.
2. **"The joiner's owner-binding" is one binding, and a joiner may have two devices.** The answer carries the binding of the device that answers. The other device is served only by its sibling, through the binding held at `self` (R04, R05). If a sibling's `self` binding does not resolve a room's audience, the other device is stranded (G02). Carrying a binding for each device closes it (G03). So does the owner re-signing the other device's binding at the room after the acceptance, which CC 3.2 already allows: it reaches its sibling on the `self` plane and the members from there (G10). The break is of the default model, where the owner never does that.
3. **A joiner who answers on a device kept off the bytes strands its other device.** B2's node key's list leaves the room out and B answers on B2. B1 has no binding at the room, B2 is its only server, and B2 holds no bytes to serve. B1 never holds the bytes (F04). Carrying a binding for each device closes it (G04). So does the owner re-signing B1's binding at the room after the acceptance (G09). As in finding 2, the break is of the default model, where the owner never does that; the text does not say the owner must.
4. **An unannounced inviter writes to an announced person who is no contact.** The rule about contacts covers an unannounced invitee only. The invitation hands the inviter's occurrences to a node that is outside the room's audience and is no contact, and it keeps them if it never answers (F01, `D.occurrence_literal`). And the answer has no address: the invitee holds no binding and no route of the inviter. Read strictly, the join stalls (G01). The other cases assume the answer returns by the path the invitation came.
5. **No row tells the room of a roster key's list.** CC 6.1.5.3 constraint (2) says each cohort receives its own projection, which of that member's nodes are in its audience. The text gives that projection no row, no family and no reading when it is not held, and it speaks of nodes, not of the roster key's list. The list rides a grant placed at `self`. A sealer on another member's device holds every occurrence placed at the room and no list, so it wraps to the key the list leaves out (F02), and a member whose every device is kept off does not read absent (F03). The kept-off device declines the wrap by its own hold decision, so `L.wrap` holds; the wrap exists at the other members' nodes. The cases L02 to L05, kind `repair`, add a projection row of this model's making to show what closes it. They are not the rules as given. The projection must be read closed: no projection held, no wrap. Read open, the occurrence is served before the projection and the wrap is made (P12). The owner's own sealer needs the lists too. Under constraint (3) read by the letter, a node holds only its own list, and the owner's other device wraps to the key its sibling's list leaves out (G11).
6. **CC 5.2's refusal is narrower than the rule as given.** By the letter a write is refused when its author has no wrap target at all. An author with one device kept off and another not has a target, so the write is sealed, and the kept-off device then holds bytes it wrote (P09). The model's rule refuses the write when the writing device's node key's list or roster key's list leaves the room out. The second half of that is this model's reading.
7. **CC 6.1.5.3 says two things of a node the list leaves out.** "The owner's choice" says the node is not in the cohort's audience, receives no keys for the cohort and pulls nothing for it. "The class and the allow list" says the node key's list withholds the bytes. Under the first, the stated consequence is never reached: B2 holds no wrap (G05).
8. **A seated member can be left without a wrap for a write made after it was seated.** CC 5.2 has the sealer wrap over the roster and the occurrences it holds when it seals. The seat and the occurrence are two rows and arrive in either order. A1 seats B and serves its sibling A2 the seat; A2 writes before it is served B's occurrence; the write carries no wrap to B1, and nothing in the model makes one later (F05, `N.wrap`; R14 reaches the same break with the last joiner sealing). CC 5.2 names a later `key_grant` for `self` and `family` content only. The same world run in batches does not reach it.
9. **Property 4 holds for the rows a member holds only because the model re-signs at the room whether or not the joiner is announced.** CC 3.2 asks for the row "when an unannounced node joins". Read by those words, a joiner who announces before answering places no row at the room, and the members end holding one row fewer than if it had never announced: 4 outcomes against 2 (G12). Reach is the same either way, since the binding at federation resolves the node. An announce after the answer changes nothing under either reading.

## What is not modelled

- The count behind the widening. One seated member that holds the proposal and the acceptance seats the joiner in one step.
- A private room. Its seats are room keys and its join carries room-key rows and binding encapsulations (CC 3.1.3.2). This model is the carriage for a room seated by identity keys.
- Any cryptography. A sealed envelope is opaque to every node it is not sealed to, by assumption.
- Routes, relays' choice of path and the Anonymous Tier. What a network observer learns is outside the model.
- Removal, resignation, a declined invitation, a withdrawn binding, a revoked key and a second room.
- Editing a list after the join. The lists are fixed before the run, so narrowing and the descent of what a node already holds are not run.
- A wrap to a node's own key by ownership (CC 3.2 "`self` is one owner's keys"). Wraps go to roster keys only, so whether the node key's list governs a wrap to the node's own key is not answered here.
- The class default. A device with no list receives everything; a server node's default is not run.
- A wrap for content written before a member was seated.
- How a server ties a roster key to a node. The model names an occurrence by its device.
- Announcing one node of several. An announce places every node of the person at federation.
- An agent's occurrence and an owned agent's place in `self`.
- More than three people, more than two devices each (three were run once, in batches), more than one write, and one row per delivery in the four-device worlds.
- A later wrap. The wraps of the one write are one row fixed when it is sealed.
- A relay that withholds an envelope, and any node that departs from the rules. The disclosure properties are read on runs where every node follows them, and the plants change the rule for all nodes at once.

## Running

```
python3 -I formal/join_audience/check_join_audience.py
```

It exits 0 when every case gives the states, breaks and witnesses recorded in `join_audience_expected.tsv`. `--write` rewrites that file from a run. `--trace ID` prints one shortest run to each break of one case.
