# Addendum 4 to BRIEF.md, ADDENDUM.md and ADDENDUM3.md (read last; where they differ, this wins)

1. **Base commit is `0763ed9`**, not `009e51c` or `b9e21f8`. At the worktree top run
   `git checkout --detach 0763ed9`, confirm `git log --oneline -1` prints `0763ed9`, and make no
   other git state change. The patch is `git diff 0763ed9 -- <your Part file> > SCRATCH/<you>.patch`.
2. **Twenty-two entries are landed.** Read two or three of them in the Parts as they stand at
   `0763ed9` for the form, in addition to `homes.md`: `CC 2.1`, `CC 2.4.1.1`, `CC 2.6.7`,
   `CC 3.1.3.2`, `CC 3.2` ("Who owns a key" and "Trust-root operational semantics"), `CC 3.4.12`,
   `CC 3.4.13`, `CC 4.2.1`, `CC 4.2.1.1`, `CC 4.2.3`, `CC 4.2.6`, `CC 4.4.3.4.3`, `CC 4.4.3.8`,
   `CC 4.5.1`, `CC 4.5.3`, `CC 4.5.5`, `CC 4.5.13`, `CC 5.1`, `CC 5.2`, `CC 5.4.3`, `CC 5.4.6`,
   `CC 6.1.2`. Where your section restates one, cite it and do not say it again, but only when
   the home entry really carries every condition of your sentence. If your sentence carries a
   condition, party or bound the home entry lacks, keep your sentence.
3. **Mistakes earlier second readers caught. Do not make them.**
   - The three of ADDENDUM3 item 3 (a parenthetical reason turned into "which is …"; an
     apposition list turned into a definition; a citation moved off the clause it supported).
   - **Conditions cut loose from a permission.** Old: "a body MAY ride the link: end-to-end
     encrypted, the room discriminated inside the link encryption, and admitted against the
     table". Wrong: "A body MAY ride the link. The body rides end-to-end encrypted, …". The
     terms of a MAY or a MUST stay grammatically tied to it ("MAY ride the link on three terms.
     It rides … The room is … The receiver admits …" is acceptable; a bare indicative sentence
     two sentences later is not).
   - **Reordering two rule sentences** to get under the word cap. If a later paragraph refers
     to "the sentence above" or calls one sentence the reason for the other, the order is part of
     the meaning. Split the long sentence instead.
   - **A new opening sentence** that lists what the section decides must list all of it or say
     "among other things"; an incomplete list reads as the section's scope.
   - "since X" / "because X" turned into "That is because X" is acceptable only when the new
     sentence directly follows a sentence holding exactly the clauses the reason supported.
4. **"Verbatim" is checked by script** (ADDENDUM3 item 4 stands), and so are keyword counts:
   report MUST NOT / MUST / MAY NOT / MAY / SHOULD / SHALL / REQUIRED before and after.
5. **The 40-word cap** counts a bold or italic lead together with the sentence that follows it
   and counts numbered-list lines ("1. …"). Lines beginning "- " or "|" are not counted. A line
   indented under a list item IS counted.
6. **Part-specific.**
   - Part 3: ADDENDUM item 4 stands in full. Every table row, every line holding
     `Canonical leaves:` or `Polarity:`, every fenced block and every heading line stays
     byte-for-byte; a generator reads them and a registry hash is taken over them. Do not add a
     table whose first column holds a backticked prefix or wire form (the generator would read
     it as registry rows); a new lookup table there uses plain words in its first column, or
     stays prose.
   - Part 2 (`CC 2.6.8`): every byte value, bit position, length, alphabet, checksum constant,
     prefix string and worked example stays exactly as written, on the statement it was on.
   - Part 6 (`CC 6.1.9`): every formula, symbol, threshold and count stays exactly as written.
   - Every Part: keep every refusal token, every `CLM-…` id, every field and code name; none
     may vanish from the section.
7. Mode for this batch is **whole-subject** for everyone: carry EVERY worklist row in the entry,
   whatever its `rule_key`. Set nothing aside as a neighbour.
8. Your section may name products or organisations, or carry history words, that BRIEF bans in
   new text. Do not add any; do not remove one that is in a heading line, a table row or a code
   name. One standing in a prose sentence you rewrite: keep it and list it in your report under
   "product names met". Removing it is a decision for the lead.
