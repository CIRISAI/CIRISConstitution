# Lane F: `cosign_rule` and `governance`, prose against data

198 statements of scope `family` (116 `cosign_rule`, 82 `governance`), 208 (statement, family) rows. Each note begins with the statement number `sN` in inventory order and its `rule_key`; a `need:` tag groups the requests below.

## Counts per verdict

| verdict | cosign_rule | governance | all |
|---|---|---|---|
| AGREE | 32 | 4 | 36 |
| FILLS | 13 | 13 | 26 |
| DISAGREE | 6 | 1 | 7 |
| RICHER | 43 | 30 | 73 |
| NOT_A_CELL | 30 | 36 | 66 |
| GONE | 0 | 0 | 0 |
| total | 124 | 84 | 208 |

No statement is gone. Three inventory gists are stale against the text (s41, s186, s189 say "merit auto-promotion"; the text today reconstitutes a moderator by election in merit order). 29 statements have no entry phrase in `rule_entries.tsv` (most of CC 3.2) and were found by gist.

Two readings shape the counts:

- **`community`, `family`, `affiliations` are not row families.** 96 statements name a group kind in `families`. The registry rows that carry what they say are `group:roster` and `membership:{stage}` (and `ballot:moderator` for the election), so each was judged against those cells. The stem `community` expands only to `community:listing`, which none of them is about.
- **A cell read from code that says `none` where the text gives a value is `FILLS`**, as the lane rules it. `DISAGREE` is kept for a cell or table row that states a value the text contradicts.

## `RICHER` needs, grouped

Counts are statements (rows in brackets where they differ). Needs marked T came from `NOT_A_CELL` statements: they are not per-family values and want a table of their own.

### `cosign_rule`

| # | need | statements | what is missing |
|---|---|---|---|
| C1 | **count set** | 14 (s16 s20 s29 s36 s40 s75 s76 s81 s86 s97 s120 s123 s167 s197) | The token names a protocol and not the set it is counted over: standing or live roster; founders only (infrastructure); the deciding seats (affiliation); the full seated roster (WA); every member other than the target (removal); persons listed, never a node; never a delegate or a transitive chain; the roster as it stands at the decision and not at the proposal. Candidate: a `count_over` part of the cell with a closed vocabulary. |
| C2 | **exception path** | 7 (s9 s17 s19 s37 s52 s53 s145) | A cosigned family has named single-signer versions: a holder's recovery version of `group:roster`, the T7 recovery widening (self-signed on a live `trust:confers`, adds one human founder, never removes), the founding record (every listed person signs; the protocol does not yet exist). Candidate: `exceptions[]` on the cell, each with its own signer and bound. |
| C3 | **protocol source** | 6 (s4 s8 s82 s89 s90 s93) | `group_consensus_protocol` does not say whose: the group the row is about, the accord, the authority named in the dimension (`licensure`), the trust root (`mesh_config`, `steward_purge`), a keyless family root's own roster (`trust:charter`, `trust:confers`). CC 2.4 says "the family declares its `consensus_protocol` source"; the model has no place for the declaration. Candidate: `source ∈ {subject_group, accord, dimension_authority, trust_root, signer_family}`. |
| C4 | **deadline on the cosignatures** | 5 (s5 s87 s95 s101 s109) | `accord:lifecycle:confirmed` must land inside `halt_fuse_secs` of each node's receipt of the halt; a departed signer's cosignature on a roster event counts only inside W. Also the hold window a group sets for collection (CC 3.3.4). Candidate: `within` on the cell, or a pointer to the freshness column. |
| C5 | **value by discriminator** | 5 (s6 s11 s58 s125 s156) | One family, several values, keyed by a segment or a member: `takedown_notice` by basis, `identity:occurrence_revocation` and `identity:occurrence` by identity role (user self against node or agent), `membership` removal in an affiliation with one deciding seat (`deciding_seat_plus_outside`, which also falls on quarantine, slashing and takedown). `membership:{stage}` already carries an informal map; make the map the cell's form. |
| C6 | **declared by a group** | 2 (4 rows: s23 s24) | `goal`, `approach`, `method`, `progress_measure` are cosigned only when a group is the declarer. A condition on the attester kind. |
| C7 | **quorum kinds without a token** | 4 (s22 s84 s92 s195) | WA quorum (the cell itself says "no vocabulary value"); the court's panel of M-of-N independent assessors; the locality-scaled receipt quorum of Policy E; the signer-set kinds `StewardTriple`, `WaQuorum`, `OneOfSix` of `accord_data`. |
| C8 | **two named parties** | 2 (s21 s198) | `retirement:custodian_minted` is cosigned by the operator holding the record and the Wise Authority. The policy table has it (`custodian_replace`, kind `cosigned`, 2/2); the cosign vocabulary does not. |
| C9 | **cosignature that confers and does not gate** | 3 (s7 s10 s88) | On `key:record` an anchor scrub, a root conferral, an accord co-scrub or a steward-triple cross-attestation is a cosignature under CC 2.4 that the row is admitted without. |
| C10 | **cosign rule that is a policy door** | 2 (s72 s74) | `identity:occurrence`: the cell says "no vocabulary value". Token wanted: `two_path(policy_row)`, the cosign rule pointing at the governance cell. |
| C11 | **per-instance option** | 1 (s177) | `moderator_quorum` exists as a token; a community MAY switch it on (full, or live within a window). The cell cannot hold a default and an option. |
| C12 | **set binding** | 1 (s174) | `ballot:moderator_acceptance` is single-signed and binds the election id and the digest of the ballot set it was counted over. |
| C13 | **no model row for a `delegates_to` edge** | 1 (s153) | A duty appointment by anyone but a founder carries the protocol's signatures; the family model has rows for dimensions only. |

### `governance`

| # | need | statements | what is missing |
|---|---|---|---|
| G1 | **which protocol a group kind may name** | 11 (s25 s30 s31 s33 s46 s48 s55 s61 s142 s160 s190) | `founder_only` for a family, a publication and a room's listing, refused above the family, allowed to an affiliation only under the countersign rule; infrastructure: `quorum:M/N` only, M at least 2, founded at N at least M+1, entrenched; `open:self_admit` only on a public community. Stated 11 times in 5 sections, held nowhere as data. Candidate table: group kind and subkind by protocol kind, with the refusal token. |
| G2 | **entrenchment and the amendment door** | 7 (s32 s60 s68 s69 s139 s140 s161) | Changing `consensus_protocol` is a governed act under the protocol's own rule unless `consensus_protocol_entrenched`; there is no policy row for it and no token for entrenched. |
| G3 | **doors with a window and no row** | 4 (s111 s144 s179 s181) | (a) The accord roster change: yes-votes against the standing roster within W. (b) A harm report raised in the room: the default at the window is removal and the act that must land is the keep, the floor applying to the keep; `moderation_action` has `at_window: tallied` and cannot say it. CC 4.5.13 says every door that opens a window is in the table. |
| G4 | **a governed setting that is not five numbers** | 3 (s83 s178 s194) | A ledger's credit limit, the moderator-quorum setting, a room's yes/no on keeping streams: each is "decided under the group's protocol" or "a policy row MAY forbid", with no row and no vocabulary value between `policy_row` and `none`. |
| G5 | **subkind admission predicate** | 4 (s116 s118 s119 s155) | Admission is the protocol AND a predicate of the subkind (location proof for geographic; operator predicates). |
| G6 | **table vocabulary** | 1 (s171), with s175 below | `base: active` means the census expected-active count in the default rows and those who sign presence in the window in `moderation_action`. A token `present` is wanted. Also found on reading the table against CC 4.5.13: the election's floor is "the smaller of two voices and the roster's size" where the row says `2 voices`; the winner's acceptance grace ("a grace the room's policy names") is a policy number with no column. |
| T1 | **the protocol kinds as data** (from NOT_A_CELL) | 15 (s62–s66 s129 s130 s132–s136 s141 s159 s163) | The seven kinds (`founder_only`, `unanimous`, `majority`, `quorum:M/N`, `weighted`, `custom`, `open:self_admit`) are defined in a table in CC 3.3.4 and again as pseudocode in CC 4.4.3.4.2. Nothing binds a kind to the five numbers of the policy table: a widening is "cosigned under the group's consensus_protocol" (s14) and also runs row `community_invite` at enact 2/3 (s191). Which decides is not data. |

## `DISAGREE` rows in full

| column | section | family | verdict | cell_value | cell_source | prose | proposed_value | cc_ref | quote | note |
|---|---|---|---|---|---|---|---|---|---|---|
| cosign_rule | 3.4.1 | accord:invoke:constitutional:{halt_id} | DISAGREE | CC accord (M-of-N); the row carries none (AccordQuorumEvidence is a typed kind) | gap | **One accord holder's signed row** — pre-signable, fired on receipt, no vote ([CC 4.2.1.1](part_4_composition_governance.md#4.2.1.1)); a majority of the standing roster lifts it by `accord:lifecycle:active` ([CC 4.2.6](part_4_composition_governance.md#4.2.6)) | none | CC 3.4.1 | **One accord holder's signed row** — pre-signable, fired on receipt, no vote | s85 [halt]; cell (gap) reads "CC accord (M-of-N)"; prose: one holder's row, no vote. CC 4.2.1.1, 4.2.6 and the policy row accord_halt (1/N fires) support the prose |
| cosign_rule | 4.2.1.1 | accord:invoke:constitutional:{halt_id} | DISAGREE | CC accord (M-of-N); the row carries none (AccordQuorumEvidence is a typed kind) | gap | **A `constitutional` halt is one holder's signature**: a consumer verifies ONE holder's signature over `canonical` against the pinned roster and halts. | none | CC 4.2.1.1 | **A `constitutional` halt is one holder's signature**: a consumer verifies ONE holder's signature over `canonical` against the pinned roster and halts. | s94 [cosign]; as statement 85 |
| cosign_rule | 4.2.1.1 | accord:invoke:constitutional:{halt_id} | DISAGREE | CC accord (M-of-N); the row carries none (AccordQuorumEvidence is a typed kind) | gap | \| `constitutional` \| **one** holder \| a missed fire is the only unrecoverable failure \| | none | CC 4.2.1.1 | \| `constitutional` \| **one** holder \| a missed fire is the only unrecoverable failure \| | s98 [cosign]; as statement 85 |
| cosign_rule | 4.2.1.1 | accord:invoke:drill:{drill_id} | DISAGREE | CC accord (M-of-N); the row carries none (AccordQuorumEvidence is a typed kind) | gap | \| `drill` \| **one** holder \| a drill rehearses the fire path; one that needs more signatures than the fire rehearses something else \| | none | CC 4.2.1.1 | \| `drill` \| **one** holder \| a drill rehearses the fire path; one that needs more signatures than the fire rehearses something else \| | s99 [cosign]; cell (gap) reads "CC accord (M-of-N)"; prose: one holder |
| cosign_rule | 4.2.1.1 | accord:invoke:notify:{notify_id} | DISAGREE | CC accord (M-of-N); the row carries none (AccordQuorumEvidence is a typed kind) | gap | \| `notify` \| **one** holder \| a message from a holder is a message from a holder; what keeps a notify from being mistaken for a halt is the mandatory | none | CC 4.2.1.1 | \| `notify` \| **one** holder \| a message from a holder is a message from a holder; what keeps a notify from being mistaken for | s100 [cosign]; cell (gap) reads "CC accord (M-of-N)"; prose: one holder |
| cosign_rule | 4.2.6 | accord:invoke:constitutional:{halt_id} | DISAGREE | CC accord (M-of-N); the row carries none (AccordQuorumEvidence is a typed kind) | gap | \| **Fire** (`constitutional` kill, [CC 4.2.1.1](#4.2.1.1)) \| **one holder's signed row** — pre-signable; no live set, no vote \| **none** — fires on receipt, latches \| | none | CC 4.2.6 | \| **Fire** (`constitutional` kill, [CC 4.2.1.1](#4.2.1.1)) \| **one holder's signed row** — pre-signable; no live set, no vote \| **none** — fires on receipt, latches | s108 [cosign]; as statement 85 |
| governance | 4.5.13 | ballot:moderator | DISAGREE | null | gap | A room where nobody votes stays locked and the ballot stays open. | policy_row: moderator_election | CC 4.5.13 | There is no reopening as a separate thing: the ballot stays open until a seating lands. | s175 [moderation]; table row moderator_election has at_window `reopens`; prose: "There is no reopening as a separate thing: the ballot stays open until a seating lands". The table's own token for that is `stay_open`. The row is also status `default` where the paragraph is headed normative |

Read together:

1. **`accord:invoke:constitutional`, `:drill`, `:notify`** (six rows). The cell's closed value is "CC accord" (M-of-N), sourced `gap`. CC 3.4.1, 4.2.1.1 and 4.2.6 each say one holder's signature, no count. The rest of the document supports the prose, and so does the policy row `accord_halt` (`1/N fires`). The cell should read `none`; `accord` belongs on `accord:lifecycle:{kind}` for `confirmed` and `active`, whose cell reads `none` from code (6 `FILLS`).
2. **`moderator_election`, `at_window`** (one row). The table says `reopens`. CC 4.5.13 says "There is no reopening as a separate thing: the ballot stays open until a seating lands." The table's own token for that is `stay_open`. The row's status is `default` under a paragraph headed normative.

Smaller mismatches recorded in notes and not raised to `DISAGREE`:

- `community_remove` has floor `—`; CC 4.4.3.4.2 and 4.5.13 say a removal "runs under the floor". Enact above 2/3 yields two voices at any base of two or more, so the outcome agrees and the expression does not (s131, s138).
- `objection:{state}` governance cell lists only the two self-roster rows; CC 4.5.13 says votes for every door travel on `objection:{state}` and the lift counts `objection:raised`. No statement in this lane names the family.
- `trust:{job}:{version}` cosign cell names the charter witness quorum; the text's cosign rule on a keyless family root is the roster reaching its protocol (s89, s90).
- `transport:canonical_rebind`, `takedown_notice:{basis}`, `identity:occurrence_revocation`: the cells agree with the text in free words outside the closed vocabulary.
- CC 3.2 (the federation-halt row of its table) still carries the phrase "the accord's roster-keyed asymmetry".

## Sections where every statement was `AGREE` or `FILLS`

These could become a pointer to the table.

- `cosign_rule`: CC 2.3.2.4 (2), CC 3.1.1 (1), CC 3.3.1 (2), CC 3.3.2 (1), CC 3.3.7 (1), CC 3.4.10 (1), CC 4.2.1 (1), CC 4.2.1.3 (2), CC 4.4.3.2.3 (2), CC 4.4.3.4.3 (2), CC 4.4.3.5.3 (1), CC 4.4.3.5.6 (1), CC 4.5.2.3 (1)
- `governance`: CC 3.3.6.3 (1), CC 4.5.4 (2)

Of these the strongest are CC 4.2.1.3 (two statements that `lifecycle:active` is cosigned by a strict majority of the standing roster, once the `accord` token is on that cell), CC 3.3.6.3's policy paragraph (the two self-roster rows, already equal to the table) and CC 4.5.4's two election statements (once `ballot:moderator` names `moderator_election`). The consent sections (2.3.2.4, 3.3.1, 3.3.7, 4.4.3.4.3, 4.4.3.5.3, 4.4.3.5.6, 4.5.2.3) agree because a bilateral pair is two single-signed rows and no cosignature.

## Proposed cells (`FILLS`)

| family | column | proposed | from |
|---|---|---|---|
| `accord:lifecycle:{kind}` | cosign_rule | `accord` (kinds `confirmed`, `active`) | CC 3.4.1, 4.2.1.1, 4.2.1.3, 4.2.6 |
| `accord:*` | cosign_rule | `accord` (standing acts) | CC 4.2.6 |
| `licensure:{authority_id}` | cosign_rule | `group_consensus_protocol` (source: the authority in the dimension) | CC 2.4.1.2.1, 3.3.9 |
| `mesh_config:{key}` | cosign_rule | `group_consensus_protocol` (source: the root; durable settings) | CC 4.2.1 |
| `cosign:{state}` | cosign_rule | `none` | CC 3.1.3 |
| `lineage_witness:{stage}` | cosign_rule | `none` | CC 3.4.10 |
| `ballot:moderator` | cosign_rule | `none` | CC 4.5.13 |
| `ballot:moderator` | governance | `policy_row: moderator_election` | CC 4.5.4, 4.5.13 |
| `membership:{stage}` | governance | `policy_row: community_invite, community_remove` | CC 4.4.3.4.2, 4.5.13 |
| `moderation:{allegation_type}` | governance | `policy_row: moderation_action` | CC 4.5.13 |
| `accord:invoke:constitutional:{halt_id}` | governance | `policy_row: accord_halt` | CC 4.5.13 |
| `retirement:{state}` | governance | `policy_row: custodian_replace` | CC 4.5.13 |
