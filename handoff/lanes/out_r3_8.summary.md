# Third reading, share 8: summary

Repository at 87c1730 (branch rc19), read-only. 425 inventory statements across 8 rule keys, `family` scope rows
taken as full members. Compared with the conflict table (C001 to C346), `manifests/reactions.json`,
`constitution/governance_policy.tsv`, `constitution/constants.tsv` and the family cards of CC 8.10.

## Per rule key

| rule key | statements | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| admission_order | 141 | 9 | 3 | 2 (C156, C188) | 4 | 0 |
| conformance | 113 | 1 | 0 | 0 | 1 | 0 |
| amendment | 79 | 4 | 0 | 0 | 3 | 1 (C089) |
| licensure | 54 | 4 | 1 | 0 | 2 | 1 (C218) |
| endpoint | 30 | 1 | 0 | 0 | 1 | 0 |
| other:client | 6 | 1 | 0 | 0 | 1 | 0 |
| other:public-transparency | 1 | 0 | 0 | 0 | 0 | 0 |
| other:local-act | 1 | 0 | 0 | 0 | 0 | 0 |
| **total** | **425** | **20** | **4** | **2** | **12** | **2** |

## Major new findings in full

1. **A community change short of signatures: refused, or held** (admission_order; CC 4.4.3.2.3 against CC 4.4.3.4.2
   and CC 3.3.4). The community pseudo-code emits `hard_case:community_consensus_protocol_violation:{C}` and rejects
   as soon as `signatures_ok` is false. The family pseudo-code says "short by signatures alone: held, never refused
   (CC 3.3.4)", and CC 3.1.3 calls the hold general to any cosigned row. One implementer refuses a community
   widening or removal that arrives one signature short and records a violation; the other holds it for the 72 h
   window. CC 3.3.4, CC 3.1.3 and the `cosigned_act` policy row support the hold; the community pseudo-code lacks
   the arm.

2. **A geographic community finer than resolution 7** (admission_order; CC 2.6.6.3 against CC 4.4.3.2.3).
   CC 2.6.6.3 and the CC 3.2 district row: "such a community admits by invitation and the constraint describes it
   rather than gates it". `evaluate_subkind_admission` returns false for every new member of any geographic
   community whose proof is not contained in the constraint, with no finer-than-7 arm, so under the pseudo-code such
   a community admits nobody. Part 2 and CC 3.2 support the invitation reading.

3. **A founder nobody appointed** (admission_order; CC 4.5.4 against CC 4.5.13 and a later paragraph of CC 4.5.4).
   `authority_set(C)` is "a founder, or a key the community's `consensus_protocol` authorizes", and CC 4.5.4 says
   "Belonging to the set holds no duty, so a member who has not been appointed moderates nothing." CC 4.5.13 says
   "A founder holds the duty at zero hops and no row confers it". The first reading refuses a founder's moderation
   act and locks the room for an election while a founder is live; the second admits the act and never locks.
   CC 4.5.13 ("A founder is never locked out") supports zero hops; the authority-set sentence lacks the exception.

4. **Which write of a licence is current** (licensure; CC 3.3.9 against CC 5.3.2.3). CC 3.3.9: "latest
   `asserted_at`, tie-break smallest `attestation_id`". CC 5.3.2.3: "`quorum_weight` → signed timestamp → content
   hash", the more restrictive state winning. For two writes of one revision, a later `active` signed by fewer
   members wins under the first and loses to an earlier `suspended` under the second, so two nodes disagree on
   whether a person is licensed. The CC 8.10 card for `licensure:{authority_id}` carries both picks, so the data
   does not decide.

## Known conflicts whose stale wording is still in the text

- **C156** (the `active_count` part, which its resolution calls "C156b"; no row with that id exists). CC 3.1.3 and
  the first sentence of CC 6.1.9 give the raw count; CC 2.6.1.7 and the card give the count after the ratchet.
  Members refuse a row that differs from their own recomputation, so this is reported as major.
- **C188**. The gate is still named `consent:scope:analyze` in prose at CC 3.3.7, CC 3.1.4 and CC 3.1.8.1 and in the
  CC 3.4.5 table row, although the resolution says the prose use is repaired.
- **C089** (held as the steward's wording): unchanged in CC 4.5.1.
- **C218**: fixed in CC 2.4.1.2.1; the same unqualified "by quorum" remains in the `license` row of the
  CC 4.4.3.4.3 scope table.

## Known conflicts checked and found fixed (not reported as rows)

- C040 at the endpoint: CC 5.3.4 now reads "Returns the named holders" (the "three" remains in CC 4.2.3 only).
- C092: "These three kinds carry enforced admission" is gone from CC 4.4.3.4.3.
- C219: "a single key MUST NOT be able to issue one" is gone from CC 3.3.9.
- C313: CC 8.8.3 D-1 now names RM ≥ 4 as the one trigger.

## Data notes

- `mesh_config:{key}`: the data carries the 72 h ceiling and the narrow-only fold, and nothing for "not renewable
  back-to-back by the same holder"; the card's signer is "steward" where the text says the trust root (row in the
  TSV, minor).
- `licensure:{authority_id}` card: two `pick` rules on `license_id` and both `result=set` and `pick=rank(...)`
  (carried in the notes of the licensure rows).
- `deferral:response:{outcome}` card: the guard carries `deferral_response_unlicensed` only; the
  `deferral_response_unseated` refusal of CC 4.3 and CC 3.1.9.3 has no guard and rests on the signer role
  (`steward, wa`). Not reported as a row: I could not tell from the card grammar whether the role cell covers it.
- `governance_policy.tsv` rows `moderator_election`, `cosigned_act`, `accord_majority` and the constants
  `mesh_config_emergency_ttl_secs`, `session_claim_max_secs` agree with the statements read.

## Coverage and limits

All eight keys were taken. `admission_order`, `conformance` and `amendment` are broad keys whose statements fall
into many unrelated topics; within each I compared the statements topic by topic (key-claim order, trust-root
head gate, community and family admission, cosign hold, census, ballots, licence and deferral, mesh config, key
separation, capacity gate, dominance gate; scale gate and entrenchment, versioning, witnessed mode, prefix gate;
trust-root floor, profiles, unknown fields, seat opt-out, node and actor roles). Topics with a single statement
were read against their section only. Not chased to the end:

- admission_order: the owner-binding rules of CC 3.2 for a user target (minor ward, adjudicated incapacity). The
  inventory gists for these have no entry phrase and I did not find today's wording of the "admitted only if the
  target is a minor user" statement; the incapacity and minors conflicts are already in the table.
- admission_order: the A/V binding and relay order of CC 5.3.3.2.3 and the dialler order of CC 5.3.3.5 (three and
  one statements, no entry phrase) were not compared with their vectors.
- conformance: the stewardship statements of CC 4.5.1.1 (axis classification) were read for internal agreement
  only, not against the generated matrix.
