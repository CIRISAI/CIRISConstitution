/-
  MinorVoid.lean: the void of a duty appointment made to a minor (CC 3.2 at v1.0-rc21, Constitution commit
  b016df4, the user-target admission rule; the fold reason `minor_appointment_void`, CC 2.7.3), as ruled on
  2026-11-20. A duty-scoped `delegates_to` D onto T is void when a minor-band age row about T is held (assured
  or self-declared, live or retracted) and no UN-RETRACTED assured adult age row about T is dated before D's
  `asserted_at`.
  Proved: the verdict is a function of the set of held rows; a store that keeps a running summary as rows
  arrive, in any order, reaches it; backdating D can only void it; a retraction of a minor row changes
  nothing; a retracted adult proof lifts nothing; a self-declared adult lifts nothing. With the clause "and
  unexpired at D's asserted_at" added, backdating can lift a void (`expiry_backdate_lifts`, kept as the
  reason that clause was withdrawn). `models/tla/MinorVoid.tla` checks the same rule under every
  interleaving TLC reaches.
-/
namespace MinorVoid

inductive Kind | self | assured | retract | duty
  deriving DecidableEq, Repr

inductive Band | minor | adult | none
  deriving DecidableEq, Repr

/-- a row about T: its kind, its band, its `asserted_at`, its `expires_at` (0: none), its id, and for a
  retraction the id of the row it names -/
structure Row where
  kind : Kind
  band : Band
  date : Nat
  exp : Nat
  id : Nat
  tgt : Nat
  deriving DecidableEq, Repr

@[simp] theorem kind_ra : (Kind.retract == Kind.assured) = false := by decide
@[simp] theorem kind_rs : (Kind.retract == Kind.self) = false := by decide
@[simp] theorem kind_ar : (Kind.assured == Kind.retract) = false := by decide
@[simp] theorem band_nm : (Band.none == Band.minor) = false := by decide
@[simp] theorem band_na : (Band.none == Band.adult) = false := by decide
@[simp] theorem band_am : (Band.adult == Band.minor) = false := by decide

def isMinor (r : Row) : Bool := (r.kind == .self || r.kind == .assured) && r.band == .minor
def isProof (r : Row) : Bool := r.kind == .assured && r.band == .adult
def isRetractionOf (x r : Row) : Bool := x.kind == .retract && x.tgt == r.id
/-- a held retraction names `r` -/
def retractedIn (L : List Row) (r : Row) : Bool := L.any (fun x => isRetractionOf x r)
/-- an assured adult row dated before `d` -/
def proofBefore (d : Nat) (r : Row) : Bool := isProof r && decide (r.date < d)
/-- clause 2's witness: an un-retracted assured adult row dated before `d` -/
def liveProof (L : List Row) (d : Nat) (r : Row) : Bool := proofBefore d r && !retractedIn L r

/-- the rule, over the held rows `H` (a list read as a set) and D's `asserted_at` `d` -/
def void (H : List Row) (d : Nat) : Bool := H.any isMinor && !(H.any (liveProof H d))

theorem any_mem_congr (L₁ L₂ : List Row) (h : ∀ x, x ∈ L₁ ↔ x ∈ L₂) (p : Row → Bool) :
    L₁.any p = L₂.any p := by
  apply Bool.eq_iff_iff.2
  simp only [List.any_eq_true]
  exact ⟨fun ⟨x, hx, px⟩ => ⟨x, (h x).1 hx, px⟩, fun ⟨x, hx, px⟩ => ⟨x, (h x).2 hx, px⟩⟩

/-- over a sublist `F` of the rows of `L` with property `rel`, a predicate that implies `rel` finds the same -/
theorem any_sub_congr (F L : List Row) (rel : Row → Bool) (hF : ∀ x, x ∈ F ↔ x ∈ L ∧ rel x = true)
    (p : Row → Bool) (hp : ∀ x, p x = true → rel x = true) : F.any p = L.any p := by
  apply Bool.eq_iff_iff.2
  simp only [List.any_eq_true]
  constructor
  · rintro ⟨x, hx, px⟩; exact ⟨x, ((hF x).1 hx).1, px⟩
  · rintro ⟨x, hx, px⟩; exact ⟨x, (hF x).2 ⟨hx, hp x px⟩, px⟩

theorem any_fun_congr (L : List Row) (p q : Row → Bool) (h : ∀ x, x ∈ L → p x = q x) :
    L.any p = L.any q := by
  induction L with
  | nil => rfl
  | cons r rs ih =>
    simp only [List.any_cons]
    rw [h r (List.mem_cons_self r rs), ih (fun x hx => h x (List.mem_cons_of_mem r hx))]

/-- the verdict is a function of the set of held rows: two nodes holding the same rows agree -/
theorem void_of_same_rows (H₁ H₂ : List Row) (h : ∀ x, x ∈ H₁ ↔ x ∈ H₂) (d : Nat) :
    void H₁ d = void H₂ d := by
  have hr : retractedIn H₁ = retractedIn H₂ := by
    funext r; exact any_mem_congr H₁ H₂ h _
  have hl : liveProof H₁ d = liveProof H₂ d := by
    funext r; simp only [liveProof, hr]
  simp only [void, hl, any_mem_congr H₁ H₂ h]

/-- the rows a store keeps besides "a minor row was seen": the assured adult proofs and the retractions -/
def relevant (r : Row) : Bool := isProof r || r.kind == .retract

def step (s : Bool × List Row) (r : Row) : Bool × List Row :=
  (s.1 || isMinor r, if relevant r then r :: s.2 else s.2)

def judge (s : Bool × List Row) (d : Nat) : Bool := s.1 && !(s.2.any (liveProof s.2 d))

theorem fold_minor (l : List Row) (s : Bool × List Row) :
    (l.foldl step s).1 = (s.1 || l.any isMinor) := by
  induction l generalizing s with
  | nil => simp
  | cons r rs ih => simp only [List.foldl_cons, ih, step, List.any_cons, Bool.or_assoc]

theorem fold_mem (l : List Row) (s : Bool × List Row) (x : Row) :
    x ∈ (l.foldl step s).2 ↔ x ∈ s.2 ∨ (x ∈ l ∧ relevant x = true) := by
  induction l generalizing s with
  | nil => simp
  | cons r rs ih =>
    simp only [List.foldl_cons]
    rw [ih (step s r)]
    simp only [step, List.mem_cons]
    by_cases hr : relevant r = true
    · simp only [hr, ite_true, List.mem_cons]
      constructor
      · rintro ((rfl | h) | ⟨h1, h2⟩)
        · exact Or.inr ⟨Or.inl rfl, hr⟩
        · exact Or.inl h
        · exact Or.inr ⟨Or.inr h1, h2⟩
      · rintro (h | ⟨(rfl | h1), h2⟩)
        · exact Or.inl (Or.inr h)
        · exact Or.inl (Or.inl rfl)
        · exact Or.inr ⟨h1, h2⟩
    · simp only [hr, Bool.false_eq_true, ite_false]
      constructor
      · rintro (h | ⟨h1, h2⟩)
        · exact Or.inl h
        · exact Or.inr ⟨Or.inr h1, h2⟩
      · rintro (h | ⟨(rfl | h1), h2⟩)
        · exact Or.inl h
        · exact absurd h2 hr
        · exact Or.inr ⟨h1, h2⟩

/-- the running summary, folded over any arrival order, gives the rule over the rows that arrived -/
theorem incremental_is_void (arrivals : List Row) (d : Nat) :
    judge (arrivals.foldl step (false, [])) d = void arrivals d := by
  have hF : ∀ x, x ∈ (arrivals.foldl step (false, [])).2 ↔ x ∈ arrivals ∧ relevant x = true := by
    intro x; rw [fold_mem]; simp
  have hr : retractedIn (arrivals.foldl step (false, [])).2 = retractedIn arrivals := by
    funext r
    exact any_sub_congr _ _ relevant hF _ (by
      intro x hx; simp only [isRetractionOf, Bool.and_eq_true, beq_iff_eq] at hx; simp [relevant, hx.1])
  have hl : liveProof (arrivals.foldl step (false, [])).2 d = liveProof arrivals d := by
    funext r; simp only [liveProof, hr]
  have ha : (arrivals.foldl step (false, [])).2.any (liveProof arrivals d) = arrivals.any (liveProof arrivals d) :=
    any_sub_congr _ _ relevant hF _ (by
      intro x hx
      simp only [liveProof, proofBefore, Bool.and_eq_true] at hx
      simp [relevant, hx.1.1])
  simp only [judge, void, hl, ha, fold_minor]
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
  have : H.any (liveProof H d₂) = true := by
    rw [List.any_eq_true]
    refine ⟨x, hx, ?_⟩
    simp only [liveProof, proofBefore, Bool.and_eq_true, decide_eq_true_eq] at px ⊢
    exact ⟨⟨px.1.1, Nat.lt_of_lt_of_le px.1.2 hle⟩, px.2⟩
  rw [hv.2] at this; exact Bool.noConfusion this

/-- a retraction of a minor row changes no verdict, so a retracted minor row still counts (given that the
  minor row's id names no assured adult row) -/
theorem minor_retraction_changes_nothing (H : List Row) (d date i : Nat) (m : Row) (_hm : isMinor m = true)
    (hid : ∀ p, p ∈ H → isProof p = true → p.id ≠ m.id) :
    void (⟨.retract, .none, date, 0, i, m.id⟩ :: H) d = void H d := by
  have hl : H.any (liveProof (⟨.retract, .none, date, 0, i, m.id⟩ :: H) d) = H.any (liveProof H d) := by
    apply any_fun_congr
    intro q hq
    simp only [liveProof, retractedIn, List.any_cons]
    cases hp : isProof q
    · simp [proofBefore, hp]
    · have hne := hid q hq hp
      have e : (m.id == q.id) = false := by rw [beq_eq_false_iff_ne]; exact Ne.symm hne
      simp [isRetractionOf, e]
  simp only [void, List.any_cons, hl]
  simp [isMinor, liveProof, proofBefore, isProof, beq_iff_eq]

/-- a retracted assured adult proof lifts nothing: holding a proof together with its retraction leaves every
  verdict as it was without either (given that the proof's id names no other assured adult row) -/
theorem retracted_proof_lifts_nothing (H : List Row) (d date i : Nat) (p : Row) (hp : isProof p = true)
    (hid : ∀ q, q ∈ H → isProof q = true → q.id ≠ p.id) :
    void (⟨.retract, .none, date, 0, i, p.id⟩ :: p :: H) d = void H d := by
  have hk : p.kind = .assured ∧ p.band = .adult := by
    simp only [isProof, Bool.and_eq_true, beq_iff_eq] at hp; exact hp
  have hl : H.any (liveProof (⟨.retract, .none, date, 0, i, p.id⟩ :: p :: H) d) = H.any (liveProof H d) := by
    apply any_fun_congr
    intro q hq
    simp only [liveProof, retractedIn, List.any_cons]
    cases hq' : isProof q
    · simp [proofBefore, hq']
    · have hne := hid q hq hq'
      have e : (p.id == q.id) = false := by rw [beq_eq_false_iff_ne]; exact Ne.symm hne
      simp [isRetractionOf, e, hk.1, beq_iff_eq]
  have hself : liveProof (⟨.retract, .none, date, 0, i, p.id⟩ :: p :: H) d p = false := by
    simp [liveProof, retractedIn, isRetractionOf]
  simp only [void, List.any_cons, hl, hself]
  simp [isMinor, liveProof, proofBefore, isProof, hk.1, hk.2, beq_iff_eq]

/-- the same, on rows: a minor row and a proof dated 2 (id 5) leave D dated 3 seated; the proof's
  retraction voids it -/
theorem retracted_proof_voids_example :
    void [⟨.self, .minor, 1, 0, 1, 0⟩, ⟨.assured, .adult, 2, 0, 5, 0⟩] 3 = false ∧
    void [⟨.self, .minor, 1, 0, 1, 0⟩, ⟨.assured, .adult, 2, 0, 5, 0⟩, ⟨.retract, .none, 4, 0, 6, 5⟩] 3 = true := by
  decide

/-- a self-declared adult row lifts nothing: dropping every one leaves every verdict as it was -/
theorem self_adult_lifts_nothing (H : List Row) (d : Nat) :
    void (H.filter (fun r => !(r.kind == .self && r.band == .adult))) d = void H d := by
  let keep := fun r : Row => !(r.kind == .self && r.band == .adult)
  have hF : ∀ x, x ∈ H.filter keep ↔ x ∈ H ∧ keep x = true := fun x => List.mem_filter
  have hr : retractedIn (H.filter keep) = retractedIn H := by
    funext r
    exact any_sub_congr _ _ keep hF _ (by
      intro x hx; simp only [isRetractionOf, Bool.and_eq_true, beq_iff_eq] at hx; simp [keep, hx.1])
  have hl : liveProof (H.filter keep) d = liveProof H d := by
    funext r; simp only [liveProof, hr]
  have ha : (H.filter keep).any (liveProof H d) = H.any (liveProof H d) :=
    any_sub_congr _ _ keep hF _ (by
      intro x hx
      simp only [liveProof, proofBefore, isProof, Bool.and_eq_true, beq_iff_eq] at hx
      simp [keep, hx.1.1.1])
  have hm : (H.filter keep).any isMinor = H.any isMinor :=
    any_sub_congr _ _ keep hF _ (by
      intro x hx; simp only [isMinor, Bool.and_eq_true, beq_iff_eq] at hx; simp [keep, hx.2])
  show void (H.filter keep) d = void H d
  simp only [void, hl, ha, hm]

/-- a minor row superseded by its own signer's newer adult row still voids: T's self-declared minor at 1,
  then T's self-declared adult at 2, no assured proof -/
theorem superseded_minor_voids :
    void [⟨.self, .minor, 1, 0, 1, 0⟩, ⟨.self, .adult, 2, 0, 2, 0⟩] 3 = true := by decide

/-- clause 2 with "and unexpired at D's asserted_at" added (persist's K2-fix14 reading, withdrawn) -/
def proofBeforeLive (d : Nat) (r : Row) : Bool :=
  isProof r && decide (r.date < d) && (r.exp == 0 || decide (r.exp > d))
def voidExp (H : List Row) (d : Nat) : Bool := H.any isMinor && !(H.any (proofBeforeLive d))

/-- with the expiry clause, backdating can lift a void: a self-declared minor at 1, an assured adult at 2
  expiring at 4; D dated 4 is void, the same D dated 3 is not -/
theorem expiry_backdate_lifts :
    voidExp [⟨.self, .minor, 1, 0, 1, 0⟩, ⟨.assured, .adult, 2, 4, 2, 0⟩] 4 = true ∧
    voidExp [⟨.self, .minor, 1, 0, 1, 0⟩, ⟨.assured, .adult, 2, 4, 2, 0⟩] 3 = false := by decide

end MinorVoid

#print axioms MinorVoid.any_mem_congr
#print axioms MinorVoid.any_sub_congr
#print axioms MinorVoid.any_fun_congr
#print axioms MinorVoid.void_of_same_rows
#print axioms MinorVoid.fold_minor
#print axioms MinorVoid.fold_mem
#print axioms MinorVoid.incremental_is_void
#print axioms MinorVoid.any_order
#print axioms MinorVoid.backdate_only_voids
#print axioms MinorVoid.minor_retraction_changes_nothing
#print axioms MinorVoid.retracted_proof_lifts_nothing
#print axioms MinorVoid.retracted_proof_voids_example
#print axioms MinorVoid.self_adult_lifts_nothing
#print axioms MinorVoid.superseded_minor_voids
#print axioms MinorVoid.expiry_backdate_lifts
