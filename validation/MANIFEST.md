# CIRIS Constitution 0.1 — Validation Manifest (CERTIFIED)

Final per-chapter source-fidelity validation of CC 0.1 vs its CEG + Accord sources, after the consolidation waves.

## Certified scoreboard

| Metric | Result |
|---|---|
| Verdicts | **19 ACCEPT · 9 ACCEPT-WITH-FIXES · 0 REJECT** |
| C0 fidelity (intent preserved) | **28/28 PASS** |
| C1 byte-exact (CEG wire) | **18/18 PASS** |
| C2 superior to source | **27/28 YES** |
| Issues | 52 (0 blockers) — all remaining are cosmetic minors |

Trajectory: wave 0 (verbatim) 20 REJECT → wave 1 (woven) 1 REJECT → wave 2 + RFC-fix **0 REJECT**.

**CC 0.1 is, by its sources' own validation rubric, byte-exact to CEG, intent-faithful to the Accord, and clearer than either input.**

## Remaining cosmetic minors (post-0.1 polish)

- [major] §18 `8.4` (C0): Source 'informative ([§0.1.1])' → CC '([CC 2.5])'. §0.1.1 maps to decimal 2.6.9.1 (normative-vs-informative); CC 2.5 is 'The reasoning grammar — the eight axes'
- [major] §18 `8.4.1` (C0): Source 'the [§0.9] JCS freeze exists to close' → CC '[CC 2.5]'. §0.9 maps to decimal 2.6.1 (envelope-canonicalization / JCS). CC 2.5 is the reasoning grammar. T
- [major] §18 `8.4.1` (C0): Source '([§5.2.1] records this decision)' → CC '([CC 2.4] records this decision)'. §5.2.1 maps to decimal 3.1.2.1 (provenance canonical-bytes). CC 2.4 is 'The p
- [major] §18 `8.4.1` (C0): Source 'MLS / TreeKEM ([§10.5.3])' → CC '[CC 3.1.5]'. §10.5.3 maps to decimal 5.1 (epoch keying + cascade). CC 3.1.5 is 'CIRISAgent — Accord principles + DMA…' 
- [major] §18 `8.4.1` (C0): Source 'RFC 6962 / 9162 transparency logs ([§10.3])' → CC '[CC 3.1]'. §10.3 maps to decimal 5.3.1 (STH cosigning + witness directory). CC 3.1 is 'The dimension 
- [major] §18 `8.4.1` (C0): Source 'SLSA (provenance:slsa:{level}, [§5.2])' → CC '[CC 2.4]'. §5.2 maps to decimal 3.1.2 (CIRISVerify attestation ladder). CC 2.4 is the 1+4 primitive set. W
- [major] §18 `8.4.1` (C0): Source 'bridge via [§5.6.8.12] settlement' → CC '[CC 2.4] settlement'. §5.6.8.12 maps to decimal 3.3.10 (settlement subject_kind). CC 2.4 is the 1+4 primitive s
- [major] §18 `8.4.2` (C0): Source 'the [§5.6.8] multimedia / federation_blobs boundary' → CC '[CC 2.4]'. §5.6.8 maps to decimal 3.3 (content-ingestion prefixes). CC 2.4 is the 1+4 primiti
- [major] §18 `8.4.2.1` (C0): Source 'the [§5.6.8.8.2] key-separation discipline generalizes' → CC '[CC 2.4]'. §5.6.8.8.2 maps to decimal 3.3.6.1 (encryption_pubkeys KEM binding). CC 2.4 is 
- [major] §18 `8.4.3` (C0): Source 'Keep the [§10.3] RFC 6962 abstraction' → CC '[CC 3.1]'. §10.3 maps to decimal 5.3.1 (STH cosigning). CC 3.1 is 'The dimension namespace'. Wrong target (
- [major] Book VII `7.4.14–7.4.19` (C2): Six empty duplicate chapter-heading stubs. Each of 7.4.14–7.4.19 is a `### 7.4.x` subsection whose only body is a repeated bare `## Chapter N: …` H2 heading wit

_Notable: the validation also surfaced two latent SOURCE bugs faithfully carried into CC — the CEG community at-rest-encryption table contradiction (filed CIRISRegistry#99) and a BCP-47→BCP-14 URL typo in CEG §0.4._

## Per-chapter

- **Book 0   ** ACCEPT (C0 PASS·C1 NA·C2 YES·r5)
- **Book I   ** ACCEPT (C0 PASS·C1 NA·C2 YES·r5)
- **Book II  ** ACCEPT-WITH-FIXES (C0 PASS·C1 NA·C2 YES·r4)
- **Book III ** ACCEPT (C0 PASS·C1 NA·C2 YES·r4)
- **Book IV  ** ACCEPT (C0 PASS·C1 NA·C2 YES·r5)
- **Book V   ** ACCEPT (C0 PASS·C1 NA·C2 YES·r5)
- **Book VI  ** ACCEPT (C0 PASS·C1 NA·C2 YES·r5)
- **Book VII ** ACCEPT-WITH-FIXES (C0 PASS·C1 NA·C2 NO·r3)
- **Book VIII** ACCEPT (C0 PASS·C1 NA·C2 YES·r5)
- **§0       ** ACCEPT-WITH-FIXES (C0 PASS·C1 PASS·C2 YES·r4)
- **§1       ** ACCEPT (C0 PASS·C1 PASS·C2 YES·r5)
- **§10      ** ACCEPT (C0 PASS·C1 PASS·C2 YES·r5)
- **§11      ** ACCEPT (C0 PASS·C1 PASS·C2 YES·r5)
- **§12      ** ACCEPT (C0 PASS·C1 PASS·C2 YES·r5)
- **§13      ** ACCEPT (C0 PASS·C1 PASS·C2 YES·r5)
- **§14      ** ACCEPT (C0 PASS·C1 PASS·C2 YES·r5)
- **§15      ** ACCEPT (C0 PASS·C1 PASS·C2 YES·r5)
- **§17      ** ACCEPT (C0 PASS·C1 NA·C2 YES·r4)
- **§18      ** ACCEPT-WITH-FIXES (C0 PASS·C1 PASS·C2 YES·r4)
- **§19      ** ACCEPT (C0 PASS·C1 PASS·C2 YES·r5)
- **§2       ** ACCEPT (C0 PASS·C1 PASS·C2 YES·r5)
- **§3       ** ACCEPT (C0 PASS·C1 PASS·C2 YES·r5)
- **§4       ** ACCEPT-WITH-FIXES (C0 PASS·C1 PASS·C2 YES·r5)
- **§5       ** ACCEPT-WITH-FIXES (C0 PASS·C1 PASS·C2 YES·r5)
- **§6       ** ACCEPT (C0 PASS·C1 PASS·C2 YES·r4)
- **§7       ** ACCEPT-WITH-FIXES (C0 PASS·C1 PASS·C2 YES·r4)
- **§8       ** ACCEPT-WITH-FIXES (C0 PASS·C1 PASS·C2 YES·r4)
- **§9       ** ACCEPT-WITH-FIXES (C0 PASS·C1 PASS·C2 YES·r4)

## Addendum — 0.8 Book IX migration (2026-07-01)

Book IX was not part of the CC 0.1 validated set (it had never been migrated). The CC 0.8 migration
into **Part VI (CC 6.2)** was given its own per-chapter validation under this same skeptical rubric,
comparing the migrated F-form engineering tier against the pinned Accord 1.3-RC2 source
(`accord/11_book_IX.md` + `90_formulas.md`). The first pass returned **ACCEPT-WITH-FIXES** (4 bounded
C0/C2 defects: an `r` "correlation radius" mischaracterization, a dropped `λ ≈ 2r`, an ambiguous
"convex feasible region", and a dropped J-as-dimensionless-cost-index guardrail); all four were
corrected and a re-validation confirmed **ACCEPT**.

- **Book IX** ACCEPT (C0 PASS·C1 NA·C2 YES·r5) — migrated to CC 6.2; retracted universal-scale
  material (grace / joint-backward pass) confirmed absent.