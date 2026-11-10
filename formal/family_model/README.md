# `formal/family_model` — one object beneath every chapter, and the DSL for v62

**The point.** The chapter models of this directory were built one plane at a time. The taxonomy lets them be one object: every scores family is one row of the family model, the row's change half is the 11+1 × 5+1 grammar of CIRISOntology and RATCHET, and every plane model is a view of the one dynamics those rows generate. `FamilyModel.lean` states the grammar half and proves what the v62 manifest's vendor gate enforces; the registry's own classification (`../derivation/family_kind_verb.tsv`, 184 families) is generated into it and checked one theorem per family.

**What is proved.**

| theorem | in plain words |
|---|---|
| `fits_factors` | a family's row factors into a change half (kind, verbs, what it carries) and a reach half (where it lives); the kind constrains only the first |
| `authorize_only_rules_identity_process` | a delegation is a permission, an identity or the right to advance an order; never a fact, a score or a priority |
| `identity_never_recanted` | a name is replaced or revoked, never confessed wrong |
| `identity_never_carried` | nothing carries into Identity: a change smuggled in as a renaming is kind-laundering, the firewalled cell |
| `record_fixes_reach` | a family that maintains the Record keeps erasure at none or legal hold and a byte-equal projection |
| `side_of_kind` | thing or account is a function of kind, with no exception in the registry |
| `fit0` … `fit191`, `registry_fits` | every family of the registry fits its kind profile, the carries firewall and the Record rule |

**The data.** `tools/check_family_kinds.py` reads the derivation table, writes the DATA section of the Lean file, and checks the same rules in Python; CI runs it with `--check` so the two cannot drift. Run: `lean -M 6000 -T 200000 FamilyModel.lean` (1.4 s, 216 MB; the first version was one `decide` over the whole list and is the reason for the cap).

## The DSL, locked for v62

CIRISHolon's closure grammar is the prototype (`engine/crates/holon-closure/src/grammar.rs`, `lean/CIRISHolon/Object.lean`), and it is the shape persist's one interpreter implements. The correspondence, term by term:

| Holon | v62 family model |
|---|---|
| terminals: atoms | signed rows (the 1+4 wire, unchanged) |
| **unit** production: members → a closure, by a condition on the carrier | **admission**: a row is admitted by the family's `signer_rule`, `subject_rule`, `cosign_rule`, `placement`, `freshness` over the carrier (the directory, the roster fold at the row's instant, the delegation walk) |
| **bond** production: two closures → a pair, by a condition on the ledger | **reference**: `reference_rule` and the carries grid, a row bound to the row it names by family, standing and kind; the carry K′→K is a cell of the grid |
| **rewrite** production: a closure changes composition, by a boundary crossed | **lifecycle and governance**: supersede, withdraw, recant by whom (`lifecycle`), and a window crossed (`governance`: enact, cancel, floor, the tally at the window) |
| conditions are the tier's, the grammar contributes the shape and the refusals | conditions are the interpreter's primitives (hybrid verification, the counting predicate, the folds and walks, the halt state, the age and capacity folds); the manifest contributes the shape and the closed refusal tokens |
| a `Grammar` is a list of productions stamped with its tier | the manifest is a list of family rows stamped with `taxonomy_version` and the registry hash |
| an ambiguous grammar reads as ambiguous, never as its first hit (`UnitReading::Ambiguous`) | a row that matches two family rows is refused as ambiguous, never admitted under the first; which family fired must not depend on the order the rows were vendored |
| a tier is a view admitted only when its square commutes: `Closed v T := ∃ h, v ∘ T = h ∘ v` | a **projection** is a view of the rows admitted only when its rebuild commutes with the dynamics: `projection.rebuild = byte_equal` is the closure gate, and persist's parity scan is the harness that hunts the witness pair when it fails (`nonfactoring_iff_not_closed`) |
| failures are certificates: two fine states the view cannot tell apart that evolve to readings it can | a projection defect is reported as the two row sets that rebuild differently, never as a mystery |
| the macro law is forced: a closed view has exactly one dynamics | a byte-equal projection has exactly one rebuild rule, so a ruling that changes a projection changes its row, never its code |

**What this buys.** The chapter models (standing, membership, consent, the moderation plane, the contact plane, the rest) are each a tier: a view of the family-row dynamics that is admitted because its square commutes with the rows it reads. That is Eric's single object instead of disparate models: one dynamics, the rows; one grammar, the kinds and verbs; many views, each closed. A new ruling is a row (unit, bond or rewrite) with its vectors; a new view is a projection with its byte-equal rebuild; code changes only for a new primitive.

**Reference modes.** A row that names another row does so as a precondition (the named row must stand: a live consent, a live proposal, the owner binding a consent reads to resolve its signer) or as a carry (the change arrives from a row of another kind). Only a carry is a cell of the carries grid and needs the verb; a precondition into Identity is not a carry (`precondition_into_identity_is_not_a_carry`). At the v61 head no family carries: the grid's filled cells are all preconditions.

**The manifest, draft 0.** `manifests/family_model.json`, generated by `tools/build_family_model.py` from the CC table and persist's census at the v61 head (vendored as `../derivation/census_v61.tsv`): one row per family over the agreed columns, every cell carrying its value and its source (cc-table, code-v61, prose, gap). Draft 0 is a census, not a rule: it says per column how much of the mesh is already data, how much is bespoke code, and how much nothing enforces, and a ruled version replaces every prose and gap cell with a closed value. The coverage line the generator prints is the number to watch fall. CI checks the file is current (`--check`).

**The default row.** Most families share one value in each of nine columns (placement, subject rule, cosign rule, freshness, lifecycle, replication, projection, erasure route, governance). That value is pinned once in `../derivation/family_default_row.json`, and the generator refuses a default that is not the commonest value of its column. Each family in the manifest lists the columns in which it departs (`departs`), and `manifests/family_departures.tsv` carries the departures alone: a family with no line there is the default row. At this head 106 of 184 families are on the default in all nine columns and 33 depart in one. The defaults are the model's cells as they stand, census readings among them; a default is stated in the Parts only once its cell is sourced from the text.

**Why and when a family departs.** Every departing cell carries a reason, and the generator refuses one that has none. A reason (`../derivation/departure_reasons.json`) says when a family leaves the default and why, names the cells it moves, and rests on one of three bases: words that stand in the Constitution, quoted and checked verbatim against the section named; the census, for a family that is not built, whose cells are unread; or a fact of the store that no rule turns on. The check runs both ways: a cell that leaves the default with no reason fails, and so does a reason whose cell has returned to the default, so a reason cannot outlive what it explained. A reason may fix the cell's value as well as the fact that it moves. Where the text states a rule and the pinned build does not enforce it, the reason says so, says whether the cell records the text or the build, and says how the build differs. A cell the text does not explain is listed open with the question whose answer would give it a reason; an open cell is a finding, never a default. At this head 42 reasons move 198 of the 209 departing cells and 11 are open. `DEPARTURES.md` in this directory is the generated statement, one section per reason, and `manifests/family_departures.tsv` names the reason on every line.

**What it does not yet hold.** The reach half (placement, replication, projection, erasure, freshness) is stated here only for the Record rule; its values per family come from persist's census at the v61 head. The carries grid beyond the Identity cell is data the census and the steward fill. The kind of 7 families is low-confidence in the derivation table and is a ruling each.
