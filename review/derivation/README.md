# Derivation — do the surfaces and the namespace fall out of the nine promises?

Review artefacts, not normative. Produced 2026-10-12 against the plain rules at rc8
(`review/pieces/00_guarantees_plain.md`), the CSD corpus (CIRISClient `FSD/CSD/` at e040ae76,
87 documents including the seven Registry fold cards), and the namespace registry
(`manifests/namespace_registry.json`, 169 families).

| file | what it holds | how it was made |
|---|---|---|
| `csd_promise_map.tsv` | one row per CSD: id, title, stage, mission, families named, the plain-rule ids that require the surface, necessity (FORCED / SUPPORTS / OPS / NONE), note | one reviewer pass over every CSD against the plain rules |
| `csd_promise_notes.md` | the sub-rules no CSD serves; the operations-only CSDs that still touch a family | same pass |
| `family_kind_verb.tsv` | one row per family: kind of change (the CIRISOntology 11+1), thing / account / record, plausible CEG verbs (5+1), confidence, note | one reviewer pass over the registry and Part 3 |
| `family_kind_grid.md` | the kinds × verbs occupancy grid and a reading of each empty cell (principled or gap) | same pass |
| `reach.py` | computes which families each promise reaches through the Constitution sections its guarantee rows cite (P00 §0b → G rows → decimals → section text), and which families the CSDs name | mechanical; run from the repo root with an output path |

Headline numbers (2026-10-12): 87 CSDs, 29 forced by a promise, 35 supporting one, 23 operations
or unlinked; 14 of 46 sub-rules have no screen, almost all from promises 5, 7, 8 and 9. 169
families: 120 reached by a promise through cited text (74 when catalogue-sized cites are
dropped), 98 named by a CSD, 26 by neither (content types, the identity substrate, telemetry,
the nine echo-chamber detectors). Grid: 48 of 72 cells occupied, 43 of those required by some
promise; `carries` has six families; Model/replace is empty.

Caveats: the kind and necessity columns are one reviewer's judgement at mostly medium
confidence; the promise reach is by section text and whole-section cites inflate it. The
tables are inputs to a ruling, not findings of fact.
