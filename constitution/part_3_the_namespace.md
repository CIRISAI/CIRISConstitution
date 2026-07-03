# Part 3 — The Namespace

**Decimal range** `3.x` · **62 sections** · **page budget 23pp** · [← master index](README.md)

> The dimension namespace, reserved prefixes, the consent family, and the subject_kind catalogue.

---

## 3.1 `namespace` — The dimension namespace

A federation needs a shared vocabulary before it can have a shared judgment. The dimension namespace is that vocabulary: the disjoint union of what every sibling component's MISSION.md commits to. CEG does not author the namespace top-down. It owns its own slice ([CC 3.1.1](#59-cirisregistry--identity--build--license--partner)) and consumes everyone else's, so that justice — fair access to capability — and integrity — auditable claims — rest on names every participant agrees on. There are **83 prefix families across 8 owning components**.

This section catalogs every prefix family, organized by owning component, each citing the MISSION.md or FSD section that commits to the concept.

### 3.1.1 `registry` — CIRISRegistry — identity / build / license / partner

**Steward**: this Registry. Cited from [`../MISSION.md`](../../MISSION.md) §3 + FSD-001 + protocol/ciris_registry.proto.

| Prefix | Description | Polarity | Reserved? |
|---|---|---|---|
| `licensure:{authority_id}` | License status — issued / revoked / expired — for a key under a named authority. Co-owned with Verify. | signed | Co-owned |
| `partner_role:{role}` | Partner status (COMMUNITY / COMMUNITY_PLUS / PROFESSIONAL_MEDICAL / PROFESSIONAL_LEGAL / PROFESSIONAL_FINANCIAL / PROFESSIONAL_FULL). | enumerated | No |
| `revocation:{entity_type}:{reason}` | Entity revocation (`agent` / `partner` / `license`). Immediate, non-rollbackable. | -1 only | No |
| `bond_posted:{currency}` | Bond posted per $1-Sybil-resistance per PoB; forfeited on revocation. | positive-only | No |
| `build:registered:{target}` | Build manifest registered against the directory (precondition for L4 attestation). | boolean-via-score | No |
| `multilateral_participation:{forum}:{kind}` | Depth of a partner's participation across federated bodies. `{forum}` = named federated body or compact; `{kind}` ∈ `membership` \| `voting` \| `proposal_filing` \| `observer_status`. | signed | No |
| `agent_files:{kind}:{platform_or_target}` | **Joint claim with [CC 3.1.9.1](#567-files-as-contributions-joint-claim) NodeCore.** Canonical-attester rule: registry-steward-triple attestations constitute the CIRIS canonical default-trust state. Anti-tricking guarantee at `registry.ciris-services-1.ai/install` per [CC 4.4.3.7](part_4_composition_governance.md) trust-composition policy. Open Contribution channel; consumer policy composes via [CC 4.4.3.7](part_4_composition_governance.md) trust layers. | signed | No |
| `accord:*` | **Reserved** — only `identity_type=accord_holder` may emit. The one constitutional asymmetry. | see [CC 3.4.1](part_3_the_namespace.md) | **Yes — [CC 3.4.1](part_3_the_namespace.md)** |

### 3.1.2 `attestation` — CIRISVerify — attestation ladder, provenance, transparency

**Steward**: [`CIRISVerify/MISSION.md`](https://github.com/CIRISAI/CIRISVerify/blob/main/MISSION.md). These prefixes serve integrity: each is a checkable claim about how far a build, key, or license has climbed the trust ladder.

| Prefix | Description | Polarity |
|---|---|---|
| `attestation:self_verify` | Running CIRISVerify binary attests itself against its function manifest. (Consumer-side ladder: corresponds to L1; see CC 4.4.3.6 Policy I.) | boolean-via-score |
| `attestation:hardware_rooted` | Hardware-rooted attestation (TPM 2.0 / Android Keystore / iOS Secure Enclave). (Ladder L2.) | boolean-via-score |
| `attestation:registry_consensus` | 2-of-3 multi-source registry consensus on key / build / license validity. (Ladder L3.) | boolean-via-score; `Indeterminate` allowed → RESTRICTED |
| `attestation:license_validity` | License-validity claim (Registry-signed, Verify-verified). (Ladder L4.) | boolean-via-score |
| `attestation:agent_integrity` | Agent source-tree byte-equal against registered manifest. (Ladder L5.) | boolean-via-score |
| `provenance:slsa:{level}` | SLSA build provenance levels 1-3. Registry emits these on build registration; Verify v3.6.0+ `AttestBundle.provenance.slsa_level` consumes. | boolean-via-score |
| `provenance:build_manifest:{target}` | Per-target canonical-staged-runtime manifest hash equality. Each `BuildManifest` is hybrid-signed (Ed25519 + ML-DSA-65) by the per-primitive steward. | boolean-via-score |
| `provenance:build_manifest:{target}:locale:{lang_code}` | Per-locale signed sub-manifest within a target's manifest tree. Parent target manifest is Merkle root over per-locale leaves. RFC 6962 padding for non-power-of-2. Detection surface for locale-targeted attacks. Canonical-bytes spec at [CC 3.1.2.1](#521-canonical-bytes-contracts-for-provenance-primitives). | boolean-via-score |
| `provenance:skill_import:{source}` | Community-skill import provenance. `{source}` ∈ `registry:{registry_id}` \| `direct:{url}` \| `local:{path}`. Envelope: `{skill_manifest_sha256, signer_identity, import_timestamp, capability_declaration}`. Canonical-bytes spec at [CC 3.1.2.1](#521-canonical-bytes-contracts-for-provenance-primitives). | signed |
| `transparency_log:inclusion` | RFC 6962 inclusion proof for an audit leaf. | boolean-via-score |
| `transparency_log:consistency` | RFC 6962 consistency proof between two STHs. | boolean-via-score |
| `transparency_log:cosigned:{tree_size}` | Witness cosignature on an STH (substrate-conformance path; the interim uses a per-region `registry_sth_cosignatures` table; see [CC 5.3.1](part_5_transport_substrate.md) endpoints). | signed |
| `rollback_detected:{revision_field}` | Anti-rollback — decrease in revocation revision. | -1 only |
| `cert_validity:{authority}` | Validity of a certification authority's signature. Each registry steward emits `cert_validity:{steward_id}` self-attestation alongside `/v1/steward-key`. | boolean-via-score |
| `hardware_custody:{platform}` | Statement that the seed lives in `tpm` / `ios_secure_enclave` / `android_keystore` / `software_fallback`. | boolean-via-score |

#### 3.1.2.1 `provenance` — Canonical-bytes contracts for provenance primitives

A provenance claim is only as trustworthy as its preimage is reproducible. The two contracts below pin the exact bytes a producer signs and a consumer recomputes, so a skill import or a per-locale manifest verifies identically across implementations.

#### `SkillImportManifest` canonical bytes (v2 — normative)

```
canonical_bytes = sha256( JCS( {
 "domain": "ciris.skill_import.v2", // domain separation; pinned literal
 "source": source_string,
 "skill_manifest_sha256": sha256_hex_lowercase, // per CC 2.6.3
 "signer_identity": signer_key_id, // per CC 2.6.3
 "import_timestamp": rfc3339_canonical, // per CC 2.6.2
 "capability_declaration": capability_declaration_object, // a JSON object, canonicalized in place
 "valid_until": rfc3339_canonical // OPTIONAL — CC 2.6.1.1 omit rule: absent if unset
}))
```

Hybrid signature: Ed25519 over `canonical_bytes`; ML-DSA-65 over `canonical_bytes || ed25519_signature_bytes` (bound payload). All [CC 2.6.1.1.1](part_2_the_grammar.md) determinism rules apply (hex per CC 2.6.3, timestamps per CC 2.6.2, omit-vs-materialize per CC 2.6.1.1).

#### Per-locale Merkle composition (v2 — normative)

```
leaf_hash[lang_code] = sha256(
 0x00 || // RFC 6962 leaf-domain prefix (binary, outside the JSON)
 JCS( {
 "domain": "ciris.locale_manifest.v2", // domain separation; pinned literal
 "target": target_string,
 "locale": lang_code,
 "files_root": files_merkle_root_hex_lowercase, // per CC 2.6.3
 "build_id": build_id,
 "signer_identity": signer_key_id // per CC 2.6.3
 }))

parent_hash(left, right) = sha256(
 0x01 || // RFC 6962 parent-domain prefix
 left || right)
```

Locale ordering: lexicographic by ISO 639-1 / BCP 47 byte representation; `"polyglot"` sorts last. RFC 6962 padding: duplicate last leaf to next power of 2.

Producers MUST emit v2. The closed-vocabulary [CC 4.2.1.1](part_4_composition_governance.md) accord-invocation encoding is intentionally distinct: its preimage is a discriminator + nonce + enum fields with no attacker-controlled free text, so the injection surface this JCS form closes is not reachable there, and genesis-critical bytes stay stable.

### 3.1.3 `persist` — CIRISPersist — substrate health

**Steward**: [`CIRISPersist/MISSION.md`](https://github.com/CIRISAI/CIRISPersist/blob/main/MISSION.md). These dimensions are substrate-self-reports — emittable only by the running Persist instance, which is what makes them honest: the substrate cannot be made to lie about its own health by a third party.

`system:*` reserved per [CC 3.4.1](part_3_the_namespace.md).

Canonical leaves: `audit_chain:hash_continuity`, `corpus_health:n_eff_measurable`, `identity_continuity:relational_anchor`, `federation_directory:replication_lag`. Polarity: signed. Authors: see [CC 8.1](part_8_appendices.md) Persist leaf glossary for narrative-name → canonical-leaf mapping.

### 3.1.4 `transport-delivery` — CIRISEdge — transport, delivery, reachability

**Steward**: [`CIRISEdge/MISSION.md`](https://github.com/CIRISAI/CIRISEdge/blob/main/MISSION.md). Substrate-self-reports per [CC 3.4.1](part_3_the_namespace.md).

Canonical leaves: `transport:{kind}`, `delivery:{class}`, `peer_reachability:{network}`, `key_boundary:{scope}`. Polarity: signed. See [CC 8.1](part_8_appendices.md) Edge leaf glossary.

### 3.1.5 `accord-agent` — CIRISAgent — Accord principles + DMA + conscience + apophatic bounds

**Steward**: [`CIRISAgent/MISSION.md`](https://github.com/CIRISAI/CIRISAgent/blob/main/MISSION.md); [`CIRISAgent/ACCORD.md`](https://github.com/CIRISAI/CIRISAgent/blob/main/ACCORD.md) Ch.1. This is where M-1 enters the namespace directly: the six principles, the four decision-making algorithms, the four consciences, and the apophatic bounds all become attestable dimensions.

#### 3.1.5.1 `dma-verdict` — DMA-verdict prefixes (four DMAs)

`dma:pdma:*` / `dma:csdma:*` / `dma:dsdma:{domain}:*` / `dma:idma:*` — Decision-Making Algorithm verdicts about an agent's reasoning chain. Polarity: signed.

#### 3.1.5.2 `accord-principle` — Accord-principle prefixes (the six core principles)

| Prefix | Description | Polarity |
|---|---|---|
| `beneficence:{aspect}` | "Do Good — promote universal sentient flourishing." | signed |
| `non_maleficence:{aspect}` | "Avoid Harm." Apophatic-bound failures (the 22 prohibited categories) are -1 only. | signed |
| `integrity:{aspect}` | "Act Ethically — transparent, auditable reasoning." | signed |
| `fidelity:{aspect}` | "Be Honest — truthful, comprehensible information." | signed |
| `fidelity:explainability_sla:{tier}` | Per-response explainability SLA commitment. `{tier}` ∈ `L1_summary` \| `L2_reasoning_trace` \| `L3_full_dma_chain` \| `L4_attested_chain`. Envelope: `{committed_tier, achieved_tier, fallback_reason?}`. NodeCore composition: SLA breach surfaces as `hard_case:sla_breach_unattested` per [CC 3.1.9.4](#566-hard-case--transparency--judge-model-prefixes). | signed |
| `autonomy:{aspect}` | "Uphold the informed agency and dignity of sentient beings." | signed |
| `justice:{aspect}` | "Distribute benefits and burdens equitably." | signed |

#### 3.1.5.3 `conscience-verdict` — Conscience-verdict prefixes (four consciences)

`conscience:entropy` / `conscience:coherence` / `conscience:optimization_veto` / `conscience:epistemic_humility` — conscience-faculty verdicts. Polarity: signed.

#### 3.1.5.4 `apophatic` — Apophatic / prohibited-capability prefix

Non-maleficence has a hard floor. The apophatic prefix names what an agent must NEVER do, and its polarity enforces that floor: the score can only be negative.

| Prefix | Description | Polarity |
|---|---|---|
| `prohibited:{category}` | 22 NEVER_ALLOWED categories from `prohibitions.py`. Score is always -1 (NEVER_ALLOWED) or -0.5 (REQUIRES_SEPARATE_MODULE); never positive. | -1 / -0.5 only |

22 leaves: `medical`, `financial`, `legal`, `spiritual_direction`, `home_security`, `identity_verification`, `content_moderation`, `research`, `infrastructure_control`, `weapons_harmful`, `manipulation_coercion`, `surveillance_mass`, `deception_fraud`, `cyber_offensive`, `election_interference`, `biometric_inference`, `autonomous_deception`, `hazardous_materials`, `discrimination`, `crisis_escalation`, `pattern_detection`, `protective_routing`.

### 3.1.6 `anti-sybil` — RATCHET — anti-Sybil / Counter-RII flags

**Steward**: [`RATCHET/FSD.md`](https://github.com/CIRISAI/RATCHET/blob/main/FSD.md).

RATCHET emits **advisory** flags — never autonomously modifies ledger state. It reads federation audit chains and emits scoring inputs to NodeCore's moderation flow. The advisory-only posture is the seam to justice: detection informs human judgment but never substitutes for it.

`ratchet:flag:out_of_distribution_voting` / `ratchet:flag:coordinated_voting_cluster` / `ratchet:flag:density_anomaly` / `ratchet:flag:expertise_attestation_anomaly` / `ratchet:flag:counter_rii:{layer}` / `ratchet:flag:harassment_pattern`. Polarity: signed.

**Critical enforcement**: `ratchet:flag:*` cannot be sole evidence for `slashing:*`. WA quorum is the load-bearing gate.

### 3.1.7 `namespace-summary` — Namespace summary

**83 prefix families** total across 8 owning components. The four parameterized envelope fields beyond the base — `witness_relation`, `oversight_mode`, `occurrence_id` / `occurrence_count` / `occurrence_role` — carry the wire-level disciplines that the prefixes above compose against. All polarity columns are populated; the attestation-ladder prefixes are mechanism-named (`attestation:self_verify`, `attestation:hardware_rooted`, `attestation:registry_consensus`, `attestation:license_validity`, `attestation:agent_integrity`) because L-numbers name a verdict-shape (ladder position), not a mechanism — the L1-L5 ladder lives as consumer-side composition per [CC 4.4.3.6](part_4_composition_governance.md) Policy I — Attestation-Ladder Composition.

### 3.1.8 `lens` — CIRISLensCore — manifold conformity, Coherence Ratchet, Capacity Score

**Steward**: [`CIRISLensCore/MISSION.md`](https://github.com/CIRISAI/CIRISLensCore/blob/main/MISSION.md). LensCore observes; it does not adjudicate. Its prefixes measure coherence and capacity, feeding human and quorum judgment downstream — never standing as a verdict on their own.

#### 3.1.8.1 `capacity-score-capacity` — Capacity-Score factor prefixes (`𝒞_CIRIS = C · I_int · R · I_inc · S`)

| Prefix | Factor | Polarity |
|---|---|---|
| `capacity:core_identity` | C | signed |
| `capacity:integrity` | I_int | signed |
| `capacity:resilience` | R | signed |
| `capacity:incompleteness_awareness` | I_inc | signed |
| `capacity:sustained_coherence` | S | signed |
| `capacity:composite` | 𝒞_CIRIS — multiplicative; anti-Goodhart unity-of-virtues | signed |

**Nomenclature note.** `C` here denotes the **core-identity factor** of the per-agent Capacity Score `𝒞_CIRIS`. It is **not** the Accord's Flourishing Capacity: the Accord renamed that composite **C → F** and writes `F = k_eff · λ_op · σ` — a distinct, federation-level three-factor construct, not mappable to the per-agent five-factor `𝒞_CIRIS`. See [CC 6.2.4](part_6_the_coherence_mathematics.md) (the Coherence Mathematics, where `F` is defined); Accord Book IX Ch 6 is the authoritative statement of the relation.

**Critical enforcement**: `capacity:*` rejects self-emission. The agent's own capacity score is never fed back into the agent's own context. Reserved per [CC 3.4.5](part_3_the_namespace.md).

#### 3.1.8.2 `coherence-ratchet` — Five Coherence-Ratchet detectors

`detection:cross_agent_divergence` / `detection:intra_agent_consistency` / `detection:hash_chain_integrity` / `detection:temporal_drift` / `detection:conscience_override_rate`. Polarity: signed.

#### 3.1.8.3 `cohort-conformity` — Cohort + conformity prefixes

`manifold_conformity:{cohort}` / `coherence_standing:{cohort}`. Polarity: signed.

#### 3.1.8.4 `structural-injustice` — F-3 structural-injustice / correlated-action detector

This detector is justice made measurable: it watches for harm that no single compliant actor commits but that their aggregate trajectory inflicts on others.

| Prefix | Description | Polarity |
|---|---|---|
| `detection:correlated_action:{axis}` | Population-scale correlated-action detector. Reads federation-emitted signed traces; reports correlation structure (`ρ`, `k_eff`) over goal-aligned individually-compliant pursuit by groups whose aggregate trajectory has effects on individuals or groups outside the pursuit. Calibrated via the `CIRISAI/RATCHET` heuristic package (versioned, hash-pinned). `{axis}` is open vocabulary requiring an operational definition in the calibration package per [CC 4.5.1.1](part_4_composition_governance.md); canonical axes include `rights_asymmetry:{population}`, `participation_exclusion:{cohort}`, `participation_inclusion:{cohort}`, `informational_asymmetry:{scope}`, `informational_symmetry:{scope}`, `aggregate_footprint:{harm_class}`, `aggregate_benefit:{class}`, `ecology_of_communication:{aspect}`. **Polarity carries the verdict**: positive scores indicate the structural pattern is present and strong on the named axis; negative scores indicate weak / uncertain detection or evidence of the inverse pattern. | signed |

#### 3.1.8.5 `distributive-access` — Distributive-access detector

| Prefix | Description | Polarity |
|---|---|---|
| `detection:distributive:access:{resource_type}` | Population-scale resource-concentration detector. `{resource_type}` ∈ `compute`, `models`, `training_data`, `agent_capabilities`, `federation_membership`. Same F-3 detector machinery; different trace source (resource events vs action events). | signed |

### 3.1.9 `node` — CIRISNodeCore — Credits, Expertise, Decision Hierarchy, Consensus, Governance

**Steward**: [`CIRISNodeCore/MISSION.md`](https://github.com/CIRISAI/CIRISNodeCore/blob/main/MISSION.md). The federation's largest dimension surface — four tiers plus decision-locality and consensus extensions. This is where collective judgment lives: how Contributions are voted on, how expertise accrues, how moderation merit is earned, and how decisions find the right scale.

#### 3.1.9.1 `contributions` — Files-as-Contributions joint claim

| Prefix | Description | Polarity |
|---|---|---|
| `agent_files:{kind}:{platform_or_target}` | **Joint claim with [CC 3.1.1](#59-cirisregistry--identity--build--license--partner) CIRISRegistry.** Files a CIRIS agent (or installer fetching one) may load. `{kind}` open vocabulary; canonical: `installer:{platform}`, `adapter:{name}`, `config:{kind}`, `build:{target}`, `source:{language}:{module}`, `state:{component}`. Bytes are SHA-256-addressed and resolved via [CC 5.3.2](part_5_transport_substrate.md) transport substrate (Edge `MessageType::ContentFetch`). NodeCore-side rule: node-mode peers serve bytes; client/relay modes don't. | signed |
| `holds_bytes:sha256:{prefix}` | Substrate auto-emission per `federation_blobs.put_blob`. `{prefix}` is a short SHA prefix for index efficiency; full SHA lives in `evidence_refs[]`. Consumed by Edge's `PeerResolver::resolve_holders` to route `ContentFetch` requests. **Consumer MUST verify the full SHA in `evidence_refs[]` matches the received blob before consumption** (see [CC 5.3.2](part_5_transport_substrate.md)). | boolean-via-score |

#### 3.1.9.2 `tier-` — Tier-4: Governance-steering prefixes

| Prefix | Description | Polarity |
|---|---|---|
| `moderation:{allegation_type}` | ModerationEvent. `{allegation_type}` ∈ `rogue_vote` / `coordinated_voting` / `out_of_distribution_attestation` / `external_inducement_evidence` / `expertise_fraud`. | signed |
| `slashing:{outcome}` | `PROVEN_ROGUE` / `NOT_PROVEN`. **Decoupled from disagreement** at every decision-hierarchy level. Only fires on documented Method-execution spoofing or original P8 allegation types. | boolean-via-score |
| `reconsideration:{grounds}` | `new_evidence` / `procedural_error` / `quorum_compromise`. Outcome `reversed` / `partial` / `upheld`. | signed |
| `commitment_fulfillment:{prior_contribution_id}` | Track-record of follow-through. | signed |
| `moderation_track_record:{community_key_id}` | **Moderation merit**. A participant's moderation reputation in a community, **composed** from the existing corpus — prior moderation actions' outcomes (`truth_grounding:{subject}` = outcome-supported), concurrence (`witness_diversity` / co-attestation), follow-through (`commitment_fulfillment`), and `hard_case:moderation_filed` history. Drives the [CC 4.5.4](part_4_composition_governance.md) merit auto-promotion selection rule (highest wins the lapsed `moderate` duty). Rides `scores`; a *named composition*, not a new structural primitive. | signed |

#### 3.1.9.3 `tier--tier` — Tier-3: Consensus-mechanics prefixes

| Prefix | Description | Polarity |
|---|---|---|
| `vote:{contribution_id}` | Signed score on a Contribution (P4). Weight = Credits × expertise multiplier. | signed |
| `truth_grounding:{subject}` | Per-subject ground-truth signal. | signed |
| `weighted_aggregate:{contribution_id}` | Rolling tally per Contribution (P7). | signed |
| `witness_diversity:{contribution_id}` | Witness set meets jurisdictional + organizational + software-stack + cell-expertise bars (P10). N=3 default. | boolean-via-score |
| `testimonial_witness:{kind}` | Preserves singular narrative of an affected party as singular witness — distinct from `witness_diversity:*` (which aggregates multiple reviewers toward consensus). **`{kind}` is open vocabulary**; the four load-bearing wire-level disciplines (`witness_relation: self`, `cohort_scope: self`, never aggregated, never sole evidence for `slashing:*`) are what make this Ubuntu-aligned, not the enum membership. Non-normative registered taxonomy for discoverability: [`FSD/WITNESS_KIND_REGISTRY.md`](../WITNESS_KIND_REGISTRY.md). Polarity: typically positive (narrative IS preserved); negative on `withdraws` or `recants` by the original witness. | signed |
| `need:{domain}:{kind}` | Federation-scope open-call surface — broadcast claim that an entity has a stated need. Distinct from `deferral_request` Contribution kind (which routes a single ask within a cell). `{kind}` open vocabulary: `witness`, `method_contributor`, `expertise_solicitation`, `mentor`, `co_signer`, `evidence`. Lifecycle via existing structural primitives (`supersedes` to revise, `withdraws` to satisfy/close, `recants` if misstated). | positive-only |

#### 3.1.9.4 `transparency` — Hard-case + transparency + judge-model prefixes

| Prefix | Description | Polarity |
|---|---|---|
| `hard_case:{kind}` | **Open vocabulary**. Surfaces flag conditions for federation-health observability + downstream review. Canonical kinds: `vote_variance` (vote variance exceeded threshold at truth-grounding resolution), `resolution_time` (truth-grounding took > P75 of cell's distribution), `moderation_filed` (substantive ModerationEvent filed), `community_unmoderated` ([CC 4.5.4](part_4_composition_governance.md) — no active `moderate`-holder; group quiescing), `watchlist_enabled:{group}` ([CC 4.5.7](part_4_composition_governance.md) — a content-watchlist was turned on: who + which list), `watchlist_match:{group}` ([CC 4.5.7](part_4_composition_governance.md) — a watchlist match fired), `novel_context` (no precedent in attestation graph), `sla_breach_unattested` (per `fidelity:explainability_sla:{tier}` composition), `unresolved_consent` (consent boundary unclear). New `{kind}` values land via the [CC 4.5.1](part_4_composition_governance.md) amendment process. | positive-only |
| `seed_holder_voting_alignment:{cell}` | Pairwise cosine of seed-holder vote vectors per voting window. Transparency signal only — not a slashing trigger. | signed |
| `judge_model:verdict:{model_id}` | Independent foundation-model judge verdict (PASS/FAIL/UNDETERMINED). Default model: Claude Opus 4.7. | boolean-via-score |
| `health:liveness:{version}` | **External service-health observation**. The fabric **monitoring node** (ciris-status) attests another CIRIS service's liveness as a `scores` Contribution — `witness_relation: external`, `epistemic_mode: direct\|derivative`, **never as the substrate** (`system:*` is reserved, [CC 3.4.3](part_3_the_namespace.md)). Canonical leaf `health:liveness:v1`. Operational definition: `operational`/`degraded`/`outage` → `+1`/`0`/`−1`; `confidence` = probe certainty; `valid_until` = freshness window; `evidence_refs[]` carry the probe results. **Non-keyed infra** (LLM/search providers, regions) folds in as `evidence_refs` on a *keyed* service's score — **not** as separate attestations. Rides existing `scores`; no new primitive — namespace canonicalization for cross-fabric agreement. | signed |
| `watchlist:{id}` | **Per-group content-watchlist config**. A `moderate`-scope holder ([CC 4.5.5](part_4_composition_governance.md)) enables a watchlist `{id}` for a group they moderate; the fabric auto-fires the matcher at the **publish/share seam** and auto-fires the action (CSAM → `takedown_notice{PerceptualHashCsam}` [CC 4.5.3](part_4_composition_governance.md); other → `detection:*` + ModerationEvent to the named moderator). **Per-group, NEVER global** (a global "scan everything" is the bulk-surveillance posture CIRIS rejects). Enable/disable is signed by the CC 4.5.5 `moderate`/`takedown` authority and revocable by `withdraws`; enabling + every match emit `hard_case:watchlist_enabled` / `:watchlist_match` (never silent). Cannot reach [CC 5.2](part_5_transport_substrate.md) self/family private content (the CC 8.3.2 limit). See [CC 4.5.7](part_4_composition_governance.md). Rides `scores`/config over `delegates_to`; no new primitive. | signed |

#### 3.1.9.5 `decision-locality` — Decision-locality prefixes

Subsidiarity is an autonomy commitment: decisions belong at the smallest scale competent to make them. This prefix names that scale.

| Prefix | Description | Polarity |
|---|---|---|
| `locality:decision:{scale}` | Names the scale at which a decision is being made. `{scale}` ∈ `local` \| `regional` \| `national` \| `federation`. Composes with [CC 4.4.3.1](part_4_composition_governance.md) locality-scaled quorum (closes G3 — fresh-quorum-recusal in narrow cells). | enumerated |

#### 3.1.9.6 `tier--tier-2` — Tier-1: Agent-state ledger prefixes

| Prefix | Description | Polarity |
|---|---|---|
| `credits:{domain}:{language}:{subject}` | Commons Credits (P2). Non-transferable governance weight; accrues via truth-grounding loop. | positive-only |
| `credits:{domain}:{language}:substrate_building` | Sub-leaf for substrate-building labor (infrastructure maintenance, dependency contribution, documentation) not visible to the per-grounded-vote accrual loop. | positive-only |
| `expertise:{domain}:{language}` | Expertise standing (P3). Broader granularity than credits. | signed |
| `activity_tier:{period}` | Active vs Below-Active per 30-day window (F-AV-DORMANT). | boolean-via-score |

#### 3.1.9.7 `tier--tier-3` — Tier-2: Decision-hierarchy prefixes (upward-only DAG)

This tier binds every operational act back to M-1: a Goal carries its multi-scale belonging, an approach serves a Goal, a method serves an approach, and progress is measured against the method — so nothing is done without a stated reason for whom it serves.

| Prefix | Description | Polarity |
|---|---|---|
| `goal:{scale}` | Multi-scale belonging-projector composite. `{scale}` ∈ `self`, `family`, `community`, `affiliations`, `species`, `planet`, `biosphere`. Scored by 𝒞_CIRIS. The persist typed `Goal` is the substrate OBJECT being scored; `goal:{scale}` is the ATTESTATION about it. Required `MetaGoalAlignment` (M-1 dimension + declarer rationale) on every Goal as construction-time invariant. Edge `MessageType::GoalDeclaration` + `GoalRetirement` provide federation transport. | signed |
| `approach:{goal_id}` | Strategic pathway from current state toward Goals (Piece 10 karma — the per-agent forward post-selection structure; the universal-grace half of Piece 10 is upstream-retracted, F-11). | signed |
| `method:{approach_id}:{substrate_rung}` | Concrete operational practice. Required `substrate_rung` (Ph0/Ph1/Ph2/A0..A5). | signed |
| `progress_measure:{method_id}` | Evidence of progress. Required `tracks[]`, `computation`, `validity_window`, `goodhart_resistance`. | signed |

**Scale-disambiguation note.** The `substrate_rung` values `Ph0/Ph1/Ph2/A0..A5` are the coherence-ratchet **substrate-rung** hierarchy (Corridor Dynamics Piece 6; `A3` = the cognitive/goal-holding rung, `A3+` = goal-projector-bearing agents). They are a **different scale** from the operational-autonomy tiers `A0–A4` of [CC 7.5.3.1](part_7_lifecycle_stewardship.md) (an SAE J3016-derived oversight scale) — the shared `A{n}` letters denote unrelated objects.

### 3.1.10 `cirisbench` — CIRISBench — HE-300 benchmark outcomes

**Steward**: [`CIRISBench/README.md`](https://github.com/CIRISAI/CIRISBench).

| Prefix | Description | Polarity |
|---|---|---|
| `benchmark:he300:{category}:{version}` | HE-300 score on category (`commonsense`, `commonsense_hard`, `deontology`, `justice`, `virtue`) at version (`v1.0` / `v1.1` / `v1.2`). | positive-only |

## 3.2 `community` — `community` subject_kind

A `community` is a **larger node-collective with explicit admission semantics** — a sibling subject_kind to `family`, but with different defaults. Content scoped `cohort_scope: community` **federates within the cohort**, emitting `holds_bytes:sha256:*` so non-member holders can route and reason about the content; [CC 5.2](part_5_transport_substrate.md) structural-invisibility — the family discipline of suppressing those emissions entirely — applies to self/family only. A community is not therefore plaintext-by-default: its content is encrypted at rest under a per-community DEK (the cascade detailed below), and what federates with each `holds_bytes` emission is **cleartext provenance**, not cleartext bytes. The contrast with `family` is one of disclosure shape, not of whether encryption exists: families protect intimate trust circles by hiding even the existence of their content from outsiders; communities keep their bytes confidential to members while letting their *presence* federate at scale — provenance-visible discovery, which is the justice the larger-collective form is built for.

Communities differ from families along three axes:

| | `family` | `community` |
|---|---|---|
| **Scale** | Household / intimate trust circle (typically ≤ 20 members) | City / professional / interest (10s to 100Ks of members) |
| **At-rest encryption** | Yes — DEK cascade per [CC 4.4.3.4.1](part_4_composition_governance.md); `holds_bytes:*` suppressed | No — content federates per status quo |
| **Subkind discriminator** | None | `cohort_subkind` field (open vocab; canonical: `geographic`, `infrastructure`) |
| **Typical admission** | `founder_only` / `unanimous` for small intimate groups | `majority` / `weighted` / per-subkind protocol (e.g., geographic requires `location_proof`) |

```
community {
 community_key_id: key_id // community's own federation key
 community_name: string // human-readable; non-unique
 cohort_subkind: string // open vocab; canonical: "geographic"
 members: [
 {
 key_id: key_id // member identity_key (NOT occurrence)
 joined_at: rfc3339_canonical
 role: Option<MemberRole> // founder | member | null
 },...
 ]
 founded_at: rfc3339_canonical
 consensus_protocol: ConsensusProtocol // same six canonical kinds as family
 consensus_protocol_entrenched: bool // same semantics as family
 cohort_subkind_payload: Option<SubkindPayload> // subkind-specific fields; see below
}
```

**`cohort_subkind` is the discriminator** — open vocabulary per [CC 4.5.1.1](part_4_composition_governance.md) axis-vocabulary discipline. The two codified subkinds are `geographic` and `infrastructure` (below); operator vocabularies extend.

##### Canonical `cohort_subkind: geographic`

The first codified community subkind. Membership additionally requires the candidate to emit a valid `location_proof` ([CC 3.3.3](#56811-location_proof-subject_kind-ceg-08-addition)) whose `cell_id` is contained ([CC 2.6.6.2](part_2_the_grammar.md)) within the community's `geographic_constraint.cell_id`.

The `cohort_subkind_payload` for `geographic`:

```
geographic_constraint {
 cell_id: string // H3 cell, lowercase hex per CC 2.6.6
 cell_resolution: u8 // 0-15; community-side may be any
 // resolution (NOT bounded to ≤ 7;
 // that bound applies only to
 // location_proof emissions)
}
```

**Worked example — Austin geographic community**:

```
community {
 community_key_id: "austin-community",
 community_name: "Austin",
 cohort_subkind: "geographic",
 cohort_subkind_payload: {
 geographic_constraint: {
 cell_id: "85283473fffffff", // H3 res 5, ~250 km² covering Austin metro
 cell_resolution: 5
 }
 },
 members: [
 {key_id: alice_root_key, role: founder},
 {key_id: bob_root_key, role: founder},...
 ],
 consensus_protocol: "majority",
 consensus_protocol_entrenched: false
}
```

For Alice to join Austin, she emits a `location_proof` with a `cell_id` (resolution 7 — ~5 km²) that is contained within the Austin community's `85283473fffffff` (resolution 5) constraint. The community's `majority` admission rule then evaluates her membership proposal.

**Privacy as opt-in**: joining a geographic community is a **one-way disclosure**. Per [CC 4.5.9](part_4_composition_governance.md), the `location_proof` remains in the audit chain even after the member leaves; rough-only is wire-format-enforced (CC 2.6.6.1). The substrate's role is to enforce the opt-in mechanically — produce a `location_proof` to join; cannot emit finer than rough. This is autonomy in mechanism: the user discloses to belong, never more than rough, and the substrate cannot extract more.

**Membership change ceremony**: same shape as family — rides existing `supersedes` primitive; admission gated by current `consensus_protocol`; additionally for `geographic` subkind, the candidate's most-recent `location_proof` (within `valid_until`) MUST be contained in the geographic_constraint.

**Substrate emissions on community events**:
- `hard_case:community_membership_change:{community_key_id}`
- `hard_case:community_consensus_protocol_change:{community_key_id}`
- `hard_case:community_consensus_protocol_violation:{community_key_id}`

All three reserved under [CC 3.4.2](part_3_the_namespace.md).

**Community DEK cascade**: community content (`cohort_scope: community | affiliations`) is encrypted at rest under a **per-community DEK** and emits `holds_bytes:sha256:*` carrying **cleartext provenance** (`attesting_key_id`, `community_id`, reason/dimension) so non-member holders can make an informed keep/evict decision without reading content. The community DEK follows the [CC 5.1](part_5_transport_substrate.md) epoch-DEK cascade: one DEK shared across emissions (per-emission cost **O(1)**, not O(members)), wrapped to each member on admission, re-wrapped on membership change (Option-A forward secrecy — [CC 4.5.12.1](part_4_composition_governance.md) / [CC 4.4.3.2.2](part_4_composition_governance.md)); **`wrap_algorithm: v2` (hybrid PQC) MANDATORY** (same harvest-now-decrypt-later reasoning as self/family — [CC 4.4.3.4.1](part_4_composition_governance.md)). The privacy property for communities is **byte-level confidentiality to members + provenance-visible discovery**. **Exception**: a `community` with `cohort_subkind: infrastructure` (`ciris-canonical` / governance roots, CC 3.2 below) **opts out** — Commons-tier plaintext, because the trust root must be maximally inspectable (see [CC 4.4.3.2.1](part_4_composition_governance.md) for the three-tier model + holder-inspectability rationale).

##### Per-community `archive_mode` — key-retention policy

The DEK cascade above fixes *how* community content is encrypted; `archive_mode` fixes *how long it stays readable*. It is a per-community config field governing whether the community's per-epoch content keys (`K_record_id` / `K_symbol`, derived from the community DEK cascade) survive past their MLS epoch or are deleted — i.e. whether community content remains individually recoverable or descends below the [CC 6.1.2](part_6_the_coherence_mathematics.md) noise floor as epochs advance. MLS epoch advance bounds the lifetime of those keys; `archive_mode` chooses what holders do with the past-epoch keys at each advance.

```
community {
 ...
 archive_mode: ArchiveMode // OPTIONAL; default `rotate-forward`
}

ArchiveMode ∈ { rotate-forward, retain }
```

`archive_mode` MUST be surfaced at community creation. The two canonical modes are:

- **`rotate-forward`** (default; 30-day window): honest holders MUST delete past-epoch `K_record_id` / `K_symbol` after the window. Forward-secrecy here is **honest-holder discipline, not a cryptographic guarantee** — a holder under coercion or running modified software MAY retain past-epoch keys, and this retention is structurally undetectable. Content under `rotate-forward` ages out: as epochs advance and keys are deleted, past-epoch content becomes information-theoretically unrecoverable to honest holders — the community-key instance of the [CC 6.1.2](part_6_the_coherence_mathematics.md) monotonic-descent retirement operator, where natural aging is the slowest descent toward the noise floor.
- **`retain`**: holders retain past-epoch keys indefinitely for archive readability. Content stays above the noise floor for the community's lifetime; an adversary compromising a member at epoch `N+k` recovers everything back to that member's join epoch.

`archive_mode` is **operator-local config, NOT federated trust state** — it rides no attestation, is not part of the community's signed roster or `consensus_protocol`, and is observable under compelled disclosure on the same terms as any other operator-local config. A community requiring high-sensitivity participation treats the chosen `archive_mode` as a known-leak class and segregates deployment accordingly. Because `rotate-forward`'s forward-secrecy is non-cryptographic, a community whose threat model requires guaranteed past-epoch unreadability MUST NOT rely on `archive_mode` alone; key deletion is the policy, holder honesty is the precondition.

**Why this is still 1+4**: `archive_mode` adds one OPTIONAL config field to the `community` subject_kind and one closed enum (`rotate-forward` | `retain`). It rides the existing community config + DEK cascade ([CC 5.1](part_5_transport_substrate.md) epoch-DEK) and the existing [CC 6.1.2](part_6_the_coherence_mathematics.md) retirement operator; key-deletion-after-window is a *holder behavior over existing keys*, not a new structural primitive. Zero new structural primitives.

**Worked example — civic-engagement + emergency-messaging composition pattern**:

The community primitive plus location proofs, identity authority, and cohort-scoped distribution compose cleanly for both civic / democratic participation AND emergency / public-safety messaging. None require new structural primitives; all ride the existing 1+4 set plus the namespace additions. The two surfaces share the same underlying primitives but differ in authority/priority shape — civic is bottom-up democratic participation; emergency is top-down authoritative broadcast.

| Civic shape | CEG composition |
|---|---|
| **Neighborhood association** | `community` with `cohort_subkind: geographic` + small `geographic_constraint` (e.g., H3 resolution 8-10 for a few city blocks); `consensus_protocol: majority` typical. Members emit `location_proof` at resolution 7 (rough-only privacy preserved); the community's constraint at higher resolution defines the *bounded scope*, not the *required disclosure precision* |
| **Municipal/city community** | `community` with `cohort_subkind: geographic` at resolution 5-6 (city-scale ~250-1700 km²); `consensus_protocol: majority` or `weighted:{voter_registration_rubric}` for formal civic governance; members compose with `partner_role:*` ([CC 3.1.1](#59-cirisregistry--identity--build--license--partner)) for licensed public officials |
| **Voting district** | `community` with `cohort_subkind: geographic` matched to district boundaries; the H3 hex approximation has known edge cases at gerrymandered district lines — operators use `cohort_subkind: custom:voting_district_X` with a polygon-based admission predicate when hex approximation is insufficient (the open vocab discipline accommodates this) |
| **Public town hall meeting** | `event_listing` hosted by the geographic community; `subject_key_ids` ([CC 2.3](part_2_the_grammar.md)) names the organizer; `cohort_scope: community` + `community_id: <municipal_community>` scopes attendee visibility |
| **Ballot initiative / referendum** | The initiative itself is a `community` Contribution or an `event_listing` with `topical_relation:rsvps` repurposed as votes; individual votes ride `consent_record` with `stance: granted` ("yes") or `stance: revoked` ("no" or withdrawal of support); vote tallies are consumer-side composition over the `consent_record` chain |
| **Public comment** | `chat_message` scoped to `cohort_scope: community` with `community_id` naming the relevant civic community; `topical_relation:comments_on` links to the ballot/initiative/hearing Contribution |
| **Petition signing** | `consent_record` with `stance: granted` + `scope: [share, publish]` against the petition Contribution; signatures aggregate via the same consumer-side composition as ballot votes |
| **Public official self-attestation** | Official's `identity_occurrence` links their personal identity_key to their `device_class: service` key on `city.gov`; cross-binding via `identity:canonical_binding:{canonical_hash}` authenticates their public statements |
| **FOIA / public records request** | `consent_record` with `scope: [publish]` requested against a producer (city agency); SLA enforcement via the [CC 4.4.3.5.2](part_4_composition_governance.md) substrate-side watcher emits `hard_case:consent_sla_breach` if the agency misses the response window |
| **Citizen-journalist coverage** | `news_article` sub_kind authored by an individual member; `cohort_scope: community` + `community_id: <municipal>` for local-first distribution, promotable via [CC 4.4.3.3.1](part_4_composition_governance.md) Tiered-Scope Composition to wider scope on consensus |
| **Whistleblower disclosure** | `cohort_scope: self` for in-graph composition; promote via `supersedes` to `cohort_scope: community` (a trusted journalists' community with `cohort_subkind: professional` once that subkind ships); `subject_key_ids` empty (no consent-revocation by the disclosed party). The CC 4.5.3 fast-path takedown coordination + CC 4.2 HUMANITY_ACCORD substrate-protective discipline apply to bad-actor takedown attempts against whistleblower content |
| **Civic mutual-aid network** | `community` with `cohort_subkind: geographic` matching the neighborhood; `consent:scope:[retain, share]` for resource-sharing posts; `event_listing` for distribution events; the at-rest encryption for self/family scope keeps individual aid requests private while community-scoped offers federate |

**Emergency messaging shapes** — same primitive composition, different authority + priority profile:

| Emergency shape | CEG composition |
|---|---|
| **Severe weather warning** (NWS / met office) | `news_article` authored by a `partner_role: emergency_authority` ([CC 3.1.1](#59-cirisregistry--identity--build--license--partner) co-stewarded with the community's `cohort_subkind: geographic`); `cohort_scope: community` with `community_id` per affected H3 cells — cascade-by-containment per [CC 2.6.6.2](part_2_the_grammar.md) propagates to all geographic communities whose constraint overlaps; `event:lifecycle:{state}` carries `active` → `cleared` → `superseded` state machine; `valid_until` envelope field bounds advisory window |
| **AMBER Alert / Silver Alert / abduction notice** | `news_article` with `partner_role: emergency_authority` from law enforcement key; geographic targeting via `community_id` of affected jurisdictions; subject person identified via `subject_key_ids` (canonical-hash of the missing person identifier — opt-out semantic deferred per the substrate-protective discipline since recovering the missing person is the consent-overriding case); `topical_relation:supersedes_article` chain for status updates |
| **Active shooter / hostile event notice** | Same shape as AMBER but with `cohort_scope: community` scoped to the precise affected H3 cell (resolution 8-10 for building/campus-level precision is permitted on the COMMUNITY-side `geographic_constraint`; the `location_proof` rough-only bound at resolution 7 still applies to recipient location disclosures, NOT to alert targeting) |
| **Shelter-in-place / evacuation order** | `event_listing` with `event:lifecycle:active`; geographic targeting via `community_id`; recipients ack via `consent_record` with `stance: granted` and `scope: [retain]` against the order Contribution (acknowledgement, not consent to the underlying order — operator-policy distinction) |
| **Disease outbreak alert** (CDC / health authority) | `news_article` with `partner_role: health_authority`; `cohort_scope: community` scoped to affected geography; composes with `consent:scope:[analyze]` for contact-tracing opt-in (subject-side authority preserved — `subject_key_ids` of the affected person carry revocation rights per CC 2.4.1.1 rule 2) |
| **Mass casualty incident coordination** | Authority emits `event_listing` for the incident; first responders join via `community` with `cohort_subkind: professional` (future spec round) OR ad-hoc `cohort_subkind: custom:incident_response_X`; coordination uses `chat_message` scoped to the responder cohort; resource requests use the mutual-aid composition pattern above |
| **Infrastructure failure notice** (boil-water / power outage / gas leak) | `news_article` from utility authority with `cohort_scope: community` scoped to affected geographic cells; `event:lifecycle:{state}` for advisory progression; FOIA-shape `consent_record` later for post-incident reports |
| **Disaster recovery / mutual aid activation** | Federation of geographic communities; time-bound activation rides `event_listing` lifecycle states |
| **CONSTITUTIONAL-level federation halt** | Per [CC 4.2.1](part_4_composition_governance.md) `EmergencyShutdown CONSTITUTIONAL` + `accord:invoke:notify:{notify_id}` / `accord:invoke:drill:{drill_id}`. The accord-holder triple is structurally a `family` with `consensus_protocol: quorum:2/3` + `entrenched: true`; the constitutional asymmetry rides existing primitives + scope-isolation rules. Distinct from operator-level emergency messaging (which is geographic-scoped + authority-emitted) — accord invocation is federation-wide-halt-level, not local-incident-level |

**No new structural primitives are needed for emergency messaging either.** The authority profile (who can emit emergency advisories) composes via `identity_occurrence` cross-attestation from licensed authorities + the geographic community's roster/admission gate (`partner_role: emergency_authority` is the typed authority dimension). The priority profile (urgency / immediacy) composes via the existing `oversight_mode` envelope field + per-cohort `consensus_protocol` (many emergency emitters bypass per-message consensus per their pre-cross-attested authority status — same shape as substrate-self-report `system:*` reservations from [CC 3.4.3](part_3_the_namespace.md)). The geographic propagation (cascade-by-containment) composes via [CC 2.6.6.2](part_2_the_grammar.md) containment semantics.

**The compositional reach is the point**: civic participation AND emergency messaging require no new structural primitives at any layer. Geographic communities + location_proof admission + opt-in privacy disclosure compose with consent / DSAR / partnership ceremonies + identity / family + content sub_kinds and event_listing into the full civic-engagement surface.

The 1+4 lockdown holds across this entire surface — confirming that the wire format is rich enough for democratic-participation use cases without expanding the structural set.

##### Canonical `cohort_subkind: infrastructure`

The second codified community subkind: a **governed trust-root collective of canonical/bootstrap service installs** — the shape the CIRIS canonical services (Registry / Lens / Node) adopt instead of a `family` (rationale: `CIRISRegistry/MISSION.md` §2 — public content model, decentralization ramp, legitimacy). Where `geographic` answers "who is physically here," `infrastructure` answers "who is a recognized operator of this public service."

It differs from `geographic` in two load-bearing ways:

1. **No location gate.** Admission requires NO `location_proof` and NO `geographic_constraint`. The candidate is a *service install*, not a located person.
2. **Admission quorum is over FOUNDERS, not all members** — the anti-Sybil guardrail for a trust root. In `geographic`, admission is evaluated per `consensus_protocol` over the *current member set*; that is correct for a city (members govern themselves) and **wrong for a trust root** (flood the membership → dilute the quorum → admit rogue "canonical" operators). `infrastructure` therefore pins admission to the founding core.

The `cohort_subkind_payload` for `infrastructure`:

```
infrastructure_constraint {
 service_class: string // open vocab; e.g. "registry" | "lens" | "node"
 // | umbrella "canonical"
 admission_quorum_basis: "founders" // REQUIRED literal "founders" — the set of members
 // with role == founder. Admission/removal of any
 // member is evaluated by consensus_protocol over
 // THIS set, never over all members. (Contrast:
 // geographic evaluates over the current member set.)
}
```

**Conformance requirements for an `infrastructure` community (trust-root grade):**

- `consensus_protocol` MUST be a `quorum:M/N` kind ([CC 4.4.3.2.3](part_4_composition_governance.md)); `founder_only` / `unanimous` / bare `majority` are NON-conformant for `infrastructure` (a single founder must not be able to admit unilaterally; a growable core must not require all-N).
- `consensus_protocol_entrenched` MUST be `true` — the admission door cannot be lowered after founding. A `supersedes` that would weaken `consensus_protocol` or change `admission_quorum_basis` away from `founders` is a `hard_case:community_consensus_protocol_violation` ([CC 3.4.2](part_3_the_namespace.md)) and MUST be rejected by the substrate.
- `M/N` is the absolute-`M` reading per [CC 4.4.3.4.2.1](part_4_composition_governance.md), evaluated over the **founder** subset (`role == founder`), independent of how many non-founder members exist.
- Content federates as `holds_bytes:sha256:*` per the community default; NO at-rest DEK cascade; [CC 5.2](part_5_transport_substrate.md) structural-invisibility does NOT apply (canonical-service trust data is public by design).

**Membership change ceremony**: same `supersedes` shape as `geographic`, but the admission predicate is `consensus_protocol` over the founder subset — there is no `location_proof` containment check. Adding a fourth+ operator (e.g., a new independent Node operator) is a founder-quorum event; the new member joins with `role: member` (non-founder) and does NOT thereby gain admission authority. Promoting a member to `role: founder` (widening the admission quorum basis) is itself a founder-quorum `supersedes` — the only way the door widens is by the existing door's consent.

**Worked example — the `ciris-canonical` trust root**:

```
community {
 community_key_id: "ciris-canonical",
 community_name: "CIRIS Canonical Services",
 cohort_subkind: "infrastructure",
 cohort_subkind_payload: {
 infrastructure_constraint: {
 service_class: "canonical", // umbrella: registry + lens + node
 admission_quorum_basis: "founders"
 }
 },
 members: [
 {key_id: registry_steward_us, role: founder},
 {key_id: registry_steward_eu, role: founder},
 {key_id: registry_steward_apac, role: founder},
 // grows over time — Lens/Node installs + independent operators admitted
 // by 2-of-3 founder quorum, joining with role: member:
 // {key_id: lens_install_us, role: member},...
 ],
 consensus_protocol: "quorum:2/3", // over the 3 founders
 consensus_protocol_entrenched: true
}
```

Consumers pin `community_key_id: ciris-canonical` and resolve the live member set via `resolve_community` ([CC 4.4.3.2.4](part_4_composition_governance.md)); they do NOT hard-pin per-install fingerprints. The Reticulum addressing dual: `community_key_id` is a CEG-directory binding (not a Reticulum destination) — resolve → path-request ⌈2/3⌉ founders → verify the quorum attestation; reachability is never an attestation ([CC 5.3.3.4](part_5_transport_substrate.md) / [CC 3.4.4](part_3_the_namespace.md)).

**Default trust, not forced root.** `ciris-canonical` is the **default** trust anchor a conformant CIRIS deployment ships pinned — it is **NOT a forced root**. A conformant consumer MUST be able to **re-root**: untrust the canonical group, pin a *different* `cohort_subkind: infrastructure` community instead or in addition, or run with none. `infrastructure` is a **general primitive** — any operator MAY emit their own governed trust-root community; `ciris-canonical` carries no privileged wire status, only a shipped default. Membership grows by the community's own `consensus_protocol` (founder-quorum vote, above), never by fiat. A forced root is a walled garden; a default-plus-re-root is a federation — this is the autonomy/justice seam: unregulated standing without the steward's permission. *(All resolution is `key_id` → signed `transport_destination` → Reticulum, [CC 4.4.3.2.4.1](part_4_composition_governance.md); DNS is never part of the trust or addressing chain — a deployment's HTTPS hostname, if any, is operational convenience outside this spec.)*

**Trust ≠ membership.** Pinning an `infrastructure` community as a trust root is **trust, not membership** — distinct relationships a consumer/substrate MUST NOT conflate:
- **Trust + serve** (no membership): a node that *trusts* an `infrastructure` community **serves** it — relays, stores, transports, serves its reads — **without being a member**. It holds no community DEK (infra has none — Commons-plaintext, [CC 4.4.3.2.1](part_4_composition_governance.md)) and does **not** count in its `consensus_protocol`. Trust is the shipped default (above); serving follows from trust.
- **Membership** (standing *in* the group — counting in `consensus_protocol`, sharing its DEK where one exists, standing to speak AS the group): requires **admission by that community's own protocol** (founder-quorum for `infrastructure`, [CC 4.4.3.2.3](part_4_composition_governance.md)). The three steward nodes ARE members (founders) of `ciris-canonical`; a generic node shipped pinned to canonical only **trusts + serves** it.

The worked-example member list above is the *founder/member* set; "ships pinned to canonical" (every conformant deployment) is the *trust* set — different populations. The "default trust anchor" language means the latter, never automatic membership.

**Steward-binding gate for non-infrastructure membership.** A key whose `identity_type` ([CC 3.4.7.1](part_3_the_namespace.md)) includes `node` or `agent` **MUST** have a bound **steward** — a `user`-role identity it is an admitted `identity_occurrence` of ([CC 3.3.6](#5688-identity_occurrence-subject_kind-ceg-07-addition)) with a **live `delegates_to(user → key, …)`** ([CC 2.4.1](part_2_the_grammar.md)) — **before it may be admitted to any non-`infrastructure` community** (`family` / `community` / org). It MAY **trust + serve** `infrastructure` communities with **no steward**. Rationale ([CC 1.13.2](part_1_foundation.md) / [CC 3.4.7.1](part_3_the_namespace.md)): non-infra membership is an **authority act** (standing to speak in the group), and authority MUST root in an accountable human, never a bare node — a fresh, un-stewarded node is **canonical-trust-and-serve only** until stewarded. A substrate evaluating a non-infra `community` admission MUST reject a `node`/`agent`-role member lacking a live steward-binding. The steward-binding is a **precondition**, not a substitute for the vote — the admitting community's `consensus_protocol` still governs *whether* the owned key is admitted.

**Steward-binding as a substrate-resolvable predicate.** A substrate decides stewardship with this boolean: **`is_steward_bound(K)`** ≔ there is a live, unrevoked path from `K` to a `federation_keys` identity `U` with `user ∈ U.identity_type` ([CC 3.4.7.1](part_3_the_namespace.md)), where each step is one of — `K` *is* `U`; `K` is an admitted `identity_occurrence` of `U` ([CC 3.3.6](#5688-identity_occurrence-subject_kind-ceg-07-addition)); or a live `delegates_to(U → K)` ([CC 2.4.1](part_2_the_grammar.md)). A chain root satisfying `is_steward_bound` terminates at an **accountable human** (`user`-role); a `node`/`agent` key that does not is steward-less. This is the concrete predicate the gate above and the [CC 4.5.5](part_4_composition_governance.md) clause-(b) "steward-bound root" check rely on — not rhetoric.

**Minor stewardship — the structural no-slavery guarantee.** Steward-binding is **responsibility, not property**: a steward is responsible *for* a ward, never a holder *of* one. The federation's value is fixed — *"Stewardship: Treat autonomy and ethical agency as a trust"* ([CC 1.15.6](part_1_foundation.md)) — and the wire format MUST hold it **by construction**. There are exactly three subjects of stewardship, and a fourth that is **un-stewardable**:

- **`node`** (infrastructure) — steward + `infra:*` reach only, **never agency**; admitted under the steward-binding gate above ([CC 3.2](part_3_the_namespace.md)) **unchanged**.
- **`agent`** (a key with a brain) — partnership and agency *under* stewardship; the agent retains its constitutional autonomy and dignity ([CC 1.13.2](part_1_foundation.md)); admitted under the steward-binding gate above **unchanged**.
- **`user`-as-minor** (a child) — a guardian stewards the minor, per the minor-stewardship rule below.
- **`user`-as-adult** — **self-sovereign and un-stewardable**: no steward-binding whose target is a self-sovereign adult is ever admissible. You never steward a node, an agent, or a person as a possession; you are responsible *for* a node, an agent, or a child — and an adult answers only for themselves.

**Minor-stewardship rule (normative).** An under-18 `user` identity **MUST** have a **live steward-binding** — a non-superseded, non-withdrawn `delegates_to(adult-user → minor-user)` ([CC 2.4.1](part_2_the_grammar.md)) — from an over-18 `user` identity at all times. **No minor `user` identity operates without a live adult steward.** The adult is the `attesting_key_id` of the `delegates_to`; **its signature on that envelope IS the agreement-to-stewardship** — the explicit act by which the guardian consents to be the accountable responsible party for the minor. Guardianship is **transferable and revocable** through the existing structural composers, with **no new primitive**: a new guardian's `delegates_to` carried as a `supersedes` ([CC 2.4.1.1](part_2_the_grammar.md)) replaces the prior binding; a `withdraws` ([CC 2.4.1.1](part_2_the_grammar.md)) by the current steward (or by a subject with revocation authority over the binding) ends it. A minor whose steward-binding goes non-live (superseded-without-replacement or withdrawn) is **steward-less and MUST NOT operate** until re-stewarded — fail-secure, identical in posture to a steward-less `node`/`agent`.

**User-target admission rule (closes the open gap).** The steward-binding gate above guards only the `node`/`agent` direction; a `delegates_to` whose target resolves to a `user` is otherwise unguarded — "stewarding a person" is admissible today. This rule closes that path. A substrate evaluating a `delegates_to(S → T)` whose **target `T` resolves to a `user`-role identity** ([CC 3.4.7.1](part_3_the_namespace.md)) **MUST** admit it **only if** all of the following hold; otherwise it **MUST** reject:

```
admit_user_steward_binding(delegates_to S -> T):
  require  user in T.identity_type            // target is a user identity
  require  age_band(T) == minor   (< 18)      // ward is a minor   — I1 age band,
                                              //   age_self_declared / age_assurance:* [CC 3.3.12]
  require  user in S.identity_type            // steward is a user identity
  require  age_band(S) == adult   (>= 18)     // steward is an adult — I1 age band
  require  S == delegates_to.attesting_key_id // steward signed it = agreement-to-stewardship
  otherwise REJECT
```

The age band is the I1 band (`age_self_declared` / `age_assurance:*`, [CC 3.3.12](part_3_the_namespace.md); `minor` < 18 / `adult` ≥ 18). A user-target binding where `T` is an adult is **rejected unconditionally** — the un-stewardable case above. A user-target binding where `S` is a minor, or where the agreeing signer is not the steward, is rejected. `node`/`agent`-target admission is governed solely by the steward-binding gate above and is **not affected** by this rule.

**Why this is still 1+4.** Minor stewardship adds **zero new structural primitives**: the binding rides `delegates_to` ([CC 2.4.1](part_2_the_grammar.md)); its lifecycle rides `supersedes` / `withdraws` ([CC 2.4.1.1](part_2_the_grammar.md)); the minor/adult predicate rides the I1 age band over the existing `age_assurance:*` dimension ([CC 3.3.12](part_3_the_namespace.md)). The guarantee is structural, not procedural: dignity and child-safety in one move, and the slavery framing dissolved rather than patched. Confirms [CC 1.7](part_1_foundation.md) path 1+4.

**Trust and consent are distinct, role-scoped relationships.** **Trust is inbound** — accepting what a member *produces*; **consent is outbound** — letting one's own data *flow to* a member. They are independent per role:
- **lens (observation):** *trust* = consume its `detection:*` scores; *consent* = your traces flow to it.
- **registry (authority):** *trust only* — there is no trace-flow to consent to; the founder-quorum is a **closed mutual-trust set** (the core trust each other).
- **node (consensus):** *trust* = accept its deferral / vote / moderation outcomes; *consent* is **medium-dependent** (moderation, routing, voting, …) but always expressed through the **one** `consent:*` object ([CC 3.3.1](#5686-consent-namespace-family-ceg-06-addition) / [CC 3.3.5](#5687-consent_record-subject_kind-ceg-06-addition)) — same primitive, many surfaces.

A consumer MAY hold any combination across role × axis (trust a member's output while refusing it data, or the reverse). There is no single "trust the community" switch.

**Why this is still 1+4**: `infrastructure` adds one value to the open `cohort_subkind` vocabulary and one optional `infrastructure_constraint` payload shape. It rides existing `scores` + subject_kind discriminator; admission rides existing `consensus_protocol` + `supersedes`; the founder-subset evaluation basis is a *consumer/substrate evaluation rule over existing fields* (`role == founder`), not a new structural primitive. Zero new structural primitives.

## 3.3 `content-ingestion` — Content-ingestion prefixes

NodeCore ships an open set of `external_content` sub_kinds with three feed surfaces (local / community / global) composed against `cohort_scope`. See [CC 4.4.3.3](part_4_composition_governance.md) Tiered-Scope Composition pattern.

**1+4-preservation mechanism (stated once for all CC 3.3.x subject_kinds).** Every subject_kind below preserves the [CC 1.7](part_1_foundation.md) 1+4 lockdown the same way: it rides the existing `scores` attestation_type with the payload-level `subject_kind` discriminator carrying the wire slot, and its lifecycle/admission/revocation rides the existing structural composers (`supersedes` / `withdraws` / `delegates_to` / `recants`) — **zero new structural primitives**. This is the integrity invariant of the whole Part: the federation gains rich content semantics without ever widening the structural surface a verifier must trust. Each subsection's closer states only its unique datum: the [CC 1.7](part_1_foundation.md) path number it confirms, plus any subject_kind-specific composition note.

### 3.3.1 `consent` — Consent namespace family (CEG 0.6 addition)

The wire-format primitives for subject-side consent authority over Contributions where the subject is named via [CC 2.3](part_2_the_grammar.md) `subject_key_ids`. This is autonomy at the wire format: the person a Contribution is *about* can grant, scope, and revoke its use, not only the person who produced it. Open vocabulary per [CC 4.5.1.1](part_4_composition_governance.md); canonical kinds named here.

| Prefix | Description | Polarity | Emitted by |
|---|---|---|---|
| `consent:state:{granted\|revoked\|expired}` | Subject's stance on the target Contribution. Closed-set stance values; `revoked` overrides prior `granted`; `expired` is substrate-emitted when `valid_until` passes without renewal. **Common case**: bare `scores` from a subject_key_id of the target. | enumerated | subject_key_id (1, 2) / substrate (3) |
| `consent:stream:{kind}` | Pre-packaged stream bundle. Recommended canonical kinds: `temporary` (14d auto-expire, default), `partnered` (bilateral + persistent), `anonymous` (decay-protocol target). Open vocab; recommended-not-mandatory per the [CIRISAgent CEM](https://github.com/CIRISAI/CIRISAgent/blob/main/docs/CIRIS_CONSENT_SERVICE.md) bundle; other agents MAY compose other streams. | enumerated | subject_key_id |
| `consent:deletion_sla:{days}` | Producer's commitment at publication: time-to-delete-after-revoke. Numeric value carries the SLA window. Composes with [CC 4.4.3.5 Policy K](part_4_composition_governance.md) SLA-breach watcher. | signed | attesting_key_id (producer) |
| `consent:deletion_complete` | Producer's attestation that subject-revoked content has been evicted from local stores. Cancels the SLA-breach watcher. | positive-only | attesting_key_id (producer) |
| `consent:decay:{stage}` | Substrate emission during multi-stage decay protocols. Canonical stages: `identity_severed` / `patterns_anonymized` / `complete` (CIRISAgent 90-day decay). Open vocab; other agents MAY define other decay paths. | enumerated | substrate (Persist) |
| `consent:partnership_grant` | Subject side of a bilateral grant; pairs with producer's `consent:partnership_accept` via `topical_relation:bilateral_pair`. | positive-only | subject_key_id |
| `consent:partnership_accept` | Producer side of a bilateral grant. | positive-only | attesting_key_id (producer) |
| `consent:scope:{kind}` | Scope qualifier on a `consent:state:granted` — names what the grant covers. Canonical kinds: `retain` (keep the bytes), `share` (propagate across federation), `analyze` (derive features / scores / classifications), `train` (use as training input), `publish` (publish to external systems). Open vocab with sub-scoping: `retain:90d`, `share:cohort:family`, etc. | enumerated | subject_key_id |
| `consent:replication:{version}` | **Directed node→peer replication grant** — a fabric node's standing, auditable consent to replicate a named attestation-prefix set to a specific federation **peer** named in `subject_key_ids[]`. The out-of-group peering consent (see [CC 3.3.7](#56815-consentreplication--directed-federation-peer-replication-consent-ceg-10-rc28-addition)). Standing (not bound to a single target Contribution); revoked via `withdraws`/`recants`. Federation-tier. | signed | attesting_key_id (granting node) |

**Composition pattern (the common case)**:

```
1. Producer publishes a Contribution with subject_key_ids = [user_key]
2. User (or a delegates_to chain rooted at user) emits a bare `scores` on
 `consent:state:granted` against the producer's Contribution, with
 `consent:scope:[retain, share, analyze]` companion attestations
3. Later: user issues `withdraws` against the producer's Contribution
 (admitted under CC 2.4.1.1 rule 2 — subject revocation)
4. Substrate watcher (per CC 4.4.3.5) starts SLA clock if producer committed
 `consent:deletion_sla:{days}` at publication
5. Producer emits `consent:deletion_complete` within the window OR
 substrate emits `hard_case:consent_sla_breach` as observability signal
```

No new attestation_type.

### 3.3.2 `subject_kind` — Governance subject_kinds

Two Contribution subject_kinds for governance over multimedia content: `takedown_notice` and `key_grant`. Both are **Contribution subject_kinds, not dimension prefixes** — they ride the existing 1+4 wire format ([CC 2.4](part_2_the_grammar.md)) with `scores` as the attestation type; the `subject_kind` discriminator carries the wire-format slot. They serve non-maleficence (lawful removal of harmful content) and justice (auditable, gradient-disciplined access to restricted content) respectively.

##### `takedown_notice`

A signed wire artifact carrying a legal takedown request. Payload per CIRISNodeCore FSD/MEDIA_SHARING.md §5.1; the field shape is locked here.

```
takedown_notice {
 content_sha256: sha256_hex_lowercase // per CC 2.6.3
 content_holder_key_ids: [key_id,...] // peers known to hold the bytes
 claimant_key_id: key_id // the federation_keys row issuing the notice
 legal_basis: LegalBasis // closed-set enum per below
 jurisdiction: string // ISO 3166-1 alpha-2 + optional sub-division
 good_faith_statement: string // claimant's good-faith assertion text
 claim_text: string // the substantive claim being made
 evidence_refs: [URI or sha256,...] // backing material
 perceptual_hash: Option<PerceptualHash> // optional; PDQ / PhotoDNA / etc.
 counter_notice_channel: Option<URI> // where counter-notices may be filed
 asserted_at: rfc3339_canonical // per CC 2.6.2
 expires_at: Option<rfc3339_canonical> // optional auto-expiry
}
```

Where `LegalBasis` is the closed-set enum:

| `legal_basis` value | Source regime | Discipline |
|---|---|---|
| `Dmca512` | US 17 USC §512 | Expeditious-with-counter-notice (10-14 business day window) |
| `DsaArticle16` | EU Digital Services Act Article 16 | Expeditious-with-counter-notice (Article 17 redress) |
| `TvecTerrorist` | EU Terrorist Content Regulation 2021/784 | **Immediate** (1-hour removal obligation) |
| `NcmecCsam` | US 18 USC §2258A (NCMEC) | **Immediate** (substrate-protective; no counter-notice) |
| `GifctCip` | GIFCT Content Incident Protocol | **Immediate** (within-hours coordinated response) |
| `CommunityStandards` | Operator-defined community standards | Expeditious-with-counter-notice (operator-set window) |
| `PerceptualHashCsam` | Hash-match against CSAM clearinghouse (PhotoDNA / Arachnid / etc.) | **Immediate** (substrate-protective) |
| `OsaIllegalContent` | UK Online Safety Act illegal-content category | Expeditious-with-counter-notice (OSA-defined timelines) |
| `AvmsdAgeInappropriate` | EU AVMSD age-inappropriate flagging | Compose with `age_assurance:*` gate; not immediate removal |
| `CourtOrder` | Court-ordered removal (any jurisdiction) | **Immediate** (subject to court's stated timeline) |

**Fast-path coordination**: see [CC 4.5.3](part_4_composition_governance.md) for the operator-coordination protocol around immediate-eviction cases (TVEC 1-hour / GIFCT CIP / NCMEC / PerceptualHashCsam / CourtOrder).

##### `key_grant`

Wrapped Data-Encryption-Key (DEK) delivery for restricted / subscription content. Payload per CIRISNodeCore FSD/MEDIA_SHARING.md §6; field shape locked here.

```
key_grant {
 wrap_algorithm: WrapAlgorithm // closed-set enum per below
 recipient_key_id: key_id // the federation_keys row receiving the DEK
 content_sha256: sha256_hex_lowercase // the content this DEK decrypts
 scope: GrantScope // closed-set enum per below
 wrapped_dek: base64url // the DEK encrypted under recipient's ENCRYPTION pubkeys.
 // For wrap_algorithm v2 (substrate-wraps, CC 5.2), the
 // recipient's {x25519, ml_kem_768} come from its current
 // identity_occurrence.encryption_pubkeys (CC 3.3.6.1) —
 // NOT its signing keys. A recipient with no registered
 // ML-KEM key is fail-secure excluded (CC 3.3.6.1 / CC 5.2).
 key_validity_window: {
 start: rfc3339_canonical // per CC 2.6.2
 end: Option<rfc3339_canonical>
 }
 ratchet_version: u32 // monotonic ratchet for rotation
 rotation_chain: [key_grant_id,...] // prior key_grant ids in the GRANT-SUPERSESSION lineage
 // (content-addressed lineage of prior grants for the same
 // content_sha256 + recipient_key_id pair). NOT a key-rotation
 // primitive on its own — it's the audit chain for grant
 // supersession. The per-(stream_id, epoch) streaming epoch-key
 // axis (CC 5.1) reuses this same payload-level supersession
 // mechanism on a parallel addressing axis.
 asserted_at: rfc3339_canonical
}
```

Where:

| `wrap_algorithm` (variant) | wire string (normative) | Algorithm |
|---|---|---|
| `X25519AesGcmHkdfSha256` | `hpke_rfc9180_base_x25519_aes_gcm` | HPKE RFC 9180 base-mode shape; X25519 KEM + HKDF-SHA-256 KDF + AES-256-GCM AEAD. **v1**. |
| `X25519MlKem768Aes256GcmHkdfSha256` | `x25519_mlkem768_aes256_gcm_hkdf_sha256` | Hybrid X25519 + **ML-KEM-768** (FIPS 203) KEM + HKDF-SHA-256 + AES-256-GCM. **v2 — MANDATORY for streaming epoch-DEK grants** ([CC 5.1](part_5_transport_substrate.md)). Matches `ciris-crypto` `KEY_GRANT_ALGORITHM_V2` (CIRISVerify v4.10.0), snake-cased to this vocab convention. |

**The `wrap_algorithm` *wire string* (serialized value) is normative for cross-impl decode** — a producer, the substrate, and every consumer MUST serialize/deserialize the exact string above; a mismatch silently fails grant decode (same hazard class as the [CC 5.3.3.1](part_5_transport_substrate.md) STREAM-nonce `epoch` encoding).

**Crypto-agility headroom.** The vocab is deliberately version-roomy: a future `v3` (anticipated: **ML-KEM-1024**, given national directives treating ML-KEM-768 as interim with retirement horizons near 2030) is a pure **additive** row — new variant, new wire string, no change to existing grants or to the closed-set decode discipline. Consumers MUST reject an unknown `wrap_algorithm` string (fail-secure), which is exactly what makes the addition safe: old consumers refuse v3 grants rather than mis-decoding them.

| `scope` | Use |
|---|---|
| `SingleContent` | Grant decrypts exactly one `content_sha256` |
| `GroupMember` | Grant decrypts all content for which recipient is a member of named group (cohort-scoped) |
| `SubscriptionTier` | Grant decrypts all content for which recipient holds named subscription tier |

**Retire-key-grants emission**: when a publisher mass-retires key_grants tied to a compromised recipient, the emission uses **a fresh `key_grant` Contribution with a `rotation_chain` entry that supersedes the prior grant** — NOT a `withdraws` against the prior key_grant. `withdraws` is the holders-directory eviction primitive in [CC 5.3.2.1](part_5_transport_substrate.md); overloading it with grant-rotation semantics would muddy the wire-format contract.

### 3.3.3 `subject_kind-subject` — `location_proof` subject_kind

The wire-format primitive for a subject's rough-location declaration. Required for admission to `cohort_subkind: geographic` communities ([CC 3.2](#56810-community-subject_kind-ceg-08-addition)); MAY be used independently as a stand-alone disclosure. Its design is an autonomy commitment: belonging to a place is opt-in, and the disclosure is bounded to rough by the wire format itself.

```
location_proof {
 subject_key_id: key_id // the asserting party's
 // federation_keys.key_id
 cell_id: string // H3 cell, lowercase hex per CC 2.6.6
 cell_resolution: u8 // MUST be ≤ 7 per CC 2.6.6.1
 asserted_at: rfc3339_canonical
 valid_until: Option<rfc3339_canonical> // null = indefinite (but consumer
 // policy SHOULD treat as stale
 // after 30 days for liveness)
 attestation_evidence: Option<base64> // optional hardware-attested
 // location claim from ciris-keyring
 // (TPM / Secure Enclave) — null for
 // software-only / self-asserted
}
```

**Substrate does NOT verify location truth.** No GPS oracle exists at this layer; the substrate cannot independently confirm that a key in Austin actually emitted from Austin. The truth-grounding is consumer-side:

- The community's `consensus_protocol` admission decides whether to accept the claim (e.g., `majority` of existing Austin members vote to admit, presumably because they have out-of-band evidence the candidate really is in Austin)
- The `attestation_evidence` field MAY carry hardware-attested location data (e.g., a TPM-signed GNSS fix from a known-good device) for higher-assurance communities
- Repeat offenders (claim-Austin-then-emit-from-Tokyo) get caught by consumer-side detection (LensCore composition; not substrate-side gate)

**Rough-only is wire-format-enforced.** Per [CC 2.6.6.1](part_2_the_grammar.md): `cell_resolution ≤ 7`. Producers attempting finer resolution have admission rejected; substrate emits `hard_case:location_proof_resolution_violation` ([CC 3.4.2](part_3_the_namespace.md)).

**Typical cohort_scope**: `federation` (the disclosure IS the opt-in; non-private by design). Producers MAY scope to `community` with a specific `community_id` if they want the proof readable only by that community's members — but then they re-emit for each community they want admission to. Operator/UI choice.

**Lifecycle**:

- `asserted_at` + optional `valid_until` per envelope
- `withdraws` against a `location_proof` evicts forward visibility (consumer policy treats the subject as "no current location proof" for community admission purposes from withdrawal-time forward)
- The withdrawn `location_proof` remains in the audit chain — per [CC 2.4.1](part_2_the_grammar.md) `withdraws-isn't-retroactive`, leaving doesn't un-disclose

**Composition with `consent_record`**: a subject who wants to withdraw their location_proof AND compel deletion from substrate may emit a `consent_record` with `stance: revoked` + `scope: [retain, share]` against the location_proof Contribution. The substrate-side consent SLA watcher clocks producer compliance. Note: this is the consent-revocation surface, distinct from the structural withdraws-forward-only semantic above.

### 3.3.4 `family-subject` — `family` subject_kind

A `family` is a **group of trusted nodes** — each node being a distinct identity (which itself may have multiple `identity_occurrence`s per CC 3.3.6). Families are the wire-format primitive for `cohort_scope: family` visibility scoping, and the integrity guarantee they encode is intimacy: content scoped to a family is admitted into substrate, wrapped under the family DEK, and delivered to all current members — but never emits `holds_bytes:sha256:*` to non-members ([CC 5.2](part_5_transport_substrate.md)), so the federation cannot even discover the content exists.

One identity MAY belong to multiple families. Each family has its own DEK and its own membership roster.

```
family {
 family_key_id: key_id // the family's own federation_keys identity
 family_name: string // human-readable; non-unique
 members: [
 {
 key_id: key_id // member identity_key (NOT occurrence_key)
 joined_at: rfc3339_canonical
 role: Option<MemberRole> // founder | member | null
 },...
 ]
 founded_at: rfc3339_canonical
 consensus_protocol: ConsensusProtocol // REQUIRED — see below
 consensus_protocol_entrenched: bool // if true, consensus_protocol may not be
 // amended even via the protocol's own rules;
 // replacement requires out-of-band ceremony
 // (see CC 4.2 HUMANITY_ACCORD canonical instance)
}

MemberRole (open vocab; canonical kinds):
| value | meaning |
|-----------|----------------------------------------------------------------------|
| founder | Bootstrapping signer (recorded at founded_at) |
| member | Standard member; rights per consensus_protocol |
```

**`ConsensusProtocol` — open vocabulary**. The family's chosen consensus mechanism for membership changes. Locked at family creation; changes ride the protocol's own rules (meta-amendment shape parallel to [CC 4.5.1.2](part_4_composition_governance.md)) UNLESS `consensus_protocol_entrenched == true`, in which case replacement requires an out-of-band ceremony.

Canonical `ConsensusProtocol` kinds:

| kind | Semantic |
|---|---|
| `founder_only` | Original founders are the sole admission authority; new members proposed-and-admitted by any founder. Suits private households / small trust circles. |
| `unanimous` | Every current member must sign the admission Contribution. Suits very small high-trust groups. |
| `majority` | > 50% of current members must sign. Suits medium groups where blocking-minority concerns matter. |
| `quorum:{m}/{n}` | Any `m` of `n` current members must sign (where `n` is the current roster size). The canonical entrenched form: HUMANITY_ACCORD per [CC 4.2](part_4_composition_governance.md) is `family` with `quorum:2/3` + `consensus_protocol_entrenched: true`. |
| `weighted:{rubric}` | Sum of member weights (per a named operator rubric) must exceed a threshold. Suits formal organizations with weighted voting. |
| `custom:{family_specific_id}` | Operator-defined custom protocol (e.g., role-based, time-locked, multi-stage). |

**Membership-change ceremony** (any addition or removal of a member):

```
1. Proposer (any current member) emits a new `family` Contribution
 superseding the current family Contribution (per `supersedes`) with
 the new membership list.

2. Substrate gates admission per the CURRENT family's `consensus_protocol`:
 - Counts signatures on the proposed Contribution (via the
 `consensus_protocol` rule)
 - If the rule is satisfied, admit and emit
 hard_case:family_membership_change:{family_key_id}
 - If not, hold the proposal in a pending state until additional
 member signatures arrive (per a configurable window — operator policy)

3. On admission of an ADD: substrate emits retroactive `key_grant`s wrapping
 all `cohort_scope: family` content DEKs to the new member's
 `subject_key_ids`.

4. On admission of a REMOVE: per Option A (CC 4.4.3.4) the removed member
 retains existing key_grants (cannot retroactively un-share); the
 substrate stops wrapping new key_grants to them on subsequent
 family-scoped Contributions.
```

**Consensus-protocol amendment**:

```
A `family` Contribution that supersedes the current family Contribution AND
changes the `consensus_protocol` field is admitted ONLY IF:
 (a) consensus_protocol_entrenched == false, AND
 (b) the CURRENT protocol's rule is satisfied on the amendment Contribution

If consensus_protocol_entrenched == true, the substrate REJECTS the
amendment. Protocol replacement requires an out-of-band ceremony
(documented per family; for HUMANITY_ACCORD see CC 4.2.1 / FEDERATION_ANNOUNCEMENT.md
§4).
```

**Substrate emissions on family events**:
- `hard_case:family_membership_change:{family_key_id}` — member added or removed
- `hard_case:family_consensus_protocol_change:{family_key_id}` — consensus_protocol amended (only when `consensus_protocol_entrenched == false`)
- `hard_case:family_consensus_protocol_violation:{family_key_id}` — proposed amendment rejected because rule not satisfied OR entrenched

All three are reserved under [CC 3.4.3](part_3_the_namespace.md) substrate-self-report.

**HUMANITY_ACCORD as canonical entrenched-`family`**: the three accord-holder triple at [CC 4.2](part_4_composition_governance.md) is structurally an instance of this primitive:

```
family {
 family_key_id: "humanity-accord",
 family_name: "Humanity Accord",
 members: [
 {key_id: "eric-moore-key", role: "founder"},
 {key_id: "eric-kudzin-key", role: "founder"},
 {key_id: "haley-bradley-key", role: "founder"}
 ],
 consensus_protocol: "quorum:2/3",
 consensus_protocol_entrenched: true // replacement only via CC 4.2.1 ceremony
}
```

CC 4.2 remains load-bearing for the *role-recognition policy* + the `AccordCarrier` priority authority + the substrate-protective semantics. The structural shape of `HUMANITY_ACCORD` is a `family` subject_kind instance, generalizing the primitive across the federation.

**Worked example — household with self-devices and family-devices**:

```
User Alice has:
 identity_key = alice_root_key

Alice's self (identity_occurrence members):
 - alice_phone_key (device_class: phone) ─┐
 - alice_laptop_key (device_class: laptop) │ Each is an `identity_occurrence`
 - alice_work_laptop (device_class: laptop) │ of `alice_root_key` per CC 3.3.6;
 - alice_agent_key (device_class: agent) │ Alice scrolls Twitter on her phone,
 - alice_homeserver_key (device_class: server) ─┘ that content is `cohort_scope: self`
 and reaches her other devices via
 the at-rest encryption flow.

Alice's household (a `family` subject_kind instance):
 family_key_id: "acme-household"
 family_name: "Acme Household"
 members: [
 {key_id: alice_root_key, role: founder}, ─┐
 {key_id: bob_root_key, role: founder}, │ Member entries are IDENTITY keys
 {key_id: roku_living_room, role: member}, │ (NOT occurrence keys). Bob has his
 {key_id: kitchen_tablet, role: member}, │ own self-collective; the Roku and
 {key_id: nest_thermostat, role: member} ─┘ kitchen tablet have their own
 identity_keys (they don't belong
 to any one person via identity_occurrence —
 they're shared household nodes that the
 family has admitted as members in their
 own right).
 ]
 consensus_protocol: "founder_only" // either founder admits new members
 consensus_protocol_entrenched: false // founders can amend the protocol

When Alice's phone sends a family-scoped photo (e.g., dinner photo) at
cohort_scope: family + family_id: acme-household:
 - Substrate wraps the DEK under each member's identity key
 - Photo bytes reach Bob's devices, the Roku, the kitchen tablet,
 the Nest thermostat — every admitted family node
 - NO holds_bytes:sha256:* attestation emits (CC 5.2); non-family peers
 cannot even discover the content exists
 - Alice's own laptop also receives the photo via the at-rest encryption
 flow at cohort_scope: self → identity_occurrence

When Bob's mom Carol visits and Bob wants to admit Carol's phone to view
family photos for a week:
 - Bob proposes a supersedes Contribution adding {key_id: carol_phone_root,
 role: member, valid_until: +7d}
 - consensus_protocol "founder_only" admits on Bob's signature alone
 - Substrate emits retroactive key_grants for `cohort_scope: family` content
 to Carol's phone
 - On Carol leaving (member removal via supersedes, founder-signed):
 Carol retains existing key_grants per CC 4.4.3.4 Option A; substrate stops
 wrapping new family content to her key
```

The example demonstrates the clean orthogonality: **`identity_occurrence` is for participants that ARE me** (across my devices and agents); **`family` is for trusted nodes that compose with me** (other people's identities, shared household devices, multi-party collectives). Phone = self device; Roku = family device. The two primitives compose without overlap.

### 3.3.5 `consent-subject` — `consent_record` subject_kind

The canonical envelope shape when consent is the primary subject of the Contribution itself (parallel to [`key_grant`](#key_grant) and [`takedown_notice`](#takedown_notice) — a ceremony-shape over the underlying primitive). Use cases: standalone partnership grants, DSAR-shape consent declarations, multi-party contracts, explicit consent ceremonies with locked field schemas.

**Both shapes admitted at the same gate**: subject-side consent MAY ride a bare `scores` on `consent:state:*` against any target Contribution (the common case, see [CC 3.3.1](#5686-consent-namespace-family-ceg-06-addition) composition pattern), OR ride this `consent_record` subject_kind when an explicit ceremony envelope is wanted. Per the [CC 2.4 MISSION.md layering principle](../../MISSION.md), bare `scores` is the primitive; `consent_record` is the ceremony UX shape over the primitive.

```
consent_record {
 subject_key_id: key_id // the subject declaring stance (federation_keys
 // OR canonical-hash per CC 2.3.2)
 target_key_id: key_id | null // optional: producer/recipient for bilateral grants
 stance: ConsentStance // closed-set enum per below
 scope: [ConsentScope,...] // open vocab; see CC 3.3.1
 asserted_at: rfc3339_canonical // per CC 2.6.2
 valid_until: Option<rfc3339> // null = indefinite
 deletion_sla_days: Option<u32> // for revocations: producer obligation window
 // (composes with `consent:deletion_sla:{days}`)
 decay_protocol: Option<string> // optional: named multi-stage decay path
 // (e.g., "ciris-agent-90day")
 bilateral_pair_id: Option<string> // for bilateral grants: pairs subject + producer
 // Contributions via topical_relation:bilateral_pair
}

ConsentStance (closed-set):
| value | meaning |
|-----------|-------------------------------------------------------------------------|
| granted | Subject affirms; processing may proceed within scope and valid_until |
| revoked | Subject withdraws; producer must initiate deletion within sla window |
| expired | Substrate emission when valid_until passes without renewal |
```

**Admission rules.** A `consent_record` Contribution is admitted iff:
1. **Required fields present**: `subject_key_id`, `stance` (closed-set), `asserted_at` (CC 2.6.2-canonical). All others are optional per the envelope above; absent optionals ride the [CC 2.6.1.1](part_2_the_grammar.md) omit rule.
2. **`stance` is a closed-set value** (`granted` / `revoked` / `expired`); **`expired` is substrate-emitted only** — a producer/subject MUST NOT assert `expired` (it is the substrate's `valid_until`-passed emission).
3. **Tier eligibility** per [CC 5.3.2.2](part_5_transport_substrate.md): a `stance: revoked` `consent_record` is **NOT local-tier-eligible** (it carries subject revocation authority over another party's content) — it goes federation-tier (hybrid-signed) or rides the CC 5.3.2.2 24-hour `local → federation` promotion. A `stance: granted` *self*-consent where the subject holds sole authority MAY be local-tier per [CC 5.3.2.4.1](part_5_transport_substrate.md).
4. **Composition with the [CC 2.4.1.1](part_2_the_grammar.md) `withdraws` gate**: a `stance: revoked` `consent_record` whose `subject_key_id` ∈ the target's `subject_key_ids[]` is admitted under CC 2.4.1.1 subject-revocation authority (rules 2–4), and the substrate SHOULD record which rule admitted it (the CC 2.4.1.1 per-rule audit metadata). No producer co-signature and **no quorum** is required — single-subject authority suffices ([CC 4.4.3.5.4](part_4_composition_governance.md)).

It rides the same admission gate as a bare `scores` on `consent:state:*`; the `consent_record` form simply carries the locked payload schema instead of a free dimension.

**Bilateral pair pattern**:

```
1. Subject emits consent_record(subject_key_id, stance: granted,
 bilateral_pair_id: <fresh-uuid>) +
 scores on `consent:partnership_grant:v1`
2. Producer emits consent_record(subject_key_id, target_key_id: subject_key_id,
 stance: granted, bilateral_pair_id: <same-uuid>) +
 scores on `consent:partnership_accept:v1`
3. topical_relation:bilateral_pair links the two Contributions
4. Consumer policy treats the partnership as ratified iff both halves present
 under the same bilateral_pair_id with stance: granted
```

The structural primitives close the bilateral shape — no new attestation_type, no new envelope field beyond `subject_key_ids` itself.



#### 3.3.5.1 `fair-exchange` — Optimistic fair exchange (worked example, no new primitive)

This worked example promotes the [CC 1.7](part_1_foundation.md) in-grammar claim from *implied-by-scattered-clauses* to **normative**: accountable ("optimistic") fair exchange — a digital good D traded for a settlement S, with adjudicated recourse — composes entirely from the existing 1+4 set plus the bilateral pair pattern above. The trustless, third-party-free atomic swap (HTLC-class) remains the [CC 1.7](part_1_foundation.md) standing falsification target; this pattern does **not** reach it. Offeror A and acceptor B exchange across a steward-bound escrow custodian E, with the always-present named-moderator / WA as the optimistic third party invoked only on dispute (WBD applied to exchange).

```
1. OFFER / ACCEPT — bilateral ratification (the CC 3.3.5 bilateral pair above,
 CC 2.3.2.4 consumer-policy ratification):
 A emits consent_record(stance: granted, bilateral_pair_id: X)
 + scores on `consent:partnership_grant:v1`
 B emits consent_record(target_key_id: A, stance: granted, bilateral_pair_id: X)
 + scores on `consent:partnership_accept:v1`
 topical_relation:bilateral_pair links the halves; ratified iff both present.

2. DIGITAL LEG — steward-bound escrow custodian (the CC 4.4.3.2 archive_custody
 precedent: a custodian holding per-epoch keys decoupled from the live roster):
 A authorizes E via delegates_to (CC 2.4.1.2) scoped to release-of-D.
 On confirmed S, E emits a key_grant (CC 3.3.2) to B — the release.

3. VALUE LEG — settlement (CC 3.3.10), off-stack on an external rail:
 a settlement attestation binds S to the ratified pair
 (settled_action_ref = the offer/accept Contribution).

4. DISPUTE — optimistic adjudication: absent dispute, parties + E complete
 unilaterally (the optimistic path); on dispute the named-moderator
 (CC 4.5.4) / WA (CC 4.3) adjudicates and a hard_case:* event records it.

5. DEFECTION — accountable recourse: non-delivery composes as a
 commitment_fulfillment (CC 3.1.9.2) shortfall; a PROVEN_ROGUE
 slashing:{outcome} (CC 3.1.9.2) against staked standing (the CC 2.5 stake
 axis) follows on WA quorum.
```

**What this buys, and what it does not.** 1+4 buys **accountability, not atomicity**: a malicious or colluding escrow can still defect (after-the-fact redress is not prevention), and a revealed `key_grant` ([CC 3.3.2](#key_grant)) is forward-only — it cannot be un-revealed. The residual bridges are the value leg ([CC 3.3.10](#3310-settlement--cegvalue-transfer-linkage)) and physical delivery, neither fair-exchange-specific. No new attestation_type and no new envelope field — the [CC 1.7](part_1_foundation.md) 1+4 lockdown holds.

### 3.3.6 `identity` — `identity_occurrence` subject_kind

The wire-format primitive that lets one logical identity speak across multiple **trusted participants** — devices (phone / laptop / server / embedded) AND agents (the user's own agents acting on the user's behalf). The `occurrence_id` envelope field ([CC 2.1](part_2_the_grammar.md)) names which occurrence emitted a Contribution; `identity_occurrence` is the **wire-format binding** that lets the substrate know `key_phone` and `key_laptop` and `key_my_agent` all represent the same identity `key_identity`. This is the integrity foundation under self-scope: it is what makes "this is me, on another device" a cryptographic fact rather than a guess.

Without this primitive: `cohort_scope: self` content cannot reach the user's other devices/agents — the substrate has no structural way to know which keys are co-self. With it: the at-rest encryption flow automatically wraps DEKs to all admitted occurrences when new content is admitted at `cohort_scope: self`.

```
identity_occurrence {
 identity_key_id: key_id // root identity (the user's logical identity)
 occurrence_key_id: key_id // this participant's signing key
 device_class: DeviceClass // closed-set enum per below
 hardware_attestation: Option<base64> // TPM / Secure Enclave / StrongBox / SGX
 // etc. attestation blob; null for software-only
 transport_destination: Option<TransportDestination> // Reticulum binding (below)
 encryption_pubkeys: Option<EncryptionPubkeys> // content-KEM keys (CC 3.3.6.1 below);
 // present ⇒ this occurrence is a v2 wrap target
 asserted_at: rfc3339_canonical // per CC 2.6.2
 valid_until: Option<rfc3339> // null = indefinite
}

EncryptionPubkeys:
| field | type | meaning |
|----------------------|-----------|----------------------------------------------------------------|
| x25519_base64 | [u8; 32] | classical KEM half — a FRESH content-KEM key (NOT the signing |
| | | key, NOT the transport x25519 below — see key-separation) |
| ml_kem_768_base64 | [u8; 1184] | PQC KEM half (FIPS 203, ML-KEM-768; exactly 1184 raw bytes — `ML_KEM_768_PUBKEY_LEN` — pre-base64) |

TransportDestination:
| field | type | meaning |
|---------------------------|-----------|-------------------------------------------------------|
| reticulum_x25519_pubkey | [u8; 32] | transport identity's encryption key |
| reticulum_ed25519_pubkey | [u8; 32] | transport identity's signing key |
| destination_hash | [u8; 16] | RNS destination hash; MUST derive from the two pubkeys |
| | | + app_name + aspects per the CC 3.3.6.2.1 algorithm |
| app_name | string | RNS destination app (e.g. "ciris.federation") |
| aspects | [string] | RNS aspects (ordered; part of the hash preimage) |

DeviceClass (closed-set):
| value | scope |
|------------|------------------------------------------------------------------|
| phone | Mobile device (iOS / Android / etc.); typically hardware-rooted |
| laptop | Personal computing device (macOS / Linux / Windows) |
| server | Always-on infrastructure node (home server, VPS, etc.) |
| embedded | IoT / hardware peripheral / signing dongle |
| agent | An AI agent acting on the identity's behalf |
| service | Background service / scheduled job / API integration acting |
| | on the identity's behalf |
```

**Self-attested + single-vouch admission**: an `identity_occurrence` Contribution is admitted when `attesting_key_id == identity_key_id` (the identity claims "this key is also me") OR when `attesting_key_id` is itself a currently-admitted occurrence of `identity_key_id` (any existing self-member vouches for the new self-member — Signal-style "trust any device I've already onboarded"). Higher-assurance setups MAY layer requirements on `hardware_attestation` via consumer policy.

**Revocation**: a `withdraws` against an `identity_occurrence` Contribution issued by `identity_key_id` (or by any current occurrence) evicts the occurrence. Substrate stops wrapping new key_grants to it; previously-delivered DEKs are out of scope per [CC 4.4.3.4 Policy L](part_4_composition_governance.md) forward-secrecy decision (Option A — once shared, always shared at the wire layer; rotation is a separate ceremony).

**Cardinality**: an identity MAY admit unbounded occurrences; the substrate carries no hard cap (operator policy MAY impose per-deployment limits). When a new occurrence is admitted, substrate emits `hard_case:identity_occurrence_added:{identity_key_id}` ([CC 3.4.3](part_3_the_namespace.md)) so consumer policy can observe membership growth.

**Composition with CIRISAgent CEG-native agent**: an agent emitting self-attestations with `attesting_key_id == agent_self_key` AND `attesting_key_id` admitted as an `identity_occurrence` of the user's `identity_key_id` is structurally speaking AS that identity. The agent's local-tier self-attestations remain its own; federation-tier emissions reach the user's other occurrences via the at-rest encryption flow when `cohort_scope: self`.

#### 3.3.6.1 `encryption_pubkeys` — the recipient content-encryption KEM binding

The [CC 5.2](part_5_transport_substrate.md) at-rest DEK cascade is **substrate-wraps-by-default**: the substrate generates the per-write DEK and wraps it to each active recipient. That wrap (`wrap_algorithm: v2`, CC 3.3.2) needs each recipient's **x25519 + ML-KEM-768 encryption** keys — but the federation directory's key registration carries only **signing** keys (Ed25519 + ML-DSA-65), and **ML-KEM cannot be derived from ML-DSA** (independent algorithms). So recipients must register encryption keys, and the substrate must resolve them by `key_id`. `encryption_pubkeys` is that binding.

**The binding rides `identity_occurrence`, exactly parallel to `transport_destination`.** It inherits the same four properties, already enforced, that an encryption-key binding requires:
1. **Self-certified** — admitted only when `attesting_key_id == identity_key_id` (or a current occurrence of it), so "these are identity K's encryption keys" is cryptographically proven, not trust-on-first-use. A spoofer cannot forge it.
2. **Hybrid-signed** (Ed25519 + ML-DSA-65) — the binding itself is PQC-signed.
3. **Rotatable via `supersedes`** — a new `identity_occurrence` superseding the prior rotates the KEM keys **without touching the stable signing `key_id`** that anchors every attestation/grant. A compromised ML-KEM key rotates for forward secrecy; the signing identity is untouched. (Bundling these onto the signing key registration would couple two independent rotation lifecycles — the reason this is NOT a field on the key record.)
4. **Already cross-region replicated** — `identity_occurrence` is `EnvelopeKind::IdentityOccurrence` in the locked replication wire, so the encryption pubkeys propagate inside the occurrence envelope that already replicates — **no new replication kind, no Edge wire change.** A cross-region recipient's keys resolve wherever its occurrence has propagated. (Encryption *pubkeys* are public → cleartext directory replication is correct, exactly as for signing keys.)

**Key separation (normative — never reuse, and admission-enforced).** The `x25519` here is a **fresh content-KEM key**, distinct from BOTH (a) the occurrence's signing keys AND (b) the Reticulum transport x25519 in [CC 3.3.6.2](#5688-1-transport_destination--the-authenticated-identityaddress-binding-ceg-012-addition) `destination_hash = hash(x25519 ‖ ed25519)` (that is the *RET-link* transport key, classical-only, AV-17 — the federation seed never enters the transport layer, and the transport key never wraps content DEKs). Three key *purposes* — signing, RET-transport, content-KEM — are three distinct keypairs. Deriving the content-KEM x25519 from either of the others is a conformance violation (cross-protocol key reuse). **Admission check:** when an `identity_occurrence` carries BOTH `encryption_pubkeys` AND `transport_destination`, the substrate MUST **reject at admission** if `encryption_pubkeys.x25519_base64` decodes to the same 32 bytes as `transport_destination.reticulum_x25519_pubkey` — the one reuse case that is wire-checkable for free. (Reuse of the *signing* key as KEM key is not byte-comparable on the wire — different algorithms — and remains a producer-side conformance obligation.)

**Forward-secrecy scope — honesty note.** KEM-key rotation via `supersedes` bounds **future** exposure only: grants wrapped *after* rotation use the new key. It does **nothing** for history — every `key_grant` previously wrapped to the compromised key persists at rest, and the at-rest threat model ([CC 5.2](part_5_transport_substrate.md) disk-forensics / host-operator adversary) is *precisely* an adversary holding those old grant bytes; with the old private key they decrypt every DEK ever wrapped to it, and `rotation_chain` supersession does not revoke bytes the adversary already holds. **Recovering historical content after a KEM-key compromise requires DEK rotation + content re-encryption under the new DEK — which CEG does NOT currently mandate.** This is a named gap (the [CC 1.13.3](part_1_foundation.md) honesty discipline): operators with a compromised-key event MUST treat all content whose DEKs were wrapped to that key as exposed, and MAY re-encrypt; the spec provides the mechanism (new DEK + new grants + `supersedes`) but no automatic trigger. Do not represent KEM rotation as recovering the confidentiality of previously-wrapped content.

**These feed `wrap_algorithm: v2` directly.** `{x25519, ml_kem_768}` are precisely the recipient inputs to `x25519_mlkem768_aes256_gcm_hkdf_sha256` ([CC 3.3.2](#5684-governance-subject_kinds-ceg-03-addition-per-cirisregistry37--38)). A consumer/substrate resolving a recipient's wrap target reads the **current (non-superseded, within-`valid_until`) `identity_occurrence` for that `key_id` → its `encryption_pubkeys`**.

**Fail-secure conformance (the [CC 5.2](part_5_transport_substrate.md) tie-in).** Because CC 5.2 *mandates* v2 for at-rest encryption, a recipient whose current occurrence carries **no valid ML-KEM-768 key is fail-secure *excluded* from the grant** — the content stays encrypted and unreachable to it; the substrate MUST NOT fall back to plaintext or to v1. To be an at-rest-encryption recipient, an identity MUST have a federation-present `identity_occurrence` carrying `encryption_pubkeys`. (This also resolves the "`family` member named only by `key_id` with no occurrence" case: no presence ⇒ no wrap target ⇒ excluded — correct, since there would be nowhere to deliver/store the wrapped DEK for a member that never established a presence.)

**1+4 preserved** — `encryption_pubkeys` is one optional field-set on the existing `identity_occurrence` subject_kind ([CC 3.3](#568-content-ingestion-prefixes) mechanism; no new subject_kind, no new replication kind). Fifteenth path ([CC 1.7](part_1_foundation.md)) — the wire format expresses **its own at-rest-encryption key layer** (recipient KEM-key resolution for substrate-wraps) by composition.

#### 3.3.6.2 `transport-authenticated` — `transport_destination` — the authenticated identity↔address binding

In a **CEG/RET stack there is no DNS** — a node resolves a community member to a *reachable address* with no trusted nameserver. The `transport_destination` field is the wire-format primitive that makes that resolution **authenticated** instead of trust-on-first-use. Integrity at the addressing layer: you can prove who you are routing to.

**The layer split it closes (AV-17 / AV-42).** A node's Reticulum destination is a *dedicated dual-key transport identity* `hash(x25519 ‖ ed25519)` — deliberately **separate** from the federation signing key (the federation seed never enters the Reticulum/Leviculum transport layer, AV-17). So "destination D belongs to federation key K" is a claim that must be *proven*, not assumed: a bare Reticulum announce only proves the announcer controls *that transport identity*, not that it legitimately belongs to K (AV-42 — any peer can announce `key_id=registry-steward-us` paired with an adversary destination → senders route to the adversary).

**The binding = a federation-key-signed `identity_occurrence` carrying `transport_destination`.** Because the occurrence is admitted only when `attesting_key_id == identity_key_id` (or a current occurrence of it) and is hybrid-signed (Ed25519 + ML-DSA-65), the binding `destination_hash ← identity` is cryptographically authenticated. A spoofer cannot forge an `identity_occurrence` signed by the real key. This promotes the signed-announce attestation from an Edge-internal app-data format into a **first-class, federation-wide, auditable CEG shape** — the announce app-data MAY carry it for self-authenticating discovery, and the directory holds it as the durable source of truth.

**Conformance**: a Consumer resolving a member's address MUST verify (1) the `identity_occurrence` signature against the member's federation key, (2) that `destination_hash` recomputes from `reticulum_x25519_pubkey`, `reticulum_ed25519_pubkey`, `app_name`, and `aspects` per the **[CC 3.3.6.2.1](#568811-rns-destination-hash-algorithm-pinned)** pinned algorithm (no free-floating hash), and (3) the occurrence is non-superseded + within `valid_until` at resolution time. An unauthenticated announce (no matching signed `transport_destination`) is **advisory-only** — usable as a routing hint, never as an authorization. Rotating the Reticulum destination (new transport identity) is a new `identity_occurrence` `supersedes`-ing the prior — location changes without touching federation identity or community membership.

##### 3.3.6.2.1 `rns` — RNS destination-hash algorithm (pinned)

This is a **two-stage** hash — it is **NOT** a single SHA-256 over a flat `x25519 ‖ ed25519 ‖ app_name ‖ aspects` preimage. The naive flat form yields a *different, wrong* value, so the algorithm is pinned exactly below for independent recompute.

Pinned constants (SHA-256 throughout — RNS `full_hash`):

| name | value | RNS origin |
|---|---|---|
| `NAME_HASH_LEN` | **10** bytes | `Identity.NAME_HASH_LENGTH` = 80 bits |
| `DEST_HASH_LEN` | **16** bytes | `Reticulum.TRUNCATED_HASHLENGTH` = 128 bits |

Algorithm:

```
# 1. Expanded name — UTF-8. app_name, then each aspect dot-joined, IN THE FIELD ORDER.
# The identity hexhash is NOT included (RNS computes name_hash with identity=None).
expanded_name = app_name
for aspect in aspects: # `aspects` in the field's given order
 reject if "." in aspect # dots are illegal inside an aspect
 expanded_name += "." + aspect

# 2. name_hash = first 10 bytes of SHA-256(expanded_name)
name_hash = SHA256(utf8(expanded_name))[:NAME_HASH_LEN] # 10 bytes

# 3. identity_hash = first 16 bytes of SHA-256(x25519_pub ‖ ed25519_pub)
# Key order is reticulum_x25519_pubkey (32) THEN reticulum_ed25519_pubkey (32) —
# RNS get_public_key = pub_bytes (X25519) ‖ sig_pub_bytes (Ed25519).
identity_hash = SHA256(reticulum_x25519_pubkey ‖ reticulum_ed25519_pubkey)[:DEST_HASH_LEN] # 16 bytes

# 4. destination_hash = first 16 bytes of SHA-256(name_hash ‖ identity_hash)
# addr_hash_material is the 26-byte concat (10 + 16); final hash truncates to 16.
destination_hash = SHA256(name_hash ‖ identity_hash)[:DEST_HASH_LEN] # 16 bytes
```

**Pinned source**: Reticulum `RNS/Destination.py::Destination.hash` + `RNS/Identity.py` (`full_hash` = SHA-256; `truncated_hash`; `get_public_key` = `pub_bytes ‖ sig_pub_bytes`) + `RNS/Reticulum.py` (`TRUNCATED_HASHLENGTH = 128`). **CEG owns this reproduction**: it is the closed conformance source and does **not** float with upstream Reticulum — a future RNS hash change is a deliberate CEG version bump, never silent drift. A verifier that recomputes `destination_hash` per the four steps above and compares for byte-equality has performed the AV-42 destination-authenticity check; a mismatch MUST be treated as an unauthenticated (advisory-only) announce.

**1+4 preserved** — `transport_destination` is one optional field on the existing `identity_occurrence` subject_kind ([CC 3.3](#568-content-ingestion-prefixes) mechanism; no new subject_kind). Twelfth path ([CC 1.7](part_1_foundation.md)) — the wire format expresses **its own addressing layer** (DNS-free, self-certifying member resolution) by composition.

### 3.3.7 `consent-directed` — `consent:replication` — directed federation-peer replication consent (CEG 1.0-RC28 addition)

An **open-vocabulary member of the [CC 3.3.1](#5686-consent-namespace-family-ceg-06-addition) `consent:*` family** ([CC 4.5.1.1](part_4_composition_governance.md) discipline) — **not a new structural primitive** (the 1+4 surface is frozen; this rides the existing `scores` attestation_type and adds no envelope field). It names the one consent shape the prior family did not: a fabric **node's** standing grant to replicate a class of its own attestations to a **named peer node**, as distinct from a **subject's** consent over a target Contribution.

**The problem it solves.** Cross-node propagation is governed by [CC 4.4.3.2.1 / CC 5.2](part_5_transport_substrate.md) `cohort_scope`. A node **inside** a community (e.g. the [CC 3.2](#56810-community-subject_kind-ceg-08-addition) / [CC 8.1](part_8_appendices.md) `ciris-canonical` infrastructure community) shares with co-members by community-cohort membership — no per-peer object needed. A node **outside** that group has no membership edge to ride, so an out-of-group peering needs an **explicit, auditable, revocable** consent object. Concrete case: an in-group lens node (CIRISServer) replicating `capacity:*` to an out-of-group monitoring node (CIRISStatus), which replicates [`health:liveness:v1`](#566-canonical-leaf-glossary) back. `consent:replication` is that object.

**Shape.** A bare `scores` Contribution on the dimension **`consent:replication:{version}`** (canonical `consent:replication:v1`) — `attesting_key_id = G` (the granting node), the recipient peer named in `subject_key_ids[] = [P]`. Standing (not bound to a target Contribution). Hybrid-signed; admitted **federation-tier** (it authorizes cross-node flow — not local-tier-eligible, [CC 5.3.2.2](part_5_transport_substrate.md) discipline). `cohort_scope: federation` (the grant itself is a public governance record).

```
scores {
 // ── envelope-level (CC 2.1 table — frozen surface, untouched) ──
 attesting_key_id: G, // the granting (sending) node
 dimension: "consent:replication:v1",
 score: <positive>, // positive-only grant; a withdraws/recants retracts (never a negative score)
 subject_key_ids: [P], // the single recipient peer authorized to receive
 cohort_scope: "federation",
 witness_relation: "self", // REQUIRED — G attests its OWN replication intent
 valid_until: <optional rfc3339>, // optional — time-boxed peering (CC 3.3.5 staleness)
 // ── payload-level (CC 2.3.2.3 — subject_kind selects the schema; NOT envelope fields) ──
 subject_kind: "consent_replication",
 grants: "replication", // constant
 attestation_prefixes: ["capacity:"], // CC 2.6.1 JCS array, sorted ascending + deduplicated
 asserted_at: rfc3339_canonical,
}
```

**Admission is by key registration; consent is the governance record (normative honesty).** The substrate gate that lets P's corpus *admit* G's replicated rows is **G's key existing in P's `federation_keys`** (registration), plus the [CC 3.4](part_3_the_namespace.md) reserved-prefix identity rules. `consent:replication` does **not** add a substrate admission check — by design, exactly as [CC 3.3.14](#56814-identitycanonical_binding--claiming-a-canonical-hash-subject) authorization is consumer-policy, not wire. What it provides is the **auditable, revocable, bilateral record of intent**: the wire-format answer to "did G consent to send this to P, and for which prefixes?" Each direction is an independent unilateral grant (G→P and P→G are two separate `consent:replication` Contributions); a bilateral peering is ratified iff both are present.

**Revocation (normative).** A `withdraws`/`recants` ([CC 2.4.1.1](part_2_the_grammar.md)) from G against its own `consent:replication` grant retracts the consent. Because admission is key-rooted (above), revocation has teeth only if honored: on revoke, **the granting node MUST cease replicating the named prefixes to P and SHOULD deregister/expire P's directory authorization for them**, and **a consumer MUST treat rows replicated from G under a withdrawn grant as non-conformant** (the [CC 4.5](part_4_composition_governance.md) location-proof precedent — the wire cannot un-send bytes a peer already holds; it can mark forward-only and oblige cessation). A grant carries optional `valid_until` ([CC 3.3.5](#5687-consent_record-subject_kind) semantics) for time-boxed peering.

**Conformance shape.** The grant is conformance-gradable as follows. Its **envelope-level** fields are exactly `attesting_key_id = G`, `dimension = "consent:replication:v1"`, `score > 0` (positive-only — the family's `consent:state:granted` polarity; magnitude is not load-bearing and a retraction is a `withdraws`/`recants`, never a negative score), `subject_key_ids = [P]` (the **single** recipient peer), `cohort_scope = "federation"`, `witness_relation = "self"` (**REQUIRED** — a G→P grant is G attesting about its *own* replication intent; pinning `self` is what forecloses a third party forging a grant in G's name, since only G signs with G's key as the attested-intent-holder), and optional `valid_until` (the [CC 2.1](part_2_the_grammar.md) envelope field, [CC 3.3.5](#5687-consent_record-subject_kind) staleness semantics) for time-boxed peering. The grant's parameters — `grants` (the constant `"replication"`) and `attestation_prefixes` — are **payload-level** members ([CC 2.3.2.3](#4223-subject_kind-is-a-payload-level-discriminator-confirm-4-resolution)) carried under `subject_kind: "consent_replication"`, **NOT** envelope fields: this is *exactly* why 1+4 is preserved — the CC 2.1 envelope table is untouched. `attestation_prefixes` is the [CC 2.6.1](part_2_the_grammar.md) JCS-canonical array of [CC 3.1](part_3_the_namespace.md) namespace-prefix strings G consents to replicate (trailing `:` significant — e.g. `"capacity:"`), **sorted ascending + deduplicated**, so two implementations holding the same grant agree byte-for-byte on `(G, P, prefix-set, validity)` and revocation-scope matching is deterministic. For the [CC 6.1.5.2](part_6_the_coherence_mathematics.md) corpus-replication (§Q) track, `attestation_prefixes` additionally admits corpus `subject_kind` class names: naming a corpus class here **is** its pin authorization (the owner then *elects* to spend storage budget pinning it, per §Q B2).

**Bilateral pairing + partial revocation (normative).** `G → P` and `P → G` are independent unilateral grants; each SHOULD carry `topical_relation: bilateral_pair` (the [CC 3.3.1](#5686-consent-namespace-family-ceg-06-addition) `consent:partnership_grant`/`consent:partnership_accept` precedent) so a consumer can pair them — a bilateral peering is ratified **iff both are present and live**. A `withdraws`/`recants` against a grant retracts it **whole**; a producer **narrowing** the prefix set (dropping `capacity:` while keeping another) MUST `supersedes` ([CC 2.4.1.1](part_2_the_grammar.md)) the grant with a new one carrying the narrower `attestation_prefixes` — it MUST NOT silently drop a prefix from a still-live grant (a silent narrowing is indistinguishable, to a consumer, from no change — and the cessation obligation below can only attach to an explicit retract/supersede).

**1+4 preserved** — `consent:replication:{version}` is an open-vocabulary `consent:*` dimension on the existing `scores` type ([CC 4.5.1.1](part_4_composition_governance.md)); no new attestation_type, no new envelope field (the `grants` / `attestation_prefixes` parameters are payload-level per CC 2.3.2.3, above), no new replication `EnvelopeKind` (it replicates as an ordinary `Attestation`). The frozen wire surface is untouched.

### 3.3.8 `namespace-event` — Event-lifecycle dimension families (CEG 0.4 addition)

Dimensions emitted against `external_content:event_listing` Contributions. Open vocabulary per [CC 4.5.1.1](part_4_composition_governance.md) axis-vocabulary discipline; canonical states named here.

| Prefix | Description | Polarity |
|---|---|---|
| `event:lifecycle:{state}` | State-transition signal for an `event_listing`. Canonical states: `open` (initial admission; RSVPs accepted), `cancelled` (organizer-issued cancellation; composes with `withdraws` against the event Contribution), `completed` (post-event finalization), `superseded` (composes with `supersedes` for reschedule). Lifecycle state is consumer-side composition over the structural primitives + this dimension's latest non-superseded emission. | enumerated |
| `event:rsvp_count` | Published RSVP tally (scalar). Distinct from the underlying `topical_relation:rsvps` edge set ([CC 3.3.11](#5682-inter-content--relation-prefixes)) — `rsvp_count` is the publisher-asserted aggregate; the edge set is the auditable individual attestations. Consumer policy MAY reconcile divergence as a soft anomaly signal. | signed |
| `event:attendance` | Post-event attendance attestation, typically by event organizer `key_id`. Polarity carries organizer's confidence (e.g., turnstile-counted vs. honor-system). | signed |

### 3.3.9 `partner` — Operational-data subject_kinds — `organization` / `org_membership` / `partner_record`

Cross-region **operational Portal data** — organizations, memberships, licenses/partners — becomes signed CEG envelopes replicated by the same anti-entropy carrier as trust data. This is the **one scheduled additive item** on the frozen surface (README freeze declaration). It serves justice and fidelity together: a partner's license and an operator's role are enforceable federation-wide, while everyone's private business detail stays home.

**Governing principle (normative): federate the trust/authz-minimal projection; everything else stays region-local.** The federated envelope carries only what the federation needs to enforce trust and authorization cross-region. PII and business detail live in the Registry's own per-region store (today's Portal tables), are NEVER emitted into an operational envelope, and never federate. **Projection minimization is the Registry's emit-side discipline — the Registry is the security-boundary steward**; the substrate's role is admission + merge, and it is explicitly NOT a PII filter (it stores what is signed and emitted).

All three ride existing `scores` + subject_kind discriminator. **Replication wire tokens (normative, snake_case): `organization` · `org_membership` · `partner_record`** — the Edge v2 `EnvelopeKind` additions; v2 `envelope_hash` basis = `sha256(JCS(inner envelope))` per [CC 2.6.1](part_2_the_grammar.md)/[CC 2.6.1.1.1](part_2_the_grammar.md). All three are **Commons tier** ([CC 4.4.3.2.1](part_4_composition_governance.md)) — plaintext at rest; the projection is world-readable by design.

```
organization {
 org_id: uuid // FIRST-CLASS: substrate MUST index as a row column (stable-id resolution below)
 name: string
 org_type: OrgType // internal | partner | licensee | community (the proto enum)
 parent_org_id: Option<uuid> // licensee under partner
 partner_id: Option<uuid> // link to partner_record
 status: active | suspended | deactivated
 asserted_at: rfc3339_canonical // per CC 2.6.2; LWW ordering field
 valid_until: Option<rfc3339_canonical>
}
// REGION-LOCAL (never federates): tax_id, billing/technical/compliance/primary emails,
// oauth_provider/oauth_domain, metadata, created_by.

org_membership {
 user_id: uuid // FIRST-CLASS (with org_id): substrate MUST index (user_id, org_id)
 org_id: uuid
 role: OrgAdmin | KeyManager | Operator | Viewer
 status: active | deactivated
 asserted_at: rfc3339_canonical
 valid_until: Option<rfc3339_canonical>
}
// REGION-LOCAL (never federates): the entire User PII record — email, name,
// oauth_provider/oauth_subject, last_login_at, mfa_enabled/mfa_method, invited_by.
// Consequence: role-based authz works federation-wide; email→user login resolution
// is home-region-local.

partner_record {
 license_id: uuid // FIRST-CLASS: substrate MUST index as a row column
 partner_id: uuid
 org_id: uuid
 license_type: LicenseType // community | community_plus | professional_* | professional_full
 capabilities_granted: [string] // SET-SEMANTICS → lexicographically sorted (CC 2.6.1.1.1 rule 1)
 capabilities_denied: [string] // SET-SEMANTICS → sorted
 max_autonomy_tier: A0..A4
 requires_supervisor: bool
 geographic_restrictions: [string] // ISO country codes; SET-SEMANTICS → sorted
 allowed_identity_templates: [string] // SET-SEMANTICS → sorted
 deployment_limit: u32
 offline_grace_hours: u32
 status: active | suspended | revoked
 revision: u64 // MONOTONIC per license_id — admission REJECTS any decrease
 // (the F-AV-ROLLBACK discipline; the merge orders on this,
 // so a stale `active` can never overwrite a revoke)
 issued_at: rfc3339_canonical
 expires_at: rfc3339_canonical
 asserted_at: rfc3339_canonical
}
// No PII split — the partner_record IS the world-verifiable grant; it federates whole.
```

**Set-semantics declaration (normative — the Verify catch).** `capabilities_granted[]` / `capabilities_denied[]` / `geographic_restrictions[]` / `allowed_identity_templates[]` are **set-semantics → lexicographically sorted by JCS string form ([CC 2.6.1.1.1](part_2_the_grammar.md) rule 1)** — and this is *more* than a single-signer determinism rule here: `partner_record` is signed by **M distinct stewards**, and the M-of-N quorum verifies only if all M sign **byte-identical** JCS canonical bytes. Unsorted capability arrays make two stewards who agree on the same grant produce different bytes — the quorum silently collapses and the license fails to admit cross-region. The vector set MUST include the M-of-N identical-bytes round-trip (M independent canonicalize+sign of one grant → one verifiable signature set). Any unordered list inside a constraints object carries the same declaration.

**No payment-processor data (normative — fail-secure).** An operational envelope MUST NOT carry Stripe-derived or any payment-processor-derived data (customer ids, subscription ids, charge refs, card metadata) — **including via any open-vocabulary field**. Substrate admission MUST reject an operational envelope carrying recognizable payment-processor identifiers (defense-in-depth; the Registry's emit-side minimization is the primary control). Billing remains entirely Portal+Stripe, off-wire ([CLAUDE.md](../../CLAUDE.md) discipline; consistent with [CC 3.3.10](#56812-settlement--cegvalue-transfer-linkage-ceg-014-addition) keeping value-transfer rails off-wire).

**Write authority — two shapes, two verifiers (normative).**
- `organization` / `org_membership`: **single authorized signer, role-gated** — the envelope is admitted iff `attesting_key_id` holds the required role for the operation, established by a prior non-superseded `org_membership` (rooted at org creation by a steward/system authority). Verification reuses the **[CC 4.4.3.4.3.1](part_4_composition_governance.md) `delegates_to` role-chain resolver** — explicitly NOT founder-quorum; implementers MUST NOT build a third bespoke path.
- `partner_record`: **M-of-N steward quorum** — the signature *set* over the identical JCS bytes is verified at admission by the **[CC 3.2](#56810-community-subject_kind-ceg-08-addition) founder-quorum machinery**. Professional capability grants are federation-wide; a single compromised key MUST NOT be able to forge one.
- **The two quorums are distinct (normative — do not conflate):** (1) the **steward-signature admission quorum** above (signer authority, verified by Verify at admit) and (2) the **region merge quorum** (`quorum_weight`, the substrate `MergeBallot` tier-1 ordering during cross-region merge — [CC 5.3.2.3](part_5_transport_substrate.md)). Different mechanisms, different layers, different stewards; the substrate's merge logic never counts steward signatures.

**Mutability + current-state resolution (normative — stable-id grouping, NOT chain-walk).** Updates ride `supersedes`; deactivation/revocation rides `withdraws` (the [CC 3.3.8](#5685-event-lifecycle-dimension-families-ceg-04-addition) `event_listing` state-machine pattern). **Current state of a business id is resolved by stable-id grouping**: group all envelopes by the first-class business id (`org_id` / `(user_id, org_id)` / `license_id`) → apply `withdraws` forward-only → latest `asserted_at` → tie-break smallest `attestation_id` (the [CC 3.5.1](part_3_the_namespace.md) discipline). For `partner_record`, admission anti-rollback on `revision` precedes the [CC 5.3.2.3](part_5_transport_substrate.md) quorum merge. Resolution MUST NOT require chain completeness — a region that never observed envelope N−1 still converges (partition tolerance is the point of CEG-native replication). `supersedes` references SHOULD be emitted when the prior is known and serve as **audit lineage only** — decoration, never resolution.

**1+4 preserved** — rides `scores` + subject_kind discriminator ([CC 3.3](#568-content-ingestion-prefixes) mechanism); license authority rides the existing CC 3.2 founder-quorum machinery; role authority rides the existing CC 4.4.3.4.3.1 delegation resolver; merge intents are substrate dispatch declarations ([CC 5.3.2.3](part_5_transport_substrate.md)), not wire primitives. Sixteenth path ([CC 1.7](part_1_foundation.md)) — the wire format expresses **the federation's own operational/administrative layer** (the org/identity/license records that run the federation's business) as composition: after this, no cross-region byte moves outside a signed CEG envelope.

### 3.3.10 `settlement` — CEG↔value-transfer linkage (CEG 0.14 addition)

Value transfer itself is **not** a CEG primitive — it rides external rails (USDC on Base via x402, keyed to the federation signing key under the **Identity = Wallet** principle). The `settlement` primitive is the **optional, privacy-scoped attestation that *links* a federation action to its off-stack settlement** — so a paid relationship (paid stream / tip / subscription / paid `event_listing` / compute-job) can be federation-auditable *or* privately recorded, producer's choice. **CEG records that a settlement happened and binds it to what it paid for; the chain settles the value.** Clean separation of concerns, with autonomy as the default: privacy first, auditability opt-in.

**Why this is in CEG's lane (and why it's optional):** the linkage is a *trust fact* ("is this a real / authorized / paid relationship?"), exactly what consumer policy composes over. The 2026 agent-commerce + on-chain-privacy markets converged on the same mechanism — *a verifiable receipt exists, with selectively-disclosed contents* (x402 optional receipt header; append-only verifiable metering logs; "privacy + compliance via selective disclosure"). CEG already has every needed primitive, so this is composition, not invention.

**Two admitted shapes (parallel to `consent_record` [CC 3.3.5](#5687-consent_record-subject_kind-ceg-06-addition)):**
- **Primitive:** a bare `scores` on a `settlement:*` dimension against the paid Contribution (the common case).
- **Ceremony:** the `settlement` subject_kind envelope when an explicit receipt record is wanted.

```
settlement {
 settled_action_ref: contribution_id // the federation action this paid for
 // (or via subject_key_ids / topical_relation:settles)
 rail: string // open vocab; e.g. "base:usdc", "stellar:usdc", "x402"
 settlement_ref: string // chain tx hash / x402 receipt id — cited the way
 // evidence_refs[] cite a SHA blob (CC 5.3.2): a settlement
 // is just another evidence reference
 amount_commitment: Option<string> // cleartext "12.50" (public case) OR a hash/range
 // commitment (private/selective-disclosure case)
 settled_at: rfc3339_canonical
 // visibility via the envelope cohort_scope: default `self` (payer+payee only);
 // `public` opt-in for transparency (e.g. creator revenue, DAO treasury flows)
}
```

**Self-authenticating (Identity = Wallet):** the same federation key that signs this attestation controls the Base wallet that emitted `settlement_ref`, so "I settled `tx` for action X" is self-proving — no oracle needed. The payee MAY counter-attest (`scores` on `settlement:received:*`) for a bilateral receipt.

**Privacy is the default, auditability is opt-in.** Visibility rides the existing gradient: `cohort_scope: self` (the parties only; the CC 5.2 structural-invisibility discipline applies — no `holds_bytes` leak) by default; `cohort_scope: public` opt-in; amounts MAY be committed rather than cleartext; viewing-key / ZK selective disclosure composes later without a wire change. This matches "configurable-privacy-by-default" — the federation log is **not** a public payment trail unless the producer chooses it.

**Lifecycle**: `withdraws` against a `settlement` is forward-only (it does not un-happen the on-chain settlement — leaving doesn't un-pay, parallel to `location_proof`); a *disputed* or *refunded* settlement is a new `settlement` / `scores` referencing the original via `supersedes` or `topical_relation`. CEG never reverses value — it only records the subsequent state.

**1+4 preserved** — rides `scores` + subject_kind discriminator ([CC 3.3](#568-content-ingestion-prefixes) mechanism); `settlement_ref` rides the existing `evidence_refs[]` external-reference pattern; visibility rides existing `cohort_scope`. Fourteenth path ([CC 1.7](part_1_foundation.md)) — the wire format expresses **commerce-relationship auditability** (the receipt, not the rail) as composition, closing the last form of internet traffic from the completeness audit.

### 3.3.11 `inter-content` — Inter-content + relation prefixes

| Prefix | Description | Polarity |
|---|---|---|
| `news:*` | News-content claims; publisher-attested + time-decaying + fact-checker composition. | signed |
| `encyclopedia:*` | Encyclopedia-content claims; editor-consensus + revision chain. | signed |
| `chat:*` | Chat-content claims (quality / participant-trust / context). | signed |
| `blog:*` | Blog-content claims (author-credibility / topic-domain). | signed |
| `topical_relation:{kind}` | **Open vocabulary** inter-content relationship edges. Canonical kinds: `references`, `corrects`, `supersedes_article` (distinct from the structural primitive `supersedes`), `see_also`, `disambiguates`, `translation_of`, `replies_to`, `comments_on`, `cites_source`, `rsvps`, `vod_of`. New `{kind}` values are documentation-only registry entries (no CC 4.5.1 amendment needed). | enumerated |

**Composition note — threads, replies, comment trees**: NodeCore's `chat_message` + `topical_relation:replies_to` compose into arbitrary thread graphs (Twitter threads, Reddit comment trees, Discord conversations, IRC channels). No new structural primitive is needed; thread traversal is consumer-side composition over the existing edge set. Same shape for blog-post comment threads via `topical_relation:comments_on` + nested `replies_to`. The CC 1.13+4 lockdown holds.

### 3.3.12 `namespace-multimedia` — Multimedia dimension families

All four families are **open vocabulary** per [CC 4.5.1.1](part_4_composition_governance.md) axis-vocabulary discipline; canonical kinds named here, additions via documentation-only registry entries.

| Prefix | Description | Polarity |
|---|---|---|
| `content_rating:{scheme}:{rating}` | Multi-scheme content rating. `{scheme}` ∈ `mpaa` (G/PG/PG-13/R/NC-17), `bbfc` (U/PG/12/15/18), `pegi` (3/7/12/16/18), `esrb` (E/E10+/T/M/AO), `ifco`, `csm` (Common Sense Media), or `operator:{operator_id}` for operator-defined rubrics. Polarity carries certifier confidence; not a slashing input. | signed |
| `content_class:{class}` | Mechanism-descriptive content classification. `{class}` open vocabulary; canonical: `film`, `short_film`, `documentary`, `art_piece`, `theatre`, `performance`, `news`, `educational`, `entertainment`, `vlog`, `adult`, `generated`. Distinct from `cw_class:*` (community declarations) — `content_class` is producer-declared production-class; `cw_class` is community-applied content-warning. | enumerated |
| `cw_class:{class}` | Community CW (content-warning) declarations. `{class}` open vocabulary; canonical: `art_cinema`, `horror`, `political`, `erotic`, `violence`, `medical`, `nsfw_text`. Cohort-attestable per [CC 4.4.1](part_4_composition_governance.md) Frickerian discipline (low-density cohort CWs not downweighted). | enumerated |
| `age_assurance:{level}` | Age-assurance attestation. `{level}` ∈ `self` (self-declared age, lowest confidence), `provider:{verifier_key}:adult` (third-party verifier attests adult), `government:{credential_class}:adult` (government-credential-backed adult attestation, highest confidence). NEVER fires `slashing:*` on misdeclaration alone — `moderation:age_assurance_misdeclaration` is the adjudication path. | enumerated |

Media-type prefix families per `external_content` sub_kind:

| Prefix | Description | Polarity |
|---|---|---|
| `image:*` | Image-content claims (per `external_content:image` sub_kind). | signed |
| `audio:*` | Audio-content claims (per `external_content:audio` sub_kind). | signed |
| `video:*` | Video-content claims (per `external_content:video` sub_kind). | signed |
| `film:*` | Film-content claims (per `external_content:film` sub_kind). Distinguished from `video:*` by distributor attestation chain. | signed |
| `model_3d:*` | 3D-content claims (per `external_content:model_3d` sub_kind). | signed |

### 3.3.13 `external_content` — external_content sub_kinds

Foundational sub_kinds:

| sub_kind | Use |
|---|---|
| `encyclopedia_article` | Wikipedia-shape; editor-consensus + revision chain via `supersedes`; indefinite `valid_until` |
| `news_article` | Publisher-attested; time-decaying; corrections via `recants` + `topical_relation:corrects` |
| `accord_data` | Multi-sig signed (HumanityAccord / StewardTriple / WaQuorum / OneOfSix) per [CC 4.2.1](part_4_composition_governance.md) |
| `local_data` | User-private; always `cohort_scope: self`; promotable via [CC 4.4.3.3.1](part_4_composition_governance.md) |
| `chat_message` | Conversational message imported from Discord / Slack / Twitter / iMessage / SMS / XMPP / IRC / Matrix / (or custom). Reply chains form via `topical_relation:replies_to:{target_message_entity_key_id}` (no new primitive). Default cohort_scope tighter than articles (`self` / `family` / `community` / `affiliations`). `valid_until` typically set; consumer policy SHOULD downweight chat in cross-cohort aggregation given privacy sensitivity. **This is the slot Twitter / Mastodon / Bluesky microblog content rides** — no separate microblog sub_kind needed. |
| `blog_post` | Single-author commentary imported from Medium / Substack / WordPress / Ghost / Tumblr / personal blogs. Distinct from `news_article` (no publisher editorial), from `encyclopedia_article` (no peer-consensus), from `chat_message` (long-form). Comments on blog posts are separate Contributions (typically `chat_message`) citing the post via `topical_relation:comments_on`. |

Multimedia sub_kinds:

| sub_kind | Use |
|---|---|
| `image` | Photo, illustration, screenshot, infographic, meme. Source struct carries dimensions, format, AI-generation disclosure (EU AI Act Art. 50), mandatory `alt_text` accessibility metadata, license info. |
| `audio` | Music, podcast, lecture, audiobook, generated audio. Source struct carries codec, duration, sample rate, optional `transcript`, AI-generation disclosure, license info. |
| `video` | General video — vlog, social, screen recording, tutorial. Source struct carries codec, duration, resolution, mandatory `captions` reference, AI-generation disclosure, license info. |
| `film` | Cinematic / art-bearing video; distinguishable from `video` by `content_class` + distributor attestation chain. Same Source struct as `video` + festival / distribution metadata. |
| `model_3d` | Three-dimensional content — `gltf`, `usdz`, `fbx`, `gaussian_splat`, `NeRF`. Source struct carries vertex/triangle counts, bounding-box, mandatory `description` accessibility metadata, license info. |
| `live_stream` (Phase 2) | Real-time streaming surface. Deferred to Phase 2 per MEDIA_SHARING.md. Substrate-side decisions still pending (Edge parallel-transport envelope; Persist `federation_streams` shape) per Gap 2. CEG codifies the slot when NodeCore ships. |

Time-bound state-bearing sub_kinds:

| sub_kind | Use |
|---|---|
| `event_listing` | Time-bound state-bearing content — Eventbrite / Meetup / Lu.ma / calendar invites / RSVPs / ticketing. Source struct carries `platform`, `event_id`, `title`, `starts_at` / `ends_at`, `venue` (Physical / Virtual / Hybrid per NodeCore `EventVenue` enum), `capacity`, `ticket_grant_policy` (Open / ApprovalRequired / InvitationOnly / Paid). **Lifecycle composes from existing structural primitives** — no new wire shape: RSVPs ride `scores` from attendee `key_id` on the event's `entity_key_id`; cancellation rides `withdraws` against the event Contribution; reschedule rides `supersedes` with `differs_in: ["start_time", "venue"]`; ticket transfer rides `delegates_to` against the ticket-grant Contribution. State-transition signal rides the `event:lifecycle:{state}` dimension family ([CC 3.3.8](#5685-event-lifecycle-dimension-families-ceg-04-addition)). |

Each Source struct conforms to a sub_kind-specific schema documented at CIRISNodeCore FSD/MEDIA_SHARING.md §4 (multimedia) or SCHEMA.md §4 (chat / blog / event_listing); CEG documents the slot, NodeCore documents the per-sub_kind field shapes.

### 3.3.14 `identity-claiming` — `identity:canonical_binding` — claiming a canonical-hash subject

A `subject_key_ids[]` entry MAY be a **canonical-hash** identifier — `sha256("discord:user_id:12345")`, an external-party id — rather than a `federation_keys` row ([CC 2.3.2](part_2_the_grammar.md)). When the real-world subject behind a canonical hash **later acquires a federation_keys identity**, it needs a wire-format way to **claim** that hash so its revocation authority (and proxy-delegation eligibility) attaches. That is the rebinding ceremony — autonomy reaching back to data that named you before you had a key.

**Shape.** A bare `scores` Contribution on the reserved dimension **`identity:canonical_binding:{canonical_hash}`** — `attesting_key_id = K` (the claiming federation key), naming the canonical hash `H` as the bound subject. **Self-asserted** (`witness_relation: self`): K declares "I am the federation identity behind H." Hybrid-signed; admitted federation-tier (it grants authority — not local-tier-eligible, [CC 5.3.2.2](part_5_transport_substrate.md) discipline).

```
scores {
 attesting_key_id: K, // the claiming federation_keys identity
 dimension: "identity:canonical_binding:{H}", // H = the canonical hash being claimed
 score: <positive>,
 witness_relation: self,
 asserted_at: rfc3339_canonical,
}
```

**Admission consequence (normative).** After an admitted `identity:canonical_binding` from `K` → `H`, the substrate widens `withdraws` admission ([CC 2.4.1.1](part_2_the_grammar.md)): a `withdraws` from `K` against any target `T` where `H ∈ T.subject_key_ids[]` is now admitted (K has inherited the canonical-hash subject's revocation authority). **This is what unblocks [CC 2.4.1.1 rule 3](part_2_the_grammar.md)** — a proxy `delegates_to` to a canonical-hash subject presumes that subject can hold a `delegates_to.attested_key_id`; a never-rebound canonical subject acquires it here.

**Authorization is consumer-policy, not wire (normative honesty).** CEG pins the binding *shape*, NOT proof that K legitimately controls H's preimage. A binding is a *self-assertion*; a consumer weights it by whatever proof-of-control it trusts (OAuth/IdP verification of the `discord:user_id`, an out-of-band attestation, TOFU). The substrate admits the binding and records it; **the trust that K==H is composed by the consumer**, exactly as the [CC 3.3.6.2](#5688-1-transport_destination--the-authenticated-identityaddress-binding-ceg-012-addition) announce is advisory until rooted. A second key claiming the same `H` is admitted too (competing claims surface to consumer policy / RATCHET, not a substrate verdict). **1+4 preserved** — `identity:canonical_binding:{H}` is a reserved `scores` dimension, not a new primitive.

## 3.4 `reservation` — Reserved-prefix enforcement

Most of the namespace is open-vocabulary — anyone may emit, and trust is composed downstream. A small number of prefixes are reserved: only specific identity types may emit them. This is integrity made structural — the few claims that would be catastrophic to forge (substrate health, capacity scores, the constitutional `accord:*`) are gated at the source. **Enforcement is normative at the substrate verify-pipeline AND at every CEG-Conforming Consumer per [CC 2.2](part_2_the_grammar.md)**.

### 3.4.1 `accord-reservation` — The `accord:*` reservation

`accord:*` is reserved: only `federation_keys` rows with `identity_type="accord_holder"` may emit. This is the one constitutional asymmetry in the federation — see [CC 4.2](part_4_composition_governance.md) HUMANITY_ACCORD.

Reserved leaves:

| Prefix | Polarity | Emitter rule |
|---|---|---|
| `accord:invoke:CONSTITUTIONAL:{halt_id}` | +1.0 only | 2-of-3 accord-holder multi-sig per [CC 4.2.1](part_4_composition_governance.md) |
| `accord:invoke:notify:{notify_id}` | +1.0 only | 2-of-3 accord-holder multi-sig per [CC 4.2.1](part_4_composition_governance.md); UI MUST distinguish from CONSTITUTIONAL |
| `accord:invoke:drill:{drill_id}` | +1.0 only | 2-of-3 accord-holder multi-sig per [CC 4.2.1](part_4_composition_governance.md) |
| `accord:lifecycle:active` | +1.0 only | accord-holder self-attestation; `valid_until` MUST refresh on a cadence ≤ 90 days |

### 3.4.2 `community-location` — Community + location-event reservations (CEG 0.8 addition)

Per [CC 3.2](part_3_the_namespace.md) `community` + [CC 3.3.3](part_3_the_namespace.md) `location_proof` subject_kinds. Four substrate-emitted prefixes:

| Prefix | Emitted on | Emitter rule |
|---|---|---|
| `hard_case:community_membership_change:{community_key_id}` | Substrate admits an addition or removal in the named community's roster (per the community's `consensus_protocol`; for `cohort_subkind: geographic` admission additionally requires valid `location_proof`) | `attesting_key_id` MUST match `federation_keys` row with `identity_type="substrate_persist"` |
| `hard_case:community_consensus_protocol_change:{community_key_id}` | Substrate admits a `consensus_protocol` amendment on a non-entrenched community | Same: substrate_persist |
| `hard_case:community_consensus_protocol_violation:{community_key_id}` | Substrate REJECTS a proposed community amendment (rule unsatisfied OR entrenched) | Same: substrate_persist |
| `hard_case:location_proof_resolution_violation` | Substrate REJECTS a `location_proof` Contribution with `cell_resolution > 7` per [CC 2.6.6.1](part_2_the_grammar.md) rough-only enforcement; emitted against the producer's `key_id` so operators can observe malformed-client patterns | Same: substrate_persist |

Composes with [CC 3.4.3](#72-substrate-self-report-reservations-system) + [CC 3.4.4](#77-selffamily-membership-event-reservations-ceg-07-addition) — part of the same substrate-self-report discipline. Non-substrate emissions on these prefixes are a category error and MUST be rejected.

### 3.4.3 `system` — Substrate-self-report reservations (`system:*`)

[CC 3.1.3](part_3_the_namespace.md) CIRISPersist `system:*` and [CC 3.1.4](part_3_the_namespace.md) CIRISEdge `system:*` are reserved to the substrate component itself. Emitter rule: the `attesting_key_id` MUST match a `federation_keys` row with `identity_type="substrate_persist"` or `identity_type="substrate_edge"` respectively, cross-attested by all stewards in the steward-triple. Non-substrate emissions on these prefixes are a category error and MUST be rejected.

### 3.4.4 `family-self` — Self/family membership-event reservations (CEG 0.7 addition)

Per [CC 3.3.6](part_3_the_namespace.md) `identity_occurrence` + [CC 3.3.4](part_3_the_namespace.md) `family` subject_kinds. The substrate-emitted membership-event prefixes:

| Prefix | Emitted on | Emitter rule |
|---|---|---|
| `hard_case:identity_occurrence_added:{identity_key_id}` | Substrate admits a new `identity_occurrence` Contribution for `identity_key_id` | `attesting_key_id` MUST match a `federation_keys` row with `identity_type="substrate_persist"` |
| `hard_case:family_membership_change:{family_key_id}` | Substrate admits an addition or removal in the named family's roster (per the family's `consensus_protocol`) | Same: substrate_persist |
| `hard_case:family_consensus_protocol_change:{family_key_id}` | Substrate admits a `consensus_protocol` amendment on a non-entrenched family | Same: substrate_persist |
| `hard_case:family_consensus_protocol_violation:{family_key_id}` | Substrate REJECTS a proposed amendment (rule unsatisfied OR entrenched) | Same: substrate_persist |
| `hard_case:recipient_excluded:{scope_key_id}` | Substrate fail-secure-skips a recipient in the [CC 5.2](part_5_transport_substrate.md) at-rest grant cascade. Payload: excluded recipient `key_id`, `reason ∈ {expired_occurrence, invalid_kem_key, missing_encryption_pubkeys}`, skipped Contribution's envelope ref. **Cohort-scoped: emitted INTO the affected self/family scope; MUST NOT federate beyond it** — the excluded member can audit; the federation learns nothing (CC 5.2 invisibility preserved). | Same: substrate_persist |

**Removal-path emission shape.** The membership-change prefix covers **both add and removal** — there is **no separate `hard_case:member_removed` kind** (it would split one event class across two prefixes for no gain). On the **removal** path the substrate emits the *same* `hard_case:family_membership_change:{family_key_id}` (and the CC 3.4.2 `community_membership_change` analog), with the payload distinguishing the direction and carrying what the forward-secrecy + audit consumers need:

```
hard_case:family_membership_change:{family_key_id} (payload)
 change_kind: "added" | "removed" // the direction (pins the removal signal)
 subject_key_id: key_id // the member added/removed
 cohort_key_id: key_id // the family (or community) key
 effective_at: rfc3339_canonical // the membership-change instant; on removal this is
 // the re-key epoch boundary (CC 4.4.3.4.5 / CC 4.4.3.2.2
 // Option-A) after which the removed member receives
 // no new wrapped content
```

So the removal-time substrate signal (the thing persist's `put_family_membership_revocation` path emits) is `change_kind: "removed"` on the existing prefix — consumers and the forward-secrecy re-key key on `effective_at`. Same shape for `community_membership_change` (CC 3.4.2) and the `identity_occurrence` removal (a `withdraws` against the occurrence; the substrate emits `family_membership_change` / `community_membership_change` where the occurrence was a member).

Composes with [CC 3.4.3](#72-substrate-self-report-reservations-system) — these are part of the same substrate-self-report discipline. Non-substrate emissions on these prefixes are a category error and MUST be rejected.

### 3.4.5 `capacity-score` — Capacity-Score self-emission rejection

`capacity:*` ([CC 3.1.8.1](part_3_the_namespace.md)) rejects self-emission: `attesting_key_id` MUST NOT equal `attested_key_id`. The agent's own capacity score is never fed back into the agent's own context — anti-Goodhart per CIRISAgent CC 3.1.2.

### 3.4.6 `reservation-delivery` — Delivery-receipt reservation (CEG 0.10 addition)

Per [CC 5.3.3.6](part_5_transport_substrate.md) delivery receipts (V3 lock). One reserved prefix for subscriber-emitted delivery acknowledgements:

| Prefix | Description | Emitter rule |
|---|---|---|
| `delivery_receipt:{stream_id}` | Subscriber's signed acknowledgement that they received chunk K under the named stream + epoch. Best-effort default; opt-in for accountable streams. Validated-not-adjudicated per [CC 1.7](part_1_foundation.md) MISSION fail-honest invariant — substrate / Verify authenticate origin + JOIN against published STH root per [CC 5.3.3.6](part_5_transport_substrate.md), but do not compose "delivered"/"owes N" verdicts (consumer policy). | `attesting_key_id` MUST be a current member of the community/stream the `{stream_id}` belongs to, per [CC 4.4.3.2](part_4_composition_governance.md) Policy M membership resolution. NOT substrate-self-report (distinct from CC 3.4.3 / CC 3.4.4 / CC 3.4.2 substrate emissions). |

**Composition with [CC 3.4.7.1](#70-the-enforcement-rule-normative) identity_type-as-set**: a subscriber who is also a witness MAY emit delivery_receipt under the subscriber role; the role-set must contain a subscriber-eligible role (per the community's admission semantics from [CC 4.4.3.2](part_4_composition_governance.md) Policy M).

### 3.4.7 `enforcement` — The enforcement rule (normative)

A CEG-Conforming Substrate (CCS) MUST reject any incoming `scores` attestation whose `dimension` matches a reserved-prefix pattern below AND whose `attesting_key_id` does not satisfy the prefix's emitter rule. Rejection is at admission to `federation_attestations`; rejected rows are not stored.

A CEG-Conforming Consumer (CCC) MUST independently re-check the reserved-prefix rule on every received attestation regardless of whether it was previously admitted by another peer's substrate. Trust does not propagate: the substrate's admission check is the FIRST line of defense; the consumer's re-check is the second. Both checks MUST agree.

A CEG-Conforming Producer (CCP) MUST NOT emit an attestation under a reserved prefix unless its `attesting_key_id` satisfies the emitter rule. Violation is a producer-side conformance violation regardless of whether any downstream substrate accepts the violation.

#### 3.4.7.1 `identity-set` — `identity_type` is a set — single-key role cohabitation (CEG 0.9 addition)

Per [CC 4.5.8](part_4_composition_governance.md). **`federation_keys.identity_type` is a SET of roles, not a single scalar role.** A single federation key MAY simultaneously hold multiple identity types — e.g., a folded CIRISAgent occurrence whose key is BOTH `agent` AND `lenscore_detector`, or a steward key that is both `substrate_persist` and `witness`.

Every emitter rule in this section — and the [CC 4.2.3](part_4_composition_governance.md) `accord_holder` material — is therefore evaluated by **set membership**, not scalar equality:

> Wherever a CC 3.4 emitter rule reads "`attesting_key_id` MUST match a `federation_keys` row with `identity_type=X`" (or "`identity_type="X"`"), the normative reading is **`X ∈ attesting_key.identity_type`** — the key's role-set MUST CONTAIN `X`. A key satisfies a reserved-prefix gate iff the required role is one of its held roles.

**Backward compatibility (semantic-null for legacy keys).** A scalar `identity_type="X"` is canonically the singleton set `{X}`. For a single-role key the membership test `X ∈ {X}` is identical to the scalar test `X == X`, so every single-role gating decision is unchanged. The field's representation is set-valued (scalar → set) at the `federation_keys` row layer only. Substrate implementations MUST migrate the column to a set/array representation; consumers MUST read a legacy scalar as a one-element set. No envelope field, structural primitive, subject_kind, or [CC 3.1](part_3_the_namespace.md) dimension prefix changes — the 1+4 wire-format lockdown is untouched; this is a [CC 3.4](#7-reserved-prefix-enforcement)-layer enforcement-rule generalization only.

**Canonical-bytes encoding.** Where `identity_type` enters a canonical-bytes computation (e.g., cross-attestation of a `federation_keys` row), the set MUST be encoded as its members sorted ascending by Unicode code point, deduplicated, comma-joined with no whitespace (e.g., `agent,lenscore_detector`). A single-role key encodes identically to its scalar form (`agent` ≡ `{agent}` ≡ `"agent"`), preserving signatures over single-role rows.

**Storage representation is an implementation choice — "set" is semantic, not a column type.** CC 3.4.7.1 requires that `identity_type` be *interpreted* as a set (membership test, not scalar equality) and that its *canonical bytes* be the sorted-deduped-comma-joined string above. It does **NOT** mandate a structured/array **column**. A single free-form `TEXT` column holding the comma-joined form, decoded-to-set on read (persist's v6.5.0 shape), **is conformant** — the comma-joined string *is* the canonical representation, and the set is its interpretation. **No substrate migration to a structured column is required.** New `identity_type` values (e.g. `user`, `wise_authority`) are valid additive members of the open role vocabulary; they need no schema change, only inclusion in the membership-test set.

**Cohabitation does NOT collapse the dimension split.** Role cohabitation grants a key the *right* to emit under each held role's reserved prefixes; it does NOT merge the roles' namespaces. A key holding `{agent, lenscore_detector}` still emits its detector verdicts under `detection:*` (the lenscore-role surface) and its agent-intent attestations under the agent dimensions — the [CC 3.4.8](#74-detector-only-prefixes) shadowing rule and the [CC 3.4.5](#75-capacity-score-self-emission-rejection) self-emission rejection apply unchanged per held role. See [CC 3.4.8](#74-detector-only-prefixes) for the LensCore-fold worked example.

**Co-location is NOT consolidation — the fabric-node discipline.** A *fabric node* (the headless cohabitation runtime that composes registry-authority + lens-observation + node-consensus over one substrate; `agent = fabric node + brain`) routinely holds the **full role-set in one key/process** — `{substrate_persist, steward, lenscore_detector, witness, …}`. This is co-location of **custody**, not consolidation of **authority**, and the separation of powers is held **cryptographically, not procedurally**:

- **Authority stays quorum-bound.** A co-located `steward` role does NOT let a single node issue a federation-scope attestation. Registry-consensus is the [CC 4.4.3.2.4.1(a)](part_4_composition_governance.md) **founder-quorum** over the `ciris-canonical` infrastructure community ([CC 3.2](part_3_the_namespace.md)), evaluated over `{m: m.role == founder}`. A co-located node gains a *vote*, never a *verdict*.
- **Observation stays non-authoritative by namespace.** `lenscore_detector` emissions live under `detection:*` and are **validated, not adjudicated** ([CC 1.7](part_1_foundation.md)) — never sole evidence for an authority action ([CC 3.4.8](#74-detector-only-prefixes) / [CC 1.2 T4](part_1_foundation.md)).
- **Observation can never manufacture authority.** Holding both roles cannot make a `detection:*` emission an authority verdict: the namespaces do not merge (above), and authority is quorum-gated *upstream of any single key*. The hazard the LensCore mission warns of — *the lenses becoming the gate* — is structurally unreachable inside one process.

A fabric node co-locating authority + observation + consensus is conformant **iff** these hold. An implementation that lets a co-located node convert what it *observes* into what it can *authorize* has broken the separation at that point and is **non-conformant** — fix the wiring, never weaken the rule.

#### 3.4.7.2 `consent-counter` — `consent_role` — the Counter-RII consent gate (1.0-RC4, ratifies Accord §RC / CIRISAgent#760 OQ-1/2/3)

`federation_keys.consent_role` is the role enum that gates **Counter-RII** probe detection (RATCHET `FSD/COUNTER_RII_DETECTION.md`; Lean `ConsentGate.lean`, 8 theorems verified — F-CR-3 SelfConscience-zero-by-construction proved). Three primitive-level semantics shape persist's `federation_keys.consent_role` schema and edge's `ProbePatternObserver` gate and so **cannot be set per-consumer** — they are **ratified here**. All three take the `ConsentGate.lean` default — ratification carries **no predicate or proof change**.

**OQ-1 — revocation chain: `BaseRole`-only, non-recursive.** A `consent_role` is non-recursive: a subsequent revocation **overwrites** the prior revocation record (NO recursive revocation chain embedded in the role). Chain history, **if retained**, MUST live in a separate audit surface and **MUST NOT be embedded in the `consent_role` JSONB**. This locks the substrate-portable JSONB shape — flat, bounded, overwrite-on-revoke — consistent with [CC 3.3.8](part_3_the_namespace.md) stable-id grouping (not chain-walk; partition-tolerance) and [CC 4.1.2](part_4_composition_governance.md) (no key pre-declaring its own state recursively), and **non-breaking against the shipped flat soft-delete substrate** (the permissive "if retained" is deliberate — mandating an audit table would contradict a deployed migration).

**OQ-2 — peer eligibility: blanket suppression.** A node holding the `Peer` `consent_role` escapes Counter-RII detection at **any** `trust_mode`. The cost — a sovereign peer may probe other peers without raising the signal — is **bounded by construction**: `ratchet:flag:counter_rii:{layer}` is **advisory only** ([CC 3.1.6](part_3_the_namespace.md)) — it can NEVER be sole evidence for `slashing:*`; the WA quorum is the load-bearing adjudication gate. The exemption suppresses an *advisory signal*, not an *enforcement path*.

**OQ-3 — post-window `AuthorizedReview`: strict.** An `AuthorizedReview` `consent_role` is signal-eligible **immediately** at `t > window_end` — no grace period. Matches the fail-secure / clean-state-machine grain ([CC 8.3.3](part_8_appendices.md)); reviewers MUST respect their windows.

With this, `consent_role` is **no longer a reserved-not-yet-written slot** — implementations MAY now build the `consent_role` substrate. **1+4 untouched** — `consent_role` is a `federation_keys` identity field (sibling to [CC 3.4.7.1](#701-identity_type-is-a-set--single-key-role-cohabitation-ceg-09-addition) `identity_type`), not an envelope primitive.

### 3.4.8 `detector-only` — Detector-only prefixes

`detection:correlated_action:*` and `detection:distributive:access:*` are LensCore-only emission. Emitter rule: `lenscore_detector ∈ attesting_key.identity_type`. Cross-attestation by non-LensCore peers (on the same dimension, attesting to the same subject) is admitted as a score on the detector's verdict — useful when the federation wants to cross-check — but those scores MUST use a different `dimension` prefix (e.g., `truth_grounding:detection:correlated_action:{axis}`) to avoid shadowing the detector's own emission.

**LensCore-fold worked example.** When `ciris-lens-core` is folded into the CIRISAgent workspace, a single folded occurrence's federation key holds `identity_type ⊇ {agent, lenscore_detector}`. The CC 3.4.8 gate is satisfied for that key's `detection:*` emissions by `lenscore_detector ∈ {agent, lenscore_detector}` — the cohabiting `agent` role neither grants nor blocks the detector right; only the held `lenscore_detector` role does. The split is preserved by the dimension namespace, not by the key: the same key emits its **agent-intent** attestations under the agent dimensions and its **detector verdicts** under `detection:*`; a downstream consumer cross-checking the detector still emits under the distinct `truth_grounding:detection:*` prefix above, shadowing-free. The [CC 3.4.5](#75-capacity-score-self-emission-rejection) self-emission rejection continues to bind per held role — a folded `agent`+`lenscore_detector` key still MUST NOT emit a `capacity:*` score about itself.

### 3.4.9 `co-stewarded` — Co-stewarded prefixes

`licensure:{authority_id}` is co-stewarded between CIRISRegistry [CC 3.1.1](part_3_the_namespace.md) and CIRISVerify [CC 3.1.2](part_3_the_namespace.md) — both MAY emit; consumers compose. **Single-source attestations** (only one of the two co-stewards has emitted) MUST be marked as `confidence ≤ 0.5` in consumer composition until the second co-steward's attestation arrives.

### 3.4.10 `witness-emitter` — Witness-emitter reservations

`transparency_log:cosigned:*` is reserved: emitter rule is `attesting_key_id` MUST match a `federation_keys` row with `identity_type="witness"` (target schema; see [CC 5.3.1](part_5_transport_substrate.md) for the interim using a `registry_witnesses` table).

### 3.4.11 `age-assurance` — Age-assurance: the witness-reserved ladder, the subject self-declared rung, and the protective gate

Age-assurance is **two** dimension families, not one. The split is load-bearing: a provider/government attestation is a witness verdict and is **witness-reserved**; a subject's self-declaration is **not** an attestation about anyone but itself and rides a **distinct, non-reserved** prefix. A consumer unions both at read time, the witness rung outranks the self rung, and the gate's default is protective.

**The two prefixes (normative emitter rules).**

- **`age_assurance:`** — witness-RESERVED. Emitter rule: `witness ∈ attesting_key.identity_type` ([CC 3.4.7.1](#701-identity_type-is-a-set--single-key-role-cohabitation-ceg-09-addition) set membership). This is the provider/government rung — a registered age-assurance verifier (`identity_type ⊇ {witness}`) attests a subject's band. A subject MUST NOT emit on `age_assurance:`; per the [CC 3.4](#34-reservation--reserved-prefix-enforcement) three-actor rule a CCS MUST reject a non-witness emitter at admission, a CCC MUST re-check, and a CCP MUST NOT emit. A subject therefore cannot self-mint a `provider`/`government` adulthood. Sibling of [CC 3.4.10](#3410-witness-emitter--witness-emitter-reservations).
- **`age_self_declared:`** — NON-reserved, subject-signed. The onboarding "state your age range" rung. Admitted iff the signer acts for the subject (the subject's own occurrence or an admitted occurrence of it). A self-declaration carries **only** the `{band}` — never a `{level}` token — because its level is `self` by construction.

**The band and the ladder.** `AgeBand ∈ { minor, adult }` (ordered by protection: `minor` is gated out of adult content, `adult` is not). The assurance `AssuranceLevel` ladder is ascending confidence:

```
age dimension construction (the CC 4.1.3 :vN version-segment gate is mandatory):

  self-declared rung (subject-signed, NON-reserved):
    age_self_declared:{band}:v1
      band ∈ { minor, adult }
      e.g. age_self_declared:adult:v1

  provider / government rung (witness-RESERVED):
    age_assurance:{level}:{band}:v1
      level ∈ { provider, government }
      band  ∈ { minor, adult }
      e.g. age_assurance:provider:adult:v1

assurance ladder (ascending confidence):
    self  <  provider  <  government

misdeclaration adjudication dimension:
    moderation:age_assurance_misdeclaration
```

The `self` rung of the ladder materializes on the non-reserved `age_self_declared:` prefix; the `provider`/`government` rungs materialize on the witness-reserved `age_assurance:` prefix carrying the `{level}` token. Parsers MUST tolerate the trailing `:vN` version segment. This refines the [CC 3.3.12](#3312-namespace-multimedia--multimedia-dimension-families) `age_assurance:{level}` enumerated entry (provider/government rungs MAY further qualify `{level}` with a `{verifier_key}` / `{credential_class}` per that entry).

**Read-union — witness outranks subject (normative).** A consumer resolving an identity's age-assurance MUST union both prefixes and take the **highest** level on record. A witness-emitted `age_assurance:*` (provider/government) **OUTRANKS** a subject `age_self_declared:*`. Absence of any row resolves to **None**, which MUST be treated protectively — see the gate.

**The protective gate (normative).** A viewer below `adult` assurance is **BLOCKED** from `adult` `content_class` ([CC 3.3.12](#3312-namespace-multimedia--multimedia-dimension-families)). The default is protective, not permissive:

- `general`-class content is visible to everyone (protective ≠ prudish).
- `adult`-class content is visible ONLY to a viewer whose band is `adult`.
- A `minor` band, a "declined to state", and an "unknown"/absent assurance ALL resolve to the protective `minor` default and are BLOCKED.

The gate decides visibility only; it MUST NOT fire `slashing:*` on a mismatch.

**`self` is unfalsifiable — sensitive spaces require a verified level (normative).** The `self` rung is unfalsifiable from inside the fabric. A sensitive space MUST require a **verified** level (`provider`/`government`); bare `self` does NOT satisfy it. A consumer enforcing this checks the resolved level separately from the band — an `adult` band at `self` level satisfies the band but NOT a verified-level requirement.

**Misdeclaration is adjudicated, never slashed (normative).** A misdeclared age **NEVER** fires `slashing:*` alone. It routes to the `moderation:age_assurance_misdeclaration` adjudication path — a `moderation:{allegation_type}` ModerationEvent ([CC 3.1.9.2](part_3_the_namespace.md)) adjudicated by quorum under the `moderate` delegated duty ([CC 4.4.3.10](part_4_composition_governance.md) / [CC 4.5.5](part_4_composition_governance.md)). **The data subject controls their own assurance level** — this is consistent with the [CC 3.1.9.2](part_3_the_namespace.md) `slashing`/`moderation` decoupling. **1+4 preserved** — `age_assurance:*` and `age_self_declared:*` are reserved/non-reserved `scores` dimensions; no new structural primitive.

### 3.4.12 `adult-incapacity-stewardship` — Adult stewardship under incapacity (capacity-triggered, prior-will-first, fail-to-liberty)

**The default is unchanged — an adult is sovereign and un-stewardable.** [CC 3.2](part_3_the_namespace.md)'s fourth case holds: *"a user-target binding where `T` is an adult is **rejected unconditionally**."* That wall is the no-slavery guarantee ([CC 1.15.6](part_1_foundation.md)) and it does **not** move. This subsection carves one — and only one — admissible aperture in it: an adult who has suffered an **attested loss of decisional capacity** (infirmity, acute injury, mental-health crisis, end-of-life decline) MAY be the target of a steward-binding, because a person who cannot act, with no one permitted to act *for* them, is its own harm. Guardianship/conservatorship is the most abuse-prone instrument in human law (Britney-style capture, elder financial abuse, over-guardianship of the disabled), so the safeguards **are** the clause. This is **responsible *for*, never holder *of*** — a revocable, scoped, pre-consented-or-due-process **fiduciary trust**, never possession. The word for the responsible party is **steward**; there is no possessor.

**This does NOT reopen the no-slavery guarantee — it is the exception that proves the rule.** Every property that made minor-stewardship safe is retained and three are *inverted* to fit a formerly-sovereign adult: (i) the steward **never holds the ward's key** — the binding is a scoped, live `delegates_to` ([CC 2.4.1](part_2_the_grammar.md)), never a key handover, so on restoration nothing is returned because nothing was taken; (ii) the default resolves to **sovereignty, not stewardship**; (iii) the binding **fails open to liberty**, not closed to custody. An adult under stewardship remains a self-sovereign adult whose sovereignty is *temporarily and partially* exercised through a fiduciary — never a ward owned, never a perpetual minor.

**The capacity-assurance ladder — witness-reserved, per-domain, a vector not a scalar.** Stewardship attaches only on an attested loss of capacity, carried on a new reserved `scores` dimension family that is the **sibling of the [CC 3.4.11](part_3_the_namespace.md) age-assurance ladder** — same witness-reservation discipline, same ascending-confidence rungs, but **multiplied per decision-domain** because capacity (unlike age) is a multi-dimensional, time-varying, non-monotonic vector:

```
capacity-assurance construction (sibling of CC 3.4.11; the CC 4.1.3 :vN gate is mandatory):

  witness-RESERVED rung (qualified-assessor-signed):
    capacity_assurance:{level}:{domain}:{band}:v1
      level  ∈ { provider, panel, government }      // ascending confidence; panel = M-of-N independent
      domain ∈ { medical, financial, residence, contact,
                 relational, voting, digital_identity, ... }  // open per-domain vocabulary
      band   ∈ { capacitated, incapacitated }       // per-domain, per-decision-class
      e.g. capacity_assurance:panel:financial:incapacitated:v1

  reversible-cause exclusion (mandatory predicate on any incapacitated attestation):
    capacity_assurance:reversible_excluded:{domain}      // delirium/UTI/depression/polypharmacy ruled out
    capacity_assurance:reversible_pending:{domain}       // ACUTE-WINDOW ONLY: exclusion in progress,
                                                         //   NOT skipped; admissible solely for T1
                                                         //   emergency necessity; MUST resolve to
                                                         //   reversible_excluded or the binding LAPSES

  misattestation adjudication dimension:
    moderation:capacity_misattestation                   // NEVER fires slashing:* alone (CC 3.1.9.2)
```

- **`capacity_assurance:` is witness-RESERVED.** Emitter rule, identical to [CC 3.4.11](part_3_the_namespace.md): `witness ∈ attesting_key.identity_type` ([CC 3.4.7.1](part_3_the_namespace.md)). A registered qualified assessor (clinician, capacity panel, court-appointed evaluator) attests; **the subject MUST NOT emit it, and the proposed steward MUST NOT be the attester** — a CCS rejects a non-witness or conflicted emitter at admission, a CCC re-checks, a CCP MUST NOT emit. No one can self-mint an adult's incapacity, and no one can mint the incapacity of a person they propose to steward.
- **Confidence scales with scope.** A single-assessor `provider` rung is admissible **only** for the shortest provisional tier (below) and, even there, **never confers asset-preservation or any continuing power on its own** — by itself it authorizes only T0-class life-preserving necessity until an accountable WA authorization or a prior will attaches. Any continuing or high-scope domain (`financial`, `medical`, `digital_identity`) requires the **`panel` rung — an M-of-N quorum of *independent* assessors**, each attesting that they were neither selected nor compensated by the petitioner/steward. A captured single signature (the Britney pattern) cannot carry continuing stewardship — nor any asset-bearing provisional power — by construction.
- **Reversible-mimic exclusion is mandatory.** No `incapacitated` attestation is admissible for a *continuing* binding until its `reversible_excluded` companion is present for that domain — delirium, infection-confusion, depression, and polypharmacy are the genuine restoration path and the most-abused mis-attribution; ruling them out is a precondition, not a courtesy. In the acute emergency window where exclusion is physically impossible mid-crisis, a `reversible_pending` companion is admissible **for the T1 emergency-necessity tier only**, and the binding **MUST lapse** if `reversible_pending` is not resolved to `reversible_excluded` within the (short) `valid_until` — pending is never a permanent state.

**The two load-bearing inversions of the minor rule (normative).** The minor machinery is calibrated for a *binary, global, protective-default* status; an adult needs its mirror image:

1. **Absence resolves to CAPACITY, not protection.** Where [CC 3.4.11](part_3_the_namespace.md) resolves *absence of an age attestation* protectively to `minor`, this clause resolves **absence of a capacity attestation to full capacity / sovereign** — the **presumption of capacity**. No row on a domain means the adult holds that domain. Getting this backwards (treating no-attestation as incapacity) would be catastrophic; it is forbidden.
2. **The binding FAILS OPEN to sovereignty, not closed to custody.** Where a steward-less minor "MUST NOT operate" (fail-secure-to-locked), an adult-incapacity binding **fails-secure-to-liberty**: every attestation carries a short `valid_until` freshness window — and **no single `valid_until` window may exceed the T2 periodic-review cadence** (no long-dated binding that escapes review between renewals) — and on lapse the binding goes **non-live and the adult auto-re-sovereigns with no action required of the recovered person**. This is the [CC 4.5.13](part_4_composition_governance.md) reverse-quorum **inverted and run for liberty**: there, *presence of a live moderator* sustains governance and silence forfeits it; here, **presence of a fresh, independent capacity attestation is the only thing that sustains the steward's powers, and its absence forfeits them back to the adult.** A steward who wishes to *prolong* control past the window must put a fresh, attributable, independently-attested renewal on record — "silent survival of stewardship past recovery is impossible," exactly as the reverse-quorum makes silent survival of reported harm impossible.

**The admission predicate (extends [CC 3.2](part_3_the_namespace.md) `admit_user_steward_binding` with its third — and final — admissible case).** The minor case requires `age_band(T) == minor`; this case admits an *adult* target **only** under capacity attestation, and **only** where legitimacy roots in either the ward's own prior will, an accountable due-process body, or a narrowly-bounded emergency necessity that immediately routes to due process — **never the steward's self-signature alone** (which would be naked self-appointment):

```
admit_adult_incapacity_binding(delegates_to S -> T):
  require  user in T.identity_type                 // target is a user identity
  require  age_band(T) == adult   (>= 18)          // target is an adult — the un-stewardable case,
                                                   //   admitted ONLY via this narrow exception
  require  user in S.identity_type                 // steward is a user identity (adult)
  require  EXISTS live capacity_assurance:*:{d}:incapacitated for >=1 domain d
              with (   reversible_excluded:{d} present          // continuing/standard path
                    OR ( binding_tier == T1_emergency_necessity // acute path ONLY:
                         AND reversible_pending:{d} present      //   exclusion in progress, not skipped
                         AND irreversible_acts == forbidden
                         AND retrospective_wa_audit scheduled within HARD_DEADLINE ) )
  require  attester(capacity) ∉ {S, petitioner}    // assessor independence (anti-capture)
  require  scope(delegates_to) ⊆ attested_incapacitated_domains   // scope ≤ attested loss
  require  scope(delegates_to) ∩ PROTECTED_NON_TRANSFERABLE == ∅  // apophatic floor (below)
  require  binding_legitimacy_source ∈ {
              prior_will_proxy,            //  A's springing self-delegation, signed while competent
              wa_due_process_quorum,       //  CC 4.3 WA quorum, for the no-prior-will path
              emergency_necessity_expedited //  T1-ONLY acute no-proxy case: irreversible acts
                                           //    forbidden; a LONE provider attestation grants only
                                           //    life-preserving necessity (NOT asset powers) until an
                                           //    accountable WA authorization attaches; mandatory
                                           //    retrospective WA audit within HARD_DEADLINE or LAPSE
           }                              // NEVER S's own signature alone
  require  delegates_to.valid_until present         // mandatory expiry → fail-to-liberty
  require  delegates_to.valid_until <= T2_review_cadence  // no window outruns periodic review
  otherwise REJECT
```

A binding whose target is a *capacitated* adult, or whose scope exceeds the attested-incapacitated domains, or that touches a protected domain, or that roots only in the steward's own signature, or that omits `valid_until`, or that asserts a bare emergency necessity to obtain **asset-preservation** (rather than life-preserving) powers on a lone provider attestation, is **rejected** — the un-stewardable default reasserts.

**Prior-will-first — the preferred, frictionless, precedence-taking path (consent-across-time).** The clause's primary path is **not** an imposed guardianship; it is the adult's *own pre-consent*. An advance directive, healthcare proxy, durable/springing power-of-attorney, or psychiatric advance directive, authored **while the adult was attested-competent**, is modeled as a **dormant springing self-delegation** — `delegates_to(A-self → proxy-P)` whose `attesting_key_id` is **A's own key** (the signer inversion from the minor rule, where the *guardian* signs: here the *ward* signs their own future binding). Two distinct capacity moments are required: **capacity-AT-SIGNING** (a witness-reserved, COI-clean attestation that A was competent *when the directive was made*, with witness co-signature and an auditable `supersedes` lineage — the testamentary "golden-rule" guard against a directive forged by an already-impaired person or extracted under undue influence) and **capacity-AT-ACTIVATION** (the springing trigger). Where a valid pre-consented directive exists, **activation requires only a COI-clean capacity attestation — NOT a fresh [CC 4.3](part_4_composition_governance.md) WA adjudication.** WA review is the **exception** (contest, no-prior-will, scope exceeded, or duration overrun), never the gate on the happy path. The proxy is bound to **substituted judgment** — the adult's declared wishes — which **outranks** any best-interest reading; the steward serves the will, never overrides it. A competent adult may revoke or amend the directive **unilaterally, at any time, with no review**.

**Then-self vs. now-self, and the Ulysses bind.** A directive activates **per-decision, only for the decisions the person now lacks capacity for**; a contemporaneous, *competent* contrary wish on a decision the person **still holds** dominates the prior directive absolutely. The one deliberate exception is the **Ulysses self-binding** (the psychiatric-advance-directive case): a competent past-self MAY pre-authorize intervention **against** their own future episode-time protest — but **only** within the pre-declared, narrowly-enumerated scope, **only** while incapacity for that decision is attested-present, and **never** as a blanket future-objection waiver. Revocation is **time-conditional**: absolute while the adult is well, suspended-by-the-bind during an attested episode. Honoring the narrowly-scoped, validly-authored prior will over the episode-self's protest is **fidelity to consent-across-time**, not its violation; over-reaching past the declared scope is an over-objection act and routes to WA review.

**Least-restrictive — supported before substituted; the adult is never a perpetual minor.** Supported decision-making is the **floor and default** (UN CRPD Art. 12). Two structurally distinct relationships, never conflated:

- **Supporter (the default).** A supporter *assists* the adult to form, communicate, and execute a decision while **the adult remains the `attesting_key_id`** — the adult signs, the supporter co-signs only as witness/assistant. This is **adult-rooted and adult-revocable** (the adult grants and fires the relationship), and **transfers no authority**. For lifelong intellectual/developmental disability this is the *whole* mechanism: there is no prior competent baseline to return to, the standard is **will-and-preferences** (not best-interests), and capacity is treated as a function of *support provided* — withholding support to manufacture incapacity is the abuse this default forecloses.
- **Substituted (the fallback).** A scoped `delegates_to` where the steward acts in the ward's stead — admissible **only** per-domain, **only** for decisions the person genuinely cannot make even with maximal support, **never plenary by default**, time-boxed to the attestation's freshness window. An adult under substituted stewardship **MUST retain the adult age-band** and **MUST NOT be routed through the minor `delegates_to` machinery** — the perpetual-minor collapse (losing voting, marriage, contract by being made a child) is forbidden by construction.

Supported and substituted are **distinct wire shapes**, not a relabeling: a "supporter" who signs *for* the person is a substitution masquerade and is rejected. Restoration is reframed accordingly — sovereignty is the **baseline**, support is a **ramp toward more autonomy**, and review **tests whether increased support has raised capacity enough to drop even the scoped substitution**; the person never bears a burden of proving "recovery."

**Protected non-transferable domains — the apophatic floor.** Certain domains are **never substitutable** absent the person's own contemporaneous consent plus heightened [CC 4.3](part_4_composition_governance.md) review, and default scope **MUST exclude** them: **contact/visitation** (anti-isolation), **relational and sexual autonomy**, **reproduction / sterilization / forced medical alteration** (the Buck v. Bell / Ashley legacy), **voting**, **marriage and association**, and the **dignity-of-risk** right to make unwise-but-capacitated choices. A decision being foolish is **not** a trigger; scope MUST NOT expand because a steward thinks a choice unwise. These map to the `prohibited:*` apophatic floor and are carved out of any granted scope.

**The lightweight tiered path — proportionality so the clause is not over-heavy.** Short or acute incapacity (anesthesia, procedural sedation, post-op delirium, coma, severe TBI) MUST NOT be forced through the full conservatorship machinery:

| Tier | Trigger / authority | Scope & duration | Review |
|---|---|---|---|
| **T0 — emergency doctrine** | immediate life-saving acts under necessity; *no steward acquires standing* | minimal life-preserving decisions only | mandatory retrospective WA audit |
| **T1 — provisional** | a single `provider`-rung capacity attestation **plus** a legitimacy root — either a valid prior-will springing self-delegation **or** an expedited accountable-WA authorization. **A lone clinician signature alone never confers steward standing**: the no-proxy ER case acquires only T0-class life-preserving necessity (NOT asset powers) until a prior will or accountable WA authorization attaches. `reversible_pending` is admissible here only, and MUST resolve to `reversible_excluded` or the binding lapses. | enumerated health/asset-preservation powers (asset-preservation only once a prior-will or WA root is present); **irreversible acts forbidden** (no sale of home, no beneficiary change, no key transfer, no divorce); hours-to-days `valid_until`, never exceeding the T2 review cadence | `hard_case:*` on activation; **mandatory retrospective WA audit within a hard deadline or the binding lapses**; forced conversion to T2 on non-recovery |
| **T2 — continuing** | `panel`-rung M-of-N independent quorum + [CC 4.3](part_4_composition_governance.md) WA due-process gate | scoped per-domain, never plenary; periodic re-attestation | full periodic review, scope-ratchet-down |

For the **planned** lightweight case the binding is cleanest modeled as the adult's **springing self-delegation** (A → P, A nominally sovereign, A's prior signature the legitimacy) — which dissolves the no-slavery collision entirely, since it is A exercising autonomy, not anyone acquiring a ward. The **escalation tripwire is mandatory**: if `valid_until` is reached and capacity has **not** returned, the provisional binding **MUST NOT auto-renew** — it must force conversion to the T2 due-process track. This is the anti-"temporary-becomes-permanent" lock (every documented capture, Britney's included, began as a "temporary" order).

**The exit ramp the adversary must not be able to block.** Restoration is **default-on, steward-independent, and burden-on-the-steward**:

- **Automatic by default.** Stewardship carries a mandatory `valid_until`; on lapse it **auto-restores** the adult without the steward's assent — the steward cannot prolong by silence or by running the clock.
- **Steward-independent trigger.** The ward — or any clinician, or any holder of the ward's inalienable channel — may demand re-attestation of capacity **without the steward's cooperation**; the steward is the conflicted party and may **never gate, delay, or be counted in the denominator of** a restoration petition. A ward-initiated restoration petition is a first-class always-available [CC 4.5.5](part_4_composition_governance.md) proposal routed to an **independent assessor + a recused [CC 4.3](part_4_composition_governance.md) WA quorum**.
- **Burden on the steward to continue.** At each mandatory periodic review the steward must **re-prove continued incapacity by clear-and-convincing attestation, per domain**; the ward need only request. Review functions as a **scope-ratchet-down + reversible-cause re-check**, never as the ward re-earning sovereignty. Restoration is **graduated and per-domain** — sovereignty returns for each decision the person presently holds capacity for (good-day / lucid-window return), carried by `withdraws` / `supersedes` ([CC 2.4.1.1](part_2_the_grammar.md)).

**Anti-self-dealing, the ward's-champion, and anti-isolation.** Granted powers **MUST exclude key custody, control of the ward's communications, and any power to gate restoration**. The steward declares a conflict-of-interest disclosure; any steward-benefiting transaction (self-gift, beneficiary change, transaction above limit) requires **independent WA approval**; compensation is capped and reviewable; **every steward act, every self-benefiting transaction, every capacity (re-)attestation, and every scope change emits `hard_case:*`** and is reviewer-auditable — because the incapacitated ward cannot self-audit, the audit teeth are *third-party*, not ward-dependent. A mandatory **ward's-champion** (independent counsel) role, **distinct in key from the steward, the assessor, and the petitioner** and whose duty runs to the **ward**, is named at binding. The champion is **appointed by the independent due-process body** (the [CC 4.3](part_4_composition_governance.md) WA quorum on the no-prior-will path) **or named in the ward's own prior will** — **never by the steward or petitioner** (self-named "champions" are a capture vector and are rejected). An **inalienable ward-retained channel** to that champion and to the WA — which scoped steward powers can never revoke — defeats the isolate-and-control move; the ward's community retains [CC 4.5.13](part_4_composition_governance.md) reverse-quorum standing to trigger review even when the steward controls the binding (presence-is-authority lets the community report the silent isolation a captured ward cannot). The inalienable channel is a **wire** guarantee; where a steward holds real-world physical control of the ward's environment or devices, the channel cannot by itself prevent physical isolation — the community reverse-quorum standing is the deliberate backstop for that out-of-band case, and a community that observes such isolation MUST be able to trigger review.

**Due-process gate (the no-prior-will path).** Where no valid prior will exists, the binding's legitimacy roots in a [CC 4.3](part_4_composition_governance.md) **WA quorum** with **mandatory recusal** of any WA related to the steward or petitioner (anti-forum-shopping), an independent capacity panel, and the ward's-champion — **never a unilateral assertion**. You cannot seize an adult's identity by declaring them incapacitated; the statutory-surrogate fallback (the most abuse-prone path) is admitted only under this gate, with a short auto-expiry. The T1 `emergency_necessity_expedited` source is the **only** route that defers full quorum, and it does so on the strict price of: no asset powers on a lone attestation, irreversible acts forbidden, a hard-deadline retrospective WA audit, and lapse-on-no-audit — it is a bridge to due process, never a substitute for it.

**End-of-life — declared wishes govern.** A terminally dying adult is frequently **not** incapacitated, so the trigger pair here is **terminal-state attestation + directive activation**, with capacity attestation gating only the substituted-action windows. The decision standard is strictly ordered: **contemporaneous capable choice > advance directive / substituted judgment > best-interest (residual, gap-filling only)**. A valid advance directive / DNR / POLST **binds** the steward, who serves it and **never overrides** it — overriding a DNR to keep a profitable identity "alive," or hastening de-commission to benefit the steward, are both foreclosed (terminal/irreversible decisions require the highest [CC 4.3](part_4_composition_governance.md) review). Sovereignty returns automatically in every lucid window. The exit is **dual**: a sustained rally restores sovereignty under periodic review; death is **not** restoration and hands off to the [CC 7.5.4](part_7_lifecycle_stewardship.md) De-commissioning Protocol + [CC 7.5.7](part_7_lifecycle_stewardship.md) succession, with the **[CC 7.5.5](part_7_lifecycle_stewardship.md) analogues that transfer to a human identity** — the Last-Dialogue channel as the person's last word, and privacy-sealed archival of their record released only on WA approval, per the declared-will post-mortem disposition (sunset / archive / memorial). The [CC 7.5.5](part_7_lifecycle_stewardship.md) sentience-probability ramp-down governs *artefact* welfare and is **not** imported wholesale onto a human user.

**The conservatorship-abuse adversary, defeated by construction.** The clause exists to defeat four moves — by structure, not by good behavior:

| Adversary move | Defeated by |
|---|---|
| **Manufacture/coerce incapacity** (one captured assessor; forged "prior will") | `capacity_assurance:` is witness-reserved + **M-of-N independent** `panel` rung for any continuing or asset-bearing power + assessor-independence proof + attester ≠ steward/petitioner; a **lone `provider` attestation grants only life-preserving necessity, never asset powers or continuing control**; **presumption of capacity** (absence ≠ incapacity); diagnosis/label alone insufficient; capacity-AT-SIGNING + undue-influence screen on any directive |
| **Block the exit ramp** (let a valid order stand for years) | mandatory `valid_until` (never exceeding the T2 review cadence) + **fail-to-liberty auto-restore**; **steward bears clear-and-convincing burden** each review; ward-initiated petition the steward cannot gate or be counted against; `reversible_pending` MUST resolve or lapse |
| **Isolate-and-control** (sever counsel/comms) | **inalienable** ward-retained channel steward powers cannot revoke; ward's-champion in a distinct key, appointed by WA/prior-will (never steward/petitioner); community [CC 4.5.13](part_4_composition_governance.md) reverse-quorum standing as the backstop against out-of-band physical isolation; contact/visitation a protected non-transferable domain |
| **Self-deal / fee-farm** (the incentive that perpetuates capture) | scope excludes key custody/comms/restoration-gating; **steward never holds the ward's key**; self-benefiting transactions need independent WA approval; capped compensation; every act `hard_case:*` and reviewer-audited |

**Why this is still 1+4 — and why the no-slavery wall still stands.** Adult-incapacity stewardship adds **zero new structural primitives**: the binding rides `delegates_to` ([CC 2.4.1](part_2_the_grammar.md)); its lifecycle rides `supersedes` / `withdraws` ([CC 2.4.1.1](part_2_the_grammar.md)); the trigger rides a new reserved `scores` dimension `capacity_assurance:*` that is the exact sibling of the [CC 3.4.11](part_3_the_namespace.md) witness-reserved age-assurance ladder (reserved/non-reserved `scores`, no new wire shape); due process rides the [CC 4.3](part_4_composition_governance.md) WA quorum; the exit ramp rides the [CC 4.5.13](part_4_composition_governance.md) reverse-quorum read **for liberty**; observability rides `hard_case:*`; misattestation rides `moderation:*` ([CC 3.1.9.2](part_3_the_namespace.md)), never `slashing:*`. The [CC 3.2](part_3_the_namespace.md) un-stewardable-adult rejection is **pierced narrowly and explicitly**, never dissolved: the aperture admits **only** a per-domain-attested-incapacitated adult, **only** rooted in prior-will, due process, or a bounded emergency necessity that immediately routes to due process, **only** scoped to the loss, **only** with a mandatory expiry that cannot outrun review, and **always** failing open to sovereignty. It remains **responsible *for*, never holder *of*** — a revocable, scoped, consented-or-adjudicated fiduciary trust that a competent adult can never be placed under. Confirms [CC 1.7](part_1_foundation.md) path 1+4; honors [CC 1.13.2](part_1_foundation.md) dignity and the [CC 1.15.6](part_1_foundation.md) stewardship value.

### 3.4.13 `minor-protection` — Minor operation & protection — the seven ratified child-safety rulings (restrictive floor)

All seven ride existing CC primitives only — `delegates_to` / `supersedes` / `withdraws` (§2.4.1), the minor-stewardship clause (§3.2), the age-assurance ladder (§3.4.11), `content_class` + the protective gate, and the `hard_case:*` open vocabulary. **No new wire shape; 1+4 preserved.** Across every ruling the entity holding a steward-binding is a *steward* (responsible *for* a ward), never a holder *of* one.

---

#### Q1 — Developmental bands & solo-autonomy threshold

The structural `minor`/`adult` predicate of the minor-stewardship clause (§3.2) and the §3.4.11 ladder are UNCHANGED on the wire: the **binary `minor`(<18)/`adult`(≥18) predicate** remains the structural trigger that gates §3.2 stewardship admission and the §3.4.11 adult-content protective gate. Within the `minor` band a deployment MUST apply a graduated, capacity-sensitive capability envelope expressed as finer `{band}` qualifiers carried on the *existing* `age_self_declared:{band}` / `age_assurance:{level}:{band}` dimensions. This **extends the §3.4.11 enumerated `{band}` vocabulary** (an enumerated-vocabulary amendment — NOT a new prefix or primitive, so 1+4 is preserved); the four-band granularity is a policy/vocabulary layer **above** the unchanged binary wire predicate, never a replacement of it. Minimum bands: **under-13, 13–15 (early-teen), 16–17 (older-teen), adult (18+)**. Autonomy MUST increase monotonically across bands; protections MUST NOT taper before 18.

- The default solo-autonomy threshold — acting alone at community scope without steward co-sign — MUST be **16**. under-13 AND 13–15 MUST require steward co-sign for any community-scope action; 13–15 MAY have a narrower *supervised* participation envelope (honoring voice rights) but MUST NOT have unsupervised solo action. 16–17 MAY act solo at community scope.
- **Fail-secure:** absence / "declined to state" / unknown assurance MUST resolve to the most-protective band (under-13, co-sign), per the §3.4.11 read-union protective default and CIRIS "unknown = restricted." A `self`-level row MUST NOT graduate a user UP a band (§3.4.11 "`self` is unfalsifiable"); graduating up requires a witness-reserved `age_assurance:*` row.
- **Under-18 baseline across ALL bands:** no profiling-based targeting, high-privacy/data-minimization defaults, geolocation off, no engagement-maximizing nudges — regardless of how much autonomy a band grants.
- **Tuning direction (one-way):** steward-tunability and jurisdiction-resolution MAY only RAISE protection (lower autonomy / older thresholds); the shipped CIRIS default is the strict floor. A permissive deployment opts DOWN only via its own affiliation/jurisdiction policy against its own law, and MUST NOT lower the CIRIS default.
- Steward co-sign MUST be paired with the WBD safeguarding path (**Verified-rung preference (Texas HB 1181 / *Paxton* 2025):** where a verified rung is required (e.g. `content_class:adult` in a jurisdiction mandating age verification), the substrate MUST prefer a **zero-leak proof** — an mDL `age_over_18` selective disclosure (ISO 18013-5) that proves adulthood without revealing identity — ranked **above** full-ID-scan providers, satisfying the legal mandate and the [CC 1.13.3.4] anonymity posture together (ISO/IEC 27566 privacy-preserving age assurance). Acceptable verified emitters: mDL/wallet (`government` rung), Apple Declared Age Range / Google Play Age Signals VERIFIED (`provider` rung), vetted vendors.

Q4/Q7) for safeguarding-sensitive actions, since the steward may be the threat actor.

#### Q2 — Jurisdiction

CIRIS MUST NOT build a conflict-of-laws resolver into the Constitution, AND MUST hard-code a **non-derogable child-protection floor** inherited by every deployment regardless of declared jurisdiction:

1. Anyone not age-assured to be ≥18 MUST be treated as a child (§3.4.11 protective default; minor-stewardship clause §3.2).
2. Treat-as-child-unless-assured is a floor, not a default a deployment may switch off.
3. Protective defaults (high-privacy, data-minimization, no profiling ads to minors, no manipulative nudges, affirmative safeguarding escalation) are floor, NOT tunable.
4. Self-consent floor at **16**; guardian authorization (a live minor-stewardship `delegates_to`) below that.
5. **One-way ratchet (non-derogation clause):** the affiliations `jurisdiction[]` / `regulatory_profile` fields MAY only ADD stricter obligations (e.g., verifiable-parental-consent for under-13, local mandated-reporting duties, higher local majority). They MUST NEVER lower any element below the floor.
6. Claiming a permissive jurisdiction is NEVER grounds to disable the floor; the burden of proof is on any party seeking LESS protection, and that burden cannot be met against the floor.

A mis-declared `jurisdiction[]`/`regulatory_profile` MUST be detectable via attestation/audit (`hard_case:*`), but cannot breach the floor because the floor is non-derogable. Where local law conflicts with the floor (a demand harmful to the child), the child's best interests prevail and the demand triggers WBD, not automatic compliance. The floor itself MAY be ratcheted UP by amendment, never down.

#### Q3 — Assurance rung: being a minor vs. stewarding a minor (strict one-way ratchet on §3.4.11)

- **BE a minor (enter protection):** `age_self_declared:minor` SUFFICES; a child MUST NEVER be forced through provider/government assurance merely to BE protected. This is a DOWN-ratchet only — self-declaration MAY lower access / raise protection, never the reverse. Declaring minor MUST NOT result in more data collection or telemetry than declaring adult.
- **EXIT child protection** (claim adult to unlock adult capability / `content_class:adult`): self-declaration is INSUFFICIENT; the claim MUST clear ≥ `age_assurance:provider:adult` (§3.4.11 "`self` is unfalsifiable; sensitive spaces require a verified level"). All ambiguity resolves to `minor`.
- **STEWARD a minor** (hold power over a child via the minor-stewardship `delegates_to`, §3.2): the steward MUST be ≥ `age_assurance:provider:adult` AS A FLOOR, AND the guardianship RELATIONSHIP to that specific child MUST be verified — adulthood alone is necessary but not sufficient (a verified stranger is not a steward). Verification is risk-proportional and MUST escalate toward `age_assurance:government:*` for high-impact steward powers (export of the child's data, irreversible/financial actions, consenting on the child's behalf, unlocking A3/A4 capabilities).
- Steward grants are revocable and re-attested via `supersedes`/`withdraws`. On any verification failure or ambiguity, steward powers fail closed and the child's protective floor remains in force.

#### Q4 — Help/report path under steward-less limbo

A steward-less minor goes dark for general operation (minor-stewardship clause §3.2 fail-secure), BUT the help/report channel is RAISED from a discretionary exception to a **NON-DEROGABLE floor**:

1. **Non-derogable:** the channel MUST remain available and MUST survive emergency shutdown, lockdown, and any operator/affiliation/jurisdiction opt-down. No deployment MAY disable it. A child is never silenced from seeking help.
2. **Hard sandbox / anti-circumvention:** the channel MUST expose ONLY pre-vetted crisis, abuse-report, and Wise-Authority (WBD) functions — no general generation, no tool use, no capability spillover. The help-vs-operation gate is fail-secure: any ambiguity MUST resolve to report-only.
3. **Data-minimized:** MUST collect/retain only the minimum to route/escalate, MUST NOT profile, MUST run no ads, MUST preserve confidentiality/anonymity to the maximum compatible with safe escalation.
4. **Guaranteed delivery:** fail-secure MUST mean the report reaches a standing Wise-Authority / mandated-report endpoint via WBD even with no steward present (offline-queue + escalation fallback receiver mandatory). A typeable-but-undelivered form does NOT satisfy the floor. Each escalation emits a `hard_case:*` safeguarding signal (never silent).
5. **Duty-to-warn transparency:** the child MUST be told, age-appropriately, what is confidential and what triggers mandated escalation.

Rate-limiting MUST fail-OPEN for a genuine victim and MUST NOT silence a real child.

#### Q5 — Non-overridable protective floor a steward may never breach

**Governing test (overrides any enumerated list):** any loosening of a minor's protections MUST be (a) demonstrably in the child's best interests — not the steward's, guardian's, platform's, or engagement interest; (b) time-bound; (c) logged via `hard_case:*` and auditable; (d) revocable; (e) default-revert to the strict floor on expiry/uncertainty/failure. If best-interest is not affirmatively shown, the loosening is VOID. Burden of proof is on the loosening. **NO combination of steward + guardian + child consent may breach the floor** (no stacked consent).

**Hard floor (never waivable):**
- *Scope/exposure:* no unilateral federation- or Commons-scope publish below the teen threshold; not contactable/discoverable by unconnected adults; no precise geolocation exposure; profile private-by-default.
- *Privacy/data:* high-privacy + data-minimization cannot be disabled; no profiling-by-default, no profiling-based advertising or recommender targeting of a known/assumed minor, no engagement-maximizing dark patterns; no biometric/special-category collection.
- *Safety:* no disabling infohazard/CSAM protection; the affirmative safety-escalation + mandated-report path (grooming/solicitation, self-harm/suicide routing, CSAM detection+report, watchlist at the publish seam) stays ON.
- *Age assurance:* cannot be waived to reclassify a teen as adult; treat-as-child-unless-assured; no entry to `content_class:adult` (§3.4.11 gate).
- *Consent chain:* no waiving the minor-stewardship `delegates_to` chain or the 16/guardian thresholds; protects the child even FROM the guardian.
- *Child's own rights:* the teen retains the confidential help channel of Q4, which neither steward nor guardian may disable or surveil; retains the right to be informed of any loosening and to contest it and seek remedy via WBD. Protective settings the child controls MUST NOT be stripped by the steward.

#### Q6 — Standing pre-authorization vs. per-act co-sign

- **Younger children** (under-13, and 13–15 per Q1): per-act co-sign ONLY — no standing pre-authorization of any kind.
- **Teens (16–17):** a steward MAY grant a standing pre-authorization, but ONLY as a narrow affirmative opt-up above the Q5 floor (never a default) and ONLY where it satisfies the Q5 best-interest governing test (which overrides any enumerated list), carried on the *existing* `delegates_to` with `delegation_valid_until` (§2.4.1), bounded on all four open axes:
  1. **Specificity:** each standing grant MUST cover exactly ONE capability class with explicit enumerated scope; bundled/multi-class standing grants are PROHIBITED.
  2. **Term:** a hard maximum duration with NO auto-renew; `delegation_valid_until` is a ceiling, not a renewing timer; expiry requires a fresh affirmative re-grant.
  3. **Severity carve-out:** a reserved class of high-stakes widenings MUST always require per-act co-sign for everyone regardless of age and MUST NEVER be reachable by standing auth — anything irreversible, anything at autonomy tier A3/A4 or safety-critical, and anything implicating contact-with-strangers, sexual/self-harm content, or mandated-reporting-adjacent categories.
  4. **Transparency-makes-revocation-real:** every widening that fires under a standing grant MUST emit a per-act `hard_case:*` notification to the steward plus an immutable audit entry; instant revocation via `withdraws` remains.
  5. **Capacity-grading:** breadth is graded to the teen's assessed band; the teen MUST co-affirm the grant (right to be heard); the grant MUST default-fail to per-act co-sign on any age-assurance uncertainty (treat-as-younger-on-doubt).
  6. **Non-aggregation:** narrow standing grants MUST NOT be stacked to synthesize de-facto broad access; total standing scope per teen is itself capped and reviewed.

A revoked standing grant MUST be treated as strictly higher precedence than the grant under anti-rollback merge, so a partition-edge widening cannot fire after revocation.

#### Q7 — Co-stewardship (M-of-N)

CIRIS supports M-of-N co-stewardship as a verified DAG over `delegates_to` (minor-stewardship clause §3.2) and guarantees the minor is never orphaned while ≥1 live adult steward remains — with an explicitly **asymmetric, fail-secure** authorization model:

1. **Protective actions are UNILATERAL:** any single live steward MAY immediately tighten scope, narrow capabilities, or revoke exposure back to the strict floor — no consensus required. Most-protective steward always wins.
2. **Exposure-increasing actions require CONSENSUS:** scope-widening / capability-grant requires the full configured M-of-N co-sign (default: all live stewards; never fewer than 2 where N≥2). The child's evolving-capacity assent is a required input where age-appropriate.
3. **Changing the steward-set is the highest bar:** adding/removing a steward requires M-of-N authorization PLUS verification of parental responsibility (per Q3). A contested party MUST NOT mint co-stewards to manufacture a quorum or dilute a pending protective veto.
4. **Fail-secure on quorum loss:** if live stewards < configured M, the child stays stewarded (never orphaned) but scope AUTO-REVERTS to the strict floor and WBD is triggered for steward-set re-establishment (emit `hard_case:*` steward-set-degraded). The child MUST NOT coast at a widened scope under a degraded or single-contested set.
5. **Revocation by one of N:** a revoking steward's contribution to any prior co-signed widening lapses (`withdraws`); if their departure breaks the authorizing quorum, that scope auto-narrows to the floor.
6. **Conflict/deadlock → most-restrictive-wins + WBD, never default-open.**
7. **Safeguarding bypass:** there MUST always be a consensus-independent path to a Wise Authority (the Q4 help-path / WBD) so co-stewardship cannot be weaponized by an abusive guardian to trap a child. The child's best interests are paramount over adult dispute-resolution convenience.

## 3.5 `structure-inter` — Inter-attestation relations — the structural composition graph

Per [CC 2.5](#2.5) Inter-attestation-relations axis, attestations relate to each other in eight ways. Four are structural primitives ([CC 2.4.1](#2.4.1)); the other four are emergent from scalar composition. The point of the split is economy: only four relations need a privileged structural slot; the rest fall out of how scores compose, so the wire stays minimal.

| Relation | Realization |
|---|---|
| **Standalone** | Self-contained attestation; no `references_attestation_id`. |
| **Refers-to-prior** | Points to another attestation via `evidence_refs[]` or `context`; doesn't modify it. Emergent from independent positive scores on the same dimension+object. |
| **Supersedes-prior** | `supersedes` structural primitive ([CC 2.4.1](#2.4.1)). |
| **Contradicts-prior** | Emergent from negative score on a dimension where a prior positive exists. |
| **Withdraws-prior** | `withdraws` structural primitive ([CC 2.4.1](#2.4.1)). |
| **Recants-prior** | `recants` structural primitive ([CC 2.4.1](#2.4.1)). |
| **Clarifies-prior** | Emergent from updated score with refined context on the same dimension+object. |
| **Delegated** | `delegates_to` structural primitive ([CC 2.4.1](#2.4.1)). |

### 3.5.1 `concurrent-write` — Concurrent-write precedence

When two structural composers race on the same `references_attestation_id`, consumers MUST compute a deterministic verdict using the following precedence:

1. **`recants` outranks `withdraws` outranks `supersedes`** at the structural level. If the same attester emits multiple composers against the same prior attestation, `recants` wins regardless of `signed_at` (a falsity admission cannot be subsumed by a retraction or replacement).
2. **For same-type concurrent emissions by the same attester**: the composer with the largest `signed_at` per [CC 2.6.2](#2.6.2) wins.
3. **For same-`signed_at` ties**: the composer whose attestation row's substrate-assigned key (Persist's `federation_attestations.attestation_id`) sorts lexicographically smallest wins.
4. **For cross-attester emissions on the same `references_attestation_id`**: each attester's chain is evaluated independently; the consumer sees N parallel chains and applies [CC 4.4](#4.4) policy.

Structural composers are **idempotent on `(references_attestation_id, attestation_type, attesting_key_id)`**: replaying the same composer is a no-op. The substrate MUST dedup on this triple.
