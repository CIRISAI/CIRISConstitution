# Pass-7 Gemini digest report: verification against rc12 source (2026-10-26, branch rc12 at f7d2af2)

**Scope note.** The Digest volume prints constitution/covers/digest.md, constitution/EXECUTIVE_SUMMARY.md, review/pieces/00_guarantees_plain.md, review/pieces/00_operator_digest.md and review/pieces/00_guarantees.md; markers are stamped from review/promise_status.tsv. The rc12 digest PDF Gemini read was built 20:44 today, after the last source commit f7d2af2 (20:30) and after the M16 landing f0b6328 (20:04), so Gemini reviewed current source. Page cites below were re-checked against `pdftotext -layout` of volumes/ciris_constitution-1.0-rc12-digest.pdf (35 pages). Abbreviations: EXEC = EXECUTIVE_SUMMARY.md, PLAIN = 00_guarantees_plain.md, OPER = 00_operator_digest.md, GUAR = 00_guarantees.md.

**Care score:** 3. **Verdict paragraph:** "A well-structured, honest four-lens summary whose main liability before 1.0 is heavy four-way repetition of its philosophical preamble and the inclusion of repo-level commit hashes, PR numbers, and rc history in the guarantees table."

Dispositions: M = mechanical fix, R = steward ruling, P = pipeline, X = reject.

## Top defects and threats, in Gemini's order

### 1. Forced-stop rule (top defect 1; threat 1) — PARTLY CONFIRMED, mostly FALSE

(a) The pieces agree on who decides and distinguish the acts; the one real inconsistency is the "and only for a safety emergency" qualifier, which the Digest adds and neither Part 7 nor the G16 row carries.

(b) Verdict: FALSE on "any person may turn off" vs "only a root or authority can force" (5a opens with "Two different acts" and separates the owner's own device from "an agent it runs for other people", PLAIN:73). FALSE on "steward" vs "authority role": the volume says three times that the steward is the agent's Wise Authority (PLAIN:15 "Today the steward is the agent's Wise Authority"; PLAIN:23 "holds root authority over it"; OPER:22 "You are the agent's Wise Authority today"; GUAR:59 "CIRISAgent root authority mints WAs"), so a steward is an AUTHORITY-or-ROOT principal and 5b, 5g and G16 name the same person. CONFIRMED on the qualifier.

(c) PLAIN:79 "only a root or an authority role can force a stop, and only for a safety emergency"; OPER:24 the same sentence. GUAR:74 G16 "Only a ROOT or AUTHORITY principal may force a shutdown over the agent's objection" (no emergency limit); constitution/claims.tsv:449 CLM-agent-forced-shutdown-role-gate says the same. The binding section is broader still: constitution/part_7_ethics_governance.md:315 "B. **Emergency Shutdown:** Triggered by catastrophic failure or WA mandate." "safety emergency" appears nowhere in constitution/ (only in the two Digest lines). The qualifier entered at 3334fae (the pass-4 landing, 2026-10-25). By the cover's own rule (covers/digest.md:5, the section is right and the digest is a defect), the two Digest lines are the defect.

(d) Pass 6: not raised (Grok raised only the truncated G16 status cell, now fixed). Not a regression.

(e) R, then M: the steward says whether a force over objection is limited to an emergency (7.5.2 B says "catastrophic failure or WA mandate"); then 5g, OPER:24 and G16 carry one wording. Gemini's proposed split (immediate forced stop vs post-window planned shutdown) is already what 5a and 5g say; only the qualifier needs the ruling.

### 2. "Reviewer standing" vs G14, G25, G26 (top defect 2; threat 2) — CONFIRMED for G14 only, FALSE for G25 and G26

(a) The standing rule kills a row only when it has no witness AND no basis AND no ticket; G25 and G26 have Basis cells, so the rule does not reach them; G14 is the one row the rule reaches as written.

(b) CONFIRMED (G14), FALSE (G25, G26).

(c) GUAR:25 "the row is not backed (no witness and no basis, and no ticket that will produce one)". GUAR:65 G14: Witness "—", Basis "—", Status "in force", no ticket. GUAR:83 G25 Basis "CIRISNode moderation flow carries `objection:*`; archive release path unpinned"; GUAR:84 G26 Basis "`AgencyErosionDetector` conscience faculty (TX-10); no force-chapter code". Adjacent, in the same paragraph block: GUAR:19 "G14 is a guarantee about the other thirteen" (the table has 28 rows); and the status legend at GUAR:48 defines only "backed, staged, unbacked" while the column prints in force, measured, established, enforced, witnessed no basis, normative-only, stated not shipped, staged (the rc11 pass-1 note line 118 raised the vocabulary; still open).

(d) Pass 6: not raised. Not a regression.

(e) M: one clause in "Reviewer standing" exempting the limits row (its basis is the Scope and 1.13.3.1, which it cites in "Lives in"); "thirteen" to "twenty-seven"; and either widen the GUAR:48 legend to the vocabulary the column uses or collapse the column to the four cover markers.

### 3. Commit hashes, PR numbers, rc history, file paths and a bug note in the G table (top defect 3; weakness 2) — CONFIRMED; two tokens are REGRESSION

(a) Every token Gemini lists is in current source.

(b) CONFIRMED.

(c) GUAR:53 "backed (the purge rows graduated at re-pin 16, persist ca6bdf60)"; GUAR:58 "closed at persist v58.0.0 `770156ef`"; GUAR:60 "backed; rc8 trace rows staged"; GUAR:73, :75, :77, :78, :79 "established at agent ef02367"; GUAR:80 "design `FSD/RETIREMENT_STANDARD.md`, CIRISAgent PR #1260"; GUAR:21 "(CIRISServer `FSD/PRIOR_ART.md`)"; GUAR:88 "that is a doc bug, not a missing mechanism". Ticket ids (CIRISServer#769, CIRISAgent#1262 and the rest) are the house convention for "being built" and are not defects.

(d) Raised in every pass since rc11 pass 1 (note line 111: ca6bdf60, a75da61c, ef02367, PRIOR_ART.md). Pass 3 M8 planned "G7's commit hashes, dates ... → the register; ruling dates and 'rc8' out of the G rows; 'findings for P01 and P06, not rows' → cut". Pass 5 Gemini #2 "rc8 references ... raw audit todos"; pass 6 verify item 20 "G7 lab-log pins" (P or M). M16 (f0b6328) removed a75da61c, the csd129 artifact path, "run 5 and run 6", "re-pin 18" and "findings for P01 and P06" from GUAR, but left `770156ef` in G7 and "rc8" in G9, both inside M8's stated scope: **REGRESSION** for those two. ca6bdf60/re-pin 16 (G2), ef02367 (G15–G21), PR #1260 and the FSD paths (G22, the no-ban paragraph) and the "doc bug" sentence were never in an M batch's explicit scope beyond M15's "P00's history", so they are carried, not regressed.

(e) M (one sweep of GUAR:53, :58, :60, :73–80, :21, :88: keep CLM ids, test names and ticket ids; drop hashes, re-pin and rc labels, repo paths and the bug aside), or P (strip at volume build; the Register volume keeps them). check_stale_refs could gain a `\b[0-9a-f]{7,8}\b` and `re-pin \d+` class for review/pieces/.

### 4. "Among other systems" (top defect 4; weakness 3) — CONFIRMED present, ruled kept

(a) The paragraph is in current source, and the steward ruled on it yesterday.

(b) CONFIRMED present; X.

(c) EXEC:49 "**Among other systems.** Decentralized social networks solved distribution without an owner, and one of them added composable moderation; none makes consent, withdrawal or a human halt part of the message format itself ... Stake-weighted governance decides by holdings". The vendor premise Gemini groups with it (PLAIN:21, GUAR:11 "Always-on agents that pursue goals under minimal oversight ... one shipped the day after its vendor withheld a successor") is sourced in the text itself: "The sourced record is CC 8.6.1", so "comparative claims about other projects" unsourced is FALSE for that pair.

(d) Pass 6 verify item 14 and SWOT R101: "cut the two Tor lines; the steward says whether the 'Among other systems' paragraph stays"; the steward ruled "cut the two Tor lines, keep the paragraph". The Tor lines are gone (0 hits in the four files). Not a regression.

(e) X (ruled 2026-10-26). If the steward wants it re-opened, R.

### 5. Unsourced numbers in the Executive Summary (top defect 5; weakness 4) — PARTLY CONFIRMED

(a) The benchmark figures are sourced in the edition but the Digest gives no pointer; the model count is right; the implementation and topology counts have no register row to point at.

(b) CONFIRMED for the missing pointer on the benchmark; FALSE as "unsourced" (the source exists); MATTER-OF-TASTE for the counts.

(c) EXEC:47 "hard safety failures on 5.8% of turns, against 37.3%" with only "Part 8 names what it would take to lose the bet" as a pointer. The source is constitution/part_8_appendices.md:1392–1405, Annex J 8.8.10 "The research evidence (measured; nothing rounded up)", table rows "the accord as a plain **prompt** | 37.3%" and "**the accord inside the pipeline** | **5.8%**", register row CLM-conscience-faculty. EXEC:45 "fourteen machine-checked models" matches formal/README.md:24 ("167 of them today, across 14 models") and README.md:5. "five open-source implementations" and "twenty-topology catalogue" have no row in the volume to cite.

(d) Pass 5 Gemini #6 (same finding, "Add the specific CC section"); pass 6 Grok (line 33) and verify item 25: "X for a summary; P if the counts are ever generated from the register". M16 did not claim it. Not a regression, but the third pass in a row to raise it.

(e) M for the benchmark: one parenthesis "(CC 8.8.10, CLM-conscience-faculty)" at EXEC:47 closes a finding three models have made. X for the counts (summary prose), P if ever generated.

### 6. Duplication of the preamble across the four pieces (top defect 6; weakness 1; opportunity 1) — CONFIRMED, overstated

(a) The thesis, the slave-race aside and the symmetry justification each print three times, not four; the operator digest carries only the symmetry line; the eleven promises print three times (EXEC in full, PLAIN as headers, GUAR 0b as a table).

(b) CONFIRMED (three-way, not four-way).

(c) Counts over EXEC / PLAIN / OPER / GUAR: "moral conscience for agents, not a consciousness" 1/1/0/1 (EXEC:23, PLAIN:7, GUAR:7); "new slave race" 1/1/0/1 (EXEC:23, PLAIN:9, GUAR:80); "cannot consent to a relationship with something more capable" 1/2/0/1 (EXEC:21, PLAIN:9 and :148, GUAR:15); the symmetry phrase family 1/3/1/1 (EXEC:21, PLAIN:9, :67, :148, OPER:19, GUAR:58, with GUAR:7 and :15 in other words); "Kind reaches the rules in three ways and no others" 1/2/0/1 (EXEC:13, PLAIN:9 twice, GUAR:7). GUAR "0. The rule this piece is built on" (GUAR:5–25) and "0b. The eleven promises" (GUAR:27–44) restate EXEC:13–41 and PLAIN:7–23.

(d) Pass 5 Gemini ("quadruplication"); pass 6 Grok line 26 "Cut ... the repeated symmetry / 'slave race' essay (pp. 3–4, 7–8, 14, 19, 24–25)" and verify item 30 "X unless the steward trims". Not in M16. Not a regression.

(e) R. The phrases are the steward's and stay; whether GUAR 0/0b keeps its own copy or becomes a pointer plus "Reviewer standing" and the 0b table is a cut question for the steward. If ruled, M (about 2.5 pages).

### 7. "One page, second person" (top defect 7; weakness 5) — CONFIRMED, REGRESSION

(a) The operator digest still calls itself one page and prints on pp. 20–23 of the PDF.

(b) CONFIRMED.

(c) OPER:5 "*One page, second person, derivative of the rules and the shipped implementation.*" In the PDF the piece opens on p. 20 and its last bullets ("Some uses are never allowed ... Nothing here limits a duty the law imposes") are on p. 23.

(d) Pass 4 GPT (line 16), pass 5 Gemini #7 ("Change 'one-page' to 'short' or 'summary'") planned under M15 ("the digest cover's 'alternatives' and 'one-page'"), pass 6 verify item 16 (M). M16 claimed the pass-3–5 batches, fixed the cover (covers/digest.md:3 now "The short versions") and edited OPER:5 itself (removed the `00_guarantees_plain.md` piece id) but left "One page": **REGRESSION** (partial landing of a claimed item).

(e) M: "In the second person, derivative of the rules and the shipped implementation."

### 8. The philosophy sentence (weakness 6; opportunity 3) — CONFIRMED in substance, numbers wrong

(a) The sentence is long and semicolon-chained, but it is 284 words with 10 semicolons, not 385 and 11; the whole paragraph is 632 words.

(b) CONFIRMED (readability), MATTER-OF-TASTE (the steward's own statement).

(c) PLAIN:7 from "The philosophy: we are owed as much as we offer to the least of us" to "not by a court." (284 words, 10 semicolons), inside a 632-word paragraph that also carries the six premises, the agency sentence, the set-asides and contextual integrity.

(d) Not raised in pass 6 as a defect. Not a regression.

(e) R: break the chain into the eleven clauses as a list under "The philosophy", or keep it as the steward's prose. M once ruled.

### 9. ciris.ai URLs as load-bearing citations (weakness 7) — CONFIRMED present, MATTER-OF-TASTE

(a) Two pages cite the site as where an argument is made, in a volume that binds nobody.

(b) MATTER-OF-TASTE.

(c) PLAIN:7 "six things this document takes as given, and ciris.ai/compare and ciris.ai/constitutional-mesh argue for:" (the six are then stated inline, so the URLs carry the argument's provenance, not the premises); PLAIN:148 "the pace of change is so great and the need so dire (ciris.ai/constitutional-mesh) that the minimum viable power to instantiate the mesh must be used". Different from the N1 sentence at PLAIN:139, which pass 6 item 28 kept on purpose.

(d) Not raised in pass 6. Not a regression. (The "need so dire" residue was named in pass 5 M15; the sentence survives with the URL.)

(e) R: cite the edition (CC 1.13 / Part 8 prior-art) instead of the site, or keep. M once ruled.

### 10. "CC 7.1 Book IV ch. 4 / ch. 5" (top defect 8; weakness 8) — CONFIRMED, new

(a) Two G rows cite Part 7 by a numbering scheme no volume uses.

(b) CONFIRMED.

(c) GUAR:82 G24 "(CC 1.3 PDMA, CC 1.9 WBD, CC 7.1 Book IV ch. 4)"; GUAR:83 G25 "(CC 4.3; Deferral Deliberation Councils, CC 7.1 Book IV ch. 5)". "Book IV" occurs nowhere else in constitution/ or review/pieces/. Part 7's 7.1 subsections carry chapter names: constitution/part_7_ethics_governance.md:50 "### 7.1.4 `4-integration` — Chapter 4: Integration" and :62 "### 7.1.5 `5-governance` — Chapter 5: Governance & Oversight Infrastructure".

(d) Not raised by any earlier pass. Not a regression.

(e) M: "CC 7.1.4" and "CC 7.1.5". check_stale_refs could gain `Book [IVX]+`.

### 11. Wise Authority board self-perpetuation carried as a defect (threat 3) — CONFIRMED present, by design

(a) The text says exactly what Gemini quotes, on purpose.

(b) CONFIRMED present; X.

(c) EXEC:41 "the self-perpetuation of the Wise Authority board, with both cells missing and carried as a defect until it is repaired or ratified"; PLAIN:148 "a declared privilege with both cells missing: no condition ends it and the deferring party cannot decline it; so it is carried as a defect, and its remedy is pending ... neither has happened" (matches the Part 4 register entry).

(d) Pass 6 verify item 29: X ("the register carries it as a defect by design"; R92 landed the remedy wording). Not a regression.

(e) X. The threat Gemini describes (a regulator reads it as unresolved capture risk) is the disclosure doing its job; the remedy is the Part 4 work, not a Digest edit.

### 12. Rendering: `Inv_` / `Prop_` broken across lines in the p. 6 table — CONFIRMED, pipeline

(a) pdftotext shows the break on p. 6 in the promise-4 Check cell.

(b) CONFIRMED.

(c) EXEC:60 Check cell "`formal/accord_halt`, `formal/accord_roster` (Lean); `RootReach.tla` `Prop_HaltReach`, `Inv_HaltOnlySubscribers`, `Prop_RestrictOnly`, `Untrust`"; the renderer breaks after the underscore.

(d) Pass 5 Gemini #8 (same class, G7's `Inv_X1_LatchDoesNotBlockServing`), pass 6 verify item 27 (P). Not a regression.

(e) P (discretionary breaks in code spans, or a narrower identifier set in the cell).

## Claims in Gemini's Strengths that were checked

- Cover rule quoted correctly (covers/digest.md:5). Markers are stamped from review/promise_status.tsv (rows for 5a, 5b, 5g confirmed). CIRISManager#27 is disclosed at PLAIN:79, OPER:24 and GUAR:81; witnessed mode off at EXEC:35, PLAIN:130 and GUAR:86. N1–N5 at PLAIN:139–143; G14 at GUAR:65. Every G row has a Kill cell. All accurate.

## Pass-6 items Gemini did not re-raise, confirmed closed in source

R99 landed (every promise header now carries its weakest sub-rule marker, EXEC:15–35). G16's status cell is complete (GUAR:74). The leaked piece paths, "P00" id and "Source:" lines are gone. "The Digests" is now "The Digest" in build_pdf.py:286 and the cover. The two Tor lines, "death as doctrine", "nothing else does", "welfare duties", "which cells each still lacks" and "has no cycles" are gone. ρ̄ is now glossed in its own cell (GUAR:63). Promise 1's mapping carries "private" (GUAR:33). The Check column says "rule; no check yet" for promises 8 and 9 (EXEC:64–65). "Beside the promises" (PLAIN:133–135) and the EXEC:37 paragraph carry the disclaimer and the practices outside the promise bodies.

## Summary

12 items: 7 CONFIRMED (items 1 partly, 2 for G14 only, 3, 6, 7, 8, 10, 12), 2 CONFIRMED-present-but-by-design (4, 11, both X), 1 PARTLY (5), 2 MATTER-OF-TASTE (8 in its numbers, 9); 2 REGRESSION tokens inside item 3 (`770156ef` in G7, "rc8" in G9) and 1 REGRESSION line in item 7 ("One page" at OPER:5); 0 wholly FALSE items, though item 1's contradiction is false in two of its three parts and item 2 is false for G25/G26. Dispositions: M 5 (2, 3, 7, 10, and the one-token cite in 5), R 4 (1, 6, 8, 9), P 1 (12), X 2 (4, 11). Top three: the "safety emergency" qualifier that only the Digest carries (item 1, needs the steward); the hashes, rc labels and the "doc bug" aside still in the G table after three batches planned their removal (item 3); "Book IV ch. 4/5" and "One page", two one-line mechanical fixes (items 10, 7).
The volume reads better than at pass 6, and Gemini's care score of 3 against Grok's 4 agrees with that: pass 6's defect list was dominated by status markers that contradicted their own sub-rules and by leaked build paths, all of which R99/M16 closed, so what is left is a cut question (the triplicated preamble), a register-hygiene sweep of one file, and one qualifier the Digest invented; none of Gemini's items is a rule contradicting a section except that qualifier.
