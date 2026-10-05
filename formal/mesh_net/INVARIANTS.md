# The net invariants of the mesh — derived, and where each is checked

Steward's question (2026-10-05): list the invariants the mesh must keep, read from
[ciris.ai/safety](https://ciris.ai/safety), [ciris.ai/constitutional-mesh](https://ciris.ai/constitutional-mesh)
and the Constitution, and model the replication / moderation states against them. This file is the
derivation; `MeshNet.tla` is the model; `formal/accord_roster` and `formal/trust_root` cover the two
invariants that are counting or verdict problems rather than state-machine ones.

Each row names the source that forces the invariant, the predicate the model checks, and its status
against the text and the shipped code on 2026-10-05. "Holds (ruled)" means it holds once the rc7
rulings on CIRISConstitution#141–#145 are in the text.

| # | Invariant (plain) | Forced by | Model property | Status |
|---|---|---|---|---|
| I1 | **We never hold anything we don't know what it is.** A node holds Commons plaintext it can inspect, or ciphertext for a cohort its owner belongs to. There is no non-member holder of bounded-cohort bytes. | CC 4.4.3.2.1 holder-inspectability; CC 6.1.5.3 audience = the owner's cohorts | `Inv_KnownHold` | Holds. The 4.4.3.2.1 "hold opaque ciphertext for a community it trusts" clause describes no shipped behaviour (edge, #141) and is retired by #141 |
| I2 | **Consent is supreme.** A node holds nothing its owner did not consent to, except what it authored; a server-class node carries nothing personal unless listed. | CC 4.2.1 "no key may cause a node to share more than its owner consented to"; CC 3.3.7 `cohorts`; CC 6.1.5.3 | `Inv_Consent` | Holds |
| I3 | **Structural privacy.** No emission about bounded-cohort content — holding claim, discovery row, announce — is observable outside the cohort. Group existence is invisible to non-members (the darknet plane); the identity plane announces normally (the lightnet). | CC 5.2 (the *unconditional* promise); CC 5.4.6 zero-emission corner; edge `LIGHTNET_DARKNET.md` §1 | `Inv_Invisible` | **Violated as shipped** for community and public-room content: persist emits `holds_bytes` at federation scope (`MeshNet_shipped_scope.cfg` finds it in four steps). Holds (ruled): #141 puts the one holding claim at the content's scope |
| I4 | **A holding claim is never a content binding.** Withdrawn content is not live because a device still reports holding it. | CC 2.3 bytes plane; CC 2.4.1.1 rule 1; #141 item 3 | `Inv_ClaimNotBinding` | **Violated as shipped** (persist v53 folds a live `custody:ack` as a binding; `MeshNet_shipped_bind.cfg` finds it in five steps). Holds (ruled) |
| I5 | **No unmoderated community, ever.** A multi-party space federates only while it has a live `moderate` holder; a lapse auto-promotes or fails secure in the same step. | CC 4.5.4 (existence gate, merit auto-promotion, fail-secure) | `Inv_Moderated` | Holds. #142's public rooms inherit it unchanged (a named moderator from creation) |
| I6 | **Scanning only at the publication seam.** The perceptual-hash tripwire runs when content is published into the Commons or a public room, and never on content inside a private cohort. | CC 1.13 (tripwire at scope widening, never on the device, never inside a cohort); CC 4.5.7 (no client-side scanning); #142 (posting into a public room is publication) | `Inv_ScanSeam` | Holds, with the #142 addition that a public-room post is a seam |
| I7 | **The halt binds subscribers and only subscribers; un-trust is one row.** | CC 4.2.1 reach; CC 3.2 T3; safety page "no party inside the federation can disable or route around the stop" | `RootReach.tla`: `Inv_HaltOnlySubscribers`, `Prop_HaltReach`, `Untrust` | Holds. #145 item 4's constraint (the kill switch never depends on a plane gate) keeps `Prop_HaltReach` true after the accord-evidence move |
| I8 | **A trust root only restricts.** `mesh_config` relieves or narrows what flows and never widens it; an un-trusted node is restricted by nothing. | CC 4.2.1 relieve-never-expand, most-restrictive-across-roots | `RootReach.tla`: `Prop_RestrictOnly`, `Inv_RestrictNeedsRoot`; `MeshNet.tla`: `Prop_RestrictOnly` (the restriction only narrows the audience) | Holds |
| I9 | **No group ban.** No accord act, and no root, removes a community mesh-wide; the accord's powers are the closed enumeration. | CC 4.2.1 enumeration ("silence confers no authority"); CC 4.5.3; #142 item 5 | `RootReach.tla`: `Prop_NoBan`; `MeshNet.tla` has no accord action at all, so a roster, a moderator set or whether a community federates cannot be touched by one | Holds; #142 writes the reason into the text |
| I10 | **A roster change needs a majority of the whole accord; seizure needs ⌊N/2⌋+1 coerced holders and censorship buys nothing.** | CC 4.2.6 (rc7, #139) | `formal/accord_roster/AccordRoster.lean` | Proved |
| I11 | **A root is valid until revoked; attaching is gated on freshness; the standing verdict never moves on the clock.** | CC 3.2 T4, T4a, T8 | `formal/trust_root/TrustRootVerdict.tla` | Model-checked (22.15 M states) |
| I12 | **One voice counts once.** Copies of one voice buy no trust (N_eff). | constitutional-mesh page P5 and the "manufactured humans" negation; CC 6.2 | not modelled here: a statistical property of the scoring layer, with its own evidence rows (`coherence-ratchet`) | Measured, not proved |

**What the model does not cover, stated.** Signature forgery; the roster fold's internal rules
(T6/T7, in `formal/trust_root`); fountain symbols and target replication counts (CC 6.1.5, a
counting problem); the tripwire's own accuracy; coercion of individuals (I10's bound is the only
statement made). Three persons, three nodes, two blobs is enough to exhibit every violation above
and to exhaust the ruled state space; it is not a proof for all sizes.

**What the exercise decided.** The two shipped defects are both consequences of carrying a holding
claim *beside* the five row types instead of *on* them: `holds_bytes` had its scope hard-coded
because it was a carrier with no family rule, and it became a binding because the bytes-plane fold
had to exclude it by type. Both vanish when the claim is a `scores` row on `custody:ack:v1` at the
content's scope (#141). Nothing in I1–I9 needs a sixth verb or a second roster.
