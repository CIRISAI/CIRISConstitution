# Fifth reading, share 1: summary

Branch rc19 at 1ee1bcf. Keys: `row_shape`, `census`, `other:choice-item`. Output: `out_r5_1.tsv` (24 findings).

## The three numbers

- New major findings, text against text: **1**
- New major findings, text against data: **1**
- Statements opened in the text: **about 400 of 425**; read by gist only: **about 25** (listed below)

## Per rule key

| Rule key | Statements | Findings | Major new | Minor new | Major known | Minor known |
|---|---|---|---|---|---|---|
| `row_shape` | 366 | 17 | 2 | 8 | 5 | 2 |
| `census` | 46 | 5 | 0 | 2 | 2 | 1 |
| `other:choice-item` | 13 | 2 | 0 | 2 | 0 | 0 |
| Total | 425 | 24 | 2 | 12 | 7 | 3 |

## The major new findings in full

**1. A standing proposal against "a proposal seats at most once" (text against text; CC 3.1.3.2, CC 3.2).**
CC 3.1.3.2 says: "A proposal seats at most once. A widening that cites an acceptance an admitted
widening has already consumed is not admissible, so one invitation never admits twice." CC 3.2 says an
open room's founder issues one standing `membership:proposal:v1` "addressed to any requester", its
`subject_key_ids` "resolved at acceptance rather than fixed at proposal". A builder who spends the
proposal on its first seating admits one person per standing proposal; a builder who spends the
acceptance admits every requester. Admission rule (5) of CC 3.1.3.2 ("P has not already seated K"),
CC 3.2 and the CC 8.10 membership guard (spent per acceptance) support the second. The
"seats at most once" sentence needs the standing offer excepted. Two smaller faults sit beside it
(both in the TSV as minor): the 30-day expiry rule does not say whether it binds a standing proposal,
and the emitter rule ("the signer resolves to the proposal's `subject_key_ids[0]`") has no arm for a
proposal whose subject list is empty.

**2. `salt` marked required on census and ballot rows of this edition (text against data; CC 2.6.1.7,
CC 2.6.1.8, CC 8.10, `manifests/family_model.json`).**
The family model body cell of `census:share:{class}`, `census:member:share`, `ballot:moderator` and
`ballot:tally:{poll_id}` carries `salt`, type `bstr .size 16`, presence `required`, citing CC 2.6.1.8,
and the CC 8.10 card prints it in the body. CC 2.6.1.8 is the planned v62 object; it says the JSON
object of CC 2.6.1.7 "stays the signed object of every earlier candidate", and neither the CC 2.6.1.7
table nor `manifests/signed_object.cddl` has a `salt` member (it is in `signed_object_v2.cddl` only).
A door built from the body cell refuses every census return of the current edition. The text is
consistent; the fault is the data's, which mixes two editions. It also puts the salt on `ballot:tally`,
a composite, where CC 2.6.1.8 names only a ballot and a census cell.

## Known conflicts found again

Still present: C436 (`valid_until` on `session:*`: CC 2.1 is repaired, the CC 2.6.1.7 row, the CDDL and
the family model body are not), C356 (`expires_at` on a proposal), C350 (the k floor on a room's
tally), C169 (v1 wrap row against "v2 only"), C188 (`consent:scope:*` still named as a grant's
discriminator in CC 2.4.1.2.1 and CC 4.5.13), C352 (base law in `governance_policy.json`).
Half fixed: C349 (CC 3.1.3 now refuses a multiplicity other than 1; the CC 2.6.1.7 gloss does not),
C438 (the partnership halves are repaired; member sets (b) and (c) are still flat), C440 (`ranks` is
named; presence, the election id and the acceptance row's body are missing).
Open with the steward: C354 (a grant with no scope).

Checked and found repaired, so not reported: C326 and C327 (CC 2.1 now states the key-grant and roster
exceptions), C328 (CC 2.1 now has the substrate resolve the dimension), C353 (both sections now say
"size `k` of the base law"), C437 (CC 2.4 now has the resignation signed by the leaving member alone),
C351 (CC 4.5.13 now says the members' vote on a moderation action does not read the base).

## Read by gist only (about 25 statements)

- CC 1.7, CC 1.13.2, CC 1.13.4 (3)
- CC 2.6.1.3 (1)
- CC 3.1.5.2 non-maleficence row (1)
- CC 3.2: the two `location_proof` resolution restatements, `archive_mode`, `infrastructure_constraint`,
  `admission_quorum_basis` (5)
- CC 3.3.3 `location_proof` struct, CC 3.3.4 family struct (two statements), CC 3.4.12 (two statements):
  only the one line was opened, not the paragraph (5)
- Statements that sit past the point where I cut a long table cell: CC 3.1.1 takedown bases, CC 3.1.3
  `cosign` signature row, CC 3.1.5.5 safety-battery kinds, CC 3.1.9.4 `hard_case` kinds and the two
  `observation` rows' tails, CC 3.1.9.7 avoidance goal, CC 3.3.6 `device_class` (about 10)

## Keys not finished

None left unread. The comparison with data covered `family_model.json` body cells for about 70 families,
`signed_object.cddl`, `governance_policy.json` and `.tsv`, `choice_item.cddl`, the verbs of
`transitions.json`, and three CC 8.10 cards (census, membership, session). `reactions.json` was not
compared for these keys, and the other CC 8.10 cards were not opened.
