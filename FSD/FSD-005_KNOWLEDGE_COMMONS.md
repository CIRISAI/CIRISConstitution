# FSD-005 — KNOWLEDGE_COMMONS: the attestation-native knowledge network

Status: DRAFT v0.2 (2026-07-14) — revised after a 4-lens adversarial review
(constitutional fidelity · substrate realizability · product coherence ·
abuse/safety red-team). Disposition of every finding: FSD-005_REVIEW_LOG.md.
Owners: CIRISConstitution (spec) · CIRISPersist (substrate) · CIRISServer
(composition + gates) · CIRISLens/GUI (reader) · CIRISAgent (Ask-the-Article)
Normative base: CIRIS Constitution CC 1.0 (Parts 2, 3, 4, 6); FSD-002.

> **v0.2 headline corrections.** (1) The finite namespace catalog is LARGER
> than the 95 `scores` families — it is CC 3.1 `scores` (95) **plus** CC 3.3
> content-ingestion (consent, content_class, content_rating, cw_class,
> age_assurance) **plus** CC 3.4 reservations (age/capacity assurance ladders,
> co-steward, detector, substrate). The safety story runs on the CC 3.3/3.4
> surface. "Zero new families" still holds — but the catalog is these three
> sections, not one. (2) Safety gating is **defense-in-depth at every tier**
> (at-rest, replication, fetch, render, AI), not a render-tier courtesy — and
> the substrate **already has** the two-layer erasure model (fade + a real
> `evict_fountain_content_hard_delete`/`takedown_notice` hard-delete, §6.2);
> hard-illegal classes are kept out of `federation` cohort. (3) The unit a user reads is a
> **claim board** of verbatim traceable rows, not synthesized prose. (4) V1
> needs a **bootstrap** (§0) or every flagship feature composes over empty sets.

---

## 0. Bootstrap — the cold-start the demo lives or dies on (NEW)

An attestation encyclopedia with zero attestations demonstrates nothing, and
its flagship features fail *by their own math* on an empty corpus: perspectives
compose over empty populations (no `expertise`/`licensure` holders at launch);
a bulk-import bot is one un-diverse source `witness_diversity` correctly
down-weights to LOW; "my friends" is empty for every new user. V1 ships a
**curated depth-first seed**, not breadth:

1. **Seed-attester ceremony** — a *diverse* founding set: N independent domain
   stewards holding real `expertise:{domain}` (distinct jurisdictions/orgs/
   software stacks so `witness_diversity` bars are met) + at least one
   `licensure:{authority_id}` co-steward **pair** (CC 3.4.9 needs two for
   confidence > 0.5).
2. **~5 flagship subjects hand-populated to full depth** — multiple independent
   claims, a live contradiction, a supersession chain, real *independent*
   `evidence_refs`. This makes the Evidence Panel demo impress, not render empty.
3. **The V1 write path is decided** (operator, §11): single-user claim authoring
   (create → attach evidence → sign); collaborative editing deferred.

### 0.1 The Wikipedia/Wikimedia import — articles as the starting substrate, claims as editorial (CIRISProxy)

The corpus body is imported from Wikipedia/Wikimedia by **CIRISProxy**. The
load-bearing rule: **import Wikipedia's STATEMENTS, never its AUTHORITY** — and
the practical model that makes bootstrap tractable: **articles are the unit;
claims are editorial acts layered on top, not generated up front.**

- **Article-granularity, NOT claim-decomposition — and the namespaces already
  exist (CEG 0.3/0.4, zero new families).** An encyclopedia article is its OWN
  object: the **`encyclopedia_article`** `external_content` sub_kind — spec'd
  verbatim as *"Wikipedia-shape; editor-consensus + revision chain via
  `supersedes`; indefinite `valid_until`"* — a Contribution whose content is the
  article text (`holds_bytes`), stable article-id. Broken-out claims ride the
  **`encyclopedia:*`** dimension family ("encyclopedia-content claims;
  editor-consensus + revision chain," `signed`). **Articles and claims reference
  each other bidirectionally** via the open-vocab **`topical_relation:{kind}`**
  edges (`cites_source` / `references` / `corrects` / `supersedes_article` /
  `see_also` — new kinds are documentation-only, no amendment). There is **no
  NLP claim-extraction in the bootstrap path** — the granularity question
  dissolves, and the whole article model is pre-existing spec.
- **No trust-root involvement.** The accord/canonical root does NOT bless imports
  as canonical truth (rooting is *recognition of provenance*, not *conferral of
  truth*; blessing would rebuild appeal-to-authority, make one key a corpus-wide
  capture point, and kill contestability). CIRISProxy is a **registered
  federation key**, nothing more.
- **Display gate = two concurring proxy occurrences = the sub_kind's
  "editor-consensus."** An imported `encyclopedia_article` is "good enough to
  DISPLAY" when **two independent CIRISProxy occurrences agree on `(article-id,
  oldid, content_hash)`** — the substrate realization of the sub_kind's
  editor-consensus requirement: a *faithful-relay* cross-attestation (two
  independent fetches confirm this really is Wikipedia revision R). The article
  renders as *"Wikipedia revision R — 2 concurring relays,"* a **provenance
  statement, never a truth claim.** Each import is a `scores` attestation with
  `epistemic_mode: derivative`, `witness_relation: external`, `evidence_refs:
  [wiki-url, oldid, content-hash]`, + a `transparency_log:inclusion` anchor.
- **Claims are editorial, layered on the article.** Any proposition inside a
  displayed article can be **broken out**: a real attester extracts the specific
  claim, creates an `encyclopedia:*` / `truth_grounding` attestation ON that
  claim, and **cites it back into a revision of the article** via
  `topical_relation:cites_source`. Epistemic weight accrues exactly where someone
  chooses to assert or contest — the article is the scaffold; claims are the
  edits. This moves claim-creation from *generation* (exhaustive, NLP-blocked, a
  mountain of un-attested atoms) to *editorial* (targeted, real, attributed).
- **The honesty property holds cleanly.** Article-level display is an explicit
  faithful-relay provenance statement ("Wikipedia says, 2 relays concur");
  claim-level *confidence* exists ONLY once a claim is editorially created and
  attested. No import ever masquerades as a verified fact, and no single-source
  content is ever rendered as high-confidence — because the article isn't
  *claiming* confidence, it's showing provenance. Real `witness_diversity`
  accrues on the broken-out claims as independent attesters engage.
- **Revision-as-supersession (free):** a later Wikipedia revision is a
  `supersedes` on the article import, so the CEG timeline natively renders
  Wikipedia's edit history. Imports MUST carry `oldid` so supersession has a key.
- **Channel-trust, not content-trust:** optionally CIRISProxy occurrences carry a
  `partner_role` / faithful-relay credential — consumers weight *"faithfully
  relays a known source,"* never *"the source is true."*
- **Licensing:** Wikipedia CC BY-SA — attribution satisfied *by construction*
  (evidence_refs + provenance chain ARE the attribution); the AI-summary layer
  carries the SA notice.
- **Scale = the substrate's first load test:** ~7M enwiki articles → that many
  article Contributions + `holds_bytes` blobs + V106 projection rows; start with
  a bounded slice (flagship subjects + one category) before the full dump.
  Tracked: CIRISProxy import pipeline (CIRISProxy#5).

## 1. Mission and the non-goal

Not another Wikipedia. A MediaWiki article is a mutable string with an edit
log; its epistemic state (who believes this, on what evidence, confidence,
since when, disputed by whom) is unrecoverable from the artifact.
KNOWLEDGE_COMMONS inverts it: **the epistemic state is the artifact**, the
article is a disposable projection.

V1 exit criterion (felt): *"I've never been able to inspect why an encyclopedia
says something so easily — and I understand why this couldn't be built on
MediaWiki."*

The mapping uses the finite constitutional catalog — three CC sections:
**CC 3.1** (95 `scores` families, Appendix A), **CC 3.3** (content-ingestion,
Appendix B), **CC 3.4** (reservations, Appendix B). No new wire primitive, no
new family; genuine gaps are CC 4.5.1 amendments (§10), never ad-hoc prefixes.

## 2. Object model

| Product concept | CEG realization |
|---|---|
| **Claim** | A *Contribution* with a **stable claim id** (`contribution_id`) that many attesters attach to; the statement TEXT is attached content (`holds_bytes:sha256`, hash-addressed), NOT the identity (hashing text makes paraphrases un-corroboratable, and resolution keys on `contribution_id` — R-C1/P-M1). Aboutness lives in **`subject_key_ids`** (the claim id, or a `canonical:{hashalg}:{hex}` for a real-world entity) — this, not `attested_key_id`, is the claim-gathering key (a world-fact claim has no subject *key*; `attested_key_id` defaults to the attester). |
| **Support / contradiction** | `scores` on `truth_grounding:{subject}` (positive corroborates, negative contradicts), `subject_key_ids` = claim id. Conflicting claims coexist as signed rows. |
| **Evidence** | `evidence_refs[]` → content-addressed `holds_bytes` blobs, `provenance:*`, `transparency_log:inclusion`. **Independence scored** (self-published down-weighted, §7). |
| **Confidence** | Never stored — composed (CC 4.4.2), displayed as a **qualitative band + n** (contributor count, `witness_diversity`, open-contradiction count), NEVER a bare high-precision % (P-H1). |
| **Witnesses** | `witness_relation` + `testimonial_witness:{kind}` (singular voice, never aggregated) + **`witness_diversity:{contribution_id}`** as the independence gate. (`n_eff`, CC 6.1.2.1.2, is a storage mass-dominance metric — NOT attester independence; it does not weight verdicts. X4.) |
| **Timeline** | `asserted_at` + the four composers: corroboration=new `scores`; development=`supersedes`+`differs_in[]`; correction=`recants` (falsity) vs `withdraws` (retraction). |
| **"Current understanding"** | Supersession is per-attester (CC 3.5.1); heads can conflict. Reader rule: the live head with the **highest composed verdict**; contradictory high-standing heads render **"contested"** (both), never a silent pick (P-M4). Who may `supersedes` whose row is bounded (a later supersedes by an unrelated key does not silently become "current" — RT-H8). |
| **Dispute / resolution** | opposite-polarity scores + `reconsideration:{grounds}` + `moderation:{allegation_type}`. `vote`/`weighted_aggregate` (NodeCore governance) are **NOT** reused for encyclopedic confidence (§11 decision). |
| **Article** | the **claim board** (§3), not synthesized prose. |

## 3. The unit of read — the claim board (RESOLVES v0.1's contradiction)

v0.1 promised both "beautiful prose" and "every sentence one-click-traceable"
over "a projection with no article-body object" — mutually exclusive (P-C1). V1:

- **The article IS a claim board**: lead claim + supporting/contradicting claims
  + evidence, **each row verbatim and individually traceable** — the unit the
  "why is this believed" trace explains, lined up by construction. Structure
  (lead selection, sectioning) is a reader-tier projection parameter.
- **Prose is a distinct labeled non-authoritative layer** ("AI summary — not
  attested") above the board; clicking a summary sentence drops into the rows.

### Ten features → substrate

| # | Feature | Realization | Handle (§5) | V1 |
|---|---|---|---|---|
| 1 | Evidence Panel | `truth_grounding` + `evidence_refs` + `witness_diversity` | `resolve_scores`/`evidence_panel` | ✅ |
| 2 | Living Articles / pending | append-only rows; local-tier drafts; `reconsideration` | `claim_timeline` | ✅ |
| 3 | Ask-the-Article | app tier over the SAME gated handles — **substrate-thin, product-substantial** (guardrailed RAG w/ a hard security property; NOT "thin" — P-H3) | §5 via pyo3 | ✅ |
| 4 | Claim Objects | §2 Claim; discussion = scores `context` | `emit_attestation` | ✅ |
| 5 | Perspectives | preset = **Policy A/B** restricted to an attester set + CC 4.4.2 mean (NOT Policy C/EigenTrust or J/media — misused in v0.1, X5) | `resolve_scores` | ✅ (2) |
| 6 | Trust Filters | caller attester predicate (§4) | `resolve_scores` | ✅ |
| 7 | Self-explaining citations | `evidence_refs` + `provenance:*` + `transparency_log:*`; **independence-scored**; card **re-runs the gate** on the referenced object | `evidence_panel` | ✅ |
| 8 | Interactive timeline | §2 row types; `rollback_detected` | `claim_timeline` | ✅ |
| 9 | Knowledge graph | subject co-occurrence — **gated per node** (unviewable-neighbor labels suppressed — RT-M2/H6) | `list_scores_for_subject` (gated) | ⚠ lite |
| 10 | Claim reputation | §2 derived | `resolve_scores` | ✅ |
| ★ | **"Show me why this is believed"** | the leak-safe composition TRACE (§6.1) | `resolve_scores(trace=true)` | ✅ iconic |

## 4. Perspectives and trust filters

```
Perspective := { policy: CC 4.4.3 A/B (V1), attester_predicate: AttesterSet, staleness }
AttesterSet := ALL
             | holders_of(dimension_prefix, min_verdict)   # V1: SINGLE non-recursive verdict level; bounded enumeration (R-H3)
             | reachable_from(key_id, scope, depth)         # "my friends" — Policy A/B over delegates_to
             | licensed_by(authority_id)                    # licensure:{authority}, CC 3.4.9 co-steward capped
             | intersection/union
```

V1 presets (honest at launch): **chronological** + **all-attesters**. The
**scientific-consensus** (holders_of `expertise`) and **legal** (licensed_by
`licensure`) presets are gated on the §0 ceremony — they return nothing until
those populations exist, and the reader renders an explicit **sparse/empty
state** ("filter leaves 0 attested claims — N excluded shown greyed"; always
show contributor count), never a blank article (P-H2/M2). A preset's **name is
an attack surface** (RT-G): it must display its resolved holder count +
`witness_diversity`, never a bare authoritative banner.

**Fail-secure floors are NON-overridable:** `prohibited:*` composes to its floor
by its `-1/-0.5-only` polarity (CC 3.1.5.4 — structural, not an overridable
4.4.2 default), and §6.1's safety gates sit beneath every perspective.

## 5. The read surface (substrate asks — CIRISPersist)

**All handles carry `caller_occurrence_key_id` and run the §6.1 stack
substrate-side** (v0.1 dropped the caller from two signatures — RT-H1/A):

1. `resolve_scores(caller, subject, dimension_or_prefix, policy, attester_filter?, as_of?, trace?)` → `ComposedVerdict { band, contributor_count, witness_diversity, open_contradictions, age_of_head, trace? }`. **`as_of` is bounded — it cannot reach content in the §6.2 hard-delete class** (RT-C2).
2. `claim_timeline(caller, subject, dimension_prefix?, window?, cursor?)` → lifecycle rows, cursor `(asserted_at, attestation_id)` (asserted_at non-unique — R-M4).
3. `evidence_panel(caller, subject, dimension)` → `{supporting[], contradicting[], witnesses[], evidence_refs[], head}` — composite that **re-runs the gate over evidence_refs/witnesses regardless of tier**.

**Honest substrate reality (v0.1 §5 was wrong — R-C1/C2/H1):**
- The flagship query is subject-centric; the subject is in `subject_key_ids`
  **JSONB**. *Re-verification note:* a subject-**filter** already exists —
  `AttestationFilter.subject_key_id` (`ceg/list/federation.rs:149`, GIN-backed
  on postgres), so realizability's "no subject-scoped handle exists" was too
  strong. What is genuinely **net-new** is (a) the composed **`resolve_scores`
  fold** (latest-wins-per-attester → polarity aggregation → policy → caps
  → diversity discount), (b) an **ordered** subject index (today's GIN is
  unordered containment), and (c) the **SQLite** subject index at all (V055's
  GIN is postgres-only; SQLite has the column + CHECK but no index → `json_each`
  scan — R-C2/M2). `claim_timeline` builds on the same.
- **Phase 1 is NOT non-breaking.** btree `(attested_key_id, dimension, …)` is
  the wrong shape (`attested_key_id` defaults to the *attester*, not the claim
  subject — verified `engine.rs:2351`; R-C1 holds). Prerequisite: a
  **normalized subject-index projection** `(subject_key_id, dimension,
  asserted_at, attestation_id)` (or a Postgres GIN-on-expression) **with a
  backfill**, + a dimension generated column (Postgres STORED; SQLite only
  VIRTUAL — R-M2), + a **GIN on `evidence_refs`** (citation lookup is an
  unindexed seq scan — R-H4).
- **The gate stack is the N+1 it derides** (R-H2): the caller-gate MUST be a
  **composite substrate op** (the #329 `ResolveEncryptionKeys` pattern — whole
  fold in the `.so`) or per-request cached, not re-fetched per handle.
- **Server-tier or deferred for V1:** `evidence_panel` composite,
  `content_rating` composition (doesn't exist in persist — X1/R-M1),
  `holders_of` recursion. Each gate owned by exactly one tier (no split-fold
  drift — RT-A/H1).

**Phase 2 (layout):** cohort-first partition (cohort = flow label = partition;
namespace = type label = key/index; state derived, tier × lifecycle, never a
mutable "trusted" flag). This is the FSD's storage triple — NOT the CC 2.3.3
wire triple (visibility × revocability × delivery — MED-7).

## 6. Cohorts and the commons

Public rows = `cohort_scope: federation`; drafts = `self`; community corpora =
`community`. Down-weight-not-delete means junk still renders, so the reader has
an **inspectable display threshold** ("512 low-confidence claims hidden —
show") as a projection parameter, consistent with fades-not-falsified (P-H4).

### 6.1 Universal safety gating — DEFENSE IN DEPTH (NORMATIVE)

v0.1's "gated by construction" was render-tier only; the content plane was
reachable beneath it. v0.2 gates at **every tier a byte or inference escapes:**

**Tier A — at-rest + replication.** Flagged classes (`content_rating:adult/
mature`, `cw_class` NSFW set, infohazard-flagged, `prohibited:*`-adjacent) have
their federation-scope payloads **encrypted at rest and suppressed from open
replication** (CC 5.2 self/family structural-invisibility extended to flagged
federation classes). **Hard-illegal classes (CSAM) are NOT admissible at
`federation` cohort at all** — world-replicable = world-readable-raw on an
untrusted replica, which no render gate can undo (RT-C1). They live only under
custody-gated scopes and the §6.2 hard-delete class.

**Tier B — content fetch.** `holds_bytes`/Edge `ContentFetch` and every
`evidence_refs` dereference run the caller gate. `evidence_ref` **URIs**
(arbitrary off-substrate — infohazard/doxxing/CSAM-locator smuggling + SSRF)
are **non-dereferenceable without the gate**; V1 prefers `evidence_refs = hash
+ holds_bytes` only (RT-C3/B1).

**Tier C — render.** Every §5 handle + `list_scores_for_subject` + graph node
labels run: `age_band(caller)` (CC 3.4.11), infohazard view-consent (CC 4.5.13
via `resolve_scoped_consent`), `content_rating`/`cw_class` band-gating
(CC 3.3.12), moderation-duty (`moderation:*`+`reachable_under_scope`),
`prohibited:*` floor. Gated-neighbor **labels suppressed, not just panels**
(RT-M2).

**Tier D — the AI.** The agent answers ONLY from the caller-scoped projection,
its read scope **provably ≡ the caller's** (never broader). A **compose-then-
gate + synthesis-level infohazard check** covers the mosaic case (RT-C2/B5).
Claim text is **untrusted input** (indirect prompt injection is in-band); the
agent cannot dereference ungated refs nor emit attestations from a reader
session.

**Reactive-gate window (RT-H4):** ratings/flags are attestations, so *novel*
content is unrated → would render ungated. V1 policy: **unrated content is
treated as its most-restrictive plausible class for `Unknown`/anonymous
callers** until rated — fail-closed in the publish→first-rating gap, not
fail-open.

**Correct gate citations (v0.1 errors — X1/X3):**
- **Age = CC 3.4.11** (NOT "presumption-of-sovereignty" — that's the CC 3.4.12
  *capacity* default, inverted). Protective ladder: witness `age_assurance:*`
  OUTRANKS subject `age_self_declared:*` (read-union, highest); **absence →
  None → BLOCKED from adult classes.** Commons policy pins the residue:
  **anonymous / no-occurrence-key / Unknown callers are treated protectively
  (minor) for flagged classes** — unwitnessed "I'm 18" does not unlock adult
  content; `is_minor()` fail-secure wins ambiguity. `age_band`-about-a-PERSON
  is **self-cohort only**, never a federation-readable panel (else it is a
  minor-status doxxing primitive — RT-D).
- **Content ratings = `content_rating:{scheme}:{rating}`** (CC 3.3.12 catalog:
  `signed`, certifier confidence in polarity). *Re-verification note:* the
  fidelity challenger called this open-emit with a fabricated §11.5.3 — both
  wrong. Persist **enforces trusted-publisher-only emission** via its
  reserved-prefix rules (`admission.rs` `default_reserved_prefix_rules`,
  `pattern_prefix: "content_rating:"`), and **§11.5.3 is a real CEG 0.3
  governance section** (hash-database operator policy). The catalog row is
  emitter-open; the *reservation* lives in CEG §11.5.3 + §8.1.10. The
  **composition into a per-caller gate is SPECIFIED** (CEG §8.1.10 Layer 2
  content_class+content_rating, Layer 3 age-assurance) but **not yet
  implemented in persist** — net-new *code*, not net-new spec (server-tier V1).

**The trace is leak-safe (RT-C/H3):** withheld rows are excluded from **both the
shown text AND the composed math** (no cross-band verdict-differencing; no
label-bearing placeholder). Withheld **existence** is reported only coarse/
noised below a threshold, never exact-count + timing + per-dimension. The trace
proves a gate *class* fired, not how many rows of what. `hard_case:
watchlist_match` emissions are **not federation-cohort** (else a surveillance
side channel — RT-G).

### 6.2 The two erasure classes (NEW — RT-C2)

The red-team argued append-only cannot erase CSAM (so `as_of` re-exposes
takedowns). **On re-verification against the code this is wrong** — the
substrate already has the two-layer erasure model, and it is exactly the right
shape. Append-only governs the **manifest/attestation tombstone** layer; the
**content-symbol layer is hard-deletable**:

- **Fade (tier demotion):** `evict_fountain_content_to_tier` / consent-decay /
  disk-pressure — symbols retained, demoted; `as_of`-reachable.
- **Hard-delete (erasure):** **`evict_fountain_content_hard_delete(content_id,
  corpus_kind)`** (trait `store::backend`, all three backends) — drops **ALL**
  fountain symbols unconditionally, **never consulting `retention_priority`**
  (revocation/takedown dominates rarity — a high rarity score can never
  resurrect erased content; the §8.1.11.3 deletion-SLA path). The bytes are
  gone and are **unrecoverable at any `as_of`** because `as_of` folds
  *attestation metadata*, not fountain symbols; `get_fountain_content` then
  returns **`EnvelopeOnly`** — the manifest survives as un-falsifiable
  provenance ("a thing with hash X existed and was taken down"). This is the
  correct CSAM posture: erase payload, keep a non-repudiable tombstone.
- **Drivers already wired:** consent-revoke →
  `evict_fountain_content_by_consent` (resolves `ConsentState::Revoked` →
  hard-delete); legal/CSAM → the `takedown_notice` subject_kind with
  **`LegalBasis::{NcmecCsam, PerceptualHashCsam, GifctCip, CourtOrder}`** (CEG
  0.3 §5.6.8.4 / §11.4), and the erasure transaction stamps `erased_at` +
  tombstones detection events.

So there is **no constitutional gap** and **no amendment** — the FSD's job is
to *wire these existing primitives to the reader/claim path* (§10): a
`federation`-scope claim whose content is hard-deleted renders `EnvelopeOnly`
(tombstone: "withdrawn under basis Y"), never the bytes, at any `as_of`. Only
the layout choice stands: hard-illegal classes are not admissible at
`federation` cohort in the first place (Tier A), so erasure is bounded to
custody-gated stores rather than chasing bytes across untrusted replicas.

## 7. Integrity and abuse (anti-Sybil on the RIGHT plane)

The pivotal finding (RT-C4/E): the Evidence Panel headline composes open-emit
`truth_grounding` scores by **mean** (CC 4.4.2 `signed`), but `witness_diversity`
/median gate the `vote`→`weighted_aggregate` **finality** plane the panel never
routes through. A brigade of M sock keys posting corroborating scores
(open-emit, **no bond**, cost = M key admissions) moves the mean; the diversity
gate never fires. v0.2:

- **The panel headline aggregation applies a `witness_diversity` gate + diversity
  discount to `truth_grounding` itself** (not just the vote plane); low-diversity
  attester sets cap the displayed band. `n_eff` is annotation, never the weight.
- **A bond/stake precondition** (`bond_posted`) to emit federation-scope
  `truth_grounding` on flagship subjects.
- **`expertise:{domain}` gets a single-source cap** like `licensure`'s CC 3.4.9
  ≤0.5 (else a cell cross-attests its own expertise, inflating the vote
  multiplier uncapped — RT-H7); `credits:substrate_building` accrual is brought
  under the same diversity discipline and its attester specified (self-attested
  = laundering pipe — RT-H7/M4).
- **Diversity attributes are attested, not self-declared** (jurisdiction/org/
  software-stack/cell-expertise) — else a ring varies declared attributes to
  inflate `witness_diversity`, defeating the gate it leans on (RT-M4).
- **`judge_model:verdict:{model_id}` bound to execution provenance** (a
  `provenance:*`/`attestation:agent_integrity` that the verdict came from that
  build) + org-`witness_diversity` before any "AI consensus" framing (open-emit
  free-text `model_id` otherwise mints "seven independent models rated PASS"
  from one key — RT-H5).
- **`withdraws` rule-3 canonical-hash proxy requires proof-of-CONTROL** (a live
  `delegates_to` chain to the canonical subject with `scope ⊇
  {consent_revocation}` — CC 2.4.1.1 rule 3, verified), not knowledge of the
  public preimage; **plus a public-interest carve-out** so consent-withdrawal-
  of-content-about-self cannot suppress true adverse public-interest claims
  (RT-H6; the codebase's #389 blanket-revoke history is the cautionary case).
- **`recants` vs `withdraws` cannot be self-selected to launder reputation:** a
  debunked-then-withdrawn contradiction does not exit the open-contradictions
  count as a good-faith retraction; reputation composition distinguishes
  contradiction-then-withdraw from voluntary withdraw (RT-M1/F).
- **Citation independence scored:** `evidence_refs` resolving to the claiming
  key's own custody are down-weighted; a ref pointing at a self/family
  `holds_bytes` the author serves out-of-band (unscannable by the watchlist
  seam) is flagged, not laundered as "well-sourced" (RT-M3/F).
- Unchanged/correct: detector dims (`correlated_action`/`distributive`/
  `ratchet:flag`) aggregate by **median** (the five coherence detectors are
  `signed`→mean — LOW-9); flags lower confidence never delete; `slashing`
  WA-quorum-gated, unreachable from `ratchet`/`detection` alone; conduct vs
  content lanes separate; `judge_model` attributed/filterable/never-silent.

## 8. V1 cut

Ship: §0 seed + write path · claim-board reader + labeled AI-summary · Evidence
Panel (gated) · Ask-the-Article (guardrailed RAG + gate-equivalence &
injection tests) · Living timeline · trust filters + 2 honest presets w/
sparse-state UX · leak-safe "why" trace · knowledge-graph-lite (gated).
Defer: expertise/licensure presets (gated on §0), collaborative editing, merge
tooling, governance workflows, graph explorer, search ranking.

## 9. Namespace catalog — the finite constitutional catalog (3 CC sections)

- **Appendix A — CC 3.1 `scores` (95):** claim/witness/dispute/evidence/trust
  kit (`truth_grounding`, `witness_diversity`, `testimonial_witness`, `vote`/
  `weighted_aggregate`, `reconsideration`/`moderation`/`prohibited`/`watchlist`,
  `judge_model:verdict`, `holds_bytes`/`provenance:*`/`transparency_log:*`).
- **Appendix B — CC 3.3 content-ingestion + CC 3.4 reservations:** the safety
  surface §6.1 runs on — `consent:*` (3.3.1), `content_class`/`content_rating`/
  `cw_class` (3.3.12), the `age_assurance`/`age_self_declared` ladder + protective
  gate (3.4.11), `capacity_assurance` (3.4.12), reservation classes. **NOT in the
  95** — v0.1's "95 = complete catalog" was false (X2). Zero new families still
  holds; the catalog is these three sections together.

## 10. Gaps and asks

| Repo | Ask | Phase |
|---|---|---|
| CIRISPersist | `list_scores_for_subject` + `resolve_scores` + `claim_timeline` (net-new); subject-index **projection + backfill**; dimension generated column; GIN on `evidence_refs`; caller-gate as a composite op | V1 |
| CIRISPersist | at-rest encryption + replication-suppression for flagged classes (§6.1-A); cohort-first partition | V1-safety / post-V1 |
| CIRISServer | perspective presets; `evidence_panel` composite; `content_rating`/`content_class` per-caller **composition gate** (net-new); delete Composer client-folds onto `resolve_scores` | V1 |
| CIRISLens/GUI | claim-board reader + AI-summary + panel + timeline + sparse-state filter + display threshold | V1 |
| CIRISAgent | Ask-the-Article guardrailed RAG; gate-equivalence + prompt-injection tests | V1 |
| CIRISPersist | **wire the EXISTING hard-delete** (`evict_fountain_content_hard_delete` / `_by_consent` / `takedown_notice` + `LegalBasis`) to the reader/claim path so a hard-deleted claim renders `EnvelopeOnly` (§6.2) — NOT an amendment; the primitive already ships | V1-safety |
| CIRISConstitution (editorial) | reconcile "83/8" vs 95/9; flesh the 10 UNDERSPECIFIED + 4 near-thin `conscience:*` (Appendix A); author Appendix B (CC 3.3/3.4 safety surface); reconcile the CC 3.3.12 catalog row (emitter-open) vs the CEG §11.5.3 content_rating trusted-publisher reservation persist enforces | editorial |

## 11. Decisions escalated to the operator

1. **Unit-of-read:** claim-board confirmed (§3). Non-authoritative AI-prose
   summary layer IN the V1 demo, or deferred?
2. **Encyclopedic `truth_grounding` × Credits loop:** should commons claims
   accrue NodeCore governance Credits? **Recommend: no** — decouple, else
   encyclopedic volume mints governance currency (fidelity LOW-8).
3. **Write path:** confirm V1 ships single-user claim authoring.

(v0.2 had a 4th decision — a "hard-delete amendment." **Withdrawn on
re-verification:** the substrate already ships `evict_fountain_content_hard_delete`
+ `takedown_notice`/`LegalBasis`; §6.2 is now a wiring task, not an amendment.)

## Appendices
- **Appendix A** — 95 CC 3.1 `scores` families: FSD-005_APPENDIX_A_namespaces.md
- **Appendix B** — CC 3.3/3.4 safety surface: *to author (the §6.1 dependency).*
- **Review Log** — 4-lens review + dispositions: FSD-005_REVIEW_LOG.md
