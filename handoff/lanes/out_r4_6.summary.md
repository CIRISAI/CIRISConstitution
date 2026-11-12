# Fourth reading, share 6: summary

Rule keys: `moderation`, `delegation`, `reserved_prefix`, `policy_row`, `accord`, `other:list-of-record`, `replication`. Output: `out_r4_6.tsv` beside this file (52 findings).

## The three numbers

- New major findings, text against text: **5**
- New major findings, text against data: **10**
- Statements opened in the text: **about 330 of 425**; read by gist only: **about 95** (listed at the end)

## Per rule key

| Rule key | Statements | Findings | Major new | Major known | Minor new | Minor known |
|---|---|---|---|---|---|---|
| moderation | 153 | 26 | 7 | 10 | 8 | 1 |
| delegation | 102 | 7 | 2 | 2 | 3 | 0 |
| reserved_prefix | 76 | 11 | 3 | 4 | 4 | 0 |
| policy_row | 55 | 4 | 2 | 0 | 2 | 0 |
| accord | 36 | 4 | 1 | 0 | 2 | 1 |
| other:list-of-record | 2 | 0 | 0 | 0 | 0 | 0 |
| replication | 1 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **425** | **52** | **15** | **16** | **19** | **2** |

## Major new findings, text against text

1. **A lift against the takedown's own reversal rule** (CC 4.5.13, CC 4.5.3). CC 4.5.13 lets the members' lift undo "a takedown still inside its withhold window". CC 4.5.3 computes withholding from one thing only: an admitted notice with no admitted reversal, the reversal being a review-holder's `reconsideration` row. A holder built from CC 4.5.3 keeps withholding after a lift and deletes at the window's close.
2. **Who issues a slashing verdict** (CC 3.1.6, 3.4.7.2, 3.4.14 against CC 4.5.5, 3.4.13). Three sections say the WA quorum is the gate and owns the verdict. CC 4.5.5 makes `slash` a delegable duty whose holder signs alone, and its duty-holder table has no slashing row saying who holds that duty over a target.
3. **A moderator ejecting an agent** (CC 1.13.2, CC 4.5.13). CC 1.13.2 says a person may eject an agent from a community they moderate at any time, for any reason, as a moderation act. CC 4.5.13 says no single key ever removes a member from the roster. Where an agent's key sits on a roster the two differ, and neither states the exception.
4. **Whether the person named learns of a private report** (CC 4.5.5, CC 4.5.13). CC 4.5.5 says the person named always sees that a record about them exists, its kind, its consequence and who answers for it. CC 4.5.13 says a report filed privately "is seen by nobody but the duty holder".
5. **One moderator's term lapsing** (CC 4.4.3.2.8, CC 4.5.4). CC 4.5.4 locks a room only when no live `moderate` holder remains. The CC 4.4.3.2.8 bullet says a lapsed `moderate` edge locks the room and opens an election, and the reactions data follows that reading with no condition.
A sixth pair is text against text but is recorded as known: **who may rate content** (CC 4.4.3.8 and the CC 3.1.9.2 row against CC 3.1.9 and CC 3.3.12). It is marked C323, a data fault whose resolution calls the text consistent. It is not: two sections reserve `content_rating:*` to a conferred `trusted_publisher`, two call it unreserved open vocabulary, and CC 3.3.12 holds no emitter rule though one is cited there.

## Major new findings, text against data

1. **The lift is absent from the data** (`objection:{state}`): the governance cell names the self-roster rows only, no fold or reaction reads `moderation_overturn`, and an objection may be withdrawn by its "subject".
2. **A moderation event signed by the content's subject**: the attest guard admits it; the CC 4.5.5 table and the same transition's roles cell do not.
3. **`subject_sha256_ed25519_raw`**: optional in CC 2.6.1.7 and the CDDL, required by the family model's body cell.
4. **`infra:*` tokens outside the closed set**: `infra:detect`, `infra:attest_assurance`, `infra:record_hard_case` gate rows in the family model; the text closes the set at eight exact strings.
5. **`regime:{artifact}:{version}`**: reserved to the substrate steward in CC 3.1.9.2; unreserved and open to any registered key in the registry and the model.
6. **`consent:state:expired`**: the substrate's alone in CC 3.4.5; the data has one signer cell (self or owner) for all three stances.
7. **`system:*`**: either substrate role in the text; `substrate_persist` alone in the model's cell.
8. **An accord roster change has no policy row**: `accord_majority` (cosigned, no window) is said to cover every threshold but the fire; CC 4.2.6 runs a roster change as participations inside W.
9. **The resumption has no guard**: CC 4.2.1.3 MUST-rejects a `lifecycle:active` whose `resumes_halt_id` is not the active halt; the data guards only the confirmation.
10. **Which count removes a member** (CC 3.2 and CC 3.1.3.2 against the policy row `community_remove`, generated into CC 4.5.13): the room's declared protocol (all others under `unanimous`, a strict majority under `majority`) or two thirds of the expected-active base. C283 asks this of admission and is open with the steward; removal is not listed there.

## Known conflicts found again

Still present, "to fix": C387, C365 and C388 (watchlist signer), C389 (residue: the OSA and DSA cells of CC 3.3.2), C377, C391, C392, C068 (slashing attest reads `registered`), C370 (text side fixed, data not), C396, C397, C323, C422, C423 (now also on `capacity_assurance` and `transparency_log:cosigned`). Open with the steward and found independently: C390, C419, C395, C399. Residue of a fixed one: C033 (the opening of CC 4.2 still says "when it is fired").

Found fixed and not reported: C393 (CC 3.4.11), C402 (CC 3.1.3 election id), C324 (CC 3.4.7.1), C401 (CC 3.4.3), C403 and C410 (CC 3.2 `founder_only`).

## Not finished: read by gist only (about 95 statements)

- `moderation`: the `hard_case` emission statements outside CC 3.1.9.4 and CC 4.5.3 (CC 2.6.6.1, 3.1.1, 3.1.4, 3.1.5.2, 3.3.1, 3.4.2, 3.4.4, 3.4.12, 3.4.14 R5 opened only for the verdict sentence, 4.4.3.1.1, 4.4.3.4.2, 4.4.3.5.2, 4.5.2.1, 4.5.2.3, 5.2, 5.3.2.2, 6.1.1, 6.1.5.2), CC 3.1.8, 3.3.5.1, 4.1.3 (one row opened), 4.5.10 to 4.5.10.4: about 40.
- `delegation`: CC 2.1, 2.6.8, 3.3.5.1, 3.4.10, 3.4.12 (five scope statements), 3.5, 4.2.1, 4.4.3.8, 4.5.2.2 opened for direction only: about 15.
- `reserved_prefix`: CC 3.1.1 stems, 3.1.5.4, 3.3.8, 3.3.11, 3.4.4, 3.4.12, 5.3.2.4.4: about 15.
- `policy_row`: the CC 3.2 infrastructure-quorum and witness-quorum statements, CC 3.3.10.1, 4.4.3.4.2, 5.3.3.2.5, 6.1.5.1, 6.1.9: about 20.
- `accord`: CC 2.6.1.2, 2.6.1.7, 3.3.4, 4.2.2, 4.2.5 opened in passing; CC 3.1.3.2 and the CC 3.2 restatements by gist: about 8.
