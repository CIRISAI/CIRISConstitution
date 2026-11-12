# What five readings found, by kind of change, and which models to build

Working analysis, 2026-11-12, asked for by the steward. Source: `formal/derivation/text_conflicts.tsv`
(C001 to C555), each row classified by a reader lane (`handoff/lanes/T_TAXONOMY.md`,
`handoff/lanes/out_t_all.tsv`). The classifiers worked from the two sides and the verifier's reasoning
and mostly did not reopen the sections, so "which existing model" is the weakest column and the
kind, class and mechanism columns are the stronger ones. Counts are of findings, not of sentences changed.

## The five readings

| | Method | Statements read | Findings logged | New majors |
|---|---|---|---|---|
| R1 | section by section, one sweep | all | 287 | not graded |
| R2 | rule key by rule key, general rules only | 2,533 | 59 | 59 |
| R3 | rule key by rule key, all rules, against the data too | 4,254 | 89 | 89 |
| R4 | the same, text opened for nearly every statement | 4,254 | 77 | 77 |
| R5 | the same | 4,254 | 43 | 43 |

R2 to R5 log major findings only, after a verifier; R1 logged everything it saw.

## By kind of change (the RATCHET taxonomy, CC 1.13.4)

| Kind | R1 | R2 | R3 | R4 | R5 | All |
|---|---|---|---|---|---|---|
| Manner (how it is said) | 70 | 1 | 0 | 0 | 0 | 71 |
| Facts (a number, a name, a value) | 37 | 1 | 6 | 3 | 0 | 47 |
| Rules (permitted, required, refused) | 56 | 20 | 25 | 19 | 16 | 136 |
| Circumstances (when, where, at what scope) | 32 | 11 | 14 | 14 | 6 | 77 |
| Identity (who a party is, which role) | 20 | 9 | 18 | 15 | 10 | 72 |
| Structure (who counts, quorums, chains) | 22 | 6 | 9 | 15 | 2 | 54 |
| Model (a formula, a fold, a data shape) | 29 | 5 | 9 | 5 | 4 | 52 |
| Process (order of steps) | 8 | 5 | 4 | 3 | 2 | 22 |
| Confidence | 7 | 0 | 2 | 3 | 1 | 13 |
| Priorities (which wins) | 2 | 1 | 2 | 0 | 2 | 7 |
| Premises | 4 | 0 | 0 | 0 | 0 | 4 |
| touches the Record | 31 | 20 | 21 | 11 | 7 | 90 |

Reading it:

- **The surface kinds went first.** Manner and Facts were 107 of R1's 287 and are 3 of R4's and R5's 120.
  A sweep by section sees wording and numbers. Nothing finds them now because they are gone.
- **What is left is Rules, Identity and Circumstances:** what is permitted, who may do it, and at what instant
  or scope. In R5 those three are 32 of 43.
- **Identity is the stubborn one.** It does not fall (20, 9, 18, 15, 10) and it is mostly one question: who
  may sign this row. That is the signer column, the duty-holder table of CC 4.5.5, and the conferral of
  reserved roles.
- **Structure spiked in R4 and fell in R5** (15 to 2): the count cells and the one-seat affiliation, corrected.
- **Priorities, Confidence and Premises barely appear.** That matches CC 1.13.4's own remark that unassisted
  reading does not surface the deep kinds. It is not evidence they are clean. It is evidence that reading
  is the wrong instrument for them.

## By class

| Class | R1 | R2 | R3 | R4 | R5 |
|---|---|---|---|---|---|
| drift (one rule, restated wrongly) | 177 | 29 | 40 | 20 | 13 |
| interaction (two right rules, one case) | 17 | 8 | 9 | 6 | 9 |
| gap (silence read two ways) | 24 | 1 | 0 | 0 | 2 |
| fault in this repository's tables | 4 | 3 | 21 | 20 | 12 |
| the text against the shipped store | 1 | 1 | 10 | 24 | 3 |
| no conflict on a full read | 64 | 17 | 9 | 7 | 4 |

- Drift fell at every step and is 13 in R5. Interactions hold at six to nine a reading: as a share of what
  is found they went from 6% to 21%.
- The share a verifier dissolves fell from 29% (R2) to 9% (R5). The readers got stricter and the findings
  got realer.
- Table faults appeared when the tables did (R3) and are falling as they are corrected.

## What a model would have caught

| | R1 | R2 | R3 | R4 | R5 |
|---|---|---|---|---|---|
| yes | 133 | 39 | 76 | 67 | 33 |
| partly | 45 | 4 | 4 | 3 | 5 |
| no (wording, citation, presentation) | 109 | 16 | 9 | 7 | 5 |

46% in R1, 77% to 87% from R3 on. The later a finding, the more it is the kind a checker finds and a
reader finds slowly.

## By part of the state processor

| Mechanism | R1 | R2 | R3 | R4 | R5 | All |
|---|---|---|---|---|---|---|
| guard (what must be held to admit a row) | 45 | 14 | 15 | 8 | 8 | 90 |
| signer (who may sign) | 17 | 5 | 19 | 17 | 12 | 70 |
| audience (who is served, scope) | 25 | 14 | 7 | 9 | 3 | 58 |
| count (how many voices, over which set) | 25 | 3 | 10 | 12 | 4 | 54 |
| clock (expiry, windows) | 25 | 4 | 12 | 6 | 5 | 52 |
| wire (bytes, members, ids) | 28 | 3 | 7 | 9 | 3 | 50 |
| fold (which row stands, how they combine) | 12 | 5 | 10 | 4 | 4 | 35 |
| change (what a replacing row may do) | 17 | 6 | 2 | 5 | 1 | 31 |
| erasure | 8 | 3 | 3 | 2 | 1 | 17 |
| lifecycle (which verbs) | 2 | 0 | 4 | 5 | 1 | 12 |

Guards and signers are 160 of the 469 findings that have a mechanism. Both are admission questions:
may this key sign this row, and what must already be true. The door is where the text disagrees with
itself most, and the door is one function (CC 4.5.13).

## Which models

Counts are findings a model would catch (yes or partly). Names that the classifiers gave to the same
thing are merged.

### New models, in order

1. **The signer gate** (21 findings; Identity 10, Rules 7). Who may sign a row of a reserved or duty-bound
   family: the membership test, the live conferral, the duty-holder table of CC 4.5.5, the steward and the
   detecting node's owner. One model with the gate as a function of (family, leaf, signer's roles,
   conferrals held), checked against every family's signer cell. Properties the findings name:
   - a row of a reserved family is admitted only from a key that holds the role and a live conferral of it;
   - every outcome the text describes is a row some key may sign or a verdict each node derives, and none
     needs a row the door refuses (this one alone covers the undefended report, the viewer's consent row
     and the steward with no duty);
   - a moderation row is admitted only from a named moderator or its chain, never from the content's
     subject as such; a takedown notice from the subject, a takedown holder, or the detecting node's owner;
   - no door depends on a quorum it cannot test.
   This is the model the seat rule needs as well, so it should be built with it.

2. **The key plane** (23 findings; Rules 8, Circumstances 6). The cascade, the epoch, the stream keys,
   who receives a wrap and when. Properties:
   - after any departure, at any scope, later content is sealed under a key the departed member cannot derive;
   - no write after a removal is sealed under a key the removed member was granted;
   - a key grant is signed only by a key that speaks for the blob's owner;
   - a new member's grant of the current epoch is emitted at the minter's next sealed write;
   - a joiner holds no key for an epoch before its admission unless the publisher signed a re-share;
   - a wrap reaches an occurrence only where its node's allow list names the cohort.
   Several open items sit here (relay trees, a late joiner, keep changed mid-stream), so the model would
   show which answers are consistent with the rest before anyone chooses.

3. **Takedown and erasure** (22 findings; Facts 7, Rules 5). The bases, the withhold windows, reversal,
   legal hold, the deletion window and its breach. Properties:
   - every windowed basis stops serving on admission, runs its window, and destroys at its close unless
     a reversal or a members' lift was admitted inside it;
   - an immediate-removal basis destroys on receipt;
   - bytes under a live legal hold are never destroyed (stated together with the one above, the checker
     reports the case the steward has been asked about);
   - a producer is in breach exactly when the window has passed with the row still present and none of
     the producer's own composers against it, whatever it reported;
   - a subject's withdrawal starts the window and discharges nothing.

4. **Guardianship and incapacity** (12 findings, plus 13 on the existing age model). Who may be a
   guardian, on what assurance, what a guardian may never do, how a binding ends. The age model
   (`formal/age_assurance`) holds the band; this holds the binding. It needs the steward's answer on how a
   guardian is displaced before its transition relation can be written.

5. **The owner binding** (13 findings; Model 4). One owner, several rows, steward-bound or not.
   Properties: a node with one owner and two live owner-signed rows reads steward-bound exactly as with
   one; at most one live owner at any instant; ownership moves by withdraw-then-rebind; an occurrence
   never makes a key steward-bound.

### Existing models to extend

| Model | Findings it should have held | What is missing from it |
|---|---|---|
| `formal/consent` | 26 | the boundary fold as the read path, who may emit each leaf (expired is the store's), the partnership pair's signer, the lapse clock |
| `formal/family_model` | 24 | signer cells and verbs checked against the text and not only the kind grid; this is where the signer gate plugs in |
| `formal/membership` | 21 | the standing proposal of an open room, a resignation's signer, the hold on a signature shortfall, the signed instant, the recovery widening as the one exception |
| `formal/authority_tree` | 20 | conferral as necessary-and-not-sufficient; depth cap; who withdraws a seat |
| `formal/mesh_net` | 15 | what crosses before rooting; who serves an owned node's route |
| `formal/trust_root` | 13 | T8 against T4 and T6 (the collapsed directory); the attach window never detaching |
| `formal/accord_halt`, `accord_roster` | 13 each | a future-dated halt; the roster change's signing; what a holder signs |

### Not a model

- **A text lint** (34 findings, all R1): counts, citations, a term used two ways. The entry check and the
  quote checks do most of this already. The remainder is a lint of terms against the glossary.
- **Wire vectors** (16 findings): member types, ids, encodings. Known answers catch these, and they belong
  with the implementers.

## What this says about method

1. A sweep by section finds Manner and Facts. Reading rule by rule finds Rules and Circumstances. Typing
   the rules as data finds Identity and Structure. A model finds interactions. Each instrument sees one
   or two kinds and is nearly blind to the rest, so the instruments have to be used in that order.
2. The first two are spent: drift is 13 in the last reading. The third is half done: typed values rest on
   17% of the rule sentences. The fourth is where the remaining return is, and three quarters of what the
   last readings found is of the kind it catches.
3. The deep kinds (Priorities, Confidence, Premises) are 24 of 555. No instrument used so far looks at
   them. Whether the document's priorities are consistent with one another is unmeasured.
4. Build order: the signer gate first, because Identity is the kind that is not falling, because the door
   is where most findings sit, and because the seat rule needs it. Then takedown and erasure, because it
   carries a steward's question a model would sharpen. Then the key plane.
