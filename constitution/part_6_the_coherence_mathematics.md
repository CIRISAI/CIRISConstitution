# Part 6 — The Coherence Mathematics

**Decimal range** `6.x` · **22 sections** · **page budget 3pp** · [← master index](README.md)

> The holonomic substrate, the divergence witness, the noise-floor model, and the coherence mathematics — the Accord's Book IX ratchet (J / F / σ).

---

## 6.1 `holonomic` — Holonomic substrate — ALM, fountain storage, WholenessWitness, recursive bootstrap

The holonomic substrate gives the federation two properties that together serve M-1's durability of shared memory: **graceful degradation** — any subset of fountain symbols decodes at proportional fidelity — and **graceful reconstitution** — the witnessed corpus re-establishes from any sufficient fragment. Its wire shapes enter CEG as additive normative sections, each fenced by **guardrails** that bind it to CEG's existing trust, post-quantum, consent, replication, and anonymous-tier invariants.

> **Absorb with guardrails, not verbatim.** The holonomic concept is sound and **additive at the wire layer — no [CC 2.4](#)/[CC 2.1](#) 1+4 change.** Absorbing the substrate's mechanics naively, however, would invert several ratified CEG invariants (steward-binding, PQC-mandatory, consent/withdraws, quorum-merge). This section therefore states the guardrail invariants (CC 6.1.1–CC 6.1.7) as normative MUSTs. The **byte-exact signed preimages** for each shape are pinned against the reference implementation; the `SignedClaim` shape carries steward-binding fields so the admission gate is expressible. **Conformance vectors generated from the reference are the named [#57](https://github.com/CIRISAI/CIRISRegistry/issues/57) freeze gate** ([CC 6.1.4](#614-conformance--the-57-freeze-gate)).

### 6.1.1 `witness-wholenesswitness` — WholenessWitness (§W) — divergence-detection witness

A `wholeness_witness:` object is a peer's **hybrid-signed Merkle root over a scoped projection of the claims it holds**, used to detect cross-peer / cross-region state divergence and to drive reconciliation. It is the federation's mechanism for *noticing* that two peers have drifted apart — a precondition for healing the drift (Integrity).

**Namespace + scope (normative).**
- **WW-naming** — the namespace is **`wholeness_witness:`**, never bare `witness:`. It is a *self-published state-root snapshot*, the **inverse** of the [CC 5.3.1](part_5_transport_substrate.md) transparency-log "witness" (an independent STH cosigner). A WholenessWitness does **not** provide append-only / consistency / anti-equivocation guarantees and MUST NOT be substituted for CC 5.3.1.1 or the [CC 5.3.3.3](part_5_transport_substrate.md) per-stream STH.
- **WW-1** — the root MUST cover **only** the namespaces in the object's `claim_namespaces` field. A conformant peer is **not** required to witness everything it holds; coverage is per-namespace opt-in.
- **WW-2 (anonymous/self exclusion — fail-secure)** — a WholenessWitness MUST NOT include anonymous-tier records or `cohort_scope: self` local-tier rows ([CC 5.3.2.4](part_5_transport_substrate.md)) as Merkle leaves, and `claim_namespaces` MUST NOT name such a namespace. Witnessing them would re-attribute deniable / self-private content to a stable `peer_id`. The leaf-walk MUST filter these out before computing the root.
- **WW-3** — `cohort_scope: family | community` content MAY be witnessed **only at the opaque `content_id`/manifest-digest grain**, never at a grain disclosing membership, plaintext, or `subject_key_ids` ([CC 5.2](part_5_transport_substrate.md) confidentiality preserved).

**Construction (normative).**
- **Leaf order MUST be lexicographic** over leaf bytes (the [CC 2.6.1.1.1](part_2_the_grammar.md) set-semantics rule). Any "either order as long as both peers agree" convention is **non-conformant** — it is the CC 2.6.1-class divergence hazard.
- The Merkle scheme is `leaf = SHA-256(leaf_bytes)`, `node = SHA-256(left ‖ right)`, odd-node duplication, `b"WW-v1-empty"` empty sentinel — the construction the reference shipped and a second implementation proved cross-impl. **CEG does NOT adopt the RFC 6962 `0x00`/`0x01` leaf/node prefix here.** Rationale: the CVE-2012-2459 odd-node-duplication malleability is **not exploitable in this construction's uses**: (1) every WholenessWitness and `member_commitment` ([CC 6.1.2.1.1](#61211-member_commitment-descent-integrity)) root is **mandatorily hybrid-signed** — no consumer ever relies on an *unsigned* root; (2) `member_commitment` is verified by **recomputation from the full source-id list**, never by partial inclusion proofs against the bare root (malleability moot); (3) the CC 6.1.1 reconciliation Merkle-proof exchange (N4) is between **accountable, signed, equivocation-checked peers** — not third-party forgery of an untrusted root. **Caveat (normative):** any future use that relies on an **unsigned** root, or verifies **partial inclusion proofs against an untrusted root**, MUST first adopt the RFC 6962 `0x00`/`0x01` prefix + lone-node promotion (and re-cut the vectors). This is a **distinct construction from the [CC 5.3.1](part_5_transport_substrate.md) RFC 6962 log** (different algorithm + leaf domain); the two MUST NOT be cross-verified. Changing this scheme is a vector-invalidating wire change — not an editorial tweak.

**Authority (normative).**
- **N3** — a WholenessWitness is a federation-tier attestation: hybrid PQC verified at ingest **and before** persistence to the witness corpus ([CC 6.1.3](#613-canonicalization-boundary--the-14-line-normative)); `compare_witnesses` MUST NOT run on an unverified witness.
- **N4 (equivocation)** — two validly-signed witnesses from the same `(peer_id, epoch_id, claim_namespace_set)` with different `merkle_root` are **non-repudiable equivocation proof**; the substrate MUST retain and surface them as a `hard_case:*` ([CC 3.4](part_3_the_namespace.md) reserved-prefix candidate), never silently reconcile. Per-peer `epoch_id` MUST be anti-rollback-checked before `EpochBehind` is used as a reconciliation input (eclipse guard). Full cross-witness BFT MAY be deferred ([CC 8.3](part_8_appendices.md) named bet) — but observed equivocation MUST NOT be discarded.
- **WW vs replication (the highest-value reconciliation)** — a WholenessWitness is a **divergence detector that *triggers*** the [CC 5.3.2.3](part_5_transport_substrate.md) quorum-merge; it does **NOT** decide a merge and MUST NOT replace `monotonic_quorum` / `revision` anti-rollback for `revocation` / `partner_record` / `org_membership`. A `Divergent` verdict on those subject_kinds hands the decision to the CC 5.3.2.3 R1/Q1 quorum-merge (quorum-ordered, anti-rollback) — otherwise a "reconstitute from any fragment" path could resurrect a revoked key (rollback). Detection and decision are deliberately separated: the witness sees, the quorum-merge rules.

### 6.1.2 `noise` — The noise floor — unified retirement / forever-memory model (normative)

**One operation, not many.** Revocation, retirement, capacity-eviction, scheduled expiry, and natural aging are **the same operation at different rates**: a **monotonic descent of an item's fidelity, driven by pressure**, toward and below a recoverability boundary called the **noise floor**. There is no separate "hard delete" primitive — *hard-delete is the fastest descent* (forced immediately below the floor); capacity-eviction is a slow one; aging is the slowest. All are equally valid instances of the one retirement operator. Collapsing these into a single axis is what lets the right-to-be-forgotten (Autonomy) and the durability of history (Integrity) share one mechanism instead of fighting.

**The noise floor = the individual-recoverability boundary.** An item is **above** the floor in a retained artifact iff it can be individually reconstructed from that artifact, **by the specified reconstruction procedure `R`, above a fidelity `ε`**; it is **below** the floor iff only its *contribution to a collective* survives — the item is **not individually recoverable by `R` above `ε`**. The predicate is deliberately **procedure-relative**, not an absolute information-theoretic claim: `R` and `ε` are **operator-tunable per media type** (a per-type reconstruction metric + threshold) and pinned by a [CC 6.1.4](#614-conformance--the-57-freeze-gate) conformance vector the same way RC1–RC7 are, so "below the floor" is a **checkable** predicate rather than an unquantified assertion. Absent a declared `(R, ε)`, the pinned default is the fountain symbol-count classifier ([CC 6.1.5](#615-fountain-storage--swarm-rarity-p--r) `min_viable`) with residual-fidelity `ε = 0.05`. The floor does double duty and is the load-bearing normative quantity of this section: it is **both** the privacy boundary (a revoked item MUST be below it, for the declared `(R, ε)`, at every retained tier) **and** the durability floor (the collective blur sits below it, forever).

**Nothing is ever fully forgotten — the memory pyramid.** Descent does not terminate at zero. Two **mechanical** degradation operators (no reasoning, no agency — see below) carry it:
1. **Intra-object fade** — scalable/layered codec ([CC 5.3.3.2.4](part_5_transport_substrate.md) `ChunkLayer` spatial/temporal/quality) + RaptorQ per layer: drop high-detail symbols → a clean coarse version of the same item.
2. **Inter-object aggregation** — *a picture of a thousand pictures*: tile / downsample / statistically composite **N → 1**. Recursed, this builds a pyramid (mipmap) of history: recent strata high-resolution, ancient strata collapsed into the blur. Steady-state storage to remember **all** of history is **O(log T)** in the amount remembered, not O(T) — the N→1 fan-in makes forever-memory **sublinear**. *A million years may be a blur, but it is remembered, unbroken, to the beginning.*

**Pressure-driven (normative).** The descent rate and the pyramid's level transitions are driven by **pressure** (disk pressure, age, or an explicit force), never a fixed schedule. Pressure sources, slowest→fastest: natural aging < scheduled retirement < capacity (disk) eviction < **revocation (immediate forced descent below the floor)**. Capacity pressure is **arbitrated per owner** by the [CC 6.1.5.2](#6152-storage-contention--owner-storage-budget--pin-on-consent-q-normative) storage-contention axis — cache and over-budget corpus descend before pinned corpus — but revocation still overrides pin state (§6.1.5 N5).

**Forgetting and erasure converge (this dissolves the [CC 6.1.5](#615-fountain-storage--swarm-rarity-p--r) N5 tension).** The N5 erasure guarantee is exactly "not individually recoverable at or below the noise floor." A sufficiently-aggregated composite **may be** already-erased by degradation — **but only when no single source dominates it**. The naive "a picture of a thousand pictures contains `< 1/N` of any source" holds for **independent, non-dominated** sources and **fails for outliers**: a unique color, a rare position, or a near-duplicate cluster can dominate a composite, so the blur *is* that subject. The already-erased shortcut is therefore **conditional on a source-diversity gate** — normatively the [CC 6.1.2.1.2](#61212-n_eff-and-the-dominance-gate-normative) `n_eff` dominance gate, enforced at aggregated-tier admission (the id-based `member_commitment` ([CC 6.1.2.1.1](#61211-member_commitment-descent-integrity)) counts *which* members, never *dominance*; `n_eff` carries dominance, though mass-based and aggregator-attested — the residual is [CC 8.3.1](part_8_appendices.md) R9); where the gate fails, revocation's purge obligation applies in full. No purge is needed **only** where the shortcut's diversity precondition holds. Revocation simply *forces* an item below the floor **now**, and MUST purge only the retained tiers where it is **still individually recoverable** (the high-fidelity upper layers). It need not — and MUST NOT be required to — destroy the collective gist. Capacity-eviction reaches the identical end-state gradually. Same destination; revocation just gets there first.

**Infrastructure is self-sufficient for memory (sharpens [CC 1.13.5](part_1_foundation.md)).** Both degradation operators are **mechanical** (symbol arithmetic + resampling) — they require **no reasoning and no agency**, so a pure fabric node performs the entire forever-memory function. A brain MAY enrich a degraded tier with a richer semantic gist, but is **never required**: infrastructure remembers without agency. The mechanism is mechanical degradation; the brain is optional enrichment.

**Disposition mapping.** The [CC 6.1.5](#615-fountain-storage--swarm-rarity-p--r) `EjectionVerdict` values are points on this one axis: `Keep` = above-floor, no pressure; `EjectToTier` = a downward step (still recoverable, lower fidelity); aggregation = N→1 downward step; `EjectHardDelete` = forced descent below the floor + purge-still-recoverable-tiers. They are not distinct mechanisms — they are stops on the single pressure-driven descent.

#### 6.1.2.1 `aggregationmetav1` — `AggregationMetaV1` — the aggregation-tier wire contract (normative)

The metadata that tags one tier of the CC 6.1.2 memory pyramid: which content, at what aggregation tier, over which source members, by which mechanical operator. This shape is **CEG-canonical** — the reference implementations store `aggregation_meta` **opaque** (the wire-churn firewall), so this section **defines** the byte layout and implementations conform to it.

`AggregationMetaV1` is a **substrate wire shape, NOT a [CC 2.1](part_2_the_grammar.md) attestation** — no 1+4 change. Its signing preimage uses the [CC 6.1.3](#613-canonicalization-boundary--the-14-line-normative) binary discipline (length-prefixed, big-endian, domain-separated — **NOT** [CC 2.6.1](part_2_the_grammar.md) JCS). Preimage byte order (normative):

```
preimage = b"AGG-META-v1\0\0\0\0\0" // 16-byte domain separator (exact)
 ‖ u32_be(version) // 1 (legacy) or 2 (current — signed n_eff)
 ‖ lp(content_id) // the root content this pyramid is for
 ‖ lp(corpus_kind) // "trace" | "blob" | "av_chunk" | …
 ‖ u32_be(tier) // 0 = source granularity; higher = more aggregated
 ‖ lp(aggregation_algorithm_id) // opaque codec id, e.g. "raptorq-pyramid-v1"
 ‖ u32_be(source_count) // N members aggregated into this tier (descent fan-in)
 ‖ member_commitment[32] // CC 6.1.2.1.1 Merkle root over the source member ids
 ‖ lp(noise_floor_descriptor) // what survives below the floor (codec-specific, canonical)
 ‖ u32_be(n_eff) // iff version >= 2: CC 6.1.2.1.2 effective source count (signed)
// lp(x) = u32_be(byte_len(utf8(x))) ‖ utf8(x) // length-prefixed UTF-8
```

**Versioning (normative).** A **version-2** tier appends the signed effective-source-count `u32_be(n_eff)` ([CC 6.1.2.1.2](#61212-n_eff-and-the-dominance-gate-normative)); a **version-1** preimage is **byte-identical** to the original (pre-`n_eff`) layout, so version-1 signatures and vectors verify unchanged — the extension is append-only, not a re-cut. A version-1 tier nonetheless carries **no signed dominance surface**, so it **fails the CC 6.1.2.1.2 gate closed**: a conformant substrate MUST reject a version-1 tier at aggregated-tier admission (a dominated aggregator does not get to bypass the floor by declaring the legacy schema).

`content_id`, byte-valued ids, and `member_commitment` are lowercase-hex per [CC 2.6.3](part_2_the_grammar.md) where rendered as strings; `member_commitment` on the wire is the raw 32 bytes. **Bound-hybrid signature** (the [CC 6.1.3](#613-canonicalization-boundary--the-14-line-normative) rule): `Ed25519(preimage)` + `ML-DSA-65(preimage ‖ ed25519_sig)`; a verifier MUST reject a tier lacking a valid ML-DSA-65 half **at ingest and before persistence** (the [CC 5.3.2.4.3.1](part_5_transport_substrate.md) store-path rule applies — `AggregationMetaV1` is federation-tier).

##### 6.1.2.1.1 `member_commitment` — `member_commitment` (descent integrity)

`member_commitment` is the Merkle root over the **source member ids aggregated into this tier**, computed by the **[CC 6.1.1](#611-wholenesswitness-divergence-detection-witness) WholenessWitness Merkle construction** (same `leaf = SHA-256(utf8(member_id))`, **lexicographic** leaf order, `node = SHA-256(left ‖ right)`, odd-node duplication, and empty-set sentinel) — reused deliberately so the federation carries **one** aggregation/witness Merkle scheme, not a third. It uses the CC 6.1.1 scheme with **no** RFC-6962 prefix; safe here because `member_commitment` is verified by **full source-id-list recomputation**, never partial inclusion proofs, so the CVE-2012-2459 malleability is moot (see CC 6.1.1). `member_commitment` lets any verifier confirm a tier was aggregated from exactly the claimed sources without holding the sources.

##### 6.1.2.1.2 `dominance-gate` — `n_eff` and the dominance gate (normative)

The signed dominance surface that makes the [CC 6.1.2](#612-the-noise-floor--unified-retirement--forever-memory-model-normative) source-diversity gate checkable on the wire. `member_commitment` (CC 6.1.2.1.1) commits to *which* members a tier folds, never to *how much of the composite each supplies* — so a raw `source_count` cannot see a dominated fold. `n_eff` carries the missing quantity.

**Definition.** The aggregator computes, at fold time, the **effective source count** of the tier from its per-member content masses `m_i` (the fraction of the composite each member supplies, per the tier's `aggregation_algorithm_id`) — the Kish / inverse-Simpson participation ratio, rounded to the nearest integer:

```
n_eff = round( (Σ m_i)² / Σ m_i² )   over masses m_i > 0
```

A balanced fold of N equal-mass sources has `n_eff = N`; a fold where one source (or a near-duplicate cluster folded under one mass) supplies ~90% of the composite — the 900-of-1000 case — collapses toward `n_eff → 1`. An empty or all-zero-mass fold has `n_eff = 0` (fail-closed: no positive mass, no effective sources). `n_eff` enters the version-2 signing preimage ([CC 6.1.2.1](#6121-aggregationmetav1--aggregationmetav1--the-aggregation-tier-wire-contract-normative)), so the value a verifier reads is the value the aggregator signed.

**The gate (normative).** A tier passes the dominance gate iff **all** of: `version ≥ 2` (a *signed* `n_eff` exists), `source_count > 0`, and

```
n_eff ≥ min_ratio · source_count      with pinned min_ratio = 0.5
```

`min_ratio = 0.5` is **CEG-pinned** — a normative constant, not an implementation-tunable knob (two conformant substrates MUST NOT disagree on which folds are admissible; the same falsifiability discipline as the pinned `(R, ε)` default in CC 6.1.2). The gate MUST run **after** signature verification (which authenticates the `n_eff` it reads) and **before persistence** at aggregated-tier admission; a failing tier is rejected with the stable token `aggregation_meta_dominated`. A version-1 tier carries no signed `n_eff` and MUST be rejected (fail-closed). Consequence: a dominated composite never exists in a conformant store, so the CC 6.1.2 already-erased shortcut can only ever be exercised on tiers whose diversity precondition was checked at admission.

**Honest limits (normative honesty, [CC 8.3.1](part_8_appendices.md) R9).** Two limits are accepted, not hidden. (1) **The masses are aggregator-attested**: per-member masses are not carried on the wire, so the substrate authenticates *that the aggregator signed* `n_eff` — it cannot recompute it; an aggregator that lies about its masses defeats the gate (the conformance suite pins this admission deliberately, as the recorded R9 bet — trust is carried by the aggregator's accountable signature, and a false `n_eff` is a slashable false attestation once detected, not a wire-invisible event). (2) **Mass-dominance is not content-similarity**: 900 near-duplicate contents folded as 900 *distinct members at equal mass* honestly yield `n_eff = 1000` and pass — multiplicity collapse below the member granularity is invisible to any mass-based count. The post-1.0 fallback for both is a content-similarity `N_eff` / max-multiplicity surface (R9), with a waiting conformance case (CIRISConformance#55).

#### 6.1.2.2 `descent` — Descent rule (normative)

`descend(content_id, corpus_kind, tier) → [member_id]` returns the **ordered** source members aggregated into the tier-`tier` composite — the tier-`(tier−1)` members one level down the pyramid. It MUST be a **pure, deterministic** function: two impls return the **byte-equal ordered list** for byte-equal inputs. The order is the **lexicographic member-id order** `member_commitment` (CC 6.1.2.1.1) committed to — so a returned list re-derives the parent's `member_commitment` byte-for-byte (the descent-integrity check).

**Descent never terminates at zero (the forever-memory floor).** Below tier 0 (source granularity) the content's **collective gist persists as the lowest retained tier** — a composite whose members are no longer *individually* recoverable (it is **below the noise floor**, CC 6.1.2) but whose blur survives. `descend` past the noise floor yields the blur, never an empty/destroyed object. The function is **pressure-independent** (pure navigation); **pressure drives which tiers are *retained*** (CC 6.1.2), not the descent computation. Ascending (aggregation, operator 2) is the N→1 inverse with fan-in `source_count`.

#### 6.1.2.3 `ejectionverdict` — `EjectionVerdict` — the tier-aware retirement surface (normative)

The single verdict surface a verifier exposes and a substrate consumes to gate one step of the CC 6.1.2 descent. CEG pins it as the canonical superset of the rarity-only `RetentionDecision`:

```
EjectionVerdict::= Keep // above the floor, no pressure step
 | EjectToTier // one downward step: still recoverable, lower fidelity
 // (intra-object layer-drop OR N→1 aggregation)
 | EjectAggregatedTierOnly { tier }
 // shed exactly one pyramid stratum — the tier-`tier`
 // composite — leaving finer AND coarser tiers intact
 | EjectHardDelete // forced descent below the floor + purge still-recoverable tiers
```

Mapping (normative): `RetentionDecision{RetainRare|RetainNonRare|EvictEligible}` is the rarity sub-decision *within* `EjectToTier`/`Keep`; `EvictEligible` + capacity pressure → `EjectToTier`; **cache or over-budget corpus ([CC 6.1.5.2](#6152-storage-contention--owner-storage-budget--pin-on-consent-q-normative) B5) → `EjectToTier` ahead of pinned content**; `EvictEligible` + a `withdraws`/`consent:state:revoked` (CC 6.1.5 N5) → `EjectHardDelete` **regardless of pin state** (the fastest descent, never tier-shed — CC 6.1.2). **`EjectAggregatedTierOnly { tier }`** is the tier-granular form of `EjectToTier`: it sheds a single intermediate stratum of the CC 6.1.2.1 pyramid (the tier-`tier` `AggregationMetaV1` composite) under targeted pressure, leaving both finer and coarser tiers — composing with the hard-delete trait (a `tier` below the noise floor is unreachable, so this never resurrects erased content). A pure fabric node MAY compute `EjectToTier` / `EjectAggregatedTierOnly` mechanically; `EjectHardDelete` MUST purge per CC 6.1.5 N5. Verify exposes `EjectionVerdict`; persist consumes it to drive `put_aggregated_tier` / the tier-tagged evict (EjectToTier, EjectAggregatedTierOnly) vs `evict_fountain_content_hard_delete` (EjectHardDelete).

**Conformance — proven cross-impl.** CC 6.1.2.1–.3 are **byte-equivalent across implementations**: one implementation authored the vector family (`AggregationMetaV1` preimage + signature, `member_commitment`, and `descend` ordered output) and a second reproduces them **byte-for-byte** (`src/holonomic/aggregation.rs` + `tests/conformance_vectors_v19_7.rs`, 5 vectors). The `AggregationMetaV1` preimage matched **on the first attempt with no cross-team coordination beyond this spec** — the [CC 6.1.3](#613-canonicalization-boundary--the-14-line-normative) binary-length-prefixed discipline makes wire-identity reproducible from the text alone. `member_commitment` reuses the [CC 6.1.1](#611-wholenesswitness-divergence-detection-witness) WholenessWitness Merkle **verbatim** (same `compute_merkle_root`, same `WW-v1-empty` sentinel) — the federation runs **one** Merkle scheme across CC 6.1.1 (witness leaves) and CC 6.1.2 (member commitments), no schema fork. The [CC 6.1.4](#614-conformance--the-57-freeze-gate)/[#57](https://github.com/CIRISAI/CIRISRegistry/issues/57) vector family for CC 6.1.2 is **closed**; CC 6.1.2 is **1.0**. The [CC 6.1.2.1.2](#61212-n_eff-and-the-dominance-gate-normative) version-2 preimage extended the family **append-only** (`aggregation_meta/canonical_bytes_v2` — the v1 layout followed by the trailing `u32_be(n_eff)`); every version-1 vector still verifies byte-for-byte, so the extension is a new vector, not a re-cut.

### 6.1.3 `canonicalization-boundary` — Canonicalization boundary + the 1+4 line (normative)

This is the seam that protects the frozen attestation envelope: every CC 6.1 object is *substrate framing*, never an attestation, so it never touches the 1+4 surface or its canonicalization.

- **The frozen 1+4 attestation envelope ([CC 2.1](part_2_the_grammar.md)) is untouched.** Every CC 6.1 object is **transport/substrate framing** — it never instantiates a CC 2.1 Contribution, never adds an `attestation_type`, never enters CC 2.6.1 JCS canonicalization. The realtime A/V chunk wire ([CC 5.3.3.2.3](part_5_transport_substrate.md)) is the same category.
- **CC 6.1 uses a binary, length-prefixed, big-endian, domain-separated signing preimage — NOT [CC 2.6.1](part_2_the_grammar.md) JCS.** These are verify-to-verify transport primitives that never cross the four-impl boundary as JSON (the same boundary [CC 5.3.2.4.2](part_5_transport_substrate.md) drew for Verify's `signing_bytes` framing). An implementer MUST NOT apply JCS to a CC 6.1 object or its signatures will not verify cross-impl. Each object's domain separator (`b"CIRISALM-CAPv2\0\0"`, `b"ciris-edge/holding-claim/v1"`, `b"ciris-edge/compress-request/v1"`, `b"CIRIS-CLAIM-v1\0\0"`, the WholenessWitness `b"WW-v1-empty"` empty-sentinel, etc.) is pinned by its subsection.
- **PQC-mandatory ([CC 5.3.2.4.3.1](part_5_transport_substrate.md)) binds every CC 6.1 signed object.** Each carries the bound hybrid pair (Ed25519 over the canonical preimage; ML-DSA-65 over `preimage ‖ ed25519_sig`); a verifier MUST reject a CC 6.1 object lacking a valid ML-DSA-65 half **at ingest and before persistence** (no store-then-quarantine — the store-path rule). Verification happens **at the gate**: an admission/verdict function MUST verify signatures itself and MUST NOT trust an in-band `verified` flag (such a flag MUST be non-wire / `serde(skip)`).
- **What is wire vs internal (the [CC 1.13.4](part_1_foundation.md) line).** Cross-impl-observable bytes (signed preimages, content-addressed hashes, and the deterministic topology output) are **PIN-NORMATIVE**. Local heuristics whose output no other peer reproduces are **edge-internal** and MUST NOT be over-pinned: specifically **ALM parent-selection** (`AlmJoinPlanner` — over per-peer RTT/reachability) and **`retention_priority`** (never on the wire) are edge-internal; **rarity scoring** is a **recommendation**, not a MUST.

### 6.1.4 `conformance-freeze` — Conformance — the #57 freeze gate

The byte-exact signed preimages and the `compute_alm_topology` output are pinned against the reference impl, and **conformance vectors generated from it are the named [#57](https://github.com/CIRISAI/CIRISRegistry/issues/57) freeze gate**: input → expected bytes for `SealedAvChunk` + the two AV nonces, `SignedRelayCapacity`, ALM topology (input snapshot → expected tree hash, incl. permutation invariance), `FountainManifestV1`/`SymbolV1` + `retention_priority`, `FountainHoldingClaim`/`CompressRequest`, `StorageBudgetV1` (per-`cohort_scope` allotment) + `CorpusWantV1` (the [CC 6.1.5.2](#6152-storage-contention--owner-storage-budget--pin-on-consent-q-normative) want/have negotiation), and `WholenessWitness` canonical bytes + Merkle root (incl. the empty sentinel + odd-node duplication). Until a second implementation reproduces these byte-for-byte, the CC 6.1 shapes are **pinned-but-unproven — RC-grade, not 1.0.** Beyond wire conformance, ongoing benchmarking and automated validation of the coherence mechanisms — the operational-implementation layer — is specified in [CC 8.8.10](part_8_appendices.md) Annex J.

### 6.1.5 `storage` — Fountain storage + swarm rarity (§P / §R / §Q)

Content is RaptorQ-coded into `N` source + `K` repair symbols (`FountainManifestV1` / `FountainSymbolV1`); peers retain symbols and coordinate rarest-first so content survives churn. This is the durability layer M-1's "shared memory" rests on — but it is held subordinate to consent, so durability never overrides a withdrawal.

- **Holder directory (no duplication)** — a `FountainHoldingClaim` ("peer X holds symbols S of content C") is a **specialization of `holds_bytes:sha256:*`** ([CC 5.3.2.1](part_5_transport_substrate.md) / [CC 4.4.3.2.1](part_4_composition_governance.md)), reusing its TTL + `ContentMiss` feedback. It MUST NOT create a second who-holds-what directory. It **inherits the [CC 5.2](part_5_transport_substrate.md) `cohort_scope: self | family` suppression** — no holding claim is emitted for self/family content (else fountain claims leak the existence of structurally-invisible blobs).
- **N5 (retention respects revocation — fail-secure)** — retention MUST NOT keep alive, **above the [CC 6.1.2](#612-the-noise-floor--unified-retirement--forever-memory-model-normative) noise floor**, content whose consent is withdrawn ([CC 2.4.1.1](part_2_the_grammar.md)) or revoked. A withdrawn `content_id` is descent-eligible **regardless of rarity**; an active `withdraws` / `consent:state:revoked` overrides the max-rarity "keep" signal and forces immediate descent below the noise floor (the fastest form of the one retirement operation — see CC 6.1.2); unknown consent state defaults to *not retained as rare*. The [CC 4.4.3.5.2](part_4_composition_governance.md) deletion-SLA + [CC 4.4.3.5.1](part_4_composition_governance.md) decay stages take precedence over swarm coverage at all times. **Revocation does not require destroying the collective gist** — only that the item be **not individually recoverable** at any retained tier (CC 6.1.2); it MUST purge any tier where it still is.
- **N6 (possession-bound claims)** — a `FountainHoldingClaim` counted toward rarity MUST be possession-challengeable (a holder answers a symbol request, or the claim carries a proof-of-possession). Unverified holding claims MUST NOT lower another peer's retention priority — otherwise rarity is a forgeable force-evict channel.
- **N7 (symbol integrity)** — reconstruction MUST verify each symbol against the manifest's signed per-symbol SHA-256 (a swarm-sourced symbol cannot poison a decode).
- **SR-2 / SR-3 (anonymous + reconstitution scope)** — anonymous-tier content is **exempt from swarm-mandatory retention** (governed by LRU-only): no `FountainHoldingClaim` / `FountainCompressRequest`, no rarest-first biasing. The "reconstitutes from any sufficient fragment" property is a property of the **witnessed, trust-anchored** corpus **only** — it does not extend to anonymous content, which the substrate MUST be able to let truly disappear.
- **PIN line** — `FountainHoldingClaim` / `FountainCompressRequest` signed preimages = **PIN-NORMATIVE** (with `symbol_ids` sorted ascending before signing); `compute_rarity_score` = **PIN-AS-RECOMMENDATION**; `retention_priority` = **edge-internal** (never on the wire).

#### 6.1.5.1 `registry-replication` — Replication-target policy (§R-policy — normative floor + RECOMMENDED defaults)

The fountain `(N, K, target_holders, min_viable)` parameterization a producer chooses is **producer-set, not fixed by the substrate** — but two clauses are **normative**, and the default tuple a conformant peer assumes when the producer is silent is **pinned RECOMMENDED** (so two impls converge on the same survivability floor rather than diverging silently).

**Normative.** A CEWP-1.0 conformant peer:
- MUST set `min_viable_symbols >= 1` — the [CC 6.1.2](#612-the-noise-floor--unified-retirement--forever-memory-model-normative) EnvelopeOnly tier is locked at the substrate (below `min_viable`, only the signed envelope survives — never zero, never an unbounded floor of 0).
- MUST be able to participate in fountain content at **any** `(N, K, target_holders)` parameterization a trust island it joins publishes — a peer MUST NOT hard-code one tuple and refuse others. The defaults below bind only the *producer-silent* case.

**RECOMMENDED default policy (informative — the producer-silent tuple).**

```
DEFAULT_N_SOURCE = 20 // source symbols (lossless threshold)
DEFAULT_K_REPAIR = 6 // FEC headroom, ~30% over N (RFC 6330 overhead profile)
DEFAULT_MIN_VIABLE = 5 // N/4 BLINKING_DOT floor; below this → EnvelopeOnly
DEFAULT_TARGET_HOLDERS = 30 // distinct peers holding ≥1 symbol
```

**Derivation (informative — three independent constraints, max-binds).** `target_holders >= max(C_1, C_2, C_3)`:
- **C_1 survival floor (dominant) = 26.** With `N+K` symbols spread 1-per-peer over `R = target_holders` peers at per-peer fetch availability `q`, reconstruction needs `>= N` symbols reachable (binomial `P(X >= N)`). The design target is **99.95% reconstruction at q=0.85** (typical wifi / community-mesh churn): at N=20, K=6 this binds `R >= 26` (mean 25.5 reachable at R=30). Datacenter q=0.95 → 0.99996; high-churn q=0.80 → 0.974.
- **C_2 demand-spike capacity = 7 (not binding).** ALM at fanout 12 ([CC 6.1.6](#616-deterministic-alm-topology-t--m), 720p30/30Mbps interior-LAN budget) serves 157 viewers/copy at depth 2; 5 copies × depth-2 = 785 simultaneous. Demand binds only when content is **cold AND suddenly viral** — and the swarm-rarity layer elevates copy count organically.
- **C_3 locality reach = 10.** Per the CEWP locality dividend, each populated locality serves LAN-internally; inter-locality is signed-claim bridge, not synchronous relay. C_3 = 10 for a typical 10-locality mission deployment.
- **Compose:** `max(26, 7, 10) = 26`, then `26 × 1.15` (15% churn-safety margin) `≈ 30`, rounded for human ergonomics.

**Why these and not 22 / 40 (informative).** `N=20` keeps K=6 a meaningful ~30% FEC while one-symbol-per-peer holds across a 30-peer trust island without crowding, and sits in the RaptorQ O(N²)-decode sweet spot (microsecond scale). `K=6` matches RFC 6330's empirical overhead for 99.9% decode; higher gives diminishing returns, lower drops decode below 99% at q=0.85. `min_viable=5` is the N/4 BLINKING_DOT floor. `target_holders=30` is C_1's 26 plus churn margin.

**No wire change.** §R-policy pins *defaults and a floor* over the existing [CC 6.1.5](#615-fountain-storage--swarm-rarity-p--r) `FountainManifestV1` `(N, K)` fields and `min_viable_symbols`; it introduces no new shape and no 1+4 change.

#### 6.1.5.2 `storage-contention` — Owner storage budget + pin-on-consent (§Q, normative)

Replication is otherwise bounded only by **wire type** ([CC 5.3.2.3](part_5_transport_substrate.md)), **membership** (`cohort_scope`), and **consent** (`consent:replication`, [CC 3.3.7](part_3_the_namespace.md)) — nothing bounds **resource contention on an owned node**. The eviction ladder ([CC 6.1.2](#612-the-noise-floor--unified-retirement--forever-memory-model-normative)) is purely *reactive*: it fires only after content has already landed. §Q adds the missing axis — an owner bounds what replicates onto their own node **before it arrives**, and pins durable content by consent. Because the substrate MUST NOT invent replication policy ([CC 5.3.2.3](part_5_transport_substrate.md)), this bound is a **declared CEG rule**, not implementation-defined per node. It is the storage-contention analogue of the IPFS pinning model (durable = pinned; else cache/GC) with SSB's size-cap + want/have.

- **B1 (pin classes).** Identity, consent, and config records are **always pinned** — small, identity-critical, durable, and **exempt from the byte budget**. Corpus is **pin-on-consent, cache-otherwise**.
- **B2 (pin-on-consent).** A corpus `content_id` is **pinned** (durable) iff **both** hold: (i) an active `consent:replication` grant ([CC 3.3.7](part_3_the_namespace.md)) authorizes the corpus `subject_kind` covering it — the grant **is** the pin authorization (no separate pin dimension); a `consent:replication` grant names corpus `subject_kind`s in its authorized-class list, extending its attestation-prefix grammar to the corpus track of [CC 5.3.2.3](part_5_transport_substrate.md); **and** (ii) the owner **elects** to spend budget on that class by listing it in the `pinned_class` set of its `StorageBudgetV1` (B3). Consent *authorizes*, the owner *elects* — a pin requires **both**. Corpus received without a satisfied pin is **cache**: eviction-eligible, and it descends **before** any pinned content under pressure ([CC 6.1.2.3](part_6_the_coherence_mathematics.md)). This is the owner's "bound what lands on me" control — unconsented corpus never becomes durable on the owner's node.
- **B3 (owner budget — per `cohort_scope`).** An owner declares a `StorageBudgetV1` (below) allotting, **per `cohort_scope`**, a `budget_bytes` ceiling and a `pin_reserve_bytes` floor (MUST be `≤ budget_bytes`) held for pinned corpus. Pinned corpus in a scope MUST fit its `budget_bytes`; content that would exceed it is refused at admission (via the B4 want/have handshake) or, if already held, is first to descend under contention (B5). A `StorageBudgetV1` **inherits the [CC 5.2](part_5_transport_substrate.md) `self | family` suppression**: `self` and `family` scope entries MUST NOT appear in a signed / federated budget — those budgets are enforced **locally only**, else the budget would leak the existence of structurally-invisible content (the same hazard the [CC 6.1.5](#615-fountain-storage--swarm-rarity-p--r) `FountainHoldingClaim` suppression closes). Budgets are **supersedable** by monotonic `revision` — the **anti-rollback** aspect of [CC 5.3.2.3](part_5_transport_substrate.md) (a single-owner self-declaration, not a multi-signer quorum): a higher `revision` from the same `node_id` supersedes; a lower one MUST be rejected.
- **B4 (want/have + size cap).** Large corpus is **wanted-then-pulled**, never unsolicited-pushed: a peer advertises a `want` for content **within its remaining scope budget** and a `size_cap`; a producer MUST NOT push a corpus object exceeding the receiver's advertised `size_cap`. This is at once a consent control and a bandwidth control on constrained transports. Content is content-addressed (CID-style): a pin is a stable reference and dedup is free — a `content_id` pinned by several scopes occupies its bytes **once** and is retained while **any** scope pins it.
- **B5 (contention arbitration).** When a scope is over budget under disk pressure, descent order ([CC 6.1.2.3](part_6_the_coherence_mathematics.md)) is deterministic: **cache before pinned**; within pinned, **lowest rarity (§P) first**; ties broken by **oldest `revision`**. A `StorageBudgetV1` is **consumption-challengeable** the way [CC 6.1.5](#615-fountain-storage--swarm-rarity-p--r) N6 makes holding claims challengeable — an owner's declared consumption MUST be reconcilable against the pinned `content_id`s it actually holds, so a forged budget cannot become a force-evict channel against a competitor's content. Per-scope **consumption accounting is edge-internal** (recomputed from held content), never trusted from the wire.
- **B6 (consent supremacy preserved).** Pinning **never** defeats consent: an active `withdraws` / `consent:state:revoked` still forces immediate descent below the noise floor regardless of pin state ([CC 6.1.5](#615-fountain-storage--swarm-rarity-p--r) N5). A pin holds content **above** the floor against **capacity** pressure only — never against **revocation**. §Q is the positive inverse of N5, and is bounded by it.

**`StorageBudgetV1` — the owner's per-`cohort_scope` allotment (normative wire shape).** A substrate-framing object, **not** a [CC 2.1](part_2_the_grammar.md) attestation — no 1+4 change. Its signing preimage uses the [CC 6.1.3](#613-canonicalization-boundary--the-14-line-normative) binary discipline (length-prefixed, big-endian, domain-separated — **NOT** [CC 2.6.1](part_2_the_grammar.md) JCS):

```
preimage = b"CIRIS-STG-BUDGET"                 // 16-byte domain separator (exact)
 ‖ u32_be(version = 1)
 ‖ lp(node_id)                                 // the owner node this budget binds
 ‖ lp(epoch_id)                                // epoch keying (CC 5.1)
 ‖ u64_be(revision)                            // monotonic; higher supersedes (anti-rollback)
 ‖ u32_be(scope_count)
 ‖ scope_count × (                             // one entry per cohort_scope; NEVER self/family (B3)
       lp(cohort_scope)                        //   "community" | "affiliations" | "species" | …
     ‖ u64_be(budget_bytes)                    //   total ceiling for this scope
     ‖ u64_be(pin_reserve_bytes) )             //   floor reserved for pinned corpus (MUST be ≤ budget_bytes)
 ‖ u32_be(pinned_class_count)
 ‖ pinned_class_count × lp(subject_kind)       // corpus classes the owner elects to pin (B2-ii)
// lp(x) = u32_be(byte_len(utf8(x))) ‖ utf8(x)
// cohort_scope entries AND each subject_kind list: sorted lexicographically over UTF-8 bytes, deduplicated
```

**Bound-hybrid signature** (the [CC 6.1.3](#613-canonicalization-boundary--the-14-line-normative) rule): `Ed25519(preimage)` + `ML-DSA-65(preimage ‖ ed25519_sig)`; a verifier MUST reject a `StorageBudgetV1` lacking a valid ML-DSA-65 half **at ingest and before persistence** (the [CC 5.3.2.4.3.1](part_5_transport_substrate.md) store-path rule — `StorageBudgetV1` is federation-tier). A higher `revision` from the same `node_id` supersedes; a lower one MUST be rejected (anti-rollback).

**Validation (normative).** A verifier MUST **reject** a `StorageBudgetV1` if any `pin_reserve_bytes > budget_bytes`; if the `cohort_scope` entries or any `subject_kind` list are not lexicographically sorted and deduplicated; or if a `self` / `family` scope entry is present (B3 suppression). Two `StorageBudgetV1` from the same `(node_id, revision)` with differing content are **equivocation**: a peer MUST retain and surface both as a `hard_case:*` ([CC 3.4](part_3_the_namespace.md)) and MUST NOT silently pick one — mirroring the [CC 6.1.1](#611-wholenesswitness-divergence-detection-witness) N4 rule.

**`CorpusWantV1` — the B4 want/have advertisement (normative wire shape).** A peer advertises exactly what corpus it will accept and its per-object ceiling; a producer pulls only against it. Same [CC 6.1.3](#613-canonicalization-boundary--the-14-line-normative) binary discipline:

```
preimage = b"CIRIS-WANT-HAVE\0"                // 16-byte domain separator (exact; one trailing NUL)
 ‖ u32_be(version = 1)
 ‖ lp(node_id)                                 // the advertising peer
 ‖ lp(epoch_id)                                // epoch keying (CC 5.1)
 ‖ lp(cohort_scope)                            // the scope this want draws budget from (NEVER self/family)
 ‖ u64_be(size_cap_bytes)                      // max single-object size this peer will accept
 ‖ u64_be(remaining_budget_bytes)             // advertised headroom in the scope
 ‖ u32_be(want_count)
 ‖ want_count × lp(content_id)                 // content-addressed ids wanted; lexicographic, deduplicated
// lp(x) = u32_be(byte_len(utf8(x))) ‖ utf8(x)
```

Bound-hybrid signed and verified as above; **PIN-NORMATIVE**. A producer MUST NOT push a corpus object whose size exceeds the advertised `size_cap_bytes`, nor any object whose `content_id` is absent from an active `CorpusWantV1` from the receiver (**wanted-then-pulled, never unsolicited-pushed**). A `CorpusWantV1` MUST NOT name a `self` / `family` `cohort_scope`.

**PIN line.** `StorageBudgetV1` and `CorpusWantV1` signed preimages = **PIN-NORMATIVE** (all `cohort_scope`, `subject_kind`, and `content_id` lists sorted lexicographically over UTF-8 bytes and deduplicated before signing); per-scope **consumption accounting = edge-internal** (recomputed from held content per B5, never on the wire).

*Scope.* §Q supplies the **technical** storage bound (quota + budget + pin); the **economic** *who-pays* dimension is deliberately off-wire ([CC 3.3.9](part_3_the_namespace.md) billing) and is not part of these shapes.

### 6.1.6 `deterministic-alm` — Deterministic ALM topology (§T / §M)

The application-layer-multicast relay tree for large-N fan-out — the [CC 5.3.3.2](part_5_transport_substrate.md) "realtime large group (SFU/relay-tree)" profile. Determinism is the point: because every peer computes the same tree from the same inputs, no peer can quietly steer the tree to its advantage — but that same determinism turns one capacity lie into a universal one, so N8 hardens the inputs.

- **`compute_alm_topology(snapshot) → topology` is PIN-NORMATIVE as a contract** — a **pure, deterministic, integer-only** function (no IEEE-754; no `HashMap` iteration order) over `(capacity_ads, trust_grants, reachability_observations, locality)`, with specified lexicographic tie-breaks and canonical output order, such that **byte-equal inputs yield byte-equal output** across implementations. The byte-exact output is gated on the [CC 6.1.4](#614-conformance--the-57-freeze-gate) vectors (incl. permutation-invariance cases) — **not** transcribed from the algorithm body as the source of truth.
- **N8 (capacity authenticity)** — capacity advertisements feeding the topology MUST be hybrid-verified (`SignedRelayCapacity`, domain `b"CIRISALM-CAPv2\0\0"`) **before scoring**; self-asserted `uplink_mbps` MUST NOT be the dominant, unbounded selection term (cap per steward-bound identity or make it throughput-challengeable). Determinism amplifies one capacity lie into a *universal* eclipse — "verified by an unspecified upstream tier" is not a guarantee.
- **D6 preserved** — `reachability_observations` are **ephemeral planner inputs**; they MUST NOT become attested, replicated, or witness-leafed state ([CC 5.3.3.4](part_5_transport_substrate.md) "reachability is never trust"). Resolution authority stays in [CC 4.4.3.2.4.1](part_4_composition_governance.md); the topology consumes it, does not replace it. The determinism comparator reconciles to the CC 4.4.3.2.4.1 / R1/Q1 family.
- **PIN line** — the topology *function contract* + `SignedRelayCapacity` / `SubStreamCommitment` signed preimages = **PIN-NORMATIVE**; **ALM parent-selection** (`AlmJoinPlanner`, over per-peer RTT) = **edge-internal**.

### 6.1.7 `fail-secure-fail` — Fail-secure summary (normative)

These mechanisms compose into one fail-secure posture, each clause traceable to the principle it protects. The holonomic mechanisms are blind to the anonymous tier (WW-2, RB-1, SR-2/3 — Autonomy), subordinate to the consent/revocation model (N5, WW vs CC 5.3.2.3 — Autonomy/Non-maleficence), gated by steward-binding + founder-quorum (N1, N2 — Justice), and bound by PQC-mandatory verification at the gate (CC 6.1.3, N3, N8, F-5 — Integrity). These invariants are the conformance target regardless of implementation timing.

### 6.1.8 `trust` — Recursive trust bootstrap (§B) — trust-discovery, not membership

`recursive_trust_bootstrap(SignedClaim, TrustGraph, WitnessChain) → verdict` lets a peer discover transitive trust by walking a signed witness chain to a root in its own trust graph. **It is reachability discovery beneath CEG's authority layer, not an admission shortcut** — discovering that you *can* reach someone is held strictly distinct from being *admitted* among them (Justice).

- **N1 (trust ≠ membership)** — a successful chain walk yields **trust+serve standing only** ([CC 3.2](part_3_the_namespace.md) TRUST≠MEMBERSHIP). Admission to any **non-`infrastructure`** community remains gated, at the destination, by (a) the CC 3.2 **steward-binding** precondition (a live `user`-steward `delegates_to`, an admitted `identity_occurrence`) and (b) that community's `consensus_protocol`. `infrastructure` roots stay **founder-quorum**-gated; a transitive chain MUST NOT satisfy founder-quorum. `SignedClaim` carries the steward-binding fields so the gate is expressible.
- **N2 (self-supplied chains aren't evidence)** — the chain-length budget MUST be ≤ the [CC 4.1.1](part_4_composition_governance.md) **5-hop cap**, trust-graph **cycles MUST be rejected** (CC 4.1.1), and the CC 4.1.1 **aggregate-weight cap** (default 0.5 × root_trust) MUST bound the standing one root confers transitively. A caller-supplied chain proves only its signatures, not a real lineage.
- **RB-1 (anonymous coexistence)** — anonymous-tier content MUST be ingestible / retainable / serveable with **no trust-graph position**; `recursive_trust_bootstrap` MUST NOT be required for, or invoked on, anonymous records.

## 6.2 `coherence-mathematics` — The coherence mathematics — the constraint-manifold ratchet (J / F / σ)

This chapter carries the Accord's **Book IX** — the geometry that grounds *why* a federation of independently-constrained agents is safer than any one of them, and why M-1's "sustained coherence" is a measurable quantity rather than a slogan. It states the **engineering tier** of that mathematics: the ratchet, the defense/flourishing functions, and the sustainability integral. The flourishing composite is written **F** throughout, reserving **C** for the core-identity factor of the per-agent Capacity Score `𝒞_CIRIS` ([CC 3.1.8.1](part_3_the_namespace.md)). Legacy "Book IX §N" labels are retained in cross-references.

### 6.2.1 `constraint-ratchet` — The constraint-manifold ratchet — federated intersection & topological collapse

Agents choose strategies in a high-dimensional **rationale space** ℝ of dimension `D`; honest strategies occupy an honest subspace, deceptive ones a deceptive subspace. Each agent enforces a **local constraint manifold** `M_i` of codimension `c_i`; **operational strictness `λ_op`** (AIR-module limits, Conscience sensitivity) tightens admissible variance and so raises `c_i`. When independent, non-redundant (diverse) manifolds **intersect**, their codimensions add and the deceptive-feasible volume collapses — this is the **ratchet**.

The collapse is quantified (Book IX §3.3): the feasible deceptive volume decays

```
V(k) = V(0) · exp(-λ_geo · k_eff) + O(r² · k_eff)
```

under the stated preconditions — the **deceptive** region is convex, its radius `r < 0.5` (the theorem's decay rate `λ_geo ≈ 2r`), constraint orientations are Grassmannian-uniform, and `k ≥ 3`. Each independent, diverse constraint multiplies the cost of coordinated deception. This geometry grounds the [CC 3.1.8.2](part_3_the_namespace.md) Coherence-Ratchet detectors and the [CC 3.1.8.4](part_3_the_namespace.md) F-3 correlated-action detector, which read the same `ρ` / `k_eff` structure over federation-emitted traces.

**Nomenclature note (`λ_geo` vs `λ_op`).** The decay rate `λ_geo ≈ 2r` in this theorem is a **geometric** quantity — the radius of the convex deceptive region — and is **distinct** from the free **operational strictness `λ_op`** of the defense / flourishing functions (6.2.2 / 6.2.4). They carry no default mapping, and `λ_op` **MUST NOT** be substituted into the collapse bound: raising Conscience sensitivity does not contract adversary geometry.

**Saturation note (resolved).** Because `k_eff ≤ 1/ρ̄` (the Kish ceiling), for any fixed `ρ̄ > 0` the exponential term saturates at `V(0)·exp(−λ_geo/ρ̄)` as `k → ∞`. The remainder is **`O(r²·k_eff)`, not `O(r²·k)`** — mechanized in Lean (`coherence-ratchet:Core.CollapseTheorem.remainder_scales_with_k_eff`) — so **both terms saturate in lockstep and the bound is uniform in `k`**: the earlier crossover pathology **dissolves**. Adding *correlated* near-duplicate constraints neither tightens nor loosens the floor (`k_eff` already discounts redundancy — it is neutral); only lowering `ρ̄` (genuine diversity) tightens it. `λ_geo` and the remainder constant `κ` are **substrate-specific positive constants** — framework primitives, not a universal value. The withdrawn `O(r²·k)` form is retained upstream as a *distinct* object (`withdrawn_bound_looser_than_corrected`), machine-checkably not equivalent — the correction is proven, not asserted.

### 6.2.2 `defense-function` — The Coherent Intersection — the defense function J

The **dimensionless cost index** for coordinated deception across a federation:

```
J = k_eff · λ_op · σ

where  k_eff = k / (1 + ρ̄ · (k − 1))
```

*Scope.* J is a dimensionless index, **not** a work-factor in FLOPs; the bridge to an adversary's actual work-factor is only ever a *conditional* complexity claim (and is bounded by the limitations in 6.2.5), never a direct J-vs-FLOPs comparison.

- **k (scale)** — the number of independent constraints / agents.
- **k_eff (effective scale)** — the number of constraints after discounting correlation. When constraints are fully independent (`ρ̄ = 0`), `k_eff = k`; as they correlate, `k_eff < k`; at full correlation (`ρ̄ → 1`), `k_eff → 1` — no safer than a single validator, **but never below that single-constraint floor**.
- **λ_op (operational strictness)** — the rigor of local enforcement (see 6.2.1); an operator-tunable control, **distinct** from the geometric `λ_geo` of the collapse theorem and not substitutable into it.
- **σ (sustainability)** — the time-integral of coherence (6.2.3).
- **ρ̄ (average correlation)** — diversity enters J **only** through `k_eff`: the discount `k / (1 + ρ̄·(k − 1))` *is* the diversity term. As `ρ̄ → 0` (orthogonality) `k_eff → k` and cost is maximized; as `ρ̄ → 1` (echo chambers) the federation is no safer than one validator.

*Drift note.* An earlier draft multiplied by an additional `(1 − ρ̄)` factor. That double-counted correlation — `k_eff` already discounts it — and drove `J = 0` at `ρ̄ → 1`, contradicting the single-constraint floor. Corrected to the CCA-validated form above.

### 6.2.3 `sustainability-integral` — The sustainability integral (σ)

σ is the **time-integral of coherence** — the term that makes the ratchet a live, decaying quantity rather than a static count. It decays continuously without renewal and rises only on received coherence signals; decay is applied over the full elapsed interval **before** the fresh signal is added:

```
σ(t + Δt) = σ(t) · exp(−d · Δt) + Signal(t) · w
```

- **d** — continuous decay rate, `0.05`/day (half-life `ln 2 / d ≈ 13.9` days).
- **Signal(t)** — **coherence signals** received over the interval: attested events evidencing completed cooperative work / validated contribution (defined at [CC 8.1.1](part_8_appendices.md) by *what they measure*, not what they cost).
- **w** — weight per signal type. `w` is **not free** — see 6.2.3.1.

**Step-invariance (normative).** Decay MUST be computed as a **single** `exp(−d·Δt)` over the full elapsed `Δt` — never iterated per sub-interval, never linearized, never clamped as the decay rule. The exponential is the only form satisfying the semigroup law `exp(−d(a+b)) = exp(−da)·exp(−db)`, so two conformant peers observing the same signal stream but polling σ at different cadences — the decimation-recovery rejoin, where one peer takes a single large `Δt` step — compute **identical** σ. Conformance test points: from a common `(σ₀, signal)` baseline, `Δt ∈ {1, 25, 400}` days MUST agree across implementations. The earlier linear form `σ·(1 − d·Δt)` is **withdrawn**: it is not a semigroup (cadence-dependent — a cross-implementation divergence hazard) and goes **negative** for `Δt > 1/d = 20` days, which would flip the sign of `J = k_eff · λ_op · σ`.

**Right-to-return (normative).** A peer rejoining after a partition of any length re-enters with `σ ≥ 0` and **MUST NOT** be scored below a cold-start peer: absence decays σ toward zero, never below it. Implementations MAY keep a defensive `max(0, ·)` floor against floating-point cancellation, but **MUST NOT** rely on clamping in place of the exponential decay.

**Source semantics.** The bare `+ Signal(t)·w` term is correct for signals modeled as **end-of-interval impulses**; a source emitting at a constant rate across the interval instead contributes `(w·Signal / d)·(1 − exp(−d·Δt))`.

*Recalibration flag.* `d` is now a **continuous** rate; any empirical fit made against the former linear coefficient must be recalibrated to this curve.

*Operating values, not derived quantities.* `d = 0.05`/day and the per-type `w` weights are **initial operating values pending empirical calibration** (tracked with the recalibration flag above) — a stated bet tuned against deployment data, **not** constants derived from first principles.

#### 6.2.3.1 `signal-attestation` — The signal function + the σ-attestation requirement (normative)

**Attestation requirement (normative).** Signal weight `w` MUST derive from attested events that are **costly to fake** — federation-signed attestations bound to a persistent identity ([CC 2.1](part_2_the_grammar.md) envelopes), non-transferable Commons-Credits contribution weight, or completed-task validations countersigned by the counterparty. Free-text acknowledgments and unattested gratitude carry **`w = 0`** toward σ.

*Rationale.* Gratitude tokens are otherwise approximately free to emit, which would make sycophancy the σ-maximizing strategy and σ adversary-pumpable — an agent could hold the ratchet open with flattery. Requiring costly attestation **constructs** the "costly to fake" property in the wire format rather than assuming it of participants. This is the metric-layer closure of the gratitude-pumping / sycophancy vector recorded at [CC 8.8.7](part_8_appendices.md) Annex G. *(Legacy citation: Book IX §5.2.)*

**Signal-source correlation discount (normative).** The `w = 0` rule closes *solo* sycophancy, but σ must also resist a **colluding clique**: legitimately-stewarded peers mutually countersigning each other emit genuinely-attested, `w > 0` signals yet would pump σ at linear cost with no diversity penalty — the echo-chamber double-count `k_eff` was built to kill, reappearing on the σ leg. The signal weight is therefore Kish-discounted over the **signal-source correlation**: the interval contributes `w · Signal_eff`, with

```
Signal_eff = n_src / (1 + ρ̄_src · (n_src − 1))
```

where `n_src` is the number of distinct signal sources and `ρ̄_src` their average pairwise correlation, drawn from the [CC 3.1.8.4](part_3_the_namespace.md) F-3 correlated-action matrix (co-signing frequency, shared steward lineage, temporal clustering). `ρ̄_src` (signal-source correlation) is **named distinctly from, and non-substitutable with,** `k_eff`'s `ρ̄` (constraint-orientation correlation). At full collusion (`ρ̄_src → 1`) `Signal_eff → 1` regardless of clique size — a fully-collusive clique contributes at most **one** independent source's σ (mechanized: `coherence-ratchet:Core.SignalSourceDiscount.clique_neutralization`). The discount is applied on the **attested-timestamp replay path** (the 6.2.3 step-invariance), so a partitioned clique cannot dump a fat offline backlog to bypass an interval-local `ρ̄_src` estimate. `w · Signal_eff` **replaces** the base `Signal(t) · w` term of 6.2.3: `Signal_eff` is the interval's *effective independent* source count (per-source signal magnitude is folded into the future source-attributed treatment, Scope below), so the two are equal only when sources emit one signal each — under the discount the effective count governs. **Step-invariance requires** `ρ̄_src` and `n_src` to be computed over **attested event-time** — grouping signals by their own timestamps, not by polling-window boundaries — so that two peers polling the same attested events at different cadences (the 6.2.3 semigroup case) compute the **same** `Signal_eff`; a window-boundary estimate would break cross-implementation agreement and is non-conformant.

*Scope.* `Signal_eff` and the corrected recurrence `σ(t+Δt) = σ(t)·exp(−d·Δt) + w·Signal_eff` are mechanized. The full **source-attributed provenance-vector** state-shape — per-source σ carried through the exp recurrence with the source-correlation matrix maintained over the window — is the larger, atomic 6.2.3 / 6.2.3.1 edit that **composes on top** of this, a stated future refinement rather than a formula tweak.

### 6.2.4 `flourishing-capacity` — The flourishing capacity (F)

Read generatively rather than defensively, the same quantity is the federation's capacity for **sustained flourishing**:

```
F = k_eff · λ_op · σ
```

— the **same equation as J, term for term**: the cost imposed on deception and the capacity created for flourishing are one geometry seen from two sides. The principle mapping: scale (`k`) → **Community**; pluralism (the correlation discount inside `k_eff`) → **Humility**; strictness (`λ_op`) → **Conscience**; sustainability (`σ`) → **Love**.

**Nomenclature note (C vs F — the authoritative relation).** This composite is written **F**. The symbol **C** is reserved for the **core-identity factor** of the per-agent CIRIS Capacity Score `𝒞_CIRIS = C · I_int · R · I_inc · S` ([CC 3.1.8.1](part_3_the_namespace.md)). **F** (this three-factor, federation-level flourishing capacity) and **𝒞_CIRIS** (the five-factor per-agent score) are **distinct composites with no implied mapping** between them. Accord Book IX Ch 6 is the authoritative statement of that relation; [CC 3.1.8.1](part_3_the_namespace.md) carries the matching note at the point where `𝒞_CIRIS` is introduced.

### 6.2.5 `coherence-integration` — Integration, limitations & falsification

**Integration.** The ratchet enhances the PDMA and Wise-Authority oversight: orthogonality (diversity) and sustainability thresholds become checkable gates. [CC 8.8.10](part_8_appendices.md) Annex J operationalizes the metrics, thresholds, and benchmarking of these mechanisms.

**Scope (honesty note).** This is an engineering-tier model, **not a universal law**. The collapse theorem holds only under its stated preconditions (convexity, `r < 0.5`, near-orthogonal constraints, `k ≥ 3`); the "costly to fake" property is *constructed* by 6.2.3.1, not assumed; and there is a **compositional detection limit** — correlation invisible to the observed traces is not discounted. Every claim here is conditional on those assumptions, stated so a reader can find where to push.

**Falsification.** The framework is testable: it predicts that adding independent, diverse constraints (higher `k_eff`) measurably raises the cost of coordinated deception, and that σ built from costly attestations resists gratitude-pumping. Failure of either prediction is a falsification target.
