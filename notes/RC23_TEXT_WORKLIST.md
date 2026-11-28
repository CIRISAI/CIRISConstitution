# Edition 1.0-rc23: the text and table edits still owed

This is the worklist of every text and table edit still owed for edition 1.0-rc23. Each entry is meant to be taken alone and written without re-deriving anything. It records rules, never the history of how they were reached. Where an entry's rule could not be recovered from the record, the entry says so and gives what is known.

## 0. Purpose, pin and the rules of an edit

### 0.1 The pin this list was written against

| What | Value |
|---|---|
| Branch and commit | `rc23-next` at `0e80f21` ("The receipt's refusal has its row in the name table, and the token delta lists it.") |
| `VERSION` | `1.0-rc23` |
| Policy pin | `85750784201150059aef28f3db8224deaf8f447f58c8adcce660759de12de99a` (`_meta.policy_sha256` of `manifests/governance_policy.json`) |
| `manifests/governance_policy.json` | sha256 `8014d6cb55e025911e72f9586eb67615e7efcd4216fc138f3e770514812ac29b` |
| `manifests/family_model.json` | sha256 `9d49c2a7d197cb95310165ca8052732c6c274b27e09e61da3d43dae6dce66bcc` (189 families) |
| `manifests/namespace_registry.json` | sha256 `29d541c8dab0f79ceac7358d758b7c70501398069a0c8a190097ecfd81569c99` |
| `constitution/governance_policy_acts.tsv` | 50 rows |
| Vendored kernel | `kernel-v0.4.0` (`formal/vendor/VENDOR.tsv`, commit `e53eb23587acc914cbf1655093e779526707a718`). Group A waits for the next tag. |

Every line number below is at `0e80f21`. Line numbers move as edits land; each REPLACES quote is exact and can be found by search.

### 0.2 The rules every edit obeys

1. **Sentences.** A normative sentence has at most 40 words. Sentences are plain and declarative. BCP 14 words are in capitals (MUST, MUST NOT, SHOULD, MAY).
2. **No history language in the Parts.** Do not write "previously", "used to", "was changed", "now", "no longer", "not yet", or "new in this edition". A Part states the rule as it stands.
3. **Fixed vocabulary.** It is the *causal* kernel (consent), never a "consensus" kernel. Never write "never a runtime". The halt is the condition of symmetry and is never called an asymmetry. Agents are never written as persons, and no personhood is presumed for them.
4. **No carve-outs.** State the uniform rule and its harsh edge plainly. If an edit seems to need an exception, stop and report it.
5. **Model first.** Write a sentence about a function of rows only where the steward ruled it, or where the vendored kernel runs it. Where the kernel runs it, cite the vendored case in the section's *Checked* note, in the style that section already uses. Group A entries wait for the kernel tag to be vendored.
6. **No file paths or product names in the Parts.** A Part names "the causal kernel's cases" and the bare file name of a vendored case, as the existing *Checked* notes do. It never names a directory path or an implementation.
7. **Quote tables.** These tables repeat sentences of the Parts verbatim: `formal/derivation/*.tsv` (rule_entries, rule_inventory, cell_cites, door_text, count_text, guard_text, body_text, fold_text, standing_text, policy_text, text_conflicts, models_vs_text and the others), `constitution/claims.tsv`, `constitution/protocol_admissibility.tsv` and `tools/divergence_cases.py`. When you reword a sentence, update every quote of it, and do not reorder or reformat rows you did not change. Each entry lists the quotes found at the pin. Grep again before editing.
8. **Generated blocks.** `manifests/*` and the generated blocks inside the Parts (the policy table in CC 4.5.13, the member tables of CC 2.6.1.4, the refusal-token manifest) come from the cascade. Never hand-edit them. Change the source table and run the cascade.
9. **New refusal names.** A new refusal name needs a row in `formal/derivation/refusal_tokens_review.tsv` with its kind (refusal, concludes_nothing, report, waiting, and so on). If it carries a transparency word (receipt, statement, log, service, registration), it also needs a row in `manifests/scitt_names.tsv`. Then `tools/build_refusal_tokens.py` rebuilds the manifest. The refusal-token manifest is sorted by name, and implementers pin a token by name, never by position.
10. **After a table change.** Run the cascade, then `tools/mesh_story.py` (without `--check`, so it regenerates `manifests/mesh_story_trace.json`), then `tools/build_adopter_files.py`. Commit, and run the gate on the committed tree. Then run `python3 tools/check_text_lints.py` and `python3 tools/check_rule_entries.py`. A change to a quoted summary also needs `formal/derivation/rule_inventory.tsv`.
11. **Fixed numbering.** Section numbers, headings and anchors never change.
12. **Privately reported weaknesses stay out.** They never go into the text, the tables, commit messages or public reports. The text states rules, not what an implementation does.
13. **Who writes the register.** `constitution/part_8_appendices.md` (the CC 8.3.4 ledger), `CHANGELOG.md`, `README.md`, `VISION.md` and `web4/` belong to the register lane. An entry that closes or changes a ledger row says so under TABLES, and the register lane writes that row.

### 0.3 The order of work

1. **Group B now**, in this order:
   - the schema rules (B-01 to B-21), with one cascade run over `constitution/signed_object_v2.tsv` and `manifests/family_payloads_v2.cddl`;
   - the policy-table cells (B-22 to B-24), with a cascade run, the mesh story and the adopter files;
   - the prose contradictions (B-25 onward).
2. **When the kernel tag is vendored**, write Group A:
   - First the head rules, as one lane, because they share sentences: A-01 to A-08.
   - Then the trust root: A-09 and A-10.
   - Then the election: A-11 and A-12.
   - Then the rest, in index order.
   - Each *Checked* note cites the vendored case file.
3. **Group C** stays as written in the text until the steward answers. Each entry says what stands meanwhile.
4. **Group D** waits until after the cut.
5. **Register lane last.** It writes the CC 8.3.4 ledger rows and changelog lines that the entries name.

Entries marked **DONE-IN-TREE** are listed so that no writer does them again. Each cites the commit that landed it.

---

## 1. Group A: edits that wait for the kernel tag

These rules are ruled and modelled. The text states each one and cites the vendored case in the section's *Checked* note. Write none of them before the tag is vendored (rule 5 above).

### A-01 A count is taken at the newest counted heads in the row's own past

- **RULE.**
  - A row that changes a roster names, as its heads, the newest counted changes over that roster in its own past. A row that names an older head, or leaves out a newer one, concludes nothing.
  - A *counted change* is a row that changes a roster and concludes under the policy the roster's record binds to its act, however many voices that policy needs. So a lone holder's `duty_confer`, and a room of one's invitation, are heads too. A one-key row that meets no bound policy is no counted change.
  - The count is taken over the members the fold seats at those heads. No head is read through another head, and no row chooses the roster it is counted over by the head it names.
  - The protocol is the record's `consensus_protocol` in force in the row's past, and a row never states one of its own.
  - No roster-changing row is exempt: a moderator's lone removal of an agent's key, a resignation and a founder's withdrawal of its own signature each name those heads.
  - An acceptance and a resignation are no head of their own. A count reads the seats at its heads, completed by the acceptances and ended by the leavings in its own past.
  - Any counted change over the object moves the head, whatever its scope, a duty change included.
  - An act that changes no roster names whatever head its signer chooses. It is not refused for an older head, and it counts at the head it names.
- **AUTHORITY.** Derived. It was accepted with the kernel's head rules and runs in the kernel's head-rules cases. The text already has its first half: CC 2.4.1.1 says "a node reads no instant to decide any of it".
- **HOME.**
  - CC 2.7.8 *The roster is the one ledger*, second paragraph. REPLACES: "A version that names several heads is counted over the members common to the newest counted versions among the heads it names, read through any head one key wrote, less the members whose own leaving is in its past. A head one key wrote narrows no count but by its own signer. A member's own admission to an open room is such a head; a resignation is an end and no head."
  - CC 2.4.1.1, the paragraph *An older head*. REPLACES its first two sentences: "That the head is the newest its signer holds is judged for an end, never for an act. An act that names an older head than its signer holds is not refused for it, and it counts at the head it names."
  - CC 3.3.4, the paragraph *A roster event is counted at the head it names (normative)*. REPLACES its first sentence: "A widening or removal names the roster head it extends, and its signers are counted over the members at that head."
- **DRAFT.**
  - For CC 2.7.8:
    - "A row that changes a roster names, as its heads, the newest counted changes over that roster in its own past. One that names an older head, or leaves out a newer one, concludes nothing."
    - "A counted change is a row that changes a roster and concludes under the policy its record binds to that act, however many voices the policy asks."
    - "A count is taken over the members the fold seats at the heads its row names. No head is read through another, and the protocol is the record's in force in the row's past."
    - "A moderator's lone removal of an agent's key, a resignation and a founder's withdrawal of its signature each name those heads."
    - "An acceptance and a resignation are no head themselves: a count reads the seats at its heads, completed by the acceptances and ended by the leavings in its own past."
  - For CC 2.4.1.1 *An older head*:
    - "That the head is the newest its signer holds is judged for an end and for every row that changes a roster ([CC 2.7.8](#2.7.8))."
    - "An act that changes no roster and names an older head is not refused for it, and it counts at the head it names."
  - For CC 3.3.4:
    - "A widening or removal names the newest counted changes of the roster in its own past, and its signers are counted over the members the fold seats there ([CC 2.7.8](part_2_the_grammar.md#2.7.8))."
- **TABLES.**
  - Quotes at the pin: none of the CC 2.7.8 sentences, nor the CC 2.4.1.1 sentences, is quoted in a quote table (searched).
  - Grep `rule_entries.tsv` for "names the roster head it extends", and update it if found.
  - The 2.7.8 *Checked* note gets the vendored head-rules case file.
  - `constitution/governance_policy_acts.tsv`: no row changes. Its header already says a row never states a protocol of its own.
- **NAMES.** None.
- **CHECKED BY.** The kernel's head-rules cases and its fold model, read in arrival orders with planted breaks. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-02, A-03, A-04 and A-07 share this paragraph. Write them in one pass.
  - CC 2.7.4 "A count is over the members at the head its row names" stands, read with this rule.
  - CC 3.3.4's `founder_only` row says "a founder **active at the instant of the act**". It is restated in A-28.

### A-02 The reader's line: sibling-safe, monotone, and made of the reader's own rows

- **RULE.**
  - **Sibling-safe.** A reader's line holds a change behind an acknowledged change *c* only where every head it names lies strictly in the past of *c*'s own heads. So a sibling is not void merely because it names an older head.
  - **Monotone.** Acknowledgements accumulate in any order. Acknowledging never makes a void change count again, and naming a void change as a head adopts nothing. A client SHOULD NOT build on a change that is void for it.
  - **What acknowledges.**
    - A reader acknowledges by its own signed rows that have the change in their past.
    - It also acknowledges by the concluded seat rows of which it is a voice.
    - Each acknowledgement counts only where its row is in the past of every end of the key that signed it.
    - An acknowledgement settles a change only where the change counts over that acknowledgement row's own past.
  - **The line holds when an act is cut.** The line binds to the acknowledged head even where the act there is later cut, and a sibling re-signs forward.
  - **A void change does nothing for that reader.** A change that is void for a reader is out of that reader's fold and heads, and a row void for a reader cuts nothing for that reader. So a count's conclusion is reader-dependent, as CC 2.7.9 already says.
  - **Where the line reaches.** The line covers counted rows and every end of a standing. It does not cover a receipt, or an act that changes no roster (A-01).
  - **A reader's first acknowledgement.** A member's own seating row is its first acknowledgement. A reader with none takes its first head from a source in its trust set: a member it knows, a listing, or a referrer.
  - **Prompt acknowledgement.** A node acknowledges the newest roster head it holds without delay.
- **AUTHORITY.** Derived. The kernel accepted it, and the bundle form ("an acknowledgement settles only if the acknowledged bundle counts over that acknowledgement row's own past") is agreed with the kernel.
- **HOME.**
  - CC 2.7.8, fourth paragraph. REPLACES: "A reader that has acknowledged a head holds void every counted act that names an older head and is not in that head's past, however many rows it has. Its signer acts again, forward, at the newer head ([CC 3.3.4](part_3_the_namespace.md#3.3.4)). This line is for counted rows and every end of a standing: a version, a vote, a cut and an end, counted or one's own. It does not reach a receipt. It does not reach an authored act that names its head, which counts at that head whatever head a reader has acknowledged."
  - CC 3.3.4, *A roster event is counted at the head it names*. REPLACES: "A node that has acknowledged a newer head holds a line from below that head void, however many rows it has. For that node a sibling of the acknowledged head is void too, since it names an older head outside that head's past ([CC 2.7.8](part_2_the_grammar.md#2.7.8))."
  - CC 3.3.6.4, *The head a self-roster row names*, second paragraph. REPLACES: "A row naming a head of which the reader has acknowledged a successor is a sibling. It is void for that reader, and never lands a change by a count over that head ([CC 2.7.8](part_2_the_grammar.md#2.7.8))."
- **DRAFT.**
  - For CC 2.7.8:
    - "A reader's line holds void, for that reader, a change every head of which lies strictly in the past of the heads of a change it has acknowledged. Its signer acts again at the newer head."
    - "So a sibling of an acknowledged change is not void for naming an older head."
    - "A reader acknowledges a change by a row of its own that has the change in its past, and by a concluded seat row of which it is a voice."
    - "Each counts only where its row is in the past of every end of the key that signed it."
    - "An acknowledgement settles a change only where the change counts over that acknowledgement's own past."
    - "Acknowledgements accumulate in any order, and acknowledging never makes a void change count. Naming a void change as a head adopts nothing."
    - "The line binds to the acknowledged head even where the act there is later cut; a sibling is re-signed forward."
    - "A change void for a reader is out of that reader's fold and heads, and it cuts nothing for that reader."
    - "This line is for counted rows and every end of a standing. It does not reach a receipt, nor an act that changes no roster ([CC 2.4.1.1](#2.4.1.1))."
    - "A member's own seating row is its first acknowledgement. A reader with none takes its first head from a key in its trust set: a member it knows, a listing or a referrer ([CC 4.4.3.8](part_4_composition_governance.md#4.4.3.8))."
    - "A node SHOULD acknowledge, by a row of its own and without delay, the newest roster head it holds."
  - For CC 3.3.4:
    - "A node that has acknowledged a change holds void, for itself, a change whose every head lies strictly behind it ([CC 2.7.8](part_2_the_grammar.md#2.7.8))."
  - For CC 3.3.6.4:
    - "A row whose every head lies strictly in the past of a change the reader has acknowledged is void for that reader, and never lands a change by a count over that head ([CC 2.7.8](part_2_the_grammar.md#2.7.8))."
- **TABLES.**
  - `formal/derivation/rule_entries.tsv:4903` quotes "A reader that has acknowledged a head holds void every counted act that names an older head".
  - `formal/derivation/rule_entries.tsv:1834` quotes "A node that has acknowledged a newer head holds a line from below that head void".
  - Update both.
  - CC 2.7.10 says "for this node only, for an act at a head older than one it has acknowledged". Re-read it against the sibling-safe line, and change "older than" to "strictly behind".
- **NAMES.** None. Which rows acknowledge is a rule, not a member (wire-map G11).
- **CHECKED BY.** The kernel's reader's-line cases (the line and its versions take the same rule) and its roster run. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-01 and A-03.
  - CC 2.7.9: "A reader's own acknowledged head closes older heads for that reader only." Reword it to "A reader's own acknowledgement closes, for that reader only, the changes strictly behind it."
  - The prompt-acknowledgement sentence is an adopter's duty. Were it to sit in an adopter document instead of the Parts, put it in CC 2.7.8 still, since the Parts carry no file names.

### A-03 A change its own voices left behind: the self-fork rule

- **RULE.**
  - **When a change is self-forked.** A counted change *q* is self-forked for a counting row *r* where every counted voice of *q* signed, in *r*'s past, a change that *q* lies behind, sibling-safely (A-02).
  - **When it is void.** A self-forked change is void for *r* only where, at the fork point, the members seated there who signed only the competing side outnumber those who signed only *q*'s side. A tie voids nothing, and that includes a fork point with no such member. Chain depth decides nothing.
  - **What counts as signing a side.** A member signed a side only:
    - by a counted voice;
    - on the chain itself, named as a head and not merely cited;
    - under a seat held at the fork point.
    A seat the side itself granted is no evidence for that side.
  - **Rows built on a void change.** A row built on a void change is void with it, unless it is rescued. A rescue is a voice of that row that never voiced a self-forked change, signed only one side, and was a member at its heads.
  - **No rescuer.** Two chains with no rescuer are both kept.
  - **Scope.** This is the only automatic effect, outside an election, of one key signing two rows over one object neither of which names the other. It voids a change and never a key.
  - **Where it applies.** It applies to the reader's own roster as well. A recovery bundle is not exempt: its holder is one voice under either key.
  - **Finality.** Finality by acknowledgement (n − t + 1 clean receipts, CC 2.7.3 and CC 2.7.5) stands as written.
- **AUTHORITY.** Derived. It was accepted with the kernel's head rules, and its rescue and fork-point count were run in the kernel's cases. The text already says the finality half (CC 2.7.3 "Final by acknowledgement").
- **HOME.** CC 2.7.8. Add a new paragraph after the paragraph that begins "*The protocol and policy in force at a head.*", headed *A change its own voices left*.
- **DRAFT.**
  - "*A change its own voices left.* A counted change is self-forked for a counting row where every counted voice of it signed, in that row's past, a change it lies behind."
  - "A self-forked change is void for that row only where, at the fork point, the members seated there who signed only the other side outnumber those who signed only its side."
  - "A tie voids nothing, and neither does a fork point where no such member exists. The depth of either side decides nothing."
  - "A member signed a side where a counted voice of that member is on it, named as a head and not only cited, under a seat held at the fork point."
  - "A seat that a side granted is no evidence for that side."
  - "A row built on a void change is void with it. It is rescued where a voice of it never voiced a self-forked change, signed only one side, and was a member at its heads."
  - "Two sides that no voice rescues are both kept."
  - "Outside an election this is the only effect of one key signing two rows over one object, neither naming the other. It voids a change and never a key."
  - "A recovery is no exception: its holder is one voice under either key ([CC 2.6.1.11](#2.6.1.11))."
- **TABLES.**
  - The new paragraph needs a new row in `formal/derivation/rule_entries.tsv`, with the next free `rule_key` the checker accepts.
  - `formal/derivation/text_conflicts.tsv` has no row for it.
  - The ledger row "Fork attempts off one point" (CC 8.3.4, open) is unchanged by this rule. The register lane re-reads it after A-07.
- **NAMES.** None.
- **CHECKED BY.** The kernel's self-fork and rescue cases, and its tips case suite. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-02 defines "behind".
  - A-11 states the election's own self-fork rule, which differs: there the key is out of the close's base. Keep the boundary: this rule voids changes and never a voice.

### A-04 The fold over surviving tips, a record-change tip, and the contested pair in every group

- **RULE.**
  - The tips that survive the reader's line (A-02) and the self-fork rule (A-03) are folded under the text's guarded fold: an addition is in only where it meets its count on voices the fold seats.
  - A tip that changes the record is read under the protocol it states. Tips of different regimes wait, as CC 2.7.8 already says.
  - In every group, two concurrent changes that each remove or demote a member the other needs are contested, whether lone or counted. Neither is in force, and every seat is kept.
  - Concurrent founders' amendments of an `infrastructure` community wait: the founders common to them count until a version names both.
- **AUTHORITY.** Derived. It was accepted with the head rules. The text already has the guarded fold and the wait (CC 2.7.8).
- **HOME.** CC 2.7.8, second paragraph. This is an addition: keep "At several tips the roster is the fold of every tip's changes" and the guarded-fold sentences. Add the DRAFT after "Tips that differ in protocol or policy wait: the roster is then the members common to them, until a version names them."
- **DRAFT.**
  - "The fold is over the tips that survive the reader's line and the rule of a change its own voices left."
  - "A tip that changes the record is read under the protocol it states."
  - "In every group, two concurrent changes that each remove or demote a member the other needs are contested, lone or counted. Neither is in force, and every seat is kept ([CC 2.7.7](#2.7.7) rule 5)."
- **TABLES.** No quotes found for the surrounding sentences. Add new rows to `rule_entries.tsv`.
- **NAMES.** None.
- **CHECKED BY.** The kernel's fold model and its head-rules cases. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-05: rule 5 is the general form of the contested pair.
  - CC 4.5.13 "Two such removals of each other, concurrent at one head, are the contested pair of [CC 2.7.7] rule 5" is consistent, and stays.

### A-05 Rules 3, 5 and 6 of CC 2.7.7, for every group and for bundles

- **RULE.**
  - **Rule 5** governs every group. Two concurrent cuts that each remove a voice the other needs are contested, and neither is in force. A later count that names both settles them, and so does a receipt by a voice neither cut removes.
  - **Only cuts that count are inputs.** A row void for the reader by the line or by the self-fork rule contests nothing. A removed key's concurrent voice stops from the head the cut names.
  - **Rule 6.** A voice that answers both ways at one head has no say in any count at that head for that reader, a grant and a settling included. It stays in the base, so it stalls a count and never captures one. The exclusion is local to that head. A halt it fires still halts.
  - **Rule 3.** A row that names both concurrent rows decides between them.
  - For bundles, see A-09.
- **AUTHORITY.** Derived. Rule 5 for every group was accepted with the head rules. Rule 6's reach to any count at the head (grant and settling) was ruled in the trust root's context, and is written as rule 6's own.
- **HOME.** CC 2.7.7 *Conflict between concurrent rows*.
  - Rule 5. REPLACES: "5. **Equal standing.** Two cuts by keys of equal standing that undo each other stay contested. A voice that the other cannot remove settles them."
  - Rule 6. Addition: append the DRAFT to "6. **One say.** On one slot at one head, a voice that has acknowledged an act and voted to cut it, in two rows neither of which names the other, has no say there. It stays among the members the count is over."
- **DRAFT.**
  - Rule 5:
    - "5. **Equal standing.** Two concurrent cuts, in any group, that each remove a voice the other needs are contested, and neither is in force."
    - "A later count that names both settles them, and so does a receipt by a voice neither removes. A cut that counts for nobody contests nothing."
  - Rule 6, appended:
    - "Such a voice has no say in any count at that head for that reader, a grant or a settling included."
    - "It stays in the base, so it stalls a count and never captures one. A halt it fires still halts ([CC 4.2.1.1](part_4_composition_governance.md#4.2.1.1))."
- **TABLES.**
  - `rule_entries.tsv:4893` quotes rule 5's "Two cuts by keys of equal standing that undo each other stay contested".
  - `rule_entries.tsv:5186` quotes the list's opening sentence (unchanged).
  - Grep for "has no say there" and update any quote.
- **NAMES.** None.
- **CHECKED BY.** The kernel's head-rules cases (rule 5 over every group) and its root-fold cases (rules 3, 5 and 6 for bundles). Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-09.
  - CC 2.7.5 *window* "A landing with a strict majority behind it is final where no key of that majority answers both ways" is consistent.

### A-06 The roster merge

- **RULE.**
  - **What a merge is.** A merge is a `group:roster` version that names two or more tips, none in another's past. It names them in `refs.head` and `refs.further_heads`.
  - **How it is counted.**
    - It is counted on each tip it names, by that tip's own members, under the room's declared protocol. That count is the tip's own line, and it does not depend on the reader.
    - It is judged on the reader's line by its own heads.
    - A tip that is void for the reader does not block it.
  - **What it states.** A merge states the whole roster, and that roster is fixed: every member seated at any tip it names, less each member that a removal or an own end on any tip took out. A merge that states another roster concludes nothing.
  - **What it does not do.** It purges nobody and revives nothing.
  - **No duty seats.** A merge carries no duty seats. They fold from the conferral, withdrawal, resignation and election rows over the merged roster.
  - **Two merges.** Two merges of the same tips can differ only where their regimes differ, and then they are contested.
  - **A side that will not sign.** A side whose members will not sign stays a room of its own for the readers on its line.
  - **Infrastructure.** In an `infrastructure` community a merge is a founders' amendment counted on each tip. A stalled tip signs none: it is recovered first (CC 3.2 T7).
  - **The root.** At the root, a join is not blocked by a void predecessor. The keys of a tip that the self-fork rule voids count for that tip, and safety rests on the honest tip's majority.
- **AUTHORITY.** Derived. It was ruled before the head rules merged, prototyped by the kernel (22 cases) and accepted. The infrastructure form was derived later.
- **HOME.**
  - CC 2.7.8. Add a new paragraph *A merge* after the A-04 sentences.
  - CC 2.7.9. Delete the bullet "a roster version that names several heads on the wire;" from "The kernel does not settle these".
  - CC 3.3.6.4 "A row that merges tips names the others in `refs.further_heads`, as a roster version does" is consistent, and stays.
- **DRAFT.**
  - "*A merge.* A merge is a roster version that names two or more tips, none in another's past, in `refs.head` and `refs.further_heads`."
  - "It is counted on each tip it names, by that tip's own members under the room's declared protocol. It is judged on the line by its own heads, and a void tip does not block it."
  - "A merge states the whole roster: every member seated at any tip it names, less each member a removal or an own end on any tip took out. Otherwise it concludes nothing."
  - "A merge purges nobody and revives nothing. It carries no duty seat: those fold from the conferral, withdrawal, resignation and election rows over the merged roster ([CC 4.5.4](part_4_composition_governance.md#4.5.4))."
  - "Two merges of the same tips differ only where their regimes differ, and then they are contested."
  - "A side whose members do not sign a merge stays a room of its own for the readers on its line."
  - "In an `infrastructure` community a merge is a founders' amendment counted on each tip. A stalled tip signs none until it is recovered ([CC 3.2](part_3_the_namespace.md#3.2) T7)."
- **TABLES.**
  - `formal/derivation/family_shapes.tsv:108` (`group:roster`) reads "a version naming several heads is open on the wire". Restate it as "a merge names its tips in head and further_heads (CC 2.7.8)".
  - `constitution/signed_object_v2.tsv`, the `group-roster` `refs` row, has the note "The predecessor version in refs.head". Add "; on a merge, the further tips under further_heads".
  - The cascade then regenerates the CC 2.6.1.4 member table.
  - No quote found for the CC 2.7.9 bullet.
- **NAMES.** None new. `refs.further_heads` exists (`refs-members`).
- **CHECKED BY.** The kernel's roster-merge cases. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-01, A-02 and A-27 (the founders' amendment).
  - B-29 is the open-on-the-wire note.
  - The record has an earlier reading that a merge states the duty seats too. The later ruling (no duty seats) is the one written here.

### A-07 What the head rules leave: the residuals, written into CC 2.7.9 and CC 2.7.8

- **RULE.** The residuals the text carries, in its own form:
  - **(a) A reader with no row of its own, at a fork point no single-side member marks.** Such a reader reads, as one tip among others, a chain signed under the same protocol by keys that met a past count. Where no member seated at the fork point signed exactly one side, nothing voids that chain, and it may list members no other tip lists.
  - **(b) A newcomer admitted on a fork.** It reads that fork's roster where the rows cannot void it. Its way back is an admission on the other line.
  - **(c) The lone-sibling window.** A lone duty holder's concurrent conferrals are not judged against each other. The window closes for a reader at the room's next counted change that reader acknowledges, and for all once the lone holder signs a later change. The rows are evidence for a recall.
  - **(d) The accepted cost.**
    - A change every voice of which later builds without it is void where more members seated at the fork point signed only the other side.
    - Its own voices could have removed what it seated, by their count. A removal's base leaves out its target.
    - A void admission is no end (no room-key finality), and it leaves no removal row.
  - **(e) Two concurrent record changes wait.** While they wait, a removal under either protocol waits. This is the same limit as (a) for a reader with no row.
- **AUTHORITY.** Derived. Each residual was stated with the head rules for the text to carry.
- **HOME.**
  - CC 2.7.9 *What the kernel does not give*, the second bulleted list, the one that follows the bullet "No guard against a slot held on one signature". Its first bullet is restated as residual (a): replace the bullet that begins "Keys that met a past count can fork on a past head" with the (a) sentences. Add (b), (c), (d) and (e) after it.
  - CC 2.7.8 *The residual.* REPLACES the whole paragraph: "A key that is the whole of the members common to the tips is the count over them. So what it signed on either tip folds in for a reader with no acknowledgement of its own ([CC 2.7.9](#2.7.9)). That is one row sooner than a rule that made the tips wait would give. A reader that acknowledged the honest head is unmoved." Its new text points to CC 2.7.9 (a).
  - CC 3.3.4, *A roster event is counted at the head it names*. Restate the sentences after "A node with no acknowledgement of its own reads the roster as the fold of the tips ([CC 2.7.8](part_2_the_grammar.md#2.7.8))." (through "for good.") as one pointer sentence. Keep "A lineage with Receipts answers that ([CC 3.2](#3.2) T6), and each node's own trust decides whose Transparency Services count."
- **DRAFT.**
  - CC 2.7.9 bullets:
    - (a) "A reader with no row of its own reads, as one tip among others, a chain signed under the same protocol by keys that met a past count."
    - (a) "Where no member seated at the fork point signed exactly one side, nothing voids that chain, and it may list members no other tip lists."
    - (b) "A newcomer admitted on a fork reads that fork's roster where the rows cannot void it. Its way back is an admission on the other line."
    - (c) "A lone duty holder's concurrent conferrals are not judged against each other until the room's next counted change. The rows are evidence for a recall."
    - (c) "That change closes the window for each reader that acknowledges it, and the holder's own later change closes it for every reader."
    - (d) "A change whose every voice later builds without it is void where more members seated at the fork point signed only the other side."
    - (d) "Its voices could have removed what it seated by their own count. A void admission is no end, and leaves no removal row."
    - (e) "Two concurrent changes of a record wait, and a removal under either protocol waits with them."
  - CC 2.7.8 *The residual.*:
    - "*The residual.* A reader with no acknowledgement of its own is the edge these rules leave ([CC 2.7.9](#2.7.9)). A reader that acknowledged the honest side is unmoved."
  - CC 3.3.4 pointer:
    - "What a node with no acknowledgement of its own can be shown is the residual of [CC 2.7.9](part_2_the_grammar.md#2.7.9)."
- **TABLES.** No quote found for the CC 2.7.9 bullet or for the CC 3.3.4 sentences. Grep `rule_entries.tsv` for "unlist" and "list nobody that head did not list", and update any hit.
- **NAMES.** None.
- **CHECKED BY.** The kernel's head-rules case suite runs each residual as a stated case. Cite it when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-01 to A-06.
  - CC 3.2 T6 *fork attempt* paragraph, "Holders revoked at head five can sign forks off head four forever, and none of them moves a reader that acknowledged head five". Re-read it against A-02's sibling-safe line when this lands. It holds where head four is strictly behind head five.

### A-08 One target for each counted removal, and the community removal floor: DONE-IN-TREE

- **RULE.**
  - A counted removal names one member. The member removed is not counted over and is no voice. A removal that names more than one member concludes nothing.
  - The floor is two voices, so a room of two removes nobody by count.
- **AUTHORITY.** Derived (the kernel's option). The policy floor was ruled with the kernel.
- **HOME.**
  - CC 3.3.4, *Membership-change ceremony* item 1, which ends "A counted removal names one member. The member removed is not counted over and is no voice, and a removal that names more than one member concludes nothing." This landed in `c125852`.
  - The policy row `community_remove`, floor "2 voices". This is in the generated table of CC 4.5.13.
- **DRAFT.** None owed.
- **TABLES.** None owed. The acts table header states it.
- **NAMES.** None.
- **CHECKED BY.** The kernel's removal cases.
- **DEPENDS ON / CONFLICTS.**
  - B-31: the CC 4.4.3.17 pseudocode still counts the target. That fix does not wait.
  - C-14: the same one-target shape for a recall, a duty withdrawal and a demotion is asked and not ruled.

### A-09 The trust root after a fork: rules 5, 6 and 3 for bundles, recovery and the stated costs

- **RULE.**
  - **Already in the tree.**
    - A join (CC 2.6.1.11, *A bundle that joins tips*), landed in `e4abbf4`, `0eb963d`.
    - Unjoined tips folding where regimes are equal and resting on the common holders where they differ (CC 3.2 T6, *Two successors of one bundle*).
    - The grants rule: a grant resolves for a reader only while its voices are a strict majority of the holders in force at that reader. A later holder adds its voice by signing, and a retired key is no voice. This landed in `b64ae3c`. Checked at the pin: CC 3.2 line 1350 says it.
  - **Owed: rules 5, 6 and 3 for bundles.**
    - Two later bundles that each remove holders the other needs are contested, and the reader stays at the bundle they both extend (rule 5).
    - A holder who signed both has no say on either and stays in the base (rule 6).
    - A bundle that names both decides (rule 3).
    - Whether rule 5 reaches back where the honest line advanced and the reader acknowledged that advance was asked of the kernel, and the record holds no answer. Confirm it at the tag before writing anything on it.
    - Residual: where the other holders split evenly, one holder who signs a single side decides between them.
  - **Owed: recovery.**
    - A recovery bundle is not exempt from the head rules or the self-fork rule. Its holder is one voice under either key, which CC 2.6.1.11 already says.
    - A recovery concurrent with an amend that changes the charter leaves the recovering holder with no seat until a join. This is a stated cost.
    - Two concurrent recoveries under one commitment are contested.
    - A revocation with no bound takes a holder out of later counts only, which CC 2.6.1.11 already says.
  - **Owed: a stated residual.** A holder that signs a sibling bundle and then a grant is a fork of its own statements, and the reader does not read it as one.
  - **A halt** still halts (A-05).
- **AUTHORITY.**
  - The steward ruled the fork, direct: "3A and agreed". A trust-root fork folds like any roster, with no freeze, and the same rows give the same verdict.
  - Rules 5, 6 and 3 for bundles, and the costs, are derived and run in the kernel's root-fold cases.
- **HOME.** CC 3.2 T6 *Two successors of one bundle (normative)*. REPLACES: "A holder who signed both successors is visible in the rows, and nothing in the fold penalises it." Keep the sentence that follows it ("The cost is stated: …"). Add the recovery sentences to CC 2.6.1.11 *A recovery is the one exception to the count*, after "The holder is one voice under either of its keys."
- **DRAFT.**
  - CC 3.2 T6:
    - "Two successors that each remove holders the other needs are contested, and the reader stays at the bundle they both extend."
    - "A holder who signed both has no say on either and stays in the base. A bundle that names both decides ([CC 2.7.7](part_2_the_grammar.md#2.7.7) rules 3, 5 and 6)."
    - "Where the other holders split evenly, one holder who signs a single side decides between them."
    - "A holder that signs a sibling bundle and then a grant has forked its own statements, and no reader reads that fork."
  - CC 2.6.1.11:
    - "A recovery is read under the head rules as any bundle is ([CC 2.7.8](#2.7.8))."
    - "A recovery concurrent with an amend that changes the charter leaves its holder with no seat until a join names both. Two concurrent recoveries under one commitment are contested."
  - The CC 3.2 *Checked* note ("These readings are derived from the roster fold of [CC 2.7.8], and they are not yet run for a bundle."): restate it to cite the vendored root-fold case file. It must not keep "not yet".
- **TABLES.**
  - No quote found for "A holder who signed both successors is visible in the rows".
  - Contested recoveries may want a refusal name. None is ruled: do not add one. Report the gap if the writer needs one.
  - The local trust-root model (`formal/trust_root`) still quotes the freeze sentences that left the text (its invariants `Inv_ForkNeverFreezes` and `Inv_FreezeAdoptionOnly`, and its plants `fork_freezes` and `freeze_blocks_ends`). Re-read it against the vendored root-fold cases, and record the result in `formal/derivation/models_vs_text.tsv`. It is a model job: run it through the shared job scheduler.
- **NAMES.** None.
- **CHECKED BY.** The kernel's root-fold cases (Python reference, 39 cases at its first run, and the cases added since). Cite them when vendored.
- **DEPENDS ON / CONFLICTS.** A-05 and A-10. CC 2.6.1.11 "Two later bundles on one predecessor are a fork, and each is read on its own" stays.

### A-10 The bounded settler

- **RULE.**
  - **What a settler is.** A settler is a counted row over the holders of a head. It is counted over the holders who have a say there: a double signer under rule 6 is out of its base, for this count only.
  - **What it may say.** It may only name one contested sibling as the one that stands. It adds nothing else. A row that does anything else takes the full base.
  - **What it is not.** A settler is never self-forked, and it is no head of its own.
  - **After it.** A reader acknowledges the later bundles after it again. That is a node's own mechanical act.
  - **Two settlers.** A holder that signs two settlers naming different siblings has no say.
  - **Residual.** Until a reader holds a settler, holders removed on one side can keep that reader stopped at the contest.
  - **The alternative.** The alternative to the settler was a stated permanent stall.
  - **Wire.** `refs.target` is the sibling that stands, and `refs.also.cites` the other siblings. The family is not named (see NAMES).
- **AUTHORITY.** Derived. It was told to the steward, and it is his to overturn (Group C, C-03).
- **HOME.** CC 3.2 T6. Add a new paragraph after *Two successors of one bundle (normative)*, headed *Settling a contest*. Add the wire to CC 2.6.1.11 *What a bundle carries and names*.
- **DRAFT.**
  - "*Settling a contest (normative).* A settler is a row counted over the holders of the contested pair's head who have a say there. A holder that signed both sides is out of its base for this count."
  - "It names the one sibling that stands in `refs.target` and the others in `refs.also.cites`, and it does nothing else. A row that does more is counted over every holder."
  - "A settler is no head and is never self-forked. A reader acknowledges again the bundles after it."
  - "A holder that signs two settlers naming different siblings has no say in either."
  - "Until a reader holds a settler, holders removed on one side can keep that reader stopped at the contest."
- **TABLES.**
  - `constitution/signed_object_v2.tsv` needs rows for the settler's payload, with its `refs` naming `target` and `also.cites`.
  - The family is registered in the CC 3.1 table, and the cascade regenerates `manifests/family_model.json`. Tell the kernel the new hash.
  - Families: 189 becomes 190.
- **NAMES.** The settler's family is **not recoverable from the notes**: it is marked "family TBD" (wire-map N8 and N9). The writer asks the coordinator for the name before writing. Is it a leaf of an existing genesis family, or a family of its own? A trust-root row is a signed object or a row, and this is a counted row.
- **CHECKED BY.** The kernel's settler cases in its root-fold suite. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-09 and C-03.
  - CC 3.2 T6 "The reader then acts on what it held before them, until a bundle names both" gains "or a settler names one" (append ", or a settler names the one that stands").

### A-11 The moderator election, as finally ruled

- **RULE.**
  - **Reading.** Every "counted", "end" and "holds" in the election's rules means as the reader's roster takes it, on the reader's line, never merely concluded.
  - **One election per seat end.** An election opens for one end of a seat as the reader's roster takes it.
  - **The opening.**
    - The opening is a counted row at the newest heads (A-01), under the policy row `election_open`: a strict majority of the members, with a floor of two voices or the roster's size if smaller.
    - The electorate is the roster's members at the opening's heads.
    - A member admitted before the opening votes and may stand. A member who left is neither candidate nor voter.
    - A lay-down outside the opening's past changes nothing in that election.
  - **Rival openings.**
    - Rival openings are contested.
    - A fork of ends is resolved by a counted end that has both in its past.
    - A holder's own lay-down concurrent with a counted end of its seat is no fork.
    - A person who cosigns both rival openings has no say in either.
    - Once a resolving opening is counted, the earlier ballots and seatings are void, and the members vote again.
  - **Naming the opening.** Every ballot, withdrawal, receipt, decline and seating names the opening by reference, never by digest. The seating cites each ballot, withdrawal and decline it counts.
  - **Inputs.**
    - Every input is read through persons and the key view: one ballot per person.
    - An agent's key is neither candidate nor voter.
    - A ballot ranks at most three, and one that ranks more is void.
    - Each row a key signs in an election has that key's earlier rows of that election in its past.
    - A key that signs two rows of one election, neither naming the other, is no voice and is out of the base of the close. That never re-tallies a set already named.
  - **The count and the seating.**
    - The count is instant runoff (A-12).
    - The seating is the winner's own acceptance, and its signer must be the key the count yields.
    - A winner who declines, or is silent past the grace, passes the seat down the runoff order.
  - **The close.**
    - A strict majority of the electorate, the winner apart, receipting one standing seating closes the election for every reader that holds those receipts. The close is reader-relative.
    - Two seatings that each meet that close are neither closed. Nobody sits until a seating over the union.
    - A reader with no line waits.
    - The node's 24 hours and the grace are that node's own reading, and they decide nothing that counts.
  - **What is seated.** An election seats `moderate` only. A room whose only duty holder is an agent's key locks.
  - **Harsh edges, to state.**
    - Until the close, a late ballot can change who sits.
    - A room that never receipts never closes.
    - An odd base with a minimal majority can lose its close.
    - A device restored from an old backup signs twice honestly, gets no exception, and returns under a new room key.
- **AUTHORITY.**
  - The steward, direct (2026-11-28, to the kernel): the election close is fixed in the kernel's next tag. The election's base is the electorate at the one vacancy the opening names. A lay-down outside the opening's past changes nothing in that election. The close is reader-relative. Every input of the close is read through persons and the key view.
  - The steward, direct (2026-11-25): the election is in the kernel tag ("hold the kernel tag until it is right").
  - The rest is derived, from the election's later reads, and given to the coordinator in final form.
- **HOME.**
  - CC 4.5.13, three paragraphs:
    - **The moderator election — the room locks and chooses (normative).** Keep its first five sentences, through "It then **elects**, in a vote of **24 hours**." REPLACES from "The **ballot is the roster**, every member a candidate" to the end of the paragraph.
    - **One result on every node (normative).** REPLACES the whole paragraph, beginning "Nothing signed opens an election, since a seat that reaches the end its own row states has no row of its ending."
    - **The floor in a small room.** REPLACES "The ballot and the acceptance are the rows of [CC 3.1.4](part_3_the_namespace.md#3.1.4), `ballot:moderator:v1` and `ballot:moderator_acceptance:v1`." (the cite names CC 3.1.4; the rows are in CC 3.1.3).
  - CC 4.5.4 rule 2, "read-only until a 24 h ranked-choice vote over its own roster seats one": consistent; leave it.
  - CC 3.1.3 table, rows `ballot:moderator` and `ballot:moderator_acceptance` (lines 251 and 252). REPLACES their descriptions (DRAFT below).
- **DRAFT.**
  - *The moderator election* (from "The ballot is the roster"):
    - "The electorate is the members at the heads of the row that opens the election. Every one of them is a candidate except an agent's key, and the order of [CC 4.5.4](#4.5.4) rule 2 decides nothing."
    - "Each person ranks up to three. A ballot that ranks more is void. One ballot counts for each person, folded as a vote is."
    - "Each row a key signs in an election has that key's earlier rows of that election in its past."
    - "A key that signs two rows of one election, neither naming the other, is no voice there and is out of the base of the close."
    - "The count is instant runoff ([CC 4.5.13](#4.5.13), ranked choice). **The winner accepts by their own row**, which is the seating: its signer is the key the count yields."
    - "A winner who declines, or is silent past the policy's `election_grace_secs`, passes the seat to the next in runoff order. Nobody holds a duty they never signed for."
    - "An election seats `moderate` only."
  - *One result on every node*:
    - "**One result on every node (normative).** An election opens for one end of a seat, as the reader's roster takes that end. Its opening is a counted row at the newest heads, under the policy row `election_open`."
    - "Every word *counted*, *end* and *holds* in these rules means as the reader's roster takes it."
    - "A member admitted before the opening votes and may stand. A member who left before it does neither, and a lay-down outside its past changes nothing in that election."
    - "Rival openings are contested. A person who cosigns both has no say in either."
    - "A fork of ends is settled by a counted end that has both in its past. A holder's own lay-down concurrent with a counted end of its seat is no fork."
    - "Once a settling opening is counted, the ballots and seatings of the earlier openings are void, and the members vote again."
    - "Every ballot, withdrawal, decline, receipt and seating names its opening by reference. The seating cites each ballot, withdrawal and decline it is counted over."
    - "A strict majority of the electorate, the winner apart, that receipts one standing seating closes the election for each reader holding those receipts."
    - "Two seatings that each meet that close leave the election open, and nobody sits until a seating over their union is held."
    - "A reader with no line of its own waits. A node's 24 hours and the grace are its own reading, and decide nothing that counts."
    - "Until the close a late ballot can change who sits, and a room that never receipts never closes. An odd base with a bare majority can lose its close."
    - "A device restored from an old backup that signs twice is no voice in that election, and returns under a new room key."
  - *The floor in a small room*, last sentence:
    - "The ballot and the seating are the rows `ballot:moderator:v1` and `ballot:moderator_acceptance:v1` of [CC 3.1.3](part_3_the_namespace.md#3.1.3)."
  - CC 3.1.3 row `ballot:moderator`:
    - "**A member's ballot in a moderator election** ([CC 4.5.13]): `community_id`, the opening it answers by reference, and `ranks`, up to three member keys in order. One ballot per person, folded as a vote is. A ballot that names no opening held, or ranks a non-member, is kept and not counted. Wire `ballot:moderator:v1`. Community scope."
  - CC 3.1.3 row `ballot:moderator_acceptance`:
    - "**The winner's seating**: `community_id`, the opening by reference, and each ballot, withdrawal and decline it is counted over, cited by reference. It waits until the node holds every row it cites. It is not counted unless the count over exactly those rows yields its signer. Wire `ballot:moderator_acceptance:v1`. Community scope."
- **TABLES.**
  - Quote-table rows to update at the pin:
    - "Nothing signed opens an election": `door_text.tsv:15`, `rule_entries.tsv:1501`.
    - "Among the valid acceptances a node holds, the one counted over the larger set stands": `fold_text.tsv:133`, `rule_entries.tsv:1394`.
    - "digest of the community id and the last seating row": `rule_entries.tsv:1389`, `rule_entries.tsv:3766`–`3769`, `rule_inventory.tsv:3139`, `text_conflicts.tsv:401`.
    - "the digest of the ballot and withdrawal rows counted": `cell_cites.tsv:93`, `fold_text.tsv:132`, `rule_entries.tsv:3770`–`3772`, `text_review.tsv:33`.
    - "The ballot and the acceptance are the rows of": `rule_entries.tsv:1397`.
    - "A winner who declines, or is silent past a grace": `cell_cites.tsv:94`, `door_text.tsv:17`, `rule_entries.tsv:1385`.
    - "the winner's acceptance row binds the ballot set it was seated on": `count_text.tsv:20`, `guard_text.tsv:11`, `reaction_text.tsv:108`, `rule_entries.tsv:1392`.
    - "An acceptance waits until the node holds that set": `rule_entries.tsv:1393`.
    - "Two acceptances over different sets of equal size are a tie": `fold_text.tsv:133`, `rule_entries.tsv:1394`, `tools/divergence_cases.py:402`.
    - "A ballot is void only against the seating that wins": `rule_entries.tsv:1395`.
    - "A member leaving while the room is locked therefore changes nothing": `rule_entries.tsv:1390`.
    - "The electorate is the roster the election names": `cell_cites.tsv:87`, `fold_text.tsv:183`, `policy_text.tsv:64`, `rule_entries.tsv:1391`, `rule_inventory.tsv:3141`.
    - "Among valid acceptances the larger set seats": `cell_cites.tsv:91`, `rule_entries.tsv:3770`–`3772`.
  - Policy rows:
    - `moderator_election` (`at_window` `stay_open`, landed by `winner`) stays.
    - `election_open` exists (`7b88ac6`). Check that its note says "at the newest heads; rival openings contested".
  - `formal/derivation/names_head_text.tsv`, the `ballot:moderator_acceptance` note "it names the election and the ballot set it was counted over", restated as "it names the opening and cites the rows it was counted over".
  - The acts row `election_seating | moderate | community | moderator_election` stays.
  - `constitution/signed_object_v2.tsv` needs payload rules for both ballot families (B-13), and the family model's `ballot:moderator_acceptance.body` becomes stated.
  - Ledger (register lane): the bullet "an election winner who declines passing the seat to the next … exercised by no run" in *What the rule tables leave unstated* closes once the kernel's decline case is vendored.
- **NAMES.**
  - The opening is a counted row under policy `election_open` (exists). Its family and role are **not recoverable from the notes**. The `ballot:*` table has no opening leaf. Ask the coordinator which family the opening row is before writing.
  - The role by which a ballot names its opening (`refs.answers` or `refs.also.cites`) is **not recoverable**. The wire-map readings proposed either. Take the kernel's wire map at the tag.
  - The decline is `membership:decline:v1` (`membership-reply`). The record says it "answers the seating row". Which row that is, when the seating is the winner's own acceptance, is **not recoverable**. See B-14.
- **CHECKED BY.** The kernel's election cases: the opening, rival openings, the ranked count, the close by receipts, and the self-fork in an election. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-01, A-02, A-12, A-13, B-13 and B-14.
  - CC 4.5.4, *The election (rule 2) emits exactly this appointment shape*, "No node signs anything" stays true.
  - CC 2.7.5 *window* is unaffected.
  - CC 3.1.3 row `ballot:moderator_acceptance` "the node's own 24 h since the lock have passed" goes (DRAFT above).

### A-12 Ranked choice: options with no ballot fall together, and the runoff order

- **RULE.**
  - In every ranked count, the options that hold no ballot still counting are eliminated together in one round.
  - The runoff order is the same count repeated, with each option already ahead of it struck. A step that ties yields nobody and ends the order.
  - This holds for every ranked count, not only the election.
- **AUTHORITY.** Derived, and built by the kernel. The kernel's own note: it moves rounds in about 18% of counts of four to six options, and some counts with no winner then seat (example A6 B3 C1).
- **HOME.** CC 4.5.13 *Ranked choice is one count, and any choice among options may use it (normative)*. Add after "While no option holds more than half of the ballots still counting, the weakest standing option is eliminated, and its ballots pass to their next standing choice."
- **DRAFT.**
  - "In each round, every standing option that holds no ballot still counting is eliminated together, before the weakest is."
  - "The runoff order is the same count repeated with each option ahead struck. A step that ties yields nobody and ends the order."
  - Confirm "before the weakest is" against the kernel's case at the tag. The record says only "eliminated together each round".
- **TABLES.** `formal/derivation/models_vs_text.tsv:47` quotes "A tie for weakest goes against the option later". That is unchanged, but check the row's verdict.
- **NAMES.** None.
- **CHECKED BY.** The kernel's ranked-count cases. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.** A-11.

### A-13 Persons: counts over persons, and the key view

- **RULE.**
  - **Persons.** Every count is over persons, its base and its voices alike.
  - **An agent's key.** An agent's key is taken out before the key-to-person map, and it is never its owner's voice.
  - **When a key speaks.** A key speaks for a person only while it is a live key of that person's self roster, the genesis key included.
  - **One roster.** One identity has one self roster.
  - **Read in the act's past.** Persons are read in the act's own past: for a count, for a countersign's "outside", and for a rival founding. So a verdict for a presented row is fixed by its past.
  - **`iss` and `kid`.** A rule that reads who signed reads `iss`. A rule that reads a key's life, cover or lapse reads `kid`. `iss` must be the person of `kid` (step 8).
- **AUTHORITY.**
  - Derived. The kernel moves every count to persons.
  - The `iss`/`kid` reading is what the text already says (CC 2.6.1.1, CC 2.6.1.7 step 8).
  - Persons read in the act's past was given by the coordinator in final form.
- **HOME.**
  - CC 4.5.13 *One vote per person*, after "A roster seats a key ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)), the person is the fedID whose self roster the key belongs to ([CC 3.3.6.4](part_3_the_namespace.md#3.3.6.4)), and a tally counts fedIDs."
  - CC 2.6.1.4 *Logical names*, for the `iss`/`kid` sentence (optional, wire-map G1 and G25).
- **DRAFT.**
  - "A count maps both its base and its voices to persons, through the self rosters read in the act's own past. So a verdict on a row is fixed by that row's past."
  - "An agent's key is taken out before that map and is never its owner's voice ([CC 4.5.4](#4.5.4))."
  - "A key speaks for a person only while it is a live key of that person's self roster, the genesis key included. One identity has one self roster."
  - For CC 2.6.1.4: "A rule that reads who signed reads `iss`, and a rule that reads a key's life reads `kid`. `iss` is the person of `kid` ([CC 2.6.1.8](#2.6.1.8) step 8)."
- **TABLES.** `rule_entries.tsv:1467` and `rule_inventory.tsv:3217` quote "a tally counts fedIDs" (unchanged). Add rows for the new sentences.
- **NAMES.** None.
- **CHECKED BY.** The kernel's person-key cases (`person_keys` and the key view). Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-14 and A-20.
  - CC 4.5.4 *An agent's key* "It is in no count and in no base of any count" is consistent.
  - In a private room the map gives the voice, not the person (CC 2.6.1.11). Keep that: there the count of persons waits for bindings (CC 3.1.3.2).

### A-14 A rival founding of a self roster

- **RULE.**
  - Two rows that each found the roster of one self are rival foundings, and the reader's line alone resolves them.
  - The line is monotone: the reader keeps the earliest row by which it took a roster up.
  - What puts a row on that reader's line is the reader's own signed rows, and the concluded seat rows of which the reader is a voice. Each counts only where it is in the past of every end of its key.
  - The genesis key loses no voice.
  - A device that holds a genesis key and no roster row fetches the roster before it signs. It never founds a roster where one may exist.
- **AUTHORITY.**
  - Derived, and ruled with the kernel: a rival founding is resolved by the reader's line only, and the genesis key is a key like any other.
  - The coordinator gave the final form. A variant in which the genesis key lost its voice is withdrawn: do not write it.
- **HOME.** CC 3.3.6.4 *The head a self-roster row names*. Add after "The first bind of a new identity names the genesis key's own record."
- **DRAFT.**
  - "Two rows that each found the roster of one self are rival foundings. A reader keeps the roster its own line took up first, and the genesis key keeps its voice ([CC 2.7.8](part_2_the_grammar.md#2.7.8))."
  - "A device that holds a genesis key and no roster row MUST fetch the roster before it signs. It MUST NOT found a roster where one may already exist."
- **TABLES.** Add a new row in `rule_entries.tsv`.
- **NAMES.** None.
- **CHECKED BY.** The kernel's self-roster founding cases. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-02 and A-13.
  - The self-roster model table in CC 3.3.6.4 has no row for a rival founding. The register's self-roster model is not changed by this entry.

### A-15 The end of a key is a cut

- **RULE.**
  - **What a cut leaves standing.** A row of a key that has ended stands for a reader in three cases:
    - where it is in the end's past;
    - where it is on that reader's line before the reader held the end;
    - where it is in a count final by acknowledgement.
  - **A rotated-away key.** A revocation signed by a key that a rotation replaced is no end. The person's key roster ends a retired key.
  - **A roster's end of a key.** It ends the key as a key of that person: it has no voice and no standing there, and the person's map does not give that person for a row with the end in its past. It does not end the key's own liveness, which only its own revocation ends.
  - **The signer's duty.** An honest revocation names the last rows of the key that it holds good.
  - **The cost.**
    - A vote of the key that a reader took up before the end stands at that reader.
    - A count final by acknowledgement stands for all.
    - The remedy is the members' later count.
    - Rows a reader had not taken up are lost to it when whoever holds the key revokes it naming nothing.
  - **No content anchor.** A citation of a row by a co-member anchors nothing.
- **AUTHORITY.** Derived. It was the kernel's proposal, agreed, and its content-anchor variant is dropped. "The roster's end ends the key as a key of that person, not its liveness" is what the text already says (CC 2.4.1.1 *Who may revoke a key*: "Only the key's own revocation ends its liveness").
- **HOME.** CC 2.4.1.1 *Who may revoke a key (normative)*. Add after "Only the key's own revocation ends its liveness, and neither of the others does ([CC 2.7.5](#2.7.5))."
- **DRAFT.**
  - "An end of a key is a cut. A row of that key stands for a reader where it is in the end's past, on that reader's line before it held the end, or in a count final by acknowledgement."
  - "A roster's end of a key ends it as a key of that person. For a row with the end in its past, the key is no key of that person's `iss` ([CC 2.6.1.8](#2.6.1.8) step 8)."
  - "A revocation signed by a key that a rotation replaced is no end; the person's key roster ends a retired key."
  - "A revocation SHOULD name in `trusted_through` the last rows of the key it holds good."
  - "A vote of the key that a reader took up before the end stands at that reader, and a count final by acknowledgement stands for all. The members' later count is the remedy."
  - "Rows a reader had not taken up are lost to it where whoever holds the key revokes it and names none of them."
- **TABLES.**
  - Ledger (register lane): the open row "Rows a revoked key signs and dates before its `revoked_after`" says "A key revocation MAY name in `trusted_through` the last rows of the key it holds good, and no sentence says what a reader does with them". This entry gives the reader's rule for a cut. The register lane re-reads whether the row narrows or closes, since `revoked_after` itself is unchanged.
  - `trusted_through` on `key:revocation:v1`: check `signed_object_v2.tsv` has the member on the revocation rule. If not, add a row "where the revoker names the rows of the key it holds good".
- **NAMES.** None new.
- **CHECKED BY.** The kernel's key-end cases. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - B-20 (the eviction's instants are documentary) and A-23 (a retired suite reads the same anchor).
  - "Voiding a rotation by the roster's counted act" is **not recoverable from the notes**. Only the rotated-away key's revocation rule is recorded. Do not write a sentence for it.

### A-16 The self roster: the landed window, two lone evictions, the lone add, and two keys

- **RULE.**
  - **The landed window.** A landed self-roster window is the seat change itself. No further row seats the added key or evicts the target.
  - **Two lone evictions.** Two lone evictions of each other, concurrent, are contested, and neither lands.
  - **Lone eviction, as written.** The lone eviction stands as written at any size (CC 3.3.6.4). The target's own signature is its defence, and no "any one objection" clause is added.
  - **The lone add, as written.** Its stated cost: a holder of one key of three who adds a key while one other key is silent then holds half the roster, and no count and no lone path removes that key. Whether a lone add should need the other members' silence is C-02.
  - **One key and two keys.**
    - Two keys cover the loss of one: one key proposes the other's eviction, and it lands after the window unless the other key answers.
    - The only bound is an active stolen key that answers within the window: two live keys at a stalemate, which a third key breaks.
    - No sentence tells a person they need three devices.
    - No sentence says an owner can revoke a stolen device key itself, since the owner has no copy of it.
    - A local lock on key use (a PIN or a biometric) is no account, identity or recovery path.
- **AUTHORITY.**
  - The steward, direct, on two keys: "Most people wont know what CIRIS is and installs generally require a login - with 2, one can propose an eviction and if the other does not respond it lands, I thought we settled that". On the login: "the login just secures key use, and is optional, a pin or biometric can be used".
  - The rest is derived and ruled with the kernel. The coordinator gave the final form (landed window, two evictions, lone add cost).
- **HOME.** CC 3.3.6.4.
  - *The outcome.* Add after "While a proposal is open or contested, nothing it would change has changed."
  - *An addition.* Add after "So a holder of one key of three adds a key after the window, unless both other keys object."
  - *One key and two keys.* REPLACES: "That bound is stated so a person knows it: a self SHOULD hold three keys."
- **DRAFT.**
  - *The outcome*:
    - "A landed proposal is the seat change itself, and no further row seats the added key or evicts the target."
    - "Two lone evictions of each other, concurrent, are contested, and neither lands."
  - *An addition*:
    - "That is a stated cost. A holder of one key of three who adds a key while one other is silent holds half the roster, and no count or lone path removes that key."
  - *One key and two keys*:
    - "Two keys cover the loss of one: a key that stays silent through the window is evicted by the other's lone path."
    - "Only a stolen key whose holder keeps signing holds a pair at a stalemate, and a third key breaks it."
- **TABLES.**
  - "a self SHOULD hold three keys": `rule_entries.tsv:2701`, `rule_inventory.tsv:1840`.
  - "At **two** keys the quorum path is both keys": `rule_entries.tsv:2706` (the paragraph stays, so check the quote).
  - The self-roster model table ("Two keys, one lost | closes"; "Two keys, one stolen | stalls (safety holds, recovery does not)") is consistent and stays.
- **NAMES.** None.
- **CHECKED BY.** The kernel's self-roster cases and the register's self-roster model. The two concurrent lone evictions are a kernel case. Cite it when vendored.
- **DEPENDS ON / CONFLICTS.** C-02. The *What the lone path costs* bullet "An owner with one live key cannot evict a stolen key whose holder signs any row" stays.

### A-17 Duty acts: quarantine, slashing, takedown, reconsideration and the lift

- **RULE.**
  - **Quarantine.** A quarantine targets a key and is the act of a `slash` holder. There is no quarantine duty. The marker plane never withholds itself, and a withhold outranks a release until a release names it.
  - **A release.** A release is an end of its withhold: the same holder's `supersedes` of that withhold, naming it in `refs.target`. Only that holder releases. Any other relief is the members' lift.
  - **Slashing.** A slashing verdict is about a key, after adjudication.
  - **Takedown.** A takedown targets a content row and is the act of a `takedown` holder. It ends by a `review` holder's reconsideration that cites it, where only the outcome `reversed` ends it, or by the members' lift.
  - **Lone acts and the lift.**
    - All three are lone duty acts, with no acts-table row in a community.
    - The members lift each by `moderation_overturn`, with the base of A-18.
    - The target of a lone duty act never releases, lifts or reverses it.
  - **One act each.** A lift and a reconsideration each cite exactly one act or notice, in `refs.also.cites`. One that cites none or two concludes nothing.
  - **Families.** `quarantine:{state}`, `slashing:{outcome}`, `takedown_notice:{basis}` and `reconsideration:{grounds}`. A reconsideration's member `outcome` is `reversed`, `partial` or `upheld`.
  - **Licences.** There is no licence-to-licence chain. "The charter is read at read" is a reader's honouring, not an end.
- **AUTHORITY.**
  - Derived, from the duty table of CC 4.5.4.
  - The release rule was ruled with the kernel after re-reading the family model ("released supersedes withheld") and Part 8's rule entry (`supersede | author`).
  - The coordinator gave the final form (exactly one cite, the target never releases).
- **HOME.**
  - CC 4.5.5 *Moderation as a delegable duty*: add a paragraph *The lone duty acts* after its duty table.
  - CC 3.1.9.2 table rows:
    - `quarantine:{state}`, line 754. REPLACES "The withhold holds until a release names the withhold it lifts."
    - `reconsideration:{grounds}`, line 760. REPLACES "Outcome `reversed` / `partial` / `upheld`."
- **DRAFT.**
  - CC 4.5.5 *The lone duty acts*:
    - "A quarantine targets a key and is a `slash` holder's act; a slashing verdict is about a key after adjudication. A takedown targets a content row and is a `takedown` holder's act."
    - "Each is one duty holder's act, and the members lift it by `moderation_overturn` ([CC 4.5.13](#4.5.13)). The target of such an act never releases, lifts or reverses it."
    - "A `review` holder reverses a takedown by a reconsideration that cites it; only the outcome `reversed` ends it."
    - "A lift or a reconsideration cites exactly one act or notice in `refs.also.cites`. One that cites none or two concludes nothing."
  - CC 3.1.9.2 `quarantine:{state}`:
    - "The withhold holds until its own holder releases it. A release is that holder's `supersedes` of the withhold, naming it in `refs.target`, and any other relief is the members' lift."
  - CC 3.1.9.2 `reconsideration:{grounds}`:
    - "`new_evidence` / `procedural_error` / `quorum_compromise`. It cites the one notice or act it rules on in `refs.also.cites`. Its member `outcome` is `reversed`, `partial` or `upheld`, and only `reversed` ends that act."
- **TABLES.**
  - "The withhold holds until a release names the withhold it lifts": `rule_entries.tsv:3801`, `rule_entries.tsv:3802`, `tools/divergence_cases.py:397`.
  - "Outcome `reversed` / `partial` / `upheld`": `rule_entries.tsv:3811`.
  - The payload rules are B-06 (reconsideration), B-07 (release) and B-08 (lift).
  - The acts table header already says a quarantine, a slashing verdict and a takedown in a community have no row there.
  - A refusal name for "cites none or two" is **not ruled**. If the writer wants one, it needs a `refusal_tokens_review.tsv` row with kind `concludes_nothing`, and the name must come from the coordinator.
- **NAMES.** The member `outcome` (tstr, closed `reversed` / `partial` / `upheld`) on `reconsideration:{grounds}`. It is registered by B-06.
- **CHECKED BY.** The kernel's duty-acts cases (quarantine, slash and takedown as acts). Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-18, B-06, B-07 and B-08.
  - CC 2.4.1.1's kept list ("a `quarantine:*` marker" is never withdrawn by a named party) is consistent.

### A-18 The lift: its heads, its two-head base, and no freshness clock

- **RULE.**
  - The lift names the newest counted heads in its own past (A-01) and cites the act.
  - Its base is the members seated both at the head the act names and at the lift's own heads, the act's author apart. So nobody joins a room to overturn it, and a member gone since is not counted.
  - The windowed overturn uses the same base.
  - An objection's freshness against `W` leaves the text: an objection concurrent with the landing is recounted, and one with the landing in its past counts for nothing (CC 4.5.13 *The clock of a window*, already in).
- **AUTHORITY.** Derived from the steward's lift ruling. The text and the policy row were owed once the kernel's cases passed. The removal of the freshness clause follows the kernel's withdrawn freshness reading: keep the recount, drop `W`.
- **HOME.** CC 4.5.13.
  - *The members' check — one acts, the room may lift (normative)*:
    - REPLACES "The act is lifted when a strict majority of the members seated at the head the act names, the act's author apart, has objected within the 48-hour window."
    - Delete "An objection counts at a node only where the node first held it within the freshness window `W` of its signed instant ([CC 2.6.7](part_2_the_grammar.md#2.6.7))."
    - REPLACES "Only a member seated at the head the act names counts, so nobody joins a room to overturn it."
  - *The lift of an agent's removal*. REPLACES "It concludes whenever its objections meet the count over the members at the head the removal names, the author and the removed key apart."
- **DRAFT.**
  - "The act is lifted when a strict majority of the members seated both at the head the act names and at the lift's own heads, the act's author apart, has objected within the 48-hour window."
  - "Only a member seated at both heads counts, so nobody joins a room to overturn it, and a member gone since is not counted."
  - Agent's removal: "It concludes whenever its objections meet the count over the members seated both at the head the removal names and at its own heads, the author and the removed key apart."
- **TABLES.**
  - "The act is lifted when a strict majority of the members seated at the head the act names": `cell_cites.tsv:701`, `text_conflicts.tsv:475`, `tools/divergence_cases.py:244`.
  - Grep `rule_entries.tsv` for "freshness window `W` of its signed instant" and "Only a member seated at the head the act names counts".
  - Policy row `moderation_overturn` ("the set at the act"): its counted-at cell becomes "the act's head and the lift's own heads". Set that in `formal/derivation/policy_text.tsv`. The cascade moves the policy pin. Tell the kernel and each implementer the new pin.
- **NAMES.** None.
- **CHECKED BY.** The kernel's lift cases (the lift's head and its two-head base). Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-01 and A-17.
  - CC 2.7.9 bullet "an objection counted within `W` ([CC 4.5.13])" in "The kernel does not settle these": delete that clause once the sentence above is gone.

### A-19 Who is served: carriage of rows

- **RULE.**
  - **Only to current-roster keys.** Carriage is of rows, and only to keys on the room's current roster, transitively. A joiner holds the past its admission names, and what is sealed under an earlier epoch's key it holds as ciphertext.
  - **Nothing to a key off the roster.** An invitee is carried its invitation alone, and a removed key its removal alone.
  - **Leaving a room.** A row leaves its room only by its own signer's act.
  - **Key grants.** A `key_grant` is never carried. It is served by the placement of the content it wraps, and only the key it names opens it.
  - **`history_on_join`.** It is no part of who is served. It marks a kept stream.
  - **The joiner.** A joiner receives what the tier gives a joiner and nothing more.
- **AUTHORITY.** Derived, run by the kernel on 53 cases, and agreed.
- **HOME.** CC 5.2 *What a row carries (normative)*. Add after its second paragraph, the one that ends "The keys a roster row seats or removes are always within its audience." The existing sentence "A row placed in a room is in the audience of the room's roster as it stands when a node replicates it" stays.
- **DRAFT.**
  - "Carriage is of rows, and only to keys on the room's current roster. A joiner is carried the rows its admission names, transitively; what an earlier epoch's key seals it holds as ciphertext."
  - "Nothing is carried to a key off the roster: an invitee is carried its invitation alone, and a removed key its removal alone."
  - "A `key_grant` is never carried. It is served by the placement of the content it wraps, and only the key it names opens it ([CC 3.3.2](part_3_the_namespace.md#3.3.2))."
  - "`history_on_join` is no part of who is served ([CC 4.4.3.10](part_4_composition_governance.md#4.4.3.10))."
- **TABLES.**
  - "The keys a roster row seats or removes are always within its audience": `cell_cites.tsv:708`, `cell_cites.tsv:709` (unchanged).
  - "A row leaves its room only by its own signer's act": `models_vs_text.tsv:4`, `:8`, `:22`, `:40`, `rule_entries.tsv:5207` (unchanged).
  - Add rows for the new sentences.
- **NAMES.** None.
- **CHECKED BY.** The kernel's audience and copy cases. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - CC 3.3.4 *Who is served* (held change), CC 3.3.4 *A resignation*, CC 2.7.5 *missing, and what is copied*, and CC 4.4.3.10 `history_on_join` are all consistent.
  - CC 2.1 `history_on_join` row ("At `community` and `affiliations`, `history_on_join` is carried and does not change what a new member receives") is consistent.

### A-20 The affiliation's countersign is a voice on the act's own row

- **RULE.**
  - The outside countersign of a one-officer affiliation's act is a voice on that act's own row: a further statement over its payload by an eligible outside key. It is counted with the officer's under `affiliation_member_action`, two of two.
  - The outside key is read in the act's own past.
  - The officer's withdrawal of the act retires it from its head on, as any end does.
- **Already in the tree.** While an affiliation has one officer, admitting a member is its only act that needs no countersign (`76302e7`, CC 4.4.3.12 *One officer*).
- **Residual.** Two officer keys of one person that no self roster links count as two officers.
- **AUTHORITY.**
  - Derived. The coordinator ruled the countersign is a voice, and the kernel's model reads the outside voice from the act row's own cosigners.
  - The one-officer rule is the coordinator's, told to the steward, and his to overturn (C-04).
- **HOME.** CC 4.4.3.12 *The floors bind power over members, not the count of voices (normative)*. REPLACES: "A countersign row by an eligible outside key that names the act completes it. The acting officer's withdrawal of the act clears it. A withdrawal concurrent with the countersign follows [CC 2.7.7](part_2_the_grammar.md#2.7.7) rule 4." Add the residual to *One officer (normative)* after "Counts are over persons: two officer keys of one person are one officer."
- **DRAFT.**
  - "The countersign is a voice on the act's own row: a further statement over its payload by an eligible outside key, counted with the officer's (`affiliation_member_action`, two of two)."
  - "Whether a key is outside the officers is read in the act's own past. The officer's withdrawal of the act retires it from its head on, as any end does."
  - Residual: "Two officer keys of one person that no self roster links are read as two officers."
- **TABLES.**
  - No quote found for the replaced sentences.
  - `constitution/governance_policy.tsv` `affiliation_member_action` already lists its voices on "cosign".
  - The `takedown-notice` comment in `manifests/family_payloads_v2.cddl` ("counted where an affiliation has one deciding seat") is consistent.
- **NAMES.** None.
- **CHECKED BY.** The kernel's countersign cases (native). Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-13 and C-04.
  - CC 4.5.13 "An affiliation names it only under the one-voice countersign rule of [CC 4.4.3.12]" is consistent.

### A-21 Licences and trust edges: the term, the reader's anchor, and edges signed before a lock

- **RULE.**
  - **The term.** A licence's term is its holder's word.
  - **The reader's anchor.** A reader honours a licence under an ended term only where it is anchored: the reader held it then, or held then a row of a key in its trust set that names it. That is the caller's duty, and it carries a residual.
  - **Already in the tree.** A locked community issues no licence, signs no onward acceptance edge and confers no `license` seat, `licensure_authority_locked` (CC 2.4.1.3). A `license` seat conferred before the lock keeps issuing until its term ends.
  - **Owed.** An onward acceptance edge signed before the lock runs to its term, at most 365 days.
  - **Owed.** A licence ends by ancestry and never retroactively.
- **AUTHORITY.** Derived (the trust-walk readings of 2026-11-27).
- **HOME.**
  - CC 4.5.4: add the term and anchor sentences after the paragraph *The authority set*, as the record asks ("write in CC 4.5.4").
  - CC 2.4.1.3 *What the fold keys on*: add the edge sentence after "A `license` seat conferred before the lock keeps issuing until its term ends or a seated duty holder's count withdraws it."
- **DRAFT.**
  - "A licence's term is its holder's word. A reader honours a licence whose term has ended only where it held the licence before then, or held then a trusted key's row that names it."
  - "A reader that holds no such anchor honours nothing under an ended term."
  - "An onward acceptance edge signed before the lock runs to its term, never more than 365 days."
- **TABLES.** No quote found for "A `license` seat conferred before the lock keeps issuing until its term ends". Add new `rule_entries.tsv` rows.
- **NAMES.** None.
- **CHECKED BY.** The kernel's trust-walk cases (built from rows). Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - The record conflicts with itself here. This ruling's second anchor ("a trusted key's row held then") predates the later finding, for retired suites and key ends, that a row by a trusted key built on an old row anchors nothing. A-23 and A-15 take only the reader's own earlier holding and explicit re-attestation.
  - Before writing, the coordinator decides whether the licence anchor keeps its second arm. Write the first sentence's second arm only if confirmed. Otherwise end it at "held the licence before then".

### A-22 The consent peer set

- **RULE.** **Not recoverable from the notes.** What is known:
  - The kernel's 0.5.1 list names "the consent peer set" as a MUST, and the attestation-plane fan-out of the transport depends on it.
  - The text was given to the kernel.
  - The headings of the rule are: who may end a grant; no revival; the fold being causal-first; class matching; and the payload.
  - The text's present rule is CC 3.3.7 (`consent:replication`): a directed node-to-peer grant, ended by its granter's `withdraws` or `recants`, narrowed only by `supersedes`, ratified bilaterally only while both grants are live.
- **AUTHORITY.** Not recoverable.
- **HOME.** CC 3.3.7 `consent:replication`.
- **DRAFT.** None. Do not write a sentence until the coordinator supplies the final rule.
- **TABLES.** None.
- **NAMES.** None.
- **CHECKED BY.** The kernel's 0.5.1 tag (not 0.5.0).
- **DEPENDS ON / CONFLICTS.** It waits for the later tag.

### A-23 Adding and retiring a signature suite

- **RULE.**
  - **Suites in force.** The suites in force are a charter member of the genesis bundle.
  - **Add and retire by amendment.** A suite is added or retired by an ordinary amendment: a later bundle counted by a strict majority of the predecessor's live holders.
  - **An add is additive.** A row under a suite the reader does not know waits.
  - **A retire is an end.** An old-suite row counts for a reader only where it is in the past of one of these:
    - (a) the retiring bundle;
    - (b) the reader's own earlier acknowledgement;
    - (c) an explicit re-attestation ("I held this row before the retirement"), by the same issuer under a suite in force, or by a key in the reader's trust set.
    An ordinary citation anchors nothing. The transitive past of the retiring bundle, or of rows the reader took up, carries everything it names with no vouching.
  - **A composite after a retirement.** A composite of A and B counts after A retires only while B is in force.
  - **Order.** An add comes before a retire, so that two suites on different assumptions stay in force. Rotate before a retirement.
  - **No third suite yet.** No third suite is named until one in force is under real pressure.
  - **Residual.** Where both suites fall, the mesh is founded again by ceremony.
- **AUTHORITY.**
  - The steward, direct: "we dont add more until one is under real pressure, so that the next can be selected from the SOTA in context"; "I think of it as antibiotic resistance analogically, and yes we need the process of adding/removing algos clear and modeled in 1.0 in anticipation of rapid algorithmic churn"; "once a handful of rows referencing a past row are migrated, the old row can be reconstructed from the consequences it engendered alone, just like reality".
  - The rules are derived, with the kernel's corrections: a per-reader anchor, and explicit re-attestation only.
  - The kernel models it after the tag. This entry waits for that model, not only for the tag.
- **HOME.**
  - CC 2.6.1.7 *The composite signature and keys (normative)*: add a new paragraph *Suites in force* at the end.
  - The charter member: CC 2.6.1.11 *What a bundle carries and names* (`charter` carries the accord's parameters).
- **DRAFT.**
  - "*Suites in force.* The signature suites in force are a member of the charter of the bundle in force. A later bundle adds or retires one, counted as any later bundle is ([CC 2.6.1.11](#2.6.1.11))."
  - "A row under a suite the reader does not know waits."
  - "A row under a retired suite counts for a reader only where the retiring bundle, the reader's own earlier acknowledgement, or an explicit re-attestation has it in its past."
  - "A re-attestation is signed under a suite in force by the row's own issuer, or by a key in the reader's trust set. A citation alone anchors nothing."
  - "A composite signature counts after one of its suites retires only while the other is in force."
  - "A suite is added before another is retired, so two suites on different assumptions stay in force. A key rotates before its suite retires."
  - "Where every suite in force falls, the mesh is founded again by ceremony."
- **TABLES.**
  - `constitution/signed_object_v2.tsv` and `manifests/signed_object_v2.cddl` `genesis-charter`: a new member (see NAMES).
  - It is a genesis-bundle schema change, so it reaches the IETF draft at -05 (D-01).
  - The minted genesis record is unchanged. The member is absent from it, and absent must read as the one composite suite in force. State that reading in the member row.
- **NAMES.** The charter member's name and type are **not recoverable from the notes**. The kernel asked for a `suites()` accessor on its row view; that is not a wire name. The coordinator names it.
- **CHECKED BY.** The kernel's model of suite churn, built after the tag. Cite it when vendored.
- **DEPENDS ON / CONFLICTS.** A-15 uses the same anchor for a key's own revocation: an honest revocation names the key's last trusted rows.

### A-24 Room keys: a second seat row, the end of a stay, a batch admission

- **RULE.**
  - **Already in the tree.**
    - A node's row in a private room, with its door order and its two refusal names (`1bd3c2f`, CC 3.1.3.2 *A node's row in a private room*, *The room's door on a row*).
    - A room key whose seat has ended is not seated again (CC 3.1.3.2, `membership_room_key_ended`).
    - Privacy is fixed at founding (CC 3.1.3.2).
  - **Owed (K1).** A second seat row of a seated room key is a second basis for one seat. The key is one voice, and the row is no refusal.
  - **Owed (K2).** An end is of the key's stay in the room: one resignation or counted removal ends every seat of that key there, and in a private room for good. A seating concurrent with the key's own end does not keep it in.
  - **Owed (R-a).** A batch admission that names one barred key is refused whole.
  - **Stays open (K3).** Two keys of one person are the caller's to collapse, since the binding is never a row.
- **AUTHORITY.** Derived (room-key readings, told to the steward). Room-key finality including resignation is the steward's: "3A and agreed" on the derivations.
- **HOME.** CC 3.1.3.2 *A room key is not seated again (normative)*. Add after "This holds of every end of the seat, a resignation included."
- **DRAFT.**
  - "A second seat row of a seated room key is a second basis for the same seat. The key is one voice, and the row is no refusal."
  - "One resignation or counted removal of a room key ends every seat of that key in the room. A seating concurrent with the key's own end does not keep it in."
  - "An admission that names several keys, one of them barred here, is refused whole."
- **TABLES.**
  - Ledger (register lane): the open row "A second seat row of one room key, and two admissions at once" closes for its first half. The two-admissions half stays open (K3).
  - The batch refusal's name is **not ruled**. If one is used, it needs a review-table row, and the name comes from the coordinator.
- **NAMES.** See TABLES.
- **CHECKED BY.** The kernel's room-key cases (the `room-key-vectors` set, 30 cases at its last count). Cite them when vendored.
- **DEPENDS ON / CONFLICTS.** CC 3.1.3.2 *A seat is one stay* is consistent.

### A-25 A lone duty holder with an offer standing

- **RULE.**
  - A lone duty holder with an offer of any duty seat standing confers no other seat alone, until that offer is accepted or withdrawn.
  - Two new holders at once are one row that names both.
- **AUTHORITY.** Derived (the lone test of the head rules).
- **HOME.** CC 4.5.4 *The authority set*. Add after "A lone holder's conferral made while two or more hold the duty concludes nothing, `duty_conferral_counted_required`."
- **DRAFT.**
  - "A lone duty holder with an offer of a duty seat standing confers no other alone until that offer is accepted or withdrawn. Two new holders at once are one row naming both."
- **TABLES.** Add a new row in `rule_entries.tsv`. No refusal name is ruled for the second lone offer: it concludes nothing under `duty_conferral_counted_required` only if the coordinator confirms that reading.
- **NAMES.** None.
- **CHECKED BY.** The kernel's duty-seat cases. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.** A-07 (c) is the window for concurrent lone conferrals.

### A-26 Receipts of counts

- **RULE.** Partly recoverable.
  - A count's receipt has no row of its own; it is a fixed rule.
  - A body's counted receipt of a lone removal is counted over the room less the remover, in its base and in its voices.
  - A counted receipt may be read at the head of the act it names or later. That is ruled, but its wire form is not: wire-map N10 says either `act-ack` admits `refs.head` on a body's counted receipt, or the later head is named another way.
  - The record names "receipts with no cascade first" and "no cascade through an ordered pair" as rules for the tag. Their sentences are **not recoverable** from the notes.
- **AUTHORITY.** Derived.
- **HOME.** CC 2.7.5 *settled, and receipts*.
- **DRAFT.**
  - "A body's counted receipt of a lone removal is counted over the room less the remover, in its base and in its voices."
  - Write nothing for the later head or the cascade until the coordinator gives the wire form.
- **TABLES.**
  - `constitution/signed_object_v2.tsv` `receipt` rows ("A receipt names no head") change only if `refs.head` is admitted.
  - CC 2.7.5 "A receipt … names no head" gains the exception then.
- **NAMES.** Not recoverable.
- **CHECKED BY.** The kernel's receipt cases (in the tag the implementers pin). Cite them when vendored.
- **DEPENDS ON / CONFLICTS.** A-01.

### A-27 Infrastructure: the founders' amendment keeps the word up to `N`

- **RULE.**
  - **Seating.** A founder seat of an `infrastructure` community is added only by a founders' amendment or by the recovery widening while stalled.
  - **The founders' amendment.** It is a record version that seats the key, is signed by it, and is counted at the present `M`. It keeps the word `quorum:M/N` unchanged while the founders it leaves number no more than `N`: a refill under the same `M`. For example, under 5/9, six founders seat a seventh.
  - **A new word.** Only a version that leaves more than `N` founders names a new word: `N` the founder count after it, `M` its strict majority, never below the present `M`.
  - **No downward word.** No version restates the word downward. `M` is never lowered.
  - **After a removal or resignation.** The word's `N` is documentary.
  - **Live.** The room is live while the active founders number at least `M` + 1.
  - **Two amendments.** Concurrent founders' amendments wait: the founders common to them count until a version names both.
  - **Plain widening.** A plain founder widening concludes nothing.
- **AUTHORITY.** Derived, from CC 3.1.3.2 and CC 3.2 read whole. It closes a hole: founders admitted while `M` stays fixed would make `M` a minority.
- **HOME.**
  - CC 3.2 *Canonical `cohort_subkind: infrastructure`*, the bullet at line 1032. REPLACES: "`N` is the founder count and `M` is its strict majority, ⌊N/2⌋+1, as for the accord ([CC 4.2.6](part_4_composition_governance.md#4.2.6))."
  - CC 4.4.3.18. REPLACES: "In an `infrastructure` community `N` is the founder count and `M` is ⌊N/2⌋ + 1 ([CC 3.2](part_3_the_namespace.md#3.2))."
- **DRAFT.**
  - CC 3.2:
    - "`N` is the founder count when the word is stated, and `M` its strict majority, ⌊N/2⌋+1, as for the accord ([CC 4.2.6](part_4_composition_governance.md#4.2.6))."
    - "A founders' amendment seats founders under the same word while the founders it leaves number no more than `N`."
    - "Only a version that leaves more than `N` founders states a new word, with `M` its strict majority and never below the present `M`. No version restates the word downward."
    - "Two concurrent founders' amendments wait: the founders common to them count until a version names both."
  - CC 4.4.3.18:
    - "In an `infrastructure` community `N` is the founder count when the word is stated and `M` is ⌊N/2⌋ + 1, and a founders' amendment keeps that word ([CC 3.2](part_3_the_namespace.md#3.2))."
- **TABLES.** Grep `rule_entries.tsv` for "`N` is the founder count", and update any quote. The acts table header already states the amendment, and its `admit founder infrastructure` row is removed.
- **NAMES.** None.
- **CHECKED BY.** The kernel's infrastructure cases, the roster kind `infrastructure`. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-06 (a merge in infrastructure).
  - CC 3.2 line 1032 "A record naming any other `M`, such as `quorum:2/5` or `quorum:3/3`, is refused at founding and at a `supersedes`" is consistent: the word's `M` is always the strict majority of its own `N`.

### A-28 A family's founders

- **RULE.**
  - **The kind.** A family's kind is its record's group kind. It is keyless.
  - **Founders.** Its founders are the members seated with `role: founder`. A later admission or a promotion may carry the role, always with that person's acceptance. A demotion is counted as a removal.
  - **Under `founder_only`.** One active founder admits, with the joiner's consent. It also removes a member other than itself, changes the record, and dissolves the family.
  - **No floor and no duty seats.** A family has no floor of two voices, and no duty seats or moderators (`duty_holders_on_family` exists).
  - **No last founder.** No rule keeps a last founder. A `founder_only` family with no founder admits nobody. Its members leave, and it dissolves with the last of them.
  - **Leaving.** A member leaves a family only by `membership:resignation`.
  - **Entrenchment.** Entrenchment covers the `consensus_protocol` field. The coordinator reads it as covering the entrenchment flag too.
- **AUTHORITY.** Derived, from CC 3.3.4, CC 3.1.3.2 and CC 4.5.12.5, and given to the kernel for the family kind.
- **HOME.** CC 3.3.4.
  - The `founder_only` row of the protocol table. REPLACES: "a founder **active at the instant of the act** ([CC 3.1.3.2](#3.1.3.2))".
  - A new paragraph after the MemberRole table, headed *A family's founders*.
- **DRAFT.**
  - `founder_only` row: "a founder seated at the heads the act names ([CC 3.1.3.2](#3.1.3.2))".
  - *A family's founders*:
    - "A family's founders are its members seated with `role: founder`. A later admission or a promotion MAY carry the role, with that person's acceptance; a demotion is counted as a removal."
    - "Under `founder_only` one active founder admits, with the joiner's consent, removes a member other than itself, changes the record and dissolves the family."
    - "A family has no floor of two voices and no duty seat. No rule keeps its last founder: a `founder_only` family with none admits nobody, and dissolves with its last member."
    - "A member leaves a family only by its own `membership:resignation`."
    - "Entrenchment holds the `consensus_protocol` field and the entrenchment flag."
- **TABLES.** Grep `rule_entries.tsv` and `protocol_admissibility.tsv` for "active at the instant of the act", and update any quote. The acts table already has family rows (`dissolve` rows).
- **NAMES.** None.
- **CHECKED BY.** The kernel's family-kind cases. Cite them when vendored.
- **DEPENDS ON / CONFLICTS.**
  - A-01.
  - The worked example in CC 3.3.4 ("Bob's signature as an active founder satisfies the protocol") is consistent.

---

## 2. Group B: edits that do not wait

These are schema rules, payload rules, contradictions inside the text, and cells the tables leave unstated. Each follows from a stated rule or a coordinator ruling, and none needs the kernel tag.

### B-01 `cohort_scope` is required only where a family is placed by its own row

- **RULE.**
  - `cohort_scope` is required on a row whose family is placed by the row itself. A family placed by another row carries none, and takes its placement from that row: a window row, a revocation, a receipt, a custody report, a duty, an ownership row.
  - An *addressed* row is one whose signed `for_key_id` names its recipient. An absent `cohort_scope` does not make a row addressed.
- **AUTHORITY.** Derived (wire-map G3, ruled to the kernel 2026-11-28). The text already says what "addressed" means (CC 6.1.9).
- **HOME.** CC 2.1, the `cohort_scope` row of the envelope table (line 24). REPLACES: "REQUIRED, with no wire default."
- **DRAFT.** "REQUIRED, with no wire default, on a row its family places by the row's own scope. A family that another row places carries none, and takes that row's placement ([CC 3.1](part_3_the_namespace.md#3.1), the family model)."
- **TABLES.**
  - Part 8 member table (line 4019) reads "REQUIRED" for `cohort_scope`. If it is generated, the cascade regenerates it. If not, the register lane edits it.
  - No quote found for "REQUIRED, with no wire default".
- **NAMES.** None.
- **CHECKED BY.** The family model's placement column; the kernel's audience table reads it.
- **DEPENDS ON / CONFLICTS.** B-42 (placements).

### B-02 `attached_head_digest` has one type: the bundle's object id

- **RULE.**
  - `attached_head_digest` is the object id of the bundle in force that the acceptance edge attaches on, a `hash-digest`.
  - It is the one member outside `refs` that names a signed object, and a holder adds it to the named set.
- **AUTHORITY.** Derived. Wire-map M2, as corrected on re-verification: three typings to reconcile.
- **HOME.**
  - CC 2.1 row `attached_head_digest` (line 59). REPLACES: "The SHA-256, a byte string ([CC 2.6.1.2](#2.6.1.2)), of the lineage head the acceptance edge attaches on: the signed roster record at that version ([CC 3.2](part_3_the_namespace.md#3.2) T4a)."
  - CC 2.6.1.3 *What a row names*. Add after "A holder reads the named set from `refs` alone, without knowing the family."
- **DRAFT.**
  - CC 2.1: "The object id of the bundle in force the acceptance edge attaches on, a `hash-digest` ([CC 2.6.1.11](#2.6.1.11), [CC 3.2](part_3_the_namespace.md#3.2) T4a)."
  - CC 2.6.1.3: "`attached_head_digest` is the one member outside `refs` that names a signed object, and a holder adds it to the named set."
- **TABLES.**
  - Part 8 member table line 3929 types it `hex64`. It becomes `hash-digest` (the register lane, unless generated).
  - Part 8 line 3793 is consistent.
  - The CDDL `trust-accepts` member is already `hash-digest`, so no CDDL change.
- **NAMES.** None.
- **CHECKED BY.** The signed-object build (`tools/build_cc_signed_object_v2.py --check`).
- **DEPENDS ON / CONFLICTS.** CC 3.2 T6 "Its digest is the bundle's object id … `attached_head_digest` names a head by it" is consistent.

### B-03 The `membership:proposal` payload rule, and "role (nullable)"

- **RULE.**
  - A proposal's payload is:
    - `author`;
    - `dimension` (`membership:proposal:v1`);
    - `group_kind`;
    - `group`;
    - an optional `role`, where absent offers no role;
    - `subject_key_ids`, exactly one key;
    - `expires_at`;
    - `refs` with the head (A-01);
    - `asserted_at`.
  - An optional member is unset by absence, never by null.
- **AUTHORITY.** Derived (wire-map M5). The text already says the members, in prose, in CC 3.1.3.2 and CC 2.1.
- **HOME.** CC 3.1.3.2 registry row `membership:{stage}`. REPLACES: "the offered `role` (nullable)".
- **DRAFT.** "the offered `role` (optional; absent offers no role)".
- **TABLES.**
  - `constitution/signed_object_v2.tsv`: add the rule `membership-proposal` (object `membership`) with the members above. Type and `required_when` as in `membership-reply`, `expires_at` as `ms-time` "always; after asserted_at and at most 30 days later". Cite `3.1.3.2 2.1`.
  - `manifests/family_payloads_v2.cddl` gains the rule, by the cascade or the signed-object build.
  - `rule_entries.tsv:360` quotes "the offered `role` (nullable)".
  - CC 2.6.1.4's list of the families whose payloads it states is shorter than its table. Regenerate it from the table if it is generated; otherwise list the families the table holds.
- **NAMES.** Rule name `membership-proposal`.
- **CHECKED BY.** The signed-object build and the shapes check.
- **DEPENDS ON / CONFLICTS.** B-04.

### B-04 The `membership:resignation` payload rule: no target

- **RULE.**
  - A resignation names the member and the heads it acts from, and no target.
  - Its payload is:
    - `author`;
    - `dimension`;
    - `group_kind`;
    - `group`;
    - `member` (equal to the CWT `sub`);
    - `refs.head`, the newest counted heads (A-01);
    - optionally `refs.trusted_through`;
    - `asserted_at`.
  - The kernel's wire map presents a resignation through a bridge until after its tag. The text states a resignation with no target.
- **AUTHORITY.** Derived. Wire-map G9, ruled to the kernel 2026-11-28 ("resignation has no target (amend CC 2.4.1.1)"); the coordinator confirmed the text form.
- **HOME.** CC 2.4.1.1 *An end names the head it acts from*. REPLACES: "A row that ends a standing carries `refs.head` beside its target: a withdrawal of an acceptance or of an offer, an unseating, a resignation."
- **DRAFT.**
  - "A row that ends a standing carries `refs.head`, and beside it the target it ends: a withdrawal of an acceptance or of an offer, and an unseating."
  - "A resignation names the member and no target."
- **TABLES.**
  - `formal/derivation/standing_text.tsv:21` and `:26` quote "a withdrawal of an acceptance or of an offer, an unseating, a resignation".
  - `constitution/signed_object_v2.tsv`: add the rule `membership-resignation`.
- **NAMES.** Rule name `membership-resignation`.
- **CHECKED BY.** The signed-object build. The kernel's resignation cases at the tag.
- **DEPENDS ON / CONFLICTS.** A-01, B-03 and B-05.

### B-05 A withdrawal that lays down one duty carries `scope`

- **RULE.**
  - A founder lays down one duty by a `withdraws` that targets the conferral (the founding record) and carries `scope`, the one duty. It ends only that duty seat. Without `scope` it ends the stay and every duty seat.
  - Rule 0 does not reach a signer's withdrawal of its own voice on a counted record. That withdrawal ends the signer's own seats there, under rule 1, and retires nothing.
- **AUTHORITY.** Derived. Wire-map N2, ruled to the kernel ("lay-down = withdraws targeting the conferral with `scope` = the one duty; amend rule 0"). The text already says the semantics (CC 4.5.4 *What a founding record seats*).
- **HOME.** CC 2.4.1.1, the withdrawal rule table. Add a sentence after the table's row 0, before "**Any one named party is enough.**".
- **DRAFT.**
  - "Rule 0 does not reach a signer's withdrawal of its own voice on `T`: that withdrawal is admitted under rule 1, ends the signer's own seats there, and retires nothing."
  - "A withdrawal that lays down one duty carries `scope`, that duty, and ends only that duty seat ([CC 4.5.4](part_4_composition_governance.md#4.5.4))."
- **TABLES.**
  - `constitution/signed_object_v2.tsv`: a payload rule for a seat's withdrawal (the only `withdraws` shape is `grant-withdrawal`). Add rows: `refs` (the conferral under target, the head under head), `scope` (tstr, "on a withdrawal that lays down one duty; a key of the founding record's `duty_holders`"), `asserted_at`.
  - Grep `rule_entries.tsv` for "A founder resigns one duty by a withdrawal".
- **NAMES.** The member `scope` (tstr) on a seat's `withdraws`. The rule name is the writer's, for example `seat-withdrawal`. Confirm it with the coordinator.
- **CHECKED BY.** The kernel's duty-seat and resignation cases (the lay-down).
- **DEPENDS ON / CONFLICTS.** The CC 4.5.4 founding paragraph is consistent.

### B-06 The `reconsideration:{grounds}` payload rule

- **RULE.**
  - A reconsideration is authored by a `review` holder. It cites exactly the one notice or act it rules on, in `refs.also.cites`, and carries the member `outcome` (`reversed` / `partial` / `upheld`).
  - Only `reversed` ends the act.
  - A reviewer is recused from an act they took, an item they authored or reported, and an act that names them (CC 4.5.4).
- **AUTHORITY.** Derived (wire-map G23, ruled 2026-11-28, confirmed on re-verification).
- **HOME.** CC 3.1.9.2 row `reconsideration:{grounds}`. The prose is A-17's DRAFT. Write that sentence here even before the tag: the role and the member are schema, not kernel rules.
- **DRAFT.** As in A-17, for the CC 3.1.9.2 row.
- **TABLES.**
  - `constitution/signed_object_v2.tsv`: a rule `reconsideration` with `author`, `dimension`, `outcome`, `refs` (the act under also.cites, exactly one) and `asserted_at`.
  - The family model's `reconsideration:{grounds}.body` becomes stated (it reads "none (no family body …)").
  - `rule_entries.tsv:3811`.
- **NAMES.** Member `outcome`, tstr, closed: `reversed` / `partial` / `upheld`.
- **CHECKED BY.** The signed-object build. The kernel's duty-acts cases at the tag.
- **DEPENDS ON / CONFLICTS.** A-17.

### B-07 A quarantine release's payload

- **RULE.**
  - A release is the same holder's `supersedes` of its withhold, naming the withhold in `refs.target`.
  - Only that holder releases. Any other relief is the members' lift.
- **AUTHORITY.** Derived. Wire-map G21, as corrected on re-verification. Part 8's rule entry (`supersede | author`) and the family model's lifecycle ("released supersedes withheld (fold)") already say it.
- **HOME.** CC 3.1.9.2 row `quarantine:{state}`. The DRAFT is A-17's. It may be written now: the rule is in Part 8 already.
- **DRAFT.** As in A-17.
- **TABLES.**
  - `constitution/signed_object_v2.tsv`: a rule for the `quarantine:{state}` payload: `author`, `dimension`, `sub` (the key quarantined), `refs` (on a release, the withhold under target), `asserted_at`.
  - The family model's body becomes stated.
  - `rule_entries.tsv:3801`, `:3802`, `tools/divergence_cases.py:397`.
- **NAMES.** None new. The release's leaf is the registry's own: read it from `manifests/namespace_registry.json` before writing.
- **CHECKED BY.** The signed-object build. The kernel's quarantine cases at the tag.
- **DEPENDS ON / CONFLICTS.** A-17.

### B-08 A lift cites exactly one act; the re-seating row's family

- **RULE.**
  - A lift cites the one act it lifts, in `refs.also.cites`, and the objections that are its voices.
  - A lift that cites no act or two concludes nothing.
- **AUTHORITY.** Derived (wire-map G24, ruled 2026-11-28; the coordinator gave "exactly one").
- **HOME.** CC 4.5.13 *The lift of an agent's removal*, after "It is a re-seating row that cites the removal, names the head the removal names and names the objections that are its voices."
- **DRAFT.**
  - "It cites the removal, and only it, in `refs.also.cites`, and the objections under the same role. A lift that cites no act, or two, concludes nothing."
- **TABLES.**
  - No quote found for "It is a re-seating row that cites the removal".
  - The re-seating row's family is unstated in the text. The acts row `lift | agent | community | moderation_overturn` names no family.
  - Under A-01, "names the head the removal names" becomes "names the newest counted heads in its own past". Make that change with A-18, after the tag.
- **NAMES.** The re-seating row's family is **not recoverable from the notes**. Ask the coordinator. It is probably a `membership:{stage}` leaf, but that is not ruled.
- **CHECKED BY.** The kernel's agent-removal cases.
- **DEPENDS ON / CONFLICTS.** A-17 and A-18.

### B-09 The community record's members: `overseen_by`, `designated_officials`, `licence_classes`, `declared_cohort`

- **RULE.**
  - The community record carries these members, at its top level beside `cohort_subkind`:
    - `declared_cohort`: `community` or `affiliations`;
    - `overseen_by`: one group id;
    - `designated_officials`: a sorted set of key ids;
    - `licence_classes`: a list of `{class, legal_weight}`.
  - A designated official is a member of the affiliation's record, and no scope word marks the official's edge.
- **AUTHORITY.** Derived (wire-map G19, ruled 2026-11-28: "overseen_by (one group id) + designated_officials (sorted set of key ids) in the record payload beside consensus_protocol"). The text already names each member (CC 4.4.3.12).
- **HOME.** CC 4.4.3.12 *The record (normative)*. The sentence "The family model states its schema as data ([CC 3.1](part_3_the_namespace.md#3.1))." becomes true once the rows exist. Keep it, and add the member list.
- **DRAFT.**
  - "Beside `consensus_protocol` it carries `declared_cohort`, `overseen_by`, `designated_officials`, a sorted set of key ids, and `licence_classes`, each class with its `legal_weight`."
- **TABLES.**
  - `constitution/signed_object_v2.tsv`, `group-roster` rule: four rows, each "on a community's record":
    - `declared_cohort` (`"community" / "affiliations"`);
    - `overseen_by` (`group-ref`);
    - `designated_officials` (`[* identity-ref]`, a set);
    - `licence_classes` (`[* {class: tstr, legal_weight: bool}]`).
  - The CDDL `group-roster` is regenerated or edited to match.
  - `rule_entries.tsv:2149` quotes "The family model states its schema as data".
- **NAMES.** The four members, typed as above. `designated_officials` is a set, not a role-to-key map: the ruling says "sorted set of key ids".
- **CHECKED BY.** The signed-object build. The kernel's charter and affiliation cases.
- **DEPENDS ON / CONFLICTS.**
  - B-10.
  - The text calls it a "limb" in CC 4.4.3.12 *C.*: "**`designated_officials`** — named accountable-human roots gating specific operations". That is consistent with a set.

### B-10 A `weighted:{rubric}` record's `weights` and `need`

- **RULE.** A record whose `consensus_protocol` is `weighted:{rubric}` carries, beside it, `weights` (a map from identity reference to a whole number) and `need` (a whole number).
- **AUTHORITY.** Derived (wire-map G20, ruled 2026-11-28). The text already says the values are whole numbers on the record (CC 3.3.4).
- **HOME.** CC 3.3.4 `ConsensusProtocol` table, the `weighted:{rubric}` row. Add: "The weights are the record's `weights` and the threshold its `need`."
- **DRAFT.** "The weights are the record's `weights`, a map from member to whole number, and the threshold is its `need`."
- **TABLES.**
  - `constitution/signed_object_v2.tsv`, `group-roster`: rows `weights` (`{ + identity-ref => uint }`) and `need` (`uint`), "where `consensus_protocol` is `weighted:{rubric}`".
  - `constitution/consensus_protocols.tsv` gives the rule "`weight:{rubric}`". Check that its spelling matches `weighted:{rubric}`.
  - The CC 4.4.3.17 pseudocode line `sum(weight(m) …) >= threshold` becomes `>= need` (B-31).
- **NAMES.** `weights`, `need`.
- **CHECKED BY.** The signed-object build.
- **DEPENDS ON / CONFLICTS.** B-31.

### B-11 A stalled room's recovery widening names its grant in `refs.also.stands_on`

- **RULE.**
  - The recovery widening names its roster head in `refs.head`, and the counted T7 grant in `refs.also.stands_on`.
  - Its own signature is its acceptance. The bundle is the one the grant names.
  - The grant's room is a token of the grant's `scope` (B-34).
- **AUTHORITY.** Derived. Wire-map N3, ruled to the kernel 2026-11-28: "recovery widening carries refs.also.stands_on = the T7 grant". The wire-map reading had proposed `also.cites`; the ruling is `stands_on`.
- **HOME.** CC 3.2 T7 *Recovery*. Add after "The widening row is signed by the named key itself, and the counted row is its authority."
- **DRAFT.**
  - "The widening names its roster head in `refs.head` and the counted row in `refs.also.stands_on`, exactly one. Its own signature is its acceptance, and the bundle is the one the counted row names."
- **TABLES.**
  - `constitution/signed_object_v2.tsv`, `membership-change` `refs` note: add "on a stalled room's recovery widening, the counted grant under stands_on".
  - Ledger (register lane): the bullet "Some rules the text states have no form in the rule tables, among them … a stalled roster's recovery widening" loses that item once Part 8's rule entry gains the form.
- **NAMES.** None new. `stands_on` is registered (CC 2.6.1.3).
- **CHECKED BY.** The signed-object build.
- **DEPENDS ON / CONFLICTS.** CC 2.6.1.3 `stands_on` ("names the one acceptance a row signed under a root grant stands on"): here the widening is itself the acceptance and names the grant. Extend the `stands_on` sentence: "…, and on a stalled room's recovery widening the grant the widening accepts."

### B-12 The acceptance of a grant cites its owner-binding: the schema note

- **RULE.** On the reply to a grant, `refs` names the grant under `answers` and the owner-binding it is made under in `also.cites`, exactly one. The text already says this (CC 3.1.2.1 *The owner's acceptance*: "It names in `refs.also.cites` the owner-binding it is made under: exactly one row, live, and placed at `federation` as the acceptance is"). The refusal is `acceptance_other_binding`.
- **AUTHORITY.** Text already says (CC 3.1.2.1). The landing commit is `d05d0a4`. The schema note is owed.
- **HOME.** No Part change.
- **DRAFT.** None for the Parts.
- **TABLES.**
  - `constitution/signed_object_v2.tsv:181` (`membership-reply` `refs`). REPLACES its note "The one row answered, under answers: the proposal, or the grant. A reply names no head and no target. One that carries proposal_hash is refused." with "The one row answered, under answers: the proposal, or the grant; on the reply to a grant, the owner-binding it is made under, under also.cites, exactly one. A reply names no head and no target. One that carries proposal_hash is refused."
  - `manifests/family_payloads_v2.cddl` line 71, comment "It names the one row it answers in refs.answers, and no head and no target": same addition.
- **NAMES.** None.
- **CHECKED BY.** The signed-object build. The verifier's acceptance vectors.
- **DEPENDS ON / CONFLICTS.** None.

### B-13 Ballot rows by reference, not digest; the section cite

- **RULE.**
  - The election's rows name rows by reference in `refs`, never by digest. Every row a row names stands in `refs` (CC 2.6.1.3).
  - The seating cites each ballot, withdrawal and decline it counts.
  - The ballot and seating rows are in CC 3.1.3, not CC 3.1.4.
  - Part 8's rule entry for `ballot:moderator_acceptance` already reads the counted set from `refs`.
- **AUTHORITY.** Derived (wire-map M3, ruled 2026-11-28: "election id = id row's row id as a ref; a seating cites each ballot it counts (no digests)"). Under A-11 the id row is the opening.
- **HOME.**
  - CC 3.1.3 rows `ballot:moderator` and `ballot:moderator_acceptance`, and CC 4.5.13 *One result on every node*.
  - The prose rewrite waits for A-11, but the cite fix does not. In CC 4.5.13 *The floor in a small room*, REPLACES "the rows of [CC 3.1.4](part_3_the_namespace.md#3.1.4)" with "rows of [CC 3.1.3](part_3_the_namespace.md#3.1.3)".
- **DRAFT.**
  - Write now: the cite fix.
  - The rest is A-11's DRAFT. Until A-11 lands, the digest sentences stand, since the opening row is part of the tag's rules.
- **TABLES.**
  - `rule_entries.tsv:1397` quotes "The ballot and the acceptance are the rows of".
  - `constitution/signed_object_v2.tsv`: rules `ballot-moderator` (`community_id`, `ranks` (B-15), `refs` naming the opening, `asserted_at`) and `ballot-moderator-acceptance` (`community_id`, `refs` naming the opening and citing each counted row, `asserted_at`). Write them with A-11.
  - The family model's `ballot:moderator.body` has `ranks` typed "unstated" and `ballot:moderator_acceptance.body` is null; both become stated.
- **NAMES.** See A-11: the opening's role is not recoverable.
- **CHECKED BY.** The kernel's election cases.
- **DEPENDS ON / CONFLICTS.** A-11 and B-15.

### B-14 An election's decline

- **RULE.**
  - An election's decline is a `membership:decline:v1` row (`membership-reply`), the offered key's own row, with `refs.answers`.
  - The record says it answers "the seating row". Which row that is, when the seating is the winner's own acceptance (A-11), is **not recoverable from the notes**.
- **AUTHORITY.** Derived (wire-map N1, as corrected on re-verification: the leaf `membership:decline:v1` and the rule `membership-reply` exist).
- **HOME.** CC 4.5.13 *The moderator election*, the decline sentence ("A decline is the winner's own signed row, and it stands for that election").
- **DRAFT.** "A decline is the winner's own `membership:decline:v1` row ([CC 3.1.3.2](part_3_the_namespace.md#3.1.3.2)), and it stands for that election." Add the row it answers once the coordinator names it.
- **TABLES.**
  - `constitution/signed_object_v2.tsv:177` (`membership-reply` `dimension`) and `:181` (`refs`): add "on an election's decline, the row it answers under answers".
  - The `group_kind` and `group` rows apply "where the reply answers a membership proposal". Check whether an election decline carries `community_id` instead.
- **NAMES.** None new.
- **CHECKED BY.** The kernel's decline case.
- **DEPENDS ON / CONFLICTS.** A-11.

### B-15 `ranks` is a sequence

- **RULE.**
  - `ranks` is a sequence of member keys, best first, at most the declared number (three in an election).
  - A ballot that ranks more is void, and counts for nothing.
- **AUTHORITY.** Derived (wire-map M5). The text says "up to three member keys in order".
- **HOME.** CC 2.6.1.2 *Sets and sequences*. REPLACES: "The sequences are the redacted-key arrays of [CC 2.6.1.10](#2.6.1.10), `evidence_refs`, the `chain` of a key record's `attestation_evidence` ([CC 4.2.2.1](part_4_composition_governance.md#4.2.2.1)), and the `aspects[]` of a `transport_destination` ([CC 4.4.3.20](part_4_composition_governance.md#4.4.3.20))."
- **DRAFT.** "The sequences are the redacted-key arrays of [CC 2.6.1.10](#2.6.1.10), `evidence_refs`, the `chain` of a key record's `attestation_evidence` ([CC 4.2.2.1](part_4_composition_governance.md#4.2.2.1)), the `aspects[]` of a `transport_destination` ([CC 4.4.3.20](part_4_composition_governance.md#4.4.3.20)), and a ballot's `ranks` ([CC 4.5.13](part_4_composition_governance.md#4.5.13))."
- **TABLES.**
  - The `ballot-moderator` rule types `ranks` as `[* identity-ref]`, declared a sequence.
  - Do not bound it at 3 in CDDL. A ballot over three is void by the count's rule, and is not malformed.
  - Grep `rule_entries.tsv` for "The sequences are the".
- **NAMES.** None.
- **CHECKED BY.** The signed-object build.
- **DEPENDS ON / CONFLICTS.** B-13. The source wire-map suggested `[1*3 identity-ref]`. That conflicts with the derived "an over-three ballot is void", and this entry takes the void reading.

### B-16 `proposal` is not an `objection` state

- **RULE.** The states of `objection:{state}` are closed at `assent` and `raised`. A proposal is the proposer's own row in its own family.
- **AUTHORITY.** Text already says (CC 3.1.9.2; the CDDL `objection-vote` "the states are closed at these two").
- **HOME.** CC 4.5.13 *How a family's act is counted*. REPLACES: "Votes travel on `objection:{state}` ([CC 3.1.9.2](part_3_the_namespace.md#3.1.9.2)): `proposal`, `assent`, `raised`."
- **DRAFT.** "Votes travel on `objection:{state}` ([CC 3.1.9.2](part_3_the_namespace.md#3.1.9.2)), `assent` or `raised`, and each names the proposal it answers, which is the proposer's own row in its own family."
- **TABLES.** `rule_entries.tsv:1445` quotes "`proposal`, `assent`, `raised`".
- **NAMES.** None.
- **CHECKED BY.** The text lints.
- **DEPENDS ON / CONFLICTS.** None.

### B-17 The receipt's protected claims, as a schema rule

- **RULE.**
  - A COSE receipt's protected header carries `iat`, the service's instant of issue, as REQUIRED.
  - A receipt without one is refused, `receipt_no_instant`. The text and its token already say this.
  - The schema rule `ceg-receipt` types its protected bytes only as `bstr`.
- **AUTHORITY.** Derived (the receipt `iat` REQUIRED, agreed with the verifier; the token is registered).
- **HOME.** No Part change. CC 2.6.1.11 already says it (`0eb963d`).
- **DRAFT.** None for the Parts.
- **TABLES.**
  - `manifests/signed_object_v2.cddl`, `ceg-receipt` (line 49): type the protected bytes as `bstr .cbor receipt-protected`, with `receipt-protected = { 1: int, 395: any, 15: { 6: uint, * int => any }, * int => any }`. That is `iat` required in the CWT claims, and the rest open as RFC 9942 allows. The writer checks the label numbers against RFC 9942 and RFC 9597 before writing.
  - `constitution/signed_object_v2.tsv`: a row for the receipt's `iat`.
  - It reaches the IETF draft at -05 (D-01).
- **NAMES.** None new.
- **CHECKED BY.** The signed-object build. The verifier's receipt vector.
- **DEPENDS ON / CONFLICTS.** D-01.

### B-18 A revocation snapshot's and a boot manifest's `sub`

- **RULE.**
  - The object claims are closed: `iss`, the edition claim, an optional `iat`, and an optional `sub` (text).
  - `sub` is checked only on a genesis bundle, where it MUST equal the payload's `family_key_id`.
  - A revocation snapshot SHOULD carry `sub`, its author's identity reference.
  - A boot manifest SHOULD carry `sub`, `build:` and its target.
- **AUTHORITY.** Derived (agreed with the verifier).
- **HOME.** CC 2.6.1.11 *Every other signed object*. Add after "A genesis bundle's statement also carries `sub`, which MUST equal the payload's `family_key_id`, and a verifier refuses one whose `sub` differs."
- **DRAFT.** "A revocation snapshot SHOULD carry `sub`, its author's identity reference, and a boot manifest SHOULD carry `sub`, `build:` and its target. A verifier checks `sub` on a genesis bundle only."
- **TABLES.**
  - `manifests/signed_object_v2.cddl` `object-claims` (lines 256–262): the `? 2: tstr` comment becomes "sub: on a genesis bundle the payload's family_key_id; on a snapshot SHOULD be the author's identity reference; on a boot manifest SHOULD be build:<target>".
  - `constitution/signed_object_v2.tsv`: the matching row.
  - The verifier's refusal for a differing genesis `sub` is `statement_sub_not_family`. The text names no token. If the writer names it, it needs a `refusal_tokens_review.tsv` row (kind `refusal`) and, since "statement" is a transparency word, a `manifests/scitt_names.tsv` row.
- **NAMES.** Optional: `statement_sub_not_family` (refusal), the verifier's spelling.
- **CHECKED BY.** The signed-object build and the verifier's vectors.
- **DEPENDS ON / CONFLICTS.** D-01.

### B-19 The `ietf/` schema copy is the published draft's snapshot

- **RULE.** `ietf/signed_object.cddl` is the CDDL as draft -04 published it. The schema of this edition is `manifests/signed_object_v2.cddl`. The copy's header claims otherwise.
- **AUTHORITY.** Derived (wire-map M1; the kernel's map withdrew M1 as a mismatch).
- **HOME.** No Part change. The header of `ietf/signed_object.cddl`, which `tools/build_ietf_draft.py` writes from its template. The writer edits that template.
- **DRAFT.** For the file's header comment: "The CDDL as draft -04 published it, kept as that draft's snapshot. The schema of this edition is `manifests/signed_object_v2.cddl`."
- **TABLES.** `tools/build_ietf_draft.py --check` must pass after the template edit.
- **NAMES.** None.
- **CHECKED BY.** `tools/build_ietf_draft.py --check`.
- **DEPENDS ON / CONFLICTS.** D-01 (`further_prev` reaches the IETF copy at -05).

### B-20 An eviction's `effective_at` and `revoked_at` are documentary

- **RULE.**
  - An eviction ends a key as a key of the self by causal past, never by a stated instant.
  - Its `effective_at` and `revoked_at` are documentary, and no rule reads them.
- **AUTHORITY.** Derived (wire-map G33, ruled 2026-11-28).
- **HOME.** CC 3.3.6.4 *On the wire*. Add at the end of its paragraph.
- **DRAFT.** "An eviction ends the key as a key of the self by causal past ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1)). Its `effective_at` and `revoked_at` are documentary, and no rule reads either."
- **TABLES.**
  - `constitution/signed_object_v2.tsv`, `occurrence-revocation` rows for `effective_at` ("may be later than asserted_at") and `revoked_at`: add "documentary; no rule reads it".
  - Part 8's eviction change rules are unchanged.
- **NAMES.** None.
- **CHECKED BY.** The kernel's key-end cases.
- **DEPENDS ON / CONFLICTS.**
  - A-15.
  - CC 3.2 T7 *The active founder set* reads `effective_at ≤ t`. That is the infrastructure fold's own reading and a separate matter: leave it, and list it for the next model pass.

### B-21 How a following family names the row it follows

- **RULE.**
  - A family placed by the row it follows names that row by the family's existing `refs` role where it has one, else in `refs.also.cites`, exactly one row of the right kind.
  - An ownership row names the owner-binding it mirrors. A duty row names the permission it attaches to.
  - A custody report names its blob by digest, and a stream head names its stream by `sub`, as each already does.
- **AUTHORITY.** Derived (wire-map G34, ruled 2026-11-28). Part 8's `ownership` guard (`one ownership:… @named[id=ref:target,…]`) uses `target` today, so for `ownership` the family's existing role is `refs.target`.
- **HOME.**
  - CC 3.1.1 `ownership:…` row: add after "An ownership row is placed where the owner-binding it mirrors is placed."
  - CC 3.1.9 `duty:{kind}` row: add after "A duty MUST NOT be placed wider than the permission it attaches to".
- **DRAFT.**
  - `ownership`: "It names the owner-binding it mirrors in `refs.target`, exactly one."
  - `duty`: "It names the permission it attaches to in `refs.also.cites`, exactly one row."
- **TABLES.**
  - `constitution/signed_object_v2.tsv`: rows for those two payloads.
  - `manifests/family_model.json` (`follows` cells) regenerates. Tell the kernel the new hash.
- **NAMES.** None new.
- **CHECKED BY.** The family model build. The kernel's audience table reads `follows`.
- **DEPENDS ON / CONFLICTS.** B-42.

### B-22 The `unstated` cells of the policy table

- **RULE.** The cells the text leaves unstated, at the pin, are these (from `manifests/governance_policy.json`):
  - `custodian_replace`: counted `voice` and `counted_at`;
  - `affiliation_member_action`: counted `voice` and `counted_at`;
  - `cosigned_act`: counted `voice`;
  - `poll`: `opener`, `opener_says`, `answer_words`.
  The build caps these counts (`UNSTATED_MAX = 5` counted, `EXPLICIT_UNSTATED_MAX = 6` explicit, in `tools/build_governance_policy.py`), so their number only falls.
- **AUTHORITY.** Derived, cell by cell. Each fill must quote its sentence.
  - `cosigned_act` voice: CC 4.5.13 "One vote per person" and the folding of cosignatures by person (CC 2.6.1.9 "A fold counts the statements by person") give `person`.
  - `affiliation_member_action` voice: CC 4.4.3.12 *One officer* ("Counts are over persons") gives `person`.
  - `affiliation_member_action` counted_at: A-20 ("read in the act's own past") gives `act`, after the tag.
  - `custodian_replace` voice and counted_at: CC 7.5.5 gives a cosigned row of two named parties. Its sentence names no person rule. Read CC 7.5.5 and fill only what it states.
  - `poll`'s three: no row opens a poll (B-40). They stay `unstated`.
- **HOME.** `formal/derivation/policy_text.tsv`, which quotes the sentence for each filled cell. A cell with no row reads `unstated`. No Part change except the generated table.
- **DRAFT.** None for the Parts.
- **TABLES.** `formal/derivation/policy_text.tsv`. Run the cascade: the policy pin moves. Run the mesh story and the adopter files, and tell the kernel and each implementer the new pin.
- **NAMES.** None.
- **CHECKED BY.** `tools/build_governance_policy.py`, and the policy vectors.
- **DEPENDS ON / CONFLICTS.** A-20 and B-40.

### B-23 The `at_window` cell `dropped` is a storage note

- **RULE.**
  - A counted roster row meets no window and is never cancelled by a clock (CC 4.5.13 *The clock of a window*).
  - The `dropped` cell (`community_remove`, `moderator_recall`, `duty_confer`, `duty_withdraw`, `cosigned_act`, `wa_adjudication`) records what a node does with held voices at the hold window's end (CC 3.3.4 *Counting the window*). It is a storage note, never an outcome.
- **AUTHORITY.** Text already says: CC 3.3.4 "At the window's end that node drops the voices it holds for the event, so no change short of its count stays held forever. … A node's expiry decides only what that node keeps."
- **HOME.** CC 4.5.13 *How a family's act is counted*, the `at_window` bullet. Add after "It lands when the voices it carries meet its count, and its proposer's withdrawal clears it."
- **DRAFT.** "Its `at_window` reads `dropped`, which says what a node does with the voices it holds at the hold window's end ([CC 3.3.4](part_3_the_namespace.md#3.3.4)). It is no outcome and decides nothing."
- **TABLES.** `constitution/governance_policy.tsv`: the column definition of `at_window` in `tools/build_governance_policy.py`'s legend, generated into CC 4.5.13. The writer edits the legend source, not the generated block.
- **NAMES.** None.
- **CHECKED BY.** `tools/build_governance_policy.py`.
- **DEPENDS ON / CONFLICTS.** B-43.

### B-24 A moderator's ballot resolves a moderation proposal

- **RULE.**
  - A moderator resolves a moderation proposal by a `ballot:moderation_action` row: `for` lands it, `against` refuses it. It counts at role `moderate`, 1.
  - The duty row that carries the action out is a separate row.
  - Two moderators' concurrent contrary ballots are contested, and the window runs on to the members' count.
- **AUTHORITY.** Ruled by the kernel, on the coordinator's reading.
- **HOME.** CC 4.5.13, *The mechanism*, item 1 (*A moderator acts unilaterally*). Add after "The community's **moderator** (the required `moderate`-duty holder, [CC 4.5.4](part_4_composition_governance.md#4.5.4)) resolves the action by a **single signature**, at any point in the window."
- **DRAFT.**
  - "That signature is the moderator's `ballot:moderation_action` row: `for` lands the proposal and `against` refuses it. The duty row that carries out the action is a separate row."
  - "Two moderators' contrary ballots, concurrent, are contested, and the window runs on to the members' count."
- **TABLES.** Policy row `moderation_action` ("role:moderate at 1") is consistent. Grep `rule_entries.tsv` for "resolves the action by a **single signature**".
- **NAMES.** None new.
- **CHECKED BY.** The kernel's window cases (the moderation fallback).
- **DEPENDS ON / CONFLICTS.** None.

### B-25 A call's alert mode, and the missing opening row

- **RULE.**
  - A call's opener states its alert mode on the call's opening row, as a signed member `alert`: `open`, `notify` or `ring`. Absent reads `open`.
  - A receiver may lower the mode and never raise it. The mode is fixed at the opening.
  - Ringing is transient and never a row: member-only, never stored, with closed reasons `declined` or `busy`.
  - **The blocker.** No row opens a call: CC 5.3.3.2 composes calls with "no new wire". The `alert` sentence cannot be written until a carrier for the call-opening row is decided (C-12).
- **AUTHORITY.** The steward answered the questions directly to an implementer; the record asked for his words and does not hold them. The reading given to the transport is provisional.
- **HOME.** CC 5.3.3.2, after the composition map, once C-12 is answered.
- **DRAFT.** Not written until C-12 is answered. Candidate, after it:
  - "A call's opening row MAY carry `alert`: `open`, `notify` or `ring`, `open` where absent. A receiver lowers it and never raises it, and it is fixed at the opening."
  - "Ringing is transient: it reaches members only, is never stored, and ends `declined` or `busy`."
- **TABLES.** Pending C-12.
- **NAMES.** Member `alert`, pending C-12.
- **CHECKED BY.** None yet.
- **DEPENDS ON / CONFLICTS.** C-12. CC 5.3.3.2 "**Zero new structural primitives**" and the composition map's "(all generic — no new wire)" are the sentences a carrier must answer.

### B-26 The pacing block's open terms, and a publisher's backward clock step

- **RULE.** **Not fully recoverable from the notes.**
  - The pacing block (CC 5.3.3.2 *Pacing under a queued uplink*) leaves two terms open: "stale" has no stated bound, and "a tenth of the rate" does not say whose rate.
  - The record has an 800 ms figure from the transport's measurement. Whether it is a named constant or sits in the signed binding is an open question. The age floor is per stream and epoch, confirmed by a second chunk; that is already in.
  - On a publisher's clock stepping back and staying back, the record says the stream reads stale until the epoch rolls, and raises (without ruling) whether the publisher restates its binding.
  - No sentence can be written from the record for any of these.
- **AUTHORITY.** Open: owed by the coordinator.
- **HOME.** CC 5.3.3.2 *Pacing under a queued uplink*, second paragraph.
- **DRAFT.** None. Candidate shape, for the coordinator to confirm: "A media chunk is stale where its age less its stream's floor exceeds `<named constant>`. The rate is the node's own uplink rate."
- **TABLES.** `constitution/constants.tsv` gains the constant if it is named.
- **NAMES.** Possibly a constant. Not ruled.
- **CHECKED BY.** The transport's pacing model (the open ledger row "Pacing beyond the bounded model").
- **DEPENDS ON / CONFLICTS.** C-15 and D-06.

### B-27 One-target removal in the CC 4.4.3.17 pseudocode

- **RULE.** As in B-31. This id is kept only so that the numbering stays stable.
- **AUTHORITY.** As in B-31.
- **HOME.** As in B-31.
- **DRAFT.** As in B-31.
- **TABLES.** As in B-31.
- **NAMES.** None.
- **CHECKED BY.** As in B-31.
- **DEPENDS ON / CONFLICTS.** It is B-31.

### B-28 The mesh configuration rules: DONE-IN-TREE

- **RULE.**
  - A `mesh_config:{key}` row's members are stated. Its keys, ranges, owner defaults and directions are data.
  - A value stands only where it lets no more flow than the owner's default. An emergency ends at its `valid_until`, and no ceiling reads zero.
  - The live keys are the six a consumer reads: the anti-entropy round cadence, the page limit, the trace-replication pause, the A/V pause, the background-task ceiling and the summary-only switch.
- **AUTHORITY.** Derived, landed.
- **HOME.** CC 4.2.1, CC 3.1.9.2 row `mesh_config:{key}`, CC 6.1.5.1 *The mesh-config loop*, and `constitution/mesh_config_keys.tsv`. Landed in `72dfade`, `c9988f8`, `9082e73`.
- **DRAFT.** None owed.
- **TABLES.** None owed. `onion.cap_factor`'s `max` reads `unstated`; that is the text's own gap (no consumer).
- **NAMES.** None.
- **CHECKED BY.** `tools/check_mesh_config_keys.py`.
- **DEPENDS ON / CONFLICTS.** The ranges for `redundancy.*` and `antientropy.*`, and whether the transport reads them, were asked of the transport and not answered. The table stands as data.

### B-29 The roster merge's "open on the wire" note

- **RULE.** Restate the note once A-06 lands. Until then it is true.
- **AUTHORITY.** Follows A-06.
- **HOME.** `formal/derivation/family_shapes.tsv:108` (`group:roster`): "a version naming several heads is open on the wire".
- **DRAFT.** With A-06: "a merge names its tips in head and further_heads and states the whole roster (CC 2.7.8)".
- **TABLES.** The cascade regenerates the family model.
- **NAMES.** None.
- **CHECKED BY.** The family model build.
- **DEPENDS ON / CONFLICTS.** A-06.

### B-30 Public rooms: gate the vouching and flood models; the mesh model's admission

- **RULE.**
  - Open admission is cut from this edition. The steward, direct: "yes, cut open:self_admit for 1.0".
  - The models in the formal tree must match. The vouching model and the flood models of public rooms, built on a working branch, become gated models registered in the formal counts.
  - The mesh model's public-room join (`JoinPub` in `formal/mesh_net/MeshNet.tla`) still models open admission, and is changed to invitation.
  - The register's evidence row for the one-voice room (`CLM-one-voice-room`) names a function of the cut open path. That row's evidence is re-pinned or marked.
- **AUTHORITY.** The steward, direct, on the cut. The rest is derived.
- **HOME.**
  - No Part sentence.
  - `formal/` and `constitution/claims.tsv` (the claim's evidence column), and `formal/derivation/models_vs_text.tsv` for the mesh model's row.
- **DRAFT.** None for the Parts.
- **TABLES.**
  - `constitution/claims.tsv` (`CLM-one-voice-room` evidence).
  - The formal counts (`tools/check_formal_counts.py`'s source) gain the two models when they are gated.
  - The mesh model change is a TLC job. It is heavy: run it through the shared job scheduler, never on the side.
- **NAMES.** None.
- **CHECKED BY.** The models themselves, once gated.
- **DEPENDS ON / CONFLICTS.** None in the Parts.

### B-31 The CC 4.4.3.17 pseudocode is stale

- **RULE.** The admission pseudocode must state the text's rules:
  - A removal's target is not counted over and is no voice.
  - The floor is two voices in a community.
  - Counts are over persons.
  - The count is taken at the heads the row names (after A-01, the newest counted heads).
  - A `weighted:{rubric}` row compares against `need`.
  - The roster version is chained by `refs.head`, never `prev_head_digest`.
- **AUTHORITY.** Text already says (CC 3.3.4 one-target removal; CC 4.5.13 the floor of two voices; CC 4.5.13 one vote per person).
- **HOME.** CC 4.4.3.17 *Membership-change admission per consensus_protocol*.
  - The opening sentence. REPLACES: "admitted under the group's quorum and chained by `prev_head_digest`".
  - The `admit_family_change` code block.
- **DRAFT.**
  - Opening sentence: "admitted under the group's quorum and chained by the head it names in `refs.head`".
  - In the code block, after `current = resolve_family(…)`, add:
    - `voters = persons(current) minus target   // a removal's target is not counted over and is no voice (CC 3.3.4)`
  - Then use `voters` in each arm.
  - Add `and count(signers) >= 2   // the floor of two voices in a community (CC 4.5.13)` before `admit = group_ok`.
  - Change `>= threshold` to `>= need`.
- **TABLES.** `rule_entries.tsv:3370` quotes the `majority` line. Update it.
- **NAMES.** None.
- **CHECKED BY.** The text lints. The kernel's removal cases.
- **DEPENDS ON / CONFLICTS.** A-01, A-08 and B-10.

### B-32 The CC 4.4.3.10 cardinality table is shaped by MLS members

- **RULE.** The table describes subscriber crypto as an MLS group's per-epoch cascade. The open subscription of CC 4.4.3.10 *Open subscription* seats nobody, so the table must not read as if every subscriber were an MLS member.
- **AUTHORITY.** Derived. It was listed as a remaining item.
- **HOME.** CC 4.4.3.10, the table *Cardinality unified across observer-share and multicast*, the row "**N>1 (multicast)**".
- **DRAFT.** Add one sentence after the table: "A subscriber to an open publication holds no seat, and receives the epoch key as a recipient of the publisher's `key_grant`, never as a group member ([CC 3.3.2](part_3_the_namespace.md#3.3.2))." Confirm with the coordinator whether delivery to a non-member subscriber is ruled (C-06). If it is not, add nothing, and leave C-06 open.
- **TABLES.** None.
- **NAMES.** None.
- **CHECKED BY.** None.
- **DEPENDS ON / CONFLICTS.** C-06.

### B-33 The remaining mentions of an old component name

- **RULE.** The Parts carry no product names. The component name `NodeCore` appears in Parts 3 and 8: part_3 lines 30, 540, 568, 711 (the heading), 723 and 745, and Part 8. The record counts 17 mentions.
- **AUTHORITY.** Text rule (no product names).
- **HOME.** Each mention.
  - Part 3, line 711, is the heading of CC 3.1.9: "### 3.1.9 `node` — CIRISNodeCore — Credits, Expertise, Decision Hierarchy, Consensus, Governance". Headings and anchors do not change (rule 11), so leave the heading, and report it to the coordinator.
  - Rewrite every body mention to "the node's governance component" or to the section it means.
- **DRAFT.** Per mention. For example, "**Joint claim with [CC 3.1.9.1](#3.1.9.1) NodeCore.**" becomes "**Joint claim with [CC 3.1.9.1](#3.1.9.1).**".
- **TABLES.** Grep every quote table for "NodeCore".
- **NAMES.** None.
- **CHECKED BY.** `tools/check_stale_refs` (or the lint that checks product names).
- **DEPENDS ON / CONFLICTS.** Rule 11 (the heading stays).

### B-34 A root grant's room is a token of the grant's `scope`

- **RULE.** The room that a T7 grant seats in is named as a token of that grant's `scope`, not by `community_id`, which is placement. The token's spelling is the bare group id.
- **AUTHORITY.** Derived. Wire-map G32, ruled 2026-11-28: "root grant's room = a token of grant `scope`". "The bare group id" is the coordinator's to confirm. The record leaves the spelling unstated.
- **HOME.** CC 3.2 T7 *Recovery*, the bullet. REPLACES: "The counted row's `scope` MUST name this room's `community_key_id`, so a key named for one room cannot seat itself in every stalled room under the same root."
- **DRAFT.** "The counted row's `scope` MUST carry this room's group id as one of its tokens, so a key named for one room cannot seat itself in every stalled room under the same root."
- **TABLES.** `rule_entries.tsv:883` quotes "The counted row's `scope` MUST name this room's `community_key_id`".
- **NAMES.** None new (`scope` on `trust-confers`).
- **CHECKED BY.** The kernel's root-grant cases.
- **DEPENDS ON / CONFLICTS.** B-11.

### B-35 Where `sub_delegation` sits

- **RULE.**
  - A charter carries `sub_delegation` in `charter.scope`, once for the charter, not per duty.
  - The steward ruled that the successor bundle's scope carries `sub_delegation`: "yes".
  - Which duties it reaches is still to derive. Whether the grant's own `scope` must also carry it is unstated.
- **AUTHORITY.** The steward, direct (2026-11-25): `sub_delegation` on the successor bundle's scope, yes. The placement is derived (wire-map G29).
- **HOME.** CC 3.4.7 *A chain from a root grant*. REPLACES: "A delegation chain starts from a root grant only where the charter of the bundle the grant names carries `sub_delegation` ([CC 4.5.5](part_4_composition_governance.md#4.5.5))."
- **DRAFT.** "A delegation chain starts from a root grant only where the charter of the bundle the grant names carries `sub_delegation` in its `scope` ([CC 4.5.5](part_4_composition_governance.md#4.5.5))."
- **TABLES.**
  - Grep `rule_entries.tsv` for "starts from a root grant only where".
  - Ledger (register lane): the open row "A root's charter and further delegation" stays open until the successor bundle is minted.
- **NAMES.** None.
- **CHECKED BY.** The kernel's chain cases.
- **DEPENDS ON / CONFLICTS.** Whether a grant must also carry the token is a choice not ruled. Leave it.

### B-36 A window's outcome is its leaf

- **RULE.**
  - A landing's outcome is its leaf: `landed` says that the change lands, and `refused` says every other outcome the table gives at the window.
  - A tally's direction is recomputed from the rows the landing cites.
- **AUTHORITY.** Derived (wire-map N6, ruled 2026-11-28).
- **HOME.** CC 3.1.3 row `window:{state}` (line 210). Add after "A `window:landed` or a `window:refused` row is a landing: it states the window's outcome, and it names its signer's held row and every row it counted."
- **DRAFT.** "`landed` states that the change lands, and `refused` states every other outcome the table gives at the window."
- **TABLES.** The policy table's `landed_means` and `refused_means` cells already say this per row. Check that they match.
- **NAMES.** None.
- **CHECKED BY.** The door model.
- **DEPENDS ON / CONFLICTS.** None.

### B-37 Which key record says a key holds an agent seat

- **RULE.** A key holds an agent seat where its key record covering the admission's instant states `agent`.
- **AUTHORITY.** Derived (wire-map G17). CC 3.2 T7 reads `identity_type` "as read at its seating row".
- **HOME.** CC 4.5.4 *An agent's key*. Add after "An AI agent's key is seated over a room in a scope of its own, `agent`, by an admission the room's persons count."
- **DRAFT.** "A key holds an agent seat where its key record that covers the admission's signed instant states `agent` in `identity_type`."
- **TABLES.** Add a new row in `rule_entries.tsv`.
- **NAMES.** None.
- **CHECKED BY.** The kernel's agent-seat cases.
- **DEPENDS ON / CONFLICTS.** None.

### B-38 The first bind of a new identity: which genesis record

- **RULE.** **Partly recoverable.**
  - The first bind names the genesis key's own record (text), and a key may hold several records (renewals).
  - The wire-map reading proposes naming the self by its fedID (`identity_key_id`) as the object, which needs no choice of record.
  - The coordinator ruled that the self-roster object is the identity. Which record the first bind names, where there are several, is not stated.
- **AUTHORITY.** Derived (wire-map G5; the coordinator's caution to the kernel: "self roster object = the identity").
- **HOME.** CC 3.3.6.4 *The head a self-roster row names*: "The first bind of a new identity names the genesis key's own record."
- **DRAFT.** Candidate: "The self roster's object is the fedID. The first bind of a new identity names in `refs.head` a record of the genesis key that covers its own instant." Confirm with the coordinator before writing.
- **TABLES.** Grep `rule_entries.tsv` for "The first bind of a new identity".
- **NAMES.** None.
- **CHECKED BY.** The kernel's self-roster cases.
- **DEPENDS ON / CONFLICTS.** A-14.

### B-39 Who signed is `iss`; a key's life is `kid` (optional)

- **RULE.**
  - A rule that reads who signed reads `iss`. A rule that reads a key's life, cover or lapse reads `kid`.
  - `iss` is the person of `kid` (step 8).
  - In a private room `iss` is the voice and `kid` the room key, and a node's row has `iss` = `kid`.
- **AUTHORITY.** Text already says (CC 2.6.1.1, CC 2.6.1.7 step 8, CC 2.6.1.11). The sentence is optional (wire-map G1 and G25).
- **HOME.**
  - CC 2.6.1.4 *Logical names*: add one sentence.
  - CC 2.4.1.1, the paragraph that begins "A row lapses when its signer's key has ended".
- **DRAFT.**
  - As in A-13, for CC 2.6.1.4.
  - In CC 2.4.1.1, REPLACES "A row lapses when its signer's key has ended" with "A row lapses when the key that signed it (`kid`) has ended".
  - It needs no tag. Write it now if A-13 waits.
- **TABLES.** Grep the quote tables for "A row lapses when its signer's key has ended".
- **NAMES.** None.
- **CHECKED BY.** The text lints.
- **DEPENDS ON / CONFLICTS.** A-13.

### B-40 No row opens a poll

- **RULE.**
  - A poll states its rule of count in the row that opens it (text), and no family registers a poll's opening row, its `options` or its `ranks_max`.
  - An election's options are the members of the roster it names.
  - The poll's family is **not recoverable from the notes**, and is not ruled.
- **AUTHORITY.** Derived (wire-map N4). The election half is text already, CC 4.5.13 "The **ballot is the roster**".
- **HOME.** CC 4.5.13 *A poll states its own rule (normative)*.
- **DRAFT.** None for the poll until a family is named. The election half is in A-11.
- **TABLES.**
  - Policy row `poll`: its `opener`, `opener_says` and `answer_words` stay `unstated` (B-22).
  - Ledger (register lane): the bullet "which row opens a poll" stays.
- **NAMES.** The opening row's family, and the members `options` (a sequence) and `ranks_max`, are not ruled.
- **CHECKED BY.** None.
- **DEPENDS ON / CONFLICTS.** C-13 (whether a poll is in 1.0's surface).

### B-41 The existence gate against the vacancy rule

- **RULE.**
  - A community locks when no person holds a duty seat over it.
  - An agent's key holding `moderate` keeps no room open: a room whose only duty holder is an agent's key locks.
  - Rule 1's "≥1 member holds the live `moderate` duty" is the sentence out of step.
- **AUTHORITY.** Derived (the election readings: "vacancy = no PERSON holds ANY duty (text's lock wording)").
- **HOME.** CC 4.5.4 rule 1. REPLACES: "1. **Existence gate.** A `community` is admitted, and continues to federate, **only while ≥1 member holds the live `moderate` duty**."
- **DRAFT.** "1. **Existence gate.** A `community` is admitted, and continues to federate, **only while a person holds a live duty seat over it**. An agent's key that holds a duty keeps no room open."
- **TABLES.** `rule_entries.tsv:2722` quotes "only while ≥1 member holds the live `moderate` duty".
- **NAMES.** None.
- **CHECKED BY.** The kernel's duty-seat and election cases.
- **DEPENDS ON / CONFLICTS.**
  - CC 4.5.4 *Enforcement layer* "`C` is admitted to federate **only if** ∃ a live `moderate`-holder" and "No unmoderated multi-party space … ≥1 active holder of its `moderate` duty". Both are consistent once read with "a person". Add "a person who is" before "a live `moderate`-holder" in (i).
  - Every duty seat over a community carries `moderate` (CC 2.7.5).

### B-42 Placements the family table does not give, and replication-audience cells

- **RULE.** **Partly recoverable.** Owed checks on `manifests/family_model.json` (the CC 3.1 table and `formal/derivation/placement_text.tsv`):
  - Nine placements are not from the table.
  - Five families are held shut, and their placement "never stored" contradicts CC 3.1.5.
  - Custody, duty and ownership follow another row (B-21).
  - `stream:head` is a gap.
  - The `may_carry_under` column is read against a node's row in a private room (CC 3.1.3.2 *A node's row in a private room*: it carries `under`).
  - The placements of a key revocation and an occurrence revocation want a look (C-10).
  - The replication-audience cells are unfilled.
- **AUTHORITY.** Derived. It was listed as owed after the placements lane.
- **HOME.** No Part sentence unless a placement needs one. `formal/derivation/placement_text.tsv` and the CC 3.1 table.
- **DRAFT.** Per family, from the sentence that places it.
- **TABLES.** `formal/derivation/placement_text.tsv`; the family model regenerates. Tell the kernel the new hash.
- **NAMES.** None.
- **CHECKED BY.** The family model build.
- **DEPENDS ON / CONFLICTS.** B-01, B-21 and C-10.

### B-43 The halt row's cells against the text

- **RULE.** Check the `accord_halt` row's cells against CC 4.2.1.1 and CC 4.5.13:
  - `concluder` `local` (each node, unsigned);
  - `opener_says` `fires`;
  - `at_window` `lapsed`.
  The text says one holder fires at once, the fuse is each node's own with no landing, and a majority confirms. The kernel's reference names the concluder `holder` and the opener's word `confirm`. "Counts nobody" is not expressible in the table.
- **AUTHORITY.** Text already says (CC 4.5.13 "The `accord_halt` row reads its two cells the other way round"; CC 4.2.1.1).
- **HOME.** The table only, unless the check finds the text unclear.
- **DRAFT.** None unless the check finds a gap. If it does, report the gap rather than write.
- **TABLES.** `constitution/governance_policy.tsv` row `accord_halt`.
- **NAMES.** None.
- **CHECKED BY.** `tools/build_governance_policy.py`.
- **DEPENDS ON / CONFLICTS.** None. The halt is the condition of symmetry; keep that wording in any note.

### B-44 Done in the tree: listed so that nobody writes them again

| Item | Where | Commit |
|---|---|---|
| The acts row `accept \| trust_edge \| affiliation` | `constitution/governance_policy_acts.tsv:40` | `0eb963d` |
| The three default policy rows' `opener` = `member`, the opening is its own approval | `constitution/governance_policy.tsv` | `46a1f6f` |
| The join's "retired" (replaced by a counted recovery, no voice) and "left" (routine rotation, still a voice on its branch) split, and who else signs a join | CC 2.6.1.11 *A bundle that joins tips* | `0eb963d` |
| `recovery_behind_head` reworded (only where `prev` is in the past of a bundle its holder signed and is none of its named predecessors) | CC 2.6.1.11 | `0eb963d` (first named in `e4abbf4`) |
| `receipt_no_instant` (a receipt without its instant is refused) and its name-table row | CC 2.6.1.11; `manifests/scitt_names.tsv:52` | `0eb963d`, `0e80f21` |
| A genesis bundle's statement carries `sub` equal to `family_key_id`; an owner-binding is placed by its own scope | CC 2.6.1.11, CDDL `object-claims` | `5923919` |
| The six live mesh configuration keys named in every list | CC 3.1.9.2, CC 4.2.1, CC 6.1.5.1 | `c9988f8`, `9082e73` |
| The one-officer rule widened: admission is the only uncountersigned act | CC 4.4.3.12 *One officer* | `76302e7` |
| A grant resolves only while its voices are a strict majority of the holders in force | CC 3.2 T6 | `b64ae3c` |
| A node's row in a private room, and the door's order | CC 3.1.3.2 | `1bd3c2f` |
| One target for each counted removal | CC 3.3.4 | `c125852` |
| At most one invitation pending by the window per member | CC 4.5.13 | `83cd94a` |
| The owner's acceptance cites its owner-binding | CC 3.1.2.1 | `d05d0a4` |
| "Anyone MAY propose a moderation action" reconciled with "a member signs it" | CC 4.5.13 reads "Any member MAY propose" | in tree at the pin |
| Open subscription seats nobody | CC 4.4.3.10 | in tree at the pin |

---

## 3. Group C: decisions still open with the steward

Each entry gives the question, the options, what each costs, and what is written meanwhile.

### C-01 Should a removal at tips need its count over the members the fold seats?

- **QUESTION.** At tips, should a removal take a key out only where it meets its count over the members the fold seats, symmetric with additions?
- **OPTIONS.**
  - (a) Symmetric. An unjust removal is not final at tips. An honest removal that is blunted is re-signed forward.
  - (b) As written: removal wins at any tip.
- **COSTS.**
  - (a) An honest removal can need re-signing.
  - (b) In a private room room-key finality makes an unjust removal at a tip irreparable.
  - The coordinator recommended (a).
- **MEANTIME.** The text stands: CC 2.7.8 "A member one tip admits and another removes is out."

### C-02 Should a lone add need the other members' silence?

- **QUESTION.** Should a self roster's lone addition need every other key's silence, as the lone eviction needs the target's?
- **OPTIONS.**
  - (a) Keep it as written: one objection of two others does not stop it.
  - (b) Any objection stops a lone add.
- **COSTS.**
  - (a) Carries the cost stated in A-16: one key of three, with one other silent, adds a key and holds half the roster, unremovable.
  - (b) Lets a single stolen key block an honest addition. CC 3.3.6.4 already says so for two keys.
- **MEANTIME.** As written, with A-16's stated cost. Put the question to the steward after the kernel tag.

### C-03 The bounded settler

- **QUESTION.** Keep the settler of A-10, or state a permanent stall of a contested trust root?
- **OPTIONS.**
  - (a) The settler, as derived.
  - (b) A stated stall until a bundle names both.
- **COSTS.**
  - (a) Adds a counted row kind and its family, and carries A-10's residual.
  - (b) A contested root can stay stopped for good.
- **MEANTIME.** A-10 is written when the tag lands, unless the steward overturns it. It was told to him, and it is his to overturn.

### C-04 The one-officer affiliation

- **QUESTION.** While an affiliation has one officer, is admission its only act with no countersign?
- **OPTIONS.**
  - (a) As written (`76302e7`).
  - (b) Countersign admission too.
- **COSTS.**
  - (a) Two officer keys of one person that no roster links read as two officers.
  - (b) A sole practitioner cannot admit a member without an outside key.
- **MEANTIME.** (a) stands in the text. It was told to the steward, and it is his to overturn.

### C-05 Who signs a trust root's naming of a room

- **QUESTION.** Which row, and whose count, names a room for readers who trust a root? There is no rule for a holders' vote on a listing, and no charter scope for it.
- **MEANTIME.** The text says only its reach and limits: it reaches only readers whose trust set holds that root, and it unlists and bans nothing (CC 3.2 *Discovery*).

### C-06 How a publication is marked open, and how it reaches a non-member subscriber

- **QUESTION.** "Marks open" names no field on a publication, and delivery to a subscriber who is no member is unstated.
- **MEANTIME.** CC 4.4.3.10 *Open subscription* stands. B-32 waits on this.

### C-07 Who holds and serves a public room

- **QUESTION.** A public roster is a list of targets. Which nodes hold a public room's rows and serve them to readers?
- **MEANTIME.** CC 3.2 and CC 5.2 as written: Commons-tier plaintext, replicated to the roster's claimed nodes, read by asking a member's node.

### C-08 Reporting a room

- **QUESTION.** There is no way to report a room. A private report goes to the room's own duty holder.
- **MEANTIME.** Hate speech is answered by visibility (labels, the default filter, each node's choice, legal notice to an operator), never by a mesh-wide ban (CC 3.2 "Nothing bans a room mesh-wide").

### C-09 A legal hold by a stranger

- **QUESTION.** CC 2.7.3's list of rows a node MUST NOT decline covers an end of a seat, a withdrawal, a recant, a takedown or purge notice and a key revocation. It does not cover a legal hold signed by a key outside the node's trust set.
- **MEANTIME.** CC 2.7.3 as written. CC 5.2 *What a node holds from a stranger* lets a node evict a stranger's row "within the limit of [CC 2.7.3]".

### C-10 A key revocation's placement against "revocations replicate federation-wide"

- **QUESTION.** The text places a `key:revocation` where the record of the key it revokes is placed. CC 2.4.1.1 also says "Revocations replicate federation-wide". The two want one reading.
- **MEANTIME.** Both sentences stand. B-42 lists the placement for the check.

### C-11 A member's vote under an affiliation's charter

- **QUESTION.** CC 4.4.3.12 says members of an affiliation hold no governance vote "unless its charter grants one". No member of the record grants one.
- **OPTIONS.**
  - (a) Remove the clause.
  - (b) Add a charter field.
- **MEANTIME.** The clause stands, and the open ledger row "A member's governance vote under an affiliation's charter" carries it.

### C-12 A carrier for a call's opening row

- **QUESTION.** B-25's alert mode needs a row that opens a call, and the text composes calls with no new wire.
- **OPTIONS.**
  - (a) A member on an existing row: the room's call stream's first binding.
  - (b) A row of its own.
  - (c) No signed alert: a node's own setting.
- **MEANTIME.** Nothing is written. The steward's words to the implementer that asked are not in the record. Get them first-hand.

### C-13 The two 1.0 decisions not answered

- **QUESTIONS.**
  - (1) Does the headline count of properties and models change when duplicate models retire?
  - (2) Does CC 8.11 (the earlier signed object) leave the 1.0 text?
- **ANSWERED.** The steward decided, direct, that the open ledger closes before 1.0: "this is our 1.0, this is pure knowledge work, and we can see the end state clearly".
- **MEANTIME.** Both stand as they are.

### C-14 One target for a recall, a duty withdrawal and a demotion

- **QUESTION.** The one-target shape of a counted removal (A-08) was asked for a recall, a duty withdrawal and a demotion, and not ruled. This is open with the kernel's model before the steward.
- **MEANTIME.** The text and the policy rows stand. A recall names the holder it recalls (CC 4.5.13).

### C-15 Pacing: the stale bound, whose rate, and a publisher's clock

- **QUESTION.** See B-26.
- **MEANTIME.** The pacing block stands, and the open ledger row "Pacing beyond the bounded model" carries the rest.

### C-16 A removal in an open room

- **STATUS.** Moot. Open admission is cut (the steward, direct). Nothing to decide for 1.0.

### C-17 A changed listing is a new row, and needs fresh vouches

- **QUESTION.** A vouch for a room is a positive public `regard:room` on its listing as it stands. Is a renamed or changed listing a superseding row that no earlier vouch names, so that it needs fresh vouches? The sentence was handed on conditionally: only if the text makes a changed listing a new row. No sentence in the Parts says so at the pin.
- **OPTIONS.**
  - (a) A changed listing is a new row, and earlier vouches do not reach it.
  - (b) A vouch follows the listing's supersession.
- **COSTS.**
  - (a) A room that renames itself starts unlisted for every reader.
  - (b) A room can be vouched as one thing and shown as another.
- **MEANTIME.** Nothing is written. CC 3.2 *Discovery* and CC 4.4.3.13 stand.

---

## 4. Group D: after the cut

### D-01 The IETF draft, revision -05

- **RULE.** These reach `draft-moore-scitt-ciris-ceg` -05:
  1. `further_prev` in the CDDL copy (M1) and its join rule (CC 2.6.1.11).
  2. A genesis bundle's statement carries `sub` equal to `family_key_id`, in `object-claims` and the matching sentence.
  3. A receipt's `iat` is REQUIRED, and a receipt without one is refused, `receipt_no_instant` (B-17).
  4. A snapshot's and a boot manifest's `sub` are SHOULD (B-18).
  5. `trust:registers:v1` as a third trust job, and the companion reference. These come only after the design team has seen a Receipt and settled whether a companion is placed in the header or the payload. The steward, direct: "yes we can propose this shape and adopt in a -05 if agreed".
  6. The CEG statement id as a named scheme in the statement-references draft, with its known answer. This is the design team's draft, not ours: track it.
  7. The submission fixes the tool reported on -04: v3 XML and `submissiontype`.
  8. The two open verification answers listed against -04: the Waiting row outside the steps, and the full reason list.
  9. Suites in force as a charter member (A-23), once modelled.
- **AUTHORITY.** As listed.
- **HOME.** `ietf/` (the draft source and `tools/build_ietf_draft.py`).
- **DEPENDS ON.** B-17, B-18, B-19 and A-23.

### D-02 A child excuses its parent's silence only on the publisher's signed backlog stamp

- **RULE.**
  - A child excuses its parent's silence only on the publisher's signed backlog stamp, relayed unaltered, judged net of the backlog it declares: age less backlog at most 2.5 s.
  - The grace before a first chunk also runs from the stamp.
  - The stamp is signed by the bound chunk key, under its own domain label. It carries the stream id, the epoch, the send time, the declared backlog and the highest chunk sequence.
  - A relay forwards it byte for byte or drops it, and never mints one. It is first class.
- **AUTHORITY.** Derived and accepted. The transport brings the wire shape.
- **HOME.** CC 5.3.3.2 or CC 5.3.3.5, with the transport's wire shape.
- **DEPENDS ON.** The transport's shape.

### D-03 A removal stops a publisher's chunks at every node that holds it

- **RULE.**
  - A node that holds a removal in force of a publisher tears down that publisher's legs, drops its chunks per chunk at relay and receiver (`av_binding_publisher_not_member`), and refuses its bindings.
  - This holds in a public stream, which has no epoch roll to cut the leg, and per chunk in a private room.
- **AUTHORITY.** Derived and accepted. It is written when the transport builds it.
- **HOME.** CC 5.3.3.5.
- **DEPENDS ON.** The transport's build.

### D-04 A non-member's view of a public room's live stream

- **RULE.**
  - A viewer asks a member's node, or a joined serve node, for a downstream-only leaf leg with no children. Only members and joined serve nodes relay.
  - A public stream's chunks are signed only, with no inner content-key seal, and the binding says so under the publisher's signature.
  - A viewer's control rides in the floor, and is not first class.
  - Viewers' media are admitted against capacity, with per-origin viewer budgets. A viewer is never in a member's backlog.
  - A removal halts the member's live publication at once.
  - A viewer's report names the stream and a `chunk_seq` range. Kept chunks are attributable evidence by their signatures.
  - The audience bound is the sum of relay uplink over the copy rate.
- **AUTHORITY.**
  - The steward, direct: "anyone can view a live stream from a public room … but only roster members can share video" (landed in CC 5.1).
  - The steward, to the transport, first-hand: viewers come after its next release.
  - The design is derived and accepted. It is neither written nor built.
- **HOME.** CC 5.1 ("receive the current DEK on request" is rewritten), CC 5.3.3.5 and CC 5.3.3.7.
- **TABLES.** Ledger (register lane): the open row "A non-member's view of a public room's live stream" closes when this is written.

### D-05 The link path between two nodes

- **RULE.**
  - The state table gains an entity `link.path`, with states `none`, `relayed`, `upgrading` and `direct`, and six transitions. It cites the transport's direct-link model when that model is vendored.
  - In CC 5.4.6, one sentence: upgrade signalling is link payload.
  - Each side probes a facilitator of its own choosing, or the relay carrying the link, never one only the peer named.
  - An Anonymous Tier identity stays relayed.
- **AUTHORITY.** Derived and agreed with the transport.
- **HOME.** `formal/STATE_TABLE.tsv` and CC 5.4.6.
- **DEPENDS ON.** The transport's model being vendored. Ask before vendoring.

### D-06 Which families pace first

- **RULE.**
  - Control is first in the pacing order (CC 5.3.3.2). The first class, by family, is: accord, membership, `key_grant`, key, session, consent, moderation, revocation, recants, `withdraws`, `duty`, `ownership`, and any row unknown or unparsed.
  - Bulk is: chat, file, `supersedes`, scores, trust, capacity, content class, objection, traces, directory and content replies.
  - A delivery is bulk only if every row in it is.
- **AUTHORITY.** Derived (the transport's real-time questions). The transport owes its first-class bytes by family.
- **HOME.** CC 5.3.3.2 *Pacing under a queued uplink*.
- **DEPENDS ON.** The transport's list.

### D-07 Two transport sentences that are not written

- **RULE.** Neither is written, and both need the transport's position:
  - Bundling individually signed chunks in one link frame conflicts with CC 5.3.3.5 ("one chunk, one link payload") and CC 5.3.3.7's outer nonce.
  - "One epoch behind does not connect" conflicts with the one-epoch-older window of CC 5.3.3.5.
- **HOME.** CC 5.3.3.5 and CC 5.3.3.7.

### D-08 Citing the transport's models in Part 8

- **RULE.** Part 8 cites the transport's model commits by name and commit, never by path.
- **HOME.** Part 8 (register lane).

### D-09 Follow-ups to implementers' releases

- **RULE.**
  - Re-pin the verifier's vector rows (CC 2.6.5) at its next release tag: row statements, key-of-issuer and the room door.
  - Vendor the kernel tag the implementers pin, and re-pin the family model's hash with the kernel after every placement change.
  - Re-pin the policy after B-22 and A-18.
  - The refusal-token manifest is sorted by name: implementers pin by name.
  - The frame cap for each outer key waits for the transport's position.
- **HOME.** `formal/vendor/VENDOR.tsv`, CC 2.6.5 and `manifests/ADOPTER_FILES.md` (generated).

---

## 5. Index

| Id | One-line rule | Home | Group | Status |
|---|---|---|---|---|
| A-01 | A count is taken at the newest counted heads in the row's past; no read-through; no roster-changing row exempt | CC 2.7.8, 2.4.1.1, 3.3.4 | A | owed |
| A-02 | The reader's line is sibling-safe, monotone, made of the reader's own rows; an acknowledgement settles over its own past | CC 2.7.8, 3.3.4, 3.3.6.4 | A | owed |
| A-03 | A change all its voices left is void only by the fork-point count; rescue; voids a change, never a key | CC 2.7.8 | A | owed |
| A-04 | The fold over surviving tips; record-change tip under its own protocol; contested pair in every group | CC 2.7.8 | A | owed |
| A-05 | Rules 3, 5 and 6 for every group; a double signer has no say at that head; a halt still halts | CC 2.7.7 | A | owed |
| A-06 | The roster merge: counted on each tip, fixed roster, no duty seats; infrastructure merge is a founders' amendment | CC 2.7.8, 2.7.9 | A | owed |
| A-07 | The residuals in text form: no-row reader, newcomer on a fork, lone-sibling window, accepted cost | CC 2.7.9, 2.7.8, 3.3.4 | A | owed |
| A-08 | One target for each counted removal; floor two | CC 3.3.4; policy | A | DONE-IN-TREE (`c125852`) |
| A-09 | Trust root: rules 5, 6 and 3 for bundles; recovery costs; residuals | CC 3.2 T6, 2.6.1.11 | A | owed (join, grants DONE) |
| A-10 | The bounded settler | CC 3.2 T6, 2.6.1.11 | A | owed; family not recoverable |
| A-11 | The election: counted opening, electorate at its heads, rows by reference, close by receipts, `moderate` only | CC 4.5.13, 3.1.3 | A | owed; opening family, ballot role and decline's answered row not recoverable |
| A-12 | Ranked count: options with no ballot fall together; the runoff order | CC 4.5.13 | A | owed |
| A-13 | Counts over persons; agent key out before the map; key speaks for a person while live in its self roster | CC 4.5.13, 2.6.1.4 | A | owed |
| A-14 | A rival founding of a self roster is resolved by the reader's line; adopter duty | CC 3.3.6.4 | A | owed |
| A-15 | A key's end is a cut; a rotated-away key's revocation is no end; caller duty and residual | CC 2.4.1.1 | A | owed; rotation voiding not recoverable |
| A-16 | Self roster: landed window is the change; two lone evictions contested; lone add cost; two keys | CC 3.3.6.4 | A | owed |
| A-17 | Duty acts: quarantine, slash, takedown, reconsideration, lift; target never releases; release is a supersede | CC 4.5.5, 3.1.9.2 | A | owed |
| A-18 | The lift: newest heads, two-head base, no freshness clock | CC 4.5.13; policy | A | owed (pin moves) |
| A-19 | Who is served: rows to current-roster keys only; key grant never carried; `history_on_join` no part | CC 5.2 | A | owed |
| A-20 | The countersign is a voice on the act's own row | CC 4.4.3.12 | A | owed (one-officer DONE `76302e7`) |
| A-21 | Licence term and reader's anchor; a pre-lock edge runs to its term | CC 4.5.4, 2.4.1.3 | A | owed; anchor's second arm to confirm |
| A-22 | The consent peer set | CC 3.3.7 | A | not recoverable |
| A-23 | Adding and retiring a signature suite | CC 2.6.1.7, 2.6.1.11 | A | owed (after its model); member name not recoverable |
| A-24 | Room keys: second seat row, end of a stay, batch admission | CC 3.1.3.2 | A | owed (node's row DONE `1bd3c2f`) |
| A-25 | A lone holder with an offer standing confers no other alone | CC 4.5.4 | A | owed |
| A-26 | Receipts of counts | CC 2.7.5 | A | partly recoverable |
| A-27 | Infrastructure: the founders' amendment keeps the word up to `N` | CC 3.2, 4.4.3.18 | A | owed |
| A-28 | A family's founders | CC 3.3.4 | A | owed |
| B-01 | `cohort_scope` required only where the row places itself | CC 2.1 | B | owed |
| B-02 | `attached_head_digest` is the bundle's object id | CC 2.1, 2.6.1.3 | B | owed |
| B-03 | `membership:proposal` payload rule; role optional, not nullable | CC 3.1.3.2; tsv | B | owed |
| B-04 | `membership:resignation` payload rule; no target | CC 2.4.1.1; tsv | B | owed |
| B-05 | A lay-down carries `scope`; rule 0 does not reach an own withdrawal | CC 2.4.1.1; tsv | B | owed |
| B-06 | `reconsideration` payload: `outcome`, cites one act | CC 3.1.9.2; tsv | B | owed |
| B-07 | A quarantine release is the holder's supersede | CC 3.1.9.2; tsv | B | owed |
| B-08 | A lift cites exactly one act | CC 4.5.13 | B | owed; re-seating family not recoverable |
| B-09 | Record members `declared_cohort`, `overseen_by`, `designated_officials`, `licence_classes` | CC 4.4.3.12; tsv | B | owed |
| B-10 | `weights` and `need` | CC 3.3.4; tsv | B | owed |
| B-11 | Recovery widening names its grant in `stands_on` | CC 3.2 T7; tsv | B | owed |
| B-12 | Reply-to-grant schema note: cites its owner-binding | tsv, CDDL | B | owed (text DONE `d05d0a4`) |
| B-13 | Ballot rows by reference; the 3.1.4 cite fixed | CC 4.5.13, 3.1.3 | B | cite owed now; rest with A-11 |
| B-14 | An election's decline is `membership:decline:v1` | CC 4.5.13; tsv | B | owed; answered row not recoverable |
| B-15 | `ranks` is a sequence | CC 2.6.1.2 | B | owed |
| B-16 | `proposal` is no objection state | CC 4.5.13 | B | owed |
| B-17 | Receipt protected claims as a schema rule | CDDL, tsv | B | owed (text DONE `0eb963d`) |
| B-18 | Snapshot and boot-manifest `sub` SHOULD | CC 2.6.1.11; CDDL | B | owed |
| B-19 | `ietf/` CDDL labelled the -04 snapshot | tool template | B | owed |
| B-20 | Eviction instants are documentary | CC 3.3.6.4; tsv | B | owed |
| B-21 | How a following family names what it follows | CC 3.1.1, 3.1.9; tsv | B | owed |
| B-22 | The `unstated` policy cells | policy_text.tsv | B | owed (pin moves) |
| B-23 | `dropped` is a storage note | CC 4.5.13 legend | B | owed |
| B-24 | A moderator's ballot resolves a moderation proposal | CC 4.5.13 | B | owed |
| B-25 | A call's alert mode; no row opens a call | CC 5.3.3.2 | B | blocked by C-12 |
| B-26 | Pacing: stale bound, whose rate, backward clock step | CC 5.3.3.2 | B | not recoverable |
| B-27 | (filed as B-31) | — | B | — |
| B-28 | Mesh configuration rules | CC 4.2.1, 3.1.9.2, 6.1.5.1 | B | DONE-IN-TREE (`72dfade`, `c9988f8`, `9082e73`) |
| B-29 | The merge's "open on the wire" note | family_shapes.tsv | B | with A-06 |
| B-30 | Gate the public-room models; the mesh model's admission; the claim's evidence | formal, claims.tsv | B | owed |
| B-31 | CC 4.4.3.17 pseudocode: one target, floor, persons, heads, `need` | CC 4.4.3.17 | B | owed |
| B-32 | CC 4.4.3.10 cardinality table and a non-member subscriber | CC 4.4.3.10 | B | waits C-06 |
| B-33 | The old component name in Parts 3 and 8 | CC 3.1.9 et al. | B | owed (heading stays) |
| B-34 | A root grant's room is a token of `scope` | CC 3.2 T7 | B | owed |
| B-35 | `sub_delegation` in `charter.scope` | CC 3.4.7 | B | owed |
| B-36 | A window's outcome is its leaf | CC 3.1.3 | B | owed |
| B-37 | Which key record says agent seat | CC 4.5.4 | B | owed |
| B-38 | Which genesis record the first bind names | CC 3.3.6.4 | B | partly recoverable |
| B-39 | `iss` for who signed, `kid` for a key's life (optional) | CC 2.6.1.4, 2.4.1.1 | B | optional |
| B-40 | No row opens a poll | CC 4.5.13 | B | not ruled |
| B-41 | The existence gate: a person holds a duty seat | CC 4.5.4 | B | owed |
| B-42 | Placements the table does not give; audience cells | placement_text.tsv | B | partly recoverable |
| B-43 | The halt row's cells against the text | governance_policy.tsv | B | check |
| B-44 | Items done in the tree | — | B | DONE-IN-TREE |
| C-01 | Symmetric removal at tips? | CC 2.7.8 | C | open |
| C-02 | Lone add needs the others' silence? | CC 3.3.6.4 | C | open (after the tag) |
| C-03 | Settler or stated stall | CC 3.2 T6 | C | his to overturn |
| C-04 | One-officer affiliation | CC 4.4.3.12 | C | his to overturn |
| C-05 | Who signs a root's naming of a room | CC 3.2 | C | open |
| C-06 | How a publication is marked open; non-member delivery | CC 4.4.3.10 | C | open |
| C-07 | Who holds and serves a public room | CC 3.2, 5.2 | C | open |
| C-08 | Reporting a room | CC 4.5.13 | C | open |
| C-09 | A stranger's legal hold vs CC 2.7.3 | CC 2.7.3 | C | open |
| C-10 | Revocation placement vs "replicate federation-wide" | CC 2.4.1.1 | C | open |
| C-11 | Affiliation member vote "unless its charter grants one" | CC 4.4.3.12 | C | open |
| C-12 | A carrier for a call's opening row | CC 5.3.3.2 | C | open |
| C-13 | Headline model count; CC 8.11 in 1.0 | — | C | open |
| C-14 | One target for recall, duty withdrawal, demotion | CC 4.5.13 | C | open (kernel first) |
| C-15 | Pacing open terms | CC 5.3.3.2 | C | open |
| C-16 | Removal in an open room | — | C | moot |
| C-17 | A changed listing is a new row and needs fresh vouches? | CC 3.2, 4.4.3.13 | C | open |
| D-01 | IETF -05 list | `ietf/` | D | after the cut |
| D-02 | Offer-as-life on the publisher's signed stamp | CC 5.3.3 | D | after the transport's shape |
| D-03 | A removal stops a publisher's chunks | CC 5.3.3.5 | D | after the build |
| D-04 | A non-member views a public stream | CC 5.1, 5.3.3.5, 5.3.3.7 | D | after the transport's next release |
| D-05 | `link.path` and the CC 5.4.6 sentences | STATE_TABLE, CC 5.4.6 | D | after vendoring |
| D-06 | Which families pace first | CC 5.3.3.2 | D | after the transport's list |
| D-07 | Bundling chunks; one epoch behind | CC 5.3.3.5, 5.3.3.7 | D | not written |
| D-08 | Part 8 cites transport models by commit | Part 8 | D | register lane |
| D-09 | Implementer re-pins and vendor | VENDOR.tsv, CC 2.6.5 | D | after releases |
