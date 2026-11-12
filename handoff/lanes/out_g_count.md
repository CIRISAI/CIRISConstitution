# Lane G: how a body's act is counted

Encoded rows: `out_g_count.tsv` (116 rows from 113 reader rows). This file holds the design
(section 2), what could not be encoded (4), where the data lives (5) and what can now be
proved (6).

## 1. What was collected

All 491 `RICHER` rows of the four tables were read. 102 ask for this concept. 89 are encoded:
66 of the 73 in `out_f_cosign.tsv` (needs C1 to C13, G1 to G4, G6), 13 in `out_f_erasure.tsv`,
9 in `out_f_lifecycle.tsv` and 1 in `out_f_audience.tsv`. 13 are not (section 4). Added to
the encoded rows, because the launch message names them: 15 `NOT_A_CELL` rows that define the
protocol kinds (the reader's T1) and 9 `AGREE` or `FILLS` rows the reader tagged
`need:protocol_source`, `need:count_set` or `need:per_discriminator`. The verdict of each
source row is in the TSV's `source_table` column.

In the TSV a `value` begins with the piece of data it is a value of: `count` (a cell of the
column, 2.1), `policy ROW:` (typed cells of a policy row, 2.2), `protocol KIND:` (cells of
the protocol table, 2.3) or `admit GROUP KIND:` (a row of the admissibility sheet, 2.3).
Several joined by ` ; ` are all stated by the one statement.

## 2. The design

One sentence: **a family's cell names a door; a door is a row of the policy table read
against a group; the policy row's `enact` may say `protocol`, and then the group's declared
kind supplies the rule from a seven-row protocol table.** Nothing parallel to the policy
table is invented. Three pieces of data, one column.

| piece | file | what it holds |
|---|---|---|
| the column `count` | `manifests/family_model.json` | per family: which door, for which rows of the family, read against whose roster |
| the policy table, six typed columns added | `constitution/governance_policy.tsv` | per door: the count set, the instant, how voices travel, the five numbers |
| the protocol table | `constitution/consensus_protocols.tsv` (new, built by `tools/build_governance_policy.py`) | per `consensus_protocol` kind: the typed rule that fills `enact`; and per group kind: which kinds it may name |

`cosign_rule` and `governance` stop being authored. Both become views of `count`:
`cosign_rule` is `none` when every arm's door is `none`, else the door names; `governance` is
the policy rows the arms name. The 167 families whose cells read `none` have `count = none`.

### 2.1 The column `count`: grammar

```
count  := arm { " ; " arm }            first arm whose guard holds decides
arm    := [ guard " => " ] doors       the last arm has no guard
guard  := test { " & " test }
test   := key "=" value { "|" value }
doors  := door { " + " door }          at most one door without "!confers"
door   := "none" | "shut" | ROW [ "@" source ] [ "!" mode ]
mode   := "confers" | "result"
```

`ROW` is a `family` value of `governance_policy.tsv`. An arm with no `verb` test binds every
verb of the family, which is CC 2.4.1.1 rule 0 (a cosigned row is retracted by the same
quorum) with no further data.

**Doors**

| token | means | the kernel does |
|---|---|---|
| `none` | one signature carries the row | counts nothing; the signer rule alone decides admission |
| `shut` | no count opens this arm | refuses the row; where the guard is on `changes=consensus_protocol` it emits `hard_case:family_consensus_protocol_violation` or `hard_case:community_consensus_protocol_violation` by group kind (CC 3.3.4) |
| `ROW@source` | the act runs policy row `ROW` over the roster `source` resolves to | admits the row at once (CC 4.5.13, a policy that is not one voice); folds the voices it holds for the act's quorum key; calls `decide(ROW, base, approvals, objections, elapsed)`; moves the object only on `lands` |
| `ROW@source!confers` | a counted cosignature the row is admitted without | never gates; when the fold over the scrubs meets `ROW` it sets the conferred standing in the view, and unsets it when a later roster fold no longer meets it |
| `ROW@source!result` | a single-signed row that binds the set a count was taken over | reads the bound set digest from the row; refuses unless it holds exactly that set, the count of `ROW` over it names the signer, the set meets `ROW.floor`, and `ROW.window_secs` has passed since this node first held the opening (CC 4.5.13, one result on every node) |

`shut` is the existing token of `emitter_class`. `!confers` and `!result` are new: nothing
existing says "counted and not required" or "single-signed over a counted set".

**Sources** (whose roster, and whose declared protocol, the row is read against)

| token | resolves to | the kernel reads |
|---|---|---|
| `subject_group` | the group the row is about (CC 2.4) | the group id in the row's cohort or subject; that group's roster fold and record |
| `signer_group` | the group the signer signs for (a group's goal, a keyless family root's conferral) | the group the attesting key resolves to as authority |
| `dimension_authority` | the authority named in the dimension segment (CC 2.4.1.2.1) | the `{authority_id}` segment as a group id |
| `accord` | the accord family the node is rooted to | the pinned accord roster |
| `trust_root` | the root's conferring roster (CC 4.2.1) | the root community's roster fold |
| `self` | the live key roster of the signer's fedID (CC 3.3.6.3) | the self-roster fold |
| `conferrer` | the group that conferred the seat or key the row is about (CC 4.3, CC 4.5.13 recall) | the roster of the group that signed the conferring row |

All but `conferrer` and `signer_group` are the reader's candidates; `subject_group`,
`accord` and `dimension_authority` are the three CC 2.4 names. Omitted `@source` means the
row needs none (a named pair).

**Guard keys** (each a fold or a row member the kernel already has)

| key | values | read from |
|---|---|---|
| `leaf[.segment]` | a value of the family's placeholder (`leaf=removal`, `leaf.job=charter`) | the row's dimension, parsed by the registry |
| `verb` | the five verbs | the row type |
| `signer` | a role token of `transitions.json` (`founder`, `steward`, `holder`, …) | the signer's standing fold |
| `identity` | `user`, `node`, `agent` | `identity_type` of the identity the row is about |
| `declarer` | `person`, `group` | whether the `authority_id` the row names is a group that names itself (CC 3.1.9.7) |
| `seat` | `founder`, `member`, `node` | the role of the seat the row gives or takes |
| `group` | `family`, `community[/subkind]`, `affiliations`, `accord`, `publication` | the source's record kind and `cohort_subkind` |
| `roster` | `founding`, `live`, `stalled` | the source's roster fold: no prior version held; T7 live; T7 stalled |
| `seats` | `one`, `many` | the number of deciding seats in the source's fold (CC 4.4.3.2.8) |
| `root` | `keyed`, `keyless` | whether the root the row charters or confers under holds a key (CC 3.4.5) |
| `changes` | a member name of the family's body | the difference between the row and the version it replaces |
| `record.<member>` | a value of a member of the source's signed record | the source's current record |
| `class` | `entrenched`, `liveness` | the decision class of CC 4.3's denominator rule |

`group`, `roster`, `seats`, `root`, `changes`, `class` and `declarer` are new key names over
states the text already names. No value is free text: every value is a registry leaf, a role
token, a record member or one of the closed words above.

### 2.2 The policy table: six typed columns

`standing_set` is free text today ("the roster the change is about"). It stays as the label.
The kernel reads these:

| column | grammar | tokens: meaning; what the kernel does |
|---|---|---|
| `count_set` | `role { "+" role } [ "-" excl ]` | `member`, `founder`, `holder`, `moderate`, `wa`, `self`, `operator`, `steward` (role tokens of `transitions.json`): the keys the source's fold seats in that role; the kernel builds the set from the fold. New: `deciding` (an affiliation's officers under its protocol), `outside` (the designated official, or a `review` holder of the conferring body, not a deciding seat), `assessor` (a member of a panel), `joiner` (the key a widening names). `+` is union, one voice each (`operator+wa`). `excl`: `target` (the key the act is about), `proposer` (today's `cancel_over: others`), `node` (a key whose `identity_type` at its seating row includes `node`); the kernel removes those keys before counting. A value of `protocol` means the set comes from the protocol table and the admissibility row. |
| `voice` | `person` \| `key` | `person`: the kernel folds signatures to one voice per fedID, agreeing voices one, disagreeing voices none until one is withdrawn. `key`: each key is a voice (the self roster only). |
| `base` | `standing` \| `active` \| `present` | `standing`: the size of `count_set` at `counted_at`. `active`: the census law `base(N)` (existing). `present` (new, G6): the members of `count_set` who signed a presence or vote row over the proposal inside the window; the kernel counts those rows and nothing else. |
| `counted_at` | `signed` \| `decision` \| `act` \| `founding` | `signed`: the set as the receiver's fold gives it at the row's signed instant (CC 2.4); a signer no longer in the set at receipt counts only while that instant is inside W, else the kernel refuses `asserted_at_stale` (CC 3.3.4). `decision`: the set as it stands when the fold is evaluated; a voice from a key since removed counts for nothing (CC 3.3.6.3; the election's electorate). `act`: the set as it stood at the first-held instant of the act the count answers; a member seated after counts for nothing (`moderation_overturn`). `founding`: the set the record itself lists, there being no earlier fold. |
| `voices` | `scrubs` \| `objection` \| `ballot` (joined by `\|`) | where the kernel finds the voices. `scrubs`: `additional_scrubs[]` on the one cosigned row, and `cosign:signature` rows for its quorum key while held as `cosign:pending`. `objection`: `objection:{state}` rows naming the proposal; `proposal` and `assent` are approvals, `raised` an objection. `ballot`: `ballot:moderator` rows under the election id. |
| `target_silent` | `yes` \| `no` | `yes`: the reverse path lands only if the kernel holds no row signed by the target and first held inside the window. |

Changes to existing columns:

- `enact`, `cancel`, `floor` gain four typed rule kinds in `rule_of`: `protocol` (resolve from
  the source's declared kind, 2.3); `all` (every member of `count_set`); `all_and_majority`
  (every member of the removal set, and that number a strict majority of the undiminished
  set); `voices_capped:n` (the smaller of `n` and the size of `count_set`: the election's
  floor in a small room and `quorum:M/N` below M are the same rule).
- `at_window` gains `removes`: the keep did not land, the reported item is removed. The
  existing `cancelled`, `stay_open`, `lapsed`, `tallied` stand.
- `base` gains `present` as above.

Rows to add (each a door the text states and the table lacks). Windows are classes the table
already has.

| row | kind | count_set | voice | base | counted_at | enact | floor | voices | window | at_window | from |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `cosigned_act` | cosigned | protocol | person | standing | signed | protocol | — | scrubs | standing_72h (the hold window; a group may set longer) | cancelled | CC 2.4, 3.3.4 |
| `group_founding` | cosigned | member (the admissibility row may narrow it) | person | standing | founding | all | — | scrubs | none | — | CC 3.1.3.2 |
| `protocol_amend` | cosigned | protocol | person | standing | signed | protocol | — | scrubs | standing_72h | cancelled | CC 3.3.4, 4.4.3.4.2 |
| `accord_roster_change` | two_path, no reverse path | holder | person | standing | signed | strict_majority | — | objection | standing_72h | cancelled | CC 4.2.6 |
| `accord_confirm` | cosigned | holder | person | standing | signed | strict_majority | — | scrubs | fuse_24h | lapsed | CC 4.2.1.1 |
| `accord_majority` | cosigned | holder | person | standing | signed | strict_majority | — | scrubs | none | — | CC 4.2.1.3, 4.2.6 |
| `harm_report_keep` | mirror | member | person | present | decision | role:moderator\|steward at 1 | strict_majority | objection | ruled_48h | removes | CC 4.5.13 |
| `moderator_quorum_full` | cosigned | moderate | person | standing | signed | all | — | scrubs | none | — | CC 4.5.13 |
| `moderator_quorum_live` | cosigned | moderate | person | present | decision | protocol | — | scrubs | (the group's stated period) | tallied | CC 4.5.13 |
| `wa_quorum_standing` | cosigned | wa | person | standing | signed | protocol | — | scrubs | none | — | CC 4.3 |
| `wa_quorum_live` | cosigned | wa | person | present | decision | protocol | — | scrubs | none | — | CC 4.3 |
| `capacity_panel` | cosigned | assessor | person | standing | signed | protocol | — | scrubs | none | — | CC 3.4.12 |

Existing rows filled from the text: `custodian_replace` `count_set=operator+wa`;
`affiliation_member_action` `count_set=deciding+outside`; `self_roster_add`/`_evict`
`count_set=self` (`self-target` on evict), `voice=key`, `counted_at=decision`,
`voices=objection|scrubs`, `target_silent=yes` on evict; `moderation_action` `base=present`;
`moderation_overturn` `counted_at=act`; `moderator_election` `voice=person`, `voices=ballot`,
`counted_at=decision`, `floor=voices_capped:2`; `community_remove` `floor=voices_capped:2`;
`accord_halt` `count_set=holder`.

`cosigned_act@subject_group` is today's token `group_consensus_protocol`, and
`accord_majority@accord` is today's `accord`. The old tokens become aliases.

### 2.3 The protocol table: how a kind binds to the numbers

A protocol kind is **a typed rule for the `enact` cell and a count set**. It is not a second
decision shape. Where a policy row's `enact` reads `protocol`, the kernel reads
`consensus_protocol` from the source's current record, looks the kind up here, and uses its
rule and set; the row supplies the window, `at_window`, `voices` and `counted_at`.

| kind | count_set | enact | on a removal | reverse path | the kernel does |
|---|---|---|---|---|---|
| `founder_only` | founder | role:founder at 1 | (not stated; section 4) | no | counts one scrub by a founder in the set at the signed instant |
| `unanimous` | member | all | set `member-target`, rule `all_and_majority` | no | counts scrubs against the whole set; on a removal drops the target and adds the majority test |
| `majority` | member | strict_majority | the same, target counted | no | `2 · approvals > size` |
| `quorum:{m}/{n}` | member | voices_capped:m | the same | no | `approvals >= min(m, size)`; `n` is read by nothing |
| `weighted:{rubric}` | member | weight:rubric | the same | no | sums the rubric's weight for each signer against its threshold; with no rubric held the door is closed |
| `custom:{id}` | — | predicate:id | — | no | calls the predicate registered under `id`; with none held the door is closed |
| `open:self_admit` | joiner (widening) | joiner | row `community_remove` | no | on a widening naming one key, that key's own signature is the group's side; a removal runs the named row |

`weight:` and `predicate:` are new rule kinds and the only two the kernel cannot evaluate
from the table alone. `reverse path: no` is the reading of `formal/membership` (a held change
lands when the protocol is met, otherwise it expires). It is the decision asked of the lead
(section 4, C-1).

**Which kinds a group may name** (the reader's G1; second sheet of the same file). The
kernel reads it at two doors: a founding record and a `protocol_amend`. A pair with no
`allowed` row is refused.

| group | kind | verdict | conditions | refusal |
|---|---|---|---|---|
| `family/*` | all seven less `open:self_admit` | allowed | | |
| `family/conferring` | `quorum` | allowed | `founding_margin=1` | |
| `publication/*` | `founder_only` | allowed | | |
| `community/listing` | `founder_only` | allowed | | |
| `community/*` | `founder_only` | refused | | `federation_community_consensus_protocol_violation` |
| `community/public` | `open:self_admit` | allowed | | |
| `*/*` (any other) | `open:self_admit` | refused | | (the text names none; the same token proposed) |
| `community/infrastructure` | `quorum` | allowed | `m_min=2` `founding_margin=1` `entrenched=required` `count_set=founder-node` | |
| `community/infrastructure` | `founder_only`, `unanimous`, `majority` | refused | | `federation_community_consensus_protocol_violation` |
| `community/geographic` | (as `community/*`) | allowed | `count_set=member` | |
| `affiliations/*` | `founder_only` | allowed | `with_row=affiliation_member_action` `count_set=deciding` | |
| `affiliations/*` | others | allowed | `count_set=deciding` | |
| `accord` | `majority` | allowed | `entrenched=required` `count_set=holder` | |

Condition tokens: `m_min=n` (the kind's `m` is at least `n`); `founding_margin=k` (the
founding record lists at least `m + k` members of `count_set`); `entrenched=required` (the
record's `consensus_protocol_entrenched` is `true`); `count_set=…` (replaces the protocol
row's set for this group); `with_row=ROW` (acts against a member run `ROW` while `seats=one`).
The kernel checks each as an integer or boolean comparison on the record.

### 2.4 Whose protocol applies: worked cells

| family | `count` |
|---|---|
| `group:roster` | `roster=founding => group_founding@subject_group ; signer=holder & changes=own_seat => none ; changes=admission_quorum_basis => shut ; changes=consensus_protocol & record.consensus_protocol_entrenched=true => shut ; changes=consensus_protocol => protocol_amend@subject_group ; group=accord & changes=members => accord_roster_change@accord ; cosigned_act@subject_group` |
| `membership:{stage}` | `leaf=proposal\|acceptance\|resignation => none ; leaf=widening & roster=stalled & seat=founder => none ; leaf=removal & group=affiliations & seats=one => affiliation_member_action@subject_group ; cosigned_act@subject_group` |
| `accord:lifecycle:{kind}` | `leaf=confirmed => accord_confirm@accord ; leaf=active => accord_majority@accord` |
| `accord:invoke:constitutional:{halt_id}` | `accord_halt@accord` |
| `identity:occurrence` | `identity=user => self_roster_add@self ; none` |
| `identity:occurrence_revocation` | `identity=node\|agent => none ; identity=user => self_roster_evict@self` |
| `takedown_notice:{basis}` | `leaf=steward_purge => cosigned_act@trust_root ; group=affiliations & seats=one => affiliation_member_action@subject_group ; none` |
| `licensure:{authority_id}` | `declarer=group => cosigned_act@dimension_authority ; none` |
| `goal:{scale}` and its three kin | `declarer=group => cosigned_act@signer_group ; none` |
| `retirement:{state}` | `leaf=custodian_minted => custodian_replace ; none` |
| `ballot:moderator` | `moderator_election@subject_group` |
| `ballot:moderator_acceptance` | `moderator_election@subject_group!result` |
| `moderation:{allegation_type}` | `record.moderator_quorum=full => moderator_quorum_full@subject_group ; record.moderator_quorum=live => moderator_quorum_live@subject_group ; moderation_action@subject_group` |
| `key:record` | `none + cosigned_act@trust_root!confers + accord_majority@accord!confers` |
| `wa_adjudication:{state}` | `leaf=petition => none ; class=entrenched => wa_quorum_standing@subject_group ; wa_quorum_live@subject_group` |

"A different protocol by stage or by basis" is the guard. "The group that conferred a seat"
is `@conferrer`. "The group the row is about" is `@subject_group`.

## 4. What could not be encoded

**Needs another column** (5 rows)

- s116, s119 (CC 4.4.3.2.3): admission is the protocol and a subkind predicate (a
  `location_proof` inside the constraint). The count is encoded; the predicate is a guard on
  another row's existence (the guard lane).
- e319 (CC 4.4.3.4.4), l4 (CC 2.1): the witnessed head, and a charter change the directory
  before it must witness. Both count a witness set. One more `count_set` role, `witness`,
  would hold them and the existing `trust:{job}:{version}` cell ("charter witness quorum");
  it was not added because the fold that seats a witness is the fold lane's.
- s194 (CC 5.3.3.2.5): "the room's policy row MAY forbid keeping in that room". A yes/no
  value of a room's record, not a count. Who decides it is `cosigned_act@subject_group` once
  the setting has a member name.

**Is really a general rule** (2 rows, both a property of every `count_set`)

- s81 (CC 3.3.9): "A delegated holder never stands in for the `consensus_protocol` on a roster or config change".
- s197 (CC 6.1.8): a chain walk yields "trust+serve standing only".
  The kernel rule: a key is in a count set only by its own seat row in the source's fold,
  never by a `delegates_to` edge and never by a chain. Stated once at the kernel; a
  property in section 6 holds it.

**A count inside a row's meaning, not a body's act** (2 rows)

- e43 (`attestation:registry_consensus`, two of three registry sources) and e153
  (`witness_diversity`, N = 3): the row reports a tally its emitter took. No signer is
  counted at the door. These belong to the derived-check column.

**Ambiguous in the text** (4 rows, and 6 values inside encoded rows)

- s84 (CC 3.3.13): `accord_data` is "Multi-sig signed (HumanityAccord / StewardTriple / WaQuorum / OneOfSix)".
  `HumanityAccord` is `accord_majority@accord` and `WaQuorum` a `wa_quorum_*` row;
  `StewardTriple` and `OneOfSix` name sets no other section defines, and there is no
  registry family.
- s195 (CC 5.3.3.6): "Policy E … locality-scaled". The threshold is a function of locality
  with no table; it needs CC 4.4.3.1 as data before a row can name it.
- l47 (CC 3.1.3) `transport:canonical_rebind`: the cell says "holder quorum (CC 5.3.4)". The
  text does not say whether that is the accord's strict majority (`accord_majority@accord`)
  or the canonical community's `quorum:2/3` over its founders (`cosigned_act@trust_root`).
  The two differ once the accord grows.
- l136 (CC 3.3.13): "editor-consensus" for an encyclopedia article. No set and no rule.
- Inside encoded rows: the rubric of `weighted:{rubric}` has no shape; `custom:{id}` has no
  registry of predicates; `moderator_quorum_live`'s period and the election's acceptance
  "grace the room's policy names" are numbers with no default (a column `accept_grace_secs`
  is wanted and cannot be filled); the WA and panel thresholds are "the quorum's" with no
  number; `record.moderator_quorum`, `record.durable` and the charter member that grants an
  affiliation's members a vote are member names the text does not fix; a harm report has no
  wire discriminator that tells it from a change proposal, so the guard that selects
  `harm_report_keep` cannot be written.
- `founder_only` on a removal: CC 3.3.4 gives founders "the sole admission authority" and
  says nothing of removal; `formal/membership` reads that a coerced founder can remove.

**Contradicts another statement** (both quoted)

- **C-1, which decides a widening: the protocol or the row.**
  CC 3.3.4: "A `membership:widening` cosigned under the CURRENT family's `consensus_protocol` seats the joiner."
  CC 4.5.13 and the table: "community invitation … and removal", row `community_invite`,
  `enact 2/3`, `floor 1/3`, `reverse_path yes`, base `active`.
  A room declared `majority` lands a widening at more than half of its current members under
  the first and at more than two thirds of the expected-active count under the second, and
  the second can land it at the window on a third of the voices, which the first never does
  (`formal/membership`: a held change "expires after its hold window"). The encoding takes
  the first: `enact=protocol`, no reverse path, and `community_invite`'s fractions unused by
  any declared kind.
- **C-2, the corridor against absolute M.**
  CC 4.5.13: enact is "a fraction of the base, strictly more; never below a strict majority".
  CC 4.4.3.4.2.1: "A `quorum:2/3` collective that grows to 5 members still admits at **2** signatures".
  Two of five is below a strict majority. If the corridor binds a declared protocol,
  `quorum:M/N` is out of it in any room larger than `2M − 1`.
- **C-3, the base.** CC 3.3.4 `majority`: "> 50% of current members must sign." The policy
  rows for the same door have base `active`, the census composite, which above twelve
  members is smaller than the roster. Encoded as `base=standing` on `cosigned_act`.
- **C-4, `community_remove`'s floor.** CC 4.4.3.4.2: "A removal under `admission: open` runs under the floor of [CC 4.5.13]".
  The row's floor cell is `—`. Encoded as `floor=voices_capped:2`.
- The reader's two `DISAGREE` findings stand and are not repeated: the `accord:invoke:*`
  cells (one holder, not M-of-N) and `moderator_election`'s `at_window` (`reopens` against
  "There is no reopening as a separate thing").

## 5. Where it lives

**The column lives in the family model. The numbers stay in the policy table. The kinds get
their own small table. Each transition's `policy` is derived.**

- *Family model, not `transitions.json`.* A count belongs to the act's quorum key, and CC
  2.4.1.1 rule 0 makes every verb on a cosigned row run the same count. A per-transition
  member would repeat one value under each verb and could drift. `tools/build_transitions.py`
  already derives each transition's `policy: {policy, rows, stages}` from the family's
  governance cell; it now derives it from `count`, an arm with a `leaf` or `verb` guard
  becoming a `stages` entry. The 445 `selfAct` cells are `count = none`.
- *Policy table, extended.* The table already has the generator, the pin, the vectors, the
  typed `rule_of` and a TLC instance per row. `count_set`, `voice`, `counted_at`, `voices`
  and `target_silent` are columns of a door, not of a family: `self_roster_evict` is pointed
  at by two families and must count the same set for both. The generator gains the four rule
  kinds and a check that every typed column parses.
- *Protocol table, new.* A kind is neither a family nor a door: seven rows keyed by kind and
  thirteen keyed by group kind. Today it is stated eleven times in five sections (the
  reader's G1) and twice as a table and pseudocode (T1). It sits beside the policy table and
  is built and pinned with it, so a row whose `enact` is `protocol` has rule vectors per kind.

## 6. What can now be proved

Stated over the data, for every family, in the manner of `formal/event_lifecycle`.

1. **Every count is total and reproducible** (`count_is_total`). For every family, every arm
   and every protocol kind the admissibility sheet allows the arm's source: the door
   resolves to one policy row whose `count_set`, `voice`, `base`, `counted_at` and `voices`
   are tokens, and whose `enact` is a typed rule that returns an integer for every set size
   from 1 up. So `decide` is a function of the rows held and two nodes holding the same rows
   reach the same verdict. Today this cannot be stated: fourteen cells are prose and the
   denominator is a label. The check also reports every arm that reaches `weight:` or
   `predicate:`, which are the only places the property fails.

2. **No lone voice moves a roster** (`no_lone_voice`). For every arm of every family whose
   row changes who is in a set (`membership:{stage}`, `group:roster`, the accord's roster),
   and every protocol kind allowed to the arm's group kind: at every set size of two or more,
   the rule's count is at least two distinct voices of `count_set`, or the arm is one of a
   closed list of exceptions that the data names (`founder_only` where the sheet allows it;
   the stalled-founder widening; a holder's own seat). CC 4.5.13's floor of two voices is
   then a theorem about three tables, and each exception is a row someone signed off.
   C-2 above is what this check first reports: it passes for `quorum:{m}` only with
   `m_min=2`, which the sheet states for infrastructure and for no other community.

3. **The set that is counted cannot be chosen by the counted** (`count_set_is_prior`). For
   every door whose act changes its own `count_set` (a removal, an eviction, a roster change,
   a protocol amendment): `counted_at` is `signed` or `act`, or the target is excluded by
   `-target`, or `target_silent=yes`. No such door reads `base=present` for its `enact`. This
   is CC 4.2.6's "no second roster" argument and CC 4.3's pre-change denominator as one
   lookup over the policy table.
