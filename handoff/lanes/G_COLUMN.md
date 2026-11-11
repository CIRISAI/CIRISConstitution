# Lane G: design one missing column of the family model

Read COMMON.md first.

Four readers compared every per-family prose statement with the family model's cells. Their
tables are `out_f_cosign.tsv`, `out_f_audience.tsv`, `out_f_erasure.tsv` and
`out_f_lifecycle.tsv` in this folder (columns: column, section, family, verdict, cell_value,
cell_source, prose, proposed_value, cc_ref, quote, note), each with a `.summary.md`. About half
the rows are `RICHER`: the prose says something no column can express. Those rows are the
requirements for new columns. Your launch message names the concept you design.

The aim: a small kernel executes the rules from data. The kernel is rows, folds, transitions
and append: a node holds signed rows; a fold over the rows it holds gives each object's state;
a transition is a row that the door admits when its guard holds; nothing else moves state.
Read CC 4.5.13 from "The state processor (normative)" to "What a preview claims", and
`formal/event_lifecycle/README.md`, for the kernel's own words. Read how existing cells are
written: `manifests/family_model.json` (look at twenty rows across kinds),
`manifests/transitions.json` (a transition has family, verb, from, to, roles, policy, undo,
confirm), `constitution/governance_policy.tsv`, and the cell parsers in
`tools/build_family_model.py`.

Do this:
1. Collect every `RICHER` row, from all four tables, whose `note` or `prose` asks for your
   concept. Be generous: read all the RICHER rows, not a keyword search.
2. Design the column: its name; a closed grammar (a few productions); every token with one
   line on what it means and one line on what the kernel DOES with it (which rows it reads,
   what it compares, what it admits, refuses, computes or emits). Reuse what exists: family
   names of the registry, the five verbs, the policy table's row names, the seven scopes, the
   role tokens of `transitions.json`, the refusal tokens the text already names. Invent a
   token only where nothing existing says it, and say so. No free text inside a value: if a
   statement needs free text to be said, the design has failed for that statement.
3. Encode every collected statement as a value of your column: one TSV row per (family,
   statement): `family	value	cc_ref	quote	source_table	note`. `quote` is the reader's
   verbatim quote where it gave one, else find at most 25 verbatim words in the section.
4. List what you could not encode, grouped by why (needs another column; is really a general
   rule; is ambiguous in the text; contradicts another statement, both quoted).
5. Say where the column lives: a new column of the family model; a member of each
   transition in `transitions.json`; or a new table of its own. Give the reason.
6. Say what a model or a check could now prove that it could not before (one or two
   properties, in the manner of `formal/event_lifecycle`: stated over the data, for every family).

Outputs, both in this folder, names given in your launch message: a markdown design file
(sections 2, 4, 5, 6) and a TSV (section 3). Final message: the grammar in at most ten lines,
how many statements you encoded and how many you could not, and the one decision you most
need from the lead. Under 200 words.
