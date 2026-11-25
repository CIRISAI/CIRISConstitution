/-
  DerivedCircle.lean — what an agent derives is shown only to those who may see every piece of it

  The rule. CC 1.13.3.4 of the CIRIS Constitution at rc22 (commit 09c8b4f), "Derived content keeps its
  circle": "What an agent derives from content may be shown only to those who may see every piece it was
  derived from. A summary of a `self` conversation is `self` content. What draws on two rooms may be shown
  only to those who are in both. A piece is shown more widely only by the act of the person whose content
  it is." Beside it, "Nothing reaches inside": "No check runs on `self` content. The known-match check runs
  only where content leaves a private circle: at a promotion into the Commons, at a post into a `public`
  room, and in a group whose moderators enabled a list (CC 4.5.7). Lawful access that an affiliation has
  declared reaches that affiliation's own scope ... Neither reaches a person's `self`."

  The model. Part 1 is generic: rows of any type with an id, an audience (who may see it), the persons
  whose content it is (`owners`) and the ids it derives from (`srcs`). A held set is the rows and the
  release rows, a release being a person and the id of the output it names. The door on an output: every
  reader of the output may see each held source, unless every person whose content that source is signed
  a release naming the output; and the output is the content of everyone whose content a source is. A
  release is per piece: it lifts that piece's audience, and no other's.

  Proved here.
    door_within_inter         (1) under the door and no release, the output's audience is within the
                              intersection of its sources' audiences
    door_two_rooms            (1) at two sources: shown only to those in both
    door_or_release           (1) as a disjunction: a reader of the output may see every source, or some
                              source it may not see had all its owners release the output
    chain_or_release          (2) by induction over derivation chains of any depth: a reader of the output
                              may see the source, or a person whose content the source is released a held
                              row on the chain
    self_stays_self           (2) at `self`: no chain moves `self` content to a reader outside that `self`
                              without a release signed by its owner
    seen_reaches_cohort       the audience rule transcribed from formal/audience_view (CC 2.1, 5.2): a row a
                              reader is served is in the audience of a held row of its cohort
    seen_derived_every_source (3) composed: a reader served a derived output, read through the audience rule,
                              is served every row it derives from at any depth, and so is in the audience
                              of a held row of each one's cohort, or a release by its owner is on the chain
    no_check_on_self          (4) no check, a read of a row at one of the three seams, reads a `self` row;
                              lawful access reaches only its affiliation, never a `self`
    no_check_on_derived_self  (4) composed: derived `self` content with no release is read by no check at a
                              place with a reader outside that `self`
    release_lifts             the release is live: the owner's release lets the output be shown more widely,
                              another person's does not
    union_plant               (5) the plant: an output shown to the UNION of its sources' audiences passes the
                              plant's door, fails `Door`, and is shown to a reader outside the `self` source
    union_breaks_chain        (5) and so (2) fails under the plant's door

  What this file does not show.
    - Who "the person whose content it is" is for a source with several owners: the text names one person.
      Here an output is the content of every owner of every source (`owners` inherited), and showing it
      beyond a source's audience needs a release by every owner of that source. For `self` content the
      owner is one.
    - The audience of a row in Part 3 is the audience rule's view (`AV.view`, transcribed): who is served
      the row in the mesh held now. A reply admitted later carries a row to a later joiner of its cohort,
      so a door kept at one mesh is to be read again at the next; `Kept` is stated over the mesh held.
    - A check reads the placed row. The text does not say whether it reads what that row names (its
      evidence); if it did, a promotion naming a `self` row would read inside the `self`.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports nothing.
-/

namespace DerivedCircle

/-! ## Part 1. The door on derived content, over any audience -/

/-- the rows: an id, an audience, the persons whose content it is, the ids it derives from -/
structure Sys (α R P : Type) where
  rid : α → Nat
  aud : α → R → Prop
  owners : α → List P
  srcs : α → List Nat

/-- what a node holds: rows, and release rows (the signer, the id of the output it names) -/
structure Held (α P : Type) where
  rows : List α
  rel : List (P × Nat)

variable {α R P : Type}

def released (H : Held α P) (p : P) (n : Nat) : Prop := (p, n) ∈ H.rel

/-- a held row `s` is a source of `o` -/
def Src (X : Sys α R P) (H : Held α P) (o s : α) : Prop := s ∈ H.rows ∧ X.rid s ∈ X.srcs o

/-- the intersection of the audiences of `o`'s held sources -/
def Inter (X : Sys α R P) (H : Held α P) (o : α) (r : R) : Prop := ∀ s, Src X H o s → X.aud s r

/-- every person whose content `s` is signed a release naming `o`, and there is such a person -/
def ReleasedBy (X : Sys α R P) (H : Held α P) (s o : α) : Prop :=
  X.owners s ≠ [] ∧ ∀ p ∈ X.owners s, released H p (X.rid o)

/-- **THE DOOR** (CC 1.13.3.4 at a74818d): a reader of the output may see every piece it was derived
    from, unless the person whose piece it is released the output; and the output stays their content -/
def Door (X : Sys α R P) (H : Held α P) (o : α) : Prop :=
  ∀ s, Src X H o s → (∀ r, X.aud o r → X.aud s r ∨ ReleasedBy X H s o) ∧
    ∀ p ∈ X.owners s, p ∈ X.owners o

/-- every held row passed the door -/
def Kept (X : Sys α R P) (H : Held α P) : Prop := ∀ o ∈ H.rows, Door X H o

/-- no person whose content a source is released `o` -/
def NoRelease (X : Sys α R P) (H : Held α P) (o : α) : Prop :=
  ∀ s, Src X H o s → ∀ p ∈ X.owners s, ¬ released H p (X.rid o)

theorem not_releasedBy {X : Sys α R P} {H : Held α P} {o s : α} (hn : NoRelease X H o)
    (hs : Src X H o s) : ¬ ReleasedBy X H s o := by
  intro ⟨hne, hall⟩
  cases h : X.owners s with
  | nil => exact hne h
  | cons p _ => exact hn s hs p (by simp [h]) (hall p (by simp [h]))

/-- **(1).** Under the door and no release, the output's audience is within the intersection of its
    sources' audiences. -/
theorem door_within_inter (X : Sys α R P) (H : Held α P) (o : α) (hd : Door X H o)
    (hn : NoRelease X H o) : ∀ r, X.aud o r → Inter X H o r := by
  intro r hr s hs
  rcases (hd s hs).1 r hr with h | h
  · exact h
  · exact absurd h (not_releasedBy hn hs)

/-- **(1), two rooms.** What draws on two rooms is shown only to those in both. -/
theorem door_two_rooms (X : Sys α R P) (H : Held α P) (o a b : α) (hd : Door X H o)
    (hn : NoRelease X H o) (ha : Src X H o a) (hb : Src X H o b) (r : R) (hr : X.aud o r) :
    X.aud a r ∧ X.aud b r :=
  ⟨door_within_inter X H o hd hn r hr a ha, door_within_inter X H o hd hn r hr b hb⟩

/-- **(1), as a disjunction.** A reader of the output may see every source, or some source it may not
    see had all its owners release the output. -/
theorem door_or_release (X : Sys α R P) (H : Held α P) (o : α) (hd : Door X H o) (r : R)
    (hr : X.aud o r) : Inter X H o r ∨ ∃ s, Src X H o s ∧ ¬ X.aud s r ∧ ReleasedBy X H s o := by
  by_cases h : Inter X H o r
  · exact Or.inl h
  · apply Or.inr
    apply Classical.byContradiction
    intro hno
    apply h
    intro s hs
    apply Classical.byContradiction
    intro hns
    rcases (hd s hs).1 r hr with h1 | h1
    · exact hns h1
    · exact hno ⟨s, hs, hns, h1⟩

/-! ### (2) Chains of derivation, any depth -/

/-- `o` derives from `s`: directly, or from a held output that derives from `s` -/
inductive Derives (X : Sys α R P) (H : Held α P) : α → α → Prop
  | direct {o s} : Src X H o s → Derives X H o s
  | step {o m s} : Src X H o m → Derives X H m s → Derives X H o s

/-- the persons whose content a source is stay persons whose content the output is, along any chain -/
theorem owners_carry (X : Sys α R P) (H : Held α P) (hk : Kept X H) {o s : α}
    (hos : Derives X H o s) (ho : o ∈ H.rows) {p : P} (hp : p ∈ X.owners s) : p ∈ X.owners o := by
  induction hos with
  | direct h => exact (hk _ ho _ h).2 p hp
  | step h _ ih => exact (hk _ ho _ h).2 p (ih h.1 hp)

/-- **(2).** By induction over the chain: a reader of the output may see the source, or a person whose
    content the source is signed a release naming a held row `m` on the chain (`m` derives from the
    source, and is the output or one the output derives from). -/
theorem chain_or_release (X : Sys α R P) (H : Held α P) (hk : Kept X H)
    {o s : α} (hos : Derives X H o s) (ho : o ∈ H.rows) {p : P} (hp : p ∈ X.owners s)
    {r : R} (hr : X.aud o r) :
    X.aud s r ∨
      ∃ m, m ∈ H.rows ∧ released H p (X.rid m) ∧ Derives X H m s ∧ (m = o ∨ Derives X H o m) := by
  induction hos with
  | @direct o s h =>
    rcases (hk o ho s h).1 r hr with h1 | ⟨_, hall⟩
    · exact Or.inl h1
    · exact Or.inr ⟨o, ho, hall p hp, Derives.direct h, Or.inl rfl⟩
  | @step o m s h hms ih =>
    have hpm : p ∈ X.owners m := owners_carry X H hk hms h.1 hp
    rcases (hk o ho m h).1 r hr with h1 | ⟨_, hall⟩
    · rcases ih h.1 hp h1 with h2 | ⟨m', hm', hrel, hd, hor⟩
      · exact Or.inl h2
      · refine Or.inr ⟨m', hm', hrel, hd, Or.inr ?_⟩
        rcases hor with rfl | hor
        · exact Derives.direct h
        · exact Derives.step h hor
    · exact Or.inr ⟨o, ho, hall p hpm, Derives.step h hms, Or.inl rfl⟩

/-! ## Part 2. Places and `self` -/

abbrev Key := Nat
abbrev Person := Nat

/-- a placement (CC 5.2's table): a person's `self`, a family, a community, an affiliation, a public room,
    the Commons -/
inductive Place
  | self (p : Person)
  | family (f : Nat)
  | community (c : Nat)
  | affiliation (a : Nat)
  | publicRoom (c : Nat)
  | commons
deriving DecidableEq

/-- the nodes each placement reaches (CC 5.2): any assignment; the rule is stated for every one -/
structure PW where
  aud : Place → Key → Bool

/-- a row with a placement -/
structure PRow where
  id : Nat
  place : Place
  owners : List Person
  srcs : List Nat
deriving DecidableEq

def PX (W : PW) : Sys PRow Key Person :=
  ⟨PRow.id, fun x k => W.aud x.place k = true, PRow.owners, PRow.srcs⟩

/-- **(2) at `self`.** No chain of derivations, of any depth, moves `p`'s `self` content to a reader
    outside that `self` without a release signed by `p` naming a held row on the chain. -/
theorem self_stays_self (W : PW) (H : Held PRow Person) (hk : Kept (PX W) H)
    {o s : PRow} (hos : Derives (PX W) H o s) (ho : o ∈ H.rows) {p : Person} (hself : s.place = .self p)
    (hp : p ∈ s.owners) {r : Key} (hr : W.aud o.place r = true) (hout : W.aud (.self p) r = false) :
    ∃ m, m ∈ H.rows ∧ released H p m.id ∧ Derives (PX W) H m s ∧ (m = o ∨ Derives (PX W) H o m) := by
  rcases chain_or_release (PX W) H hk hos ho hp hr with h | h
  · exact absurd h (by show ¬ W.aud s.place r = true; rw [hself, hout]; simp)
  · exact h

/-! ## Part 3. Composition with the audience rule of formal/audience_view

The definitions below are transcribed from `formal/audience_view/AudienceView.lean` Part 2 of the
Constitution at a74818d (unchanged since 0fad9be), with the same names and bodies: a row's audience is
everyone at federation scope (cohort 0), else the members of its cohort at the roster head it names, plus
its delivered key (CC 2.1); a row carries its audience to a row it names when concluded, in the same
cohort, and its signer is in the named row's audience (CC 5.2 "What a row carries"); the reader's view
walks the mesh newest first. -/

namespace AV

structure Cohort where
  members : Nat → List Key

structure World where
  everyone : List Key
  cohorts : List Cohort

def membersAt (w : World) (c : Nat) (t : Nat) : List Key :=
  match w.cohorts.get? (c - 1) with
  | some co => co.members t
  | none => []

structure Row where
  id : Nat
  producer : Key
  cohort : Nat
  head : Nat
  subjects : List Key
  deliveredTo : List Key
  names : List Nat
  concluded : Bool
  body : Nat
  deriving DecidableEq, Repr

def audience (w : World) (x : Row) : List Key :=
  (if x.cohort = 0 then w.everyone else membersAt w x.cohort x.head) ++ x.deliveredTo

def reaches (w : World) (x : Row) (k : Key) : Bool := decide (k ∈ audience w x)

def carries (w : World) (y x : Row) : Bool :=
  decide (x.id ∈ y.names) && decide (y.cohort = x.cohort) && y.concluded && reaches w x y.producer

def reachesAfter (w : World) : List Row → Row → Key → Bool
  | [], x, k => reaches w x k
  | y :: rest, x, k => reachesAfter w rest x k || (carries w y x && reachesAfter w rest y k)

abbrev Mesh := List Row

def viewFrom (w : World) (k : Key) : List Row → Mesh → List Row
  | _, [] => []
  | nw, x :: older => (if reachesAfter w nw x k then [x] else []) ++ viewFrom w k (x :: nw) older

def view (w : World) (k : Key) (m : Mesh) : List Row := viewFrom w k [] m

end AV

open AV in
/-- a row reached after the newer rows is in the audience of itself or a newer row of its cohort -/
theorem reachesAfter_cohort (w : World) : ∀ (nw : List Row) (x : Row) (k : Key),
    reachesAfter w nw x k = true → ∃ y, (y = x ∨ y ∈ nw) ∧ y.cohort = x.cohort ∧ reaches w y k = true := by
  intro nw
  induction nw with
  | nil => intro x k h; exact ⟨x, Or.inl rfl, rfl, h⟩
  | cons y rest ih =>
    intro x k h
    simp only [reachesAfter, Bool.or_eq_true, Bool.and_eq_true] at h
    rcases h with h | ⟨hc, h⟩
    · obtain ⟨z, hz, hzc, hzr⟩ := ih x k h
      exact ⟨z, by rcases hz with hz | hz <;> simp [hz], hzc, hzr⟩
    · obtain ⟨z, hz, hzc, hzr⟩ := ih y k h
      have hyx : y.cohort = x.cohort := by
        simp only [carries, Bool.and_eq_true, decide_eq_true_eq] at hc; exact hc.1.1.2
      exact ⟨z, by rcases hz with hz | hz <;> simp [hz], hzc.trans hyx, hzr⟩

open AV in
theorem viewFrom_mem (w : World) (k : Key) : ∀ (m : Mesh) (nw : List Row) (x : Row),
    x ∈ viewFrom w k nw m → x ∈ m ∧ ∃ nw', (∀ z ∈ nw', z ∈ nw ∨ z ∈ m) ∧ reachesAfter w nw' x k = true := by
  intro m
  induction m with
  | nil => intro nw x h; simp [viewFrom] at h
  | cons y older ih =>
    intro nw x h
    simp only [viewFrom, List.mem_append] at h
    rcases h with h | h
    · split at h
      · next hr =>
        simp at h; subst h
        exact ⟨by simp, nw, fun z hz => Or.inl hz, hr⟩
      · simp at h
    · obtain ⟨hxo, nw', hsub, hr⟩ := ih (y :: nw) x h
      refine ⟨by simp [hxo], nw', fun z hz => ?_, hr⟩
      rcases hsub z hz with hz | hz
      · simp at hz; rcases hz with rfl | hz
        · exact Or.inr (by simp)
        · exact Or.inl hz
      · exact Or.inr (by simp [hz])

open AV in
/-- **The audience rule (formal/audience_view).** A row a reader is served is held, and is in the
    audience of a held row of its own cohort: itself, or a newer row that carries it. -/
theorem seen_reaches_cohort (w : World) (k : Key) (m : Mesh) (x : Row) (h : x ∈ view w k m) :
    x ∈ m ∧ ∃ y, y ∈ m ∧ y.cohort = x.cohort ∧ reaches w y k = true := by
  obtain ⟨hx, nw', hsub, hr⟩ := viewFrom_mem w k m [] x h
  obtain ⟨y, hy, hyc, hyr⟩ := reachesAfter_cohort w nw' x k hr
  refine ⟨hx, y, ?_, hyc, hyr⟩
  rcases hy with rfl | hy
  · exact hx
  · rcases hsub y hy with h | h
    · simp at h
    · exact h

/-- a row of the mesh, with whose content it is and what it derives from -/
structure DRow where
  row : AV.Row
  owners : List Person
  srcs : List Nat

/-- the audience of a row is who the audience rule serves it to, in the mesh held -/
def DX (w : AV.World) (H : Held DRow Person) : Sys DRow Key Person :=
  ⟨fun d => d.row.id, fun d k => d.row ∈ AV.view w k (H.rows.map DRow.row), DRow.owners, DRow.srcs⟩

/-- **(3), composed.** A reader served a derived output is served every row it derives from, at any
    depth, and so is in the audience of a held row of that row's cohort, unless a person whose content
    that row is released a held row on the chain. -/
theorem seen_derived_every_source (w : AV.World) (k : Key) (H : Held DRow Person)
    (hk : Kept (DX w H) H) {o : DRow} (ho : o ∈ H.rows)
    (hseen : o.row ∈ AV.view w k (H.rows.map DRow.row)) :
    ∀ s, Derives (DX w H) H o s → ∀ p ∈ s.owners,
      (s.row ∈ AV.view w k (H.rows.map DRow.row) ∧
        ∃ y, y ∈ H.rows.map DRow.row ∧ y.cohort = s.row.cohort ∧ AV.reaches w y k = true) ∨
        ∃ m, m ∈ H.rows ∧ released H p m.row.id ∧ Derives (DX w H) H m s ∧
          (m = o ∨ Derives (DX w H) H o m) := by
  intro s hos p hp
  rcases chain_or_release (DX w H) H hk hos ho hp hseen with h | h
  · exact Or.inl ⟨h, (seen_reaches_cohort w k _ s.row h).2⟩
  · exact Or.inr h

/-! ## Part 4. The checks clause -/

/-- the three seams where the known-match check runs (CC 1.13.3.4, CC 4.5.7) -/
inductive Seam
  | promote               -- a promotion into the Commons
  | post                  -- a post into a `public` room
  | groupList (c : Nat)   -- in a group whose moderators enabled a list

/-- a row is at the seam: placed in the Commons, in a public room, or in group `c` with its list enabled -/
def atSeam (listEnabled : Nat → Bool) : Seam → Place → Bool
  | .promote, .commons => true
  | .post, .publicRoom _ => true
  | .groupList c, .community d => decide (c = d) && listEnabled c
  | _, _ => false

/-- **A CHECK** reads one row, at one of the three seams, where that row is placed -/
structure Check (listEnabled : Nat → Bool) where
  seam : Seam
  row : PRow
  at_seam : atSeam listEnabled seam row.place = true

/-- lawful access an affiliation declared reaches that affiliation's own scope (CC 4.4) -/
def lawfulReaches (a : Nat) (pl : Place) : Bool := decide (pl = .affiliation a)

/-- **(4).** No check reads a `self` row; lawful access never reaches a `self`. -/
theorem no_check_on_self (en : Nat → Bool) (c : Check en) (p : Person) (a : Nat) :
    c.row.place ≠ .self p ∧ lawfulReaches a (.self p) = false := by
  refine ⟨fun h => ?_, by simp [lawfulReaches]⟩
  have := c.at_seam
  rw [h] at this
  cases hs : c.seam <;> rw [hs] at this <;> simp [atSeam] at this

/-- **(4), composed.** Content derived, at any depth, from `p`'s `self` with no release by `p` on the
    chain is read by no check whose place has a reader outside `p`'s `self`. -/
theorem no_check_on_derived_self (W : PW) (en : Nat → Bool) (H : Held PRow Person) (hk : Kept (PX W) H)
    {s : PRow} {p : Person} (hself : s.place = .self p) (hp : p ∈ s.owners)
    (hnr : ∀ m, m ∈ H.rows → Derives (PX W) H m s → ¬ released H p m.id)
    (c : Check en) (ho : c.row ∈ H.rows) (hos : Derives (PX W) H c.row s)
    (r : Key) (hr : W.aud c.row.place r = true) (hout : W.aud (.self p) r = false) : False := by
  obtain ⟨m, hm, hrel, hms, _⟩ := self_stays_self W H hk hos ho hself hp hr hout
  exact hnr m hm hms hrel

/-! ## Part 5. The release, and the plant: the union of audiences -/

/-- person 1's `self` reaches key 1; the Commons reaches keys 1 and 2 -/
def W0 : PW := ⟨fun pl k => match pl with
  | .self 1 => k == 1
  | .commons => k == 1 || k == 2
  | _ => false⟩

def sSelf : PRow := ⟨1, .self 1, [1], []⟩
def sPub : PRow := ⟨2, .commons, [2], []⟩

/-- a summary of person 1's `self` note placed in the Commons -/
def oRel : PRow := ⟨3, .commons, [1], [1]⟩
def H1 : Held PRow Person := ⟨[sSelf, oRel], [(1, 3)]⟩

/-- **The release is live.** The summary in the Commons passes `Door` when person 1 signed a release
    naming it, and fails it when only person 2 did. -/
theorem release_lifts :
    Door (PX W0) H1 oRel ∧ ¬ Door (PX W0) ⟨H1.rows, [(2, 3)]⟩ oRel := by
  constructor
  · intro s hs
    obtain ⟨hsm, hid⟩ := hs
    simp only [H1, List.mem_cons, List.mem_singleton, List.not_mem_nil, or_false] at hsm
    rcases hsm with rfl | rfl
    · refine ⟨fun r _ => Or.inr ⟨by simp [PX, sSelf], fun p hp => ?_⟩,
        fun p hp => by simpa [PX, sSelf, oRel] using hp⟩
      simp [PX, sSelf] at hp; subst hp; simp [released, H1, PX, oRel]
    · simp [PX, oRel] at hid
  · intro hd
    have hs : Src (PX W0) ⟨H1.rows, [(2, 3)]⟩ oRel sSelf := by simp [Src, H1, PX, oRel, sSelf]
    rcases (hd sSelf hs).1 2 (by simp [PX, W0, oRel]) with h | ⟨_, hall⟩
    · simp [PX, W0, sSelf] at h
    · exact absurd (hall 1 (by simp [PX, sSelf])) (by simp [released, PX, oRel])

/-- the plant's door: an output, a row with a held source, may be shown to anyone who may see SOME
    piece (the union of its sources' audiences) -/
def UnionDoor (X : Sys α R P) (H : Held α P) (o : α) : Prop :=
  (∃ s, Src X H o s) → ∀ r, X.aud o r → ∃ s, Src X H o s ∧ X.aud s r

/-- an output drawing on the `self` note and a Commons row, placed in the Commons, no release held -/
def oWide : PRow := ⟨3, .commons, [1, 2], [1, 2]⟩
def H0 : Held PRow Person := ⟨[sSelf, sPub, oWide], []⟩

/-- the plant keeps every held row of `H0` -/
theorem union_kept : ∀ o ∈ H0.rows, UnionDoor (PX W0) H0 o := by
  intro o ho hsrc r hr
  simp only [H0, List.mem_cons, List.mem_singleton, List.not_mem_nil, or_false] at ho
  rcases ho with rfl | rfl | rfl
  · obtain ⟨_, _, h⟩ := hsrc; simp [PX, sSelf] at h
  · obtain ⟨_, _, h⟩ := hsrc; simp [PX, sPub] at h
  · exact ⟨sPub, by simp [Src, H0, PX, sPub, oWide], by simp [PX, W0, sPub, oWide] at hr ⊢; exact hr⟩

/-- **(5), the plant violates (1).** Shown to the union of its sources' audiences, the output passes the
    plant's door and fails `Door`: no release is held, and key 2 is shown it and is outside person 1's
    `self`, so outside the intersection. -/
theorem union_plant :
    UnionDoor (PX W0) H0 oWide ∧ ¬ Door (PX W0) H0 oWide ∧ H0.rel = [] ∧
      (PX W0).aud oWide 2 ∧ ¬ Inter (PX W0) H0 oWide 2 := by
  have hs : Src (PX W0) H0 oWide sSelf := by simp [Src, H0, PX, oWide, sSelf]
  refine ⟨union_kept oWide (by simp [H0]), ?_, rfl, by simp [PX, W0, oWide], ?_⟩
  · intro hd
    rcases (hd sSelf hs).1 2 (by simp [PX, W0, oWide]) with h | ⟨_, hall⟩
    · simp [PX, W0, sSelf] at h
    · exact absurd (hall 1 (by simp [PX, sSelf])) (by simp [released, H0])
  · intro hi
    have := hi sSelf hs
    simp [PX, W0, sSelf] at this

/-- **(5), the plant violates (2).** Every held row passes the plant's door, yet a chain moves person 1's
    `self` content to key 2, outside that `self`, with no release by person 1. -/
theorem union_breaks_chain :
    (∀ o ∈ H0.rows, UnionDoor (PX W0) H0 o) ∧ Derives (PX W0) H0 oWide sSelf ∧
      sSelf.place = .self 1 ∧ 1 ∈ sSelf.owners ∧ W0.aud oWide.place 2 = true ∧
      W0.aud (.self 1) 2 = false ∧ ∀ n, ¬ released H0 1 n :=
  ⟨union_kept, Derives.direct (by simp [Src, H0, PX, oWide, sSelf]), rfl, by simp [sSelf], rfl, rfl,
    fun n => by simp [released, H0]⟩

end DerivedCircle

#print axioms DerivedCircle.door_within_inter
#print axioms DerivedCircle.door_two_rooms
#print axioms DerivedCircle.door_or_release
#print axioms DerivedCircle.chain_or_release
#print axioms DerivedCircle.self_stays_self
#print axioms DerivedCircle.seen_reaches_cohort
#print axioms DerivedCircle.seen_derived_every_source
#print axioms DerivedCircle.no_check_on_self
#print axioms DerivedCircle.no_check_on_derived_self
#print axioms DerivedCircle.release_lifts
#print axioms DerivedCircle.union_plant
#print axioms DerivedCircle.union_breaks_chain
