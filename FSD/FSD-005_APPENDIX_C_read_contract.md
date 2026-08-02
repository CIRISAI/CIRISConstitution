# FSD-005 Appendix C — the `scores` read contract (durable; pin-once)

Purpose: settle the subject-index shape for v17.4.0 and define the
consumer-facing read contract so **consumers pin once and we never break them
again**. The design rule throughout: query by LOGICAL axes, evolve
ADDITIVE-only, and put every extensibility escape in the *trace*, never in the
signature.

## C.1 Index decision — (B) a normalized subject projection

**Chosen: (B) a normalized `attestation_subjects` projection table.** Rejected
(A) Postgres GIN-on-expression.

| | (A) pg GIN-on-expression | **(B) normalized projection** |
|---|---|---|
| Backend symmetry (conformance HARD req) | postgres-only; SQLite falls to `json_each` scan → two code paths → the #442 divergence class | **identical btree on both backends** ✓ |
| Hot query "subject X, dimension D, newest-first" | unordered containment + in-query sort | **index-only ordered seek** `(subject_key_id, dimension, asserted_at DESC, attestation_id)` ✓ |
| Write cost | one GIN entry | one projection row per `subject_key_ids[]` element (fan-out ~1, bounded) |
| Backfill | reindex | populate the table (both need a backfill) |
| Serves edge advertise-sweep + server Composer | partially | yes (same ordered seek) |

Backend symmetry is non-negotiable (it is what broke in #442 and what
conformance pins), and the demand is an ordered subject+dimension seek, which
GIN cannot give. The write-side fan-out is a read-heavy-corpus's correct
trade. **V106**: `attestation_subjects(subject_key_id, dimension, asserted_at,
attestation_id, tier, cohort_scope)` maintained on every attestation write +
backfill; `dimension` is the generated column (Postgres STORED / SQLite
VIRTUAL); plus a GIN on `evidence_refs` for the citation lookup.

## C.2 The request contract — ONE filter, all axes, additive-only

Extend the EXISTING `AttestationFilter` (do not fork — it already has the
forward-compat discipline: every field `Option`, `#[serde(default,
skip_serializing_if)]`). The complete orthogonal axis set a `scores` consumer
ever queries by — validated against the demand survey + the namespace analysis
— is fixed NOW so no new axis forces a signature change later:

```
ScoresQuery {                                  // = AttestationFilter, extended; #[non_exhaustive]
  caller_occurrence_key_id: String,            // MANDATORY from v1 (the gate hook — present before all gates exist)
  // — aboutness —
  subject_key_id: Option<String>,              // the claim/entity (exists today)
  attesting_key_id: Option<String>,            // "by" (exists)
  attested_key_id: Option<String>,             // "about-as-target" (exists; NOT the claim key)
  // — namespace —
  dimension_prefixes: Vec<String>,             // prefix, OR-combined (exists)
  dimension_exact: Option<String>,             // NEW — the exact-match axis today's API lacks (attestation_type is exact, dimension only prefix)
  attestation_type: Option<String>,            // exact (exists)
  // — time —
  valid_at: Option<DateTime>,                  // point-in-time (exists)
  window: Option<(DateTime, DateTime)>,        // NEW — range, for timeline
  // — state (made explicit so drafts/retractions need no new handle later) —
  tier: Option<Tier>,                          // NEW — local | federation | any (default: federation)
  lifecycle: LifecycleView,                    // NEW — default Live; opt into IncludeSuperseded / IncludeWithdrawn / IncludeRecanted
  // — trust —
  attester_filter: Option<AttesterSet>,        // NEW — holders_of | reachable_from | licensed_by | ∪/∩ (perspectives/filters)
  confidence_floor: Option<f64>,               // (exists)
}
```

Both handles consume this ONE struct, so a consumer builds a filter once and
uses it for the panel and the timeline:

- `list_scores(ScoresQuery, cursor?) -> Page<ScoredRow>` — raw rows, cursor
  `(asserted_at, attestation_id)` (the existing versioned `AttestationCursor`
  shape). Feeds the Living Article / timeline.
- `resolve_scores(ScoresQuery, policy, trace?) -> ComposedVerdict` — the fold.
  Feeds the Evidence Panel / "why is this believed."

## C.3 The response contract — verdict as a BAND, derivation in an OPEN trace

```
ComposedVerdict {                              // #[non_exhaustive]
  band: ConfidenceBand,                        // QUALITATIVE enum — NEVER a bare float (kills false-precision AND the scale-lock)
  contributor_count: u32,
  witness_diversity: Option<DiversityScore>,   // the anti-collusion n (NOT n_eff)
  open_contradictions: u32,
  age_of_head: Duration,
  policy_applied: PolicyId,                     // which CC 4.4.3 policy
  trace: Option<CompositionTrace>,             // the EXTENSIBILITY ESCAPE HATCH
}
```

`ConfidenceBand` is an enum (e.g. Refuted / Contested / Weak / Supported /
WellEstablished / Insufficient-witnesses), `#[non_exhaustive]` so a future band
does not break a `match`. The float scale never enters the contract, so we can
change the internal composition math forever without a wire break.

**`CompositionTrace` is the escape hatch that guarantees "never change again":**
it is an OPEN structure (`#[non_exhaustive]`, or `serde_json::Value` at the FFI
seam). Any future fold input — the witness_diversity sybil discount, a bond
weighting, a new gate that fired, a new cap — appears as a NEW trace field.
The `band` already reflects it; consumers that ignore the trace are unaffected;
consumers that read it get the new derivation without a signature change. This
is CC 2.6.1.1's omit-vs-materialize discipline applied to the API.

## C.4 The five rules that make this pin-once (and what would break it)

1. **`caller_occurrence_key_id` is mandatory from v1.** The gate hook exists
   before all gates do (the RT-A lesson: two v0.1 handles dropped it and became
   ungatable). Adding gates later is internal, never a signature change.
2. **Every other axis is `Option`/additive**, structs `#[non_exhaustive]`, FFI
   is serde with `default + skip_serializing_if`. A new query axis is a new
   optional field defaulting to today's behavior. A new return datum is a new
   field. Old consumers keep compiling and deserializing.
3. **Query by LOGICAL axes only** (subject / namespace / trust / time / state /
   policy) — never by physical storage (no "index hint," no
   attested_key_id-as-subject). This is what makes **Phase-2 cohort-partition
   re-layout invisible** to consumers: the axes are logical, the storage moves
   underneath.
4. **The verdict is a band + n's, never a float.** The composition math is
   free to evolve (sybil discounts, bonds, diversity gates) because the wire
   commits to a qualitative band + a trace, not a number on a fixed scale.
5. **State is a first-class axis now** (tier + lifecycle), not a second handle
   later. Drafts (local tier), superseded, withdrawn, recanted are all reachable
   by opting the filter in — so "I need to see retracted history" never forces a
   new API.

**The only things that could still break the contract, and why they can't
here:**
- *A new query dimension we didn't foresee* → covered: it's a new `Option`
  field (rule 2). The axis SET is closed by the CC grammar (subject × namespace
  × the 8 reasoning axes × cohort × delivery); we enumerated it.
- *Cross-cohort admin reads* → NOT this contract. Cohort is caller-derived (the
  gate), never a query param. A privileged all-cohort audit read is a SEPARATE
  handle with its own authz, not a mutation of this one. Keeping cohort OUT of
  the query is what preserves the security property.
- *The composition result changing* → not a break: the band reflects policy,
  the change shows in the trace (rule 4).
- *A new composition policy* → a new `PolicyId` enum value (additive).

## C.5 v17.4.0 issue scope (persist)

1. V106: `attestation_subjects` projection + backfill; `dimension` generated
   column; GIN on `evidence_refs`. Backend-symmetric.
2. `ScoresQuery` (extend `AttestationFilter`, `#[non_exhaustive]`, the C.2
   fields); `Tier` / `LifecycleView` / `AttesterSet` / `ConfidenceBand` /
   `CompositionTrace` types.
3. `list_scores` (ordered subject+dimension seek) + `resolve_scores` (the fold,
   as a **composite substrate op** — the #329 pattern — so the caller-gate is
   not the N+1 it replaces).
4. PyO3 + directory-capsule surface (append-only op variants).
5. Delete server's Composer client-fold + the two N+1s onto `resolve_scores`
   (the adoption proof the demand survey asked for).

Explicitly OUT (separate tracks): the composition-POLICY hardening
(witness_diversity discount on the truth_grounding mean, bond-to-emit,
expertise cap, judge_model provenance) is server-tier + CEG-spec policy;
`evidence_panel`/`content_rating` composition is server-tier; wiring the
existing hard-delete to the reader is its own small cut. None of those change
the C.2/C.3 contract — they land as trace fields and policy ids.
