# `formal/anonymous` — anonymous participation, and what still stops abuse

**The question.** CC 5.4.6 item 1 (rc17) makes using the Anonymous Tier and being anonymous one thing: a mode of a node, a separate dedicated identity, unannounced, anonymous from its first run or never, confined to the row plane, in rooms only once rooms ride the tier. Does that hold on every trace, and what controls abuse by a key that costs nothing to mint?

**The model** (`Anonymous.lean`, Lean 4 core, no Mathlib). A world of nodes (announced or anonymous), pseudonyms (each belonging to an anonymous node) and one flag, whether rooms ride the tier. Thirteen events, each with a guard that is the text's rule and one row it writes; a trace runs every event whose guard holds and drops the rest, so every theorem covers adversarial traces (a forged link, a pseudonym trying to be appointed or to vote, prohibited content under a pseudonym).

**Proved, as one invariant `Inv` over every run (`inv_holds`) and its corollaries:**

- `anon_never_announced`, `anon_route_never_held`, `anon_never_direct`: an anonymous node never announces, nobody ever holds its route, and it is never in a direct contact (item 10).
- `anon_in_no_room_until_then`, `anon_room_always_via_tier`: until rooms ride the tier an anonymous node is in no room; after, only over the tier.
- `link_only_by_proof`, `forged_link_is_one_signature`: a row that links an anonymous identity to an announced one under both keys exists only by the person's own act; anyone else's claim lands signed by one key.
- `pseud_holds_nothing`, `seat_never_anonymous`: a pseudonym holds no duty and casts no vote, and a seat is never anonymous: pseudonyms are free to mint and worth nothing to mint, so Sybil pseudonyms buy no governance and no moderation.
- `gate_blind_to_signer`, `block_hides_pseudonym`, `tombstone_hides_item`: the admission gate, a reader's block and a moderator's tombstone act on a pseudonym's rows exactly as on anyone's.
- `no_hop_sees_both_ends`: on a three-hop route no relay sees both the publisher and the store; the mailbox seat learns a count (item 8).

**What it does not model.** Timing correlation between a pseudonym's activity and a person's other traffic (the tier's anonymity set, item 8, is a residual the text states). The census (an anonymous node sends returns like any node; pseudonyms have none). Whether an anonymous node may hold a duty once rooms ride the tier: the model's guard requires an announced holder, which is the conservative reading and is flagged to the steward.

**Run.** `lean -M 6000 -T 200000 Anonymous.lean` (exit 0, no `sorry`).
