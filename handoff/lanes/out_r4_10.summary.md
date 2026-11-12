# Fourth reading, share 10: summary

Head 05cbcc8, branch rc19. 425 statements in eight rule keys. 38 findings: 17 major (10 new, 7 known), 21 minor (16 new, 5 known).

## The three numbers

- New major findings, text against text: **1**
- New major findings, text against data: **9**
- Statements opened in the text: **409**; read by gist only: **16**

## Per rule key

| rule key | statements | major new | major known | minor new | minor known |
|---|---|---|---|---|---|
| withdraw | 133 | 5 | 7 | 3 | 1 |
| cosign | 125 | 2 | 1 | 4 | 2 |
| transparency_log | 74 | 1 | 0 | 7 | 0 |
| expiry | 54 | 2 | 0 | 2 | 1 |
| trace | 32 | 0 | 0 | 0 | 0 |
| other:namespace-gate | 3 | 0 | 0 | 0 | 0 |
| other:inventory | 3 | 0 | 0 | 0 | 0 |
| signer_named_by_ref | 1 | 0 | 0 | 0 | 0 |

`trace`, `other:namespace-gate`, `other:inventory` and `signer_named_by_ref` were read in full and gave no finding. The anchor rule of CC 1.13.6 and its restatement in CC 5.3.2 agree (the opt-in receipt plane is plain in one and a conditional MUST in the other, the same behaviour). Whether a named subject may withdraw a trace row is left alone: it is one of the questions held for the steward.

## Major new findings in full

### withdraw · 2.4.1.1,7.5.5 · actor

- A: CC 2.4.1.1: "A node MUST admit a `withdraws` against a target row `T` when one line of this table holds. It MUST refuse any other with `federation_withdraws_not_admitted`."
- B: CC 7.5.5: "the key named in `decided_by` withdraws the `decided` row, admitted because that row names it (the lineage-witness rule, as for the custodian)"
- The admission table has five lines (quorum, signer, a key in subject_key_ids, hash proxy, delegate). A key named in the envelope member decided_by is none of them, so a node built from CC 2.4.1.1 refuses the decider's cancellation that CC 7.5.5 and CC 3.1.5 admit, unless decided_by is also in subject_key_ids, which no section says. The retirement model assumes the CC 7.5.5 reading.

### withdraw · 3.2,3.1.3 · data:exception

- A: CC 3.2: "An owner ends it by a `withdraws` of the acceptance."
- B: data manifests/transitions.tsv: lineage_witness:{stage} attest none admitted founder,owner selfAct true none
- lineage_witness:{stage} has verbs attest only (cc-table) and one transition, attest, with undo false; the CC 8.10 card shows no way back. The text lets the node's owner end witnessing by withdrawing the acceptance, after which that key's cosignatures stop counting. The lifecycle cell of the same family (code-v61) does allow attester or subject to withdraw, so the data also disagrees with itself.

### withdraw · 3.1.3,3.3.4 · data:exception

- A: CC 3.1.3: "A signature row is never withdrawn: a member that has sent its signature cannot recall it"
- B: data manifests/transitions.tsv: cosign:{state} withdraw admitted withdrawn author selfAct
- cosign:{state} has one withdraw transition, role author, no guard on the leaf. The text admits a withdraws of a pending row by its proposer only and refuses one naming a signature row. A kernel executing the transition lets a member recall a sent cosignature. The attest guard is leaf-conditioned; the withdraw is not.

### withdraw · 3.1.3.2 · data:actor

- A: CC 3.1.3.2: "The inviter withdraws a proposal with the ordinary `withdraws`."
- B: data manifests/transitions.tsv: membership:{stage} withdraw admitted withdrawn member cosigned
- membership:{stage} has one withdraw transition, policy cosigned, for every stage. A proposal is a single-signer row its inviter withdraws alone (rule 1); rule 0 reaches only rows carrying additional_scrubs. The lifecycle note says "check_cosigned_withdraws; resignation self" and does not carve out the proposal either.

### withdraw · 2.4,3.1.1 · data:actor

- A: CC 2.4: "so no single signer and no subject can retire a community, un-name a charter or retract a roster event"
- B: data manifests/transitions.tsv: trust:{job}:{version} withdraw admitted withdrawn author,subject selfAct
- trust:{job}:{version} withdraw is selfAct by author or subject for every job. A trust:charter row that carries a scrub set (the keyless family root, the witness quorum the cosign_rule cell names) is a cosigned row, and rule 0 lets only the quorum withdraw it. The data does not separate the cosigned charter from the single-signer confers and accepts edges.

### cosign · 3.1.9.7 · data:actor

- A: CC 3.1.9.7: "A member votes for the Goal by cosigning it, and the row is admitted only when its full scrub set meets the group's protocol at `asserted_at`."
- B: data manifests/transitions.tsv: goal:{scale} attest none admitted registered selfAct
- goal:{scale}, approach:{goal_id}, method:{approach_id}:{substrate_rung} and progress_measure:{method_id} have cosign_rule none and one-signer attest, withdraw and supersede for every row. The text makes a group-declared row (authority_id naming the group) a cosigned row, and says its supersedes, withdraws and recants stand only when cosigned under the same protocol. The data has no arm for the group-declared form, so one member could declare or retire a group's Goal.

### cosign · 4.2.1,6.1.5.1 · data:actor

- A: CC 4.2.1: "**Durable** settings are earned by **quorum, never by having been exercised**."
- B: data manifests/transitions.tsv: mesh_config:{key} attest none admitted steward selfAct
- mesh_config:{key} has cosign_rule none and a one-signer steward attest with no guard on TTL. The text lets one holder set only emergency relief (threshold 1, TTL at most 72 h, not renewable back to back) and gives a durable setting to the root's own quorum. The data does not separate the two, so one steward key could write a durable setting. (C379 is the text side of the same rule.)

### transparency_log · 5.3.3.6,5.3.3.3,8.10 · data:force

- A: CC 5.3.3.6: "MUST equal a `SignedTreeHead.root_hash` actually published for `log_id = "stream:<stream_id>"` ([CC 5.3.3.3](#5.3.3.3)) at `tree_size ≥ K`. A phantom / self-invented root → REJECT."
- B: CC 8.10: "attest: `one transparency_log:inclusion@admitted[val:root_hash=val:chunk_root] else advise` (CC 5.3.3.6)"
- The repair of C358 and C433 removed the refusing clause altogether. The one guard left on delivery_receipt:{stream_id} is the recommended inclusion proof (step 3) and it only advises. Nothing in the data refuses a receipt whose chunk_root is no published head (step 2, a MUST with REJECT), nor one on an accountable stream whose head is not witness-cosigned. A kernel built from the card admits phantom-root receipts.

### expiry · 3.3.1,4.4.3.5.6,4.4.3.5.5 · data:number

- A: CC 4.4.3.5.5: "g.valid_until passed without renewal"
- B: data manifests/reactions.json: "default": "consent_temporary_ttl_secs",
- reactions.json has two expiry entries for consent:state:{stance} leaf granted, both optional on valid_until: one with no default (cites CC 3.3.1, 4.4.3.5.5) and one with default consent_temporary_ttl_secs counted from asserted_at (cites CC 4.4.3.5.6). The text lapses only a grant that carries a valid_until; 14 days is the TEMPORARY bundle's, and constants.tsv says so ("for a temporary grant that states no `valid_until`"). The second entry has no condition naming the temporary stream, so a kernel reading it lapses every undated grant at 14 days.

### expiry · 3.3.4,4.4.3.4.6,3.1.2 · data:condition

- A: CC 3.3.4: "A time-boxed guest is a widening with `valid_until`, and the seat lapses at that instant."
- B: data manifests/reactions.json: "member": "expires_at",
- The only expiry entry for membership:{stage} is the proposal's expires_at; the family_model lifecycle cell reads "expires_at honoured". Nothing in the data lapses a widening at its valid_until, so a time-boxed guest stays seated. The same gap holds for identity:occurrence (CC 4.4.3.4.6 drops an occurrence past valid_until from the self-collective) and for capacity_assurance:reversible_pending (CC 3.1.2: the binding MUST lapse unless resolved within its valid_until): neither has an expiry entry.

## Known conflicts found again

Still present (resolution says to fix, the fault is still there): C429 (entity revocation missing from the never-withdrawn list), C370 (quarantine lifecycle cell and transition still let the subject withdraw), C412 (identity:occurrence withdraw is selfAct), C430 and C367 (retirement withdraw role omits the decider; lifecycle cell still held shut), C386 (build manifest has no supersede), C388 and C365 (watchlist signer), C346 (self:delegates_to has no withdraw), C432 (licensure cosign cell and transitions), C356 (three lists of where expires_at is required).

Found again and settled on reading: C010 (a guardian's withdrawal and a prior cosigned widening), C039 (the fuse phrase in the CC 4.2.6 table), C054 (the accord_data signer names).

Checked and now fixed, so not reported: C265, C345, C378, C415, C427, C428, C434, C435. The repair of C358 and C433 removed the refusing guard on delivery_receipt altogether; that is reported as a new major finding.

## Method notes

- Data quotes from `manifests/transitions.tsv` and `constitution/governance_policy.tsv` are a row's cells in order with each tab written as one space, since the output format allows no tab.
- Every quote was checked by script to occur verbatim in the text or the data file named.
- The accord roster-change window is reported minor, not major: the policy row has window 0, but reactions.json carries the window as a clock on group:roster.

## Read by gist only (16)

The statement had no entry phrase and I did not find its words; the home statement of the same rule was opened in each case.

- withdraw (5): CC 2.1 (a cosigned row is retracted only by a cosigned withdraws); CC 2.6.1.7 (the refusal token row; recantation_reason and what_was_false optional); CC 3.1.3 key_grant row (CC 3.3.2 opened instead); CC 3.2 (location_proof on leaving a geographic community; the informative consent example).
- cosign (6): CC 2.6.1.7 (two statements of the signed-bytes paragraph; cosigned_at); CC 2.6.1.8 (planned quorum form); CC 3.1.3.2 (the widening and removal row); CC 3.2 (promotion to founder; CC 3.1.3.2 opened instead).
- transparency_log (3): CC 2.6.1.8, three planned statements.
- other:namespace-gate (1): CC 2.1, no accountability:* family.
- 5 withdraw + 6 cosign + 3 transparency_log + 1 namespace-gate = 15, plus CC 4.4.3.4.3 delegation row of the layer table (withdraw) = 16.

## Keys not finished

None.
