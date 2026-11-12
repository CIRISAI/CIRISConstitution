# Lane G: the `guard` of a transition

Scope: an admission precondition (a row is admitted only if a named row of another family is
held, live or cited) and a predicate on a key the row names. 73 statements collected from the
four readers' `RICHER` rows (all 488 read): 56 encoded in `out_g_guard.tsv` (43 whole, 13
marked `PARTIAL:` in the note), 17 not encoded (section 4).

## 2. The column

Name: **`guard`**. A guard is a conjunction of clauses. Each clause is a query over the rows
the node holds, joined to the row at the door, with a named outcome when it fails. Nothing in
a value is free text: every terminal is a registry family or leaf, a state of
`transitions.json`, a role token, a signer condition, an identity type, a policy row name, a
refusal token, a hard-case kind, or a member name of the signed object or the family's body.

### Grammar

```
guard   := "none" | clause *( " & " clause )
clause  := [ "each(" KEYS ") " ] [ "when(" cond *( "," cond ) ") " ] ( atom | "(" guard ")" ) [ " else " outcome ]
cond    := "verb=" VERB | "leaf=" LEAF *( "|" LEAF ) | "subkind=" SUBKIND | "has=" MEMBER | atom
atom    := rowatom | keyatom
rowatom := QUANT " " FAMILY *( "|" FAMILY ) "@" STATE "[" join *( "," join ) "]" [ " as " NAME ] [ " at " INSTANT ] [ " " window ]
join    := SLOT OP SLOT                     ; left: the required row; right: the row at the door, or NAME "." SLOT
keyatom := [ "not " ] ( ROLE "(" KEY "," TARGET [ ",via=" VIA ] ")" | CONDITION "(" KEY ")" | "type(" KEY "," IDENTITY_TYPE ")" | "signs(" KEY ")" ) [ " at " INSTANT ]
window  := ( "within" | "after" ) "(" POLICY ")"
outcome := ( "refuse" [ "(" TOKEN ")" ] | "exclude" | "advise" ) [ "+" HARD_CASE_KIND ]
```

Terminals:

```
QUANT    := one | all | latest | no | set(MEMBER)
STATE    := admitted | withdrawn | recanted | superseded | landed
SLOT     := id | signer | attested | subject | object | key | ref:MEMBER | ref:* | val:MEMBER | leaf:SEGMENT
OP       := = | >= | <= | in | commits
KEY      := signer | attested | subject | key | val:MEMBER | NAME.signer
KEYS     := subject | val:MEMBER
TARGET   := object | attested | ref:MEMBER | SCOPE
INSTANT  := asserted_at | receipt | its_asserted_at
VERB     := attest | authorize | replace | withdraw | recant            (the five verbs)
ROLE     := the role tokens of transitions.json (member, founder, owner, serve, wa, moderate, subject, winner, holder, steward, …)
CONDITION:= adult | capacitated                                         (the signer rule's conditions)
VIA      := none | delegates_to                                         (the signer rule's `via`)
POLICY   := a row name of constitution/governance_policy.tsv
SCOPE    := one of the seven scopes
```

### What each token means and what the kernel does

The kernel's step takes the held set, one row R and the instant (CC 4.5.13). The guard runs
inside that step, after the signer's roles are folded and before the row is appended.

| token | meaning | the kernel does |
|---|---|---|
| `none` | no guard | nothing; the roles and the policy decide |
| `&` | every clause holds | evaluates clauses left to right; the first failing clause gives the outcome |
| `each(KEYS)` | the clause holds for every key of the set | iterates the keys of R's `subject_key_ids` or of the named member, binding `key`; with `exclude` a failing key is dropped and the others stand |
| `when(…)` | the clause applies only if every cond holds | tests the conds; if one fails the clause is skipped and counts as held |
| `verb=` | R's verb | compares R's verb. Lifts into the transition key when the guard sits on a transition |
| `leaf=` | the value of R's discriminating segment (`{stage}`, `{kind}`, `{outcome}`…) | compares the segment. Lifts into the transition's stage |
| `subkind=` | the `cohort_subkind` of R's object | reads the group record held as head for R's object, compares the member |
| `has=` | R carries the member | tests presence in R's signed bytes |
| `one` | at least one held row satisfies the atom | scans held rows of the named families in the named state whose joins hold; fails if none |
| `all` | every id in the joined list member resolves | for each id in R's `ref:` member, looks the row up; fails on the first that is missing, of another family or in another state |
| `latest` | the row with the greatest `asserted_at` among those matching the `=` joins satisfies the remaining joins | sorts the matches by signed instant, tests the first |
| `no` | no held row satisfies the atom | the same scan; fails if one is found. This is how "not already seated", "no frozen row" and "a duplicate is refused" are said |
| `set(MEMBER)` | R binds a set of rows by digest | collects the held rows matching the joins, hashes their ids in byte order, compares with R's member; fails if the node does not hold exactly that set |
| `FAMILY|FAMILY` | a row of any of the listed families | scans each |
| `@admitted` | the fold over held rows gives the required row state `admitted` at the instant (not withdrawn, recanted or superseded, inside its `valid_until`) | runs the family's lifecycle fold on the candidate |
| `@withdrawn`, `@recanted`, `@superseded` | that state | the same fold, the other answer |
| `@landed` | admitted, and the policy the row runs under is met at the instant (CC 4.5.13, "a policy that is not one voice") | runs the policy's fold over the row's cosignatures or votes. **Invented**: no state token says "moved the object"; needed for a conferral, a cosigned head and a re-bind |
| `as NAME` | names the row found, for a later join or key | binds it |
| `id` | the row's `attestation_id` | compares bytes |
| `signer`, `attested`, `subject` | the three key slots of the signed object (`subject`: any of `subject_key_ids`) | compares key ids |
| `object` | the thing the row is about, the key of its view (group, election, stream, content, period) | compares the segment or member the family's `binds_segment` cell names |
| `key` | the key bound by `each` | compares key ids |
| `ref:MEMBER` | the attestation id or digest the row carries in that member | resolves it among held rows |
| `ref:*` | any reference member of the signed object | tries each. Used only where the text names no member; every use is a question for the body column |
| `val:MEMBER` | the member's value | compares values (integers and byte strings only) |
| `leaf:SEGMENT` | the value of a dimension segment | compares strings |
| `=`, `>=`, `<=` | equality and integer order | integer arithmetic over signed inputs, so every node agrees |
| `in` | the left cell is contained in the right cell | prefix containment of cell ids (location proofs; blocked today, section 4) |
| `commits` | an entry of the left member is the CC 3.2 T3 commitment over the right key's public key material | computes the commitment, searches the member. **Invented** |
| `ROLE(KEY,TARGET)` | the key holds the role toward the target | runs the standing fold, the same one that gives the signer's roles, for another key or another target |
| `via=none` | the role is held directly, never through a delegation | the standing fold with the delegation walk off |
| `CONDITION(KEY)` | the key resolves adult, or capacitated | the age or capacity fold, as for a signer |
| `type(KEY,T)` | the key's record lists the identity type | reads the held key record |
| `signs(KEY)` | the key's signature is on R, as primary or cosigner | verifies the signature among R's own. **Invented**: founding and one amendment seat only those who signed |
| `not` | the key atom fails | negates |
| `at asserted_at` | folds are run as of R's signed instant (the default) | passes R's `asserted_at` to the folds |
| `at receipt` | as of this node's first-held instant | passes the receipt instant |
| `at its_asserted_at` | as of the required row's own signed instant | passes that row's `asserted_at` |
| `within(POLICY)` | this node first held the required row no longer ago than the policy row's `window_secs` | subtracts first-held instant from the step's instant, compares |
| `after(POLICY)` | at least that long ago | the same, the other way |
| `refuse(TOKEN)` | the row is refused by that name | answers the token; `refuse` alone marks a statement whose text names no token, which is a gap to close and not a licence to refuse silently |
| `exclude` | the key is left out of what the row does and the row stands | drops the key from the effect |
| `advise` | the row is admitted; the clause is a SHOULD | admits; the preview lists the clause as missing |
| `+KIND` | the node also emits `hard_case:{kind}` | appends that row |

One rule completes the outcomes and needs no token: when a clause fails because a required row
is **not held**, as opposed to held and failing, the row follows its family's `replication.held`
cell (`settle_on_key`: held until the row arrives; `refuse`). CC 3.3.1 says it for owner-gated
rows: "a grant whose binding rows have not yet arrived is held, as every owner-gated row is".

Three invented tokens (`landed`, `commits`, `signs`) and one wildcard (`ref:*`). Everything
else is an existing vocabulary.

### What the grammar does not say, on purpose

- The signer's own role. `roles` and `conditions` of the transition already say it. A guard
  uses a key atom on `signer` only as a `when` condition or where the text pairs it with a row.
- Counts and thresholds. They are the policy row's; `@landed` asks the policy and never restates it.
- What the row may change (a supersede that grows a roster). That is a bound on the delta.

## 4. What could not be encoded (17 statements)

**Needs a row the registry does not have (7).**
- `location_proof` (6: erasure rows 31, 72, 176, 210, 297; cosign row 120; CC 2.6.6.2, 3.1.3.2,
  3.2, 3.4.2, 4.4.3.2.3). The value is ready and waits on the family name:
  `each(subject) when(leaf=widening,subkind=geographic) (one group:roster@admitted[object=object] as G & latest location_proof@admitted[signer=key,val:cell_id in G.val:geographic_constraint] else refuse)`.
- `external_content` (erasure row 332, CC 4.4.3.10): a distributor attestation chain; neither the content kind nor the chain has a family.
- Also blocks one PARTIAL: the licence guard of `deferral:response` (CC 4.3) needs the seat row, a `delegates_to` edge with no family (cosign row 159).

**Is really a general rule, not a family's (3).**
- A steward binding for every scored agent (erasure rows 223 to 225, CC 3.4.5 restating CC 3.2). It is a rule about agents. As a default-row guard it reads `when(type(attested,agent)) steward(subject,attested)`.
- A live guardian chain for records naming a minor (erasure row 309, CC 4.4.3.2.8): any family in an affiliation that sets `minor_data_handling`. As a default-row guard: `each(subject) when(not adult(key)) one self:delegates_to@admitted[subject=key]`, but the condition is the charter's, not the family's.
- Operator subkind predicates (cosign row 124, CC 4.4.3.2.3): `evaluate_subkind_admission` under `custom:{id}` is an open hook. A closed grammar cannot hold it; the registry would need the operator's guard as data.

**Needs another column (5).**
- The reader's ladder: `build:registered` is the precondition of L4 (erasure row 39, CC 3.1.1). No L4 row is on the wire; this is the fold column's reader composition.
- Partnership: each half names the other (audience row 166, CC 4.4.3.5.3). CC 2.3.2.4 calls ratification consumer policy, so it is a fold, not a door.
- The bound on the T7 recovery widening: adds one founder, removes nothing, changes no M (cosign row 55, CC 3.2). A bound on the delta.
- `founder_only`: the founder is active at the instant of the act (cosign row 64, CC 3.3.4), and the revoker is another live roster key (lifecycle row 125, CC 3.3.6.3). Both are the signer: `roles` with `not_subject`, already columns.
- A pending companion lapses unless resolved inside `valid_until` (lifecycle row 37, CC 3.1.2). A reaction on a deadline.

**Ambiguous in the text (2, and three notes).**
- Capacity at signing (erasure row 261, CC 3.4.12): "with witness co-signature and an auditable `supersedes` lineage" guards "a directive", which is no family.
- The T1 provisional tier (rows 250 to 259): "admissible for the T1 provisional tier only" names a tier that is no value of `{level}`, so the `reversible_pending` alternative cannot be conditioned.
- Which row carries the recovery commitment test: CC 4.2.6 says "The recovery key's record … is accepted only if it hashes to the committed value" and, next, "A recovery is a new version of the accord's roster record, signed under the recovery key alone". Encoded on `group:roster` (leaf `recovery`, not yet a stage) and, from the CC 2.1 gist, on `key:record`.
- 27 of the 40 distinct values (39 of the 56 rows) hold a bare `refuse`: the text refuses and names no token.
- 8 distinct values (9 rows) use `ref:*`: the text says "cites" and names no member.

**Contradicts another statement.** None found inside this concept. One near case is settled by the text itself: CC 3.2 both refuses a record listing a node-bearing key as founder and tells a reader's fold to drop such a seat; the first is the guard, the second is the fold's defence for rows admitted before the rule.

Left to other lanes after reading, never collected here: the eleven `protocol_admissibility` statements (which protocol a group kind may name: a constraint on a body value keyed by kind), the count-set and exception-path needs, and the reactions.

## 5. Where it lives

**A member of each transition in `manifests/transitions.json`, sourced from a text table
`formal/derivation/guard_text.tsv`** (the pattern of `transition_text.tsv`: family, verb,
stage, guard, cc_ref). Not a column of the family model.

Reasons:
1. A guard belongs to a verb and a leaf, not to a family. Of the 56 values, 30 carry
   `verb=` or `leaf=`. On a transition those two conditions are the key and leave the grammar,
   which then keeps only `subkind=`, `has=` and atoms.
2. CC 4.5.13 defines the door as "the row's transition is enabled for the signer's standing".
   `formal/event_lifecycle` proves queue, preview and door are one predicate over a
   transition's fields. A guard anywhere else would be a second predicate the queue does not
   run, and `door_is_queue` would be false of the real door.
3. The preview needs it: "what is still missing" for a guarded item is the list of failing
   clauses, which the same evaluation gives.

The family model gets no new cell. Its `reference` column (`pre:<kind>`) becomes derivable:
the kinds of the families a family's guards name. The guards that are not a family's (section 4,
general rules) go on the default row's transitions. The recovery paths (T7 widening, holder
recovery version) need their own transitions, which the cosign lane's exception path also asks for.

## 6. What a model or check can now prove

**Guard closure (a check over the data, for every family).** Every family named in a guard is
a registry family; every leaf is a leaf of it; every state is a state its lifecycle reaches;
every `ref:` and `val:` member is a member of the body the row carries; every policy is a
table row; every refusal token is in the family's `evidence` cell. Run today it fails in
named places: 27 values with no token, 8 with no member, `recovery` not a stage,
`location_proof` not a family.

**No guard waits on itself (`guard_well_founded`).** The graph "a transition of F requires a row
of G" has no cycle through `one`/`all` edges unless some transition on the cycle has guard
`none` for a first row. So every guarded row has a finite order of admission, and a node that
holds a row's whole guard set admits it whatever order the rows arrived in. With the hold rule
this gives convergence: two nodes holding the same rows admit the same rows.

**Queue completeness survives the guard (`door_is_queue`, extended).** With `admits` taking the
guard as a third conjunct beside roles and state, `queue_sound`, `queue_complete` and
`preview_is_execution` of `formal/event_lifecycle` hold for every one of the 455 transitions,
and a new lemma follows: an item refused by its guard previews exactly its failing clauses.
A second lemma is specific and checkable on the data: **a withdrawal un-admits nothing
already admitted** unless the guard says `at receipt`, since every other guard is judged at
signed instants over signed rows.
