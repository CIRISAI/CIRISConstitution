# Changelog

All notable changes to the CIRIS Constitution. CC is one document with one version line;
each cut is validated against its sources under the skeptical rubric before it lands.

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
