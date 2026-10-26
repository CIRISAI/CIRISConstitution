# The Reader's Policies (ciris_constitution-1.0-rc11-policies.pdf, 35 pages)

**Care score:** 3 (needs a focused pass to resolve an internal schema contradiction, strip design-history artifacts, and clean up minor rendering defects)
**One-line verdict:** A well-specified composition and delegation manual marred by an internal schema conflict in the partnership ceremony, leftover design-ticket references, and non-ordered policy sections.

## Strengths
- Deterministic resolution rules for community membership, member-to-address bindings, and JCS canonicalization are concretely pinned for interoperability (pp. 9–10, 24–26).
- Forward-secrecy and member-removal semantics are stated once in a single normative section (4.4.3.4.5) and cleanly cross-referenced from community and delivery sections without contradiction (pp. 8, 12, 26–27).
- The institutional cohort configuration (`cohort_scope: affiliations`, 4.4.3.2.8) cleanly maps regulatory, retention, and hierarchy requirements onto existing primitives with clear defaults (pp. 12–17).

## Weaknesses
- **Internal contradiction on the `PARTNERED` ceremony schema:** Section 4.4.3.4.3.1(a) pins `consent:partnership_grant:v1` and `consent:partnership_accept:v1` as `attestation_type: "scores"` with required members `dimension`, `score`, and `subject_key_ids`, citing "CC 4.4.3.5.3 binding mechanism" (pp. 24–25). However, Section 4.4.3.5.3 (`ratified_pair`) queries for `subject_kind == "consent_record"`, `envelope.stance == "granted"`, `envelope.subject_key_id`, and `envelope.target_key_id` (pp. 28–29). A consumer implementing `ratified_pair` as written on pp. 28–29 will never ratify a pair emitted under the normative JCS contract on pp. 24–25.
- **Leftover ticket, gap, and review history:** Section 4.1.5 has a table column "Stories reached for" citing "7 stories", "12 stories", "10 stories", "6 stories", "(1 reviewer)", and "8 stories" (p. 4). Section 4.4.3.1 opens with "Closes G3 (narrow-cell fresh-quorum-recusal infeasibility)" (p. 5). Section 4.4.3.2.8 refers to "the operator the seed lacked" (p. 13). Section 4.4.4 cites "M-1’s symmetry is structural, not bolted on" (p. 35).
- **Raw markdown file reference in prose:** Section 4.4.3.2.8 refers to "(part_3 guardianship clause)" instead of a section number (p. 16).
- **Arbitrary ordering of Reference Policies:** Section 4.4.3 presents Policies A through M in the order E, M, H, L, K, I, F, A, D, J, G, B, C (pp. 5–35), burying the mandatory conformance floor (Policy A, p. 32) near the end of the volume.
- **Clipped inline code on page 34:** In Section 4.4.3.11, `(attestation:registry_consensus` is clipped at the right margin to `(attestation:regi` (p. 34).
- **Editorializing and informal shorthand:** "Why this is still 1+4" (p. 17) and "1+4 preserved" (pp. 22, 33) read as internal design defense rather than constitutional rule-stating.

## Opportunities
- Reordering the subsections of 4.4.3 alphabetically (Policy A through Policy M) would put the mandatory conformance floor (Policy A) first and make the volume navigable as a reference manual.
- Removing the "Stories reached for" column in 4.1.5 (p. 4) and stripping "Closes G3" (p. 5), "the seed lacked" (p. 13), "1+4 preserved" (pp. 17, 22, 33), and "M-1's symmetry" (p. 35) will bring the text into compliance with house rules against history and ticket references in under an hour.

## Threats
- **Interop failure on login partnering:** Because 4.4.3.4.3.1 (pp. 24–25) and 4.4.3.5.3 (pp. 28–29) specify incompatible envelope shapes for the `PARTNERED` bilateral pair (`attestation_type: "scores"` with `dimension: "consent:partnership_grant:v1"` vs. `subject_kind == "consent_record"` with `stance == "granted"`), two conforming implementations of this volume will fail to interop on agent login.
- **Unresolved cross-reference:** A lawyer or regulator reading the minor data handling rules on p. 16 will hit "(part_3 guardianship clause)", exposing the build's markdown source structure and leaving the exact legal hook ambiguous.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | pp. 24–25 vs. 28–29 | contradiction | 4.4.3.4.3.1(a) defines `PARTNERED` halves as bare `scores` (`dimension: "consent:partnership_grant:v1"`, `subject_key_ids`), while 4.4.3.5.3 (`ratified_pair`) queries `subject_kind == "consent_record"`, `stance == "granted"`, `subject_key_id`, and `target_key_id`. | Rewrite the `ratified_pair` pseudocode in 4.4.3.5.3 to match the normative `:v1` bare-scores member set pinned in 4.4.3.4.3.1(a). |
| 2 | p. 34 | rendering | In 4.4.3.11 first paragraph, inline code `(attestation:registry_consensus` runs off the right margin and is clipped to `(attestation:regi`. | Allow line breaks after colons in inline `\texttt` or rephrase the line so the token wraps cleanly. |
| 3 | pp. 4, 5, 13, 35 | stale | Design/ticket history in normative text: "7 stories" / "(1 reviewer)" column in 4.1.5 (p. 4); "Closes G3" in 4.4.3.1 (p. 5); "the operator the seed lacked" (p. 13); "M-1's symmetry" (p. 35). | Delete the "Stories reached for" column on p. 4; remove "Closes G3", "the seed lacked", and "M-1's" phrasing. |
| 4 | p. 16 | stale | Raw file reference "(part_3 guardianship clause)" in 4.4.3.2.8 Minors paragraph. | Replace with the exact `CC 3.x` section number. |
| 5 | pp. 5–35 | numbering | Reference policies in 4.4.3 are ordered E, M, H, L, K, I, F, A, D, J, G, B, C, burying mandatory Policy A at 4.4.3.8 (p. 32). | Reorder 4.4.3.1–4.4.3.13 to A–M (and update cross-references), or add a note at 4.4.3 explaining the grouping. |
| 6 | pp. 17, 22, 33 | editorializing | Internal design-constraint shorthand "Why this is still 1+4" (p. 17) and "1+4 preserved" (pp. 22, 33) used without definition in this volume. | State simply that the design introduces no new structural primitives or envelope fields. |
| 7 | p. 3 | unclear rule | Missing preposition in 4.1.4 table: "The recants distinction matters CC 2.4.1.3". | Change to "The `recants` distinction matters per CC 2.4.1.3". |
| 8 | p. 22 | editorializing | Unmatched closing parenthesis in `license` scope table row: "...and the one refusal a license-scoped issuance meets is stated there)". | Remove the stray closing parenthesis after "there" (or open it before "anyone may be"). |

## Rendering
- **Page 2:** In the 4.1.1 table, column 1, "Unbounded depth" has a wide inter-word gap (`Unbounded              depth`) due to narrow column justification.
- **Page 10:** In 4.4.3.2.5 code block item 1, the tilde in `∼5 km^2` renders as a raised math operator with extra trailing space (`∼5`) inside the monospace block.
- **Page 13:** In 4.4.3.2.8 (`legal_hold` bullet), an uncollapsed hyphen + en-dash pair (`–-`) appears in `(accountable human / court –- CC 3.2)`.
- **Page 34:** In 4.4.3.11, the inline monospace string `(attestation:registry_consensus` overflows the right margin and is clipped to `(attestation:regi`.

## Effort estimate
Roughly 2 to 3 hours of mostly mechanical editing, plus one quick steward ruling to confirm that `ratified_pair` in 4.4.3.5.3 should be updated to match the `:v1` bare-scores schema in 4.4.3.4.3.1(a) (and whether renumbering 4.4.3.x to alphabetical order A–M is acceptable given cross-volume `CC 4.4.3.x` references).

<!-- model google/gemini-4-argon; 35 pages; prompt_tokens 29225; completion_tokens 2307; 32s -->
