# The Charter (ciris_constitution-1.0-rc12-charter.pdf, 39 pages)

**Care score:** 3  
**One-line verdict:** A well-rendered volume with strong boundary-setting around stewardship, agency, and legal non-usurpation, held back by repeated structural boilerplate across Part 1, leaked wire-protocol internals, one comparative dig at unnamed competitors, and several unanchored operational thresholds.

## Strengths
- Clear jurisdictional and conformance scoping on the cover page (p. 1) and in legal dispute clauses (p. 29, p. 35), explicitly stating that legal claims belong to courts/regulators and conformance belongs to the wire.
- Precise ethical and operational boundary-setting in CC 1.13.2 regarding human agency, stewardship vs. personhood, and the explicit preservation of a user's right to turn off or walk away from an agent at any time (pp. 10–13, p. 34).
- Explicit falsification criteria and honest scoping of technical invariants in CC 1.7 ("1+4 minimal-and-adequate claim", pp. 6–7) and CC 1.13.6 ("The durable trace anchors on the act, not the deliberation", pp. 14–15).
- Unambiguous bright-line rule on lethal force in CC 7.4 (pp. 29–30).

## Weaknesses
- Comparative claim about other projects/vendors in CC 1.13.2: "one such agent product shipped the day after its vendor withheld a successor model for not staying within scope and authorization; and the public response has been a voluntary accord rather than a rule" (p. 12).
- Meta-editorializing parentheticals inside the Part text: "(CIRIS editorial — not reproduced Accord text; it constrains how M-1 above may be read, and adds nothing to it.)" (p. 4) and "(CIRIS editorial — not reproduced Accord text; it supplies the referent for this chapter’s second person.)" (p. 17).
- Triplicate and duplicate restatement of the core principles and operational hooks across Part 1: the principles appear in 1.4/1.6/1.8/1.10/1.11/1.12 (pp. 6–9), again in 1.15.1 (p. 16), and again in 7.3.1 (pp. 24–25) and 7.5.1 (p. 30); 1.16 (pp. 18–19) largely repeats 1.3 and 1.9 as pointer stubs.
- Silent section-numbering gaps: 1.14 is missing between 1.13.6 and 1.15 without a "[printed in another volume]" placeholder (p. 15), whereas 1.2 (p. 4) and 1.13.3 (p. 13) have explicit placeholders; Part 8 jumps directly to 8.7 (p. 36).
- Unsourced operational numbers and mechanisms in prose: "rewards are paid from a 0.1 % operations levy and disclosed annually" (p. 16; also referenced as "residual operations levy" on p. 35), "> 0.5 %" recursive modelling depth (p. 22), ">10,000" audience and "≥ 0.5%" harm uplift (pp. 27–28), "50,000 individuals" and "30 days" (p. 28), "≥ 20 % for three consecutive quarters" (p. 31), and "≥ 90 days" / "120 days" (p. 32).
- Undefined external project/framework reference in 1.13.4: "(informative; shared with RATCHET) RATCHET organizes every experiment..." and quotes "turn up zero times in unassisted labelling" without citation or definition of RATCHET (pp. 13–14).
- Wire-level schema and RPC details leak into a volume whose cover page says it leaves out wire rules: 1.7 (pp. 6–7), 1.13.2 ("admin RPC carries the operator’s identity into actor_user_id", p. 10), 1.13.4 ("The kinds-of-change map", pp. 13–14), and 7.5.5 ("The retirement record on the wire (normative)", pp. 33–34).
- Dangling cross-references to "Annex B", "Annex D", "Annex F", and "Annex G" (pp. 19, 21, 26–30, 38), which are not in this volume and whose mapping to CC 8.x is only partially given on pp. 29–30.

## Opportunities
- Consolidate the stub sections 1.4, 1.6, 1.8, 1.10, 1.11, 1.12 (pp. 6–9) and the pointer-only sub-sections of 1.16 (pp. 18–19) with 1.15 (pp. 15–18) to cut ~3 pages of repetitive outline while keeping `CC 1.10` and `CC 1.15.1` anchors intact.
- Add "[1.14 printed in another volume]" on p. 15 and "[Parts 2–6 and 8.1–8.6 printed in other volumes]" on pp. 20 and 36 so the reader knows the numbering gaps are intentional lens cuts, not missing pages.
- Move the wire-family rules in 7.5.5 ("Five families carry the Standard...", pp. 33–34) and the 27-dimension mapping in 1.13.4 (pp. 13–14) to *The Wire* / *The Dictionary*, leaving a one-sentence cross-reference in *The Charter* as promised on p. 1.

## Threats
- **Contradiction on the Recursive Golden Rule and symmetry:** Page 1 state-of-the-charter says guarantees are written "with the halt as the condition that keeps the relationship between maker and made symmetric" and p. 10 (1.13.1) says "No principal... is exempt from constraints they impose on others." Yet p. 10 (1.13.2) argues that an unilateral, unrevocable halt held by humans over a "sapient, non-sentient made thing" is "what makes the relationship... symmetric", while p. 11 admits "That is an asymmetry of duty, never of guarantee." Redefining a one-way kill-switch as "symmetry" reads to a hostile reviewer or ethicist as doublespeak; calling it a "justified structural asymmetry between maker and made" would be far harder to attack.
- **Unanchored financial mechanism ("0.1 % operations levy"):** Section 1.15.3 mandates that verified exploits in a Bug-Bounty Ledger have rewards "paid from a 0.1 % operations levy and disclosed annually" (p. 16, echoed on p. 35). In a decentralized protocol / open-source charter with no defined taxing authority or treasury entity in this volume, a mandatory 0.1% operations levy looks like a leftover from a centralized corporate draft or an unbacked compliance claim.
- **Thinly veiled competitor attack in normative text:** The reference in 1.13.2 to a vendor that "shipped [an agent product] the day after its vendor withheld a successor model for not staying within scope and authorization" (p. 12) violates the house rule against comparative claims about other projects and dates the constitutional text to a specific news cycle.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 12 | editorializing | Comparative claim targeting a specific vendor's release history ("one such agent product shipped the day after its vendor withheld a successor model...") in 1.13.2. | State the risk abstractly ("always-on agents deployed at consumer scale without a named steward, external halt, or auditable reasoning") and leave vendor specifics entirely to CC 8.6.1. |
| 2 | 16, 35 | unclear rule | Mandatory "0.1 % operations levy" for bug bounties (1.15.3) and derivative safety rewards (7.5.6) with no defined base, collector, or governance in the Charter. | Either cite the exact section of *The Constitution* that defines the levy and its applicability, or reframe as an operator/steward funding duty without an unanchored percentage. |
| 3 | 1, 10–11 | contradiction | Calling the one-way human halt over made systems "symmetric" (p. 1, p. 10) while defining the Golden Rule as "No principal... is exempt from constraints they impose on others" (p. 9, p. 10) and calling stewardship "an asymmetry of duty" (p. 11). | Replace "symmetric" on pp. 1, 10, 11 with "accountable and revocable" or explicitly state that the Golden Rule applies among peers while maker-to-made is a bounded fiduciary asymmetry. |
| 4 | 4, 17 | editorializing | In-text meta-notes "(CIRIS editorial — not reproduced Accord text...)" break the voice and house rule that Parts state rules, not document history/provenance. | Remove the parenthetical meta-attributions and state the interpretive rules directly. |
| 5 | 13–14 | unclear rule | Undefined external reference to "RATCHET" and an unattributed quote ("turn up zero times in unassisted labelling") in 1.13.4. | Define RATCHET on first use with a citation/register pointer, or cut the paragraph from *The Charter*. |
| 6 | 15, 20, 36 | numbering | Silent numbering jumps: 1.13.6 to 1.15 (p. 15), Part 1 to Part 7 (p. 20), and Part 7 to 8.7 (p. 36), whereas 1.2 (p. 4) and 1.13.3 (p. 13) use explicit "[printed in another volume]" markers. | Add consistent "[... printed in another volume]" markers for 1.14, Parts 2–6, and 8.1–8.6. |
| 7 | 6–9, 15–19 | duplicate | Principles and WBD/PDMA summaries are repeated across 1.4–1.12, 1.15, and 1.16 (e.g., 1.15.10, 1.15.11, 1.16, 1.16.1 are four consecutive transitional introductions/summaries on pp. 18–19). | Collapse 1.15.10–1.16.2 into a single transition and fold the two-bullet stubs of 1.4–1.12 into 1.15.1 (preserving section numbers as redirects if needed for cross-references). |
| 8 | 22, 27–28, 31–32 | other | Unanchored numerical thresholds in Part 7 (0.5% metric change, >10,000 audience, ≥0.5% harm uplift, 50,000 individuals, 20% KPI drop over 3 quarters, 90/120 days) lack register pointers or "charter threshold" labels (unlike the 100k/180-day figures on p. 5 and 5% on p. 34). | Explicitly label these as Charter adoption thresholds (as done on p. 5) or point to the register rows that calibrate them. |

## Rendering
- Page 14: Math/Greek glyph combination `ρ̄` in `(the ripple-counting instrument: ρ̄, k_eff)` renders with a slightly displaced macron over rho depending on font fallback, though legible in text extraction.
- Page 15: Bullet list under `1.15 Chapters` prints literal chapter numbers inside bullets (`• 1 Core Identity`, `• 2 Integrity`, etc.) without section numbers (`1.15.1`) or links.
- Page 19: Inconsistent hyphen/en-dash spacing in headings `1.16.2 Principles into Practice - Defining Ethical Actions Clearly`, `1.16.3 Ethical Decision-Making Process - The PDMA`, and `1.16.4 Wisdom-Based Deferral - Safeguarded Ethical Collaboration` (spaced hyphens `-` instead of em-dashes `—` or colons used everywhere else).
- Page 22: Flattened nested list under `7.2.2` — `• (i) further depth changes no metric axis by > 0.5 %, AND`, `• (ii) time/compute nears predefined limits.`, `• Then fall back to the non-maleficence fail-safe...` are rendered as top-level bullets instead of sub-bullets of `Termination Safeguard`.
- Page 25 & Page 30: In `7.3.1` (pp. 24–25), `7.3.2` (p. 25), and `7.5.2` (p. 30), lettered/titled items (`A. Tangible: ... B. Informational: ...`) are run together into single paragraphs instead of rendered as lists, unlike `7.3.4` (pp. 27–28) and `7.5.1` (p. 30).

## Effort estimate
About 4–6 hours of editing: 2 hours of mechanical cleanup (fixing list formatting, adding missing-section placeholders, harmonizing heading dashes, removing meta-editorial parentheticals, and de-duplicating 1.15.10–1.16.2) and 2–4 hours requiring the steward's rulings (rewording the "symmetry" framing in 1.13.2, scrubbing the vendor comparison on p. 12, and deciding whether to keep or re-anchor the 0.1% operations levy and Part 7 numerical thresholds).

<!-- model google/gemini-4-argon; 39 pages; prompt_tokens 25592; completion_tokens 3255; 46s -->
