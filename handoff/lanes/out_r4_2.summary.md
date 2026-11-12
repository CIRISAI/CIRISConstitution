# Fourth reading, share 2: `wire`, `registration`, `media`

Head 05cbcc8, branch rc19. Findings: `out_r4_2.tsv` beside this file (25 rows). Every quoted side was checked by script to be a verbatim substring of the section, card or CDDL it names.

## The three numbers

- **New major findings, text against text: 2**
- **New major findings, text against data: 2**
- **Statements opened in the text: 426 of 429. Read by gist only: 3.**

"Opened" means the paragraph that carries the statement was read in today's text. For sections under 6,000 characters the whole section was read; for longer ones (CC 2.3.2.1, 2.6.8, 3.1.3, 3.1.7, 3.2, 3.3.2, 3.3.13, 4.2.6, 5.1, 5.4.3, 5.4.6, 6.1.2.1.2 and others) only the carrying paragraphs were read, except CC 2.6.1.7, 2.6.1.8, 4.2.1.1, 5.3.3.2.3 and 3.3.14, which were read whole.

Gist only (3): `wire` CC 3.2 (geographic_constraint cell form); `registration` CC 4.4.3.4.3 (a user key's identity_type when the user is a WA) and CC 5.2 (occurrence with encryption_pubkeys required of a recipient; its twin in CC 3.3.6.1 was read).

## Per rule key

| rule key | statements | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| wire | 324 | 14 | 4 | 2 (C341, C342) | 7 | 1 (C343) |
| registration | 60 | 7 | 0 | 4 (C359, C276, C055, C266) | 3 | 0 |
| media | 45 | 4 | 0 | 1 (C315) | 3 | 0 |
| total | 429 | 25 | 4 | 7 | 13 | 1 |

Known conflicts whose fault is still in the text: C341, C342, C359, C055, C266 (all "to fix" or "proposed, not applied"), and C343 at a third site its resolution does not name (CC 4.4.3.10). C276 and C315 are open with the steward and are listed because this reading reached them on its own.

Known conflicts of these keys found repaired and not reported: C321 (CC 4.5.8.4 now names the one refused pair), C322 (CC 2.6.8 now says ten characters at every size), C037 (the CC 4.2.1.3 comment now says v2), C358/C433 as first written (the cosigned-for-every-receipt guard is gone; see the new data finding below for what replaced it).

## Major new findings in full

### 1. Is `chunk_seq` counted per epoch or per stream? (text against text; CC 5.3.3.1, 5.3.3.2.5, 5.3.3.3)

- CC 5.3.3.1: "On epoch roll the DEK changes, so a reset counter lives in a different keyspace", and the 32-bit counter's wrap is avoided by a forced epoch roll, which only helps if the counter restarts at the roll.
- CC 5.3.3.1, same section: "Substrate MUST reject a chunk-append whose `(stream_id, seq)` collides with an existing sealed chunk". CC 5.3.3.3 hashes leaves "in `seq` order" into one tree per stream with `tree_size` the chunk count.
- CC 5.3.3.2.5 ties them: the nonce counter is "the chunk's `chunk_seq`", which "MUST stay below 2³² within an epoch".

A builder who restarts `chunk_seq` at each epoch and a builder who numbers the stream once derive different inner nonces from the second epoch on (the chunk does not open), or the second refuses the first's chunk 0 of a new epoch as a collision. No sentence says which. CC 3.3.13 (`sequence_start`, HLS sequence numbers) leans to per stream. Confidence: medium; the known answers cover epoch 5, chunk 0 only, which does not separate the two.

### 2. What does an `accord:invoke` row's signature cover? (text against text; CC 4.2.1.1, 2.6.1.7)

- CC 4.2.1.1: "Every `accord:invoke:*` Contribution signs the canonical bytes below", a SHA-256 over a labelled, newline-joined field list, and "a consumer verifies ONE holder's signature over `canonical`".
- CC 2.6.1.7: "The signing input is JCS(attestation_envelope) and nothing else."

For delivery receipts and stream roots the text states two layers (CC 5.3.3.6, 5.3.3.3: the row is signed over JCS, an inner payload over its own layout). For the accord rows (invoke, CC 4.2.1.3 lifecycle, CC 4.2.6 proposal and participation) no sentence does, and the signed-object table types no member that could carry a second signature, a nonce, an invocation id or a payload digest. A halt row signed over one input fails verification under the other reading, so whether a halt fires at a node turns on it. Confidence: medium that this is an unstated layering, not two rival rules; either way the text does not let an implementer build it from one section.

### 3. A minted row's id is a SHA-256; the schema types it as a UUID (text against data; CC 3.1.3, signed_object.cddl)

- CC 3.1.3 (`identity:occurrence_revocation`): "id = sha256(domain ‖ JCS(object)); a receiver re-derives the row and refuses any byte difference". The `cosign:signature` row is likewise "sha256(`ciris-persist/cosign-signature/v1` ‖ quorum key ‖ signer key id)".
- `manifests/signed_object.cddl`: `attestation_id: uuid`, with `uuid = tstr .regexp "[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}"`; the CC 2.6.1.7 table says the id is "minted by the stamper before the bytes exist (a UUID; this edition pins no version)".

A 64-character digest does not match the pattern and is refused `envelope_member_invalid`; how 32 bytes are folded to a UUID is not stated; and the receiver refuses any byte difference. Two mints of the same framed object can therefore refuse each other. Confidence: medium (the shipped store presumably folds the digest one fixed way; the text and the schema do not say how).

### 4. The delivery-receipt guard no longer refuses an invented root (text against data; CC 5.3.3.6, CC 8.10 card, transitions.json)

- CC 5.3.3.6 step 2: `chunk_root` "MUST equal a `SignedTreeHead.root_hash` actually published" for the stream at `tree_size ≥ K`. "A phantom / self-invented root → REJECT."
- CC 8.10 card and `manifests/transitions.json`: "attest: `one transparency_log:inclusion@admitted[val:root_hash=val:chunk_root] else advise`".

This is what replaced the guard C358 and C433 faulted. The repair removed the demand for a witness cosignature on every receipt, but the guard now encodes step 3 (the recommended inclusion proof) as an advisory and nothing encodes step 2, which is a MUST with a refusal. A kernel executing the card admits a receipt over a root nobody published. Confidence: high.

## Notes outside the output format

- CC 3.2's halt row (the "CONSTITUTIONAL-level federation halt" table cell) still describes the accord as carrying a "roster-keyed asymmetry". It is no conflict between two statements, so it is not in the TSV, but it is the wording the lanes are told never to use of the halt.
- Compared and found in agreement with the text for these keys: the model cells and cards for `key:record` (self, by possession), `rendezvous:route`, `cosign:{state}`, `transparency_log:cosigned:{tree_size}`, `identity:canonical_binding:{canonical_hash}`; the CDDL's base64, hex64, key-id and array-kind typing against CC 2.6.1.1.1; `governance_policy.json` and `reactions.json` hold nothing these three keys state.
- Looked at and not reported, as resolved on a careful reading: public keys "lowercase hex" (CC 2.6.1.1.1) against the `*_base64` key members (the same clause excepts fields documented as base64); the relay "forwards as received" against "re-canonicalises" (C221, no conflict); the fingerprint check scope (C224, settled); the revocation envelope's explicit null (stated as the one exception on both sides); the v62 COSE subsection against the JSON object (different editions by its own words).

## Keys not finished

None. All three keys were read to the end.
