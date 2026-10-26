# The Dictionary (ciris_constitution-1.0-rc12-dictionary.pdf, 110 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The leaf tables can be repaired, but this volume contradicts itself on polarity, ownership, and which model is in force, so it cannot yet be the text a generated registry is built from.

## Strengths
- The opener states who is bound, what is omitted (3.2, the wire, verdict composition), and that the count lives in the manifest rather than in prose (p. 1).
- The case rule is specified as data: segment classes, refusal tokens, version-tail stripping, and match vectors (pp. 28–30).
- `goal:{scale}` is explicitly not `cohort_scope`, with seven tokens named and `federation` excluded from belonging (p. 40).
- Six senses of “witness” are listed, with a rule that none confers another (pp. 93–94).

## Weaknesses
- Polarity is not stable for the same family. `age_assurance:*` is “signed” (p. 7) and “enumerated” (p. 73). `content_class:{class}` and `cw_class:{class}` are “signed” (p. 35) and “enumerated” (p. 73). `consent:replication:{version}` is “signed” (p. 22) and “positive-only” / “never a negative score” (pp. 63–64). Admission is told to read polarity from the registry “and never from this prose” (p. 28), so these clashes are load-bearing.
- `boolean-via-score` is “the two points {-1, +1}” (p. 28), but `attestation:registry_consensus` allows “Indeterminate” (p. 5) and `judge_model:verdict:{model_id}` is “PASS/FAIL/UNDETERMINED” under that same class (p. 37).
- Registration is defined twice on one spread. A family is registered “iff” it has a CC 3.1 or CC 3.3 table row (p. 27); a CC 3.3-only family “is registered only once its CC 3.1 row exists” (p. 28). The generator “reaches only the CC 3.1 tables” (p. 27), while DMA verdicts (p. 25), conscience prefixes (p. 26), `ratchet:flag:*` (p. 26), and the coherence detectors (p. 31) are prose, not table rows.
- `system:*` is a Persist family (p. 9) and an Edge canonical leaf (p. 20), against the “disjoint union” (p. 2). One prefix, two owners, two `identity_type` values (pp. 80–81).
- Organisation records are withdrawn and kept. “nothing about an organisation is a record kind of its own” and “The three kinds below remain registered and in force. … and both stand” (p. 66).
- Adult incapacity is court-order-only at the predicate — `binding_legitimacy_source == court_order`, a prior will “never a source of its own” (pp. 97–98) — and then “rooted in prior-will, due process, or a bounded emergency necessity” (p. 102).
- Child protections “MUST NOT taper before 18” and “16–17 MAY act solo” (p. 103). The next sentences say jurisdiction “MAY only RAISE protection” and “A permissive deployment opts DOWN” (p. 103).
- `founder_only` is “not a community’s” protocol (p. 50) and is an emitter rule for family-or-community membership (p. 16).
- Deletion breach is two signals: the worked steps emit `` `hard_case:consent_sla_breach` `` (p. 44); D2 names `hard_case:deletion_window_breach` (p. 44). Only the latter is in the canonical kind list (p. 37).
- `detection:correlated_action:{axis}` uses one negative score for “weak / uncertain detection or evidence of the inverse pattern” (p. 32). A consumer cannot tell those apart.
- `objection:{state}` is “∈ proposal | assent | raised” and “the vocabulary stays open” in the same cell (p. 34).
- `consent:replication` is called “An open-vocabulary member” (p. 63) after the consent leaf set is closed (p. 41).
- House style breaks often: “F-3” as a heading (p. 31); “original P8 allegation types” (p. 34); “$1-Sybil-resistance per PoB” (p. 3); “not CONSTITUTIONAL” (p. 5); “Provisional” on `accord:human_dignity` (pp. 5, 79); “Lightnet settles; darknet transacts” (p. 70); a design essay on mutual credit (pp. 71–72); a “Status” argument against a read rule that is not the rule (pp. 84–86); “celebrity-conservatorship” and “defeated by construction” (pp. 95, 102). Code-shaped pointers: `MessageType::ContentFetch` (p. 34), `persist’s DeferralRequest` (p. 36), `EnvelopeKind::IdentityOccurrence` (p. 57), “the proto enum” (p. 66), `federation_attestations.attestation_id` (p. 109).
- Unsourced numbers stated as rules: `source_count < 10` (p. 13); “confidence ≤ 0.5” until the second co-steward emits (p. 93). “retirement horizons near 2030” (p. 47) is unverifiable from here, not treated as invented.
- Transitional wire: until “a substrate’s door carries this family”, a deferral “travels as a contribution: row”; “once the family ships, the contribution: prefix no longer carries it” (p. 36). Two conformant shapes, no cutover.
- “The CC 1.13+4 lockdown holds” (p. 72) is a garbled cross-reference. “bounded by the hold window below” (p. 17) does not point at a window on that page (259 200 s appears at p. 51). Family events are “reserved under CC 3.4.3” (p. 52); the emitter table for them is 3.4.4 (pp. 81–82).

## Opportunities
- One polarity column, generated from the CC 3.1 table only; delete the second polarity in every CC 3.3 repeat (pp. 7/73, 35/73, 22/63).
- Either drop `organization` / `org_membership` / `partner_record` or delete “nothing about an organisation is a record kind of its own” — not both (p. 66). Same cut for the p. 102 prior-will sentence versus the p. 97 predicate.
- Put DMA, conscience, ratchet, and coherence detectors into the same table shape as the other leaves, or they never enter `namespace_registry.json` (pp. 25–27, 31).
- Replace the p. 44 step-5 token with `hard_case:deletion_window_breach`, and expand the p. 37 kind list to the kinds 3.4.2 and 3.4.4 actually emit.
- Strike ticket labels (F-3, P8, PoB), “Provisional”, the darknet sentence, and the pp. 71–72 and 84–86 essays; leave the predicates.

## Threats
- A hostile implementer trusts the manifest over the prose, as p. 1 and p. 28 instruct, and ships `signed` consent replication and `signed` age assurance while another implementation follows pp. 63–64 and p. 73. Both can claim conformance.
- `identity:canonical_binding` is “a reserved scores dimension” (pp. 77–78) but 3.4 defines reserved as “only specific identity types may emit” (p. 78), and any claiming key K may emit it (p. 77). `prohibited:{category}` has a hard score floor and no emitter rule (p. 26). The attestation-ladder prefixes name a steward and do not reserve the emitter (pp. 5–6). Forged license-validity, prohibition, and canonical-hash claims are not clearly refused.
- `takedown_notice.content_sha256` is “the content” (p. 45) and, for `steward_purge`, a selection digest over `"plane:id"` strings (p. 46). A peer that hashes content will drop a purge; the text says those are the notices that must not be dropped (p. 48).
- Roster landing is timed from “the instant it first held the proposal”, so two nodes “holding the same rows” need not agree (p. 62). This volume also says an admission verdict must not depend on arrival order (p. 59, citing T8 vii).
- `live_stream` is a multimedia `sub_kind` (p. 74) and is absent from the media dimension families (pp. 72–73). `accord_data` (p. 74) sits beside reserved `accord:*` (p. 78). Apple and Google product names are normative age emitters (p. 103), which is a comparison this house style does not allow.
- Q1’s “opts DOWN” (p. 103) against Q2’s “MUST NEVER lower any element below the floor” (p. 104) is the sentence a regulator will quote.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 7, 22, 28, 35, 37, 63, 73 | contradiction | Same family, two polarity classes; boolean-via-score is two points but Indeterminate and UNDETERMINED are required | One class per family in the CC 3.1 table; point the other tables at it |
| 2 | 66 | contradiction | Affiliation model and `organization` / `org_membership` / `partner_record` “both stand” | Steward picks one; delete the other, including the M-of-N `partner_record` rule if licensure stays open-emitter (p. 93) |
| 3 | 97–98, 102 | contradiction | Court order is the only legitimacy source; the closer also roots the aperture in “prior-will” and emergency necessity | Delete the p. 102 triad; keep the predicate |
| 4 | 16, 50 | contradiction | `founder_only` is not a community protocol, and is a community membership emitter rule | One sentence: communities cannot select it, and the p. 16 parenthetical applies to families only — or the reverse, after a ruling |
| 5 | 103–104 | contradiction | Protections do not taper before 18, solo action starts at 16, and jurisdiction may only raise protection except a deployment “opts DOWN” | Strike “opts DOWN”; state whether 16 is a taper or the floor |
| 6 | 2, 9, 20, 25–27, 31 | contradiction | Disjoint union vs shared `system:*`; generator reads tables only, and several families have no table | One owner for `system:*`; table rows for every leaf the manifest must contain |
| 7 | 26, 44, 77–78 | unclear rule | `prohibited:*` has no emitter; “reserved” means two things for canonical binding; SLA breach has two kind strings | Emitter rule or “open” on `prohibited:*`; stop calling self-asserted binding reserved; one `hard_case` kind |
| 8 | 31, 34, 36, 70–72, 84–86 | editorializing | Ticket labels, a dual deferral wire “until the family ships”, and essay sections that are not rules | Delete labels and essays; one deferral dimension, no interim `contribution:` shape |

## Rendering
- Literal backslash in “dimension\'s” (p. 85).
- Markdown backticks left in prose, including `` `hard_case:consent_sla_breach` `` and `` `consent:deletion_complete` `` (pp. 43–44, 54).
- Household diagram broken (`-+`, stray `|`, backticks inside the figure) (pp. 52–53).
- Not-equal rendered as a combining slash plus equals (`̸=`) rather than ≠ (pp. 3, 21).
- No empty section and no clipped code block seen. Wide LegalBasis / wrap tables (pp. 45–47) extracted intact; overfull boxes not visible from the text.

## Effort estimate
Several days: polarity, stubs, cross-references, and markdown leaks are mechanical; the organisation dual model, the incapacity closer, the age floor, and who may emit reserved stems need the steward’s rulings before a registry build can be honest.

<!-- model x-ai/grok-4.7; 110 pages; prompt_tokens 94980; completion_tokens 28813; 319s -->
