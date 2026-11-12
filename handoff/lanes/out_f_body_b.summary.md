# Lane F, column `body`, files p4 to p7 (no `body` statement of scope `family` is in p1 or p7)

120 inventory statements, 136 (statement, family) rows. All 120 statements were found in today's text (119 by `entry_phrase`, one by gist); none is `GONE`.

## Counts per verdict

| verdict | rows |
|---|---|
| AGREE | 4 |
| FILLS | 56 |
| DISAGREE | 1 |
| RICHER | 55 |
| NOT_A_CELL | 20 |
| GONE | 0 |

## How families were chosen

The inventory `families` field holds stems, and many are not registry families (`family`, `community`, `affiliations`, `delegates_to`, `identity_occurrence`, `location_proof`, `wholeness_witness`, `storage_budget`, `corpus_want`, `live_stream`, `scores`). Each statement was placed on the model row its words bear on: the community, family and accord roster records on `group:roster`; `identity_occurrence` on `identity:occurrence`; the login grant on `self:delegates_to:agent_occurrence`; the accord charter on `trust:{job}:{version}`. Where no row exists the `family` field says so and the verdict is `RICHER` with `need:row`. A stem was not expanded to every row under it when the sentence concerns one of them (for example `accord` to `accord:lifecycle:{kind}`).

## RICHER needs, grouped

A row may carry two tags; each is counted. 55 RICHER rows.

| need | rows | what is missing |
|---|---|---|
| `need:relation` | 14 | a relation to another row or to folded state: version-to-version difference bounds, set membership (compartment within roster, scope within parent scope), cardinality (one grant per member per write), a value class that depends on another key's identity_type. Candidate column: body_relation with a small closed grammar. |
| `need:row` | 14 | an object whose members the prose gives has no row among the 184 families and no CDDL: subject_kind payloads (location_proof, live_stream), framing objects (StorageBudgetV1, CorpusWantV1, wholeness_witness), the three accord roster-change objects. Candidate: an objects table beside the family model, or rows for them. |
| `need:enum` | 10 | a closed token vocabulary as data (name, meaning, sometimes status): scope tokens of delegates_to, mesh_config key names, hardware_custody platforms. Candidate: a vocabulary table keyed by (family, member or segment). |
| `need:presence` | 8 | presence rules beyond required/optional: required-to-resolve through a default or preset, forbidden by kind or by tier, present only when N>1, absent on one variant. Candidate tokens: forbidden, iff(cond), resolves_by(default or preset). |
| `need:encode` | 8 | encoding rules: a second signed preimage inside a row (delivery receipt), field order and endianness, a member carried but unsigned, one-hot over log2 buckets, fixed-size padding. Candidate column: body_encoding naming a layout id. |
| `need:equal` | 6 | an equality: a member equal to folded node state (resumes_halt_id), equal across two rows (bilateral_pair_id), arithmetic sums (mass_total), two members of one row (n_eff = source_count), a case-folded member equal to a scope segment. Candidate token: eq(a, b) inside a body_check column. |
| `need:bound` | 6 | a numeric bound on a member, absolute (cell_resolution at most 7, u32 length) or against another member (pin_reserve_bytes at most budget_bytes). Candidate token: max(n) / le(member). |
| `need:derive` | 3 | a member whose value is a digest or commitment of named inputs: election id, ballot-set digest, Merkle root. Candidate token: derive(fn, inputs). |

Secondary needs noted on FILLS rows (`also need:`): `need:relation` 5, `need:presence` 4, `need:derive` 4, `need:encode` 2, `need:bound` 1.

### `need:relation`

- CC 4.2.2, `hardware_custody:{platform}`: need:relation a lookup table from a key-record property value (hardware_class) to this family's {platform} segment; five table lines; wants a small mapping table as data; cddl:no[hardware_class]
- CC 4.2.6, `group:roster`: need:relation a bound on what may differ between a version and the one before it (only one seat's signing key and next commitment); the CDDL has recovers, successor_keys and pre_rotation_commitment "on a charter recovery" but this prose names none of them and calls the object a roster version; cddl:yes[recovers,successor_keys,pre_rotation_commitment]
- CC 4.2.6, `group:roster`: need:relation the refusal form of the preceding row: version-to-version difference outside the named members is refused
- CC 4.3, `delegates_to (seat; no family row of its own)`: need:relation a child delegates_to scope is within its parent's (attenuation), depth-capped; a relation between two rows of a chain; cddl:yes[scope]
- CC 4.3, `deferral:request`: need:relation a conditional reference: an escalating request names the request it was handed, and the eventual answer cites the ruling received; the reference cell of deferral:request is null, so the reference column has no token for "sometimes carries"; cddl:yes[references_attestation_id]
- CC 4.4.3.2.1, `key_grant:{axis}`: need:relation cardinality across rows: one grant per current member occurrence per sealed write, under one per-community epoch DEK
- CC 4.4.3.2.1, `group:roster`: need:relation whether a content body is plaintext is read from the community record (its subkind), never from a member of the writer's row
- CC 4.4.3.2.8, `key_grant:{axis}`: need:relation a DEK and its grants per compartment: the grant set is the compartment's members less its exclusions, the cascade applied one level down
- CC 4.4.3.4.3, `trust:{job}:{version}`: need:relation the allowed scope tokens depend on the delegate key's identity_type; agency:* is a class name, never an emitted string; the subject_rule cell already carries this in prose; cddl:yes[scope,identity_type]
- CC 4.5.13, `ballot:moderator`: need:relation the option set of the ballot is the live roster in a computed order, and an unedited ballot means that order; cell is gap, noted "not in the census"; cddl:no[ranking] (in choice_item/view cddl: ranking)
- CC 5.1, `key_grant:{axis}`: need:relation what the wrapped key is: a per-stream DEK derived from the epoch secret, one stream per grant; the exporter secret is never a wrapped value
- CC 6.1.1, `wholeness_witness (no family row)`: need:row need:relation one member (the root) is computed over exactly the set another member names; cddl:no[claim_namespaces]
- CC 6.1.1, `wholeness_witness (no family row)`: need:row need:relation a bound on a member's values by tier and scope: no anonymous-tier or self local-tier namespace, and no such leaf under the root; cddl:no[claim_namespaces,peer_id]
- CC 6.1.1, `wholeness_witness (no family row)`: need:row need:relation the leaf grain allowed depends on the leaf's cohort_scope (family or community: opaque ids only); cddl:no[content_id]

### `need:row`

- CC 4.2.6, `accord_proposal / accord_participation / accord_decision (no family row)`: need:row three signed objects whose members the prose lists have no family row and no CDDL; only window_until is spelled as a member name; cddl:no[window_until,nonce,action]
- CC 4.5.9.2, `location_proof (no family row)`: need:row need:bound a subject_kind payload with no family row; an upper bound on a member, refused at admission above it; cddl:no[cell_resolution]
- CC 4.5.9.3, `location_proof (no family row)`: need:row need:bound restates 4.5.9.2; cddl:no[cell_resolution]
- CC 4.5.9.4, `location_proof (no family row)`: need:row need:bound restates CC 2.6.6.1; cddl:no[cell_resolution]
- CC 5.1, `live_stream (no family row)`: need:row need:presence a subject_kind payload with no family row; "kept" is derived from one member or from the existence of other rows, and "recorded" is a forbidden member; cddl:yes[history_on_join]
- CC 5.3.2.5, `live_stream (no family row)`: need:row need:presence a member (total size) required on every descriptor except this one while in progress; each chunk and the init segment carry their own
- CC 6.1.1, `wholeness_witness (no family row)`: need:row need:derive an object the text calls "`wholeness_witness:` object" with no family row; its main member is a Merkle root over held claims
- CC 6.1.1, `wholeness_witness (no family row)`: need:row need:relation one member (the root) is computed over exactly the set another member names; cddl:no[claim_namespaces]
- CC 6.1.1, `wholeness_witness (no family row)`: need:row need:relation a bound on a member's values by tier and scope: no anonymous-tier or self local-tier namespace, and no such leaf under the root; cddl:no[claim_namespaces,peer_id]
- CC 6.1.1, `wholeness_witness (no family row)`: need:row need:relation the leaf grain allowed depends on the leaf's cohort_scope (family or community: opaque ids only); cddl:no[content_id]
- CC 6.1.1, `wholeness_witness (no family row)`: need:row a member and its meaning (a count over opaque leaves); the same sentence names epoch_id and claim_namespace_set as the comparison key; cddl:no[leaf_count,epoch_id]
- CC 6.1.5.2, `StorageBudgetV1 (no family row)`: need:row need:bound a signed framing object, expressly not an attestation, with its own preimage; one member bounded by another; cddl:no[budget_bytes,pin_reserve_bytes,revision,node_id]
- CC 6.1.5.2, `StorageBudgetV1 (no family row)`: need:row need:bound need:encode three refusals: reserve above budget, lists not sorted and deduplicated, forbidden scope entries; cddl:yes[cohort_scope] cddl:no[pin_reserve_bytes,budget_bytes,subject_kind]
- CC 6.1.5.2, `CorpusWantV1 (no family row)`: need:row a signed framing object with its own preimage and no family row; cddl:no[size_cap_bytes,remaining_budget_bytes,content_id,node_id,epoch_id]

### `need:enum`

- CC 4.2.1.4, `mesh_config:{key}`: need:enum the closed list of {key} names with a status each (live, planned and refused, shaping, onion); the cell says only that a key names a consumer processor; five key names are literal (shaping.rho, shaping.window_secs, shaping.node_cap_bytes_per_s, onion.cap_factor, onion.mix_mean_delay_ms), the six others are described and not spelled
- CC 4.2.2, `hardware_custody:{platform}`: need:enum the closed {platform} token list is pinned in the register (CLM-hardware-custody-vocabulary), not in the model or the registry row
- CC 4.3, `delegates_to (seat; no family row of its own)`: need:enum the scope tokens of a delegates_to are a vocabulary with no home in the model: the signer_rule cell of deferral:response:{outcome} cites delegates_to(resolve_deferral) but no row holds the seat row's own body; self:delegates_to is qualified "confers nothing"; scope is cddl:yes, required on delegates_to; cddl:yes[scope]
- CC 4.4.3.4.3, `self:delegates_to:agent_occurrence`: need:enum scope token act_on_behalf with its meaning; the tokens of scope are a table of name and meaning, not a member type; cddl:yes[scope]
- CC 4.4.3.4.3, `self:delegates_to:agent_occurrence`: need:enum scope token message_io with its meaning; cddl:yes[scope]
- CC 4.4.3.4.3, `self:delegates_to:agent_occurrence`: need:enum scope token network_presence with its meaning; cddl:yes[scope]
- CC 4.4.3.4.3, `self:delegates_to:agent_occurrence`: need:enum scope token sub_delegation with its meaning; cddl:yes[scope]
- CC 4.4.3.4.3, `trust:{job}:{version}`: need:enum the closed infra:* scope set (serve, store, transport, attest, network_presence, hold_community_membership, hold_family_membership, relay); the subject_rule cell of trust:{job}:{version} says "node agency scopes infra-only" without the list; cddl:yes[scope]
- CC 4.4.3.4.3, `trust:{job}:{version}`: need:enum the infra:* tokens with one meaning each (same list as the class table above it); cddl:yes[scope]
- CC 6.1.5.1, `mesh_config:{key}`: need:enum the same key list as 4.2.1.4 with the status of each; the two sections agree

### `need:presence`

- CC 4.4.3.2.6, `key_grant:{axis}`: need:presence the epoch is absent on a grant to a single recipient and present on a cohort grant; the inventory gist says revocation is a withdraws against the grant, the text now says "the grant is never withdrawn"; cddl:no[epoch]
- CC 4.4.3.2.8, `group:roster`: need:presence "required to resolve": a member may be absent on the wire yet must have a value through a shipped default or a named preset; required/optional cannot say this; cddl:no[affiliation_archetype]
- CC 4.5.3, `hard_case:{kind}`: need:presence a forbidden member by kind: subject_key_ids (and any subject reference in the event member) empty when the hard case records an erasure; cddl:yes[subject_key_ids]
- CC 5.1, `live_stream (no family row)`: need:row need:presence a subject_kind payload with no family row; "kept" is derived from one member or from the existence of other rows, and "recorded" is a forbidden member; cddl:yes[history_on_join]
- CC 5.3.2.5, `live_stream (no family row)`: need:row need:presence a member (total size) required on every descriptor except this one while in progress; each chunk and the init segment carry their own
- CC 6.1.9, `census:composite:{class}`: need:presence forbidden content: no delta, no node id; the per-period token is return_token in the CDDL (on shares); cddl:yes[return_token]
- CC 6.1.9, `census:share:{class}`: need:presence forbidden members: a return has no field about the Anonymous Tier
- CC 6.1.9, `census:member:share`: need:encode need:presence fixed size with padding where no poll is open; poll_id only in the sealed body, yet the tally family carries {poll_id} in its name; cddl:no[poll_id]

### `need:encode`

- CC 5.3.3.6, `delivery_receipt:{stream_id}`: need:encode a second signed thing inside the row: a domain-separated length-prefixed preimage with its own signature, beside the JCS envelope the row signature covers
- CC 5.3.3.6, `delivery_receipt:{stream_id}`: need:encode need:bound field order of a preimage (subscriber_key_id before stream_id), little-endian, and a length bound per field; cddl:no[subscriber_key_id,stream_id]
- CC 5.3.3.6, `delivery_receipt:{stream_id}`: need:encode a member that is carried but outside the signed preimage: the column has no "signed or not" per member; cddl:no[received_at]
- CC 6.1.5.2, `StorageBudgetV1 (no family row)`: need:row need:bound need:encode three refusals: reserve above budget, lists not sorted and deduplicated, forbidden scope entries; cddl:yes[cohort_scope] cddl:no[pin_reserve_bytes,budget_bytes,subject_kind]
- CC 6.1.9, `census:share:{class}`: need:encode a value encoding (one-hot over log2 buckets) whose layout is named by a registered id; the CDDL requires aggregation_algorithm_id on partials and composites, not on a share; cddl:yes[aggregation_algorithm_id]
- CC 6.1.9, `census:member:share`: need:encode as census:share:{class}; cddl:yes[aggregation_algorithm_id]
- CC 6.1.9, `census:member:share`: need:encode a poll field in the member cell: one-hot over options plus none
- CC 6.1.9, `census:member:share`: need:encode need:presence fixed size with padding where no poll is open; poll_id only in the sealed body, yet the tally family carries {poll_id} in its name; cddl:no[poll_id]

### `need:equal`

- CC 4.2.1.3, `accord:lifecycle:{kind}`: need:equal a member must equal a value of the node's folded state (the id of the halt now in force), not another member of the same row; the same sentence adds a uniqueness rule on invocation_id within valid_until; cddl:yes[valid_until] cddl:no[resumes_halt_id,invocation_id]
- CC 4.3, `deferral:response:{outcome}`: need:equal a member of the answered row, case-folded, equals a segment of the scope token on the answerer's delegates_to; the unscoped token matches any; cddl:yes[scope]
- CC 4.4.3.4.3.1, `consent:partnership_grant`: need:equal one member equal across two rows of different families (the grant and the accept); both halves; cddl:no[bilateral_pair_id]
- CC 4.4.3.4.3.1, `consent:partnership_accept`: need:equal one member equal across two rows of different families (the grant and the accept); both halves; cddl:no[bilateral_pair_id]
- CC 6.1.9, `census:composite:{class}`: need:equal arithmetic equalities checked at admission: within the row (cells sum to mass_total) and across rows (the two named partials sum to it); the model cell says none while the CDDL requires these members; cddl:yes[partial_a,partial_b,mass_total]
- CC 6.1.9, `ballot:tally:{poll_id}`: need:equal two members of one row equal; both are "REQUIRED on ballot:tally:{poll_id}:v1" in the CDDL while the model cell says none; cddl:yes[n_eff,source_count]

### `need:bound`

- CC 4.5.9.2, `location_proof (no family row)`: need:row need:bound a subject_kind payload with no family row; an upper bound on a member, refused at admission above it; cddl:no[cell_resolution]
- CC 4.5.9.3, `location_proof (no family row)`: need:row need:bound restates 4.5.9.2; cddl:no[cell_resolution]
- CC 4.5.9.4, `location_proof (no family row)`: need:row need:bound restates CC 2.6.6.1; cddl:no[cell_resolution]
- CC 5.3.3.6, `delivery_receipt:{stream_id}`: need:encode need:bound field order of a preimage (subscriber_key_id before stream_id), little-endian, and a length bound per field; cddl:no[subscriber_key_id,stream_id]
- CC 6.1.5.2, `StorageBudgetV1 (no family row)`: need:row need:bound a signed framing object, expressly not an attestation, with its own preimage; one member bounded by another; cddl:no[budget_bytes,pin_reserve_bytes,revision,node_id]
- CC 6.1.5.2, `StorageBudgetV1 (no family row)`: need:row need:bound need:encode three refusals: reserve above budget, lists not sorted and deduplicated, forbidden scope entries; cddl:yes[cohort_scope] cddl:no[pin_reserve_bytes,budget_bytes,subject_kind]

### `need:derive`

- CC 4.5.13, `ballot:moderator`: need:derive a member whose value is a digest of two other things the node holds (community id; last seating row or roster genesis); "A ballot names that id"
- CC 4.5.13, `ballot:moderator_acceptance`: need:derive two members, one copied from the ballots, one a digest over a set of rows (ballots and withdrawals held); admission recounts over exactly that set
- CC 6.1.1, `wholeness_witness (no family row)`: need:row need:derive an object the text calls "`wholeness_witness:` object" with no family row; its main member is a Merkle root over held claims

## DISAGREE rows in full

- section 4.4.3.2.8, family `group:roster`. Cell (prose): "signed group object under one member (group_record / widening / revocation)". Prose: "The family model manifest carries its schema as data.". the prose says the manifest holds the affiliation config schema; manifests/family_model.json holds none of its member names (declared_cohort, membership_basis, classification_scheme: 0 occurrences) and the group:roster body cell names no member; the rest of the document sides with neither: the register pins the shape, per the sentence before; cddl:no[declared_cohort]

No other cell contradicts its prose, which is expected where 152 of 184 cells are gaps. Three discrepancies sit beside the column and are recorded in notes:

- The model cell reads "none (no family body)" for `census:partial:{class}`, `census:composite:{class}` and `ballot:tally:{poll_id}` while `manifests/signed_object.cddl` marks six or more members REQUIRED on each. The model and the CDDL disagree; the prose of CC 6.1.9 sides with the CDDL.
- CC 4.4.3.4.3.1 writes `subject_key_id` (singular) in the partnership member set and has `signed_at` and no `asserted_at` in the login `delegates_to` block; the CDDL has `subject_key_ids` (a set), requires `asserted_at` and has no `signed_at`.
- CC 4.4.3.4.1 names the grant's recipient `recipient_key_id` in the block and `attested_key_id` in the block's own comment, and spells one `wrap_algorithm` value three ways.
- CC 4.4.3.2.6: the inventory gist says an observer share is revoked by a `withdraws` against the grant; the text now says "the grant is never withdrawn". The inventory gist is stale.

## Member names against the CDDL

Checked against `manifests/signed_object.cddl` and `signed_object_v2.cddl`. Distinct member names appearing in a `proposed_value`: 24 found, 85 not found.

Found: `aggregation_algorithm_id`, `asserted_at`, `attestation_evidence`, `attestation_type`, `attested_key_id`, `attesting_key_id`, `delegation_purpose`, `delegation_valid_from`, `delegation_valid_until`, `dimension`, `history_on_join`, `key_id`, `mass_total`, `member_commitment_hex`, `n_eff`, `partial_a`, `partial_b`, `period`, `recovery_commitments`, `role`, `scope`, `share_count`, `share_index`, `source_count`.

Not found (written only in the prose): `K`, `action`, `affiliation_archetype`, `app_name`, `aspects`, `axis`, `baa`, `bilateral_pair_id`, `breach_notification`, `budget_bytes`, `cell_resolution`, `chain_of_custody`, `chunk_root`, `claim_namespaces`, `classification_scheme`, `cohort_subkind`, `compartment`, `compartments`, `confirms_halt_id`, `consensus_protocol`, `consensus_protocol_entrenched`, `content_id`, `content_sha256`, `crypto_tier`, `declared_cohort`, `derived_from`, `designated_officials`, `destination_hash`, `device_class`, `disclosure_bar`, `domain`, `duty`, `epoch`, `epoch_id`, `erasure_exempt`, `exposure`, `external_controller`, `family_key_id`, `family_name`, `geographic_constraint`, `hardware_class`, `hierarchy`, `identity_key_id`, `invocation_id`, `invocation_kind`, `jurisdiction`, `lawful_access`, `leaf_count`, `legal_basis`, `legal_weight`, `licence_classes`, `marking_binds_to_record`, `members`, `membership_basis`, `node_id`, `nonce`, `occurrence_key_id`, `outcome`, `pin_reserve_bytes`, `prev_head_digest`, `processor_chain`, `purpose`, `ranking`, `received_at`, `recipient_key_id`, `regulatory_profile`, `remaining_budget_bytes`, `resumes_halt_id`, `retention`, `reticulum_ed25519_pubkey`, `reticulum_x25519_pubkey`, `signed_at`, `size_cap_bytes`, `stance`, `statutory_basis`, `stream_id`, `subject_key_id`, `subject_kind`, `subscriber_key_id`, `transparency_mode`, `transparency_obligations`, `transport_destination`, `window_until`, `wrap_algorithm`, `wrapped_dek`.

The not-found names fall in four groups: the community and affiliation config record (about 30 names, CC 4.4.3.2.8); typed objects under one member (`identity_occurrence`, `key_grant`, the delivery receipt); preimage lines of the accord lifecycle domain; and objects with no row at all. `ranking` is in `manifests/choice_item.cddl` only.

## Sections where every statement is AGREE or FILLS

These could become a pointer to the table once the proposed cells land:

- CC 4.2.1 (AGREE)
- CC 4.2.3 (FILLS)
- CC 4.4.3.4.1 (FILLS)
- CC 4.4.3.4.2 (FILLS)
- CC 4.5.4 (FILLS)

CC 4.4.3.4.3.1 is nearly so: its member tables are FILLS throughout, with one cross-row equality (`bilateral_pair_id`) and two versioning rules left as prose. CC 4.4.3.2.8 likewise: 13 of 18 rows are FILLS, all on `group:roster`, and the section itself says the manifest carries the schema, which it does not yet.
