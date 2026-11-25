# `formal/binding_carriage`: the binding of a private room, and its carriage before the seat

**The point.** A private room seats room keys, and the statement that a room key is a given person's is the
binding: three flows that nobody signs, made for one addressee. Three parties must hold a joiner's binding before
the joiner is seated: each cosigner, each founder at a founding, and the duty holder. Until now the binding was
taken as a given fact ([`causal_kernel/roomkey.py`](../causal_kernel/roomkey.py)), and nothing ran its flows or its
carriage. This model builds the binding from its terms and runs the carriage in every order of delivery within
the bounds printed.

Everything here is symbolic. A term is a nested tuple, and a party knows what it can derive from what it holds.
Nothing here is cryptography, and a run is a run over the stated bound and never a proof.

Run: `python3 -I formal/binding_carriage/check_binding_carriage.py` (about 40 seconds, under 400 MB, exit 0 when
everything holds, every planted break is caught and every finding is reproduced).

## The rule sentences modelled

| Sentence | Home |
|---|---|
| The seat row of a room key carries a commitment to its person, which the binding opens. The commitment is a hash over the room, the room key, the person and fresh random bytes. | CC 3.1.3.2, CC 2.6.1.11 |
| The binding is never a row, and nobody signs it. It is made for one addressee, which can check it and cannot prove it to anyone else. | CC 3.1.3.2 |
| The binding is a challenge that only the person's identity can open and a confirmation that the recipient could also have produced. A binding that does not open the commitment is refused. | CC 3.1.3.2 |
| A member's node does not cosign a widening until it holds the joiner's binding, nor one whose binding names a person already seated. | CC 3.1.3.2 |
| A widening in a room that seats a duty holder names that duty holder's acknowledgement of the joiner's binding and waits until it is held. | CC 4.5.4 |
| A count of persons is missing at a node until it holds the binding of every seated room key, and the node says which key it lacks. A withheld binding is a stall and never a fork. | CC 3.1.3.2 |
| The construction as accepted for typing: the claim, the challenge made to the person's binding key, and the confirmation as a seal to the addressee's room-key KEM key that is keyed by the challenge's secret and bound to the room, both room keys, the commitment and the binding key. One exchange for each room key, a fresh challenge each time. | not yet in the Parts |
| In a private room each listed member signs the founding record as a room key, and holds every other listed member's binding before signing. | CC 3.1.3, "Founding" |
| The flows ride sealed envelopes addressed to one room key: the invitation and its return, and the same envelope to each cosigner and to the duty holder. | not yet in the Parts |

## The model

`model.py` has eight sections. The terms are a public key, an encapsulation, a seal, a keyed seal, a hash, a
signature and an encoding. A party opens a seal only with the secret half of its key, and a keyed seal only with
the key as well. A sealed term shows the public key it was made to, since no anonymity of the key exchange is
assumed. `can_make` says whether a party can produce exactly a given term.

The construction is one function for each flow and one for the addressee's check. Every planted break is a switch
of the rule, so the text's rule and each break are read by the same code.

## What is checked, and over what bound

| | Property | Bound |
|---|---|---|
| 1 | **Authenticity inside.** The coalition holds every secret except P's binding key, P's roster key and the addressee's own, P's room keys and nonces included. Nothing it can put before the addressee makes it take a key to be P's that P did not prove to that addressee in that room: not a key P never held (forged), not P's key on an answer P made for someone else (misaddressed), and not a key P holds in another room (taken across rooms). Where the addressee reads the seat row P signed, it does not take P's key as a coalition person's (stolen). Where it reads a seat row the coalition signed for P's room key, it does: finding 3. | six sessions of one addressee, each on a named seat row; P holds one room key in each of two rooms and answers every challenge the coalition can form, to two addressee names and two KEM keys; 258 candidate confirmations |
| 2 | **Deniability outside.** Every term the addressee ends up holding follows from its own secrets and from what a holder of R's secret says. The same view, up to the fresh names, is made by the addressee and a party that is not P. The addressee can show that R's holder named P: the seat row needs R's secret, and the opening opens it. | one exchange, the addressee's whole view |
| 3 | **No signature without the binding.** In every reachable state, a cosign, an acknowledgement or a founder's signature stands on a binding its signer checked against its own live challenge, and the admission stands on all of them. | a widening (joiner, inviter, second cosigner, duty holder: 221,897 states, at most two lost secrets and two wipes); a founding of two (5,381 states); a founding of three (187,941 states, at most one lost secret) |
| 4 | **Every flow restarts.** From every reachable state the admission can still be signed, with what the parties keep for good and the rows they can read, and by the parties' own steps alone: no path counted needs a further loss or wipe. The restart is not from public state alone. It needs the prover to send its claim again, and the prover to have kept its nonce. | the same three runs |
| 5 | **A second voice.** Where the first seat and its binding have reached every signer, a second admission of the same person is seated only when no signer checked. This is a decision table of the cosigner's duty, counted. No state machine is run for it, and the three facts of each signer are inputs. | second admissions of two to four signers, each with three facts (checks, sees the first seat, holds its binding), with and without a duty holder; three readings of the cosigner's duty |
| 6 | **Stall, not fork.** With one seat row for each room key, a node's own check ends with one person for each key and no other, so there is one way to hold every binding. Two nodes that both count therefore hold the same bindings and agree. Two nodes that hold different bindings never both count. A waiting node names exactly the keys it lacks. | five seated room keys, one shared by two colluders; 248,832 pairs of holdings and votes, of which the 243 that both count are the one full holding against itself |
| 7 | **A relay.** From all the envelopes of one widening together, a relay with no row of the room and no secret derives neither the room nor a nonce nor a challenge secret, and no person from an envelope addressed to a room key. A holder of the room's rows with no binding ties no person to a room key. | ten envelopes; one seat row and four known persons |

The network of properties 3 and 4 holds every message ever sent and hands any of them to anyone, any number of
times, or never. A wipe empties it. An addressee may lose its pending secret. A message handed to a party that
cannot open it is checked on a table of every message against every party and every pending secret, and is not
explored as a step.

## Planted breaks

Each is a change to the rule that the same check must catch. Thirty-three are run. Those of properties 3 and 4
are run at a smaller bound than the property: one lost secret and one wipe, and for a founding of three one lost
secret and no wipe.

| Property | Break | What the check finds |
|---|---|---|
| 1 | the confirmation is not keyed by the challenge's secret | a forged key |
| 1 | the challenge is made to the room key | a forged key |
| 1 | the addressee does not check the opened person | a forged key |
| 1 | the addressee does not check the commitment | P's key taken as a coalition person's |
| 1 | the info binds neither room key, commitment nor addressee | a forged key |
| 1 | the info does not bind the addressee | an answer made for one addressee accepted by another |
| 1 | the info binds neither the room nor the commitment | a key P holds in another room taken as P's in this one |
| 2 | the claim carries P's identity signature | a third party is convinced |
| 2 | the commitment is outside what R signs | the addressee can show nothing about whom R named |
| 2 | the seat row is also signed under P's identity key | a third party is convinced from the row alone |
| 3 | a cosigner signs on the claim (widening, and a founder at a founding) | a signature with no binding |
| 3 | a cosigner takes the inviter's word | a signature with no binding |
| 3 | the admission does not name the duty holder's acknowledgement | an admission the duty holder never checked |
| 3 | the confirmation is not keyed | a confirmation that answers a lost challenge is accepted |
| 3 | an addressee that lost its pending secret takes a confirmation anyway | a signature on a binding checked against nothing |
| 3 | the admission stands on the inviter and the duty holder only | an admission the second cosigner never signed |
| 3 | a founder signs holding one of the two other founders' bindings | a founder's signature with a binding missing |
| 4 | the joiner sends each claim once | states from which the admission is never signed |
| 4 | an addressee never issues a second challenge (widening and founding) | the same |
| 4 | an addressee refuses a room key for good after one confirmation it cannot open | the same |
| 4 | an addressee never sends its pending challenge again | the same, after a wipe |
| 5 | a checking member signs although the person is seated | a second voice with a checker among the signers |
| 6 | no check of the opening against the commitment | two nodes holding every binding count differently |
| 6 | a node counts over the bindings it has | two nodes count differently |
| 6 | a node waits only for the bindings of the keys that voted | the same yes and no, a different number of persons in the room |
| 7 | the claim outside the seal; the challenge outside an envelope; the info beside the confirmation; an envelope addressed by the room key's record; the return sealed to the inviter's identity key | the relay learns a person, the room, or both |
| 7 | the commitment covers no fresh bytes | a holder of the rows tries every person it knows and finds the one |

## Witnesses

Fourteen named states are required to be reached, so that no property passes on an empty premise. Among them:
P's own answer is accepted; the admission is signed, after a lost secret, and after the network lost everything;
a stale confirmation is dropped; a repeated confirmation changes nothing; every cosigner has signed and the
admission waits for the duty holder; a founding waits for its last founder; both nodes count, one waits, both wait;
and a second voice is seated where nobody checked, which is the stated cost.

Two stated limits are reproduced as runs. A third party that forms the challenge itself is convinced. A coalition
that holds a roster key of P places an occurrence with a binding key of its own and forges a key: the binding key
is as good as the roster that states it.

## What the run found

The check requires each of these to be reproduced, so a change that hides one fails. It prints five finding lines
for the four items below, since item 3 is reached from property 6 and again from property 1.

1. **A cosigner that cannot tell.** The text forbids a cosign where the binding names a person already seated. A
   checking member that sees the first seat and lacks its binding cannot tell, and as written it signs. 1,245 of
   4,672 second admissions are seated that way. Under a strict reading, where it waits until it holds the binding
   of every seated key, there are none.
2. **Two admissions at once.** One person asks for two voices at the same time. Every signer checks, the first seat
   has reached none of them, and both are seated. This holds under both readings of the text and with a checking
   duty holder. So the sentence "a person gains a second voice only where every signer of that admission failed to
   check" does not hold for two admissions at once. Under a reading the text does not state, where a checker
   refuses a person it holds another binding of, seated or not, a checking duty holder closes it, since the duty
   holder holds every binding. With no duty holder, two admissions whose checking signers share no binding still
   seat one.
3. **Two seat rows of one room key.** The text says the seat row carries a commitment and does not say what a
   second seat row of the same room key does. If a binding is taken when it opens either commitment, the fork the
   commitment was added to stop returns. If such a key takes no binding at all, nothing forks and no node ever
   counts, and the holder of that key causes the stall alone. The same gap is reached from property 1. A coalition
   that holds the signing secret of P's room key signs a second seat row for it, committed to its own person C. C
   answers the addressee's challenge honestly, and an addressee that reads that row takes P's room key to be C's.
   Nothing in the construction refuses it, so "not stolen" holds only where the addressee reads the seat row P
   signed.
4. **The invitation's address.** The invitation is sealed to the invitee's identity key, since no room key of
   theirs exists yet. Unless the key exchange hides the key a seal was made to, a relay learns that this person
   was sent a sealed envelope. It learns nothing of which room.

The run also shows what in the confirmation's info carries weight within this bound. Over all 32 subsets left out,
a key is forged exactly when the room key and the commitment are both left out, an answer is misaddressed exactly
when the addressee's room key is left out, and a key of P's other room is taken exactly when the room and the
commitment are both left out. So the room binds nothing here that the commitment does not. The binding key's
thumbprint is not exercised at all: no person in the run has two binding keys.

## Bounds raised by one, run by hand

These are not part of the check command. Each was run once on the model as committed, with the same safety and
restart tests unless the row says otherwise, and found no unsafe state and no state from which the admission cannot
be signed.

| Run | Bound | States |
|---|---|---|
| widening | 3 lost secrets, 2 wipes | 737,249 |
| widening | 2 lost secrets, 3 wipes | 330,201 |
| founding of two | 3 lost secrets, 3 wipes | 21,243 |
| founding of three | 2 lost secrets, no wipe | 1,217,001 |
| founding of three | 1 lost secret, 1 wipe | 14,678,898, safety only: states were kept as 64-bit hashes to stay under 2 GiB, so the count is exact up to a hash collision, and the restart test was not run at this bound |

## Against `causal_kernel/roomkey.py`

`roomkey.py` takes a binding as a fact with a set of makers. This model derives who can make each term. The two
overlap on five answers and agree on each: when two commitments are equal, that the planned binding is authentic
and deniable, that an identity signature is authentic and not deniable, a count of persons in 1,296 cases, and the
fork of two colluders with and without the commitment.

This model adds four things. It derives that a binding is accepted only by the addressee it was made for, which
`roomkey.py` assumes and which rests on the addressee's room key in the info. It shows that the addressee can
produce the confirmation only once a holder of R's secret has said the opening, so what the addressee holds shows
whom R's holder named and nothing about P. It runs the carriage, which `roomkey.py` does not have. It runs a second
admission where the first seat or its binding has not reached a signer, and a room key with two seat rows.
`roomkey.py` runs neither, and its sentence on the second voice holds only for the case it runs.

## What is not modelled

- Real cryptography: the hybrid key exchange, the keyed seal, the hash. Deniability against an addressee that
  forms a challenge it cannot itself open stays a conjecture, as CC 3.1.3.2 states.
- Anonymity of the key exchange. One run assumes it and says so.
- Traffic: who sends to whom and when, and the route by which an envelope reaches the node that holds a room key.
- How the joiner learns the room keys of the cosigners and the duty holder. The invitation is taken to carry their
  key records.
- A voice of several room keys. One room key for each party is run, so "one exchange for each room key" is run as
  one exchange.
- The order in which rows reach a node. Rows are held by all once signed, and the kernel's own models state that an
  admission naming a row waits for it.
- A joiner that loses its room key before the seat. It is read as a fresh join, whose meeting with the first is
  finding 2.
- A founder who is not a cosigner of a widening. No row shows that such a founder holds the joiner's binding, so
  the model has nothing to check.
- More than one binding key for one person, a rotated binding key, and the liveness of the occurrence that states
  it.
- A coalition that includes the addressee, and an accomplice who lends an identity: a binding that names an
  accomplice is one the accomplice made, and the model cannot see who holds a room key.
- A relay that is or was a member of the room.
- Fairness. Property 4 says the admission can still be signed, not that it will be.
- An adversary inside the carriage. The network of properties 3 and 4 reorders, drops, repeats and misdelivers
  honest messages. It forges none. Forged confirmations are property 1, which is run apart and is not composed
  with the state machine.
- A prover that has lost its nonce. The nonce is kept for as long as the seat lasts, since every later addressee
  needs the opening. A device that loses it can give no further binding for that room key.
- Whether the prover answers a challenge from an addressee it sent no claim to. Here it answers any challenge it
  can open, to any addressee the coalition names. That is the stronger adversary for property 1. What an observer
  learns from the fact that an answer was sent is traffic, and is not modelled.
- A founding of three with both a lost secret and a wiped network inside the check command.

## Assumed and not checked

The coalition of property 1 is the largest one, and a smaller one derives no more. One challenge of the
coalition's own making stands for all of them, since P's answer to it tells the coalition nothing it lacks. A hash
has no collision and a seal cannot be changed into another.
