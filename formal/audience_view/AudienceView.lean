/-
  formal/audience_view/AudienceView.lean — the view theory, tied to the mesh's audience rules

  A reader of the mesh holds a lossy view of it. The general theory of such views is stated once,
  in Part 1 of this file, with the definitions and theorem names of the view theory it restates
  (CORRESPONDENCE.md maps each to its source and records the mechanical check that they agree):

    * `Factors u v`        — u = h ∘ v for some h: everything u knows, v determines;
    * `SeparatesFiber v d` — two states with one view differ in d (the witness pair);
    * `factors_iff_not_separatesFiber` — a quantity factors through a view exactly when no
      witness pair separates a fibre;
    * `Closed v T`         — v ∘ T factors through v: the view keeps its own law of motion;
    * `Held v T`           — v ∘ T = v: the step leaves the view as it was.

  Parts 2 to 4 instantiate the view with three audience rules of the text, each with what the
  reader must be able to decide (it factors), what the reader must not learn (it does not factor,
  with the witness pair), and how the reader's view moves under the mesh's step.

    2. The row's audience (CC 2.1, 5.2): a reader's view is the rows whose audience includes it,
       with a reply carrying the row it answers (CC 5.2 "What a row carries").
    3. The private room (CC 3.1.3.2): a room seats room keys; the binding of a room key to a
       person is never a row. Three readers: a member's node holding the bindings, a holder of
       the rows without bindings, and an outsider.
    4. The public roster and the served set (CC 3.2 public rooms, CC 5.2's table, CC 5.4.6's
       served set to a stranger).

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.
-/

namespace AudienceView

universe uX uC uD

/-! ## Part 1. The view theory, restated -/

/-- **THE RELATION.** `u` factors through `v`: everything `u` knows, `v` determines. -/
def Factors {X : Type uX} {C : Type uC} {D : Type uD} (u : X → C) (v : X → D) : Prop :=
  ∃ h : D → C, u = h ∘ v

/-- A datum separates a fibre of a summary when two states share the summary yet differ in the
    datum: the witness pair. -/
def SeparatesFiber {State : Type uX} {Summary : Type uC} {Datum : Type uD}
    (summary : State → Summary) (d : State → Datum) : Prop :=
  ∃ a b : State, summary a = summary b ∧ d a ≠ d b

/-- The domain argument: a datum that separates a fibre is not computable from the summary. -/
theorem not_computable_from {State : Type uX} {Summary : Type uC} {Datum : Type uD}
    (summary : State → Summary) (d : State → Datum)
    (h : SeparatesFiber summary d) :
    ¬ ∃ g : Summary → Datum, ∀ x, d x = g (summary x) := by
  intro ⟨g, hg⟩
  obtain ⟨a, b, hs, hd⟩ := h
  exact hd (by rw [hg a, hg b, hs])

/-- **THE CENTRAL LEMMA.** A quantity factors through a view iff no witness pair separates a
    fibre. -/
theorem factors_iff_not_separatesFiber {X : Type uX} {S : Type uC} {D : Type uD} [Nonempty D]
    (d : X → D) (summary : X → S) :
    Factors d summary ↔ ¬ SeparatesFiber summary d := by
  constructor
  · intro ⟨h, hh⟩ ⟨a, b, hs, hd⟩
    subst hh
    exact hd (congrArg h hs)
  · intro hns
    have hconst : ∀ a b, summary a = summary b → d a = d b := fun a b hab =>
      Classical.byContradiction fun hne => hns ⟨a, b, hab, hne⟩
    classical
    refine ⟨fun s => if hx : ∃ x, summary x = s then d (Classical.choose hx)
                     else Classical.choice inferInstance, ?_⟩
    funext x
    have hx : ∃ y, summary y = summary x := ⟨x, rfl⟩
    show d x = (if hx : ∃ y, summary y = summary x then d (Classical.choose hx)
               else Classical.choice inferInstance)
    rw [dif_pos hx]
    exact (hconst _ _ (Classical.choose_spec hx)).symm

/-- The witness pair refutes factoring, with no assumption on the codomain. -/
theorem not_factors_of_separatesFiber {X : Type uX} {S : Type uC} {D : Type uD}
    {d : X → D} {summary : X → S} (h : SeparatesFiber summary d) : ¬ Factors d summary := by
  intro ⟨g, hg⟩
  obtain ⟨a, b, hs, hd⟩ := h
  exact hd (by rw [hg]; exact congrArg g hs)

/-- Factoring is closed under post-composition: what a view decides, any function of it decides. -/
theorem factors_comp {X : Type uX} {C : Type uC} {D : Type uD} {E : Type uX}
    {u : X → C} {v : X → D} (f : C → E) (h : Factors u v) : Factors (f ∘ u) v := by
  obtain ⟨g, hg⟩ := h
  exact ⟨f ∘ g, by rw [hg]; rfl⟩

/-- **THE VIEW DETERMINES ITS OWN SUCCESSOR.** -/
def Closed {X : Type uX} {C : Type uC} (v : X → C) (T : X → X) : Prop := Factors (v ∘ T) v

/-- **THE READING SURVIVES THE STEP.** -/
def Held {X : Type uX} {C : Type uC} (v : X → C) (T : X → X) : Prop := v ∘ T = v

theorem held_imp_closed {X : Type uX} {C : Type uC} {v : X → C} {T : X → X} (h : Held v T) :
    Closed v T := ⟨id, by rw [h]; rfl⟩

/-- The forward half of fibre invariance, needing nothing of the codomain. -/
theorem Closed.never_splits {X : Type uX} {C : Type uC} {v : X → C} {T : X → X}
    (h : Closed v T) : ∀ x y, v x = v y → v (T x) = v (T y) := by
  obtain ⟨φ, hφ⟩ := h
  intro x y hxy
  have hx := congrFun hφ x
  have hy := congrFun hφ y
  simp only [Function.comp] at hx hy
  rw [hx, hy, hxy]

/-- **CLOSURE IS FIBRE-INVARIANCE.** -/
theorem closed_iff_fiber_invariant {X : Type uX} {C : Type uC} [Nonempty C]
    {v : X → C} {T : X → X} :
    Closed v T ↔ ∀ x y, v x = v y → v (T x) = v (T y) := by
  constructor
  · exact Closed.never_splits
  · intro h
    classical
    refine ⟨fun c => if hc : ∃ z, v z = c then v (T (Classical.choose hc))
                     else Classical.choice inferInstance, ?_⟩
    funext x
    have hex : ∃ z, v z = v x := ⟨x, rfl⟩
    show v (T x) = (if hc : ∃ z, v z = v x then v (T (Classical.choose hc))
                    else Classical.choice inferInstance)
    rw [dif_pos hex]
    exact (h _ x (Classical.choose_spec hex)).symm

/-- The square's other spelling: some coarse update completes it. -/
def ViewClosed {S V : Type} (v : S → V) (T : S → S) : Prop :=
  ∃ h : V → V, ∀ x, v (T x) = h (v x)

/-- The two spellings of closure are one condition. -/
theorem closed_iff_viewClosed {S V : Type} (v : S → V) (T : S → S) :
    Closed v T ↔ ViewClosed v T := by
  constructor
  · intro ⟨h, hh⟩
    exact ⟨h, fun x => congrFun hh x⟩
  · intro ⟨h, hh⟩
    exact ⟨h, funext hh⟩

/-- A bounded check of fibre invariance over an explicit finite list of states. -/
def closedOn {X C : Type} [DecidableEq C] (states : List X) (v : X → C) (T : X → X) : Bool :=
  states.all fun a => states.all fun b => !(decide (v a = v b)) || decide (v (T a) = v (T b))

/-- A passing bounded check is closure on the finite state space it enumerates. -/
theorem closed_of_closedOn {X C : Type} [DecidableEq C] [Nonempty C]
    (states : List X) (v : X → C) (T : X → X) (hT : ∀ x ∈ states, T x ∈ states)
    (h : closedOn states v T = true) :
    Closed (fun s : {x // x ∈ states} => v s.val)
      (fun s => ⟨T s.val, hT s.val s.property⟩) := by
  apply closed_iff_fiber_invariant.mpr
  intro ⟨a, ha⟩ ⟨b, hb⟩ hab
  unfold closedOn at h
  have h1 := List.all_eq_true.mp h a ha
  have h2 := List.all_eq_true.mp h1 b hb
  simp only at hab ⊢
  simp only [Bool.or_eq_true, Bool.not_eq_true', decide_eq_false_iff_not,
    decide_eq_true_eq] at h2
  cases h2 with
  | inl hn => exact absurd hab hn
  | inr hy => exact hy

/-! ## Part 2. The row's audience (CC 2.1, CC 5.2)

A mesh state is the list of rows held, newest first. A row has an audience: everyone at
federation scope, otherwise the members of its cohort at the roster head it names, plus the key
its family delivers it to (CC 2.1). A row carries its audience to a row it names when it is
concluded, sits in the same room and its signer is already in the named row's audience (CC 5.2);
since a row naming another comes after it, a row's effective audience is read from the rows newer
than it. The reader's view is the rows whose effective audience includes it: "A row is served to
a node in its audience and to no other" (CC 5.2). -/

abbrev Key := Nat
abbrev RowId := Nat

/-- a cohort is its roster fold: who is a member at a roster head -/
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
  id : RowId
  producer : Key
  cohort : Nat               -- 0 = federation (everyone); n ≥ 1 indexes a bounded cohort
  head : Nat                 -- the roster head the row names
  subjects : List Key        -- subject_key_ids
  deliveredTo : List Key     -- the key the family delivers the row to
  names : List RowId         -- the rows this row names
  concluded : Bool
  body : Nat
  deriving DecidableEq, Repr

/-- the row's own audience (CC 2.1): everyone at federation scope; else the members at the head
    the row names, plus the delivered key -/
def audience (w : World) (x : Row) : List Key :=
  (if x.cohort = 0 then w.everyone else membersAt w x.cohort x.head) ++ x.deliveredTo

def reaches (w : World) (x : Row) (k : Key) : Bool := decide (k ∈ audience w x)

/-- the audience rule for subjects (CC 2.1): every subject is within the row's audience -/
def admitAudience (w : World) (x : Row) : Bool := x.subjects.all (fun s => reaches w x s)

/-- `y` carries its audience to `x` (CC 5.2 "What a row carries") -/
def carries (w : World) (y x : Row) : Bool :=
  decide (x.id ∈ y.names) && decide (y.cohort = x.cohort) && y.concluded && reaches w x y.producer

/-- whether `x` reaches `k`, given the rows newer than `x`, nearest first: its own audience, or
    the audience of a newer row that carries it -/
def reachesAfter (w : World) : List Row → Row → Key → Bool
  | [], x, k => reaches w x k
  | y :: rest, x, k => reachesAfter w rest x k || (carries w y x && reachesAfter w rest y k)

abbrev Mesh := List Row

/-- the rows a reader is served, walking the mesh from newest to oldest -/
def viewFrom (w : World) (k : Key) : List Row → Mesh → List Row
  | _, [] => []
  | nw, x :: older => (if reachesAfter w nw x k then [x] else []) ++ viewFrom w k (x :: nw) older

/-- **THE READER'S VIEW** under the audience rule -/
def view (w : World) (k : Key) (m : Mesh) : List Row := viewFrom w k [] m

/-- the mesh's step: a row is admitted -/
def admit (x : Row) (m : Mesh) : Mesh := x :: m

theorem reachesAfter_of_reaches (w : World) (x : Row) (k : Key) (h : reaches w x k = true) :
    ∀ nw, reachesAfter w nw x k = true := by
  intro nw
  induction nw generalizing x with
  | nil => simpa [reachesAfter] using h
  | cons y rest ih => simp [reachesAfter, ih x h]

/-- a row that names nothing carries nothing, wherever it sits among the newer rows -/
theorem reachesAfter_append_nameless (w : World) (x : Row) (hx : x.names = []) (k : Key) :
    ∀ nw z, reachesAfter w (nw ++ [x]) z k = reachesAfter w nw z k := by
  intro nw
  induction nw with
  | nil => intro z; simp [reachesAfter, carries, hx]
  | cons y rest ih => intro z; simp [reachesAfter, ih]

theorem viewFrom_append_nameless (w : World) (x : Row) (hx : x.names = []) (k : Key) :
    ∀ m nw, viewFrom w k (nw ++ [x]) m = viewFrom w k nw m := by
  intro m
  induction m with
  | nil => intro nw; rfl
  | cons y older ih =>
    intro nw
    simp only [viewFrom, reachesAfter_append_nameless w x hx k]
    rw [← List.cons_append, ih]

/-- admitting a row that names nothing moves the view by that row alone, and only if it reaches -/
theorem view_admit (w : World) (k : Key) (x : Row) (hx : x.names = []) (m : Mesh) :
    view w k (admit x m) = (if reaches w x k then [x] else []) ++ view w k m := by
  unfold view admit
  simp only [viewFrom, reachesAfter]
  rw [show [x] = ([] : List Row) ++ [x] from rfl, viewFrom_append_nameless w x hx k]

/-- **(c) HELD.** Admitting a row outside the reader's audience leaves the reader's view as it
    was (CC 5.2: a node outside the audience learns nothing, not even that the row exists). -/
theorem admit_outside_is_held (w : World) (k : Key) (x : Row) (hx : x.names = [])
    (hout : reaches w x k = false) : Held (view w k) (admit x) := by
  funext m
  simp [Function.comp, view_admit w k x hx, hout]

/-- **(c) CLOSED.** Admitting a row inside the reader's audience moves the view by a function of
    the view and the row alone. -/
theorem admit_inside_is_closed (w : World) (k : Key) (x : Row) (hx : x.names = [])
    (hin : reaches w x k = true) : view w k ∘ admit x = (fun v => x :: v) ∘ view w k := by
  funext m
  simp [Function.comp, view_admit w k x hx, hin]

/-- **(c) CLOSED, for every row that names nothing.** -/
theorem admit_is_closed (w : World) (k : Key) (x : Row) (hx : x.names = []) :
    Closed (view w k) (admit x) := by
  cases h : reaches w x k
  · exact held_imp_closed (admit_outside_is_held w k x hx h)
  · exact ⟨fun v => x :: v, admit_inside_is_closed w k x hx h⟩

/-- **(b) HIDES.** A row outside the reader's audience does not factor through the reader's
    view: not its content, not even that it is held. The witness pair is the mesh without it and
    the mesh with it alone. -/
theorem outside_row_hidden (w : World) (k : Key) (x : Row) (hout : reaches w x k = false) :
    ¬ Factors (fun m : Mesh => decide (x ∈ m)) (view w k) := by
  apply not_factors_of_separatesFiber
  refine ⟨[], [x], ?_, ?_⟩
  · simp [view, viewFrom, reachesAfter, hout]
  · simp

/-- the rows a reader is party to: admitted under the audience rule and naming it (CC 3.4.5) -/
def partyTo (w : World) (k : Key) (m : Mesh) : List Row :=
  m.filter (fun x => decide (k ∈ x.subjects) && admitAudience w x)

/-- under the audience rule a subject is in the row's audience (Standing.lean `standing_reaches`) -/
theorem subject_reaches (w : World) (x : Row) (k : Key)
    (h : (decide (k ∈ x.subjects) && admitAudience w x) = true) : reaches w x k = true := by
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact List.all_eq_true.mp h.2 k h.1

theorem viewFrom_filter (w : World) (k : Key) (q : Row → Bool)
    (hq : ∀ x, q x = true → reaches w x k = true) :
    ∀ m nw, (viewFrom w k nw m).filter q = m.filter q := by
  intro m
  induction m with
  | nil => intro nw; rfl
  | cons y older ih =>
    intro nw
    simp only [viewFrom, List.filter_append, ih]
    cases hy : q y
    · cases reachesAfter w nw y k <;> simp [List.filter_cons, hy]
    · simp [List.filter_cons, hy, reachesAfter_of_reaches w y k (hq y hy) nw]

/-- **(a) DECIDES.** The rows a reader is party to factor through the reader's view: under the
    audience rule a subject can see every row it may withdraw or contest (CC 2.1, 3.4.5, 5.2
    "A row about a party reaches that party"). -/
theorem party_rows_decided (w : World) (k : Key) :
    Factors (partyTo w k) (view w k) := by
  refine ⟨fun v => v.filter (fun x => decide (k ∈ x.subjects) && admitAudience w x), ?_⟩
  funext m
  simp only [Function.comp, partyTo, view]
  exact (viewFrom_filter w k _ (subject_reaches w · k) m []).symm

/-- **(a) DECIDES, any decision.** Whatever a reader decides from the rows it is party to (that a
    row binds it, that it may withdraw or contest it) it decides from its own view. -/
theorem party_decisions_decided {E : Type} (w : World) (k : Key) (f : List Row → E) :
    Factors (f ∘ partyTo w k) (view w k) :=
  factors_comp f (party_rows_decided w k)

/-! ### The carriage of a reply to a later joiner

A room of three; key 9 joins at roster head 5. `old` was written at head 4; `reply` names it at
head 6, signed by member 2, concluded. -/

def roomC : Cohort := ⟨fun t => if t < 5 then [1, 2, 3] else [1, 2, 3, 9]⟩
def w0 : World := ⟨[1, 2, 3, 4, 5, 6, 7, 8, 9], [roomC]⟩
def old : Row := ⟨1, 1, 1, 4, [], [], [], true, 0⟩
def reply : Row := ⟨2, 2, 1, 6, [], [], [1], true, 0⟩

/-- the reply carries the row it answers to the later joiner (CC 5.2) -/
theorem reply_carries_to_joiner : view w0 9 [reply, old] = [reply, old] := by decide

/-- **(c) FINDING: NOT CLOSED WITHOUT THE WAIT.** Over every mesh state, the joiner's view is not
    closed under admitting the reply: two meshes the joiner cannot tell apart (without `old`,
    with `old`) are sent to different views. The joiner's next view depends on a row outside
    its view. -/
theorem carriage_not_closed : ¬ Closed (view w0 9) (admit reply) := by
  intro h
  have := h.never_splits [] [old] (by decide)
  exact absurd this (by decide)

/-! The kernel keeps a row only after the rows it names (a row waits for what it names). On the
states that rule allows, the joiner's view is closed under the reply. Bounded: the states are
every causal set of the rows below holding `old`, before and after the reply. -/

def beside : Row := ⟨3, 1, 1, 6, [], [], [], true, 1⟩      -- a row 9 reaches on its own
def hiddenR : Row := ⟨4, 1, 1, 4, [], [], [], true, 2⟩     -- a row before 9 joined, named by nothing
def aside : Row := ⟨5, 3, 1, 4, [], [], [1], true, 3⟩      -- names `old` before 9 joined

def subsetsOf : List Row → List (List Row)
  | [] => [[]]
  | x :: xs => (subsetsOf xs).map (x :: ·) ++ subsetsOf xs

/-- the causal states holding `old`: `old` is the oldest row; `aside` only with `old` -/
def waitStates : List Mesh :=
  let before := (subsetsOf [beside, hiddenR, aside]).map (· ++ [old])
  before ++ before.map (reply :: ·)

def admitOnce (x : Row) (m : Mesh) : Mesh := if x ∈ m then m else x :: m

theorem waitStates_step : ∀ m ∈ waitStates, admitOnce reply m ∈ waitStates := by decide

theorem carriage_closed_bounded : closedOn waitStates (view w0 9) (admitOnce reply) = true := by
  decide

/-- **(c) CLOSED WITH THE WAIT (bounded).** On the causal states, the joiner's next view is a
    function of its view and the reply. -/
theorem carriage_closed_with_wait :
    Closed (fun s : {m // m ∈ waitStates} => view w0 9 s.val)
      (fun s => ⟨admitOnce reply s.val, waitStates_step s.val s.property⟩) :=
  closed_of_closedOn waitStates (view w0 9) (admitOnce reply) waitStates_step
    carriage_closed_bounded

/-! ## Part 3. The private room (CC 3.1.3.2)

A private room's roster seats room keys. The binding of a room key to a person is never a row; a
member's node holds the bindings made for it. Standing is read from the rows, and no rule of
standing reads a binding. A count of persons reads the bindings. -/

abbrev Person := Nat

inductive RKind | seat | speech | removal
  deriving DecidableEq, Repr

structure RRow where
  signer : Key
  kind : RKind
  target : Key        -- the room key a seat or a removal names
  body : Nat
  deriving DecidableEq, Repr

structure Room where
  rows : List RRow
  bindings : List (Key × Person)   -- held by a member's node; never a row
  deriving DecidableEq, Repr

/-- the seated room keys, read from the rows alone -/
def seated (rows : List RRow) : List Key :=
  ((rows.filter (fun r => r.kind = .seat)).map (·.target)).filter
    (fun k => !(rows.any fun r => r.kind = .removal && r.target = k))

def personOf (b : List (Key × Person)) (k : Key) : Option Person :=
  (b.find? (fun e => e.1 = k)).map (·.2)

/-- whether a person is in the room -/
def isMember (p : Person) (s : Room) : Bool :=
  (seated s.rows).any (fun k => personOf s.bindings k = some p)

/-- who said what: each speech row with the person of its signer -/
def whoSaid (s : Room) : List (RRow × Option Person) :=
  (s.rows.filter (fun r => r.kind = .speech)).map (fun r => (r, personOf s.bindings r.signer))

/-- the count of persons (CC 4.5.13 read through the bindings, CC 3.1.3.2) -/
def personCount (s : Room) : Nat :=
  ((seated s.rows).filterMap (personOf s.bindings)).eraseDups.length

/-- whether a room key stands in the room: read from the rows -/
def stands (k : Key) (s : Room) : Bool := decide (k ∈ seated s.rows)

/-- the three readers -/
def memberView (s : Room) : List RRow × List (Key × Person) := (s.rows, s.bindings)
def rowsView (s : Room) : List RRow := s.rows
def outsiderView (_ : Room) : Unit := ()

/-- **(a) DECIDES: standing reads no binding.** Whether a room key stands factors through the
    rows alone, so any holder of the rows decides it, member or not. -/
theorem standing_reads_rows (k : Key) : Factors (stands k) rowsView :=
  ⟨fun rows => decide (k ∈ seated rows), rfl⟩

/-- **(a) DECIDES.** A member's node holding the bindings decides who is in the room, who said
    what and the count of persons. -/
theorem member_decides_membership (p : Person) : Factors (isMember p) memberView :=
  ⟨fun v => (seated v.1).any (fun k => personOf v.2 k = some p), rfl⟩

theorem member_decides_who_said : Factors whoSaid memberView :=
  ⟨fun v : List RRow × List (Key × Person) =>
    (v.1.filter (fun r => decide (r.kind = RKind.speech))).map (fun r => (r, personOf v.2 r.signer)),
    by funext s; rfl⟩

theorem member_decides_count : Factors personCount memberView :=
  ⟨fun v => ((seated v.1).filterMap (personOf v.2)).eraseDups.length, rfl⟩

def seat10 : RRow := ⟨10, .seat, 10, 0⟩
def seat11 : RRow := ⟨11, .seat, 11, 0⟩
def speak10 : RRow := ⟨10, .speech, 0, 7⟩

/-- **(b) HIDES: who said it.** The rows do not tell who said it: the same rows, the room key
    bound to person 1 or to person 2. -/
theorem rows_hide_who_said : ¬ Factors whoSaid rowsView := by
  apply not_factors_of_separatesFiber
  exact ⟨⟨[speak10, seat10], [(10, 1)]⟩, ⟨[speak10, seat10], [(10, 2)]⟩, rfl, by decide⟩

/-- **(b) HIDES: who is in the room**, from a holder of the rows without the bindings. -/
theorem rows_hide_membership : ¬ Factors (isMember 1) rowsView := by
  apply not_factors_of_separatesFiber
  exact ⟨⟨[seat10], [(10, 1)]⟩, ⟨[seat10], [(10, 2)]⟩, rfl, by decide⟩

/-- **(b) The count of persons needs the bindings**: two room keys of one person or of two. -/
theorem person_count_needs_bindings : ¬ Factors personCount rowsView := by
  apply not_factors_of_separatesFiber
  exact ⟨⟨[seat11, seat10], [(10, 1), (11, 1)]⟩, ⟨[seat11, seat10], [(10, 1), (11, 2)]⟩, rfl,
    by decide⟩

/-- **(b) HIDES: membership, from an outsider.** -/
theorem outsider_hides_membership : ¬ Factors (isMember 1) outsiderView := by
  apply not_factors_of_separatesFiber
  exact ⟨⟨[], []⟩, ⟨[seat10], [(10, 1)]⟩, rfl, by decide⟩

/-- **(b) HIDES: that the room has any row**, from an outsider. -/
theorem outsider_hides_existence : ¬ Factors (fun s : Room => s.rows.isEmpty) outsiderView := by
  apply not_factors_of_separatesFiber
  exact ⟨⟨[], []⟩, ⟨[speak10], []⟩, rfl, by decide⟩

/-- the room's steps: a row signed under a room key, and a joining (a seat row and, apart from
    the rows, the binding the member's node is given) -/
def speak (r : RRow) (s : Room) : Room := ⟨r :: s.rows, s.bindings⟩
def join (k : Key) (p : Person) (s : Room) : Room := ⟨⟨k, .seat, k, 0⟩ :: s.rows, (k, p) :: s.bindings⟩

/-- **(c)** An outsider's view is held under every step of the room. -/
theorem outsider_held_speak (r : RRow) : Held outsiderView (speak r) := rfl
theorem outsider_held_join (k : Key) (p : Person) : Held outsiderView (join k p) := rfl

/-- **(c)** The member's view and the rows view are closed under both steps. -/
theorem member_closed_speak (r : RRow) : Closed memberView (speak r) :=
  ⟨fun v => (r :: v.1, v.2), rfl⟩
theorem member_closed_join (k : Key) (p : Person) : Closed memberView (join k p) :=
  ⟨fun v => (⟨k, .seat, k, 0⟩ :: v.1, (k, p) :: v.2), rfl⟩
theorem rows_closed_join (k : Key) (p : Person) : Closed rowsView (join k p) :=
  ⟨fun v => ⟨k, .seat, k, 0⟩ :: v, rfl⟩

/-- **(c) The stated limit, confirmed.** A holder of the rows sees that a joining happened: its
    view is not held under a joining (CC 3.1.3.2 "What a private room does not give"). -/
theorem rows_see_a_joining (k : Key) (p : Person) : ¬ Held rowsView (join k p) := by
  intro h
  have := congrFun h ⟨[], []⟩
  simp [rowsView, join, Function.comp] at this

/-! ## Part 4. The public roster and the served set

A public room seats identities, and its roster is public: a non-member reads the roster and the
content by asking a member's node (CC 3.2, CC 5.2's table). A responder serves a stranger the
public self-authenticating rows and the announced testimony of a subject whose live
federation-scope owner-binding it holds, and nothing more; an owned node's route never (CC 5.4.6). -/

/-- **(a) DECIDES: the public roster.** In a public room an outsider's view is the rows, and the
    rows seat identities, so who is in the room is decided by the outsider. -/
def isMemberPublic (p : Key) (rows : List RRow) : Bool := decide (p ∈ seated rows)

theorem public_roster_decides_membership (p : Key) :
    Factors (fun s : Room => isMemberPublic p s.rows) rowsView :=
  ⟨isMemberPublic p, rfl⟩

inductive Item
  | keyRecord (k : Key)
  | fedBinding (owner node : Key)       -- a live federation-scope owner-binding
  | occurrence (subject : Key) (fed : Bool)   -- `fed = false`: placed addressed to a contact
  | publicKind (subject : Key)
  | ownedRoute (node : Key)
  | unownedRoute (node : Key)
  | scoped (row : Nat)
  | contactGrant (a b : Key)
  deriving DecidableEq, Repr

def bindsSubject (s : Key) : Item → Bool
  | .fedBinding o _ => decide (o = s)
  | _ => false

def hasBinding (held : List Item) (s : Key) : Bool := held.any (bindsSubject s)

/-- the served set, read with the audience rule: testimony is served when it is at federation
    scope and the subject's binding is held -/
def servedBy (bound : Key → Bool) : Item → Bool
  | .keyRecord _ => true
  | .fedBinding _ _ => true
  | .occurrence s fed => fed && bound s
  | .publicKind s => bound s
  | .unownedRoute _ => true
  | .ownedRoute _ => false
  | .scoped _ => false
  | .contactGrant _ _ => false

def strangerView (held : List Item) : List Item := held.filter (servedBy (hasBinding held))

theorem any_filter_of_imp {α : Type} (p q : α → Bool) (hq : ∀ a, q a = true → p a = true) :
    ∀ l : List α, (l.filter p).any q = l.any q := by
  intro l
  induction l with
  | nil => rfl
  | cons a t ih =>
    cases hqa : q a
    · cases hpa : p a <;> simp [List.filter_cons, hpa, hqa, ih]
    · simp [List.filter_cons, hq a hqa, hqa]

theorem hasBinding_view (held : List Item) (s : Key) :
    hasBinding (strangerView held) s = hasBinding held s := by
  unfold strangerView hasBinding
  apply any_filter_of_imp
  intro a ha
  cases a <;> simp_all [bindsSubject, servedBy]

/-- **(a) DECIDES.** A stranger decides whether a subject is announced at this responder. -/
theorem stranger_decides_announced (s : Key) :
    Factors (fun held => hasBinding held s) strangerView :=
  ⟨fun v => hasBinding v s, by funext held; exact (hasBinding_view held s).symm⟩

/-- **(a) DECIDES.** A stranger decides whether the responder holds a key's public record. -/
theorem stranger_decides_key_record (k : Key) :
    Factors (fun held => decide (Item.keyRecord k ∈ held)) strangerView := by
  refine ⟨fun v => decide (Item.keyRecord k ∈ v), ?_⟩
  funext held
  simp [strangerView, List.mem_filter, servedBy]

/-- **(b) HIDES.** The stranger never learns that the responder holds an owned node's route, a
    contact grant, a scoped row, or an occurrence placed with a contact. -/
theorem stranger_never_learns_owned_route (n : Key) :
    ¬ Factors (fun held => decide (Item.ownedRoute n ∈ held)) strangerView := by
  apply not_factors_of_separatesFiber
  exact ⟨[], [.ownedRoute n], by simp [strangerView, servedBy], by simp⟩

theorem stranger_never_learns_contacts (a b : Key) :
    ¬ Factors (fun held => decide (Item.contactGrant a b ∈ held)) strangerView := by
  apply not_factors_of_separatesFiber
  exact ⟨[], [.contactGrant a b], by simp [strangerView, servedBy], by simp⟩

theorem stranger_never_learns_scoped (r : Nat) :
    ¬ Factors (fun held => decide (Item.scoped r ∈ held)) strangerView := by
  apply not_factors_of_separatesFiber
  exact ⟨[], [.scoped r], by simp [strangerView, servedBy], by simp⟩

theorem stranger_never_learns_sealed_occurrence (s n : Key) :
    ¬ Factors (fun held => decide (Item.occurrence s false ∈ held)) strangerView := by
  apply not_factors_of_separatesFiber
  refine ⟨[.fedBinding s n], [.fedBinding s n, .occurrence s false], ?_, by simp⟩
  simp [strangerView, servedBy, hasBinding, bindsSubject]

/-- the served set read without the audience rule: testimony whenever the binding is held -/
def servedLiteral (bound : Key → Bool) : Item → Bool
  | .occurrence s _ => bound s
  | i => servedBy bound i

def strangerViewLiteral (held : List Item) : List Item :=
  held.filter (servedLiteral (hasBinding held))

/-- **FINDING (composition).** Read alone, the served-set sentence would serve a stranger the
    occurrence an unannounced identity placed with a contact, once the identity announces. -/
theorem literal_reading_serves_sealed_occurrence (s n : Key) :
    Item.occurrence s false ∈ strangerViewLiteral [.fedBinding s n, .occurrence s false] := by
  simp [strangerViewLiteral, servedLiteral, servedBy, hasBinding, bindsSubject]

/-- the responder's step: it comes to hold one more item -/
def hold (i : Item) (held : List Item) : List Item := i :: held

theorem hasBinding_hold (i : Item) (hi : ∀ s, bindsSubject s i = false) (held : List Item)
    (s : Key) : hasBinding (hold i held) s = hasBinding held s := by
  simp [hasBinding, hold, List.any_cons, hi s]

/-- **(c) CLOSED.** Coming to hold anything but a binding moves the stranger's view by a
    function of that view and the item. -/
theorem stranger_closed_hold (i : Item) (hi : ∀ s, bindsSubject s i = false) :
    Closed strangerView (hold i) := by
  refine ⟨fun v => (if servedBy (hasBinding v) i then [i] else []) ++ v, ?_⟩
  funext held
  have hb : hasBinding (hold i held) = hasBinding held := funext (hasBinding_hold i hi held)
  simp only [Function.comp, strangerView, hb, hasBinding_view]
  have hv : hasBinding (held.filter (servedBy (hasBinding held))) = hasBinding held :=
    funext (hasBinding_view held)
  simp only [hold, List.filter_cons, hv]
  cases servedBy (hasBinding held) i <;> simp

/-- **(c) HELD.** Coming to hold a route of an owned node, a contact grant, a scoped row or an
    occurrence placed with a contact leaves the stranger's view as it was. -/
theorem stranger_held_private (i : Item) (hi : ∀ s, bindsSubject s i = false)
    (hpriv : ∀ b, servedBy b i = false) : Held strangerView (hold i) := by
  funext held
  have hb : hasBinding (hold i held) = hasBinding held := funext (hasBinding_hold i hi held)
  simp only [Function.comp, strangerView, hb]
  simp [hold, List.filter_cons, hpriv]

/-- **(c) FINDING: NOT CLOSED UNDER A BINDING.** Coming to hold a subject's binding is not closed:
    federation-scope testimony held before the binding is served after it, so the stranger's next
    view depends on what it could not see. -/
theorem stranger_not_closed_binding (s n : Key) :
    ¬ Closed strangerView (hold (.fedBinding s n)) := by
  intro h
  have := h.never_splits [] [.occurrence s true]
    (by simp [strangerView, servedBy, hasBinding, bindsSubject])
  simp [strangerView, hold, servedBy, hasBinding, bindsSubject] at this

end AudienceView

/-! ## The axioms each top theorem rests on -/
#print axioms AudienceView.factors_iff_not_separatesFiber
#print axioms AudienceView.closed_iff_fiber_invariant
#print axioms AudienceView.closed_iff_viewClosed
#print axioms AudienceView.admit_outside_is_held
#print axioms AudienceView.admit_inside_is_closed
#print axioms AudienceView.admit_is_closed
#print axioms AudienceView.outside_row_hidden
#print axioms AudienceView.party_rows_decided
#print axioms AudienceView.party_decisions_decided
#print axioms AudienceView.reply_carries_to_joiner
#print axioms AudienceView.carriage_not_closed
#print axioms AudienceView.carriage_closed_with_wait
#print axioms AudienceView.standing_reads_rows
#print axioms AudienceView.member_decides_membership
#print axioms AudienceView.member_decides_who_said
#print axioms AudienceView.member_decides_count
#print axioms AudienceView.rows_hide_who_said
#print axioms AudienceView.rows_hide_membership
#print axioms AudienceView.person_count_needs_bindings
#print axioms AudienceView.outsider_hides_membership
#print axioms AudienceView.outsider_hides_existence
#print axioms AudienceView.outsider_held_speak
#print axioms AudienceView.outsider_held_join
#print axioms AudienceView.member_closed_speak
#print axioms AudienceView.member_closed_join
#print axioms AudienceView.rows_closed_join
#print axioms AudienceView.rows_see_a_joining
#print axioms AudienceView.public_roster_decides_membership
#print axioms AudienceView.stranger_decides_announced
#print axioms AudienceView.stranger_decides_key_record
#print axioms AudienceView.stranger_never_learns_owned_route
#print axioms AudienceView.stranger_never_learns_contacts
#print axioms AudienceView.stranger_never_learns_scoped
#print axioms AudienceView.stranger_never_learns_sealed_occurrence
#print axioms AudienceView.literal_reading_serves_sealed_occurrence
#print axioms AudienceView.stranger_closed_hold
#print axioms AudienceView.stranger_held_private
#print axioms AudienceView.stranger_not_closed_binding
