# Lane G, concept: what a superseding or changing row may do to the thing it changes

Column name: **`change`**. Encoded rows: `out_g_lifecycle.tsv` (69 rows, 50 distinct (family, value) pairs, 19 families).

Read first: CC 2.4.1.1 (who may take a row back; forward only; the one reach behind), CC 3.5.1
(precedence among concurrent composers), CC 4.5.13 (the state processor), `formal/event_lifecycle`.

Three needs of the lifecycle reader are covered: N-SUPC (a bound on a supersede), N-ROT (the key
effect of a roster change by tier) and the cascade part of N-ENDS, N-REACH and N-EFFECT (what a
change does to rows that depended on the old one). Rows of the cosign, audience and erasure tables
that say the same kind of thing are folded in (entrenchment, the recovery version, the T7 bound,
the file under a widened directory, the key-grant cascade).

## 2. The column

### Grammar

```
change  := item ( " ; " item )*
item    := on guard? ": " clause ( ", " clause )*
on      := verb | leaf
guard   := "[" atom ( "&" atom )* "]"
clause  := "by=" signer
         | "link=" ( "ranked:" | "chained:" ) member
         | "field=" member ":" dir
         | "reach=" reach
         | "after=" family
         | "cascade=" family "/" rel ":" effect
         | "key=" keyeffect
         | "refuse=" token
```

No production takes free text. `family` is a registry family name or `*`. `member` is a wire member
name of the family's body or envelope (the `body` column or CC 2.6.1.7 must list it; a check
enforces that). `token` is a refusal token the text names. `verb` is one of the five
(`attest`, `authorize`, `replace`, `withdraw`, `recant`). `leaf` is a closed leaf of the family
(`widening`, `removal`, `resignation`, `expired`, `custodian_minted`), as the `stages` of
`transitions.json` already name them.

An item with a guard overrides the unguarded item of the same `on` where the guard holds. A family
with no `change` value takes the default row:
`replace: by=same_attester, link=ranked:references_attestation_id, reach=own_prior ; withdraw: cascade=*/ref:stand`.

### Tokens

`on` and `guard`

| token | means | the kernel does |
|---|---|---|
| verb or leaf | the transition this item governs | selects the item when the arriving row's transition has that verb, or its dimension resolves to that leaf |
| `entrenched` | the held head's `consensus_protocol_entrenched` is true | reads the member of the head it holds for the row's group |
| `stalled` | the roster fold of the group reads stalled (CC 3.2 T7) | reads the fold state; no new fold |
| `grade:trust_root` | the group is trust-root-grade (CC 3.2) | reads the head's grade |
| `subkind:<cohort_subkind>` | the group's `cohort_subkind` | reads the head's member |
| `scope:<s>` (`\|` joins several) | the `cohort_scope` of the group the row changes, one of the seven | reads the head's scope |
| `seat:<role>` | the row's subject holds that seat; role tokens of `transitions.json` | reads the standing fold |
| `last:<role>` | after this row the fold holds no live seat of that role, no admitted successor and no `dissolves_at` | runs the fold with the row appended and counts |
| `ephemeral` | the record carries a `valid_until` (CC 5.3.3.2) | reads the head's member |
| `axis:<axis>` | the key-grant axis the effect concerns | selects by axis |
| `cosigned` | the target row carries `additional_scrubs[]` | reads the target row (CC 2.4.1.1 rule 0) |
| `recovery` | the row is the holder's recovery version or the T7 recovery widening | reads the row's kind. **Invented**: the text names the two rows and no token |

`by=`: who may sign the changing row, relative to the row it changes

| token | means | the kernel does |
|---|---|---|
| `same_attester` | the signer of the old row (existing token) | compares `attesting_key_id` of the two rows; refuses otherwise |
| `none` | no row of this verb is admitted against the family (existing token) | refuses, `federation_withdraws_not_admitted` for a withdraw |
| `cosigned` | the quorum of the family's protocol, judged on the fold **before** the change (existing token) | counts `additional_scrubs[]` against the protocol of the held head at the row's signed instant |
| `cosigned_prior` | the set that witnessed the old row witnesses the new one | verifies the cosignatures against the directory of the parent head, never the new row's own. **Invented**: CC 3.2 says "witnessed by the directory before it" |
| `committed_key` | a key other than the one replaced, whose record hashes to the commitment the charter holds for that holder | hashes the signer's key record as CC 2.1 states, compares with the charter's entry for the holder; refuses the replaced key itself. **Invented** |
| `substrate` | the substrate emitter class (existing emitter class) | checks the signer's `identity_type` |

`link=`: how the new row names the old and how rivals are settled

| token | means | the kernel does |
|---|---|---|
| `ranked:<member>` | the member names the old row; concurrent successors are ranked by CC 3.5.1 | applies rules 1 to 3; both rows stay stored |
| `chained:<member>` | the member must equal the digest of the head this node holds | compares; refuses a row that names anything else, whatever its `asserted_at`. CC 3.5.1 rule 2 is off for the family, and a second child of one head is `lineage_fork_attempt` |

`field=<member>:<dir>`: one way a member may move between the old row and the new

| dir | means | the kernel does |
|---|---|---|
| `any` | may change, and only by this transition | no comparison; the member's value in the fold is read from the latest admitted row only |
| `frozen` | must be equal | compares the two values; refuses on a difference |
| `shrink` | a set that may lose elements and gain none | set difference new minus old must be empty |
| `grow_signed` | a set that may gain only keys that signed this row | every element of new minus old is the attester or in `additional_scrubs[]` |
| `lower` | an ordered value that may fall and never rise; absent sorts lowest | compares; the fold takes the minimum across versions (CC 2.4.1.1) |
| `no_weaker` | a protocol that may not be weakened | compares under a strength order. **The order is not data today**, see section 4 |
| `as_attest` | the new value passes the bound a first row passes | runs the attest transition's own check on the member |

All seven `dir` tokens are invented; the text states each rule in words and the model's
`supersedes` part has only `same_attester | none`.

`reach=`: which rows the change displaces

| token | means | the kernel does |
|---|---|---|
| `own_prior` | the signer's own earlier version (default) | the fold marks the referenced row `superseded` |
| `other_attester` | a row another party signed, named by the link or by subject | marks that row `superseded` though the signers differ; admitted only with the item's `by` |
| `below_seq` | every detail row of the same ledger with a lower sequence number | the fold reads from this row forward; the rows below are no longer needed above the noise floor |
| `whole` | the row entire, never a part of it | a withdraw takes every member of the body out; a narrower value is a replace |

`after=<family>`: the change is admitted only if the node holds an admitted row of that family
about the same subject, newer than the row being replaced. The kernel looks the row up and refuses
with the item's `refuse` token when it is absent.

`cascade=<family>/<rel>:<effect>`: what the change does, in the fold, to rows that depended on the
old one. Nothing is written or deleted; each is a read-time verdict from the change's signed
instant.

| rel | the dependants are rows of `<family>` that |
|---|---|
| `by` | the changed key or record signed or issued |
| `under` | sit in the cohort, or under the authority, of the changed record |
| `about` | name the changed row or its subject |
| `ref` | cite the changed row in `references_attestation_id` or `evidence_refs` |
| `over` | are the record the changed row sits under (the cascade runs upward) |

| effect | means | the kernel does |
|---|---|---|
| `stand` | unaffected | nothing; stated so that the absence of a cascade is data |
| `lapsed` | stands for what was done under it, reads `lapsed` for every later use | the fold returns `lapsed` for the dependant at any instant at or after the change |
| `withdrawn` | reads as withdrawn at that instant, no signer needed | the fold returns the state `withdrawn` of `transitions.json` |
| `stop` | rows before the instant stand, a row after it is refused | the door refuses a new dependant row signed after the change |
| `void_after:<member>` | void back to the bound the member carries | a dependant is valid iff its `asserted_at` precedes the minimum of the member across all changing rows |
| `discharged` | the timed obligation folded from the dependant is met | the window fold closes without a breach row |
| `forfeited` | the stake the dependant records is lost | the fold returns `forfeited`. The text's own word (CC 3.1.1); **no model state has it** |

`key=`: the key effect of a roster change. The value sits on the roster-changing leaf and the guard
gives the tier.

| token | means | the kernel does |
|---|---|---|
| `rekey_walk` | every earlier per-write DEK is wrapped to the newcomer | for each blob the cohort holds grants on, emits one `key_grant:content:v1` row to each live occurrence of the new member |
| `next_seal` | the current epoch key at the minter's next sealed write, no earlier epoch | adds the newcomer's occurrences to the wrap set of the next `key_grant:epoch:v1`; emits nothing now |
| `stop_wrap` | no later wrap names the removed key; nothing is rotated | drops the key from the wrap set |
| `rotate_epoch` | each minter mints a fresh epoch DEK before its next sealed write | marks the epoch closed; the door refuses a sealed write under the closed epoch signed after the removal |
| `none` | no key act follows | nothing |

In every case existing grants stay and nothing is re-encrypted; that is `key_grant:{axis}`
`withdraw: by=none`, not a key effect.

`refuse=<token>`: the refusal the door answers with. Only tokens the text names appear:
`session_claim_out_of_window`, `transport_rebind_without_holder_quorum`,
`serve_transit_pair_rotation_before_rebind`.

### What it replaces

The `supersedes` and `rotation_on_removal` parts of the `lifecycle` cell. `supersedes` holds three
values today, one of them free text ("typed record supersede only"); `rotation_on_removal` holds
yes/no plus free text on seven families.

## 4. What could not be encoded

**Needs another column**

- Who signs the T7 recovery widening and that the key is a conferred human founder (cosign c54;
  the bound, c55, is encoded). Signer and subject columns.
- `hard_case:community_consensus_protocol_violation`, `hard_case:family_membership_change`, the
  room locking on a lapsed `moderate` edge (L185), the decay stages on a partnership withdrawal
  (L200, L201), the deletion SLA firing on a revoked stance (L219), ceasing replication on a
  revoked grant (L129), the audited disable of a watchlist (L225): each is a row or act the change
  triggers. Reaction column.
- The boundary fold of `consent:community_trust` and `consent:state:{stance}` (L89, L90, L94, L213,
  L214), union by identity on `key_grant` (L99), no resurrection after a withdrawal (L246, L247):
  how rows of one key combine. Fold column. `reach` could take a `boundary` token; I left it to
  that lane so one column owns it.
- A withdrawal of `retirement:decided` only while no `frozen` row exists (L261): a guard on the
  withdraw, not a bound on what it does. Guard column.
- A licence ended by its authority's revoke or suspend, a grant ended by exhaustion, `dissolves_at`
  (L26, L27, L187): ends by another transition or by a clock. Expiry and ends-by columns.
- `location_proof`, `organization`, `org_membership`, `transport_destination`, `live_stream` (N-ROW):
  no family row for the value to sit on.

**Is really a general rule**

- "A withdrawal reaches forward only" and "any one named party is enough" (CC 2.4.1.1). The first
  is the default row (`cascade=*/ref:stand`) and is encoded once on `*`.
- CC 3.5.1 precedence (`recants` over `withdraws` over `supersedes`; largest `asserted_at`; lowest
  `attestation_id`). It is what `link=ranked` invokes, stated once.
- The purge rule that a structural composer goes only with its target and a score with its
  inadmissible evidence (CC 2.4.1.1). A cascade of the tombstone, not of a row; none of the four
  tables collected it.

**Ambiguous in the text**

- `encyclopedia:*` (L136): "editor-consensus + revision chain via `supersedes`". No rule says who an
  editor is or what consensus counts, so `by` has no value.
- "A vote from an evicted key is void" (cosign c79, CC 3.3.6.3). The effect is `void`; the text
  does not name the family a self-roster vote is a row of, so the cascade has no target.
- `no_weaker` (L81). The text says "weaken" and gives no order over `consensus_protocol` values.
  The value is encoded; the kernel cannot run it until the order is a table.
- `last:seat` (L171). "Deciding seat" has no role token in `transitions.json`; the affiliation's
  officers are named by its charter.
- `identity:occurrence` (L207): "a version supersedes only its own earlier one" while any live
  occurrence of the identity may sign. `same_attester` is the cell as coded; the text may mean
  same lineage.

**Contradicts another statement**

- Key grant. CC 2.4.1.2.1: "`rotation_chain` is supersession lineage, not onward transfer." CC 5.1:
  "no row supersedes or removes a wrap". Encoded as `replace: by=none` (CC 3.3.2 and CC 5.1 agree;
  the code cell says `same_attester`).
- Epoch on admission. CC 4.4.3.2.6 multicast row: "epoch rolls on member removal (mandatory), on
  member addition (the MLS commit) and on time/bytes (optional)". Same section, `from_join`: "the
  epoch rotates on removal, never on admission". If the first is the stream epoch and the second
  the community epoch they do not conflict, and the text does not say so. Encoded: removal only.
- `rotation_on_removal=yes` on `group:roster` and `key_grant:{axis}` (code) against CC 4.4.3.4.5
  "no key is reused, so nothing is rotated" at self and family. Encoded from the text.

Tally: 69 rows encoded, for 62 reader statements (two of them split over two families) and 5
statements read from the text. 22 reader statements bearing on the concept are not encoded: 20
belong to another column (1 signer, 7 reaction, 8 fold, 1 guard, 3 ends-by) and 2 are ambiguous
(L136, c79). Three more ambiguous ones (L81, L171, L207) carry a provisional value in the TSV, and
the three contradictions are encoded toward the side named above. The N-ROW statements are not
counted: they have no family to sit on.

## 5. Where it lives

**A member of each transition in `transitions.json`, named `change`, with the grammar's `on` and
guard becoming the transition's verb and `stages`.** Reasons:

1. Every clause is a property of one verb on one family: a bound on `replace`, a cascade of
   `withdraw`, a key effect of the `removal` leaf. The family model has one cell per family; this
   concept has between one and five values per family, and the reader's N-LEAF need is the same
   shortage. Transitions already carry `stages` for leaves.
2. The door, the preview and the queue read `transitions.json` and nothing else. A bound the door
   enforces and an impact the preview shows (`cascade`, `key`) belong in the table those three read.
   CC 4.5.13 says the impact is "the difference between the fold before and the fold after, with
   the family's columns for undo"; `cascade` and `key` are that difference declared.
3. `undo` and `confirm` already sit there and depend on it: a transition whose `change` has a
   `cascade` other than `stand`, or `key=rotate_epoch`, has no way back and must confirm.

In the family model the `supersedes` and `rotation_on_removal` parts of `lifecycle` become a
generated summary of the transition members, so the model still shows one row per family.
`tools/build_transitions.py` gains the parser; the default row goes in
`formal/derivation/family_default_row.json`.

Two consequences. `membership:{stage}` needs its leaves as stages (`widening`, `removal`,
`resignation`), which the lifecycle reader also asks for. The key effect leaves `group:roster` and
`key_grant:{axis}`, where the code census put it, for the leaf that causes it.

## 6. What a model or a check can now prove

Stated over the data, for every family, in the manner of `formal/event_lifecycle`.

**P1, a change never needs fewer voices than the act it changes.** For every family and every
transition with verb `replace`, `withdraw` or `recant`: `by` is at least the policy of the family's
`attest` transition, under the order `none > cosigned_prior ≥ cosigned > committed_key, same_attester`,
except under a guard the data names (`recovery`). CC 2.4.1.1 rule 0 is the instance for `withdraw`;
the property carries it to `replace` and `recant` and shows every exception is a named guard. Today
it cannot be stated: `supersedes` has no token for a quorum.

**P2, a roster grows only by a consenting key.** For every family with `field=members`: every
unguarded `replace` has `shrink`, and every item that can add a member has `grow_signed`. So in any
run of the kernel a key in the fold's member set either signed the row that seated it or is seated
by a `widening`, whose guard requires its acceptance. With `link=chained` the member set is a
function of one chain, so two nodes holding the same head hold the same roster. This is CC 3.1.3.2
("nobody joins without their own consent, under any protocol") proved from the table.

**P3, a removal closes the key at every tier that seals.** For each of the seven scopes, the
`removal` and `resignation` stages carry a `key` value or the scope is declared plaintext; where
the scope seals per write the value is `stop_wrap`, where it seals per epoch it is `rotate_epoch`.
Then no `key_grant` row signed after a removal names the removed key on content sealed after it,
and no row before it is touched. The check finds today's gap: `species`, `biosphere` and
`federation` have no stated value, and the model's single bit is wrong for two tiers.

**P4, cascades end.** The graph with an edge from family A to family B for each
`cascade=B/…:e` with `e ≠ stand` on a transition of A is acyclic, so the fold after any one row
reaches a fixed point in at most the graph's depth (three on today's data: `membership` to
`group:roster` to `licensure`).
