# `formal/influence` — the Structural Influence score (Annex E) as a model

**Why.** The rc8 mathematics review found that Annex E's `SI = CW + OA + log(1 + DWP)` is unbounded while Annex I
reads it against fixed cutoffs (0.4, 0.6, 0.8), and that the normalisation named to bridge them — scaling
against a population's or a deployment's maximum — was unstated. The steward asked for a model, not a nod
(2026-10-19). `StructuralInfluence.lean` (core Lean 4.14, no Mathlib, no `sorry`) states both normalisations
in thousandths and proves what each does.

| Theorem | Statement |
|---|---|
| `raw_le`, `fixedNorm_le_1000` | three factors on 0–4 give a raw sum ≤ 12 and a normalised score in [0, 1] |
| `fixedNorm_mono` | more influence never lowers the score |
| `controller_iff_raw`, `negligence_iff_raw`, `high_iff_raw` | Annex I's cutoffs are exact raw bands: 7.2 / 12 for controller, 4.8–9.6 for the negligence band, 9.6 for high |
| `fixed_verdict_ignores_population` | under fixed maxima the verdict is the party's alone |
| `singleton_is_never_a_controller`, `sole_architect_scores_zero` | min-max over a population gives a sole party 0: a sole architect at every top is never a controller |
| `status_depends_on_others` | raw 6.0 among {3.0, 9.0} is not a controller; add an unrelated raw 0 and it is |
| `mid_party_one_answer` | the same party under fixed maxima: 0.5, one answer in both samples |
| `pure_operator_below_negligence_band` | **finding for the steward:** built nothing, full live control, not central = 0.333, below Annex I's 0.4 band for the deploying organisation |

**What the model fixes in the text (landed in CC 8.8.4):** `SI_norm = (CW + OA + min(4, log(1 + DWP))) / 12`,
each factor on a 0–4 scale; no population, no deployment-calibrated `SI_max`.

**What it does not decide:** the weights. Equal weights put a pure operator under the negligence band; whether
the deployer's duties rest on SI alone or OA should weigh more is the steward's.

Run: `lean StructuralInfluence.lean`.
