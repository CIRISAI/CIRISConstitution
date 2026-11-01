# `formal/mesh_life` — the whole story, one model, and it closes

**The story** is [`LIFECYCLE.md`](LIFECYCLE.md) (and each thing's own story is [`../STORIES.md`](../STORIES.md)): ten steps from three people sitting down to the mesh having ended. **The model** is `MeshLife.tla`, with one action per sentence in bold in the story, in the story's order.

**The bound.** Three holders, two persons with one device each (a device is named by its owner), one room, two rows, one agent, one canonical. The ruled configuration uses symmetry over holders, persons and rows.

**What closes.**

| configuration | what it checks | result |
|---|---|---|
| `MeshLife.cfg` | the eight invariants, the two progress facts, no deadlock | closes: 3,224,293 distinct states (38,371,214 generated), 36 s on 32 workers |
| `MeshLife_live.cfg` (one row, no symmetry) | `Live_WindsDownToEnd`: once the holders decide to wind down, the mesh ends | holds: 4,000,129 distinct states, 5 min 33 s on 16 workers |
| `MeshLife_lone_halt.cfg` | one holder may confirm a halt | fails `Inv_HaltIsMajority` |
| `MeshLife_gone_with_device.cfg` | a person may be gone while a device of theirs is claimed | fails `Inv_DeviceHasOwner` |
| `MeshLife_gone_stewarding.cfg` | a person may be gone while stewarding an agent | fails `Inv_AgentHasSteward` |

**The invariants, in plain words.** Nothing exists before the ceremony. A claimed device has a living owner. A member, and a proposed member, is an announced person. A row lives only in a founded room and names its author. A bonded or frozen agent has an announced steward. A confirmed halt was confirmed by a majority. A contact is between announced people. An ended mesh is empty.

**Progress, as facts rather than a long run.** On the full bound the liveness property is checked through three facts that imply it under weak fairness of the wind-down steps: while winding no step raises the rank (`Act_WindNeverRaisesRank`), every wind-down step lowers it (`Act_WindStepLowersRank`), and while winding and not yet empty some wind-down step is enabled (`Inv_WindAlwaysCanStep`). The rank counts what is still alive. On the one-row bound the property itself is checked.

**Where the first version bubbled, and what was done.** The first cut closed at 176,235,777 distinct states in 9 min 27 s. The size came from state that carried no information multiplying everything else: the set of confirming holders (now one bit, whether a majority confirmed), a consent that remembered it had been revoked (now granted or not), a purged row that remembered its author (now cleared), and no symmetry. Those four changes, with the progress facts replacing the liveness run on the big bound, took it to 3.2 million.

**What it does not model.** More than one room, more than one device per person, more than one agent, federation between meshes, the anonymous tier (see `contact/`), the content of rows, the trust-root arithmetic (see `trust_root/`, `accord_halt/`), the self roster's thief and loss cases (see `self_roster/`), the retirement ladder's seven steps (see `retirement/`). Each of those is a chapter model; this one is the spine they hang on.

**Run.** `java -cp tla2tools.jar tlc2.TLC -workers auto -deadlock -config MeshLife.cfg MeshLife.tla` and the same for each twin; the liveness run wants a few cores and ten minutes. CI runs all five (`.github/workflows/formal.yml`, job `mesh_life`).
