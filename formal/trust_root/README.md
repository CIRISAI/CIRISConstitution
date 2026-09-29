# `formal/trust_root` — the CC 3.2 T8 standing verdict, model-checked

**What this is.** A TLA+ model of the standing verdict `V(rows, t)` that CC 3.2 T8 states as a
normative state machine — `Rooted` / `Stalled` / `NotRooted` over the rows a node holds and a
signer-stamped instant — together with the T8 invariants as TLC-checkable properties. It is the
evidence artifact for the claims-register row `CLM-standing-verdict` (CIRISConstitution#127).

**What it models.** One evaluating node, one `infrastructure` root, a bounded founder set (some
keys `node`-bearing), a bounded independent witness directory, and discrete instants. The rows:
founder seats with `identity_type` read at seating; revocations / withdraws with `effective_at`;
lower-only `revoked_after` bounds; lineage heads chained by previous digest and signed by the
active founders (T6); witness cosignatures with `signed_at`; acceptance edges written only on a
fresh, witnessed head (T4a) and deleted in one row (T3); the halt latch and `lifecycle:active`;
ceremony-plane conferrals and the T7 recovery widening.

**What it checks** (`TrustRootVerdict.cfg`):

| Property | T8 clause |
|---|---|
| `Inv_i` | (i) a `node`-bearing seat never moves a state — `V` equals `V` with node seats ignored |
| `Prop_ii` | (ii) a tick never moves `Rooted`/`Stalled` to `NotRooted` — `V` does not read the clock |
| `Prop_iv` | (iv) the edge-written transition is enabled only on a fresh, witnessed head (freshness read in the pre-state) |
| `Inv_vi` | (vi) no edge ⇒ `NotRooted`; `Rooted` ⇒ an edge naming a head |
| `Inv_viii` | (viii) a revoked-all key is out of the active set and out of every current head's quorum |
| `Inv_T7` | `Stalled` is exactly "every other leg holds, the margin fails" |
| `Inv_RecoverEnabled` | from `Stalled` with a conferrable human, the T7 recovery path is enabled |

Three clauses hold **by construction** in this cut and are stated in the module rather than
checked: (iii) rows are sets admitted at `now`, so nothing reaches behind; (v) the halt latch is
a definitional leg of `V` (its second branch) and is not toggled, since toggling it doubled the
space for no information; (vii) `V` reads only the row variables and `now`. Two representation
choices to know when reading a trace: each witness keeps only its latest cosignature (all T4a
and T6 read), so a witness moving to a newer head un-witnesses the older one; and a
`revoked_after` bound has one modelled value, revoke-all, since a bound at `now` is
behaviourally a resignation.

**How it got small — the three cuts, by TLC's per-action coverage profile.**

| Cut | Distinct states | Depth | Result |
|---|---|---|---|
| 1 — instant-stamped rows, edge/halt interval histories, a past-verdict vector, cosignatures as a free set | > 366,000,000 | 15 | did not close; stopped for memory; no violation |
| 2 — no histories, per-witness latest cosignature, bounds at {0, now}, a fifth human so T7 recovery is reachable | > 25,000,000 | 12 | did not close; no violation |
| 3 — set-valued rows, one bound semantics, no halt toggling, no edge timestamp | **22,152,480** | **25** | **closed, no violation, 9 min on 8 workers** |

The first cut's profile showed `LowerBound` and `Cosign` generating most successors and `Halt`
forking the whole tree, and that `Recover` had **never fired** — all three human founders started
seated, so no key was conferrable. Two earlier runs also found modelling bugs (a single-record
edge and a single-flag halt made `V` impure in `t`). No run found a defect in the T8 text.

**What it does not model.** The charter legs (recovery commitment, scope) are constants; witness
independence is by construction (disjoint constant sets) rather than derived from steward
bindings; the directory does not rotate; the accord family is out of scope (T7 excludes it).
Persist's five rc5 review corners are **not** encoded — #127 asks persist to list them, and they
become `Corner1..Corner5` here before any further property is added.

**Run it.**

```
java -cp tla2tools.jar tlc2.TLC -workers auto -deadlock TrustRootVerdict.tla
```

**Status (2026-09-29).** The checked-in configuration (five founders, one node-bearing, one human
unseated; three witnesses; `M = 2`, `K = 2`; four instants; window 2) **closes**: 22,152,480
distinct states to depth 25, no invariant or property violated. The CI job
(`.github/workflows/formal.yml`) runs it on every change to this directory or to CC 3.2, and
fails the build on any violation. Keep TLC's state files out of the tree (`-metadir`); a run
without it left 49 GB under `states/` once.
