# Lane F: replication, placement, subject_rule against the family model

152 statements of `rule_inventory.tsv` (75 replication, 37 placement, 40 subject_rule), 174 (statement, family) rows in `out_f_audience.tsv`. Every quote was checked to be verbatim in the Parts as they stand on `rc19`.

## Counts per verdict

| column | AGREE | FILLS | DISAGREE | RICHER | NOT_A_CELL | GONE | rows |
|---|---|---|---|---|---|---|---|
| replication | 0 | 29 | 2 | 28 | 26 | 1 | 86 |
| placement | 5 | 15 | 0 | 13 | 7 | 0 | 40 |
| subject_rule | 1 | 15 | 3 | 17 | 12 | 0 | 48 |
| all | 6 | 59 | 5 | 58 | 45 | 1 | 174 |

How the verdicts were drawn. Most cells of these three columns were read from the shipped store, and the replication and subject cells of 140 to 164 families are the one generic default. So `AGREE` is rare: it is used only where the cell is itself sourced from the text. Where the cell is the generic default or a code reading and the prose gives the family's value, the verdict is `FILLS`, also when the prose is narrower than the code reading (these are marked "Narrower than the cell" in the note). `DISAGREE` is kept for a cell that states a specific value the prose contradicts.

FILLS that narrow the code reading (the store admits more than the text allows): `session:{kind}` (cohort ceiling at every commons tier), `consent:replication:{version}`, `self:delegates_to:agent_occurrence` and `consent:partnership_grant` (federation tier only), `deferral:request` (never a federation broadcast), `rendezvous:route` (everyone), `census:share:{class}` and `census:member:share` (addressee only), `watchlist:{id}` (never commons).

## RICHER needs, grouped

Each is a candidate token or column. The number is the count of (statement, family) rows that want it; two rows (location_proof, chat_message) want both need 3 and need 10, so the numbers sum to 60 over 58 rows.

**Across the three columns**

1. **A value that depends on the leaf inside one parameterised family (6).** `hard_case:{kind}`: `deletion_window_breach` is local tier and self-scoped, `recipient_excluded` goes into the affected self or family scope and never beyond (CC 3.3.1, 3.4.4, 5.2). `consent:state:{stance}`: `revoked` is not local-tier-eligible (CC 3.3.5). `config:{scope}`: `admission` and `transport` MUST be self, `load` MAY be the smallest scope that reaches its routing peers (CC 3.4.5.1). Candidate: split the family row per leaf, or a per-leaf override on a cell.
2. **A value decided by the cohort's record, per class, never by the family or the writer (4).** Licence scope per licence class in the charter (CC 2.4.1.2.1, 4.4.3.2.8); `disclosure_posture: transparency-seeking` placing classes at federation (CC 4.4.3.2.8); `access_control_model: minimum-necessary` making the audience a subset of the cohort (CC 4.4.3.2.8). Candidate token: `by_cohort_record(member)` in placement and in audience.
3. **Kinds named in the text with no row in the model (7).** `location_proof`, `local_data` and `chat_message` (content sub_kinds, CC 3.3.3, 3.3.13, 4.4.3.3), `observed:*` and `epistemic:*` (CC 2.3.1, 4.5.2.1), `data_subject_access_grant` (CC 4.4.3.2.8). Each has a placement or subject rule and nowhere to put it.

**replication**

4. **The public-room and infrastructure exception to "the content's scope" (5, of which 2 in placement).** Holding claims of a public room or an authorised infrastructure community sit at federation scope though the content is at community scope (CC 1.13.3.4, 3.1.3.3, 3.2, 4.4.3.2.1). Candidate token: `scope_of(content)` with `commons if cohort_subkind in {public, infrastructure}`.
5. **Audience at an instant, and a bound on holding (3).** `cosign:{state}`: members at the event's signed instant who are members still when served; the invitee is named and not served; a pending row is held at most one hold window and never again (CC 3.1.3, 3.3.4). `key_grant:epoch`: a later joiner is served no earlier epoch's grant (CC 2.1). Candidate parts: `audience_as_of`, `hold_bound`.
6. **The carrier (2).** A row that travels inside another object or on its own replication kind: a `steward_purge` notice inside the tombstone bundle (CC 3.3.2), `identity_occurrence` as its own wire kind (CC 3.3.6.1). Candidate part: `carrier`.
7. **A condition on the node's announcement state (3).** For an unannounced node the occurrence and owner-binding rows ride sealed inside the contact request and acceptance, held by the owner's nodes and the contact alone (CC 5.4.6); `identity:occurrence` and `ownership:*`.
8. **A pin class (3).** Identity, consent and config records are always pinned and exempt from the byte budget; corpus is pin on consent, cache otherwise (CC 6.1.5.2). Candidate column: `pin_class`.
9. **Singles (7).** An audience of "every node that holds a named trust root" (`transport:canonical_rebind`, CC 3.1.3). The minting origin: only the primary's node mints, others relay verbatim (`cosign:pending`, CC 3.1.3). A flag that the family replicates even when what it marks is withheld (`quarantine:{state}`, CC 3.1.9.2). A row replicated to the roster's nodes yet readable by anyone on request (public room content, CC 3.2). Reach beyond the cohort only by re-emission naming the readers (`licensure`, CC 2.4.1.2.1). `non_recipient: refuse(token)` and "no widening ever applies" (`census:share`, CC 6.1.9). The condition and the withheld members when a duty-holder shields a reporter (`moderation`, CC 4.5.5).

**placement**

10. **The authoring default as distinct from the allowed set (3).** Settlement defaults to the narrowest cohort holding payer and payee (CC 3.3.10); chat defaults tighter than articles (CC 3.3.13); location proofs are typically federation (CC 3.3.3). The cell lists what may be chosen and has no place for the default.
11. **A placement derived from another row (2 RICHER; 5 AGREE rows already hold it as free text).** `file:{version}` takes its directory's scope at the instant of placing and does not follow it afterwards (CC 3.1.3.4). `ownership:*` is self by default, wider by the owner's re-sign, federation required for a serve seat (CC 3.1.3.2). The `custody` and `key_grant` cells already say "the content's scope" in prose; the declared vocabulary has no such token.

**subject_rule**

12. **A predicate on a key the row names (11).** The key must hold a seat (`rendezvous:route`, CC 3.1.4), be a roster member (`ballot:moderator` ranks, CC 3.1.3), be the owner of the attested node at `asserted_at` (`consent:community_trust`, CC 3.3.1, three statements), have signed its own acceptance of the proposal (`group:roster` widenings, CC 4.4.3.2.3, 4.4.3.2.5, 4.4.3.4.2, four statements), not be a node-bearing key in a founder role (CC 3.2), or be independent of the lineage (charter witnesses, CC 2.1). Candidate part: `named_key_predicate`.
13. **Singles (4).** A vocabulary for `in_audience` (only "no" occurs; the prose has "member at asserted_at" and "the key the family delivers to", CC 2.1). The strength of enforcement: producer MUST, substrate MAY refuse or flag (CC 2.3.1, 4.5.2.1). A binding across two rows: each partnership half names the other's signer (CC 4.4.3.5.3). A mark that the row's own `subject_key_ids` is advisory and authority is read from the target's signed subject set (`takedown_notice`, CC 4.5.5).

## DISAGREE rows in full

**replication · CC 2.6.1.7 · `consent:state:{stance}`**

- Cell (mixed): `default: tier local or federation; audience by scope (self_collective: owner's nodes; targeted: cohort_plus_subjects(full); commons: everyone); non_recipient null; held settle_on_key`
- Prose: "Also carried on consent:state rows."
- Cell: the generic audience, cohort plus the keys referred to (for_key_id among them), so for_key_id adds a recipient. Prose: the member table states for every row carrying for_key_id that it is held by the author's node and this key's node and by no other, then says consent:state rows carry it. The document does not settle which reading holds for consent:state; 6.1.9 states the addressed rule generally but in the census context.

**replication · CC 3.3.2 · `key_grant:{axis}`**

- Cell (mixed): `{"tier": "federation", "audience": "addressee", "non_recipient": null, "held": "refuse"}`
- Prose: "the row is placed at the content's scope and reaches the recipient's node because the row *refers to* it"
- Cell: audience addressee, held refuse. Prose: 'Audience by the one rule', the row has the audience of the content's scope and the recipient's node is added because the row refers to it. CC 3.1.3 ('placed at the content's scope'), CC 2.1 and CC 5.2 support the prose; nothing in the text makes a key grant addressee-only.

**subject_rule · CC 2.1 · `key_grant:{axis}`**

- Cell (code-v61): `{"kind": ["attested = recipient occurrence (AV-84 exception)", "cardinality 0"], "for_key_id": "none"}`
- Prose: "a key grant's recipient ([CC 3.3.2](part_3_the_namespace.md#3.3.2))"
- Cell: attested = recipient occurrence, cardinality 0, marked as an exception to the producer rule. Prose: CC 2.1 counts the recipient among the keys a row lists in subject_key_ids, and its producer rule ('A targeted row naming a third party in attested_key_id is refused') names no exception for a key grant. CC 3.1.3 and CC 3.3.2 ('The recipient is attested_key_id') support the cell.

**subject_rule · CC 2.1 · `ownership:{relation}:{target_kind}:{version}`**

- Cell (code-v61): `attested = the node; a minor's binding never announced at federation`
- Prose: "and the owner's own node on an owner-binding"
- Cell: attested = the node. Prose: CC 2.1 lists the owner's node among delivered keys in a paragraph about subject_key_ids, and its producer rule names no exception for an owner-binding, whose attested key is the node and not the owner who signs. The cell's reading is the one CC 3.1.3.2 describes.

**subject_rule · CC 4.4.3.4.7 · `* (default row, family scope)`**

- Cell (code-v61): `default: kind any; cardinality any; must_be_registered attested yes, subjects no; for_key_id none; in_audience no; attested_party Targeted only`
- Prose: "is admitted at family visibility only when the subject's rule-3 proxy is within the family's audience, and is otherwise refused `subject_outside_audience`"
- Cell (the default row, read from code): in_audience 'no'. Prose: at a targeted scope every key in subject_key_ids must be within the row's audience, else the row is refused. CC 2.1 ('Whom a targeted row may name') and CC 5.2 state the same rule; the text supports the prose and the shipped store does not yet check it.

## Sections where every statement was AGREE or FILLS

Within the column named, these sections could become a pointer to the table.

- **replication**: CC 3.1.3.1 (session:{kind}); CC 3.1.4 (rendezvous:route); CC 3.1.9.3 (deferral:request); CC 3.4.5 (capacity:*); CC 4.4.3.4.7 (key_grant:{axis})
- **placement**: CC 3.1.1 (community:listing, device:label); CC 3.1.2.1 (provenance:build_manifest:{target}); CC 3.1.3 (census:composite:{class}, key_grant:{axis}, settlement:*); CC 3.1.9.3 (need:{domain}:{kind}, testimonial_witness:{kind}); CC 3.1.9.4 (watchlist:{id}); CC 3.1.9.7 (goal:{scale}); CC 4.4.3.2.1 (attestation:registry_consensus); CC 6.1.5 (custody:{kind}); CC 6.1.9 (census:composite:{class}, census:expected_active, census:member:share, census:partial:{class})
- **subject_rule**: CC 2.4.1.1 (key:revocation); CC 3.1.3.2 (membership:{stage}); CC 3.1.9 (config:{scope}); CC 3.3.10.1 (ledger:head:{unit}:{version}, ledger:checkpoint:{unit}:{version}, ledger:promotion:{version}); CC 3.4.1 (accord:human_dignity); CC 4.4.3.4.3.1 (consent:partnership_accept, consent:partnership_grant); CC 5.4.3 (capacity:relay_delivery); CC 6.1.9 (census:share:{class})

## Other things seen

- `4.5.12.6`: the inventory's sentence about holding claims is gone; the section now points to CC 5.2 (`GONE`).
- The cell tokens `may_receive_group_plane` (`group:roster`, `membership:{stage}`) and `key-plane reach` (`identity:*`, `key:*`) are code names outside the column's declared audience vocabulary.
- CC 4.4.3.2.8 gives a non-public affiliation a `community:listing` row; CC 3.1.1 and the cell describe the listing as a public community's row.
- CC 3.2's worked example seats node members "with no acceptance"; CC 4.4.3.4.2 says nobody joins without their own consent "under any protocol".
- CC 2.1's inventory gist for charter witnesses (identity_type includes `witness`) no longer matches the text, which now says "whatever its `identity_type`".
- `binds_segment` is empty for every family with a subject-bearing pattern (CC 4.5.2.1); it is the natural home for five FILLS rows recorded here under `subject_rule`.
