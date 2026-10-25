# The Reader’s Policies (ciris_constitution-1.0-rc11-policies.pdf, 35 pages)

**Care score:** 5  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** Several admission, consent and key-distribution examples contradict their governing prose, so this volume needs a consistency rewrite before implementers can safely follow it.

## Strengths
- Policy A is explicitly identified as the conformance floor, with aggregation rules stated separately (pp. 4–5, 32).
- The removal rule distinguishes fresh per-write keys for self/family from epoch rotation for communities, and explicitly disclaims retroactive removal of access (pp. 26–27).

## Weaknesses
- Family-admission pseudocode returns from every consensus branch before reaching the new member’s acceptance check, contradicting “nobody joins without their own consent, under any protocol” on the same page (p. 19).
- The partnership signing contract specifies “bare scores,” but the ratification function searches for `subject_kind == "consent_record"` with different fields. The prescribed login emissions therefore do not satisfy the prescribed ratification query (pp. 24–25, 28–30).
- Membership admission explicitly rejects additions through supersession, yet the geographic joining example adds Alice through `supersedes` and omits her signed acceptance. Community and family resolution still walk supersedes chains rather than explaining how the stated roster planes are folded (pp. 8–10, 19, 26).
- Community onboarding says `from_join` means “no retroactive key_grant cascade,” while Policy L says held past community epochs “are re-wrapped to every active member’s devices.” A newcomer also receives the current epoch key, which can open earlier content encrypted under that key (pp. 7, 12, 18).
- The promise of reproducibility by anyone holding the same rows omits the evaluation time: membership resolution uses “the resolving Consumer’s own clock” while requiring every implementation to “resolve identically” (pp. 1, 9).
- The aggregation table still names `attestation:l*` as a hard-constraint example, although Policy I says that form “is rejected at admission” (pp. 5, 31).
- Rule text retains development history and attribution: “7 stories,” “12 stories,” “10 stories,” “6 stories,” “8 stories” and “(1 reviewer)” have no visible source; “Per Miranda Fricker’s epistemic injustice,” “Closes G3,” “the operator the seed lacked,” and “replace infra:join_communities outright” belong to rationale or migration material, not rules (pp. 4–5, 13, 23).
- Implementation references and editorial assurances remain throughout: “Per CIRISNodeCore,” “Why this is still 1+4,” “the four implementations,” “Registry owns these member sets,” the install endpoint, and repeated “no new structural primitive” commentary (pp. 17–18, 20, 22, 25, 29, 31, 33). Policy C’s “less common in practice” is an unsupported empirical claim (p. 35).

## Opportunities
- Reconcile each executable example with its immediately preceding rule: replace the stale membership and partnership shapes, and make all admission checks reachable before returning.
- Give the existing encryption exceptions explicit scope. Updating the universal statements on p. 7 to acknowledge the institutional rules on pp. 13–14 would remove conflicting instructions without adding policy.
- State the existing time dependency in the reproducibility promise, and use the same evaluation-time terminology in resolution functions (pp. 1, 9).
- Move stress-test counts, migration explanations, implementation ownership and “1+4” defenses out of the rule text. Retain the operative requirements and their register references.
- Verify the legal summaries against their cited register material, particularly the erasure exemptions, HIPAA assertion, gag-reporting assertion and FERPA summary; qualify what the configuration expresses rather than promising legal compliance (pp. 13–16).

## Threats
- An implementer following the family pseudocode can bypass the very acceptance check presented as a universal consent protection; another following the partnership query cannot ratify the specified login ceremony (pp. 19, 24–25, 28–29).
- The confidentiality guarantee says “there is no non-member holder of community bytes,” while institutional policy supplies a read-and-portability grant “to a non-member data subject.” Likewise, “The only plaintext bodies at community scope” are infrastructure/public-room bodies, until affiliations introduce per-class plaintext promotion. A privacy reviewer can reasonably ask which guarantee governs affiliations, which explicitly share this tier (pp. 7, 12–14).
- Legal holds override consent-driven descent and erasure requests may be refused, but the multi-subject section says “any one signatory revokes → the contract Contribution is evicted” without identifying that exception. This leaves the retention/withdrawal boundary unclear precisely where legal evidence is involved (pp. 13, 29).
- “Honors the HIPAA minimum-necessary standard,” “a FISA/NSL gag complies,” and the declaration that a class “lawfully resists” erasure are stronger than configuration descriptions establish. Legal citations are present, but their application to these guarantees is unverifiable from here (pp. 13–15).
- Policy G promises “multi-source-consensus-backed” output even when its alternative condition is `license_validity`, without showing that every permitted path entails multi-source consensus (p. 34).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 19 | contradiction | Every consensus arm executes `return`, making the mandatory acceptance check and subsequent admission/cascade logic unreachable. | Store the consensus result, then evaluate acceptance and emit the final result once. |
| 2 | 24–25, 28–30 | contradiction | Partnership emissions are bare scores with partnership dimensions and `subject_key_ids`; ratification instead requires consent-record payloads with `stance`, `subject_key_id` and `target_key_id`. | Make the ratification query consume the pinned signed shape; remove the obsolete alternative representation. |
| 3 | 8–10, 19, 26 | stale | “A supersede NEVER adds” conflicts with Alice’s superseding membership addition; resolution examples also retain the older supersedes-only model. | Rewrite the joining example and both resolution functions using the already-stated roster/version and acceptance rules. |
| 4 | 7, 12, 18 | contradiction | “No retroactive key_grant cascade” conflicts with rewrapping held past epochs to every active member; sharing the current epoch key also leaves the meaning of “forward only” unclear. | Apply the declared `history_on_join` condition consistently and distinguish delivery restrictions from cryptographic access. |
| 5 | 29–30 | contradiction | The text says terminal `withdraws` is handled by the effective-consent read path, but `resolve_consent` reads only `consent:state:*` rows and never checks admitted withdrawals. | Include the existing admitted-withdrawal precedence in the function or explicitly require it as a preceding check. |
| 6 | 7, 12–14 | contradiction | Universal no-non-member-holder and limited-plaintext rules conflict with institutional data-subject access and per-class Commons promotion. | State the existing institutional exceptions in the tier rules and identify their precedence. |
| 7 | 24–25 | unclear rule | “Exactly this member set” and “Additional canonical members are a :v2 bump” conflict with other envelope fields being included whenever the producer explicitly sets them. | Specify whether the seven fields are the complete v1 set or required fields within an extensible set; align the omission rule accordingly. |
| 8 | 5, 31 | stale | Aggregation uses `attestation:l*` as an example even though that wire form is expressly rejected. | Replace it with an admitted mechanism dimension whose registered polarity matches the example. |

## Rendering
- **p. 34:** The Policy G composition expression stops at `attestation:regi`; the registry-consensus token and the rest of that line are missing from the supplied page text. Reflow the expression rather than leaving it on an overlong line.
- **pp. 19–20:** The heading “quorum:M/N is absolute-M (normative)” is stranded at the foot of p. 19, with its explanation beginning on p. 20.
- **pp. 24–25:** The signed-member table begins with only its header and first data row on p. 24 before continuing on p. 25; move its start to keep a useful group of rows together.
- **p. 13:** The legal-hold field contains the mixed dash sequence “court –- CC 3.2.”
- These observations are limited to the supplied page transcription; actual PDF margins, glyph integrity and visual clipping cannot be independently checked here.

## Effort estimate
Allow 20–30 hours for reconciliation, example correction, editorial cleanup and a rendered proof pass; the consent schema, history-access boundary, institutional exceptions and signed-member contract need steward rulings before the mechanical edits.

<!-- model openai/gpt-6-astra-pro; 35 pages; prompt_tokens 88123; completion_tokens 5130; 73s -->
