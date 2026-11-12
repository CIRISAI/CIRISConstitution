# Fifth reading, share 6: summary

Head 1ee1bcf, branch rc19. Seven rule keys, 425 inventory statements. Output: `out_r5_6.tsv` (29 findings).

## The three numbers

- New major findings, text against text: **4**
- New major findings, text against data: **2**
- Statements opened in the text: **397**; read by gist only: **28**

## Per rule key

| Rule key | Statements | Findings | Major new | Major known | Minor new | Minor known |
|---|---|---|---|---|---|---|
| moderation | 153 | 15 | 5 | 5 | 3 | 2 |
| delegation | 102 | 3 | 0 | 2 | 1 | 0 |
| reserved_prefix | 76 | 3 | 1 | 1 | 1 | 0 |
| policy_row | 55 | 6 | 0 | 2 | 3 | 1 |
| accord | 36 | 2 | 0 | 2 | 0 | 0 |
| other:list-of-record | 2 | 0 | 0 | 0 | 0 | 0 |
| replication | 1 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **425** | **29** | **6** | **12** | **8** | **3** |

A finding is filed under the key whose statement carries it; several touch two keys (the witness role is filed under delegation, the accord's "live set" under policy_row).

## Major new findings in full

### Text against text

1. **A community steward acts alone, but the admission gate knows no steward** (moderation; CC 4.5.13 against CC 4.5.5 and 4.5.4).
   CC 4.5.13: "or any **steward** where the community has named one, resolves the action by a **single signature**". CC 4.5.5 admits a duty action as-self only from the content's subject or the community's "named-moderator / `moderate`-holder", and its duty-holder table and the CC 4.5.4 authority set name no steward. A steward who is not also a moderate-holder is admitted by one section and refused by the other. The policy row `moderation_action` (`role:moderator|steward`) sides with CC 4.5.13. The same gap covers "A steward, where one exists, MAY appoint a moderator directly", since CC 4.5.4 lets only a founder or a protocol-authorised key appoint.

2. **An undefended harm report is removed by a notice nobody may sign** (moderation; CC 4.5.13 against CC 4.5.3 and 4.5.5).
   The outcome ladder gives "report undefended (no keep-decision and no vote carried in the window)" the outcome "the removal action (`takedown_notice`); content does not survive". CC 4.5.3 item 1 requires the notice's key to hold the `takedown` duty, and CC 4.5.7 and 4.5.4 say no node signs. The case arises only when no moderator or steward acted, so no eligible signer exists. `manifests/reactions.json` reads the case as a verdict `withdrawn` on the target, with no notice. C390 (for Eric) covers the neighbouring vote-against case, not this one.

3. **The viewer's consent row is refused by the consent reservation** (moderation; CC 4.5.13 against CC 3.4.5 and 3.3.1).
   The infohazard interstitial "publishes a `consent:*` attestation (`consent:state:granted` + a `consent:scope:view` qualifier, viewer-side". CC 3.4.5: `consent:state:granted` "MUST be emitted by a `subject_key_id` of the target Contribution or a `delegates_to` chain rooted at one". A viewer is not a subject of the reported item. One reading records every view; the other refuses the row at the door, which leaves the attributable-view rung with no row.

4. **A required `system:` leaf that the registry rule refuses** (reserved_prefix; CC 3.1.7 against CC 4.5.10.4).
   CC 3.1.7: "A reserved wildcard family publishes the leaves this Part names beneath it (`leaves`) and is **closed**"; any other leaf is `namespace_family_unregistered`. CC 4.5.10.4 says an operator "MUST register" via a `system:perceptual_hash_matcher:registered` row. Part 3 catalogues no leaf under `system:*` and never names that one. The registry disagrees with CC 3.1.7 too: `system:*` has `"leaves": []` and `"leaves_closed": false`. `system:` and `delivery_receipt:` are also missing from the CC 3.1.7 reserved-stem list and from `_meta.case_rule.reserved_stems`, though CC 3.4.3 and 3.4.6 reserve them.

### Text against data

5. **Who may sign a takedown notice** (moderation; CC 4.5.5 and 4.5.3 against `manifests/family_model.json`).
   The text admits a `takedown_notice` from the content's signed subject as-self (`subject_of(content_sha256)`) and, on a hash match, from the owner of the detecting node. The cell `takedown_notice:{basis}` signer_rule (code-v61) reads `seat_role(takedown)` via `delegates_to(takedown)` with no conditions, which admits neither.

6. **Which `hard_case` kinds are the substrate's alone** (moderation; CC 3.4.2 and 3.4.4 against `manifests/namespace_registry.json` and the family model).
   CC 3.4.2 and 3.4.4: "Non-substrate emissions on these prefixes are a category error and MUST be rejected", for the named kinds. The registry row `hard_case:{kind}` is `"reserved": false`, "Open vocabulary.", with no per-kind rule. The family model reserves the whole family to `substrate_persist`. A door built from the registry admits anyone's `hard_case:family_membership_change`; a door built from the family model refuses every non-substrate kind. The two data files also disagree with each other.

## Known conflicts found still present

- C478 (slash duty-holder against WA quorum): still in CC 4.1.3 and CC 3.4.7.1, neither of which C478 lists.
- C068 (marked settled): the duty-holder table of CC 4.5.5 still has no row for slashing or quarantine, and the CC 4.5.4 appointment shape still carries three scopes.
- C387, C397, C403: wording unchanged.
- C392, C457, C476, C488: data unchanged.
- C323: also a text-against-text matter. CC 3.2, 3.4.1 and 4.4.3.8 treat `content_rating` as a reserved-prefix role; CC 3.1.7 and CC 3.4 carry no such reservation, and CC 3.1.9.2 cites an emitter rule at CC 3.3.12 that is not there.
- For Eric, reported because I would have reported them unprompted: C283, C399, C419, C395 (C395's ruling has landed in CC 4.5.7; residue wording remains in CC 4.5.5 and 3.1.9.4), and C487 (open).

## Read by gist only (28 statements)

The dossier tool could not locate these by entry phrase and I did not open their paragraphs:

| Key | Section | Count |
|---|---|---|
| policy_row | CC 3.2 (founder_only, infrastructure M/N, entrenchment, admission) | 11 |
| policy_row | CC 5.3.3.2.5 | 1 |
| delegation | CC 2.1 (oversight mode) | 2 |
| delegation | CC 2.4.1.1 | 1 |
| delegation | CC 3.2 (T3 conferral, quorum confers a duty scope) | 2 |
| delegation | CC 4.4.3.8 | 1 |
| moderation | CC 2.4.1.1 | 1 |
| moderation | CC 3.2 (founder sets room moderation) | 1 |
| moderation | CC 5.2 (recipient_excluded) | 2 |
| reserved_prefix | CC 3.2 (hard_case community kinds) | 1 |
| reserved_prefix | CC 4.4.3.8 | 1 |
| accord | CC 3.2 (accord triple as a family; two planes) | 2 |
| accord | CC 4.4.3.8 | 1 |
| accord | CC 2.6.1.7 (attestation_evidence) | 1 |

## Limits of this reading

- All keys were finished, but the conflict table was checked by keyword search and by a listing of the first 188 of its 420 rows that touch my sections. A finding marked `new` may be listed under words I did not search.
- `manifests/transitions.json`, `signed_object.cddl` and the CC 8.10 cards were not compared for these keys. Data comparison covered `governance_policy.tsv`, `namespace_registry.json`, `family_model.json` (signer, cosign, governance, freshness cells of 16 families) and one `reactions.json` entry.
- CC 4.5.3 `CourtOrder` ("follows the court's stated timeline" against "destroyed on receipt") is not reported: C303 reads it as no conflict.
