# Third reading, share 7: summary

Head 87c1730, branch rc19. Five rule keys, 428 statements, every scope taken (the `family` rows as full members). 46 findings: 14 major (13 new, 1 known) and 32 minor (26 new, 6 known).

| rule key | statements | major new | major known | minor new | minor known |
|---|---|---|---|---|---|
| key_plane | 146 | 4 | 0 | 10 | 3 |
| roster_fold | 113 | 5 | 1 | 4 | 1 |
| consent_fold | 65 | 3 | 0 | 4 | 1 |
| content_ingestion | 59 | 0 | 0 | 5 | 0 |
| subject | 45 | 1 | 0 | 3 | 1 |

## Major new findings

1. **key_plane** (5.1,5.3.3.2.5; condition)
   - A: CC 5.1: for a kept stream the earlier epochs reach the joiner as `key_grant:stream:v1` wraps, bounded by the catch-up bound below
   - B: CC 5.3.3.2.5: a publisher who wants a newcomer to see more re-shares by their own act
   - CC 5.1 gives a late joiner of a kept stream the earlier epochs within the catch-up bound; CC 5.3.3.2.5 gives nothing earlier unless the publisher re-shares. CC 2.1 (what a kept stream's joiner can fetch) sides with CC 5.1; CC 4.4.3.2.6 `full` "confers no grant on an earlier epoch" sides with 5.3.3.2.5.

2. **key_plane** (3.2,4.4.3.2.1; instant)
   - A: CC 3.2: one DEK shared across emissions (per-emission cost **O(1)**, not O(members)), wrapped to each member on admission
   - B: CC 4.4.3.2.1: a member admitted since the epoch's DEK was minted is wrapped at the next sealed write in that epoch
   - When a new community member first holds the epoch key: at admission (CC 3.2) or only at the minter's next sealed write (CC 4.4.3.2.1, 4.4.3.4.1, 4.4.3.2.5). In a quiet community the two differ for the person. manifests/reactions.json (on sealed, emit key_grant:epoch) sides with Part 4.

3. **key_plane** (3.2,4.4.3.4.1; exception)
   - A: CC 3.2: honest holders MUST delete past-epoch content keys, the epoch DEKs and `K_record_id` / `K_symbol`, after the window
   - B: CC 4.4.3.4.1: A member's new device at those scopes is granted every epoch that member's other devices already hold, by the minter's receive doors and sweep.
   - Under the default `rotate-forward` a holder deletes past-epoch community DEKs after 30 days; CC 4.4.3.4.1 and 4.4.3.4.5 (every grant held stays; nothing re-encrypted) have no such lapse and grant a new device every past epoch. Neither names the other; whether community history older than the window stays readable differs.

4. **key_plane** (3.2; scope)
   - A: CC 3.2: `archive_mode` adds one OPTIONAL config field to the `community` subject_kind and one closed enum
   - B: CC 3.2: it rides no attestation, is not part of the community's signed roster or `consensus_protocol`
   - One section calls archive_mode a per-community field of the community record, surfaced at creation, and operator-local config that rides no attestation. A field on the signed record and a node-local setting are different bytes; CC 4.4.3.2.8 (retain is the default when a class declares a floor) reads it from the declared record. No data file carries the member.

5. **roster_fold** (4.4.3.4.6,3.3.6.3; exception)
   - A: CC 4.4.3.4.6: The root `I` itself is implicitly a member (the identity_key is always an admissible signer for its own content).
   - B: CC 3.3.6.3: The string survives as the self's name if that key is later evicted, and resolution then verifies the roster chain back to it.
   - resolve_self returns the occurrences "∪ {I}" and calls the root always an admissible signer; CC 3.3.6.3 makes the genesis key roster key one and evictable, and CC 4.5.12.3 says "until the self evicts its genesis key". A builder of 4.4.3.4.6 keeps wrapping to and admitting from an evicted (stolen) genesis key.

6. **roster_fold** (2.6.6.3,3.2,4.4.3.2.3; exception)
   - A: CC 2.6.6.3: such a community admits by invitation and the constraint describes it rather than gates it
   - B: CC 3.2: the candidate's most-recent `location_proof` (within `valid_until`) MUST be contained in the geographic_constraint
   - A geographic community with a constraint finer than resolution 7: CC 2.6.6.3 admits by invitation with the constraint not gating; CC 3.2, CC 2.6.6.2 and the CC 4.4.3.2.3 predicate (not contained: return false) refuse every joiner, since no proof is finer than 7. CC 3.1.3.2 says the proof is required in addition, never instead.

7. **roster_fold** (3.2,4.5.12.5,4.5.13; exception)
   - A: CC 4.5.12.5: and admissible for an affiliation only under the one-voice countersign rule of [CC 4.4.3.2.8](#4.4.3.2.8)
   - B: CC 3.2: `founder_only` is refused for every community above the family, not only infrastructure
   - An affiliation is a community at cohort_scope affiliations (CC 3.3.9). CC 4.5.12.5 admits `founder_only` there (CC 4.4.3.2.8: a one-voice body may hire); CC 3.2 (twice), CC 3.3.4 and CC 4.5.13 refuse it for every community above the family and list no affiliation exception. A sole practitioner's record is admitted under one and refused under the other.

8. **roster_fold** (3.1.3.2,4.5.13; condition)
   - A: CC 3.1.3.2: A role change for an already-active member is not growth and needs no acceptance.
   - B: CC 4.5.13: A founder who would rather hand the room on promotes a member to founder under the protocol, with that member's own signature.
   - Promotion of a member to founder is a role change. CC 3.1.3.2 asks nothing of the member; CC 4.5.13 requires the member's own signature. A role-change row without it is admitted under one reading and refused under the other; the trust-root rule (a founders' amendment seats only a key that signed) sides with 4.5.13.

9. **roster_fold** (3.3.6,3.3.6.3; data:actor)
   - A: data manifests/transitions.json: "policy": "selfAct"
   - B: CC 3.3.6: No single occurrence evicts at once with no window: that unilateral configuration is one a thief wins in two steps.
   - In manifests/transitions.json the identity:occurrence withdraw transition is roles author, subject under policy selfAct (code-v61); only attest carries two_path with self_roster_add, and no transition names self_roster_evict. The text lands an eviction by quorum or the lone path. The family model's governance cell names both policy rows, so the transition is the stale side.

10. **consent_fold** (3.3.1,4.4.3.5.5; condition)
   - A: CC 3.3.1: the latest admitted revocation's `asserted_at` putting every earlier grant out
   - B: CC 4.4.3.5.5: a revoke is terminal for the grant it names (its supersedes_id)
   - CC 3.3.1 gives `consent:state:*` the boundary fold: any revocation or withdrawal puts every earlier grant out, whichever row it named. resolve_consent lets a revoke that names a grant end only that grant, and drops a withdrawn grant from the rows, so an older grant stands again. One reads no consent where the other reads granted. CC 4.4.3.5 ("latest non-superseded emission") is a third wording.

11. **consent_fold** (3.3.1,4.4.3.5.1,4.4.3.5.6; actor)
   - A: CC 4.4.3.5.6: Revocation + decay-protocol per CC 4.4.3.5.1: substrate emits stage milestones; agent honors stage-appropriate processing constraints
   - B: CC 3.3.1: which is eviction, not a protocol stage, and it emits no `consent:decay:*` row
   - Who signs a `consent:decay:{stage}` row. CC 3.3.1 (emitter class: the protocol runner) and the last sentence of CC 4.4.3.5.1 say the running party, never the substrate; the CC 4.4.3.5.1 pseudo-code ("substrate emits at elapsed=0") and the CC 4.4.3.5.6 table say the substrate. manifests/reactions.json emits by author. A substrate-signed decay row fails the leaf's emitter class.

12. **consent_fold** (3.3.1,4.4.3.5.5; condition)
   - A: CC 3.3.1: which it emits for a lapsed grant (`expires_at`, or a `retain:<window>` in the scope) with `consent_supersedes` naming the grant
   - B: CC 4.4.3.5.5: g.valid_until passed without renewal
   - When a grant lapses. One sentence of CC 3.3.1 lapses a grant at `expires_at` or at the window of a `retain:<window>` scope token; the `consent:state:expired` row of the same table, resolve_consent and manifests/reactions.json (expiry member `valid_until`, optional) know only `valid_until`. A `retain:90d` grant with no `valid_until` lapses at 90 days under one and never under the other.

13. **subject** (3.3.5,4.4.3.4.3.1; term)
   - A: CC 3.3.5: subject_key_id: key_id // the subject declaring stance (federation_keys
   - B: CC 4.4.3.4.3.1: **the partner** — the OTHER party (agent occurrence for `grant`, user identity for `accept`); singular, non-empty
   - On a `consent_record`, `subject_key_id` is the party declaring the stance (CC 3.3.5, and its bilateral pattern, where the subject emits the grant under its own key) or the other party (CC 4.4.3.4.3.1, the canonical signed member set, and CC 4.4.3.5.3). On a partnership grant the member holds the user under one and the agent occurrence under the other, so the signed bytes and the ratification check differ. CC 3.3.1 ("emitted by subject_key_id") follows 3.3.5.

## Known conflicts checked against the text today

- Fixed in the text, no finding raised: C098 ("MUST hold the asset" is gone from CC 4.4.3.4.3), C109 (the `unanimous` arm of the CC 4.4.3.4.2 pseudo-code now states the removal reading), C158 and C159 (CC 3.3.4 no longer says "the family DEK" or wraps to `subject_key_ids`), C170 (the N=1 row of CC 4.4.3.2.6 now says a grant is never withdrawn), C291 (the CC 5.2 pseudo-code names the allow list), C325 (CC 4.5.12.3 now says "unless a strict majority of the other members objects"; "with no objection" is nowhere in Parts 1 to 7), C329 (CC 4.4.3.4.3 now says the agent's occurrence buys reading only).
- Fixed, reported for the overlap: C311 (CC 5.2 is fixed; CC 4.4.3.4.4 keeps one sentence of the old reading), C326 and C330 (CC 2.1 now states the two exceptions).
- Still as written: C115 (one word, epoch, for two keys; the CC 4.4.3.2.6 table itself is fixed), C188 (the dimension spelling `consent:scope:analyze` stands in CC 3.4.5, 3.1.4 and 3.1.8.1), C292 (public room: community scope against federation scope), C110 (pseudo-code iterates new members of a proposed record), C283 (held for Eric; text unchanged).

## Data compared

`manifests/family_model.json`, `manifests/transitions.json`, `manifests/reactions.json` (with `formal/derivation/reaction_text.tsv`), `constitution/governance_policy.tsv`, `constitution/constants.tsv`, `manifests/family_departures.tsv`, for the families `key_grant:{axis}`, `membership:{stage}`, `identity:occurrence`, `group:roster`, `consent:*`, `content_class:{class}`, `cw_class:{class}`, `config:{scope}`. The CC 8.10 cards were not read as text: they are generated from the family model, the transitions and the reactions, which I read directly, so a fault of the card generator itself would not show here. Five findings are text against data (one major: the `identity:occurrence` withdraw transition is one voice where the text lands an eviction by two paths). `archive_mode` appears in no data file except the `epoch_key_retention_secs` constant.

## Limits

- 80 of the 428 statements have no entry phrase in `rule_entries.tsv` (mostly table rows and pseudo-code of CC 2.1, 3.2, 4.4.3.4.3 and 5.2). I read those by gist and looked up today's words only where the gist differed from a neighbour, so a wording-only difference inside those rows can have been missed.
- Quotes were checked by program to be verbatim substrings of the Parts or the named data file, at most 30 words.
- Keys not finished: none.
