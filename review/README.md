# Reviewing the Constitution in pieces

The CC is one document (eight Parts, about 440 numbered sections, 405 register rows, four formal models). Nobody can review that whole, so CIRISConstitution#72's ask — reviewers with standing to kill sections — has never been met. This directory cuts the document into ten reviewable pieces without changing a word of it.

## The pieces

`pieces.tsv` is the map: one row per piece, with the decimal-id prefixes it includes and excludes, extra files, the `formal/` models that witness it, and the reviewer profile with the standing to kill. `tools/build_review_piece.py` assembles a piece into a self-contained packet under `packets/`: the sections' text, the claims-register slice with status counts, the open tickets the staged rows name, and the checked names in the formal models. Packets are generated; edit the sources.

| Piece | Scope | Reviewer |
|---|---|---|
| P00 | The guarantees (this directory's `pieces/00_guarantees.md`) + the plain rules + the operator digest + the status quo (`pieces/00_status_quo.md`, what the alternatives do, promise by promise) + executive summary + scope | any reader; the entry piece |
| P01 | Part 1 foundation and ethics, Part 7 lifecycle, 8.7 narrative | ethicist |
| P02 | Part 2 grammar | wire-protocol engineer |
| P03 | Part 3 namespace (not 3.2) + registry manifest | schema / registry engineer |
| P04 | 3.2 trust root, 4.2 accord and halt, 4.3 wise authorities | distributed systems + governance |
| P05 | 4.1 anti-patterns, 4.4 composition and delegation | authorization / graph |
| P06 | 4.5 governance discipline: moderation, redress, child safety, purge | trust and safety + legal |
| P07 | Part 5 transport and privacy + 1.13.3 adversary model | cryptographer / network |
| P08 | Part 6 coherence mathematics | mathematician (the original #72 scope) |
| P09 | Part 8 appendices: glossary, concerns ledger, references, annexes, stubs | editor + review coordinator |

Every register row maps to exactly one piece (`build_review_piece.py --check`; the one non-decimal row, `corpus`, is assigned to P09).

## The rule the pieces are reviewed against

Guarantees are written once for human and AI participants alike. No one stands above anyone: rights do not come from what others sign about you, trust does, and no human's rights or trust turn on any finding about what they are. What differs is decided by three facts, none a scale: kind (a made system accepts a root, discloses itself, has no vote), stewardship (a key that cannot accept for itself is held by an accountable human), and evidence of experience (CC 7.5.5 welfare duties on the holder). The halt is the one asymmetry that does not lift, because consent requires revocability and revocability requires a halt authority outside the system being halted (CC 1.5, 1.13.2). An AI is not a human and does not become one; no finding about an agent removes a person's agency over what acts for them. A reviewer in any piece may kill text that gates a duty or a guarantee on substrate where it should gate on one of the three facts, that ranks one participant above another, or that likens an agent to a child.

## Protocol

1. **Packet.** `python3 tools/build_review_piece.py Pnn` produces `packets/Pnn.md`. The packet is what the reviewer gets, plus the PDF for context.
2. **Standing.** The reviewer profile in `pieces.tsv` states what the reviewer may kill. Standing is within the piece; a cross-piece dependency is listed in the packet's scope block and goes to the other piece's reviewer.
3. **Findings.** Each finding is one of: `KILL` (the text is removed or demoted to informative), `AMEND` (text changes; a ruling is filed on a CIRISConstitution issue in the steward's words), `HOLD` (the text stands; the finding is answered on the record), `RECORD` (the text stands and the weakness is written into CC 8.3 as a standing weakness).
4. **Resolution.** Every finding is resolved before the piece is marked reviewed in `pieces.tsv` (a `reviewed_at` column is added at first use). The CHANGELOG names the reviewer, the piece, and the counts by disposition.
5. **Re-review.** A piece is re-reviewed when its sections change under a MAJOR bump or when its register slice loses an established row.

## Volumes (#123)

Each piece names the #123 volume it feeds (`volume` column): digest (P00: the user's plain rules and the operator digest), charter (P01), wire (P02, P07), dictionary (P03), constitution (P04: admission, standing, root, accord, halt, roster, the Wise, amendment and the register of declared power, gathered in one packet; P06 the governance discipline), policies (P05), maths (P08), register (P10: every claim rendered with its status, artefact and pin; P09 the appendices and concerns), threats (P07, P09). `--check` now also fails if any claim is owned by other than exactly one prefix piece. Not yet done from #123: `build_pdf.py --volume`, the eight covers, the glossary first-use gate and the term budget, the which-means sentences.

## Mutants against the promises

`review/mutation_plan.md` — the rc9 opening item: five mutant layers (spec twin, wire must-reject vector, program mutant joined to the claim id, conduct battery, CSD/3 surface) per plain rule, with the boundary stated per rule.

## Status

Scaffolding only. No piece has been reviewed. P00 is drafted; its five rulings (R1–R5) were made 2026-10-11 (#168) and landed. P03 at ~49k words is too large for one reviewer and should be split at 3.1 / 3.3+3.4+3.5 before commissioning.
