# `formal/alm` — the member relay tree, layered

**Status: a model of CC 6.1.6 and of the two additions ruled 2026-11-08 (CC 5.3.3.2).** The structure theorems run on a worked instance; the quantitative theorems are general. Core Lean 4, no Mathlib; the companion `alm_model.py` carries the same numbers to any input and `--check` keeps the two one model.

**The question.** CC 6.1.6 pins the live tree as a contract: a deterministic, integer-only function of the signed snapshot, the publisher the binding names at depth zero, seats and forwarders never in it. The steward asked for two features: a phone streams once through low-bandwidth peers that each carry a layer and pass it on, the stream reassembling where the layers meet; and ten thousand senders live in one call down to a presence tile. Are these the tree as written, an addition, or a new wire?

**The answer.** An addition of rule, not of wire: *per-layer parents* (a member takes each layer from a different parent), *sibling pull* (a chunk the parent did not deliver is pulled from a sibling), and a *presence floor layer* per codec class with *budget ÷ senders*. Rateless repair under the sealed chunk is a separate question whose break-even the model states; with the assumed 0.1–2 % per-hop loss (edge: a sweep, not a measurement; leviculum#102 will measure), refetch is the cheaper repair to depth 5.

**Proved.**

- `tree_permutation_invariant`: the same ads in another order give the same tree (CC 6.1.6, byte-equal inputs, byte-equal output).
- `publisher_is_the_only_root`, `seats_and_unverified_outside`, `child_one_deeper`: one root, the publisher; seats and unverified ads nowhere; every child one deeper than its parent, so no cycles.
- `clamp_before_scoring`: an uplink of 50 and one of 40 score alike at the cap (N8): no one buys a slot with a number.
- `per_layer_parents_differ`, `phones_carry_the_base_only`: a member takes the base layer from one parent and the enhancement layer from another; a phone is never a parent for a layer it does not offer.
- `dave_and_frank_are_siblings`, `today_loss_is_final`, `sibling_pull_completes`: under today's tree a lost chunk stays lost; one round of sibling pull restores it.
- `one_percent_five_hops` (49 ‰), `three_percent_five_hops` (141 ‰), `five_percent_five_hops` (226 ‰), `ten_percent_eight_hops` (569 ‰): loss compounds along whole-chunk hops.
- `refetch_cheaper_at_one_percent`, `rateless_cheaper_at_five_percent_past_two_hops`: the break-even of refetch (costs the loss rate) against rateless repair (a fixed ~10 %).
- `striped_upload_is_once`: striping a stream across first-hop peers uploads it once; today's tree uploads fan-out times.
- `presence_floor_keeps_everyone`: `n` senders at the floor within the budget are all live. `ten_thousand_live_on_wifi` (19,531 at 32 B/s on 5 Mb/s), `ten_thousand_do_not_fit_cellular` (1,953), `twelve_senders_today_on_cellular` (12 at today's 5 kB/s base layer).

**What it does not model.** Scoring by RTT or locality (edge-internal by 6.1.6), the retry schedule, the codec's layer rates (the floor rate is an input), and the wire of a symbol envelope, which does not exist. Fan-out is a snapshot field because the constitution pins no number.

**Run.** `lean -M 6000 -T 200000 Alm.lean` (exit 0, no `sorry`); `python3 alm_model.py` prints the tables, `--check` replays the pinned numbers. In CI.
