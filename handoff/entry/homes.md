

<<<<< HOME ENTRY of rule `row_shape`: CC 2.1 in constitution/part_2_the_grammar.md >>>>>

## 2.1 `envelope` — The envelope

The envelope is where a claim becomes accountable. Every `scores` Attestation carries it. Each member binds the claim to evidence, names who may take it back, or records the conditions it was made under. This entry says what each member means, once, and the rest of the document refers back to it. A member's type, its place relative to the signed bytes and its presence rule are the table of [CC 2.6.1.7](#2.6.1.7).

The members fall into three groups: those every row carries, those any row may carry, and those one family requires. An optional member the producer leaves out is read as its default, and no party writes that default into the signed bytes ([CC 2.6.1.1](#2.6.1.1)).

**Every row carries**

| Member | Meaning |
|---|---|
| `attesting_key_id` | The attester's `federation_keys.key_id`. A substrate field. |
| `attested_key_id` | The subject's `federation_keys.key_id`. A substrate field. |
| `dimension` | REQUIRED. The canonical namespace prefix and scoped leaf. The substrate treats it as text; consumers parse it against the namespace map of [CC 3.1](part_3_the_namespace.md#3.1). |
| `score` | REQUIRED on `scores`. A scalar in [-1, +1]. The sign is polarity and the magnitude is strength. The per-dimension table of [CC 3.1](part_3_the_namespace.md#3.1) names each dimension's polarity: ±1 only, positive-only, or signed. |
| `confidence` | REQUIRED on `scores`. The attester's own confidence in the score, in [0, 1]. High magnitude with low confidence says "I believe this strongly but I might be wrong". Low magnitude with high confidence says "I am sure the truth is near neutral". |
| `cohort_scope` | REQUIRED, with no wire default. One of `self`, `family`, `community`, `affiliations`, `species`, `biosphere`, `federation`: the Scope axis of [CC 2.5](#2.5), a closed set of seven. It is the cohort tier the row is addressed to: who may see it, and the tier its holding claims stay within ([CC 5.2](part_5_transport_substrate.md#5.2)). The authoring default is the smallest scope ([CC 1.13.3.4](part_1_foundation.md#1.13.3.4)). |
| `subject_key_ids` | The consent-holder keys for this Contribution. Each entry MAY be a `federation_keys.key_id` or a canonical-hash identifier. Always present in the mirror, `[]` when empty; the column beside the row is absent when empty. An explicit `null` is refused ([CC 2.6.1.1.1](#2.6.1.1.1)). |

**Any row may carry**

| Member | Absent reads as | Meaning |
|---|---|---|
| `context` | nothing | Free-form scoping detail. Not parsed by the substrate; read by consumers, audit and RATCHET. |
| `evidence_refs` | nothing | URIs or content hashes pointing to backing evidence: a payment receipt, a licensing-body record, an observed interaction, a log entry, an audit-chain leaf. Optional in general; some dimensions in [CC 3.1](part_3_the_namespace.md#3.1) require it non-empty. |
| `valid_until` | nothing | A datetime in the [CC 2.6.2](#2.6.2) form. If set, consumer policy treats the attestation as stale after that point, independent of the row's own `expires_at`. |
| `epistemic_mode` | `direct` | The Epistemic-mode axis of [CC 2.5](#2.5): how the claim was formed. Consumers MAY weight by mode, a direct witness above hearsay. |
| `witness_relation` | `external` | `self`, `external` or `derived`: the attester's relation to the attested fact. `self` is the attested entity itself. `external` observed independently. `derived` inferred from other attestations or signed traces. Consumers weight by relation, so that self-attestation cannot game a verdict. |
| `oversight_mode` | `null`: consumer policy applies a per-cell default | `HITL`, `HOTL` or `HOOTL`: the human-control gradient under which the attestation was produced. |
| `occurrence_id` | `occurrence-0` | Which occurrence of a multi-occurrence agent deployment emitted the attestation: `occurrence-{n}` as the deployment assigns it, or `__shared__` for a shared-task emission. Self-asserted (below). |
| `occurrence_count` | `1` | Total occurrences in the deployment fleet, an integer at least 1. Self-asserted. |
| `occurrence_role` | `primary` | `primary`, `shared` or `replica`: the occurrence's role within the fleet. |
| `stake` | `reputational` | The Stake axis of [CC 2.5](#2.5). It composes with the attester's stake-backed-by attestations from [CC 3.1.1](part_3_the_namespace.md#3.1.1). |
| `community_id` | nothing | REQUIRED iff `cohort_scope` is `community` or `affiliations`; an affiliation is a community ([CC 4.4.3.2.8](part_4_composition_governance.md)). The `community_key_id` of the community this Contribution is scoped to ([CC 3.2](part_3_the_namespace.md#3.2) `community` subject_kind). One identity MAY belong to multiple communities, and this member says which community's roster gates visibility. A hierarchy edge resolves its `role_term` through it. The substrate rejects a community- or affiliation-scoped Contribution missing it. |
| `family_id` | nothing | REQUIRED iff `cohort_scope` is `family`. The `family_key_id` of the family this Contribution is scoped to ([CC 3.3.4](part_3_the_namespace.md#3.3.4) `family` subject_kind). One identity MAY belong to multiple families ([CC 4.4.3.4](part_4_composition_governance.md#4.4.3.4) Policy L), and this member says which family's DEK and roster apply. The substrate rejects a family-scoped Contribution missing it. |
| `delivery_mode` | `pull` | `pull` or `push`. On `pull`, subscribers discover holders through the holding claims at the content's scope (`custody:ack:v1` `here` rows, [CC 3.1.3.3](part_3_the_namespace.md#3.1.3.3)) and fetch with `ContentFetch` ([CC 5.3.2](part_5_transport_substrate.md#5.3.2)). On `push`, the substrate fans out to the live-delivery set, `fan_out = entitled ∩ reachable` ([CC 5.3.3.4](part_5_transport_substrate.md#5.3.3.4)), on direct links and never through a relay tree. One-to-many delivery to a large audience stays pull-only ([CC 5.3.3.5](part_5_transport_substrate.md#5.3.3.5) E2). |
| `history_on_join` | `from_join` | `full` or `from_join`. Per target, and reserved for membership. On a stream, `full` is the producer's signal that the stream is kept ([CC 5.1](part_5_transport_substrate.md#5.1)). |
| `additional_scrubs` | nothing | **Quorum on a row** ([CC 2.4](#2.4) cosigned rows): a list of hybrid signatures (Ed25519 + ML-DSA-65) over the same canonical bytes as the row's own. Each is `{scrub_key_id, scrub_signature_classical, scrub_signature_pqc, cosigned_at?}` ([CC 2.6.1.7](#2.6.1.7)). This is the quorum carrier. |

**Members one family requires or carries**

| Member | On | Meaning |
|---|---|---|
| `session_id` | `session:*`, REQUIRED | The exchange a `session:*` claim is about, verbatim and case-preserved. With `community_id` it is the claim's key ([CC 3.1.3.1](part_3_the_namespace.md)). |
| `claimed_at` | `session:*`, REQUIRED | When the claiming occurrence took the session, in the [CC 2.6.2](#2.6.2) canonical form. The convergent merge orders on it ([CC 3.1.3.1](part_3_the_namespace.md)). |
| `scope` | `consent:state:granted` and `delegates_to`, REQUIRED | What the row covers: a bare token or an array of tokens. On a `consent:state:granted` row it is **the grant's scope** ([CC 3.3.1](part_3_the_namespace.md)): `retain`, `share`, `analyze`, `train` or `publish`, sub-scoped in the token as `retain:90d`. A grant naming no scope matches nothing. On a `delegates_to` it is the delegated scope set ([CC 4.4.3.4.3](part_4_composition_governance.md)). It is inside the signed bytes like every member. A consumer that does not know the member preserves it per [CC 2.1.1](#2.1.1) and MUST NOT compose a `capacity:*` verdict that ignores it. |
| `custody_state` | `custody:ack`, REQUIRED | `here` or `none`: whether the reporting device holds the blob ([CC 3.1.3.3](part_3_the_namespace.md)). A signed `none` is a custody fact, not an absence. |
| `group_kind` | `membership:proposal`, REQUIRED | `family` or `community`: which kind of group the proposal's target names ([CC 3.1.3.2](part_3_the_namespace.md)). |
| `role` | `membership:proposal`, nullable; restated on `membership:acceptance` | The role the proposal offers the invitee. An acceptance restates it, and a widening that assigns a different role does not match ([CC 3.1.3.2](part_3_the_namespace.md)). |
| `expires_at` | `membership:proposal`, REQUIRED | The proposal's signed expiry in the [CC 2.6.2](#2.6.2) canonical form, after its `asserted_at` and at most 30 days later. The acceptance and the widening are each judged against it on their own signed instants, never a receiver's clock ([CC 3.1.3.2](part_3_the_namespace.md)). |
| `proposal_hash` | `membership:acceptance` and `membership:decline`, REQUIRED | The answered proposal's `original_content_hash`. With `references_attestation_id` it binds an answer to exactly one proposal ([CC 3.1.3.2](part_3_the_namespace.md)). |
| `subject_sha256_ed25519_raw` | a `moderation:*` score, optional | The subject key named by the SHA-256 of its raw 32-byte Ed25519 public key, 64 lowercase hex per [CC 2.6.3](#2.6.3), so the row does not carry the key's cleartext label ([CC 2.4.1.1](#2.4.1.1)). A malformed value is refused at admission. |
| `attached_head_digest` | `trust:accepts:v1`, REQUIRED | The SHA-256, lowercase hex per [CC 2.6.3](#2.6.3), of the lineage head the acceptance edge attaches on: the signed roster record at that version ([CC 3.2](part_3_the_namespace.md) T4a). It is checked at the edge's **first admission only**, against the head's witness cosignatures and the root's `attach_window_secs`, and never re-checked on a node's own restore. An edge whose digest is later un-headed by a lowered `revoked_after` is read as naming that head's nearest verifying ancestor (T8 viii). |
| `attach_window_secs` | `trust:charter:v1`, optional | Integer seconds. The oldest a lineage head's newest counted witness cosignature may be for a consumer to *attach* to this root ([CC 3.2](part_3_the_namespace.md) T4a). It MUST exceed `witness_cadence_secs` plus the [CC 2.6.7](#2.6.7) skew tolerance. A charter that declares none makes its root attachable only through an out-of-band anchor to a specific head (T5). Never a validity leg for an attached root (T4). |
| `witness_cadence_secs` | the `trust:charter:v1` of a witnessed lineage, REQUIRED | Integer seconds. How often each directory witness MUST re-cosign the current head, unchanged: the equivocation-exposure window ([CC 3.2](part_3_the_namespace.md) T6). |
| `witness_quorum` | the `trust:charter:v1` of a witnessed lineage, REQUIRED | Integer. The cosignatures from distinct independent witnesses a head needs to count as witnessed. It MUST equal ⌊\|`witnesses`\|/2⌋ + 1 and be at least 2, or be `0`: witnessed mode off, whether or not `witnesses[]` already lists keys ([CC 3.2](part_3_the_namespace.md) T6). Any other value is refused at admission. |
| `witnesses` | the `trust:charter:v1` of a witnessed lineage, REQUIRED | Array of `SignedKeyRecord`: the lineage's witness directory ([CC 3.2](part_3_the_namespace.md) T6). It sits inside the charter's scrub-signed bytes, and therefore inside the genesis bundle for the shipped roots ([CC 5.3.4](part_5_transport_substrate.md)). Each MUST have `identity_type ⊇ {witness}` and be independent of the lineage: not a founder, not a member seat, not owner- or steward-bound to a founder. A change is a charter re-scrub, witnessed by the directory before it. |
| `halt_fuse_secs` | the accord's `trust:charter:v1`, optional | Integer seconds. How long a `constitutional` halt signed by ONE holder stands before it lapses unless a strict majority of the standing roster confirms it ([CC 4.2.1.1](part_4_composition_governance.md)). **Absent means 86400.** The value is a constant of this document, read by the verifier, not a substrate-internal default. So a charter minted without the member is conformant and carries the 24-hour fuse. An explicit value overrides it, by re-scrub. |
| `recovery_commitments` | the accord's `trust:charter:v1`, REQUIRED ([CC 4.2.6](part_4_composition_governance.md)) | Object `{holder_key_id: commitment}`. Each commitment is lowercase-hex SHA-256 over the JCS array of the committed recovery key's `{key_id, pubkey_ed25519_base64, pubkey_ml_dsa_65_base64}` exactly as stored on its key record ([CC 3.2](part_3_the_namespace.md) T3), a one-element array here. It binds key material, never only the id. A holder rotates lost signing-key material by a self-`supersedes` under a key whose record hashes to its entry. |
| `consent_supersedes` | `consent:state:*`, optional | The prior consent-state row this one supersedes: a renewal, or the substrate's `consent:state:expired` naming the grant that lapsed ([CC 3.3.1](part_3_the_namespace.md)). |
| `deletion_window` | a consent grant, optional | The deadline by which a consented payload must be deleted once consent ends, carried on the grant ([CC 3.3.1](part_3_the_namespace.md)). Absent means the family's default. |
| `widened_at` | a widening `supersedes`, REQUIRED | The instant a widening took effect, RFC 3339 with milliseconds ([CC 2.6.7](#2.6.7)). It is the `scrub_timestamp` of the widening's signature ([CC 4.4.3.3.1](part_4_composition_governance.md)). |
| `accord_root` | `accord:*` rows, REQUIRED | The `key_id` of the accord an `accord:*` row belongs to ([CC 4.2](part_4_composition_governance.md)). |
| `consent_basis` | `capacity:*` and `observation:access_assumption:v1`, carried | The consent grants a witness relied on, as `[* {principal, paths, attestation_id}]`. For each principal: the paths by which its grant reached the subject (`subject`, `occurrence_of`, `delegates_to`) and the `attestation_id` of the `consent:state:granted` row. Validated at the family's gate. |
| `n_eff_pr` | `capacity:*`, carried | The effective sample size of the scoring window as a participation ratio of the feature covariance spectrum. The gate reads this one. |
| `n_eff_h` | `capacity:*`, carried | The same window's effective sample size as an entropy perplexity, `exp(−Σ p·ln p)` over the normalised spectrum. Carried for audit, not gated. |
| `sample_size`, `feature_dim` | `capacity:*`, carried | Rows in the scoring matrix, and features per row. |
| `sample_size_gate`, `target_n_eff`, `min_feature_dim`, `n_eff_floor` | `capacity:*`, carried | The configured gates: the minimum sample size the score was gated on, the target effective sample size, the minimum feature dimension, and the effective-sample-size floor below which no score is emitted. |
| `window` | `capacity:*` and `observation:access_assumption:v1`, carried | The scoring or observation window, in rows. |
| `trace_level` | `observation:access_assumption:v1`, REQUIRED | `generic`, `detailed` or `full_traces`: the trace level the observed agent's install emitted at. |
| `occurrence_key_ids` | `observation:access_assumption:v1`, REQUIRED | A set: the occurrences whose rows the witness read. |
| `window_from`, `window_to` | `observation:access_assumption:v1`, REQUIRED | Start and end of the observation window, each RFC 3339 with milliseconds ([CC 2.6.7](#2.6.7)). |
| `channel_classes` | `observation:access_assumption:v1`, REQUIRED | A set: the classes of channel through which the witness saw the subject, as the emitter names them. |
| `amendment_digest` | `identity_amendment:v1`, REQUIRED | SHA-256 of the identity amendment as applied ([CC 3.1.5](part_3_the_namespace.md#3.1.5)). |
| `authorized_by` | `identity_amendment:v1`, REQUIRED | The `attestation_id` of the `deferral:response:approved:v1` row that authorised the amendment. |

**Three axes that do not depend on each other.** `cohort_scope`, with `family_id` or `community_id`, is the visibility axis. `subject_key_ids` is the revocability axis. `delivery_mode` is the delivery axis. Each is orthogonal to the other two ([CC 2.3.3](#2.3.3)). `cohort_scope` is the one mirror member a placement-touching re-sign may narrow; it is never re-authored ([CC 2.6.1.7](#2.6.1.7)).

**The group id is read inside the group.** Community content is encrypted at rest under the per-community DEK. Its holding claims reach the community's members only, and the same holds at every bounded scope ([CC 5.2](part_5_transport_substrate.md#5.2)). So `family_id` is consulted in-substrate and never on the wire to non-members.

**A targeted row names its producer (normative).** A row placed at a targeted scope (`family`, `community`, `affiliations`) names its own producer in `attested_key_id` and the party it is about in `subject_key_ids`. A targeted row naming a third party in `attested_key_id` is refused at admission ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). For a `delegates_to` row `attested_key_id` is the delegate by the grammar's definition ([CC 2.4.1.2](#2.4.1.2)), and the producer rule is the `scores` row's.

**Whom a targeted row may name (normative).** At a targeted scope the keys a row lists in `subject_key_ids` are keys within the row's audience and no others. A key is within the audience in one of two ways. It is a member of the cohort by the authorized roster fold at the row's `asserted_at`. That is the fold every bounded-scope door uses, so a key removed before that instant is outside. Or it is the key the family delivers the row to. Today that is a membership proposal's invitee ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)), a key grant's recipient ([CC 3.3.2](part_3_the_namespace.md#3.3.2)) and the owner's own node on an owner-binding ([CC 3.2](part_3_the_namespace.md#3.2)). A further family reaches outside its cohort only where its registration says so. A subject named by canonical hash is reached through its rule-3 proxy ([CC 2.4.1.1](#2.4.1.1)), which must be within the audience. A row naming a key outside its audience is refused `subject_outside_audience`. A subject who can neither see nor contest a row has no standing to exercise, and [CC 3.4.5](part_3_the_namespace.md#3.4.5) promises the subject a read over the rows they are party to. Within the audience a row about another member is admissible. The named member's standing is that of `subject_key_ids` and [CC 4.5.5](part_4_composition_governance.md#4.5.5).

**What a subject key may do.** Each key listed in `subject_key_ids` has authority the substrate recognises to do two things. It may issue `withdraws` against this Contribution, under the rules and the kept list of [CC 2.4.1.1](#2.4.1.1). It may emit `consent:*` dimensions about this Contribution. An empty list means no subject authority: the producer alone has authority over the row.

**Cosignatures travel beside the row.** `additional_scrubs` is never inside the signed object, since a cosignature cannot be inside the bytes it signs. Each cosigner's role is read from the receiver's fold, not from the entry. The family declares which `consensus_protocol` the cosigners must satisfy. A cosigned row is retracted only by a cosigned `withdraws` ([CC 2.4.1.1](#2.4.1.1)). This is the general form of the ceremony plane's scrub set ([CC 3.2](part_3_the_namespace.md) T2).

**A change of oversight mode is the steward's act.** A mode shift is a stewardship act on the delegation plane, not a scored dimension. The human-control gradient an agent may operate under is bounded by the `agency:*` scopes its steward conferred ([CC 4.4.3.4.3](part_4_composition_governance.md)). So a shift is recorded as the steward issuing a **superseding `delegates_to`** ([CC 2.4.1](part_2_the_grammar.md)) carrying the new scope set. `supersedes` keeps the prior grant as forward-only history ([CC 4.5.9.3](part_4_composition_governance.md)). This is the same naming and superseding machinery that governs stewards and moderators ([CC 4.5.5](part_4_composition_governance.md)). A consumer MAY treat an `oversight_mode` inconsistent with the agent's live grant as it treats any self-claim exceeding its delegation. There is **no `accountability:*` family**. Accountability is structural (the audit chain), never a named axis, and an `accountability:*` dimension does not admit under [CC 3.1.7](part_3_the_namespace.md) R2.

**Occurrence members are self-asserted.** `occurrence_id` and `occurrence_count` are not cryptographically bound to a fleet-attestation primitive. An adversary running a single key can claim any `occurrence_id`. This limit of the design is acknowledged at [CC 8.3.1](part_8_appendices.md#8.3.1). Substrate self-report attestations SHOULD carry `occurrence_id`, `occurrence_count` and `occurrence_role`. A compliance reviewer can then reconstruct, after the fact, which occurrence agreed to which mandate.

**Delivery and history beyond the member.** `delivery_mode` composes with [CC 4.4.3.2](part_4_composition_governance.md#4.4.3.2) Policy M for community-scoped delivery, and with [CC 5.3.3](part_5_transport_substrate.md#5.3.3) streaming for `live_stream` chunk-DAG delivery. At `community` and `affiliations`, `history_on_join` is carried and does not change what a new member receives. The tier's rule fixes that: a community joiner receives the current epoch's key and no earlier epoch's ([CC 4.4.3.4.1](part_4_composition_governance.md#4.4.3.4.1)). What a kept stream's joiner can fetch is bounded by `min(operator depth cap, chunk-eviction horizon)` ([CC 5.1](part_5_transport_substrate.md#5.1) P4). An evicted-epoch grant returns `ContentMiss`, never a silent gap.

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


<<<<< HOME ENTRY of rule `withdraw`: CC 2.4.1.1 in constitution/part_2_the_grammar.md >>>>>

#### 2.4.1.1 `withdraws` — Who may take a row back

A `withdraws` row retires its target from the instant it is signed. It does not say the target was false. The rule below widens who may retract a row; the primitive itself does not change.

A node MUST admit a `withdraws` against a target row `T` when one line of this table holds. It MUST refuse any other with `federation_withdraws_not_admitted`.

| Rule | Who signs the withdrawal | Condition |
|---|---|---|
| 0 | the quorum of `T`'s family | `T` carries `additional_scrubs[]` ([CC 2.4](#2.4)). The withdrawal is cosigned under the same `consensus_protocol`, judged on the receiver's fold at the withdrawal's signed instant. Rules 1 to 4 do not reach `T`: a quorum's act is undone only by a quorum. |
| 1 | the key that signed `T` (`T.attesting_key_id`) | none |
| 2 | a key `T` names in `subject_key_ids` | `T`'s family is not on the kept list |
| 3 | a proxy for a party `T` names by canonical hash | the proxy holds a live `delegates_to` chain to that hash whose scope includes `consent_revocation`, and `T`'s family is not on the kept list |
| 4 | a delegate of anyone in rules 1 to 3 | the delegate holds a live `delegates_to` from them, and the kept list binds the delegate as it binds them |

**Any one named party is enough.** Where `T` names several parties, an admitted withdrawal from one retires `T` for all of them. A reader MUST NOT wait for a majority or for the others ([CC 4.4.3.5.4](part_4_composition_governance.md#4.4.3.5.4)).

**A withdrawal reaches forward only.** Acts taken while `T` stood still stand. One case reaches behind: a key revoked as compromised is void back to its `revoked_after` bound, stated below.

**The kept list (the anti-Goodhart retraction dual).** A named party acting under rules 2 to 4 MUST NOT withdraw these rows about itself:

- a `capacity:*` or `detection:*` finding made by someone else;
- a `licensure:*` or `revocation:*` row, where the licensee's path is `reconsideration:{grounds}`;
- a duty-holder's record on the accountability trail: a `moderation:*` report or action, a `hard_case:*`, a `slashing:*` verdict ([CC 4.5.5](part_4_composition_governance.md#4.5.5));
- an act of a body under a declared legal-weight class, such as a conviction or a licence ([CC 2.4.1.2.1](#2.4.1.2.1), [CC 4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8));
- a `takedown_notice:*`, where the path is the counter-notice its basis names ([CC 3.3.2](part_3_the_namespace.md#3.3.2)).

An affiliation withdraws no statement about itself, whatever the statement. Its path is reconsideration and the reader's composition. A named party contests a kept row by `reconsideration:{grounds}`, and it holds standing there ([CC 4.5.5](part_4_composition_governance.md)). The consent and scoring context of this list is [CC 3.4.5](part_3_the_namespace.md).

**Why the list exists.** Consent can be taken back, so a named party may retire a row about itself. A finding is not consent. A party that could retire the adverse rows about itself and keep the rest would launder its reputation.

**Between peers the person named retracts.** A `withdraws` of peer speech about oneself is admitted under rule 2. It is a signed act the row's audience sees, and it leaves the speaker attributed.

**Never withdrawn.** A `key:revocation:v1` row is withdrawn by nobody, because revocation is non-rollbackable ([CC 3.1.1](part_3_the_namespace.md)). An occurrence revocation, a key grant and a cosignature already sent are never withdrawn either ([CC 3.1.3](part_3_the_namespace.md#3.1.3)).

**The proxy of rule 3.** Rule 3 serves a party that holds no federation key: a platform user id, an entity bound by a content hash, any other outside party. A federation-key signer, typically the agent that holds data for that party, emits `delegates_to(canonical_hash → agent_key, scope: [consent_revocation])` when the proxy is set up. Its later `withdraws` against any row carrying that hash in `subject_key_ids` is admitted under rule 3. The hash is the tagged `canonical:{hashalg}:{hex}` wire form with the `{platform}:{entity_kind}:{id}` preimage convention of [CC 2.3.2.1](#2.3.2.1). A `canonical_binding` is a different act: a retroactive identity claim that promotes a canonical hash to a real `key_id`, which opens rule 2. It is not an admission rule ([CC 2.3.2.2](#2.3.2.2)).

**Only the signer recants.** A `recants` row says `T` was false, and only `T`'s signer may say so. A named party who holds the claim factually wrong answers with a `scores` row of negative polarity on a contradicting dimension. A named party's authority covers consent, which can be taken back. It does not cover truth.

**Which rule admitted it.** A substrate SHOULD record which rule (0 to 4) admitted each `withdraws` in `federation_attestations` metadata. A consumer can then compose policy on it, for example weighing a named party's own withdrawal above a proxy's.

**What the signer keeps (normative).** A named party's withdrawal takes the row out of every audience. It does not take the signer's words from the signer. The signer MAY keep the withdrawn row and its `withdraws` together at `cohort_scope` `self`. A node MUST NOT serve that copy to anyone, the row's former audience included, and the copy counts toward no score, standing or grant. The keep covers a signer's own words about another party, and it gives way to every duty to delete. A signer that committed to a deletion window deletes within it and keeps no copy ([CC 3.3.1](part_3_the_namespace.md#3.3.1), D1). An affiliation holds the row only as the retention and erasure limbs of its record allow ([CC 4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8)). A signer running a decay protocol on the named party's data follows its stages ([CC 4.4.3.5.1](part_4_composition_governance.md#4.4.3.5.1)). The signer MAY hand the pair to a party that holds a duty to judge it: filed with a room's named moderator it is a duty-holder's record ([CC 4.5.5](part_4_composition_governance.md#4.5.5)), and given to a body acting under a declared legal-weight class it is evidence before that body ([CC 4.4.3.2.8](part_4_composition_governance.md#4.4.3.2.8)). Saying the same thing again to the audience is a new row, and the party it names may withdraw that one in turn. Shown to its former audience beside the retraction, the row would be read by everyone who read it before, and the retraction would be a label. Deleted from its signer as well, the retraction would take the signer's own words. The retention rule carries this copy as a declared gate ([CC 6.1.5](part_6_the_coherence_mathematics.md#6.1.5) N5).

**`revoked_after` — the revocation history bound (normative, optional member).** A key-plane revocation MAY declare `revoked_after: rfc3339` — a bound before which statements signed by the revoked key **still stand**: everything after the bound is suspect; everything before it is not unmade. Resolution is a **pure read-time function**: a claim signed by K is valid iff its `asserted_at` precedes `K.revoked_after`, so a partitioned node converges when the revocation arrives late — the same fold shape as consent. Absent member = revoke-all. **`revoked_after` is an upper bound, not a fact** — a compromise may long predate its detection: a later revocation MAY lower it and MUST NOT raise it, and where a key carries multiple revocations the effective bound is the **minimum** `revoked_after` across all of them, absent-member sorting as negative infinity — keeping the fold commutative and the resolution a pure read-time function, so partitioned convergence is preserved.

**A key revocation names its subject by the key's digest, not its `key_id` (normative).** A `key_id` is `<label>-<fingerprint>`, and the label is the holder's own keystore alias in cleartext. Revocations replicate federation-wide, so a revocation addressed by `key_id` would tell every node the subject's label — `frank-laptop` — whether or not that node held the key's record. The revocation is a `key:revocation:v1` row ([CC 3.1.3](part_3_the_namespace.md)), never withdrawn. The subject is therefore **`revoked_key_sha256_ed25519_raw`**: the SHA-256 of the revoked key's raw 32-byte Ed25519 public key, 64 lowercase hex digits ([CC 2.6.3](#2.6.3)) — the full digest whose truncation is the `key_id`'s fingerprint, stable for the life of the key and carrying no label. The member is REQUIRED. `revoked_key_id` is OPTIONAL: when present it MUST name a key whose raw-key digest equals the subject, a mismatch is refused, and a receiver that does not hold the named key cannot compare the two and refuses the row *retryable*; when absent it is bound as explicit JSON `null`. The signed revocation binds **eight** members inside its own `revocation_envelope` — `revocation_id`, `revoked_key_id` (string or `null`), `revoked_key_sha256_ed25519_raw`, `revoking_key_id`, `reason` (string or `null`), `revoked_at`, `effective_at`, `scrub_timestamp` — every one REQUIRED in the bytes, an absent optional bound as explicit `null` (an omitted member is refused as unbound); `revoked_after` is the ninth, optional, absent or `null` meaning unbounded. This is the key plane's own signing contract: `scrub_timestamp` is inside the bytes because it is the anti-rollback ordering key, and the explicit `null` is the one exception to the no-null rule of [CC 2.6.1.1.1](#2.6.1.1.1), which governs the attestation envelope. Three consequences follow. **(1) A revocation may precede the record it revokes**: one naming only the digest MAY be admitted for a key the receiver does not hold, and takes effect the moment a key with that digest is held; authority on this plane is the revoker's and is judged without the subject's record. **(2) Readers ask by digest**: "is key K revoked?" is answered over K's digest, so one revocation reaches every `key_id` that names the same public key, and the per-subject anti-rollback ordering ([CC 5.3.2.3](part_5_transport_substrate.md)) keys on the digest. **(3) Self-revocation** is recognised when the revoker's own key digests to the subject, whether or not `revoked_key_id` is present. A `moderation:*` score MAY likewise name its subject key by **`subject_sha256_ed25519_raw`** (same spelling; a malformed value is refused) instead of exposing its label. Family and community rosters list members by `key_id`, so a roster's holders see the labels, and roster-removal rows are addressed by `key_id` — they reach only the audience that already holds the roster. The revocation's signed object is this contract; it carries no member table in [CC 2.6.1.7](#2.6.1.7), and its signature rule is the key record's.

**A purge is a tombstone, not a `withdraws` (normative).** Rules 0–4 are consent paths — the author's or the subject's. A row the purger neither authored nor is the subject of (a mock-LLM trace, a harness identity's rows, a row no peer can verify) is removed by a **tombstone by digest on its plane**, authorised by a cosigned `takedown_notice` under the trust root's `consensus_protocol` with basis `steward_purge` ([CC 3.3.2](part_3_the_namespace.md)) naming the selection digest, the reason and the ledger; a substrate MUST NOT admit a `withdraws` forged on the author's behalf for this — a `withdraws` does not even claim falsity, and a purge says the row never belonged. **A purge never tombstones or deletes a key:** a selection naming a `federation_keys` row is refused, a by-actor selection takes the actor's own rows and their derived rows, and key retirement is a separate `key:revocation:v1` signed under this section's own paths — the root's quorum has no path over a key it does not own (a root that could revoke strangers' keys would be an authority roster by another name, [CC 3.4.7](part_3_the_namespace.md)), so an ownerless key stays registered and inert while its rows go, and the admission gates stop its next ones. Entities go by `revocation:{entity_type}:{reason}`, bytes by the bytes-plane tombstone ([CC 4.5.3](part_4_composition_governance.md)). **The accountability record is outside the root's reach:** `revocation:*`, `key:revocation:v1`, `moderation:*`, `moderation_track_record:*`, `slashing:*` and **`hard_case:*`** rows are never purgeable, by the root or by anyone — trust-root moderation is not trust-root history-editing; `hard_case:*` is in the set because an equivocation proof (`hard_case:lineage_equivocation`, [CC 6.1.1](part_6_the_coherence_mathematics.md) N4) or a liveness transition (`community_liveness_stalled` / `_restored`, [CC 3.2](part_3_the_namespace.md) T7) is an adverse row about a root whose only purge door is that root's own quorum — the subject — and the anti-Goodhart dual admits no subject-side removal of an adverse row; the substrate that produced the proof withdraws it under rule 1, or recants a false one, and nobody else; a structural composer (`withdraws`, `recants`, `supersedes`) is purged only together with its target, and a `delegates_to` only when a party to it is in the selection — a purge removes a party, never a third party's standing. **Derived rows follow the reason, and the selection digest says which:** a `scores` row whose evidence was never admissible input (mock, harness, unverifiable) is purged with its evidence, in the same selection and ledger — its subject never ran, so it attests nothing — and so are a trace's own `trace:complete:v1` attestation and the bytes a purged holding claim holds, transitively over `evidence_refs`; a score over real evidence later taken down on a legal basis stands, its `evidence_refs` resolving to the tombstone. The door refuses a purge without the notice (`purge_unauthorised`) and one whose selection digest differs from the authorised one (`purge_selection_digest_mismatch`); every purged id is appended to a ledger attested at the next tag.


<<<<< HOME ENTRY of rule `owner_binding`: CC 3.2 in constitution/part_3_the_namespace.md >>>>>

##### Who owns a key (normative)

A device cannot accept anything for itself, and neither can an `agent`-role identity. So every `node` key and every `agent` key is held by one person who answers for it: its **owner**, also called its **steward**. The owner says so in one signed row, the **owner-binding**. A key with exactly one is **steward-bound**. This entry is the whole rule for that row.

| Question | Answer |
|---|---|
| What the row is | a `delegates_to(owner → K)` carrying `delegation_purpose: "owner_binding"` ([CC 2.4.1.2](part_2_the_grammar.md)); no new primitive |
| Which keys need one | every key whose `identity_type` ([CC 3.4.7.1](part_3_the_namespace.md)) includes `node` or `agent` |
| Who signs it | the owner: `attesting_key_id` is the owner's key, and the signature is the claim of ownership. Any live key of the owner's roster signs as the owner ([CC 3.3.6.3](#3.3.6.3)) |
| Who may be an owner | a `federation_keys` identity with `user` in its `identity_type` that is not itself steward-bound |
| How many | at most one live owner-binding on a key at any time |
| Where it sits | `cohort_scope: self`; the owner may re-sign it at a wider scope |
| How long it lasts | it SHOULD carry `delegation_valid_until` ([CC 2.4.1.2](part_2_the_grammar.md)), so it can lapse |

**Three readings of the row.** Every rule that asks about ownership asks one of these, and nothing else answers them.

| Reading | Value |
|---|---|
| `owner_of(K)` | the owner named by the live owner-bindings of `K`. It resolves to at most one key, never to a set to be reduced |
| `is_steward_bound(K)` | true iff exactly one live owner-binding on `K` exists, from a `user`-role identity that is not itself steward-bound |
| `accountable_root(K)` | true iff `K` is a `user`-role key of an adult ([CC 3.3.12](part_3_the_namespace.md) I1 band) not itself steward-bound, or `is_steward_bound(K)` |

Nothing else binds a key: not an `identity_occurrence` ([CC 3.3.6](#3.3.6)), which places a key under an identity and binds nothing by itself; not a `delegates_to` of any other purpose; not `K` being a `user` key itself. A steward-bound key ends at an accountable human. A `node` or `agent` key with no owner-binding, or with more than one, is steward-less. An accountable adult ends every ownership chain and is the accountable root of what they found or appoint. The [CC 4.5.5](part_4_composition_governance.md) clause-(b) check, and its moderator-appointment and delegation predicates, name these readings.

**One owner at a time: the single-owner invariant (MUST).** Steward-binding answers "is this key accountable to a human?". Ownership answers "to which one?", and it has one answer. While a live owner-binding exists on a key, a node MUST refuse at bind time a second one naming a different owner. The incumbent first signs a `withdraws` or a `recants` under [CC 2.4.1.1](part_2_the_grammar.md), or its binding lapses. Ownership therefore moves by withdraw-then-rebind or supersede-then-rebind, never by adding an owner. A second distinct claimant is refused, not merged, as at a founder's first-run claim. The refusal happens when the binding is admitted; it is not left to the reader. Only the owner-binding purpose is single-valued. Act-on-behalf and hierarchy delegations stay multi-parent ([CC 4.5.13](part_4_composition_governance.md)) and this rule does not gate them.

**How ownership is read (MUST).** Ownership MUST be resolved by `owner_of`, which reads owner-bindings and nothing else. A reader that returns every live `delegates_to(user → K)` whatever its purpose MUST NOT be used to resolve ownership. It would count act-on-behalf and hierarchy edges as owners.

| Live owners of `K` | What a reader does |
|---|---|
| none | `K` has no owner, is steward-less, and has an empty `self` cohort: its `self` content goes nowhere beyond the key itself |
| one | that key is the owner |
| two or more | the `self` boundary is undefined. `K` MUST NOT be treated as owned by any of them: a hard error, with no widening of `self` |

A consumer that widens `self` to a person's several devices through `owner_of` MUST treat any count other than one as an error and fail closed. It MUST NOT pick one owner from a sorted set. An adversary who landed a second binding whose `key_id` sorts first would then become the owner. The base resolution of [CC 5.2](part_5_transport_substrate.md), the occurrences of one `attesting_key_id`, is single-key and needs no such care.

**`self` is one owner's keys.** The `self` cohort is the set of nodes sharing one owner: a person's own devices, distinct keys joined by their owner-bindings. For `self` content an outsider is exactly a node not owner-bound to my owner ([CC 1.13.3.4](part_1_foundation.md), [CC 5.2](part_5_transport_substrate.md)). An `identity_occurrence` of an owned key inherits its key's owner. So the occurrence set of CC 5.2 is a subset of the owner's cohort. The owner-binding widens that set to the person's distinct device keys. It does not replace it, and the two never disagree on who is in.

**Where the row is placed.** An owner-binding is written at `cohort_scope: self`. The owner MAY later re-sign it at `federation`, which is announcing the node ([CC 5.4.6](part_5_transport_substrate.md)). When an unannounced node joins a group, the owner re-signs the binding at that group's scope, so the group's members can see who owns the node. That scope is `family`, `community`, `affiliations`, or a wider cohort the owner belongs to. The re-signed row is a second owner-signed row beside the `self` one, never a replacement, and the audience rule of its tier places it. Every one of the seven scopes is an admissible audience for an owner-binding, and a node refuses none of them. `owner_of` folds every live binding of the key, so ownership never depends on announcement or on any re-signing. An announcement at `federation` makes the group-scoped rows redundant in reach and leaves them standing.

**The first binding (MUST).** An owner's signature alone does not prove authority over the node. So the first owner-binding of a node is set at provisioning: it is cosigned by the node's own key, or carried in the node's genesis record. Provisioning custody decides it, never who reaches a node first and never a `key_id` sort. A node with no first owner is unowned, with an empty `self`. It is not open to the first claimant: a remote party cannot sign a binding onto an unclaimed node's `key_id` ahead of its owner. A person's next device takes its first binding by **Adding a device**, below.

**What the binding opens: the steward-binding gate.** A `node` or `agent` key MUST be steward-bound before it is admitted to any community that is not `infrastructure`: a `family`, a `community` or an organisation. A node evaluating such an admission MUST reject a `node`-role or `agent`-role member that lacks a live owner-binding. With no owner, a key MAY trust and serve `infrastructure` communities and does nothing more. Membership outside `infrastructure` is an authority act, standing to speak in the group. Authority MUST root in an accountable human, never in a bare node ([CC 1.13.2](part_1_foundation.md), [CC 3.4.7.1](part_3_the_namespace.md)). The ground of the gate is custody, not substrate; `identity_type` is how the wire reads that fact. The binding is a precondition and not the vote. The admitting community's `consensus_protocol` still decides whether the owned key is admitted.

**Conferral is not stewardship.** Stewardship is a custody relation over a key that cannot accept for itself. A capability conferral is a grant the receiving side must accept (T3 below): a person for themselves and for the keys they own. No ceremony substitutes for that acceptance. An act the receiving side must accept cannot be custody of the target. So `is_steward_bound`, its admission gate and the `steward_bindings_of` fold read owner-bindings alone. They never read conferrals, occurrences or any other edge. Four consequences follow, paired so the gate and the fold never disagree.

- A quorum MAY confer a duty scope ([CC 4.5.5](part_4_composition_governance.md) `moderate` / `takedown` / `review` / `slash`) or any delegation-plane capability on an adult `user`-role key, and the write gate MUST NOT refuse it as a stewardship act.
- Steward-binding an adult remains forbidden, except under adjudicated incapacity ([CC 3.4.12](part_3_the_namespace.md), the presumption of sovereignty).
- Registering a person as `agent` or `accord_holder` to route a duty past the gate is a misclassification, and this rule makes it unnecessary.
- The steward gate is not an age gate for conferrals. A duty scope that needs an age or assurance floor MUST declare it on its own [CC 4.5.5](part_4_composition_governance.md) row, per the [CC 3.4.11](part_3_the_namespace.md) ladders, and never inherits it from a custody rule.

The same reading, and nothing else, is reused where a person cannot accept for themselves: an adult under adjudicated incapacity ([CC 3.4.12](part_3_the_namespace.md)) and a minor under guardianship ([CC 3.4.13](part_3_the_namespace.md)). The relations are not alike, and this document draws no analogy between an agent and a child ([CC 1.13.2](part_1_foundation.md)).

**An organisation's agent.** Where a steward holds an `agent` key on behalf of an organisation, the owner-binding names the organisation's affiliation in its `community_id` ([CC 2.1](part_2_the_grammar.md)). It is cosigned under that affiliation's protocol ([CC 2.4](part_2_the_grammar.md)), the same shape as a licence under [CC 2.4.1.2.1](part_2_the_grammar.md). The affiliation then answers alongside the steward. `slash` and `quarantine` ([CC 3.1.9.2](#3.1.9.2)) reach the affiliation's keys as well as the steward's, and the record names the deploying organisation first. A steward who is the organisation's employee signs as the accountable human the gate requires. The organisation does not escape by naming one. Without a `community_id` the binding is a personal steward's.

**The recovery path: an owner who is gone, or one who should not be there (MUST).** No key is locked ownerless forever. Being ownerless is fail-secure, with no `self`-scope delivery, and it is never permanent. A live owner-binding is taken away from outside the owner's hand on one of two findings, each made by a Wise-Authority quorum ([CC 4.3](part_4_composition_governance.md)).

| Finding | What it finds |
|---|---|
| abandonment | the owner is provably gone: an owner key lost and unable to sign a `withdraws`, shown by sustained non-response and out-of-band confirmation |
| seizure | a live wrongful owner-binding, admitted by front-run or fraud |

A front-run that installs a live adversarial owner is therefore reversible. A partition merge that admits two owners is repaired to one by the same authority. A binding that is merely quiet is not withdrawn as dead: the liveness predicate is pinned per deployment.

*Who signs the withdrawal.* [CC 2.4.1.1](part_2_the_grammar.md) admits no stranger's `withdraws` against a live binding, and recovery adds no primitive. The owner-binding names `K` in its `subject_key_ids`, so `K` itself may sign under rule 2. A recovery authority `R` holding `delegates_to(K → R, scope: [owner_binding_recovery])` may sign under rule 4. The key that is still being kept running is the subject with standing to say its owner is gone.

*The recovery gate.* A node MUST reject a rule-2 or rule-4 `withdraws` against a live owner-binding unless it carries a `wa_adjudication_ref`. The reference names a quorum finding of abandonment or seizure against that binding. Without this gate a compromised node key withdraws its own owner, and the single-owner invariant is worth nothing. The node records the finding; it never makes it.

*What abandonment rests on.* The measure is a signed freshness floor: the owner's most recent owner-signed attestation, carried as `fresh_as_of`. The owner-binding itself sets the first floor, so no binding is floorless. Abandonment needs that floor to have stood still for longer than the deployment's `owner_abandonment_window`, and the out-of-band confirmation above. The window's floor is **90 days**. A deployment MUST publish its window; where none is published, no abandonment finding is admissible.

*The four steps.* They MUST NOT be collapsed.

1. A petition, `wa_adjudication:petition:v1` under the petitioner's key, naming `K` and the evidence.
2. The quorum finding, minted as the attestation the `wa_adjudication_ref` resolves to.
3. The gated `withdraws`, after which `K` is unowned: an empty `self` cohort and no `self`-scope delivery.
4. A fresh owner-binding under the first-binding rule above, cosigned by `K`.

Reclaim MUST NOT move a key from incumbent to claimant in one act. Passing through the unowned state is what keeps the single-owner invariant, and keeps an unclaimed node closed to the first claimant.

**Adding a device.** The genesis binding of a person's *next* node is set by the owner's own pen on a node they already own — while the self's roster holds one key; with two or more keys a new `user`-role key lands by the self-roster door ([CC 3.3.6.3](#3.3.6.3): a strict majority of the live roster, the proposer included, or the lone path after its window with no objection) — peer to peer, with no canonical store. **(a)** An unowned node may originate exactly one kind of message: a **device-join request** on the pairing plane: an opaque request of kind `0x0000_0002` that carries exactly two fields, `key_record` (the sender's own key record, self-signed: scrub key, `key_id` and signing key are one key) and `challenge` (32 fresh random bytes, present exactly when `key_record` is), signed by its node key, with the public halves of its occurrence keys in the record; no attestation, no route and no third party's record. The receiver checks, in this order and before any cryptography: a per-sender-key rate, a per-link rate, then a node-wide ceiling on pending requests; only then does it verify the record and the signature. A known key takes the ordinary path and its record is ignored; an unknown key without a record is dropped; it serves and asserts nothing else until bound. The request moves no trust state and confers nothing, so T8 (i) is untouched, and the receiving node holds it only while its owner has opened "add a device" for a bounded window. **(b)** The owner's one approval signs **two rows, each standing alone**: the owner-binding `delegates_to(owner → new node, infra:*)` of this section and the new node's device occurrence under the owner's self ([CC 3.3.6](#3.3.6)); the binding is admitted first and the occurrence second, and the new node applies the binding through its own setup door before it links. **(c)** The availability residual is accepted and bounded: the receiving node holds at most a fixed number of pending join requests and one per sender key, so a flooder who refills free keys can keep the receiving node's ceiling full and delay a join; that is availability, not safety, and is met by the owner-opened window, fair eviction and the joiner's retry — never by a proof-of-work stamp, which would price joining against the preamble's precondition that joining costs nothing. **(d)** The **matching code** the owner compares MUST be derived by the owner's own node from the request (requester key and challenge) and MUST NOT be supplied by the requester; the derivation is the implementer's. **(e) Under the per-link hybrid seal ([CC 5.3.3.5](part_5_transport_substrate.md) E1), the joining device is unowned but never anonymous.** The seal admits an initiator with no owner-binding on the pairing plane only, and binds the initiator's **self-signed node key** into the handshake: the key that opened the sealed link, the key that signed the device-join request and the key the matching code is derived from MUST be one key, the responder is the owner's announced node authenticated by its published transit pair, and a link opened this way carries the pairing plane and nothing else. Proof of possession verifies the key's `key_id` fingerprint against its public key ([CC 2.6.8](part_2_the_grammar.md)), so a self-signed record cannot claim another key's id. Together these close on-path substitution: what the person types into the new device and the device's fresh keys cross under post-quantum confidentiality, the device they approve is provably the device that asked, the first device still tells a stranger nothing before approval, and nobody can dial an unowned node. A fresh device roots the canonical nodes' transit pairs from the genesis bundle ([CC 5.3.4](part_5_transport_substrate.md), `serve_transport_destinations`), seals to one, and replicates the owner node's announced binding before it dials the owner node. **(f) Offline or LAN-only pairing:** where no canonical node is reachable, the owner's device-join pairing payload (the [CC 2.6.8](part_2_the_grammar.md) contact code or its QR form) carries the owner node's transit pair; the new device pins it **for that one pairing link only**, never stores it as Rooted, and every key-bound rule of (e) applies unchanged.


<<<<< HOME ENTRY of rule `trust_fold`: CC 4.4.3.8 in constitution/part_4_composition_governance.md >>>>>

#### 4.4.3.8 `policy-direct` — Policy A — direct trust

A reader trusts a signed statement when the key that signed it (`attesting_key_id`) is in the reader's pinned trust set. This is the cheapest policy, with the lowest latency and the narrowest reach.

**The pinned trust set is a graph, and its roots are pluggable (normative).** The set is the reader's own rows and nothing else. It has a base, and the entries the reader hangs off the base.

| Part of the set | The row | Rule |
|---|---|---|
| The base | `attestation(user → user)` with no modifiers, written at first run | The user is their own root: "I trust my own attestations and service". This is the immutable identity floor. A node inherits it by the owner-binding `delegates_to(user → node)` ([CC 3.2](part_3_the_namespace.md)), an agent by the partnership object ([CC 4.4.3.4.3](#4.4.3.4.3)). |
| An entry | an acceptance edge `delegates_to(reader → authority)` bearing `trust:accepts:v1` ([CC 3.2](part_3_the_namespace.md) T3) | The reader signs it, and adds and removes it freely. The base is untouched. The reader is a person, signing with any live key of their roster, and every node and agent that person owns reads the entry ([CC 3.2](part_3_the_namespace.md) T3). |
| What an entry trusts the authority for | the edge's `trust_classes` | **As a licensor**: every class the authority's charter declares ([CC 2.4.1.2.1](part_2_the_grammar.md#2.4.1.2.1)). Or **for a class of licence**, such as medical, legal or financial: the classes listed on the edge, and no other. |
| How far an entry reaches | the edge's `trust_depth` | `0` honours that authority's own licences. `n` honours the licensors that authority itself trusts for the class, to `n` further hops (licensors of licensors), within the cap of five hops ([CC 4.1.1](#4.1.1)). |

**The shipped root is one entry.** It is written at first run and is removable like any other. The recommended default is Policy A with `pinned_trust = {community_key_id: ciris-canonical, family: humanity-accord}`. That names the founders of `ciris-canonical`, who are the three accord holders `A1`, `B1`, `C1` ([CC 3.2](part_3_the_namespace.md)). They are resolved live, and the default never pins a serving install's key. This is the shipped default root, never *the* root.

**A root is a charter that delegates to itself.** The row is `delegates_to(root → root, scopes)`, and rooting to itself is rootness. Grants down the chain are attenuation-bound: a grant resolves only where every edge on the chain bears the scope, and nothing amplifies. The self-declaration is therefore the charter: the capability ceiling of the whole trust domain. It is held in signed bytes and re-resolved by a live walk of the graph, so an amendment re-scopes existing grants with no re-issuance. The root validity minimum is `[infra:serve, infra:attest]`: a root serves and vouches, or it is inert. The humanity accord's charter is `[infra:attest, infra:serve, infra:store, infra:transport]`.

**Validity flows from a shared root.** Two nodes under one shared root cross-attest and vouch. Two nodes with no shared root compose nothing. The sanctioned bootstrap and re-root artifact is a **portable trust root**: a charter plus at least one blessed `infra:serve` node. It is minted by the [CC 4.2.1](#4.2.1) conferral ceremony and owes nothing to any prior root.

**The walk.** The walk is breadth-first from the reader's own edges. An onward hop counts only from the authority's own acceptance edges, signed by its authority set. At each hop the remaining depth is the lesser of what is left and the edge's own. The classes are the intersection, so the walk only ever narrows. Cycles are visited once, and the cap holds whatever a licensor carries. Nothing is cached.

**The charter is read at read.** A class the charter does not declare is not a refusal. It is a licence that does not match. A class a later amendment drops stops matching, and the edge stands.

**Honouring a licence.** The reader honours a `licensure:{authority_id}:v1` row iff two things hold. Its own walk from its own edges reaches the issuing authority for the row's class, and that authority's charter declares the class. A licence confers no trust: holding one from an authority makes nobody a trusted licensor. A licence that fails the walk is read, not refused: `licence_issuer_not_trusted` or `licence_class_not_trusted`.

**Removing an entry.** A removal removes exactly what reached through the edge. Deleting the reader's edge to a root is the un-trust lever of [CC 3.2](part_3_the_namespace.md) T3. It revokes at once, for this reader and on every node and agent the reader owns, that root's conferred roles, score validity and vouching, **and its kill-switch authority** ([CC 4.2.1](#4.2.1)). The base survives, so the installation keeps running un-federated, and attaching a new root resumes federation. Un-trust is the exit that makes the halt consensual.

**Composing what is trusted.** The reader aggregates per (`dimension`, `attested_key_id`) tuple, over trusted attesters, by the polarity defaults of [CC 4.4.2](#4.4.2). The reader's threshold determines the verdict.

**On the wire.** The entry's two choices are two members inside the reader's own signature on the edge. `trust_classes` absent means every class the charter declares. Present, it is a non-empty, sorted, deduplicated list of class ids, and an empty list is refused. `trust_depth` is `0..5`. Absent reads as `0`, so an edge without it keeps its meaning, and above `5` is refused. Admission refuses shape only (`trust_accepts_classes_malformed`, `trust_accepts_depth_out_of_range`). Both members ride the existing `delegates_to` edge as signed envelope-extra members, like `delegation_valid_until`.

**1+4 preserved.** Every element here composes the existing `attestation` and `delegates_to` primitives. There is no new structural primitive and no bespoke "trust" attestation kind. The model that proves the rules of this entry is the trust-set model, pinned by the register.

**Cold-start bootstrap.** A new consumer fetches `GET /v1/trust-root/bundle` ([CC 5.3.4](part_5_transport_substrate.md)), re-derives the bundle's quorum from the holder records it carries against out-of-band pins (the published holder fingerprints, or a build-baked copy of the bundle), holds a witnessed lineage head inside the root's `attach_window` ([CC 3.2](part_3_the_namespace.md) T4a; served beside the bundle per [CC 5.3.4](part_5_transport_substrate.md)), and persists the anchors locally; `GET /v1/accord-holders` is a projection it cross-checks, not a second root.

**Capability gate — the federation floor (fail-closed).** With no valid *external* trust root, federated agent capabilities and manifest validation MUST be disabled at the server tier. The base self-root is the floor, never sufficient for federation: it constitutes an identity, and identity is not standing ([CC 4.1.2](#4.1.2)).

**Two conferral planes.** **Ceremony** confers root *identity* (an m-of-n co-scrub on the key record, [CC 4.2.1](#4.2.1)); **delegation** confers operational *capability* (`delegates_to(root → key, [scope])`, resolved at use against a root the asking node trusts). Every reserved-prefix role — `trusted_publisher` reserving `content_rating:*` ([CC 4.4.3.10](#4.4.3.10)), `lenscore_detector` reserving `detection:*` — is conferred on the **delegation** plane. Putting a routine operator role on the ceremony plane fails closed on every legitimate operator and leaves each newly-minted root *less* able to stand up its own; leaving a reserved-prefix role with **no** named plane leaves it self-assertable, which is the hole this rule closes.

**Charter recovery lives in the record.** A charter MUST carry a pre-rotation commitment (the successor key committed in advance) and an m-of-n recovery ceremony, and the m-of-n MUST be audited for holder **independence** — an m-of-n assembled inside one organisation is a 1-of-1. Absent both, root-key compromise is unrecoverable by construction: the attacker holds the tombstoning pen.

**Genesis is tamper-evident, not self-verifying.** A portable-root bundle verifies internally — and so does an attacker's identical-shaped bundle. The trust-on-first-use moment therefore sits in the distribution channel, so out-of-band fingerprint comparison is a **first-class attach step**, not an optional hardening.


<<<<< HOME ENTRY of rule `audience`: CC 5.2 in constitution/part_5_transport_substrate.md >>>>>

## 5.2 `family` — Structural invisibility — no holding claim leaves a bounded cohort

Every row has an **audience**: the nodes it may reach. A row is served to a node in its audience and to no other, and a node holds a row only when it is in that audience. This is one rule at every tier, and only the roster changes size: `self` and `family` are not a special case but the audience rule applied to the smallest rosters.

| `cohort_scope` of the row | Its audience | What a node outside the audience learns |
|---|---|---|
| `self` | the owner's own nodes | nothing, not even that the content exists |
| `family` | the nodes of the family's current members | nothing, not even that the content exists |
| `community`, `affiliations` | the claimed nodes of the roster's members | nothing of the content, of the roster or of who holds it |
| `community`, in a public room ([CC 3.2](part_3_the_namespace.md#3.2)) | the claimed nodes of the roster's members | the listing, the holding claims and, by asking a member's node, the content; never the roster |
| `species`, `biosphere`, `federation` (the Commons) | every node | everything: the holding claims here are the holder directory ([CC 3.1.3.3](part_3_the_namespace.md)) |

Within every cohort, holding claims, custody reports, target replication and anti-entropy run exactly as at every other tier ([CC 6.1.5.3](part_6_the_coherence_mathematics.md)). Carrying a sealed frame for someone else is not being in its audience; who may carry is the rule of [CC 5.4.6](#5.4.6).

**Which of a member's nodes.** A node is in a cohort's audience only through its owner's membership, and the owner chooses per node which of their cohorts it serves ([CC 6.1.5.3](part_6_the_coherence_mathematics.md)). A node with no owner is in no cohort's audience.

**A row about a party reaches that party.** A row that names a node, or a grant issued for it, is always served to that node ([CC 6.1.5.3](part_6_the_coherence_mathematics.md)). A row placed at `family`, `community` or `affiliations` may name only keys within its audience, and one that names a key outside it is refused `subject_outside_audience` ([CC 2.1](part_2_the_grammar.md#2.1)). So at those scopes the person a row is about is always in its audience. What a duty-holder's record shows the person it names is the rule of [CC 4.5.5](part_4_composition_governance.md#4.5.5). The one row about a person that does not reach them is the author's own `self` note, the last boundary case below.

**No holding claim leaves a bounded cohort (normative).** When a Contribution carries `cohort_scope: self` or `cohort_scope: family`, the substrate MUST NOT emit any holding claim observable outside the cohort. The `custody:ack:v1` report is placed at the content's scope and replicated to members only ([CC 3.1.3.3](part_3_the_namespace.md)). The bytes are delivered to admitted members of the self-collective ([CC 3.3.6](part_3_the_namespace.md) `identity_occurrence`) or the family ([CC 3.3.4](part_3_the_namespace.md)) through the at-rest encryption flow, never through the public holder-discovery directory. The holding claims of `community` and `affiliations` content reach the roster's members only, in the same way. The Commons' holding claims are at federation scope and are the holder directory.

**What an outsider cannot do.** The privacy property is structural, not policy:

- A non-member peer cannot issue `ContentFetch` for the bytes because no holding claim it can observe names a holder.
- A non-member peer cannot discover that the bytes exist through the substrate: the only attestations that refer to them are scoped to the cohort and never federate beyond it.
- This is **structural invisibility**: the privacy comes from what the wire format can carry, not from operator policy or a legal undertaking, so no operator can switch it off.

> **Scope (normative):** structural invisibility buys **content-holding confidentiality only** — it is NOT relationship-existence, metadata, traffic-analysis, or unobservability privacy. The bounding non-goals are stated canonically at [CC 1.13.3.1](part_1_foundation.md); do not represent CEG as providing the stronger properties.

**What moves to a peer (normative).** Being in a row's audience means the row may be served to a node, not that it is sent. A row moves to a peer when it is requested or required, and appropriate. It never moves because it is federation-tier: that tier means a row can be shared and may be public, not that it is copied to everyone.

| A row is | when |
|---|---|
| requested | the peer itself pulls for a subject or a dimension ([CC 5.3.2.4.4](#5.3.2.4.4)); an automatic diff is not a request |
| required | the peer must hold it to seal, address and take part: the consent-free set of [CC 5.4.6](#5.4.6) and the rows of the cohorts it belongs to |
| appropriate | its audience names the peer: it is addressed to the peer, is about it, or is placed in a cohort it is in, the family's replication tier and audience deciding ([CC 3.1](part_3_the_namespace.md#3.1), the family model) |

A `consent:replication` grant ([CC 3.3.7](part_3_the_namespace.md#3.3.7)) names the class it moves and moves that class and nothing else; it does not make a peer a mirror of the grantor's corpus. Anti-entropy over the commons is what serve seats do among themselves. A seat offers a person's node only what is required or appropriate for it, and the rest waits on a pull. A node with no owner is offered no more than that. It holds what it must to seal to and address the peers it dials, and what it was asked to hold, which is what a peer referred to it asks of it ([CC 5.4.6](#5.4.6)). It is never a copy of the mesh. What is required moves before any walk, so a fresh grant or a contact's own row never waits behind history. What is offered unasked is the live state, and a superseded row moves on request.

**Substrate enforcement**:

```
On admission of a Contribution C with cohort_scope ∈ {self, family}:
    # (1) STRUCTURAL INVISIBILITY — UNCONDITIONAL:
    substrate MUST NOT emit a holding claim for C's evidence_refs bytes outside the cohort
    substrate MUST NOT propagate C beyond the self-collective / family scope
        via any other directory or discovery surface
    # (2) AT-REST ENCRYPTION — the CC 4.4.3.4.1 cascade, always on (CC 4.4.3.4):
    recipients := if cohort_scope == self:   all current identity_occurrences of C.attesting_key_id
                  if cohort_scope == family: all current members of family per C.family_id
    FOR each recipient r:
        kem := resolve_encryption_keys(r.key_id)    # current occurrence's encryption_pubkeys (CC 3.3.6.1)
        IF kem is None OR kem.ml_kem_768 invalid:
            # FAIL-SECURE: no valid v2 wrap target ⇒ EXCLUDE r from the grant.
            # MUST NOT fall back to plaintext or to wrap_algorithm v1.
            # NOT SILENT: emit hard_case:recipient_excluded:{scope_key_id}
            #   (CC 3.4.4, which defines the closed reason-set) INTO the self/family
            #   scope — recipient r, reason, + the skipped Contribution's envelope
            #   ref. Scoped to the cohort; never federates beyond it (CC 5.2
            #   invisibility preserved).
            skip r   # content stays encrypted + unreachable to r until r registers encryption_pubkeys
        ELSE:
            substrate MUST wrap C's DEK via key_grant (CC 4.4.3.4.1, wrap_algorithm v2)
                to kem.{x25519, ml_kem_768}
```

**Two layers, not one.** (1) **Structural invisibility** — holding claims that never leave the cohort + non-propagation beyond scope — is the **unconditional** guarantee: no discovery attestation federates. (2) **At-rest encryption** — the CC 4.4.3.4.1 DEK cascade — is **defense-in-depth** (against local-disk forensics, the host operator, or the cloud-substrate operator); it is always on — a body written at a self, family, community or affiliations tier is sealed by the substrate, and no operator switch turns that off — and it uses `wrap_algorithm: v2` (hybrid PQC, CC 4.4.3.4.1), never v1. At those tiers the only plaintext bodies are those of authorized infrastructure communities and public rooms, which [CC 4.4.3.2.1](part_4_composition_governance.md#4.4.3.2.1) places at federation scope, holding claims included.

**Composition with the at-rest encryption flow**: persist wraps the DEK (`wrap_algorithm: v2`) under each currently-admitted `identity_occurrence`'s `occurrence_key_id` (self) or each `member.key_id` in the named family's roster (family). New occurrence / new family-member admission triggers retroactive `key_grant` emission for all extant `cohort_scope: self|family` content (the "I bought a new phone and want my history" / "I added Carol to the household" flows from CC 3.3.4 worked example).

**Recipient encryption-key resolution + fail-secure exclusion.** The wrap target is **not** a recipient's signing key. `wrap_algorithm: v2` needs the recipient's `{x25519, ml_kem_768}` **content-KEM** keys, which the recipient self-certifies via its `identity_occurrence.encryption_pubkeys` ([CC 3.3.6.1](part_3_the_namespace.md)); the substrate resolves them by `resolve_encryption_keys(key_id)` = the recipient's current (non-superseded, within-`valid_until`) occurrence → its `encryption_pubkeys`. Because this layer **mandates v2**, a recipient whose current occurrence carries **no valid ML-KEM-768 key MUST be fail-secure *excluded*** from the grant — the content remains encrypted and unreachable to it; the substrate MUST NOT fall back to plaintext or to `wrap_algorithm: v1`. To be an at-rest-encryption recipient, an identity MUST have a federation-present occurrence carrying `encryption_pubkeys`. This is the non-maleficence / fail-secure default: a missing key denies access, never downgrades the protection.

**Exclusion MUST NOT be silent.** A bare `skip` makes a fail-secure exclusion indistinguishable from "the family went quiet" — a soft-censorship vector for a buggy or malicious substrate, and a contradiction of the spec's own `hard_case:*` attestability grain. On every fail-secure skip the substrate MUST emit **`hard_case:recipient_excluded:{scope_key_id}`** ([CC 3.4.4](part_3_the_namespace.md), which defines the closed `reason` set) **into the affected self/family scope itself** — carrying the excluded recipient's `key_id`, a `reason`, and the skipped Contribution's envelope ref — so the excluded member (who still sees cohort-scoped attestations) has something to audit and remediate. The event is cohort-scoped: it MUST NOT federate beyond the self/family (the CC 5.2 invisibility promise is preserved; the *fact* of the family's content is not leaked by its exclusion events).

**Locality dividend**: `cohort_scope: self|family` content is the bulk of daily activity (family photos, personal notes, in-household device chatter), and that bulk never federates. Operators do not configure this; the wire format enforces it.

**Boundary cases**:

- A `cohort_scope: self` Contribution that is later promoted via `supersedes` to `cohort_scope: community` emits its holding claims at the new scope, on the NEW Contribution, at promotion time. The original `cohort_scope: self` Contribution's bytes remain structurally-invisible at federation; only the promoted scope's bytes propagate.
- `cohort_scope: self` content with `subject_key_ids` containing a non-self party (e.g., a private note Alice writes ABOUT Bob) is admitted and stays in Alice's self-collective; Bob does NOT receive a key_grant unless Bob is also in Alice's self (not the case for two distinct identities). Bob's [CC 2.3](part_2_the_grammar.md) subject-side revocation authority over the note still composes, but the bytes never reach Bob without Alice's explicit re-emit at a higher cohort_scope including Bob.
