# `formal/mesh_life` — the whole story, one model, and it closes

**The story** is [`LIFECYCLE.md`](LIFECYCLE.md) (and each thing's own story is [`../STORIES.md`](../STORIES.md)): ten steps from three people sitting down to the mesh having ended. **The model** is `MeshLife.tla`, with one action per sentence in bold in the story, in the story's order.

**The bound.** Three holders, two persons with one device each (a device is named by its owner), one room, two rows, one agent, one Wise Authority seat, one goal, one canonical. The ruled configurations use symmetry over holders, adult persons and rows.

**The spine and the planes.** The spine (steps 1, 2, 10 and the bare forms of 3, 5, 6, 8: the ceremony, the canonical, persons and devices, the room and its members, rows, the agent, the wind-down) is always on. Everything else is a plane switched on by the constant `Families`, checked on the spine one at a time, and the three the first story had (halt, consent, contact) together as `MeshLife.cfg`:

| plane | objects | configuration |
|---|---|---|
| halt | a holder lost and re-minted, the latch, the lapse, the majority's confirmation and resumption | in `MeshLife.cfg` |
| consent | a subject's consent granted and revoked | in `MeshLife.cfg` |
| contact | the request, acceptance, private ignore and un-ignore, private block and unblock, the end; a member's mute | in `MeshLife.cfg`; alone in `MeshLife_contact.cfg` |
| identity | the post-quantum half, key rotation and escrow, the minor and the guardian bond, the capacity finding | `MeshLife_identity.cfg` (p2 a minor) |
| content | inline or chunked blobs, the durable mark and its descent | `MeshLife_content.cfg` |
| moderation | quarantine; a moderation action any member raises, the respondents, the ruling by a moderator or by the delegated agent at any time, else the majority of respondents at the window; a hard removal as a duty-holder's record; the halt over the agent moderator | `MeshLife_moderation.cfg`, `MeshLife_moderation_halt.cfg` |
| wa | the Wise Authority seat, its abandonment, seizure and successor | `MeshLife_wa.cfg` |
| deferral | the agent's deferral, the answer, the identity amendment | `MeshLife_deferral.cfg` |
| goal | the goal tree staged, proposed, declared, withdrawn; approach, method, measure | `MeshLife_goal.cfg` |
| evidence | the attest duty; evidence offered, admitted, counted, superseded, blessed or not | `MeshLife_evidence.cfg` |
| event | the affiliation charter and the room's event | `MeshLife_event.cfg` (the room an affiliation) |
| ledger | the owner's ledger: head, checkpoint, fork | `MeshLife_ledger.cfg` |

Planes touch each other only through the spine, so every invariant mentions the spine and at most one plane, and a fact checked on spine plus plane holds in the product. The product of every plane on one run is beyond the checker and is not claimed.

**What closes.**

| configuration | planes | result |
|---|---|---|
| `MeshLife_spine.cfg` | none (the bare spine) | closes: 46,858 distinct states, 2 s |
| `MeshLife.cfg` | halt, consent, contact | closes: 13,001,125 distinct states, 15 min on 16 workers |
| `MeshLife_contact.cfg` | contact (request, accept, ignore, block, mute) | closes: 274,578 states, 12 s |
| `MeshLife_channel.cfg` | the bare spine with a room that names its writers (`WriteRight = "named"`) | closes: 81,130 states, 3 s |
| `MeshLife_identity.cfg` | identity (p2 a minor) | closes: 1,296,397 states, 21 s |
| `MeshLife_content.cfg` | content | closes: 347,638 states, 9 s |
| `MeshLife_moderation.cfg` (one row) | moderation: any member raises an action, members respond, a moderator or the delegated agent rules at any time, else the majority of respondents decides at the window | closes: 185,537 states, 7 s |
| `MeshLife_moderation_halt.cfg` (one row) | moderation with the halt: the halt stops the agent moderator's ruling and leaves the members their vote | closes: 244,158 states |
| `MeshLife_wa.cfg` | the Wise Authority seat | closes: 275,530 states, 9 s |
| `MeshLife_deferral.cfg` | the deferral | closes: 250,903 states, 7 s |
| `MeshLife_goal.cfg` | the goal tree | closes: 253,274 states, 7 s |
| `MeshLife_evidence.cfg` | evidence, with the goal chain | closes: 2,792,648 states, 77 s |
| `MeshLife_event.cfg` | the event and the charter (the room an affiliation) | closes: 356,482 states, 10 s |
| `MeshLife_ledger.cfg` | the ledger | closes: 666,574 states, 18 s |
| `MeshLife_live.cfg` (one row, no symmetry) | halt, consent, contact; `Live_WindsDownToEnd` | holds: 15,428,353 states, 55 min 39 s on 16 workers (run here; CI runs the next row) |
| `MeshLife_live_contact.cfg` (one row, no symmetry) | contact; `Live_WindsDownToEnd` | holds: 163,863 states, 20 s |
| `MeshLife_lone_halt.cfg` | one holder may confirm a halt | fails `Inv_HaltIsMajority` |
| `MeshLife_gone_with_device.cfg` | a person may be gone while a device of theirs is claimed | fails `Inv_DeviceHasOwner` |
| `MeshLife_gone_stewarding.cfg` | a person may be gone while stewarding an agent | fails `Inv_AgentHasSteward` |

Every closing configuration checks every invariant and the two progress facts (`Act_WindNeverRaisesRank`, `Act_WindStepLowersRank`) and the mute property (`Act_MuteChangesNoRow`), with no deadlock; all 32 workers unless stated.

**The spine's invariants, in plain words.** Nothing exists before the ceremony. A claimed device has a living owner. A member, and a proposed member, is an announced person (or a minor whose guardian is bound). A row lives only in a founded room and names its author. A bonded or frozen agent has an announced steward. A confirmed halt was confirmed by a majority. A live contact is between announced people. An ended mesh is empty. **The planes add theirs:** an ignored request looks to the asker exactly like a pending one; a block is one party's own act; a mute is between members and changes nothing but itself; a minor is never announced; an announced key has both halves; a guardian is an announced adult; an incapacitated person holds no seat; the moderator is a member, or the bonded agent; an action lands by a moderator's ruling or by the majority of the respondents and never otherwise; the majority lands only the action that was asked or keeps the row visible; the halt stops the agent moderator's ruling and not the members' vote; a hard removal withdraws the row; a durable mark rides an admitted row; a seated Wise Authority is announced; an amendment follows an approval; a goal lives in a founded room; evidence names a declared goal and is counted only by a measure; the measure chain is whole; an event belongs to a founded room; a charter only on an affiliation.

**Progress, as facts rather than a long run.** On the full bound the liveness property is checked through three facts that imply it under weak fairness of the wind-down steps: while winding no step raises the rank (`Act_WindNeverRaisesRank`), every wind-down step lowers it (`Act_WindStepLowersRank`), and while winding and not yet empty some wind-down step is enabled (`Inv_WindAlwaysCanStep`). The rank counts what is still alive. On the one-row bound the property itself is checked.

**Where it bubbled, and what was done.** The first cut closed at 176,235,777 distinct states in 9 min 27 s. The size came from state that carried no information multiplying everything else: the set of confirming holders (now one bit, whether a majority confirmed), a consent that remembered it had been revoked (now granted or not), a purged row that remembered its author (now cleared), and no symmetry. Those four changes, with the progress facts replacing the liveness run on the big bound, took it to 3.2 million. Adding every remaining object to one flat run would not close (the governance objects alone passed 25 minutes without finishing), which is what the planes are for: each object's lifecycle is checked on the spine it hangs from, and the planes are independent of each other by construction.

**What it does not model.** More than one room, more than one device per person, more than one agent, federation between meshes, the anonymous tier (see `contact/`), the content of rows, the trust-root arithmetic (see `trust_root/`, `accord_halt/`), the self roster's thief and loss cases (see `self_roster/`), the retirement ladder's seven steps (see `retirement/`). Each of those is a chapter model; this one is the spine they hang on.

**Run.** `java -cp tla2tools.jar tlc2.TLC -workers auto -deadlock -config MeshLife.cfg MeshLife.tla` and the same for each twin; the liveness run wants a few cores and ten minutes. CI runs all five (`.github/workflows/formal.yml`, job `mesh_life`).
