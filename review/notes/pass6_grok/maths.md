# The Mathematics (ciris_constitution-1.0-rc12-maths.pdf, 21 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The substrate rules are mostly stated as checkable predicates with explicit limits, but several of those statements contradict each other and two normative byte layouts are broken, so this volume needs steward rulings before 1.0.

## Strengths
- The below-floor MUST is scoped to adversary A0 and forbids reading an A0 result as anonymity or erasure against side information: "Aggregation is not anonymization" (pp. 4–5).
- The odd-node Merkle construction states the malleability, the dedup rule that is supposed to close it, and a normative ban on cross-verifying it with the CC 5.3.1 RFC 6962 log (p. 3).
- Ballot secrecy is limited to two non-colluding tally members, and coercion resistance is explicitly not claimed (p. 21).
- The purge rule states a delivery limit: a purge attestation is not "the bytes are gone", and unreachable holders are outside the mesh's reach (pp. 9–10).

## Weaknesses
- Same page, two rules for \(k_{\mathrm{eff}}\): a deny-on-low threshold "is therefore safe", then "an implementation MUST NOT gate on" \(\bar\rho\), \(k_{\mathrm{eff}}\), or any ratio derived from them (p. 8).
- Withdrawn content "descends — fewer holders, then none (CC 6.1.2.2)" (p. 12), but N5 on the same page, and CC 6.1.2, say revocation "MUST NOT be required to — destroy the collective gist" (pp. 6, 12) and ordinary descent "never terminates at zero" (p. 9).
- "Every CC 6.1 object" "never instantiates a CC 2.1 Contribution" and "never enters CC 2.6.1 JCS" (p. 10); the census composite "is a CC 2.1 scores row" whose signed members are the CC 6.1.2.1 inputs (p. 20).
- "The only path from measurement to action is the mesh-config plane" (p. 2; repeated p. 19), but a one-period fall freezes "the base and every narrowing relief" without a new steward signature (p. 20), and the census is also the base CC 4.5.13 counts against (p. 19).
- Privacy is stated as "only the two aggregators of a period acting together" (p. 19). Later: "Until the seat order is a signed row, the pair of seats for a period is the sender's choice among seats and the door checks only that each recipient is a seat" (p. 21).
- The ratcheted base "falls by at most a tenth per period (a larger fall is clipped to that tenth)", then "A fall of more than a third in one period is read as a partition" (p. 20). If "fall" is the published base, the partition rule cannot fire; the text does not say it means the raw count.
- 6.1.4 puts `retention_priority` in the freeze-gate vector list (p. 11); 6.1.3 and the PIN line say it is edge-internal and "MUST NOT be over-pinned" / "never on the wire" (pp. 11–12).
- 6.1.7 says the mechanisms of this Part are "gated by steward binding and founder quorum (N1) and the chain-length and cycle budget (N2)" (p. 18). N1 and N2 are defined only for `recursive_trust_bootstrap` (p. 19), after N3–N8, and do not gate census, replication, or the witness.
- Normative pins with no derivation in this volume: \(\varepsilon = 0.05\) (p. 4), `min_ratio = 0.5` (p. 8), similarity \(0.950\) and "near-duplicate \(\rightarrow \geq 0.99\)" marked "Calibration (measured)" (p. 8), \(k = 10\) (p. 20), "nine instances with eight twins" (p. 21). Unverifiable from here. The \(0.667 \approx 1 - 85/255\) sketch is at least local arithmetic (p. 8).
- Code and model paths sit in the Part after p. 1 says the register pins the repositories: `lean:coherence-ratchet:Core.BaseIdentity` (p. 8), `formal/census_ballot` (p. 21). "why v3 exists" (p. 8) is design history. Domain separators end in "etc." (p. 11). "CEWP-1.0" is undefined (p. 12). "rounded to a grid of max(k, two significant figures)" mixes a count with a significant-figure rule (p. 20). "is said to be —" has no complement (p. 10). "With a holder a whole copy" is missing words (p. 13).

## Opportunities
- After a ruling, delete one of the two \(k_{\mathrm{eff}}\) sentences on p. 8 so a deny-threshold is either permitted or forbidden, not both.
- Make the 6.1.5 opening match N5: either "then none" applies only to chunk holders of unmarked items, or withdrawn content is not in that sentence (p. 12).
- Align p. 10 with p. 20 in one edit: either the census composite is not "a CC 2.1 scores row", or the "every CC 6.1 object" sentence stops covering it. Same pass can say whether that row is JCS or the binary preimage.
- Replace "etc." (p. 11) with the closed separator list already named in the subsections, and state the dominance test as integer arithmetic (`n_eff * 2 >= source_count`) so it matches the no-IEEE-754 rule already on p. 8.
- Move the Lean and `formal/census_ballot` paths out of the Part, as p. 1 already tells the reviewer to start from the register.

## Threats
- A lawyer can quote p. 12 against pp. 6 and 9 and say the document both requires the gist to survive revocation and requires withdrawn items to reach "none".
- A regulator can quote the A0 limit (pp. 4–5) against the census opening (p. 19) and the seat-choice admission (p. 21): information-theoretic privacy holds only for a pair the sender did not get to choose, and that pair is not yet a signed row. Colluding aggregators "can drop returns or invent tokens" (p. 21) sits beside "the stuffing ceiling, enforced rather than trusted" (p. 19).
- An implementer can mis-encode AggregationMetaV1 from the clipped v3 append sentence (p. 6) or treat `budget_bytes)` as a preimage field (p. 15), and can refuse the redundancy keys forever: their consumer "arrives with the durability tier (until it does, rule (2) refuses them)" (p. 13). `hard_case:*` is only a "reserved-prefix candidate" (p. 4) while peers MUST surface equivocation as that prefix (pp. 4, 15).
- The effective-count discount is advertised as a mechanised result that binds "by being true" (p. 1) and then withdrawn as a gate (p. 8). A hostile reviewer will call that a leftover from an earlier design, along with "R9", "HE-300" (p. 11), and the "LP pair-pinning gate" that "nothing here rests on" (p. 5).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 8 | contradiction | "A threshold that denies on low \(k_{\mathrm{eff}}\) is therefore safe" and it "MUST NOT be the sole gate", then "MUST NOT gate on" \(\bar\rho\), \(k_{\mathrm{eff}}\), or "any ratio derived from them". | Keep one rule. Delete the other. |
| 2 | 12 | contradiction | "withdrawn, descends — fewer holders, then none (CC 6.1.2.2)" vs N5 on the same page: gist need not be destroyed. p. 9: ordinary descent "yields the blur, never an empty/destroyed object." | Restrict "none" to chunk holders, or drop "withdrawn" from that sentence. |
| 3 | 10, 20 | contradiction | p. 10: every CC 6.1 object "never instantiates a CC 2.1 Contribution" and never enters JCS. p. 20: "The composite is a CC 2.1 scores row". | One canonicalization story for the composite. Strike the universal claim or the scores-row claim. |
| 4 | 19, 21 | overclaim | p. 19: only the period's two aggregators together can read a return. p. 21: until a signed seat row exists, "the pair of seats for a period is the sender's choice". | State the sender-choice gap in the opening rule, or stop claiming a designated pair. |
| 5 | 20 | contradiction | Base fall "clipped to that tenth"; a fall "of more than a third in one period" freezes the base and narrowing reliefs. | Say whether the third is raw count or ratcheted base. If raw, write "raw". |
| 6 | 2, 20 | contradiction | "the only path from measurement to action is the mesh-config plane" (p. 2) vs automatic freeze of "every narrowing relief" (p. 20) and the CC 4.5.13 base (p. 19). | Name the ratchet and the governance base as measurement paths, or stop saying there is only one. |
| 7 | 11, 12 | contradiction | Freeze gate includes `retention_priority` (p. 11); PIN line says it is "edge-internal (never on the wire)" (p. 12). | Remove it from the vector list or stop calling it unpinned. |
| 8 | 6 | rendering | v3 append order reads "u32_be(max_source_mult" then "∥ mass_commitment[32] at v3" — identifier clipped, parenthesis gone. | Rejoin `max_source_multiplicity` and close the parenthesis. |

## Rendering
- p. 6: the prose formula clips `max_source_multiplicity` to `max_source_mult` at the line break and drops the closing `)`.
- p. 15: in the StorageBudgetV1 preimage, the comment wraps so `budget_bytes)` sits on its own line, where it can be read as a field. The CorpusWantV1 comment also splits "NEVER self/ family" across lines (same page).
- p. 5: the pyramid series is printed "1/N2", not a superscript 2.
- p. 19: not-equal is the combining sequence "̸=" in "trust ̸= membership" and "TRUST̸=MEMBERSHIP", not a single glyph.
- No empty sections, duplicated page blocks, or literal `**` / stray backslashes seen. The p. 10 "is said to be —" gap reads as a cut sentence, not a glyph failure.

## Effort estimate
A day of editing: a few hours of mechanical repair (clipped formulas, "etc.", code paths, the dangling sentences), and the rest steward rulings on which of each contradictory pair stands, including the unfinished "until" clauses for seats and redundancy-key consumers.

<!-- model x-ai/grok-4.7; 21 pages; prompt_tokens 21342; completion_tokens 20429; 223s -->
