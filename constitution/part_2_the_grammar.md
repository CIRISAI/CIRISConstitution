# Part 2 — The Grammar

**Decimal range** `2.x` · **42 sections** · **page budget 17pp** · [← master index](README.md)

> The minimal-and-adequate wire grammar: the envelope, the five primitives, conformance, and canonicalization.

---

## 2.1 `envelope` — The envelope

The envelope is where a claim becomes accountable. Every `scores` Attestation carries it, and every field below either binds the claim to evidence, names who may revoke it, or records the conditions under which it was made — the integrity guarantees that let a consumer trust a stranger's signed word. Field semantics are consolidated here once; the rest of the Part references back to this table.

| Field | Required | Description |
|---|:---:|---|
| `attesting_key_id` | (substrate field) | Attester's `federation_keys.key_id`. |
| `attested_key_id` | (substrate field) | Subject's `federation_keys.key_id`. |
| `dimension` | yes | The canonical namespace prefix + scoped leaf. Persist treats this as TEXT; consumers parse against [CC 3.1](#3.1)'s namespace map. |
| `score` | yes | Pos/neg scalar in [-1, +1]. Polarity is encoded by sign; magnitude carries strength. Some dimensions are boolean-via-score (±1 only); some are positive-only; some are signed; per-dimension table in [CC 3.1](#3.1) names the polarity. |
| `confidence` | yes | The attester's own confidence in their score. [0, 1]. Low confidence + high magnitude = "I believe this strongly but I might be wrong"; high confidence + low magnitude = "I am sure the truth is near-neutral." |
| `context` | no | Free-form scoping detail. Not parsed by the substrate; used by consumers + audit + RATCHET. |
| `evidence_refs` | no (often required by per-dimension policy) | List of URIs / content-hashes pointing to backing evidence (Stripe receipt, licensing-body record, observed interaction, log entry, audit-chain leaf, etc.). Some dimensions in [CC 3.1](#3.1) require non-empty evidence_refs. |
| `valid_until` | no | ISO 8601 datetime per [CC 2.6.2](#2.6.2). If set, consumer policy treats the attestation as stale after that point (independent of the substrate row's own `expires_at`). |
| `epistemic_mode` | no | Per [CC 2.5](#2.5) Epistemic-mode axis; default `direct`. Consumers may weight by mode (e.g., direct witness > hearsay). |
| `witness_relation` | no | `self` \| `external` \| `derived`. Names the attester's relation to the attested fact: `self` = attester is the attested entity (self-attestation); `external` = attester observed independently; `derived` = attester inferred from other attestations or signed traces. Default `external`. Consumers weight by relation to prevent self-attestation gaming. Complements `epistemic_mode` (which names HOW the claim was formed) — `witness_relation` names WHO the attester is in relation to the attested entity. |
| `oversight_mode` | no | `HITL` \| `HOTL` \| `HOOTL`. Names the human-control gradient under which the attestation was produced. Default `null` (legacy contributions; consumer policy applies a per-cell default). Mode shifts are themselves attestable as `accountability:mode_shift:{from}:{to}` Contributions. |
| `occurrence_id` | no | Identifies which occurrence of a multi-occurrence agent deployment emitted this attestation. Format: `"occurrence-{n}"` per the agent's `AGENT_OCCURRENCE_ID` env var, or `"__shared__"` for shared-task pattern emissions. Default `null` → treated as `occurrence-0` for backward compat. **Self-asserted**: this field is NOT cryptographically bound to a fleet-attestation primitive in 0.x; an adversary running a single key can claim any occurrence_id. Acknowledged design tradeoff per [CC 8.3.1](#8.3.1). |
| `occurrence_count` | no | Total occurrences in the deployment fleet emitting the attestation; integer ≥ 1. Default `null` → `1` (single-occurrence). Same self-assertion caveat as `occurrence_id`. |
| `occurrence_role` | no | `primary` \| `shared` \| `replica`. Names the occurrence's role within the fleet. Default `null` → `primary` for backward compat. Substrate-self-report attestations SHOULD carry occurrence_id + occurrence_count + occurrence_role so post-facto compliance reviewers can reconstruct "which occurrence agreed to which mandate." |
| `stake` | no | Per [CC 2.5](#2.5) Stake axis; default `reputational`. Composes with the attester's actual stake-backed-by attestations from [CC 3.1.1](#3.1.1). |
| `community_id` | no (REQUIRED iff `cohort_scope == community`) | The `community_key_id` of the community this Contribution is scoped to, per [CC 3.2](#3.2) `community` subject_kind. One identity MAY belong to multiple communities; the field disambiguates which community's roster gates visibility. Required iff `cohort_scope == community` (substrate rejects community-scoped Contributions missing the field). Parallel to `family_id` but with different semantics: community content emits `holds_bytes:sha256:*` pointing to **ciphertext + cleartext provenance** — encrypted at rest under the per-community DEK. Byte-level structural-invisibility (no `holds_bytes` at all, [CC 5.2](#5.2)) remains self/family only. |
| `family_id` | no (REQUIRED iff `cohort_scope == family`) | The `family_key_id` of the family this Contribution is scoped to, per [CC 3.3.4](#3.3.4) `family` subject_kind. One identity MAY belong to multiple families ([CC 4.4.3.4](#4.4.3.4) Policy L); the field disambiguates which family's DEK applies and which membership roster gates visibility. Required iff `cohort_scope == family` (substrate rejects family-scoped Contributions missing the field). Composes with [CC 5.2](#5.2) structural-invisibility — `cohort_scope: self \| family` content never emits `holds_bytes:sha256:*`, so the field is only consulted in-substrate, never on the wire to non-members. |
| `subject_key_ids` | no | List of consent-holder `key_id`s for this Contribution. Each entry MAY be a `federation_keys.key_id` OR a canonical-hash identifier. Each listed key has substrate-recognized authority to (a) issue `withdraws` against this Contribution and (b) emit `consent:*` dimensions about this Contribution. Default `null`/empty = no subject authority (status quo; producer-only authority). Orthogonal to `cohort_scope` AND `delivery_mode` — see [CC 2.3.3](#2.3.3). |
| `delivery_mode` | no | `pull \| push`. Default `pull`. `pull` = subscribers discover via the `holds_bytes:sha256:*` directory ([CC 3.1.9.1](#3.1.9.1)) + fetch via [CC 5.3.2](#5.3.2) `ContentFetch`. `push` = substrate fans out to the live-delivery set per [CC 5.3.3.4](#5.3.3.4) `fan_out = entitled ∩ reachable`. Composes with [CC 4.4.3.2](#4.4.3.2) Policy M for community-scoped delivery; with [CC 5.3.3](#5.3.3) streaming for `live_stream` chunk-DAG delivery. Distinct from `cohort_scope` (visibility) and `subject_key_ids` (revocability) — see [CC 2.3.3](#2.3.3). RC1: pull-only multicast; push tree → 1.x per / #43. |
| `listed` | no | Per-membership opt-in flag — value `public`. Default absent (roster is producer- + self-queryable, NEVER globally enumerable). Public listing mirrors the [CC 4.5.9.1](#4.5.9.1) location opt-in discipline: opting into roster visibility is a one-way disclosure the member chooses; substrate does NOT solicit. Composes with [CC 4.4.3.2](#4.4.3.2) Policy M community membership and the new [CC 5.3.3](#5.3.3) streaming endpoint set. |
| `history_on_join` | no | `full \| from_join`. Default `from_join`. Per-target — names what content a new community/stream member receives at admission. `full` = Option-A retroactive catch-up (trace / registry-export backlog) per [CC 4.5.12.1](#4.5.12.1); `from_join` = current epoch forward only (live media). For `full` on streams: catch-up is bounded by `min(operator depth cap, chunk-eviction horizon)` per [CC 5.1](#5.1) P4; an evicted-epoch grant returns `ContentMiss` — fail-honest, no silent gap. |

**`epistemic_mode` vs `witness_relation` — distinct dimensions**: these co-vary at edges but name different concerns. `epistemic_mode` names the *process* by which the claim was formed; `witness_relation` names the *relational position* of the attester to the attested. F-3 detector attestations carry both (`epistemic_mode: derivative` + `witness_relation: derived`). Most encyclical-sourced translations are `witness_relation: external` + `epistemic_mode: hearsay`. When in doubt, set both.

### 2.1.1 `forward-compatibility` — Forward-compatibility rule

The envelope is meant to grow without breaking the peers already speaking it. Two rules make that safe: the canonical-bytes contract (so a new field never silently changes what an old signature covers) and an unknown-field discipline (so a consumer never rejects an envelope merely for carrying a field it has not learned yet).

> **Canonical-bytes contract**: the canonical-bytes encoding of this envelope for signing follows [CC 2.6.1](#2.6.1) (JCS over the envelope object; defaults are interpretation-time, NOT encoding-time; relay MUST preserve member presence/absence exactly as the producer signed). Optional fields with documented defaults in the table above ride the CC 2.6.1.1 omit-vs-materialize rule. Conditional-required fields are NOT optional-with-default and substrate rejects mis-shape per [CC 2.3.1](#2.3.1) + [CC 4.5.2.1](#4.5.2.1) + [CC 4.5.12.2](#4.5.12.2).

A Conforming Consumer that receives an envelope carrying a field-name it does not recognize MUST:

- Preserve the unknown field on read (do not strip).
- Preserve it on re-emission if the Consumer is also acting as a Producer relaying the attestation.
- NOT use it in verdict composition.
- NOT reject the envelope on the basis of the unknown field alone.

Producers introducing a new envelope field MUST follow the [CC 2.6.4](#2.6.4) versioning rules: a new field with a documented default is a MINOR bump; a field whose absence breaks consumer semantics is a MAJOR bump.

## 2.2 `conformance` — Conformance levels

Interoperability needs named roles so that "conforming" means the same thing to every peer. A **Producer** is any peer that emits Contributions onto the federation wire. A **Consumer** is any peer that reads and composes verdicts over received Contributions. A **Substrate Implementation** is the storage + transport + crypto layer (CIRISPersist + CIRISEdge + CIRISVerify) underneath both.

Three normative conformance profiles set the floor each role must meet:

1. **CEG-Conforming Producer (CCP)** — emits well-formed envelopes per [CC 2.1](#2.1), signs per CC 2.6.5 References [hybrid-sig], respects reserved-prefix rules per [CC 3.4](#3.4), declares its `oversight_mode` and `witness_relation` per [CC 2.1](#2.1).
2. **CEG-Conforming Consumer (CCC)** — verifies hybrid signatures, enforces reserved-prefix rules at admission, implements at least Policy A ([CC 4.4.3.8](#4.4.3.8)) with the default aggregation rules from [CC 4.4.2](#4.4.2), MUST honor `null` placeholder/dev hardware-class rejection per [CC 4.2.2](#4.2.2).
3. **CEG-Conforming Substrate (CCS)** — implements the storage + transport guarantees referenced in [CC 5.3.2](#5.3.2) + [CC 5.3.1](#5.3.1), including idempotent replication, full-SHA blob verification before consumption ([CC 5.3.2](#5.3.2)), and witness-quorum multi-party admission per [CC 5.3.1](#5.3.1).

Sections that follow MAY add per-feature conformance subsections; the three profiles above are the minimums.

## 2.3 `subject_keys` — `subject_key_ids` semantics

Consent is incomplete if only the producer of data has authority over it. The baseline envelope encoded **producer authority** alone (`attesting_key_id`); `subject_key_ids` adds the missing half — **subject authority** — for content where the subject of the data is not the producer of the data. This is the wire-format expression of the Autonomy and Non-maleficence principles: a person who appears in someone else's data can still pull it.

### 2.3.1 `subject_kind-subject-2` — Subject-bearing dimensions (governance requirement)

Per [CC 4.5.2](#4.5.2), dimensions whose namespace pattern names a subject (e.g., `observed:user:{key_id}:*`, `epistemic:about:{key_id}:*`, `consent:partnered:{user_key}`, `agent_files:*:{subject_target}`) MUST carry `subject_key_ids` containing that subject. The substrate MAY reject admission of subject-naming dimensions that omit `subject_key_ids`. This closes the default-leak failure mode where subject-bearing content publishes without wire-level subject authority.

### 2.3.2 `federation-key` — Federation-key vs canonical-hash identifier

A subject is not always a federation-enrolled identity. The two forms below let `subject_key_ids` name either an enrolled key that can sign for itself or an external party that cannot — without losing the external party's revocation rights.

`subject_key_ids[i]` MAY be either:

1. **A `federation_keys.key_id`** — the subject is a federation-enrolled identity that can sign on its own behalf. Direct revocation: subject signs a `withdraws` against this Contribution; substrate admits via rule (2) of [CC 2.4.1 broadened `withdraws` admission](#2.4.1). Wire form: the bare `key_id` (no tag).
2. **A tagged canonical-hash identifier** — the subject is an external party with no federation_keys row (Discord user-id, channel-id, content-sha256-bound entity, etc.). The substrate cannot verify a signature from this entity directly; **revocation rides a `delegates_to` proxy chain** per rule (3) of [CC 2.4.1 broadened admission](#2.4.1). Wire form: a tagged string per CC 2.3.2.1 below.

This answers the open question of how to attest about un-enrolled parties — canonical-hash or pseudonymous federation_keys — with "both, distinguished by an explicit tag on the canonical-hash variant."

#### 2.3.2.1 `registry-canonical` — Canonical-hash wire form + preimage convention

A CEG-Conforming implementation cannot interoperate without pinning two things: (a) how a canonical-hash entry is distinguished from a `federation_keys.key_id` entry on the wire, and (b) what string is hashed (the preimage). Both are normative.

**Wire form — tag REQUIRED**. A canonical-hash entry MUST carry the tag `canonical:{hashalg}:{hex}`:

- `{hashalg}` — the hash algorithm; `sha256` is the v1 algorithm. Algorithm-agility: future hashes (e.g. `sha3-256`) extend this position without ambiguity
- `{hex}` — the digest in [CC 2.6.3](#2.6.3) canonical hex (lowercase, unpadded, byte-length-exact: 64 chars for sha256)
- Example: `canonical:sha256:ff7c5632dae6ef3ae7f6283bd35268bc7910332414aa8a1c35a1645ca0295f61`

**Why the tag is mandatory and bare-hex is rejected**: a `federation_keys.key_id` is, in the reference Registry, `hex(sha256(ed25519_pubkey))` — a **lowercase 64-char hex string** ([`crypto::HybridCrypto::fingerprint`](../../rust-registry/ciris-registry-core/src/crypto/mod.rs)). A bare canonical-hash (also lowercase 64-char hex) would be **format-indistinguishable** from a key_id. A "base64 key_id vs hex canonical-hash" disambiguation heuristic FAILS because Registry key_ids are themselves hex fingerprints, not base64 pubkeys. The tag is therefore load-bearing, not cosmetic. The CC 2.6.3 hex rule governs the `{hex}` segment only; the `canonical:{hashalg}:` prefix is a tagged-union discriminator outside CC 2.6.3's scope and is exempt from the "no separators" rule.

**Preimage convention — `{platform}:{entity_kind}:{id}`**. The string hashed to produce `{hex}` MUST be:

```
preimage = "{platform}:{entity_kind}:{id}"
hex = sha256_hex_lowercase(utf8_bytes(preimage))
```

Parsing is **split-on-first-two-colons**: the substring before the first `:` is `{platform}`; the substring between the first and second `:` is `{entity_kind}`; **everything after the second `:` is `{id}` verbatim, and MAY itself contain colons** (so Matrix IDs like `@alice:example.org` survive). Rules:

- `{platform}` — lowercased; open vocabulary per [CC 4.5.1.1](#4.5.1.1). Canonical seeds: `discord`, `slack`, `twitter`, `matrix`, `email`, `phone`, `github`, `xmpp`, `irc`
- `{entity_kind}` — lowercased; open vocabulary. Canonical seeds: `user`, `channel`, `guild`, `room`, `group`, `address`
- `{id}` — the platform's **stable, immutable** identifier, **verbatim** (case-preserved — some IDs are case-sensitive). MUST be the immutable account/object identifier (Discord/Twitter numeric snowflake; Matrix MXID; UUID), **NOT** a mutable handle/username/display-name. Using a mutable handle breaks subject-identity stability the moment the user renames.

The split-on-first-two-colons rule means a producer constructs the preimage by joining exactly three parts with `:`; only the first two colons are structural. This is what makes the rule-(3) `delegates_to` proxy chain (`canonical_hash ∈ T.subject_key_ids`) match across producers: every CEG-Conforming producer that names the same `(platform, entity_kind, immutable_id)` triple computes the same `{hex}`, hence the same tagged wire string.

**Conformance vectors**:

| Preimage | sha256 hex | Wire form |
|---|---|---|
| `discord:user:123456789012345678` | `ff7c5632dae6ef3ae7f6283bd35268bc7910332414aa8a1c35a1645ca0295f61` | `canonical:sha256:ff7c5632…0295f61` |
| `discord:channel:987654321098765432` | `af23411c3c6faa55a788660ea29719669b9c4e4ea4b6ab9568247d9f646f05dd` | `canonical:sha256:af23411c…646f05dd` |
| `matrix:user:@alice:example.org` (id contains colons) | `16d4d0bf478835a9af68cdaac730a29b36f82bf0dfe2073237ee4980f6b975d9` | `canonical:sha256:16d4d0bf…f6b975d9` |
| `twitter:user:1455079377986420736` (numeric id, NOT @handle) | `10243ba010bf159a45197d368f91c025ef6ac1eb7f42ca32e55b414d90c861c2` | `canonical:sha256:10243ba0…90c861c2` |
| `email:address:alice@example.org` | `04481a02fccfc8d99a47bde4f0563dd360d425b0734e8fcd8d5dd7198d0a263f` | `canonical:sha256:04481a02…98d0a263f` |

#### 2.3.2.2 `canonical_binding` — Rule-(3) proxy vs `canonical_binding` — distinct mechanisms

These are **two distinct mechanisms**, not one:

- **Rule-(3) `delegates_to` proxy** ([CC 2.4.1.1](#2.4.1.1) admission rule 3) — *ongoing* revocation authority for an un-enrolled subject. A federation-enrolled key (typically the agent holding data on behalf of the external party) carries `delegates_to(canonical_hash → agent_key, scope: [consent_revocation])`; the agent proxies revocation. The subject never enrolls; the agent acts for them indefinitely.
- **`canonical_binding`** — *retroactive identity claim*. A now-enrolled federation key asserts "I AM the entity behind `canonical:sha256:{hex}`", binding past canonical-hash subject entries to its real identity. After an admitted `canonical_binding`, the formerly-un-enrolled subject can sign `withdraws` **directly** under rule (2) — the binding promotes the canonical-hash to a real key_id for admission purposes.

`canonical_binding` is **NOT a new admission rule** (no "rule 5"). It composes: the binding is itself a `delegates_to`-shaped attestation (`delegates_to(canonical_hash → newly_enrolled_key, scope: [identity_binding])`) admitted because the enrolling key proves control of the preimage out-of-band. Once bound, rule (2) [direct subject revocation] becomes available to the bound key, and rule (3) [proxy] is no longer needed for that subject.

#### 2.3.2.3 `subject_kind-payload` — `subject_kind` is a payload-level discriminator

`subject_kind` (e.g. `consent_record`, `consent_replication` ([CC 3.3.7](#3.3.7)), `key_grant`, `takedown_notice`, `community`, `family`, `identity_occurrence`, `location_proof`) is a **payload-level** field — it lives inside the Contribution payload, parallel to how `external_content` carries `sub_kind` in payload. It is NOT an envelope-level field. The envelope-level fields are exactly those in the [CC 2.1](#2.1) table (`cohort_scope`, `subject_key_ids`, `community_id`, `family_id`, `delivery_mode`, etc.); `subject_kind` is the payload discriminator that selects which [CC 3.3](#3.3) payload schema applies. The CC 3.3.5 `consent_record` example and any conformant producer payload agree byte-for-byte: `"subject_kind": "consent_record"` is a payload member.

#### 2.3.2.4 `bilateral` — Bilateral ratification is consumer-policy

Per [CC 3.3.5](#3.3.5) step 4: a bilateral partnership is "ratified iff both halves present under the same `bilateral_pair_id` with `stance: granted`" — and this predicate is **consumer policy**, NOT registry-normative. CIRISAgent's CEM `PartnershipRequestHandler` is the canonical consumer that enforces it. Ingest-layer builders (NodeCore's `build_bilateral_pair_id` + request/accept builders) correctly produce the two halves WITHOUT enforcing ratification — that is the right boundary. The substrate admits each half independently; composition of the pair into a ratified partnership is a downstream read-time computation, never an admission gate.

### 2.3.3 `cohort-orthogonality` — Orthogonality with `cohort_scope` AND `delivery_mode` (3-axis)

The envelope keeps visibility, revocability, and delivery as three independent concerns so they can be reasoned about — and enforced — separately. They compose without overlap:

| Axis | Field | Authority | Names |
|---|---|---|---|
| **Visibility** | `cohort_scope` + (`family_id` or `community_id` when set) | Producer-side | Who can SEE the data |
| **Revocability** | `subject_key_ids` | Subject-side | Who can REVOKE the data |
| **Delivery** | `delivery_mode` + `listed` + `history_on_join` | Substrate / subscriber | Who actively RECEIVES the data + how the substrate fans out |

All three may coexist on the same Contribution:

```
A `cohort_scope: family` contribution
 carrying `subject_key_ids: [user_canonical_hash]`
 carrying `delivery_mode: push` + `history_on_join: from_join`
 carrying `family_id: <acme_household>`

publishes the bytes at family-cohort visibility (cohort_scope);
the user retains revocation authority (subject_key_ids);
the substrate actively fans out to currently-reachable members
 with new-members getting forward-only content (delivery_mode + history_on_join);
the named family roster gates the membership set (family_id).
```

This orthogonality is load-bearing for the multi-occurrence consent shape: subject-side revocation applies federation-wide regardless of producer's `occurrence_id`; per-occurrence lifecycle consent is a producer-side concern, separately tracked.

The delivery axis is the **third orthogonal axis**: visibility + revocability alone left the substrate with no envelope-level handle on who actively *receives* content and how the substrate fans out. Per [CC 5.3.3](#5.3.3), three optional envelope fields + the CC 5.3.3 endpoint section + a delivery extension to [CC 4.4.3.2](#4.4.3.2) Policy M close that gap.

### 2.3.4 `self-as-subject` — Self-as-subject ceremony

When `attesting_key_id ∈ subject_key_ids`, the Contribution is a **self-consent ceremony** — the same identity is attesting AS subject AND producer. This composes naturally with the CEG-native agent's self-attestation pattern: agent attests `identity:current` about itself with `subject_key_ids = [self.key_id]`, asserting consent-authority over its own identity claims (D08 autonomy claim).

### 2.3.5 `shape` — The shape

`subject_key_ids` is an OPTIONAL list. When present, each entry names a party with substrate-recognized authority over this Contribution's continued processing. The basic shape:

> A consent record is a signed declaration by a subject about the substrate's continued processing of content where that subject appears.

The medical record, photo, interview, training-datum, and group-chat cases all share the same shape — a producer publishes a Contribution; one or more subjects appear in it; the subjects retain revocation authority. A single shape carries thirteen distinct content cases uniformly.

### 2.3.6 `absent` — Empty/absent = status-quo

`subject_key_ids: null` or `[]` is the status-quo shape (producer-only authority; same as a baseline Contribution carrying no subject authority). Consumers that don't read the field see status-quo behavior. Subject authority is additive at the envelope layer — adding it never changes how an existing consumer reads an envelope that omits it.

## 2.4 `primitive` — The primitive set — 1+4

The whole grammar reduces to five wire primitives: one workhorse that makes claims, and four structural composers that operate on the claim graph itself. Minimal-and-adequate is the design discipline — fewer primitives mean a smaller surface to attack, audit, and prove conformant, which is what Integrity asks of the wire.

### 2.4.1 `structure` — The four structural composers

The four structural composers act on the attestation graph itself, not as score-claims on entities. They are how an attester delegates authority, replaces a row, retracts a row, or admits a row was false:

| `attestation_type` | What it does | Envelope shape |
|---|---|---|
| `delegates_to` | A authorizes B to sign on A's behalf within a bounded scope | `{delegated_scope[], delegation_purpose, delegation_valid_from, delegation_valid_until}` |
| `supersedes` | This attestation row replaces a prior one by the same attester | `{references_attestation_id, supersession_reason, differs_in[]}` |
| `withdraws` | I retract my prior attestation (does NOT claim it was false) | `{references_attestation_id, withdrawal_reason}` |
| `recants` | My prior attestation was false at issuance — admits epistemic error | `{references_attestation_id, recantation_reason, what_was_false}` |

**Translation implications**:

- A **doctrinal-development** claim ("this version extends but does not contradict the prior version") is `supersedes` with `differs_in: ["scope", "evidence_refs"]` — NOT `recants` (which would assert prior was false).
- An **acknowledged-error** claim ("the prior framing was wrong; I admit the mistake") is `recants` — distinct from `withdraws` (which retracts without making a falsity claim).
- A **prudent-retraction** ("I'm withdrawing without claiming it was false; context has changed") is `withdraws`.
- An **authority-source claim via delegation** ("this constitutional position derives from authority-key X in scope Y") is `delegates_to` with X as `attested_key_id` (the [CC 2.4.1.2](#2.4.1.2) reuse pattern for authority-source claims, replacing what would otherwise need a `grounding:{tradition}:{principle}` prefix that fails [CC 1.2](#1.2) T2).

#### 2.4.1.1 `withdraws` — `withdraws` admission rule (semantic, not structural)

Revocation has to reach beyond the original producer without inventing new structure. The `withdraws` admission rule broadens *who* the substrate accepts a retraction from — federation-enrolled subjects, proxies for un-enrolled subjects, and delegates — while keeping the primitive itself unchanged.

Substrate MUST admit a `withdraws` Contribution against target `T` when the issuer's `key_id` satisfies **ANY** of:

| # | Authority path | Description |
|---|---|---|
| 1 | `issuer.key_id == T.attesting_key_id` | Producer self-withdraw (today's shape; unchanged) |
| 2 | `issuer.key_id ∈ T.subject_key_ids` | Federation-keys subject revocation |
| 3 | ∃ `delegates_to` chain: `issuer →* canonical_hash` where `canonical_hash ∈ T.subject_key_ids` AND `scope ⊇ {consent_revocation}` | Proxy authority for non-federation-enrolled subjects |
| 4 | `issuer` holds valid `delegates_to → any of 1-3` | Delegated revocation (existing primitive, new admission path) |

**Rule (3) is the elegant answer to the un-enrolled-party case.** When a subject is a Discord user-id, a content-sha256-bound entity, or any other non-federation party, revocation authority is mediated through a `delegates_to` chain from a federation-keys signer (typically the agent that holds data on behalf of the external party) to the canonical-hash subject. The agent emits `delegates_to(canonical_hash → agent_key, scope: [consent_revocation])` at proxy-establishment time; subsequent `withdraws` from the agent against any Contribution carrying `canonical_hash` in its `subject_key_ids` is admitted under rule (3). The `canonical_hash` here is the tagged `canonical:{hashalg}:{hex}` wire form with the `{platform}:{entity_kind}:{id}` preimage convention pinned at [CC 2.3.2.1](#2.3.2.1). **Rule (3) proxy is distinct from `canonical_binding`** (a retroactive identity claim that promotes a canonical-hash to a real key_id, enabling rule (2) direct revocation) — see [CC 2.3.2.2](#2.3.2.2) for the distinction; `canonical_binding` is not a new admission rule.

**Per-rule audit metadata**: substrate SHOULD record which admission rule (1-4) admitted each `withdraws` Contribution in `federation_attestations` metadata so downstream consumers can compose policy (e.g., higher confidence weight for subject self-revocation rule 2 than for proxy rule 3).

**Composition with `recants`**: subject-side authority does NOT extend to `recants` (the falsity-admission primitive) — only the original attester can `recant` their own claim. A subject who believes the producer's claim about them is FACTUALLY wrong (not merely unwanted) issues `scores` with negative polarity on a contradicting dimension; that is the consumer-side rebuttal path, distinct from consent revocation. The `recants` / `withdraws` distinction matters precisely because subject authority covers the consent dimension (revocability) but not the truth dimension (falsity).

#### 2.4.1.2 `delegates_to` — Authority-source claims via `delegates_to`

A constitutional or framework claim can name its source-of-authority by emitting `delegates_to` against an `attested_key_id` representing the framework, with `delegated_scope` naming the principle. Example: a Ubuntu-substrate commitment in [CC 1.13.1](#1.13.1) commitment 2 can be expressed as `delegates_to` against the `ubuntu_relational_substrate` framework-key with `delegated_scope: ["personhood_constitutive_by_attestation"]`. Reuses the existing structural primitive rather than introducing a `grounding:{tradition}:{principle}` prefix (which would fail [CC 1.2](#1.2) T2 — "tradition" claims are interpretive, not mechanism-descriptive).

#### 2.4.1.3 `recants` — The `recants` distinction matters

Per `PRIOR_ART_SCAN.md` Bucket 1: no prior identity system (PGP, SPKI/SDSI, W3C VC) typed epistemic-error-admission as a wire primitive distinct from retraction. CEG types both because the Recursive Golden Rule applies to attesters: admitting error is a primary act, not a derivative of retraction. Consumer policy can apply different trust adjustments to attesters who `recant` versus those who `withdraw`.

### 2.4.2 `scores` — The workhorse: `scores`

The federation has exactly **one** workhorse attestation primitive. Every claim about an entity — positive or negative, identity or capability or behavior or state or commitment, by any attester source — is expressed as a `scores` attestation on a named dimension.

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
 "oversight_mode": "<HITL | HOTL | HOOTL | null>", // optional; default null
 "occurrence_id": "<occurrence-N | __shared__ | null>", // optional; default null
 "occurrence_count": <int ≥ 1 | null>, // optional; default null
 "occurrence_role": "<primary | shared | replica | null>", // optional; default null
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

`biosphere` is a distinct Scope value from `species` (which is the Homo sapiens cohort). See [CC 4.1](#4.1) for the `planet` colloquial alias note.

## 2.6 `foreword` — Foreword

CEG — the CIRIS Epistemic Grammar — is the federation's language for making **structured, signed, machine-checkable claims about reality and each other**. It is the wire format the federation's peers speak. Everything above is that grammar; everything below is the canonicalization discipline that makes one peer's bytes verify identically on another peer's machine — the mechanical foundation of the Integrity principle.

The grammar has exactly five wire-format primitives (one workhorse + four structural composers) and an open-vocabulary dimension namespace organized by mechanism-descriptive prefixes. Consumers compose verdicts from primitive attestations using the policies in [CC 4.4](#4.4); nothing in the wire format prescribes what verdict to reach.

CEG is **substrate-consuming**: it sits above the federation substrate (CIRISPersist for storage, CIRISVerify for crypto, CIRISEdge for transport) and below the application tier (CIRISAgent). It does not author primitives in the substrate it consumes; it composes policy over them. It is also **substrate-supplying** for the second-tier consensus crates (CIRISNodeCore for consensus, CIRISLensCore for detection) — they own slices of the dimension namespace and emit attestations that other CEG consumers read.

This specification has **two readerships**:
- **Implementers** of federation primitives consuming or emitting CEG attestations: read CC 1.13-CC 4.5 normative.
- **Translators** mapping substantive content into CEG envelopes: read CC 8.2-CC 8.1 + the [`LANGUAGE_PRIMER.md`](../LANGUAGE_PRIMER.md) companion.

Both readerships should read [CC 1.13](#1.13) first.

### 2.6.1 `envelope-canonicalization` — Envelope canonicalization — JCS + the omit-vs-materialize rule

This rule closes the canonical-bytes ambiguity that arises whenever an envelope carries optional fields with documented defaults — `epistemic_mode`/`witness_relation`/`occurrence_*`/`stake`, `oversight_mode`, `subject_key_ids`, `family_id`, `community_id`. Without it, two honest peers can disagree on the bytes and a valid signature fails to verify.

**The hazard is structural.** If Producer A omits an optional field (relying on the [CC 2.1](#2.1) documented default) and Relay R re-serializes the attestation with the default materialized into the byte stream, the canonical bytes diverge and the Ed25519 + ML-DSA-65 signatures no longer verify. The rule below makes the discipline explicit and normative: every party — producer, substrate, relay, consumer — must make the same choice, and that choice is "preserve what the producer signed, exactly."

#### 2.6.1.1 `round-trip` — The round-trip rule — defaults are interpretation-time, not encoding-time (normative)

The canonical bytes are computed over **the literal envelope members the producer signs**. Optional fields that the producer omits MUST NOT be materialized into canonical bytes by any party — producer, substrate, relay, or consumer. Optional fields that the producer explicitly emits (even at their default value) MUST be preserved in the canonical bytes by any party. Documented defaults from [CC 2.1](#2.1) are **interpretation-time semantics**, not encoding-time content.

**Two valid encodings of the semantically-identical attestation**:

```
# Producer A — omits epistemic_mode (relies on §4 default)
{"attested_key_id":"...","attesting_key_id":"...","confidence":0.9,"dimension":"licensure:CA_medical_board","score":0.8}

# Producer B — explicitly emits epistemic_mode at its default value
{"attested_key_id":"...","attesting_key_id":"...","confidence":0.9,"dimension":"licensure:CA_medical_board","epistemic_mode":"direct","score":0.8}
```

Both producers compute different canonical bytes (Producer B's includes the `"epistemic_mode":"direct"` member) and emit different signatures. **Both signatures verify under their respective canonical bytes.** Both are **semantically equivalent** — a CEG-Conforming Consumer evaluates `effective_epistemic_mode(envelope) = envelope.epistemic_mode if present else "direct"` and proceeds identically. The wire-format admits both encodings; the consumer policy admits no observable difference.

**Relay discipline (normative)**. A substrate, relay, or consumer that re-stores or forwards an attestation MUST preserve member presence/absence exactly as the producer signed it:

- Stripping an explicitly-emitted default ("the producer wrote `epistemic_mode:direct` but I'll save bytes by removing it") MUST NOT happen
- Materializing an omitted default ("the producer omitted `epistemic_mode` so I'll fill in `direct` for clarity") MUST NOT happen
- Reordering object members on re-emission is REQUIRED (JCS lexicographic order; if a producer somehow emits non-canonical order, the relay re-canonicalizes — but member presence/absence stays fixed)

This composes with the [CC 2.1.1](#2.1.1) forward-compatibility rule (which already mandates preserving unknown fields on read and re-emission); the same preservation discipline extends to known-optional fields.

##### 2.6.1.1.1 `canonicalization-array` — Array ordering + byte-field + timestamp encoding (normative — the three determinism rules JCS does NOT pin)

JCS ([CC 2.6.1.3](#2.6.1.3)) canonicalizes **object member order** but is silent on three things that still let two conformant producers emit different bytes (and therefore non-verifying signatures, the same hazard). All three are pinned here once, globally, for every CEG envelope:

1. **Array element order.** An array field is one of two kinds, stated in its [CC 2.1](#2.1)/[CC 3.1](#3.1) definition:
 - **Set-semantics** (order carries no meaning) — elements MUST be **lexicographically sorted by their JCS string form (UTF-16 code-unit order, ascending)** before signing. This is producer-independent: any producer building the set in any order yields identical bytes. **`subject_key_ids[]` and `delegates_to.delegated_scope[]` are set-semantics → sorted.**
 - **Sequence-semantics** (order is meaningful) — elements retain their as-authored order. **`transport_destination.aspects[]`** (RNS hash preimage order), **`key_grant.rotation_chain`** (supersession lineage), and **`evidence_refs[]`** (producer-asserted order) are sequence-semantics → preserved. A field's definition MUST declare which kind it is; absent a declaration, set-semantics (sorted) is the default.
2. **Byte-field string encoding.** JSON has no byte type, so every byte/binary field is a string whose encoding MUST be pinned. **Key references, hashes, and identifiers — `key_id` / `attesting_key_id` / `attested_key_id` / `subject_key_ids[]` elements, public keys, `destination_hash`, `root_hash`, fingerprints — MUST be lowercase hex per [CC 2.6.3](#2.6.3)** (no `0x`, no separators, byte-length-exact; never base64 in canonical bytes). Fields explicitly documented as base64 (e.g., `hardware_attestation`, an opaque attestation blob) use base64 as their definition states — but the *default* for any key/hash/id byte field is CC 2.6.3 lowercase hex.
 - **The base64 variant is pinned: every field documented as base64 MUST use the RFC 4648 §4 STANDARD alphabet, WITH padding, no whitespace or embedded newlines** (the `base64::engine::general_purpose::STANDARD` shape `ciris-verify-core` ships). The pin lives at the **protocol layer**: the crypto layer (`ciris-crypto`) is correctly encoding-agnostic and deals in raw bytes; the wire encoding is CEG's to pin. A variant mismatch (URL-safe alphabet, stripped padding) produces different signed bytes and a **silently non-verifying signature** — the same hazard class as the wrap-algorithm wire-string. The vector set MUST include a base64-variant case (encode→sign→verify round-trip across two independent encoders).
3. **Timestamp encoding.** Every datetime field (`signed_at`, `asserted_at`, `valid_until`, `delegation_valid_from`/`_until`, `valid_at`, …) is the **[CC 2.6.2](#2.6.2) canonical string** — UTC literal `Z` (never `+00:00`), millisecond precision (exactly three fractional digits), `YYYY-MM-DDTHH:MM:SS.sssZ`. A producer emitting `+00:00` or a different sub-second precision produces different bytes and a non-verifying signature.

With key order (JCS) + omit-vs-materialize + these three, **byte-identity across conformant implementations is closed by construction**. The cross-impl JCS vector set MUST cover all three (a set-vs-sequence array case, a hex-vs-base64 byte case, a timestamp case) alongside the per-Contribution vectors.

#### 2.6.1.2 `per-field` — Per-field encoding table (informational)

The omit-vs-materialize rule applies uniformly to every optional [CC 2.1](#2.1) field. Catalog:

| Field | Introduced | Default per CC 2.1 | Canonical when omitted | Canonical when explicit |
|---|---|---|---|---|
| `epistemic_mode` | pre-0.4 | `direct` | member absent | `"epistemic_mode":"direct"` (or other enum value) |
| `witness_relation` | pre-0.4 | `external` | member absent | `"witness_relation":"self"` (or other enum value) |
| `oversight_mode` | pre-0.4 | `null` (per-cell default applies) | member absent | `"oversight_mode":"HITL"` (or other enum value) |
| `occurrence_id` | pre-0.4 | `null` → `"occurrence-0"` at interpretation | member absent | `"occurrence_id":"occurrence-1"` |
| `occurrence_count` | pre-0.4 | `null` → `1` at interpretation | member absent | `"occurrence_count":3` |
| `occurrence_role` | pre-0.4 | `null` → `"primary"` at interpretation | member absent | `"occurrence_role":"shared"` |
| `stake` | pre-0.4 | `reputational` | member absent | `"stake":"capital"` (or other enum value) |
| `context` | pre-0.4 | absent | member absent | `"context":"..."` (free-form) |
| `evidence_refs` | pre-0.4 | absent | member absent | `"evidence_refs":["..."]` |
| `valid_until` | pre-0.4 | absent | member absent | `"valid_until":"2026-12-31T00:00:00.000Z"` |
| `subject_key_ids` | CEG 0.6 | `null`/empty | member absent | `"subject_key_ids":["..."]` |
| `family_id` | CEG 0.7 | n/a (REQUIRED iff `cohort_scope == family`) | member absent (admission rejects if cohort_scope == family) | `"family_id":"..."` |
| `community_id` | CEG 0.8 | n/a (REQUIRED iff `cohort_scope == community`) | member absent (admission rejects if cohort_scope == community) | `"community_id":"..."` |
| `delivery_mode` | CEG 0.10 | `pull` | member absent | `"delivery_mode":"push"` |
| `listed` | CEG 0.10 | absent (private roster) | member absent | `"listed":"public"` (opt-in only; producers MUST omit unless the subject has opted in) |
| `history_on_join` | CEG 0.10 | `from_join` | member absent | `"history_on_join":"full"` |

The conditional-required fields `family_id` and `community_id` are NOT optional-with-default — substrate rejects mis-shape per [CC 2.3.1](#2.3.1) + [CC 4.5.2.1](#4.5.2.1) + [CC 4.5.12.2](#4.5.12.2) — but they encode under the same JCS rule when present.

#### 2.6.1.3 `canonical` — Canonical encoding format (normative)

CEG envelope signing bytes are computed via **JCS — JSON Canonicalization Scheme, [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785)** (Rundgren, Jordan, Erdtman; March 2020). JCS pins, in summary:

- Object members sorted lexicographically by member name (UTF-16 code-unit order, RFC 8785 §3.2.3)
- No insignificant whitespace
- UTF-8 byte encoding (RFC 8259 §8.1)
- Strings escaped per RFC 8259 §7 with the JCS narrowing on `\uXXXX` form
- Numbers serialized per the ES6-derived rule (RFC 8785 §3.2.2.3) — integers without trailing `.0`, no exponent unless the magnitude requires it

A CEG-Conforming Producer MUST produce signing bytes via JCS over the envelope object. A CEG-Conforming Consumer (CCC) MUST recompute signing bytes via the same JCS rule for signature verification. A CEG-Conforming Substrate (CCS) MUST preserve the as-received envelope object bytes for relay (per the round-trip rule above); it MAY store a parsed representation alongside, but the canonical-bytes contract is against the as-received form, not the parsed-and-re-serialized form.



**Number totality (normative).** RFC 8785 §3.2.2.3 fixes the number model as the IEEE-754 binary64 (ECMAScript `Number`) image. A CCP MUST coerce every numeric value to its finite IEEE-754 double image *before* computing JCS bytes, and MUST reject — with a hard error, never a fallback or best-effort hash — any number that has no finite double (overflow to ±Infinity, e.g. `1e1000` or a thousand-digit integer). An implementation built against an arbitrary-precision JSON parser otherwise admits a string-backed number that bypasses the double model: JCS then emits a non-canonical result and the content address silently diverges between peers — the same non-determinism-is-broken hazard class as the byte-field and timestamp rules of [CC 2.6.1.1.1](#2.6.1.1.1). With this rule a content address is always either the spec-canonical hash or an honest error, never a wrong-but-plausible one, in any parser feature configuration. The cross-impl JCS vector set MUST include a non-representable-number case (a value with no finite double, asserted to reject) under both default and arbitrary-precision parser builds.

#### 2.6.1.4 `worked` — Worked attack the rule closes

Without the rule (implicit / unspecified) failure mode:

> Alice's CEG-Conforming Producer signs an envelope omitting `epistemic_mode`. Bob's CEG-Conforming Relay receives, parses, materializes the default `"direct"`, re-serializes via JCS, and forwards to Carol. Carol receives the relay-modified envelope with the new bytes, computes JCS, verifies signature → **FAILS** because Alice signed over bytes without the `epistemic_mode` member. Carol cannot distinguish "Bob is a malicious relay corrupting the bytes" from "Bob is honestly applying defaults to be helpful." Carol rejects. The attestation is lost in transit despite no party acting in bad faith.

With the rule (explicit, normative):

> Bob's relay MUST preserve member presence/absence exactly. Bob forwards the as-received bytes. Carol's verify succeeds. The semantic interpretation step at Carol (applying default `"direct"` to the absent member) happens AFTER signature verification.

#### 2.6.1.5 `verification` — Verification flow (informational)

```
On signature verify:
    1. Receive envelope from wire as object O (preserved as-received)
       and signature S
    2. Compute canonical bytes B = JCS(O)
    3. Verify S over B via the hybrid Ed25519 + ML-DSA-65 path per §5.2.1
    4. If signature valid:
        a. Compute effective semantics by applying §4 defaults to absent
           optional fields (interpretation-time only)
        b. Apply consumer policy per §8 over the resulting semantic shape
    5. If forwarding/storing:
        a. Store/forward object O AS RECEIVED — do not normalize, strip,
           or materialize defaults
        b. Forward original signature S unchanged
```

#### 2.6.1.6 `section` — Scope of the canonicalization rule

Scope pointer: the JCS canonicalization rules above (JCS-as-encoding, omit-vs-materialize + relay-preservation, per-field catalog, worked attack).

What this rule does NOT do:
- Introduce a new encoding format — JCS is the only encoding
- Change any semantic interpretation — defaults still apply at interpretation time per [CC 2.1](#2.1)
- Modify the datetime / hex / time / H3 sub-rules — those are domain-specific and compose under JCS
- Wire-break prior emissions — emissions that omitted optional fields remain valid; emissions that explicitly emitted defaults likewise remain valid; what the rule normatively prohibits is RELAY-TIME mutation of presence/absence, which was always wrong but is now explicitly so

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

- **MAJOR (X.0.0)** — any wire-incompatible change: removal of an envelope field, change of a field's semantic, removal of a structural primitive, change to canonical-bytes domain-separation labels, removal or breaking-redefinition of a [CC 3.1](#3.1) prefix, change to a [CC 3.4](#3.4) reservation, or change to the CC 2.6.9 / CC 2.2 conformance language.
- **MINOR (0.X.0)** — wire-compatible additions: new prefix in [CC 3.1](#3.1), new envelope field with documented default, new composition policy in [CC 4.4](#4.4), new endpoint shape in [CC 5.3](#5.3), new optional conformance subsection. Existing Conforming Producers and Consumers continue to interoperate without modification.
- **PATCH (0.0.X)** — clarifications, editorial fixes, additions to non-normative sections ([WITNESS_KIND_REGISTRY](../WITNESS_KIND_REGISTRY.md), glossaries [CC 8.1](#8.1)), addition to [CC 8.3](#8.3) acknowledged-gaps, fixes to non-normative examples in [CC 8.1](#8.1).

The 0.x series indicates this specification is a Public Working Draft. Any 0.x → 0.(x+1) bump MAY include wire-breaking changes; consumers MUST treat 0.x as unstable until 1.0 publication. Once 1.0 is published, the rules above bind strictly.

A **deprecation** is announced by adding a `**DEPRECATED in 0.X**` marker to the affected element with a stated removal target (e.g., `removal: 1.2`). Deprecated elements MUST remain interoperable until the announced removal version. Removal in MAJOR or 0.MINOR per the rules above.

**The wire vocabulary is a hash-pinned artifact.** The set of message types the substrate recognizes — the *wire vocabulary* — is not the emergent product of individual repos' needs but a ratified contract, expressed as a versioned, hash-addressable artifact, [`manifests/WIRE_VOCABULARY.md`](../../manifests/WIRE_VOCABULARY.md), governed in **two tiers** (the RFC 8126 partitioned-registry discipline, the pattern proven by Nostr kind-ranges and Matrix reverse-DNS namespacing). **Tier 1** — message types whose canonicalization is load-bearing to an ethical primitive (attestations, votes, moderation/slashing, deferral, steward directives, key registration, the humanity-accord path, `withdraws`, goals, build provenance, content/blob fetch) — is closed and CC-ratified: a Tier-1 addition rides the ordinary [CC 4.5.1](part_4_composition_governance.md) amendment (the "Standards Action" bar), a working reference implementation, and a coordinated cut. **Tier 2** — app-tier remote-procedure channels whose inner semantics are the app's concern — uses three opaque envelopes (`OpaqueRequest` / `OpaqueResponse` / `OpaqueEvent`) carrying a `kind` from a reserved per-repo range delegated to the range steward (the "Private Use" bar); no CC amendment is required to define a `kind`. Every ratifying repo **pins the artifact's SHA-256 at build**; a hash mismatch at cohabitation is a substrate-tier build failure, not a warning. Amendment is a substrate-coordinated event across the covenant of ratifying repos; unanimous hash-commit blocks the *cut*, never the *decision* (the decision is the CC 4.5.1 amendment). This governs the **transport vocabulary** — a surface distinct from, and complementary to, the frozen [CC 1.7](part_1_foundation.md) 1+4 attestation grammar: 1+4 freezes what a claim *is*; the wire vocabulary governs the message types that *carry* claims.

### 2.6.5 `references` — Normative References

The following documents are normatively cited; implementations MUST conform to them where referenced inline.

| Short name | Normative document |
|---|---|
| [BCP 14] | [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) + [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) — keywords for use in RFCs |
| [FIPS-180-4] | [FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) — SHA-256 and the SHA-2 family |
| [FIPS-202] | [FIPS 202](https://csrc.nist.gov/pubs/fips/202/final) — SHA-3 / SHAKE128 / SHAKE256 / TupleHash |
| [FIPS-204] | [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final) — ML-DSA (Module-Lattice-Based Digital Signature Algorithm); CEG uses parameter set ML-DSA-65 |
| [RFC-3339] | [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) — Date and Time on the Internet, with fractional-seconds disambiguation in CC 2.6.2 below |
| [RFC-5905] | [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905) — Network Time Protocol Version 4 |
| [RFC-6962] | [RFC 6962](https://www.rfc-editor.org/rfc/rfc6962) — Certificate Transparency; this spec's transparency-log discipline tracks 6962 except where 6962-bis (RFC 9162) supersedes |
| [RFC-8032] | [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032) — Edwards-Curve Digital Signature Algorithm (EdDSA); specifically Ed25519 |
| [RFC-8174] | [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (with BCP 14) |
| [RFC-8785] | [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) — JSON Canonicalization Scheme (JCS); used where this spec serializes JSON for signing |
| [RFC-9162] | [RFC 9162](https://www.rfc-editor.org/rfc/rfc9162) — Certificate Transparency v2.0 (CT-bis); MUST be used for new transparency-log integrations; older 6962 instances continue to interoperate |
| [ISO-639-1] | [ISO 639-1:2002](https://www.iso.org/standard/22109.html) — Codes for the representation of names of languages, two-letter |
| [BCP-47] | [BCP 47](https://www.rfc-editor.org/info/bcp47) ([RFC 5646](https://www.rfc-editor.org/rfc/rfc5646)) — Tags for identifying languages; for locale strings richer than ISO 639-1 alone |
| [RFC-9420] | [RFC 9420](https://www.rfc-editor.org/rfc/rfc9420) — Messaging Layer Security (MLS); the streaming epoch-key rekey ([CC 5.1](#5.1)) conforms to MLS TreeKEM |
| [SFrame] | [draft-ietf-sframe](https://datatracker.ietf.org/wg/sframe/about/) — Secure Frames; the per-frame AEAD chunk seal ([CC 5.3.3.1](#5.3.3.1)) conforms to the SFrame model |
| [FIPS-203] | [FIPS 203](https://csrc.nist.gov/pubs/fips/203/final) — ML-KEM (Module-Lattice KEM); the post-quantum half of the hybrid KEM (ML-KEM-768) |
| [FIPS-204] | [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final) — ML-DSA (Module-Lattice signatures); the post-quantum half of the hybrid signature (ML-DSA-65) |
| [RFC-9180] | [RFC 9180](https://www.rfc-editor.org/rfc/rfc9180) — Hybrid Public Key Encryption (HPKE); the `key_grant` wrap shape |

Informational citations (Magnifica Humanitas, anthropological literature, Ubuntu philosophical literature, etc.) appear in [CC 8.6.1](#8.6.1) without normative force.

### 2.6.6 `canonicalization-cell` — H3 cell canonicalization

Geographic claims compose with [CC 3.3.3](#3.3.3) `location_proof` and [CC 3.2](#3.2) `community` with `cohort_subkind: geographic`.

Geographic primitives in CEG use [H3 hierarchical hexagonal indexing](https://h3geo.org/) as the canonical cell-identifier encoding. H3 partitions the Earth's surface into hexagonal cells at 16 resolution levels (0 = coarsest, ~4.3 M km² per cell; 15 = finest, ~0.9 m² per cell). Each cell has a 64-bit integer ID, conventionally encoded as a 15-character lowercase hex string.

**Canonical form for `cell_id`**:

- 15-character lowercase hex string (no `0x` prefix; per [CC 2.6.3](#2.6.3))
- The cell encodes its own resolution in the standard H3 index bit layout; a conformant decoder extracts the resolution **via the H3 library** (the resolution field lives in bits 52–55), **NOT** by reading the high 4 bits — the high nibble is the H3 **mode marker** (cell-mode = `1`), not the resolution
- Leading zeros preserved (a resolution-0 cell at base position 0 is `8001fffffffffff`, not `1fffffffffff` — the high nibble `8` is the mode marker, correctly consistent with res-0)

**Canonical form for `cell_resolution`**:

- Integer in `[0, 15]`
- MUST equal the resolution **decoded from the H3 index** of `cell_id` (substrate verifies the redundancy on admission via the H3 library; mismatched pairs MUST be rejected as malformed)

#### 2.6.6.1 `location` — Rough-only enforcement for `location_proof` (normative)

Location disclosure is bounded by the protocol itself, not by operator goodwill — the Non-maleficence principle made mechanical. A `location_proof` subject_kind Contribution ([CC 3.3.3](#3.3.3)) MUST carry `cell_resolution ≤ 7` (H3 resolution 7 hexagons average ~5 km² edge-length, sufficient for city/borough-level disclosure without block/building precision). Producers attempting to emit finer-resolution `location_proof` Contributions MUST have admission rejected at the substrate gate.

This is the wire-format-enforced privacy promise: **rough is rough by protocol**, not by operator policy. A producer cannot accidentally over-share at the protocol layer; a malformed client cannot publish a precise location even if its UI fails to gate. Substrate emits `hard_case:location_proof_resolution_violation` ([CC 3.4.2](#3.4.2)) on rejection so operators can observe malformed-producer patterns.

#### 2.6.6.2 `cell` — Cell containment

A cell `C` at resolution `R_C` is **contained within** a cell `B` at resolution `R_B` iff:

- `R_C >= R_B` (the contained cell is at equal or finer resolution); AND
- The parent-walk from `C` at resolution `R_C - 1, R_C - 2,..., R_B` reaches exactly `B` (standard H3 hierarchy semantics; `h3ToParent` library call)

Used by community admission gates per [CC 4.4.3.2](#4.4.3.2) Policy M: a `location_proof` Contribution's `cell_id` MUST be contained within the geographic community's `geographic_constraint.cell_id` for membership admission.

#### 2.6.6.3 `documents` — Scope of the H3 rule

Scope pointer: the H3 canonicalization rules above (lowercase-hex `cell_id`, rough-only `cell_resolution ≤ 7`, containment for community admission).

What the H3 rule does NOT do:
- Mandate H3 over alternative geospatial systems (S2, Geohash) — H3 is chosen for hex-cell uniformity, well-defined parent/child hierarchy, and protocol-agnostic absence of a centralized gazetteer dependency. Operator-internal use of other systems is unconstrained; the wire format uses H3.
- Provide a place-name registry. Communities self-name; cell IDs are the substrate-level binding. UI may map cell IDs to human-readable names per consumer policy.
- Restrict community-side `geographic_constraint.cell_resolution`. A community CAN scope itself at any resolution (e.g., an "Austin metro" community at resolution 5, ~250 km²; a smaller-scale "Downtown Austin" community at resolution 7, ~5 km²). The rough-only invariant applies to `location_proof`, NOT to community definitions.

### 2.6.7 `time` — Time and clocks

Every `signed_at`, `asserted_at`, `valid_until`, `delegation_valid_from`, `delegation_valid_until`, and `cosigned_at` in this specification refers to **wall-clock UTC** at the asserting peer's clock. Producers SHOULD synchronize via [NTPv4 (RFC 5905)](https://www.rfc-editor.org/rfc/rfc5905) or [Roughtime](https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/) to a known-good time source. The maximum tolerated skew between attester clock and consumer clock for a freshness check is **±5 minutes** by default; tighter thresholds MAY be applied by per-application consumer policy. Consumers receiving an attestation with `signed_at` more than 5 minutes in the future MUST reject as malformed.

Time-skew between cosigners on a single STH ([CC 5.3.1](#5.3.1)) is bounded by the STH's own `signed_at` field; cosignatures with `signed_at` farther than 5 minutes from the STH's published `signed_at` MUST be rejected.

For long-lived attestations carrying `valid_until` in the future, the freshness check is "the attestation has not yet reached its `valid_until`, AND the current consumer clock is within ±5 minutes of the substrate's network-consensus clock"; a consumer whose clock drifts past the skew bound MUST fail-secure (reject) rather than accept.

### 2.6.8 `key_id` — NodeCode — the canonical `key_id` shorthand encoding (normative)

Federation `key_id`s are long opaque identifiers, unfit for a human to type or read aloud. **NodeCode** is the **one** human-shareable shorthand — a compact, QR-able, checksummed render of a peer's identity for **bootstrap UX**. It is pinned here so **every implementation renders and parses the same code for the same key** — a cross-impl determinism requirement of the same class as [CC 2.6.3](#2.6.3) hex / [CC 2.6.1](#2.6.1) JCS. It is a deterministic *render of an existing `key_id`*, **not** a new envelope field — additive on the frozen 1+4 surface. NodeCode resolution is **DNS-free**: the decoded `key_id` resolves to a destination via the signed `transport_destination` → Reticulum chain ([CC 3.3.6.2](#3.3.6.2) / [CC 4.4.3.2.4.1](#4.4.3.2.4.1)); a NodeCode carries no hostname.

**Binary payload (normative):**

```
offset  size  field
------  ----  -----
   0      1   version                 = 0x01
   1     32   key_id_hash             = SHA-256(key_id_str, UTF-8)
  33     32   pubkey_ed25519          (raw 32 bytes)
  65      1   key_id_str_len          (0–255)
  66      N   key_id_str              (UTF-8)
 66+N     1   transport_hint_len      (0–255)
 67+N     M   transport_hint          (UTF-8; OPTIONAL — len 0 if absent)
67+N+M    1   alias_hint_len          (0–255)
68+N+M    K   alias_hint              (UTF-8; OPTIONAL — len 0 if absent)
   …      2   crc16                   = CRC-16-CCITT over ALL preceding bytes
```

- All length-prefixed fields are **1-byte** length (max 255 UTF-8 bytes); a field overflow is a malformed NodeCode.
- `key_id_hash` is the stable 32-byte fingerprint (suitable for binary-only Edge ANNOUNCE surfaces); `key_id_str` carries the display form so a round-trip preserves exactly what the user saw. Both are carried — a decoder MUST verify `SHA-256(key_id_str) == key_id_hash`.
- **CRC-16-CCITT**: polynomial `0x1021`, init `0xFFFF`, **no** final xor, big-endian; computed over every byte before the trailing 2.

**String form (normative):** the payload is **RFC 4648 base32** (alphabet `A–Z2–7`) with padding **stripped** on encode (re-padded on decode), then split into **4-character groups joined by `-`** and prefixed with **`CIRIS-V1-`**:

```
CIRIS-V1-ABCD-EFGH-IJKL-…
```

The encoded form is **case-insensitive** (decoder upper-cases input) and a conformant decoder MUST tolerate dashes, embedded whitespace, and the dash-free QR form. The version token in the prefix (`V1`) tracks the payload `version` byte; a future layout bumps both.

### 2.6.9 `conformance-language` — Conformance language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [BCP 14](https://www.rfc-editor.org/info/bcp14) ([RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) + [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)) when, and only when, they appear in all capitals, as shown here.

#### 2.6.9.1 `informative` — Normative vs informative content (what interop requires)

A reader may **agree with the protocol and disagree with its philosophy** and still build a fully conforming implementation. The two are deliberately separable:

- **Normative (binding for interoperability):** the wire format and its conformance surface — the [CC 2.4](#2.4) structural primitives; the [CC 2.1](#2.1) envelope fields; the [CC 3.1](#3.1) namespace + `subject_kind`s; the [CC 2.6.2–2.6.1](#2.6) canonicalization rules; the [CC 3.5](#3.5) relation precedence; the [CC 3.4](#3.4) reserved-prefix rules; the [CC 4.4](#4.4) composition policies; the [CC 5.3](#5.3) endpoint shapes; and every RFC-2119-keyworded statement. This is exactly the surface enumerated in [CC 1.7](#1.7) ("report the surface beside the invariant"). **Conformance is judged against this and nothing else.**
- **Informative (explanatory framing; NOT binding):** the motivating philosophy and rationale — notably [CC 1.13.1](#1.13.1) (the Ubuntu / relational-anthropology substrate), the cross-tradition readings, and prose written as motivation rather than requirement. These explain *why* the normative choices were made; they add **no** conformance obligations. An implementer who rejects the anthropology but emits/consumes wire-correct Contributions is conforming.

Where framing produced a concrete wire consequence, that consequence is restated as a normative rule in its own section (e.g., structural invisibility is motivated informatively but enforced normatively at [CC 5.2](#5.2), bounded by [CC 1.13.3](#1.13.3)). When in doubt, the RFC-2119 keywords and the [CC 1.7](#1.7) surface govern; informative prose never overrides them.
