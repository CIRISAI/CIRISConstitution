# `formal/transport_tiers` — what each traffic tier carries, and for whom

**Status: a model for evaluation.** Nothing here is normative yet. The carriage rule it compares is a proposal, not CC text.

**The question.** There are three tiers: slow shaped (`base`), fast shaped between serve seats (`seat`, CIRISConstitution#200), and unshaped (`bulk`). Can the base tier carry, across strangers, only what no one has to consent to carry: key exchange and the consent requests themselves?

**The model** (`Tiers.lean`, Lean 4 core, no Mathlib). The first half states the tiers as they stand: lower of two offers, seat rate only with a seat at both ends, eight links then refusal with bulk offered. The second half gives each payload four traits (a person wrote it, it names a third person, its size is bounded, it asks custody) and each node one relation to a frame (`endpoint`, `offered`, `stranger`).

| | `currentAllows` | `proposedAllows` | `strictAllows` |
|---|---|---|---|
| a stranger carries | any link ciphertext | the consent-free set, at any rate | the same |
| an endpoint or a carrier that said yes | everything | everything | `base` holds only the consent-free set |

**Proved.**

- `current_stranger_carries_room_body`, `current_stranger_carries_media`: today a stranger carries both.
- `stranger_only_consent_free`, `carrying_bulk_needs_a_yes`, `carrying_a_room_body_needs_a_yes`: under the proposal it does not.
- `endpoints_keep_everything`, `proposed_narrows_current`: the proposal takes nothing from the two parties or from a carrier that said yes, and only ever narrows.
- `every_road_runs_on_strangers`: first contact, adding a device, joining a room, the halt and revoking a key all complete on strangers alone, so consent has no chicken-and-egg.
- `strict_takes_rows_off_shaping`, `ordinary_pair_has_no_seat_link`: read strictly, two contacts' own rows lose shaping.
- `carriage_independent_of_class`, `consent_only_same_at_every_rate`, `seat_link_may_be_consent_only`: the size of a shaped link and its carriage are two axes; a fast seat link may be first-contact-and-consent only.
- `home_displaces_a_phone`, `phone_does_not_displace_a_phone`, `displaced_keeps_shaping`, `lower_never_displaces`, `place_keeps_bound`: a higher class takes a slot, the displaced peer moves to a shaped peer and keeps shaping, a phone never displaces a phone, the bound holds.
- `same_device_same_rate`: with the class tied to the device class universally, a rate singles nobody out.
- `unowned_only_strands_the_73rd`, `marker_default_off_strands_the_73rd`, `relay_offering_seats_everyone`, `each_home_adds_seven`: a refused peer can make first contact only where it is referred; referring unowned nodes only, or owned nodes by an opt-in marker, strands the seventy-third peer at nine canonicals; with relay offering as the consent every peer is seated and each seated home adds seven slots.
- `routed_nine_canonicals`, `flooded_home_link_six_seconds`, `key_plane_whole_takes_ten_days`: reach is not capacity.
- `unreachable_homes_add_nothing`, `each_reachable_home_adds_seven`, `zero_reach_rests_on_seats`, `reach_forty_of_a_thousand`: a home seats others only when it can be dialled directly (CC 5.4.3, a shaped link is one hop; CC 5.4.6, relay by default, a phone while charging on an unmetered network); the reachable share is a measured input, and at zero reach seating rests on the seats alone.
- `seat_budget_is_thirty_three_thousand`, `shaped_wire_independent_of_demand`, `home_window_bytes_fixed`: the seat class rate, and the shaped wire moving the class budget per window whatever the demand, so load reaches latency and the unshaped plane only.

**What it does not model.** The traits are assigned by hand, so the model proves what follows from them and not that they are right. It does not model routing: how a hop finds the way down a tree without retained path state, which CC 5.4.6's directed-announce paragraph bars for scoped destinations. `askBytes` is an assumption. A sealed ask's emptiness cannot be checked by a carrier; only its size can.

**Run.** `lean -M 6000 -T 200000 Tiers.lean` (exit 0, no `sorry`). Not yet in CI.

## The shaped frame: A against B (`frame_ab.py`)

The frame was first pinned at the link MDU, 16 KB on a TCP link; a first contact relayed through a shaped home-class link then waited about seven frame gaps, some 40 s, against a target of 30 s. `frame_ab.py` runs the two frames at the same class byte rate, with the two sizes the IETF names as floors beside them (1,280 B, the smallest link MTU IPv6 permits, RFC 8200; 1,200 B, the smallest datagram QUIC requires a path to carry, RFC 9000). What it finds: λ scales as the frame ratio, about 11.6; the real bytes a window admits are within three per cent between arms (the per-frame overhead); the transit time of a volume of bytes is equal, bytes over rate; only the first-byte wait divides by the frame ratio, so seven shaped waits fit the target at the 95th percentile on server, home and phone-wifi at 1,400 B and on none but server at the MDU; an onion packet of 15,296 B spans twelve frames; seals a second at the eight-link bound rise to a few tens. The transport's per-packet header (107 B) and proof (83 B) put about a tenth more on the wire than the budget at 1,400 B against about one per cent at the MDU (edge's figures, to be measured on the rig). The observer's view (one constant-size Poisson stream at λ) is the same in every arm by construction. `--check` asserts the figures CC 5.4.3 carries. Run: `python3 -I formal/transport_tiers/frame_ab.py` (and `--check`, in CI). The vendored edge model `formal/vendor/edge/transport_tiers.py` still carries the 16,272 B frame it measured; it moves when edge re-cuts it.
