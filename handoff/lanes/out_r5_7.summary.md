# Fifth reading, share 7: summary

Keys: `key_plane`, `roster_fold`, `consent_fold`, `content_ingestion`, `subject`. Read at head 1ee1bcf, family-scope rows included as full members. Known ids checked against `formal/derivation/text_conflicts.tsv` (C001 to C512).

## The three numbers

- New major findings, text against text: **3**
- New major findings, text against data: **2**
- Statements opened in the text: **428 of 428**; read by gist only: **0**. (348 found by their entry phrase; 78 had no entry phrase and were found by matching the gist inside the named section, then read in the paragraph; 2 had neither and were read in the paragraph that carries the rule: CC 3.2 community wrap v2, CC 2.4.1.1 `subject_sha256_ed25519_raw`.)

## Per key

| rule key | statements | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| key_plane | 146 | 7 | 1 | 2 (C404, C407) | 4 | 0 |
| roster_fold | 113 | 8 | 1 | 4 (C283, C329, C412, C487) | 2 | 1 (C494) |
| consent_fold | 65 | 11 | 3 | 4 (C354, C449, C495, C496) | 2 | 2 (C188, C474) |
| content_ingestion | 59 | 5 | 0 | 0 | 5 | 0 |
| subject | 45 | 4 | 0 | 1 (C331) | 3 | 0 |
| total | 428 | 35 | 5 | 11 | 16 | 3 |

## Major new findings in full

1. **key_plane, text against text (instant): when a change of keep takes effect.** CC 5.1: "Turning kept on mid-stream wraps the current and later epochs." CC 5.3.3.2.5: "A publisher changes keep mid-stream at an epoch boundary, as ruled for one DEK per stream per epoch, and the change reaches forward only." One build wraps the epoch in progress the moment keep is turned on; the other waits for the next boundary, which on a call with no membership change may never come. CC 5.1 is the home and is specific in both directions (on: current and later; off: from the next epoch).

2. **roster_fold, text against text (actor): how a new device joins a self.** CC 4.5.12.5: "Unlike self-occurrence, family membership changes are **NOT single-vouch by default**"; CC 4.4.3.4.3 "co-admitted at login by single-vouch"; CC 4.5.12.3 opens with admission "on a signature from EITHER the root ... OR any currently active occurrence". CC 3.3.6.3: with two or more live keys an addition lands by a strict majority at once or by the lone path after 86 400 s. CC 4.4.3.4.6 and `transitions.json` (`identity:occurrence` attest = `two_path`, `self_roster_add`) follow 3.3.6.3. Under the single-vouch reading one stolen device seats another at once.

3. **consent_fold, text against text (actor): the viewer's consent row at the infohazard interstitial.** CC 4.5.13 has the viewer publish "`consent:state:granted` + a `consent:scope:view` qualifier, viewer-side". CC 3.4.5 admits `consent:state:granted` only from "a `subject_key_id` of the target Contribution or a `delegates_to` chain rooted at one". A viewer is not a subject of the hidden item, so a substrate built to 3.4.5 refuses the row the interstitial depends on, and `resolve_consent` reads only the named subjects' rows. No exception is stated.

4. **consent_fold, text against data (condition): the terminal cut is still in the fold cell.** CC 4.4.3.5.5 and CC 3.3.1 now both state the boundary fold ("Every grant from s asserted at or before R is out, whichever row was named"). The `fold` cell of `consent:state:{stance}` in `manifests/family_model.json` still carries `@stance=revoked: cut=terminal` and `cut=boundary(asserted_at),terminal`, each citing CC 4.4.3.5.5: the reading C413 and C427 removed from the text. Under it, revoking the newest grant leaves an older one standing. CC 4.4.3.5.4 keeps the phrase "revoke-is-terminal precedence".

5. **consent_fold, text against data (actor): who signs a partnership grant.** CC 3.4.5 (corrected under C360): "`consent:partnership_grant` by the granting user as `attesting_key_id`, its `subject_key_id` naming the partner". The signer cells of `consent:partnership_grant` and `consent:{kind}` (cc-table) still read `self x delegates_to(chain rooted at a subject) x {}`. The only subject of a grant is the partner, so the cell admits a chain rooted at the agent occurrence signing the user's grant.

## Known findings still present

C329 (an agent occurrence is a roster key that signs owner acts), C412 (`identity:occurrence` withdraw and `identity:occurrence_revocation` attest are `selfAct`), C494 / C506 (`membership:{stage}` withdraw is cosigned), C449 (`consent:state` signer cell lacks the subject and its chain), C496 (`consent:community_trust` signer and fold are owner-only), C495 (`watch_sla` reads the row, not the member; only the comment was changed), C474 (`consent:partnered` in CC 1.13.2), C331 (158 `in_audience: no` cells), C188 (the gate still named `consent:scope:analyze`).

Open with the steward and reported because this reading reached them independently: C404, C407, C283, C487, C354.

Checked and found fixed in the text, so not reported: C170, C291, C304, C305, C311, C325, C405, C408, C410, C413, C414, C427, C428, C490, C299.

## Keys not finished

None. Limits of this reading: CC 8.10 family cards were not opened one by one; the data comparison used `family_model.json`, `transitions.json`, `governance_policy.json` and the departures, and `reactions.json` and `signed_object.cddl` only by search for the members in question.
