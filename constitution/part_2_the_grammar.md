# Part 2 — The Grammar

**Decimal range** `2.x` · **60 sections** · **page budget 17pp** · [← master index](../README.md)

> The minimal-and-adequate wire grammar: the envelope, the five primitives, conformance, and canonicalization.

---

## 2.1 `envelope` — The envelope

The envelope is where a claim becomes accountable. Every `scores` Attestation carries it. Each member binds the claim to evidence, names who may take it back, or records the conditions it was made under. This entry says what each member in its tables means, once, and the rest of the document refers back to it. A member defined elsewhere has its home in the CC column of [CC 2.6.1.4](#2.6.1.4). A member's place relative to the signed bytes is the table of [CC 2.6.1.4](#2.6.1.4), which also gives a type and a presence rule to each member it lists by name. Every other member of a claim is a payload member under its own name, with the presence rule and the values this entry states.

The members fall into three groups: those every row carries, those any row may carry, and those one family requires. An optional member the producer leaves out is read as its default, and no party writes that default into the signed bytes ([CC 2.6.1.2](#2.6.1.2)).

**Every row carries**

| Member | Meaning |
|---|---|
| `attesting_key_id` | The attester's `federation_keys.key_id`. A substrate field. |
| `attested_key_id` | The subject's `federation_keys.key_id`. A substrate field. At a targeted scope it names the row's producer, as stated below. |
| `dimension` | REQUIRED. The canonical namespace prefix and scoped leaf. The admitting substrate resolves it through the namespace of [CC 3.1](part_3_the_namespace.md#3.1) on all five row types and refuses a row that fails the gate ([CC 2.4](#2.4), [CC 3.1.7](part_3_the_namespace.md#3.1.7)). |
| `score` | REQUIRED on `scores`. A scalar in [-1, +1]. The sign is polarity and the magnitude is strength. The per-dimension table of [CC 3.1](part_3_the_namespace.md#3.1) names each dimension's polarity, and [CC 3.1.7](part_3_the_namespace.md#3.1.7) R4 holds the closed classes. |
| `confidence` | REQUIRED on `scores`. The attester's own confidence in the score, in [0, 1]. High magnitude with low confidence says "I believe this strongly but I might be wrong". Low magnitude with high confidence says "I am sure the truth is near neutral". |
| `cohort_scope` | REQUIRED, with no wire default. One of `self`, `family`, `community`, `affiliations`, `species`, `biosphere`, `federation`: the Scope axis of [CC 2.5](#2.5), a closed set of seven. It is the cohort tier the row is addressed to: who may see it, and the tier its holding claims stay within ([CC 5.2](part_5_transport_substrate.md#5.2)). The authoring default is the smallest scope ([CC 1.13.3.4](part_1_foundation.md#1.13.3.4)). |
| `subject_key_ids` | The consent-holder keys for this Contribution. Each entry MAY be a `federation_keys.key_id` or a canonical-hash identifier. A set ([CC 2.6.1.2](#2.6.1.2)), absent when empty; the earlier form's mirror is [CC 8.11.9](part_8_appendices.md#8.11.9). An explicit `null` is refused ([CC 2.6.1.2](#2.6.1.2)). |

**Any row may carry**

| Member | Absent reads as | Meaning |
|---|---|---|
| `context` | nothing | Free-form scoping detail. Not parsed by the substrate; read by consumers, audit and RATCHET. |
| `evidence_refs` | nothing | Content hashes, a sequence ([CC 2.6.1.4](#2.6.1.4)), naming backing evidence: a payment receipt, a licensing-body record, an observed interaction, a log entry, an audit-chain leaf. Optional in general; some dimensions in [CC 3.1](part_3_the_namespace.md#3.1) require it non-empty. |
| `valid_until` | nothing | An instant in the [CC 2.6.2](#2.6.2) form. If set, consumer policy treats the attestation as stale after that point, independent of the row's own `expires_at`. It is REQUIRED on `session:*`, where it is the claim's signed horizon and a row without it is malformed ([CC 3.1.3.1](part_3_the_namespace.md#3.1.3.1)). |
| `epistemic_mode` | `direct` | The Epistemic-mode axis of [CC 2.5](#2.5): how the claim was formed. Consumers MAY weight by mode, a direct witness above hearsay. |
| `witness_relation` | `external` | `self`, `external` or `derived`: the attester's relation to the attested fact. `self` is the attested entity itself. `external` observed independently. `derived` inferred from other attestations or signed traces. Consumers weight by relation, so that self-attestation cannot game a verdict. |
| `oversight_mode` | `null`: consumer policy applies a per-cell default | `HITL`, `HOTL` or `HOOTL`: the human-control gradient under which the attestation was produced. |
| `occurrence_id` | `occurrence-0` | Which occurrence of a multi-occurrence agent deployment emitted the attestation: `occurrence-{n}` as the deployment assigns it, or `__shared__` for a shared-task emission. Self-asserted (below). |
| `occurrence_count` | `1` | Total occurrences in the deployment fleet, an integer at least 1. Self-asserted. |
| `occurrence_role` | `primary` | `primary`, `shared` or `replica`: the occurrence's role within the fleet. |
| `stake` | `reputational` | The Stake axis of [CC 2.5](#2.5). It composes with the attester's stake-backed-by attestations from [CC 3.1.1](part_3_the_namespace.md#3.1.1). |
| `community_id` | nothing | REQUIRED iff `cohort_scope` is `community` or `affiliations`; an affiliation is a community ([CC 4.4.3.12](part_4_composition_governance.md#4.4.3.12)). The `community_key_id` of the community this Contribution is scoped to ([CC 3.2](part_3_the_namespace.md#3.2) `community` subject_kind). One identity MAY belong to multiple communities, and this member says which community's roster gates visibility. A hierarchy edge resolves its `role_term` through it. The substrate rejects a community- or affiliation-scoped Contribution missing it. |
| `family_id` | nothing | REQUIRED iff `cohort_scope` is `family`. The `family_key_id` of the family this Contribution is scoped to ([CC 3.3.4](part_3_the_namespace.md#3.3.4) `family` subject_kind). One identity MAY belong to multiple families ([CC 4.4.3.15](part_4_composition_governance.md#4.4.3.15) Policy L), and this member says which family's roster applies. The substrate rejects a family-scoped Contribution missing it. |
| `delivery_mode` | `pull` | `pull` or `push`. On `pull`, subscribers discover holders through the holding claims at the content's scope (`custody:ack:v1` `here` rows, [CC 3.1.3.3](part_3_the_namespace.md#3.1.3.3)) and fetch with `ContentFetch` ([CC 5.3.2](part_5_transport_substrate.md#5.3.2)). On `push`, the substrate fans out to the live-delivery set, `fan_out = entitled ∩ reachable` ([CC 5.3.3.9](part_5_transport_substrate.md#5.3.3.9)), on links between members, directly or through the member relay tree ([CC 6.1.6](part_6_the_coherence_mathematics.md#6.1.6)). One-to-many delivery to a large audience stays pull-only ([CC 5.3.3.10](part_5_transport_substrate.md#5.3.3.10) E2). |
| `history_on_join` | `from_join` | `full` or `from_join`. Per target, and reserved for membership. On a stream, `full` is the producer's signal that the stream is kept ([CC 5.1](part_5_transport_substrate.md#5.1)). |
| `additional_scrubs` | nothing | **Quorum on a row** ([CC 2.4](#2.4) cosigned rows): further statements over the same payload as the row's own, one for each voice, each with its own composite signature ([CC 2.6.1.9](#2.6.1.9)). The list of the earlier form is [CC 8.11.9](part_8_appendices.md#8.11.9). This is the quorum carrier. |

**Members one family requires or carries**

| Member | On | Meaning |
|---|---|---|
| `session_id` | `session:*`, REQUIRED | The exchange a `session:*` claim is about, verbatim and case-preserved. With `community_id` it is the claim's key ([CC 3.1.3.1](part_3_the_namespace.md#3.1.3.1)). |
| `claimed_at` | `session:*`, REQUIRED | When the claiming occurrence took the session, in the [CC 2.6.2](#2.6.2) form. The convergent merge orders on it ([CC 3.1.3.1](part_3_the_namespace.md#3.1.3.1)). |
| `scope` | `consent:state:granted` and `delegates_to`, REQUIRED | What the row covers: a bare token or an array of tokens. On a `consent:state:granted` row it is **the grant's scope** ([CC 3.3.1](part_3_the_namespace.md#3.3.1)): `retain`, `share`, `analyze`, `train` or `publish`, sub-scoped in the token as `retain:90d`. A grant naming no scope matches nothing. On a `delegates_to` it is the delegated scope set ([CC 4.4.3.19](part_4_composition_governance.md#4.4.3.19)). It is inside the signed bytes like every member. A consumer that does not know the member preserves it per [CC 2.1.1](#2.1.1) and MUST NOT compose a `capacity:*` verdict that ignores it. |
| `custody_state` | `custody:ack`, REQUIRED | `here` or `none`: whether the reporting device holds the blob ([CC 3.1.3.3](part_3_the_namespace.md#3.1.3.3)). A signed `none` is a custody fact, not an absence. |
| `group_kind` | `membership:proposal`, REQUIRED | `family` or `community`: which kind of group the proposal's target names ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). |
| `role` | `membership:proposal`, optional; restated on `membership:acceptance` | The role the proposal offers the invitee. An acceptance restates it, and a widening that assigns a different role does not match ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). |
| `expires_at` | `membership:proposal`, REQUIRED | The proposal's signed expiry in the [CC 2.6.2](#2.6.2) form, after its `asserted_at` and at most 30 days later. It is the proposal's own stated end: the member who concludes reads it on its own clock and signs the widening as the landing, and a late acceptance is closed ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). |
| `subject_sha256_ed25519_raw` | a `moderation:*` score, optional | The subject key named by the SHA-256 of its raw 32-byte Ed25519 public key, a byte string ([CC 2.6.1.2](#2.6.1.2)) whose earlier form is 64 lowercase hex per [CC 8.11.11](part_8_appendices.md#8.11.11), so the row does not carry the key's cleartext label ([CC 2.4.1.1](#2.4.1.1)). A malformed value is refused at admission. |
| `attached_head_digest` | `trust:accepts:v1` that attaches a root, REQUIRED | The SHA-256, a byte string ([CC 2.6.1.2](#2.6.1.2)), of the lineage head the acceptance edge attaches on: the signed roster record at that version ([CC 3.2](part_3_the_namespace.md#3.2) T4a). It is checked at the edge's **first admission only**, against the Receipts held for that head and the root's `attach_window_secs`, and never re-checked on a node's own restore. An edge whose digest is later un-headed by a lowered `revoked_after` is read as naming that head's nearest verifying ancestor (T8 viii). |
| `attach_window_secs` | the genesis bundle's `charter` member, optional | Integer seconds. The oldest that the newest counted Receipt of a lineage head may be for a consumer to *attach* to this root ([CC 3.2](part_3_the_namespace.md#3.2) T4a). It MUST exceed `receipt_cadence_secs` plus the [CC 2.6.7](#2.6.7) skew tolerance. A charter that declares none makes its root attachable only through an out-of-band anchor to a specific head (T5). Never a validity leg for an attached root (T4). |
| `receipt_cadence_secs` | the genesis bundle's `charter` member, REQUIRED where the charter names services | Integer seconds. How often each named Transparency Service issues a Receipt again for the head in force, unchanged: the equivocation-exposure window ([CC 3.2](part_3_the_namespace.md#3.2) T6). It is present with `receipt_quorum` and `transparency_services`, or none of the three is. |
| `receipt_quorum` | the genesis bundle's `charter` member, REQUIRED where the charter names services | Integer. The Receipts from distinct independent named services that a head needs to count as receipted. It MUST equal ⌊\|`transparency_services`\|/2⌋ + 1 and be at least 2 ([CC 3.2](part_3_the_namespace.md#3.2) T6). A charter without it names no services, and `0` is never written. Any other value is refused at admission. |
| `transparency_services` | the genesis bundle's `charter` member, REQUIRED where the charter names services | A set of identity references ([CC 2.6.1.1](#2.6.1.1)): the Transparency Services the lineage registers its heads with ([CC 3.2](part_3_the_namespace.md#3.2) T6). Each service's key record is named by its row id among the rows the bundle cites. The set sits inside the bundle's signed bytes ([CC 5.3.4](part_5_transport_substrate.md#5.3.4)). Each counts as a service of the lineage by this listing alone, whatever its `identity_type` ([CC 3.2](part_3_the_namespace.md#3.2) T6). Each MUST be independent of the lineage: not a holder, not a seat, and not owner- or steward-bound to a holder or a seat. A listed service that is not independent of the lineage is not counted toward `receipt_quorum`, and the other Receipts stand. A change is a later bundle, an amend ([CC 5.3.4](part_5_transport_substrate.md#5.3.4)), receipted by the set before it. |
| `halt_fuse_secs` | the genesis bundle's `charter` member, optional | Integer seconds. How long a `constitutional` halt signed by ONE holder stands before it lapses unless a strict majority of the standing roster confirms it ([CC 4.2.1.1](part_4_composition_governance.md#4.2.1.1)). **Absent means 86400.** The value is a constant of this document, read by the verifier, not a substrate-internal default. So a charter minted without the member is conformant and carries the 24-hour fuse. An explicit value overrides it, by a later bundle. |
| `recovery_commitments` | the genesis bundle's `charter` member, REQUIRED ([CC 4.2.6](part_4_composition_governance.md#4.2.6)) | A map from each holder's identity reference to its commitment ([CC 2.6.1.11](#2.6.1.11)). Each commitment is the [CC 3.2](part_3_the_namespace.md#3.2) T3 commitment over the holder's one recovery key, its composite COSE key exactly as stored on its key record ([CC 2.6.1.7](#2.6.1.7)). A commitment of the earlier form is the one of [CC 8.11.14](part_8_appendices.md#8.11.14). It binds key material, never only the id. A holder rotates lost signing-key material by a self-`supersedes` under a key whose record hashes to its entry. |
| `consent_supersedes` | `consent:state:*`, optional | The prior consent-state row this one supersedes: a renewal, or the substrate's `consent:state:expired` naming the grant that lapsed ([CC 3.3.1](part_3_the_namespace.md#3.3.1)). |
| `deletion_window` | a producer's row, optional | The producer's commitment at publication: the deadline by which the consented payload must be deleted once consent ends, carried on the envelope of the row that holds it ([CC 3.3.1](part_3_the_namespace.md#3.3.1)). Absent means this member carries no commitment; no family default exists ([CC 2.6.1.4](#2.6.1.4)). |
| `widened_at` | a widening `supersedes`, REQUIRED | The instant a widening took effect, in milliseconds ([CC 2.6.2](#2.6.2)). It is the `scrub_timestamp` of the widening's signature ([CC 4.4.3.14](part_4_composition_governance.md#4.4.3.14)). |
| `accord_root` | `accord:*` rows, REQUIRED | The `key_id` of the accord an `accord:*` row belongs to ([CC 4.2](part_4_composition_governance.md#4.2)). |
| `consent_basis` | `capacity:*` and `observation:access_assumption:v1`, carried | The consent grants a witness relied on, as `[* {principal, paths, attestation_id}]`. For each principal: the paths by which its grant reached the subject (`subject`, `occurrence_of`, `delegates_to`) and the `attestation_id` of the `consent:state:granted` row. Validated at the family's gate. |
| `n_eff_pr` | `capacity:*`, carried | The effective sample size of the scoring window as a participation ratio of the feature covariance spectrum. The gate reads this one. |
| `n_eff_h` | `capacity:*`, carried | The same window's effective sample size as an entropy perplexity, `exp(−Σ p·ln p)` over the normalised spectrum. Carried for audit, not gated. |
| `sample_size`, `feature_dim` | `capacity:*`, carried | Rows in the scoring matrix, and features per row. |
| `sample_size_gate`, `target_n_eff`, `min_feature_dim`, `n_eff_floor` | `capacity:*`, carried | The configured gates: the minimum sample size the score was gated on, the target effective sample size, the minimum feature dimension, and the effective-sample-size floor below which no score is emitted. |
| `window` | `capacity:*` and `observation:access_assumption:v1`, carried | The scoring or observation window, in rows. |
| `trace_level` | `observation:access_assumption:v1`, REQUIRED | `generic`, `detailed` or `full_traces`: the trace level the observed agent's install emitted at. |
| `occurrence_key_ids` | `observation:access_assumption:v1`, REQUIRED | A set: the occurrences whose rows the witness read. |
| `window_from`, `window_to` | `observation:access_assumption:v1`, REQUIRED | Start and end of the observation window, each an instant of [CC 2.6.2](#2.6.2). |
| `channel_classes` | `observation:access_assumption:v1`, REQUIRED | A set: the classes of channel through which the witness saw the subject, as the emitter names them. |
| `amendment_digest` | `identity_amendment:v1`, REQUIRED; `deferral:response:approved:v1`, where it authorises an amendment | SHA-256 of the identity amendment as applied ([CC 3.1.5](part_3_the_namespace.md#3.1.5)). |
| `authorized_by` | `identity_amendment:v1`, REQUIRED | The `attestation_id` of the `deferral:response:approved:v1` row that authorised the amendment. |

**Three axes that do not depend on each other.** `cohort_scope`, with `family_id` or `community_id`, is the visibility axis. `subject_key_ids` is the revocability axis. `delivery_mode` is the delivery axis. Each is orthogonal to the other two ([CC 2.3.3](#2.3.3)). `cohort_scope` is the one member a placement-touching re-sign may narrow; it is never re-authored. The earlier form states the same of its mirror member at [CC 8.11.9](part_8_appendices.md#8.11.9).

**The group id is read inside the group.** Community content is encrypted at rest under the per-community DEK. Its holding claims reach the community's members only, and the same holds at every bounded scope ([CC 5.2](part_5_transport_substrate.md#5.2)). So `family_id` is consulted in-substrate and never on the wire to non-members.

**A targeted row names its producer (normative).** A row placed at a targeted scope (`family`, `community`, `affiliations`) names its own producer in `attested_key_id` and the party it is about in `subject_key_ids`. A targeted row naming a third party in `attested_key_id` is refused at admission ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)), with two registered exceptions. A key grant names the recipient occurrence there, and a roster version names the group ([CC 3.1.3](part_3_the_namespace.md#3.1.3), [CC 3.3.2](part_3_the_namespace.md#3.3.2)). For a `delegates_to` row `attested_key_id` is the delegate by the grammar's definition ([CC 2.4.1.2](#2.4.1.2)), and the producer rule is the `scores` row's.

**Whom a targeted row may name (normative).** At a targeted scope the keys a row lists in `subject_key_ids` are keys within the row's audience and no others. A key is within the audience in one of two ways. It is a member of the cohort by the authorized roster fold at the roster head the row names. That is the fold every bounded-scope door uses, so a key whose removal is in the row's causal past is outside. Or it is the key the family delivers the row to. These are a membership proposal's invitee ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)), a key grant's recipient ([CC 3.3.2](part_3_the_namespace.md#3.3.2)) and the owner's own node on an owner-binding ([CC 3.2](part_3_the_namespace.md#3.2)). A further family reaches outside its cohort only where its registration says so. A subject named by canonical hash is reached through its rule-3 proxy ([CC 2.4.1.1](#2.4.1.1)), which MUST be within the audience. A row naming a key outside its audience concludes nothing, since the check reads the roster at the head the row names; the reason reported is `subject_outside_audience`. A subject who can neither see nor contest a row has no standing to exercise, and [CC 3.4.5](part_3_the_namespace.md#3.4.5) promises the subject a read over the rows they are party to. Within the audience a row about another member is admissible. The named member's standing is that of `subject_key_ids` and [CC 4.5.5](part_4_composition_governance.md#4.5.5). So the rows a reader is served decide every row it is party to, and tell it nothing of a row outside its audience, not even that the row is held ([CC 5.2](part_5_transport_substrate.md#5.2)).

**What a subject key may do.** Each key listed in `subject_key_ids` has authority the substrate recognises to do two things. It may issue `withdraws` against this Contribution, under the rules and the kept list of [CC 2.4.1.1](#2.4.1.1). It may emit `consent:*` dimensions about this Contribution. An empty list means no subject authority: the producer alone has authority over the row.

**Cosignatures travel beside the row.** `additional_scrubs` is never inside the signed object, since a cosignature cannot be inside the bytes it signs. Each cosigner's role is read from the receiver's fold, not from the entry. The family declares which `consensus_protocol` the cosigners must satisfy. A cosigned row is retracted only by a cosigned `withdraws` ([CC 2.4.1.1](#2.4.1.1)). This is the general form of the ceremony plane's scrub set ([CC 3.2](part_3_the_namespace.md#3.2) T2).

**A change of oversight mode is the steward's act.** A mode shift is a stewardship act on the delegation plane, not a scored dimension. The human-control gradient an agent may operate under is bounded by the `agency:*` scopes its steward conferred ([CC 4.4.3.19](part_4_composition_governance.md#4.4.3.19)). So a shift is recorded as the steward issuing a **superseding `delegates_to`** ([CC 2.4.1](#2.4.1)) carrying the new scope set. `supersedes` keeps the prior grant as forward-only history ([CC 4.5.9.3](part_4_composition_governance.md#4.5.9.3)). This is the same naming and superseding machinery that governs a community's duty holders ([CC 4.5.5](part_4_composition_governance.md#4.5.5)). A consumer MAY treat an `oversight_mode` inconsistent with the agent's live grant as it treats any self-claim exceeding its delegation. There is **no `accountability:*` family**. Accountability is structural (the audit chain), never a named axis, and an `accountability:*` dimension does not admit under [CC 3.1.7](part_3_the_namespace.md#3.1.7) R2.

**Occurrence members are self-asserted.** `occurrence_id` and `occurrence_count` are not cryptographically bound to a fleet-attestation primitive. An adversary running a single key can claim any `occurrence_id`. This limit of the design is acknowledged at [CC 8.3.1](part_8_appendices.md#8.3.1). Substrate self-report attestations SHOULD carry `occurrence_id`, `occurrence_count` and `occurrence_role`. A compliance reviewer can then reconstruct, after the fact, which occurrence agreed to which mandate.

**Delivery and history beyond the member.** `delivery_mode` composes with [CC 4.4.3.10](part_4_composition_governance.md#4.4.3.10) Policy M for community-scoped delivery, and with [CC 5.3.3](part_5_transport_substrate.md#5.3.3) streaming for `live_stream` chunk-DAG delivery. At `community` and `affiliations`, `history_on_join` is carried and does not change what a new member receives. The tier's rule fixes that: a community joiner receives the current epoch's key and no earlier epoch's ([CC 4.4.3.16](part_4_composition_governance.md#4.4.3.16)). What a kept stream's joiner can fetch is bounded by `min(operator depth cap, chunk-eviction horizon)` ([CC 5.1](part_5_transport_substrate.md#5.1), catch-up bound). An evicted-epoch grant returns `ContentMiss`, never a silent gap.

**`epistemic_mode` and `witness_relation` are two things.** They co-vary at the edges but name different concerns. `epistemic_mode` names the *process* by which the claim was formed. `witness_relation` names the *relational position* of the attester to the attested. Detector-derived attestations carry both: `epistemic_mode: derivative` and `witness_relation: derived`. Most encyclical-sourced translations are `witness_relation: external` with `epistemic_mode: hearsay`. When in doubt, set both.

### 2.1.1 `forward-compatibility` — Forward-compatibility rule

The envelope is meant to grow without breaking the peers already speaking it. Two rules make that safe. The canonical-bytes contract means a new field never silently changes what an old signature covers. The unknown-field discipline means a consumer never rejects an envelope merely for carrying a field it has not learned yet.

> **Canonical-bytes contract**: the canonical-bytes encoding of this envelope for signing follows [CC 2.6.1](#2.6.1) (the deterministic CBOR payload of [CC 2.6.1.2](#2.6.1.2); defaults are interpretation-time, NOT encoding-time; relay MUST preserve member presence/absence exactly as the producer signed). Optional fields with documented defaults in the table above ride the CC 2.6.1.2 omit rule. Conditional-required fields are NOT optional-with-default and substrate rejects mis-shape per [CC 2.3.1](#2.3.1) + [CC 4.5.2.1](part_4_composition_governance.md#4.5.2.1) + [CC 4.5.12.2](part_4_composition_governance.md#4.5.12.2).

A Conforming Consumer that receives an envelope carrying a field-name it does not recognize MUST:

- Preserve the unknown field on read (do not strip).
- Preserve it on re-emission if the Consumer is also acting as a Producer relaying the attestation.
- NOT use it in verdict composition.
- NOT reject the envelope on the basis of the unknown field alone.

Producers introducing a new envelope field MUST follow the [CC 2.6.4](#2.6.4) versioning rules: a new field with a documented default is a MINOR bump; a field whose absence breaks consumer semantics is a MAJOR bump.

## 2.2 `conformance` — Conformance levels

Interoperability needs named roles so that "conforming" means the same thing to every peer. CEG is the **CIRIS Epistemic Grammar**, the wire grammar this specification defines ([CC 8.1.1](part_8_appendices.md#8.1.1)); the roles below are named for it. A **Producer** is any peer that emits Contributions onto the federation wire. A **Consumer** is any peer that reads and composes verdicts over received Contributions. A **Substrate Implementation** is the storage + transport + crypto layer underneath both.

Three normative conformance profiles set the floor each role must meet:

1. **CEG-Conforming Producer (CCP)** — emits well-formed envelopes per [CC 2.1](#2.1), signs per [CC 2.6.1.1](#2.6.1.1) ([composite-sig]), respects reserved-prefix rules per [CC 3.4](part_3_the_namespace.md#3.4), declares its `oversight_mode` and `witness_relation` per [CC 2.1](#2.1).
2. **CEG-Conforming Consumer (CCC)** — verifies composite signatures ([CC 5.3.2.8](part_5_transport_substrate.md#5.3.2.8)), enforces reserved-prefix rules at admission ([CC 3.4](part_3_the_namespace.md#3.4)), implements at least Policy A ([CC 4.4.3.34](part_4_composition_governance.md#4.4.3.34)) with the default aggregation rules from [CC 4.4.2](part_4_composition_governance.md#4.4.2), MUST honor `null` placeholder/dev hardware-class rejection per [CC 4.2.2](part_4_composition_governance.md#4.2.2).
3. **CEG-Conforming Substrate (CCS)** — implements the storage + transport guarantees referenced in [CC 5.3.2](part_5_transport_substrate.md#5.3.2) + [CC 5.3.1](part_5_transport_substrate.md#5.3.1), including idempotent replication, full-SHA blob verification before consumption ([CC 5.3.2](part_5_transport_substrate.md#5.3.2)), and receipt-quorum counting of registered heads ([CC 5.3.1](part_5_transport_substrate.md#5.3.1)).

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

**Scope of the fingerprint check:** the check is the MUST of [CC 2.6.8](#2.6.8). A consumer verifies a `key_id`'s fingerprint suffix against the public key it obtains **at registration and at pairing** — the proof-of-possession door — for fedIDs and roster keys ([CC 3.3.6.4](part_3_the_namespace.md#3.3.6.4)). A held key registered under an older or otherwise non-matching id is not re-keyed or refused by a migration (the record is history), it simply cannot be re-registered or introduced at pairing under that id. A bundle's `family_key_id` and a group's id are not fingerprint-suffixed, and this rule does not check them. The reader's anchor verifies a bundle ([CC 5.3.4](part_5_transport_substrate.md#5.3.4)), and a group's id is derived as [CC 3.3.4](part_3_the_namespace.md#3.3.4) states. The fingerprint rule is separate from the roster-id *form* rule of [CC 3.3.6.4](part_3_the_namespace.md#3.3.6.4). A `device-<hex>-<fp>` id passes the fingerprint check and is refused by the roster door for its form, on the roster door's own schedule.

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

**P2 — injectivity is structural, not statistical.** Because `{platform}` and `{entity_kind}` admit no colon, the joined string reverse-parses to exactly one triple (the `{id}` production only shrinks the admitted domain, so injectivity survives it a fortiori). `("p","k:a","b")` and `("p","k","a:b")` are not two spellings of one preimage: one is an admissible triple, the other is a rejected input. The delimiter therefore carries the full anti-collision property over the admitted domain, and no length prefix is needed to obtain it. The `lp(x) = u32_be(len(x)) ‖ utf8(x)` discipline is the [CC 6.1.3](part_6_the_coherence_mathematics.md#6.1.3) rule for **substrate framing objects that never enter the signed payload**. A canonical subject is a string value *inside* a [CC 2.1](#2.1) envelope field and sits on the signed-payload side of that boundary. So adopting `lp` here would cross the CC 6.1.3 seam and re-spell every digest below to buy a property P2 already gives. The delimiter form stands.

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
- **`canonical_binding`** — *retroactive identity claim*. A now-enrolled federation key asserts "I AM the entity behind `canonical:sha256:{hex}`", binding past canonical-hash subject entries to its real identity. The binding is a claim consumers weigh, and it admits nothing by itself: it opens no `withdraws` under rule (2) ([CC 3.3.14](part_3_the_namespace.md#3.3.14)). Rule (2) opens only for a row that names the bound real `key_id`.

`canonical_binding` is **NOT a new admission rule** (no "rule 5"). It is a bare `scores` row on `identity:canonical_binding:{canonical_hash}`, self-asserted by the enrolling key ([CC 3.3.14](part_3_the_namespace.md#3.3.14)). Proof that the key controls the preimage is the consumer's to weigh. Withdrawal for that subject stays the rule (3) proxy.

#### 2.3.2.3 `subject_kind-payload` — `subject_kind` is a payload-level discriminator

`subject_kind` (e.g. `consent_record`, `consent_replication` ([CC 3.3.7](part_3_the_namespace.md#3.3.7)), `key_grant`, `takedown_notice`, `community`, `family`, `identity_occurrence`, `location_proof`) is **not a typed member of the [CC 2.1](#2.1) table**. It rides inside the signed `attestation_envelope`, the payload of [CC 2.6.1.4](#2.6.1.4), untyped by the substrate, and is preserved on relay ([CC 2.1.1](#2.1.1)); the substrate neither validates nor indexes it. The typed envelope members are those the [CC 2.1](#2.1) table names (`cohort_scope`, `subject_key_ids`, `community_id`, `family_id`, `delivery_mode`, and the rest). `subject_kind` is the discriminator that selects which [CC 3.3](part_3_the_namespace.md#3.3) payload schema applies, validated at the family's own gate, parallel to the `sub_kind` an `external_content` row carries. The CC 3.3.5 `consent_record` example and any conformant producer payload agree byte-for-byte: `"subject_kind": "consent_record"` is a member of the signed bytes, not a column of the row.

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

The delivery axis is the **third orthogonal axis**: visibility + revocability alone give the substrate no envelope-level handle on who actively *receives* content and how the substrate fans out. Per [CC 5.3.3](part_5_transport_substrate.md#5.3.3), three optional envelope fields + the CC 5.3.3 endpoint section + a delivery extension to [CC 4.4.3.10](part_4_composition_governance.md#4.4.3.10) Policy M supply it.

### 2.3.4 `self-as-subject` — Self-as-subject ceremony

When `attesting_key_id ∈ subject_key_ids`, the Contribution is a **self-consent ceremony** — the same identity is attesting AS subject AND producer. This composes naturally with the CEG-native agent's self-attestation pattern: agent attests `identity:current` about itself with `subject_key_ids = [self.key_id]`, asserting consent-authority over its own identity claims.

### 2.3.5 `shape` — The shape

`subject_key_ids` is an OPTIONAL list. When present, each entry names a party with substrate-recognized authority over this Contribution's continued processing ([CC 2.1](#2.1), [CC 2.3](#2.3)). The basic shape:

> A consent record is a signed declaration by a subject about the substrate's continued processing of content where that subject appears.

The medical record, photo, interview, training-datum, and group-chat cases all share the same shape — a producer publishes a Contribution; one or more subjects appear in it; the subjects retain revocation authority. A single shape carries thirteen distinct content cases uniformly.

### 2.3.6 `absent` — Empty/absent = status-quo

`subject_key_ids` absent or empty is the status-quo shape (producer-only authority; same as a baseline Contribution carrying no subject authority) ([CC 2.1](#2.1), [CC 2.3](#2.3)). Consumers that don't read the field see status-quo behavior. Subject authority is additive at the envelope layer — adding it never changes how an existing consumer reads an envelope that omits it.

## 2.4 `primitive` — The primitive set — 1+4

The whole grammar reduces to five wire primitives: one workhorse that makes claims, and four structural composers that operate on the claim graph itself. Minimal-and-adequate is the design discipline — fewer primitives mean a smaller surface to attack, audit, and prove conformant, which is what Integrity asks of the wire.

**The row-type slot is closed: the five, and nothing else (normative).** Every row on the attestation plane names its type in one slot: the row's `attestation_type`, label -70001 of the protected header ([CC 2.6.1.1](#2.6.1.1)). That slot admits exactly the five primitives of this section, closed by [CC 1.7](part_1_foundation.md#1.7). There is no second class of row. A **carrier** — a self-attestation with no score, no subject and no dimension, read by no fold — is a claim with its family rule missing. A holder directory without a family has no declared audience, so bounded content would advertise its existence to everyone, and a fold would have to exclude it by type. The holding claim is `custody:ack:v1` at the content's scope ([CC 3.1.3.3](part_3_the_namespace.md#3.1.3.3)). A set of wraps in one row has, as its only structural property, a union that only grows, which one `scores` row per recipient already gives. A key grant is `key_grant:{axis}:v1`, one row per recipient ([CC 3.3.2](part_3_the_namespace.md#3.3.2)). A row naming `holds_bytes` as its type is refused `attestation_type_unregistered`.

*The gate.* A substrate MUST refuse at admission, with **`attestation_type_unregistered`**, any row whose type is not one of the five, byte-compared — on local emission and on replication alike. The gate is an **allowlist** built from the registry's `_meta.row_types` ([CC 3.1.7](part_3_the_namespace.md#3.1.7)); the absence of a check on a free-text column is not a gate, and a type that is merely *storable* is not thereby admitted. A row of the five that names `holds_bytes` as its `dimension` is refused.

*The dimension gate follows the dimension, not the row type.* A `dimension` on **any** of the five MUST resolve through the namespace exactly as it does on `scores`: the case rule, the version tail, the reserved and gated stems. That holds for the job label on a `delegates_to` row as much as the family on a `scores` row. A row type is never a way around the namespace.

*No more of them.* The slot is amended only by a change to this section, in a release of this document, through the [CC 1.7](part_1_foundation.md#1.7) refutation bar: a claim that cannot be expressed by the five plus envelope composition. A component that needs a new row type files it here **before** it ships; a type found in code and not here is a defect in the code. A row of an unregistered type that a substrate already holds when it adopts this rule is reported to the operator, is neither served nor replicated, and is not deleted. The registry carries the closed list and vectors for it.

**Cosigned rows: quorum is an envelope property, not a row type (normative).** A single-signer row cannot carry a quorum's act, and [CC 2.4.1.1](#2.4.1.1) rules 1 and 2 would let one signer or one subject undo one. Cosigned rows close both, so group records, membership widenings and removals, partner records and the `ciris-canonical` scrub set are rows on the plane. **Any of the five MAY carry `additional_scrubs[]`** ([CC 2.1](#2.1), [CC 2.6.1.9](#2.6.1.9)): further statements over the same payload, each with its composite signature, by a key whose role the receiver's fold names. Those signatures are the general form of the scrub set the ceremony plane already uses ([CC 3.2](part_3_the_namespace.md#3.2) T2).

The **family declares its `consensus_protocol` source**: the group the row is about, the accord, or — for `licensure:{community_key_id}` ([CC 2.4.1.3](#2.4.1.3)) — the authority community named in the dimension. A `licensure:{authority_id}` row that is the authority community's act under that protocol is counted ([CC 2.6.1.9](#2.6.1.9)), and every other is authored. **Admission:** the row is admitted when its cosigners satisfy that protocol, judged on the *receiver's own* fold over the members at the roster head the row names ([CC 2.7.4](#2.7.4)). **Collection:** a row short of its protocol by signatures alone is not refused; it waits, as the kernel states ([CC 2.7.3](#2.7.3)). Such a row is held as its own voices, served to the group's active members only, for the hold window of [CC 3.3.4](part_3_the_namespace.md#3.3.4).

A cosigned act is named by its row id ([CC 2.6.1.3](#2.6.1.3)), the digest of what its signers signed, which covers no signature. So every node that assembles a sufficient set holds the same act whichever signatures it gathered, and a row that names the act resolves on each of them. **Retraction of a cosigned row is by the same quorum** ([CC 2.4.1.1](#2.4.1.1) rule 0), so no single signer and no subject can retire a community, un-name a charter or retract a roster event.

What this brings onto the base, each as a registered family in [CC 3.1.3](part_3_the_namespace.md#3.1.3):

- **roster versions** (`group:roster:v1`, the T6 head, with `prev_head_digest` in `refs`, [CC 3.1.3](part_3_the_namespace.md#3.1.3)),
- **membership events** (`membership:widening:v1` / `removal:v1`, cosigned, and `resignation:v1`, signed by the leaving member alone ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)), beside the single-signer proposal, acceptance and decline), and
- the **key plane**:
  - a key claim (`key:record:v1`, attester = the key, admitted by **proof of possession** against the keys it carries, the one stated exception to resolve-the-attester). Renewal is a `supersedes` by the same key and rotation a record of the next key cosigned by the old one, each bounded as [CC 2.4.1.1](#2.4.1.1) states; an anchor scrub or accord co-scrub is a cosignature),
  - occurrences (`identity:occurrence:v1`, signed by the identity or a live occurrence) and
  - revocations (`key:revocation:v1`, never withdrawn, subject = the key digest, `revoked_after` only ever lowering).

The roster fold, the acceptance gate and T7 recovery are unchanged; only their inputs become rows. **Admission order:** a row is admitted only once its signer's key-claim row is held, and a row signed by a key not yet held is retryable, since a row waits for what it names ([CC 2.7.3](#2.7.3)).

What stays off the plane, by definition, is not a claim: payload bytes (sealed chunks, and the A/V plane's symbols), a Transparency Service's Receipts ([CC 5.3.1](part_5_transport_substrate.md#5.3.1)), the wholeness corpus, node-local derived state, an agent's private runtime. **Accord evidence** (proposals and participations as rows) is not on the base: it would amend the entrenched [CC 4.2](part_4_composition_governance.md#4.2) surface. Any such change is bound by this constraint: the invocation's domain-separated canonical bytes MUST travel inside the envelope unchanged, and the kill switch MUST NOT depend on any plane gate beyond verifying those bytes and the holder roster.

### 2.4.1 `structure` — The four structural composers

The four structural composers act on the attestation graph itself, not as score-claims on entities. They are how an attester delegates authority, replaces a row, retracts a row, or admits a row was false:

| `attestation_type` | What it does | Envelope shape |
|---|---|---|
| `delegates_to` | A authorizes B to sign on A's behalf within a bounded scope | `{scope[], delegation_purpose, delegation_valid_from, delegation_valid_until}` — `delegation_valid_until` is **REQUIRED, at most 365 days (365 × 86 400 s) after `delegation_valid_from`**, on any edge carrying `sub_delegation`, `license`, `grant`, `moderate`, `takedown`, `review` or `slash`, or sitting in an affiliation's `hierarchy` ([CC 4.4.3.12](part_4_composition_governance.md#4.4.3.12) C); a perpetual or over-ceiling edge is refused `delegation_term_required`; `delegation_valid_from` absent means the edge's own `asserted_at`, and `delegation_valid_until` absent on an edge that needs no term is open-ended, never malformed — `scope` is the [CC 2.1](#2.1) member (a bare token or a set; the one name for this wire member, never `delegated_scope[]`) |
| `supersedes` | This attestation row replaces a prior one by the same attester, or by the same protocol for a cosigned row. Another signer's row is replaced only where that signer has signed its own step-down ([CC 3.2](part_3_the_namespace.md#3.2)). A widening replaces nothing ([CC 3.5.1](part_3_the_namespace.md#3.5.1)) | `{references_attestation_id, supersession_reason, differs_in[]}` |
| `withdraws` | A party [CC 2.4.1.1](#2.4.1.1) admits retracts a row (does NOT claim it was false) | `{references_attestation_id, withdrawal_reason}` |
| `recants` | My prior attestation was false at issuance — admits epistemic error | `{references_attestation_id, recantation_reason, what_was_false}` |

**Translation implications**:

- A **doctrinal-development** claim ("this version extends but does not contradict the prior version") is `supersedes` with `differs_in: ["scope", "evidence_refs"]` — NOT `recants` (which would assert prior was false).
- An **acknowledged-error** claim ("the prior framing was wrong; I admit the mistake") is `recants` — distinct from `withdraws` ([CC 2.4.1.1](#2.4.1.1)).
- A **prudent-retraction** ("I'm withdrawing without claiming it was false; context has changed") is `withdraws`.
- An **authority-source claim via delegation** ("this constitutional position derives from authority-key X in scope Y") is `delegates_to` with X as `attested_key_id`. This is the [CC 2.4.1.2](#2.4.1.2) reuse pattern for authority-source claims. It replaces what would otherwise need a `grounding:{tradition}:{principle}` prefix that fails [CC 1.2](part_1_foundation.md#1.2) T2.

#### 2.4.1.1 `withdraws` — Who may take a row back

A `withdraws` row retires its target as a cut does ([CC 2.7.7](#2.7.7)). An act under the target that the withdrawal has among its ancestors stands. One that has the withdrawal in its own past does not count. One concurrent with it counts where it was made and is not in force afterwards, as the paragraphs below state. It does not say the target was false. The rule below widens who may retract a row; the primitive itself does not change.

**The end of a standing (normative).** The two sentences above are read as follows, and a node reads no instant to decide any of it.

*An act names its head.* A row signed in exercise of a standing names the head it is at, in `refs.head`. The head is the newest its signer holds of the record that seats the standing. For a seat in a room or a family it is the roster version ([CC 2.7.8](#2.7.8)). For a grant from a root it is the bundle in force. A row signed under a root grant names that bundle, and names in `refs.also.stands_on` the acceptance of that grant it stands on. A row that names the bundle alone, or names a binding, stands on no acceptance and counts for nobody. Where one row between two keys is the whole record, as an owner-binding is, that row is the head. A row that exercises a standing and names no head concludes nothing, `act_names_no_head`. An acceptance or a decline names none: it names the row it answers, and that row names the head. An accord invocation names none, since it fires at each node on receipt, under the roster that node holds ([CC 4.2.1.1](part_4_composition_governance.md#4.2.1.1)). At federation scope and in the commons there is no roster, so a row there names a head only where its signer signs under a standing.

*An end names the head it acts from.* A row that ends a standing carries `refs.head` beside its target: a withdrawal of an acceptance or of an offer, an unseating, a resignation. That head is the newest its signer holds, and an end with a newer head in its own past concludes nothing, `end_names_old_head`. The end concludes under its signer's own standing at that head, so one's own acceptance is withdrawn by one's own signature. It reaches the acts exercised under its target, a deputy's among them. It never reaches the members counted at any head ([CC 2.7.8](#2.7.8)).

*What the end does to an act.* An act with the end in its past does not count under the ended standing. An act at the end's head, at an older head or at a concurrent one counts at its own head, and from the end's head on it is not in force. The end never undoes that count. An act at a later head finds the standing ended and does not count. Where the ender holds a clean receipt of such an act concurrent with the end, the act counts at its own head, and is not in force ([CC 2.7.7](#2.7.7) rule 6).

*What stays in force.* A receipt keeps in force only an act that counts: one at the end's head, an older head or a concurrent one. Such an act stays in force after the end where a clean receipt of it is held that does not have the end in its past ([CC 2.7.5](#2.7.5)). The receipt is the conferrer's, another holder's of the body the act was done for, or that of a receipter the offer names in `receipter`. It is never the act's own signer's and never a node's. A count that ends a standing MAY state `lifts`, and then only the count's own receipts keep an act in force. An end by the one whose standing it is lifts nothing: a withdrawal of one's own acceptance, or a resignation. `lifts` on such an end is refused, `lifts_on_own_end`. A conferrer that ends its own offer MAY lift. A receipter's role ends with the offer that names it, and a receipt that has that end in its past keeps nothing. So a body does not stop one receipter and leave the grant standing: it ends the offer and offers again, or it ends by a count with `lifts`. A receipt changes what is in force, never what counted, and it revives no act.

*Another standing.* An act that another live standing of its signer authorises at its head stands on that standing. So one grantor's end does not reach what another still consents to.

*The limit.* A device that has not seen the end may sign an act at an older head. That act counts there and is never in force after the end. No reader can tell it from an honest earlier act, and no rule here tries. Where the record is one row, an act from such a device counts at that row and is never in force after the end.

A node MUST admit a `withdraws` against a target row `T` when one line of this table holds. It MUST also admit the key a `retirement:decided` row names in `decided_by`, against that row ([CC 7.5.5](part_7_lifecycle_stewardship.md#7.5.5)). It MUST refuse any other with `federation_withdraws_not_admitted`.

| Rule | Who signs the withdrawal | Condition |
|---|---|---|
| 0 | the quorum of `T`'s family | `T` carries `additional_scrubs[]` ([CC 2.4](#2.4)). The withdrawal is cosigned under the same `consensus_protocol`, counted over the members at the roster head the withdrawal names ([CC 2.7.4](#2.7.4)). Rules 1 to 4 do not reach `T`: a quorum's act is undone only by a quorum. |
| 1 | the key that signed `T` (`T.attesting_key_id`) | none |
| 2 | a key `T` names in `subject_key_ids` | `T`'s family is not on the kept list |
| 3 | a proxy for a party `T` names by canonical hash | the proxy holds a live `delegates_to` chain to that hash whose scope includes `consent_revocation`, and `T`'s family is not on the kept list |
| 4 | a delegate of anyone in rules 1 to 3 | the delegate holds a live `delegates_to` from them, and the kept list binds the delegate as it binds them |

**Any one named party is enough.** Where `T` names several parties, an admitted withdrawal from one retires `T` for all of them, since any bound voice ends a relation alone ([CC 2.7.5](#2.7.5)). A reader MUST NOT wait for a majority or for the others ([CC 4.4.3.29](part_4_composition_governance.md#4.4.3.29)).

**A withdrawal reaches forward only.** Acts the withdrawal has among its ancestors still stand. A copy a peer took before the withdrawal reached it is not recalled by the wire. One case reaches behind: a key revoked as compromised is void back to its `revoked_after` bound, stated below.

**The kept list (the anti-Goodhart retraction dual).** A named party acting under rules 2 to 4 MUST NOT withdraw these rows about itself:

- a `capacity:*` or `detection:*` finding made by someone else;
- a `licensure:*` or `revocation:*` row, where the licensee's path is `reconsideration:{grounds}`;
- a duty-holder's record on the accountability trail: a `moderation:*` report or action, a `moderation_track_record:*`, a `hard_case:*`, a `slashing:*` verdict, a `quarantine:*` marker ([CC 4.5.5](part_4_composition_governance.md#4.5.5));
- an act of a body under a declared legal-weight class, such as a conviction or a licence ([CC 2.4.1.3](#2.4.1.3), [CC 4.4.3.12](part_4_composition_governance.md#4.4.3.12));
- a `takedown_notice:*`, where the path is the counter-notice its basis names ([CC 3.3.2](part_3_the_namespace.md#3.3.2));
- a producer's own `trace:*`, where the path of a person named in it is withdrawing consent ([CC 3.1.5](part_3_the_namespace.md#3.1.5)).

An affiliation withdraws no statement about itself, whatever the statement. Its path is reconsideration and the reader's composition. The test is the row's subject: where it is an affiliation's own id, nobody acting for that affiliation withdraws the row under rules 2 to 4.

*An act under a declared class.* A row is such an act where three things hold. Its emitter resolves to the body at the head the row names. The row carries `class`. The body's record declares that class with `legal_weight` true ([CC 4.4.3.12](part_4_composition_governance.md#4.4.3.12)). A row with no `class` is under no class. Where the record that decides either test is not held, the withdrawal waits ([CC 2.7.3](#2.7.3)).

*A trace.* Only the key that signed a trace withdraws it under rule 1. Its owner does not, since the trace is the record of what that key did ([CC 3.1.5](part_3_the_namespace.md#3.1.5)). A named party contests a kept row by `reconsideration:{grounds}`, and it holds standing there ([CC 4.5.5](part_4_composition_governance.md#4.5.5)). The consent and scoring context of this list is [CC 3.4.5](part_3_the_namespace.md#3.4.5).

**Why the list exists.** Consent can be taken back, so a named party may retire a row about itself. A finding is not consent. A party that could retire the adverse rows about itself and keep the rest would launder its reputation.

**Between peers the person named retracts.** A `withdraws` of peer speech about oneself is admitted under rule 2. It is a signed act the row's audience sees, and it leaves the speaker attributed.

**Never withdrawn.** A `key:revocation:v1` row is withdrawn by nobody, because revocation is non-rollbackable ([CC 3.1.1](part_3_the_namespace.md#3.1.1)). An entity revocation ([CC 3.1.1](part_3_the_namespace.md#3.1.1)), an occurrence revocation, a key grant, a cosignature already sent and a receipt are never withdrawn either ([CC 3.1.3](part_3_the_namespace.md#3.1.3)). A receipt taken back would let a later row change what an act counted for. One key's mistaken receipt is met by the count's end with `lifts` or by the removal of that key. A count that receipted by mistake has no undo here, and it decides on the act anew.

**The proxy of rule 3.** Rule 3 serves a party that holds no federation key: a platform user id, an entity bound by a content hash, any other outside party. A federation-key signer, typically the agent that holds data for that party, emits `delegates_to(canonical_hash → agent_key, scope: [consent_revocation])` when the proxy is set up. Its later `withdraws` against a row carrying that hash in `subject_key_ids` is admitted under rule 3, on the conditions of [CC 3.3.14](part_3_the_namespace.md#3.3.14). The proxy attaches only after the party's identity is established out of band, reaches no row on the kept list above, and is suspended while two bindings for the same person compete. The hash is the tagged `canonical:{hashalg}:{hex}` wire form with the `{platform}:{entity_kind}:{id}` preimage convention of [CC 2.3.2.1](#2.3.2.1). A `canonical_binding` is a different act: a retroactive identity claim that consumers weigh. Rule 2 opens only for a row that names the bound real `key_id`, never by the binding alone. It is not an admission rule ([CC 2.3.2.2](#2.3.2.2)).

**Only the signer recants.** A `recants` row says `T` was false, and only `T`'s signer may say so. A named party who holds the claim factually wrong answers with a `scores` row of negative polarity on a contradicting dimension. A named party's authority covers consent, which can be taken back. It does not cover truth.

**Which rule admitted it.** A substrate SHOULD record which rule (0 to 4) admitted each `withdraws` in `federation_attestations` metadata. A consumer can then compose policy on it, for example weighing a named party's own withdrawal above a proxy's.

**What the signer keeps (normative).** A named party's withdrawal takes the row out of every audience. It does not take the signer's words from the signer. The signer MAY keep the withdrawn row and its `withdraws` together at `cohort_scope` `self`. A node MUST NOT serve that copy to anyone, the row's former audience included, and the copy counts toward no score, standing or grant. The keep covers a signer's own words about another party, and it gives way to every duty to delete. A signer that committed to a deletion window deletes within it and keeps no copy ([CC 3.3.1](part_3_the_namespace.md#3.3.1), D1). An affiliation holds the row only as the retention and erasure limbs of its record allow ([CC 4.4.3.12](part_4_composition_governance.md#4.4.3.12)). A signer running a decay protocol on the named party's data follows its stages ([CC 4.4.3.26](part_4_composition_governance.md#4.4.3.26)). The signer MAY hand the pair to a party that holds a duty to judge it. Filed with a room's named moderator it is a duty-holder's record ([CC 4.5.5](part_4_composition_governance.md#4.5.5)). Given to a body acting under a declared legal-weight class it is evidence before that body ([CC 4.4.3.12](part_4_composition_governance.md#4.4.3.12)). Saying the same thing again to the audience is a new row, and the party it names may withdraw that one in turn. Shown to its former audience beside the retraction, the row would be read by everyone who read it before, and the retraction would be a label. Deleted from its signer as well, the retraction would take the signer's own words. The retention rule carries this copy as a declared gate ([CC 6.1.5](part_6_the_coherence_mathematics.md#6.1.5) N5).

**What a named party keeps (normative).** The keep is the same for the party a row is about. Where a row's signer withdraws it, a party the row names who held it MAY keep the row and its `withdraws` together at `cohort_scope` `self`. The same limits bind that copy: a node serves it to no one, it counts toward no score, standing or grant, and it gives way to every duty to delete. The party MAY hand the pair to a party that holds a duty to judge it, as the signer may. So words that wronged someone are not unmade for the one they wronged by their author's taking them back. The withdrawal reaches the row's audience, the named party among them, so the party knows the row was withdrawn.

**`revoked_after` — the revocation history bound (normative, optional member).** A key-plane revocation MAY declare `revoked_after`, an instant of [CC 2.6.2](#2.6.2). It is a bound before which statements signed by the revoked key **still stand**: everything after the bound is suspect, and everything before it is not unmade. Resolution is a **pure read-time function**: a claim signed by K is valid iff its `asserted_at` precedes `K.revoked_after`. So a partitioned node converges when the revocation arrives late. Absent member = revoke-all. **`revoked_after` is an upper bound, not a fact**: a compromise may long predate its detection. A later revocation MAY lower it and MUST NOT raise it. Where a key carries multiple revocations the effective bound is the **minimum** `revoked_after` across all of them, absent-member sorting as negative infinity. That keeps the fold commutative and the resolution a pure read-time function, so partitioned convergence is preserved ([CC 3.2](part_3_the_namespace.md#3.2)). One count stands outside the bound: a bound on a holder's key never unmakes the first bundle of a lineage ([CC 2.6.1.11](#2.6.1.11)).

**A key revocation names its subject by the key's thumbprint, not its label (normative).** A key's label is the holder's own keystore alias in cleartext. Revocations replicate federation-wide, so a revocation addressed by label would tell every node the subject's label — `frank-laptop` — whether or not that node held the key's record. The revocation is a `key:revocation:v1` row ([CC 3.1.3](part_3_the_namespace.md#3.1.3)), never withdrawn, signed as every row is ([CC 2.6.1](#2.6.1)). Its subject is its `sub`: the revoked key's identity reference ([CC 2.6.1.1](#2.6.1.1)), stable for the life of the key and carrying no label. An optional member it leaves unset is absent, never null ([CC 2.6.1.2](#2.6.1.2)). A revocation of the earlier form is [CC 8.11.13](part_8_appendices.md#8.11.13). Three consequences follow. **(1) A revocation may precede the record it revokes**: one naming a key the receiver does not hold MAY be admitted, and takes effect the moment that key is held. Authority on this plane is the revoker's and is judged without the subject's record. **(2) Readers ask by thumbprint**: "is key K revoked?" is answered over K's thumbprint, so one revocation reaches every `key_id` that displays the same key. The per-subject anti-rollback ordering ([CC 5.3.2.3](part_5_transport_substrate.md#5.3.2.3)) keys on the subject. **(3) Self-revocation** is recognised when the revoker's own key is the subject. A `moderation:*` score MAY likewise name its subject key by its identity reference instead of exposing its label. Family and community rosters list members by `key_id`, so a roster's holders see the labels, and roster-removal rows are addressed by `key_id` — they reach only the audience that already holds the roster. Its signature rule is the key record's.

**Who may revoke a key (normative).** Three may revoke a key, and no other. The key revokes itself. Its owner revokes it under the owner-binding ([CC 3.2](part_3_the_namespace.md#3.2)), and that ends the owner-binding's standing. The roster that seats it revokes it by its count, and that ends the seat: the eviction door of a self roster ([CC 3.3.6.4](part_3_the_namespace.md#3.3.6.4)), and for a room key the room's removal ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). Only the key's own revocation ends its liveness, and neither of the others does ([CC 2.7.5](#2.7.5)). A key is its owner's, so ending it without the owner is a cut, and a cut takes standing ([CC 2.7.7](#2.7.7)). A revocation signed by any other key revokes nothing: it concludes nothing, `key_revocation_no_standing`.

**A key's own end (normative).** A `key:record`'s `identity_type` is a set of roles ([CC 3.4.7.1](part_3_the_namespace.md#3.4.7.1)). A set that holds `user` or `accord_holder` together with `node` or `agent` is malformed and refused, since a key is a person's or a machine's, never both. A `key:record` whose `identity_type` contains `user` or `accord_holder` MUST NOT state `valid_until`, since no person loses their self to a clock. Any other `key:record` whose `identity_type` contains `node` or `agent` MUST state `valid_until`, unless it is a room key of a private room ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). A room key's record is one that carries `room`, the id of its one room. A pseudonym's key record ([CC 5.4.6](part_5_transport_substrate.md#5.4.6)) MAY state `valid_until` and need not, since it is neither a self nor a node or agent. A role outside both groups, such as a steward, a witness or a pipeline, takes no end rule of its own. The bound is read from the record alone. `valid_until` MUST be later than the record's `asserted_at`, and no more than `key_record_max_secs` after it. A record that breaks the bound, or omits or carries `valid_until` against this paragraph, is refused `key_record_out_of_window`. A statement of this form is signed by a composite key, and that key is live only by a `key:record` of this form. A key record of the earlier form ([CC 8.11](part_8_appendices.md#8.11)) gives standing to nothing ([CC 2.6.1.12](#2.6.1.12)). Each key's own holder signs its record of this form, so the genesis ends no key and gives no key a power over another. A key is live at an instant when one of its records covers that instant and its own revocation has not taken effect by then ([CC 2.7.5](#2.7.5)). It has ended when every one of its records has ended. No other row enters that reading, so no third party ends a key and no third party revives one.

A key renews by signing a further record that `supersedes` its own earlier record. Renewals that do not name each other all count, and the key lives to the greatest end they state. A renewal MAY be signed after the end of the record it supersedes, and it then revives the key at every node that holds it. A rotation is a record of another key that names the old key's record, in the one shape of the `key:record` row of [CC 3.1.3](part_3_the_namespace.md#3.1.3). It carries the old key's signature, made at an instant that record covers: at or after its `asserted_at` and before its `valid_until` ([CC 2.6.2](#2.6.2)). A rotation hands on what the old key may hand on, and never extends the old key. Two rotations of one key, neither naming the other, hand on nothing until a rotation names both ([CC 2.7.7](#2.7.7)). A rotation is such a rival only where it names a valid record of the old key that covers its own instant, so one that does not blocks nothing. The owner of the key settles the pair's ownership by binding one successor and revoking the other's binding; the hand-on stays empty until a rotation names both. A key with no owner stays contested.

A row lapses when its signer's key has ended and no row that has not lapsed names it, directly or through other rows ([CC 2.7.5](#2.7.5)). A revocation never lapses. A lapsed row MUST NOT count in any tally, score, walk of trust or other reading. Its own verdict is unchanged: a row signed while its key was live stays what it was. A row that has not lapsed counts as before, whatever its key's end. A node MAY stop serving a lapsed row and MAY drop it. A node MUST NOT stop serving or drop, for its key's end, a row that has not lapsed; [CC 2.7.10](#2.7.10) states when it MAY drop a row's bytes. It MUST NOT keep a digest by which to refuse a dropped row again. A row whose signed instant no held record of its key covers is retryable, as a row signed by a key not yet held is.

A signer's instants are its own word. Whoever holds an ended key's private half can revive it with a further record, and no reader can tell when that record was signed. Only a key's own revocation makes its end final ([CC 2.7.9](#2.7.9)). A key made for one task MAY revoke itself at its end; that revocation is never withdrawn and is kept. An implementation SHOULD state the greatest end the bound allows. A key made for one task SHOULD state an end that fits that task.

**A purge is a tombstone, not a `withdraws` (normative).** Rules 0–4 are consent paths — the author's or the subject's. A row the purger neither authored nor is the subject of (a mock-LLM trace, a harness identity's rows, a row no peer can verify) is removed by a **tombstone by digest on its plane**. The tombstone is authorised by a cosigned `takedown_notice` under the trust root's `consensus_protocol` with basis `steward_purge` ([CC 3.3.2](part_3_the_namespace.md#3.3.2)), naming the selection digest, the reason and the ledger. A substrate MUST NOT admit a `withdraws` forged on the author's behalf for this. A `withdraws` does not even claim falsity, and a purge says the row never belonged. **A purge never tombstones or deletes a key.** A selection naming a `federation_keys` row concludes nothing, and a by-actor selection takes the actor's own rows and their derived rows. Key retirement is a separate `key:revocation:v1` signed under this section's own paths. The root's quorum has no path over a key it does not own: a root that could revoke strangers' keys would be an authority roster by another name ([CC 3.4.7](part_3_the_namespace.md#3.4.7)). So an ownerless key stays registered and inert while its rows go, and the admission gates stop its next ones. A key's own end is not a purge. A `node` or `agent` key ends by its own record, and its rows lapse by the rule of its own end above, by no third party's act. Entities go by `revocation:{entity_type}:{reason}`, bytes by the bytes-plane tombstone ([CC 4.5.3](part_4_composition_governance.md#4.5.3)). **The accountability record is outside the root's reach.** `revocation:*`, `key:revocation:v1`, `moderation:*`, `moderation_track_record:*`, `slashing:*` and **`hard_case:*`** rows are never purgeable, by the root or by anyone. Trust-root moderation is not trust-root history-editing. `hard_case:*` is in the set because an equivocation proof (`hard_case:lineage_equivocation`, [CC 6.1.1](part_6_the_coherence_mathematics.md#6.1.1) N4) or a liveness transition (`community_liveness_stalled` / `_restored`, [CC 3.2](part_3_the_namespace.md#3.2) T7) is an adverse row about a root. That root's only purge door is its own quorum, which is the subject, and the anti-Goodhart dual admits no subject-side removal of an adverse row. The substrate that produced the proof withdraws it under rule 1, or recants a false one, and nobody else. A structural composer (`withdraws`, `recants`, `supersedes`) is purged only together with its target, and a `delegates_to` only when a party to it is in the selection. A purge removes a party, never a third party's standing. **Derived rows follow the reason, and the selection digest says which.** A `scores` row whose evidence was never admissible input (mock, harness, unverifiable) is purged with its evidence, in the same selection and ledger: its subject never ran, so it attests nothing. So are a trace's own `trace:complete:v1` attestation and the bytes a purged holding claim holds, transitively over `evidence_refs`. A score over real evidence later taken down on a legal basis stands, its `evidence_refs` resolving to the tombstone. A tombstone waits for the notice it names (`purge_unauthorised` while it is not held). One whose selection digest differs from the notice's concludes nothing (`purge_selection_digest_mismatch`), and neither is executed; every purged id is appended to a ledger attested at the next tag.

#### 2.4.1.2 `delegates_to` — Authority-source claims via `delegates_to`

A constitutional or framework claim can name its source-of-authority by emitting `delegates_to` against an `attested_key_id` representing the framework, with `scope` naming the principle. Example: a Ubuntu-substrate commitment in [CC 1.13.1](part_1_foundation.md#1.13.1) commitment 2 can be expressed as `delegates_to` against the `ubuntu_relational_substrate` framework-key with `scope: ["personhood_constitutive_by_attestation"]`. Reuses the existing structural primitive rather than introducing a `grounding:{tradition}:{principle}` prefix (which would fail [CC 1.2](part_1_foundation.md#1.2) T2 — "tradition" claims are interpretive, not mechanism-descriptive).

**Owner-binding is the single-valued purpose.** A `delegates_to(user → node/agent)` carrying `delegation_purpose: owner_binding` is the owner-binding, held to the single-owner invariant ([CC 3.2](part_3_the_namespace.md#3.2), *Who owns a key*). This is the **one** `delegation_purpose` that is single-valued — act-on-behalf, hierarchy ([CC 4.5.13](part_4_composition_governance.md#4.5.13)), and authority-source delegations remain **multi-parent** DAGs.

**The family a `delegates_to` row names (normative).** A `delegates_to` row's family, its label -70002, is a registered family ([CC 2.6.1.3](#2.6.1.3)). What the row binds picks it:

| What the row binds | Its family |
|---|---|
| a capability delegation, a moderator's seat, a steward-binding | `self:delegates_to` |
| an owner-binding ([CC 3.2](part_3_the_namespace.md#3.2)) | `ownership:{relation}:{target_kind}:{version}` |
| a guardianship, an incapacity binding | `self:delegates_to`, told apart by `delegation_purpose` |
| an agent occurrence | `self:delegates_to:agent_occurrence` |
| a trust edge | `trust:{job}:{version}`, its dimension `trust:accepts:v1` or `trust:confers:v1` |

#### 2.4.1.3 `authority-triad` — Licensure, grant, delegation — three concepts, three wire discriminators (normative)

`delegates_to` is one of three ways a key comes to hold something. The three are routinely conflated because only one of them has a structural primitive. Two of them run through different machinery: licence authority rides the [CC 3.2](part_3_the_namespace.md#3.2) founder-quorum machinery, and role authority rides the [CC 4.4.3.19](part_4_composition_governance.md#4.4.3.19) delegation scopes ([CC 3.3.9](part_3_the_namespace.md#3.3.9)). The triad is stated here, at the grammar.

| | **Licensure** | **Grant** | **Delegation** |
|---|---|---|---|
| who gives it | an **authority** | the asset's **owner / steward** | a **principal** |
| what it confers | standing to practise | access to a specific thing | agency to act *for* someone |
| what it is about | the subject | the asset (hash, stream, balance) | the principal's own powers |
| ends by | the authority revokes / suspends | rotation, expiry, exhaustion | the principal withdraws; attenuation |
| **chains?** | **no** | **no** | **yes** — attenuated, depth-capped, revocable per link |
| wire discriminator | dimension prefix on `scores`: `licensure:{authority_id}` / `attestation:license_validity` | dimension prefix on `scores`: `key_grant:{axis}:v1` ([CC 3.3.2](part_3_the_namespace.md#3.3.2)), or the `consent:scope:*` family | **structural primitive**: `attestation_type: delegates_to` |

**The transitivity row is the discriminator of record.** Only delegation composes. That is why only `delegates_to` gets a graph walk ([CC 4.1.1](part_4_composition_governance.md#4.1.1) depth cap, a cycle visited once, aggregate-weight cap). A licence does not chain: holding one confers no power to issue one. A grant does not chain: receiving access confers no power to re-grant it (below). Any design that walks a licence or a grant transitively has mistaken it for a delegation.

The professional analogue is exact, and it is the domain this federation licenses. A physician assistant holds a **licence** from a board, practises under a supervising physician's **delegated** authority, and holds **privileges** (a grant) at one hospital for named procedures. These are three grantors and three revocation paths, reported as separate categories by the registries that track them.

**Provenance is the authority, not a delegation (normative).** A licence's provenance is its **`authority_id`**, carried inside the dimension. Where the authority is a collective it is constituted by **quorum** ([CC 3.3.9](part_3_the_namespace.md#3.3.9) / [CC 3.2](part_3_the_namespace.md#3.2) founder-quorum). It is **never** conferred by `delegates_to`. Three things stay distinct:

- *who grants the licence* (the `authority_id`);
- *who vouches for the attester* (the trust walk, `infra:attest`);
- *what external legal force it carries* (a **bridge** on an in-grammar record — [CC 8.3](part_8_appendices.md#8.3): bridges compose with the record, they are never alternatives to it).

**Who may be a licensing authority, and what admits a licence (normative).** Anyone. `authority_id` names a key: a `federation_keys.key_id`, or an organisation, an affiliation whose keys resolve through its `membership:{stage}` seats on the community record and the `delegates_to` edges of its hierarchy ([CC 4.4.3.12](part_4_composition_governance.md#4.4.3.12), [CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). The words "X holds licence authority for `A`" mean exactly that X's key *is* `A`, or holds a `license`-scoped delegation whose chain resolves to `A` ([CC 4.4.3.19](part_4_composition_governance.md#4.4.3.19)). There is no roster of permitted authorities and a substrate checks none. A `licensure:{A}` row admits under the same gate as every other row on the wire. The gate is that the reader trusts the emitter's root or has consented to receive from it ([CC 4.4.3.34](part_4_composition_governance.md#4.4.3.34); the contextual-integrity rule: a medical licensure claim reaches a reader only along a flow that reader's trust or consent admits). The row reaches nobody else. Per [CC 4.4.4](part_4_composition_governance.md#4.4.4) a Sovereign key scoring `licensure:CA_medical_board` is wire-identical to a Registry steward scoring it; consumer policy weights by attester. The provenance paragraph above says "by quorum". That is a statement about the authority's *own* governance where it is a collective: the [CC 3.2](part_3_the_namespace.md#3.2) founder quorum that constitutes a community's key, the [CC 3.3.9](part_3_the_namespace.md#3.3.9) M-of-N write rule under which an affiliation issues a licence. That statement is never an admission gate a substrate applies to somebody else's authority.

**What the fold keys on (normative).** The `licensure:{A}` status set for a subject folds only rows whose emitter resolves to `A`: `A`'s key, or a `license` chain to `A`. A row under `licensure:{A}` signed by a key that is neither `A` nor `A`'s delegate is admitted if trusted or consented to. Such a row is *testimony about* `A`'s licensure, not `A`'s licensure: it stays out of the `(subject, A)` fold and composes at consumer confidence. That is how a stranger's absorbing `revoked` binds nobody. The one failure on the `license` scope itself is an issuance whose delegator chain does not resolve to `A`: it concludes nothing, reason **`licensure_delegator_not_authority`**, and waits where a link is not held. There is no bootstrap: `A`'s first `licensure:{A}` row is signed by `A`, or, for a keyless affiliation, cosigned by its quorum.

*Authority is judged at issuance.* It is judged over the issuance's own causal past under the cosigned-row rule, never at receipt, because this is a shared verdict every node has to compute identically. A `withdraws` of a link in the chain stops every issuance that has it in its own past. An issuance concurrent with it counts at its own head and is not in force from the withdrawal's head on ([CC 2.4.1.1](#2.4.1.1), [CC 2.7.7](#2.7.7)). It does **not** reclassify licences the withdrawal has among its ancestors. The authority ends those with `suspended` or `revoked`.

*A licence has no public default.* It is a claim about a person, so its `cohort_scope` is the authority's declared choice *per licence class* in the affiliation's charter, the smallest that fits ([CC 1.13.3.4](part_1_foundation.md#1.13.3.4)). A practice licence meant to be checked by strangers is federation-scope by its nature; an internal credential is not. At whatever scope the class declares, the licence and the **authority head** a verifier needs (the roster version, the protocol, the `license` edges on the chain) travel together. Where the class is not public they are **re-emitted** to the readers who validate them, never carried at the wrong scope (`cohort_scope` is in the signed bytes) and never by widening the roster. They are re-emitted as new rows, signed and cosigned again, each addressed to one reader by `for_key_id` and naming no reader in `subject_key_ids`.

*An organisation-named authority.* An organisation is an **affiliation** ([CC 4.4.3.12](part_4_composition_governance.md#4.4.3.12)), and an organisation-named authority is its `community_key_id`. Its authority set is whatever the affiliation's *current* `consensus_protocol` admits. A `licensure:{community_key_id}` row is a **cosigned row** ([CC 2.4](#2.4)) whose protocol source is the authority named in the dimension. That is the one case where the source is neither the group the row is about nor the accord. A `license`-scoped chain roots at that quorum; one founder suffices only where the protocol says so.

**A grant is non-transferable by default (normative).** A `key_grant` conveys access to an asset; it does **not** convey the power to convey it. An onward grant is a **new grant issued by the asset's owner or steward, or by a holder of a `grant`-scoped delegation from them** ([CC 4.4.3.19](part_4_composition_governance.md#4.4.3.19)), never a forwarded one. `rotation_chain` is supersession lineage, not onward transfer. **Possession of the data-encryption key is not issuance authority.** Every recipient necessarily holds the DEK, having unwrapped `wrapped_dek`. So the ability to wrap a new grant is *necessary* and never *sufficient*: the cryptographic gate stops a stranger, and only the authority gate stops a recipient. A `key_grant` whose issuer neither owns or stewards the asset nor holds a `grant`-scoped delegation over it concludes nothing, as an issuance does whose delegator lacks the authority. A design that treats receipt of a grant, or possession of its key, as authority to re-grant has, again, mistaken a grant for a delegation.

#### 2.4.1.4 `recants` — The `recants` distinction matters

CEG types epistemic-error-admission as a wire primitive distinct from retraction, because the Recursive Golden Rule applies to attesters: admitting error is a primary act, not a derivative of retraction. Consumer policy can apply different trust adjustments to attesters who `recant` versus those who `withdraw`.

### 2.4.2 `scores` — The workhorse: `scores`

The federation has exactly **one** workhorse attestation primitive. Every claim about an entity — positive or negative, identity or capability or behavior or state or commitment, by any attester source — is expressed as a `scores` attestation on a named dimension.

Illustration of the logical view, not canonical bytes: the names are the logical names of [CC 2.6.1.4](#2.6.1.4), `attestation_envelope` is the payload, and an optional member is omitted, never null.

```
// Logical view (the names of CC 2.6.1.4):
attestation_type: "scores"
attesting_key_id: <attester's key_id>
attested_key_id: <subject's key_id>
attestation_envelope: {
  "dimension": "<canonical-namespace-prefix>:<scoped-leaf>",
  "cohort_scope": "<self | family | community | affiliations | species | biosphere | federation>", // REQUIRED, no wire default
  "score": <integer ∈ [-10^6, 10^6], CC 2.6.1.5>,
  "confidence": <integer ∈ [0, 10^6], CC 2.6.1.5>,
  "context": "<free-form scoping detail>",
  "evidence_refs": [<content hash of backing evidence, bytes>,...],
  "valid_until": <instant, CC 2.6.2, optional>,
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

### 2.6.1 `signed-object-cose` — The signed object: deterministic CBOR and COSE

This rule closes the canonical-bytes ambiguity. A row carries optional members with documented defaults, among them `epistemic_mode`, `witness_relation`, `oversight_mode`, `subject_key_ids` and `community_id`. Two honest peers that encode one value two ways disagree on the bytes, and a valid signature then fails to verify.

**The hazard is structural.** Suppose a producer omits an optional member, relying on its [CC 2.1](#2.1) default, and a relay re-encodes the row with the default written in. The bytes then differ and the signature fails. So every party — producer, substrate, relay and consumer — makes one choice: preserve what the producer signed, exactly ([CC 2.6.1.2](#2.6.1.2)).

**The object (normative).** A row's signed object is a CBOR payload ([RFC-8949]) in the deterministic encoding, signed with COSE ([RFC-9052]). Each voice of a row signs it as one `COSE_Sign1`. The form follows the transparency architecture of [RFC-9943], with COSE receipts ([RFC-9942]) and ML-DSA in COSE ([RFC-9964]). The statement, its encoding, its name, its members and its signature are [CC 2.6.1.1](#2.6.1.1) to [CC 2.6.1.11](#2.6.1.11). The earlier JSON object is [CC 8.11](part_8_appendices.md#8.11), and no node of this edition reads it ([CC 2.6.1.12](#2.6.1.12)).

#### 2.6.1.1 `statement` — The statement (normative)

A **statement** is one `COSE_Sign1` under CBOR tag 18, made by one signer. A row is one statement, or several over one payload where the row is counted ([CC 2.6.1.9](#2.6.1.9)). The protected header of a row carries exactly seven members, and the signature covers all of them:

- `alg` (label 1): `-70100`, the composite algorithm of [CC 2.6.1.7](#2.6.1.7).
- `cty` (label 3): the content type `application/vnd.ciris.row+cbor`, with no parameters.
- `kid` (label 4): the 32-byte thumbprint of the key that signs ([CC 2.6.1.7](#2.6.1.7)).
- the CWT claims (label 15, [RFC-9597]): `iss`, `sub`, `iat`, `nbf` and `exp` where the row has them, and the edition claim (label -70003), whose value is 2.
- `typ` (label 16, [RFC-9596]): `ceg-row/2`.
- the row's type (label -70001): one of the five row types ([CC 2.4](#2.4)), as a text string.
- the row's family (label -70002): its family id, as a text string.

A verifier MUST refuse a row whose `cty` carries parameters, or whose protected header lacks the type or the family label. A signed object that is not a row carries neither label, and one that does is refused. `sub` names what the row is about: the attested key, or the object the row refers to.

**The family id.** The family label carries a family id, never a leaf. A family id is the family's registry prefix ([CC 3.1](part_3_the_namespace.md#3.1)) with each `{name}` segment written `.name` and each `*` written `.`, such as `key:record` or `provenance:build_manifest:.target`. A literal segment never begins with `.`, so no two prefixes share a family id. A row that scores a dimension carries it whole, leaf and version, in the payload member `dimension`. A verifier MUST refuse a `dimension` that does not resolve to the family id the header carries. A `withdraws` or a `recants` carries the family id of its target and no `dimension`, and its `sub` is its target's. A `supersedes` is a row of its own family and carries its own.

**Identity references.** `iss` is the signer's stable identity reference: the COSE key thumbprint URI of [RFC-9679] (its section 5.7) for the signer's genesis key. It is `urn:ietf:params:oauth:ckt:sha-256:` followed by the unpadded base64url of the 32-byte thumbprint: 43 characters, the last with zero trailing bits. `author`, a key named by `sub` or by an element of `subject_key_ids`, and every role party ([CC 2.6.1.3](#2.6.1.3)) use this one spelling. A verifier MUST refuse any other. A dimension segment that names a key carries the bare thumbprint, the reference less its prefix, since a dimension is colon-delimited ([CC 3.1.7](part_3_the_namespace.md#3.1.7)).

`external_aad` is the empty byte string, and no party puts a domain prefix there. A statement's kind is its `typ`, and a row's type and family are its labels -70001 and -70002. The unprotected header is outside the signature. No admission check reads it; a holder may add a receipt there, or present a disclosure there ([CC 2.6.1.10](#2.6.1.10), [CC 2.6.1.11](#2.6.1.11)). A host's receipt check reads a receipt there before it runs admitted code, and the receipt grants nothing ([CC 2.7.11](#2.7.11)).

This form has no mirror of the row inside the bytes and no cosignature beside them. The protected header and the payload are the row, and a further voice is a further statement.

#### 2.6.1.2 `deterministic-encoding` — Deterministic encoding and the omit rule (normative)

The payload is encoded in CBOR's deterministic encoding ([CDE]). A verifier MUST refuse a payload whose bytes differ from the deterministic re-encoding of the value they decode to. That covers a non-shortest integer, an indefinite length, an unsorted map key and a duplicate key. A second encoding of one value would otherwise be a second row. A verifier verifies the bytes it received, never a re-encoding of members it decoded.

The protected header is in the deterministic encoding too. It carries exactly the members of [CC 2.6.1.1](#2.6.1.1), or of [CC 2.6.1.11](#2.6.1.11) for a signed object that is not a row. A verifier MUST refuse any other, so one statement has one statement id.

**The omit rule.** The bytes are the members the producer signs. An optional member the producer omits MUST NOT be written into the payload by any party. An optional member the producer emits, even at its default, MUST be kept by every party. Documented defaults ([CC 2.1](#2.1)) are read at interpretation time, never written at encoding time. An optional member is unset by absence, never by null. A payload with null for an optional member is refused `federation_malformed_row` with reason `envelope_member_null`. This form has no exception: a key revocation is a row like any other. No value a family names, at any depth, is a float, a null, an undefined value, a tag or a simple value, except the redaction marks of [CC 2.6.1.10](#2.6.1.10) and the decimal fractions below. A free-form body states an integral number as a plain integer, and any other as tag 4, `[exponent, mantissa]`, normalised: a negative exponent and a mantissa not divisible by 10. It is the source number's exact decimal, never read through binary64. A mantissa outside CBOR's integer range, −2^64 to 2^64−1, is refused, `body_number_unrepresentable`. A tag-4 value that is not normalised is a second encoding of one value, refused at step 3 of [CC 2.6.1.8](#2.6.1.8). A fixed-scale member stays fixed6 ([CC 2.6.1.5](#2.6.1.5)).

**Relays.** A substrate, relay or consumer that stores or forwards a statement MUST forward the octets it received. It never strips an emitted default and never writes in an omitted one. Unknown members are kept the same way ([CC 2.1.1](#2.1.1)).

**Sets and sequences.** An array whose positions the schema names is a **tuple**, and its order is its definition. An array of one element type is a set or a sequence, as its definition states; where no definition says, it is a set. The sequences are the redacted-key arrays of [CC 2.6.1.10](#2.6.1.10), `evidence_refs`, the `chain` of a key record's `attestation_evidence` ([CC 4.2.2.1](part_4_composition_governance.md#4.2.2.1)), and the `aspects[]` of a `transport_destination` ([CC 4.4.3.20](part_4_composition_governance.md#4.4.3.20)). Those aspects, in order, are part of the name its destination hash is derived from ([CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3)). A set is sorted by the bytewise order of its elements' deterministic encodings and holds no duplicate. A verifier refuses any other with `federation_set_semantics_unsorted`, naming the member, and never re-sorts it. A sequence keeps its authored order, as `evidence_refs` does.

**Bytes and text.** A byte member is a CBOR byte string; hex and base64 do not stand in the payload for bytes. `subject_key_ids` is the one two-form member. An element naming a registered key carries that key's identity reference ([CC 2.6.1.1](#2.6.1.1)). An element naming a canonical-hash subject, as an un-enrolled subject is named, is the tagged text `canonical:{hashalg}:{hex}` that [CC 2.3.2.1](#2.3.2.1) requires. An implementer who strips the tag produces other bytes and a signature that silently fails.

With the deterministic encoding, the omit rule, set order, byte strings and integer instants ([CC 2.6.2](#2.6.2)), byte identity across conforming implementations is closed by construction.

**The attack the rule closes.** Alice signs a row that omits `epistemic_mode`. Bob's relay decodes it, writes in the default `direct` and re-encodes it for Carol. Carol's verifier refuses the bytes, and she cannot tell a malicious relay from a helpful one. Under the rule Bob forwards the octets he received, Carol's verifier accepts them, and Carol applies the default after verification.

#### 2.6.1.3 `row-id` — The row id and what a row names (normative)

A row is named by one digest, its **row id**. It is SHA-256 over the deterministic encoding of the array `["CEG-row/2", type, family, sub, author, payload]`, written as `[-16, digest]`. `type` and `family` are the text strings of labels -70001 and -70002, `sub` is the CWT subject, and `author` is the payload's author or null. `payload` enters as the byte string signed, never as the decoded map. A row whose content is low-entropy, such as a ballot or a census cell, carries a random `salt` of sixteen bytes in its payload, bound by every voice, so its row id confirms no guess.

Signatures, `kid`, `alg`, receipts and disclosures are outside the row id. So every voice of a counted row has the same row id, and it does not change when a voice, a receipt or a disclosure is added. The header's `iat`, `nbf` and `exp` are derived from payload members and checked against them ([CC 2.6.2](#2.6.2)), so the row id commits to them. The row id does not read `cty`.

A statement's own id is SHA-256 over the deterministic encoding of `["CEG-statement-id/2", protected, payload]`, written the same way. It names one voice, and the row id names the row. It is a name of this specification: [RFC-9943] defines no statement identifier. It leaves out the signature and the unprotected header, and `external_aad` is empty, so it selects the same statements as a reference to the statement's COSE `Sig_structure`. A match on an id says two parties name the same bytes, and nothing of who signed them.

**The author.** A family is authored or counted, as its family model states ([CC 3.1](part_3_the_namespace.md#3.1)). Its `authorship` cell says which, and its `second_signers` cell names each role below with the payload member that names its party. An authored family's payload carries `author`, the `iss` of the one who authors the row, and the row id reads it from the payload. A counted family's author is null. Where the cell reads `subject`, the row is authored by the attested key: `author` MUST be the CWT `sub`, and a statement whose `iss` is another key is Invalid. A statement whose `iss` is not the payload's `author` is accepted only in a role its family names, such as a delegate or a bound node. Its `iss` MUST then be the party that role names in the payload, or the CWT `sub` where that party is the attested key, as a delegate is. On an authored row its family counts, as an owner-binding an affiliation cosigns ([CC 3.2](part_3_the_namespace.md#3.2)), a voice of that count is accepted too. Any other `iss` is Invalid ([CC 2.6.1.8](#2.6.1.8)). The `act` a family model's selector reads is never a payload member. A reader derives it from the statements the row carries: `own` for one statement by the author, `group` for several statements over one payload, counted over the roster they name ([CC 2.6.1.9](#2.6.1.9)).

**What a row names.** Every row a row names stands in one payload member, `refs`, by row id. That covers a head (`head`, and `further_heads`), a predecessor (`prev`, and `further_prev`), the target of a withdrawal or a supersession, and every other row the row cites, such as `also` and `trusted_through`. A head is the one a count is over, an act is exercised at, or an end acts from ([CC 2.4.1.1](#2.4.1.1)). A holder reads the named set from `refs` alone, without knowing the family. The roles of `also` are a closed registry of five. `ack` names a row acknowledged, as a revocation snapshot and a receipt of acts do ([CC 2.6.1.11](#2.6.1.11), [CC 2.4.1.1](#2.4.1.1)). `under` names the one edge a deputy's edge hangs from, a set of exactly one ([CC 4.5.5](part_4_composition_governance.md#4.5.5)). `cites` names a row the row cites, as a build attestation names its manifest contribution ([CC 3.1.2.1](part_3_the_namespace.md#3.1.2.1)). `stands_on` names the one acceptance a row signed under a root grant stands on, a set of exactly one ([CC 2.4.1.1](#2.4.1.1)). `voice` names the head of the key roster of the voice a room key signs for, a set of exactly one ([CC 2.6.1.11](#2.6.1.11)). Any other role is a later registration. Every array inside `refs` is a set ([CC 2.6.1.2](#2.6.1.2)) and is refused otherwise. An empty `refs` is refused: absence is its one encoding.

**No row names the earlier form.** A `row-ref` names a signed object of this form, and no row of this form names an object of the earlier form ([CC 2.6.1.12](#2.6.1.12)). `original_content_hash` is not a member of this form ([CC 8.11](part_8_appendices.md#8.11)).

#### 2.6.1.4 `signed-object-members` — Members, placement and types (normative)

<!-- BEGIN GENERATED: signed_object_v2 -->

*This table is rendered from one data file and checked member for member against [`manifests/signed_object_v2.cddl`](../manifests/signed_object_v2.cddl), the schema, with the payload rules of [`manifests/family_payloads_v2.cddl`](../manifests/family_payloads_v2.cddl); the two never disagree.*

**Placement vocabulary.** `statement`: a position of the `COSE_Sign1` array. `header:protected`: the protected header, covered by the signature. `header:cwt`: a CWT claim inside the protected header. `header:unprotected`: never signed, and never read by a rule. `payload`: covered by the signature and by the row id. `payload:refs`: inside `refs`, the one member that names rows. `payload:body`: inside `body`. `derived`: computed by a verifier, never carried as such. `object`: a member of a signed object that is not a row. `none`: a logical name with no member of its own.

**Logical names.** The Parts name members by their logical names. The logical name of each member stands in the first column; a logical name with no member of its own stands in the last table, with what carries it.

**The statement: one `COSE_Sign1` per signer**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `protected` | statement | `bstr .cbor statement-protected` | always | [2.6.1.1](#2.6.1.1) [2.6.1.2](#2.6.1.2) | The protected header as bytes, in deterministic encoding and with exactly its seven members; the signature covers them. |
| — | `unprotected` | statement | `unprotected-header` | always | [2.6.1.1](#2.6.1.1) | Never signed; a rule never reads it. |
| — | `payload` | statement | `bstr .cbor attestation-envelope` | always | [2.6.1.1](#2.6.1.1) [2.6.1.2](#2.6.1.2) | The payload as bytes, in deterministic encoding; a payload that is not the deterministic re-encoding of the value it decodes to is refused. Never nil. |
| `scrub_signature_classical`, `scrub_signature_pqc` | `signature` | statement | `composite-signature` | always | [2.6.1.7](#2.6.1.7) | The composite ML-DSA-65 with Ed25519 signature, 3373 bytes; neither half verifies alone. |

**The protected header**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `1` | header:protected | `composite-alg` | always | [2.6.1.7](#2.6.1.7) | alg: -70100, the composite; a private-use identifier until one is assigned. |
| — | `3` | header:protected | `row-cty` | always | [2.6.1.1](#2.6.1.1) | cty: application/vnd.ciris.row+cbor, with no parameters; any other is refused. |
| `attestation_type` | `-70001` | header:protected | `row-type` | always | [2.6.1.1](#2.6.1.1) | The row's type, one of the five; refused on any object that is not a row. The row id reads it. |
| — | `-70002` | header:protected | `family-id` | always | [2.6.1.1](#2.6.1.1) | The row's family id, never a leaf; the payload's dimension MUST resolve to it. The row id reads it. |
| `attesting_key_id` | `4` | header:protected | `kid` | always | [2.6.1.7](#2.6.1.7) | kid: the 32-byte thumbprint of the signer's composite key, fixed for the key's life. |
| — | `15` | header:protected | `cwt-claims` | always | [2.6.1.1](#2.6.1.1) | The CWT claims. |
| — | `16` | header:protected | `"ceg-row/2"` | always | [2.6.1.1](#2.6.1.1) [2.6.1.11](#2.6.1.11) | typ: ceg-row/2 for every row. |

**The CWT claims (protected header, label 15)**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `1` | header:cwt | `identity-ref` | always | [2.6.1.1](#2.6.1.1) [2.6.1.7](#2.6.1.7) | iss: the signer's stable identity reference, the thumbprint URI of its genesis key; under a room key, the voice: the identity reference of the voice's first room key, never the person's. kid's key is a key of it. |
| `attested_key_id` | `2` | header:cwt | `tstr` | always | [2.6.1.1](#2.6.1.1) [2.6.1.3](#2.6.1.3) | sub: what the row is about; a key subject is an identity reference; the row id reads it. |
| — | `6` | header:cwt | `uint` | always | [2.6.2](#2.6.2) | iat: floor(asserted_at / 1000); a disagreement is refused. |
| — | `5` | header:cwt | `uint` | iff the payload carries valid_from | [2.6.2](#2.6.2) | nbf: floor(valid_from / 1000); a disagreement is refused. |
| — | `4` | header:cwt | `uint` | iff the payload carries valid_until | [2.6.2](#2.6.2) | exp: floor(valid_until / 1000); a disagreement is refused. |
| — | `-70003` | header:cwt | `2` | always | [2.6.1.1](#2.6.1.1) | edition: the constant 2. |

**The unprotected header**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `sd_claims` | `17` | header:unprotected | `[+ bstr .cbor sd-disclosure]` | when disclosures are presented beside the statement | [2.6.1.10](#2.6.1.10) | sd_claims of SD-CWT: disclosures as presented to one who may see them; they travel and are held as bytes, never in the row. |
| `receipts` | `394` | header:unprotected | `[* bstr]` | where a Transparency Service has registered the statement | [2.6.1.11](#2.6.1.11) [2.7.11](#2.7.11) | receipts of RFC 9942, never signed: each read by the host as a COSE receipt, a malformed one ignored; admitted code runs only once one from a service the host trusts is held. |

**The payload**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | iff the family is authored | [2.6.1.3](#2.6.1.3) [2.6.1.9](#2.6.1.9) | The iss of the author, read by the row id from the payload; in a private room, the voice. A counted family carries none, and its row id takes null. |
| `references_attestation_id` | `"refs"` | payload | `refs` | iff the row names a row | [2.6.1.3](#2.6.1.3) | Every row this row names, and the only member that names a row; never empty. |
| `dimension` | `"dimension"` | payload | `tstr` | where the family scores a dimension | [2.6.1.1](#2.6.1.1) | The full scored dimension, leaf and version; it resolves to the family id of label -70002, and is refused otherwise. |
| `evidence_refs` | `"evidence_refs"` | payload | `[+ hash-digest]` | where the row cites a blob | [2.6.1.6](#2.6.1.6) [2.6.1.2](#2.6.1.2) | The blobs the row cites, by content hash: a sequence, bytes never hex. |
| — | `"seat_commitment"` | payload | `hash-digest` | on the key record of a room key | [2.6.1.11](#2.6.1.11) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The commitment to the seat's person, which the binding opens. The seat row of a room key is its own key record, so a row carries one commitment. |
| `score` | `"score"` | payload | `fixed6-score` | where the family carries a score | [2.6.1.5](#2.6.1.5) | fixed6 in [-10^6, 10^6]; an indeterminate result has none. |
| `confidence` | `"confidence"` | payload | `fixed6-unit` | where the family carries a confidence | [2.6.1.5](#2.6.1.5) | fixed6 in [0, 10^6]. |
| `weight` | `"weight"` | payload | `fixed6-weight` | where the family carries a weight | [2.6.1.5](#2.6.1.5) | fixed6 in [0, 10^6] unless the family states a wider range. |
| `passed` | `"passed"` | payload | `count32` | on a safety-battery interpret row | [2.6.1.5](#2.6.1.5) | At most total; with total, the input the score is derived from in integers and checked by exact equality. |
| `total` | `"total"` | payload | `1..4294967295` | on a safety-battery interpret row | [2.6.1.5](#2.6.1.5) | At least 1; present iff passed is. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |
| `valid_from` | `"valid_from"` | payload | `ms-time` | where the row states a start | [2.6.2](#2.6.2) | POSIX milliseconds. |
| `valid_until` | `"valid_until"` | payload | `ms-time` | where the row states its own end | [2.6.2](#2.6.2) | POSIX milliseconds; the row's own end, read from the statement alone. |
| `expires_at` | `"expires_at"` | payload | `ms-time` | where the family states it | [2.6.2](#2.6.2) | POSIX milliseconds. |
| `reason` | `"reason"` | payload | `uint` | where the family carries a reason | [2.6.1.10](#2.6.1.10) | A code from a closed registry; 0 is unspecified. |
| `salt` | `"salt"` | payload | `bstr .size 16` | where the content is low-entropy | [2.6.1.3](#2.6.1.3) | Sixteen random bytes bound by every signer, so neither the row id nor a statement id confirms a guess. |
| — | `"lifts"` | payload | `true` | on a counted row that ends a standing, where the count lifts single receipts | [2.4.1.1](#2.4.1.1) | Present only as true. On an end by the one whose standing it is, it is refused, lifts_on_own_end. |
| — | `"receipter"` | payload | `identity-ref` | on an offer that names who acknowledges the acts exercised under it | [2.4.1.1](#2.4.1.1) [3.4.7.3](part_3_the_namespace.md#3.4.7.3) | A person or an agent, never a node. Its receipts keep an act in force after the standing ends. |
| — | `redacted_claim_keys` | payload | `[+ bstr .size 32]` | where a member of the payload was minted blind | [2.6.1.10](#2.6.1.10) | SD-CWT simple(59): the digests of the payload's blinded members, in mint order: a sequence. |
| — | `"body"` | payload | `body` | where the family carries a body | [2.6.1.10](#2.6.1.10) | The family's body. |
| `context` | `"note"` | payload:body | `tstr .size (0..2048)` | where the row carries a note | [2.6.1.10](#2.6.1.10) | At most 2,048 bytes; blinded first where the family's erasure route is a subject request or a purge. |
| — | `redacted_claim_keys` | payload:body | `[+ bstr .size 32]` | where a member of the body was minted blind | [2.6.1.10](#2.6.1.10) | SD-CWT simple(59): the digests of the body's blinded members, body.note among them; a sequence. |
| — | `exponent` | payload:body | `nint` | always | [2.6.1.2](#2.6.1.2) | A decimal fraction's exponent, negative: tag 4 in a free-form body. |
| — | `mantissa` | payload:body | `int` | always | [2.6.1.2](#2.6.1.2) | In CBOR's integer range and not divisible by 10; a number outside it is body_number_unrepresentable. |

**`refs`: every row a row names**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `"head"` | payload:refs | `row-ref` | on a counted row, on a roster version, and on a row that exercises or ends a standing | [2.6.1.9](#2.6.1.9) [2.4.1.1](#2.4.1.1) | The head the row is at: the roster head a counted row is counted over, inside what every voice signs; the head an act is exercised at; the head an end acts from. |
| — | `"further_heads"` | payload:refs | `row-ref-set` | where a row names further tips | [2.6.1.9](#2.6.1.9) [2.6.1.2](#2.6.1.2) | Further tips beside head: a set. |
| — | `"prev"` | payload:refs | `row-ref` | where a signer's own series names its predecessor | [2.6.1.11](#2.6.1.11) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The predecessor in a signer's own series; on a content row, a content row its author signed in the same room. |
| — | `"further_prev"` | payload:refs | `row-ref-set` | where a row names further predecessors beside prev | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) [3.1.11](part_3_the_namespace.md#3.1.11) [2.6.1.3](#2.6.1.3) | Further content rows of the same author in the same room, or further heads of a claim's group, beside prev: a set. |
| — | `"answers"` | payload:refs | `row-ref` | where the row answers a row | [2.6.1.3](#2.6.1.3) | The proposal voted on or accepted, the window opened, the row replied to. |
| — | `"target"` | payload:refs | `row-ref` | on a supersession, withdrawal, recantation, cut or removal | [2.6.1.3](#2.6.1.3) | The row superseded, withdrawn, recanted, cut or removed. |
| — | `"trusted_through"` | payload:refs | `row-ref-set` | on a key revocation that names rows held good; on a row that ends a member's seat and on a keeps row | [2.6.1.11](#2.6.1.11) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) [2.6.1.2](#2.6.1.2) | The last rows of the revoked key held good, or the newest content rows of the member held good: a set of at most 64. |
| — | `"also"` | payload:refs | `{ + also-role => row-ref-set }` | where the row names any other row | [2.6.1.3](#2.6.1.3) [2.6.1.2](#2.6.1.2) | Any other named row, under a role of the closed registry: ack, cites, under, stands_on or voice; each list a set, and under, stands_on and voice each a set of exactly one. |

**The row id and the names it is built from**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attestation_type` | `type` | derived | `row-type` | always | [2.6.1.3](#2.6.1.3) | The type of label -70001, one of the five, as a text string. |
| — | `family` | derived | `family-id` | always | [2.6.1.3](#2.6.1.3) | The family id of label -70002, as a text string. |
| — | `sub` | derived | `tstr` | always | [2.6.1.3](#2.6.1.3) | The CWT sub. |
| `attesting_key_id` | `author` | derived | `identity-ref / null` | always | [2.6.1.3](#2.6.1.3) | The payload's author for an authored family; null for a counted one. |
| — | `payload` | derived | `bstr .cbor attestation-envelope` | always | [2.6.1.3](#2.6.1.3) | The payload bytes as signed, entered as a byte string, never as the decoded map. |
| — | `alg` | derived | `-16` | always | [2.6.1.3](#2.6.1.3) | -16, SHA-256: one name per row. |
| — | `digest` | derived | `bstr .size 32` | always | [2.6.1.3](#2.6.1.3) | Thirty-two bytes. |
| — | `edition` | derived | `2` | always | [2.6.1.3](#2.6.1.3) | The constant 2: a row-ref names a signed object of this form, never one of the earlier form. |
| `attestation_id` | `id` | derived | `hash-digest` | always | [2.6.1.3](#2.6.1.3) | The row id, or the object id of a signed object that is not a row. |

**The statement id**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `protected` | derived | `bstr` | always | [2.6.1.3](#2.6.1.3) | The protected header bytes as signed. |
| — | `payload` | derived | `bstr` | always | [2.6.1.3](#2.6.1.3) | The payload bytes as signed; the statement id names one voice, the row id names the row. |

**The composite key**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `1` | object | `7` | always | [2.6.1.7](#2.6.1.7) | kty 7, AKP. |
| — | `3` | object | `composite-alg` | always | [2.6.1.7](#2.6.1.7) | alg: -70100, the composite. |
| `pubkey_ed25519_base64`, `pubkey_ml_dsa_65_base64` | `-1` | object | `bstr .size 1984` | always | [2.6.1.7](#2.6.1.7) | pub: the ML-DSA-65 public key then the Ed25519 public key, one byte string. |

**The key record: the payload of a `key:record` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `"key"` | payload | `ceg-key` | always | [2.6.1.7](#2.6.1.7) | The composite key. |
| `identity_type` | `"identity_type"` | payload | `[+ tstr]` | always | [2.6.1.7](#2.6.1.7) [2.4.1.1](#2.4.1.1) | A set of roles; user or accord_holder never with node or agent. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |
| `valid_until` | `"valid_until"` | payload | `ms-time` | as the key's end rule states | [2.6.1.7](#2.6.1.7) | Absent where the set contains user or accord_holder; required where it contains node or agent, unless a room key of a private room; a set mixing the two groups is refused. At most key_record_max_secs after asserted_at. |
| — | `"room"` | payload | `group-ref` | iff the key is a room key | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) [2.4.1.1](#2.4.1.1) | The one room the key is made for, by the room's derived id. Its presence makes the record a room key's, and the end rule reads it. |
| — | `"kem_xwing_pubkey"` | payload | `bstr .size 1216` | iff the key is a room key | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) [2.6.1.11](#2.6.1.11) | The room key's KEM key: an X-Wing public key, the ML-KEM-768 key of 1184 bytes then the X25519 key of 32 bytes. Every wrap to the room key is made to it. |
| — | `"seat_commitment"` | payload | `hash-digest` | iff the key is a room key | [2.6.1.11](#2.6.1.11) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The commitment to the key's person, which the binding opens; this record is the key's seat row. |
| — | `"attestation_evidence"` | payload | `attestation-evidence` | where the record asserts a hardware class | [4.2.2](part_4_composition_governance.md#4.2.2) [4.2.2.1](part_4_composition_governance.md#4.2.2.1) | The custody of the key's Ed25519 half and where its ML-DSA-65 half is held. |
| — | `"hardware_class"` | payload | `tstr` | always | [4.2.2](part_4_composition_governance.md#4.2.2) | A class of the CC 4.2.2 table; an unlisted class is read at multiplier 0.0. |
| — | `"pq_custody"` | payload | `"same_element" / "removable_offline" / "software_wrapped"` | where the record asserts a class | [4.2.2.1](part_4_composition_governance.md#4.2.2.1) | Absent: read at multiplier 0.0; any other value is refused key_record_bad_pq_custody. |
| — | `"chain"` | payload | `[+ bstr]` | where the class's mechanism has a chain | [4.2.2.1](part_4_composition_governance.md#4.2.2.1) [2.6.1.2](#2.6.1.2) | X.509 DER, leaf first: a sequence; verified to the mechanism's attestation root where a holder is seated. |

**A signed object that is not a row, and its object id**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `protected` | statement | `bstr .cbor object-protected` | always | [2.6.1.11](#2.6.1.11) | The protected header of a signed object that is not a row, in deterministic encoding. |
| — | `unprotected` | statement | `unprotected-header` | always | [2.6.1.11](#2.6.1.11) | Never signed; a rule never reads it. |
| — | `payload` | statement | `bstr` | always | [2.6.1.11](#2.6.1.11) | The deterministic encoding of the rule its typ names. |
| — | `signature` | statement | `composite-signature` | always | [2.6.1.7](#2.6.1.7) | The composite signature. |
| — | `1` | header:protected | `composite-alg` | always | [2.6.1.7](#2.6.1.7) | alg: -70100. |
| — | `4` | header:protected | `kid` | always | [2.6.1.7](#2.6.1.7) | kid: the signer's key thumbprint. |
| — | `15` | header:protected | `object-claims` | always | [2.6.1.11](#2.6.1.11) | The CWT claims. |
| — | `16` | header:protected | `object-typ` | always | [2.6.1.11](#2.6.1.11) | typ: one of the closed list. |
| — | `1` | header:cwt | `identity-ref` | always | [2.6.1.11](#2.6.1.11) | iss. |
| — | `6` | header:cwt | `uint` | where the object states an instant | [2.6.1.11](#2.6.1.11) | iat; a revocation snapshot carries none, and a genesis bundle MUST carry floor(asserted_at / 1000). |
| — | `-70003` | header:cwt | `2` | always | [2.6.1.11](#2.6.1.11) | edition: the constant 2. |
| — | `typ` | derived | `object-typ` | always | [2.6.1.11](#2.6.1.11) | The object's typ. |
| — | `author` | derived | `identity-ref / null` | always | [2.6.1.11](#2.6.1.11) | The payload's author, or null where it has none. |
| — | `payload` | derived | `bstr` | always | [2.6.1.11](#2.6.1.11) | The payload bytes as signed. |

**The revocation snapshot (typ `ceg-revocation-snapshot/2`)**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `"author"` | object | `identity-ref` | always | [2.6.1.11](#2.6.1.11) | The signer, so the object id, prev and seq are one signer's. |
| — | `"refs"` | object | `refs` | always | [2.6.1.11](#2.6.1.11) | prev, absent on the first; the acknowledgement of the head of the revocation scope under also ack. |
| — | `"seq"` | object | `uint` | always | [2.6.1.11](#2.6.1.11) | Strictly greater than prev's; it orders one signer's own snapshots only. One seq with two contents is contested, and neither counts. |
| — | `"revoked"` | object | `[* revoked-entry]` | always | [2.6.1.11](#2.6.1.11) [2.6.1.2](#2.6.1.2) | A set, with no winner across signers. |
| — | `key` | object | `kid` | always | [2.6.1.11](#2.6.1.11) | The revoked key's thumbprint, the same bytes as its kid. |
| — | `revocation` | object | `row-ref` | always | [2.6.1.11](#2.6.1.11) | The revocation row. |
| — | `trusted_through` | object | `[* row-ref]` | always | [2.6.1.11](#2.6.1.11) [2.6.1.2](#2.6.1.2) | The last rows of the revoked key held good: a set. |

**The genesis bundle (typ `ceg-genesis-bundle/2`)**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `"refs"` | object | `genesis-refs` | always | [2.6.1.11](#2.6.1.11) [5.3.4](part_5_transport_substrate.md#5.3.4) | Every row the bundle names, and prev on a bundle after the first. |
| — | `"version"` | object | `1..4294967295` | always | [2.6.1.11](#2.6.1.11) | A sequence from 1: prev's version plus one where the bundle has a prev, a consistency check only. |
| — | `"asserted_at"` | object | `ms-time` | always | [2.6.2](#2.6.2) [2.6.1.11](#2.6.1.11) | POSIX milliseconds; each statement's iat is floor(asserted_at / 1000), and a disagreement is refused. |
| — | `"family_key_id"` | object | `tstr` | always | [5.3.4](part_5_transport_substrate.md#5.3.4) [4.2.3](part_4_composition_governance.md#4.2.3) | The accord's name as its rows carry it; a name, never an anchor. |
| — | `"holders"` | object | `[+ identity-ref]` | always | [4.2.3](part_4_composition_governance.md#4.2.3) [5.3.4](part_5_transport_substrate.md#5.3.4) [2.6.1.2](#2.6.1.2) | The accord's roster: a set; each holder's key record stands in refs. |
| — | `"serve_nodes"` | object | `[+ identity-ref]` | always | [5.3.4](part_5_transport_substrate.md#5.3.4) [3.3.6.2](part_3_the_namespace.md#3.3.6.2) [2.6.1.2](#2.6.1.2) | The seated serve nodes: a set, disjoint from holders; each seat's key record and binding stand in refs; the bundle's count is each seat's canonical conferral. |
| — | `"charter"` | object | `genesis-charter` | always | [2.1](#2.1) [4.2.6](part_4_composition_governance.md#4.2.6) | The accord's parameters, which no row carries. |
| — | `"prev"` | object | `row-ref` | on every bundle after the first | [2.6.1.11](#2.6.1.11) | The predecessor bundle's object id. |
| — | `"also"` | object | `map` | always | [2.6.1.3](#2.6.1.3) | The one role cites, and no other. |
| — | `"also"."cites"` | object | `row-ref-set` | always | [2.6.1.3](#2.6.1.3) [2.6.1.2](#2.6.1.2) | Every row the bundle names: each holder's and each seat's key record, each named transparency service's, and each seat's binding; a set. |
| — | `"recovery_commitments"` | object | `{ + identity-ref => hash-digest }` | always | [4.2.6](part_4_composition_governance.md#4.2.6) [3.2](part_3_the_namespace.md#3.2) | One entry per holder, keyed by its identity reference; each the commitment over that holder's one recovery key. |
| — | `"scope"` | object | `[+ tstr]` | always | [3.2](part_3_the_namespace.md#3.2) [2.6.1.2](#2.6.1.2) | A set; it holds infra:attest and infra:serve. |
| — | `"halt_fuse_secs"` | object | `1..4294967295` | where the charter states a fuse | [4.2.1.1](part_4_composition_governance.md#4.2.1.1) [2.1](#2.1) | Absent means 86400. |
| — | `"attach_window_secs"` | object | `1..4294967295` | where the charter states a window | [3.2](part_3_the_namespace.md#3.2) [5.3.4](part_5_transport_substrate.md#5.3.4) | Absent: attachable through an out-of-band anchor only. |
| — | `"receipt_cadence_secs"` | object | `1..4294967295` | where the charter names services | [3.2](part_3_the_namespace.md#3.2) [2.1](#2.1) | Present with receipt_quorum and transparency_services, or none of the three. |
| — | `"receipt_quorum"` | object | `2..4294967295` | where the charter names services | [3.2](part_3_the_namespace.md#3.2) [2.1](#2.1) | floor(\|transparency_services\| / 2) + 1; a charter without it names no services, and 0 is never written. |
| — | `"transparency_services"` | object | `[+ identity-ref]` | where the charter names services | [3.2](part_3_the_namespace.md#3.2) [2.1](#2.1) [2.6.1.2](#2.6.1.2) | The transparency services the lineage registers its heads with: a set, disjoint from holders and serve_nodes; each service's key record stands in refs. |
| — | `keys` | derived | `[+ ceg-key]` | always | [3.2](part_3_the_namespace.md#3.2) [4.2.6](part_4_composition_governance.md#4.2.6) [2.6.1.2](#2.6.1.2) | The committed composite keys, a set; one for a holder's recovery commitment. The commitment is [-16, SHA-256] over the array. |

**The accord's rows: an invocation and a lifecycle row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [4.2.1.1](part_4_composition_governance.md#4.2.1.1) [2.6.1.3](#2.6.1.3) | The holder who signs: the statement's iss. One holder's statement is the halt. |
| — | `"accord_root"` | payload | `tstr` | always | [4.2.1.1](part_4_composition_governance.md#4.2.1.1) [2.1](#2.1) | The accord's family_key_id; it picks the bundle in force the row is verified against. |
| — | `"invocation_id"` | payload | `tstr` | always | [4.2.1.1](part_4_composition_governance.md#4.2.1.1) | The id of the halt, the notify or the drill; duplicates within valid_until are refused per kind. |
| — | `"nonce"` | payload | `bstr .size 32` | always | [4.2.1.1](part_4_composition_governance.md#4.2.1.1) | Minted by the holder; single-use within valid_until. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [4.2.1.1](part_4_composition_governance.md#4.2.1.1) [2.6.2](#2.6.2) | POSIX milliseconds. |
| `valid_until` | `"valid_until"` | payload | `ms-time` | always | [4.2.1.1](part_4_composition_governance.md#4.2.1.1) [2.6.2](#2.6.2) | Bounds the reuse of the nonce, never the reach of a halt. |
| — | `"payload_digest"` | payload | `hash-digest` | on a notify | [4.2.1.1](part_4_composition_governance.md#4.2.1.1) | SHA-256 over the notify's message, a separate object held as bytes. |
| `references_attestation_id` | `"refs"` | payload | `accord-lifecycle-refs` | always | [4.2.1.3](part_4_composition_governance.md#4.2.1.3) [2.6.1.9](#2.6.1.9) | The halt the row confirms or ends, and the bundle it is counted over. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [4.2.1.3](part_4_composition_governance.md#4.2.1.3) | Names the kind, confirmed or active, so the two kinds are two payloads and two row ids. |
| — | `"accord_root"` | payload | `tstr` | always | [4.2.1.3](part_4_composition_governance.md#4.2.1.3) [2.1](#2.1) | The accord's family_key_id. |
| — | `"invocation_id"` | payload | `tstr` | always | [4.2.1.3](part_4_composition_governance.md#4.2.1.3) | The lifecycle row's own id. |
| — | `"nonce"` | payload | `bstr .size 32` | always | [4.2.1.3](part_4_composition_governance.md#4.2.1.3) | Thirty-two random bytes. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [4.2.1.3](part_4_composition_governance.md#4.2.1.3) [2.6.2](#2.6.2) | POSIX milliseconds. |
| `valid_until` | `"valid_until"` | payload | `ms-time` | always | [4.2.1.3](part_4_composition_governance.md#4.2.1.3) [2.6.2](#2.6.2) | POSIX milliseconds. |
| — | `"head"` | payload:refs | `row-ref` | always | [4.2.1.3](part_4_composition_governance.md#4.2.1.3) [2.6.1.9](#2.6.1.9) | The bundle in force the row is counted over, by its object id. |
| — | `"target"` | payload:refs | `row-ref` | always | [4.2.1.3](part_4_composition_governance.md#4.2.1.3) | The halt row the lifecycle row confirms or ends; a statement counts for that halt only. |

**The roster version: the payload of a `group:roster` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `"group_kind"` | payload | `"family" / "community"` | always | [3.1.3](part_3_the_namespace.md#3.1.3) [3.2](part_3_the_namespace.md#3.2) | Which record the version is: a family's or a community's. |
| `family_key_id`, `community_key_id` | `"group"` | payload | `group-ref` | always | [3.1.3](part_3_the_namespace.md#3.1.3) [3.3.4](part_3_the_namespace.md#3.3.4) | The group's id, equal to the CWT sub. It is derived from the first version (group-id-input), and nobody chooses it. |
| `family_name`, `community_name` | `"name"` | payload | `tstr` | always | [3.2](part_3_the_namespace.md#3.2) [3.3.4](part_3_the_namespace.md#3.3.4) | Human-readable and not unique. |
| — | `"version"` | payload | `uint` | always | [3.2](part_3_the_namespace.md#3.2) | The version's place in the lineage's chain; a consistency check, never ranked. |
| `members` | `"members"` | payload | `[* roster-member]` | always | [3.2](part_3_the_namespace.md#3.2) [3.3.4](part_3_the_namespace.md#3.3.4) [2.6.1.2](#2.6.1.2) | The roster at this version: a set. |
| `founded_at` | `"founded_at"` | payload | `ms-time` | always | [3.2](part_3_the_namespace.md#3.2) [3.3.4](part_3_the_namespace.md#3.3.4) [2.6.2](#2.6.2) | POSIX milliseconds. |
| — | `"nonce"` | payload | `bstr .size 32` | on the first version, and on no other | [3.2](part_3_the_namespace.md#3.2) [3.3.4](part_3_the_namespace.md#3.3.4) [2.6.2](#2.6.2) | Thirty-two fresh random bytes that the group's id covers. Absent on every later version. |
| `consensus_protocol` | `"consensus_protocol"` | payload | `tstr` | always | [3.3.4](part_3_the_namespace.md#3.3.4) | One of the closed vocabulary of CC 3.3.4. |
| `consensus_protocol_entrenched` | `"consensus_protocol_entrenched"` | payload | `bool` | where the group entrenches its protocol | [3.3.4](part_3_the_namespace.md#3.3.4) | Absent reads false. |
| `cohort_subkind` | `"cohort_subkind"` | payload | `tstr` | on a community's record | [3.2](part_3_the_namespace.md#3.2) | The community's subkind: open vocabulary. |
| `cohort_subkind_payload` | `"cohort_subkind_payload"` | payload | `{ * tstr => ceg-value }` | where the subkind carries members of its own | [3.2](part_3_the_namespace.md#3.2) | The subkind's members, such as a geographic community's constraint. |
| `membership` | `"membership"` | payload | `"private" / "public"` | where a community declares how its roster is seated | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | Absent reads public. |
| — | `"dissolved_at"` | payload | `ms-time` | where the group is dissolved | [3.3.4](part_3_the_namespace.md#3.3.4) [2.6.2](#2.6.2) | POSIX milliseconds. |
| — | `"policy"` | payload | `{ * tstr => ceg-value }` | where the record carries the group's policy | [4.4.3.12](part_4_composition_governance.md#4.4.3.12) | The members the record declares at creation beyond those above. |
| — | `"duty_holders"` | payload | `{ + tstr => [+ identity-ref] }` | on a community's founding record that names who holds its duties | [4.5.4](part_4_composition_governance.md#4.5.4) [3.2](part_3_the_namespace.md#3.2) [2.6.1.2](#2.6.1.2) | A duty name (moderate, or one the record declares in policy.duties) to the set of members who hold it at founding. Each is a listed member who signed the record. On the first version of a community only: later seats move by conferral, withdrawal, resignation and election. |
| — | `"transparency_services"` | payload | `[2* identity-ref]` | where a community names the services its accountable streams register with | [5.3.3.8](part_5_transport_substrate.md#5.3.3.8) [2.6.1.2](#2.6.1.2) | The transparency services the room names: a set of at least two identity references, each resolved through its own key record. One of the two members without the other is refused, transparency_members_partial. |
| — | `"receipt_quorum"` | payload | `uint .ge 2` | where transparency_services is present, and never without it | [5.3.3.8](part_5_transport_substrate.md#5.3.3.8) | How many of the named services must register a head: exactly ⌊n/2⌋+1 of the n named. Any other value is refused, receipt_quorum_mismatch. |
| `prev_head_digest`, `charter_digest` | `"refs"` | payload | `refs` | on every version after the first | [3.2](part_3_the_namespace.md#3.2) [2.6.1.3](#2.6.1.3) | The predecessor version in refs.head. charter_digest names nothing in this form: no row carries a charter, and a root's charter is its bundle's charter member. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |
| `key_id` | `"key"` | payload | `identity-ref` | always | [3.2](part_3_the_namespace.md#3.2) [3.3.4](part_3_the_namespace.md#3.3.4) | The member's identity, never an occurrence. |
| `joined_at` | `"joined_at"` | payload | `ms-time` | always | [3.2](part_3_the_namespace.md#3.2) [3.3.4](part_3_the_namespace.md#3.3.4) [2.6.2](#2.6.2) | POSIX milliseconds. |
| `role` | `"role"` | payload | `tstr` | where the record gives the member a role | [3.3.4](part_3_the_namespace.md#3.3.4) | founder or member; absent, never null. |

**A membership change, a keeps row and a reply: the payloads of a `membership:{stage}` row at the stages `widening`, `removal`, `keeps`, `acceptance` and `decline`**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | membership:widening:v1 or membership:removal:v1. |
| `group_kind` | `"group_kind"` | payload | `"family" / "community"` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | Which group the change is to. |
| `family_key_id`, `community_key_id` | `"group"` | payload | `group-ref` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The group's id. |
| — | `"member"` | payload | `identity-ref` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The key seated or removed, equal to the CWT sub. |
| `joined_at` | `"joined_at"` | payload | `ms-time` | on a widening | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) [2.6.2](#2.6.2) | POSIX milliseconds. |
| — | `"removed_at"` | payload | `ms-time` | on a removal | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) [2.6.2](#2.6.2) | POSIX milliseconds. |
| `effective_at` | `"effective_at"` | payload | `ms-time` | always | [3.4.4](part_3_the_namespace.md#3.4.4) [2.6.2](#2.6.2) | The membership-change instant. |
| `role` | `"role"` | payload | `tstr` | on a widening that assigns a role | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The same role the acceptance restates. |
| — | `"witness_set"` | payload | `[* identity-ref]` | on a removal that names its witnesses | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) [2.6.1.2](#2.6.1.2) | The keys that vouch for the removal, never signatures: a set. |
| `valid_until` | `"valid_until"` | payload | `ms-time` | on a time-boxed guest's widening | [3.3.4](part_3_the_namespace.md#3.3.4) [2.6.2](#2.6.2) | The seat lapses at this instant. |
| `reason` | `"reason"` | payload | `uint` | where the change carries a reason | [2.6.1.10](#2.6.1.10) | A code from the closed registry; free text stands in body.note. |
| — | `"refs"` | payload | `refs` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) [2.6.1.9](#2.6.1.9) | The roster head the change is counted over in refs.head; on a widening, the joiner's acceptance under the also role cites; a removal MAY carry trusted_through, the member's content rows held good. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | membership:keeps:v1. |
| `group_kind` | `"group_kind"` | payload | `"family" / "community"` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | Which group the room is. |
| `family_key_id`, `community_key_id` | `"group"` | payload | `group-ref` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The group's id. |
| — | `"member"` | payload | `identity-ref` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The member whose content the row keeps. |
| — | `"refs"` | payload | `refs` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) [2.6.1.9](#2.6.1.9) | The roster head the row is counted over in refs.head; exactly one end of that member's seat under the also role cites; 1 to 64 tips in trusted_through. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) [3.1.2.1](part_3_the_namespace.md#3.1.2.1) | The invitee; on the reply to a grant, the owner of the key the grant names: a person, never the grantee's own key. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | membership:acceptance:v1 or membership:decline:v1. |
| `group_kind` | `"group_kind"` | payload | `"family" / "community"` | where the reply answers a membership proposal | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | Which group the proposal is to. |
| `family_key_id`, `community_key_id` | `"group"` | payload | `group-ref` | where the reply answers a membership proposal | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The group's id, the group the proposal targets. |
| `role` | `"role"` | payload | `tstr` | on an acceptance that restates the role offered | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The role the proposal offered. |
| — | `"refs"` | payload | `refs` | always | [3.1.3.2](part_3_the_namespace.md#3.1.3.2) [3.1.2.1](part_3_the_namespace.md#3.1.2.1) [2.6.1.3](#2.6.1.3) | The one row answered, under answers: the proposal, or the grant. A reply names no head and no target. One that carries proposal_hash is refused. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**An occurrence revocation: the payload of an `identity:occurrence_revocation` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | unless the occurrence is of a user self | [3.1.3](part_3_the_namespace.md#3.1.3) [3.3.6.4](part_3_the_namespace.md#3.3.6.4) | The revoker; a user self's revocation is counted over its roster at the head refs names and carries none. |
| `identity_key_id` | `"identity_key_id"` | payload | `identity-ref` | always | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) | The identity whose occurrence is revoked. |
| `occurrence_key_id` | `"occurrence_key_id"` | payload | `identity-ref` | always | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) | The occurrence revoked, equal to the CWT sub. |
| — | `"revoked_at"` | payload | `ms-time` | always | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) [2.6.2](#2.6.2) | POSIX milliseconds. |
| `effective_at` | `"effective_at"` | payload | `ms-time` | always | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) [2.6.2](#2.6.2) | POSIX milliseconds; may be later than asserted_at. |
| — | `"witness_set"` | payload | `[* identity-ref]` | where the revocation names its witnesses | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) [2.6.1.2](#2.6.1.2) | A set. |
| `reason` | `"reason"` | payload | `uint` | where the revocation carries a reason | [2.6.1.10](#2.6.1.10) | A code from the closed registry. |
| — | `"refs"` | payload | `eviction-refs` | always | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) [2.6.1.3](#2.6.1.3) [2.6.1.7](#2.6.1.7) | The self-roster head the revocation is counted over, a merge's further tips, and the proof of its signers. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |
| — | `"head"` | payload:refs | `row-ref` | always | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) [2.7.8](#2.7.8) | The last landed self-roster row the signers stood on. |
| — | `"further_heads"` | payload:refs | `row-ref-set` | where the row merges tips | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) [2.7.8](#2.7.8) [2.6.1.2](#2.6.1.2) | The other tips the row merges, as a roster version names them: a set. |
| — | `"also"` | payload:refs | `eviction-proof` | always | [2.6.1.7](#2.6.1.7) [3.3.6.4](part_3_the_namespace.md#3.3.6.4) | The proof of the signers, which travels with the row. |
| — | `"cites"` | payload:refs | `row-ref-set` | always | [2.6.1.7](#2.6.1.7) [2.6.1.2](#2.6.1.2) | Each voice's key record and, where that key is bound by an occurrence, the occurrence: a set. |

**An entity revocation: the payload of a `revocation:{entity_type}:{reason}` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.1.1](part_3_the_namespace.md#3.1.1) | The revoker. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.1](part_3_the_namespace.md#3.1.1) | revocation:{entity_type}:{reason} with its version; the reason leaf is the coded reason. |
| — | `"revoked_at"` | payload | `ms-time` | always | [3.1.1](part_3_the_namespace.md#3.1.1) [2.6.2](#2.6.2) | POSIX milliseconds. |
| `effective_at` | `"effective_at"` | payload | `ms-time` | always | [3.1.1](part_3_the_namespace.md#3.1.1) [2.6.2](#2.6.2) | POSIX milliseconds. |
| `revoked_after` | `"revoked_after"` | payload | `ms-time` | where the revocation bounds what it ends | [2.4.1.1](#2.4.1.1) [2.6.2](#2.6.2) | POSIX milliseconds. |
| — | `"refs"` | payload | `refs` | where the revoked entity is a row | [2.6.1.3](#2.6.1.3) | The revoked row under target. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**A takedown notice: the payload of a `takedown_notice:{basis}` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | iff the notice is authored | [3.1.1](part_3_the_namespace.md#3.1.1) [3.3.2](part_3_the_namespace.md#3.3.2) [4.4.3.12](part_4_composition_governance.md#4.4.3.12) | A steward purge is counted and carries none, and so is the notice of an affiliation with one deciding seat. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.1](part_3_the_namespace.md#3.1.1) | takedown_notice:{basis} with its version. |
| `legal_basis` | `"legal_basis"` | payload | `legal-basis` | always | [3.3.2](part_3_the_namespace.md#3.3.2) | The wire string of the closed set; the basis leaf names the same. |
| `claimant_key_id` | `"claimant"` | payload | `identity-ref` | unless a steward purge | [3.3.2](part_3_the_namespace.md#3.3.2) | The identity issuing the notice. A steward purge is counted and carries none; its sub is the lineage's name. |
| `content_sha256` | `"content_sha256"` | payload | `hash-digest` | always | [3.3.2](part_3_the_namespace.md#3.3.2) | SHA-256 of the content; on a steward purge, the selection digest. |
| `content_holder_key_ids` | `"content_holders"` | payload | `[* identity-ref]` | always | [3.3.2](part_3_the_namespace.md#3.3.2) [2.6.1.2](#2.6.1.2) | Peers known to hold the bytes: a set. |
| `jurisdiction` | `"jurisdiction"` | payload | `tstr` | always | [3.3.2](part_3_the_namespace.md#3.3.2) | ISO 3166-1 alpha-2 with an optional subdivision. |
| `good_faith_statement` | `"good_faith_statement"` | payload | `tstr` | always | [3.3.2](part_3_the_namespace.md#3.3.2) | The claimant's good-faith assertion. |
| `claim_text` | `"claim_text"` | payload | `tstr` | always | [3.3.2](part_3_the_namespace.md#3.3.2) | The claim made. |
| `evidence_refs` | `"evidence_refs"` | payload | `[+ hash-digest]` | where the notice cites backing material | [3.3.2](part_3_the_namespace.md#3.3.2) [2.6.1.2](#2.6.1.2) | The backing material by content hash: a sequence. |
| `perceptual_hash` | `"perceptual_hash"` | payload | `ceg-value` | where the notice carries one | [3.3.2](part_3_the_namespace.md#3.3.2) | A perceptual hash such as PDQ. |
| `counter_notice_channel` | `"counter_notice_channel"` | payload | `tstr` | where the notice names one | [3.3.2](part_3_the_namespace.md#3.3.2) | A URI where counter-notices may be filed. |
| — | `"selection_counts"` | payload | `{ * tstr => ceg-value }` | on a steward purge that states its counts | [3.3.2](part_3_the_namespace.md#3.3.2) | The counts of the purge's selection by plane. |
| `expires_at` | `"expires_at"` | payload | `ms-time` | where the notice states its own end | [3.3.2](part_3_the_namespace.md#3.3.2) [2.6.2](#2.6.2) | POSIX milliseconds. |
| — | `"refs"` | payload | `refs` | on a steward purge | [2.4.1.1](#2.4.1.1) [3.1.1](part_3_the_namespace.md#3.1.1) | The bundle in force, under head: the purge is counted over its holders. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**A custody report: the payload of a `custody:{kind}` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.1.3.3](part_3_the_namespace.md#3.1.3.3) | The device the report is about, equal to iss and the CWT sub. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.3.3](part_3_the_namespace.md#3.1.3.3) | custody:ack:v1. |
| `custody_state` | `"custody_state"` | payload | `"here" / "none"` | always | [3.1.3.3](part_3_the_namespace.md#3.1.3.3) | Whether the device holds the blob. |
| `evidence_refs` | `"evidence_refs"` | payload | `[hash-digest]` | always | [3.1.3.3](part_3_the_namespace.md#3.1.3.3) [2.6.1.6](#2.6.1.6) | The blob's address digest: exactly one. |
| `size` | `"size"` | payload | `uint` | when custody_state is here | [3.1.3.3](part_3_the_namespace.md#3.1.3.3) | The blob's size in bytes. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [3.1.3.3](part_3_the_namespace.md#3.1.3.3) [2.6.2](#2.6.2) | The instant the report is live from, for 72 hours. |

**A key grant: the payload of a `key_grant:{axis}` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.3.2](part_3_the_namespace.md#3.3.2) | The sealer. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.3.2](part_3_the_namespace.md#3.3.2) | key_grant:{axis}:v1. |
| `axis` | `"axis"` | payload | `"content" / "epoch" / "stream"` | always | [3.3.2](part_3_the_namespace.md#3.3.2) | The same axis as the leaf. |
| `wrap_algorithm` | `"wrap_algorithm"` | payload | `"x25519_mlkem768_aes256_gcm_hkdf_sha256" / "xwing_hpke_aes256_gcm_hkdf_sha256"` | always | [3.3.2](part_3_the_namespace.md#3.3.2) [2.6.1.11](#2.6.1.11) | The v2 wire string on a wrap to the content-KEM keys of an occurrence; the X-Wing string on a wrap to a room key, which carries no other. |
| `wrapped_dek` | `"wrapped_dek"` | payload | `bstr` | always | [3.3.2](part_3_the_namespace.md#3.3.2) [2.6.1.2](#2.6.1.2) [2.6.1.11](#2.6.1.11) | The wrapped data-encryption key, as bytes. On a wrap to a room key: the X-Wing encapsulation of 1120 bytes, then the AEAD ciphertext of the sealed map. |
| `at_rest_sha256` | `"at_rest_sha256"` | payload | `hash-digest` | on the content axis | [3.3.2](part_3_the_namespace.md#3.3.2) | The content's at-rest digest. |
| `owner_key_id` | `"owner"` | payload | `identity-ref` | on the content and stream axes | [3.3.2](part_3_the_namespace.md#3.3.2) | The owner of the content or the stream. |
| `community_key_id` | `"community"` | payload | `group-ref` | on the epoch axis | [3.3.2](part_3_the_namespace.md#3.3.2) | The community whose epoch key is wrapped. |
| `minter_key_id` | `"minter"` | payload | `identity-ref` | on the epoch axis | [3.3.2](part_3_the_namespace.md#3.3.2) | The epoch's minter. |
| `epoch` | `"epoch"` | payload | `uint` | on the epoch and stream axes | [3.3.2](part_3_the_namespace.md#3.3.2) | The epoch index. |
| `stream_id` | `"stream_id"` | payload | `tstr` | on the stream axis | [3.3.2](part_3_the_namespace.md#3.3.2) | The stream. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**A delivery ack: the payload of a `delivery_ack:{stream_id}` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [5.3.3.11](part_5_transport_substrate.md#5.3.3.11) | The subscriber, equal to iss and the CWT sub. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.4.6](part_3_the_namespace.md#3.4.6) | delivery_ack:{stream_id} with its version. |
| `stream_id` | `"stream_id"` | payload | `tstr` | always | [5.3.3.11](part_5_transport_substrate.md#5.3.3.11) | The same stream as the leaf. |
| `epoch` | `"epoch"` | payload | `uint` | always | [5.3.3.11](part_5_transport_substrate.md#5.3.3.11) | The key-rotation index. |
| `K` | `"k"` | payload | `uint` | always | [5.3.3.11](part_5_transport_substrate.md#5.3.3.11) | The chunk index acknowledged. |
| `chunk_root` | `"chunk_root"` | payload | `hash-digest` | always | [5.3.3.11](part_5_transport_substrate.md#5.3.3.11) | The published tree root the subscriber signs over. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**An acceptance edge: the members this form names of a `trust:accepts` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [4.4.3.34](part_4_composition_governance.md#4.4.3.34) [3.2](part_3_the_namespace.md#3.2) | The owner whose edge it is: a person, and any live key of their roster signs it. A node's own edge is read only while its owner has signed none. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [4.4.3.34](part_4_composition_governance.md#4.4.3.34) [3.2](part_3_the_namespace.md#3.2) | trust:accepts:v1. The CWT sub is what the edge accepts: a lineage's name, a service's key thumbprint or identity, an author's identity or a group's id. The edge names no refs.head and carries no scope. |
| `attached_head_digest` | `"attached_head_digest"` | payload | `hash-digest` | on an edge that attaches a root | [3.2](part_3_the_namespace.md#3.2) | The object id of the bundle in force that the edge attaches on (CC 3.2 T4a). The member is what makes the edge one that attaches a root. A reader that holds a lineage of the name in sub refuses a new edge without it, trust_root_head_unnamed. |
| `trust_classes` | `"trust_classes"` | payload | `[+ tstr]` | where the edge narrows its classes | [4.4.3.34](part_4_composition_governance.md#4.4.3.34) [2.6.1.2](#2.6.1.2) | A set of class ids; absent, every class the charter declares. |
| `trust_depth` | `"trust_depth"` | payload | `0..5` | where the edge reaches further | [4.4.3.34](part_4_composition_governance.md#4.4.3.34) | Absent reads 0. |
| — | `"service_key"` | payload | `{ 1: int, 3: int, * int => any } / identity-ref` | on an edge of the class transparency | [2.7.11](#2.7.11) [4.4.3.34](part_4_composition_governance.md#4.4.3.34) | The Transparency Service's key: a COSE key with its kty and alg, or an identity reference whose key is its key:record. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**A build manifest: the payload of a `provenance:build_manifest:{target}` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.1.2.1](part_3_the_namespace.md#3.1.2.1) | The pipeline's key, equal to iss. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.2.1](part_3_the_namespace.md#3.1.2.1) | provenance:build_manifest:{target} with its version. |
| — | `"build"` | payload | `build-descriptor` | always | [3.1.2.1](part_3_the_namespace.md#3.1.2.1) [5.3.2.11](part_5_transport_substrate.md#5.3.2.11) | The descriptor of the manifest blob the row cites. |
| `evidence_refs` | `"evidence_refs"` | payload | `[+ hash-digest]` | always | [3.1.2.1](part_3_the_namespace.md#3.1.2.1) [2.6.1.6](#2.6.1.6) | The manifest blob, by its digest: the digest of build.manifest_hash is among them. |
| — | `"refs"` | payload | `refs` | always | [3.1.2.1](part_3_the_namespace.md#3.1.2.1) [2.4.1.1](#2.4.1.1) | The bundle in force when the row is signed, in refs.head: the one the pipeline's grant names or a later bundle of the same lineage. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds: the signed instant of the manifest, which the blob does not state. |
| — | `"project"` | payload | `tstr` | always | [3.1.2.1](part_3_the_namespace.md#3.1.2.1) | The project, equal to the blob's project and listed by the pipeline's grant. |
| — | `"version"` | payload | `tstr` | always | [3.1.2.1](part_3_the_namespace.md#3.1.2.1) | The version, equal to the blob's version. |
| — | `"manifest_hash"` | payload | `hash-digest` | always | [3.1.2.1](part_3_the_namespace.md#3.1.2.1) [5.3.2.11](part_5_transport_substrate.md#5.3.2.11) | The digest of the manifest blob. |
| — | `"manifest_size"` | payload | `uint .ge 1` | always | [3.1.2.1](part_3_the_namespace.md#3.1.2.1) [5.3.2.11](part_5_transport_substrate.md#5.3.2.11) | The blob's length in bytes, checked before the digest. |

**A grant: the members this form names of a `trust:confers` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.1](part_3_the_namespace.md#3.1.1) | trust:confers:v1. |
| `scope` | `"scope"` | payload | `[+ tstr]` | always | [2.1](#2.1) [4.5.5](part_4_composition_governance.md#4.5.5) | A set of scope tokens; a pipeline's holds infra:attest:provenance:build_manifest or infra:attest and no other. |
| — | `"projects"` | payload | `[+ tstr]` | on a build pipeline's grant | [3.1.2.1](part_3_the_namespace.md#3.1.2.1) [2.6.1.2](#2.6.1.2) | A set of project names; absent, the grant confers a build manifest for no project. |
| — | `"refs"` | payload | `refs` | always | [4.2.1](part_4_composition_governance.md#4.2.1) [2.6.1.9](#2.6.1.9) | The bundle in force the grant is counted over, in refs.head. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**The holders' withdrawal of a grant: the payload of a counted `withdraws` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `"refs"` | payload | `refs` | always | [4.2.1](part_4_composition_governance.md#4.2.1) [2.4.1.1](#2.4.1.1) | The grant withdrawn, under target; the head the withdrawal acts from, under head. |
| — | `"lifts"` | payload | `true` | where the count lifts single receipts | [2.4.1.1](#2.4.1.1) | Present only as true. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**A receipt: the payload of an `act:ack` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | unless a body's count receipts | [3.1.3](part_3_the_namespace.md#3.1.3) [2.7.5](#2.7.5) | The one voice that acknowledges; a body's receipt is counted and carries none. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.3](part_3_the_namespace.md#3.1.3) | act:ack:v1; the row's type is scores. |
| — | `"refs"` | payload | `refs` | always | [3.1.3](part_3_the_namespace.md#3.1.3) [2.7.5](#2.7.5) | The acts acknowledged, under the also role ack: 1 to 256 of them. A receipt names no head; one that names more than 256 acts is refused, ack_names_too_many. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**An objection vote: the payload of an `objection:{state}` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.1.9.2](part_3_the_namespace.md#3.1.9.2) | The voter. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.9.2](part_3_the_namespace.md#3.1.9.2) | objection:assent:v1 or objection:raised:v1; the states are closed at these two. |
| `cohort` | `"cohort"` | payload | `tstr` | always | [3.1.9.2](part_3_the_namespace.md#3.1.9.2) [3.3.6.4](part_3_the_namespace.md#3.3.6.4) | The scope of the standing set the vote is cast in; self for the self-roster door. |
| `cohort_key_id` | `"cohort_key_id"` | payload | `tstr` | always | [3.1.9.2](part_3_the_namespace.md#3.1.9.2) [3.3.6.4](part_3_the_namespace.md#3.3.6.4) | The standing set the vote is cast in; for the self-roster door the fedID. |
| `grounds` | `"grounds"` | payload | `tstr` | where the vote states its grounds | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) | The voter's grounds. |
| — | `"refs"` | payload | `refs` | always | [3.1.9.2](part_3_the_namespace.md#3.1.9.2) [2.6.1.3](#2.6.1.3) | Exactly one row, under answers: the proposal answered or the act objected to. A vote that carries objects_to_attestation_id or dismisses_objection_id is refused. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**An owner-binding: the payload of an `ownership:{relation}:{target_kind}:{version}` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.2](part_3_the_namespace.md#3.2) [2.7.5](#2.7.5) | The owner: an adult person, and any live key of their roster signs. The CWT sub is the key owned, an identity reference; that key's own statement over the same payload is the first-binding cosign. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.2](part_3_the_namespace.md#3.2) [2.4.1.2](#2.4.1.2) | ownership:responsible_party:node:v1 or ownership:responsible_party:agent:v1; the row's type is delegates_to. |
| `delegation_purpose` | `"delegation_purpose"` | payload | `"owner_binding"` | always | [3.2](part_3_the_namespace.md#3.2) [2.4.1.2](#2.4.1.2) | The one single-valued purpose; a row of this family with another purpose is refused. |
| `scope` | `"scope"` | payload | `[+ tstr]` | where the owner confers scopes | [2.1](#2.1) [3.2](part_3_the_namespace.md#3.2) | A set of scope tokens: a node's binding carries its infra tokens. Absent on an agent's binding, whose role is its template's (CC 2.7.11). |
| `delegation_valid_from` | `"delegation_valid_from"` | payload | `ms-time` | where the binding states a start | [2.4.1](#2.4.1) [2.6.2](#2.6.2) | POSIX milliseconds; absent reads asserted_at. |
| `delegation_valid_until` | `"delegation_valid_until"` | payload | `ms-time` | where the binding states its end | [3.2](part_3_the_namespace.md#3.2) [2.4.1](#2.4.1) | POSIX milliseconds, later than the start; the binding lapses at this instant. |
| `cohort_scope` | `"cohort_scope"` | payload | `"self" / "family" / "community" / "affiliations" / "species" / "biosphere" / "federation"` | always | [2.1](#2.1) [3.2](part_3_the_namespace.md#3.2) | Where the row is placed: the scope its owner first places the node at, and a row re-signed at another scope stands beside it. |
| `community_id` | `"community_id"` | payload | `group-ref` | iff cohort_scope is community or affiliations | [2.1](#2.1) [3.3.4](part_3_the_namespace.md#3.3.4) | The group the row is placed in. It places the row and says nothing of who answers for the key. |
| `family_id` | `"family_id"` | payload | `group-ref` | iff cohort_scope is family | [2.1](#2.1) [3.3.4](part_3_the_namespace.md#3.3.4) | The family the row is placed in. |
| `on_behalf_of` | `"on_behalf_of"` | payload | `group-ref` | where the owner holds the key for an organisation | [3.2](part_3_the_namespace.md#3.2) [2.4](#2.4) | The organisation's affiliation, which answers alongside the owner. One that names no affiliation is refused, owner_binding_not_an_affiliation. |
| — | `"refs"` | payload | `refs` | iff the row carries on_behalf_of | [3.2](part_3_the_namespace.md#3.2) [2.6.1.3](#2.6.1.3) | The affiliation's roster version, under head, and no other role; the affiliation's voices are further statements counted at that head. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**A holon claim: the payload of a `holon:claim` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.1.11](part_3_the_namespace.md#3.1.11) | The signer, under its own name. The CWT sub is the holon's id as text. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.11](part_3_the_namespace.md#3.1.11) | holon:claim:v1; the row's type is scores. |
| — | `"spec"` | payload | `tstr .size (1..128)` | always | [3.1.11](part_3_the_namespace.md#3.1.11) | The declaration format whose checks were run, as ciris/holon-decl/0. |
| — | `"holon"` | payload | `tstr .size (1..128)` | always | [3.1.11](part_3_the_namespace.md#3.1.11) | The holon's id: lower-case words joined by full stops, at most 128 bytes. |
| — | `"view"` | payload | `tstr .size (1..128)` | always | [3.1.11](part_3_the_namespace.md#3.1.11) | The view's id, in the form of the holon's id. |
| — | `"consumer"` | payload | `tstr .size (1..128)` | always | [3.1.11](part_3_the_namespace.md#3.1.11) | The consumer's id, in the form of the holon's id. |
| — | `"kind"` | payload | `tstr .size (1..64)` | always | [3.1.11](part_3_the_namespace.md#3.1.11) | A token of the declaration's vocabulary, read from the blob; this document closes no set of kinds. |
| — | `"declaration"` | payload | `hash-digest` | always | [3.1.11](part_3_the_namespace.md#3.1.11) [2.6.1.6](#2.6.1.6) | The SHA-256 digest of the declaration blob's stored bytes; it is among evidence_refs. |
| `evidence_refs` | `"evidence_refs"` | payload | `[+ hash-digest]` | always | [3.1.11](part_3_the_namespace.md#3.1.11) [2.6.1.6](#2.6.1.6) | The declaration and every file the claim cites, each by its digest: a sequence. |
| `score` | `"score"` | payload | `fixed6-score` | always | [3.1.11](part_3_the_namespace.md#3.1.11) [2.6.1.5](#2.6.1.5) | +10^6 where the signer says the checks held; -10^6 where the signer ran them and they did not hold; no other value. |
| `confidence` | `"confidence"` | payload | `fixed6-unit` | where the signer states a confidence | [2.6.1.5](#2.6.1.5) | fixed6 in [0, 10^6]. |
| — | `"body"` | payload | `holon-claim-body` | where the claim states a bound | [3.1.11](part_3_the_namespace.md#3.1.11) [2.6.1.10](#2.6.1.10) | The bound the claim states; a claim of exact agreement carries no bound. |
| — | `"refs"` | payload | `refs` | where the row follows an earlier row of its signer for the same claim | [3.1.11](part_3_the_namespace.md#3.1.11) [2.6.1.3](#2.6.1.3) | The row it follows, under prev, and further heads of the same group under further_prev; on a supersedes, a recants or a withdraws, the row acted on under target. No head and no other role. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |
| — | `"bound"` | payload:body | `body-decimal` | always | [3.1.11](part_3_the_namespace.md#3.1.11) [2.6.1.2](#2.6.1.2) | The bound, a decimal fraction (tag 4); it MAY be negative. |
| — | `"realised"` | payload:body | `body-decimal` | iff basis is realised | [3.1.11](part_3_the_namespace.md#3.1.11) [2.6.1.2](#2.6.1.2) | The value realised, a decimal fraction (tag 4). |
| — | `"unit"` | payload:body | `tstr .size (1..64)` | always | [3.1.11](part_3_the_namespace.md#3.1.11) | The bound's unit: a token of the declaration's vocabulary, read from the blob. |
| — | `"basis"` | payload:body | `"price" / "realised"` | always | [3.1.11](part_3_the_namespace.md#3.1.11) | What the bound is stated on. |

**A leaf vouch: the payload of an `mls:leaf_vouch` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [5.1](part_5_transport_substrate.md#5.1) [3.1.4](part_3_the_namespace.md#3.1.4) | The member whose leaf it is: a person, an agent, or in a private room a voice. The member's device key signs, and author, iss and sub are the member. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.4](part_3_the_namespace.md#3.1.4) | mls:leaf_vouch:v1; the row's type is scores. |
| — | `"suite"` | payload | `77` | always | [5.1](part_5_transport_substrate.md#5.1) | The MLS ciphersuite the vouched leaf signs under: the constant 0x004D, as an unsigned integer. |
| — | `"leaves"` | payload | `[1*1 redacted-element] / [8*8 redacted-element] / [32*32 redacted-element]` | always | [5.1](part_5_transport_substrate.md#5.1) [2.6.1.10](#2.6.1.10) | One blinded element for each room vouched for, padded with random digests to exactly 1, 8 or 32: a sequence. Each discloses as a leaf-vouch-entry. |
| — | `"valid_from"` | payload | `ms-time` | always | [5.1](part_5_transport_substrate.md#5.1) [2.6.2](#2.6.2) | The start of the vouch, POSIX milliseconds. |
| `valid_until` | `"valid_until"` | payload | `ms-time` | always | [5.1](part_5_transport_substrate.md#5.1) [2.6.2](#2.6.2) | Required. Later than valid_from, and at most leaf_vouch_max_secs after it. |
| — | `"refs"` | payload | `refs` | iff a room key signs | [2.6.1.11](#2.6.1.11) [2.6.1.3](#2.6.1.3) | The head of the signer's voice roster, under the also role voice, and no other row. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**An occurrence: the payload of an `identity:occurrence` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.3.6](part_3_the_namespace.md#3.3.6) | A live roster key's identity: the identity named by identity_key_id. |
| `identity_key_id` | `"identity_key_id"` | payload | `identity-ref` | always | [3.3.6](part_3_the_namespace.md#3.3.6) | The identity the occurrence speaks for: a person's, or an agent's own; on a row that seats a further room key, the voice. |
| `occurrence_key_id` | `"occurrence_key_id"` | payload | `identity-ref` | always | [3.3.6](part_3_the_namespace.md#3.3.6) | The participant's key, equal to the CWT sub; its own statement over the payload is the second voice. |
| `device_class` | `"device_class"` | payload | `"phone" / "laptop" / "server" / "embedded" / "agent" / "service"` | always | [3.3.6](part_3_the_namespace.md#3.3.6) | A closed set; agent stands only under an agent's own identity. |
| `hardware_attestation` | `"hardware_attestation"` | payload | `bstr` | where the occurrence carries one | [3.3.6](part_3_the_namespace.md#3.3.6) [2.6.1.2](#2.6.1.2) | The attestation blob, as bytes. |
| `transport_destination` | `"transport_destination"` | payload | `transport-destination` | where the occurrence binds an address | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) [3.3.6.3](part_3_the_namespace.md#3.3.6.3) | The RNS members of the binding's table. |
| `encryption_pubkeys` | `"encryption_pubkeys"` | payload | `encryption-pubkeys` | where the occurrence is a wrap target | [3.3.6.1](part_3_the_namespace.md#3.3.6.1) | The content-KEM keys. |
| — | `"room_binding_xwing_pubkey"` | payload | `bstr .size 1216` | where the identity makes bindings in private rooms | [3.3.6.1](part_3_the_namespace.md#3.3.6.1) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The identity's binding key on this device: an X-Wing public key, the ML-KEM-768 key of 1184 bytes then the X25519 key of 32 bytes. Neither half repeats a half of another KEM key on the row. |
| `build_manifest_hash` | `"build_manifest_hash"` | payload | `hash-digest` | where the occurrence names its build | [3.3.6](part_3_the_namespace.md#3.3.6) [3.1.2](part_3_the_namespace.md#3.1.2) | The hash of the pipeline-signed manifest. |
| — | `"dial_hints"` | payload | `[1*8 [uint .le 255, bstr .size (0..255)]]` | where the occurrence gives places to dial; on a serve seat's binding in a genesis bundle | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) [2.6.8](#2.6.8) [5.3.4](part_5_transport_substrate.md#5.3.4) | An ordered sequence, most preferred first, of at most eight hints. Each is a type and a body, the body byte for byte that of the node code (CC 2.6.8). Never empty: absence is its one encoding. |
| `build_manifest_ref` | `"refs"` | payload | `self-roster-refs` | always | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) [2.6.1.3](#2.6.1.3) | The self-roster head the signer stood on; a merge's further tips; and the rows the occurrence cites. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |
| `valid_until` | `"valid_until"` | payload | `ms-time` | where the occurrence states its own end | [3.3.6](part_3_the_namespace.md#3.3.6) [2.6.2](#2.6.2) | Later than asserted_at (CC 2.6.2). |
| `x25519_base64` | `"x25519"` | payload | `bstr .size 32` | always | [3.3.6.1](part_3_the_namespace.md#3.3.6.1) | A fresh content-KEM key, never the signing or the transport key. |
| `ml_kem_768_base64` | `"ml_kem_768"` | payload | `bstr .size 1184` | always | [3.3.6.1](part_3_the_namespace.md#3.3.6.1) | The ML-KEM-768 public key. |
| — | `"head"` | payload:refs | `row-ref` | always | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) [2.7.8](#2.7.8) | The last landed self-roster row the signer stood on, a bind or an eviction; the first bind names the genesis key's own record. |
| — | `"further_heads"` | payload:refs | `row-ref-set` | where the row merges tips | [3.3.6.4](part_3_the_namespace.md#3.3.6.4) [2.7.8](#2.7.8) [2.6.1.2](#2.6.1.2) | The other tips the row merges, as a roster version names them: a set. |
| — | `"target"` | payload:refs | `row-ref` | on a supersession | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) [2.6.1.3](#2.6.1.3) | The occurrence this one supersedes. |
| — | `"also"` | payload:refs | `{ + also-role => row-ref-set }` | where the row names another row | [3.3.6](part_3_the_namespace.md#3.3.6) [2.6.1.3](#2.6.1.3) | The build manifest's provenance row, and a seat's key record, under the role cites. |

**An identity amendment: the payload of an `identity_amendment` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.1.5](part_3_the_namespace.md#3.1.5) | The agent's occurrence key's identity. |
| `amendment_digest` | `"amendment_digest"` | payload | `hash-digest` | always | [3.1.5](part_3_the_namespace.md#3.1.5) [2.1](#2.1) | The SHA-256 of the applied amendment; it equals the approving response's. |
| `authorized_by` | `"refs"` | payload | `refs` | always | [3.1.5](part_3_the_namespace.md#3.1.5) [2.6.1.3](#2.6.1.3) | The approving deferral:response:approved row, under the also role cites; the amendment it follows in refs.prev, absent on the base template (CC 2.7.11). |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**An admission of a unit: the members of an `admission:unit` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | where the row is one person's | [2.7.11](#2.7.11) [3.1.3](part_3_the_namespace.md#3.1.3) | The one person who admits; absent on a counted row, whose voices are its statements. Naming an effect, it admits only on the author's own host. |
| `unit` | `"unit"` | payload | `hash-digest` | always | [2.7.11](#2.7.11) | SHA-256 over the unit's bytes as the host loads them, or over its manifest; equals the CWT sub's digest. |
| `capabilities` | `"capabilities"` | payload | `[+ capability]` | always | [2.7.11](#2.7.11) [2.6.1.2](#2.6.1.2) | A set from the closed seven; the last five are effects. |
| `head` | `"refs"` | payload | `refs` | where the row is counted | [2.7.11](#2.7.11) [2.6.1.9](#2.6.1.9) | The roster head the count is over, in refs.head. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) [2.7.11](#2.7.11) | The lease opens. |
| `valid_until` | `"valid_until"` | payload | `ms-time` | always | [2.6.2](#2.6.2) [2.7.11](#2.7.11) | The lease closes: later than asserted_at, by at most unit_lease_max_secs. |

**A deferral response: the members this form names of a `deferral:response:{outcome}` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.1.9.3](part_3_the_namespace.md#3.1.9.3) [4.3](part_4_composition_governance.md#4.3) | The seated Wise Authority who answers. |
| `dimension` | `"dimension"` | payload | `tstr` | always | [3.1.9.3](part_3_the_namespace.md#3.1.9.3) | deferral:response:approved:v1 or deferral:response:rejected:v1. |
| `amendment_digest` | `"amendment_digest"` | payload | `hash-digest` | on an approval that authorises an identity amendment | [3.1.5](part_3_the_namespace.md#3.1.5) [2.1](#2.1) | The digest of the amendment approved. |
| `deferral_id` | `"deferral_id"` | payload | `tstr` | always | [3.1.9.3](part_3_the_namespace.md#3.1.9.3) | The request's own correlation id, copied from it. |
| `call_fingerprint` | `"call_fingerprint"` | payload | `hash-digest` | on an approval of a call | [2.7.11](#2.7.11) [4.3](part_4_composition_governance.md#4.3) | The fingerprint of the call approved; a dispatch resting on it executes only that call. |
| `references_attestation_id` | `"refs"` | payload | `refs` | always | [3.1.9.3](part_3_the_namespace.md#3.1.9.3) [2.6.1.3](#2.6.1.3) | The request answered, under answers. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**A deferral request: the members this form names of a `deferral:request` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attesting_key_id` | `"author"` | payload | `identity-ref` | always | [3.1.9.3](part_3_the_namespace.md#3.1.9.3) [4.3](part_4_composition_governance.md#4.3) | The deferring party: an agent's occurrence key, or a person's own key. |
| `deferral_id` | `"deferral_id"` | payload | `tstr` | always | [3.1.9.3](part_3_the_namespace.md#3.1.9.3) | The deferring party's own correlation id. |
| `reason_digest` | `"reason_digest"` | payload | `hash-digest` | always | [3.1.9.3](part_3_the_namespace.md#3.1.9.3) | The SHA-256 of the reason, which travels as bytes beside the row; a response carries none. |
| `references_attestation_id` | `"refs"` | payload | `refs` | where the request sends a handed case up | [3.1.9.3](part_3_the_namespace.md#3.1.9.3) [2.6.1.3](#2.6.1.3) | The request it was handed, under answers. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |
| `valid_until` | `"valid_until"` | payload | `ms-time` | always | [3.1.9.3](part_3_the_namespace.md#3.1.9.3) [4.3](part_4_composition_governance.md#4.3) | The request's own end, after which it re-routes. |

**A canonical re-bind: the payload of a `transport:canonical_rebind` row**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `"refs"` | payload | `refs` | always | [3.1.3](part_3_the_namespace.md#3.1.3) [2.6.1.11](#2.6.1.11) | The bundle in force the re-bind is counted over, in refs.head. |
| `transport_destination` | `"transport_destination"` | payload | `transport-destination` | always | [3.1.3](part_3_the_namespace.md#3.1.3) [3.3.6.2](part_3_the_namespace.md#3.3.6.2) | The seated node's new destination. |
| — | `"transit_xwing_pubkey"` | payload | `bstr .size 1216` | always | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) | The seat's new transit key. |
| — | `"onion_hop_xwing_pubkey"` | payload | `bstr .size 1216` | on a serve node | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) | The seat's new onion hop key. |
| `asserted_at` | `"asserted_at"` | payload | `ms-time` | always | [2.6.2](#2.6.2) | POSIX milliseconds. |

**The transport destination binding (`identity:occurrence`)**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `transport_destination` | `"transport_destination"` | payload | `transport-destination` | always | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) [3.3.6.3](part_3_the_namespace.md#3.3.6.3) | The RNS members, from which destination_hash is recomputed. |
| — | `"transit_xwing_pubkey"` | payload | `bstr .size 1216` | on a node that relays, and on every seat | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) | At the payload's top level, beside transport_destination; a seat's is taken from the bundle or a counted re-bind. |
| — | `"onion_hop_xwing_pubkey"` | payload | `bstr .size 1216` | on a node that relays, and on every serve node | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) | At the payload's top level, beside transport_destination. |
| — | `"dial_hints"` | payload | `[1*8 [uint .le 255, bstr .size (0..255)]]` | on a serve seat's binding in a genesis bundle, with at least one tcp hint; optional elsewhere | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) [2.6.8](#2.6.8) [5.3.4](part_5_transport_substrate.md#5.3.4) | At the payload's top level, beside transport_destination, inside what the seat signs. A cold-start seed only: the seat's live signed route row supersedes it once linked. |
| — | `"onion_relay"` | payload | `map` | on a node that opts out of relaying | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) [5.4.6](part_5_transport_substrate.md#5.4.6) | The opt-out marker; a node carrying it carries no hop key. |
| — | `"onion_relay"."opt_out"` | payload | `true` | always | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) | The constant true. |
| `references_attestation_id` | `"refs"` | payload | `refs` | on a seat's binding | [3.3.6.2](part_3_the_namespace.md#3.3.6.2) [2.6.1.11](#2.6.1.11) | The seat's own key record, under the also role cites. |
| — | `"reticulum_x25519_pubkey"` | payload | `bstr .size 32` | always | [3.3.6.3](part_3_the_namespace.md#3.3.6.3) | The RNS link X25519 key. |
| — | `"reticulum_ed25519_pubkey"` | payload | `bstr .size 32` | always | [3.3.6.3](part_3_the_namespace.md#3.3.6.3) | The RNS transport Ed25519 key. |
| — | `"app_name"` | payload | `tstr` | always | [3.3.6.3](part_3_the_namespace.md#3.3.6.3) | The RNS application name. |
| — | `"aspects"` | payload | `[* tstr]` | always | [3.3.6.3](part_3_the_namespace.md#3.3.6.3) [2.6.1.2](#2.6.1.2) | A sequence: the hash reads the aspects in this order. |
| — | `"destination_hash"` | payload | `bstr .size 16` | always | [3.3.6.3](part_3_the_namespace.md#3.3.6.3) | Recomputed by the two-stage hash; a disagreement is refused. |

**The seat commitment of a room key**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `room` | derived | `group-ref` | always | [2.6.1.11](#2.6.1.11) [3.3.4](part_3_the_namespace.md#3.3.4) | The room's derived id: the room member of the key record that carries the commitment. |
| — | `room_key` | derived | `kid` | always | [2.6.1.11](#2.6.1.11) | The room key's thumbprint. |
| — | `person` | derived | `identity-ref` | always | [2.6.1.11](#2.6.1.11) | The person's identity reference. |
| — | `nonce` | derived | `bstr .size 32` | always | [2.6.1.11](#2.6.1.11) | Thirty-two fresh random bytes. |

**The binding of a voice to its person, and what a wrap to a room key seals**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `room` | derived | `group-ref` | always | [2.6.1.11](#2.6.1.11) | The room's derived id. |
| — | `room_key` | derived | `kid` | always | [2.6.1.11](#2.6.1.11) | The thumbprint of the room key the binding is of. |
| — | `addressee_key` | derived | `kid` | always | [2.6.1.11](#2.6.1.11) | The thumbprint of the addressee's room key, never a node key. |
| — | `seat_commitment` | derived | `hash-digest` | always | [2.6.1.11](#2.6.1.11) | The commitment on the room key's record. |
| — | `binding_key` | derived | `bstr .size 32` | always | [2.6.1.11](#2.6.1.11) [2.6.1.12](#2.6.1.12) | The thumbprint of the person's binding key; its encoding is open. |
| — | `person` | derived | `identity-ref` | always | [2.6.1.11](#2.6.1.11) | The person the room key's holder names. |
| — | `nonce` | derived | `bstr .size 32` | always | [2.6.1.11](#2.6.1.11) | The nonce under the seat commitment. |
| — | `"dek"` | object | `bstr .size 32` | on a wrap to a room key | [2.6.1.11](#2.6.1.11) [3.3.2](part_3_the_namespace.md#3.3.2) | The wrapped key. A sealed envelope outside a wrap carries none. |
| — | `"claim"` | object | `binding-claim` | where the sender names its person to the recipient | [2.6.1.11](#2.6.1.11) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The first flow, from the room key's holder to the addressee. |
| — | `"challenge"` | object | `bstr .size 1120` | where the sender challenges the recipient's person | [2.6.1.11](#2.6.1.11) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The second flow, from the addressee: an X-Wing encapsulation to the person's binding key. |
| — | `"confirmation"` | object | `binding-confirmation` | where the sender answers the recipient's challenge | [2.6.1.11](#2.6.1.11) [3.1.3.2](part_3_the_namespace.md#3.1.3.2) | The third flow, from the room key's holder: an HPKE seal in PSK mode to the addressee's room key. |
| — | `"person"` | object | `identity-ref` | always | [2.6.1.11](#2.6.1.11) | The person claimed. |
| — | `"occurrence"` | object | `[+ bstr]` | where the addressee may hold no occurrence of the person | [2.6.1.11](#2.6.1.11) [3.3.6.1](part_3_the_namespace.md#3.3.6.1) | The statements of the person's identity:occurrence row that carries the binding key, as bytes: a sequence. |
| — | `"enc"` | object | `bstr .size 1120` | always | [2.6.1.11](#2.6.1.11) | The confirmation's own X-Wing encapsulation, to the addressee's room key. |
| — | `"ct"` | object | `bstr` | always | [2.6.1.11](#2.6.1.11) | The AEAD ciphertext over the opening. |

**A room's MLS group ids: what each is derived from**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `room` | derived | `group-ref` | always | [2.6.1.11](#2.6.1.11) [5.1](part_5_transport_substrate.md#5.1) | The room's derived id. |
| — | `room` | derived | `group-ref` | always | [2.6.1.11](#2.6.1.11) [5.1](part_5_transport_substrate.md#5.1) | The room's derived id. |
| — | `call` | derived | `bstr` | always | [2.6.1.11](#2.6.1.11) [2.6.1.12](#2.6.1.12) | The call's id; the member that carries it is open. |

**The id of a group: what its first version derives it from**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `group_kind` | derived | `"family" / "community"` | always | [3.3.4](part_3_the_namespace.md#3.3.4) [2.6.1.2](#2.6.1.2) | The first version's group_kind. |
| — | `first_members` | derived | `[+ identity-ref]` | always | [3.3.4](part_3_the_namespace.md#3.3.4) [2.6.1.2](#2.6.1.2) | The key of every member the first version lists: a set. |
| — | `founded_at` | derived | `ms-time` | always | [3.3.4](part_3_the_namespace.md#3.3.4) [2.6.1.2](#2.6.1.2) | The first version's founded_at. |
| — | `nonce` | derived | `bstr .size 32` | always | [3.3.4](part_3_the_namespace.md#3.3.4) [2.6.1.2](#2.6.1.2) | The first version's nonce. |

**A disclosure of a blinded member**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| — | `salt` | object | `bstr .size 16` | always | [2.6.1.10](#2.6.1.10) | Sixteen random bytes; a blinded map member is disclosed as [salt, value, key]. |
| — | `value` | object | `ceg-value` | always | [2.6.1.10](#2.6.1.10) | The blinded member's value. |
| — | `key` | object | `tstr` | always | [2.6.1.10](#2.6.1.10) | The blinded member's name; the digest is SHA-256 over the disclosure's bytes as sd_claims carries them. |
| — | `salt` | object | `bstr .size 16` | always | [2.6.1.10](#2.6.1.10) | Sixteen random bytes; a blinded array element is disclosed as [salt, value]. |
| — | `value` | object | `ceg-value` | always | [2.6.1.10](#2.6.1.10) | The blinded element's value. |
| — | `leaf_key` | object | `bstr .size 32` | always | [5.1](part_5_transport_substrate.md#5.1) | The value a blinded element of a leaf vouch discloses: first the leaf's Ed25519 public key. |
| — | `room` | object | `group-ref` | always | [5.1](part_5_transport_substrate.md#5.1) | The room the leaf is vouched for, by its derived id. |
| — | `suite` | object | `77` | always | [5.1](part_5_transport_substrate.md#5.1) | The constant 0x004D, equal to the row's suite. |

**Logical names with no member of their own**

| Logical name | CBOR member | Placement | Type | Required when | CC | Note |
|---|---|---|---|---|---|---|
| `attestation_id` | the row id | none | — | - | [2.6.1.3](#2.6.1.3) | Computed by every holder from the statement; the same for every voice of a counted row. |
| `attesting_key_id` | kid, iss and author | none | — | - | [2.6.1.7](#2.6.1.7) | kid names the signing key; iss the signer's stable identity; author the author of an authored row. |
| `attestation_type` | label -70001 | none | — | - | [2.6.1.1](#2.6.1.1) | One of the five. |
| `attested_key_id` | sub | none | — | - | [2.6.1.1](#2.6.1.1) | — |
| `references_attestation_id` | a member of refs | none | — | - | [2.6.1.3](#2.6.1.3) | Under the label the family's role gives it. |
| `wa_adjudication_ref` | a member of refs | none | — | - | [3.2](part_3_the_namespace.md#3.2) [2.6.1.3](#2.6.1.3) | On a rule-2 or rule-4 withdraws against a live owner-binding, the Wise-Authority quorum finding, under the also role cites; the owner-binding withdrawn is under target. |
| `additional_scrubs` | a further statement over the same payload | none | — | - | [2.6.1.9](#2.6.1.9) | Each voice is its own statement, found by the row id. |
| `original_content_hash` | none | none | — | - | [2.6.1.3](#2.6.1.3) | The earlier form's content hash; no row of this form names an earlier-form row. |
| `row` | none | none | — | - | [2.6.1.1](#2.6.1.1) | The protected header carries type, family and kid; the CWT claims carry iss and sub. |
| `context` | body.note | none | — | - | [2.6.1.10](#2.6.1.10) | Bounded; no free text outside it. |
| `cosignatures`, `quorum_signatures` | a co-signature of these families | none | — | - | [2.6.1.9](#2.6.1.9) | A further statement over the same payload, counted; never a payload member. |

<!-- END GENERATED: signed_object_v2 -->

**Logical names (normative).** This document names a row's members by logical names. Each stands in the statement as the table says, and a name with no member in this form says so.

| Logical name | In the statement |
|---|---|
| `attestation_id` | the row id ([CC 2.6.1.3](#2.6.1.3)); never a member |
| `references_attestation_id` | a row id inside `refs` ([CC 2.6.1.3](#2.6.1.3)) |
| `attesting_key_id` | `kid` (protected header, label 4) for the key that signs; `iss` (CWT claim 1) for the signer's stable identity; `author` in the payload of an authored family |
| `attested_key_id` | `sub` (CWT claim 2) |
| `attestation_type` | the row's type (protected header, label -70001) |
| the row's family | the row's family id (protected header, label -70002) |
| `row`, the mirror | none: the protected header and the payload carry what it mirrored |
| `subject_key_ids`, `cohort_scope`, `family_id`, `community_id`, `dimension` and the claim's other members | payload members of the same names |
| `score`, `confidence`, `weight` | payload integers at the scale of [CC 2.6.1.5](#2.6.1.5) |
| `asserted_at` | payload `asserted_at`, with `iat` derived from it ([CC 2.6.2](#2.6.2)) |
| `valid_from`, `valid_until` | payload members, with `nbf` and `exp` derived from them |
| `expires_at` | payload `expires_at` |
| `context` | `body.note` in the payload, bounded ([CC 2.6.1.10](#2.6.1.10)) |
| `evidence_refs` | payload `evidence_refs`, a sequence |
| the roster head a row names | `refs.head`, with further tips in `refs.further_heads` ([CC 2.6.1.9](#2.6.1.9)) |
| `additional_scrubs` | further statements over the same payload ([CC 2.6.1.9](#2.6.1.9)) |
| `scrub_key_id` | the `kid` of the further statement |
| the row's signature halves and `scrub_signature_classical`, `scrub_signature_pqc` | the statement's `signature`, one composite signature ([CC 2.6.1.7](#2.6.1.7)) |
| `pubkey_ed25519_base64`, `pubkey_ml_dsa_65_base64` | the composite key's `pub` (COSE key label -1), one byte string ([CC 2.6.1.7](#2.6.1.7)) |
| `key_id` | the composite key's thumbprint ([CC 2.6.1.7](#2.6.1.7), [CC 2.6.8](#2.6.8)) |
| `original_content_hash` | none: the row id commits to the payload, and no row names an earlier-form row ([CC 2.6.1.3](#2.6.1.3)) |
| `attestation_envelope` | the payload ([CC 2.6.1.2](#2.6.1.2)); the earlier form's object is [CC 8.11.9](part_8_appendices.md#8.11.9) |
| `registration_envelope` | none: a key record is the payload of a `key:record` row ([CC 2.6.1.7](#2.6.1.7)) |

**A family's payload (normative).** A family's payload carries the members its record names, one to one, and embeds no signed object. What a record carried as a co-signature is a further statement over the same payload, a counted voice ([CC 2.6.1.9](#2.6.1.9)), never a member. The table above states the payloads of `group:roster`, `membership:{stage}` at its stages `widening` and `removal`, `identity:occurrence_revocation`, `revocation:{entity_type}:{reason}`, `takedown_notice:{basis}`, `custody:{kind}`, `key_grant:{axis}` and `delivery_ack:{stream_id}`. A verifier refuses a payload that breaks its family's rule with `edition2_payload_invalid`, at step 3 of [CC 2.6.1.8](#2.6.1.8). Their schema is [`manifests/family_payloads_v2.cddl`](../manifests/family_payloads_v2.cddl), read together with [`manifests/signed_object_v2.cddl`](../manifests/signed_object_v2.cddl) as one schema.

#### 2.6.1.5 `numbers` — Numbers (normative)

No member of the payload is a float. A score, a confidence and a weight are integers at the fixed scale of 10^6: the value times 10^6. A score lies in [-10^6, 10^6], a confidence in [0, 10^6] and a weight in [0, 10^6], unless the family states a wider range.

A fold sums in signed 64-bit integers, so a sum is exact and a fold is a function of the set it reads. Its arithmetic is checked: a fold that would overflow concludes nothing, and never wraps. A derived value is computed in integers, rounded half away from zero unless its own rule states otherwise, and checked by exact equality. `n_eff` is a floor ([CC 6.1.2.3](part_6_the_coherence_mathematics.md#6.1.2.3)). Where every operand is non-negative, rounding ties up is the same rule.

A safety-battery row ([CC 3.1.5.5](part_3_the_namespace.md#3.1.5.5)) carries `passed` and `total` as unsigned integers below 2^32, both or neither. `total` is at least 1, and `passed` is at most `total`. With n = 10^6 · (2·passed − total), its score is sign(n) · ⌊(2·|n| + total) / (2·total)⌋, checked by exact equality. An indeterminate result carries no `score`, never a sentinel integer.

#### 2.6.1.6 `size` — Size (normative)

A payload's deterministic encoding MUST NOT exceed **1 MiB (1 048 576 bytes)**. The signed thing is the sized thing, so the bound is on the bytes the signature covers. A producer MUST NOT emit a payload above it. A substrate MUST refuse one at every write path with the reason `envelope_too_large`. Over HTTP that refusal is carried as status 413 with the error code `ENVELOPE_TOO_LARGE` ([CC 5.3.6.1](part_5_transport_substrate.md#5.3.6.1)).

Every write path MUST also enforce a finite ceiling on the octets it buffers from an untrusted source, and refuse at it with the same token without completing the decode. The ceiling is local, MUST NOT be below 1 MiB, and SHOULD be published. On a conforming path the received octets are the deterministic octets, so the two bounds coincide.

Above the cap the row carries the manifest, not the bytes. The payload moves to the blob plane as encrypted chunks ([CC 6.1.5](part_6_the_coherence_mathematics.md#6.1.5)), and the row names it by content hash in `evidence_refs`. The relocation adds no member and no primitive.

#### 2.6.1.7 `composite` — The composite signature and keys (normative)

A statement's signature is the composite ML-DSA-65 with Ed25519 of [composite-sig], exactly, at the revision [CC 2.6.5](#2.6.5) pins. Both halves sign one message representative: the prefix `CompositeAlgorithmSignatures2025`, the label `COMPSIG-MLDSA65-Ed25519-SHA512`, a zero byte for the empty context, and the SHA-512 of the message. ML-DSA-65 signs it with the label bytes as its FIPS 204 context string, never the empty one, and Ed25519 signs it as it is. The representative binds both halves, so neither half verifies alone. Its encoding is the ML-DSA-65 signature followed by the Ed25519 signature, 3373 bytes. Its algorithm identifier is `-70100`, private-use until one is assigned. A key's thumbprint covers the identifier, so `kid` and `iss` carry it and a new identifier renames every identity ([CC 2.6.1.8](#2.6.1.8)). A lineage therefore keeps `-70100` for its keys. A move to an assigned identifier is a planned migration, by a later bundle that seats the renamed keys, and never a silent change. ML-DSA-65 alone is COSE algorithm -49 ([RFC-9964]).

A key is one composite COSE key of key type AKP (kty 7). Its `pub` is the ML-DSA-65 public key followed by the Ed25519 public key, 1984 bytes. Its `kid` is its 32-byte thumbprint ([RFC-9679]) under the composite's identifier, fixed for the key's life. A key's displayed identity, its `key_id` and its FedCode, is that thumbprint ([CC 2.6.8](#2.6.8)). FedCode v1 to v3 belong to the earlier mesh.

`iss` is the identity reference of the signer's genesis key ([CC 2.6.1.1](#2.6.1.1)), so the issuer stays the same when the signing key rotates. A key record is a row of the family `key:record` ([CC 2.4.1.1](#2.4.1.1)), renewed by a `supersedes` and named by a rotation. Its payload carries `key`, `identity_type`, `asserted_at` and, where its end rule requires, `valid_until`, with `exp` derived from it.

**A statement's key MUST be a key of its `iss`** (step 8 of [CC 2.6.1.8](#2.6.1.8)). It is one where `kid` is the thumbprint inside `iss`: the genesis key, or a room key signing as itself. It is also one where the reader holds a record of that key whose own `iss` is the statement's, and that record reaches the genesis key's record through rotation records. It is also one that the bundle in force of an accord lineage the reader holds seats for that `iss` ([CC 2.6.1.11](#2.6.1.11)), as a recovery or a rotation by bundle does. Where that bundle is not held, the statement answers Waiting on it. The seat ends at the first later bundle in force that does not seat that key. It is also one that a live occurrence of `iss` binds: an `identity:occurrence` row of `iss` the reader holds, whose `occurrence_key_id` is the key ([CC 3.3.6](part_3_the_namespace.md#3.3.6)). That row is admitted under the two paths of [CC 3.3.6.4](part_3_the_namespace.md#3.3.6.4), not evicted, covers the statement's instant and carries the bound key's own statement. An occurrence is evicted only by an eviction that has concluded. An `identity:occurrence_revocation` cites in `refs.also` the key record of each of its voices and, where that key is bound by an occurrence, the occurrence. One that cites nothing is Invalid at the door, since it fails on its own bytes. One that cites its proof concludes as soon as the proof does, and the proof travels with it ([CC 3.3.6.4](part_3_the_namespace.md#3.3.6.4)). It never binds a `node` or `agent` key under an identity whose genesis record is `user` or `accord_holder` ([CC 2.4.1.1](#2.4.1.1)). A rotation record has the one shape of the `key:record` row of [CC 3.1.3](part_3_the_namespace.md#3.1.3). A renewal on the way, a `supersedes` by the key itself, leaves the chain where it was. A link stands where its predecessor's statement stands under [CC 2.4.1.1](#2.4.1.1): made inside the predecessor's record, and before the `revoked_after` of a revocation by that key itself. So a link made while its predecessor was live stands after that key has ended, and no other voice's revocation cuts a chain. A link through a rotation with a rival hands on nothing ([CC 2.4.1.1](#2.4.1.1)), and the statement is `kid_not_of_iss` until a rotation names both. Where no way reaches the genesis key and a row one needs is not held, the statement answers Waiting on that row. Such a row is a link of a chain, a voice a rotation record or an occurrence lacks, the bundle in force, or what an occurrence's admission needs. Otherwise it is Invalid, `kid_not_of_iss`: each held record of the key is of another identity, or its chain does not reach. Where a link fails only by its predecessor's own `revoked_after`, the detail is `rotation_after_revocation`. A reader that holds bare keys and no rows can show the first case only. The statements of a genesis bundle and of the accord's rows bind their key to the holder by the bundle in force instead ([CC 2.6.1.11](#2.6.1.11), [CC 4.2.1.1](part_4_composition_governance.md#4.2.1.1)).

`identity_type` is a set of roles ([CC 4.5.8](part_4_composition_governance.md#4.5.8)), and the key's end rule of [CC 2.4.1.1](#2.4.1.1) reads it as a set. A set that mixes `user` or `accord_holder` with `node` or `agent` is refused. A record whose set contains `user` or `accord_holder` carries no `valid_until`. One whose set contains `node` or `agent` carries one, unless it is a room key of a private room. A pseudonym's record MAY carry one, and a role outside both groups takes no end rule of its own. The bound is in milliseconds: `asserted_at` < `valid_until` ≤ `asserted_at` + `key_record_max_secs` × 1000. A record whose `valid_until` is not later than its `asserted_at` is Invalid at step 4 of [CC 2.6.1.8](#2.6.1.8). One that otherwise breaks the rule is refused `key_record_out_of_window`.

#### 2.6.1.8 `verification-three` — Verification has three answers (normative)

Verifying a statement gives one of three answers: **Valid**, **Invalid** with a reason, or **Waiting** on the keys it names as missing.

- A bad signature under a held key is Invalid, and that answer is final. A structural fault is Invalid whatever keys are held.
- A statement whose key record is Waiting is Waiting, naming the deepest missing key. A statement whose key record is Invalid is Invalid.
- A key is one composite key ([CC 2.6.1.7](#2.6.1.7)); a statement whose signer's key record is not held is Waiting on it, and a key never verifies on one half.
- Waiting never becomes Valid by default and is never counted. A waiting statement is held inert until the key it names is held ([CC 2.7.2](#2.7.2)).

```
On a statement received:
    1. Decode strictly: tag 18; the protected header and the
       payload in the deterministic encoding (CC 2.6.1.2)
    2. Check the header: typ on the closed list; alg -70100;
       edition 2; cty the constant; a row's type and family
       labels present, an object's absent
    3. Check the payload against the schema: no float or null,
       the sets, the ranges, passed and total; dimension
       resolving to the header's family; the family's own
       payload rule (edition2_payload_invalid)
    4. Check iat, nbf and exp against the payload, and that a
       valid_until is later than asserted_at (CC 2.6.2)
    5. Run the family's static checks, the key record's end
       among them
    6. Read kid; resolve the key record, or answer Waiting on it
    7. Verify the composite signature over the bytes received
    8. Check that kid's key is a key of iss (CC 2.6.1.7): Waiting
       on a chain link, a voice, the bundle in force or an
       occurrence not held; otherwise Invalid, kid_not_of_iss
    9. Check iss against author, or against the party of a role
       the family names (CC 2.6.1.3)
   10. Valid:
        a. apply the CC 2.1 defaults to absent members
           (interpretation time only)
        b. apply consumer policy (CC 4.4) to the result
   11. Store or forward the statement as received
```

A failure at steps 1 to 5 or 7 to 9 is Invalid. Steps 6 and 8 alone answer Waiting.

#### 2.6.1.9 `cosigned` — Counted rows and the second consent (normative)

A counted row is several statements over one payload, one for each voice, found by the row id. The head the row is counted over stands in `refs.head`, inside what every voice signs. Further tips stand in `refs.further_heads`, a set. One acknowledgement names one head. A fold counts the statements by person, as it counts votes ([CC 4.5.13](part_4_composition_governance.md#4.5.13)).

The second consent of a scoped `delegates_to` ([CC 2.4.1.2](#2.4.1.2)) is a second statement over the same payload, signed by the delegate, the row's `sub`. A scoped delegation seats only with that statement.

#### 2.6.1.10 `erasable` — Erasability and the redaction constraints (normative)

**Erasability is minted, never retrofitted.** The form is the selective disclosure of [SD-CWT]. A blinded member is absent from its map and is a disclosure, that draft's salted claim `[salt, value, key]`, whose salt is sixteen random bytes. Its digest stands in that map's `redacted_claim_keys` array, keyed by the simple value 59, in mint order. A blinded array element is tag 60 over its disclosure's digest, and its disclosure is `[salt, value]`. A digest is SHA-256 over the disclosure's bytes as `sd_claims` carries them. So a reader holding the statement alone sees how many members were minted blind and which are gone. Erasure drops a disclosure and alters no signed byte.

**A disclosure set is bytes, not a row member.** The statement replicates with its commitment and without its disclosures. The set is held on the bytes plane and fetched on demand under the consent edge that governs any bytes the object's audience may pull. Erasure is the bytes-plane tombstone, and a set that was never replicated is indistinguishable from one erased. The unprotected header's `sd_claims` (label 17) is where a set is presented beside its statement to one who may see it, never where it travels or is held.

**Which members are blind is a column of the family model** ([CC 3.1](part_3_the_namespace.md#3.1)), so a row that seals a member its family blinds is refused at the door. No fold, verdict or admission reads a member that can be blinded, since a node that erased it and one that did not would otherwise disagree. A family whose erasure route is a subject request or a purge MUST mint blind every free-text member, and every member another party authored, `body.note` first. Identifiers, instants, references and the digests themselves stay sealed. A family whose route is none or a legal hold seals its members, and its `body.note` carries nothing a subject request could reach. Every payload member is bounded, and `body.note` holds at most 2048 bytes. A payload MAY carry `reason`, a code from a closed registry.

**Redaction vs tampering — the signed-discriminator shape is excluded (normative dead end).** A signed "I redacted this" marker proves that an authorised party changed the bytes, not that only the redacted parts changed. A compromised or coerced authority key would then rewrite arbitrary content while every reader reports a legitimate redaction. Any redaction scheme is bound by four constraints:

- **(a) it lives on the envelope plane**, where the integrity gate is the row id at ingest, receiver-side; a storage-plane build is inert.
- **(b) it carries its own redactability declaration** in the signed object, unless it is uniformly redactable by construction; the selective disclosure above is this form, its declaration the family model's column.
- **(c) it lives above whole-row hashing**, which forecloses partial redaction downstream.
- **(d) the third option stays open**: a redacted row MAY simply be a different object carrying a different kind.

#### 2.6.1.11 `other-objects` — Receipts and the other signed objects (normative)

**Receipts** are COSE receipts ([RFC-9942]) over the SHA-256 tree of [RFC-9162], whose hashing is that of [RFC-6962], so every root already published stays valid. Each Transparency Service registers a statement in its own log and issues its own receipt over that log's root ([CC 5.3.1](part_5_transport_substrate.md#5.3.1)). The receipt carries the service's instant of issue, and no service signs inside another's log. A stream's receipts cover batches, never single chunks.

**Every other signed object** is a `COSE_Sign1` whose `typ` names its kind, from one closed list: `ceg-genesis-bundle/2`, `ceg-revocation-snapshot/2` and `ceg-boot-manifest/2`. A verifier MUST refuse any other `typ`. Its protected header carries exactly `alg`, `kid`, the CWT claims and `typ`, and no `cty`. Its CWT claims are `iss`, the edition claim and, where the object states an instant, `iat`. Its payload is the deterministic encoding of the schema its `typ` names. The payload rule of `ceg-boot-manifest/2` is an open encoding ([CC 2.6.1.12](#2.6.1.12)). A key record, a key revocation, a build manifest, safety evidence, an accord invocation and an agent's text manifest statement are rows. The family of the text manifest statement is an open encoding ([CC 2.6.1.12](#2.6.1.12)). The per-chunk media trailer of [CC 5.3.3.5](part_5_transport_substrate.md#5.3.3.5) and the substrate objects of [CC 6.1.3](part_6_the_coherence_mathematics.md#6.1.3) are the exceptions. Each stays a raw signature over fixed big-endian fields, and its preimage never parses as a COSE structure. A substrate object's signature is the composite of [CC 2.6.1.7](#2.6.1.7).

**The object id.** A signed object that is not a row is named by its object id: SHA-256 over the deterministic encoding of `["CEG-object/2", typ, author, payload]`, written as a row id is ([CC 2.6.1.3](#2.6.1.3)). `author` is the payload's `author`, or null where it has none. A `row-ref` of this form names the object by that digest. Like a row id, it is the same for every voice of a counted object.

**The genesis bundle** ([CC 5.3.4](part_5_transport_substrate.md#5.3.4)) carries its predecessor as `prev` in `refs`. Its `version` is a sequence from 1 and is never ranked. Where a bundle has a `prev`, its `version` is one greater than prev's, checked as a consistency check. The first bundle of this form has `version` 1 and no `prev`: it is a fresh genesis, the ceremony row of [CC 2.6.1.12](#2.6.1.12), and a signed object, not a row. A verifier follows `prev` to the head and reports a fork as a fork. With no state of its own it holds the tips, waiting. Two first bundles are a fork of the genesis: a reader anchored by the object id of one holds the other void, and a reader anchored by thumbprints reports the fork and roots on neither (*The anchor*, below).

**What a bundle carries and names.** A bundle's payload is a closed map of the members the table above lists, and carries no `author`, so its object id takes null. `holders` is the accord's roster and `serve_nodes` its seats, each a set of identity references. `charter` carries the accord's parameters, which no row carries ([CC 2.1](#2.1), [CC 4.2.6](part_4_composition_governance.md#4.2.6)). Every row the bundle seats stands in `refs.also` under `cites`, by row id, and is never copied into the payload. Those rows are the key record of each holder, seat and named Transparency Service, and the `transport_destination` binding of each seat ([CC 3.3.6.2](part_3_the_namespace.md#3.3.6.2)). Each is checked by its own family's payload rule, as it is alone. A seat's binding is an `identity:occurrence` whose `identity_key_id` and `occurrence_key_id` are the seat's identity reference, with `device_class` `server`. A seat's canonical conferral is the bundle's own count: a key listed in `serve_nodes` of the bundle in force is canonical ([CC 4.2.1](part_4_composition_governance.md#4.2.1)). That standing rides no key record, so it survives the seat's renewals and moves only by a later bundle. `holders`, `serve_nodes` and `transparency_services` are disjoint, so a reader places each named row by its family and its author alone. A bundle that names a row with no place, or two rows for one place, concludes nothing. A seat stands by the bundle that names it. The end of a seat's key record does not unseat it, and the seat's key renews by its own later record ([CC 2.4.1.1](#2.4.1.1)).

**How a bundle is counted.** A bundle is counted: one statement for each holder, over one payload. Each statement MUST carry `iat`, equal to `asserted_at` divided by 1000 and rounded down. The instant is the payload's, agreed before signing, so every holder's `iat` is the same whatever its clock reads ([CC 2.6.2](#2.6.2)). `iat` lies outside the object id, so a statement whose `iat` disagrees is Invalid on its own, and the bundle is counted on the statements that remain. The first bundle counts when every holder it lists has a valid statement over it, under the key its named key record holds. A later bundle counts when a strict majority of its predecessor's holders have valid statements over it, each under the key the predecessor names. Each holder it adds signs it too, as does each holder whose recovery commitment it changes ([CC 5.3.4](part_5_transport_substrate.md#5.3.4)). Each statement is that holder's proof of life and its yes ([CC 4.2.6](part_4_composition_governance.md#4.2.6)). A count not yet met concludes nothing, and the bundle is held.

**The first bundle's count stands.** A bound on a holder's key never unmakes the first bundle: its count stands once every holder it lists has made a valid statement over it. A holder's key revoked with no bound takes that holder out of the live holders and unmakes nothing ([CC 3.2](part_3_the_namespace.md#3.2) T8). Every later bundle is read by the bound: a statement over it that a holder's bound voids does not count ([CC 2.4.1.1](#2.4.1.1), [CC 3.2](part_3_the_namespace.md#3.2) T8 (viii)). A first bundle made with a holder key that was already compromised at the ceremony is not unmade by that holder's later bound. Nothing roots without the first bundle.

**A recovery is the one exception to the count** ([CC 4.2.6](part_4_composition_governance.md#4.2.6)). It is a later bundle with one statement. Its `iss` is the holder's identity reference, and its `kid` is the recovery key's thumbprint, resolved through the recovery key's record. The statement counts only where the predecessor's `recovery_commitments` entry for that `iss` equals the commitment over the recovery key, compared in constant time ([CC 3.2](part_3_the_namespace.md#3.2) T3). The bundle is self-contained, as the first is. Its `refs.also.cites` names the recovery key's record and the holder's new signing-key record, and its `recovery_commitments` entry for that holder is the next commitment. It counts on that one statement alone. A reader holds as spent every commitment that a counted recovery of the lineage it follows has used. The refusals are these:

- the recovery key is not the one the commitment in force commits to: the statement does not count, `recovery_commitment_mismatch`;
- the recovery key's commitment is spent: the statement does not count, `recovery_commitment_spent`;
- the new record's key is the recovery key, or a key any commitment of the lineage commits to: Invalid, `recovery_key_is_signing_key`;
- the new record's key is the holder's current key: Invalid, `recovery_reuses_signing_key`;
- anything changes against `prev` beyond that holder's key-record citation and its `recovery_commitments` entry, other than `version`, `asserted_at` and `refs.prev`: Invalid, `recovery_changes_other_seat`.

Any bundle that names a spent commitment concludes nothing, `recovery_commitment_spent`, so the next commitment never equals the one a recovery spends. Two later bundles that count on one predecessor are a fork, and the genesis rule applies. A reader reports the fork, holds both as tips, and acts on what every tip names, the holders and seats common to them ([CC 2.7.8](#2.7.8)).

**Which key a later bundle seats.** Each statement over a later bundle counts under the key the predecessor seats for its holder. A statement under any other key is refused alone, `statement_kid_not_iss`, since a holder's key changes only by a bundle. Outside a recovery, a later bundle may seat a holder at a new key only where that holder's statement under its current key counts in it. That is routine rotation: it spends no recovery commitment, and the holder's own voice under the old key is its consent. Otherwise the bundle concludes nothing, `genesis_bundle_row_invalid`, with the detail `holder_not_genesis_key`.

**A key a holder cannot return to.** A holder's retired set holds every key the lineage seated it at and it left, and every recovery key a counted recovery of it spent. A later bundle that seats a holder at a key other than the predecessor's is Invalid, `holder_key_retired`, where that key is in the holder's retired set or is the key its in-force commitment commits to, compared in constant time. The check reads the cited records and the predecessor only, never which statements are held.

**The anchor.** A reader's anchor is what the reader was built or configured to trust, never a member of the wire ([CC 5.3.4](part_5_transport_substrate.md#5.3.4)). A release carries a default anchor, and a reader may be re-rooted to another. An anchor is the object id of one first bundle, or the set of its holders' thumbprints. An object-id anchor selects that bundle, and any other first bundle is void for the reader ([CC 2.7.8](#2.7.8)). Under a thumbprint anchor, a first bundle verifies only where its `holders` equal the anchored set and every one of them signed it. Two first bundles that both do so are a fork, and the reader roots on neither. A reader rooted on no bundle has no root: it runs no agent and serves no directory or seat of that mesh until its owner re-anchors it, by the object id of one bundle. A reader's anchor changes only by its owner's act, never by which bundle arrived first.

**What a bundle waits on.** A named row, a predecessor or a voice's key record that the reader does not hold answers Waiting on it, and nothing else does. A named row that is Invalid leaves the bundle concluding nothing, never refused for that row. Every holder's and seat's key record verifies under its own key, so a bundle and the rows it names verify with no key from outside them. A holder is seated only through the custody gate of [CC 4.2.2.1](part_4_composition_governance.md#4.2.2.1). A seat's key record covers the bundle's instant: its `valid_until` is later than the bundle's `asserted_at`. A seat's binding names that key record by row id in `refs`, under the `also` role `cites` ([CC 3.3.6.2](part_3_the_namespace.md#3.3.6.2)). A valid bundle yields its placement: the holders, and each seat with its binding's `transit_xwing_pubkey` and `onion_hop_xwing_pubkey`, so a consumer does not place them again.

**The order of verification.** A reader verifies a bundle in this order, and the first of steps 2 to 6 that answers gives the bundle's answer:

1. Each statement alone: its signature, its `typ`, its `kid`, its role and its `iat`. A statement that fails is refused alone, and the bundle is read on the rest. The refusals are `statement_invalid`, `statement_not_genesis_bundle`, `statement_kid_not_iss`, `statement_no_role`, `iat_mismatch` and `iat_missing`.
2. The payload against its rule. A fault is Invalid, `genesis_bundle_malformed`, with the detail the table below names.
3. For a first bundle, the anchor: otherwise `genesis_bundle_not_anchored`. For a later bundle, `prev`: Waiting where it is not held, `genesis_bundle_prev_not_valid` where it is held and not Valid, and Invalid where `version` or `family_key_id` disagrees with it ([CC 3.2](part_3_the_namespace.md#3.2)).
4. The named rows: Waiting on a row not held; `genesis_bundle_row_unplaced` for a row with no place or two rows for one place; `genesis_bundle_row_invalid` for a row that is Invalid or breaks a seat's rule above. Its details are `row_invalid`, `row_signer`, `row_author_not_iss`, `holder_not_accord_holder`, `holder_not_genesis_key`, `seat_not_node`, `seat_opted_out`, `seat_record_ended`, `binding_no_transport_destination`, `binding_xwing_member`, `binding_earlier_transit_pair`, `binding_names_no_record` and `seat_dial_hints_missing`, where a serve seat's binding carries no `tcp` dial hint. A dial hint of a known type whose body is malformed makes its row Invalid, `dial_hint_malformed` ([CC 2.6.8](#2.6.8)). A recovery that breaks one of its Invalid rules above is Invalid here, once its records are placed, and then any bundle that seats a retired key is Invalid, `holder_key_retired`. Every Invalid answer comes before any answer that turns on which statements are held. `holder_not_genesis_key` reads as a holder record whose key is not the key the bundle in force seats for that holder, so a recovered holder's new record is its seat. A bundle is read as a recovery only once its one statement's signature verifies, so a forged statement never makes another's bundle Invalid.
5. The custody gate of each holder it seats: `genesis_holder_custody`. Its details are `custody_no_class`, `custody_unattested`, `custody_chain_invalid`, `custody_attested_key_mismatch`, `custody_floor_not_met` and `custody_pq_not_removable_offline`.
6. The count: `genesis_bundle_count_unmet` where it is not met, with the detail `recovery_commitment_mismatch` or `recovery_commitment_spent` where a recovery's statement does not count or a bundle names a spent commitment.

Every other answer from step 3 on is Waiting or concludes nothing. The details of a malformed bundle are these:

| Detail | The fault |
|---|---|
| `version_prev_mismatch` | `version` is not 1 exactly when `prev` is absent, or not one greater than prev's |
| `holders_seats_overlap` | `holders`, `serve_nodes` and `transparency_services` are not disjoint |
| `recovery_commitments_not_holders` | the keys of `recovery_commitments` are not exactly `holders` |
| `scope_missing_infra` | `scope` lacks `infra:attest` or `infra:serve` |
| `transparency_members_partial` | the three transparency members stand only in part |
| `receipt_quorum_mismatch` | `receipt_quorum` is not ⌊\|`transparency_services`\|/2⌋ + 1 |
| `federation_set_semantics_unsorted` | a set is not in its order or holds a duplicate ([CC 2.6.1.2](#2.6.1.2)) |
| `family_key_id_changed` | a later bundle changes `family_key_id` ([CC 5.3.4](part_5_transport_substrate.md#5.3.4)) |
| `recovery_key_is_signing_key` | a recovery's new signing key is the recovery key, or a key a commitment of the lineage commits to |
| `recovery_reuses_signing_key` | a recovery's new signing key is the holder's current key |
| `recovery_changes_other_seat` | a recovery changes more than its holder's key-record citation and commitment |
| `holder_key_retired` | a later bundle seats a holder at a key in its retired set, or at the key its in-force commitment commits to |
| `holder_device_shared` | two holders the bundle seats name one device in their attestation leaves ([CC 4.2.3](part_4_composition_governance.md#4.2.3)) |
| `recovery_commitment_shared` | two holders the bundle seats carry one recovery commitment ([CC 4.2.6](part_4_composition_governance.md#4.2.6)) |
| `recovery_commitment_is_holder_key` | a holder's recovery commitment is the commitment over a signing key the bundle seats, its own or another holder's ([CC 4.2.6](part_4_composition_governance.md#4.2.6)) |
| `genesis_bundle_schema` | any other fault against the bundle's schema |

**The revocation snapshot** is a set of revoked keys, with no winner across issuers, and it carries no instant. Its payload names its signer as `author`, so its object id is one signer's. Each snapshot carries `seq`, an unsigned integer greater than its predecessor's, beside `refs.prev`, so one signer orders its own snapshots. Under the `also` role `ack` it names its acknowledgement of the head of the revocation scope. Each revoked entry is a tuple: the revoked key's thumbprint, its revocation and the rows it held good. The snapshot names its `refs` and, in each entry, the revocation and the rows held good. A snapshot whose `seq` is not greater than that of the `prev` it names concludes nothing. Two snapshots of one signer with one `seq` and different content are contested, and neither counts.

No rule ranks statements of different issuers by `iat`, and no helper picks the latest across issuers ([CC 2.7.2](#2.7.2)).

**One key exchange.** One hybrid KEM, X-Wing, serves every key wrap and every onion hop ([CC 5.4.6](part_5_transport_substrate.md#5.4.6)), under HPKE where a wrap is single-shot. The transit handshake of [CC 5.3.3.10](part_5_transport_substrate.md#5.3.3.10) is not a single-shot wrap; it is a KEM-authenticated handshake with X-Wing inside it.

**Room keys** ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). A voice is named by the identity reference of its first room key, and the name outlives that key. On every row a room key signs, `iss` is the voice and `kid` is the room key that signed. Neither is ever the person's. A voice's first key signs as itself, and a further key is a key of the voice by its `identity:occurrence` in the room ([CC 3.3.6.4](part_3_the_namespace.md#3.3.6.4)). Every row of a private room names the head of its signer's voice roster in `refs.also` under the role `voice`, a set of exactly one. For a voice of one key that head is the key's own record. A row of the voice's own key roster names that head in `refs.head`, as a self-roster row does. A row concludes only if the room key that signed it is a live key of the voice at the head the row names. A row of a private room that names no such head is refused. A room key's record carries `room`, the derived id of the one room the key is made for ([CC 3.3.4](part_3_the_namespace.md#3.3.4)). That member makes the record a room key's. The record carries `kem_xwing_pubkey`, the key's KEM key: an X-Wing public key of 1216 bytes, to which every wrap for that key is made. The record carries `seat_commitment`, which the binding opens. So the seat row of a room key is its own key record, and no row carries more than one commitment. `kem_xwing_pubkey` and `seat_commitment` are present exactly where `room` is. A record that carries either and no `room`, or `room` and not both, is refused `edition2_payload_invalid`. The commitment is SHA-256 over the deterministic encoding of `["CEG-seat/2", room, room_key, person, nonce]`, written as `[-16, digest]`. `room` is the record's `room`. `room_key` is the key's thumbprint, `person` an identity reference and `nonce` 32 fresh random bytes. An identity's binding key is `room_binding_xwing_pubkey`, a top-level member of its `identity:occurrence` beside `encryption_pubkeys` ([CC 3.3.6.1](part_3_the_namespace.md#3.3.6.1)). Its halves and those of the other KEM keys on that row are distinct bytes, and a node refuses at admission a row where they are not. The HPKE `info` of an invitation is the text `CEG-invitation/2`, and of a wrap to a room key `CEG-room-wrap/2`.

**The binding of a voice to its person** ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). A binding is three flows between two devices. M holds the room key R and the person's binding key. A, the addressee, holds a room key of its own in the same room. The claim goes from M to A. It is the person's identity reference, with the person's occurrence that carries the binding key where A may hold none. The challenge goes from A to M. It is `ct_c`, an X-Wing encapsulation to the person's binding key, of 1120 bytes. The confirmation goes from M to A. It is an HPKE seal in PSK mode ([RFC 9180](https://www.rfc-editor.org/rfc/rfc9180)) to the `kem_xwing_pubkey` of A's room key:

```
mode     = mode_psk
KEM      = X-Wing        (kem_id  = 0x647a)
KDF      = HKDF-SHA256   (kdf_id  = 0x0001)
AEAD     = AES-256-GCM   (aead_id = 0x0002)
psk      = the shared secret of the challenge
psk_id   = SHA-256(ct_c)
info     = the deterministic encoding of ["CEG-binding/2", room, room_key, addressee_key, seat_commitment, binding_key]
aad      = empty
pt       = the deterministic encoding of [person, nonce]
```

`room_key` is the thumbprint of R. `addressee_key` is the thumbprint of A's room key, and never a node key. `seat_commitment` is the commitment on R's record. `binding_key` is the thumbprint of the person's binding key, whose encoding is open ([CC 2.6.1.12](#2.6.1.12)). A opens the confirmation. A MUST check that `person` is the one it challenged. A MUST check that SHA-256 over the deterministic encoding of `["CEG-seat/2", room, room_key, person, nonce]` equals `seat_commitment`. The confirmation's AEAD authenticates the opening under both shared secrets, so a separate MAC adds no property. No seed is derived and no label names one. The AEAD nonce is HPKE's own. One exchange is made for each room key, each with a fresh challenge, and the addressee challenges first. A checks that the binding key stands on a live occurrence of the person. That check is A's own, made when it opens the confirmation, and it binds nobody else. The bytes of the three flows are fixed with the verifier's known-answer vectors, over X-Wing as [X-Wing] states it.

**A wrap to a room key.** A wrap to a room key is a `key_grant` row whose `wrap_algorithm` is `xwing_hpke_aes256_gcm_hkdf_sha256`. It is HPKE base mode under the same three identifiers, to the `kem_xwing_pubkey` of the recipient room key's record, with `info` the text `CEG-room-wrap/2` and empty `aad`. `wrapped_dek` is the encapsulation `enc`, of 1120 bytes, then the AEAD ciphertext. The plaintext is the deterministic encoding of a map. The map carries `dek`, the wrapped key, and whichever flows of a binding ride that wrap: `claim`, `challenge` and `confirmation`. The row's signature covers the ciphertext alone, so no flow is a cleartext member of a row. No flow rides an MLS Welcome. A wrap's own encapsulation is never the confirmation. A wrap to a room key carries this `wrap_algorithm` and no other, and it is not a wrap of the earlier string. The same map with no `dek`, sealed the same way to one room key, is the sealed envelope of [CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2).

**A room's MLS group ids** ([CC 5.1](part_5_transport_substrate.md#5.1)). The id of each MLS group of a room is derived, so a door recomputes which room a group is of. The chat group's id is SHA-256 over the deterministic encoding of `["CEG-mls-group/2", room]`. A call group's id is SHA-256 over the deterministic encoding of `["CEG-mls-call-group/2", room, call]`. `room` is the room's derived id ([CC 3.3.4](part_3_the_namespace.md#3.3.4)). `call` is the call's id, and the member that carries it is an open encoding ([CC 2.6.1.12](#2.6.1.12)). A group whose id is neither is a group of no room.

No Transparency Service or registrar decides what a node admits or serves: a reader's own trust decides that ([CC 4.4.3.34](part_4_composition_governance.md#4.4.3.34)). Anyone MAY run a Transparency Service under their own key, and its receipt shows registration and confers nothing ([CC 2.7.11](#2.7.11)).

#### 2.6.1.12 `earlier-form` — The earlier form and the cutover (normative)

The earlier signed object is [CC 8.11](part_8_appendices.md#8.11): a JSON object signed over its JCS image, the form of the earlier mesh. This edition begins a new mesh with a fresh genesis of this form ([CC 2.6.4](#2.6.4)), signed by every holder ([CC 5.3.4](part_5_transport_substrate.md#5.3.4)), and its genesis bundle is the **ceremony row**.

Nothing of the earlier mesh comes across. No row of this form names an object of the earlier form, and no object of the earlier form gives standing to anything in this mesh. Every key record, binding, roster, edge, consent, grant, recovery commitment and pre-signed halt is signed anew in this form ([CC 2.4.1.1](#2.4.1.1), [CC 5.3.4](part_5_transport_substrate.md#5.3.4)). Every holder mints a fresh key for the genesis, both its halves, under the custody of [CC 4.2.3](part_4_composition_governance.md#4.2.3). A node that upgrades MUST destroy its store of the earlier mesh, keeping a record of the destruction with counts and no content. A live legal hold on that store stops the upgrade until the hold lifts ([CC 4.4.3.12](part_4_composition_governance.md#4.4.3.12)). A node of the long-term-support line conforms to that line's text.

A node of this form reads and writes this form only. It refuses an object of the earlier form, so the earlier form is never offered in place of this one and no downgrade is possible. The earlier mesh and this one share no rows, and a node that has not upgraded stays in the earlier mesh.

The known-answer vectors of this object are the verifier's: the row id, the refusals of non-deterministic encodings, the order of the sets in `refs`, a counted row as several statements, and the three answers.

The verifier publishes fourteen files of them ([edition-2-vectors]). Its vectors for the trust root, the node code, receipts and stream heads are the nine files of [trust-root-vectors]. Its known answers for the build manifest blob and its tree are [build-manifest-vectors], and those for a group's id are [group-id-vectors]. The composite signature's is checked against the examples of [composite-sig]. The row statements hold four valid statements and 42 refusals, with 17 key records, the custody cases of [CC 4.2.2.1](part_4_composition_governance.md#4.2.2.1) among them, and references. The substrate file holds one composite signature for each preimage. The recovery commitment file holds six known answers of the commitment of [CC 3.2](part_3_the_namespace.md#3.2) T3, over one key and over a set. The stream key binding file holds its two bindings ([CC 5.3.3.5](part_5_transport_substrate.md#5.3.3.5)). The link handshake file holds three handshakes, one promotion, two framing cases and 38 refusals ([CC 5.3.3.10](part_5_transport_substrate.md#5.3.3.10)). The link seal file holds 25 scripted receiver sequences of the per-frame seal ([CC 5.3.3.10](part_5_transport_substrate.md#5.3.3.10)). The first genesis bundle file holds 70 cases of the bundle's reading, first and later bundles, with their pool of statements. The second holds 105, recoveries, rotations, retired keys and forks of later bundles among them. The accord halt file holds four invocations, 15 lifecycle rows, 14 refused invocations and 12 latch sequences of the halt row ([CC 4.2.1.1](part_4_composition_governance.md#4.2.1.1)). The second holds 21 invocations, 22 lifecycle rows and 13 latch sequences, and in it a halt by a key outside the bundle in force waits. The key of iss file holds 24 cases of step 8 of [CC 2.6.1.8](#2.6.1.8): nine valid, nine `kid_not_of_iss`, five waiting and one family fault. The third row statements file holds the same four valid statements, 42 refusals, 17 key records and 11 references. It adds 42 cases read under a family model, four groups of statements read together, four read through a key-record directory and six other objects. The genesis re-seat file holds four cases of a later bundle that seats a seat at a new key. The vectors of the revocation snapshot and the boot manifest are still the verifier's to publish.

**Open encodings.** Each encoding below waits on its owner's submission. The section it stands in states what is fixed of it and cites this table:

| Open encoding | Section | Owner |
|---|---|---|
| The payload rule of `ceg-boot-manifest/2`. Its member `build_manifest_row`, a `row-ref`, is the server's and is fixed | [CC 2.6.1.11](#2.6.1.11), [CC 3.1.2.1](part_3_the_namespace.md#3.1.2.1) | server |
| The member of a stream key binding that states the head interval | [CC 5.3.3.8](part_5_transport_substrate.md#5.3.3.8) | edge |
| The family of the agent text manifest statement | [CC 2.6.1.11](#2.6.1.11), [CC 3.1.2.1](part_3_the_namespace.md#3.1.2.1) | agent |
| The member that carries a call's id, which a call group's MLS group id is derived from | [CC 2.6.1.11](#2.6.1.11), [CC 5.1](part_5_transport_substrate.md#5.1) | edge |
| The thumbprint of a binding key, as a binding's `info` carries it | [CC 2.6.1.11](#2.6.1.11) | verifier |
| The contents of a sealed invitation and of its return beyond a binding's flows; the key a first invitation is sealed to; how a sealed envelope travels | [CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2) | edge |
| The signing bytes of a skill import manifest | [CC 3.1.2.1](part_3_the_namespace.md#3.1.2.1) | agent |
| A locale manifest's leaf | [CC 3.1.2.1](part_3_the_namespace.md#3.1.2.1) | agent |
| The preimage of a steward purge's selection digest | [CC 3.3.2](part_3_the_namespace.md#3.3.2) | store |
| The plaintext of a sealed descriptor | [CC 3.3.13](part_3_the_namespace.md#3.3.13) | client |
| The payloads of the Self-at-login rows | [CC 4.4.3.20](part_4_composition_governance.md#4.4.3.20) | verifier |
| The member that serves a genesis bundle's object id | [CC 5.3.4](part_5_transport_substrate.md#5.3.4) | server |
| The members, placement and types of the census | [CC 6.1.9](part_6_the_coherence_mathematics.md#6.1.9) | store |

### 2.6.2 `instants` — Instants (normative)

`asserted_at`, `valid_from`, `valid_until`, `expires_at` and every other instant in a payload are unsigned integers of POSIX milliseconds, never floats. The header's `iat`, `nbf` and `exp` are the standard seconds claims, each the floor of its payload member divided by 1000. A verifier MUST refuse a statement whose header claim disagrees with its payload member. A row or object covers an instant t when its `asserted_at` ≤ t < its `valid_until`, as a header `exp` reads. A payload that states `valid_until` MUST state it later than its `asserted_at`, since an equal one covers nothing. A statement that breaks this is Invalid, `valid_until_not_after_asserted_at`, at step 4 of [CC 2.6.1.8](#2.6.1.8).

### 2.6.3 `text-forms` — Text forms a person reads (normative)

Hex occurs only inside a text identifier and the signed text below, never for bytes in a payload. Every hex string in such an identifier MUST be **lowercase**, **unpadded** (no leading `0x`, no separators) and **byte-length-exact**: a SHA-256 digest is exactly 64 hex characters. This governs the `{hex}` segment of a `canonical:{hashalg}:{hex}` subject ([CC 2.3.2.1](#2.3.2.1)), a 64-hex `key_id` a directory still holds, and an H3 `cell_id` ([CC 2.6.6](#2.6.6)). FedCode is base32 as [CC 2.6.8](#2.6.8) states. An identity reference is base64url as [RFC-9679] requires ([CC 2.6.1.1](#2.6.1.1)), and this rule does not govern it. A verifier MUST refuse uppercase hex.

Where bytes stand in a signed text preimage or an HTTP member, they are hex under the same rule. Where an instant stands in signed text or an HTTP member, it is the canonical [RFC-3339] form `YYYY-MM-DDTHH:MM:SS.sssZ`: UTC with an uppercase `Z`, never `+00:00` or a lowercase `z`, and exactly three digits of fractional seconds. An example is `2026-05-28T13:45:09.000Z`. Producers MUST emit these forms, and a verifier MUST refuse any other form when it verifies a signature.

### 2.6.4 `policy-versioning` — Versioning policy

The grammar can evolve only if every change announces whether it breaks the wire. SemVer makes that announcement machine-legible, so a peer knows from the version alone whether it can still interoperate.

CEG follows **SemVer 2.0.0** with these mapping rules:

- **MAJOR (X.0.0)** — any wire-incompatible change: removal of an envelope field, change of a field's semantic, removal of a structural primitive, or change to canonical-bytes domain-separation labels. Also MAJOR: removal or breaking-redefinition of a [CC 3.1](part_3_the_namespace.md#3.1) prefix, change to a [CC 3.4](part_3_the_namespace.md#3.4) reservation, or change to the CC 2.6.9 / CC 2.2 conformance language.
- **MINOR (0.X.0)** — wire-compatible additions: new prefix in [CC 3.1](part_3_the_namespace.md#3.1), new envelope field with documented default, new composition policy in [CC 4.4](part_4_composition_governance.md#4.4), new endpoint shape in [CC 5.3](part_5_transport_substrate.md#5.3), new optional conformance subsection. Existing Conforming Producers and Consumers continue to interoperate without modification.
- **PATCH (0.0.X)** — clarifications, editorial fixes, additions to non-normative sections (open-vocabulary lists, glossaries [CC 8.1](part_8_appendices.md#8.1)), addition to [CC 8.3](part_8_appendices.md#8.3) acknowledged-gaps, fixes to non-normative examples in [CC 8.1](part_8_appendices.md#8.1).

The wire surface is frozen at 1.0. Until 1.0 is cut this document is a release candidate. A release candidate ordinarily adds, clarifies and corrects under the MINOR and PATCH rules above and moves no signed byte. Where a candidate must move signed bytes before 1.0, it says so in its own text, and begins a new mesh with a fresh genesis of the new form, in which nothing of the earlier one counts. The CBOR and COSE signed object of [CC 2.6.1](#2.6.1) is such a move, and the earlier form is [CC 8.11](part_8_appendices.md#8.11). The MAJOR rule binds from 1.0: a MINOR may add an optional member, and a row signed before the addition verifies unchanged. From 1.0, a change that would alter the signed bytes of any conforming row is a new MAJOR, announced as such.

A **removal notice** is given by marking the affected element as scheduled for removal, naming the version that gives notice and a removal target (e.g., `removal: 2.0`). An element under notice MUST remain interoperable until the announced removal version. Removal is a MAJOR change per the rules above.

**The wire vocabulary is a hash-pinned artifact.** The set of message types the substrate recognizes — the *wire vocabulary* — is not the emergent product of individual repos' needs but a ratified contract. The contract is expressed as a versioned, hash-addressable artifact, [`manifests/WIRE_VOCABULARY.md`](../manifests/WIRE_VOCABULARY.md), governed in **two tiers** (the RFC 8126 partitioned-registry discipline). **Tier 1** holds the message types whose canonicalization is load-bearing to an ethical primitive (attestations, votes, moderation/slashing, deferral, steward directives, key registration, the humanity-accord path, `withdraws`, goals, build provenance, content/blob fetch). Tier 1 is closed and CC-ratified: a Tier-1 addition rides the ordinary [CC 4.5.1](part_4_composition_governance.md#4.5.1) amendment (the "Standards Action" bar), a working reference implementation, and a coordinated cut. **Tier 2** — app-tier remote-procedure channels whose inner semantics are the app's concern — uses three opaque envelopes (`OpaqueRequest` / `OpaqueResponse` / `OpaqueEvent`) carrying a `kind` from a reserved per-repo range delegated to the range steward (the "Private Use" bar). No CC amendment is required to define a `kind`. Every ratifying repo **pins the artifact's SHA-256 at build**; a hash mismatch at cohabitation is a substrate-tier build failure, not a warning. Amendment is a substrate-coordinated event across the covenant of ratifying repos; unanimous hash-commit blocks the *cut*, never the *decision* (the decision is the CC 4.5.1 amendment). This governs the **transport vocabulary** — a surface distinct from, and complementary to, the frozen [CC 1.7](part_1_foundation.md#1.7) 1+4 attestation grammar: 1+4 freezes what a claim *is*; the wire vocabulary governs the message types that *carry* claims.

### 2.6.5 `references` — Normative References

The following documents are normatively cited; implementations MUST conform to them where referenced inline.

| Short name | Normative document |
|---|---|
| [BCP 14] | [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) + [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) — keywords for use in RFCs |
| [FIPS-180-4] | [FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) — SHA-256 and the SHA-2 family |
| [FIPS-202] | [FIPS 202](https://csrc.nist.gov/pubs/fips/202/final) — SHA-3 / SHAKE128 / SHAKE256 / TupleHash |
| [FIPS-204] | [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final) — ML-DSA (Module-Lattice-Based Digital Signature Algorithm); CEG uses parameter set ML-DSA-65, the post-quantum half of the composite signature ([CC 2.6.1.7](#2.6.1.7)) |
| [RFC-3339] | [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) — Date and Time on the Internet, the instant form of the earlier signed object ([CC 8.11.10](part_8_appendices.md#8.11.10)) |
| [RFC-5905] | [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905) — Network Time Protocol Version 4 |
| [RFC-6962] | [RFC 6962](https://www.rfc-editor.org/rfc/rfc6962) — Certificate Transparency; this spec's transparency-log discipline tracks 6962 except where 6962-bis (RFC 9162) supersedes |
| [RFC-8032] | [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032) — Edwards-Curve Digital Signature Algorithm (EdDSA); specifically Ed25519 |
| [RFC-8174] | [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (with BCP 14) |
| [RFC-8785] | [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) — JSON Canonicalization Scheme (JCS); the signing input of the earlier signed object ([CC 8.11.5](part_8_appendices.md#8.11.5)) |
| [RFC-9162] | [RFC 9162](https://www.rfc-editor.org/rfc/rfc9162) — Certificate Transparency v2.0 (CT-bis); MUST be used for new transparency-log integrations; older 6962 instances continue to interoperate |
| [ISO-639-1] | [ISO 639-1:2002](https://www.iso.org/standard/22109.html) — Codes for the representation of names of languages, two-letter |
| [BCP-47] | [BCP 47](https://www.rfc-editor.org/info/bcp47) ([RFC 5646](https://www.rfc-editor.org/rfc/rfc5646)) — Tags for identifying languages; for locale strings richer than ISO 639-1 alone |
| [RFC-9420] | [RFC 9420](https://www.rfc-editor.org/rfc/rfc9420) — Messaging Layer Security (MLS); the streaming epoch-key rekey ([CC 5.1](part_5_transport_substrate.md#5.1)) conforms to MLS TreeKEM |
| [SFrame] | [RFC 9605](https://www.rfc-editor.org/rfc/rfc9605) — Secure Frame (SFrame); the per-frame AEAD chunk seal ([CC 5.3.3.1](part_5_transport_substrate.md#5.3.3.1)) conforms to the SFrame model |
| [FIPS-203] | [FIPS 203](https://csrc.nist.gov/pubs/fips/203/final) — ML-KEM (Module-Lattice KEM); the post-quantum half of the hybrid KEM (ML-KEM-768) |
| [RFC-9180] | [RFC 9180](https://www.rfc-editor.org/rfc/rfc9180) — Hybrid Public Key Encryption (HPKE); the `key_grant` wrap shape |
| [RFC-4648] | [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648) — The Base16, Base32, and Base64 Data Encodings; the base64 pin of [CC 8.11.3](part_8_appendices.md#8.11.3) and the base32 `key_id` fingerprint |
| [RFC-8949] | [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949) — Concise Binary Object Representation (CBOR); the signed object ([CC 2.6.1](#2.6.1)) and the deterministic-CBOR `record_id` profile ([CC 5.3.3.2](part_5_transport_substrate.md#5.3.3.2)) |
| [RFC-5869] | [RFC 5869](https://www.rfc-editor.org/rfc/rfc5869) — HMAC-based Extract-and-Expand Key Derivation Function (HKDF); every key derivation of Part 5 |
| [X-Wing] | [draft-connolly-cfrg-xwing-kem](https://datatracker.ietf.org/doc/draft-connolly-cfrg-xwing-kem/) — X-Wing: general-purpose hybrid post-quantum KEM; the onion hop key and the hybrid KEM of Part 5 |
| [HPKE-PQ] | [draft-ietf-hpke-pq](https://datatracker.ietf.org/doc/draft-ietf-hpke-pq/) — Post-quantum and hybrid KEMs for HPKE; the X-Wing HPKE suite |
| [XChaCha] | [draft-irtf-cfrg-xchacha](https://datatracker.ietf.org/doc/draft-irtf-cfrg-xchacha/) — XChaCha: eXtended-nonce ChaCha and AEAD_XChaCha20_Poly1305; the symbol and frame AEAD of Part 5 |
| [hybrid-sig] | The **bound-hybrid signature** of the earlier signed object ([CC 8.11.12](part_8_appendices.md#8.11.12)) |
| [composite-sig] | [draft-ietf-jose-pq-composite-sigs-06](https://datatracker.ietf.org/doc/draft-ietf-jose-pq-composite-sigs/06/) — composite ML-DSA for JOSE and COSE, over [draft-ietf-lamps-pq-composite-sigs-19](https://datatracker.ietf.org/doc/draft-ietf-lamps-pq-composite-sigs/19/); the ML-DSA-65 with Ed25519 signature of [CC 2.6.1.7](#2.6.1.7), its prefix, label and pre-hash as those revisions state them |
| [RFC-9052] | [RFC 9052](https://www.rfc-editor.org/rfc/rfc9052) — CBOR Object Signing and Encryption (COSE): structures and process; the `COSE_Sign1` statement of [CC 2.6.1.1](#2.6.1.1) |
| [RFC-8610] | [RFC 8610](https://www.rfc-editor.org/rfc/rfc8610) — Concise Data Definition Language (CDDL); the schema of the signed object |
| [CDE] | [draft-ietf-cbor-cde-13](https://datatracker.ietf.org/doc/draft-ietf-cbor-cde/13/) — CBOR Common Deterministic Encoding; the payload and protected-header encoding of [CC 2.6.1.2](#2.6.1.2) |
| [RFC-9943] | [RFC 9943](https://www.rfc-editor.org/rfc/rfc9943) — An Architecture for Trustworthy and Transparent Digital Supply Chains (SCITT) |
| [RFC-9942] | [RFC 9942](https://www.rfc-editor.org/rfc/rfc9942) — COSE Receipts; the receipts of [CC 2.6.1.11](#2.6.1.11) |
| [RFC-9964] | [RFC 9964](https://www.rfc-editor.org/rfc/rfc9964) — ML-DSA for COSE; algorithm -49 and key type AKP |
| [RFC-9679] | [RFC 9679](https://www.rfc-editor.org/rfc/rfc9679) — COSE Key Thumbprint; the `kid` of [CC 2.6.1.7](#2.6.1.7) and the identity reference of [CC 2.6.1.1](#2.6.1.1) |
| [RFC-9596] | [RFC 9596](https://www.rfc-editor.org/rfc/rfc9596) — COSE "typ" (type) Header Parameter |
| [RFC-9597] | [RFC 9597](https://www.rfc-editor.org/rfc/rfc9597) — CBOR Web Token (CWT) Claims in COSE Headers |
| [SD-CWT] | [draft-ietf-spice-sd-cwt-09](https://datatracker.ietf.org/doc/draft-ietf-spice-sd-cwt/09/) — Selective Disclosure CWT; the erasable members of [CC 2.6.1.10](#2.6.1.10) |
| [edition-2-vectors] | The verifier's known-answer vectors of this form ([CC 2.6.1.12](#2.6.1.12)), pinned at the tag v23.1.1: [the composite signature](https://github.com/CIRISAI/CIRISVerify/blob/v23.1.1/src/ciris-crypto/tests/vectors/composite/mldsa65_ed25519_draft_kats.json) and [the substrate objects](https://github.com/CIRISAI/CIRISVerify/blob/v23.1.1/src/ciris-verify-core/tests/vectors/substrate_composite/composite_signatures_v1.json) and [the stream key binding](https://github.com/CIRISAI/CIRISVerify/blob/v23.1.1/src/ciris-crypto/tests/vectors/composite/stream_key_binding_v2_composite_v1.json) and [the link handshake](https://github.com/CIRISAI/CIRISVerify/blob/v23.1.1/src/ciris-crypto/tests/vectors/transit/transit_ctkx_v2_v1.json) and [the link seal frame](https://github.com/CIRISAI/CIRISVerify/blob/v23.1.1/src/ciris-crypto/tests/vectors/transit/transit_seal_frame_v2_v1.json); and, at the same tag, the link handshake's wire and its per-frame seal, [the transit handshake document](https://github.com/CIRISAI/CIRISVerify/blob/v23.1.1/docs/TRANSIT_HANDSHAKE_V2.md); and, at the tag v23.2.0, [the row statements](https://github.com/CIRISAI/CIRISVerify/blob/v23.2.0/src/ciris-verify-core/tests/vectors/edition2/row_statements_v2.json) and [the recovery commitment](https://github.com/CIRISAI/CIRISVerify/blob/v23.2.0/src/ciris-verify-core/tests/vectors/recovery_commitment/recovery_commitment_v1.json) and [the genesis bundles](https://github.com/CIRISAI/CIRISVerify/blob/v23.2.0/src/ciris-verify-core/tests/vectors/edition2/genesis/genesis_bundles_v1.json) and [the second genesis bundles](https://github.com/CIRISAI/CIRISVerify/blob/v23.2.0/src/ciris-verify-core/tests/vectors/edition2/genesis/genesis_bundles_v2.json) and [the accord halt](https://github.com/CIRISAI/CIRISVerify/blob/v23.2.0/src/ciris-verify-core/tests/vectors/accord_halt/accord_halt_v1.json); and, at the tag v23.3.0, [the key of iss](https://github.com/CIRISAI/CIRISVerify/blob/v23.3.0/src/ciris-verify-core/tests/vectors/edition2/key_of_iss_v1.json) and [the third row statements](https://github.com/CIRISAI/CIRISVerify/blob/v23.3.0/src/ciris-verify-core/tests/vectors/edition2/row_statements_v3.json) and [the second accord halt](https://github.com/CIRISAI/CIRISVerify/blob/v23.3.0/src/ciris-verify-core/tests/vectors/accord_halt/accord_halt_v2.json) and [the genesis re-seat](https://github.com/CIRISAI/CIRISVerify/blob/v23.3.0/src/ciris-verify-core/tests/vectors/edition2/genesis/genesis_reseat_v1.json) | <!-- stale-ok -->
| [trust-root-vectors] | The verifier's known-answer vectors for the trust root, the node code, receipts and stream heads, pinned at the tag v23.4.1, commit `732c44847cc8d0e3bd2779fd186b504478584623`. Each file is named with its SHA-256: [the genesis bundle](https://github.com/CIRISAI/CIRISVerify/blob/v23.4.1/src/ciris-verify-core/tests/vectors/edition2/genesis/genesis_bundles_v6.json) `82778bc136e33af7c3c6eaf9fde763b74096868a5186f931f69c3e969bb97be9`; [one device a holder](https://github.com/CIRISAI/CIRISVerify/blob/v23.4.1/src/ciris-verify-core/tests/vectors/edition2/genesis/genesis_holder_device_v2.json) `0c9a4514cdbaf19633116295bfeb1d49689dcee13e8dee0bb85c3dd99da9463d`; [the recovery commitments](https://github.com/CIRISAI/CIRISVerify/blob/v23.4.1/src/ciris-verify-core/tests/vectors/edition2/genesis/genesis_commitments_v2.json) `b4220cc7bd61653f795b819c88d0ebf6499e1ab1df8f136798407c4fecd9ab82`; [a later bundle](https://github.com/CIRISAI/CIRISVerify/blob/v23.4.1/src/ciris-verify-core/tests/vectors/edition2/genesis/genesis_reseat_v4.json) `f95e69d1dc79530266f953344c53d62274b885e3610d22a9033ac98f36e44f90`; [the node code](https://github.com/CIRISAI/CIRISVerify/blob/v23.4.1/src/ciris-verify-core/tests/vectors/fedcode/fedcode_e2_v1.json) `f00bae960c2a498171b7eb3ff461cb09624c72832af001bdfd7590511db3b386`; [receipts](https://github.com/CIRISAI/CIRISVerify/blob/v23.4.1/src/ciris-verify-core/tests/vectors/edition2/receipts/receipts_v1.json) `d7e8cb35191c2094fa1cac744d8b28a0aa650e8d786e78be7689cbd8dbe474e8`; [stream heads](https://github.com/CIRISAI/CIRISVerify/blob/v23.4.1/src/ciris-verify-core/tests/vectors/edition2/receipts/stream_heads_v1.json) `a8e88d02039c3631244ad191b482b59a601d0ac2e8470098d42883c077df3da2`; [withdrawals and recantations](https://github.com/CIRISAI/CIRISVerify/blob/v23.4.1/src/ciris-verify-core/tests/vectors/edition2/composer_v1.json) `a795e8a8cb0200d87d913882ce90dfcf9ce349232602f085036922bc9f0b6d08`; [the stream key binding](https://github.com/CIRISAI/CIRISVerify/blob/v23.4.1/src/ciris-crypto/tests/vectors/composite/stream_key_binding_v2_composite_v3.json) `4f2c4dd780fc19b428a693ed01022893cc721bc1f5f82bc17878ad0c4984740f`. | <!-- stale-ok -->
| [build-manifest-vectors] | The verifier's CDDL and known answers for the build manifest blob and its Merkle tree ([CC 3.1.2.1](part_3_the_namespace.md#3.1.2.1)), vendored at `manifests/binary_manifest_v1.cddl` and `manifests/binary_manifest_v1_vectors.json` from commit `231b9e4` of CIRISAI/CIRISVerify. Their SHA-256 are `07bbe78801ea75a8c245e0e4194bf49ea859f0c711fac59c0af4b7e5b4b09806` and `468cce628e4f35232bd3b367f68f6e92adf30b6937525f2240e5bf7314446f58`. |
| [group-id-vectors] | The verifier's known answers for a group's id ([CC 3.3.4](part_3_the_namespace.md#3.3.4)): `group_id_v1.json` at commit `9518060` of CIRISAI/CIRISVerify, SHA-256 `c796353db656a32110fdb7e9c429c9f3e015f396d992751d13030723e49c1249`. |

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

Used by community admission gates per [CC 4.4.3.9](part_4_composition_governance.md#4.4.3.9) Policy M: a `location_proof` Contribution's `cell_id` MUST be contained within the geographic community's `geographic_constraint.cell_id` for membership admission.

#### 2.6.6.3 `documents` — Scope of the H3 rule

Scope pointer: the H3 canonicalization rules above (lowercase-hex `cell_id`, rough-only `cell_resolution ≤ 7`, containment for community admission).

What the H3 rule does NOT do:
- Mandate H3 over alternative geospatial systems (S2, Geohash) — H3 is chosen for hex-cell uniformity, well-defined parent/child hierarchy, and protocol-agnostic absence of a centralized gazetteer dependency. Operator-internal use of other systems is unconstrained; the wire format uses H3 ([CC 2.6.6](#2.6.6)).
- Provide a place-name registry. Communities self-name; cell IDs are the substrate-level binding. UI may map cell IDs to human-readable names per consumer policy.
- Restrict community-side `geographic_constraint.cell_resolution`. A community CAN scope itself at any resolution (e.g., an "Austin metro" community at resolution 5, ~250 km²; a smaller-scale "Downtown Austin" community at resolution 7, ~5 km²). The rough-only invariant applies to `location_proof`, NOT to community definitions. A community whose `geographic_constraint` is finer than resolution 7 can admit nobody by containment, since no proof is finer than 7; such a community admits by invitation and the constraint describes it rather than gates it.

### 2.6.7 `time` — Time and clocks

This entry says which clock every stated instant refers to, and how far that instant may stand from the instant it is checked against. The window differs by case, and the table gives each one.

**The clock.** Every `asserted_at`, `valid_until`, `delegation_valid_from` and `delegation_valid_until` in this specification refers to **wall-clock UTC** at the asserting peer's clock. Producers SHOULD synchronize via [NTPv4 (RFC 5905)](https://www.rfc-editor.org/rfc/rfc5905) or [Roughtime](https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/) to a known-good time source.

**The skew bound.** The maximum tolerated skew between attester clock and consumer clock for a freshness check is **±5 minutes** by default. Tighter thresholds MAY be applied by per-application consumer policy.

**The window by case.**

| Case | Window | Rule |
|---|---|---|
| An attestation whose `asserted_at` is in the future | 5 minutes in the future | Consumers receiving an attestation whose `asserted_at` is more than 5 minutes in the future MUST reject it with `CLOCK_SKEW_VIOLATION` ([CC 5.3.6.1](part_5_transport_substrate.md#5.3.6.1)). A `constitutional` halt is the one exception: a node acts on it at receipt whatever its `asserted_at`, and counts the fuse from receipt ([CC 4.2.1.1](part_4_composition_governance.md#4.2.1.1)). |
| A long-lived attestation carrying `valid_until` in the future | The freshness check is "the attestation has not yet reached its `valid_until`, AND the consumer's own clock is within ±5 minutes of the known-good time source it synchronises to". | A consumer whose clock drifts past the skew bound MUST fail-secure (reject) rather than accept. |
| A `node` or `agent` key record ([CC 2.4.1.1](#2.4.1.1)) | its own `valid_until`, at most `key_record_max_secs` after its `asserted_at` | Read from the record alone against the reader's clock. Peers MUST NOT apply an arrival-clock check to a replicated record. |
| A row whose admission walks a `delegates_to` chain | **`W` = 72 hours** (259 200 s) before the receiver's clock | The substrate MUST refuse such a row whose `asserted_at` precedes the receiver's clock by more than `W`, with the refusal token **`asserted_at_stale`**. |
| A cosigned roster event | none | A cosigned roster event is counted over the members at the roster head it names, and its signed instant decides no one's standing ([CC 3.3.4](part_3_the_namespace.md#3.3.4)). |
| Rows not judged on a chain (traces, scores on the base) | not bound by `W` | The future bound of the first line is unchanged. |

**The admission freshness window `W` (normative).** `W` is the window of the fourth line of the table. A row whose admission walks a `delegates_to` chain is checked for its age at the node that first receives it ([CC 2.4.1.3](#2.4.1.3)). Such rows are a key wrap (`key_grant:*`), a consent row, a licence (`licensure:*`), a deferral response and the epoch-axis membership check. That instant is signer-chosen, so it is bounded. The window decides no standing. Whether an act under an ended standing counts is read from the heads that rows name ([CC 2.4.1.1](#2.4.1.1)). `W` is the participation-window baseline, one "until everyone has heard" constant ([CC 4.2.6](part_4_composition_governance.md#4.2.6)). A row refused `asserted_at_stale` is well-formed, not malformed, and it is not admitted-as-stale. The remedy is to re-sign. A signer back from a week offline is present and can.

**Why the window exists.** The window bounds how far back a row may be dated when a node first holds it. It is not what stops a withdrawn delegate. A row that exercises an ended standing is judged by the head it names, and a date changes nothing there ([CC 2.4.1.1](#2.4.1.1)).

### 2.6.8 `key_id` — FedCode — the kind-tagged identity shorthand; NodeCode v1 retained as `kind: node` (normative)

This entry sets the short code that stands for a federation identity, and the format of the `key_id` that the code renders. It gives the code's kinds, how a code resolves to nodes, the wire format, five constraints, the commitment to the PQC half of the key, and how a node given its owner's code comes to be owned.

**The earlier form.** The `key_id` format below and FedCode v1 to v3 are the earlier form: they render and decode the keys of the earlier mesh ([CC 2.6.1.12](#2.6.1.12)). In this mesh a key's displayed identity is the composite key's thumbprint ([CC 2.6.1.7](#2.6.1.7)), and its code is the form `CIRIS-V4-` stated next. No code of the earlier form converts to it.

**The code of this mesh, `CIRIS-V4-` (normative).** A code names one identity by its key's thumbprint. A `user` code MAY also name up to four of its owner's nodes, and a `node` code names one node. For each node it gives the node's transport identity and an ordered list of up to eight hints for reaching it. Two nodes that hold no root and reach no directory find each other by a code handed over ([CC 5.4.6](part_5_transport_substrate.md#5.4.6)).

```
payload (big-endian)
  version(1) = 0x04 | kind(1) | kid(32)
  kind user:    node_count(1) = 0..=4 | node_count × [ node_kid(32) | endpoint ]
  kind node:    endpoint
  kind agent, family, community: nothing more
endpoint = transport_identity(64) | hint_count(1) = 0..=8 | hint_count × hint
hint     = type(1) | len(1) | body(len)
code     = "CIRIS-V4-" ‖ base32( payload ‖ CRC-16-CCITT(payload) )
```

`kid` is the 32-byte thumbprint of the identity's composite key ([CC 2.6.1.7](#2.6.1.7)), and `node_kid` that of the node's. The identity reference is derived from the thumbprint. The thumbprint commits to both halves of the key, so the code carries no separate commitment. `transport_identity` is the node's transport public identity, the X25519 key then the Ed25519 key, in the order of [CC 3.3.6.2](part_3_the_namespace.md#3.3.6.2). The node's destination is derived from it by that section's four steps and from nothing else. The CRC is as for the earlier form, appended as two bytes big-endian. The base32 is RFC 4648 without padding, in its canonical form. A code is displayed in groups of four characters joined by dashes, and its QR form is ungrouped. A decoder drops white space and dashes and folds case. The payload is at most 1024 bytes.

**The hints.** A hint says how to reach a node whose address the transport identity already gives. Hints are a sequence, most preferred first. Each is unsigned and is only a place to dial. A hint is never a transit pair, a route row or a secret, and a network passphrase never stands in one.

| Type | Name | Body |
|---|---|---|
| 1 | `tcp` | port (2 bytes, not zero), then a host of 1 to 253 bytes |
| 2 | `udp` | as `tcp` |
| 3 | `auto` | scope (1 byte: 0 link, 1 admin, 2 site, 3 organisation, 4 global), then a group id of 1 to 64 bytes |
| 4 | `rnode` | frequency (4 bytes, not zero), bandwidth (4 bytes, not zero), spreading factor 7 to 12, coding rate 5 to 8: exactly 10 bytes |
| 5 | `http` | an `https://` URL of at most 255 bytes |
| 6 | `i2p` | exactly 32 bytes: the I2P destination hash, never its text form |
| 7 | `kiss` | frequency (4 bytes, not zero), bit rate (4 bytes, not zero), then an optional AX.25 callsign with its SSID: 0 to 9 bytes of upper-case letters and digits with at most one inner `-` |
| 8 | `ble` | empty |

Text in a hint carries no space and no control character. A host is a DNS name or an IP literal in text form. IPv4 is a dotted quad. IPv6 is written without brackets and without a zone id, since the port is its own field. A `ble` hint names no device. A fixed radio address in a code would let whoever holds the code follow the device, so the hint says only that the node is reachable over BLE, and the dialler finds it by the service it advertises. A `kiss` hint carries the channel and rate two radios share, and never a local port. A decoder carries a hint of any other type as unknown and a dialler skips it, so a later type breaks no earlier reader. A dialler also skips a type it knows and cannot bring up, as a failed dial. A hint of a known type whose body is malformed is refused.

**What a minter writes.** A minter writes hints from the node's configured, stable reachability, in this order: an endpoint the operator set, then each relay the node holds a client interface to, then its local group, then its radio. It MUST NOT write an address it bound without choosing, an address inside a container, an observed address mapping or a punched path. A relay the node is attached to is a permitted hint, and it is how a node behind address translation is reached. A minter emits only the eight assigned types. Where the nodes and hints exceed the payload bound, the minter drops the least preferred hint of the last node first, then trailing nodes, until the code fits. A decoder never truncates. A node left out crosses as an ordinary row after the link is sealed. Empty is valid: a `user` code with no node, and a node with no hint.

**What a dialler does.** A dialler records the node's thumbprint, its transport identity and its hints, locally and unsigned. It dials the derived destination over each hint in order, and over any path it already has. With no path it asks the network for one, which needs no directory and no root. A hint that fails is a failed dial and never a refusal of the code. The dialler then makes the pre-seal route request of [CC 5.3.3.10](part_5_transport_substrate.md#5.3.3.10). It keeps the key record it receives only where that record's thumbprint equals the code's `node_kid`, and the route row only where that key signed it. The code's `node_kid` is the anchor that section requires. Nothing but the node's own key record and route row crosses before the seal. The owner's rows cross sealed, inside the contact request and the acceptance ([CC 5.4.6](part_5_transport_substrate.md#5.4.6)), and the dialler then checks that the owner they name has the code's `kid`. Each check that fails is refused by name, and nothing is stored. Before the seal: `code_node_key_mismatch`, where the key record is not the dialled node's own; `code_route_signer_mismatch`, where the route row is not that node's own binding; and `code_route_carries_no_transit_key`. After the seal: `code_owner_mismatch`, where the owner's key record is not the code's identity's own; and `code_owner_binding_not_for_node`, where no owner-binding of that identity binds the code's node. A host never registers a peer's key from a code alone: the peer's own signed key record has to arrive.

**The rules of the code (each MUST be enforced at the encoder and at the decoder).**

1. A transport identity is never a federation key. Once the reader holds the composite keys, the Ed25519 half of the transport identity MUST differ from the Ed25519 half of the owner's key and of that node's key (`fedcode_transport_is_federation_key`).
2. Only a `user` code names nodes. A `node` code carries its own one endpoint, and any other kind carries nothing after the thumbprint (`fedcode_nodes_not_user`).
3. No node equals the identity, no node is named twice, and no two nodes share one transport identity (`fedcode_duplicate_node`).
4. The counts and the size are bounded as stated (`fedcode_node_count`, `fedcode_hint_count`, `fedcode_payload_too_large`).
5. A decoder of this form reads only `CIRIS-V4-`. It refuses `CIRIS-V1-`, `CIRIS-V2-` and `CIRIS-V3-` by their prefix, before any payload byte (`fedcode_earlier_form`).

The other refusals are `fedcode_prefix`, `fedcode_base32` (a non-canonical encoding included), `fedcode_crc`, `fedcode_version`, `fedcode_kind`, `fedcode_truncated`, `fedcode_trailing_bytes` and `fedcode_hint_malformed`. A code is unsigned and confers no authority: what it names is believed only as the rows fetched under it verify.

Federation `key_id`s are long opaque identifiers, unfit for a human to type or read aloud. **FedCode** is the **one** human-shareable shorthand: a compact, QR-able, checksummed render of a federation entity's identity for **bootstrap UX**. It is pinned here so **every implementation renders and parses the same code for the same key**. That is a cross-impl determinism requirement of the same class as [CC 2.6.3](#2.6.3) hex / [CC 2.6.1.2](#2.6.1.2) deterministic encoding. FedCode is a deterministic render of an existing `key_id`, **not** a new envelope field. It is additive on the frozen 1+4 surface. The `kind` byte is a payload discriminator of the same discipline as `subject_kind` riding the single `scores` shape ([CC 3.3.2](part_3_the_namespace.md#3.3.2)). Resolution is **DNS-free**. The reference implementation is the verifier; every other component decodes through it.

**Tied to the user, not the node (the model).** In the earlier form the v1 **NodeCode** (`CIRIS-V1-`) renders a *node's* key and is retained as `kind: node`. The code is tied to the **entity** — five kinds, of which three are [CC 3.4.7.1](part_3_the_namespace.md#3.4.7.1) `identity_type` roles and two are rostered `subject_kind`s:

```
kind(1): 1=user  2=agent  3=node  4=family  5=community
```

A `user` code is the owner's identity; the owner's **nodes and transport are optional**. A code that carries them resolves with no directory — pairing, a QR across a table, an air-gapped hand-off. A code that carries none resolves through the **federation directory**. The consumer walks `nodes_owned_by(U)` — the exact inverse of `owner_of` ([CC 3.2](part_3_the_namespace.md#3.2); `n ∈ nodes_owned_by(U)` iff `owner_of(n) == U`, held by construction) — to find the nodes to transport to, **as visible to the walker**. A peer outside `U`'s `self` cohort holds only the owner-bindings of `U` whose audience names it ([CC 5.2](part_5_transport_substrate.md#5.2) audience rule). Those are the federation-scoped ones, those re-signed at a group it shares with `U`, and one addressed to it as a contact ([CC 3.2](part_3_the_namespace.md#3.2)). So a stranger's directory walk yields exactly the announced roster of [CC 5.4.6](part_5_transport_substrate.md#5.4.6), while `U`'s own nodes see every binding. A node whose owner resolves ambiguous is **skipped, not fatal**: one poisoned node does not make its owner unroutable, while a direct query about that node still fails closed.

**Wire format of the earlier form, v1 to v3 (normative for a reader of the earlier mesh).** A decoder of this form refuses these codes under rule 5 above. Binary payload, then **CRC-16-CCITT** (polynomial `0x1021`, init `0xFFFF`, no final xor) appended as 2 bytes big-endian, then **RFC 4648 base32** (alphabet `A–Z2–7`, padding stripped on encode, re-padded on decode). The result is prefixed by the version token and grouped into 4-character dash-separated chunks for display; the QR form is ungrouped. Decoders normalize (drop whitespace, upper-case, strip dashes) and accept the undashed prefix. All length-prefixed fields are 1-byte length, ≤ 255 UTF-8 bytes; an overflow is malformed.

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

**Constraints of the earlier form (each MUST be enforced at encoder AND decoder — a code minted by another implementation is exactly the case an encoder cannot police).**

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

**The PQC commitment of the earlier form (normative).** A code of the earlier form names an Ed25519 key and nothing else, but the substrate takes `federation_keys` writes only at `algorithm: hybrid` (Ed25519 + ML-DSA-65; [CC 5.3.2.8](part_5_transport_substrate.md#5.3.2.8)). So without more, a code-admitted key has no PQC half to register and pairing has no conformant path. The ML-DSA-65 public key is 1952 bytes, which would end the code's life as something a person can read aloud. The code therefore carries the **32-byte commitment** `sha256(raw ML-DSA-65 public key)`. Rules:

- **(a)** The host admits the classical half plus the commitment, fetches the ML-DSA body through the existing Key Pull, and verifies it against the commitment **before** writing a hybrid record. Nothing is registered until both halves are present and bound, so the hybrid-only rule is preserved, not weakened.
- **(b)** The commitment applies to **any** kind of code — a plain `user` code with no nodes emits v3 with `node_count = 0`.
- **(c)** The commitment is presence-tagged and **last**, so a v3 code minted before it still decodes with the commitment absent.
- **(d)** The API form is exactly 64 **lowercase** hex characters, **rejected, never repaired** — normalizing case would let two spellings of one identity mint two codes.
- **(e)** A FedCode is **unsigned**: the commitment inherits exactly the trust of the code carrying it and adds no authority. A conforming implementation MUST NOT treat a commitment match as authentication of the identity; what it buys is that a Key Pull cannot be substituted after the fact.

A code with **no** commitment fails closed at the pull check: there is nothing to bind the pulled key to.

**`key_id` format of the earlier form (normative).** `key_id = "<label>-<fingerprint>"`, `fingerprint` = the first **10 base32 characters** (50 bits) of `sha256(ed25519_pubkey)`, lowercased; `label` is lowercased and reduced to `[a-z0-9-]`, cosmetic. **Collision-resistant by construction, not collision-free** — the suffix is bound to the key, so two entities choosing one label collide only if their keys' hashes share 50 bits. Under one label that becomes likely near **2²⁵ keys** (the birthday bound), not 2⁵⁰. **Verifiable** — anyone recomputes the suffix from the pubkey (a random UUID cannot do this: one could claim another's). Friendly — `alice-k7f3qd2pza` reads as a name. **Registry global-uniqueness is therefore load-bearing, not a backstop**: a registrar MUST refuse a second key under an already-registered `key_id`, and a consumer resolving a `key_id` MUST verify the fingerprint against the pubkey it obtains ([CC 2.6.8](#2.6.8) constraint above). So an aliasing collision is detected at registration and never at resolution. The fingerprint is ten characters at every deployment size, because a consumer recomputes that length and a longer suffix fails the check. A deployment expecting more than **2¹⁶ identities under one label** relies on the registrar's refusal above, which detects a collision at registration.

**Onboarding — usercode → owner (the chosen model).** Put the owner's usercode (`kind: user`) in a node's configuration and the node becomes one of the owner's devices with **one approval tap and no PIN or QR handshake**. It does so under the honest constraint of [CC 1.13.2](part_1_foundation.md#1.13.2): owner-binding MUST be a **user-signed** `delegates_to`, so a node cannot make itself owned by reading a pubkey. On boot the node decodes the usercode, learns its intended owner `U`, and sends `U`'s node a **device-join request** signed by its own node key ([CC 3.2](part_3_the_namespace.md#3.2), Adding a device) — trust-and-serve only until owned. `U`'s client lists the pending requests. `U` compares the matching code their own node derives and approves; their hardware-rooted key then signs the two rows of [CC 3.2](part_3_the_namespace.md#3.2) (b), `delegates_to(U → node)` and the node's device occurrence. The pending-until-approved window **is** the safety property: a usercode is public (a pubkey), so a stolen one lets a node *request* ownership, never *obtain* it. A usercode embedding a pre-authorized signed delegation, so the node binds with no tap, would be a **bearer credential** (theft = silent ownership) and is NOT the default. If ever added it MUST be expiring, scope-limited, and revocable, by amendment.

### 2.6.9 `conformance-language` — Conformance language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [BCP 14](https://www.rfc-editor.org/info/bcp14) ([RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) + [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)) when, and only when, they appear in all capitals, as shown here.

#### 2.6.9.1 `informative` — Normative vs informative content (what interop requires)

A reader may **agree with the protocol and disagree with its philosophy** and still build a fully conforming implementation. The two are deliberately separable:

- **Normative (binding for interoperability):** the wire format and its conformance surface. That surface is the [CC 2.4](#2.4) structural primitives; the [CC 2.1](#2.1) envelope fields; the [CC 3.1](part_3_the_namespace.md#3.1) namespace + `subject_kind`s; and the [CC 2.6.1–2.6.3](#2.6.3) canonicalization rules; the earlier form's rules ([CC 8.11](part_8_appendices.md#8.11)) bind only an object of that form. It is also the [CC 3.5](part_3_the_namespace.md#3.5) relation precedence; the [CC 3.4](part_3_the_namespace.md#3.4) reserved-prefix rules; the [CC 4.4](part_4_composition_governance.md#4.4) composition policies; the [CC 5.3](part_5_transport_substrate.md#5.3) endpoint shapes; and every RFC-2119-keyworded statement. This is exactly the surface enumerated in [CC 1.7](part_1_foundation.md#1.7) ("report the surface beside the invariant"). **Conformance is judged against this and nothing else.**
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

The instant a node first held a row is its own receipt, outside the signed row and never replicated ([CC 4.5.13](part_4_composition_governance.md#4.5.13), the processor's state). There is no trust set among the inputs: who a node trusts is a fold over the rows its own key signed ([CC 4.4.3.34](part_4_composition_governance.md#4.4.3.34)). Configuration is not an input. A value that binds others is a row signed by whoever decided it, and a value that binds only the node is a row under the node's own key.

### 2.7.2 `kernel-order` — The only order is what rows name

A row names other rows by digest: the row it answers, the head it extends, the proposal it votes on. That relation is well founded, since a digest cannot name a row that names it back. There is no sequencer. Nothing ranks the rows of different signers by a signed instant, by arrival or by digest ([CC 3.3.4](part_3_the_namespace.md#3.3.4), [CC 4.5.1.3](part_4_composition_governance.md#4.5.1.3)). Two rows where neither names the other, directly or through other rows, are **concurrent**.

Judging each row as it arrives, against what was admitted so far, is not a function of the rows: one set can give two answers in two arrival orders. So the kernel reads what a row names, never what a node happened to admit before it.

One voice may order its own rows. Between two acts of one kind by one signer on one named row, the later signed instant wins and the lower row id breaks a tie ([CC 3.5.1](part_3_the_namespace.md#3.5.1)). A signer who back-dates changes only what that signer says. A session goes to the earliest claimed instant among one person's own devices, which is one voice ordering its own rows ([CC 3.1.3.1](part_3_the_namespace.md#3.1.3.1)). Rows of different signers are decided by a party's own rows, by a count, or by a fixed order on kinds ([CC 2.7.7](#2.7.7)). A listing is not a ranking: the order in which a ballot shows the roster is read by no rule ([CC 4.5.4](part_4_composition_governance.md#4.5.4)).

### 2.7.3 `kernel-layers` — Three layers

| Layer | Reads | Property |
|---|---|---|
| **kept** | the row alone, its signer's key plane, and whether the rows it names are kept | the least set closed under the door; the same in every arrival order |
| **concluded** | the row against its ancestors | one solution, with negation and counts allowed; final once the row is kept, for a rule that reads no row concurrent with it |
| **derived** | conclusions over a set of rows | a function of the kept set, the node's key and, in one place, `now` |

Admission stops, and ends at one kept set, in every arrival order. A row waits for what it names. One naming makes no row wait: `refs.prev` and `refs.further_prev` on a content row, and `refs.trusted_through` on a row that ends a seat or a `keeps` row, are named for the fold ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). A row is never refused for what another row says: a check that reads another row concludes nothing, is not counted, is contested, or is kept and not served ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2), the refusals; [CC 4.5.13](part_4_composition_governance.md#4.5.13), the state processor). A node may decline to keep or serve a row by its own configuration or duty. That is its own act, never a verdict on the row, and the row is not Invalid. A signer that declines to sign makes no row, and nothing is refused.

Every answer about a row is of one of three kinds. **Final by form**: whether the row is kept, its conclusion for a rule that reads no concurrent row, and a row that names a blocking set of receipts. **Final by acknowledgement**: whether an act counts at the head it names, once n − t + 1 of the n members there have given receipts, where t can cut it ([CC 2.7.5](#2.7.5)). **Provisional**: the rest, including whether an act is still in force at a later head ([CC 2.7.7](#2.7.7)). This is finality of authorisation against cuts: a key revoked back to a bound, a row's own end and a reader's own trust are outside it, and it promises nothing about execution.

After a counting cut on a slot, only a key that may cut that slot changes it. A key whose standing has ended can still change what a reader with no acknowledgement of its own concludes ([CC 2.7.9](#2.7.9)).

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

Nine answers, each a composition of the operators. Each role, window, policy and constant they read is data.

| Answer | Question | Layer |
|---|---|---|
| **state** | is this row live: admitted, withdrawn, recanted, superseded | derived, since a later concurrent row on its target can change it |
| **stands** | does this key hold this relation over this object | derived: a bounded walk of live edges |
| **tally** | is this count met, over the head it names | derived |
| **may** | may this key do this act on this target, and if not, which row is missing and who could sign it | derived |
| **audience** | who is this row for | derived, since a row naming it may come later |
| **missing** | which rows that this conclusion depends on are not held, and which receipts an act lacks to be settled | kept |
| **owed** | what this node must emit or do | derived |
| **window** | has this window closed, and with what outcome | derived; the one answer that reads `now` |
| **settled** | does this act count at its head in every later set | concluded for a row that names its receipts; final by acknowledgement once they are held; derived until then |

**stands.** One act underlies it: a voice consents to what binds it. A relation stands when every voice it binds has a concluded consent, one consent names the other, none is withdrawn by its own signer, and no cut removes it. A permission gives something of the signer's own and binds nobody else, so one row carries it. A duty binds the one who places it and the one who carries it, so it takes two consents ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2), [CC 4.5.4](part_4_composition_governance.md#4.5.4)).

That pair is the **seat**. It is two consents and no other object, and it stands the same whichever was signed first. Nobody is bound by the rows of others. Any bound voice ends the relation alone, and no third key ends it without a cut ([CC 4.5.4](part_4_composition_governance.md#4.5.4)).

Where a body places a duty, the body is one party, and its consent is a count of its members' signatures on the row. One voice is not a count. A count once met is final: no member's later row lowers it, and only the holder's own withdrawal or a cut ends the duty. The members are those at the head the row names, and no key admits itself ([CC 3.3.4](part_3_the_namespace.md#3.3.4)). A member the row removes is a voice of its own removal, except where the group's policy states otherwise ([CC 3.3.4](part_3_the_namespace.md#3.3.4), [CC 4.5.13](part_4_composition_governance.md#4.5.13)).

Who may place a duty is one of three: the object's own key, a key holding a seat that may confer, or a group whose count is met. A key stands when a bounded walk of live seats leads to it from a root. For what a row means to a node, the root is that node's own key ([CC 4.4.3.34](part_4_composition_governance.md#4.4.3.34)). An onward hop counts only from the authority's own acceptance edges. At each hop the remaining depth is the lesser of what is left and the edge's own, the classes intersect, and a cycle is visited once. A scope stands at the end of a walk only if every seat on it carries the scope, so nothing amplifies.

A duty seat over a community is one seat with four scopes: `moderate`, `review`, `slash` and `takedown`. The founding record seats the duty holders who sign it, and they are equals. A duty seat is conferred by a strict majority of the duty holders, or by a lone holder with the new holder's acceptance. It is withdrawn by a strict majority of the others, never on fewer than two voices where there are two holders ([CC 4.5.4](part_4_composition_governance.md#4.5.4)). A delegation that carries a scope seats its delegate only with the delegate's own signature ([CC 4.4.3.19](part_4_composition_governance.md#4.4.3.19)). A deputy holds no seat of its own: it acts under its delegator's seat, and what it may do ends when that seat ends. A duty seat validly conferred then stands as an equal. A claim seats no one ([CC 3.4.5.1](part_3_the_namespace.md#3.4.5.1)).

**may.** The door, the control a person is offered and the gate on serving a row are one answer ([CC 4.5.13](part_4_composition_governance.md#4.5.13), one function run three ways). Where it is no, the control is not offered, the row concludes nothing, and the answer names the missing row. A screen is a function of the rows a node holds, the viewer's key and `now`. It offers exactly what the door admits, and never draws as sent a fact the node did not send.

**missing, and what is copied.** A row moves to a peer because that peer must conclude something and lacks it. What is sent is what lies among the ancestors of that conclusion, within the row's audience. A row whose audience is everyone may be served to anyone, and a stranger is routed nothing outside that. A node keeps a row only when it is in the row's audience as it reads it. A row it declines is not Invalid, and it may take the row once it is. Being in an audience permits serving a row and does not cause a send; a peer's own request for it is a cause. A row carries its audience to the rows it names when it is concluded, sits in the same room, and its signer is already in the named row's audience. A row leaves its room only by its own signer's act ([CC 5.2](part_5_transport_substrate.md#5.2)).

**settled, and receipts.** A **receipt** names each act it acknowledges and names no head. It has those acts in its past, and no cut of them by its own key. Its family is `act:ack` ([CC 3.1.3](part_3_the_namespace.md#3.1.3)). An act is **settled** once receipts are held from n − t + 1 of the n members at its head, where t can cut it ([CC 2.7.7](#2.7.7) rule 6). **missing** names the voices whose receipts it lacks; a node MAY ask them under the copy rule above, and nobody owes one. An effect that cannot be undone, such as a key wrap or release, a disclosure, an external actuation or a deletion, names a blocking set of receipts of the act it rests on and waits for them. A section that requires such an effect without them says so ([CC 4.5.3](part_4_composition_governance.md#4.5.3)).

**window.** A row opens a clock. An answering row closes it, or time does, and the table states the outcome at the close. Where the outcome binds others, the concluder signs it as a landing row naming the acknowledgement by which it first held the opener, and its own head. Where it binds only the reader, each node reads the close on its own clock and signs nothing ([CC 4.5.13](part_4_composition_governance.md#4.5.13), the clock of a window).

A landing that states an outcome its own past does not give concludes nothing. An answer concurrent with a landing is **recounted**: it is counted with the landing's past, and the landing stands only if the table still gives the outcome it stated. A landing that does not stand says nothing against one that does. A landing with a strict majority behind it is final where no key of that majority answers both ways, in two rows neither of which names the other; such a key has no say there ([CC 2.7.7](#2.7.7) rule 6).

One door runs every policy row and every clock that takes answers, and the policy table states its count, floor and length ([CC 4.5.13](part_4_composition_governance.md#4.5.13)). The door reads five more things, each stated in the text. They are who concludes and with which row, and whether a late answer counts. They are also whether the opening act is in force while its window is open, whether the joiner's own yes is a voice of the floor, and the threshold the room's founding row declares.

**Two notions of time.** There are two: a row's own stated end, read from the row against `now`, and a window with a landing. An invitation's expiry is a window that shuts out a late acceptance ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). A key is live while one of its own records covers `now` and it has not revoked itself, and no row of another key enters that reading. A row of an ended key that no live row has in its past lapses and counts in no answer. Its own verdict is unchanged, and a revocation never lapses.

### 2.7.6 `kernel-shapes` — Two mechanisms, four shapes

Every row family is one of four shapes: a **consent**, a **door**, a **claim** or **content**. A roster is a consent given by a count, and an acknowledgement is a claim. A family that takes no shape states why.

The four are labels over two mechanisms, consent and the door. Content is carried by consent: its audience is read off roster heads and the rows that name it, and its life is the **state** answer. A claim is carried by consent: what it means to a reader is the reader's own one-voice consents, walked from the reader's key. Nothing else reads `now`, so the door stays. Nothing else makes an offer stand, so consent stays.

### 2.7.7 `kernel-conflict` — Conflict between concurrent rows

Concurrent rows on one target are settled by six rules, and by no ranking of their signers.

1. **Different kinds on one target** are decided by a fixed order on kinds ([CC 3.5.1](part_3_the_namespace.md#3.5.1)).
2. **The same kind on one slot**: both count or neither does. No rule that cannot tell two rows apart can pick one.
3. **A row that names both** may decide between them.
4. **The cut.** A cut is a row on a slot by whoever may conclude it. Once it counts, rows on that slot concurrent with it do not count from the head the cut names, rows in its past stand, and rows that name it are judged at the head they name ([CC 2.4.1.1](#2.4.1.1)).
5. **Equal standing.** Two cuts by keys of equal standing that undo each other stay contested. A voice that the other cannot remove settles them.
6. **One say.** On one slot at one head, a voice that has acknowledged an act and voted to cut it, in two rows neither of which names the other, has no say there. It stays among the members the count is over.

**Answers by head.** Whether an act counts is read at the head it names, and whether it is still in force at a later head. A cut by a voice seated at a later head acts forward from the head it names and never changes what counted earlier; takedown, moderation and the halt act forward too.

A row of a removed key counts when the removal has it among its ancestors: something the removal can see had already named it ([CC 3.3.4](part_3_the_namespace.md#3.3.4)). A row of that key concurrent with the removal counts at its own head and is not in force from the removal's head on ([CC 2.4.1.1](#2.4.1.1)). Among several duty holders, one holder's own conferral concludes only while it is the one duty holder ([CC 4.5.4](part_4_composition_governance.md#4.5.4)).

Three further rules hold. A cosignature is a voice only for a row counted over a head that the cosignature itself names. An offer conferred by a count is ended by its holder or by a count, never by its proposer alone. A counted row counts only if every counted row it is built on counts.

### 2.7.8 `kernel-roster` — The roster is the one ledger

A group's roster is a lineage. Each version names the heads it extends and is counted over their members. Every other row takes its place from the roster head it names, and nothing else is ordered ([CC 3.2](part_3_the_namespace.md#3.2) T6).

Two versions of one head wait as tips. The roster is then the members common to all tips, until a version naming the tips makes one head again. The members at a head are a function of the head, its signatures and its past. A removal is a later counted version and changes the members there, not at the old head. A member's own leaving binds the same way, by causal past ([CC 3.3.4](part_3_the_namespace.md#3.3.4)).

Where the count asks two or more, one key's rows remove nobody, and a removed key counts again only after a version lists it again ([CC 4.5.13](part_4_composition_governance.md#4.5.13), the floor of two voices). A reader that has acknowledged a head holds void every counted act that names an older head and is not in that head's past, however many rows it has. Its signer acts again, forward, at the newer head ([CC 3.3.4](part_3_the_namespace.md#3.3.4)). This line is for counted rows and every end of a standing: a version, a vote, a cut and an end, counted or one's own. It does not reach a receipt. It does not reach an authored act that names its head, which counts at that head whatever head a reader has acknowledged. That voiding is the reader's own and binds nobody else. Anything that binds others rests on receipts, a row that names a blocking set ([CC 2.7.5](#2.7.5)), never on one reader's own closure. Keys that met the count of an old head can sign a valid version alone; a receipted lineage answers that ([CC 3.2](part_3_the_namespace.md#3.2) T6).

A person's keys, a voice's room keys, a room, the accord and an infrastructure community are this one roster, with parameters read from the policy table and the text. A public room's roster is public, so an audience is the members of a roster, everyone, or one named key ([CC 3.2](part_3_the_namespace.md#3.2)). It is read by asking a member's node, and every other roster is never enumerable outside its cohort.

**A writer's keys are a fold.** Who is entitled to a wrap of which key is a matter of seats and cuts. A rotation is due when a holder of the current key has lost its entitlement ([CC 4.4.3.16](part_4_composition_governance.md#4.4.3.16)). Each write and each mint names the head of the membership rows the writer held. The epoch is the count of the writer's mint rows, and the writer's state is a fold over its own rows.

**A private room seats voices.** In a private room the roster seats a **voice**, never an identity. A voice is a small counted roster of **room keys**, one for each device, made for that room only. That a voice is a given person's is the **binding**, which is never a row and is made for one addressee who cannot prove it to anyone else. No named answer reads a binding, and every named answer is the same over voices as over identity keys. A count of persons waits at a node for the bindings it lacks; a withheld binding is a stall, never a fork ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)).

### 2.7.9 `kernel-limits` — What the kernel does not give

- **No finality without the rows that show it.** Two nodes with the same rows conclude the same, and what is final by form or by receipts is final for every reader that holds them. A reader's own acknowledged head closes older heads for that reader only. Any other slot can be reopened by a key with standing on it.
- **No conclusion from silence without a clock.** A window closing unopposed, and the lapse of an unconfirmed halt, are read on the node's own count of elapsed time. Nodes may differ while a window is open.
- **No decision that is not a function of rows.** Link and load decisions, retries, rendering and the prose rules given to a model stay outside the kernel.
- **No invariant of the form "at least one".** Two honest keys acting concurrently can leave none. For a community the way back is the lock and the members' count ([CC 4.5.4](part_4_composition_governance.md#4.5.4)).
- **No guard against a slot held on one signature.** A key of equal standing can undo such a slot, and the kernel does not check the tables for one.

An attacker keeps these, each bounded as stated:

- Keys that met a past count can fork on a past head. That unlists members and never lists one, and it moves only a reader with no acknowledgement of its own.
- A relay can choose the order of delivery and withhold a row until it is delivered. An emission made meanwhile cannot be unsent.
- A relay can withhold the row that would answer a window until one node's clock has closed it. That node's answer then differs for good from that of a node that held the row in time, even once both hold the same rows. Each first-held instant is an input ([CC 2.7.1](#2.7.1)). The halt's fuse is one such window: a confirmation after it lapses confirms nothing, and a fresh halt is fired instead ([CC 4.2.1.3](part_4_composition_governance.md#4.2.1.3)).
- A lone landing is never final against a key that can still sign, and the window's length is the concluder's own word.
- Whoever controls a new reader's first view can make a wrong head stick, until the reader withdraws its own rows.
- Whoever holds an ended key's private half can revive it, and only the key's own revocation makes its end final.
- A relay that withholds an eviction leaves a reader accepting the evicted device until the eviction arrives, as any withheld row does. The eviction carries its signer's proof, so a reader that holds it can resolve it.
- A lone duty holder can confer any number of seats, each with its holder's acceptance. Each such seat stands on its own after the conferrer leaves ([CC 4.5.5](part_4_composition_governance.md#4.5.5)).

A private room does not give deniability against a member who cooperates live with an outsider. A member's word is always possible; what is removed is the proof ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)).

The kernel does not settle these:

- a roster version that names several heads on the wire;
- how a second consent travels, and from when a delegation without one stops seating;
- the reach of a cosignature attached against a node's clock, unless it states its own end;
- a meaning for a clock that times a window from a signed instant and judges it at receipt. The freshness window `W` and `CLOCK_SKEW_VIOLATION` ([CC 2.6.7](#2.6.7)), the bound on a key that has lost standing ([CC 3.3.6.4](part_3_the_namespace.md#3.3.6.4)) and the attach window ([CC 3.2](part_3_the_namespace.md#3.2) T4a) read one. So do a response bounded by `W` ([CC 4.3](part_4_composition_governance.md#4.3)), an objection counted within `W` ([CC 4.5.13](part_4_composition_governance.md#4.5.13)) and the instant of a reserved family's row ([CC 3.4.7](part_3_the_namespace.md#3.4.7)). The kernel gives each no meaning beyond one node's own reading;
- `revoked_after`, which reads a revoked key's rows by their signed instants ([CC 2.4.1.1](#2.4.1.1), [CC 2.6.1.7](#2.6.1.7), [CC 3.2](part_3_the_namespace.md#3.2) T6 to T8, [CC 5.3.2.3](part_5_transport_substrate.md#5.3.2.3)). The kernel gives that reading no meaning beyond one node's own;
- a seat, a licence or an owner read at a row's signed `asserted_at` where the row names no head ([CC 3.1.5](part_3_the_namespace.md#3.1.5), [CC 3.3.1](part_3_the_namespace.md#3.3.1), [CC 3.4.7](part_3_the_namespace.md#3.4.7), [CC 4.3](part_4_composition_governance.md#4.3)). The kernel gives that reading no meaning beyond one node's own;
- the standing verdict of a trust root, which [CC 3.2](part_3_the_namespace.md#3.2) T6 to T8 index by a signed `effective_at`. The kernel gives it no meaning beyond one node's own reading;
- a meaning for a rule cell that keeps a word the operators do not carry, or calls a fold no cell defines;
- what a family confers where no sentence states it;
- the smallest set of rows a node must keep ([CC 2.7.10](#2.7.10));
- whether a withdrawn receipt still blocks a cut. It is treated as blocking, and that is not established.

### 2.7.10 `kernel-checkpoint` — Checkpoint and purge

A node MAY keep its folded state and fold only the rows it has not yet folded. It MAY sign a **checkpoint**: a row under its own key that names the held rows no held row names, and carries the digest of its folded state. It MAY then drop the bytes of rows beneath a checkpoint, as this section allows. None of this is a duty: a node that keeps every row conforms.

A checkpoint binds nobody and is served to nobody unless its signer chooses. It is not an acknowledgement of the heads beneath it, and signing one changes no answer.

**What a checkpoint keeps.** For every row whose bytes it drops, a node keeps the row's digest, the digests it names, the fields a rule reads, and its conclusion. Where an act's count at its own head is final, the node keeps that answer. That is so for a settled act, kept with its receipts' digests, and, for this node only, for an act at a head older than one it has acknowledged ([CC 2.7.8](#2.7.8)). Any other act is kept whole, with its receipts and every cut of it. Whether an act is still in force at a later head is read again. A row that arrives naming a dropped row waits or concludes as it would if the bytes were held.

Nothing that reads `now` is frozen. A node keeps the instant it first held each row that opened a window ([CC 2.7.1](#2.7.1)), and reads again at each `now` every window, row's own end, key's end and `revoked_after` ([CC 2.4.1.1](#2.4.1.1)).

**What a purge never drops.** A purge never drops bytes another section keeps:

- the accountability record ([CC 2.4.1.1](#2.4.1.1));
- identity, consent and config records ([CC 6.1.5.2](part_6_the_coherence_mathematics.md#6.1.5.2) B1);
- records under a `legal_hold` or a class's retention floor ([CC 4.4.3.12](part_4_composition_governance.md#4.4.3.12));
- bytes counted toward an item's target or reported `here`, until `none` is acknowledged ([CC 6.1.5.1](part_6_the_coherence_mathematics.md#6.1.5.1), [CC 3.1.3.3](part_3_the_namespace.md#3.1.3.3));
- a retirement record under an accepted preserve request ([CC 7.5.5](part_7_lifecycle_stewardship.md#7.5.5));
- a tombstone ([CC 4.5.3](part_4_composition_governance.md#4.5.3)).

A deletion duty outranks a kept copy ([CC 4.5.3](part_4_composition_governance.md#4.5.3), [CC 3.3.1](part_3_the_namespace.md#3.3.1)). Only a `legal_hold` or an `erasure_exempt` class suspends consent-driven descent ([CC 4.4.3.29](part_4_composition_governance.md#4.4.3.29)). After a purge a node still serves its audience what it owes. A node holding bytes in custody for others drops only those whose custody has ended.

**Scope.** This section concerns a node's own storage and answers. A new reader taking a group's past on a member's vouch performs a different act ([CC 3.3.4](part_3_the_namespace.md#3.3.4)).

### 2.7.11 `kernel-admission` — Admission: what an agent is, what a node runs, what an agent does

Three changes are one admission: a change to what an agent is (its profile), to what a node runs (code), and to what an agent is about to do (an action). In each, authority is a verified row that names the exact digest which takes effect, and it reads forward only. For a profile and for code that row is rooted in a person. No program's key produces it: a key whose `identity_type` contains `node` or `agent` admits nothing ([CC 2.6.1.7](#2.6.1.7)). An action's row is different: it is the agent's own review record, under the agent's key, and it binds only that agent's own dispatch. A person's row is needed where an objection is discharged, or where the act claims an authority no delegation gives it.

| Scope | What changes | The row | Who |
|---|---|---|---|
| profile | the agent's identity | the `identity_amendment` chain from the base template ([CC 3.1.5](part_3_the_namespace.md#3.1.5)) | one approval by a person seated over the agent ([CC 4.3](part_4_composition_governance.md#4.3)) |
| code | a unit a node runs | `admission:unit` ([CC 3.1.3](part_3_the_namespace.md#3.1.3)) | one person for a unit that only computes, or on a host that person owns; otherwise a count of persons |
| action | one call an agent dispatches | the review record over the call's fingerprint | all four faculties of the agent |

**Code.** A **unit** is what a host executes under one digest: SHA-256 over its bytes, or over its manifest where it is several files. A host MUST NOT execute a unit outside its attested build, in any mode, unless it holds a live `admission:unit` row naming that exact digest. Code a program wrote is data. It runs nowhere until a person's row names its digest, and a changed unit is another digest with no admission.

A row names the capabilities it admits from a closed set: `compute`, `read`, `net_send`, `submit`, `sign`, `store_write` and `actuate`. Nothing is ambient. The last five are **effects**. A row that names no effect MAY be one person's. A row that names an effect is a counted row ([CC 2.6.1.9](#2.6.1.9)), counted over the members at the head it names by the group's declared protocol. It is never counted on fewer than two persons. One exception holds: one person's row that names an effect admits on a host that person owns, and on no other host. A host knows its owner by its owner-binding, which the owner signs and the node cosigns ([CC 3.2](part_3_the_namespace.md#3.2)). Such a row MUST be at `self` scope ([CC 2.1](#2.1)); at any other scope it is Invalid (`admission_owner_row_not_self`). A counted row takes any scope its signers choose, and at `federation` it serves every host whose owner accepts its group.

Every voice's `iss` is a person's identity, whose `identity_type` contains `user` or `accord_holder`. It is read after step 8 finds the statement's key to be a key of that `iss` ([CC 2.6.1.8](#2.6.1.8)). A delegation carries no admission, so the family names no role for a delegate.

**The attested build.** A unit inside an attested build runs under the build's own attestation: the build's manifest names it, and the host holds the counted grant of the pipeline that signed it ([CC 3.1.2.1](part_3_the_namespace.md#3.1.2.1)). An `admission:unit` row admits what a host loads beyond that build, such as an imported skill, a discovered adapter or a tool added at run time.

**Standing.** The author, or the group whose head a counted row names, stands at a host when it is the host owner's own key. It also stands when the owner's own acceptance edges reach it ([CC 4.4.3.34](part_4_composition_governance.md#4.4.3.34)), with the class `admission` listed on every edge of that walk. An edge signed by a program's key carries nothing on the walk. No list of issuers ships with anything. A row whose author or group does not stand at a host admits nothing there.

**The lease.** A row admits from its `asserted_at` to its `valid_until`, read on the host's own clock, at most `unit_lease_max_secs` apart. It admits for at most `unit_lease_max_secs` after the host first held it ([CC 2.7.1](#2.7.1)). So a host that hears nothing more stops within one lease. A renewal is a later row for the same digest. A host runs a unit while any admitting row covers `now`, with the capabilities those rows name together.

**The end.** An admission ends at its lease, at its withdrawal and at the halt. An authored row is withdrawn by its author, and a counted row by the same count ([CC 2.4.1.1](#2.4.1.1) rule 0). A withdrawal reaches forward from the host's receipt of it. A host owner MAY always stop running a unit.

**Capabilities only narrow.** A unit started by another unit holds no capability its parent lacks. A unit submitted to another host runs there only by that host's own admission, against its own owner. The sender's standing carries nothing across.

**The halt reaches every unit.** On a node the halt reaches, from the instant it latches, the host permits no effect of any admitted unit ([CC 4.2.1.1](part_4_composition_governance.md#4.2.1.1)). The host reads the latch before every effect. Computing and reading continue, and the lease ends a halted unit.

**A receipt before it runs.** A host MUST NOT run admitted code until it holds a receipt for a statement of the `admission:unit` row from a Transparency Service the host trusts. The receipt is SCITT's own: a COSE receipt ([RFC-9942]) in the unprotected header's `receipts` parameter, label 394, as [RFC-9943] carries it. The service registers the statement's deterministic `COSE_Sign1` encoding with an empty unprotected header, and its leaf hash is SHA-256(0x00 ‖ leaf), as [RFC-9162] hashes a leaf. A missing or unverifiable receipt is not held, so the unit waits, and it never admits. The unprotected header is unsigned, so a malformed receipt is ignored and is never a fault of the statement. A receipt adds no authority. It witnesses that the statement was registered, which closes a release seen only by those it was sent to.

**Who runs a Transparency Service.** Anyone may run one, under their own key. A host trusts a service by its owner's own acceptance edge with the class `transparency` ([CC 4.4.3.34](part_4_composition_governance.md#4.4.3.34)): one hop, read at the host's `self` scope, whatever the edge's tier. The edge carries the service's key as `service_key`: a COSE key with its algorithm, or an identity reference whose key is its `key:record`. A receipt whose protected algorithm is not that key's does not verify. No list of services ships with anything. A receipt from a service the host does not trust counts for nothing there.

**Profile.** An agent loads its profile only when the digest of what it loads equals the digest its rows derive ([CC 3.1.5](part_3_the_namespace.md#3.1.5)). The base link of the `identity_amendment` chain names no predecessor and approves the exact digest of the agent's shipped template, as that template's manifest signature or the attested build checks it. Each later link names the one before. With no base link, the agent runs that template alone, counts no amendment and reports `profile_unanchored`. The expected digest is SHA-256 over the deterministic encoding of `["CEG-profile/2", d0, ..., dn]`, the links' digests in chain order. Two links that name one predecessor both stay uncounted, and the expected digest is that of the chain before them ([CC 2.7.7](#2.7.7) rule 2).

**The base link.** The agent proposes it by a deferral naming the template's name, version and manifest digest. A person seated over the agent approves it by a response whose `amendment_digest` is that manifest digest ([CC 4.3](part_4_composition_governance.md#4.3)). The agent's node then signs the link. The approver is shown the name, the version and the digest, never the bytes. The attested build checks the template's manifest until that manifest carries a composite signature of its own. An agent that adopts this section starts unanchored. No amendment counts until a base link is approved and each amendment is approved again by its exact bytes.

**Action.** Before an agent dispatches a call, it computes the call's **fingerprint**: SHA-256 over the deterministic encoding of `["CEG-call/2", verb, tool, arguments, channel]`, written as a row id is. `tool` is the name after alias resolution. `arguments` are the arguments as reviewed, each secret standing as its reference and never its value. `channel` is the channel's id, or the empty text. A number in the arguments is read by its exact decimal value. An integral value is an integer. Any other is its exact decimal as CBOR tag 4, normalised: a negative exponent and a mantissa not divisible by ten. An integer or a mantissa outside CBOR's integer range is refused (`call_argument_unrepresentable`). No float is written.

The agent's four faculties ([CC 3.1.5.3](part_3_the_namespace.md#3.1.5.3)) are faculties of the agent, not keys. Their passes form a **review record**, a record under the agent's own key that binds only its own dispatch ([CC 2.7.1](#2.7.1)). The trace that anchors the act carries it ([CC 1.13.6](part_1_foundation.md#1.13.6)), and it confers nothing on any other node.

An agent MUST NOT dispatch a call unless a review record of the same thought names the fingerprint it recomputes, before any secret is opened, with the passes of all four faculties. Execution is bound to the exact reviewed fingerprint, so what executes is byte-identical to what was reviewed, and a material change is a new action with no record. An independent dispatch gate also enforces the authorisation facts outside the reviewing stages, so authorisation holds even when review or its context fails.

**An objection binds its fingerprint.** A faculty's objection bans the draft it was raised against, and a different draft is a new fingerprint that all four faculties review afresh. A pass over the same fingerprint dispatches only when it names the objection with the trusted row that discharges it: a row signed by a person seated over the agent ([CC 4.3](part_4_composition_governance.md#4.3)). A pass over a new fingerprint names every earlier objection of its thought as considered, so no retry loses one. The drafter's own argument discharges nothing, and the absence of evidence never licenses. A Wise Authority's approval of a call names the call's fingerprint, and a dispatch resting on it executes only that call.

**Derived trust.** A result is no more trusted than the least trusted row it derives from. A later signature attests who acted, not what the content is. An effect whose arguments derive from untrusted input is licensed by a pass record that declares that derivation. An agent acts under standing delegations, and the person who signed one approves no single act under it. Its owner-binding delegates it the role its template defines ([CC 3.2](part_3_the_namespace.md#3.2)). Under that delegation it does any act that needs no role, speech included. An act that needs a role needs a live delegation whose scope names that role ([CC 4.5.5](part_4_composition_governance.md#4.5.5)): an agent delegated `moderate` moderates. Only an act that no delegation covers needs the approving row that names its fingerprint. An effect that is a row binding others waits for the acknowledgements of those who could stop it ([CC 2.7.5](#2.7.5)).

| Token | Answer | Where |
|---|---|---|
| `admission_unit_malformed` | Invalid | a row with both `author` and a head, or neither |
| `admission_capability_unknown` | Invalid | no capability, or one outside the closed set |
| `admission_owner_row_not_self` | Invalid | one person's row names an effect at a scope other than `self` |
| `admission_lease_out_of_window` | Invalid | `valid_until` not after `asserted_at`, or more than `unit_lease_max_secs` after it |
| `admission_issuer_not_person` | Invalid; a voice of a counted row is refused alone | a signer whose key is not a person's |
| `admission_issuer_not_reached` | admits nothing at this host | the author or group does not stand here, or one person's row names an effect on a host that person does not own |
| `admission_count_unmet` | held | the count is not met at the head the row names |
| `admission_none` | the unit does not run | no live row admits this digest; detail `no_row`, `lease_ended` or `withdrawn` |
| `admission_receipt_missing` | the unit waits, and does not run | no receipt from a Transparency Service the host trusts is held; detail `none`, `unverifiable` or `untrusted_service` |
| `admission_capability_not_admitted` | the effect is refused | no live row names the capability |
| `admission_capability_not_held` | the effect is refused | the unit's parent lacks the capability |
| `admission_halted` | the effect is refused | the halt is latched |
| `profile_digest_mismatch` | the profile does not load | its digest differs from the derived one |
| `profile_contested` | the profile does not load beyond the fork | two links name one predecessor |
| `profile_unanchored` | the shipped template alone runs | no base link is held |
| `call_argument_unrepresentable` | no fingerprint, not dispatched | an argument's integer or mantissa outside CBOR's integer range |
| `action_not_reviewed` | not dispatched | no record names this fingerprint in this thought |
| `action_review_incomplete` | not dispatched | a faculty's pass is missing |
| `action_objection_undischarged` | not dispatched | an objection to this fingerprint is not named with a trusted row |
| `action_objection_not_carried` | not dispatched | an objection to another draft of the thought is not named as considered |
| `action_approval_mismatch` | not dispatched | the approval names another fingerprint |
| `effect_untrusted_unacknowledged` | the effect waits | an undeclared derivation, claimed authority without its row, or a binding row without its acknowledgements |

**What this rests on.** A model of the review contract shows that binding execution to the reviewed fingerprint is necessary. It holds under two stated assumptions: a drafter may err, and a faculty that holds the evidence judges correctly. That is sufficiency of the contract under those assumptions, not proof that an implementation follows it.

**What this does not give.** A stage that must see the action it judges can be shown untrusted text inside that action. That residual is declared and not closed; how often it occurs is measured on one model, not proved. A person with standing who admits harmful code makes it attributable and withdrawable, not impossible. A unit that interprets its input can run what nobody admitted, carried as data. Capabilities and the effect gate bound it and do not forbid it. A host that does not follow this section gains no reach into one that does.
