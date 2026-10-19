# `formal/two_path` — one decision shape for every governance change, and its corridor

**Why.** The steward's direction (2026-10-18): every governance change should be able to run under
one m-of-n policy with both paths — a forward threshold to enact at once, a reverse threshold to
cancel within a window, the window set by the sensitivity of the change, and an irreversibility flag
that removes the instant landing so the reverse path always has its chance — scaled as a roster-
scoped configuration; and the policy space must have limits, so no roster can configure itself into
an extreme, from the most open community allowed (a takedown very hard) to the most restricted (a
takedown very easy). The self roster (CC 3.3.6.3) and the halt (4.2.1.1) are the two instances the
text already has; persist is building the shared decision function for the roster door
(CIRISPersist#1099) and has surveyed every other door (below).

**Prior art, so the shape is not claimed as new.** The reverse path is the silence procedure (NATO,
the EU Council), Apache's lazy consensus, Wikipedia's proposed deletion, the suspensive veto; in
protocol governance it is optimistic governance (Aragon, Safe's delay module, UMA's optimistic
oracle, oSnap), with Lido's dual governance the closest single artefact (two signalling thresholds,
a minority extends the delay, a larger minority blocks). The forward supermajority with a threshold
that scales with the stakes is Buchanan & Tullock (1962) and Tsebelis's veto players. The
irreversibility delay is the governor timelock (Compound, OpenZeppelin), MakerDAO's governance
security module, Optimism's security-council veto. What is composed here and not found elsewhere:
the four as one parametrized object per roster, thresholds over the standing set, and a proved
corridor.

## `TwoPath.tla` — the generic machine

Constants: `Voters` (the standing set, N), `Coerced`, `EnactNum/EnactDen` (approvals × den > num × N,
strict), `CancelNum/CancelDen` (objections × den ≥ num × N), `Window`, `Irreversible`, `MaxChanges`.
One open proposal at a time; every voter answers once (honest approve honest changes and object
to adversarial ones; coerced do the reverse); the window ages only after every present voter has
answered; a forward landing happens at Enact unless irreversible; at the window the change is
cancelled if objections reached Cancel, else lands.

| Property | Statement |
|---|---|
| `Inv_AdversaryBelowCancelCannotBlock` | coerced below the cancel threshold never cancel an honest change |
| `Inv_HonestAtCancelStopsAdversary` | an honest set at or above the cancel threshold lets no adversarial change land |
| `Prop_IrreversibleWaits` | with the flag, nothing lands before the window |
| `Prop_HonestChangeResolves` | every honest proposal is decided (and, below Cancel, decided by landing) |

| Config | Instance | Verdict |
|---|---|---|
| `TwoPath_3_selfroster` | 3 voters, strict majority both ways, 1 coerced — CC 3.3.6.3 | closes, 47 states |
| `TwoPath_6_enact23_cancel13_1coerced` | enact 2/3, cancel 1/3, 1 of 6 coerced (below cancel) | closes, 431 |
| `TwoPath_6_enact23_cancel13_2coerced` | 2 of 6 coerced = exactly 1/3: can cancel, cannot enact | closes, 702 (the bound, shown) |
| `TwoPath_6_irreversible` | the same policy with no instant landing | closes, 431 |
| `TwoPath_7_enact23_cancel13_2coerced` | 7 voters, 2 coerced (below 1/3) | closes, 995 |

The halt is the mirror instance — fire at one, lapse at the fuse unless a majority confirms, a
majority resumes — and is checked in `formal/accord_halt`; the self roster's full policy with
per-door conditions (silent target, one open proposal per proposer, void votes of evicted keys) is
`formal/self_roster`. This module is the common core both refine.

## `PolicyCorridor.lean` — the limits

The corridor has the shape of coherence-ratchet's consent corridor (`consent_impossible_at_rigidity_pole`,
`consent_impossible_at_chaos_pole`, `corridor_is_consent_possible`), applied to thresholds:

- **the rigidity pole**: one voter can cancel, or enact needs everyone — a single coerced key blocks
  every change (the liberum veto; Buchanan & Tullock's diverging decision cost);
- **the chaos pole**: one voter can enact, or cancel needs everyone — one key takes content down and
  nothing stops it (below Greenberg's and Caplin–Nalebuff's stability bound);
- **the corridor**: neither pole, cancel ≤ enact, enact at least a strict majority, window at or
  above the sensitivity floor.

Checked: the steward's example (enact 2/3, cancel 1/3, 72 h) is in the corridor at 6 and 7 voters;
the self roster at 3; a one-of-six cancel is the rigidity pole; a below-one-sixth enact is the chaos
pole; unanimity is rigidity; a one-minute window is outside.

**Standing roster or who shows up (the steward's question).** Persist resolves thresholds over the
*live* roster count today; CC 4.2.6 ruled the *standing* roster for the accord because a censoring
adversary games the live set (`formal/accord_roster`). The file shows the cost of the standing
choice as size grows: with an expected-active law that saturates (a stand-in for the measured
participation curve, Olson's direction), a cancel fraction of one third over a standing roster of
10,000 needs 3,334 objections while about 344 members are active — the reverse path is dead, the
rigidity pole arrived at by size (`standing_fraction_dies_with_size`). The same fraction over the
expected-active base needs 115 and stays reachable (`active_base_stays_reachable`); at ten members
the two bases coincide and the small community pays the full fraction, 4 of 10 to cancel and 7 of
10 to enact (`small_community_pays_full`); a floor keeps a tiny roster from collapsing to one voice
(`floor_holds`). So the steward's intuition holds in the model: a fixed fraction of the standing
roster is right for small communities and wrong for large ones, and the base has to scale — either
by an expected-active law whose exponent is measured, or by coherence-ratchet's `k_eff`, which is
the same idea with correlation instead of attendance. Which base, and the exponent, are the
steward's and the measurement's; the file only shows that the choice is not free.

## What this directory does not decide

The per-family policy table (enact, cancel, window class, irreversible, standing set, clock, the
row families that carry proposal, approval and objection, the per-door conditions, any floor) is
the steward's to set and CC's to publish as manifest data beside the namespace registry
(persist's ask, 2026-10-18); the vectors `(policy, roster, events, now) → Lands | Pending | Refused`
follow from it. The door-by-door delta persist reported is filed as issues from this directory.
