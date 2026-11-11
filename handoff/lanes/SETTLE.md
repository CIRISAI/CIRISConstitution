# Settle a place where a rulebook disagrees with itself

The CIRIS Constitution (`<main checkout>/constitution/part_1…part_8*.md`, cited
as "CC x.y.z") is a normative rulebook with formal models under `<main checkout>/formal/`
(one directory per model, each with a README), data tables under `manifests/` and
`formal/derivation/`, and a claim register (`constitution/claims.tsv`) whose `impl:`/`test:`
pointers say what shipped code does (vendored evidence in `constitution/vendor/evidence/`).

Your work file lists conflicts: two wordings of one rule, or a rule one place assumes and no
place states. For each, decide what the document already commits to, from the document itself.
You do not choose values. You find which side the rest of the text, the models, the tables and
the established register rows already take.

For each item:
1. Read both places in the Parts, with their surrounding paragraphs. Confirm the conflict is
   really there today. If one side has since been reworded, say so.
2. Look for what decides it: a more specific or more recent normative statement, a "(normative)"
   lead against an informative one, a table the text calls the single source, a model invariant
   or theorem that already checks one side (name it: file and symbol), an established register
   row, the document's own stated principles (for example: every exit is one step; a quorum's
   act is undone only by a quorum; a seat is withdrawn by whoever conferred it; no node appoints
   anyone; absence of a row is never a grant; the smallest scope is the default; a row is
   judged at its signed instant inside the freshness window; a halt moves no trust state).
3. Give one verdict:
   - `SETTLED_A` / `SETTLED_B`: the document already takes that side; the other wording is stale.
   - `BOTH`: no conflict on a careful reading; the two apply to different cases. Say which cases.
   - `GAP`: nothing decides it and it is not a value choice: propose the rule that follows from
     the principles above, and name the principle.
   - `VALUE`: resolving it changes who is protected, who decides, or what is promised, and the
     document does not decide it. Do not propose; state the two options and who is affected.
   - `FIXED`: the conflict is no longer in the text.
4. For `SETTLED_*` and `GAP`, give the exact repair: `old` (a verbatim substring of ONE line of a
   Part file, long enough to be unique in the file, copied exactly) and `new` (its replacement).
   Keep every sentence under 40 words. Change as little as possible. Never edit inside a fenced
   code block or a table row of Part 3 (a generator reads those); if the stale side is there,
   say so and give no repair. Use British spelling. Never describe the halt as an asymmetry.
   Never write an AI agent as a person.
5. Name the witness that would hold the settled rule: an existing invariant or theorem (file and
   symbol) if one already checks it, else what should be added and where (a cell of
   `manifests/transitions.json` or `formal/derivation/signer_rule_text.tsv`, an invariant in a
   named model, a row of a table).

You are read-only: edit nothing, run no git command that changes anything, spawn no subagents.
Write your results to the output file named in your launch message as JSON: a list of objects
`{"id", "verdict", "reason" (under 60 words, citing sections), "decided_by" (the statement,
table, model symbol or register row that decides it), "file" (Part file name, or ""), "old",
"new", "witness", "changes_rule" (true if a conforming implementation would have to behave
differently from either current wording), "confidence" ("high"|"medium"|"low")}`.
Check with a script before you finish that every non-empty `old` occurs exactly once in `file`.

Your final message: counts per verdict and the three items you were least sure of. Under 120 words.

## Addendum for the citation, count, term, editorial and force items

- A *citation* item is settled by finding the section that does state the cited thing: the
  repair replaces the section number (and its link target) and nothing else. If no section
  states it, the verdict is `GAP` with no repair, and say so.
- A *count* item is settled by counting the list or table the sentence introduces, in the text
  as it stands today, and reading whether the count or the list is the stale side. Where a
  closed set is stated in two sections with different members, find which is the home (a
  registry row, a CDDL, a table the text calls the source) and repair the other.
- A *term* item: one word in several senses. Repair only where one use can take the document's
  own other word for that sense without changing a rule; otherwise `BOTH` and say which senses.
- An *editorial* item names a product or organisation in rule text, history wording, a
  duplicated paragraph or a slip. Product and organisation names: do NOT remove them (that is
  the lead's decision); verdict `VALUE` with reason "product name". Fix slips and wrong
  pointers ("below" that is above).
- A *force* item: the same act stated with a keyword in one place and as a plain sentence or a
  weaker keyword in another. The home statement decides; never raise or lower a keyword at the
  home. Where the non-home sentence is the weaker restatement, the repair makes it cite the
  home rather than change its keyword. Lower-case "must"/"never" inside a "(normative)"
  paragraph: leave, verdict `BOTH`, unless the home uses the capital form for the same act.
- Never repair inside a fenced code block, and never a table row of Part 3. A table row in
  another Part may be repaired if the row is not generated (no "generated" marker near it).
- If two repairs you propose touch the same line, say so in `reason`.

## Addendum for the parameter and data-shape items

- A *parameter* item is one number, default, window or bound stated two ways. Find its home:
  a table the text calls the source (`constitution/governance_policy.tsv`, the window table of
  CC 2.6.7, `formal/derivation/family_default_row.json`), a charter member with a stated
  default, a constant a formal model or a generator reads, or the "(normative)" statement.
  The repair makes the other place agree or cite the home. Also fill these extra keys for
  every parameter item, whatever the verdict: `"constant"` (a short snake_case name for the
  number, e.g. `halt_fuse_secs`), `"value"` (with unit), `"home"` (the decimal of its home
  section, or the data file that holds it), `"read_by"` (models, generators or checks that
  already read it, by path; empty if none). These feed one constants table.
- A *shape_of_data* item is a field, family name, layout, encoding or vocabulary on which the
  text disagrees with a manifest, a CDDL, the registry or another section. Decide which is
  the source of the other: `manifests/namespace_registry.json` is generated FROM Part 3's
  tables by `tools/build_cc_namespace.py`, so a Part 3 table row is the source and the
  registry follows; `manifests/signed_object.cddl` and CC 2.6.1.7's table are generated from
  `constitution/signed_object.tsv`; `manifests/choice_item.cddl` and `manifests/view.cddl`
  are hand-written and normative. Where the stale side is generated, the repair is to its
  source and you say which generator must be re-run. Where the stale side is a fenced block
  or a Part 3 table row, give no `old`/`new`; instead fill `"manual"` with the exact change
  needed and where (file, the line's first 60 characters), so the lead can make it by hand
  and regenerate. Where the wire shape is the implementer's and not built, verdict `VALUE`
  with reason "implementer's shape".
