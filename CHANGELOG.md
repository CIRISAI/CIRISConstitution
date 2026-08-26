# Changelog

All notable changes to the CIRIS Constitution. CC is one document with one version line;
each cut is validated against its sources under the skeptical rubric before it lands.

## 1.0-rc4 — in progress

**CC 3.4.7.3 — the actor/substrate separation (#95, ruled).** CC enforced one direction of the
node/agency split and was silent on its converse: a node-only key may not *receive* agency, but
nothing stopped an actor key from *being* the infrastructure — and the live agent topology fused
both onto one key, so `owner_of()` resolved a person to an actor where a node was asked for. Worse,
the escape was legal: CC 4.4.3.4.3's conformance rule fired only on `node`-**only** recipients, so
adding `agent` to a node's role-set repealed the invariant — **the loophole was spelled as a
simplification**. Ruled in six clauses: `node` is exclusive of `agent`/`user` (A); the gate reads
**set membership**, never purity (B) — both required, since A stops a fused key being minted and B
protects against the ones that already exist; the actor↔node relation is **entailed, never
asserted** (C) — neither party has standing, so the pairing derives from two human-signed edges and
cannot be forged by either side; the common-human predicate `∃h. h=owner_of(node) ∧ h ∈
stewards_of(agent)` (D), existential because node ownership is single-valued while stewardship is
multi-parent, fail-closed on unresolvable; the enforcement seam is the **node's** (E), because
infrastructure holding no agency is exactly what can be trusted to refuse it — an actor gating
itself is the constrained party checking its own constraint; and fused keys are **non-conformant,
not deprecated** (F), forward-only so history stands, and still refused agency meanwhile.
Amended in the same cut (CIRISPersist v38.6.0, ffa6608): `stewards_of` is the **custody** set, never the conferral set — for a key that can accept for itself the delegation half counts only where the envelope declares custody (#87), so an unmarked delegation is a job and MUST NOT satisfy Clause D; and the cardinality is the occurrence half plus **one** custody claim, a second distinct claim being refused at bind time. That withdraws this section's first, too-broad statement that co-stewardship expresses multi-tenant hosting: only two shapes are admissible, and the deferred space is most of multi-tenancy rather than an exotic corner. Also repaired: the
"infrastructure must not have agency" rule was cited **four times** at CC 1.13.5 — the
operational-language gate, which says nothing about agency, and which a substrate implementation
had already inherited into its own doc comments. 3.4.7.3 is now that rule's numbered home and all
four citations repoint to it. `CLM-actor-substrate` / `CLM-common-human` staged.

**CC 1.13.6 — the durable trace anchors on the act, not the deliberation (normative).** An assurance
finding the substrate passed *by behaving as designed*: an aged `THOUGHT_START` with no
`ACTION_RESULT` is purged, and nothing in the compliance surface said that was deliberate. The
defect was documentation, so the repair is a stated position. Traces anchor on the terminal
`ACTION_RESULT` — no action, no trace — because accountability attaches to acts, and because
retained deliberation would be a permanent archive of unexecuted thought carrying the
conversation's humans at their most exposed while carrying no accountability weight (CC 1.9 requires
an agent free to consider and reject). The safety argument is reduced to one attackable invariant:
*absence of an `ACTION_RESULT` asserts no external effect occurred* — so the sweep can only ever
discard deliberation that produced nothing, and any counterexample is a defect in the emission path,
never in the purge. Stated as a **named wager** (#84 discipline) with its falsification condition and
its dye test — a totality test over effect-producing paths, explicitly *not* a retention test on
thoughts — filed at #93, plus a rate-observability requirement on the purge and an honest residual
on interrupted-path forensics. `CLM-trace-anchor` staged.

**CC 3.3.10.1 — in-grammar ledgers: owner-serialized content, cohort-witnessed conservation (#92).**
The ballot machinery extended to value, on a three-track prior-art sweep (theory, channels/mints,
mutual-credit practice). Total order lives in the owner's hash chain, never the grammar (CC 3.2
single-owner ⇒ consensus number 1, Guerraoui PODC 2019 — which also corrects the stance's dated
"no totally-ordered ledger" premise; the real exclusions are named in-text). Nine normative
clauses: identity/unit binding, dense hash-chained entries, delegate serialization, witness-anchored
heads with the cadence stated as the equivocation-exposure window (SUNDR's 2004 "time stamp box";
CT's failed voluntary gossip is why the anchor is an obligation), checkpoints riding §19.7 descent
(the regulator-endorsed summarize-and-delete shape), promotion-with-proof, the deterministic
byte-equal conservation fold (Sardex's zero-sum invariant; PeerReview's transferable evidence),
fork-as-adjudicated-slashing with mandatory restore-then-resync (the eltoo critique answered —
available because the witness set is cooperative), and the non-claims (no atomicity, no
member-vs-member privacy, no cross-cohort conservation — netting + net rail settlement, the
CLS ~96% pattern). 1+4 lockdown holds: rides scores + subject_kind + evidence_refs + supersedes +
cohort_scope. Staged claim rows on #92 / CIRISPersist#754. The attempted-systems record lands
verified: Holochain's 8-year gestation vs NetzBon-on-Taler's two; SSB/Hypercore fork-death
answered by L8's mandatory resync and L3's Keybase-shaped in-chain delegation; Sardex's
load-bearing brokers hooked to the named-moderator invariant; Circles' rail-boundary death
shaping the netting guidance. Closed with the kernel note: each application is the club-bounded
sibling of its famous problem, the novelty budget spent once on the deployed two-plane kernel.
CC 5.4.6 Position additionally adopts the lightnet/darknet name the transport implementation
already carries, closing edge's dangling citation. *Lightnet settles; darknet transacts.*

**CC 5.4.6 — a directed announce inherits the prohibition (#91, ruled).** The first RC4 revision.
The clause binds the emission, not the addressing mode: on Reticulum transport no directed announce
satisfies the purposive sentence — multi-hop path learning *is* outsider observation (path state a
subpoena reaches), and the epoch-bound derivation forces either a roster-wide re-announce wave on
every Add/Remove or a removed member keeping every peer's addressing indefinitely. The flat MUST NOT
was never broadcast-era shorthand — the same section bans the targeted, non-broadcast per-destination
query in the same breath. The trade on offer was a structural, claimable guarantee for a
traffic-analysis-statistical one — a claim base CEG/RET declines to make (CC 1.13.3.1; the goal
stands, the Anonymous Tier is its opt-in). The leak reading's sound insight is kept in-text:
in-group MLS distribution of addressing material was never prohibited. Multi-hop scoped reach is an
amendment-plane design question with its bar stated in-clause.

## 1.0-rc3 — the external-review remediation, the trust-root ratifications, and an honest matrix

RC3 closes the open issue set. Where an issue asked for a ruling, this cut gives one; where an
issue was wrong, the disposition says so. Provenance, review archaeology and superseded text live
in the GitHub issues and on Zenodo — not in this document.

**Part VI — the math corrections (#50, #45, #26, #34, #35, #6).** §6.2 is demoted from
justification to **capacity analysis under chosen constraints**: the collapse geometry cuts honest
and deceptive regions alike, so the asymmetry lives in the choice of constraints, not in a
theorem's gift. The reviewer's contradiction is real and is fixed at the root — J = k_eff·λ_op·σ is
a *throughput index* monotone in diversity, maximised at ρ̄ = 0, and it **MUST NOT** be cited as the
corridor's basis. **No operating corridor is stated at all**: the campaign's own k ≥ 4 positive floor means the
poles-are-zero basis does not hold in the regime CC needs, so §6.2 declines to re-found a corridor,
voids any band appearing in a derived document, and an implementation MUST NOT gate on one. The σ recurrence was a conformance
bug — not step-invariant for interior signals, yet carrying a MUST that implementations agree at
Δt ∈ {1, 25, 400} days, which is unsatisfiable as written; the event-time form is now the rule, and
conformance MUST include a strictly-interior signal, since those three deltas cannot discriminate
the two forms. The §6.1 fountain sentence is corrected (RaptorQ is all-or-nothing at block level;
graceful degradation belongs to the layered codec) and the noise-floor default re-founds on the
layered-codec fidelity metric. #6 is addressed without being closed: the MUST now binds relative to
a pinned adversary model, and the side-informed limb is marked unverifiable-pending-instrument.

**CCA is no longer cited as authority.** CCA v5 withdraws its own validations — k_eff hardware
checks reclassified as identity checks, institutional application re-scored below chance, collapse
asymmetry "assumed, not derived". No "CCA-validated" label attaches to any claim in §6.2; v5 is
cited for the surviving Möbius/ceiling core only.

**Part VIII — the traceability matrix stops flattering itself (#50 item 7).**
`remainder_scales_with_k_eff` is re-graded to *theorem-given-model, remainder only*: it bounds the
remainder order of an assumed decay law with substrate-specific free constants. It does not
establish the decay law, and nothing in the corpus establishes the collapse asymmetry. Kish and the
ceiling are *identity*; J = F is *identity*. §8.6.1 is populated with the borrowed instruments, and
the priority claim is retired positively: **the claim is application, not discovery.**

**Part I — the keeper thesis (#32), scoped to what is evidenced.** A recognition-grade preamble
paragraph, and "what M-1 does not contain": no aggregation rule, no ranking of losses, no
superlative derivable. M-1 does not launder witness into theorem.

**Trust, consent and contextual integrity (#48, #46, #47, #49, #40, #44).** Trust-root operational
semantics ratified: two named conferral planes, un-trust as one deletable acceptance edge with
everything downstream failing closed emergently, and **liveness as a reported signal that MUST NOT
be ANDed into validity** — a root is valid until revoked, superseding an RC2 reading that would
have darkened the mesh at once. Consent-before-scoring for `capacity:*` is **ratified**
(CC 3.4.5): family-scoped, community-addressed (root-addressed consent is consent to an
unenumerable set), enforced at federation-tier admission on a live `consent:scope:analyze` grant,
with the role-gated abuse-response families exempt because an abuser never consents — the rule the
shipped substrate already enforces, so the spec and the mesh agree. The fourteen verify attestation
families are dispositioned per family (none consent-gated: they verify artifacts, not agents). The
**read boundary** remains reserved design space, tracked at CIRISConstitution#49.
`hard_case:deletion_window_breach` is evidence, never a verdict; no affirmative `deletion_proof`
artifact, which a producer could emit while retaining the bytes. The swap test becomes a
mandatory drafting gate, and bootstrap is handled by *building* the declared-asymmetry register
rather than leaving a silent exemption.

**Wire hygiene (#41, #38, #37, #30, #42, #43, #39).** The CC 2.3.2.1 canonical-subject preimage is
pinned byte-level (all five golden vectors verified to reproduce; no digest changes). A 1 MiB
canonical-bytes bound lands at CC 2.6.1.3, enforced at every write path — Part V's fixed 1.4 KB
envelope is a traffic-analysis rule that chunks rather than refuses, so it bounded nothing at
admission. One canonical spelling is frozen for the hybrid construction, chosen on repo evidence
rather than preference, together with the class rule that prevents the next collision. `C_CIRIS`
becomes `min(...)`: the five-factor product scored positive whenever an even number of factors were
negative, inverting the anti-Goodhart rationale it exists to serve. Family counts are now
**generated, not asserted** — `manifests/namespace_registry.json` is the registry of record, and the
generator's hard-coded expectation is removed so the number cannot go stale again.

**Declined or deferred, on the record.** Dead-clauses-keep-their-killers (#49-A4) — declined;
errata live in git, GitHub and Zenodo. The proof-centipede witness format (#36) — deferred to 1.1;
ratifying a paragraph does not make a format real. The `lp()` re-spelling of the canonical subject
(#41 comment) — declined; it crosses the CC 6.1.3 seam and re-spells every ratified digest to buy a
property the colon-ban already gives. The severance window on the halt fire path (#40 comment) —
declined; it hands the halted party an escape at the instant the brake is pulled.

**Deferred to the post-1.0 candidate backlog, on the record (the #36 principle: ratify the format that survived, not the one specified).** #32's asks 2-5 — the six consent-foundation `lean:` claim rows, the `need:survival:*` reserved domain with the one-card mandate, and the totalitarian-case proxy-promotion composition — are deferred with successor issues; only the keeper thesis (ask 1) landed in this cut. #57 (mesh-config authorship) is **reserved, not designed**: CC 4.2.1 now forbids an implementation deriving the authority from silence, and the model ratifies on the issue's sketch. #58 (graded enforcement tiers), #59 (reverse-quorum objection form), #60 (volume standing + `revoked_after`) are deferred with their proposal sketches recorded on the issues — each has no implementation whose survival could be ratified, and #60's own caveat (a naive rate cap is a censorship primitive absent a reserved admission class) is the reason not to ratify it from the armchair. #49-A1 (the `capacity:*` read boundary) is deferred at CC 3.4.5 with the non-conformance rationale stated in-text.

**Not discharged, and marked as such.** #49-A2's anti-forking binding did not survive drafting:
CC 1.15.5 states covenant identity recognition-grade and explicitly declines the binding (no
lineage dimension family exists, moderation records are relative and positional, and nothing
bounds keys per owner — a whole-or-nothing rule would quantify over a unit the subject itself
partitions); the wire-level design is tracked at #49 and the claims row is `staged` against it. #50 item 8 — commissioning
external reviewers with standing to kill sections — is not a document change and remains open; it
is the one item nobody inside this ecosystem can substitute for.

### Machine-generation disclosure becomes mandatory (#9, EU AI Act Art. 50(2))

**CC 3.4.14 `synthesis-disclosure` (new, normative).** Marking AI-generated content is no longer a
planned interoperability profile — it is a MUST, discharging EU AI Act Art. 50(2)/(4) (applicable
2026-08-02) with **zero new wire surface**. The rule rests on what CEG already does: attest a source.
R1 makes `content_class:generated` / `content_class:generated_modified` mandatory on every
Contribution carrying generated or materially-altered content, from any attester; R2 binds the
agent-produced case to an `identity_type` containing `agent`, so machine origin is readable from the
signed envelope rather than from a self-declared flag; R3 requires the marking to survive egress to
non-CEG channels, with an unmarkable channel recorded as a `hard_case:*` exception rather than
silently dropped; R4 carves out assistive operations (a disclosure that fires on every spell-check is
not a signal); R5 puts the duty on the generator, keeps false marking on the existing false-attestation
evidence floor, and leaves verdicts with the WA quorum. `generated_modified` is a canonical addition to
`content_class`'s existing open vocabulary (documentation-only per CC 4.5.1.1), and CC 3.3.12's
`content_class` is clarified as not multimedia-scoped — it reaches text.

**CC 8.4.2 C2PA profile — ADOPT → adopted, emit limb normative.** The profile's `MAY` is promoted to
`MUST` for generated media as the media-egress form of CC 3.4.14 R3; the AI-generation disclosure
named descriptively in the CC 3.3.13 multimedia Source structs is marked mandatory with a fail-secure
default (absent/unknown on an agent-attested Contribution resolves to *disclosed as generated*).

**Compliance-mapping corrections.** The CC 4.5.2 regulatory table filed training-data transparency
under EU AI Act Art. 50; that is Art. 53(1)(d) (GPAI) — the row is split and both are now pointed at
the primitives that actually carry them. The CC 8.3 conformance row for Art. 50 moves from
*Informative* to *Evidence-bearing (staged)* — the normative rule is cut; the emit is unshipped and
tracked at CIRISConstitution#9.

**Conformance pin.** For the text outputs the platform generates — the only synthetic content any
shipped path produces — the Art. 50(2) machine-readable marking is the **shipped attestation
surface itself** (`is_bot` on every agent message + the admission-enforced signed
`identity_type: agent` binding), marking by construction rather than add-on. The **C2PA emit** is
the media-egress interop limb: no shipped path generates synthetic media, so it is pre-staged, not
overdue — its claims rows are `staged` against CIRISConstitution#9 until a generation path exists
for it to mark. Normative coverage holds at 100% (134/134 sections).

## 1.0-rc2 — evidence registry, two new invariants, and the coherence math finalized

Consolidates the post-review work into the release candidate.

**Evidence registry (spec as executable infrastructure).** New `constitution/EVIDENCE.md`
(tag vocabulary), `constitution/claims.tsv` (146 load-bearing claims), and
`tools/check_claims.py` — a CI gate (`.github/workflows/consistency.yml`) that validates
evidence pointers, the dual-ID spine, and normative coverage. Coverage **132/132 sections
(100%)**. Cross-repo `impl`/`test`/`lean`/`bench` pointers resolve by CC decimal against
five **pinned, vendored** sibling manifests (CIRISServer, CIRISConformance,
coherence-ratchet, RATCHET, CIRISAgent): **116 pointers resolved, 118 claims established**.
A generated **Evidence Register** appendix is rendered into the PDF. The checker also caught
and closed real drift — **29 prose sections** were missing from `toc.tsv`/`codebook.json`
(reconciled; spine 400 → 429; drift now a hard error).

**Single-owner invariant (CC 3.2).** Closes a grindable ownership-resolution leak: node
ownership is the single-valued `delegates_to(user→key, purpose: owner_binding)` sub-relation
(distinct from multi-parent act-on-behalf/hierarchy); `owner_of` is purpose-filtered → at
most one; admission-time reject of a second distinct owner; consumers fail-closed on
cardinality ≠ 1 (no `.next()` a sorted set); no permanent ownerless lock. Adversarially
validated (grind CLOSED).

**Detection discriminator (CC 3.4.8).** Pins the wire discriminator as the prefix contract
itself — any `detection:*` row is a primary emission requiring `lenscore_detector`;
cross-attestations ride `truth_grounding:detection:*` — so the persist admission gate is a
blanket reserved-prefix rule with no envelope parsing.

**Coherence mathematics finalized (CC 6.2.1 / 6.2.3.1).** Both upstream-open questions are
now mechanized in Lean. The collapse remainder is **`O(r²·k_eff)`** (not `O(r²·k)`) —
`remainder_scales_with_k_eff` — so the bound is uniform in `k` and the crossover pathology
dissolves. The **σ signal-source Kish discount** (`Signal_eff`, `clique_neutralization`)
lands normatively at 6.2.3.1, closing the colluding-clique σ-pump. Honesty caveats preserved
(substrate-specific constants; the full source-attributed provenance-vector state-shape is a
stated future refinement).

VERSION → 1.0-rc2.

## 1.0-rc1 — 1.0-readiness gap register (G-A…G-G) + finalized front matter

The seven-gap pre-1.0 register, applied with exact fixes, plus the finalized executive summary.

**G-A (BLOCKER) — live-quorum roster-capture (CC 4.2.6).** Closes a defeat of the HUMANITY_ACCORD
kill switch through its own recovery path: an adversary capturing a strict live majority and censoring
the honest minority through the participation window `W` could remove honest holders (the old
steward-cosign trigger only fired at `\|L\| < L_floor = 3`, which stopped scaling as the roster grew).
Four additive fixes: (1) a **scaling removal-gate** — any roster change that *removes* a standing
holder needs the 2-of-3 steward co-sign whenever `2·\|L\| ≤ N_standing`; (2) **fire-authority
persistence** — a holder named for removal keeps floor-of-1 fire through a lame-duck window;
(3) **contest is a duty** — a removed holder MAY contest within `W` **or post-`W` on immutable
append-log evidence**, the steward quorum MUST adjudicate within a bounded SLA (72 h / 7 d) and MUST
restore on a seizure finding; (4) the entrenchment proof corrected to state the capture partition
honestly. Adds the `accord_contest` / `accord_restore` canonical-bytes domains and the log-snapshot
verify-resolution carve-out for off-roster contestants. Adversarially validated:
PARTIALLY-CLOSED → fixes → **CLOSED** (attack no longer achieves permanent disablement; the surviving
bounded steward-restore dependence is named).

**G-B — noise-floor overclaim (CC 6.1.2).** "Information-theoretically unrecoverable" → **not
individually recoverable by the specified procedure `R` above fidelity `ε`**; `(R, ε)` operator-tunable
with a pinned default + conformance vector; the `< 1/N` claim caveated to non-dominated composites.
New acknowledged risk **R9** (composite invertibility) in CC 8.3.1.

**G-C — Order-Maximisation Veto (CC 1.3).** "→ abort action" → **mandatory WBD deferral** (CC 1.9): the
10× ratio triggers human judgment over incommensurable estimates, not an unfalsifiable MUST-abort.

**G-D…G-G (editorial).** Kill severity-dial paragraph (missed fire terminal / false fire recoverable)
at CC 4.2.6 + cross-ref from 4.2.3; "coherence signal" defined in CC 8.1.1 by what it measures (kills
the σ integrand circularity); σ constants `d`/`w` marked initial operating values pending calibration;
the HF/Reticulum relay backbone indexed as a deferred row in CC 8.3.6.

**Doc precision (folded in — closes #8, #10).** Annex C statutory mapping consolidated to adopted
**Regulation (EU) 2024/1689** numbering (post-market monitoring **Art 61 → Art 72**; added Art 10 / 15 /
16 / 50 rows; 2 Aug 2026 applicability). The `DISCRIMINATION` prohibition is described at its true
enforcement point — the **WiseBus capability gate** (`NEVER_ALLOWED`), with the prohibited-capability
set injected into the round-1 DMA reasoning context (CIRISAgent#910) — not "PDMA Step 1"; the Art
10(2)(f)/Art 9 evidence is the bus-rejection log **and** the DMA reasoning trace.

**Front matter.** Executive summary finalized: running-system framing ("this is not a proposal"), the
safety thesis stated as a bet (plurality, never a singleton; correlation not headcount), and Part 8 as
the standing weakness register.

**Ratification note.** G-A amends the **entrenched** CC 4.2 HUMANITY_ACCORD surface; per CC 4.5.1.2 an
entrenched change requires a MAJOR version bump **and** a dedicated accord ratification — pre-maturity,
the founder/accord-holder authority, exercised via an out-of-band ceremony. Tagged **1.0-rc1** pending
that ratification; tagging 1.0 is the steward's ratifying act.

## 0.9.3 — executive summary: mesh-safety thesis + what the assumptions rest on

Reframes the executive summary around the whole-mesh safety thesis: this is the
constitution of a decentralized network (CEWP — the internet without the centralized
middle), safety is a property of the diverse federation rather than any single aligned
model ("a singleton is a condition to be prevented; the parts, together, are what is
safe"; check the behavior, not the weights). Adds an explicit "what the safety
assumptions rest on" section — the Part VI correlation-not-headcount mathematics, its
narrow engineering-tier import from coherence-ratchet, its falsifiable/open status, and
that current empirics strengthen it. No normative change.

## 0.9.2 — executive summary revised: consent-reaching-all-agency-surfaces framing

Revises the executive summary to lead with *why*: consent-based governance must touch
every output surface a frontier system's agency can reach, checkable at the point of
expression. Trims the apex language to a single M-1 mention; adds an explicit statement
of how the science (coherence-ratchet) relates to the law — narrow engineering-tier
import, public retractions upstream, the seam explicit so neither corrupts the other.
No normative change.

## 0.9.1 — executive summary in the front matter

Adds `constitution/EXECUTIVE_SUMMARY.md` — a one-page plain-language statement of
what this document is and why (the README's register, inside the document itself) —
placed before the Foreword in the built PDF. No normative change.

## 0.9 — CEG replication storage-contention axis (§Q, seed-blocker)

Closes the last replication gap before mesh seed: replication was specified by **wire type**
(CC 5.3.2.3), **membership** (`cohort_scope`), and **consent** (`consent:replication`), but had
**no rule for resource / storage contention on an owned node** — no owner budget, no pin, only
reactive eviction after content had already landed. New normative section **CC 6.1.5.2**
(`storage-contention`, §Q) adds the missing 4th axis (the IPFS-pinning model), sourced from
CIRISServer `FSD/MESH_REPLICATION.md §3.3` and twinned with CIRISServer#145:

- **Pin classes / pin-on-consent (B1–B2).** Identity/consent/config always pinned; corpus is
  pinned iff a `consent:replication` grant authorizes its `subject_kind` **and** the owner elects
  to spend budget on it — else it is cache (GC-eligible, descends first). The grant's
  `attestation_prefixes` grammar is extended to name corpus classes (reciprocal note at CC 3.3.7).
- **Owner budget, per `cohort_scope` (B3).** A new signed `StorageBudgetV1` declares per-scope
  `budget_bytes` + `pin_reserve_bytes`; `self`/`family` scopes are suppressed from the wire
  (CC 5.2 structural invisibility); supersedable by monotonic `revision` (anti-rollback).
- **want/have + size cap (B4).** A new signed `CorpusWantV1` makes large corpus wanted-then-pulled,
  never unsolicited-pushed; content-addressed (CID) for free dedup.
- **Arbitration + consent supremacy (B5–B6).** Deterministic descent order (cache → low-rarity →
  oldest revision); budgets are consumption-challengeable (no forged-budget force-evict); a pin
  **never** defeats revocation (N5 still forces descent below the floor regardless of pin).

Both `StorageBudgetV1` and `CorpusWantV1` are CC 6.1 substrate shapes (16-byte domain separators,
hybrid Ed25519+ML-DSA-65, verify-at-ingest, #57 freeze-gate vectors) — **not** CC 2.1 attestations,
so the 1+4 surface is untouched. Given its own skeptical validation: REJECT (9 issues) → fixes →
ACCEPT (results.csv + MANIFEST addendum). Wired into CC 6.1.2 pressure sources and CC 6.1.2.3
`EjectionVerdict`.

## 0.8.1 — coherence-math errata (σ decay + λ symbol split)

Two bounded corrections to the Part VI coherence mathematics, surfaced by a
review of the 0.8 migration and pressure-tested before landing:

- **σ update rule → continuous exponential decay (CC 6.2.3).** The printed
  linear recurrence `σ·(1 − d·Δt)` went negative for `Δt > 20` days (flipping the
  sign of `J = k_eff·λ_op·σ` for a node rejoining after a long partition — the
  decimation-recovery case) and, more deeply, was not a semigroup, so peers
  polling σ at different cadences over the same signal stream desynced. Replaced
  with `σ(t+Δt) = σ(t)·exp(−d·Δt) + Signal·w` (`d = 0.05`/day, continuous rate,
  decay before signal), with normative **step-invariance**, **right-to-return**
  (a rejoining peer never scores below cold-start), source-semantics, and a
  recalibration note. `d` is now a continuous rate (half-life ≈ 13.9 d).
- **λ symbol split (CC 6.2.1 / 6.2.2 / 6.2.4).** The collapse theorem's geometric
  decay rate (`λ_geo ≈ 2r`, deceptive-region radius) and the operational
  strictness knob of J/F (`λ_op`) were one glyph; now split, with a normative
  MUST-NOT-substitute clause. Added a **saturation note**: past the Kish ceiling
  `k_eff ≤ 1/ρ̄` the collapse bound is uninformative, so only lowering `ρ̄`
  (genuine diversity) — never adding correlated constraints — tightens the floor.

σ is a locally-computed metric and enters no signed/byte-exact preimage, so this
is behavioral errata, not a wire change. Deeper items (a noise-floor adversary
model, signal-source correlation discounting, the O(r²·k) error-term form) are
tracked as issues, not bundled here.

## 0.8 — Book IX migrated into Part VI; honesty & pointer-hygiene pass

Migrates the Accord's **Book IX** (1.3-RC2, post-cleanup) into **Part VI** as a new chapter
**CC 6.2 — the coherence mathematics**: the constraint-manifold ratchet and topological-collapse
theorem, the defense / flourishing functions `J = F = k_eff·λ·σ`, the sustainability integral σ,
and the normative **σ-attestation requirement** (CC 6.2.3.1). Only the surviving F-form engineering
tier is carried — the upstream-retracted universal-scale material (grace / joint-backward pass) is
excluded by construction. Repoints the previously-dangling "Book IX §5.2" citation (Annex G) to
CC 6.2.3.1, and extends the dual-ID codebook (392 → 399 concepts). Also carries the **C/F**
nomenclature note where `𝒞_CIRIS` is introduced (CC 3.1.8.1); adds the pointer-hygiene notes
(Piece 10 *karma* precision; the A0–A4 autonomy-tier vs A0..A5 substrate-rung scale
disambiguation); and, per the corpus's own honesty discipline, restates the migration record as
**source-fidelity validation under a skeptical rubric** rather than "adversarial certification"
(the evidence is unchanged; only the framing is corrected).

## 0.7 — wire vocabulary as a hash-pinned artifact

Introduces the two-tier wire-vocabulary governance hook (§2.6.4, no new section) plus the
[`manifests/WIRE_VOCABULARY.md`](manifests/WIRE_VOCABULARY.md) registry artifact: **Tier-1**
CC-ratified load-bearing message types (amended via the ordinary §4.5.1 "Standards Action"
path) and **Tier-2** opaque `kind`-range channels delegated per-repo ("Private Use"), grounded
in the RFC 8126 / Nostr / Matrix / AT-Lexicon prior art. The vocabulary is a hash-pinned
manifest; migrating a type to Tier-2 moves its schema, canonicalization, and convenience API
into the range steward's own repo.

## 0.6.1 — CEWPOS object-model review batch

Ratifies / doc-fixes the CEWPOS object-model review findings (#116–127) and triages the
demand-pull backlog (#118–129): fair-exchange narrowed to trustless atomic swap,
canonicalization totality, the Order-Max-Veto reasoning ruling, record/legal-recognition
clarification, and acronym doc-fixes.

## 0.6 — adult-incapacity stewardship, child-safety rulings, HUMANITY_ACCORD H6/H7

Adds adult-incapacity stewardship (§3.4.12 — capacity-assurance, prior-will-first,
least-restrictive per CRPD Art 12, fail-to-liberty auto-restore); seven child-protection
rulings (§3.4.13); the HUMANITY_ACCORD key-independent steward floor (H6) and
restore-to-known-good entrenchment exception (H7); and the live-quorum decimation-recovery
canonical-bytes pins (#113).

## 0.5.1 — affiliations + infohazard glossary

Defines the affiliations institutional cohort (§4.4.3.2.8 — necessity-vs-interest, legal-hold,
N5-erasure gate, compartments, lawful-access) and the six-phase infohazard glossary entry
(§8.1.1, grounded in the Bostrom typology).

## 0.5 — mesh-safe seed cut

The mesh-safe seed. Reframes binding to **stewardship** throughout (responsible *for*, never
holder *of* — steward, not the retired term); adds verified-rung age-assurance (§3.4.11) and minor-steward binding; absorbs the
§11 wire vocabulary; and defines reverse-quorum moderation (§4.5.13 — propose → 48h fallback →
unilateral moderator/steward action or community live-vote; default-remove for harm reports;
infohazard consent gate).

## 0.4 — accord:lifecycle:active resumption preimage

Ratifies the `accord:lifecycle:active` resumption preimage into HUMANITY_ACCORD (§4.2.1.3).

## 0.3 — accord live-quorum decimation-recovery

Ratifies the live-quorum decimation-recovery procedure into the entrenched HUMANITY_ACCORD
(§4.2.6 — fire-floor-1, fail-to-liberty for adults). Grounds CIRISVerify FSD-004.

## 0.2 — first complete cut

The first complete, clean cut: all ten Accord annexes (A–J) migrated in full, all internal
references resolved, and the three definitional frameworks anchored to international sources
(Risk Magnitude → MIL-STD-882E / DO-178C / EU AI Act; autonomy A0–A4 → SAE J3016 / DoDD
3000.09; sentience heuristic).

## 0.1 – 0.1.5 — consolidation

Initial consolidation of CEG (1.0-RC29, 1+4 surface frozen) and the CIRIS Accord (1.3-RC2)
into one document. Importance-derived spine (PageRank over the unified cross-reference graph),
dual reversible IDs, faithful copy-migration baseline, skeptical per-chapter validation to
0-REJECT certification, Scope & Disclaimers, and the perpetual-stewardship model.
