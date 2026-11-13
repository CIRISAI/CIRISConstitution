# `formal/causal_kernel` — the kernel, running

**The point.** `formal/causal_order` proves that what a node concludes is a function of the rows it was
offered, with no rank. This package is that kernel as code, run against every arrival order of small worlds and
against the seventeen cases where the rule tables give two results from one set today.

**The kernel** (`causal_kernel.py`, `cut.py`). A row has a digest, a kind, a signer and the digests it names.
The only order is what rows name.

| Layer | Function | What it reads |
|---|---|---|
| kept | `kept` | the row alone, and whether what it names is kept |
| concluded | `concluded` | the row against its ancestors |
| derived | `wins`, `slot`, `tally`, `reach`, `means`, and the cut | conclusions over a set of rows |

**The cut.** A cut is a row on a slot signed by whoever may conclude that slot. Once a cut counts, the rows on
its slot that are concurrent with it do not count. Rows in its past stand, and rows that name it are judged at
the head they name. A removal is a cut on a key. A deciding row is a cut on a contest. Two concurrent cuts on
one slot that say different things contest each other, and neither counts until a row names both.

**What is checked** (`check.py`, `check_cut.py`).

- Every set of up to six rows from two pools, in every arrival order: 6,606 sets, 2,182,671 orders, one answer
  each. Renaming the digests renames the answers and changes nothing else.
- Six statements of `formal/causal_order` as properties, each with a mutation that must be caught: the
  conclusion layer is final; a new row reaches only itself, its descendants and concurrent conflicts; only a
  removal stops a row counting; only a withdrawal removes meaning; a row first held after a removal never
  counts; a row with no path to the reader concludes nothing for it.
- The seventeen cases of `formal/derivation/order/witnesses.tsv`: one result in every order here, two results
  when judged on arrival. `witness_runs.tsv` records each run and what the adversary in it gains.
- Under the cut: 4,898 sets in 440,291 orders, one answer each. After a counting cut is on a slot, no row by
  a key that may not cut that slot changed it.

**Standing, windows, copying and keys** (`seat.py`, `roles.py`, `window.py`, `route.py`, `keyplane.py`,
checked by `check_lock.py`).

- **The seat.** An offer and an acceptance, with the conferrer as one parameter. 2,774 sets in 701,176 arrival
  orders, one answer each. `role_shapes.tsv` writes the 23 role names of the tables as parameters of three
  shapes; 222 instance checks pass. Over a community the founding record seats duty holders, who are equals
  (CC 4.5.4): a duty seat is conferred by a strict majority of them or by the lone holder, and withdrawn by a
  strict majority of the others, never on fewer than two voices.
- **The window.** A receipt, a landing, and three rules for an answer concurrent with the landing, run against
  the self-roster lone path, the moderation fallback and the halt fuse. `window_adversary.tsv` is the table:
  recount breaks none of twenty checks.
- **Copying as need.** A party given only its routed rows concludes the same as one given everything; a
  stranger is routed nothing.
- **A writer's keys.** The key plane re-read from rows on the writer's own chain agrees with
  `formal/key_plane` on 402,950 comparisons.

**Attacked** (`attacks.py`, `check_attacks.py`, `attack_expected.tsv`, `checkpoint.py`). Thirty-four attacks,
thirty-three from the published failures of comparable systems, each with the class it must fall in: the attacker gains
nothing, the limit is one `formal/KERNEL.md` states, or the scenario cannot be expressed here. The check fails
if any attack gains what is not conceded, or if any scenario gives two answers in two arrival orders.

`checkpoint.py` holds two rules that are part of the kernel, a counted row counting only if what it is built on
counts and a reader's own acknowledged line, and one that is not: a counted row leaving behind acts that name
only older heads. That one is off unless asked for, and the attacks run it both ways to show why. It makes the
longer line win.

**A private room seats voices** (`roomkey.py`, `check_roomkey.py`). A community declares its membership private
or public. A private room's roster seats a voice, a small counted roster of room keys made for that room, and
every row of the room is signed under a room key. That a voice is a given person's is a binding: never a row,
made for one addressee, opened against a commitment on the key's seat row. The kernel is not changed.

- Every named answer for a room of 34 rows is the same over voices as over identity keys: 691 sets of rows,
  22,468 answers in two arrival orders, none differ. A reader that breaks a tie by key name is caught.
- A tally over voices equals the count of persons in each of 1,728 ways for devices to vote. A count of keys is
  wrong in 1,216 of them.
- Five ways to make the binding. The planned one, two encapsulations and no signature, is forged by 0 of 180
  coalitions and lets 0 of 14 prove anything outside. An identity signature lets 14 of 14.
- A count of persons is missing at a node for exactly the bindings it lacks: 20,736 pairs of nodes, none that
  hold every binding disagree. Without the commitment two members make honest nodes count differently in 108 of
  243 votes. With it none do, and the node told otherwise waits and names the key.
- Under identity keys a carried reply proves all four members. Under room keys none of 657 sets of rows of the
  room proves or names a person.
- Detection in a private room: the detector's seat is conferred inside the room by the act that enables the
  list, the owner-binding of the node's room key is a row of the room, and the record names no person.
- The declaration: an absent member reads public, a self room and a family are seated by identity keys, and no
  sequence of later declarations takes a room from public to private.

The verdicts on the binding are symbolic: a fact has a set of parties able to make it, and a party is
convinced when nobody else but the person could have. Nothing here is proved in Lean. The check prints ten
limits and marks each as run or as stated from outside the model.

**One roster, five instances** (`roster.py`, `check_rosters.py`, `roster_expected.tsv`). A person's keys, a
voice's room keys, a room, the accord and an infrastructure community run on one mechanism: a lineage of counted
versions, each naming the head it extends. The instances differ by parameters read from the policy table and the
text. The check runs 77 properties that each instance's own model or text claims, over every arrival order up to
a cap of 400, each with a deliberate break that must be caught. Nothing here is proved in Lean. The plain
mechanism was wrong in four places, and a stated parameter restores each:

- One signature removed a member under a one-voice protocol. The floor of two voices now sits under every protocol.
- An invitation by one member never seated anyone. The joiner's own yes now counts toward the window's floor.
- A member who left was seated again on its old acceptance. An acceptance is spent once its key has left. The
  text says a key is not seated twice; "once it has left" is this model's reading.
- An agent's self roster ran the person's lone path. That path is for a person's roster only.

Two limits. The accord's rule that a removed holder no longer fires needs a latch at the node's receipt, which
reads arrival order and is not a function of the rows. The parameters for removing a key from a voice are
guessed, since the text states only how a voice's keys are seated.

**One door, every policy row and clock** (`door.py`, `check_door.py`, `doors.tsv`, `door_expected.tsv`). The
door is the window of `window.py` with its parameters named: who opens, who answers, the answer kinds, the
length, the clauses read at once or at the close, whether a late answer counts, the target's silence and who
concludes. All eighteen policy rows are built from their own cells, and further instances cover ten clocks and a deferral's own end.
`doors.tsv` holds one row for each instance, with a column for what the tables do not state. Eleven instances
read who concludes, with which row and whether a late answer counts from the `land` entries of
`manifests/reactions.json`. The check records 204 verdicts and exits on any difference, any break that is not caught and any difference between
arrival orders. Rooms are of three and four keys. Nothing here is proved in Lean.

**Two notions of time** (`check_time.py`, `time_expected.tsv`). A row's own stated end, and a window with a
landing. The check builds 86 worlds of two rows and looks for two worlds that the two notions and the naming
cannot tell apart and that a reading sends to different results. Six readings are covered. Two need an instant
as written and have a replacement. Two are not covered and are recorded with their witnesses: a cosignature
attached against the node's clock at first receipt, and a session held by the earliest claimed instant.

**A shape for every family** (`check_shapes.py`, `claim.py`, `shapes_expected.tsv`, and the table
`formal/derivation/family_shapes.tsv`). Each of the 184 families is run as an instance of its shape, with every
parameter traced to a table cell or a quoted sentence and each quote checked against the section it cites.
`claim.py` states a claim and content over the kernel's layers. The check also removes the shapes in three
orders and records which survive. Three made-up families that fit no shape must be reported as not fitting.

**What it shows that the proof does not.**

- Only the conclusion layer is final. A slot, a count and a roster are functions of the rows, and a later row by
  a key with standing on that slot can still change them.
- Two cuts by keys of equal standing that undo each other stay contested. What settles it is a voice the other
  cannot remove, which is a property of the count and not of the cut.
- A window closing unopposed and the lapse of an unconfirmed halt are not expressible from rows.
- A merge of roster tips is written here and is not in the shared library.

Run: `python3 -I formal/causal_kernel/check.py` (add `--bound 5` for a short run),
`python3 -I formal/causal_kernel/check_cut.py`, `python3 -I formal/causal_kernel/check_lock.py`,
`python3 -I formal/causal_kernel/check_attacks.py`, `python3 -I formal/causal_kernel/check_roomkey.py` and
`python3 -I formal/causal_kernel/check_rosters.py`, `python3 -I formal/causal_kernel/check_door.py` , `python3 -I formal/causal_kernel/check_time.py` and `python3 -I formal/causal_kernel/check_shapes.py`
