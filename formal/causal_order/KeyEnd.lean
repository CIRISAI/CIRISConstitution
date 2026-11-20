/-
  KeyEnd.lean — a key's own end, read from its records and now

  A key record states `vu` (its `valid_until`); `vf` is the record's own signed instant. Its bound is
  self-contained: `vf < vu` and `vu - vf ≤ C`, read from the record alone (it covers `vf ≤ t < vu`). A key is LIVE at `now` when some record of it, within the bound,
  covers `now`. A key has ENDED at `now` when every record of it within the bound ends by `now`.

  Proved here, over a list of records (the rows a node holds, in any order):
    bound_reads_row     the bound is a function of the record alone
    live_perm           liveness does not depend on the order the records are held in
    live_mono           a further record never ends a live key (a renewal only extends)
    live_own_rows       records of other keys change nothing: only the key's own record revives it
    live_le_ceiling     a live key is within the ceiling of some valid_from it stated
    ended_stays_ended   with the same records, a key ended at `now` is live at no later instant
    ended_not_live      an ended key is not live
  and, over rotation links (`Link`, `ofIss`: a statement's key is a key of the identity `iss` it states):
    ofIss_genesis       the genesis key is a key of its identity, whatever is held
    ofIss_perm          the answer does not depend on the order the links are held in
    ofIss_mono          a further link never takes a key out of its identity
    ofIss_unrelated     a key that is not iss and is the new key of no signed link of iss is never of iss
    ofIss_needs_old     a link without its predecessor's statement adds nothing
    ofIss_successor     one signed link from the genesis key makes its successor a key of iss
  What this file does not show: that a renewal was signed before the end. No function of the records and now
  can, since a back-dated renewal is the same record (formal/causal_kernel/check_key_end.py, the in-time section).

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports nothing.
-/

namespace KeyEnd

structure Rec where
  key : Nat
  vf : Nat
  vu : Nat
deriving DecidableEq

def boundOk (C : Nat) (r : Rec) : Bool := decide (r.vf < r.vu) && decide (r.vu - r.vf ≤ C)

def covers (now : Nat) (r : Rec) : Bool := decide (r.vf ≤ now) && decide (now < r.vu)

def mine (C k : Nat) (r : Rec) : Bool := (r.key == k) && boundOk C r

def live (C : Nat) (rs : List Rec) (k now : Nat) : Bool := rs.any (fun r => mine C k r && covers now r)

def ended (C : Nat) (rs : List Rec) (k now : Nat) : Bool := rs.all (fun r => !mine C k r || decide (r.vu ≤ now))

/-- The bound reads the record and nothing else. -/
theorem bound_reads_row (C : Nat) (r s : Rec) (h : r = s) : boundOk C r = boundOk C s := by
  subst h; rfl

theorem any_perm {α} (p : α → Bool) {l l' : List α} (h : l.Perm l') : l.any p = l'.any p := by
  induction h with
  | nil => rfl
  | cons x _ ih => simp [List.any, ih]
  | swap x y l => simp [List.any]; cases p x <;> cases p y <;> simp
  | trans _ _ ih1 ih2 => exact ih1.trans ih2

theorem live_perm (C : Nat) {rs rs' : List Rec} (h : rs.Perm rs') (k now : Nat) :
    live C rs k now = live C rs' k now := any_perm _ h

theorem live_mono (C : Nat) (rs more : List Rec) (k now : Nat) (h : live C rs k now = true) :
    live C (rs ++ more) k now = true := by
  simp only [live, List.any_append, Bool.or_eq_true]; exact Or.inl h

theorem live_own_rows (C : Nat) (rs : List Rec) (k now : Nat) :
    live C (rs.filter (fun r => r.key == k)) k now = live C rs k now := by
  induction rs with
  | nil => rfl
  | cons r rs ih =>
    by_cases hk : (r.key == k) = true
    · simp [List.filter, hk, List.any, live] at ih ⊢; rw [ih]
    · have : (r.key == k) = false := by simpa using hk
      simp [List.filter, this, live, mine] at ih ⊢; exact ih

theorem live_le_ceiling (C : Nat) (rs : List Rec) (k now : Nat) (h : live C rs k now = true) :
    ∃ r ∈ rs, r.key = k ∧ now < r.vf + C := by
  simp only [live, List.any_eq_true] at h
  obtain ⟨r, hr, hm⟩ := h
  simp [mine, boundOk, covers] at hm
  obtain ⟨⟨hk, h1, h2⟩, _, h4⟩ := hm
  exact ⟨r, hr, hk, by omega⟩

theorem ended_not_live (C : Nat) (rs : List Rec) (k now : Nat) (h : ended C rs k now = true) :
    live C rs k now = false := by
  simp only [ended, List.all_eq_true] at h
  cases hl : live C rs k now
  · rfl
  · simp only [live, List.any_eq_true] at hl
    obtain ⟨r, hr, hm⟩ := hl
    have := h r hr
    simp [mine, covers] at hm this
    obtain ⟨⟨hk, hb⟩, _, h4⟩ := hm
    rcases this with (h1 | h1) | h1
    · exact absurd hk h1
    · rw [hb] at h1; exact absurd h1 (by decide)
    · omega

theorem ended_stays_ended (C : Nat) (rs : List Rec) (k now now' : Nat) (h : ended C rs k now = true)
    (hle : now ≤ now') : live C rs k now' = false := by
  apply ended_not_live
  simp only [ended, List.all_eq_true] at h ⊢
  intro r hr
  have := h r hr
  cases hm : mine C k r <;> simp [hm] at this ⊢
  omega

/-! ## The key of an identity: a statement's key against the `iss` it states

A rotation record (`Link`) is a record of the key `new`, of the identity `iss`, naming its predecessor key `old`'s
record and carrying a statement by `old` made inside that record (`byOld`). A key is a key of `iss` when it is
`iss`'s genesis key or a link of `iss` with the old key's statement reaches it from a key of `iss`. `n` bounds the
walk (the number of links held suffices).
-/

structure Link where
  new : Nat
  old : Nat
  iss : Nat
  byOld : Bool
deriving DecidableEq

def ofIss (ls : List Link) (iss : Nat) : Nat → Nat → Bool
  | 0, k => k == iss
  | n + 1, k => k == iss || ls.any (fun l => l.new == k && l.iss == iss && l.byOld && ofIss ls iss n l.old)

/-- The genesis key is a key of its identity, whatever is held. -/
theorem ofIss_genesis (ls : List Link) (iss n : Nat) : ofIss ls iss n iss = true := by
  cases n <;> simp [ofIss]

/-- The answer does not depend on the order the records are held in. -/
theorem ofIss_perm {ls ls' : List Link} (h : ls.Perm ls') (iss : Nat) :
    ∀ n k, ofIss ls iss n k = ofIss ls' iss n k := by
  intro n
  induction n with
  | zero => intro k; rfl
  | succ n ih =>
    intro k
    simp only [ofIss]
    have : (ls.any fun l => l.new == k && l.iss == iss && l.byOld && ofIss ls iss n l.old)
         = (ls'.any fun l => l.new == k && l.iss == iss && l.byOld && ofIss ls iss n l.old) := any_perm _ h
    rw [this]
    congr 1
    congr 1
    funext l
    rw [ih l.old]

/-- A further record never takes a key out of its identity: an answer of Valid stays Valid. -/
theorem ofIss_mono (ls more : List Link) (iss : Nat) :
    ∀ n k, ofIss ls iss n k = true → ofIss (ls ++ more) iss n k = true := by
  intro n
  induction n with
  | zero => intro k h; simpa [ofIss] using h
  | succ n ih =>
    intro k h
    simp only [ofIss, Bool.or_eq_true, List.any_eq_true, Bool.and_eq_true, List.any_append] at h ⊢
    rcases h with h | ⟨l, hl, ⟨⟨⟨h1, h2⟩, h3⟩, h4⟩⟩
    · exact Or.inl h
    · exact Or.inr (Or.inl ⟨l, hl, ⟨⟨⟨h1, h2⟩, h3⟩, ih _ h4⟩⟩)

/-- An unrelated key is never a key of `iss`: a key that is not `iss` and is the new key of no link of `iss`
carrying its predecessor's statement does not count, however many links are held. -/
theorem ofIss_unrelated (ls : List Link) (iss k : Nat) (hk : k ≠ iss)
    (hno : ∀ l ∈ ls, l.new = k → l.iss = iss → l.byOld = false) : ∀ n, ofIss ls iss n k = false := by
  intro n
  cases n with
  | zero => simp [ofIss, hk]
  | succ n =>
    simp only [ofIss, Bool.or_eq_false_iff, List.any_eq_false]
    refine ⟨by simp [hk], ?_⟩
    intro l hl
    by_cases h1 : l.new = k
    · by_cases h2 : l.iss = iss
      · simp [hno l hl h1 h2]
      · simp [h2]
    · simp [h1]

/-- A link without its predecessor's statement adds nothing. -/
theorem ofIss_needs_old (ls : List Link) (l : Link) (hl : l.byOld = false) (iss : Nat) :
    ∀ n k, ofIss (l :: ls) iss n k = ofIss ls iss n k := by
  intro n
  induction n with
  | zero => intro k; rfl
  | succ n ih =>
    intro k
    simp only [ofIss, List.any_cons, hl, Bool.and_false, Bool.false_and, Bool.false_or]
    congr 1
    congr 1
    funext m
    rw [ih m.old]

/-- A successor is not refused: one link of `iss`, carrying the genesis key's statement, makes its key a key of
`iss` (the reader that admits only the genesis key fails this). -/
theorem ofIss_successor (ls : List Link) (l : Link) (iss n : Nat) (h1 : l.old = iss) (h2 : l.iss = iss)
    (h3 : l.byOld = true) (hl : l ∈ ls) : ofIss ls iss (n + 1) l.new = true := by
  simp only [ofIss, Bool.or_eq_true, List.any_eq_true, Bool.and_eq_true]
  refine Or.inr ⟨l, hl, ⟨⟨⟨by simp, by simp [h2]⟩, h3⟩, ?_⟩⟩
  rw [h1]; exact ofIss_genesis ls iss n

end KeyEnd

#print axioms KeyEnd.live_perm
#print axioms KeyEnd.live_mono
#print axioms KeyEnd.live_own_rows
#print axioms KeyEnd.live_le_ceiling
#print axioms KeyEnd.ended_not_live
#print axioms KeyEnd.ended_stays_ended
#print axioms KeyEnd.bound_reads_row
#print axioms KeyEnd.ofIss_genesis
#print axioms KeyEnd.ofIss_perm
#print axioms KeyEnd.ofIss_mono
#print axioms KeyEnd.ofIss_unrelated
#print axioms KeyEnd.ofIss_needs_old
#print axioms KeyEnd.ofIss_successor
