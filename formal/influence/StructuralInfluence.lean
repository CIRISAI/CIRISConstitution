/-
  StructuralInfluence.lean — the Annex E (CC 8.8.4) Structural Influence score and its normalisation,
  as a model rather than a nod (steward, 2026-10-19: "Annex E needs a model not a nod").

  The question from the rc8 mathematics review: Annex I reads SI against fixed cutoffs (0.4, 0.6, 0.8)
  on a 0–1 scale, while Annex E defines SI = CW + OA + log(1 + DWP), unbounded, and says it is
  normalised by "min-max scaling" over a population it never names. This file states both
  normalisations and proves what each does:

    - min-max over a population is undefined for a sole party (a singleton collapses to 0, so a sole
      creator is never a controller) and a party's verdict changes when an unrelated low-influence
      party joins the sample;
    - normalisation against FIXED MAXIMA is a property of the party alone, bounded, monotone in every
      factor, and its cutoffs translate to exact raw bands.

  Units: thousandths. Each factor is on a 0–4 scale (CW is 0–4 in the text; OA and the capped
  dependency term are given the same range here, which is the proposal), so a factor is 0..4000 and
  the raw sum 0..12000. Core Lean 4.14, no Mathlib, no sorry.
-/

namespace StructuralInfluence

/-- the three factors of Annex E, in thousandths of a 0–4 scale: Creator Weight, Operational
    Authority, and the dependency-web term log(1 + DWP) after its cap -/
structure Factors where
  cw  : Nat
  oa  : Nat
  dwp : Nat
  cw_le  : cw ≤ 4000
  oa_le  : oa ≤ 4000
  dwp_le : dwp ≤ 4000

/-- the raw score: the sum (Annex E's "conceptual formula", with the log term already capped) -/
def raw (f : Factors) : Nat := f.cw + f.oa + f.dwp

theorem raw_le (f : Factors) : raw f ≤ 12000 := by
  unfold raw; have := f.cw_le; have := f.oa_le; have := f.dwp_le; omega

/-- the fixed ceiling: every factor at its top -/
def maxRaw : Nat := 12000

/-- normalisation against fixed maxima, in thousandths of [0, 1] -/
def fixedNorm (f : Factors) : Nat := raw f * 1000 / maxRaw

/-- the Annex I verdicts, as cutoffs on the normalised score (thousandths) -/
def controller (n : Nat) : Prop := 600 ≤ n          -- "SI ≥ 0.6 → controller duties"
def negligenceBand (n : Nat) : Prop := 400 ≤ n ∧ n ≤ 800   -- "SI 0.4–0.8"
def highBand (n : Nat) : Prop := 800 ≤ n

/- ---- what fixed maxima give ---- -/

theorem fixedNorm_le_1000 (f : Factors) : fixedNorm f ≤ 1000 := by
  unfold fixedNorm maxRaw; have := raw_le f; omega

/-- monotone: more influence on any factor never lowers the score -/
theorem fixedNorm_mono (f g : Factors) (h : raw f ≤ raw g) : fixedNorm f ≤ fixedNorm g := by
  unfold fixedNorm maxRaw; omega

/-- the cutoffs are exact raw bands: controller iff the raw sum is at least 7.2 of 12 -/
theorem controller_iff_raw (f : Factors) : controller (fixedNorm f) ↔ 7200 ≤ raw f := by
  unfold controller fixedNorm maxRaw; omega

theorem negligence_iff_raw (f : Factors) : negligenceBand (fixedNorm f) ↔ 4800 ≤ raw f ∧ raw f ≤ 9611 := by
  unfold negligenceBand fixedNorm maxRaw; omega

theorem high_iff_raw (f : Factors) : highBand (fixedNorm f) ↔ 9600 ≤ raw f := by
  unfold highBand fixedNorm maxRaw; omega

/-- the verdict is a property of the party alone: it is a function of the party's factors and of
    nothing else, so no population enters it (stated over an arbitrary population to make the
    contrast with min-max explicit) -/
def fixedVerdictIn (_population : List Factors) (f : Factors) : Prop := controller (fixedNorm f)
theorem fixed_verdict_ignores_population (P Q : List Factors) (f : Factors) :
    fixedVerdictIn P f ↔ fixedVerdictIn Q f := Iff.rfl

/- ---- what min-max over a population gives ---- -/

/-- min-max scaling of a raw score x against the population's minimum lo and maximum hi -/
def minmaxNorm (x lo hi : Nat) : Nat := (x - lo) * 1000 / (hi - lo)

/-- a sole party: minimum = maximum, the spread is zero, and the scaled score is 0 whatever the
    raw score — a sole creator with every factor at its top is not a controller -/
theorem singleton_is_never_a_controller (x : Nat) : ¬ controller (minmaxNorm x x x) := by
  unfold controller minmaxNorm; simp

theorem sole_architect_scores_zero : minmaxNorm 12000 12000 12000 = 0 := by decide

/-- the verdict depends on who else is in the sample: a party with raw 6.0 among {3.0, 9.0} is not a
    controller (0.5); add an unrelated party with raw 0 and the same party becomes one (0.667) -/
theorem status_depends_on_others :
    ¬ controller (minmaxNorm 6000 3000 9000) ∧ controller (minmaxNorm 6000 0 9000) := by
  unfold controller minmaxNorm; decide

/-- and under fixed maxima the same party has one answer in both samples: 6.0 of 12 is 0.5, not a
    controller, whoever else is present -/
def midParty : Factors := ⟨2000, 2000, 2000, by decide, by decide, by decide⟩
theorem mid_party_one_answer : fixedNorm midParty = 500 ∧ ¬ controller (fixedNorm midParty) := by
  unfold controller fixedNorm maxRaw raw midParty; decide

/- ---- what the proposal says about the parties Annex I names (findings, not rulings) ---- -/

/-- a sole architect with full live control at the centre of the web: 1.0 -/
def soleArchitect : Factors := ⟨4000, 4000, 4000, by decide, by decide, by decide⟩
theorem sole_architect_is_controller : fixedNorm soleArchitect = 1000 ∧ controller (fixedNorm soleArchitect) := by
  unfold controller fixedNorm maxRaw raw soleArchitect; decide

/-- FINDING: a pure operator — built nothing, full live control, not central — scores 0.333 under
    equal weights, below Annex I's 0.4 negligence band for the deploying organisation. Either the
    deployer's duties do not rest on SI alone (Annex I's row also names the stage), or OA carries
    more weight than CW in the sum. The model records the consequence; the weights are the steward's. -/
def pureOperator : Factors := ⟨0, 4000, 0, by decide, by decide, by decide⟩
theorem pure_operator_below_negligence_band :
    fixedNorm pureOperator = 333 ∧ ¬ negligenceBand (fixedNorm pureOperator) := by
  unfold negligenceBand fixedNorm maxRaw raw pureOperator; decide

/-- an incidental user with no control and no centrality: 0, and never a controller -/
def incidental : Factors := ⟨0, 0, 0, by decide, by decide, by decide⟩
theorem incidental_is_zero : fixedNorm incidental = 0 := by decide

end StructuralInfluence
