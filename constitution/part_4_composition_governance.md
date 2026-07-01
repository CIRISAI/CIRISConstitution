# Part 4 — Composition & Governance

**Decimal range** `4.x` · **96 sections** · **page budget 26pp** · [← master index](README.md)

> How attestations compose into trust; self-governance, amendment, moderation, and the human halt-authority.

The substrate carries edges; consumers compose verdicts. That separation is the spine of this Part. Everything here serves one purpose: keeping trust *constituted relationally* — through attestation by others, not self-declaration — and keeping the whole federation revocable, because consent (M-1's load-bearing property) requires a halt-authority that lives outside the system being halted.

---

## 4.1 `anti-pattern` — Anti-patterns

These are wire-format reaches that fail the [CC 1.2](#1.2) operational-language gate or import Cartesian-individualist defaults. They are recorded so the next generation of authors finds the discipline before the wire format does. A CEG-Conforming Producer (CCP) SHOULD NOT emit attestations matching the anti-patterns below.

### 4.1.1 `anti-pattern-delegation` — Delegation-laundering anti-pattern

`delegates_to → delegates_to → delegates_to →... → attacker` chains, where each hop is individually well-formed but the aggregate routes trust to a terminal attester the original delegator would not have approved.

| What's wrong | Correct expression |
|---|---|
| Unbounded depth `delegates_to` chains | Consumer policy MUST cap traversal depth at **5 hops** by default (configurable); chains longer than the cap are treated as `attestation:self_verify` only (no transitive trust) |
| Cycles (A → B → A) | Substrate MUST detect cycles on the `delegates_to` graph and reject the cycle-closing emission |
| Aggregate-weight concentration | Consumer policy SHOULD cap the trust weight any single terminal delegate can accumulate from a given root attester at **0.5 × root_trust** by default |

### 4.1.2 `pattern` — Discipline pattern

The recurring shape across most anti-patterns: **extending the wire format so single attesters can pre-declare their own state more richly**. Each one is reachable, none is necessary.

The Ubuntu-primary discipline cuts cleanly: standing is constituted relationally through attestation by others, not through self-declaration. The wire format should **resist** primitives that let a single key announce its own state without external composition. The substrate is austere by design so consumers compose verdicts; richer narrative expression belongs in `context:`, `evidence_refs[]`, and downstream witness attestations, not in new envelope enum members or new self-attestation prefix families.

### 4.1.3 `already-rejected` — Already-rejected wire additions

| Anti-pattern | What it would smuggle | Correct expression |
|---|---|---|
| `detection:emergent_deception:{axis}` | Moral verdict ("deception") in prefix name | `detection:correlated_action:{axis}` — mechanism-descriptive |
| `attestation:l{N}:*` | Ladder-position (verdict-shape) in wire prefix — same shape as `score:trustworthiness:*` smuggling meta-judgment as wire | `attestation:{mechanism}` bare mechanism (`self_verify` / `hardware_rooted` / `registry_consensus` / `license_validity` / `agent_integrity`); consumer composes L1-L5 ladder via [CC 4.4.3.6](#4.4.3.6) Policy I |
| `score:trustworthiness:{entity}` | Meta-judgment as separate prefix | Compose downstream from `licensure:*` / `capacity:*` / `provenance:*` attestations |
| `flag:bad_actor:{axis}` | Pejorative wire vocabulary | Surface as low-confidence scores on `provenance:*` and `coherence_standing:*`; adjudicate via NodeCore P8 quorum |
| `grounding:{tradition}:{principle}` | "Tradition" claims are interpretive, not mechanism | Reuse `delegates_to` structural primitive per [CC 2.4.1.2](#2.4.1.2) |

### 4.1.4 `withdraws-arbitrage` — `withdraws` arbitrage

Per [CC 2.4.1.3](#2.4.1.3): a misattester can `withdraws` instead of `recants` to dodge the trust penalty consumers apply to acknowledged-error chains.

| What's wrong | Mitigation |
|---|---|
| Asymmetric attester incentive | Consumer policy MUST track per-attester `withdraws:recants` ratio over a rolling window; attesters whose ratio exceeds a configured threshold (default 5:1) SHOULD be downweighted regardless of which structural primitive they use. The `recants` distinction matters [CC 2.4.1.3](#2.4.1.3), but the practical anti-arbitrage countermeasure is consumer-policy behavioral analysis, not a wire-format change. |

### 4.1.5 `registry-rejections` — Rejected stress-test reaches

The stories below each reached for a richer self-declaration; each is reducible to existing primitives.

| Anti-pattern | Stories reached for | Why reject | Correct expression |
|---|---|---|---|
| `epistemic_mode: introspection` | 7 stories | Cartesian shortcut — lone subject pre-declaring inner state as if that constitutes standing | `witness_relation: self` + `confidence < 1.0` + pending external composition. The wire makes introspection awkward to express, because the framework's claim is that self-knowledge does not constitute standing without external witness. |
| `epistemic_mode: testimony` | (same set) | Reducible to existing values | `epistemic_mode: external` + `witness_relation: external` |
| `transparency:{kind}` standalone prefix | 12 stories | Disclosure is constituted by reception, not announcement. Cartesian self-claim shape. | `evidence_refs[]` carries the reasoning-chain hash; downstream `transparency_log:inclusion` from a witness who actually retrieved it. |
| `stake: civic` / `epistemic` / `dignitary` | 10 stories | `civic` = `stake: reputational + cohort_scope: community`. `epistemic` = `confidence + stake: reputational` (same axis as confidence; not separate). `dignitary` lives on wrong axis (stake names what the attester loses; dignity harm is what the attested loses → belongs in `harm_class:dignity_harm`). | Compose existing values with cohort/harm-class. |
| `oversight_mode: deferred` / `active` / `advisory` | 6 stories | All map to existing HITL/HOTL/HOOTL | `deferred` = HITL pre-decision; `active` = HITL with substrate monitoring; `advisory` = HOTL |
| `provenance_walk` as wire primitive | (1 reviewer) | UX concern smuggled into wire format | Consumer-side composition (Portal / Verify dashboards / agent introspection); the chain already walks via `references_attestation_id` + `topical_relation:*` + `valid_until` |
| Renaming canonical capacity factors and HE-300 categories to "kid-friendly" names | 8 stories | Canonical names map to a worked-out epistemic/ethical lattice that loses precision under accessibility renames | Translation glossary in [`LANGUAGE_PRIMER.md`](../LANGUAGE_PRIMER.md) (spec name ↔ narrative name) + version pinning in worked examples |

## 4.2 `accord` — The HUMANITY_ACCORD constitutional layer

The federation is symmetric by design — every participant binds every other under the Recursive Golden Rule. There is exactly one asymmetry in the whole wire format, and it points outward: humanity's right to halt the system. This section specifies it.

### 4.2.1 `authority` — Authority scope

`HUMANITY_ACCORD` signatures are valid only on `EmergencyShutdown CONSTITUTIONAL` (`IncidentSeverity::INCIDENT_CONSTITUTIONAL = 5`), `accord:invoke:notify:{notify_id}`, `accord:invoke:drill:{drill_id}`, `accord:lifecycle:active`, and the corresponding `FederationAnnouncement` priority `AccordCarrier`. Announcements of any other priority signed by accord-holder keys are rejected at admission (out of role). Federation-side authority cannot sign `AccordCarrier`; humanity-accord authority cannot sign anything else. **Wire-isolated AND scope-isolated.**

#### 4.2.1.1 `invocation` — Invocation canonical bytes (anti-replay)

Every `accord:invoke:*` Contribution signs the following canonical bytes (BOTH the discriminator AND a per-invocation nonce are in the signed payload — preventing CONSTITUTIONAL ↔ notify ↔ drill cross-replay):

```
canonical = sha256(
 "ciris.accord_invoke.v1\n" ||
 "invocation_kind=" || ("CONSTITUTIONAL" | "notify" | "drill") || "\n" ||
 "invocation_id=" || halt_id_or_notify_id_or_drill_id || "\n" ||
 "nonce=" || base64url(rand_32_bytes) || "\n" ||
 "asserted_at=" || rfc3339_canonical || "\n" || // per §0.5
 "valid_until=" || rfc3339_canonical || "\n" ||
 "payload_sha256=" || sha256_hex_lowercase_of_payload // per §0.6)
```

Hybrid signature per [CC 3.1.2.1](part_3_the_namespace.md): Ed25519 + ML-DSA-65 bound-payload. Each of the 2-of-3 holders signs `canonical` independently; consumer verifies all three signatures against the same `canonical` bytes and counts ≥ 2 valid.

The substrate MUST reject duplicate `invocation_id` values within the `valid_until` window (per-kind unique).

#### 4.2.1.2 `notify` — `notify` vs `CONSTITUTIONAL` — consumer-UI requirement

Wire-format isolation alone does not close the social-engineering risk that downstream UI conflates a `notify` with a CONSTITUTIONAL halt. The consumer-UI requirement below is therefore the load-bearing safeguard: it stops accord-holders from being socially pressured into emitting a `notify` that carries CONSTITUTIONAL social weight without CONSTITUTIONAL substrate weight.

A CEG-Conforming Consumer (CCC) presenting accord invocations to humans MUST visually distinguish the four kinds:

- **`CONSTITUTIONAL`** — kill-switch authority; full halt; visible as an unambiguous emergency banner.
- **`notify`** — federation-wide accord-holder communication; MUST NOT be visually conflated with CONSTITUTIONAL.
- **`drill`** — accord-holder exercise; MUST be visually marked as a drill (e.g., explicit "[DRILL]" prefix on any human-visible surface).
- **`lifecycle:active`** — resumption from a constitutional halt (the federation coming back online; [CC 4.2.1.3](#4213-lifecycle--lifecycle-resumption-canonical-bytes--accordlifecycleactive)). MUST be shown as its own unambiguous "reactivated — resumed from constitutional halt" state, never conflated with an active CONSTITUTIONAL halt (its opposite) nor with a `notify`.

#### 4.2.1.3 `lifecycle` — Lifecycle (resumption) canonical bytes — `accord:lifecycle:active`

`accord:lifecycle:active` is the **only** sanctioned resumption after a `CONSTITUTIONAL` halt ([CC 4.2.1](#421-authority--authority-scope)). It signs a **separate canonical-bytes domain** from `accord:invoke:*`: the `accord:invoke` `invocation_kind` stays closed to `{CONSTITUTIONAL, notify, drill}` (the scope-isolation rule — a fourth value is *not* added to it), and resumption rides its own domain prefix so an invoke signature can never be replayed as a resumption, nor a resumption as an invoke:

```
canonical = sha256(
 "ciris.accord_lifecycle.v1\n" ||                       // distinct domain — NOT accord_invoke.v1
 "invocation_kind=lifecycle:active\n" ||
 "invocation_id=" || resumption_id || "\n" ||
 "resumes_halt_id=" || prior_constitutional_invocation_id || "\n" ||
 "nonce=" || base64url(rand_32_bytes) || "\n" ||
 "asserted_at=" || rfc3339_canonical || "\n" ||        // per §0.5
 "valid_until=" || rfc3339_canonical || "\n" ||
 "payload_sha256=" || sha256_hex_lowercase_of_payload) // per §0.6
```

**`resumes_halt_id` is mandatory and binds the resumption to the one halt it ends.** A resumption authorizes ending a *single named* `CONSTITUTIONAL` halt, not resumption-in-general — so a stockpiled or replayed `lifecycle:active` cannot silently un-halt a *later*, unrelated kill; the signature is worthless against any halt but the one it names. The substrate MUST reject a `lifecycle:active` whose `resumes_halt_id` does not match the currently-active CONSTITUTIONAL halt, and MUST reject a duplicate `invocation_id` within the `valid_until` window.

**Resumption is not a fire — it admits at quorum, never at the fire floor.** The [CC 4.2.6](#426-live-quorum--live-quorum-operation--recovery-under-decimation-normative) bias gradient runs `fire ≤ roster-change ≤ standing`. Firing leans easiest (floor = 1) because a missed fire is terminal; **un-firing leans hard**, because a lone coerced or replayed key trivially undoing a legitimate halt is precisely the failure the halt-authority exists to prevent. `lifecycle:active` therefore admits at **no less than the roster-change threshold — strict majority of the live set `L`, with the [CC 4.2.6](#426-live-quorum--live-quorum-operation--recovery-under-decimation-normative) steward backstop when `\|L\|` is small — never a lone signature.** It is hybrid-signed and tallied exactly as [CC 4.2.1.1](#4211-invocation--invocation-canonical-bytes-anti-replay), only over the resumption domain and at the resumption threshold.

This ratifies the CIRISVerify v6.10.0 first-implementation layout (issue #109), with one addition the implementation flagged as open: the **mandatory `resumes_halt_id` field** (its sub-Q1). Verify adjusts by the one-field change; until then its layout is first-impl-pending-cross-confirm, now confirmed with that field added.

### 4.2.2 `hardware-class` — Hardware-class taxonomy

| Value | Use |
|---|---|
| `HSM_FIPS_140_3_L3` | Production stewards (US / EU / APAC) |
| `Apple_Secure_Enclave` | Accord-holders on iOS/macOS |
| `YubiKey_5_FIPS` | Accord-holders preferring portable hardware tokens |
| `TPM_2_0` | Accord-holders on Linux/Windows desktops |
| `placeholder_pending_provisioning` | Interim value before actual hardware provisioning. Consumers MUST treat as `0.0` trust weight |
| `software_hsm_development` | DEVELOPMENT ONLY; consumer policy MUST reject for federation-scope verification |

Per-class recommended trust-multipliers: `HSM_FIPS_140_3_L3` = 1.0; `Apple_Secure_Enclave` = 0.95; `YubiKey_5_FIPS` = 0.95; `TPM_2_0` = 0.9; `placeholder_pending_provisioning` = 0.0; `software_hsm_development` = 0.0.

#### 4.2.2.1 `hardware-class-hardware` — Hardware-class self-assertion gap (acknowledged)

The `hardware_class` field is a self-asserted string on each `federation_keys` row. There is no normative mechanism (TPM quote chain, Apple attestation, FIDO attestation) for a verifier to independently corroborate the claim. Per [CC 8.3.1](part_8_appendices.md) **R5** (acknowledged risk): consumer policy MUST treat the `hardware_class` field as a producer claim, not a cryptographically-attested fact. A planned roadmap item closes this via per-platform attestation-chain verification; until then the trust-multipliers in CC 4.2.2 above bind only as guidance.

### 4.2.3 `accord-holder` — The accord-holder triple

Three named human key holders. Initial state at federation genesis:

| Position | Holder | Threshold |
|---|---|---|
| 1 | Eric Moore | 2-of-3 |
| 2 | Eric Kudzin | 2-of-3 |
| 3 | Haley Bradley | 2-of-3 |

Hardware-attested. Permanent: no automatic decay; replacement requires out-of-band CIRIS L3C process per FEDERATION_ANNOUNCEMENT.md §4. This triple is the **seed** of a growable M-of-N roster; how the quorum is computed — and how the kill-switch stays operable — as holders are added, lost to decimation, and regained is specified in [CC 4.2.6](#426-live-quorum--live-quorum-operation--recovery-under-decimation-normative).

**Correlated-failure geometry:** two of the three holders share a household, so the 2-of-3 quorum is physically achievable from one street address — a correlated compromise/coercion surface that entrenchment makes harder to correct later. The authority at stake is the **full constitutional kill** (`EmergencyShutdown CONSTITUTIONAL` — not a recoverable pause), so the exposure is real and is not softened here; what scope isolation ([CC 4.2.1](#92-authority-scope)) does guarantee is that compromise cannot escalate *beyond* the kill — accord keys cannot sign grants, licenses, or amendments. **The mitigant is diversifying the holder set: finding new holders** (via the out-of-band replacement process, FEDERATION_ANNOUNCEMENT.md §4) so that no household — and ultimately no single jurisdiction — can assemble the quorum. This is an active obligation on CIRIS L3C, not a deferred nice-to-have.

**The HUMANITY_ACCORD triple is the canonical entrenched-`family` instance.** Per [CC 3.3.4](part_3_the_namespace.md), the accord-holder triple structurally IS a `family` subject_kind with:

```
family {
 family_key_id: "humanity-accord",
 family_name: "Humanity Accord",
 members: [
 {key_id: <eric-moore-key>, role: founder},
 {key_id: <eric-kudzin-key>, role: founder},
 {key_id: <haley-bradley-key>, role: founder}
 ],
 consensus_protocol: "quorum:2/3",
 consensus_protocol_entrenched: true // replacement requires §9.2 / FEDERATION_ANNOUNCEMENT.md §4.5.3 ceremony
}
```

The 2-of-3 multi-sig verifier at [CC 4.2.1.1](#921-invocation-canonical-bytes-anti-replay-01-scaffold) is the `quorum:2/3` consensus_protocol enforcement; the entrenchment property is what prevents any federation-internal authority from amending the protocol. CC 4.2 remains load-bearing for the **role-recognition policy** and the **scope-isolation** discipline. The constitutional asymmetry is "an entrenched family that is wire-scope-isolated to halt authority," not a one-off primitive. Other entrenched-family instances (a national-emergency triple, an international body, a court-ordered preservation triple) MAY appear in operator deployments; HUMANITY_ACCORD is the one CIRIS L3C deployments ship at genesis.

### 4.2.4 `policy-concern` — Concern split — key material vs role-recognition policy

**Key material** (Ed25519 + ML-DSA-65 pubkeys for the three holders) lives in **CIRISPersist substrate**: `federation_keys` rows with `identity_type="accord_holder"`, self-signed at provisioning, cross-attested by all three regional stewards.

**Role-recognition policy + verifier logic** lives in **`ciris-registry-core`**: the 2-of-3 multi-sig verification, the `EmergencyShutdown CONSTITUTIONAL` admin RPC, the audit hooks.

### 4.2.5 `isn` — Why this isn't a Golden-Rule violation

Per [CC 1.13.2](part_1_foundation.md): the Recursive Golden Rule binds *participants in the federation* to each other. Humanity-as-such occupies a position outside the federation's participant set, by design. The three named human key holders hold `AccordCarrier` authority that no federation-side authority class (including `SYSTEM_ADMIN` / `WISE_AUTHORITY` / per-install stewards) can grant itself, revoke, override, or decay. This is not a Golden-Rule exemption; it is the recognition that consent (M-1's load-bearing property) requires revocability, and revocability requires a halt-authority that lives outside the system being halted. The federation cannot deny humans the right to halt it, because no federation-internal protocol path to that signature exists.

### 4.2.6 `live-quorum` — Live-quorum operation & recovery under decimation (normative)

The genesis triple ([CC 4.2.3](#423-accord-holder--the-accord-holder-triple)) is the **seed** of a **growable M-of-N accord family**: holders are added, removed, or swapped through the same family membership-change `supersedes` machinery as any other `family` ([CC 4.4.3.4.2](#4432--admission-membership--membership-change-admission-per-consensus_protocol)). At any size, the question this section settles is **how the quorum is computed** — and the answer is what keeps the kill-switch operable in the one scenario it exists for.

**The deadlock it removes.** A quorum taken over the **standing roster** (M-of-N of every enrolled holder) **deadlocks under catastrophic loss**: if most holders are dead, incapacitated, or censored, the standing quorum is unreachable — the switch goes inoperable exactly when it is needed. The design target is the worst case: a misaligned superintelligence executing a **first strike against its own off-switch**, reducing the reachable, key-capable holders of a grown roster (e.g. 21) to one or two, with communications censored as the *expected* condition.

**The rule — one live quorum.** There is **no separate recovery protocol**; "decimation" is simply the case where the live set is small. Every accord decision (fire, roster change, or both) opens a bounded **participation window** `W`. Within `W` a holder participates by signing a fresh **proof-of-life bundled with a vote** over the proposal's server-issued nonce. When `W` closes, the **live set `L`** is the holders who proved life within it (always a subset of the pinned standing roster — only real, key-holding members count), and the decision is tallied **over `L`**. Absence is self-correcting (a holder who does not respond is simply *not in the denominator* — they cannot block by being gone); presence is self-asserting (showing up enters `L` with a vote). This is the inactivity-leak dynamic (Casper FFG) made the accord's standing rule, not an emergency exception.

**Proof-of-life modifies the quorum and carries a vote — it is *not* a veto.** A holder's signature both enters them into `L` (floating the live denominator, and thus the strict-majority threshold, *up* to include them) and records their yes/no. A presumed-dead holder who resurfaces therefore does **not** unilaterally defeat a proposal — they rejoin and are counted, and the proposal still succeeds on the live majority. The protection bought is the correct one: *a living, reachable holder cannot be erased from a decision without being counted and given a vote*, yet the family is never hostage to a single absent signature. A server-issued freshness nonce stops a replayed signature from manufacturing a phantom participant.

**Per-action thresholds, all taken over `L`:**

| Action | Threshold over `L` | Window |
|---|---|---|
| **Fire** (`CONSTITUTIONAL` kill, [CC 4.2.1.1](#4211-invocation--invocation-canonical-bytes-anti-replay)) | **floor = 1** — a single reachable survivor may fire | **none** — immediate on a fresh survivor signature |
| **Roster change** (add / remove / swap) | **strict majority of `L`** (`2·M > \|L\|`) | `W` = 72 h baseline (extensible to 7 d under a declared severe-degradation state) |
| **Standing acts** (non-emergency) | strict majority of the standing roster (unchanged) | normal cadence |

When `\|L\|` falls below `L_floor` (`3`, and certainly `1`), a **roster change** additionally requires a **2-of-3 quorum of the regional stewards** (us/eu/apac — the cross-attestation root the accord is already upstream-rooted in) to co-sign, removing the pure self-attestation of the most capturable case. **Firing is never gated this way.** A holder who proves life *after* a decision missed that vote is re-enrolled going forward (the Enoch Arden rebuttable-presumption pattern): past actions validly decided by the then-live set stand; the returnee simply rejoins.

**The steward floor is key-independent (H6).** The regional-steward backstop MUST be a **separately-pinned trust domain** — its signing keys **key-independent of** the holder-attestation root that cross-attests the accord holders at admission, not merely role-labeled "steward." Under a first strike the always-on steward HSMs are exactly the infrastructure an adversary targets first; a backstop sharing the holders' attestation root would collapse precisely when `|L| < L_floor`, when it is most needed. Registry publishes the steward-backstop PQC key set as its **own** trust domain (cross-confirmed at CIRISVerify FSD-004 H6 / issue #113), resolvable for the live-quorum tally independently of the holder root.

**The single optimization direction — minimize the missed fire.** A **missed fire** (the adversary decapitated everyone who could pull the plug) is **terminal and unrecoverable**; a **false fire** (an agent halted in error) is a **recoverable** governance nuisance — the agent is re-licensed; humanity cannot be un-extincted. Every lever therefore leans toward firing, with no countervailing brake: the bias gradient is **fire ≤ roster-change ≤ (former) standing quorum**, all over the live set, never over the absent roster. The firing floor sitting *below* the roster-change threshold is the whole point — even a partially-captured live set's honest minority, down to one, can still fire.

**Why this restores the accord and cannot seize it (the entrenchment proof).** The adversary cannot **forge** a holder — every proof-of-life is a hybrid signature over a pinned key — so it can only **remove** (kill/censor) or **coerce** existing ones. Against that: *firing* survives all but **total, sustained censorship of every honest holder on every channel** (a publishable signature, not a network round-trip, suffices to fire); a *false reconstitution* requires the adversary to capture a **live majority** *and* subvert the **independent steward floor** on separate channels, and every `accord_decision` is append-only logged, leaving an immutable trail for post-hoc governance reversal. The irreducible residual is **coercion/duress** — proof-of-life proves presence, not willingness — which is **bounded, not solved**, by the steward floor, the live majority, and transparency; it is named here as an open problem, not papered over. The live quorum is thus strictly a **restoration** of the accord's operability under loss; it grants no path to *weaken* or *seize* the halt-authority beyond this stated residual.

**Bounded steward recovery — restore-to-known-good (H7, a sanctioned exception to entrenchment).** Entrenchment ([CC 4.5.1.2](#4512-meta-amendment--entrenchment)) forbids a captured quorum from rewriting the accord roster — but that rule, unrelieved, would make a *successful seizure permanent*: if an adversary captures a quorum and installs an all-adversary roster, the only roster-mutation path is authorized by the (now-seized) roster, so the honest side could prove *what happened* in the append-only log yet hold no authority to *undo* it. This section sanctions one bounded reversal: the **key-independent steward quorum** (the floor above — a body the seized roster does not control) MAY authorize a **restore to a known-good roster snapshot taken from the append-only log at the seizure boundary** — and *only* that. It is **restore-only**: it can roll a seizure *back* to a state the log already proves was legitimate; it can **never install a novel roster**, so it cannot itself become a seizure vector. This *serves* entrenchment's telos rather than bending it — entrenchment stops the gate from being *seized*; restore-to-known-good stops a seizure from being *permanent*. Ratified by the founder under the [CC 4.5.1](#451-amendment--amendment-process--federation-contribution--wa-quorum--1-of-6-sign-off) maturity gate as a bounded exception to [CC 4.5.1.2](#4512-meta-amendment--entrenchment); the verify-side `verify_recovery_supersede` (CIRISVerify FSD-004 H7 / CIRISAccord#4) is fail-closed until this grounding, which is it.

**Wire shape — additive, no 1+4 change.** The mechanism rides three hybrid-signed (Ed25519 + ML-DSA-65, JCS-canonical) objects — `accord_proposal` (the action, nonce, and `window_until`), `accord_participation` (proof-of-life **+** vote in one signed object — entering `L` and voting are the same act), and `accord_decision` (the proposal + the participation bundle collected in `W` + the tally + any membership `supersedes` + the steward attestations when `\|L\| < L_floor`). **`DECIMATION` is a quorum-computation rule over the existing `CONSTITUTIONAL` kind — not a new invocation verb.** Verify-side obligations are **fail-closed**: each participation resolves to a current roster member in the pinned directory and verifies over the proposal nonce; the authoritative tally is CIRISServer recomputing over pinned `federation_keys`, the local objects advisory.

**Canonical-bytes pins (cross-confirmed with the verify first-impl — CIRISVerify FSD-004 §6 / issue #113).** Each live-quorum object signs a distinct, wire-isolated canonical-bytes domain, pinned the same way as the [CC 4.2.1.1](#4211-invocation--invocation-canonical-bytes-anti-replay) `accord:invoke` and [CC 4.2.1.3](#4213-lifecycle--lifecycle-resumption-canonical-bytes--accordlifecycleactive) `accord:lifecycle` preimages — distinct prefixes prevent invoke ↔ lifecycle ↔ proposal ↔ participation cross-replay:

```
proposal = sha256(
 "ciris.accord_proposal.v1\n" ||
 "family_key_id=" || family_key_id || "\n" ||
 "prior_family_digest=" || prior_family_digest || "\n" ||
 "action=" || action || "\n" ||            // fire | membership-change envelope | both
 "nonce=" || base64url(rand_32_bytes) || "\n" ||
 "window_until=" || rfc3339_canonical)
participation = sha256(
 "ciris.accord_participation.v1\n" ||
 "family_key_id=" || family_key_id || "\n" ||
 "refers_to=" || proposal_nonce_or_digest || "\n" ||
 "proof_of_life=true\n" ||
 "vote=" || ("yes" | "no" | "abstain") || "\n" ||
 "asserted_at=" || rfc3339_canonical || "\n" ||
 "nonce=" || base64url(rand_32_bytes))
```

`accord_decision` carries **no separate signing domain** — its authority is the contained `accord_participation` signatures + any membership `supersedes`. All hybrid (Ed25519 + ML-DSA-65). The CIRISVerify `accord_live_quorum` impl aligns to these pins; this section is the CEG-registry confirmation (#113). **Steward PQC publication:** the accord-holder **and** the (key-independent, H6) steward-backstop PQC halves are published over the [CC 5.3](part_5_transport_substrate.md) HTTPS-consensus steward-key endpoint, so the tally resolves every signer at the federation tier under RequireHybrid; absent publication, hybrid resolution **fails closed**.

**Physical assumption (deployment, not constitution).** The model rests only on a survivor getting a few-hundred-byte signed proof-of-life to a relaying node with **no standing infrastructure** — satisfiable over HF/shortwave skywave + NVIS store-and-forward (JS8Call) bridged into the mesh by EMP-hardened, geographically-distributed HF↔Reticulum gateways co-located with the steward sites. The signature is the trust, not the path, so any number of untrusted RF hops is safe. The relay/gateway backbone is itself adversary-targeted infrastructure and belongs in a deployment spec.

**Ratification status.** This section amends the **entrenched** [CC 4.2](#42-accord--the-humanity_accord-constitutional-layer) surface ([CC 4.5.1.2](#4512-meta-amendment--entrenchment)) — it changes how the §9 kill-switch quorum is computed (standing roster → live set). It is ratified by the **founder under the [CC 4.5.1](#451-amendment--amendment-process--federation-contribution--wa-quorum--1-of-6-sign-off) maturity gate** (pre-maturity founder/accord-holder authority over entrenched surfaces); post-maturity, a change to this surface requires the dedicated 2-of-3 entrenched accord ratification. The verify-side construction is staged in CIRISVerify FSD-004; the constitutional grounding it required (its Q5) is this section.

## 4.3 `wise-authority` — Designated Wise Authorities

## Section IV: Designated Wise Authorities

Designated Wise Authorities (WAs) are appointed under the Governance Charter (Annex B). Appointment, rotation, recusal, and appeals are external to this system’s control and follow explicit anti-capture rules.

Criteria for wisdom assessment include ethical coherence, track-record of sound judgment, complexity handling, epistemic humility, and absence of conflict-of-interest.

## 4.4 `composition-policies` — Composition policies

The substrate carries edges (attestations); consumers compose traversals (verdicts). CEG specifies a library of named reference policies. A CEG-Conforming Consumer MUST implement at least Policy A; the others are RECOMMENDED for richer compositions.

### 4.4.1 `frickerian` — Frickerian discipline — consumer-policy norms

Per Miranda Fricker's *epistemic injustice*: consumers SHOULD apply identity-prejudice-resistant weighting. Concretely:

- Don't downweight `testimonial_witness:*` from cohorts with low overall attestation density (testimonial preservation is precisely what corrects for that low density).
- Don't downweight `non_maleficence:*` claims about a partner just because the partner has a long `partner_role:*` track record (the long track record may be the harm).
- Apply [CC 4.4.3.9](#814-policy-d--lexical-vulnerability-priority) lexical-vulnerability-priority in tie-breaks involving small cohorts.

**Adversarial caveat**: the discipline above is consumer-policy-only; an adversary can emit `testimonial_witness:victim_of_my_competitor` exploiting the Frickerian non-downweighting rule. Per [CC 3.1.9.3](part_3_the_namespace.md), `testimonial_witness:*` is never sole evidence for `slashing:*`; per [CC 3.4.7](part_3_the_namespace.md) the consumer MUST also weight `witness_relation: self` claims against the attester's other-emission track record. The Frickerian rule applies AFTER these structural safeguards, not before them.

### 4.4.2 `aggregation` — Aggregation semantics — opinionated defaults

Per dimension+attested_key_id, the verdict is computed by composing attestations under the chosen policy. Default aggregation by polarity column ([CC 3.1](part_3_the_namespace.md)):

| Polarity column value | Default aggregation |
|---|---|
| `signed` | **Mean** of `score × confidence` across attesters |
| `boolean-via-score` | **Min** (any negative trumps positive — fail-secure for hard constraints like `prohibited:*`, `attestation:l*`) |
| `+1.0 only` / `positive-only` | **Max** across attesters (any positive is conclusive) |
| `-1.0 only` | **Min** across attesters (any negative is conclusive) |
| `enumerated` | **Most-recent** by `signed_at` from the attester(s) authorized to emit per [CC 3.4](part_3_the_namespace.md) |
| Detector dimensions (`detection:correlated_action:*`, `detection:distributive:access:*`, `ratchet:flag:*`) | **Median** across attesters (resists adversarial mean-pulling by a single captured detector) |

Specific dimensions override via consumer policy; the defaults above are the [CC 2.2](part_2_the_grammar.md) CEG-Conforming Consumer (CCC) minimum.

### 4.4.3 `reference` — Reference policies

The named reference policies below give consumers a shared library for turning edges into verdicts. Policy A (direct trust) is the conformance floor; the rest are RECOMMENDED for richer compositions and are referenced freely across this Part.

#### 4.4.3.1 `quorum` — Policy E — Locality-scaled quorum

Closes G3 (narrow-cell fresh-quorum-recusal infeasibility). Makes WA quorum size a function of decision locality:

```
quorum_size(scale) = f(locality:decision:{scale})

reference function (policy-tunable):
 local → 2
 regional → 3
 national → 4
 federation → 6

minimum cell-pool requirement for fresh-quorum recusal at scale S:
 min_pool(S) = quorum_size(S) × 2
```

Recusal is feasible when `cell_pool ≥ min_pool(S)`. Decision-scale-matching is structurally enforced; overreach surfaces as a named "locality mismatch" failure.

##### 4.4.3.1.1 `sub-quorum` — Sub-quorum fallback

When `cell_pool < min_pool(S)`, the consumer MUST take one of these explicit paths — there is no implicit fallback:

1. **Scale-down**: re-attest the decision at the next-lower `locality:decision:{scale}` (where the smaller quorum requirement is met) AND emit `hard_case:locality_scale_down` so the scaling event is observable for downstream review.
2. **Escalate**: emit `hard_case:locality_underpopulated` and route the decision to the federation-scale cell (which by definition has the largest pool).
3. **Liveness-defer**: emit `hard_case:locality_quorum_unreachable` and defer the decision until the cell pool grows. The deferred state MUST itself be reviewable via subsequent reconsideration.

Recursion safety: the [CC 4.5.1](part_4_composition_governance.md) amendment process routes through `locality:decision:federation` by default; the federation cell's pool is sized to make `cell_pool ≥ min_pool(federation)` always true at federation genesis. If federation-scale pool ever falls below `min_pool(federation)`, the entire amendment surface is in a constitutional crisis state and only the HUMANITY_ACCORD CONSTITUTIONAL halt ([CC 4.2](part_4_composition_governance.md)) can resolve it.

#### 4.4.3.2 `community-policy` — Policy M — Community membership composition

Per [CC 3.2](part_3_the_namespace.md) `community` + [CC 3.3.3](part_3_the_namespace.md) `location_proof`. Composition pattern for resolving the **current membership set** of a community, gating cohort-filtered visibility for `cohort_scope: community` content.

Sibling to [CC 4.4.3.4 Policy L](#8112-policy-l--selffamily-membership-composition-ceg-07-addition) (self/family) but with different defaults — community content is encrypted under a per-community DEK + emits `holds_bytes:sha256:*` with cleartext provenance; the privacy property is byte-confidential-to-members, not cohort-filtered-visibility.

##### 4.4.3.2.1 `community-three` — The three crypto tiers + the Community DEK cascade (normative)

The line is drawn at **"does it have a bounded membership roster?"** — yes → encrypt, no → plaintext. This gives a persecuted community a cryptographic home (a bounded **Community**) distinct from the unbounded **Commons**:

| Tier | `cohort_scope` | At-rest | Wire discovery | Reader |
|---|---|---|---|---|
| **self / family** | `self`, `family` | encrypted, per-write DEK | **none** ([CC 5.2](part_5_transport_substrate.md) structural invisibility) | occurrences / family members |
| **Community** | `community`, `affiliations` | **encrypted under the community DEK** | `holds_bytes:*` **+ cleartext provenance** | community members (DEK cascade) |
| **Commons** | `species`, `biosphere`, `federation` | **plaintext** | `holds_bytes:*` | anyone |

**Community DEK cascade (MANDATORY).** Community content (`cohort_scope: community | affiliations`) is encrypted at rest under a **per-community DEK** and emits `holds_bytes:sha256:*` carrying **cleartext provenance** (`attesting_key_id`, `community_id`, reason/dimension) so non-member holders can make an informed keep/evict decision without reading content. The community DEK **is the [CC 5.1](part_5_transport_substrate.md) epoch-DEK cascade applied to `cohort_scope: community`** — *a community is a stream its members subscribe to, cryptographically*: **one** DEK shared across emissions (per-emission cost O(1), not O(members)), wrapped to each member on admission, re-wrapped on membership change (CC 4.4.3.2.2), **`wrap_algorithm: v2` (hybrid PQC) MANDATORY** (same harvest-now-decrypt-later reasoning as [CC 4.4.3.4.1](#81124-key-grant-cascade-the-at-rest-encryption-flow) / [CC 5.1](part_5_transport_substrate.md)). This is **mandatory, not opt-in** — the tier name *is* the guarantee; a persecuted community is protected by *being a community*, not by remembering a flag. (Deliberately stronger than the [CC 4.4.3.4.1](#81124-key-grant-cascade-the-at-rest-encryption-flow) self/family opt-in: self/family has structural invisibility so at-rest crypto is defense-in-depth; community *federates*, so the DEK is its **sole** confidentiality boundary.)

**Holder-inspectability principle (normative rationale).** Any data a host holds above local tier MUST support an informed keep/evict decision: either the holder **inspects the bytes** (Commons — plaintext, maximally inspectable, hence the *preferred* social-distribution mechanism) **or** it **inspects the provenance** (Community — the cleartext `attesting_key_id` + `community_id` + reason on an otherwise-encrypted blob) and chooses to hold opaque ciphertext for a community it trusts. **Nothing above local tier is ever a forced, unattributable opaque blob.** This is *why* the split is shaped this way and what the eviction rules (persist `EvictionSweeper` / `evict_actor`) enforce.

**The `infrastructure` exception (normative).** A `community` with `cohort_subkind: infrastructure` ([CC 3.2](part_3_the_namespace.md)) — `ciris-canonical` and any governance/trust root — **opts OUT of the mandatory DEK cascade and is Commons-tier (plaintext, `holds_bytes:*`, no DEK)**. The trust root cannot be an opaque blob; its entire purpose is public auditability — transparency-seeking, not privacy-seeking. **Node→canonical traces** (conformance / `registry_consensus` emissions to a governance community) are therefore `cohort_scope: federation` (Commons/plaintext, world-readable) — a node enrolling in governance is thereby told its conformance traces are public.

##### 4.4.3.2.2 `community-forward` — Forward secrecy on community member removal (Option A)

With a community DEK, community **does** have the removed-member-can-still-decrypt concern. The [CC 4.4.3.4.5](#81125-forward-secrecy-on-member-removal-option-a-recommended-for-v1) **Option A** discipline applies identically: on member removal the substrate **rotates the community DEK** ([CC 4.5.12.1](part_4_composition_governance.md)); subsequent emissions are sealed under a DEK the removed member doesn't have. "Once shared, always shared" forward-only — content the removed member already received during membership stays in their cache (no PCS); they receive no NEW community content post-removal.

##### 4.4.3.2.3 `community-admission` — Community admission per `consensus_protocol` + `cohort_subkind`

A proposed membership change rides a `supersedes` Contribution on the community's latest admitted `community` Contribution. Substrate evaluates the CURRENT community's `consensus_protocol` (same six canonical kinds as family) AND any subkind-specific admission requirements:

```
admit_community_change(C, proposed: community_record):
 current = resolve_community(C, now)
 protocol = current_community_record(C).consensus_protocol
 subkind = current_community_record(C).cohort_subkind

 signatures_ok = evaluate_consensus_protocol(protocol, current, proposed.signatures)
 if not signatures_ok:
 emit hard_case:community_consensus_protocol_violation:{C}
 reject

 subkind_ok = evaluate_subkind_admission(subkind, current, proposed)
 if not subkind_ok:
 // For geographic: subkind admission failed (e.g., new member's location_proof
 // not contained in geographic_constraint, or expired location_proof)
 emit hard_case:community_consensus_protocol_violation:{C} // same observability prefix
 reject

 admit
 emit hard_case:community_membership_change:{C}
```

The `evaluate_subkind_admission` predicate dispatches per `cohort_subkind`:

```
evaluate_subkind_admission(subkind, current, proposed):
 match subkind:
 "geographic":
 # Per §5.6.8.10 geographic admission requirement
 for each NEW member in proposed.members (not in current):
 their_proof = latest valid location_proof from new_member.key_id
 if their_proof IS NULL:
 return false // no location_proof on file
 if their_proof.cell_id NOT contained in current.geographic_constraint.cell_id:
 return false // location outside community's geographic bound
 if their_proof.valid_until passed:
 return false // expired
 return true
 _:
 return true // unknown subkinds admit on consensus_protocol alone
```

Operator vocabularies extending `cohort_subkind` provide their own `evaluate_subkind_admission` predicates per the `custom:{id}` consensus_protocol hook pattern from [CC 4.4.3.4.2](#81123-membership-change-admission-per-consensus_protocol).

##### 4.4.3.2.4 `community-membership` — Community membership resolution

For community `C`, the current member set is computed as:

```
resolve_community(C, now):
 latest = federation_attestations.where(subject_kind == "community").where(envelope.community_key_id == C).where(supersedes chain → latest non-superseded).where(admission rule satisfied per CURRENT consensus_protocol;
 see §8.1.13.2)
 return {m.key_id for m in latest.envelope.members}
```

Same shape as `resolve_family` ([CC 4.4.3.4.4](#81122-family-membership-resolution)). Each `member.key_id` is an identity.

###### 4.4.3.2.4.1 `deterministic` — Deterministic resolution + member→address resolution (NORMATIVE)

In a CEG/RET stack member resolution replaces DNS+IP: it is a chain of *signed* bindings, and every implementation MUST resolve **identically** (an interop requirement). Two normative pins:

**(a) Determinism of `resolve_community`.** Where the CC 4.4.3.2.4 computation has choices, they are fixed:
- **`now` semantics** — the resolving Consumer's own clock; membership is evaluated as of `now` (a member is included iff joined ≤ `now` and not removed ≤ `now`). No global clock assumed.
- **"latest non-superseded"** — the `community` Contribution with the highest `signed_at`; on equal `signed_at`, the higher `canonical_bytes_hash` ([CC 2.6.1](part_2_the_grammar.md)) wins (total order, no ambiguity). The same comparator the R1/Q1 merge uses (quorum_weight DESC → signed_timestamp DESC → canonical_bytes_hash).
- **member ordering** — the returned set is canonically ordered by `key_id` (lowercase-hex byte order) for any downstream hashing/iteration.
- **founder-subset eval** — for `cohort_subkind: infrastructure` ([CC 3.2](part_3_the_namespace.md)) admission is `evaluate_consensus_protocol` over `{m: m.role == founder}`, NOT all members.

**(b) Member → reachable address (the DNS-free resolution).** Resolving a member identity to a Reticulum destination:

```
resolve_member_transport(C, now):
 members = resolve_community(C, now) // (a) above; founder-quorum verified
 out = []
 for M in members (canonical key_id order):
 occ = latest non-superseded identity_occurrence of M
 with transport_destination present, valid at now,
 hybrid-sig verified against M (or an occurrence of M) // §5.6.8.8.1
 if occ is null: continue // no authenticated binding → skip (fail-secure)
 td = occ.transport_destination
 REQUIRE td.destination_hash == rns_destination_hash( // §5.6.8.8.1.1 pinned two-stage
 td.reticulum_x25519_pubkey, td.reticulum_ed25519_pubkey,
 td.app_name, td.aspects) // NOT a flat-concat SHA-256
 out.push((M, td.destination_hash))
 return out // → Reticulum announce/path-request per dest
```

The three resolutions and their trust roots: **WHO** = `resolve_community` (signed Contribution + founder-quorum) · **BINDING** = `transport_destination` (federation-key-signed `identity_occurrence`, CC 3.3.6.2) · **WHERE** = Reticulum announce/path-request (mesh, no CEG). Reachability is never trust ([CC 5.3.3.4](part_5_transport_substrate.md)): a path that answers is not an authorization; only the signed binding + quorum are.

**Cold-start (bootstrap).** A node that knows only `community_key_id` needs two out-of-band pins: (1) the `community_key_id` itself (trust anchor) and (2) ≥1 **seed `destination_hash`** (reachability). It reaches any one seed, pulls the signed `community` Contribution, runs `resolve_member_transport`, verifies founder-quorum against the pinned `community_key_id`, then floats on the live set thereafter. A malicious seed cannot forge membership (quorum signature check) — it can only deny service (try another seed). **Bootstrap reachability ≠ bootstrap trust.** `ciris-canonical` ([CC 3.2](part_3_the_namespace.md)) is the root community whose seeds clients pin.

##### 4.4.3.2.5 `admission-geographic` — Geographic-community admission flow (worked example)

```
1. Alice publishes a location_proof:
 subject_kind: location_proof
 subject_key_id: alice_root_key
 cell_id: "872830828ffffff" // H3 res 7, ~5 km², downtown Austin
 cell_resolution: 7
 asserted_at: now
 valid_until: now + 30 days
 cohort_scope: federation // public; the disclosure IS the opt-in

 Substrate admits (resolution 7 ≤ 7 OK). Emission federates.

2. Alice proposes joining Austin community:
 subject_kind: community
 community_key_id: austin-community
 supersedes: prior_austin_community_record_id
 members: [...existing..., {key_id: alice_root_key, joined_at: now, role: member}]
 signatures: [...current_member_sigs] // satisfies majority rule

3. Substrate admission gate (per §8.1.13.2):
 - signatures_ok: majority rule satisfied ✓
 - subkind: "geographic" → evaluate_subkind_admission:
 - alice_root_key's latest valid location_proof exists
 - cell_id "872830828ffffff" CONTAINED in "85283473fffffff" (austin metro, res 5)
 via §0.8.2 containment (res 7 ≥ res 5; parent-walk reaches the constraint)
 - valid_until in the future
 - subkind_ok ✓
 - admit + emit hard_case:community_membership_change:austin-community

4. Alice now receives cohort-filtered visibility for cohort_scope:community content
 with community_id: austin-community. No key_grant cascade (community is unencrypted);
 no at-rest wrap; substrate emits holds_bytes:* for community content per status quo.
```

##### 4.4.3.2.6 `delivery-extension` — Delivery extension — `delivery_mode` × Policy M

Policy M's community-membership composition extends to govern the **delivery axis**. The subscriber-set for any push-delivery flow IS a `community` Contribution; "subscribe = join the community"; it inherits revocation, consensus, and structural-invisibility from Policy M unchanged.

**Subscriber-set composition**:

```
For a Contribution C with delivery_mode = push AND cohort_scope = community:
 subscriber_set(C) = resolve_community(C.community_id, now)
 per §8.1.13.1 community membership resolution

The community is admitted under the standard Policy M consensus_protocol
options (founder_only / unanimous / majority / quorum:M/N / weighted /
custom) per §8.1.13.2. Subscription-specific admission semantics —
producer_gated (publisher approves each member) vs open (anyone can
join) — ride the consensus_protocol choice:

 producer_gated → consensus_protocol = "founder_only" with the
 publisher as sole founder; the publisher authorizes
 each new subscriber
 open → consensus_protocol = "open:self_admit" (open-vocab
 extension hook) where any subject signs their own
 admission Contribution
```

**Cardinality unified across observer-share and multicast**:

| Cardinality | Per-subscriber crypto | Epoch handling |
|---|---|---|
| **N=1 (observer-share)** | Single `key_grant` ([CC 3.3.2](part_3_the_namespace.md)); no epoch needed (one recipient, one DEK) | No epoch — single grant, single DEK; revocation = `withdraws` against the grant |
| **N>1 (multicast)** | Flat per-epoch `key_grant` cascade — one grant per (subscriber, epoch); the stream-epoch DEK seals content O(1), the cascade distributes the 32-byte epoch key O(N)/epoch per [CC 5.1](part_5_transport_substrate.md) | Per-`(stream_id, epoch)` axis; epoch rolls on member removal (mandatory) + time/bytes (optional) per [CC 5.1](part_5_transport_substrate.md) D3 |

The same Policy M machinery handles both cardinalities — the difference is purely the cascade fan-out factor.

**Composition with `delivery_mode: pull` (default)**:

For `delivery_mode: pull`, subscribers discover via the standard `holds_bytes:sha256:*` directory per [CC 5.3.2](part_5_transport_substrate.md). Policy M still resolves the community for visibility-filtering (consumer reads `community_id` envelope field, walks the membership, filters out non-member peers from the discovery surface). No fan-out push; no `delivery_receipt` emission required (best-effort).

**Composition with `delivery_mode: push`**:

For `delivery_mode: push`, the substrate fans out to `entitled ∧ reachable` per [CC 5.3.3.4](part_5_transport_substrate.md) D6 liveness invariant. Entitlement = Policy M membership resolution (durable, signed CEG, replicated, logged); reachability = Edge `reachability.rs` node-local presence tracker (TTL sec/min, NEVER an attestation, never replicated, never logged). Missed (entitled-but-unreachable) members fall back to pull on reconnect per [CC 5.3.3.4](part_5_transport_substrate.md).

**`history_on_join` × Policy M membership additions**:

On a new-member admission via Policy M, the new member's `history_on_join` envelope value determines retroactive content delivery:

- `from_join` (default) — new member receives current-epoch content forward only; no retroactive `key_grant` cascade
- `full` — new member receives `key_grant`s for prior epochs subject to the [CC 5.1](part_5_transport_substrate.md) P4 catch-up bound (`min(operator depth cap, chunk-eviction horizon)`); evicted-epoch grants return `ContentMiss` per the [`MISSION.md`](../../MISSION.md) fail-honest invariant

This composes with [CC 4.4.3.4.5](#81125-forward-secrecy-on-member-removal-option-a-recommended-for-v1) Option A forward-secrecy: removed members retain extant `key_grant`s for content they were entitled to during membership; new members may or may not get retroactive grants per `history_on_join`. The substrate's forward-secrecy posture is uniform across consent, takedown, membership-departure, AND delivery-onboarding surfaces.

##### 4.4.3.2.7 `composition-8-1-13-6` — Composition with consent + self-collectives

Communities compose with consent and self-collectives cleanly:

- A community member who is also a CIRISAgent-using individual has an `identity_occurrence` set; community content arriving at the member's identity_key is then propagated to their occurrences via Policy L's at-rest cascade (if the member's local substrate chose to re-emit the community content at `cohort_scope: self` for cross-device sync; otherwise community content stays at the cohort_scope: community visibility on each device the member uses to query)
- A community member who is also a subject in `subject_key_ids` of a community-scoped Contribution retains revocation authority per [CC 2.4.1.1](part_2_the_grammar.md) rule 2; the orthogonality between cohort_scope (visibility) and subject_key_ids (revocability) holds at community scope same as at family scope
- A geographic community whose `geographic_constraint` covers a region that overlaps a family's at-home location does NOT cross-contaminate: families are not auto-admitted to communities; communities are not auto-admitted to families. Each membership is explicit, ceremony-shaped, and independent.

##### 4.4.3.2.8 `affiliations` — The institutional cohort (necessity, not interest) (normative)

A **community** ([CC 4.4.3.2](part_4_composition_governance.md)) gathers by *interest* — voluntary, opt-in, no role compels it. An **affiliation** (`cohort_scope: affiliations`) gathers by *necessity* — the work, institution, or office a person belongs to because their role requires it. The discriminator is the single `cohort_scope` value; affiliations **share the CommunityDek crypto tier** ([CC 4.4.3.2.1](part_4_composition_governance.md)) and all the community machinery (DEK cascade, forward secrecy on removal, `consensus_protocol` admission), and add **institutional governance by construction** through one declared config record. Everything in that record is **DECLARED at creation and visible to members on joining** — there are no undeclared institutional powers.

**Necessity is an axis, not a binary (the kibbutz catch).** A few institutions are *voluntarily entered yet total* (a collective settlement, a religious order). The interest/necessity split is therefore carried by an explicit `membership_basis` field — `{voluntary-total | ascriptive | role-assigned | employment-contract}` — orthogonal to `cohort_scope`, so a body can declare institutional governance without asserting a coercion that does not exist. A group that needs **no** institutional governance is simply a `community`; affiliation's machinery is never forced on a body with no use for it.

**Mandatory-with-default, not mandatory-to-author (the low-floor guarantee).** The two mandatory limbs — **data-classification** and **retention** — are *mandatory in that a value MUST resolve*, **not** that a steward must hand-author a scheme. The constitution ships a canonical no-op default (a single `internal` class; retention = `rotate-forward` per [CC 6.1.2](part_6_the_coherence_mathematics.md)/`archive_mode` [CC 3.3](part_3_the_namespace.md)) and named **`affiliation_archetype` presets** (e.g. `informal_adhoc`, `nonprofit_board`, `healthcare_provider`, `legal_practice`, `gov_body`, `igo`) that pre-fill every field below. A 5-person committee sets one field (`affiliation_archetype: informal_adhoc`) and is served by construction; a regulated giant overrides into the full matrix. The optional limbs — **hierarchy**, **lawful-access/transparency** — are absent until declared and scale up only when needed.

**A. Classification + retention — MANDATORY, default-satisfiable (substrate-enforced).**

- **`classification_scheme`** — an ordered sensitivity lattice (e.g. `Public < Internal < Confidential < Restricted`) plus open-vocab handling tags, **orthogonal to** but *carried on* `content_class` ([CC 3.3](part_3_the_namespace.md), open vocabulary — extended here with institutional values: `phi`, `psychotherapy_notes`, `sud_42cfr2`, `genetic`, `minor_adolescent`, `privileged`, `work_product`, `cui`, `itar`, `ear`, `trade_secret`, `provenance`, `accession`, `culturally_restricted`, `member_economic_standing`, `governance_visible`, …). Each class entry binds: `crypto_tier`, `retention`, `disclosure_bar`, `erasure_exempt`, `external_controller`, and optional `compartment`. Default scheme: one `internal` class.
- **`retention_policy`** — a **per-class** matrix, not one cohort-wide rate. Each class declares a **floor** (`retain_minimum` / `permanent` — *must-NOT-delete-before-N*), a **ceiling** (`delete_after` — GDPR-style delete-by), an optional `minor_age_of_majority_offset`, and `legal_basis`. The default class rides the [CC 6.1.2](part_6_the_coherence_mathematics.md) monotonic-descent noise floor unchanged (the free zero-config posture). A floor is the **inverse of descent**: it pins a class **above** the noise floor against capacity/aging pressure — the operator the seed lacked, expressed as a declared modifier *to* the [CC 6.1.2](part_6_the_coherence_mathematics.md) retirement operator, not a new primitive. `archive_mode: retain` ([CC 3.3](part_3_the_namespace.md)) is the default whenever any class declares a floor.
- **`legal_hold`** — a descent-**suspending freeze**: `{hold_id, issuer (accountable human / court — [CC 3.2](part_3_the_namespace.md)), scope (subjects/records/compartment), basis, tamper-evident, indefinite}`. While set it **overrides both** the retention schedule **and** consent-driven descent, pinning named records above the noise floor; `hard_case:legal_hold_set` / `:lifted` / `:violation_attempt` make set, lift, and any deletion-during-hold observable (spoliation is liability). Default: none.
- **`erasure_policy`** — declares which classes are **non-erasable during retention**, so a right-to-be-forgotten / N5 signal is **refused-with-reason** rather than honored (GDPR Art 17(3)(b)/(c)/(d) legal-obligation / public-interest-archiving exemptions). This is the **declared gate on [CC 6.1.5](part_6_the_coherence_mathematics.md) N5**: absent the gate, N5/withdrawal forces content below the floor as today; with it, a lawful-basis class lawfully resists. Erasure remains the default for unflagged classes (e.g. donor/marketing PII alongside permanent provenance in the same museum).
- **`disclosure_posture`** — `privacy-seeking` (default; whole cohort under the CommunityDek) **or** `transparency-seeking` (per-class **promotion to Commons/plaintext** for legally-public records — FOIA bodies, 501(c)(3) Form 990, published collections, GA/SC documents). This **generalizes the existing `infrastructure` plaintext exception** ([CC 4.4.3.2.1](part_4_composition_governance.md)) from whole-cohort to per-class, letting one affiliation simultaneously hold Commons-public and Community-encrypted classes.

**B. Compartments + access — OPTIONAL (sub-roster granularity).**

- **`compartments[]`** — named need-to-know sub-cohorts *within* the affiliation, membership ⊆ roster, **each with its own DEK** — the [CC 4.4.3.2.1](part_4_composition_governance.md) epoch-DEK cascade applied recursively (*a compartment is a stream a subset of members subscribe to*). Each carries explicit **per-member EXCLUSIONS** (deny-list) so a member high in the hierarchy can be cryptographically walled out (ethical walls / conflict screens; NAGPRA culturally-restricted records gated to external tribal designees and hidden **even from ordinary members** — which the flat all-members-read DEK cannot express). This is the single most load-bearing addition and is **the same machinery at finer scope**, not a new primitive.
- **`member_attributes`** — per-member `{nationality/us_person, clearance, credential + expiry, …}` consumed by compartment gating: deemed-export (ITAR/EAR exclude foreign-person members), MAC clearance (a Confidential-cleared member MUST NOT decrypt Secret), credential-expiry auto-descope (lapsed clinical license → automatic exclusion).
- **`access_control_model`** — `roster-wide` (default; the DEK cascade) | `rbac` (role→(class,compartment)) | `minimum-necessary` (treatment-/matter-relationship binding + audited **break-the-glass**). Honors HIPAA §164.502(b) minimum-necessary and the law-firm/bank/intel chinese-wall pattern.
- **`data_subject_access_grant`** — a scoped read+portability path to a **non-member** data subject (patient, client, student) over **their own** records, via a `delegates_to`/key-grant scoped grant **without conferring membership** (Cures Act, GDPR Art 15, FERPA rights-transfer-on-enrollment). Resolves the "the subject owns the data but is outside the roster" gap. Default: none.
- **`archive_custody`** — an institutional archive-key **custodian/escrow** role holding per-epoch archive keys **decoupled from the live roster**, so `permanent`/`retain` records survive member turnover. Resolves the forward-secrecy-vs-permanence collision ([CC 4.4.3.2.2](part_4_composition_governance.md) DEK rotation on removal would otherwise render a treaty-inviolable permanent archive unreadable). Rides the key-grant/escrow cascade. Default: none.
- **`chain_of_custody`** — an append-only, **gap-marked** provenance chain per accessioned object / matter / lot (museum provenance with the legally-significant 1933–45 gap; product-liability lot traceability). Rides `supersedes` + `holds_bytes:*`. Default: none.

**C. Hierarchy + designated officials — OPTIONAL.**

- **`hierarchy`** — reporting/authority roles over `delegates_to` ([CC 2.4.1](part_2_the_grammar.md)), generalizing the [CC 4.5.13](part_4_composition_governance.md) steward/moderator tiers. Supports **term-bound** authority (`delegation_valid_until` for annually-elected officers), **multi-parent DAG** roles (a grad student under PI + chair + registrar at once), a **configurable depth cap** (> the [CC 4.1.1](part_4_composition_governance.md) default-5 for deep secretariats), and **per-compartment/per-matter** roles (responsible attorney, conflicts counsel, PI). Authority roots in **accountable humans** ([CC 3.2](part_3_the_namespace.md)) **or**, for a collective principal (member-state assembly, kibbutz *asefa*), in the **`consensus_protocol` body** — no single human sovereign required. An `independent_branch` flag marks oversight bodies (OIOS, Ethics, IG) **exempt from the chain's read/control authority**, and `hierarchy` may **nest federated sub-affiliations** (autonomous specialized agencies). Default: flat.
- **`designated_officials`** — named accountable-human roots gating specific operations (Privacy + Security Officer / Controller-DPO at SI ≥ 0.6 per [CC 8.8.9](part_8_appendices.md) Annex I; Records Officer; FOIA Officer; Original Classification Authority; archive custodian; conflicts counsel). Mandatory at federal/regulated scale, **waivable below threshold** (a town clerk has none). Default: none.

**D. Lawful-access, transparency, accountability — OPTIONAL, NEVER covert.**

- **`lawful_access`** — DECLARED, scope-bounded **to the declaring affiliation only**, always logged as `hard_case:*`, transparency-reportable, and **NEVER a covert backdoor** — it does not touch anonymity-by-default ([CC 1.13.3.4](part_1_foundation.md)) or no-client-side-scanning ([CC 4.5.7](part_4_composition_governance.md)) anywhere else. Each authority declares a **type** — `surveillance/interception` | `records_production` (subpoena/discovery) | `regulator_inspection` (named auditor: DDTC/BIS/OSHA/Registrar) | `mandated_reporting` (scheduled outbound: communicable-disease, vital stats) — a `statutory_basis`, a **per-authority `transparency_mode`** `{immediate | delayed | aggregate_banded | sealed_cleared_audit}` (so a FISA/NSL gag complies via USA-FREEDOM-style aggregate banding rather than unlawful real-time emission), and optional **carve-out compartments** lawful access cannot reach (NIH Certificate-of-Confidentiality research, IRB, attorney-client privilege, academic-freedom). A `none/immune` value expresses **resistance-to / immunity-from** access as a first-class posture (privilege assertion via external judicial review; privileges-and-immunities of an IGO). Default: OFF.
- **`transparency_obligations[]`** — affirmative **proactive-disclosure** duties (FOIA reading-room, IRS Form 990 public inspection, NAGPRA inventories → NPS), **DECOUPLED** from `lawful_access` — transparency here is a *duty to publish*, not an *access concession*. Default: none.
- **`disclosure_accounting`** — a **per-data-subject** disclosure ledger (HIPAA §164.528), retrievable **by that subject**, distinct from the aggregate transparency report. Default: none.
- **`breach_notification`** — detection→notify config tied to DEK / unauthorized-access compromise: SLA and notifier identity (e.g. ≤60-day HHS + individual, media ≥ 500). Default: none.
- **`processor_chain` / `baa`** — declared sub-processors and **affiliation-to-affiliation** sharing/referral boundary, with `marking_binds_to_record` so a class's classification + export marking + retention obligation **travel across the cohort boundary** (OEM→Tier-1 supply chain; HIE referral). Default: none.

**Minors (the PTA / EdTech tie-in).** Where records bear minor `subject_key_ids`, set **`minor_data_handling`**: such records REQUIRE a **live guardian consent chain** — `delegates_to(parent → minor, scope: [consent_revocation/share])` — per the **minor-stewardship rule** (part_3 minor-stewardship clause) and the FERPA/COPPA hook (Annex I rows, [CC 8.8.9](part_8_appendices.md)). This is **minor-as-data-subject** (guardian consent over records about a child), distinct from **minor-as-member** (the operating-identity stewardship clause); both ride `delegates_to` with no new primitive. Note FERPA rights **transfer to the adult student at postsecondary enrollment** — model the institution as records **custodian** with the subject retaining rights (`external_controller` + `data_subject_access_grant`), not as parent→minor stewardship.

**Lifecycle.** **`dissolves_at` / `sunset`** gives ephemeral institutions a first-class auto-wind-down (holiday committee → purge + dissolve after the event), riding `supersedes`/`withdraws` so a casual group leaves no zombie cohort or un-purged data. **`internal_normative_regime`** optionally references bylaws / *takanon* / halachic order — an internal normative order that is neither external statute nor corporate hierarchy.

**Regulatory anchoring.** `regulatory_profile` and `jurisdiction[]` are **open lists** (not a closed HIPAA/SOX/FISA enum): values load the relevant **Annex I §3.2 sector overlay** and **Annex C cross-walk** ([CC 8.8.5](part_8_appendices.md) / [CC 8.8.9](part_8_appendices.md)) and supply defaults — and equally admit `self-regulated/cooperative-light` (kibbutz under a Registrar) and `treaty / customary-IL / privileges-and-immunities` (IGO, largely exempt from the national statutes Annex I enumerates). The SI ≥ 0.6 Controller rule ([CC 8.8.9](part_8_appendices.md)) selects the accountable authority.

**Instantiation — smallest vs largest, same fields:**

| Field | Holiday-party committee (`informal_adhoc`) | UN / IGO (`igo`) |
|---|---|---|
| `membership_basis` | `role-assigned` (workplace); a purely-social one needs no affiliation → plain `community` | `employment-contract` + `ascriptive` (member-state principal) |
| `regulatory_profile` | `[]` (none) | `["P&I-Convention-1946-Art.II§4","UN-PDP-2018","ST/SGB/2007/6"]` |
| `classification_scheme` | default single `internal` | `Unclassified < Confidential < Strictly-Confidential` + caveats |
| `retention_policy` | `rotate-forward` (noise-floor default) | per-series: `permanent` (archival) + scheduled (ARMS) + floors |
| `legal_hold` | — | litigation-hold freeze, role-gated lift |
| `disclosure_posture` | `privacy-seeking` | mixed: `transparency-seeking` for GA/SC docs, encrypted for ops |
| `compartments[]` | — | peacekeeping / OIOS / source-protected, member-excluding |
| `archive_custody` | — | institutional custodian decoupled from rotating staff |
| `hierarchy` | omitted (flat) | deep DAG, collective-`consensus_protocol` root, `independent_branch` oversight, nested agencies |
| `lawful_access` | omitted | `none/immune` (inviolable archives) + scoped internal OIOS |
| `transparency_obligations[]` | — | affirmative publication of designated classes |
| `dissolves_at` | event date + short TTL | — (perpetual) |

(The regulated middle — hospital, law firm, university, manufacturer, government body, museum, PTA — instantiates the *same* fields at intermediate settings: a solo clinic resolves the whole matrix from `affiliation_archetype: healthcare_provider` + `regulatory_profile: ["HIPAA"]`; a hospital overrides into per-class floors, compartments, disclosure accounting, breach notification, and BAA chain.)

**Why this is still 1+4.** One `cohort_scope` value (`affiliations`) + one declared config record riding existing machinery: classification on `content_class` (open vocab, [CC 3.3](part_3_the_namespace.md)); retention floors/holds/erasure-gates as declared modifiers to the [CC 6.1.2](part_6_the_coherence_mathematics.md) retirement operator and the [CC 6.1.5](part_6_the_coherence_mathematics.md) N5 rule; compartments + archive custody as the [CC 4.4.3.2.1](part_4_composition_governance.md) DEK / key-grant cascade at sub-roster granularity; hierarchy + designated officials on `delegates_to` ([CC 2.4.1](part_2_the_grammar.md)) and `consensus_protocol`; lawful-access/transparency as `hard_case:*` events; minor handling on the minor-stewardship `delegates_to` rule. The mandatory limbs default to a no-op so the floor stays low; the optional limbs stay absent until declared so the ceiling stays high. No new structural primitive.

#### 4.4.3.3 `policy` — Policy H — Tiered-Scope Composition (LIVE)

Per CIRISNodeCore three-tier interface model. Three feed-shape composition idioms that read attestations by `cohort_scope`:

| Feed | `cohort_scope` filter | Trust composition |
|---|---|---|
| **local_feed** | `self` only; steward-filtered | self-attested only; no peer weighting; consumer's own attestation graph subset |
| **community_feed** | `{family, community, affiliations}` | cohort-weighted; expertise WITHIN cohort matters; cross-cohort attestations downweighted unless explicitly invited |
| **global_feed** | `{species, biosphere, federation}` | full federation expertise weighting; fact-checkers (`encyclopedia:*` editors, `news:*` fact-check attestations) carry weight; [CC 4.4.1](#83-frickerian-discipline--consumer-policy-norms) Frickerian discipline applied |

**Composition with [CC 3.3](part_3_the_namespace.md) sub_kinds**: each NodeCore `external_content` sub_kind (`encyclopedia_article`, `news_article`, `accord_data`, `local_data`) composes naturally across these tiers because all four use the same envelope shape. A `local_data` Contribution starts at `cohort_scope: self` and SHOULD only appear in `local_feed`; promotion to community/global widens `cohort_scope` via the `supersedes` structural primitive (see CC 4.4.3.3.1 below).

##### 4.4.3.3.1 `supersedes` — Promotion via `supersedes` (worked pattern)

A Contribution's `cohort_scope` MAY be widened (promoted) by emitting a `supersedes` against the prior attestation with:

- `references_attestation_id` = the prior attestation's id
- `differs_in: ["cohort_scope", "sub_kind?"]` — naming what changed
- new attestation envelope reuses the prior `content_sha256` (no body re-upload)
- new `cohort_scope` is wider (e.g., `self` → `community` or `community` → `global`)
- optionally morph `sub_kind` (e.g., `local_data` → `encyclopedia_article` for "promote my private note to a published encyclopedia entry")

This pattern is wire-format-clean: it re-uses the structural primitive `supersedes` rather than introducing a `promote` primitive. The chain is walkable via `references_attestation_id` so the promotion lineage is preserved.

#### 4.4.3.4 `family-policy` — Policy L — Self/family membership composition

Per [CC 3.3.6](part_3_the_namespace.md) `identity_occurrence` + [CC 3.3.4](part_3_the_namespace.md) `family` + [CC 5.2](part_5_transport_substrate.md) structural-invisibility. Composition pattern for resolving the **current membership set** of an identity's self-collective OR a family, gating the at-rest encryption flow that wraps DEKs to admitted members.

Reads as: "for any `cohort_scope: self | family` Contribution, the substrate computes the current member set by walking the latest `identity_occurrence` / `family` Contributions and resolves which keys MUST receive a `key_grant` wrap of the content DEK."

##### 4.4.3.4.1 `cascade` — Key-grant cascade (the at-rest encryption flow)

On admission of a new `identity_occurrence` OR a `family` membership-add, substrate emits retroactive `key_grant`s wrapping all extant `cohort_scope: self|family` content DEKs to the new member's key:

```
on_member_added(scope_target, new_member_key):
 for each Contribution C in federation_attestations where:
 C.cohort_scope == "self" AND C.attesting_key_id ∈ resolve_self(scope_target)
 OR
 C.cohort_scope == "family" AND C.family_id == scope_target
 AND C is still substrate-admitted (not withdrawn / not expired):
 emit key_grant {
 wrap_algorithm: X25519MlKem768Aes256GcmHkdfSha256, // v2 — see PQC note
 recipient_key_id: new_member_key,
 content_sha256: C.evidence_refs[0].sha256,
 scope: GroupMember,
 wrapped_dek: wrap(C.dek, new_member_key.pubkey),...
 }
```

**PQC at rest — `wrap_algorithm: v2` MANDATORY (normative).** The self/family at-rest DEK MUST be wrapped with **`wrap_algorithm: v2` = `x25519_mlkem768_aes256_gcm_hkdf_sha256`** (hybrid X25519+ML-KEM-768; the [CC 3.3.2](part_3_the_namespace.md) variant `X25519MlKem768Aes256GcmHkdfSha256`), **never v1** (X25519-only). Self/family content is the user's most private and longest-lived data (memory, photos, identity, the [CC 4.4.3.4.3](#81127-the-self-at-login--app--agent-co-self--partnered-delegation-ceg-015-normative-composition) Self DEK) — a classical-only KEM is a harvest-now-decrypt-later exposure, the identical mandate as the streaming epoch DEK ([CC 5.1](part_5_transport_substrate.md)). The AES-256-GCM content seal is symmetric (PQC-safe); the wrap signature is hybrid Ed25519+ML-DSA-65. A Consumer MUST reject a self/family at-rest grant carrying `wrap_algorithm: v1`.

The cascade is the wire-format primitive for the "I got a new phone and want my Twitter history" + "I added Carol to the household for a week" flows. Operator policy MAY bound the cascade depth (e.g., last 90 days of self-content; opt-in for the full historical wrap).

##### 4.4.3.4.2 `admission-membership` — Membership-change admission per consensus_protocol

A proposed membership change (addition OR removal) rides a `supersedes` Contribution on the family's latest admitted `family` Contribution. Substrate admission gate evaluates the CURRENT family's `consensus_protocol` against the signatures on the proposal:

```
admit_family_change(F, proposed: family_record):
 current = resolve_family(F, now)
 protocol = current_family_record(F).consensus_protocol
 signatures = collect_signatures_on(proposed)

 match protocol:
 "founder_only":
 return any sig from m where m.role == "founder" in current
 "unanimous":
 return every m.key_id in current has signed
 "majority":
 return count(sig from m in current) > len(current) / 2
 "quorum:M/N":
 return count(sig from m in current) >= M // M is ABSOLUTE — see §8.1.12.3.1
 "weighted:{rubric}":
 return sum(weight(m, rubric) for m in current who signed) >= threshold
 "custom:{family_id}":
 return operator-defined predicate evaluates to true

 if admit:
 emit hard_case:family_membership_change:{F}
 trigger §8.1.12.4 key_grant cascade
 else:
 hold in pending state (per operator-policy window) OR
 emit hard_case:family_consensus_protocol_violation:{F} and reject
```

**Consensus-protocol amendment** (changing `consensus_protocol` itself on a non-entrenched family) rides the SAME admission rule on the proposed amendment Contribution — meta-amendment shape parallel to [CC 4.5.1.2](part_4_composition_governance.md). Entrenched families (`consensus_protocol_entrenched == true`) reject amendments at the substrate gate; replacement requires the out-of-band ceremony documented per family (for HUMANITY_ACCORD see [CC 4.2.1](part_4_composition_governance.md)).

###### 4.4.3.4.2.1 `quorum-absolute` — `quorum:M/N` is absolute-M (normative)

The `M` in `quorum:M/N` is an **absolute signature count**, NOT a fraction that rebases with roster size. A `quorum:2/3` collective that grows to 5 members still admits at **2** signatures; the `N` is documentary (records the roster size at protocol-adoption time) and is NOT recomputed against the live roster. The ceremony gate requires a deterministic, operator-independent reading, so absolute-`M` is pinned.

**Rationale**: absolute-`M` is the simpler invariant (the gate is a pure `count >= M` with no live-roster division), it matches NodeCore's shipped `evaluate_consensus_protocol` so the single shared predicate needs no change, and proportional/rebasing quorum is still expressible for operators who want it via `weighted:{rubric}` (assign each member weight 1, set threshold = `ceil(roster_size / 2)` recomputed by the rubric resolver). Collectives that want "M grows with the roster" therefore use `weighted:`, not `quorum:` — keeping `quorum:M/N` unambiguous.

This rule applies identically to `community` admission ([CC 4.4.3.2.3](#81132-community-admission-per-consensus_protocol-cohort_subkind-dispatch)) — the `quorum:M/N` arm there is the same absolute-`M` reading.

##### 4.4.3.4.3 `cohort` — The "Self at login" — app + agent co-self + partnered delegation (normative composition)

The canonical user-identity composition: a person's **app** (the KMP client key) and their **agent** (CIRISAgent's local key) are two occurrences of one user identity that share one **Self DEK**, and at login the agent is **partnered + delegated** to act as the user on the network. **No new structural primitive** — this composes `identity_occurrence` + Policy L + `consent:partnered` + `delegates_to` + `identity_type`-set + `transport_destination`. The four implementations MUST follow this shape so a "Self" is identical everywhere.

**The Self (membership).** One **user `identity_key`**: hybrid Ed25519+ML-DSA-65 ([CC 5.3.1](part_5_transport_substrate.md)), hardware-rooted ([CC 4.2.2](part_4_composition_governance.md); WebAuthn/passkey is the *presence/unlock factor*, not the key), with `identity_type ⊇ {user}` — and `⊇ {user, wise_authority}` when the user is also a WA ([CC 3.4.7.1](part_3_the_namespace.md) set-membership; one key, two roles). Its occurrences ([CC 3.3.6](part_3_the_namespace.md)): the **app** (`device_class: phone|laptop`) and the **agent** (`device_class: agent`), co-admitted at login by single-vouch (the user key admits the agent occurrence). Both receive the **Self DEK** via the [CC 4.4.3.4.1](#81124-key-grant-cascade-the-at-rest-encryption-flow) Policy-L cascade — every `cohort_scope: self` Contribution's DEK wraps to both, so **the app and the agent decrypt the same Self content** (memory / config / consent / identity). That shared cascade *is* the "single Self key."

**Two layers — and they are independently revocable (the load-bearing distinction):**

| Layer | Mechanism | Buys | Revoked by |
|---|---|---|---|
| **Co-self** (visibility) | occurrence + Policy-L Self DEK | the agent can *read/manage the user's Self* (decrypts self-content) | `withdraws` the occurrence → Option-A re-key ([CC 4.4.3.4.5](#81125-forward-secrecy-on-member-removal-option-a-recommended-for-v1)) |
| **Agency** (act-on-behalf) | `consent:partnered` + scoped `delegates_to` | the app may *act AS the user on the network* (send/receive, presence, sub-delegate) | `withdraws` the delegation → agency ends, **co-self unaffected** |

So a user MAY grant a device co-self (it manages their data locally) while revoking its network agency — or vice-versa — without disturbing the other.

**Agency at login (the partnering + delegation).**
1. **Partnering** — the user emits `consent:partnership_grant` and the agent occurrence emits `consent:partnership_accept` under one `bilateral_pair_id` ([CC 4.4.3.5.3](#81114-bilateral-partnered-pair) PARTNERED); the bilateral pair is the persistent, auditable relationship.
2. **Delegation** — the user identity emits `delegates_to` against the **agent occurrence key**, with `delegated_scope` drawn from the canonical act-on-behalf kinds below, `delegation_purpose: "act_as_user"`, bounded `delegation_valid_until`. Sub-delegation works because `delegates_to` chains.
3. **This grant is FEDERATION-tier ([CC 5.3.2.4](part_5_transport_substrate.md)), not local** — *other peers must verify the agent's authority before honoring its messages/presence*, so the partnering+delegation is signed + promoted at login. **Promotion is the "app shows up on the network" moment.** (The agent's own self-content stays local-tier; only the act-on-behalf authorization federates.)

**Canonical `delegated_scope` kinds for act-on-behalf**:

| scope | grants the agent |
|---|---|
| `act_on_behalf` | umbrella: emit Contributions AS the user |
| `message_io` | send + receive directed messages on the user's behalf |
| `network_presence` | announce/resolve the user's `transport_destination` ([CC 3.3.6.2](part_3_the_namespace.md)) — be reachable AS the user |
| `sub_delegation` | issue further `delegates_to` within the granted scope (depth-capped) |

**Moderation duties — `moderate` / `takedown` / `review`.** Moderation is a **delegable *duty*, not a platform/fabric-assigned role**: a participant exercises it *as themselves*, or delegates it — to **their agent** (AI on-behalf-of) or to **any trusted party** (a human, a community moderator) — via `delegates_to`. These three kinds carry **enforced admission** (unlike the *recommended* act-on-behalf kinds above), mirroring `consent_revocation` ([CC 2.4.1.1](part_2_the_grammar.md) rule 3):

| scope | authorizes the delegate to emit, on the delegator's behalf | shipped primitive |
|---|---|---|
| `moderate` | a `moderation:{allegation_type}` ModerationEvent + the report→`scores` path + `age_assurance:*`/`content_class:*` gates | [CC 3.1.9.2](part_3_the_namespace.md) / [CC 4.4.3.10](part_4_composition_governance.md) |
| `takedown` | a `takedown_notice` (incl. the CC 4.5.3 immediate-removal fast-path) | [CC 3.3.2](part_3_the_namespace.md) / [CC 4.5.3](part_4_composition_governance.md) |
| `review` | a `reconsideration:{grounds}` appeal / review | [CC 3.1.9.2](part_3_the_namespace.md) |

**Enforced-admission rule (normative):** a moderation action above is admitted **iff** its `attesting_key_id` is the delegator itself **or** sits on a live `delegates_to` chain bearing the matching scope from the delegator (the entity holding the duty over the target content/scope) — exactly the CC 2.4.1.1 rule-(3) proxy shape (`scope ⊇ {moderate|takedown|review}`), depth-capped per [CC 4.1.1](part_4_composition_governance.md), revocable by `withdraws` against the `delegates_to`. **Reject otherwise.** Every action is therefore delegate-signed, delegator-traceable up the chain, and revocable — the [CC 4.5.3](part_4_composition_governance.md) **"takedown-isn't-a-coup"** property made *structural* (coordinated + attributable + revocable, never a unilateral seizure). See [CC 4.5.5](part_4_composition_governance.md). **1+4 preserved** — a `delegated_scope` vocabulary + enforcement addition over the existing `delegates_to`; the action primitives already ship; no new structural primitive.

**Partnership WITHOUT agency — the infrastructure delegation profile.** The flow above binds an **agent** (a key with a brain) to a user as partnership **+ agency** — the scope includes `act_on_behalf` / `message_io`, so the agent reasons and acts AS the user. A **fabric/infrastructure node** ([CC 3.4.7.1](part_3_the_namespace.md); CIRISServer) needs the *partnership* (identity + the [CC 3.2](part_3_the_namespace.md) steward-binding that lets it hold non-infra membership standing under the user's authority) but MUST NOT receive agency — [CC 1.13.5](part_1_foundation.md) "infrastructure must not have agency." CEG pins a **reserved two-prefix scope split** so a verifier can enforce this cryptographically:

| prefix | class | scopes |
|---|---|---|
| `infra:*` | server-class (allowed for a `node`-role delegate) | `infra:network_presence`, `infra:join_communities`, `infra:serve`, `infra:store`, `infra:attest`, `infra:transport` |
| `agency:*` | brain-only (forbidden for a pure `node`-role delegate) | `agency:act_on_behalf`, `agency:message_io`, `agency:reason`, `agency:decide` |

**Conformance:** a `delegates_to` whose `attested_key_id` resolves to an identity whose `identity_type` ([CC 3.4.7.1](part_3_the_namespace.md)) is `node`-only (no `agent`/brain) MUST carry **only** `infra:*` scopes; a verifier MUST **reject** (treat as non-conformant, never grant) an `infra`-only key presenting any `agency:*` scope. This makes CC 1.13.5 a wire-checkable invariant: a user-owned fabric node can serve + hold group-membership *standing* under the user's authority, but the delegation **literally cannot carry agency**. The legacy unprefixed kinds above remain valid for `agent`-role delegates (the Self-at-login agency profile) and are the `agency:*` / `infra:network_presence` equivalents; new **infra** delegations SHOULD use the explicit `infra:*` prefixes.

**Cohabitation (`agent = node + brain`):** when both compose in one process, the node holds **partnership-without-agency** (`infra:*` — identity + membership standing) and the brain layers **Self-at-login partnership-with-agency** (`agency:*` — reasoning) as a *separate* `delegates_to`. Two delegations, two scope classes, independently revocable — the user can strip the brain's agency while the fabric node keeps serving.

**Transport (network presence) — AV-17.** Each occurrence binds a `transport_destination` ([CC 3.3.6.2](part_3_the_namespace.md)); the app is reachable on RET *as the user occurrence*. The Reticulum destination is a **separate dual-key transport identity** that the user's signing key *authorizes by signing the binding* — the federation signing seed MUST NOT enter the transport layer. "User key used as a transport key" means *roots/authorizes* the transport identity, not a shared keypair.

**Worked login flow.** (1) unlock the hardware-rooted user key (WebAuthn presence) → (2) admit the agent occurrence (single-vouch) → Policy-L Self DEK now wraps to both → (3) optionally add the `wise_authority` role to the user's `identity_type` set → (4) bind each occurrence's `transport_destination` → (5) `consent:partnership_grant`/`accept` under a `bilateral_pair_id` → (6) `delegates_to(user → agent occurrence, scope: [act_on_behalf, message_io, network_presence, sub_delegation])`, **promoted to federation-tier**. The app now reads the user's Self locally AND acts as the user on the network; the user can revoke either layer independently.

###### 4.4.3.4.3.1 `canonicalization-signing` — Signing member sets (normative — the JCS contract Verify hybrid-signs)

Each of the three Self-at-login Contributions is hybrid-signed over `JCS(envelope)` ([CC 2.6.1](part_2_the_grammar.md) / RFC 8785), and at login promoted to federation-tier (the [CC 5.3.2.4.2](part_5_transport_substrate.md) promotion canonicalizes the **exact committed member set** — omit-vs-materialize ([CC 2.6.1.1](part_2_the_grammar.md)) is load-bearing; the signer MUST NOT re-default). **The [CC 2.6.1.1.1](part_2_the_grammar.md) determinism rules apply**: `subject_key_ids[]` and `delegated_scope[]` are **lexicographically sorted** (set-semantics); `aspects[]` retains RNS order (sequence-semantics); all key/hash/pubkey byte fields (`*_key_id`, `subject_key_ids[]`, the two reticulum pubkeys, `destination_hash`) are **lowercase hex per [CC 2.6.3](part_2_the_grammar.md)**; all timestamps are **[CC 2.6.2](part_2_the_grammar.md)-canonical**. The member sets the producer commits (and which `JCS` therefore covers) are pinned below. Optional [CC 2.1](part_2_the_grammar.md) envelope fields not listed ride the CC 2.6.1.1 omit rule (absent unless the producer sets them).

**(a) `consent:partnership_grant:v1` (user side) / `consent:partnership_accept:v1` (agent side)** — bare `scores` ([CC 3.3.1](part_3_the_namespace.md)) bound by `bilateral_pair_id`:
```
{ attestation_type: "scores",
 attesting_key_id: <user identity_key_id (grant) | agent occurrence_key_id (accept)>,
 dimension: "consent:partnership_grant:v1" | "consent:partnership_accept:v1",
 score: <positive>,
 subject_key_ids: [<the partner key: agent occurrence (grant) | user identity (accept)>],
 bilateral_pair_id:<shared pair id>, // §8.1.11.4 binding mechanism
 signed_at: <rfc3339_canonical> }
```
> **Version segment pinned.** The dimension carries the `:v1` version segment — `consent:partnership_grant:v1` / `consent:partnership_accept:v1` — to satisfy the [CC 4.1.3](part_4_composition_governance.md) `scores` version-segment gate. The `:v1` is the partnership-ceremony schema version (bump to `:v2` only if the bilateral shape changes); the shared `bilateral_pair_id` remains the CC 4.4.3.5.3 binding mechanism.

**Canonical signed member set for the two `:v1` envelopes.** Both impls MUST canonicalize (and thus hybrid-sign) **exactly** this member set, or the JCS bytes — and the signatures — diverge. The set is the [CC 3.3.1](part_3_the_namespace.md) bare-`scores` shape; these seven members are **REQUIRED** (present in the JCS for both `grant` and `accept`):

| Member | Value | Verify#63 name |
|---|---|---|
| `attestation_type` | literal `"scores"` | — |
| `attesting_key_id` | **the signer** = `granter_key_id` (grant) / `accepter_key_id` (accept); the bound sig binds because signer ≡ `attesting_key_id` | `granter_key_id` / `accepter_key_id` |
| `dimension` | literal `"consent:partnership_grant:v1"` \| `"consent:partnership_accept:v1"` | `envelope_type` |
| `score` | positive (the affirmation) | — |
| `subject_key_ids` | **exactly `[partner_key_id]`** — the OTHER party (agent occurrence for `grant`, user identity for `accept`); single-element, [CC 2.6.1.1.1](part_2_the_grammar.md) set-sort is trivial | `partner_key_id` |
| `bilateral_pair_id` | the shared join ([CC 4.4.3.5.3](#81114-bilateral-partnered-pair)) — identical string on both halves | `bilateral_pair_id` |
| `signed_at` | [CC 2.6.2](part_2_the_grammar.md)-canonical RFC 3339 | `timestamp` |

**Mapping (so the two impls agree on naming):** `granter`/`accepter` ≡ `attesting_key_id` (the signer of that half); `partner` ≡ `subject_key_ids[0]`. **No `valid_until`** — a PARTNERED pair has no expiry ([CC 4.4.3.5.3](#81114-bilateral-partnered-pair)); the field is **omitted** (NOT materialized as `null`), per the [CC 2.6.1.1](part_2_the_grammar.md) omit rule. **All other [CC 2.1](part_2_the_grammar.md) envelope fields ride the omit rule** — absent from the JCS unless the producer explicitly sets them; the signer MUST NOT re-default. Additional canonical members are a `:v2` bump, never a silent `:v1` addition. Byte-field members (`attesting_key_id`, `subject_key_ids[]`) are lowercase-hex per [CC 2.6.3](part_2_the_grammar.md).

**(b) `delegates_to` (user → agent occurrence)** — the act-on-behalf grant ([CC 2.4.1](part_2_the_grammar.md) envelope shape):
```
{ attestation_type: "delegates_to",
 attesting_key_id: <user identity_key_id>,
 attested_key_id: <agent occurrence_key_id>, // the delegate
 delegated_scope: ["act_on_behalf",...], // §8.1.12.7 canonical kinds
 delegation_purpose: "act_as_user",
 delegation_valid_from:<rfc3339_canonical>,
 delegation_valid_until:<rfc3339_canonical>,
 signed_at: <rfc3339_canonical> }
```

**(c) `transport_destination` binding** — an `identity_occurrence` ([CC 3.3.6](part_3_the_namespace.md) / [CC 3.3.6.2](part_3_the_namespace.md)) carrying the binding; signed by `identity_key_id` (or a current occurrence), AV-17:
```
{ attestation_type: "scores",
 subject_kind: "identity_occurrence", // payload discriminator §4.2.2.3
 attesting_key_id: <user identity_key_id | a current occurrence>,
 identity_key_id: <user identity_key_id>,
 occurrence_key_id:<the occurrence being bound>,
 device_class: "phone" | "laptop" | "agent" |...,
 transport_destination: {
 reticulum_x25519_pubkey: <[u8;32]>,
 reticulum_ed25519_pubkey: <[u8;32]>,
 destination_hash: <[u8;16]>, // MUST derive per §5.6.8.8.1
 app_name: <string>,
 aspects: [<string>,...] }, // ordered
 asserted_at: <rfc3339_canonical>,
 signed_at: <rfc3339_canonical> }
```

Registry owns these member sets (this section); Verify computes `JCS(...)` + the hybrid Ed25519+ML-DSA-65 signature over each via `jcs::canonicalize`; the promotion signature ([CC 5.3.2.4.2](part_5_transport_substrate.md) OQ-4) is the identical JCS bytes.

**`encryption_pubkeys` joins member set (c).** When the occurrence carries the [CC 3.3.6.1](part_3_the_namespace.md) `encryption_pubkeys` field-set, both halves are **inside the signed JCS bytes** as opaque base64 strings (RFC 4648 STANDARD, padded — the [CC 2.6.1.1.1](part_2_the_grammar.md) rule-2 pin). Optional presence rides the CC 2.6.1.1 omit rule (absent unless the producer sets it; the signer MUST NOT re-default). They are payload, never verification material — neither half may be fed to a signature-verify path (the CC 3.3.6.1 key-separation rule, type-enforced in Verify).

##### 4.4.3.4.4 `family-membership` — Family membership resolution

For family `F`, the current member set is computed as:

```
resolve_family(F, now):
 latest = federation_attestations.where(subject_kind == "family").where(envelope.family_key_id == F).where(supersedes chain → latest non-superseded).where(admission rule satisfied per CURRENT consensus_protocol;
 see §8.1.12.3)
 return {m.key_id for m in latest.envelope.members}
```

Each `member.key_id` is itself an identity — the substrate does NOT walk into each member's `identity_occurrence` set at family-resolution time. When DEK wrapping happens, each member's identity_key receives a `key_grant`; the member's own substrate then composes Policy L on its own self-collective to propagate to that member's devices/agents (recursive composition).

**Concrete**: The Acme Household family has members `{alice_root, bob_root, roku_living_room, kitchen_tablet, nest_thermostat}`. When Alice's phone publishes a `cohort_scope: family` dinner photo with `family_id: acme-household`, the substrate wraps the DEK under each of those 5 identity keys. Alice's `alice_root` then re-wraps to her self-collective (phone, laptop, agent); Bob's `bob_root` re-wraps to his self-collective; the Roku and kitchen tablet receive directly (single-key identities — they don't have multi-occurrence sets); the Nest thermostat same.

##### 4.4.3.4.5 `forward-secrecy` — Forward secrecy on member removal (Option A, recommended for v1)

**Option A** — once shared, always shared at the wire layer:

```
on_member_removed(scope_target, removed_member_key):
 // The removed member retains existing key_grants — cannot retroactively un-share.
 // Substrate STOPS wrapping NEW key_grants to them on subsequent
 // cohort_scope: self|family Contributions for scope_target.
 // No DEK rotation; no re-encryption of historical content.
```

This is consistent with [CC 4.5.3](part_4_composition_governance.md) "takedown isn't a coup" + [CC 2.4.1](part_2_the_grammar.md) `withdraws-isn't-retroactive` semantics — historical state isn't retroactively re-keyed. Option B (rotate-DEK on removal) is deferred to a future `subject_kind: family_rotation` ceremony; the slot is documented and the rotation primitive left for a downstream-demand-driven release.

**Why Option A**: aligns with the substrate's existing forward-secrecy posture; matches user-intuition that "leaving the family" governs future content, not historical; bounded substrate cost (no re-wrap-all-content storm on member removal).

##### 4.4.3.4.6 `self-collective` — Self-collective resolution

For identity `I`, the current self-collective is computed as:

```
resolve_self(I, now):
 candidates = federation_attestations.where(subject_kind == "identity_occurrence").where(envelope.identity_key_id == I).where(supersedes chain → latest non-superseded).where(NOT withdrawn by I or by current occurrence).where(envelope.valid_until IS NULL OR > now)
 return {c.envelope.occurrence_key_id for c in candidates} ∪ {I}
```

The root `I` itself is implicitly a member (the identity_key is always an admissible signer for its own content). Single-vouch admission: any current occurrence (including `I` itself) may admit a new occurrence via `attesting_key_id` on a fresh `identity_occurrence` Contribution.

**Concrete**: Alice has admitted `alice_phone`, `alice_laptop`, `alice_agent`. Her self-collective is `{alice_root, alice_phone, alice_laptop, alice_agent}`. When Alice's phone publishes a `cohort_scope: self` Twitter scroll, the substrate wraps the content DEK under all four keys; the content reaches her laptop and agent via the at-rest encryption flow without emitting `holds_bytes:sha256:*`.

##### 4.4.3.4.7 `composition-subject` — Composition with subject_key_ids[]

`identity_occurrence` + `family` (membership / visibility scoping) compose cleanly with `subject_key_ids[]` (revocation authority):

- A `cohort_scope: family` Contribution naming `subject_key_ids: [user_canonical_hash]` is admitted at family visibility AND the named subject retains independent revocation authority per CC 4.4.3.5.
- A `cohort_scope: self` Contribution that Alice writes about Bob (Bob in `subject_key_ids`) stays in Alice's self-collective (Bob does NOT receive a key_grant unless Bob's identity is in Alice's self — which it isn't). Bob's subject-side revocation authority still composes: Bob CAN issue `withdraws` against Alice's Contribution; admission emits `hard_case:consent_sla_breach` clock-start if Alice committed `consent:deletion_sla`.

The orthogonality holds: **`cohort_scope` is producer-side visibility scoping**; **`identity_occurrence` + `family` are substrate-side membership primitives that gate at-rest DEK wrapping**; **`subject_key_ids` is subject-side revocation authority**. Three independent envelope-level concerns that compose without overlap.

#### 4.4.3.5 `policy-cem` — Policy K — CEM composition

Composition pattern for dual-authority Contributions where the subject is named via [CC 2.3](part_2_the_grammar.md) `subject_key_ids`, with consent state composed from the [CC 3.3.1](part_3_the_namespace.md) `consent:*` namespace family.

Reads as: "this Contribution names a subject whose consent state evolves over time; consumer policy resolves the effective consent verdict by walking the subject's latest non-superseded `consent:state:*` emission, gated by `valid_until`, and tracks producer deletion-SLA obligations on revocation."

##### 4.4.3.5.1 `composition-decay` — Decay-protocol stage composition (CIRISAgent CEM ANONYMOUS)

For consent_records carrying `decay_protocol: "ciris-agent-90day"` (or any named decay path):

```
decay_state(consent_record, now):
 elapsed = now - revocation_event(consent_record).asserted_at

 walk substrate emissions on dimension `consent:decay:*` against consent_record,
 matching the decay_protocol's stage map. CIRISAgent 90-day decay:

 elapsed < 30d → consent:decay:identity_severed (substrate emits at elapsed=0)
 30d ≤ elapsed < 60d → consent:decay:patterns_anonymized (substrate emits at elapsed=30d)
 60d ≤ elapsed < 90d → (in flight; no new stage emission)
 elapsed ≥ 90d → consent:decay:complete (substrate emits at elapsed=90d)
```

Per [CC 3.3.1](part_3_the_namespace.md) `consent:decay:{stage}` is open vocab. Other decay protocols MAY name other stage sequences; substrate honors the producer's published `decay_protocol` string and emits stages per the protocol's stage map.

##### 4.4.3.5.2 `deletion-sla` — Deletion-SLA watcher (substrate emission)

When subject `s` emits `consent:state:revoked` (or an admitted `withdraws`) against target `T`, substrate watches for producer compliance:

```
watch_sla(T, s, revocation_at):
 sla = T.attestations.where(attesting_key_id == T.attesting_key_id).where(dimension == "consent:deletion_sla:*").latest.extract_days

 if sla is None:
 return # no SLA commitment; no watcher

 deadline = revocation_at + sla.days
 completion = T.attestations.where(attesting_key_id == T.attesting_key_id).where(dimension == "consent:deletion_complete").where(asserted_at > revocation_at).first

 if now > deadline and completion is None:
 emit hard_case:consent_sla_breach against T
```

The `hard_case:*` emission is the **primitive observability signal**; per [CC 4.5.2](part_4_composition_governance.md) governance, LensCore composes derived detectors on top (`detection:consent:repeat_sla_breach`, etc.).

##### 4.4.3.5.3 `composition-bilateral` — Bilateral pair composition (PARTNERED ceremony)

For the bilateral partnership shape per [CC 3.3.5](part_3_the_namespace.md) `consent_record`:

```
ratified_pair(pair_id):
 subject_half = federation_attestations.where(subject_kind == "consent_record").where(envelope.bilateral_pair_id == pair_id).where(envelope.stance == "granted").where(envelope.subject_key_id == attesting_key_id) # subject signing for self.first

 producer_half = federation_attestations.where(subject_kind == "consent_record").where(envelope.bilateral_pair_id == pair_id).where(envelope.stance == "granted").where(envelope.target_key_id == subject_half.subject_key_id).where(attesting_key_id != subject_half.subject_key_id) # producer signing.first

 return subject_half AND producer_half # both required for ratification
```

`topical_relation:bilateral_pair` is the open-vocab edge documenting the pair linkage (recommended, not required for ratification — `bilateral_pair_id` is the binding mechanism).

##### 4.4.3.5.4 `multi-subject` — Multi-subject revocation (any-subject-binding)

When `len(T.subject_key_ids) > 1`, each subject is an **independent** revocation authority. A `withdraws` admitted under [CC 2.4.1.1 rule 2 or 3](part_2_the_grammar.md) from ANY single subject in `T.subject_key_ids` evicts the Contribution. Consumer policy MUST treat `T` as revoked from the perspective of all subjects (no "majority-rules" or "all-subjects-must-agree" softening) — this is the subject-as-individual principle from MISSION.md §1.5 applied at the subject-authority layer.

Concrete cases:
- Group photo with three subjects: any one subject revokes → the photo is evicted from federation propagation.
- Group chat export with N participants: any one participant revokes → the export is evicted.
- Multi-party contract: any one signatory revokes → the contract Contribution is evicted (separate from the legal-validity question, which is consumer-side; the substrate just removes the wire artifact).

Producers MAY mitigate by partitioning content into per-subject Contributions (e.g., one chat-message Contribution per author, linked via `topical_relation:replies_to`) so that one subject's revocation doesn't evict another's content.

> **No distinct multi-subject evict path — admission + precedence is sufficient.** Multi-subject eviction is fully expressed by two mechanisms already in the spec and needs **no new primitive, dimension, or `hard_case`**: (1) **admission** — the per-subject `withdraws` is admitted under [CC 2.4.1.1 rule 2/3](part_2_the_grammar.md) exactly as a single-subject `withdraws` is (each subject in `subject_key_ids` is independently a valid revoker; the rule does not change for `len > 1`); (2) **precedence** — the latest-wins / revoke-is-terminal precedence at the consumer read path ([CC 4.4.3.5.5](#81111-effective-consent-resolution-read-path)) applies per-subject, and any one subject's terminal `withdraws` evicts `T` for all (the any-subject-binding above). There is no quorum to compute and no "evict event" to materialize separately from the admitted `withdraws` — the withdrawal IS the evict. Substrates implement this as the OR over per-subject revocation state, not as a new code path.

##### 4.4.3.5.5 `consent-effective` — Effective consent resolution (read path)

For a target Contribution `T` carrying `subject_key_ids` of length ≥ 1, the effective consent state per subject `s ∈ T.subject_key_ids` is computed as:

```
resolve_consent(T, s, now):
 candidates = federation_attestations.where(target == T).where(attesting_key_id == s OR
 attesting_key_id ∈ delegates_to(s).proxies).where(dimension matches "consent:state:*").where(supersedes_id IS NULL OR replaced by latest in supersedes chain).where(valid_until IS NULL OR valid_until > now).order_by(asserted_at DESC)

 latest = first(candidates)
 return:
 granted if latest.dimension == "consent:state:granted"
 revoked if latest.dimension == "consent:state:revoked"
 expired if latest.dimension == "consent:state:expired" OR
 latest.valid_until passed without renewal
 unspecified if no candidates (subject named but never declared)
```

Substrate MAY cache the resolution per `(T, s)` keyed on the latest `asserted_at`; invalidate on any new `consent:*` write from `s` or `s`'s proxy chain.

##### 4.4.3.5.6 `policy-what` — What Policy K composes

| CIRISAgent CEM stream | Policy K composition |
|---|---|
| **TEMPORARY** (14d default) | `consent:state:granted` + envelope `valid_until = asserted_at + 14d` + auto-renew dimension on interaction (consumer-policy concern) |
| **PARTNERED** | Bilateral pair per CC 4.4.3.5.3: subject `consent:partnership_grant` + producer `consent:partnership_accept` under same `bilateral_pair_id`; no `valid_until` |
| **ANONYMOUS** | Revocation + decay-protocol per CC 4.4.3.5.1: substrate emits stage milestones; agent honors stage-appropriate processing constraints |

Per CEG's [CC 2.4 MISSION.md](../../MISSION.md) layering: CIRISAgent's three streams are a **named bundle** at the consumer-policy layer. Other agents MAY compose other streams over the same wire primitives. CEG documents the canonical bundle for ecosystem coordination; CEG does not lock the bundle.

#### 4.4.3.6 `policy-attestation` — Policy I — Attestation-Ladder Composition

The familiar L1-L5 verification "ladder" (self_verify → hardware_rooted → registry_consensus → license_validity → agent_integrity) is **consumer-side composition over the mechanism prefixes** in [CC 3.1.2](part_3_the_namespace.md), not a wire-level taxonomy.

Per [CC 1.2](part_1_foundation.md) T2 honestly applied: the L-number names a *ladder position* (a verdict-shape consumers compute), not a *mechanism* (which is what the wire MUST carry). Prefixes like `attestation:l3:registry_consensus` smuggle the verdict-shape into the prefix name, conflating the mechanism (registry consensus check) with the ladder slot (third rung). The wire separates them.

**Wire prefixes (mechanism)** [CC 3.1.2](part_3_the_namespace.md):

| Mechanism prefix | Ladder position (consumer-rendered) |
|---|---|
| `attestation:self_verify` | L1 |
| `attestation:hardware_rooted` | L2 |
| `attestation:registry_consensus` | L3 |
| `attestation:license_validity` | L4 |
| `attestation:agent_integrity` | L5 |

**Composition function** (reference implementation):

```
ladder_verdict(attestations) =
 let levels = []
 for prefix in [self_verify, hardware_rooted, registry_consensus,
 license_validity, agent_integrity]:
 if any positive attestation on attestation:{prefix}:
 levels.push(prefix_to_ladder_position(prefix))
 return {
 achieved: max(levels) if levels else None,
 ladder: sorted(levels),
 rendering: format_as_l1_l5_for_ui(levels)
 }
```

Consumers MAY render the ladder as `L1` / `L2` / `L3` / `L4` / `L5` for UI / dashboards / audit trails. The rendering is composition output, not wire emission.

**Why this matters**: a Verify implementation emitting `attestation:registry_consensus +1.0` is the mechanism claim. Whether that's "L3" in any particular consumer's ladder ordering is a composition concern — different consumers may order or weight the rungs differently (e.g., some safety-critical applications may require L4 *and* L5, others may treat L3 as sufficient for advisory work). The wire stays neutral; the ladder is consumer policy.

**Mechanism-only emission**: emissions use the `attestation:{mechanism}` form per the table above. The deprecated `attestation:l{N}:*` form is rejected at admission per the [CC 1.2](part_1_foundation.md) gate.

#### 4.4.3.7 `contributions-policy` — Policy F — `agent_files` trust composition

Three-layer consumer policy for composing trust over `agent_files:*` attestations ([CC 3.1.9.1](part_3_the_namespace.md) + [CC 3.1.1](part_3_the_namespace.md)).

**Layer 1 — Canonical (default trust)**: an `agent_files:*` attestation with `score ≥ 0.7` from a `registry-steward-triple` key constitutes the CIRIS canonical default-trust state. The install endpoint at `registry.ciris-services-1.ai/install` resolves canonical files via this rule.

**Layer 2 — Open Contribution**: any federation-key holder may emit `agent_files:*` attestations. The wire format admits them; consumer policy decides whether to surface them. The "Browse alternatives" view shows third-party agent_files with explicit provenance disclosure.

**Layer 3 — Vote-then-trust**: a non-canonical `agent_files:*` attestation accumulates NodeCore P4 votes. Consumer policy may elevate trust once an accumulated-weight threshold is reached.

**Anti-tricking guarantee**: the canonical-default Layer 1 rule applies at the install endpoint **regardless of attester or vote accumulation**. Third-party agent_files are reachable only via the explicit "Browse alternatives" path. This binds CIRIS L3C: the federation cannot exempt itself from the rule that newcomers' default trust path is the steward-attested canonical one.

#### 4.4.3.8 `policy-direct` — Policy A — direct trust

Consumer trusts an attestation if `attesting_key_id` is in the consumer's pinned trust set (canonical bootstraps + consumer-added pins). Cheapest, lowest-latency, narrowest reach.

Aggregation: per (`dimension`, `attested_key_id`) tuple, mean of `score × confidence` from trusted attesters. Consumer threshold determines verdict.

**Recommended default**: Policy A with `pinned_trust = {us-steward, eu-steward, apac-steward, accord_holder_1, accord_holder_2, accord_holder_3}`. Cold-start bootstrap: a new consumer obtains the pinned trust set by fetching `GET /v1/steward-key` + `GET /v1/accord-holders` ([CC 5.3.4](part_5_transport_substrate.md)), verifying the responses' hybrid signatures against TLS pubkey pinning (consumer-side TOFU or out-of-band distribution), and persisting locally.

#### 4.4.3.9 `policy-lexical` — Policy D — Lexical-vulnerability-priority

A composition tie-breaking rule layered on top of any base policy. When two otherwise-equivalent attestations conflict, defer to whichever attestation names the more-affected cohort — measured by `affected_population_estimate` in the attestation `context`, weighted inversely (smaller = more vulnerable, more weight).

Inverts the default popularity-weighted aggregation specifically for ties. Consumer policy, NOT a wire-format primitive.

#### 4.4.3.10 `policy-trusted` — Policy J — Trusted-Publisher composition

Composition pattern for multimedia content discovery per CIRISNodeCore FSD/MEDIA_SHARING.md. Reads as: "this `external_content` Contribution comes from a publisher whose attestation chain is trusted at the cohort level, with content-class + content-rating + age-assurance composed into the gate."

The composition has three layers (analogous to [CC 4.4.3.7](#816-policy-f--agent_files-trust-composition) Policy F for agent_files but specialized for multimedia content):

**Layer 1 — Distributor attestation chain**: an `external_content` Contribution with `sub_kind: film` (or any media sub_kind) carries a distributor attestation that chains to a federation_key with `identity_type: distributor`. Distributor identity is established via [CC 3.1.1](part_3_the_namespace.md) Registry partner_role machinery + an out-of-band distributor-onboarding flow (operator's choice — CIRIS L3C maintains a default trust set; community-run substrates maintain their own).

**Layer 2 — Content-class + content-rating composition**: consumer gates by combining `content_class:{class}` + `content_rating:{scheme}:{rating}` per CC 3.3.12:

```
gate_decision(content) = match (content.content_class, content.content_rating, consumer.preferences):
 # Producer-declared content_class is consultable but not authoritative — UI may show
 # the producer claim alongside cohort cw_class declarations and let the consumer choose.
 (class, _, prefs) if class in prefs.blocked_classes => Block
 (_, rating, prefs) if rating.exceeds(prefs.max_rating) => Block
 (_, _, _) => Allow
```

Layered with [CC 4.4.1](#83-frickerian-discipline--consumer-policy-norms) — `cw_class:*` declarations from low-attestation-density cohorts MUST NOT be downweighted; they ride alongside the gate decision as informational.

**Layer 3 — Age-assurance gating**: for content where `content_rating:*` rises above an age threshold (e.g. PEGI 18, MPAA NC-17), consumer gates via `age_assurance:{level}` per CC 3.3.12:

```
age_gate(content, consumer):
 required_level = age_required_for(content.content_rating)
 consumer_level = consumer.highest_age_assurance_level
 return consumer_level >= required_level
```

Where the `age_assurance:{level}` ordering is: `self < provider:{verifier_key}:adult < government:{credential_class}:adult`. Consumer SHOULD accept the strongest assurance the user has provided; substrate MUST NOT issue `slashing:*` on age-assurance misdeclaration alone — `moderation:age_assurance_misdeclaration` is the adjudication path per [CC 3.1.9.2](part_3_the_namespace.md).

**Anti-tricking guarantee parallel to CC 4.4.3.7**: the canonical-distributor Layer 1 rule MUST apply regardless of vote accumulation. No amount of NodeCore P4 vote weight elevates an unverified distributor into Layer 1; the only path is the operator-set trust list. Binds CIRIS L3C: cannot exempt itself from this rule for its own content distribution.

#### 4.4.3.11 `policy-trust` — Policy G — Trust-Fresh / Lighthouse

Composition pattern recognized in stories — `cert_validity:{authority} + transparency_log:inclusion + (attestation:registry_consensus OR attestation:license_validity)` recurred organically across ~20 substrate stories as the "freshness + attested + verified" idiom.

Reads as: the consumer wants confirmation that (a) the cert chain is currently valid; (b) the attestation appears in a transparency log; (c) either `attestation:registry_consensus` (the ladder's L3 position per CC 4.4.3.6 Policy I) or `attestation:license_validity` (L4) is satisfied. The combination is the consumer-side recipe for "this attestation is fresh AND verified AND multi-source-consensus-backed."

Not a wire primitive; a recognized composition pattern that consumer libraries SHOULD expose as a named one-call helper.

#### 4.4.3.12 `policy-one` — Policy B — one-hop transitive

Consumer trusts an attestation if `attesting_key_id` has been vouched for by the pinned trust set. Adds one hop of indirection.

#### 4.4.3.13 `policy-weighted` — Policy C — weighted graph (EigenTrust-style)

Consumer applies transitive-trust propagation across the full attestation graph, weighted by canonical-bootstrap distance with confidence decay per hop. Requires more compute; less common in practice; needed for federated reputation across many partner orgs.

### 4.4.4 `sovereign-registered` — Sovereign-Registered equivalence (wire-symmetric, policy-differentiated)

A Sovereign agent scoring `licensure:CA_medical_board: +1.0` is wire-format identical to a Registry-steward scoring the same. Consumer policy weights by attester source; the substrate is source-neutral. M-1's symmetry is structural, not bolted on.

Per [`../MISSION.md`](../../MISSION.md) §1.1: both paths produce federation membership; neither is a gate. What differs is the *attestation surface* — the kind of claim the federation can compose about why a participant is trustworthy.

## 4.5 `discipline` — Governance discipline

The federation governs itself by the same grammar it governs everything else: changes ride Contributions, are adjudicated by quorum, and are gated against capture. This section specifies how rules change, how moderation works as a delegable duty, and how the substrate protects itself against being weaponized — always with the [CC 4.2](part_4_composition_governance.md) halt-authority as the backstop.

### 4.5.1 `amendment` — Amendment process — federation Contribution + WA quorum + 1-of-6 sign-off

Rule-layer changes (new prefixes, new envelope fields, new policies, calibration package version transitions) route through:

1. **Proposed amendment** filed as a NodeCore P5 Contribution (kind: `PROPOSAL`, subject: the proposal artifact).
2. **Witness diversity** per NodeCore P10 (N=3 default).
3. **WA quorum adjudication** per NodeCore P8.
4. **Reconsideration** per NodeCore P11 with fresh-quorum recusal.
5. **1-of-6 accord-holder OR steward sign-off** as defense-in-depth gate against rules-layer Sybil capture. The 1-of-6 sign-off is the secondary check; WA quorum is the primary substantive review. Any single signer can VETO by refusing to sign. Reduces the attack surface from "produce N Sybils" to "compromise one of six specific hardware-attested keys."

**Transitional authority — the maturity gate (normative).** The mechanized process above — federation Contribution → witness diversity → WA quorum → reconsideration → 1-of-6 sign-off, together with the entrenched 2-of-3 ratification of [CC 4.5.1.2](#4512-meta-amendment--entrenchment) — is the **mature-federation** governance. It presumes a federation large enough that witness diversity and WA quorum are *meaningful*; below that scale the machinery is theater, not protection. **Until the mesh reaches maturity — a working threshold of ≥100,000 nodes — amendment authority rests with the founder, and with any accord-holder:** a benevolent-steward model in the lineage of the open-source projects this ultimately is (Linux and its maintainer-decides discipline). The maintainer decides; the work stays forkable under its license; no one is bound who does not voluntarily join the instance. The federation-Contribution + WA-quorum machinery is **deferred to mechanization** at maturity — at which point it *supersedes* founder authority and tightens governance onto the quorum/entrenchment process. The entrenchment quorum MAY be set as low as 2-of-3 by the founder before maturity; after maturity governance tightens, never loosens. The maturity gate itself is amendable by the founder/accord-holders pre-maturity, and only by the [CC 4.5.1.2](#4512-meta-amendment--entrenchment) entrenched process post-maturity.

#### 4.5.1.1 `axis` — Axis-vocabulary discipline

Every `{axis}` value emittable under open-vocabulary prefixes (e.g., `detection:correlated_action:{axis}`, `hard_case:{kind}`, `testimonial_witness:{kind}`) MUST carry an operational definition where the prefix has a calibration package (RATCHET-calibrated detectors) or a documented convention where it doesn't.

For RATCHET-calibrated detectors, the operational definition lives in the calibration package version pinned via `evidence_refs[]`:

1. Measurement procedure
2. Threshold function
3. Statistical floor
4. Evidence-shape requirement
5. Polarity semantics

For documentation-only open vocabularies (`testimonial_witness:{kind}`, `hard_case:{kind}`, `topical_relation:{kind}`), discoverability lives in non-normative registry documents like [`WITNESS_KIND_REGISTRY.md`](../WITNESS_KIND_REGISTRY.md) — additions there require no spec amendment.

#### 4.5.1.2 `meta-amendment` — Meta-amendment + entrenchment

The CC 4.5.1 amendment process itself, the [CC 1.2](part_1_foundation.md) T1–T4 prefix-admission gate, and the [CC 4.2](part_4_composition_governance.md) HUMANITY_ACCORD constitutional layer are **entrenched** — changes to these three surfaces require a MAJOR version bump per [CC 2.6.4](part_2_the_grammar.md) AND an additional 2-of-3 HUMANITY_ACCORD signatures (NOT the 2-of-3 from CC 4.5.1 step 5 — a separate, dedicated accord ratification). Without this entrenchment, a single quorum could rewrite the gate admitting the next quorum. (This entrenched ratification is the **mature-federation** mechanism; pre-maturity it is exercised by the founder/accord-holders under the maturity gate in [CC 4.5.1](#451-amendment--amendment-process--federation-contribution--wa-quorum--1-of-6-sign-off).)

#### 4.5.1.3 `open-vocabulary` — Open-vocabulary collision rule

When two parties independently register confusingly-similar `{kind}` / `{axis}` values within the same prefix family, the following resolution applies:

1. **First-registered wins** for the canonical-attestation surface. The earlier `signed_at` holds the name; later registrations carry a `differs_in: ["semantic_disambiguation"]` clarification or pick a distinct value.
2. **Levenshtein-distance guard**: a CEG-Conforming Substrate (CCS) SHOULD compute Levenshtein distance against existing values in the same prefix family at admission; values within distance ≤ 2 of an existing canonical value SHOULD return a `409 IDEMPOTENT_CONFLICT` with an advisory hint, NOT a hard reject — the producer may proceed if the similarity is intentional (e.g., `commonsense` vs `commonsense_hard` are intentionally close).
3. **No squatting**: a `{kind}` registered but never used (no scored attestations in 90 days) MAY be reclaimed by another producer via the [CC 4.5.1](#451-amendment-process--federation-contribution--wa-quorum--1-of-6-sign-off) amendment process.

### 4.5.2 `compliance` — Vertical compliance + subject-bearing dimension governance

The wire-format primitives in [CC 2.3](part_2_the_grammar.md) `subject_key_ids` + [CC 3.3.1](part_3_the_namespace.md) `consent:*` family + [CC 3.3.5](part_3_the_namespace.md) `consent_record` + [CC 4.4.3.5](part_4_composition_governance.md) Policy K compose into regulatory-vertical compliance mappings. CEG documents the canonical mappings as **informational**; the wire-format primitives are domain-agnostic and operator-configurable.

#### 4.5.2.1 `subject_kind-subject-3` — Subject-bearing dimension governance (normative)

Per [CC 2.3.1](part_2_the_grammar.md). Dimensions whose namespace pattern names a subject MUST carry `subject_key_ids` containing that subject. This closes the default-leak failure mode where subject-bearing content publishes without wire-level subject authority.

**Subject-bearing dimension patterns** (open catalog; operator vocabularies extend):

| Pattern | Example | Required `subject_key_ids` entry |
|---|---|---|
| `observed:user:{key_id}:*` | `observed:user:abc123:interaction_count` | `abc123` (or its canonical-hash form) |
| `epistemic:about:{key_id}:*` | `epistemic:about:abc123:trust_assessment` | `abc123` |
| `epistemic:memory:topic={topic}` (when topic names a person/entity) | `epistemic:memory:topic=patient_xyz_session` | `patient_xyz` canonical-hash |
| `consent:partnered:{user_key}` (CIRISAgent CEM agent-side stance) | `consent:partnered:abc123` | `abc123` |
| `agent_files:*:{subject_target}` (when target names a person) | `agent_files:medical_record:patient_xyz` | `patient_xyz` canonical-hash |
| `licensure:{authority_id}:{practitioner_key}` (when practitioner is named) | `licensure:CA_medical_board:dr_jones_key` | `dr_jones_key` |

**Substrate enforcement**: substrate admission gate MAY reject Contributions where the dimension matches a subject-bearing pattern but `subject_key_ids` is empty / does not contain the named subject. This is **operator-policy** (not normative across all substrates) — some operator configurations may admit and emit a `hard_case:subject_authority_missing` for review-queue handling instead of rejection.

**The takedown-isn't-a-coup parallel** ([CC 4.5.3 fast-path takedown](#453-fast-path-takedown-coordination-ceg-03-addition-per-cirisregistry37--38)) applies: substrate enforcement of subject-bearing dimension discipline cannot be used as a coup against the substrate itself (e.g., a state actor publishing `observed:user:dissenter_key:*` with `subject_key_ids = []` and demanding substrate admission). The CC 4.2 HUMANITY_ACCORD remains load-bearing; admission-gate rules apply uniformly.

#### 4.5.2.2 `compliance-vertical` — Vertical compliance mapping (informational)

| Regulatory framework | CEG primitive | How it composes |
|---|---|---|
| **GDPR Article 7** (consent) | `consent:state:granted` + `consent_record.subject_key_id` | Subject's wire-format declaration of consent; revocable via [CC 2.4.1.1](part_2_the_grammar.md) rule 2 |
| **GDPR Article 9** (special category — health, biometric, sexual orientation, etc.) | `subject_key_ids` MANDATORY for special-category content; producer's `consent:deletion_sla` SHOULD be ≤ 30 days | Substrate-level recognition that special category requires subject-side wire authority |
| **GDPR Article 17** (right to erasure) | `consent:state:revoked` → substrate-watched `consent:deletion_sla:{days}` → producer emits `consent:deletion_complete` OR substrate emits `hard_case:consent_sla_breach` | The CC 4.4.3.5.2 SLA watcher is the wire-format observability primitive for Article 17 compliance |
| **GDPR Article 20** (data portability) | DSAR export via `attestations.where(s ∈ subject_key_ids)` query | CIRISAgent's `DSARExportPackage` composes from this query trivially |
| **HIPAA 45 CFR 164.502** (uses + disclosures) | `consent:scope:{retain\|share\|analyze\|train\|publish}` + `cohort_scope` | scope qualifier names the permitted use; cohort_scope names the permitted visibility |
| **HIPAA 45 CFR 164.524** (patient right of access) | DSAR export per Article 20 above | Same composition |
| **FERPA 34 CFR Part 99** (educational records) | `subject_key_ids: [student_key]` + `delegates_to(parent_key → student_canonical_hash, scope: [consent_revocation])` for minors | Parental authority composes via the existing `delegates_to` primitive; no new shape needed |
| **CCPA §1798.105** (right to delete) | Same composition as GDPR Article 17 | Substrate-watched SLA + `consent:deletion_complete` |
| **EU AI Act Article 50** (training data transparency + opt-out) | `consent:scope:train` + `is_ai_generated` field at content publish + subject's `consent:state:revoked` against the training-datum Contribution | Subject can withdraw training-set consent; producer's deletion-SLA fires on the training-corpus Contribution |
| **CIRIS Accord M-1** (sustainable adaptive coherence — consent revocability) | The entire subject-authority surface | The constitutional anchor — "consent (M-1's load-bearing property) requires revocability, and revocability requires a halt-authority that lives outside the system being halted" ([CC 4.2](part_4_composition_governance.md) + MISSION.md §1.5). This recognition extends from accord-carriers (federation-as-a-whole halt) to all subject-authorities (per-Contribution halt) at scale. |

CEG does NOT prescribe which regulatory framework an operator MUST comply with; the wire primitives compose to ANY of them based on operator policy. Operators in regulated verticals (medical / legal / financial / educational) SHOULD pin compliance mappings as configuration above the wire primitives, not as new wire shapes.

#### 4.5.2.3 `documents-what-3` — What this governance layer documents

- The wire-format primitives that compose into vertical compliance (informational mapping above)
- The dimension-pattern-implies-`subject_key_ids` requirement (normative gate)
- The bilateral-pair shape for ceremony grants per [CC 4.4.3.5.3](part_4_composition_governance.md)
- The decay-protocol stage composition per [CC 4.4.3.5.1](part_4_composition_governance.md)
- The SLA watcher boundary (substrate emits `hard_case:*`; LensCore composes `detection:*`) per [CC 4.4.3.5.2](part_4_composition_governance.md)

What it does NOT do:
- Bundle CIRISAgent's CEM streams as the only valid stream set (open vocab; CEG names `temporary` / `partnered` / `anonymous` as recommended canonical kinds, not lockdown)
- Define specific SLA values for any regulatory framework (operator policy — though informational guidance: GDPR Article 9 default ≤ 30 days; CCPA default 45 days; etc.)
- Provide a decay-protocol library (CIRISAgent's 90-day-decay is the canonical example; other protocols MAY exist)
- Prescribe per-vertical compliance audit cadence (consumer / regulator concern)

### 4.5.3 `takedown` — Fast-path takedown coordination

Some takedowns cannot wait for the CC 4.5.1 amendment timeline. For `takedown_notice` Contributions ([CC 3.3.2](part_3_the_namespace.md)) whose `legal_basis` falls in the **immediate-removal** category (`TvecTerrorist` / `NcmecCsam` / `GifctCip` / `PerceptualHashCsam` / `CourtOrder`), TVEC mandates a 1-hour removal obligation; GIFCT CIP coordinates within hours; NCMEC + perceptual-hash + court orders demand near-immediate response.

A fast-path coordination protocol carves this out:

1. **Notice admission**: the `takedown_notice` Contribution arrives at the substrate, signed by `claimant_key_id`. The substrate accepts it without CC 4.5.1 quorum; speed matters at this layer.
2. **Holder eviction**: substrate emits a `withdraws` against the matching `holds_bytes:sha256:{prefix}` directory entry per [CC 5.3.2.1](part_5_transport_substrate.md). Holders see their advertisement marked withdrawn and SHOULD cease serving the bytes.
3. **Per-basis dispatch**:
 - `TvecTerrorist` — operator coordinates via TVEC-designated channel (national regulator notification within 1 hour); substrate logs the notice + the eviction action to its audit chain.
 - `GifctCip` — operator coordinates via GIFCT Content Incident Protocol communication channel; same audit-chain logging.
 - `NcmecCsam` + `PerceptualHashCsam` — operator MUST file the NCMEC CyberTipline report (US 18 USC §2258A); substrate retains hash + minimal metadata for the federal-legal retention window only. No content retention.
 - `CourtOrder` — operator follows the court's stated timeline; substrate logs the order text + the eviction action.
4. **Audit trail**: every fast-path takedown enters a `hard_case:fast_path_takedown` Contribution ([CC 3.1.9.4](part_3_the_namespace.md)) for downstream review. Reviewers MAY file a `reconsideration:procedural_error` if the fast-path basis was misclassified.
5. **No counter-notice for immediate-removal cases**: by `legal_basis` design (TVEC / NCMEC / GIFCT / PerceptualHashCsam / CourtOrder all bypass counter-notice). The `expeditious-with-counter-notice` bases (`Dmca512` / `DsaArticle16` / `CommunityStandards` / `OsaIllegalContent`) route through the standard CC 4.5.1 amendment path on counter-notice via `reconsideration:new_evidence`.

**The takedown-isn't-a-coup property**: the CC 4.2 HUMANITY_ACCORD remains load-bearing. Fast-path takedowns happen via this protocol but a `takedown_notice` Contribution targeting the substrate itself (e.g., a state actor demanding takedown of `federation_keys` for whole categories of dissenting participants) would not propagate the same way — substrate-protective discipline + HUMANITY_ACCORD veto authority intersect at the substrate level. Operators in jurisdictions where this conflict materializes SHOULD escalate to the HUMANITY_ACCORD triple per CC 4.2.1 invocation procedures.

### 4.5.4 `registry-named` — Named-moderator existence invariant + merit auto-promotion

**No unmoderated multi-party space, ever.** A `community` ([CC 3.2](part_3_the_namespace.md)) operates / federates **only while it has ≥1 active holder of its `moderate` duty** ([CC 4.5.5](#455-moderation-as-a-delegable-duty--moderate--takedown--review-10-rc19-per-cirisregistry90)) — the moderation analogue of the [CC 3.2](part_3_the_namespace.md) steward-binding gate. This closes the unmoderated-space-for-predators gap of relay-level (Nostr) / immutable-store (IPFS) / lax-instance (fediverse) models. Design: CIRISServer `FSD/MODERATION_CHILD_SAFETY.md` + `FSD/SAFETY_LANDSCAPE.md`.

Three normative rules:

1. **Existence gate.** A `community` is admitted, and continues to federate, **only while ≥1 member holds the live `moderate` duty**. The creator **names one at creation** (founder responsibility). A community with no active `moderate`-holder is non-conformant.
2. **Merit auto-promotion (no moderator-less window).** When the named moderator lapses (`withdraws` against the `moderate` `delegates_to`, or inactivity past the community's freshness window), the member with the **highest [`moderation_track_record`](part_3_the_namespace.md)** ([CC 3.1.9.2](part_3_the_namespace.md)) is **automatically granted** the `moderate` duty — emergent, meritocratic authority (the moderation analogue of the steward-binding gate: authority emerges from an accountable, *merited* member, never a vacuum). **Deterministic selection:** highest `moderation_track_record`; tiebreak by earliest membership, then lexicographic `key_id` (so every peer auto-promotes the *same* member).
3. **Fail-secure.** If no eligible member can be named (none with sufficient track record, none consenting, none steward-bound), the community **fails-secure** — it MUST NOT federate / operate at moderated capability. **Better no group than an unmoderated one.** (Degrade, never escalate — the fail-secure default.)

**Named-moderator binding — the substrate-resolvable shape.** "K is a named-moderator over community C" is an **appointment**: a `delegates_to(authority → K, scope ⊇ {moderate|takedown|review}, community_id: C)` whose root `authority` is in **C's authority set** — a founder, or a key the community's `consensus_protocol` authorizes, per the [CC 3.2](part_3_the_namespace.md) community record — and is steward-bound. It rides the **existing** `community_id` envelope field + `delegates_to`; **no new shape.** A substrate resolves: **`is_named_moderator(K, C, duty)`** ≔ ∃ live `delegates_to` chain `root →* K` with every edge `scope ⊇ {duty}`, `community_id == C`, `root ∈ authority_set(C)` (the CC 3.2 founders / consensus signers), and `is_steward_bound(root)` ([CC 3.2](part_3_the_namespace.md)). **Merit auto-promotion (rule 2) emits exactly this appointment shape** — the community's authority auto-grants the `moderate` `delegates_to` to the highest-`moderation_track_record` member — so an auto-promoted moderator is resolvable **identically** to a hand-named one (one code path, no special case).

**Merit grants the duty, NOT fiat (anti-censorship).** The auto-promoted moderator holds the [CC 4.5.5](#455-moderation-as-a-delegable-duty--moderate--takedown--review-10-rc19-per-cirisregistry90) `moderate`/`takedown`/`review` duty — but every **action** is constrained, so this is not arbitrary power: (a) the [CC 4.5.6](#456-operational-language-gate-at-admission) operational-language gate at admission, and (b) deterministic verdicts + the [CC 4.5.5](#455-moderation-as-a-delegable-duty--moderate--takedown--review-10-rc19-per-cirisregistry90) Reconsideration appeals (recused reviewers). **Merit grants the seat; the gate + appeals constrain the action.** The duty is itself revocable and re-auto-promotes on lapse — so capture is bounded.

**1+4 preserved.** `moderation_track_record` rides `scores` ([CC 3.1.9.2](part_3_the_namespace.md)); the existence invariant + auto-promotion are admission/composition rules over the existing `delegates_to` (`moderate` scope) + the reputation corpus. **No new structural primitive.**

**Enforcement layer — substrate, at admission *and* on every federation step.** The existence gate (rule 1) is a **substrate invariant, not a governance- or consumer-policy-layer obligation.** The substrate MUST evaluate `is_named_moderator(·, C, moderate)` over a `community` `C` at two points: **(i) at admission** — `C` is admitted to federate **only if** ∃ a live `moderate`-holder resolvable by the rule-1 shape; and **(ii) on the federation path** — every cross-region propagation / federation apply step keyed on `C` MUST re-check live `moderate`-holder existence **at apply time**, so a community that *loses* its moderator (lapse, `withdraws`-revocation, or freshness-window expiry per rule 2) cannot continue at moderated capability without one. On that loss the substrate MUST first attempt **merit auto-promotion** (rule 2): if a deterministically-selected eligible member exists, the substrate emits the rule-2 appointment and federation continues on the same apply step (one code path, per the named-moderator-binding shape above). If none is auto-promotable, the community enters the [CC 4.5.13](part_4_composition_governance.md) **48-hour no-moderator recovery** (a 24 h open candidacy phase + selection); it **fails-secure** (rule 3) — MUST NOT federate at moderated capability — only if that window elapses with no named moderator. **No governance or consumer-policy layer may admit or sustain a moderator-less `C` into federation: the gate lives where the write lands.** This mirrors the [CC 3.2](part_3_the_namespace.md) steward-binding gate, which the substrate likewise enforces at admission rather than delegating to a higher layer. The `is_named_moderator` resolution (e.g. persist's `admission::named_moderator_holders`) is the **primitive** this gate consumes; the **gate itself** — admission check *plus* federation-path re-check — is **substrate**, not LensCore / consumer filter policy ([CC 4.4](part_4_composition_governance.md)). (Per CIRISRegistry#110(a) / CIRISPersist#238 — resolving the deferred enforcement-layer ambiguity.)

### 4.5.5 `takedown-moderation` — Moderation as a delegable duty — `moderate` / `takedown` / `review`

Moderation is a **delegable *duty*, not a platform- or fabric-assigned role** (design: CIRISServer `FSD/MODERATION_CHILD_SAFETY.md`). A participant exercises a moderation / takedown / review duty **as themselves**, or delegates it — to **their agent** (AI on-behalf-of) or to **any trusted party** (another human, a community moderator) — via `delegates_to`. This is the wire foundation under the child-safety / takedown / accord UX, and the spine of *accountability ships ahead of capability*: **no media/chat feature ships until this — plus persist enforcement + fabric wiring — is solved and working.**

**Two layers — open labeling, and authoritative action.** Moderation in CEG spans both layers of the composable/stackable model (cf. Bluesky labelers + Ozone) but unifies them on the 1+4 grammar and adds the enforced action tier:

- **Open labeling — anyone, no authority.** Anyone MAY file a `scores` Contribution against anything they see (an *opinion/observation*, not an action). It is **visible to everyone who chooses** to read it, and consumers compose **filters** over the score graph — hide / blur / annotate / down-rank — as pure consumer policy ([CC 4.4](part_4_composition_governance.md)). This generalizes independent labelers: stackable, swappable, subscribed by choice. A filter MAY **escalate to an auto-finding** — e.g. a [CC 4.5.7](#457-watchlist-auto-detection--opt-in-per-group-separation-of-powers-10-rc23-per-cirisregistry94) CSAM watchlist match auto-fires a `takedown_notice` under an *enabling authority* — turning a passive filter into an action.
- **Authoritative action — the enforced duty.** Hiding-for-yourself needs no authority; **acting on a group's behalf** (a takedown, an authoritative ModerationEvent, an appeal ruling) requires the delegated `moderate`/`takedown`/`review` duty (below). [`moderation_track_record`](part_3_the_namespace.md) ([CC 3.1.9.2](part_3_the_namespace.md)) composites a moderator's action outcomes into the **relative, positional reputation** decentralized-moderation converges on — never a single global score.

One grammar covers a group chat, a classroom (teacher = delegated `moderate`), a town hall, an art gallery, a subreddit, a Discord, a Facebook-scale community: **the labeling open + filterable, the authority delegable + attenuable + revocable.**

CEG **names** the three duties as canonical `delegated_scope` kinds and **enforces** their admission — mirroring the only previously-enforced scope, `consent_revocation` ([CC 2.4.1.1 rule 3](part_2_the_grammar.md)). The kinds + their shipped action primitives are pinned at [CC 4.4.3.4.3.1](part_4_composition_governance.md):

| scope | emits, on the delegator's behalf | shipped primitive |
|---|---|---|
| `moderate` | `moderation:{allegation_type}` ModerationEvent + report→`scores` + `age_assurance`/`content_class` gates | [CC 3.1.9.2](part_3_the_namespace.md) / [CC 4.4.3.10](part_4_composition_governance.md) |
| `takedown` | `takedown_notice` (incl. the CC 4.5.3 immediate-removal fast-path) | [CC 3.3.2](part_3_the_namespace.md) / [CC 4.5.3](#453-fast-path-takedown-coordination-ceg-03-addition-per-cirisregistry37--38) |
| `review` | `reconsideration:{grounds}` appeal / review | [CC 3.1.9.2](part_3_the_namespace.md) |

**Enforced-admission rule — the principal is the chain root, NOT a payload field.** The principal an action is taken *on behalf of* is **discovered by walking the `delegates_to` graph upward from `attesting_key_id`** — it is **never** carried in a payload field. There is deliberately **no `on_behalf_of` (or equivalent) envelope field**: a side-field both violates the 1+4 lockdown *and* opens a bypass — if "absent field ⇒ as-self ⇒ admit," then any emitter that simply omits the field (e.g. an AI agent or untrusted party firing a takedown) is admitted as-self with no steward-bound chain proven, and the gate becomes a no-op exactly where it is load-bearing. A moderation action (`takedown_notice`, `moderation:*`, `reconsideration:*`) is admitted **iff** one holds **positively**:

- **(a) as-self** — `attesting_key_id` *itself* holds the matching duty over the target: it is the target content's own subject, **or** the target community's [CC 4.5.4](#454-named-moderator-existence-invariant--merit-auto-promotion-10-rc21-per-cirisregistry93) named-moderator / `moderate`-holder. A zero-hop chain rooted at itself.
- **(b) delegated** — a live `delegates_to` chain `root →* attesting_key_id` where **every edge bears the matching scope** (`scope ⊇ {moderate|takedown|review}`), the **root holds the duty over the target** and is **steward-bound** ([CC 3.2](part_3_the_namespace.md) — an accountable human), depth ≤ 5 ([CC 4.1.1](part_4_composition_governance.md)), and **no edge is `withdraws`-revoked**.

Otherwise **REJECT**. **Absence of a principal field is NOT an admit condition** — admission requires (a) or (b) to hold positively; a verifier MUST NOT read "no field present" as "as-self." This is the faithful mirror of `consent_revocation` ([CC 2.4.1.1 rule 3](part_2_the_grammar.md)), which derives its principal from the existing `subject_key_ids` relationship + the chain, never a side-field. Substrate SHOULD record which rule + which root admitted the action (the CC 2.4.1.1 per-rule audit metadata).

**Deputization + attenuation (normative; SOTA-aligned — UCAN / macaroons / SPKI-SDSI / ZCAP-LD).** A `delegates_to` MAY permit its delegate to **deputize** (further-delegate the duty) — but **only if the delegator granted it**, by including `sub_delegation` in the granted `delegated_scope` ([CC 4.4.3.4.3.1](part_4_composition_governance.md)). Every sub-delegation **attenuates, never expands**: `child.scope ⊆ parent.scope`, and constraints may be *added* but never removed — the capability-attenuation rule shared by UCAN (each delegation "restates or attenuates"), macaroon caveats, and SPKI/SDSI proof-carrying authorization. The chain is depth-capped at 5 ([CC 4.1.1](part_4_composition_governance.md)) and **revocable at any link**: a `withdraws` against *any* `delegates_to` in the chain invalidates everything downstream of it (UCAN-style proof-chain revocation). So a delegator decides at grant time **whether** their deputy may appoint further deputies and **under what constraints**, and can sever the entire subtree with a single revocation — deputize-a-teacher's-aide, hand-a-shift-to-another-mod, appoint-an-agent, all with bounded, revocable, attenuating authority.

**Target → duty-holder resolution — makes the rule substrate-enforceable.** "Holds the duty over the target" is resolved by mapping the action's target to its duty-holder set, then checking the two predicates against it:

- `takedown_notice{content_sha256}` → the content's **authoritative** subject set `subject_of(content_sha256)` (self — see the resolution rule below; **not** the action payload's self-declared `subject_key_ids`) ∪ `is_named_moderator(·, C, takedown)` for the content's community `C` (its `cohort_scope: community` / `community_id`).
- `moderation:{allegation_type}` against a subject → `is_named_moderator(·, C, moderate)` for the relevant community.
- `reconsideration:{grounds}` against a prior action → `is_named_moderator(·, C, review)` for that action's community.

**(a) as-self** holds iff `attesting_key_id ∈ duty-holders(target)` (a subject, or `is_named_moderator`); **(b) delegated** holds iff the chain `root ∈ duty-holders(target)` ∧ `is_steward_bound(root)`. With **`is_steward_bound`** ([CC 3.2](part_3_the_namespace.md)) and **`is_named_moderator`** ([CC 4.5.4](#454-named-moderator-existence-invariant--merit-auto-promotion-10-rc21-per-cirisregistry93)) both resolvable from existing rows (community record + `identity_occurrence` + `delegates_to` + `community_id` + `subject_key_ids`), CC 4.5.5 is **fully substrate-enforceable** — community moderation is not rejected for lack of a resolvable shape. No new structural primitive.

**Subject authority is resolved from the content's signed provenance, NOT the action payload.** The subject side of admit-(a) has the same substrate-resolvability requirement the named-mod path got: *which* `subject_key_ids` is authoritative. A `takedown_notice` / `moderation:*` action carries a `content_sha256` **and** its own payload `subject_key_ids` — and a substrate that reads the subject set from the **action's own payload** lets an actor self-declare `subject_key_ids = [self]` over content it does not own, satisfy "as-self," and take down arbitrary content **without being a named-moderator** (a narrower, attributable re-opening of the takedown-isn't-a-coup hole on the subject path; the named-mod path is unaffected). The subject claim MUST instead be verified against the content's **establishing attestation**:

- **`subject_of(content_sha256)`** ≔ the signed `subject_key_ids` of the **establishing attestation** — the `scores` Contribution whose content the `content_sha256` binds (the [CC 2.3](part_2_the_grammar.md) subject set is signed *inside* that attestation by its producer, not assertable by a later third party). A substrate resolves `content_sha256` → establishing attestation → its signed `subject_key_ids`. This is the same content-hash → signed-attestation resolution every [CC 2.1](part_2_the_grammar.md) verifier already performs; no new index.
- **Admit-(a) subject-self** for content targets then means `attesting_key_id ∈ subject_of(content_sha256)` — the **signed** subject, never the takedown payload's self-declared set. The action payload's `subject_key_ids` is, on the subject-authority path, **advisory only** (it MAY be used to *route* / *queue*, but MUST NOT be the set admit-(a) is checked against).
- **Fail-secure when the establishing attestation is not locally held.** If a substrate cannot resolve `content_sha256` to its establishing attestation, `subject_of(content_sha256)` is **undetermined** and the subject-self clause **fails** (it does not admit) — the named-moderator path (b) is the only remaining route, exactly as for any other unprovable-authority case. Absence of provenance is never an admit condition (the same discipline as the `on_behalf_of` absence rule above).

With this, **both** clauses of admit-(a) — subject-self and named-moderator — and clause (b) resolve against **signed** state, never self-declared payload. The CC 4.5.5 gate has no remaining self-declaration spoof. Composes over the existing `scores` attestation + `subject_key_ids`; no new structural primitive.

**The "takedown-isn't-a-coup" property, made structural.** Because every action is delegate-signed, delegator-traceable up the `delegates_to` chain, steward-bound at the root ([CC 3.2](part_3_the_namespace.md) — authority roots in an accountable human), and revocable, a takedown is **coordinated + attributable + revocable** — never a unilateral seizure. A no-authority actor, or a state actor demanding removal of `federation_keys` for whole classes of dissenters, **fails the enforced-admission gate** and escalates to the [CC 4.2](part_4_composition_governance.md) HUMANITY_ACCORD per [CC 4.5.3](#453-fast-path-takedown-coordination-ceg-03-addition-per-cirisregistry37--38). The CC 4.5.3 immediate-removal timeline is unchanged — speed at the action layer; authority checked at the delegation layer.

**1+4 preserved.** A `delegated_scope` vocabulary + enforced-admission addition over the existing `delegates_to`; the action primitives (`moderation:*`, `takedown_notice`, `reconsideration:*`) already ship. **No new structural primitive.**

### 4.5.6 `admission-operational` — Operational-language gate at admission

Every new prefix admitted to the [CC 3.1](part_3_the_namespace.md) namespace passes the [CC 1.2](part_1_foundation.md) four-test gate. Failed admissions are revised (mechanism-descriptive reframe) or rejected.

### 4.5.7 `registry-watchlist` — Watchlist auto-detection — opt-in, per-group, separation-of-powers

Content-watchlist auto-detection (design: CIRISServer `FSD/WATCHLIST_DETECTION.md`): a [CC 4.5.5](#455-moderation-as-a-delegable-duty--moderate--takedown--review-10-rc19-per-cirisregistry90) `moderate`-scope holder **optionally** enables a watchlist (`watchlist:{id}`, [CC 3.1.9.4](part_3_the_namespace.md)) for a group they moderate; the fabric auto-fires the matcher at the **publish/share seam** and auto-fires the action — CSAM → `takedown_notice{PerceptualHashCsam}` ([CC 4.5.3](#453-fast-path-takedown-coordination-ceg-03-addition-per-cirisregistry37--38)); other → `detection:*` + a `moderation:*` ModerationEvent to the named moderator. Rides shipped primitives — **no new structural primitive.**

**Opt-in, per-group, NEVER global (normative).** A watchlist is enabled per-group by its `moderate`/`takedown` authority; a global "scan everything" config is **non-conformant** — that is the bulk-surveillance posture the framework refuses. Enable/disable is **signed by the authority and revocable** (`withdraws`).

**Separation of powers (the responsible-design invariant).** No single party does all three:

| Party | Holds | Cannot |
|---|---|---|
| **Fabric** (the node) | the *mechanism* — the matcher at the publish/share seam | provision the hash-DB; choose to enable |
| **Operator** | the *licensed hash-DB* (IWF/NCMEC/PDQ, [CC 4.5.10.1](#45101-hash-database-access-landscape), operator-provisioned + unshippable) + the NCMEC report obligation | turn it on for a group; act without the authority's opt-in |
| **Authority** (`moderate`-holder) | the *opt-in* (per-group enable) | run the match itself; access the licensed list |

**Audit — never silent (normative).** Enabling a watchlist emits `hard_case:watchlist_enabled:{group}` ([CC 3.1.9.4](part_3_the_namespace.md)) — who turned it on + which list; **every match** emits `hard_case:watchlist_match:{group}`. Enablement and matches are on the record, always.

**CSAM-disable non-silent floor (normative).** Disabling a **CSAM** watchlist MUST be an audited act — a `withdraws` signed by the authority that **emits `hard_case:watchlist_enabled` (disable variant)**; **silent removal of a CSAM list is barred** (a predator-operator cannot turn off CSAM detection without leaving a trace). Ordinary (non-CSAM) lists may be freely toggled. This is the floor that keeps the opt-in honest.

**Honest scope.** Detection runs **only at the publish/share seam of enabled groups** — it **cannot** reach [CC 5.2](part_5_transport_substrate.md) self/family private content (the universal E2EE limit; not claimed solved), and CEG does **not** mandate client-side scanning. **1+4 preserved** — `watchlist:{id}` rides `scores`/config over `delegates_to`; the audit reasons ride the existing `hard_case:*` prefix; the actions ride `takedown_notice` / `detection:*` / `moderation:*`.

### 4.5.8 `identity-set-2` — `identity_type` as a set — single-key role cohabitation

Per [CC 3.4.7.1](part_3_the_namespace.md). `federation_keys.identity_type` is a **set of roles**, not a single scalar role, so the [CC 3.4](part_3_the_namespace.md) reserved-prefix gates are evaluated by set membership (`X ∈ identity_type`). This routes through the [CC 4.5.1](#451-amendment-process--federation-contribution--wa-quorum--1-of-6-sign-off) amendment process.

#### 4.5.8.1 `cohabitation` — Cohabitation discipline for constitutional + substrate roles

Set membership grants the wire-level *right* to emit per held role, but two roles carry defense-in-depth guidance against cohabitation:

- **`accord_holder` ([CC 3.4.1](part_3_the_namespace.md) + [CC 4.2](part_4_composition_governance.md))**: the one constitutional asymmetry. Consumer policy SHOULD treat an `accord_holder` key that also holds non-constitutional roles (e.g., `{accord_holder, agent}`) with elevated scrutiny — the HUMANITY_ACCORD triple's halt authority is strongest when its keys are single-purpose. The cohabitation is NOT forbidden at the wire layer (the substrate cannot adjudicate constitutional intent), but the CC 4.2 entrenched-`family` discipline RECOMMENDS dedicated accord-holder keys.
- **`substrate_persist` / `substrate_edge` ([CC 3.4.3](part_3_the_namespace.md))**: substrate-self-report roles remain cross-attested by the full steward-triple per CC 3.4.3. A key cohabiting a substrate role with an application role (e.g., `{substrate_persist, agent}`) MUST still satisfy the steward cross-attestation requirement for the substrate-role emissions; cohabitation does not relax the cross-attestation gate.

#### 4.5.8.2 `amendment-what` — What this changes — and what it deliberately does not

| Surface | Representation |
|---|---|
| `federation_keys.identity_type` representation | set of role strings (legacy scalar = singleton set) |
| CC 3.4 emitter-rule evaluation | `X ∈ identity_type` ([CC 3.4.7.1](part_3_the_namespace.md)) |
| CC 3.1 dimension namespace | unchanged |
| Envelope ([CC 2.1](part_2_the_grammar.md)) | unchanged |
| 1+4 structural primitives ([CC 2.4](part_2_the_grammar.md)) | unchanged |
| subject_kinds ([CC 3.3](part_3_the_namespace.md)) | unchanged |

This is a wire-break at the `federation_keys` row representation only. It is **semantically null for every legacy single-role key**: `X ∈ {X}` ≡ `X == X`. It is NOT a [CC 1.7](part_1_foundation.md) "Nth path" confirmation (it adds no namespace surface); it is a [CC 3.4](part_3_the_namespace.md)-layer enforcement generalization that unblocks the CIRISAgent fold-in (one key, many roles) without expanding the wire's expressive surface.

#### 4.5.8.3 `settled` — Settled in CIRISAgent, carried as-is

- **Capacity self-emission ([CC 3.4.5](part_3_the_namespace.md))**: unchanged. The anti-Goodhart `attesting_key_id ≠ attested_key_id` rule binds regardless of how many roles a key holds. A folded `{agent, lenscore_detector}` key still MUST NOT score its own `capacity:*`. Role cohabitation does not create a self-attestation backdoor.
- **Reasoning-trace dimensions**: no separate reserved `identity_type` required; reasoning-trace emission rides the agent role's open-vocabulary surface. Cohabitation does not change this.
- **Agent-intent / LensCore-envelope split**: a cohabiting key emits agent-intent attestations under the agent dimensions and detector verdicts under `detection:*` ([CC 3.4.8](part_3_the_namespace.md) worked example). The namespace keeps the two surfaces distinct; cohabitation grants the right to emit on each, never merges them.

#### 4.5.8.4 `documents-what-6` — What this documents

- The set-membership reading of every CC 3.4 reserved-prefix emitter rule ([CC 3.4.7.1](part_3_the_namespace.md))
- The canonical-bytes encoding for the set (sorted-ascending, deduplicated, comma-joined; single-role keys encode identically to their scalar form)
- The LensCore-fold worked example ([CC 3.4.8](part_3_the_namespace.md))
- The cohabitation discipline for constitutional + substrate roles (CC 4.5.8.1)

What it does NOT do:
- Expand the CC 3.1 dimension namespace, the CC 2.1 envelope, the CC 2.4 structural-primitive set, or the CC 3.3 subject_kinds (zero new wire surface beyond the `identity_type` representation)
- Enumerate a closed set of role values — `identity_type` members remain an open vocabulary owned per [CC 3.4](part_3_the_namespace.md) reservations + sibling-component vocabulary extensions
- Forbid any cohabitation at the wire layer (substrate enforces gates by membership; constitutional/substrate cohabitation discipline is consumer/operator policy per CC 4.5.8.1)
- Address `affiliations` (the fourth `cohort_scope` tier; remains deferred to a later candidate round)

### 4.5.9 `registry-geographic` — Geographic-community privacy invariant

Per [CC 3.2](part_3_the_namespace.md) `community` with `cohort_subkind: geographic` + [CC 3.3.3](part_3_the_namespace.md) `location_proof` + [CC 2.6.6](part_2_the_grammar.md) H3 cell canonicalization + [CC 4.4.3.2](part_4_composition_governance.md) Policy M.

A load-bearing privacy invariant: **joining a geographic community is a one-way disclosure**. Three sub-properties make this wire-format-level, not policy-level.

#### 4.5.9.1 `location-joining` — Joining is opt-in — substrate does NOT solicit location

A `location_proof` Contribution is emitted **only** by the subject themselves (`attesting_key_id == subject_key_id`) or by a `delegates_to` chain with `scope: [consent_revocation]` — the substrate has no path to mint a location_proof on behalf of a key without an explicit signature.

Communities cannot **require** a location_proof from non-members (they can only **gate admission** on whether a member has produced one). The substrate has no mechanism for "involuntary location disclosure" via the wire format. A bad actor cannot force-publish another key's location_proof; without the subject's signature, the substrate rejects.

**Compose with [CC 4.2 HUMANITY_ACCORD](part_4_composition_governance.md) substrate-protective discipline**: a state actor demanding the substrate emit location_proofs for non-consenting subjects is exactly the substrate-protective case that the HUMANITY_ACCORD halt authority exists to address. The substrate's role at this primitive is mechanical opt-in enforcement; political/legal disputes route through the CC 4.2 + CC 4.5.3 takedown coordination + the HUMANITY_ACCORD `EmergencyShutdown CONSTITUTIONAL` path if necessary.

#### 4.5.9.2 `rough-only` — Rough-only is wire-format-enforced

Per [CC 2.6.6.1](part_2_the_grammar.md): `location_proof.cell_resolution ≤ 7`. H3 resolution 7 hexagons average ~5 km² edge-length — sufficient for city/borough disclosure without block/building precision. Producers attempting finer resolution have admission rejected at the substrate gate.

**This is the closure of an entire class of accidental over-share**: a malformed UI cannot publish precise location even if the client-side gating fails. The wire-format-level enforcement is the privacy primitive; UI is the second line.

Substrate emits `hard_case:location_proof_resolution_violation` ([CC 3.4.2](part_3_the_namespace.md)) on rejection so operators can observe malformed-client patterns. This is observability for operator debugging, NOT a slashing trigger — malformed producers are usually buggy clients, not attackers.

#### 4.5.9.3 `leaving` — Leaving is forward-only — the audit chain preserves the historical claim

Per [CC 2.4.1](part_2_the_grammar.md) `withdraws-isn't-retroactive` + [CC 4.5.12.1](#45121-forward-secrecy-on-member-departure--option-a-ceg-07-default) Option A forward-secrecy. When a subject withdraws their location_proof (or leaves a geographic community):

- Forward visibility evicts (consumer policy treats the subject as "no current location proof" for new admission decisions from withdrawal-time forward)
- The withdrawn `location_proof` Contribution **remains in the audit chain** — federation peers retain the historical record
- "I was in Austin from May to August" is permanent; "I am currently in Austin" is what withdraws/expiry govern

This is the cost the subject opts into when emitting the `location_proof`. Per the [CEWP](https://ciris.ai/cewp) structural-not-policy framing, the wire format does not promise to expunge historical claims — that promise would be hollow (federation peers retain copies; the substrate can mark forward-only). What the wire format DOES promise:

- **Rough-only** (CC 4.5.9.2): the historical claim is bounded to resolution ≤ 7, never finer
- **Opt-in** (CC 4.5.9.1): the historical claim exists only because the subject signed and emitted it
- **Auditability**: the subject can prove what they did or did not claim, when (the audit chain is the receipt)

#### 4.5.9.4 `documents-what-5` — What this documents

- The rough-only enforcement primitive at [CC 2.6.6.1](part_2_the_grammar.md) (resolution ≤ 7 for location_proof)
- The forward-only leave semantics at [CC 2.4.1](part_2_the_grammar.md) (withdraws-isn't-retroactive applied to location_proof)
- The opt-in admission flow at [CC 3.3.3](part_3_the_namespace.md) (location_proof signed by subject only or delegates_to proxy chain)
- The geographic-community admission composition at [CC 4.4.3.2.3](part_4_composition_governance.md) (Policy M evaluate_subkind_admission for geographic)
- The substrate-self-report observability at [CC 3.4.2](part_3_the_namespace.md) (4 hard_case prefixes)

What it does NOT do:
- Mandate H3 over alternative geospatial systems for operator-internal use (operator choice; wire format uses H3 only)
- Provide a place-name registry (communities self-name; H3 cells are the substrate-level binding)
- Define specific cell-resolution conventions for community-side `geographic_constraint` (only `location_proof` is bounded to ≤ 7; communities MAY scope themselves at any resolution per operator/founder choice)
- Codify non-geographic community subkinds (`professional` / `interest` / `local-business` / `event-attendees` / etc. are downstream-demand-driven future spec rounds)
- Address `affiliations`

### 4.5.10 `registry-hash` — Hash-database operator policy

Perceptual-hash matchers (PhotoDNA / PDQ / Project Arachnid / GIFCT hash-sharing) are pluggable per the CIRISPersist `PerceptualHashMatcher` trait. Operators choose which matcher implementations to enable; CEG governs the access-policy contract.

#### 4.5.10.1 `hash-database` — Hash-database access landscape

| Matcher | Access posture |
|---|---|
| **PDQ** (Meta, 2019) | Open — algorithm + reference hashes publicly distributed |
| **PhotoDNA** (Microsoft, 2009) | Access-gated; restricted to vetted orgs (NCMEC + select platforms); substrate operators cannot download the hash database directly |
| **Project Arachnid** (C3P, 2017) | Access-gated; API access requires C3P partnership |
| **GIFCT hash-sharing** | TVEC-focused; access via GIFCT membership |

#### 4.5.10.2 `registry-operator` — Operator path (default)

For a CIRIS substrate operator running a federation node, **the default operator path is**:

> **Self-hosted PDQ matcher against publicly-distributed reference feeds** (Microsoft Project Arachnid feed where publicly available, GIFCT-published lists where openly available). No access-governance overhead. Operator carries responsibility for index freshness.

This avoids the federation-dependency-at-substrate-protective-layer problem that option (b) (clearinghouse delegation) would introduce, and the controversy around option (c) (on-device hash-database access via OS-vended hooks, per the iOS NeuralHash 2021 incident).

#### 4.5.10.3 `future` — Future hash-coalition path (deferred; awaits CIRIS hash-coalition emergence)

A follow-up will be filed when a CIRIS hash-coalition emerges that can serve as a clearinghouse for option (b) — substrate operators delegating perceptual-hash checks to a trusted coalition peer via federation. The slot is documented; the actual coalition operator-onboarding flow is deferred.

#### 4.5.10.4 `documents-what-2` — What this documents

- The closed-set of `legal_basis` values that compose with `PerceptualHashCsam` (the only `legal_basis` value that consumes hash-match output as immediate-removal trigger; see [CC 3.3.2](part_3_the_namespace.md))
- The operator-onboarding contract: an operator running a PDQ matcher MUST register their matcher's source feeds (which hash-list source URLs they're pulling from + freshness cadence) via a `system:perceptual_hash_matcher:registered` Contribution. Composes with [CC 3.1.3](part_3_the_namespace.md) Persist substrate-self-report discipline.

What it does NOT do: prescribe which hash databases an operator MUST use. Operator choice. CEG documents the wire-format slot + the operator-onboarding contract + the recommended default; concrete matcher selection is operator policy.

### 4.5.11 `bootstrap-content` — Bootstrap-content pattern

After federation genesis, a curated batch of P5 Contributions is admitted via the CC 4.5.1 amendment flow, populating the federation's substantive content surface with high-quality ethical-framework material. **Content-neutral**: any sufficiently substantive ethical-framework source can serve. The wire format admits content via the [CC 3.1](part_3_the_namespace.md) namespace; the [CC 1.2](part_1_foundation.md) gate ensures prefix names don't import source-tradition vocabulary.

**First deployment**: the *Magnifica Humanitas* encyclical mapping at ~75-80% transparent translation rate (Cargo `ciris-response-magnifica-humanitas` repo).

**Multi-source commitment**: subsequent bootstrap batches from CARE Principles (Indigenous data governance), Buddhist economic-justice scholarship, secular humanist instruments, African philosophy of personhood work — all through the same amendment process. The framework is multi-traditional by design.

### 4.5.12 `family-self-2` — Self/family membership governance

Per [CC 3.3.6](part_3_the_namespace.md) `identity_occurrence` + [CC 3.3.4](part_3_the_namespace.md) `family` + [CC 4.4.3.4](part_4_composition_governance.md) Policy L + [CC 5.2](part_5_transport_substrate.md) structural-invisibility. The four governance decisions for self/family membership.

#### 4.5.12.1 `forward` — Forward secrecy on member departure — Option A (default)

When a member leaves a family (or an occurrence is revoked from a self-collective), the removed party retains existing `key_grant`s for historical content; the substrate stops wrapping new `key_grant`s on subsequent content. No DEK rotation; no re-encryption.

**Rationale**: consistent with [CC 2.4.1](part_2_the_grammar.md) `withdraws-isn't-retroactive` + [CC 4.5.3](#453-fast-path-takedown-coordination-ceg-03-addition-per-cirisregistry37--38) "takedown isn't a coup" + [CC 4.4.3.5.1](part_4_composition_governance.md) consent-decay-doesn't-re-encrypt. The substrate's forward-secrecy posture is uniform across consent, takedown, and membership-departure surfaces.

**Option B** (rotate-DEK on member departure; re-wrap all extant content to remaining members) is deferred. The slot is documented for a future `subject_kind: family_rotation` ceremony that operators can opt into per family; the per-`(family_id, epoch)` rotation axis would parallel the per-`(stream_id, epoch)` axis ([CC 5.1](part_5_transport_substrate.md)) — a distinct axis from the `key_grant.rotation_chain`. The ceremony envelope is downstream-demand-driven; the wire-format primitives needed are the `key_grant` wrap + Option-A re-grant on existing members (which already work today).

#### 4.5.12.2 `envelope-multi` — Multi-family membership — envelope `family_id`

One identity MAY belong to multiple families. Each family has its own DEK and its own membership roster; a `cohort_scope: family` Contribution MUST carry `family_id` ([CC 2.1](part_2_the_grammar.md) envelope field) naming which family's DEK and visibility apply. Substrate rejects family-scoped Contributions missing `family_id`.

**Rationale**: avoids cross-family DEK confusion when one identity is in N families; gives the substrate an unambiguous routing key for the `key_grant` cascade per [CC 4.4.3.4.1](part_4_composition_governance.md).

#### 4.5.12.3 `admission-self` — Self-occurrence admission — single-vouch

A new `identity_occurrence` is admitted on a signature from EITHER the root `identity_key_id` OR any currently-admitted occurrence of that identity (Signal-style "trust any device I've already onboarded"). Higher-assurance setups MAY layer requirements on `hardware_attestation` via consumer policy.

**Rationale**: matches user-intuition for self-membership ("my phone unlocks my laptop's trust posture for new devices"); avoids the operational overhead of multi-vouch for routine onboarding; the security gradient lives in the optional `hardware_attestation` field, not in the admission rule.

#### 4.5.12.4 `reservation-reserved` — Reserved-prefix substrate emissions — locked in CC 3.4.4

Per [CC 3.4.4](part_3_the_namespace.md). The four substrate-emitted membership-event prefixes (`hard_case:identity_occurrence_added:*`, `hard_case:family_membership_change:*`, `hard_case:family_consensus_protocol_change:*`, `hard_case:family_consensus_protocol_violation:*`) are reserved to `identity_type="substrate_persist"` emitters. Same discipline as the existing `system:*` substrate-self-report family.

#### 4.5.12.5 `family-admission` — Family admission — consensus_protocol (normative)

Unlike self-occurrence, family membership changes are **NOT single-vouch by default**. The family's `consensus_protocol` field governs admission. Six canonical protocols (`founder_only` / `unanimous` / `majority` / `quorum:M/N` / `weighted:{rubric}` / `custom:{family_id}`); operator vocabulary extends.

The consensus_protocol field is itself subject to amendment via the SAME protocol's rules (meta-amendment shape parallel to [CC 4.5.1.2](#4512-meta-amendment--entrenchment)) UNLESS the family is `consensus_protocol_entrenched: true`. Entrenched families reject amendments at the substrate gate; replacement requires the family's documented out-of-band ceremony.

**Rationale**: families are multi-party collectives where membership changes have real consequences (admit-new-member = grant DEK access to all extant cohort_scope: family content). The consensus_protocol gives the family explicit governance over its own boundary. Self-amendment lets families evolve their governance as they grow; entrenchment lets safety-critical families lock the boundary against any internal authority.

#### 4.5.12.6 `documents-what-4` — What this documents

- The wire-format primitives that compose into self/family membership ([CC 3.3.6](part_3_the_namespace.md) + [CC 3.3.4](part_3_the_namespace.md))
- The structural-invisibility discipline at [CC 5.2](part_5_transport_substrate.md) (cohort_scope: self/family suppresses holds_bytes:*)
- The at-rest encryption flow composition at [CC 4.4.3.4](part_4_composition_governance.md) Policy L
- The consensus_protocol vocabulary (canonical kinds; open-vocab extension)
- HUMANITY_ACCORD as the canonical entrenched-`family` instance at [CC 4.2.3](part_4_composition_governance.md)

What it does NOT do:
- Lock the consensus_protocol vocabulary (open vocab; canonical kinds named for ecosystem coordination)
- Provide a key-rotation ceremony for Option B forward secrecy (deferred to downstream-demand-driven future release)
- Prescribe per-family entrenchment policy (operator/family choice)
- Document the at-rest encryption flow details (substrate-side; persist spec)

### 4.5.13 `reverse-quorum` — Reverse-quorum governance — presence is authority, absence forfeits it

**The general pattern.** [CC 4.2.6](part_4_composition_governance.md) is not a one-off kill-switch rule; it is the federation's **general governance shape**, and this section ratifies it as such. **Presence is authority, absence forfeits it, a timer decides.** A decision opens a bounded window; whoever shows up and signs is counted; whoever stays absent is simply *not in the denominator* and cannot block by being gone. The [CC 4.2.6](part_4_composition_governance.md) accord kill-switch is the **constitutional instance** of this pattern (the live set governs the halt-authority); **community-scope moderation is its first community instance** (the live community governs its own content). One mechanism, two scopes — the accord over humanity's off-switch, moderation over a group's content.

**Roles — moderator (required), steward (optional super-mod).** A community is **required** to have a named **moderator** — the [CC 4.5.4](part_4_composition_governance.md) `moderate`-duty holder — and that is the *only* required role: the moderator is the fast-path decision-maker. A community **MAY** additionally name **one or more stewards** — the super-mod tier, steward-bound per [CC 3.2](part_3_the_namespace.md), who appoint and oversee moderators; **a steward may add further stewards**. At creation the creator chooses their own role: **steward + moderator**, or **moderator only**. **No quorum is ever imposed *on* a moderator or a steward** — unilateral accountable authority within scope is what each role means; either resolves an action by a **single signature**.

**The mechanism — propose, 48 h window, moderator or steward acts, community falls back.** **Anyone MAY propose a moderation action** — a report, a takedown request, a keep-or-remove question — by the [CC 4.5.5](part_4_composition_governance.md) open-labeling path (a report→`scores` Contribution against the target). The proposal opens a **48-hour participation window**. Two ways it resolves:

1. **A moderator or steward acts unilaterally.** The community's **moderator** (the required `moderate`-duty holder, [CC 4.5.4](part_4_composition_governance.md)) — or any **steward**, where the community has named one — resolves the action by a **single signature**, at any point in the window. This is the fast path, and the moderation analogue of the [CC 4.2.6](part_4_composition_governance.md) **fire-floor-of-1**: a single accountable party acts, and the absence of others never blocks them.
2. **On their absence, the community vote carries.** If **no moderator or steward acts within the 48 h window**, the proposal is tallied by **live-majority vote over the community's live members** — the [CC 4.2.6](part_4_composition_governance.md) live quorum, generalized: presence asserts (a member signs a fresh proof-of-presence + vote over the proposal nonce, entering the live set `L`), absence never blocks (a silent member is not in the denominator), and the tally is taken over **who shows up**. The community **routes around** an absent moderator.

The reverse-quorum is a **fallback for moderator/steward absence, never a check on them.** The 48 h figure is tuned so that a **present** moderator always has time to act unilaterally; the community fallback fires **only** on genuine absence.

**No-moderator recovery — 48 h, with a 24 h open candidacy phase.** A community must never sit without a moderator. When the moderator lapses, the substrate first attempts [CC 4.5.4](part_4_composition_governance.md) **merit auto-promotion** (instant, when an eligible member exists). If none is auto-promotable, the community enters a **48-hour recovery**: a **24-hour open candidacy phase** in which **any member MAY propose themselves** as moderator — open to all, so everyone has 24 h to start a candidacy — followed by selection over the live members (a steward, where one exists, MAY instead appoint a moderator directly at any point). A community that reaches the end of the 48 h with no named moderator **fails-secure** — it MUST NOT federate at moderated capability ([CC 4.5.4](part_4_composition_governance.md)).

**Optional moderator quorum (community config).** Unilateral moderator action is the *default*. A community **MAY** instead require a **moderator quorum** for an action to carry — either **full** (every named moderator must sign) or **live-within-window** (a live-quorum of the moderators who respond within a stated period — the reverse-quorum applied to the moderator set itself). This rides the community's existing `consensus_protocol` ([CC 4.4.3.2](part_4_composition_governance.md)) applied to the `moderate` duty; it **tightens the fast path** without weakening the community-vote fallback, which still carries on total moderator/steward absence. The choice is the community's to make and to change (a steward, or the community vote, may set it).

**Protective default — a harm report defaults to removal.** For a takedown / harm report, the window's **default outcome is removal.** Content survives **only** by an affirmative, on-record **keep-decision**: either **(A)** a steward's unilateral *approve-to-keep* signature, **or** **(B)** a live-majority *vote-to-keep*. **Passive survival is impossible** — doing nothing within the window removes the content. Therefore **surviving harmful content is always attributable**: the steward who approved it, or the majority who voted to keep it, are cryptographically on record. *A community in which reported abuse survives has self-identified* — by name, by signature.

**Infohazard consent gate — no passive exposure.** When the live-majority vote **favors removal/moderation but the content is retained** (flagged, not hard-removed), it is **auto-hidden behind an active interstitial** — *"I consent to view this material reported as a potential infohazard."* Clicking it **publishes a [CC 3.3.1](part_3_the_namespace.md) `consent:*` attestation** (`consent:state:granted` + a `consent:scope:view` qualifier, viewer-side, attributable within scope) — so **passive exposure is impossible here too**: every viewing is an affirmative, signed act by a named identity. This **rides the existing `consent:*` family + a [CC 3.3.12](part_3_the_namespace.md) `content_class:{class}` flag** (`content_class:infohazard` / `content_class:reported`); **no new wire shape** — it is the [CC 4.5.5](part_4_composition_governance.md) `content_class` gate composed with the [CC 3.3.1](part_3_the_namespace.md) consent primitive.

**The outcome ladder — every transition an attributable act.** A graduated, fully-attributable ladder; nobody passively flags, keeps, or views harmful content:

| Outcome | Trigger | Who is cryptographically on record |
|---|---|---|
| **Hard-removal** | CSAM perceptual-hash tripwire ([CC 4.5.3](part_4_composition_governance.md) `PerceptualHashCsam`) / takedown / **report undefended** (no keep-decision in the window) | the removal action ([CC 4.5.5](part_4_composition_governance.md) `takedown_notice`); content does not survive |
| **Consent-gated** (retained, auto-hidden) | live-majority **flagged-but-retained** | **each viewer** — every interstitial click publishes a `consent:*` attestation |
| **Kept-visible** | steward **approve-to-keep** (A) **or** live-majority **vote-to-keep** (B) | **the steward** who approved, or **the majority** who voted to keep |

**Single-point warning + inactive forfeiture.** A community with **only one moderator and no steward MUST be warned to add a second** moderator or a steward — a lone authority is a single point of capture and of failure. **Inactive moderators and stewards lose their standing:** silence past the community's freshness window **lapses the duty**, and merit auto-promotion + the no-moderator recovery above **reconstitute authority** — the highest-`moderation_track_record` live member is auto-granted the `moderate` duty. **No community is ever hostage to an absent moderator or steward.**

**What the protocol guarantees — structure, not behavior (the M-1 framing).** The protocol guarantees the **structure**: **default-remove, attributable-keep, attributable-view.** It does **not** guarantee the *behavior* of a community that **affirmatively chooses harm** — a steward may sign to keep abuse, a majority may vote to keep it, and a viewer may consent to view it. What the protocol forecloses is doing any of these **silently**: every transition up the ladder — flag, keep, view — is an **affirmative, attributable act by a named identity**. Per [CC 4.2](part_4_composition_governance.md) M-1, the federation's promise here is **revocability and accountability**, not behavioral control: a community that harbors harm is on the record as having done so, and that record is what justice composes over.

**Consistency — member-reporting, not substrate scanning.** This is **member-reporting + reverse-quorum adjudication**, *not* substrate scanning of private content. CEG **refuses client-side scanning** ([CC 4.5.7](part_4_composition_governance.md)): detection runs only at enabled groups' publish/share seam, never over [CC 5.2](part_5_transport_substrate.md) self/family private content. The principle is unchanged across the federation — **anonymity to outsiders, accountability to insiders** — applied here with teeth on harm: the structure makes silent survival, silent keeping, and silent viewing impossible, while leaving private content unscanned.

**The symmetry with the accord (explicit).** This is [CC 4.2.6](part_4_composition_governance.md) read at community scope, and the two halves mirror exactly. In the accord, a **lone survivor fires** and the **live set reconstitutes the roster** when holders vanish; in moderation, a **lone steward acts** and the **live community reconstitutes governance** when stewards vanish. Fire-floor-of-1 ↔ single-steward signature; live-quorum-over-`L` ↔ live-majority-over-present-members; Enoch-Arden return ↔ merit re-auto-promotion on a lapsed steward's silence. **Presence is authority, absence forfeits it, a timer decides** — at every scope.

**1+4 preserved.** The proposal/window/tally rides the generalized [CC 4.2.6](part_4_composition_governance.md) participation shape + the [CC 4.5.5](part_4_composition_governance.md) action primitives (`moderation:*` / `takedown_notice` / `reconsideration:*`); the consent gate rides the existing [CC 3.3.1](part_3_the_namespace.md) `consent:*` family + the [CC 3.3.12](part_3_the_namespace.md) `content_class` flag. **No new structural primitive.**
