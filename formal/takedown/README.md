# `formal/takedown` — takedown and erasure of one blob at one node

**The point.** CC 4.5.3 gives nine bases for removing content: five destroy on receipt, four withhold for a
window and destroy at its close. CC 4.5.13 lets the members lift a moderator's act, CC 4.5.5 lets a reversal be
admitted, and CC 4.4.3.2.8 lets a court freeze a record. Five readings of the text found twenty-two conflicts
among those rules. This model states them once, as a fold over the rows a node holds, and checks them together.

**The model.** `takedown_model.py`. One blob, one node. The node holds rows about the blob, each with the instant
it first held it: a notice on a basis, a reversal, a lift, a hold, a hold lifted. The blob's state at an instant
is `fold(rows held, instant)`: served, withheld or destroyed. Nothing is stored beside the rows.

The bases and their windows are not written in the model. It reads them from `manifests/reactions.json` and the
constants table, and refuses to run if a windowed basis lacks a stop on admission, a named window or a
destruction at the window's close.

**What is checked**, over every set of up to three rows at every arrival instant (1,092 cases):

| | Property |
|---|---|
| P1 | a windowed notice withholds from the instant it is held and never before, unless a reversal or a lift is already held |
| P2 | a windowed notice destroys at the close of its window unless a reversal or a lift was held inside it |
| P3 | an immediate basis destroys at the instant it is held; under a live legal hold it withholds at once and destroys when the hold lifts |
| P4 | destruction is final: no row held later brings the blob back |
| P5 | the state is a function of the rows held and their first-held instants |
| P6 | a blob under a live legal hold is not destroyed |

**Legal hold.** A live hold defers destruction and never serving: the bytes are withheld from everyone at once and destroyed when the hold lifts (CC 4.5.3). The model first ran this both ways, since the text did not say (conflict C312); the steward ruled on 2026-11-12. The reading in which a hold defers nothing is still run and must fail P6, so the two stay told apart.

**What it does not model.** Who may sign each row (the signer gate, `tools/check_signer_gate.py`); what a
restored item looks like to a viewer (the consent gate of CC 4.5.13); more than one node (each node runs its own
windows from its own first-held instants, CC 4.5.13, so two nodes may differ until their windows close); the
deletion deadline a producer owes a subject (CC 3.3.1), which is `formal/deletion`.

Run: `python3 formal/takedown/takedown_model.py --check`
