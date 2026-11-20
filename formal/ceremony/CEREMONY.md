# The genesis of this edition

This edition begins a new mesh. Its genesis is a fresh genesis of the signed object of CC 2.6.1 (deterministic CBOR
under COSE). Nothing of the earlier mesh, whose rows are of the form of CC 8.11, comes across: no row of this form
names an object of the earlier form, and no object of the earlier form gives standing to anything (CC 2.6.1.12). It
is a wire break. A node that has not upgraded stays in the earlier mesh, and the two meshes share no rows.

The **ceremony row** is the first `ceg-genesis-bundle/2`, with no `prev` (CC 2.6.1.11). Every holder signs it
(CC 5.3.4). Everything else is signed anew in this form, before it where it names them and after it otherwise.

Each statement is marked **text** (the Parts say it), **model** (the check in this folder runs it), or **open**
(section 7, for the owner).

## 1. Preconditions

| Item | What must hold |
|---|---|
| The edition | 1.0-rc20 is tagged, and every implementer pins it |
| The genesis bundle | the `ceg-genesis-bundle/2` payload rule (CC 2.6.1.11); its known-answer vectors, the verifier's |
| The verifier | the composite, the row reader and the link handshake (v23.1.1, the text's pin); the bundle's payload rule; the accord invocation's composite known answer; the later bundle's count and the recovery's exception (CC 2.6.1.11) |
| The store | key liveness only by a `key:record` of this form; `canonical` as a conferral; a seat's X-Wing key only from the bundle or a counted re-bind; no migration of earlier rows |
| Edge | the composite on every producer; the mutual X-Wing handshake (`CTKX` 0x02) and seal frame 0x02, the earlier versions refused by name; a fresh X-Wing transit key per relaying node |
| The server | the route serving the bundle of this form and its object id; the holders' thumbprints as the default anchor, the object id once published |
| The agent | the composite holder signature on the halt; its own `key:record` of this form with `valid_until` |
| The holders' custody | the Ed25519 half on a token, the ML-DSA-65 half `removable_offline` on separate media (CC 4.2.3). **model** (P4): then no one device yields a halt; **model** (F7): with both halves on the token one device does. Each holder's attestation is exported fresh from that holder's own token, and the leaves name three distinct token serials (CC 4.2.3, `holder_device_shared`) |

## 2. Roles

| Role | What it signs |
|---|---|
| accord holder | its own key record; its pre-signed halt; the genesis |
| a seat's operator | from the node's own custody, offline: the node's key record and its binding carrying `transit_xwing_pubkey` |
| the steward | nothing; it tags the edition, carries the holders' thumbprints as the default anchor, and publishes the genesis's object id once it is signed (CC 5.3.4) |
| every key's holder | its own `key:record` of this form, after the genesis |
| every owner | its acceptance edge, and an owner-binding for each node and agent it owns, each cosigned by the key owned |
| every community's members | the community's founding record of this form, each signing |

No one is an authority over another's key, and no one signs another's record (CC 2.4.1.1). **model** (P2).

## 3. The steps

| # | Row | Signer and count | Names | What a node that holds it concludes |
|---|---|---|---|---|
| 1 | each holder's `key:record`, `identity_type` {`accord_holder`}, no `valid_until`, `attestation_evidence` with `hardware_class`, `pq_custody` `removable_offline` and the attestation chain | the holder | nothing | the key is live; the holders' thumbprints, the release's default anchor, now exist |
| 2 | each seat's `key:record` {`node`}, `valid_until` at most 365 days, and its `identity:occurrence` binding: `transport_destination`, with `transit_xwing_pubkey` and `onion_hop_xwing_pubkey` at the payload's top level beside it, never inside it (CC 2.6.1.4, the transport destination binding) | the seat's key, offline | the binding names the record | the seat's key is live |
| 3 | each holder's pre-signed halt, sealed | the holder | the holder's record | nothing until published; a node holding the genesis honours it then (**model**, P8) |
| 4 | **the genesis**: `ceg-genesis-bundle/2`, `version` 1, no `prev`; `holders`, `serve_nodes`, and its charter with `halt_fuse_secs` and a new `recovery_commitments` entry per holder; its count is each listed seat's canonical conferral (CC 4.2.1) | every holder (CC 5.3.4) | steps 1 and 2 | the mesh of this form exists; its roster is the holders it lists, and its seats are canonical (**model**, P3, P5) |
| 5 | the anchor: the release carries the holders' thumbprints as its default anchor, which exist from step 1; the genesis's object id is published once step 4 is signed, and a later release may carry it as the anchor | the steward | none | a node anchored by thumbprints verifies only a genesis every anchored holder signed, and two such are a fork; a node anchored by the object id holds any other genesis void (**model**, P7) |
| 6 | release and upgrade | node operators | none | the node reads this form only, and its links speak `CTKX` 0x02 only |
| 7 | every key's own `key:record` | the key | nothing | the key is live (**model**, P2) |
| 8 | each owner's acceptance edge | the owner | the genesis | the owner's nodes are Rooted and in the halt's reach |
| 9 | each owner-binding, cosigned by the key owned | owner and key | both records | a node or agent is owned; an agent acts only from here, and only with its steward's edge (**model**, P6) |
| 10 | each community's founding record, the trust-root community's among them | every member, each signing | the members' records | the community, with the members who signed |
| 11 | the first drill, within 7 days of the genesis's publication (CC 4.2.1.1) | each holder | the holder's record | shown as a drill; it rehearses the fire path. Confirmation and resumption are rehearsed on a `constitutional` halt only when one is fired, since a lifecycle row names a `constitutional` halt and nothing else |

Step 4 is published only once step 3 exists for every holder, so a halt of this form is available from the first
moment after the genesis (**model**, P8; TLA+ `Inv_HaltAvailable`; the plant `publish_ungated` is caught).

A seat's canonical standing is the genesis's own count, not a row of its own. It rides no key record, so it
survives the seat's renewals, and it moves only by a later bundle (**model**, P5: `canonical_self_claimed` and
`canonical_ends_with_record` are caught).

## 4. What each participant sees

| Participant | After the genesis |
|---|---|
| an upgraded node, online or offline through it | reads this form only; the same rows give the same answers in any arrival order (**model**, P9; TLA+ `Inv_P9`) |
| a node not upgraded | stays in the earlier mesh; its links fail at `CTKX` 0x01; it shares no row with this mesh (**model**, F1) |
| a new node | needs an anchor (the holders' thumbprints, or the genesis's object id), seeds the seats from the bundle's bindings, signs its own record |
| a person | signs a key record, edges, owner-bindings and communities anew; nothing earlier is lost from the earlier mesh, and nothing of it counts here |
| an accord holder | one composite key, live with no end; a seat on the roster by the genesis |
| an agent | no standing until its owner-binding of this form, then acts only with its owner's edge (**model**, P6, F3, F4) |

## 5. Failure and abort

Before the genesis is published, abandoning costs nothing: rows of this form bind nobody until a genesis names them,
and the earlier mesh goes on.

| Event | What happens |
|---|---|
| a holder is unavailable | no genesis can be signed (**model**, F2); the ceremony waits, or the holders re-form the roster in the earlier mesh first |
| a holder's key is lost after | the roster and its count stand (**model**, P3); the holder recovers by a later bundle signed by its recovery key alone (**model**, P11) |
| two geneses | a fork. A reader under a thumbprint anchor reports it and roots on neither: no root, so no agent runs and the node serves nothing of that mesh until its owner re-anchors it by an object id. One anchored by an object id holds the other void (**model**, P7) |
| the pin is published wrong | a node pinned to a bundle no holder signed roots on nothing; it changes its own pin |
| a key holder never signs a record | it has no standing in this mesh, and is never removed from anything by silence, since nothing of it was carried |

## 6. What the model checks

`check_ceremony.py` runs P1 to P11 over the kernel's own functions, with planted breaks, and nine findings.
`Cutover.tla` runs the interleavings under TLC. The README gives the numbers.

## 7. Open, for the owner

The ruling settles the ceremony's shape. What it does not force is listed, ranked, with a recommendation, in the
coordinator's `for_owner.md`; none is decided here.
