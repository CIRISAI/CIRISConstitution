# Lane G: the `guard` of a transition

Scope: an admission precondition (a row is admitted only if a named row of another family is
held, live or cited) and a predicate on a key the row names. 73 statements collected from the
four readers' `RICHER` rows (all 488 read) in the first pass, 56 encoded and 17 not. The
second pass (last section) covers the rows `out_g_taxonomy.tsv` marks `guard`: the table now
holds 67 rows (50 whole, 17 marked `PARTIAL:`), and 34 statements are not encoded.

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

## Second pass

`out_g_taxonomy.tsv` marks 140 rows `guard` (119 primary, 21 second). Row numbers below are the
taxonomy's `row_index` (1-based). The erasure reader's table has one broken line near row 312,
so from there the taxonomy's index runs four ahead of the 0-based numbers used in sections 2 to 4
and in the TSV's `source_table` column (taxonomy 357 is row 353 there); before it, one ahead.

### Coverage

| | taxonomy rows |
|---|---|
| already encoded by the first pass | 62 |
| encoded by the second pass (11 new TSV rows) | 33 |
| not encoded, already listed in section 4 | 17 |
| not encoded, new (below) | 28 |
| total | 140 |

**Rows the first pass had not encoded (78), by source table and `row_index`.**
- cosign: 121, 125, 207.
- audience: 12, 86, 97, 112, 135, 167.
- erasure: 32, 33, 40, 73, 111 to 130, 149, 150, 155, 156, 160, 177, 178, 180, 189, 211, 212,
  224 to 226, 244, 245, 247, 250, 255, 256, 262, 268 to 275, 294, 295, 298, 299, 308, 310,
  336 to 341.
- lifecycle: 38, 93, 126, 127.

### Added to the grammar

Three additions to the family term of a row atom, and one reading made explicit. No new
production elsewhere.

```
FAMILYSET := FAMILY *( "|" FAMILY ) | "other(" FAMILY *( "|" FAMILY ) ")" | "*"
FAMILY    := a registry family | a registry leaf | STEM ":*"
```

| token | meaning | the kernel does |
|---|---|---|
| `other(F|G|…)` | a row of any registry family except those listed | the same scan as `one`, over the complement. **Added**: the sole-evidence bars cannot be said without a complement |
| `STEM:*` | every registry family under the stem (`ratchet:flag:*`, `detection:*`), as the registry and the text already write it | expands the stem from the registry |
| `*` | a row of any registry family | no family test. **Added** for a row that cites "the content" or "the event" whatever its family |
| `SLOT=ref:MEMBER` where the member is a list | under `one`: some listed id resolves to such a row; under `all`: every listed id does; under `no`: none does | iterates the list; an id that resolves to no held row is skipped by `one` and `no` and fails `all` |

### The evidence bar

The statements say three different things, and one atom says all three:

- "`ratchet:flag:*` cannot be sole evidence for `slashing:*`" (CC 3.1.6): the cited evidence
  includes a row outside the family.
  `one other(ratchet:flag:*)@admitted[id=ref:evidence_refs]`
- "a `slashing:*` row whose entire resolvable evidence set falls within (detector ∪ testimonial),
  with no moderation antecedent, is likewise insufficient" (CC 3.1.6): the complement of a
  union. Two bars asked apart both pass on a mixture, which is the text's own point, so the
  union is one clause with one `other(…)` and never two clauses joined by `&`.
  `one other(ratchet:flag:*|detection:*|testimonial_witness:{kind})@admitted[id=ref:evidence_refs]`
- "Only fires on documented Method-execution spoofing or the `moderation:{allegation_type}`
  allegation types" (CC 3.1.9.2): a required antecedent, which the first-pass grammar already said.
  `one moderation:{allegation_type}@admitted[id=ref:evidence_refs]`

"Resolvable" is the kernel's ordinary reading: `one` scans held rows, so an id that resolves to
nothing held neither helps nor hurts. `@admitted` adds that a withdrawn row grounds nothing.
A general check follows: for every family the text bars as sole evidence, the consuming
family's guard holds an `other(…)` whose list contains it; today that set is `ratchet:flag:*`,
`detection:*`, `testimonial_witness:{kind}` and `seed_holder_voting_alignment:{cell}`, and the
only consumer is `slashing:{outcome}`. All nine slashing rows end in a bare `refuse`: the text
calls the row insufficient and names no token, and says the WA quorum is the gate, so whether
the door refuses or the quorum's readers discount is the open point (it is `refuse` or `advise`,
nothing else changes).

Two readings to settle. CC 3.1.6 lets any row outside detector and testimony ground a slashing
row; CC 3.1.9.2 closes the grounds to a moderation allegation or documented spoofing. The TSV
holds both; if 3.1.9.2 governs, the three `other(…)` values are implied by it and can go.
And "Transparency signal only — not a slashing trigger" (CC 3.1.9.4) is encoded as a bar; the
stronger reading is `no seed_holder_voting_alignment:{cell}@admitted[id=ref:evidence_refs]`.

### Still not encoded from the taxonomy's rows (28 new rows, 17 statements)

| rows | family | why |
|---|---|---|
| erasure 33, 178, 212, 299 | `location_proof` | needs a row: four statements about the proof itself; no registry family, so nothing to hang a transition on |
| erasure 308 | affiliation charter `member_attributes` | needs a row: decryption gated on a member attribute, declared in a charter member with no family |
| erasure 337 to 341 | `detection:*` | ambiguous: "the operational definition lives in the calibration package version pinned via `evidence_refs[]`" names no family for the package and states no refusal. With a family it is `one <package>@admitted[id=ref:evidence_refs]` |
| erasure 268 to 275 | `hardware_custody:{platform}` and the accord families | another column: "admits a class only when the chain for that mechanism verifies" is a cryptographic check of the row's own body, not a row or a key the node holds. The second half fits: `one key:record@admitted[attested=attested]` |
| erasure 189 | `consent:deletion_complete` | another column (evidential weight): "evidence toward D1 and never a substitute for it"; D1 is a duty, and no row consumes the evidence |
| erasure 180 | a public room | another column: a screen keyed on where a row is placed, not on a transition |
| erasure 247 | `age_assurance` | a reader's gate (fold): "a consumer enforcing this checks the resolved level"; the door admits |
| erasure 256 | `capacity_assurance` | per-value cell: what a provider level may support |
| cosign 207 | `membership:{stage}` | count: a delegation chain never counts toward founder quorum. The count set would use `via=none`, which this grammar already has |
| audience 86 | `census:share:{class}` | audience rule: refusal at the receive door for a node that is not the recipient (`federation_addressed_not_recipient`); it tests the receiving node, not a held row |
| audience 112 | `config:{scope}` | placement: the smallest scope reaching the routing peers, a derived value |
| audience 135 | `consent:{kind}`, `agent_files` | body: presence of `subject_key_ids`. Its strength is sayable with this column's outcome (`advise+subject_authority_missing`) once the body column names the test |
| lifecycle 93 | `consent:community_trust` | fold: the new owner revokes by its own later row |
| lifecycle 127 | `identity:occurrence_revocation` | policy: a revocation without the roster door's vote does not evict; that is `@landed`, the policy's own effect |

Statements not encoded in all: 34 (17 from the first pass, 17 here). By cause: needs a row 12,
general rule 3, another column or lane 16, ambiguous 3.

### Changes to first-pass rows

Reading CC 3.1.3.2's refusal list gave names to six clauses, and the TSV is updated:
`membership_proposal_expired` and `membership_declined` (condition 2), `membership_reply_conflict`
(the second reply), `membership_founding_member_unsigned` (founding, which was `exclude` and is
now a refusal), `membership_supersede_cannot_add` (the amendment that seats a signer), each with
`+community_consensus_protocol_violation`, which the text says surfaces every refusal of that
entry; and `deferral_response_unlicensed` (Part 3, the `deferral:response` entry). The same list marks two tokens
RETRYABLE (`membership_acceptance_unresolved`, `membership_proposal_unresolved`): they are the
names of the hold rule's state for those two clauses, which supports reading "not held" apart
from "held and failing".

### The 39 first-pass rows that refused with no token

`TSV row` is the data row of `out_g_guard.tsv` (1-based). "Nearest" is an existing token in the
Parts or in the family's `evidence` cell; "none" means nothing near was found.

| TSV row | family | CC | the refusal's meaning | nearest existing token |
|---|---|---|---|---|
| 3 | `reconsideration:{grounds}` | 3.1.1 | targets no admitted takedown notice | `reconsideration_community_mismatch` (same family, other test) |
| 4 | `capacity_assurance:{level}:…` | 3.1.2 | incapacitated rung lacks exclusion companion | none |
| 5, 6 | `capacity_assurance:{level}:…` | 3.4.12 | incapacitated rung lacks either companion | none |
| 7 | `ballot:moderator_acceptance` | 3.1.3 | bound ballot set not held; signer not winner; lock younger than window | none (`ballot_tally_partials_mismatch` is the tally's) |
| 8 | `ballot:moderator_acceptance` | 4.5.13 | bound ballot set not held | none |
| 9 | `ballot:moderator` | 3.1.3 | ballot ranks a non-member | `ballot_share_recipient_not_tally_member` (shape only) |
| 12, 13 | `membership:{stage}` | 3.1.3.2 | acceptance already spent by widening | `membership_acceptance_mismatch`; still unnamed, now `refuse+community_consensus_protocol_violation` |
| 18 | `membership:{stage}` | 3.1.3.2 | node seat lacks conferring scrub | none |
| 19 | `capacity:relay_delivery` | 3.1.4 | no analyze grant for consumer | `consent_for_key_not_delegated` (consent door, other test) |
| 20 | `rendezvous:route` | 3.1.4 | named node holds no seat | `seat_without_hop_key`; `federation_rendezvous_key_not_an_identity` |
| 21 | `key_grant:{axis}` | 3.1.5 | sealed archive, no release cited | none |
| 23 | `observation:access_assumption` | 3.1.9.4 | a cited grant not live | none |
| 26 | `deferral:response:{outcome}` | 4.3 | signer holds no live licence | **`deferral_response_unlicensed`** (the text's own; filled in) |
| 27, 29 | `takedown_notice:{basis}` | 4.5.5 | signer not the content's subject | `takedown_unauthorised` (evidence cell) |
| 28 | `moderation:{allegation_type}` | 4.5.5 | signer not the content's subject | `takedown_unauthorised` |
| 30 | `delivery_receipt:{stream_id}` | 5.3.3.6 | chunk root never published ("REJECT") | none |
| 32 | `trust:{job}:{version}` | 2.1 | witness not independent of lineage | none |
| 34, 35, 36 | `consent:community_trust` | 3.3.1 | node's grant omits its owner | `community_trust_attester_not_owner` (evidence cell) |
| 37, 38, 39 | `membership:{stage}` | 3.1.3.2, 3.2, 4.4.3.4.2.1 | recovery signer holds no conferral | none |
| 40 to 43 | `accord:lifecycle:{kind}` | 3.4.1, 4.2.1.1, 4.2.6 | confirmation outside the halt's fuse | none |
| 44, 45 | `group:roster` | 3.1.3, 4.2.6 | recovery key matches no commitment | `key_id_fingerprint_mismatch` (key record, other test) |
| 46 | `key:record` | 2.1 | superseding key matches no commitment | `key_id_fingerprint_mismatch` |
| 48 | `group:roster` | 3.1.3.2 | amendment seats a non-signer | **`membership_supersede_cannot_add`** (filled in) |
| 50 | `ownership:{relation}:…` | 3.4.5 | recovery withdrawal cites no adjudication | none |
| 51 | `group:roster` | 4.4.3.4.4 | version does not name held head | `trust_root_head_stale` (the edge's, other test) |
| 52 | `retirement:{state}` | 7.5.5 | withdrawal after a frozen row | none (`registered_family_held_shut` today) |
| 55 | `census:member:share` | 3.1.3 | second share, same token and index | `census_share_duplicate_token`; `ballot_share_duplicate_token` |
| 56 | `membership:{stage}` | 3.1.3.2 | second, opposite reply to proposal | **`membership_reply_conflict`** (filled in) |

Of the 39, three now carry the text's own token; 36 remain unnamed, plus the 9 slashing rows
and the 2 other second-pass rows: 45 TSV rows with a bare `refuse`, and 2 more (12, 13) that
name the hard case and no token.
