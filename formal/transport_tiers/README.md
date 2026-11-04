# `formal/transport_tiers` — what each traffic tier carries, and for whom

**Status: a model for evaluation.** Nothing here is normative yet. The carriage rule it compares is a proposal, not CC text.

**The question.** There are three tiers: slow shaped (`base`), fast shaped between serve seats (`seat`, CIRISConstitution#200), and unshaped (`bulk`). Can the base tier carry, across strangers, only what no one has to consent to carry: key exchange and the consent requests themselves?

**The model** (`Tiers.lean`, Lean 4 core, no Mathlib). The first half states the tiers as they stand: lower of two offers, seat rate only with a seat at both ends, eight links then refusal with bulk offered. The second half gives each payload four traits (a person wrote it, it names a third person, its size is bounded, it asks custody) and each node one relation to a frame (`endpoint`, `offered`, `stranger`).

| | `currentAllows` | `proposedAllows` | `strictAllows` |
|---|---|---|---|
| a stranger carries | any link ciphertext | the consent-free set, on `base` only | the same |
| an endpoint or a carrier that said yes | everything | everything | `base` holds only the consent-free set |

**Proved.**

- `current_stranger_carries_room_body`, `current_stranger_carries_media`: today a stranger carries both.
- `stranger_only_consent_free`, `carrying_bulk_needs_a_yes`, `carrying_a_room_body_needs_a_yes`: under the proposal it does not.
- `endpoints_keep_everything`, `proposed_narrows_current`: the proposal takes nothing from the two parties or from a carrier that said yes, and only ever narrows.
- `every_road_runs_on_strangers`: first contact, adding a device, joining a room, the halt and revoking a key all complete on strangers alone, so consent has no chicken-and-egg.
- `strict_takes_rows_off_shaping`, `ordinary_pair_has_no_seat_link`: read strictly, two contacts' own rows lose shaping.
- `routed_nine_canonicals`, `flooded_home_link_six_seconds`, `key_plane_whole_takes_ten_days`: reach is not capacity.

**What it does not model.** The traits are assigned by hand, so the model proves what follows from them and not that they are right. It does not model routing: how a hop finds the way down a tree without retained path state, which CC 5.4.6's directed-announce paragraph bars for scoped destinations. `askBytes` is an assumption. A sealed ask's emptiness cannot be checked by a carrier; only its size can.

**Run.** `lean -M 6000 -T 200000 Tiers.lean` (exit 0, no `sorry`). Not yet in CI.
