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

- **The seat.** An offer and an acceptance, with the conferrer as one parameter. 2,727 sets in 587,536 arrival
  orders, one answer each. `role_shapes.tsv` writes the 23 role names of the tables as parameters of three
  shapes; 215 instance checks pass.
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

**What it shows that the proof does not.**

- Only the conclusion layer is final. A slot, a count and a roster are functions of the rows, and a later row by
  a key with standing on that slot can still change them.
- Two cuts by keys of equal standing that undo each other stay contested. What settles it is a voice the other
  cannot remove, which is a property of the count and not of the cut.
- A window closing unopposed and the lapse of an unconfirmed halt are not expressible from rows.
- A merge of roster tips is written here and is not in the shared library.

Run: `python3 -I formal/causal_kernel/check.py` (add `--bound 5` for a short run),
`python3 -I formal/causal_kernel/check_cut.py`, `python3 -I formal/causal_kernel/check_lock.py` and
`python3 -I formal/causal_kernel/check_attacks.py`
