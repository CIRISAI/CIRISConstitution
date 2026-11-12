# Third reading, share 6: summary

Read-only lane, rc19 at 87c1730. 425 statements over seven rule keys, family-scope rows taken as full members. 51 findings: 23 major (17 new, 6 known), 28 minor (24 new, 4 known).

## Per rule key

| rule key | statements | major new | major known | minor new | minor known |
|---|---|---|---|---|---|
| `moderation` | 153 | 9 | 2 | 11 | 2 |
| `delegation` | 102 | 3 | 1 | 3 | 0 |
| `reserved_prefix` | 76 | 3 | 1 | 3 | 1 |
| `policy_row` | 55 | 2 | 1 | 3 | 0 |
| `accord` | 36 | 0 | 1 | 3 | 1 |
| `other:list-of-record` | 2 | 0 | 0 | 1 | 0 |
| `replication` | 1 | 0 | 0 | 0 | 0 |

`replication` has one statement (the `cosign:{state}` pending row, CC 3.1.3) and no finding: the reactions entries for the hold agree with it.

## How far the reading went

- Read in full, today's text: CC 4.2 to 4.2.6, 4.3, 4.1.1, 4.4.3.4.3, 4.5.3, 4.5.4, 4.5.5, 4.5.7, 4.5.13, 3.3.2 (takedown half), 3.4 to 3.4.11 (lead of 3.4.11), 6.1.5.1, and the registry rows of CC 3.1.9.2 and 3.1.9.4 that carry these keys.
- Read from the inventory's gist and entry phrase only, with the surrounding section not re-read: the statements in CC 3.4.12, 3.4.13, 3.4.14, 3.3.1, 3.4.7.3, 2.4.1.2.1, 3.3.8 to 3.3.12, 5.3.x and most of CC 3.2. A conflict that turns on words outside the entry phrase in those sections can have been missed.
- Data: constitution/governance_policy.tsv and manifests/governance_policy.json (every row), manifests/reactions.json (every entry), constants.tsv (the rows these keys name), the CC 8.10 cards of about twenty families (the moderation, takedown, ballot, accord, trust, deferral, membership, roster, objection, age and detection families). manifests/transitions.json was opened for five families only. The code-v61 cells of family_model.json were not compared cell by cell; a difference there that family_departures.tsv already records was not reported.
- Every quote was checked by script to be a verbatim substring of the Parts or of the data file named, at most 30 words, inside one table cell.

## Known items checked against today's text

- C302 (court order in CC 7.5.5): fixed. CC 7.5.5 and the `lawful_order:release` row now say a duty-holder's notice reaching the bytes plane only.
- C345 (rule-3 proxy sentence in CC 2.4.1.1): the quoted sentence is gone from Part 2; not re-read further.
- C324 (self-assertable reserved role): fixed at CC 3.4.7.1; the per-family emitter rules still state set membership alone (reported, minor).
- C321 (CC 4.5.8.4 cohabitation line): the quoted line is gone.
- C067, C094: fixed (four duties; `slash` row in CC 4.4.3.4.3). C068: partly; the duty-holder table has no slash row and `slashing:{outcome}` attest still reads `registered` (reported).
- C203: fixed in CC 4.5.4 enforcement (ii).
- C307: the takedown card now counts the steward_purge leaf as a cosigned act; its attest row still reads role `takedown`, policy selfAct for every basis. Not reported again.
- C298, C288, C283, C051, C002, C137: still there (reported with their ids).

## Major new findings

### 1. `moderation` (actor), CC 4.5.7,3.1.9.4

- A: CC 4.5.7 a [CC 4.5.5](#4.5.5) `moderate`-scope holder **optionally** enables a watchlist (`watchlist:{id}`, [CC 3.1.9.4](part_3_the_namespace.md)) for a group they moderate
- B: CC 4.5.7 A watchlist is enabled per-group by its `moderate`/`takedown` authority
- One sentence lets only a moderate holder enable a watchlist; the next (and the CC 3.1.9.4 row: "signed by the CC 4.5.5 `moderate`/`takedown` authority") also lets a takedown-only holder. The separation-of-powers table in CC 4.5.7 says `moderate`-holder.

### 2. `moderation` (data:actor), CC 4.5.7,8.10

- A: CC 4.5.7 Enable/disable is **signed by the authority and revocable** (`withdraws`).
- B: manifests/transitions.tsv, row watchlist:{id} attest, roles cell: registered
- The card (and manifests/transitions.json, family_model signer_rule any_registered) lets any registered key sign a watchlist row; the text limits enabling to the group's moderate (or takedown) duty holder. CC 8.10 says the card is the statement of the value. The text is the side the rest supports.

### 3. `moderation` (number), CC 3.3.2,4.5.3

- A: CC 3.3.2 Expeditious-with-counter-notice (operator-set window)
- B: CC 4.5.3 The windows are `Dmca512` 10 days, `DsaArticle16` 14 days, `OsaIllegalContent` 14 days and `CommunityStandards` 30 days.
- The CommunityStandards withhold window is the operator's to set in the CC 3.3.2 table and a fixed 30 days in CC 4.5.3; constants.tsv (withhold_window_community_standards) sides with CC 4.5.3. The window decides when held bytes are hard-deleted. Same family as C171 (Dmca512), which did not cover this row.

### 4. `moderation` (condition), CC 4.5.13

- A: CC 4.5.13 Content survives **only** by an affirmative, on-record **keep-decision**
- B: CC 4.5.13 When the live-majority vote **favors removal/moderation but the content is retained** (flagged, not hard-removed), it is **auto-hidden behind an active interstitial**.
- The protective default gives two outcomes for a report raised in the room (removed unless a keep lands). The infohazard gate and the ladder give a third, "flagged-but-retained", when the majority favours removal, and nothing says when a vote for removal retains the bytes behind the interstitial and when it removes them. One reader destroys, the other keeps consent-gated.

### 5. `moderation` (data:condition), CC 4.5.13,4.5.5,8.10

- A: CC 4.5.13 A **report filed privately with the duty holder** (the named moderator, or the steward) opens no window and is seen by nobody but the duty holder.
- B: CC 8.10 card moderation:{allegation_type}: [harm_report] on close(window) unless fold(keep_decided): read withdrawn (CC 4.5.13)
- CC 4.5.5 says a harm report filed with the moderator is the `moderation:{allegation_type}` row under the moderate duty, and CC 4.5.13 says that report opens no window; the action raised in the room is "a report→`scores` Contribution". manifests/reactions.json hangs the 48 h default-removal clock on the moderation:harm_report leaf, the duty holder's record, and none on the room's scores proposal. Text side of this is C137; the data is not in the table.

### 6. `moderation` (data:number), CC 4.5.13,8.10

- A: CC 4.5.13 the proposal is tallied by **live-majority vote over the community's live members**
- B: constitution/governance_policy.tsv, row moderation_action, floor cell: 1/2
- The text asks a majority of those who show up ("A silent member is not in the denominator"; "a vote-to-keep that carries its majority"). The row gives floor 1/2, which the table defines as "at least the fraction", over base `active` (the standing roster up to 12): governance_policy_vectors.json lands it on 1 voice at base 2. Exactly half, counted over the roster, is not a majority of the present. The family model fold says over=present; the policy row says base active.

### 7. `moderation` (actor), CC 3.4.11,4.5.13

- A: CC 3.4.11 a `moderation:{allegation_type}` ModerationEvent ([CC 3.1.9.2](part_3_the_namespace.md)) adjudicated by quorum under the `moderate` delegated duty
- B: CC 4.5.13 **This document imposes no quorum *on* a moderator or a steward; a community MAY impose one on itself (below).**
- CC 3.4.11 has an age misdeclaration adjudicated by a quorum under the moderate duty. CC 4.5.13 and the card (moderation:{allegation_type} attest, selfAct, cosign none) have a moderator resolve by one signature unless the community chose a moderator quorum. One reader refuses a single-signed misdeclaration event; the other admits it.

### 8. `moderation` (data:condition), CC 3.1.1,4.5.5,8.10

- A: CC 4.5.5 A's authority set ([CC 2.4.1.2.1](part_2_the_grammar.md)) plus any holder of a `review`-scoped chain from that set
- B: CC 8.10 card reconsideration:{grounds}: attest: `one takedown_notice:{basis}@admitted[id=ref:*] else refuse` (CC 3.1.1)
- The text lets a reconsideration target any prior action: a takedown, a moderation event, a licence, a slashing. The guard in transitions.json (reach whole, sourced from the CC 3.1.1 takedown row) refuses every reconsideration that does not name an admitted takedown_notice, so a contest of a licence or of a moderator's record is refused at the door. The text is the side the rest supports.

### 9. `moderation` (actor), CC 4.5.7,4.4.3.4.3,4.5.3

- A: CC 4.5.7 The fabric auto-fires the matcher at the **publish/share seam** and auto-fires the action: CSAM → `takedown_notice{PerceptualHashCsam}`
- B: CC 4.4.3.4.3 a key whose `identity_type` contains `node` may carry *only* `infra:*` scopes, therefore it cannot hold a judgment duty at all
- The fabric (the node) fires the takedown notice and the `moderation:*` event on a match. CC 4.5.3 admits a notice only from a key that holds the `takedown` duty ("never the duty-holder gate") and CC 4.4.3.4.3 bars a node key from every judgment duty. CC 4.5.5 says the notice fires "under an *enabling authority*" and no statement says whose key signs it. One reader has the node sign and refuses it at the gate; another admits it.

### 10. `delegation` (condition), CC 4.5.5,4.3

- A: CC 4.5.5 A `delegates_to` MAY permit its delegate to **deputize** (further-delegate the duty), but **only if the delegator granted it**.
- B: CC 4.3 A seated Wise Authority may delegate the answering to an agent by a further `delegates_to` of the same or a narrower scope
- CC 4.5.5 lets a delegate hand a duty on only where the grant carries `sub_delegation`. CC 4.3 calls `resolve_deferral` "a duty with the enforced admission of CC 4.4.3.4.3" and lets the seated person hand the answering to an agent with no such condition; its admission clause asks only for "a live chain from the conferrer bearing `resolve_deferral`". An agent's answer under a seat granted without `sub_delegation` is admitted by one reading and refused by the other.

### 11. `delegation` (number), CC 4.5.5,4.4.3.2.8,4.1.1

- A: CC 4.5.5 depth ≤ 5 ([CC 4.1.1](part_4_composition_governance.md)), and **no edge is `withdraws`-revoked**
- B: CC 4.4.3.2.8 a **configurable depth cap** (> the [CC 4.1.1](part_4_composition_governance.md) default-5 for deep secretariats)
- The enforced-admission test fixes the chain at five edges ("The chain is depth-capped at 5"). CC 4.1.1 makes five a consumer default, "(configurable)", and CC 4.4.3.2.8 lets an affiliation's hierarchy set a cap above five. A duty act signed six edges down an affiliation is refused by CC 4.5.5 and admitted by CC 4.4.3.2.8; CC 4.4.3.4.3 says only "depth-capped per CC 4.1.1".

### 12. `delegation` (data:condition), CC 4.3,8.10

- A: CC 4.3 Where the seat requires a licence the attester does not hold, it is refused `deferral_response_unlicensed`.
- B: CC 8.10 card deferral:response:{outcome}: attest: `one licensure:{authority_id}@admitted[attested=signer] at asserted_at else refuse(deferral_response_unlicensed)` (CC 4.3)
- In the text a licence is asked only where the seat row names a licensing authority ("A seat in a domain may require a licence"). The guard in manifests/transitions.json has no condition, so every deferral response from a signer with no licence is refused. The card also names the signers `steward, wa`; CC 4.3 admits the conferrer or any key on a live chain from it, an agent handed the answering included.

### 13. `reserved_prefix` (actor), CC 3.4.10,3.4.11

- A: CC 3.4.10 it is the emitter role for `transparency_log:cosigned:*`, the log-checkpoint cosignature, and for nothing else in this section
- B: CC 3.4.11 Emitter rule: `witness ∈ attesting_key.identity_type` ([CC 3.4.7.1](#3.4.7.1) set membership).
- CC 3.4.10 says the `witness` identity_type emits only log cosignatures, that the witness of `age_assurance:*` is a different thing ("Being a registered provider, authority or assessor"), and that a substrate MUST NOT accept one where another is required. CC 3.4.11 and CC 3.4.12 gate both ladders on that same identity_type. Under CC 3.4.11 a log witness may attest a person adult; under CC 3.4.10 it may not. The family model has a third rule: a delegated `infra:attest_assurance` scope.

### 14. `reserved_prefix` (actor), CC 3.4.8,4.5.7,4.4.3.5.2

- A: CC 3.4.8 **any** row whose `dimension` is under `detection:*` **is** a primary detector emission and MUST satisfy `lenscore_detector ∈ attesting_key.identity_type`
- B: CC 4.5.7 other → `detection:*` + a `moderation:*` ModerationEvent to the named moderator
- CC 3.4.8 reserves the whole `detection:` stem to a key holding `lenscore_detector`. CC 4.5.7 has the fabric emit `detection:*` on a watchlist match and CC 4.4.3.5.2 has "a detector library" compose `detection:consent:repeat_sla_breach`; neither names the role. CC 3.1.7 also refuses any leaf under a reserved stem that no row claims, and neither leaf is registered (CC 3.1.8 closes `detection:{detector}` to three). The first sentence of CC 3.4.8 names two sub-families only.

### 15. `reserved_prefix` (actor), CC 3.4.3,3.4.7.1

- A: CC 3.4.3 cross-attested by all stewards in the steward-triple
- B: CC 3.4.7.1 every reserved role but `accord_holder` is conferred by a live `delegates_to`, resolved at use against a root the evaluating node trusts
- For `system:*`, CC 3.4.3 asks that the substrate key be cross-attested by all three stewards, which is a unanimous act on the key record. CC 3.4.1 and CC 3.4.7.1 confer "the substrate families" by one live delegation under any root. A node of another root, or one with two of three attestations, emits `system:*` under one reading and is refused under the other. "The steward-triple" is also a fixed three where CC 4.2.1.1 says three is the seed.

### 16. `policy_row` (condition), CC 3.1.3,4.5.13

- A: CC 3.1.3 the election id (digest of community id, roster head and last seating)
- B: CC 4.5.13 Its id is the digest of the community id and of the last seating row or, for a room never yet seated, the genesis of the roster.
- The ballot row of CC 3.1.3 puts the roster head into the election id. CC 4.5.13 leaves it out on purpose: "A member leaving while the room is locked therefore changes nothing about the election". With the head in the id a resignation during the lock makes a new id, and "a ballot naming an unknown election id ... is refused", so the ballots already cast fall under another election and two nodes seat differently.

### 17. `policy_row` (exception), CC 3.2,4.5.13,4.4.3.2.6

- A: CC 3.2 `founder_only` is refused for every community above the family, not only infrastructure
- B: CC 4.4.3.2.6 producer_gated → consensus_protocol = "founder_only" with the
- CC 3.2 refuses `founder_only` on every community and types the field as "the family's kinds less founder_only". CC 4.5.13 excepts "a publication's subscriber list and a room's own listing", and CC 4.4.3.2.6 says a subscriber set "IS a `community` Contribution" under `founder_only`. A producer-gated subscriber community is refused by CC 3.2 and admitted by the other two. CC 4.5.4 also speaks of a community that "moves from `founder_only`".

## Keys not finished

None left unread. The limits are those under "How far the reading went".
