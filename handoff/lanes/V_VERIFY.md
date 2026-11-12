# Lane V: try to refute each finding

Read COMMON.md first. Your launch message names a file of findings: each is a claimed contradiction
between two statements of the Constitution (or between a statement and a data manifest), found
by another reader. Your job is to try to make each one go away, and to say honestly whether it does.

For each finding:
1. Read both sections in full, not only the quoted words, and any section either one cites for
   the rule. Read the home of the rule (the section a restating sentence cites).
2. Try each of these refutations: the two statements are about different objects, different
   periods or different scopes; one is a stated exception to the other; one is an example or
   informative text and the other normative; a definition elsewhere makes the two terms the
   same thing; a later sentence in the same section resolves it.
3. Verdict, one of:
   - `NOT_A_CONFLICT`: a refutation holds. Say which, with the sentence that shows it.
   - `STALE`: the two do conflict, and the document itself shows which side is the rule (it is
     the home of the rule, or it carries a normative marker and the other is a summary, or
     three other sections agree with it). Name the side that should change and quote the exact
     sentence that would have to be edited.
   - `DATA`: the text is consistent and a data manifest differs from it. Say which file and cell.
   - `CHOICE`: the two conflict and nothing in the document says which is the rule. State the
     choice in one plain sentence a non-specialist could answer, and what each answer would
     mean for a person using the system.
4. `confidence`: high, medium or low.

Do not soften a real conflict and do not manufacture a refutation. A reader builds from this
text; if two readers would build differently, it is a conflict.

Output: a TSV at the path your launch message gives, header
`id	verdict	confidence	which_side_changes	sentence_to_edit	plain_choice	reasoning`
(no tab or newline in a field; `sentence_to_edit` verbatim from the Part where given;
`reasoning` at most 60 words). Final message under 100 words: counts per verdict.

## From the fifth reading on: say what kind of conflict it is

Add a column `class` after `confidence`, one of:
- `drift`: one rule, and a second statement of it that has fallen out of line (a number, an actor, a condition
  that the home states and another place states differently).
- `interaction`: two rules, each right in its own section, that give different answers in a case neither was
  written for (a general rule meeting a special case; two mechanisms that overlap).
- `gap`: the text is silent on a case and the finding reads the silence two ways.
- `data`: the text is consistent and a manifest differs.
Header then: `id	verdict	confidence	class	which_side_changes	sentence_to_edit	plain_choice	reasoning`.
For an `interaction`, also say in `reasoning` whether a small formal model with both rules in it would have
found it (`model: yes` or `model: no`).
