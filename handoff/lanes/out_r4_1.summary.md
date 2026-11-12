# Fourth reading, share 1: summary

Head read: rc19 at 05cbcc8. Output: `out_r4_1.tsv` beside this file (33 findings).

## The three numbers

- New major findings, text against text: **3**
- New major findings, text against data: **2**
- Statements opened in the text: **384 of 425**. A further 39 were read in their own verbatim sentence
  (the `entry_phrase`) without the paragraph around it, and 2 by gist only. Lists below.

## Per rule key

| Rule key | Statements | Findings | Major new | Major known | Minor new | Minor known |
|---|---|---|---|---|---|---|
| `row_shape` | 366 (269 family, 97 other) | 19 | 4 | 2 | 12 | 1 |
| `census` | 46 (25 family, 21 other) | 9 | 0 | 5 | 4 | 0 |
| `other:choice-item` | 13 | 5 | 1 | 1 | 3 | 0 |
| Total | 425 | 33 | 5 | 8 | 19 | 1 |

Known ids met and reported: C154, C156, C259, C317, C348, C350, C352, C354, C356.
Still present: C356 (the `expires_at` row of the signed-object table), C350 (the below-ten note on a
tally), C352 (the base law in the data), C348 (in a changed form: the freeze is now absent from the
fold, not mis-stated), C317 (announcing starts on), C259 (held), C156 (the `active_count` half; the
table refers to a C156b that is not a row), C154 (the ground of its no-conflict reading is not in the
text). C354 is open with the steward and reported because I would have reported it.

Known and found repaired, so not reported: C347 (the expected-active fold now reads
`over=active/owner`), C349 for CC 3.1.3 (the composite row now refuses a multiplicity other than 1),
C353 (both sections now say "the size `k` of the base law"; that repair made the new minor finding on
`k` in CC 6.1.9), C140, C326, C327, C330. C355 (two stances against three) is "no conflict on reading"
and I agree.

## Major new findings in full

### Text against text

1. **`row_shape`: a session claim without `valid_until` (CC 3.1.3.1 against CC 2.1 and CC 2.6.1.7).**
   CC 3.1.3.1: "The horizon is the row's own `valid_until`" and "A row without `valid_until` is
   malformed on this family." CC 2.1 and CC 2.6.1.7 list `session_id` and `claimed_at` as the members
   REQUIRED on `session:*` and give `valid_until` as OPTIONAL on every row, read by consumer policy
   ("If set, consumer policy treats the attestation as stale after that point"). A door built from the
   signed-object table admits a claim with no horizon, and the earliest such claim holds its session
   for ever, which is the case the horizon exists to prevent. `reactions.json` agrees with CC 3.1.3.1;
   the table lacks the row.
2. **`row_shape`: who signs a resignation (CC 2.4 and the roster folds of CC 4.4.3.2.4 and CC 4.4.3.4.4
   against CC 3.1.3.2).** CC 2.4 lists "`membership:widening:v1` / `removal:v1` / `resignation:v1`,
   cosigned", and the comment in `resolve_community` and `resolve_family` reads "revocations,
   widenings, resignations, each admitted per CURRENT consensus_protocol". CC 3.1.3.2: "a resignation
   is signed by the leaving member"; CC 3.3.4 and `transitions.json` (resignation: `selfAct`) agree
   with it. A door built from CC 2.4 or the fold comment keeps a member seated until a quorum signs
   their leaving. (The CC 3.1.3.2 row itself calls the last three stages "cosigned rows" one clause
   before it says who signs each.)
3. **`row_shape`: the partnership signing set against the signed object (CC 4.4.3.4.3.1 against
   CC 2.6.1.7 and CC 2.1).** CC 4.4.3.4.3.1 fixes "the REQUIRED core" of a `consent:partnership_*:v1`
   half at "eight members present in every `:v1` half", written flat with `attestation_type` and
   `attesting_key_id` at the top level, and adds "Additional REQUIRED members are a `:v2` bump". The
   signed object requires the `row` mirror (closed seven, `cohort_scope` and `subject_key_ids` among
   them; "a row with no mirror is refused `envelope_member_missing`") and `score` and `confidence` on
   every `scores` row. Bytes signed to the eight-member contract are refused at the door, and bytes
   that pass the door carry required members the contract forbids in `:v1`. The login `delegates_to`
   and the occurrence binding of the same section are flat in the same way and carry a `signed_at`
   member no other section has. CC 2.6.1.7 is rendered from data with vectors, so CC 4.4.3.4.3.1 is the
   stale side.

### Text against data

4. **`row_shape`: the moderation subject digest (CC 2.1, CC 2.6.1.2, CC 2.6.1.7 against
   `family_model.json`).** The text gives `subject_sha256_ed25519_raw` three times as optional on a
   `moderation:*` row, absent meaning "the subject is named some other way, or not at all". The body
   cell of `moderation:{allegation_type}`, read from the shipped store, says "moderation subject digest
   required (moderation_subject_digest)". A moderation row with no digest is admitted under the text
   and refused under the cell. If the cell means only "well-formed when present" it should say that.
5. **`other:choice-item`: the ballot's ranked member is `ranks` in the text and `ranking` in the data
   (CC 3.1.3 against `family_model.json`, the CC 8.10 card and `choice_item.cddl`).** The registry row
   of `ballot:moderator` names the member `ranks` ("up to three member keys in order"). The family
   model's body cell and its card name it `ranking` and cite CC 4.5.13, which uses neither word; the
   choice item's answer also carries `ranking`. Two emitters reading one each sign different members,
   and each door finds no ranks on the other's ballot.

## Minor new findings, in one line each

`row_shape`: the custody report's lapse (rule (5) `expires_at` against "72 hours from its instant",
with no requirement of the member in the text; `reactions.json` decides it); `size` on a `here` report
missing from the body cell; the `session:{kind}` body and lifecycle cells against CC 3.1.3.1 (the
reactions manifest is right); the triad's "`consent:scope:*` family" as the wire discriminator of a
grant (C188's fault in three more places); `recipient_key_id` and `content_sha256` in the cascade
pseudo-code and in the `key_grant` body cell; `hard_case:{kind}` open, yet "new kinds land via the
amendment process"; CC 2.2 has a producer declare two members the envelope makes optional;
`custodian_minted` placed before `retired` in "the closed lifecycle"; `role` "nullable" where an
explicit `null` is refused; the `trust:{job}` and `lineage_witness` body cells list fewer members than
the table and the registry row state; `for_key_id` "also carried on consent:state rows" under a
two-holder rule no consent section states.

`census`: `k` used for two numbers in CC 6.1.9; the share duplicate key (token, index, seat) against
the fold's (period, token); Part 1's "publish the median bucket" against the histogram of CC 6.1.9;
`salt` marked required today on four families from the planned CC 2.6.1.8.

`other:choice-item`: every stage of `membership:{stage}` is confirmed in `transitions.json`, leaving and
declining included, against "leaving [is] one step" (the other 455 confirm cells follow the rule,
checked mechanically); the schema's `self_choice` policy and the text's "self row, one voice of one, no
window" name no row of the policy table; the schema's write scope has five values where
`cohort_scope` has seven.

## How far each key was read

- `census` and `other:choice-item`: every statement read in its section, with CC 6.1.9, the census rows
  of CC 3.1.3, the census rows of CC 2.6.1.7, the census rows of CC 1.13.3.3 and the choice paragraphs
  of CC 4.5.13 read whole; compared with `governance_policy.json` (base law, decider, min_count, the
  sixteen rows), every cell of the nine census and ballot families in `family_model.json`, the
  CC 8.10 cards of `census:expected_active`, `ballot:moderator` and `membership:{stage}`,
  `choice_item.cddl`, `ui_primitives.json` (law L6), `reactions.json` and all 456 transitions' widen,
  undo and confirm cells. Two census statements (CC 6.1, the two lead sentences) and one (CC 1.13.2)
  were read in their own sentence only.
- `row_shape`: CC 2.1, CC 2.1.1, CC 2.4, CC 2.4.1, CC 2.4.1.2.1, CC 2.6.1.2, CC 2.6.1.7 and CC 2.6.1.8
  read whole; every Part 3 statement read in the paragraph or table row that carries it (161 lines of
  Part 3, with CC 3.1.3.1, CC 3.1.3.2, CC 3.1.3.3, the `key_grant` and `takedown_notice` shapes of
  CC 3.3.2, the `consent_record` shape of CC 3.3.5, the `consent:replication` shape of CC 3.3.7 and the
  community record of CC 3.2 read at length); CC 4.2.1.3, CC 4.4.3.4.1, CC 4.4.3.4.3.1, CC 6.1.1,
  CC 6.1.5.2 and CC 7.5.5 read in the paragraphs concerned. The body cell of all 184 families was read
  against the text; lifecycle, freshness and reactions were read for the families a finding touches.

### Read in the statement's own sentence only (39), not the paragraph

CC 1.13.2 (1), CC 1.13.4 (1), CC 2.2 (1), CC 2.3.2.3 (2), CC 2.4.2 (1), CC 2.6 (1), CC 2.6.1.3 (1),
CC 4.1.5 (2), CC 4.2.3 (1), CC 4.2.6 (2), CC 4.4.3.2.8 (7), CC 4.4.3.5.3 (1), CC 4.5.4 (1),
CC 4.5.5 (1), CC 4.5.9.2 to 4.5.9.4 (3), CC 4.5.12.2 (1), CC 4.5.13 (2: the ballot rows and the
objection states), CC 5.3.2.4 (1), CC 5.3.2.5 (2), CC 5.3.4 (1), CC 5.3.6.1 (1), CC 5.4.6 (1),
CC 6.1 (2), CC 6.1.5 (2).

### Read by gist only (2)

CC 3.2, the two statements on the resolution bound of a `location_proof` against a community's
constraint (their words were not located; the bound itself was read at CC 3.4.2 and CC 4.5.9.2).

### Read in part

Two Part 3 table rows are longer than I read: `cosign:{state}` (CC 3.1.3) from its **Audience** clause
on, and `goal:{scale}` (CC 3.1.9.7) from the group-declaration paragraph on.

## Not reported, and why

- The CC 2.1 producer rule names two exceptions (a key grant, a roster version). The owner-authored
  `consent:community_trust` grant (CC 3.3.1: attester the owner, attested the node) would be a third
  if it is ever placed at a targeted scope. The text does not state its scope, so I could not make it
  a conflict.
- The body cell of `community:listing` omits the admission policy and the named moderator that
  CC 3.1.1 and CC 3.2 list. CC 3.2 also says "there is no `admission` field", so the member name is
  not stated and the cell cannot be called wrong.
- A `trust:accepts:v1` edge to an authority that is a single key (CC 4.4.3.8) must still carry an
  `attached_head_digest` (CC 3.2: refused `trust_root_head_unnamed` "in every mode"). What head a
  single-key authority has is not stated. A gap, not two statements.

## Keys not finished

None left unread. `row_shape` is the one whose depth is uneven: the 39 statements above were not read
in their paragraphs, and the columns other than `body` were compared with the text only for the
families a finding touches.
