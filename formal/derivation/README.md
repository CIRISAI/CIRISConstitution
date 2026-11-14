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

Headline numbers: 4,330 statements (Part 3 1,520, Part 4 955, Part 2 678, Part 5 644, Part 6 226,
Part 1 154, Part 7 153); by scope family 1,858, kernel 1,327, mechanism 727, foundation 217,
stewardship 201; by role states 3,335, restates 686, applies 244, exception 65. 206 cut-candidate
blocks, about 260 KB.

Caveats: twelve readers each took one line range, so a rule stated in two ranges may carry two
keys; the `role` column is the reader's judgement of where a rule's home is. Of the 607 lines
that carry MUST, SHALL or REQUIRED, 72 have no row on that exact line, most of them table rows
whose statement is recorded on a neighbouring line. Sweep those before a statement is moved.

## Rule entries

A rule lands in the rulebook register one at a time: its home section becomes one entry, a table
of who may act and short paragraphs that each state one thing with its reason in its own sentence.
`rule_entries.tsv` lists, for each rule landed, every inventory statement whose home is that
section and the phrase of the entry that carries it. `python3 tools/check_rule_entries.py` fails
when a statement has no row, a phrase has left the section, an entry sentence runs past forty
words, or a Part calls a landed rule by a name its entry does not use. Landed: `withdraw` at
CC 2.4.1.1 (24 statements). The 110 statements of that rule made in other sections are read
against the entry: a statement for one family stays with its family, and a sentence that said the
rule again in other words cites the entry.
`trust_fold` at CC 4.4.3.8 (18 statements): who a reader trusts, as a base, the entries the reader
signs, the walk from them and what removing one removes. Two neighbouring rules keep their own
homes and are cited from the entry: the standing of a root (CC 3.2, T1 to T8) and how trusted
statements are aggregated and weighted (CC 4.4.1, 4.4.2).
`audience` at CC 5.2 (17 statements): which nodes a row may reach at each scope, what a node
outside that audience learns, and what moves to a peer unasked. Being in an audience means a row
may be served, not that it is sent, so the Commons is readable by every node and copied to none by
default. Which of a member's nodes a cohort reaches stays with the owner's per-node choice
(CC 6.1.5.3) and is cited from the entry, as is who may carry a sealed frame (CC 5.4.6). The
paragraphs of CC 5.2 on sealing at rest keep their own rule and are not counted in the entry.
`owner_binding` at CC 3.2, under the heading *Who owns a key* (22 statements): the one signed row by
which a person answers for a device or agent key, the three readings every other rule takes from
it, one owner at a time, the first binding, what the binding opens, and the recovery path. CC 3.2
is a long section, so this entry is one headed block of it and the check reads that block alone.
Pairing a new device keeps its own paragraph beside the entry. Stewardship of an adult who has
lost capacity (CC 3.4.12, 35 statements) reuses the same row and lands as its own entry.
`row_shape` at CC 2.1 (43 statements): the members a signed row carries, in three tables: those
every row carries, those any row may carry with the reading when one is absent, and those one
family requires. Each member's type, placement and presence rule stay in the generated table of
CC 2.6.1.7, so the entry says what a member means and the table says how it is written. The
sentences that had sat inside table cells (whom a targeted row may name, what a subject key may
do, the oversight-mode shift, cosignatures beside the row) are short titled paragraphs under the
tables, and the rules they belong to cite them there.

A section with no sentence over forty words is registered as it stands, without a rewrite: a scoring pass proposes, for each inventory statement of the section, the sentence or table cell closest to its gist, and every proposal scoring under 0.6 is read by hand before the rows are appended. 174 sections were registered this way; three were held back because the inventory places a statement in them that their text does not carry (CC 2.6.5, 4.5.9.4, 4.5.12.6).

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

## Consolidation findings and text conflicts

`consolidation_findings.tsv` lists the sentences marked as restating a rule that carry a
condition, party or bound the rule's home lacks (`EXTRA`), or that differ from the home
(`CONFLICT`). `text_conflicts.tsv` lists the places where the text disagrees with itself or
leaves a rule unstated: `shape` is one of citation, count, parameter, authority, temporal,
audience, term, force, shape_of_data, editorial; `for_eric` marks a row whose resolution changes
who is protected, who decides or what is promised; `still_there` says whether a grep found the
wording in the Parts when the table was made; `carrier` names the model, manifest or check
that could hold the settled rule and `witness` what would be added to it; `resolution` is filled when a row is settled, and says whether the settlement was derived from the text or ruled. Both are review
artefacts, one reader's classification, and inputs to decisions, not findings of fact.

Two further tables feed the divergence manifest (`tools/build_divergences.py`).
`seven_rankings_shipped.tsv` lists shipped claims and checks that rank rows, each with what the
text asks instead; the divergence cases cite its items. `models_vs_text.tsv` sets each rule a
model of this repository asserts beside the text it models; it is counted, not entered.

## Cells sourced from the text

`cell_text.tsv` fills a cell of the family model that the text states and the census leaves
open (source `gap` or `generic`): `family`, `column`, `value` in the column's own vocabulary,
`cc_ref`, and a `quote` that must stand verbatim in that section. `tools/build_family_model.py`
applies a row only over an open cell and keeps the census reading as `code`. A cell the census
closes is never overridden here: where text and build differ, that is a departure and takes a
reason in `departure_reasons.json`. `signer_rule_text.tsv` does the same for the signer column,
with its own grammar.

`placement_text.tsv` states where a row goes when its family states no placement of its own.
Its one `default` row gives the placements a family's rows may take and the sentence that leaves
the choice to the emitter. A placement cell the census leaves to the signer takes that default
and is marked `rule: default`. `tools/kernel_closure.py` counts such a cell as a default and not
as a rule. Its `scope` rows give the audience of each `cohort_scope`, each quoting its line of the
CC 5.2 table. The `reach`, `moves` and `copy` rows state whom a row reaches because it names
them, when a row moves to a peer, and whose audience a row joins because another row names it.
The text states the last for a reply only. The build puts the table in `_meta.placement`.
