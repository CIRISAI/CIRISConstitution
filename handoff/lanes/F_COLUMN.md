# Lane F: prose into data, one model column

Read COMMON.md first. Your launch message names your column(s).

For every row of `rule_inventory.tsv` whose `scope` is `family` and whose `column` is yours:
1. Find the statement's words today (via `rule_entries.tsv` `entry_phrase`, else by its `gist`
   in its `section`). If it is gone, verdict `GONE`.
2. For each family the statement names (the `families` field; expand a stem to the registry
   rows it covers; `*` means it is not a per-family statement), read that family's cell for the
   column in `family_model.json`.
3. Verdict, one per (statement, family):
   - `AGREE`: the cell says what the prose says. The prose is then a copy of data.
   - `FILLS`: the cell is `gap`, `generic` or read from code, and the prose gives the value.
     Propose the cell: `proposed_value` in the cell's own vocabulary (look at how other
     families' cells of this column are written and reuse those tokens; do not invent a
     vocabulary), with `cc_ref` and a verbatim `quote` of at most 25 words from the section.
   - `DISAGREE`: the cell and the prose say different things. Quote both. Say which the rest
     of the document supports, if it does.
   - `RICHER`: the prose says something the column's vocabulary cannot express (a condition,
     an exception, a bound). Say exactly what is missing: this is a request for a new token
     or a new column, and is the most valuable finding.
   - `NOT_A_CELL`: the statement is a general rule, a reason or an example, not a per-family value.
4. Do not judge whether the rule is good. Only whether prose and data say the same.

Output: a TSV at the path your launch message gives, header
`column	section	family	verdict	cell_value	cell_source	prose	proposed_value	cc_ref	quote	note`
(no tabs or newlines inside a field; `prose` is at most 30 words, verbatim where possible).

Then a second file beside it, same name with `.summary.md`: counts per verdict; the list of
distinct `RICHER` needs grouped (each is a candidate token or column, with how many
statements want it); the `DISAGREE` rows in full; and the sections where every statement was
`AGREE` or `FILLS` (those sections could become a pointer to the table).

Final message: counts per verdict and the three most important `RICHER` needs. Under 150 words.
