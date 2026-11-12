# Third reading, share 1: summary

Head read: rc19 at 87c1730. Output: `out_r3_1.tsv` beside this file (30 findings).

## Per rule key

| Rule key | Statements in the inventory | Findings | Major new | Major known | Minor new | Minor known |
|---|---|---|---|---|---|---|
| `row_shape` | 366 (269 family, 97 other) | 11 | 3 | 0 | 7 | 1 |
| `census` | 46 (25 family, 21 other) | 17 | 7 | 2 | 7 | 1 |
| `other:choice-item` | 13 | 2 | 0 | 1 | 1 | 0 |
| Total | 425 | 30 | 10 | 3 | 15 | 2 |

Known ids met: C154, C155, C156, C259, C317. Checked and found fixed in the text, so not reported:
C140 (the confirmation now says "four facts"), C326, C327 and C330 (CC 2.1 now states the key grant and
the roster version as exceptions to the producer rule), C343 (the MAY parenthetical of CC 3.4.11 is
gone), and the rounding half of C156 (CC 1.13.3.3 no longer lists rounding as a mitigation).

## How far each key was read

- `census` and `other:choice-item`: every statement read in its section today, side by side, with
  CC 6.1.9, CC 4.5.13, CC 3.1.3, CC 2.6.1.7 and CC 1.13.3.3 read whole for the census; compared with
  `governance_policy.json`, `family_model.json` (every cell of the eight census and ballot families),
  the CC 8.10 cards, `choice_item.cddl`, `transitions.json` (the widen, undo and confirm cells of all
  455 transitions agree with the confirm rule) and `reactions.json` (one row, the election window; no
  reaction is typed for a census share's expiry at the period's end, which I did not report as a
  conflict).
- `row_shape`: not finished to the same depth. Done: every member of the CC 2.1 tables compared
  mechanically with CC 2.6.1.2 and CC 2.6.1.7 (59 members, three tables); the gists of all 366
  statements read; the statements that state one thing in more than one place followed into the text
  (scope, stance, expires_at, role, references_attestation_id, witness_relation, key grant members,
  device_class, location resolution, accord lifecycle kinds, hard-case kinds, the envelope cap, the
  session key, run_kind, retirement states, goal scale); the registry's open and closed flags compared
  with the Part 3 rows. Not done: a statement-by-statement reading of the roughly 190 single-home
  family rows of CC 3.1.1 to 3.1.10 and CC 3.3.x against their family-model body cells and CC 8.10
  cards, and CC 4.4.3.2.8, CC 6.1.1, CC 6.1.5.2 and CC 7.5.5 against data. Those rows are where a
  further pass would look.

## Major new findings in full

1. **`census`: what a fallback vote is counted over (CC 4.5.13).** "A silent member is not in the
   denominator. The tally is taken over **who shows up**" against "The base is the standing roster at
   or below the count minimum the governance policy table pins and, above it, the expected-active
   count". The policy row `moderation_action` has base `active` and floor 1/2. With 3 of 40
   expected-active members voting, 2 keep-votes carry under the first and fail under the second. The
   census model refuses the first reading by name (`ThresholdBase = responders`).
2. **`census`: the base law in the data is not the census (CC 4.5.13 against
   `governance_policy.json`).** The data computes `base(N) = N if N <= k else max(min, k + (N - k) //
   tail)` from roster size alone (a roster of 100 gives 14) and the decider reads it. The text takes
   the base above the count minimum from `census:expected_active` under the ratchet. Both are marked
   provisional, but they are different functions, and an implementation that replays the decider
   never reads the census row.
3. **`census`: "the count minimum the governance policy table pins" (CC 4.5.13, CC 6.1.9 against the
   data).** The data has `min_count` (community 2), the fewest voices, and `base_law.k` (12), the
   roster size up to which the base is the roster. The phrase fits the first by name and the second
   by meaning; rooms of 3 to 12 get a different base under each.
4. **`census`: does the floor of ten apply to a secret poll (CC 2.6.1.7 against CC 3.1.3 and
   CC 6.1.9).** The `source_count` row is required on `ballot:tally` and says "below 10 the cell is
   refused census_composite_below_k". The `ballot:tally` registry row lists no below-k refusal and
   CC 6.1.9 gives a tally only the dominance gate. A room of six gets a poll result under one and a
   refused tally under the other.
5. **`census`: multiplicity on a composite (CC 6.1.9 against CC 2.6.1.7 and CC 3.1.3).** CC 6.1.9:
   the value is 1 by construction "and the census door refuses any other value". CC 2.6.1.7 and the
   CC 3.1.3 refusal list apply only the R9 gate, which admits 2 over a large enough source count. No
   token is named for the CC 6.1.9 refusal.
6. **`census`: the expected-active fold reads four periods (CC 6.1.9 against `family_model.json` and
   the CC 8.10 card).** Text: the owner sets its own four-period bit, which "is not something
   recoverable from a sum", and the count is recomputed from the period's two partials. Fold cell:
   `reads=census:member:partial&last(4); … combine=count(owner)`. The window is applied twice, or
   owners are counted from sums that do not hold them.
7. **`census`: the release of a frozen base (CC 6.1.9 against the same fold).** Text: released by the
   first period whose count is two thirds of the count before the fall. Fold cell:
   `test=count*3>=prev*2 ?open:frozen`, one test against the previous period. Read period by period, a
   base frozen at a fall from 30 to 10 is released the next period at 10; the text holds it until 20.
8. **`row_shape`: a grant with no scope (CC 2.1 and CC 2.6.1.7 against CC 3.3.1, CC 2.6.1.2 and
   CC 3.3.5).** `scope` is "REQUIRED on consent:state:granted", and "A `granted` naming no scope
   matches nothing, by design". CC 2.6.1.2 lists it with the optional members and CC 3.3.5 admits a
   granted `consent_record` without it. Refused at the door, or admitted as a grant of nothing.
9. **`row_shape`: the stance set (CC 3.3.1 against CC 3.1.5, CC 3.3.5 and the registry).** CC 3.3.1
   heads its row `consent:state:{granted|revoked}` and calls the values closed. The others have three,
   `expired` being substrate-emitted. A door built from CC 3.3.1 refuses another substrate's
   `consent:state:expired` row.
10. **`row_shape`: `expires_at` on a proposal (CC 2.1 and CC 2.6.1.2 against CC 2.6.1.7).** The
    signed-object table gives the member as optional and names where it is required: the two census
    shares. CC 2.1 and CC 2.6.1.2 require it on a membership proposal and CC 3.1.3 on a
    lineage-witness proposal. A door driven by the table admits an invitation that never expires.

## Major known

- C156 (`active_count` raw or after the ratchet): the wording of CC 2.6.1.7 is still there.
- C154 (one return per node or per owner): the table reads it as no conflict because the token is per
  owner; CC 2.6.1.7 derives the token from `node_secret`, so the ground of that reading is not in the
  text. Reported as major for that reason.
- C317 (announcing starts on, against the minor floor): to fix from the text, and not yet fixed.

## Keys not finished

`row_shape`, as described above. `census` and `other:choice-item` are finished.
