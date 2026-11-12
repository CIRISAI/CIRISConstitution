# `formal/key_plane` — who holds which content key

**The point.** Content at rest is sealed under a key, and the key is wrapped to the devices allowed to read it
(CC 4.4.3.4.1). What a membership change does to keys differs by tier: `self` and `family` seal every write under
a fresh key, `community` and `affiliations` seal under the writer's epoch key (CC 4.4.3.4.5, CC 4.4.3.2.1). The
readings found twenty-three conflicts among these rules. This model runs the rules as the typed data carries
them and checks what a member who joins, leaves or loses a device can and cannot read.

**The model.** `key_plane_model.py`. One group and one writer. Two members come and go, and one of them has a
second device that may be added and revoked. The acts are an admission, a removal, a resignation, a device added,
a device revoked, a rotation falling due, and a write.

The key effect of each act is not written in the model. It is read from the change column of
`manifests/transitions.json`, which gives every membership act one of four words by scope: `rekey_walk`,
`next_seal`, `stop_wrap`, `rotate_epoch`. The model gives the four words their meaning and refuses to run if an
act has no word at a scope or if two scopes of one tier differ.

**What is checked**, over every sequence of up to six acts at each tier:

| | Property |
|---|---|
| K1 | a key is wrapped only to a live device of a current member |
| K2 | no write is sealed under a key held by a member who has left |
| K3 | after a write every live device of every current member holds its key |
| K4 | at the epoch tier a new member is wrapped the key of the epoch it joins, at the next write, and no other |
| K5 | at the per-write tier a new member, and a member's new device, holds the key of every earlier write |
| K6 | the epoch changes only after a departure or a rotation falling due, never on an admission |
| K7 | a wrap once made is never unmade |
| K8 | no write is sealed under a key held by a revoked device of a member who stays |
| K9 | a member admitted to a group with content in the current epoch holds that epoch's key without a further write |

K1 to K7 hold at both tiers. Changing any one word of the table breaks the property that names it.

**Two named breakers.** K8 fails at the epoch tier. The data gives a device revocation a key effect at `self`
scope alone, and the text says nothing of the epoch key when a continuing member's device is revoked. So a lost
or stolen device keeps reading what the writer seals until a removal or a scheduled rotation moves the epoch. If
a revocation rotated the epoch as a removal does, K8 would hold with nothing else changed. The check requires
exactly this failure (conflict C558 of `formal/derivation/text_conflicts.tsv`).

K9 fails at the epoch tier as well. `next_seal` wraps a newcomer at the writer's next write. In a room where
nobody writes again, the newcomer never reads what the current epoch already holds, though the rule grants it.
A three-node run of an implementation showed it. With the wrap made when the writer's roster gains the member,
K9 holds and K1 to K7 still hold; where a rotation is due, the wrap still waits for the write that rotates
(conflict C559).

**What it does not model.** The instant a writer learns of a removal: a write made before the writer holds the
removal row is under the old key, which is the exposure window of CC 5.1. Streams and their kept epochs
(CC 5.1, CC 5.3.3.2.5), where a late joiner and a change of `history_on_join` mid-stream are open. Who may sign a
grant (the signer gate, `tools/check_signer_gate.py`). Whether a holder of a key is served the bytes.

**To explore, with the wire work of the next edition.** A rotation today is one signed row for each recipient
device (CC 3.3.2): 150 rows and about 1.15 MB from one writer in a room of fifty members with three devices each,
some 59% of it signature. An alternative signs once over a digest of the set of wraps and delivers each device its
own wrap with a short proof of inclusion: one signature for a rotation and about 60% fewer bytes. Three things it
would have to answer, and a model should show before anyone chooses: a wrap is then admissible only once its
header is held, so two nodes holding different parts must still converge; a header is a set object, a kind the
row slot was closed against; and a header may disclose how many devices a room has. This is to be modelled as an
exploratory piece on the wire-protocol twin (`formal/cewp_node`), against K1 to K9 here, when that work is reached.

Run: `python3 formal/key_plane/key_plane_model.py --check`
