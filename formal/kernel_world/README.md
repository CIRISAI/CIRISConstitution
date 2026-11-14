# `formal/kernel_world` — the kernel in a world that is the adversary's

**The point.** The kernel is one function: the rows a node holds, each with the instant the node first held it,
give what the node shows and what it must do. A function can be tested on cases. A world has to be explored:
any row may reach any node at any instant in any order, and what matters is what is true in every reachable
state. TLC explores all of them to a bound, so no schedule is left to luck.

**The model.** `KernelWorld.tla`. Two nodes and the rows of one blob under takedown (CC 4.5.3, CC 4.5.13): a
windowed notice, an immediate notice, a reversal, the members' lift, a legal hold and its lifting. The schedule
delivers any row to any node at any instant. A node keeps no state but the rows and their first-held instants.
Destruction is read from them, so the record of an irreversible act is not a second store.

What a node shows is a screen state of `manifests/ui_primitives.json`: `populated`, `withheld` (drawn under a
cover that says on what ground, who acted and when the window closes), `gone`, and `not_on_this_node` (the bytes
were destroyed here and a reversal has since given the row its standing back, so they may be fetched again).

**What is checked.**

| Configuration | Holds in every reachable state |
|---|---|
| `KernelWorld.cfg` (notice, reversal, lift; 86,331 states) | the screen is always one of the four states; a cover always has a notice behind it; the same rows first held at the same instants give the same screen |
| `KernelWorld_hold.cfg` (immediate notice against a hold; 81,924 states) | the same, and a held blob is not destroyed while its hold is live; an immediate notice is never shown |
| `KernelWorld_reach.cfg` | expected to fail: the trace is a world that shows all four states, so none is unreachable |
| `KernelWorld_standing.cfg` | expected to fail: see below |

**What the world found.**

1. *A reversal that outruns its notice.* The first run had a reversal count only if held after the notice it
   answers. A schedule delivered the reversal first, and that node destroyed what the other restored. The rule
   is now: a reversal or a lift held before the window closes voids the notice, whenever it arrived.
   `formal/takedown` carried the same fault and is corrected.
2. *The same rows, different standing, for good.* Once every window has closed, two nodes that hold the same
   rows can still disagree: one held the members' lift inside its window and restored the item, the other held
   it one instant after its own window closed and destroyed it. Each node counts the window from its own
   first-held instant (CC 4.5.13), so the lift's reach depends on the order rows arrived in. No later row
   repairs it. This is the open question the check pins (conflict C565 of
   `formal/derivation/text_conflicts.tsv`): whether a lift is judged at the instant each node held it, or at
   an instant every node reads the same.

**Signed instants.** `KernelWorldSigned.tla` keeps the instant a row is signed apart from the instant a node
holds it, and lets a signer date a row early. Standing is judged at signed instants, and a signed instant is
trusted at a node only where the node first held the row within the freshness bound (CC 3.3.4, CC 4.5.13, the
steward's ruling of 2026-11-12). With every row delivered inside the bound, the same rows give the same standing
at every instant (49,240 states), a lift signed later than the bound after the instant it claims counts nowhere,
and a node never shows as present what it destroyed. `KernelWorldSigned_late.cfg` lets a row arrive later than
the bound and is expected to fail: the node that held the lift in time counts it and the late node does not. That
residue is what a vouched past is for (CC 3.3.4), and it is the one case in which two nodes holding the same rows
may still differ.

**The screen, in the same world.** `KernelWorldScreen.tla` puts a screen on each node: a read that is idle,
pending, failed or answered; the state the reader is shown; and one act the reader is offered, the objection
that lifts a moderator's act. The laws of the screen standard are invariants in every reachable state.

| Law | In the model |
|---|---|
| L2, exactly one state | the screen is always one of seven states |
| L3, an honest zero | an answer is drawn only when the node answered, an error only when the read failed, loading only while it is pending |
| L5, a reasoned refusal | an act that is present and disabled names its reason (the window has closed; already objected) |
| the cover | a withheld item always has its notice behind it |
| L9, nothing unreachable | expected to fail when negated: one trace shows every state and every form of the offer |
| offered is admitted | whenever the screen offers the objection, an objection taken at that instant would count |
| taken takes effect | an objection taken at a node restores the item at that node at once |

"Offered is admitted" is the law that ties the screen to the kernel, and it is where a screen goes wrong.
`KernelWorldScreen_receipt.cfg` has the screen judge the window by the node's own clock, where the kernel
judges it at signed instants. It is expected to fail: a node that held the notice late offers an objection the
kernel would not count. A screen has to ask the kernel whether an act is open, and never compute it again.

**What it does not model.** Who may sign each row (the signer gate); clocks that differ between nodes; more
than one blob; the other families. The module is the pattern: a family's fold, a schedule that is free, the
screen states as the vocabulary of the result. The rest of the rules join it as they are typed.

Run (TLC 1.7.4):
`java -cp tla2tools.jar tlc2.TLC -deadlock -config KernelWorld.cfg KernelWorld.tla`
