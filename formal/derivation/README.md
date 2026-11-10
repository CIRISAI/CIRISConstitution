# Derivation — do the surfaces and the namespace fall out of the promises?

*Run against the first nine promises; promises 10 and 11 are not in these tables.*

Review artefacts, not normative. Produced against the plain rules
(`constitution/digest/00_guarantees_plain.md`), the CSD corpus (CIRISClient `FSD/CSD/` at e040ae76,
87 documents including the seven Registry fold cards), and the namespace registry
(`manifests/namespace_registry.json`, 169 families).

| file | what it holds | how it was made |
|---|---|---|
| `csd_promise_map.tsv` | one row per CSD: id, title, stage, mission, families named, the plain-rule ids that require the surface, necessity (FORCED / SUPPORTS / OPS / NONE), note | one reviewer pass over every CSD against the plain rules |
| `csd_promise_notes.md` | the sub-rules no CSD serves; the operations-only CSDs that still touch a family | same pass |
| `family_kind_verb.tsv` | one row per family: kind of change (the CIRISOntology eleven), thing / account, plausible CEG verbs (5+1), confidence, note, whether the family maintains the Record relation (the +1), and the row it names (`reference`: a precondition `pre:` or a carry `carry:` with the kind named) | one reviewer pass over the registry and Part 3 |
| `family_kind_grid.md` | the kinds × verbs occupancy grid and a reading of each empty cell (principled or gap) | same pass |
| `reach.py` | computes which families each promise reaches through the Constitution sections its guarantee rows cite (P00 §0b → G rows → decimals → section text), and which families the CSDs name | mechanical; run from the repo root with an output path |

Headline numbers: 87 CSDs, 29 forced by a promise, 35 supporting one, 23 operations
or unlinked; 14 of 46 sub-rules have no screen, almost all from promises 5, 7, 8 and 9. 169
families: 120 reached by a promise through cited text (74 when catalogue-sized cites are
dropped), 98 named by a CSD, 26 by neither (content types, the identity substrate, telemetry,
the nine echo-chamber detectors). Grid: 48 of 72 cells occupied, 43 of those required by some
promise; `carries` has six families; Model/replace is empty.

Caveats: the kind and necessity columns are one reviewer's judgement at mostly medium
confidence; the promise reach is by section text and whole-section cites inflate it. The
tables are inputs to a decision, not findings of fact.

## Rule inventory

`rule_inventory.tsv` lists every rule statement in Parts 1 to 7, one row per statement, with line
numbers at commit 30fddf6; a statement added since is noted as such and sits on the line of the
paragraph it joined. `rule_cut_candidates.tsv` lists the blocks of those Parts that state no
rule of their own. Both are review artefacts, not normative.

A rule statement is a sentence, clause or table cell that constrains what a conforming node,
signer, reader, steward or implementation does or may do. A sentence that says a rule again while
pointing elsewhere is a row of its own, so the table counts repeats.

| column | value |
|---|---|
| `file`, `line`, `section` | the Part (`p1` to `p7`), the line the statement starts on, and the decimal of the nearest numbered heading above it |
| `scope` | `kernel` (holds for rows in general), `family` (one family or a few named ones), `mechanism` (bytes, endpoints, transport, media), `stewardship`, `foundation` |
| `rule_key` | the rule the statement belongs to, from a closed vocabulary of 47 keys; `other:<slug>` where none fits (69 rows) |
| `column` | the family-model column a family-scope statement fills, or `none` |
| `families` | the family stems the statement names; `*` for all rows |
| `force` | `MUST`, `MUST_NOT`, `SHOULD`, `MAY`, or `is` for an indicative sentence with rule force |
| `role` | `states` (the rule's own statement), `restates`, `applies` (a general rule applied to one case), `exception` |
| `points_to` | the decimals the statement cites |
| `gist` | the rule in at most thirty plain words, written so that two statements of one rule read alike |
| `note` | a contradiction with another line, an ambiguity, or `table` for a table cell |

The cut-candidates table gives `file`, `line_start`, `line_end`, `kind` (`rationale`,
`restated_block`, `informative`, `example`, `duplicate_table`, `history`), `bytes` and a note.

Headline numbers: 4,248 statements (Part 3 1,525, Part 4 956, Part 5 640, Part 2 601, Part 6 226,
Part 1 153, Part 7 147); by scope family 1,864, kernel 1,246, mechanism 727, foundation 211,
stewardship 200; by role states 3,277, restates 823, applies 83, exception 65. 206 cut-candidate
blocks, about 260 KB.

Caveats: twelve readers each took one line range, so a rule stated in two ranges may carry two
keys; the `role` column is the reader's judgement of where a rule's home is. Of the 607 lines
that carry MUST, SHALL or REQUIRED, 72 have no row on that exact line, most of them table rows
whose statement is recorded on a neighbouring line. Sweep those before a statement is moved.

## Compliance wire forms

Four published works are mapped to the signed-row vocabulary under 27 dimension ids: *Magnifica
Humanitas*, the EU Ethics Guidelines for Trustworthy AI, IEEE Ethically Aligned Design and the
ASEAN Guide on AI Governance and Ethics. The mapping lives outside this repository
(`ciris-response-magnifica-humanitas`, read at commit 5465f48). Two tables carry what it leans on:

| File | Rows | What a row is |
|---|---|---|
| `compliance_dimensions.tsv` | 27 | a dimension id, its stem and tier, which works attest it, the registry families that carry the stem, the Part 3 sections that define them |
| `compliance_wire_forms.tsv` | 1,059 | one wire form a work's mapping cites, the number of mapped lines citing it, the registry family it resolves to, and the answer: `resolves`, `open` (open vocabulary no row claims) or the refusal token |

`python3 tools/check_compliance_wire_forms.py` re-resolves every form against the generated
registry and fails when a dimension loses its family or anchor, a cited section is no longer a
Part 3 heading, a resolving form stops resolving, or any answer changes. `--write` records a
changed answer once it has been read; `--extract <dir>` rebuilds both tables from a checkout of
the mapping.

Readings: 26 of the 27 stems have registered families; the 27th (`accountability`) is structural
and its evidence is the audit chain. Of 1,344 mapped lines 1,027 resolve (*Magnifica Humanitas*
295, EU 208, IEEE 348, ASEAN 176). The 317 that do not are forms the mapping wrote to an earlier
arity or case: a `method:` form without its rung or version segment, a `transparency_log:` or
`attestation:` leaf beyond the registered ones, an upper-case segment, a `consent:` or
`prohibited:` leaf the closed vocabularies do not carry. Those are for the mapping to relabel;
the check holds them at their present answer so a change in either direction is seen.

