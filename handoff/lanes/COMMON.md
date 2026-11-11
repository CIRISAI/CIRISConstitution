# Common ground for every lane

The CIRIS Constitution is a normative rulebook: `<main checkout>/constitution/part_1…part_8*.md`,
cited as "CC x.y.z". It is being refactored (branch `rc19`) so that each rule is stated once and
everything that can be data is data that a small kernel executes: rows, folds, transitions.

Data and tools you will need (all under `<main checkout>/`):
- `manifests/family_model.json`: one row per row family (184), one cell per column (`placement`,
  `signer_rule`, `subject_rule`, `cosign_rule`, `body`, `freshness`, `lifecycle`, `replication`,
  `projection`, `erasure_route`, `governance`, `evidence`, …). Each cell has `value`, `source`
  (`cc-table`, `code-v61`, `generic`, `prose`, `mixed`, `gap`) and often `note`. `code-v61` means
  the value was read from the shipped store, not from the text.
- `formal/derivation/family_default_row.json` (the default value per column),
  `manifests/family_departures.tsv` (where a family departs), `formal/derivation/departure_reasons.json`
  (why), `formal/derivation/signer_rule_text.tsv` and `transition_text.tsv` (cells sourced from text).
- `manifests/transitions.json` (455 transitions: family, verb, roles, undo, confirm),
  `manifests/namespace_registry.json` (generated from Part 3's tables),
  `constitution/governance_policy.tsv` (the policy numbers).
- `formal/derivation/rule_inventory.tsv`: every rule statement of Parts 1 to 7 (4,248 rows):
  `file` (p1…p7), `line` (STALE: the line at an old commit; find the statement by its `gist`
  inside its `section`), `section`, `scope`, `rule_key`, `column`, `families`, `force`, `role`,
  `points_to`, `gist`, `note`.
- `formal/derivation/rule_entries.tsv`: for each statement, the verbatim phrase of its section
  that carries it (`entry_phrase`). Use this to find a statement's words today.
- `formal/` holds the models, one directory each with a README.

You are read-only on the repository: edit nothing there, run no git command that changes
anything, spawn no subagents, message no other session. You write only the output file(s) your
lane names. Rewrite your output every so often so partial work survives. British spelling.
Never describe the halt as an asymmetry. Never write an AI agent as a person.
