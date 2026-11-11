# Addendum 3 to BRIEF.md and ADDENDUM.md (read last; where they differ, this wins)

1. **Base commit is `009e51c`**, not `b9e21f8`. At the worktree top run
   `git checkout --detach 009e51c`, confirm `git log --oneline -1` prints `009e51c`, and make no
   other git state change. The patch is `git diff 009e51c -- <your Part file> > SCRATCH/<you>.patch`.
2. **Thirteen entries are landed, not five.** Besides `CC 2.1`, `CC 2.4.1.1`, `CC 3.2` (who owns
   a key), `CC 4.4.3.8` and `CC 5.2`, these are now entries: `CC 2.6.7` (which clock, how old a
   row may be), `CC 4.5.1` (who may change the rulebook), `CC 4.4.3.4.3` (delegation), `CC 5.1`
   (the key plane), `CC 3.1.3.2` (joining a family or community), `CC 3.4.13` (a person under
   18), `CC 3.4.12` (an adult under a court's incapacity order), `CC 3.2` "Trust-root operational
   semantics" (T1–T8). Read two or three of them in the Parts as they stand at `009e51c` for the
   form, in addition to `homes.md`. Where your section restates one, cite it; do not say it again
   — but only when the home entry really carries every condition of your sentence. If your
   sentence carries a condition, party or bound the home entry lacks, keep your sentence.
3. **Three mistakes the last batch's second readers caught. Do not make them.**
   - A parenthetical reason turned into "which is …" changes what is asserted. Old: "never by
     the remaining founders lowering M (entrenchment, CC 4.5.1.2)". Wrong: "…lowering M, which is
     entrenchment". Keep a parenthetical citation-with-reason as a parenthesis, or give the reason
     its own sentence that says what the old words said.
   - A dash- or parenthesis-enclosed list after a general term ("every roster-affecting row — a
     seat added, a join, … — MUST …") must not become a definition ("A roster-affecting row is a
     seat added, a join, …"). That narrows the general term to the list. Keep it an apposition:
     a parenthesis, or a lead sentence ending in a colon before the list.
   - A citation stays on the clause it supported. BRIEF says "placed last in its sentence":
     read that as last in its *clause*. If moving it to the sentence end would make it read as
     the authority for a different clause, leave it where it was. The same holds for
     parenthetical examples: "(a verdict field, the served status)" stays a parenthesis on the
     noun it exemplified and does not become "Such a signal is …".
4. **"Verbatim" is checked by script.** If your report says a passage is unchanged, it must be
   byte-identical after whitespace normalisation. If you split, moved or re-punctuated anything
   in it, say exactly what.
5. **The 40-word cap counts an italic or bold lead together with the sentence that follows it**
   ("*What moves the head.* Every …" is one sentence to the checker), and it counts numbered-list
   lines ("1. …"). Lines beginning "- " or "|" are not counted.
6. **Part-specific.** Your section is in Part 4, 5 or 6. Keep every table row and fenced block
   byte-for-byte unless you are turning prose into a new table; a table you did not create keeps
   its rows exactly (you may move it whole). Keep every refusal token, every `CLM-…` id and
   every field name: none may vanish from the section.
7. Mode for this batch is **whole-subject** for everyone: carry EVERY worklist row in the entry,
   whatever its `rule_key`. Set nothing aside as a neighbour.
