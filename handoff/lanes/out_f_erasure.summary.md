# Lane F: projection, erasure_route, evidence_screen, evidence

180 statements (projection 70, erasure_route 15, evidence_screen 92, evidence 3), 379 rows (one per statement and family). Every statement was found in today's text: none is GONE. Thirteen had no entry phrase and were found by their gist. Every quote was checked verbatim against its section.

## Counts per verdict

| column | AGREE | FILLS | DISAGREE | RICHER | NOT_A_CELL | GONE | rows |
|---|---|---|---|---|---|---|---|
| projection | 0 | 4 | 0 | 99 | 15 | 0 | 118 |
| erasure_route | 0 | 17 | 1 | 18 | 1 | 0 | 37 |
| evidence_screen | 1 | 38 | 2 | 136 | 35 | 0 | 212 |
| evidence | 0 | 6 | 0 | 6 | 0 | 0 | 12 |
| all | 1 | 65 | 3 | 259 | 51 | 0 | 379 |

How the verdicts were applied. Almost every cell of these columns is read from code or is gap, so a match is `FILLS` (the prose could become the cell's source), never `AGREE`. `DISAGREE` is kept for a cell that departs from the default and says something else than the prose. The `evidence` cell is shown without its three generic tokens. Where another existing column is the one that can hold a statement and its cell was read (`body`, `confers`), the row shows that cell and its note begins `[cell shown: …]`.

## RICHER needs, grouped

Statements counts distinct statements; a statement may carry two needs.

| need | what is asked for | statements | rows | sections |
|---|---|---|---|---|
| `admission_precondition` | new column `requires` (or a typed `reference`) | 33 | 52 | 2.1, 2.6.6.2, 3.1.1, 3.1.2, 3.1.3, 3.1.3.2, 3.1.4, 3.1.5, 3.1.5.5, 3.1.9.4, 3.2, 3.3.6.1, 3.4.12, 3.4.2, 3.4.5, 4.2.6, 4.3, 4.4.3.10, 4.4.3.2.3, 4.4.3.2.8, 4.5.5, 5.3.3.6 |
| `fold_rule` | new column `fold` beside `projection` | 30 | 36 | 2.4.1.1, 2.4.1.2.1, 3.1.1, 3.1.2, 3.1.3, 3.1.3.1, 3.1.5.5, 3.1.9.2, 3.1.9.3, 3.2, 3.3.1, 3.3.7, 3.3.8, 4.4.3.2.4, 4.4.3.2.4.1, 4.4.3.2.6, 4.4.3.2.8, 4.4.3.4, 4.4.3.4.4, 4.4.3.4.6, 4.4.3.5, 4.4.3.5.5, 6.1.9 |
| `no_family_row` | a row, or a second table | 16 | 16 | 2.6.6.2, 3.2, 3.3.3, 3.4.2, 4.4.3.10, 4.4.3.2.3, 4.4.3.2.8, 4.4.3.5.4, 6.1.5.2 |
| `reaction` | new table of reactions (or transitions with a substrate actor) | 15 | 33 | 3.1.1, 3.1.5.2, 3.1.9.4, 3.3.1, 3.4.11, 3.4.12, 4.4.3.2.3, 4.4.3.4.1, 4.4.3.4.2, 4.4.3.5.1, 4.5.2.2 |
| `sole_evidence_bar` | new token on the consuming family: `grounds` | 10 | 32 | 3.1.6, 3.1.9.2, 3.1.9.3, 3.1.9.4, 3.3.1, 3.4.11, 3.4.12, 3.4.7.2, 4.4.1 |
| `backing` | new column `vouches` | 9 | 16 | 1.13.3.3, 3.1.3.3, 3.1.5, 3.3.3, 3.4.6, 4.2.2.1, 6.1.5, 6.1.5.2 |
| `consumer_composition` | token `composed_by: reader` (on the fold column) | 7 | 18 | 2.3.2.4, 3.1.7, 3.1.9.4, 3.3.5, 3.4.11, 4.1.3, 4.4.3.2.8 |
| `absence_default` | token `absent → value` (on the fold column) | 6 | 6 | 3.1.2, 3.1.3.1, 3.1.3.2, 3.4.5, 4.4.3.5.5 |
| `fold_weight` | token `read_by: none | advisory` (on the fold column) | 4 | 19 | 3.1.3, 3.1.3.3, 3.1.6, 3.1.8 |
| `per_value` | cells keyed by dimension value | 4 | 4 | 3.1.1, 3.1.9.2, 3.4.12, 6.1.2.2 |
| `reader_weight` | token: reader-side verdict tokens beside door tokens | 4 | 7 | 3.1.2.1, 3.1.4, 4.4.3.2.8, 4.4.3.7 |
| `erasure_gate` | token on erasure_route: `refused_with_reason(gate)` | 3 | 3 | 4.4.3.2.8, 4.4.3.5.4 |
| `erasure_residue` | token on erasure_route: `leaves` | 3 | 3 | 3.2, 3.3.3, 6.1.2.2 |
| `threshold` | policy rows | 3 | 9 | 3.1.2, 3.1.9.3, 4.2.6 |
| `derived_check` | fill the `derived` column | 2 | 4 | 3.1.9.3, 6.1.9 |
| `erasure_executor` | token on erasure_route: `executed_by` | 2 | 2 | 7.5.5 |
| `presentation` | no cell; a reader-display table | 2 | 2 | 3.1.3.3, 6.1.9 |
| `erasure_terminus` | token on erasure_route: `terminus ∈ retained_floor | zero` | 1 | 1 | 6.1.2.2 |
| `evidence_refs_target` | token: what evidence_refs must point at | 1 | 5 | 4.5.1.1 |
| `placement_screen` | a rule keyed on placement | 1 | 1 | 3.2 |
| `purge_basis` | parameter on `purge` | 1 | 1 | 7.5.5 |
| `segment_type` | token on binds_segment: `row_id(family)` | 1 | 2 | 3.1.9.7 |

**`admission_precondition`** (33 statements). A row is admitted only if a named row of another family is held, live, in a given state, or cited: `requires: [{family, state, relation ∈ cites | live_for_subject | companion | contained_in, at ∈ asserted_at | receipt}]`. Today `reference` holds `pre:<kind>`, a kind and never a family or a state, and `evidence` holds only the token a failure returns. Examples: identity_amendment cites deferral:response:approved; key_grant on a sealed archive cites archive_release; a geographic widening needs a contained, unexpired location_proof; an incapacitated rung needs its reversible_excluded companion; a deferral response needs a live licence where the seat requires one; a delivery receipt joins a published tree head.

**`fold_rule`** (30 statements). `projection` names the output table and whether it rebuilds. The prose states the function: which rows are read (filter: emitter resolves to the authority, signer is the subject or its proxy, seat not node-bearing), the key (raw-key digest, attested_key_id, (community, session)), the pick (latest non-superseded, union by identity, set not scalar), the order (key_id lowercase hex), the input head (held or witnessed), and which other fold reads the family. `fold: {reads, key, pick, order, result}` would turn the consent, roster, licensure and session resolvers into data.

**`no_family_row`** (16 statements). The statement is about something that has no row among the 184: `location_proof` (8 statements), affiliation charter members (`erasure_policy`, `legal_hold`, `member_attributes`, `disclosure_accounting`), `external_content`, `StorageBudgetV1`, a public room as a placement. No cell of any column can hold these. location_proof is the clear case for a row; the charter members want a table of their own.

**`reaction`** (15 statements). An admitted row, a refusal, a match or a missed deadline makes the substrate emit a row of another family: duty breach → hard_case:duty_unmet; SLA breach → hard_case:sla_breach_unattested; watchlist match → takedown_notice or detection, plus hard_case:watchlist_match; membership change → hard_case:family_membership_change and the key_grant cascade; consent revoked → deletion_complete within consent:deletion_sla days or hard_case:deletion_window_breach; consent:decay stages on a clock. `on: {family, event ∈ admitted | refused | deadline(days)} → emits: family:leaf`. Several are timed, which no column can say.

**`sole_evidence_bar`** (10 statements). Rows of family F never suffice alone to ground a row of family G: ratchet:flag, detection, testimonial_witness and seed_holder_voting_alignment against slashing; consent:deletion_complete against proof of deletion. 3.1.6 reads the bars as one screen over the union of families in a slashing row's evidence_refs, and 3.1.9.2 gives slashing a closed list of grounds. `slashing.grounds: {requires_antecedent: moderation, insufficient_alone: [ratchet, detection, testimonial_witness]}`.

**`backing`** (9 statements). What an admitted row proves and what stays unproven: parseable only (trace), origin and tree-head join but no verdict (delivery_receipt), signed but possession unproven (custody, weights 2/1/0), self-asserted until a chain verifies (hardware class), self-assertion until cross-attested (occurrence), location truth never verified. `vouches ∈ {shape, signature, origin, possession, chain}` with the weight a reader may give.

**`consumer_composition`** (7 statements). The verdict is computed by the reader at read time and the substrate never enforces it: the L1 to L5 attestation ladder, bilateral ratification, liveness from several vantages, a sensitive space checking the level apart from the band.

**`absence_default`** (6 statements). What a reader resolves when no row exists: registry_consensus absent → RESTRICTED; consent never declared → unspecified; no session claim → nobody acts; no publish right named → every member writes; no capacity verdict → the gate fails closed.

**`fold_weight`** (4 statements). The row is read by no fold, or feeds human judgment and is never a verdict: ratchet flags, LensCore measures, the closed self:delegates_to label, holding claims excluded from the bytes-plane liveness fold.

**`per_value`** (4 statements). A property varies by the value of a dimension inside one family: licensure status suspended (reversible) against revoked (terminal); objection {state} vote weights; what a provider {level} supports; the erasure terminus per takedown {basis}. A cell has one value per family.

**`reader_weight`** (4 statements). The door admits the row and a reader counts it only under a condition: emitter holds infra:attest (provenance), the relay countersigned (relay_delivery), the licence class is declared (licence_class_not_trusted), score at or above the root's threshold from a roster key (agent_files). `evidence` holds door refusal tokens only; reader verdict tokens have no place.

**`erasure_gate`** (3 statements). The route is refused with reason while the row is held under an affiliation class flagged erasure_exempt or under a legal_hold. The gate is keyed on the holding class or the hold scope, never on the family. The default cell reads "legal_hold: none in code".

**`erasure_residue`** (3 statements). What remains after the route runs: a tombstone in the audit chain and never the cell (location_proof); the content hash for the legal retention window (prohibited content).

**`threshold`** (3 statements). A count with no row in governance_policy.tsv: k = 10 census floor, witness_diversity N = 3, registry_consensus 2 of 3, accord roster change floor(N/2)+1, n_eff_floor.

**`derived_check`** (2 statements). The row must equal a recomputation over named sibling rows (census composite = sum of partials, expected_active recount, weighted_aggregate tally). The `derived` column exists for this and is gap in all 184 families, with no projection ids defined.

**`erasure_executor`** (2 statements). Who executes: the subject, the producer, or after `retired` the custodian on the producer's side (7.5.5).

**`presentation`** (2 statements). What a UI must or must not show (custody states: unknown never shown as none; census display rounding).

**`erasure_terminus`** (1 statements). CC 6.1.2: ordinary retirement ends at the retained floor (the gist survives); an immediate-removal basis ends at zero at every tier. The cell names a route and not how far it descends.

**`evidence_refs_target`** (1 statements). A RATCHET detector's evidence_refs must pin its calibration package version.

**`placement_screen`** (1 statements). The perceptual-hash screen runs on any post into a public room: keyed on where the row is placed.

**`purge_basis`** (1 statements). The cell's purge is "steward purge on a cosigned notice". 4.5.3 and 7.5.5 run a duty-holder's takedown and a court order as the same tombstone row; purge needs its authorising basis.

**`segment_type`** (1 statements). {goal_id} is another row's attestation_id; binds_segment maps a placeholder to signer, subject, group or none.

## What the three columns can and cannot hold

- **projection** (70 statements): 4 rows fill a cell (`identity:occurrence_revocation`, `goal:{scale}`, `cosign:{state}`, and `consent:scope:{kind}` against `confers`). The inventory filed under this column every statement about how rows are read. `{table, rebuild}` holds none of that: the column describes where the store keeps a view, and the prose describes the fold.
- **erasure_route** (15): the accountability record and the detection route fill their cells. Everything from CC 6.1.2 (one descent, a floor, a terminus at zero for prohibited content, what survives) is outside the vocabulary `dsar | purge | legal_hold | none`, and so are the gates of CC 4.4.3.2.8.
- **evidence_screen** (92) and **evidence** (3): the `evidence` cell is `{claim ids, refusal tokens}`. It takes a statement only when the prose names a token (8 statements name one the cell lacks, 2 more name one the cell spells otherwise) or when a claim id already stands for the rule (the capacity consent gate, 5 statements). What a row must carry goes to `body` (gap for capacity, census, ledger). What must already be held goes nowhere (`admission_precondition`). What a reader may conclude goes nowhere (`sole_evidence_bar`, `backing`, `reader_weight`).

## Refusal tokens the prose names and no evidence cell carries

`census_composite_below_k` (census:composite, ballot:tally), `census_expected_active_mismatch` (census:expected_active), `evidence_reference_unresolved` (evidence), `deferral_response_unseated`, `deferral_response_unlicensed` (deferral:response), `trace_run_kind_mock` (trace; the cell reads `run_kind`), `identity_amendment_unauthorized` (identity_amendment; the cell has five other tokens). Seen in passing: the takedown_notice cell lists a token `reason`, which looks clipped in the same way as `run_kind`.

## DISAGREE rows in full

- **evidence_screen · CC 3.1.5 · `identity_amendment`**
  - cell (code-v61): `{"door_claims": ["CLM-identity-amendment-row"], "door_tokens": ["attester_not_the_agents_occurrence", "envelope_member_invalid", "evidence_does_not_cite_response", "response_not_approved", "response_not_held", "response_signer_not_a_seated_wa"]} + generic_tokens`
  - prose: "otherwise it is refused `identity_amendment_unauthorized`"
  - proposed: `door_tokens: [identity_amendment_unauthorized]`
  - cell (code-v61) lists attester_not_the_agents_occurrence, evidence_does_not_cite_response, response_not_approved, response_not_held, response_signer_not_a_seated_wa and envelope_member_invalid; the text names one token for all of them. The text is the only place the single token appears

- **evidence_screen · CC 3.1.5 · `trace:{form}:{version}`**
  - cell (code-v61): `{"door_claims": ["CLM-trace-family"], "door_tokens": ["run_kind"]} + generic_tokens`
  - prose: "A `mock` trace is refused at federation-tier admission outright (`trace_run_kind_mock`)"
  - proposed: `door_tokens: [trace_run_kind_mock]`
  - cell door_tokens reads ["run_kind"], which looks like a clipped token; the body cell of the same family spells trace_run_kind_mock

- **erasure_route · CC 4.5.3 · `revocation:{entity_type}:{reason}`**
  - cell (code-v61): `"none (accountability record, unpurgeable: migration.rs:606)"`
  - prose: "the request is executed by the row's **producer** under rule 1, the data controller withdrawing its own row, or refused with reason under Article 17(3)"
  - proposed: `dsar (producer withdraws + tombstone), no purge`
  - cell says no route at all; 4.5.3 gives every kept-list row a producer-executed route. 2.4.1.1 supports the prose ("the substrate that produced the proof withdraws it under rule 1"), and supports the cell only on purge. The same holds for moderation, slashing and hard_case, which this statement's family list omits

One wider disagreement sits behind the first of these and is recorded as FILLS rows because the cells involved are the default. CC 4.5.3 defines an adverse row as "any row on the kept list of CC 2.4.1.1" and gives it one route: the producer withdraws under rule 1, or refuses with reason. The kept list names `capacity:*`, `detection:*`, `licensure:*`, `revocation:*`, `moderation:*`, `hard_case:*`, `slashing:*`, legal-weight acts and `takedown_notice:*`. The data gives that route to the five `detection` families only (reason `signer_erases_adverse`). `capacity` (3 families), `licensure` and `takedown_notice` sit on the default (purge only); `revocation`, `moderation`, `slashing` and `hard_case` read `none`. Also outside the inventoried statements: the first sentence of the 4.5.3 erasure paragraph gives every ordinary row about a subject a route by the subject's own `withdraws`, and the default cell names no `dsar` route at all.

## Sections where every statement of these columns was AGREE or FILLS

Each has one statement in these columns; a section becomes a pointer only if its statements in the other lanes' columns clear too.

| column | section | statements | what fills |
|---|---|---|---|
| erasure_route | CC 2.4.1.1 | 1 | the accountability record is never purgeable: six cells `none` |
| evidence | CC 1.13.3.3 | 1 | ratchet:flag carries no evidence row: six cells with no claim ids |
| evidence_screen | CC 2.6.1.7 | 1 | door token census_composite_below_k on census:composite and ballot:tally |
| evidence_screen | CC 3.1.8.1 | 1 | claim CLM-capacity-consent-gate on the three capacity families |
| evidence_screen | CC 3.3.10.1 | 1 | body of ledger:promotion: the compliance proof |
| evidence_screen | CC 3.3.14 | 1 | confers of identity:canonical_binding: nothing |

Statements that fill a cell inside a mixed section (the sentence could point to the table though the section cannot): CC 2.1 (consent_basis, n_eff_pr, n_eff_floor into `body`; authorized_by agrees with `body`), CC 3.1.3 (census_expected_active_mismatch; cosign projection; ledger promotion body; occurrence_revocation projection), CC 3.1.4, 3.3.1, 3.3.7, 3.4.5 (the capacity consent gate, five restatements of one claim), CC 3.1.5.5 (evidence_reference_unresolved), CC 3.1.9.3 and 4.3 (the two deferral tokens), CC 3.1.9.7 (goals table), CC 4.5.3 (detection erasure route), CC 6.1.9 (k floor, expected_active, multiplicity).
