# The Reader’s Policies (ciris_constitution-1.0-rc12-policies.pdf, 35 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The policy library is usable as a map, but the opening promise, the JCS member set, and the community catch-up rule contradict the body, and design notes still sit in the rules.

## Strengths
- Polarity defaults are a single table with an explicit override rule (p. 5), and Policy A repeats that split rather than inventing a second aggregator (p. 32).
- Cycle rejection is distinguished from a self-edge and from a `trust:accepts:v1` edge, with both arrival orders stated (p. 2).
- Policies A–M are all present, and the conformance floor is named as Policy A twice (pp. 4, 5).
- Member removal has a declared home: “This is the one statement of the removal rule” (p. 26), with 4.4.3.2.2 pointing at it (p. 8).

## Weaknesses
- The cover promise does not match the scope table. p. 1: “a grant confers no re-grant and a licence no issuance, and that only a grant-scoped delegation from the owner confers issuance.” p. 22: a `license` scope “conveys the right to issue,” and a `grant` may be issued by a delegator who “holds a grant-scoped delegation,” not only by the owner.
- The JCS contract cannot be implemented as written. p. 25: “these seven members are REQUIRED,” then eight rows. The signed example and the required-member table use `subject_key_id` (pp. 24–25); the mapping says `partner ≡ subject_key_ids[0]` (p. 25).
- Community history contradicts itself. p. 11: `history_on_join: full` “new member receives key_grants for prior epochs.” p. 18: “At community and affiliations there is no walk for a new member … and no earlier epoch’s.”
- Consent resolution contradicts its own comment and the eviction rule. p. 30 comment: “a withdrawn grant resolves to none”; the next branch `return unspecified`. p. 29: an admitted `withdraws` from any subject “evicts the Contribution.”
- Agency is both forbidden and permitted to the agent. p. 21: the accept half is “never withheld — an agent has no veto”; same page: “Either half may be withdrawn by its signer’s withdraws,” and the accept signer is “the agent occurrence’s signature.”
- Part 4.1 is a rejected-design catalog, not a rule: “Cartesian-individualist defaults” (p. 2), “The Ubuntu-primary discipline cuts cleanly” (p. 3), “Cartesian shortcut” (p. 4). Normative force in the Frickerian bullets is “Don’t,” not an RFC 2119 keyword (pp. 4–5).
- Code and product names are used as specification: “CIRISNodeCore” (p. 17), “CIRISAgent” (pp. 20, 28, 30), “LensCore” (p. 28), “Verify” (pp. 24, 31), “Portal” (p. 4), “CIRISServer” / “KMP” (pp. 23, 20), and the host `registry.ciris-services-1.ai/install` (p. 31).
- Leftover design talk: “the member is reserved and decides nothing today” (p. 11); “the operator the seed lacked” (p. 13); “M-1’s symmetry is structural, not bolted on” (p. 35); “The four implementations MUST follow this shape” with the four unnamed (p. 20).
- `score ≥ 0.7` (p. 31) has no cite. `SI ≥ 0.6` (p. 16) is only “CC 8.8.9,” not visible here — unverifiable from here.
- Policy letters are not in section order: 4.4.3.1 is Policy E (p. 5); the MUST policy, Policy A, starts at p. 32. “Policies A to M” (p. 1) is not how the volume is walked.
- `designated_officials` are “OPTIONAL” and “Default: none,” then “Mandatory at federal/regulated scale, waivable below threshold” with no threshold (p. 15).

## Opportunities
- Rewrite the p. 1 promise so it matches whatever ruling is kept on p. 22 (owner-only issuance, or license-scoped and grant-scoped delegation). One sentence; no new scope.
- On pp. 24–25, delete “seven,” pick `subject_key_id` or `subject_key_ids[]`, and make the JSON, the table, and the mapping the same member set.
- Strike the p. 11 aside, the p. 13 “seed” clause, the p. 35 “M-1” sentence, and the “Why this matters” / “rather than rhetorical” / “tombstoning pen” asides (pp. 31, 32–33). Point 4.4.3.4.3.1’s scope comment at 4.4.3.4.3, not at itself (p. 25).
- Add a half-page ordered list of A–M with section numbers at the start of 4.4 so the MUST policy is findable without reordering the sections.
- One paragraph that states which of p. 11 `full` and p. 18 “no earlier epoch’s” wins, and which of `unspecified` / `none` / evict a withdrawn consent row returns (pp. 29–30).

## Threats
- An implementer who signs the p. 24 set and a verifier who signs `subject_key_ids[0]` will disagree on every partnership byte. That is an interop failure in a section marked normative (pp. 24–25).
- A lawyer will not accept “so a FISA/NSL gag complies via USA-FREEDOM-style aggregate banding” (p. 15) as a compliance claim. The GDPR gloss “Art 17(3)(b)/(c)/(d) legal-obligation / public-interest-archiving” (p. 13) collapses public health (c) into archiving (d).
- “a persecuted community is protected by being a community, not by remembering a flag” (p. 7) and “replaces DNS+IP” (p. 9) are claims a hostile reviewer can quote as marketing. “Ubuntu-primary” (p. 3) reads as a comparison with another tradition, and to a careless reader as another project.
- p. 6 states the federation pool makes `cell_pool ≥ min_pool(federation)` “always true at federation genesis,” then describes the crisis if it is not. “Always” is stronger than the text’s evidence.
- The worked Austin admission asserts H3 containment of `872830828ffffff` in `85283473fffffff` (p. 10). Unverifiable from here; a failed parent-walk falsifies the only geographic example.
- Un-trust “revokes, at once,” score validity (p. 33) sits next to “withdraws-isn’t-retroactive” (p. 27). A reader can treat past scores as both still valid and already void.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 1, 22 | contradiction | Cover: grant “confers no re-grant,” licence confers “no issuance,” “only a grant-scoped delegation from the owner confers issuance.” Body: `license` “conveys the right to issue”; `grant` may be issued by a holder of “a grant-scoped delegation.” | Steward picks one rule; replace the p. 1 sentence so it quotes that rule. |
| 2 | 24–25 | contradiction | “seven members” vs eight listed; `subject_key_id` in the example and table vs `subject_key_ids[0]` in the mapping. | One identifier, one count, one canonical member list. |
| 3 | 11, 18 | contradiction | `history_on_join: full` grants prior epoch keys; 4.4.3.4.1 says a new community member gets “no earlier epoch’s.” | Delete one sentence after a ruling; leave a cross-reference, not a second procedure. |
| 4 | 29–30 | contradiction | Comment “resolves to none”; code returns `unspecified` when every row is withdrawn; 4.4.3.5.4 says that `withdraws` evicts. | State one return value and whether eviction is that value or a separate admission fact. |
| 5 | 21 | contradiction | Accept “never withheld” and “an agent has no veto,” but “either half may be withdrawn by its signer,” and the accept signer is the agent occurrence. | Say who may `withdraws` the accept half, in one sentence. |
| 6 | 11, 13, 35 | stale | “decides nothing today”; “the operator the seed lacked”; “M-1’s symmetry.” | Delete the three clauses. |
| 7 | 31 | overclaim | Default-trust if `score ≥ 0.7`, no register row or cite in this volume. | Cite the row or drop the number. |
| 8 | 34 | rendering | Policy G prints `(attestation:regi` and the next line is `OR attestation:license_validity` — `stry_consensus` is missing. | Restore `attestation:registry_consensus`. |

## Rendering
- p. 34: identifier clipped; `attestation:registry_consensus` lost at the line break (see defect 8).
- p. 10: not-equal rendered as a combining slash, “Bootstrap reachability ̸= bootstrap trust,” not a ≠ glyph.
- p. 5: `testimonial_` / `witness:victim_of_my_competitor` broken across lines.
- p. 2: table cells hyphenate mid-word (“concentra-tion”) and split “Unbounded depth” from “delegates_to chains”; “attestation:” / “self_verify” can be copied with a space.
- p. 3: “WA quo-rum”; cross-reference broken as “CC 4.4.” / “3.6 Policy I.”
- pp. 8–10, 19, 26: code lines wrap inside calls (`community_key_id == C` then `).where`), so the blocks are not copyable.
- p. 7: “custody:ack:v1, here | none” — pipe fragment, unclear whether a table cell was flattened.
- p. 22: unmatched parenthesis, “is stated there).”

## Effort estimate
About one to two days: cutting asides, restoring the clipped identifier, and aligning the JCS count are mechanical; re-grant, `history_on_join`, the consent return value, and who may withdraw the accept half need the steward’s rulings before the sentences can be made to match.

<!-- model x-ai/grok-4.7; 35 pages; prompt_tokens 29470; completion_tokens 17903; 211s -->
