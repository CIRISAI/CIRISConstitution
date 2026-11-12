/-
  Causal.lean — the kernel as a function of the set of rows, with no global rank

  Order.lean shows the kernel is a function of the offered set when rows carry a total rank
  (signed instant, id). That rank is chosen by signers, gated by a per-node first-seen instant,
  and breaks on roster forks. This file removes it.

  Rows name their parents by digest (the rows they extend or answer). `parent p r` says r names
  p. The one hypothesis is that `parent` is well-founded, which is what hash-links give: a
  digest cannot name a row that names it back, at any depth. There are no instants, no ids and
  no sequencer. Ancestry is the transitive closure of `parent`. Two rows are concurrent when
  neither is an ancestor of the other.

  What this file proves.
    T6 (i)    The door keeps a row iff it is well-formed alone and all its parents are kept. No
              row is refused because of another row. The kept set is the least fixed point of a
              monotone operator and is the same for every arrival order. For finite lists the
              closure is executable and is proved to terminate at that set.
    T6 (ii)   Conclusions are by recursion on ancestry. The rule for a row may negate and count
              over the conclusions about its ancestors, and may read which rows concurrent with
              it are live. The conclusion is a function of the kept set and the seed, and is
              the only solution of its equation.
    T6 (iii)  Locality. A new row x changes the conclusion about r only if r is x or a
              descendant of x, or r or one of r's ancestors is in concurrent conflict with x or
              with a descendant of x.
    T7        The price. If the rule is symmetric under a swap of two concurrent rows and the
              offered set is unchanged by the swap, both rows get the same conclusion and any
              symmetric holder rule names both or neither (by `Order.no_symmetric_choice`). On
              an instance: two concurrent claims leave the slot empty; a row that is a
              descendant of both decides it, with no rank; two concurrent deciding rows empty
              it again.
    T6 (v)    A seed above. Conclusions take a set of root rows. A kept row with no root at
              or above it concludes nothing. Enlarging the seed changes conclusions without any
              row being offered again, and only within the same locality as (iii).
    Reach     The reader as its own seed, below. Edges are concluded rows naming a key; the
              reader reaches keys by a bounded walk from edges it signed; a row means something
              when it is concluded and its signer is reached. Meaning is a function of the
              offered set and the reader's key. Two readers differ only through rows signed by
              their own keys. Meaning is lost only through a withdrawal row by the signer of an
              edge on a walk from the reader. The per-row conclusion stays final.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Order.lean.
-/

import Order

namespace Causal

open Order Relation

/-! ## Part A. The door -/

section Door

variable {Row : Type}

theorem anc_trans {parent : Row → Row → Prop} {a b c : Row}
    (hab : TransGen parent a b) (hbc : TransGen parent b c) : TransGen parent a c := by
  induction hbc with
  | single h => exact TransGen.tail hab h
  | tail _ h ih => exact TransGen.tail ih h

variable (parent : Row → Row → Prop) (wf : WellFounded parent)
variable (wellFormed : Row → Prop)

/-- The door. A row is kept iff it is well-formed alone and every parent it names is kept.
    It reads no other row. No negation: more rows kept can only let more rows in. -/
def doorJudge (r : Row) (P : Row → Prop) : Prop :=
  wellFormed r ∧ ∀ p, parent p r → P p

/-- The kept set for the offered set `S`. -/
noncomputable def kept (S : Row → Prop) : Row → Prop :=
  adm (TransGen parent) (WellFounded.transGen wf) (doorJudge parent wellFormed) S

theorem kept_iff (S : Row → Prop) (r : Row) :
    kept parent wf wellFormed S r ↔
      (S r ∧ wellFormed r ∧ ∀ p, parent p r → kept parent wf wellFormed S p) := by
  have h := adm_iff (WellFounded.transGen wf) (doorJudge parent wellFormed) S r
  exact h.trans
    ⟨fun ⟨a, b, c⟩ => ⟨a, b, fun p hp => (c p hp).2⟩,
     fun ⟨a, b, c⟩ => ⟨a, b, fun p hp => ⟨TransGen.single hp, c p hp⟩⟩⟩

theorem kept_offered (S : Row → Prop) (r : Row) (h : kept parent wf wellFormed S r) : S r :=
  ((kept_iff parent wf wellFormed S r).1 h).1

/-- A kept row has every ancestor kept: the kept set has no holes. -/
theorem kept_ancestors (S : Row → Prop) (p r : Row) (h : TransGen parent p r) :
    kept parent wf wellFormed S r → kept parent wf wellFormed S p := by
  induction h with
  | single h => exact fun hk => ((kept_iff parent wf wellFormed S _).1 hk).2.2 p h
  | tail _ h ih => exact fun hk => ih (((kept_iff parent wf wellFormed S _).1 hk).2.2 _ h)

/-- T6 (i), function. The kept set depends on the offered set only. -/
theorem kept_function (S S' : Row → Prop) (h : ∀ r, S r ↔ S' r) :
    kept parent wf wellFormed S = kept parent wf wellFormed S' :=
  adm_congr _ _ S S' h

/-- T6 (i), monotone. Offering more never removes a row from the kept set. -/
theorem kept_mono (S S' : Row → Prop) (h : ∀ r, S r → S' r) :
    ∀ r, kept parent wf wellFormed S r → kept parent wf wellFormed S' r := by
  intro r
  induction r using WellFounded.induction wf with | _ r ih => ?_
  intro hk
  have ⟨a, b, c⟩ := (kept_iff parent wf wellFormed S r).1 hk
  exact (kept_iff parent wf wellFormed S' r).2 ⟨h r a, b, fun p hp => ih p hp (c p hp)⟩

/-- If the offered set is well-formed and has no holes, all of it is kept. -/
theorem kept_of_closed (S : Row → Prop) (hw : ∀ r, S r → wellFormed r)
    (hcl : ∀ p r, parent p r → S r → S p) :
    ∀ r, S r → kept parent wf wellFormed S r := by
  intro r
  induction r using WellFounded.induction wf with | _ r ih => ?_
  intro hS
  exact (kept_iff parent wf wellFormed S r).2
    ⟨hS, hw r hS, fun p hp => ih p hp (hcl p r hp hS)⟩

theorem door_mono : ∀ r (A B : Row → Prop), (∀ q, A q → B q) →
    doorJudge parent wellFormed r A → doorJudge parent wellFormed r B :=
  fun _ _ _ hAB ⟨a, b⟩ => ⟨a, fun p hp => hAB p (b p hp)⟩

/-- T6 (i), least fixed point. The kept set is the least set closed under the door. -/
theorem kept_is_least (S : Row → Prop) :
    ∀ r, least S (doorJudge parent wellFormed) r ↔ kept parent wf wellFormed S r := by
  intro r
  constructor
  · intro hl
    apply hl
    intro q hS ⟨hw, hp⟩
    exact (kept_iff parent wf wellFormed S q).2 ⟨hS, hw, hp⟩
  · induction r using WellFounded.induction wf with | _ r ih => ?_
    intro hk A hA
    have ⟨a, b, c⟩ := (kept_iff parent wf wellFormed S r).1 hk
    exact hA r a ⟨b, fun p hp => ih p hp (c p hp) A hA⟩

/-- T6 (i), any arrival order with waiting. Rows arrive in any order; a row whose parents are
    not yet kept waits and is tried again. `Reach` is every such path. Once no waiting row can
    enter (`Closed`), the set kept is the kept set of the offered set. -/
theorem door_any_order (S A : Row → Prop)
    (hrun : Reach S (doorJudge parent wellFormed) A)
    (hsat : Closed S (doorJudge parent wellFormed) A) :
    ∀ r, A r ↔ kept parent wf wellFormed S r :=
  fun r => (saturated_is_least S _ (door_mono parent wellFormed) A hrun hsat r).trans
    (kept_is_least parent wf wellFormed S r)

/-- Offering one more row `x` changes whether `r` is kept only if `r` is `x` or a descendant
    of `x`. -/
theorem kept_new_row (S : Row → Prop) (x r : Row) (hne : r ≠ x) (hnd : ¬ TransGen parent x r) :
    kept parent wf wellFormed S r ↔ kept parent wf wellFormed (fun q => S q ∨ q = x) r :=
  late_row_keeps _ _ (fun _ _ _ => anc_trans) S x r hne hnd

/-- A row offered later is not an ancestor of any row kept before it. -/
theorem new_row_not_ancestor (S : Row → Prop) (x r : Row)
    (hk : kept parent wf wellFormed S r) (hx : ¬ S x) : r ≠ x ∧ ¬ TransGen parent x r :=
  ⟨fun e => hx (e ▸ kept_offered parent wf wellFormed S r hk),
   fun h => hx (kept_offered parent wf wellFormed S x
     (kept_ancestors parent wf wellFormed S x r h hk))⟩

end Door

/-! ## Part B. The door on finite lists: executable, and it terminates -/

section FiniteDoor

variable {Row : Type} [DecidableEq Row]
variable (parents : Row → List Row) (wfB : Row → Bool)

/-- May `r` enter, given the rows kept so far? -/
def okB (r : Row) (acc : List Row) : Bool :=
  wfB r && (parents r).all (fun p => decide (p ∈ acc))

/-- A waiting row that may now enter. -/
def cand (acc : List Row) (r : Row) : Bool := !decide (r ∈ acc) && okB parents wfB r acc

/-- Let waiting rows in one at a time, for at most `n` steps. -/
def close (l : List Row) : Nat → List Row → List Row
  | 0, acc => acc
  | n + 1, acc =>
    match l.find? (cand parents wfB acc) with
    | none => acc
    | some r => close l n (acc ++ [r])

/-- The door on a finite list of offered rows. One step per offered row is enough. -/
def door (l : List Row) : List Row := close parents wfB l l.length []

theorem okB_iff (r : Row) (acc : List Row) :
    okB parents wfB r acc = true ↔
      doorJudge (fun p r => p ∈ parents r) (fun r => wfB r = true) r (fun q => q ∈ acc) := by
  simp [okB, doorJudge, List.all_eq_true]

omit [DecidableEq Row] in
theorem filter_length_le (p q : Row → Bool) (himp : ∀ x, p x = true → q x = true) :
    ∀ l : List Row, (l.filter p).length ≤ (l.filter q).length
  | [] => Nat.le_refl _
  | x :: xs => by
    have ih := filter_length_le p q himp xs
    rw [List.filter_cons, List.filter_cons]
    cases hp : p x with
    | false =>
      cases hq : q x with
      | false => simpa using ih
      | true => simp; omega
    | true => simp [himp x hp]; omega

omit [DecidableEq Row] in
theorem filter_length_lt (p q : Row → Bool) (himp : ∀ x, p x = true → q x = true) (r : Row)
    (hq : q r = true) (hp : p r = false) :
    ∀ l : List Row, r ∈ l → (l.filter p).length < (l.filter q).length
  | x :: xs, hm => by
    have hle := filter_length_le p q himp xs
    rw [List.filter_cons, List.filter_cons]
    cases List.mem_cons.1 hm with
    | inl e =>
      rw [← e, hp, hq]
      simp; omega
    | inr m =>
      have ih := filter_length_lt p q himp r hq hp xs m
      cases hpx : p x with
      | false =>
        cases hqx : q x with
        | false => simpa using ih
        | true => simp; omega
      | true => simp [himp x hpx]; omega

/-- Rows offered and not yet kept. Each step that lets a row in makes this shorter. -/
def waiting (l acc : List Row) : List Row := l.filter (fun r => !decide (r ∈ acc))

/-- Termination. If at most `n` offered rows are still outside, then after `n` steps no
    waiting row can enter. -/
theorem close_saturated (l : List Row) : ∀ (n : Nat) (acc : List Row),
    (waiting l acc).length ≤ n →
    l.find? (cand parents wfB (close parents wfB l n acc)) = none := by
  intro n
  induction n with
  | zero =>
    intro acc h
    rw [List.find?_eq_none]
    intro x hx hc
    have hin : x ∈ waiting l acc := by
      simp only [waiting, List.mem_filter]
      simp only [cand, Bool.and_eq_true] at hc
      exact ⟨hx, hc.1⟩
    have h0 : waiting l acc = [] := List.eq_nil_of_length_eq_zero (Nat.le_zero.1 h)
    rw [h0] at hin
    exact nomatch hin
  | succ n ih =>
    intro acc h
    simp only [close]
    split
    · rename_i hnone
      exact hnone
    · rename_i r hsome
      apply ih
      have hr : cand parents wfB acc r = true := List.find?_some hsome
      have hmem : r ∈ l := List.mem_of_find?_eq_some hsome
      simp only [cand, Bool.and_eq_true, Bool.not_eq_true', decide_eq_false_iff_not] at hr
      have hlt : (waiting l (acc ++ [r])).length < (waiting l acc).length := by
        apply filter_length_lt _ _ _ r _ _ l hmem
        · intro x hx
          simp only [Bool.not_eq_true', decide_eq_false_iff_not, List.mem_append,
            List.mem_singleton] at hx ⊢
          exact fun hm => hx (Or.inl hm)
        · simp only [Bool.not_eq_true', decide_eq_false_iff_not]
          exact hr.1
        · simp
      omega

/-- Every step of the executable door is a step of the abstract door. -/
theorem close_reach (l : List Row) : ∀ (n : Nat) (acc : List Row),
    Reach (fun r => r ∈ l) (doorJudge (fun p r => p ∈ parents r) (fun r => wfB r = true))
      (fun q => q ∈ acc) →
    Reach (fun r => r ∈ l) (doorJudge (fun p r => p ∈ parents r) (fun r => wfB r = true))
      (fun q => q ∈ close parents wfB l n acc) := by
  intro n
  induction n with
  | zero => intro acc h; exact h
  | succ n ih =>
    intro acc h
    simp only [close]
    split
    · exact h
    · rename_i r hsome
      apply ih
      have hr : cand parents wfB acc r = true := List.find?_some hsome
      have hmem : r ∈ l := List.mem_of_find?_eq_some hsome
      simp only [cand, Bool.and_eq_true] at hr
      have hstep := Reach.step (S := fun r => r ∈ l) (fun q => q ∈ acc) r h hmem
        ((okB_iff parents wfB r acc).1 hr.2)
      have e : (fun q => q ∈ acc ++ [r]) = (fun q => q ∈ acc ∨ q = r) := by
        funext q; simp
      rw [e]
      exact hstep

theorem door_reach (l : List Row) :
    Reach (fun r => r ∈ l) (doorJudge (fun p r => p ∈ parents r) (fun r => wfB r = true))
      (fun q => q ∈ door parents wfB l) := by
  apply close_reach
  have e : (fun q : Row => q ∈ ([] : List Row)) = (fun _ => False) := by funext q; simp
  rw [e]
  exact Reach.empty

theorem door_closed (l : List Row) :
    Closed (fun r => r ∈ l) (doorJudge (fun p r => p ∈ parents r) (fun r => wfB r = true))
      (fun q => q ∈ door parents wfB l) := by
  intro r hr hj
  have hsat := close_saturated parents wfB l l.length []
    (List.length_filter_le _ l)
  rw [List.find?_eq_none] at hsat
  have hnc := hsat r hr
  have hok := (okB_iff parents wfB r (door parents wfB l)).2 hj
  cases hd : decide (r ∈ door parents wfB l) with
  | true => exact of_decide_eq_true hd
  | false =>
    exact absurd (by simp only [cand, door, Bool.and_eq_true] at hd ⊢; simp [hd]; exact hok) hnc

/-- T6 (i) on finite lists. The executable door stops, and what it holds when it stops is the
    kept set of the offered rows. -/
theorem door_spec (wf : WellFounded (fun p r : Row => p ∈ parents r)) (l : List Row) :
    ∀ x, x ∈ door parents wfB l ↔
      kept (fun p r => p ∈ parents r) wf (fun r => wfB r = true) (fun r => r ∈ l) x :=
  door_any_order _ wf _ _ _ (door_reach parents wfB l) (door_closed parents wfB l)

/-- T6 (i) on finite lists, arrival order. Two lists with the same members give the same kept
    rows. This needs nothing about the parent relation: the closure is monotone. -/
theorem door_same_members (l l' : List Row) (h : ∀ r, r ∈ l ↔ r ∈ l') :
    ∀ x, x ∈ door parents wfB l ↔ x ∈ door parents wfB l' := by
  have e : (fun r => r ∈ l) = (fun r => r ∈ l') := funext fun r => propext (h r)
  have h1 := door_reach parents wfB l
  have h2 := door_closed parents wfB l
  rw [e] at h1 h2
  exact saturated_agree _ _ (door_mono _ _) _ _ h1 h2
    (door_reach parents wfB l') (door_closed parents wfB l')

theorem door_perm (l l' : List Row) (h : l.Perm l') :
    ∀ x, x ∈ door parents wfB l ↔ x ∈ door parents wfB l' :=
  door_same_members parents wfB l l' (fun _ => h.mem_iff)

end FiniteDoor

/-! ## Part C. Conclusions: recursion on ancestry, a seed, and a symmetric view of concurrency -/

section Conclusions

variable {Row : Type}
variable (parent : Row → Row → Prop) (wf : WellFounded parent)

/-- Concurrent: neither is an ancestor of the other, and they are two rows. -/
def conc (q r : Row) : Prop :=
  ¬ TransGen parent q r ∧ ¬ TransGen parent r q ∧ q ≠ r

/- The rule. `judge r P C`: `P` is the set of ancestors of `r` already concluded; `C` is the
   set of live rows concurrent with `r`. The rule may negate and count over both. It is given
   the concurrent rows as a set, with no order among them, and it is not given their
   conclusions. -/
variable (judge : Row → (Row → Prop) → (Row → Prop) → Prop)

/-- The conclusion over a set `L` of live rows, by recursion on ancestry. -/
noncomputable def conclOf (L : Row → Prop) : Row → Prop :=
  adm (TransGen parent) (WellFounded.transGen wf)
    (fun r P => judge r P (fun q => L q ∧ conc parent q r)) L

theorem conclOf_iff (L : Row → Prop) (r : Row) :
    conclOf parent wf judge L r ↔
      (L r ∧ judge r (fun q => TransGen parent q r ∧ conclOf parent wf judge L q)
        (fun q => L q ∧ conc parent q r)) :=
  adm_iff _ _ L r

/-- The conclusion is the only solution of its equation, whatever the rule. -/
theorem conclOf_unique (L A : Row → Prop)
    (hA : ∀ r, A r ↔ (L r ∧ judge r (fun q => TransGen parent q r ∧ A q)
      (fun q => L q ∧ conc parent q r))) :
    ∀ r, A r ↔ conclOf parent wf judge L r :=
  adm_unique _ _ L A hA

/-- Locality, general form. `conflict y q` names the concurrent rows the rule for `q` reads:
    the rule depends on its concurrent set only at rows in conflict with `q` (`hC`). Let two
    live sets differ only inside `D`. Then the conclusion about `r` is the same under both,
    provided neither `r` nor any ancestor of `r` is in `D` or in concurrent conflict with a
    row of `D`. -/
theorem conclOf_local (conflict : Row → Row → Prop)
    (hC : ∀ r P (C C' : Row → Prop), (∀ y, conflict y r → (C y ↔ C' y)) →
      (judge r P C ↔ judge r P C'))
    (L L' D : Row → Prop) (hD : ∀ q, ¬ D q → (L q ↔ L' q)) (r : Row)
    (hr : ∀ q, (q = r ∨ TransGen parent q r) →
      ¬ D q ∧ ∀ y, D y → conflict y q → ¬ conc parent y q) :
    conclOf parent wf judge L r ↔ conclOf parent wf judge L' r := by
  induction r using WellFounded.induction (WellFounded.transGen wf) with | _ r ih => ?_
  have e : (fun q => TransGen parent q r ∧ conclOf parent wf judge L q)
      = (fun q => TransGen parent q r ∧ conclOf parent wf judge L' q) :=
    funext fun q => propext
      ⟨fun ⟨hq, a⟩ => ⟨hq, (ih q hq (fun p hp => hr p (Or.inr
          (hp.elim (fun e => e ▸ hq) (fun hpq => anc_trans hpq hq))))).1 a⟩,
       fun ⟨hq, a⟩ => ⟨hq, (ih q hq (fun p hp => hr p (Or.inr
          (hp.elim (fun e => e ▸ hq) (fun hpq => anc_trans hpq hq))))).2 a⟩⟩
  have hrr := hr r (Or.inl rfl)
  have hL : L r ↔ L' r := hD r hrr.1
  have hJ : ∀ P, judge r P (fun q => L q ∧ conc parent q r) ↔
      judge r P (fun q => L' q ∧ conc parent q r) :=
    fun P => hC r P _ _ (fun y hy =>
      ⟨fun ⟨a, b⟩ => ⟨(hD y (fun hDy => hrr.2 y hDy hy b)).1 a, b⟩,
       fun ⟨a, b⟩ => ⟨(hD y (fun hDy => hrr.2 y hDy hy b)).2 a, b⟩⟩)
  have h1 := conclOf_iff parent wf judge L r
  have h2 := conclOf_iff parent wf judge L' r
  rw [e] at h1
  exact h1.trans
    ⟨fun ⟨a, b⟩ => h2.2 ⟨hL.1 a, (hJ _).1 b⟩,
     fun h => ⟨hL.2 (h2.1 h).1, (hJ _).2 (h2.1 h).2⟩⟩

variable (wellFormed : Row → Prop)

/-- The seed. `root` is the set of rows the reader takes as its own starting points. A row is
    live when it is kept and a root is at or above it. -/
def Live (root : Row → Prop) (S : Row → Prop) (r : Row) : Prop :=
  kept parent wf wellFormed S r ∧ (root r ∨ ∃ q, root q ∧ TransGen parent q r)

/-- The conclusion for seed `root` and offered set `S`. -/
noncomputable def concl (root : Row → Prop) (S : Row → Prop) : Row → Prop :=
  conclOf parent wf judge (Live parent wf wellFormed root S)

/-- T6 (ii). The conclusion is a function of the kept set (and the seed). -/
theorem concl_of_kept (root : Row → Prop) (S S' : Row → Prop)
    (h : ∀ r, kept parent wf wellFormed S r ↔ kept parent wf wellFormed S' r) :
    concl parent wf judge wellFormed root S = concl parent wf judge wellFormed root S' := by
  have e : Live parent wf wellFormed root S = Live parent wf wellFormed root S' :=
    funext fun r => propext ⟨fun ⟨a, b⟩ => ⟨(h r).1 a, b⟩, fun ⟨a, b⟩ => ⟨(h r).2 a, b⟩⟩
  rw [concl, concl, e]

/-- T6 (i)+(ii). So the conclusion is a function of the offered set and the seed. -/
theorem concl_function (root root' : Row → Prop) (S S' : Row → Prop)
    (hS : ∀ r, S r ↔ S' r) (hR : ∀ r, root r ↔ root' r) :
    concl parent wf judge wellFormed root S = concl parent wf judge wellFormed root' S' := by
  have e1 : S = S' := funext fun r => propext (hS r)
  have e2 : root = root' := funext fun r => propext (hR r)
  rw [e1, e2]

theorem concl_live (root S : Row → Prop) (r : Row)
    (h : concl parent wf judge wellFormed root S r) : Live parent wf wellFormed root S r :=
  ((conclOf_iff parent wf judge _ r).1 h).1

/-- T6 (v). A row with no root at or above it concludes nothing, kept or not. -/
theorem unrooted_concludes_nothing (root S : Row → Prop) (r : Row)
    (h0 : ¬ root r) (h1 : ∀ q, root q → ¬ TransGen parent q r) :
    ¬ concl parent wf judge wellFormed root S r := by
  intro h
  cases (concl_live parent wf judge wellFormed root S r h).2 with
  | inl h => exact h0 h
  | inr h => exact h.elim fun q hq => h1 q hq.1 hq.2

variable (conflict : Row → Row → Prop)
variable (hC : ∀ r P (C C' : Row → Prop), (∀ y, conflict y r → (C y ↔ C' y)) →
      (judge r P C ↔ judge r P C'))
include hC

/-- T6 (iii). Offering one more row `x` leaves the conclusion about `r` as it was, provided
    `r` is not `x`, `r` is not a descendant of `x`, and neither `r` nor an ancestor of `r` is
    in concurrent conflict with `x` or with a descendant of `x`. -/
theorem concl_new_row (root S : Row → Prop) (x r : Row)
    (hne : r ≠ x) (hnd : ¬ TransGen parent x r)
    (hfar : ∀ q, (q = r ∨ TransGen parent q r) → ∀ y, (y = x ∨ TransGen parent x y) →
      conflict y q → ¬ conc parent y q) :
    concl parent wf judge wellFormed root S r ↔
      concl parent wf judge wellFormed root (fun q => S q ∨ q = x) r := by
  apply conclOf_local parent wf judge conflict hC _ _ (fun q => q = x ∨ TransGen parent x q)
  · intro q hq
    have hk := kept_new_row parent wf wellFormed S x q
      (fun e => hq (Or.inl e)) (fun h => hq (Or.inr h))
    exact ⟨fun ⟨a, b⟩ => ⟨hk.1 a, b⟩, fun ⟨a, b⟩ => ⟨hk.2 a, b⟩⟩
  · intro q hq
    refine ⟨?_, hfar q hq⟩
    intro hD
    cases hq with
    | inl e =>
      cases hD with
      | inl e' => exact hne (e ▸ e')
      | inr h => exact hnd (e ▸ h)
    | inr hqr =>
      cases hD with
      | inl e' => exact hnd (e' ▸ hqr)
      | inr h => exact hnd (anc_trans h hqr)

/-- T6 (v), locality of the seed. Adding one row `y` to the seed leaves the conclusion about
    `r` as it was under the same three conditions, with `y` in place of the new row. Nothing is
    offered again: the offered set `S` is the same on both sides. -/
theorem concl_new_root (root S : Row → Prop) (y r : Row)
    (hne : r ≠ y) (hnd : ¬ TransGen parent y r)
    (hfar : ∀ q, (q = r ∨ TransGen parent q r) → ∀ z, (z = y ∨ TransGen parent y z) →
      conflict z q → ¬ conc parent z q) :
    concl parent wf judge wellFormed root S r ↔
      concl parent wf judge wellFormed (fun q => root q ∨ q = y) S r := by
  apply conclOf_local parent wf judge conflict hC _ _ (fun q => q = y ∨ TransGen parent y q)
  · intro q hq
    constructor
    · intro ⟨a, b⟩
      exact ⟨a, b.elim (fun h => Or.inl (Or.inl h)) (fun ⟨p, hp, hpq⟩ => Or.inr ⟨p, Or.inl hp, hpq⟩)⟩
    · intro ⟨a, b⟩
      refine ⟨a, ?_⟩
      cases b with
      | inl h =>
        cases h with
        | inl h => exact Or.inl h
        | inr e => exact absurd (Or.inl e) hq
      | inr h =>
        have ⟨p, hp, hpq⟩ := h
        cases hp with
        | inl hp => exact Or.inr ⟨p, hp, hpq⟩
        | inr e => exact absurd (Or.inr (e ▸ hpq)) hq
  · intro q hq
    refine ⟨?_, hfar q hq⟩
    intro hD
    cases hq with
    | inl e =>
      cases hD with
      | inl e' => exact hne (e ▸ e')
      | inr h => exact hnd (e ▸ h)
    | inr hqr =>
      cases hD with
      | inl e' => exact hnd (e' ▸ hqr)
      | inr h => exact hnd (anc_trans h hqr)

/-- T6 (iii) for conclusions about several rows (a slot, a count). `D` reads the per-row
    conclusions only on its parties `T`. Offering `x` leaves `D` as it was when every party
    meets the conditions of `concl_new_row`. -/
theorem derived_new_row (root S : Row → Prop) (x : Row)
    (D : (Row → Prop) → Prop) (T : Row → Prop)
    (hD : ∀ A B : Row → Prop, (∀ r, T r → (A r ↔ B r)) → (D A ↔ D B))
    (hT : ∀ r, T r → r ≠ x ∧ ¬ TransGen parent x r ∧
      ∀ q, (q = r ∨ TransGen parent q r) → ∀ y, (y = x ∨ TransGen parent x y) →
        conflict y q → ¬ conc parent y q) :
    D (concl parent wf judge wellFormed root S) ↔
      D (concl parent wf judge wellFormed root (fun q => S q ∨ q = x)) :=
  hD _ _ (fun r hr => concl_new_row parent wf judge wellFormed conflict hC root S x r
    (hT r hr).1 (hT r hr).2.1 (hT r hr).2.2)

omit hC

/-- T6 (iii), finality when the rule reads no concurrent row. Then once a row is kept, no row
    offered later changes the conclusion about it. A rule that does read concurrent rows gives
    this up: see `concl_new_row`. -/
theorem concl_final
    (hC0 : ∀ r P (C C' : Row → Prop), judge r P C ↔ judge r P C')
    (root S : Row → Prop) (x r : Row)
    (hk : kept parent wf wellFormed S r) (hx : ¬ S x) :
    concl parent wf judge wellFormed root S r ↔
      concl parent wf judge wellFormed root (fun q => S q ∨ q = x) r :=
  concl_new_row parent wf judge wellFormed (fun _ _ => False) (fun r P C C' _ => hC0 r P C C')
    root S x r
    (new_row_not_ancestor parent wf wellFormed S x r hk hx).1
    (new_row_not_ancestor parent wf wellFormed S x r hk hx).2
    (fun _ _ _ _ h => h.elim)

end Conclusions

/-! ## Part D. T7: symmetry, and what it costs -/

section Symmetry

variable {Row : Type}

/-- A relabelling `σ` that keeps the order carries one kernel's verdicts to another's, when the
    two rules and the two offered sets correspond under `σ`. -/
theorem adm_equiv {below : Row → Row → Prop} (wf : WellFounded below)
    (judge judge' : Row → (Row → Prop) → Prop) (σ : Row → Row)
    (hb : ∀ q r, below (σ q) (σ r) ↔ below q r)
    (hj : ∀ r P, judge (σ r) P ↔ judge' r (fun q => P (σ q)))
    (S S' : Row → Prop) (hS : ∀ r, S' r ↔ S (σ r)) :
    ∀ r, adm below wf judge' S' r ↔ adm below wf judge S (σ r) := by
  intro r
  induction r using WellFounded.induction wf with | _ r ih => ?_
  have h1 := adm_iff wf judge' S' r
  have h2 := adm_iff wf judge S (σ r)
  have h3 := hj r (fun q => below q (σ r) ∧ adm below wf judge S q)
  have e : (fun q => below q r ∧ adm below wf judge' S' q)
      = (fun q => below (σ q) (σ r) ∧ adm below wf judge S (σ q)) :=
    funext fun q => propext
      ⟨fun ⟨hq, a⟩ => ⟨(hb q r).2 hq, (ih q hq).1 a⟩,
       fun ⟨hq, a⟩ => ⟨(hb q r).1 hq, (ih q ((hb q r).1 hq)).2 a⟩⟩
  rw [e] at h1
  exact h1.trans
    ⟨fun ⟨a, b⟩ => h2.2 ⟨(hS r).1 a, h3.2 b⟩,
     fun h => ⟨(hS r).2 (h2.1 h).1, h3.1 (h2.1 h).2⟩⟩

variable (parent : Row → Row → Prop) (wf : WellFounded parent)
variable (σ : Row → Row) (hσ : ∀ x, σ (σ x) = x)
variable (hp : ∀ p r, parent (σ p) (σ r) ↔ parent p r)
include hσ hp

/-- The swap keeps ancestry. -/
theorem anc_swap (q r : Row) : TransGen parent (σ q) (σ r) ↔ TransGen parent q r := by
  have fwd : ∀ a b, TransGen parent a b → TransGen parent (σ a) (σ b) := by
    intro a b h
    induction h with
    | single h => exact TransGen.single ((hp _ _).2 h)
    | tail _ h ih => exact TransGen.tail ih ((hp _ _).2 h)
  constructor
  · intro h
    have := fwd _ _ h
    rw [hσ, hσ] at this
    exact this
  · exact fwd q r

/-- The swap keeps concurrency. -/
theorem conc_swap (q r : Row) : conc parent (σ q) (σ r) ↔ conc parent q r := by
  have hinj : σ q = σ r ↔ q = r :=
    ⟨fun h => by have := congrArg σ h; rw [hσ, hσ] at this; exact this, fun h => by rw [h]⟩
  unfold conc
  rw [anc_swap parent σ hσ hp q r, anc_swap parent σ hσ hp r q]
  exact ⟨fun ⟨a, b, c⟩ => ⟨a, b, fun e => c (hinj.2 e)⟩, fun ⟨a, b, c⟩ => ⟨a, b, fun e => c (hinj.1 e)⟩⟩

variable (wellFormed : Row → Prop) (hw : ∀ r, wellFormed (σ r) ↔ wellFormed r)
include hw

/-- The door treats swapped rows alike. -/
theorem kept_swap (S : Row → Prop) (r : Row) :
    kept parent wf wellFormed (fun x => S (σ x)) r ↔ kept parent wf wellFormed S (σ r) := by
  apply adm_equiv (WellFounded.transGen wf) _ _ σ (anc_swap parent σ hσ hp)
  · intro r P
    constructor
    · intro ⟨a, b⟩
      exact ⟨(hw r).1 a, fun p h => b (σ p) ((hp p r).2 h)⟩
    · intro ⟨a, b⟩
      refine ⟨(hw r).2 a, fun p h => ?_⟩
      have h' : parent (σ p) r := by
        have := (hp (σ p) r).1 (by rw [hσ]; exact h)
        exact this
      have := b (σ p) h'
      simp only [hσ] at this
      exact this
  · intro r; exact Iff.rfl

variable (judge : Row → (Row → Prop) → (Row → Prop) → Prop)
variable (hj : ∀ r P C, judge (σ r) P C ↔ judge r (fun q => P (σ q)) (fun q => C (σ q)))
variable (root : Row → Prop) (hroot : ∀ r, root (σ r) ↔ root r)
include hj hroot

/-- A symmetric rule gives symmetric conclusions: swapping the offered rows swaps the
    conclusions. -/
theorem concl_swap (S : Row → Prop) (r : Row) :
    concl parent wf judge wellFormed root (fun x => S (σ x)) r ↔
      concl parent wf judge wellFormed root S (σ r) := by
  have hL : ∀ r, Live parent wf wellFormed root (fun x => S (σ x)) r ↔
      Live parent wf wellFormed root S (σ r) := by
    intro r
    have hk := kept_swap parent wf σ hσ hp wellFormed hw S r
    constructor
    · intro ⟨a, b⟩
      refine ⟨hk.1 a, ?_⟩
      cases b with
      | inl h => exact Or.inl ((hroot r).2 h)
      | inr h =>
        have ⟨q, hq, hqr⟩ := h
        exact Or.inr ⟨σ q, (hroot q).2 hq, (anc_swap parent σ hσ hp q r).2 hqr⟩
    · intro ⟨a, b⟩
      refine ⟨hk.2 a, ?_⟩
      cases b with
      | inl h => exact Or.inl ((hroot r).1 h)
      | inr h =>
        have ⟨q, hq, hqr⟩ := h
        refine Or.inr ⟨σ q, (hroot q).2 hq, ?_⟩
        have := (anc_swap parent σ hσ hp (σ q) r).1 (by rw [hσ]; exact hqr)
        exact this
  refine adm_equiv (WellFounded.transGen wf)
    (fun r P => judge r P (fun q => Live parent wf wellFormed root S q ∧ conc parent q r))
    (fun r P => judge r P
      (fun q => Live parent wf wellFormed root (fun x => S (σ x)) q ∧ conc parent q r))
    σ (anc_swap parent σ hσ hp) ?_ _ _ hL r
  intro r P
  show judge (σ r) P (fun q => Live parent wf wellFormed root S q ∧ conc parent q (σ r)) ↔
    judge r (fun q => P (σ q))
      (fun q => Live parent wf wellFormed root (fun x => S (σ x)) q ∧ conc parent q r)
  have e : (fun q => Live parent wf wellFormed root (fun x => S (σ x)) q ∧ conc parent q r)
      = (fun q => Live parent wf wellFormed root S (σ q) ∧ conc parent (σ q) (σ r)) :=
    funext fun q => propext
      ⟨fun ⟨a, b⟩ => ⟨(hL q).1 a, (conc_swap parent σ hσ hp q r).2 b⟩,
       fun ⟨a, b⟩ => ⟨(hL q).2 a, (conc_swap parent σ hσ hp q r).1 b⟩⟩
  rw [e]
  exact hj r P _

/-- T7. Two rows swapped by `σ`, an offered set the swap leaves unchanged, a symmetric rule:
    the kernel concludes both or neither. From `Order.no_symmetric_choice`. -/
theorem contested_both_or_neither (S : Row → Prop) (hS : ∀ x, S (σ x) ↔ S x) (a : Row) :
    ¬ ((concl parent wf judge wellFormed root S a ∧
          ¬ concl parent wf judge wellFormed root S (σ a)) ∨
       (¬ concl parent wf judge wellFormed root S a ∧
          concl parent wf judge wellFormed root S (σ a))) :=
  no_symmetric_choice (fun S => concl parent wf judge wellFormed root S) σ
    (fun S r => concl_swap parent wf σ hσ hp wellFormed hw judge hj root hroot S r) S hS a

/-- T7, for any holder rule built on the conclusions. `H A x` says x holds the slot given the
    conclusions `A`. If `H` treats swapped rows alike, it names both or neither. One holder
    therefore needs a fact that the swap does not preserve: a row outside the two. -/
theorem holder_both_or_neither (H : (Row → Prop) → Row → Prop)
    (hH : ∀ A x, H (fun y => A (σ y)) x ↔ H A (σ x))
    (S : Row → Prop) (hS : ∀ x, S (σ x) ↔ S x) (a : Row) :
    ¬ ((H (concl parent wf judge wellFormed root S) a ∧
          ¬ H (concl parent wf judge wellFormed root S) (σ a)) ∨
       (¬ H (concl parent wf judge wellFormed root S) a ∧
          H (concl parent wf judge wellFormed root S) (σ a))) := by
  apply no_symmetric_choice (fun S => H (concl parent wf judge wellFormed root S)) σ _ S hS a
  intro S r
  have e : concl parent wf judge wellFormed root (fun x => S (σ x))
      = (fun y => concl parent wf judge wellFormed root S (σ y)) :=
    funext fun y => propext
      (concl_swap parent wf σ hσ hp wellFormed hw judge hj root hroot S y)
  show H (concl parent wf judge wellFormed root (fun x => S (σ x))) r ↔ _
  rw [e]
  exact hH _ r

end Symmetry

/-! ## Part E. An instance: a contested slot, a deciding descendant, and a seed -/

namespace Slot

/-- `g` is a genesis row. `a` and `b` each name `g` and claim the same slot; they are
    concurrent. `c` and `d` each name both `a` and `b`; `c` decides for `a`, `d` for `b`.
    No row carries a rank. -/
inductive R | g | a | b | c | d
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | g, a => true | g, b => true
  | a, c => true | b, c => true
  | a, d => true | b, d => true
  | _, _ => false

def parent (p r : R) : Prop := parentB p r = true

def depth : R → Nat
  | g => 0 | a => 1 | b => 1 | c => 2 | d => 2

theorem parent_depth : ∀ p r, parent p r → depth p < depth r := by
  intro p r
  cases p <;> cases r <;> simp [parent, parentB, depth]

/-- The hash-link hypothesis holds here. -/
theorem parent_wf : WellFounded parent :=
  Subrelation.wf (fun {p r} h => parent_depth p r h) (InvImage.wf depth Nat.lt_wfRel.wf)

theorem anc_depth {p r : R} (h : TransGen parent p r) : depth p < depth r := by
  induction h with
  | single h => exact parent_depth _ _ h
  | tail _ h ih => exact Nat.lt_trans ih (parent_depth _ _ h)

/-- The rule. A claim is denied while a concurrent claim is live. A deciding row is denied
    while a concurrent deciding row is live. Symmetric under swapping a with b and c with d. -/
def judge : R → (R → Prop) → (R → Prop) → Prop
  | g, _, _ => True
  | a, _, C => ¬ C b
  | b, _, C => ¬ C a
  | c, _, C => ¬ C d
  | d, _, C => ¬ C c

/-- The holder of the slot: a concluded claim, or the claim a concluded deciding row names. -/
def holder (A : R → Prop) (x : R) : Prop :=
  A x ∨ (x = a ∧ A c) ∨ (x = b ∧ A d)

def seed (r : R) : Prop := r = g
def noSeed (_ : R) : Prop := False

def S2b : R → Bool | g => true | a => true | b => true | _ => false
def S3b : R → Bool | d => false | _ => true
abbrev S2 (r : R) : Prop := S2b r = true     -- g, a, b
abbrev S3 (r : R) : Prop := S3b r = true     -- g, a, b, c
def S4 (_ : R) : Prop := True             -- g, a, b, c, d

theorem S2_closed : ∀ p r, parent p r → S2 r → S2 p := by
  intro p r; cases p <;> cases r <;> simp [parent, parentB, S2, S2b]
theorem S3_closed : ∀ p r, parent p r → S3 r → S3 p := by
  intro p r; cases p <;> cases r <;> simp [parent, parentB, S3, S3b]
theorem S4_closed : ∀ p r, parent p r → S4 r → S4 p := fun _ _ _ _ => trivial

abbrev K (root S : R → Prop) : R → Prop := concl parent parent_wf judge (fun _ => True) root S
abbrev Kept (S : R → Prop) : R → Prop := kept parent parent_wf (fun _ => True) S
abbrev L (root S : R → Prop) : R → Prop := Live parent parent_wf (fun _ => True) root S

theorem rooted : ∀ r, seed r ∨ ∃ q, seed q ∧ TransGen parent q r := by
  intro r
  cases r with
  | g => exact Or.inl rfl
  | a => exact Or.inr ⟨g, rfl, TransGen.single rfl⟩
  | b => exact Or.inr ⟨g, rfl, TransGen.single rfl⟩
  | c => exact Or.inr ⟨g, rfl, TransGen.tail (TransGen.single (b := a) rfl) rfl⟩
  | d => exact Or.inr ⟨g, rfl, TransGen.tail (TransGen.single (b := a) rfl) rfl⟩

theorem live (S : R → Prop) (hcl : ∀ p r, parent p r → S r → S p) (r : R) (h : S r) :
    L seed S r :=
  ⟨kept_of_closed parent parent_wf _ S (fun _ _ => trivial) hcl r h, rooted r⟩

theorem conc_ab : conc parent a b ∧ conc parent b a :=
  ⟨⟨fun h => absurd (anc_depth h) (by decide), fun h => absurd (anc_depth h) (by decide),
      by decide⟩,
   ⟨fun h => absurd (anc_depth h) (by decide), fun h => absurd (anc_depth h) (by decide),
      by decide⟩⟩

theorem conc_cd : conc parent c d ∧ conc parent d c :=
  ⟨⟨fun h => absurd (anc_depth h) (by decide), fun h => absurd (anc_depth h) (by decide),
      by decide⟩,
   ⟨fun h => absurd (anc_depth h) (by decide), fun h => absurd (anc_depth h) (by decide),
      by decide⟩⟩

/-- Whenever both claims are offered, each is denied. -/
theorem claims_denied (S : R → Prop) (hcl : ∀ p r, parent p r → S r → S p)
    (ha : S a) (hb : S b) : ¬ K seed S a ∧ ¬ K seed S b :=
  ⟨fun h => ((conclOf_iff parent parent_wf judge _ a).1 h).2 ⟨live S hcl b hb, conc_ab.2⟩,
   fun h => ((conclOf_iff parent parent_wf judge _ b).1 h).2 ⟨live S hcl a ha, conc_ab.1⟩⟩

theorem not_offered (root S : R → Prop) (r : R) (h : ¬ S r) : ¬ K root S r :=
  fun hk => h (kept_offered parent parent_wf _ S r
    (concl_live parent parent_wf judge _ root S r hk).1)

/-- T7 (instance). Two concurrent claims and nothing else: the slot is empty. -/
theorem conflict_empty : ¬ holder (K seed S2) a ∧ ¬ holder (K seed S2) b := by
  have hd := claims_denied S2 S2_closed rfl rfl
  have hc : ¬ K seed S2 c := not_offered seed S2 c (by decide)
  have hdd : ¬ K seed S2 d := not_offered seed S2 d (by decide)
  constructor
  · intro h
    cases h with
    | inl h => exact hd.1 h
    | inr h =>
      cases h with
      | inl h => exact hc h.2
      | inr h => exact absurd h.1 (by decide)
  · intro h
    cases h with
    | inl h => exact hd.2 h
    | inr h =>
      cases h with
      | inl h => exact absurd h.1 (by decide)
      | inr h => exact hdd h.2

/-- T7 (instance). A row that is a descendant of both claims decides: `c` names `a` and `b` as
    parents and decides for `a`. The slot has one holder, and no rank was used. -/
theorem descendant_decides : holder (K seed S3) a ∧ ¬ holder (K seed S3) b := by
  have hd := claims_denied S3 S3_closed rfl rfl
  have hdd : ¬ K seed S3 d := not_offered seed S3 d (by decide)
  have hc : K seed S3 c :=
    (conclOf_iff parent parent_wf judge _ c).2
      ⟨live S3 S3_closed c rfl,
       fun h => absurd (kept_offered parent parent_wf _ S3 d h.1.1) (by decide)⟩
  constructor
  · exact Or.inr (Or.inl ⟨rfl, hc⟩)
  · intro h
    cases h with
    | inl h => exact hd.2 h
    | inr h =>
      cases h with
      | inl h => exact absurd h.1 (by decide)
      | inr h => exact hdd h.2

/-- T7 (instance). Two concurrent deciding rows restore the symmetry, one level up: the slot
    is empty again. A decision is itself a contested row until something below it decides. -/
theorem two_decisions_empty : ¬ holder (K seed S4) a ∧ ¬ holder (K seed S4) b := by
  have hd := claims_denied S4 S4_closed trivial trivial
  have hc : ¬ K seed S4 c := fun h =>
    ((conclOf_iff parent parent_wf judge _ c).1 h).2 ⟨live S4 S4_closed d trivial, conc_cd.2⟩
  have hdd : ¬ K seed S4 d := fun h =>
    ((conclOf_iff parent parent_wf judge _ d).1 h).2 ⟨live S4 S4_closed c trivial, conc_cd.1⟩
  constructor
  · intro h
    cases h with
    | inl h => exact hd.1 h
    | inr h =>
      cases h with
      | inl h => exact hc h.2
      | inr h => exact absurd h.1 (by decide)
  · intro h
    cases h with
    | inl h => exact hd.2 h
    | inr h =>
      cases h with
      | inl h => exact absurd h.1 (by decide)
      | inr h => exact hdd h.2

/-- T6 (v) (instance). With no seed every row of S3 is kept and none concludes anything. -/
theorem no_seed_kept_and_silent :
    (∀ r, S3 r → Kept S3 r) ∧ (∀ r, ¬ K noSeed S3 r) :=
  ⟨kept_of_closed parent parent_wf _ S3 (fun _ _ => trivial) S3_closed,
   fun r => unrooted_concludes_nothing parent parent_wf judge _ noSeed S3 r
     (fun h => h) (fun _ h _ => h)⟩

/-- T6 (v) (instance). Take `g` as a root. The offered set is the same S3; nothing is offered
    again. The deciding row now concludes and the slot has its holder. -/
theorem seed_brings_to_life :
    ¬ K noSeed S3 c ∧ K (fun r => noSeed r ∨ r = g) S3 c := by
  refine ⟨no_seed_kept_and_silent.2 c, ?_⟩
  have e : (fun r => noSeed r ∨ r = g) = seed :=
    funext fun r => propext ⟨fun h => h.elim False.elim id, Or.inr⟩
  rw [e]
  exact (conclOf_iff parent parent_wf judge _ c).2
    ⟨live S3 S3_closed c rfl,
     fun h => absurd (kept_offered parent parent_wf _ S3 d h.1.1) (by decide)⟩

/-- The rule of this instance is symmetric, so the general theorem applies to it. -/
def swap : R → R | g => g | a => b | b => a | c => d | d => c

theorem swap_invol : ∀ x, swap (swap x) = x := by intro x; cases x <;> rfl
theorem swap_parent : ∀ p r, parent (swap p) (swap r) ↔ parent p r := by
  intro p r; cases p <;> cases r <;> simp [parent, parentB, swap]
theorem swap_judge : ∀ r P C, judge (swap r) P C ↔
    judge r (fun q => P (swap q)) (fun q => C (swap q)) := by
  intro r P C; cases r <;> exact Iff.rfl
theorem swap_seed : ∀ r, seed (swap r) ↔ seed r := by
  intro r; cases r <;> simp [seed, swap]

/-- T7 on the instance by the general theorem: on any offered set the swap leaves unchanged,
    the two claims get the same conclusion. -/
theorem claims_alike (S : R → Prop) (hS : ∀ x, S (swap x) ↔ S x) :
    ¬ ((K seed S a ∧ ¬ K seed S b) ∨ (¬ K seed S a ∧ K seed S b)) :=
  contested_both_or_neither parent parent_wf swap swap_invol swap_parent (fun _ => True)
    (fun _ => Iff.rfl) judge swap_judge seed swap_seed S hS a

end Slot

/-! ## Part F. Reach: what a row means to a reader

  A second layer over the same kept set. The per-row conclusion (Part C) is the same for every
  reader. Meaning is the reader's. Every reader is its own seed: it signs acceptance rows that
  name what it trusts, those keys sign rows naming others, and meaning runs from the reader's
  rows outward along the naming edges, to a bounded depth. This is the walk of
  formal/trust_set/TrustSet.lean (`reaches`, capped depth) with its edges read off the kept
  rows. One global depth cap stands in for the per-edge budgets of that file.

  (a) An edge is a row whose per-row conclusion holds and which names a target key. A
      withdrawal of an edge is a row that names that edge as parent, is marked a withdrawal,
      and is signed by the edge's own signer (the house rule). An edge is live when it is
      concluded and no concluded withdrawal names it.
  (b) `reaches E own n k`: k is the reader's own key or is within n live edges of it.
  (c) A row means something to the reader iff its per-row conclusion holds and the reader
      reaches its signer. -/

section Reach

variable {Row Key : Type}

/-- The bounded walk. Within `n` edges of `own`, zero edges included. -/
def reaches (E : Key → Key → Prop) (own : Key) : Nat → Key → Prop
  | 0, k => k = own
  | n + 1, k => reaches E own n k ∨ ∃ m, reaches E own n m ∧ E m k

/-- The same walk from a set of starting keys. -/
def walkFrom (E : Key → Key → Prop) (A : Key → Prop) : Nat → Key → Prop
  | 0, k => A k
  | n + 1, k => walkFrom E A n k ∨ ∃ m, walkFrom E A n m ∧ E m k

theorem reaches_mono_edges (E E' : Key → Key → Prop) (h : ∀ s t, E s t → E' s t) (own : Key) :
    ∀ n k, reaches E own n k → reaches E' own n k := by
  intro n
  induction n with
  | zero => exact fun _ h => h
  | succ n ih =>
    intro k hk
    cases hk with
    | inl hk => exact Or.inl (ih k hk)
    | inr hk => exact hk.elim fun m hm => Or.inr ⟨m, ih m hm.1, h m k hm.2⟩

theorem walkFrom_start (E : Key → Key → Prop) (A : Key → Prop) (k : Key) (h : A k) :
    ∀ n, walkFrom E A n k
  | 0 => h
  | n + 1 => Or.inl (walkFrom_start E A k h n)

/-- The reader enters the walk only through the targets of edges signed by its own key. -/
theorem reaches_succ_iff (E : Key → Key → Prop) (own : Key) :
    ∀ n k, reaches E own (n + 1) k ↔ (k = own ∨ walkFrom E (E own) n k) := by
  intro n
  induction n with
  | zero =>
    intro k
    constructor
    · intro h
      cases h with
      | inl h => exact Or.inl h
      | inr h => exact h.elim fun m hm => Or.inr (hm.1 ▸ hm.2)
    · intro h
      cases h with
      | inl h => exact Or.inl h
      | inr h => exact Or.inr ⟨own, rfl, h⟩
  | succ n ih =>
    intro k
    constructor
    · intro h
      cases h with
      | inl h =>
        cases (ih k).1 h with
        | inl e => exact Or.inl e
        | inr hw => exact Or.inr (Or.inl hw)
      | inr h =>
        have ⟨m, hm, he⟩ := h
        cases (ih m).1 hm with
        | inl e => exact Or.inr (walkFrom_start E (E own) k (e ▸ he) (n + 1))
        | inr hw => exact Or.inr (Or.inr ⟨m, hw, he⟩)
    · intro h
      cases h with
      | inl h => exact Or.inl ((ih k).2 (Or.inl h))
      | inr h =>
        cases h with
        | inl hw => exact Or.inl ((ih k).2 (Or.inr hw))
        | inr h => exact h.elim fun m hm => Or.inr ⟨m, (ih m).2 (Or.inr hm.1), hm.2⟩

/-- (2) Two readers over the same edges. If the edges signed by their own keys name the same
    targets, they reach the same keys, their own two keys aside. So two readers differ only
    through rows signed by their own keys. -/
theorem two_readers (E : Key → Key → Prop) (own own' : Key)
    (h : ∀ t, E own t ↔ E own' t) (n : Nat) (k : Key) (hk : k ≠ own) (hk' : k ≠ own') :
    reaches E own (n + 1) k ↔ reaches E own' (n + 1) k := by
  have e : E own = E own' := funext fun t => propext (h t)
  rw [reaches_succ_iff, reaches_succ_iff, e]
  exact ⟨fun h => h.elim (fun x => absurd x hk) Or.inr,
         fun h => h.elim (fun x => absurd x hk') Or.inr⟩

/-- A reader with no live edge signed by its own key reaches only itself. -/
theorem no_own_edge_no_reach (E : Key → Key → Prop) (own : Key) (h : ∀ t, ¬ E own t) :
    ∀ n k, reaches E own n k → k = own := by
  intro n
  induction n with
  | zero => exact fun _ h => h
  | succ n ih =>
    intro k hk
    cases hk with
    | inl hk => exact ih k hk
    | inr hk => exact hk.elim fun m hm => absurd ((ih m hm.1) ▸ hm.2) (h k)

variable (parent : Row → Row → Prop) (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (signer : Row → Key) (names : Row → Option Key) (isWd : Row → Prop)

/- `C S r` is the per-row conclusion about `r` for the offered set `S`. The two facts used
   about it are stated as hypotheses where needed and are discharged for `concl` at the end:
     hCk   a concluded row is kept;
     hfin  once a row is kept, a row offered later does not change its conclusion. -/
variable (C : (Row → Prop) → Row → Prop)

/-- `w` withdraws edge `e`: marked a withdrawal, names `e` as parent, signed by `e`'s signer. -/
def wdOf (w e : Row) : Prop := isWd w ∧ parent e w ∧ signer w = signer e

/-- A live edge. `X` says whose withdrawals count; the definition used is `X = everyone`. -/
def liveEdge (X : Key → Prop) (S : Row → Prop) (e : Row) : Prop :=
  C S e ∧ (∃ t, names e = some t) ∧
    ¬ ∃ w, wdOf parent signer isWd w e ∧ C S w ∧ X (signer w)

/-- The edge relation on keys read off the rows. -/
def Edge (X : Key → Prop) (S : Row → Prop) (s t : Key) : Prop :=
  ∃ e, liveEdge parent signer names isWd C X S e ∧ signer e = s ∧ names e = some t

/-- (c) Meaning. -/
def means (depth : Nat) (own : Key) (S : Row → Prop) (r : Row) : Prop :=
  C S r ∧ reaches (Edge parent signer names isWd C (fun _ => True) S) own depth (signer r)

/-- (1) Meaning is a function of the offered set and the reader's key. -/
theorem means_function (depth : Nat) (own : Key) (S S' : Row → Prop) (h : ∀ r, S r ↔ S' r) :
    means parent signer names isWd C depth own S = means parent signer names isWd C depth own S' := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

/-- (1) Any arrival order: two lists that are permutations of each other give every row the
    same meaning. -/
theorem means_perm (depth : Nat) (own : Key) (l l' : List Row) (h : l.Perm l') :
    means parent signer names isWd C depth own (fun r => r ∈ l)
      = means parent signer names isWd C depth own (fun r => r ∈ l') :=
  means_function parent signer names isWd C depth own _ _ (fun _ => h.mem_iff)

/-- The circle, and why the house rule removes it. Suppose a withdrawal counted only when its
    signer has standing with the reader (`X`). A withdrawal is signed by the signer of the edge
    it withdraws, and the walk uses an edge only from a key it has already reached. So wherever
    an edge is used its withdrawals already count, and the walk is the same as when every
    withdrawal counts. The hypothesis is only that `X` holds of every key the reader reaches. -/
theorem reaches_standing_irrelevant (X : Key → Prop) (own : Key) (S : Row → Prop)
    (hX : ∀ n m, reaches (Edge parent signer names isWd C (fun _ => True) S) own n m → X m) :
    ∀ n k, reaches (Edge parent signer names isWd C X S) own n k ↔
      reaches (Edge parent signer names isWd C (fun _ => True) S) own n k := by
  have hedge : ∀ s t, X s → (Edge parent signer names isWd C X S s t ↔
      Edge parent signer names isWd C (fun _ => True) S s t) := by
    intro s t hs
    constructor
    · intro ⟨e, ⟨h1, h2, h3⟩, h4, h5⟩
      refine ⟨e, ⟨h1, h2, ?_⟩, h4, h5⟩
      intro ⟨w, hw, hc, _⟩
      exact h3 ⟨w, hw, hc, by rw [hw.2.2, h4]; exact hs⟩
    · intro ⟨e, ⟨h1, h2, h3⟩, h4, h5⟩
      exact ⟨e, ⟨h1, h2, fun ⟨w, hw, hc, _⟩ => h3 ⟨w, hw, hc, trivial⟩⟩, h4, h5⟩
  intro n
  induction n with
  | zero => exact fun _ => Iff.rfl
  | succ n ih =>
    intro k
    constructor
    · intro h
      cases h with
      | inl h => exact Or.inl ((ih k).1 h)
      | inr h =>
        have ⟨m, hm, he⟩ := h
        have hm' := (ih m).1 hm
        exact Or.inr ⟨m, hm', (hedge m k (hX n m hm')).1 he⟩
    · intro h
      cases h with
      | inl h => exact Or.inl ((ih k).2 h)
      | inr h =>
        have ⟨m, hm, he⟩ := h
        exact Or.inr ⟨m, (ih m).2 hm, (hedge m k (hX n m hm)).2 he⟩

/-- (3) A live edge signed by the reader's own key and naming the signer of `r` gives a
    concluded `r` meaning, at any depth of one or more. -/
theorem acceptance_gives_meaning (depth : Nat) (own : Key) (S : Row → Prop) (r : Row)
    (hr : C S r) (he : Edge parent signer names isWd C (fun _ => True) S own (signer r)) :
    means parent signer names isWd C (depth + 1) own S r := by
  refine ⟨hr, ?_⟩
  induction depth with
  | zero => exact Or.inr ⟨own, rfl, he⟩
  | succ n ih => exact Or.inl ih

variable (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
variable (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
    (C S r ↔ C (fun q => S q ∨ q = x) r))
include hCk hfin

/-- A live edge stays live when `x` is offered, unless a withdrawal of that edge is `x` itself
    or a descendant of `x` (a withdrawal that was waiting on `x`). -/
theorem edge_survives (S : Row → Prop) (x e : Row) (hx : ¬ S x)
    (hl : liveEdge parent signer names isWd C (fun _ => True) S e)
    (hw : ∀ w, wdOf parent signer isWd w e → w ≠ x ∧ ¬ TransGen parent x w) :
    liveEdge parent signer names isWd C (fun _ => True) (fun q => S q ∨ q = x) e := by
  refine ⟨(hfin S x e (hCk S e hl.1) hx).1 hl.1, hl.2.1, ?_⟩
  intro ⟨w, hwd, hcw, _⟩
  have ⟨hne, hna⟩ := hw w hwd
  have hk : kept parent wf wellFormed S w :=
    (kept_new_row parent wf wellFormed S x w hne hna).2 (hCk _ w hcw)
  exact hl.2.2 ⟨w, hwd, (hfin S x w hk hx).2 hcw, trivial⟩

/-- (4) What can remove meaning. Let `r` mean something to the reader, and let a row `x` be
    offered. `r` still means something afterwards, provided no withdrawal of a live edge whose
    signer the reader reaches (in fewer than `depth` edges) is `x` or a descendant of `x`.
    So meaning is lost only through a withdrawal row, signed by the signer of an edge on a
    walk from the reader, that arrives as `x` or was waiting on `x`. No other row removes it. -/
theorem meaning_survives (depth : Nat) (own : Key) (S : Row → Prop) (x r : Row) (hx : ¬ S x)
    (hm : means parent signer names isWd C depth own S r)
    (hno : ∀ e w n, n < depth →
      liveEdge parent signer names isWd C (fun _ => True) S e →
      reaches (Edge parent signer names isWd C (fun _ => True) S) own n (signer e) →
      wdOf parent signer isWd w e → w ≠ x ∧ ¬ TransGen parent x w) :
    means parent signer names isWd C depth own (fun q => S q ∨ q = x) r := by
  refine ⟨(hfin S x r (hCk S r hm.1) hx).1 hm.1, ?_⟩
  have walk : ∀ n, n ≤ depth → ∀ k,
      reaches (Edge parent signer names isWd C (fun _ => True) S) own n k →
      reaches (Edge parent signer names isWd C (fun _ => True) (fun q => S q ∨ q = x)) own n k := by
    intro n
    induction n with
    | zero => exact fun _ _ h => h
    | succ n ih =>
      intro hn k hk
      cases hk with
      | inl hk => exact Or.inl (ih (Nat.le_of_succ_le hn) k hk)
      | inr hk =>
        have ⟨m, hreach, e, hl, hs, ht⟩ := hk
        refine Or.inr ⟨m, ih (Nat.le_of_succ_le hn) m hreach, e, ?_, hs, ht⟩
        exact edge_survives parent wf wellFormed signer names isWd C hCk hfin S x e hx hl
          (fun w hwd => hno e w n hn hl (hs ▸ hreach) hwd)
  exact walk depth (Nat.le_refl _) (signer r) hm.2

/-- (4), corollary. A row that is not a withdrawal and has no withdrawal waiting on it removes
    no meaning from any row, for any reader. -/
theorem only_withdrawals_remove (depth : Nat) (own : Key) (S : Row → Prop) (x r : Row)
    (hx : ¬ S x) (hm : means parent signer names isWd C depth own S r)
    (hnw : ∀ w, isWd w → w ≠ x ∧ ¬ TransGen parent x w) :
    means parent signer names isWd C depth own (fun q => S q ∨ q = x) r :=
  meaning_survives parent wf wellFormed signer names isWd C hCk hfin depth own S x r hx hm
    (fun _ w _ _ _ _ hwd => hnw w hwd.1)

end Reach

/-- (5) The per-row conclusion of Part C, for a rule that reads no concurrent row, meets the
    two hypotheses of the reach layer: a concluded row is kept, and a kept row's conclusion is
    final. So the conclusion layer is final and the meaning layer is revisable only as
    `meaning_survives` says. -/
theorem meaning_survives_concl {Row Key : Type}
    (parent : Row → Row → Prop) (wf : WellFounded parent) (wellFormed : Row → Prop)
    (judge : Row → (Row → Prop) → (Row → Prop) → Prop)
    (hC0 : ∀ r P (C C' : Row → Prop), judge r P C ↔ judge r P C')
    (root : Row → Prop)
    (signer : Row → Key) (names : Row → Option Key) (isWd : Row → Prop)
    (depth : Nat) (own : Key) (S : Row → Prop) (x r : Row) (hx : ¬ S x)
    (hm : means parent signer names isWd (concl parent wf judge wellFormed root) depth own S r)
    (hno : ∀ e w n, n < depth →
      liveEdge parent signer names isWd (concl parent wf judge wellFormed root)
        (fun _ => True) S e →
      reaches (Edge parent signer names isWd (concl parent wf judge wellFormed root)
        (fun _ => True) S) own n (signer e) →
      wdOf parent signer isWd w e → w ≠ x ∧ ¬ TransGen parent x w) :
    means parent signer names isWd (concl parent wf judge wellFormed root) depth own
      (fun q => S q ∨ q = x) r :=
  meaning_survives parent wf wellFormed signer names isWd _
    (fun S r h => (concl_live parent wf judge wellFormed root S r h).1)
    (fun S x r hk hx => concl_final parent wf judge wellFormed hC0 root S x r hk hx)
    depth own S x r hx hm hno

/-! ### An instance of the reach layer -/

namespace Trust

/-- Keys: the reader and a board. -/
inductive Key | me | board
  deriving DecidableEq, Repr

/-- `ch` is the board's charter row. `p` is a row the board signs, naming the charter. `acc`
    is the reader's acceptance row: it names the charter as parent and the board's key as
    target. `wd` is the reader's withdrawal of that acceptance. -/
inductive R | ch | p | acc | wd
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | ch, p => true | ch, acc => true | acc, wd => true | _, _ => false
def parent (q r : R) : Prop := parentB q r = true

def depth : R → Nat | ch => 0 | p => 1 | acc => 1 | wd => 2

theorem parent_wf : WellFounded parent :=
  Subrelation.wf (r := InvImage (· < ·) depth)
    (fun {q r} h => by
      revert h; cases q <;> cases r <;> simp [parent, parentB, depth, InvImage])
    (InvImage.wf depth Nat.lt_wfRel.wf)

def signer : R → Key | ch => Key.board | p => Key.board | acc => Key.me | wd => Key.me
def names : R → Option Key | acc => some Key.board | _ => none
def isWd (r : R) : Prop := r = wd

/-- The per-row rule concludes every kept row and reads no concurrent row. -/
def judge : R → (R → Prop) → (R → Prop) → Prop := fun _ _ _ => True

abbrev Cn (S : R → Prop) : R → Prop :=
  concl parent parent_wf judge (fun _ => True) (fun _ => True) S

abbrev Means (S : R → Prop) (r : R) : Prop := means parent signer names isWd Cn 1 Key.me S r

def S1b : R → Bool | ch => true | p => true | _ => false
abbrev S1 (r : R) : Prop := S1b r = true                 -- charter and the board's row
abbrev S2 : R → Prop := fun q => S1 q ∨ q = acc          -- then the reader accepts
abbrev S3 : R → Prop := fun q => S2 q ∨ q = wd           -- then the reader withdraws

theorem S1_closed : ∀ q r, parent q r → S1 r → S1 q := by
  intro q r; cases q <;> cases r <;> simp [parent, parentB, S1, S1b]
theorem S2_closed : ∀ q r, parent q r → S2 r → S2 q := by
  intro q r; cases q <;> cases r <;> simp [parent, parentB, S2, S1, S1b]
theorem S3_closed : ∀ q r, parent q r → S3 r → S3 q := by
  intro q r; cases q <;> cases r <;> simp [parent, parentB, S3, S2, S1, S1b]

theorem concluded (S : R → Prop) (hcl : ∀ q r, parent q r → S r → S q) (r : R) (h : S r) :
    Cn S r :=
  (conclOf_iff parent parent_wf judge _ r).2
    ⟨⟨kept_of_closed parent parent_wf _ S (fun _ _ => trivial) hcl r h, Or.inl trivial⟩, trivial⟩

theorem offered (S : R → Prop) (r : R) (h : Cn S r) : S r :=
  kept_offered parent parent_wf _ S r (concl_live parent parent_wf judge _ _ S r h).1

/-- Before the reader accepts anything, the board's row is kept and concluded and means
    nothing to the reader. -/
theorem before : Cn S1 p ∧ ¬ Means S1 p := by
  refine ⟨concluded S1 S1_closed p rfl, ?_⟩
  intro ⟨_, h⟩
  cases h with
  | inl h => exact absurd (show Key.board = Key.me from h) (by decide)
  | inr h =>
    have ⟨_, _, e, hl, _, _⟩ := h
    have hoff := offered S1 e hl.1
    have hn := hl.2.1
    cases e <;> simp [names, S1, S1b] at hn hoff

/-- (3) The reader's acceptance row arrives. The board's row, already kept, now means
    something. The offered set is S1 plus that one row: nothing is offered again. -/
theorem acceptance : Means S2 p := by
  refine ⟨concluded S2 S2_closed p (Or.inl rfl), Or.inr ⟨Key.me, rfl, acc, ?_, rfl, rfl⟩⟩
  refine ⟨concluded S2 S2_closed acc (Or.inr rfl), ⟨Key.board, rfl⟩, ?_⟩
  intro ⟨w, hw, hc, _⟩
  have hoff := offered S2 w hc
  have hwd : w = wd := hw.1
  rw [hwd] at hoff
  simp [S2, S1, S1b] at hoff

/-- (4), (5) The reader's withdrawal arrives. The board's row keeps its per-row conclusion
    and loses its meaning to this reader. -/
theorem withdrawal : Cn S3 p ∧ ¬ Means S3 p := by
  refine ⟨concluded S3 S3_closed p (Or.inl (Or.inl rfl)), ?_⟩
  intro ⟨_, h⟩
  cases h with
  | inl h => exact absurd (show Key.board = Key.me from h) (by decide)
  | inr h =>
    have ⟨_, _, e, hl, _, _⟩ := h
    have hn := hl.2.1
    have hlive := hl.2.2
    cases e with
    | acc =>
      exact hlive ⟨wd, ⟨rfl, rfl, rfl⟩,
        concluded S3 S3_closed wd (Or.inr rfl), trivial⟩
    | ch => simp [names] at hn
    | p => simp [names] at hn
    | wd => simp [names] at hn

end Trust

/-! ## Axioms used -/

#print axioms kept_is_least
#print axioms door_any_order
#print axioms kept_function
#print axioms kept_mono
#print axioms close_saturated
#print axioms door_spec
#print axioms door_perm
#print axioms conclOf_unique
#print axioms concl_of_kept
#print axioms concl_function
#print axioms conclOf_local
#print axioms concl_new_row
#print axioms derived_new_row
#print axioms concl_final
#print axioms new_row_not_ancestor
#print axioms unrooted_concludes_nothing
#print axioms concl_new_root
#print axioms concl_swap
#print axioms contested_both_or_neither
#print axioms holder_both_or_neither
#print axioms Slot.conflict_empty
#print axioms Slot.descendant_decides
#print axioms Slot.two_decisions_empty
#print axioms Slot.no_seed_kept_and_silent
#print axioms Slot.seed_brings_to_life
#print axioms Slot.claims_alike
#print axioms means_function
#print axioms means_perm
#print axioms two_readers
#print axioms no_own_edge_no_reach
#print axioms reaches_standing_irrelevant
#print axioms acceptance_gives_meaning
#print axioms edge_survives
#print axioms meaning_survives
#print axioms only_withdrawals_remove
#print axioms meaning_survives_concl
#print axioms Trust.before
#print axioms Trust.acceptance
#print axioms Trust.withdrawal

end Causal
