# Lane C: the sections the inventory never read, and three misfiled rows

Read COMMON.md first.

Part 1. These seventeen numbered sections have no row in `rule_inventory.tsv`:
1.13, 1.15, 1.15.9, 1.15.10, 1.16, 1.16.1, 4.5.10.1, 4.5.10.3, 4.5.12, 5.3, 5.3.2.4.5, 7.1,
7.1.6, 7.2, 7.2.8, 7.3.6, 7.5.9. A section runs from its numbered heading to the next numbered
heading at its depth or shallower, or to its first numbered child. Read each one whole.
For each, either list its rule statements or say it states none (a heading over children, a
summary, a pointer). A rule statement is a sentence, clause or table cell that constrains
what a conforming node, signer, reader, steward or implementation does or may do. For each
statement give the inventory's columns exactly as `formal/derivation/README.md` defines them
(`file`, `line` = `x`, `section`, `scope`, `rule_key` from the vocabulary already used in the
table, `column`, `families`, `force`, `role`, `points_to`, `gist` in at most thirty plain
words, `note`) plus `entry_phrase`: a verbatim substring of ONE line of the section that
carries the statement. Also report any sentence over 40 words in these sections (split on a
full stop followed by a capital, an asterisk or a backtick; table rows and "- " list lines
are not counted).

Part 2. Three sections have an inventory row whose statement their text does not carry:
2.6.5, 4.5.9.4, 4.5.12.6. For each such row (compare every row of that `section` against the
section's text today), find the section where the statement actually stands today, by
searching the Parts for the gist's content. Report: the row's gist, the section it is filed
under, the section it is in, and a verbatim phrase there that carries it; or `GONE` if no
section states it any more.

Output: a JSON object at the path your launch message gives:
`{"sections": [{"section", "states_rules": true|false, "why_none", "statements": [ … ],
"over_40": [ … ]}], "misfiled": [{"filed_under", "gist", "found_in", "phrase", "status"}]}`.
Final message: how many sections state rules, how many statements, and the misfiled results. Under 120 words.
