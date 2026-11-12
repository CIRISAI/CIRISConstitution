# Third reading, share 2: `wire`, `registration`, `media`

Head 87c1730, branch rc19. Read-only. Findings are in `out_r3_2.tsv` beside this file (38 rows, every quote checked verbatim against the files).

## Counts

| rule key | statements read | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| `wire` | 324 (12 of them `family` scope) | 25 | 2 | 3 | 17 | 3 |
| `registration` | 60 (12 `family` scope) | 4 | 1 | 1 | 1 | 1 |
| `media` | 45 | 9 | 0 | 1 | 8 | 0 |
| total | 429 | 38 | 3 | 5 | 26 | 4 |

All three keys were finished. Limits of the reading are at the end.

## Major new findings, in full

**1. `wire`: the array kind of `consent_basis` (CC 2.1, 2.6.1.1.1, 2.6.1.7, the CDDL).**
CC 2.6.1.1.1: "A field's definition MUST declare which kind it is; absent a declaration, set-semantics (sorted) is the default." CC 2.1 defines `consent_basis` as `[* {principal, paths, attestation_id}]` and declares no kind, so by that rule it is a set, and an unsorted or duplicated array is refused `federation_set_semantics_unsorted`. The 2.6.1.7 table and `manifests/signed_object.cddl` say "array kind: sequence", kept as authored. The table applies the default in so many words to `differs_in` ("Array kind not declared in 2.4.1, so the 2.6.1.1.1 default (set, sorted) applies"), so the two rows of one table take opposite routes for an undeclared array. A door built from CC 2.1 and 2.6.1.1.1 refuses a `capacity:*` row that a door built from the table admits. The `paths` array inside each entry has no kind either. Repair: one word in the CC 2.1 row (sequence), or the table reads set.

**2. `wire`: the delivery receipt's guard on the family card (CC 5.3.3.6, 5.3.3.3, CC 8.10).**
CC 5.3.3.6 step 2: `chunk_root` MUST equal a published `SignedTreeHead.root_hash`, and "For accountable streams, "published" means **witness-cosigned**". CC 5.3.3.3 makes the witness cosign OPTIONAL and gives a best-effort stream producer-signed roots only. The card of `delivery_receipt:{stream_id}` in CC 8.10 reads: attest: `one transparency_log:cosigned:{tree_size}@admitted[…] else refuse`, and the registry describes that family as "Witness cosignature on an STH". So the card refuses every receipt on a best-effort stream, and the text admits it. CC 8.10 says a card is this document's statement of the value, so the two statements both claim to govern. Repair: the guard needs the stream's profile as its condition, or a family for the producer-signed head.

**3. `registration`: who may sign the base of a key record (CC 2.4, 3.1.3, 2.6.1.7).**
CC 3.1.3: "**Yes — self only, by possession**"; CC 2.4: "attester = the key, admitted by **proof of possession** … an anchor scrub or accord co-scrub is a cosignature". The 2.6.1.7 key-record table, on `scrub_key_id`: "Self-scrub when equal to key_id; an anchor scrub when it names a pinned anchor (the one record kind where the scrubber may differ from the subject)." Under the first, an anchor's signature is an entry of `additional_scrubs[]` beside a self-signed record. Under the second, the record's own base signature may be the anchor's, and the key never proves possession. A new record of the second shape is admitted by one reader and refused by the other. The family model's note on the cell ("pre-rc8 anchor-scrubbed base admitted") and the card ("attest: self") suggest the table is describing records already held; if so, the table's note should say that a new record is self-scrubbed.

## Known conflicts whose resolution is "to fix from the text"

- **C341** (`link_seq` per link or per link and stream): not fixed; both sentences stand in CC 5.3.3.2.5. Reported, major.
- **C342** (chunk trailer, first form or shipping form with `source_ms`): not fixed; CC 5.3.3.2.3 still lays out the v1 trailer and names v2 as shipping without its layout. Reported, major.
- **C321** (node with agent or user): fixed. CC 4.5.8.4 now carves the one pair out. Not reported.
- **C322** (fingerprint SHOULD be 16 characters): fixed. CC 2.6.8 now says ten characters at every deployment size. Not reported. The inventory row for the SHOULD is stale.
- **C324** (role held is sufficient): fixed. CC 3.4.7.1 now says holding the role is necessary and never sufficient. Not reported.
- **C343** (age-assurance rungs MAY further qualify): fixed. CC 3.4.11 now says a rung carries no further qualifier. Not reported. The inventory row is stale.

Other known conflicts met and reported with their ids: C221, C178, C169 (held), C259 (held), C224, C276 (for Eric), C315 (for Eric). Met, already settled and not reported again: C167 (FedCode kinds, the text now reads three roles and two subject kinds), C223 (the 1 MiB boundary, the text now reads "at or below"), C129, C131, C232, C264.

## The 2.6.1.7 table against its data

The table, `constitution/signed_object.tsv` (143 rows) and `manifests/signed_object.cddl` are one generation and agree member for member; I found no row where the three differ on placement, type, array kind, presence or default. The differences are between that data and the prose around it:

- `consent_basis` array kind (major, above).
- `expires_at` is not marked REQUIRED on a membership proposal in the table; CC 2.1 and 2.6.1.2 require it.
- The columns beside the row are typed `rfc3339` (any string) while CC 2.6.2 binds every datetime; the comparison rule for `typed_diverges_from_envelope` on an instant is unstated.
- `canonical-id` in the CDDL admits what CC 2.3.2.1 lists as reject vectors (another algorithm, any digest length).
- Vectors: 14 in the file. Two refusal vectors carry a description, not a token. Four cases the text says the set MUST or should hold are absent: the non-representable number, the base64-variant round trip, an explicit null, an unsorted or duplicated set. The admit vectors, the cap pair and `refuse_timestamp_form` match the text.
- `manifests/family_model.json` names a token `signed_instant_form_violation` that no Part states.

## Limits

- CC 3.1.7 (22 statements) was read against the registry's `_meta.case_rule` only, not clause by clause against `manifests/namespace_match_vectors.json`.
- `family` scope rows were compared with the family model, the transitions and the CC 8.10 cards for `key:record`, `key:revocation` and `delivery_receipt:{stream_id}`. `manifests/reactions.json` holds two entries in this share (`key:record` lapses on a key revocation or a withdrawn acceptance; `identity:occurrence` emits a hard case); neither contradicts a statement I read. There is no card or model row named for the media sub_kinds, so `media` has no data comparison beyond the `media` member of the signed object.
- The planned edition (CC 2.6.1.8) was read as planned: its differences from the present wire (CBOR, thumbprint key ids, X-Wing for every wrap, no little-endian layout) are not reported as conflicts.
- Binary layouts were checked for internal agreement (lengths, offsets, byte order, separators), not against any implementation or vector file outside this repository.
