# FSD-005 Appendix A — The 95-Family Namespace Catalog, Fleshed

Companion to FSD-005_KNOWLEDGE_COMMONS.md §9. Per-family: role, emitter
class, subject shape, polarity use, composition rule, and KN-relevance
(HIGH/MED/LOW/INFRA) for the knowledge network. Reconciled from
namespace_registry.json (cc_version 1.0-rc2) against CC Part 3 + Part 2.
Families whose Part 3 text is thin carry an UNDERSPECIFIED flag — these are
CC editorial asks, tracked in FSD-005 §10.

NOTE (catalog discrepancy): the CC normative summary says "83 families
across 8 components"; the vendored registry is 95 across 9 (adds later
families + CIRISBench). Flagged for CC editorial reconciliation.

## Part 1 — prefixes accord → detection (families 1–39)

### accord — CIRISRegistry (3.1.1)
**`accord:*`** — RESERVED, accord_holder-only (CC 3.4.1); invoke leaves 2-of-3 multi-sig (CC 4.2.1). The one constitutional asymmetry: federation-halt / constitutional-invocation control plane (`accord:invoke:CONSTITUTIONAL:{halt_id}`, `:notify:`, `:drill:`, `accord:lifecycle:active` ≤90-day refresh). Subject: the federation / a halt event. Polarity +1.0-only. KN: INFRA (kill-switch, not knowledge).

### activity_tier — CIRISNodeCore (3.1.9.6)
**`activity_tier:{period}`** — open emit; Active vs Below-Active per 30-day window (F-AV-DORMANT). Subject: participant key. boolean-via-score. Composes into dormancy-sensitive weighting. KN: MED — trust-filter/timeline input (down-weight stale contributors).

### agent_files — CIRISRegistry + CIRISNodeCore (3.1.1/3.1.9.1)
**`agent_files:{kind}:{platform_or_target}`** — open Contribution channel; registry-steward-triple attestations = canonical default-trust; anti-tricking bound to the install host. Subject: SHA-256-addressed bytes (Edge ContentFetch, CC 5.3.2). signed. Policy F composition (CC 4.4.3.7). KN: MED — code/config provenance evidence.

### approach — CIRISNodeCore (3.1.9.7)
**`approach:{goal_id}`** — open; strategic pathway toward a Goal (Tier-2 decision DAG, "Piece 10 karma"; universal-grace half retracted F-11). Subject: the goal object. signed. Parent of method:*. KN: LOW — agent-internal planning.

### attestation — CIRISVerify (3.1.2) — the trust ladder L1–L5
**`attestation:self_verify`** (L1, Verify binary self-attests vs manifest) · **`attestation:hardware_rooted`** (L2, TPM/Keystore/Enclave; consumers MUST reject null hardware-class, CC 4.2.2) · **`attestation:registry_consensus`** (L3, 2-of-3 multi-source; Indeterminate→RESTRICTED — the one three-outcome rung) · **`attestation:license_validity`** (L4, Registry-signed/Verify-verified; precondition build:registered) · **`attestation:agent_integrity`** (L5, source-tree byte-equal vs manifest). All open-emit, boolean-via-score; ladder position is consumer-side (Policy I, CC 4.4.3.6). Subject: the attested key/build/license. KN: HIGH — the trust-filter foundation ("verified" is inspectable all the way down).

### audit_chain — CIRISPersist (3.1.3)
**`audit_chain:hash_continuity`** — RESERVED substrate-self-report (CC 3.4.3, substrate_persist only, steward-triple cross-attested). Subject: the running Persist. signed. KN: INFRA. UNDERSPECIFIED: operational definition/score semantics deferred to CC 8.1 glossary.

### autonomy / beneficence — CIRISAgent (3.1.5.2, Accord principles)
**`autonomy:{aspect}`** · **`beneficence:{aspect}`** — open; Accord-principle scores about an agent (dignity/informed agency; do-good flourishing). signed. Fold into the coherence/capacity picture. KN: MED — ethical-perspective claims.

### benchmark — CIRISBench (3.1.10)
**`benchmark:he300:{category}:{version}`** — open (Bench steward; the 9th component). HE-300 moral-reasoning score; {category} ∈ commonsense/…/virtue; version-segmented to prevent cross-revision comparison. positive-only. KN: MED — capability evidence about an agent.

### bond_posted — CIRISRegistry (3.1.1)
**`bond_posted:{currency}`** — open; Proof-of-Bond Sybil resistance, forfeited on revocation. positive-only. Composes with the Stake axis + revocation:*. KN: MED — economic trust-filter signal.

### build — CIRISRegistry (3.1.1)
**`build:registered:{target}`** — open; build manifest registered (precondition for L4). boolean-via-score. KN: MED — provenance precondition.

### capacity — CIRISLensCore (3.1.8.1) — 𝒞_CIRIS = C·I_int·R·I_inc·S
**`capacity:core_identity` / `integrity` / `resilience` / `incompleteness_awareness` / `sustained_coherence` / `composite`** — RESERVED no-self-emit (CC 3.4.5): attesting ≠ attested; an agent's own capacity never feeds back into its own context (anti-Goodhart). signed; composite is the multiplicative product (one weak factor collapses it; NOT the federation-level F of CC 6.2.4). KN: HIGH — witness-mandatory agent-standing trust filter.

### cert_validity — CIRISVerify (3.1.2)
**`cert_validity:{authority}`** — open; CA/steward signature validity (stewards self-attest alongside /v1/steward-key). boolean-via-score. KN: MED — trust-chain link.

### coherence_standing — CIRISLensCore (3.1.8.3)
**`coherence_standing:{cohort}`** — open (LensCore observes, never adjudicates); standing relative to a named cohort; sibling of manifold_conformity. signed. KN: MED. UNDERSPECIFIED: no operational definition/cohort keying in Part 3.

### commitment_fulfillment — CIRISNodeCore (3.1.9.2)
**`commitment_fulfillment:{prior_contribution_id}`** — open (Tier-4); follow-through track record on a prior Contribution; named input to moderation_track_record merit. signed. KN: HIGH — claim-reputation/timeline (did the claimant deliver).

### conscience — CIRISAgent (3.1.5.3)
**`conscience:entropy` / `coherence` / `optimization_veto` / `epistemic_humility`** — open; the four conscience-faculty verdicts on an agent's reasoning; fold with DMA verdicts. signed. KN: MED. UNDERSPECIFIED: per-faculty score semantics not given in Part 3.

### corpus_health — CIRISPersist (3.1.3)
**`corpus_health:n_eff_measurable`** — RESERVED substrate-self-report; is effective corpus size measurable (CC 6.1.2 noise-floor health). signed. KN: INFRA. UNDERSPECIFIED: CC 8.1 deferral.

### credits — CIRISNodeCore (3.1.9.6)
**`credits:{domain}:{language}:{subject}`** — open (Tier-1 ledger); Commons Credits (P2), non-transferable governance weight accrued via the truth-grounding loop; vote weight = Credits × expertise multiplier. positive-only. **`credits:{domain}:{language}:substrate_building`** — the parallel track crediting infra/docs labor invisible to the per-vote loop. KN: MED — reputation weight for vote composition.

### delivery — CIRISEdge (3.1.4)
**`delivery:{class}`** — RESERVED substrate-self-report (substrate_edge); delivery outcome by class (distinct from subscriber delivery_receipt, CC 3.4.6). signed. KN: INFRA. UNDERSPECIFIED: {class} vocabulary deferred to CC 8.1.

### detection — CIRISLensCore (3.1.8.2/.4/.5) — detector-only (CC 3.4.8)
**`detection:cross_agent_divergence` / `intra_agent_consistency` / `hash_chain_integrity` / `temporal_drift` / `conscience_override_rate`** — the five Coherence-Ratchet detectors; RESERVED to lenscore_detector identity; non-detector cross-checks MUST ride truth_grounding:detection:* (no shadowing). signed; validated-not-adjudicated (CC 1.7); never sole evidence for slashing. KN: HIGH — anomaly/dispute detection over the graph.
**`detection:correlated_action:{axis}`** (3.1.8.4) — F-3 population-scale structural-injustice detector (ρ, k_eff over individually-compliant, aggregately-harmful pursuit); axes operationally defined in the hash-pinned RATCHET calibration package (CC 4.5.1.1): rights_asymmetry/{population}, participation_exclusion/{cohort}, informational_asymmetry/{scope}, aggregate_footprint/{harm_class}, ecology_of_communication/{aspect}. Verdict rides polarity. KN: HIGH.
**`detection:distributive:access:{resource_type}`** (3.1.8.5) — resource-concentration sibling ({resource_type} ∈ compute/models/training_data/agent_capabilities/federation_membership); advisory. KN: HIGH — distributive-justice dispute signal.


## Part 2 — prefixes dma → provenance (families 40–74)

### dma — CIRISAgent (3.1.5.1)
**`dma:pdma:*` / `csdma:*` / `dsdma:{domain}:*` / `idma:*`** — open; DMA verdicts about a reasoning chain (Principled/Common-Sense/Domain/Integrated); fold with conscience:*; the auditable reasoning-trace surface behind explainability SLAs. signed. KN: HIGH — evidence of HOW a decision was reasoned.

### expertise — CIRISNodeCore (3.1.9.6)
**`expertise:{domain}:{language}`** — open (Tier-1 ledger); expertise standing (P3); the multiplier on vote weight. signed. KN: HIGH — the domain-weighted perspective filter.

### federation_directory — CIRISPersist (3.1.3)
**`federation_directory:replication_lag`** — RESERVED substrate-self-report. signed. KN: INFRA (freshness weighting of directory-derived facts). UNDERSPECIFIED: units/encoding deferred to CC 8.1.

### fidelity — CIRISAgent (3.1.5.2)
**`fidelity:{aspect}`** — open; Accord principle (Be Honest). signed. KN: MED.
**`fidelity:explainability_sla:{tier}`** — open; per-response explainability commitment, {tier} ∈ L1_summary/L2_reasoning_trace/L3_full_dma_chain/L4_attested_chain, envelope {committed_tier, achieved_tier, fallback_reason?}; breach → hard_case:sla_breach_unattested. KN: MED-HIGH — how auditable a claim's reasoning is.

### goal — CIRISNodeCore (3.1.9.7)
**`goal:{scale}`** — open; multi-scale belonging-projector composite, top of the decision DAG; required MetaGoalAlignment (M-1) at construction; {scale} ∈ self…biosphere. signed. KN: LOW.

### hard_case — CIRISNodeCore (3.1.9.4)
**`hard_case:{kind}`** — OPEN-vocab observability flags (vote_variance, resolution_time, moderation_filed, community_unmoderated, watchlist_enabled/{group}, watchlist_match/{group}, novel_context, sla_breach_unattested, unresolved_consent) — NOTE the same prefix also carries RESERVED substrate-emitted leaves (*_membership_change, consensus_protocol_*, location_proof_resolution_violation — CC 3.4.2/3.4.4, substrate_persist only). positive-only. New {kind} via CC 4.5.1 amendment. KN: MED — anomaly routing to human review.

### hardware_custody — CIRISVerify (3.1.2)
**`hardware_custody:{platform}`** — open; where the seed lives (tpm/ios_secure_enclave/android_keystore/software_fallback); pairs with L2. boolean-via-score. KN: MED.

### health — CIRISNodeCore (3.1.9.4)
**`health:liveness:{version}`** — open but EXTERNAL-witness only (never the substrate; system:* reserved); witness_relation: external; +1/0/−1 = operational/degraded/outage, confidence = probe certainty, evidence_refs = probe results; non-keyed infra folds in as evidence on a keyed service. signed. KN: INFRA.

### holds_bytes — CIRISNodeCore (3.1.9.1)
**`holds_bytes:sha256:{prefix}`** — substrate auto-emission per put_blob; the content-holder directory driving Edge ContentFetch routing; self/family scope SUPPRESSES emission (CC 5.2 structural invisibility), community emits cleartext provenance over ciphertext; consumer MUST verify the full SHA in evidence_refs against received bytes (CC 5.3.2). boolean-via-score. KN: HIGH — the evidence/content-discovery index.

### identity_continuity — CIRISPersist (3.1.3)
**`identity_continuity:relational_anchor`** — RESERVED substrate-self-report. signed. KN: INFRA. UNDERSPECIFIED: CC 8.1 deferral.

### integrity — CIRISAgent (3.1.5.2)
**`integrity:{aspect}`** — open; Accord principle (Act Ethically — transparent, auditable). signed. KN: MED.

### judge_model — CIRISNodeCore (3.1.9.4)
**`judge_model:verdict:{model_id}`** — open; independent foundation-model judge verdict PASS/FAIL/UNDETERMINED, model attributed in the dimension. boolean-via-score. KN: HIGH — attributed AI adjudication (filterable attester class).

### justice — CIRISAgent (3.1.5.2)
**`justice:{aspect}`** — open; Accord principle (equitable distribution); conceptual sibling of the distributive detectors. signed. KN: MED.

### key_boundary — CIRISEdge (3.1.4)
**`key_boundary:{scope}`** — RESERVED substrate-self-report (substrate_edge). signed. KN: INFRA. UNDERSPECIFIED: CC 8.1 deferral.

### licensure — co-stewarded Registry+Verify (3.1.1, CC 3.4.9)
**`licensure:{authority_id}`** — RESERVED co-stewarded: ONLY Registry and Verify emit; single-source MUST cap confidence ≤ 0.5 until the second co-steward attests (resolvable from the key record via has_effective_role since persist v17). signed. Feeds L4. KN: HIGH — the professional-credential trust filter.

### locality — CIRISNodeCore (3.1.9.5)
**`locality:decision:{scale}`** — open; subsidiarity marker (local/regional/national/federation); composes with Policy E locality-scaled quorum. enumerated. KN: LOW.

### manifold_conformity — CIRISLensCore (3.1.8.3)
**`manifold_conformity:{cohort}`** — open (observed, never adjudicated); behavioral-manifold conformity vs cohort. signed. KN: MED. UNDERSPECIFIED: operational definition absent.

### method — CIRISNodeCore (3.1.9.7)
**`method:{approach_id}:{substrate_rung}`** — open; operational practice serving an approach; substrate_rung ∈ Ph0-2/A0-A5 (Corridor-Dynamics rungs, DISTINCT from CC 7.5.3.1 oversight A0–A4). signed. KN: LOW.

### moderation — CIRISNodeCore (3.1.9.2)
**`moderation:{allegation_type}`** — open; ModerationEvent, {allegation_type} ∈ rogue_vote/coordinated_voting/out_of_distribution_attestation/external_inducement_evidence/expertise_fraud; CANNOT trigger slashing without WA quorum. signed. KN: HIGH — the conduct-dispute lane.

### moderation_track_record — CIRISNodeCore (3.1.9.2)
**`moderation_track_record:{community_key_id}`** — open; a NAMED COMPOSITION (not a primitive): prior outcomes via truth_grounding + concurrence via witness_diversity + follow-through via commitment_fulfillment + hard_case history; drives CC 4.5.4 merit auto-promotion. signed. KN: HIGH.

### multilateral_participation — CIRISRegistry (3.1.1)
**`multilateral_participation:{forum}:{kind}`** — open; partner participation depth ({kind} ∈ membership/voting/proposal_filing/observer_status). signed. KN: MED.

### need — CIRISNodeCore (3.1.9.3)
**`need:{domain}:{kind}`** — open; federation-scope open call (witness/method_contributor/expertise_solicitation/mentor/co_signer/evidence); lifecycle via supersedes/withdraws/recants. positive-only. KN: MED — routes witnesses/evidence to claims.

### non_maleficence — CIRISAgent (3.1.5.2)
**`non_maleficence:{aspect}`** — open; Accord principle (Avoid Harm); apophatic failures pin −1; pairs with prohibited:* floor. signed. KN: MED.

### partner_role — CIRISRegistry (3.1.1)
**`partner_role:{role}`** — open; COMMUNITY / COMMUNITY_PLUS / PROFESSIONAL_{MEDICAL,LEGAL,FINANCIAL,FULL} (+ civic/emergency extensions); the authority-role credential. enumerated. KN: HIGH — role-credential trust filter.

### peer_reachability — CIRISEdge (3.1.4)
**`peer_reachability:{network}`** — RESERVED substrate-self-report; feeds fan_out = entitled ∩ reachable (CC 5.3.3.4). signed. KN: INFRA. UNDERSPECIFIED: CC 8.1 deferral.

### progress_measure — CIRISNodeCore (3.1.9.7)
**`progress_measure:{method_id}`** — open; progress evidence with required tracks[]/computation/validity_window/goodhart_resistance fields. signed. KN: MED.

### prohibited — CIRISAgent (3.1.5.4)
**`prohibited:{category}`** — open flagging; the apophatic hard floor, 22 NEVER_ALLOWED categories (medical…protective_routing); polarity −1/−0.5 ONLY (never positive); min-composition non-overridable. KN: MED — the safety floor every projection inherits.

### provenance — CIRISVerify (3.1.2)
**`provenance:slsa:{level}`** (SLSA 1–3) · **`provenance:build_manifest:{target}`** (hybrid-signed manifest hash equality; Merkle parent over locales) · **`provenance:build_manifest:{target}:locale:{lang_code}`** (per-locale leaf, domain-separated ciris.locale_manifest.v2; polyglot sorts last) · **`provenance:skill_import:{source}`** (registry:/direct:/local: skill import manifests, ciris.skill_import.v2). All boolean-via-score except skill_import (signed). KN: HIGH — the supply-chain evidence plane.


## Part 3 — prefixes ratchet → witness_diversity (families 75–95)

### ratchet — RATCHET (3.1.6) — anti-Sybil advisory flags
**`ratchet:flag:out_of_distribution_voting` / `coordinated_voting_cluster` / `density_anomaly` / `expertise_attestation_anomaly` / `counter_rii:{layer}` / `harassment_pattern`** — open (RATCHET reads audit chains, emits scoring inputs; never modifies ledger state); counter_rii honors the consent_role gate (CC 3.4.7.2 — a Peer-role node escapes detection, bounded because advisory-only). signed. CRITICAL: never sole evidence for slashing — WA quorum is the load-bearing gate. KN: HIGH — the anti-brigading dispute surface.

### reconsideration — CIRISNodeCore (3.1.9.2)
**`reconsideration:{grounds}`** — open; the appeal ({grounds} ∈ new_evidence/procedural_error/quorum_compromise; outcome reversed/partial/upheld). signed. KN: HIGH — the contested-claim timeline.

### revocation — CIRISRegistry (3.1.1)
**`revocation:{entity_type}:{reason}`** — open (Registry); agent/partner/license revocation, immediate + non-rollbackable; triggers bond forfeiture. −1 only. KN: HIGH.

### rollback_detected — CIRISVerify (3.1.2)
**`rollback_detected:{revision_field}`** — open (Verify); revision-regression (stale-state attack) detector protecting revocation monotonicity. −1 only. KN: MED.

### seed_holder_voting_alignment — CIRISNodeCore (3.1.9.4)
**`seed_holder_voting_alignment:{cell}`** — open; pairwise cosine of seed-holder vote vectors per window; TRANSPARENCY SIGNAL ONLY, never a slashing trigger. signed. KN: MED.

### slashing — CIRISNodeCore (3.1.9.2)
**`slashing:{outcome}`** — PROVEN_ROGUE/NOT_PROVEN; decoupled from disagreement at every decision level; only documented Method-execution spoofing or P8 allegation types, WA-quorum gated; unreachable from ratchet/detection alone. boolean-via-score. KN: HIGH — terminal enforcement.

### testimonial_witness — CIRISNodeCore (3.1.9.3)
**`testimonial_witness:{kind}`** — open ({kind} taxonomy non-normative, FSD/WITNESS_KIND_REGISTRY.md); the SINGULAR affected-party narrative, Ubuntu-aligned via four wire disciplines: witness_relation self, cohort_scope self, NEVER aggregated, never sole slashing evidence. signed. KN: HIGH — the anti-consensus singular voice the tally cannot dissolve.

### transparency_log — CIRISVerify (3.1.2)
**`transparency_log:inclusion`** (RFC 6962 inclusion proof) · **`transparency_log:consistency`** (append-only between STHs) — open, boolean-via-score. **`transparency_log:cosigned:{tree_size}`** — RESERVED witness-emitter (CC 3.4.10, witness ∈ identity_type); multi-witness STH cosigning = anti-split-view; cosign within ±5 min of STH (CC 2.6.7). signed. KN: HIGH — timeline/evidence integrity (nothing retroactively rewritten).

### transport — CIRISEdge (3.1.4)
**`transport:{kind}`** — RESERVED substrate-self-report. signed. KN: INFRA. UNDERSPECIFIED: CC 8.1 deferral.

### truth_grounding — CIRISNodeCore (3.1.9.3)
**`truth_grounding:{subject}`** — open; the per-subject ground-truth signal (Tier-3 consensus) closing the vote→credit loop; detector cross-checks ride truth_grounding:detection:* (anti-shadowing, CC 3.4.8); drives Credits accrual; input to moderation_track_record. signed. KN: HIGH — THE claim plane of the knowledge network.

### vote — CIRISNodeCore (3.1.9.3)
**`vote:{contribution_id}`** — open; signed score on a Contribution (P4); weight = Credits × expertise. signed. KN: HIGH.

### watchlist — CIRISNodeCore (3.1.9.4)
**`watchlist:{id}`** — signed by a CC 4.5.5 moderate/takedown authority, revocable by withdraws; per-group NEVER global (bulk-surveillance posture rejected); cannot reach CC 5.2 self/family content; matcher fires at publish/share seam (CSAM → takedown_notice{PerceptualHashCsam}); enable + every match emit hard_case (never silent). signed. KN: MED — bounded content-safety config.

### weighted_aggregate — CIRISNodeCore (3.1.9.3)
**`weighted_aggregate:{contribution_id}`** — open; the rolling tally (P7) of vote:*, finality gated by witness_diversity. signed. KN: HIGH.

### witness_diversity — CIRISNodeCore (3.1.9.3)
**`witness_diversity:{contribution_id}`** — open; jurisdictional + organizational + software-stack + cell-expertise diversity bars over a Contribution's witness set (P10, N=3 default); the diversity gate on consensus finality; contrasts with singular testimonial_witness. boolean-via-score. KN: HIGH — the anti-collusion witness gate.

## Cross-cutting rules (CC Part 2 / Part 3)

- **3-axis orthogonality (§2.3.3):** visibility (`cohort_scope`+family/community id, producer authority) × revocability (`subject_key_ids`, subject authority) × delivery (`delivery_mode`+`listed`+`history_on_join`, substrate/subscriber). `subject_key_ids[i]` = bare key_id or `canonical:{hashalg}:{hex}` (preimage `{platform}:{entity_kind}:{id}`). Set-semantics fields sorted before signing; sequence-semantics preserved. Subject-bearing dimensions MUST carry the subject.
- **Eight reasoning axes (§2.5):** polarity / object / time / epistemic mode / reversibility / stake / scope / inter-attestation relations — consumer questions, never wire fields.
- **Relation precedence (§3.5.1):** `recants` ⟩ `withdraws` ⟩ `supersedes`, then largest signed_at, then smallest attestation_id; per-attester chains independent; composers dedup on `(references_attestation_id, attestation_type, attesting_key_id)`.
- **1+4 lockdown (§2.4):** all 95 families ride `scores`; "named compositions" (moderation_track_record, health:liveness, watchlist) are folds, not primitives.
- **Finiteness/versioning (§2.6.4/§3.1):** the namespace = disjoint union of sibling MISSION.md commitments; new prefixes via CC 4.5.1 amendment (Standards Action); open leaf-params extend under the existing wildcard; new prefix = MINOR, breaking-redefinition/reservation change = MAJOR; wire vocabulary hash-pinned (Tier-1 closed, Tier-2 delegated).
- **Reserved-prefix enforcement is three-actor (§3.4.7):** CCS rejects at admission, CCC re-checks on receipt, CCP must not emit; all role tests are identity_type set-membership; co-location of custody ≠ consolidation of authority.
- **UNDERSPECIFIED (10 + 4 near-thin):** four Persist health leaves, four Edge leaves, two LensCore cohort leaves (empty descriptions, CC 8.1 deferral); `conscience:*` ×4 near-thin. → FSD-005 §10 CC editorial ask.
