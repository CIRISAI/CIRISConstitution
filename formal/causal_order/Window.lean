/-
  Window.lean — the window with a signed outcome, and the roster tips

  Part C. THE WINDOW. A row `p` opens it. A concluder signs a receipt naming `p` and later a
          landing naming the receipt and the concluder's then-current head. The landing says
          the window closed unopposed. Two rules for an objection the landing does not name
          are stated and compared. The duration of a window is not in the rows: nothing here
          reads an instant, and no theorem here says a landing came late enough.
  Part D. TIPS WAIT. Versions name the heads they extend; the tips are the versions no kept
          version names; the roster is what all tips list. With a strict majority of the
          named head behind every version, two versions of one head share a signer.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Seat.lean.
-/

import Seat

namespace Kernel

open Order Relation Causal

/-! ## Part C. The window -/

section Window

variable {Row Key : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key)
/- `objects x p`: `x` is a row naming `p`, of the objecting kind, by a key entitled to object.
   That the landing names a receipt by its own signer, that the receipt names `p`, and that
   the signer holds a seat that may conclude `p`'s slot at the head the landing names, are
   the conclusion layer's (they read the landing's past only) and sit inside `A lam`. -/
variable (objects : Row → Row → Prop)

/-- Inside the window: in the landing's past and not in the receipt's. -/
def inside (ρ lam x : Row) : Prop := TransGen parent x lam ∧ ¬ TransGen parent x ρ

/-- The landing has a concluded objection in its past (inside the window, or already in the
    receipt's past: both are objections the concluder has acknowledged by naming them). -/
def opposed (A : Row → Prop) (p lam : Row) : Prop :=
  ∃ x, A x ∧ objects x p ∧ TransGen parent x lam

/-- The concluder forked its own rows around an objection: a concluded row by the landing's
    signer, concurrent with the landing, has a concluded objection in its past. Two rows by
    one key, neither naming the other, is something rows do show. -/
def forked (A : Row → Prop) (p lam : Row) : Prop :=
  ∃ α x, A α ∧ signer α = signer lam ∧ conc parent α lam ∧
    A x ∧ objects x p ∧ TransGen parent x α

/-- RULE (i), the rule chosen. The landing is a cut on `p`'s slot. It counts iff it is
    concluded, no objection is in its past, and its signer has no concurrent row of its own
    with an objection in its past. -/
def landsI (A : Row → Prop) (p lam : Row) : Prop :=
  A lam ∧ ¬ opposed parent objects A p lam ∧ ¬ forked parent signer objects A p lam

/-- Under rule (i) an objection counts unless a counting landing is concurrent with it:
    the cut voids what is on its slot and concurrent. -/
def objectionI (A : Row → Prop) (p lam x : Row) : Prop :=
  A x ∧ objects x p ∧ ¬ (landsI parent signer objects A p lam ∧ conc parent x lam)

/-- A concluded objection concurrent with the landing. -/
def unanswered (A : Row → Prop) (p lam : Row) : Prop :=
  ∃ x, A x ∧ objects x p ∧ conc parent x lam

/-- RULE (ii), the alternative. A concurrent objection contests the landing. -/
def landsII (A : Row → Prop) (p lam : Row) : Prop :=
  A lam ∧ ¬ opposed parent objects A p lam ∧ ¬ unanswered parent objects A p lam

def contestedII (A : Row → Prop) (p lam : Row) : Prop :=
  A lam ∧ ¬ opposed parent objects A p lam ∧ unanswered parent objects A p lam

/-! ### The outcome is a function of the offered set -/

theorem landsI_function (C : (Row → Prop) → Row → Prop) (S S' : Row → Prop)
    (h : ∀ r, S r ↔ S' r) :
    landsI parent signer objects (C S) = landsI parent signer objects (C S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

theorem landsII_function (C : (Row → Prop) → Row → Prop) (S S' : Row → Prop)
    (h : ∀ r, S r ↔ S' r) :
    landsII parent objects (C S) = landsII parent objects (C S') ∧
      contestedII parent objects (C S) = contestedII parent objects (C S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]
  exact ⟨rfl, rfl⟩

/-- What is not in the rows. The concluder held the objection `x` and then signed the landing;
    or it signed the landing and then came to hold `x`. The two histories are the same rows in
    two orders, and every rule that is a function of the set gives them one outcome. Here for
    rule (i); the same holds for any function of the set. -/
theorem held_before_or_after_one_outcome (C : (Row → Prop) → Row → Prop) (l : List Row)
    (x lam : Row) :
    landsI parent signer objects (C (fun r => r ∈ l ++ [x, lam]))
      = landsI parent signer objects (C (fun r => r ∈ l ++ [lam, x])) :=
  landsI_function parent signer objects C _ _
    (fun r => by simp only [List.mem_append, List.mem_cons, List.mem_singleton,
                   List.not_mem_nil, or_false]
                 exact ⟨fun h => h.elim Or.inl (fun h => Or.inr h.symm),
                        fun h => h.elim Or.inl (fun h => Or.inr h.symm)⟩)

/-! ### An acknowledged objection -/

/-- A concluder cannot land over an objection its landing names, under either rule. -/
theorem acknowledged_objection_voids (A : Row → Prop) (p lam x : Row)
    (hx : A x) (ho : objects x p) (hin : TransGen parent x lam) :
    ¬ landsI parent signer objects A p lam ∧ ¬ landsII parent objects A p lam ∧
      ¬ contestedII parent objects A p lam :=
  ⟨fun h => h.2.1 ⟨x, hx, ho, hin⟩, fun h => h.2.1 ⟨x, hx, ho, hin⟩,
   fun h => h.2.1 ⟨x, hx, ho, hin⟩⟩

/-- In particular an objection inside the window. -/
theorem cannot_land_inside (A : Row → Prop) (p ρ lam x : Row)
    (hx : A x) (ho : objects x p) (hin : inside parent ρ lam x) :
    ¬ landsI parent signer objects A p lam ∧ ¬ landsII parent objects A p lam :=
  let h := acknowledged_objection_voids parent signer objects A p lam x hx ho hin.1
  ⟨h.1, h.2.1⟩

/-! ### An objection the landing does not name -/

/-- All that rows say of an objection the landing does not name, and that does not name the
    landing: the two are concurrent. Whether the concluder held it is not a fact about rows. -/
theorem unacknowledged_is_concurrent (lam x : Row) (h1 : ¬ TransGen parent x lam)
    (h2 : ¬ TransGen parent lam x) (h3 : x ≠ lam) : conc parent x lam :=
  ⟨h1, h2, h3⟩

/-- Rule (i): what the dishonest concluder gains. If it signs nothing else that names an
    objection, its landing counts however many objections are concurrent with it, held or
    not. -/
theorem ruleI_concluder_decides (A : Row → Prop) (p lam : Row) (hl : A lam)
    (hpast : ¬ opposed parent objects A p lam)
    (hown : ∀ α, A α → signer α = signer lam → ¬ conc parent α lam) :
    landsI parent signer objects A p lam :=
  ⟨hl, hpast, fun ⟨α, _, hα, hs, hc, _⟩ => hown α hα hs hc⟩

/-- ... and each of those objections is void. -/
theorem ruleI_ignored_objection_void (A : Row → Prop) (p lam x : Row)
    (hl : landsI parent signer objects A p lam) (hc : conc parent x lam) :
    ¬ objectionI parent signer objects A p lam x :=
  fun h => h.2.2 ⟨hl, hc⟩

/-- Rule (i): what binds it. If the concluder has signed any row with the objection in its
    past (an acknowledgement of it), and its landing counts, then that row names the landing:
    it was signed after. A concluder that has acknowledged an objection cannot land without
    naming the acknowledgement, and naming it voids the landing. -/
theorem ruleI_acknowledgement_binds (A : Row → Prop) (p lam α x : Row)
    (hl : landsI parent signer objects A p lam)
    (hα : A α) (hs : signer α = signer lam) (hx : A x) (ho : objects x p)
    (hanc : TransGen parent x α) : TransGen parent lam α :=
  Classical.byContradiction fun hn =>
    have h1 : ¬ TransGen parent α lam := fun h => hl.2.1 ⟨x, hx, ho, anc_trans hanc h⟩
    have h2 : α ≠ lam := fun e => hl.2.1 ⟨x, hx, ho, e ▸ hanc⟩
    hl.2.2 ⟨α, x, hα, hs, ⟨h1, hn, h2⟩, hx, ho, hanc⟩

/-- Rule (ii): the same rows. Any concluded objection concurrent with the landing contests
    it, held or not, timely or not. -/
theorem ruleII_any_objection_contests (A : Row → Prop) (p lam x : Row) (hl : A lam)
    (hpast : ¬ opposed parent objects A p lam)
    (hx : A x) (ho : objects x p) (hc : conc parent x lam) :
    contestedII parent objects A p lam ∧ ¬ landsII parent objects A p lam :=
  ⟨⟨hl, hpast, x, hx, ho, hc⟩, fun h => h.2.2 ⟨x, hx, ho, hc⟩⟩

/-! ### What a later row can undo -/

variable (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (C : (Row → Prop) → Row → Prop)
variable (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
variable (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
    (C S r ↔ C (fun q => S q ∨ q = x) r))
include hCk hfin

/-- Rule (i): a landing that counts is undone only by its own signer. If no row that is `x`
    or was waiting on `x` is signed by the landing's signer, the landing still counts. No
    objector, at any later time, moves it. -/
theorem ruleI_only_concluder_undoes (S : Row → Prop) (x p lam : Row) (hx : ¬ S x)
    (hl : landsI parent signer objects (C S) p lam)
    (hsig : ∀ w, (w = x ∨ TransGen parent x w) → signer w ≠ signer lam) :
    landsI parent signer objects (C (fun q => S q ∨ q = x)) p lam := by
  have hk := hCk S lam hl.1
  have past : ∀ y z, kept parent wf wellFormed S z → TransGen parent y z →
      C (fun q => S q ∨ q = x) y → C S y :=
    fun y z hz hyz hc => (hfin S x y (kept_ancestors parent wf wellFormed S y z hyz hz) hx).2 hc
  refine ⟨(hfin S x lam hk hx).1 hl.1, ?_, ?_⟩
  · intro ⟨y, hy, ho, hanc⟩
    exact hl.2.1 ⟨y, past y lam hk hanc hy, ho, hanc⟩
  · intro ⟨α, y, hα, hs, hc, hy, ho, hanc⟩
    have hne : α ≠ x ∧ ¬ TransGen parent x α :=
      ⟨fun e => hsig α (Or.inl e) hs, fun h => hsig α (Or.inr h) hs⟩
    have hkα : kept parent wf wellFormed S α :=
      (kept_new_row parent wf wellFormed S x α hne.1 hne.2).2 (hCk _ α hα)
    exact hl.2.2 ⟨α, y, (hfin S x α hkα hx).2 hα, hs, hc, past y α hkα hanc hy, ho, hanc⟩

/-- Rule (ii): a landing that counts is undone only by an objection: if no objection to `p`
    is `x` or was waiting on `x`, it still counts. -/
theorem ruleII_only_objection_undoes (S : Row → Prop) (x p lam : Row) (hx : ¬ S x)
    (hl : landsII parent objects (C S) p lam)
    (hno : ∀ w, objects w p → w ≠ x ∧ ¬ TransGen parent x w) :
    landsII parent objects (C (fun q => S q ∨ q = x)) p lam := by
  have hk := hCk S lam hl.1
  have back : ∀ y, objects y p → C (fun q => S q ∨ q = x) y → C S y :=
    fun y ho hc => (hfin S x y ((kept_new_row parent wf wellFormed S x y (hno y ho).1
      (hno y ho).2).2 (hCk _ y hc)) hx).2 hc
  exact ⟨(hfin S x lam hk hx).1 hl.1,
    fun ⟨y, hy, ho, hanc⟩ => hl.2.1 ⟨y, back y ho hy, ho, hanc⟩,
    fun ⟨y, hy, ho, hc⟩ => hl.2.2 ⟨y, back y ho hy, ho, hc⟩⟩

omit hCk hfin in
/-- Rule (ii): and an objection always can, however late. An objection first offered after
    the landing is kept, that does not name the landing, takes the landing from "counts" to
    "contested". Under rule (ii) no landing is ever final against a key entitled to object. -/
theorem ruleII_never_final (S : Row → Prop) (x p lam : Row) (hx : ¬ S x)
    (hk : kept parent wf wellFormed S lam)
    (hcx : C (fun q => S q ∨ q = x) x) (ho : objects x p) (hnn : ¬ TransGen parent lam x) :
    ¬ landsII parent objects (C (fun q => S q ∨ q = x)) p lam :=
  fun h =>
    have hn := new_row_not_ancestor parent wf wellFormed S x lam hk hx
    h.2.2 ⟨x, hcx, ho, ⟨hn.2, hnn, fun e => hn.1 e.symm⟩⟩

end Window

/-! ## Part D. Tips wait -/

section Tips

variable {V Key : Type}
/- `names h v`: version `v` names `h` among the heads it extends. `roster v k`: `v` lists `k`. -/
variable (names : V → V → Prop) (roster : V → Key → Prop)

/-- The tips of the kept versions `S`: kept, and named by no kept version. -/
def tips (S : V → Prop) (v : V) : Prop := S v ∧ ¬ ∃ u, S u ∧ names v u

/-- The roster: the keys every tip lists. -/
def rosterOf (S : V → Prop) (k : Key) : Prop := ∀ v, tips names S v → roster v k

/-- A function of the kept set. -/
theorem rosterOf_function (S S' : V → Prop) (h : ∀ v, S v ↔ S' v) :
    tips names S = tips names S' ∧ rosterOf names roster S = rosterOf names roster S' := by
  have e : S = S' := funext fun v => propext (h v)
  rw [e]
  exact ⟨rfl, rfl⟩

/-- Any arrival order. -/
theorem rosterOf_perm (l l' : List V) (h : l.Perm l') :
    rosterOf names roster (fun v => v ∈ l) = rosterOf names roster (fun v => v ∈ l') :=
  (rosterOf_function names roster _ _ (fun _ => h.mem_iff)).2

section TipsSwap

variable (σ : V → V) (hσ : ∀ x, σ (σ x) = x)
variable (hn : ∀ a b, names (σ a) (σ b) ↔ names a b)
include hσ hn

/-- Equivariant: relabelling the versions relabels the tips. -/
theorem tips_swap (S : V → Prop) (v : V) :
    tips names (fun x => S (σ x)) v ↔ tips names S (σ v) := by
  constructor
  · intro ⟨h1, h2⟩
    refine ⟨h1, fun ⟨u, hu, hnu⟩ => h2 ⟨σ u, by show S (σ (σ u)); rw [hσ]; exact hu, ?_⟩⟩
    have := (hn v (σ u)).1 (by rw [hσ]; exact hnu)
    exact this
  · intro ⟨h1, h2⟩
    exact ⟨h1, fun ⟨u, hu, hnu⟩ => h2 ⟨σ u, hu, (hn v u).2 hnu⟩⟩

/-- Equivariant: relabelling versions by `σ` and keys by `π` relabels the roster. -/
theorem rosterOf_swap (π : Key → Key) (hr : ∀ v k, roster (σ v) (π k) ↔ roster v k)
    (S : V → Prop) (k : Key) :
    rosterOf names roster (fun x => S (σ x)) k ↔ rosterOf names roster S (π k) := by
  constructor
  · intro h v hv
    have ht : tips names (fun x => S (σ x)) (σ v) :=
      (tips_swap names σ hσ hn S (σ v)).2 (by rw [hσ]; exact hv)
    have := (hr (σ v) k).2 (h (σ v) ht)
    rw [hσ] at this
    exact this
  · intro h v hv
    exact (hr v k).1 (h (σ v) ((tips_swap names σ hσ hn S v).1 hv))

/-- So two versions the kept set does not tell apart are both tips or neither is. -/
theorem tips_both_or_neither (S : V → Prop) (hS : ∀ x, S (σ x) ↔ S x) (a : V) :
    tips names S a ↔ tips names S (σ a) :=
  symmetric_same_verdict (fun S => tips names S) σ (tips_swap names σ hσ hn) S hS a

end TipsSwap

/-- A version `m` that names every tip, and that nothing kept names, is the one tip. -/
theorem merge_one_tip (S : V → Prop) (m : V)
    (hall : ∀ v, tips names S v → names v m)
    (hfresh : ∀ u, (S u ∨ u = m) → ¬ names m u) :
    ∀ v, tips names (fun q => S q ∨ q = m) v ↔ v = m := by
  intro v
  constructor
  · intro ⟨hv, hnn⟩
    cases hv with
    | inl hs =>
      have ht : tips names S v := ⟨hs, fun ⟨u, hu, hnu⟩ => hnn ⟨u, Or.inl hu, hnu⟩⟩
      exact absurd ⟨m, Or.inr rfl, hall v ht⟩ hnn
    | inr e => exact e
  · intro e
    rw [e]
    exact ⟨Or.inr rfl, fun ⟨u, hu, hnu⟩ => hfresh u hu hnu⟩

/-- And the roster is then that version's roster. -/
theorem merge_roster (S : V → Prop) (m : V)
    (hall : ∀ v, tips names S v → names v m)
    (hfresh : ∀ u, (S u ∨ u = m) → ¬ names m u) (k : Key) :
    rosterOf names roster (fun q => S q ∨ q = m) k ↔ roster m k :=
  ⟨fun h => h m ((merge_one_tip names S m hall hfresh m).2 rfl),
   fun h v hv => (merge_one_tip names S m hall hfresh v).1 hv ▸ h⟩

/-- While there are several tips, a key listed must be listed by each of them. -/
theorem roster_within_every_tip (S : V → Prop) (v : V) (hv : tips names S v) (k : Key)
    (h : rosterOf names roster S k) : roster v k :=
  h v hv

end Tips

/-! ### Quorum intersection, for finite lists -/

section Quorum

variable {K : Type} [DecidableEq K]

/-- A list without repeats, all of whose members are in `l`, is no longer than `l`. -/
theorem nodup_subset_length : ∀ (a l : List K), a.Nodup → (∀ k, k ∈ a → k ∈ l) →
    a.length ≤ l.length
  | [], _, _, _ => Nat.zero_le _
  | x :: a, l, ha, hs => by
    have hx : x ∈ l := hs x (List.mem_cons_self x a)
    have hn := List.nodup_cons.1 ha
    have ih := nodup_subset_length a (l.erase x) hn.2 (fun k hk =>
      (List.mem_erase_of_ne (fun (e : k = x) => hn.1 (e ▸ hk))).2 (hs k (List.mem_cons_of_mem x hk)))
    have hl := List.length_erase_of_mem hx
    have hp := List.length_pos_of_mem hx
    simp only [List.length_cons]
    omega

/-- The counting lemma. Two lists without repeats, inside `l`, with no common member, have
    at most `l.length` members between them. -/
theorem disjoint_length : ∀ (a b l : List K), a.Nodup → b.Nodup →
    (∀ k, k ∈ a → k ∈ l) → (∀ k, k ∈ b → k ∈ l) → (∀ k, k ∈ a → ¬ k ∈ b) →
    a.length + b.length ≤ l.length
  | [], b, l, _, hb, _, hbl, _ => by
    have := nodup_subset_length b l hb hbl
    simp only [List.length_nil]
    omega
  | x :: a, b, l, ha, hb, hal, hbl, hd => by
    have hx : x ∈ l := hal x (List.mem_cons_self x a)
    have hn := List.nodup_cons.1 ha
    have hxb : ¬ x ∈ b := hd x (List.mem_cons_self x a)
    have ih := disjoint_length a b (l.erase x) hn.2 hb
      (fun k hk => (List.mem_erase_of_ne (fun (e : k = x) => hn.1 (e ▸ hk))).2
        (hal k (List.mem_cons_of_mem x hk)))
      (fun k hk => (List.mem_erase_of_ne (fun (e : k = x) => hxb (e ▸ hk))).2 (hbl k hk))
      (fun k hk => hd k (List.mem_cons_of_mem x hk))
    have hl := List.length_erase_of_mem hx
    have hp := List.length_pos_of_mem hx
    simp only [List.length_cons]
    omega

/-- Quorum intersection. Two strict majorities of one list share a member. -/
theorem quorum_intersection (a b l : List K) (ha : a.Nodup) (hb : b.Nodup)
    (hal : ∀ k, k ∈ a → k ∈ l) (hbl : ∀ k, k ∈ b → k ∈ l)
    (hqa : l.length < 2 * a.length) (hqb : l.length < 2 * b.length) :
    ∃ k, k ∈ a ∧ k ∈ b := by
  cases hd : a.find? (fun k => decide (k ∈ b)) with
  | some k =>
    exact ⟨k, List.mem_of_find?_eq_some hd, of_decide_eq_true (List.find?_some (p := fun k => decide (k ∈ b)) hd)⟩
  | none =>
    have hdis : ∀ k, k ∈ a → ¬ k ∈ b := by
      intro k hk hkb
      have := List.find?_eq_none.1 hd k hk
      exact this (decide_eq_true hkb)
    have := disjoint_length a b l ha hb hal hbl hdis
    omega

variable {V : Type}
/- `members h`: the roster of head `h`, as a list. `signed v k`: key `k` signed version `v`. -/
variable (members : V → List K) (signed : V → K → Prop)

/-- A version is valid over a head: signed by a strict majority of that head's members. -/
def validOver (h v : V) : Prop :=
  ∃ a : List K, a.Nodup ∧ (∀ k, k ∈ a → k ∈ members h ∧ signed v k) ∧
    (members h).length < 2 * a.length

/-- Two valid versions of one head share a signer, a member of that head. Nothing is asked
    about concurrency: it holds for any two. -/
theorem fork_shares_signer (h v1 v2 : V)
    (h1 : validOver members signed h v1) (h2 : validOver members signed h v2) :
    ∃ k, k ∈ members h ∧ signed v1 k ∧ signed v2 k :=
  let ⟨a, ha, has, hqa⟩ := h1
  let ⟨b, hb, hbs, hqb⟩ := h2
  let ⟨k, hka, hkb⟩ := quorum_intersection a b (members h) ha hb
    (fun k hk => (has k hk).1) (fun k hk => (hbs k hk).1) hqa hqb
  ⟨k, (has k hka).1, (has k hka).2, (hbs k hkb).2⟩

/-- So a fork of a head needs a member who signed both versions. If no member of the head
    signs two different versions of it, the head has at most one valid version. -/
theorem no_double_signer_no_fork (h v1 v2 : V)
    (h1 : validOver members signed h v1) (h2 : validOver members signed h v2)
    (hon : ∀ k, k ∈ members h → signed v1 k → signed v2 k → v1 = v2) : v1 = v2 :=
  let ⟨k, hm, hs1, hs2⟩ := fork_shares_signer members signed h v1 v2 h1 h2
  hon k hm hs1 hs2

end Quorum

/-! ## Axioms used -/

#print axioms landsI_function
#print axioms landsII_function
#print axioms held_before_or_after_one_outcome
#print axioms acknowledged_objection_voids
#print axioms cannot_land_inside
#print axioms unacknowledged_is_concurrent
#print axioms ruleI_concluder_decides
#print axioms ruleI_ignored_objection_void
#print axioms ruleI_acknowledgement_binds
#print axioms ruleII_any_objection_contests
#print axioms ruleI_only_concluder_undoes
#print axioms ruleII_only_objection_undoes
#print axioms ruleII_never_final
#print axioms rosterOf_function
#print axioms rosterOf_perm
#print axioms tips_swap
#print axioms rosterOf_swap
#print axioms tips_both_or_neither
#print axioms merge_one_tip
#print axioms merge_roster
#print axioms nodup_subset_length
#print axioms disjoint_length
#print axioms quorum_intersection
#print axioms fork_shares_signer
#print axioms no_double_signer_no_fork

end Kernel
