# Draft addition to CIRISPersist#1259 (not posted; for Eric to read first)

Questions from the rc19 data pass. Each is a point where the Constitution text and the census of the
pinned release differ, or where the text names a rule and no token. Nothing here asks for a change before
you say which side is right; where the build is right the text will record it as a departure with a reason.

## Where the text and the census cell differ

1. `key_grant:{axis}` supersede. CC 3.3.2 and CC 5.1: no row supersedes or withdraws a wrap; a rotation is a
   new row. Census cell: `supersedes=same_attester`. Which does the door do?
2. `key_grant:{axis}` and `group:roster` rotation on removal. CC 4.4.3.4.5 and CC 4.5.12.1: at self and
   family scope nothing is rotated, the store stops wrapping; epoch and stream axes rotate. Census cell:
   yes for the whole family.
3. `revocation:{entity_type}:{reason}` erasure. CC 4.5.3 gives every kept-list row a producer-executed route.
   Census cell: none (unpurgeable, migration.rs:606).
4. `revocation:{entity_type}:{reason}` rollback. CC 3.1.1: non-rollbackable. Census cell admits the
   attester's withdrawal.
5. `licensure:{authority_id}` retraction class. CC 2.4.1.1 lists a licence as an act of a body. Census cell:
   `retraction_class=peer`.
6. `membership:{stage}` proposal. CC 3.1.3.2: the inviter withdraws a proposal alone. Census cell: a cosigned
   withdrawal for the whole family.
7. `identity:occurrence` eviction. CC 3.3.6.3: an eviction lands only by the two self-roster paths. Census
   cell: the attester or the subject withdraws alone.
8. `consent:state:{stance}` and `key_grant:{axis}` audience. CC 2.6.1.7 and CC 3.3.2 against the cells'
   audience (`for_key_id` as an added recipient; `addressee` against the content scope's audience).
9. Default `subject_rule.in_audience`. CC 4.4.3.4.7: at a targeted scope every key in `subject_key_ids` is
   within the row's audience. Census default: no.
10. Two door-token lists. `identity_amendment` lists five tokens where CC 3.1.5 names
    `identity_amendment_unauthorized`; `trace:{form}:{version}` lists `run_kind`, which reads as a clipped
    `trace_run_kind_mock`.

## Rules the text states with no refusal token

The guard table carries 32 refusals with no name, and five folds refuse by a name the text does not give
(`roster_change_below_majority`, `witness_quorum_invalid`, `evidence_score_mismatch`,
`aggregation_meta_mismatch`, `locality_mismatch`). A refusal token is on the wire, so the names are yours
to give or confirm. The list with the nearest existing token for each is `handoff/lanes/out_g_guard.md`,
section "The 39 first-pass rows that refused with no token".

## Member names the text uses that the signed-object table does not carry (Parts 4 to 6; Parts 2 and 3 to follow)

Each is a member of a sealed or framed body the table does not list, or a name only the prose uses. Which?

| member | family or object | section |
|---|---|---|
| `K` | `delivery_receipt:{stream_id}` | CC 5.3.3.6 |
| `action` | `accord_proposal / accord_participation / accord_decision` | CC 4.2.6 |
| `affiliation_archetype` | `group:roster` | CC 4.4.3.2.8 |
| `app_name` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `aspects` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `axis` | `key_grant:{axis}` | CC 4.4.3.4.1 |
| `baa` | `group:roster` | CC 4.4.3.2.8 |
| `bilateral_pair_id` | `consent:partnership_accept`, `consent:partnership_grant`, `topical_relation:{kind}` | CC 4.4.3.4.3.1, CC 4.4.3.5.3 |
| `breach_notification` | `group:roster` | CC 4.4.3.2.8 |
| `budget_bytes` | `StorageBudgetV1` | CC 6.1.5.2 |
| `cell_resolution` | `location_proof` | CC 4.5.9.2, CC 4.5.9.3, CC 4.5.9.4 |
| `chain_of_custody` | `group:roster` | CC 4.4.3.2.8 |
| `chunk_root` | `delivery_receipt:{stream_id}` | CC 5.3.3.6 |
| `claim_namespaces` | `wholeness_witness` | CC 6.1.1 |
| `classification_scheme` | `group:roster` | CC 4.4.3.2.8 |
| `cohort_subkind` | `group:roster` | CC 4.4.3.2.1 |
| `compartment` | `group:roster` | CC 4.4.3.2.8 |
| `compartments` | `group:roster` | CC 4.4.3.2.8 |
| `confirms_halt_id` | `accord:lifecycle:{kind}` | CC 4.2.1.3 |
| `consensus_protocol` | `group:roster` | CC 4.2.3 |
| `consensus_protocol_entrenched` | `group:roster` | CC 4.2.3 |
| `content_id` | `CorpusWantV1`, `wholeness_witness` | CC 6.1.1, CC 6.1.5.2 |
| `content_sha256` | `key_grant:{axis}` | CC 4.4.3.4.1 |
| `crypto_tier` | `group:roster` | CC 4.4.3.2.8 |
| `data_subject_access_grant` | `group:roster` | CC 4.4.3.2.8 |
| `decay_protocol` | `consent:decay:{stage}` | CC 4.4.3.5.1 |
| `declared_cohort` | `group:roster` | CC 4.4.3.2.8 |
| `derived_from` | `video:*` | CC 5.1 |
| `designated_officials` | `group:roster` | CC 4.4.3.2.8 |
| `destination_hash` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `device_class` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `disclosure_bar` | `group:roster` | CC 4.4.3.2.8 |
| `domain` | `deferral:request` | CC 4.3 |
| `duty` | `moderation:{allegation_type}` | CC 4.5.13 |
| `encryption_pubkeys` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `epoch` | `delivery_receipt:{stream_id}`, `key_grant:{axis}` | CC 4.4.3.2.6, CC 5.3.3.6 |
| `epoch_id` | `CorpusWantV1`, `wholeness_witness` | CC 6.1.1, CC 6.1.5.2 |
| `erasure_exempt` | `group:roster` | CC 4.4.3.2.8 |
| `exposure` | `moderation:{allegation_type}` | CC 4.5.13 |
| `external_controller` | `group:roster` | CC 4.4.3.2.8 |
| `family_key_id` | `group:roster` | CC 4.2.3 |
| `family_name` | `group:roster` | CC 4.2.3 |
| `geographic_constraint` | `group:roster` | CC 4.5.9.4 |
| `hardware_class` | `hardware_custody:{platform}`, `key:record` | CC 4.2.2 |
| `hierarchy` | `group:roster` | CC 4.4.3.2.8 |
| `identity_key_id` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `invocation_id` | `accord:lifecycle:{kind}` | CC 4.2.1.3 |
| `invocation_kind` | `accord:lifecycle:{kind}` | CC 4.2.1.3 |
| `jurisdiction` | `group:roster` | CC 4.4.3.2.8 |
| `lawful_access` | `group:roster` | CC 4.4.3.2.8 |
| `leaf_count` | `wholeness_witness` | CC 6.1.1 |
| `legal_basis` | `takedown_notice:{basis}` | CC 4.5.10.4, CC 4.5.3 |
| `legal_weight` | `group:roster` | CC 4.4.3.2.8 |
| `licence_classes` | `group:roster` | CC 4.4.3.2.8 |
| `marking_binds_to_record` | `group:roster` | CC 4.4.3.2.8 |
| `members` | `group:roster` | CC 4.2.3 |
| `membership_basis` | `group:roster` | CC 4.4.3.2.8 |
| `node_id` | `CorpusWantV1`, `StorageBudgetV1` | CC 6.1.5.2 |
| `nonce` | `accord:*`, `accord_proposal / accord_participation / accord_decision` | CC 4.2.6 |
| `occurrence_key_id` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `outcome` | `moderation:{allegation_type}` | CC 4.5.13 |
| `peer_id` | `wholeness_witness` | CC 6.1.1 |
| `pin_reserve_bytes` | `StorageBudgetV1` | CC 6.1.5.2 |
| `poll_id` | `census:member:share` | CC 6.1.9 |
| `prev_head_digest` | `group:roster` | CC 4.4.3.2.3, CC 4.4.3.4.2 |
| `processor_chain` | `group:roster` | CC 4.4.3.2.8 |
| `purpose` | `moderation:{allegation_type}` | CC 4.5.13 |
| `ranking` | `ballot:moderator` | CC 4.5.13 |
| `received_at` | `delivery_receipt:{stream_id}` | CC 5.3.3.6 |
| `recipient_key_id` | `key_grant:{axis}` | CC 4.4.3.4.1 |
| `regulatory_profile` | `group:roster` | CC 4.4.3.2.8 |
| `remaining_budget_bytes` | `CorpusWantV1` | CC 6.1.5.2 |
| `resumes_halt_id` | `accord:lifecycle:{kind}` | CC 4.2.1.3 |
| `retention` | `group:roster` | CC 4.4.3.2.8 |
| `reticulum_ed25519_pubkey` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `reticulum_x25519_pubkey` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `revision` | `StorageBudgetV1` | CC 6.1.5.2 |
| `signed_at` | `identity:occurrence`, `self:delegates_to:agent_occurrence` | CC 4.4.3.4.3.1 |
| `size_cap_bytes` | `CorpusWantV1` | CC 6.1.5.2 |
| `stance` | `consent:partnership_accept`, `consent:partnership_grant` | CC 4.4.3.4.3.1 |
| `statutory_basis` | `group:roster` | CC 4.4.3.2.8 |
| `stream_id` | `delivery_receipt:{stream_id}`, `video:*` | CC 5.1, CC 5.3.3.6 |
| `subject_key_id` | `consent:partnership_accept`, `consent:partnership_grant` | CC 4.4.3.4.3.1 |
| `subject_kind` | `StorageBudgetV1`, `consent:partnership_accept`, `consent:partnership_grant`, `identity:occurrence` | CC 4.4.3.4.3.1, CC 6.1.5.2 |
| `subscriber_key_id` | `delivery_receipt:{stream_id}` | CC 5.3.3.6 |
| `transparency_mode` | `group:roster` | CC 4.4.3.2.8 |
| `transparency_obligations` | `group:roster` | CC 4.4.3.2.8 |
| `transport_destination` | `identity:occurrence` | CC 4.4.3.4.3, CC 4.4.3.4.3.1 |
| `window_until` | `accord_proposal / accord_participation / accord_decision` | CC 4.2.6 |
| `wrap_algorithm` | `key_grant:{axis}` | CC 4.4.3.2.1, CC 4.4.3.4.1 |
| `wrapped_dek` | `key_grant:{axis}` | CC 4.4.3.4.1 |

## Carried from earlier in the thread, still open

- The refusal token for a future-dated row.
- Whether an un-announce withdraws the federation row.
- Whether the steward fold reads an occurrence anchor.
- Chain-row freshness W against the signer's standing.

## One-emitter rule (CC 4.5.13, landed 8aec89d)

A row a clock or a fold causes is emitted by the door the causing row first entered; peers re-derive and
emit nothing. Seven such emits are written in the text as the store's or the author's
(`manifests/reactions.json`, `_meta.one_emitter.not_yet_by_origin_door`). Does the store today emit
`consent:state:expired`, `hard_case:deletion_window_breach` and `hard_case:recipient_excluded` on every
node that sees the condition, or on one?
