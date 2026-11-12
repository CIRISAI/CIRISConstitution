# Third reading, share 10: summary

Read at head 87c1730 (branch rc19). 425 inventory statements over 8 rule keys, `family` rows read as full members. Compared with `manifests/transitions.json`, `manifests/family_model.json`, `manifests/reactions.json`, `constitution/governance_policy.tsv`, `constitution/consensus_protocols.tsv`, `constitution/constants.tsv`, `manifests/signed_object.cddl` and the CC 8.10 cards. Conflict table checked through C346.

| rule key | statements | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| withdraw | 133 | 10 | 4 | 0 | 5 | 1 |
| cosign | 125 | 6 | 2 | 0 | 3 | 1 |
| transparency_log | 74 | 5 | 1 | 0 | 4 | 0 |
| expiry | 54 | 5 | 2 | 0 | 2 | 1 |
| trace | 32 | 0 | 0 | 0 | 0 | 0 |
| other:namespace-gate | 3 | 0 | 0 | 0 | 0 | 0 |
| other:inventory | 3 | 0 | 0 | 0 | 0 | 0 |
| signer_named_by_ref | 1 | 0 | 0 | 0 | 0 | 0 |
| total | 425 | 26 | 9 | 0 | 14 | 3 |

## Major new findings

1. **withdraw: the consent fold is stated two ways (CC 3.3.1 against CC 4.4.3.5.5).** CC 3.3.1 says `consent:state:*` rows use the boundary fold: the latest admitted revocation puts every grant at or before it out, whichever row it named. The read path of CC 4.4.3.5.5 drops only the grant a withdrawal or a revoke names, so an older unnamed grant resolves to `granted`. Withdrawing the newest grant resurrects an older one under 4.4.3.5.5 and never under 3.3.1. The pinned consent model follows 3.3.1.
2. **withdraw: the agent key's revocation of `consent:community_trust` (CC 3.3.1, one cell).** The cell names three parties, lets each withdraw, and says the agent key's withdrawal is folded as a boundary. Its closing rule folds a grant or revocation only from the node or its owner. Capture stops on the agent key's withdrawal under one sentence and not the other.
3. **withdraw: is an entity revocation ever withdrawn (CC 3.1.1 against CC 2.4.1.1 and the data).** CC 3.1.1 calls `revocation:{entity_type}:{reason}` non-rollbackable, and CC 2.4.1.1 cites that cell as the reason a `key:revocation` is never withdrawn. The never-withdrawn list omits the entity revocation, rule 1 admits its signer's `withdraws`, and the family model, the transitions table and the card give withdraw to the attester.
4. **withdraw (data): a planned retirement cannot be cancelled in the data.** CC 3.1.5 and CC 7.5.5 cancel a planned retirement by a `withdraws` of the `decided` row while no `frozen` row exists. `retirement:{state}` has only `attest` in transitions.json, lifecycle "none (held shut)" in the family model, and "way back: none" on its CC 8.10 card.
5. **cosign: the instant a cosigned roster event is judged at (CC 2.4 and CC 3.3.4 against CC 4.4.3.4.2).** The home judges signatures on the fold at the event's signed instant, a departed signer counting inside W. The gate pseudo-code of CC 4.4.3.4.2 resolves the roster at `now`. A signer who left between signing and receipt counts under one and not the other.
6. **cosign (data): an organisation's licence is single-signer in the data.** CC 2.4.1.2.1 and CC 3.3.9 make `licensure:{community_key_id}` a cosigned row under the affiliation's protocol. The family model has `cosign_rule` "none", and the transitions table and card admit any registered signer under `selfAct` and let the author withdraw alone.
7. **transparency_log (data): the delivery-receipt guard asks a witness cosign of every stream.** CC 5.3.3.6 asks a witness-cosigned root only of an accountable stream, and CC 5.3.3.3 makes witness cosign optional for best-effort media. The guard on `delivery_receipt:{stream_id}` refuses any receipt with no admitted `transparency_log:cosigned` row.
8. **expiry: which member lapses a consent grant (CC 3.3.1, two cells).** One cell lapses a grant when `valid_until` passes; another has the substrate emit `consent:state:expired` on `expires_at` or a `retain:<window>` in the scope. CC 2.1 holds the two members independent.
9. **expiry (data): the heartbeat's expiry sits on the halt's lifecycle rows.** reactions.json and the card require `valid_until` (at most 90 days, then stale) on `accord:lifecycle:{kind}`, which is `confirmed` and `active`. CC 3.4.1 gives that cadence to the heartbeat `accord:lifecycle:v1`, and CC 4.2.1.3 gives a confirmed halt no TTL. The stale name in CC 3.2 T4 ("refresh cadence of `accord:lifecycle:active`") is the likely source.

## Known conflicts checked for repair

- Fixed in the text since the table was written: C021 (CC 2.1 `witnesses`), C109 (unanimous removal in the gate pseudo-code), C170 (the N=1 `key_grant` row), C173 (both present and live), C189 (dissolution needs no signer), C281 (the `withdraws` cell of CC 2.4.1), C304 and C305 (the watcher pseudo-code).
- Stale wording still there, reported with the id: C010 (CC 3.4.13 guardian's withdrawal un-counts a cosignature), C039 (CC 4.2.6 "within halt_fuse_secs of the halt"), C040 (CC 5.3.4 "the charter's quorum:2/3").

## Keys not finished

None. Limits of the reading: for `withdraw` and `cosign` every statement's gist was read and the home sections (CC 2.4, 2.4.1.1, 3.3.4, 4.4.3.4.2, 4.2.6) were read whole; other statements were opened in the text only where the gist suggested a difference from the home. The `organization` and `org_membership` merge row of CC 5.3.2.3 and the guardian rules of CC 3.4.13 were not compared with the data.
