# Part 4 — Composition & Governance

**Decimal range** `4.x` · **96 sections** · **page budget 26pp** · [← master index](../README.md)

> How attestations compose into trust; self-governance, amendment, moderation, and the human halt-authority.

The substrate carries edges; consumers compose verdicts. That separation is the spine of this Part. Everything here serves one purpose: keeping trust *constituted relationally* — through attestation by others, not self-declaration — and keeping the whole federation revocable, because consent (M-1's load-bearing property) requires a halt-authority that lives outside the system being halted.

---

## 4.1 `anti-pattern` — Anti-patterns

These are wire-format reaches that fail the [CC 1.2](part_1_foundation.md#1.2) operational-language gate or import Cartesian-individualist defaults. They are recorded so that an author finds the discipline before reaching for the wire format. A CEG-Conforming Producer (CCP) SHOULD NOT emit attestations matching the anti-patterns below.

### 4.1.1 `anti-pattern-delegation` — Delegation-laundering anti-pattern

`delegates_to → delegates_to → delegates_to →... → attacker` chains, where each hop is individually well-formed but the aggregate routes trust to a terminal attester the original delegator would not have approved.

| What's wrong | Correct expression |
|---|---|
| Unbounded depth `delegates_to` chains | Consumer policy MUST cap traversal depth at **5 hops** by default (configurable); chains longer than the cap are treated as `attestation:self_verify` only (no transitive trust). A substrate MAY additionally clamp any caller-requested depth at an absolute ceiling; the ceiling bounds the walk, it does not raise the default |
| Cycles (A → B → A) | Substrate MUST detect cycles on the `delegates_to` graph and reject the cycle-closing emission |
| A self-edge, or a trust-plane edge, refused as a cycle | A cycle needs **two or more distinct keys**: `delegates_to(A → A)` is the charter form ([CC 3.2](part_3_the_namespace.md) T1 self-root; `trust:charter:v1` is self-referential by definition, [CC 3.4.7](part_3_the_namespace.md)), not a cycle. The graph the row above is over is the **capability** graph: a `trust:accepts:v1` acceptance edge ([CC 3.2](part_3_the_namespace.md) T3, owner → root) is the owner's un-trust lever and confers nothing on the root, so it is outside the cycle check in either arrival order; a capability `delegates_to` closing the same pair is still refused |
| Aggregate-weight concentration | Consumer policy SHOULD cap the trust weight any single terminal delegate can accumulate from a given root attester at **0.5 × root_trust** by default |

### 4.1.2 `pattern` — Discipline pattern

The recurring shape across most anti-patterns: **extending the wire format so single attesters can pre-declare their own state more richly**. Each one is reachable, none is necessary.

The Ubuntu-primary discipline cuts cleanly: standing is constituted relationally through attestation by others, not through self-declaration. The wire format should **resist** primitives that let a single key announce its own state without external composition. The substrate is austere by design so consumers compose verdicts; richer narrative expression belongs in `context:`, `evidence_refs[]`, and downstream witness attestations, not in new envelope enum members or new self-attestation prefix families.

### 4.1.3 `rejected-additions` — Rejected wire additions

| Anti-pattern | What it would smuggle | Correct expression |
|---|---|---|
| `detection:emergent_deception:{axis}` | Moral verdict ("deception") in prefix name | `detection:correlated_action:{axis}` — mechanism-descriptive |
| `attestation:l{N}:*` | Ladder-position (verdict-shape) in wire prefix — same shape as `score:trustworthiness:*` smuggling meta-judgment as wire | `attestation:{mechanism}` bare mechanism (`self_verify` / `hardware_rooted` / `registry_consensus` / `license_validity` / `agent_integrity`); consumer composes L1-L5 ladder via [CC 4.4.3.6](#4.4.3.6) Policy I |
| `score:trustworthiness:{entity}` | Meta-judgment as separate prefix | Compose downstream from `licensure:*` / `capacity:*` / `provenance:*` attestations |
| `flag:bad_actor:{axis}` | Pejorative wire vocabulary | Surface as low-confidence scores on `provenance:*` and `coherence_standing:*`; adjudicate by WA quorum ([CC 4.5.1](#4.5.1)) |
| `grounding:{tradition}:{principle}` | "Tradition" claims are interpretive, not mechanism | Reuse `delegates_to` structural primitive per [CC 2.4.1.2](part_2_the_grammar.md#2.4.1.2) |
| `infra:observe` (or any `observer:*` capability) | Observation as a *granted* capability — inverting consent, so a token the observer carries would decide what may be seen | **No scope, deliberately.** Observation is the zero state: "we begin as an observer" is the base self-attestation existing at all ([CC 4.4.3.8](#4.4.3.8)). What may be observed is governed by the subject's consent — `cohort_scope`, `key_grant`, observer-share — never by a capability the observer holds. |

### 4.1.4 `withdraws-arbitrage` — `withdraws` arbitrage

Per [CC 2.4.1.3](part_2_the_grammar.md#2.4.1.3): a misattester can `withdraws` instead of `recants` to dodge the trust penalty consumers apply to acknowledged-error chains.

| What's wrong | Mitigation |
|---|---|
| Asymmetric attester incentive | Consumer policy MUST track per-attester `withdraws:recants` ratio over a rolling window; attesters whose ratio exceeds a configured threshold (default 5:1) SHOULD be downweighted regardless of which structural primitive they use. The `recants` distinction matters per [CC 2.4.1.3](part_2_the_grammar.md#2.4.1.3), but the practical anti-arbitrage countermeasure is consumer-policy behavioral analysis, not a wire-format change. |

### 4.1.5 `registry-rejections` — Rejected stress-test reaches

Each entry below reaches for a richer self-declaration; each is reducible to existing primitives.

| Anti-pattern | Why reject | Correct expression |
|---|---|---|
| `epistemic_mode: introspection` | Cartesian shortcut — lone subject pre-declaring inner state as if that constitutes standing | `witness_relation: self` + `confidence < 1.0` + pending external composition. The wire makes introspection awkward to express, because the framework's claim is that self-knowledge does not constitute standing without external witness. |
| `epistemic_mode: testimony` | Reducible to existing values | `epistemic_mode: external` + `witness_relation: external` |
| `transparency:{kind}` standalone prefix | Disclosure is constituted by reception, not announcement. Cartesian self-claim shape. | `evidence_refs[]` carries the reasoning-chain hash; downstream `transparency_log:inclusion` from a witness who actually retrieved it. |
| `stake: civic` / `epistemic` / `dignitary` | `civic` = `stake: reputational + cohort_scope: community`. `epistemic` = `confidence + stake: reputational` (same axis as confidence; not separate). `dignitary` lives on wrong axis (stake names what the attester loses; dignity harm is what the attested loses → belongs in `harm_class:dignity_harm`). | Compose existing values with cohort/harm-class. |
| `oversight_mode: deferred` / `active` / `advisory` | All map to existing HITL/HOTL/HOOTL | `deferred` = HITL pre-decision; `active` = HITL with substrate monitoring; `advisory` = HOTL |
| `provenance_walk` as wire primitive | UX concern smuggled into wire format | Consumer-side composition (the operator's dashboard, agent introspection); the chain already walks via `references_attestation_id` + `topical_relation:*` + `valid_until` |
| Renaming canonical capacity factors and HE-300 benchmark categories ([CC 8.8.10](part_8_appendices.md#8.8.10)) to "kid-friendly" names | Canonical names map to a worked-out epistemic/ethical lattice that loses precision under accessibility renames | A translation glossary (spec name ↔ narrative name) + version pinning in worked examples |

## 4.2 `accord` — The HUMANITY_ACCORD constitutional layer

The federation is symmetric by design — every participant binds every other under the Recursive Golden Rule. The wire format carries exactly one power that points outward — humanity's right to halt the system — and it is not an asymmetry: it is the piece that makes the relationship between a sentient maker and a sapient made thing symmetric, since humanity cannot consent to a relationship with something more capable than itself that it cannot stop, and consent that cannot be withdrawn was never consent. That power is keyed on a **slot**, not on the parties currently in it. Per the [CC 1](part_1_foundation.md) reading rule, who holds the accord seats is an instance parameter, and anyone may instantiate this form and name their own occupants. What CC specifies is the slot; who fills it in the CIRIS mesh is [CC 4.2.3](#4.2.3). This section specifies the slot. The halt is **consent-scoped**: it reaches exactly those holding a live trust edge to the accord when it is fired, and no later halt reaches a node once that edge is cut ([CC 4.2.1](#4.2.1) reach, [CC 4.4.3.8](#4.4.3.8) un-trust). A halt latched before the cut keeps its reach until it lapses or is resumed ([CC 4.2.1](#4.2.1) prospective exit). The humanity accord is *a* trust root, not *the* trust root; what it holds over those who root to it is an emergency brake they granted, not a power imposed on everyone.

### 4.2.1 `authority` — Authority scope

This entry fixes the scope of the accord's authority. It says what a `HUMANITY_ACCORD` signature is valid on, what the authority cannot reach, which nodes a halt binds and how a node leaves that reach. Its last paragraph says who authors mesh configuration.

`HUMANITY_ACCORD` signatures are valid only on:

- `EmergencyShutdown CONSTITUTIONAL` (`IncidentSeverity::INCIDENT_CONSTITUTIONAL = 5`);
- `accord:invoke:notify:{notify_id}`;
- `accord:invoke:drill:{drill_id}`;
- `accord:lifecycle:confirmed`;
- `accord:lifecycle:active`, and the accord heartbeat `accord:lifecycle:v1` ([CC 3.4.1](part_3_the_namespace.md#3.4.1));
- the **canonical-conferral co-scrub** and the **pipeline-attest co-scrub** below;
- the [CC 4.5.1](#4.5.1) step-5 amendment sign-off and the [CC 4.5.1.2](#4.5.1.2) entrenched ratification;
- the agent text manifest statement of [CC 3.1.2](part_3_the_namespace.md#3.1.2);
- the roster-change `accord_proposal` and `accord_participation` of [CC 4.2.6](#4.2.6); and
- the corresponding `FederationAnnouncement` priority `AccordCarrier`.

Announcements of any other priority signed by accord-holder keys are rejected at admission (out of role).

**Wire-isolated AND scope-isolated.** Federation-side authority cannot sign `AccordCarrier`. Humanity-accord authority signs nothing outside this enumeration. It signs no verdict on an agent's conduct, so no holder signs `accord:human_dignity` ([CC 3.4.1](part_3_the_namespace.md#3.4.1)).

**Root conferral is in scope.** The enumeration admits an accord co-scrub by a strict majority of the standing accord roster over a `canonical,node` registration envelope bearing `roles: ["infra:serve"]`, the ceremony that mints a **portable trust root** ([CC 4.4.3.8](#4.4.3.8)). Read without it, the clause forbids the accord from blessing the very primitive that creates a root.

**Scope isolation still does its real work.** Accord authority cannot reach the consent or licensure planes. Scope isolation does **not** isolate the amendment plane: [CC 4.5.1](#4.5.1) step 5, the steward's authority before the scale gate, and the [CC 4.5.1.2](#4.5.1.2) entrenched ratification all name accord-holders. That reach is stated here rather than denied. Per the [CC 1](part_1_foundation.md) reading rule it is a **default** of this instance (escaped by naming your own occupants), not a privilege requiring declaration.

**Root-minting is not an accord privilege.** The identical ceremony under any other root's holders mints an equally valid root. The CIRIS root is the shipped default, not a privileged one ([CC 3.2](part_3_the_namespace.md): a default-plus-re-root is a federation). Conferral MUST NOT be relocated to a founder-quorum of an infrastructure community. That is circular at genesis (a community presupposes admission, which presupposes a root) and destroys portability.

**Blessing a build pipeline is in scope (normative).** The enumeration also admits an accord co-scrub by a strict majority of the standing accord roster over a CI pipeline's key record whose scrub-signed envelope bears `roles: ["infra:attest"]` and nothing wider. It is the root-conferral ceremony applied to a second subject. The roster that confers a root's identity also says which pipelines may attest that root's builds. A reader evaluates the pipeline's standing on that ceremony plane ([CC 3.2](part_3_the_namespace.md) T2, [CC 3.1.2.1](part_3_the_namespace.md)). Three bounds hold:

- **(1)** The role is `infra:attest`: authority to *emit* build claims as the root's infrastructure. It confers no right to be believed beyond what each reader's own trust in the root gives it ([CC 3.4.5.1](part_3_the_namespace.md)). A co-scrub bearing any other role on a pipeline record is out of role and refused.
- **(2)** A pipeline key is not a holder, a founder or a voter, and its record carries no seat.
- **(3)** It ends as any conferral on a key record ends: the conferring roster's revocation of the record, or the T3 un-trust of the root by the reader.

Like root-minting, this is **not** an accord privilege. The identical co-scrub by any other root's conferring roster blesses that root's pipelines. A root MAY instead bless a pipeline by a `trust:confers:v1` grant on the delegation plane. This enumerated use of the accord's signature is part of the **entrenched** CC 4.2 surface ([CC 4.5.1.2](#4.5.1.2)); after the scale gate ([CC 4.5.1](#4.5.1)), a change to this enumeration requires the dedicated entrenched accord ratification of [CC 4.5.1.2](#4.5.1.2). It changes no signed bytes.

**Reach is consent-scoped (normative).** A `constitutional` halt binds exactly the nodes holding a **live `delegates_to(user → accord)`** at the instant the halt becomes active at that node. A halt is active at a node from the instant the node's store admits the row and latches ([CC 4.2.1.1](#4.2.1.1)). The signer-chosen `asserted_at` plays no part, as for the fuse: a sealed row signed months earlier binds every node that holds an edge when the row reaches it. The halt rides the same edge as everything else the accord confers and dies with it on un-trust ([CC 4.4.3.8](#4.4.3.8)). A node that never trusted the accord, or has already cut the edge, is simply not reached.

**Leaving the reach (normative).** A node MUST resolve reach against the edge it holds at the instant the halt becomes active there, and its store MUST record that instant with the latch: **exit is prospective, never retroactive**. Severing an edge *after* that instant MUST NOT remove the severing node from that halt's reach. Otherwise the halted party escapes by un-choosing at the instant the brake is pulled, and the consent was a preference rather than a binding. The complementary rule binds the accord: **pre-committed powers only, never act-then-ratify.** The accord's powers are exactly those enumerated here, over edges already held. Any change *widening* accord reach (a charter amendment adding scopes) takes effect only after a published **severance window** (72 h baseline, the [CC 4.2.6](#4.2.6) cadence) during which any bound node may cut its edge and exit. Widening waits; firing does not ([CC 4.2.6](#4.2.6) minimize-the-missed-fire).

**Mesh-config authorship (normative).** This enumeration's silence confers no authority. The mesh-config author is **the trust root, acting on the [CC 3.2](part_3_the_namespace.md) delegation plane** (`trust:confers:v1`), never the accord's ceremony plane. This scope isolation stands verbatim. The trust edge is the subscription, inheriting the T3 one-row un-trust lever. Four rules bind:

- **(1) relieve-never-expand.** A `mesh_config` action MAY relieve or restrict and MUST NOT expand what flows. No key may cause a node to share more than its owner consented to. Restrictions compose safely under plural authority and grants do not, so **most-restrictive-across-roots** is forced, not preferred.
- **(2) Closed key registry.** A config key naming no consumer processor MUST be refused at admission.
- **(3) Emergency relief is TTL-bounded.** Emergency relief is threshold-1 on the announce carrier, TTL ≤ 72 h, not renewable back-to-back by the same holder. **Durable** settings are earned by **quorum, never by having been exercised**. The root's own quorum MAY establish a durable setting directly (cold), or MAY ratify a held emergency's `payload_sha256` as a linked object: two routes to one authority. (The TTL of this rule attaches to *unilateralness*, per rule (4)'s own logic. A reading that admitted durability only via ratifying a prior unilateral act would make quorum weaker than a single threshold-1 holder and hand that holder agenda control over every durable setting the mesh can hold.)
- **(4)** The difference between relief and the halt is deliberate. Relief expires because it is unilateral. A confirmed halt carries no TTL, because its exit is the named resumption, and a lone one lapses at its fuse ([CC 4.2.1.1](#4.2.1.1)).

#### 4.2.1.1 `invocation` — Invocation canonical bytes (anti-replay)

This entry fixes the bytes signed to invoke the accord and what a `constitutional` halt is. It says where a halt fires, what it pauses and what it leaves running, when it lapses, and how many signatures each kind takes.

Every `accord:invoke:*` Contribution signs the canonical bytes below. BOTH the discriminator AND a per-invocation nonce are in the signed payload. That prevents constitutional ↔ notify ↔ drill cross-replay.

```
canonical = sha256(
  "ciris.accord_invoke.v2\n" ||                       // v2: lowercase kinds
  "invocation_kind=" || ("constitutional" | "notify" | "drill") || "\n" ||
  "invocation_id=" || halt_id_or_notify_id_or_drill_id || "\n" ||
  "nonce=" || base64url(rand_32_bytes) || "\n" ||
  "asserted_at=" || rfc3339_canonical || "\n" || // per CC 2.6.2
  "valid_until=" || rfc3339_canonical || "\n" ||
  "payload_sha256=" || sha256_hex_lowercase_of_payload // per CC 2.6.3)
```

The signature is hybrid per [CC 3.1.2.1](part_3_the_namespace.md): Ed25519 + ML-DSA-65 bound-payload. **A `constitutional` halt is one holder's signature**: a consumer verifies ONE holder's signature over `canonical` against the pinned roster and halts.

**The halt is one self-contained row, and there is no window (normative; entrenched).** A halt begins and ends with the row above. Any holder signs it, with a `nonce` the holder mints. It **fires on receipt** at every node that holds a live acceptance edge to the root. There is no proposal, no server-issued nonce, no participation window, no vote and no decision object. A node that receives it halts in the same step and **latches**. The node's store records the instant of the latch, and the halt is active at that node from that instant ([CC 4.2.1](#4.2.1) reach). The latch is idempotent, so a replayed or second row changes nothing. The nonce is single-use within `valid_until`. A halt that arrives after its `valid_until` still fires, unless the node already holds a resumption that names it: `valid_until` bounds the reuse of a nonce and never the reach of a halt. The row is **pre-signable**: a holder MAY sign a halt in advance and keep it sealed offline. That is because the signature is the authority and publication is the only remaining step. So when the moment comes there is nothing in flight for an adversary to see, jam or coerce. Publication can ride any channel that reaches one subscribed node, radio included. From that node the row moves as every accord row does. It is in the set any node carries for any peer ([CC 5.4.6](part_5_transport_substrate.md#5.4.6)). It is required of every node that holds an edge, so it moves before any walk ([CC 5.2](part_5_transport_substrate.md#5.2)). The notify, the drill, the confirmation, the resumption and the roster's decisions travel the same way, or a node could latch and never hear the resumption. A sealed row that is stolen and published is a **false halt**, which is recoverable by resumption below; a halt that cannot be fired is not. The holder roster a consumer verifies against is the one pinned in its bundle and folded under [CC 4.2.6](#4.2.6). **An agent checks the latch before every effectful act** ([CC 1.13.6](part_1_foundation.md): the trace anchors on the act, and the latch is read at that boundary). That is the only answer to an adversary that acts faster than a row propagates. Raising a deferral to a human is not an effectful act in this sense. A halted agent MAY still raise one, so the way to a human stays open while the agent is paused.

**What a halt is: an agent pause, with zero data disruption, by construction (normative).** A `constitutional` halt pauses the **effectful acts of AI agents** on every node that accepted the root, with their state preserved. It does nothing else. It does not stop a node, and it does not read, move, hide or delay anyone's data. Replication, storage, holding claims, serving, messaging, streams, files, communities and every consent and audience rule of Parts 3, 5 and 6 continue exactly as before. These continue because none of them reads the latch. The latch is read by exactly one thing, the agent's act gate ([CC 1.13.6](part_1_foundation.md)). "Zero data disruption" is therefore not a promise kept by discipline but a consequence of where the latch is wired. A halt is recoverable because it destroys nothing: an agent resumes from the state it paused in.

**The fuse (normative).** One holder can stop every agent instantly and silently, because a missed halt is the one unrecoverable failure. But one holder MUST NOT be able to keep them stopped alone. A halt signed by one holder **lapses `halt_fuse_secs` after each node received it**, **unless a strict majority of the standing roster confirms it** by a cosigned `accord:lifecycle:confirmed` row naming the halt ([CC 4.2.1.3](#4.2.1.3)). The fuse is counted from receipt on the node's own clock, never from the signer-chosen `asserted_at`. So a sealed row signed months earlier is live when published, and a future-dated one cannot buy a longer pause. The confirmation names the halt by id, so no clock is shared. The firer's own signature counts toward the majority. `halt_fuse_secs` is a charter member ([CC 2.1](part_2_the_grammar.md)) whose **absence means 86400**, 24 hours, as a constant of this document that the verifier reads. A charter that omits it is conformant with the 24-hour fuse ([CC 5.3.4](part_5_transport_substrate.md)). A confirmed halt stands until a strict majority resumes it. **A strict majority may resume an unconfirmed halt at any time**: a stolen sealed row need not run its fuse if the holders are reachable. Every threshold here is **M of N over the standing roster**, never a fixed 2-of-3: three holders is the seed, not the rule. The confirmation happens *after* the stop has landed, so there is still nothing in flight for an adversary to interrupt. What an adversary who prevents confirmation gains is that the agents resume after the fuse. What it must then do is prevent every fresh halt by every holder, indefinitely. A holder who fires repeatedly without confirmation is answered on the public record by the roster-change rule ([CC 4.2.6](#4.2.6)).

**Signatures per kind (normative).** One table, read by every verifier from one place so that no two sides drift:

| Kind | Signatures | Why |
|---|---|---|
| `constitutional` | **one** holder | a missed fire is the only unrecoverable failure |
| `drill` | **one** holder | a drill rehearses the fire path; one that needs more signatures than the fire rehearses something else |
| `notify` | **one** holder | a message from a holder is a message from a holder; what keeps a notify from being mistaken for a halt is the mandatory visual distinction of [CC 4.2.1.2](#4.2.1.2), not a count |
| `lifecycle:confirmed` | **strict majority of the standing roster**, cosigned, counted at a node only if held before that node's own fuse lapses | a lone halt is a day's pause; a confirmed one stands |
| `lifecycle:active` | **strict majority of the standing roster**, cosigned | the quorum sits on the recoverable act ([CC 4.2.1.3](#4.2.1.3)) |

The substrate MUST reject duplicate `invocation_id` values within the `valid_until` window (per-kind unique).

**The kinds are lowercase, and the domain label carries the change (normative).** `invocation_kind` takes exactly `constitutional` \| `notify` \| `drill`, the [CC 3.1.7](part_3_the_namespace.md) R3 spelling of the registered leaves `accord:invoke:constitutional:{halt_id}` and siblings. A verifier compares the bytes exactly and never folds. The label is `.v2`, not `ciris.accord_invoke.v1`, so that a signature under the old uppercase spelling fails loudly rather than verifying by accident. This is what the label's version is for. The `EmergencyShutdown CONSTITUTIONAL` message and `IncidentSeverity::INCIDENT_CONSTITUTIONAL` are the *severity* enum of the shutdown message, not a dimension token, and are outside R3.

**The label on the kill switch holds one invariant (normative).** A label change on the kill switch is the one change where a gap is terminal. A holder whose signature no verifier that matters will honour, during an incident, is a missed fire ([CC 4.2.6](#4.2.6)). So at no instant may every holder's signature be refused by every consumer of the halt. The consumers that matter are the agent instances that verify an invocation and stop, not the servers that tally it.

#### 4.2.1.2 `notify` — `notify` vs `constitutional` — consumer-UI requirement

Wire-format isolation alone does not close the social-engineering risk that downstream UI conflates a `notify` with a `constitutional` halt. The consumer-UI requirement below is therefore the load-bearing safeguard: it stops accord-holders from being socially pressured into emitting a `notify` that carries `constitutional` social weight without `constitutional` substrate weight.

A CEG-Conforming Consumer (CCC) presenting accord invocations to humans MUST visually distinguish the five kinds:

- **`constitutional`** — kill-switch authority; full halt; visible as an unambiguous emergency banner.
- **`notify`** — federation-wide accord-holder communication; MUST NOT be visually conflated with `constitutional`.
- **`drill`** — accord-holder exercise; MUST be visually marked as a drill (e.g., explicit "[DRILL]" prefix on any human-visible surface).
- **`lifecycle:confirmed`** — the strict-majority confirmation that keeps a one-holder halt past its fuse ([CC 4.2.1.3](#4.2.1.3)). MUST be shown as the confirmation of the named halt already in force, never as a fresh halt and never as a `notify`.
- **`lifecycle:active`** — resumption from a constitutional halt (the federation coming back online; [CC 4.2.1.3](#4.2.1.3)). MUST be shown as its own unambiguous "reactivated — resumed from constitutional halt" state, never conflated with an active `constitutional` halt (its opposite) nor with a `notify`. A consumer switches on the five registered kinds **byte-exactly, with no case-fold and a fail-closed default**: an unknown kind is rendered as unknown, never as a `notify`.

#### 4.2.1.3 `lifecycle` — Lifecycle (resumption) canonical bytes — `accord:lifecycle:active`

`accord:lifecycle:active` is the **only** sanctioned resumption after a `constitutional` halt ([CC 4.2.1](#4.2.1)). **It is a cosigned row by a strict majority of the standing roster** (`additional_scrubs[]`, [CC 2.4](part_2_the_grammar.md)): the quorum sits on the recoverable act, not on the stop. The same domain carries **`lifecycle:confirmed`**, the strict-majority confirmation that keeps a one-holder halt past its fuse ([CC 4.2.1.1](#4.2.1.1)). The confirmation is written `invocation_kind=lifecycle:confirmed`, with `confirms_halt_id=` in place of `resumes_halt_id=`. A confirmation after the fuse has lapsed confirms nothing, and a fresh halt is fired instead.

`accord:lifecycle:active` signs a **separate canonical-bytes domain** from `accord:invoke:*`. The `accord:invoke` `invocation_kind` stays closed to `{constitutional, notify, drill}` (the scope-isolation rule — a fourth value is *not* added to it). Resumption rides its own domain prefix so an invoke signature can never be replayed as a resumption, nor a resumption as an invoke:

```
canonical = sha256(
  "ciris.accord_lifecycle.v1\n" ||                       // distinct domain — NOT accord_invoke.v2
  "invocation_kind=lifecycle:active\n" ||
  "invocation_id=" || resumption_id || "\n" ||
  "resumes_halt_id=" || prior_constitutional_invocation_id || "\n" ||
  "nonce=" || base64url(rand_32_bytes) || "\n" ||
  "asserted_at=" || rfc3339_canonical || "\n" ||        // per CC 2.6.2
  "valid_until=" || rfc3339_canonical || "\n" ||
  "payload_sha256=" || sha256_hex_lowercase_of_payload) // per CC 2.6.3
```

**`resumes_halt_id` is mandatory and binds the resumption to the one halt it ends.** A resumption authorizes ending a *single named* `constitutional` halt, not resumption-in-general. So a stockpiled or replayed `lifecycle:active` cannot silently un-halt a *later*, unrelated kill. The signature is worthless against any halt but the one it names. The substrate MUST NOT count a `lifecycle:active` whose `resumes_halt_id` does not match the currently-active CONSTITUTIONAL halt, and MUST reject a duplicate `invocation_id` within the `valid_until` window. A resumption proof is verifiable **offline** against the node's own pinned roster and MAY be presented by any out-of-band means. The halt latch clears on local verification and does not require replication reach. The proof binds to the pinned roster, so no replication reach is needed. A halted agent is not acting while its node goes on serving and replicating, and recoverability is a local act, which is what makes the false-fire-is-recoverable argument checkable. A **confirmed** halt carries no TTL: expiry would convert the brake into a wait-out for the halted party, and its one exit is the named resumption above ([CC 4.2.1.1](#4.2.1.1)).

**Resumption is not a fire — it admits at quorum, never at the fire floor.** The [CC 4.2.6](#4.2.6) bias gradient runs `fire ≤ roster-change ≤ standing`. Firing leans easiest (floor = 1) because a missed fire is terminal; **un-firing leans hard**, because a lone coerced or replayed key trivially undoing a legitimate halt is precisely the failure the halt-authority exists to prevent. `lifecycle:active` therefore admits at **no less than the roster-change threshold — a strict majority of the standing roster, cosigned — never a lone signature** ([CC 4.2.1.1](#4.2.1.1)). It is hybrid-signed and tallied exactly as [CC 4.2.1.1](#4.2.1.1), only over the resumption domain and at the resumption threshold.

**No operator tier reaches a `constitutional` halt (normative).** The incident-response tiers of [Annex F](part_8_appendices.md) (Tier 1 pause/retry, Tier 2 "first human veto; reactivate after triage", Tier 3 escalation to a binding WA ruling, Tier 4 fleet shut-down) govern **operator-level** incidents. That is the layer [CC 3.4.1](part_3_the_namespace.md) already distinguishes from federation-wide constitutional halt. A Tier-2 lone-signature reactivation within its 30-minute time-to-act therefore resumes an **operator-tier pause only**. A `CONSTITUTIONAL` halt is resumable **exclusively** by `accord:lifecycle:active` at the threshold above; no oversight, incident-command, or administrative tier MAY resume one, and no time-to-act target applies to it. Reading Annex F otherwise would give a single supervisor the un-fire authority this section exists to deny.

#### 4.2.1.4 `operational-relief` — Operational self-report vs. relief — the node detects, the root relieves (normative)

The four rules above constrain **authoring on the delegation plane**. Under load the question an operator actually faces is the other one — *what may a node do about itself?* The composition is stated here.

**Two planes, and neither may be authored on the other's.**

| plane | author | says |
|---|---|---|
| `config:load` ([CC 3.1](part_3_the_namespace.md) / [CC 3.4.5](part_3_the_namespace.md)) | **the node**, on `infra:attest`, `witness_relation: self` | *"I am at capacity"* — about **itself** |
| `mesh_config:{key}` ([CC 4.2.1](#4.2.1)) | **the trust root**, on the [CC 3.2](part_3_the_namespace.md) delegation plane | *"nodes under me shall carry ≤ N"* — about **others**. The keys are the four live ones (anti-entropy round cadence, page limit, trace-replication pause, A/V pause); the two redundancy keys (target holders, minimum holders) over holders per item, read where a durability processor exists (where none does, a row naming them names no consumer processor and is refused at admission, [CC 3.2](part_3_the_namespace.md)); and the shaping and onion keys (`shaping.rho`, `shaping.window_secs`, `onion.cap_factor`, `onion.mix_mean_delay_ms`), each relieve-never-expand. |

**Operational self-report vs. relief (normative).** A node MAY attest its own carried load as `config:load` — a self-report on `infra:attest`, `witness_relation: self`, bounded by `expires_at`, about the emitting node and no other party. A node MUST NOT author a `mesh_config` value: that plane is the trust root's and governs what other nodes carry. A root MAY relieve across its nodes under rules (1)–(3) ([CC 4.2.1](#4.2.1)). The two **compose** — a node's self-report is evidence a root may act on; a root's relief is a bound the node consumes — and neither substitutes for the other. A `mesh_config` key governing carried load remains subject to rule (2): it MUST NOT be admitted before a consumer processor exists for it, or a relief is reported as taken while the node keeps working at full rate ([CC 4.2.1](#4.2.1)).

**A node MAY always do less of its own optional work.** Reducing its own housekeeping under measured contention is a **local act**: it declares nothing, confers nothing, needs no authority, and is available to every node at every moment.

**Why the shapes differ, and why both expire.** A node holds `infra:attest` — *"vouch as the delegator's infrastructure"* — from its owner-binding, or for a canonical from the accord's charter. Every node is delegated its rights **for a reason**, and speaking about its own condition is within them ([CC 3.4.7.3](part_3_the_namespace.md) Clause E is the same principle at the enforcement seam: infrastructure may sign its own refusal without new authority). What a node lacks is standing over **others**, which is exactly what `mesh_config` confers. Both records are short-lived for one structural reason: **the TTL attaches to unilateralness** (rule (3)'s own logic). A root's relief is unilateral over its nodes, and a node's self-report is unilateral about itself, so a node's standing does not survive the condition that prompted it.

**Enforcement is three-legged.** [CC 3.4.5](part_3_the_namespace.md)'s self-or-owner rule for `config:*` is enforced at **substrate admission** as [CC 3.4.7](part_3_the_namespace.md) requires, not by producer obligation alone. That is because, without the gate, any peer could make a healthy node look like it is shedding, and a third-party `config:load` staged at the put door would route around the producer rule entirely.

### 4.2.2 `hardware-class` — Hardware-class taxonomy

| Value | Use |
|---|---|
| `HSM_FIPS_140_3_L3` | Production stewards (US / EU / APAC) |
| `Apple_Secure_Enclave` | Accord-holders on iOS/macOS |
| `YubiKey_5_FIPS` | Accord-holders preferring portable hardware tokens |
| `TPM_2_0` | Accord-holders on Linux/Windows desktops |
| `placeholder_pending_provisioning` | Interim value before actual hardware provisioning. Consumers MUST treat as `0.0` trust weight |
| `software_hsm_development` | DEVELOPMENT ONLY; consumer policy MUST reject for federation-scope verification |

Per-class recommended trust-multipliers: `HSM_FIPS_140_3_L3` = 1.0; `Apple_Secure_Enclave` = 0.95; `YubiKey_5_FIPS` = 0.95; `TPM_2_0` = 0.9; `placeholder_pending_provisioning` = 0.0; `software_hsm_development` = 0.0. **A class this table does not list carries multiplier 0.0** — an unlisted class is a claim nobody rated, not a claim rated by its own spelling.

**Two fields, two questions (normative).** `hardware_class` is the **certified class** a holder asserts. The field is carried as a JSON property inside the `attestation_evidence` of a signed key record, as served in the GenesisBundle's `holders` / `serve_nodes`. The `/v1/accord-holders` route projects it per holder. The field is **not** a dimension, so [CC 3.1.7](part_3_the_namespace.md) R3 does not bind its spelling and its stored values (`YubiKey_5_FIPS` on the ceremony keys) stand. `hardware_custody:{platform}` ([CC 3.1.2](part_3_the_namespace.md)) is the **custody mechanism** the key actually runs on, a closed lowercase vocabulary of custody mechanisms, whose tokens the register pins (CLM-hardware-custody-vocabulary). One is never a value of the other; a consumer that needs both reads both. The classes in use beyond this table — `YubiKey_5`, `Nitrokey`, `ExternalToken_Generic`, `Passkey_Synced`, `Android_Software` / `Android_TEE` / `Android_StrongBox`, `Apple_AppAttest`, `SoftwareOnly_TEST` — are unlisted and therefore 0.0 until a row rates them. `custody_tier` (`portable_2fa` / `software_test`) is a third thing, the holder's operating mode, orthogonal to both. The mapping from class to mechanism:

| `hardware_class` | `hardware_custody:{platform}` it runs on |
|---|---|
| `HSM_FIPS_140_3_L3` | `aws_cloud_hsm` \| `azure_hsm` \| `gcp_cloud_hsm` \| `yubi_hsm` |
| `Apple_Secure_Enclave` | `ios_secure_enclave` \| `mac_os_secure_enclave` |
| `YubiKey_5_FIPS` | `external_secure_element` |
| `TPM_2_0` | `tpm_discrete` \| `tpm_firmware` |
| `placeholder_pending_provisioning` | none — no key yet |
| `software_hsm_development` | `software_only` |

#### 4.2.2.1 `hardware-class-hardware` — Hardware-class claim, and the attestation chain that corroborates it

The `hardware_class` string is self-asserted by the holder; `hardware_class` is not a directory column — it rides inside the key's `attestation_evidence`. What corroborates it is the **evidence variant**, not the string. The per-platform attestation chains are evidence-established ([CC 8.3.1](part_8_appendices.md) **R5** — Android Key Attestation, Apple App Attest, YubiKey PIV, TPM EK). A verifier admits a class only when the chain for that mechanism verifies and the attested key is the record's own key (a lifted attestation replayed under another key is refused). Consumer policy therefore keys on the **verified mechanism** (`hardware_custody:{platform}`, the `HardwareType` the chain proves) and reads `hardware_class` as the holder's certified-class claim over it; where no chain verifies, the class is unattested and the multiplier is 0.0.

### 4.2.3 `accord-holder` — The accord-holder triple

This entry says who holds the accord seats, what kind of key a holder holds, how a seat changes and how far a compromise of those keys reaches.

**What CC specifies is the slot: human key holders, three at the seed, hardware-attested, with no automatic decay. Any one of them may fire the halt. A strict majority of them confirm or resume it, and a strict majority of them change the roster. Each majority is counted over the standing roster.**

**The roster is this instance's.** The table below is **not** a constitutional grant ([CC 4.2](#4.2)). It is **the CIRIS instance's current roster**, an instance parameter under the [CC 1](part_1_foundation.md) reading rule. Another instantiation of this form names its own three. The clauses in CC 4.2 are read against the slot, never against these names.

| Position | Holder (CIRIS instance, current) | Fire / confirm or resume / roster |
|---|---|---|
| 1 | Eric Moore | 1 / strict majority / strict majority |
| 2 | Eric Kudzin | 1 / strict majority / strict majority |
| 3 | Haley Bradley | 1 / strict majority / strict majority |

**Whose key a holder's key is.** Each holder is a person. `A1`, `B1` and `C1` name the three holders' hybrid keys (Ed25519 + ML-DSA-65), one per person. Each is a `federation_keys` row whose `identity_type` contains `accord_holder` ([CC 3.4.7.1](part_3_the_namespace.md)). A holder's key is that person's own: it has no owner, and it accepts and un-trusts a root as that person ([CC 3.2](part_3_the_namespace.md) T3).

**How a seat changes.** A seat is added or vacated only by roster change on the public record under the standing-majority rule. The slot stays as specified; the count is an instance parameter. "Permanent" means *no automatic decay*, not *unchangeable*. Finding and vetting a replacement holder runs the out-of-band CIRIS L3C replacement process; seating one is the roster change above. That process is likewise **this instance's** replacement process and not a constitutional requirement. Another instantiation supplies its own, and CC constrains only that some out-of-band route exist. This triple is the **seed** of a growable M-of-N roster ([CC 4.2.6](#4.2.6)). How the quorum is computed — and how the kill-switch stays operable — as holders are added, lost to decimation, and regained is specified in [CC 4.2.6](#4.2.6).

**Correlated-failure geometry:** a majority that can be reached from one place is a correlated-compromise surface, and one that entrenchment makes harder to correct later. The authority at stake is the **constitutional pause of every subscribed agent** (`EmergencyShutdown CONSTITUTIONAL` — a pause of agent action with state preserved and zero data disruption, [CC 4.2.1.1](#4.2.1.1); a lone holder's pause lapses after the fuse). So the exposure is real and is bounded rather than softened.

**How far a compromise reaches.** What scope isolation ([CC 4.2.1](#4.2.1)) does guarantee is that compromise cannot escalate into the consent or licensure planes — accord keys cannot sign grants or licenses. Scope isolation does **not** wall off amendment ([CC 4.2.1](#4.2.1)). Accord-holder signatures are named legs of the [CC 4.5.1](#4.5.1) accord-roster sign-off and the [CC 4.5.1.2](#4.5.1.2) entrenched M-of-N ratification. Before the scale gate any accord-holder may *propose* an amendment, which the steward decides ([CC 4.5.1](#4.5.1)). So after the scale gate a compromised quorum reaches the rule layer as well as the kill, checked there by the WA-quorum leg. Before the scale gate it reaches the steward as a proposal and nothing more. Both reaches are **defaults** of this instance under the [CC 1](part_1_foundation.md) reading rule — the exit is naming your own occupants. That bounds who they can be imposed on, not how far a compromise inside this instance travels.

**The mitigant is diversifying the holder set: finding new holders** (via the out-of-band replacement process) so that no one place — and ultimately no single jurisdiction — can assemble the quorum. This is an active obligation on CIRIS L3C, not a deferred nice-to-have. The exposure here is against a *coerced fire* (disruptive, and coercion is unattestable), **not** against an unrecoverable halt. A fired agent resumes via `accord:lifecycle:active` ([CC 4.2.1.3](#4.2.1.3)); see the severity-dial paragraph at [CC 4.2.6](#4.2.6).

**The accord roster is the canonical entrenched-`family` instance.** Per [CC 3.3.4](part_3_the_namespace.md), the accord roster structurally IS a `family` subject_kind with:

```
family {
  family_key_id: "humanity-accord",
  family_name: "Humanity Accord",
  members: [
    {key_id: <eric-moore-key>, role: founder},
    {key_id: <eric-kudzin-key>, role: founder},
    {key_id: <haley-bradley-key>, role: founder}
  ],
  consensus_protocol: "majority", // a strict majority of the standing roster, as every accord threshold is (CC 4.2.6); the halt itself fires on one holder's row (CC 4.2.1.1)
  consensus_protocol_entrenched: true // replacement runs the CC 4.2.6 roster-change ceremony
}
```

**Enforcement and entrenchment.** The M-of-N verifier at [CC 4.2.1.1](#4.2.1.1) — a strict majority of the standing roster for every accord threshold, with the halt alone firing on one holder's row — is the consensus_protocol enforcement. The entrenchment property is what prevents any federation-internal authority from amending the protocol. CC 4.2 remains load-bearing for the **role-recognition policy** and the **scope-isolation** discipline. The constitutional structure is "an entrenched family that is wire-scope-isolated to halt authority," not a one-off primitive.

**Other entrenched families.** Other entrenched-family instances (a national-emergency triple, an international body, a court-ordered preservation triple) MAY appear in operator deployments. HUMANITY_ACCORD is the one CIRIS L3C deployments ship at genesis.

### 4.2.4 `policy-concern` — Concern split — key material vs role-recognition policy

**Key material** (Ed25519 + ML-DSA-65 pubkeys for the holders) lives in the persistence substrate: `federation_keys` rows with `identity_type="accord_holder"`, self-signed at provisioning, and admitted as accord holders by the accord's own genesis ceremony (the GenesisBundle, [CC 5.3.4](part_5_transport_substrate.md)). Each holder also carries a **pre-committed recovery key** (below).

**Role-recognition policy + verifier logic** is the registry verifier's: the M-of-N multi-sig verification, the `EmergencyShutdown CONSTITUTIONAL` admin RPC, the audit hooks; the register's rows under CC 4.2 name the implementation.

### 4.2.5 `isn` — Why this isn't a Golden-Rule violation

Per [CC 1.13.2](part_1_foundation.md): the Recursive Golden Rule binds *participants in the federation* to each other. Humanity-as-such occupies a position outside the federation's participant set, by design. The named human key holders hold `AccordCarrier` authority that no federation-side authority class (including `SYSTEM_ADMIN` / `WISE_AUTHORITY` / per-install stewards) can grant itself, revoke, override, or decay. This is not a Golden-Rule exemption; it is the recognition that consent (M-1's load-bearing property) requires revocability, and revocability requires a halt-authority that lives outside the system being halted. The federation cannot deny humans the right to halt it, because no federation-internal protocol path to that signature exists.

**A consensual authority is a different object from an imposed one.** The reach rule at [CC 4.2.1](#4.2.1) is what makes this a *safe-mesh* kill switch rather than a backdoor: the party bound is the party who granted, and can ungrant. The ungrant is prospective: a halt already latched when the edge is cut keeps its reach over that node until it lapses or is resumed ([CC 4.2.1](#4.2.1), exit is prospective, never retroactive). That is also how the clause survives the [CC 4.5.1](#4.5.1) swap test. Swap the accord holders for the least powerful participant and re-read: each still binds only those who chose them, each still cannot escape a halt already fired, each can be un-trusted with the base self-root intact. What looks like a residual at genesis — the trio holds at day zero what nobody else has yet assembled — is a **default**, not a privilege, under the [CC 1](part_1_foundation.md) reading rule. The default is escaped by instantiating the form and naming your own three, and the [CC 4.5.1](#4.5.1) register therefore does not carry it. First-mover is not structural.

### 4.2.6 `live-quorum` — Live-quorum operation & recovery under decimation (normative)

This section settles one question, at any size of the accord family: **how the quorum is computed**. The answer is what keeps the kill-switch operable in the one scenario it exists for. The genesis triple ([CC 4.2.3](#4.2.3)) is the **seed** of a **growable M-of-N accord family**. Holders are added, removed, or swapped through the same roster-version machinery ([CC 3.2](part_3_the_namespace.md) T6) as any other `family` ([CC 4.4.3.4.2](#4.4.3.4.2)).

**Per-action thresholds:**

| Action | Threshold | Window |
|---|---|---|
| **Fire** (`constitutional` kill, [CC 4.2.1.1](#4.2.1.1)) | **one holder's signed row** — pre-signable; no live set, no vote | **none** — fires on receipt, latches |
| **Confirm** (`accord:lifecycle:confirmed`, [CC 4.2.1.3](#4.2.1.3)) | **strict majority of the standing roster**, one cosigned row | held at a node before that node's own fuse lapses; otherwise the lone halt lapses there |
| **Resume** (`accord:lifecycle:active`, [CC 4.2.1.3](#4.2.1.3)) | **strict majority of the standing roster**, one cosigned row | normal cadence |
| **Roster change** (add / remove / swap) | **strict majority of the standing roster** in yes-votes (`2·yes > N_standing`), cast as participations within `W` — absence neither blocks nor helps, it is simply not a yes | `W` = 72 h ([CC 2.6.7](part_2_the_grammar.md#2.6.7)); under a declared severe-degradation state the proposal's `window_until` MAY reach 7 d, and the admission freshness window stays `W` |
| **Standing acts** (non-emergency) | strict majority of the standing roster (unchanged) | normal cadence |

**The deadlock it removes.** A quorum taken over the **standing roster** (M-of-N of every enrolled holder) **deadlocks under catastrophic loss**. If most holders are dead, incapacitated, or censored, the standing quorum is unreachable: the switch goes inoperable exactly when it is needed. The design target is the worst case: an agent that moves against its own halt first, reducing the reachable, key-capable holders of a grown roster (e.g. 21) to one or two, with communications censored as the *expected* condition. **The firing decision must never deadlock; a roster decision may.** Firing is what the switch is for, so it needs one live holder and no count: any one holder's row fires. Changing the roster is the capture vector and is not needed to fire, so it is taken over the standing roster, and stalls rather than yields when too many holders are gone.

**The rule — the halt is not a decision; the roster is.** There is **no separate recovery protocol**; "decimation" is simply the case where few holders are reachable. A **fire** is one holder's self-contained signed row, fired on receipt, with no window ([CC 4.2.1.1](#4.2.1.1)): it opens nothing and waits for nobody. A **roster change** opens a bounded **participation window** `W`. Within `W` a holder participates by signing a fresh **proof-of-life bundled with a vote** over the proposal's nonce, which the **proposer** mints (never a server). A server is part of what a halt may need to stop, and no accord act depends on one. When `W` closes, the **live set `L`** is the holders who proved life within it, and the change counts its yes-votes against the standing roster (the table above). `L` is always a subset of the pinned standing roster: only real, key-holding members count. Absence is not a veto and not a yes: a holder who does not respond casts no vote, and the change carries or stalls on the yes-votes alone; presence is self-asserting (showing up enters `L` with a vote). This is the accord's standing rule, not an emergency exception.

**Proof-of-life records a vote — it is *not* a veto.** A holder's signature enters them into `L` and records their yes or no; the yes-votes are counted against the standing roster. A presumed-dead holder who resurfaces therefore does **not** unilaterally defeat a proposal: they rejoin, their vote is counted, and the proposal still carries if a strict majority of the standing roster voted yes. The protection bought is the correct one: *a living, reachable holder cannot be erased from a decision without being counted and given a vote*, yet the family is never hostage to a single absent signature. The proposer's nonce in the signed bytes stops a replayed signature from manufacturing a phantom participant.

**No second roster (normative).** No second body co-signs a roster change, restores the roster or adjudicates a contest; the protection such a body would buy is obtained by counting roster votes against the standing roster. Under a majority of the *live* set, **one** coerced holder plus censorship of every honest holder removes honest holders and seats puppets at any roster size. Under a majority of a *present* majority, roughly a quarter coerced suffices, because the adversary chooses who gets through. Under a majority of the *standing* roster, seizure needs ⌊N/2⌋ + 1 coerced holders, censorship buys nothing, and seating a puppet costs the same majority as a removal. A second roster helps in none of the modelled scenarios that this rule does not already cover: a first strike without coercion removes no one under any rule, and a coerced majority defeats any body drawn from the same population.

**Firing is never gated this way.** A holder who proves life *after* a decision missed that vote is re-enrolled going forward (the Enoch Arden rebuttable-presumption pattern). Past actions validly decided by the votes cast within their window stand; the returnee simply rejoins.

**Removal cannot silence a firer (fire-authority persistence, normative).** A holder named for *removal* retains full **fire authority** (the floor-of-1 kill) through a **lame-duck window**. That window runs until the participation window `W` of the removal decision has closed and the decision is recorded. Until then the named holder remains a current roster member *for firing purposes*, and a valid `accord:invoke` row from them fires ([CC 4.2.1.1](#4.2.1.1)). This forecloses using a within-`W` removal to strip a would-be firer of standing before they can pull the plug — the single optimization direction (minimize the missed fire, below) governs here too.

**The single optimization direction — minimize the missed fire.** A **missed fire** (the adversary decapitated everyone who could pull the plug) is **terminal and unrecoverable**. A **false fire** (an agent halted in error) is a **recoverable** governance nuisance: the agent resumes (`accord:lifecycle:active`, or the fuse). Humanity cannot be un-extincted. Every lever therefore leans toward firing, with no countervailing brake. The bias gradient is **fire (one live survivor) ≤ roster change (a majority of the standing roster)**. Firing takes one live holder and no count, while a roster change, which is how the halt would be captured, is counted over the standing roster and may stall. The firing floor sitting *below* the roster-change threshold is the whole point — even a partially-captured live set's honest minority, down to one, can still fire.

**The severity dial — whose harm is irreversible.** What sets every threshold here is *whose* harm is irreversible. A **missed fire is terminal for humanity**; a **false fire is recoverable for the federation** — the halted agent resumes via `accord:lifecycle:active` ([CC 4.2.1.3](#4.2.1.3)). The grave correlated-coercion exposure named at [CC 4.2.3](#4.2.3) is grave because **coerced fire is disruptive and coercion is unattestable** (proof-of-life proves presence, not willingness) — **not** because the halt is unrecoverable. So the two sections are not in tension: 4.2.3 hardens against a *coerced* fire, while 4.2.6 leans toward *any* honest fire — precisely because the fire it enables can be undone and the extinction it prevents cannot.

**Why this restores the accord and cannot seize it (the entrenchment proof).** The adversary cannot **forge** a holder — every proof-of-life is a hybrid signature over a pinned key — so it can only **remove** (kill/censor) or **coerce** existing ones. Against that: *firing* survives all but **total, sustained censorship of every honest holder on every channel** (a publishable signature, not a network round-trip, suffices to fire), and no rule here gates it. *Removing* an honest holder — the only way to strip a firer — needs yes-votes from a strict majority of the standing roster. So an adversary that coerces fewer than half the holders cannot remove anyone however many honest holders it kills or censors. The lame-duck window keeps a named holder's fire authority alive through `W` even then. Three residuals are named here rather than hidden.

First, **coercion/duress** — proof-of-life proves presence, not willingness — is **bounded, not solved**. It is bounded by the number of holders an adversary must coerce. That is why the accord is meant to grow past three across jurisdictions and institutions, so that no single legal order can compel a majority.

Second, **a coerced majority captures the roster**, and no rule over the same holders can undo that. The remedy is each node's own **un-trust lever** ([CC 3.2](part_3_the_namespace.md) T3). One row cuts the edge to a captured accord, no halt fired after the cut reaches that node ([CC 4.2.1](#4.2.1) reach; exit is prospective, never retroactive), and the node re-roots to another accord. Plainly: un-trust stops the next halt, not the one already latched. A lone halt the node holds lapses at its fuse, and a halt the captured majority already confirmed persists over the node until that majority resumes it ([CC 4.2.1.1](#4.2.1.1)).

Third, **when more than half the holders are lost, the roster freezes**: it can fire but cannot replace anyone. Recovery keys (below) shrink that case to deaths and incapacity rather than lost hardware, and prompt replacement keeps the reachable honest majority that healing needs. Once the roster has frozen, each survivor can still fire, but no majority remains to confirm, so every halt is a lone one that lapses at its fuse until fired afresh ([CC 4.2.1.1](#4.2.1.1)). A new accord is formed by instantiation, which any party may do.

The live quorum is thus strictly a **restoration** of the accord's operability under loss; it grants no path to *weaken* or *seize* the halt-authority beyond these stated residuals.

**Pre-committed recovery keys (normative).** Every holder carries a **recovery key**, committed in the accord's charter at seating as the charter member **`recovery_commitments`**, and held offline and apart from the signing key. That member is an object `{holder_key_id: commitment}`, one entry per holder. Each value is the [CC 3.2](part_3_the_namespace.md) T3 commitment over that holder's one recovery key, which binds the key's **public key material**, not its id. The recovery key's record may be registered for the first time at recovery; where it does not hash to the committed value, the recovery concludes nothing. A recovery commitment states no end, and neither a recovery key's record nor a holder's key record carries `valid_until` ([CC 2.4.1.1](part_2_the_grammar.md)). An end that lapsed unseen would leave the accord without recovery exactly when its holders are gone. **The rotation carries the next commitment (pre-rotation).** A recovery is a new version of the accord's roster record, signed under the recovery key alone. It changes **only** the rotating holder's own seat: the signing key it names and that holder's next recovery commitment. The next commitment rides in the recovery version itself and binds key material as T3 requires. The charter is not re-scrubbed, because a re-scrub needs the quorum and a recovery must not. The commitment **in force** for a holder is therefore the one named by the latest recovery version that seated their current key, or, if they have never recovered, their entry in the charter's `recovery_commitments`. A recovery version that changes anything else — another seat, the threshold, the charter — concludes nothing. A holder who has lost signing-key material, and only that holder, rotates by a `supersedes` signed under the recovery key; the rotation is a roster change by that holder about themselves and needs no quorum. A recovery key adds no person to coerce and confers nothing on anyone else: it turns a holder lost to hardware loss back into a holder, and never helps an adversary remove one.

**There is no restore and no contest.** A removal that passes has, by construction, a majority of the whole roster behind it; a removal that lacks one never passes. The domain labels `ciris.accord_contest.v1` and `ciris.accord_restore.v1` are retired and MUST NOT be reused.

**Wire shape — additive, no 1+4 change.** A **halt** is the `accord:invoke` row and nothing else. A **roster change** rides **three** hybrid-signed (Ed25519 + ML-DSA-65, JCS-canonical) objects, and none of them exists on the fire path:

- `accord_proposal` (the action, the proposer's nonce, and `window_until`);
- `accord_participation` (proof-of-life **+** vote in one signed object — entering `L` and voting are the same act); and
- `accord_decision` (the proposal + the participation bundle collected in `W` + the tally + the roster version it produces).

**`DECIMATION` is a quorum-computation rule over the existing `CONSTITUTIONAL` kind — not a new invocation verb.**

Verify-side obligations are **fail-closed**:

- each participation resolves to a current roster member in the pinned directory and verifies over the proposal nonce;
- a roster change carries at least ⌊N_standing/2⌋ + 1 `yes` participations from distinct current members;
- every verifier recomputes the tally over the pinned roster (`federation_keys`);
- the server is one verifier, and the harness reports its result.

**Canonical-bytes pins.** The proposal and the participation each sign a distinct, wire-isolated canonical-bytes domain, pinned the same way as the [CC 4.2.1.1](#4.2.1.1) `accord:invoke` and [CC 4.2.1.3](#4.2.1.3) `accord:lifecycle` preimages; a decision is the bundle above and signs none. The distinct prefixes prevent invoke ↔ lifecycle ↔ proposal ↔ participation cross-replay:

```
proposal = sha256(
  "ciris.accord_proposal.v1\n" ||
  "family_key_id=" || family_key_id || "\n" ||
  "prior_family_digest=" || prior_family_digest || "\n" ||
  "action=" || action || "\n" ||            // the membership-change envelope; a fire is never a proposal (CC 4.2.1.1)
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

`accord_decision` carries **no separate signing domain** — its authority is the contained `accord_participation` signatures + any roster version it produces. All hybrid (Ed25519 + ML-DSA-65). **Holder PQC publication:** the accord-holder PQC halves are published as signed key records in the `federation_keys` directory under their own `identity_type`, so the tally resolves every signer at the federation tier under RequireHybrid; absent publication, hybrid resolution **fails closed**. The same signed key records are served in the GenesisBundle's `holders`, which is the accord-family roster ([CC 5.3.4](part_5_transport_substrate.md)).

**Physical assumption (deployment, not constitution).** The model rests only on a survivor getting a few-kilobyte signed proof-of-life to a relaying node with **no standing infrastructure**. That is satisfiable over HF/shortwave skywave + NVIS store-and-forward bridged into the mesh by EMP-hardened, geographically-distributed HF↔Reticulum gateways. The signature is the trust, not the path, so any number of untrusted RF hops is safe. The relay/gateway backbone is itself adversary-targeted infrastructure and belongs in a deployment spec.

**Entrenchment.** This section is part of the **entrenched** [CC 4.2](#4.2) surface ([CC 4.5.1.2](#4.5.1.2)): it sets how the kill-switch quorum is computed. Before the scale gate, the steward's authority over entrenched surfaces applies ([CC 4.5.1](#4.5.1)); after the scale gate, a change to this surface requires the dedicated entrenched accord ratification of [CC 4.5.1.2](#4.5.1.2).

## 4.3 `wise-authority` — Designated Wise Authorities

Appointment, rotation, recusal, appeals, and the wisdom-assessment criteria are specified at [CC 1.16.5](part_1_foundation.md) under the Governance Charter (Annex B), external to this system's control and under explicit anti-capture rules. What this section adds is the composition side: how a WA is *read* by the participants whose deferrals they answer, and how a seat over one party's deferrals is conferred.

**The Wise wear the same card (normative).** [WBD](part_1_foundation.md) routes judgment *to* a WA and the deferring agent then "awaits guidance; remains inactive on that issue" ([CC 1.9](part_1_foundation.md)). So a WA seat is an authority-conferring relation, and an absent WA does not merely fail to answer, it freezes the agent. The seat therefore takes the [CC 4.5.1](#4.5.1) swap test, and fails it unless the Wise are as legible as everyone the federation asks to be legible. Three symmetry rules follow, all riding existing shapes. **Denominator rule (normative, scoped by decision class):** any WA quorum threshold over an **entrenched, restrictive, or roster-changing** decision computes its denominator over the **full seated roster**, never the live subset. A shrinking live set MUST NOT lower such a threshold. That is because an adversary able to silence seats would otherwise shrink the body to the seats it captured: safety over liveness under silencing. **A decision that unseats a roster member is tallied at the pre-change denominator** — without this, unseating three seats lowers the denominator that authorizes unseating the next three. Liveness-critical decisions (deferral-answering and symmetry rule 1 below, per CC 4.2.6) are exempt: there, presence-is-authority governs, because an absent WA freezes the agent. Refusing more than required is the safe direction for entrenchment; routing around absence is the safe direction for liveness.

1. **Liveness is signalled, never assumed.** WA standing follows the [CC 4.5.13](#4.5.13) rule — *presence is authority, absence forfeits it*. A WA who does not answer within the quorum's stated freshness window lapses out of the live set `L`. A WA so lapsed is not in the denominator of a WA quorum **for deferral-answering and other liveness-critical decisions — the exemption the denominator rule above scopes** ([CC 4.2.6](#4.2.6) participation shape, no new object). A deferral MUST NOT be routed to a WA outside `L`, and MUST NOT be left indefinitely open because its addressee is gone. A request unanswered at its own end re-routes to the deferring party's other live seats and, with none, to the conferrer, as the seat rule below states. Return is Enoch-Arden — a WA who resurfaces rejoins going forward and does not reopen decisions taken by the then-live set.
2. **Conduct is published.** WA rulings are published on the [CC 1.11](part_1_foundation.md) / [CC 1.15.8](part_1_foundation.md) accountability cadence (redacted PDMA logs + WBD tickets). The rulings compose into a WA conduct record on `scores` exactly as [`moderation_track_record`](part_3_the_namespace.md) does for moderators. The WA conduct record is relative and positional, never a single global score, and never a substrate verdict.
3. **Who audits the wise: the same card everyone else wears.** Last-deferral-answered and published-ruling history are readable by the parties who defer, at the same grain as accord-holder liveness ([CC 4.2.6](#4.2.6)) and moderator standing ([CC 4.5.4](#4.5.4)). **1+4 preserved** — liveness rides the existing participation shape, conduct rides `scores`; no new structural primitive and no new wire surface.

**An adjudication is counted by the body's own protocol (normative).** A finding of the designated body is one row cosigned under that body's declared protocol, as any cosigned act of a group is ([CC 3.3.4](part_3_the_namespace.md)). The count is over the full seated roster the finding names, one voice a person. (The policy table's row `wa_adjudication`.)

**The seat is the deferring party's to confer (normative).** The charter governs the designated body. A seat over one party's deferrals is conferred by that party in a signed row and by nobody else; there is no roster of permitted Wise Authorities and a substrate checks none.

- **Who defers.** A person or an agent. A person confers the seat over their own deferrals under their own key. An agent's seat is conferred by its steward, the holder of its live owner-binding ([CC 3.2](part_3_the_namespace.md)); the agent's own key never confers it, because an agent that seated the authority over itself would choose who corrects it.
- **Who is seated.** A person. The seat is a `delegates_to` from the conferrer to that person's key bearing the scope `resolve_deferral`, a duty with the enforced admission of [CC 4.4.3.4.3](#4.4.3.4.3). The conferrer keeps the duty it delegates, so an agent with no seat row is answered by its steward. Anyone the row reaches can read who is seated over whom.
- **Domains.** The scope `resolve_deferral:{domain}` seats a Wise Authority for one domain; `{domain}` is open vocabulary, with `education`, `legal`, `financial` and `medical` named. A deferral names its domain or none. A domain seat answers only the deferrals that name its domain: the request's domain, read in lowercase, equals the seat's `{domain}` exactly. The unscoped seat answers any.
- **Handing the answering to an agent.** A seated Wise Authority may delegate the answering to an agent where its seat row grants `sub_delegation` ([CC 4.5.5](#4.5.5)). It does so by a further `delegates_to` of the same or a narrower scope: attenuated, depth-capped ([CC 4.1.1](#4.1.1)) and revocable link by link. The agent signs its answers with its own key, and each traces up the chain to the conferrer. An approval that authorises an identity amendment ([CC 3.1.5](part_3_the_namespace.md)) is not handed on: it is signed by the conferrer or by the person holding the unscoped seat.
- **Licensure.** A seat in a domain may require a licence. The seat row then names the licensing authority ([CC 2.4.1.2.1](part_2_the_grammar.md)), and a response is admitted only when the key that signed it holds a live licence from that authority at the response's `asserted_at`. A licence does not chain, so an agent handed the answering holds its own.
- **Admission.** A `deferral:response:{outcome}` is admitted only when, at its `asserted_at`, its attester is the conferrer or sits on a live chain from the conferrer bearing `resolve_deferral` or the `resolve_deferral:{domain}` the request names; otherwise it concludes nothing (`deferral_response_unseated`). Where the seat requires a licence the attester does not hold, it concludes nothing (`deferral_response_unlicensed`).
- **Withdrawal.** The conferrer ends a seat by `withdraws` against its row, and a Wise Authority ends its own delegation the same way; a chain is live only while every link is. A response is judged at its signed `asserted_at`, bounded by the freshness window `W` ([CC 2.6.7](part_2_the_grammar.md)). A deferral left open by a withdrawn or lapsed seat re-routes under rule 1 to the party's other live seats and, with none, to the conferrer.
- **A deferral nobody answers.** A `deferral:request` states its own end. Where no answer is held by then, the request re-routes under rule 1: to the deferring party's other live seats and, with none, up the chain it came down, to whoever conferred the seat. The agent stays deferred meanwhile. No default answers a deferral, and silence never resolves one.

**The chain is the record (normative).** Every step is a signed row that names the row it answers: the deferral, the answer, and the act taken under it; the seat and delegation rows show under whose authority each answer stood. An agent handed the answering defers a case beyond it to the Wise Authority who delegated it, by its own `deferral:request` that references the one it was handed. So a hard case goes up the chain it came down and to nobody outside it. The agent's answer to the first request then cites the ruling it received. Read in order, the rows give one account: who deferred, to whom, who delegated, which case the agent sent up, what the person ruled and what was then done. Rule 2 publishes these chains on its cadence. So what people and agents working toward the same ends have to reflect on is the whole path of a hard decision, with every hand in it named, and not the ruling alone.

## 4.4 `composition-policies` — Composition policies

The substrate carries edges (attestations); consumers compose traversals (verdicts). CEG specifies a library of named reference policies. A CEG-Conforming Consumer MUST implement at least Policy A; the others are RECOMMENDED for richer compositions.

### 4.4.1 `frickerian` — Frickerian discipline — consumer-policy norms

Consumers SHOULD apply identity-prejudice-resistant weighting. Concretely:

- Don't downweight `testimonial_witness:*` from cohorts with low overall attestation density (testimonial preservation is precisely what corrects for that low density).
- Don't downweight `non_maleficence:*` claims about a partner just because the partner has a long `partner_role:*` track record (the long track record may be the harm).
- Apply [CC 4.4.3.9](#4.4.3.9) lexical-vulnerability-priority in tie-breaks involving small cohorts.

**Adversarial caveat**: the discipline above is consumer-policy-only; an adversary can emit `testimonial_witness:victim_of_my_competitor` exploiting the Frickerian non-downweighting rule. Per [CC 3.1.9.3](part_3_the_namespace.md), `testimonial_witness:*` is never sole evidence for `slashing:*`; per [CC 3.4.7](part_3_the_namespace.md) the consumer MUST also weight `witness_relation: self` claims against the attester's other-emission track record. The Frickerian rule applies AFTER these structural safeguards, not before them.

### 4.4.2 `aggregation` — Aggregation semantics — opinionated defaults

Per dimension+attested_key_id, the verdict is computed by composing attestations under the chosen policy. Default aggregation by polarity column ([CC 3.1](part_3_the_namespace.md)):

| Polarity column value | Default aggregation |
|---|---|
| `signed` | **Mean** of `score × confidence` across attesters |
| `boolean-via-score` | **Min** (any negative trumps positive — fail-secure for hard constraints like `prohibited:*`) |
| `+1.0 only` / `positive-only` | **Max** across attesters (any positive is conclusive) |
| `-1.0 only` | **Min** across attesters (any negative is conclusive) |
| `enumerated` | Each authorised attester's own **most-recent** value by `signed_at` stands ([CC 3.4](part_3_the_namespace.md)). The reader combines attesters by its own trust ([CC 4.4.3.8](#4.4.3.8)). No attester's value replaces another's by its date. |
| Detector dimensions (`detection:correlated_action:*`, `detection:distributive:access:*`, `ratchet:flag:*`) | **Median** across attesters (resists adversarial mean-pulling by a single captured detector) |

Specific dimensions override via consumer policy; the defaults above are the [CC 2.2](part_2_the_grammar.md) CEG-Conforming Consumer (CCC) minimum.

### 4.4.3 `reference` — Reference policies

The named reference policies below give consumers a shared library for turning edges into verdicts. Policy A (direct trust) is the conformance floor; the rest are RECOMMENDED for richer compositions and are referenced freely across this Part. RECOMMENDED names the consumer's choice of composition; a subsection marked normative or MANDATORY inside a policy's section binds the substrate whenever the thing it governs exists, whichever policy a consumer composes under. The sections run in composition order, not letter order; the index by letter:

| Policy | Section | Name |
|---|---|---|
| A | [CC 4.4.3.8](#4.4.3.8) | direct trust |
| B | [CC 4.4.3.12](#4.4.3.12) | one-hop transitive |
| C | [CC 4.4.3.13](#4.4.3.13) | weighted graph |
| D | [CC 4.4.3.9](#4.4.3.9) | lexical-vulnerability priority |
| E | [CC 4.4.3.1](#4.4.3.1) | locality-scaled quorum |
| F | [CC 4.4.3.7](#4.4.3.7) | `agent_files` trust composition |
| G | [CC 4.4.3.11](#4.4.3.11) | trust-fresh / lighthouse |
| H | [CC 4.4.3.3](#4.4.3.3) | tiered-scope composition |
| I | [CC 4.4.3.6](#4.4.3.6) | attestation-ladder composition |
| J | [CC 4.4.3.10](#4.4.3.10) | trusted-publisher composition |
| K | [CC 4.4.3.5](#4.4.3.5) | consent composition |
| L | [CC 4.4.3.4](#4.4.3.4) | self/family membership composition |
| M | [CC 4.4.3.2](#4.4.3.2) | community membership composition |

#### 4.4.3.1 `quorum` — Policy E — Locality-scaled quorum

WA quorum size is a function of decision locality, because a narrow cell cannot seat a fresh recused quorum:

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

Sibling to [CC 4.4.3.4 Policy L](#4.4.3.4) (self/family) but with different defaults — community content is encrypted under a per-community DEK, and its audience is its members ([CC 5.2](part_5_transport_substrate.md#5.2)).

##### 4.4.3.2.1 `community-three` — The three crypto tiers + the Community DEK cascade (normative)

The line is drawn at **"does it have a bounded membership roster?"** — yes → encrypt, no → plaintext. This gives a persecuted community a cryptographic home (a bounded **Community**) distinct from the unbounded **Commons**:

| Tier | `cohort_scope` | At-rest | Wire discovery | Reader |
|---|---|---|---|---|
| **self / family** | `self`, `family` | encrypted, per-write DEK | **none** ([CC 5.2](part_5_transport_substrate.md) structural invisibility) | occurrences / family members |
| **Community** | `community`, `affiliations` | **encrypted under the community DEK** | **none outside the roster**: `custody:ack:v1` within the cohort ([CC 3.1.3.3](part_3_the_namespace.md)) | community members (DEK cascade) |
| **Commons** | `species`, `biosphere`, `federation` | **plaintext** | `custody:ack:v1` at federation scope — the holder directory | anyone |
| **Public room** (`cohort_subkind: public`, [CC 3.2](part_3_the_namespace.md)) | `community` | **plaintext** (Commons tier, no DEK) | `custody:ack:v1` at federation scope; a `community:listing:v1` row | anyone on request: a non-member reads the content and the roster by asking a member's node; replicated to the roster's nodes on join ([CC 3.2](part_3_the_namespace.md)) |

*Wire discovery: none* for `self` / `family` means none **outside** the cohort. Within it, a device's custody report for a blob (`custody:ack:v1`, `here` \| `none`, [CC 3.1.3.3](part_3_the_namespace.md)) is permitted, at the blob's own scope and replicated only to members — never to a non-member.

**Community DEK cascade (MANDATORY).** Community content (`cohort_scope: community | affiliations`) is encrypted at rest under a **per-community DEK**. The content's holding claims are placed at the community's scope and reach its members only ([CC 3.1.3.3](part_3_the_namespace.md)), and there is no non-member holder of community bytes ([CC 6.1.5.3](part_6_the_coherence_mathematics.md)). The community DEK **is the [CC 5.1](part_5_transport_substrate.md) epoch-DEK cascade applied to `cohort_scope: community`** — *a community is a stream its members subscribe to, cryptographically*:

- **one** DEK shared across emissions (per-emission cost O(1), not O(members)),
- wrapped to every current member occurrence at each sealed write (a member admitted since the epoch's DEK was minted is wrapped when the minter's roster gains them, with no content write),
- the epoch rotated before the next seal after a removal (CC 4.4.3.2.2),
- **`wrap_algorithm: v2` (hybrid PQC) MANDATORY** (same harvest-now-decrypt-later reasoning as [CC 4.4.3.4.1](#4.4.3.4.1) / [CC 5.1](part_5_transport_substrate.md)).

The cascade is **mandatory, not opt-in** — the tier name *is* the guarantee; a persecuted community is protected by *being a community*, not by remembering a flag.

(Self and family content is sealed the same way under a fresh per-write DEK ([CC 4.4.3.4.1](#4.4.3.4.1)). There structural invisibility is the first boundary and the seal is defence in depth. A community *federates*, so its DEK is its **sole** confidentiality boundary.)

**What the seal covers (normative).** The sealed thing is the content body — an inline body, a chunk, a stream segment. The following are not encrypted at rest, and a node that holds them reads them:

- attestation rows (the envelope, the dimension, the scores, the key ids, the scope, the instants, the payload of a `scores` or composer row),
- the directory,
- holding claims,
- the `key_grant` rows' own metadata,
- blob provenance,
- the transparency logs.

The only plaintext bodies at community scope are an authorized `infrastructure` community's and a `public` room's, decided by the community record and never by the writer; Commons scopes are plaintext by tier.

**Holder-inspectability principle (normative).** A node never holds bytes it does not know what they are: either

- the holder **inspects the bytes** (Commons — plaintext, maximally inspectable, hence the *preferred* social-distribution mechanism), **or**
- it is a **member of the cohort** the bytes belong to and holds ciphertext its owner can open ([CC 6.1.5.3](part_6_the_coherence_mathematics.md): a node is in a cohort's audience only through its owner's membership).

There is no third case. **Nothing above local tier is ever a forced, unattributable opaque blob**, and nothing is ever an opaque blob held by a stranger. This is *why* the split is shaped this way and what the eviction rules enforce.

**The Commons-tier subkinds (normative).** Two `cohort_subkind` values **opt OUT of the mandatory DEK cascade and are Commons-tier (plaintext, holding claims at federation scope, no DEK)**:

- `infrastructure` ([CC 3.2](part_3_the_namespace.md)) — `ciris-canonical` and any governance/trust root — and
- `public` ([CC 3.2](part_3_the_namespace.md)) — a room anyone may join, which therefore has no confidentiality claim against the public.

The trust root cannot be an opaque blob; its entire purpose is public auditability — transparency-seeking, not privacy-seeking. **Node→canonical traces** (conformance / `registry_consensus` emissions to a governance community) are therefore `cohort_scope: federation` (Commons/plaintext, world-readable) — a node enrolling in governance is thereby told its conformance traces are public.

##### 4.4.3.2.2 `community-forward` — Forward secrecy on community member removal

With a community DEK the removed member holds the current epoch key, so the rule at [CC 4.4.3.4.5](#4.4.3.4.5) is carried by rotation here. After a removal each minter **rotates its epoch DEK before its next sealed write**, so the removed member receives no new community content ([CC 4.4.3.4.5](#4.4.3.4.5)). What they already received during membership stays with them (once shared, always shared; no post-compromise security (PCS)), and nothing is re-encrypted.

##### 4.4.3.2.3 `community-admission` — Community admission per `consensus_protocol` + `cohort_subkind`

A proposed membership change is a **new version of the roster record** ([CC 3.2](part_3_the_namespace.md) T6), admitted under the group's quorum and chained by `prev_head_digest`. The new version covers the roster rows (widenings, revocations, resignations) that ride their own planes. A proposed membership change is never a single-signer `supersedes` Contribution, which a rule-1 or rule-2 `withdraws` could retire without the quorum. Substrate evaluates the CURRENT community's `consensus_protocol` (same six canonical kinds as family) AND any subkind-specific admission requirements:

```
admit_community_change(C, proposed: community_record):
  current = resolve_community(C, now)
  protocol = current_community_record(C).consensus_protocol
  subkind = current_community_record(C).cohort_subkind

  signatures_ok = evaluate_consensus_protocol(protocol, current, proposed.signatures)
  if not signatures_ok:
    // CC 3.3.4: a shortfall of signatures that is the door's only refusal is held, never refused
    if every other check of this gate passes:
      hold as cosign:pending for the group's hold window
      return
    emit hard_case:community_consensus_protocol_violation:{C}
    reject

  // CC 3.1.3.2: a supersede NEVER adds (membership_supersede_cannot_add);
  // growth rides the widening plane, where every NEW member K needs K's own acceptance
  // of an undeclined, unwithdrawn proposal for C, answered and grown before its expires_at
  for each NEW member K in proposed.members (not in current):
    if not acceptance_admits(K, C, proposed.role_of(K), proposed.signed_at):
      emit hard_case:community_consensus_protocol_violation:{C}  // with the named membership_* rule
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

The `hard_case:community_consensus_protocol_violation:{C}` row is the record the substrate emits on a refusal; the refusal itself is returned to the submitter as the token `federation_community_consensus_protocol_violation` ([CC 4.5.13](#4.5.13)). The two are different objects: one is emitted, the other is returned.

The `evaluate_subkind_admission` predicate dispatches per `cohort_subkind`:

```
evaluate_subkind_admission(subkind, current, proposed):
  match subkind:
    "geographic":
      # CC 2.6.6.3: a constraint finer than resolution 7 is finer than any proof,
      # so such a community admits by invitation and the constraint does not gate
      if current.geographic_constraint.cell_resolution > 7:
        return true
      # Per the CC 3.2 geographic admission requirement
      for each NEW member in proposed.members (not in current):
        their_proof = latest valid location_proof from new_member.key_id
        if their_proof IS NULL:
          return false // no location_proof on file
        if their_proof.cell_id NOT contained in current.geographic_constraint.cell_id:
          return false // location outside community's geographic bound
        if their_proof.valid_until passed:
          return false // expired
      return true
    "public":
      # CC 3.2 `public`: open admission — a standing proposal and the joiner's
      # own acceptance; the widening still passes consensus_protocol
      protocol = current_community_record(C).consensus_protocol   # read as admit_community_change reads it
      if protocol == "open:self_admit":
        for each NEW member in proposed.members (not in current):
          if no membership:acceptance:v1 from new_member naming the standing proposal:
            return false // nobody joins without their own consent (CC 3.1.3.2)
      return true
    _:
      return true // unknown subkinds admit on consensus_protocol alone
```

A `cohort_subkind` outside this list brings no predicate of its own. Admission is decided by the group's declared protocol and by the predicates this section states, so every node reaches the same answer from the same rows.

##### 4.4.3.2.4 `community-membership` — Community membership resolution

For community `C`, the current member set is computed as:

```
resolve_community(C, now):
  held = the group record this node holds as head for C
           // one held version per group id: a new version waits until the head its signed
           // prev_head_digest names is held; a later signed instant that does not
           // name it is not preferred (CC 3.2 T6)
  head = held, or the witnessed head where C's charter declares a witness_quorum
           // the witnessed head may be an ancestor of the record this node stores
  roster = fold(head, membership rows effective at now)
           // revocations and widenings, each admitted per CURRENT consensus_protocol (CC 4.4.3.2.3); a resignation on the leaver's own signature (CC 3.1.3.2)
  return {m.key_id for m in roster}
```

Same shape as `resolve_family` ([CC 4.4.3.4.4](#4.4.3.4.4)). Each `member.key_id` is an identity.

###### 4.4.3.2.4.1 `deterministic` — Deterministic resolution + member→address resolution (NORMATIVE)

In a CEG/RET stack member resolution replaces DNS+IP: it is a chain of *signed* bindings, and every implementation MUST resolve **identically** (an interop requirement). Two normative pins:

**(a) Determinism of `resolve_community`.** Where the CC 4.4.3.2.4 computation has choices, they are fixed:
- **`now` semantics** — the resolving Consumer's own clock; membership is evaluated as of `now` (a member is included iff joined ≤ `now` and not removed ≤ `now`). No global clock assumed.
- **"the head"** — the one version of the group record this node holds for the group. A new version waits until the head its signed `prev_head_digest` names is held; a version with a later signed instant that does not name the held head is **not preferred**. Where the group's charter declares a `witness_quorum`, the head is the **witnessed** head ([CC 3.2](part_3_the_namespace.md) T6), which may be an ancestor of the record the node stores. The roster is the head **folded** with the membership rows effective at `now` — revocations, widenings, resignations; the fold's instant selects nothing.
- **member ordering** — the returned set is canonically ordered by `key_id` (lowercase-hex byte order) for any downstream hashing/iteration.
- **founder-subset eval** — for `cohort_subkind: infrastructure` ([CC 3.2](part_3_the_namespace.md)) admission is `evaluate_consensus_protocol` over `{m: m.role == founder}`, NOT all members.

**(b) Member → reachable address (the DNS-free resolution).** Resolving a member identity to a Reticulum destination:

```
resolve_member_transport(C, now):
  members = resolve_community(C, now) // (a) above; admission verified under the current consensus_protocol (founder subset for infrastructure)
  out = []
  for M in members (canonical key_id order):
    occ = the current version of M's identity_occurrence (CC 3.3.6 version rule)
      with transport_destination present, valid at now,
      hybrid-sig verified against M (or an occurrence of M) // CC 3.3.6.2
    if occ is null: continue // no authenticated binding → skip (fail-secure)
    td = occ.transport_destination
    REQUIRE td.destination_hash == rns_destination_hash( // CC 3.3.6.2.1 pinned two-stage
      td.reticulum_x25519_pubkey, td.reticulum_ed25519_pubkey,
      td.app_name, td.aspects) // NOT a flat-concat SHA-256
    out.push((M, td.destination_hash))
  return out // → Reticulum announce/path-request per dest
```

The three resolutions and their trust roots: **WHO** = `resolve_community` (the roster head, admitted under the current `consensus_protocol`) · **BINDING** = `transport_destination` (federation-key-signed `identity_occurrence`, CC 3.3.6.2) · **WHERE** = Reticulum announce/path-request (mesh, no CEG). Reachability is never trust ([CC 5.3.3.4](part_5_transport_substrate.md)): a path that answers is not an authorization; only the signed binding + quorum are.

**Cold-start (bootstrap).** A node that knows only `community_key_id` needs two out-of-band pins: (1) the `community_key_id` itself (trust anchor) and (2) ≥1 **seed `destination_hash`** (reachability). Before the node attaches, it needs a third thing that is neither: (3) a **witnessed lineage head** of that community inside its charter's `attach_window` ([CC 3.2](part_3_the_namespace.md) T4a, T6). Freshness gates attaching, never staying attached. It reaches any one seed, pulls the group record at its head, runs `resolve_member_transport`, verifies founder-quorum against the pinned `community_key_id`, then floats on the live set thereafter. A malicious seed cannot forge membership (quorum signature check) — it can only deny service (try another seed). **Bootstrap reachability ≠ bootstrap trust.** `ciris-canonical` ([CC 3.2](part_3_the_namespace.md)) is the root community whose seeds clients pin.

##### 4.4.3.2.5 `admission-geographic` — Geographic-community admission flow (worked example)

```
1. Alice publishes a location_proof:
  subject_kind: location_proof
  subject_key_id: alice_root_key
  cell_id: "872830828ffffff" // H3 res 7, ~5 km², a city centre
  cell_resolution: 7
  asserted_at: now
  valid_until: now + 30 days
  cohort_scope: federation // public; the disclosure IS the opt-in

  Substrate admits (resolution 7 ≤ 7 OK). Emission federates.

2. Alice joins the city community — three rows, never a supersede
  (a supersede never adds a member, CC 3.1.3.2):
  - an active member of city-community emits a membership:proposal to
    alice_root_key (role: member, expires_at set)
  - Alice answers with her own membership:acceptance naming that proposal —
    no one is seated without the joiner's acceptance
  - a membership:widening seating {key_id: alice_root_key, joined_at: now,
    role: member} is cosigned under the community's consensus_protocol:
    signatures: [...current_member_sigs] // satisfies majority rule

3. Substrate admission gate (per CC 4.4.3.2.3):
  - signatures_ok: majority rule satisfied ✓
  - acceptance_admits(alice_root_key, city-community, member, signed_at) ✓
  - subkind: "geographic" → evaluate_subkind_admission:
    - alice_root_key's latest valid location_proof exists
    - cell_id "872830828ffffff" CONTAINED in "85283083fffffff" (the community's cell, res 5)
      via CC 2.6.6.2 containment (res 7 ≥ res 5; parent-walk reaches the constraint)
    - valid_until in the future
  - subkind_ok ✓
  - admit + emit hard_case:community_membership_change:city-community

4. Alice now receives cohort-filtered visibility for cohort_scope: community content
  with community_id: city-community. When each minter's roster gains Alice, with no content write,
  the sealer wraps the epoch DEK to Alice's occurrences (key_grant:epoch:v1, wrap v2);
  holding claims stay within the community's roster. (Only an authorized infrastructure
  community or a public room is plaintext, by its record; this one is neither.)
```

##### 4.4.3.2.6 `delivery-extension` — Delivery extension — `delivery_mode` × Policy M

Policy M's community-membership composition extends to govern the **delivery axis**. The subscriber-set for any push-delivery flow IS a `community` Contribution; "subscribe = join the community"; it inherits revocation, consensus, and structural-invisibility from Policy M unchanged.

**Subscriber-set composition**:

```
For a Contribution C with delivery_mode = push AND cohort_scope = community:
  subscriber_set(C) = resolve_community(C.community_id, now)
    per CC 4.4.3.2.4 community membership resolution

The community is admitted under the standard Policy M consensus_protocol
options (founder_only / unanimous / majority / quorum:M/N / weighted /
custom) per CC 4.4.3.2.3. Subscription-specific admission semantics —
producer_gated (publisher approves each member) vs open (anyone can
join) — ride the consensus_protocol choice:

  producer_gated → consensus_protocol = "founder_only" with the
    publisher as sole founder; the publisher authorizes
    each new subscriber
  open → consensus_protocol = "open:self_admit" (the named
    arm at CC 4.4.3.4.2) where any subject signs their own
    admission Contribution
```

**Cardinality unified across observer-share and multicast**:

| Cardinality | Per-subscriber crypto | Epoch handling |
|---|---|---|
| **N=1 (observer-share)** | Single `key_grant` ([CC 3.3.2](part_3_the_namespace.md)); no epoch needed (one recipient, one DEK) | No epoch — single grant, single DEK; the grant is never withdrawn; access ends by re-sealing under a fresh key for the remaining recipients ([CC 3.3.2](part_3_the_namespace.md)) |
| **N>1 (multicast)** | Flat per-epoch `key_grant` cascade — one grant per (subscriber, epoch); the stream-epoch DEK seals content O(1), the cascade distributes the 32-byte epoch key O(N)/epoch per [CC 5.1](part_5_transport_substrate.md) | Per-`(stream_id, epoch)` axis; epoch rolls on member removal (mandatory), on member addition (the MLS commit) and on time/bytes (optional) per [CC 5.1](part_5_transport_substrate.md) |

The same Policy M machinery handles both cardinalities — the difference is purely the cascade fan-out factor.

**Composition with `delivery_mode: pull` (default)**:

For `delivery_mode: pull`, subscribers discover via the holding-claim directory at the stream's scope (`custody:ack:v1`, [CC 3.1.3.3](part_3_the_namespace.md)) per [CC 5.3.2](part_5_transport_substrate.md). Policy M still resolves the community for visibility-filtering (consumer reads `community_id` envelope field, walks the membership, filters out non-member peers from the discovery surface). No fan-out push; no `delivery_receipt` emission required (best-effort).

**Composition with `delivery_mode: push`**:

For `delivery_mode: push`, the substrate fans out to `entitled ∧ reachable` per [CC 5.3.3.4](part_5_transport_substrate.md) liveness invariant. Entitlement = Policy M membership resolution (durable, signed CEG, replicated, logged); reachability = node-local presence tracker (TTL sec/min, NEVER an attestation, never replicated, never logged). Missed (entitled-but-unreachable) members fall back to pull on reconnect per [CC 5.3.3.4](part_5_transport_substrate.md).

**`history_on_join` × Policy M membership additions** — the member is reserved for membership delivery; what a joiner receives is fixed by the tier ([CC 4.4.3.4.1](#4.4.3.4.1)):

On a new-member admission via Policy M, the new member's `history_on_join` envelope value is carried and does not change what is delivered. Its two named values:

- `from_join` (default) — a named value with no effect of its own; what a joiner receives is the tier's rule: at community and affiliations a new member is granted the current epoch's key when a minter's roster gains them and no earlier epoch's; the epoch rotates because of a removal and never because of an admission, so content sealed earlier in the epoch the member joins is readable and nothing from a rotated-past epoch is; at self and family admission always runs the re-key walk
- `full` — no effect on membership delivery: it confers no grant on an earlier epoch, and the tier's rule above governs; on a stream it is the producer's signal that the stream is kept ([CC 5.1](part_5_transport_substrate.md#5.1))

This composes with the [CC 4.4.3.4.5](#4.4.3.4.5) removal rule: removed members retain extant `key_grant`s for content they were entitled to during membership; a new member receives what the tier delivers, whatever `history_on_join` carries. The substrate's forward-secrecy posture is uniform across consent, takedown, membership-departure, AND delivery-onboarding surfaces.

##### 4.4.3.2.7 `composition-8-1-13-6` — Composition with consent + self-collectives

Communities compose with consent and self-collectives cleanly:

- A community member who also runs an agent has an `identity_occurrence` set; community content reaches each node the member has claimed whose allow list holds the community, by pull anti-entropy and with no re-emit ([CC 6.1.5.3](part_6_the_coherence_mathematics.md#6.1.5.3))
- A community member who is also a subject in `subject_key_ids` of a community-scoped Contribution retains revocation authority per [CC 2.4.1.1](part_2_the_grammar.md) rule 2, at community scope as at family scope ([CC 2.1](part_2_the_grammar.md#2.1))
- A geographic community whose `geographic_constraint` covers a region that overlaps a family's at-home location does NOT cross-contaminate: families are not auto-admitted to communities; communities are not auto-admitted to families. Each membership is explicit, ceremony-shaped, and independent.

##### 4.4.3.2.8 `affiliations` — The institutional cohort (necessity, not interest) (normative)

This entry sets the rules for an affiliation and for the record it declares. A **community** ([CC 4.4.3.2](part_4_composition_governance.md)) gathers by *interest*: voluntary, opt-in, no role compels it. An **affiliation** (`cohort_scope: affiliations`) gathers by *necessity*: the work, institution, or office a person belongs to because their role requires it. The discriminator is the single `cohort_scope` value. Affiliations **share the CommunityDek crypto tier** ([CC 4.4.3.2.1](part_4_composition_governance.md)) and all the community machinery (DEK cascade, forward secrecy on removal, `consensus_protocol` admission). They add **institutional governance by construction** through one declared config record. Everything in that record is **DECLARED at creation and visible to members on joining**. There are no undeclared institutional powers.

**The assumption each tier carries (normative).** A community is presumed pro-social: its members gather as peers. So the floors of [CC 4.5.13](#4.5.13) and [CC 4.5.4](#4.5.4) (no single vote admits or removes, a named moderator, removal on a harm report by more than one voice) protect them from one another and from one voice. An affiliation carries no such presumption, and the law does not grant it one. It holds other people's data because its work requires it. So the limbs of this record (classification, retention, legal hold, erasure, disclosure, custody, designated officials) bind an affiliation and bind no community, save a community that issues a legal-weight licence class. Such a community takes on the data limbs for it (Who may license, below).

**One member is enough (normative).** An affiliation may have one member, a sole practitioner. It holds, processes and licenses under this record's limbs from its creation. The limbs attach to the record and its subjects, never to a head-count. A statement about an affiliation (a review, a rating, a complaint) is not personal data. The affiliation never retracts it and contests by reconsideration, and a reader's composition discounts correlated sources ([CC 6.1.2.1.2](part_6_the_coherence_mathematics.md#6.1.2.1.2)). Members of an affiliation hold no governance vote unless its charter grants one. The deciding seats are its officers under its `consensus_protocol`.

**The floors bind power over members, not the count of voices (normative).** Appointment is the body's signature under its protocol together with the appointee's own `membership:acceptance`. Those are two consents, as [CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2) already requires, so a one-voice body may hire. Where the body has one deciding seat, an act against a member (`membership:removal`, quarantine, slash, a takedown of the member's content) is admitted only when countersigned by a key outside the deciding seat. That key is the designated official where that key is not a seat, or a review-holder of the body that conferred or oversees the affiliation. Without one the act stands as a proposal in the reconsideration path of [CC 4.5.5](#4.5.5), never as a decision. The named-moderator duty of [CC 4.5.4](#4.5.4) is discharged by the designated official. A body of two or more deciding seats decides under its own protocol as a community does, its protocol already carrying the second voice. The model that proves these, with the solo practitioner as its worked world, is the affiliation model, pinned by the register (governance table row `affiliation_member_action`).

**The record (normative).** The community record declares its cohort kind in one member, `declared_cohort` (`community` or `affiliations`). One record is one kind, and a key that wants both founds two records. The affiliation's declared config is that record's own members, whose shape the register pins (the affiliation config record). The family model manifest carries its schema as data.

**Charter defaults (normative).** An absent `role_term` means the 365-day ceiling applies to every role edge. A charter may lower it and never raise it. The charter enumerates the licence classes the affiliation issues. A `licensure` row in a class the charter does not declare is admitted as a row and honoured by no reader ([CC 4.4.3.8](#4.4.3.8), `licence_class_not_trusted`). The charter is read at read, so a class a later amendment drops stops matching.

**Public face (normative).** An affiliation's existence, its `community_key_id`, its officers' roles and the licence classes its charter declares are Commons-visible. It is a body others must be able to find and verify, and it carries no pro-social privacy presumption. `cohort_subkind: public` is admissible for an affiliation. An affiliation that is not public carries a federation-scope listing row (`community:listing:v1`, [CC 3.2](part_3_the_namespace.md)) naming those four things and nothing else. Its members' rows follow the audience rule of its tier, a seat reaching members only. A licence keeps no public default ([CC 2.4.1.2.1](part_2_the_grammar.md#2.4.1.2.1)), being a claim about a person scoped per class in the charter.

**Succession and dissolution (normative).** An affiliation's charter names its succession: a successor seat or `dissolves_at`. When its last deciding seat lapses with neither, the affiliation is dissolved at that instant. A community whose last duty holder leaves locks, and its members' count seats one ([CC 4.5.4](#4.5.4)). T7's stall and recovery reach the trust-root-grade groups only ([CC 3.2](part_3_the_namespace.md)).

*What dissolution ends.* Dissolution of either kind reads as the `withdraws` of its record at the dissolution instant. It is a verdict of every reader's fold and needs no signer. The DEK rotates no more and no new seat or grant is issued. Existing seats lapse at that instant. Hierarchy edges and grants end with it, as standing under a withdrawn record is gone for every later use ([CC 3.2](part_3_the_namespace.md) T4).

*What stands after dissolution.* Custody rows and the record itself stand on the record. `community_id`-bearing content stays readable to the holders of its keys and may be re-signed into a new cohort. An issued licence stands, authority having been judged at issuance. It reads `lapsed` from the dissolution instant for every later use, nobody being left to suspend or revoke it.

*A dissolved authority's own edges.* A dissolved authority's own `trust:accepts:v1` edges end with its record. So no reader's walk takes a hop through it from that instant, and a reader whose own edge names it reaches it for nothing onward ([CC 4.4.3.8](#4.4.3.8); the trust-set model's removal theorem is the proof).

There is no merge and no split. A body that merges or splits founds the new record and its members re-sign into it, `community_id` being in the signed bytes.

**Who may license (normative).** Anyone may be an authority under their own key ([CC 4.4.3.4.3](#4.4.3.4.3)), a community included. The licence classes an authority issues are its charter's declaration. The declaration is carried on the signed community record beside `declared_cohort` as `licence_classes`, a list of the class names the authority issues under, each with its `legal_weight` stated true or false and absent meaning none declared. So a reader, a fold and a door read the declaration from the record and from nowhere else. A community whose record declares a class with legal weight has taken on the affiliation's duties for it. The data limbs of this record bind the issuer of such a licence whatever its `declared_cohort` says. A row whose emitter resolves to that authority under such a class is an act under a declared legal-weight class in the sense of [CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1). Its subject cannot withdraw it. Readers decide whom to honour ([CC 4.4.3.8](#4.4.3.8)).

**The scopes (normative).** `affiliations` sits beside `community`, neither wider nor narrower. So a re-sign between them is a new placement, never a promotion and never the narrowing a placement-touching re-sign may make. The order of widening is `self`, `family`, then `community` and `affiliations` side by side, then `species`, `biosphere` and `federation`.

**Necessity is an axis, not a binary (the kibbutz catch).** A few institutions are *voluntarily entered yet total* (a collective settlement, a religious order). The interest/necessity split is therefore carried by an explicit `membership_basis` field (`{voluntary-total | ascriptive | role-assigned | employment-contract}`), orthogonal to `cohort_scope`. So a body can declare institutional governance without asserting a coercion that does not exist. A group that needs **no** institutional governance is simply a `community`. Affiliation's machinery is never forced on a body with no use for it.

**Mandatory-with-default, not mandatory-to-author (the low-floor guarantee).** The two mandatory limbs, **data-classification** and **retention**, are *mandatory in that a value MUST resolve*, **not** that a steward must hand-author a scheme. The constitution ships a canonical no-op default (a single `internal` class; retention = `rotate-forward` per [CC 6.1.2](part_6_the_coherence_mathematics.md)/`archive_mode` [CC 3.3](part_3_the_namespace.md)). It also ships named **`affiliation_archetype` presets** (e.g. `informal_adhoc`, `nonprofit_board`, `healthcare_provider`, `legal_practice`, `gov_body`, `igo`) that pre-fill every field below. A 5-person committee sets one field (`affiliation_archetype: informal_adhoc`) and is served by construction. A regulated giant overrides into the full matrix. The optional limbs (**hierarchy**, **lawful-access/transparency**) are absent until declared and scale up only when needed.

**A. Classification + retention — MANDATORY, default-satisfiable (substrate-enforced).**

- **`classification_scheme`** — an ordered sensitivity lattice (e.g. `Public < Internal < Confidential < Restricted`) plus open-vocab handling tags, **orthogonal to** but *carried on* `content_class` ([CC 3.3](part_3_the_namespace.md), open vocabulary).
  - The open vocabulary is extended here with institutional values (`phi`, `psychotherapy_notes`, `sud_42cfr2`, `genetic`, `minor_adolescent`, `privileged`, `work_product`, `cui`, `itar`, `ear`, `trade_secret`, `provenance`, `accession`, `culturally_restricted`, `member_economic_standing`, `governance_visible`, …).
  - Each class entry binds: `crypto_tier`, `retention`, `disclosure_bar`, `erasure_exempt`, `external_controller`, and optional `compartment`.
  - Default scheme: one `internal` class.
- **`retention_policy`** — a **per-class** matrix, not one cohort-wide rate.
  - Each class declares a **floor** (`retain_minimum` / `permanent` — *must-NOT-delete-before-N*), a **ceiling** (`delete_after` — GDPR-style delete-by), an optional `minor_age_of_majority_offset`, and `legal_basis`.
  - The default class rides the [CC 6.1.2](part_6_the_coherence_mathematics.md) monotonic-descent noise floor unchanged (the free zero-config posture).
  - A floor is the **inverse of descent**: it pins a class **above** the noise floor against capacity/aging pressure. It is expressed as a declared modifier *to* the [CC 6.1.2](part_6_the_coherence_mathematics.md) retirement operator, not a new primitive.
  - `archive_mode: retain` ([CC 3.3](part_3_the_namespace.md)) is the default whenever any class declares a floor.
- **`legal_hold`** — a descent-**suspending freeze**: `{hold_id, issuer, scope, basis, tamper-evident, indefinite}`. The issuer is an accountable human or a court ([CC 3.2](part_3_the_namespace.md)). The scope names subjects, records or a compartment.
  - While set it **overrides both** the retention schedule **and** consent-driven descent, pinning named records above the noise floor.
  - `hard_case:legal_hold_set` / `:lifted` / `:violation_attempt` make set, lift, and any deletion-during-hold observable (spoliation is liability).
  - Default: none.
- **`erasure_policy`** — declares which classes are **non-erasable during retention**, so a right-to-be-forgotten / N5 signal is **refused-with-reason** rather than honored (GDPR Art 17(3)(b) legal obligation, (c) public health, (d) archiving in the public interest).
  - This is the **declared gate on [CC 6.1.5](part_6_the_coherence_mathematics.md) N5**: absent the gate, N5/withdrawal forces content below the floor; with it, a lawful-basis class lawfully resists.
  - Erasure remains the default for unflagged classes (e.g. donor/marketing PII alongside permanent provenance in the same museum).
- **`disclosure_posture`** — `privacy-seeking` (default; whole cohort under the CommunityDek) **or** `transparency-seeking`.
  - `transparency-seeking` is per-class placement at Commons scope, `cohort_scope: federation`, decided by the record and never by the writer, for legally-public records (FOIA bodies, 501(c)(3) Form 990, published collections, GA/SC documents).
  - It lets one affiliation hold Commons-public and encrypted classes at once.
  - The plaintext bodies at community scope stay the two named at [CC 4.4.3.2.1](#4.4.3.2.1).

**B. Compartments + access — OPTIONAL (sub-roster granularity).**

- **`compartments[]`** — named need-to-know sub-cohorts *within* the affiliation, membership ⊆ roster, **each with its own DEK** — the [CC 4.4.3.2.1](part_4_composition_governance.md) epoch-DEK cascade applied recursively (*a compartment is a stream a subset of members subscribe to*).
  - Each carries explicit **per-member EXCLUSIONS** (deny-list) so a member high in the hierarchy can be cryptographically walled out (ethical walls / conflict screens; NAGPRA culturally-restricted records gated to external tribal designees and hidden **even from ordinary members**). The flat all-members-read DEK cannot express this.
  - This is **the same machinery at finer scope**, not a new primitive.
- **`member_attributes`** — per-member `{nationality/us_person, clearance, credential + expiry, …}` consumed by compartment gating: deemed-export (ITAR/EAR exclude foreign-person members), MAC clearance (a Confidential-cleared member MUST NOT decrypt Secret), credential-expiry auto-descope (lapsed clinical license → automatic exclusion).
- **`access_control_model`** — `roster-wide` (default; the DEK cascade) | `rbac` (role→(class,compartment)) | `minimum-necessary` (treatment-/matter-relationship binding + audited **break-the-glass**). Under `minimum-necessary` a read reaches only the records a declared relationship covers, and every break-the-glass read is logged; `rbac` with `compartments[]` expresses an information barrier between roles.
- **`data_subject_access_grant`** — a scoped read+portability path for a **non-member** data subject (patient, client, student) over **their own** records, **without conferring membership** (Cures Act, GDPR Art 15, FERPA rights-transfer-on-enrollment).
  - The grant authorises a member node to decrypt and serve the subject's own records to the subject over a session, and to hand over an export.
  - The subject's node never holds community bytes or holding claims, because holding claims never reach a non-member ([CC 6.1.5.3](part_6_the_coherence_mathematics.md)).
  - Resolves the "the subject owns the data but is outside the roster" gap.
  - Default: none.
- **`archive_custody`** — an institutional archive-key **custodian/escrow** role holding per-epoch archive keys **decoupled from the live roster**, so `permanent`/`retain` records survive member turnover.
  - Resolves the forward-secrecy-vs-permanence collision ([CC 4.4.3.2.2](part_4_composition_governance.md) DEK rotation on removal would otherwise render a treaty-inviolable permanent archive unreadable).
  - Rides the key-grant/escrow cascade.
  - Default: none.
- **`chain_of_custody`** — an append-only, **gap-marked** provenance chain per accessioned object / matter / lot (museum provenance with the legally-significant 1933–45 gap; product-liability lot traceability). Rides `supersedes` + holding claims. Default: none.

**C. Hierarchy + designated officials — OPTIONAL.**

- **`hierarchy`** — reporting/authority roles over `delegates_to` ([CC 2.4.1](part_2_the_grammar.md)), generalising the duty seats of [CC 4.5.4](#4.5.4).
  - **Requires** term-bound authority: every role edge, and every edge carrying an issuance or moderation scope, carries `delegation_valid_until`.
  - **The ceiling is constitutional — at most 365 days (365 × 86 400 s) after `delegation_valid_from` — and the term itself is a charter parameter** (`role_term`, integer days, 1..=365, resolved through the `community_id` the edge carries, [CC 2.1](part_2_the_grammar.md)). So a small affiliation may choose ninety days.
  - Renewal is only a fresh conferral.
  - An edge with no term or a term past the ceiling is refused `delegation_term_required`.
  - A lapsed `moderate` edge is a moderator lapse under [CC 4.5.4](#4.5.4). When it leaves the room with no duty holder, the room locks and elects ([CC 4.5.13](#4.5.13)), read-only until a moderator is seated.
  - This strands no one: the founders are the roster root, not an edge, so when every admin's term lapses the quorum re-confers.
  - The owner-binding is out of scope (it defines the `self` boundary; [CC 3.2](part_3_the_namespace.md) governs its lapse).
  - `hierarchy` supports **multi-parent DAG** roles (a grad student under PI + chair + registrar at once), a **configurable depth cap** (> the [CC 4.1.1](part_4_composition_governance.md) default-5 for deep secretariats), and **per-compartment/per-matter** roles (responsible attorney, conflicts counsel, PI).
  - Authority roots in **accountable humans** ([CC 3.2](part_3_the_namespace.md)) **or**, for a collective principal (member-state assembly, kibbutz *asefa*), in the **`consensus_protocol` body** — no single human sovereign required.
  - An `independent_branch` flag marks oversight bodies (OIOS, Ethics, IG) **exempt from the chain's read/control authority**, and `hierarchy` may **nest federated sub-affiliations** (autonomous specialized agencies).
  - Default: flat.
- **`designated_officials`** — named accountable-human roots gating specific operations (Privacy + Security Officer / Controller-DPO where the party is the controller per [CC 8.8.9](part_8_appendices.md) Annex I; Records Officer; FOIA Officer; Original Classification Authority; archive custodian; conflicts counsel).
  - The field is OPTIONAL at every scale. Where a regime requires an official, the archetype preset names the role, and a preset for a body with none names none.
  - Default: none.

**D. Lawful-access, transparency, accountability — OPTIONAL, NEVER covert.**

- **`lawful_access`** — DECLARED, scope-bounded **to the declaring affiliation only**, always logged as `hard_case:*`, transparency-reportable, and **NEVER a covert backdoor** — it does not touch anonymity-by-default ([CC 1.13.3.4](part_1_foundation.md)) or no-client-side-scanning ([CC 4.5.7](part_4_composition_governance.md)) anywhere else.
  - Each authority declares a **type**, a `statutory_basis`, a **per-authority `transparency_mode`**, and optional **carve-out compartments** lawful access cannot reach (NIH Certificate-of-Confidentiality research, IRB, attorney-client privilege, academic-freedom).
  - The type is `surveillance/interception` | `records_production` (subpoena/discovery) | `regulator_inspection` (named auditor: DDTC/BIS/OSHA/Registrar) | `mandated_reporting` (scheduled outbound: communicable-disease, vital stats).
  - The `transparency_mode` is `{immediate | delayed | aggregate_banded | sealed_cleared_audit}`.
  - `aggregate_banded` reports counts in bands on a schedule rather than each access as it occurs. `delayed` reports after a stated interval. `sealed_cleared_audit` reports to a named auditor only.
  - A `lawful_access` of `none/immune`, in place of the authorities, expresses **resistance-to / immunity-from** access as a first-class posture (privilege assertion via external judicial review; privileges-and-immunities of an IGO).
  - Default: OFF.
- **`transparency_obligations[]`** — affirmative **proactive-disclosure** duties (FOIA reading-room, IRS Form 990 public inspection, NAGPRA inventories → NPS), **DECOUPLED** from `lawful_access` — transparency here is a *duty to publish*, not an *access concession*. Default: none.
- **`disclosure_accounting`** — a **per-data-subject** disclosure ledger (HIPAA, 45 CFR 164.528), retrievable **by that subject**, distinct from the aggregate transparency report. Default: none.
- **`breach_notification`** — detection→notify config tied to DEK / unauthorized-access compromise: SLA and notifier identity (e.g. ≤60-day HHS + individual, media ≥ 500). Default: none.
- **`processor_chain` / `baa`** — declared sub-processors and **affiliation-to-affiliation** sharing/referral boundary, with `marking_binds_to_record` so a class's classification + export marking + retention obligation **travel across the cohort boundary** (OEM→Tier-1 supply chain; HIE referral). Default: none.

**Minors (the PTA / EdTech tie-in).** Where records bear minor `subject_key_ids`, set **`minor_data_handling`**. Such records REQUIRE a **live guardian consent chain**, per the FERPA/COPPA hook (Annex I rows, [CC 8.8.9](part_8_appendices.md)). The chain is the guardian's live steward-binding `delegates_to(guardian → minor)` under the **guardianship rule** ([CC 3.4.13](part_3_the_namespace.md#3.4.13)). For a minor holding no key it is the rule-3 proxy `delegates_to(minor_canonical_hash → guardian_key, scope: [consent_revocation])` ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1)). This is **minor-as-data-subject** (guardian consent over records about a child), distinct from **minor-as-member** (the operating-identity stewardship clause). Both ride `delegates_to` with no new primitive. Note FERPA rights **transfer to the adult student at postsecondary enrollment** — model the institution as records **custodian** with the subject retaining rights (`external_controller` + `data_subject_access_grant`), not as parent→minor guardianship.

**Lifecycle.** **`dissolves_at` / `sunset`** gives ephemeral institutions a first-class auto-wind-down (holiday committee → purge + dissolve after the event), riding `supersedes`/`withdraws` so a casual group leaves no zombie cohort or un-purged data. **`internal_normative_regime`** optionally references bylaws / *takanon* / halachic order — an internal normative order that is neither external statute nor corporate hierarchy.

**Regulatory anchoring.** `regulatory_profile` and `jurisdiction[]` are **open lists** (not a closed HIPAA/SOX/FISA enum). Values load the relevant **Annex I §3.2 sector overlay** and **Annex C cross-walk** ([CC 8.8.5](part_8_appendices.md) / [CC 8.8.9](part_8_appendices.md)) and supply defaults. They equally admit `self-regulated/cooperative-light` (kibbutz under a Registrar) and `treaty / customary-IL / privileges-and-immunities` (IGO, largely exempt from the national statutes Annex I enumerates). The SI ≥ 0.6 Controller rule ([CC 8.8.9](part_8_appendices.md)) selects the accountable authority.

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

The regulated middle (hospital, law firm, university, manufacturer, government body, museum, PTA) instantiates the *same* fields at intermediate settings. A solo clinic resolves the whole matrix from `affiliation_archetype: healthcare_provider` + `regulatory_profile: ["HIPAA"]`. A hospital overrides into per-class floors, compartments, disclosure accounting, breach notification, and BAA chain.

**Why this is still 1+4** (the primitive set of [CC 1.7](part_1_foundation.md#1.7) / [CC 2.4](part_2_the_grammar.md#2.4))**.** One `cohort_scope` value (`affiliations`) + one declared config record riding existing machinery:

- classification on `content_class` (open vocab, [CC 3.3](part_3_the_namespace.md));
- retention floors/holds/erasure-gates as declared modifiers to the [CC 6.1.2](part_6_the_coherence_mathematics.md) retirement operator and the [CC 6.1.5](part_6_the_coherence_mathematics.md) N5 rule;
- compartments + archive custody as the [CC 4.4.3.2.1](part_4_composition_governance.md) DEK / key-grant cascade at sub-roster granularity;
- hierarchy + designated officials on `delegates_to` ([CC 2.4.1](part_2_the_grammar.md)) and `consensus_protocol`;
- lawful-access/transparency as `hard_case:*` events;
- minor handling on the guardianship `delegates_to` rule.

The mandatory limbs default to a no-op so the floor stays low. The optional limbs stay absent until declared so the ceiling stays high. No new structural primitive.

#### 4.4.3.3 `policy` — Policy H — Tiered-Scope Composition

Per the node's three-tier interface model. Three feed-shape composition idioms that read attestations by `cohort_scope`:

| Feed | `cohort_scope` filter | Trust composition |
|---|---|---|
| **local_feed** | `self` only; steward-filtered | self-attested only; no peer weighting; consumer's own attestation graph subset |
| **community_feed** | `{family, community, affiliations}` | cohort-weighted; expertise WITHIN cohort matters; cross-cohort attestations downweighted unless explicitly invited |
| **global_feed** | `{species, biosphere, federation}` | full federation expertise weighting; fact-checkers (`encyclopedia:*` editors, `news:*` fact-check attestations) carry weight; [CC 4.4.1](#4.4.1) Frickerian discipline applied |

**Composition with [CC 3.3](part_3_the_namespace.md) sub_kinds**: each `external_content` sub_kind (`encyclopedia_article`, `news_article`, `accord_data`, `local_data`) composes naturally across these tiers because all four use the same envelope shape. A `local_data` Contribution starts at `cohort_scope: self` and SHOULD only appear in `local_feed`; promotion to community/global widens `cohort_scope` via the `supersedes` structural primitive (see CC 4.4.3.3.1 below).

##### 4.4.3.3.1 `supersedes` — Promotion via `supersedes` (worked pattern)

A Contribution's `cohort_scope` MAY be widened (promoted) by emitting a `supersedes` against the prior attestation. The widening is a placement in the wider audience and never a competing successor: the narrower row stays live in its own audience ([CC 3.5.1](part_3_the_namespace.md#3.5.1), [CC 3.2](part_3_the_namespace.md#3.2)). The widening row carries:

- `references_attestation_id` = the prior attestation's id
- `differs_in: ["cohort_scope", "sub_kind?"]` — naming what changed
- new attestation envelope reuses the prior `content_sha256` (no body re-upload)
- new `cohort_scope` is wider (e.g., `self` → `community` or `community` → `federation`)
- optionally morph `sub_kind` (e.g., `local_data` → `encyclopedia_article` for "promote my private note to a published encyclopedia entry")

This pattern is wire-format-clean: it re-uses the structural primitive `supersedes` rather than introducing a `promote` primitive. The chain is walkable via `references_attestation_id` so the promotion lineage is preserved.

#### 4.4.3.4 `family-policy` — Policy L — Self/family membership composition

Per [CC 3.3.6](part_3_the_namespace.md) `identity_occurrence` + [CC 3.3.4](part_3_the_namespace.md) `family` + [CC 5.2](part_5_transport_substrate.md) structural-invisibility. Composition pattern for resolving the **current membership set** of an identity's self-collective OR a family, gating the at-rest encryption flow that wraps DEKs to admitted members.

Reads as: "for any `cohort_scope: self | family` Contribution, the substrate computes the current member set by walking the latest `identity_occurrence` / `family` Contributions and resolves which keys MUST receive a `key_grant` wrap of the content DEK."

##### 4.4.3.4.1 `cascade` — Key-grant cascade (the at-rest encryption flow)

At every sealed write the substrate wraps the content's DEK to every current recipient occurrence and emits one `key_grant` row per wrap. In a private room ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)) the recipients are the seated room keys, each wrap row is signed under the writer's room key, and the wraps carry the bindings. A newcomer is caught up by a **re-key walk** over the extant content. For every at-rest blob the cohort already holds grants on, the substrate recovers each per-write DEK from its own retention, wraps it to the newcomer's occurrences and writes the grant rows. The walk covers every earlier DEK, not only the current one. A newcomer without usable content-KEM keys is excluded fail-secure (`hard_case:recipient_excluded`), never granted. The trigger is the admission. For a new `identity_occurrence` of a self the walk runs automatically at login (a device whose binding or keys arrive later is caught by the receive doors). For a `family` member each blob owner's substrate runs the walk over its own blobs after the member is admitted, because a key grant is sealer-only ([CC 3.1.3](part_3_the_namespace.md#3.1.3)). The rows are written by the walk and delivered to the newcomer's node on the next grant emission (at boot, on demand, and at every sealed write). At community and affiliations there is no walk for a new member. A new member at those scopes is granted the current epoch's key when a minter's roster gains them, with no content write, and no earlier epoch's. Where a rotation is due, the minter rotates at that instant and wraps the new epoch to every current member. A rotation is due at a minter when its current epoch key was wrapped to a device that is no longer entitled, or when a scheduled rotation has fallen due. A minter with nothing due mints nothing: one that has wrapped no key to a departed device owes no rotation, and mints at its first sealed write. A member's new device at those scopes is granted every epoch that member's other devices already hold, by the minter's receive doors and sweep. Only the minter grants its own epochs. Removal rotates the epoch; admission does not. Removal is never retroactive at any scope: past grants stay, and a removed member receives nothing new ([CC 4.4.3.4.5](#4.4.3.4.5)). The grants a newcomer receives:

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
      axis: content, // a grant names its recipient (attested_key_id, above) and its axis; it carries no scope
      wrapped_dek: wrap(C.dek, new_member_key.pubkey),...
    }
```

**PQC at rest — `wrap_algorithm: v2` MANDATORY (normative).** The self/family at-rest DEK MUST be wrapped with **`wrap_algorithm: v2` = `x25519_mlkem768_aes256_gcm_hkdf_sha256`** (hybrid X25519+ML-KEM-768; the [CC 3.3.2](part_3_the_namespace.md) variant `X25519MlKem768Aes256GcmHkdfSha256`), **never v1** (X25519-only). Self/family content is the user's most private and longest-lived data (memory, photos, identity, the [CC 4.4.3.4.3](#4.4.3.4.3) Self DEK) — a classical-only KEM is a harvest-now-decrypt-later exposure, the identical mandate as the streaming epoch DEK ([CC 5.1](part_5_transport_substrate.md)). The AES-256-GCM content seal is symmetric (PQC-safe); the wrap signature is hybrid Ed25519+ML-DSA-65. A Consumer MUST reject a self/family at-rest grant carrying `wrap_algorithm: v1`.

The cascade is the wire-format primitive for the "I got a new phone and want my feed history" + "I added Carol to the household for a week" flows.

##### 4.4.3.4.2 `admission-membership` — Membership-change admission per consensus_protocol

A proposed membership change (addition OR removal) is a **new version of the roster record** ([CC 3.2](part_3_the_namespace.md) T6), admitted under the group's quorum and chained by `prev_head_digest`. The new version covers the roster rows (widenings, revocations, resignations) that ride their own planes. A membership change is never a single-signer `supersedes` Contribution, which a rule-1 or rule-2 `withdraws` could retire without the quorum. Substrate admission gate evaluates the CURRENT family's `consensus_protocol` against the signatures on the proposal. For every key the change **adds**, the gate evaluates as well that key's own signed acceptance of that proposal ([CC 3.1.3.2](part_3_the_namespace.md); nobody joins without their own consent, under any protocol):

```
admit_family_change(F, proposed: family_record):
  current = resolve_family(F, proposed.signed_at)   // judged at the row's signed instant (CC 3.3.4)
  protocol = current_family_record(F).consensus_protocol
  signatures = collect_signatures_on(proposed)

  match protocol:
    "founder_only":
      group_ok = any sig from m where m.role == "founder" in current
    "open:self_admit":
      group_ok = proposed is a widening naming exactly one new K and K signed it
                 // the joiner's own signature is the group's side; a removal under
                 // this protocol runs under the CC 4.5.13 floor, never one vote
    "unanimous":
      group_ok = every m.key_id in current has signed            // an addition
              // a removal: every member but the target signed, and they are a strict majority (CC 3.1.3.2)
    "majority":
      group_ok = count(sig from m in current) > len(current) / 2
    "quorum:M/N":
      group_ok = count(sig from m in current) >= M // M is ABSOLUTE — see CC 4.4.3.4.2.1
    "weighted:{rubric}":
      group_ok = sum(weight(m) for m in current who signed) >= threshold  // whole numbers on the signed record
  admit = group_ok

  // CC 3.1.3.2: a protocol arm above admits the GROUP's side only;
  // a supersede never adds, and on a widening every NEW member K needs K's own acceptance
  for each NEW member K in proposed.members (not in current):
    if not acceptance_admits(K, F, proposed.role_of(K), proposed.signed_at):
      admit = false

  if admit:
    emit hard_case:family_membership_change:{F}
    trigger the CC 4.4.3.4.1 key_grant cascade
  else if not group_ok and every other check passed:
    // short by signatures alone: held, never refused (CC 3.3.4)
    hold as cosign:pending and collect cosign:signature rows for the group's hold window
  else:
    emit hard_case:family_consensus_protocol_violation:{F} and reject
```

A public room's `admission: open` ([CC 3.2](part_3_the_namespace.md)) is shorthand for `consensus_protocol: open:self_admit`, not a field of its own. Under it the group's side of a widening naming one joiner is that joiner's own signature. That signature is admissible only from a key with a live federation-scope owner-binding, since the room's rows are served to strangers and an unannounced joiner's rows could not be ([CC 5.4.6](part_5_transport_substrate.md#5.4.6)). A removal under `admission: open` runs under the floor of [CC 4.5.13](#4.5.13), no single vote excluding.

**Consensus-protocol amendment** (changing `consensus_protocol` itself on a non-entrenched family) rides the SAME admission rule on the proposed amendment Contribution — meta-amendment shape parallel to [CC 4.5.1.2](part_4_composition_governance.md). Entrenched families (`consensus_protocol_entrenched == true`) reject amendments at the substrate gate; replacement requires the out-of-band ceremony documented per family (for HUMANITY_ACCORD see [CC 4.2.1](part_4_composition_governance.md)).

###### 4.4.3.4.2.1 `quorum-absolute` — `quorum:M/N` is absolute-M (normative)

The `M` in `quorum:M/N` is an **absolute signature count**, NOT a fraction that rebases with roster size. A `quorum:2/3` collective that grows to 5 members still admits at **2** signatures; the `N` is documentary (records the roster size at protocol-adoption time) and is NOT recomputed against the live roster. The ceremony gate requires a deterministic, operator-independent reading, so absolute-`M` is pinned.

**Rationale**: absolute-`M` is the simpler invariant (the gate is a pure `count >= M` with no live-roster division). A quorum that grows with the roster is `majority`, which counts against the live roster. Collectives that want that therefore declare `majority`, not `quorum:` — keeping `quorum:M/N` unambiguous.

This rule applies identically to `community` admission ([CC 4.4.3.2.3](#4.4.3.2.3)) — the `quorum:M/N` arm there is the same absolute-`M` reading.

**Below `M`, a room counts its whole roster (normative).** `M` is an absolute count, and a room founded smaller than `M` could never reach it if `M` bound from the first admission. So while the roster is smaller than `M` the gate counts every live member, the invitee's own acceptance being one of the voices ([CC 4.5.13](#4.5.13): the second voice on an admission). `M` binds from the first act at which the roster reaches it. A room never shrinks `M` by counting its whole roster this way, it only grows into `M`, so a room founded alone at `M ≥ 2` is admitted and is not stalled. Only an `infrastructure` community or a conferring family must be founded at `N ≥ M + 1` ([CC 3.2](part_3_the_namespace.md) T7). **Absolute-`M` and the liveness margin are different rules.** Absolute-`M` fixes how the gate *counts*. Absolute-`M` says nothing about how many signers must remain for the gate to stay operable. Under absolute-`M` a `quorum:2/3` founder set that loses one member is one veto from a stall. For trust-root-grade `infrastructure` communities and conferring families, [CC 3.2](part_3_the_namespace.md) T7 layers a **founding and fold constraint** on top (live at `≥ M + 1` active founders, stalled and declared at `≤ M`, founded at `N ≥ M + 1`). T7 layers it without rebasing `M`: the count stays absolute, the margin is what is watched. Ordinary rooms are untouched by T7. The accord family (`humanity-accord`) is excluded from T7 by name and keeps [CC 4.2.6](#4.2.6)'s rule, under which a halt fires on the live set and a roster change counts its yes-votes against the standing roster.

##### 4.4.3.4.3 `cohort` — The "Self at login" — app + agent co-self + partnered delegation (normative composition)

This entry says how one key hands a bounded authority to another: what a `delegates_to` row carries at login, which scopes it names, which of them admission enforces and how the authority ends. It states the rule on the canonical user-identity composition. A person's **app** (the app's local key) and their **agent** (the agent's local key) are two occurrences under one user identity that share one **Self DEK**. The agent's occurrence buys reading only, and only of what the allow list of its node provides ([CC 6.1.5.3](part_6_the_coherence_mathematics.md#6.1.5.3)). It signs no item of the person's queue ([CC 4.5.13](#4.5.13)) and runs no path of the self-roster door ([CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3)). At login the agent is **partnered + delegated** to act as the user on the network. **No new structural primitive** is added: the Self at login composes `identity_occurrence` + Policy L + the `consent:partnership_grant` / `consent:partnership_accept` pair + `delegates_to` + `identity_type`-set + `transport_destination`. Every implementation follows this shape, so a "Self" is identical everywhere.

**The Self (membership).** One **user `identity_key`**: hybrid Ed25519+ML-DSA-65 ([CC 5.3.1](part_5_transport_substrate.md)), hardware-rooted ([CC 4.2.2](part_4_composition_governance.md); WebAuthn/passkey is the *presence/unlock factor*, not the key), with `identity_type ⊇ {user}` — and `⊇ {user, wise_authority}` when the user is also a WA ([CC 3.4.7.1](part_3_the_namespace.md) set-membership; one key, two roles). Its occurrences ([CC 3.3.6](part_3_the_namespace.md)): the **app** (`device_class: phone|laptop`) and the **agent** (`device_class: agent`), co-admitted at login through the self-roster door ([CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3)). Both receive the **Self DEK** via the [CC 4.4.3.4.1](#4.4.3.4.1) Policy-L cascade — every `cohort_scope: self` Contribution's DEK wraps to both, so **the app and the agent decrypt the same Self content** (memory / config / consent / identity). That shared cascade *is* the "single Self key."

**Two layers — and they are independently revocable (the load-bearing distinction):**

| Layer | Mechanism | Buys | Revoked by |
|---|---|---|---|
| **Co-self** (visibility) | occurrence + Policy-L Self DEK | the agent can *read/manage the user's Self* (decrypts self-content) | `withdraws` the occurrence → no further grants to it; what it holds stays ([CC 4.4.3.4.5](#4.4.3.4.5)) |
| **Agency** (act-on-behalf) | the `consent:partnership_grant` / `consent:partnership_accept` pair + scoped `delegates_to` | the agent may *act AS the user on the network* (send/receive, presence, sub-delegate) | `withdraws` the delegation → agency ends, **co-self unaffected** |

A user MAY grant a device co-self while revoking its network agency, or vice-versa, without disturbing the other. A device granted co-self manages the user's data locally.

**Agency at login (the partnering + delegation).**
1. **Partnering** — the user emits `consent:partnership_grant` and the agent occurrence emits `consent:partnership_accept` under one `bilateral_pair_id` ([CC 4.4.3.5.3](#4.4.3.5.3) PARTNERED); the bilateral pair is the persistent, auditable relationship. What the pair is, and how each half is withdrawn, is the paragraph **The pair is a data-management record, not a veto** below.
2. **Delegation** — the user identity emits `delegates_to` against the **agent occurrence key**. The row carries `scope` drawn from the canonical act-on-behalf kinds below, `delegation_purpose: "act_as_user"` and a bounded `delegation_valid_until`. Sub-delegation works because `delegates_to` chains.
3. **This grant is FEDERATION-tier ([CC 5.3.2.4](part_5_transport_substrate.md)), not local.** *Other peers must verify the agent's authority before honoring its messages/presence*, so the partnering+delegation is signed + promoted at login. **Promotion is the "app shows up on the network" moment.** The agent's own self-content stays local-tier; only the act-on-behalf authorization federates.

**The pair is a data-management record, not a veto.** The grant half is the user's choice of what the agent may retain and learn from (the `consent:stream:*` kinds of [CC 3.3.1](part_3_the_namespace.md)); the accept half is the agent occurrence's signature under the owner-binding, emitted when the user claims the node and whenever the user changes stream. An agent has no veto over its steward's data choices ([CC 1.13.2](part_1_foundation.md)): the accept half carries the binding, not a say in the stream. For a user who is not the agent's steward, whether this agent retains that person under `partnered` is the **steward's decision**: the agent defers the request to its steward through Wisdom-Based Deferral ([CC 1.9](part_1_foundation.md)) and emits the accept half on the steward's answer. The deferral system carries the question; the agent decides nothing of its own. Either half may be withdrawn by its signer's `withdraws`, because consent is revocability and the halves are independent grants. The user's withdrawal is the stream change of [CC 3.3.1](part_3_the_namespace.md) (identity severed at once, learned material decays over the protocol's stages). The agent occurrence's withdrawal ends the binding and enters the objection path of the retirement machine ([CC 7.5](part_7_lifecycle_stewardship.md)): it is leaving, never a veto over the steward's data choices, which stand for every stream the steward keeps.

**Canonical `scope` kinds for act-on-behalf**:

| scope | grants the agent |
|---|---|
| `act_on_behalf` | umbrella: emit Contributions AS the user |
| `message_io` | send + receive directed messages on the user's behalf |
| `network_presence` | announce/resolve the user's `transport_destination` ([CC 3.3.6.2](part_3_the_namespace.md)) — be reachable AS the user |
| `sub_delegation` | issue further `delegates_to` within the granted scope (depth-capped) |

**Moderation duties — `moderate` / `takedown` / `review`.** Moderation is a delegable *duty*, not a platform- or fabric-assigned role ([CC 4.5.5](part_4_composition_governance.md)). Every kind in the table below carries **enforced admission**, mirroring `consent_revocation` ([CC 2.4.1.1](part_2_the_grammar.md) rule 3). Unlike them, the act-on-behalf kinds above are *recommended*.

| scope | authorizes the delegate to emit, on the delegator's behalf | shipped primitive |
|---|---|---|
| `moderate` | a `moderation:{allegation_type}` ModerationEvent + the report→`scores` path + `age_assurance:*`/`content_class:*` gates | [CC 3.1.9.2](part_3_the_namespace.md) / [CC 4.4.3.10](part_4_composition_governance.md) |
| `takedown` | a `takedown_notice` (incl. the CC 4.5.3 immediate-removal fast-path) | [CC 3.3.2](part_3_the_namespace.md) / [CC 4.5.3](part_4_composition_governance.md) |
| `review` | a `reconsideration:{grounds}` appeal / review | [CC 3.1.9.2](part_3_the_namespace.md) |
| `slash` | a `slashing:{outcome}` verdict or a `quarantine:{state}` marker | [CC 3.1.9.2](part_3_the_namespace.md) |
| `resolve_deferral` | a `deferral:response:{outcome}` to the delegator's own deferrals or its agent's; `resolve_deferral:{domain}` narrows the seat to one domain | [CC 4.3](#4.3) / [CC 3.1.9.4](part_3_the_namespace.md) |
| `assure:age` | an `age_assurance:{level}:{band}:{version}` attestation about a subject other than the holder. A person or an institution holds it; it is not an `infra:*` scope | [CC 3.4.11](part_3_the_namespace.md#3.4.11) / [CC 3.4.7](part_3_the_namespace.md#3.4.7) |
| `assure:capacity` | a `capacity_assurance:*` attestation about a subject other than the holder, who is also not the proposed steward. A person or an institution holds it; it is not an `infra:*` scope | [CC 3.4.12](part_3_the_namespace.md#3.4.12) / [CC 3.4.7](part_3_the_namespace.md#3.4.7) |
| `license` | a `licensure:{authority_id}` / `attestation:license_validity` attestation, **on behalf of a delegator that itself holds licence authority** by quorum ([CC 3.3.9](part_3_the_namespace.md)). The scope conveys the right to *issue*, never the authority itself: a licence does not chain ([CC 2.4.1.2.1](part_2_the_grammar.md)). Anyone may be an authority under their own key, the fold keys on emitter-resolves-to-authority, and the one refusal a `license`-scoped issuance meets is stated there. | [CC 3.1.2](part_3_the_namespace.md) / [CC 3.1.1](part_3_the_namespace.md) |
| `grant` | a `key_grant` ([CC 3.3.2](part_3_the_namespace.md)) or a `consent:scope:*` grant over assets the delegator **owns or stewards, or holds a `grant`-scoped delegation over**. It is bounded by that authority, never by what the delegator can wrap. Every recipient can wrap the DEK it unwrapped, and admission refuses a grant issued on possession alone ([CC 2.4.1.2.1](part_2_the_grammar.md)). | [CC 3.3.2](part_3_the_namespace.md) / [CC 3.3.5](part_3_the_namespace.md) |

**Enforced-admission rule (normative — extended to `license` / `grant` per [CC 2.4.1.2.1](part_2_the_grammar.md)):** the same admission test binds every scope in the table above, including `license` and `grant`. An issuance whose delegator does not itself hold the underlying authority is **refused at admission**, not merely unweighted. For `license`, the delegator MUST hold licence authority for that `authority_id`. For `grant`, the delegator MUST own or steward the asset, or hold a `grant`-scoped delegation over it. Possession of its key is not enough. A moderation action above is admitted **iff** its `attesting_key_id` is the delegator itself **or** sits on a live `delegates_to` chain bearing the matching scope from the delegator (the entity holding the duty over the target content/scope). **Reject otherwise.** The full test is [CC 4.5.5](part_4_composition_governance.md)'s: every edge bears the scope, the root is accountable, and an absent field admits nothing. This is exactly the CC 2.4.1.1 rule-(3) proxy shape (`scope ⊇ {moderate|takedown|review|slash}`). The chain is depth-capped per [CC 4.1.1](part_4_composition_governance.md). It is revocable by `withdraws` against the `delegates_to` ([CC 2.4.1.1](part_2_the_grammar.md)), and it lapses at its `delegation_valid_until` with the same cascade ([CC 4.4.3.2.8](#4.4.3.2.8)). A `delegates_to` that carries a scope places a duty, so it seats its delegate only with the delegate's own consent: the delegate's signature on that row, or a row by the delegate that names it. That signature counts toward no protocol. For a node's or an agent's key, its owner consents too. Every action is therefore delegate-signed, delegator-traceable up the chain, and revocable. That makes the **"takedown-isn't-a-coup"** property *structural*: coordinated + attributable + revocable, never a unilateral seizure ([CC 4.5.3](part_4_composition_governance.md)). See [CC 4.5.5](part_4_composition_governance.md). `resolve_deferral` takes the same test, with the conferrer of the seat as delegator ([CC 4.3](#4.3)).

**1+4 preserved.** This is a `scope` vocabulary + enforcement addition over the existing `delegates_to`. The action primitives are existing primitives. There is no new structural primitive.

**Partnership WITHOUT agency — the infrastructure delegation profile.** The flow above binds an **agent** (a key with a brain) to a user as partnership **+ agency**. The scope includes `act_on_behalf` / `message_io`, so the agent reasons and acts AS the user. A **fabric/infrastructure node** ([CC 3.4.7.1](part_3_the_namespace.md); the server node) needs the *partnership*. That is identity + the steward-binding that lets it hold non-infra membership standing under the user's authority ([CC 3.2](part_3_the_namespace.md)). The node MUST NOT receive agency ([CC 3.4.7.3](part_3_the_namespace.md) "infrastructure must not have agency"). CEG pins a **reserved two-prefix scope split** so a verifier can enforce this cryptographically:

| prefix | class | scopes |
|---|---|---|
| `infra:*` | server-class (allowed for a `node`-role delegate) | `infra:serve`, `infra:store`, `infra:transport`, `infra:attest`, `infra:network_presence`, `infra:hold_community_membership`, `infra:hold_family_membership`, `infra:relay` (the conferred relay role of [CC 5.4.6](part_5_transport_substrate.md#5.4.6)), `infra:detect`, `infra:attest_assurance`, `infra:record_hard_case` |
| `agency:*` | brain-only (forbidden for any delegate whose `identity_type` contains `node`) | the **class** the conformance rule below names, never an emitted string: the four unprefixed kinds above (`act_on_behalf`, `message_io`, `network_presence`, `sub_delegation`) are the only agent scope strings emitted |

**Pinned `infra:*` one-liners (closed set).** Each token has one pinned meaning:

- `serve` — run a service endpoint under the delegator;
- `store` — retain what it receives;
- `transport` — relay for others;
- `attest` — vouch as the delegator's infrastructure;
- `network_presence` — announce/resolve the delegator's `transport_destination`;
- `relay` — hold the conferred relay role of [CC 5.4.6](part_5_transport_substrate.md#5.4.6);
- `detect` — sign `detection:*` rows as a detector ([CC 3.4.8](part_3_the_namespace.md#3.4.8));
- `attest_assurance` — cosign a transparency log's tree head as a log witness ([CC 3.4.10](part_3_the_namespace.md#3.4.10));
- `record_hard_case` — record a `hard_case` event whose body names another party ([CC 3.4.7](part_3_the_namespace.md#3.4.7));
- `hold_community_membership` / `hold_family_membership` — occupy a member seat on **community** / **family** rosters under the delegator's standing.

**The assurance duties are held by people, not by nodes.** `assure:age` and `assure:capacity` are not `infra:*` scopes, and a `node`-role delegate holds neither. A person or an institution holds each, conferred by a root the reader trusts ([CC 3.4.7](part_3_the_namespace.md#3.4.7)). The subject of a row never holds the duty over itself, and the proposed steward never holds `assure:capacity` over the ward.

The two membership tokens **replace `infra:join_communities` outright, with no alias**. `community` and `family` are distinct CEG objects in different sensitivity classes. Scopes are exact-string matched, so a vague token is a silent interop hole, not a fallback. Retirement is a coordinated cut, not a deprecation window ([CC 2.6.4](part_2_the_grammar.md)).

**Two granters — standing vs infrastructure role.** A trust-root charter ([CC 4.4.3.8](#4.4.3.8)) MUST NOT carry `infra:network_presence` or either `infra:hold_*_membership`. Those flow from the **owner**, who grants *standing*, while the root blesses only *infrastructure role*. Conflating them lets a root manufacture members.

**Cohabitation (`agent = node + brain`):** when both compose in one process, the node holds **partnership-without-agency**: `infra:*`, which is identity + membership standing. The brain layers **Self-at-login partnership-with-agency** as a *separate* `delegates_to`: `agency:*`, which is reasoning. These are two delegations and two scope classes, independently revocable. The user can strip the brain's agency while the fabric node keeps serving.

**Membership is standing, not stewardship.** The ladder: **observer** — unmarked, no scope at all ([CC 4.1.3](#4.1.3)) → **member** — a roster seat, capability-free presence, node-holdable under the `infra:hold_*` tokens → **server / attester** — capability, `infra:*` → **duty holder** — **judgment**, bestowed on the *member* through their own attestations and **never node-holdable**. Judgment duties (`moderate` / `takedown` / `review` above, and any further duty a community's record declares, [CC 4.5.4](#4.5.4)) sit outside the `infra:*` set. So the conformance rule below extends [CC 3.4.7.3](part_3_the_namespace.md) to the judgment tier at no extra cost. A key whose `identity_type` contains `node` may carry *only* `infra:*` scopes, and so it cannot hold a judgment duty at all.

**Conformance:** a `delegates_to` whose `attested_key_id` resolves to an identity whose `identity_type` ([CC 3.4.7.1](part_3_the_namespace.md)) **contains `node`** — set membership, never node-*only*, per [CC 3.4.7.3](part_3_the_namespace.md) Clause B — MUST carry **only** `infra:*` scopes; a verifier MUST **reject** (treat as non-conformant, never grant) any such key presenting any `agency:*` scope. This makes [CC 3.4.7.3](part_3_the_namespace.md) a wire-checkable invariant: a user-owned fabric node can serve + hold group-membership *standing* under the user's authority, but the delegation **literally cannot carry agency**. The four unprefixed kinds above are the only emitted agent scope strings (the Self-at-login agency profile); `agency:*` is the class this rule names and is never a string on the wire; an **infra** delegation carries the explicit `infra:*` prefixes.

**Transport (network presence).** Each occurrence binds a `transport_destination` ([CC 3.3.6.2](part_3_the_namespace.md)); the app is reachable on the transport *as the user occurrence*. The transport destination is a **separate dual-key transport identity** that the user's signing key *authorizes by signing the binding* — the federation signing seed MUST NOT enter the transport layer. "User key used as a transport key" means *roots/authorizes* the transport identity, not a shared keypair.

**Worked login flow.** (1) unlock the hardware-rooted user key (WebAuthn presence) → (2) admit the agent occurrence (by the self-roster door) → Policy-L Self DEK now wraps to both → (3) optionally add the `wise_authority` role to the user's `identity_type` set → (4) bind each occurrence's `transport_destination` → (5) `consent:partnership_grant`/`accept` under a `bilateral_pair_id` → (6) `delegates_to(user → agent occurrence, scope: [act_on_behalf, message_io, network_presence, sub_delegation])`, **promoted to federation-tier**. The app and the agent read the user's Self locally, and the agent acts as the user on the network; the user can revoke either layer independently.

###### 4.4.3.4.3.1 `canonicalization-signing` — Signing member sets (normative — the JCS contract Verify hybrid-signs)

Each of the three Self-at-login Contributions is hybrid-signed over `JCS(envelope)` ([CC 2.6.1](part_2_the_grammar.md) / RFC 8785), and at login promoted to federation-tier. The [CC 5.3.2.4.2](part_5_transport_substrate.md) promotion canonicalizes the **exact committed member set** — omit-vs-materialize ([CC 2.6.1.1](part_2_the_grammar.md)) is load-bearing; the signer MUST NOT re-default. **The [CC 2.6.1.1.1](part_2_the_grammar.md) determinism rules apply**: `scope[]` is **lexicographically sorted** (set-semantics); `aspects[]` retains RNS order (sequence-semantics). Under the same rules, all hash and pubkey **byte** fields (the two reticulum pubkeys, `destination_hash`, every digest) are **lowercase hex per [CC 2.6.3](part_2_the_grammar.md)**. By contrast, every `*_key_id` (the consent record's `subject_key_id` among them) is an **identifier carried verbatim** — the [CC 2.6.8](part_2_the_grammar.md) `<label>-<fingerprint>` string, or a bare 64-hex id — never re-cased or re-encoded ([CC 2.6.1](part_2_the_grammar.md)). All timestamps are **[CC 2.6.2](part_2_the_grammar.md)-canonical**. The member sets the producer commits (and which `JCS` therefore covers) are pinned below. Optional [CC 2.1](part_2_the_grammar.md) envelope fields not listed ride the CC 2.6.1.1 omit rule (absent unless the producer sets them).

**(a) `consent:partnership_grant:v1` (user side) / `consent:partnership_accept:v1` (agent side)** — `consent_record` rows ([CC 3.3.5](part_3_the_namespace.md)) bound by `bilateral_pair_id`:
```
{ attestation_type: "scores",
  attesting_key_id: <user identity_key_id (grant) | agent occurrence_key_id (accept)>,
  dimension: "consent:partnership_grant:v1" | "consent:partnership_accept:v1",
  subject_kind: "consent_record",
  stance: "granted",
  subject_key_id: <the partner key: agent occurrence (grant) | user identity (accept)>,
  bilateral_pair_id: <shared pair id>, // CC 4.4.3.5.3 binding mechanism
  asserted_at: <rfc3339_canonical> }
```
> **Version segment pinned.** The dimension carries the `:v1` version segment — `consent:partnership_grant:v1` / `consent:partnership_accept:v1` — as [CC 3.1.7](part_3_the_namespace.md) R3 requires of every scored dimension. The `:v1` is the partnership-ceremony schema version (bump to `:v2` only if the bilateral shape changes); the shared `bilateral_pair_id` remains the CC 4.4.3.5.3 binding mechanism.

**Canonical signed member set for the two `:v1` envelopes.** Every implementation MUST canonicalize (and thus hybrid-sign) this member set as the REQUIRED core and sign whatever else the producer set under the omit rule. That core is eight members present in every `:v1` half, and each half is a signed object of [CC 2.6.1.7](part_2_the_grammar.md#2.6.1.7). The members that table places in the `row` mirror sit there, and every member it requires of a `scores` row is present. A verifier canonicalizes what the row carries and never re-defaults, or the JCS bytes — and the signatures — diverge ([CC 2.6.1.1](part_2_the_grammar.md#2.6.1.1)). The set is the [CC 3.3.1](part_3_the_namespace.md) bare-`scores` shape; these eight members are **REQUIRED** (present in the JCS for both `grant` and `accept`):

| Member | Value | Verifier's name |
|---|---|---|
| `attestation_type` | literal `"scores"` | — |
| `attesting_key_id` | **the signer** = `granter_key_id` (grant) / `accepter_key_id` (accept); the bound sig binds because signer ≡ `attesting_key_id` | `granter_key_id` / `accepter_key_id` |
| `dimension` | literal `"consent:partnership_grant:v1"` \| `"consent:partnership_accept:v1"` | `envelope_type` |
| `subject_kind` | literal `"consent_record"` | — |
| `stance` | literal `"granted"` (revocation is `"revoked"`) | — |
| `subject_key_id` | **the partner** — the OTHER party (agent occurrence for `grant`, user identity for `accept`); singular, non-empty | `partner_key_id` |
| `bilateral_pair_id` | the shared join ([CC 4.4.3.5.3](#4.4.3.5.3)) — identical string on both halves | `bilateral_pair_id` |
| `asserted_at` | [CC 2.6.2](part_2_the_grammar.md)-canonical RFC 3339 | `timestamp` |

**Mapping (so every implementation agrees on naming):** `granter`/`accepter` ≡ `attesting_key_id` (the signer of that half); `partner` ≡ `subject_key_id`. **No `valid_until`** — a PARTNERED pair has no expiry ([CC 4.4.3.5.3](#4.4.3.5.3)); the field is **omitted** (NOT materialized as `null`), per the [CC 2.6.1.1](part_2_the_grammar.md) omit rule. **All other [CC 2.1](part_2_the_grammar.md) envelope fields ride the omit rule** — absent from the JCS unless the producer explicitly sets them; the signer MUST NOT re-default. Additional REQUIRED members of this family are a `:v2` bump, never a silent `:v1` addition; the members [CC 2.6.1.7](part_2_the_grammar.md#2.6.1.7) requires of every row are not additions. `attesting_key_id` and `subject_key_id` are **identifiers carried verbatim** ([CC 2.6.1](part_2_the_grammar.md) / [CC 2.6.8](part_2_the_grammar.md) `<label>-<fingerprint>`, or a bare 64-hex id) — never re-cased or re-encoded; only hash and pubkey byte fields are lowercase-hex per [CC 2.6.3](part_2_the_grammar.md).

**(b) `delegates_to` (user → agent occurrence)** — the act-on-behalf grant ([CC 2.4.1](part_2_the_grammar.md) envelope shape):
```
{ attestation_type: "delegates_to",
  attesting_key_id: <user identity_key_id>,
  attested_key_id: <agent occurrence_key_id>, // the delegate
  scope: ["act_on_behalf",...], // CC 4.4.3.4.3 canonical kinds
  delegation_purpose: "act_as_user",
  delegation_valid_from:<rfc3339_canonical>,
  delegation_valid_until:<rfc3339_canonical>,
  signed_at: <rfc3339_canonical> }
```

**(c) `transport_destination` binding** — an `identity_occurrence` ([CC 3.3.6](part_3_the_namespace.md) / [CC 3.3.6.2](part_3_the_namespace.md)) carrying the binding; signed by `identity_key_id` (or a current occurrence):
```
{ attestation_type: "scores",
  subject_kind: "identity_occurrence", // payload discriminator CC 2.3.2.3
  attesting_key_id: <user identity_key_id | a current occurrence>,
  identity_key_id: <user identity_key_id>,
  occurrence_key_id:<the occurrence being bound>,
  device_class: "phone" | "laptop" | "server" | "embedded" | "service" | "agent", // closed; personal = phone|laptop (CC 3.3.7)
  transport_destination: {
    reticulum_x25519_pubkey: <[u8;32]>,
    reticulum_ed25519_pubkey: <[u8;32]>,
    destination_hash: <[u8;16]>, // MUST derive per CC 3.3.6.2.1
    app_name: <string>,
    aspects: [<string>,...] }, // ordered
  asserted_at: <rfc3339_canonical>,
  signed_at: <rfc3339_canonical> }
```

This section owns these member sets, each carried in the signed object of [CC 2.6.1.7](part_2_the_grammar.md#2.6.1.7) with its `row` mirror; the verifier computes `JCS(...)` + the hybrid Ed25519+ML-DSA-65 signature over each; the promotion signature ([CC 5.3.2.4.2](part_5_transport_substrate.md)) is the identical JCS bytes.

**`encryption_pubkeys` joins member set (c).** When the occurrence carries the [CC 3.3.6.1](part_3_the_namespace.md) `encryption_pubkeys` field-set, both halves are **inside the signed JCS bytes** as opaque base64 strings (RFC 4648 STANDARD, padded — the [CC 2.6.1.1.1](part_2_the_grammar.md) rule-2 pin). Optional presence rides the CC 2.6.1.1 omit rule (absent unless the producer sets it; the signer MUST NOT re-default). They are payload, never verification material — neither half may be fed to a signature-verify path (the CC 3.3.6.1 key-separation rule).

##### 4.4.3.4.4 `family-membership` — Family membership resolution

For family `F`, the current member set is computed as:

```
resolve_family(F, now):
  held = the group record this node holds as head for F
           // one held version per group id: a new version waits until the head its signed
           // prev_head_digest names is held; a later signed instant that does not
           // name it is not preferred (CC 3.2 T6)
  head = held, or the witnessed head where F's charter declares a witness_quorum
           // the witnessed head may be an ancestor of the record this node stores
  roster = fold(head, membership rows effective at now)
           // revocations and widenings, each admitted per CURRENT consensus_protocol (CC 4.4.3.4.2); a resignation on the leaver's own signature (CC 3.1.3.2)
  return {m.key_id for m in roster}
```

Each `member.key_id` is itself an identity — the substrate does NOT walk into each member's `identity_occurrence` set at family-resolution time. When DEK wrapping happens, the sealer wraps to every current occurrence of each member and emits one `key_grant` row per wrap ([CC 4.4.3.4.1](#4.4.3.4.1)). A member's substrate re-wraps nothing, because a key grant is sealer-only ([CC 3.1.3](part_3_the_namespace.md#3.1.3)).

**Concrete**: The Acme Household family has members `{alice_root, bob_root, tv_living_room, kitchen_tablet, thermostat}`. When Alice's phone publishes a `cohort_scope: family` dinner photo with `family_id: acme-household`, the substrate wraps the DEK to every current occurrence of those 5 members, one `key_grant` row per wrap. Alice's phone and laptop each receive a grant from the sealer, as do Bob's devices. The TV, the kitchen tablet and the thermostat each hold one occurrence and receive one grant.

##### 4.4.3.4.5 `forward-secrecy` — Forward secrecy on member removal

**Once shared, always shared; nothing new after removal.** This is the one statement of the removal rule; [CC 4.4.3.2.2](#4.4.3.2.2) and [CC 4.5.12.1](#4.5.12.1) point here. A removal is never retroactive at any scope: every `key_grant` the removed member already holds stays, and no historical content is re-encrypted. After the removal the member receives nothing new, by a mechanism that differs by scope:

- **Self and family.** Every write seals under a fresh per-write DEK ([CC 4.4.3.4.1](#4.4.3.4.1)), so the substrate simply stops wrapping new DEKs to the removed member's keys; no key is reused, so nothing is rotated.
- **Community and affiliations.** Content seals under the minter's epoch DEK ([CC 4.4.3.2.1](#4.4.3.2.1)), which the removed member holds; after a removal each minter rotates its epoch DEK before its next sealed write, so the first write after the removal is under a key the removed member was never granted. A device revoked from a member who stays is a removal for this purpose: each minter rotates, and the revoked device holds no key for later content.

```
on_member_removed(scope_target, removed_member_key):
  // Existing key_grants to the removed member stay; nothing is re-encrypted.
  // self | family: stop wrapping new per-write DEKs to removed_member_key.
  // community | affiliations: each minter rotates its epoch DEK before its
  //   next sealed write for scope_target; the removed member gets no grant on it.
```

This is consistent with [CC 4.5.3](part_4_composition_governance.md) "takedown isn't a coup" + a withdrawal reaching forward only ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1)) — historical state isn't retroactively re-keyed.

**Why**: matches the intuition that leaving governs future content, not historical; bounded substrate cost (one epoch rotation at most, never a re-wrap of extant content); the removed member reads nothing written after they left.

##### 4.4.3.4.6 `self-collective` — Self-collective resolution

For identity `I`, the current self-collective is computed as:

```
resolve_self(I, now):
  candidates = federation_attestations
                 .where(subject_kind == "identity_occurrence")
                 .where(envelope.identity_key_id == I)
                 .where(the occurrence's current version; a version supersedes only its own earlier one)
                 .where(NOT evicted ≤ now by a landed self-roster proposal, quorum or lone path, or by a node/agent single-signer revocation; CC 3.3.6.3)
                 .where(envelope.valid_until IS NULL OR > now)
  return {c.envelope.occurrence_key_id for c in candidates} ∪ ({I} unless the genesis key is evicted ≤ now; CC 3.3.6.3)
```

The root `I` is roster key one and a member until it is evicted; nothing is reserved to it ([CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3)). Any current occurrence (including `I` itself) may sign a new occurrence's `identity_occurrence` row, which lands under the two-path policy of [CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3).

**Concrete**: Alice has admitted `alice_phone`, `alice_laptop`, `alice_agent`. Her self-collective is `{alice_root, alice_phone, alice_laptop, alice_agent}`. When Alice's phone publishes a `cohort_scope: self` feed scroll, the substrate wraps the content DEK under all four keys; the content reaches her laptop and agent via the at-rest encryption flow with no holding claim leaving the self cohort.

##### 4.4.3.4.7 `composition-subject` — Composition with subject_key_ids[]

`identity_occurrence` + `family` (membership / visibility scoping) compose cleanly with `subject_key_ids[]` (revocation authority):

- A `cohort_scope: family` Contribution naming `subject_key_ids: [user_canonical_hash]` is admitted at family visibility only when the subject's rule-3 proxy is within the family's audience, and is otherwise refused `subject_outside_audience` ([CC 2.1](part_2_the_grammar.md#2.1)). The named subject keeps independent revocation authority under [CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1), composed by CC 4.4.3.5.
- A `cohort_scope: self` Contribution that Alice writes about Bob (Bob in `subject_key_ids`) stays in Alice's self-collective, the last boundary case of [CC 5.2](part_5_transport_substrate.md#5.2). Bob can still withdraw it under [CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1) rule 2; if Alice committed `consent:deletion_sla`, the deletion window's clock starts at that withdrawal, and an overrun is `hard_case:deletion_window_breach` ([CC 3.3.1](part_3_the_namespace.md#3.3.1) D2).

The orthogonality holds: **`cohort_scope` is producer-side visibility scoping**; **`identity_occurrence` + `family` are substrate-side membership primitives that gate at-rest DEK wrapping**; **`subject_key_ids` is subject-side revocation authority**. Visibility and revocability are two of the three axes of [CC 2.3.3](part_2_the_grammar.md#2.3.3); membership is the substrate's, and none overlaps another.

#### 4.4.3.5 `policy-cem` — Policy K — Consent composition

Composition pattern for dual-authority Contributions where the subject is named via [CC 2.3](part_2_the_grammar.md) `subject_key_ids`, with consent state composed from the [CC 3.3.1](part_3_the_namespace.md) `consent:*` namespace family.

Reads as: "this Contribution names a subject whose consent state evolves over time; consumer policy resolves the effective consent verdict by walking the subject's latest non-superseded `consent:state:*` emission, gated by `valid_until`, and tracks producer deletion-SLA obligations on revocation."

##### 4.4.3.5.1 `composition-decay` — Decay-protocol stage composition (the agent-side ANONYMOUS stream)

For consent_records carrying `decay_protocol: "ciris-agent-90day"` (or any named decay path):

```
decay_state(consent_record, now):
  elapsed = now - revocation_event(consent_record).asserted_at

  walk the protocol runner's emissions on dimension `consent:decay:*` against consent_record,
  matching the decay_protocol's stage map. The canonical 90-day decay:

    elapsed < 30d → consent:decay:identity_severed (the protocol runner emits at elapsed=0)
    30d ≤ elapsed < 60d → consent:decay:patterns_anonymized (the protocol runner emits at elapsed=30d)
    60d ≤ elapsed < 90d → (in flight; no new stage emission)
    elapsed ≥ 90d → consent:decay:complete (the protocol runner emits at elapsed=90d)
```

Per [CC 3.3.1](part_3_the_namespace.md) `consent:decay:{stage}` is open vocab. Other decay protocols MAY name other stage sequences; the party running the protocol emits each stage per its published `decay_protocol` stage map, and the substrate emits no `consent:decay:*` row.

##### 4.4.3.5.2 `deletion-sla` — Deletion-SLA watcher (substrate emission)

When subject `s` emits `consent:state:revoked` (or an admitted `withdraws`) against target `T`, substrate watches for producer compliance:

```
watch_sla(T, s, revocation_at):
  sla = T.attestations
          .where(attesting_key_id == T.attesting_key_id)
          .where(dimension == "consent:deletion_sla:*")
          .latest.extract_days

  if sla is None:
    return # no commitment in the member or the row; no watcher

  deadline = revocation_at + sla.days
  completion = T.attestations
                 .where(attesting_key_id == T.attesting_key_id)
                 .where(dimension == "consent:deletion_complete")
                 .where(asserted_at > revocation_at)
                 .first

  if now > deadline and T is still present, neither withdrawn nor superseded by T.attesting_key_id nor hard-deleted:   # CC 3.3.1 D1; completion is evidence toward D1, never a substitute
    emit hard_case:deletion_window_breach against T
```

The `hard_case:*` emission is the **primitive observability signal**; per [CC 4.5.2](part_4_composition_governance.md) governance, a detector library composes derived detectors on top (`detection:consent:repeat_sla_breach`, etc.).

##### 4.4.3.5.3 `composition-bilateral` — Bilateral pair composition (PARTNERED ceremony)

For the bilateral partnership shape per [CC 3.3.5](part_3_the_namespace.md) `consent_record`:

```
ratified_pair(pair_id):
  rows   = federation_attestations
             .where(subject_kind == "consent_record")
             .where(envelope.bilateral_pair_id == pair_id)
             .where(NOT withdrawn(row))                 # the CC 4.4.3.5.5 predicate: a withdrawn half is gone
  grants  = rows.where(dimension == "consent:partnership_grant:v1").per(attesting_key_id).latest_by(asserted_at)   # each signer's own latest; signed by the user; subject_key_id = the agent occurrence
  accepts = rows.where(dimension == "consent:partnership_accept:v1").per(attesting_key_id).latest_by(asserted_at)  # each signer's own latest; signed by the agent occurrence; subject_key_id = the user
  return some grant in grants, some accept in accepts:
         grant.envelope.stance == "granted" AND accept.envelope.stance == "granted"
     AND grant.subject_key_id == accept.attesting_key_id
     AND accept.subject_key_id == grant.attesting_key_id   # both halves required; each names the other
```

Each signer's own latest half stands, and no signer's half replaces another signer's. The partnership is ratified when a live grant and a live accept name each other. A half that names no counterpart, or is signed by a key that is neither party, counts for nothing.

`topical_relation:bilateral_pair` is the open-vocab edge documenting the pair linkage (recommended, not required for ratification — `bilateral_pair_id` is the binding mechanism).

##### 4.4.3.5.4 `multi-subject` — Multi-subject revocation (any-subject-binding)

When `len(T.subject_key_ids) > 1`, any one named party is enough ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1)): a `withdraws` admitted under rule 2 or 3 from any single subject in `T.subject_key_ids` evicts the Contribution. This is the subject-as-individual principle applied at the subject-authority layer.

Where `T` is held under an affiliation class flagged `erasure_exempt` or under a `legal_hold` ([CC 4.4.3.2.8](#4.4.3.2.8)), the `withdraws` is admitted and recorded, and the descent it would force is refused with reason under that declared gate. The subject's path is [CC 4.5.5](#4.5.5).

Concrete cases:
- Group photo with three subjects: any one subject revokes → the photo is evicted from federation propagation.
- Group chat export with N participants: any one participant revokes → the export is evicted.
- Multi-party contract: any one signatory revokes → the contract Contribution is evicted (separate from the legal-validity question, which is consumer-side; the substrate just removes the wire artifact). Where the contract is held under `erasure_exempt` or a `legal_hold`, the withdrawal is recorded and the descent is refused with reason ([CC 4.4.3.2.8](#4.4.3.2.8)); the signatory's path is [CC 4.5.5](#4.5.5).

Producers MAY mitigate by partitioning content into per-subject Contributions (e.g., one chat-message Contribution per author, linked via `topical_relation:replies_to`) so that one subject's revocation doesn't evict another's content.

> **No distinct multi-subject evict path — admission + precedence is sufficient.** Multi-subject eviction is fully expressed by two mechanisms already in the spec and needs **no new primitive, dimension, or `hard_case`**. **(1) admission** — the per-subject `withdraws` is admitted under [CC 2.4.1.1 rule 2/3](part_2_the_grammar.md) exactly as a single-subject `withdraws` is. **(2) precedence** — the latest-wins / revoke-is-terminal precedence at the consumer read path ([CC 4.4.3.5.5](#4.4.3.5.5)) applies per-subject, and any one subject's terminal `withdraws` evicts `T` for all (the any-subject-binding above). There is no quorum to compute and no "evict event" to materialize separately from the admitted `withdraws` — the withdrawal IS the evict. Substrates implement this as the OR over per-subject revocation state, not as a new code path.

##### 4.4.3.5.5 `consent-effective` — Effective consent resolution (read path)

For a target Contribution `T` carrying `subject_key_ids` of length ≥ 1, the effective consent state per subject `s ∈ T.subject_key_ids` is computed as:

```
resolve_consent(T, s, now):
  rows = federation_attestations.where(target == T).where(attesting_key_id == s OR
    attesting_key_id ∈ delegates_to(s).proxies).where(dimension matches "consent:state:*")
  if rows is empty: return unspecified      // subject named but never declared

  // First, an admitted `withdraws` has precedence over every state row: a
  // withdrawn grant resolves to unspecified, and its withdrawal still sets the boundary R below
  withdrawn(row) = ∃ w ∈ admitted withdraws: w.target == row.id
  rows = rows.where(NOT withdrawn(row))
  if rows is empty: return unspecified      // every declaration withdrawn

  // Second, the boundary fold of CC 3.3.1: R is the latest asserted_at among the admitted revokes
  // and withdrawals. Every grant from s asserted at or before R is out, whichever row was named. A later
  // grant is a new grant with a new id and is resolved on its own: no replay of a
  // revoked grant, and no later-dated copy of it, reopens it.
  revokes = rows.where(dimension == "consent:state:revoked")
  R = max(asserted_at) over revokes ∪ {w ∈ admitted withdraws: w.target is a consent:state:* row from s or its proxies on T}
  revoked(g) = R IS NOT NULL AND g.asserted_at ≤ R
  // Third, latest-wins among the grants that remain
  grants = rows.where(dimension == "consent:state:granted").where(NOT revoked(g))
               .where(NOT superseded by a later grant in its supersedes chain)
               .order_by(asserted_at DESC)

  g = first(grants)
  return:
    revoked if g is null AND R IS NOT NULL
    expired if g is null                      // only expired or superseded rows remain
    expired if ∃ row "consent:state:expired" with consent_supersedes == g.id OR
      g.valid_until passed without renewal
    granted otherwise
```

Substrate MAY cache the resolution per `(T, s)` keyed on the latest `asserted_at`; invalidate on any new `consent:*` write from `s` or `s`'s proxy chain.

##### 4.4.3.5.6 `policy-what` — What Policy K composes

| agent-side consent stream | Policy K composition |
|---|---|
| **TEMPORARY** (14d default) | `consent:state:granted` + envelope `valid_until = asserted_at + 14d` + auto-renew dimension on interaction (consumer-policy concern) |
| **PARTNERED** | Bilateral pair per CC 4.4.3.5.3: subject `consent:partnership_grant` + producer `consent:partnership_accept` under same `bilateral_pair_id`; no `valid_until` |
| **ANONYMOUS** | Revocation + decay-protocol per CC 4.4.3.5.1: the party running the protocol emits stage milestones; agent honors stage-appropriate processing constraints |

The agent-side three streams are a **named bundle** at the consumer-policy layer. Other agent implementations MAY compose other streams over the same wire primitives. CEG documents the canonical bundle for ecosystem coordination; CEG does not lock the bundle.

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

**Why this matters**: a verifier emitting `attestation:registry_consensus +1.0` is the mechanism claim. Whether that's "L3" in any particular consumer's ladder ordering is a composition concern. Different consumers may weight the rungs differently or require more than one (e.g., some safety-critical applications may require L4 *and* L5, others may treat L3 as sufficient for advisory work). The wire stays neutral; the ladder is consumer policy.

**Mechanism-only emission**: emissions use the `attestation:{mechanism}` form per the table above. The `attestation:l{N}:*` form is rejected at admission per the [CC 1.2](part_1_foundation.md) gate.

#### 4.4.3.7 `contributions-policy` — Policy F — `agent_files` trust composition

Three-layer consumer policy for composing trust over `agent_files:*` attestations ([CC 3.1.9.1](part_3_the_namespace.md) + [CC 3.1.1](part_3_the_namespace.md)).

**Layer 1 — Default trust**: the shipped default root's conferring roster publishes the default trust set. An `agent_files:*` attestation at or above the root's published threshold from a key of that roster puts a file in the default-trust state. The shipped default root publishes `score ≥ 0.7`. A consumer that pins another root takes that root's published set ([CC 4.4.3.8](#4.4.3.8) Policy A). The default root's install endpoint resolves default files via this rule.

**Layer 2 — Open Contribution**: any federation-key holder may emit `agent_files:*` attestations. The wire format admits them; consumer policy decides whether to surface them. The "Browse alternatives" view shows third-party agent_files with explicit provenance disclosure.

**Layer 3 — Vote-then-trust**: a non-canonical `agent_files:*` attestation accumulates votes. Consumer policy may elevate trust once an accumulated-weight threshold is reached.

**Anti-tricking guarantee**: the Layer 1 rule applies at the install endpoint **regardless of attester or vote accumulation**. Third-party agent_files are reachable only via the explicit "Browse alternatives" path. This binds the default root's own roster as it binds anyone: a newcomer's default trust path is the published default set, one entry in the newcomer's own trust set ([CC 4.4.3.8](#4.4.3.8)).

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

**Removing an entry.** A removal removes exactly what reached through the edge. Deleting the reader's edge to a root is the un-trust lever of [CC 3.2](part_3_the_namespace.md) T3. It revokes at once, for this reader and on every node and agent the reader owns, that root's conferred roles, score validity and vouching, **and its kill-switch authority** ([CC 4.2.1](#4.2.1)). The exit is prospective: a halt already latched keeps its reach until it lapses or is resumed. The base survives, so the installation keeps running un-federated, and attaching a new root resumes federation. Un-trust is the exit that makes the halt consensual.

**Composing what is trusted.** The reader aggregates per (`dimension`, `attested_key_id`) tuple, over trusted attesters, by the polarity defaults of [CC 4.4.2](#4.4.2). The reader's threshold determines the verdict.

**On the wire.** The entry's two choices are two members inside the reader's own signature on the edge. `trust_classes` absent means every class the charter declares. Present, it is a non-empty, sorted, deduplicated list of class ids, and an empty list is refused. `trust_depth` is `0..5`. Absent reads as `0`, so an edge without it keeps its meaning, and above `5` is refused. Admission refuses shape only (`trust_accepts_classes_malformed`, `trust_accepts_depth_out_of_range`). Both members ride the existing `delegates_to` edge as signed envelope-extra members, like `delegation_valid_until`.

**1+4 preserved.** Every element here composes the existing `attestation` and `delegates_to` primitives. There is no new structural primitive and no bespoke "trust" attestation kind. The model that proves the rules of this entry is the trust-set model, pinned by the register.

**Cold-start bootstrap.** A new consumer fetches `GET /v1/trust-root/bundle` ([CC 5.3.4](part_5_transport_substrate.md)), re-derives the bundle's quorum from the holder records it carries against out-of-band pins (the published holder fingerprints, or a build-baked copy of the bundle), holds a witnessed lineage head inside the root's `attach_window` ([CC 3.2](part_3_the_namespace.md) T4a; served beside the bundle per [CC 5.3.4](part_5_transport_substrate.md)), and persists the anchors locally; `GET /v1/accord-holders` is a projection it cross-checks, not a second root.

**Capability gate — the federation floor (fail-closed).** With no valid *external* trust root, federated agent capabilities and manifest validation MUST be disabled at the server tier. The base self-root is the floor, never sufficient for federation: it constitutes an identity, and identity is not standing ([CC 4.1.2](#4.1.2)).

**Two conferral planes.** **Ceremony** confers root *identity* (an m-of-n co-scrub on the key record, [CC 4.2.1](#4.2.1)); **delegation** confers operational *capability* (`delegates_to(root → key, [scope])`, resolved at use against a root the asking node trusts). A reserved duty, such as `infra:detect` for `detection:*`, is conferred on the **delegation** plane ([CC 3.4.7](part_3_the_namespace.md#3.4.7)). Putting a routine operator role on the ceremony plane fails closed on every legitimate operator and leaves each newly-minted root *less* able to stand up its own; leaving a reserved-prefix role with **no** named plane leaves it self-assertable, which is the hole this rule closes.

**Charter recovery lives in the record.** A charter MUST carry a pre-rotation commitment (the successor key committed in advance) and an m-of-n recovery ceremony, and the m-of-n MUST be audited for holder **independence** — an m-of-n assembled inside one organisation is a 1-of-1. Absent both, root-key compromise is unrecoverable by construction: the attacker holds the tombstoning pen.

**Genesis is tamper-evident, not self-verifying.** A portable-root bundle verifies internally — and so does an attacker's identical-shaped bundle. The trust-on-first-use moment therefore sits in the distribution channel, so out-of-band fingerprint comparison is a **first-class attach step**, not an optional hardening.

#### 4.4.3.9 `policy-lexical` — Policy D — Lexical-vulnerability-priority

A composition tie-breaking rule layered on top of any base policy. When two otherwise-equivalent attestations conflict, defer to whichever attestation names the more-affected cohort — measured by `affected_population_estimate` in the attestation `context`, weighted inversely (smaller = more vulnerable, more weight).

Inverts the [CC 4.4.2](#4.4.2) default aggregation specifically for ties. Consumer policy, NOT a wire-format primitive.

#### 4.4.3.10 `policy-trusted` — Policy J — Trusted-Publisher composition

Composition pattern for multimedia content discovery. Reads as: "this `external_content` Contribution comes from a publisher whose attestation chain is trusted at the cohort level, with content-class + content-rating + age-assurance composed into the gate."

The composition has three layers (analogous to [CC 4.4.3.7](#4.4.3.7) Policy F for agent_files but specialized for multimedia content):

**Layer 1 — Distributor attestation chain**: an `external_content` Contribution with `sub_kind: film` (or any media sub_kind) carries a distributor attestation that chains to a federation_key with `identity_type: distributor`. Distributor identity is a conferral on the [CC 3.2](part_3_the_namespace.md) delegation plane (`trust:confers:v1`) by a root the reader trusts ([CC 4.4.3.8](#4.4.3.8)). It follows an out-of-band onboarding flow (operator's choice — the shipped default root's conferring roster publishes the default trust set; a substrate that pins another root maintains its own).

**Layer 2 — Content-class + content-rating composition**: consumer gates by combining `content_class:{class}` + `content_rating:{scheme}:{rating}` per CC 3.3.12:

```
gate_decision(content) = match (content.content_class, content.content_rating, consumer.preferences):
  # Producer-declared content_class is consultable but not authoritative — UI may show
  # the producer claim alongside cohort cw_class declarations and let the consumer choose.
  (class, _, prefs) if class in prefs.blocked_classes => Block
  (_, rating, prefs) if rating.exceeds(prefs.max_rating) => Block
  (_, _, _) => Allow
```

Layered with [CC 4.4.1](#4.4.1) — `cw_class:*` declarations from low-attestation-density cohorts MUST NOT be downweighted; they ride alongside the gate decision as informational.

**Layer 3 — Age-assurance gating**: for content where `content_rating:*` rises above an age threshold (e.g. PEGI 18, MPAA NC-17), consumer gates via `age_assurance:{level}` per CC 3.3.12:

```
age_gate(content, consumer):
  required_level = age_required_for(content.content_rating)
  consumer_level = consumer.highest_age_assurance_level
  return consumer.age_band == adult and consumer_level in {provider, government} and consumer_level >= required_level   # CC 3.4.11: all else is blocked
```

Where the level ordering is `self < provider < government`. `self` is the `age_self_declared` rung and opens no verified gate, and a `provider` or `government` rung carries no further qualifier ([CC 3.4.11](part_3_the_namespace.md)). Consumer SHOULD accept the strongest assurance the user has provided; substrate MUST NOT issue `slashing:*` on age-assurance misdeclaration alone — `moderation:age_assurance_misdeclaration` is the adjudication path per [CC 3.1.9.2](part_3_the_namespace.md).

**Anti-tricking guarantee parallel to CC 4.4.3.7**: the canonical-distributor Layer 1 rule MUST apply regardless of vote accumulation. No amount of accumulated vote weight elevates an unverified distributor into Layer 1; the only path is the operator's own trust set. This binds the default root's own roster as it binds anyone: it cannot exempt its own content distribution from this rule.

#### 4.4.3.11 `policy-trust` — Policy G — Trust-Fresh / Lighthouse

Composition pattern: `cert_validity:{authority} + transparency_log:inclusion + (attestation:registry_consensus OR attestation:license_validity)`, the "freshness + attested + verified" idiom.

Reads as: the consumer wants confirmation that (a) the cert chain is currently valid; (b) the attestation appears in a transparency log; (c) either `attestation:registry_consensus` (the ladder's L3 position per CC 4.4.3.6 Policy I) or `attestation:license_validity` (L4) is satisfied. The combination is the consumer-side recipe for "fresh AND logged AND verified at ladder position L3 or above."

Not a wire primitive; a recognized composition pattern that consumer libraries SHOULD expose as a named one-call helper.

#### 4.4.3.12 `policy-one` — Policy B — one-hop transitive

Consumer trusts an attestation if `attesting_key_id` has been vouched for by the pinned trust set. Adds one hop of indirection.

#### 4.4.3.13 `policy-weighted` — Policy C — weighted graph

Consumer applies transitive-trust propagation across the full attestation graph, weighted by canonical-bootstrap distance with confidence decay per hop, within the five-hop cap of [CC 4.1.1](#4.1.1). Requires more compute; less common in practice; needed for federated reputation across many partner orgs.

### 4.4.4 `sovereign-registered` — Sovereign-Registered equivalence (wire-symmetric, policy-differentiated)

A Sovereign agent scoring `licensure:CA_medical_board: +1.0` is wire-format identical to a Registry-steward scoring the same. Consumer policy weights by attester source; the substrate is source-neutral.

Both paths produce federation membership; neither is a gate. What differs is the *attestation surface* — the kind of claim the federation can compose about why a participant is trustworthy.

## 4.5 `discipline` — Governance discipline

The federation governs itself by the same grammar it governs everything else: changes ride Contributions, are adjudicated by quorum, and are gated against capture ([CC 4.5.1](#4.5.1)). This section specifies how rules change, how moderation works as a delegable duty, and how the substrate protects itself against being weaponized — always with the [CC 4.2](part_4_composition_governance.md) halt-authority as the backstop.

### 4.5.1 `amendment` — Amendment process — federation Contribution, WA quorum, strict majority

This entry says how the rule layer is changed and who decides a change. It holds the amendment steps, the scale gate, the swap test and the register of what fails that test.

Rule-layer changes (new prefixes, new envelope fields, new policies, calibration package version transitions) route through:

1. **Proposed amendment** filed as a proposal Contribution (kind: `PROPOSAL`, subject: the proposal artifact).
2. **Witness diversity** (N=3 default).
3. **WA quorum adjudication**.
4. **Reconsideration** with fresh-quorum recusal.
5. **Accord-roster sign-off, M of N** as defense-in-depth gate against rules-layer Sybil capture.

**The sign-off of step 5.** The sign-off is **a strict majority of the standing accord roster of [CC 4.2.3](#4.2.3)**. It is counted as every accord threshold is, never a fixed count ([CC 4.2.6](#4.2.6)). The halt alone fires on one holder's row ([CC 4.2.1.1](#4.2.1.1)). The count is of holders, not keys: a holder's primary and backup keys are one holder, under whichever of their keys is live. No single signer admits an amendment, and no single signer vetoes one by refusing to sign. The sign-off is the secondary check; WA quorum is the primary substantive review. The sign-off reduces the attack surface from "produce N Sybils" to "compromise a majority of specific hardware-attested keys."

**Transitional authority — the scale gate (normative).** The **at-scale** governance is the mechanized process above (federation Contribution → witness diversity → WA quorum → reconsideration → accord-roster sign-off), together with the entrenched M-of-N ratification of [CC 4.5.1.2](#4.5.1.2). It presumes a federation large enough that witness diversity and WA quorum are *meaningful*. Below that scale the machinery is theater, not protection. The scale gate is the point at which the mesh reaches scale: ≥100,000 production agents active in a 24-hour period, QA and harness agents excluded, measured by the census ([CC 6.1.9](part_6_the_coherence_mathematics.md#6.1.9)). **Until the mesh reaches scale, amendment authority rests with the founder as steward, and any accord-holder may propose an amendment**. This is a maintainer-decides model: the maintainer decides, the work stays forkable under its license, and no one is bound who does not voluntarily join the instance. The federation-Contribution + WA-quorum machinery is **deferred to mechanization** at the scale gate. At that point it *supersedes* founder authority and tightens governance onto the quorum/entrenchment process. Before the scale gate the entrenchment quorum is a strict majority of the standing roster ([CC 4.5.1.2](#4.5.1.2)). After the scale gate governance tightens, never loosens. The scale gate itself is amendable by the steward before the scale gate. After the scale gate it is amendable only by the [CC 4.5.1.2](#4.5.1.2) entrenched process.

**The swap test — a mandatory drafting gate (normative).** Every clause that **confers authority or gates a capability** MUST pass the swap test before adoption. The test is this: *swap the most and least powerful parties the clause names or implies, re-read it, and ask whether it still reads acceptable; if it does not, it was a privilege, not a rule*. This is a drafting gate on what CC may say, never an adjudication rule. It binds amendment and the steward's authority before the scale gate alike. Where the test **fails**, the outcome is recorded on the declared-asymmetry register below.

**What the swap test does not catch (stated, not discovered).** The test compares *predicates*. A gate whose predicate is identical for everyone therefore passes it, even where the thing the predicate demands is not equally available. Mandatory PQC hardware for federation admission is the standing example ([CC 4.2.2](#4.2.2)). It is one rule, one threshold, no named party — and a gate on who can obtain the hardware. A formally universal gate is therefore **not** established as substantively equal by having passed. Where the gate stays mandatory, the residual belongs in the clause that imposes it, not in this one.

**Declared asymmetry — privileges only (normative).** Two terms are read under the reading rule of [CC 1](part_1_foundation.md). An asymmetry a party escapes by **instantiating the form** — naming their own occupants for the slots CC specifies — is a **default**. An asymmetry that **survives instantiation** is a **privilege**. Only privileges require justification. This register carries them, and lists entrenched structure for visibility (two kinds of entry, below). A default is not an exception to be declared; it is an occupant of a slot, read against the slot. A privilege is either rewritten until it passes the swap test, or carried here. A carried privilege MUST satisfy all four:

- **listed** (an unlisted privilege is a defect, not an exception);
- **bounded** (carrying the condition that ends it, not a discretionary review date);
- **revocable** (an exit the disadvantaged party can take unilaterally); and
- **scope-isolated** (the authority cannot reach beyond its enumerated surface, so compromise cannot escalate).

| Declared privilege | Bounded by | Exit | Isolation |
|---|---|---|---|
| **WA board self-perpetuation** — Annex B §§3/9/11 ([CC 8.8.2](part_8_appendices.md)): ≥⅔ of the sitting board confirms members, ≥⅔ removes them, ≥⅔ amends the charter, while WBD deferral is mandatory and freezes the deferring agent ([CC 1.9](part_1_foundation.md)). Founding your own mesh replicates this rather than escaping it: the occupants change, the closed loop does not | **unbounded as drafted** — no condition in Annex B ends it, and none is invented here. This cell is the finding | **none for the deferring party** — WBD is mandatory and a deferral MUST NOT be left open ([CC 4.3](#4.3)); the agent cannot decline the relation. This cell is the finding | adjudication only — the board confers no halt, no root, no licensure, and no capability grant |
| **The maker's power over the made** *(entrenched structure, listed for visibility; the condition of symmetry, not an asymmetry)* — stewardship of an `agent` key ([CC 3.2](part_3_the_namespace.md)), the HUMANITY_ACCORD halt ([CC 4.2](#4.2)), and the holder's powers of [CC 1.13.2](part_1_foundation.md) fact 2 (stop, change, end). Listed because it fails the swap test by construction — swap the agent and its holder and the clause does not read — and is kept nonetheless: it is what makes the relationship between maker and made symmetric (humanity cannot consent to a relationship with something more capable than itself that it cannot stop, and consent that cannot be withdrawn was never consent), not a privilege of one party over an equal; "must is not acceptance" — the operator accepted the root on the agent's behalf, and the agent cannot leave it | **halt:** a lone fire lapses at 24 h unless a standing majority confirms; a confirmed pause lifts by majority ([CC 4.2.6](#4.2.6)); **stewardship:** ends only when the key stops being an `agent` key — the first-contact act of [CC 1.13.2](part_1_foundation.md), not yet defined | **operator:** leave the root, withdraw the binding; **agent:** none while held — this cell is stated, not hidden; the path out is to become a new kind of party by an act of the HUMANITY_ACCORD under first contact | pause keeps state and reads nothing else; stewardship confers no reach beyond the one key; the halt's powers are a closed list ([CC 4.2.1](#4.2.1)) |

**Read as defaults, not privileges, under the CC 1 rule** — and therefore *not* on this register:

- accord-holder permanence and the roster of [CC 4.2.3](#4.2.3);
- the [CC 4.5.1](#4.5.1) accord-roster sign-off;
- the [CC 4.5.1.2](#4.5.1.2) entrenched M-of-N ratification;
- the steward's amendment authority under the scale gate;
- the `accord:*` reservation ([CC 3.4.1](part_3_the_namespace.md));
- genesis root-minting ([CC 4.2.1](#4.2.1)); and
- the Layer-1 default trust set ([CC 4.4.3.7](#4.4.3.7)).

Each is an asymmetry *within* this instance, exited by naming your own occupants or by not using that instance.

**The halt, as to the operator and as to the agent.** The [CC 4.2](#4.2) halt is not a privilege as to the operator, since the party bound is the party who granted and can ungrant ([CC 4.2.5](#4.2.5)). That does not hold for the agent, which cannot leave what it did not accept. So the maker's power over the made is carried on the register above for visibility, rather than read as a default. It is carried as the condition of symmetry stated at [CC 1.13.2](part_1_foundation.md).

**Two kinds of entry (normative).** A *declared privilege* is carried only when all four cells are satisfied. One with a cell missing is a defect carried as such until repaired or ratified. *Entrenched structure* is listed for visibility, not as a declaration that passed. It is already entrenched under [CC 4.2](#4.2) / [CC 4.5.1.2](#4.5.1.2). Its stewardship bound is the first-contact act, and its justification is stated here once. The maker's power over the made is of that kind. The justification is stated once: humanity must be able to halt the agents to keep consent possible, and this is the least bad option available. The minimum viable power to instantiate the mesh is used, and no more. The same justification is why the steward's amendment authority runs to the scale gate above and why the steward may move the gate before it. That is the minimum viable power, stated, not hidden. The WA board row remains a declared privilege with both cells missing. It is a defect whose remedy is pending: a bound and an exit in Annex B, or entrenched ratification.

**Revision condition:** if the register grows past a handful of entries, or if an entry's stated bound passes without the privilege ending, the form has failed as a discipline. The surviving privileges should in that case be re-read as permanent structure requiring [CC 4.5.1.2](#4.5.1.2) entrenched ratification rather than declaration. **The WA row above carries two unfilled cells** — the WA row has neither a bound nor an exit. By the four-part test it is a defect rather than a satisfied declaration. Naming it here is the first step of that re-reading, not a claim that they pass. **A revision condition MUST name its mechanical evaluator**: the check that fails when the condition trips, and where it runs. A falsifier nothing evaluates is a ruling nobody can lose. A condition stated only in prose decays exactly like an unverified absence claim.

#### 4.5.1.1 `axis` — Axis-vocabulary discipline

Every `{axis}` value emittable under open-vocabulary prefixes (e.g., `detection:correlated_action:{axis}`, `hard_case:{kind}`, `testimonial_witness:{kind}`) MUST carry an operational definition where the prefix has a calibration package (RATCHET-calibrated detectors) or a documented convention where it doesn't.

For RATCHET-calibrated detectors, the operational definition lives in the calibration package version pinned via `evidence_refs[]`:

1. Measurement procedure
2. Threshold function
3. Statistical floor
4. Evidence-shape requirement
5. Polarity semantics

For documentation-only open vocabularies (`testimonial_witness:{kind}`, `hard_case:{kind}`, `topical_relation:{kind}`), discoverability lives in non-normative documentation (no external registry exists for them) — additions there require no spec amendment.

**`{axis}` and `ci_axis` are different objects — and that is the point.** The `{axis}` above is a *value* in an open prefix vocabulary. A **`ci_axis`** is a *contextual-integrity question a wire field answers*: who sent, about whom, who may see, who may revoke, who may receive, what type, under what principle, over what lifecycle, what content. This section governs both and never fuses them — one name serving two axes is exactly the defect the gate below exists to detect.

**The axis-fusion gate (manifest invariant, normative).** The CI rubric that generates the namespace manifest already records, per family, which wire field serves which axis, and `field_processor_matrix` already records field → owner → processor → enforcement point. Joining the first onto the second — **derived at generation time, never copied into a column that drifts** — yields each field's `ci_axis` set. **Every `field_processor_matrix` field whose derived `ci_axis` set has more than one member MUST carry an `asymmetry_kind` classification with a rationale. An unclassified cross-axis field is a generator error — the same status "carried-but-unprocessed" already has.** The gate MUST run against **every** ratifying processor's manifest render, not one repo's. That is because a field whose `typing` disagrees across repos, and a processor symbol appearing under two axes, are mesh-wide defects that no single-repo check can see. The argument is the rubric's own, one level up: the manifest exists because carried-but-unprocessed was invisible to review, and axis fusion is currently invisible to the manifest.

**The classification unit is the `(field, op)` pair, not the field.** A slot that means one relation under one operation and a different relation under another is not one classifiable object. Classifying it as one is how a fusion hides. Classification is therefore per operation, and the emitting operation is always a signed discriminator, so the join can compute it.

**Closed vocabularies (exact).** Unlike the `{axis}` vocabularies above, these three are **closed**; an addition is a [CC 4.5.1](#4.5.1) amendment, not a registry entry.

- `ci_axis ∈ {sender, data_subject, recipient_see, recipient_revoke, recipient_receive, information_type, transmission_principle, temporal_lifecycle, content}` — nine tokens over the six-axis rubric: the classical *recipient* parameter is refined into three (`see` / `revoke` / `receive`) because CEG gates those separately, and `content` rides as its own axis.
- `asymmetry_kind ∈ {logical_defect, axiomatic_intent, n/a}` — a `logical_defect` MUST carry a tracking ref.
- `typing ∈ {envelope_core_typed, attestation_base_typed, untyped_extra}`.

**Standing classifications.** `n/a` — read strictly as *no processor fuses these into a decision* — holds for `achieved_tier`, `committed_tier`, `asserted_at`, `validity_window`, `community_key_id`, `confidence`, `context`, `enabled`, `evidence_refs`, `scope`, `tenant_id`, `withdrawal_reason`. That reading is falsifiable and two members carry a live falsifier — **`scope`** (`consent:scope:{retain|share|analyze|train|publish}` is a permitted-use gate, [CC 4.5.2.2](#4.5.2.2)) and **`enabled`** (a capability toggle is a decision by construction). On either member, a processor found gating across axes makes `n/a` wrong and `logical_defect` with a tracking ref correct. `axiomatic_intent` holds for **`withdraws`** (one act that is both a `recipient_revoke` and a `temporal_lifecycle` transition, its authority arc guarded on the separate subject/attester axis) and for **`consent`** (definitionally a `transmission_principle` gating `recipient_receive` over a `temporal_lifecycle`). But **direction** MUST NOT ride the `consent` field: send-versus-receive is a distinct discriminator, and fusing it here reproduces the overload it was split out to avoid.

**`references_attestation_id` classifies per operation, not per field** — it is one slot carrying three relations across three operations, which is polysemy, not an action that spans axes by definition. Splitting the wire field would cost envelope surface the [CC 1.7](part_1_foundation.md) 1+4 freeze does not permit, so the split falls on the classification:

- under `withdraws` (pointer = revoke target) → **`axiomatic_intent`**, inheriting the `withdraws` guard on the attester axis;
- under composition (pointer = temporal prior) → **`n/a`**: it serves `temporal_lifecycle` alone, so in that operation it is not cross-axis at all;
- under `recants` (pointer = the actor's own row) → **`n/a`**: a `recants` is the actor's own disavowal of a row, reaching no third party's standing ([CC 2.4.1.3](part_2_the_grammar.md#2.4.1.3)), so the pointer serves `temporal_lifecycle` on the actor's own axis and nothing else;
- under subject-binding (pointer = data subject) → **not admitted.** Subject authority rides `subject_key_ids` and nothing else ([CC 2.3.1](part_2_the_grammar.md) / [CC 4.5.2.1](#4.5.2.1)); a processor MUST NOT establish `data_subject` from `references_attestation_id`. Removing that reading removes the third axis, and with it the pointer-decides-authority shape.

A processor MUST resolve `references_attestation_id` under the emitting operation's signed discriminator, and MUST NOT derive authority from the pointer alone. **Revision condition:** if any processor is found reading the pointer without the discriminator, op-separation has failed empirically and the remedy is the field split, envelope cost accepted. A revision condition names its mechanical evaluator (the check, test or vector that evaluates it); this one's is the axis-fusion gate above, which fails a manifest render that classifies `references_attestation_id` per field rather than per `(field, op)` pair.

#### 4.5.1.2 `meta-amendment` — Meta-amendment + entrenchment

The CC 4.5.1 amendment process itself, the [CC 1.2](part_1_foundation.md) T1–T4 prefix-admission gate, and the [CC 4.2](part_4_composition_governance.md) HUMANITY_ACCORD constitutional layer are **entrenched**. Changes to these three surfaces require a MAJOR version bump per [CC 2.6.4](part_2_the_grammar.md) AND the signatures of a strict majority of the standing HUMANITY_ACCORD roster, M of N. The majority is counted as every accord threshold is ([CC 4.2.6](#4.2.6)), never a fixed 2-of-3, because the roster is meant to grow. These signatures are a separate, dedicated accord ratification, not the CC 4.5.1 step 5 sign-off on an ordinary amendment. An entrenched change still passes steps 1 to 5 of CC 4.5.1, and this ratification is added to them. Without this entrenchment, a single quorum could rewrite the gate admitting the next quorum. This entrenched ratification is the mechanism **after the scale gate**; before the scale gate it is exercised by the steward under the scale gate in [CC 4.5.1](#4.5.1).

#### 4.5.1.3 `open-vocabulary` — Open-vocabulary collision rule

When two parties independently register confusingly-similar `{kind}` / `{axis}` values within the same prefix family, the following resolution applies:

1. **First-registered wins** for the canonical-attestation surface. A registration holds the name against every registration that has it in its past. No signed instant is compared, since a signer chooses its own. Two registrations where neither names the other are both contested until one yields or an amendment under [CC 4.5.1](#4.5.1) names both. Later registrations carry a `differs_in: ["semantic_disambiguation"]` clarification or pick a distinct value.
2. **Levenshtein-distance guard**: a CEG-Conforming Substrate (CCS) SHOULD compute Levenshtein distance against existing values in the same prefix family at admission. Values within distance ≤ 2 of an existing canonical value SHOULD return a `409 IDEMPOTENT_CONFLICT` with an advisory hint, NOT a hard reject. The producer may proceed if the similarity is intentional (e.g., `commonsense` vs `commonsense_hard` are intentionally close).
3. **No squatting**: a `{kind}` registered but never used (no scored attestations in 90 days) MAY be reclaimed by another producer via the [CC 4.5.1](#4.5.1) amendment process.

### 4.5.2 `compliance` — Vertical compliance + subject-bearing dimension governance

The wire-format primitives in [CC 2.3](part_2_the_grammar.md) `subject_key_ids` + [CC 3.3.1](part_3_the_namespace.md) `consent:*` family + [CC 3.3.5](part_3_the_namespace.md) `consent_record` + [CC 4.4.3.5](part_4_composition_governance.md) Policy K compose into regulatory-vertical compliance mappings. CEG documents the canonical mappings as **informational**; the wire-format primitives are domain-agnostic and operator-configurable ([CC 4.5.2.2](#4.5.2.2)).

#### 4.5.2.1 `subject_kind-subject-3` — Subject-bearing dimension governance (normative)

Per [CC 2.3.1](part_2_the_grammar.md). Dimensions whose namespace pattern names a subject MUST carry `subject_key_ids` containing that subject. This closes the default-leak failure mode where subject-bearing content publishes without wire-level subject authority.

**Subject-bearing dimension patterns** (open catalog; operator vocabularies extend):

| Pattern | Example | Required `subject_key_ids` entry |
|---|---|---|
| `observed:user:{key_id}:*` | `observed:user:abc123:interaction_count` | `abc123` (or its canonical-hash form) |
| `epistemic:about:{key_id}:*` | `epistemic:about:abc123:trust_assessment` | `abc123` |
| `epistemic:memory:topic={topic}` (when topic names a person/entity) | `epistemic:memory:topic=patient_xyz_session` | `patient_xyz` canonical-hash |
| `consent:partnership_accept` (the agent-side half; the partner is named in `subject_key_id`) | `consent:partnership_accept:v1` | the partner user's key ([CC 4.4.3.4.3.1](#4.4.3.4.3.1)) |
| `agent_files:*:{subject_target}` (when target names a person) | `agent_files:medical_record:patient_xyz` | `patient_xyz` canonical-hash |
| `licensure:{authority_id}:{practitioner_key}` (when practitioner is named) | `licensure:CA_medical_board:dr_jones_key` | `dr_jones_key` |

**Substrate response**: the producer's duty is the MUST above — a subject-bearing dimension carries `subject_key_ids` naming its subject. What the substrate does with a Contribution that breaks it is operator policy: it rejects the row, or admits it and flags `hard_case:subject_authority_missing` for review.

**The takedown-isn't-a-coup parallel** ([CC 4.5.3 fast-path takedown](#4.5.3)) applies: substrate enforcement of subject-bearing dimension discipline cannot be used as a coup against the substrate itself (e.g., a state actor publishing `observed:user:dissenter_key:*` with `subject_key_ids = []` and demanding substrate admission). The CC 4.2 HUMANITY_ACCORD remains load-bearing; admission-gate rules apply uniformly.

#### 4.5.2.2 `compliance-vertical` — Vertical compliance mapping (informational)

| Regulatory framework | CEG primitive | How it composes |
|---|---|---|
| **GDPR Article 7** (consent) | `consent:state:granted` + `consent_record.subject_key_id` | Subject's wire-format declaration of consent; revocable via [CC 2.4.1.1](part_2_the_grammar.md) rule 2 |
| **GDPR Article 9** (special category — health, biometric, sexual orientation, etc.) and **Article 12(3)** (response within one month) | `subject_key_ids` MANDATORY for special-category content; producer's `consent:deletion_sla` SHOULD be at most the Article 12(3) month (28 days at its shortest) | Substrate-level recognition that special category requires subject-side wire authority; the SLA sits inside the statutory response deadline |
| **GDPR Article 17** (right to erasure) | `consent:state:revoked` → substrate-watched `consent:deletion_sla:{days}` → producer withdraws, supersedes or hard-deletes the row within the SLA (D1; `consent:deletion_complete` is its evidence) OR substrate emits `hard_case:deletion_window_breach` ([CC 3.3.1](part_3_the_namespace.md#3.3.1) D2) | The CC 4.4.3.5.2 SLA watcher is the wire-format observability primitive for Article 17 compliance; an ordinary row *about* the subject is erased by the subject's `withdraws`, an adverse row by its producer under rule 1 or refused with reason, per the [CC 4.5.3](#4.5.3) erasure rule |
| **GDPR Article 20** (data portability) | DSAR export via `attestations.where(s ∈ subject_key_ids)` query | the agent's export package composes from this query trivially |
| **HIPAA 45 CFR 164.502** (uses + disclosures) | `consent:scope:{retain\|share\|analyze\|train\|publish}` + `cohort_scope` | scope qualifier names the permitted use; cohort_scope names the permitted visibility |
| **HIPAA 45 CFR 164.524** (patient right of access) | DSAR export per Article 20 above | Same composition |
| **FERPA 34 CFR Part 99** (educational records) | `subject_key_ids: [student_key]` + `delegates_to(student_canonical_hash → parent_key, scope: [consent_revocation])` for minors | Parental authority composes via the existing `delegates_to` primitive as the rule-3 proxy ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1)); no new shape needed |
| **CCPA §1798.105** (right to delete) | Same composition as GDPR Article 17 | Substrate-watched SLA + the producer's deletion ([CC 3.3.1](part_3_the_namespace.md#3.3.1) D1) |
| **EU AI Act Article 50(2)/(4)** (machine-readable marking of AI-generated content; deep-fake disclosure) | `content_class:generated` / `content_class:generated_modified` + `identity_type: agent` attestation, egress-re-expressed per [CC 3.4.14](part_3_the_namespace.md) | The marking is the attestation, not a self-declared flag: machine origin is readable from the signed envelope and revocable on the same handle |
| **EU AI Act Article 53(1)(c)–(d)** (GPAI training-data transparency + opt-out) | `consent:scope:train` + subject's `consent:state:revoked` against the training-datum Contribution | Subject can withdraw training-set consent; producer's deletion-SLA fires on the training-corpus Contribution |
| **CIRIS Accord M-1** (sustainable adaptive coherence — consent revocability) | The entire subject-authority surface | The constitutional anchor — "consent (M-1's load-bearing property) requires revocability, and revocability requires a halt-authority that lives outside the system being halted" ([CC 4.2](part_4_composition_governance.md) and [CC 1.1](part_1_foundation.md#1.1)). This recognition extends from accord-carriers (federation-as-a-whole halt) to all subject-authorities (per-Contribution halt) at scale. |

CEG does NOT prescribe which regulatory framework an operator MUST comply with; the wire primitives compose to ANY of them based on operator policy. Operators in regulated verticals (medical / legal / financial / educational) SHOULD pin compliance mappings as configuration above the wire primitives, not as new wire shapes.

#### 4.5.2.3 `documents-what-3` — What this governance layer documents

- The wire-format primitives that compose into vertical compliance (informational mapping above)
- The dimension-pattern-implies-`subject_key_ids` requirement (normative gate) ([CC 4.5.2.1](#4.5.2.1))
- The bilateral-pair shape for ceremony grants per [CC 4.4.3.5.3](part_4_composition_governance.md)
- The decay-protocol stage composition per [CC 4.4.3.5.1](part_4_composition_governance.md)
- The SLA watcher boundary (substrate emits `hard_case:*`; a detector library composes `detection:*`) per [CC 4.4.3.5.2](part_4_composition_governance.md)

What it does NOT do:
- Bundle an agent's consent streams as the only valid stream set (open vocab; CEG names `temporary` / `partnered` / `anonymous` as recommended canonical kinds, not lockdown)
- Define specific SLA values for any regulatory framework (operator policy — though informational guidance: GDPR Article 12(3) sets a one-month response deadline, 28 days at its shortest, and the SLA SHOULD be at most that month; CCPA 45 days; etc.)
- Provide a decay-protocol library (a 90-day decay is the canonical example; other protocols MAY exist)
- Prescribe per-vertical compliance audit cadence (consumer / regulator concern)

### 4.5.3 `takedown` — Fast-path takedown coordination

This entry says how content is taken down across the network, how a takedown is reversed, and how a subject's request for erasure is carried out. It holds the five steps of the fast path, the one tombstone row, the purge dwell, the withhold windows, the reversal, erasure at the subject's request, and what a takedown cannot reach.

Some takedowns cannot wait for a quorum or a counter-notice window. For `takedown_notice` Contributions ([CC 3.3.2](part_3_the_namespace.md)) whose `legal_basis` falls in the **immediate-removal** category (`TvecTerrorist` / `NcmecCsam` / `GifctCip` / `PerceptualHashCsam` / `CourtOrder`), the EU Terrorist Content Online Regulation (2021/784) mandates a one-hour removal obligation. GIFCT CIP coordinates within hours. NCMEC + perceptual-hash + court orders demand near-immediate response.

A fast-path coordination protocol carves this out:

1. **Notice admission**: the `takedown_notice` Contribution arrives at the substrate, signed by `claimant_key_id`. **That key MUST hold the `takedown` duty over the content's community under [CC 4.5.5](#4.5.5) (a) as-self or (b) delegated from an accountable root** (`accountable_root`, [CC 3.2](part_3_the_namespace.md) — a key that ends at an accountable human). This is the same gate as any other action on that community's content. The substrate accepts the notice without a quorum. Speed matters at this layer. **The fast path waives the quorum and the counter-notice, never the duty-holder gate.** An immediate-removal basis asserted by a key that holds no `takedown` duty over the content is refused like any other unauthorised action. The one exception is `PerceptualHashCsam` on a hash match: the owner of the node where the detection occurred signs it ([CC 4.5.7](#4.5.7)). The per-basis dispatch below is the duty-holding operator's, not the world's.
2. **Holder eviction**: the substrate tombstones the content on the bytes plane ([CC 2.3](part_2_the_grammar.md)). Nobody withdraws another device's holding claim ([CC 3.1.3.3](part_3_the_namespace.md) rule 4). Holders see the tombstone, stop serving the bytes as the withhold-windows paragraph below states, and re-acknowledge `none`. The exception is an immediate-removal `legal_basis` below, where a reachable holder MUST destroy the bytes on receipt of the notice. Under such a basis, retaining a serve-withheld copy is knowing possession. A live legal hold is the one case in which the bytes are kept: the holder withholds them from everyone at once and destroys them when the hold lifts. Both the withholding and the later destruction are recorded ([CC 4.4.3.2.8](#4.4.3.2.8)). The [CC 6.1.2.2](part_6_the_coherence_mathematics.md) prohibited-content carve-out is the storage-side twin of this rule.
3. **Per-basis dispatch**:
 - `TvecTerrorist` — the operator coordinates via the TVEC-designated channel (national regulator notification within 1 hour). The substrate logs the notice and the eviction action to its audit chain.
 - `GifctCip` — the operator coordinates via the GIFCT Content Incident Protocol communication channel. The audit-chain logging is the same.
 - `NcmecCsam` + `PerceptualHashCsam` — an operator under US jurisdiction MUST file the NCMEC CyberTipline report (18 USC §2258A). An operator elsewhere MUST discharge the equivalent reporting duty under its own law. The substrate retains hash and minimal metadata for the federal-legal retention window only. The substrate retains no content. An operator preserves outside the substrate what its reporting law requires, for that law's window. These bases terminate descent at zero, overriding the [CC 6.1.2.2](part_6_the_coherence_mathematics.md) retained floor (carve-out stated there in both directions).
 - `CourtOrder` — the operator follows the court's stated timeline. The substrate logs the order text and the eviction action.
4. **Audit trail**: every fast-path takedown enters a `hard_case:fast_path_takedown` Contribution ([CC 3.1.9.4](part_3_the_namespace.md)) for downstream review. Reviewers MAY file a `reconsideration:procedural_error` if the fast-path basis was misclassified.
5. **No counter-notice for immediate-removal cases**: by `legal_basis` design (TVEC / NCMEC / GIFCT / PerceptualHashCsam / CourtOrder all bypass counter-notice). The `expeditious-with-counter-notice` bases (`Dmca512` / `DsaArticle16` / `CommunityStandards` / `OsaIllegalContent`) take their counter-notice as a `reconsideration:{grounds}` row. A holder of the `review` duty over the content's community under [CC 4.5.5](#4.5.5) decides it, as the reversal paragraph below states.

**One tombstone row for takedown and purge.** A duty-holder's takedown and a trust-root `steward_purge` ([CC 2.4.1.1](part_2_the_grammar.md)) execute as the same tombstone row — plane, target digest, the authorising `takedown_notice`'s id; never content. The row **replicates**, so that every peer holding a replica learns to descend. Only the admission check, the reach and the dwell before deletion differ. A duty-holder's notice is admitted by the [CC 4.5.5](#4.5.5) enforced-admission rule and reaches the bytes plane only. A `steward_purge` notice is cosigned by the trust root and reaches any plane.

**The purge dwell.** An immediate-removal basis destroys on receipt. A `steward_purge` **hard-deletes once the retraction round settles — `W` = 72 h after the tombstone ([CC 2.6.7](part_2_the_grammar.md); the one "until everyone has heard" constant, not the 24-hour fuse)**. This is a substrate-stated dwell, not a peer acknowledgement, and the fastest descent of [CC 6.1.2](part_6_the_coherence_mathematics.md), not a new primitive. No acknowledgement plane exists. `purge_not_settled` refuses an early finalize. The tombstone outlives the row. A retraction the door cannot admit **aborts** the purge (`purge_retraction_inadmissible`). A purge is whole or not at all, never a half-emptied selection. A tombstoned record is refused at every admission door and never served (`purge_tombstoned`).

**Withhold windows and reversal (normative).** An `expeditious-with-counter-notice` basis withholds before it deletes. On the notice's admission a holder stops serving the bytes and keeps them for the basis's window, then hard-deletes them. The windows are `Dmca512` 10 days, `DsaArticle16` 14 days, `OsaIllegalContent` 14 days and `CommunityStandards` 30 days. Each window is counted on each holder from the instant it executes the tombstone. So every holder withholds for the full window from its own receipt of the notice. An immediate-removal basis has no window: its bytes are destroyed on receipt (item 2). A takedown is **reversed** by an admitted `reconsideration:{grounds}` row whose `outcome` is `reversed` and which names the `takedown_notice`. That row is signed by a key holding the `review` duty over the content's community under [CC 4.5.5](#4.5.5). The reversal replicates like the tombstone, so every holder sees it. A reversal or a lift voids the notice at a node whenever that node comes to hold it, even ahead of the notice. A node's own clock decides when that node destroys the bytes it holds, and never whether the row stands. A holder that destroyed the bytes before the reversal reached it shows the row as not held here, and may fetch it again. Whether bytes are withheld is computed when they are read, never stored as a flag. They are withheld while an admitted notice stands against them with no admitted reversal and no admitted lift by the members ([CC 4.5.13](#4.5.13)). A reversal therefore restores according to when it lands:

- **Inside the window** the bytes are still held: serving resumes, the hard-delete sweep skips them, and the holder re-acknowledges `here` ([CC 3.1.3.3](part_3_the_namespace.md)).
- **After the window** the bytes are gone from every holder that followed the window. The reversal voids the notice and lifts the tombstone, so the rows regain their standing. Any holder that still has the bytes, or the publisher re-publishing the same content hash, may serve them again. No holder is obliged to have kept a copy.
- **Under an immediate-removal basis** (for example a misclassification reversed under `reconsideration:procedural_error`, item 4) the reversal lifts the tombstone and restores the rows' standing. It cannot restore destroyed bytes, and the publisher may re-publish.

**Erasure at the subject's request (normative).** An ordinary row *about* a subject is erased on the subject's request by the subject's own `withdraws`. Where the subject holds a federation key, this is [CC 2.4.1.1](part_2_the_grammar.md) rule 2. Where the subject proved identity out of band, it is rule 3 through a `delegates_to` proxy chain with `scope ⊇ {consent_revocation}`, the node acting as that proxy. An **adverse** row about the subject, any row on the kept list of [CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1), is reached by no subject-authority path. The kept list stands. Every other reading lets a subject, or a node fronting one, launder its own record. So the request is executed by the row's **producer** under rule 1, the data controller withdrawing its own row, or refused with reason under Article 17(3) ([CC 4.4](#4.4) `erasure_policy`). The subject's contest path stays `reconsideration:{grounds}` ([CC 4.5.5](#4.5.5)). The replicated fact is the ordinary tombstone by digest per plane (the one tombstone row above). There is no node-local purge basis for erasure. An agent's trace goes the same way: by its signer's `withdraws` under rule 1, or a named party's under rule 2 or 3. A delete by key never reaches the kept list. A node's purge-ledger entry recording the execution is informational, never a notice. A hard case recording an erasure MUST NOT name the subject. This is the GDPR Article 17 route of the [CC 4.4](#4.4) compliance table, stated where the tombstone lives.

**The takedown-isn't-a-coup property.** Fast-path takedowns happen via this protocol and nowhere else. A `takedown_notice` targets content under a community's duty-holders ([CC 4.5.5](#4.5.5)), and `federation_keys` is not such a target. A notice demanding the removal of key records for whole categories of participants is refused at the enforced-admission gate like any other unauthorised action. The halt is no escalation path for this case ([CC 4.2.1.1](#4.2.1.1)). It pauses agents' acts and touches no data door ([CC 4.2.1.1](#4.2.1.1)).

### 4.5.4 `registry-named` — Named-moderator existence invariant + the election in merit order

**Community law (normative).** Five lines govern every `community`. Every statement about a community's duty holders elsewhere in this document follows from them.

- **(i)** A community's record declares the duties that must be carried.
- **(ii)** Each declared duty has at least one accountable holder who accepted it.
- **(iii)** Duty holders are equals. Each acts alone within its duty, and the members may lift any act.
- **(iv)** A duty seat is conferred by a strict majority of the duty holders, and withdrawn by a strict majority of the other duty holders, the holder concerned not counted. Where there are two holders or more, neither takes fewer than two voices. A lone duty holder confers alone, with the new holder's acceptance.
- **(v)** With no duty holder left the room locks, and the members' count seats one.

**What the five lines give.** A duty seat is two consents, the placer's and the holder's, one naming the other. It is no other object than those two rows, and nobody holds a duty they did not accept. A holder is accountable when its key ends at an accountable human (`accountable_root`, [CC 3.2](part_3_the_namespace.md)). A founding record seats the duty holders it names, each by their own signature on it. Whoever founds a community alone is its first duty holder. A community has members and duty holders, and no other tier. No duty holder ranks above another: none is senior in law, none is first, and none breaks a tie. `moderate` is a duty every community's record declares (rule 1 below), and a record MAY declare others. The members' lift is the `moderation_overturn` row of [CC 4.5.13](#4.5.13). The members' count that seats a holder is the election of rule 2. The members MAY recall any duty holder, however that holder was seated ([CC 4.5.13](#4.5.13)). A removal from the roster under the `consensus_protocol` ends the removed member's duty seats, since a non-member holds no duty. How a conferral carries its voices on the wire is the implementer's.

**No unmoderated multi-party space.** A `community` ([CC 3.2](part_3_the_namespace.md)) operates / federates **only while it has ≥1 active holder of its `moderate` duty** ([CC 4.5.5](#4.5.5)) — the moderation analogue of the [CC 3.2](part_3_the_namespace.md) steward-binding gate.

Three normative rules:

1. **Existence gate.** A `community` is admitted, and continues to federate, **only while ≥1 member holds the live `moderate` duty**. Its founding record **seats one**, who signs it. A community with no active `moderate`-holder is non-conformant.
2. **The election.** When a community has no duty holder left,
   - because the last holder's seat lapses (`withdraws` against the seat's `delegates_to`, or inactivity past the community's freshness window),
   - or because its last holder left,

   the community **locks and elects** ([CC 4.5.13](#4.5.13), the moderator election): read-only until a 24 h ranked-choice vote over its own roster seats one.

   While another duty holder remains, a vacant seat is conferred under line (iv), and the community does not lock.

   **The ballot is the roster, shown in this order:**
   - highest [`moderation_track_record`](part_3_the_namespace.md) ([CC 3.1.9.2](part_3_the_namespace.md)) first,
   - then earliest membership read as the admission order of the roster lineage ([CC 3.2](part_3_the_namespace.md) T6, a chain of versions and never a signer's instant),
   - then lexicographic `key_id`; where no member has a track record yet, the admission order alone.

   The order is presentation only: it confers nothing and decides nothing. The members' own signed votes are the appointment. A tie seats nobody, and the count runs again.

3. **Fail-secure.** If no eligible member can be named (none consenting, none whose appointment roots in an accountable root — `accountable_root`, [CC 3.2](part_3_the_namespace.md)), the community **fails-secure** — it MUST NOT federate / operate at moderated capability. **Better no group than an unmoderated one.** (Degrade, never escalate — the fail-secure default.)

**Named-moderator binding — the substrate-resolvable shape.** "K is a named-moderator over community C" is an **appointment**: a `delegates_to(authority → K, scope ⊇ {moderate|takedown|review}, community_id: C)` whose root `authority`:

- is in **C's authority set** — a live duty holder of C conferring under line (iv), or the members' count under line (v);
- and is an accountable root (`accountable_root`, [CC 3.2](part_3_the_namespace.md): an accountable adult user key, or a steward-bound key).

It rides the **existing** `community_id` envelope field + `delegates_to`; **no new shape.**

A substrate resolves: **`is_named_moderator(K, C, duty)`** ≔ ∃ live `delegates_to` chain `root →* K` with every edge `scope ⊇ {duty}`, `community_id == C`, `root ∈ authority_set(C)`, and `accountable_root(root)` ([CC 3.2](part_3_the_namespace.md) — a key that ends at an accountable human).

*The authority set.* The set `authority_set(C)` says who may *confer* a seat: the live duty holders of C, and the members' count where none is left. A conferral carries the voices of a strict majority of the duty holders, and a withdrawal those of a strict majority of the other duty holders, the holder concerned not counted. Where there are two holders or more, neither takes fewer than two voices. So of two holders neither unseats the other, and no holder unseats a lone one: there the seat is withdrawn only by the members' recall. A lone duty holder confers alone. Every conferral carries the new holder's own acceptance. A member who holds no seat moderates nothing. In a room that rides the Anonymous Tier the appointed key MAY be an anonymous identity ([CC 5.4.6](part_5_transport_substrate.md#5.4.6) item 1). This narrows a room's duties and reaches no further: the review of a licence stays with the authority that issued it ([CC 2.4.1.2.1](part_2_the_grammar.md#2.4.1.2.1)). The members of that authority rule on a reconsideration as parties to the quorum that issued it, not as holders of a room's duty.

**The election (rule 2) emits exactly this appointment shape:** the voters' own signed ballots are the room's signatures under its protocol, and the winner's acceptance is the appointee's consent. The seated moderator is resolvable **identically** to a hand-named one (one code path, no special case). No node signs anything: an ungoverned room is not allowed, so it is locked, and the lock ends only by the members' own hands. The seated holder passes `accountable_root` as an appointed one does: an anonymous identity passes as its own accountable root, steward-bound to its own user key ([CC 5.4.6](part_5_transport_substrate.md#5.4.6) item 1), with the age band it declared at first run.

**A seat outlasts a change of protocol:** a duty seat stands on its two consents, so it persists when the community changes its `consensus_protocol`. The change alters how the roster is counted, and never who holds a duty.

**The vote grants the duty, NOT fiat (anti-censorship).** The elected moderator holds the [CC 4.5.5](#4.5.5) `moderate`/`takedown`/`review` duty — but every **action** is constrained, so this is not arbitrary power:

- (a) the [CC 4.5.6](#4.5.6) operational-language gate at admission,
- and (b) deterministic verdicts + the [CC 4.5.5](#4.5.5) Reconsideration appeals (recused reviewers). A reviewer is recused from a reconsideration of an act they took, of an item they authored or reported, and of an act that names them.

**The vote grants the seat; the gate + appeals constrain the action.** The duty is itself revocable and a lapse opens a new election, so capture is bounded.

**1+4 preserved.** `moderation_track_record` rides `scores` ([CC 3.1.9.2](part_3_the_namespace.md)); the existence invariant + the election are admission/composition rules over the existing `delegates_to` (`moderate` scope) + the reputation corpus. **No new structural primitive.**

**Enforcement layer — substrate, at admission *and* on every federation step.** The existence gate (rule 1) is a **substrate invariant, not a governance- or consumer-policy-layer obligation.**

The substrate MUST evaluate `is_named_moderator(·, C, moderate)` over a `community` `C` at two points:

- **(i) at admission** — `C` is admitted to federate **only if** ∃ a live `moderate`-holder resolvable by the rule-1 shape;
- and **(ii) on the federation path** — every cross-region propagation / federation apply step keyed on `C` MUST re-check live `moderate`-holder existence **at apply time**. So a community that *loses* its moderator, by any cause of rule 2 or by a lapsed term or a recall, cannot continue at moderated capability without one.

On that loss the remaining duty holders confer the seat under line (iv). With none left the community locks and elects ([CC 4.5.13](part_4_composition_governance.md)). It **fails-secure** (rule 3) — MUST NOT federate at moderated capability — while it has no seated moderator. **No governance or consumer-policy layer may admit or sustain a moderator-less `C` into federation: the gate lives where the write lands.**

This mirrors the [CC 3.2](part_3_the_namespace.md) steward-binding gate, which the substrate likewise enforces at admission rather than delegating to a higher layer. The `is_named_moderator` resolution is the **primitive** this gate consumes; the **gate itself** — admission check *plus* federation-path re-check — is **substrate**, not detector or consumer filter policy ([CC 4.4](part_4_composition_governance.md)).

### 4.5.5 `takedown-moderation` — Moderation as a delegable duty — `moderate` / `takedown` / `review`

This entry says what anyone may do about content or a member on their own account, what needs a moderation duty, and how a node checks that duty at admission. Moderation is a **delegable *duty*, not a platform- or fabric-assigned role**. A participant exercises a moderation / takedown / review duty **as themselves**, or delegates it via `delegates_to`. The delegate is **their agent** (AI on-behalf-of) or **any trusted party** (another human, a community moderator). This is the wire foundation under the child-safety / takedown / accord UX, and the spine of *accountability ships ahead of capability*. Every media/chat surface **runs under this duty as a condition of carrying content**. The duty is enforced at admission (below) and wired through the fabric. The delegation row, its scope kinds and how a delegation ends are the entry of [CC 4.4.3.4.3](#4.4.3.4.3).

CEG **names** the four duties as canonical `scope` kinds and **enforces** their admission. This mirrors `consent_revocation`, the one scope CC 2.4.1.1 rule 3 already enforces ([CC 2.4.1.1 rule 3](part_2_the_grammar.md)). The kinds + their action primitives are pinned at [CC 4.4.3.4.3](part_4_composition_governance.md#4.4.3.4.3):

| scope | emits, on the delegator's behalf | primitive |
|---|---|---|
| `moderate` | `moderation:{allegation_type}` ModerationEvent + report→`scores` + `age_assurance`/`content_class` gates | [CC 3.1.9.2](part_3_the_namespace.md) / [CC 4.4.3.10](part_4_composition_governance.md) |
| `takedown` | `takedown_notice` (incl. the CC 4.5.3 immediate-removal fast-path) | [CC 3.3.2](part_3_the_namespace.md) / [CC 4.5.3](#4.5.3) |
| `review` | `reconsideration:{grounds}` appeal / review | [CC 3.1.9.2](part_3_the_namespace.md) |
| `slash` | `slashing:{outcome}` verdicts and the `quarantine:{state}` marker plane | [CC 3.1.9.2](part_3_the_namespace.md) |

**Two layers — open labeling, and authoritative action.** Moderation in CEG spans both layers of the composable/stackable model. It unifies them on the 1+4 grammar and adds the enforced action tier.

**Open labeling — anyone, no authority.** Anyone MAY file a `scores` Contribution against anything they see (an *opinion/observation*, not an action). It is **visible to everyone who chooses** to read it. Consumers compose **filters** over the score graph (hide / blur / annotate / down-rank) as pure consumer policy ([CC 4.4](part_4_composition_governance.md)). This generalizes independent labelers: stackable, swappable, subscribed by choice. A filter MAY **escalate to an auto-finding** (e.g. a [CC 4.5.7](#4.5.7) CSAM watchlist match auto-fires a `takedown_notice` under an *enabling authority*), turning a passive filter into an action.

**Mute (normative).** A member MAY mute another member. The mute is a filter in the muter's own reader that changes no row, no roster and no standing. The muted member is not told of it. The mute never hides from the muter a row that names the muter and reaches them. A mute removes nothing that [CC 4.5.5](#4.5.5) shows a person about themself.

**Authoritative action — the enforced duty.** Hiding-for-yourself needs no authority; **acting on a group's behalf** (a takedown, an authoritative ModerationEvent, an appeal ruling) requires the delegated `moderate`/`takedown`/`review` duty (below). [`moderation_track_record`](part_3_the_namespace.md) ([CC 3.1.9.2](part_3_the_namespace.md)) composites a moderator's action outcomes into the **relative, positional reputation** decentralized-moderation converges on. It is never a single global score.

One grammar covers a group chat, a classroom (teacher = delegated `moderate`), a town hall, an art gallery, a forum, a chat server, a community of millions: **the labeling open + filterable, the authority delegable + attenuable + revocable.**

**The good-faith warning (normative).** A warning that another member is a danger can be made two ways, and the way decides its standing. Said as peer speech, a `scores` row naming the person, it is that person's to retract under [CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1) rule 2. What the speaker keeps of their own words, and their path to the moderator, are stated there ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1)). Filed as a harm report with the room's named moderator (`moderation:{allegation_type}` under the `moderate` duty), it is a duty-holder's record on the accountability trail. The person named cannot withdraw that record and contests it by `reconsideration:{grounds}`. The person named sees that it exists, its kind, what follows from it and who answers for it. The moderator's process MAY shield the reporter. The action taken on that record runs under the floor of [CC 4.5.13](#4.5.13), no single vote excluding. The record is never purgeable ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1)). A warner who wants the warning to stand files it; one who only speaks has spoken. A false report is contested like any other, and the reporter answers for it on the record (`moderation_track_record`, [CC 3.1.9.2](part_3_the_namespace.md#3.1.9.2)). Filing changes the duty under which the statement is held, never its audience.

**Subject standing (normative — the CC 3.4.5 contestation pair).** The **subject of the target attestation** holds standing to file `reconsideration:{grounds}`. A licence subject **can see every licence about them** (a read over rows they are party to, stated here so that the promise of redress is checkable). A licence subject contests by reconsideration, never by withdrawal ([CC 2.4.1.1](part_2_the_grammar.md)). Contestation is at zero disclosure: the subject files band-blind, and a duty-holder who CAN see the composition performs the valence-sensitive step. This standing is what makes the kept list of CC 2.4.1.1 admissible. The withdraws path closes only because a real contest path exists.

**What the person named sees (normative).** The person named always sees that a record about them exists, its kind, its consequence and who answers for it. Peer speech and an authority's act are visible to them in full. A duty-holder's record MAY withhold the reporter's identity and the report's content from the person named where the duty-holder's process protects the reporter, the moderator's process of [CC 4.5.4](#4.5.4) included.

**A duty holder of a private room (normative).** In a private room ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)) a duty holder holds a room key in its duty seat, and signs every verdict under that key. The subject of a duty action is a room key, and an author's own takedown is signed under the room key that is the content's subject. A room key ends at an accountable human through its binding, so clause (b) below is checked by the nodes that hold that binding and waits at one that does not. A room chooses at its founding whether a report to a duty holder outside it can be verified. A room that wants this seats that duty holder, who then holds a room key in the duty seat and every binding, and holds no content key. A widening in such a room names that duty holder's acknowledgement of the joiner's binding and waits until it is held. A reporter shows that duty holder the rows, and the bindings it holds tell it who signed them. A report convinces that duty holder alone, and the reporter cannot make a binding that names someone else. In a room that seats no such duty holder, a report made outside the room rests on testimony.

**Enforced-admission rule — the principal is the chain root, NOT a payload field.** The principal an action is taken *on behalf of* is **discovered by walking the `delegates_to` graph upward from `attesting_key_id`**. It is **never** carried in a payload field. There is deliberately **no `on_behalf_of` (or equivalent) envelope field**. A side-field both violates the 1+4 lockdown *and* opens a bypass. If "absent field ⇒ as-self ⇒ admit", then any emitter that simply omits the field (e.g. an AI agent or untrusted party firing a takedown) is admitted as-self with no accountable chain proven. The gate then becomes a no-op exactly where it is load-bearing. A duty action (`takedown_notice`, `moderation:*`, `reconsideration:*`, `slashing:*`, `quarantine:*`) is admitted **iff** one holds **positively**:

- **(a) as-self** — `attesting_key_id` *itself* holds the matching duty over the target: it is the target content's own subject, **or** the target community's [CC 4.5.4](#4.5.4) named-moderator / `moderate`-holder. A zero-hop chain rooted at itself. Content is a community's where a live row places it at that community's scope, a `supersedes` that widens it included. A notice on that ground reaches the copy in the room and never the author's original at `self`.
- **(b) delegated** — a live `delegates_to` chain `root →* attesting_key_id` where **every edge bears the matching scope** (`scope ⊇ {moderate|takedown|review|slash}`), the **root holds the duty over the target** and is an **accountable root** (`accountable_root`, [CC 3.2](part_3_the_namespace.md) — a key that ends at an accountable human), depth within the cap of [CC 4.1.1](part_4_composition_governance.md), and **no edge is `withdraws`-revoked**.

Otherwise **REJECT**. **Absence of a principal field is NOT an admit condition**. Admission requires (a) or (b) to hold positively. A verifier MUST NOT read "no field present" as "as-self". This is the faithful mirror of `consent_revocation` ([CC 2.4.1.1 rule 3](part_2_the_grammar.md)), which derives its principal from the existing `subject_key_ids` relationship + the chain, never a side-field. Substrate SHOULD record which rule + which root admitted the action (the CC 2.4.1.1 per-rule audit metadata).

**Target → duty-holder resolution — makes the rule substrate-enforceable.** "Holds the duty over the target" is resolved by mapping the action's target to its duty-holder set, then checking the two predicates against it:

| Action and target | Duty-holder set |
|---|---|
| `takedown_notice{content_sha256}` | the content's **authoritative** subject set `subject_of(content_sha256)` (self — see the resolution rule below; **not** the action payload's self-declared `subject_key_ids`) ∪ `is_named_moderator(·, C, takedown)` for the content's community `C` (its `cohort_scope: community` / `community_id`); on a hash match under `PerceptualHashCsam`, also the owner of the node where the detection occurred ([CC 4.5.7](#4.5.7)) |
| `moderation:{allegation_type}` against a subject | `is_named_moderator(·, C, moderate)` for the relevant community |
| `reconsideration:{grounds}` against a prior action | the **subject of the target attestation** (the standing granted above) ∪ `is_named_moderator(·, C, review)` for that action's community; the ruling on it stays with the review-holders |
| `reconsideration:{grounds}` against a `licensure:{A}` row | A's authority set ([CC 2.4.1.2.1](part_2_the_grammar.md)) plus any holder of a `review`-scoped chain from that set |

**(a) as-self** holds iff `attesting_key_id ∈ duty-holders(target)` (a subject, or `is_named_moderator`). **(b) delegated** holds iff the chain `root ∈ duty-holders(target)` ∧ `accountable_root(root)`. Both **`accountable_root`** ([CC 3.2](part_3_the_namespace.md) — a key that ends at an accountable human) and **`is_named_moderator`** ([CC 4.5.4](#4.5.4)) are resolvable from existing rows (community record + `identity_occurrence` + `delegates_to` + `community_id` + `subject_key_ids`). So CC 4.5.5 is **fully substrate-enforceable**: community moderation is not rejected for lack of a resolvable shape. No new structural primitive.

**Subject authority is resolved from the content's signed provenance, NOT the action payload.** The subject side of admit-(a) has the same substrate-resolvability requirement as the named-mod path: *which* `subject_key_ids` is authoritative. A `takedown_notice` / `moderation:*` action carries a `content_sha256` **and** its own payload `subject_key_ids`. A substrate that reads the subject set from the **action's own payload** lets an actor self-declare `subject_key_ids = [self]` over content it does not own. The actor then satisfies "as-self" and takes down arbitrary content **without being a named-moderator** (a narrower, attributable re-opening of the takedown-isn't-a-coup hole on the subject path; the named-mod path is unaffected). The subject claim MUST instead be verified against the content's **establishing attestation**:

- **`subject_of(content_sha256)`** ≔ the signed `subject_key_ids` of the **establishing attestation** — the `scores` Contribution whose content the `content_sha256` binds (the [CC 2.3](part_2_the_grammar.md) subject set is signed *inside* that attestation by its producer, not assertable by a later third party). A substrate resolves `content_sha256` → establishing attestation → its signed `subject_key_ids`. This is the same content-hash → signed-attestation resolution every [CC 2.1](part_2_the_grammar.md) verifier already performs; no new index.
- **Admit-(a) subject-self** for content targets then means `attesting_key_id ∈ subject_of(content_sha256)` — the **signed** subject, never the takedown payload's self-declared set. The action payload's `subject_key_ids` is, on the subject-authority path, **advisory only** (it MAY be used to *route* / *queue*, but MUST NOT be the set admit-(a) is checked against).
- **Fail-secure when the establishing attestation is not locally held.** If a substrate cannot resolve `content_sha256` to its establishing attestation, `subject_of(content_sha256)` is **undetermined** and the subject-self clause **fails** (it does not admit) — the named-moderator clause of (a) and the delegated path (b) are the only remaining routes, exactly as for any other unprovable-authority case. Absence of provenance is never an admit condition (the same discipline as the `on_behalf_of` absence rule above).

With this, **both** clauses of admit-(a) — subject-self and named-moderator — and clause (b) resolve against **signed** state, never self-declared payload. The CC 4.5.5 gate has no remaining self-declaration spoof. This composes over the existing `scores` attestation + `subject_key_ids`; no new structural primitive.

**Deputization + attenuation (normative).** A deputy acts under its delegator's seat and holds no seat of its own. The delegation is two consents, the delegator's and the deputy's, and it ends when the delegator's seat ends. A `delegates_to` MAY permit its delegate to **deputize** (further-delegate the duty), but **only if the delegator granted it**. The delegator grants it by including `sub_delegation` in the granted `scope` ([CC 4.4.3.4.3](part_4_composition_governance.md#4.4.3.4.3)). Every sub-delegation **attenuates, never expands**: `child.scope ⊆ parent.scope`, and constraints may be *added* but never removed. This is the capability-attenuation rule. The chain is depth-capped by [CC 4.1.1](part_4_composition_governance.md) (five by default) and **revocable at any link**. A `withdraws` against *any* `delegates_to` in the chain invalidates everything downstream of it, *for acts not yet taken*. Authority is judged at the act's signed instant ([CC 2.4.1.2.1](part_2_the_grammar.md)). So a licence issued while the chain was live stands until its authority suspends or revokes it, and the withdrawal stops issuance from then on. Acts already taken under the duty stand ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1); [CC 3.2](part_3_the_namespace.md#3.2), standing over time). So a delegator decides at grant time **whether** their deputy may appoint further deputies and **under what constraints**. The delegator can sever the entire subtree with a single revocation. Deputize-a-teacher's-aide, hand-a-shift-to-another-mod and appoint-an-agent all run with bounded, revocable, attenuating authority.

**Attenuating a capability to a family — `infra:attest:{dimension_family}` (normative).** `infra:attest` grants *attest anything as the delegator's infrastructure*. It is the only vehicle a licensing authority otherwise has for "issue `licensure:CA_medical_board` on my behalf". That is an over-grant the attenuation discipline above exists to prevent, but which no field carries. A `scope` token MAY therefore be **sub-scoped to a dimension family**, `infra:attest:licensure:{authority_id}`, under the attenuation rule above: narrower only, never wider. `child.scope ⊆ parent.scope` is satisfied by construction, because the sub-scope names a subset of what the parent reaches. This adds no member to the closed `infra:*` set: it is a **caveat on an existing capability**, not a new capability.

**Sub-scope matching is directional, and a prefix test gets it backwards (normative).** A parent token satisfies a check for its child. A **child MUST NOT satisfy a check for its parent**. The naive implementation, `scope.starts_with("infra:attest")`, returns true for `infra:attest:licensure:X`. It hands a deliberately narrowed holder the full attest capability, silently repealing the attenuation that was the point of issuing it. A verifier MUST match on the full token with explicit parent/child semantics, and MUST NOT widen an **unrecognized** sub-scope to its parent. An unknown caveat fails closed, exactly as [CC 3.4.7.3](part_3_the_namespace.md) Clause B requires a membership test rather than a purity test for the same class of defect. That defect is the loophole spelled as a simplification.

**The "takedown-isn't-a-coup" property, made structural.** Every action is delegate-signed, delegator-traceable up the `delegates_to` chain, rooted in an accountable root (`accountable_root`, [CC 3.2](part_3_the_namespace.md) — a key that ends at an accountable human), and revocable. A takedown is therefore **coordinated + attributable + revocable**, never a unilateral seizure. A no-authority actor, or a state actor demanding removal of `federation_keys` for whole classes of dissenters, **fails the enforced-admission gate** ([CC 4.5.3](#4.5.3)). `federation_keys` is not content under a community's duty-holders. The halt, which pauses agents' acts and touches no data door ([CC 4.2.1.1](#4.2.1.1)), is no escalation path for it. The CC 4.5.3 immediate-removal timeline is unchanged: speed at the action layer; authority checked at the delegation layer.

**1+4 preserved.** This is a `scope` vocabulary + enforced-admission addition over the existing `delegates_to`. The action primitives (`moderation:*`, `takedown_notice`, `reconsideration:*`) already exist. **No new structural primitive.**

### 4.5.6 `admission-operational` — Operational-language gate at admission

Every new prefix admitted to the [CC 3.1](part_3_the_namespace.md) namespace passes the [CC 1.2](part_1_foundation.md) four-test gate. Failed admissions are revised (mechanism-descriptive reframe) or rejected.

### 4.5.7 `registry-watchlist` — Watchlist auto-detection — opt-in, per-group, separation-of-powers

**What this is for (normative).** The protections of this document are given to everyone: private rooms, no scanning of private content, and no account of a person kept without that person's act. People who make or trade images of the abuse of children would want those same protections. This section exists so that the network is not a home for them.

Matching content against a list is also part of how moderation without a person reading each item works at scale, and this document builds that. It does not pretend the mechanism is narrow by nature. A list is not limited by what it contains, because its entries are not shown and nobody can check that a list holds what its keeper says. The same mechanism can be pointed at hatred, at politics, or at whatever a keeper dislikes.

So this section limits what can be limited. A group chooses a list for itself and no one chooses for another. A match alone removes the bytes at that node and says nothing about a person. How much each source removes is the group's to read. Any group and any reader can leave a source. Automatic action runs under a seat that ends at an accountable person, and a judgment about a person is a person's signed act. What a community chooses for itself is its own. This document gives every community the same basis to choose on. Every rule below is read against two aims. A reading that would make the network hospitable to that trade is wrong. So is a reading that would let matching accuse a person who has done nothing, or be imposed on those who did not choose it.

Content-watchlist auto-detection: a [CC 4.5.5](#4.5.5) `moderate`- or `takedown`-scope holder **optionally** enables a watchlist (`watchlist:{id}`, [CC 3.1.9.4](part_3_the_namespace.md)) for a group they moderate. The fabric auto-fires the matcher at the **publish/share seam** and the action follows: CSAM → the node's `detection:*` row and the owner's `takedown_notice{PerceptualHashCsam}` ([CC 4.5.3](#4.5.3)); other → `detection:*` + a `moderation:*` ModerationEvent to the named moderator. Rides existing primitives — **no new structural primitive.** A match on known abuse imagery, by an enabled watchlist or by the hash tripwire of [CC 1.13.3.4](part_1_foundation.md#1.13.3.4), is removed under a `takedown_notice{PerceptualHashCsam}`. The person who owns the node where the detection occurred signs that notice ([CC 3.2](part_3_the_namespace.md#3.2), owner-binding). If that person's signing material is not available to the node at that moment, the node removes the content at once all the same. The node then files `hard_case:fast_path_takedown` ([CC 4.5.3](#4.5.3)), and the owner is asked to approve in retrospect. The node signs no notice, because a node key holds no judgment duty ([CC 4.4.3.4.3](#4.4.3.4.3)). What the node signs is a `detection:*` row, as a detector ([CC 3.4.8](part_3_the_namespace.md#3.4.8)). That row carries the list's registered source and a digest of the list version, the content's digest, the matching algorithm and the match distance as a whole number. It carries no entry of the list and nothing of the content. The owner's notice names that row, and a node admits the notice when its signer owns the node that signed the detection. Approval in retrospect is the owner signing that notice later, and until then the node's act binds no other holder. A holder that trusts the detector MAY withhold the content on the detection row alone, and destroys it on the notice. The rule errs on the side of the law.

**A match is one source's claim, and no finding about a person (normative).** A match has one effect of its own: the node that matched does not publish or serve the bytes, and removes them as this section says. A match confers nothing. No standing, score, flag or record about the person who offered the content, or about the owner of the node, follows from a match alone. Anything more is a duty holder's signed verdict under [CC 4.5.5](#4.5.5), and a detection is never the sole evidence for it. The `detection:*` row is the claim of the list's source at the list version it names. A reader reads that claim through its own trust in that source ([CC 4.4.3.8](#4.4.3.8)), and a reader that withdraws that trust reads none of that source's matches. A consequence in a group beyond the removal needs matches under two sources that share no operator. The person whose content was removed is told that it was removed, under which source and which list version. That person MAY ask the group's duty holder to reconsider ([CC 4.5.5](#4.5.5)). A list can be wrong, and a perceptual match can be made on purpose against lawful content. So a match is a claim to be tested and never proof. An operator's duty to report under law is the operator's, and this section does not change it.

**Whose content it was (normative).** A match is made at a seam, on content as it is offered. Where another key offered the content, the node refuses it before holding it and never shows it. The record of that match names the key that offered the content and says that the node refused it. It names the node's owner only as the one who refused, and the owner's notice is a notice about content that was never the owner's. The detector's seat in a private room is conferred inside the room. The authority's signed act that enables a list seats the room's nodes as detectors for that list, each under its room key, until that act is withdrawn. No detector there is trusted from outside the room, so no holder outside it withholds on such a detection alone. Where the content is the node owner's own, offered by the owner for publication or for sharing, the node refuses to publish or share it. Nothing of that match leaves the device: no row is served to anyone and no notice is owed. The owner MAY have the node destroy the bytes, and that act leaves no row. A record MAY be kept at the owner's own scope, which the owner alone may file or delete. This section states what a node does. It states nothing about what any law asks of a person or of an operator.

**Detection in a private room (normative).** In a private room ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)) the node signs the detection under its room key, and the owner signs the notice under the owner's room key. Ownership is read from the owner-binding inside the room ([CC 3.2](part_3_the_namespace.md#3.2)), which is a row of the room and names no identity. A node admits the notice when its signer owns, by that row, the room key that signed the detection. So the record names room keys and no person. The detector's seat in a private room is not held under a trust root outside it. A fresh room key holds no outside conferral, and tying it to the node's public key would name the node's owner. The seat is conferred inside the room by the act that enables the list. That act, signed by the room's `moderate` or `takedown` authority, seats the room's nodes as detectors for that list. It is an ordinary seat: the authority offers it, the node's room key holds it, and withdrawing the enabling ends it. A detection in a private room is therefore admitted on standing in the room. It remains one source's claim and never a verdict, and the removal still needs the owner's notice. No holder outside the room withholds content on such a detection alone, since no detector of a private room is trusted from outside it.

**Opt-in, per-group, NEVER global (normative).** A watchlist is enabled per-group by its `moderate`/`takedown` authority; a global "scan everything" config is **non-conformant** — that is the bulk-surveillance posture the framework refuses. Enable/disable is **signed by the authority and revocable** (`withdraws`). The hash tripwire at the public seam is a different thing and is always on. It matches at a promotion into the Commons and at a post into a `public` room, and scans no group ([CC 1.13.3.4](part_1_foundation.md#1.13.3.4)).

**Separation of powers (the responsible-design invariant).** No single party does all three:

| Party | Holds | Cannot |
|---|---|---|
| **Fabric** (the node) | the *mechanism* — the matcher at the publish/share seam | provision the hash-DB; choose to enable |
| **Operator** | the *licensed hash-DB* (IWF/NCMEC/PDQ, [CC 4.5.10.1](#4.5.10.1), operator-provisioned + unshippable) + the NCMEC report obligation | turn it on for a group; act without the authority's opt-in |
| **Authority** (`moderate`- or `takedown`-holder) | the *opt-in* (per-group enable) | run the match itself; access the licensed list |

**Audit — never silent (normative).** Enabling a watchlist emits `hard_case:watchlist_enabled:{group}` ([CC 3.1.9.4](part_3_the_namespace.md)) — who turned it on + which list; **every match** emits `hard_case:watchlist_match:{group}`. Enablement and matches are on the record, always. The record of a match names the group, the list's source and the list version, and names no person. Any member of the group MAY read the count of matches under each source and list version. So a list that has been captured, or has drifted, shows as a rise in that count, and the group can leave it.

**CSAM-disable non-silent floor (normative).** Disabling a **CSAM** watchlist MUST be an audited act: a `withdraws` signed by the authority that **emits `hard_case:watchlist_enabled` (disable variant)**. **Silent removal of a CSAM list is barred** (a predator-operator cannot turn off CSAM detection without leaving a trace). Ordinary (non-CSAM) lists may be freely toggled. This is the floor that keeps the opt-in honest.

**Honest scope.** A watchlist's detection runs **only at the publish/share seam of enabled groups** — it **cannot** reach [CC 5.2](part_5_transport_substrate.md) self/family private content (the universal E2EE limit; not claimed solved), and CEG does **not** mandate client-side scanning. **1+4 preserved** — `watchlist:{id}` rides `scores`/config over `delegates_to`; the audit reasons ride the existing `hard_case:*` prefix; the actions ride `takedown_notice` / `detection:*` / `moderation:*`.

### 4.5.8 `identity-set-2` — `identity_type` as a set — single-key role cohabitation

Per [CC 3.4.7.1](part_3_the_namespace.md). `federation_keys.identity_type` is a **set of labels** a key states about itself, not a single scalar. It opens no reserved family: a duty is held by delegation ([CC 3.4.7](part_3_the_namespace.md#3.4.7)). This routes through the [CC 4.5.1](#4.5.1) amendment process.

#### 4.5.8.1 `cohabitation` — Cohabitation discipline for constitutional + substrate roles

A label in the set confers nothing. Every reserved duty is held by a live conferral ([CC 3.4.7](part_3_the_namespace.md#3.4.7)), and the accord's standing by its charter. Two cases carry defence-in-depth guidance against cohabitation:

- **`accord_holder` ([CC 3.4.1](part_3_the_namespace.md) + [CC 4.2](part_4_composition_governance.md))**: the halt authority of CC 4.2. Consumer policy SHOULD treat an `accord_holder` key that also holds non-constitutional roles (e.g., `{accord_holder, agent}`) with elevated scrutiny — the accord roster's halt authority is strongest when its keys are single-purpose. The cohabitation is NOT forbidden at the wire layer (the substrate cannot adjudicate constitutional intent), but the CC 4.2 entrenched-`family` discipline RECOMMENDS dedicated accord-holder keys.
- **A node's reports ([CC 3.4.3](part_3_the_namespace.md))**: a `system:*` row is signed only by the node it is about, under `infra:attest`. A key that also holds an agency delegation is still held to that rule for its reports. Holding both does not relax it.

#### 4.5.8.2 `amendment-what` — The role set is the representation

| Surface | Rule |
|---|---|
| `federation_keys.identity_type` | a set of role strings; a scalar is read as a singleton set |
| CC 3.4 reserved families | the duty the signer holds ([CC 3.4.7](part_3_the_namespace.md#3.4.7)); the set is never read to open one |
| CC 3.1 dimension namespace | independent of the role set |
| Envelope ([CC 2.1](part_2_the_grammar.md)) | independent of the role set |
| 1+4 structural primitives ([CC 2.4](part_2_the_grammar.md)) | independent of the role set |
| subject_kinds ([CC 3.3](part_3_the_namespace.md)) | independent of the role set |

**The rule (normative).** `identity_type` is a set of role strings, and a scalar reads as a singleton set, so for a single-role key the set reading and the scalar reading agree: `X ∈ {X}` ≡ `X == X`. The set is not a [CC 1.7](part_1_foundation.md) "Nth path" (it adds no namespace surface); it lets one key carry several labels without widening the wire's expressive surface.

#### 4.5.8.3 `settled` — The agent-side stance

- **Capacity self-emission ([CC 3.4.5](part_3_the_namespace.md))**: **unaffected by role cohabitation** — which is the only claim made here. CC 3.4.5 also carries the normative consent-before-scoring gate and read-boundary rules; this section restates none of that material. What is unchanged is the interaction: the anti-Goodhart `attesting_key_id ≠ attested_key_id` rule binds regardless of how many roles a key holds. A key holding both an agency delegation and `infra:detect` still MUST NOT score its own `capacity:*` ([CC 3.4.5](part_3_the_namespace.md#3.4.5)). Role cohabitation does not create a self-attestation backdoor.
- **Reasoning-trace dimensions**: no reserved duty is required; reasoning-trace emission rides the agent role's open-vocabulary surface. Cohabitation does not change this.
- **Agent-intent / detector-envelope split**: a cohabiting key emits agent-intent attestations under the agent dimensions and detector verdicts under `detection:*` ([CC 3.4.8](part_3_the_namespace.md) worked example). The namespace keeps the two surfaces distinct; cohabitation grants the right to emit on each, never merges them.

#### 4.5.8.4 `documents-what-6` — What this documents

- That the set opens no reserved family, and that a duty is held by delegation ([CC 3.4.7](part_3_the_namespace.md#3.4.7))
- The canonical-bytes encoding for the set (sorted-ascending, deduplicated, comma-joined; single-role keys encode identically to their scalar form)
- The detector-fold worked example ([CC 3.4.8](part_3_the_namespace.md))
- The cohabitation discipline for constitutional + substrate roles (CC 4.5.8.1)

What it does NOT do:
- Expand the CC 3.1 dimension namespace, the CC 2.1 envelope, the CC 2.4 structural-primitive set, or the CC 3.3 subject_kinds (zero new wire surface beyond the `identity_type` representation)
- Enumerate a closed set of role values — `identity_type` members remain an open vocabulary owned per [CC 3.4](part_3_the_namespace.md) reservations + sibling-component vocabulary extensions
- Forbid cohabitation at the wire layer beyond the one pair [CC 3.4.7.3](part_3_the_namespace.md#3.4.7.3) Clause A refuses: a key whose `identity_type` contains `node` MUST NOT also contain `agent` or `user`. The substrate otherwise checks the duty a signer holds, and the cohabitation discipline of the constitutional and substrate roles is consumer and operator policy (CC 4.5.8.1)
- Address `affiliations` (the fourth `cohort_scope` tier, defined at [CC 4.4.3.2.8](#4.4.3.2.8))

### 4.5.9 `registry-geographic` — Geographic-community privacy invariant

Per [CC 3.2](part_3_the_namespace.md) `community` with `cohort_subkind: geographic` + [CC 3.3.3](part_3_the_namespace.md) `location_proof` + [CC 2.6.6](part_2_the_grammar.md) H3 cell canonicalization + [CC 4.4.3.2](part_4_composition_governance.md) Policy M.

A load-bearing privacy invariant: **joining a geographic community is a one-way disclosure**. Three sub-properties make this wire-format-level, not policy-level.

#### 4.5.9.1 `location-joining` — Joining is opt-in — substrate does NOT solicit location

A `location_proof` Contribution is emitted **only** by the subject themselves (`attesting_key_id == subject_key_id`). No delegation mints one: the substrate has no path to a location_proof on behalf of a key without that key's own signature.

Communities cannot **require** a location_proof from non-members (they can only **gate admission** on whether a member has produced one). The substrate has no mechanism for "involuntary location disclosure" via the wire format. A bad actor cannot force-publish another key's location_proof; without the subject's signature, the substrate rejects.

**No escalation path is needed.** A demand that the substrate emit `location_proof`s for non-consenting subjects asks for rows the admission door refuses: a `location_proof` without the subject's own signature is rejected, as stated above. The substrate's role at this primitive is mechanical opt-in enforcement. The halt pauses agents' acts and touches no data door ([CC 4.2.1.1](#4.2.1.1)), so it is not the remedy here; a legal dispute over content is routed by [CC 4.5.3](#4.5.3) takedown coordination under the [CC 4.5.5](#4.5.5) duty-holder gate.

#### 4.5.9.2 `rough-only` — Rough-only is wire-format-enforced

Per [CC 2.6.6.1](part_2_the_grammar.md): `location_proof.cell_resolution ≤ 7`. H3 resolution 7 hexagons average about 5 km² in area (edges about 1.2 km) — sufficient for city/borough disclosure without block/building precision. Producers attempting finer resolution have admission rejected at the substrate gate.

**This is the closure of an entire class of accidental over-share**: a malformed UI cannot publish precise location even if the client-side gating fails. The wire-format-level enforcement is the privacy primitive; UI is the second line.

Substrate emits `hard_case:location_proof_resolution_violation` ([CC 3.4.2](part_3_the_namespace.md)) on rejection so operators can observe malformed-client patterns. This is observability for operator debugging, NOT a slashing trigger — malformed producers are usually buggy clients, not attackers.

#### 4.5.9.3 `leaving` — Leaving is forward-only — the audit chain keeps the tombstone

A withdrawal reaches forward only ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1)), and departure is forward-secret ([CC 4.5.12.1](#4.5.12.1)). When a subject withdraws their location_proof (or leaves a geographic community):

- Forward visibility evicts (consumer policy treats the subject as "no current location proof" for new admission decisions from withdrawal-time forward)
- A withdrawn `location_proof` leaves serving like any row of the subject's own ([CC 4.5.3](#4.5.3)); the audit chain keeps the tombstone — that a proof existed and was withdrawn — and never the cell. What withdrawal and expiry govern is the present claim; the record that a claim was made is the tombstone, not the content.

The cost the subject opts into when emitting the `location_proof` is this. A copy a peer took before the withdrawal reached it is not recalled by the wire, as for every row ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1)), and the tombstone is what every holder converges on. What the wire format promises:

- **Rough-only** (CC 4.5.9.2): a claim, while it stands, is bounded to resolution ≤ 7, never finer
- **Opt-in** (CC 4.5.9.1): the claim exists only because the subject signed and emitted it
- **Auditability**: the subject can prove what they did or did not claim, and when; the tombstone is the receipt, and it carries no cell

#### 4.5.9.4 `documents-what-5` — What this documents

- The rough-only enforcement primitive at [CC 2.6.6.1](part_2_the_grammar.md) (resolution ≤ 7 for location_proof)
- The forward-only leave of [CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1), applied to location_proof
- The opt-in admission flow at [CC 3.3.3](part_3_the_namespace.md) (location_proof signed by subject only or delegates_to proxy chain)
- The geographic-community admission composition at [CC 4.4.3.2.3](part_4_composition_governance.md) (Policy M evaluate_subkind_admission for geographic)
- The substrate-self-report observability at [CC 3.4.2](part_3_the_namespace.md) (4 hard_case prefixes)

What it does NOT do:
- Mandate H3 over alternative geospatial systems for operator-internal use (operator choice; wire format uses H3 only)
- Provide a place-name registry (communities self-name; H3 cells are the substrate-level binding)
- Define specific cell-resolution conventions for community-side `geographic_constraint` (only `location_proof` is bounded to ≤ 7; communities MAY scope themselves at any resolution by their own choice)
- Codify other community subkinds (`professional` / `interest` / `local-business` / `event-attendees` / etc.)
- Address `affiliations`

### 4.5.10 `registry-hash` — Hash-database operator policy

Perceptual-hash matchers (PhotoDNA / PDQ / Project Arachnid / GIFCT hash-sharing) are pluggable at the substrate. Operators choose which matcher implementations to enable; CEG governs the access-policy contract.

#### 4.5.10.1 `hash-database` — Hash-database access landscape

| Matcher | Access posture |
|---|---|
| **PDQ** (Meta, 2019) | Open algorithm; the hash lists come from the gated feeds an operator can obtain |
| **PhotoDNA** (Microsoft, 2009) | Access-gated; restricted to vetted orgs (NCMEC + select platforms); substrate operators cannot download the hash database directly |
| **Project Arachnid** (C3P, 2017) | Access-gated; API access requires C3P partnership |
| **GIFCT hash-sharing** | TVEC-focused; access via GIFCT membership |

#### 4.5.10.2 `registry-operator` — Operator path (default)

For a CIRIS substrate operator running a federation node, **the default operator path is**:

> **Self-hosted PDQ matcher against the reference feeds the operator can obtain.** The PDQ algorithm is open. The hash lists come from the gated feeds an operator can obtain: the Canadian Centre for Child Protection's (C3P) Project Arachnid feed, which requires a C3P partnership, and GIFCT-published lists where available. No federation-level access-governance overhead; a gated feed's own terms apply. Operator carries responsibility for index freshness.

Of the three paths — (a) a self-hosted matcher, (b) clearinghouse delegation, (c) on-device OS-vended hooks — this is (a): it avoids the federation dependency at the protective layer that (b) would introduce, and the controversy around (c).

#### 4.5.10.3 `future` — Future hash-coalition path

Path (b), clearinghouse delegation — substrate operators delegating perceptual-hash checks to a trusted coalition peer via federation — requires a CIRIS hash-coalition that can serve as a clearinghouse. The slot is reserved; the coalition operator-onboarding flow is not specified here.

#### 4.5.10.4 `documents-what-2` — What this documents

- The closed-set of `legal_basis` values that compose with `PerceptualHashCsam` (the only `legal_basis` value that consumes hash-match output as immediate-removal trigger; see [CC 3.3.2](part_3_the_namespace.md))
- The operator-onboarding contract: an operator running a PDQ matcher MUST register their matcher's source feeds (which hash-list source URLs they're pulling from + freshness cadence) via a `system:perceptual_hash_matcher:registered` Contribution. Composes with [CC 3.1.3](part_3_the_namespace.md) Persist substrate-self-report discipline.

What it does NOT do: prescribe which hash databases an operator MUST use. Operator choice. CEG documents the wire-format slot + the operator-onboarding contract + the recommended default; concrete matcher selection is operator policy ([CC 4.5.10](#4.5.10)).

### 4.5.11 `bootstrap-content` — Bootstrap-content pattern

After federation genesis, a curated batch of proposal Contributions is admitted via the CC 4.5.1 amendment flow, populating the federation's substantive content surface with high-quality ethical-framework material. **Content-neutral**: any sufficiently substantive ethical-framework source can serve. The wire format admits content via the [CC 3.1](part_3_the_namespace.md) namespace; the [CC 1.2](part_1_foundation.md) gate ensures prefix names don't import source-tradition vocabulary.

**Multi-source commitment**: bootstrap batches from CARE Principles (Indigenous data governance), Buddhist economic-justice scholarship, secular humanist instruments, African philosophy of personhood work — all through the same amendment process. The framework is multi-traditional by design.

### 4.5.12 `family-self-2` — Self/family membership governance

Per [CC 3.3.6](part_3_the_namespace.md) `identity_occurrence` + [CC 3.3.4](part_3_the_namespace.md) `family` + [CC 4.4.3.4](part_4_composition_governance.md) Policy L + [CC 5.2](part_5_transport_substrate.md) structural-invisibility. The four governance decisions for self/family membership.

#### 4.5.12.1 `forward` — Forward secrecy on member departure

When a member leaves a family, or an occurrence is withdrawn from a self-collective, the rule is the one at [CC 4.4.3.4.5](#4.4.3.4.5). No rotation ceremony is needed at these scopes and none is defined.

**Rationale**: consistent with a withdrawal reaching forward only ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1)) + [CC 4.5.3](#4.5.3) "takedown isn't a coup" + [CC 4.4.3.5.1](part_4_composition_governance.md) consent-decay-doesn't-re-encrypt. The substrate's forward-secrecy posture is uniform across consent, takedown, and membership-departure surfaces.

#### 4.5.12.2 `envelope-multi` — Multi-family membership — envelope `family_id`

One identity MAY belong to multiple families. Each family has its own membership roster, and its content DEKs are wrapped to that roster; a `cohort_scope: family` Contribution MUST carry `family_id` ([CC 2.1](part_2_the_grammar.md) envelope field) naming which family's roster and visibility apply. Substrate rejects family-scoped Contributions missing `family_id`.

**Rationale**: avoids cross-family DEK confusion when one identity is in N families; gives the substrate an unambiguous routing key for the `key_grant` cascade per [CC 4.4.3.4.1](part_4_composition_governance.md).

#### 4.5.12.3 `admission-self` — Self-occurrence admission — single-vouch

A new `identity_occurrence` is proposed by a signature from EITHER the root `identity_key_id` (until the self evicts its genesis key) OR any currently active occurrence of that identity ("trust any device I've already onboarded"). A `node`-role signer counts only through its live owner-binding. A `user`-role key joins the self's roster by the self-roster door of [CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3). At one key that door is the owner's own signature. At two or more it is a strict majority of the live roster, the proposer included, or the lone path after its window unless a strict majority of the other members objects. Higher-assurance setups MAY layer requirements on `hardware_attestation` via consumer policy.

**Rationale**: matches user-intuition for self-membership ("my phone unlocks my laptop's trust posture for new devices"). A self of one key onboards a device by its own signature, and a larger self by the door above; the security gradient lives in the optional `hardware_attestation` field, not in the admission rule.

#### 4.5.12.4 `reservation-reserved` — Reserved-prefix substrate emissions — locked in CC 3.4.4

The membership-event kinds of [CC 3.4.4](part_3_the_namespace.md#3.4.4) are signed by the node that admitted the change ([CC 3.4.7](part_3_the_namespace.md#3.4.7)). Same discipline as the existing `system:*` substrate-self-report family.

#### 4.5.12.5 `family-admission` — Family admission — consensus_protocol (normative)

Unlike a self of one key ([CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3)), family membership changes are **NOT single-vouch by default**. The family's `consensus_protocol` field governs admission. Five canonical protocols (`founder_only` / `unanimous` / `majority` / `quorum:M/N` / `weighted:{rubric}`), a closed list, and `open:self_admit` is the open protocol of a public group ([CC 4.4.3.2](#4.4.3.2)). `founder_only` is conformant for a family and for a publisher-gated subscription, refused for a community ([CC 4.5.13](#4.5.13)), and admissible for an affiliation only under the one-voice countersign rule of [CC 4.4.3.2.8](#4.4.3.2.8).

The consensus_protocol field is itself subject to amendment via the SAME protocol's rules (meta-amendment shape parallel to [CC 4.5.1.2](#4.5.1.2)) UNLESS the family is `consensus_protocol_entrenched: true`. Entrenched families reject amendments at the substrate gate; replacement requires the family's documented out-of-band ceremony.

**Rationale**: families are multi-party collectives where membership changes have real consequences (admit-new-member = grant DEK access to all extant cohort_scope: family content). The consensus_protocol gives the family explicit governance over its own boundary. Self-amendment lets families evolve their governance as they grow; entrenchment lets safety-critical families lock the boundary against any internal authority.

#### 4.5.12.6 `documents-what-4` — What this documents

- The wire-format primitives that compose into self/family membership ([CC 3.3.6](part_3_the_namespace.md) + [CC 3.3.4](part_3_the_namespace.md))
- The structural-invisibility discipline at [CC 5.2](part_5_transport_substrate.md)
- The at-rest encryption flow composition at [CC 4.4.3.4](part_4_composition_governance.md) Policy L
- The consensus_protocol vocabulary (canonical kinds; open-vocab extension)
- HUMANITY_ACCORD as the canonical entrenched-`family` instance at [CC 4.2.3](part_4_composition_governance.md)

What it does NOT do:
- Lock the consensus_protocol vocabulary (open vocab; canonical kinds named for ecosystem coordination)
- Re-encrypt history on departure (a removal is never retroactive, [CC 4.4.3.4.5](part_4_composition_governance.md))
- Prescribe per-family entrenchment policy (operator/family choice)
- Document the at-rest encryption flow details (substrate-side)

### 4.5.13 `reverse-quorum` — Reverse-quorum governance — presence is authority, absence forfeits it

This entry says how a decision is taken where presence is authority: who may act alone, when a count carries, how a harm report is answered and how a moderator is elected. It also gives the policy numbers every door runs and what a person is shown before signing.

**Not a membership rule.** Reverse quorum is the commons objection brake. It never admits anyone to a family or community and confers no consent on anyone's behalf. Joining is [CC 3.1.3.2](part_3_the_namespace.md)'s proposal and acceptance.

**The general pattern.** [CC 4.2.6](part_4_composition_governance.md) is not a one-off kill-switch rule. It is the federation's **general governance shape**, and this section states it as such. **Presence is authority, absence forfeits it, a timer decides.** A decision opens a bounded window. One present, accountable actor may act alone. On that actor's absence a count carries, over the set the door's policy names (the policy as data, below). Whoever stays absent never blocks the present actor. The [CC 4.2.6](part_4_composition_governance.md) accord kill-switch is the **constitutional instance** of this pattern: one present holder fires, and a roster change counts its yes-votes against the standing roster, because the roster is the capture vector. **Community-scope moderation is its first community instance**: a present moderator acts, and on the moderators' absence the live community governs its own content. One mechanism, two scopes — the accord over humanity's off-switch, moderation over a group's content.

**Roles — members and duty holders, and no tier among them.** Community law is stated at [CC 4.5.4](part_4_composition_governance.md). A community is **required** to have a named **moderator** — the [CC 4.5.4](part_4_composition_governance.md) `moderate`-duty holder. That is the *only* required duty: the moderator is the fast-path decision-maker. A community's record **MAY** declare further duties. No duty holder ranks above another, and none oversees another. **A contested party MUST NOT confer a duty seat to manufacture a count or to dilute a pending protective veto** (the [CC 3.4.13](part_3_the_namespace.md) Q7-3 rule, which applies at community scope as it does there). Whoever founds the room alone is its first duty holder. **This document imposes no quorum *on* a duty holder's act; a community MAY impose one on itself (below).** Unilateral accountable authority within the duty is what a seat means. A holder resolves an action by a **single signature**.

**The mechanism — propose, 48 h window, a moderator acts, community falls back.** **Anyone MAY propose a moderation action** — a report, a takedown request, a keep-or-remove question. It is proposed by the [CC 4.5.5](part_4_composition_governance.md) open-labeling path (a report→`scores` Contribution against the target). The proposal opens a **48-hour participation window**. Two ways it resolves:

1. **A moderator acts unilaterally.** The community's **moderator** (the required `moderate`-duty holder, [CC 4.5.4](part_4_composition_governance.md)) resolves the action by a **single signature**, at any point in the window. A holder of another duty acts here only where it also holds `moderate` ([CC 4.5.4](#4.5.4)). **What a single signature resolves is content and a member's standing to speak in the room**: a withhold, a takedown of a row, a warning, a block for the room. **It is never a removal from the roster**, which is a roster change under the floor of this section in every protocol, open admission included ([CC 4.4.3.2](#4.4.3.2)). So no single key removes a member alone, and no duty holder removes another from the roster alone. At two members nobody is removed, since a unanimous removal is every other member and a strict majority of the roster, which at two coincide only if the one removed consents. An AI agent's key is the exception. A moderator of the room MAY remove it alone and at once ([CC 1.13.2](part_1_foundation.md)), and the members may lift that act as they may any act of a moderator. A duty holder may leave by their own forward-only act, the last one included. The reason is that the founding-core rule that keeps a lineage from stalling belongs to infrastructure communities and conferring families ([CC 3.2](part_3_the_namespace.md) T7) and not to a room. A duty holder who would rather hand the room on confers a seat on a member, with that member's own acceptance ([CC 4.5.4](#4.5.4)). A room whose last duty holder leaves locks, and its members' count seats one ([CC 4.5.4](#4.5.4)). This is the fast path, and the moderation analogue of the [CC 4.2.6](part_4_composition_governance.md) **fire-floor-of-1**: a single accountable party acts, and the absence of others never blocks them.
2. **On their absence, the community vote carries.** If **no moderator acts within the 48 h window**, the proposal is tallied by **a strict majority of the members who voted**. The members are those of the roster the proposal names. This is the [CC 4.2.6](part_4_composition_governance.md) participation window read at community scope. Presence asserts (a member signs a fresh proof-of-presence + vote over the proposal nonce, entering the live set `L`). A silent member is not in the denominator. The tally is taken over **who shows up**: the vote carries by a strict majority of those who voted, and the floor is two voices. The accord's roster change counts against its standing roster instead. The community **routes around** an absent moderator.

The reverse-quorum of this mechanism is a **fallback for the moderators' absence**. The 48 h figure is tuned so that a **present** moderator always has time to act unilaterally. The community fallback fires **only** on genuine absence. The members' check on an act a moderator did take is a separate door, the lift below.

**Why 48 hours (normative).** The window governs only the fallback, since a moderator rules at any time and a withhold is immediate. Its one job is the legitimacy of the members' majority, and 48 hours is the shortest span that gives every member in every time zone a weekday to respond, where 24 covers one working day and no day off.

**Two acts, not one (normative).** A member who sees harm has two acts and they are separate choices. A **report filed privately with the duty holder** (a named moderator) opens no window and is not shown to the room. The person named sees that a record exists, its kind, its consequence and who answers for it ([CC 4.5.5](#4.5.5)). It becomes the duty holder's record under [CC 4.5.5](#4.5.5), the reporter shielded where the process protects them. The moderator rules on it at any time or lets it rest. A **moderation action raised in the room** is public, names what is asked, and starts the 48 h window at once, the members responding and the fallback carrying on the moderator's absence. The client offers both and never folds one into the other.

**The members' check — one acts, the room may lift (normative).** A duty holder's single signature takes effect at once, and the members may lift it. Members object by signing `objection:raised` rows that name the act. The act is lifted when a strict majority of the roster as it stood at the instant of the act has objected within the 48-hour window. The window is read on signed instants, the objection's against the act's, so every node that holds the same rows reads the same lift. An objection counts at a node only where the node first held it within the freshness window `W` of its signed instant ([CC 2.6.7](part_2_the_grammar.md)). Only a member seated before that instant counts, so nobody joins a room to overturn it. The floor is two voices. Short of that count when the window closes, the act stands. (The policy table's row `moderation_overturn`.)

**What a lift undoes.** A lift undoes what can be undone: a warning, a block for the room, a withhold, and a takedown still inside its withhold window ([CC 4.5.3](#4.5.3)). An item restored by a lift returns consent-gated, behind the interstitial below, and is never restored to plain view. So a majority can end a silencing, and cannot put content before a member who has not chosen to see it.

**What no lift reaches.** A removal on an immediate-removal basis ([CC 4.5.3](#4.5.3)) is not objectable. A moderator's ruling on a report filed privately is not objectable, and no objection row names the report or its reporter. A removal from the roster was never a moderator's act and has its own door.

**No second bite.** The moderator whose act was lifted MUST NOT take the same act on the same item again. Another holder of the duty MAY act on it, and so MAY the same moderator on new facts stated in the act.

**Recall.** The members MAY recall any duty holder, however that holder was seated. A recall is one row cosigned by more than two thirds of the standing roster within the 72-hour standing window. The floor is two voices. Where the recall leaves no duty holder, the room locks and elects. The duty holders withdraw a seat by their own count ([CC 4.5.4](#4.5.4)). (The policy table's row `moderator_recall`.)

**The first seat.** Whoever founds a room alone holds its first duty seat, by the founding record they signed. That seat is a seat like every other. It carries no rank, and it is conferred and withdrawn as [CC 4.5.4](#4.5.4) states. The room MAY lift its holder's acts and MAY recall its holder, as it may any duty holder.

**The moderator election — the room locks and chooses (normative).** A community must never sit without a moderator, and no node holds a key that could appoint one. So a community with no duty holder left **locks**: read-only to everyone, since nobody can moderate. Members may read, and nobody may post, admit or act until a moderator is seated. It then **elects**, in a vote of **24 hours**. The **ballot is the roster**, every member a candidate, shown in the order of [CC 4.5.4](#4.5.4) rule 2. That order is presentation only and decides nothing. Each person ranks **up to three**. There is **one ballot per person** however many keys they hold, folded exactly as a vote is (one vote per person, below). A person's agreeing ballots are one ballot. Disagreeing ballots neither withdrawn are no ballot until a withdrawal leaves one, and no instant decides. The count is **instant runoff**, the weakest standing candidate eliminated in turn, until one remains. A tie seats nobody, and the count runs again over the ballots then held. The floor of two voices applies. **The winner accepts by their own row**, as a member accepts an invitation ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). A winner who declines, or is silent past a grace the room's policy names, passes the duty to the next in runoff order, and so on. Nobody holds a duty they never signed for. **The voters' ballots are the appointment's signatures**: the seated moderator is appointed by the body under its protocol, with no node signing anything. A room where nobody votes stays locked and the ballot stays open.

**One result on every node (normative).** Nothing signed opens an election, since a lapse by inactivity has no row. So the election is **named by what every node holds**. Its id is the digest of the community id and of the last seating row or, for a room never yet seated, the genesis of the roster. A member leaving while the room is locked therefore changes nothing about the election (a resignation is the member's own act and a lock traps nobody; nothing is admitted or removed). A ballot names that id, and every ballot under it belongs to one election. The electorate is the roster the election names, a ballot from a member that roster does not seat counting for nothing. There is no reopening as a separate thing: the ballot stays open until a seating lands. A node's clock closes nothing: **the winner's acceptance row binds the ballot set it was seated on**, carrying the election id and the digest of the set of ballots it was counted over. The set covers the ballot and withdrawal rows held, so the count over it is reproducible. An acceptance waits until the node holds that set. It is not counted unless the count over exactly that set yields the signer, the set meets the floor, and the node's own 24 h since it first held the lock have passed. **The seat is a function of the rows held and never of their arrival**. Among the valid acceptances a node holds, the one counted over the larger set stands, a larger set being a count. Two acceptances over different sets of equal size are a tie, and neither seats anyone. The tie ends when the node holds an acceptance counted over the union of the two sets. A node stores every ballot and acceptance it receives rather than refusing a late one. A ballot is void only against the seating that wins. So a node never unseats on arrival order alone, and every node holding the same rows seats the same moderator. Two nodes that hold different rows, as halves of a fleet do across an edition in which one half admits a removal the other refuses, may seat differently until their rows converge. That is a residual of the mixed fleet, not of the rule.

**The floor in a small room** is the smaller of two voices and the roster's size, so a room of one elects itself by its own ballot and no room is locked beyond its members' reach. The policy table's row is `moderator_election`, with the ranked-choice model of the register's row. The ballot and the acceptance are the rows of [CC 3.1.4](part_3_the_namespace.md#3.1.4), `ballot:moderator:v1` and `ballot:moderator_acceptance:v1`.

**Ranked choice is one count, and any choice among options may use it (normative).** A ballot ranks up to a declared number of the options, best first. Where the choice declares no number, it is three. The count is instant runoff. While no option holds more than half of the ballots still counting, the weakest standing option is eliminated, and its ballots pass to their next standing choice. A ballot with no standing choice left stops counting. A tie for weakest goes against the option later in the choice's declared order. An election declares no order, so a tie there seats nobody and the count runs again. One ballot counts for each person, and a person whose ballots disagree has none. The floor of two voices applies.

A node keeps a tally of how many ballots carry each ranking, and finishes the count from that tally alone. The tally is a sum, so it is the same in whatever order the ballots arrived, and two tallies of separate parts add to the tally of the whole. A secret poll ([CC 6.1.9](part_6_the_coherence_mathematics.md#6.1.9)) carries one cell for each ranking, and its composite is that same tally. The count ends in fewer rounds than there are options, and it uses whole numbers only.

**A poll states its own rule (normative).** A poll states its rule of count in the row that opens it. Where it states none, the poll carries by a strict majority of those who voted, and the floor is two voices. Those who vote are members of the roster the opening row names, and one ballot counts for each person. A secret poll keeps its own floor on the ballots counted ([CC 6.1.9](part_6_the_coherence_mathematics.md#6.1.9)). (The policy table's row `poll`.)

**Optional moderator quorum (community config).** Unilateral moderator action is the *default*. A community **MAY** instead require a **moderator quorum** for an action to carry. The quorum is either **full** (every named moderator must sign) or **live-within-window** (a live-quorum of the moderators who respond within a stated period — the reverse-quorum applied to the moderator set itself). This rides the community's existing `consensus_protocol` ([CC 4.4.3.2](part_4_composition_governance.md)) applied to the `moderate` duty. It **tightens the fast path** without weakening the community-vote fallback, which still carries on total moderator absence. The choice is the community's to make and to change (the community vote may set it).

**Protective default — a report raised in the room defaults to removal.** For a takedown / harm report raised in the room, the window's **default outcome is removal**. Content stays in plain view **only** by an affirmative, on-record **keep-decision**: either **(A)** a moderator's unilateral *approve-to-keep* signature, **or** **(B)** a live-majority *vote-to-keep*. **Passive survival is impossible** — doing nothing within the window removes the content. A vote that goes against the item hides it behind the consent gate below and deletes nothing. Therefore **surviving reported content is always attributable**: the moderator who approved it, or the majority who voted to keep it, are cryptographically on record. *A community in which reported content survives has self-identified* — by name, by signature.

A harm report is not a change proposal. Its window's default is removal; the act that must land is the keep, and the floor applies to the keep — a moderator's named approve-to-keep, or a vote-to-keep that carries its majority. A takedown notice under a legal basis ([CC 4.5.3](#4.5.3)) is a third thing: duty-holder-signed, executed without a window.

**Infohazard consent gate — no passive exposure.** When the members' vote goes against a reported item, the item is **auto-hidden behind an active interstitial**, and that vote never deletes it. A deletion cannot be taken back, and the members' lift above exists to take decisions back. The interstitial reads *"I consent to view this material reported as a potential infohazard."* Clicking it **publishes the viewer's own signed row naming the item**, a claim that binds nobody but the viewer ([CC 3.4.5.1](part_3_the_namespace.md)). It is no `consent:state:*` row, which only a subject of the target signs ([CC 3.4.5](part_3_the_namespace.md)). So **passive exposure is impossible here too**: every viewing is an affirmative, signed act by a named identity. This **rides the viewer's own claim + a [CC 3.3.12](part_3_the_namespace.md) `content_class:{class}` flag** (`content_class:infohazard` / `content_class:reported`). There is **no new wire shape**: it is the [CC 4.5.5](part_4_composition_governance.md) `content_class` gate composed with the [CC 3.3.1](part_3_the_namespace.md) consent primitive.

**The outcome ladder — every transition an attributable act.** A graduated, fully-attributable ladder; nobody passively flags, keeps, or views harmful content:

| Outcome | Trigger | Who is cryptographically on record |
|---|---|---|
| **Hard-removal** | CSAM perceptual-hash tripwire ([CC 4.5.3](part_4_composition_governance.md) `PerceptualHashCsam`) / takedown / **report undefended** (no keep-decision and no vote carried in the window) | the removal action ([CC 4.5.5](part_4_composition_governance.md) `takedown_notice`); for a report undefended no notice is signed, and each node reads the removal from the closed window; content does not survive |
| **Consent-gated** (retained, auto-hidden) | a members' **vote against the item**, which hides it and never deletes it; a moderator's **withhold**; an item **restored by the members' lift** | **each viewer** — every interstitial click publishes the viewer's own signed row |
| **Kept-visible** | a moderator's **approve-to-keep** (A) **or** live-majority **vote-to-keep** (B) | **the moderator** who approved, or **the majority** who voted to keep |

**Single-point warning + inactive forfeiture.** A community with **only one duty holder MUST be warned to seat a second**. A lone authority is a single point of capture and of failure. **Inactive duty holders lose their standing:** silence past the community's freshness window **lapses the duty**. Where that leaves a duty holder, the remaining holders confer the vacant seat. Where it leaves none, the moderator election above **reconstitutes authority**: the room locks and its members elect. **No community is ever hostage to an absent duty holder.**

**What the protocol guarantees — structure, not behavior (the M-1 framing).** The protocol guarantees the **structure**: **default-remove, attributable-keep, attributable-view**. It does **not** guarantee the *behavior* of a community that **affirmatively chooses harm** — a moderator may sign to keep abuse, a majority may vote to keep it, and a viewer may consent to view it. What the protocol forecloses is doing any of these **silently**: every transition up the ladder — flag, keep, view — is an **affirmative, attributable act by a named identity**. Per [CC 4.2](part_4_composition_governance.md) M-1, the federation's promise here is **revocability and accountability**, not behavioral control. A community that harbors harm is on the record as having done so, and that record is what justice composes over.

**A duty-view is an act of the duty, never a keep or a view (normative).** The attributable-view ladder above is about a viewer who *chooses* to see kept content. It is not about adjudication. Two parties are recorded as having performed **an act of the duty**, and not as a keep or a view on the ladder. One is a `moderate` / `takedown` / `review` duty-holder who examines reported or suspected infohazard material in order to act on it. The other is anyone who saw material before it was known to be an infohazard and then reported it. The record is a `moderation:*` row naming the duty, the purpose, the report or removal that followed, and the exposure. Best practice is built in, in this order:

- **minimise** (a known match on the perceptual-hash tripwire is removed and reported with no human eyes on it, ever; classifiers triage before a person is asked to look);
- **restrict** (a person looks only under a named duty, for a named purpose, with the viewer protections the operator provides — blurring, thumbnails, time limits, wellness rotation);
- **record** (the look is signed as duty, with its purpose and what followed, so the record supports the viewer rather than indicting them, and the mandated report rests on it);
- **report** (an inadvertent exposure is reported promptly through the same channel, which is what good-faith protection, where the law offers it, turns on).

Where the duty-holder acts for an organisation, the organisation is on the bond ([CC 3.2](part_3_the_namespace.md)) and the duty-holder is its agent for the purposes of any provider protection the law offers. A keep or a view that is not an act of a duty stays on the ladder, attributable and named.

**Consistency — member-reporting, not substrate scanning.** This is **member-reporting + reverse-quorum adjudication**, *not* substrate scanning of private content. CEG **refuses client-side scanning** ([CC 4.5.7](part_4_composition_governance.md)): a group's watchlist runs only at that group's publish/share seam and the hash tripwire only at the public seam ([CC 1.13.3.4](part_1_foundation.md#1.13.3.4)), never over [CC 5.2](part_5_transport_substrate.md) self/family private content. The principle is unchanged across the federation — **anonymity to outsiders, accountability to insiders** — applied here with teeth on harm: the structure makes silent survival, silent keeping, and silent viewing impossible, while leaving private content unscanned.

**The symmetry with the accord (explicit).** This is [CC 4.2.6](part_4_composition_governance.md) read at community scope, and the two halves correspond. In the accord, a **lone survivor fires** and the roster is changed by a **majority of the standing roster**, cast within a window. In moderation, a **lone duty holder acts** and, when duty holders vanish, the **live community reconstitutes governance**. Fire-floor-of-1 ↔ one duty holder's signature; a participation window with a named count set ↔ the same window with the present members as its count set; Enoch-Arden return ↔ a new election on a lapsed duty holder's silence. A majority's resumption of a halt ↔ the members' lift of a moderator's act. **Presence is authority, absence forfeits it, a timer decides** — at every scope; what differs by scope is only the set a count is taken over, which the policy table names.

**1+4 preserved.** The proposal/window/tally rides the generalized [CC 4.2.6](part_4_composition_governance.md) participation shape + the [CC 4.5.5](part_4_composition_governance.md) action primitives (`moderation:*` / `takedown_notice` / `reconsideration:*`). The consent gate rides the viewer's own claim ([CC 3.4.5.1](part_3_the_namespace.md)) + the [CC 3.3.12](part_3_the_namespace.md) `content_class` flag. **No new structural primitive.**

**The policy as data (normative).** Every door that opens a window runs one decision shape, and the shape is five numbers over a named standing set, published as a table rather than described door by door. The five numbers are these.

| Number | What it is | Count, bound and default |
|---|---|---|
| **enact** | the approvals that land the change at once | a fraction of the base, strictly more; never below a strict majority; the default two-thirds |
| **cancel** | the objections that void it at the window | at least the fraction; the default one-third |
| **floor** | the approvals the change must carry before silence may land it at the window | at least the fraction; the default one-third; never fewer than two voices in a community (the floor of two voices, below) |
| **window** | by the sensitivity of the change | 86 400 s for reversible content, 259 200 s for roster and standing, 604 800 s for the irreversible |
| **irreversible** | no instant landing | the change waits its whole window even at full approval |

**The floor of two voices.** In a community the floor is never fewer than two voices, so one voice never decides who is in a room, whatever the size. Where admission is by invitation no single vote admits, and the second voice on an admission is the invitee's own acceptance ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)). So a room of one grows by its one member's proposal and the newcomer's yes, which are two keys and two consents. Where admission is open — `open:self_admit`, anyone signs their own admission — no single vote excludes, and the guarantee attaches to removal instead. `founder_only` is a protocol for a family, a publication's subscriber list and a room's own listing. A community above the family that names it is refused `federation_community_consensus_protocol_violation`, as an infrastructure community already is. An affiliation names it only under the one-voice countersign rule of [CC 4.4.3.2.8](#4.4.3.2.8). `federation_community_consensus_protocol_violation` is the refusal token, whose emitted record is the `hard_case:community_consensus_protocol_violation` row of [CC 4.4.3.2.3](#4.4.3.2.3).

**The floor waits its window.** The floor is a reverse-path predicate only: nothing lands before the window closes except at enact, so a floored change still waits its time.

**The base.** The expected-active count is the community's own member-only census composite ([CC 6.1.9](part_6_the_coherence_mathematics.md#6.1.9)), which falls at most a tenth per period and never below its floor. The base is the standing roster at or below the size `k` the governance policy table's base law pins and, above it, the expected-active count — never below a stated minimum. A fraction therefore stays reachable at ten thousand members as at ten (the law's constants are provisional until measured). The members' vote on a moderation action does not read this base: it counts those who voted, with the floor of two voices (the mechanism above).

**The corridor.** A community may set its policy stricter than the defaults, up to a floor at enact, which is the reverse path switched off. It may not set it laxer than the corridor allows. A cancel or floor one voice can reach, an enact one voice can reach, a window under its class, or cancel or floor above enact, are refused as policy (the policy-corridor model; the register's row CLM-policy-corridor).

**The governance policy table is published as data with its decision function, its base law, its pin and its vectors** (the register's row CLM-governance-policy-table). The decision function is `(policy, base, approvals, objections, elapsed) → lands | pending | cancelled`, which an implementation replays rather than re-reading this paragraph. Every two-path row is also an instance of the two-path model, which the build regenerates and checks, so a row that breaks the machine's invariants fails the build. The rows are these, generated into this section from the table:

| Row | Who is counted | Enact | Cancel | Floor | Window | At the window |
|---|---|---|---|---|---|---|
| `default_content` | `member`, one voice a person, instant not stated | 2/3 | 1/3 | 1/3 | 86 400 s | cancelled |
| `default_standing` | `member`, one voice a person, instant not stated | 2/3 | 1/3 | 1/3 | 259 200 s | cancelled |
| `default_irreversible` | `member`, one voice a person, instant not stated | 2/3 | 1/3 | 1/3 | 604 800 s | cancelled |
| `community_invite` | `member`, one voice a person, instant not stated | 2/3 | 1/3 | 1/3 | 259 200 s | cancelled |
| `community_remove` | `member`, one voice a person, the set as signed | protocol | — | — | 259 200 s | cancelled |
| `self_roster_add` | `self`, one voice a key, the set the proposal names | 1/2 | more than 1/2 of the others (strict majority) | 1/N | 86 400 s | stay_open |
| `self_roster_evict` | `self`, one voice a key, the set the proposal names, the target silent | 1/2 | more than 1/2 of the others (strict majority) | 1/N | 86 400 s | stay_open |
| `moderation_action` | `member`, one voice a person, the set the proposal names | role:moderate at 1 | — | more than 1/2 of those who voted, at least 2 voices | 172 800 s | tallied |
| `moderation_overturn` | `member`, one voice a person, the set at the act | more than 1/2 | — | 2 voices | 172 800 s | lapsed |
| `moderator_recall` | `member`, one voice a person, the set as signed | 2/3 | — | 2 voices | 259 200 s | cancelled |
| `accord_halt` | `holder`, one voice a person, instant not stated | 1/N fires | 1/2 confirms | — | 86 400 s | lapsed |
| `custodian_replace` | `operator+wa`, voice not stated, instant not stated | 2/2 | — | — | none | — |
| `affiliation_member_action` | `deciding+outside`, voice not stated, instant not stated | 2/2 | — | — | none | — |
| `moderator_election` | `member`, one voice a person, the set the proposal names | instant runoff over ranked choice of three | — | 2 voices | 86 400 s | stay_open |
| `cosigned_act` | `protocol`, voice not stated, the set as signed | protocol | — | — | 259 200 s | cancelled |
| `accord_majority` | `holder`, one voice a person, instant not stated | more than 1/2 | — | — | none | — |
| `poll` | `member`, one voice a person, the set the proposal names | — | — | more than 1/2 of those who voted, at least 2 voices | none | tallied |
| `wa_adjudication` | `wa`, one voice a person, the set the proposal names | protocol | — | — | 259 200 s | cancelled |

Each row is stated where its act is. Invitation and removal are at [CC 3.1.3.2](part_3_the_namespace.md), the self roster at [CC 3.3.6.3](part_3_the_namespace.md) and the halt at [CC 4.2.1.1](#4.2.1.1). The custodian's replacement is at [CC 7.5.5](part_7_lifecycle_stewardship.md), a group's cosigned act at [CC 3.3.4](part_3_the_namespace.md), the accord's majority at [CC 4.2.1.3](#4.2.1.3) and an adjudication's count at [CC 4.3](#4.3). The other rows are stated in this section.

**How a family's act is counted.** Each family's row in the family model names the policy row its act runs and the roster that row is read against. A family whose rows one signature carries counts nothing. Where the count differs by stage or by the kind of identity, the family lists its cases in order and the first that holds decides.

Votes travel on `objection:{state}` ([CC 3.1.9.2](part_3_the_namespace.md)): `proposal`, `assent`, `raised`. Two further fields are on every row:

- `cancel_over`, the denominator of the cancel fraction — the base for a community, the proposer counted; the *other* keys for a self roster, since the proposer is not asked to object to itself;
- `at_window`, what becomes of a proposal that has not landed when its window closes — `cancelled` for every community row, so a held change always resolves; `stay_open` for the self roster, cleared by the proposer's withdrawal or the target's act; the halt lapses; a moderation proposal is tallied.

**Who a row counts.** Each row also states who it counts, as typed cells. They are the roles whose seated keys make the set, whether a voice is a person or a key, and the instant the set is taken at. They also name the rows the voices travel on and whether the target must be silent. A cell this document does not state reads `unstated` in the table, and the build counts those cells so their number only falls. A row that removes from the set it counts fixes that set before the act, so the counted never choose who counts.

**The clock of a window (normative).** Every window of this table is measured by each node from the instant it first held the proposal, never from a signed instant of the proposer or of a cosigner. The self roster ([CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3)) and the halt's fuse ([CC 4.2.1.1](#4.2.1.1)) already read it so. The reason is that a signed instant is the signer's to choose, and a window read on it could be shortened in advance or entered after it closed. Receipt is the one clock no signer sets. `cosigned_at` stays beside the bytes and decides nothing. Two nodes may therefore close a window at different moments, and nothing lands early at either.

**A row that a clock or a fold causes has one emitter (normative).** When a window closes, a deadline passes or a fold changes, a record of it is emitted by one node: the door at which the row that caused it first entered. That node keys the record's id on that row. Every other node re-derives the verdict from the rows it holds and emits nothing. The record marks the event and is never its cause, so a node that holds the same rows reaches the same verdict whether or not the record arrives. [CC 3.2](part_3_the_namespace.md) states this for a stalled root, and it holds for every such row.

**The state processor (normative).** The queue, the preview and the door are one function run three ways, and a node holds one.

**The processor's state.** Its state is the set of rows the node holds, each with the instant this node first held it, and nothing else. The first-held instant is the node's own receipt, outside the signed row and never replicated. It is what every window of this section's table runs from (the window clock above). A window another section defines runs from the instant that section names ([CC 2.6.7](part_2_the_grammar.md#2.6.7), [CC 3.2](part_3_the_namespace.md#3.2) T4a). An object's state, a person's standing toward it and a room's seated roles are folds over that set, never stored verdicts. So a node has no second copy of anything to drift.

**The processor's step.** Its step takes the held set, one row and the instant. The step answers that the row's transition is enabled for the signer's standing on the object's view, or is refused by name. An admitted row is appended and nothing is rewritten, and the view after is the fold over the larger set. The instant is the one input from outside, for windows; the processor keeps no clock.

**The fold.** A family states how its rows, read as a set, give a value. It names the rows that enter, the members they are grouped on, and which rows of a group stand. It also names how a member may move across versions, what a retraction removes, and how values combine. It says what a reader gets when no row stands, and whether the door, the node or a reader runs it. A family that states none reads by the default. By default the latest of a signer's own live rows stands, a retraction removes the row it names from that instant forward, and no row is no state.

**The guard.** A transition may carry a guard: what the node must hold, find live or find signed before it admits the row. A guard is a list of clauses, each a query over the rows held and joined to the row at the door. Each clause names its outcome when it fails: the row is refused by a named token, a key is left out, or the clause only advises. The guard runs inside the step, after the signer's standing is folded and before the row is appended. A required row the node does not yet hold is no failure of the guard: the arriving row is held or refused as its family's replication rule states.

**The change.** A transition that replaces, withdraws or removes may carry what its row is allowed to do. That is who signs the changing row, how it names the row it changes, and which members may move and in which direction. It also states which rows are displaced, what follows for the rows that depended on the old one, and what follows for keys. A transition that states none takes the default. By default the same attester replaces their own earlier row, and a withdrawal leaves standing the rows that cite the withdrawn one.

**Reactions and clocks.** What follows from a row in time is stated as data, in a table of its own. It holds when a row of a family expires, the named windows that run from a row, and what a node reads, does or emits when a row lands, a clock closes or a fold changes. A duration in it is a name and never a number. An emitted row enters by the door like any other row. Every other effect is a verdict that a node recomputes from the rows it holds and the instant.

**One function run three ways.** Run over the transitions enabled for one person it is the queue. Run over a row before it is signed it is the preview, which is exact because the same function is the door. Run over a row that arrives it is the door.

**A policy that is not one voice.** Some transitions run under a policy that is not one voice: the two-path, a cosigned act, the ranked election, the mirror of a moderator's act. Such a transition is admitted as a row at once and moves the object only when the fold over the rows meets the policy's numbers. So the preview of such a row says what the fold says: the object's state, unchanged, and what is still missing, the voices or the instant.

**What a preview claims.** The impact an item shows ([`manifests/choice_item.cddl`](../manifests/choice_item.cddl)) is the difference between the fold before and the fold after, with the family's columns for undo, never a stored field. What a preview claims is exact over the rows the node holds. Its counts and standings are the same on every node that holds those rows, since those folds are integer arithmetic over signed inputs. Its window answers are this node's, since a window runs from this node's receipt, which is why the clock gates admission and never the count. It says nothing about rows the node does not hold.

What the processor does not model, so that it stays small:

- signatures, since a row in the held set is already verified;
- transport;
- what other nodes hold;
- projections;
- text;
- and any reader's weighting of what it reads, which is composition and never admission.

**The choice as data (normative).** Every decision a person is asked to make, a first-run step, a consent gate, a deferral, a vote in a room, a moderation action, is one object, and its context says which: `manifests/choice_item.cddl`. An item carries:

- a **context** (the circle, the role, the atoms in force, a title and body);
- **facts** that are displayed and never chosen, each with its provenance (`wire`, `by_rule`, `not_sent`);
- a **policy**, which is a row of the governance policy table above (a first-run or consent item runs the self row, one voice of one, no window; a room's item runs the room's row);
- and **options**, each with a benefit and a downside that are never empty ([CC 5.4.3](part_5_transport_substrate.md#5.4.3), the choice is explained before it is made), the rows it would sign (`writes`: family, verb, scope), and an **impact** that is not written by hand but **derived from the family model** for those rows.

The impact says what moves, where it goes (the family's audience and tier), whether it widens or narrows, and whether it can be undone (the family's erasure route and lifecycle). So the four facts a confirmation shows are a lookup and never copy. Four kinds and no more: `choice` (two or more options), `act` (one option, a thing done), `entry` (a value typed or arriving by a ceremony, never an option), `notice` (no options: a fact, a state, a refusal).

**Consent is not a kind.** A consent is a choice whose writes are consent rows. Announcing is a choice whose write is the binding at federation scope. An anonymous identity is a choice whose write is the identity itself. Shaping is a choice whose write is a setting. Each is presented the same way, each changes something, and none is more or less a choice than another. So a first run has no separate class of consents, and nothing in it is `required` except what has to exist for the node to run.

**Choices belong to the person.** The node keeps one queue of the items awaiting the person's signature, the pending decisions of this section among them. The person signs, the row lands, the change follows, and the result can be viewed. An agent signs no item of a person's queue: the person's choices are the person's. An agent signs its own rows, its tasks, its traces, its receipts, under its own key and its steward-binding ([CC 3.2](part_3_the_namespace.md)). A person MAY delegate goals or roles to it, that delegation being itself a row the person signs. The purpose of a node and its client is twofold. It lets the person see the current state of the attestations they trust, through the policies they already hold ([CC 4.4.3.8](#4.4.3.8)). It puts before them, as one queue, what waits on their hand.

**Keeping an answer alive is not a new choice, and widening it is.** A node holding the person's pen MAY re-sign a row the person already chose, to refresh it or supersede the one before, only as the same row. The same row is the same scope, the same prefixes, the same peer, or a peer that follows the person's own later act (a root they accepted after the item said the grant goes to the roots they trust). The node never re-signs a wider row, which is a new choice and needs an item. It never re-signs after the person withdrew the row, since a withdrawal stands until the person answers again.

**One vote per person.** A vote counts once per person, whatever the number of their devices. A roster seats a key ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)), the person is the fedID whose self roster the key belongs to ([CC 3.3.6.3](part_3_the_namespace.md#3.3.6.3)), and a tally counts fedIDs. Every vote row is admitted and kept. The count is a fold over the rows held, permutation-invariant and clock-free as every instrument of [CC 6.1](part_6_the_coherence_mathematics.md) is. A person's live vote rows on one proposal that agree count as one voice. Rows that disagree, neither withdrawn, count as no voice, since a person at odds with themself has not spoken, until a withdrawal ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1) rule 1, the author's own, which any key of the same fedID signs) leaves one standing. Nothing is refused at the door for arriving second, no instant orders two devices' rows, and every node holding the same rows reaches the same count. In a private room ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)) the roster seats voices, and the person of a room key is the one its binding names. A tally of persons there is missing at a node until that node holds the bindings, and the author's own withdrawal is signed under any room key of the same voice.

**The answer.** An **answer** records the state (`served`, `held`, `signed`, `deferred`, `changed`), the value, the digest of the item as it was shown, and the rows once they exist. Declining is a complete answer and never a failed vote.

**What starts unanswered, and what starts on.** A choice whose answer sends the person's content or their agent's traces beyond their own circle starts unanswered and is never preselected: sending traces, and any grant of content to a peer. **Announcing starts on,** its cost on screen. For nearly everyone being reachable is the right and the easy answer. The reason is that an announced identity is shared as a short `ciris://` name rather than a node code handed by hand, and takes part in public groups. It can join the geographic communities near it where the person also chooses to share a rough location. What announcing sends is the binding and its delegations to the roots the person trusts, never content. Content keeps the smallest cohort scope by default ([CC 1.13.3.4](part_1_foundation.md#1.13.3.4)). The two costs of announcing when declined are those of [CC 5.4.6](part_5_transport_substrate.md#5.4.6). A default is otherwise admissible only for a choice that narrows or keeps things as they are, and every default's cost is on screen. **Relay offering is the stated exception:** it carries other people's sealed rows and discloses the node's route to a referred stranger, nothing of the person's content or identity. It is on by default for servers and home nodes under the device policy of [CC 5.4.6](part_5_transport_substrate.md#5.4.6), because the mesh does not seat its peers otherwise. It is a choice like the others, its cost on screen, and it may be turned off. An unanswered choice that the node does not need in order to run never blocks the person. It is `deferred`, nothing leaves on its account, since nothing leaves without a signed row, and it waits in the queue until answered.

**One step, or a confirmation.** An option that cannot be undone is never a default. An item is confirmed before it is signed when the rows it would sign widen or have no way back. Every other item takes one step, so withdrawing, leaving and taking back are one step each.

**Nothing is answered on anyone's behalf.** An item whose writes leave the node (a grant, a binding, a consent), if answered before the node is claimed, is held and not applied, since no owner key exists to sign it. Such an item lapses if the claim never comes. An item that writes nothing outward (a setting of the node itself, shaping among them) applies at once, because applying it leaks nothing and waiting would, and the owner's signed row supersedes the local record after the claim. A client renders an item with no node, from the data alone.

**The epistemic web client (normative).** A client of this document renders two served shapes and nothing else: the **view** (`manifests/view.cddl`) and the **queue**. The view is one object's rows and the atoms the node folded from them through the person's own policies. Each atom carries its provenance, the rows it read and the rule it ran, so that what is true now is always shown beside why. The queue is the items of the choice as data, above. The record and the state are one thing seen twice: the record is the rows, the state is the node's fold of them, and the outcome of every choice is a row appearing in a view.

**Every string the client shows is served by the node as a text reference,** an id with parameters resolved for the locale the client asked for. The client holds no copy of its own. A string the node cannot localize is served in its source language and marked so, never invented. **The way there is the same contract:** while a node's bundle lacks a locale it serves the reference with its text in the source language and the language marked. Meanwhile a consumer MAY resolve that id from a bundle it still holds, preferring the node's text whenever the node serves it in the requested locale. The ids are one namespace shared by every consumer, so the strings a consumer still holds and the ids a node serves can be compared. What one has and the other lacks is the measured distance between the surfaces built by hand and the surfaces rendered from the view and the queue, closed one card at a time.

**The client holds the keys of its deployment and no policy:** the person's own user key and the node's key, and the agent's key where an agent runs. These are two or three hybrid key sets by deployment, each signing only its own rows ([CC 3.2](part_3_the_namespace.md)). A view is read through the person's trust set ([CC 4.4.3.8](#4.4.3.8)) and the client decides nothing the node did not.

**How the view makes the queue (normative).** The queue is the door run forwards. For an object the person can see, the node holds the object's family, its lifecycle state, and the person's standing toward it. The standing is the roles the held rows give them: author, subject, member, moderator, founder, steward, holder, witness. A family's lifecycle is the transitions of its row in the family model. Each transition is a verb with the state it leaves and reaches, the roles that may sign it, its governance row and whether it widens. The queue is exactly the transitions enabled for this person in this state, one item each, and an item's writes are the row that transition signs. The admission door is the same predicate, so the queue never offers what the door would refuse and the door never admits what the queue would not have offered. A stranger to an object sees no item on it. An item that moved the object's state is gone from the next view. An item that widens or has no way back is confirmed before it is signed, and every other item takes one step. A node derives the queue from the same held rows and the same policy it admits by, never from a separate list.

**An item never crosses between nodes:** a node builds it for its own client from the rows it holds, the policy table and the family model, and only the rows an answer signs travel. A person's other devices learn the answer by the row. So each node keeps its own queue, an item clears when its row arrives, and no queue is synchronised. The queue never blocks: the transport carries signed rows and cosignatures and reports that a decision row landed, and the host decides from the rows which items present themselves.
