/-
  OnionLayersCount.lean — the counting bounds of the onion layer deal (CC 5.4.6 item 4),
  for any N. The TLA+ model (OnionLayers.tla) checks the deal's invariants on small
  instances for every hash; this file proves the arithmetic they rest on in general.

  A layer holds `s` seat-like relays (serve seats and conferred infra:relay standings)
  and `n` others, dealt under the cap `n ≤ c * s` (c the steward's cap factor, default 2).
  Core Lean 4.14, no Mathlib, no `sorry`; every theorem closes by `omega` over the
  products named as atoms.
-/

namespace OnionLayers

/-- A layer's dealt counts and the cap they were dealt under. -/
structure Layer where
  s : Nat          -- seat-like members
  n : Nat          -- other members
  c : Nat          -- the cap factor
  cap : n ≤ c * s  -- the cap the deal enforced (Inv_HostileShareBound, first conjunct)

/-- Layer size. -/
def Layer.size (L : Layer) : Nat := L.s + L.n

/-- The hostile share bound: whatever subset `h ≤ n` of the others is hostile,
    `h * (1 + c) ≤ c * size`, i.e. the hostile share is at most c / (1 + c). -/
theorem hostile_share_bound (L : Layer) (h : Nat) (hh : h ≤ L.n) :
    h * (1 + L.c) ≤ L.c * L.size := by
  unfold Layer.size
  have cap := L.cap
  have e1 : h * (1 + L.c) = h + h * L.c := by rw [Nat.mul_add, Nat.mul_one]
  have e2 : L.c * (L.s + L.n) = L.c * L.s + L.c * L.n := Nat.mul_add _ _ _
  have e3 : h * L.c ≤ L.n * L.c := Nat.mul_le_mul_right _ hh
  have e4 : L.n * L.c = L.c * L.n := Nat.mul_comm _ _
  omega

/-- A layer's size is at most (1 + c) × its seat-like count: capacity grows with
    seat-like members, never with others alone. -/
theorem size_le (L : Layer) : L.size ≤ (1 + L.c) * L.s := by
  unfold Layer.size
  have cap := L.cap
  have e : (1 + L.c) * L.s = L.s + L.c * L.s := by rw [Nat.add_mul, Nat.one_mul]
  omega

/-- A layer with no seat-like member is empty under any cap. -/
theorem no_seat_no_layer (L : Layer) (h0 : L.s = 0) : L.size = 0 := by
  unfold Layer.size
  have cap := L.cap
  rw [h0] at cap
  simp at cap
  omega

/-- The floor (three per layer) therefore needs a seat-like member in every layer,
    and across three layers at least three seat-like relays in the deal. -/
theorem floor_needs_a_seat (L : Layer) (floor : 3 ≤ L.size) : 1 ≤ L.s := by
  cases hs : L.s with
  | zero => have := no_seat_no_layer L hs; omega
  | succ k => omega

theorem floor_needs_three_seats (L0 L1 L2 : Layer)
    (f0 : 3 ≤ L0.size) (f1 : 3 ≤ L1.size) (f2 : 3 ≤ L2.size) :
    3 ≤ L0.s + L1.s + L2.s := by
  have := floor_needs_a_seat L0 f0
  have := floor_needs_a_seat L1 f1
  have := floor_needs_a_seat L2 f2
  omega

/-- The crowd arithmetic for any N: with `S` seat-like relays dealt round-robin over three
    layers and `O` others, the dealt total is at most `S + min O (c * S)`, hence at most
    `(1 + c) * S`; everyone else waits for the next period. -/
def dealtMax (S O c : Nat) : Nat := S + min O (c * S)

theorem dealt_le (S O c : Nat) : dealtMax S O c ≤ (1 + c) * S := by
  unfold dealtMax
  have e : (1 + c) * S = S + c * S := by rw [Nat.add_mul, Nat.one_mul]
  have := Nat.min_le_right O (c * S)
  omega

theorem dealt_le_all (S O c : Nat) : dealtMax S O c ≤ S + O := by
  unfold dealtMax
  have := Nat.min_le_left O (c * S)
  omega

/-- Raising the cap factor never lowers the dealt total (Inv_NeverWorse in the cap). -/
theorem dealt_mono_c (S O c c' : Nat) (hc : c ≤ c') : dealtMax S O c ≤ dealtMax S O c' := by
  unfold dealtMax
  have : c * S ≤ c' * S := Nat.mul_le_mul_right _ hc
  have h1 := Nat.min_le_left O (c * S)
  have h2 := Nat.min_le_right O (c * S)
  have h3 : min O (c * S) ≤ min O (c' * S) := by
    apply Nat.le_min.mpr
    exact ⟨h1, Nat.le_trans h2 this⟩
  omega

/-- Adding a seat-like relay never lowers the dealt total. -/
theorem dealt_mono_seats (S O c : Nat) : dealtMax S O c ≤ dealtMax (S + 1) O c := by
  unfold dealtMax
  have : c * S ≤ c * (S + 1) := Nat.mul_le_mul_left _ (Nat.le_succ S)
  have h1 := Nat.min_le_left O (c * S)
  have h2 := Nat.min_le_right O (c * S)
  have h3 : min O (c * S) ≤ min O (c * (S + 1)) := by
    apply Nat.le_min.mpr
    exact ⟨h1, Nat.le_trans h2 this⟩
  omega

end OnionLayers
