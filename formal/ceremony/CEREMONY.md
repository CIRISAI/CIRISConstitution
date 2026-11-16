# The edition-2 ceremony

The ceremony moves the mesh from the earlier signed object (JSON over JCS, CC 8.11) to the signed object of
CC 2.6.1 (deterministic CBOR under COSE). It happens once. It is a wire break: the ceremony and the implementers'
release that reads the new form are one event, and a node that has not upgraded is off the mesh afterwards. There is
no coexistence protocol.

The **ceremony row** is the first `ceg-genesis-bundle/2` (CC 2.6.1.11). The **cutover** is that row's causal past,
never a log position or an instant (CC 2.6.1.12). After it, an earlier-form object is accepted only in that past.

Each statement below is marked **text** (the Parts say it, with the section), **model** (the check in this folder
runs it), **derived** (it follows from text and rulings, and a proposal in `TEXT_PROPOSALS.md` states it), or
**open** (listed in section 8 with options and a recommendation).

## 1. Preconditions

Nothing is signed until every line below holds. Abandoning before the ceremony row costs nothing (section 6).

### 1.1 The text

| Item | What must hold | Status |
|---|---|---|
| The edition | 1.0-rc20 is tagged, and every implementer pins it | open: not tagged |
| The acknowledgement family | the family of the row that carries a scope over, with its `carried` root (CC 2.6.1.12) | open: "waits on its owner's submission" |
| The scopes carried | which scopes the ceremony carries, and who acknowledges each | open (8, item 1) |
| The genesis bundle of this form | the `ceg-genesis-bundle/2` payload rule and its vectors (CC 2.6.1.11) | open: the verifier's |
| The revocation snapshot | the `ceg-revocation-snapshot/2` payload rule and its vectors | open: the verifier's |
| The cutover proof | its vectors (CC 2.6.1.12) | open: the verifier's |
| The accord's roster objects | the forward form of `accord_proposal`, `accord_participation`, `accord_decision` (CC 4.2.6) | open: without them no roster change and no recovery can be signed after the cut |

### 1.2 The implementers' releases

Each release below must be built and tested before the ceremony row is signed. Each must also be able to take the
pin of section 3, step 9, without a rebuild, or must anchor on the holders' composite thumbprints (CC 5.3.4 allows
either anchor). The anchors are taken from the issues and tags read for this page; nothing here was built.

| Implementer | Release | What it must contain for the ceremony |
|---|---|---|
| verifier | v23.1.1 or later (v23.1.3 is the newest tag) | the composite (v23.0.0); row statements, substrate objects, recovery refusals, stream key binding, link handshake and seal vectors (v23.1.1, the text's pin); **owed before the ceremony**: the bundle and snapshot payload rules, the trust root on edition 2, the cutover proof, the accord invocation's composite holder signature known answer, the roster objects' forward form, the login contract's encoding, the edition-2 bindings for the agent |
| kernel crate | `kernel-v0.1.0` or later | the five departures persist accepted, and the sixth (a delegation cycle visited once) listed; `key_end` as a conclusion (`well_formed`, `conclude_rule`, `live`, `ended`, `retained`) |
| store (persist) | v62, its second wave (the edition-2 wire) | key liveness only by a forward `key:record`; holders' records carried by holders; `canonical` as a conferral, not a type; the wider identity-set exclusion on every door, the replicated insert included; `cosign:{state}` by row id; the five recovery sentences against the verifier's vectors; forks held as tips; a seat's X-Wing key live only by an admitted re-bind (persist's own finding); the acknowledgement row and its `carried` root |
| edge | the refactor cut on verify 23 | every forward producer on the composite (Welcome, stream tree head, receipts, `StreamKeyBinding` v2 with `profile`); the mutual X-Wing handshake of CC 5.3.3.10 (`CTKX` 0x02) and the seal frame 0x02; `CTKX` 0x01 and frame 0x01 refused by name; a fresh X-Wing transit pair per relaying node, never regenerated once published |
| server | the release that bundles the three above | `GET /v1/trust-root/bundle` serving the bundle of this form and its object id outside `bundle`; the pin or the holders' thumbprints baked in; the boot manifest's payload rule |
| agent | the release on the verifier's edition-2 bindings | the composite holder signature on `accord:invoke` and `accord:lifecycle:*`; its own `key:record` of this form with `valid_until`; the text manifest statement as a row; the latch read before every effectful act, unchanged |

### 1.3 The holders' custody

Each accord holder holds the Ed25519 half of its composite key on a token and the ML-DSA-65 half `removable_offline`,
on separate media (CC 4.2.3, CC 4.2.2.1). **model** (P4): with that custody no one device yields a halt. **model**
(F11): a holder that carries over the same two halves, where the earlier key ever held both on one device, leaves one
device that yields a halt. Such a holder rotates to fresh halves (section 3, step 2). **derived**.

## 2. Roles

| Role | Who | What it signs in the ceremony |
|---|---|---|
| accord holder | each of the three persons of CC 4.2.3 | its own key record; the re-binds; the conferrals; the acknowledgements (option); the ceremony row; later, halts, confirmations, resumptions, drills |
| the steward | the steward of CC 4.5.1 | nothing in the ceremony. It tags the edition and publishes the pin with the release (CC 5.3.4) |
| the canonical's operator | whoever operates a seated serve node | from the node's own custody, offline: the node's key record of this form and its `transport_destination` of this form; it mints the X-Wing transit key |
| node owner | every person who owns a node | the node's acceptance edge again (option); owner-bindings where the earlier one is not carried |
| key holder | every key: person, node, agent, store | its own `key:record` of this form, naming its earlier record |
| a steward of an agent | the owner its owner-binding names | the forward owner-binding, where the earlier one is not carried; the agent cosigns |

Nobody is an authority over another's key. The ceremony ends no key and gives no key a power over another
(CC 2.4.1.1). **model** (P2).

## 3. The steps, in order

The order is what each row names. Two steps with no name between them may be signed in any order.

| # | Row | Form, family | Signer and count | Key and custody | Names (`refs`) | What a node that holds it concludes |
|---|---|---|---|---|---|---|
| 1 | Release candidates | none | the implementers | none | none | nothing: software with the forward rules and a pin slot |
| 2 | Each holder's key record | this form, `key:record`, `identity_type` {`accord_holder`}, no `valid_until`, `hardware_class` and `pq_custody: removable_offline` in `attestation_evidence` | the holder, one statement; a rotation also carries the earlier key's signature | composite, halves on token and offline media | the holder's earlier `key:record`, by its earlier-form name (CC 2.6.1.3) | the key is live in this form; it speaks for the same person as the earlier key (open, 8 item 2) |
| 3 | Each seat's re-bind | earlier form, `transport:canonical_rebind:v1`, carrying the earlier pair and `transit_xwing_pubkey` | the holders, counted, a strict majority of the standing roster; once per seat | earlier hybrid keys | the seat's earlier binding | a node of the earlier form stores and serves it and reads nothing new; an upgraded node takes the X-Wing key only once the row is in the ceremony's past (model, F4) |
| 4 | Each seat's key record and binding | this form, `key:record` {`node`} with `valid_until` ≤ 365 days; `transport_destination` carrying `transit_xwing_pubkey` only | the seat's key, signed offline from custody | composite, the node's custody | the seat's earlier `key:record`; the binding names the record | the seat's key is live; the binding's X-Wing key must equal the re-bind's (model, F5) |
| 5 | Each seat's canonical conferral | this form, the accord's statements over the seat's key record payload (CC 4.2.1) | the holders, counted, a strict majority | holders' composite keys | the seat's key record of this form; the accord's head | the seat holds canonical standing in this form; the earlier conferral stands only for rows in the past |
| 6 | The acknowledgement of each scope carried | this form, family open | open (8 item 1) | composite | its signer's key record | nothing alone; it counts only when the ceremony row names it |
| 7 | The revocation snapshot | `ceg-revocation-snapshot/2`, `seq` 1 | one signer, its `author` | composite | `prev` none; under `also` role `ack`, its acknowledgement of the revocation scope; each entry the revoked key's thumbprint, its revocation and the rows it held good | the revoked keys, as a set with no winner across issuers |
| 8 | **The ceremony row** | `ceg-genesis-bundle/2`, `version` 1 | every holder (open, 8 item 3), one statement each | composite | `prev`: the earlier bundle, by the SHA-256 of its `authorization_digest`; the holders' key records; the seats' key records and bindings; the conferrals; the re-binds; under `also` role `ack`, every acknowledgement and the snapshot | the cut: the earlier form is accepted only in this row's past |
| 9 | The pin | none: published text | the steward, with the release | none | the ceremony row's object id (CC 2.6.1.11) | a node that holds the pin acknowledges this ceremony row, and holds any other void (model, P6) |
| 10 | Release and upgrade | none | node operators | none | none | the node reads both forms and writes this one; `CTKX` 0x01 is refused, so it speaks only to upgraded peers |
| 11 | Each key's own record | this form, `key:record` | the key itself | composite, the holder's custody | its earlier record, by its earlier-form name | the key is live in this form (model, P2); a node or agent record states `valid_until` of at most 365 days |
| 12 | Each owner's acceptance edge | this form, the acceptance of CC 3.2 T3 | the owner | composite | the ceremony row | the node is Rooted on the bundle of this form, and in the halt's reach (model, F9; open, 8 item 4) |
| 13 | Owner-bindings and steward-bindings | this form, an owner-binding cosigned by the key owned | owner and key | composite | both key records | needed only where the earlier binding is not in the past (model, F14), or on handover |
| 14 | A community's next act | this form, a roster version or any counted act | counted over the members at the head it names, by person | composite | the community's earlier head, by its earlier-form name | the community continues; nothing is carried by anyone (section 4) |
| 15 | Sealed halts again | this form, `accord:invoke:constitutional`, pre-signed, kept sealed | each holder, one | composite | the holder's key record | a sealed earlier-form halt published after the ceremony row is refused (model, F2); the earlier sealed rows are destroyed |
| 16 | The first drill | this form, `accord:invoke:drill:{drill_id}` | one holder | composite | the holder's key record | shown as a drill; then a confirmation and a resumption are rehearsed at a strict majority |

Steps 2 to 7 come before step 8, since step 8 names them. Step 3 is of the earlier form, so a node of the earlier
form can store it. Steps 11 to 16 come after step 8 and may run in any order among themselves.

### 3.1 The quiet point

An earlier-form row signed after its scope's acknowledgement, and not in the ceremony row's past, counts until a node
holds the ceremony row and never after (model, F3). Its signer signs it again in this form. So between step 6 and
step 8, a writer of the earlier form SHOULD write nothing it cannot sign again. **derived**.

## 4. The causal structure

| Row | Names |
|---|---|
| holder's key record (2) | the holder's earlier key record |
| seat's re-bind (3, earlier form) | the seat's earlier binding (by the earlier form's own reference, which is no name of this form) |
| seat's key record (4) | the seat's earlier key record |
| seat's binding (4) | the seat's key record of this form |
| conferral (5) | the seat's key record of this form; the accord's head |
| acknowledgement (6) | its signer's key record; `carried`: the root over the scope's earlier-form names |
| revocation snapshot (7) | its acknowledgement of the revocation scope; each revocation and the rows each held good |
| ceremony row (8) | the earlier bundle (`prev`); 2; 4; 5; 3 (by earlier-form name); 6 and 7 (`also` role `ack`) |
| a key's own record (11) | the key's earlier record (accepted only if that record is in the ceremony's past) |
| acceptance edge (12) | the ceremony row |
| owner-binding (13) | the owner's and the key's records of this form |
| a community's next act (14) | the community's earlier head |
| halt, drill (15, 16) | the holder's key record |

An earlier-form object names nothing by digest, so a chain enters the earlier form only at its last hop. An earlier
row that a carried earlier row refers to, and that no `carried` root holds, is outside the past (model, F1). So a
scope's `carried` root lists every earlier row of the scope, not only its heads. **derived**.

## 5. What each participant sees

| Participant | Before the ceremony row | After |
|---|---|---|
| an upgraded node online at the ceremony | reads both forms; every earlier row counts | holds the ceremony row once it holds what it names; earlier rows outside the past stop counting; it dials seats by their X-Wing keys |
| an upgraded node offline through it | as above, with the earlier rows it holds | on return, receives the ceremony row late and reaches the same answers as a node online throughout, once both hold the same rows (model, P9; TLA+ `Inv_P9`) |
| a node not upgraded | reads the earlier form | cannot read the ceremony row; its links fail at `CTKX` 0x01; it is off the mesh (model, F12) |
| a new node joining after | none | needs the pin or the holders' thumbprints; seeds the seats from the bundle's bindings; signs its own record of this form |
| a person with one phone | a `user` key; the phone is a client-only initiator | signs one key record of this form naming the earlier one; its memberships and bindings in the past carry by person (open, 8 item 2) |
| an accord holder | an earlier hybrid key | one composite key (step 2), live with no end; its voice is the same person's (model, P7) |
| an agent and its steward | an earlier owner-binding | the agent signs a record of this form with `valid_until`; its steward of record continues if the earlier binding is in the past (model, P8); it may act only with its steward's acceptance edge in force (model, F9) |
| a key that never re-registers | its earlier record | no row it signs after counts; nothing in the past is lost; it is never removed by silence (model, P3) |

## 6. Failure and abort

**Before the ceremony row.** Every earlier row still counts, and no node concludes a cut. Rows of this form already
signed (steps 2, 4 to 7) bind nobody: a key record of this form makes its key live, and nothing else reads it.
Abandoning means not signing step 8, and the releases keep reading the earlier form. Step 3 rows stay as earlier-form
rows that a node of the earlier form never reads. Nothing is withdrawn and nothing needs to be.

**After it.**

| Event | What happens | Remedy |
|---|---|---|
| a holder's key is unavailable before step 8 | with every holder required, step 8 cannot be signed (model, F7) | wait, or the holder recovers in the earlier form first; open (8 item 3) |
| a holder's key is lost after step 8 | its key of this form ends nothing else; the roster and the count stay (model, P7) | recovery by the holder, which needs the roster objects' forward form (1.1) |
| a seat's re-bind is missing from the past | the seat has the bundle's binding only; with neither, no X-Wing key, and no upgraded node can dial it (model, F4) | a re-bind of this form by the holders' count |
| the bundle's binding and the re-bind differ | the seat has no key in force until a row names both (model, F5) | a re-bind of this form naming both |
| two ceremony rows | a fork. A reader with no pin holds both as tips and accepts only the earlier rows common to both pasts. A reader that pinned one holds the other void (model, P6) | the pin; a later bundle naming both cannot undo what the pins chose (open, 8 item 5) |
| the pin is published wrong | a node pinned to a bundle no holder signed accepts no bundle; one pinned to the other fork row holds the ceremony row void | publish again; each node changes its own pin (open, 8 item 6) |
| a key holder never re-registers | no row it signs after counts, and nothing it held in the past is lost (model, P3) | none needed |
| a halt is fired in the window | an earlier-form halt fired after the acknowledgement stops counting at the ceremony row (model, F15). A node that latched it keeps the latch until a counted resumption (TLA+ `Inv_LatchOnlyByResume`) | a resumption of this form naming it by id (open, 8 item 7) |
| a resumption counted on an earlier-form statement before the ceremony row | its count falls when the ceremony row arrives, after the latch already cleared (TLA+ `Inv_ResumeStable` fails) | holders sign resumptions in this form only, from step 2 on (derived) |

## 7. What the model checks

`check_ceremony.py` runs the properties P1 to P9 over the kernel's own functions, each with planted breaks that it
must catch, and fifteen findings computed from runs. `Cutover.tla` runs the interleavings of P1, P2, P7 and P9 and
three halt invariants under TLC. The README gives the numbers.

## 8. Open details

Ranked by how much of the ceremony each blocks. Each names the sections that bear on it, the options, and a
recommendation. None is decided here.

1. **Which scopes the ceremony carries, and who acknowledges each.** CC 2.6.1.12 names "each scope", and only the
   revocation scope is named (CC 2.6.1.11). An earlier row in no carried root is lost after the cut (model, F1, F3).
   Options: (a) the stores the canonical seats hold; (b) every community acknowledges its own scope before step 8;
   (c) a later bundle of this form may carry further scopes. Recommendation: (a) for federation-scope rows, plus (b)
   for each community that wants its history; (c) needs a ruling, since it widens the past after the pin.
2. **How a key of this form speaks for an earlier key.** CC 2.4.1.1 says a holder "carries the key over" and
   CC 2.6.1.7 changes the displayed identity at the ceremony. No sentence says a reader treats the composite key as
   the earlier key, so rosters, seats and owner-bindings in the past bind it. Options: same halves; a rotation naming
   the earlier record; both. Recommendation: both, by the record naming the earlier record (model, P7, P8;
   `no_continuity` breaks P8).
3. **The ceremony row's count.** CC 5.3.4 has a fresh genesis signed by every holder and an amend at M. The ceremony
   moves the signed bytes, so it is no amend. Options: every holder (a holder can block); a strict majority (an absent
   holder's recovery commitment cannot be restated by others). Recommendation: every holder (model, F7), since only
   each holder restates its own commitment (CC 5.3.4).
4. **The acceptance edge after the cut.** An earlier edge in no carried root stops counting, and with it the node's
   reach by the halt and its agents' capability (model, F9). Options: carry every edge; each owner signs again
   (step 12). Recommendation: each owner signs again, naming the ceremony row; until then the node's agents may not act.
5. **A fork of the genesis.** CC 2.6.1.11 reports a fork and holds tips. The text does not say what "the ceremony
   row's past" is under two tips. Recommendation: the earlier rows common to both pasts (model, P6), as a roster's
   members are those common to its tips (CC 2.7.8).
6. **Correcting a wrong pin.** CC 5.3.4 makes the pin an out-of-band anchor. Nothing says how a node replaces one.
   Recommendation: the node's own act, as any acknowledgement is its own.
7. **A halt in the window.** CC 4.2.1.1 makes the halt pre-signable and latched until a named resumption. CC 2.6.1.12
   refuses its earlier-form row outside the past. Recommendation: the latch stands, and a resumption of this form
   counts by `resumes_halt_id` against a halt of either form (TLA+ `Inv_NoStranded`; the strict reading strands the
   latch).
8. **An earlier-form sealed halt.** It is refused after the cut (model, F2). Recommendation: each holder re-seals in
   this form before step 8 and destroys the earlier rows; CC 4.2.1.1 says so (proposal).
9. **The X-Wing key from an earlier-form row.** A seat alone can publish an earlier-form binding carrying a new
   X-Wing key, and the store admits it (persist's run on v61). Recommendation: an upgraded node takes a seat's X-Wing
   key only from a counted re-bind or the bundle's binding (model, P5 plant `seat_alone_td`).
10. **The bundle's binding against the re-bind.** Both are authorised by the holders' count. The text does not
    require them to agree. Recommendation: they carry the same key, or the seat has none (model, F5).
11. **An owner's revocation of a key it owns.** CC 2.4.1.1 lists three revokers, the owner among them, then says no
    row of another key enters the liveness reading (model, F13). Recommendation: the liveness reading names the
    three revokers.
12. **The recovery commitments.** CC 4.2.6 keys them by `holder_key_id`, which changes at the ceremony. Options:
    restate the same commitments under the composite thumbprints; new ones. Recommendation: restate, in the bundle's
    charter; the commitment binds the recovery key's two public halves, whatever the encoding.
13. **The roster objects' forward form.** Until it exists no accord roster change and no recovery can be signed after
    the cut (CC 4.2.6). Recommendation: a precondition of step 8.
14. **The thumbprint of an earlier revoked key in the snapshot.** CC 2.6.1.11 names "the revoked key's thumbprint".
    Recommendation: the composite thumbprint computed from its two halves, so a later record of those halves is caught
    (model, F10).
15. **The lineage heads in the bundle.** CC 5.3.4 makes the accord's family record and the canonical birth record
    members of the bundle. Recommendation: the earlier records, named by the ceremony row, with the next versions of
    this form naming them.
16. **A row concurrent with the ceremony row that had an effect.** A node may have acted on an earlier row later
    outside the past (model, F3). Recommendation: no irreversible effect on an earlier row signed after its scope's
    acknowledgement; the quiet point (3.1).
17. **A holder that both carries and rotates.** It has no voice until a row names both keys (model, F6; CC 2.4.1.1).
    Recommendation: the procedure says one path per holder.
18. **The overlap rule at the cut.** CC 5.3.4 keeps a seat's pinned pair until its replacement is Rooted on every
    node. Under the wire break the earlier pair is refused everywhere at once. Recommendation: the rule reads within
    one handshake.
19. **An agent whose steward never re-registers.** It keeps its steward of record, which can sign nothing forward
    (model, F8). Recommendation: none needed in the ceremony; CC 7.5.5 handover applies once the steward returns.
20. **A community with no carried history.** Its earlier rows count nowhere after the cut. Recommendation: its members
    found it again in this form, each signing (CC 3.1.3.2).
21. **The release order.** The pin is known only after step 8. Options: release with a pin slot, then publish;
    anchor on the holders' thumbprints, known after step 2. Recommendation: both.
22. **The steward's role.** The text names none in the ceremony. Recommendation: none beyond publishing the pin.
