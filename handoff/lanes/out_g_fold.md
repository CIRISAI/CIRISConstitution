# Lane G: the `fold` column

The model's `projection` cell names a family's output table and whether it rebuilds. This column
states the function: which rows are read, what they are keyed on, which row wins, what may only
move one way, what a retraction removes, who is counted, how values combine, what an absent row
means, what comes out, who runs it and which other fold reads the result.

Encoded rows: `out_g_fold.tsv` (243 rows, 236 statements, 87 family rows touched, 29 rows carry a
leaf selector). Every value in it passes a validator written from the grammar below, every quote
is verbatim in the Parts as they stand on `rc19`, and every family is a row of
`manifests/family_model.json` (or the default row `*`). The `note` column begins with the
statement's id: `L`, `E`, `C`, `A` plus the row index in the lifecycle, erasure, cosign or audience
table; `F` plus the index among the 183 inventory rows whose `column` is `formula`, `tie_break`
or `monotone_field`, in inventory order.

Sources: 132 `RICHER` rows of the four readers (erasure 90, lifecycle 26, cosign 15, audience 1)
and 104 of the 183 inventory fold statements (63 of the 69 at family scope, 41 at kernel scope
that are the default row or sit on one family).

## 2. The column

**Name:** `fold`.

### Grammar

```
fold    := [ "@" segment "=" leaf { "|" leaf } ": " ] part { "; " part }
part    := "reads="   source { "+" source } { "&" filter }
         | "key="     member { "," member }
         | "pick="    picker { "," picker }
         | "order="   compare { "," compare }
         | "bound="   mono "(" member ")" { "," mono "(" member ")" }
         | "cut="     cut { "," cut }
         | "over="    set [ "@" instant ] [ "/" unit ]
         | "weight="  expr
         | "combine=" agg "(" expr ")" | "combine=policy(" policy_row ")"
         | "test="    expr cmp expr ( " !" refusal_token | " ?" state ":" state )
         | "absent="  absent
         | "result="  shape
         | "by="      runner
         | "feeds="   target { "," target }
picker  := compare | "union" | "once" [ "(" refusal_token ")" ] | "chain(" member ")"
         | "first_seen" | "agree" | "set" | "pair(" family ")"
compare := "max(" member ")" | "min(" member ")" | "rank(" value { ">" value } ")"
expr    := integer | member | "prev" | "n" | "m" | expr ("+"|"-"|"*"|"div"|"/") expr
         | ("min"|"max"|"sum"|"count"|"rate") "(" expr { "," expr } ")"
```

`member` is a member of the signed object or of the family's body (CC 2.6.1.7, the family's
CDDL), or a `{placeholder}` of the family's own pattern written without braces. `family` is a
family of the registry. `refusal_token` is a token the text names. `policy_row` is a row of
`constitution/governance_policy.tsv`. A cell is a list of values: one without a selector, and
one per leaf where the leaf selects the fold. A part a leaf value omits is inherited from the
family's unselected value, and a part that omits is inherited from the default row.

The selector `@segment=leaf:` names a placeholder of the family's pattern (`stance`, `stage`,
`state`, `job`, `axis`, `kind`, `scale`) and one or more of its closed values. Four selectors
used in the rows are not pattern placeholders and are members of the row the fold starts from:
`cohort_subkind`, `group_kind`, `group` (the group record a roster row is about) and `status`
(a licence's status member). They are marked in section 4.

### The default row

```
*   reads=own&live; key=references_attestation_id,attesting_key_id;
    pick=rank(recants>withdraws>supersedes),max(asserted_at),min(attestation_id);
    bound=narrow_only(cohort_scope); cut=named,forward; over=standing/person;
    absent=none; result=scalar; by=node
```

This is CC 3.5.1 (the precedence of the composers, then the latest signed instant, then the
bytewise-lowest id), CC 2.4.1.1 (a withdrawal retires the row it names and reaches forward),
CC 2.1 (`cohort_scope` narrows and is never re-authored), CC 4.5.13 (a voice is a person) and
CC 5.3.2.4.4 (`asserted_at ≤ t < expires_at`). 158 families whose projection is "the row itself"
need nothing more.

The reader's default, chosen by the family's `polarity` cell (CC 4.4.2), is a five-row table and
not a per-family value:

| polarity | value |
|---|---|
| signed | `reads=own&live&signer:trusted; key=dimension,attested_key_id; combine=mean(score*confidence); by=reader` |
| boolean-via-score | `combine=min(score); by=reader` |
| positive-only | `combine=max(score); by=reader` |
| -1.0-only | `combine=min(score); by=reader` |
| enumerated | `pick=max(signed_at); by=reader` |

Detector families depart from it with `combine=median(score)`. A last comparator
`min(affected_population_estimate)` is the reader's tie-break of CC 4.4.3.9.

### Parts and tokens

Each line: what the token means, then what the kernel does.

**`reads`**: the rows that enter.

| token | means | the kernel |
|---|---|---|
| `own` | rows of this family | selects held rows whose dimension matches the family pattern |
| `head` | the group record's head: the held head, or the witnessed head where the record's charter declares a `witness_quorum` | reads the one head row for the key and starts the fold from its member list |
| a family name | rows of that family under the same key | selects them too; the set of sources is closed, so a family not named never enters (this is how `capacity:relay_delivery` stays out of the composite) |
| `&live` | not withdrawn, recanted, superseded or expired at the instant | drops rows whose state in the five retraction states is not `admitted`, and rows outside `asserted_at ≤ t < expires_at` |
| `&at(now\|asserted_at\|decision)` | rows effective at the instant: seated by it, not removed, resigned or evicted by it, signed before the signer's `revoked_after` | compares each row's effective instant and every row that ends it with the instant |
| `&signer:role` | only rows whose signer holds the role toward the key at the row's `asserted_at` | resolves the signer's standing as the door does and drops the rest as testimony |
| `&direct` | the seated key signed, never a delegate and never a chain | drops a signature whose signer reaches the seat through `delegates_to` |
| `&seat:human` | the seat's `identity_type` at seating does not include `node` | drops a founder seat held by a node-bearing key from the count |
| `&has(member)` | the row carries the member | drops a row that lacks it (a row lacking a `key` member is dropped in any case) |
| `&cap(scope)` | the signer holds a live conferral carrying the scope | walks the signer's conferrals and drops the row when none carries it |
| `&declared(member)` | the member's value is one the issuer's record declares | reads the issuer's record and drops the row when the value is not declared |
| `&cites(family)` | the row cites a live row of that family | resolves the reference and drops the row when it does not resolve |
| `&last(n)` | the last n periods | drops rows of earlier periods |

Roles are the role tokens of `transitions.json` (`self`, `subject`, `owner`, `author`, `founder`,
`member`, `holder`, `serve`, `steward`, `wa`). Three are added: `authority` (the key the
family's `{authority_id}` resolves to, CC 2.4.1.2.1), `proxy` (the subject's `delegates_to`
proxy, the `via` of the signer rule) and `trusted` (a key of the reader's trust set, CC 4.4.3.8).

**`key`**: the members the rows are grouped on. The kernel builds one group per distinct tuple,
and each group is one object with one state. A row lacking a key member is not folded.

**`pick`**: which rows of a group stand. A list is applied left to right, each later picker
deciding only what the earlier leaves tied.

| token | means | the kernel |
|---|---|---|
| `max(m)` / `min(m)` | the row with the greatest or least value of the member | compares the member, bytewise for ids and digests |
| `rank(a>b>c)` | the row whose leaf, verb or member value stands earliest in the order | compares positions in the list |
| `union` | every row stands; a repeat of a row's identity is the row already held; no later row removes one | appends, and answers a repeat as held |
| `once(token)` | the first row for the key stands and a second is refused by the token | refuses at the door when a row for the key is held |
| `chain(m)` | a new version stands only if its member names the standing head | compares the member with the head's digest and refuses otherwise; a later instant does not help |
| `first_seen` | among versions naming the same head, the one this node held first | compares first-held instants; the one picker that reads the node's own receipt |
| `agree` | the rows of one voice count as one where they agree and as none where they differ, until withdrawals leave one | compares the rows' choices under the key |
| `set` | every live row stands and the result is their set | collects |
| `pair(family)` | the group stands only when it holds a live row of this family and one of the named family, each naming the other's signer | joins the two rows and compares signer with subject both ways |

**`order`**: the order of the result where it is a list, as a comparator list. The kernel sorts
by it (a roster by `min(key_id)`, the election's ballot by merit, then admission order, then id).

**`bound`**: a member that moves one way across the versions of a key. The check runs at the
door and before the merge, so a stale row never enters.

| token | the kernel refuses a row whose member |
|---|---|
| `lower_only(m)` | is greater than the standing value |
| `raise_only(m)` | is less than the standing value |
| `narrow_only(m)` | is wider or weaker than the standing value in the member's declared order (the seven scopes for `cohort_scope`) |
| `drop_only(m)` | holds an element the standing set does not |
| `fixed(m)` | differs from the standing value |

**`cut`**: what an admitted retraction removes from the fold.

| token | the kernel |
|---|---|
| `named` | removes the row the retraction names |
| `boundary(m)` | removes every row of the key whose member is at or before the retraction's own value of it |
| `whole` | removes the whole row and never a part of its body |
| `terminal` | keeps the key ended: no replay and no later-dated copy reopens it |
| `forward` | applies the removal to instants after the retraction and to none before |
| `none` | refuses a retraction of the family's rows |

**`over`**: the set a count is taken over, the instant it is read at and what is counted.

| set | means |
|---|---|
| `standing` | the roster the act is about (the policy table's word) |
| `active` | the census expected-active base (the policy table's word) |
| `live` | the roster members not evicted or lapsed at the instant |
| `others` | the roster without the act's target (the policy table's `cancel_over` word) |
| `present` | those who signed presence inside the window |
| `founders` | the active founder set |
| `deciding_seats` | the seats an affiliation's charter gives the decision to |
| `seated` | the full seated roster, never its live subset |
| `listed` | the persons a founding record lists |

Instants: `now`, `asserted_at` (the row's signed instant), `decision` (the instant the numbers
are met), `prior` (the roster without the row being decided), `act` (the instant of the act
under review), `count`, `seating`. Units: `person` (the fedID of the key's self roster), `key`,
`owner`, `node`. The kernel folds the named roster at the instant, maps each signer to its unit
and counts distinct units; the policy row supplies the numbers the count is compared with.

**`weight`**: what one row contributes to `combine`, an integer expression over its members.
`rate(m)` is the value a published rating table gives the member's value, and 0 for a value the
table does not list. `count(m)` counts distinct values of the member in the group.

**`combine`**: `min`, `max`, `sum`, `count`, `mean`, `median` over the group; `all(present)`
(every source of `reads` has a live row under the key); `strictest(m)` (the most restrictive
value in the member's declared order); `policy(row)` (the policy row's own machine, for the
ranked election). The kernel computes it in integers where `by` is `node` or `door`.

**`test`**: a comparison over the folded values. With `!token` the door refuses the row by
that name when the comparison fails. With `?a:b` the fold's state is `a` when it holds and `b`
when it does not. `n` is the size of the `over` set, `m` the M of the group's `quorum:M/N`,
`prev` this fold's result for the period before.

**`absent`**: what a reader of the fold gets when no row stands for the key.

| token | means |
|---|---|
| `none` | no state: nobody acts, no consent |
| `unspecified` | the subject never declared |
| `restricted` | the fail-secure verdict of CC 3.1.2 |
| `protective` | the protective default of CC 3.4.11 |
| `full` | the presumption of CC 3.4.12 |
| `undefined` | no value, and the row that would carry one is not emitted |
| `refuse` | every guard that needs the value fails closed |
| `from(family)` | the value the named family's row carries |

**`result`**: `scalar`, `set`, `one` (exactly one row or none), `bool`, `vector(m)` (one value
per value of the member, never combined across it), `state(a|b|c)` (the closed states a reader
may be told).

**`by`**: who runs the fold.

| token | means | consequence |
|---|---|---|
| `door` | the kernel at admission | a failure is a refusal by name |
| `node` | the kernel over held rows | byte-equal on every node holding the same rows |
| `reader` | a consumer at read time | the substrate admits the rows and enforces nothing |
| `advisory` | a person or a quorum reads it | no fold run by `door` or `node` may name the family in `reads` |
| `none` | read by no fold | the row is kept and served and moves nothing |

**`feeds`**: the folds that read this family's result: a family, `replication.audience`,
`cosign_rule`, `signer_rule`, or `policy(row)`. It is the inverse of `reads` and is checked
against it.

### Tokens invented here

Everything else is a registry family, a wire member, a role token, a policy-table word or a
token the text names.

- Roles `authority`, `proxy`, `trusted`.
- Sets `founders`, `deciding_seats`, `seated`, `present`, `listed`; instants `prior`, `act`, `count`, `seating`.
- Pickers `agree`, `pair`, `chain`, `once`; cuts `boundary`, `whole`, `terminal`, `forward`; bounds as a group.
- Four refusal tokens the text does not name: `roster_change_below_majority` (CC 4.2.6),
  `witness_quorum_invalid` (CC 3.2), `evidence_score_mismatch` (CC 3.1.5.5),
  `aggregation_meta_mismatch` (CC 6.1.2.1.2, to be checked against the tokens there). The text
  gives the rule and no name for its refusal.
- Member names `ballot_count`, `ballot_set_digest`, `admission_order`, `relay_countersignature`,
  `chunk_commitment`, `transfer_id`, `account`, `seq`: written from the prose and to be matched
  to the CDDL when the column is built.

## 4. What could not be encoded

### Needs another column or table

- **A reader's gate over a folded value** (lane G guard): `E246` (a sensitive space requires a
  verified level, CC 3.4.11), `E255` (a single-assessor `provider` level supports the T1 tier
  only, CC 3.4.12), `F29` `F58` `F59` (the accountable-root and one-human-three-keys predicates,
  CC 3.2, 3.4.7.3), `F108` to `F111` (the content gate and the age gate, CC 4.4.3.10), `F137`,
  `F8`, and the federation-scope refusal half of `F76`. The fold gives the value and the guard
  compares it.
- **A `backing` column** (the erasure reader's own request): `E77`, `E80`, `F158` (a holding
  claim counts 2, 1 or 0 by what backs it, CC 6.1.5; the bytes-plane liveness fold never reads a
  holding claim, CC 3.1.3.3). With `backing` in the model the value is `weight=backing`.
- **A `pin_class` column** (the audience reader's request): `F159`, `F161` (cache descends before
  pinned, then lowest rarity, then oldest revision, CC 6.1.5.2) and `F157`.
- **Body defaults**: `E75` (a record naming no publish right gives every member the right,
  CC 3.1.3.2) and the half of `F5` that sorts an absent `revoked_after` as negative infinity are
  defaults of a body member, where `absent` here is about a missing row.
- **Freshness**: `C5` (a departed signer's cosignature counts only inside W, CC 2.6.7).
- **A verb rule**: the half of `L131` that says a narrowing of a replication grant must be a
  `supersedes` and never a silent drop (CC 3.3.7).
- **A policy row or a policy number**: `F94` (quorum size by locality: 2, 3, 4, 6), `E43`
  (two of three registry sources), `E153` (three witnesses and four bars), `F101` and the
  threshold of `E331` (0.7), `F102`, `F73` and `F165` (a delegate's weight capped at half the
  root's). Each is a number a `test` would name if a row held it.
- **A rating table**: `F75` to `F80` are encoded as `weight=rate(hardware_class)`; the table of
  class and multiplier (CC 4.2.2) has no data file yet.
- **A selector that is not a segment**: `F86` (the full-roster denominator yields to presence
  for a liveness-critical decision, CC 4.3), the `cohort_subkind`, `group_kind`, `group` and
  `status` selectors used in 11 rows, and the six placement and tier values per leaf the
  audience reader collected (`hard_case:{kind}`, `consent:state:{stance}`, `config:{scope}`:
  rows A34, A40, A44, A76, A110, A111). The `@segment=leaf:` prefix is not special to this
  column: `placement` and `replication` can take it as written, and the class of a decision
  needs a member on the row.
- **No family row**: `L246` `L247` `F128` (`organization`, `org_membership`: the value would be
  `pick=max(asserted_at),min(attestation_id); cut=forward`), `L255` (`transport_destination`),
  `F144` (`wholeness_witness`: `key=peer; bound=raise_only(epoch_id)`), `F160` `F162`
  (`StorageBudgetV1`: `key=node_id; bound=raise_only(revision)`), `F65` `F66` (the
  `delegates_to` edge: a revoked grant ranks above the grant; guardian conflict resolves most
  restrictive), `E308`, and `F169` to `F182` (the Stewardship Tier of CC 7.3.3, whose formula
  `ceil(CIS*RM/7)` the expression grammar can write and no row can hold). The row `e311` of the
  erasure table is misaligned; its statement (the key-grant recipient set is computed from the
  occurrence and roster rows, CC 4.4.3.4) is carried by `feeds=key_grant:{axis}` on `group:roster`.

### Is really a general rule

- **Properties of every fold, to be proved and not encoded** (section 6): `F41` `F42` `F43` `F44`
  `F47` `F49` (the standing verdict has no input but rows, is constant between declared
  instants, is the same with and without a latched halt, and is independent of arrival order,
  CC 3.2), `F143` (every instrument is a pure, integer, permutation-invariant fold, CC 6.1).
- **A walk over a graph, not a fold over a key**: `F104` `F105` `F113` `F34` `F46` (the
  trust-set walk: breadth first, depth the lesser, classes the intersection, CC 4.4.3.8;
  `formal/trust_set` holds it). `F67` (contradicts and clarifies are emergent readings).
- **Byte layouts and derivations**, which belong to `body`: `F31` `F32` `F125` `F126` `F127`
  `F134` `F135` `F136` `F138` `F139` `F141` `F152`.
- **Instrument mathematics of Part 6**, a table of instruments and not of families: `F145`
  `F146` `F149` `F150` `F151` `F153` to `F156`, `F163` `F164`; and transport: `F140` `F142`.
- **Registry rule**: `F114` (the earlier `signed_at` holds a name in an open vocabulary).
- **Restatements with no value of their own**: `F1` `F2` `F182`.

### Ambiguous in the text

- `C79`, CC 3.3.6.3: "any signed act by a roster key answers every open proposal and proves the
  key is not lost". The fold would read every family's rows as a vote; the text does not say
  which way the answer counts or whether a withdrawn act still answers.
- `F7`, CC 3.2: `witness_quorum` "MUST equal ⌊|witnesses|/2⌋ + 1 … and at least 2", and a charter
  declaring 0 is witnessed mode off. The encoded test covers the first and a single `test`
  cannot say "or 0".
- `F22`, CC 3.1.9.2: "relieve-never-expand" is encoded as `narrow_only(value)`; the direction of
  relief is not defined per key.
- `E157`, CC 3.1.9.3: responses compose into "the ruling CC 4.3 publishes on the accountable
  seat"; the record that fold produces has no family, so `feeds` has no target.
- The consent-state fold of CC 4.4.3.5.5 orders grants by `asserted_at` and names no tie-break,
  where CC 3.3.1 gives `consent:community_trust` "ties on the smallest attestation id" and says
  `consent:state` rows "use the same boundary fold". The encoding inherits the default row's
  last comparator.

### Contradicts another statement

- **The licence's winner.** CC 3.3.9: "Current state is resolved by stable-id grouping —
  `supersedes` to amend, `withdraws` to revoke, latest `asserted_at`, tie-break smallest
  `attestation_id`". CC 5.3.2.3: "Then the `MergeBallot` comparator: `quorum_weight` → signed
  timestamp → content hash. Quorum-above-time is deliberate". The two give different winners
  when quorum weights differ, and different tie-breaks when they do not. Both are in the TSV
  (`F55`, `F130`).
- **A licence's status: a set or the most restrictive.** CC 3.1.1: "More than one status MAY be
  live concurrently … so a consumer composes the set rather than reading a scalar." CC 5.3.2.3:
  "More-restrictive state wins on conflict: `revoked` > `suspended` > `active`." Encoded as
  `result=set` (`E34`) and `pick=rank(revoked>suspended>active)` (`F131`); they agree only if
  the rank applies inside one `license_id` and the set across status dimensions, which neither
  section says.
- **First seen and the function of rows held.** CC 3.2: "Forks of a family or community roster
  are first-seen-wins". CC 4.5.13: "The seat is a function of the rows held and never of their
  arrival", and CC 3.2 (vii) says the standing verdict "is independent of the order in which the
  rows arrived". The text limits first-seen to ordinary rooms, so there is no clash in the
  words; `group:roster` is still the one family whose fold reads arrival, and its projection
  cell says `byte_equal`.

## 5. Where the column lives

A new column `fold` of the family model, beside `projection`, with the default row in
`formal/derivation/family_default_row.json` and departures in `manifests/family_departures.tsv`.

Reasons. The fold is a property of the family's rows as a set and of no single transition: the
step of CC 4.5.13 appends a row and "the view after is the fold over the larger set", so every
transition of a family shares one fold. The 158 families whose projection is the row itself take
the default row and need no cell. The per-leaf values use the form `transitions.json` already
uses for `stages`: one value for the family and one per leaf that differs.

Three pieces sit elsewhere and the cell points at them:

- **The polarity defaults** are five rows keyed by the `polarity` cell, kept beside the default row.
- **The numbers** stay in `governance_policy.tsv`. `over` duplicates, in closed tokens, what the
  table's `standing_set` column says in free text and what `base` and `cancel_over` say in
  tokens. Where a family has a policy row the count set should be written once: see the decision
  asked of the lead.
- **The rating table** of `rate()` is a small data file of its own (member, value, multiplier).

`derived` (today `gap` in every family) becomes computable: a family whose fold has a `reads`
naming other families and `by=node` or `by=door` is a derived family, and its row must equal the
fold's result (`weighted_aggregate`, `census:composite`, `census:expected_active`).

## 6. What a model or a check can now prove

Stated over the data, for every family, in the manner of `formal/event_lifecycle`.

1. **`fold_commutes`.** For every family whose fold is run by `door` or `node` and has no
   `first_seen`: for any two orderings of the same set of rows, the fold's result is equal. The
   proof is by cases on the grammar: each picker except `first_seen` selects by a total order on
   signed members or is a set union, each `bound` and `cut` is a meet over the rows, each `agg`
   is commutative and associative. The check that makes the order total is syntactic: the
   comparator list of `pick`, with the default row's `min(attestation_id)` appended, ends in a
   member unique per row. This is CC 3.2 (vii) and CC 6.1 for every family at once, and it names
   the exceptions as data: today `group:roster` alone. Corollary `rebuild_is_fold`: a family
   whose `projection.rebuild` is `byte_equal` has a commuting fold, so two nodes holding the same
   rows hold byte-equal tables.

2. **`advisory_moves_nothing`.** No family whose fold is `by=advisory`, `by=reader` or `by=none`
   appears in the `reads` of a fold run by `door` or `node`, nor in the roles or guard of any
   transition. So a detector, a ratchet flag or a LensCore measure never changes an object's
   state by its own arrival (CC 3.1.6, 3.1.8), proved over the 46 families so marked in the rows (16 of them advisory) and not asserted per
   section. The same closure gives `reads_feeds_inverse` (G is in `reads` of F exactly when F is
   in `feeds` of G) and `inputs_reach_the_holder` (every family in the `reads` of a `node` fold
   has a replication audience that contains the folding family's audience, so a node that holds
   the rows to fold also holds the rows the fold reads).

A third, smaller: **`ended_stays_ended`**. For every family with `cut=terminal` or a `bound`,
no sequence of admitted rows returns a key from an ended state or moves the bounded member back,
which is anti-rollback (CC 5.3.2.3) and "no later-dated copy reopens it" (CC 4.4.3.5.5) as one
theorem over the grammar.
