/-
  formal/roster_listing/RosterListing.lean — a member's public listing is a per-membership opt-in

  CC 2.1 (`listed`): a per-membership opt-in flag, value `public`, default absent: the roster is
  producer- and self-queryable and never globally enumerable; opting into roster visibility is a
  one-way disclosure the member chooses, admitted only on a community membership signed by its own
  subject. CC 5.4.6 / mesh_net I3: nothing about a bounded cohort is observable outside it unless
  a member discloses it. This file states the rule a non-member's roster view must obey and shows
  the two readings that break it.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.
-/

namespace RosterListing

abbrev Key := Nat

/-- one key's standing in one room: `span` counts admissions (0 = never admitted), `member` says
    whether the current span is live, `listedSpan` is the span in which the key last signed a
    listing (0 = never) -/
structure Standing where
  span : Nat
  member : Bool
  listedSpan : Nat
  deriving Repr, DecidableEq

def fresh : Standing := ⟨0, false, 0⟩

inductive Act
  | join (k : Key)                 -- proposal + acceptance landed: a new span opens
  | leave (k : Key)                -- removal or resignation: the span ends
  | list (signer : Key) (k : Key)  -- a `listed: public` row about k's membership, signed by signer
  deriving Repr, DecidableEq

abbrev World := Key → Standing

instance : Inhabited World := ⟨fun _ => fresh⟩

/-- in every reachable world a listing names a span the member has reached -/
def Tidy (w : World) (k : Key) : Prop := (w k).listedSpan ≤ (w k).span

def update (w : World) (k : Key) (s : Standing) : World := fun j => if j = k then s else w j

/-- admission: a listing lands only when the member signs it themself, about a live membership;
    everything else is refused (`none`) -/
def step (w : World) : Act → Option World
  | .join k => some (update w k ⟨(w k).span + 1, true, (w k).listedSpan⟩)
  | .leave k => if (w k).member then some (update w k ⟨(w k).span, false, (w k).listedSpan⟩) else none
  | .list signer k =>
      if signer = k ∧ (w k).member then some (update w k ⟨(w k).span, true, (w k).span⟩) else none

def run (w : World) : List Act → Option World
  | [] => some w
  | a :: as => match step w a with
    | some w' => run w' as
    | none => none

/-! ## The views a non-member may be served -/

/-- the constitution's reading: served iff the current membership carries a listing the member
    signed in this very span -/
def servedCC (w : World) (k : Key) : Bool :=
  (w k).member && (w k).listedSpan == (w k).span && (w k).span != 0

/-- twin (a): absent means listed -/
def servedAbsentListed (w : World) (k : Key) : Bool := (w k).member

/-- twin (b): the span filter dropped: a listing from any earlier span still counts -/
def servedNoSpan (w : World) (k : Key) : Bool := (w k).member && (w k).listedSpan != 0

/-- the invariant: a non-member observes k in the roster only if k's latest listing lies within
    k's current, live span -/
def Inv (served : World → Key → Bool) (w : World) (k : Key) : Prop :=
  served w k = true → (w k).member = true ∧ (w k).listedSpan = (w k).span ∧ (w k).span ≠ 0

/-! ## What holds -/

/-- the CC view satisfies the invariant in every world, reachable or not: it serves nothing the
    member has not disclosed in this span -/
theorem cc_view_discloses_only_the_listed (w : World) (k : Key) : Inv servedCC w k := by
  intro h
  unfold servedCC at h
  simp only [Bool.and_eq_true, beq_iff_eq, bne_iff_ne, ne_eq] at h
  exact ⟨h.1.1, h.1.2, h.2⟩

/-- a listing signed by anyone but the member is refused at the door -/
theorem listing_needs_the_members_signature (w : World) (s k : Key) (h : s ≠ k) :
    step w (.list s k) = none := by
  unfold step; simp [h]

/-- a listing about a membership that is not live is refused -/
theorem listing_needs_a_live_membership (w : World) (k : Key) (h : (w k).member = false) :
    step w (.list k k) = none := by
  unfold step; simp [h]

/-- removal ends the disclosure: after a leave the CC view serves nothing about k -/
theorem leave_ends_the_listing (w : World) (k : Key) (w' : World)
    (h : step w (.leave k) = some w') : servedCC w' k = false := by
  unfold step at h
  by_cases hm : (w k).member = true
  · simp [hm] at h; subst h; simp [servedCC, update]
  · simp [hm] at h

/-- a fresh admission is unlisted until the member lists again: joining opens a new span and the
    old listing names the old one -/
theorem readmission_is_unlisted (w : World) (k : Key) (w' : World) (ht : Tidy w k)
    (h : step w (.join k) = some w') : servedCC w' k = false := by
  unfold step at h; simp at h; subst h
  simp [servedCC, update]
  intro h; unfold Tidy at ht; omega

/-- every step keeps worlds tidy, so the hypothesis above is an invariant, not an assumption -/
theorem step_keeps_tidy (w : World) (a : Act) (w' : World) (k : Key) (ht : ∀ j, Tidy w j)
    (h : step w a = some w') : Tidy w' k := by
  unfold Tidy at *
  cases a with
  | join j =>
    unfold step at h; simp at h; subst h; simp [update]
    by_cases hj : k = j
    · subst hj; simp; have := ht k; omega
    · simp [hj]; exact ht k
  | leave j =>
    unfold step at h
    by_cases hm : (w j).member = true
    · simp [hm] at h; subst h; simp [update]
      by_cases hj : k = j
      · subst hj; simp; exact ht k
      · simp [hj]; exact ht k
    · simp [hm] at h
  | list s j =>
    unfold step at h
    by_cases hc : s = j ∧ (w j).member = true
    · simp [hc] at h; subst h; simp [update]
      by_cases hj : k = j
      · subst hj; simp
      · simp [hj]; exact ht k
    · simp [hc] at h

/-! ## The worked room: key 7 joins, is listed, leaves, rejoins -/

def w0 : World := fun _ => fresh
def trace : List Act := [.join 7, .list 7 7, .leave 7, .join 7]

-- the four worlds along the trace, computed
def at_ (acts : List Act) : World := match run w0 acts with | some w => w | none => w0
def w1 := at_ [.join 7]
def w2 := at_ [.join 7, .list 7 7]
def w3 := at_ [.join 7, .list 7 7, .leave 7]
def w4 := at_ trace

/-- the invariant as a Boolean, so a world can be checked by evaluation -/
def invB (served : World → Key → Bool) (w : World) (k : Key) : Bool :=
  !(served w k) || ((w k).member && (w k).listedSpan == (w k).span && (w k).span != 0)

theorem invB_iff (served : World → Key → Bool) (w : World) (k : Key) :
    invB served w k = true ↔ Inv served w k := by
  unfold invB Inv
  cases hs : served w k <;> simp [Bool.and_eq_true, beq_iff_eq, bne_iff_ne, ne_eq, and_assoc]

theorem absent_is_private : servedCC w1 7 = false := by decide
theorem listed_is_served : servedCC w2 7 = true := by decide
theorem left_is_private : servedCC w3 7 = false := by decide
theorem readmitted_is_private : servedCC w4 7 = false := by decide
theorem a_stranger_cannot_list : (run w0 [.join 7, .list 8 7]).isNone = true := by decide

/-- twin (a) fails: a member who never listed is served -/
theorem twin_absent_listed_fails : ¬ Inv servedAbsentListed w1 7 := by
  rw [← invB_iff]; decide

/-- twin (b) fails: after removal and re-admission the stale listing is served -/
theorem twin_no_span_fails : ¬ Inv servedNoSpan w4 7 := by
  rw [← invB_iff]; decide

/-- and the CC view holds on the same worlds -/
theorem cc_holds_on_the_trace : Inv servedCC w1 7 ∧ Inv servedCC w2 7 ∧ Inv servedCC w3 7 ∧ Inv servedCC w4 7 :=
  ⟨cc_view_discloses_only_the_listed _ _, cc_view_discloses_only_the_listed _ _,
   cc_view_discloses_only_the_listed _ _, cc_view_discloses_only_the_listed _ _⟩

end RosterListing
