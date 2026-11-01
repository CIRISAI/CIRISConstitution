# The life of a mesh, top down

One story, in order. Each step says who acts, what comes into being, and what can end it. The model `MeshLife.tla` has one action per sentence in bold, and it closes: every path from the ceremony reaches the end of the mesh, and nothing along the way is left owning nothing or owned by no one.

## 1. Three people sit down

**Three people sit down and perform the genesis ceremony.** Each holds their own key on their own hardware. Each signs the charter, their recovery commitment, the serve-node grants and the authorization. What comes out is the bundle: tamper-evident, pinned by its fingerprint, published with the release. That fingerprint is the only anchor anyone will ever need; the names in the bundle are names, not anchors.

Born here: the **mesh** (live), the three **holders** (seated), and the first **canonical node**, seated in the bundle but owned by no one yet. **The root confers the attest duty on a node**, and **withdraws it**; evidence offered while it is live is blessed.

A holder can be **lost** (hardware gone, person gone, person coerced). **A majority of the seated holders can re-mint**, seating a new person in the lost seat. Below a majority nothing about the root can move, by design.

## 2. The canonical gets an owner

**A person who is already announced takes ownership of the canonical node and announces it.** Only then does it serve. A canonical is one source of route rows, never a required party: everything below works between two phones with no canonical anywhere.

## 3. A person arrives

**A person makes a key.** Nothing else is needed. **The key's post-quantum half is registered**; until both halves are present the key cannot be announced. **The person claims a device** with that key and the bundle's anchor; the device is now theirs and roots to the mesh. **The person announces** by carrying their owner binding at federation scope; from now on they can be found by their federation id. An unannounced person exists and can act in rooms they are invited to, but no stranger can reach them. **A key rotates** to its successor once, and **a key is escrowed**. A minor never announces: **an announced adult binds themselves as the minor's guardian**, and only then can the minor be proposed to a room; **the bond ends** when the minor is in no room. **A capacity finding is made about an announced person** under the trusted tier, and **it lapses**; while it stands the person stewards no agent, holds no Wise Authority seat and no ward.

**A device is released** when lost, evicted by the person's other keys, or retired. **A person is gone** only when every device of theirs is released, they are in no room, steward no agent, and hold no contact.

## 4. Two people become contacts

**One announced person asks another for contact.** The request crosses a forwarder sealed, carrying the asker's own route. **The other accepts**, sealing back their own route, and the two go direct; the forwarder holds nothing about the pair. **Or the other ignores it**: a private, local act the asker is never told of, which looks to the asker exactly like a request still pending, and which **the ignorer can undo**. **Either party blocks the other**: a private act too, after which further requests from the blocked key are dropped without answer and nobody, the forwarder included, learns of it; **a block is lifted** by the one who made it. **Either ends a contact.**

## 5. A room is founded

**An announced person founds a community.** They are its first member and its first moderator; **when the moderator leaves, another member is named**. If the room is an affiliation its charter is declared at founding and **its officers supersede it**. A room's record may name who may publish in it: then **the moderator grants a member the publish right** and **withdraws it**, and the others read; such a room is a channel, and a post in it cannot be replied to in place. Where the record names no right, every member writes. **A member opens an event** in the room, and **closes it** as completed or cancelled. **A member proposes another person.** **The proposed person accepts** and is a member, or **declines**. **A member resigns.** **The other members remove a member**; one member alone cannot remove anyone. **A member mutes another member**, a private filter in the reader that changes nothing in the room, not a row, not the roster; a row that names the muter stays in the muter's own read, because a statement about a person is always visible to that person. **A mute is lifted** by the one who set it. **A room with no members is dissolved**, and what it held is purged.

## 6. Members write

**A member writes a row** in the room, inline or chunked. **The author marks it durable**; a withdrawn durable row descends. **The author withdraws it**; a withdrawn row is then **purged**. A row never comes back once withdrawn. **The moderator withholds a row** in quarantine and **releases it**. **Another member flags a row**, and **the moderator decides**: kept visible, consent-gated, or a hard removal, which withdraws the row as a duty-holder's record the author cannot undo. **An announced person opens their ledger**, **checkpoints it**, **continues it**, **closes it**; **a fork** is evidence against them.

## 7. A person consents, and revokes

**An announced person grants consent** for their traces to be captured. **They revoke it**, any time, and may grant again.

## 8. An agent is bonded

**An announced person bonds an agent** and is its steward. **The steward hands the agent to another announced person.** **The steward freezes the agent**, and **a frozen agent is retired**; retirement runs one way. **An announced person takes the Wise Authority seat**, **steps down**, or **a quorum finds the seat abandoned or seized** and **names a successor**. **The agent defers** a question while no halt is latched; **the seated Wise Authority answers** it, approved or rejected; **an approval amends the agent's identity**; **an answered deferral is cleared**. **The canonical stages the room's goal tree**; **a founder proposes it**; **the founder quorum declares it**; **an approach, a method and a progress measure are declared** under it, in that order; **the declarer withdraws it**, and the evidence under it is superseded. **A node holding the attest duty offers evidence** against the declared goal, **the evidence is admitted** when its bytes match, **counted** by the progress measure, and **superseded** by a re-post.

## 9. The holders halt

**One seated holder latches a halt.** **A lone latch lapses at the fuse.** **A majority confirms it**, and **a majority resumes**. A confirmed halt is a record the bundle keeps.

## 10. The mesh winds down

**A majority of the holders decides to wind down.** From that instant nothing new is born: no key, no claim, no contact request, no room, no proposal, no row, no bond, no consent. Everything already alive runs to its own end by the steps above: members resign, rooms dissolve, rows purge, devices release, agents retire, the canonical retires, people are gone. **When nothing is left, the mesh has ended.**

## How it closes

The model is bounded to the genesis topology: three holders, one canonical, two persons with one device each, one room, two rows, one agent, one Wise Authority seat, one goal. The spine of the story (the ceremony, the canonical, persons and devices, the room and its members, rows, the agent, the wind-down) is always on; everything else is a plane that switches on by a constant: the halt, consent, contact (with ignore, block and mute), identity, content, moderation, the Wise Authority seat, the deferral, the goal, evidence, the event and charter, the ledger. Each plane is checked on the spine, one at a time, and the three that the first story had (halt, consent, contact) together. Planes touch each other only through the spine, so a fact that mentions the spine and one plane holds in the whole. TLC closes every configuration with no deadlock, the spine's invariants being:

- nothing exists before the ceremony;
- a claimed device has a living owner;
- a member is an announced person;
- a row lives only in a founded room, and its author was a member;
- a bonded agent has an announced steward;
- a confirmed halt was confirmed by a majority;
- an ended mesh is empty.

And one liveness property under weak fairness of the wind-down steps: once the holders decide to wind down, the mesh ends.

and each plane adding its own (an ignored request looks to the asker like a pending one; a block is one party's own act; a mute is between members and changes no row; a minor is never announced; an announced key has both halves; a guardian is an announced adult; an incapacitated person holds no seat; the moderator is a member; a hard removal withdraws the row; a durable mark rides an admitted row; a seated Wise Authority is announced; an amendment follows an approval; a goal lives in a founded room; evidence names a declared goal and is counted only by a measure; the measure chain is whole; an event belongs to a founded room; a charter only on an affiliation).

Three twins loosen one rule each and fail the invariant that rule carries: a lone holder confirming a halt, a person gone while a device of theirs is still claimed, a person gone while stewarding an agent.

Every variable of the state table is carried by a model, this one or a chapter: `tools/check_lifecycle_coverage.py` gates it.
