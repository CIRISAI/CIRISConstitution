# The Mathematics (ciris_constitution-1.0-rc11-maths.pdf, 21 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The wire layouts are mostly implementable, but the volume contradicts itself on who it binds, which result is mechanised, whether census rows sit inside the frozen attestation envelope, and whether withdrawn content ends at none or at a retained blur.

## Strengths
- The below-floor obligation is scoped to adversary A0 and expressly refuses to treat an A0 result as erasure against side information: "Aggregation is not anonymization" (p. 4–5).
- Prohibited-content termination at zero is carved out from blur-forever, with the purge-delivery limit stated rather than implied (p. 9).
- Ballot secrecy is limited to two non-colluding tally members, and coercion resistance is explicitly not claimed (p. 21).
- StorageBudgetV1 and CorpusWantV1 preimages, sort/dedup rules, and equivocation handling are specified as bytes, not as intent (p. 14–15).

## Weaknesses
- The cover disclaims binding — "Whom it binds. Nobody directly" — while the body is a run of implementer MUST/MUST NOT rules (p. 1 vs p. 2 onward).
- Two sentences on the cover name different "one" mechanised results: "the effective source count that gates aggregation (the one result here with a Lean witness)" and "One witness is mechanised, the census ballot model under formal/census_ballot" (p. 1). Page 9 mechanises a third object, k_eff, and then says an implementation "MUST NOT gate on" it.
- "fewer holders, then none (CC 6.1.2.2)" (p. 12) cites the section that says ordinary descent "yields the blur, never an empty/destroyed object" (p. 9) and that revocation "MUST NOT be required to — destroy the collective gist" (p. 5).
- "Every CC 6.1 object … never instantiates a CC 2.1 Contribution, never enters CC 2.6.1 JCS" (p. 10), but the census composite "is a CC 2.1 scores row" (p. 20). Which canonicalization a verifier applies is unspecified.
- The aggregation domain separator is written `b"AGG-META-v1\0\0\0\0\0"` (12 + 5 = 17 bytes) and labelled "16-byte domain separator (exact)" (p. 6).
- "below the floor" means the recoverability boundary (p. 4), the census k-withholding rule (p. 20), and the governance ratchet floor (p. 20), often without a qualifier.
- History and asides the house style forbids: "A reviewer who wants to kill a result" (p. 1); "instead of fighting" (p. 4); "named bet" (p. 4); "Stated honestly" (p. 9); "Considered and not adopted" (p. 18); "verified by an unspecified upstream tier" (p. 18). Code and ticket pointers: `formal/census_ballot`, `lean:coherence-ratchet:Core.BaseIdentity`, "R9" (p. 5, p. 8–9, p. 21).
- Normative "etc." in the domain-separator list (p. 10). Undefined in this volume: "M-1" (p. 2, p. 11), "brain" (p. 5), "CEWP-1.0" (p. 12), "HE-300" (p. 11).
- Numbers with no derivation visible here: ε = 0.05 (p. 4), min_ratio = 0.5 (p. 7), similarity 0.950 and "near-duplicate → ≥ 0.99" (p. 8), k = 10, "at most eight per owner", "a tenth", "a third", "two thirds" (p. 19–20), "nine instances with eight twins" (p. 21).

## Opportunities
- Rewrite the cover "Whom it binds" sentence so it matches the MUSTS, or mark each MUST as argument rather than rule. One steward ruling, then a mechanical pass.
- One sentence distinguishing noise floor, holder floors, census k-floor, and ratchet floor, and use the qualified name at p. 12 and p. 20.
- Put the broken preimage sentence (p. 6) on its own line and make the AGG-META literal match its length comment (drop one NUL, or say 17).
- Delete the "Considered and not adopted" subsection, the "named bet" parenthesis, and the Lean/formal paths, leaving only register-row names as p. 1 already instructs.
- Close the separator list at p. 10; replace "etc." with "the separators named in this Part" or a register pointer.
- Finish the two truncated sentences (p. 9, p. 19) with the term that was cut.

## Threats
- A lawyer can quote p. 1 ("Nobody directly") against any MUST in the volume, and can quote p. 10 against p. 20 to argue the census composite is both forbidden from and required to be a CC 2.1 scores row — so JCS and the binary preimage are both "conformant."
- Two implementations that follow p. 6 literally will disagree on the first 16 versus 17 bytes of every AggregationMetaV1 signature. The text calls that class of disagreement "a vector-invalidating wire change" (p. 6).
- A hostile reviewer will note that the Lean names on p. 9 witness k_eff, which "MUST NOT" be a gate, while the aggregation gate is n_eff, which is not the named witness — so "the one result here with a Lean witness" (p. 1) is false on its face.
- Right-to-be-forgotten is sold as one mechanism with durability (p. 4), but a withdrawn item both keeps a gist (p. 5, p. 9) and descends to "none" (p. 12), and a purge "is not 'the bytes are gone'" (p. 9). A regulator can treat that as three different erasure claims.
- p. 2 and p. 19 say measurement changes behaviour "only" through mesh-config, then p. 19 makes the census the base CC 4.5.13 counts governance against. That is a second path from measurement to a decision.
- p. 10 says wire-identity for CC 6.1.2.1–.3 is "reproducible from the text alone"; p. 11 says those same preimages are "pinned against the reference impl." The impl, not the Part, is the oracle.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 1 | contradiction | "Whom it binds. Nobody directly" vs implementer MUSTS throughout Part 6 | One ruling: this volume binds implementers, or the MUSTS are not rules. Align the cover sentence. |
| 2 | 10, 20 | contradiction | CC 6.1 objects "never" instantiate a CC 2.1 Contribution or enter JCS; census composite "is a CC 2.1 scores row" | State which object the composite is, and which canonicalization applies. Delete the other sentence. |
| 3 | 1, 9 | contradiction | Cover: effective count that gates aggregation is the one Lean witness; also the census model is the one witness. Body mechanises k_eff and says MUST NOT gate on it | Name the census model and the k_eff witness separately; do not call either the aggregation gate. |
| 4 | 6 | contradiction | `AGG-META-v1` plus five NULs is 17 bytes, labelled "16-byte domain separator (exact)" | Make the literal and the comment the same length. |
| 5 | 5, 9, 12 | contradiction | Gist "MUST NOT" be destroyed and descent "never" yields an empty object; withdrawn items descend to "none" | Replace "then none" with the end-state 6.1.2.2 actually specifies, or change 6.1.2.2. Steward must pick one. |
| 6 | 6 | rendering | Formula clipped mid-token: "u32_be(max_source_mult" then "∥ mass_commitment[32]" | Reprint the v2/v3 suffix unbroken on its own line. |
| 7 | 9 | other | "is said to be — the obligation on reachable holders is total" | Restore the missing predicate after "said to be". |
| 8 | 20 | unclear rule | "rounded to a grid of max(k, two significant figures)" mixes a count with a precision rule; "floor" is overloaded | State the grid in one unit, and name which floor. |

## Rendering
- p. 6: the version-suffix sentence breaks inside `max_source_multiplicity` and resumes at `∥ mass_commitment[32]`, so the formula is not readable as bytes.
- p. 9: truncated sentence, "and is said to be —".
- p. 19: truncated sentence, "only the two aggregators of a period acting together could."
- p. 14: preimage comment wraps so `budget_bytes)` sits on its own line inside the listing.
- p. 15: `(NEVER self/` wraps so `family)` sits on its own line inside the listing.
- No literal `**`, no missing glyph, no empty section, no duplicated page block seen.

## Effort estimate
About a day: clipping, the separator length, "etc.", and the editorial/code-pointer cuts are mechanical; the binding sentence, the 1+4 status of the census composite, blur versus "none", and which count may be gated need the steward's rulings before the sentences can be rewritten.

<!-- model x-ai/grok-4.7; 21 pages; prompt_tokens 21116; completion_tokens 15725; 177s -->
