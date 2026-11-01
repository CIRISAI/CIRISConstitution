# `formal/contact` — what the relay learns when two peers become contacts

**Question.** A peer that wants to be reachable publishes its owner binding at federation scope ([CC 5.4.6](../../constitution/part_5_transport_substrate.md#5.4.6), the public roster). A stranger reaches it by its federation identity. The first message crosses a relay (the canonical), because two NAT'd peers hold no path to each other; after consent the pair brings its link direct by exchanging reflexive addresses ([CC 5.4.6](../../constitution/part_5_transport_substrate.md#5.4.6), the intermediary's only role is reachability). The relay holds every announced node's signed route. When may it hand one to a requesting peer, and what does it come to hold about who contacted whom?

**The model** (`Contact.lean`, Lean 4 core, no Mathlib). Four events: a request, an acceptance, a route fetch from the relay, a punch. Two kinds of peer: announced (a signed route, an address) and anonymous (reached only at a published rendezvous, [CC 5.4.6](../../constitution/part_5_transport_substrate.md#5.4.6) item 6; nothing to hand). Two designs under one vocabulary:

| | `relayGated` | `ownerHanded` |
|---|---|---|
| the contact grant | crosses the relay as a plaintext row; the relay holds it | sealed end to end; the relay forwards bytes |
| an owned node's route | served by the relay to a peer the owner's held grant names | handed by its owner inside the sealed request or acceptance; the relay serves none |
| the relay's record of the pair | both grants, durable | a link crossed it, or a packet reached a mailbox it keeps |

**Proved for both designs, over every trace** (`inv_run`):

- `route_only_from_its_owner`: a peer holds a route only when its owner's grant names that peer.
- `anonymous_route_never_held`, `anonymous_address_never_held`: nobody ever holds an anonymous peer's route or address.
- `direct_only_mutual_and_announced`: a direct path forms only between two announced peers who both consented.

**Where they part:**

- `owner_handed_relay_holds_no_pair`: under `ownerHanded` the relay holds no pair record, whatever the trace.
- `relay_gated_holds_the_pair`: under `relayGated` the relay holds both grants of the worked pair; `relay_gated_learns_the_pseudonym_graph`: an anonymous peer's pseudonymous grant sits there too.
- `owner_handed_two_announced`, `owner_handed_one_anonymous`: the exact relay contents under `ownerHanded` are the two unavoidable facts.
- `both_complete_two_announced`, `both_complete_one_anonymous`, `no_consent_no_route`: both designs complete the contact, the announced pair goes direct, the anonymous pair never does, and without the acceptance no address moves.

**The rule.** The owner-handed design is the rule of [CC 5.4.6](../../constitution/part_5_transport_substrate.md#5.4.6), first contact through a forwarder, with item 9 of the Anonymous Tier for the anonymous peer.

**What it does not model.** Store-and-forward for a sleeping peer (the relay then keeps sealed bytes until pickup, which is custody of ciphertext, not a pair record); route rotation after contact (a superseding route is handed the same way the first was); the facilitator's knowledge of each dialled-in peer's own reflexive address, which every transport node has for the life of a link; traffic analysis on the relay's link facts, which [CC 1.13.3.1](../../constitution/part_1_foundation.md#1.13.3.1) concedes.

**Run.** `lean Contact.lean` (exit 0, no `sorry`). CI compiles it in the `reciprocity` job of `.github/workflows/formal.yml`.
