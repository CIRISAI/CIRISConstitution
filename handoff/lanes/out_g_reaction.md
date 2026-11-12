# Lane G: the `reaction` column (a reaction and a clock)

Encoded rows: `out_g_reaction.tsv` in this folder (113 rows; every value parses under the grammar
below, checked by a regular expression per clause). Sources read: the four reader tables (488
`RICHER` rows, all read), the 139 inventory statements whose column is `window` or `freshness`,
`constitution/constants.tsv`, `constitution/governance_policy.tsv`, `manifests/transitions.json`,
CC 4.5.13 (the state processor) and `formal/event_lifecycle/README.md`.

## 2. The column

**Name:** `reaction`. One cell is a list of clauses. A clause is an expiry, a clock or a reaction.

### Grammar

```
cell     := clause *( "; " clause )
clause   := [ selector " " ] ( expiry | clock | react )
selector := "[" leaf *( "|" leaf ) "]"  |  "@" scope
expiry   := "expiry " mode [ " " member ] [ " eq " dur ] [ " default " dur ] [ " max " dur ]
            [ " from " origin ] [ " by " judge ]
clock    := "clock " name " = " dur [ " default " dur ] [ " max " dur ] " from " origin [ " by " judge ]
react    := "on " event *( "|" event ) [ " unless " event *( "|" event ) ] " -> " effect *( ", " effect )
event    := state "(" famref ")" | "close(" name ")" | "fold(" foldname ")"
effect   := [ "should " | "may " ] ( "emit " famref " by " role | "read " verdict [ " of " famref ]
            | "do " act | "open " policy_row )
dur      := constant | policy_row ".window_secs" | holder "." member
origin   := "first_held" | signed_member | event *( "|" event )
```

No free text appears in a value. A number never appears: a `dur` is a name.

### Tokens: what each means, and what the kernel does

**Selector**

| token | means | kernel does |
|---|---|---|
| `[leaf]` | the clause holds for the named closed leaf of a parameterised family (`[granted]`, `[confirmed]`, `[Dmca512]`); leaves are the registry's | matches the row's dimension leaf before applying the clause |
| `@scope` | the clause holds when the row's `cohort_scope` is this one of the seven scopes | compares the row's signed scope |

**Expiry** (the row's own clock, carried in a signed member)

| token | means | kernel does |
|---|---|---|
| `required` | the member must be present | the door refuses a row without it (malformed) |
| `optional` | the member may be present | reads it if present; no clock otherwise |
| `forbidden` | the member must be omitted, never null | the door refuses a row that carries it |
| `none` | the family has no expiry clock at all, whatever the row carries | never lapses the row on time |
| `member` | which signed member carries the instant: `valid_until`, `expires_at`, `delegation_valid_until`, `dissolves_at` | reads that member; absent `member` means `valid_until` |
| `eq dur` | the instant equals origin + dur | door compares and refuses otherwise |
| `default dur` | value applied when the member is absent | the fold computes origin + dur |
| `max dur` | ceiling on member minus origin | door compares and refuses over the ceiling |
| `from origin` | where the span is measured from; absent means `asserted_at` | reads that signed member |
| `by judge` | whose clock decides that the instant has passed (below) | chooses the instant it compares against |

An expiry declares a clock named `expiry`; `on close(expiry)` is the lapse.

**Clock** (a window that is not the row's own expiry member)

| token | means | kernel does |
|---|---|---|
| `clock name = dur` | a named span | computes close = origin + dur |
| `from first_held` | the instant this node first held this row (CC 4.5.13) | reads its own receipt instant for the row |
| `from <signed member>` | `asserted_at`, `claimed_at`, `effective_at`, `cosigned_at`, `delegation_valid_from` | reads the member from the row |
| `from event(...)` | the instant this node first held the row that makes the event | reads its receipt instant for that other row |
| `by signed` | both ends are signed instants; no receiver clock is used | compares two signed members; same answer on every node |
| `by receipt` | close is compared with this node's present instant | the instant argument of the step; answer is this node's |
| `by origin_door` | judged once, at the door that first admitted the row; a replica does not re-judge | a replicating node skips the check (new token; see X4) |

**Events** (triggers and `unless` conditions)

| token | means | kernel does |
|---|---|---|
| `admitted(F)`, `withdrawn(F)`, `superseded(F)`, `recanted(F)` | a row of family F reached that state; the four states are those of `transitions.json` | the fold over held rows shows the state, and the node has a receipt instant for the row that made it |
| `purged(F)` | the row was hard-deleted under a tombstone (new token) | the node holds the tombstone for the row's digest |
| `refused(F)` | the door refused a row of F by name | fires in the step that refuses; the refused row is not held |
| `matched(F)` | a watchlist row of F matched content at the publish or share seam (new token) | the matcher's result on a row being admitted |
| `sealed(F)` | a sealed write into the cohort the row belongs to (new token) | fires in the step that admits the sealed content row |
| `close(name)` | the named clock or `expiry` has closed | origin + dur is at or before the instant argument |
| `fold(name)` | a named fold result became true; the names are the fold column's (lane G fold) | recomputes the fold after each append and at each instant |

`F` is a registry family, a leaf of one, `self` (this row), `target` (the row this row names) or
the primitive `delegates_to`. Fold names used: `no_live_deciding_seat`, `no_member`,
`signer_seated`, `policy_met`, `keep_decided`, `promoted`, `head_covers_row`, `terminal_row`,
`subject_absent`, `no_wrap_target`, `founder_quorum_unreachable`, `founder_quorum_restored`.

**Effects**

| token | class | means | kernel does |
|---|---|---|---|
| `emit F by role` | **row** | the node whose key holds `role` signs a row of F about the trigger row | builds the row with an identity computed from (trigger row id, clause), offers it to its own door, appends, replicates under F's own replication cell |
| `read V [of F]` | **verdict** | the fold reports V for this row, or for F | nothing is written; any node holding the same rows recomputes it |
| `do A` | **verdict** | a duty that follows from the verdict | the node acts on its own store or serving; no row |
| `open P` | **verdict** | the queue offers the transitions of policy row P | the queue generator enables them |

- `role` is a role token of `transitions.json`: `identity:substrate_persist`,
  `identity:lenscore_detector`, `author` and so on. One new token: `origin_door`, the node that
  admitted the row which moved the fold (CC 3.2: "Peers re-derive the verdict from the rows and do not emit").
- Verdicts `V`: `lapsed`, `stale`, `unknown`, `closed` (the door refuses this leaf from now on),
  `withdrawn` (reads as the withdraws of the record), `locked`, `lagging`, `purgeable`,
  `forfeited`. The text uses each word; `closed` and `forfeited` are new as tokens.
- Acts `A`: `stop_serving`, `destroy_bytes`, `drop_held`, `cease_replication`,
  `deregister_peer`, `cancel_watch`, `purge`, `reroute`.
- `should` and `may` lower the force; absent means MUST.

### The kernel rule, kept

A reaction never moves state by itself. `read`, `do` and `open` are functions of the held rows
and the instant, so they are the node's own recomputable verdict. `emit` produces a row, which
enters by the door like any other row. So the answer asked for, per reaction, is the effect
keyword: `emit` is a row others replicate; everything else is a verdict.

Of the 113 encoded rows: 42 contain an `emit`, 71 are verdict only.

### Constants

Clocks point at names. Present in `constants.tsv` and used: `admission_freshness_window_secs`,
`moderation_fallback_window_secs`, `withhold_window_dmca512`. Read from the policy table:
`default_standing.window_secs`, `self_roster_add.window_secs`, `moderation_action.window_secs`,
`moderator_election.window_secs`. Read from a signed holder: `charter.halt_fuse_secs`,
`charter.witness_cadence_secs`, `charter.attach_window_secs`, `charter.role_term`,
`group.hold_window_secs`, `self.days`, `decay_protocol.*`, `community.t2_review_cadence`.

Names the text gives a number for and `constants.tsv` lacks (to add, 15):
`session_claim_max_secs` (86,400), `custody_report_ttl_secs` (259,200),
`consent_temporary_ttl_secs` (14 d), `membership_proposal_max_secs` (30 d),
`delegation_term_max_secs` (365 d), `mesh_config_emergency_ttl_secs` (72 h),
`purge_dwell_secs` (72 h), `consent_revocation_promotion_window_secs` (24 h),
`accord_heartbeat_max_secs` (90 d), `accord_roster_window_max_secs` (7 d; today inside the note
of `admission_freshness_window_secs`), `epoch_key_retention_secs` (30 d),
`withhold_window_dsa16`, `withhold_window_osa` (14 d each), `withhold_window_community_standards`
(30 d), `census_period_end`. Named in the text with no value: `trace_orphan_age_secs`,
`wa_freshness_window_secs`, `incapacity_t1_window_secs`.

## 4. What could not be encoded

Of the `RICHER` rows that ask for a reaction or a clock, 79 are encoded and 27 are not. Of the
139 inventory statements, 32 are encoded; the rest are counted by group below.

**Needs another column (9 reader rows, about 15 inventory statements)**
- Ends by another party's act with a status value: `licensure` revoked or suspended by the
  authority (CC 2.4.1.2.1). This is the lifecycle column's `ends_by`.
- What survives an erasure and who executes it: CC 6.1.2.2 (the hash kept), CC 7.5.5 (the
  custodian writes the tombstone, the court-order basis). Erasure column.
- What a missing row reads as (`attestation:registry_consensus`, `session`, `capacity:composite`,
  `consent:state` unspecified). A fold default.
- Guards on admission that use a clock but react to nothing: the emergency `mesh_config` "not
  renewable back-to-back by the same holder"; the W bound applying only to a key that has lost
  standing; `delegation_term_required`; the duplicate `invocation_id` within `valid_until`. Guard column.
- A bound of SHOULD strength: "deletion_sla SHOULD be at most one month". The grammar lowers the
  force of an effect and not of a `max`.
- Sums of spans: `rendezvous:route` retention is "the current period plus one grace period".
  Encoded in part (the `purgeable` verdict only).

**No family row to key on (6 reader rows, 2 inventory)**
- `location_proof` (tombstone kept, forward-only, stale after 30 days), `live_stream` (kept only
  at an epoch boundary). The clauses are sayable once the kinds have rows.

**Really a general rule (about 55 inventory statements)**
- The skew bound, the future bound, the W = 72 h rule for chain-judged rows, "every window is
  measured from the instant the node first held the proposal", the window classes by
  sensitivity. These are the grammar's defaults (`by`, `from first_held`) or rows of the policy
  table, stated once, not per family.
- Mechanism and steward statements with no family: shaping windows per device class (CC 5.4.3),
  the STH cadence, the Registry's 5-minute rule, the 90-day and 120-day notices of CC 7.5.4, the
  72 h severance window. They are constants, and nothing reacts.

**A person's act, not a node's reaction (5 reader rows)**
- A misdeclared age or capacity "is adjudicated, never slashed" (CC 3.4.11, 3.4.12): somebody
  files a `moderation:*` row; no node emits one.
- CC 4.4.3.4.3: the agent occurrence's withdrawal "enters the objection path of the retirement
  machine". The text names a path and no row.

**Ambiguous in the text (7 reader rows, 3 inventory)**
- A1. `duty:{kind}`: "its **breach** routes to `hard_case:duty_unmet`" (CC 3.1.1). No emitter, no
  clock, no instant of breach.
- A2. `fidelity:explainability_sla:{tier}`: "SLA breach surfaces as
  `hard_case:sla_breach_unattested`". No emitter rule.
- A3. The deletion window "starts at the subject's withdrawal" (CC 4.4.3.4.7): the signed
  instant or each node's receipt is not said. Encoded as receipt.
- A4. `key_grant` ends by "exhaustion" (CC 2.4.1.2.1): undefined.
- A5. The WA freshness window (CC 3.1.9.3, 4.3) and the moderator's (CC 4.5.13) have no value and no name.

**Contradictions (both sides quoted; one side encoded)**
- X1. CC 3.3.1 D1: "that emission is evidence **toward** D1 and never a substitute for it.
  Breach is therefore: the window passed **and** the row is still present with none of the three
  composers against it." CC 4.5.2.2: "producer emits `consent:deletion_complete` OR substrate
  emits `hard_case:deletion_window_breach`". Encoded D1: the `unless` set is withdrawn,
  superseded or purged, and `consent:deletion_complete` does not stop the breach row.
- X2. CC 4.5.3: "Each window is counted on each holder from the instant it executes" the
  tombstone. CC 4.5.13: "The first-held instant is the node's own receipt … It is what every
  window in this document runs from". An execution instant is not a held row's receipt. Encoded
  `from admitted(self)`.
- X3. Who emits a row that a fold or a clock causes. CC 3.2: "The substrate that admitted the
  row … MUST emit … Peers re-derive the verdict from the rows and do not emit". CC 3.3.1 D2:
  "emitted by the observing substrate". One rule names a single emitter, the other any observer.
  Encoded as written in each place (`origin_door` against `identity:substrate_persist`).
- X4. CC 3.1.3.1: the session clock rule "is applied once at the emitter's admitting substrate
  and an admitted row replicates as admitted". Under the kernel rule a verdict is a fold over
  held rows and their first-held instants on every node. Encoded with the new token `by origin_door`.
- A reader note (erasure 321) says the substrate emits `consent:decay:*`; the text it quotes
  says "the substrate emits no `consent:decay:*` row". The text is encoded.

## 5. Where it lives

**A table of its own, `manifests/reactions.json`, one row per clause, keyed by (family,
selector).** Three reasons.

1. A reaction relates two families: the trigger and the family emitted. The readers filed the
   same statement under both ends (21 of the encoded rows are inverses, re-keyed on the trigger family). One row keyed on the
   trigger family, with the emitted family as a field, states it once; the emitted family's
   view is an index over the table.
2. A family has from none to six clauses and they differ by leaf. A single cell per family
   would be a list with selectors inside, which is a table written sideways.
3. It is not a member of a transition. A transition is a row a person signs when a guard holds;
   a reaction is what a node does after a row lands or an instant passes. The trigger of half
   the clauses is `close(...)`, which is no transition.

Two links to what exists. The `expiry` clause replaces the `expires` part of the `lifecycle`
cell ("expires_at honoured" in all 181 code-read cells) and should be generated into the family
model from this table. A clock whose `dur` is `P.window_secs` leaves the close to the policy
row's `at_window`; the reaction table does not restate it.

Proposed fields per row: `family`, `selector`, `clause` (expiry | clock | react), `name`,
`mode`, `member`, `dur`, `default`, `max`, `origin`, `judge`, `on[]`, `unless[]`, `effects[]`
(each `kind`, `family` or `verdict` or `act`, `role`, `force`), `class` (row | verdict),
`cc_ref`, `source`.

## 6. What a model or a check can now prove

Stated over the table, for every family.

**P1. No clock-caused row is the only cause of a state.** For every clause whose trigger
contains a `close(...)` or a `fold(...)` and whose effects contain an `emit`, the fold of the
affected object gives the same state with and without the emitted row held. In words: a node
that never receives `consent:state:expired` still reads the grant as lapsed, since
CC 4.4.3.5.5 gives both causes. Where this holds, "nothing but a row moves state" and "a clock
makes a node act" do not conflict, and two nodes that close a window at different instants
never disagree once both instants have passed. The check is mechanical: such a clause must
carry a `read` beside its `emit`. Today 8 of the encoded clock or fold clauses emit with no
paired verdict (the deletion breach, the promotion overdue, the liveness pair, the decay
stages, the missing subject, the excluded recipient); each is either evidence only, or a place where P1 fails and the text must choose.

**P2. Reactions terminate and every emitter is admissible.** Build the graph with an edge from
family A to family B for each `on …(A) -> emit B`. (a) The graph has no cycle, so one admitted
row causes a bounded number of emitted rows. (b) For each edge, the `role` after `by` is in the
`roles` of B's `attest` transition in `transitions.json` and satisfies B's `signer_rule` cell.
(c) B is a registry family or leaf. On the 113 rows the graph is acyclic (emitted families are
`hard_case:*`, `consent:state:expired`, `consent:decay:*`, `key_grant:*`, `takedown_notice`,
`detection:*`, none of which triggers a clause that emits its own cause).

Smaller checks that fall out: every `expiry required` family has an `on close(expiry)` clause
or is covered by the default row; no family has `expiry forbidden` or `none` together with
`on close(expiry)`; every `dur` resolves to a row of `constants.tsv`, a policy row or a signed
member of a named holder (15 names fail today, listed above); every clock judged `by signed`
has a signed origin.
