# The Reader’s Policies (ciris_constitution-1.0-rc12-policies.pdf, 36 pages)

**Care score:** 3
**One-line verdict:** Substantively rigorous and free of banned words or historical attribution, but needs a targeted editing pass to resolve two direct contradictions on delegation depth and trust-root attachment, fix clipped tokens, and replace design-review shorthand with constitutional prose.

## Strengths
- Clear cryptographic and structural boundaries across the three privacy tiers (self/family, Community, Commons), with explicit rules for DEK rotation and forward secrecy on member removal (pp. 7–8, 18–19, 27).
- Exact deterministic canonicalization and JCS signing member-set definitions for the Self-at-login ceremony (`consent:partnership_grant:v1`, `delegates_to`, `transport_destination`) (pp. 25–26).
- Precise separation of co-self visibility from network agency, backed by a wire-checkable `infra:*` vs. `agency:*` scope split (pp. 21–24).
- Zero occurrences of the banned words (`humane`, `dignified`, `graceful`, `farewell`, `"last word"`), and no ticket links, dates on rules, or comparative claims against external projects.

## Weaknesses
- Clipped monospace token running off the right margin in 4.4.3.11: `"(attestation:regi"` instead of `"(attestation:registry_consensus"` (p. 35).
- Unexplained internal architecture shorthand in prose: `"Why this is still 1+4."` (p. 17) and `"1+4 preserved —"` (pp. 23, 34). Neither `"1+4"` nor its referent is defined in this volume.
- Internal repository/service component names (`Verify`, `Registry`, `NodeCore`, `lenscore_detector`) used as proper nouns in normative rules without definition in this volume: `"the JCS contract Verify hybrid-signs"` (p. 25), `"Registry owns these member sets (this section); Verify computes JCS(...)"` (p. 26), `"each NodeCore external_content sub_kind"` (p. 18), `"lenscore_detector reserving detection:*"` (p. 34).
- Missing preposition in 4.1.4 table: `"The recants distinction matters CC 2.4.1.3"` (p. 3).
- Missing space after colon in code block in 4.4.3.2.5: `"cohort_scope:community"` (p. 11).
- Unwrapped long lines in code blocks in 4.4.3.5.2 (`watch_sla`) and 4.4.3.5.3 (`ratified_pair`) force ugly mid-expression line breaks in the rendered output (p. 29).

## Opportunities
- Expand or replace the three `"1+4"` references (pp. 17, 23, 34) with plain English ("one structural primitive plus four envelope/scope mechanisms") so the volume stands alone for a reader who does not know the internal design slogan.
- Replace internal module names (`Verify`, `Registry`, `NodeCore`) on pp. 18, 25–26 with standard constitutional roles (`the verifier`, `the schema`, `the node`) to keep the text implementation-independent and plain-English.
- Reconcile the pseudocode in 4.4.3.2.4 (`resolve_community`, p. 9) and 4.4.3.4.4 (`resolve_family`, p. 27), which still says `.where(supersedes chain -> latest non-superseded)`, with 4.4.3.2.3 (p. 8) and 4.4.3.4.2 (p. 19), which state that a membership change is chained by `prev_head_digest` and is `"never a single-signer supersedes Contribution"`.

## Threats
- **Contradiction on whether a consumer can raise the delegation depth cap above 5:** Page 2 (4.1.1) states that `"Consumer policy MUST cap traversal depth at 5 hops by default (configurable)"` and `"A substrate MAY additionally clamp any caller-requested depth at an absolute ceiling; the ceiling bounds the walk, it does not raise the default"`. Page 15 (4.4.3.2.8.C) states that an affiliation `hierarchy` supports `"a configurable depth cap (> the CC 4.1.1 default-5 for deep secretariats)"`. Page 1 (What it promises) simultaneously promises that `"only a grant-scoped delegation from the owner confers issuance, within the depth cap and the yearly term."` An implementer cannot tell whether 5 is a consumer-overridable default or whether a substrate ceiling blocks deep secretariats.
- **Contradiction on how a consumer attaches a trust root (`delegates_to` vs. `trust:accepts:v1`):** Page 33 (4.4.3.8 item 3) states: `"A consumer trusts one by hanging delegates_to(user → root, [infra:attest, infra:serve]) off the base"`. Page 2 (4.1.1 table, row 3) states that the node->root acceptance edge is `"a trust:accepts:v1 acceptance edge (CC 3.2 T3, node → root)"` which `"is outside the cycle check in either arrival order; a capability delegates_to closing the same pair is still refused"`. If the root delegates capability to a node/user and the user attaches the root using `delegates_to(user → root, [infra:attest, infra:serve])` per p. 33, the substrate cycle check on p. 2 will reject it as a cycle on the capability `delegates_to` graph.
- **Contradiction between `resolve_community` pseudocode and `resolve_member_transport` comment:** Page 9 (`resolve_community`) returns all `{m.key_id for m in latest.envelope.members}` without checking founder quorum separately unless required by `consensus_protocol`. Page 10 (`resolve_member_transport`) calls `members = resolve_community(C, now) // (a) above; founder-quorum verified`, even though item (a) on p. 10 specifies that founder-subset evaluation applies only `"for cohort_subkind: infrastructure (CC 3.2)"`, not for all communities.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 2, 33 | contradiction | Page 33 says a consumer attaches a root via `delegates_to(user → root, [infra:attest, infra:serve])`, whereas p. 2 says the node→root acceptance edge is `trust:accepts:v1` and that `"a capability delegates_to closing the same pair is still refused"` as a cycle. | Align 4.4.3.8 (p. 33) with 4.1.1 (p. 2) and CC 3.2 T3 by specifying whether root attachment uses `trust:accepts:v1` or `delegates_to`. |
| 2 | 1, 2, 15 | contradiction | Page 1 promises issuance stays `"within the depth cap"`, p. 2 says `"the ceiling bounds the walk, it does not raise the default"` (5 hops), and p. 15 allows `"a configurable depth cap (> the CC 4.1.1 default-5 for deep secretariats)"`. | Clarify in 4.1.1 and 4.4.3.2.8.C whether the charter/substrate ceiling can exceed 5 hops for `affiliations` hierarchies and how that interacts with the p. 1 promise. |
| 3 | 35 | rendering | In 4.4.3.11, the inline code token `(attestation:registry_consensus` is clipped at the right margin to `(attestation:regi`. | Allow line breaking after colons/underscores in inline `\texttt` or rephrase the line so the token does not overflow. |
| 4 | 8, 9, 19, 27 | unclear rule | Sections 4.4.3.2.3 (p. 8) and 4.4.3.4.2 (p. 19) state roster changes chain via `prev_head_digest` and are `"never a single-signer supersedes Contribution"`, but `resolve_community` (p. 9) and `resolve_family` (p. 27) still query `.where(supersedes chain -> latest non-superseded)`. | Update the `resolve_community` and `resolve_family` pseudocode on pp. 9 and 27 to walk the `prev_head_digest` roster lineage rather than `supersedes`. |
| 5 | 17, 23, 34 | editorializing | Unexplained internal shorthand `"Why this is still 1+4"` (p. 17) and `"1+4 preserved"` (pp. 23, 34) appears without definition in this volume. | Replace `"1+4"` with explicit prose ("the five structural primitives of CC 2.4") or remove the slogan. |
| 6 | 18, 25, 26 | stale | Internal codebase component names `NodeCore` (p. 18), `Verify` (pp. 25, 26), and `Registry` (p. 26) are used as normative actors without definition. | Replace `Verify` and `Registry` with constitutional terms (`the verifier`, `this specification`) and drop `NodeCore`. |
| 7 | 10 | contradiction | In 4.4.3.2.4.1, item (a) says founder-subset evaluation is for `cohort_subkind: infrastructure`, but item (b) comments `resolve_community(C, now) // (a) above; founder-quorum verified` for any community `C`. | Change the comment in `resolve_member_transport` (p. 10) to `// (a) above; consensus_protocol verified (founder-quorum for infrastructure)`. |
| 8 | 3 | other | Missing preposition in 4.1.4 table: `"The recants distinction matters CC 2.4.1.3"`. | Change to `"The recants distinction matters per CC 2.4.1.3"`. |

## Rendering
- Page 35 (4.4.3.11): Overfull line clips inline monospace token to `(attestation:regi` at the right margin (missing `stry_consensus`).
- Page 11 (4.4.3.2.5, step 4): Missing space after colon in `cohort_scope:community`.
- Page 29 (4.4.3.5.2 and 4.4.3.5.3): Long lines in `watch_sla` and `ratified_pair` code blocks wrap mid-statement onto unindented continuation lines (`deletion_sla:*").latest.extract_days`, `deletion_complete").where(asserted_at > revocation_at).first`, `bilateral_pair_id == pair_id).where(envelope.stance == "granted")`).

## Effort estimate
Roughly 3–4 hours of editing: mostly mechanical cleanup (fixing the clipped token on p. 35, wrapping code blocks on p. 29, replacing `1+4` and `Verify`/`Registry` jargon, updating `supersedes` in two pseudocode blocks), plus one steward ruling to align the `delegates_to` vs. `trust:accepts:v1` root-attachment edge between pp. 2 and 33.

<!-- model google/gemini-4-argon; 36 pages; prompt_tokens 29776; completion_tokens 2658; 41s -->
