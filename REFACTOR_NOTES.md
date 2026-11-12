# Refactor notes for rc19 (working file)

Written 2026-11-11 at `beb888e`, updated the same day after the register pass, for the session that picks the refactor up from a fresh clone.
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

## 2. State

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
- **333 sections are held by the entry check** (`formal/derivation/rule_entries.tsv`): 73
  rewritten as entries, 174 registered as they stand, 86 registered after their over-long
  sentences were split (Eric, 2026-11-11: knock the mechanicals out so the rest can be
  analysed; the stance text was split with every word of substance kept). Four sentences are
  kept whole by name (`EXEMPT` in the check). A bold lead ending in a full stop counts as its
  own sentence.
- **27 numbered sections are not landed** (`handoff/remaining.tsv`):
  - 7 wire sections with sentences over 40 words, held for edge 45.1 and for being wire-exact:
    CC 2.6.1.7, 2.6.1.8, 5.3.3.2.1, 5.3.3.2.2, 5.3.3.2.3, 5.3.3.2.5, 5.3.3.5 (about 60
    sentences, several past 100 words; byte layouts written as prose that want tables, not
    splits).
  - 17 with no inventory statement (1.13, 1.15, 1.15.9, 1.15.10, 1.16, 1.16.1, 4.5.10.1,
    4.5.10.3, 4.5.12, 5.3, 5.3.2.4.5, 7.1, 7.1.6, 7.2, 7.2.8, 7.3.6, 7.5.9): read each for
    statements the inventory missed, or record that it states no rule.
  - 3 with an inventory statement their text does not carry (2.6.5, 4.5.9.4, 4.5.12.6): correct
    the inventory row's section first.
- What the check does and does not show: every inventory statement is pinned to a phrase of
  its section, so text can be moved without losing a rule. It does not show that a rule is
  stated once. The document is no shorter. The consolidation is the work that follows.

## 2a. Scope of RC19, as Eric set it on 2026-11-11

Eric: knock the mechanicals out so the rest can be analysed; focus on clarity, accuracy and
consolidation; harvest the text conflicts as opportunities to add formalizations; everything
that can be turned into data eventually is. Asked whether the decimal re-cut should wait for a
later edition with the prose-into-data pass, he ruled that leaving the re-cut out would be
confusing and the data pass folds into RC19: "just do it fully". So RC19 carries all of it, in
this order, and the decimals are cut once, last:

1. Mechanical pass (done apart from the wire sections edge is changing).
2. Accuracy: the conflicts where one side is plainly stale.
3. Consolidation: every sentence that restates a rule cites its home, or its extra condition
   moves into the home; then a gate that refuses an uncited restatement.
4. Formalization harvest: the conflicts table (`formal/derivation/`, shape, carrier, witness);
   each temporal, authority and audience conflict becomes an invariant, a table cell or a
   departure reason; each parameter conflict a row of one constants table; each data-shape
   conflict a CDDL member or vector; counts, citations, terms and keyword force become lints.
5. Prose into data: per-family statements (shape, signer, audience, lifecycle, erasure,
   freshness) move from Part prose into the family model and its generated tables; the Parts
   keep the rule once and cite the table.
6. The one seat rule.
7. The decimal re-cut on the spine, with the old-to-new map, once the sections are settled.
8. Cut mechanics.

CIRISClient PR #297 (branch feat/csd5-export) carries the join export with scope per write.

## 3. Next steps, in order

1. **The mechanical pass is done** apart from the 27 sections of section 2. The registered
   phrases were matched by score (`handoff/register.py`) and only the low scores were read by
   hand, so a phrase may sit in the right paragraph on the wrong sentence.
2. **The analysis the mechanical pass was for.** In this order: (a) the paragraphs that are hard
   for structure, not length: CC 1.13.2 (one paragraph makes about ten claims), CC 7.5.5 (wire
   mechanism for the retirement record sits in Part 7 beside the stance), CC 1.15.5; (b) the
   text-against-text conflicts of section 6; (c) the duplication: pivot `rule_entries.tsv` by
   `rule_key` to list every rule stated in more than one home, and decide each rule's one home.
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
- CC 5.4.2: "strangers hold nothing" beside "the bytes they hold remain sealed" (residue of the
  time community holding claims were public); "(keep/evict decision)" has lost its subject.
- CC 5.3.6.1: the list of admission refusal tokens omits `federation_withdraws_not_admitted`
  and `federation_addressed_not_recipient` of Part 2.
- CC 4.2.2 carries `hardware_class` "as a JSON property on a signed key record … and inside
  `attestation_evidence`"; CC 4.2.2.1 says it "is not a directory column".
- CC 1.7 credits the impossibility of fair exchange without a trusted third party to
  Even–Goldreich–Lempel; a reader recalls it as Even–Yacobi (1980) or Pagnia–Gärtner (1999).
  Not looked up. Check against CC 8.6.1 before the cut.
- CC 1.16.4 paraphrases CC 1.9 more broadly than 1.9 states it ("the agent halts" for "halt the
  action in question"; "a defined threshold" for "deployment-defined thresholds").
- CC 7.5.3.1 "five-level scale modeled on SAE J3016 (L0–L5)": six levels cited, five used.
- CC 7.5.5: "the consciousness indicators below" points at no list; "take none of it" is loose
  between the window and the postponement. CC 1.13.2 cites CC 6.1.2.1.2 twice in two clauses
  and cites itself "above".
- CC 5.3.2.2 cites the subject's withdrawal authority as "rule 2" in one sentence and "rule 2 or
  3" in the next; CC 5.3.3.1 says "binding and nonce pinned here" and pins no nonce there.
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

Owed at the cut, asked by the client session for Eric (2026-11-11): when the namespace work is
final (the fold, the one seat rule, the decimal re-cut), file an issue on CIRISAI/CIRISClient
giving the commit or tag to pin, the sha256 of `manifests/namespace_registry.json`,
`manifests/transitions.json` and `manifests/ui_primitives.json` there, the family rows renamed
or folded since v1.0-rc6 (the client's pin, 158 families), and the old-to-new decimal map. The
client's guide was told not to print a CC section number for CSD/5 until the laws are in a Part.

CSD/5 and the formal work (answered to the client session 2026-11-11; my readings, not Eric's):
- `formal/event_lifecycle` carries L6 whole, L5 (offered iff admitted) and the first half of L7
  (the previewed view is the door's). It does not carry "sent only while the preview is held",
  nor L12: `answer.shown_digest` binds an answer to the item as served, and no text says who
  checks it. That is a gap to close before L12 is an obligation in a Part.
- `manifests/choice_item.cddl` `write.verb` lists six verbs (it has `carry`);
  `manifests/ui_primitives.json` `write_verbs` lists five. Reconcile.
- Offered to the client and not built: a generated list of theorem names (file, line) to pin as
  data; a new ADEQUACY row for "what was offered is what the door admits, and what was shown is
  what was signed" (not A13); the screen model as a refinement from a card's `issue` to the
  door's `execute`, per-card in TLA+, the general statement in Lean. The client would export
  each card's writes as (family, verb, scope, confirm, sends, shows) with guards and bindings.

Halt reach, ruled by Eric 2026-11-11: it takes effect the moment the halt is active, captured
at the store. Landed per node (the store admits the row, latches, records the instant); model
`formal/accord_halt/AccordHaltReach.tla`. Owed: tell persist and server (CLM-accord-reach is
staged on CIRISPersist#803; the store must record the latch instant and judge the edge then;
Server's `accord.rs` pointers were written against the `asserted_at` wording). Still open in
the same section: no rule for a halt row past `valid_until`; no rule for a duplicate
`invocation_id` on `lifecycle:confirmed`.

Accord carriage at the build, from edge's trace of release/45.0.0 (2026-11-11): no accord row
is in `required_rows`; the accord family moves unasked by prefix only where a peer's walk
reaches; a first-contact peer is offered no accord row, the halt included; the relay gate is
off unless a host sets it; `accord_decision` does not replicate on edge's plane; the quorum
evidence plane is served to anyone who asks (conforming). So a v45 halt reaches consented,
Rooted peers and serve seats, not every node holding an edge. Tracked as CIRISEdge#981;
`CLM-stranger-carries-consent-free` is staged on it and `CLM-moves-requested-required-appropriate`
is narrowed to what edge's pointers do. Open at edge: a flood bound on the stranger path, and
how `accord_decision` objects travel (needs a persist door). For Eric: when #981 is scheduled.

The election against the old promotion rule: `formal/mesh_net` `ModLapse` still promotes in the
same step and `CLM-promotion-cohort-standing` (established, persist) still claims it. To do:
change the model's lapse to lock and elect with the invariant "no unmoderated room is
writable", and ask persist whether `check_promotion_cohort_standing` orders a ballot or appoints.

Persist issue opened at Eric's word, 2026-11-11: CIRISPersist#1259 (halt latch instant in the
store; split of `may_relay_accord_object` into signer-seated and local-edge; a door for
`accord_decision` objects and for the holders' key records and seating roster version; whether
`check_promotion_cohort_standing` seats or only checks standing). Server's facts are on it as
a comment: the server judges a halt at receipt, records `latched_at` and `received_at` in a
latch file of its own, and tests no acceptance edge. So "holds a live edge at that instant" is
checked by nothing in the build today; `CLM-accord-reach` stays staged.

Age default, ruled by Eric 2026-11-11: no assurance reads as under 13 with co-sign; a phone
added to a desktop user's self produces the platform signal and it applies to the whole self
roster; ground it in law. Landed in CC 3.4.13 and 3.4.11 with `formal/age_assurance/AgeBand.lean`.
The no-estimation rule (a node never estimates age from behaviour; a platform that does attests
at the provider rung) was my addition to the recommendation he accepted: confirm it stands.
His context: platforms now run AI to catch children posing as teens and teens as adults, after
the 2026 verdicts and settlements. Owed: `CLM-child-protection` rests on persist's `is_minor`;
ask whether it reads an absent assurance as under 13 and whether the assurance is resolved per
identity across the roster.

Incapacity, 2026-11-11. Eric confirmed the no-estimation rule for age. On CC 3.4.12 he said
telling a ward's community could violate the ward's rights and asked for the ward to have a
choice. Landed: standing to petition is the court's law; the row names the petitioner; who is
told is the ward's choice, private by default. Mine and not his: the private default, and that
a removal during a live binding needs the champion's confirmation. Owed: the petitioner member
and the told-list are the implementer's to shape (add to CIRISPersist#1259 or its own ticket);
the fenced predicate of 3.4.12 has no `require` for the petitioner or the champion.

Members' check on moderators, 2026-11-11. Eric confirmed the amendment (relayed first by the
server session, aimed at Server 0.6) and agreed the shape I proposed: the accord's pattern at
room scope. Landed in CC 4.5.13 with policy rows `moderation_overturn` (strict majority of the
roster at the act's instant, 48 h, floor two voices) and `moderator_recall` (more than 2/3
of the standing roster, cosigned, 72 h; elected moderators only). Restored items return
consent-gated; immediate-removal bases and private-report rulings are not objectable; no
second bite. Open by his agreement: the founder's seat (held at zero hops, not recallable),
stated as a declared default; whether it ever becomes the room's is a decision of its own,
and CC 4.5.1's register does not carry it yet. Owed: a register row staged on the server's
ticket (none named yet); a model (the lift as a mirror row beside `accord_halt`; the fixed
electorate; no second bite); persist facts from the server: a cohort declares reverse quorum
only through `consensus_protocol`, and the `moderation_action` 48 h absence fallback is not
built. Recusal at room scope is defined in CC 4.5.4 (derived).

## State at the end of 2026-11-11 (rc19 at 13c448b)

- Mechanical pass: done (333 of 360 sections held; 27 left as listed in section 2).
- Consolidation: 62 restatements cite their home; 39 findings in
  `formal/derivation/consolidation_findings.tsv` are unresolved; the gate that refuses an
  uncited restatement is not written.
- Conflicts (`formal/derivation/text_conflicts.tsv`, 282 rows, `resolution` column): 120
  settled or ruled, 50 no conflict on reading, 12 already fixed, 12 proposed and not applied
  (each says why), 7 waiting on Eric, 81 open. The open ones are the data pass: 37
  text-against-manifest (`shape_of_data`), 31 two-values-for-one-number (`parameter`), 11
  authority rows that wait on field shapes, and two of Eric's.
- Method that worked for the conflicts: one read-only agent per shape with
  `$scratch/settle/BRIEF.md` (verdicts SETTLED_A/B, BOTH, GAP, VALUE, FIXED; an exact `old`
  line and `new`; what decides it; a witness), then my read of every repair, then a guarded
  apply (one occurrence, never in a fence, never a Part 3 table row), then repair of the
  register phrases the edit moved, then regen and gates. The brief is not in the repo:
  rebuild it from this description.
- Models added today: `formal/accord_halt/AccordHaltReach.tla`, `formal/age_assurance/AgeBand.lean`,
  `formal/moderation_lift/ModerationLift.tla`; `formal/mesh_net` locks and elects.
- Waiting on Eric: a halt row arriving after its `valid_until` (I recommended it still
  fires); whether a self-asserted canonical binding opens a withdrawal rule (I recommended
  no); six product or organisation names in rule text (replace by role words, or keep);
  the founder's seat (open by agreement).
- Waiting on implementers: CIRISPersist#1259 (six items), #1260 (room content bound to no
  community), CIRISEdge#981 (accord carriage), CIRISServer#873 (members' lift).
- Next: the data pass. Start with one constants table for the 31 `parameter` rows (each
  number one home, generated into the text and read by the models), then the 37
  `shape_of_data` rows as CDDL members or vectors, then prose into the family model one
  column at a time (signer rules first), then the one seat rule, then the decimal re-cut.

## Lanes, 2026-11-11 evening (rc19 at 9eda7e0 and after)

Eric: "this refactor is our critical path now, I theorize if we can get all our prose into data
the kernel can do 60%+ of our cycles." All lanes were launched in parallel; edits go through
one gate. Briefs and the outputs that are design input are in `handoff/lanes/`.

- Done: every conflict has an outcome; 341 sections held, 12 state no rule, 7 wire sections
  wait on edge; consolidation findings settled; the uncited-restatement gate (7 pinned).
- Prose into data. The engine is `formal/derivation/cell_text.tsv` (see the derivation README).
  Each column lane writes a TSV of (statement, family) verdicts: AGREE (prose is a copy),
  FILLS (becomes a `cell_text.tsv` row), DISAGREE, RICHER (the column's vocabulary cannot say
  it: a request for a token or a column), NOT_A_CELL (a general rule: stated once).
  First column back, cosign and governance (`handoff/lanes/out_f_cosign.*`): of 208 pairs,
  36 agree, 26 fill, 66 are not cells, 7 disagree, 73 are richer than the vocabulary. The
  three missing concepts: who is counted (the count set), which protocols a group kind may
  name and how a protocol binds to the policy table's five numbers, and whose protocol
  applies. Next for this column: land the 26 FILLS as rows; design the three tokens.
  Columns still out when this was written: lifecycle; replication, placement, subject;
  projection, erasure, evidence. Held: signer (after the seat rule), body, freshness.
- The one seat rule: `handoff/lanes/out_e1.md`. Nine gates replaced, the accord's kept; 25 of
  88 reserved families read wholly by the rule and one arm of 9 more; 46 keep a relation
  rule; eight flips; eight decisions for Eric (D1 to D8 in section 6 of that file). Nothing
  lands until he answers them.
- The hard paragraphs: `handoff/lanes/out_h.md`, a proposed order for CC 1.13.2, 7.5.5 and
  1.15.5 with no rewording, and 25 contradictions found in them. Needs Eric's approval.
- `handoff/fix_entries.py` repairs register phrases after any text edit; run it before the
  entry check.

## The data pass measured, and the five column designs (2026-11-11 night)

Four readers compared 1,023 (statement, family) pairs in nine model columns with the model's
cells (`handoff/lanes/out_f_*.tsv`): 273 are data already or fill an open cell, 231 are general
rules, 27 disagree, 491 say something no column can express. A completeness check classified
the 491 (`out_g_taxonomy.*`): guard 119, fold 88, reaction 63, count 41, change constraint 32,
then a family with no model row 30, evidential weight 22, plain cell 20, policy row 16,
audience rule 14, field rule 12, derived value 11, keyed cell 11, erasure effect 10, screen
duty 2. Executable from data: 420 yes, 70 partly, 1 no. So the five concepts take per-family
prose from 27% to about 60% data, and three smaller ones to about 70%.

Five designs, each a closed grammar with every statement encoded and the failures listed:
`out_g_guard.*` (on each transition; second pass asked to cover all 119 and the slashing
evidence bars), `out_g_fold.*` (a column of the family model), `out_g_reaction.*` (expiry,
clock, reaction; durations only by name; wants 18 constants), `out_g_lifecycle.*` (the
`change` column, on each transition), `out_g_count.*` (typed columns and twelve rows for the
policy table, a seven-row protocol table, a sheet of which protocol a group kind may name).
Not integrated: the five were designed apart. To do before anything lands: one schema (the
transition carries guard, change and reaction; the family carries fold; the policy table
carries the count); one shared way to key a cell by leaf, role or group kind; every invented
token and member matched to the CDDL or dropped; the refusal tokens the text never names
(39 guards refuse with none); then generators and checks, then the cells, then the prose
cut to a citation of the table.

Edge v45.0.0 is tagged (merge commit a54c6a2); the register is not re-pinned to it yet (a
cut step). Nothing about accord carriage is claimed for it.

Decisions waiting on Eric, gathered: the seat rule's D1 to D8 (`out_e1.md` section 6); who
emits a row a clock or a fold causes (the admitting door, peers re-derive: recommended; same
question as D5); what decides a roster widening (the group's declared protocol, or the
`community_invite` policy row's fractions); one guardian or a set; whether a steward-bound
agent accepts membership under its own key; a halt row past `valid_until`; whether a
canonical binding opens a withdrawal rule; six product names in rule text; the entrenched
list of CC 4.2.1 and three wordings in CC 4.5.1; the hard-paragraph order (`out_h.md`);
the founder's seat.

Eric, 2026-11-11 night. (1) Who emits a row a clock or a fold causes: "agreed" to the
recommendation: the door the causing row first entered emits, peers re-derive; landed in
CC 4.5.13 and 3.3.1. Consequence stated to him: a deletion breach is then recorded by the
breaching producer's own node or not at all, and what holds the producer to account is that
every holder reads the breach itself. (2) and (3): he asked for plain explanations of the
roster-widening question and of the seat rule's decisions D1 to D8, was given both with a
recommendation each, and answered "proceed". I am taking that as yes to the recommendations:
a group's declared protocol decides a widening and is refused where it would let fewer voices
admit than the corridor's floor; D1 split the assurance duty; D2 a root the reader trusts
confers age and capacity assurance; D3 a node's self-report needs its owner's `infra:attest`
and the steward-triple words go; D4 one token; D5 as (1); D6 content ratings are open and the
reader filters; D7 only the unscoped seat or its conferrer opens a retired agent's seal; D8
either. None of these is landed. Confirm the reading with him before the seat rule lands.
The guard designer's second pass was cut off by a usage limit and restarted.


## Data pass, step 1a: who a policy row counts (2026-11-11)

`formal/derivation/policy_text.tsv` types six cells per policy row (count_set, voice, counted_at, voices,
target_silent, changes_set), each with a quote checked verbatim by `tools/build_governance_policy.py`; they are
emitted as `counted` on each row of `manifests/governance_policy.json`. Ten cells are `unstated` (listed in the
manifest under `counted_columns.unstated_cells`); the generator refuses a rise. Two checks run: a row that removes
from its own count set fixes the set before the act; only a self roster counts keys.
The text gaps this found: no section says at what instant the generic two-path rows and the halt's confirmation
take their set; `custodian_replace` and `affiliation_member_action` say nothing of person against key.
Next (1b): the protocol sheet and the twelve rows the count design adds, after C-1 to C-4 of
`handoff/lanes/out_g_count.md` are in `text_conflicts.tsv`; then the `count` cell of the family model (1c).
The client is owed notice that the policy pin moved.

Step 1b landed in part: the protocol kinds are `constitution/consensus_protocols.tsv` (seven rows, quotes checked),
emitted as `protocols` in the policy manifest with votes by roster size. Found: the text gives no removal rule under
`founder_only` or `open:self_admit` (the latter cites the floor of CC 4.5.13), and no count set for `custom`.
C283 to C286 in `text_conflicts.tsv` are the count design's C-1 to C-4; C283 and C284 wait on Eric's confirmation.
Still to do in 1b: the sheet of which group kind may name which protocol; the twelve policy rows the design adds.

The admissibility sheet is `constitution/protocol_admissibility.tsv` (14 rows, quotes checked). It holds only pairs
the text states: the count design's rows for `geographic`, `affiliations` and `family/conferring` are not in it,
since no sentence gives them. Next: the policy rows a cosigned act runs (`enact = protocol`), then the `count` cell.

Step 1c landed: the `count` cell of the family model (`formal/derivation/count_text.tsv`, 18 arms over 11 families;
166 generic `none`; 7 open: collection:{kind}, group:roster, lineage_witness:{stage}, takedown_notice:{basis},
transport:canonical_rebind, trust:{job}:{version}, wa_adjudication:{state}). Policy rows `cosigned_act`
(enact = protocol) and `accord_majority` added. Not yet done: selector values held to the registry's leaves;
`cosign_rule` and `governance` derived from `count`; each transition's `policy` derived from `count`
(tools/build_transitions.py still reads the governance cell); the count design's rows with no stated numbers
(harm report keep, moderator and WA quorums, capacity panel). `membership:{stage}` widening points at
`cosigned_act`, which is the reading C283 waits on Eric to confirm; `community_invite` is pointed at by no family.

Step 1d: `tools/build_transitions.py` derives the entry transitions' policy from a typed `count` cell (value, `stages`
where the roles cell keys the same leaves, `cases` otherwise). A family whose roles are an open cell keeps its old
policy (identity:occurrence_revocation). Withdraw and supersede policies still come from the lifecycle cell.
Found: `membership:{stage}` has no per-leaf roles, though its Part 3 row gives a per-leaf emitter, so its leaf arms
are cases and not stages; that is a signer-column fill.

Data pass, step 2 (guard): `tools/guard_grammar.py` (parser, closure, self-test) and `formal/derivation/guard_text.tsv`
(63 statements from `handoff/lanes/out_g_guard.tsv`); `tools/build_transitions.py` puts a `guard` cell on every
transition (28 carry clauses) and counts the marks, each held from rising: refuse with no token 32, `ref:*` 10,
`landed` 3, `signs` 2, `commits` 1. A refusal token must stand in backticks in a Part. Set aside: three rows whose
quotes span table cells (identity_amendment CC 2.1, key:record CC 2.1, slashing:{outcome} CC 3.4.12) and one guard
on a withdraw of `retirement:{state}`, a verb that family has no transition for (a lifecycle finding).
A guard with no verb lands on attest and authorize only; whether it also binds a supersede is not decided.
Not done: `guard_well_founded` (no guard requires a row whose own guard requires it back), the model extension in
`formal/event_lifecycle`, the 34 statements the design could not encode, names for the bare refusals (persist).

Data pass, step 3 (change): `tools/change_grammar.py` and `formal/derivation/change_text.tsv` (61 statements from
`handoff/lanes/out_g_lifecycle.tsv`); a `change` cell on every transition (20 carry items), the default and the
every-family rows under `_meta.changes`. Marks held from rising: recovery 4, cosigned_prior 1, committed_key 2,
forfeited 1, no_weaker 1. Set aside: five `key_grant:{axis}` rows saying no supersede, withdraw or recant is admitted
(the model already has no such transition, so they agree and add nothing), one `goal:{scale}` row naming a recant the
family has no transition for, one ledger row whose quote spans cells. `guard_well_founded` is built (13 requiring
nodes, longest chain 2). Not done: member names checked against the CDDL; the strength order `no_weaker` needs;
the three properties the change design names; `lifecycle`'s supersedes and rotation parts derived from `change`.

Data pass, step 4 (fold): `tools/fold_grammar.py` and `formal/derivation/fold_text.tsv` (217 rows from
`handoff/lanes/out_g_fold.tsv`); the `fold` cell of the family model (76 families, 160 statements), default and
every-family rows under `_meta.fold`. Expressions are held to their alphabet only, not evaluated. Held back, 25 rows:
14 that refuse by a token the text never names (`roster_change_below_majority`, `witness_quorum_invalid`,
`evidence_score_mismatch`, `aggregation_meta_mismatch`, `locality_mismatch`), five reader defaults by polarity
(a table of its own, not a family), two with two tests in one fold, two using `strictest`, two naming `cosign_rule`
as a family. Not done: member names against the CDDL; a part inherited from the family's unselected value is not
yet resolved into one fold per leaf; `fold_commutes`, `advisory_moves_nothing`, `ended_stays_ended`.
The family model now reads role tokens from `manifests/transitions.json`, which is built from it: build the family
model, then the transitions.

Data pass, step 5 (reactions): `tools/build_reactions.py` (grammar, closure, builder, --check) and
`formal/derivation/reaction_text.tsv` (65 statements from `handoff/lanes/out_g_reaction.tsv`) give
`manifests/reactions.json` (116 entries). Held, 41 rows: 30 wait on a duration with no row in
`constitution/constants.tsv` (census_period_end, incapacity_t1_window_secs, session_claim_max_secs,
consent_temporary_ttl_secs, mesh_config_emergency_ttl_secs, accord_roster_window_max_secs,
membership_proposal_max_secs, custody_report_ttl_secs, delegation_term_max_secs,
consent_revocation_promotion_window_secs, purge_dwell_secs, accord_heartbeat_max_secs, wa_freshness_window_secs,
trace_orphan_age_secs, epoch_key_retention_secs); seven name `takedown_notice:PerceptualHashCsam`, a leaf the
registry spells otherwise; the rest are quotes that span cells. One-emitter: seven clock- or fold-caused emits are
written `by identity:substrate_persist` or `by author`, not `by origin_door`; the token does not yet say both the
role and which node, so the list is pinned and may only shrink.
All five column designs now have a grammar, a text table, a generator and a closure check. Left for each: the
held rows, member names against the CDDL, the properties the designs named, and cutting the per-family prose.

Eight durations added to `constitution/constants.tsv`, each read in its section first; the reactions manifest is now
135 entries from 77 statements, 29 held. Still unnamed: census_period_end, incapacity_t1_window_secs,
consent_temporary_ttl_secs, accord_roster_window_max_secs (today inside the note of admission_freshness_window_secs),
consent_revocation_promotion_window_secs, accord_heartbeat_max_secs, wa_freshness_window_secs, trace_orphan_age_secs,
epoch_key_retention_secs, delegation_term for `trust`, and purge dwell (which is W itself and wants no second name).

Reader-lane cells: ten gap cells landed through `cell_text.tsv`; `formal/derivation/cell_cites.tsv` (171 rows) gives
99 closed cells their sections (`cites`, reading agree or fills). 100 lane rows were skipped: columns the model does
not carry (evidence_screen), open cells, or quotes that span table cells. Six fills did not land: five placements
(provenance:build_manifest:{target}, testimonial_witness:{kind}, need:{domain}:{kind}, watchlist:{id},
attestation:registry_consensus) each need a departure reason in `departure_reasons.json`, and
`lineage_witness:{stage}` cosign none contradicts a reason that says the family leaves the default.
The 27 DISAGREE rows are not yet in `text_conflicts.tsv`. `cites` is what the prose cut will read: a sentence whose
cell reads `agree` is covered by data; `fills` is not yet.

The reader lanes' 27 DISAGREE rows are text against the census of the pinned build, about ten distinct points
(key-grant supersede and rotation, revocation erasure and rollback, licence class, proposal withdrawal, eviction
door, two audiences, the default in_audience, two token lists). They are drafted as questions for persist in
`handoff/persist/1259_addition_draft.md`, with the unnamed refusals and the one-emitter question. Not posted:
Eric reads it first. Once answered, each becomes a departure with a reason or a census correction.

## The measure: how much rule text rests under typed data (2026-11-11 late)

`python3 tools/data_coverage.py` places every quote of every text table in its Part and marks the rule entries
(`rule_entries.tsv`, 5,175 sentences that state or apply a rule) whose sentence a quote falls in. Today: 579 of
5,175 (11%). By Part: 1: 6/156; 2: 18/513; 3: 342/1,998; 4: 177/1,295; 5: 17/703; 6: 18/358; 7: 1/152.
This is not the lanes' figure (27% now, about 60% with the five designs): theirs is over 1,023 (statement, family)
pairs in nine columns, the per-family statements only. The whole rule text is five times that and most of it is
not per-family: general rules, wire layouts, transport, mathematics, stewardship. Largest uncovered homes in
Part 3: CC 3.2 (257), 3.4.12 (122), 3.4.13 (111), 3.1.7 (90), 3.4.5 (80). The measure is of sentences a value
rests on, not of sentences cut; nothing is cut yet. `--list-uncovered pN` lists the homes to work next.

Held rows worked: five placements landed with reasons (48 reasons now); `lineage_witness:{stage}` cosign and count
are none from CC 3.4.10 and the family leaves the `quorum` reason (count open cells 6); the five reader defaults by
polarity are `fold_reader_defaults.tsv`. Four held rows (three guard, one change) quote a gist and not the text;
their rules are carried by other rows or stay prose. Four reader lanes launched for the unmeasured per-family
columns: body (two lanes, 436 statements), signer (286), and freshness/window/formula/tie_break/monotone_field/
projection/placement (about 240); outputs to scratch `lanes/out_f_{body_a,body_b,signer,small}.tsv`.

First prose cut (the method): the bullet list of policy rows in CC 4.5.13 is replaced by a table that
`tools/build_governance_policy.py` writes into the Part (found by its lead sentence; CI diffs the Part). The three
restating entries now rest on table rows; the cross-references the bullets carried are kept in one paragraph after
the table. The pattern for further cuts: (1) the data table prints into the Part, (2) entries that restated the
value are repointed to the printed row, (3) a quote that rested on the cut words is moved to the sentence that
states the rule, (4) links kept. A value stated only by the cut words must not be cut: it would cite itself.

Body column: `tools/build_family_model.py` now reads a family's body members from `constitution/signed_object.tsv`
where a presence cell names a wire form (11 families; 28 presences are written in words and listed under
`_meta.body.presence_in_words`). The body lane for Parts 4 to 7 (scratch `lanes/out_f_body_b.*`): 120 statements,
FILLS 56, RICHER 55, AGREE 4, DISAGREE 1, NOT_A_CELL 20; of the member names it proposes, 24 are in the CDDL and
85 are not. So the text names many members the signed-object table does not carry: each is either a member of a
sealed or framed body the table does not list, or a name the prose invented. That list goes to persist before any
of it lands as a wire member. Objects with members in prose and no family row or CDDL: location_proof, live_stream,
wholeness_witness, StorageBudgetV1, CorpusWantV1, the three accord roster-change objects. CC 4.4.3.2.8 says the
family model manifest carries the affiliation config schema; it carries none.
The first prose cut's gate failed once, as designed: four `cell_cites` rows quoted the cut bullets and were dropped.

Signer lane (`handoff/lanes/out_f_signer.*`): 286 statements, 387 rows: AGREE 263, FILLS 26, RICHER 32, DISAGREE 9,
NOT_A_CELL 57. The signer prose is mostly a copy of the data. 265 citations added to `cell_cites.tsv`; the coverage
measure is 793 of 5,175 (15%). Nine disagreements to fix in the model, each where the text is clear:
`system:*` omits `substrate_edge` (CC 3.1.3, 3.1.4, 3.4.3); `consent:{kind}` stage `community_trust` should admit
the owner or the node it owns, stage `state` should carry the delegation chain and give `expired` to the store
alone (CC 3.3.1, 3.4.5); the attest transitions of `membership:{stage}` and `reconsideration:{grounds}` carry one
role where the family cell and the text give the invitee and the subject (a derivation fault in
`tools/build_transitions.py`: per-stage roles are lost when the cell is not marked per_stage);
`provenance:build_manifest:{target}`: CC 3.1.2 says the per-primitive steward signs, CC 3.1.2.1 says the pipeline
that built it (text against itself, for `text_conflicts.tsv`). RICHER needs: a role no token names (8), a
condition (7), a delegation shape (4), per-leaf signers (3), a family with no row (3), a group as signer (2).
Ten statements are marked seat-rule and wait.

Signer disagreements worked: `tools/build_transitions.py` keeps per-stage roles for a census cell that is a map
(membership, reconsideration, revocation), so membership's leaf arms are stages of its policy. `consent:{kind}`
stage `state` carries the delegation chain. One correction was wrong and is reverted: adding `self` to
`community_trust` let any signer grant for a node it does not own, and the mesh story (step 51) caught it; the cell
stays owner-only with the node-authored form in its qualifier. `system:*` and `substrate_edge` is text against the
census of the store alone and goes to the implementers, not into the cell. C287 records the build-manifest signer.

All four reader lanes are in (`handoff/lanes/out_f_{signer,body_a,body_b,small}.*`). Totals over 965 statements:
AGREE 632 rows, FILLS 216, RICHER 271, DISAGREE 21, NOT_A_CELL 173. 220 further agreeing rows are in
`cell_cites.tsv` (projection 73, body 64, fold 60, placement 19, freshness 4); 84 agreeing rows sit on an open cell
and wait for its value. Coverage: 833 of 5,175 (16%). The persist draft lists every member name the two body lanes
could not find in either CDDL. Small-lane findings still to work: two disagreements (the halt row's `valid_until`
against `expiry none` in the reactions table; the deletion watcher and `consent:deletion_complete`, CC 4.4.3.5.2
against CC 3.3.1), thirteen unnamed durations, and needs for a recurring clock, a clock on a seat-holder's silence,
a placement selector and the hardware-class weight table. 21 rows concern objects with no family row.

Body fills landed: `formal/derivation/body_text.tsv` (322 rows; 246 distinct family members applied, 100 in the
CDDL and 146 named by the text alone) joins the members read from the signed-object table; 49 families have a typed
body. The `in_cddl` test is a word match and can be fooled by a short name. Freeform proposals of the Parts 4 to 6
lane were reduced to their member names with type and presence `unstated`.
A finding from answering the CIRISHolon session: the `confirm` and `widens` cells of `manifests/transitions.json`
are nearly functions of the verb (every attest and authorize confirms; one withdraw of 146 does), because `widens`
is derived from the replication tier with a default and the way back is "offered by this table". The confirm test
of CC 4.5.13 is therefore not yet informative as data; it needs `widens` per family from the text.

`widens` on entry transitions carries `when` (always 11, by_scope 165, unset 8); the boolean is unchanged, so a
consumer reading only `value` and `confirm` behaves as before. Not done: a replacing row that promotes its scope
(CC 4.4.3.3.1) widens and the table marks every supersede as not widening; changing that boolean changes what the
client confirms, so it goes to the client thread first. `handoff/items/` holds outcome-bearing items (56 guard
cases, 732 policy cases, 96 story steps; facts and truth files) made for the CIRISHolon instrument; Eric's go-ahead
for that hour came relayed by that session.

Widens and confirm, agreed with the client session (a derived reading, not Eric's ruling): the boolean is an upper
bound, `when` narrows it. Supersede on a by_scope family: widens true, when by_scope_change (69 transitions).
confirm.when: always 49, if_widens 205. The client will state CSD/5 L6 as: confirmed when the row widens at the
scope it is signed at, or has no way back. "Way back" still means this table offers a withdraw or recant.

Restatement cuts (`lanes/out_cut_a.tsv` in scratch): of 93 restating sentences with data under them, 4 cut, 3
shortened, 86 kept (list items, code lines, a local reason); 190 words. Applied with the guards; three entries and
their inventory rows removed; ten data rows had quoted the cut words: seven dropped where another row carried the
value, three moved to the home sentence (CC 4.4.3.4.5, CC 3.3.6.3). Conclusion: cutting restatements is nearly
spent. The volume is in home statements of per-family values, which shrink only by the method of the policy table:
a generated table becomes the Part's statement and the prose that listed the values goes.

`tools/family_card.py` prints a family's card from the three manifests (signers by transition, policy, widens,
confirm, way back; count; guard; change; fold; in time; body), each line with its sections; `--coverage`: of 184
families, count typed 12, guard 27, change 16, fold 76, in time 31, body 49, any block 118. Samples in
`handoff/cards/`. Building it showed the reactions manifest repeated a clause once per section that states it:
merged, it is 83 distinct clauses, not 143. The card is the artifact for the larger cut: Part 3's registry rows
hold about 6,300 words of per-family description in single cells (cosign:{state} alone 641 words), and the card
for a family is what a generated statement of the same values would look like.

Eric, 2026-11-11 late. (1) His earlier "proceed" was NOT a ruling on roster widening or on the seat rule's D1 to D8:
he has not reviewed them. Every note above that reads it as a yes is withdrawn; C283 and C284 say so. The membership
count cell stands on the sentence of CC 3.1.3.2 it quotes and on the build, not on a ruling. The seat rule stays
undrafted. (2) He asked whether a persist session is needed: none is live among the peer sessions (edge, client,
server, agent, bridge, holon and ratchet are); the draft for #1259 is unposted. (3) "Annex is fine ... we need to
cash this in": the family cards are CC 8.10, written by `tools/family_card.py --write` (118 cards, 9,861 words),
checked in the gates and CI, carried in volume P03. Next: trim each Part 3 description cell to purpose and reasons,
the values now being the card's.

Card as home: `section_span('CC 8.10')` returns a span that holds exactly the marker `=card`, so a row of any text
table may carry cc_ref `CC 8.10` and quote `=card` once the prose that stated its value is trimmed; every quote
check then passes for it and for nothing else. Scratch `repoint.py` moves rows whose quote no longer stands onto
the card home and drops citation rows. A trim lane (`lanes/out_trim_a.tsv`) is proposing trimmed description cells
for the 33 Part 3 cells over 80 words with a card; before any lands, the registry is compared before and after and
only `description` may differ. toc.tsv carries 8.10 (added by hand; `build_pdf.py --write-toc-volumes` placed it).

Trim lane result (`handoff/lanes/out_trim_a.tsv`), NOT applied: across the 33 Part 3 description cells over 80
words that have a card, 5,247 words would become 5,008. Thirteen cells cannot lose a sentence, because no card line
carries a whole one; the pointer sentence each trimmed cell gains eats most of the rest. The cards carry about a
twentieth of what these cells say. What the cells hold that the data does not: what the row is and why, id and
digest derivations, audience and serving rules, the conditions marked partial in the guard table, and reasons.
One mismatch found: the `retirement:{state}` cell cancels by `withdraws` and the model has no withdraw transition
(the same finding the guard pass made). Conclusion: the data pass has produced kernel-readable tables and checks,
not a shorter Part 3; shortening Part 3 needs the audience, derivation and body-rule columns that do not exist yet.

## The second reading (2026-11-11 night)

Six lanes read the 2,533 non-family statements rule key by rule key (`handoff/lanes/K_KEY.md`, `out_k_*.tsv`):
242 findings; major 80 (59 new, 21 known), minor 162 (123 new, 39 known). Three verifier lanes
(`V_VERIFY.md`, `out_v_*.tsv`) judged the 59 new major: STALE 29, NOT_A_CONFLICT 17, DATA 4, CHOICE 9 (7 distinct).
All 59 are C288 to C346. A writer lane drafted the stale fixes (`out_w_stale.tsv`, 37 edits); 29 edits applied after
my read, with three long sentences split and one entry repointed.
Held, not applied: K03 (Part 1 Accord text and the CC 4.5.1 register cell, on the WA seat: Eric's wording);
K29 and K30 (what the under-13 default means for an owner with no assurance: whether such an owner may operate and
may announce; a consequence of his age ruling he has not seen); K46 (the `supersedes` cell of CC 2.4.1, waits on the
guardian-displacement choice); K54 and K55 (wire sections that wait on the edge's known answers).
DATA: K20 fixed (`takedown_notice:{basis}` count: steward_purge is `cosigned_act@trust_root`; count open cells 5);
K36 (`content_rating` reserved in the text and open in the registry) waits on the seat rule's D6; K44 (default
`in_audience`) and K59 (owner-binding recovery gate) are text against build, for the store.
Not read by the second reading: the wire's known-answer vectors, CC 2.6.1.7 row by row, `reactions.json`,
`formal/accord_halt`. The 123 new minor findings are in `out_k_all.tsv` and not yet in the conflict table.
Stop criterion agreed with Eric in substance: every statement read twice, then one more rule-by-rule reading after
the fixes whose count of new major findings is a handful.

## The third reading (2026-11-11 night)

Ten lanes over all 4,254 statements against the fixed text and the data (`out_r3_*.tsv`): 362 findings; major 129
(89 new, 40 known), minor 233 (191 new, 42 known). Four verifier lanes on the 89 (`out_v3_*.tsv`): STALE 40, DATA
31, CHOICE 9, NOT_A_CONFLICT 9. Logged as C347 to C435. Only 9 of 89 dissolved (17 of 59 last time).
Eric's theory, 2026-11-11: each fault fixed makes the next easier to find. The breakdown fits it: on the general
rules (the ground the second reading cleaned) new text-against-text majors fell from 51 to 12; 42 are per-family
rules never compared statement against statement before; 35 are text against data, visible only because the data
exists. Prediction to test on the next pass: per-family text majors fall to about ten, data findings fall as cells
are corrected, and more findings have two finders (7 of 76 this pass).
Data faults of this repository fixed: heartbeat expiry moved to `accord:lifecycle` (C378, C435); canonical re-bind
counted `accord_majority@accord` (C369, C374; count open cells 4); the three further withhold windows (C376;
the reversal condition on the delete, C377, has no event token and is open); `retirement:{state}` gains withdraw
(roles author, selfAct) and its guard (C367, C430); guards dropped for reconsideration, delivery receipt cosign
and deferral licence (C394, C358, C433, C398: each needs a condition the grammar cannot yet say); two
expected-active folds dropped (C347, C348); two registry literals in `tools/build_cc_namespace.py` (C363, C364).
Not fixed: C352 (the base law is a declared stand-in); C372 (freshness defaults); C386 (build manifest
supersede: the kind grid gives Facts no replace); C391 (harm-report reactions); C392 (waits on choice C351);
C432 (an organisation-named licence is cosigned: needs a `declarer` key in the count grammar).
Text against the shipped store, for the implementers: C365, C366, C371, C383, C384, C388, C412, C422, C423.
A writer lane (`out_w3_stale.tsv`) is drafting the 40 stale fixes.

Third-reading stale fixes (`handoff/lanes/out_w3_stale.tsv`, 53 edits): 44 applied after my read, plus two
pseudo-code arms in CC 4.4.3.2.3 written by hand (hold on a signature shortfall; the resolution-7 exception).
Held: edit 2 (OSA timelines, weak), 4 and 5 (who enables a watchlist: tied to the hash-matching choices), 26 (CC 4.3
hand-on needs `sub_delegation`: touches the seat ruling, low confidence), 35 and 36 (delegation depth cap, low),
43 (entity revocation withdrawn by nobody: low, and the store admits it). Not written by the lane: R13, R10, R04,
whose stale side is the generated CC 2.6.1.7 table (fix in `constitution/signed_object.tsv`: key_record
scrub_key_id, expires_at, source_count). Eighteen data rows quoted changed sentences: seven citations dropped,
eleven moved to the corrected sentence; the licensure fold now reads the quorum-weighted merge.

## Eric's rulings, 2026-11-11 late night (to land when the fourth reading's lanes have finished)

His words, on the six choices no principle decided:
(1) An owner with no age assurance on record may announce: "yes, or else desktop users would be unable to
participate - add a note that as privacy respecting age signals become available, we adopt and may tighten, but
this is a side effect of the state of the tech available (best effort)". So CC 5.4.6's refusal of a minor's
announcement does not reach the unassured owner; CC 4.5.13 "announcing starts on" stands; add the note. (K30, C317.)
(3) A hash match on known abuse imagery: "removed with the signature of the person who owned the node where the
detection occured, or if the signing materials are unavailable removed with a request to approve in retrospect and
a hard case registered (we err on the side of the law)". (R49, C395.)
(4) Legal hold against immediate removal: "legal hold wins right?" Asked as a question; my answer to him: yes for
destruction, and the item is withheld from everyone at once, destroyed when the hold lifts, both recorded. To land
only if he confirms that reading. (K25, C312.)
(2) guardian displacement, (5) the founder's seat, (6) roster widening: "what?" Each to be put to him again as a
plain story.
Also from him: "a lot of those are obvious, you can not retract a decision regarding something deleted". Twelve of
the eighteen are settled from the architecture as derived readings (listed to him; table in the session), to land
with these.

## The fourth reading (2026-11-12, early)

Ten lanes, same shares, text opened for nearly every statement (`out_r4_*.tsv`): 325 findings; major 154 (77 new).
New major text against text 26 (general keys 13, family keys 13; third reading 12 and 42), text against data 51
(third reading 35); two-finder 2 of 71. Verified (`out_v4_*.tsv`): DATA 44 (store 24, repo 20), STALE 23,
NOT_A_CONFLICT 7, CHOICE 3. Logged C436 to C512.
Reading: the text is converging (text-against-text majors 51, 54, 26 across readings two to four; family keys fell
by two thirds after one round of fixes, as the general keys did the round before). The data is not: readers now
compare cell by cell, half the data findings are text against the shipped store, and two were regressions from my
own fixes (removing the over-broad delivery-receipt guard left no refusing guard: C440, C510). Data findings are a
work queue for the model and the store, not the document contradicting itself.
The three CHOICE: C441 (chunk number per epoch or per stream: technical, for the edge); C487 (which count decides a
removal: the same open question as roster widening); C479 (a moderator ejecting an agent alone: settled from the
floor of two voices and universality, removal takes the same count as a person's, a moderator may block).
Repo data faults fixed: resumption guard added; resignation at community scope rotates; guards dropped (recovery
condition on every widening; subject as moderator); reactions dropped (attach close; default grant lapse); verbs
added (goal and need recant; lineage_witness withdraw); ballot `ranks`. Not fixed: delivery receipt step 2 (no
family for a published, uncosigned head: C440, C510); moderation body digest and two audience cells (census prose);
canonical re-bind supersede policy; an accord roster-change policy row (C488); missing expiry entries (C512);
`system:*` signer. Twenty-four store findings go to the draft for the store.
Writer lanes running: `out_w_settled.tsv` (the two rulings and twelve derived settlements) and `out_w4_stale.tsv`.

## Landed 2026-11-12 early: rulings, settlements, fourth-reading fixes

From `out_w_settled.tsv` (62 rows): applied 32. Eric's rulings A (unassured owner may announce, with the
best-effort note) and B (hash match removed under the node owner's signature, or removed with a hard case and
retrospective approval). Derived and applied: C (a vote against hides), D (majority of those who voted; the policy
row `moderation_action` still reads base active and floor 1/2 and must follow), J (unregistered family refused),
K (accord signs halt acts and heartbeat only; `accord:human_dignity` stays a registered leaf that no holder signs),
M (tripwire always on, watchlist per group), N (standing mandated-report endpoint), and two allow-list pointers of G.
NOT applied, because my derived outcome would have overridden a deliberate design and is not mine to decide:
E (a late joiner and a kept stream: the stream's `history_on_join` setting exists), F (relay trees: CC 5.3.3.4's
layered multipath landed 2026-11-08 at Eric's word and the edge builds to it; the member relays are audience
members), H (`archive_mode` is stated as operator-local on purpose, and a signed member is a wire change),
I (an empty grant "matches nothing, by design", and refusing it changes the CDDL), L (who vouches for an age band
is the seat rule's D2, unreviewed), the rest of G (an agent's node is not always server class).
Gaps B leaves: no row for the owner's retrospective approval or refusal; a peer cannot resolve "the node where the
detection occurred" from rows it holds.
From `out_w4_stale.tsv` (52 rows): applied 41. Held: F07 (what a halt invocation's signature covers: the halt, mine
to read first), F44 (a moderator ejecting an agent: CC 1.13.2 is Eric's stance text; my settlement would weaken a
human's power over an agent and is his to make), the CC 1.13.2 term fix, F63 (a "retryable" refusal is a new
notion), F08 (digest to uuid: the store's), and three that need the generated table or several lines.
Nineteen data rows followed their sentences; three citations dropped.
