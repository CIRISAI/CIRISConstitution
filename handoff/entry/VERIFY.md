# Check a rewritten rule section against the original

A section of a normative rulebook (the CIRIS Constitution: the rules of a network that people,
organisations and AI agents share on their own devices) was rewritten in plainer language. The
rewrite was required to change no rule. You are the independent second reader. You have not
seen the writer's reasoning and should not look for it. Your job is to find what the rewrite
lost, weakened, strengthened or added. Assume there is something to find.

`SCRATCH` = `handoff/entry`

Files (read-only; you edit nothing in the repository):
- `SCRATCH/<name>.old.md`: the section before.
- `SCRATCH/<name>.new.md`: the section after.
- The seven Parts at `<main checkout>/constitution/part_*.md` (the main checkout
  still holds the OLD text) for looking up what a citation says.

Method. Do it in this order and do all of it.

1. **Old to new, clause by clause.** Go through the old section one sentence at a time, tables
   cell by cell. Break each sentence into its separate rule statements: who (which party or
   key), does or may not do what, to whom, under which condition, with which exception, within
   which bound (days, counts, thresholds), with which force (MUST, MUST NOT, SHOULD, MAY, or a
   plain "is"/"never"), which refusal token or code name. For each, find where the new section
   says it. Verdict per statement: `same`, `weaker` (a condition, exception, party, bound or
   force is missing or softer), `stronger` (force raised or scope widened), `changed` (says
   something else), `lost` (not there), or `cited` (replaced by a citation: then open the cited
   section and confirm it really says that; if it does not, the verdict is `lost`).
2. **New to old.** Go through the new section sentence by sentence. For each rule statement,
   find its source in the old section. Anything with no source is `added`. A reason or
   explanation with no normative force that the old text did not have is `added-gloss`.
3. **Structure.** Labels (T1…, Q1…, (a)…, numbered rules), refusal tokens, code names,
   numbers, `CC x.y` citations and heading lines: list any that moved to a different statement
   than the one they were on, or changed.
4. **Meaning under reordering.** Where the rewrite merged, split or reordered sentences, check
   that "it", "this", "such a row", "the same" still point at the same thing, and that an
   exception still attaches to the rule it limited and to no other.

Be strict about people's protections: a separation of roles (X must not also be Y), a default
that applies when nothing is on record, a time bound, a thing a guardian, steward or root may
never do, a thing a person always keeps. For each of those in the old text, quote where the new
text keeps it.

Write your findings to `SCRATCH/<name>.verify.md` (this one file is the only thing you write):
- a line `VERDICT: clean` or `VERDICT: N findings`;
- a table of every statement that is not `same` or a confirmed `cited`: verdict, old words
  (quoted, with old line number in the old.md file), new words (quoted) or "absent", and one
  line on what differs;
- the count of old statements you checked and how many were `same`/`cited`;
- anything in either text that reads as self-contradictory or wrong, separately (these are not
  the rewrite's fault but are wanted).

Your final message is the content of that file, raw. Do not spawn subagents, do not message
other sessions, do not edit repository files.
