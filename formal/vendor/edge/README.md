# `formal/vendor/edge` — edge's quantitative models, vendored

Edge's models of the transport and the mesh, vendored from CIRISEdge branch `docs/fsd-ciris-mesh` at commit `bf383b3` (2026-11-05; local to the machine until edge's release push, which is why the commit and not a tag is named). They are **models, not measurements**: seeded, standard-library Python, run with `python3 -I`, and every figure they print is marked `[inf]` or `[model]` in the FSD beside it. The CC cites them where a residual in the text carries their number.

| Script | FSD | What it models | Where the CC uses it |
|---|---|---|---|
| `transport_tiers.py` | `TRANSPORT_TIERS_MODEL.md` | the three tiers, the eight-link bound, referrals, displacement, seat links, canonical capacity | CC 5.4.3 (the bound, the seat class, referrals); `formal/transport_tiers` |
| `onion_rooms.py` | `ONION_ROOMS_MODEL.md` | rooms over the tier: the cap, the walk, the sticky guard, mailboxes, sync, the trilemma, intersection | CC 5.4.6 (rooms over the tier, the guard, the mailbox by scope, item 8's residuals) |
| `retry_schedule.py` | `EVENT_PATH_MODEL.md` §M8 | refusal memory and re-ask cadence | CC 4.5.13 (a refused row is not a held change) |
| `event_path.py` | `EVENT_PATH_MODEL.md` §M1 | the event path: receiver order, stranger budget, first contact under flood | CC 5.4.6 (first contact under a flood is not promised) |
| `reply_lane.py` | `EVENT_PATH_MODEL.md` §M2 | the reply lane | CC 5.4.3 |

`EVENT_PATH_MODEL.md` §0.1 maps each piece to the formal model and invariant of this directory it relies on (membership, transport_tiers, withdraws_admission, anonymous, moderator_election, mesh_net), as read at CC rc17 `6d9e1da`.

**Running.** Each script runs stand-alone and prints its tables; some run for minutes. They are not run in CI here; CI checks that the vendored copies match the recorded commit when edge's branch is pushed (`tools/vendor_edge_models.py --check`, to come with the push). Re-vendor by copying the five scripts and three FSDs and updating the commit above.
