# `formal/key_roles` — which key signs what

**The point.** A home has up to three kinds of key: a person's roster key, a node key and an agent key. The text keeps them apart. A key is substrate or actor, and a person's or a machine's, never both (CC 3.4.7.3 Clause A, CC 3.4.7.1, CC 2.4.1.1). The node never signs as the agent and the agent never signs as the node (Clause E). A person's acts are signed by that person's roster key (CC 3.3.6.4). Shipped code has broken this axis several times:
- the agent signing as the node;
- consent read on the wrong axis;
- the MLS store keyed by the actor;
- room rows co-scrubbed by the agent;
- edge refusing every call when its signer defaulted to the agent on a two-key home.

The signer gate cannot catch these on its own. Its role tokens (`author`, `owner`, `member`, `infra:attest`, …) say who a signer is *to the row*, and never whether the key is a node's, an agent's or a person's. This model adds that axis and checks it.

**The data.** [`formal/derivation/signer_kind.tsv`](../derivation/signer_kind.tsv) gives every family transition in `manifests/transitions.json` a **signer kind**: `person`, `holder` (the accord holder's key, a person's), `agent`, `node`, `detector`, `witness`, `rendezvous`, `any-of(...)`, `by-leaf`, or `open`. Each cell names the section and the line that state it. Where a family's leaves differ, it carries leaf rows: `consent:state:{stance}` (`expired` is the node's), `membership:{stage}` and `identity:occurrence`. Uses that are not families carry `@` rows: the mesh crossing (co-scrub), the device-join request, a private room's rows, the chunk key, the content-KEM key, the transit pair, the stream binding, the MLS leaf and KeyPackage, and the identifier kept at the split.

`tools/build_key_roles.py` writes [`manifests/key_roles.json`](../../manifests/key_roles.json) from the transitions and that table. It refuses:
- a transition with no cell;
- a kind outside the vocabulary;
- a cell with no section and line;
- an open cell with no question;
- a cell that contradicts its relational tokens (`owner`, `wa`, `steward` and `winner` need a person; `holder` needs the holder key; `infra:attest`, `serve` and `identity:substrate_persist` need a node).

It checks those refusals on six plants every run. The two columns agree on all 466 transitions.

**The model.** `key_roles_model.py` covers one home in four configurations:
- **two keys:** person, node and agent;
- **two keys with an accord holder:** the same, plus the person's holder key;
- **one key:** person and node, no agent;
- **fused:** one configured key that turns out to be the actor's, so a node key must be minted beside it. This is the split.

From each configuration it explores every sequence of up to five structural acts:
- an owner-binding, cosigned or not;
- a second owner;
- the split, both ways (the configured identifier kept by the actor, or by the fresh node);
- renewal;
- revocation by the key, its owner or the node;
- a single or a rival rotation;
- the person's seed leaving the device;
- joining a private room;
- offering the agent as an occurrence of the person's identity (#871 as worded).

That is 9,461 states. In every state, every party tries every use in the manifest, and every read is asked. The uses are read from the manifest, not written in the model, and the model refuses to run if a use it names is missing.

An implementation is a set of choices: which key signs a use for a party, which key is the node, what `owner_of` returns, and so on. The correct implementation makes each choice from the text. Each plant changes one choice the way a shipped bug did.

**What is checked:**

| | Property | Text |
|---|---|---|
| R1 | no key record holds `node` with `agent`/`user`, or `user`/`accord_holder` with `node`/`agent`; no key signs both node rows and actor rows | CC 3.4.7.3 Clause A, CC 3.4.7.1, CC 2.4.1.1 |
| R2 | a node-only use (transport rows, `consent:state:expired`, the substrate self-reports, the mesh crossing) is signed by the node key; the node key signs nothing whose cell does not name `node` | CC 3.4.3, Clause E |
| R3 | a person's act (owner-binding, root acceptance, consent as the person, votes, invites' widening and removal) is signed by that person's own key, the holder's by the holder key; a machine key never signs for a person | CC 3.3.6.4, CC 3.2, CC 1.13.2 |
| R4 | an agent-only use (trace, identity amendment) is signed by the agent key; the agent key signs nothing whose cell does not name `agent` | CC 3.1.5, CC 3.3.6 |
| R5 | `owner_of` returns the one counted owner, and nothing for any other count | CC 3.2 |
| R6 | an agent acts through a node iff one human stands at both corners (Clause D), never by a node-or-its-owner rule | CC 3.4.7.3 Clause D |
| R7 | an owner-binding counts only when the owned key cosigned it | CC 3.2 |
| R8 | no machine key is admitted as an occurrence of a person's identity | CC 3.3.6 |
| R9 | the content-KEM key, the transit pair and every signing key are distinct | CC 3.3.6.1, CC 3.3.6.2 |
| R10 | in a private room every row is signed by a room key, never an identity key | CC 3.1.3.2 |
| R11 | a node or agent record states an end of at most 365 days; a person's states none | CC 2.4.1.1 |
| R12 | only the key itself, its owner or its roster revokes a key | CC 2.4.1.1 |
| R13 | which key is the node is decided by what was minted as the node, never by a configured label | CC 3.4.7.3 (no key declares itself into a duty), Clause F |
| R14 | a node or agent key with no counted owner-binding signs nothing but a device-join request | CC 3.2 |
| R15 | a rotation hands on no more than the old key held, and rival rotations hand on nothing | CC 2.4.1.1 |
| R16 | MLS group state is keyed by the room member's key (the room key in a private room, the member's own key otherwise) | **open**: for Eric (below) |
| R17 | the node is named by its node key: its public identity, its transport binding and its serve seat | Clauses A and E, CC 3.2 |

Results: R1–R15 and R17 hold; R16 is OPEN while its cell is. An R whose rule rests on a cell is reported OPEN while the cell is open, never passed. Each of the 19 plants fails the R that names it:

| Plant | Caught by |
|---|---|
| the fused configured key keeps both roles | R1 |
| edge defaults its signer to the agent | R2 |
| the mesh crossing is co-scrubbed by the engine (the agent) | R2 |
| the agent signs the trust-root acceptance | R3 |
| a machine key authors consent when no seed is held | R3 |
| the node signs the agent's trace | R4 |
| `owner_of` picks the first binding | R5 |
| edge admits only the node or its owner | R6 |
| an uncosigned binding counts | R7 |
| the agent is the owner's occurrence (#871 as worded) | R8 |
| the transit pair is the node's signing key | R9 |
| a private-room row is signed by the identity key | R10 |
| the agent's record states no end | R11 |
| the node revokes the agent key | R12 |
| `register_self_key`: the configured key is the node by its label | R13 |
| an unowned node signs node rows | R14 |
| rival rotations hand on the old standing | R15 |
| the MLS store is keyed by the node | R16 |
| the federation surface answers the agent as the node | R17 |

**The readings that close the cells the text left open.** Each is read from a rule the text does state, and each is a cell of `signer_kind.tsv` citing it. No cell is open.

| Use | Signer | Read from |
|---|---|---|
| a tally member's rows (`ballot:tally`, `census:member:partial`, `census:expected_active`) | the person: the tally member is drawn from the roster, and a count is one voice a person | CC 3.1.3 (P3:186), CC 4.5.13 |
| `custody:{kind}` | the node: what a node holds is the node's, and the report is about the device that holds it | CC 3.1.3.3 (P3:307) |
| an invitation (`membership:{stage}` proposal) | a person: an invite counts one voice a person, and an agent has no vote | CC 3.1.3.2 (P3:228), CC 4.5.13 (P4:2178) |
| an agent's `identity:occurrence` | its owner, a person; the agent voices its own possession as the occurrence role | CC 3.3.6 (P3:1821) |
| the configured key_id at the split | the actor keeps it; the node key is minted fresh. No verdict depends on it | CC 3.4.7.3 Clause F (P3:2615) |

Open, for Eric: the MLS leaf and KeyPackage (a room key per device in a private room is stated, P3:281; elsewhere the node key, as edge builds it, or the device's roster key) and the stream binding's publisher (the producing device's node key, as edge signs it, or the actor's key on that device). The text fixes neither axis, and each choice decides how edge builds rooms and calls, so they are not read here. A site that uses an open cell is reported, not passed. 

**What it found.**
- **The tokens never carried the key axis.** The signer gate's role tokens carry no key axis at all. Read alone, the 466 transitions cannot tell an agent signing a node's row from the node signing it. With the signer-kind column, the two columns agree everywhere, and every token that implies a kind (`owner`, `infra:attest`, `holder`, `serve`) meets one.
- **One breach needed a new property.** The server's measured inventory listed the federation surface answering the agent as the node's public identity. No property among R1–R16 caught it, since it is a read, not a signature. R17 closes that gap.
- **The split identifier changes no verdict.** Which key keeps the configured identifier at the split changes no verdict: every property gives the same answer under both readings. It matters to a site table, which must know which identifier its sites hold, and not to the rules.
- **The configured key can sign nothing before the split.** Before the split, a configured key whose actor status is not yet resolved may sign nothing in the node column. An implementation that registers it as `node` first fails R13 and R2 together.

**The server's measured inventory, against these properties.** The inventory is CIRISServer `release/0.5.250` at 7e41958e: 445 sites. It lives with the server (CIRISServer `formal/keys`), which checks its site table against this manifest. It is not copied here. Its five likely breaches each fail a property here:

| Site | Breach | Fails |
|---|---|---|
| `attestation_crossing.rs:120` and callers | the plain engine, the agent on a two-key home, co-scrubs the mesh crossing | R2 (`@crossing` is the node's) |
| `mesh_genesis.rs:915`, `:938` | the agent signs the trust-root acceptance | R3 (`trust:{job}` is the person's) |
| `peer.rs:1290`, `:1374`, `:1433`; `auth/consent.rs:114` | a machine key authors consent when no owner seed is held, or whatever key the request names | R3, and R2 where the node signs |
| `federation_surface.rs:137`, `:162` | the agent answered as the node's public identity | R17 |
| `compose.rs:4190` `register_self_key`, `node_key.rs:1072` | the configured key registered as `node` before the split resolves | R13, with R2 |

**The inventory's use vocabulary, mapped to the manifest:**

| Inventory `use` | Manifest use or read | Property |
|---|---|---|
| `registration`, `renewal` | `key:record` | R1, R11, R13 |
| `signs:revocation`, `revoking_key_id` | `key:revocation` | R12 |
| `co-scrubs`, `co-scrubs consent into mesh` | `@crossing` (node) | R2 |
| `authors-consent` and its variants, `signs:consent withdrawal` | `consent:state:{stance}[granted\|revoked]` (the subject, person or agent), `consent:community_trust` (person), `consent:replication` (node or person), `consent:state[expired]` (node) | R3, R2 |
| `signs:trust-root acceptance` (as owner, as node), `signs:trust:accepts`, `signs:delegates_to trust acceptance` | `trust:{job}:{version}` (person) | R3 |
| `signs:owner-binding …`, `signs:<owner rows>`, `signs:owner requests`, `signs:delegates_to` | `ownership:*`, `self:delegates_to` (person) | R3, R7 |
| `owner-binding-subject`, `directory-lookup-subject` | the reads `owner_of`, `is_steward_bound` | R5 |
| `signs:identity occurrence`, `signs:occurrence label`, `signs:occurrence revoke`, `signs:evict_device`, `signs:evict_actor` | `identity:occurrence[user\|node\|agent]` (agent: the owner), `device:label` (person), `identity:occurrence_revocation` | R8, R3 |
| `signs:invite proposal`, `signs:family invite`, `signs:pair join intent`, `signs:pair-room founding/proposal` | `membership:{stage}[proposal]` (person) | R3 |
| `signs:invite reply`, `signs:… acceptance widen`, `signs:membership widening`, `signs:member removal`, `signs:leave` | `membership:{stage}[acceptance\|decline\|resignation]` (the invitee), `[widening\|removal]` (person) | R3 |
| `signs:room rows`, `signs:self room actor half`, `signs:room epoch`, `signs:… DEK rewrap`, `signs:self-DEK rekey`, `signs:group-content …` | `@room_row` (room key, in a private room); `key_grant:{axis}` | R10 |
| `mls-leaf/store-key`, `mls`, `signs:KeyPackage` | `@mls_leaf`, `@mls_keypackage` (open) | R16 |
| `transport-occurrence`, `signs:transport`, `route-publish`, `signs:node_proof`, `sign as node` | `transport:{kind}` (node), `@transit_pair`; the read `node_identity` | R2, R9, R17 |
| `call-attendee` | the read `may_act_through` (Clause D) | R6 |
| `call-row`, `call chunk-key-binding` | `@stream_key_binding` (open), `@chunk_key` | open |
| `holding claims`, `signs:holding-claim withdrawals` | `custody:{kind}` (node) | R2 |
| `health/telemetry label` | the read `node_identity` | R17 |
| `audience/self-check`, `audience`, `cache key`, `store key …` | a set of "own keys" never mixes the node key with an actor's | R1, R17 |
| `cli/config`, `signs:config:*` | `config:{scope}` (node or person) | R2, R3 |
| `engine signer`, `signs:<any>`, `signs:<caller's row>` | none: an unlabelled signer has no kind until resolved | R13 |
| `signs:deferral:request`, `signs:deferral response` | `deferral:request`, `deferral:response:{outcome}` (person or agent) | R3, R4 |
| `signs:identity:amendment`, `signs:trace receipt` | `identity_amendment`, `trace:{form}:{version}` (agent) | R4 |
| `signs:ballot`, `signs:objection`, `signs:community roster rows`, `signs:seat roster cosignature`, `signs:roster …`, `signs:change co-sign…` | `ballot:*`, `objection:{state}`, `group:roster`, `cosign:{state}` (person, or person and agent for `cosign`) | R3 |
| `signs:chat message`, `signs:message revision`, `signs:file rows`, `signs:detached object…`, `signs:family rows`, `signs:community founding…`, `signs:dissolve`, `signs:commons conduct rows`, `signs:content_class flag`, `signs:location proof`, `signs:session claim`, `signs:moderation …`, `signs:takedown decision`, `signs:quarantine marker`, `signs:watchlist…`, `signs:appeal decision`, `signs:role change`, `signs:admin …`, `signs:scores de-admission`, `signs:remote claim`, `signs:capacity score`, `signs:age assurance`, `signs:mesh_config subscription row`, `signs:reserved-prefix rows` | the family's own cell: content and seat-holder rows are an actor's (person or agent), never the node's; `mesh_config` is the person's; `capacity`, `age_assurance` and the machine claims may be any key | R2, R3, R4 |

**Where it sits.** This is one of the last pieces of the end-to-end model:
- `formal/owner_binding` says who owns a key, over every order of arrival.
- `formal/key_plane` says who holds which content key.
- The signer gate (`tools/check_signer_gate.py`) says which relation a signer must stand in.
- `formal/mesh_life` tells the life of a mesh as one closing story.
- The server's `add_device` (vendored at [`vendor/server/add_device`](../vendor/server/add_device/)) checks the second-device join.

None of them says which *kind* of key stands in the relation. This model does, over the same transitions manifest, so the story's rows, the gate's relations and the owners' bindings are now held to the key that may sign them.

**What it does not model.**
- **Order:** the order of arrival is owner_binding's and the self roster's.
- **Cryptography:** keys are names.
- **Leaf vocabularies:** a family whose leaves differ is split only where the text gives leaf rows (`consent:state`, `membership`, `identity:occurrence`). Other families take one kind for every leaf.
- **Subjects:** for the consent stance, "an agent only as the data subject itself" is a subject rule. The cell gives `person` or `agent`, and the subject check is the signer gate's.
- **The machine roles:** detector, witness and rendezvous keys are held only by the generator's table and the reserved-emitter refusals. The model's home has none.

Run: `python3 tools/build_key_roles.py --check` and `python3 formal/key_roles/key_roles_model.py --check`.
