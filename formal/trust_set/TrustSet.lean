/-
  formal/trust_set/TrustSet.lean — the reader's pinned trust set

  "Who I trust" is one of the reader's options: it adds licensors, licensors of licensors, or a
  class of licensor (medical, legal, financial), and removes them — the shipped root included.

  CC 4.4.3.8: the pinned trust set is a graph and its roots are pluggable; a reader trusts an
  authority by hanging an acceptance edge off its own base, "added and removed freely"; the
  shipped root is the default entry, never the root. CC 2.4.1.2.1: a licence is a leaf — holding
  one never confers issuing one, and never confers trust. CC 4.1.1: a walk is capped at five hops.

  The model: a finite world of authorities, acceptance edges (each the signed row of the key it
  leaves), licence classes declared in charters, and licences. The reader's verdict on a licence
  is a function of the reader's OWN edges and the edges of the authorities those reach, within
  the depth the reader set, and of nothing else. Every theorem below is about that function.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.
-/

namespace TrustSet

/-- a key: the reader, an authority, a licence holder; `0` is reserved for the reader -/
abbrev Key := Nat
/-- a licence class: medical, legal, financial, … -/
abbrev Class := Nat

/-- an acceptance edge: `from` trusts `to` as a licensor. `classes = []` is the wire's ABSENT
    `trust_classes` (every class the target declares); otherwise only the classes listed (on the
    wire a present list is non-empty; the empty list is refused at admission). `depth` is how far the trust walk may
    continue past `to` (0 = this authority alone, no licensors-of-licensors). -/
structure Accepts where
  src : Key
  dst : Key
  classes : List Class
  depth : Nat
  deriving DecidableEq, Repr

/-- a licence: authority `auth` licensed `holder` in class `cls` (CC 2.4.1.2.1) -/
structure Licence where
  auth : Key
  holder : Key
  cls : Class
  deriving DecidableEq, Repr

/-- the world the reader reads: every acceptance edge (its own and every authority's, replicated
    rows), every charter's declared classes, every licence -/
structure World where
  edges : List Accepts
  charter : Key → List Class      -- the classes an authority's charter declares (CC 2.4.1.2.1)
  licences : List Licence

def reader : Key := 0
/-- the CC 4.1.1 traversal cap -/
def hopCap : Nat := 5

/-- an edge admits a class when it lists it, or lists nothing -/
def Accepts.admits (e : Accepts) (c : Class) : Bool := e.classes.isEmpty || e.classes.contains c

/-- the walk, structural on a fuel so the kernel can run it: `walk w f k c b a` says that from key
    `k`, with budget `b` hops left, the reader's walk reaches authority `a` for class `c`. A step
    uses an edge that leaves `k`, admits `c`, and whose own `depth` bounds the rest of the walk. -/
def walk (w : World) : Nat → Key → Class → Nat → Key → Bool
  | 0, _, _, _, _ => false
  | f + 1, k, c, b, a =>
      match b with
      | 0 => false
      | b + 1 => w.edges.any (fun e =>
          e.src == k && e.admits c && (e.dst == a || walk w f e.dst c (min b e.depth) a))

/-- `reaches w k c n a`: the walk from `k` with `n` hops of budget (and `n` of fuel, which is
    never the binding bound: the budget falls at least as fast) -/
def reaches (w : World) (k : Key) (c : Class) (n : Nat) (a : Key) : Bool := walk w n k c n a

/-- the reader honours a licence iff its own walk, from its own base, within the cap, reaches
    the issuing authority for the licence's class, and that authority's charter declares the
    class -/
def honours (w : World) (l : Licence) : Bool :=
  (w.charter l.auth).contains l.cls && reaches w reader l.cls hopCap l.auth

/-! ## The one lemma the rest rests on

  The walk is monotone in two things at once: more edges never reach less, and more budget never
  reaches less. Stated once with an explicit bound so the inner call, whose budget is
  `min n e.depth`, is covered by the induction. -/

private theorem bool_and_left {a b : Bool} (h : (a && b) = true) : a = true := by
  cases a <;> simp at h ⊢
private theorem bool_and_right {a b : Bool} (h : (a && b) = true) : b = true := by
  cases a <;> simp at h ⊢; exact h

theorem walk_mono (w w' : World) (hsub : ∀ e ∈ w.edges, e ∈ w'.edges) (c : Class) (a : Key) :
    ∀ f f' b b' k, f ≤ f' → b ≤ b' → walk w f k c b a = true → walk w' f' k c b' a = true := by
  intro f
  induction f with
  | zero => intro f' b b' k _ _ h; simp [walk] at h
  | succ f ih =>
    intro f' b b' k hf hb h
    cases f' with
    | zero => exact absurd hf (Nat.not_succ_le_zero f)
    | succ f' =>
      cases b with
      | zero => simp [walk] at h
      | succ b =>
        cases b' with
        | zero => exact absurd hb (Nat.not_succ_le_zero b)
        | succ b' =>
          simp only [walk] at h ⊢
          rw [List.any_eq_true] at h ⊢
          obtain ⟨e, he, hp⟩ := h
          refine ⟨e, hsub e he, ?_⟩
          have h12 := bool_and_left hp
          have h3 := bool_and_right hp
          have h1 := bool_and_left h12
          have h2 := bool_and_right h12
          rw [h1, h2]
          simp only [Bool.true_and]
          cases hd : (e.dst == a) with
          | true => simp
          | false =>
            rw [hd] at h3
            simp only [Bool.false_or] at h3
            have hle : min b e.depth ≤ min b' e.depth :=
              Nat.le_min.mpr ⟨Nat.le_trans (Nat.min_le_left _ _) (Nat.le_of_succ_le_succ hb), Nat.min_le_right _ _⟩
            simp [ih f' (min b e.depth) (min b' e.depth) e.dst (Nat.le_of_succ_le_succ hf) hle h3]

theorem reaches_mono_gen (w w' : World) (hsub : ∀ e ∈ w.edges, e ∈ w'.edges) (c : Class) (a : Key) :
    ∀ m n k, m ≤ n → reaches w k c m a = true → reaches w' k c n a = true := by
  intro m n k hmn h
  exact walk_mono w w' hsub c a m n m n k hmn hmn h

/-- more edges, more reach -/
theorem reaches_mono (w w' : World) (hsub : ∀ e ∈ w.edges, e ∈ w'.edges)
    (k : Key) (c : Class) (n : Nat) (a : Key) (h : reaches w k c n a = true) :
    reaches w' k c n a = true :=
  reaches_mono_gen w w' hsub c a n n k (Nat.le_refl n) h

/-- more budget, more reach -/
theorem reaches_mono_budget (w : World) (k : Key) (c : Class) (m n : Nat) (hmn : m ≤ n) (a : Key)
    (h : reaches w k c m a = true) : reaches w k c n a = true :=
  reaches_mono_gen w w (fun _ he => he) c a m n k hmn h

/-- the same edges, the same reach, whatever else the world holds -/
theorem reaches_same_edges (w w' : World) (he : ∀ e, e ∈ w.edges ↔ e ∈ w'.edges)
    (k : Key) (c : Class) (n : Nat) (a : Key) : reaches w k c n a = reaches w' k c n a := by
  have h1 := reaches_mono w w' (fun e h => (he e).mp h) k c n a
  have h2 := reaches_mono w' w (fun e h => (he e).mpr h) k c n a
  cases hx : reaches w k c n a <;> cases hy : reaches w' k c n a
  · rfl
  · exact absurd (h2 hy) (by simp [hx])
  · exact absurd (h1 hx) (by simp [hy])
  · rfl

/-! ## T1. Nothing is honoured without the reader's own edge

  Every honoured licence rests on an edge that leaves the reader. Delete the reader's edges and
  the verdict is `false` for every licence, whatever the rest of the graph says. -/

theorem reaches_needs_an_edge_from (w : World) (k : Key) (c : Class) (n : Nat) (a : Key)
    (h : reaches w k c n a = true) : ∃ e ∈ w.edges, e.src = k := by
  unfold reaches at h
  cases n with
  | zero => simp [walk] at h
  | succ n =>
    simp only [walk] at h
    rw [List.any_eq_true] at h
    obtain ⟨e, he, hp⟩ := h
    refine ⟨e, he, ?_⟩
    have h1 := bool_and_left (bool_and_left hp)
    exact beq_iff_eq.mp h1

/-- the reader's verdict needs the reader's own edge -/
theorem no_trust_without_my_edge (w : World) (l : Licence) (h : honours w l = true) :
    ∃ e ∈ w.edges, e.src = reader := by
  unfold honours at h
  exact reaches_needs_an_edge_from w reader l.cls hopCap l.auth (bool_and_right h)

/-- a world whose reader has no edge honours nothing -/
theorem empty_set_honours_nothing (w : World) (hno : ∀ e ∈ w.edges, e.src ≠ reader) (l : Licence) :
    honours w l = false := by
  cases hh : honours w l with
  | false => rfl
  | true =>
    obtain ⟨e, he, hs⟩ := no_trust_without_my_edge w l hh
    exact absurd hs (hno e he)

/-! ## T2. A licence confers no trust

  The walk reads acceptance edges only. Licences are not edges: adding any licence to the world,
  or removing every one, changes no reach. Holding a licence from A makes nobody a licensor the
  reader trusts (CC 2.4.1.2.1: a licence is a leaf; I4 of `formal/authority_tree`). -/

theorem licences_move_no_reach (w : World) (ls : List Licence) (k : Key) (c : Class) (n : Nat) (a : Key) :
    reaches { w with licences := ls } k c n a = reaches w k c n a :=
  reaches_same_edges { w with licences := ls } w (fun _ => Iff.rfl) k c n a

/-- the verdict on a licence does not depend on which other licences exist -/
theorem licence_confers_no_trust (w : World) (ls : List Licence) (l : Licence) :
    honours { w with licences := ls } l = honours w l := by
  unfold honours; rw [licences_move_no_reach]

/-! ## T3. The shipped root is one entry

  Removing the edge to the shipped root removes exactly what reached only through it; what the
  reader reaches through another of its edges is reached still, because the walk is monotone in
  the edge list. -/

/-- remove one edge -/
def without (w : World) (x : Accepts) : World := { w with edges := w.edges.filter (fun e => e != x) }

theorem without_sub (w : World) (x : Accepts) : ∀ e ∈ (without w x).edges, e ∈ w.edges := by
  intro e he; simp [without, List.mem_filter] at he; exact he.1

/-- removing an edge never adds reach -/
theorem removal_only_removes (w : World) (x : Accepts) (l : Licence)
    (h : honours (without w x) l = true) : honours w l = true := by
  unfold honours at h ⊢
  have hc := bool_and_left h
  have hr := bool_and_right h
  simp only [without] at hc
  rw [hc]
  simp only [Bool.true_and]
  exact reaches_mono (without w x) w (without_sub w x) reader l.cls hopCap l.auth hr

/-! ## T4. Class trust

  An edge that lists classes admits exactly those; an edge that lists none admits what the
  target declares. So "trust A for medical" honours A's medical licences and none of A's legal
  ones, through that edge. -/

theorem class_edge_admits_listed (e : Accepts) (c : Class) (hc : e.classes.contains c = true) :
    e.admits c = true := by
  unfold Accepts.admits; rw [hc]; cases e.classes.isEmpty <;> rfl

theorem class_edge_refuses_unlisted (e : Accepts) (c : Class) (hne : e.classes ≠ [])
    (hc : e.classes.contains c = false) : e.admits c = false := by
  unfold Accepts.admits
  have hemp : e.classes.isEmpty = false := by
    cases h : e.classes with
    | nil => exact absurd h hne
    | cons _ _ => rfl
  rw [hemp, hc]; rfl

/-- and the charter is the second gate: a class the authority's charter does not declare is never
    honoured, whatever the reader's edges say -/
theorem undeclared_class_never_honoured (w : World) (l : Licence)
    (h : (w.charter l.auth).contains l.cls = false) : honours w l = false := by
  unfold honours; rw [h]; rfl

/-! ## T5. Depth

  More budget never reaches less (`reaches_mono_budget`), so an edge's `depth` can only lower the
  walk past that authority, and the global cap of five (CC 4.1.1) is the outer bound: the verdict
  is the walk at the cap. -/

theorem verdict_is_the_capped_walk (w : World) (l : Licence) :
    honours w l = ((w.charter l.auth).contains l.cls && reaches w reader l.cls hopCap l.auth) := rfl

/-! ## T6. Determinism: order never matters

  The verdict reads the edge list as a set: permuting the edges changes nothing. -/

theorem reaches_perm (w w' : World) (h : ∀ e, e ∈ w.edges ↔ e ∈ w'.edges)
    (k : Key) (c : Class) (n : Nat) (a : Key) : reaches w k c n a = reaches w' k c n a := by
  have h1 := reaches_mono w w' (fun e he => (h e).mp he) k c n a
  have h2 := reaches_mono w' w (fun e he => (h e).mpr he) k c n a
  cases hx : reaches w k c n a <;> cases hy : reaches w' k c n a
  · rfl
  · exact absurd (h2 hy) (by simp [hx])
  · exact absurd (h1 hx) (by simp [hy])
  · rfl

/-! ## The worked world: the clause as a run

  The reader ships with one edge, to the CIRIS root (key 1), every class, depth 5. A hospital
  board (key 2) declares the medical class and licenses a clinician (key 10). The reader adds
  "medical under the board" as its own edge, then removes the CIRIS root. The clinician's medical
  licence is honoured before and after; the board's legal licence (key 11) never is; a licence
  from an authority the reader never trusted (key 3 licensing key 12) never is. -/

def ciris : Key := 1
def board : Key := 2
def stranger : Key := 3
def medical : Class := 1
def legal : Class := 2

def rootEdge : Accepts := ⟨reader, ciris, [], 5⟩
def boardEdge : Accepts := ⟨reader, board, [medical], 0⟩

def charter0 : Key → List Class
  | 1 => [medical, legal]
  | 2 => [medical, legal]
  | 3 => [medical]
  | _ => []

def clinician : Licence := ⟨board, 10, medical⟩
def boardLegal : Licence := ⟨board, 11, legal⟩
def strangerMed : Licence := ⟨stranger, 12, medical⟩

/-- as shipped: the root alone -/
def shipped : World := ⟨[rootEdge], charter0, [clinician, boardLegal, strangerMed]⟩
/-- the reader added the board for medical -/
def withBoard : World := ⟨[rootEdge, boardEdge], charter0, shipped.licences⟩
/-- and removed the CIRIS root -/
def withoutCiris : World := without withBoard rootEdge

theorem shipped_trusts_no_board : honours shipped clinician = false := by decide
theorem board_added : honours withBoard clinician = true := by decide
theorem board_legal_not_trusted : honours withBoard boardLegal = false := by decide
theorem stranger_never : honours withBoard strangerMed = false := by decide
/-- the root removed: the reader's own medical trust stands -/
theorem root_removed_board_stands : honours withoutCiris clinician = true := by decide
theorem root_removed_edges : withoutCiris.edges = [boardEdge] := by decide

/-- licensors of licensors: the board trusts a college (key 4) for medical; with depth 1 on the
    reader's edge, the college's licence (key 13) is honoured; with depth 0 it is not -/
def college : Key := 4
def collegeMed : Licence := ⟨college, 13, medical⟩
def boardTrustsCollege : Accepts := ⟨board, college, [medical], 0⟩
def charter1 : Key → List Class
  | 4 => [medical]
  | k => charter0 k
def deep : World := ⟨[⟨reader, board, [medical], 1⟩, boardTrustsCollege], charter1, [collegeMed]⟩
def shallow : World := ⟨[⟨reader, board, [medical], 0⟩, boardTrustsCollege], charter1, [collegeMed]⟩

theorem licensor_of_licensor_at_depth_one : honours deep collegeMed = true := by decide
theorem licensor_of_licensor_cut_at_depth_zero : honours shallow collegeMed = false := by decide

end TrustSet
