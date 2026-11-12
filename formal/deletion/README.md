# `formal/deletion` — the deletion deadline a producer owes a subject

**The point.** A producer that commits to `consent:deletion_sla:{days}` owes the subject a deletion within that
window once the subject revokes or withdraws (CC 3.3.1 D1, CC 4.4.3.5.2). The rule turns on whose act a row is:
the subject's act starts the window, only the producer's act ends the duty, and an attestation of deletion is
evidence and never the deletion. A reading of the text found the breach sentence and the typed rule disagreeing
on exactly that point (conflict C525 of `formal/derivation/text_conflicts.tsv`).

**The model.** `deletion_model.py`. One row about one subject at one node. The node holds acts against the row,
each with the instant it first held it. The verdict at an instant is `fold(rows held, instant)`: no window,
running, met or breach. Nothing is stored beside the rows.

**What is checked**, over every set of up to three acts at every arrival instant (2,905 cases):

| | Property |
|---|---|
| D1 | breach exactly when the window has closed with no composer of the producer's held inside it |
| D2 | a `consent:deletion_complete` row changes no verdict |
| D3 | the subject's own act starts the window and discharges nothing |
| D4 | a composer of the producer's held inside the window means no breach at any later instant |
| D5 | a breach is final: a composer held after the close does not undo it |
| D6 | the verdict is a function of the rows held and their first-held instants |

**Held to the data.** The model reads the deadline from `manifests/reactions.json`: the events that start the
clock and the events that excuse the breach, each with the actor it names. The manifest's rule is run over the
same cases and must agree in every one. An excusing withdrawal that names no actor fails the check in 579 cases,
291 of them a missed breach. The reaction grammar gained the actor word (`withdrawn(target,producer)`) for this.

**What it does not model.** Who emits the breach record and that it is emitted once (CC 3.3.1 D2, the one-emitter
check of `tools/build_reactions.py`); what follows a breach (D3: evidence, never a verdict); the bytes a producer
keeps outside the record, which no row can show; takedown by notice (`formal/takedown`).

Run: `python3 formal/deletion/deletion_model.py --check`
