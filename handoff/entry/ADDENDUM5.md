# Addendum 5 to BRIEF.md, ADDENDUM.md, ADDENDUM3.md and ADDENDUM4.md (read last; where they differ, this wins)

1. **Base commit is `fc106f9`**, not `0763ed9`, `009e51c` or `b9e21f8`. At the worktree top run
   `git checkout --detach fc106f9`, confirm `git log --oneline -1` prints `fc106f9`, and make no
   other git state change. The patch is `git diff fc106f9 -- <your Part file> > SCRATCH/<you>.patch`.
2. **Forty-two entries are landed (the list below plus `CC 2.3.2.1`, `CC 2.4.1.2.1`, `CC 2.6.1.3`, `CC 3.1.2.1`, `CC 3.3.6.3`, `CC 3.4.7.3`, `CC 4.5.4`, `CC 5.3.1`, `CC 6.1.2.1.2`, `CC 6.1.5.3`).** Read two or three of them in the Parts as they stand at
   `fc106f9` for the form, in addition to `homes.md`: `CC 2.1`, `CC 2.4.1.1`, `CC 2.6.7`,
   `CC 2.6.8`, `CC 3.1.3.2`, `CC 3.1.7`, `CC 3.2` ("Who owns a key" and "Trust-root operational
   semantics"), `CC 3.3.2`, `CC 3.3.4`, `CC 3.3.6.2`, `CC 3.3.7`, `CC 3.4.5`, `CC 3.4.12`,
   `CC 3.4.13`, `CC 4.2.1`, `CC 4.2.1.1`, `CC 4.2.3`, `CC 4.2.6`, `CC 4.4.3.2.8`, `CC 4.4.3.4.3`,
   `CC 4.4.3.8`, `CC 4.5.1`, `CC 4.5.3`, `CC 4.5.5`, `CC 4.5.13`, `CC 5.1`, `CC 5.2`, `CC 5.3.4`,
   `CC 5.4.3`, `CC 5.4.6`, `CC 6.1.2`, `CC 6.1.9`. Good models of a wire-exact section rewritten
   without moving a byte: `CC 2.6.8`, `CC 4.2.1.1`, `CC 5.3.4`. Where your section restates a
   landed entry, cite it and do not say it again, but only when the home entry really carries
   every condition of your sentence. If your sentence carries a condition, party or bound the
   home entry lacks, keep your sentence.
3. **`SCRATCH/<you>.old.md` and `SCRATCH/<you>.worklist.tsv` are already written** from the
   Part at `fc106f9`. Do not overwrite `old.md`; confirm it is a byte-exact slice of your Part
   file and that it is the whole of your home, and say so in the report. Worklist line numbers
   may be stale: match rows by `gist`.
4. **Home bounds (replaces ADDENDUM item 3).** Your home runs from its numbered heading down to
   the next heading that is (a) numbered and at the home's own depth, or (b) shallower, or (c) a
   numbered child of the home (`<home>.N`), which is not yours. An unnumbered heading inside
   that span, even at the home's own depth, is a block of your section: keep its heading line
   byte-for-byte and in order. `old.md` is exactly that span.
5. **Mistakes earlier second readers caught** (ADDENDUM3 item 3 and ADDENDUM4 item 3 stand in
   full), and four more from the last batch:
   - **A bold lead that says "(normative)" covers its whole paragraph.** If you split the
     paragraph, the pieces must not open with a new bold lead that lacks the marker; open them
     with an italic lead, or keep them in the one paragraph.
   - **A point of time or place attached to a duty is a condition.** "MUST compare … at attach
     time" may not become "MUST compare …". Keep every "before", "at", "on receipt", "at
     admission", "on every step", "while".
   - **An added summary sentence is the likeliest place for a changed rule.** Every second
     reader's findings last batch were in sentences the writer added. Add an opening sentence
     only where the section has none that says what it decides; build it from the section's own
     words; add no closing summary.
   - **"The X is Y" for "X — Y"**: an em-dash gloss is not always an identity. Where the dash
     introduced an example, a consequence or a reason, write it as that.
6. **Verbatim is checked by script**, and so are keyword counts: report MUST NOT / MUST /
   MAY / SHOULD / SHALL / REQUIRED before and after, one line of explanation per difference.
   The intended difference is none.
7. **The 40-word cap** counts a bold or italic lead together with the sentence that follows it
   and counts numbered-list lines ("1. …"). Lines beginning "- " or "|" are not counted; a line
   indented under a list item IS counted (start a carried-over sub-point with "  - " to keep it
   a list item). A long numbered item may become a lead line plus "- " sub-items if the number
   label stays on its statement.
8. **Part-specific.**
   - Part 3: every table row, every line holding `Canonical leaves:` or `Polarity:`, every
     fenced block and every heading line stays byte-for-byte; a generator reads them and a
     registry hash is taken over the section. Do not add a table whose first column holds a
     backticked prefix or wire form; a new lookup table there uses plain words in its first
     column, or stays prose.
   - Parts 2, 5, 6 (wire-exact sections): every byte value, bit position, length, constant,
     formula, symbol, threshold, domain label, field name, preimage, worked example and vector
     stays exactly as written, on the statement it was on. Fenced blocks and existing tables
     stay byte-for-byte (you may move one whole). You are shortening the sentences around the
     exact things, never the exact things.
   - Every Part: keep every refusal token, every `CLM-…` id, every invariant name, every field
     and code name; none may vanish from the section.
9. Mode for this batch is **whole-subject** for everyone: carry EVERY worklist row in the entry,
   whatever its `rule_key`. Set nothing aside as a neighbour.
10. Your section may name products or organisations, or carry history or pending words
    ("staged", "to be replayed", "this edition", "older form"), that BRIEF bans in new text. Do
    not add any; do not remove one. List them in your report under "product names and history
    words met". Removing one is a decision for the lead.
11. **More from the last batch's second readers.**
    - **A pronoun cut loose by a split is the commonest fault.** After you split a sentence, read
      each new sentence alone: if "It", "This", "That" or "They" could point at the noun just
      before it instead of the old subject, name the subject ("The scheme carries…", "That bound
      is…", "A fork attempt never…").
    - **A verb moved to a sentence with a different object changes what it acts on** ("…MUST record
      it, MUST NOT cosign it, counts further attempts, and raises X" split so that "raises X" sits
      with "further attempts"). Keep each verb with its object.
    - **A sentence must stay a sentence**: a label, a colon and a noun phrase is not one.
    - **Continuation lines inside a numbered item** are indented three spaces, with a blank line
      before the next number; nested bullets under a numbered item are indented three spaces.
    - **A "where/when none" fallback is not a peer bullet** of the ordered cases it falls back
      from; keep it attached to the last case or as a continuation line.
    - A reason that followed a colon stays marked as a reason ("That is because…") when split.
12. `SCRATCH/<you>.info.txt` gives your section's size, keyword counts and bold leads as they
    stand. Write `SCRATCH/<you>.new.md` (the new section, a byte-exact slice of your edited Part)
    as a required output.
