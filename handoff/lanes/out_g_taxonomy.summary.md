# Lane G taxonomy: what each RICHER row needs

All 491 `RICHER` rows of the four reader tables are classified in `out_g_taxonomy.tsv` (cosign 73, audience 58, erasure 259, lifecycle 101). Each row was read; the readers' need tags were a starting point and were overridden where the prose said otherwise. No row was classed `general_rule`: every statement that looked general turned out to be keyed on a family, a leaf, a group kind or a cohort record.

## Count per concept

| concept | rows | of the five |
|---|---|---|
| `guard` | 119 | yes |
| `fold` | 88 | yes |
| `reaction` | 63 | yes |
| `count` | 41 | yes |
| `change_constraint` | 32 | yes |
| `missing_row` | 30 | no |
| `evidential_weight` | 22 | no |
| `plain_cell` | 20 | no |
| `policy_row` | 16 | no |
| `audience_rule` | 14 | no |
| `field_rule` | 12 | no |
| `derived_value` | 11 | no |
| `conditional_cell` | 11 | no |
| `erasure_effect` | 10 | no |
| `ui_duty` | 2 | no |

The five designed concepts take 343 rows (70%). Ten other names take 148.

## Count per `executable`

| executable | rows |
|---|---|
| yes | 420 |
| partly | 70 |
| no | 1 |

The 70 `partly` rows: all 30 `missing_row` (runnable once the row exists), 21 `evidential_weight`, 5 `reaction` (a breach routed to a moderation type that a person raises; a SHOULD on the grantor's node), and 14 scattered (a SHOULD-strength guard, an out-of-band ceremony, a reader's own un-trust, assessors attesting their own independence, a duty-holder's discretion, the two display rows, the two erasure executors). The one `no` is CC 3.3.3: nobody verifies that a location is true.

## How the readers' tags were re-read

- `sole_evidence_bar` (32 rows) is a `guard` on `slashing:{outcome}` over the families in its `evidence_refs`, with `evidential_weight` second. It is executable.
- `consumer_composition`, `reader_weight`, `absence_default`, `fold_weight` (read by no fold) and the lifecycle `N-CONFLICT` and `N-EFFECT` tags are `fold`: a reader-side fold, a filter on the emitter, a value when no row is held, a boundary.
- `N-EXP` and `N-SIDE` are `reaction`; required or forbidden `valid_until` carries `field_rule` second (8 rows).
- `N-ENDS` splits: a landing row or a lapsed seat that ends something is `reaction`; what ends with a dissolved record is a `change_constraint` cascade; a status read from the issuer's later rows is `fold`.
- `N-WHO` and `N-COND` are `guard` (a predicate on the withdrawer or on the state).
- `protocol_admissibility` (11 rows) is not `count`: it bounds a field of the group record by group kind. It is `field_rule`.
- `entrenchment` is `change_constraint`, except "infrastructure MUST be entrenched", a `field_rule`.
- `threshold` and `missing_policy_row` are `policy_row`.

## Second concepts

259 rows carry a second concept. The most frequent: `count` 47, `evidential_weight` 46, `conditional_cell` 37, `fold` 35, `change_constraint` 23, `guard` 21, `reaction` 19. `conditional_cell` is primary on 11 rows and second on 37: 48 rows want a cell keyed by a leaf, role, subkind or instance attribute, whichever column holds it.

## The concepts outside the five

### `missing_row` (30)

The statement is about a record kind with no row among the 184.

- CC 3.3.3, `location_proof`: "Producers MAY scope to `community` with a specific `community_id`".
- CC 5.3.3.2.5, `live_stream`: live by default, nothing is held past forwarding unless the publisher keeps it.
- CC 4.4.3.2.8, affiliation charter members: decryption gated on a member attribute (clearance, unexpired credential).

Verdict: belongs to existing data. Add rows to `manifests/namespace_registry.json` (through Part 3's tables) and so to `manifests/family_model.json` for `location_proof` (15 rows here), `live_stream`, `local_data`, `chat_message`, `external_content`, `organization`, `org_membership`, `consent_record`, the transport destination, `observed:*` and `epistemic:*`, the storage budget and the `delegates_to` duty edge. The affiliation charter members (`erasure_policy`, `legal_hold`, `member_attributes`, `disclosure_accounting`) are fields of a record, not families: they want a small table of their own keyed by charter member. No new concept is needed; every one of these rows names a second concept that then applies.

### `evidential_weight` (22)

What an admitted row proves and what a reader may rest on it.

- CC 3.1.5, `trace:{form}:{version}`: admission vouches for parseability only.
- CC 3.1.8, `capacity:*` and `detection:*`: a measure that feeds human and quorum judgement and never stands as a verdict by itself.
- CC 3.3.1, `consent:deletion_complete`: evidence toward proof of deletion, never proof alone.

Verdict: a small enum column, `vouches` over {shape, signature, origin, possession, chain} with an `advisory` flag, would let a check prove that no fold reads an advisory family as a verdict. That half is executable and is already carried where it bites (the slashing guard, the custody weights 2/1/0, the reader filters, all classed under `guard` and `fold`). The remainder states limits of the claim and should stay prose: it tells a reader what not to conclude, and no kernel acts on it.

### `plain_cell` (20)

A closed token on an existing column, or one simple enum column. No grammar.

- CC 2.4.1.1, `detection:*` and `capacity:*` (8 rows): a `retraction_class` token for a third party's finding.
- CC 6.1.5.2, identity, consent and config records: "always pinned" (a `pin_class` column: pinned, pin on consent, cache).
- CC 6.1.9, `census:composite:{class}`: five equalities any holder can recompute (the existing `derived` column, gap in every family).

Verdict: belongs to `manifests/family_model.json`. Extend the lifecycle and subject vocabularies in `tools/build_family_model.py` (`retraction_class`, `recants`, `in_audience`, `binds_segment`), fill `derived`, add `pin_class`.

### `policy_row` (16)

A number, a door or a governed setting that the policy table does not hold.

- CC 4.2.6, `accord:*`: a roster change needs floor(N/2)+1 yes from distinct current members within W.
- CC 4.5.13, `moderation:{allegation_type}`: a harm report's window default is removal and the act that must land is the keep.
- CC 3.1.9.3, `witness_diversity`: N = 3 by default and four bars.

Verdict: belongs to `constitution/governance_policy.tsv`. Two things the table cannot say today: an `at_window` outcome other than tallied (default removal, the keep must land), and a governed setting that is not five numbers (a credit limit, the moderator-quorum switch, a room forbidding kept streams). The first is one more value of an existing field; the second wants a `setting` kind of row.

### `audience_rule` (14)

Who is served what, when and by what carrier, beyond tier and audience.

- CC 3.1.3, `cosign:{state}`: served to "the members who were active at the event's signed instant and are members still when served, and no one else".
- CC 3.2, public room content: nothing is pushed to a node whose owner has not joined, yet anyone may read on request.
- CC 5.4.6, `identity:occurrence`: for an unannounced node the rows "ride sealed inside the contact request and inside the acceptance".

Verdict: deserves parts on the existing `replication` cell, not a new column: `audience_as_of` (two instants), `excluded` (a named key), `on_request`, `carrier`, an audience token for root holders, `hold_bound`, `withhold_exempt`. All but two rows are executable.

### `field_rule` (12)

A bound on a field's value, or its presence, by group kind or subkind.

- CC 3.2: "A community above the family never names founder_only as its consensus_protocol".
- CC 3.2: an infrastructure community is founded at "N ≥ M + 1" active human founders, M at least 2.
- CC 3.2: `open:self_admit` is admissible only on a public community.

Verdict: deserves a table of its own, group kind and subkind by protocol kind with the numeric bounds and the entrenchment requirement. The rule is stated eleven times in five sections and held nowhere as data. It is keyed on the group kind, not on a family, so it is not a family-model column. Fully executable. The same table shape would hold the eight required or forbidden `valid_until` rules that sit second under `reaction`.

### `derived_value` (11)

A cell whose value is read from another row.

- CC 3.1.3.3, `custody:{kind}`: the report takes the content's scope, and federation where the content's cohort is public or infrastructure.
- CC 2.4.1.2.1, `licensure:{authority_id}`: the scope is "the authority's declared choice *per licence class*" in the charter.
- CC 3.1.3.4, `file:{version}`: placed at the directory's scope at that instant, and not following it afterwards.

Verdict: deserves three tokens in the `placement` and `replication` vocabularies: `scope_of(content)`, `by_cohort_record(member)`, `scope_of(container, at_placing)`. Five cells already say this in free text. Fully executable.

### `conditional_cell` (11 primary, 37 second)

One family, several values keyed by leaf, role, subkind or instance attribute.

- CC 3.3.5, `consent:state:{stance}`: a revoked stance "is **NOT local-tier-eligible**".
- CC 3.4.5.1, `config:{scope}`: the `admission` and `transport` leaves MUST be emitted at `self`.
- CC 3.3.4, `membership:{stage}`: a removal is cosigned, a resignation is the member's own row.

Verdict: a change to the model's form, not a column: let any cell be a map from a closed key (leaf, identity role, cohort subkind, cosigned or not) to a value, or split the family into rows per leaf. `membership:{stage}` already carries an informal map. This is the most frequent need hidden under the others, and the five designers will each meet it.

### `erasure_effect` (10)

What erasure leaves, who executes it, on what basis, when it is refused.

- CC 6.1.2.2, `takedown_notice:{basis}`: only the content hash survives, for the legal retention window.
- CC 4.4.3.5.4, legal hold: the route is refused with reason, keyed on the affiliation class or the hold's scope.
- CC 7.5.5, `retirement:{state}`: inside a sealed record the tombstone is written by whoever holds custody.

Verdict: parts on the existing `erasure_route` cell: `leaves`, `terminus`, `basis`, `executed_by`, `refused_when`. Five of the ten also wait on a missing row or table.

### `ui_duty` (2)

- CC 3.1.3.3, `custody:{kind}`: the four per-device states a reader is shown and what a UI must not show.
- CC 6.1.9, `census:composite:{class}`: display rounding is a presentation convention.

Verdict: stays out of the family model. It belongs with `manifests/ui_primitives.json` if anywhere. The second row conflicts with CC 1.13.3.3, which lists rounding as a mitigation of the published value.

## What share a kernel could run

- The five designed concepts: 343 rows, 331 of them `yes`.
- Existing data files with no new concept (`plain_cell`, `policy_row`): 36 more, 35 `yes`.
- Three more concepts (`audience_rule`, `field_rule`, `derived_value`): 37 more, 35 `yes`.
- Keyed cells (`conditional_cell`): 11 more, all `yes`.

That is 412 of 491 (84%) runnable from data. Adding the missing rows brings the 30 `missing_row` statements in and the figure to about 90%. The residue is `evidential_weight` (22), `ui_duty` (2), the two erasure executors and the dozen `partly` rows inside the five.
