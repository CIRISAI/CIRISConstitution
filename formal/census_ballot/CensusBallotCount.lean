/-
  CensusBallotCount.lean — the counting facts under the census and the secret ballot
  (steward rulings of 2026-10-22; CC 4.5.13, 5.4.6, 6.1.2.1.2), for any N. The TLA+ model
  (CensusBallot.tla) checks the machine on small instances; this file proves the arithmetic
  it rests on in general.

    tally_exact        — the sum of the two tally members' partial sums is the sum of the
                         values, modulo M, and exactly when the count is in range;
    secrecy_one_share  — one share is consistent with every value, by exactly one complement
                         (so a single tally member's view is uniform over the value);
    onehot_histogram   — a histogram of one-hot reports sums to the number of reports
                         (a valid report adds exactly one count to one bucket);
    ratchet_floor      — after t periods of maximal silencing the base is at least the floor
                         and at least base_0 · (p/q)^t, stated on naturals;
    freeze_holds       — a one-period fall of more than the freeze fraction leaves the base
                         where it was;
    dominance_bound    — if no owner holds more than half the mass then n_eff ≥ 2, and with
                         unit masses n_eff = source_count.

  Core Lean 4.14, no Mathlib, no `sorry`.
-/

namespace CensusBallot

/- ---------------- lists, sums ---------------- -/

def sum : List Nat → Nat
  | [] => 0
  | x :: xs => x + sum xs

def sumsq : List Nat → Nat
  | [] => 0
  | x :: xs => x * x + sumsq xs

theorem sum_append (a b : List Nat) : sum (a ++ b) = sum a + sum b := by
  induction a with
  | nil => simp [sum]
  | cons x xs ih => simp [sum, ih, Nat.add_assoc]

/- ---------------- (a) additive sharing: the tally is exact ---------------- -/

/-- A shared entry: a value `v` split as `s0 + s1 ≡ v (mod M)` with the first share `r`. -/
def split (M v r : Nat) : Nat × Nat := (r % M, (v + (M - r % M)) % M)

theorem split_sum (M v r : Nat) (hM : 0 < M) :
    ((split M v r).1 + (split M v r).2) % M = v % M := by
  unfold split
  simp only
  have hlt : r % M < M := Nat.mod_lt r hM
  have e : r % M + (v + (M - r % M)) = v + M := by omega
  calc (r % M + (v + (M - r % M)) % M) % M
      = (r % M + (v + (M - r % M))) % M := Nat.add_mod_mod _ _ _
    _ = (v + M) % M := by rw [e]
    _ = v % M := Nat.add_mod_right v M

/-- A period's reports as (value, first-share randomness) pairs; the two partial sums. -/
def partial0 (M : Nat) : List (Nat × Nat) → Nat
  | [] => 0
  | (v, r) :: xs => (split M v r).1 + partial0 M xs

def partial1 (M : Nat) : List (Nat × Nat) → Nat
  | [] => 0
  | (v, r) :: xs => (split M v r).2 + partial1 M xs

def values : List (Nat × Nat) → List Nat
  | [] => []
  | (v, _) :: xs => v :: values xs

/-- Inv_Correctness for any N: partial_0 + partial_1 ≡ Σ values (mod M). -/
theorem tally_exact_mod (M : Nat) (hM : 0 < M) (rs : List (Nat × Nat)) :
    (partial0 M rs + partial1 M rs) % M = sum (values rs) % M := by
  induction rs with
  | nil => simp [partial0, partial1, values, sum]
  | cons p xs ih =>
    obtain ⟨v, r⟩ := p
    simp only [partial0, partial1, values, sum]
    have h := split_sum M v r hM
    have e : (split M v r).1 + partial0 M xs + ((split M v r).2 + partial1 M xs)
           = ((split M v r).1 + (split M v r).2) + (partial0 M xs + partial1 M xs) := by omega
    rw [e, Nat.add_mod, h, ih, ← Nat.add_mod]

/-- And exactly, when the count is in range (the modulus exceeds the sum: the "range of
    shares in bounds" assumption the README states). -/
theorem tally_exact (M : Nat) (hM : 0 < M) (rs : List (Nat × Nat))
    (hrange : sum (values rs) < M) :
    (partial0 M rs + partial1 M rs) % M = sum (values rs) := by
  rw [tally_exact_mod M hM rs, Nat.mod_eq_of_lt hrange]

/- ---------------- (b) one share says nothing ---------------- -/

/-- For every share `s` and every value `v` there is a complement `s'` with `s + s' ≡ v`. -/
theorem secrecy_one_share (M s v : Nat) (hM : 0 < M) (hv : v < M) :
    ∃ s', s' < M ∧ (s + s') % M = v := by
  refine ⟨(v + (M - s % M)) % M, Nat.mod_lt _ hM, ?_⟩
  have hlt : s % M < M := Nat.mod_lt s hM
  have e : s % M + (v + (M - s % M)) = v + M := by omega
  calc (s + (v + (M - s % M)) % M) % M
      = (s + (v + (M - s % M))) % M := Nat.add_mod_mod _ _ _
    _ = (s % M + (v + (M - s % M))) % M := (Nat.mod_add_mod _ _ _).symm
    _ = (v + M) % M := by rw [e]
    _ = v := by rw [Nat.add_mod_right, Nat.mod_eq_of_lt hv]

/-- The complement is unique below M: the map value ↦ complement is a bijection, so a
    single share is uniformly consistent with every value. -/
theorem secrecy_one_share_unique (M s v s₁ s₂ : Nat) (hM : 0 < M)
    (h₁ : s₁ < M) (h₂ : s₂ < M)
    (e₁ : (s + s₁) % M = v) (e₂ : (s + s₂) % M = v) : s₁ = s₂ := by
  -- s₁ = (s + s₁ + (M - s % M)) % M, and likewise s₂; both middles equal v
  have key : ∀ x, x < M → (s + x + (M - s % M)) % M = x := by
    intro x hx
    have hlt : s % M < M := Nat.mod_lt s hM
    have hle : s % M ≤ s := Nat.mod_le s M
    have e : s + x + (M - s % M) = (s - s % M) + x + M := by omega
    have hd : (s - s % M) % M = 0 := by
      have := Nat.div_add_mod s M
      have e2 : s - s % M = M * (s / M) := by omega
      rw [e2, Nat.mul_mod_right]
    calc (s + x + (M - s % M)) % M = ((s - s % M) + x + M) % M := by rw [e]
      _ = ((s - s % M) + x) % M := Nat.add_mod_right _ _
      _ = (((s - s % M) % M) + x % M) % M := Nat.add_mod _ _ _
      _ = x := by rw [hd, Nat.zero_add, Nat.mod_mod, Nat.mod_eq_of_lt hx]
  have a₁ : (s + s₁ + (M - s % M)) % M = (v + (M - s % M)) % M := by
    rw [Nat.add_mod, e₁]; exact Nat.add_mod_mod _ _ _
  have a₂ : (s + s₂ + (M - s % M)) % M = (v + (M - s % M)) % M := by
    rw [Nat.add_mod, e₂]; exact Nat.add_mod_mod _ _ _
  rw [key s₁ h₁] at a₁
  rw [key s₂ h₂] at a₂
  omega

/- ---------------- one-hot reports and the histogram ---------------- -/

/-- A report is one-hot: entries in {0,1} and sum 1. -/
def OneHot (v : List Nat) : Prop := (∀ x ∈ v, x ≤ 1) ∧ sum v = 1

/-- Pointwise sum of two vectors of equal length. -/
def vadd : List Nat → List Nat → List Nat
  | x :: xs, y :: ys => (x + y) :: vadd xs ys
  | _, _ => []

theorem sum_vadd (a b : List Nat) (h : a.length = b.length) :
    sum (vadd a b) = sum a + sum b := by
  induction a generalizing b with
  | nil => cases b with
    | nil => simp [vadd, sum]
    | cons y ys => simp at h
  | cons x xs ih => cases b with
    | nil => simp at h
    | cons y ys =>
      simp [vadd, sum]
      have := ih ys (by simpa using h)
      omega

theorem length_vadd (a b : List Nat) (h : a.length = b.length) :
    (vadd a b).length = a.length := by
  induction a generalizing b with
  | nil => cases b with
    | nil => rfl
    | cons y ys => simp at h
  | cons x xs ih => cases b with
    | nil => simp at h
    | cons y ys => simp [vadd]; exact ih ys (by simpa using h)

/-- The histogram over B buckets of a list of reports (each of length B). -/
def histogram (B : Nat) : List (List Nat) → List Nat
  | [] => List.replicate B 0
  | r :: rs => vadd r (histogram B rs)

theorem sum_replicate_zero (B : Nat) : sum (List.replicate B 0) = 0 := by
  induction B with
  | zero => rfl
  | succ n ih => simp [List.replicate, sum, ih]

theorem length_histogram (B : Nat) (rs : List (List Nat)) (hl : ∀ r ∈ rs, r.length = B) :
    (histogram B rs).length = B := by
  induction rs with
  | nil => simp [histogram]
  | cons r rs ih =>
    simp only [histogram]
    have hr : r.length = B := hl r (by simp)
    have hrest := ih (fun x hx => hl x (by simp [hx]))
    rw [length_vadd r _ (by rw [hr, hrest])]
    exact hr

/-- Inv_Validity's consequence for any N: a histogram of one-hot reports sums to the number
    of reports — each accepted report adds exactly one count to one bucket, so the "yes"
    count of the expected-active cell and each option's count are counts of owners. -/
theorem onehot_histogram (B : Nat) (rs : List (List Nat))
    (hl : ∀ r ∈ rs, r.length = B) (hv : ∀ r ∈ rs, OneHot r) :
    sum (histogram B rs) = rs.length := by
  induction rs with
  | nil => simp [histogram, sum_replicate_zero]
  | cons r rs ih =>
    simp only [histogram, List.length_cons]
    have hr : r.length = B := hl r (by simp)
    have hrest := length_histogram B rs (fun x hx => hl x (by simp [hx]))
    rw [sum_vadd r _ (by rw [hr, hrest])]
    rw [(hv r (by simp)).2, ih (fun x hx => hl x (by simp [hx])) (fun x hx => hv x (by simp [hx]))]
    omega

/- ---------------- (c) the base law: ratchet, floor, freeze ---------------- -/

/-- ⌈a / q⌉ on naturals. -/
def ceilDiv (a q : Nat) : Nat := (a + q - 1) / q

theorem ceilDiv_mul_ge (a q : Nat) (hq : 0 < q) : ceilDiv a q * q ≥ a := by
  unfold ceilDiv
  have h1 := Nat.div_add_mod (a + q - 1) q
  have h2 := Nat.mod_lt (a + q - 1) hq
  have e : (a + q - 1) / q * q = q * ((a + q - 1) / q) := Nat.mul_comm _ _
  omega

/-- One period of the base law outside a freeze: the composite `ea`, the ratchet term
    ⌈p · b / q⌉ (p/q = 9/10 ruled), and the period's floor. Maximal silencing is `ea = 0`
    (and `floor` as low as the law allows): the result is monotone in both. -/
def step (p q b ea floor : Nat) : Nat := max ea (max (ceilDiv (b * p) q) floor)

theorem step_ge_floor (p q b ea floor : Nat) : step p q b ea floor ≥ floor := by
  unfold step; omega

theorem step_ge_ea (p q b ea floor : Nat) : step p q b ea floor ≥ ea := by
  unfold step; omega

theorem step_ratchet (p q b ea floor : Nat) (hq : 0 < q) :
    step p q b ea floor * q ≥ b * p := by
  unfold step
  have h := ceilDiv_mul_ge (b * p) q hq
  have hm : ceilDiv (b * p) q ≤ max ea (max (ceilDiv (b * p) q) floor) := by omega
  exact Nat.le_trans h (Nat.mul_le_mul_right q hm)

/-- Silencing can only lower the composite and the floor; the law answers monotonically,
    so `ea = 0` is the worst a silencer achieves. -/
theorem step_mono (p q b ea ea' floor floor' : Nat) (he : ea ≤ ea') (hf : floor ≤ floor') :
    step p q b ea floor ≤ step p q b ea' floor' := by
  unfold step; omega

/-- The base after `t` periods under composites `eas` and floors `floors` (lists read
    oldest first), starting from `b0`. -/
def run (p q : Nat) : Nat → List Nat → List Nat → Nat
  | b0, ea :: eas, fl :: fls => run p q (step p q b0 ea fl) eas fls
  | b0, _, _ => b0

/-- ratchet_floor, the per-step form the TLA+ invariant checks: every period's base is at
    least that period's floor and at least p/q of the previous base. (Stated on the last
    step; `run` threads it through every step.) -/
theorem ratchet_floor_step (p q b ea floor : Nat) (hq : 0 < q) :
    step p q b ea floor ≥ floor ∧ step p q b ea floor * q ≥ b * p :=
  ⟨step_ge_floor p q b ea floor, step_ratchet p q b ea floor hq⟩

/-- ratchet_floor, the cumulative form: after `t` periods the base satisfies
    base_t · q^t ≥ base_0 · p^t, whatever the composites and floors (so in particular under
    maximal silencing, every composite 0). -/
theorem ratchet_floor (p q : Nat) (hq : 0 < q) (b0 : Nat) (eas fls : List Nat)
    (ht : eas.length = fls.length) :
    run p q b0 eas fls * q ^ eas.length ≥ b0 * p ^ eas.length := by
  induction eas generalizing b0 fls with
  | nil => simp [run]
  | cons ea eas ih =>
    cases fls with
    | nil => simp at ht
    | cons fl fls =>
      simp only [run, List.length_cons]
      have h1 := ih (step p q b0 ea fl) fls (by simpa using ht)
      have h2 := step_ratchet p q b0 ea fl hq
      -- run * q^(n+1) = (run * q^n) * q ≥ (step * p^n) * q = (step * q) * p^n ≥ (b0 * p) * p^n
      have e1 : run p q (step p q b0 ea fl) eas fls * q ^ (eas.length + 1)
              = run p q (step p q b0 ea fl) eas fls * q ^ eas.length * q := by
        rw [Nat.pow_succ, Nat.mul_assoc]
      have e2 : b0 * p ^ (eas.length + 1) = b0 * p * p ^ eas.length := by
        rw [Nat.pow_succ, Nat.mul_comm (p ^ eas.length) p, ← Nat.mul_assoc]
      rw [e1, e2]
      have e3 : step p q b0 ea fl * p ^ eas.length * q = step p q b0 ea fl * q * p ^ eas.length := by
        rw [Nat.mul_assoc, Nat.mul_comm (p ^ eas.length) q, ← Nat.mul_assoc]
      calc b0 * p * p ^ eas.length
          ≤ step p q b0 ea fl * q * p ^ eas.length := Nat.mul_le_mul_right _ h2
        _ = step p q b0 ea fl * p ^ eas.length * q := e3.symm
        _ ≤ run p q (step p q b0 ea fl) eas fls * q ^ eas.length * q := Nat.mul_le_mul_right q h1

/-- The floor is honoured at every period, not only the last. -/
theorem run_ge_last_floor (p q b0 ea fl : Nat) (eas fls : List Nat) :
    run p q b0 (eas ++ [ea]) (fls ++ [fl]) ≥ fl ∨ eas.length ≠ fls.length := by
  by_cases h : eas.length = fls.length
  · left
    induction eas generalizing b0 fls with
    | nil => cases fls with
      | nil => simp [run]; exact step_ge_floor _ _ _ _ _
      | cons _ _ => simp at h
    | cons e es ih => cases fls with
      | nil => simp at h
      | cons f fs => simp only [List.cons_append, run]; exact ih _ fs (by simpa using h)
  · right; exact h

/-- The partition freeze: when the composite falls by more than the fraction n/d in one
    period, the base holds. `frozenStep` is the law with the freeze in front of `step`. -/
def frozenStep (n d p q b prevEA ea floor : Nat) : Nat :=
  if ea * d < prevEA * (d - n) then b else step p q b ea floor

theorem freeze_holds (n d p q b prevEA ea floor : Nat) (h : ea * d < prevEA * (d - n)) :
    frozenStep n d p q b prevEA ea floor = b := by
  unfold frozenStep; simp [h]

theorem frozenStep_ratchet (n d p q b prevEA ea floor : Nat) (hq : 0 < q) :
    frozenStep n d p q b prevEA ea floor * q ≥ b * p ∨
    frozenStep n d p q b prevEA ea floor = b := by
  unfold frozenStep
  by_cases h : ea * d < prevEA * (d - n)
  · right; simp [h]
  · left; simp [h]; exact step_ratchet p q b ea floor hq

/- ---------------- (d) the dominance bound: n_eff ---------------- -/

/-- Kish's effective count on integer masses, floored: (Σm)² / Σm². -/
def nEff (ms : List Nat) : Nat := (sum ms * sum ms) / sumsq ms

theorem two_sumsq_le (ms : List Nat) (T : Nat) (h : ∀ m ∈ ms, 2 * m ≤ T) :
    2 * sumsq ms ≤ T * sum ms := by
  induction ms with
  | nil => simp [sumsq, sum]
  | cons m rest ih =>
    simp only [sumsq, sum]
    have hm : 2 * m ≤ T := h m (by simp)
    have hr := ih (fun x hx => h x (by simp [hx]))
    have e1 : 2 * (m * m + sumsq rest) = (2 * m) * m + 2 * sumsq rest := by
      rw [Nat.mul_add, ← Nat.mul_assoc]
    have e2 : T * (m + sum rest) = T * m + T * sum rest := Nat.mul_add _ _ _
    have h3 : (2 * m) * m ≤ T * m := Nat.mul_le_mul_right m hm
    omega

theorem sumsq_pos (ms : List Nat) (h : 0 < sum ms) : 0 < sumsq ms := by
  induction ms with
  | nil => simp [sum] at h
  | cons m rest ih =>
    simp only [sum, sumsq] at *
    by_cases hm : m = 0
    · subst hm; simp at h; have := ih h; omega
    · have : 0 < m * m := Nat.mul_pos (Nat.pos_of_ne_zero hm) (Nat.pos_of_ne_zero hm)
      omega

/-- dominance_bound: if every owner holds at most half the mass (and there is mass), then
    n_eff ≥ 2 — the dominance gate's refusal of a one-owner composite, for any N. -/
theorem dominance_bound (ms : List Nat) (hpos : 0 < sum ms) (h : ∀ m ∈ ms, 2 * m ≤ sum ms) :
    2 ≤ nEff ms := by
  unfold nEff
  have hs := sumsq_pos ms hpos
  have h2 := two_sumsq_le ms (sum ms) h
  rw [Nat.le_div_iff_mul_le hs]
  omega

/-- Hence a published composite has at least two owners: a single mass fails the gate. -/
theorem dominance_needs_two (m : Nat) (hpos : 0 < m) : ¬ (∀ x ∈ [m], 2 * x ≤ sum [m]) := by
  intro h
  have := h m (by simp)
  simp [sum] at this
  omega

theorem sum_replicate_one (n : Nat) : sum (List.replicate n 1) = n := by
  induction n with
  | zero => rfl
  | succ k ih => simp [List.replicate, sum, ih]; omega

theorem sumsq_replicate_one (n : Nat) : sumsq (List.replicate n 1) = n := by
  induction n with
  | zero => rfl
  | succ k ih => simp [List.replicate, sumsq, ih]; omega

/-- Inv_OnePerOwner's consequence: with one accepted report per owner every mass is one,
    and n_eff = source_count exactly. -/
theorem n_eff_unit (n : Nat) (hn : 0 < n) : nEff (List.replicate n 1) = n := by
  unfold nEff
  rw [sum_replicate_one, sumsq_replicate_one]
  exact Nat.mul_div_cancel n hn

end CensusBallot
