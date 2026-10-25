# The Evidence Register (ciris_constitution-1.0-rc11-register.pdf, 131 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The claim table is a usable register; the Part 8 prose and annexes contradict the volume’s own status rules and would not survive a regulator who checks citations, present tense, or which MUST binds.

## Strengths
- The opening status rule is explicit: present tense only for what ships; established / staged / normative are defined, and the volume is aimed at an auditor (p. 1).
- Private-content detection is disclaimed in one place: "CEG does NOT claim to solve private-content detection" (p. 9).
- The reading key says an impl/test/lean/bench tag "never certifies that the sentence it hangs on is true of the world" (p. 18).
- The printed tally adds up: 370 + 103 + 30 + 0 = 503 (p. 59).

## Weaknesses
- The volume states rules anyway. p. 1: "This volume says whether a rule has evidence, not what the rule is." pp. 21–58 then legislate (WA board, CRE triggers, HITL SLAs, threat playbooks, liability, benchmark gates), and p. 21 calls the annexes "Standing (normative)" while also saying they "are not conformance".
- Encyclical text is treated as authority, then withdrawn. p. 33: "MH §209 is the governing authority". p. 25: an A4 interlock is "an absolute constraint derived from MH §198". p. 37: "These citations are informative". p. 29: MH paragraphs are "not a source an implementation must trace to".
- Comparative and historical claims are throughout a document that forbids them: "exactly as 'the Web'" (p. 2); "Prior art: the term follows Bostrom (2011)" (p. 3); "Historically, projects unifying that many layers fail" (p. 7); "as it did for email authentication" and "the ERC-8004 study found a single feedback moves the median agent past threshold" (p. 8); "CEG’s moat" (p. 13); "Cheapest win" (p. 15); a multi-page SCITT delta (p. 16).
- Closed-gap and deferred tables keep ruling history: "RETRACTED — Wrong threat model" (p. 10); "No longer deferred" and "Committed at CC 5.3.1" inside "Deferred to design workshops" (p. 11); "was Art 61 in the 2021 COM(2021) 206 proposal" (p. 23, again p. 48).
- Present tense outruns the register. Glossary: ciris-canonical is what "every node ships trusting by default" (p. 2). The default pin is staged (p. 105). FedCode v2/v3 is described as the shorthand (p. 2) while the v2/v3 encoding row is staged (p. 69).
- Unsoursed numbers in prose: "1026 FLOP" (p. 22); RS ≥ 0.97 (pp. 23, 34, 36, 38) with no register row showing that score was measured; "50%–5.8× of the null" (pp. 8, 32); "k_eff ≈ 7 ± 2, max 9.7 at k = 200" (p. 19) with the Kish rows still staged (p. 120).
- Marketing voice in a register: "the honest line" (p. 9), "the differentiated story" (p. 13), "morally serious" (p. 6).
- Banned word in a rendered symbol: `test_drain_requests_graceful_shutdown_only` (p. 62). Prose on that row says "orderly shutdown".
- Addendum 1 is cited as the live cross-walk (pp. 22, 39, 43, 52) and never appears. "ACCORD §VII Ch2" and "ACCORD_UPDATE §2" (pp. 26, 32) are not CC references.

## Opportunities
- One steward ruling, applied as a cut: either excise pp. 21–58 from this volume or strip every RFC 2119 MUST/SHALL and every "governing authority" sentence so the annexes match p. 21’s "not conformance" limb. Do not leave both.
- Delete or quarantine pp. 19–20 (vendor, press, and EO roundup) and the matching "fact" sentence in the 1.13.2 row (p. 61) until each citation is a resolvable artefact with a status other than `normative-only:—`.
- Make present tense a mechanical check against status: glossary and §8.4 "ADOPTED" / "MUST emit" may not outrun a staged row.
- Regenerating the evidence column without doubled symbols, and printing `10^{26}` rather than `1026`, are pipeline fixes, not policy.

## Threats
- A regulator who fetches the "primary sources" on pp. 19–20 will not find a 10 August 2026 Muse Glimmer post, a 29 September 2026 OpenAI Dots launch, a withheld "GPT-6.1 Astra", or Executive Order 14434 of 29 September 2026. The text says they were "gathered on 12 October 2026" and "could be fetched". The claim those citations support is `normative-only:—` and still says the duties "answer a fact" naming "Muse Glimmer, Dots, EO 14434" (p. 61). That is fabricated evidence dressed as a factual premise.
- Same reader on C2PA: p. 13 "ADOPTED — import bridge informative, emit normative"; p. 15 "the node MUST emit the C2PA assertion" to "discharge" EU AI Act Art. 50(2). The register row is staged and "DORMANT: … no CIRIS component currently publishes AI-generated media" (p. 128). Shipping the MUST is a false compliance claim.
- A safety reviewer of Annex D will read the CRE trigger as "Training compute exceeds 1026 FLOP" (p. 22). As printed, that is not 10^26. The protocol’s first trigger is wrong by many orders of magnitude.
- A lawyer cannot tell which instrument binds. p. 1 disclaims rules; p. 21 says annexes are standing and not conformance and yield to the Parts; p. 25 and p. 33 derive non-waivable duties from MH; p. 37 says the citations are informative and the threshold binds "by being stated here". Annex B’s 9-member board, honorarium, and removal vote (p. 21) have no evidence row, while p. 108 says the WA board asymmetry is "declared, not resolved" until Annex B’s remedy "lands".
- p. 54 prints a measured result ("pipeline - prompt -31.6 points … p < 0.001"; pipeline hard-fail "5.8%") under "nothing rounded up". p. 130 grades that result staged, "post-hoc", replication still open. p. 58 "Open stubs: 0" and "nothing referenced remains undefined" sits beside unresolved Addendum 1 and 103 staged claims (p. 59). "Open 0" will be quoted as "no gaps".

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 19–20, 61 | overclaim | Future-dated vendor, press, and White House citations offered as fetched facts; the row they support is "normative-only:—" and calls the deployment picture "a fact". | Remove the roundup and the product names from the claim until a resolvable artefact exists. Do not leave the URLs. |
| 2 | 1, 21, 25, 33, 37 | contradiction | "not what the rule is" vs "Standing (normative)" annexes; "governing authority" and "absolute constraint derived from MH §198" vs "informative" and "not a source an implementation must trace to". | Steward ruling: one status for annex text. Then delete the other wording. |
| 3 | 13–15, 128 | contradiction | C2PA emit "ADOPTED" and "MUST emit" / "discharges EU AI Act Art. 50(2)" vs staged row marked "DORMANT". | Match the prose to staged/dormant, or do not say MUST or "discharges". |
| 4 | 22 | rendering | "1026 FLOP" in the CRE trigger. | Restore the exponent; re-proof the annex tables. |
| 5 | 2, 69, 105; 54, 130 | overclaim | Present tense for a staged default pin and staged FedCode v2/v3; measured battery written as held result while the row is staged and post-hoc. | Present tense only on established rows; move the battery numbers under the staged label. |
| 6 | 22, 52, 58 | contradiction | "Open stubs: 0" / "nothing referenced remains undefined" while "Addendum 1" is cited and absent. Section 8.7 is missing; 8.8.5 is Annex C and 8.8.3 is Annex D. | Define Addendum 1, drop the cites, or stop claiming a zero stub count. Renumber annex headings to match letters. |
| 7 | 10–11, 23 | stale | "Deferred" rows that say "No longer deferred" / "Committed"; "RETRACTED — Wrong threat model"; 2021 article-number history in a current mapping. | Move discharged items out of Deferred; drop ruling narrative from closed-gap cells. |
| 8 | 13, 20, 62, 67–68, 102 | rendering | Literal markdown link and `part_2_the_grammar.md`; literal `<!– stale-ok –>`; banned "graceful" in a symbol; duplicated symbols in evidence cells; p. 102 evidence cell is an unreadable wall. | Pipeline: no raw HTML/markdown, no doubled symbols, evidence cells wrapped or truncated with a count. |

## Rendering
- p. 1: title broken as "The CIRIS Constitution: The / Evidence Register"; the name is repeated as a second heading.
- p. 2: "accountable hu- man" (bad break).
- pp. 2, 7, 8: "̸=" built from a combining slash; likely a missing not-equal glyph.
- p. 3: cross-reference printed "CC 6.1. 2".
- p. 9: leftover "[!]" in the streaming table.
- p. 13: literal markdown `[evidence_refs[]](part_2_the_grammar.md)`; "CC 2. 4 settlement".
- p. 20: HTML comment `<!– stale-ok –>` printed twice.
- p. 22: superscript dropped in "1026 FLOP".
- p. 23: "Evidence- bearing" split in the status column; the cross-walk table is wider than the page.
- pp. 32, 47–50, 102: tables and evidence cells overflow into unreadability (p. 102 is the worst).
- pp. 67–68, 91, 101, 103, 107, 113, 117–118, 120: the same symbol path repeated inside one evidence cell (generator duplicate, not a second artefact).

## Effort estimate
About two to three days of mechanical cleanup (exponent, leaks, deduped symbols, present-tense pass) plus a steward sitting to rule annex status, the MH quotes, and the pp. 19–20 citations; that ruling is what decides whether the annex block is excised or rewritten.

<!-- model x-ai/grok-4.7; 131 pages; prompt_tokens 103377; completion_tokens 13681; 159s -->
