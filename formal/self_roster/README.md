# `formal/self_roster` — key states under one self, model-checked

**Why.** The steward asked (2026-10-16) for a model of the keys under one identity with one
invariant to attempt: with three or more keypairs under a self, a stolen device cannot on its own
kick the other devices off, yet two lost devices are recoverable from the one that remains. The
mitigation he named is the combination of quorum rules and the reverse quorum (CC 3.1.9.2's
`objection:{state}`) applied to the self, the same first-strike shape as the constitutional halt:
one actor's act, a window, a strict majority of the standing set deciding whether it stands.

**What it models.** Three or four devices under one self plus one spare; each device HELD by the
owner, by a thief, or by nobody (lost), and actionable only by a holder who can authenticate on it
(the owner always; the thief in the worst case, `StolenAuth = TRUE`). Possession and
authentication are separate; data at rest is not modelled. A device proposes an eviction or an
addition; any signed act by a device answers every open proposal (approve what its holder wants,
object to what they do not) and proves the device is not lost. Two paths: the **quorum** path (a
strict majority of the roster lands it at once) and the **lone** path (lands when the proposal's
window closes unless a strict majority of the *other* members, target included, object, and, for
an eviction, only if the target was silent all window). Votes from a key no longer on the roster
are void. An owner device proposes only against what it lost or had stolen; a thief proposes
anything. Adding a device runs under the same policy. `OwnerPresent` makes the owner use every
device each tick; `FALSE` is the owner away for a whole window. Time is per proposal (no clock).

**Sixteen configurations, one module.** Three devices unless stated; one theft or two losses. The one- and two-key runs were added for the 2026-10-18 ruling (CC 3.3.6.3), with `Inv_SelfSurvives` (the owner never holds no key) added to the ruled configurations; the stolen device ranges over every member, the genesis key included, so the genesis key's evictability is covered by the three- and four-key runs.

| Config | Policy / adversary | Expectation | TLC verdict (2026-10-16) |
|---|---|---|---|
| `combined3_stolen` | ruled; one stolen, owner present | both clauses hold; the thief is evicted | **closes**, 29,850 states |
| `combined3_lost` | ruled; two lost | the owner evicts both over two windows and adds a device | **closes**, 5,667 states |
| `combined4_mixed` | ruled; four devices, one stolen and one lost | holds with the owner at two of four | **closes**, 2,558,560 states |
| `unilateral3_stolen` | any member acts at once | thief evicts an owner device | `Inv_ThiefCannotEvictHonest` violated in 2 steps |
| `quorum3_lost` | quorum only; two lost | one of three is no majority: no recovery | `Prop_LostRecoverable` violated (stutters) |
| `reverse3_stolen` | lone path only; one stolen | safety holds, but a thief who keeps using the device is never silent, so it is never evicted | `Prop_LostRecoverable` violated: the quorum fast path is what evicts an active thief |
| `combined3_absent` | ruled; owner away a whole window | an absent owner's devices look lost | `Inv_ThiefCannotEvictHonest` violated: the stated residual |
| `combined3_mixed` | ruled; three devices, one stolen AND one lost | one owner device against one thief device is a tie no policy decides | `Inv_ThiefNeverMajority` violated: the bound; four devices repair it (above) |
| `combined4_2stolen` | ruled; four devices, two stolen | safety holds; two against two cannot recover | `Prop_LostRecoverable` violated: the bound |
| `unilateral3_lost`, `quorum3_stolen`, `reverse3_lost` | the remaining cells | the easy cases close | **close** |
| `combined1_add` | ruled; one key, the owner adds a device (2026-10-18) | at one key the add lands at once: the add-device approval | **closes**, 80 states |
| `combined1_stolen` | ruled; one key, stolen (2026-10-18) | the self is lost; nothing on the wire recovers it | `Inv_SelfSurvives` violated: the one-key bound |
| `combined2_lost` | ruled; two keys, one lost (2026-10-18) | the remaining key evicts the lost one over a window and adds | **closes**, 252 states |
| `combined2_stolen` | ruled; two keys, one stolen (2026-10-18) | safety holds; one against one is a stalemate the thief can hold | `Prop_LostRecoverable` violated: the two-key bound, stated in CC 3.3.6.3 |

**What the runs forced into the rule, each found as a counterexample first.** (1) Without the
silence condition, a thief's lone eviction landed on a present owner whose devices had not yet
objected when the window closed. (2) An owner device proposing to evict another owner device gave
the thief the one vote it needed for a quorum. (3) An approval kept from a device evicted
meanwhile made the thief's second eviction a majority of a smaller roster. (4) A proposing device
counted as present without counting as having spoken, so a target busy proposing looked silent.
(5) A global cap on open proposals let the thief fill every slot so the owner could never propose;
the slot is per proposer.

**The invariants.** `Inv_ThiefCannotEvictHonest` (no thief-held device's proposal ever evicts an
owner-held device), `Inv_ThiefNeverMajority` (thief-held devices never form a strict majority while
the owner holds one), `Prop_LostRecoverable` (once the owner starts acting, every lost and every
stolen device eventually leaves and the owner holds two devices again), `TypeOK`.

**What it does not model.** Data at rest and DEK re-wrap (CIRISServer#678); the add-device join
itself (CIRISServer `formal/add_device`); a thief who steals after the owner has started acting;
an owner with fewer than three devices, where the clauses do not apply.

Run: `java -cp tla2tools.jar tlc2.TLC -workers auto -metadir /tmp/tlc -deadlock -config SelfRoster_<cfg>.cfg SelfRoster.tla` (TLA+ tools 1.7.4; the three-device runs finish in seconds, the four-device ones in minutes).

## Traces for implementers (`traces/`, `dump_traces.py`)

`python3 dump_traces.py <tla2tools.jar>` writes six behaviours as JSON (model variables per state plus
a derived `step`), for a roster door to replay (CIRISPersist#1099): `unilateral3_stolen` (**refuse** —
the thief's lone eviction that a conforming door must not land), `combined1_stolen` and
`combined2_stolen` (**bound** — the one-key loss and the two-key stalemate, the latter a stuttering lasso),
and `combined3_stolen`, `combined3_lost`, `combined4_mixed` (**land** — the shortest behaviour that spends
the whole adversary budget and still reaches `Recovered`, obtained by checking `Inv_NotRecovered` as an
invariant; every `Execute` in it must land under the ruled policy). The files are generated from TLC
output and are regenerated whenever the module or a configuration changes.
