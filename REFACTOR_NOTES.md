# Refactor notes for rc19 (working file)

Written 2026-11-11 at `beb888e` for the session that picks the refactor up from a fresh clone.
This file and `handoff/` are working material. **Delete both before the rc19 cut**: the
repository carries no working notes or history language in a release.

A fresh clone has none of the earlier session's memory or scratch files. Everything needed is
here, in `handoff/`, in `formal/derivation/README.md`, in `CHANGELOG.md` (rc19 section) and in the
tracking issue CIRISConstitution#203.

## 1. What rc19 is

- The open refactor edition, branch `rc19`, opened from the rc18 tag. The long-term-support text
  is 1.0-rc18 and is not touched from here.
- Aim (CC#203): each rule stated once at its home as a plain entry; the family model as data;
  every other section applies and cites. Then the decimals are re-cut on the state processor's
  spine (Foundation, the kernel once, the family model as data, mechanism, stewardship) with an
  old-to-new decimal map so every register anchor and every "CC x.y.z" citation in the five
  implementing repositories still resolves.
- Eric's order for the work (2026-11-10): first clarity on the state machine of the
  decentralised network, then how the ethics drives the rules, then validating that the control
  surfaces align with ethical and technical standards.
- "About half the size" is an estimate of what removing duplication saves. It is not a target
  Eric set. Measured so far: length falls from rewriting home sections, not from cutting repeats
  (the repeat sweep saved about 320 words).

## 2. State at `beb888e`

Data side (done, all gated):
- Default row of the family model: `formal/derivation/family_default_row.json`; departures in
  `manifests/family_departures.tsv`; 184 families after the same-stem fold.
- Departure reasons: `formal/derivation/departure_reasons.json` (43 reasons, 10 open cells);
  `tools/build_family_model.py` refuses an unexplained departure. It quotes Part text verbatim,
  so a rewrite must keep the quoted words (see `handoff/entry/pinned.tsv`).
- Signer rules from the text: `formal/derivation/signer_rule_text.tsv`, `transition_text.tsv`;
  five transition cells pinned open in `tools/check_transition_roles.py` (`PINNED`).
- Confirm lookup and way-back cells in `manifests/transitions.json`; 31 `undo` cells are `gap`.
- Screen standard draft imported: `manifests/ui_primitives.json`, `tools/check_ui_primitives.py`.
- Wise Authority seat rule in CC 4.3; root acceptance is the owner's (CC 3.2).

Text side (in progress):
- Inventory: `formal/derivation/rule_inventory.tsv` (4,248 statements; line numbers are those of
  commit `30fddf6` and are stale, match by `gist`).
- **73 sections are landed as entries** (`formal/derivation/rule_entries.tsv`, 3,497 rows; gate
  `tools/check_rule_entries.py`).
- **287 numbered sections are not landed.** `handoff/remaining.tsv` lists them, ranked by the
  words sitting in sentences over 40 words. 190 of them have no over-cap sentence and need only
  registering (rows in `rule_entries.tsv`, no rewrite). 97 need a rewrite.

## 3. Next steps, in order

1. **Register the 190 sections with no over-cap sentence.** For each: one `rule_entries.tsv` row
   per inventory statement whose section is that home, `entry_phrase` a verbatim substring of the
   section. No Part edit, so no regeneration. Do them in a few large commits. A section with no
   inventory statement still needs reading for statements the inventory missed (72 of the 607
   MUST/SHALL/REQUIRED lines had no row on their exact line, mostly table rows).
2. **Rewrite the remaining sections that are free to rewrite**, by the ranking in
   `handoff/remaining.tsv`, in batches of ten to eighteen writers (recipe in section 4).
3. **Held sections: do not rewrite without the stated word.**
   - CC 5.3.3.2.3, 5.3.3.5, 2.6.1.8, and by extension 5.3.3.2.1 and 5.3.3.2.5: the edge 45.1
     work is changing these wire sections. Wait for edge's built layouts and passing
     known-answer tests.
   - CC 2.6.1.7: wire-exact and generated in part (`tools/build_cc_signed_object.py`).
   - CC 1.13.2, 7.5.5, and the other Part 1 and Part 7 stance text (1.3, 1.7, 1.13.4, 1.15.x,
     7.3.x, 7.4, 7.5.x): Eric's voice. Ask him before a rewrite; registering is fine.
4. **Consolidation 3, the one seat rule** (approved by Eric): one rule in the text in place of
   nine per-family gates. A reserved family names one duty; a row is admitted when its signer
   holds a live delegation for that duty from whoever may confer it. Normative edit touching
   CC 3.4.7 and CC 4.4.3.8 item 6; same shape as the seat rule of CC 4.3. It gives about thirty
   reserved-but-ungated families a rule. Registry generator defects to fix with it
   (`tools/build_cc_namespace.py`): wrong reserved rules for `ballot:moderator`,
   `ballot:moderator_acceptance`, `identity:occurrence_revocation`; retirement families lack
   `cc_ref`; retirement cancel-by-withdraw has no verb; a person as conferrer has no role token.
5. **State the default row and its reasons in Part 3.** Needs Eric's word first: several
   defaults are census readings, and a default goes into a Part only when its cell is
   text-sourced.
6. **Consistency pass over the text-against-text conflicts** (section 6). Fix a pair only where
   one side is plainly stale. Bring the value choices to Eric.
7. **CSD/5 remainder:** Part 4 text for the laws (needs Eric's word, the manifest says draft);
   a screen model composed with the kernel (nothing drawn that the door refuses, nothing admitted
   undrawn, a `not_sent` fact never drawn); an issue on the CEWPOS side; the halt-card confirm
   question; the 31 open `undo` cells, each a per-family reading.
8. **Decimal re-cut** on the spine, with the old-to-new map. Last, after the entries are in.
   Then re-run the five Part readers of CC#203 to verify, re-anchor the register, and tell the
   implementing repositories and CEWP which hashes moved.
9. Leftovers from landed rules: `formal/withdraws_admission` notes still say four paths;
   `formal/mesh_net` notes still say "the one audience rule"; CC 7.5.5's decider withdrawing a
   retirement `decided` row is a path outside the table of CC 2.4.1.1; the aggregation and
   weighting rule (CC 4.4.1, 4.4.2) has no entry yet.

## 4. The per-entry recipe

Each section: writer, then an independent second reader, then my own read, then land. "A
condition lost in a rewrite is a protection lost": sections about minors, incapacity, consent
and the halt get the hardest read.

Kit, in `handoff/entry/`:
- `BRIEF.md`, `ADDENDUM.md`, `ADDENDUM3.md`, `ADDENDUM4.md`, `ADDENDUM5.md`: the writer's brief.
  The later addendum wins. **Update the base commit in ADDENDUM5 item 1 and the landed list in
  item 2 before each batch.**
- `WRITER.md`: the writer's launch message. `VLAUNCH.md` and `VERIFY.md`: the second reader's.
  `<main checkout>` in these files is a placeholder: fill in the checkout path.
- `homes.md`: the first five landed entries, the model of form.
- `pinned.tsv`: strings tools quote verbatim from the Parts. An entry must keep them.
- `land.py <name> <part file>`: replaces a section by its rewrite (exact, once).
  `sub.py <file>`: exact one-occurrence replacements. `fixent.py <name>`: repairs entry phrases
  after a fix. `sentdiff.py <name>`: new sentences not found in the old text, for the own read.
  `mech.py`: the mechanical old-against-new check.
- Per-writer input files are not in the kit and are generated per batch, three for each name:
  `<name>.old.md` (the home, a byte-exact slice; `section()` in `tools/check_rule_entries.py`
  gives the bounds), `<name>.worklist.tsv` (inventory rows whose `section` is the home) and
  `<name>.info.txt` (section number, file, word count, counts of MUST NOT / MUST / MAY / SHOULD /
  SHALL / REQUIRED, and the bold leads).

Steps:
1. Pick sections from `handoff/remaining.tsv`. Generate the three input files for each.
2. One writer subagent per section, each in its own git worktree, detached at the base commit.
   Whole-subject mode: the writer carries every worklist row whatever its `rule_key`.
3. One second-reader subagent per section, given only `old.md`, `new.md` and `info.txt`. It
   must not see the writer's report.
4. Read every finding. Read `sentdiff.py` output myself. Fix in `new.md`, then `fixent.py`.
5. Land: `land.py`, append the entries to `formal/derivation/rule_entries.tsv`, add
   `NEIGHBOURS` / `WITHIN` / `BLOCK` in the checker only where needed, one `CHANGELOG.md` bullet
   per entry ("… is one entry (x.y): … No rule changes.").
6. Regenerate and gate (section 5). Commit with the generated manifests. One commit per batch
   or per group; the message names the sections.
7. Record any text-against-text conflict the writer or reader found; resolve none in a rewrite.

What second readers keep catching:
- A pronoun ("It", "This") cut loose by a sentence split. Name the subject.
- A parenthetical reason turned into "which is" inverts it. An em-dash gloss turned into
  "X is a, b, c" narrows a duty.
- A citation moved to the sentence end re-attaches to the wrong clause.
- A "(normative)" lead split into paragraphs leaves the later ones unmarked.
- A point of time or place on a duty ("at attach time", "on receipt") dropped.
- Added summary sentences are where rules change. Add one only where the section has none.
- A writer's "verbatim" claim is checked by script, never trusted.
- Numbered-list continuations need a three-space indent and a blank line before the next number.

## 5. Gates and regeneration

- `handoff/gates.sh` runs every regenerator and every check and prints `fail=N`. Run it before
  every commit. It needs `pdflatex` only for the PDF itself, not for `--write-toc-volumes`.
  After it, run `git status`: it regenerates manifests (for example `manifests/csd4_chain.json`)
  and those go in the same commit.
- After any Part 3 edit: save `manifests/namespace_registry.json` as
  `$HANDOFF_TMP/registry.before.json` first, then `handoff/regen3.sh`. It regenerates the
  registry, the match vectors, the family model, the transitions and the story trace, and
  prints every registry difference. A prose-only edit should show hash members only. CEWP sees
  the transitions hash move.
- `gates.sh` runs the `--check` forms of `build_transitions.py` and `mesh_story.py`, not the
  writers. After a Part 3 or family-model change run both writers first.
- Never run `tools/build_cc_assemble.py` or `tools/build_cc_scaffold.py`: they overwrite every
  Part with placeholders. Never run `build_pdf.py --help`.
- `build_pdf.py`: every non-ASCII glyph needs an entry in its `NUC` map or `pdflatex` halts.
- Never split a markdown table row on `|` naively; cells carry escaped `\|`.
- Part 3: every table row, every `Canonical leaves:` and `Polarity:` line, every fenced block
  and heading stays byte-for-byte; a generator reads them. No new table whose first column
  holds a backticked prefix.
- Adding or removing a section: `constitution/toc.tsv` and all five maps of
  `constitution/codebook.json`, kept bijective, `n_concepts` equal to the row count.
- The `formal/mesh_life` model check takes about two hours; CI runs it. Do not wait on it for
  a text-only commit.
- Before closing a register matter: `tools/check_claims.py`. Before a merge: `build_pdf.py`.

## 6. Conflicts in the text, kept as written

Every rewrite kept both wordings of a disagreement. The full lists are in the writers' and
readers' reports, which are not in this clone; `handoff/sweep_findings.md` holds the repeat
sweep's list, and the items below are the ones that change who is protected or who decides.
Re-derive the rest by reading the landed entries against the sections they cite.

For Eric (value choices):
- The default for a person with no age assurance on record: CC 3.4.13 says under-13 with
  co-sign in one place, `minor` in another, "treated as a child" in a third; CC 3.4.11 says none.
- One live guardian (CC 3.2) against M-of-N co-guardianship (CC 3.4.13); whether a guardian may
  remove themself alone.
- Whether an incapacity binding may ever be plenary ("never plenary by default" against "never
  plenary"); who may petition for one (unstated).
- The instant a halt's reach is judged: receipt at every node holding a live acceptance edge
  (CC 4.2.1.1) against the edge set pinned at `asserted_at` (CC 4.2.1).
- Holder replacement by public record against out of band (CC 4.2.3).
- Is a `consent:replication` grant public at federation scope (CC 3.3.7) or seen only by the
  two nodes (the build)? A public grant naming an unannounced node would list it against
  CC 5.4.6.
- Which request removes a trace, and may a per-key delete remove ordinary rows other parties
  signed about the key.
- Which key signs for a node's or an agent's occurrence revocation (a pinned cell).
- Merit auto-promotion "auto-granted the `moderate` duty" (CC 4.5.13, 4.5.4) against "nobody
  holds a duty they never signed for".

Plainly stale, fixable in a consistency pass (a sample; confirm each against the text):
- Five immediate-removal bases in CC 4.5.3 against four in CC 6.1.2.2.
- "CEG names the three duties" over a four-row table (CC 4.5.5).
- Stale cites: CC 3.1.7 to "CC 2.6.7 `{platform}` discipline" (it is CC 2.3.2.1, also in
  `tools/build_cc_namespace.py`); CC 3.3.6.3 "(CC 3.3.1)" (it is CC 2.6.7); "[CC 4.5.1.1] swap
  test" (it is CC 4.5.1); CC 3.2 cites the public-broadcast exemption as CC 5.3.3 (it is CC 5.1).
- `CLM-link-shaping` wording in `constitution/claims.tsv` is stale against CC 5.4.3.
- Product names standing in Part text (CC 5.1, 5.4.6, 3.4.5): removal is a decision, list them.
- "announce" used in three senses in CC 5.4.6.

## 7. Standing rules for the writing

- Change no rule in a rewrite. Where two sentences disagree, keep both and record it.
- Bring Eric only story-sized value choices. Derive everything else from the grammar, the
  models and the text, and mark a derived reading as mine, not his ruling.
- Read the whole home section for the edge case before sending a derivation to an implementer
  (the "no owner means not rooted" mistake: an ownerless key may trust and serve
  `infrastructure` communities).
- Before ruling text on a wire shape, read the implementing ticket and its design: the wire
  shape is the implementer's.
- Never call the halt an asymmetry: it is the condition of symmetry (CC 1.13.2).
- Never write an AI agent as a person: an agent is "it", a key, an identity.
- No authority rosters: anyone may assert under their own key; admission is trust or consent.
- No lethal action anywhere in the text.
- In the Parts: no product or organisation names, no repo paths, no ticket numbers, no history
  words ("previously", "now", "as of"). British spelling. Two registers: the terse exact entry,
  and plain explanation that cites and never restates. Sentences at most 40 words, mean near 20.
- `CHANGELOG.md` is the release history; one bullet per landed change under "1.0-rc19 (open)".
- Commits go on `rc19` directly. A regenerated manifest goes in the commit that moved it.

## 8. What a fresh session will not have

- The peer sessions for persist, edge, server, agent, verify and client: relays to them went
  through this machine. From a fresh clone, write what an implementer must be told into the
  commit message or an issue on that repository, and tell Eric.
- Local clones of the other repositories (the compliance mappings, the client's CSD/5 branch).
  `tools/check_compliance_wire_forms.py` runs from the committed tables and needs no clone.
- The writers' and readers' per-section reports from the landed batches.

Open with implementers at this commit (each staged in the register, nothing to do in the text
until they answer or ship): persist #1252 (cosign hold, `cosign:{state}`), #1255 (departure
answers), #1256 (group goal vote), #1257 (acceptance is the owner's); server #814 (seat rule).
Told and not yet answered: the other implementers and CEWP have not been told the token moves
of the 192 to 184 family fold.
