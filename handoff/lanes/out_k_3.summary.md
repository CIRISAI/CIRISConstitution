# Lane K, share 3: summary

Read: 399 statements across 10 rule keys (plus 238 `family`-scope rows of the same keys as context). Findings: 33 (13 major, 20 minor; 26 new, 7 known).

| rule key | statements read | family rows (context) | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|---|
| principle | 120 | 1 | 4 | 0 | 0 | 3 | 1 |
| erasure | 70 | 25 | 10 | 7 | 0 | 3 | 0 |
| delegation | 59 | 43 | 4 | 1 | 1 | 2 | 0 |
| steward | 46 | 1 | 3 | 0 | 1 | 1 | 1 |
| cosign | 34 | 91 | 3 | 0 | 1 | 2 | 0 |
| endpoint | 30 | 0 | 2 | 0 | 0 | 2 | 0 |
| census | 21 | 25 | 2 | 0 | 0 | 0 | 2 |
| expiry | 14 | 40 | 3 | 1 | 0 | 2 | 0 |
| legal_hold | 4 | 12 | 2 | 1 | 0 | 1 | 0 |
| other:cell-containment | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

## Major new findings

1. **erasure** (4.5.3,2.4.1.1,7.5.5; condition)
   - A: CC 4.5.3: execute as the same tombstone row — plane, target digest, the authorising `takedown_notice`'s id; never content
   - B: CC 7.5.5: a person's deletion inside the sealed record is the same tombstone by digest on the record's plane, citing the subject's own withdrawal or the order, written by whoever holds custody.
   - The one tombstone row carries an authorising takedown_notice id and CC 2.4.1.1's door refuses a tombstone without the notice (purge_unauthorised); CC 7.5.5 (and CC 4.5.3's own erasure paragraph: 'the ordinary tombstone by digest per plane') has a tombstone authorised by a subject's withdrawal with no notice. One implementer refuses the erasure tombstone, the other writes it.

2. **erasure** (4.5.3,7.5.5; scope)
   - A: CC 4.5.3: A duty-holder's notice is admitted by the [CC 4.5.5](#4.5.5) enforced-admission rule and reaches the bytes plane only.
   - B: CC 7.5.5: a lawful order to destroy sealed material is a `takedown_notice:court_order:v1` executed as the tombstone by digest of [CC 2.4.1.1](part_2_the_grammar.md) with every purge guarantee
   - A court_order notice is a duty-holder basis (immediate-removal, bytes plane only, destroyed on receipt); CC 7.5.5 has it destroy a sealed retirement record (identity record, audit trail, logs: rows on other planes) with 'every purge guarantee', which in CC 4.5.3 belongs to the root-cosigned steward_purge (any plane, 72 h dwell, whole or not at all). Which reach and which dwell a court order has differs by section.

3. **erasure** (4.5.3; instant)
   - A: CC 4.5.3: `CourtOrder` — the operator follows the court's stated timeline.
   - B: CC 4.5.3: An immediate-removal basis has no window: its bytes are destroyed on receipt (item 2).
   - CourtOrder is in the immediate-removal list, so a reachable holder destroys on receipt; the per-basis dispatch gives the same basis the court's own timeline. An order that allows 30 days is destroyed at once under one sentence and on the court's date under the other. The Annex transition (destroy_bytes on admitted) supports destroy on receipt.

4. **erasure** (4.4.3.5.2,3.3.1; condition)
   - A: CC 4.4.3.5.2: if now > deadline and completion is None:
   - B: CC 3.3.1: Breach is therefore: the window passed **and** the row is still present with none of the three composers against it.
   - The watcher of CC 4.4.3.5.2 raises the breach when the producer has emitted no consent:deletion_complete, so the emission alone clears it; CC 3.3.1 D1 says the emission never substitutes and the test is the row's presence. A producer that emits deletion_complete and keeps the row breaches under one and not the other. CC 3.3.1 also says the watcher is cancelled only by withdraws, supersedes or hard deletion; D1 is marked normative.

5. **delegation** (4.5.2.2,2.4.1.1; actor)
   - A: CC 4.5.2.2: `delegates_to(parent_key → student_canonical_hash, scope: [consent_revocation])` for minors
   - B: CC 2.4.1.1: emits `delegates_to(canonical_hash → agent_key, scope: [consent_revocation])` when the proxy is set up.
   - Direction of the proxy edge. Rule 3 (CC 2.4.1.1, CC 2.3.2.2) runs from the subject's canonical hash to the key that will revoke for it; the FERPA row runs from the parent's key to the student's hash, which under rule 3 gives the parent no path to withdraw for the student. CC 2.4.1.1 is the home; the table row is reversed.

6. **erasure** (4.4.3.5.2; data:condition)
   - A: CC 4.4.3.5.2: if now > deadline and completion is None:
   - B: manifests/reactions.json consent:deletion_sla:{days}: the breach reaction at the close of the sla clock is emitted unless the target was withdrawn, superseded or purged; consent:deletion_complete is not among the conditions
   - The data follows CC 3.3.1 D1 (the row's absence), not the CC 4.4.3.5.2 watcher (the producer's deletion_complete). The same data row starts the clock on 'withdrawn of target' and excuses the breach on 'withdrawn of target', so as written a subject's withdrawal both starts and clears the watch; the text's D1 means the producer's own composer.

7. **erasure** (4.5.3; data:instant)
   - A: CC 4.5.3: `CourtOrder` — the operator follows the court's stated timeline.
   - B: manifests/reactions.json takedown_notice:{basis}, leaves NcmecCsam, PerceptualHashCsam, TvecTerrorist, GifctCip, CourtOrder: on admitted, stop_serving and destroy_bytes, force must
   - The data destroys a CourtOrder target at admission with the other immediate bases; the per-basis dispatch gives it the court's timeline. Data agrees with the 'no window, destroyed on receipt' sentence of the same section.

8. **erasure** (2.4.1.1,3.3.2; data:actor)
   - A: CC 2.4.1.1: authorised by a cosigned `takedown_notice` under the trust root's `consensus_protocol` with basis `steward_purge`
   - B: manifests/transitions.json takedown_notice:{basis}: one attest transition for every basis, role takedown, policy selfAct (one voice); no cosigned policy for the steward_purge leaf and no steward_purge row in governance_policy.tsv
   - The text makes a steward_purge notice a row cosigned by the trust root's seats under its protocol; the transition data admits every takedown_notice basis on one signature by a takedown duty-holder. A kernel executing the data admits a one-signer purge notice that the text's door refuses.

9. **legal_hold** (4.4.3.2.8,4.5.3; exception)
   - A: CC 4.4.3.2.8: `hard_case:legal_hold_set` / `:lifted` / `:violation_attempt` make set, lift, and any deletion-during-hold observable (spoliation is liability).
   - B: CC 4.5.3: The exception is an immediate-removal `legal_basis` below, where a reachable holder MUST destroy the bytes on receipt of the notice.
   - Neither section says which wins when a takedown or a steward_purge reaches a record under a legal_hold. CC 4.4.3.2.8 names only the retention schedule and consent-driven descent as overridden and treats any deletion during a hold as a violation attempt; CC 4.5.3 and CC 6.1.2.2 make destruction on receipt total. One implementer destroys held evidence, the other keeps prohibited bytes.

10. **expiry** (3.3.1,4.4.3.5.6; condition)
   - A: CC 3.3.1: `temporary` (14d auto-expire, default)
   - B: CC 4.4.3.5.6: `consent:state:granted` + envelope `valid_until = asserted_at + 14d` + auto-renew dimension on interaction (consumer-policy concern)
   - A temporary grant lapses 14 days after it was granted under CC 3.3.1 and 14 days after the last interaction under CC 4.4.3.5.6, which adds an auto-renew the first does not state; who signs the renewal is not said, and a grant row is the subject's to sign (CC 3.3.1 Emitted by). CC 3.4.13 and CC 3.4.12 forbid auto-renew for their own grants.

## Major known findings (still in the text)

- C002 (delegation; 3.2,3.4.13): One guardian per minor, superseded and never accreted, against a set of N guardians with a quorum M. Still in the text on both sides; CC 3.4.13 Q7's seven rules and the CC 3.2 guardianship clause it cites support the set.
- C197 (steward; 5.3.4,4.2.6): A roster change takes every holder under CC 5.3.4 (fresh genesis) and a strict majority of the standing roster under CC 4.2.6; governance_policy.tsv accord_majority ('every other accord threshold but the fire') follows CC 4.2.6. A lost or refusing holder blocks the change under one and not the other.
- C284 (cosign; 4.4.3.4.2.1,4.5.13): Absolute M of 2 in a roster of 5 against the CC 4.5.13 corridor in which enact is never below a strict majority of the base (side B as recorded in C284; not re-quoted here). Still in the text; whether the declared protocol or the policy row decides a cosigned admission is the open question of C283.

## Notes on method and limits

- Every quote in the TSV was checked by script to be a verbatim substring of today's Part text and at most 30 words. Data sides (three `data:` rows) describe the data row and are not quotes.
- Known conflicts that the text no longer shows were not reported (C061: CC 6.1.2.2 now lists five immediate-removal bases; C060 and C062: CC 4.5.3 item 2 now reads 'stop serving' and 'receipt of the notice'; C067: CC 4.5.5 now says four duties).
- For C284 side B is given without a quote: the CC 4.5.13 corridor sentence was taken from the conflict table and not re-located in the text.
- `principle` (120 statements) is a broad key of mostly single-statement rules in Parts 1 and 7; it was read whole and gave four minor findings. The PDMA, Veto, constraints-not-weights and lethal-action statements agree with one another.
- Data comparison was done for the takedown, deletion-SLA, consent-term, delegation-term, hop-cap, accord-threshold and census-floor rules (reactions.json, transitions.json, governance_policy.tsv, constants.tsv, signed_object.tsv). The 238 family-scope rows were read as context and not each compared cell by cell with family_model.json.
- Statements whose `entry_phrase` was absent from rule_entries.tsv (about 50, mostly CC 2.4.1.1, CC 2.6.1.7 table rows and CC 4.4.3.8) were read from their section by gist; the CC 2.6.1.7 and CC 2.6.1.8 rows were checked against signed_object.tsv only.

## Keys not finished

None. All ten keys were read; `other:cell-containment` has one statement and nothing to compare it with.
