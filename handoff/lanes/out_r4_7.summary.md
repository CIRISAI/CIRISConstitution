# Fourth reading, share 7: summary

Repository at 05cbcc8 (branch rc19). Five rule keys, 428 inventory statements, every scope
including `family`. Output: `out_r4_7.tsv` beside this file (32 findings). Every quoted phrase
was checked by script to be present verbatim in the text or data file it is attributed to.

## The three numbers

- New major findings, text against text: **3**
- New major findings, text against data: **5**
- Statements opened in the text: **427**; read by gist only: **1**

The one read by gist only is `key_plane`, CC 5.2, "Persist wraps the DEK (v2) under each admitted
identity_occurrence's occurrence_key_id (self) or each member key_id in the family roster
(family)": the sentence is no longer in CC 5.2 (the C311 repair removed it), so there was nothing
to open. About 80 statements have no `entry_phrase`; those were located by word overlap inside
their section and the paragraph read. Where the match landed on the wrong line (seven in
`key_plane`, one in `roster_fold`) the passage was found by hand.

## Per rule key

| rule key | statements | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| key_plane | 146 | 10 | 2 | 1 | 7 | 0 |
| roster_fold | 113 | 7 | 3 | 1 | 3 | 0 |
| consent_fold | 65 | 8 | 3 | 1 | 3 | 1 |
| content_ingestion | 59 | 3 | 0 | 0 | 3 | 0 |
| subject | 45 | 4 | 0 | 1 | 2 | 1 |
| total | 428 | 32 | 8 | 4 | 18 | 2 |

Known ids met: C404 (held for Eric), C412, C427, C331 (each still present in the data), C188
(still present in the text), C360 (text repaired, data residue).

Known conflicts in this share that I found repaired in the text and did not report: C115, C170,
C291, C304, C311, C405, C411, C413, C414, C415, C428, C361/C416.

## Major new findings, text against text

1. **key_plane: who signs a family catch-up grant** (CC 4.4.3.4.1 against CC 4.4.3.4.4, CC 3.1.3,
   CC 3.3.2). CC 4.4.3.4.1: "For a `family` member the admitting host runs the walk after the
   member is admitted", re-wrapping every earlier DEK it holds. CC 4.4.3.4.4: "A member's
   substrate re-wraps nothing, because a key grant is sealer-only"; CC 3.1.3 makes the sealer a
   key that speaks for the blob's owner, and CC 4.4.3.4.3 refuses a grant issued on possession
   alone. A host-signed wrap of another member's blob is admitted under one reading and refused
   under the other. The data shows the same doubt: the card's signer is "member, owner" and its
   reaction emits the grant "by identity:substrate_persist" (reported as a minor data finding).

2. **key_plane: the instant a removal takes effect** (CC 4.4.3.4.5 against CC 5.1). CC 4.4.3.4.5,
   "the one statement of the removal rule", at any scope: "the first write after the removal is
   under a key the removed member was never granted". CC 5.1: the substrate MUST coalesce
   removals into one rotation per window T (2 s), and "A removed member's exposure window is
   therefore `≤ T`". CC 4.4.3.2.1 makes the community DEK the CC 5.1 cascade, so both instants
   fall on one key. CC 4.4.3.2.2 and CC 1.13.3.3 support rotate-before-next-write.

3. **consent_fold: a row with no deletion commitment** (CC 2.1 against CC 4.4.3.5.2). CC 2.1 on
   `deletion_window`: "Absent means the family's default." CC 4.4.3.5.2: "return # no SLA
   commitment; no watcher". Under one a deadline and a breach exist for every producer's row;
   under the other none does. No default window is stated anywhere. The watcher also reads only
   the `consent:deletion_sla:{days}` row, so a row carrying the `deletion_window` member and no
   such row is watched under CC 3.3.1 ("the member carries the commitment") and not under
   CC 4.4.3.5.2; reactions.json starts the clock from the row only.

## Major new findings, text against data

4. **roster_fold: the recovery guard is written for every widening**
   (`manifests/transitions.json`, `membership:{stage}` attest guard, printed in CC 8.10).
   `when(leaf=widening) (one trust:confers@landed[attested=signer,val:scope=object] else refuse &
   type(signer,user) else refuse & not type(signer,node) else refuse)`, reach whole. CC 3.2 T7
   asks this of the one recovery widening on a stalled roster. As data it refuses any ordinary
   widening whose signer holds no conferral. The change cell beside it carries
   `widening[stalled&recovery]`; the guard does not.

5. **roster_fold: no key change on a resignation from a community or affiliation**
   (`membership:{stage}` change cells). The cells rotate the epoch on
   `removal[scope:community|affiliations]` and stop wraps on `resignation[scope:self|family]`,
   and have nothing for a resignation at community or affiliations. CC 5.1: "Once a member
   leaves, subsequent content is sealed under a key that member cannot derive"; CC 3.2:
   resignation and removal are one row kind at the fold. As data, a member who resigns keeps
   reading.

6. **roster_fold: one cosigned withdraw for every membership stage** (`membership:{stage}`
   withdraw: roles member, policy cosigned, source code-v61). CC 3.1.3.2: "The inviter withdraws
   a proposal with the ordinary `withdraws`", and a growth already admitted is never re-judged.
   The attest row has per-stage policies; the withdraw row has none.

7. **consent_fold: a node-authored trace-capture grant is not counted**
   (`manifests/family_model.json`, `consent:community_trust`). Signer cell `owner_of_subject`
   (closed), fold `reads=own&signer:owner`. CC 3.3.1: "The node-authored form stays valid, and
   the fold below groups both forms by `attested_key_id`." The verbs cell also lacks recant.

8. **consent_fold: a proxy's consent state** (`consent:state:{stance}` signer cell
   `self | owner_of_subject(for_key_id) x none x {}`). CC 3.3.1 and CC 4.4.3.5.5 admit a row
   from a `delegates_to` proxy of the subject, the card's fold reads `signer:subject|proxy`, and
   the parent row `consent:{kind}` gives `state` a delegation arm. Two cells of one manifest
   disagree on whether a proxy's grant is admitted.

## Known majors still present

- C412: `identity:occurrence` withdraw and `identity:occurrence_revocation` attest read
  `selfAct` in transitions.json; the text requires the two paths or a strict majority.
- C427: the text of CC 4.4.3.5.5 is repaired to the boundary fold; the `consent:state:{stance}`
  fold cells still carry `cut=terminal` and `pick=rank(revoked>granted)`.
- C331: `"in_audience": "no"` in the default row and the family cells.
- C404 (for Eric): catch-up wraps for a kept stream's late joiner, CC 5.1 against CC 5.3.3.2.5.

## Notes on judgement

- The keep-change instant (CC 5.1 "wraps the current and later epochs" against CC 5.3.3.2.5 "at
  an epoch boundary") is filed minor because an unkept call holds no chunks past forwarding, so
  the wraps of the current epoch open little.
- CC 5.4.3's "except as the community's `archive_mode` permits" is filed minor because the body
  stays sealed under the epoch DEK either way.
- Not reported, read as consistent: the two-consents rule under `open:self_admit` (C106), the
  roster version beside the membership events (CC 3.2, CC 4.4.3.4.2), the self-scope row about a
  non-member (self is not a targeted scope), `founder_only` (C403, C410 already cover it).

## Keys not finished

None.
