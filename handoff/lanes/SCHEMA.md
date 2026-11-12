# One schema from the five column designs (working draft, 2026-11-11)

The five designs (`out_g_guard`, `out_g_lifecycle`, `out_g_reaction`, `out_g_fold`,
`out_g_count`) were made apart. This is how they fit into the data the repository already has.
Nothing here is built. It is the plan a build follows, and it is the lead's reading of the
five, to be corrected by the steward.

## The unit is the transition

The kernel is rows, folds, transitions and append. The data follows that:

| What | Where it lives | Sourced from | Why there |
|---|---|---|---|
| Who may sign (roles) | each transition in `manifests/transitions.json` | `signer_rule_text.tsv`, `transition_text.tsv` (exist) | already there |
| **Guard**: what must be held, live or signed for the row to be admitted | each transition, member `guard` | new `formal/derivation/guard_text.tsv` | the door, the queue and the preview read the transition and nothing else; a guard elsewhere is a second predicate |
| **Change**: what a superseding, withdrawing or removing row may do, what it cascades to, what it does to keys | each transition, member `change` | new `formal/derivation/change_text.tsv` | a bound on a change belongs to the verb and leaf that makes it; `undo` and `confirm` already sit there and depend on it |
| **Count**: how a body's act is counted | the family's `count` cell, which resolves to a row of the policy table; each transition's `policy` is derived from it | `cell_text.tsv` (exists) + `constitution/governance_policy.tsv` (extended) | every verb on a cosigned row runs the same count; the policy table already has a generator, a pin, vectors and model instances |
| **Fold**: which rows are read, keyed how, which wins, how values combine, who computes it | the family's `fold` cell, with a default row | `cell_text.tsv` | a fold is a property of a family's rows as a set, shared by all its transitions |
| **Reaction and clock**: expiry, a named window, what a node emits or does when a row lands or an instant passes | new `manifests/reactions.json`, one row per clause, keyed by (family, selector) | new `formal/derivation/reaction_text.tsv` | a reaction relates two families and half its triggers are a clock, which is no transition |
| **Numbers** | `constitution/constants.tsv` | (exists; 18 to add) | a duration anywhere else is a name, never a number |
| **Protocol kinds** and which a group kind may name | new sheet beside the policy table | the count design, section 2.3 | stated eleven times in five sections today |

After this the family model keeps one row per family, and three of its present cells shrink to
generated summaries: `cosign_rule` and `governance` become views of `count`; the `supersedes`,
`rotation_on_removal` and `expires` parts of `lifecycle` become views of `change` and of the
reaction table's expiry clauses; `reference` and `derived` become computable from guards and folds.

## One selector, used everywhere

Every design needed a value that depends on the leaf, the verb, the role or the group kind,
and each wrote it differently (`@segment=leaf:` in the fold, `[leaf]` and `@scope` in the
reaction, `when(leaf=…)` in the guard, `guard => door` in the count, `stages` in the
transitions). One form:

    selector := key "=" value { "|" value } { " & " key "=" value { "|" value } }
    key      := leaf | verb | stage | subkind | scope | group_kind | role | has

- In `transitions.json` the selector is the transition's own key (verb) and its `stages` (leaf).
  A guard or a change written against a leaf lands on that stage and the selector leaves the value.
- In a family cell (`fold`, `count`) the value is a list of arms, `selector => value ; …`,
  the first arm whose selector holds deciding, the last arm bare as the default.
- In `reactions.json` the selector is a field of the row.

A check holds every selector's values to the registry: a leaf is a leaf of the family, a scope
is one of the seven, a group kind is a registered subkind.

## What has to be true before any value lands

1. **No invented name survives unmarked.** The designs invented tokens (`landed`, `commits`,
   `signs`; four refusal tokens in the fold; eight member names written from prose) and used
   `ref:*` where the text names no citing member. Each is matched to the signed-object table
   or the CDDL, or the statement stays prose and is listed as a gap in the text.
2. **Refusals get names.** Forty-five guards refuse with no token in the text. A refusal token
   is on the wire, so the names are proposed here and settled with the store's maintainers;
   until then the guard carries `refuse` bare and a check counts them, the count only falling.
3. **Contradictions the encoding found are settled first** (the licence's winner; licence
   status as a set or the most restrictive; whether a key grant is superseded; the grounds for
   slashing in CC 3.1.6 against CC 3.1.9.2; four in the reaction design). Each goes into
   `formal/derivation/text_conflicts.tsv`.
4. **Each value carries its words.** As in `cell_text.tsv`: a `cc_ref` and a quote that must
   stand verbatim in the section, so an edit to the text that moves a rule fails the build.

## Order of building

Each step is a generator change, a closure check, the values, then the property the design
named, proved or checked. One step at a time through the gates.

1. **Selector and count.** Type the policy table's free-text `standing_set` into `count_set`,
   `voice`, `counted_at`, `voices`, `target_silent`; add the protocol sheet; add the `count`
   cell. Properties: `count_is_total`, `no_lone_voice`, `count_set_is_prior`. First because the
   generator and vectors exist and because the steward's decision on roster widening
   (the declared protocol decides; refused below the corridor's floor) is a row of the sheet.
2. **Guard.** `guard_text.tsv`, the parser in `tools/build_transitions.py`, guard closure,
   then `guard_well_founded` and the extension of `door_is_queue` in `formal/event_lifecycle`.
3. **Change.** `change_text.tsv`; `membership:{stage}` gains its leaves as stages; the key
   effect moves to the leaf that causes it. Properties: a change never needs fewer voices than
   the act it changes; a roster grows only by a consenting key; a removal closes the key at
   every tier that seals.
4. **Fold.** The `fold` cell and its default row. Properties: `fold_commutes`,
   `advisory_moves_nothing`, `ended_stays_ended`.
5. **Reactions.** `reactions.json`; the 18 constants; every clock-caused emit paired with a
   verdict (the one-emitter rule of CC 4.5.13). Properties: no clock-caused row is the only
   cause of a state; reactions terminate and every emitter is admissible.
6. **The 230 ready cells** from the four readers land through `cell_text.tsv` as each column's
   parser is ready. A cell the census closes and the text agrees with gains its `cc_ref`
   without changing value.
7. **The prose.** Only then is a section's per-family prose cut to a citation of its table,
   and the tables are generated into the Parts where a reader needs them.

The signer column (after the seat rule), the body column and the freshness column follow the
same path and are not measured yet.

## What this buys, as measured

Of 1,023 (statement, family) pairs in nine columns: 27% is data now or fills an open cell;
the five designs take it to about 60%; the audience rule, the field rule and the derived value
to about 70%; 23% is general rules, which are the kernel's own statement and not per-family
data. The measure is statements, not how often a rule runs.
