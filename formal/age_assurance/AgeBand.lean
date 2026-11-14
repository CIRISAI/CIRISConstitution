/-
  formal/age_assurance — the band a person is read at, from the rows on record (CC 3.4.11, CC 3.4.13).

  Rows about one identity come at three levels: the person's own declaration (`self`), and a
  witness's attestation at `provider` or `government`. A reader unions them, takes the highest
  level on record, and reads the band that level states. The questions this file settles:

    * with no row on record, which band? The most protective: `under13` (fail-secure);
    * can a person's own declaration lift them? Never above the band they would be read at
      without it; it can only lower;
    * does the device matter? No: the band is a function of the rows about the identity, so
      every key of the self roster reads the same band;
    * does anything but a witness row reach `adult`? No.

  Lean 4 core, no Mathlib.  Run: `lean AgeBand.lean` (exit 0, no `sorry`).
-/

inductive Band | under13 | b13_15 | b16_17 | adult
  deriving DecidableEq, Repr

/-- Autonomy grows with the band: under13 < 13–15 < 16–17 < adult. -/
def Band.rank : Band → Nat
  | .under13 => 0 | .b13_15 => 1 | .b16_17 => 2 | .adult => 3

inductive Level | self | provider | government
  deriving DecidableEq, Repr

def Level.rank : Level → Nat
  | .self => 0 | .provider => 1 | .government => 2

/-- One row about an identity: who vouches, and the band they state. No device appears in it. -/
structure Row where
  level : Level
  band  : Band
  deriving DecidableEq, Repr

def isWitness (r : Row) : Bool := r.level != Level.self

/-- The most protective band a list of rows states (the lowest rank), or `none` for no rows. -/
def lowest : List Row → Option Band
  | [] => none
  | r :: rs => match lowest rs with
    | none => some r.band
    | some b => some (if r.band.rank ≤ b.rank then r.band else b)

/-- The band read from the witness rows of the highest level on record, most protective on a tie. -/
def witnessBand (rows : List Row) : Option Band :=
  match lowest (rows.filter (fun r => r.level == Level.government)) with
  | some b => some b
  | none => lowest (rows.filter (fun r => r.level == Level.provider))

/-- The band a person's own declarations state, most protective first. -/
def selfBand (rows : List Row) : Option Band :=
  lowest (rows.filter (fun r => r.level == Level.self))

/-- The more protective of two bands. -/
def lower (a b : Band) : Band := if a.rank ≤ b.rank then a else b

/-- The band an identity is read at.
    A witness row sets it. A person's own declaration can lower it and never raise it.
    With no witness row the band is `under13`, whatever the person declares. -/
def resolve (rows : List Row) : Band :=
  match witnessBand rows, selfBand rows with
  | some w, some s => lower w s
  | some w, none   => w
  | none,   _      => Band.under13

/-- Fail-secure: no row on record reads as the most protective band. -/
theorem absent_is_under13 : resolve [] = Band.under13 := by rfl

/-- A person's own declaration alone never leaves the most protective band. -/
theorem self_alone_is_under13 (rows : List Row) (h : ∀ r ∈ rows, r.level = Level.self) :
    resolve rows = Band.under13 := by
  have hf : ∀ (l : Level), l ≠ Level.self → rows.filter (fun r => r.level == l) = [] := by
    intro l hl
    apply List.filter_eq_nil_iff.mpr
    intro r hr
    have := h r hr
    simp [this]
    exact fun h' => hl h'.symm
  have hg := hf Level.government (by decide)
  have hp := hf Level.provider (by decide)
  simp [resolve, witnessBand, hg, hp, lowest]

theorem lower_le_left (a b : Band) : (lower a b).rank ≤ a.rank := by
  unfold lower; split <;> omega

/-- A person's own declaration never raises the band: with it, the band read is at most the
    band the witness rows give. -/
theorem self_never_raises (rows : List Row) (w : Band) (h : witnessBand rows = some w) :
    (resolve rows).rank ≤ w.rank := by
  unfold resolve
  rw [h]
  cases selfBand rows with
  | none => exact Nat.le_refl _
  | some s => exact lower_le_left w s

/-- `adult` is read only where a witness row is on record. -/
theorem adult_needs_witness (rows : List Row) (h : resolve rows = Band.adult) :
    witnessBand rows ≠ none := by
  intro hn
  simp [resolve, hn] at h

/-- The band is a function of the rows about the identity and of nothing else: two keys of one
    self roster, holding the same rows, read the same band. A row obtained on one device, a
    phone's platform signal for one, is a row about the identity. -/
theorem device_independent (rows : List Row) (deviceA deviceB : Nat) :
    (fun (_ : Nat) => resolve rows) deviceA = (fun (_ : Nat) => resolve rows) deviceB := rfl

/-- Worked: a desktop with nothing on record; the same person after a phone joins the roster
    and its platform signal is attested at the provider rung. -/
example : resolve [] = Band.under13 := by decide
example : resolve [⟨.self, .adult⟩] = Band.under13 := by decide
example : resolve [⟨.self, .adult⟩, ⟨.provider, .adult⟩] = Band.adult := by decide
/-- A person may always declare themselves younger: the declaration lowers. -/
example : resolve [⟨.provider, .adult⟩, ⟨.self, .b13_15⟩] = Band.b13_15 := by decide
/-- A government row outranks a provider row. -/
example : resolve [⟨.provider, .adult⟩, ⟨.government, .b16_17⟩] = Band.b16_17 := by decide
