/-
  MinorVoid.lean: the void of a duty appointment made to a minor (CC 3.2 at v1.0-rc21, Constitution commit
  b016df4, the user-target admission rule; the fold reason `minor_appointment_void`, CC 2.7.3). A duty-scoped
  `delegates_to` D onto T is void when a minor-band age row about T is held (assured or self-declared, live
  or retracted) and no assured adult age row about T is dated before D's `asserted_at`.
  Proved: the verdict is a function of the set of held rows; a store that keeps a running summary as rows
  arrive, in any order, reaches it; backdating D can only void it; a retraction changes nothing; a
  self-declared adult lifts nothing. With the clause "and unexpired at D's asserted_at" added, backdating
  can lift a void (`expiry_backdate_lifts`). `models/tla/MinorVoid.tla` checks the same rule under every
  interleaving TLC reaches.
-/
namespace MinorVoid

inductive Kind | self | assured | retract | duty
  deriving DecidableEq, Repr

inductive Band | minor | adult | none
  deriving DecidableEq, Repr

/-- a row about T: its kind, its band, its `asserted_at` and its `expires_at` (0: none) -/
structure Row where
  kind : Kind
  band : Band
  date : Nat
  exp : Nat
  deriving DecidableEq, Repr

def isMinor (r : Row) : Bool := (r.kind == .self || r.kind == .assured) && r.band == .minor
def isProof (r : Row) : Bool := r.kind == .assured && r.band == .adult
/-- clause 2's witness: an assured adult row dated before `d` -/
def proofBefore (d : Nat) (r : Row) : Bool := isProof r && decide (r.date < d)

/-- the rule, over the held rows `H` (a list read as a set) and D's `asserted_at` `d` -/
def void (H : List Row) (d : Nat) : Bool := H.any isMinor && !(H.any (proofBefore d))

/-- the verdict is a function of the set of held rows: two nodes holding the same rows agree -/
theorem void_of_same_rows (H₁ H₂ : List Row) (h : ∀ x, x ∈ H₁ ↔ x ∈ H₂) (d : Nat) :
    void H₁ d = void H₂ d := by
  have e : ∀ p : Row → Bool, H₁.any p = H₂.any p := by
    intro p
    apply Bool.eq_iff_iff.2
    simp only [List.any_eq_true]
    exact ⟨fun ⟨x, hx, px⟩ => ⟨x, (h x).1 hx, px⟩, fun ⟨x, hx, px⟩ => ⟨x, (h x).2 hx, px⟩⟩
  simp only [void, e]

/-- what a store keeps as rows arrive: "a minor row was seen" and the dates of the assured adult proofs -/
def step (s : Bool × List Nat) (r : Row) : Bool × List Nat :=
  (s.1 || isMinor r, if isProof r then r.date :: s.2 else s.2)

def judge (s : Bool × List Nat) (d : Nat) : Bool := s.1 && !(s.2.any (fun a => decide (a < d)))

theorem fold_summary (l : List Row) (s : Bool × List Nat) (d : Nat) :
    (l.foldl step s).1 = (s.1 || l.any isMinor) ∧
    (((l.foldl step s).2.any (fun a => decide (a < d))) =
      (s.2.any (fun a => decide (a < d)) || l.any (proofBefore d))) := by
  induction l generalizing s with
  | nil => simp
  | cons r rs ih =>
    obtain ⟨h1, h2⟩ := ih (step s r)
    simp only [List.foldl_cons]
    refine ⟨?_, ?_⟩
    · rw [h1]; simp only [step, List.any_cons, Bool.or_assoc]
    · rw [h2]
      simp only [step, List.any_cons, proofBefore]
      cases hp : isProof r <;> simp [List.any_cons, Bool.or_assoc, Bool.or_comm, Bool.or_left_comm]

/-- the running summary, folded over any arrival order, gives the rule over the rows that arrived -/
theorem incremental_is_void (arrivals : List Row) (d : Nat) :
    judge (arrivals.foldl step (false, [])) d = void arrivals d := by
  obtain ⟨h1, h2⟩ := fold_summary arrivals (false, []) d
  simp only [judge, void, h1, h2]
  simp

/-- order-independence: two arrival orders of the same rows give the same verdict -/
theorem any_order (o₁ o₂ : List Row) (h : ∀ x, x ∈ o₁ ↔ x ∈ o₂) (d : Nat) :
    judge (o₁.foldl step (false, [])) d = judge (o₂.foldl step (false, [])) d := by
  rw [incremental_is_void, incremental_is_void]; exact void_of_same_rows o₁ o₂ h d

/-- backdating D can only void it, never lift a void -/
theorem backdate_only_voids (H : List Row) (d₁ d₂ : Nat) (hle : d₁ ≤ d₂) (hv : void H d₂ = true) :
    void H d₁ = true := by
  simp only [void, Bool.and_eq_true, Bool.not_eq_true'] at hv ⊢
  refine ⟨hv.1, ?_⟩
  apply Bool.eq_false_iff.2
  intro h1
  rw [List.any_eq_true] at h1
  obtain ⟨x, hx, px⟩ := h1
  have : H.any (proofBefore d₂) = true := by
    rw [List.any_eq_true]
    refine ⟨x, hx, ?_⟩
    simp only [proofBefore, Bool.and_eq_true, decide_eq_true_eq] at px ⊢
    exact ⟨px.1, Nat.lt_of_lt_of_le px.2 hle⟩
  rw [hv.2] at this; exact Bool.noConfusion this

theorem any_filter_irrelevant (H : List Row) (p q : Row → Bool) (hq : ∀ r, q r = false → p r = false) :
    (H.filter q).any p = H.any p := by
  induction H with
  | nil => rfl
  | cons r rs ih =>
    simp only [List.filter_cons, List.any_cons]
    cases h : q r
    · simp only [Bool.false_eq_true, ite_false, ih, hq r h, Bool.false_or]
    · simp only [ite_true, List.any_cons, ih]

/-- a retraction changes no verdict, so a retracted minor row still counts -/
theorem retraction_changes_nothing (H : List Row) (d : Nat) :
    void (H.filter (fun r => !(r.kind == .retract))) d = void H d := by
  have hm := any_filter_irrelevant H isMinor (fun r => !(r.kind == .retract)) (by
    intro r h; simp only [Bool.not_eq_false', beq_iff_eq] at h; simp [isMinor, h])
  have hp := any_filter_irrelevant H (proofBefore d) (fun r => !(r.kind == .retract)) (by
    intro r h; simp only [Bool.not_eq_false', beq_iff_eq] at h; simp [proofBefore, isProof, h])
  simp only [void, hm, hp]

/-- a self-declared adult row lifts nothing: dropping every one leaves every verdict as it was -/
theorem self_adult_lifts_nothing (H : List Row) (d : Nat) :
    void (H.filter (fun r => !(r.kind == .self && r.band == .adult))) d = void H d := by
  have hm := any_filter_irrelevant H isMinor (fun r => !(r.kind == .self && r.band == .adult)) (by
    intro r h; simp only [Bool.not_eq_false', Bool.and_eq_true, beq_iff_eq] at h; simp [isMinor, h.2])
  have hp := any_filter_irrelevant H (proofBefore d) (fun r => !(r.kind == .self && r.band == .adult)) (by
    intro r h; simp only [Bool.not_eq_false', Bool.and_eq_true, beq_iff_eq] at h; simp [proofBefore, isProof, h.1])
  simp only [void, hm, hp]

/-- a minor row superseded by its own signer's newer adult row still voids: T's self-declared minor at 1,
  then T's self-declared adult at 2, no assured proof -/
theorem superseded_minor_voids :
    void [⟨.self, .minor, 1, 0⟩, ⟨.self, .adult, 2, 0⟩] 3 = true := by decide

/-- clause 2 with "and unexpired at D's asserted_at" added (persist's K2-fix14 reading) -/
def proofBeforeLive (d : Nat) (r : Row) : Bool :=
  isProof r && decide (r.date < d) && (r.exp == 0 || decide (r.exp > d))
def voidExp (H : List Row) (d : Nat) : Bool := H.any isMinor && !(H.any (proofBeforeLive d))

/-- with the expiry clause, backdating can lift a void: a self-declared minor at 1, an assured adult at 2
  expiring at 4; D dated 4 is void, the same D dated 3 is not -/
theorem expiry_backdate_lifts :
    voidExp [⟨.self, .minor, 1, 0⟩, ⟨.assured, .adult, 2, 4⟩] 4 = true ∧
    voidExp [⟨.self, .minor, 1, 0⟩, ⟨.assured, .adult, 2, 4⟩] 3 = false := by decide

end MinorVoid

#print axioms MinorVoid.void_of_same_rows
#print axioms MinorVoid.fold_summary
#print axioms MinorVoid.incremental_is_void
#print axioms MinorVoid.any_order
#print axioms MinorVoid.backdate_only_voids
#print axioms MinorVoid.any_filter_irrelevant
#print axioms MinorVoid.retraction_changes_nothing
#print axioms MinorVoid.self_adult_lifts_nothing
#print axioms MinorVoid.superseded_minor_voids
#print axioms MinorVoid.expiry_backdate_lifts
