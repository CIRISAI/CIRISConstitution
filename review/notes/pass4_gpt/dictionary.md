# The Dictionary (ciris_constitution-1.0-rc11-dictionary.pdf, 109 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The catalogue needs a substantive consistency pass: several admission rules contradict their explanations, and security and legal guarantees exceed what the stated mechanisms establish.

## Strengths
- The text distinguishes signature verification from truth verification for location claims, and explicitly limits what key rotation repairs after compromise (pp. 49, 58).
- Several boundaries are stated rather than concealed: custody reports do not prove possession; fair exchange does not provide atomicity; general multi-tenant hosting remains outside the specified actor/node relation (pp. 19, 55, 92).

## Weaknesses
- Catalogue entries and their detailed rules disagree. `consent:replication` is “signed” in the catalogue but “positive-only” in its conformance rule; `observation:access_assumption` says “score fixed at +1” immediately above “Polarity: signed”; the supposedly exhaustive consent leaf list omits `community_trust`, which is subsequently defined (pp. 23, 38, 41, 43, 64).
- A stale status sentence says the capacity read boundary “remains deferred and non-normative,” whereas the later section explicitly makes its composition-context rule normative (pp. 31, 84–85).
- Some examples conflict with the wire rules: `ledger:head:usd:v1` uses lowercase currency despite the explicit rule that “USD” is correct and “usd is not”; the household example wraps under “each member’s identity key,” whereas the encryption section requires occurrence encryption keys and excludes recipients without them (pp. 10, 28, 52, 58).
- History and implementation commentary remain embedded in rules: “formal/membership,” “formal/self_roster,” “before the two-path door existed,” the proposed retirement of operational record kinds “until that amendment lands,” and the LensCore workspace-fold example (pp. 17, 62–63, 66, 93). These belong outside the normative Parts under the stated house rules.
- The guardianship vocabulary contradicts itself: “responsible for a ward, never a holder of one” becomes “a guardian holds a person” two pages later (pp. 102, 104).

## Opportunities
- Reconcile each catalogue row against its detailed section, concentrating on polarity, closed leaf sets, emitter rules and valid examples. This would remove several implementation disagreements without changing the architecture (pp. 10, 23, 38, 41–43, 64).
- Replace repeated design defenses with short rules and cross-references. The ledger “Design notes,” capacity-composition alternatives and adult-stewardship defenses obscure the operative requirements (pp. 31, 70–72, 96–102).
- Complete the existing timing requirements: `HARD_DEADLINE`, the T2 review cadence and the teen standing-grant “hard maximum duration” have no supplied value or clear source of authority in their clauses. Name the existing controlling parameter rather than leaving apparently enforceable limits undefined (pp. 98, 100, 106).

## Threats
- A hostile implementer can follow the canonical-binding rule literally: claim another person’s hash and obtain withdrawal authority, even though the text expressly supplies no proof-of-control requirement and admits competing claims (pp. 77–78).
- A regulator could challenge “proof of deletion” based on withdrawal or supersession, particularly when the volume also says withdrawn records remain in the audit chain (pp. 44, 49).
- Legal and security claims are overstated: “regulator-endorsed retention shape” lacks a pinpoint EDPB source; “defeated by construction” overstates the conservatorship safeguards; and “discharging” the AI Act marking obligation is stronger than demonstrating a marking mechanism. The regulatory assertions are unverifiable from here (pp. 70, 102, 107–108).
- Prohibited comparative/design advocacy remains: other commerce systems “use the same mechanism,” the “eltoo argument against Lightning-class penalties,” and “as HLS, OCI and UnixFS all do.” These are not necessary to state CIRIS’s rules (pp. 69, 71, 74).
- “Guaranteed delivery” and rate-limiting that must fail open “for a genuine victim” are absolute obligations without a stated way to identify that condition or overcome unavailable endpoints. An implementer cannot infer a testable guarantee from the offline-queue requirement alone (p. 105).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 77–78 | contradiction | After an admitted canonical binding, withdrawal “is now admitted,” but the same section says authorization is “consumer-policy, not wire” and that a competing claimant is admitted too. Advisory identity testimony thereby grants destructive authority. | Obtain a steward ruling on the intended authority boundary; reconcile the withdrawal consequence with the existing authorization rules. |
| 2 | 44, 49 | overclaim | D1 says deletion is proven if a row was “withdrawn, superseded, or hard-deleted.” The location section says a withdrawn record “remains in the audit chain.” Neither withdrawal nor supersession establishes erasure of retained bytes. | Separate evidence of lifecycle change from evidence of deletion; align D1 with the actual retention and bytes-plane rules. |
| 3 | 95, 103–104 | contradiction | Page 95 says an adult band at self level “satisfies the band,” reserving verified assurance for sensitive spaces. Pages 103–104 forbid upward graduation by self-declaration and require provider-level assurance to exit child protection or unlock adult content. | State the stricter requirement in the base ladder section and remove the permissive reading, or explicitly resolve which rule governs. |
| 4 | 98, 100, 102 | contradiction | Prior-will activation requires “NOT a fresh CC 4.3 WA adjudication,” but the T2 table requires a “WA due-process gate.” T1 allows provider-level asset-preservation powers once prior-will or WA authority exists; the summary instead requires a panel for “any continuing or asset-bearing power.” | Reconcile the predicate, tier table and summary into one account of prior-will, provider and panel authority; specify the controlling timing parameters. |
| 5 | 6, 9 | other | “RFC 6962 padding: duplicate last leaf to next power of 2” misstates RFC 6962’s Merkle-tree construction, which recursively splits at the largest smaller power of two rather than duplicating leaves. | Correct the algorithm or identify it as a distinct construction; reconcile the provenance claim and its canonical-byte contract. |
| 6 | 109 | contradiction | Same-type concurrent composers are resolved by timestamp and ID, but mandatory deduplication uses only `(references_attestation_id, attestation_type, attesting_key_id)`. Distinct candidates in precisely that race share the dedup key. | Distinguish exact replay from competing composer rows and make deduplication consistent with the stated precedence rule. |
| 7 | 23, 38, 41, 43, 64 | contradiction | Catalogue polarity and closed-set declarations disagree with detailed rules: signed versus positive-only replication grants; signed versus fixed-+1 access observations; an exhaustive consent list missing `community_trust`. | Synchronize the catalogue and semantic clauses, then regenerate and replay the existing registry vectors. |
| 8 | 31, 84–86 | stale | “The read boundary remains deferred and non-normative” survives beside a later normative composition-context rule and explicit read/redaction requirements. | Replace the obsolete status sentence with an accurate cross-reference and distinguish read access from inference-loop use. |

## Rendering
- A literal escape survives in “dimension\’s” (p. 85).
- “The CC 1.13+4 lockdown holds” is a malformed reference or joined-text typo (p. 72).
- The common Source-field code block has broken continuation alignment, including isolated fragments such as “the” and “allocation”; reflow it for readable field-to-description association (p. 76).
- All 109 supplied page blocks were reviewed, but only their text representation was available. Actual PDF clipping, missing glyphs and page-edge overflow could not be verified.

## Effort estimate
Approximately 24–40 hours of editing and consistency checking, with steward rulings needed on authority, deletion, age assurance and incapacity tiers; catalogue synchronization, prose cleanup and rendering repairs are mostly mechanical.

<!-- model openai/gpt-6-astra-pro; 109 pages; prompt_tokens 284455; completion_tokens 6569; 84s -->
