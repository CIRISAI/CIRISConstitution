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
| `Prop_ii` | (ii) a tick that crosses no row-declared instant never moves `Rooted`/`Stalled` to `NotRooted` |
| `Inv_iii_viii` | (iii)+(viii) a past verdict changes only through a lowered `revoked_after` |
| `Inv_iv` | (iv) an edge written now names a head that was fresh and witnessed now |
| `Inv_v` | (v) halted ⇒ `NotRooted` at every instant until `lifecycle:active` |
| `Inv_vi` | (vi) no edge ⇒ `NotRooted`; `Rooted` ⇒ an edge |
| `Inv_viii` | (viii) a bound removes the signer from the active set from the bound onward |
| `Inv_T7` | `Stalled` is exactly "every other leg holds, the margin fails" |

(vii) — determinism in `(rows, t)` — holds by construction: `V` reads only row variables and its
parameter `t`; `now` enters only as `t`.

**What it does not model yet.** The charter legs (recovery commitment, scope, custody) are
constants; witness independence is by construction (disjoint constant sets) rather than derived
from steward bindings; the directory does not rotate; the accord family is not modelled (T7
excludes it). Persist's five rc5 review corners are **not** encoded — #127 asks persist to list
them, and they become `Corner1..Corner5` here before any further property is added.

**Run it.**

```
java -cp tla2tools.jar tlc2.TLC -workers auto -deadlock TrustRootVerdict.tla
```

**Status (2026-09-28).** At the checked-in configuration (four founders, one node-bearing; three
witnesses; `M = 2`, `K = 2`; four instants; window 2), TLC with symmetry reduction explored
**366,026,741 distinct states to depth 15 with no invariant or property violated** before the run
was stopped for memory on the workstation; the state space did not close. Two earlier
configurations found two *modelling* bugs (a single-record edge and a single-flag halt lost their
history and made `V` impure in `t`), now fixed by making both interval sets; no run found a defect
in the T8 text. The CI job (`.github/workflows/formal.yml`) is `workflow_dispatch` only until a
configuration closes — a smaller instant horizon or a state constraint is the next step, tracked
on CIRISConstitution#127 alongside persist's five corners.
