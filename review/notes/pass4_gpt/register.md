# The Evidence Register (ciris_constitution-1.0-rc11-register.pdf, 131 pages)

**Care score:** 5  (1 = ship as is, 5 = needs a rewrite pass before 1.0)  
**One-line verdict:** The register contains incompatible security rules, unresolved legal-compliance claims and stale annex text that undermine its function as the constitution’s audit surface.

## Strengths
- The evidence-reading instructions distinguish artifact existence from proof of a prose claim and distinguish definitions, model-conditioned theorems, measurements and external citations (pp. 18–19).
- The research summary identifies its post-hoc contrast, missing comparison arm and limits on transfer; the corresponding register row remains staged (pp. 53–54, 130).
- The generated register separates established, staged and normative claims, including implementation work still outstanding near the end of the volume (pp. 59, 127–130).

## Weaknesses
- **The printed register omits promised audit identifiers.** Page 1 promises “the commit it was checked at,” but the table supplies only CC section, claim, evidence and status. Neither claim IDs nor repository pin commits appear alongside the rows; a reader cannot reconstruct the promised pinned audit trail from this volume alone (pp. 1, 59–131).
- **Scope labels conflict with their contents.** “This whole section is informative” precedes a normative C2PA requirement; annexes supposedly bind adopting deployments, “never … conformance,” yet Annex F says “No CIRIS-conformant system…” (pp. 12, 15, 21, 26).
- **The concerns ledger is not consistently current.** “These are settled” includes “PARTIALLY CLOSED,” “ACKNOWLEDGED” and “STAGED-STREAMING”; the deferred list includes “No longer deferred” and committed items (pp. 10–11).
- **History, attribution and marketing remain in operative prose.** Examples include “Historically, projects unifying that many layers fail,” “CEG’s moat,” “the differentiated story,” “Cheapest win,” “the lake’s binding-fusion correction,” and “before the language-guidance split” (pp. 7, 13, 15, 96, 104). Annexes repeatedly explain how MH passages generated rules rather than simply stating the rules (pp. 24–53).
- **Comparative claims violate the house rule.** Examples include “outperforms token-weighting,” “never as protocol substrate,” “C2PA has no consent architecture, no revocation,” the SCITT algorithm comparison, and claims about other vendors’ absent safeguards (pp. 7, 11, 14, 16, 19–20). The dated 2026 reports are unverifiable from here, not presumed fabricated.
- **Several empirical numbers lack a visible measurement source.** “50%–5.8× of the null,” “k_eff ≈ 7 ± 2,” and a model “lying 45% of the time” have no identifiable report with sample, floor and error bar in this volume, despite page 19 requiring those details (pp. 8, 19, 32).
- **Stale references and terminology survive.** The CEP requires `controller_si_threshold`, absent from the current controller definition; Annex B §9 is cited for appointment, recusal and rotation although it concerns oversight/removal; “NIST SP 800-218 (SLSA)” conflates SSDF with SLSA (pp. 21, 36, 45, 52–53).
- **Banned vocabulary appears in printed identifiers:** `test_drain_requests_graceful_shutdown_only` and `test_negotiation_timeout_forces_graceful_shutdown` (pp. 62, 126). Resolve this without silently breaking evidence pointers.

## Opportunities
- Reconcile duplicate statements of the same rule before copyediting: halt-state effects, stream-key derivation, membership consent, capacity-scoring consent and irreversible-action handling each have conflicting formulations (pp. 26–28, 73, 84–86, 88, 95, 112, 116).
- Render the existing claim IDs and pinned repository commits, and make the distinction between “artifact backed” and “whole claim implemented” explicit beside mixed established/staged rows (pp. 59–131; examples on pp. 84, 107, 122–123).
- Apply the annexes’ existing “operational targets” label locally to benchmark suites, dashboards and workflows described in present tense; reserve implementation assertions for rows that actually support them (pp. 21, 34–42, 54–57).
- Consolidate repeated MH quotations into informational grounding references, leaving the existing obligations and thresholds in direct English with consistent RFC 2119 wording (pp. 24–53).
- Replace legal-sufficiency language with the document’s existing engineering-correspondence qualification until the specified legal review is linked (pp. 23, 43–57).

## Threats
- **An implementer can choose opposite halt behavior.** One row says “a latched halt is NotRooted until lifecycle:active”; the next page says the halt “moves no T8 state” (pp. 85–86).
- **The stream-key contradiction crosses a cryptographic boundary.** One row says “the exporter secret is never wrapped”; another says “the MLS exporter secret is the epoch DEK” and is wrapped for kept streams (pp. 112, 116).
- **Membership consent has incompatible universal statements.** “Nobody joins … without their own consent” conflicts with node members being “seated without an acceptance.” The later `open:self_admit` rule also needs reconciliation with “no key is seated on rows it alone signed” (pp. 73, 84, 112).
- **Irreversible-action handling alternates between prohibition and authorization.** “Safe-state is the only permissible outcome under any condition” conflicts with the KPI for “100 % of irreversible actions under confirmed human authorization” and hardware examples permitting activation (pp. 26, 28–29).
- **A regulator could quote compliance assurances against the disclaimer.** “Discharges EU AI Act Art. 50(2),” “one set of controls suffices,” and GDPR explanation rights “satisfied by storing” a reasoning trace exceed the pending-review posture (pp. 15, 23, 43, 57). Specific errors compound this: “72 hours (GDPR standard)” for objections, DSA “Art. 28b,” and AI Act Article 13 labelled “Universal” (pp. 46–48, 53).
- **The register’s confidence can outrun its own evidence discipline.** “Controlled, verifiable destruction” is asserted in the glossary while R9 acknowledges an unverifiable adversary/side-information limb; “open 0” is printed without explaining how such acknowledged gaps are represented (pp. 3, 8, 59). Likewise, the generated summary’s measured research contrast points to a staging ticket rather than a visible benchmark artifact (pp. 54, 130).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 112, 116 | contradiction | Derived per-stream DEK with exporter secret “never wrapped” versus exporter secret itself used as DEK and wrapped. | Select the governing formulation and update both claim text and evidence binding together. |
| 2 | 85–86 | contradiction | Halt makes T8 `NotRooted` versus halt “moves no T8 state.” | Remove the superseded invariant and align the model claim with the current halt rule. |
| 3 | 73, 84, 112 | contradiction | Universal acceptance/two-signer membership language conflicts with node seating and public self-admission. | State the existing exceptions and their exact scope in each affected summary. |
| 4 | 88, 95 | contradiction | Consent scope comes from the grant’s own `scope`; `consent:scope:*` is “descriptive only,” yet the capacity gate requires a “consent:scope:analyze grant.” | Use the canonical grant shape and terminology consistently; confirm which gate the pointer establishes. |
| 5 | 26, 28–29 | contradiction | A4 irreversible actions must always remain in safe-state, but KPIs and hardware examples contemplate authorized execution. | Obtain a steward ruling on the intended boundary, then reconcile prohibition, KPI and implementation notes. |
| 6 | 15, 23, 43–57 | overclaim | Pending legal review coexists with assertions that controls discharge or satisfy law, plus incorrect legal references. | Correct article references and deadlines; retain engineering mappings without declaring legal sufficiency. |
| 7 | 1, 59–131 | other | Promised checked-at commits and stable claim identifiers are absent from the printed register. | Include existing claim IDs and pin information in the generated output or a compact printed pin table. |
| 8 | 21, 54–57 | numbering | Missing section numbers and Annex J’s new top-level sequence retain old subclause numbering and references. | Rebuild numbering and resolve references against the resulting sequence. |

## Rendering
- Assessment is limited to the supplied page-by-page rendition; page-edge clipping, glyph appearance and table overflow cannot be reliably verified without PDF images.
- Literal Markdown link syntax survives: `[evidence_refs[]](part_2_the_grammar.md)` (p. 13).
- Two literal `<!– stale-ok –>` editorial markers are printed (p. 20).
- The Nextgov URL appears incomplete, ending at `/2026/09` before continuing with `house-unveils...`; check the source link and PDF wrapping (p. 20).
- Section 8.6.4 announces namespace stewards but provides no list. Numbering jumps from 8.6.4 to 8.8, then begins annexes at 8.8.2 and skips 8.8.4 without explanation (pp. 21–22).
- Annex J headings 7–11 contain subsections numbered 1.1–5.3; references such as “see 5.3” consequently point into an obsolete numbering scheme (pp. 54–57).
- Identical evidence pointers are printed twice within individual rows on pp. 67–68, 91–92, 101, 103, 107, 113, 115, 117–118 and 120–123. Deduplicate the generated evidence lists rather than treating repeated anchors as additional support.

## Effort estimate
Allow 32–48 hours of editing and regeneration, including a legal-reference pass; numbering, duplicate pointers and rendering cleanup are mechanical, but the security contradictions and scope boundaries require steward rulings.

<!-- model openai/gpt-6-astra-pro; 131 pages; prompt_tokens 308358; completion_tokens 5773; 66s -->
