# Third reading, share 5: summary

Statements read: 425 over 7 rule keys (family-scope rows taken as full members). Findings: 32.

| rule key | statements | major new | major known | minor new | minor known |
|---|---|---|---|---|---|
| audience | 178 | 5 | 1 | 3 | 0 |
| supersede | 100 | 2 | 2 | 3 | 2 |
| agent_identity | 65 | 0 | 2 | 5 | 0 |
| placement | 52 | 0 | 1 | 5 | 0 |
| other:family-registration | 19 | 0 | 1 | 0 | 0 |
| projection | 10 | 0 | 0 | 0 | 0 |
| other:cell-containment | 1 | 0 | 0 | 0 | 0 |
| total | 425 | 7 | 7 | 16 | 2 |

## Major new findings

### audience: 4.4.3.2.7,6.1.5.3,5.2 (condition)

- Side A. CC 4.4.3.2.7: "if the member's local substrate chose to re-emit the community content at `cohort_scope: self` for cross-device sync; otherwise community content stays at the cohort_scope: community visibility on each device"
- Side B. CC 6.1.5.3: "A node is set up as **personal** by default, and a personal node's allow list is all of its owner's cohorts."
- Whether a member's other devices receive community content: CC 4.4.3.2.7 makes it depend on a local re-emit at self scope; CC 5.2 and CC 6.1.5.3 put every claimed node of a member in the audience, by pull anti-entropy and under the allow list, with no re-emit. The rest of the text supports side B.

### audience: 4.4.3.4.3,6.1.5.3,3.3.7,3.3.4,3.3.6 (scope)

- Side A. CC 4.4.3.4.3: "every `cohort_scope: self` Contribution's DEK wraps to both, so **the app and the agent decrypt the same Self content**"
- Side B. CC 6.1.5.3: "With no `cohorts` member a personal node receives every cohort its owner is in and a server node receives no `self` or `family` content."
- Does an agent occurrence, or a home server, receive its owner's self content. CC 6.1.5.3 puts `agent` and `server` in the server class, and CC 3.3.7 says `self` is never listed, so no grant can add it. CC 4.4.3.4.3, the CC 3.3.4 worked example (alice_agent_key, alice_homeserver_key) and CC 3.3.6 deliver self content to those occurrences. Nothing decides between them.

### audience: 3.1.1,3.2,4.4.3.2.8 (scope)

- Side A. CC 3.1.1: "a federation-scoped `scores` row by the founder carrying the room's name, description, `cohort_subkind`, admission policy, named moderator and `community_key_id`"
- Side B. CC 4.4.3.2.8: "An affiliation that is not public carries a federation-scope listing row (`community:listing:v1`, [CC 3.2](part_3_the_namespace.md)) naming those four things and nothing else."
- What the public listing row is and holds. CC 3.1.1 and CC 3.2 make it a public community's row with name, description, admission policy and named moderator, and say a private community has no directory entry. CC 4.4.3.2.8 gives a non-public affiliation one, holding existence, key id, officers' roles and licence classes only. The family model body has name, description, cohort_subkind, community_key_id.

### audience: 6.1.9,3.1.3,2.6.1.7; manifests/family_model.json (data:scope)

- Side A. CC 6.1.9: "held by the author's node and the recipient's node and by no other"
- Side B. manifests/family_model.json census:share:{class} replication.audience: "targeted -> cohort_plus_subjects(full) (refers-to: attested, subjects, for_key_id); commons -> everyone"
- The text gives a census share one recipient and no widening. The model cell (code-v61) gives it the default audience, and its placement cell says "no addressed placement in code"; subject_rule says for_key_id = serve seat is "not enforced". A kernel run from the data serves a share beyond its seat. The text is consistent in three sections.

### audience: 4.5.5; manifests/family_model.json (data:scope)

- Side A. CC 4.5.5: "A duty-holder's record MAY withhold the reporter's identity and the report's content from the person named"
- Side B. manifests/family_model.json moderation:{allegation_type} replication.audience: "cohort_plus_subjects(full) (refers-to: attested, subjects, for_key_id)"
- The model names an audience value existence_only and a two-part body for it, and no family carries it. A moderation record built from the data is served whole to the person named, so the reporter cannot be shielded as CC 4.5.5 allows.

### supersede: 3.3.9,5.3.2.3 (condition)

- Side A. CC 3.3.9: "Current state is resolved by stable-id grouping — `supersedes` to amend, `withdraws` to revoke, latest `asserted_at`, tie-break smallest `attestation_id`"
- Side B. CC 5.3.2.3: "Then the `MergeBallot` comparator: `quorum_weight` → signed timestamp → content hash."
- Which licence row is current. CC 3.3.9: latest signed instant, tie on the smallest attestation id, and "the substrate's merge never counts signers". CC 5.3.2.3: quorum weight first, then time, then content hash, with the more restrictive state winning. Two nodes holding the same rows can read a licence as active and as suspended. Nothing decides.

### supersede: 3.1.2.1; CC 8.10; manifests/transitions.json (data:exception)

- Side A. CC 3.1.2.1: "A rebuild is a `supersedes` on the earlier Contribution"
- Side B. CC 8.10 card provenance:build_manifest:{target}: transitions attest and withdraw only; manifests/family_model.json verbs ["attest", "withdraw"]
- A rebuild's superseding row is admitted by the text and has no transition in the data or on the card, which CC 8.10 says is the document's statement of the value. A door built from the transitions refuses the row the text calls for.

## Known conflicts whose stale wording is still in the text

- C240 (audience, 1.13.3.1,5.2,2.4.1.1): What an outsider learns of a bounded group. C240 is proposed and not applied: the CC 1.13.3.1 wording stands unchanged (ids ride the envelope, membership changes emit hard_case rows into the log), while CC 5.2 and CC 2.4.1.1 keep roster rows inside the audience that already holds the roster.
- C290 (agent_identity, 1.16.5,4.3,4.5.1,7.1.5): Who seats a Wise Authority. C290 says to fix from the text and it is not fixed: CC 1.16.5 still appoints under the Governance Charter, the lead of CC 4.3 restates it, and the CC 4.5.1 register row still has two thirds of the sitting board confirming members. CC 4.3 (the party confers, no roster) is the wire-checked rule.
- C329 (agent_identity, 3.3.6,4.4.3.4.3,4.5.13): Whether a row signed by an agent's occurrence key counts as the person's. C329 is repaired in CC 4.4.3.4.3 (the "two occurrences of one user identity" wording is gone), but CC 3.3.6 still says the agent speaks as the identity. CC 4.4.3.4.3, CC 4.5.13 and CC 1.15.11 support side B.
- C333 (supersede, 2.4.1,4.2.6,2.4,3.1.3,3.1.1): C333 says to fix the CC 2.4.1 table and the wording stands. More cases of a supersedes by another signer than C333 lists: a key rotation (the new record is attested by the new key), the holders' transport:canonical_rebind over a node's own binding, a listing changed by a moderate-holder. The model cell reads same_attester and notes "the door admits any signer's supersedes".
- C332 (supersede, 2.4.1,3.2,3.5.1): Still open for the steward: whether a new guardian displaces the old by their own row. Both wordings stand. The CC 8.10 card for ownership rows gives supersede to the author only.
- C334 (supersede, 3.4.5.1,2.4.1,4.4.3.3.1,3.5.1): C334 is repaired in CC 4.4.3.3.1, which now says a widening is a placement. The CC 2.4.1 gloss ("replaces a prior one") and CC 3.4.5.1 still give supersedes one meaning, ending the prior row, with no exception for a widening.
- C110 (supersede, 3.3.4,4.4.3.4.2,3.1.3.2): Whether a new version of the group record can add a member. C110 reads them as two objects and no conflict; the wording of CC 4.4.3.4.2 and CC 4.4.3.2.3 is unchanged. The transitions guard (membership_supersede_cannot_add) agrees with CC 3.3.4.
- C317 (placement, 4.5.13,5.4.6,1.13.3.4): C317 says to fix CC 4.5.13 and the sentence stands. Beyond the minor band that C317 treats, the two differ for every owner: CC 5.4.6, CC 3.2 and CC 1.13.3.4 make a federation-scope binding an opt-in, and CC 4.5.13 makes it the starting answer.
- C319 (other:family-registration, 3.1.7,2.4): Still open for the steward: refuse a row of an unregistered family, or admit it under the producer-steward default. Both sentences stand. CC 2.4 gives a third treatment for a row of an unregistered type already held: reported, not served, not replicated, not deleted.

## Known conflicts checked and found repaired (not reported in the table)

- C291 and C311: the CC 5.2 enforcement block now names occurrences and the allow list (the repair leaves the minor finding on `self` above).
- C295: CC 3.3.6.2 now lists addressed rows and cohort rows among what a link carries before Rooted.
- C262: the mute paragraph of CC 4.5.5 no longer says "always visible".
- C249, C214: CC 6.1.5 reads "at any tier"; CC 6.1.5.1 reads a larger target as the audience.
- C134, C278: CC 2.6.8 and CC 3.4.5.1 now cite the audience rule.
- C156 (the rounding part): Part 1 no longer lists grid rounding as a mitigation.
- C326, C330: CC 2.1 now states the key grant and roster version exceptions.

## Keys with nothing to report

- projection (10 statements): the text and the projection cells agree (goals table rebuildable, key_grant and consent peer set derived, occurrence revocation minted to the key plane).
- other:cell-containment (1 statement): one formula, no second statement and no data.

## Limits

- All seven keys were finished. In `audience` the 5.4.6 carriage lists (stranger, forwarder, responder, what crosses before Rooted) were compared with each other and with C294, C338 and C147 and no new difference was found; they were not compared with the shipped serve gate.
- The data comparison for placement and audience covered the families named by the statements, not all 184 rows. Placement cells marked `gap` were reported only where the text states a bound for the family (four rows); the same holds for any other family whose text pins a scope.
- The cosign:{state} replication and placement cells are null (reason `unbuilt`), so the audience CC 3.1.3 and CC 3.3.4 state for a held change has no data to compare with.
