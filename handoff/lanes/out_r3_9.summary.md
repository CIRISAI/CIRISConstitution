# Third reading, share 9: summary

Statements read: 425 across seven rule keys (the `family` scope rows taken as full members). Findings: 32 (9 major, 23 minor; 19 new, 13 known).

| rule key | statements | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| trust_fold | 137 | 13 | 1 | 0 | 7 | 5 |
| principle | 121 | 1 | 0 | 0 | 1 | 0 |
| signature | 75 | 5 | 2 | 0 | 2 | 1 |
| minor_floor | 52 | 10 | 3 | 3 | 2 | 2 |
| announce | 37 | 3 | 0 | 0 | 1 | 2 |
| other:session-claim | 2 | 0 | 0 | 0 | 0 | 0 |
| other:dsar-export | 1 | 0 | 0 | 0 | 0 | 0 |

## Major new findings

### minor_floor (3.4.11,3.4.13), condition

- Side A: CC 3.4.11 an `adult` band at `self` level satisfies the band but NOT a verified-level requirement
- Side B: CC 3.4.13 A `self`-level row MUST NOT graduate a user up a band, because `self` is unfalsifiable
- Note: CC 3.4.11 lets a self-declared adult pass every gate that asks the band and not a verified level (only 'sensitive spaces' ask the level); CC 3.4.13 Q1 and Q3 give a self-declared adult no lift at all, so the person stays under_13 with co-sign. CC 3.4.13 Q2 ('not age-assured to be ≥18 MUST be treated as a child') and the 2026-11-11 ruling in C001 support CC 3.4.13.

### minor_floor (3.4.11), data:actor

- Side A: CC 3.4.11 Admitted iff the signer acts for the subject (the subject's own occurrence or an admitted occurrence of it).
- Side B: manifests/family_model.json age_self_declared:band:{band}:{version} signer_rule (code-v61): who any_registered, via none, conditions []; cites CC 3.4.11 as 'fills'
- Note: The model's signer cell, read from the shipped store, admits any registered key and records the text as silent; CC 3.4.11 and the CC 3.1.2 row ('not open-sender') admit only a signer acting for the subject. A stranger's `minor` declaration about a person would enter protection for them under the cell and be refused under the text.

### minor_floor (3.4.11), data:condition

- Side A: CC 3.4.11 Emitter rule: `witness ∈ attesting_key.identity_type` ([CC 3.4.7.1](#3.4.7.1) set membership).
- Side B: manifests/family_model.json age_assurance:{level}:{band}:{version} signer_rule (code-v61): seat_role(attest) via delegates_to(infra:attest_assurance), not_subject; qualifier + identity_type contains witness
- Note: The cell adds a delegation leg under a scope `infra:attest_assurance` that no Part names; the text admits on the `witness` identity type alone. A witness key with no such delegation emits under the text and is refused under the cell. C324 holds the general identity-type-against-delegation question.

### signature (2.6.1.7,5.3.2.4.3.1), condition

- Side A: CC 2.6.1.7 REQUIRED once hybrid-complete
- Side B: CC 5.3.2.4.3.1 The only conformant state for a federation-tier key is "carries a valid ML-DSA-65 half".
- Note: The key record's `scrub_signature_pqc` cell (and `pqc_completed_at`, 'when the ML-DSA-65 half was attached') describes a record admitted before its PQ signature exists; CC 5.3.2.4.3.1 allows no hybrid-pending state and CC 2.6.1.7's own `algorithm` cell says 'hybrid on every admitted record'. The rest of the document supports CC 5.3.2.4.3.1.

### signature (2.6.1.7,5.3.2.4.3.1), data:condition

- Side A: CC 5.3.2.4.3.1 There is no opportunistic-acceptance window and no fleet-floor or calendar trigger.
- Side B: manifests/signed_object.cddl key record: ? scrub_signature_pqc: base64, ; REQUIRED once hybrid-complete
- Note: Same difference in the schema: the key record's PQ signature is optional with the comment 'once hybrid-complete', so a schema-valid key record may carry the classical half alone.

### trust_fold (3.4.9,4.4.3.8), condition

- Side A: CC 3.4.9 **Single-source attestations** (only one of the two co-stewards has emitted) MUST be marked as `confidence ≤ 0.5` in consumer composition until the second co-steward's attestation arrives.
- Side B: CC 4.4.3.8 The reader honours a `licensure:{authority_id}:v1` row iff two things hold.
- Note: CC 3.4.9 caps a CIRIS-issued licence recorded by one of Registry or Verify at confidence 0.5; CC 4.4.3.8 honours a licence on two conditions (walk reaches the authority, charter declares the class) and names no second emitter. CC 2.4.1.2.1 and CC 4.4.3.8 (the homes) support the two-condition reading; the 0.5 rule has no counterpart there.

## Known conflicts whose stale wording is still in the text

- C132 (5.4.6,3.2, minor): C132 is held (an open wire question for the store); the sentence of CC 5.4.6 is unchanged.
- C142 (5.4.6, minor): C142's repair is proposed, not applied: the section still uses 'announces' for the transport broadcast after fixing it to the federation-scope owner-binding.
- C316 (3.4.13,3.2, major): C316 is 'to fix from the text'; the stale side is still there, in CC 3.2 and in CC 3.4.13 Q4 ('A guardian-less minor goes dark for general operation').
- C002 (3.2,3.4.13, major): C002 is held for Eric (one custody edge with co-signers, or a set of guardians); both statements stand unchanged.
- C343 (4.4.3.10,3.4.11, minor): C343 was fixed in CC 3.4.11; the qualified shapes are still written in the ordering line of CC 4.4.3.10, and a row so shaped is refused `namespace_family_unregistered`.
- C001 (3.4.12,3.4.11, minor): Ruled in C001; CC 3.4.11 and CC 3.4.13 now read under_13, CC 3.4.12 still says `minor`.
- C317 (5.4.6,4.5.13,3.4.13, major): C317 is 'to fix from the text'; CC 4.5.13 is unchanged. With absence read as under_13, a person with no assurance on record cannot announce at all.
- C287 (3.1.2,3.1.2.1, minor): C287 is held for the decision on role names; both sentences stand unchanged.
- C001 (3.4.12,3.4.11, minor): C001 was ruled (absence reads as under_13 with co-sign). CC 3.4.12 still says `minor`, the stale wording.
- C135 (4.1.1,6.1.8, minor): Read independently; C135 holds it as no conflict (two cases: general consumer policy against the one bootstrap function). The two forces still stand in the text.
- C246 (6.1.8,4.4.3.8, minor): Read independently; C246 holds it as two graphs (capability graph against acceptance edges). CC 6.1.8 says 'trust-graph', the word CC 4.1.1 reserves for neither, so the reader has to know C246's reading.
- C339 (3.2,4.4.3.8, minor): Read independently; C339 holds it as no conflict (identity by ceremony, entry by delegation). Both sentences stand unchanged.
- C267 (4.4.3.12,4.4.3.8, minor): Policy B's 'vouched for' names no row and no relation to trust_depth 1; C267 settled the cap only. Policy C now cites the five-hop cap; Policy B still names none.

## Limits of this reading

- No key was left unfinished, but depth was uneven. `trust_fold`, `minor_floor`, `signature` and `announce` were read against the current text of their sections. `principle` (121 statements, almost all agent-conduct prose in Parts 1 and 7) was read from the inventory gists, with the text opened for CC 1.1, 1.3, 1.13.2, 7.1.4, 7.4 and 7.5 only; one finding.
- `other:session-claim` (CC 3.1.3.1) and `other:dsar-export` (CC 4.5.2.2) were read in full against the model, the transitions, the reactions and `constants.tsv`: no finding.
- Data compared: `family_model.json` (trust, age_assurance, age_self_declared, session), `transitions.json`, `reactions.json`, `signed_object.cddl`, `constants.tsv`. The CC 8.10 family cards for these families repeat the model cells (the fold lines were checked for the two age families) and gave nothing beyond the model. `governance_policy.json` holds nothing for these keys.
- Every quoted text side was checked verbatim against `constitution/part_*.md` at head 87c1730. The data sides are paraphrases of the cells, not verbatim JSON.
- The two data findings on the age families rest on cells marked `code-v61`: they say what the shipped store does, and I did not open the store to confirm it.
- The CC 3.4.9 finding (single-source licence at confidence 0.5) is rated major on the reading that a capped confidence can fail a reader threshold; if confidence never gates honouring, it is minor.
