# Draft addition to CIRISPersist#1259 (not posted; for Eric to read first)

Questions from the rc19 data pass. Each is a point where the Constitution text and the census of the
pinned release differ, or where the text names a rule and no token. Nothing here asks for a change before
you say which side is right; where the build is right the text will record it as a departure with a reason.

## Where the text and the census cell differ

1. `key_grant:{axis}` supersede. CC 3.3.2 and CC 5.1: no row supersedes or withdraws a wrap; a rotation is a
   new row. Census cell: `supersedes=same_attester`. Which does the door do?
2. `key_grant:{axis}` and `group:roster` rotation on removal. CC 4.4.3.4.5 and CC 4.5.12.1: at self and
   family scope nothing is rotated, the store stops wrapping; epoch and stream axes rotate. Census cell:
   yes for the whole family.
3. `revocation:{entity_type}:{reason}` erasure. CC 4.5.3 gives every kept-list row a producer-executed route.
   Census cell: none (unpurgeable, migration.rs:606).
4. `revocation:{entity_type}:{reason}` rollback. CC 3.1.1: non-rollbackable. Census cell admits the
   attester's withdrawal.
5. `licensure:{authority_id}` retraction class. CC 2.4.1.1 lists a licence as an act of a body. Census cell:
   `retraction_class=peer`.
6. `membership:{stage}` proposal. CC 3.1.3.2: the inviter withdraws a proposal alone. Census cell: a cosigned
   withdrawal for the whole family.
7. `identity:occurrence` eviction. CC 3.3.6.3: an eviction lands only by the two self-roster paths. Census
   cell: the attester or the subject withdraws alone.
8. `consent:state:{stance}` and `key_grant:{axis}` audience. CC 2.6.1.7 and CC 3.3.2 against the cells'
   audience (`for_key_id` as an added recipient; `addressee` against the content scope's audience).
9. Default `subject_rule.in_audience`. CC 4.4.3.4.7: at a targeted scope every key in `subject_key_ids` is
   within the row's audience. Census default: no.
10. Two door-token lists. `identity_amendment` lists five tokens where CC 3.1.5 names
    `identity_amendment_unauthorized`; `trace:{form}:{version}` lists `run_kind`, which reads as a clipped
    `trace_run_kind_mock`.

## Rules the text states with no refusal token

The guard table carries 32 refusals with no name, and five folds refuse by a name the text does not give
(`roster_change_below_majority`, `witness_quorum_invalid`, `evidence_score_mismatch`,
`aggregation_meta_mismatch`, `locality_mismatch`). A refusal token is on the wire, so the names are yours
to give or confirm. The list with the nearest existing token for each is `handoff/lanes/out_g_guard.md`,
section "The 39 first-pass rows that refused with no token".

## Carried from earlier in the thread, still open

- The refusal token for a future-dated row.
- Whether an un-announce withdraws the federation row.
- Whether the steward fold reads an occurrence anchor.
- Chain-row freshness W against the signer's standing.

## One-emitter rule (CC 4.5.13, landed 8aec89d)

A row a clock or a fold causes is emitted by the door the causing row first entered; peers re-derive and
emit nothing. Seven such emits are written in the text as the store's or the author's
(`manifests/reactions.json`, `_meta.one_emitter.not_yet_by_origin_door`). Does the store today emit
`consent:state:expired`, `hard_case:deletion_window_breach` and `hard_case:recipient_excluded` on every
node that sees the condition, or on one?
