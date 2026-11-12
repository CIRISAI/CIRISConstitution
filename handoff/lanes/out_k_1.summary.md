# Lane K, share 1: summary

Six rule keys, 538 statements read (every row of the inventory under each key; the `family`-scope rows read as context and reported on where they are the home of the rule, as for the halt). 43 findings: 12 major (8 new, 4 known), 31 minor (26 new, 5 known).

| rule key | statements (of which family scope) | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| `wire` | 324 (11) | 17 | 3 | 1 | 10 | 3 |
| `content_ingestion` | 59 (28) | 7 | 2 | 0 | 5 | 0 |
| `halt` | 61 (40) | 8 | 1 | 3 | 3 | 1 |
| `placement` | 52 (37) | 5 | 0 | 0 | 5 | 0 |
| `accord` | 36 (22) | 5 | 2 | 0 | 2 | 1 |
| `other:client` | 6 (0) | 2 | 0 | 0 | 2 | 0 |

Known ids met: C033, C036, C039, C040, C169, C178, C221, C224.

## Major new findings

**1. `wire` (scope), CC 5.3.3.2.5**

- A: CC 5.3.3.2.5 `link_seq` is `u64` **big-endian** and monotonic per RNS Link (transit replay guard).
- B: CC 5.3.3.2.5 `link_seq` is a per-`(link, stream)` counter both ends keep and is never carried in the frame
- The outer nonce is SHA-256(label, link_id, link_seq) with no stream id in it. One counter per link gives distinct nonces across the streams of a link; one counter per (link, stream), each starting at 0, gives two streams on one link the same outer nonce, and a receiver built the other way cannot open. The nonce formula supports per link; the loss-recovery paragraph is written per (link, stream).

**2. `wire` (condition), CC 5.3.3.2.3**

- A: CC 5.3.3.2.3 is a 64-byte Ed25519 signature by the bound chunk key, appended to the inner unit after the inner ciphertext and inside the outer seal
- B: CC 5.3.3.2.3 the shipping form, which precedes the signature with an 8-byte publisher timestamp `source_ms` under the domain `ciris-edge:av-chunk-sig:v2`
- One sentence lays out the v1 trailer (64 bytes, domain av-chunk-sig:v1) and says the shipping form is another (72 bytes, domain v2, budget eight bytes lower) without laying it out. The relay rule still reads "take the last 64 bytes as the trailer". An implementer of the written layout and one of the shipping form refuse each other's chunks as av_chunk_trailer_invalid. CC 2.6.1.8 only says the trailer stays a raw signature.

**3. `wire` (exception), CC 3.4.11,3.1.7**

- A: CC 3.4.11 are the only shapes this Part registers
- B: CC 3.4.11 provider/government rungs MAY further qualify `{level}` with a `{verifier_key}` / `{credential_class}`
- Same sentence. The registry and the match vectors carry only age_assurance:{level}:{band}:{version}; age_assurance: is a reserved stem, so CC 3.1.7 refuses an unclaimed leaf under it as namespace_family_unregistered. A producer using the MAY emits a row every conformant substrate refuses. The registry supports "only two shapes".

**4. `halt` (condition), CC 4.2.1.1,4.2.1.3**

- A: CC 4.2.1.1 The latch is idempotent, so a replayed or second row changes nothing.
- B: CC 4.2.1.3 A resumption authorizes ending a *single named* `constitutional` halt, not resumption-in-general.
- Two holders fire two halts (two ids) for one emergency. Under 4.2.1.1 the second row changes nothing: one latch, the first id, the first fuse. Under 4.2.1.3 and the confirmation rule ("names the halt by id") each halt is its own object. If the majority confirms the second id, a single-latch node sees a confirmation of a halt it never latched and lapses at the first fuse; a per-halt node stays paused. Likewise a resumption of the first id frees a single-latch node and leaves a per-halt node paused under the second. Neither section says which halt is "the currently-active" one when two have arrived.

**5. `accord` (exception), CC 4.2.1,3.4.1,3.1.1**

- A: CC 4.2.1 Humanity-accord authority signs nothing outside this enumeration.
- B: CC 3.4.1 The accord-holder verdict on an agent's human-dignity conduct, carried as `accord:human_dignity:v1` (`attested_key_id` = the agent scored)
- The enumeration of CC 4.2.1 holds neither accord:human_dignity nor the accord heartbeat accord:lifecycle ("accord-holder self-attestation about the accord", CC 3.4.1); both are registered leaves only an accord_holder may emit, and transitions.json admits each on one holder's act. A verifier built from 4.2.1 refuses them as out of role; one built from the registry admits them. C051 records the same gap for the roster-change objects of CC 4.2.6.

**6. `accord` (actor), CC 4.2.3,4.5.1**

- A: CC 4.2.3 name the three holders' hybrid keys (Ed25519 + ML-DSA-65), one per person
- B: CC 4.5.1 a holder's primary and backup keys are one holder, under whichever of their keys is live
- CC 4.2.3 seats one key per holder; CC 4.5.1 counts a holder under a primary or a backup key. No section says how a backup key is seated, pinned in the bundle or recognised by a verifier, and CC 4.2.6 gives recovery by a pre-committed rotation, never a standing second key. A halt or a sign-off signed by a backup key is honoured under 4.5.1 and refused under 4.2.3.

**7. `content_ingestion` (condition), CC 3.1.3.4,1.13.3.4,4.5.7,4.5.13**

- A: CC 3.1.3.4 The perceptual-hash tripwire likewise fires at every scope-widening promotion
- B: CC 4.5.7 Detection runs **only at the publish/share seam of enabled groups**
- CC 1.13.3.4 and 3.1.3.4 make the tripwire unconditional at every widening; CC 4.5.7 makes the matcher an opt-in the group's moderate-holder enables per group, on a hash list the operator provisions, and CC 4.5.13 repeats "only at enabled groups' publish/share seam". A promotion into a group that has not enabled a list is hash-matched under the first and not under the second. Neither says whether the CSAM list is the always-on case.

**8. `content_ingestion` (scope), CC 1.13.3.4,3.2,3.1.3.4**

- A: CC 1.13.3.4 **substrate-protective perceptual-hash tripwire at every scope-*widening* promotion event**, never on the device, never inside a private cohort
- B: CC 3.2 runs on the post exactly as it runs on a promotion into the Commons — never inside a private cohort, never on the device
- A widening from self to family, or from family to a gated community, is a scope-widening promotion that lands inside a private cohort. "Every widening" (CC 3.1.3.4: "Every widening is an act on specific bytes ... each with its own emission and tripwire") matches it; "never inside a private cohort" and the next sentence of 1.13.3.4 (only a promotion into the Commons or a post into a public room is matched) do not. The Commons-or-public-room reading is the one the privacy position supports.

## How the keys were read, and what was not finished

- **`wire` (324).** Every statement was read as its gist and entry phrase. The sections were then read in full wherever the rule is stated in more than one place: CC 2.6.1 to 2.6.1.6, 2.6.1.8, 2.6.2, 2.6.3, 2.6.6, 2.6.8, 2.3.2.1, 3.1.7, 3.3.2 (wrap vocabulary), 3.4.11, 4.4.3.4.3.1, 5.1 (first half), 5.3.2.4.2, 5.3.2.5, 5.3.3.1, 5.3.3.2.1 to 5.3.3.2.5, 6.1.1 to 6.1.3. Statements with a single home and no restatement (the reject vectors of 2.3.2.1, the FedCode layout, the scope-privacy derivations of 5.4.1 to 5.4.6, the preimages of 6.1.5.2, the destination hash of 3.3.6.2.1, the cosign bytes of 5.3.1, the receipt bytes of 5.3.3.6) were checked by search for a second wording only; none was found to disagree. **Not done:** the known-answer vectors were not recomputed, `signed_object.cddl` was not compared line by line with the 2.6.1.7 table (only array kinds, key encodings and `evidence_refs`), and the large table of CC 2.6.1.7 was read through its inventory gists and by search, not row by row.
- **`halt` (61), `accord` (36).** CC 4.2 to 4.2.1.3, 4.2.2, 4.2.3 and 4.2.5 read in full; CC 4.2.6 read for its thresholds table, the rule and the un-trust paragraphs, the rest by search; every other statement read in place. Data compared: the two accord rows of `governance_policy` (tsv and json) and the accord families of `transitions.json`. `reactions.json` was not compared. The `formal/accord_halt` model was not opened, so the two-halts finding is from the text alone and the model may already decide it.
- **`content_ingestion` (59).** CC 5.3.2.5, 5.3.2.6 and 3.4.14 read in full; CC 3.3.13 read for its common field set, the rendition rule and the rows the inventory names, not end to end; the render-tier table was not compared with any data file (none was found for it).
- **`placement` (52).** Every statement read in place; data compared: the `placement` column of `family_model.json` for the families the statements name, and the default row. The known conflicts on the owner-binding's scope (C107, C132, C253) and on the replication grant (C216, C227) were seen and not re-reported, since this pass found nothing beyond what they record. C260 is fixed in the text.
- **`other:client` (6).** All six are one passage of CC 4.5.13; read in full. `manifests/view.cddl` was not compared.

Two inventory gists are stale against today's text and produced no finding: the FedCode kinds no longer claim a one-to-one map onto `identity_type` (C167 reads as repaired in CC 2.6.8), and CC 5.1 now carries "ordering" (C131 reads as repaired).
