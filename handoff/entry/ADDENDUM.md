# Addendum to BRIEF.md (read after it; where they differ, this wins)

1. **Base commit.** Your worktree starts at an old commit. Before reading or editing anything in
   it, run `git checkout --detach b9e21f8` at the worktree top and confirm `git log --oneline -1`
   prints `b9e21f8`. Make no other git state change. The patch is `git diff b9e21f8 -- <your Part
   file> > SCRATCH/<you>.patch`.
2. **Line numbers in the worklist are stale.** Match rows by their `gist` and `section`, not by
   `line`. Copy `file`, `line`, `role`, `gist` into your entries file exactly as the worklist has
   them all the same.
3. **Home means the section's own body.** From its numbered heading down to the next heading of
   any depth that carries a decimal number (a numbered subsection is NOT yours; leave it
   byte-for-byte). Unnumbered sub-headings inside your section are yours; keep their heading
   lines byte-for-byte and in order, because other sections cite them.
   Where your home is one headed block of a larger section, it runs from that heading line to
   the next heading line of any depth.
4. **What a generator reads stays byte-for-byte.** In Part 3, any table row, any line holding
   `Canonical leaves:` or `Polarity:`, and any fenced code block is read by a generator: keep
   each such line exactly as it is (you may move a table or block whole, with its lines in the
   same order). In every Part, keep fenced code blocks byte-for-byte.
5. **Normative words.** Keep each MUST / MUST NOT / SHALL / REQUIRED / SHOULD / MAY as the
   same word on the same duty. Do not turn "MUST" into "is" or "never" into "MUST NOT". Report
   the count of each keyword before and after; a difference needs a line of explanation each.
6. **Labels are handles.** Labels such as `T1`…`T8`, `Q1`…`Q7`, `D1`…, `R1`…, `(a)`…`(f)`, rule
   numbers and refusal tokens (`snake_case` in backticks) are cited from elsewhere and from
   code. Keep every one, on the statement it labelled.
7. **Mode.** Your launch message says either "whole-subject" (carry EVERY worklist row in the
   entry, whatever its `rule_key`; set nothing aside as a neighbour unless the launch message
   names it) or "one rule" (carry the rows keyed to your rule; other paragraphs are neighbours,
   left verbatim after the entry, as BRIEF item 5 says).
8. **This text protects people.** Several of these sections are the rules that protect a child,
   or an adult a court has found unable to decide for themselves, or that say who may change the
   rulebook. A condition lost in a rewrite is a protection lost. When in doubt, keep the original
   clause word for word inside a shorter sentence, and say so in your report.
9. Do not spawn subagents. Do not message other sessions. Do not edit anything but your home
   section in its Part file.
