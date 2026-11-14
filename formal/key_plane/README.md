# `formal/key_plane` — who holds which content key

**The point.** Content at rest is sealed under a key, and the key is wrapped to the devices allowed to read it
(CC 4.4.3.16). What a membership change does to keys differs by tier: `self` and `family` seal every write under
a fresh key, `community` and `affiliations` seal under the writer's epoch key (CC 4.4.3.22, CC 4.4.3.4). The
readings found twenty-three conflicts among these rules. This model runs the rules as the typed data carries
them and checks what a member who joins, leaves or loses a device can and cannot read.

**The model.** `key_plane_model.py`. One group and one writer. Two members come and go, and one of them has a
second device that may be added and revoked. The acts are an admission, a removal, a resignation, a device added,
a device revoked, a rotation falling due, and a write.

The key effect of each act is not written in the model. It is read from the change column of
`manifests/transitions.json`, which gives every membership act one word by scope: `rekey_walk`,
`at_seat`, `stop_wrap`, `rotate_epoch`. The model gives each word its meaning and refuses to run if an
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
| K10 | a writer mints a key with no write only when a device no longer entitled holds its current key, or a scheduled rotation fell due |

All ten hold at both tiers. Changing any one word of the table breaks the property that names it.

**What it found.** On its first runs K8 and K9 failed at the epoch tier. A revoked device of a member who stayed kept the epoch key until the next rotation (conflict C558). A newcomer was wrapped at the writer's next write, so in a room where nobody wrote again they never read what the epoch already held; a three-node run of an implementation showed it (C559). The steward ruled on 2026-11-12: a revocation rotates the epoch as a removal does, and a member is wrapped when the writer's roster gains them, the writer rotating then if a rotation is due. The change column carries both, and the model holds them.

**When a rotation is due.** The first build of the seat door treated any removal as making a rotation due, so a writer that had sealed nothing would mint and wrap a key at the next seat for nobody's benefit: in a room of fifty, fifty such mints after one removal. A rotation is due only when a device no longer entitled holds the writer's current key (CC 4.4.3.16). In the model that is read from who holds what, not remembered as a flag: a member removed and seated again before any write leaves nothing due. K10 holds it, and the reading in which every departure makes a rotation due fails K10.

**A proposal, checked before the text moves.** Files at `self` and `family` take a fresh key for every write today, so one write signs a grant for each recipient device and a newcomer is caught up by a walk over every earlier key. The proposal is one group key for an epoch, as `community` has: an admission is wrapped at the seat together with one history key that opens every earlier epoch, and a removal, a resignation or a device revocation rotates. The model runs it as a third table and it holds every property, with K5 (a newcomer holds the key of every earlier write) in place of K4 (a newcomer holds no earlier epoch). Leaving out the rotation on revocation fails K8, leaving out the rotation on removal fails K2, and leaving out the history key fails K5. It is not the rule: CC 4.4.3.16 still gives a key for each write at those scopes.

**What it does not model.** The instant a writer learns of a removal: a write made before the writer holds the
removal row is under the old key, which is the exposure window of CC 5.1. Streams and their kept epochs
(CC 5.1, CC 5.3.3.7), where a late joiner and a change of `history_on_join` mid-stream are open. Who may sign a
grant (the signer gate, `tools/check_signer_gate.py`). Whether a holder of a key is served the bytes.

**To explore, with the wire work of the next edition.** A rotation today is one signed row for each recipient
device (CC 3.3.2): 150 rows and about 1.15 MB from one writer in a room of fifty members with three devices each,
some 59% of it signature. An alternative signs once over a digest of the set of wraps and delivers each device its
own wrap with a short proof of inclusion: one signature for a rotation and about 60% fewer bytes. Three things it
would have to answer, and a model should show before anyone chooses: a wrap is then admissible only once its
header is held, so two nodes holding different parts must still converge; a header is a set object, a kind the
row slot was closed against; and a header may disclose how many devices a room has. This is to be modelled as an
exploratory piece on the wire-protocol twin, the simulation in the separate CEWP repository, when that work is
reached. The twin has no key plane as a protocol today, only its load, so this is a new package there: holders,
partial delivery and the order of admission, with K1 to K9 here as its property list and the byte cost fed into
its seat and phone budgets.

Run: `python3 formal/key_plane/key_plane_model.py --check`
