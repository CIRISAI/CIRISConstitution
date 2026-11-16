# `formal/ceremony` — the edition-2 ceremony

**The point.** The ceremony moves the mesh from the earlier signed object (CC 8.11) to the one of CC 2.6.1, once.
It is a wire break: a node that has not upgraded is off the mesh afterwards. After the ceremony row, an earlier-form
object counts only in that row's causal past (CC 2.6.1.12). Every key is carried over by its own holder
(CC 2.4.1.1). This folder states the ceremony as an ordered procedure and checks it.

**The procedure.** [`CEREMONY.md`](CEREMONY.md): the preconditions per implementer, the roles, sixteen steps with
what each row names and what a node that holds it concludes, the causal structure, what each participant sees,
failure and abort, and the open details, ranked. [`TEXT_PROPOSALS.md`](TEXT_PROPOSALS.md) gives the sentences the
Parts would need, each marked derived or needing a ruling.

**The model.** `ceremony.py`, over the kernel's own functions (`formal/causal_kernel`: `kept`, `ancestors`,
`frontier`, and key_end's door for a key record). A small world: an earlier-form lineage (a genesis, three accord
holders, two seats, a community of three persons and an agent, the agent's steward, a key that revoked itself), the
ceremony's rows, and rows after it. Worlds vary the holders' paths (the same halves, fresh halves, both, never), the
re-binds, the bundle's transit rows, the agent's bindings, a second ceremony row, and halts. Three readers read each
world: upgraded with no pin, upgraded and pinned, and not upgraded. Each property's expected answers are written by
the world builder from how the world was made, never by the model.

**What is checked** (`check_ceremony.py`, compared with `ceremony_expected.tsv`):

| | Property | Planted breaks, each caught |
|---|---|---|
| P1 | an earlier-form row counts iff it is in the ceremony row's past, in every arrival order | an earlier row's own references extend the past; a signed instant decides; arrival decides |
| P2 | a key is live in this form iff it has a key record of this form, and no row of another key makes it live or ends it | the ceremony carries keys; a naming row revives; an earlier revocation is ignored; a third party ends a key |
| P3 | a key that never re-registers has no standing after and loses nothing in the past | silence retires; a signed instant decides; earlier rows dropped at the cut |
| P4 | no single device yields a halt | one half verifies; an earlier-form halt outside the past is honoured |
| P5 | a seat has at most one transit key in force, the one the holders' count authorised | a seat's own binding; a one-holder re-bind; a re-bind outside the past; a pick between two keys |
| P6 | two ceremony rows are a fork: tips to a reader with no pin, the other void to a reader that pinned | the union of pasts; a pin ignored |
| P7 | the accord's count is unbroken: the same persons, the same count, never fewer, at every point | keys counted in place of persons; the roster shrunk to the keys re-registered |
| P8 | an agent has a steward at every point across the cutover | no continuity from the earlier key; acting without a steward |
| P9 | the result does not depend on the order a node receives the rows | arrival decides; the first ceremony row to arrive wins |

All nine hold, and all 24 planted breaks are caught. 71 worlds, 16 arrival orders each, 4,622 answers, under two
seconds.

**The interleavings** (`Cutover.tla`, run by `run_tlc.sh` under TLC v1.7.4). The world signs in any order the rules
allow: the holders' records, a user's record, the acknowledgement, a late earlier row, the ceremony row, one halt
(of either form, the earlier one fired in the window), and its resumption's statements. Two nodes receive the rows
one at a time, one of them nothing until the ceremony row is signed. Each node updates its state as an
implementation does, one arrival at a time, and every state is checked against the function of the rows it holds.

| Configuration | Result |
|---|---|
| `Cutover.cfg` (the halt of the earlier form) | closes: 840,819 distinct states, `Inv_P1`, `Inv_P2`, `Inv_P7`, `Inv_P9`, `Inv_HaltPathOpen`, `Inv_LatchOnlyByResume`, `Inv_NoStranded` |
| `Cutover_forward.cfg` (the halt of this form) | closes: 954,840 distinct states |
| one twin per break | `NoRecheck` fails `Inv_P9`, `ByInstant` fails `Inv_P1`, `CeremonyCarries` fails `Inv_P2`, `EarlierAfterCut` fails `Inv_P7`, `CutWithoutRecords` fails `Inv_HaltPathOpen`, `CutClears` fails `Inv_LatchOnlyByResume` |
| the text's gap | `ResumeNeedsHonoured` fails `Inv_NoStranded`: a resumption read as counting only for a halt still honoured strands a latch |
| a finding | `Inv_ResumeStable` fails in the model that closes: a resumption counted on an earlier-form statement loses its count when the ceremony row arrives |

The full run takes about two and a half minutes on two workers.

**What it found.** Fifteen findings, each computed from a run and listed in the expected table. The ones the text
does not answer:

- an earlier row that a carried earlier row refers to, and that no `carried` root holds, is outside the past (F1);
- a halt sealed in the earlier form and published after the ceremony row is refused (F2);
- an earlier row concurrent with the ceremony row counts at a node until it holds the ceremony row (F3);
- a seat with no re-bind in the past and no binding in the bundle has no transit key (F4), and so does one whose two
  authorised keys differ (F5);
- with every holder required, one holder who never re-registers blocks the ceremony row (F7);
- an earlier acceptance edge in no carried root leaves an agent unable to act (F9);
- an owner's revocation of a key it owns does not end the key under the liveness sentence of CC 2.4.1.1 (F13);
- an earlier owner-binding the ceremony does not carry leaves the agent with no steward from the ceremony row until
  a binding of this form (F14);
- an earlier-form halt fired after the acknowledgement stops counting at the ceremony row, while its latch stands
  (F15).

**What it does not model.** Bytes, signatures and encodings: a signature is a set of halves. The transport: a link
is not modelled, and the handshake switch is read from whether a node has upgraded. Windows and the fuse: those are
`formal/accord_halt`. A roster change or a recovery of the accord: their forward form is not yet stated. More than
one community, more than one agent, more than two seats. Arrival orders are sampled, 16 for each world; the TLA+
spec covers every interleaving of its smaller world.

    python3 -I formal/ceremony/check_ceremony.py           # compare with ceremony_expected.tsv
    python3 -I formal/ceremony/check_ceremony.py --write   # write it
    bash formal/ceremony/run_tlc.sh /path/to/tla2tools.jar
