# Fifth reading, share 10: summary

Head 1ee1bcf, branch rc19. 425 statements in eight rule keys. 44 findings: 22 major (5 new, 17 known), 22 minor (17 new, 5 known).

## The three numbers

- New major findings, text against text: **1**
- New major findings, text against data: **4**
- Statements opened in the text: **424**; read by gist only: **1**

## Per rule key

| rule key | statements | major new | major known | minor new | minor known |
|---|---|---|---|---|---|
| withdraw | 133 | 2 | 8 | 3 | 1 |
| cosign | 125 | 2 | 4 | 5 | 3 |
| transparency_log | 74 | 0 | 2 | 8 | 0 |
| expiry | 54 | 1 | 3 | 1 | 1 |
| trace | 32 | 0 | 0 | 0 | 0 |
| other:namespace-gate | 3 | 0 | 0 | 0 | 0 |
| other:inventory | 3 | 0 | 0 | 0 | 0 |
| signer_named_by_ref | 1 | 0 | 0 | 0 | 0 |

`trace`, `other:namespace-gate`, `other:inventory` and `signer_named_by_ref` were read in full and gave no finding. The anchor rule of CC 1.13.6 and its restatement in CC 5.3.2 agree: the opt-in receipt plane is plain in one and a conditional MUST in the other, which is the same behaviour.

## Major new findings in full

### withdraw · 3.1.1,2.4.1.1,8.10 · data:exception

- A: CC 3.1.1: "Entity revocation (`agent` / `partner` / `license`). Immediate, non-rollbackable."
- B: data manifests/transitions.tsv: "revocation:{entity_type}:{reason} withdraw admitted withdrawn author selfAct"
- The data gives the issuer a withdraw of an entity revocation with attest as its way back (lifecycle withdraws_by {attester}). The text calls the row non-rollbackable, which CC 2.4.1.1 reads as withdrawn by nobody. The data side of C429: once the list is repaired the transition must go, as for key:revocation, which has none.

### withdraw · 2.4.1.1,4.4.3.2.8 · data:exception

- A: CC 2.4.1.1: "An affiliation withdraws no statement about itself, whatever the statement. Its path is reconsideration and the reader's composition."
- B: data formal/derivation/family_default_row.json: ""withdraws_by": "{attester, subject}""
- 155 families take the default lifecycle and a withdraw transition for roles author, subject with no guard typed. Nothing in transitions.json, guard_text.tsv or the lifecycle cells closes the subject arm to a subject that is an affiliation, so a kernel run from the data admits an affiliation's withdrawal of a review, rating or complaint naming it. CC 2.4.1.1 and CC 4.4.3.2.8 agree it never retracts.

### cosign · 3.2,3.1.3,4.2.6 · condition

- A: CC 3.2: "On the base it is the cosigned `group:roster:v1` row, whose cosigners are the version's signers"
- B: CC 4.2.6: "The proposal and the participation each sign a distinct, wire-isolated canonical-bytes domain"
- Text against text. CC 3.2 and the CC 3.1.3 group:roster row make an accord roster version a cosigned row: additional_scrubs over the record's own canonical bytes, reaching the roster-change threshold. CC 4.2.6 has each holder sign an accord_participation preimage (a vote over the proposer's nonce) and says the decision bundle signs nothing. A verifier built from one refuses the roster change the other produces; no sentence says how participations become the version's cosignatures. C051 notes only that the objects are missing from the CC 4.2.1 enumeration.

### cosign · 4.4.3.2.8,4.5.13,8.10 · data:condition

- A: CC 4.4.3.2.8: "an act against a member (`membership:removal`, quarantine, slash, a takedown of the member's content) is admitted only when countersigned by a key outside the deciding seat"
- B: data manifests/family_model.json: "group=affiliations & seats=one => affiliation_member_action@subject_group"
- Text against data. The affiliation_member_action arm exists on membership:{stage} (leaf removal) and nowhere else. quarantine:{state} and slashing:{outcome} have count none and a one-signer attest; takedown_notice:{basis} has a cosigned case for steward_purge only. A kernel run from the data lets the one deciding seat of an affiliation quarantine, slash or take down a member's content alone, where the text leaves such an act a proposal.

### expiry · 2.4.1,4.4.3.2.8,8.10 · data:scope

- A: CC 2.4.1: "on any edge carrying `sub_delegation`, `license`, `grant`, `moderate`, `takedown`, `review` or `slash`, or sitting in an affiliation's `hierarchy`"
- B: data formal/derivation/reaction_text.tsv: "@affiliations expiry required delegation_valid_until default delegation_term_max_secs max charter.role_term from delegation_valid_from"
- Text against data. The one typed expiry on a delegation (reactions.json, trust:{job}:{version}: required delegation_valid_until, bounded by the term ceiling) is scoped to affiliations. CC 2.4.1 and the CC 2.6.1.7 row require the term, at most 365 days, on every edge that carries an issuance or moderation scope in a group of any kind, and refuse a perpetual or over-ceiling one delegation_term_required. The family's subject_rule cell (code-v61) does say a term is required, so the data disagrees with itself; but run from the reactions, a moderate, takedown, license or grant edge in a family or community has no ceiling and no lapse, and the reaction that locks a room when its moderate edge expires never fires there.

## How sure each new major is

- **Accord roster version (text against text).** Sure of the two shapes; less sure nobody intends both. CC 4.2.6 calls its three objects what a roster change rides, and nothing there scrubs the roster record; CC 3.2 and CC 3.1.3 count scrubs over the record. One bridging sentence would settle it either way.
- **Entity revocation withdraw (data).** Follows from C429. If the steward reads non-rollbackable as something weaker than never withdrawn, both this and C429 fall together.
- **An affiliation's withdrawal of a statement about itself (data).** The text is plain in two homes. The data has no guard typed for it; the manifest says an untyped guard is not a claim that the text states none, so this is a missing arm, not a contrary one.
- **One-seat affiliation acting against a member (data).** The arm exists for membership removal only; quarantine, slash and takedown are named in the same sentence of the text and have none.
- **Delegation term outside affiliations (data).** The reactions scope the typed expiry to affiliations; the family's subject_rule cell says a term is required. The lapse and the ceiling are what is missing outside affiliations.

## Known conflicts found again

Still present, the resolution says to fix and the fault is there:

- withdraw: C429 (entity revocation missing from the never-withdrawn list), C370 (quarantine: the text is repaired, the lifecycle cell and transition still admit the subject), C412 (identity:occurrence withdraw is selfAct; the occurrence_revocation carrier's policy cell is selfAct with no user arm), C430 with C367 (retirement withdraw role omits the decider; lifecycle cell held shut), C506 with C494 (membership proposal withdraw is cosigned), C507 (trust charter withdraw is selfAct), C346 (owner-binding guard binds only a withdraw that carries the reference; self:delegates_to has no withdraw), C388 with C365 (watchlist signer), C386 (build manifest has no supersede).
- cosign: C432 (licensure), C508 with C469 (goal and its three companions), C509 (mesh_config durable setting), C488 (accord roster-change window), C173 (CC 3.3.7 prose keeps "both are present").
- transparency_log: C510 with C444 (delivery receipt guard only advises), C448 with C483 (witness signer cell).
- expiry: C512 (no valid_until lapse for a widening, an occurrence, a reversible_pending binding), C436 (CC 2.6.1.7 still lists valid_until as optional everywhere), C450 with C485 (the expired leaf's emitter), C356 (where expires_at is required).

Found again and settled on reading: C039 (the fuse phrase in the CC 4.2.6 table), C054 (the accord_data signer names).

Checked and now repaired, so not reported: C503 (CC 2.4.1.1 now admits the key named in decided_by), C504 (lineage_witness has a withdraw transition), C505 (cosign withdraw has stages, signature empty), C511 (the 14-day default now sits on consent:stream temporary), C500 (no attach clock on trust accepts), C378 (heartbeat expiry is on accord:lifecycle), C411 on the CC 3.1.3.2 side, C265, C345, C281.

## Read and left alone

- A guardian's own withdrawal against a prior cosigned widening (C010, settled).
- CC 3.3.5 rule 4 and CC 2.4.1.1 (C275, no conflict on reading).
- The group:roster attest policy reads selfAct with a guard that every founding member signs; later versions are supersedes under the cosigned policy. Read as the founding record, it agrees with CC 3.1.3.2.
- The policy fractions (1/2 against "more than 1/2") are read under CC 4.5.13 as strictly more.
- Whether a named subject may withdraw a trace row is with the steward.

## Method notes

- Each statement was located by its entry phrase in the text at head 1ee1bcf and read in its paragraph; the 47 statements with no entry phrase were found by search in their sections.
- Every quote was checked by script to occur verbatim in the Part or the data file named. Data quotes from `.tsv` files are a row's cells in order with each tab written as one space.
- Known ids were looked up in `formal/derivation/text_conflicts.tsv` (C001 to C512).
- The minor findings of the fourth reading for this share are not in the conflict table, so those that still hold are marked `new` here.

## Read by gist only (1)

- transparency_log, CC 2.6.1.8 (planned): a row's anchor is its provenance-log position, never a signer-chosen instant. The other two planned statements of that subsection were opened.

## Keys not finished

None.
