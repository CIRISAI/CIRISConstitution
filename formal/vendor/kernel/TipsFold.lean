/-
  TipsFold.lean: the fold at tips (KERNEL.md section 7; crates/ciris-kernel src/seat.rs, `Seats::tips_fold`;
  models/roster_fork/fold.py).

  With several tips, the keys seated are the least set that holds the keys common to the tips and every
  candidate whose addition meets its count on the voices of keys already in the set. A candidate is a key some
  tip seats that no tip's line removed without a later addition. This file states that fold as passes from the
  common keys and proves its bounds: the common keys are in at every pass; a pass only adds; nothing outside
  the common keys and the candidates is ever in, so a key that is out is never in; with no candidate the fold
  is the common keys, which is the rule it replaces; a pass that adds nothing is the last; and an admission
  reads only the keys already in, so a key the fold never seats is a voice for nobody.

  It does not prove the count (`SeatCount.lean` states the counts), nor that the crate's code is this
  definition: the crate is tied to it by cases (`tests/seat.rs`, `tests/fold.rs`). Core Lean 4.14, no Mathlib.
-/
namespace TipsFold

variable {K : Type}

/-- One pass: what is in stays in, and a candidate comes in when its addition is admitted on the keys in. -/
def step (cand : K → Prop) (admits : (K → Prop) → K → Prop) (S : K → Prop) : K → Prop :=
  fun k => S k ∨ (cand k ∧ admits S k)

/-- The fold after `n` passes from the common keys. -/
def pass (common cand : K → Prop) (admits : (K → Prop) → K → Prop) : Nat → K → Prop
  | 0 => common
  | n + 1 => step cand admits (pass common cand admits n)

/-- The common keys are in at every pass. -/
theorem common_in (common cand : K → Prop) (admits : (K → Prop) → K → Prop) (n : Nat) (k : K)
    (h : common k) : pass common cand admits n k := by
  induction n with
  | zero => exact h
  | succ n ih => exact Or.inl ih

/-- A pass only adds. -/
theorem pass_grows (common cand : K → Prop) (admits : (K → Prop) → K → Prop) (n : Nat) (k : K)
    (h : pass common cand admits n k) : pass common cand admits (n + 1) k := Or.inl h

/-- Nothing outside the common keys and the candidates is ever in. -/
theorem in_common_or_cand (common cand : K → Prop) (admits : (K → Prop) → K → Prop) (n : Nat) (k : K)
    (h : pass common cand admits n k) : common k ∨ cand k := by
  induction n with
  | zero => exact Or.inl h
  | succ n ih =>
    cases h with
    | inl h => exact ih h
    | inr h => exact Or.inr h.1

/-- A key that is out (removed on some tip's line, with no later addition) is never in: it is neither common
    to the tips nor a candidate. -/
theorem out_never_in (common cand out : K → Prop) (admits : (K → Prop) → K → Prop)
    (hc : ∀ k, common k → ¬ out k) (hd : ∀ k, cand k → ¬ out k) (n : Nat) (k : K)
    (h : pass common cand admits n k) : ¬ out k := by
  cases in_common_or_cand common cand admits n k h with
  | inl h => exact hc k h
  | inr h => exact hd k h

/-- With no candidate the fold is the common keys: where no tip adds anyone it is the rule it replaces. -/
theorem no_candidate_is_common (common cand : K → Prop) (admits : (K → Prop) → K → Prop)
    (h : ∀ k, ¬ cand k) (n : Nat) (k : K) : pass common cand admits n k ↔ common k := by
  constructor
  · intro hp
    cases in_common_or_cand common cand admits n k hp with
    | inl hc => exact hc
    | inr hd => exact absurd hd (h k)
  · exact common_in common cand admits n k

/-- A pass that adds nothing is the last, where an admission reads only which keys are in. -/
theorem stable (common cand : K → Prop) (admits : (K → Prop) → K → Prop)
    (ext : ∀ S T : K → Prop, (∀ k, S k ↔ T k) → ∀ k, admits S k ↔ admits T k) (n : Nat)
    (h : ∀ k, pass common cand admits (n + 1) k ↔ pass common cand admits n k) :
    ∀ m k, pass common cand admits (n + m) k ↔ pass common cand admits n k := by
  intro m
  induction m with
  | zero => intro k; exact Iff.rfl
  | succ m ih =>
    intro k
    constructor
    · intro hp
      have hp' : step cand admits (pass common cand admits (n + m)) k := hp
      cases hp' with
      | inl hin => exact (ih k).1 hin
      | inr had =>
        have : admits (pass common cand admits n) k :=
          (ext (pass common cand admits (n + m)) (pass common cand admits n) ih k).1 had.2
        exact (h k).1 (Or.inr ⟨had.1, this⟩)
    · intro hp
      exact Or.inl ((ih k).2 hp)

/-- A voice counts only once its key is in: where an admission reads only the keys in, two folds that differ
    only in a key neither ever seats admit the same keys at the next pass. A key the fold refuses vouches for
    nobody (the forged line of two). -/
theorem refused_key_is_no_voice (cand : K → Prop) (admits : (K → Prop) → K → Prop)
    (ext : ∀ S T : K → Prop, (∀ k, S k ↔ T k) → ∀ k, admits S k ↔ admits T k) (S T : K → Prop)
    (same : ∀ k, S k ↔ T k) (k : K) : step cand admits S k ↔ step cand admits T k := by
  unfold step
  constructor
  · intro h
    cases h with
    | inl h => exact Or.inl ((same k).1 h)
    | inr h => exact Or.inr ⟨h.1, (ext S T same k).1 h.2⟩
  · intro h
    cases h with
    | inl h => exact Or.inl ((same k).2 h)
    | inr h => exact Or.inr ⟨h.1, (ext S T same k).2 h.2⟩

end TipsFold

#print axioms TipsFold.common_in
#print axioms TipsFold.pass_grows
#print axioms TipsFold.in_common_or_cand
#print axioms TipsFold.out_never_in
#print axioms TipsFold.no_candidate_is_common
#print axioms TipsFold.stable
#print axioms TipsFold.refused_key_is_no_voice
