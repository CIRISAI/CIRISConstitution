# Lane F, small columns: freshness, window, formula, tie_break, monotone_field, projection, placement

243 statements of `rule_inventory.tsv` (scope `family`), 304 rows (one per statement and family). Every statement was found in the text today: none is GONE. Every quote was checked verbatim against its section by script.

How the columns were read. `freshness`, `projection` and `placement` are cells of `manifests/family_model.json`; where a statement filed under one of them is in fact a fold, a clock or a change bound, it was compared with `fold_text.tsv`, `reaction_text.tsv` or `change_text.tsv`, and `cell_value` names that table (prefix `fold:`, `reactions:`, `change:`, `constants:`, `policy:`). Most of the 70 `projection` statements are of this kind: they say how a reader composes rows, which is the `fold` cell, not the store's projection table. `(no row)` marks a subject kind or transport frame with no row among the 184 families.

## Counts per verdict

| column | AGREE | FILLS | RICHER | DISAGREE | NOT_A_CELL | GONE | rows |
|---|---|---|---|---|---|---|---|
| freshness | 5 | 5 | 12 | 1 | 7 | 0 | 30 |
| projection | 75 | 7 | 1 | 0 | 20 | 0 | 103 |
| placement | 24 | 1 | 10 | 0 | 10 | 0 | 45 |
| window | 22 | 5 | 9 | 1 | 5 | 0 | 42 |
| formula | 36 | 6 | 11 | 0 | 2 | 0 | 55 |
| tie_break | 15 | 0 | 0 | 0 | 2 | 0 | 17 |
| monotone_field | 9 | 0 | 0 | 0 | 3 | 0 | 12 |
| all | 186 | 24 | 43 | 2 | 49 | 0 | 304 |

## RICHER needs, grouped

Each is a candidate token, selector or table. The count is of statements.

| need | statements | columns | sections | what is missing |
|---|---|---|---|---|
| `need:rate_table` | 5 | formula | 4.2.2 | `weight=rate(hardware_class)` names a lookup whose table (six classes, their multipliers, 0.0 for an unlisted class) exists only as prose. |
| `need:bound_is_ref_expiry` | 3 | freshness | 2.1, 3.1.3.2 | A signed instant bounded by another row's signed member (the proposal's `expires_at`) instead of by W. reactions.json already carries it (`expiry ... by signed`): the freshness cell could be a view of the reaction table. |
| `need:cadence` | 3 | projection, window | 2.1, 3.3.10.1, 4.3 | A recurring duty or clock: something done every N seconds (a witness re-cosigns the head, ledger heads are anchored, rulings are published). The reaction grammar has a clock that runs once from an event. Also met, without a RICHER verdict, in the daily custody re-acknowledgement (CC 3.1.3.3), the accord heartbeat refresh (CC 3.4.1) and the constant-tick publications of Part 6. |
| `need:placement_by_selector` | 3 | placement | 3.1.3.2, 3.4.5.1 | A placement that depends on the leaf or on the signer's seat (`config` leaves `admission`/`transport` at self; an owner-binding at self, at commons for a `serve` seat). The column holds one value per family. |
| `need:seat_liveness_clock` | 3 | freshness | 3.1.9.3, 4.3, 4.5.13 | A clock on a seat-holder's silence, its length a member of the body's own record (`the quorum's stated freshness window`, `the community's freshness window`; the text names no member), whose close takes the holder out of the `present` set, lapses a duty or re-routes an ask. |
| `need:most_restrictive` | 2 | formula | 3.1.9.2, 4.2.1 | An aggregate across several roots that takes the most restrictive value under each key's own ordering; `combine=min` covers numeric keys only. |
| `need:once_within_window` | 2 | freshness | 4.2.1.1, 4.2.1.3 | `pick=once` bounded by the row's own `valid_until`, on a key of (kind, invocation_id), with no refusal token named in the text. |
| `need:period_definition` | 2 | window | 3.1.9.6, 6.1.9 | The length of a family's `{period}` segment (activity tier: 30 days; census: the constant tick). No table defines a period. |
| `need:placement_declared_by_record` | 2 | placement | 2.4.1.2.1, 4.4.3.2.8 | A placement chosen by a member of a group's record, per class of row (`licence class` in the charter; `disclosure_posture`), `never the writer`. |
| `need:quorum_by_scale` | 2 | formula | 4.4.3.1 | A count that is a function of a leaf segment (`quorum_size(scale)`, `min_pool = 2 x quorum_size`); the policy table has one row per act. |
| `need:W_unless_signer_standing` | 1 | freshness | 3.3.4 | W applies only to a signer who no longer stands at receipt. Four freshness cells write this as free text inside `W`; reactions.json says it as `unless fold(signer_seated)`. |
| `need:banded_liveness` | 1 | freshness | 3.4.1 | The age of the newest row read as three bands (green, yellow, red); the cell has one W and a fold `test=` yields two states. |
| `need:cascade_by_author` | 1 | placement | 3.1.3.4 | A cascade that depends on the author of the row under the changed one (the promoter's own files widen; another author's receive a request). |
| `need:deletion_window_default` | 1 | window | 2.1 | A per-family default deletion window (`Absent means the family's default`) for the envelope member `deletion_window`; no table holds it. |
| `need:derived_record_family` | 1 | projection | 4.3 | A named composite (the WA conduct record) with no family row for its fold to sit on. |
| `need:effect_destroy_keys` | 1 | window | 3.2 | An effect word for destroying key material at the close of a retention window (`rotate-forward`). |
| `need:first_admission_only` | 1 | freshness | 2.1 | A check made at first admission and never repeated on restore. |
| `need:fold_reads_other_roster` | 1 | freshness | 3.2 | A roster fold whose eligibility reads another roster's fold (an accord holder as founder). |
| `need:no_consecutive_renewal` | 1 | window | 4.2.1 | A bound on the next row by the same signer: an emergency relief is not renewable back-to-back by the same holder. |
| `need:placement_default` | 1 | placement | 3.3.10 | A default among the scopes a signer may choose (the narrowest cohort holding both parties), with commons as an opt-in. |
| `need:placement_default_from` | 1 | placement | 3.1.3.4 | A placement that defaults to the scope of the row the new row is placed under, read at that instant (a file in a directory), with a narrower pin allowed. |
| `need:reach_plane` | 1 | placement | 4.5.3 | Which plane a tombstone under a notice may touch, by leaf (bytes plane only; any plane for `steward_purge`). `reach=` has no plane value. |
| `need:recommended_bound` | 1 | window | 4.5.2.2 | A SHOULD-force maximum on a leaf segment value (`consent:deletion_sla:{days}` at most 28). |
| `need:runoff_rule` | 1 | formula | 4.5.13 | The instant-runoff count: elimination order and its tie-break. The policy row names it in words only. |
| `need:score_formula` | 1 | formula | 3.1.5.5 | The value a signer must write in the row's own `score`, as a function of its body and leaf (1.0; 2 x pass ratio - 1). A body or guard matter. |
| `need:selector_off_wire` | 1 | window | 4.4.3.5.6 | A default that holds for a category not on the wire (the agent-side TEMPORARY consent stream). |

Read together, the needs fall into four groups: (1) **placement wants a selector, a default and a deciding record** (five tags, 10 statements); (2) **time wants a recurring clock and a clock on silence** (`cadence`, `seat_liveness_clock`, `period_definition`, `banded_liveness`); (3) **the freshness cell is a weaker copy of the reaction table** (`bound_is_ref_expiry`, `W_unless_signer_standing`, `first_admission_only`: in each the reaction entry already says more than the cell can); (4) **numbers that are tables** (`rate_table`, `quorum_by_scale`).

## need:constant

Numbers the text gives that have no name in `constitution/constants.tsv`.

| section | family | verdict | number and proposed name |
|---|---|---|---|
| 3.3.3 | location_proof | NOT_A_CELL | 30 days (proposed location_proof_stale_secs) |
| 3.4.1 | accord:lifecycle | RICHER | 90 days and 180 days (proposed liveness_band_green_secs, liveness_band_yellow_secs) |
| 5.3.2.3 | organization | NOT_A_CELL | 5 minutes (proposed clock_skew_tolerance_secs, 300 s) |
| 3.1.3.3 | custody:{kind} | AGREE | the daily re-acknowledgement has no name (proposed custody_reack_cadence_secs, 86,400 s) and no entry: a recurring duty, see need:cadence |
| 3.1.9.6 | activity_tier:{period} | RICHER | 30 days (proposed activity_tier_window_secs) |
| 3.2 | key_grant:{axis} | RICHER | 30 days (proposed archive_rotate_forward_window_secs) |
| 3.4.1 | accord:lifecycle | FILLS | 90 days (proposed accord_heartbeat_max_secs, 7,776,000 s) |
| 4.2.6 | trust:{job}:{version} | AGREE | 7 days (604,800 s) sits inside the description of admission_freshness_window_secs and has no name of its own (proposed accord_roster_window_max_secs) |
| 4.4.3.5.1 | consent:decay:{stage} | AGREE | 30 days and 90 days of the canonical protocol have no names (proposed consent_decay_anonymise_secs, consent_decay_complete_secs) |
| 4.4.3.5.6 | consent:state:{stance} | RICHER | 14 days (proposed consent_temporary_default_secs) |
| 4.5.2.2 | consent:deletion_sla:{days} | RICHER | 28 days (proposed deletion_sla_recommended_max_days) |
| 3.1.3 | census:expected_active | AGREE | 4 periods: the fold carries the literal (`last(4)`, text `window_periods = 4`; proposed census_active_window_periods) |
| 4.4.3.1 | locality:decision:{scale} | RICHER | 2, 3, 4 and 6 (proposed wa_quorum_local, wa_quorum_regional, wa_quorum_national, wa_quorum_federation) and the factor 2 of min_pool |

## DISAGREE rows in full

### freshness, CC 4.2.1.1, accord:invoke:constitutional:{halt_id}

- **column**: freshness
- **section**: 4.2.1.1
- **family**: accord:invoke:constitutional:{halt_id}
- **verdict**: DISAGREE
- **cell_value**: reactions: expiry none; clock fuse = charter.halt_fuse_secs from first_held by receipt
- **cell_source**: formal/derivation/reaction_text.tsv
- **prose**: A node that receives it halts in the same step and **latches**. The node's store records the instant of the latch, and the halt is active at that node from
- **cc_ref**: CC 4.2.1.1
- **quote**: The nonce is single-use within `valid_until`.
- **note**: the entry says the halt row has no expiry, sourced from `A confirmed halt carries no TTL` (CC 4.2.1.3); CC 4.2.1.1 twice gives the row a `valid_until` that bounds replay (here and `within the valid_until window`). CC 2.6.1.7 leaves `valid_until` optional on any row. The two may speak of different things (the halt's effect has no TTL; the row's member bounds the nonce), and the text does not say which. The latch and its idempotence are not a freshness

### window, CC 4.4.3.5.2, consent:deletion_sla:{days}

- **column**: window
- **section**: 4.4.3.5.2
- **family**: consent:deletion_sla:{days}
- **verdict**: DISAGREE
- **cell_value**: reactions: clock sla = self.days from admitted(consent:state:revoked)|withdrawn(target); on close(sla) unless withdrawn(target)|superseded(target)|purged(target) -> emit hard_case:deletion_window_breach by identity:substrate_persist
- **cell_source**: formal/derivation/reaction_text.tsv
- **prose**: When subject `s` emits `consent:state:revoked` (or an admitted `withdraws`) against target `T`, substrate watches for producer compliance:
- **cc_ref**: CC 4.4.3.5.2
- **quote**: .where(dimension == "consent:deletion_complete")
- **note**: the section discharges the watcher by a consent:deletion_complete row asserted after the revocation; the entry discharges it only by a withdrawal, a supersession or a purge of the target and never reads consent:deletion_complete. CC 3.3.1 supports the entry (`the watcher is cancelled only by a withdraws, supersedes or hard deletion of the row`; D1: proof of deletion is the absence, not a new artifact); CC 4.5.2.2 names both. The text is at odds with itself

Two near-disagreements are filed as RICHER or AGREE because each side is faithful to a section: (a) CC 3.1.3.4, `collection:{kind}`: the change item says every file under a promoted directory stands, and the section says the promoting author's own files widen (`need:cascade_by_author`); (b) `licensure:{authority_id}` carries two orderings in its fold cell, `max(asserted_at),min(attestation_id)` from CC 3.3.9 and `max(quorum_weight),max(asserted_at),min(content_hash)` from CC 5.3.2.3: the text gives the family two last tie-breaks.

## FILLS, by table

| table | statement | family | proposed |
|---|---|---|---|
| family_model cell (freshness) | CC 2.4.1.2.1 (freshness) | licensure:{authority_id} | `{"judged_at": "signed_instant_with_W", "W": "admission_freshness_window_secs"}` |
| family_model cell (freshness) | CC 3.1.3 (freshness) | cosign:{state} | `{"judged_at": "signed_instant_with_W", "W": "admission_freshness_window_secs"}` |
| reaction_text.tsv | CC 3.1.3 (freshness) | census:partial:{class} | `on admitted(census:composite:{class}) -> read closed` |
| family_model cell (freshness) | CC 3.3.4 (freshness) | membership:{stage} | `{"judged_at": "signed_instant_with_W", "W": "admission_freshness_window_secs"}` |
| family_model cell (freshness) | CC 4.3 (freshness) | deferral:response:{outcome} | `{"judged_at": "signed_instant_with_W", "W": "admission_freshness_window_secs"}` |
| fold_text.tsv | CC 3.1.1 (projection) | commitment_fulfillment:{prior_contribution_id} | `feeds=duty:{kind}` |
| fold_text.tsv | CC 3.1.1 (projection) | duty:{kind} | `reads=own+commitment_fulfillment:{prior_contribution_id}; by=reader` |
| reaction_text.tsv | CC 3.1.1 (projection) | duty:{kind} | `on fold(duty_unmet) -> emit hard_case:duty_unmet by origin_door` |
| fold_text.tsv | CC 3.1.3.3 (projection) | custody:{kind} | `reads=own&live; key=content,attesting_key_id; combine=count(attesting_key_id); by=reader` |
| reaction_text.tsv | CC 3.1.5.2 (projection) | fidelity:explainability_sla:{tier} | `on fold(sla_breach) -> emit hard_case:sla_breach_unattested by origin_door` |
| reaction_text.tsv | CC 3.1.9.4 (projection) | watchlist:{id} | `[csam] on matched(self) -> emit takedown_notice:{basis} by identity:substrate_persist; on matched(self) -> emit detection:{detector} by identity:substrate_persist` |
| fold_text.tsv | CC 3.3.11 (projection) | topical_relation:{kind} | `@kind=replies_to|comments_on: by=reader` |
| family_model cell (placement) | CC 6.1.9 (placement) | census:member:partial | `targeted_room` |
| reaction_text.tsv | CC 3.4.1 (window) | accord:lifecycle | `expiry required valid_until max accord_heartbeat_max_secs from asserted_at` |
| reaction_text.tsv | CC 4.2.1.1 (window) | accord:invoke:constitutional:{halt_id} | `expiry none; clock fuse = charter.halt_fuse_secs default accord_halt.window_secs from first_held by receipt; on close(fuse) unless admitted(accord:lifecycle:confirmed) -> read lapsed` |
| reaction_text.tsv | CC 4.2.6 (window) | trust:{job}:{version} | `[charter] clock participation = admission_freshness_window_secs from asserted_at by receipt; [charter] on close(participation) -> read closed` |
| reaction_text.tsv | CC 4.5.3 (window) | takedown_notice:{basis} | `[DsaArticle16] on admitted(self) -> do stop_serving; [DsaArticle16] clock withhold = withhold_window_dsa16 from admitted(self) by receipt; [DsaArticle16] on close(withhold) -> do destroy_bytes; [OsaIllegalContent] on admitted(self) -> do stop_serving; [OsaIllegalContent] clock withhold = withhold_window_osa from admitted(self) by receipt; [OsaIllegalContent] on close(withhold) -> do destroy_bytes; [CommunityStandards] on admitted(self) -> do stop_serving; [CommunityStandards] clock withhold = withhold_window_community_standards from admitted(self) by receipt; [CommunityStandards] on close(withhold) -> do destroy_bytes` |
| reaction_text.tsv | CC 7.5.5 (window) | retirement:{state} | `[decided] clock objection = decider.objection_window_secs default default_standing.window_secs from first_held by receipt` |
| fold_text.tsv | CC 3.1.3 (formula) | census:composite:{class} | `test=source_count>=census_k_floor !census_composite_below_k` |
| fold_text.tsv | CC 4.4.2 (formula) | ratchet:flag:counter_rii:{layer} | `combine=median(score); by=reader` |
| fold_text.tsv | CC 4.4.2 (formula) | ratchet:flag:density_anomaly | `combine=median(score); by=reader` |
| fold_text.tsv | CC 4.4.2 (formula) | ratchet:flag:expertise_attestation_anomaly | `combine=median(score); by=reader` |
| fold_text.tsv | CC 4.4.2 (formula) | ratchet:flag:harassment_pattern | `combine=median(score); by=reader` |
| fold_text.tsv | CC 4.4.2 (formula) | ratchet:flag:out_of_distribution_voting | `combine=median(score); by=reader` |

## Sections where every statement of these columns was AGREE or FILLS

These sections could point at the table for the statements this lane read (the count is of statements in these seven columns only; other columns of the same section were read by other lanes).

CC 2.3.2.4 (1), CC 2.4.1.1 (2), CC 2.6.1.7 (1), CC 3.1.2 (3), CC 3.1.2.1 (1), CC 3.1.3 (16), CC 3.1.3.1 (8), CC 3.1.5.2 (1), CC 3.1.6 (1), CC 3.1.7 (1), CC 3.1.8 (1), CC 3.1.8.1 (3), CC 3.3.1 (3), CC 3.3.2 (1), CC 3.3.6.3 (1), CC 3.3.8 (1), CC 3.3.9 (2), CC 3.3.11 (1), CC 3.4.9 (1), CC 3.4.12 (1), CC 4.1.3 (1), CC 4.2.2.1 (1), CC 4.2.6 (5), CC 4.4.2 (1), CC 4.4.3.1.1 (1), CC 4.4.3.2.4.1 (3), CC 4.4.3.2.6 (1), CC 4.4.3.4 (1), CC 4.4.3.4.2 (1), CC 4.4.3.4.4 (2), CC 4.4.3.4.6 (1), CC 4.4.3.4.7 (1), CC 4.4.3.5 (1), CC 4.4.3.5.1 (2), CC 5.3.2.1 (1), CC 6.1.5 (1), CC 7.5.5 (1)

## Notes for the build

- The inventory's family stems are loose: `community` resolves in the registry to `community:listing`, while most statements filed under it are about `group:roster`, `membership:{stage}`, `ballot:moderator` or a `trust:{job}:{version}` edge. The `family` field of the output names the family the sentence is about.
- 21 rows are `(no row)`: `location_proof`, `external_content`/`chat_message`, `organization`, `org_membership`, `wholeness_witness`, `storage_budget`, `corpus_want`, `conformance`, `scores`. They are subject kinds or transport frames; their placement, window and monotone statements have no cell to land in.
- Literals in existing fold statements that have or want a name: `last(4)` on `census:expected_active` (no name), `min(2,n)` on `ballot:moderator` (`community_floor_voices`).
- `reaction_text.tsv` has the Dmca512 withhold window and not the three others that `constants.tsv` already names; and the halt fuse has no `default` although the text gives one.
