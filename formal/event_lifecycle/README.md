# `formal/event_lifecycle` — view, queue, row, view

**The question.** A client renders a view and a queue (CC 4.5.13). How does the view make the queue?

**The answer, proved.** The queue is the door run forwards. For an object the person can see, the node holds the object's family, its lifecycle state, and the person's standing toward it (the roles folded from held rows: author, subject, member, moderator, founder, steward, holder, witness). A family's lifecycle is a list of transitions, each a verb with the state it leaves and reaches, the roles that may sign it, its governance policy and whether it widens. The queue is the transitions enabled for this viewer in this state, one item each; an item's writes are the row that transition signs; the admission door is the same predicate.

**The model** (`EventLifecycle.lean`, Lean 4 core, no Mathlib). `admits` is the door; `enabled` filters a family's transitions by it; `queue` maps them to items; `answer` performs an item's rewrite.

**Proved.** `queue_sound`: every item is a transition the door admits. `queue_complete`: every transition the door admits is an item. `door_is_queue`: the two are one predicate. `preview_is_execution`: for every item in the queue, the view it previews is the view the door produces when the row arrives; `refused_previews_nothing`: a row whose item was not offered produces nothing at the door (the state processor of CC 4.5.13, one function run three ways). `stranger_sees_nothing`: no standing, no queue. `answered_item_leaves_queue`: an item that moved the state is gone from the next view's queue, so the life closes. `widening_is_confirmed`: P8 fires exactly on widening items. A worked room post: the author sees withdraw, recant and vote; a member sees the vote; a moderator sees the withhold; a stranger sees nothing; after the author withdraws, the author's queue is empty.

**Holon and CEWPOS.** A view is a unit, its rows and atoms are its bonds, the queue is the set of rewrites this holder may perform, and answering an item is the rewrite. P7 is the state, P9 an enabled rewrite, P8 an enabled rewrite that widens, P4 the row written, P3 and P11 the bonds.

**What it does not model.** The fold from rows to standing and atoms (`formal/family_model` and the chapter models hold those); the policy's own machine (`formal/two_path`, `formal/moderator_election`); the transitions of every real family: `tools/build_transitions.py` derives them from the family model manifest into `manifests/transitions.json` (draft 0: one row per family and verb, with the states of CC 2.4.1.1, roles mapped from the signer rule, the policy from the governance row, and every cell with its source), which is the table a node's queue generator reads.

**Run.** `lean -M 6000 -T 200000 EventLifecycle.lean` (exit 0, no `sorry`).
