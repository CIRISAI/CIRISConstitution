# Second-reader launch brief (batch 6)

You are an independent second reader of a rewritten section of a normative rulebook. Read
`VERIFY.md` in this folder (SCRATCH) and follow it exactly, with the `<name>` your launch message
gives. `SCRATCH/<name>.info.txt` gives the section number, file and the old size, keyword counts
and bold leads.

You edit nothing in the repository `<main checkout>` and run no git command that
changes anything (no checkout, fetch, commit, stash). To read what another section says, use
`git -C <main checkout> show fc106f9:constitution/part_N_....md` (the main
checkout may have moved on). Do not read any file ending in `.output`, nor any other file or
folder in SCRATCH whose name starts with `<name>` except `.old.md`, `.new.md` and `.info.txt`.

Write your report to `SCRATCH/<name>.verify.md` in the format VERIFY.md gives (first content line
`VERDICT: clean` or `VERDICT: N findings`).

Do all of these, whatever else your launch message asks:
1. A word-level diff of old against new (python difflib over whitespace-split tokens). List every
   change site. For each, say what the old joint was (a consequence, a reason, an example, an
   apposition, a condition) and whether the new wording still says that.
2. Script checks: heading line, fenced blocks, table lines and "- " list lines byte-identical
   where the old section had them; multiset of backticked tokens, of `CC x.y` citations, of
   numbers and of bold spans; counts of MUST NOT / MUST / MAY / SHOULD / SHALL / REQUIRED, each
   on the same party, condition and moment.
3. After every sentence split, read the new sentence alone: does each "It", "This", "That",
   "They", "Such" point at exactly what the old clause's subject was? Does each verb still act
   on the same object? Is each new sentence a sentence?
4. Every added lead, opening sentence or connective: does it state anything the section did not?
   Does a "(normative)" or "(informative)" marker still cover exactly what it covered?
5. Anything replaced by a citation: open the cited section at fc106f9 and confirm it says it
   with every condition.
6. In Part 3: no new table whose first-column cells begin with a backtick.
7. No AI agent written as a person in new wording; the halt never called an asymmetry.
8. Separately list things wrong or self-contradictory in BOTH texts (not the rewrite's fault).

Your final message: the verdict line, the findings table (if any, with a suggested exact repair
for each), the counts, and the both-texts list. Under 400 words.
