# Lane T: what kind of change each finding was, and what would have caught it

Read COMMON.md first. Your launch message names a range of conflict ids in
`formal/derivation/text_conflicts.tsv` (columns: id, sections, side_a, side_b, shape, for_eric,
still_there, carrier, witness, note, resolution). The `note` says which reading found the row and
the `resolution` gives the verifier's verdict and reasoning.

For each row in your range, read the two sides and the resolution, open the sections where you
need to, and classify it. Do not re-judge whether it is a conflict.

1. `kind`: the kind of change of the RATCHET taxonomy that the two sides differ in. The
   definition is CC 1.13.4 in `constitution/part_1_foundation.md` (the kinds-of-change map) with
   `formal/derivation/family_kind_grid.md`. Ask the map's own question, "what does varying this
   break?", of the difference between side A and side B. One of:
   Facts (what is the case: a number, a size, a name, a value) | Rules (what is permitted,
   required or refused) | Manner (how something is said or shown) | Identity (who or what a
   party or key is, which role or type it holds) | Priorities (which of two things wins or goes
   first) | Confidence (how much weight or assurance a statement carries) | Circumstances (when,
   where, at what scope or instant a rule applies) | Process (the order of steps, who acts at
   which step, what follows what) | Structure (how parts are composed: who counts, quorums,
   chains, what contains what) | Model (the instrument or representation: a formula, a fold, a
   data shape, an encoding) | Premises (what a rule assumes or exists for).
   Pick the one the difference is most about.
2. `record`: yes if the difference is about the Record (who said what, to whom, with what
   standing, what is kept or erased, what a retraction does), else no.
3. `class`: drift (one rule, restated wrongly somewhere) | interaction (two rules right in their
   own sections that differ in a case neither was written for) | gap (the text is silent and the
   silence is read two ways) | data-repo (the text is consistent and a typed table of this
   repository differs) | data-store (the text is consistent and the shipped store differs) |
   none (the verifier found no conflict).
4. `mechanism`: the part of the state processor the difference lives in. One of: signer (who may
   sign) | count (how many voices, over which set) | guard (what must be held for a row to be
   admitted) | change (what a replacing or withdrawing row may do) | fold (how rows give a
   value: which stands, how they combine) | clock (expiry, a window, what follows in time) |
   audience (who is served a row, placement, scope) | wire (bytes, members, encodings, ids) |
   erasure (what is deleted, kept, withheld) | lifecycle (which verbs a family has) | other.
5. `model`: the formal model that should hold this rule. Look at the directories under `formal/`
   (each has a README; `formal/INVARIANTS.tsv` lists every checked property). If an existing
   model covers the mechanism and the objects, give its directory name. If none does, write
   `new:` and a short name for the model that would (for example `new:deletion_window`,
   `new:consent_fold`, `new:takedown`). Use the same name for findings that belong together.
6. `would_catch`: yes if a model with both sides' rules stated in it would have reported the
   difference as a failed property or an unreachable state; no if it is a matter of wording, a
   citation or a presentation that no model reads; partly if only one half.
7. `property`: where `would_catch` is yes or partly, the property in one plain sentence (for
   example "a revoked grant never folds as granted, whatever rows arrive later").

Output: a TSV at the path your launch message gives, header
`id	kind	record	class	mechanism	model	would_catch	property`
(no tab or newline in a field). Then a file beside it, same name with `.summary.md`: counts by
kind, by class, by mechanism and by model, and the properties grouped under each `new:` model.
Final message under 100 words: the three models (existing or new) with the most findings.
