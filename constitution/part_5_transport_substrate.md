# Part 5 — Transport & Substrate

**Decimal range** `5.x` · **35 sections** · **page budget 11pp** · [← master index](README.md)

> Byte-level content transport, structural invisibility, epoch keying, and delivery.

---

A wire-format attestation makes a *claim*; it does not carry the *bytes* the claim is about. Part 5 is the layer beneath the grammar: how content actually moves, who is allowed to see that it exists, how live media is sealed and rekeyed as audiences change, and how delivery is acknowledged. Two disciplines run through every mechanism here. The first is **non-maleficence / fail-secure**: a missing key, an unreachable peer, an evicted chunk all resolve to *less* access and an honest miss — never a silent downgrade to plaintext or a fabricated success. The second is **integrity through structure**: privacy and authenticity are properties the wire format *cannot violate*, not promises an operator makes. Where the rest of the Constitution says what a claim means, Part 5 says how the claim — and the bytes it points at — survive the network without losing either guarantee.

## 5.1 `epoch` — Epoch keying + cascade (normative — D2 / D3)

The stream-epoch DEK seals content **O(1)**; the per-subscriber `key_grant` cascade distributes the 32-byte epoch key **O(N)/epoch** (sender-key / Megolm shape) = [CC 4.4.3.4.1](part_4_composition_governance.md) Policy-L cascade applied to a community roster against a *rotating* key.

**PQC at rest — `wrap_algorithm: v2` MANDATORY (normative).** The epoch-DEK `key_grant` cascade MUST wrap the DEK with **`wrap_algorithm: v2 = x25519+ml-kem-768` (hybrid; FIPS 203)** — never `v1` (X25519-only). The DEK protects content that may persist indefinitely; a classical-only KEM is a harvest-now-decrypt-later exposure even though the content AEAD (AES-256-GCM, CC 5.3.3.1) and the wrap *signature* (Ed25519 + ML-DSA-65) are already PQC-safe. The hybrid KEM primitive is shipped in `ciris-crypto`; the versioned [`KEY_GRANT_V1_INFO`](https://github.com/CIRISAI/CIRISVerify/blob/main/src/ciris-crypto/src/key_grant.rs) HKDF-context rotates cleanly to the v2 context. A Consumer MUST reject a streaming epoch grant carrying `wrap_algorithm: v1`. **The v2 `wrap_algorithm` payload wire string is pinned: `x25519_mlkem768_aes256_gcm_hkdf_sha256`** (the [CC 3.3.2](part_3_the_namespace.md) vocab variant `X25519MlKem768Aes256GcmHkdfSha256`; matches `ciris-crypto` `KEY_GRANT_ALGORITHM_V2`). Producer, substrate, and every consumer MUST serialize/deserialize this exact string — a mismatch silently fails grant decode. **Full PQC envelope for streaming**: content = AES-256-GCM (symmetric, PQC-safe) · DEK wrap = X25519+ML-KEM-768 · authenticity = Ed25519+ML-DSA-65 · hashes = SHA-256 (PQC-safe) · in-transit = CC 5.3.3.5 E1 two-layer hybrid (below).

**Epoch index is monotonic, per-`stream_id`, greenfield** — a **separate addressing axis** from `key_grant.rotation_chain`:

| Axis | Addressing | Where it lives | Supersession |
|---|---|---|---|
| Content-addressed grant supersession | `(content_sha256, recipient_key_id)` | [`cirisnode_contributions`](https://github.com/CIRISAI/CIRISPersist) V054 partial indexes (planner-AND'd) | `rotation_chain` payload-level lineage (list of prior `key_grant_id`s); walked reader-side |
| Stream/epoch-addressed grant supersession | `(stream_id, epoch[, recipient])` | `federation_stream_chunks(stream_id, seq)` | Same `rotation_chain` payload-level supersession **reused on the new axis** |

⚠️ **Not pure-additive at the Persist constraint layer**: the V054 cross-column CHECK requires `key_grant` rows be content-addressed (`media_content_sha256 IS NOT NULL`). The CC 5.1 epoch-key axis with NULL `media_content_sha256` would be REJECTED by today's CHECK. Introducing the new axis requires a **parallel CHECK arm migration** at Persist (content-addressed OR stream/epoch-addressed) — a bounded constraint migration, not a pure index-add. The spec text does not claim "purely additive" at the Persist constraint layer.

**Epoch triggers (D3)** carry the forward-secrecy guarantee — once a member leaves, subsequent content is sealed under a key they cannot derive:

| Trigger | Behavior | Forward-secrecy implication |
|---|---|---|
| Member removal | **MANDATORY rotation** (coalesced per below; exempt for ungated public broadcasts per below) — the forward-only-unsubscribe enforcement | Subsequent epochs sealed under a DEK the removed member doesn't have |
| Member addition | NO rotation + Option-A catch-up per [CC 4.5.12.1](part_4_composition_governance.md) (subject to `history_on_join`) | New member gets `key_grant`s for the current epoch + (optionally) prior epochs per the `history_on_join` envelope field ([CC 2.1](part_2_the_grammar.md)) |
| Time / bytes | Optional hygiene rotation | Operator policy; default off |

**Removal coalescing.** At broadcast scale, naive per-removal rotation is unaffordable: at N = 10⁶ and realistic audience churn (~30%/hr), one rotation per departure ≈ 83 epochs/s → a flat-unicast cascade of **~3.1 Tbps — exceeding the ~2 Tbps content fan-out itself**. The substrate therefore MUST **coalesce removals**: all removals admitted within one STH cadence window **T (default 2 s, the [CC 5.3.3.6](#1054-per-stream-transparency--sth--receipts-v3-lock) equivocation-window grain)** are batched into a **single** epoch rotation covering the whole batch. This caps the rotation rate at 1/T **regardless of churn** (≤ 1,800 epochs/hr at T = 2 s → ~18.7 Gbps flat-unicast cascade at N = 10⁶, ~0.9% of content fan-out), and bounds removed-viewer exposure to ≤ T — the same grain the stream's equivocation window already accepts. A removed member's exposure window is therefore `≤ T`, never "until the next scheduled rotation."

**Public-broadcast exemption (normative).** A `live_stream` whose roster is **ungated** — `listed: public` AND grants issued to any requester without an admission ceremony — carries **no confidentiality claim against departed viewers** (anyone, including the departed viewer, can re-subscribe and receive the current DEK on request). For such streams, member removal MUST NOT force rotation (it buys nothing and costs the full cascade); the time/bytes hygiene rotation and the [CC 5.3.3.1](#1052-chunk-sealing--stream-nonce-v2-lock) nonce-space bounds still apply. Rotation-on-removal remains **MANDATORY for every gated roster** (bounded membership, admission ceremony, or any non-public `listed` state) — there the DEK *is* the access-control boundary and the forward-only-unsubscribe guarantee is real.

**Rekey conforms to MLS TreeKEM ([RFC 9420](https://www.rfc-editor.org/rfc/rfc9420), normative).** The epoch-DEK rekey on member change is the MLS TreeKEM construction: an O(log N) path rekey, the commit signed once, with RFC 9420 blank-node / unmerged-leaf handling and parent-hash tree integrity. The hybrid KEM (X25519+ML-KEM-768) is the MLS ciphersuite's HPKE KEM.

**Delivery is decisive (carried from the bandwidth model).** The TreeKEM advantage is *multicast aggregation*, not the tree itself: with efficient multicast the commit egress is **O(log N)** (one commit serves all); over unicast the commit must reach each member, **O(N log N)** — in which case the **flat per-member cascade (O(N), one grant per member) is competitive-to-better**. The substrate MUST select per deployment based on whether the transport multicasts; the choice is **wire-invisible** (tree position rides the opaque `key_grant` payload; no schema migration). Whether the RET mesh offers efficient multicast is the open transport question (the bandwidth model's one free parameter).

**Forward secrecy** is forward-only by default ([CC 4.5.12.1](part_4_composition_governance.md) Option A). **Post-Compromise Security (PCS)** is AVAILABLE (inherent to TreeKEM key-updates: a compromised current member heals on the next commit) and is **OPTIONAL, operator-enabled** — a deployment MAY require periodic self-updates for PCS, or stay forward-only.

**Catch-up bound (P4)**: `min(operator depth cap [LensCore knob, NOT a substrate constant], chunk-eviction horizon)`. Three distinct windows that are NOT conflated: chunk-eviction horizon ≠ [CC 5.3.2.1](#1012-holder-directory-ttl--contentmiss-feedback) `holds_bytes` 24h TTL ≠ grant durability. A catch-up request against an evicted epoch returns **`ContentMiss` — fail-honest, no silent gap** (consistent with the [`MISSION.md`](../../MISSION.md) fail-honest invariant). Operators MUST ship the P4 cap **with** the cascade, else 10⁶ grant Contributions per rekey is the unbounded worst case.

## 5.2 `family` — Structural invisibility — `holds_bytes:sha256:*` suppression for `cohort_scope: self | family`

The strongest privacy guarantee in the system is the one the operator cannot switch off. The load-bearing claim from [ciris.ai/cewp](https://ciris.ai/cewp):

> Self and family content never emits the attestation that would tell the rest of the network it exists. You don't need a privacy policy to keep family photos off the federation — the wire format can't carry them in the first place.

This is codified as a normative substrate discipline. When a Contribution carries `cohort_scope: self` OR `cohort_scope: family`, the substrate MUST NOT emit a corresponding `holds_bytes:sha256:{prefix}` directory attestation per [CC 3.1.9.1](part_3_the_namespace.md) — the content's bytes are delivered to admitted members of the relevant self-collective ([CC 3.3.6](part_3_the_namespace.md) `identity_occurrence`) or family ([CC 3.3.4](part_3_the_namespace.md)) via the at-rest encryption flow, NOT via the public holder-discovery directory.

**The privacy property is structural, not policy**:

- A non-member peer cannot issue `ContentFetch` for the bytes because no `holds_bytes:sha256:*` attestation names a holder.
- A non-member peer cannot even *discover* the bytes exist via the substrate — the only attestations referencing them are scoped to the self-collective / family and never federate beyond it.
- This is the wire-format-level closure of the cewp **structural invisibility** claim: privacy emerges from format constraints, not from operator policy or legal undertaking.

> **Scope (normative):** structural invisibility buys **content-holding confidentiality only** — it is NOT relationship-existence, metadata, traffic-analysis, or unobservability privacy. The bounding non-goals are stated canonically at [CC 1.13.3.1](part_1_foundation.md); do not represent CEG as providing the stronger properties.

**Substrate enforcement**:

```
On admission of a Contribution C with cohort_scope ∈ {self, family}:
    # (1) STRUCTURAL INVISIBILITY — UNCONDITIONAL (the cewp privacy promise):
    substrate MUST NOT emit holds_bytes:sha256:* for C's evidence_refs bytes
    substrate MUST NOT propagate C beyond the self-collective / family scope
        via any other directory or discovery surface
    # (2) AT-REST ENCRYPTION — the §8.1.12.4 cascade (defense-in-depth):
    WHEN self/family at-rest encryption is enabled for the deployment:
        recipients := if cohort_scope == self:   all current identity_occurrences of C.attesting_key_id
                      if cohort_scope == family: all current members of family per C.family_id
        FOR each recipient r:
            kem := resolve_encryption_keys(r.key_id)    # current occurrence's encryption_pubkeys (§5.6.8.8.2)
            IF kem is None OR kem.ml_kem_768 invalid:
                # FAIL-SECURE: no valid v2 wrap target ⇒ EXCLUDE r from the grant.
                # MUST NOT fall back to plaintext or to wrap_algorithm v1.
                # NOT SILENT: emit hard_case:recipient_excluded:{scope_key_id}
                #   (§7.7, which defines the closed reason-set) INTO the self/family
                #   scope — recipient r, reason, + the skipped Contribution's envelope
                #   ref. Scoped to the cohort; never federates beyond it (§10.1.4
                #   invisibility preserved).
                skip r   # content stays encrypted + unreachable to r until r registers encryption_pubkeys
            ELSE:
                substrate MUST wrap C's DEK via key_grant (§5.6.8.4, wrap_algorithm v2 — §8.1.12.4)
                    to kem.{x25519, ml_kem_768}
```

**Two layers, not one.** (1) **Structural invisibility** — suppressing `holds_bytes:sha256:*` + non-propagation beyond scope — is the **unconditional** privacy promise (the cewp "the wire format can't carry them" claim); it holds even when the at-rest bytes are plaintext, because no discovery attestation federates. (2) **At-rest encryption** — the CC 4.4.3.4.1 DEK cascade — is **defense-in-depth** (against local-disk forensics, the host operator, or the cloud-substrate operator); it is operator-policy and MAY default off as a v1 migration posture, **but when enabled MUST use `wrap_algorithm: v2` (hybrid PQC, CC 4.4.3.4.1)** — never v1. The CEG-RET-native target is at-rest-on for self/family (the "everything PQC at rest" standard).

**Composition with at-rest encryption flow**: when self/family at-rest encryption is enabled, persist wraps the DEK (`wrap_algorithm: v2`) under each currently-admitted `identity_occurrence`'s `occurrence_key_id` (self) or each `member.key_id` in the named family's roster (family). New occurrence / new family-member admission triggers retroactive `key_grant` emission for all extant `cohort_scope: self|family` content (the "I bought a new phone and want my Twitter history" / "I added Carol to the household" flows from CC 3.3.4 worked example).

**Recipient encryption-key resolution + fail-secure exclusion.** The wrap target is **not** a recipient's signing key. `wrap_algorithm: v2` needs the recipient's `{x25519, ml_kem_768}` **content-KEM** keys, which the recipient self-certifies via its `identity_occurrence.encryption_pubkeys` ([CC 3.3.6.1](part_3_the_namespace.md)); the substrate resolves them by `resolve_encryption_keys(key_id)` = the recipient's current (non-superseded, within-`valid_until`) occurrence → its `encryption_pubkeys`. Because this layer **mandates v2**, a recipient whose current occurrence carries **no valid ML-KEM-768 key MUST be fail-secure *excluded*** from the grant — the content remains encrypted and unreachable to it; the substrate MUST NOT fall back to plaintext or to `wrap_algorithm: v1`. To be an at-rest-encryption recipient, an identity MUST have a federation-present occurrence carrying `encryption_pubkeys`. This is the [non-maleficence / fail-secure default](../../CLAUDE.md): a missing key denies access, never downgrades the protection.

**Exclusion MUST NOT be silent.** A bare `skip` makes a fail-secure exclusion indistinguishable from "the family went quiet" — a soft-censorship vector for a buggy or malicious substrate, and a contradiction of the spec's own `hard_case:*` attestability grain. On every fail-secure skip the substrate MUST emit **`hard_case:recipient_excluded:{scope_key_id}`** ([CC 3.4.4](part_3_the_namespace.md), which defines the closed `reason` set) **into the affected self/family scope itself** — carrying the excluded recipient's `key_id`, a `reason`, and the skipped Contribution's envelope ref — so the excluded member (who still sees cohort-scoped attestations) has something to audit and remediate. The event is cohort-scoped: it MUST NOT federate beyond the self/family (the CC 5.2 invisibility promise is preserved; the *fact* of the family's content is not leaked by its exclusion events).

**Locality dividend** (cewp claim): the structural invisibility mechanism is *why* ~65% of activity stays local in the cewp scaling model — `cohort_scope: self|family` content is the bulk of daily activity (family photos, personal notes, in-household device chatter), and that bulk never federates. Operators do not configure this; the wire format enforces it.

**Boundary cases**:

- `cohort_scope: community | affiliations | federation` content emits `holds_bytes:sha256:*` per status-quo behavior. Only the self/family path is suppressed.
- A `cohort_scope: self` Contribution that is later promoted via `supersedes` to `cohort_scope: community` emits `holds_bytes:sha256:*` at promotion time on the NEW Contribution. The original `cohort_scope: self` Contribution's bytes remain structurally-invisible at federation; only the promoted scope's bytes propagate.
- `cohort_scope: self` content with `subject_key_ids` containing a non-self party (e.g., a private note Alice writes ABOUT Bob) is admitted and stays in Alice's self-collective; Bob does NOT receive a key_grant unless Bob is also in Alice's self (not the case for two distinct identities). Bob's [CC 2.3](part_2_the_grammar.md) subject-side revocation authority over the note still composes, but the bytes never reach Bob without Alice's explicit re-emit at a higher cohort_scope including Bob.

## 5.3 `endpoint` — Endpoint shapes

CEG specifies five public + one admin HTTP endpoint shape for the discovery + cosigning surfaces. Wire format consumers (CIRISVerify v3.1.0+, CIRISAgent KMP UI, iOS/Android FFI) read these.

### 5.3.1 `witness` — STH cosigning + witness directory

The witness directory is where transparency becomes accountable: independent witnesses cosign the log's tree heads so a producer cannot show one history to one party and a different one to another. CIRISVerify v2.12.0+ ships consumer-side `SignedTreeHead::cosign` + `count_valid_witnesses` + `witness_quorum_met`. CEG's emission half:

### `POST /v1/transparency/sth/cosign` (public)

Witness posts cosignature on `(tree_size, root_hash, signed_at)`. Registry verifies hybrid Ed25519 + ML-DSA-65 against witness pubkey in directory; persists on success.

Request body:

```json
{
  "tree_size": <int>,
  "root_hash_sha256_hex": "<64-char-lowercase>",     // per §0.6
  "signed_at": "<rfc3339_canonical>",                // per §0.5
  "witness_key_id": "<string>",
  "ed25519_signature_b64": "<base64-url>",
  "mldsa65_signature_b64": "<base64-url>",
  "consistency_proof_root_hash_sha256_hex": "<64-char-lowercase>",
  "consistency_proof_tree_size": <int>,
  "consistency_proof_path_b64": ["<base64-url>", ...]
}
```

Canonical bytes (witness MUST sign these):

```
canonical = sha256(
    "ciris.sth_cosign.v1\n" ||
    "tree_size=" || decimal_no_leading_zeros || "\n" ||
    "root_hash_sha256=" || sha256_hex_lowercase || "\n" ||  // per §0.6
    "signed_at=" || rfc3339_canonical                       // per §0.5
)
```

Ed25519 over `canonical`; ML-DSA-65 over `canonical || ed25519_sig` (bound payload).

#### 5.3.1.1 `consistency-proof` — Consistency-proof requirement (normative)

A cosignature only means something if the witness has checked that the new tree is a consistent extension of the one it last saw — otherwise quorum is agreement on a string, not on a history. A witness signing an STH MUST first verify a consistency proof from the prior STH it cosigned (or from genesis if it is the witness's first cosignature against this log). The Registry MUST reject `POST /v1/transparency/sth/cosign` requests that omit the `consistency_proof_*` fields OR whose consistency proof does not verify against the named prior STH. `witness_quorum_met` is therefore "quorum on log consistency," not "quorum on a string."

The cosign request carries `consistency_proof_path_b64[]` (base64 RFC 6962 §2.1.2 node hashes). The Registry anchors the check against the prior `(tree_size, root_hash)` **it recorded** for that witness — not a root the requester claims — and rejects: missing proof when a prior STH exists or a tree_size behind the witness's prior cosigned STH → `MALFORMED_REQUEST`; a proof that does not reconstruct both roots → `CONSISTENCY_PROOF_INVALID` ([CC 5.3.6.1](#1001-error-envelope)). A witness's first cosignature is exempt ("from genesis"). The RFC 6962 verifier is vendored from `ciris-verify-core::transparency` (Registry omits that crate for a libsqlite3 linker reason) and proven against independent known-answer vectors.

### 5.3.2 `transport` — Transport substrate for byte-level content

Wire-format Attestations carry claims; they don't carry bytes. When a claim's `evidence_refs[]` cites a SHA-256-addressed blob (e.g., an installer binary, a config file, an adapter package per `agent_files:*` per [CC 3.1.7 / CC 3.1.10](part_3_the_namespace.md)), the bytes travel via Edge transport substrate: `MessageType::ContentFetch` + `ContentBody` + `ContentMiss`. Holder-discovery via Persist's `holds_bytes:sha256:*` directory; peer-resolution via Edge's `PeerResolver::resolve_holders`. NodeCore node-mode peers serve the bytes per their MISSION CC 2.4 cohabitation contract. Attestation envelope shape unchanged; SHA-256 in `evidence_refs[]` becomes universally resolvable to bytes through the substrate.

#### 5.3.2.1 `holder` — Holder directory TTL + ContentMiss feedback

A `holds_bytes:sha256:{prefix}` attestation has a default validity of **24 hours** from `signed_at`. After that the holder is considered stale; consumer policy MUST attempt at most 2 holders in parallel and accept the first successful full-SHA verification. On `ContentMiss` (holder no longer has the blob), the consumer MUST emit a `withdraws` against the `holds_bytes:sha256:{prefix}` attestation referencing the stale holder, with `withdrawal_reason: "content_miss"`. Holders consistently failing ContentMiss are downweighted in `PeerResolver::resolve_holders`.

#### 5.3.2.2 `consent-revocations` — Consent revocations are NOT local-tier-eligible

A user's withdrawal of consent is the one signal federation peers rely on to stop propagating that user's data — so it can never be left unsigned and invisible to them, even briefly. The CEG-native agent design proposes **local-tier signature deferral** — self-attestations skip the hybrid Ed25519 + ML-DSA-65 signature path locally and only sign at federation-tier promotion. This is sound for **producer-only-authority self-attestations**. **The discriminator is *who holds revocation authority*, NOT whether `subject_key_ids` is empty**: a producer-authority self-attestation MAY name a subject in `subject_key_ids` per [CC 2.3.1](part_2_the_grammar.md) — e.g. `observed:user:{hash}:*`, `epistemic:about:{key}:*`, a self-`consent:partnered:{user}`, or the [CC 2.3.4](part_2_the_grammar.md) self-`identity:current` with `subject_key_ids=[self]` — and remains local-tier-eligible, because the producer holds the authority and no *other* subject can revoke it. The single carve-out is below: a Contribution where a **subject other than the producer holds revocation authority** over it.

**Consent revocations from subjects MUST NOT use the local-tier deferral path.** When a Contribution carries non-empty `subject_key_ids`, any subsequent `consent:state:revoked` emission OR `withdraws` admitted under [CC 2.4.1.1 rule 2 or 3](part_2_the_grammar.md) from a subject in that set MUST promote to federation-tier within a bounded window. Default window: **24 hours** (operator-tunable per local policy).

**Rationale**: subject-side revocation is the wire-format observability primitive that federation peers depend on to honor consent. If a user revokes consent in the local-tier scope of one agent's substrate, and that revocation is unsigned + unpromoted for an extended window, other federation peers continue propagating the user's data — exactly the failure mode this closes.

**Substrate emission**: substrate MUST emit `hard_case:consent_revocation_promotion_overdue` when a subject-side revocation has been local-tier for longer than the operator-configured window without federation-tier promotion. LensCore composes `detection:consent:promotion_delay_pattern` on top (operator monitoring; not a slashing trigger on its own).

**Composition with the self-attestation pattern**: the CEG-native agent's `consent:partnered:{user_key}` self-attestation (producer-side stance) MAY ride local-tier; the user's `consent:state:revoked` against the agent's stance Contribution (subject-side) MUST NOT. This preserves the cardinality win of deferral while closing the leak window.

**Ratification — AV-61 consent-tail: transit-not-rest reconciliation (resolves CIRISRegistry#110(b) / CIRISPersist#238, ref CIRISPersist#146 §10.1.3).** CIRISPersist's "no local subject-revocations" rule and the consent-SLA promotion gate above are the **same invariant viewed from the two gates**, not a contradiction. A subject-side consent revocation — a subject-emitted `consent:state:revoked`, or a `withdraws` admitted under [CC 2.4.1.1 rule 2/3](part_2_the_grammar.md) from a subject named in the target's `subject_key_ids` — is **federation-tier by classification**. It MAY *transit* the local-tier write path while in flight (the producing occurrence's substrate accepts the unsigned envelope before promotion), but it MUST NOT *rest* there: a subject revocation is **never a durable local row**. Its only conformant terminal states are *promoted* (federation-tier, hybrid-signed per CC 5.3.2.4.3) or *overdue-flagged* — never *settled local*. The substrate MUST drive it to federation-tier promotion within the 24-hour SLA defined above; the local tier is a momentary staging buffer for it, not a resting place.

**The overdue emission IS the SLA enforcement.** When the 24-hour window lapses without federation promotion, the substrate MUST emit `hard_case:consent_revocation_promotion_overdue` (as required above). This emission is not merely observability — it is the signal the consent-promotion path keys off: the consent-promotion gate and the CC 5.3.2.4.3 `local ⟹ caller is the producing occurrence` read-gate read the **same** overdue state. Because both gates key off one shared signal, a subject revocation can never be simultaneously (a) invisible to federation peers under the local read-gate and (b) un-flagged by the consent-promotion gate. Keeping the two gates reading one state is exactly what closes **AV-61** (the two gates de-synced, CC 5.3.2.4.3): there is no window in which a subject revocation persists as an authoritative-looking local row while federation peers continue propagating the subject's data.

#### 5.3.2.3 `merge` — Cross-region merge intents — CEG-declared per subject_kind (normative)

With operational data joining the CEG-native replication stream ([CC 3.3.9](part_3_the_namespace.md)), the substrate runs **more than one merge policy**. The policy is a **normative property of the subject_kind, declared here** — the substrate reads and dispatches on the declaration; it MUST NOT infer policy per record type (the substrate enforces declared merges; it does not invent policy).

| subject_kind(s) | Merge intent | Semantics |
|---|---|---|
| `organization`, `org_membership` | **`lww_skew_bounded` + `withdrawal_forward_only`** | Stable-id grouping ([CC 3.3.9](part_3_the_namespace.md)); an admitted `withdraws` (deactivation) is forward-only — a later non-withdrawn write does NOT resurrect; else latest `asserted_at` wins; tie-break smallest `attestation_id` ([CC 3.5.1](part_3_the_namespace.md)). The forward-only here is the **lightweight authz flag**, NOT the [CC 4.4.3.4](part_4_composition_governance.md) DEK-cascade crypto path — Commons tier, no DEK exists. |
| `partner_record` | **`monotonic_quorum`** (the CIRISPersist V058 R1/Q1 machinery, generalized from `revoked_key_id` to `license_id`) | Admission anti-rollback first: a write whose `revision` decreases never enters the merge. Then the `MergeBallot` comparator: `quorum_weight` → signed timestamp → content hash. Quorum-above-time is deliberate — it neutralizes timestamp front-running (F-AV-FRONTRUN) on the records where it matters most. More-restrictive state wins on conflict: `revoked` > `suspended` > `active`. |
| `revocation` + the three membership-revocations | V058 R1/Q1 (the original `monotonic_quorum` instance) | As shipped. |
| keys / attestations / occurrences / families / communities / location_proofs | Content-addressed idempotent admission | Same content → same `envelope_hash` → dedup; rotation collisions rejected non-destructively. |

**Skew-bounded admission (normative — the LWW front-running fix).** For every subject_kind merging by `lww_skew_bounded`, the substrate MUST reject at admission any envelope with `asserted_at > now + tolerance`, where `tolerance` is the [CC 2.6.7](part_2_the_grammar.md) clock-skew bound (±5 minutes; the existing `CLOCK_SKEW_VIOLATION` error class). Without this, a signer with a forward-skewed clock future-dates `asserted_at` and wins LWW indefinitely; with it, a forward-dated write can win for at most the skew window. This matters precisely because `org_membership` carries `role: OrgAdmin` — unbounded LWW on authz data is a role-escalation surface.

**The two quorums (restated from [CC 3.3.9](part_3_the_namespace.md) — different layers, different stewards):** the **steward-signature admission quorum** (M-of-N signature set over identical JCS bytes; the [CC 3.2](part_3_the_namespace.md) founder-quorum machinery at admit — Verify's layer) is NOT the **region merge quorum** (`quorum_weight`, the `MergeBallot` tier-1 ordering above — the substrate's layer). The substrate's merge logic never counts steward signatures; Verify's admission check never orders merges.

#### 5.3.2.4 `attestation-tier` — The attestation tier model — local-tier write, query, promotion (normative)

Pins the **shared attestation surface** the four CEG-RC1 implementations (CIRISAgent, CIRISNodeCore, CIRISLensCore, CIRISRegistry) write/query/promote through, so it is analyzable + modelable as one contract. The substrate exposes the *methods*; CEG pins the *wire/conformance semantics* every implementation MUST agree on. **No 1+4 change** — a "tier" is recorded state on an attestation, not a new primitive. The tier split serves the same fail-secure cost discipline as streaming: cheap, unsigned writes stay private and local until the costly hybrid signature is paid exactly once, at the moment authority actually crosses to the federation.

##### 5.3.2.4.1 `authority-local` — Local-tier eligibility — the discriminator is *revocation authority*, not subject-set emptiness

A write is local-tier-eligible iff **the producer holds sole revocation authority** over it. The discriminator (*revocation authority*, NOT empty `subject_key_ids`), the producer-authority-with-named-subject examples, and the single carve-out (a Contribution where a subject other than the producer holds revocation authority — a `withdraws` under [CC 2.4.1.1 rule 2/3](part_2_the_grammar.md) or a subject-emitted `consent:state:revoked`, which MUST go signed / promote per the CC 5.3.2.2 24-hour obligation, never local) are defined canonically at [CC 5.3.2.2](#1013-consent-revocations-are-not-local-tier-eligible-ceg-06-addition). Tier-specific addition: `witness_relation` MUST be `self` for any local-tier write.

##### 5.3.2.4.2 `local` — Promotion — `local → federation` (the deferred-signature moment)

Promotion computes the hybrid signature and flips the row federation-visible. It is **idempotent** (promoting a `federation` row returns it unchanged), and at the promotion instant the tiered-scope promotion ([CC 4.4.3.3.1](part_4_composition_governance.md)) and `holds_bytes` emission ([CC 5.3.2.1](#1012-holder-directory-ttl--contentmiss-feedback)) fire exactly as for any federation write — **promotion *is* the federation-emit moment**.

**Canonical bytes — `JCS(envelope)` per [CC 2.6.1](part_2_the_grammar.md) / RFC 8785:**
- The signature MUST cover `JCS(contribution_envelope)` — the **identical** canonical bytes any natively-federation attestation signs. A promoted row is therefore **byte-indistinguishable on the wire from one born federation-tier**; there is no "was-promoted" marker in the signed bytes.
- **Substrate columns are NOT in the canonical bytes.** `tier`, `promoted_at`, and any other storage bookkeeping are substrate state, never part of `JCS(envelope)`. Only the [CC 2.1](part_2_the_grammar.md) envelope member set is canonicalized.
- **CC 2.6.1 omit-vs-materialize is load-bearing here.** Promotion MUST canonicalize the **exact member set the producer committed at local-write time** — a field *omitted* at local write MUST NOT be materialized at promote, and vice-versa, or the recomputed bytes diverge from what a peer verifies and the hybrid sig fails. The substrate serializes the stored row → the committed envelope → JCS → sign; it MUST NOT re-default.
- Registry owns the exact envelope member set ([CC 2.1](part_2_the_grammar.md) + the [CC 2.6.1.2](part_2_the_grammar.md) catalog); Verify recomputes the identical JCS bytes. Do NOT use Verify's internal length-prefixed `signing_bytes` framing — that is for verify-to-verify primitives that never cross the four-impl boundary as JSON; a promoted attestation is the opposite.

##### 5.3.2.4.3 `two` — The two tiers

| Tier | Signature | Federation-visible | Read-visibility | Written by |
|---|---|---|---|---|
| `local` | MAY be absent (deferred per CC 5.3.2.2) | **No** | **only the producing occurrence** (self-read); every other caller — even an authorized family/community peer — sees nothing | local-tier write |
| `federation` | hybrid Ed25519 + ML-DSA-65 **present** | Yes | per [CC 2.1](part_2_the_grammar.md) `cohort_scope` + the CC 5.2 invisibility rule | direct signed write OR `local → federation` promotion |

**Invariant (substrate MUST enforce):** `tier = federation ⟹ hybrid signature present`. Nothing crosses to federation-visible unsigned. A `local` row is **labelled** local and MUST NOT be served as federation-authoritative ([fail-honest](../../MISSION.md)). The read-gate is **orthogonal** to `cohort_scope`: it is an additional filter (`local ⟹ caller is the producing occurrence`), composing with the CC 5.2 target-membership predicate. Threat entries: AV-59 (local row leaked to a non-self caller), AV-60 (unsigned local served as authoritative), AV-61 (the two gates de-synced).

###### 5.3.2.4.3.1 `admission-pqc` — The PQC half is MANDATORY at admission — no classical-only, no hybrid-pending accommodation (normative)

The CC 5.3.2.4.3 invariant `tier = federation ⟹ hybrid signature present` is **enforced at the admission gate**, and "present" means **verified**: every federation-tier admission gate MUST check **both** halves — Ed25519 over `JCS(envelope)` **and** ML-DSA-65 over `JCS(envelope) ‖ ed25519_sig` (the [CC 3.1.2.1](part_3_the_namespace.md) bound-payload form) — and MUST **reject** a federation-tier Contribution that carries only the classical half. This binds **all operational-authority admission gates**, explicitly including `operational_admit` (key_grant / partner / org-membership / license writes), the [CC 3.3.6.2](part_3_the_namespace.md) `transport_destination` binding, and the [CC 3.2](part_3_the_namespace.md) `partner_record` / founder-quorum gates.

**This is an immediate requirement — not a phased cutover.** There is no opportunistic-acceptance window and no fleet-floor or calendar trigger. The rationale is exactly the threat hybrid exists to defend: an adversary holding a future Ed25519 break could forge a grant / binding / partner-record and have it admitted if the classical half alone sufficed. There is **no `require_hybrid: false` posture** — a verifier's hybrid-required check is always-on, never an operator toggle; the only conformant state for a federation-tier key is "carries a valid ML-DSA-65 half." A key that has not completed PQC wiring is **not conformant for federation-tier emission** and is confined to local-tier (self-read, [CC 5.3.2.4.1](#10152-local-tier-eligibility--the-discriminator-is-revocation-authority-not-subject-set-emptiness)) until it does. The mandate is at the **federation admission boundary only** — the single place authority crosses; local-tier rows MAY still defer the signature per [CC 5.3.2.2](#1013-consent-revocations-are-not-local-tier-eligible-ceg-06-addition).

**The mandate binds the durable store + replication path, not only the authority gates.** "Federation-tier" means **every** federation-tier attestation, including the bulk **per-trace / store-and-replicate** path — not merely the operational-authority gates enumerated above. A federation-tier trace written to the durable, content-addressed, replicated corpus MUST carry (and a verifier MUST check on ingest) the ML-DSA-65 half exactly as a `key_grant` does; there is **no "operational authority vs testimony leaf" exemption** (federation root and the trace leaf are bound by the same rule). **Content-addressing is NOT a defense against forge-later:** a CRQC-era adversary who breaks Ed25519 mints a backdated trace under a historical key and hashes **their own** forgery — the content hash matches by construction, so the address proves nothing about authenticity. Because the trace store is *kept for posterity* (it outlives the classical primitive), the per-trace signature is the single most forge-exposed surface in the federation — the "store at massive scale" CEWP crux — and the PQC half is mandatory there for the same forge-now / harvest-now-exploit-later reason as the at-rest DEK cascade ([CC 5.1](#1053-membership-change--epoch-rekey) / [CC 4.4.3.4.1](part_4_composition_governance.md)). A substrate persisting/replicating a federation-tier row whose envelope signature lacks a valid ML-DSA-65 half MUST reject it at the ingest gate — store-then-quarantine is non-conformant.

##### 5.3.2.4.4 `persist-query` — Query — open-prefix dimensions, bounded operators (normative)

The uniform read filters on `(dimensions[], valid_at, confidence_floor, subject_key_id?, scope)`.
- **`dimensions[]` is an OPEN-vocabulary set of prefix strings, matched by hierarchical prefix — NOT a closed enum.** Per [CC 4.5.1.1](part_4_composition_governance.md) axis-vocabulary discipline, dimension prefixes are open vocab (new families — `consent:*`, `detection:community:*`, `settlement:*` — ship continuously). A closed enum would force a substrate redeploy per CEG namespace addition and break forward-compat. A query for `detection:*` matches `detection:correlated_action:bribery` etc.; an exact string matches exactly.
- **The bounded surface is the *operator set*, not the *vocabulary*.** The apophatic discipline (a fixed, named surface — not an OLAP/graph engine) is preserved by the **closed set of five predicates** above + no caller-composed SQL/projections — NOT by closing the dimension vocabulary. *Open data, closed operators.*
- `valid_at` filters `asserted_at ≤ valid_at < COALESCE(expires_at, ∞)`; `confidence_floor` filters `weight ≥ floor`; `scope` applies BOTH the CC 5.2 target-membership gate AND the CC 5.3.2.4.3 tier gate. Write-side reserved-prefix emitter gates ([CC 3.4.7.1](part_3_the_namespace.md)) are unaffected — read is gated by scope, not by dimension authority.

##### 5.3.2.4.5 `holistic` — For holistic analysis + modeling (informative)

The tier model is the *same KEM-then-symmetric placement* the streaming model uses ([CC 5.3.3](#105-streaming-transport-per-stream-logs--delivery-receipts-ceg-010-addition)), applied to attestations: the **expensive op (hybrid sign) is on the cold path** (promotion, at federation-emit), while the **hot path (local self-attestation write) is O(1) and unsigned**. Cost shape for a node:
- **local write**: O(1), no asymmetric crypto — the agent's steady-state memory/config/consent/identity churn.
- **promotion**: one hybrid Ed25519+ML-DSA-65 sign (~the CC 5.3.3-model per-op cost; ML-DSA-65 sign ~330 µs) + JCS canonicalization — only at the federation-emit moment, never per local write.
- **query**: the [CC 2.1](part_2_the_grammar.md)/DAS scope-filtered read; cost is the predicate + index, independent of tier.
- **observability for modeling**: `local` row count, promotion rate, and `hard_case:consent_revocation_promotion_overdue` count are the three measurable signals; the CC 5.3.2.2 24-hour window is the one tunable. A model of a federation's attestation load is therefore *(local-write rate, promotion rate, query rate)* with promotion carrying the only asymmetric-crypto cost — the dual of the streaming model's epoch-rekey tail.

#### 5.3.2.5 `full-sha` — Full-SHA verification before consumption (normative)

A CEG-Conforming Consumer (CCC) MUST verify the full SHA-256 of received bytes against the value in `evidence_refs[]` BEFORE handing the bytes to any consumer (Agent loader, Portal renderer, etc.). The `holds_bytes:sha256:{prefix}` directory ([CC 3.1.9.1](part_3_the_namespace.md)) carries only a short prefix for index efficiency; the consumer MUST NOT short-circuit verification to the prefix. Bytes that fail the full-SHA check MUST be discarded and the holder MUST be reported via the `holds_bytes:sha256:{prefix}` chain (emit a `withdraws` or negative score per consumer policy).

### 5.3.3 `transport-streaming` — Streaming transport, per-stream logs & delivery receipts

This is the **delivery axis** — the third orthogonal envelope concern alongside visibility (`cohort_scope`) and revocability. [CC 2.4](part_2_the_grammar.md)'s 1+4 primitive set is untouched; this is an endpoint + envelope + composition extension, NOT a grammar change.

**Bifurcation**:

| Half | Cardinality | RC1 status |
|---|---|---|
| **Observer-share / directed delivery** (single Contribution → subscriber-set; no `stream_id`) | N=1 typical; per-subscriber `key_grant` | **impl-live**; substrate paths shipping per [CC 3.3.2](part_3_the_namespace.md) `key_grant` + [CC 4.4.3.2](part_4_composition_governance.md) Policy M membership |
| **Media / streaming multicast** (`live_stream` chunk-DAG; per-`(stream_id, epoch)` keys) | N>1; flat per-epoch `key_grant` cascade | **spec-now, impl substrate-pending**; subsections CC 5.3.3.1 / CC 5.1 / CC 5.3.3.6 ride this dependency |

#### 5.3.3.1 `stream` — Chunk seal + STREAM nonce (normative — V2 lock)

Per-chunk content sealing **conforms to SFrame** ([draft-ietf-sframe](https://datatracker.ietf.org/wg/sframe/about/), normative): the per-frame AEAD model with a `(KID, CTR)` header, here bound as `KID = stream_id` and `CTR = counter`, AEAD = AES-256-GCM, keys derived per MLS epoch (the canonical SFrame+MLS composition, CC 5.1). The STREAM nonce below is CEG's binding profile of SFrame's per-sender nonce derivation. Per-chunk content sealing uses AES-256-GCM (NIST FIPS 197 + SP 800-38D). The 12-byte (96-bit) nonce follows the **STREAM** layout (Hoang, Reyhanitabar, Rogaway, Vizár — *Online Authenticated-Encryption and its Nonce-Reuse Misuse-Resistance*, CRYPTO 2015):

```
nonce[12] = prefix[7] ‖ counter_be[4] ‖ last_flag[1]
```

- **`prefix[7]`** — derived, NOT transmitted: `prefix = HKDF-SHA256(epoch_dek; info)[0..7]` where the HKDF `info` is the **byte-exact** concatenation: `info = b"ciris-stream-nonce/v1" ‖ stream_id_utf8 ‖ epoch_be8`, with `stream_id_utf8` = the UTF-8 bytes of `stream_id` and **`epoch_be8` = the `u64` epoch as 8-byte big-endian** (`epoch.to_be_bytes()`, consistent with `counter_be`). **This encoding is normative and MUST be byte-identical across producer, substrate, and every consumer** — the CC 5.1 zero-trust-of-host posture has consumers recompute this exact nonce to *open* chunks, so any BE/LE/ASCII disagreement on `epoch` yields a different `prefix` → different nonce → GCM auth-tag failure (silent whole-stream decryption failure), the same hazard class `counter_be` already guards. No length-prefix on `stream_id` is required: the fixed-length tag prefix + fixed 8-byte `epoch` suffix make the parse unambiguous (distinct `(stream_id, epoch)` pairs always yield distinct `info` — unequal `stream_id` length changes total `info` length; equal length splits unambiguously). Matches the **`KEY_GRANT_V1_INFO`** versioned-context HKDF pattern at [`CIRISVerify/src/ciris-crypto/src/key_grant.rs:71`](https://github.com/CIRISAI/CIRISVerify/blob/main/src/ciris-crypto/src/key_grant.rs) (`b"cewp-key-grant/v1"`). Per-`(stream_id, epoch)` unique; verifiable by any holder of the epoch DEK
- **`counter_be[4]`** — 32-bit big-endian; hard ceiling 2³²−1 chunks per epoch. Substrate MUST force an epoch roll before wrap. Recommended operational cap: **`MAX_CHUNKS_PER_EPOCH = 2²⁴`** (~16.7M chunks/epoch) to keep per-epoch state + proof sizes bounded (operator-tunable)
- **`last_flag[1]`** — `0x01` on the final chunk of an epoch (sealed by `seal_stream` per CC 5.1); `0x00` otherwise. The distinct nonce on the final chunk gives **truncation + append resistance**: an adversary cannot drop the final chunk and pass off a short stream, nor append past a sealed segment

**Cross-epoch counter reset is nonce-safe (normative reasoning)**: GCM's catastrophic case is reuse of a `(key, nonce)` pair. On epoch roll the DEK changes, so a reset counter lives in a different keyspace — `(DEK_e, nonce=0)` and `(DEK_{e+1}, nonce=0)` are distinct pairs. The enforced invariant is therefore only within a single epoch: counter strictly monotonic, never wraps (guaranteed by the forced roll). Across epochs, reset is free.

**Single-sender-per-`(stream_id, epoch)` invariant (normative — nonce-collision safety; cribbed from SFrame/MLS)**: the `counter_be[4]` space of a `(stream_id, epoch)` is owned by **exactly one** sender — the `stream_id`'s producer. Two distinct senders MUST NOT seal chunks under the same `(stream_id, epoch)` DEK, or their independently-incremented counters could collide into a reused `(DEK, nonce)` pair (GCM-catastrophic). In **group video** ([CC 5.3.3.2](#1058-realtime-group-communication--composition-ceg-013-addition)) each participant emits their **own** `live_stream` with their **own** `stream_id`, so the nonce prefix `HKDF(epoch_dek; "ciris-stream-nonce/v1" ‖ stream_id ‖ epoch)` is per-sender-unique by construction — the same hazard SFrame avoids with per-sender keys, achieved here by per-sender `stream_id`. Substrate MUST reject a chunk-append whose `(stream_id, seq)` collides with an existing sealed chunk (replay/forking guard, [CC 5.1](#1053-epoch-keying--cascade-normative--d2--d3-substrate-pending-142)).

#### 5.3.3.2 `composition` — Realtime group communication — composition

The delivery axis was framed for 1:1 observer-share and 1:N broadcast multicast. Realtime **group communication** — group video, voice, desktop/screen sharing, text chat, and topic-scoped channels with sub-channels — is the **same primitive set at N↔N cardinality**. It composes entirely from `community` ([CC 3.2](part_3_the_namespace.md)) + `live_stream` (the CC 5.3.3 streaming surface) + `chat_message` + member/transport resolution ([CC 4.4.3.2.4.1](part_4_composition_governance.md)). **Zero new structural primitives** — this is the thirteenth path on the [CC 1.7](part_1_foundation.md) claim and the most product-complete: the whole realtime-collaboration surface is composition.

**The composition map (all generic — no new wire):**

| Surface | Composes from |
|---|---|
| **1:1 / group video call** | each participant emits a `live_stream` (their A/V) scoped to the channel `community`; each subscribes to peers. N↔N = N simultaneous bidirectional streams over a small roster |
| **Voice channel** | identical to group video with an audio-only codec; same `live_stream` wire |
| **Desktop / screen sharing** | a `live_stream` whose source is a screen capture (1→N within the channel); same chunk-seal + epoch-DEK wire |
| **Text chat** | `chat_message` at `cohort_scope: community`, `community_id: <channel>`; threads via `topical_relation: replies_to` |
| **Channel** | a `community` (persistent) — its roster gates who can join the call / read the chat |
| **Sub-channels** | nested `community` membership ([CC 4.4.3.2.5](part_4_composition_governance.md) multi-level pattern): a parent "space" community whose members admit child channel-communities; sub-channel members are a subset of the space roster |
| **Presence ("who's here")** | the D6 reachable set ([CC 5.3.3.4](#1056-d6-liveness-invariant--entitled-vs-reachable-normative)) — node-local, never an attestation, never logged |
| **Invite / join / leave** | community admission ceremony ([CC 4.4.3.2.3](part_4_composition_governance.md)) — invite = membership proposal; join = admitted member; leave = forward-only `withdraws` |

**Transport profiles (normative — extends CC 5.3.3.5):**

| Profile | Topology | Transport | RC1 (1.0) |
|---|---|---|---|
| Broadcast (1:N, large N) | asymmetric | pull-only `ContentFetch` (CC 5.3.3.5 E2); relay tree → 1.x | ✅ pull |
| **Realtime small/medium group** (calls, huddles, ≤ ~50) | symmetric mesh | **direct Reticulum Links between participants** (low-latency push; no relay tree needed at small N) | ✅ direct-link mesh |
| Realtime large group (≫50 in one A/V room) | fan-out | selective-forwarding relay (SFU role) | → 1.x (same relay-tree axis as broadcast scale) |

The low-latency realtime profile (direct Reticulum Links) is **in 1.0 scope** because small/medium rosters need no relay tree — RNS Links give encrypted low-latency point-to-point natively. The wire is identical to broadcast (chunk-seal CC 5.3.3.1, per-`(stream_id, epoch)` epoch DEK CC 5.1, per-stream STH CC 5.3.3.3); only the transport profile + roster size differ. **PQC is unchanged and mandatory** — epoch DEK wrapped `wrap_algorithm: v2` (X25519+ML-KEM-768) at rest, hybrid KEX in transit.

**Ephemeral vs persistent rosters**: a persistent channel is a long-lived `community`; an ad-hoc call is an **ephemeral `community`** (short `valid_until`, torn down on last-leave). Same primitive, different lifetime — no special-case "session" primitive.

The breadth confirmation: a full realtime group-communication platform — group video, voice, screen sharing, chat, and channels-with-sub-channels — requires **no addition to the 1+4 structural set** beyond the CC 5.3.3 delivery axis and the `community` membership machinery already locked.

##### 5.3.3.2.1 `namespace-realtime` — `codec_id` namespace — realtime A/V chunk codec discriminator (normative)

[CC 5.3.3.2.2](#10581-realtime-non-av-data-streams-normative-scope-boundary) makes the realtime chunk payload codec **application-defined and opaque to the substrate**. For realtime **A/V at scale**, a hop fanning out chunks must drop chunks for per-receiver bandwidth degradation **without** decrypting them — so the codec's layer-numbering semantics must be a **clear (non-AEAD) discriminator**. CEG ratifies a 1-byte `codec_id` namespace so every implementation reads the same meaning. **This is a namespace ratification on the transport-layer chunk header, not a change to the [CC 2.1](part_2_the_grammar.md) attestation envelope** — the frozen 1+4 surface and its canonicalization are untouched.

**Wire position (normative).** `codec_id` (1 byte) + `ChunkLayer { spatial: u8, temporal: u8, quality: u8 }` (3 bytes) = a **4-byte additive block** at `SealedAvChunk` header offset **48..52**, after the existing v3.7.0 header. **Clear metadata, NOT inside the AEAD** — a relay drops chunks by `codec_id`/`ChunkLayer` without touching the inner epoch-DEK seal ([CC 5.3.3.1](#1052-chunk-seal--stream-nonce-normative--v2-lock)); tampering causes mis-decode or drop, never a crypto break. **Additive + backward-compatible**: a v3.7.0 chunk round-trips identically as `codec_id = 0xFF` + `ChunkLayer { 0, 0, 0 }`. No length-prefix is needed — the block is fixed 4 bytes at a fixed offset.

| Hex | Codec | Semantics |
|---|---|---|
| `0x01` | **AV1 SVC** | Scalable Video Coding — 3 spatial × 4 temporal × N SNR layers; base layer required to decode anything. Production default (WebRTC-native, royalty-free). The deployable codec today. |
| `0x02` | JPEG XS (layered) | Low-latency intra-only; broadcast use case. **Reserved.** |
| `0x03` | **Symmetric MDC** | Multiple Description Coding — any subset of chunks decodes at proportional fidelity, no base-layer floor. **The substrate design target** (below). **Reserved** — encoder lineage academic-grade today; substrate is MDC-ready. |
| `0xFF` | Opaque | No scalable-coding semantics; v3.7.0 wire-compat. `ChunkLayer` MUST be `{ 0, 0, 0 }`. Default for legacy / non-layered streams. |
| `0x04`–`0x7F` | — | **Reserved** for future standardized codecs (CEG-assigned). |
| `0x80`–`0xFE` | — | **Experimental / per-deployment** — no cross-federation meaning guaranteed. |

`codec_id` lets a receiver know whether `ChunkLayer { spatial: 2, temporal: 2, quality: 0 }` means "SVC base + 2 spatial enhancements" or "MDC quadrant" — without it, layer numbers are ambiguous across codecs. The substrate (Edge) never picks the codec — choice is upstream (agent/server tier); Edge needs only the namespace stable. The variable-depth `SubStreamPath` (MDC tree-path encoding) is a follow-on (tracked `§N.3`).

**MDC-primacy design intent (informative).** The user-facing contract CEWP realtime A/V targets is *"any node can request a lower-bandwidth stream from peers — as simple as taking every other chunk, down to a blinking dot."* MDC (`0x03`) matches that **symmetrically**: drop any subset → decode the rest at proportionally lower quality, no coordination, no base-layer floor. SVC (`0x01`) is production-deployable today but has a floor (base-layer bytes must arrive) and needs coordination for an "every other chunk" drop. The substrate is **MDC-shaped** (the `ChunkLayer` / `SubStreamPath` model is symmetric-drop-ready) even while production streams ship SVC; the ~20–40% MDC compression overhead vs SVC at equal quality is the accepted cost of symmetric drop semantics.

##### 5.3.3.2.2 `realtime` — Realtime non-A/V data streams (normative scope boundary)

The realtime profile is **not media-only.** Any high-frequency mutable shared state — multiplayer game ticks, collaborative-editing operations (CRDT/OT), live cursors/whiteboard strokes, remote-control input, high-rate telemetry — rides the **same** CC 5.3.3.2 realtime transport (direct Reticulum Links / SFU at scale) with an application-defined payload codec in place of an A/V codec. The wire is identical: per-`(stream_id, epoch)` epoch DEK (CC 5.1, `wrap_algorithm: v2` PQC), STREAM-nonce chunk seal (CC 5.3.3.1), per-stream STH (CC 5.3.3.3). A data-stream chunk is just a chunk.

**Scope boundary (the explicit call):**
- **IN scope (transport):** ordered, sealed, authenticated, PQC-encrypted realtime delivery of arbitrary data-stream payloads — covered by CC 5.3.3.2, no addition.
- **OUT of scope (merge semantic):** the conflict-free / convergent-merge logic for shared mutable state (CRDT, Operational Transform, last-writer-wins, etc.) is **application-layer**, not a CEG primitive — consistent with the [CC 1.13.4](part_1_foundation.md) discipline ("the substrate stores; the wire transports; CEG describes the shape of the claim; consumer policy composes verdicts"). CEG carries the ops; the application converges them. A future codified merge primitive would route through the [CC 4.5.1](part_4_composition_governance.md) amendment process if real demand pulls it (the downstream-demand-pulls-additions discipline), but it is explicitly NOT required for 1.0 — realtime collaborative apps are buildable on the transport today.

##### 5.3.3.2.3 `registry-wire` — `SealedAvChunk` wire layout (normative)

The realtime A/V chunk that lands on each RNS Link payload (and the broadcast pull path). **Byte layout (normative — transcribed from the edge v4.0.0 reference `SealedAvChunk::to_bytes`):**

```
offset  field                       encoding
0..32   stream_id                   32 bytes (caller-derived: sha256(stream_meta))
32..40  epoch                       u64 big-endian
40..48  chunk_seq                   u64 big-endian
48..49  codec_id                    u8  (§10.5.8.2 namespace)
49..50  layer.spatial               u8
50..51  layer.temporal              u8
51..52  layer.quality               u8
52..    double_sealed_ciphertext    remaining bytes
```

- `CHUNK_HEADER_LEN = 48` (the `stream_id`+`epoch`+`chunk_seq` fixed header, stable since v3.7.0); `CHUNK_CODEC_LAYER_LEN = 4` (the `codec_id`+`ChunkLayer` block).
- **Backward compatibility (normative, length-disambiguated):** a wire carrying **only** the 48-byte header (no trailing 4-byte block) MUST be read as `codec_id = 0xFF` (opaque) + `layer = {0,0,0}`, bytes `48..` as ciphertext — the v3.7.0 shape. A wire with ≥ `48+4` bytes after parsing the header is read as v3.8.0+ (codec+layer present). New writes always include the 4-byte block.
- `codec_id` + `layer` are **clear metadata, NOT inputs to the AEAD** ([CC 5.3.3.2.1](#10582-codec_id-namespace--realtime-av-chunk-codec-discriminator-normative-10-rc9--ratifies-cirisregistry84)) — a relay drops by `(codec_id, layer)` without compromising the inner DEK; tampering causes mis-decode or drop, never a crypto break.

##### 5.3.3.2.4 `chunklayer` — `ChunkLayer` + `ReceiverLayerPolicy` — SVC layer model (normative)

`ChunkLayer` is the 3-byte SVC layer descriptor in the chunk header (`spatial`, `temporal`, `quality`, each `u8`). Each axis is **monotonic**: layer `0` is the base (lowest fidelity, always required); each increment is an additive enhancement. A receiver reconstructs from the prefix `0..=max_spatial × 0..=max_temporal × 0..=max_quality` of cells. The base cell `{0,0,0}` is the **"blinking dot"** — the minimum a participant can subscribe to. For `codec_id = 0xFF` (opaque) the layer MUST be `{0,0,0}`.

`ReceiverLayerPolicy { max_spatial, max_temporal, max_quality }` (each `u8`) is the per-receiver drop policy. It is **advertised over the existing `federation_session` / `key_grant` entitlement surface — NOT a new wire** — and the sender drops chunks above the cap without re-encoding. `admits(layer)` is the per-axis test `spatial ≤ max_spatial ∧ temporal ≤ max_temporal ∧ quality ≤ max_quality`; a chunk tagged `codec_id = 0xFF` MUST be admitted **unconditionally** regardless of policy (the fan-out filter short-circuits before consulting `admits`). Canonical policies: `BLINKING_DOT = {0,0,0}`, `UNCAPPED = {255,255,255}`. This composes with the inner-once / outer-N fan-out optimization: the inner seal runs once per chunk; the outer seal runs only for the `(receiver, chunk)` pairs the policy admits.

##### 5.3.3.2.5 `stream-double` — Double-seal + deterministic nonce derivation (normative)

`double_sealed_ciphertext` is **outer-AEAD( inner-AEAD( chunk_plaintext ) )** — two independent AES-256-GCM layers (12-byte nonce + 16-byte tag, standard ring layout each). The **inner** seal is end-to-end (the epoch-DEK content seal); the **outer** seal is the per-RNS-Link transit wrap (a relay sees the outer layer only, never plaintext — the [CC 5.3.3.5 E1](#1055-streaming-deliverymodel-analysis--the-pull-defaults-the-relay-extensions) two-layer posture). Both nonces are **deterministic** (no nonce is transmitted — every holder recomputes; collision-safety rides the [CC 5.3.3.2](#1058-realtime-group-communication--composition-ceg-013-addition) single-sender-per-`(stream_id, epoch)` invariant):

```
inner_nonce = SHA-256( b"CIRIS-AV-INNER-V1" ‖ stream_id[32] ‖ epoch_be8 ‖ chunk_seq_be8 )[0..12]
outer_nonce = SHA-256( b"CIRIS-AV-OUTER-V1" ‖ link_id ‖ link_seq_be8 )[0..12]
```

The label bytes (`b"CIRIS-AV-INNER-V1"` / `b"CIRIS-AV-OUTER-V1"`, ASCII, no terminator) are **domain separators pinned by this section** — they bind the nonce to its layer and prevent cross-layer reuse. `epoch`, `chunk_seq`, and `link_seq` are `u64` **big-endian**. `link_seq` is monotonic per RNS Link (transit replay guard). **Conformance is proven by the vector set** (input → expected 12-byte nonce + expected `to_bytes`), generated from the v4.0.0 reference impl.

#### 5.3.3.3 `per-stream` — Per-stream log + stream-root (normative — V1 lock)

A live stream is its own transparency log, which is what makes a producer accountable for what it streamed: the signed roots commit the producer to a single chunk history. For each live_stream:

- `log_id = stream_id`; chunks = leaves; stream-root = `SignedTreeHead{ log_id: stream_id, tree_size: chunk_count, root_hash, timestamp, signature }`
- **Producer signs the STH — MANDATORY** authenticity root; hybrid Ed25519 + ML-DSA-65 per the [CC 5.3.1](#103-sth-cosigning--witness-directory) `signing_bytes` discipline; canonical bytes per [CC 2.6.1](part_2_the_grammar.md) JCS for the envelope-bearing wrapper
- **Witness cosign — OPTIONAL**, via the [CC 5.3.1](#103-sth-cosigning--witness-directory) path verbatim. This is the best-effort / accountable split:
  - **Best-effort** (open media) → producer-signed root only; impl-pending only
  - **Accountable** (paid media, registry propagation, emergency) → witness cosign per [CC 5.3.1.1](#1031-consistency-proof-requirement-normative-addresses-ceg-01-distsys-review) consistency-proof, which is the **anti-equivocation guarantee** — producer cannot show different chunk-K to different subscribers nor rewrite mid-stream. Accountable tier is impl-pending the streaming substrate AND STH consistency-proof enforcement
- **Cadence**: producer publishes a signed root every `K` chunks OR `T` seconds (whichever first), **always at an epoch boundary** (CC 5.1) + at `sealed_at`. Witness cosign runs **per-epoch** (coarser than per-K to keep cosign-quorum cost off the hot path). Default pins: **K=64, T=2s** (operator-tunable)
- **Incremental verify** (D4): each leaf's "root-after-K" lets a subscriber verify chunk K's inclusion against the nearest signed STH ≥ K via the [CC 5.3.1.1](#1031-consistency-proof-requirement-normative-addresses-ceg-01-distsys-review) consistency path. No new commitment structure beyond the per-leaf chain-link + periodic STH that CC 5.3.1 already provides.
- **Accountable-stream quorum**: Policy E ([CC 4.4.3.1](part_4_composition_governance.md) locality-scaled quorum) applies — not a fixed N. Emergency-channel roots want a higher quorum than a paid-media stream; locality scaling provides the gradient.

#### 5.3.3.4 `liveness` — D6 liveness invariant — entitled vs reachable (normative)

Two sets are NEVER conflated — the durable record of who is *allowed* in, and the ephemeral fact of who is *currently here*. Mixing them would turn presence into a logged, federated attestation, which the fail-secure posture forbids:

- **Entitlement roster** (Persist-owned): signed CEG envelope, Edge-propagated, durable, logged. It's **evidence** — it MUST propagate + be auditable. Per [CC 4.4.3.2](part_4_composition_governance.md) Policy M community-membership composition
- **Live-reachability set** (Edge-owned): generalizes the [CC 5.3.2.1](#1012-holder-directory-ttl--contentmiss-feedback) `EdgeConfig.holds_bytes_ttl_seconds` 24h default down to seconds-to-minutes for live-multicast. Node-local presence tracker. **NEVER an attestation, never `holds_bytes`, never replicated, never logged**

**Fan-out invariant: `fan_out(C) = entitled(C) ∩ reachable(now)`**.

**Heartbeat-suppression discipline**: this is a **producer-side-refusal invariant** (same class as the [CC 5.2](#1014-structural-invisibility--holds_bytessha256-suppression-for-cohort_scope-self--family-ceg-07-addition) `cohort_scope: self|family` `holds_bytes` suppression). Missed (entitled-but-unreachable) members fall back to pull on reconnect — substrate does NOT keep retrying push, does NOT emit a "delivery_failed" attestation, does NOT log liveness state. The reconnect-then-pull catch-up rides CC 5.1 `history_on_join`.

#### 5.3.3.5 `transport-edge` — Transport — Edge layer (normative — E1–E4 lock)

| Decision | Behavior |
|---|---|
| **E2 — pull-only RC1** | RC1 multicast = **pull-only**: producer seals chunks under the epoch DEK → emits `holds_bytes:sha256:*` → subscribers pull via the existing `ContentFetch` path. Relay / fan-out tree → 1.x |
| **E1 — two-layer crypto (security-critical)** | Transit-key is a **hop-by-hop transport wrap UNDER the E2E epoch DEK** (two independent crypto layers). MUST NOT replace the cascade — a relay never sees plaintext. Transit-key is for path-confidentiality; epoch-DEK is for end-to-end content confidentiality. **PQC in transit (normative):** BOTH layers MUST use PQC-grade key agreement — the transit-key wrap MUST be hybrid X25519+ML-KEM-768 (same `hybrid_kex` primitive as CC 5.1), and the underlying transport (Edge/Reticulum) MUST negotiate the hybrid/PQC crypto-kind (`CIR2`, per `CIRISVerify/docs/CRYPTO_AGILITY.md`), never classical-only `CIR1`. Classical-only transport is rejected for streaming. |
| **E3 — fan-out = entitled ∧ reachable** | **Persist owns durable entitlement** (the roster: signed CEG envelopes, replicated, logged). **Edge owns transport-reachability** via [`reachability.rs`](https://github.com/CIRISAI/CIRISEdge) node-local presence tracker. Fan-out targets the intersection. Reachability is NEVER an attestation, never `holds_bytes`, never replicated, never logged — consistent with the [CC 5.2](#1014-structural-invisibility--holds_bytessha256-suppression-for-cohort_scope-self--family-ceg-07-addition) `cohort_scope: self\|family` structural-invisibility shape |
| **E4 — durable side rides existing federation-attestation path** | Durable entitlement (roster + epoch-key grants) rides the **existing federation-attestation Edge path** — just more `federation_attestations` rows. NO net-new Edge transport for the durable side. Net-new is only on CC 5.3.3.3 streaming-log endpoints |

#### 5.3.3.6 `delivery` — Delivery receipts (normative — D5 / V3 lock)

A `delivery_receipt:{stream_id}` Contribution is a subscriber's signed acknowledgement that they received chunk K under the named stream + epoch. **Best-effort default**; opt-in for **accountable** profiles (registry propagation, emergency).

**Canonical bytes** (domain-separated + length-prefixed, matching `SignedTreeHead::signing_bytes` discipline; per [CC 2.6.1](part_2_the_grammar.md) the envelope-bearing wrapper is JCS-encoded, but the receipt's signed-bytes inner payload follows the explicit-length-prefix shape below):

```
receipt_signing_bytes =
    "ciris-delivery-receipt/v1"                       // domain separator
  ‖ len(subscriber_key) ‖ subscriber_key
  ‖ len(stream_id)      ‖ stream_id
  ‖ epoch        (u64 LE)
  ‖ chunk_root   ([u8; 32])
  ‖ K            (u64 LE)
```

Both `epoch` (key-rotation index — for per-epoch entitlement / billing) and `K`/`chunk_root` (chunk position + its committed root) are independent indices — both required (each names a distinct authorization scope).

**Verify check is a JOIN, NOT a sig-check**:

1. **Signature valid** over the canonical bytes (subscriber hybrid Ed25519 + ML-DSA-65 sig). Necessary but **not sufficient**.
2. **`chunk_root` is a real published STH root** — MUST equal a `SignedTreeHead.root_hash` actually published for `log_id = stream_id` at `tree_size ≥ K`. A phantom / self-invented root → REJECT. For accountable streams, "published" means **witness-cosigned** (the CC 5.3.1 path), so the subscriber cannot collude with the producer on a private root.
3. *(Recommended for accountable)* **Inclusion proof** chunk K → `chunk_root`. Upgrades the receipt from "subscriber saw a root" to "subscriber saw a root that provably commits to chunk K".

**Semantics — proof-of-DELIVERY, not proof-of-CONSUMPTION**: the receipt proves the subscriber received bytes committing to chunk K. It does NOT prove they decrypted those bytes (they may not hold the epoch DEK). Consumers MUST NOT overclaim a delivery receipt as proof of consumption. Per the [`MISSION.md`](../../MISSION.md) fail-honest invariant + [CC 1.7](part_1_foundation.md) "Verify authenticates origin, does not compose 'delivered'/'owes N'", Verify's role is validation-not-adjudication: emit the validated receipt as an attestation on `delivery_receipt:{stream_id}` — the "delivered" verdict is consumer policy.

**Accountable-stream receipt quorum**: Policy E ([CC 4.4.3.1](part_4_composition_governance.md) locality-scaled) — same shape as the CC 5.3.3.3 STH quorum.

#### 5.3.3.7 `normative` — Framing (normative)

A stream is **its own per-stream transparency-log instance** (`log_id = stream_id`). A `live_stream` MUST NOT append chunks into the federation provenance log ([CC 5.3.1](#103-sth-cosigning--witness-directory)'s global log carrying builds / licenses / identities) — millions of media chunks would pollute provenance and inflate the global tree. The CC 5.3.3 path **reuses** the CC 5.3.1 `SignedTreeHead` / `ConsistencyProof` / `WitnessConsistencyProof` / cosign abstractions, instantiated per-stream as separate log instances under the same RFC 6962 algorithm.

The 1+4 wire-format lockdown holds: there are no new `attestation_type` values. Stream chunks ride content addressing; stream-roots ride the existing `SignedTreeHead` shape; delivery receipts ride `scores` against the new `delivery_receipt:{stream_id}` reserved prefix ([CC 3.4.6](part_3_the_namespace.md)).

#### 5.3.3.8 `documents-what` — What the streaming surface documents

Scope pointer: the CC 5.3.3 streaming surface — delivery axis ([CC 5.3.3.3](#1051-per-stream-log--stream-root-normative--v1-lock)–[CC 5.3.3.4](#1056-d6-liveness-invariant--entitled-vs-reachable-normative)) — does **not** change the 1+4 primitive set ([CC 2.4](part_2_the_grammar.md)) (delivery rides existing primitives), does **not** bundle the streaming-half substrate impl (the streaming-chunk store + the parallel CHECK-arm migration), keeps push-mode multicast relay/fan-out pull-only at RC1, and leaves the K / T / MAX_CHUNKS_PER_EPOCH constants + accountable-stream quorum operator-tunable.

### 5.3.4 `multi-steward` — Multi-steward + accord-holder discovery

These endpoints publish the trust roots themselves — the steward set and accord holders — so a verifier can discover *whom* to trust before trusting anything. Every response is hybrid-signed by the serving steward, and a consumer MUST verify that signature before promoting any field to a trust root: this is the fidelity / fail-secure floor for the whole discovery surface.

### `GET /v1/steward-key`

Returns the multi-steward set with M-of-N policy.

Response (`200 OK`):

```json
{
  "stewards": [
    {
      "region": "us",
      "key_id": "us-steward-2026",
      "ed25519_pubkey_b64": "<base64-url>",
      "mldsa65_pubkey_b64": "<base64-url>",
      "hardware_class": "HSM_FIPS_140_3_L3",
      "deployed": true,
      "fingerprint_sha256_hex": "<64-char-lowercase>",
      "cert_validity_self_attest": {
        "valid_until": "<rfc3339_canonical>",
        "signature_b64": "<base64-url>"
      }
    },
    {"region": "eu", ..., "deployed": false},
    {"region": "apac", ..., "deployed": false}
  ],
  "threshold_policy": {"required": 2, "available": 1},
  "response_signature": {
    "signer_key_id": "us-steward-2026",
    "ed25519_b64": "<base64-url>",
    "mldsa65_b64": "<base64-url>",
    "canonical_bytes_label": "ciris.steward_key_response.v1"
  }
}
```

The response itself is hybrid-signed by the serving region's steward over `canonical = "ciris.steward_key_response.v1\n" || sha256_hex_lowercase(canonicalized_json_body_excluding_signature)`. Consumers MUST verify the response signature before trusting any field in the body — placeholder pubkeys without `deployed: true` MUST NOT be promoted to trust roots.

### `GET /v1/accord-holders`

Three named holders with hybrid pubkeys + per-holder `hardware_class` + `provisioned` flag. v1.4 interim ships with placeholder fingerprints + `provisioned: false`; consumers MUST NOT honor CONSTITUTIONAL invocations against placeholders. Response signed by the serving region's steward (same shape as `/v1/steward-key`).

### `GET /v1/accord/holders`

UI wrapper around `/v1/accord-holders` with per-holder `accord_emissions[]` for UI rendering. Same response-signing requirement.

### `GET /v1/rotation-history`

Chronological rotation events from `registry_signing_keys` table. Substrate-conformance migration moves to `federation_keys`.

### 5.3.5 `registry-other` — Other Registry endpoints

`GET /v1/builds/{version}` returns the BuildRecordResponse with a `federation_provenance` block. `GET /v1/verify/build-manifest/{project}/{version}/{target}` (Path B) returns the verbatim signed BuildManifest. `GET /v1/agent_files/{kind}?platform_or_target=...` returns the [CC 4.4.3.7](part_4_composition_governance.md) trust-composition layers. `GET /v1/partner/{key_id}` composes ProfileScorecard data from existing tables.

Full response schemas for these endpoints land in the Rust handlers + OpenAPI export; the spec commits to publishing a versioned OpenAPI spec alongside this document.

### 5.3.6 `common` — Common response shape

All CEG endpoints return:

- **Content-Type**: `application/json` (`Accept: application/json` honored; other types respond `406 Not Acceptable`)
- **CEG-API-Version header**: `CEG-Version: <current spec major.minor>` on every response (track the [README](README.md) `Version:` field; currently `1.0-rc27`); clients SHOULD echo `CEG-Accept-Version: <pinned-version>` on request, naming the version they were built against. Per [CC 2.6.4](part_2_the_grammar.md) SemVer policy, MAJOR mismatch is a wire-incompat reject; MINOR mismatch is compatible (clients MAY warn).
- **Time-Source header**: `X-CEG-Server-Time: <rfc3339_canonical>` per [CC 2.6.2](part_2_the_grammar.md) for client clock-skew bounds
- **Pagination** (where applicable): `?cursor=` + `?limit=` query params; response includes `next_cursor` (null if exhausted) and `total_estimate` (server's best estimate, may be approximate)

#### 5.3.6.1 `envelope-error` — Error envelope

All error responses MUST conform to:

```json
{
  "error": {
    "code": "<ENUM_VALUE>",
    "http_status": <int>,
    "message": "<human-readable>",
    "request_id": "<server-assigned>",
    "details": {<error-specific fields>}
  }
}
```

| HTTP status | Error code | Meaning |
|---|---|---|
| 400 | `MALFORMED_REQUEST` | Invalid JSON, missing required field, bad field type |
| 400 | `CANONICAL_BYTES_VIOLATION` | Date-time / hex / encoding doesn't match [CC 2.6.2 / CC 2.6.3](part_2_the_grammar.md) |
| 401 | `UNAUTHENTICATED` | Bearer token missing or invalid (admin endpoints) |
| 403 | `RESERVED_PREFIX_VIOLATION` | Producer attempted to emit under a reserved prefix without authority per [CC 3.4](part_3_the_namespace.md) |
| 404 | `UNKNOWN_WITNESS` | Witness key_id not registered in directory ([CC 5.3.1](#103-sth-cosigning--witness-directory)) |
| 404 | `NOT_FOUND` | Generic resource not found (build, partner, key) |
| 409 | `IDEMPOTENT_CONFLICT` | Replay detected (e.g., duplicate `(tree_size, witness_key_id)` cosignature with different signatures) |
| 422 | `SIGNATURE_VERIFICATION_FAILED` | Ed25519 or ML-DSA-65 failed to verify; `details.algorithm` names which |
| 422 | `CLOCK_SKEW_VIOLATION` | `signed_at` exceeds [CC 2.6.7](part_2_the_grammar.md) ±5 minute tolerance |
| 422 | `WITNESS_QUORUM_NOT_MET` | Insufficient cosignatures to validate |
| 422 | `CONSISTENCY_PROOF_INVALID` | A witness cosignature's [CC 5.3.1.1](#1031-consistency-proof-requirement-normative-addresses-ceg-01-distsys-review) consistency proof against the prior STH it cosigned is absent or does not verify. A missing proof when a prior STH exists, or a tree_size behind the witness's prior cosigned STH, is `MALFORMED_REQUEST` instead. |
| 429 | `RATE_LIMITED` | `X-RateLimit-*` headers set; `Retry-After` honored |
| 500 | `INTERNAL_ERROR` | Server-side fault; request_id usable for support |
| 503 | `WITNESS_DIRECTORY_UNAVAILABLE` | Substrate replication lag exceeds liveness bound |

Rate-limit headers on every response: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` (seconds-until-reset epoch).

## 5.4 `scope-privacy-wire` — Scope-Native Privacy wire profile

The wire-format absorption of the Scope-Native Privacy construction (the CEWP `SCOPE_PRIVACY.md` FSD; CIRISRegistry#107). These are the deterministic, byte-pinned primitives a conformant substrate uses to make real and cover traffic indistinguishable below the cohort boundary — record addressing, per-symbol AEAD, uniform fragmentation, the MLS Welcome wrap, the witness-chain discipline, and announce suppression. They are additive to the wire layer; the 1+4 surface is unchanged. Reference implementation: CIRISEdge `scope_privacy` (`derive_record_id` / `derive_symbol_key`).

### 5.4.1 `record-id` — Deterministic `record_id` (CBOR profile, normative)

Scope-native distribution addresses each record by an HMAC-opaque `record_id` rather than any plaintext key. The `record_id` is a deterministic, group-keyed commitment to the record's identity: every member of the MLS group derives the identical `record_id` for a given record, while non-members observe an unlinkable 32-byte tag. This is the addressing argument of the deterministic ALM "directory" — a pure function, never a queryable authority ([CC 4.4.3.2.1](part_4_composition_governance.md) cohort-scope lattice).

The preimage `record_id_input` is the Core Deterministic Encoding of a fixed four-entry map; `record_id` is its HMAC under the per-epoch key `K_record_id`. The preimage, the key derivation, and the resulting tag MUST be byte-identical across producer, substrate, and every consumer — any disagreement on CBOR byte order, integer minimal-encoding, major-type selection, or HKDF/HMAC suite yields a different `record_id`, silently partitioning holders of the same record. This is the same byte-exactness hazard class the STREAM nonce derivation guards ([CC 5.3.3.1](part_5_transport_substrate.md)).

**Per-epoch key.** `K_record_id` is a bare HKDF-Expand (no Extract, no MLS KDF-label framing) over the raw group `exporter_secret`:

```
K_record_id = HKDF-SHA256-Expand(
    PRK  = raw group exporter_secret,
    info = "ciris-edge/scope-privacy/record-id/v1"  (ASCII),
    L    = 32
)
```

The HKDF hash here is **SHA-256** (matching openmls ciphersuite 0x004D's key-schedule hash). Implementations MUST pass the raw `exporter_secret` to the `ciris-crypto` `scope_privacy::k_record_id` helper and MUST NOT route this label through openmls's `export_secret()` / RFC 9420 `MLS_Exporter()`.

**Preimage and commitment.** Each record:

```
record_id_input = CBOR_dCE({
    "v":   1,
    "epc": mls_group_epoch,
    "iid": internal_id,
    "typ": record_type,    // integer per RecordType table below
})
record_id       = HMAC-SHA3-256(K_record_id, record_id_input)
```

`CBOR_dCE` is RFC 8949 §4.2.1 Core Deterministic Encoding (shortest-form integer encoding, definite lengths only, no floating-point unless required), with map keys ordered **by encoded-length first, then lexicographically by encoded key bytes**. The four-entry map at `v=1` therefore serializes keys in the canonical order `v, epc, iid, typ`.

**Major types are pinned.** Within the map the four keys (`v`, `epc`, `iid`, `typ`) are CBOR text strings (major type 3). The values of `v`, `epc`, and `typ` are unsigned integers (major type 0). The value of `iid` is a **CBOR byte string (major type 2)** — `internal_id` is committed as its raw bytes, never as a text string, even when those bytes are human-readable (e.g. `record-0001`). Encoding `iid` as a text string (major type 3) produces a different preimage and a different `record_id`; the byte-string header is why the vectors below carry `0x4b`/`0x41` (major-2) and not `0x6b`/`0x61` (major-3) at the `iid` value position.

**`RecordType` integer encoding** (pinned for cross-impl conformance; CIRISConformance asserts byte-for-byte reproducibility):

| Type             | int |
|------------------|-----|
| reserved         | 0   |
| SelfRecord       | 1   |
| FamilyRecord     | 2   |
| CommunityRecord  | 3   |
| FederationRecord | 4   |

Additional record types extend this table via CEG §11.

**Conformance vectors (normative).** With `K_record_id = 0x11` repeated 32 times, conforming implementations MUST reproduce these exact CBOR preimage bytes and `record_id` tags (hex):

```
// Vector 1 — CommunityRecord (typ=3), epc=7, iid="record-0001"
record_id_input = a46176016365706307636969644b7265636f72642d303030316374797003
record_id       = 5428ddb514a8f8692cc4f254f3550ea75790f5069673e42afb6ef318517a0b21

// Vector 2 — FederationRecord (typ=4), epc=300, iid="record-0002"
//   (forces 0x19 u16 epc header: bytes[8..11] == 0x19 0x01 0x2c)
record_id_input = a46176016365706319012c636969644b7265636f72642d303030326374797004
record_id       = 04eebeee4d5b83f2fdd0012a205781e6c05fe9a587377e6161b347629a189ff2

// Vector 3 — SelfRecord (typ=1), epc=16909060 (0x01020304), iid="x"
//   (forces 0x1a u32 epc header: bytes[8..13] == 0x1a 0x01 0x02 0x03 0x04)
record_id_input = a4617601636570631a010203046369696441786374797001
record_id       = 79bee8b3f1e815a1df03ca9d83427dc5ab474e184f34e3876d3ef3c36559d6a3
```

The byte-exact source of truth is `ciris-crypto` `scope_privacy::derive_record_id` (CIRISEdge#193); the deterministic CBOR profile is normatively absorbed here per the CEG §11 record-type registry.

### 5.4.2 `symbol` — Uniform symbol AEAD framing for fountain-coded fragments (normative)

Within both encrypted crypto tiers — the self/family **InvisibleEncrypted** tier and the community/affiliations **CommunityDek** tier ([CC 4.4.3.2.1](part_4_composition_governance.md), resolved through `crypto_tier(cohort_scope, cohort_subkind)` with non-`infrastructure` subkind) — record bytes are fountain-coded (RaptorQ) and each emitted symbol is sealed under its **own** AEAD key, so a holder lacking the keys holds indistinguishable-from-random ciphertext. The two tiers differ in *discoverability*, not in fragment confidentiality: self/family content emits **no** `holds_bytes:sha256:*` holder-directory attestation at all ([CC 5.2](#52-family--structural-invisibility--holds_bytessha256-suppression-for-cohort_scope-self--family) structural invisibility) — outsiders cannot even discover the bytes exist; community/affiliations content **does** emit `holds_bytes:sha256:*` carrying cleartext provenance ([CC 4.4.3.2.1](part_4_composition_governance.md) holder-inspectability principle) so non-member holders can make an informed keep/evict decision — but the fragment bytes they hold remain sealed under the symbol AEAD below and unreadable without `K_symbol` and `record_id`. The substrate MUST seal every RaptorQ symbol with the framing below; a holder lacking both `K_symbol` and `record_id` MUST be unable to distinguish a real symbol envelope from a cover symbol envelope.

`record_id` is the per-record HMAC-opaque addressing tag for the CEG §19.3 group-keyed fountain-coding construction — `record_id = HMAC-SHA3-256(K_record_id, CBOR_dCE({v, epc, iid, typ}))`. `K_symbol` and `K_record_id` are the MLS-exporter-derived per-scope subkeys (`HKDF-SHA256-Expand` over the group's raw `exporter_secret`); both rebind on MLS Add/Remove.

For each RaptorQ symbol the wire framing is byte-exact:

```
For each RaptorQ symbol:

    symbol_key = HKDF-SHA3-256(salt=record_id, ikm=K_symbol,
                               info="ciris-edge/scope-privacy/symbol/v1"
                                    || u16_be(symbol_index), len=32)
    symbol_envelope = (record_id, u16_be(symbol_index), nonce,
                       XChaCha20-Poly1305(symbol_key, nonce, fragment), tag)
```

Normative constraints:

- **`symbol_key` derivation is byte-identical across every implementation.** `salt = record_id` (the 32-byte HMAC tag), `ikm = K_symbol` (the 32-byte exporter subkey), and `info` is the **exact** concatenation of the UTF-8 bytes of the ASCII label `ciris-edge/scope-privacy/symbol/v1` followed by `u16_be(symbol_index)` (the symbol index as a 2-byte big-endian unsigned integer), with `len = 32`. The same ASCII label is used both to derive `K_symbol` from the MLS exporter and as this info-prefix; producer, substrate, and every consumer MUST recompute this exact value. Any BE/LE disagreement on `symbol_index`, or any drift in the label bytes, yields a different `symbol_key` → AEAD authentication failure (silent decryption failure). This matches `ciris_crypto::scope_privacy::derive_symbol_key` and the pinned `LABEL_SYMBOL` constant; CIRISConformance asserts byte-for-byte reproducibility.
- **The AEAD is XChaCha20-Poly1305 with a 24-byte `nonce` and the Poly1305 `tag`** carried in the envelope. The same suite seals **both** real fragments and cover fragments — there is no separate cover cipher, no cover marker, and no length distinguisher. A holder lacking `K_symbol` and `record_id` holds indistinguishable-from-random bytes (Tahoe-LAFS least-authority, by reduction to XChaCha20-Poly1305 IND-CCA + HKDF-SHA3 extract-then-expand); cover and real envelopes are observationally identical.
- **The fragment-set rebinds on MLS Add/Remove.** Because `symbol_key` chains from `K_symbol` and `record_id`, both of which rotate with the group epoch, a removed member's symbol keys do not open post-epoch fragments. Past-epoch `K_record_id` / `K_symbol` are deleted by honest holders per the community's archive policy.
- **`symbol_envelope` field order is fixed: `(record_id, u16_be(symbol_index), nonce, ciphertext, tag)`.** The cleartext `record_id` and `symbol_index` are the addressing argument to the HMAC-opaque directory function (the CEG §19.4 deterministic ALM topology) and are NOT authority-bearing — they reveal nothing to a non-member, who cannot derive the corresponding `symbol_key`.

This framing is the byte-level analogue of the [CC 5.3.3.1](#5331-stream--chunk-seal--stream-nonce-normative--v2-lock) per-chunk stream seal: the costly key agreement is amortized into the MLS exporter, and the hot path is a per-symbol symmetric AEAD with a deterministically derived key. It composes with — and never substitutes for — the at-rest DEK cascade ([CC 4.4.3.4.1](part_4_composition_governance.md)); the symbol AEAD protects fragments in transit and at holders, the DEK cascade protects the record at rest.

### 5.4.3 `fragmentation` — Uniform-envelope fragmentation & reassembly (normative)

A claim's bytes rarely fit one packet, and the split is where privacy is most easily lost: a naive fragmenter leaks payload size, count, and cadence to anyone on the path. The discipline here is that every fragment on the wire — a real publication symbol or a synthetic cover envelope — is the **same size** and the **same AEAD shape**, so an on-path observer cannot distinguish a large publication from idle substrate maintenance. This composes with the chunk-seal of [CC 5.3.3.1](#1052-chunk-seal--stream-nonce-normative--v2-lock) (a *different* axis: streaming media chunks) — fragmentation is the substrate-emission layer beneath every Edge `send`, not the streaming codec.

**Fixed envelope size (normative).** All outbound substrate traffic MUST conform to a fixed envelope size of **1.4 KB**, one MTU. A payload larger than one envelope MUST be chunked per this section; a payload smaller MUST be padded to the fixed size before emission. The fixed size is not a tuning knob — a variable envelope re-exposes the size channel the cover budget exists to close (the companion Poisson-cover emission discipline; budget anchor is the substrate-maintenance throughput, ~10–60 KB/s/peer).

**Uniform AEAD framing across real + cover (normative).** Every envelope — real publication AND synthetic cover alike — MUST use uniform **XChaCha20-Poly1305** AEAD framing. A synthetic cover envelope MUST be marked `type=cover` in the **AEAD-protected** header; the `type` discriminator MUST live inside the AEAD envelope so an on-path observer cannot separate real from cover by inspecting cleartext. This XChaCha20-Poly1305 envelope/symbol framing is distinct from the streaming chunk-seal AES-256-GCM of [CC 5.3.3.1](#1052-chunk-seal--stream-nonce-normative--v2-lock) and from the HPKE-layer AES-256-GCM of the MLS Welcome wrap; they are different layers and MUST NOT be conflated.

**Fragment unit — the RaptorQ symbol envelope (normative — wire-exact).** A chunked record is fountain-coded with RaptorQ defaults `(N=20, K=6, target_holders=30)`. Each symbol is sealed independently, with a per-symbol key diversified from the group `K_symbol` (MLS exporter-derived per the [CC 5.1](#1053-epoch-keying--cascade-normative--d2--d3-substrate-pending-142) epoch key schedule) and the record's `record_id` (the deterministic-CBOR `record_id` profile):

```
symbol_key = HKDF-SHA3-256(salt=record_id, ikm=K_symbol,
                           info="ciris-edge/scope-privacy/symbol/v1"
                                || u16_be(symbol_index), len=32)
symbol_envelope = (record_id, u16_be(symbol_index), nonce,
                   XChaCha20-Poly1305(symbol_key, nonce, fragment), tag)
```

The per-symbol KDF is **HKDF-SHA3-256** — harvest-now-decrypt-later (HNDL) discipline at the per-symbol layer, deliberately distinct from the SHA-256 key-schedule hash used one layer up. The `info` string `"ciris-edge/scope-privacy/symbol/v1"` (ASCII) concatenated with `u16_be(symbol_index)` is normative and MUST be byte-identical across producer, substrate, and every consumer; a `u16_be` / `u16_le` disagreement on `symbol_index` yields a different `symbol_key` → AEAD verify failure on reassembly. Without `K_symbol` and `record_id`, a holder possesses bytes indistinguishable from random (Tahoe-LAFS least-authority, by reduction to XChaCha20-Poly1305 IND-CCA + HKDF-SHA3 extract-then-expand) — the structural basis for a holder's truthful cold-state-ignorance claim.

**Fragment-set rebinds on MLS Add/Remove (normative).** `K_symbol` and `K_record_id` are bound to the MLS group epoch (derived from the group `exporter_secret`). On any MLS **Add** or **Remove** the group epoch advances, so the fragment set MUST rebind: `record_id` and `symbol_key` are recomputed under the new epoch, and subsequent symbols seal under the new keying. This carries the forward-secrecy guarantee of [CC 5.1](#1053-epoch-keying--cascade-normative--d2--d3-substrate-pending-142) onto the fragment layer — a removed member cannot derive the post-removal fragment set, and a newly-added member receives forward keying without retroactive symbol access except as the archive policy permits (the companion per-community archive-policy section; default `rotate-forward`, 30-day window).

**Reassembly (fail-honest).** A consumer holding `K_symbol` + `record_id` collects symbol envelopes from holders ([CC 5.3.2.1](#1012-holder-directory-ttl--contentmiss-feedback) holder discovery), opens each `symbol_envelope` under its recomputed `symbol_key` (XChaCha20-Poly1305 verify; a failed tag MUST discard that symbol, never accept partial plaintext), and RaptorQ-decodes once `≥ K` valid symbols are recovered. Insufficient surviving symbols MUST resolve to a `ContentMiss` — an honest miss, never a silent gap or a downgrade to unverified bytes ([fail-honest](../../MISSION.md)).

### 5.4.4 `welcome-wrap` — MLS Welcome HPKE wrap under invitee static X-Wing key (normative)

MLS Welcome messages MUST be wrapped by **HPKE `mode_base`** ([RFC 9180](https://www.rfc-editor.org/rfc/rfc9180) §5.1.1) encrypted to the invitee's **static X-Wing KEM** public key (ML-KEM-768 + X25519; [draft-connolly-cfrg-xwing-kem](https://datatracker.ietf.org/doc/draft-connolly-cfrg-xwing-kem/); confirmed in [draft-ietf-hpke-pq](https://datatracker.ietf.org/doc/draft-ietf-hpke-pq/) §7.2). This is the admission-ceremony half of the MLS construction whose epoch rekey is specified in [CC 5.1](part_5_transport_substrate.md) — the same hybrid KEM (X25519 + ML-KEM-768) the MLS ciphersuite uses as its HPKE KEM.

**`mode_auth` is structurally unavailable.** X-Wing has no `AuthEncap` (per draft-connolly-cfrg-xwing-kem; confirmed in draft-ietf-hpke-pq §7.2), so HPKE `mode_auth` cannot be used. Sender authentication therefore MUST NOT be claimed at the HPKE layer; it is provided out-of-band by an **ML-DSA-65 signature from the inviter** over the encapsulation bytes (below). Both halves of MLS ciphersuite `0x004D` are used.

**HPKE parameters (cross-impl pinned; private-use suite-id, since X-Wing has no IANA KEM-id):**

```
HPKE_SUITE_ID = b"HPKE-xwing-hkdf-sha256-aes256gcm-v1"
KDF           = HKDF-SHA256
AEAD          = AES-256-GCM
```

The `HPKE_SUITE_ID` string MUST be used, byte-for-byte identically on both sides, in every RFC 9180 `LabeledExtract` / `LabeledExpand` call. The HPKE-layer AEAD is **AES-256-GCM** — distinct from the XChaCha20-Poly1305 the CEWP substrate uses to protect fountain symbols and envelope fragments at its lower layers.

**Inviter signature.** The inviter MUST sign the encapsulation bytes with ML-DSA-65 over the following length-delimited encoding (no `algorithm` field):

```
encap_signing_bytes
    = x25519_ephemeral_pub      (32 bytes)
    || u32_be(len(mlkem768_ct))
    || mlkem768_ciphertext
```

Signature verification is a **precondition** to unwrapping the Welcome. An implementation that omits it forfeits sender authentication, and the [CC 5.2](part_5_transport_substrate.md) forwarder-side membership-opacity guarantee no longer holds.

### 5.4.5 `witness-content` — Witness-chain content discipline (privacy witness, normative)

A witness chain that names *what* a peer holds leaks the existence of its records as surely as a holder-discovery attestation does ([CC 5.2](#1014-structural-invisibility--holds_bytessha256-suppression-for-cohort_scope-self--family-ceg-07-addition)). The content a witness chain may commit to is therefore scoped by tier, and the federation tier additionally **hides its own rate** so that the *amount* of non-federation activity cannot be read off the chain.

> **Distinction (normative — do NOT conflate).** This is the **privacy witness chain** — a content-and-rate discipline on what a peer's witness commitments may reveal. It is NOT the [CC 6.1.1](part_6_the_coherence_mathematics.md) **WholenessWitness** (`wholeness_witness:`, the self-published divergence-detection state-root that triggers [CC 5.3.2.3](#1016-cross-region-merge-intents--ceg-declared-per-subject_kind-normative-ceg-10-rc2-addition) quorum-merge), and it is NOT the [CC 5.3.1](#103-sth-cosigning--witness-directory) **transparency-log witness** (an independent STH cosigner providing append-only / consistency / anti-equivocation guarantees). The three "witness" surfaces are distinct constructions, MUST NOT be cross-verified, and MUST NOT be substituted for one another.

**Federation witness chain — commits to federation-scope `record_id`s + a single rate-smoothed constant-tick counter.** A federation witness chain MUST commit only to federation-scope `record_id`s plus a single rate-smoothed counter for all non-federation activity. The counter ticks on a federation-wide **constant** schedule — **1 tick / federation epoch** ([CC 5.1](#1053-epoch-keying--cascade-normative--d2--d3-substrate-pending-142)) — independent of how much real activity occurred. At each tick the witness commits to a target-relative count, padding below-target ticks with cover leaves and back-pressuring above-target leaves into the next tick:

```
At each federation epoch tick the witness commits to `count mod target_rate`:
real leaves below target are padded by cover leaves to the target;
real leaves above target back-pressure into the next tick.
Cover leaves commit to
`HMAC-SHA3(witness_signing_key, leaf_position || epoch_id)`
— cryptographically indistinguishable from real Merkle roots
under the IND of HMAC-SHA3.
```

Because the tick is constant and the per-tick commitment is `count mod target_rate` smoothed by IND-indistinguishable cover leaves, an observer of the chain learns neither the true non-federation activity rate nor which leaves are real. **The signal is the deviation, not the count**: a witness that fails to tick on the constant schedule has emitted the only observable signal the chain carries, and **deviation from the constant tick is a federation-tier slashing condition**.

**Per-community witness chain — member-only visibility, signed inside the group.** A per-community ([CC 3.2](part_3_the_namespace.md)) witness chain MUST commit to the community's `record_id` set with **member-only visibility**, and MUST be **signed inside the community's MLS encryption** ([CC 5.1](#1053-epoch-keying--cascade-normative--d2--d3-substrate-pending-142) epoch keying / [RFC 9420](https://www.rfc-editor.org/rfc/rfc9420) TreeKEM). The chain — like the in-group trust graph, attestation, and eviction machinery — runs *inside* the same encryption boundary that delivers outsider opacity: a non-member cannot read the community's `record_id` set off the chain, because the chain never federates beyond the group's encryption. There is no constant-tick rate counter at the community tier; rate-hiding is a federation-tier concern (the federation chain already smooths *all* non-federation activity, of which per-community activity is a part).

This codifies CEWP `SCOPE_PRIVACY` §3.4 ([#107](https://github.com/CIRISAI/CIRISRegistry/issues/107)) as a normative substrate discipline, composing with the [CC 5.2](#1014-structural-invisibility--holds_bytessha256-suppression-for-cohort_scope-self--family-ceg-07-addition) structural-invisibility promise: structural invisibility keeps self/family content off the discovery surface; the witness-content discipline keeps the *witness* surface from re-leaking, at federation scope, what the discovery surface withholds.

### 5.4.6 `announce-suppress` — Announce suppression for group-scoped destinations (normative)

A Reticulum **announce** is the broadcast that tells the whole network a destination exists and is reachable. Announcing a *group-scoped* destination therefore leaks the one fact the cohort tiers exist to withhold: that the group exists at all. The discovery discipline closes that leak — group destinations are resolved from a **cached directory + per-group HKDF**, never from an announce. This is the transport-layer realization of [CC 5.2](part_5_transport_substrate.md) structural invisibility on the *addressing* plane: bytes are already suppressed from the holder directory ([CC 5.3.2.1](part_5_transport_substrate.md)) by the [CC 5.2](part_5_transport_substrate.md) `holds_bytes:sha256:*` suppression rule; here the **destination itself** is suppressed at the announce plane.

**No announce for group-scoped destinations (normative).** A destination whose `cohort_scope` is below federation (the InvisibleEncrypted and CommunityDek tiers — `self`, `family`, `community`, `affiliations`) MUST NOT emit a Reticulum announce. The substrate MUST suppress the announce that would reveal a group-scoped destination's existence. Only federation/Commons-scope destinations (`species`, `biosphere`, `federation`, and the `infrastructure` opt-out) MAY announce normally — they carry no anonymity claim.

**Discovery is directory-cached, not announced (normative).** Group members resolve each other's destinations from a locally cached directory plus a deterministic per-group derivation — no announce, no per-resolution query:

```
- Every participating L1 peer maintains a COMPLETE local copy of the
  federation directory's X-Wing public keys, refreshed via the existing
  `federation_keys` anti-entropy. The directory remains federation-public.
- A group destination is resolved DETERMINISTICALLY from
  (cached directory entry + per-group HKDF) — every member derives the
  same destination; outsiders, lacking the group key, cannot.
- NO per-invitation / per-resolution directory query is emitted.
- Phone-class peers that cannot hold the full directory resolve through
  their L1-relay parent over a relay-blinded path.
```

The per-group HKDF derivation is the same group-and-epoch-bound key schedule the substrate already uses to diversify record-ids and symbols; destination resolution reuses it, so the addressing argument is HMAC-opaque to non-members and no new key material is introduced.

**The anonymity target is outsiders, not in-group members (normative framing).** Trust-enforceability to insiders and anonymity to outsiders are the same property viewed from opposite sides of the cohort encryption boundary ([CC 1.13.3.4](part_1_foundation.md)). In-group members already hold the per-group key and resolve every peer's destination from the cache — they see the group fully. The construction hides the group's existence, membership, and `querier → invitee` edges from **outsiders only**, including a subpoena against the federation-public directory: because no announce is broadcast and no resolution query is emitted, the directory exposes no edge linking a resolver to the resolved destination.

**Fail-secure.** A peer with a stale or incomplete directory cache resolves *fewer* destinations and reports an honest miss; it MUST NOT fall back to emitting a group-scoped announce or a per-destination query to recover reachability. Per-destination announce control is a small Leviculum substrate extension (informative); its absence MUST fail toward suppression, never toward announce.
