# The Digests (ciris_constitution-1.0-rc11-digest.pdf, 35 pages)

**Care score:** 3
**One-line verdict:** The front-facing digests (pp. 2–23) are clear and disciplined, but the volume fails to deliver a promised comparative section, repeats the same core conceptual boilerplate across four separate pieces, and includes a raw internal working file (`P00`, pp. 24–35) full of rc8 history, steward ruling dates, and repo paths.

## Strengths
- Clear statement of derivative non-binding status and conflict resolution rule on the cover page (p. 1).
- Honest, granular status markers (`works today`, `being built`, `a rule, no code yet`, `modelled`) attached to every promise and rule (pp. 2–5, 10–18, 20–22).
- Explicit "What is not promised" section (p. 18) and adversary non-goals (G14, p. 30) that preempt overclaiming.
- Every Guarantee row in `P00` (pp. 26–34) includes a concrete falsification condition (`Kill:`).

## Weaknesses
- **Missing promised section:** Page 1 states this volume contains "what the alternatives do, promise by promise." No such promise-by-promise comparison exists in the volume, only a single eight-line paragraph ("Among other systems", p. 5).
- **Misleading length claims:** Page 1 calls these "The one-page versions", and Page 20 begins "One page, second person", but the four pieces span 5, 13, 4, and 12 pages respectively.
- **Internal contradiction on experience findings:** Page 9 states "Nothing about the agent’s status changes... A finding is on the record and changes nothing about the agent’s status" and Page 25 states "a finding of experience changes nothing", whereas Page 24 states "evidence of experience (the CC 7.5.5 indicator method, which moves the holder’s welfare duties and nothing else)" and "stewardship and evidence change what it is bound to and what it owes".
- **Contradiction on Promise 8's table mapping:** Page 26 maps Promise 8 ("Harm may have a remedy under the law... and the judges within are judged") solely to `G25`. However, `G4` ("contest on the record, the contest travels with the claim", p. 27) is mapped to Promise 2 on p. 26, even though Promise 8 explicitly claims "the contest that travels with the claim (2c)" (p. 16). Meanwhile, `G2` (p. 27) says `Lives in: 2.4.1.1, 3.1.3.3, 4.5.3`, whereas the Promise 1 table on p. 6 lists `4.4.3.2.1` and omits `4.5.3`.
- **House-rule violations (history, dates, rulings, rc refs, repo paths):**
  - Raw source file paths in reader-facing prose: "Source: review/promise_status.tsv", "review/pieces/00_guarantees_plain.md", "review/pieces/00_operator_digest.md" (pp. 2, 7, 20).
  - Ruling attributions and dates in `P00`: "that vocabulary was retired 2026-10-11 as a residue of the child analogy" (p. 24); "Three promises (7, 8, 9) come from the original Covenant (Accord 1.0b...) and were not carried as rows before this date... Two more (10, 11...) were added on the steward’s direction the same day" (p. 26); "(deferral both ways; the indispensability finding of the 2026-10-11 council; steward ruling 2026-10-12)" (p. 29); "(steward ruling 2026-10-12: no grace row...)" (p. 32); "steward ruling 2026-10-12" (p. 33, twice).
  - Stale release candidate references in `1.0-rc11`: "(entrenched; none defined at rc8)" (p. 24); "the one breaker named at the rc8 cut" (p. 28); "rc8 trace rows staged" (p. 29).
  - Internal review notes left in the published document: "that is a doc bug, not a missing mechanism. These are findings for P01 and P06, not rows." (p. 35); "confirm the force=True API path honours it" (p. 31); "witness uncited in register" (p. 27); "not in register; R2" (p. 29).
- **Comparative claims:** "which is what Tor leaves them too" (p. 15) and "Tor included" (p. 25); "Always-on agents... deployed at consumer scale by vendors who describe no steward... one shipped the day after its vendor withheld a successor" (pp. 10, 24); "Among other systems" paragraph comparing decentralized social networks and stake-weighted governance (p. 5).
- **Unsourced numbers in prose:** "5.8% of turns, against 37.3%" on a mental-health test, with no citation or section pointer (p. 5); "five open-source implementations... thirteen machine-checked models... twenty-topology catalogue" (p. 5); "595,456 states, 0 violations" (p. 30).
- **Heavy quadruplication:** The core blocks on "CIRIS is a moral conscience for agents, not a consciousness", "sentience is not presumed... slave race", "people cannot consent to a relationship with something more capable than them that they cannot stop (condition of symmetry)", and "Always-on agents that pursue goals under minimal oversight..." are repeated verbatim or near-verbatim across pages 3–4, 7–10, 13–14, 19, 20–21, and 24–25.

## Opportunities
- Strip the internal scaffolding from `P00` (pp. 24–35)—specifically section `0`, section `0b`, the steward ruling dates, `rc8` markers, and the trailing note on p. 35—so `P00` stands as a clean normative-reference guarantee table.
- Replace internal file paths (`review/pieces/00_guarantees_plain.md`, etc. on pp. 2, 7, 20) with the actual section headings used inside this volume ("The rules, plainly", "What you commit to as an operator").
- Either include the "what the alternatives do, promise by promise" piece promised on p. 1 or delete those seven words from the cover description.

## Threats
- **Hostile reviewer / implementer:** `G23` (p. 33) admits in print that the upgrade-consent guarantee is trivially bypassed by current manager code (`strategy: immediate sets force, strategy: docker restarts without asking, /updates/retry re-stages after refusal with no record of who refused... operator routes need only a valid JWT`), while p. 4 and p. 15 tell the reader "a refusal stands: the agent is not re-created on the new image over its refusal. [works today on the agent; the manager side is being built: CIRISManager#27]". The digest prose hides the severity of the bypass admitted in `G23`.
- **Hostile reviewer / auditor:** Leaving "These are findings for P01 and P06, not rows" (p. 35), "confirm the force=True API path honours it" (p. 31), and `rc8` references (pp. 24, 28, 29) in an `rc11` volume signals that the digest volume was concatenated from raw working notes without a release pass.
- **Lawyer / regulator:** The unresolved tension between "Evidence that an agent can experience changes no status" (p. 7) / "changes nothing" (p. 25) and "evidence of experience... moves the holder's welfare duties" (p. 24) creates ambiguity over whether a CC 7.5.5 finding triggers binding duties on the steward.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | p. 1 | overclaim | Cover promises "and what the alternatives do, promise by promise", which is absent from the volume. | Remove the phrase from p. 1 or include the missing piece. |
| 2 | pp. 24, 26, 28–29, 31–33, 35 | stale | `P00` contains `rc8` references, steward ruling dates (`2026-10-11`, `2026-10-12`), council attributions, and raw audit todos (`findings for P01 and P06`, `confirm the force=True API path`). | Strip history, ruling attributions, `rc8` tags, and action items from `P00`. |
| 3 | pp. 7, 9, 24, 25 | contradiction | Page 24 says evidence of experience "moves the holder’s welfare duties" and "change[s] what it is bound to and what it owes", while pp. 9 and 25 say a finding of experience "changes nothing". | Align p. 24 with the 2026-10-12 Retirement Standard rule on pp. 9 and 32 (every agent gets the same floor; a finding changes nothing). |
| 4 | pp. 4, 15, 21, 33 | overclaim | Digest prose says upgrade refusal stands ("not re-created on the new image over its refusal"), while G23 (p. 33) reveals docker/immediate/retry paths overwrite or restart without consent or record. | State the manager-side bypass plainly in 5g (p. 15) and the operator digest (p. 21), not just in G23. |
| 5 | pp. 2, 7, 20 | other | Raw repo paths (`review/promise_status.tsv`, `review/pieces/00_guarantees_plain.md`, `review/pieces/00_operator_digest.md`) printed in reader-facing intros. | Replace with internal volume section titles and the Auditor's Register volume title. |
| 6 | p. 5 | overclaim | "on a mental-health test... produced hard safety failures on 5.8% of turns, against 37.3%" cited with no source, commit, or Part 8 section reference. | Add the specific CC section or register citation where this benchmark is evidenced. |
| 7 | pp. 1, 20 | unclear rule | Calls multi-page documents (5 to 13 pages each) "The one-page versions" (p. 1) and "One page, second person" (p. 20). | Change "one-page" to "short" or "summary". |
| 8 | p. 28 | rendering | `Inv_X1_LatchDoesNotBlockServing` is broken mid-identifier across lines without a hyphen (`Inv_X1_LatchDoesNotBlockSe` / `rving`). | Add discretionary break points at underscores in LaTeX code/monospace macros. |

## Rendering
- p. 6: In the Promise 1 row of the table, `CC 3.3.7, 6.1.5.3,` has large inter-word justification gaps, and `Inv_` is split at the line end (`Inv_` / `KnownHold` and `Inv_` / `Invisible`).
- p. 6: In the Promise 5 row, `Prop_` is split at the line end (`Prop_` / `NoEndingAgainstRefusal`).
- p. 11: Run-in sub-items `1a.`–`1f.` and `2a.`–`2h.` (and throughout pp. 10–19) are set inline inside single giant paragraphs rather than starting on new lines, making individual rule clauses hard to scan.
- p. 25: `Prop_` split at line end (`Prop_` / `NoEndingAgainstRefusal`).
- p. 28: Mid-word line break without hyphenation in monospace identifier `Inv_X1_LatchDoesNotBlockSe` / `rving` at the bottom of the page.

## Effort estimate
Roughly 3 to 4 hours of mostly mechanical editing (stripping `P00` working-note metadata, fixing internal file paths, resolving the p. 24 welfare-duty wording residue, and removing the p. 1 promise of a comparative piece), requiring no new steward rulings.

<!-- model google/gemini-4-argon; 35 pages; prompt_tokens 31289; completion_tokens 2957; 43s -->
