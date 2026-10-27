# The Mathematics (ciris_constitution-1.0-rc12-maths.pdf, 22 pages)

**Care score:** 2
**One-line verdict:** A tightly argued, mathematically honest volume with explicit adversary scopes and integer-only wire determinism, needing only minor cleanup of version-history residue, one clipped code line, and a rounding-rule contradiction.

## Strengths
- **Explicit adversary scoping and non-claims:** Refuses to overclaim on privacy or deletion; bounds the noise floor against a specific baseline adversary $A_0$ ("Aggregation is not anonymization", p. 5), states the pull-only delivery limit on prohibited-content purges (p. 9), and explicitly disavows coercion resistance in secret polls (p. 21).
- **Deterministic, IEEE-754-free wire math:** Every normative gate (`n_eff`, L1 similarity, `StorageBudgetV1`) is specified in exact integer or fixed-point arithmetic (`n_eff * 2 >= source_count`, milli-units, `round(m × 1e6)` as `u64`) to prevent cross-implementation admissibility forks (pp. 7–8, 18).
- **Clear separation of wire vs. local heuristics:** Consistently draws the PIN-NORMATIVE vs. edge-internal line across all subsections (pp. 11, 12, 16, 18), keeping local RTT and retention priorities off the wire.
- **Self-contained cryptographic rationale:** The decision to omit RFC 6962 `0x00`/`0x01` prefixes in `wholeness_witness` and `member_commitment` is accompanied by the exact deduplication precondition that closes the odd-node-duplication malleability hazard and a normative caveat on when prefixes must be adopted (pp. 3, 7).

## Weaknesses
- **Rounding-rule contradiction in the census:** Page 20 defines the rounding grid step as "the larger of k and one unit in the value’s second significant figure: 47 publishes as 50, and 23 500 as 24 000", where $k = 10$ ("fewer than k = 10 owners"). For 47, one unit in the second significant figure is 1, and $\max(10, 1) = 10$, which rounds 47 to 50. For 23,500, one unit in the second significant figure is 1,000, and $\max(10, 1000) = 1000$. However, if the rule is "second significant figure", 47's second significant figure is the ones place (step 1); if $k=10$ overrides it to step 10, the text works, but "one unit in the value's second significant figure" is ambiguous (for 47, is it 1 or 10?) and should be stated as a formula ($10^{\lfloor \log_{10} x \rfloor - 1}$).
- **Version-evolution history in normative rules:** Section 6.1.2.1 (`AggregationMetaV1`) narrates v1/v2/v3 evolution ("unchanged at v3", "v2+: signed effective source count", "The v2 and v3 signed members close those two blindnesses in that order", "since v3 a lying n_eff is checkable", pp. 6–7), even though `version = 3` is the only valid value with no deprecation window (p. 6).
- **Undefined ticket/risk shorthands in normative prose:** Uses internal tracking labels like "(R9-b)", "(R9-a)" (p. 6), "the R9 residual" (p. 5), "The R9 negative" (p. 8), and "D6 preserved" (p. 18) without defining what R9 or D6 stand for in this volume (only once referencing `CC 8.3.1 R9` on p. 6).
- **Normative rules without RFC 2119 keywords:** On p. 9, "An implementation clamps $\bar{\rho}$ to $[0, 1]$ before applying it" states a mandatory security defense against fabricated anti-correlation in indicative mood instead of `MUST clamp`. Similarly, p. 20 states "Each aggregator publishes a partial" and "A published value is rounded" without `MUST`.
- **Unanchored calibration numbers in prose:** Page 8 states "Calibration (measured): byte-identical → 1.000; near-duplicate → ≥ 0.99; independent high-entropy → ≈ 0.667" and p. 11 mentions "the three calibration points as the executable similarity vector" without citing a register row in Section 6.1.2.1.2.

## Opportunities
- **Flatten `AggregationMetaV1` to v3:** Removing the v1/v2 historical commentary on pp. 6–8 and simply stating the v3 preimage and its invariants would shorten Section 6.1.2.1 by a third and obey the house rule against history in the Parts.
- **State the `mass_to_fixed` rounding tie-breaker:** On p. 8, `mass_to_fixed(m) = round(m × 1e6)` is used right after banning IEEE-754 decision paths. Defining `mass_i` directly as a fixed-point integer numerator/denominator or specifying round-half-to-even (and what type `m` is before `mass_to_fixed`) would eliminate the last floating-point ambiguity at the aggregator boundary.

## Threats
- **Unverifiable sender-routing in the census (`CC 6.1.9`):** Page 21 admits that "Until the seat order is a signed row, the door cannot check that a sender addressed the drawn pair: it checks only that each recipient is a seat, so a sender may address any pair". A hostile reviewer will point out that this allows a malicious node to cherry-pick a colluding pair of aggregator seats (if at least two seats in the federation are compromised) to bypass the validity proof and stuff the census, or allows two colluding seats to be targeted. Moreover, "Until the seat order is a signed row" reads as an unfinished roadmap item inside a 1.0 normative specification.
- **`mass_to_fixed(m)` input type ambiguity:** Section 6.1.2.1.2 (p. 8) bans IEEE-754 paths because they fork admissibility, yet defines `mass_to_fixed(m) = round(m × 1e6)` where `m` is described on p. 7 as `fraction_i`. If an aggregator computes `fraction_i` in floating point before calling `mass_to_fixed`, two honest aggregators can sign different `mass_commitment` roots on the same inputs.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 6 | rendering | Line clipped in `AggregationMetaV1` prose: `then u32_be(max_source_mult` runs off the right margin mid-identifier. | Wrap or hyphenate `u32_be(max_source_multiplicity)` in the markdown source. |
| 2 | 21 | stale | "Until the seat order is a signed row, the door cannot check that a sender addressed the drawn pair" — roadmap/unfinished mechanism in normative text, leaving a seat-shopping vector open. | Either specify the signed seat-order row for 1.0 or state the limitation as a permanent rule of the current protocol without "Until...". |
| 3 | 7–8 | unclear rule | `m_i = mass_to_fixed(fraction_i)` and `round(m × 1e6)` do not specify exact integer division or tie-breaking for `fraction_i`, despite banning IEEE-754 in the same section. | Define `m_i` via integer arithmetic: e.g., `(member_bytes * 1_000_000 + total_bytes / 2) / total_bytes`. |
| 4 | 6–8 | editorializing | Version history ("at v2, then... at v3", "since v3 a lying n_eff is checkable") retained in `AggregationMetaV1` even though v3 is the only admissible version. | Strip v1/v2 history; state `version = 3` as the sole layout and rule. |
| 5 | 9 | unclear rule | "An implementation clamps $\bar{\rho}$ to $[0, 1]$ before applying it" lacks RFC 2119 keyword on a critical Sybil/collusion defense. | Change "clamps" to "MUST clamp". |
| 6 | 5–8, 18 | other | Undefined internal shorthand labels (`R9`, `R9-a`, `R9-b`, `D6`) used as nouns in the prose. | Replace with descriptive names (e.g., "the multiplicity residual", "ephemeral reachability") and keep `CC 8.3.1` as a parenthetical ref. |
| 7 | 11 | other | Domain separator list in `6.1.3` omits `b"AGG-META-v1\0\0\0\0\0"` (p. 6), `b"CIRIS-STG-BUDGET"` (p. 15), and `b"CIRIS-WANT-HAVE\0"` (p. 15), while listing `b"CIRIS-CLAIM-v1\0\0"` which appears nowhere else in the volume. | Synchronize the domain-separator summary list in 6.1.3 with the subsections of Part 6. |
| 8 | 20 | unclear rule | Census rounding step "the larger of k and one unit in the value’s second significant figure" is prose-ambiguous for 2-digit numbers. | Write explicitly as $\max(k, 10^{\lfloor \log_{10} v \rfloor - 1})$. |

## Rendering
- **p. 6:** Right-margin clipping / overfull hbox on the line `The version members are appended in version order — u32_be(n_eff) at v2, then u32_be(max_source_mult` (truncates `multiplicity)`).
- **p. 15:** Code block line wrapping inside comments in `StorageBudgetV1` (`// floor reserved for pinned corpus (MUST be <=` wrapped to `budget_bytes)`) and `CorpusWantV1` (`// the scope this want draws budget from (NEVER self/` wrapped to `family)`), which is readable but visuallyragged.

## Effort estimate
About 2–3 hours of mostly mechanical editing to fix the clipped line, synchronize the domain separator list, strip v1/v2 history, and tighten RFC 2119 keywords, plus one brief steward ruling on whether integer division for `mass_to_fixed` should be pinned for 1.0.

<!-- model google/gemini-4-argon; 22 pages; prompt_tokens 21065; completion_tokens 2474; 46s -->
