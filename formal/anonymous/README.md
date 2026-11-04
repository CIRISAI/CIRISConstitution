# `formal/anonymous` — anonymous participation, and what still stops abuse

**The question.** CC 5.4.6 item 1 (rc17) makes using the Anonymous Tier and being anonymous one thing: a mode of a node, a separate dedicated identity, unannounced, anonymous from its first run or never, confined to the row plane, in rooms only once rooms ride the tier. Does that hold on every trace, and what controls abuse by a key that costs nothing to mint?

**The model** (`Anonymous.lean`, Lean 4 core, no Mathlib). A world of nodes (announced or anonymous), pseudonyms (each belonging to an anonymous node) and one flag, whether rooms ride the tier. Thirteen events, each with a guard that is the text's rule and one row it writes; a trace runs every event whose guard holds and drops the rest, so every theorem covers adversarial traces (a forged link, a pseudonym trying to be appointed or to vote, prohibited content under a pseudonym).

**Proved, as one invariant `Inv` over every run (`inv_holds`) and its corollaries:**

- `anon_never_announced`, `anon_route_never_held`, `anon_never_direct`: an anonymous node never announces, nobody ever holds its route, and it is never in a direct contact (item 10).
- `anon_in_no_room_until_then`, `anon_room_always_via_tier`: until rooms ride the tier an anonymous node is in no room; after, only over the tier.
- `link_only_by_proof`, `forged_link_is_one_signature`: a row that links an anonymous identity to an announced one under both keys exists only by the person's own act; anyone else's claim lands signed by one key.
- `pseud_holds_nothing`, `seat_never_anonymous`: a pseudonym holds no duty and casts no vote, and a seat is never anonymous: pseudonyms are free to mint and worth nothing to mint, so Sybil pseudonyms buy no governance and no moderation.
- `gate_blind_to_signer`, `block_hides_pseudonym`, `tombstone_hides_item`: the admission gate, a reader's block and a moderator's tombstone act on a pseudonym's rows exactly as on anyone's.
- `all_anonymous_room_needs_anonymous_moderator`: with the existence gate of CC 4.5.4 and no anonymous duty holders, a room whose every member is anonymous never operates, on any trace; `anonymous_room_operates`: with anonymous duty holders allowed, one anonymous founder founds and runs a room; `anonymous_moderator_is_an_identity`: whoever holds the duty is a persistent identity, never a pseudonym, so it can be blocked, contested and revoked like any holder.
- `public_room_needs_announce`: a public room (open admission at the Commons tier) admits announced keys only, so no anonymous or unannounced identity ever sits in one.
- `no_hop_sees_both_ends`: on a three-hop route no relay sees both the publisher and the store; the mailbox seat learns a count (item 8).

**What it does not model.** Timing correlation between a pseudonym's activity and a person's other traffic (the tier's anonymity set, item 8, is a residual the text states). The census (an anonymous node sends returns like any node; pseudonyms have none). Whether an anonymous node may hold a duty is the world's `anonDuty` switch, so both answers are modelled; the text takes `true` (CC 5.4.6 item 1, ruled 2026-11-04), because the forcing theorem shows the alternative leaves anonymous participants no room.

**Run.** `lean -M 6000 -T 200000 Anonymous.lean` (exit 0, no `sorry`).
