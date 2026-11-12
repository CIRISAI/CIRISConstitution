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

## Member names the text uses that the signed-object table does not carry

Each is a member of a sealed or framed body the table does not list, or a name only the prose uses. Which?

| member | family or object | section |
|---|---|---|
| `K` | `delivery_receipt:{stream_id}` | CC 5.3.3.6 |
| `achieved_tier` | `fidelity:explainability_sla:{tier}` | CC 3.1.5.2 |
| `action` | `accord_proposal / accord_participation / accord_decision` | CC 4.2.6 |
| `admission` | `group:roster` | CC 3.2 |
| `admission_quorum_basis` | `group:roster` | CC 3.2 |
| `advertiser_key_id` | `capacity:relay_delivery` | CC 3.1.4 |
| `affiliation_archetype` | `group:roster` | CC 4.4.3.2.8 |
| `agent_id_hash` | `trace:{form}:{version}` | CC 3.1.5 |
| `alt_text` | `image:*` | CC 3.3.13 |
| `amount_commitment` | `settlement:*` | CC 3.3.10 |
| `app_name` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `aspects` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `at_rest_sha256` | `key_grant:{axis}` | CC 3.3.2 |
| `attestation_prefixes` | `consent:replication:{version}` | CC 3.3.7 |
| `axis` | `key_grant:{axis}` | CC 3.3.2, CC 4.4.3.4.1 |
| `baa` | `group:roster` | CC 4.4.3.2.8 |
| `bilateral_pair_id` | `consent:partnership_accept`, `consent:partnership_grant`, `consent:state:{stance}`, `topical_relation:{kind}` | CC 3.3.5, CC 4.4.3.4.3.1, CC 4.4.3.5.3 |
| `breach_notification` | `group:roster` | CC 4.4.3.2.8 |
| `budget_bytes` | `StorageBudgetV1` | CC 6.1.5.2 |
| `build_manifest_hash` | `identity:occurrence` | CC 3.3.6 |
| `build_manifest_ref` | `identity:occurrence` | CC 3.3.6 |
| `capability_declaration` | `provenance:skill_import:{source}` | CC 3.1.2 |
| `captions` | `video:*` | CC 3.3.13 |
| `cell_id` | `location_proof` | CC 3.3.3 |
| `cell_resolution` | `location_proof` | CC 2.6.6.1, CC 3.2, CC 3.3.3, CC 4.5.9.2, CC 4.5.9.3, CC 4.5.9.4 |
| `chain_of_custody` | `group:roster` | CC 4.4.3.2.8 |
| `change_kind` | `hard_case:{kind}` | CC 3.4.4 |
| `charter_digest` | `group:roster` | CC 2.4, CC 3.1.3 |
| `chunk_root` | `delivery_receipt:{stream_id}` | CC 5.3.3.6 |
| `claim_namespaces` | `wholeness_witness` | CC 6.1.1 |
| `claim_text` | `takedown_notice:{basis}` | CC 3.3.2 |
| `claimant_key_id` | `takedown_notice:{basis}` | CC 3.3.2 |
| `classification_scheme` | `group:roster` | CC 4.4.3.2.8 |
| `cohort` | `objection:{state}` | CC 3.1.9.2, CC 3.3.6.3 |
| `cohort_key_id` | `hard_case:{kind}`, `objection:{state}` | CC 3.1.9.2, CC 3.3.6.3, CC 3.4.4 |
| `cohort_subkind` | `community:listing`, `group:roster` | CC 3.1.1, CC 3.2, CC 4.4.3.2.1 |
| `cohort_subkind_payload` | `group:roster` | CC 3.2 |
| `cohorts` | `consent:replication:{version}` | CC 3.3.7 |
| `committed_tier` | `fidelity:explainability_sla:{tier}` | CC 3.1.5.2 |
| `community_key_id` | `community:listing`, `group:roster`, `key_grant:{axis}` | CC 3.1.1, CC 3.2, CC 3.3.2 |
| `community_name` | `group:roster` | CC 3.2 |
| `compartment` | `group:roster` | CC 4.4.3.2.8 |
| `compartments` | `group:roster` | CC 4.4.3.2.8 |
| `computation` | `progress_measure:{method_id}` | CC 3.1.9.7 |
| `confirms_halt_id` | `accord:lifecycle:{kind}` | CC 4.2.1.3 |
| `consensus_protocol` | `group:roster` | CC 3.2, CC 3.3.4, CC 4.2.3 |
| `consensus_protocol_entrenched` | `group:roster` | CC 3.2, CC 3.3.4, CC 4.2.3 |
| `content_holder_key_ids` | `takedown_notice:{basis}` | CC 3.3.2 |
| `content_id` | `CorpusWantV1`, `wholeness_witness` | CC 6.1.1, CC 6.1.5.2 |
| `content_sha256` | `key_grant:{axis}`, `takedown_notice:{basis}` | CC 3.3.2, CC 4.4.3.4.1 |
| `counter_notice_channel` | `takedown_notice:{basis}` | CC 3.3.2 |
| `crypto_tier` | `group:roster` | CC 4.4.3.2.8 |
| `data_subject_access_grant` | `group:roster` | CC 4.4.3.2.8 |
| `decay_protocol` | `consent:decay:{stage}`, `consent:state:{stance}` | CC 3.3.5, CC 4.4.3.5.1 |
| `decided_by` | `retirement:{state}` | CC 3.1.5 |
| `declared_cohort` | `group:roster` | CC 4.4.3.2.8 |
| `delegation_id` | `hard_case:{kind}` | CC 3.1.9.4 |
| `deletion_sla_days` | `consent:state:{stance}` | CC 3.3.5 |
| `derived_from` | `video:*` | CC 5.1 |
| `description` | `community:listing`, `model_3d:*` | CC 3.1.1, CC 3.2, CC 3.3.13 |
| `designated_officials` | `group:roster` | CC 4.4.3.2.8 |
| `destination_hash` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `device_class` | `identity:occurrence` | CC 3.3.6, CC 4.4.3.4.3.1 |
| `disclosure_bar` | `group:roster` | CC 4.4.3.2.8 |
| `domain` | `deferral:request` | CC 4.3 |
| `duty` | `moderation:{allegation_type}` | CC 4.5.13 |
| `effective_at` | `group:roster`, `hard_case:{kind}`, `key:revocation` | CC 2.4.1.1, CC 3.1.3, CC 3.4.4 |
| `encryption_pubkeys` | `identity:occurrence` | CC 3.3.6, CC 3.3.6.1, CC 4.4.3.4.3.1 |
| `endpoint` | `observation:reachability` | CC 3.1.9.4 |
| `epoch` | `capacity:relay_delivery`, `delivery_receipt:{stream_id}`, `key_grant:{axis}` | CC 3.1.4, CC 3.3.2, CC 4.4.3.2.6, CC 5.3.3.6 |
| `epoch_id` | `CorpusWantV1`, `wholeness_witness` | CC 6.1.1, CC 6.1.5.2 |
| `erasure_exempt` | `group:roster` | CC 4.4.3.2.8 |
| `event_id` | `hard_case:{kind}` | CC 3.4.2 |
| `exposure` | `moderation:{allegation_type}` | CC 4.5.13 |
| `external_controller` | `group:roster` | CC 4.4.3.2.8 |
| `fallback_reason` | `fidelity:explainability_sla:{tier}` | CC 3.1.5.2 |
| `family_key_id` | `group:roster` | CC 4.2.3 |
| `family_name` | `group:roster` | CC 4.2.3 |
| `format` | `file:{version}`, `image:*`, `model_3d:*`, `rendezvous:route` | CC 3.1.3.4, CC 3.1.4, CC 3.3.13 |
| `founded_at` | `group:roster` | CC 3.2 |
| `geographic_constraint` | `group:roster` | CC 4.5.9.4 |
| `good_faith_statement` | `takedown_notice:{basis}` | CC 3.3.2 |
| `goodhart_resistance` | `progress_measure:{method_id}` | CC 3.1.9.7 |
| `grants` | `consent:replication:{version}` | CC 3.3.7 |
| `grounds` | `objection:{state}` | CC 3.3.6.3 |
| `hardware_attestation` | `identity:occurrence` | CC 3.3.6 |
| `hardware_class` | `hardware_custody:{platform}`, `key:record` | CC 3.1.2, CC 4.2.2 |
| `hierarchy` | `group:roster` | CC 4.4.3.2.8 |
| `identity_key_id` | `identity:occurrence` | CC 3.3.6, CC 4.4.3.4.3.1 |
| `import_timestamp` | `provenance:skill_import:{source}` | CC 3.1.2 |
| `invocation_id` | `accord:lifecycle:{kind}` | CC 4.2.1.3 |
| `invocation_kind` | `accord:lifecycle:{kind}` | CC 4.2.1.3 |
| `joined_at` | `group:roster` | CC 3.2, CC 3.3.4 |
| `jurisdiction` | `group:roster`, `takedown_notice:{basis}` | CC 3.3.2, CC 4.4.3.2.8 |
| `kind` | `retirement:{state}` | CC 3.1.5 |
| `label` | `device:label` | CC 3.1.1 |
| `lawful_access` | `group:roster` | CC 4.4.3.2.8 |
| `leaf_count` | `wholeness_witness` | CC 6.1.1 |
| `legal_basis` | `takedown_notice:{basis}` | CC 3.3.2, CC 4.5.10.4, CC 4.5.3 |
| `legal_weight` | `group:roster` | CC 4.4.3.2.8 |
| `licence_classes` | `group:roster` | CC 4.4.3.2.8 |
| `lineage_key_id` | `hard_case:{kind}` | CC 3.4.2 |
| `manifest` | `trace:{form}:{version}` | CC 3.1.5, CC 3.4.5 |
| `marking_binds_to_record` | `group:roster` | CC 4.4.3.2.8 |
| `members` | `group:roster` | CC 3.2, CC 3.3.4, CC 4.2.3 |
| `membership_basis` | `group:roster` | CC 4.4.3.2.8 |
| `minter_key_id` | `key_grant:{axis}` | CC 3.3.2 |
| `ml_kem_768` | `identity:occurrence` | CC 3.3.6 |
| `node_id` | `CorpusWantV1`, `StorageBudgetV1` | CC 6.1.5.2 |
| `nonce` | `accord:*`, `accord_proposal / accord_participation / accord_decision` | CC 4.2.6 |
| `objects_to_attestation_id` | `objection:{state}` | CC 3.1.9.2, CC 3.3.6.3 |
| `observed` | `observation:reachability` | CC 3.1.9.4 |
| `occurrence_key_id` | `identity:occurrence` | CC 3.3.6, CC 4.4.3.4.3.1 |
| `outcome` | `moderation:{allegation_type}` | CC 4.5.13 |
| `owner_key_id` | `key_grant:{axis}` | CC 3.3.2 |
| `parent` | `collection:{kind}`, `file:{version}` | CC 3.1.3.4 |
| `peer_id` | `wholeness_witness` | CC 6.1.1 |
| `perceptual_hash` | `takedown_notice:{basis}` | CC 3.3.2 |
| `pin_reserve_bytes` | `StorageBudgetV1` | CC 6.1.5.2 |
| `poll_id` | `census:member:share` | CC 6.1.9 |
| `preserve_until` | `preserve_request`, `retirement:{state}` | CC 3.1.5 |
| `prev_head_digest` | `group:roster` | CC 2.4, CC 3.1.3, CC 4.4.3.2.3, CC 4.4.3.4.2 |
| `processor_chain` | `group:roster` | CC 4.4.3.2.8 |
| `purpose` | `archive_release:{basis}`, `moderation:{allegation_type}` | CC 3.1.5, CC 4.5.13 |
| `rail` | `settlement:*` | CC 3.3.10 |
| `ranking` | `ballot:moderator` | CC 4.5.13 |
| `ranks` | `ballot:moderator` | CC 3.1.3 |
| `received_at` | `delivery_receipt:{stream_id}` | CC 5.3.3.6 |
| `recipient_key_id` | `key_grant:{axis}` | CC 4.4.3.4.1 |
| `regulatory_profile` | `group:roster` | CC 4.4.3.2.8 |
| `remaining_budget_bytes` | `CorpusWantV1` | CC 6.1.5.2 |
| `rendezvous_node_key_id` | `rendezvous:route` | CC 3.1.4 |
| `resumes_halt_id` | `accord:lifecycle:{kind}` | CC 4.2.1.3 |
| `retention` | `group:roster` | CC 4.4.3.2.8 |
| `reticulum_ed25519_pubkey` | `identity:occurrence` | CC 4.4.3.4.3.1 |
| `reticulum_x25519_pubkey` | `identity:occurrence` | CC 3.3.6.1, CC 4.4.3.4.3.1 |
| `retirement_id` | `archive_release:{basis}`, `preserve_request`, `retirement:{state}` | CC 3.1.5 |
| `revision` | `StorageBudgetV1` | CC 6.1.5.2 |
| `revocation_id` | `key:revocation` | CC 2.4.1.1 |
| `revoked_after` | `key:revocation` | CC 2.4.1.1 |
| `revoked_at` | `key:revocation` | CC 2.4.1.1 |
| `revoked_key_id` | `key:revocation` | CC 2.4.1.1 |
| `revoked_key_sha256_ed25519_raw` | `key:revocation` | CC 2.4.1.1 |
| `revoking_key_id` | `key:revocation` | CC 2.4.1.1 |
| `route_blob_base64` | `rendezvous:route` | CC 3.1.4 |
| `run_kind` | `trace:{form}:{version}` | CC 3.1.5 |
| `selection_counts` | `takedown_notice:{basis}` | CC 3.3.2 |
| `sequence` | `ledger entry`, `ledger:head:{unit}:{version}` | CC 3.1.3, CC 3.3.10.1 |
| `service_class` | `group:roster` | CC 3.2 |
| `settled_action_ref` | `settlement:*` | CC 3.3.10 |
| `settled_at` | `settlement:*` | CC 3.3.10 |
| `settlement_ref` | `settlement:*` | CC 3.3.10 |
| `signed_at` | `identity:occurrence`, `self:delegates_to:agent_occurrence` | CC 4.4.3.4.3.1 |
| `signer_identity` | `provenance:skill_import:{source}` | CC 3.1.2 |
| `size` | `custody:{kind}` | CC 3.1.3.3 |
| `size_cap_bytes` | `CorpusWantV1` | CC 6.1.5.2 |
| `skill_manifest_sha256` | `provenance:skill_import:{source}` | CC 3.1.2 |
| `stance` | `consent:partnership_accept`, `consent:partnership_grant`, `consent:state:{stance}` | CC 3.3.5, CC 4.4.3.4.3.1 |
| `statement` | `preserve_response` | CC 3.1.5 |
| `status` | `licensure:{authority_id}` | CC 3.1.1 |
| `statutory_basis` | `group:roster` | CC 4.4.3.2.8 |
| `stream_id` | `capacity:relay_delivery`, `delivery_receipt:{stream_id}`, `key_grant:{axis}`, `video:*` | CC 3.1.4, CC 3.3.2, CC 5.1, CC 5.3.3.6 |
| `subject_key_id` | `consent:partnership_accept`, `consent:partnership_grant`, `consent:state:{stance}`, `hard_case:{kind}`, `location_proof` | CC 3.3.3, CC 3.3.5, CC 3.4.4, CC 4.4.3.4.3.1 |
| `subject_kind` | `StorageBudgetV1`, `consent:partnership_accept`, `consent:partnership_grant`, `identity:occurrence`, `takedown_notice:{basis}` | CC 3.1.1, CC 4.4.3.4.3.1, CC 6.1.5.2 |
| `subscriber_key_id` | `delivery_receipt:{stream_id}` | CC 5.3.3.6 |
| `target_key_id` | `consent:state:{stance}` | CC 3.3.5 |
| `trace` | `trace:{form}:{version}` | CC 3.1.5, CC 3.4.5 |
| `trace_id` | `trace:{form}:{version}` | CC 3.1.5 |
| `tracks` | `progress_measure:{method_id}` | CC 3.1.9.7 |
| `transcript` | `audio:*` | CC 3.3.13 |
| `transit_kex_pubkeys` | `identity:occurrence` | CC 3.3.6.2 |
| `transparency_mode` | `group:roster` | CC 4.4.3.2.8 |
| `transparency_obligations` | `group:roster` | CC 4.4.3.2.8 |
| `transport_destination` | `identity:occurrence` | CC 3.3.6, CC 4.4.3.4.3, CC 4.4.3.4.3.1 |
| `unit` | `ledger:head:{unit}:{version}` | CC 3.1.3 |
| `validity_window` | `progress_measure:{method_id}` | CC 3.1.9.7 |
| `via` | `observation:reachability` | CC 3.1.9.4 |
| `window_until` | `accord_proposal / accord_participation / accord_decision` | CC 4.2.6 |
| `wrap_algorithm` | `key_grant:{axis}` | CC 3.1.3, CC 3.3.2, CC 4.4.3.2.1, CC 4.4.3.4.1 |
| `wrapped_dek` | `key_grant:{axis}` | CC 3.1.3, CC 3.3.2, CC 4.4.3.4.1 |
| `x25519_base64` | `identity:occurrence` | CC 3.3.6.1 |

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
