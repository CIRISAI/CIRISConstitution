# The life of a mesh, top down

One story, in order. Each step says who acts, what comes into being, and what can end it. The model `MeshLife.tla` has one action per sentence in bold, and it closes: every path from the ceremony reaches the end of the mesh, and nothing along the way is left owning nothing or owned by no one.

## 1. Three people sit down

**Three people sit down and perform the genesis ceremony.** Each holds their own key on their own hardware. Each signs the charter, their recovery commitment, the serve-node grants and the authorization. What comes out is the bundle: tamper-evident, pinned by its fingerprint, published with the release. That fingerprint is the only anchor anyone will ever need; the names in the bundle are names, not anchors.

Born here: the **mesh** (live), the three **holders** (seated), and the first **canonical node**, seated in the bundle but owned by no one yet.

A holder can be **lost** (hardware gone, person gone, person coerced). **A majority of the seated holders can re-mint**, seating a new person in the lost seat. Below a majority nothing about the root can move, by design.

## 2. The canonical gets an owner

**A person who is already announced takes ownership of the canonical node and announces it.** Only then does it serve. A canonical is one source of route rows, never a required party: everything below works between two phones with no canonical anywhere.

## 3. A person arrives

**A person makes a key.** Nothing else is needed. **The person claims a device** with that key and the bundle's anchor; the device is now theirs and roots to the mesh. **The person announces** by carrying their owner binding at federation scope; from now on they can be found by their federation id. An unannounced person exists and can act in rooms they are invited to, but no stranger can reach them.

**A device is released** when lost, evicted by the person's other keys, or retired. **A person is gone** only when every device of theirs is released, they are in no room, steward no agent, and hold no contact.

## 4. Two people become contacts

**One announced person asks another for contact.** The request crosses a forwarder sealed, carrying the asker's own route. **The other accepts**, sealing back their own route, and the two go direct; the forwarder holds nothing about the pair. **Either declines or ends it.**

## 5. A room is founded

**An announced person founds a community.** They are its first member. **A member proposes another person.** **The proposed person accepts** and is a member, or **declines**. **A member resigns.** **The other members remove a member**; one member alone cannot remove anyone. **A room with no members is dissolved**, and what it held is purged.

## 6. Members write

**A member writes a row** in the room. **The author withdraws it**; a withdrawn row is then **purged**. A row never comes back once withdrawn.

## 7. A person consents, and revokes

**An announced person grants consent** for their traces to be captured. **They revoke it**, any time, and may grant again.

## 8. An agent is bonded

**An announced person bonds an agent** and is its steward. **The steward hands the agent to another announced person.** **The steward freezes the agent**, and **a frozen agent is retired**; retirement runs one way.

## 9. The holders halt

**One seated holder latches a halt.** **A lone latch lapses at the fuse.** **A majority confirms it**, and **a majority resumes**. A confirmed halt is a record the bundle keeps.

## 10. The mesh winds down

**A majority of the holders decides to wind down.** From that instant nothing new is born: no key, no claim, no contact request, no room, no proposal, no row, no bond, no consent. Everything already alive runs to its own end by the steps above: members resign, rooms dissolve, rows purge, devices release, agents retire, the canonical retires, people are gone. **When nothing is left, the mesh has ended.**

## How it closes

The model is bounded to the genesis topology: three holders, one canonical, two persons with one device each, one room, two rows, one agent. TLC closes the full state space with no deadlock and these invariants:

- nothing exists before the ceremony;
- a claimed device has a living owner;
- a member is an announced person;
- a row lives only in a founded room, and its author was a member;
- a bonded agent has an announced steward;
- a confirmed halt was confirmed by a majority;
- an ended mesh is empty.

And one liveness property under weak fairness of the wind-down steps: once the holders decide to wind down, the mesh ends.

Three twins loosen one rule each and fail the invariant that rule carries: a lone holder confirming a halt, a person gone while a device of theirs is still claimed, a person gone while stewarding an agent.
