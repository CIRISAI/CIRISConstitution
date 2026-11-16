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
| The genesis bundle | the `ceg-genesis-bundle/2` payload rule and its vectors (CC 2.6.1.11), the verifier's |
| The verifier | the composite, the row reader and the link handshake (v23.1.1, the text's pin); the bundle's payload rule; the accord invocation's composite known answer; the accord roster objects' forward form, without which no roster change or recovery can be signed (CC 4.2.6) |
| The store | key liveness only by a `key:record` of this form; `canonical` as a conferral; a seat's X-Wing key only from the bundle or a counted re-bind; no migration of earlier rows |
| Edge | the composite on every producer; the mutual X-Wing handshake (`CTKX` 0x02) and seal frame 0x02, the earlier versions refused by name; a fresh X-Wing transit key per relaying node |
| The server | the route serving the bundle of this form and its object id; the pin or the holders' thumbprints as the anchor |
| The agent | the composite holder signature on the halt; its own `key:record` of this form with `valid_until` |
| The holders' custody | the Ed25519 half on a token, the ML-DSA-65 half `removable_offline` on separate media (CC 4.2.3). **model** (P4): then no one device yields a halt; **model** (F7): with both halves on the token one device does |

## 2. Roles

| Role | What it signs |
|---|---|
| accord holder | its own key record; the conferrals; its pre-signed halt; the genesis |
| a seat's operator | from the node's own custody, offline: the node's key record and its binding carrying `transit_xwing_pubkey` |
| the steward | nothing; it tags the edition and publishes the pin with the release (CC 5.3.4) |
| every key's holder | its own `key:record` of this form, after the genesis |
| every owner | its acceptance edge, and an owner-binding for each node and agent it owns, each cosigned by the key owned |
| every community's members | the community's founding record of this form, each signing |

No one is an authority over another's key, and no one signs another's record (CC 2.4.1.1). **model** (P2).

## 3. The steps

| # | Row | Signer and count | Names | What a node that holds it concludes |
|---|---|---|---|---|
| 1 | each holder's `key:record`, `identity_type` {`accord_holder`}, no `valid_until`, `hardware_class` and `pq_custody` | the holder | nothing | the key is live |
| 2 | each seat's `key:record` {`node`}, `valid_until` at most 365 days, and its `transport_destination` carrying `transit_xwing_pubkey` only | the seat's key, offline | the binding names the record | the seat's key is live |
| 3 | each seat's canonical conferral, the holders' statements over the seat's key record (CC 4.2.1) | every holder (a strict majority is the floor) | the seat's record | canonical standing |
| 4 | each holder's pre-signed halt, sealed | the holder | the holder's record | nothing until published; a node holding the genesis honours it then (**model**, P8) |
| 5 | **the genesis**: `ceg-genesis-bundle/2`, `version` 1, no `prev`; its charter with `halt_fuse_secs` and a new `recovery_commitments` entry per holder | every holder (CC 5.3.4) | steps 1 to 3 | the mesh of this form exists; its roster is the holders it lists (**model**, P3) |
| 6 | the pin: the genesis's object id, published with the release | the steward | none | a node with the pin holds any other genesis void (**model**, P7) |
| 7 | release and upgrade | node operators | none | the node reads this form only, and its links speak `CTKX` 0x02 only |
| 8 | every key's own `key:record` | the key | nothing | the key is live (**model**, P2) |
| 9 | each owner's acceptance edge | the owner | the genesis | the owner's nodes are Rooted and in the halt's reach |
| 10 | each owner-binding, cosigned by the key owned | owner and key | both records | a node or agent is owned; an agent acts only from here, and only with its steward's edge (**model**, P6) |
| 11 | each community's founding record | every member, each signing | the members' records | the community, with the members who signed |
| 12 | the first drill | one holder | the holder's record | shown as a drill; confirmation and resumption rehearsed at a strict majority |

Step 5 is published only once step 4 exists for every holder, so a halt of this form is available from the first
moment after the genesis (**model**, P8; TLA+ `Inv_HaltAvailable`; the plant `publish_ungated` is caught).

## 4. What each participant sees

| Participant | After the genesis |
|---|---|
| an upgraded node, online or offline through it | reads this form only; the same rows give the same answers in any arrival order (**model**, P9; TLA+ `Inv_P9`) |
| a node not upgraded | stays in the earlier mesh; its links fail at `CTKX` 0x01; it shares no row with this mesh (**model**, F1) |
| a new node | needs the pin or the holders' thumbprints, seeds the seats from the bundle's bindings, signs its own record |
| a person | signs a key record, edges, owner-bindings and communities anew; nothing earlier is lost from the earlier mesh, and nothing of it counts here |
| an accord holder | one composite key, live with no end; a seat on the roster by the genesis |
| an agent | no standing until its owner-binding of this form, then acts only with its owner's edge (**model**, P6, F3, F4) |

## 5. Failure and abort

Before the genesis is published, abandoning costs nothing: rows of this form bind nobody until a genesis names them,
and the earlier mesh goes on.

| Event | What happens |
|---|---|
| a holder is unavailable | no genesis can be signed (**model**, F2); the ceremony waits, or the holders re-form the roster in the earlier mesh first |
| a holder's key is lost after | the roster and its count stand (**model**, P3); recovery needs the roster objects' forward form |
| two geneses | a fork. A reader with no pin holds both as tips and takes only what both name; one that pinned holds the other void (**model**, P7) |
| the pin is published wrong | a node pinned to a bundle no holder signed roots on nothing; it changes its own pin |
| a key holder never signs a record | it has no standing in this mesh, and is never removed from anything by silence, since nothing of it was carried |

## 6. What the model checks

`check_ceremony.py` runs P1 to P9 over the kernel's own functions, with planted breaks, and nine findings.
`Cutover.tla` runs the interleavings under TLC. The README gives the numbers.

## 7. Open, for the owner

The ruling settles the ceremony's shape. What it does not force is listed, ranked, with a recommendation, in the
coordinator's `for_owner.md`; none is decided here.
