# `formal/mesh_net` — the replication, holding, moderation and trust-root state, model-checked

**What this is.** `INVARIANTS.md` derives the mesh's net invariants from ciris.ai/safety,
ciris.ai/constitutional-mesh and the Constitution, and says where each is checked. `MeshNet.tla`
is a TLA+ model of the holding and moderation state those invariants quantify over: who holds what,
at which scope, under whose consent; who can observe a holding claim; whether a community has a
moderator; whether a root's restriction only narrows. `RootReach.tla` is the trust root's reach over
its subscribers: the halt, un-trust, mesh_config restrictions, and what the accord may do at all.

**What it models.** Three persons, three nodes (one a server-class node of the first person), one
family, one community, one public room, the Commons, two blobs. Actions: author at a scope (posting
into the Commons or a public room runs the tripwire); replicate under the one audience rule
(CC 6.1.5.3: the owner's membership, the node's allow list, a root's restrictions, the community
federating); emit a holding claim with the audience its emitter gives it; withdraw; widen scope;
a moderator lapses (auto-promote or fail secure in the same step, CC 4.5.4); open admission to the
public room (#142); a root restricts (relieve-never-expand); the owner widens an allow list;
un-trust in one row (T3); an accord act from the closed enumeration.

**Three configurations, one module.**

| Config | Parameters | Result |
|---|---|---|
| `MeshNet_shipped_scope.cfg` | holding claims for community/public content at federation scope (persist's `holds_bytes` builder; the rc6/rc7 text) | `Inv_Invisible` violated in 4 steps: author in the room, claim, and every person can see the room's content exists |
| `MeshNet_shipped_bind.cfg` | a live holding claim folded as a content binding (persist v53, witnessed on CIRISConstitution#141) | `Inv_ClaimNotBinding` violated in 5 steps: author, claim, withdraw, and the blob is still live |
| `MeshNet_ruled.cfg` | one holding claim at the content's scope; a claim is never a binding (#141) | every invariant and action property holds: 2,013,648 distinct states, depth 18, 17 s on 8 workers |

**How it got small — by TLC's per-action coverage profile, as for `formal/trust_root`.** The first
cut ran past 73 M distinct states at depth 13 without closing. The profile ranked the producers:
`Untrust` 2.5 M, `SetAllow` 1.5 M, `AccordAct` 1.4 M, `Restrict` 1.1 M distinct states each, against
~70 k for every holding action. The trust root's reach is orthogonal to holding and was multiplying
it by its own product (subscription × halt latch × per-node restriction sets ≈ 4 000). Four
simplifications, each a reading of the text rather than a trick: (1) the reach properties are their
own module, `RootReach.tla` (9 825 states), and holding keeps one restriction bit; (2) scope is
immutable — a promotion is a new Contribution of the same bytes at the wider scope (CC 5.2), so
`Widen` is `Author` again and no node needs to remember the scope it received a blob at;
(3) `scanned` is a function of scope, not a variable; (4) a holding claim's audience is a function of
the content's scope, not of the emitting node, so one claim per blob carries every property. A
`lastAct` bookkeeping variable (×14) and the four accord acts that change nothing also went.

**Run.** `java -cp tla2tools.jar tlc2.TLC -workers auto -metadir /tmp/tlc -deadlock -config
MeshNet_<cfg>.cfg MeshNet.tla` with TLA+ tools 1.7.4; the two shipped configurations finish in
under a second, the ruled one in minutes. Always pass `-metadir`.
