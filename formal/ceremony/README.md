# `formal/ceremony` — the genesis of this edition, a clean mesh

**The point.** This edition begins a new mesh with a fresh genesis of the signed object of CC 2.6.1. Nothing of the
earlier mesh comes across: no row of this form names an object of the earlier form (CC 8.11), and no earlier object
gives standing to anything (CC 2.6.1.12). Every key record, binding, community, edge and pre-signed halt is signed
anew. This folder states the ceremony as an ordered procedure and checks it.

**The procedure.** [`CEREMONY.md`](CEREMONY.md): the preconditions, the roles, eleven steps with what each row
names and what a node that holds it concludes, what each participant sees, and failure and abort.

**The model.** `ceremony.py`, over the kernel's own functions (`formal/causal_kernel`: `kept`, `ancestors`,
`frontier`, and key_end's door for a key record). A small world: an earlier mesh (holders' earlier keys, an earlier
genesis, a community, an agent's earlier binding, an earlier edge, re-bind, sealed halt and votes) and a mesh of this
form signed anew. Worlds vary who signs the genesis, a second genesis, the re-binds, a seat's own binding, the agent's
binding and edge, revocations, and when the pre-signed halts are sealed. Three readers read each world: upgraded with
no pin, upgraded and pinned, and not upgraded. Each property's expected answers are written by the world builder from
how the world was made, never by the model.

**What is checked** (`check_ceremony.py`, compared with `ceremony_expected.tsv`):

| | Property | Planted breaks, each caught |
|---|---|---|
| P1 | no earlier-form row counts for anything, in any arrival order | earlier rows accepted until the genesis; an earlier row a row of this form names |
| P2 | a key is live only by its own record of this form, and only its three revokers end it | an earlier record; a naming row revives; a third party ends; an owner's revocation ignored |
| P3 | the accord's count holds from the genesis, which every holder signs | a genesis on a majority; the roster shrunk to live keys; earlier votes counted |
| P4 | no single device yields a halt | one half verifies; an earlier halt honoured |
| P5 | a seat is canonical by the genesis's count and has one transit key from it, moved only by the holders' count | a seat's own binding; a one-holder re-bind; a pick between two keys; an earlier re-bind; a node that claims canonical standing for itself; standing that ends with the seat's record |
| P6 | an agent has no standing until its steward-binding of this form exists | an earlier binding; acting without a steward; an earlier community |
| P7 | two geneses are a fork: tips to a reader with no pin, the other void to one that pinned | the union of tips; a pin ignored |
| P8 | a halt of this form is available from the first moment after the genesis | the genesis published before the halts are sealed |
| P9 | the result does not depend on the order a node receives the rows | arrival decides; the first genesis to arrive wins |

All nine hold, and all 25 planted breaks are caught: 37 worlds, 16 arrival orders each, under a second.

**The interleavings** (`Cutover.tla`, run by `run_tlc.sh` under TLC v1.7.4). The world signs in any order the rules
allow: the holders' records, their sealed halts, the genesis (published only once the halts exist), a user's record,
the resumption's statements, and rows of the earlier mesh. Two nodes receive the published rows one at a time, one of
them nothing until the genesis is signed, and each updates its state as an implementation does. `Cutover.cfg` closes
at 1,250,135 distinct states under `Inv_P1`, `Inv_P2`, `Inv_P7`, `Inv_P9`, `Inv_HaltAvailable`, `Inv_HaltPathOpen` and
`Inv_NoEarlierLatch`. Seven twins each fail their own invariant: `AcceptEarlier` (P1), `ArrivalEarlier` (P9),
`CeremonyCarries` (P2), `EarlierVotes` (P7), `PublishUngated`, `CutWithoutRecords` and `EarlierHalt`. The run takes
under a minute on two workers.

**What it does not model.** Bytes and encodings; the link itself; windows and the fuse (`formal/accord_halt`); a
roster change or a recovery of the accord, whose forward form is not yet stated; more than one community, one agent
and two seats. Arrival orders are sampled in Python; the TLA+ spec covers every interleaving of its smaller world.

    python3 -I formal/ceremony/check_ceremony.py           # compare with ceremony_expected.tsv
    python3 -I formal/ceremony/check_ceremony.py --write   # write it
    bash formal/ceremony/run_tlc.sh /path/to/tla2tools.jar
