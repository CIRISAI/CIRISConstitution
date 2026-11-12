# Lane F: `signer_rule` and `signer_named_by_ref`, prose against data

286 statements of scope `family` (283 `signer_rule`, 3 `signer_named_by_ref`), 387 (statement, family) rows. Each note begins with the statement number `sN` in inventory order and its `rule_key`; `verb:` names the transition the statement is about; `need:` and `is:` tags group the findings below.

## Counts per verdict

| verdict | rows | statements with at least one such row |
|---|---|---|
| AGREE | 263 | 182 |
| FILLS | 26 | 25 |
| DISAGREE | 9 | 9 |
| RICHER | 32 | 27 |
| NOT_A_CELL | 57 | 55 |
| GONE | 0 | 0 |
| total | 387 | 286 |

No statement is gone. 15 statements have no entry phrase in `rule_entries.tsv` and were found by gist (marked in the note). Every quote was checked by script to stand verbatim in its section, at most 25 words, inside one table cell.

Readings that shape the counts:

- **A cell read from code that the text narrows or widens is `FILLS`** (25 statements), as the lane rules it; `code-differs` in the note marks each place where the code's cell states something the text does not (26 statements, two of them `RICHER`). `DISAGREE` is kept for a cell sourced from the text (`cc-table`, `prose`) or a transition's roles that the text contradicts.
- **A cell that says what the prose says in free text or in a qualifier is `AGREE`**, with a `need:` tag where the saying is outside the closed vocabulary. So the `need:` counts below are given twice: over `RICHER` rows, and over every row.
- **Stems are expanded** to the registry rows they cover (`accord` 7, `capacity` 3, `capacity_assurance` 3, `detection` 5, `ledger` 3, the content families 13). `community` statements were judged against `group:roster` or `community:listing`, whichever they are about. `consent_record`, `identity_occurrence` and `reasoning_trace` were judged against `consent:state:{stance}`, `identity:occurrence` and `trace:{form}:{version}`.
- **The Wise Authority seat is not ruled on.** 10 statements carry `seat-rule` (s87 s97 s98 s214 s215 s216 s217 s227 s233 s285); each records what the text says. Two of them show a difference a ruling would settle: `archive_release:{basis}` reads `seat_role(wa)` where the text adds "or the steward's recorded WA standing for this agent" (s87), and the seat's domain narrowing has no place in the cell (s227).

## `RICHER` needs, grouped

Statements in brackets. "RICHER" counts statements whose verdict is `RICHER`; "all" adds `AGREE`, `FILLS`, `DISAGREE` and `NOT_A_CELL` rows that carry the same tag.

| # | need | RICHER | all | what is missing |
|---|---|---|---|---|
| S1 | **a who-token for an identity type**: `identity_type contains X` | 2 (s191 s199) | 9 | The cells of 15 families already write `identity_type contains substrate_persist / substrate_edge / lenscore_detector` and say of themselves "(no vocabulary value)"; `witness` (age and capacity assurance, `transparency_log:cosigned`), `agent` (generated content, CC 3.4.14 R2) and `rendezvous` have no token at all, in the signer vocabulary or in `role_tokens`. Candidate: `identity_type(x)` as a who-token over the closed identity-type set. |
| S2 | **a who-token for a named component or its steward** | 3 (s26 s27 s94) | 3 | "Registry-signed", "Registry emits", "substrate-steward-emitted" (`attestation:license_validity`, `provenance:slsa`, `regime`). `steward` in the vocabulary is a trust root or an agent's steward, not the steward of a component. |
| S3 | **other who-tokens**: founder, revoker, author of the target, viewer; and three meanings of `self` | 3 (s42 s143 s277) | 8 | `founder` is a role token in transitions and marked "outside vocabulary" in two cells. The revoker of a key or an occurrence has no token and `identity:occurrence_revocation` has empty roles. `content_class` is "producer-declared" and `cw_class` "community-applied": the vocabulary has `not_author` and no positive author. `self` is written for three relations: attester equals attested (session, custody), attester is among `subject_key_ids` (trace, consent), and signer acts for the attested identity (occurrence, ledger). `observation:access_assumption` needs two of them at once (s102). |
| S4 | **conditions beyond {adult, capacitated, not_subject, not_author}** | 7 (s32 s102 s183 s198 s219 s271 s284) | 10 | `owner_bound(scope)`: the signer holds a live owner-binding, at federation scope (open self-admission, s219), chaining to a bundle root (census return, s284), or as the only way a node-role key counts (s271, s221). `not_proposed_steward` on `capacity_assurance` (s32 s198; the cell already records it as GAP). `signer_not_in_subjects` (s102). A condition on the signer's identity role set (s183). The signer turning on the group's protocol (s61). |
| S5 | **one signer per leaf, where the family cell is closed** | 3 (s20 s128 s181) | 10 | `signer_rule_text.tsv` gives per-stage rules only to a family whose census cell is a gap or shut. Families with a closed cell and one leaf that differs cannot take one: `consent:state:{stance}` (`expired` is the substrate's; five statements, all `FILLS`), `takedown_notice:{basis}` (`steward_purge`), `wa_adjudication:{state}` (`petition` is the petitioner's), `key_grant:{axis}` (axis decides owner or minter, and the minter is also an active member at `asserted_at`), `trust:{job}:{version}` (one free-text string over three leaves). Candidate: allow a per-leaf map on any cell, as `consent:{kind}` and `retirement:{state}` already have. |
| S6 | **delegation shapes `delegates_to(scope, depth, term, caps)` cannot say** | 4 (s12 s227 s254 s286) | 8 | The root's standing (an accountable root that holds the duty, every edge bearing the scope, depth at most 5: s254, three families). A root that is a quorum, not a key (`license`, s12). A scope narrowed by a value the request names (`resolve_deferral:{domain}`, s227). A role held by an accord co-scrub of the key record and not by an edge (`evidence`, s89). **A key named by a current row and not delegated** (`retirement` after `retired`, s286; `preserve_response`, s86), which is the `signer_named_by_ref` column itself: candidate who-token `named_by(family:leaf)`. Scope names `license` and `grant` are outside the scope vocabulary (s9 s15). |
| S7 | **a keyless group as the signer** | 2 (s11 s20) | 4 | A keyless affiliation's first `licensure` row, a keyless family root's `trust:charter` and `trust:confers`, a `steward_purge` notice: "the family is derived from the verified signers, never read from a field". The who-set has no token for a signer that is a group known only by its cosigners. |
| S8 | **signed things with no row in the model** | 3 (s243 s265 s276) | 8 | `location_proof` (subject only, or a `consent_revocation` chain; five statements in CC 4.5.9); the appointment edge `delegates_to(authority → K, scope, community_id)` and who may sign it (s243 s244 s276); which scopes an edge to a node may bear (s234). |
| S9 | **the instant at which standing is judged** | 0 | 5 | `roster_member(at)` has an `at` no cell fills. The text gives four different ones: the row's own `asserted_at` (membership proposal, key_grant minter, deferral response), the signed instant of another row (a `cosign:signature` signer is judged at the pending event's instant, s45), evaluation (`ballot:moderator`, s56), and "without the subject's record" (`key:revocation`, s41). Never the verdict `RICHER` here, since each cell's qualifier says it; it is the commonest thing held only in a qualifier. |
| S10 | **the signer turns on the family of the row acted on** | 1 (s258) | 1 | A reconsideration against a `licensure` row is ruled by the issuing authority's set, not by the community's review holders (s258). |

### Statements that are another column (`NOT_A_CELL` with `is:`)

| tag | carried | statements |
|---|---|---|
| is:binds_segment | no | 2 (s7 s140) |
| is:change | no | 1 (s66) |
| is:change | yes | 1 (s213) |
| is:count | yes | 1 (s245) |
| is:guard | no | 2 (s204 s222) |
| is:guard | yes | 7 (s63 s105 s106 s108 s125 s130 s216) |
| is:reaction | yes | 5 (s109 s126 s129 s135 s159) |

Not carried: s66 (a collection amended by its cohort under the cohort's protocol is a replace by another signer; `change_text.tsv` has only the cascade), s204 (a co-scrub on a pipeline key record must bear `infra:attest` and no other role), s222 (the accept half for a non-steward user follows the steward's answer to a deferral), s7 and s140 (`{authority_id}` binds the signer; the `binds_segment` cell is a gap). Refusal token `licensure_delegator_not_authority` (s10) is in no table.

## `DISAGREE` rows in full

| column | section | family | verdict | cell_value | cell_source | prose | proposed_value | cc_ref | quote | note |
|---|---|---|---|---|---|---|---|---|---|---|
| signer_rule | 3.1.2 | provenance:build_manifest:{target} | DISAGREE | any_registered x none x {} ; the pipeline that built it, whose standing the reader judges | cc-table | Each `BuildManifest` is hybrid-signed (Ed25519 + ML-DSA-65) by the per-primitive steward. |  | CC 3.1.2 | Each `BuildManifest` is hybrid-signed (Ed25519 + ML-DSA-65) by the per-primitive steward. | s28 [signature]; verb:attest; cell (cc-table, CC 3.1.2.1): any_registered, "the pipeline that built it, whose standing the reader judges"; this table row says the per-primitive steward. CC 3.1.2.1 ("signed by the pipeline that built it") supports the cell; the row here may mean the manifest object and not the row, which the text does not say |
| signer_rule | 3.1.3 | system:* | DISAGREE | identity_type contains substrate_persist (no vocabulary value) x none x {} ; CC self-report attester == subject: GAP | prose | CIRISPersist emits on it with `identity_type="substrate_persist"` and CIRISEdge ([CC 3.1.4](part_3_the_namespace.md)) with `identity_type="substrate_edge"` | identity_type contains substrate_persist \| identity_type contains substrate_edge x none x {} | CC 3.1.3 | CIRISPersist emits on it with `identity_type="substrate_persist"` and CIRISEdge ([CC 3.1.4](part_3_the_namespace.md)) with `identity_type="substrate_edge"` | s38 [reserved_prefix]; verb:attest; cell (source prose) and transition roles name substrate_persist only; the text gives Edge the same family under substrate_edge. CC 3.4.3 and CC 3.1.4 support the text |
| signer_rule | 3.1.3.2 | membership:{stage} | DISAGREE | transitions.json attest roles: ["member"] (derived, no stages) | derived | an acceptance or decline is the invitee's only | {"proposal": ["member"], "acceptance": ["self"], "decline": ["self"], "widening": ["member"], "removal": ["member"], "resignation": ["self"]} | CC 3.1.3.2 | an acceptance or decline is the invitee's only | s62 [signer]; verb:attest; transitions.json gives membership attest the one role `member` with no stages; the invitee is not a member. The family cell and CC 3.1.3.2 agree with each other against the transition |
| signer_rule | 3.1.4 | system:* | DISAGREE | identity_type contains substrate_persist (no vocabulary value) x none x {} ; CC self-report attester == subject: GAP | prose | Edge also emits on the one `system:*` family registered at [CC 3.1.3](part_3_the_namespace.md), under its own `identity_type` | identity_type contains substrate_persist \| identity_type contains substrate_edge x none x {} | CC 3.1.4 | Edge also emits on the one `system:*` family registered at [CC 3.1.3](part_3_the_namespace.md), under its own `identity_type` | s69 [signer]; verb:attest; as s38: the cell names substrate_persist only |
| signer_rule | 3.3.1 | consent:{kind} | DISAGREE | {"community_trust": "owner_of_subject x none x {}", "decay": "self x none x {}", "deletion_complete": "self x none x {}", "deletion_sla": "self x none x {}", "partnership_accept": "self x none x {}", "partnership_grant": "self x delegates_to(chain rooted at a subject) x {}", "replication": "self \| owner_of_subject(for_key_id) x none x {}", "scope": "self x delegates_to(chain rooted at a subject) x | cc-table | the node's owner-binding chain — the owner, or the node it owns | self \| owner_of_subject x none x {} | CC 3.3.1 | the node's owner-binding chain — the owner, or the node it owns | s123 [signer]; verb:attest; stage community_trust of the cc-table cell reads owner_of_subject only; the text gives self-or-owner and says the node-authored form stays valid. guard_text (when(type(signer,node)) ...) already assumes a node signer, so the rest of the data supports the text |
| signer_rule | 3.4.3 | system:* | DISAGREE | identity_type contains substrate_persist (no vocabulary value) x none x {} ; CC self-report attester == subject: GAP | prose | the `attesting_key_id` MUST match a `federation_keys` row with `identity_type="substrate_persist"` or `identity_type="substrate_edge"` respectively | identity_type contains substrate_persist \| identity_type contains substrate_edge x none x {} | CC 3.4.3 | the `attesting_key_id` MUST match a `federation_keys` row with `identity_type="substrate_persist"` or `identity_type="substrate_edge"` respectively | s162 [reserved_prefix]; verb:attest; the cell (source prose) names substrate_persist only. Also "cross-attested by all stewards in the steward-triple" is a condition on the key record, in no cell (need:condition) |
| signer_rule | 3.4.5 | consent:{kind} | DISAGREE | {"community_trust": "owner_of_subject x none x {}", "decay": "self x none x {}", "deletion_complete": "self x none x {}", "deletion_sla": "self x none x {}", "partnership_accept": "self x none x {}", "partnership_grant": "self x delegates_to(chain rooted at a subject) x {}", "replication": "self \| owner_of_subject(for_key_id) x none x {}", "scope": "self x delegates_to(chain rooted at a subject) x | cc-table | MUST be emitted by a `subject_key_id` of the target Contribution or a `delegates_to` chain rooted at one | state: self \| owner_of_subject(for_key_id) x delegates_to(chain rooted at a subject) x {} | CC 3.4.5 | MUST be emitted by a `subject_key_id` of the target Contribution or a `delegates_to` chain rooted at one | s172 [signer]; verb:attest; stage `state` of the cc-table cell (signer_rule_text, CC 3.3.1) has via none, where scope, stream and partnership_grant in the same sentence got delegates_to(chain rooted at a subject). The sentence supports the text |
| signer_rule | 3.4.5 | consent:{kind} | DISAGREE | {"community_trust": "owner_of_subject x none x {}", "decay": "self x none x {}", "deletion_complete": "self x none x {}", "deletion_sla": "self x none x {}", "partnership_accept": "self x none x {}", "partnership_grant": "self x delegates_to(chain rooted at a subject) x {}", "replication": "self \| owner_of_subject(for_key_id) x none x {}", "scope": "self x delegates_to(chain rooted at a subject) x | cc-table | **`consent:state:expired`** alone by `substrate_persist`, the one substrate-emitted consent leaf | state: {"granted\|revoked": "self \| owner_of_subject(for_key_id) x delegates_to(chain rooted at a subject) x {}", "expired": "identity_type contains substrate_persist x none x {}"} | CC 3.4.5 | **`consent:state:expired`** alone by `substrate_persist`, the one substrate-emitted consent leaf | s175 [signer]; verb:attest; stage `state` of the cc-table cell gives one signer for all three stances; the text gives expired to the substrate alone. CC 3.3.1 and reaction_text support the text |
| signer_rule | 4.5.5 | reconsideration:{grounds} | DISAGREE | transitions.json attest roles: ["review"] (derived, no stages) | derived | The **subject of the target attestation** holds standing to file `reconsideration:{grounds}`. | {"filing": ["subject", "review"], "ruling": ["review"]} | CC 4.5.5 | The **subject of the target attestation** holds standing to file `reconsideration:{grounds}`. | s252 [signer]; verb:attest; transitions.json gives reconsideration attest the one role `review`; the subject files. The family cell and CC 4.5.5 agree with each other against the transition |

Four findings in nine rows:

1. **`system:*` omits the Edge** (s38 s69 s162). The cell and the transition's roles name `substrate_persist` alone. CC 3.1.3, CC 3.1.4 and CC 3.4.3 all give the family to Edge too, under `substrate_edge`. The text supports itself; the cell is short one arm.
2. **`consent:{kind}` stages `state` and `community_trust`** (s123 s172 s175). The stage rows of `signer_rule_text.tsv` cite CC 3.3.1. For `state` the row has no delegation where CC 3.4.5 gives "a `delegates_to` chain rooted at one" to state, scope, stream and partnership_grant alike, and it gives `expired` the subject's signer where the text gives it to the substrate alone. For `community_trust` it reads `owner_of_subject` where the text reads self-or-owner and keeps the node-authored form valid; `guard_text.tsv` already assumes a node signer.
3. **Two transitions lost their stages** (s62 s252). `membership:{stage}` attest has roles `member`, and `reconsideration:{grounds}` attest has roles `review`, each derived with no `stages`, though both family cells are per stage. An invitee accepting and a subject filing are neither. The family cells and the text agree; the transitions are wrong.
4. **`provenance:build_manifest:{target}`** (s28). The CC 3.1.2 table says the manifest is signed "by the per-primitive steward"; CC 3.1.2.1, which the cell cites, says "signed by the pipeline that built it". This is the text against itself, seen through the cell.

Three more places where the text is in tension with itself or a cell carries a stale remark, not counted as `DISAGREE`: s277 (a viewer signs `consent:state:granted` about content the viewer is no subject of, against CC 3.4.5); s39 and s142 (the `ledger:*` cells carry the qualifier "CC delegate arm: GAP" while the text says no delegate writes); s253 and s255 (the content's own subject may sign a takedown or a moderation act, which `guard_text.tsv` carries and the transitions' roles do not list).

## `FILLS`: the values the text gives

| family | proposed_value | statements | cell today |
|---|---|---|---|
| `key_grant:{axis}` | `minter | owner_of(content or stream) | steward x delegates_to(grant) x {}` | s6 s13 s15 s229 s231 | minter \| owner_of(content or stream) x none x {} ; (owner of the content, not of the subject) |
| `attestation:self_verify` | `self x none x {}` | s25 s35 | any_registered x none x {} |
| `age_self_declared:band:{band}:{version}` | `self x none x {}` | s31 s144 s195 | any_registered x none x {} |
| `attestation:agent_integrity` | `self x none x {}` | s35 | any_registered x none x {} |
| `consent:state:{stance}` | `{"granted|revoked": "self | owner_of_subject(for_key_id) x delegates_to(chain rooted at a subject) x {}", "expired": "identity_type contains substrate_persist x none x {}"}` | s76 s113 s131 s132 s172 s175 | self \| owner_of_subject(for_key_id) x none x {} ; W on the owner's standing |
| `evidence:{suite}:{kind}:{cell}:{prefix}` | `seat_role(attest) x delegates_to(infra:attest) x {}` | s89 | any_registered x none x {} |
| `wa_adjudication:{state}` | `{"petition": "self x none x {}", "abandonment|seizure|successor": "seat_role(wa) x none x {}"}` | s98 | seat_role(wa) quorum, re-derived from this node's state |
| `watchlist:{id}` | `seat_role(moderate) x delegates_to(moderate) x {}` | s103 s260 | any_registered x none x {} |
| `consent:community_trust` | `self | owner_of_subject x none x {}` | s123 | owner_of_subject (binding in force at the signed instant) x none x {} |
| `consent:replication:{version}` | `self x none x {}` | s138 | self \| owner_of_subject(for_key_id) x none x {} ; W on the owner's standing |
| `attestation:license_validity` | `any_registered x delegates_to(license) x {}` | s228 | any_registered x none x {} |
| `slashing:{outcome}` | `seat_role(slash) x delegates_to(slash) x {}` | s251 | any_registered x none x {} |
| `moderation:{allegation_type}` | `seat_role(moderate) | steward x delegates_to(moderate) x {not_subject}` | s274 | seat_role(moderate) x delegates_to(moderate) via the CC 4.5.5 community duty walk x {not_subject} |

## Sections where every statement was `AGREE` or `FILLS`

Of these two columns only; statements in brackets. A section marked F has at least one `FILLS`, so the pointer is safe once the proposed value lands.

CC 2.4 (2), CC 2.4.1.1 (1), CC 3.1.3.3 (1), CC 3.1.5.5 (1 F), CC 3.1.8.1 (1), CC 3.1.9 (1), CC 3.1.9.3 (2), CC 3.3.5 (3 F), CC 3.3.6.1 (1), CC 3.3.6.2 (1), CC 3.3.7 (1 F), CC 3.3.8 (1), CC 3.3.10.1 (1), CC 3.4.1 (6), CC 3.4.4 (6), CC 3.4.8 (5), CC 3.4.9 (2), CC 3.4.11 (2 F), CC 4.2.4 (1), CC 4.4.3.2.8 (1), CC 4.4.3.4.3.1 (2), CC 4.4.3.4.6 (2), CC 4.4.3.5.3 (1), CC 4.4.3.7 (1), CC 4.5.3 (2), CC 4.5.7 (1 F), CC 4.5.8.1 (1), CC 4.5.12.4 (1), CC 5.3.3.6 (1), CC 5.4.6 (2)

The large tables, by verdict of their statements:

| section | statements | AGREE | FILLS | DISAGREE | RICHER | NOT_A_CELL |
|---|---|---|---|---|---|---|
| CC 2.4.1.2.1 | 11 | 4 | 3 | 0 | 2 | 2 |
| CC 3.1.1 | 9 | 5 | 0 | 0 | 1 | 3 |
| CC 3.1.2 | 9 | 3 | 2 | 1 | 3 | 0 |
| CC 3.1.3 | 21 | 19 | 0 | 1 | 1 | 0 |
| CC 3.1.4 | 7 | 6 | 0 | 1 | 0 | 0 |
| CC 3.1.5 | 14 | 11 | 1 | 0 | 0 | 2 |
| CC 3.1.9.4 | 6 | 3 | 2 | 0 | 1 | 0 |
| CC 3.2 | 6 | 1 | 0 | 0 | 0 | 5 |
| CC 3.3.1 | 17 | 10 | 2 | 1 | 0 | 5 |
| CC 3.4.1 | 6 | 6 | 0 | 0 | 0 | 0 |
| CC 3.4.2 | 11 | 10 | 0 | 0 | 0 | 1 |
| CC 3.4.4 | 6 | 6 | 0 | 0 | 0 | 0 |
| CC 3.4.5 | 12 | 9 | 2 | 2 | 1 | 1 |
| CC 4.2.1.4 | 7 | 6 | 0 | 0 | 0 | 1 |
| CC 4.4.3.4.3 | 15 | 11 | 3 | 0 | 1 | 2 |
| CC 4.5.5 | 14 | 10 | 1 | 1 | 2 | 2 |

CC 3.4.2, CC 3.4.4 and CC 3.4.1 are copies of data almost line for line (the `hard_case` emitter repeated per kind; the accord rows). CC 3.1.3's signer column agrees on 19 of 21 statements. CC 3.3.1's *Emitted by* column and the CC 3.4.5 consent row say one rule twice and are where the `consent:{kind}` stage rows need repair before either becomes a pointer.
