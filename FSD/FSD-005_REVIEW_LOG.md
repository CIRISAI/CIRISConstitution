# FSD-005 — Adversarial Review Log (v0.1 → v0.2)

Four independent adversarial reviewers challenged FSD-005 v0.1 on distinct
lenses. No fatal flaw in the core thesis (zero new wire primitives, zero new
namespace families). All findings below with disposition:
**ACCEPTED** (fixed in v0.2), **SCOPED** (deferred/re-tiered with a reason),
or **REJECTED** (challenger mistaken, with the counter).

## Cross-validated (≥2 reviewers converged — highest confidence)

| # | Finding | Reviewers | Disposition |
|---|---|---|---|
| X1 | **`content_rating` gate is misspecified** — it is CC 3.3.12 (open-emit, `signed`, certifier confidence in polarity), NOT reserved/trusted-publisher-only; §11.5.3 is fabricated; the *composition* into a per-caller decision does not exist in persist | fidelity HIGH-1, realizability M1, red-team CRIT-1 | ACCEPTED — §6.1 corrected; composition marked net-new server-tier ask |
| X2 | **The safety families are OUTSIDE the 95** — content_rating/content_class/cw_class (CC 3.3.12), consent:* (CC 3.3.1), age_assurance (CC 3.4.11), capacity_assurance (CC 3.4.12) are the CC 3.3/3.4 surface, not the CC 3.1 `scores` registry the 95 come from | fidelity MED-5 | ACCEPTED — §1/§9 rescoped: finite catalog = CC 3.1 (95) + CC 3.3 + CC 3.4; "zero new families" still true, but the catalog claim is now honest. THE headline correction for the operator's "flesh every namespace" directive |
| X3 | **Age default mislabeled + anonymous reader unaddressed** — CC 3.4.11 is protective (absence/Unknown/declined → BLOCKED from adult); "presumption-of-sovereignty" is the CC 3.4.12 *capacity* default, inverted. Substrate default is already fail-secure; the real gap is the reader routing anonymous/no-occurrence-key callers through the gate | fidelity MED-6, red-team CRIT-3 | ACCEPTED — §6.1 corrected to CC 3.4.11 protective semantics + explicit anonymous→protective-minor policy |
| X4 | **`n_eff` misused as witness-independence** — n_eff (CC 6.1.2.1.2) is a fountain-storage content-mass dominance metric, not attester independence; the witness gate is `witness_diversity` (CC 3.1.9.3). As a headline weight it's cosmetic and on the wrong plane | fidelity MED-4, red-team HIGH-4 | ACCEPTED — §2/§7 use witness_diversity; n_eff scoped to storage/retirement plane |
| X5 | **Perspective presets misuse Policy C/J** — Policy C (CC 4.4.3.13) is EigenTrust transitive trust (not expertise-weighting); Policy J (CC 4.4.3.10) is multimedia distribution (not licensure). Also `holders_of` is unbounded/recursive | fidelity HIGH-2/3, product M2, realizability H3 | ACCEPTED — presets = Policy A/B restricted to `holders_of`/`licensed_by`; holders_of restricted to one non-recursive verdict level in V1 |

## Substrate realizability (persist — reshapes §5/§10)

| # | Finding | Disposition |
|---|---|---|
| R-C1 | A world-fact claim has no valid `attested_key_id` (NOT NULL FK); emit defaults to attester's own key → evidence scatters; aboutness lives only in `subject_key_ids` | ACCEPTED — §2 declares the subject-key convention; `attested_key_id` is NOT the claim-gathering key |
| R-C2 | Phase-1 btree `(attested_key_id, dimension, asserted_at)` is the WRONG shape — subject is JSONB-array membership; needs GIN-on-expression or a normalized subject projection **with a backfill** (not "non-breaking") | ACCEPTED — §5 phase-1 rewritten to a subject-index projection; honest about the backfill |
| R-H1 | No subject-scoped read handle exists; the cited "proven mold" (`resolve_scoped_consent`) is a full-history fetch-and-fold-in-Rust | ACCEPTED — `list_scores_for_subject` named as net-new; resolve_scores/claim_timeline are ground-up, not "3 handles in a proven mold" |
| R-H2 | The §6.1 gate stack IS the N+1 — `age_band`/infohazard each do a full `list_attestations_for` before the scores fold | ACCEPTED — §6.1 notes the caller-gate must be a composite op (like the #329 ResolveEncryptionKeys pattern) or per-request cached |
| R-H4/M1 | `evidence_panel` per-ref = unindexed seq scan (needs GIN on evidence_refs); `content_rating` composition net-new | SCOPED — evidence_panel + content_rating composition = server-tier V1; GIN-on-evidence_refs added to §10 |
| R-M2/M3/M4 | SQLite STORED-generated-column asymmetry; tier-blindspot (local rows for drafts); cursor must be (asserted_at, attestation_id); trace size uncapped | ACCEPTED — §5 notes |

## Red-team abuse/safety (deepest — reshapes §6)

| # | Finding | Disposition |
|---|---|---|
| RT-C1 | **Content plane beneath the gate** — replication (federation-scope = cleartext to every node's disk), at-rest, holds_bytes/ContentFetch (takes a hash not a caller), evidence_ref *URIs* (arbitrary off-substrate) are all ungated. §6.1 is render-tier only → fails OPEN for infohazard/CSAM | ACCEPTED — §6.1 becomes defense-in-depth: flagged classes fail-closed at-rest + suppressed-from-replication (CC 5.2 invisibility extended); holds_bytes/ContentFetch gated; evidence_ref URIs non-dereferenceable without a gate (prefer hash+holds_bytes) |
| RT-C2 | **Ask-the-Article** — mosaic synthesis across per-row-gated claims produces aggregate hazards; agent dereferences ungated evidence_refs; claim text is a prompt-injection surface | ACCEPTED — §6.1: compose-then-gate + synthesis-level check; agent forbidden from ungated ref deref; claim text = untrusted input |
| RT-H5 | **Withheld-count oracle** — "N rows withheld" + subject + timeline ordering = existence/targeting index; cross-band verdict differencing leaks stance | ACCEPTED — withheld rows excluded from text AND math; existence reported only coarse/noised, never per-dimension |
| RT-H6 | `list_attestations` + knowledge-graph neighbor labels ungated (feature 9 handle isn't a §5 gated handle) | ACCEPTED — graph labels/list_attestations run the gate stack; gated-neighbor titles suppressed |
| RT-M8 | Epistemic: withdraws rule-3 proxy needs proof-of-CONTROL (not guessable-hash knowledge) else mass-censorship; judge_model open-emit needs execution-provenance binding; recants-vs-withdraws reputation laundering; citation-laundering (self-published evidence_refs) | ACCEPTED as §7 hardening asks; withdraws rule-3 VERIFIED against CC 2.4.1.1 (proxy requires a live `delegates_to` chain — control, not knowledge; noted) |
| RT-M9 | `expertise` uncapped (only licensure has the ≤0.5 co-steward cap); substrate_building credits bypass the vote-loop sybil bars | SCOPED — §7 flags an expertise single-source cap as a composition-policy ask |

## Product coherence (reshapes §2/§3/§8, adds §0)

| # | Finding | Disposition |
|---|---|---|
| P-C1 | **Unit-of-read contradiction** — "beautiful prose article" vs "every sentence one-click-traceable" cannot both hold over "a projection with no article-body object". Either LLM-synthesized prose (un-attested, trace is a category error) or a bullet list of atomic claims (not a readable article) | ACCEPTED — §2/§3: V1 unit-of-read is the **claim board** (lead + supporting/contradicting + evidence, each verbatim and traceable); prose is a distinct labeled "AI summary — not attested" layer; the trace clicks into the rows |
| P-C2 | **Cold-start absent** — perspectives/filters compose over empty populations (zero expertise/licensure holders at launch); bulk-import is one un-diverse bot → all LOW confidence; no contribution incentive; V1 has no authoring surface | ACCEPTED — new §0 Bootstrap: diverse seed-attester ceremony + depth-first hand-seeded flagship subjects + explicit V1 write-path decision |
| P-H1 | "99.999%" is false precision the composition math can't support — the exact sin the product claims to cure | ACCEPTED — §2: qualitative band + n (contributor count, witness_diversity, open-contradiction count), never a bare high-precision % |
| P-H2/H4 | Trust-filter empty/sparse states undefined; down-weight-not-delete → junk drowns the panel, no curation UX | ACCEPTED — §4 sparse-state spec; §6 reader-tier display threshold (inspectable projection parameter) |
| P-H3 | "Ask the Article (thin)" mislabeled — it's substrate-thin, product-substantial (guardrailed RAG with a hard security property) | ACCEPTED — relabeled |
| P-M1 | Claim-as-hash brittle to wording (paraphrases → different hash → no corroboration); subject-hash vs `contribution_id` keying mismatch | ACCEPTED — §2: stable claim/contribution id attesters attach to, statement text as attached content; softens "the claim IS its hash" |
| P-M4 | No single "current understanding" — per-attester supersession heads can conflict | ACCEPTED — §2 head-selection rule (highest composed verdict, else "contested") |

## REJECTED / already-correct (challenger over-reached)

- **RT-C3 "fail-open minor default"** — PARTIALLY rejected: the *substrate* default is already protective (CC 3.4.11 absence→None→BLOCKED, verified line 1504-1506). The valid residue (reader must route anonymous callers through the gate) is folded into X3. The FSD was under-specified, not fail-open by construction.
- **fidelity LOW-9 "median over-generalizes"** — ACCEPTED as a precision fix (median = correlated_action/distributive/ratchet only; the 5 coherence detectors are signed→mean); minor.
- **fidelity LOW-10 mechanism nit** — ACCEPTED: prohibited:* non-overridability comes from its −1/−0.5-only polarity (CC 3.1.5.4), not a 4.4.2 lock; corrected wording.

## Decisions escalated to the operator (genuinely theirs)

1. **Unit-of-read (P-C1):** claim-board default confirmed for V1; is a non-authoritative AI-prose layer in or out of the V1 demo?
2. **Encyclopedic `truth_grounding` and the Credits loop (fidelity LOW-8):** should commons claims accrue NodeCore governance Credits? Recommendation: **no** — decouple, else encyclopedic volume mints governance currency.

## Addendum — red-team third pass (two constitutional-grade additions)

The abuse/safety reviewer's fuller re-run surfaced two findings that need a
CONSTITUTIONAL answer, not a spec patch — both ACCEPTED into v0.2:

- **RT-C2 — `as_of` time-travel defeats hard takedown.** Append-only + `as_of`
  re-exposes retracted content at a prior timestamp. Fine for consent/doctrinal
  fade; fatal for CSAM/illegal. → v0.2 §6.2 defines two erasure classes (fade
  vs hard-delete); the hard-delete class (exempt from append-only, unreachable
  at any `as_of`, inadmissible at `federation` cohort) is a **V1-blocking
  CC 4.5.1 amendment** (§10) — the substrate has no such class today.
- **RT-C1 (sharpened) — gated hard-illegal content cannot be `federation`
  cohort.** World-replicable = world-readable-raw on an untrusted replica; no
  render gate can undo a byte already on a peer's disk. → v0.2 §6.1-A: CSAM
  inadmissible at federation cohort; flagged classes encrypted-at-rest +
  suppressed-from-replication.

These are the FSD's honest edge: it is realizable on the existing grammar with
ZERO new families and ZERO new wire primitives EXCEPT one genuine substrate gap
— a hard-delete class — which the FSD surfaces rather than papers over. That
single amendment is the only place the knowledge network exceeds today's
substrate, and it is a safety requirement, not a feature.

## Re-verification pass (operator-prompted: "double-check the assumptions")

After the hard-delete finding proved a false "the substrate lacks X," every
absence-claim was re-checked against code. **Three challenger findings
OVERTURNED; two confirmed.**

| Finding | Claimed | Code reality | Verdict |
|---|---|---|---|
| RT-C2 / my §6.2 | "append-only cannot erase CSAM; no hard-delete class; V1-blocking amendment" | `evict_fountain_content_hard_delete` (all backends) drops all symbols, revocation-dominates-rarity, `EnvelopeOnly` tombstone survives; `evict_fountain_content_by_consent`; `takedown_notice` + `LegalBasis::{NcmecCsam,PerceptualHashCsam,GifctCip,CourtOrder}`; erasure stamps `erased_at` | **OVERTURNED** — substrate has it; §6.2 = wiring task, not amendment; §11 decision 4 withdrawn |
| fidelity HIGH-1 | "`content_rating` is open-emit, NOT reserved; §11.5.3 fabricated" | persist ENFORCES trusted-publisher emission (`admission.rs:415/423` reserved-prefix rule); §11.5.3 is a real CEG 0.3 governance section; composition specified in CEG §8.1.10 (unimplemented in persist) | **OVERTURNED** — v0.1 was right; v0.2 "correction" reverted. (Residue: CC 3.3.12 catalog row IS emitter-open — the reservation lives in CEG, a real catalog-vs-CEG discrepancy → editorial ask) |
| realizability R-H1 | "no subject-scoped read handle exists; ground-up" | `AttestationFilter.subject_key_id` (`federation.rs:149`, GIN-backed pg) is a real subject filter | **OVERTURNED (softened)** — filter exists; net-new is only the composed `resolve_scores` fold + an ordered/SQLite index |
| realizability R-C1 | "`attested_key_id` defaults to attester; not the claim key" | `engine.rs:2351` `unwrap_or_else(|| key_id.clone())` | **CONFIRMED** |
| realizability R-C2/M2 | "SQLite subject index unbuilt; GIN pg-only" | V055 comment: "GIN index on subject_key_ids is a Postgres-only optimization"; SQLite has column+CHECK, no index | **CONFIRMED** |

**Lesson for the panel's credibility:** the adversarial reviewers were reliable
on *presence* bugs (a real N+1, a real signature mismatch, a real
mean-vs-diversity-plane gap) and on *product/spec* gaps, but repeatedly
over-claimed *absence* ("the substrate has no X") without grepping — 3 of the
scariest CRITICALs were "missing capability" claims that the code refutes. The
surviving safety findings (defense-in-depth tiers, withheld-count oracle,
sybil-on-the-mean-plane, judge_model laundering, withdraws proof-of-control)
are composition/gating corrections and stand. The FSD's core thesis is now
*stronger* than v0.1 stated: zero new primitives, zero new families, **and no
substrate amendment** — every safety requirement maps to an existing primitive.
