# Part 6 — The Coherence Mathematics

**Decimal range** `6.x` · **14 sections** · **page budget 2pp** · [← master index](README.md)

> The holonomic substrate, the divergence witness, the noise-floor model, and the coherence mathematics.

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

**The noise floor = the individual-recoverability boundary.** An item is **above** the floor in a retained artifact iff it can be individually reconstructed from that artifact above a fidelity ε; it is **below** the floor iff only its *contribution to a collective* survives — the item itself is information-theoretically unrecoverable. The floor does double duty and is the load-bearing normative quantity of this section: it is **both** the privacy boundary (a revoked item MUST be below it at every retained tier) **and** the durability floor (the collective blur sits below it, forever).

**Nothing is ever fully forgotten — the memory pyramid.** Descent does not terminate at zero. Two **mechanical** degradation operators (no reasoning, no agency — see below) carry it:
1. **Intra-object fade** — scalable/layered codec ([CC 5.3.3.2.4](part_5_transport_substrate.md) `ChunkLayer` spatial/temporal/quality) + RaptorQ per layer: drop high-detail symbols → a clean coarse version of the same item.
2. **Inter-object aggregation** — *a picture of a thousand pictures*: tile / downsample / statistically composite **N → 1**. Recursed, this builds a pyramid (mipmap) of history: recent strata high-resolution, ancient strata collapsed into the blur. Steady-state storage to remember **all** of history is **O(log T)** in the amount remembered, not O(T) — the N→1 fan-in makes forever-memory **sublinear**. *A million years may be a blur, but it is remembered, unbroken, to the beginning.*

**Pressure-driven (normative).** The descent rate and the pyramid's level transitions are driven by **pressure** (disk pressure, age, or an explicit force), never a fixed schedule. Pressure sources, slowest→fastest: natural aging < scheduled retirement < capacity (disk) eviction < **revocation (immediate forced descent below the floor)**.

**Forgetting and erasure converge (this dissolves the [CC 6.1.5](#615-fountain-storage--swarm-rarity-p--r) N5 tension).** The N5 erasure guarantee is exactly "not individually recoverable at or below the noise floor." A sufficiently-aggregated composite (a picture of a thousand pictures contains < 1/1000 of any source) is **already-erased by degradation** — no purge needed. Revocation simply *forces* an item below the floor **now**, and MUST purge only the retained tiers where it is **still individually recoverable** (the high-fidelity upper layers). It need not — and MUST NOT be required to — destroy the collective gist. Capacity-eviction reaches the identical end-state gradually. Same destination; revocation just gets there first.

**Infrastructure is self-sufficient for memory (sharpens [CC 1.13.5](part_1_foundation.md)).** Both degradation operators are **mechanical** (symbol arithmetic + resampling) — they require **no reasoning and no agency**, so a pure fabric node performs the entire forever-memory function. A brain MAY enrich a degraded tier with a richer semantic gist, but is **never required**: infrastructure remembers without agency. The mechanism is mechanical degradation; the brain is optional enrichment.

**Disposition mapping.** The [CC 6.1.5](#615-fountain-storage--swarm-rarity-p--r) `EjectionVerdict` values are points on this one axis: `Keep` = above-floor, no pressure; `EjectToTier` = a downward step (still recoverable, lower fidelity); aggregation = N→1 downward step; `EjectHardDelete` = forced descent below the floor + purge-still-recoverable-tiers. They are not distinct mechanisms — they are stops on the single pressure-driven descent.

#### 6.1.2.1 `aggregationmetav1` — `AggregationMetaV1` — the aggregation-tier wire contract (normative)

The metadata that tags one tier of the CC 6.1.2 memory pyramid: which content, at what aggregation tier, over which source members, by which mechanical operator. This shape is **CEG-canonical** — the reference implementations store `aggregation_meta` **opaque** (the wire-churn firewall), so this section **defines** the byte layout and implementations conform to it.

`AggregationMetaV1` is a **substrate wire shape, NOT a [CC 2.1](part_2_the_grammar.md) attestation** — no 1+4 change. Its signing preimage uses the [CC 6.1.3](#613-canonicalization-boundary--the-14-line-normative) binary discipline (length-prefixed, big-endian, domain-separated — **NOT** [CC 2.6.1](part_2_the_grammar.md) JCS). Preimage byte order (normative):

```
preimage = b"AGG-META-v1\0\0\0\0\0" // 16-byte domain separator (exact)
 ‖ u32_be(version = 1)
 ‖ lp(content_id) // the root content this pyramid is for
 ‖ lp(corpus_kind) // "trace" | "blob" | "av_chunk" | …
 ‖ u32_be(tier) // 0 = source granularity; higher = more aggregated
 ‖ lp(aggregation_algorithm_id) // opaque codec id, e.g. "raptorq-pyramid-v1"
 ‖ u32_be(source_count) // N members aggregated into this tier (descent fan-in)
 ‖ member_commitment[32] // CC 6.1.2.1.1 Merkle root over the source member ids
 ‖ lp(noise_floor_descriptor) // what survives below the floor (codec-specific, canonical)
// lp(x) = u32_be(byte_len(utf8(x))) ‖ utf8(x) // length-prefixed UTF-8
```

`content_id`, byte-valued ids, and `member_commitment` are lowercase-hex per [CC 2.6.3](part_2_the_grammar.md) where rendered as strings; `member_commitment` on the wire is the raw 32 bytes. **Bound-hybrid signature** (the [CC 6.1.3](#613-canonicalization-boundary--the-14-line-normative) rule): `Ed25519(preimage)` + `ML-DSA-65(preimage ‖ ed25519_sig)`; a verifier MUST reject a tier lacking a valid ML-DSA-65 half **at ingest and before persistence** (the [CC 5.3.2.4.3.1](part_5_transport_substrate.md) store-path rule applies — `AggregationMetaV1` is federation-tier).

##### 6.1.2.1.1 `member_commitment` — `member_commitment` (descent integrity)

`member_commitment` is the Merkle root over the **source member ids aggregated into this tier**, computed by the **[CC 6.1.1](#611-wholenesswitness-divergence-detection-witness) WholenessWitness Merkle construction** (same `leaf = SHA-256(utf8(member_id))`, **lexicographic** leaf order, `node = SHA-256(left ‖ right)`, odd-node duplication, and empty-set sentinel) — reused deliberately so the federation carries **one** aggregation/witness Merkle scheme, not a third. It uses the CC 6.1.1 scheme with **no** RFC-6962 prefix; safe here because `member_commitment` is verified by **full source-id-list recomputation**, never partial inclusion proofs, so the CVE-2012-2459 malleability is moot (see CC 6.1.1). `member_commitment` lets any verifier confirm a tier was aggregated from exactly the claimed sources without holding the sources.

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

Mapping (normative): `RetentionDecision{RetainRare|RetainNonRare|EvictEligible}` is the rarity sub-decision *within* `EjectToTier`/`Keep`; `EvictEligible` + capacity pressure → `EjectToTier`; `EvictEligible` + a `withdraws`/`consent:state:revoked` (CC 6.1.5 N5) → `EjectHardDelete` (the fastest descent, never tier-shed — CC 6.1.2). **`EjectAggregatedTierOnly { tier }`** is the tier-granular form of `EjectToTier`: it sheds a single intermediate stratum of the CC 6.1.2.1 pyramid (the tier-`tier` `AggregationMetaV1` composite) under targeted pressure, leaving both finer and coarser tiers — composing with the hard-delete trait (a `tier` below the noise floor is unreachable, so this never resurrects erased content). A pure fabric node MAY compute `EjectToTier` / `EjectAggregatedTierOnly` mechanically; `EjectHardDelete` MUST purge per CC 6.1.5 N5. Verify exposes `EjectionVerdict`; persist consumes it to drive `put_aggregated_tier` / the tier-tagged evict (EjectToTier, EjectAggregatedTierOnly) vs `evict_fountain_content_hard_delete` (EjectHardDelete).

**Conformance — proven cross-impl.** CC 6.1.2.1–.3 are **byte-equivalent across implementations**: one implementation authored the vector family (`AggregationMetaV1` preimage + signature, `member_commitment`, and `descend` ordered output) and a second reproduces them **byte-for-byte** (`src/holonomic/aggregation.rs` + `tests/conformance_vectors_v19_7.rs`, 5 vectors). The `AggregationMetaV1` preimage matched **on the first attempt with no cross-team coordination beyond this spec** — the [CC 6.1.3](#613-canonicalization-boundary--the-14-line-normative) binary-length-prefixed discipline makes wire-identity reproducible from the text alone. `member_commitment` reuses the [CC 6.1.1](#611-wholenesswitness-divergence-detection-witness) WholenessWitness Merkle **verbatim** (same `compute_merkle_root`, same `WW-v1-empty` sentinel) — the federation runs **one** Merkle scheme across CC 6.1.1 (witness leaves) and CC 6.1.2 (member commitments), no schema fork. The [CC 6.1.4](#614-conformance--the-57-freeze-gate)/[#57](https://github.com/CIRISAI/CIRISRegistry/issues/57) vector family for CC 6.1.2 is **closed**; CC 6.1.2 is **1.0**.

### 6.1.3 `canonicalization-boundary` — Canonicalization boundary + the 1+4 line (normative)

This is the seam that protects the frozen attestation envelope: every CC 6.1 object is *substrate framing*, never an attestation, so it never touches the 1+4 surface or its canonicalization.

- **The frozen 1+4 attestation envelope ([CC 2.1](part_2_the_grammar.md)) is untouched.** Every CC 6.1 object is **transport/substrate framing** — it never instantiates a CC 2.1 Contribution, never adds an `attestation_type`, never enters CC 2.6.1 JCS canonicalization. The realtime A/V chunk wire ([CC 5.3.3.2.3](part_5_transport_substrate.md)) is the same category.
- **CC 6.1 uses a binary, length-prefixed, big-endian, domain-separated signing preimage — NOT [CC 2.6.1](part_2_the_grammar.md) JCS.** These are verify-to-verify transport primitives that never cross the four-impl boundary as JSON (the same boundary [CC 5.3.2.4.2](part_5_transport_substrate.md) drew for Verify's `signing_bytes` framing). An implementer MUST NOT apply JCS to a CC 6.1 object or its signatures will not verify cross-impl. Each object's domain separator (`b"CIRISALM-CAPv2\0\0"`, `b"ciris-edge/holding-claim/v1"`, `b"ciris-edge/compress-request/v1"`, `b"CIRIS-CLAIM-v1\0\0"`, the WholenessWitness `b"WW-v1-empty"` empty-sentinel, etc.) is pinned by its subsection.
- **PQC-mandatory ([CC 5.3.2.4.3.1](part_5_transport_substrate.md)) binds every CC 6.1 signed object.** Each carries the bound hybrid pair (Ed25519 over the canonical preimage; ML-DSA-65 over `preimage ‖ ed25519_sig`); a verifier MUST reject a CC 6.1 object lacking a valid ML-DSA-65 half **at ingest and before persistence** (no store-then-quarantine — the store-path rule). Verification happens **at the gate**: an admission/verdict function MUST verify signatures itself and MUST NOT trust an in-band `verified` flag (such a flag MUST be non-wire / `serde(skip)`).
- **What is wire vs internal (the [CC 1.13.4](part_1_foundation.md) line).** Cross-impl-observable bytes (signed preimages, content-addressed hashes, and the deterministic topology output) are **PIN-NORMATIVE**. Local heuristics whose output no other peer reproduces are **edge-internal** and MUST NOT be over-pinned: specifically **ALM parent-selection** (`AlmJoinPlanner` — over per-peer RTT/reachability) and **`retention_priority`** (never on the wire) are edge-internal; **rarity scoring** is a **recommendation**, not a MUST.

### 6.1.4 `conformance-freeze` — Conformance — the #57 freeze gate

The byte-exact signed preimages and the `compute_alm_topology` output are pinned against the reference impl, and **conformance vectors generated from it are the named [#57](https://github.com/CIRISAI/CIRISRegistry/issues/57) freeze gate**: input → expected bytes for `SealedAvChunk` + the two AV nonces, `SignedRelayCapacity`, ALM topology (input snapshot → expected tree hash, incl. permutation invariance), `FountainManifestV1`/`SymbolV1` + `retention_priority`, `FountainHoldingClaim`/`CompressRequest`, and `WholenessWitness` canonical bytes + Merkle root (incl. the empty sentinel + odd-node duplication). Until a second implementation reproduces these byte-for-byte, the CC 6.1 shapes are **pinned-but-unproven — RC-grade, not 1.0.** Beyond wire conformance, ongoing benchmarking and automated validation of the coherence mechanisms — the operational-implementation layer — is specified in [CC 8.8.10](part_8_appendices.md) Annex J.

### 6.1.5 `storage` — Fountain storage + swarm rarity (§P / §R)

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
