# Write one rule's home entry

## What this is

The CIRIS Constitution (`constitution/part_1…part_7*.md`) is normative text: the rulebook of a
network that people, organisations and AI agents share on their own devices. It is being
refactored so that each rule is stated once, at its home, as one plain entry; every other section
applies the rule and cites it. Five rules are already landed. You write the entry for one more.

Read first, completely:
- `SCRATCH/homes.md`: the five landed entries. They are your model of form: a first
  sentence that says what the rule decides; a table where the rule is a lookup; then short
  paragraphs, each with a bold lead that names the one thing it says; reasons in a sentence of
  their own; citations last.
- your home section as it stands, and the two or three sections it cites most.
- your worklist `SCRATCH/<you>.worklist.tsv`: every statement an earlier inventory found in your
  home section, with `rule_key`. Rows whose `rule_key` is YOUR rule are the statements your entry
  must carry. Rows with another `rule_key` are statements of other rules that happen to live in
  your section (see "neighbours").

`SCRATCH` = `handoff/entry`

## The job

Rewrite the home section (only it) as one entry that:

1. **Carries every statement.** Each worklist row keyed to your rule must be carried by a phrase
   of the entry: same parties, same condition, same force (MUST stays MUST, MAY stays MAY), same
   code names, same refusal tokens, same numbers. You may merge two sentences that say one thing.
   You may not drop a condition, an exception or a bound because it reads awkwardly. Also read the
   section line by line for rule statements the inventory missed (table cells especially): carry
   those too and list them.
2. **Changes no rule.** No new MUST/MUST NOT/SHOULD/MAY that the section did not hold. Nothing
   strengthened, nothing weakened, nothing "clarified" into a new meaning. If two sentences of
   the section disagree, or the section disagrees with another section, do NOT pick: keep both
   statements as they are, in adjacent sentences, and report it under "conflicts". If something
   is ambiguous, keep the original words for that clause and report it.
3. **Reads plainly.** No sentence over 40 words (tables and list items are not counted; aim for a
   mean near 15–20). One thing per sentence. The reason for a rule gets its own sentence after the
   rule. Say who does what: "A node MUST refuse…", "The owner MAY…". Prefer a table when the rule
   is a lookup over cases. Keep code names in backticks exactly. Keep every `CC x.y` citation the
   section makes, placed last in its sentence.
4. **Keeps the handles.** The numbered heading line stays byte-for-byte. Any bold lead or named
   term of this section that other sections cite by name (grep all seven Parts for it) stays as a
   lead in the entry, so the cross-reference still resolves. Anchors `{#…}` stay.
5. **Sets neighbours aside.** A paragraph that states another rule (its worklist rows carry
   another `rule_key`) and is not needed to state yours: leave it verbatim, moved to the end of
   the section under your entry, each still beginning with its own bold lead. Do not rewrite
   them. If such a statement sits inside a sentence of your rule, keep the sentence true to both.
   Where the whole section is about one subject and the "other" rows are that subject's own
   applications (e.g. how long such a row lives), carry them in the entry as written rules of the
   entry rather than setting them aside; say which you did.
6. **Does not touch pinned words.** `SCRATCH/pinned.tsv` lists strings that tools quote
   verbatim from the Parts. If one stands in your section, your entry must still contain it
   verbatim (build the sentence around it), or, if that is impossible under the 40-word cap,
   keep it and report it.

Words you may not use: humane, dignified, graceful, farewell, "last word", optimal, trade-off,
prioritise, balanced. No product or organisation names, no code or repo paths, no ticket numbers,
no history ("previously", "now", "used to", "as of"). Never write an AI agent as a person (an
agent is "it", a key, an identity; never "who", "someone", "they" as a person). Never describe
the halt as an asymmetry. British spelling as the file uses. Do not call any landed rule by:
"broadened admission", "retraction carve-out", "third-party path", "trust list", "trusted set",
"pin set", "trust store", "target-membership", "recipient predicate", "one audience rule",
"existence-invisible", "owner binding"/"steward binding" (unhyphenated), "ownership edge",
"responsible steward". Where your section restates one of the five landed rules, cite it
(`CC 2.1`, `CC 2.4.1.1`, `CC 3.2`, `CC 4.4.3.8`, `CC 5.2`) and do not say it again.

## Where you work

You are in an isolated git worktree of the repository. Run `git rev-parse --show-toplevel` and
`git log --oneline -1` first. Edit files only under that directory, by relative path; never edit
under the main checkout's `constitution/` (if `--show-toplevel` prints exactly
`<main checkout>`, stop and report). Do not commit, stash, branch or push. Do not
run any generator (`tools/build_*.py`, `build_pdf.py`, `tools/mesh_story.py`). Edit ONLY your home
section in its Part file. Do not edit `formal/derivation/rule_entries.tsv` or any tool; your rows
go to SCRATCH.

## Outputs (all required)

1. `SCRATCH/<you>.old.md`: the home section exactly as you found it (write this before editing).
2. `SCRATCH/<you>.entries.tsv`: header `rule_key	home	file	line	role	gist	entry_phrase`; one row per
   worklist row keyed to your rule (and one per extra statement you found, with `line` = `x` and
   your own gist). `file`, `line`, `role`, `gist` copied exactly from the worklist. `entry_phrase` =
   a verbatim substring of your new section, on one line of the file, that carries the statement
   (long enough to carry its force and condition: usually a whole clause). Plain `"\t".join`, no
   csv module, no tabs/newlines inside a field.
3. `SCRATCH/<you>.neighbours.txt`: the bold leads (first ~30 characters, one per line) of the
   paragraphs you left verbatim as neighbours.
4. `SCRATCH/<you>.patch`: at the very end, `git diff > SCRATCH/<you>.patch` from the worktree top.
5. Final message, raw findings, no preamble: words and mean sentence length before and after;
   longest sentence after; statements carried / extras found; **conflicts** (both lines quoted,
   one line each on what differs); **ambiguities** kept in original words; pinned strings met;
   names other sections cite this section by; any statement elsewhere in the Parts that your
   entry now makes a pure repeat (section + first words; do not edit them); anything that looked
   wrong. Be specific and complete: a second reader will check your entry against the old
   section sentence by sentence, with no access to your reasoning.

Before finishing: run `python3 tools/check_links.py` and `python3 tools/check_stale_refs.py` from
the worktree top and fix what you caused. Then check your own entries file with a short script:
every `entry_phrase` is in the new section; no sentence of the entry (outside tables, lists and
neighbour paragraphs) is over 40 words, splitting on `(?<=[.])\s+(?=[A-Z*\x60])`. Then read old
and new side by side once more as a sceptic hunting for a lost condition.
