# The Mathematics (ciris_constitution-1.0-rc11-maths.pdf, 21 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The volume states important limits explicitly, but incompatible aggregation, census and verification rules prevent implementation from the text alone.

## Strengths
- The below-floor guarantee is explicitly procedure-relative: the text excludes side-informed adversaries and says “Aggregation is not anonymization” (pp. 4–5).
- The prohibited-content rule distinguishes a holder’s destruction obligation from guaranteed delivery of a purge (p. 9).
- The census states its non-collusion assumption and disclaims coercion resistance; the conformance section separately acknowledges the absence of operational benchmarking (pp. 11, 21).

## Weaknesses
- Storage nodes “never encode or decode stored content,” yet a “pure fabric node performs the entire retention function,” including resampling and content-similarity measurement. The text never reconciles sealed-chunk storage with these payload-dependent operations (pp. 2, 6, 8, 11).
- Census composites and ballots inherit the content-multiplicity gate without defining what content is compared. Equal voting weight establishes the mass ratio, not content diversity; identical ballots could fail the stated gate (pp. 8, 20–21).
- The deterministic mass calculation leaves `round(m × 1e6)` without a tie-breaking convention or overflow treatment, despite requiring byte-identical admissibility decisions (p. 8).
- “Calibration (measured)” gives “near-duplicate → ≥ 0.99” without a visible dataset or measurement source; the cosine claim “even independent members score ≈ 0.75” also lacks stated sampling assumptions. These are unverifiable from here. The separate ≈ 0.667 figure does at least show its uniform-byte calculation (p. 8).
- The effective-count assertion that it “can overstate effective diversity and never understates it” does not define the reference quantity or supply an argument for that direction. The named mechanised results concern bounds, monotonicity, the ceiling and a fully correlated clique—not explicitly this general claim (p. 9).
- Implementation history and editorial commentary remain in the rules: “a candidate instrument exists … has not been ported” (p. 5), “why v3 exists” (p. 8), “whose consumer arrives with the durability tier” (p. 13), and “Considered and not adopted … would need its own ruling” (p. 18). Code/model pointers also remain on pp. 1, 9 and 21 rather than solely in the register.

## Opportunities
- Reconcile the scope of existing rules: identify which actor performs payload-dependent aggregation, which census checks actually apply, and whether census rows are exceptions to the substrate-framing rule. This would remove several implementation forks without adding mechanisms (pp. 6–8, 10, 20–21).
- Move the four-period interpretation from the closing model discussion into the census’s normative field definition. Readers should not need the final paragraph to discover what the activity bit means (pp. 20–21).
- Replace implementation-history explanations with present-tense requirements and register references; attach the calibration claims to their evidence rows (pp. 5, 8, 13, 18).
- Correct the preimage description and repair the clipped identifier before regenerating the PDF; these are small edits with direct interoperability value (p. 6).

## Threats
- A literal implementation could reject a unanimous secret poll: the multiplicity rule requires `max_source_multiplicity · n_min ≤ source_count`, with default `n_min = 2`; identical source ballots would give multiplicity equal to the entire electorate. The tally section nevertheless applies that same gate (pp. 8, 21).
- An implementer must choose between “never partial inclusion proofs” for `member_commitment` and the census requirement that contributors have an “inclusion path against member_commitment_hex.” This is particularly exposed because the Merkle construction’s safety argument relies on its restricted uses (pp. 3, 7, 21).
- Two teams could build different census signing paths: “Every CC 6.1 object … never instantiates a CC 2.1 Contribution” conflicts with “The composite is a CC 2.1 scores row” (pp. 10, 20).
- The claim that two colluding aggregators can invent tokens only within a bound set by the directory’s “rounding grid” is stronger than the argument shown. No binding between those invented tokens and that directory count is described here; the same paragraph acknowledges that seat allocation is not enforced (p. 21).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 8, 20–21 | unclear rule | Content-multiplicity admission is applied to census returns and ballots without defining its comparison payload; literal application can reject identical legitimate responses. | State the intended census interpretation and reconcile it with the existing gate, including the identical-response case. |
| 2 | 2, 6, 8, 11 | contradiction | Nodes “never encode or decode stored content,” but a pure fabric node performs retention requiring resampling and payload comparison. | Clarify the existing actor and data-access boundary; make both statements describe the same permitted operations. |
| 3 | 3, 7, 21 | contradiction | `member_commitment` is verified “never [by] partial inclusion proofs,” but census contributors check an inclusion path against it. | Reconcile the permitted proof use and its safety justification; retain one unambiguous verification contract. |
| 4 | 10, 20 | contradiction | Every CC 6.1 object is declared non-attestation framing, while the census composite is explicitly a CC 2.1 scores row. | Narrow the blanket statement to its intended scope and identify census row canonicalisation explicitly. |
| 5 | 6 | contradiction | “Each older preimage is a byte-exact prefix of the next,” although the early `version` field changes between versions. | Say that fields are appended in version order, but complete preimages differ at the version field. |
| 6 | 20–21 | unclear rule | Page 20 says the cell contains “active this period” and members recompute activity over four periods from partials; p. 21 says the cell itself contains the owner’s recent-window bit, “not something recoverable from a sum.” | Put the latter definition in the normative return description and remove the incompatible reading. |
| 7 | 8 | unclear rule | `round(m × 1e6)` is not a complete deterministic conversion rule. | Specify the intended rounding convention and admissible range, aligned with the existing vectors. |
| 8 | 6 | rendering | The version-order paragraph cuts off `u32_be(max_source_mult…` at the right edge. | Break the expression at a safe boundary or set it as a wrapping display. |

## Rendering
- Page 6: the version-order paragraph visibly truncates the long `max_source_multiplicity` expression.
- Page 15: the heading “6.1.5.3 Durability at every tier (normative)” is stranded at the foot of the page; its entire body starts on p. 16.
- Page 15: code comments wrap into separate lines, notably `budget_bytes)`, `deduplicated`, and `family)`. Keep wrapped comment text visually marked as commentary rather than apparent preimage content.
- No other definite rendering defects are apparent in the supplied page representations.

## Effort estimate
Approximately 16–24 hours of editing and focused consistency checking; typography and history removal are mechanical, but aggregation access, census gate semantics, proof use and canonicalisation need the steward’s rulings.

<!-- model openai/gpt-6-astra-pro; 21 pages; prompt_tokens 66508; completion_tokens 5551; 75s -->
