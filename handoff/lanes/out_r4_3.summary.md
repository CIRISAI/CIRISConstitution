# Fourth reading, share 3: summary

Repository at 05cbcc8 (branch rc19). Conflict table read: C001 to C435.

## The three numbers

- New major findings, text against text: **2**
- New major findings, text against data: **7**
- Statements opened in the text: **424** of 425; read by gist only: **1**

## Per rule key

| rule key | statements read | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| signer | 201 | 15 | 6 | 5 | 4 | 0 |
| owner_binding | 93 | 4 | 2 | 2 | 0 | 0 |
| freshness | 61 | 3 | 0 | 2 | 1 | 0 |
| steward | 47 | 1 | 0 | 1 | 0 | 0 |
| legal_hold | 16 | 2 | 1 | 1 | 0 | 0 |
| other:keep | 4 | 2 | 0 | 0 | 1 | 1 |
| other:asymmetry-register | 2 | 1 | 0 | 0 | 0 | 1 |
| other:generated-from-data | 1 | 0 | 0 | 0 | 0 | 0 |
| **total** | 425 | 28 | 9 | 11 | 6 | 2 |

## Major new findings in full

### 1. `owner_binding` — condition — CC 3.2,3.4.13

- Side A: CC 3.2 The age band is the I1 band (`age_self_declared` / `age_assurance:*`, [CC 3.3.12](part_3_the_namespace.md); `minor` < 18 / `adult` ≥ 18).
- Side B: CC 3.4.13 The guardian MUST be ≥ `age_assurance:provider:adult` as a floor, and the guardianship relationship to that specific child MUST be verified.
- The CC 3.2 admission predicate for a guardian's binding asks only age_band(S) == adult on the I1 band, which a self-declaration supplies; CC 3.4.13 asks a provider-rung assurance and a verified relationship. One admits a self-declared adult as guardian, the other refuses. CC 3.4.13 is the minors' home.

### 2. `owner_binding` — term — CC 3.2

- Side A: CC 3.2 true iff exactly one live owner-binding on `K` exists, from a `user`-role identity that is not itself steward-bound
- Side B: CC 3.2 The re-signed row is a second owner-signed row beside the `self` one, never a replacement, and the audience rule of its tier places it.
- An announced or group-joined node carries two or more live owner-binding rows by one owner. Read by rows, is_steward_bound is false for it and the steward-binding gate refuses it; read by owners it holds. owner_of ('at most one key') supports counting owners; the data fold (family_model ownership fold: test=count=1 over live rows keyed by attested_key_id) counts rows.

### 3. `signer` — data:actor — CC 3.1.9.2; manifests/family_model.json

- Side A: CC 3.1.9.2 **reserved — substrate-steward-emitted**, the emitter rule pinned at mint per R2(a), so the ProducerSteward default never applies
- Side B: manifests/family_model.json regime:{artifact}:{version} signer_rule (code-v61): who any_registered, via none; transitions.json attest roles: registered
- The text reserves regime rows to the substrate steward; the data admits any registered key and cites no section. The cell is read from the store; the text is the only rule stated.

### 4. `signer` — data:actor — CC 3.1.5.5; manifests/family_model.json

- Side A: CC 3.1.5.5 Emitted at `federation` scope by a key holding `infra:attest`, delegated by the root or conferred by an accord co-scrub of its key record
- Side B: manifests/family_model.json evidence:{suite}:{kind}:{cell}:{prefix} signer_rule (code-v61): who any_registered, via none; transitions.json attest roles: registered
- The text gates evidence rows on the infra:attest role (CC 4.2.1 rule 1 agrees); the data admits any registered key and marks CC 3.1.5.5 as 'fills'.

### 5. `signer` — data:actor — CC 4.5.5,4.4.3.4.3; manifests/family_model.json

- Side A: CC 4.5.5 A duty action (`takedown_notice`, `moderation:*`, `reconsideration:*`, `slashing:*`, `quarantine:*`) is admitted **iff** one holds **positively**
- Side B: manifests/family_model.json slashing:{outcome} signer_rule (code-v61): who any_registered, via none; transitions.json attest roles: registered
- The text puts slashing verdicts under the enforced duty-holder gate with scope slash (CC 4.5.5 scope table, CC 4.4.3.4.3); quarantine's cell carries seat_role(slash) but slashing's cell admits anyone. C068 settled the text side only.

### 6. `signer` — data:condition — CC 3.4.10,3.1.2; manifests/family_model.json

- Side A: CC 3.4.10 `transparency_log:cosigned:*` is reserved: emitter rule is `attesting_key_id` MUST match a `federation_keys` row with `identity_type="witness"`
- Side B: manifests/family_model.json transparency_log:cosigned:{tree_size} signer_rule (code-v61): seat_role(attest) via delegates_to(infra:attest_assurance); qualifier + identity_type contains witness
- The text asks only the witness role in identity_type; the data adds a delegated scope infra:attest_assurance that no section names. Same shape as C423 (age_assurance), on a different family.

### 7. `signer` — data:actor — CC 3.4.5,3.3.1; manifests/family_model.json

- Side A: CC 3.4.5 `consent:state:granted` / `consent:state:revoked`, `consent:scope:*`, `consent:stream:*` MUST be emitted by a `subject_key_id` of the target Contribution or a `delegates_to` chain rooted at one
- Side B: manifests/family_model.json consent:state:{stance} signer_rule (code-v61): who self | owner_of_subject(for_key_id), via none; the consent:scope and consent:stream cells carry via delegates_to(chain rooted at a subject)
- The text admits a delegate on a chain rooted at a subject for consent:state as for scope and stream; the data's consent:state cell has no chain and adds the owner of the node named in for_key_id, which the text does not state for this leaf.

### 8. `signer` — data:actor — CC 3.3.1,3.3.5,3.4.5; manifests/family_model.json

- Side A: CC 3.3.5 **`expired` is substrate-emitted only** — a producer/subject MUST NOT assert `expired` (it is the substrate's `valid_until`-passed emission)
- Side B: manifests/family_model.json consent:state:{stance} signer_rule (code-v61): who self | owner_of_subject(for_key_id); transitions.json attest roles: owner, self
- Text (CC 3.3.1, 3.3.5, 3.4.5) gives the expired leaf to substrate_persist alone by the longest-pattern rule; the data has one cell for all three stances with no substrate emitter, so it admits a subject's expired and not the substrate's.

### 9. `legal_hold` — data:exception — CC 4.4.3.5.4,4.4.3.2.8; manifests/family_model.json

- Side A: CC 4.4.3.5.4 or under a `legal_hold` ([CC 4.4.3.2.8](#4.4.3.2.8)), the `withdraws` is admitted and recorded, and the descent it would force is refused with reason
- Side B: formal/derivation/family_default_row.json erasure_route: purge (steward purge on a cosigned notice); legal_hold: none in code (162 families carry it); manifests/reactions.json and transitions.json hold no legal_hold entry
- The text gives a legal hold a gate in front of withdrawal-driven descent and three hard_case emissions (set, lifted, violation_attempt); the data's erasure route has no hold, and no reaction emits those rows. A withdrawn record under hold is kept by the text and descends by the data.

## Known conflicts met again

Reported as known, with the fault still present at this head: C368 (the residue has moved to CC 4.5.9.4), C366, C365 and C388, C422 and C364, C360 (now a fault of the data only), C346, C371, C372 (wider than recorded), C117 (open), C197 (held). Reported although open with the steward: C312, C404. Reported although proposed and not applied: C085.

## Looked at and not reported

- `key_grant` issuer (CC 2.4.1.2.1 owner or steward, against the epoch minter of CC 3.3.2): each minter owns its own epoch key (CC 4.4.3.2.1), so the two agree.
- The unowned serve seat (CC 3.2 against CC 5.4.6): C252, already fixed; both end with the node not serving.
- `archive_release` under a lawful order (CC 3.1.5 WA-emitted on both bases, CC 7.5.5 'WA approval or lawful order'): the row is the Wise Authority's on both bases; a careful reader follows the table.
- `attach_window_secs` 604800 declared with witnessed mode off (CC 5.3.4) against 'no timer' (CC 3.2 T6): the declared value is read by nothing while the quorum is 0.
- The substrate role wording (CC 3.4.2 'MUST match a federation_keys row' against CC 3.4.3 'conferred by a live delegates_to'): one rule, CC 3.4.7.1.
- Data cells whose who is narrower in transitions.json than in family_model.json (`census:member:partial`, `ballot:moderator_acceptance`): the data disagrees with itself, the text agrees with the narrower one.

## Keys not finished

None. One statement was read by gist only: `steward`, CC 4.4.3.8, the cold-start restatement (inventory p4:1241), whose words I did not find in the section today; the four `steward` statements beside it in CC 4.4.3.8 were opened.

## Method note

The share is the same list of keys the third reading took, so most of what the table already holds was met again; what is new here is mostly text against the family model, where a `code-v61` signer cell admits any registered key to a family the text reserves (`regime`, `evidence`, `slashing`), or carries a condition no section states (`transparency_log:cosigned`), or has one cell for leaves the text separates (`consent:state`). The CC 8.10 cards are generated from the same data and repeat each of these.
