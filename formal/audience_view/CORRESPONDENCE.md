# Correspondence with the view theory

Part 1 of `AudienceView.lean` restates the view theory of CIRISOntology in plain Lean, so that this repository's formal models need no Mathlib. Each definition below has the same name and the same body as its source, and each theorem the same statement; only the proofs are rewritten in core Lean. The sources are at CIRISOntology commit `395a7ec`.

| Here | Source (CIRISOntology `395a7ec`) | Agreement |
|---|---|---|
| `Factors` | `CIRISOntology/Core/Factoring.lean:64` `Factoring.Factors` | definitionally equal (`rfl`) |
| `SeparatesFiber` | `CIRISOntology/Core/Coordination.lean:58` `SeparatesFiber` | definitionally equal (`rfl`) |
| `not_computable_from` | `CIRISOntology/Core/Coordination.lean:69` | each statement proved from the other's theorem |
| `factors_iff_not_separatesFiber` | `CIRISOntology/Core/Factoring.lean:80` | each statement proved from the other's theorem |
| `Closed` | `CIRISOntology/Core/Habit.lean:236` `Habit.Closed` | definitionally equal (`rfl`) |
| `Held` | `CIRISOntology/Core/Habit.lean:240` `Habit.Held` | definitionally equal (`rfl`) |
| `held_imp_closed` | `CIRISOntology/Core/Habit.lean:265` | each statement proved from the other's theorem |
| `closed_iff_fiber_invariant` | `CIRISOntology/Core/Habit.lean:305` | each statement proved from the other's theorem |
| `ViewClosed` | `CIRISOntology/Core/Closure.lean:48` `ViewClosed` | definitionally equal (`rfl`) |
| `closed_iff_viewClosed` | `CIRISOntology/Core/Closure.lean:56` `viewClosed_iff_never_splits`, with `Habit.closed_iff_fiber_invariant` | the two spellings of closure proved one condition here; the source's statement proved from it where the view's codomain is inhabited |

Added here and not in the source: `not_factors_of_separatesFiber` (the witness pair refutes factoring, with no assumption on the codomain), `factors_comp`, `Closed.never_splits` (the forward half of `closed_iff_fiber_invariant`, with no assumption on the codomain) and `closedOn` with `closed_of_closedOn` (a bounded check of fibre invariance, and that it gives `Closed` on the finite state space it enumerates).

**The mechanical check.** A scratch file imported `CIRISOntology.Core.Factoring`, `Habit`, `Closure` and `Coordination` from the Ontology's own build at `395a7ec` (Lean 4.14.0, Mathlib v4.14.0), with Part 1 of `AudienceView.lean` copied in unchanged. It proved by `rfl` that each restated definition equals its source at every universe, and proved each restated theorem's statement from the source theorem and each source statement from the restated theorem. It compiled with no error. The check is not run in this repository's CI, which has no Mathlib; it is to be rerun when the source moves.
