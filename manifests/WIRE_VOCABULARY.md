# CIRIS Federation Wire Vocabulary

**Constitution:** CC (CIRIS Accord) 0.7 — wire vocabulary as a hash-pinned constitutional artifact
**Artifact steward:** CIRISRegistry (`manifests/WIRE_VOCABULARY.md`)
**Vocabulary version:** v1.0.1 (ratified baseline; v1.0.1 adds the §3.3 migration-semantics clarification — schema+canonicalization move to the range steward, not just the wire discriminator)
**Vocabulary hash:** `sha256(` canonical bytes of this document `)` — computed at build time, pinned by every ratifying repo (§4)
**Implements:** CIRISRegistry#130
**Status:** DRAFT for the coordinated v8.0.0 substrate cut

---

## 0. Preamble — what this document is, in constitutional terms

The CIRIS federation substrate carries signed envelopes between peers. The *set of message types the substrate recognizes* is not the emergent residue of whatever `CIRISEdge/src/messages/mod.rs::MessageType` happens to hold after N cuts — it is a **ratified contract** that binds every peer to a single interpretation of the same bytes. This document is that contract.

The vocabulary is **two-tier**, and the two tiers map onto two long-proven governance postures rather than novel machinery. We deliberately reuse **RFC 8126** (*Guidelines for Writing an IANA Considerations Section*) registration-policy vocabulary so the discipline is recognizable to any protocol engineer:

- **Tier 1 — constitutional `MessageType` variants** correspond to RFC 8126 **"Standards Action"**. The set is *closed*: adding, removing, or changing the semantics of a Tier-1 variant is a wire break that rides **the ordinary CC §4.5.1 amendment path** — draft in CIRISRegistry, review by the covenant of ratifying repos (§5), ratification, coordinated cut. A Tier-1 variant is admitted only when its canonicalization is *load-bearing to an ethical primitive*: an attestation, a vote, a moderation/slashing event, a deferral, a steward directive, a key registration, the humanity-accord announcement path, a consent withdrawal, an M-1-aligned goal, build provenance, a signed holding claim, or the content-addressed fetch substrate the whole mesh relies on. This is `MessageType` as *closed federation vocabulary* — the [CIRISEdge §3.302] threat (*"ambiguity is how a buggy peer or a Sybil claims something a peer never said"*) is defeated only if every peer parses these bytes identically.

- **Tier 2 — app-tier opaque channels** correspond to RFC 8126 **"Private Use"** (and "Specification Required" within a range steward's own repo). The substrate reserves exactly **three** opaque envelope variants (`OpaqueRequest` / `OpaqueResponse` / `OpaqueEvent`) carrying a `kind: u32` drawn from a **reserved per-repo range table** (§3.1). Edge treats the `payload` as opaque bytes; the *app* owns inner-semantic canonicalization and signs its own inner body. Allocation and documentation within a range is **delegated to the range steward** — no CC amendment is required to define a new `kind`, exactly as no IANA action is required to use a Private-Use code point.

**Prior art this design is copied from, not invented against:**

- **Nostr `kind` ranges** — a flat `u32`-ish `kind` field partitions the event space into regular / replaceable / ephemeral / addressable bands owned by NIPs. Our §3.1 range table is the same idea, but **CC-anchored, not NIP-anchored**: ranges are owned by ratifying repos and governed by this artifact.
- **Matrix reverse-DNS event types** (`m.*` reserved for the spec, `com.example.*` for everyone else) — a namespace whose "official" band is spec-governed and whose vendor band is delegated. Tier 1 is our `m.*`; Tier 2 `kind` ranges are our vendor namespace.
- **RFC 8126** — the registration-policy spectrum ("Standards Action" ⟶ "Private Use") is the exact lever we pull: high-ceremony for the ethical core, zero-ceremony for app RPC.

The point of two tiers is to stop the **category error** of letting an app-tier RPC (e.g. a mesh control-plane call) drive a federation-tier wire break. App RPC belongs in Private Use; only ethical primitives earn Standards Action.

---

## 1. The envelope + the one canonicalization anchor

Every message on the wire is a single **`EdgeEnvelope`** (`CIRISEdge/src/messages/mod.rs::EdgeEnvelope`). Its shape is the outer contract; `message_type` is the discriminator this document enumerates; `body` is preserved verbatim as a `RawValue` so verification sees exactly the bytes the sender signed.

Canonical bytes for the envelope signature come from **one** function and one function only:

> `ciris_persist :: canonicalize_envelope_for_signing()` (CIRISPersist#7; strips `signature` / `signature_pqc` before canonicalizing).

**No consumer reimplements canonicalization.** This is the AV-5 closure and the [CIRISEdge MISSION §6 anti-pattern 2] rule: a second implementation of "the canonical bytes" is a second, silently-diverging wire format. Edge dispatches on `message_type` *after* verify; handlers receive parsed body structs, never raw bytes.

Envelope-shape versioning (`SchemaVersion`) is **orthogonal** to vocabulary versioning. A Tier-1 additive amendment bumps the vocabulary MINOR; it does **not** bump `SchemaVersion` unless the `EdgeEnvelope` struct itself changes shape. A semantic change / removal bumps vocabulary MAJOR and `SchemaVersion` in lockstep.

Signatures are hybrid throughout: Ed25519 (mandatory) + ML-DSA-65 (`signature_pqc`, required once the sender's `federation_keys` row is hybrid-complete). The outer envelope signature proves **transport-tier fed-key provenance**. For Tier-2 opaque channels, any *semantic* inner signature lives inside `payload` and is the app's responsibility.

---

## 2. Tier 1 — constitutional `MessageType` variants (closed; CC §4.5.1 / Standards Action)

25 variants. Each row: **delivery class** · one-line contract. Body structs live in the named consumer crates; edge stays domain-agnostic.

### 2.1 Attestations (signed standing claims)

| Variant | Delivery | Contract |
|---|---|---|
| `AttestationGossip` | Durable (fire-and-forget) | Peer A vouches for peer B's key; transparent over persist `SignedAttestation`. The signed attestation is the trust edge peers merge (AV-1/AV-9). |
| `DeliveryAttestation` | Durable (fire-and-forget) | Per-peer proof a `FederationAnnouncement`/`StewardDirective` reached the app layer; `canonical_bytes` domain-separated + LOCKED cross-repo (FSD §3.2.1). The attestation IS the governance audit observable. |
| `DeliveryRefusalAttestation` | Durable (fire-and-forget) | Signed refusal when the AccordCarrier 2-of-3 multi-sig fails; `RefusalReason` distinguishes suppression of legitimate accords from suppression of forged ones. |
| `ExpertiseAttestationPublish` | Durable (requires_ack) | Expertise attestation (NodeCore SCHEMA §7); signed standing claim underpinning trust-weighting. |
| `FountainHoldingClaim` | Ephemeral (fire-and-forget) | Signed federation holding claim over the LOCKED v1 `HOLDING_CLAIM_DOMAIN` canonical bytes. Fire-and-forget delivery, but the domain-separated bytes are the trust primitive. |

### 2.2 Ballots, moderation & due process

| Variant | Delivery | Contract |
|---|---|---|
| `ContributionSubmit` | Durable (requires_ack) | The signed governance object votes/moderation/slashing bind to (SCHEMA §3). *(Borderline — a submission, not a ballot — but every downstream ballot references its canonical bytes.)* |
| `VoteCast` | Durable (requires_ack) | Vote on a Contribution (SCHEMA §5); identical canonicalization is what makes a vote uncounterfeitable. |
| `ModerationEventPublish` | Durable (requires_ack, witness-set-required) | Moderation event (SCHEMA §8); witness set makes canonicalization consensus-critical. |
| `SlashingAttestationPublish` | Durable (requires_ack, witness-set-required) | Punitive standing change (SCHEMA §8); byte-ambiguity would let a Sybil slash an innocent peer. |
| `ReconsiderationRequest` | Durable (requires_ack, witness-set-required) | Appeal of a moderation/slashing outcome (SCHEMA §9); the due-process half of the ballot family. |

### 2.3 Deferral / Wisdom-Based Deferral

| Variant | Delivery | Contract |
|---|---|---|
| `DeferralRequest` | Durable (requires_ack) | Generalizes CIRISNode WBD submit (SCHEMA §4.7). |
| `DeferralResponse` | Durable (requires_ack) | Routed Wise-Authority signed response (SCHEMA §4.8); the WA signature over canonical bytes is the authority primitive. |

### 2.4 Steward & humanity-accord governance

| Variant | Delivery | Contract |
|---|---|---|
| `StewardDirective` | Federation (`priority: StewardClass`) | Steward-class directive; recipient set derived from persist `federation_keys` where `identity_type = "steward"`. Emits `DeliveryAttestation` per peer. |
| `FederationAnnouncement` | Mandatory (`authority_signed`, `bypass_subscription`) | The announcement / humanity-accord path. `AccordCarrier` priority is constitutionally bound to `AuthorityClass::HumanityAccord` under the 2-of-3 `ACCORD_THRESHOLD_M_OF_N`; `canonical_bytes_for_accord_signatures` domain is LOCKED cross-repo. `bypass_subscription` reach is the Justice-failure-mode guarantee. |

### 2.5 Key & identity registration

| Variant | Delivery | Contract |
|---|---|---|
| `PublicKeyRegistration` | Durable (requires_ack) | New-peer key registration into the federation directory (transparent over persist `SignedKeyRecord`); the root of all downstream signature trust. |

### 2.6 Provenance & mission alignment

| Variant | Delivery | Contract |
|---|---|---|
| `BuildManifestPublication` | Durable (requires_ack) | Hybrid-signed build manifest → registry; SLSA-tier build-legitimacy provenance. *(Body is a `serde_json::Value` at the current cut — CIRISEdge#TODO to swap to a typed shape; the Tier-1 admission is on the primitive, the tight typed canonicalization follows.)* |
| `GoalDeclaration` | Durable (requires_ack) | Wraps persist typed `Goal` whose `MetaGoalAlignment` is a construction-time invariant — every Goal on the wire carries an M-1 alignment payload. |
| `GoalRetirement` | Durable (requires_ack) | Single-signer retirement of a declared Goal; the envelope hybrid signature IS the proof-of-authority. Lifecycle half of the M-1 Goal primitive. |

### 2.7 Consent / trust-graph retraction

| Variant | Delivery | Contract |
|---|---|---|
| `Withdraws` | Durable (fire-and-forget) | Consent/withdrawal — a 1+4 CEG relation (consumer downweight of a holder that failed to serve advertised bytes; delegation-retraction signal, CEG §10.1.2). A signed trust-graph edge, not app content. Fire-and-forget (same shape as `DeliveryAttestation` — the withdrawal IS the observable; no second ACK). |

### 2.8 Content-addressed fetch substrate

The integrity primitive here is **`sha256(body)` itself**, not an inner signature — the whole mesh depends on identical hashing and identical `MissReason` handling. Whole-file (`Content*`) and chunked-swarm (`BlobChunk*`) form two parallel fetch triples. Edge is not a passive carrier here: `dispatch_inbound` itself enforces `sha256(bytes) == claimed` on `ContentBody` before handler dispatch, and the shared `MissReason` vocabulary carries federation-trust states (`Withdrawn`/`Revoked`) every peer must read identically — which is exactly why this substrate is closed-vocabulary Tier-1 rather than an opaque channel.

| Variant | Delivery | Contract |
|---|---|---|
| `ContentFetch` | Ephemeral (request/response) | Request the bytes hashing to `sha256`; retryable, on-demand pull. |
| `ContentBody` | Ephemeral (response) | Carries the bytes; receiver MUST verify `sha256(bytes) == claimed` on receipt. AV-13 16 MiB ceiling. |
| `ContentMiss` | Ephemeral (response) | Typed refusal (`NotHeld`/`Withdrawn`/`Revoked`/`PolicyDenied`) so the fetcher fails over rather than hangs. |
| `BlobChunkFetch` | Ephemeral (request/response) | Request one chunk keyed by `(blob_sha256, chunk_sha256)`. |
| `BlobChunkBody` | Ephemeral (response) | Carries chunk bytes; persist `put_blob_chunk` atomically verifies `sha256(bytes) == chunk_sha256` or returns `ChunkMismatch`. |
| `BlobChunkMiss` | Ephemeral (response) | Chunk-level typed refusal sharing the `ContentMiss` `MissReason` vocabulary. |

---

## 3. Tier 2 — app-tier opaque channels (Private Use; delegated to range stewards)

The substrate has **exactly three** opaque channel variants and no others. Edge carries `payload` as opaque bytes and enforces only the outer envelope signature + the global body caps (§3.2). Inner-semantic canonicalization and any inner signature belong to the app.

```rust
OpaqueRequest  { kind: u32, payload: Vec<u8> }              // ephemeral; expects OpaqueResponse
OpaqueResponse { kind: u32, status: u16, payload: Vec<u8> } // ephemeral; response to a request
OpaqueEvent    { kind: u32, payload: Vec<u8> }              // fire-and-forget (durable retry, no ack)
```

**Delivery classes:** `OpaqueRequest` + `OpaqueResponse` are Ephemeral (request/response); `OpaqueEvent` is Durable/fire-and-forget.

**Delivery-expressiveness limit (covenant-review item).** The three opaque variants deliberately cover only {ephemeral request/response, durable fire-and-forget}. They CANNOT express **Durable + requires_ack** (a durable request whose sender needs an observable completion receipt). Any Tier-2 migrant that currently rides Durable/requires_ack (see §3.3 — `DSARRequest`, and the `InlineTextDurable` sender variant of `InlineText`) either downgrades to Ephemeral on migration or must model completion as a separate durable `OpaqueEvent` receipt. Where the completion guarantee is load-bearing (erasure confirmation), this is a reason to keep the variant in Tier-1 rather than migrate — resolved per-variant at covenant review, not assumed.

**Unknown-`kind` rule:** a peer that receives a `kind` it does not implement returns `OpaqueResponse { status: 501 }` — never a silent drop ([CIRISEdge MISSION §6 anti-pattern 7]).

### 3.1 Reserved `kind` ranges (16-bit sub-range per repo; RFC 8126 Private Use)

| Range | Steward | Scope |
|---|---|---|
| `0x0000_0000..=0x0000_FFFF` | CIRISServer | mesh control plane (CIRISEdge#240 lives here) |
| `0x0001_0000..=0x0001_FFFF` | CIRISLensCore | relay + client-mode control |
| `0x0002_0000..=0x0002_FFFF` | CIRISNodeCore | federation coordinator |
| `0x0003_0000..=0x0003_FFFF` | CIRISRegistry | registry-tier queries |
| `0x0004_0000..=0x0004_FFFF` | CIRISAgent | agent-tier (inline chat, etc.) |
| `0x0005_0000..=0x0005_FFFF` | CIRISPersist | persist-tier telemetry (trace batches, DSAR) |
| `0x0006_0000..=0x0006_FFFF` | CIRISVerify | verify-tier probes |
| `0x0007_0000..=0x0007_FFFF` | CIRISConformance | conformance harness reach-through |
| `0xFFFF_0000..=0xFFFF_FFFF` | experimental / unallocated | peers negotiate; never assume stability |

**CIRISEdge holds no Tier-2 kind range by design.** Edge owns the substrate and the entire Tier-1 closed vocabulary itself; it has no app-tier RPC of its own. Edge's mesh-control-plane calls (e.g. CIRISEdge#240) are allocated in **CIRISServer's** range, above. This is intentional, not an omission.

Each range steward publishes a `WIRE_VOCABULARY_KINDS.md` in its own repo documenting `kind → semantics`. Edge does not know or enforce what a `kind` means.

### 3.2 Global caps (both tiers)

`MAX_BODY_BYTES` (currently 8 MiB) and `MAX_DATA_DEPTH` (32) bound every body (AV-13, AV-14). App-tier consumers should assume the cap and MAY declare a smaller per-`kind` sub-cap in their own kinds doc.

### 3.3 Variants migrating from `MessageType` into Tier 2 at v8.0.0

The following current `MessageType` variants are **app-tier** by the ethical-primitive test and migrate to opaque channels under the noted range. Their inner bytes are already the app's/persist's concern; the substrate need not close-vocabulary them.

> **What "migrate to Tier-2" means — normative, so it cannot be misread.** Migration moves the **schema, its canonicalization, AND the convenience API into the range steward's own repo**. It is **NOT** satisfied by swapping the wire discriminator to opaque while the typed struct and its `canonical_bytes` remain in CIRISEdge. A retained `struct InlineText` + `canonical_bytes(InlineText)` inside the transport tier keeps the transport **owning app semantics** — the exact category error this migration exists to remove.
>
> **Rationale (CIRISEdge MISSION.md).** §1.3 — *"the policy tier owns its own meaning; edge is reach, not meaning"* — and §6 anti-pattern 2 — *"edge re-implements no canonicalization; canonical bytes come from the authority, never edge."* A migrant whose canonicalization stays in edge violates both.
>
> **Therefore, post-migration:**
> - **CIRISEdge** exposes only the **generic** Tier-2 surface — `send_opaque_event` / `send_opaque_request` / `subscribe_opaque(range)` — and carries `payload` as opaque bytes. It holds no typed struct, trait, or `canonical_bytes` for any migrant.
> - **The range steward's repo** owns the migrant's schema + canonicalization + inner signature, documented in its `WIRE_VOCABULARY_KINDS.md`, and **re-exposes the same-signature convenience method** (e.g. CIRISAgent's `send_inline_text(text)`) as a thin wrapper over `edge.send_opaque_event(kind, app_canonicalize(text))`.
> - **API impact:** the *app-level* API stays stable (callers of `agent.send_inline_text(...)` see no change); the only thing that changes is that a call to the *transport's* `edge.send_inline_text(...)` — the layering inversion itself — no longer exists. "App owns meaning" is honored **on the wire and in the stewardship graph**, not just the discriminator.

**`DSARRequest` / `DSARResponse` stay Tier-1** (resolved, not migrated): data-subject access/erasure is rights-bearing (consent-weight, adjacent to `Withdraws`) **and** rides Durable/requires_ack — the erasure-completion receipt the opaque model cannot express (§3 limit). It keeps its closed, ack-bearing schema. Should a durable, ack-bearing opaque channel ever be added, DSAR MAY be revisited; until then it is not a migrant.

| Current variant | Migrates to | Suggested steward range | Note |
|---|---|---|---|
| `AccordEventsBatch` | `OpaqueEvent` | CIRISPersist `0x0005_*` | Trace/telemetry; hash-chain verify + scrub + persist happen inside lens/persist, edge is agnostic. |
| `InlineText` | `OpaqueRequest` / `OpaqueEvent` | CIRISAgent `0x0004_*` | Inline agent chat text; app owns meaning. Producer-side `speak_pipeline` scrub is an app concern, not substrate canonicalization. The sender's `InlineTextDurable` (Durable/requires_ack) loses its ACK on migration — see the §3 delivery-expressiveness limit; chat-tier completion is not load-bearing, so this is acceptable. |
| `FederationKeyDirectoryQuery` | `OpaqueRequest` / `OpaqueResponse` | CIRISRegistry `0x0003_*` | Pure directory lookup; the `KeyRecord` it returns is separately attested via the Tier-1 registration/gossip path. |

---

## 4. Hash-pin + coordinated-cut discipline

The SHA-256 of this document's canonical bytes is **the vocabulary hash**. Every ratifying repo pins it at build time:

```rust
pub const WIRE_VOCABULARY_HASH: [u8; 32] = hex!("…");
```

CIRISConformance runs the cohabitation gauntlet against the pinned hash; a mismatch at cohabitation is a **substrate-tier build failure, not a warning**.

**Working-implementation-before-ratification (the Matrix discipline).** Following Matrix's spec-process rule that a proposal lands only behind a *working implementation across the reference peers*, a vocabulary amendment does not ratify on prose alone. A Tier-1 addition must have a working `MessageType` variant + body struct + canonicalization exercised end-to-end through the conformance gauntlet before the covenant votes the hash.

**Unanimity blocks the CUT, not the DECISION.** The covenant may *decide* an amendment is right by ordinary quorum (§4.5.1). But the *coordinated cut* — the moment every repo flips to the new `WIRE_VOCABULARY_HASH` — requires **unanimous hash-commit** across the ratifying repos. A single repo's inability to satisfy the amendment does not veto the decision; it blocks the cut and is read as a signal that the amendment is **not yet coherent with the substrate**. The decision waits for the implementation, never the other way around. Old hashes are rejected at cohabitation only after a documented deprecation window.

---

## 5. The covenant of ratifying repos

A ratification requires **unanimous hash-commit** from:

- CIRISVerify
- CIRISPersist
- CIRISEdge
- CIRISAgent
- CIRISLensCore
- CIRISServer
- CIRISNodeCore
- CIRISRegistry (artifact steward)
- CIRISConformance (gauntlet enforcer)

Each ratifying repo, once the hash is pinned, files its own tracking issue for the v8.0.0 co-bump. No repo ships against an unratified vocabulary.

---

*This is a registry artifact — a technical contract. The ethical framing lives in CC; the load-bearing bytes live here.*