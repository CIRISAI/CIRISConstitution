# Part 2 — The Grammar

**Decimal range** `2.x` · **55 sections** · **page budget 17pp** · [← master index](../README.md)

> The minimal-and-adequate wire grammar: the envelope, the five primitives, conformance, and canonicalization.

---

## 2.1 `envelope` — The envelope

The envelope is where a claim becomes accountable. Every `scores` Attestation carries it. Each member binds the claim to evidence, names who may take it back, or records the conditions it was made under. This entry says what each member in its tables means, once, and the rest of the document refers back to it. A member defined elsewhere has its home in the CC column of [CC 2.6.1.7](#2.6.1.7). A member's type, its place relative to the signed bytes and its presence rule are the table of [CC 2.6.1.7](#2.6.1.7).

The members fall into three groups: those every row carries, those any row may carry, and those one family requires. An optional member the producer leaves out is read as its default, and no party writes that default into the signed bytes ([CC 2.6.1.1](#2.6.1.1)).

**Every row carries**

| Member | Meaning |
|---|---|
| `attesting_key_id` | The attester's `federation_keys.key_id`. A substrate field. |
| `attested_key_id` | The subject's `federation_keys.key_id`. A substrate field. |
| `dimension` | REQUIRED. The canonical namespace prefix and scoped leaf. The admitting substrate resolves it through the namespace of [CC 3.1](part_3_the_namespace.md#3.1) on all five row types and refuses a row that fails the gate ([CC 2.4](#2.4), [CC 3.1.7](part_3_the_namespace.md#3.1.7)). |
| `score` | REQUIRED on `scores`. A scalar in [-1, +1]. The sign is polarity and the magnitude is strength. The per-dimension table of [CC 3.1](part_3_the_namespace.md#3.1) names each dimension's polarity, and [CC 3.1.7](part_3_the_namespace.md#3.1.7) R4 holds the closed classes. |
| `confidence` | REQUIRED on `scores`. The attester's own confidence in the score, in [0, 1]. High magnitude with low confidence says "I believe this strongly but I might be wrong". Low magnitude with high confidence says "I am sure the truth is near neutral". |
| `cohort_scope` | REQUIRED, with no wire default. One of `self`, `family`, `community`, `affiliations`, `species`, `biosphere`, `federation`: the Scope axis of [CC 2.5](#2.5), a closed set of seven. It is the cohort tier the row is addressed to: who may see it, and the tier its holding claims stay within ([CC 5.2](part_5_transport_substrate.md#5.2)). The authoring default is the smallest scope ([CC 1.13.3.4](part_1_foundation.md#1.13.3.4)). |
| `subject_key_ids` | The consent-holder keys for this Contribution. Each entry MAY be a `federation_keys.key_id` or a canonical-hash identifier. Always present in the mirror, `[]` when empty; the column beside the row is absent when empty. An explicit `null` is refused ([CC 2.6.1.1.1](#2.6.1.1.1)). |

**Any row may carry**

| Member | Absent reads as | Meaning |
|---|---|---|
| `context` | nothing | Free-form scoping detail. Not parsed by the substrate; read by consumers, audit and RATCHET. |
| `evidence_refs` | nothing | URIs or content hashes pointing to backing evidence: a payment receipt, a licensing-body record, an observed interaction, a log entry, an audit-chain leaf. Optional in general; some dimensions in [CC 3.1](part_3_the_namespace.md#3.1) require it non-empty. |
| `valid_until` | nothing | A datetime in the [CC 2.6.2](#2.6.2) form. If set, consumer policy treats the attestation as stale after that point, independent of the row's own `expires_at`. It is REQUIRED on `session:*`, where it is the claim's signed horizon and a row without it is malformed ([CC 3.1.3.1](part_3_the_namespace.md#3.1.3.1)). |
| `epistemic_mode` | `direct` | The Epistemic-mode axis of [CC 2.5](#2.5): how the claim was formed. Consumers MAY weight by mode, a direct witness above hearsay. |
| `witness_relation` | `external` | `self`, `external` or `derived`: the attester's relation to the attested fact. `self` is the attested entity itself. `external` observed independently. `derived` inferred from other attestations or signed traces. Consumers weight by relation, so that self-attestation cannot game a verdict. |
| `oversight_mode` | `null`: consumer policy applies a per-cell default | `HITL`, `HOTL` or `HOOTL`: the human-control gradient under which the attestation was produced. |
| `occurrence_id` | `occurrence-0` | Which occurrence of a multi-occurrence agent deployment emitted the attestation: `occurrence-{n}` as the deployment assigns it, or `__shared__` for a shared-task emission. Self-asserted (below). |
| `occurrence_count` | `1` | Total occurrences in the deployment fleet, an integer at least 1. Self-asserted. |
| `occurrence_role` | `primary` | `primary`, `shared` or `replica`: the occurrence's role within the fleet. |
| `stake` | `reputational` | The Stake axis of [CC 2.5](#2.5). It composes with the attester's stake-backed-by attestations from [CC 3.1.1](part_3_the_namespace.md#3.1.1). |
| `community_id` | nothing | REQUIRED iff `cohort_scope` is `community` or `affiliations`; an affiliation is a community ([CC 4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8)). The `community_key_id` of the community this Contribution is scoped to ([CC 3.2](part_3_the_namespace.md#3.2) `community` subject_kind). One identity MAY belong to multiple communities, and this member says which community's roster gates visibility. A hierarchy edge resolves its `role_term` through it. The substrate rejects a community- or affiliation-scoped Contribution missing it. |
| `family_id` | nothing | REQUIRED iff `cohort_scope` is `family`. The `family_key_id` of the family this Contribution is scoped to ([CC 3.3.4](part_3_the_namespace.md#3.3.4) `family` subject_kind). One identity MAY belong to multiple families ([CC 4.4.3.4](part_4_composition_governance.md#4.4.3.4) Policy L), and this member says which family's roster applies. The substrate rejects a family-scoped Contribution missing it. |
| `delivery_mode` | `pull` | `pull` or `push`. On `pull`, subscribers discover holders through the holding claims at the content's scope (`custody:ack:v1` `here` rows, [CC 3.1.3.3](part_3_the_namespace.md#3.1.3.3)) and fetch with `ContentFetch` ([CC 5.3.2](part_5_transport_substrate.md#5.3.2)). On `push`, the substrate fans out to the live-delivery set, `fan_out = entitled ∩ reachable` ([CC 5.3.3.4](part_5_transport_substrate.md#5.3.3.4)), on links between members, directly or through the member relay tree ([CC 6.1.6](part_6_the_coherence_mathematics.md#6.1.6)). One-to-many delivery to a large audience stays pull-only ([CC 5.3.3.5](part_5_transport_substrate.md#5.3.3.5) E2). |
| `history_on_join` | `from_join` | `full` or `from_join`. Per target, and reserved for membership. On a stream, `full` is the producer's signal that the stream is kept ([CC 5.1](part_5_transport_substrate.md#5.1)). |
| `additional_scrubs` | nothing | **Quorum on a row** ([CC 2.4](#2.4) cosigned rows): a list of hybrid signatures (Ed25519 + ML-DSA-65) over the same canonical bytes as the row's own. Each is `{scrub_key_id, scrub_signature_classical, scrub_signature_pqc, cosigned_at?}` ([CC 2.6.1.7](#2.6.1.7)). This is the quorum carrier. |

**Members one family requires or carries**

| Member | On | Meaning |
|---|---|---|
| `session_id` | `session:*`, REQUIRED | The exchange a `session:*` claim is about, verbatim and case-preserved. With `community_id` it is the claim's key ([CC 3.1.3.1](part_3_the_namespace.md#3.1.3.1)). |
| `claimed_at` | `session:*`, REQUIRED | When the claiming occurrence took the session, in the [CC 2.6.2](#2.6.2) canonical form. The convergent merge orders on it ([CC 3.1.3.1](part_3_the_namespace.md#3.1.3.1)). |
| `scope` | `consent:state:granted` and `delegates_to`, REQUIRED | What the row covers: a bare token or an array of tokens. On a `consent:state:granted` row it is **the grant's scope** ([CC 3.3.1](part_3_the_namespace.md#3.3.1)): `retain`, `share`, `analyze`, `train` or `publish`, sub-scoped in the token as `retain:90d`. A grant naming no scope matches nothing. On a `delegates_to` it is the delegated scope set ([CC 4.4.3.4.3](part_4_composition_governance.md#4.4.3.4.3)). It is inside the signed bytes like every member. A consumer that does not know the member preserves it per [CC 2.1.1](#2.1.1) and MUST NOT compose a `capacity:*` verdict that ignores it. |
| `custody_state` | `custody:ack`, REQUIRED | `here` or `none`: whether the reporting device holds the blob ([CC 3.1.3.3](part_3_the_namespace.md#3.1.3.3)). A signed `none` is a custody fact, not an absence. |
| `group_kind` | `membership:proposal`, REQUIRED | `family` or `community`: which kind of group the proposal's target names ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). |
| `role` | `membership:proposal`, nullable; restated on `membership:acceptance` | The role the proposal offers the invitee. An acceptance restates it, and a widening that assigns a different role does not match ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). |
| `expires_at` | `membership:proposal`, REQUIRED | The proposal's signed expiry in the [CC 2.6.2](#2.6.2) canonical form, after its `asserted_at` and at most 30 days later. It is the proposal's own stated end: the member who concludes reads it on its own clock and signs the widening as the landing, and a late acceptance is closed ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). |
| `proposal_hash` | `membership:acceptance` and `membership:decline`, REQUIRED | The answered proposal's `original_content_hash`. With `references_attestation_id` it binds an answer to exactly one proposal ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). |
| `subject_sha256_ed25519_raw` | a `moderation:*` score, optional | The subject key named by the SHA-256 of its raw 32-byte Ed25519 public key, 64 lowercase hex per [CC 2.6.3](#2.6.3), so the row does not carry the key's cleartext label ([CC 2.4.1.1](#2.4.1.1)). A malformed value is refused at admission. |
| `attached_head_digest` | `trust:accepts:v1`, REQUIRED | The SHA-256, lowercase hex per [CC 2.6.3](#2.6.3), of the lineage head the acceptance edge attaches on: the signed roster record at that version ([CC 3.2](part_3_the_namespace.md#3.2) T4a). It is checked at the edge's **first admission only**, against the head's witness cosignatures and the root's `attach_window_secs`, and never re-checked on a node's own restore. An edge whose digest is later un-headed by a lowered `revoked_after` is read as naming that head's nearest verifying ancestor (T8 viii). |
| `attach_window_secs` | `trust:charter:v1`, optional | Integer seconds. The oldest a lineage head's newest counted witness cosignature may be for a consumer to *attach* to this root ([CC 3.2](part_3_the_namespace.md#3.2) T4a). It MUST exceed `witness_cadence_secs` plus the [CC 2.6.7](#2.6.7) skew tolerance. A charter that declares none makes its root attachable only through an out-of-band anchor to a specific head (T5). Never a validity leg for an attached root (T4). |
| `witness_cadence_secs` | the `trust:charter:v1` of a witnessed lineage, REQUIRED | Integer seconds. How often each directory witness MUST re-cosign the current head, unchanged: the equivocation-exposure window ([CC 3.2](part_3_the_namespace.md#3.2) T6). |
| `witness_quorum` | the `trust:charter:v1` of a witnessed lineage, REQUIRED | Integer. The cosignatures from distinct independent witnesses a head needs to count as witnessed. It MUST equal ⌊\|`witnesses`\|/2⌋ + 1 and be at least 2, or be `0`: witnessed mode off, whether or not `witnesses[]` already lists keys ([CC 3.2](part_3_the_namespace.md#3.2) T6). Any other value is refused at admission. |
| `witnesses` | the `trust:charter:v1` of a witnessed lineage, REQUIRED | Array of `SignedKeyRecord`: the lineage's witness directory ([CC 3.2](part_3_the_namespace.md#3.2) T6). It sits inside the charter's scrub-signed bytes, and therefore inside the genesis bundle for the shipped roots ([CC 5.3.4](part_5_transport_substrate.md#5.3.4)). Each is a lineage witness by this listing alone, whatever its `identity_type` ([CC 3.2](part_3_the_namespace.md#3.2) T6), and MUST be independent of the lineage: not a founder, not a member seat, not owner- or steward-bound to a founder. A listed key that is not independent at the head it cosigns is not counted toward `witness_quorum`, and the other cosignatures stand. A change is a charter re-scrub, witnessed by the directory before it. |
| `halt_fuse_secs` | the accord's `trust:charter:v1`, optional | Integer seconds. How long a `constitutional` halt signed by ONE holder stands before it lapses unless a strict majority of the standing roster confirms it ([CC 4.2.1.1](part_4_composition_governance.md#4.2.1.1)). **Absent means 86400.** The value is a constant of this document, read by the verifier, not a substrate-internal default. So a charter minted without the member is conformant and carries the 24-hour fuse. An explicit value overrides it, by re-scrub. |
| `recovery_commitments` | the accord's `trust:charter:v1`, REQUIRED ([CC 4.2.6](part_4_composition_governance.md#4.2.6)) | Object `{holder_key_id: commitment}`. Each commitment is lowercase-hex SHA-256 over the JCS array of the committed recovery key's `{key_id, pubkey_ed25519_base64, pubkey_ml_dsa_65_base64}` exactly as stored on its key record ([CC 3.2](part_3_the_namespace.md#3.2) T3), a one-element array here. It binds key material, never only the id. A holder rotates lost signing-key material by a self-`supersedes` under a key whose record hashes to its entry. |
| `consent_supersedes` | `consent:state:*`, optional | The prior consent-state row this one supersedes: a renewal, or the substrate's `consent:state:expired` naming the grant that lapsed ([CC 3.3.1](part_3_the_namespace.md#3.3.1)). |
| `deletion_window` | a producer's row, optional | The producer's commitment at publication: the deadline by which the consented payload must be deleted once consent ends, carried on the envelope of the row that holds it ([CC 3.3.1](part_3_the_namespace.md#3.3.1)). Absent means this member carries no commitment; no family default exists ([CC 2.6.1.7](#2.6.1.7)). |
| `widened_at` | a widening `supersedes`, REQUIRED | The instant a widening took effect, RFC 3339 with milliseconds ([CC 2.6.2](#2.6.2)). It is the `scrub_timestamp` of the widening's signature ([CC 4.4.3.3.1](part_4_composition_governance.md#4.4.3.3.1)). |
| `accord_root` | `accord:*` rows, REQUIRED | The `key_id` of the accord an `accord:*` row belongs to ([CC 4.2](part_4_composition_governance.md#4.2)). |
| `consent_basis` | `capacity:*` and `observation:access_assumption:v1`, carried | The consent grants a witness relied on, as `[* {principal, paths, attestation_id}]`. For each principal: the paths by which its grant reached the subject (`subject`, `occurrence_of`, `delegates_to`) and the `attestation_id` of the `consent:state:granted` row. Validated at the family's gate. |
| `n_eff_pr` | `capacity:*`, carried | The effective sample size of the scoring window as a participation ratio of the feature covariance spectrum. The gate reads this one. |
| `n_eff_h` | `capacity:*`, carried | The same window's effective sample size as an entropy perplexity, `exp(−Σ p·ln p)` over the normalised spectrum. Carried for audit, not gated. |
| `sample_size`, `feature_dim` | `capacity:*`, carried | Rows in the scoring matrix, and features per row. |
| `sample_size_gate`, `target_n_eff`, `min_feature_dim`, `n_eff_floor` | `capacity:*`, carried | The configured gates: the minimum sample size the score was gated on, the target effective sample size, the minimum feature dimension, and the effective-sample-size floor below which no score is emitted. |
| `window` | `capacity:*` and `observation:access_assumption:v1`, carried | The scoring or observation window, in rows. |
| `trace_level` | `observation:access_assumption:v1`, REQUIRED | `generic`, `detailed` or `full_traces`: the trace level the observed agent's install emitted at. |
| `occurrence_key_ids` | `observation:access_assumption:v1`, REQUIRED | A set: the occurrences whose rows the witness read. |
| `window_from`, `window_to` | `observation:access_assumption:v1`, REQUIRED | Start and end of the observation window, each RFC 3339 with milliseconds ([CC 2.6.2](#2.6.2)). |
| `channel_classes` | `observation:access_assumption:v1`, REQUIRED | A set: the classes of channel through which the witness saw the subject, as the emitter names them. |
| `amendment_digest` | `identity_amendment:v1`, REQUIRED | SHA-256 of the identity amendment as applied ([CC 3.1.5](part_3_the_namespace.md#3.1.5)). |
| `authorized_by` | `identity_amendment:v1`, REQUIRED | The `attestation_id` of the `deferral:response:approved:v1` row that authorised the amendment. |

**Three axes that do not depend on each other.** `cohort_scope`, with `family_id` or `community_id`, is the visibility axis. `subject_key_ids` is the revocability axis. `delivery_mode` is the delivery axis. Each is orthogonal to the other two ([CC 2.3.3](#2.3.3)). `cohort_scope` is the one mirror member a placement-touching re-sign may narrow; it is never re-authored ([CC 2.6.1.7](#2.6.1.7)).

**The group id is read inside the group.** Community content is encrypted at rest under the per-community DEK. Its holding claims reach the community's members only, and the same holds at every bounded scope ([CC 5.2](part_5_transport_substrate.md#5.2)). So `family_id` is consulted in-substrate and never on the wire to non-members.

**A targeted row names its producer (normative).** A row placed at a targeted scope (`family`, `community`, `affiliations`) names its own producer in `attested_key_id` and the party it is about in `subject_key_ids`. A targeted row naming a third party in `attested_key_id` is refused at admission ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)), with two registered exceptions. A key grant names the recipient occurrence there, and a roster version names the group ([CC 3.1.3](part_3_the_namespace.md#3.1.3), [CC 3.3.2](part_3_the_namespace.md#3.3.2)). For a `delegates_to` row `attested_key_id` is the delegate by the grammar's definition ([CC 2.4.1.2](#2.4.1.2)), and the producer rule is the `scores` row's.

**Whom a targeted row may name (normative).** At a targeted scope the keys a row lists in `subject_key_ids` are keys within the row's audience and no others. A key is within the audience in one of two ways. It is a member of the cohort by the authorized roster fold at the roster head the row names. That is the fold every bounded-scope door uses, so a key whose removal is in the row's causal past is outside. Or it is the key the family delivers the row to. These are a membership proposal's invitee ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)), a key grant's recipient ([CC 3.3.2](part_3_the_namespace.md#3.3.2)) and the owner's own node on an owner-binding ([CC 3.2](part_3_the_namespace.md#3.2)). A further family reaches outside its cohort only where its registration says so. A subject named by canonical hash is reached through its rule-3 proxy ([CC 2.4.1.1](#2.4.1.1)), which MUST be within the audience. A row naming a key outside its audience concludes nothing, since the check reads the roster at the head the row names; the reason reported is `subject_outside_audience`. A subject who can neither see nor contest a row has no standing to exercise, and [CC 3.4.5](part_3_the_namespace.md#3.4.5) promises the subject a read over the rows they are party to. Within the audience a row about another member is admissible. The named member's standing is that of `subject_key_ids` and [CC 4.5.5](part_4_composition_governance.md#4.5.5).

**What a subject key may do.** Each key listed in `subject_key_ids` has authority the substrate recognises to do two things. It may issue `withdraws` against this Contribution, under the rules and the kept list of [CC 2.4.1.1](#2.4.1.1). It may emit `consent:*` dimensions about this Contribution. An empty list means no subject authority: the producer alone has authority over the row.

**Cosignatures travel beside the row.** `additional_scrubs` is never inside the signed object, since a cosignature cannot be inside the bytes it signs. Each cosigner's role is read from the receiver's fold, not from the entry. The family declares which `consensus_protocol` the cosigners must satisfy. A cosigned row is retracted only by a cosigned `withdraws` ([CC 2.4.1.1](#2.4.1.1)). This is the general form of the ceremony plane's scrub set ([CC 3.2](part_3_the_namespace.md#3.2) T2).

**A change of oversight mode is the steward's act.** A mode shift is a stewardship act on the delegation plane, not a scored dimension. The human-control gradient an agent may operate under is bounded by the `agency:*` scopes its steward conferred ([CC 4.4.3.4.3](part_4_composition_governance.md#4.4.3.4.3)). So a shift is recorded as the steward issuing a **superseding `delegates_to`** ([CC 2.4.1](#2.4.1)) carrying the new scope set. `supersedes` keeps the prior grant as forward-only history ([CC 4.5.9.3](part_4_composition_governance.md#4.5.9.3)). This is the same naming and superseding machinery that governs a community's duty holders ([CC 4.5.5](part_4_composition_governance.md#4.5.5)). A consumer MAY treat an `oversight_mode` inconsistent with the agent's live grant as it treats any self-claim exceeding its delegation. There is **no `accountability:*` family**. Accountability is structural (the audit chain), never a named axis, and an `accountability:*` dimension does not admit under [CC 3.1.7](part_3_the_namespace.md#3.1.7) R2.

**Occurrence members are self-asserted.** `occurrence_id` and `occurrence_count` are not cryptographically bound to a fleet-attestation primitive. An adversary running a single key can claim any `occurrence_id`. This limit of the design is acknowledged at [CC 8.3.1](part_8_appendices.md#8.3.1). Substrate self-report attestations SHOULD carry `occurrence_id`, `occurrence_count` and `occurrence_role`. A compliance reviewer can then reconstruct, after the fact, which occurrence agreed to which mandate.

**Delivery and history beyond the member.** `delivery_mode` composes with [CC 4.4.3.2](part_4_composition_governance.md#4.4.3.2) Policy M for community-scoped delivery, and with [CC 5.3.3](part_5_transport_substrate.md#5.3.3) streaming for `live_stream` chunk-DAG delivery. At `community` and `affiliations`, `history_on_join` is carried and does not change what a new member receives. The tier's rule fixes that: a community joiner receives the current epoch's key and no earlier epoch's ([CC 4.4.3.4.1](part_4_composition_governance.md#4.4.3.4.1)). What a kept stream's joiner can fetch is bounded by `min(operator depth cap, chunk-eviction horizon)` ([CC 5.1](part_5_transport_substrate.md#5.1), catch-up bound). An evicted-epoch grant returns `ContentMiss`, never a silent gap.

**`epistemic_mode` and `witness_relation` are two things.** They co-vary at the edges but name different concerns. `epistemic_mode` names the *process* by which the claim was formed. `witness_relation` names the *relational position* of the attester to the attested. Detector-derived attestations carry both: `epistemic_mode: derivative` and `witness_relation: derived`. Most encyclical-sourced translations are `witness_relation: external` with `epistemic_mode: hearsay`. When in doubt, set both.

### 2.1.1 `forward-compatibility` — Forward-compatibility rule

The envelope is meant to grow without breaking the peers already speaking it. Two rules make that safe. The canonical-bytes contract means a new field never silently changes what an old signature covers. The unknown-field discipline means a consumer never rejects an envelope merely for carrying a field it has not learned yet.

> **Canonical-bytes contract**: the canonical-bytes encoding of this envelope for signing follows [CC 2.6.1](#2.6.1) (JCS over the envelope object; defaults are interpretation-time, NOT encoding-time; relay MUST preserve member presence/absence exactly as the producer signed). Optional fields with documented defaults in the table above ride the CC 2.6.1.1 omit-vs-materialize rule. Conditional-required fields are NOT optional-with-default and substrate rejects mis-shape per [CC 2.3.1](#2.3.1) + [CC 4.5.2.1](part_4_composition_governance.md#4.5.2.1) + [CC 4.5.12.2](part_4_composition_governance.md#4.5.12.2).

A Conforming Consumer that receives an envelope carrying a field-name it does not recognize MUST:

- Preserve the unknown field on read (do not strip).
- Preserve it on re-emission if the Consumer is also acting as a Producer relaying the attestation.
- NOT use it in verdict composition.
- NOT reject the envelope on the basis of the unknown field alone.

Producers introducing a new envelope field MUST follow the [CC 2.6.4](#2.6.4) versioning rules: a new field with a documented default is a MINOR bump; a field whose absence breaks consumer semantics is a MAJOR bump.

## 2.2 `conformance` — Conformance levels

Interoperability needs named roles so that "conforming" means the same thing to every peer. CEG is the **CIRIS Epistemic Grammar**, the wire grammar this specification defines ([CC 8.1.1](part_8_appendices.md#8.1.1)); the roles below are named for it. A **Producer** is any peer that emits Contributions onto the federation wire. A **Consumer** is any peer that reads and composes verdicts over received Contributions. A **Substrate Implementation** is the storage + transport + crypto layer underneath both.

Three normative conformance profiles set the floor each role must meet:

1. **CEG-Conforming Producer (CCP)** — emits well-formed envelopes per [CC 2.1](#2.1), signs per [CC 2.6.1.7](#2.6.1.7) ([hybrid-sig]), respects reserved-prefix rules per [CC 3.4](part_3_the_namespace.md#3.4), declares its `oversight_mode` and `witness_relation` per [CC 2.1](#2.1).
2. **CEG-Conforming Consumer (CCC)** — verifies hybrid signatures ([CC 5.3.2.4.3.1](part_5_transport_substrate.md#5.3.2.4.3.1)), enforces reserved-prefix rules at admission ([CC 3.4](part_3_the_namespace.md#3.4)), implements at least Policy A ([CC 4.4.3.8](part_4_composition_governance.md#4.4.3.8)) with the default aggregation rules from [CC 4.4.2](part_4_composition_governance.md#4.4.2), MUST honor `null` placeholder/dev hardware-class rejection per [CC 4.2.2](part_4_composition_governance.md#4.2.2).
3. **CEG-Conforming Substrate (CCS)** — implements the storage + transport guarantees referenced in [CC 5.3.2](part_5_transport_substrate.md#5.3.2) + [CC 5.3.1](part_5_transport_substrate.md#5.3.1), including idempotent replication, full-SHA blob verification before consumption ([CC 5.3.2](part_5_transport_substrate.md#5.3.2)), and witness-quorum multi-party admission per [CC 5.3.1](part_5_transport_substrate.md#5.3.1).

Sections that follow MAY add per-feature conformance subsections; the three profiles above are the minimums.

## 2.3 `subject_keys` — `subject_key_ids` semantics

Consent is incomplete if only the producer of data has authority over it. `attesting_key_id` carries **producer authority**; `subject_key_ids` carries **subject authority**, for content where the subject of the data is not the producer of the data. This is the wire-format expression of the Autonomy and Non-maleficence principles: a person who appears in someone else's data can still pull it.

### 2.3.1 `subject_kind-subject-2` — Subject-bearing dimensions (governance requirement)

Per [CC 4.5.2](part_4_composition_governance.md#4.5.2), dimensions whose namespace pattern names a subject (e.g., `observed:user:{key_id}:*`, `epistemic:about:{key_id}:*`, `agent_files:*:{subject_target}`) MUST carry `subject_key_ids` containing that subject. The substrate MAY reject admission of subject-naming dimensions that omit `subject_key_ids`. This closes the default-leak failure mode where subject-bearing content publishes without wire-level subject authority.

### 2.3.2 `federation-key` — Federation-key vs canonical-hash identifier

A subject is not always a federation-enrolled identity. The two forms below let `subject_key_ids` name either an enrolled key that can sign for itself or an external party that cannot — without losing the external party's revocation rights.

`subject_key_ids[i]` MAY be either:

1. **A `federation_keys.key_id`** — the subject is a federation-enrolled identity that can sign on its own behalf. Direct revocation: subject signs a `withdraws` against this Contribution; substrate admits under rule 2 of [CC 2.4.1.1](#2.4.1.1). Wire form: the bare `key_id` (no tag).
2. **A tagged canonical-hash identifier** — the subject is an external party with no federation_keys row (a platform user-id, channel-id, content-sha256-bound entity, etc.). The substrate cannot verify a signature from this entity directly; **revocation rides a `delegates_to` proxy chain** under rule 3 of [CC 2.4.1.1](#2.4.1.1). Wire form: a tagged string per CC 2.3.2.1 below.

Both forms are admitted; the canonical-hash variant is distinguished by its explicit tag ([CC 2.3.2.1](#2.3.2.1)).

#### 2.3.2.1 `registry-canonical` — Canonical-hash wire form + preimage convention

A CEG-Conforming implementation cannot interoperate without pinning two things: (a) how a canonical-hash entry is distinguished from a `federation_keys.key_id` entry on the wire, and (b) what string is hashed (the preimage). Both are normative.

**Wire form — tag REQUIRED**. A canonical-hash entry MUST carry the tag `canonical:{hashalg}:{hex}`:

- `{hashalg}` — the hash algorithm; `sha256` is the v1 algorithm. Algorithm-agility: future hashes (e.g. `sha3-256`) extend this position without ambiguity
- `{hex}` — the digest in [CC 2.6.3](#2.6.3) canonical hex (lowercase, unpadded, byte-length-exact: 64 chars for sha256)
- Example: `canonical:sha256:ff7c5632dae6ef3ae7f6283bd35268bc7910332414aa8a1c35a1645ca0295f61`

**Why the tag is mandatory and bare-hex is rejected**: a directory MAY still hold a `federation_keys.key_id` of the older form `hex(sha256(ed25519_pubkey))` — a **lowercase 64-char hex string**. A `key_id` is otherwise the `<label>-<fingerprint>` form of [CC 2.6.8](#2.6.8), which contains `-` and base32 letters and is therefore format-distinguishable from a bare hash by construction. The tag stays mandatory because such older ids exist and because a subject reference MUST never depend on a consumer's guess about which form it is reading. A bare canonical-hash (also lowercase 64-char hex) would be **format-indistinguishable** from a key_id. A "base64 key_id vs hex canonical-hash" disambiguation heuristic FAILS because Registry key_ids are themselves hex fingerprints, not base64 pubkeys. The tag is therefore load-bearing, not cosmetic. The CC 2.6.3 hex rule governs the `{hex}` segment only; the `canonical:{hashalg}:` prefix is a tagged-union discriminator outside CC 2.6.3's scope and is exempt from the "no separators" rule.

**Scope of the fingerprint check:** the check is the MUST of [CC 2.6.8](#2.6.8). A consumer verifies a `key_id`'s fingerprint suffix against the public key it obtains **at registration and at pairing** — the proof-of-possession door — for fedIDs and roster keys ([CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3)). A held key registered under an older or otherwise non-matching id is not re-keyed or refused by a migration (the record is history), it simply cannot be re-registered or introduced at pairing under that id. The bundle-pinned anchors (`ciris-canonical-1`, `humanity-accord*`) and family ids are not fingerprint-suffixed and are verified by the genesis bundle pin ([CC 5.3.4](part_5_transport_substrate.md#5.3.4)), not by this rule. The fingerprint rule is separate from the roster-id *form* rule of 3.3.6.3 ([CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3)). A `device-<hex>-<fp>` id passes the fingerprint check and is refused by the roster door for its form, on the roster door's own schedule.

**Preimage convention — `{platform}:{entity_kind}:{id}`**. The string hashed to produce `{hex}` MUST be:

```
preimage = "{platform}:{entity_kind}:{id}"
hex = sha256_hex_lowercase(utf8_bytes(preimage))
```

Parsing is **split-on-first-two-colons**: the substring before the first `:` is `{platform}`; the substring between the first and second `:` is `{entity_kind}`. **Everything after the second `:` is `{id}` verbatim, and MAY itself contain colons** (so an identifier like `@alice:example.org` survives). Rules:

- `{platform}` — REQUIRED; MUST match `[a-z0-9][a-z0-9._-]*` — ASCII lowercase, and therefore **colon-free** by construction. Open vocabulary per [CC 4.5.1.1](part_4_composition_governance.md#4.5.1.1). Canonical seeds: `discord`, `slack`, `twitter`, `matrix`, `email`, `phone`, `github`, `xmpp`, `irc`
- `{entity_kind}` — REQUIRED; the same production as `{platform}`. Canonical seeds: `user`, `channel`, `guild`, `room`, `group`, `address`
- `{id}` — REQUIRED; the platform's **stable, immutable** identifier, **verbatim** (case-preserved — some IDs are case-sensitive). MUST be the immutable account/object identifier (a numeric snowflake; a server-qualified user id; a UUID), **NOT** a mutable handle/username/display-name. Using a mutable handle breaks subject-identity stability the moment the user renames. `{id}` is the **only** component that MAY contain a colon.
  - **Production (normative)** — `{id}` MUST be a non-empty sequence of Unicode **scalar values**. It MUST NOT contain any surrogate code point (U+D800–U+DFFF), any C0 or C1 control (U+0000–U+001F, U+007F–U+009F — so NUL, TAB, LF and CR are all rejects), or U+FEFF. It MUST NOT begin or end with a character bearing the Unicode `White_Space` property. Interior whitespace is admissible (visible and platform-stable); leading or trailing whitespace is not (invisible, and it would silently fork the digest). No length bound is imposed: the preimage never rides the wire — only its 64-hex digest does.
  - **Why scalar values and not "any UTF-8-ish string"** — `utf8(id)` MUST be **total**, and it is undefined for an unpaired surrogate. A Rust implementation cannot construct the string at all. A Python implementation using `surrogatepass` emits WTF-8 and computes a **different** digest from the same nominal input. Admitting only scalar values makes the encoder agree across implementations by construction. An implementation handed an unpaired surrogate MUST reject it under P1 and MUST NOT substitute U+FFFD — substitution is a repair.

**Preimage bytes (normative).** The hashed octets are exactly, and only:

```
preimage_bytes = utf8(platform) ‖ 0x3A ‖ utf8(entity_kind) ‖ 0x3A ‖ utf8(id)
hex            = lowercase_hex( SHA-256(preimage_bytes) )
```

`0x3A` is the ASCII colon, contributed exactly twice by the construction. There is **no** length prefix, **no** domain-separation label, **no** trailing NUL, **no** BOM, and no framing of any other kind. An implementation that adds any of these computes a different subject and its gate diverges from every other gate.

**P1 — no normalization at hash time.** A producer MUST NOT case-fold, trim, pad, or Unicode-normalize (NFC / NFD / NFKC / NFKD) any component before hashing. `{id}` is hashed exactly as the platform issues it. An input that does not already satisfy the productions above MUST be **rejected, not repaired**. A repairing producer and a rejecting producer would otherwise compute different subjects from the same input, which is the divergence this clause exists to close.

**P2 — injectivity is structural, not statistical.** Because `{platform}` and `{entity_kind}` admit no colon, the joined string reverse-parses to exactly one triple (the `{id}` production only shrinks the admitted domain, so injectivity survives it a fortiori). `("p","k:a","b")` and `("p","k","a:b")` are not two spellings of one preimage: one is an admissible triple, the other is a rejected input. The delimiter therefore carries the full anti-collision property over the admitted domain, and no length prefix is needed to obtain it. The `lp(x) = u32_be(len(x)) ‖ utf8(x)` discipline is the [CC 6.1.3](part_6_the_coherence_mathematics.md#6.1.3) rule for **substrate framing objects that never enter JCS**. A canonical subject is a string value *inside* a [CC 2.1](#2.1) envelope field and sits on the JCS side of that boundary. So adopting `lp` here would cross the CC 6.1.3 seam and re-spell every digest below to buy a property P2 already gives. The delimiter form stands.

**P3 — the tag and the digest are governed, not re-opened.** `{hex}` is [CC 2.6.3](#2.6.3) lowercase hex; `{hashalg}` is exactly `sha256` for v1; an exact tag admits neither case variance nor whitespace. Uppercase hex, `SHA256`, a non-v1 algorithm, a bare untagged hex string, and any leading or trailing whitespace are all **rejects**.

Together these make the rule-(3) `delegates_to` proxy chain (`canonical_hash ∈ T.subject_key_ids`) match across producers: every CEG-Conforming producer naming the same `(platform, entity_kind, immutable_id)` triple computes the same `{hex}`, hence the same tagged wire string.

**Conformance vectors**:

| Preimage | sha256 hex | Wire form |
|---|---|---|
| `discord:user:123456789012345678` | `ff7c5632dae6ef3ae7f6283bd35268bc7910332414aa8a1c35a1645ca0295f61` | `canonical:sha256:ff7c5632…0295f61` |
| `discord:channel:987654321098765432` | `af23411c3c6faa55a788660ea29719669b9c4e4ea4b6ab9568247d9f646f05dd` | `canonical:sha256:af23411c…646f05dd` |
| `matrix:user:@alice:example.org` (id contains colons) | `16d4d0bf478835a9af68cdaac730a29b36f82bf0dfe2073237ee4980f6b975d9` | `canonical:sha256:16d4d0bf…f6b975d9` |
| `twitter:user:1455079377986420736` (numeric id, NOT @handle) | `10243ba010bf159a45197d368f91c025ef6ac1eb7f42ca32e55b414d90c861c2` | `canonical:sha256:10243ba0…90c861c2` |
| `email:address:alice@example.org` | `04481a02fccfc8d99a47bde4f0563dd360d425b0734e8fcd8d5dd7198d0a263f` | `canonical:sha256:04481a02…98d0a263f` |

**Reject vectors** — each MUST be refused at the gate, never normalized into acceptance:

| Input | Rejected because |
|---|---|
| `ff7c5632…0295f61` (untagged) | the tag is REQUIRED; bare hex is format-indistinguishable from a `key_id` |
| `canonical:md5:…` | `{hashalg}` is not the v1 algorithm |
| `canonical:SHA256:ff7c5632…` | the alg segment is not exactly `sha256` |
| `canonical:sha256:FF7C5632…` | `{hex}` is not [CC 2.6.3](#2.6.3) lowercase |
| `canonical:sha256:ff7c5632…␣` (leading/trailing space) | an exact tag admits no padding |
| triple `("Forum","user","1234…")` | `{platform}` is not ASCII-lowercase — reject, do NOT case-fold (P1) |
| triple `("discord:x","user","1")` | `{platform}` contains `:` (P2) |
| triple `("discord","user","")` | `{id}` is empty; the production requires ≥ 1 scalar value |
| triple `("discord","user","1234␣")` (trailing space) | `{id}` ends in `White_Space` — reject, do NOT trim (P1) |
| triple `("discord","user","12␊34")` (embedded LF; likewise CR, TAB, NUL) | `{id}` contains a C0 control |
| triple `("matrix","user","@a\uD800:example.org")` (unpaired surrogate) | not a Unicode scalar value — `utf8(id)` is undefined; reject, never WTF-8 and never U+FFFD |

#### 2.3.2.2 `canonical_binding` — Rule-(3) proxy vs `canonical_binding` — distinct mechanisms

These are **two distinct mechanisms**, not one:

- **Rule-(3) `delegates_to` proxy** ([CC 2.4.1.1](#2.4.1.1) admission rule 3) — *ongoing* revocation authority for an un-enrolled subject. A federation-enrolled key (typically the agent holding data on behalf of the external party) carries `delegates_to(canonical_hash → agent_key, scope: [consent_revocation])`; the agent proxies revocation ([CC 2.4.1.1](#2.4.1.1)). The subject never enrolls; the agent acts for them indefinitely.
- **`canonical_binding`** — *retroactive identity claim*. A now-enrolled federation key asserts "I AM the entity behind `canonical:sha256:{hex}`", binding past canonical-hash subject entries to its real identity. The binding is a claim consumers weigh, and it admits nothing by itself: it opens no `withdraws` under rule (2) ([CC 3.3.14](part_3_the_namespace.md#3.3.14)).

`canonical_binding` is **NOT a new admission rule** (no "rule 5"). It is a bare `scores` row on `identity:canonical_binding:{canonical_hash}`, self-asserted by the enrolling key ([CC 3.3.14](part_3_the_namespace.md#3.3.14)). Proof that the key controls the preimage is the consumer's to weigh. Withdrawal for that subject stays the rule (3) proxy.

#### 2.3.2.3 `subject_kind-payload` — `subject_kind` is a payload-level discriminator

`subject_kind` (e.g. `consent_record`, `consent_replication` ([CC 3.3.7](part_3_the_namespace.md#3.3.7)), `key_grant`, `takedown_notice`, `community`, `family`, `identity_occurrence`, `location_proof`) is **not a typed member of the [CC 2.1](#2.1) table**. It rides inside the signed `attestation_envelope` untyped by the substrate, under the `*` row of the [CC 2.6.1.7](#2.6.1.7) signed-object table, and is preserved on relay ([CC 2.1.1](#2.1.1)); the substrate neither validates nor indexes it. The typed envelope members are those the [CC 2.1](#2.1) table names (`cohort_scope`, `subject_key_ids`, `community_id`, `family_id`, `delivery_mode`, and the rest). `subject_kind` is the discriminator that selects which [CC 3.3](part_3_the_namespace.md#3.3) payload schema applies, validated at the family's own gate, parallel to the `sub_kind` an `external_content` row carries. The CC 3.3.5 `consent_record` example and any conformant producer payload agree byte-for-byte: `"subject_kind": "consent_record"` is a member of the signed bytes, not a column of the row.

#### 2.3.2.4 `bilateral` — Bilateral ratification is consumer-policy

Per [CC 3.3.5](part_3_the_namespace.md#3.3.5) step 4: a bilateral partnership is "ratified iff both halves present and live under the same `bilateral_pair_id` with `stance: granted`" — and this predicate is **consumer policy**, NOT registry-normative. Ingest-layer builders produce the two halves WITHOUT enforcing ratification. The substrate admits each half independently; composition of the pair into a ratified partnership is a downstream read-time computation, never an admission gate.

### 2.3.3 `cohort-orthogonality` — Orthogonality with `cohort_scope` AND `delivery_mode` (3-axis)

The envelope keeps visibility, revocability, and delivery as three independent concerns so they can be reasoned about — and enforced — separately. They compose without overlap:

| Axis | Field | Authority | Names |
|---|---|---|---|
| **Visibility** | `cohort_scope` + (`family_id` or `community_id` when set) | Producer-side | Who can SEE the data |
| **Revocability** | `subject_key_ids` | Subject-side | Who can REVOKE the data |
| **Delivery** | `delivery_mode` + `history_on_join` | Substrate / subscriber | Who actively RECEIVES the data + how the substrate fans out |

All three may coexist on the same Contribution:

```
A cohort_scope: family contribution
  carrying subject_key_ids: [user_canonical_hash]
  carrying delivery_mode: push + history_on_join: from_join
  carrying family_id: <acme_household>

publishes the bytes at family-cohort visibility (cohort_scope);
the user retains revocation authority (subject_key_ids);
the substrate actively fans out to currently-reachable members
  with new-members getting forward-only content (delivery_mode + history_on_join);
the named family roster gates the membership set (family_id).
```

This orthogonality is load-bearing for the multi-occurrence consent shape: subject-side revocation applies federation-wide regardless of producer's `occurrence_id`; per-occurrence lifecycle consent is a producer-side concern, separately tracked.

The delivery axis is the **third orthogonal axis**: visibility + revocability alone give the substrate no envelope-level handle on who actively *receives* content and how the substrate fans out. Per [CC 5.3.3](part_5_transport_substrate.md#5.3.3), three optional envelope fields + the CC 5.3.3 endpoint section + a delivery extension to [CC 4.4.3.2](part_4_composition_governance.md#4.4.3.2) Policy M supply it.

### 2.3.4 `self-as-subject` — Self-as-subject ceremony

When `attesting_key_id ∈ subject_key_ids`, the Contribution is a **self-consent ceremony** — the same identity is attesting AS subject AND producer. This composes naturally with the CEG-native agent's self-attestation pattern: agent attests `identity:current` about itself with `subject_key_ids = [self.key_id]`, asserting consent-authority over its own identity claims.

### 2.3.5 `shape` — The shape

`subject_key_ids` is an OPTIONAL list. When present, each entry names a party with substrate-recognized authority over this Contribution's continued processing ([CC 2.1](#2.1), [CC 2.3](#2.3)). The basic shape:

> A consent record is a signed declaration by a subject about the substrate's continued processing of content where that subject appears.

The medical record, photo, interview, training-datum, and group-chat cases all share the same shape — a producer publishes a Contribution; one or more subjects appear in it; the subjects retain revocation authority. A single shape carries thirteen distinct content cases uniformly.

### 2.3.6 `absent` — Empty/absent = status-quo

`subject_key_ids` as `[]` in the mirror (the column beside the row absent) is the status-quo shape (producer-only authority; same as a baseline Contribution carrying no subject authority) ([CC 2.1](#2.1), [CC 2.3](#2.3)). Consumers that don't read the field see status-quo behavior. Subject authority is additive at the envelope layer — adding it never changes how an existing consumer reads an envelope that omits it.

## 2.4 `primitive` — The primitive set — 1+4

The whole grammar reduces to five wire primitives: one workhorse that makes claims, and four structural composers that operate on the claim graph itself. Minimal-and-adequate is the design discipline — fewer primitives mean a smaller surface to attack, audit, and prove conformant, which is what Integrity asks of the wire.

**The row-type slot is closed: the five, and nothing else (normative).** Every row on the attestation plane names its type in one slot: the row's `attestation_type`, mirrored in the signed envelope. That slot admits exactly the five primitives of this section, closed by [CC 1.7](part_1_foundation.md#1.7). There is no second class of row. A **carrier** — a self-attestation with no score, no subject and no dimension, read by no fold — is a claim with its family rule missing. A holder directory without a family has no declared audience, so bounded content would advertise its existence to everyone, and a fold would have to exclude it by type. The holding claim is `custody:ack:v1` at the content's scope ([CC 3.1.3.3](part_3_the_namespace.md#3.1.3.3)). A set of wraps in one row has, as its only structural property, a union that only grows, which one `scores` row per recipient already gives. A key grant is `key_grant:{axis}:v1`, one row per recipient ([CC 3.3.2](part_3_the_namespace.md#3.3.2)). A row naming `holds_bytes` as its type is refused `attestation_type_unregistered`.

*The gate.* A substrate MUST refuse at admission, with **`attestation_type_unregistered`**, any row whose type is not one of the five, byte-compared — on local emission and on replication alike. The gate is an **allowlist** built from the registry's `_meta.row_types` ([CC 3.1.7](part_3_the_namespace.md#3.1.7)); the absence of a check on a free-text column is not a gate, and a type that is merely *storable* is not thereby admitted. A row of the five that names `holds_bytes` as its `dimension` is refused.

*The dimension gate follows the dimension, not the row type.* A `dimension` on **any** of the five MUST resolve through the namespace exactly as it does on `scores`: the case rule, the version tail, the reserved and gated stems. That holds for the job label on a `delegates_to` row as much as the family on a `scores` row. A row type is never a way around the namespace.

*No more of them.* The slot is amended only by a change to this section, in a release of this document, through the [CC 1.7](part_1_foundation.md#1.7) refutation bar: a claim that cannot be expressed by the five plus envelope composition. A component that needs a new row type files it here **before** it ships; a type found in code and not here is a defect in the code. A row of an unregistered type that a substrate already holds when it adopts this rule is reported to the operator, is neither served nor replicated, and is not deleted. The registry carries the closed list and vectors for it.

**Cosigned rows: quorum is an envelope property, not a row type (normative).** A single-signer row cannot carry a quorum's act, and [CC 2.4.1.1](#2.4.1.1) rules 1 and 2 would let one signer or one subject undo one. Cosigned rows close both, so group records, membership widenings and removals, partner records and the `ciris-canonical` scrub set are rows on the plane. **Any of the five MAY carry `additional_scrubs[]`** ([CC 2.1](#2.1), [CC 2.6.1.7](#2.6.1.7)): hybrid signatures over the same canonical bytes, beside the row, each by a key whose role the receiver's fold names. Those signatures are the general form of the scrub set the ceremony plane already uses ([CC 3.2](part_3_the_namespace.md#3.2) T2).

The **family declares its `consensus_protocol` source**: the group the row is about, the accord, or — for `licensure:{community_key_id}` ([CC 2.4.1.2.1](#2.4.1.2.1)) — the authority community named in the dimension. **Admission:** the row is admitted when its cosigners satisfy that protocol, judged on the *receiver's own* fold over the members at the roster head the row names ([CC 2.7.4](#2.7.4)). **Collection:** a row short of its protocol by signatures alone is not refused; it waits, as the kernel states ([CC 2.7.3](#2.7.3)). Such a row is held and its cosignatures are collected as `cosign:pending` and `cosign:signature` rows ([CC 3.1.3](part_3_the_namespace.md#3.1.3)), served to the group's active members only, for the hold window of [CC 3.3.4](part_3_the_namespace.md#3.3.4).

A cosigned act is named by its quorum key, the digest of what its signers signed with no signature in it. So every node that assembles a sufficient set holds the same act whichever signatures it gathered, and a row that names the act resolves on each of them. **Retraction of a cosigned row is by the same quorum** ([CC 2.4.1.1](#2.4.1.1) rule 0), so no single signer and no subject can retire a community, un-name a charter or retract a roster event.

What this brings onto the base, each as a registered family in [CC 3.1.3](part_3_the_namespace.md#3.1.3):

- **roster versions** (`group:roster:v1`, the T6 head, with `prev_head_digest` and `charter_digest` as envelope members, [CC 3.1.3](part_3_the_namespace.md#3.1.3)),
- **membership events** (`membership:widening:v1` / `removal:v1`, cosigned, and `resignation:v1`, signed by the leaving member alone ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)), beside the single-signer proposal, acceptance and decline), and
- the **key plane**:
  - a key claim (`key:record:v1`, attester = the key, admitted by **proof of possession** against the keys it carries, the one stated exception to resolve-the-attester). Renewal is a `supersedes` by the same key and rotation a record of the next key cosigned by the old one, each bounded as [CC 2.4.1.1](#2.4.1.1) states; an anchor scrub or accord co-scrub is a cosignature),
  - occurrences (`identity:occurrence:v1`, signed by the identity or a live occurrence) and
  - revocations (`key:revocation:v1`, never withdrawn, subject = the key digest, `revoked_after` only ever lowering).

The roster fold, the acceptance gate and T7 recovery are unchanged; only their inputs become rows. **Admission order:** a row is admitted only once its signer's key-claim row is held, and a row signed by a key not yet held is retryable, since a row waits for what it names ([CC 2.7.3](#2.7.3)).

What stays off the plane, by definition, is not a claim: payload bytes (sealed chunks, and the A/V plane's symbols), transparency-log heads and cosigns ([CC 5.3.1](part_5_transport_substrate.md#5.3.1) framing), the wholeness corpus, node-local derived state, an agent's private runtime. **Accord evidence** (proposals and participations as rows) is not on the base: it would amend the entrenched [CC 4.2](part_4_composition_governance.md#4.2) surface. Any such change is bound by this constraint: the invocation's domain-separated canonical bytes MUST travel inside the envelope unchanged, and the kill switch MUST NOT depend on any plane gate beyond verifying those bytes and the holder roster.

### 2.4.1 `structure` — The four structural composers

The four structural composers act on the attestation graph itself, not as score-claims on entities. They are how an attester delegates authority, replaces a row, retracts a row, or admits a row was false:

| `attestation_type` | What it does | Envelope shape |
|---|---|---|
| `delegates_to` | A authorizes B to sign on A's behalf within a bounded scope | `{scope[], delegation_purpose, delegation_valid_from, delegation_valid_until}` — `delegation_valid_until` is **REQUIRED, at most 365 days (365 × 86 400 s) after `delegation_valid_from`**, on any edge carrying `sub_delegation`, `license`, `grant`, `moderate`, `takedown`, `review` or `slash`, or sitting in an affiliation's `hierarchy` ([CC 4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8) C); a perpetual or over-ceiling edge is refused `delegation_term_required`; `delegation_valid_from` absent means the edge's own `asserted_at`, and `delegation_valid_until` absent on an edge that needs no term is open-ended, never malformed — `scope` is the [CC 2.1](#2.1) member (a bare token or a set; the one name for this wire member, never `delegated_scope[]`) |
| `supersedes` | This attestation row replaces a prior one by the same attester, or by the same protocol for a cosigned row. Another signer's row is replaced only where that signer has signed its own step-down ([CC 3.2](part_3_the_namespace.md#3.2)). A widening replaces nothing ([CC 3.5.1](part_3_the_namespace.md#3.5.1)) | `{references_attestation_id, supersession_reason, differs_in[]}` |
| `withdraws` | A party [CC 2.4.1.1](#2.4.1.1) admits retracts a row (does NOT claim it was false) | `{references_attestation_id, withdrawal_reason}` |
| `recants` | My prior attestation was false at issuance — admits epistemic error | `{references_attestation_id, recantation_reason, what_was_false}` |

**Translation implications**:

- A **doctrinal-development** claim ("this version extends but does not contradict the prior version") is `supersedes` with `differs_in: ["scope", "evidence_refs"]` — NOT `recants` (which would assert prior was false).
- An **acknowledged-error** claim ("the prior framing was wrong; I admit the mistake") is `recants` — distinct from `withdraws` ([CC 2.4.1.1](#2.4.1.1)).
- A **prudent-retraction** ("I'm withdrawing without claiming it was false; context has changed") is `withdraws`.
- An **authority-source claim via delegation** ("this constitutional position derives from authority-key X in scope Y") is `delegates_to` with X as `attested_key_id`. This is the [CC 2.4.1.2](#2.4.1.2) reuse pattern for authority-source claims. It replaces what would otherwise need a `grounding:{tradition}:{principle}` prefix that fails [CC 1.2](part_1_foundation.md#1.2) T2.

#### 2.4.1.1 `withdraws` — Who may take a row back

A `withdraws` row retires its target as a cut does ([CC 2.7.7](#2.7.7)). An act under the target that the withdrawal has among its ancestors stands. One that has the withdrawal in its own past, or is concurrent with it, does not count. It does not say the target was false. The rule below widens who may retract a row; the primitive itself does not change.

A node MUST admit a `withdraws` against a target row `T` when one line of this table holds. It MUST also admit the key a `retirement:decided` row names in `decided_by`, against that row ([CC 7.5.5](part_7_lifecycle_stewardship.md#7.5.5)). It MUST refuse any other with `federation_withdraws_not_admitted`.

| Rule | Who signs the withdrawal | Condition |
|---|---|---|
| 0 | the quorum of `T`'s family | `T` carries `additional_scrubs[]` ([CC 2.4](#2.4)). The withdrawal is cosigned under the same `consensus_protocol`, counted over the members at the roster head the withdrawal names ([CC 2.7.4](#2.7.4)). Rules 1 to 4 do not reach `T`: a quorum's act is undone only by a quorum. |
| 1 | the key that signed `T` (`T.attesting_key_id`) | none |
| 2 | a key `T` names in `subject_key_ids` | `T`'s family is not on the kept list |
| 3 | a proxy for a party `T` names by canonical hash | the proxy holds a live `delegates_to` chain to that hash whose scope includes `consent_revocation`, and `T`'s family is not on the kept list |
| 4 | a delegate of anyone in rules 1 to 3 | the delegate holds a live `delegates_to` from them, and the kept list binds the delegate as it binds them |

**Any one named party is enough.** Where `T` names several parties, an admitted withdrawal from one retires `T` for all of them, since any bound voice ends a relation alone ([CC 2.7.5](#2.7.5)). A reader MUST NOT wait for a majority or for the others ([CC 4.4.3.5.4](part_4_composition_governance.md#4.4.3.5.4)).

**A withdrawal reaches forward only.** Acts the withdrawal has among its ancestors still stand. A copy a peer took before the withdrawal reached it is not recalled by the wire. One case reaches behind: a key revoked as compromised is void back to its `revoked_after` bound, stated below.

**The kept list (the anti-Goodhart retraction dual).** A named party acting under rules 2 to 4 MUST NOT withdraw these rows about itself:

- a `capacity:*` or `detection:*` finding made by someone else;
- a `licensure:*` or `revocation:*` row, where the licensee's path is `reconsideration:{grounds}`;
- a duty-holder's record on the accountability trail: a `moderation:*` report or action, a `hard_case:*`, a `slashing:*` verdict, a `quarantine:*` marker ([CC 4.5.5](part_4_composition_governance.md#4.5.5));
- an act of a body under a declared legal-weight class, such as a conviction or a licence ([CC 2.4.1.2.1](#2.4.1.2.1), [CC 4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8));
- a `takedown_notice:*`, where the path is the counter-notice its basis names ([CC 3.3.2](part_3_the_namespace.md#3.3.2));
- an agent's own `trace:*`, where the path of a person named in it is withdrawing consent ([CC 3.1.5](part_3_the_namespace.md#3.1.5)).

An affiliation withdraws no statement about itself, whatever the statement. Its path is reconsideration and the reader's composition. A named party contests a kept row by `reconsideration:{grounds}`, and it holds standing there ([CC 4.5.5](part_4_composition_governance.md#4.5.5)). The consent and scoring context of this list is [CC 3.4.5](part_3_the_namespace.md#3.4.5).

**Why the list exists.** Consent can be taken back, so a named party may retire a row about itself. A finding is not consent. A party that could retire the adverse rows about itself and keep the rest would launder its reputation.

**Between peers the person named retracts.** A `withdraws` of peer speech about oneself is admitted under rule 2. It is a signed act the row's audience sees, and it leaves the speaker attributed.

**Never withdrawn.** A `key:revocation:v1` row is withdrawn by nobody, because revocation is non-rollbackable ([CC 3.1.1](part_3_the_namespace.md#3.1.1)). An entity revocation ([CC 3.1.1](part_3_the_namespace.md#3.1.1)), an occurrence revocation, a key grant and a cosignature already sent are never withdrawn either ([CC 3.1.3](part_3_the_namespace.md#3.1.3)).

**The proxy of rule 3.** Rule 3 serves a party that holds no federation key: a platform user id, an entity bound by a content hash, any other outside party. A federation-key signer, typically the agent that holds data for that party, emits `delegates_to(canonical_hash → agent_key, scope: [consent_revocation])` when the proxy is set up. Its later `withdraws` against a row carrying that hash in `subject_key_ids` is admitted under rule 3, on the conditions of [CC 3.3.14](part_3_the_namespace.md#3.3.14). The proxy attaches only after the party's identity is established out of band, reaches no row on the kept list above, and is suspended while two bindings for the same person compete. The hash is the tagged `canonical:{hashalg}:{hex}` wire form with the `{platform}:{entity_kind}:{id}` preimage convention of [CC 2.3.2.1](#2.3.2.1). A `canonical_binding` is a different act: a retroactive identity claim that promotes a canonical hash to a real `key_id`, which opens rule 2. It is not an admission rule ([CC 2.3.2.2](#2.3.2.2)).

**Only the signer recants.** A `recants` row says `T` was false, and only `T`'s signer may say so. A named party who holds the claim factually wrong answers with a `scores` row of negative polarity on a contradicting dimension. A named party's authority covers consent, which can be taken back. It does not cover truth.

**Which rule admitted it.** A substrate SHOULD record which rule (0 to 4) admitted each `withdraws` in `federation_attestations` metadata. A consumer can then compose policy on it, for example weighing a named party's own withdrawal above a proxy's.

**What the signer keeps (normative).** A named party's withdrawal takes the row out of every audience. It does not take the signer's words from the signer. The signer MAY keep the withdrawn row and its `withdraws` together at `cohort_scope` `self`. A node MUST NOT serve that copy to anyone, the row's former audience included, and the copy counts toward no score, standing or grant. The keep covers a signer's own words about another party, and it gives way to every duty to delete. A signer that committed to a deletion window deletes within it and keeps no copy ([CC 3.3.1](part_3_the_namespace.md#3.3.1), D1). An affiliation holds the row only as the retention and erasure limbs of its record allow ([CC 4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8)). A signer running a decay protocol on the named party's data follows its stages ([CC 4.4.3.5.1](part_4_composition_governance.md#4.4.3.5.1)). The signer MAY hand the pair to a party that holds a duty to judge it. Filed with a room's named moderator it is a duty-holder's record ([CC 4.5.5](part_4_composition_governance.md#4.5.5)). Given to a body acting under a declared legal-weight class it is evidence before that body ([CC 4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8)). Saying the same thing again to the audience is a new row, and the party it names may withdraw that one in turn. Shown to its former audience beside the retraction, the row would be read by everyone who read it before, and the retraction would be a label. Deleted from its signer as well, the retraction would take the signer's own words. The retention rule carries this copy as a declared gate ([CC 6.1.5](part_6_the_coherence_mathematics.md#6.1.5) N5).

**`revoked_after` — the revocation history bound (normative, optional member).** A key-plane revocation MAY declare `revoked_after: rfc3339` — a bound before which statements signed by the revoked key **still stand**: everything after the bound is suspect; everything before it is not unmade. Resolution is a **pure read-time function**: a claim signed by K is valid iff its `asserted_at` precedes `K.revoked_after`, so a partitioned node converges when the revocation arrives late — the same fold shape as consent. Absent member = revoke-all. **`revoked_after` is an upper bound, not a fact**: a compromise may long predate its detection. A later revocation MAY lower it and MUST NOT raise it. Where a key carries multiple revocations the effective bound is the **minimum** `revoked_after` across all of them, absent-member sorting as negative infinity. That keeps the fold commutative and the resolution a pure read-time function, so partitioned convergence is preserved ([CC 3.2](part_3_the_namespace.md#3.2)).

**A key revocation names its subject by the key's digest, not its `key_id` (normative).** A `key_id` is `<label>-<fingerprint>`, and the label is the holder's own keystore alias in cleartext. Revocations replicate federation-wide, so a revocation addressed by `key_id` would tell every node the subject's label — `frank-laptop` — whether or not that node held the key's record. The revocation is a `key:revocation:v1` row ([CC 3.1.3](part_3_the_namespace.md#3.1.3)), never withdrawn. The subject is therefore **`revoked_key_sha256_ed25519_raw`**: the SHA-256 of the revoked key's raw 32-byte Ed25519 public key, 64 lowercase hex digits ([CC 2.6.3](#2.6.3)). It is the full digest whose truncation is the `key_id`'s fingerprint, stable for the life of the key and carrying no label. The member is REQUIRED. `revoked_key_id` is OPTIONAL: when present it MUST name a key whose raw-key digest equals the subject, and the row waits until that key is held and concludes nothing on a mismatch. When absent it is bound as explicit JSON `null`. The signed revocation binds **eight** members inside its own `revocation_envelope`: `revocation_id`, `revoked_key_id` (string or `null`), `revoked_key_sha256_ed25519_raw`, `revoking_key_id`, `reason` (string or `null`), `revoked_at`, `effective_at`, `scrub_timestamp`. Every one is REQUIRED in the bytes, an absent optional bound as explicit `null` (an omitted member is refused as unbound). `revoked_after` is the ninth, optional, absent or `null` meaning unbounded. This is the key plane's own signing contract: `scrub_timestamp` is inside the bytes because it is the anti-rollback ordering key, and the explicit `null` is the one exception to the no-null rule of [CC 2.6.1.1.1](#2.6.1.1.1), which governs the attestation envelope. Three consequences follow. **(1) A revocation may precede the record it revokes**: one naming only the digest MAY be admitted for a key the receiver does not hold, and takes effect the moment a key with that digest is held. Authority on this plane is the revoker's and is judged without the subject's record. **(2) Readers ask by digest**: "is key K revoked?" is answered over K's digest, so one revocation reaches every `key_id` that names the same public key, and the per-subject anti-rollback ordering ([CC 5.3.2.3](part_5_transport_substrate.md#5.3.2.3)) keys on the digest. **(3) Self-revocation** is recognised when the revoker's own key digests to the subject, whether or not `revoked_key_id` is present. A `moderation:*` score MAY likewise name its subject key by **`subject_sha256_ed25519_raw`** (same spelling; a malformed value is refused) instead of exposing its label. Family and community rosters list members by `key_id`, so a roster's holders see the labels, and roster-removal rows are addressed by `key_id` — they reach only the audience that already holds the roster. The revocation's signed object is this contract; it carries no member table in [CC 2.6.1.7](#2.6.1.7), and its signature rule is the key record's.

**Who may revoke a key (normative).** Three may revoke a key, and no other. The key revokes itself. Its owner revokes it under the owner-binding ([CC 3.2](part_3_the_namespace.md#3.2)). The roster that seats it revokes it by its count: the eviction door of a self roster ([CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3)), and for a room key the room's removal ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). A key is its owner's, so ending it without the owner is a cut, and a cut takes standing ([CC 2.7.7](#2.7.7)). A revocation signed by any other key revokes nothing.

**A key's own end (normative).** A `key:record` whose `identity_type` contains `user` or `accord_holder` MUST NOT state `valid_until`, since no person loses their self to a clock. Any other `key:record` whose `identity_type` contains `node` or `agent` MUST state `valid_until`, unless it is a room key of a private room ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). A pseudonym's key record ([CC 5.4.6](part_5_transport_substrate.md#5.4.6)) MAY state `valid_until` and need not, since it is neither a self nor a node or agent. The bound is read from the record alone. `valid_until` MUST NOT be before the record's `asserted_at`, nor more than `key_record_max_secs` after it. A record that breaks the bound, or omits or carries `valid_until` against this paragraph, is refused `key_record_out_of_window`. The requirement binds a record whose `asserted_at` is at or after `key_record_end_required_from`, and an earlier record that states no end stays endless. A key is live at an instant when one of its records covers that instant and the key has not revoked itself by then ([CC 2.7.5](#2.7.5)). It has ended when every one of its records has ended. No row of another key enters that reading, so no third party ends a key and no third party revives one.

A key renews by signing a further record that `supersedes` its own earlier record. Renewals that do not name each other all count, and the key lives to the greatest end they state. A renewal MAY be signed after the end of the record it supersedes, and it then revives the key at every node that holds it. A rotation is a record of another key that names the old key's record. It carries the old key's signature, made at an instant inside that record. A rotation hands on what the old key may hand on, and never extends the old key. Two rotations of one key, neither naming the other, hand on nothing until a rotation names both ([CC 2.7.7](#2.7.7)). An owner settles such a pair for a key it owns by revoking one. A key with no owner stays contested.

A row lapses when its signer's key has ended and no row that has not lapsed names it, directly or through other rows ([CC 2.7.5](#2.7.5)). A revocation never lapses. A lapsed row MUST NOT count in any tally, score, walk of trust or other reading. Its own verdict is unchanged: a row signed while its key was live stays what it was. A row that has not lapsed counts as before, whatever its key's end. A node MAY stop serving a lapsed row and MAY drop it. A node MUST NOT stop serving or drop a row that has not lapsed. It MUST NOT keep a digest by which to refuse a dropped row again. A row whose signed instant no held record of its key covers is retryable, as a row signed by a key not yet held is.

A signer's instants are its own word. Whoever holds an ended key's private half can revive it with a further record, and no reader can tell when that record was signed. Only a key's own revocation makes its end final ([CC 2.7.9](#2.7.9)). A key made for one task MAY revoke itself at its end; that revocation is never withdrawn and is kept. An implementation SHOULD state the greatest end the bound allows. A key made for one task SHOULD state an end that fits that task.

**A purge is a tombstone, not a `withdraws` (normative).** Rules 0–4 are consent paths — the author's or the subject's. A row the purger neither authored nor is the subject of (a mock-LLM trace, a harness identity's rows, a row no peer can verify) is removed by a **tombstone by digest on its plane**. The tombstone is authorised by a cosigned `takedown_notice` under the trust root's `consensus_protocol` with basis `steward_purge` ([CC 3.3.2](part_3_the_namespace.md#3.3.2)), naming the selection digest, the reason and the ledger. A substrate MUST NOT admit a `withdraws` forged on the author's behalf for this. A `withdraws` does not even claim falsity, and a purge says the row never belonged. **A purge never tombstones or deletes a key.** A selection naming a `federation_keys` row is refused, and a by-actor selection takes the actor's own rows and their derived rows. Key retirement is a separate `key:revocation:v1` signed under this section's own paths. The root's quorum has no path over a key it does not own: a root that could revoke strangers' keys would be an authority roster by another name ([CC 3.4.7](part_3_the_namespace.md#3.4.7)). So an ownerless key stays registered and inert while its rows go, and the admission gates stop its next ones. A key's own end is not a purge. A `node` or `agent` key ends by its own record, and its rows lapse by the rule of its own end above, by no third party's act. Entities go by `revocation:{entity_type}:{reason}`, bytes by the bytes-plane tombstone ([CC 4.5.3](part_4_composition_governance.md#4.5.3)). **The accountability record is outside the root's reach.** `revocation:*`, `key:revocation:v1`, `moderation:*`, `moderation_track_record:*`, `slashing:*` and **`hard_case:*`** rows are never purgeable, by the root or by anyone. Trust-root moderation is not trust-root history-editing. `hard_case:*` is in the set because an equivocation proof (`hard_case:lineage_equivocation`, [CC 6.1.1](part_6_the_coherence_mathematics.md#6.1.1) N4) or a liveness transition (`community_liveness_stalled` / `_restored`, [CC 3.2](part_3_the_namespace.md#3.2) T7) is an adverse row about a root. That root's only purge door is its own quorum, which is the subject, and the anti-Goodhart dual admits no subject-side removal of an adverse row. The substrate that produced the proof withdraws it under rule 1, or recants a false one, and nobody else. A structural composer (`withdraws`, `recants`, `supersedes`) is purged only together with its target, and a `delegates_to` only when a party to it is in the selection. A purge removes a party, never a third party's standing. **Derived rows follow the reason, and the selection digest says which.** A `scores` row whose evidence was never admissible input (mock, harness, unverifiable) is purged with its evidence, in the same selection and ledger: its subject never ran, so it attests nothing. So are a trace's own `trace:complete:v1` attestation and the bytes a purged holding claim holds, transitively over `evidence_refs`. A score over real evidence later taken down on a legal basis stands, its `evidence_refs` resolving to the tombstone. The door refuses a purge without the notice (`purge_unauthorised`) and one whose selection digest differs from the authorised one (`purge_selection_digest_mismatch`); every purged id is appended to a ledger attested at the next tag.

#### 2.4.1.2 `delegates_to` — Authority-source claims via `delegates_to`

A constitutional or framework claim can name its source-of-authority by emitting `delegates_to` against an `attested_key_id` representing the framework, with `scope` naming the principle. Example: a Ubuntu-substrate commitment in [CC 1.13.1](part_1_foundation.md#1.13.1) commitment 2 can be expressed as `delegates_to` against the `ubuntu_relational_substrate` framework-key with `scope: ["personhood_constitutive_by_attestation"]`. Reuses the existing structural primitive rather than introducing a `grounding:{tradition}:{principle}` prefix (which would fail [CC 1.2](part_1_foundation.md#1.2) T2 — "tradition" claims are interpretive, not mechanism-descriptive).

**Owner-binding is the single-valued purpose.** A `delegates_to(user → node/agent)` carrying `delegation_purpose: owner_binding` is the owner-binding, held to the single-owner invariant ([CC 3.2](part_3_the_namespace.md#3.2), *Who owns a key*). This is the **one** `delegation_purpose` that is single-valued — act-on-behalf, hierarchy ([CC 4.5.13](part_4_composition_governance.md#4.5.13)), and authority-source delegations remain **multi-parent** DAGs.

#### 2.4.1.2.1 `authority-triad` — Licensure, grant, delegation — three concepts, three wire discriminators (normative)

`delegates_to` is one of three ways a key comes to hold something. The three are routinely conflated because only one of them has a structural primitive. Two of them run through different machinery: licence authority rides the [CC 3.2](part_3_the_namespace.md#3.2) founder-quorum machinery, and role authority rides the [CC 4.4.3.4.3](part_4_composition_governance.md#4.4.3.4.3) delegation scopes ([CC 3.3.9](part_3_the_namespace.md#3.3.9)). The triad is stated here, at the grammar.

| | **Licensure** | **Grant** | **Delegation** |
|---|---|---|---|
| who gives it | an **authority** | the asset's **owner / steward** | a **principal** |
| what it confers | standing to practise | access to a specific thing | agency to act *for* someone |
| what it is about | the subject | the asset (hash, stream, balance) | the principal's own powers |
| ends by | the authority revokes / suspends | rotation, expiry, exhaustion | the principal withdraws; attenuation |
| **chains?** | **no** | **no** | **yes** — attenuated, depth-capped, revocable per link |
| wire discriminator | dimension prefix on `scores`: `licensure:{authority_id}` / `attestation:license_validity` | dimension prefix on `scores`: `key_grant:{axis}:v1` ([CC 3.3.2](part_3_the_namespace.md#3.3.2)), or the `consent:scope:*` family | **structural primitive**: `attestation_type: delegates_to` |

**The transitivity row is the discriminator of record.** Only delegation composes. That is why only `delegates_to` gets a graph walk ([CC 4.1.1](part_4_composition_governance.md#4.1.1) depth cap, cycle rejection, aggregate-weight cap). A licence does not chain: holding one confers no power to issue one. A grant does not chain: receiving access confers no power to re-grant it (below). Any design that walks a licence or a grant transitively has mistaken it for a delegation.

The professional analogue is exact, and it is the domain this federation licenses. A physician assistant holds a **licence** from a board, practises under a supervising physician's **delegated** authority, and holds **privileges** (a grant) at one hospital for named procedures. These are three grantors and three revocation paths, reported as separate categories by the registries that track them.

**Provenance is the authority, not a delegation (normative).** A licence's provenance is its **`authority_id`**, carried inside the dimension. Where the authority is a collective it is constituted by **quorum** ([CC 3.3.9](part_3_the_namespace.md#3.3.9) / [CC 3.2](part_3_the_namespace.md#3.2) founder-quorum). It is **never** conferred by `delegates_to`. Three things stay distinct:

- *who grants the licence* (the `authority_id`);
- *who vouches for the attester* (the trust walk, `infra:attest`);
- *what external legal force it carries* (a **bridge** on an in-grammar record — [CC 8.3](part_8_appendices.md#8.3): bridges compose with the record, they are never alternatives to it).

**Who may be a licensing authority, and what admits a licence (normative).** Anyone. `authority_id` names a key: a `federation_keys.key_id`, or an organisation, an affiliation whose keys resolve through its `membership:{stage}` seats on the community record and the `delegates_to` edges of its hierarchy ([CC 4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8), [CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). The words "X holds licence authority for `A`" mean exactly that X's key *is* `A`, or holds a `license`-scoped delegation whose chain resolves to `A` ([CC 4.4.3.4.3](part_4_composition_governance.md#4.4.3.4.3)). There is no roster of permitted authorities and a substrate checks none. A `licensure:{A}` row admits under the same gate as every other row on the wire. The gate is that the reader trusts the emitter's root or has consented to receive from it ([CC 4.4.3.8](part_4_composition_governance.md#4.4.3.8); the contextual-integrity rule: a medical licensure claim reaches a reader only along a flow that reader's trust or consent admits). The row reaches nobody else. Per [CC 4.4.4](part_4_composition_governance.md#4.4.4) a Sovereign key scoring `licensure:CA_medical_board` is wire-identical to a Registry steward scoring it; consumer policy weights by attester. The provenance paragraph above says "by quorum". That is a statement about the authority's *own* governance where it is a collective: the [CC 3.2](part_3_the_namespace.md#3.2) founder quorum that constitutes a community's key, the [CC 3.3.9](part_3_the_namespace.md#3.3.9) M-of-N write rule under which an affiliation issues a licence. That statement is never an admission gate a substrate applies to somebody else's authority.

**What the fold keys on (normative).** The `licensure:{A}` status set for a subject folds only rows whose emitter resolves to `A`: `A`'s key, or a `license` chain to `A`. A row under `licensure:{A}` signed by a key that is neither `A` nor `A`'s delegate is admitted if trusted or consented to. Such a row is *testimony about* `A`'s licensure, not `A`'s licensure: it stays out of the `(subject, A)` fold and composes at consumer confidence. That is how a stranger's absorbing `revoked` binds nobody. The one refusal is on the `license` scope itself: an issuance whose delegator chain does not resolve to `A` is **`licensure_delegator_not_authority`**. There is no bootstrap: `A`'s first `licensure:{A}` row is signed by `A`, or, for a keyless affiliation, cosigned by its quorum.

*Authority is judged at issuance.* It is judged over the issuance's own causal past under the cosigned-row rule, never at receipt, because this is a shared verdict every node has to compute identically. A `withdraws` of a link in the chain stops every issuance that has it in its own past, or is concurrent with it ([CC 2.7.7](#2.7.7)). It does **not** reclassify licences the withdrawal has among its ancestors. The authority ends those with `suspended` or `revoked`.

*A licence has no public default.* It is a claim about a person, so its `cohort_scope` is the authority's declared choice *per licence class* in the affiliation's charter, the smallest that fits ([CC 1.13.3.4](part_1_foundation.md#1.13.3.4)). A practice licence meant to be checked by strangers is federation-scope by its nature; an internal credential is not. At whatever scope the class declares, the licence and the **authority head** a verifier needs (the roster version, the protocol, the `license` edges on the chain) travel together. Where the class is not public they are **re-emitted** to the readers who validate them, never carried at the wrong scope (`cohort_scope` is in the signed bytes) and never by widening the roster. They are re-emitted as new rows, signed and cosigned again, each addressed to one reader by `for_key_id` and naming no reader in `subject_key_ids`.

*An organisation-named authority.* An organisation is an **affiliation** ([CC 4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8)), and an organisation-named authority is its `community_key_id`. Its authority set is whatever the affiliation's *current* `consensus_protocol` admits. A `licensure:{community_key_id}` row is a **cosigned row** ([CC 2.4](#2.4)) whose protocol source is the authority named in the dimension. That is the one case where the source is neither the group the row is about nor the accord. A `license`-scoped chain roots at that quorum; one founder suffices only where the protocol says so.

**A grant is non-transferable by default (normative).** A `key_grant` conveys access to an asset; it does **not** convey the power to convey it. An onward grant is a **new grant issued by the asset's owner or steward, or by a holder of a `grant`-scoped delegation from them** ([CC 4.4.3.4.3](part_4_composition_governance.md#4.4.3.4.3)), never a forwarded one. `rotation_chain` is supersession lineage, not onward transfer. **Possession of the data-encryption key is not issuance authority.** Every recipient necessarily holds the DEK, having unwrapped `wrapped_dek`. So the ability to wrap a new grant is *necessary* and never *sufficient*: the cryptographic gate stops a stranger, and only the authority gate stops a recipient. A substrate MUST refuse at admission a `key_grant` whose issuer neither owns or stewards the asset nor holds a `grant`-scoped delegation over it, exactly as it refuses an issuance whose delegator lacks the underlying authority. A design that treats receipt of a grant, or possession of its key, as authority to re-grant has, again, mistaken a grant for a delegation.

#### 2.4.1.3 `recants` — The `recants` distinction matters

CEG types epistemic-error-admission as a wire primitive distinct from retraction, because the Recursive Golden Rule applies to attesters: admitting error is a primary act, not a derivative of retraction. Consumer policy can apply different trust adjustments to attesters who `recant` versus those who `withdraw`.

### 2.4.2 `scores` — The workhorse: `scores`

The federation has exactly **one** workhorse attestation primitive. Every claim about an entity — positive or negative, identity or capability or behavior or state or commitment, by any attester source — is expressed as a `scores` attestation on a named dimension.

Illustration of member placement, not canonical bytes: the signed object is `attestation_envelope` as [CC 2.6.1.7](#2.6.1.7) lays it out, with the `row` mirror and `asserted_at`, and an optional member is omitted, never null.

```
// Wire shape (Persist's federation_attestations row):
attestation_type: "scores"
attesting_key_id: <attester's key_id>
attested_key_id: <subject's key_id>
attestation_envelope: {
  "dimension": "<canonical-namespace-prefix>:<scoped-leaf>",
  "score": <f64 ∈ [-1.0, +1.0]>,
  "confidence": <f64 ∈ [0.0, 1.0]>,
  "context": "<free-form scoping detail>",
  "evidence_refs": ["<URI or hash referencing backing evidence>",...],
  "valid_until": "<ISO8601 datetime, optional>",
  "epistemic_mode": "<direct | crypto | hearsay | derivative | appeal>", // optional; default 'direct'
  "witness_relation": "<self | external | derived>", // optional; default 'external'
  "oversight_mode": "<HITL | HOTL | HOOTL>", // optional; omitted when unset
  "occurrence_id": "<occurrence-N | __shared__>", // optional; omitted when unset
  "occurrence_count": <int ≥ 1>, // optional; omitted when unset
  "occurrence_role": "<primary | shared | replica>", // optional; omitted when unset
  "stake": "<free | reputational | capital | cryptoeconomic>" // optional; default 'reputational'
}
```

Full field semantics in [CC 2.1](#2.1).

## 2.5 `reasoning` — The reasoning grammar — the eight axes

The wire stays minimal precisely because the richness lives in how consumers *reason* about it. These eight axes are **not wire fields**; they are the canonical questions a consumer can ask about any Attestation. Nothing in the wire prescribes the verdict — the axes are the vocabulary the verdict is built from.

| Axis | Question | Values |
|---|---|---|
| **Polarity** | Direction of the claim | Positive / Negative / Neutral / Indeterminate{reason} |
| **Object** | What the claim is about | key_id (entity) / attestation_id / contribution_id |
| **Time** | When is the claim valid | `asserted_at` + optional `valid_until`; consumer composes with substrate `expires_at` |
| **Epistemic mode** | How was the claim formed | direct / crypto / hearsay / derivative / appeal |
| **Reversibility** | Can the attestation be reversed | rollbackable / non-rollbackable (consumer policy + per-prefix rule) |
| **Stake** | What's backing the attester's claim | free / reputational / capital / cryptoeconomic |
| **Scope** | At what scale does the claim apply | self / family / community / affiliations / species / biosphere / federation |
| **Inter-attestation relations** | How does this attestation relate to others | standalone / refers-to / supersedes / withdraws / recants / corroborates / contradicts / clarifies |

`biosphere` is a distinct Scope value from `species` (which is the Homo sapiens cohort). See [CC 4.1](part_4_composition_governance.md#4.1) for the `planet` colloquial alias note.

## 2.6 `foreword` — Canonical form and the signed object

CEG — the CIRIS Epistemic Grammar — is the federation's language for making **structured, signed, machine-checkable claims about reality and each other**. It is the wire format the federation's peers speak. Everything above is that grammar; everything below is the canonicalization discipline that makes one peer's bytes verify identically on another peer's machine — the mechanical foundation of the Integrity principle.

The grammar has exactly five wire-format primitives (one workhorse + four structural composers) and an open-vocabulary dimension namespace organized by mechanism-descriptive prefixes. Consumers compose verdicts from primitive attestations using the policies in [CC 4.4](part_4_composition_governance.md#4.4); nothing in the wire format prescribes what verdict to reach.

CEG is **substrate-consuming**: it sits above the federation substrate (storage, crypto and transport) and below the application tier (the agent). It does not author primitives in the substrate it consumes; it composes policy over them. It is also **substrate-supplying** for the second-tier consensus and detection components — they own slices of the dimension namespace and emit attestations that other CEG consumers read.

This specification has **two readerships**:
- **Implementers** of federation primitives consuming or emitting CEG attestations: read CC 1.13-CC 4.5 normative.
- **Translators** mapping substantive content into CEG envelopes: read CC 8.1–8.2.

Both readerships should read [CC 1.13](part_1_foundation.md#1.13) first.

### 2.6.1 `envelope-canonicalization` — Envelope canonicalization — JCS + the omit-vs-materialize rule

This rule closes the canonical-bytes ambiguity that arises whenever an envelope carries optional fields with documented defaults — `epistemic_mode`/`witness_relation`/`occurrence_*`/`stake`, `oversight_mode`, `subject_key_ids`, `family_id`, `community_id`. Without it, two honest peers can disagree on the bytes and a valid signature fails to verify.

**The hazard is structural.** Suppose Producer A omits an optional field (relying on the [CC 2.1](#2.1) documented default) and Relay R re-serializes the attestation with the default materialized into the byte stream. The canonical bytes then diverge and the Ed25519 + ML-DSA-65 signatures fail to verify. The rule below makes the discipline explicit and normative: every party — producer, substrate, relay, consumer — must make the same choice, and that choice is "preserve what the producer signed, exactly." ([CC 2.6.1.1](#2.6.1.1))

#### 2.6.1.1 `round-trip` — The round-trip rule — defaults are interpretation-time, not encoding-time (normative)

The canonical bytes are computed over **the literal envelope members the producer signs**. Optional fields that the producer omits MUST NOT be materialized into canonical bytes by any party — producer, substrate, relay, or consumer. Optional fields that the producer explicitly emits (even at their default value) MUST be preserved in the canonical bytes by any party. Documented defaults from [CC 2.1](#2.1) are **interpretation-time semantics**, not encoding-time content.

**One envelope, as the vectors carry it.** The object below is the admit vector `scores_minimal` of [`manifests/signed_object_vectors.json`](../manifests/signed_object_vectors.json), copied verbatim: the `row` mirror, `asserted_at`, and the claim's own members, with `epistemic_mode` omitted. [CC 2.6.1.7](#2.6.1.7) is the authority for the shape; this copy illustrates member placement and is not itself the canonical bytes (those are JCS of the object, [CC 2.6.1.3](#2.6.1.3)).

```json
{
  "row": {
    "attestation_id": "5684f46c-749c-282f-bb10-0d74759dcde7",
    "attesting_key_id": "alice-ctffz2edis",
    "attestation_type": "scores",
    "attested_key_id": "bob-fx44qqfrla",
    "subject_key_ids": [],
    "cohort_scope": "federation"
  },
  "asserted_at": "2026-10-18T12:00:00.000Z",
  "dimension": "expertise:cardiology:en:v1",
  "score": 0.8,
  "confidence": 0.9
}
```

The admit vector `scores_explicit_default` is the same object with `"epistemic_mode": "direct"` emitted at its default value. A producer that omits the member and one that emits it compute different canonical bytes (the second includes the `"epistemic_mode":"direct"` member) and emit different signatures. **Both signatures verify under their respective canonical bytes.** Both are **semantically equivalent** — a CEG-Conforming Consumer evaluates `effective_epistemic_mode(envelope) = envelope.epistemic_mode if present else "direct"` and proceeds identically. The wire-format admits both encodings; the consumer policy admits no observable difference.

**Relay discipline (normative)**. A substrate, relay, or consumer that re-stores or forwards an attestation MUST preserve member presence/absence exactly as the producer signed it:

- Stripping an explicitly-emitted default ("the producer wrote `epistemic_mode:direct` but I'll save bytes by removing it") MUST NOT happen
- Materializing an omitted default ("the producer omitted `epistemic_mode` so I'll fill in `direct` for clarity") MUST NOT happen
- A relay forwards the canonical octets as received. A relay that re-serializes from a parsed object at all MUST emit JCS ([CC 2.6.1.3](#2.6.1.3)): canonical member order on re-emission is required, and nothing else changes — member presence/absence stays fixed

This composes with the [CC 2.1.1](#2.1.1) forward-compatibility rule (which already mandates preserving unknown fields on read and re-emission); the same preservation discipline extends to known-optional fields.

##### 2.6.1.1.1 `canonicalization-array` — Array ordering + byte-field + timestamp encoding (normative — the three determinism rules JCS does NOT pin)

JCS ([CC 2.6.1.3](#2.6.1.3)) canonicalizes **object member order** but is silent on three things that still let two conformant producers emit different bytes (and therefore non-verifying signatures, the same hazard). All three are pinned here once, globally, for every CEG envelope:

1. **Array element order.** An array field is one of two kinds, stated in its [CC 2.1](#2.1)/[CC 3.1](part_3_the_namespace.md#3.1) definition:
 - **Set-semantics** (order carries no meaning) — elements MUST be **lexicographically sorted by their JCS string form (UTF-16 code-unit order, ascending)** before signing. This is producer-independent: any producer building the set in any order yields identical bytes. **`subject_key_ids[]` and `delegates_to.scope[]` are set-semantics → sorted.**
 - **Sequence-semantics** (order is meaningful) — elements retain their as-authored order. **`transport_destination.aspects[]`** (RNS hash preimage order), **`key_grant.rotation_chain`** (supersession lineage), and **`evidence_refs[]`** (producer-asserted order) are sequence-semantics → preserved. A field's definition MUST declare which kind it is; absent a declaration, set-semantics (sorted) is the default. A substrate that finds a set-kind array out of order refuses the row with **`federation_set_semantics_unsorted`**, naming the member, and never re-sorts it (re-sorting would move signed bytes). **A set-kind array is sorted AND unique:** a duplicate element is refused under the same token. No reader counts multiplicity anywhere in the substrate, every other set this document encodes is already stated as deduplicated ([CC 3.4.7.1](part_3_the_namespace.md#3.4.7.1), [CC 3.3.7](part_3_the_namespace.md#3.3.7)), and a duplicate is otherwise a second byte string for one meaning. **An optional member is unset by absence, never by `null`.** An explicit JSON `null` on any optional envelope member is refused as malformed, as `federation_malformed_row` with reason `envelope_member_null`. That reason is one of the closed malformed-row reasons of [CC 2.6.1.7](#2.6.1.7), beside `envelope_member_missing` / `envelope_member_invalid`. A null and an absence would be two byte strings for one meaning, the duplicate rule again. The key plane's `revocation_envelope` of [CC 2.4.1.1](#2.4.1.1) is the one exception: it binds its absent optionals as explicit `null`. Where this document writes a default as `null` it means *absent*.
2. **Byte-field string encoding.** JSON has no byte type, so every byte/binary field is a string whose encoding MUST be pinned. **Hashes and raw key material — public keys, `destination_hash`, `root_hash`, digests and fingerprints — MUST be lowercase hex per [CC 2.6.3](#2.6.3)** (no `0x`, no separators, byte-length-exact; never base64 in canonical bytes). Fields explicitly documented as base64 (e.g., `hardware_attestation`, an opaque attestation blob) use base64 as their definition states — but the *default* for any key/hash/id byte field is CC 2.6.3 lowercase hex.
 - **`subject_key_ids[]` is the one two-form field, and [CC 2.3.2.1](#2.3.2.1) governs its second form.** An element naming a `federation_keys.key_id` — like `attesting_key_id` and `attested_key_id` — carries that key's `key_id` string **verbatim**: the [CC 2.6.8](#2.6.8) `<label>-<fingerprint>` form (lowercase `[a-z0-9-]`), or an older 64-hex id a directory still holds. A `key_id` is an identifier, not a byte field, so the hex rule above does not re-encode it. An element naming a canonical-hash subject is the **tagged** `canonical:{hashalg}:{hex}` string, which CC 2.3.2.1 REQUIRES and whose untagged bare-hex spelling CC 2.3.2.1 refuses at the gate. The CC 2.6.3 hex rule governs the `{hex}` segment of that string only; the `canonical:{hashalg}:` prefix is a tagged-union discriminator, outside CC 2.6.3's scope and **exempt from the no-separators rule**. The exemption is restated here on purpose, because these are signing bytes. An implementer who reads only this clause and strips the tag, or refuses the tagged form, produces a different canonical envelope and a **silently non-verifying signature**, not a visible admission error.
 - **The base64 variant is pinned: every field documented as base64 MUST use the RFC 4648 §4 STANDARD alphabet, WITH padding, no whitespace or embedded newlines**. The pin lives at the **protocol layer**: the crypto layer is encoding-agnostic and deals in raw bytes; the wire encoding is CEG's to pin. A variant mismatch (URL-safe alphabet, stripped padding) produces different signed bytes and a **silently non-verifying signature** — the same hazard class as the wrap-algorithm wire-string. The vector set MUST include a base64-variant case (encode→sign→verify round-trip across two independent encoders).
3. **Timestamp encoding.** Every datetime field (`signed_at`, `asserted_at`, `valid_until`, `delegation_valid_from`/`_until`, `valid_at`, …) is the **[CC 2.6.2](#2.6.2) canonical string** — UTC literal `Z` (never `+00:00`), millisecond precision (exactly three fractional digits), `YYYY-MM-DDTHH:MM:SS.sssZ`. A producer emitting `+00:00` or a different sub-second precision produces different bytes and a non-verifying signature.

With key order (JCS) + omit-vs-materialize + these three, **byte-identity across conformant implementations is closed by construction**. The cross-impl JCS vector set MUST cover all three (a set-vs-sequence array case, a hex-vs-base64 byte case, a timestamp case) alongside the per-Contribution vectors.

#### 2.6.1.2 `per-field` — Per-field encoding table (informational)

The omit-vs-materialize rule applies uniformly to every optional [CC 2.1](#2.1) field. Catalog:

| Field | Section | Default per CC 2.1 | Canonical when omitted | Canonical when explicit |
|---|---|---|---|---|
| `epistemic_mode` | CC 2.1 | `direct` | member absent | `"epistemic_mode":"direct"` (or other enum value) |
| `witness_relation` | CC 2.1 | `external` | member absent | `"witness_relation":"self"` (or other enum value) |
| `oversight_mode` | CC 2.1 | `null` (per-cell default applies) | member absent | `"oversight_mode":"HITL"` (or other enum value) |
| `occurrence_id` | CC 2.1 | `null` → `"occurrence-0"` at interpretation | member absent | `"occurrence_id":"occurrence-1"` |
| `occurrence_count` | CC 2.1 | `null` → `1` at interpretation | member absent | `"occurrence_count":3` |
| `occurrence_role` | CC 2.1 | `null` → `"primary"` at interpretation | member absent | `"occurrence_role":"shared"` |
| `stake` | CC 2.1 | `reputational` | member absent | `"stake":"capital"` (or other enum value) |
| `context` | CC 2.1 | absent | member absent | `"context":"..."` (free-form) |
| `evidence_refs` | CC 2.1 | absent | member absent | `"evidence_refs":["..."]` |
| `valid_until` | CC 2.1 | absent | member absent | `"valid_until":"2026-12-31T00:00:00.000Z"` |
| `row.subject_key_ids` | CC 2.3, CC 2.6.1.7 | `[]` (no subject authority) | always present in the mirror, `[]` when there is no subject; the `subject_key_ids` column beside the row is absent when empty | `"subject_key_ids":["..."]` |
| `scope` | CC 2.1, CC 3.3.1 | absent | member absent | `"scope":["retain","share"]` or `"scope":"retain:90d"` |
| `session_id` | CC 3.1.3.1 | n/a (REQUIRED on `session:*`) | member absent (not a claim) | `"session_id":"s1"` |
| `claimed_at` | CC 3.1.3.1 | n/a (REQUIRED on `session:*`) | member absent (not a claim) | `"claimed_at":"2026-08-30T12:00:00.000Z"` |
| `custody_state` | CC 3.1.3.3 | n/a (REQUIRED on a custody report) | member absent (not a custody report; on one, admission refuses) | `"custody_state":"none"` |
| `group_kind` | CC 3.1.3.2 | n/a (REQUIRED on a membership proposal) | member absent (not a proposal; on one, admission refuses) | `"group_kind":"family"` |
| `role` | CC 3.1.3.2 | `null` (no role offered) | member absent | `"role":"member"` |
| `expires_at` | CC 3.1.3.2 | n/a (REQUIRED on a membership proposal) | member absent (not a proposal; on one, admission refuses) | `"expires_at":"2026-10-07T00:00:00.000Z"` |
| `proposal_hash` | CC 3.1.3.2 | n/a (REQUIRED on a membership answer) | member absent (not an answer; on one, admission refuses) | `"proposal_hash":"<original_content_hash>"` |
| `attached_head_digest` | CC 3.2 T4a | n/a (REQUIRED on `trust:accepts:v1`) | member absent (not an acceptance edge; a NEW acceptance edge without it is refused; an edge admitted before the member was required stays valid, T4) | `"attached_head_digest":"<64-char-lowercase>"` |
| `subject_sha256_ed25519_raw` | CC 2.4.1.1 | absent (the subject is named some other way, or not at all) | member absent | `"subject_sha256_ed25519_raw":"<64 lowercase hex>"` |
| `attach_window_secs` | CC 3.2 T4a | absent = no window declared (attach by out-of-band anchor only) | member absent | `"attach_window_secs":604800` |
| `witness_cadence_secs` | CC 3.2 T6 | n/a (REQUIRED on a witnessed lineage's charter) | member absent (the lineage is unwitnessed for T6) | `"witness_cadence_secs":86400` |
| `additional_scrubs` | CC 2.4 | absent (single-signer row) | member absent | `"additional_scrubs":[{"scrub_key_id":"…","scrub_signature_classical":"…","scrub_signature_pqc":"…"}]` (beside the row) |
| `halt_fuse_secs` | CC 4.2.1.1 | **86400** — a constitutional constant, not a substrate default | member absent ≡ `86400` (a verifier reads the constant) | `"halt_fuse_secs":3600` (an explicit value overrides) |
| `recovery_commitments` | CC 4.2.6 | n/a (REQUIRED on the accord's charter) | member absent (no holder can self-rotate; recovery is a roster change) | `"recovery_commitments":{"<holder_key_id>":"<64 lowercase hex>"}` |
| `witness_quorum` | CC 3.2 T6 | absent ≡ `0`: witnessed mode off; no substrate default is substituted | member absent (witnessed mode off — the lineage is unwitnessed for T6) | `"witness_quorum":2` |
| `witnesses` | CC 3.2 T6 | n/a (REQUIRED on a witnessed lineage's charter) | member absent (the lineage is unwitnessed for T6) | `"witnesses":[<SignedKeyRecord>, ...]` |
| `family_id` | CC 3.3.4 | n/a (REQUIRED iff `cohort_scope == family`) | member absent (admission rejects if cohort_scope == family) | `"family_id":"..."` |
| `community_id` | CC 3.2 | n/a (REQUIRED iff `cohort_scope ∈ {community, affiliations}`) | member absent (admission rejects if `cohort_scope ∈ {community, affiliations}`) | `"community_id":"..."` |
| `delivery_mode` | CC 5.3.3 | `pull` | member absent | `"delivery_mode":"push"` |
| `history_on_join` | CC 5.3.3 | `from_join` | member absent | `"history_on_join":"full"` |

The conditional-required fields `family_id` and `community_id` are NOT optional-with-default ([CC 2.1.1](#2.1.1)), but they encode under the same JCS rule when present ([CC 2.3.1](#2.3.1)).

#### 2.6.1.3 `canonical` — Canonical encoding format (normative)

CEG envelope signing bytes are computed via **JCS — JSON Canonicalization Scheme, [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785)**. JCS pins, in summary:

- Object members sorted lexicographically by member name (UTF-16 code-unit order, RFC 8785, section 3.2.3)
- No insignificant whitespace
- UTF-8 byte encoding (RFC 8259, section 8.1)
- Strings escaped per RFC 8259 §7 with the JCS narrowing on `\uXXXX` form
- Numbers serialized per the ES6-derived rule (RFC 8785, section 3.2.2.3) — integers without trailing `.0`, no exponent unless the magnitude requires it

A CEG-Conforming Producer MUST produce signing bytes via JCS over the envelope object — `attestation_envelope`, whose member set and placement are pinned at [CC 2.6.1.7](#2.6.1.7). A CEG-Conforming Consumer (CCC) MUST recompute signing bytes via the same JCS rule for signature verification. A CEG-Conforming Substrate (CCS) MUST preserve the as-received envelope object bytes for relay (per the round-trip rule above) ([CC 2.6.1.1](#2.6.1.1)). It MAY store a parsed representation alongside, but the canonical-bytes contract is against the as-received **object** — its member set and its member values, which no party may alter. The contract is not against a parsed-and-re-serialized shape with defaults materialized or members dropped. Insignificant whitespace and member order are **not** part of that contract: JCS erases both, so normalizing them changes no signing byte.

**Redaction vs tampering — the signed-discriminator shape is excluded (normative dead end).** The excluded shape is a signed "I redacted this" marker distinguishing authorized redaction from tampering. It is excluded because **a signed redaction marker proves an authorized party changed the bytes — it does not prove that *only* the redacted parts changed**. A compromised or coerced authority key becomes a licence to rewrite arbitrary content while every reader reports the row as legitimately redacted: integrity replaced by authority, arriving quietly. Any future redaction scheme is bound by four constraints:

- **(a) it lives on the envelope plane**. The integrity gate is `original_content_hash` at ingest, receiver-side. `persist_row_hash` is never re-verified on read, so a storage-plane build is inert.
- **(b) it carries its own redactability declaration** in the signed object. Per-field commitments cannot derive "which fields are redactable" from the manifest, whose wire fields and storage containers are disjoint sets with no bridge. The scheme carries that declaration **unless the scheme is uniformly redactable by construction** (BBS+-style multi-message signatures, JMSW set schemes), in which case the signed object MUST instead commit to the member count and index ordering.
- **(c) it lives above whole-row hashing**, which forecloses partial redaction downstream.
- **(d) the third option stays open** — a redacted row MAY simply be a *different object carrying a different kind*, relocating the work entirely.

Note for any per-field commitment design: canonical member ordering is **one of two routes** to a derivable leaf sequence. The other is committing to the encoded disclosure bytes directly (the SD-JWT/mDoc salted-digest shape, which needs no canonicalization). Where the canonical route is taken, CC 2.6's canonicalization choice is already load-bearing for redactable signatures.

**Number totality (normative).** RFC 8785, section 3.2.2.3, fixes the number model as the IEEE-754 binary64 (ECMAScript `Number`) image. A CCP MUST coerce every numeric value to its finite IEEE-754 double image *before* computing JCS bytes. It MUST reject — with a hard error, never a fallback or best-effort hash — any number that has no finite double (overflow to ±Infinity, e.g. `1e1000` or a thousand-digit integer). An implementation built against an arbitrary-precision JSON parser otherwise admits a string-backed number that bypasses the double model. JCS then emits a non-canonical result and the content address silently diverges between peers. This is the same non-determinism-is-broken hazard class as the byte-field and timestamp rules of [CC 2.6.1.1.1](#2.6.1.1.1). With this rule a content address is always either the spec-canonical hash or an honest error, never a wrong-but-plausible one, in any parser feature configuration. The cross-impl JCS vector set MUST include a non-representable-number case (a value with no finite double, asserted to reject) under both default and arbitrary-precision parser builds.

**Canonical-bytes size bound (normative).** A CEG envelope's canonical (JCS) bytes MUST NOT exceed **1 MiB (1 048 576 bytes)**. The signed thing is the sized thing, so the bound is on the bytes the signature covers, never on a stored or transport-framed image of them. A CCP MUST NOT emit an envelope above the cap. A CCS MUST reject one at admission — at **every** write path, including capsule/FFI and tier-ingest, not only an HTTP body gate — with `ENVELOPE_TOO_LARGE` (HTTP 413, [CC 5.3.6.1](part_5_transport_substrate.md#5.3.6.1)). The value is the blob-payload threshold (inline at or below 1 MiB, a blob above), so the cap adds a rule, not a second regime.

*An above-cap payload.* Above the cap **the envelope carries the manifest, not the bytes**: the heavy payload moves to the blob plane as encrypted chunks, replicated per item to the holder count its owner chose ([CC 6.1.5](part_6_the_coherence_mathematics.md#6.1.5)). The envelope names it by content hash in `evidence_refs`. How that hash resolves is **scope-dependent**, and both routes exist. For Commons scopes it resolves through the holding-claim directory (`custody:ack:v1` `here` rows at federation scope, [CC 3.1.3.3](part_3_the_namespace.md#3.1.3.3)) + [CC 5.3.2](part_5_transport_substrate.md#5.3.2) `ContentFetch`. For a bounded cohort the same rows exist **inside the cohort only** ([CC 5.2](part_5_transport_substrate.md#5.2)). There the same `evidence_refs` content hash resolves over the in-cohort at-rest-encrypted delivery path to the cohort's admitted members. An above-cap self- or family-scoped envelope therefore has exactly one route, not zero. The attestation remains the CEG object; only its payload relocates — **no new envelope field and no new primitive; the [CC 1.7](part_1_foundation.md#1.7) 1+4 surface is untouched**.

*The cap as wire contract.* This is a different axis from the [CC 5.4.3](part_5_transport_substrate.md#5.4.3) constant frame size on a shaped link. That is a traffic-analysis uniformity rule which *fragments* an oversize payload rather than refusing it, so it bounds no admission decision. Absent the cap here, a multi-megabyte attestation is simply hundreds more fragments on the anti-entropy walk. The cap is wire-contract precisely because peers have to agree on it: unratified, one node's legitimate envelope is another's rejection. The freeze-gate vector set MUST include an at-cap envelope (admits) and a cap-plus-one-byte envelope (rejects with the token above).

**What is measured, and when (normative).** JCS bytes are not the received octets — the same envelope can arrive pretty-printed, with expanded `\uXXXX` escapes, or with exponent-form numbers. So the cap alone does not tell an implementer when to stop reading, and a rule measured on canonical bytes is not to be read as a mandate to buffer an unbounded input in order to find them. Two bounds, distinct roles:

1. **The contract bound (interop-visible).** `|JCS(envelope)| ≤ 1 MiB`. This is the only bound peers have to agree on; it is measured on the bytes the signature covers and is therefore decided **after** parse. A CCP MUST NOT emit above it; a CCS MUST reject above it with `ENVELOPE_TOO_LARGE`.
2. **The intake bound (local, mandatory, not interop-visible).** Because (1) cannot be decided without parsing, every write path MUST **also** enforce a finite ceiling on the octets it will buffer from an untrusted source. The path MUST refuse at that ceiling **without completing the parse** — same `ENVELOPE_TOO_LARGE` / 413. The ceiling is a deployment parameter, not a wire constant. It MUST NOT be set below 1 MiB (a lower ceiling could refuse a conformant envelope). A deployment SHOULD publish the ceiling. This is what makes "at every write path, not only an HTTP body gate" implementable: each path bounds its own intake instead of delegating the bound to a body gate it may not have.

**The two coincide on a conformant relay path.** A relay that re-emits has already recomputed JCS to verify. [CC 2.6.1.1](#2.6.1.1) requires it to re-canonicalize member order while holding member presence/absence fixed. So what it forwards is the canonical form, and there the received octets **are** the canonical octets. The gap exists only where a non-canonical serialization first enters. Consequently **the interoperable serialization is the canonical one**: a party that transmits an inflated serialization of a semantically-conformant envelope MAY have it refused by a receiver's intake ceiling. That refusal is conformant receiver behavior, not a receiver defect.

#### 2.6.1.4 `worked` — Worked attack the rule closes

Without the rule (implicit / unspecified) failure mode:

> Alice's CEG-Conforming Producer signs an envelope omitting `epistemic_mode`. Bob's CEG-Conforming Relay receives, parses, materializes the default `"direct"`, re-serializes via JCS, and forwards to Carol. Carol receives the relay-modified envelope with the new bytes, computes JCS, verifies signature → **FAILS** because Alice signed over bytes without the `epistemic_mode` member. Carol cannot distinguish "Bob is a malicious relay corrupting the bytes" from "Bob is honestly applying defaults to be helpful." Carol rejects. The attestation is lost in transit despite no party acting in bad faith.

With the rule (explicit, normative):

> Bob's relay MUST preserve member presence/absence exactly ([CC 2.6.1.1](#2.6.1.1)). Bob forwards the as-received bytes. Carol's verify succeeds. The semantic interpretation step at Carol (applying default `"direct"` to the absent member) happens AFTER signature verification.

#### 2.6.1.5 `verification` — Verification flow (informational)

```
On signature verify:
    1. Receive envelope from wire as object O (preserved as-received)
       and signature S
    2. Compute canonical bytes B = JCS(O)
    3. Verify S over B via the hybrid Ed25519 + ML-DSA-65 path per CC 5.3.2.4.3.1
    4. If signature valid:
        a. Compute effective semantics by applying the CC 2.6.1.1 defaults to absent
           optional fields (interpretation-time only)
        b. Apply consumer policy (CC 4.4) over the resulting semantic shape
    5. If forwarding/storing:
        a. Store/forward object O AS RECEIVED — do not strip or materialize
           defaults (CC 2.6.1.3 governs the bytes; member order is not in
           the contract; forward the octets as received)
        b. Forward original signature S unchanged
```

#### 2.6.1.6 `section` — Scope of the canonicalization rule

Scope pointer: the JCS canonicalization rules above (JCS-as-encoding, omit-vs-materialize + relay-preservation, per-field catalog, worked attack).

What this rule does NOT do:
- Introduce a new encoding format — JCS is the only encoding ([CC 2.6.1.3](#2.6.1.3))
- Change any semantic interpretation — defaults still apply at interpretation time per [CC 2.1](#2.1)
- Modify the datetime / hex / time / H3 sub-rules — those are domain-specific and compose under JCS
- Wire-break prior emissions — emissions that omitted optional fields remain valid; emissions that explicitly emitted defaults likewise remain valid; what the rule normatively prohibits is RELAY-TIME mutation of presence/absence ([CC 2.6.1.1](#2.6.1.1))

#### 2.6.1.7 `signed-object` — The signed object — member set, placement and types (normative)

*This table, [`manifests/signed_object.cddl`](../manifests/signed_object.cddl) and [`manifests/signed_object.json`](../manifests/signed_object.json) are rendered from one data file, and [`manifests/signed_object_vectors.json`](../manifests/signed_object_vectors.json) holds the byte vectors; the data is the source and the three never disagree.*

**The object (normative).** The signed object of an attestation row is `attestation_envelope`: one JSON object. The signing input is JCS(`attestation_envelope`) ([CC 2.6.1.3](#2.6.1.3)) and nothing else — the row's own signature members, every cosignature and every column beside the row are outside the bytes, so a cosignature is never inside the bytes it signs. Seven of those columns are mirrored *inside* the bytes under the member `row`, a closed set; a row with no mirror is refused `envelope_member_missing`, and a column that disagrees with its mirror is refused `typed_diverges_from_envelope`. The claim's instants ride inside the bytes as `asserted_at` and `expires_at`, and the columns are read back out of them. The row's own signature is the attester's: the classical half verifies against `attesting_key_id`'s pinned Ed25519 key over the signing input, the post-quantum half against its ML-DSA-65 key over the signing input followed by the raw Ed25519 signature ([hybrid-sig], [CC 2.6.5](#2.6.5)); at the federation tier both halves verify or the row is refused. `original_content_hash` is the lowercase hex SHA-256 of the signing input and is recomputed at ingest. A second signer over the same bytes is an entry of `additional_scrubs[]`, beside the row, verified against its own key. A JCS image above 1 MiB is refused `ENVELOPE_TOO_LARGE` ([CC 2.6.1.3](#2.6.1.3)).

**Refusals at this door (normative).** A shape refusal of the signed object is the token `federation_malformed_row` with one reason from this closed set: `envelope_member_missing` (the mirror or another required member is absent), `envelope_member_invalid` (a member is ill-typed or an instant is not in the [CC 2.6.2](#2.6.2) form), `envelope_member_null` (an optional member is `null`), `typed_diverges_from_envelope` (a column beside the row differs from its mirror), `envelope_row_member_unknown` (the `row` mirror carries a member outside its closed seven), `content_hash_mismatch` (`original_content_hash` is not the SHA-256 of the signing input) and `subject_key_id_malformed` (an element of `subject_key_ids` is neither a `key_id` nor the tagged canonical form of [CC 2.3.2.1](#2.3.2.1)). A `withdraws` that meets no rule of [CC 2.4.1.1](#2.4.1.1) is refused `federation_withdraws_not_admitted`. A set out of order or with a duplicate is `federation_set_semantics_unsorted`, a type outside the five is `attestation_type_unregistered`, a failed signature half is `SIGNATURE_VERIFICATION_FAILED`, and an envelope over the cap is `ENVELOPE_TOO_LARGE`.

**Placement vocabulary.** `signed:row` — inside `attestation_envelope.row`. `signed:envelope` — inside `attestation_envelope`, typed by persist. `signed:envelope-extra` — inside `attestation_envelope`, typed by this table and defined in [CC 2.1](#2.1), carried untyped by persist and validated at the family's gate. `beside` — outside the bytes, replicated, bound to the bytes by a gate. `beside:signature` — the row's own signature members. `beside:cosign` — an `additional_scrubs[]` entry. `local` — persist-internal, not a wire contract. `not-on-wire` — named by this text, not carried on the wire. An array's kind is `set` (sorted by JCS string before signing) or `sequence` (as authored), per [CC 2.6.1.1.1](#2.6.1.1.1).

**Inside the signed bytes — the mirror (closed, exactly seven)**

| Member | Placement | Type | Array | Presence | Default | CC | Note |
|---|---|---|---|---|---|---|---|
| `row.attestation_id` | signed:row | `uuid` | — | REQUIRED | — | [2.6.1.7](#2.6.1.7) | The row's identity, minted by the stamper before the bytes exist (a UUID; this edition pins no version); the composers' references_attestation_id points at it. |
| `row.attesting_key_id` | signed:row | `key-id` | — | REQUIRED | — | [2.1](#2.1) [2.6.8](#2.6.8) | The signer. The row's own signature verifies against this key's pinned Ed25519 and ML-DSA-65 public keys; there is no separate signer slot inside the bytes. |
| `row.attestation_type` | signed:row | `row-type` | — | REQUIRED | — | [2.4](#2.4) | One of the five, byte-compared; anything else is refused attestation_type_unregistered. |
| `row.attested_key_id` | signed:row | `key-id` | — | REQUIRED | the attester | [2.1](#2.1) | Defaults to the attester at the mint (a self-claim). |
| `row.subject_key_ids` | signed:row | `[* subject-id]` | set | REQUIRED (may be empty) | [] | [2.3](#2.3) [2.3.2.1](#2.3.2.1) [2.6.1.1.1](#2.6.1.1.1) | Always present in the mirror, an empty array when there is no subject; the column beside the row is absent when empty. An element is a key_id verbatim or the tagged canonical:{alg}:{hex} form; uppercase and whitespace are refused at emit. A set (2.6.1.1.1): sorted and unique, an unsorted or duplicated set refused federation_set_semantics_unsorted. |
| `row.cohort_scope` | signed:row | `cohort-scope` | — | REQUIRED | — | [2.3.3](#2.3.3) [5.2](part_5_transport_substrate.md#5.2) | Closed set of seven. No wire default: the member is required. The authoring default is the smallest scope (CC 1.13.3.4). The one mirror member a placement-touching re-sign may narrow; it may never be re-authored. |
| `row.weight` | signed:row | `float` | — | OPTIONAL | absent | [2.1](#2.1) | Absent in the mirror iff the column is NULL. A non-finite value is refused at the stamp rather than serialised as null. |

**Inside the signed bytes — members persist types**

| Member | Placement | Type | Array | Presence | Default | CC | Note |
|---|---|---|---|---|---|---|---|
| `row` | signed:envelope | `row-mirror` | — | REQUIRED | — | [2.6.1.7](#2.6.1.7) | The signed twin of the seven typed columns beside the row. The member set is closed (an eighth member is refused); a row with no mirror is refused envelope_member_missing, a mirror that disagrees with a column is refused typed_diverges_from_envelope. |
| `asserted_at` | signed:envelope | `rfc3339-ms` | — | REQUIRED | stamped at the mint | [2.6.2](#2.6.2) [2.6.7](#2.6.7) | The claim's instant, truncated to the millisecond and rendered YYYY-MM-DDTHH:MM:SS.sssZ before signing; the column beside the row is read back out of this member and never from a second clock. Judged against the receiver's clock only where 2.6.7 says (the future bound; W on chain-judged rows). |
| `expires_at` | signed:envelope | `rfc3339-ms` | — | OPTIONAL | absent (no expiry) | [2.1](#2.1) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The column's signed twin; present iff the column is set, any other pairing refused. REQUIRED on membership:proposal and lineage_witness:proposal (CC 3.1.3.2, CC 3.1.3), and on census:share:{class}:v1 and census:member:share:v1, where it is the period's end (census_return_expired after it). |
| `dimension` | signed:envelope | `tstr` | — | REQUIRED on every row type | — | [2.1](#2.1) [2.4](#2.4) [3.1](part_3_the_namespace.md#3.1) [3.1.7](part_3_the_namespace.md#3.1.7) | The namespace prefix plus leaf, resolved through manifests/namespace_registry.json on all five row types (the job label on a delegates_to as much as the family on a scores). |
| `references_attestation_id` | signed:envelope | `uuid` | — | REQUIRED on supersedes, withdraws, recants, otherwise OPTIONAL | — | [2.4.1](#2.4.1) [3.1.2.1](part_3_the_namespace.md#3.1.2.1) [4.5.1.1](part_4_composition_governance.md#4.5.1.1) | On the three composers it is the composer target: the prior row's attestation_id, read only with the row type as discriminator (three readings, CC 4.5.1.1). On any other type it cites a row and carries no composer meaning (CC 3.1.2.1). A fourth composer reading is a separate member, which is why consent_supersedes exists. |
| `scope` | signed:envelope | `tstr / [* tstr]` | set | REQUIRED on consent:state:granted and on delegates_to | — | [2.1](#2.1) [3.3.1](part_3_the_namespace.md#3.3.1) [4.4.3.4.3](part_4_composition_governance.md#4.4.3.4.3) | The form an emitter writes is the array: an emitter writes ["retain"], and a bare token is admitted as the one-element array it denotes; admission normalises nothing in the signed bytes. |
| `pre_rotation_commitment` | signed:envelope | `hex64` | — | OPTIONAL (charter) | absent | [3.2](part_3_the_namespace.md#3.2) | Pre-rotation commitment on a charter. |
| `recovers` | signed:envelope | `key-id` | — | REQUIRED on a charter recovery | absent | [3.2](part_3_the_namespace.md#3.2) | The predecessor root being rotated. |
| `successor_keys` | signed:envelope | `[* key-id]` | set | REQUIRED on a charter recovery | absent | [3.2](part_3_the_namespace.md#3.2) | The pre-committed successor key set. |
| `withdrawal_reason` | signed:envelope | `tstr` | — | OPTIONAL on withdraws | absent | [2.4.1](#2.4.1) | The producer's stated reason. |
| `consent_supersedes` | signed:envelope | `uuid` | — | OPTIONAL on consent:state:* | absent | [3.3.1](part_3_the_namespace.md#3.3.1) [4.5.1.1](part_4_composition_governance.md#4.5.1.1) | The prior consent statement this one replaces. Separate from references_attestation_id by the CC 4.5.1.1 op split. |
| `delivery_mode` | signed:envelope | `"pull" / "push"` | — | OPTIONAL | pull | [2.1](#2.1) [2.3.3](#2.3.3) | Recipient-receive axis; the processor is edge's. |
| `deletion_window` | signed:envelope | `tstr` | — | OPTIONAL | absent | [3.3.1](part_3_the_namespace.md#3.3.1) | Deadline by which a consented payload must be deleted. |
| `media` | signed:envelope | `object` | — | OPTIONAL | absent | [3.3.13](part_3_the_namespace.md#3.3.13) | The multimedia Source struct, kept as JSON and validated at the door. |
| `widened_at` | signed:envelope | `rfc3339-ms` | — | REQUIRED on a widening supersedes, absent otherwise | absent | [4.4.3.3.1](part_4_composition_governance.md#4.4.3.3.1) [2.6.7](#2.6.7) | When the widening itself was placed; asserted_at on a widening is the claim's own instant carried verbatim. |
| `accord_root` | signed:envelope | `key-id` | — | REQUIRED on accord:* rows | absent | [4.2](part_4_composition_governance.md#4.2) | Which accord an accord:* row belongs to; a foreign row carrying junk fails closed at the fold. |
| `attach_window_secs` | signed:envelope | `uint` | — | OPTIONAL on trust:charter:v1 | absent (anchor only) | [2.1](#2.1) [3.2](part_3_the_namespace.md#3.2) | T4a attach window. |
| `witness_cadence_secs` | signed:envelope | `uint` | — | REQUIRED on a witnessed lineage's charter | absent | [2.1](#2.1) [3.2](part_3_the_namespace.md#3.2) | T6 cadence. |
| `witness_quorum` | signed:envelope | `uint` | — | REQUIRED on a witnessed lineage's charter | absent (= 0, witnessed mode off) | [2.1](#2.1) [3.2](part_3_the_namespace.md#3.2) | T6 quorum; ⌊\|witnesses\|/2⌋ + 1 and at least 2, or 0. |
| `attached_head_digest` | signed:envelope | `hex64` | — | REQUIRED on trust:accepts:v1 | — | [2.1](#2.1) [3.2](part_3_the_namespace.md#3.2) | T4a: the lineage head the acceptance attaches on. |
| `recovery_commitments` | signed:envelope | `{* key-id => hex64}` | — | REQUIRED on the accord's charter | — | [2.1](#2.1) [4.2.6](part_4_composition_governance.md#4.2.6) | Holder key id to commitment; object keys sort under JCS like any member. |
| `for_key_id` | signed:envelope | `key-id` | — | REQUIRED on census:share:{class}:v1, census:member:share:v1 | absent | [3.1.3](part_3_the_namespace.md#3.1.3) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | The addressed recipient. The row is held by the author's node and this key's node and by no other; the serve gate sends it to this key only, no widening applies, and any other node refuses it federation_addressed_not_recipient. Also carried on consent:state rows. |
| `period` | signed:envelope | `uint` | — | REQUIRED on census:share:{class}:v1, census:member:share:v1, census:partial:{class}:v1, census:member:partial:v1, census:composite:{class}:v1, ballot:tally:{poll_id}:v1, census:expected_active:v1 | absent | [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | The census period index on the global cadence (CC 5.4.5). |
| `return_token` | signed:envelope | `hex64` | — | REQUIRED on census:share:{class}:v1, census:member:share:v1 | absent | [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | H(node_secret ‖ period): the per-period token a contributor later checks for inclusion; never a node id. |
| `share_index` | signed:envelope | `uint` | — | REQUIRED on census:share:{class}:v1, census:member:share:v1, census:partial:{class}:v1, census:member:partial:v1 | absent | [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | 0 or 1: which of the two additive shares, and which aggregator's partial. Any other value is census_share_index_invalid. |
| `share_count` | signed:envelope | `uint` | — | REQUIRED on census:partial:{class}:v1, census:member:partial:v1 | absent | [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | Shares the aggregator summed into this partial; both partials of a period must agree. |
| `source_count` | signed:envelope | `uint` | — | REQUIRED on census:composite:{class}:v1, ballot:tally:{poll_id}:v1 | absent | [6.1.2.1](part_6_the_coherence_mathematics.md#6.1.2.1) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | Distinct owners behind the composite. On census:composite:{class}:v1 a count below 10 is refused census_composite_below_k. |
| `n_eff` | signed:envelope | `uint` | — | REQUIRED on census:composite:{class}:v1, ballot:tally:{poll_id}:v1 | absent | [6.1.2.1.2](part_6_the_coherence_mathematics.md#6.1.2.1.2) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | The effective source count; equals source_count by construction for one-hot returns; aggregation_meta_dominated below half of source_count. |
| `max_source_multiplicity` | signed:envelope | `uint` | — | REQUIRED on census:composite:{class}:v1, ballot:tally:{poll_id}:v1 | absent | [6.1.2.1](part_6_the_coherence_mathematics.md#6.1.2.1) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | The largest multiplicity cluster; aggregation_meta_multiplicity above the floor; on a census composite any value but 1 is refused (CC 6.1.9). |
| `mass_commitment_hex` | signed:envelope | `hex64` | — | REQUIRED on census:composite:{class}:v1, ballot:tally:{poll_id}:v1 | absent | [6.1.2.1](part_6_the_coherence_mathematics.md#6.1.2.1) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | Merkle root over the per-member masses. |
| `member_commitment_hex` | signed:envelope | `hex64` | — | REQUIRED on census:partial:{class}:v1, census:member:partial:v1, census:composite:{class}:v1, ballot:tally:{poll_id}:v1, census:expected_active:v1 | absent | [6.1.2.1.1](part_6_the_coherence_mathematics.md#6.1.2.1.1) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | Merkle root over the accepted tokens; a contributor checks its token's path against it; both partials of a period must carry the same root. |
| `mass_total` | signed:envelope | `tstr` | — | REQUIRED on census:partial:{class}:v1, census:member:partial:v1, census:composite:{class}:v1, ballot:tally:{poll_id}:v1 | absent | [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | The decimal string of a field element: the sum of the cells. On a composite it equals source_count and the sum of the two partials' mass_total, else census_composite_mass_total_mismatch / census_composite_partials_mismatch. |
| `aggregation_algorithm_id` | signed:envelope | `tstr` | — | REQUIRED on census:partial:{class}:v1, census:member:partial:v1, census:composite:{class}:v1, ballot:tally:{poll_id}:v1 | absent | [6.1.2.1](part_6_the_coherence_mathematics.md#6.1.2.1) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | Names the field prime, the one-hot bucket layout and the proof system the shares were made under. |
| `noise_floor_descriptor` | signed:envelope | `tstr` | — | OPTIONAL on census:composite:{class}:v1, ballot:tally:{poll_id}:v1 | absent | [6.1.2.1](part_6_the_coherence_mathematics.md#6.1.2.1) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | What survives below the floor, when a cell is withheld. |
| `version` | signed:envelope | `uint` | — | REQUIRED on census:composite:{class}:v1, ballot:tally:{poll_id}:v1 | absent | [6.1.2.1](part_6_the_coherence_mathematics.md#6.1.2.1) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | 3: the composite carries the CC 6.1.2.1 verify inputs as signed members; a lower value is refused as the tier object's would be. |
| `partial_a` | signed:envelope | `uuid` | — | REQUIRED on census:composite:{class}:v1, ballot:tally:{poll_id}:v1 | absent | [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | The attestation_id of the share-index-0 partial this composite sums. references_attestation_id stays unset on a composite. |
| `partial_b` | signed:envelope | `uuid` | — | REQUIRED on census:composite:{class}:v1, ballot:tally:{poll_id}:v1 | absent | [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | The attestation_id of the share-index-1 partial. |
| `window_periods` | signed:envelope | `uint` | — | REQUIRED on census:expected_active:v1 | absent | [4.5.13](part_4_composition_governance.md#4.5.13) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | 4: a member is expected-active when active in at least one of the last four periods. |
| `active_count` | signed:envelope | `uint` | — | REQUIRED on census:expected_active:v1 | absent | [4.5.13](part_4_composition_governance.md#4.5.13) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | Owners active within the window, after the ratchet; every member recomputes it, else census_expected_active_mismatch. |
| `floor_applied` | signed:envelope | `bool` | — | REQUIRED on census:expected_active:v1 | absent | [4.5.13](part_4_composition_governance.md#4.5.13) [6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | Whether the ratchet's floor, not the raw count, set active_count this period. |

**Inside the signed bytes — members this text types and persist carries untyped**

| Member | Placement | Type | Array | Presence | Default | CC | Note |
|---|---|---|---|---|---|---|---|
| `score` | signed:envelope-extra | `float` | — | REQUIRED on scores | — | [2.1](#2.1) [3.1.7](part_3_the_namespace.md#3.1.7) | In [-1, 1]; the family's polarity class is an admission rule (CLM-polarity-admission). |
| `confidence` | signed:envelope-extra | `float` | — | REQUIRED on scores | — | [2.1](#2.1) | In [0, 1]. |
| `context` | signed:envelope-extra | `tstr` | — | OPTIONAL | absent | [2.1](#2.1) | Free form; not parsed by the substrate. |
| `evidence_refs` | signed:envelope-extra | `[* tstr]` | sequence | OPTIONAL (some families require it) | absent | [2.1](#2.1) [2.6.1.1.1](#2.6.1.1.1) [2.6.1.3](#2.6.1.3) | Producer-asserted order, preserved. Above the 1 MiB cap the payload moves to the blob plane and is named here by content hash. |
| `valid_until` | signed:envelope-extra | `rfc3339-ms` | — | REQUIRED on session:*, otherwise OPTIONAL | absent | [2.1](#2.1) [2.6.2](#2.6.2) [3.1.3.1](part_3_the_namespace.md#3.1.3.1) | Consumer-policy staleness, independent of expires_at. On session:* it is the claim's signed horizon (CC 3.1.3.1). |
| `epistemic_mode` | signed:envelope-extra | `"direct" / "crypto" / "hearsay" / "derivative" / "appeal"` | — | OPTIONAL | direct | [2.1](#2.1) [2.5](#2.5) [2.6.1.2](#2.6.1.2) | Interpretation-time default; an explicit default value is signed as written (2.6.1.1). |
| `witness_relation` | signed:envelope-extra | `"self" / "external" / "derived"` | — | OPTIONAL | external | [2.1](#2.1) [2.6.1.2](#2.6.1.2) |  |
| `oversight_mode` | signed:envelope-extra | `"HITL" / "HOTL" / "HOOTL"` | — | OPTIONAL | absent (per-cell default) | [2.1](#2.1) [2.6.1.2](#2.6.1.2) | CC 2.1 writes the default as null, which means absent; an explicit JSON null on any optional member is refused federation_malformed_row / envelope_member_null (CC 2.6.1.1.1). |
| `occurrence_id` | signed:envelope-extra | `tstr` | — | OPTIONAL | absent (read as occurrence-0) | [2.1](#2.1) [2.6.1.2](#2.6.1.2) | Self-asserted (CC 8.3.1). |
| `occurrence_count` | signed:envelope-extra | `uint` | — | OPTIONAL | absent (read as 1) | [2.1](#2.1) [2.6.1.2](#2.6.1.2) | At least 1. |
| `occurrence_role` | signed:envelope-extra | `"primary" / "shared" / "replica"` | — | OPTIONAL | absent (read as primary) | [2.1](#2.1) [2.6.1.2](#2.6.1.2) |  |
| `stake` | signed:envelope-extra | `"free" / "reputational" / "capital" / "cryptoeconomic"` | — | OPTIONAL | reputational | [2.1](#2.1) [2.5](#2.5) |  |
| `community_id` | signed:envelope-extra | `key-id` | — | REQUIRED iff cohort_scope is community or affiliations | — | [2.1](#2.1) [2.3.3](#2.3.3) [4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8) | The community whose roster gates visibility; refused when missing at those scopes. |
| `family_id` | signed:envelope-extra | `key-id` | — | REQUIRED iff cohort_scope is family | — | [2.1](#2.1) [2.3.3](#2.3.3) [3.3.4](part_3_the_namespace.md#3.3.4) |  |
| `session_id` | signed:envelope-extra | `tstr` | — | REQUIRED on session:* | — | [2.1](#2.1) [3.1.3.1](part_3_the_namespace.md#3.1.3.1) | Verbatim, case-preserved. |
| `claimed_at` | signed:envelope-extra | `rfc3339-ms` | — | REQUIRED on session:* | — | [2.1](#2.1) [3.1.3.1](part_3_the_namespace.md#3.1.3.1) |  |
| `custody_state` | signed:envelope-extra | `"here" / "none"` | — | REQUIRED on custody:ack | — | [2.1](#2.1) [3.1.3.3](part_3_the_namespace.md#3.1.3.3) | Refused custody_ack_malformed otherwise. |
| `group_kind` | signed:envelope-extra | `"family" / "community"` | — | REQUIRED on membership:proposal | — | [2.1](#2.1) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) |  |
| `role` | signed:envelope-extra | `tstr` | — | OPTIONAL on membership:proposal, restated on membership:acceptance | absent | [2.1](#2.1) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) |  |
| `proposal_hash` | signed:envelope-extra | `hex64` | — | REQUIRED on membership:acceptance and membership:decline | — | [2.1](#2.1) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The answered proposal's original_content_hash. |
| `subject_sha256_ed25519_raw` | signed:envelope-extra | `hex64` | — | OPTIONAL on moderation:* | absent | [2.4.1.1](#2.4.1.1) | Refused moderation_subject_digest_malformed when malformed. |
| `halt_fuse_secs` | signed:envelope-extra | `uint` | — | OPTIONAL on the accord's charter | 86400 (a constant of this document) | [2.1](#2.1) [4.2.1.1](part_4_composition_governance.md#4.2.1.1) | The halt latch reads the constant when the member is absent. |
| `witnesses` | signed:envelope-extra | `[* key-record]` | set | REQUIRED on a witnessed lineage's charter | — | [2.1](#2.1) [3.2](part_3_the_namespace.md#3.2) | A set, sorted by each element's JCS string (the 2.6.1.1.1 default made explicit). |
| `history_on_join` | signed:envelope-extra | `"full" / "from_join"` | — | OPTIONAL | from_join | [2.1](#2.1) [4.4.3.4.1](part_4_composition_governance.md#4.4.3.4.1) [5.1](part_5_transport_substrate.md#5.1) |  |
| `supersession_reason` | signed:envelope-extra | `tstr` | — | OPTIONAL on supersedes | absent | [2.4.1](#2.4.1) |  |
| `differs_in` | signed:envelope-extra | `[* tstr]` | set | OPTIONAL on supersedes; a widening lists cohort_scope | absent | [2.4.1](#2.4.1) [4.4.3.3.1](part_4_composition_governance.md#4.4.3.3.1) | Member names that differ from the prior. Array kind not declared in 2.4.1, so the 2.6.1.1.1 default (set, sorted) applies. |
| `recantation_reason` | signed:envelope-extra | `tstr` | — | OPTIONAL on recants | absent | [2.4.1](#2.4.1) |  |
| `what_was_false` | signed:envelope-extra | `tstr` | — | OPTIONAL on recants | absent | [2.4.1](#2.4.1) |  |
| `delegation_purpose` | signed:envelope-extra | `tstr` | — | OPTIONAL on delegates_to | absent | [2.4.1](#2.4.1) [2.4.1.2](#2.4.1.2) | owner_binding is the one single-valued purpose. |
| `delegation_valid_from` | signed:envelope-extra | `rfc3339-ms` | — | OPTIONAL on delegates_to | the edge's asserted_at | [2.4.1](#2.4.1) |  |
| `delegation_valid_until` | signed:envelope-extra | `rfc3339-ms` | — | REQUIRED on a termed delegates_to (CC 2.4.1), otherwise OPTIONAL | absent (open-ended) | [2.4.1](#2.4.1) [4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8) | At most 365 days after delegation_valid_from; refused delegation_term_required. |
| `trust_classes` | signed:envelope-extra | `[* tstr]` | set | OPTIONAL on a delegates_to bearing trust:accepts:v1 | absent (every class the authority's charter declares) | [4.4.3.8](part_4_composition_governance.md#4.4.3.8) | The licence classes the reader trusts this authority for; present non-empty; [] refused trust_accepts_classes_malformed. |
| `trust_depth` | signed:envelope-extra | `uint` | — | OPTIONAL on a delegates_to bearing trust:accepts:v1 | absent (0) | [4.4.3.8](part_4_composition_governance.md#4.4.3.8) [4.1.1](part_4_composition_governance.md#4.1.1) | Further hops honoured past this authority, 0..5; out of range refused trust_accepts_depth_out_of_range. |
| `*` | signed:envelope-extra | `any` | — | OPTIONAL | — | [2.1.1](#2.1.1) [3.3](part_3_the_namespace.md#3.3) | Every other member, including subject_kind and the per-family payloads of CC 3.3, rides the envelope untyped by the substrate and is preserved on relay (2.1.1); families validate their own at their gates. This table does not enumerate them. |
| `consent_basis` | signed:envelope-extra | `[* consent-basis]` | sequence | OPTIONAL (capacity:*, observation:access_assumption:v1) | absent | [2.1](#2.1) [3.3.1](part_3_the_namespace.md#3.3.1) | The grants a witness relied on. |
| `n_eff_pr` | signed:envelope-extra | `number` | — | OPTIONAL (carried on capacity:*; validated at the capacity:* gate) | absent | [2.1](#2.1) | Participation-ratio effective sample size; gated. |
| `n_eff_h` | signed:envelope-extra | `number` | — | OPTIONAL (carried on capacity:*; validated at the capacity:* gate) | absent | [2.1](#2.1) | Entropy-perplexity effective sample size; carried for audit. |
| `sample_size` | signed:envelope-extra | `uint` | — | OPTIONAL (carried on capacity:*; validated at the capacity:* gate) | absent | [2.1](#2.1) | Rows in the scoring matrix. |
| `feature_dim` | signed:envelope-extra | `uint` | — | OPTIONAL (carried on capacity:*; validated at the capacity:* gate) | absent | [2.1](#2.1) | Features per row. |
| `sample_size_gate` | signed:envelope-extra | `uint` | — | OPTIONAL (carried on capacity:*; validated at the capacity:* gate) | absent | [2.1](#2.1) | Configured minimum sample size. |
| `target_n_eff` | signed:envelope-extra | `number` | — | OPTIONAL (carried on capacity:*; validated at the capacity:* gate) | absent | [2.1](#2.1) | Configured target effective sample size. |
| `min_feature_dim` | signed:envelope-extra | `uint` | — | OPTIONAL (carried on capacity:*; validated at the capacity:* gate) | absent | [2.1](#2.1) | Configured minimum feature dimension. |
| `n_eff_floor` | signed:envelope-extra | `number` | — | OPTIONAL (carried on capacity:*; validated at the capacity:* gate) | absent | [2.1](#2.1) | Configured effective-sample-size floor. |
| `window` | signed:envelope-extra | `uint` | — | OPTIONAL (capacity:*, observation:access_assumption:v1) | absent | [2.1](#2.1) | The scoring or observation window, in rows. |
| `trace_level` | signed:envelope-extra | `"generic" / "detailed" / "full_traces"` | — | REQUIRED on observation:access_assumption:v1 | absent | [2.1](#2.1) [3.1.9.4](part_3_the_namespace.md#3.1.9.4) | The trace level the observed agent's install emitted at. |
| `occurrence_key_ids` | signed:envelope-extra | `[* key-id]` | set | REQUIRED on observation:access_assumption:v1 | absent | [2.1](#2.1) [3.1.9.4](part_3_the_namespace.md#3.1.9.4) | The occurrences whose rows the witness read. |
| `window_from` | signed:envelope-extra | `rfc3339-ms` | — | REQUIRED on observation:access_assumption:v1 | absent | [2.1](#2.1) [2.6.7](#2.6.7) [3.1.9.4](part_3_the_namespace.md#3.1.9.4) | Start of the observation window. |
| `window_to` | signed:envelope-extra | `rfc3339-ms` | — | REQUIRED on observation:access_assumption:v1 | absent | [2.1](#2.1) [2.6.7](#2.6.7) [3.1.9.4](part_3_the_namespace.md#3.1.9.4) | End of the observation window. |
| `channel_classes` | signed:envelope-extra | `[* tstr]` | set | REQUIRED on observation:access_assumption:v1 | absent | [2.1](#2.1) [3.1.9.4](part_3_the_namespace.md#3.1.9.4) | Channel classes the witness saw the subject through, as the emitter names them. |
| `amendment_digest` | signed:envelope-extra | `hex64` | — | REQUIRED on identity_amendment:v1 | absent | [2.1](#2.1) [3.1.5](part_3_the_namespace.md#3.1.5) | SHA-256 of the applied identity amendment. |
| `authorized_by` | signed:envelope-extra | `uuid` | — | REQUIRED on identity_amendment:v1 | absent | [2.1](#2.1) [3.1.5](part_3_the_namespace.md#3.1.5) [4.3](part_4_composition_governance.md#4.3) | The deferral:response:approved:v1 row that authorised it; admission checks it. |

**Beside the row — outside the bytes, bound to them**

| Member | Placement | Type | Array | Presence | Default | CC | Note |
|---|---|---|---|---|---|---|---|
| `attestation_id` | beside | `uuid` | — | REQUIRED | — | [2.6.1.7](#2.6.1.7) | Equals row.attestation_id or the row is refused. |
| `attesting_key_id` | beside | `key-id` | — | REQUIRED | — | [2.1](#2.1) | Equals row.attesting_key_id. |
| `attested_key_id` | beside | `key-id` | — | REQUIRED | — | [2.1](#2.1) | Equals row.attested_key_id. |
| `attestation_type` | beside | `row-type` | — | REQUIRED | — | [2.4](#2.4) | Equals row.attestation_type. |
| `weight` | beside | `float` | — | OPTIONAL | absent | [2.1](#2.1) | Equals row.weight; absent iff absent. |
| `asserted_at` | beside | `rfc3339` | — | REQUIRED | — | [2.6.7](#2.6.7) | Read out of the signed member at the mint; a column that disagrees is refused typed_diverges_from_envelope. |
| `expires_at` | beside | `rfc3339` | — | OPTIONAL | absent | [2.1](#2.1) | Present iff the signed member is. |
| `subject_key_ids` | beside | `[* subject-id]` | set | OPTIONAL (absent when empty) | absent | [2.3](#2.3) | Equals row.subject_key_ids as a list. |
| `cohort_scope` | beside | `cohort-scope` | — | REQUIRED | — | [2.3.3](#2.3.3) | Equals row.cohort_scope. No wire default; the authoring default is the smallest scope (CC 1.13.3.4). |
| `attestation_envelope` | beside | `envelope` | — | REQUIRED | — | [2.1](#2.1) [2.6.1](#2.6.1) [2.6.1.3](#2.6.1.3) | The signed object itself, stored and relayed as received (2.6.1.1). The signing input is JCS(attestation_envelope) and nothing else. |
| `original_content_hash` | beside | `hex64` | — | REQUIRED | — | [2.6.1.3](#2.6.1.3) [2.6.3](#2.6.3) | Lowercase hex SHA-256 of JCS(attestation_envelope); recomputed at federation-tier ingest and refused on mismatch. |
| `additional_scrubs` | beside | `[* scrub-sig]` | sequence | OPTIONAL (absent when empty) | absent | [2.4](#2.4) [3.2](part_3_the_namespace.md#3.2) | Second and later signers over the same JCS bytes, each verified against its own scrub_key_id's pinned keys. This is the carrier of quorum on a row. |
| `persist_row_hash` | beside | `hex64` | — | OPTIONAL (store-computed; absent on a row as emitted) | — | — | Store-computed over the row's own serialisation (not JCS), excluding itself; informational on the wire, never re-verified on read (CC 2.6.1.3). Not a conformance target. |
| `withdraws_admission_rule` | local | `uint` | — | OPTIONAL | absent | [2.4.1.1](#2.4.1.1) | Audit metadata: which rule (0 to 4) admitted a withdraws; persist-internal. |
| `tier` | local | `"local" / "federation"` | — | OPTIONAL | federation | [3.1.3](part_3_the_namespace.md#3.1.3) | Persist-internal; absent on the wire for a federation row. Not in the signed bytes, so a promoted row is byte-identical to a native one. |
| `promoted_at` | local | `rfc3339` | — | OPTIONAL | absent | [3.1.3](part_3_the_namespace.md#3.1.3) | Persist-internal. |
| `scrub_signature_classical` | beside:signature | `base64` | — | REQUIRED | — | [2.6.5](#2.6.5) [2.6.1.1.1](#2.6.1.1.1) [5.3.2.4.3.1](part_5_transport_substrate.md#5.3.2.4.3.1) | Ed25519 (RFC 8032) over JCS(attestation_envelope); RFC 4648 section 4 standard alphabet, padded. |
| `scrub_signature_pqc` | beside:signature | `base64` | — | REQUIRED at the federation tier | — | [2.6.5](#2.6.5) [5.3.2.4.3.1](part_5_transport_substrate.md#5.3.2.4.3.1) [6.1.3](part_6_the_coherence_mathematics.md#6.1.3) | ML-DSA-65 (FIPS 204) over JCS(attestation_envelope) followed by the raw 64 Ed25519 signature bytes (the bound-payload form); verified under the strict hybrid policy, never classical-only. |
| `scrub_key_id` | beside:signature | `key-id` | — | REQUIRED | — | [2.1](#2.1) | On an attestation row the verifier resolves attesting_key_id, so this names the same key; assemble sets both from one key. (On a key record it may name an anchor, CC 3.2.) |
| `scrub_timestamp` | beside:signature | `rfc3339` | — | REQUIRED | — | [2.6.7](#2.6.7) | When the signature was issued: asserted_at, or widened_at on a widening. Outside the bytes. |
| `pqc_completed_at` | beside:signature | `rfc3339` | — | OPTIONAL | — | [5.3.2.4.3.1](part_5_transport_substrate.md#5.3.2.4.3.1) | When the ML-DSA-65 half was attached. Outside the bytes. |
| `additional_scrubs[].scrub_key_id` | beside:cosign | `key-id` | — | REQUIRED | — | [2.4](#2.4) [3.2](part_3_the_namespace.md#3.2) | The cosigner; must resolve to a registered key. |
| `additional_scrubs[].scrub_signature_classical` | beside:cosign | `base64` | — | REQUIRED | — | [2.6.5](#2.6.5) | Ed25519 over the same JCS(attestation_envelope). |
| `additional_scrubs[].scrub_signature_pqc` | beside:cosign | `base64` | — | REQUIRED at the federation tier | — | [2.6.5](#2.6.5) | ML-DSA-65 over the same JCS bytes followed by this entry's Ed25519 signature. |
| `additional_scrubs[].cosigned_at` | beside:cosign | `rfc3339-ms` | — | OPTIONAL | absent | [2.6.7](#2.6.7) | When the cosignature was applied; outside every preimage, so stamping it moves no signed byte. |

**The key record — the second signed object (outer shape; its envelope's member table is the key plane's)**

| Member | Placement | Type | Array | Presence | Default | CC | Note |
|---|---|---|---|---|---|---|---|
| `key_id` | beside | `key-id` | — | REQUIRED | — | [2.6.8](#2.6.8) [3.2](part_3_the_namespace.md#3.2) | <label>-<fingerprint>, the fingerprint the first ten lowercase base32 characters of sha256(ed25519 public key). |
| `pubkey_ed25519_base64` | beside | `base64` | — | REQUIRED | — | [3.2](part_3_the_namespace.md#3.2) [5.3.2.4.3.1](part_5_transport_substrate.md#5.3.2.4.3.1) | Raw 32-byte key. |
| `pubkey_ml_dsa_65_base64` | beside | `base64` | — | REQUIRED for algorithm hybrid | — | [5.3.2.4.3.1](part_5_transport_substrate.md#5.3.2.4.3.1) | Raw 1952-byte key; the substrate takes writes only at algorithm hybrid. |
| `algorithm` | beside | `tstr` | — | REQUIRED | — | [5.3.2.4.3.1](part_5_transport_substrate.md#5.3.2.4.3.1) | hybrid on every admitted record. |
| `identity_type` | beside | `tstr` | — | REQUIRED | — | [3.4.7.1](part_3_the_namespace.md#3.4.7.1) | A set rendered as one string; see CC 3.4.7.1. |
| `identity_ref` | beside | `tstr` | — | REQUIRED | — | [3.2](part_3_the_namespace.md#3.2) |  |
| `valid_from` | beside | `rfc3339` | — | REQUIRED | — | [2.1](#2.1) |  |
| `valid_until` | beside | `rfc3339` | — | OPTIONAL | absent | [2.1](#2.1) | Its signed twin is inside registration_envelope (CLM-key-validity-window). |
| `registration_envelope` | beside | `object` | — | REQUIRED | — | [3.2](part_3_the_namespace.md#3.2) [3.3.6](part_3_the_namespace.md#3.3.6) | The key record's signed object: JCS(registration_envelope) is the signing input for the base scrub and every additional scrub. Its member table is the key plane's (key:record:v1) and is not enumerated here. |
| `original_content_hash` | beside | `hex64` | — | REQUIRED | — | [2.6.1.3](#2.6.1.3) | Lowercase hex SHA-256 of JCS(registration_envelope). |
| `scrub_signature_classical` | beside:signature | `base64` | — | REQUIRED | — | [2.6.5](#2.6.5) | Ed25519 over JCS(registration_envelope). |
| `scrub_signature_pqc` | beside:signature | `base64` | — | REQUIRED once hybrid-complete | — | [2.6.5](#2.6.5) | ML-DSA-65 over JCS(registration_envelope) followed by the Ed25519 signature bytes. |
| `scrub_key_id` | beside:signature | `key-id` | — | REQUIRED | — | [3.2](part_3_the_namespace.md#3.2) | Self-scrub when equal to key_id; an anchor scrub when it names a pinned anchor (the one record kind where the scrubber may differ from the subject). |
| `scrub_timestamp` | beside:signature | `rfc3339` | — | REQUIRED | — | [2.6.7](#2.6.7) |  |
| `pqc_completed_at` | beside:signature | `rfc3339` | — | OPTIONAL | — | [5.3.2.4.3.1](part_5_transport_substrate.md#5.3.2.4.3.1) |  |
| `persist_row_hash` | beside | `hex64` | — | REQUIRED | — | — | Store-computed; excludes itself and consent_role; informational. |
| `roles` | beside | `[* tstr]` | set | OPTIONAL | [] | [3.4.7.1](part_3_the_namespace.md#3.4.7.1) | Serialised as roles; the record also carries roles inside the signed registration_envelope. |
| `attestation_evidence` | beside | `object` | — | OPTIONAL | absent | [4.2.2](part_4_composition_governance.md#4.2.2) | Hardware attestation blob. |
| `consent_role` | local | `tstr` | — | OPTIONAL | absent | [3.4.7.2](part_3_the_namespace.md#3.4.7.2) | Mutable operational marker, excluded from persist_row_hash and from the signed bytes. |
| `additional_scrubs` | beside | `[* scrub-sig]` | sequence | OPTIONAL (absent when empty) | absent | [3.2](part_3_the_namespace.md#3.2) | Second and later scrubs over the same JCS(registration_envelope); what lets a replicated record prove its own m-of-n. |

**Rules this table carries.** A set-kind array is sorted **and** unique, refused otherwise as `federation_set_semantics_unsorted` with the member named; a relay never re-sorts it, since re-sorting would move signed bytes. The form an emitter writes for `scope` is the array; a bare token is admitted as the one-element array it denotes, and nothing is normalised in signed bytes. An explicit JSON `null` on an optional member is refused as malformed ([CC 2.6.1.1.1](#2.6.1.1.1)). `witnesses[]` is a set. The quorum carrier is `additional_scrubs[]` beside the row, as [CC 2.1](#2.1) and [CC 2.4](#2.4) name it.

**Vectors.** [`manifests/signed_object_vectors.json`](../manifests/signed_object_vectors.json) carries two test identities (Ed25519 and ML-DSA-65 seeds, public keys and the [CC 2.6.8](#2.6.8) `key_id` derived from each), and for each vector the envelope, its JCS bytes, `original_content_hash`, both signature halves and the assembled row: a minimal `scores`; the same claim with an explicit default (different bytes, both verify, [CC 2.6.1.1](#2.6.1.1)); a cosigned variant; a `withdraws`; the at-cap and cap-plus-one envelopes as a recipe with their hashes; and refusal cases with their tokens. The signatures verify under the identities the file carries; the JCS bytes, the hashes and the Ed25519 half are recomputed from the vectors on every change to this document. A second implementation that reproduces these bytes and signatures has met the [CC 2.6.1.1.1](#2.6.1.1.1) byte-identity target for this object.

#### 2.6.1.8 `signed-object-cose` — The signed object of the v62 edition: CBOR and COSE (planned)

**Ruled, and planned (normative when the edition lands).** The signed object of the release candidate that accompanies the substrate's v62 is a CBOR object signed with COSE, aligned with the IETF's transparency work: SCITT's architecture ([RFC 9943]), COSE receipts ([RFC 9942]), ML-DSA in COSE ([RFC 9964]) and the composite signatures of the JOSE and COSE working group. This subsection states the shape in advance so that every implementer builds to one target; the JSON object of [CC 2.6.1.7](#2.6.1.7) stays the signed object of every earlier candidate, every row signed under it verifies as itself for ever, and none of its bytes move. The schema is `manifests/signed_object_v2.cddl`.

**The statement.** A row is one `COSE_Sign1`, one signer, as a SCITT signed statement is. **The mirror goes:** the row's type and family ride the content type, the author's key id rides `kid`, and the issuer and subject ride the CWT claims the architecture requires, all in the protected header, which the signature covers by construction, so nothing is written beside the bytes and again inside them. **A quorum is several statements:** the cosigned rows of [CC 2.4](#2.4) become one statement per signer over the same payload bytes, found by the **quorum key**, which is the digest of the payload alone in the same hash-agile form as the id, so that each signature is its own transparent statement with its own id and nothing is stripped when a statement is registered; `additional_scrubs` as a sidecar ends, and a fold counts statements by person exactly as it counts votes ([CC 4.5.13](part_4_composition_governance.md#4.5.13)). **Canonical bytes are CBOR's deterministic encoding** as the CBOR working group fixes it, and a verifier verifies the bytes it received, never a re-encoding of typed fields. **The statement id** is the digest of a labelled structure of the protected header and the payload, hash-agile, with the signature excluded, so one statement has one id whatever its signature and two signers over one payload have two ids and one quorum key; a statement whose content is low-entropy, a ballot or a census cell, carries a random salt as a payload member, bound by every signer, so neither its id nor its quorum key confirms a guess. **The hybrid is the composite:** the ML-DSA-65 with Ed25519 construction of the working group's draft, exactly, signing a domain-separated representative that binds both halves so neither verifies alone, carried under a private-use algorithm identifier until the IETF assigns one; the construction is adopted now, since the project cannot wait, and only the identifier changes later. **Keys** are one composite COSE key each, and a key id is its thumbprint ([RFC 9679]) computed under that identifier and fixed for the key's life, so key ids are this document's until the codepoint lands; the key id rotates with the key, and a person's stable reference is the thumbprint of their genesis key, carried as the issuer. **Instants** are integers of POSIX milliseconds in the envelope and the standard seconds claims in the header, derived by a fixed rule, never floats. **Free text leaves the envelope:** the `context` member becomes a bounded note in the body, every envelope member is bounded, and a reason code from a closed registry may stand in the envelope. **Erasability is minted, never retrofitted** ([CC 2.6.1.1](#2.6.1.1)): the form is the selective disclosure of the SPICE working group's CWT draft, exactly, with the member name this document's until a label is assigned, as with the algorithm; a blinded member is absent from the payload and is a disclosure, a salt of sixteen random bytes with the member's name and value, and the payload carries the digests of every disclosure in order, so a reader holding the statement alone sees how many members were minted blind and which are gone; erasure drops a disclosure and alters no signed byte. **A disclosure set is bytes, not a row member:** the statement replicates with its commitment and without its disclosures, the set is held on the bytes plane and fetched on demand under the same consent edge as any bytes the object's audience may pull, erasure is the bytes-plane tombstone, and a set that was never replicated is indistinguishable from one erased; the unprotected header, which the signature excludes, is the form in which a set is presented beside its statement to one who may see it, never the form in which it travels or is held. **Which members are blind is a column of the family model** ([CC 3.1](part_3_the_namespace.md#3.1)), checked when the manifest is vendored, so a row that seals a member its family blinds is refused at the door; and no fold, verdict or admission reads a member that can be blinded, since a node that erased it and a node that did not would otherwise disagree. A family whose erasure route is a subject request or a purge MUST mint every free-text member and every member whose content a party other than the signer authored as a blinded member, `body.note` first among them; identifiers, instants, references and the digests themselves stay sealed; a family whose route is none or a legal hold seals its members, and `body.note` in such a family is bounded as above and carries nothing a subject request could reach. **Receipts** over the provenance log and each stream's log are COSE receipts of [RFC 9942] over the SHA-256 tree of [RFC 9162], whose hashing is that of [RFC 6962], so every root already published stays valid; each witness issues its own receipt over the same root with its instant in the protected header, rather than signing inside another's, and a stream's receipts cover batches, never single chunks. **What stays as it is:** the view and the queue of [CC 4.5.13](part_4_composition_governance.md#4.5.13) are presentation and need no change; the per-chunk media trailer of [CC 5.3.3.2.3](part_5_transport_substrate.md#5.3.3.2.3) stays a raw signature over fixed big-endian fields, since no streaming standard offers per-sender authentication at all, and its preimage never parses as a COSE structure.

**The key exchange.** One hybrid KEM, X-Wing, serves every key wrap and every onion hop ([CC 5.4.6](part_5_transport_substrate.md#5.4.6)), under HPKE where a wrap is single-shot; the transit handshake of [CC 5.3.3.5](part_5_transport_substrate.md#5.3.3.5) is not a single-shot wrap and is a KEM-authenticated handshake with X-Wing inside it, as that section pins it.

**What moves and what does not.** Every preimage of the attestation plane moves: the signing input, the id, the cosignature set, the known-answer vectors, the signed-object table and its match vectors, and the relationship draft; and every other signed thing except the chunk trailer becomes a COSE object with its own `typ`, so no hand-laid layout and no little-endian field remains. Where this edition differs from SCITT it keeps differing: there is no transparency service and no registrar, since a trust decides what a node serves and no party stands in the middle.

**The migration is the one already named.** New domain, old rows verify as themselves, emission switches at the ceremony of the edition, once every node of the fleet reads both forms, and the genesis is re-signed in that ceremony, which the substrate's v62 already requires for its instant forms, so the fleet re-signs once; a release that reads both forms and still writes the earlier one is the new candidate before its switch, and is what the fleet runs until the ceremony. Receipts and custody acknowledgements signed by other people cannot be re-signed by that ceremony: their earlier forms verify as themselves for ever, a verifier chooses by kind and edition, and the earlier form is accepted only for a row anchored before the cutover, never after, so the old form cannot be offered in place of the new. **What anchors a row is a position in the provenance log**, never an instant a signer chose: the cutover is the log position of the first statement of the new edition the ceremony registers, an earlier-form receipt is accepted when the tree size it covers is at most the tree size at the cutover, and an earlier-form custody acknowledgement when the row it acknowledges sits at a position before it; a row that was never logged has no anchor and its earlier form is not accepted after the cutover. A node of the new candidate reads both objects and writes one; a node of an earlier candidate reads only its own. This document is still a release candidate of 1.0, and a candidate may move signed bytes while it says so and re-signs ([CC 2.6.4](#2.6.4)); the MAJOR rule binds from 1.0.

### 2.6.2 `canonicalization` — Date-time canonicalization

Every ISO 8601 / RFC 3339 datetime in this specification MUST be:

- UTC (suffix: literal `Z`; the offset form `+00:00` MUST NOT be used)
- Millisecond-precision (exactly three digits of fractional seconds; trailing zeros required)
- Lowercase `z` MUST NOT be used; uppercase `Z` only

Canonical form: `YYYY-MM-DDTHH:MM:SS.sssZ`. Example: `2026-05-28T13:45:09.000Z`. Producers MUST emit this form; consumers MUST reject any other form when verifying a signature.

### 2.6.3 `canonicalization-hexadecimal` — Hexadecimal canonicalization

Every hex string used in canonical-bytes encoding (e.g., SHA-256 digests in `root_hash`, public-key fingerprints) MUST be **lowercase**, **unpadded** (no leading `0x`, no separators), and **byte-length-exact** (a SHA-256 digest is exactly 64 hex characters). Producers MUST emit lowercase; consumers MUST reject uppercase when verifying.

### 2.6.4 `policy-versioning` — Versioning policy

The grammar can evolve only if every change announces whether it breaks the wire. SemVer makes that announcement machine-legible, so a peer knows from the version alone whether it can still interoperate.

CEG follows **SemVer 2.0.0** with these mapping rules:

- **MAJOR (X.0.0)** — any wire-incompatible change: removal of an envelope field, change of a field's semantic, removal of a structural primitive, or change to canonical-bytes domain-separation labels. Also MAJOR: removal or breaking-redefinition of a [CC 3.1](part_3_the_namespace.md#3.1) prefix, change to a [CC 3.4](part_3_the_namespace.md#3.4) reservation, or change to the CC 2.6.9 / CC 2.2 conformance language.
- **MINOR (0.X.0)** — wire-compatible additions: new prefix in [CC 3.1](part_3_the_namespace.md#3.1), new envelope field with documented default, new composition policy in [CC 4.4](part_4_composition_governance.md#4.4), new endpoint shape in [CC 5.3](part_5_transport_substrate.md#5.3), new optional conformance subsection. Existing Conforming Producers and Consumers continue to interoperate without modification.
- **PATCH (0.0.X)** — clarifications, editorial fixes, additions to non-normative sections (open-vocabulary lists, glossaries [CC 8.1](part_8_appendices.md#8.1)), addition to [CC 8.3](part_8_appendices.md#8.3) acknowledged-gaps, fixes to non-normative examples in [CC 8.1](part_8_appendices.md#8.1).

The wire surface is frozen at 1.0. Until 1.0 is cut this document is a release candidate. A release candidate ordinarily adds, clarifies and corrects under the MINOR and PATCH rules above and moves no signed byte. Where a candidate must move signed bytes before 1.0, it says so in its own text, keeps every row signed under the earlier form verifying as itself, and re-signs the genesis once. The v62 edition is such a candidate: it moves signed bytes before 1.0 for the signed object ([CC 2.6.1.8](#2.6.1.8)). The MAJOR rule binds from 1.0: a MINOR may add an optional member, and a row signed before the addition verifies unchanged. From 1.0, a change that would alter the signed bytes of any conforming row is a new MAJOR, announced as such.

A **removal notice** is given by marking the affected element as scheduled for removal, naming the version that gives notice and a removal target (e.g., `removal: 2.0`). An element under notice MUST remain interoperable until the announced removal version. Removal is a MAJOR change per the rules above.

**The wire vocabulary is a hash-pinned artifact.** The set of message types the substrate recognizes — the *wire vocabulary* — is not the emergent product of individual repos' needs but a ratified contract. The contract is expressed as a versioned, hash-addressable artifact, [`manifests/WIRE_VOCABULARY.md`](../manifests/WIRE_VOCABULARY.md), governed in **two tiers** (the RFC 8126 partitioned-registry discipline). **Tier 1** holds the message types whose canonicalization is load-bearing to an ethical primitive (attestations, votes, moderation/slashing, deferral, steward directives, key registration, the humanity-accord path, `withdraws`, goals, build provenance, content/blob fetch). Tier 1 is closed and CC-ratified: a Tier-1 addition rides the ordinary [CC 4.5.1](part_4_composition_governance.md#4.5.1) amendment (the "Standards Action" bar), a working reference implementation, and a coordinated cut. **Tier 2** — app-tier remote-procedure channels whose inner semantics are the app's concern — uses three opaque envelopes (`OpaqueRequest` / `OpaqueResponse` / `OpaqueEvent`) carrying a `kind` from a reserved per-repo range delegated to the range steward (the "Private Use" bar). No CC amendment is required to define a `kind`. Every ratifying repo **pins the artifact's SHA-256 at build**; a hash mismatch at cohabitation is a substrate-tier build failure, not a warning. Amendment is a substrate-coordinated event across the covenant of ratifying repos; unanimous hash-commit blocks the *cut*, never the *decision* (the decision is the CC 4.5.1 amendment). This governs the **transport vocabulary** — a surface distinct from, and complementary to, the frozen [CC 1.7](part_1_foundation.md#1.7) 1+4 attestation grammar: 1+4 freezes what a claim *is*; the wire vocabulary governs the message types that *carry* claims.

### 2.6.5 `references` — Normative References

The following documents are normatively cited; implementations MUST conform to them where referenced inline.

| Short name | Normative document |
|---|---|
| [BCP 14] | [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) + [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) — keywords for use in RFCs |
| [FIPS-180-4] | [FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) — SHA-256 and the SHA-2 family |
| [FIPS-202] | [FIPS 202](https://csrc.nist.gov/pubs/fips/202/final) — SHA-3 / SHAKE128 / SHAKE256 / TupleHash |
| [FIPS-204] | [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final) — ML-DSA (Module-Lattice-Based Digital Signature Algorithm); CEG uses parameter set ML-DSA-65, the post-quantum half of the hybrid signature |
| [RFC-3339] | [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) — Date and Time on the Internet, with fractional-seconds disambiguation in CC 2.6.2 below |
| [RFC-5905] | [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905) — Network Time Protocol Version 4 |
| [RFC-6962] | [RFC 6962](https://www.rfc-editor.org/rfc/rfc6962) — Certificate Transparency; this spec's transparency-log discipline tracks 6962 except where 6962-bis (RFC 9162) supersedes |
| [RFC-8032] | [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032) — Edwards-Curve Digital Signature Algorithm (EdDSA); specifically Ed25519 |
| [RFC-8174] | [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (with BCP 14) |
| [RFC-8785] | [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) — JSON Canonicalization Scheme (JCS); used where this spec serializes JSON for signing |
| [RFC-9162] | [RFC 9162](https://www.rfc-editor.org/rfc/rfc9162) — Certificate Transparency v2.0 (CT-bis); MUST be used for new transparency-log integrations; older 6962 instances continue to interoperate |
| [ISO-639-1] | [ISO 639-1:2002](https://www.iso.org/standard/22109.html) — Codes for the representation of names of languages, two-letter |
| [BCP-47] | [BCP 47](https://www.rfc-editor.org/info/bcp47) ([RFC 5646](https://www.rfc-editor.org/rfc/rfc5646)) — Tags for identifying languages; for locale strings richer than ISO 639-1 alone |
| [RFC-9420] | [RFC 9420](https://www.rfc-editor.org/rfc/rfc9420) — Messaging Layer Security (MLS); the streaming epoch-key rekey ([CC 5.1](part_5_transport_substrate.md#5.1)) conforms to MLS TreeKEM |
| [SFrame] | [RFC 9605](https://www.rfc-editor.org/rfc/rfc9605) — Secure Frame (SFrame); the per-frame AEAD chunk seal ([CC 5.3.3.1](part_5_transport_substrate.md#5.3.3.1)) conforms to the SFrame model |
| [FIPS-203] | [FIPS 203](https://csrc.nist.gov/pubs/fips/203/final) — ML-KEM (Module-Lattice KEM); the post-quantum half of the hybrid KEM (ML-KEM-768) |
| [RFC-9180] | [RFC 9180](https://www.rfc-editor.org/rfc/rfc9180) — Hybrid Public Key Encryption (HPKE); the `key_grant` wrap shape |
| [RFC-4648] | [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648) — The Base16, Base32, and Base64 Data Encodings; the base64 pin of [CC 2.6.1.1.1](#2.6.1.1.1) and the base32 `key_id` fingerprint |
| [RFC-8949] | [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949) — Concise Binary Object Representation (CBOR); the signed object's CDDL ([CC 2.6.1.7](#2.6.1.7)) and the deterministic-CBOR `record_id` profile ([CC 5.3.3.2](part_5_transport_substrate.md#5.3.3.2)) |
| [RFC-5869] | [RFC 5869](https://www.rfc-editor.org/rfc/rfc5869) — HMAC-based Extract-and-Expand Key Derivation Function (HKDF); every key derivation of Part 5 |
| [X-Wing] | [draft-connolly-cfrg-xwing-kem](https://datatracker.ietf.org/doc/draft-connolly-cfrg-xwing-kem/) — X-Wing: general-purpose hybrid post-quantum KEM; the onion hop key and the hybrid KEM of Part 5 |
| [HPKE-PQ] | [draft-ietf-hpke-pq](https://datatracker.ietf.org/doc/draft-ietf-hpke-pq/) — Post-quantum and hybrid KEMs for HPKE; the X-Wing HPKE suite |
| [XChaCha] | [draft-irtf-cfrg-xchacha](https://datatracker.ietf.org/doc/draft-irtf-cfrg-xchacha/) — XChaCha: eXtended-nonce ChaCha and AEAD_XChaCha20_Poly1305; the symbol and frame AEAD of Part 5 |
| [hybrid-sig] | The **bound-hybrid signature**: Ed25519 ([RFC-8032]) over the canonical bytes, and ML-DSA-65 ([FIPS-204]) over the canonical bytes ‖ `ed25519_sig` (the bound-payload form, [CC 3.1.2.1](part_3_the_namespace.md#3.1.2.1)); both halves verified at every federation-tier admission gate and on the store path, never an operator toggle — normative at [CC 5.3.2.4.3.1](part_5_transport_substrate.md#5.3.2.4.3.1) and [CC 6.1.3](part_6_the_coherence_mathematics.md#6.1.3) |

Informational citations (Magnifica Humanitas, anthropological literature, Ubuntu philosophical literature, etc.) appear in [CC 8.6.1](part_8_appendices.md#8.6.1) without normative force.

### 2.6.6 `canonicalization-cell` — H3 cell canonicalization

Geographic claims compose with [CC 3.3.3](part_3_the_namespace.md#3.3.3) `location_proof` and [CC 3.2](part_3_the_namespace.md#3.2) `community` with `cohort_subkind: geographic`.

Geographic primitives in CEG use [H3 hierarchical hexagonal indexing](https://h3geo.org/) as the canonical cell-identifier encoding. H3 partitions the Earth's surface into hexagonal cells at 16 resolution levels (0 = coarsest, ~4.3 M km² per cell; 15 = finest, ~0.9 m² per cell). Each cell has a 64-bit integer ID, conventionally encoded as a 15-character lowercase hex string.

**Canonical form for `cell_id`**:

- 15-character lowercase hex string (no `0x` prefix; per [CC 2.6.3](#2.6.3))
- The cell encodes its own resolution in the standard H3 index bit layout. A conformant decoder extracts the resolution **via the H3 library** (the resolution field lives in bits 52–55), **NOT** by reading the high 4 bits. The high nibble is the H3 **mode marker** (cell-mode = `1`), not the resolution
- Leading zeros preserved (a resolution-0 cell at base position 0 is `8001fffffffffff`, not `1fffffffffff` — the high nibble `8` is the mode marker, correctly consistent with res-0)

**Canonical form for `cell_resolution`**:

- Integer in `[0, 15]`
- MUST equal the resolution **decoded from the H3 index** of `cell_id` (substrate verifies the redundancy on admission via the H3 library; mismatched pairs MUST be rejected as malformed)

#### 2.6.6.1 `location` — Rough-only enforcement for `location_proof` (normative)

Location disclosure is bounded by the protocol itself, not by operator goodwill — the Non-maleficence principle made mechanical. A `location_proof` subject_kind Contribution ([CC 3.3.3](part_3_the_namespace.md#3.3.3)) MUST carry `cell_resolution ≤ 7` (an H3 resolution-7 hexagon averages about 5 km² in area, sufficient for city/borough-level disclosure without block/building precision). Producers attempting to emit finer-resolution `location_proof` Contributions MUST have admission rejected at the substrate gate.

This is the wire-format-enforced privacy promise: **rough is rough by protocol**, not by operator policy. A producer cannot accidentally over-share at the protocol layer; a malformed client cannot publish a precise location even if its UI fails to gate. Substrate emits `hard_case:location_proof_resolution_violation` ([CC 3.4.2](part_3_the_namespace.md#3.4.2)) on rejection so operators can observe malformed-producer patterns.

#### 2.6.6.2 `cell` — Cell containment

A cell `C` at resolution `R_C` is **contained within** a cell `B` at resolution `R_B` iff:

- `R_C >= R_B` (the contained cell is at equal or finer resolution); AND
- The parent-walk from `C` at resolution `R_C - 1, R_C - 2,..., R_B` reaches exactly `B` (standard H3 hierarchy semantics; `h3ToParent` library call)

Used by community admission gates per [CC 4.4.3.2](part_4_composition_governance.md#4.4.3.2) Policy M: a `location_proof` Contribution's `cell_id` MUST be contained within the geographic community's `geographic_constraint.cell_id` for membership admission.

#### 2.6.6.3 `documents` — Scope of the H3 rule

Scope pointer: the H3 canonicalization rules above (lowercase-hex `cell_id`, rough-only `cell_resolution ≤ 7`, containment for community admission).

What the H3 rule does NOT do:
- Mandate H3 over alternative geospatial systems (S2, Geohash) — H3 is chosen for hex-cell uniformity, well-defined parent/child hierarchy, and protocol-agnostic absence of a centralized gazetteer dependency. Operator-internal use of other systems is unconstrained; the wire format uses H3 ([CC 2.6.6](#2.6.6)).
- Provide a place-name registry. Communities self-name; cell IDs are the substrate-level binding. UI may map cell IDs to human-readable names per consumer policy.
- Restrict community-side `geographic_constraint.cell_resolution`. A community CAN scope itself at any resolution (e.g., an "Austin metro" community at resolution 5, ~250 km²; a smaller-scale "Downtown Austin" community at resolution 7, ~5 km²). The rough-only invariant applies to `location_proof`, NOT to community definitions. A community whose `geographic_constraint` is finer than resolution 7 can admit nobody by containment, since no proof is finer than 7; such a community admits by invitation and the constraint describes it rather than gates it.

### 2.6.7 `time` — Time and clocks

This entry says which clock every stated instant refers to, and how far that instant may stand from the instant it is checked against. The window differs by case, and the table gives each one.

**The clock.** Every `signed_at`, `asserted_at`, `valid_until`, `delegation_valid_from`, `delegation_valid_until`, and `cosigned_at` in this specification refers to **wall-clock UTC** at the asserting peer's clock. Producers SHOULD synchronize via [NTPv4 (RFC 5905)](https://www.rfc-editor.org/rfc/rfc5905) or [Roughtime](https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/) to a known-good time source.

**The skew bound.** The maximum tolerated skew between attester clock and consumer clock for a freshness check is **±5 minutes** by default. Tighter thresholds MAY be applied by per-application consumer policy.

**The window by case.**

| Case | Window | Rule |
|---|---|---|
| An attestation whose `asserted_at` is in the future | 5 minutes in the future | Consumers receiving an attestation whose `asserted_at` is more than 5 minutes in the future MUST reject it with `CLOCK_SKEW_VIOLATION` ([CC 5.3.6.1](part_5_transport_substrate.md#5.3.6.1)). A `constitutional` halt is the one exception: a node acts on it at receipt whatever its `asserted_at`, and counts the fuse from receipt ([CC 4.2.1.1](part_4_composition_governance.md#4.2.1.1)). |
| A cosignature on a single STH ([CC 5.3.1](part_5_transport_substrate.md#5.3.1)) | 5 minutes from the STH's published `signed_at`. Time-skew between cosigners on a single STH is bounded by the STH's own `signed_at` field. | Cosignatures with `signed_at` farther than 5 minutes from the STH's published `signed_at` MUST be rejected. |
| A long-lived attestation carrying `valid_until` in the future | The freshness check is "the attestation has not yet reached its `valid_until`, AND the consumer's own clock is within ±5 minutes of the known-good time source it synchronises to". | A consumer whose clock drifts past the skew bound MUST fail-secure (reject) rather than accept. |
| A `node` or `agent` key record ([CC 2.4.1.1](#2.4.1.1)) | its own `valid_until`, at most `key_record_max_secs` after its `asserted_at` | Read from the record alone against the reader's clock. Peers MUST NOT apply an arrival-clock check to a replicated record. |
| A row whose admission walks a `delegates_to` chain | **`W` = 72 hours** (259 200 s) before the receiver's clock | The substrate MUST refuse such a row whose `asserted_at` precedes the receiver's clock by more than `W`, with the refusal token **`asserted_at_stale`**. |
| A cosigned roster event | none | A cosigned roster event is counted over the members at the roster head it names, and its signed instant decides no one's standing ([CC 3.3.4](part_3_the_namespace.md#3.3.4)). |
| Rows not judged on a chain (traces, scores on the base) | not bound by `W` | The future bound of the first line is unchanged. |

**The admission freshness window `W` (normative).** `W` is the window of the fourth line of the table. Every row whose admission walks a `delegates_to` chain — a key wrap (`key_grant:*`), a consent row, a licence (`licensure:*`), a deferral response, the epoch-axis membership check — is judged at its signed `asserted_at` at the node that receives it. That instant is signer-chosen, so it is bounded. `W` is the participation-window baseline, one "until everyone has heard" constant ([CC 4.2.6](part_4_composition_governance.md#4.2.6)). A row refused `asserted_at_stale` is well-formed, not malformed, and it is not admitted-as-stale. The remedy is to re-sign. A signer back from a week offline is present and can.

**Why the window exists.** Without the bound a delegate whose chain was withdrawn could sign a row dated inside its old live window and have it admit. With it, a withdrawn delegate keeps at most `W` of backdatable authority at a node that holds the withdrawal. That is exactly the honest divergence at a node that does not hold it. A withdrawal takes full effect at each node within `W` of that node holding it, no worse than replication already is.

### 2.6.8 `key_id` — FedCode — the kind-tagged identity shorthand; NodeCode v1 retained as `kind: node` (normative)

This entry sets the short code that stands for a federation identity, and the format of the `key_id` that the code renders. It gives the code's kinds, how a code resolves to nodes, the wire format, five constraints, the commitment to the PQC half of the key, and how a node given its owner's code comes to be owned.

Federation `key_id`s are long opaque identifiers, unfit for a human to type or read aloud. **FedCode** is the **one** human-shareable shorthand: a compact, QR-able, checksummed render of a federation entity's identity for **bootstrap UX**. It is pinned here so **every implementation renders and parses the same code for the same key**. That is a cross-impl determinism requirement of the same class as [CC 2.6.3](#2.6.3) hex / [CC 2.6.1](#2.6.1) JCS. FedCode is a deterministic render of an existing `key_id`, **not** a new envelope field. It is additive on the frozen 1+4 surface. The `kind` byte is a payload discriminator of the same discipline as `subject_kind` riding the single `scores` shape ([CC 3.3.2](part_3_the_namespace.md#3.3.2)). Resolution is **DNS-free**. The reference implementation is the verifier; every other component decodes through it.

**Tied to the user, not the node (the model).** The v1 **NodeCode** (`CIRIS-V1-`) renders a *node's* key and is retained as `kind: node`. The code is tied to the **entity** — five kinds, of which three are [CC 3.4.7.1](part_3_the_namespace.md#3.4.7.1) `identity_type` roles and two are rostered `subject_kind`s:

```
kind(1): 1=user  2=agent  3=node  4=family  5=community
```

A `user` code is the owner's identity; the owner's **nodes and transport are optional**. A code that carries them resolves with no directory — pairing, a QR across a table, an air-gapped hand-off. A code that carries none resolves through the **federation directory**. The consumer walks `nodes_owned_by(U)` — the exact inverse of `owner_of` ([CC 3.2](part_3_the_namespace.md#3.2); `n ∈ nodes_owned_by(U)` iff `owner_of(n) == U`, held by construction) — to find the nodes to transport to, **as visible to the walker**. A peer outside `U`'s `self` cohort holds only the owner-bindings of `U` whose audience names it ([CC 5.2](part_5_transport_substrate.md#5.2) audience rule). Those are the federation-scoped ones, those re-signed at a group it shares with `U`, and one addressed to it as a contact ([CC 3.2](part_3_the_namespace.md#3.2)). So a stranger's directory walk yields exactly the announced roster of [CC 5.4.6](part_5_transport_substrate.md#5.4.6), while `U`'s own nodes see every binding. A node whose owner resolves ambiguous is **skipped, not fatal**: one poisoned node does not make its owner unroutable, while a direct query about that node still fails closed.

**Wire format (normative).** Binary payload, then **CRC-16-CCITT** (polynomial `0x1021`, init `0xFFFF`, no final xor) appended as 2 bytes big-endian, then **RFC 4648 base32** (alphabet `A–Z2–7`, padding stripped on encode, re-padded on decode). The result is prefixed by the version token and grouped into 4-character dash-separated chunks for display; the QR form is ungrouped. Decoders normalize (drop whitespace, upper-case, strip dashes) and accept the undashed prefix. All length-prefixed fields are 1-byte length, ≤ 255 UTF-8 bytes; an overflow is malformed.

```
v2 payload  (prefix CIRIS-V2-)
  version(1)=0x02 | kind(1) | sha256(key_id)(32) | ed25519_pubkey(32)
  | LP(key_id) | hint(transport) | hint(alias) | hint(group_key_id)
v3 payload  (prefix CIRIS-V3-)  — all v2 fields byte-identical, then:
  node_count(1) = 0..=16
  node_count × [ LP(node_key_id) | transport_ed25519(32) ]
  pqc_commitment: 0x00 absent | 0x01 + 32 raw bytes = sha256(ML-DSA-65 pubkey)
```

`LP` = 1-byte length prefix + UTF-8; `hint` = `0x00` when absent, else `LP`. `group_key_id` is the family/community `*_key_id`, absent otherwise. `sha256(key_id)` binds the display `key_id` into the CRC-protected payload — a decoder MUST verify it against `key_id`. The v1 layout is retained unchanged: `version=0x01 | key_id_hash(32) | pubkey(32) | LP(key_id_str) | LP(transport_hint) | LP(alias_hint) | crc16` under `CIRIS-V1-`.

**Constraints (each MUST be enforced at encoder AND decoder — a code minted by another implementation is exactly the case an encoder cannot police).**

1. **An embedded node key is the node's TRANSPORT Ed25519 — never the owner's federation key, never the node's federation key.**

   A destination derived from a federation key is `sha256(fed)[..16]`, an explicit-hash destination that categorically cannot be announced, so no peer can self-learn a route to it. A code whose embedded transport key equals the owner's pubkey MUST be rejected.

2. **Only `kind = user` MAY embed nodes.**

   "The owner's nodes" is meaningless for a node, and a group's destinations are group-scoped material a code MUST NOT carry at all ([CC 5.4.6](part_5_transport_substrate.md#5.4.6)). A code carries transport destinations and nothing of a group: an announced node's, or an unannounced node's handed by the owner's own hand, which is how an unannounced person is reached at all ([CC 5.4.6](part_5_transport_substrate.md#5.4.6)). Either carries no anonymity claim, since the holder of the code learns only what the owner chose to hand and nobody else can find the node. What a code never carries is an anonymous-tier identity, which is a different thing from an unannounced one, or group-scoped material.

3. **`node_count ≤ 16` and total payload ≤ 1024 bytes before base32.**

   Bounding the count without bounding the size bounds the wrong thing: 16 × 255-byte ids exceeds what a QR can render, defeating the hand-off the format exists for.

4. **Empty is valid and is the default.**

   A code with no nodes and no commitment MUST encode as **v2, byte-identically**, so nothing already issued moves; only a non-empty tail emits `CIRIS-V3-`.

5. **Compatibility.**

   v1 decodes as `kind: node`; v2 decodes unchanged; a v3 decoder accepts all three prefixes; a v2-only decoder MUST reject `CIRIS-V3-` outright rather than mis-parse it — the prefix differs before any payload byte is read.

**The PQC commitment (normative).** A code names an Ed25519 key and nothing else, but the substrate takes `federation_keys` writes only at `algorithm: hybrid` (Ed25519 + ML-DSA-65; [CC 5.3.2.4.3.1](part_5_transport_substrate.md#5.3.2.4.3.1)). So without more, a code-admitted key has no PQC half to register and pairing has no conformant path. The ML-DSA-65 public key is 1952 bytes, which would end the code's life as something a person can read aloud. The code therefore carries the **32-byte commitment** `sha256(raw ML-DSA-65 public key)`. Rules:

- **(a)** The host admits the classical half plus the commitment, fetches the ML-DSA body through the existing Key Pull, and verifies it against the commitment **before** writing a hybrid record. Nothing is registered until both halves are present and bound, so the hybrid-only rule is preserved, not weakened.
- **(b)** The commitment applies to **any** kind of code — a plain `user` code with no nodes emits v3 with `node_count = 0`.
- **(c)** The commitment is presence-tagged and **last**, so a v3 code minted before it still decodes with the commitment absent.
- **(d)** The API form is exactly 64 **lowercase** hex characters, **rejected, never repaired** — normalizing case would let two spellings of one identity mint two codes.
- **(e)** A FedCode is **unsigned**: the commitment inherits exactly the trust of the code carrying it and adds no authority. A conforming implementation MUST NOT treat a commitment match as authentication of the identity; what it buys is that a Key Pull cannot be substituted after the fact.

A code with **no** commitment fails closed at the pull check: there is nothing to bind the pulled key to.

**`key_id` format (normative).** `key_id = "<label>-<fingerprint>"`, `fingerprint` = the first **10 base32 characters** (50 bits) of `sha256(ed25519_pubkey)`, lowercased; `label` is lowercased and reduced to `[a-z0-9-]`, cosmetic. **Collision-resistant by construction, not collision-free** — the suffix is bound to the key, so two entities choosing one label collide only if their keys' hashes share 50 bits. Under one label that becomes likely near **2²⁵ keys** (the birthday bound), not 2⁵⁰. **Verifiable** — anyone recomputes the suffix from the pubkey (a random UUID cannot do this: one could claim another's). Friendly — `alice-k7f3qd2pza` reads as a name. **Registry global-uniqueness is therefore load-bearing, not a backstop**: a registrar MUST refuse a second key under an already-registered `key_id`, and a consumer resolving a `key_id` MUST verify the fingerprint against the pubkey it obtains ([CC 2.6.8](#2.6.8) constraint above). So an aliasing collision is detected at registration and never at resolution. The fingerprint is ten characters at every deployment size, because a consumer recomputes that length and a longer suffix fails the check. A deployment expecting more than **2¹⁶ identities under one label** relies on the registrar's refusal above, which detects a collision at registration.

**Onboarding — usercode → owner (the chosen model).** Put the owner's usercode (`kind: user`) in a node's configuration and the node becomes one of the owner's devices with **one approval tap and no PIN or QR handshake**. It does so under the honest constraint of [CC 1.13.2](part_1_foundation.md#1.13.2): owner-binding MUST be a **user-signed** `delegates_to`, so a node cannot make itself owned by reading a pubkey. On boot the node decodes the usercode, learns its intended owner `U`, and sends `U`'s node a **device-join request** signed by its own node key ([CC 3.2](part_3_the_namespace.md#3.2), Adding a device) — trust-and-serve only until owned. `U`'s client lists the pending requests. `U` compares the matching code their own node derives and approves; their hardware-rooted key then signs the two rows of [CC 3.2](part_3_the_namespace.md#3.2) (b), `delegates_to(U → node)` and the node's device occurrence. The pending-until-approved window **is** the safety property: a usercode is public (a pubkey), so a stolen one lets a node *request* ownership, never *obtain* it. A usercode embedding a pre-authorized signed delegation, so the node binds with no tap, would be a **bearer credential** (theft = silent ownership) and is NOT the default. If ever added it MUST be expiring, scope-limited, and revocable, by amendment.

### 2.6.9 `conformance-language` — Conformance language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [BCP 14](https://www.rfc-editor.org/info/bcp14) ([RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) + [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)) when, and only when, they appear in all capitals, as shown here.

#### 2.6.9.1 `informative` — Normative vs informative content (what interop requires)

A reader may **agree with the protocol and disagree with its philosophy** and still build a fully conforming implementation. The two are deliberately separable:

- **Normative (binding for interoperability):** the wire format and its conformance surface. That surface is the [CC 2.4](#2.4) structural primitives; the [CC 2.1](#2.1) envelope fields; the [CC 3.1](part_3_the_namespace.md#3.1) namespace + `subject_kind`s; and the [CC 2.6.1–2.6.2](#2.6.2) canonicalization rules. It is also the [CC 3.5](part_3_the_namespace.md#3.5) relation precedence; the [CC 3.4](part_3_the_namespace.md#3.4) reserved-prefix rules; the [CC 4.4](part_4_composition_governance.md#4.4) composition policies; the [CC 5.3](part_5_transport_substrate.md#5.3) endpoint shapes; and every RFC-2119-keyworded statement. This is exactly the surface enumerated in [CC 1.7](part_1_foundation.md#1.7) ("report the surface beside the invariant"). **Conformance is judged against this and nothing else.**
- **Informative (explanatory framing; NOT binding):** the motivating philosophy and rationale — notably [CC 1.13.1](part_1_foundation.md#1.13.1) (the Ubuntu / relational-anthropology substrate), the cross-tradition readings, and prose written as motivation rather than requirement. These explain *why* the normative choices were made; they add **no** conformance obligations. An implementer who rejects the anthropology but emits/consumes wire-correct Contributions is conforming.

Where framing produced a concrete wire consequence, that consequence is restated as a normative rule in its own section (e.g., structural invisibility is motivated informatively but enforced normatively at [CC 5.2](part_5_transport_substrate.md#5.2), bounded by [CC 1.13.3](part_1_foundation.md#1.13.3)). When in doubt, the RFC-2119 keywords and the [CC 1.7](part_1_foundation.md#1.7) surface govern; informative prose never overrides them.

## 2.7 `kernel` — The kernel

The kernel is what a set of signed rows concludes, given only what the rows name and who has consented. It is one function. A node gives it the rows it holds or has been offered, its own clock and its own key. It returns what every row means to that node, what the node may do, what it owes, and what to copy to whom. Everything else a node does is storage, transport or presentation.

It is a causal kernel. Order comes only from what rows name, and standing comes only from signed consent. No node agrees an order with another; each computes the same answer from the same set of rows. Each rule below has its home in the section it cites. A rule that cites no other section has its home here.

### 2.7.1 `kernel-inputs` — Inputs

| Input | What it is |
|---|---|
| rows | the signed rows the node holds or has been offered, each with the instant this node first held it |
| `now` | the node's own clock |
| own key | the key the node signs under |

The instant a node first held a row is its own receipt, outside the signed row and never replicated ([CC 4.5.13](part_4_composition_governance.md#4.5.13), the processor's state). There is no trust set among the inputs: who a node trusts is a fold over the rows its own key signed ([CC 4.4.3.8](part_4_composition_governance.md#4.4.3.8)). Configuration is not an input. A value that binds others is a row signed by whoever decided it, and a value that binds only the node is a row under the node's own key.

### 2.7.2 `kernel-order` — The only order is what rows name

A row names other rows by digest: the row it answers, the head it extends, the proposal it votes on. That relation is well founded, since a digest cannot name a row that names it back. There is no sequencer. Nothing ranks the rows of different signers by a signed instant, by arrival or by digest ([CC 3.3.4](part_3_the_namespace.md#3.3.4), [CC 4.5.1.3](part_4_composition_governance.md#4.5.1.3)). Two rows where neither names the other, directly or through other rows, are **concurrent**.

Judging each row as it arrives, against what was admitted so far, is not a function of the rows: one set can give two answers in two arrival orders. So the kernel reads what a row names, never what a node happened to admit before it.

One voice may order its own rows. Between two acts of one kind by one signer on one named row, the later signed instant wins and the lower row id breaks a tie ([CC 3.5.1](part_3_the_namespace.md#3.5.1)). A signer who back-dates changes only what that signer says. A session goes to the earliest claimed instant among one person's own devices, which is one voice ordering its own rows ([CC 3.1.3.1](part_3_the_namespace.md#3.1.3.1)). Rows of different signers are decided by a party's own rows, by a count, or by a fixed order on kinds ([CC 2.7.7](#2.7.7)). A listing is not a ranking: the order in which a ballot shows the roster is read by no rule ([CC 4.5.4](part_4_composition_governance.md#4.5.4)).

### 2.7.3 `kernel-layers` — Three layers

| Layer | Reads | Property |
|---|---|---|
| **kept** | the row alone, and whether the rows it names are kept | the least set closed under the door; the same in every arrival order |
| **concluded** | the row against its ancestors | one solution, with negation and counts allowed; final once the row is kept, for a rule that reads no row concurrent with it |
| **derived** | conclusions over a set of rows | a function of the kept set, the node's key and, in one place, `now` |

Admission stops, and ends at one kept set, in every arrival order. A row waits for what it names. It is never refused for what another row says: a check that reads another row concludes nothing, is not counted, is contested, or is kept and not served ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2), the refusals; [CC 4.5.13](part_4_composition_governance.md#4.5.13), the state processor).

Only the first two layers are final. A derived answer can be changed by a later row. After a counting cut on a slot, only a key that may cut that slot changes it. A key whose standing has ended can still change what a reader with no acknowledgement of its own concludes ([CC 2.7.9](#2.7.9)).

### 2.7.4 `kernel-operators` — Operators

Every rule cell of the tables is written in these operators.

| Operator | What it does |
|---|---|
| select | the rows matching a pattern on their fields |
| group and reduce | the least, the greatest, the one distinct value, the count of distinct values, or the sum |
| interval | whether a value lies between an opening and a closing |
| table cell | the value a typed table gives for a key |
| bounded repeat | a step applied until nothing changes |
| closure over what rows name | the past of a row; no cell needs more |
| integer arithmetic | an opening plus a duration, or a fraction of a base; no floating point |
| join on a named row | two rows that name the same row |
| result assembly | a verdict for each element, or a set of effects |

A reduce that meets a tie between two different rows concludes nothing for that group, and never breaks the tie by position. A count is over the members at the head its row names, never at the instant of a decision or of the count ([CC 3.3.4](part_3_the_namespace.md#3.3.4)).

### 2.7.5 `kernel-answers` — Named answers

Eight answers, each a composition of the operators. Each role, window, policy and constant they read is data.

| Answer | Question | Layer |
|---|---|---|
| **state** | is this row live: admitted, withdrawn, recanted, superseded | derived, since a later concurrent row on its target can change it |
| **stands** | does this key hold this relation over this object | derived: a bounded walk of live edges |
| **tally** | is this count met, over the head it names | derived |
| **may** | may this key do this act on this target, and if not, which row is missing and who could sign it | derived |
| **audience** | who is this row for | derived, since a row naming it may come later |
| **missing** | which rows that this conclusion depends on are not held | kept |
| **owed** | what this node must emit or do | derived |
| **window** | has this window closed, and with what outcome | derived; the one answer that reads `now` |

**stands.** One act underlies it: a voice consents to what binds it. A relation stands when every voice it binds has a concluded consent, one consent names the other, none is withdrawn by its own signer, and no cut removes it. A permission gives something of the signer's own and binds nobody else, so one row carries it. A duty binds the one who places it and the one who carries it, so it takes two consents ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2), [CC 4.5.4](part_4_composition_governance.md#4.5.4)).

That pair is the **seat**. It is two consents and no other object, and it stands the same whichever was signed first. Nobody is bound by the rows of others. Any bound voice ends the relation alone, and no third key ends it without a cut ([CC 4.5.4](part_4_composition_governance.md#4.5.4)).

Where a body places a duty, the body is one party, and its consent is a count of its members' signatures on the row. One voice is not a count. A count once met is final: no member's later row lowers it, and only the holder's own withdrawal or a cut ends the duty. The members are those at the head the row names, and no key admits itself ([CC 3.3.4](part_3_the_namespace.md#3.3.4)).

Who may place a duty is one of three: the object's own key, a key holding a seat that may confer, or a group whose count is met. A key stands when a bounded walk of live seats leads to it from a root. For what a row means to a node, the root is that node's own key ([CC 4.4.3.8](part_4_composition_governance.md#4.4.3.8)). An onward hop counts only from the authority's own acceptance edges. At each hop the remaining depth is the lesser of what is left and the edge's own, the classes intersect, and a cycle is visited once. A scope stands at the end of a walk only if every seat on it carries the scope, so nothing amplifies.

A duty seat over a community is one seat with four scopes: `moderate`, `review`, `slash` and `takedown`. The founding record seats the duty holders who sign it, and they are equals. A duty seat is conferred by a strict majority of the duty holders, or by a lone holder with the new holder's acceptance. It is withdrawn by a strict majority of the others, never on fewer than two voices where there are two holders ([CC 4.5.4](part_4_composition_governance.md#4.5.4)). A delegation that carries a scope seats its delegate only with the delegate's own signature ([CC 4.4.3.4.3](part_4_composition_governance.md#4.4.3.4.3)). A deputy holds no seat of its own: it acts under its delegator's seat, and what it may do ends when that seat ends. A duty seat validly conferred then stands as an equal. A claim seats no one ([CC 3.4.5.1](part_3_the_namespace.md#3.4.5.1)).

**may.** The door, the control a person is offered and the gate on serving a row are one answer, and a refusal names the missing row ([CC 4.5.13](part_4_composition_governance.md#4.5.13), one function run three ways). A screen is a function of the rows a node holds, the viewer's key and `now`. It offers exactly what the door admits, and never draws as sent a fact the node did not send.

**missing, and what is copied.** A row moves to a peer because that peer must conclude something and lacks it. What is sent is what lies among the ancestors of that conclusion, within the row's audience. A row whose audience is everyone may be served to anyone, and a stranger is routed nothing outside that. A node holds a row only when it is in the row's audience. Being in an audience permits serving a row and does not cause a send; a peer's own request for it is a cause. A row carries its audience to the rows it names when it is concluded, sits in the same room, and its signer is already in the named row's audience. A row leaves its room only by its own signer's act ([CC 5.2](part_5_transport_substrate.md#5.2)).

**window.** A row opens a clock. An answering row closes it, or time does, and the table states the outcome at the close. Where the outcome binds others, the concluder signs it as a landing row naming the acknowledgement by which it first held the opener, and its own head. Where it binds only the reader, each node reads the close on its own clock and signs nothing ([CC 4.5.13](part_4_composition_governance.md#4.5.13), the clock of a window).

A landing that states an outcome its own past does not give concludes nothing. An answer concurrent with a landing is **recounted**: it is counted with the landing's past, and the landing stands only if the table still gives the outcome it stated. A landing that does not stand says nothing against one that does. A landing with a strict majority behind it is final where no key has answered both ways.

One door runs every policy row and every clock that takes answers, and the policy table states its count, floor and length ([CC 4.5.13](part_4_composition_governance.md#4.5.13)). The door reads five more things, each stated in the text. They are who concludes and with which row, and whether a late answer counts. They are also whether the opening act is in force while its window is open, whether the joiner's own yes is a voice of the floor, and the threshold the room's founding row declares.

**Two notions of time.** There are two: a row's own stated end, read from the row against `now`, and a window with a landing. An invitation's expiry is a window that shuts out a late acceptance ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). A key is live while one of its own records covers `now` and it has not revoked itself, and no row of another key enters that reading. A row of an ended key that no live row has in its past lapses and counts in no answer. Its own verdict is unchanged, and a revocation never lapses.

### 2.7.6 `kernel-shapes` — Two mechanisms, four shapes

Every row family is one of four shapes: a **consent**, a **door**, a **claim** or **content**. A roster is a consent given by a count, and an acknowledgement is a claim. A family that takes no shape states why.

The four are labels over two mechanisms, consent and the door. Content is carried by consent: its audience is read off roster heads and the rows that name it, and its life is the **state** answer. A claim is carried by consent: what it means to a reader is the reader's own one-voice consents, walked from the reader's key. Nothing else reads `now`, so the door stays. Nothing else makes an offer stand, so consent stays.

### 2.7.7 `kernel-conflict` — Conflict between concurrent rows

Concurrent rows on one target are settled by five rules, and by no ranking of their signers.

1. **Different kinds on one target** are decided by a fixed order on kinds ([CC 3.5.1](part_3_the_namespace.md#3.5.1)).
2. **The same kind on one slot**: both count or neither does. No rule that cannot tell two rows apart can pick one.
3. **A row that names both** may decide between them.
4. **The cut.** A cut is a row on a slot by whoever may conclude it. Once it counts, rows on that slot concurrent with it do not count, rows in its past stand, and rows that name it are judged at the head they name ([CC 2.4.1.1](#2.4.1.1)).
5. **Equal standing.** Two cuts by keys of equal standing that undo each other stay contested. A voice that the other cannot remove settles them.

A row of a removed key counts when the removal has it among its ancestors: something the removal can see had already named it ([CC 3.3.4](part_3_the_namespace.md#3.3.4)). Among several duty holders, one holder's own conferral concludes only while it is the one duty holder ([CC 4.5.4](part_4_composition_governance.md#4.5.4)).

Three further rules hold. A cosignature is a voice only for a row counted over a head that the cosignature itself names. An offer conferred by a count is ended by its holder or by a count, never by its proposer alone. A counted row counts only if every counted row it is built on counts.

### 2.7.8 `kernel-roster` — The roster is the one ledger

A group's roster is a lineage. Each version names the heads it extends and is counted over their members. Every other row takes its place from the roster head it names, and nothing else is ordered ([CC 3.2](part_3_the_namespace.md#3.2) T6).

Two versions of one head wait as tips. The roster is then the members common to all tips, until a version naming the tips makes one head again. The members at a head are a function of the head, its signatures and its past. A removal is a later counted version and changes the members there, not at the old head. A member's own leaving binds the same way, by causal past ([CC 3.3.4](part_3_the_namespace.md#3.3.4)).

Where the count asks two or more, one key's rows remove nobody, and a removed key counts again only after a version lists it again ([CC 4.5.13](part_4_composition_governance.md#4.5.13), the floor of two voices). A reader that has acknowledged a head holds a line from below that head void, however many rows it has. That line is the reader's own and ranks nothing for anyone else ([CC 3.3.4](part_3_the_namespace.md#3.3.4)). Keys that met the count of an old head can sign a valid version alone; a witnessed lineage answers that ([CC 3.2](part_3_the_namespace.md#3.2) T6).

A person's keys, a voice's room keys, a room, the accord and an infrastructure community are this one roster, with parameters read from the policy table and the text. A public room's roster is public, so an audience is the members of a roster, everyone, or one named key ([CC 3.2](part_3_the_namespace.md#3.2)). It is read by asking a member's node, and every other roster is never enumerable outside its cohort.

**A writer's keys are a fold.** Who is entitled to a wrap of which key is a matter of seats and cuts. A rotation is due when a holder of the current key has lost its entitlement ([CC 4.4.3.4.1](part_4_composition_governance.md#4.4.3.4.1)). Each write and each mint names the head of the membership rows the writer held. The epoch is the count of the writer's mint rows, and the writer's state is a fold over its own rows.

**A private room seats voices.** In a private room the roster seats a **voice**, never an identity. A voice is a small counted roster of **room keys**, one for each device, made for that room only. That a voice is a given person's is the **binding**, which is never a row and is made for one addressee who cannot prove it to anyone else. No named answer reads a binding, and every named answer is the same over voices as over identity keys. A count of persons waits at a node for the bindings it lacks; a withheld binding is a stall, never a fork ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)).

### 2.7.9 `kernel-limits` — What the kernel does not give

- **No finality across readers.** Two nodes with the same rows conclude the same, and a settled slot can be reopened by a key with standing on it. Finality is each reader's, from what it has itself acknowledged.
- **No conclusion from silence without a clock.** A window closing unopposed, and the lapse of an unconfirmed halt, are read on the node's own clock. Nodes may differ while a window is open.
- **No decision that is not a function of rows.** Link and load decisions, retries, rendering and the prose rules given to a model stay outside the kernel.
- **No invariant of the form "at least one".** Two honest keys acting concurrently can leave none. For a community the way back is the lock and the members' count ([CC 4.5.4](part_4_composition_governance.md#4.5.4)).
- **No guard against a slot held on one signature.** A key of equal standing can undo such a slot, and the kernel does not check the tables for one.

An attacker keeps these, each bounded as stated:

- Keys that met a past count can fork on a past head. That unlists members and never lists one, and it moves only a reader with no acknowledgement of its own.
- A relay can choose the order of delivery and withhold a row until it is delivered. An emission made meanwhile cannot be unsent.
- A lone landing is never final against a key that can still sign, and the window's length is the concluder's own word.
- Whoever controls a new reader's first view can make a wrong head stick, until the reader withdraws its own rows.
- Whoever holds an ended key's private half can revive it, and only the key's own revocation makes its end final.
- One row of a seat that may confer can seat any number of keys, until one withdrawal by its conferrer.

A private room does not give deniability against a member who cooperates live with an outsider. A member's word is always possible; what is removed is the proof ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)).

The kernel does not settle these:

- a roster version that names several heads on the wire;
- how a second consent travels, and from when a delegation without one stops seating;
- the reach of a cosignature attached against a node's clock, unless it states its own end;
- a meaning for a clock that times a window from a signed instant and judges it at receipt. The freshness window `W` and `CLOCK_SKEW_VIOLATION` ([CC 2.6.7](#2.6.7)), the bound on a key that has lost standing ([CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3)) and the attach window ([CC 3.2](part_3_the_namespace.md#3.2) T4a) read one. So do a response bounded by `W` ([CC 4.3](part_4_composition_governance.md#4.3)) and an objection counted within `W` ([CC 4.5.13](part_4_composition_governance.md#4.5.13)). The kernel gives each no meaning beyond one node's own reading;
- `revoked_after`, which reads a revoked key's rows by their signed instants ([CC 2.4.1.1](#2.4.1.1), [CC 5.3.2.3](part_5_transport_substrate.md#5.3.2.3)). The kernel gives that reading no meaning beyond one node's own;
- the standing verdict of a trust root, which [CC 3.2](part_3_the_namespace.md#3.2) T6 to T8 index by a signed `effective_at`. The kernel gives it no meaning beyond one node's own reading;
- a meaning for a rule cell that keeps a word the operators do not carry, or calls a fold no cell defines;
- what a family confers where no sentence states it.
