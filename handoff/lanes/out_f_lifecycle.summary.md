# Lane F, column `lifecycle`: prose against the family model

201 inventory statements (scope `family`, column `lifecycle`) give 262 (statement, family) rows. No statement is gone.

## How to read the verdicts

- Every `lifecycle` cell in the model is read from code (`code-v61`, 181 families) or is a gap (3). No cell is sourced from the text, so no row is `AGREE`. Where prose and cell say the same, the verdict is `FILLS` and the note begins "confirms". A `FILLS` whose note says "fills a gap" or "held shut" gives a value the model lacks.
- A stem was expanded to all its registry rows only where the statement covers them all (`capacity`, `detection`). Where the words name one leaf or one record, the row is on that family: `consent` goes to the consent leaf named; `family`, `community` and `affiliations` records go to `group:roster`; `identity_occurrence` goes to `identity:occurrence`.
- A `[need:…]` tag in a note marks a vocabulary need. It appears on every `RICHER` row and on any other row that shows the same need.
- `prose` ending `[gist]` is the inventory gist, used where `rule_entries.tsv` has no phrase for the statement. The `quote` is empty on those rows unless one was found by hand.
- I did not judge whether a rule is good, only whether prose and cell say the same.
- The repository changed under this lane while it ran (other lanes were editing the text, `rule_entries.tsv` and `family_model.json`). Cells and words are as read at about the time of writing; CC 3.1.3.2 and CC 5.3.3.2 were re-read after their wording on leaving a group changed from "withdraws" to `membership:resignation`.

## Counts per verdict

| verdict | rows |
|---|---|
| AGREE | 0 |
| FILLS | 80 |
| DISAGREE | 12 |
| RICHER | 101 |
| NOT_A_CELL | 69 |
| GONE | 0 |

Of the 80 `FILLS` rows, 4 give a value where the cell is empty or held shut (`cosign:{state}`, `retirement:{state}`), one states the default row, and the rest confirm a code reading.

## RICHER needs, grouped

Each is a candidate token or column. Counts are distinct inventory statements: first those with a `RICHER` verdict, then every statement carrying the tag.

- **N-SUPC** (12 RICHER, 14 in all). supersede_constraint: a bound on what a supersede may change or who may sign it (never grows a roster, never weakens a protocol, narrowing only by supersede, monotone member, head-chained by prev_head_digest, bounded renewal, signed by a key other than the attester under a prior commitment or quorum). Families: `consent:replication:{version}`, `encyclopedia:*`, `group:roster`, `identity:occurrence`, `key:revocation`, `session:{kind}`, `transport:canonical_rebind`, `trust:{job}:{version}`. Sections: 2.1, 2.4, 3.1.3, 3.1.3.1, 3.1.3.2, 3.2, 3.3.13, 3.3.4, 3.3.6.2, 3.3.7, 4.4.3.4.4.
- **N-EXP** (12 RICHER, 13 in all). expiry mode and consequence: expires in {required, optional, forbidden, default:<ttl>, bounded:<max>, none_when_confirmed/fuse_when_lone} and on_expiry in {lapse, substrate_emits:<leaf>, reaped, purgeable}. Families: `accord:invoke:constitutional:{halt_id}`, `capacity_assurance:reversible_pending:{domain}:{version}`, `census:member:share`, `census:share:{class}`, `config:{scope}`, `consent:partnership_accept`, `consent:partnership_grant`, `consent:state:{stance}`, `consent:stream:{kind}`, `mesh_config:{key}`, `rendezvous:route`, `session:{kind}`. Sections: 2.6.1.7, 3.1.2, 3.1.3.1, 3.1.4, 3.3.1, 4.2.1, 4.2.1.3, 4.2.1.4, 4.4.3.4.3.1, 4.4.3.5.5, 6.1.9.
- **N-ROT** (5 RICHER, 13 in all). key effect of a roster change by tier or axis: on_remove in {stop_wrapping, rotate_epoch}, on_add in {rekey_walk, next_seal, none}; rotation_on_removal yes/no is one bit for a rule with two tiers and two directions. Families: `group:roster`, `key_grant:{axis}`. Sections: 3.2, 3.3.4, 4.4.3.2.1, 4.4.3.2.2, 4.4.3.2.5, 4.4.3.2.6, 4.4.3.4.1, 4.4.3.4.5, 4.5.12.1.
- **N-ROW** (12 RICHER, 12 in all). no row in the family model for this record kind (location_proof, live_stream, organization, org_membership, transport_destination, event listing, consent_record): its lifecycle rule has no cell to live in. Families: `consent_record`, `external_content (event_listing)`, `live_stream`, `location_proof`, `org_membership`, `organization`, `transport_destination`. Sections: 3.2, 3.3.13, 3.3.3, 4.5.2.2, 4.5.9.3, 4.5.9.4, 5.3.2.3, 5.3.3.2.5, 5.3.4, 5.4.6.
- **N-ENDS** (9 RICHER, 9 in all). ends_by other than withdrawal: revocation or suspension by the issuing authority, lapse on the issuer's dissolution, exhaustion, forfeiture, dissolution of the record (dissolves_at, last seat lapsed, last leave). Families: `bond_posted:{currency}`, `group:roster`, `key:record`, `key_grant:{axis}`, `licensure:{authority_id}`, `trust:{job}:{version}`. Sections: 2.4.1.2.1, 3.1.1, 4.2.1, 4.4.3.2.8, 5.3.3.2.
- **N-CONFLICT** (8 RICHER, 8 in all). conflict_rule: which row stands among rows of one key (latest wins | earliest wins | duplicate refused | idempotent | union by identity | first reply terminal); the model now hides these in free text under rotation_on_removal. Families: `census:composite:{class}`, `census:member:share`, `census:share:{class}`, `consent:partnership_accept`, `consent:partnership_grant`, `consent:state:{stance}`, `cosign:{state}`, `key_grant:{axis}`, `membership:{stage}`. Sections: 3.1.3, 3.1.3.2, 3.3.1, 3.3.2, 4.4.3.5.3.
- **N-SIDE** (8 RICHER, 8 in all). on_withdraw / on_lapse effect: an act the withdrawal or lapse triggers (emits a hard_case row, starts the decay protocol, fires the deletion SLA, ceases replication, locks the room). Families: `consent:deletion_sla:{days}`, `consent:partnership_accept`, `consent:partnership_grant`, `consent:replication:{version}`, `consent:state:{stance}`, `identity:occurrence`, `trust:{job}:{version}`, `watchlist:{id}`. Sections: 3.3.1, 3.3.7, 3.4.4, 4.4.3.2.8, 4.4.3.4.3, 4.5.2.2, 4.5.7.
- **N-LEAF** (3 RICHER, 7 in all). per-leaf cells: one family whose leaves have different lifecycle values (a cell per closed leaf, or the family split into rows). Families: `cosign:{state}`, `membership:{stage}`. Sections: 3.1.3, 3.1.3.2, 3.3.4, 5.3.3.2.
- **N-EFFECT** (6 RICHER, 6 in all). withdraw_effect: what an admitted withdrawal does in the fold (retire the named row | boundary R: every grant at or before R leaves | whole, never partial | terminal, no later copy reopens | forward-only, a later write does not resurrect). Families: `consent:community_trust`, `consent:state:{stance}`. Sections: 3.3.1, 4.4.3.5.5.
- **N-WHO** (5 RICHER, 6 in all). withdraws_by parties outside {attester, subject, cosigned}: the self-roster door (quorum path or lone path), another live roster key, the current owner, an adjudicated recovery (wa_adjudication_ref). Families: `consent:community_trust`, `identity:occurrence`, `identity:occurrence_revocation`, `ownership:{relation}:{target_kind}:{version}`. Sections: 3.3.1, 3.3.6, 3.3.6.3, 3.4.5, 4.4.3.4.6.
- **N-CLASS** (3 RICHER, 5 in all). retraction_class tokens and contest path: no token for a third party's finding or a notice; class conditional on the issuer's declared legal-weight class; contest_path in {reconsideration, counter_notice}. Families: `capacity:composite`, `capacity:relay_delivery`, `capacity:{factor}`, `detection:correlated_action:{axis}`, `detection:distributive:access:{resource_type}`, `detection:hash_chain_integrity`, `detection:intra_agent_consistency`, `detection:{detector}`, `licensure:{authority_id}`, `revocation:{entity_type}:{reason}`, `takedown_notice:{basis}`. Sections: 2.4.1.1, 4.4.3.2.8.
- **N-COND** (1 RICHER, 2 in all). withdraw_condition: a withdrawal admissible only while a named state holds (e.g. no later-stage row exists). Families: `retirement:{state}`. Sections: 3.1.5, 7.5.5.
- **N-REACH** (2 RICHER, 2 in all). supersedes reach: a row that supersedes a range of other rows below it (compaction), not its own earlier version. Families: `ledger:checkpoint:{unit}:{version}`. Sections: 3.1.3, 3.3.10.1.
- **N-RECANT** (1 RICHER, 2 in all). recants_by in {attester, none}: the column names who withdraws and has no token for a family whose recants is refused. Families: `key_grant:{axis}`, `news:*`. Sections: 3.3.13, 3.3.2.
- **N-SUBJKIND** (0 RICHER, 2 in all). subject exclusion by subject kind: an affiliation named as subject never withdraws, whatever the family. Families: `*`, `affiliations`. Sections: 2.4.1.1, 4.4.3.2.8.
- **N-COSIGN-INST** (1 RICHER, 1 in all). withdraws_by by instance: rule 0 turns on whether this row carries additional_scrubs, so a family with single-signer and cosigned instances needs a conditional value. Families: `goal:{scale}`. Sections: 3.1.9.7.

## DISAGREE rows in full

- **CC 2.4.1.1, `licensure:{authority_id}`**
  - cell (code-v61): `withdraws_by={attester}; retraction_class=peer; supersedes=same_attester; expires=expires_at honoured; rotation_on_removal=no`
  - prose: "a `licensure:*` or `revocation:*` row, where the licensee's path is `reconsideration:{grounds}`"
  - quote: "a `licensure:*` or `revocation:*` row, where the licensee's path is `reconsideration:{grounds}`"
  - proposed: retraction_class=authority_act (withdraws_by={attester} stands)
  - reading: [need:N-CLASS] cell class peer; prose keeps the row from its subject and gives the licensee reconsideration; 2.4.1.1 also lists a licence as an act of a body under a declared legal-weight class; the vocabulary has authority_act and no cell uses it
- **CC 2.4.1.1, `licensure:{authority_id}`**
  - cell (code-v61): `withdraws_by={attester}; retraction_class=peer; supersedes=same_attester; expires=expires_at honoured; rotation_on_removal=no`
  - prose: "an act of a body under a declared legal-weight class, such as a conviction or a licence"
  - quote: "an act of a body under a declared legal-weight class, such as a conviction or a licence"
  - proposed: retraction_class=authority_act
  - reading: [need:N-CLASS] cell class peer; prose names a licence as an act of a body under a declared legal-weight class; supported by 4.4.3.2.8
- **CC 3.1.1, `revocation:{entity_type}:{reason}`**
  - cell (code-v61): `withdraws_by={attester}; retraction_class=duty_record; supersedes=same_attester; expires=expires_at honoured; rotation_on_removal=no`
  - prose: "Entity revocation (`agent` / `partner` / `license`). Immediate, non-rollbackable."
  - quote: "Immediate, non-rollbackable."
  - proposed: withdraws_by={}; retraction_class=none
  - reading: cell admits the attester's withdrawal; prose says non-rollbackable, which 2.4.1.1 reads as "withdrawn by nobody" for key:revocation, citing this section; the document supports the prose
- **CC 3.1.3.2, `membership:{stage}`**
  - cell (code-v61): `withdraws_by={cosigned}; retraction_class=cosigned; supersedes=typed record supersede only; expires=expires_at honoured; rotation_on_removal=yes`
  - prose: "The inviter withdraws a proposal with the ordinary `withdraws`."
  - quote: "The inviter withdraws a proposal with the ordinary `withdraws`."
  - proposed: proposal leaf: withdraws_by={attester}; retraction_class=peer
  - reading: [need:N-LEAF] cell says only a cosigned withdrawal for the whole family; prose gives the inviter the ordinary withdraws for a proposal; the registry row (3.1.3) calls proposal, acceptance and decline single-signer, so the document supports the prose
- **CC 3.3.2, `key_grant:{axis}`**
  - cell (code-v61): `withdraws_by={}; retraction_class=none; supersedes=same_attester; expires=expires_at honoured; rotation_on_removal=yes`
  - prose: "A rotation is a new row under a new axis identity, never an edit of an old one."
  - quote: "A rotation is a new row under a new axis identity, never an edit of an old one."
  - proposed: supersedes=none
  - reading: cell says a same-attester supersede; prose says a rotation is a new row, never an edit; 5.1 says no row supersedes a wrap, so the document supports the prose
- **CC 3.3.2, `key_grant:{axis}`**
  - cell (code-v61): `withdraws_by={}; retraction_class=none; supersedes=same_attester; expires=expires_at honoured; rotation_on_removal=yes`
  - prose: "No row supersedes or removes the prior wrap."
  - quote: "No row supersedes or removes the prior wrap."
  - proposed: supersedes=none
  - reading: cell says a same-attester supersede; prose says no row supersedes or withdraws the prior wrap
- **CC 3.3.4, `group:roster`**
  - cell (code-v61): `withdraws_by={cosigned}; retraction_class=cosigned; supersedes=typed record supersede only; expires=expires_at honoured; rotation_on_removal=yes`
  - prose: "4. On admission of a REMOVE: per [CC 4.4.3.4.5](part_4_composition_governance.md) the removed member retains existing key_grants (cannot retroactively un-share); the substrate stops wrapping new key_grants to them on subsequent family-scoped Contributions."
  - quote: "4. On admission of a REMOVE: per [CC 4.4.3.4.5](part_4_composition_governance.md) the removed member retains existing key_grants (cannot retroactively un-share); the substrate stops wrapping new key_grants to"
  - proposed: rotation_on_removal=no at family (stop wrapping); yes at community
  - reading: [need:N-ROT] cell says yes for every group; prose says a family removal stops new wraps and 4.4.3.4.5 says nothing is rotated at self and family
- **CC 3.3.6, `identity:occurrence`**
  - cell (code-v61): `withdraws_by={attester, subject}; retraction_class=peer; supersedes=same_attester; expires=expires_at honoured; rotation_on_removal=no`
  - prose: "**Revocation**: an eviction is a `withdraws` against the `identity_occurrence` row, proposed by a live roster key and landing under [CC 3.3.6.3](#3.3.6.3)."
  - quote: "**Revocation**: an eviction is a `withdraws` against the `identity_occurrence` row, proposed by a live roster key and landing under [CC 3.3.6.3](#3.3.6.3)."
  - proposed: withdraws_by = the self-roster door (quorum path or lone path), no token today
  - reading: [need:N-WHO] cell lets the attester or the subject withdraw alone; prose lands an eviction only under the two self-roster paths of 3.3.6.3 once the self holds two or more keys; 4.4.3.4.6 reads the same
- **CC 4.4.3.4.5, `key_grant:{axis}`**
  - cell (code-v61): `withdraws_by={}; retraction_class=none; supersedes=same_attester; expires=expires_at honoured; rotation_on_removal=yes`
  - prose: "- **Self and family.** Every write seals under a fresh per-write DEK ([CC 4.4.3.4.1](#4.4.3.4.1)), so the substrate simply stops wrapping new DEKs to the removed member's keys; no key is"
  - quote: "no key is reused, so nothing is rotated"
  - proposed: rotation_on_removal=no (content axis, self and family); yes (epoch and stream axes)
  - reading: [need:N-ROT] cell says yes for the whole family; prose says at self and family nothing is rotated
- **CC 4.5.12.1, `group:roster`**
  - cell (code-v61): `withdraws_by={cosigned}; retraction_class=cosigned; supersedes=typed record supersede only; expires=expires_at honoured; rotation_on_removal=yes`
  - prose: "When a member leaves a family, or an occurrence is withdrawn from a self-collective, the rule is the one at [CC 4.4.3.4.5](#4.4.3.4.5). The departed party keeps the `key_grant`s it already"
  - quote: "The departed party keeps the `key_grant`s it already holds and nothing is re-encrypted."
  - proposed: rotation_on_removal=no at family
  - reading: [need:N-ROT] cell says yes; prose says a departure from a family rotates nothing: the substrate stops wrapping
- **CC 5.1, `key_grant:{axis}`**
  - cell (code-v61): `withdraws_by={}; retraction_class=none; supersedes=same_attester; expires=expires_at honoured; rotation_on_removal=yes`
  - prose: "| Content-addressed grant rotation | `(at_rest_sha256, attested_key_id)` (the recipient) | the substrate's grant store, indexed on the pair | `rotation_chain`, an informative trail of the prior `key_grant_id`s; no row supersedes"
  - quote: "no row supersedes or removes a wrap"
  - proposed: supersedes=none
  - reading: cell says a same-attester supersede; prose says no row supersedes or removes a wrap
- **CC 5.1, `key_grant:{axis}`**
  - cell (code-v61): `withdraws_by={}; retraction_class=none; supersedes=same_attester; expires=expires_at honoured; rotation_on_removal=yes`
  - prose: "| Stream/epoch-addressed grant rotation | `(stream_id, epoch[, recipient])` | `federation_stream_chunks(stream_id, seq)` | The same `rotation_chain` trail **on the new axis**; a rotation is a new row under a new axis"
  - quote: "a rotation is a new row under a new axis identity"
  - proposed: supersedes=none
  - reading: cell says a same-attester supersede; prose says a rotation is a new row under a new axis identity

The disagreements reduce to six findings:

1. `licensure:{authority_id}` reads class `peer` where the text makes a licence an authority act.
2. `revocation:{entity_type}:{reason}` admits the attester's withdrawal where the text says non-rollbackable.
3. `membership:{stage}` gives one cosigned value where a proposal is single-signer and withdrawn by its inviter. (A member's leaving is its own `membership:resignation` row; that is recorded as N-LEAF, not as a disagreement.)
4. `key_grant:{axis}` reads `supersedes=same_attester` where the text says no row supersedes a wrap. CC 2.4.1.2.1 calls `rotation_chain` "supersession lineage", so the text also disagrees with itself here.
5. `rotation_on_removal=yes` on `group:roster` and `key_grant:{axis}` where the text rotates at community scope only.
6. `identity:occurrence` lets one key evict where the text requires the self-roster door.

## Sections where every statement is AGREE or FILLS

For this column these could become a pointer to the table:

- CC 1.13.2 (1 statements; `consent:partnership_grant`)
- CC 3.1.2.1 (2 statements; `provenance:build_manifest:{target}`, `provenance:build_manifest:{target}:locale:{lang_code}`)
- CC 3.1.3.3 (1 statements; `custody:{kind}`)
- CC 3.1.5 (1 statements; `retirement:{state}`)
- CC 3.1.5.5 (1 statements; `evidence:{suite}:{kind}:{cell}:{prefix}`)
- CC 3.1.9.3 (2 statements; `need:{domain}:{kind}`, `testimonial_witness:{kind}`)
- CC 3.3.5.1 (1 statements; `key_grant:{axis}`)
- CC 3.3.6.2 (1 statements; `identity:occurrence`)
- CC 3.3.10 (1 statements; `settlement:*`)
- CC 4.2.3 (1 statements; `group:roster`)
- CC 4.4.3.2.2 (1 statements; `group:roster`, `key_grant:{axis}`)
- CC 5.3.2.1 (1 statements; `custody:{kind}`)
- CC 5.3.2.5 (1 statements; `custody:{kind}`)

Sections whose only other rows are `NOT_A_CELL`, so their lifecycle content also reduces to a pointer: CC 3.1.3.4, CC 3.3.6.1, CC 4.3, CC 4.4.3.2.6, CC 4.5.5, CC 6.1.9.

## Notes on the model

- The cells of `community:listing`, `config:{scope}`, `content_class:{class}`, `goal:{scale}`, `mesh_config:{key}`, `quarantine:{state}` and `session:{kind}` carry a conflict or fold rule as free text inside `rotation_on_removal`. That is N-CONFLICT and N-EFFECT already showing in the data.
- `retraction_class` declares the token `authority_act` and no cell uses it. `none` is used by three cells and is not in the declared vocabulary. `supersedes` carries "typed record supersede only", also outside it.
- The note on the default `withdraws_by` cell already records that the owner, the rule-3 proxy and the rule-4 delegate are "outside vocabulary".
- Mappings I inferred and did not verify against the shipped store: `affiliations` records to `group:roster`; the scoped agency delegation to `self:delegates_to:agent_occurrence`; the "grant" column of the CC 2.4.1.2.1 table to `key_grant:{axis}`.

