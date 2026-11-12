# Lane K: one rule, every statement of it, read side by side

Read COMMON.md first. Your launch message names a file of rule keys: that is your share.

The first search for contradictions in this text went section by section. This one goes rule by
rule, and it is the second, independent reading. For each rule key in your share:

1. Take every row of `formal/derivation/rule_inventory.tsv` with that `rule_key` (any scope other
   than `family`; include the `family` rows of the same key only as context). Find each
   statement's words today (via `rule_entries.tsv` `entry_phrase`, else by `gist` in its
   `section`; line numbers are stale).
2. Read them together, the home statement (`role` = states) first. Ask of every other statement
   of the same rule, and of every pair of home statements where a key has more than one:
   **could two careful implementers, each reading one of these and not the other, build systems
   that behave differently?** Look for: a different number or window; a different actor or
   quorum; MUST against MAY or SHOULD; a condition present in one and absent in the other; a
   different instant a thing is judged at; a term used for two things, or two terms for one;
   a scope or audience that differs; an exception one states and the other denies.
3. Also compare the statements with the data where data exists for the rule
   (`manifests/governance_policy.json`, `constitution/constants.tsv`, `manifests/transitions.json`,
   `manifests/reactions.json`, `manifests/family_model.json`, `manifests/signed_object.cddl`).
   A difference between text and data is reported with `kind` starting `data:`.
4. Do not report: a restatement that is merely shorter; a difference of emphasis; a rule you
   think unwise. Only two statements that cannot both be followed, or that a reader would
   implement differently.

`formal/derivation/text_conflicts.tsv` holds the 287 conflicts already found (id, sections, the
two sides, resolution). For each thing you report, look there: if it is already listed, put its
id in `known`; if not, put `new`. Report known ones too: the overlap is wanted.

Output: a TSV at the path your launch message gives, header
`rule_key	sections	side_a	side_b	kind	severity	known	note`
- `side_a`, `side_b`: the section (`CC x.y`) then a verbatim quote of at most 30 words, no tab,
  no newline, not crossing a table cell boundary.
- `kind`: number | actor | force | condition | instant | term | scope | exception, or `data:<that>`.
- `severity`: `major` (the two readings give different outcomes for a person or a row: who is
  admitted, who decides, what is kept or deleted, when something lapses) or `minor` (a wording or
  citation difference a careful reader resolves the same way).
- `note`: one line: what differs, and which side the rest of the document supports if it does.

Then a file beside it, same name with `.summary.md`: per rule key, how many statements you read
and how many findings (major and minor, new and known); the major new findings in full; and the
keys you could not finish. Final message under 120 words: statements read, findings by
severity and by new or known.
