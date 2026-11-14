/-
  Recount.lean — the window's third rule: a concurrent answer is counted again

  A window on a proposal `p` has ANSWERS (rows by entitled keys naming `p`: objections,
  assents, confirmations) and a TABLE `outcome`, a function from a set of answers to an
  outcome. The table is a parameter. A LANDING is a row by the concluder that names its
  receipt of `p` and states an outcome.

    honest   the table, over the answers in the landing's past, gives the outcome it states.
             A landing that is not honest concludes nothing.
    stands   honest, and the table over the answers in the landing's past together with the
             answers concurrent with the landing still gives the outcome it states.

  An answer that names the landing (a descendant of it) is late and is counted nowhere.

  Part 1. Definitions, and the two descriptions of the counted set.
  Part 2. Function of the kept set; a false outcome never stands; an unnamed answer gains
          the concluder nothing (the main theorem).
  Part 3. Later rows: what is fixed for ever, and exactly which rows can change `stands`.
  Part 4. Tables with an absorbing outcome.
  Part 5. The price: an entitled key that leaves the landing unnamed is always counted;
          finality holds only against answers that cannot change the table's outcome.
  Part 6. Two counting doors, with `quorum_intersection`.
  Part 7. Three instances on six rows.

  What recount does not give: the duration. No definition here reads an instant. That the
  landing was signed late enough after the receipt is the concluder's own word, and no
  theorem below says otherwise.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Window.lean.
-/

import Window

namespace Kernel

open Order Relation Causal

namespace Recount

/-! ## Part 1. Definitions -/

section Rule

variable {Row Key Out : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key)
/- `answers x p`: `x` is a row naming `p`, of a kind the window's table counts, by a key
   entitled to answer. `outcome X`: what the table gives over the set of answers `X`.
   `states lam`: the outcome the landing `lam` states. `A`: the concluded rows. That the
   landing names a receipt by its own signer, that the receipt names `p`, and that the signer
   holds the concluder's seat, read the landing's past only and sit inside `A lam`. -/
variable (answers : Row → Row → Prop)
variable (outcome : (Row → Prop) → Out) (states : Row → Out)

/-- The concluded answers in the landing's past: the ones it names. -/
def pastAns (A : Row → Prop) (p lam x : Row) : Prop :=
  A x ∧ answers x p ∧ TransGen parent x lam

/-- The concluded answers concurrent with the landing: the ones it leaves unnamed and that
    leave it unnamed. -/
def concAns (A : Row → Prop) (p lam x : Row) : Prop :=
  A x ∧ answers x p ∧ conc parent x lam

/-- What is counted: past and concurrent together. -/
def recounted (A : Row → Prop) (p lam x : Row) : Prop :=
  pastAns parent answers A p lam x ∨ concAns parent answers A p lam x

/-- Late: the landing itself, or a row that names it. -/
def late (lam x : Row) : Prop := x = lam ∨ TransGen parent lam x

/-- The concluded answers that are not late. -/
def notLate (A : Row → Prop) (p lam x : Row) : Prop :=
  A x ∧ answers x p ∧ ¬ late parent lam x

/-- The landing is concluded and the table over its own past gives the outcome it states. -/
def honest (A : Row → Prop) (p lam : Row) : Prop :=
  A lam ∧ outcome (pastAns parent answers A p lam) = states lam

/-- RECOUNT. The landing stands iff it is honest and the table over past and concurrent
    answers together still gives the outcome it states. -/
def stands (A : Row → Prop) (p lam : Row) : Prop :=
  honest parent answers outcome states A p lam ∧
    outcome (recounted parent answers A p lam) = states lam

/-- No row is its own ancestor. -/
theorem anc_irrefl (wf : WellFounded parent) (a : Row) : ¬ TransGen parent a a :=
  (WellFounded.transGen wf).induction (C := fun a => ¬ TransGen parent a a) a
    (fun x ih h => ih x h h)

/-- The counted answers are exactly the answers that are not late. -/
theorem recounted_iff_notLate (wf : WellFounded parent) (A : Row → Prop) (p lam x : Row) :
    recounted parent answers A p lam x ↔ notLate parent answers A p lam x := by
  constructor
  · intro h
    cases h with
    | inl h =>
      refine ⟨h.1, h.2.1, fun hl => ?_⟩
      cases hl with
      | inl e => rw [e] at h; exact anc_irrefl parent wf lam h.2.2
      | inr h' => exact anc_irrefl parent wf lam (anc_trans h' h.2.2)
    | inr h => exact ⟨h.1, h.2.1, fun hl => hl.elim h.2.2.2.2 h.2.2.2.1⟩
  · intro ⟨ha, ho, hl⟩
    cases Classical.em (TransGen parent x lam) with
    | inl h => exact Or.inl ⟨ha, ho, h⟩
    | inr h => exact Or.inr ⟨ha, ho, h, fun h' => hl (Or.inr h'), fun e => hl (Or.inl e)⟩

theorem recounted_eq (wf : WellFounded parent) (A : Row → Prop) (p lam : Row) :
    recounted parent answers A p lam = notLate parent answers A p lam :=
  funext fun x => propext (recounted_iff_notLate parent answers wf A p lam x)

theorem stands_iff (wf : WellFounded parent) (A : Row → Prop) (p lam : Row) :
    stands parent answers outcome states A p lam ↔
      (honest parent answers outcome states A p lam ∧
        outcome (notLate parent answers A p lam) = states lam) := by
  unfold stands
  rw [recounted_eq parent answers wf]

/-! ## Part 2. Function of the set; a false outcome; an unnamed answer -/

/-- (1) `honest` and `stands` are functions of the offered set. -/
theorem stands_function (C : (Row → Prop) → Row → Prop) (S S' : Row → Prop)
    (h : ∀ r, S r ↔ S' r) :
    honest parent answers outcome states (C S) = honest parent answers outcome states (C S') ∧
      stands parent answers outcome states (C S) = stands parent answers outcome states (C S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]
  exact ⟨rfl, rfl⟩

/-- (1) Any arrival order. -/
theorem stands_perm (C : (Row → Prop) → Row → Prop) (l l' : List Row) (h : l.Perm l') :
    stands parent answers outcome states (C (fun r => r ∈ l))
      = stands parent answers outcome states (C (fun r => r ∈ l')) :=
  (stands_function parent answers outcome states C _ _ (fun _ => h.mem_iff)).2

/-- (2), at one set. A landing that is not honest does not stand, whatever is concurrent
    with it. -/
theorem dishonest_does_not_stand (A : Row → Prop) (p lam : Row)
    (h : ¬ honest parent answers outcome states A p lam) :
    ¬ stands parent answers outcome states A p lam :=
  fun hs => h hs.1

/-- (3) Leaving answers unnamed gains nothing. If counting the concurrent answers with the
    landing's past gives another outcome than its past alone, the landing does not stand. -/
theorem unnamed_gains_nothing (A : Row → Prop) (p lam : Row)
    (h : outcome (recounted parent answers A p lam) ≠ outcome (pastAns parent answers A p lam)) :
    ¬ stands parent answers outcome states A p lam :=
  fun hs => h (hs.2.trans hs.1.2.symm)

/-- For an honest landing, to stand is for the concurrent answers to leave the table's
    outcome where the landing's past put it. -/
theorem honest_stands_iff (A : Row → Prop) (p lam : Row)
    (hh : honest parent answers outcome states A p lam) :
    stands parent answers outcome states A p lam ↔
      outcome (recounted parent answers A p lam) = outcome (pastAns parent answers A p lam) :=
  ⟨fun hs => hs.2.trans hh.2.symm, fun h => ⟨hh, h.trans hh.2⟩⟩

/-- (3) THE MAIN THEOREM. If a landing stands, the outcome it states is the table's outcome
    over every concluded answer that is not the landing and does not name it. Which answers
    the concluder named and which it left out does not enter. -/
theorem stands_is_table_over_all_not_late (wf : WellFounded parent) (A : Row → Prop)
    (p lam : Row) (h : stands parent answers outcome states A p lam) :
    states lam =
      outcome (fun x => A x ∧ answers x p ∧ ¬ (x = lam ∨ TransGen parent lam x)) :=
  ((stands_iff parent answers outcome states wf A p lam).1 h).2.symm

/-- And conversely, for a concluded landing: it stands iff its past and the set of all
    answers that are not late both give the outcome it states. -/
theorem stands_iff_table (wf : WellFounded parent) (A : Row → Prop) (p lam : Row) :
    stands parent answers outcome states A p lam ↔
      (A lam ∧ outcome (pastAns parent answers A p lam) = states lam ∧
        outcome (fun x => A x ∧ answers x p ∧ ¬ (x = lam ∨ TransGen parent lam x))
          = states lam) :=
  (stands_iff parent answers outcome states wf A p lam).trans
    ⟨fun ⟨⟨a, b⟩, c⟩ => ⟨a, b, c⟩, fun ⟨a, b, c⟩ => ⟨⟨a, b⟩, c⟩⟩

/-! ## Part 3. Later rows -/

/-- `T` is `S` with any number of further rows offered, one at a time. -/
inductive Grows (S : Row → Prop) : (Row → Prop) → Prop
  | refl : Grows S S
  | step {T : Row → Prop} (x : Row) : Grows S T → ¬ T x → Grows S (fun q => T q ∨ q = x)

variable (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (C : (Row → Prop) → Row → Prop)

theorem kept_grows (S T : Row → Prop) (r : Row) (hg : Grows S T)
    (hk : kept parent wf wellFormed S r) : kept parent wf wellFormed T r := by
  induction hg with
  | refl => exact hk
  | step x _ _ ih => exact kept_mono parent wf wellFormed _ _ (fun _ h => Or.inl h) r ih

/-- A concluded answer to `p` that the new row `x` brings in: concluded now and not before,
    concurrent with the landing, and either `x` itself or a row that was waiting on `x`. -/
def fresh (S : Row → Prop) (x p lam w : Row) : Prop :=
  C (fun q => S q ∨ q = x) w ∧ ¬ C S w ∧ answers w p ∧ conc parent w lam ∧
    (w = x ∨ TransGen parent x w)

/-- A row first offered after the landing is kept is concurrent with it exactly when it does
    not name it. Which of the two, the row's signer chooses. -/
theorem late_row_concurrent_iff (S : Row → Prop) (x lam : Row)
    (hk : kept parent wf wellFormed S lam) (hx : ¬ S x) :
    conc parent x lam ↔ ¬ TransGen parent lam x :=
  have hn := new_row_not_ancestor parent wf wellFormed S x lam hk hx
  ⟨fun h => h.2.1, fun h => ⟨hn.2, h, fun e => hn.1 e.symm⟩⟩

variable (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
variable (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
    (C S r ↔ C (fun q => S q ∨ q = x) r))
include hCk hfin

omit hCk in
/-- The conclusion on a kept row is the same at every later set. -/
theorem concl_grows (S T : Row → Prop) (r : Row) (hg : Grows S T)
    (hk : kept parent wf wellFormed S r) : C S r ↔ C T r := by
  induction hg with
  | refl => exact Iff.rfl
  | step x hg' hx ih =>
    exact ih.trans (hfin _ x r (kept_grows parent wf wellFormed S _ r hg' hk) hx)

omit hCk in
/-- The answers in a kept landing's past are the same at every later set. -/
theorem past_grows (S T : Row → Prop) (p lam : Row) (hg : Grows S T)
    (hk : kept parent wf wellFormed S lam) :
    pastAns parent answers (C T) p lam = pastAns parent answers (C S) p lam :=
  funext fun x => propext
    ⟨fun ⟨a, o, h⟩ => ⟨(concl_grows parent wf wellFormed C hfin S T x hg
        (kept_ancestors parent wf wellFormed S x lam h hk)).2 a, o, h⟩,
     fun ⟨a, o, h⟩ => ⟨(concl_grows parent wf wellFormed C hfin S T x hg
        (kept_ancestors parent wf wellFormed S x lam h hk)).1 a, o, h⟩⟩

omit hCk in
/-- (2) Honesty is settled when the landing is kept: no later row makes a landing honest or
    dishonest. -/
theorem honest_grows (S T : Row → Prop) (p lam : Row) (hg : Grows S T)
    (hk : kept parent wf wellFormed S lam) :
    honest parent answers outcome states (C S) p lam ↔
      honest parent answers outcome states (C T) p lam := by
  unfold honest
  rw [past_grows parent answers wf wellFormed C hfin S T p lam hg hk]
  exact ⟨fun ⟨a, b⟩ => ⟨(concl_grows parent wf wellFormed C hfin S T lam hg hk).1 a, b⟩,
         fun ⟨a, b⟩ => ⟨(concl_grows parent wf wellFormed C hfin S T lam hg hk).2 a, b⟩⟩

omit hCk in
/-- (2) A concluder cannot land a false outcome. A kept landing that states an outcome its
    own past does not give never stands, whatever arrives later and however it is named. -/
theorem dishonest_never_stands (S T : Row → Prop) (p lam : Row) (hg : Grows S T)
    (hk : kept parent wf wellFormed S lam)
    (h : ¬ honest parent answers outcome states (C S) p lam) :
    ¬ stands parent answers outcome states (C T) p lam :=
  fun hs => h ((honest_grows parent answers outcome states wf wellFormed C hfin S T p lam
    hg hk).2 hs.1)

/-- An answer once counted is counted at every later set. -/
theorem notLate_grows (S T : Row → Prop) (p lam w : Row) (hg : Grows S T)
    (h : notLate parent answers (C S) p lam w) : notLate parent answers (C T) p lam w :=
  ⟨(concl_grows parent wf wellFormed C hfin S T w hg (hCk S w h.1)).1 h.1, h.2.1, h.2.2⟩

/-- (4) LOCALITY, the counted set. When one row `x` is offered, the counted answers are those
    counted before together with the fresh ones: concurrent answers that are `x` or were
    waiting on `x`. Nothing leaves the count and nothing else enters it. -/
theorem notLate_new_row (S : Row → Prop) (x p lam : Row) (hx : ¬ S x)
    (hk : kept parent wf wellFormed S lam) (w : Row) :
    notLate parent answers (C (fun q => S q ∨ q = x)) p lam w ↔
      (notLate parent answers (C S) p lam w ∨ fresh parent answers C S x p lam w) := by
  constructor
  · intro ⟨hc, ho, hl⟩
    cases Classical.em (C S w) with
    | inl h => exact Or.inl ⟨h, ho, hl⟩
    | inr hn =>
      refine Or.inr ⟨hc, hn, ho, ⟨fun h => ?_, fun h => hl (Or.inr h), fun e => hl (Or.inl e)⟩, ?_⟩
      · exact hn ((hfin S x w (kept_ancestors parent wf wellFormed S w lam h hk) hx).2 hc)
      · exact Classical.byContradiction fun hne =>
          hn ((hfin S x w ((kept_new_row parent wf wellFormed S x w
            (fun e => hne (Or.inl e)) (fun h => hne (Or.inr h))).2 (hCk _ w hc)) hx).2 hc)
  · intro h
    cases h with
    | inl h => exact ⟨(hfin S x w (hCk S w h.1) hx).1 h.1, h.2.1, h.2.2⟩
    | inr h => exact ⟨h.1, h.2.2.1, fun hl => hl.elim h.2.2.2.1.2.2 h.2.2.2.1.2.1⟩

/-- (4) LOCALITY, exactly. For a kept honest landing and a new row `x`: the landing stands
    afterwards iff the table over the answers counted before together with the fresh ones
    gives the outcome it states. -/
theorem stands_new_row_iff (S : Row → Prop) (x p lam : Row) (hx : ¬ S x)
    (hk : kept parent wf wellFormed S lam)
    (hh : honest parent answers outcome states (C S) p lam) :
    stands parent answers outcome states (C (fun q => S q ∨ q = x)) p lam ↔
      outcome (fun w => notLate parent answers (C S) p lam w ∨
        fresh parent answers C S x p lam w) = states lam := by
  have e : notLate parent answers (C (fun q => S q ∨ q = x)) p lam =
      (fun w => notLate parent answers (C S) p lam w ∨ fresh parent answers C S x p lam w) :=
    funext fun w => propext
      (notLate_new_row parent answers wf wellFormed C hCk hfin S x p lam hx hk w)
  have hh' := (honest_grows parent answers outcome states wf wellFormed C hfin S _ p lam
    (Grows.step x Grows.refl hx) hk).1 hh
  rw [stands_iff parent answers outcome states wf, e]
  exact ⟨fun h => h.2, fun h => ⟨hh', h⟩⟩

/-- (4) A row that brings in no fresh answer changes nothing, in either direction. -/
theorem stands_unchanged (S : Row → Prop) (x p lam : Row) (hx : ¬ S x)
    (hk : kept parent wf wellFormed S lam)
    (hno : ∀ w, ¬ fresh parent answers C S x p lam w) :
    stands parent answers outcome states (C S) p lam ↔
      stands parent answers outcome states (C (fun q => S q ∨ q = x)) p lam := by
  have e : notLate parent answers (C (fun q => S q ∨ q = x)) p lam =
      notLate parent answers (C S) p lam :=
    funext fun w => propext
      ((notLate_new_row parent answers wf wellFormed C hCk hfin S x p lam hx hk w).trans
        ⟨fun h => h.elim id (fun h => absurd h (hno w)), Or.inl⟩)
  have hh := honest_grows parent answers outcome states wf wellFormed C hfin S _ p lam
    (Grows.step x Grows.refl hx) hk
  rw [stands_iff parent answers outcome states wf, stands_iff parent answers outcome states wf, e]
  exact ⟨fun h => ⟨hh.1 h.1, h.2⟩, fun h => ⟨hh.2 h.1, h.2⟩⟩

/-- (4) What a later row can undo, in the style of `only_withdrawals_remove`. A landing that
    stands still stands when `x` is offered, provided no answer to `p` concurrent with the
    landing is `x` or was waiting on `x`. No other row moves it. -/
theorem stands_survives (S : Row → Prop) (x p lam : Row) (hx : ¬ S x)
    (hl : stands parent answers outcome states (C S) p lam)
    (hno : ∀ w, answers w p → conc parent w lam → w ≠ x ∧ ¬ TransGen parent x w) :
    stands parent answers outcome states (C (fun q => S q ∨ q = x)) p lam :=
  (stands_unchanged parent answers outcome states wf wellFormed C hCk hfin S x p lam hx
    (hCk S lam hl.1.1)
    (fun w ⟨_, _, ho, hc, hw⟩ => hw.elim (hno w ho hc).1 (hno w ho hc).2)).1 hl

/-- (4) So a landing that stood and no longer stands was undone by a fresh concurrent answer,
    and that answer changed the table's outcome over the counted set. -/
theorem undone_only_by_counted_answer (S : Row → Prop) (x p lam : Row) (hx : ¬ S x)
    (hl : stands parent answers outcome states (C S) p lam)
    (hn : ¬ stands parent answers outcome states (C (fun q => S q ∨ q = x)) p lam) :
    (∃ w, fresh parent answers C S x p lam w) ∧
      outcome (notLate parent answers (C (fun q => S q ∨ q = x)) p lam) ≠
        outcome (notLate parent answers (C S) p lam) := by
  have hk := hCk S lam hl.1.1
  constructor
  · exact Classical.byContradiction fun hne =>
      hn ((stands_unchanged parent answers outcome states wf wellFormed C hCk hfin S x p lam
        hx hk (fun w hw => hne ⟨w, hw⟩)).1 hl)
  · intro e
    have h1 := ((stands_iff parent answers outcome states wf _ p lam).1 hl).2
    have hh := (honest_grows parent answers outcome states wf wellFormed C hfin S _ p lam
      (Grows.step x Grows.refl hx) hk).1 hl.1
    exact hn ((stands_iff parent answers outcome states wf _ p lam).2 ⟨hh, e.trans h1⟩)

/-! ## Part 4 and Part 5 (c). Finality against answers that cannot change the outcome -/

/-- (5c) FINALITY, the general form. `Q` is a set of rows (the rows of some set of keys, or
    the rows of one kind). Suppose that adding rows of `Q` to the answers now counted never
    changes the table's outcome. Then the landing stands at every later set whose newly
    counted answers are all in `Q`. A lone landing is final against exactly such answers. -/
theorem final_against (Q : Row → Prop) (S : Row → Prop) (p lam : Row)
    (hl : stands parent answers outcome states (C S) p lam)
    (hclosed : ∀ Y : Row → Prop, (∀ w, notLate parent answers (C S) p lam w → Y w) →
      (∀ w, Y w → ¬ notLate parent answers (C S) p lam w → Q w) →
      outcome Y = states lam)
    (T : Row → Prop) (hg : Grows S T)
    (hQ : ∀ w, notLate parent answers (C T) p lam w →
      ¬ notLate parent answers (C S) p lam w → Q w) :
    stands parent answers outcome states (C T) p lam :=
  (stands_iff parent answers outcome states wf _ p lam).2
    ⟨(honest_grows parent answers outcome states wf wellFormed C hfin S T p lam hg
        (hCk S lam hl.1.1)).1 hl.1,
     hclosed _ (fun w h => notLate_grows parent answers wf wellFormed C hCk hfin S T p lam w hg h)
       hQ⟩

/-- An outcome `o` is absorbing under `Q` when adding rows of `Q` to a set that gives `o`
    still gives `o`. For a reverse-quorum door with `Q` the objections and `o` "cancelled":
    more objections never turn "cancelled" into "landed". -/
def absorbing (Q : Row → Prop) (o : Out) : Prop :=
  ∀ X Y : Row → Prop, (∀ x, X x → Y x) → (∀ x, Y x → ¬ X x → Q x) →
    outcome X = o → outcome Y = o

omit wf wellFormed C hCk hfin in
/-- (4) At one set. An honest landing that states an absorbing outcome stands, if every
    answer concurrent with it is in `Q`. -/
theorem absorbing_honest_stands (Q : Row → Prop) (o : Out)
    (hab : absorbing outcome Q o) (A : Row → Prop) (p lam : Row)
    (hh : honest parent answers outcome states A p lam) (ho : states lam = o)
    (hQ : ∀ x, concAns parent answers A p lam x → Q x) :
    stands parent answers outcome states A p lam :=
  ⟨hh, (hab _ _ (fun _ h => Or.inl h)
    (fun x h hn => hQ x (h.elim (fun h => absurd h hn) id)) (hh.2.trans ho)).trans ho.symm⟩

omit hCk in
/-- (4) For ever. An honest landing that states an absorbing outcome stands at every later
    set in which the answers concurrent with it are in `Q`. -/
theorem absorbing_stands_for_ever (Q : Row → Prop) (o : Out)
    (hab : absorbing outcome Q o) (S : Row → Prop) (p lam : Row)
    (hk : kept parent wf wellFormed S lam)
    (hh : honest parent answers outcome states (C S) p lam) (ho : states lam = o)
    (T : Row → Prop) (hg : Grows S T)
    (hQ : ∀ x, concAns parent answers (C T) p lam x → Q x) :
    stands parent answers outcome states (C T) p lam :=
  absorbing_honest_stands parent answers outcome states Q o hab (C T) p lam
    ((honest_grows parent answers outcome states wf wellFormed C hfin S T p lam hg hk).1 hh)
    ho hQ

omit hCk in
/-- (4) The plain case. If more answers of any kind never move the table off `o`, an honest
    landing that states `o` stands for ever: nothing later undoes it. -/
theorem monotone_cancelled_stands_for_ever (o : Out)
    (hab : absorbing outcome (fun _ => True) o) (S : Row → Prop) (p lam : Row)
    (hk : kept parent wf wellFormed S lam)
    (hh : honest parent answers outcome states (C S) p lam) (ho : states lam = o)
    (T : Row → Prop) (hg : Grows S T) :
    stands parent answers outcome states (C T) p lam :=
  absorbing_stands_for_ever parent answers outcome states wf wellFormed C hfin
    (fun _ => True) o hab S p lam hk hh ho T hg (fun _ _ => trivial)

/-! ## Part 5 (a), (b). The price -/

/-- (5a) An entitled key that leaves the landing unnamed is counted, at any later time. Let
    the landing be kept. Let `x` be a new row, on which nothing held is waiting, that is a
    concluded answer to `p` and does not name the landing. If the table over the answers
    counted so far together with `x` does not give the outcome the landing states, then once
    `x` is offered the landing does not stand. Nothing is asked about when `x` was signed. -/
theorem unnamed_answer_unseats (S : Row → Prop) (x p lam : Row) (hx : ¬ S x)
    (hk : kept parent wf wellFormed S lam)
    (hnew : ∀ w, S w → ¬ TransGen parent x w)
    (hcx : C (fun q => S q ∨ q = x) x) (ho : answers x p)
    (hnn : ¬ TransGen parent lam x)
    (hchg : outcome (fun w => notLate parent answers (C S) p lam w ∨ w = x) ≠ states lam) :
    ¬ stands parent answers outcome states (C (fun q => S q ∨ q = x)) p lam := by
  have hlam : x ≠ lam := fun e => hx (e ▸ kept_offered parent wf wellFormed S lam hk)
  have e : notLate parent answers (C (fun q => S q ∨ q = x)) p lam =
      (fun w => notLate parent answers (C S) p lam w ∨ w = x) := by
    funext w
    apply propext
    rw [notLate_new_row parent answers wf wellFormed C hCk hfin S x p lam hx hk w]
    constructor
    · intro h
      cases h with
      | inl h => exact Or.inl h
      | inr h =>
        cases h.2.2.2.2 with
        | inl e => exact Or.inr e
        | inr hd =>
          have hoff := kept_offered parent wf wellFormed _ w (hCk _ w h.1)
          cases hoff with
          | inl hs => exact absurd hd (hnew w hs)
          | inr e => exact Or.inr e
    · intro h
      cases h with
      | inl h => exact Or.inl h
      | inr e =>
        rw [e]
        exact Or.inr ⟨hcx, fun hc => hx (kept_offered parent wf wellFormed S x (hCk S x hc)),
          ho, (late_row_concurrent_iff parent wf wellFormed S x lam hk hx).2 hnn, Or.inl rfl⟩
  intro hs
  have h2 := ((stands_iff parent answers outcome states wf _ p lam).1 hs).2
  rw [e] at h2
  exact hchg h2

/-- (5a) As an existence. Suppose the key `k` can always sign a fresh concluded answer to `p`
    that leaves the landing unnamed (`hsign`: an assumption about what keys can do, which the
    rows do not prove), and that an answer by `k` added to what is counted always takes the
    table off the landing's outcome (`hchg`). Then at every later set there is a row by `k`
    after which the landing does not stand. Under recount no landing is final against such a
    key. -/
theorem entitled_key_can_always_unseat (k : Key) (S : Row → Prop) (p lam : Row)
    (hk : kept parent wf wellFormed S lam)
    (hsign : ∀ T, kept parent wf wellFormed T lam → ∃ x, signer x = k ∧ ¬ T x ∧
      (∀ w, T w → ¬ TransGen parent x w) ∧ answers x p ∧ ¬ TransGen parent lam x ∧
      C (fun q => T q ∨ q = x) x)
    (hchg : ∀ T x, signer x = k → answers x p → ¬ T x →
      outcome (fun w => notLate parent answers (C T) p lam w ∨ w = x) ≠ states lam)
    (T : Row → Prop) (hg : Grows S T) :
    ∃ x, signer x = k ∧ ¬ T x ∧
      ¬ stands parent answers outcome states (C (fun q => T q ∨ q = x)) p lam :=
  have hkT := kept_grows parent wf wellFormed S T lam hg hk
  let ⟨x, hs, hx, hnew, ho, hnn, hcx⟩ := hsign T hkT
  ⟨x, hs, hx, unnamed_answer_unseats parent answers outcome states wf wellFormed C hCk hfin
    T x p lam hx hkT hnew hcx ho hnn (hchg T x hs ho hx)⟩

/-- (5b) The same answer signed naming the landing changes nothing. A new row that names the
    landing, whatever it says and whatever was waiting on it, leaves `stands` as it was. -/
theorem naming_answer_changes_nothing (S : Row → Prop) (x p lam : Row) (hx : ¬ S x)
    (hk : kept parent wf wellFormed S lam) (hnames : TransGen parent lam x) :
    stands parent answers outcome states (C S) p lam ↔
      stands parent answers outcome states (C (fun q => S q ∨ q = x)) p lam :=
  stands_unchanged parent answers outcome states wf wellFormed C hCk hfin S x p lam hx hk
    (fun _ ⟨_, _, _, hc, hw⟩ =>
      hc.2.1 (hw.elim (fun e => e ▸ hnames) (fun h => anc_trans hnames h)))

end Rule

/-! ## Part 6. Two counting doors -/

section Doors

variable {Row K Out : Type} [DecidableEq K]
variable (parent : Row → Row → Prop) (signer : Row → K)
variable (answers : Row → Row → Prop)
variable (outcome : (Row → Prop) → Out) (states : Row → Out)
/- `l`: the keys counted, as a list. `yes x`, `no x`: what the answer `x` says. -/
variable (l : List K) (yes no : Row → Prop)

/-- A strict majority of `l` each have an answer in `X` that says `says`. -/
def majority (says : Row → Prop) (X : Row → Prop) : Prop :=
  ∃ a : List K, a.Nodup ∧ (∀ k, k ∈ a → k ∈ l ∧ ∃ x, X x ∧ signer x = k ∧ says x) ∧
    l.length < 2 * a.length

omit [DecidableEq K] in
theorem majority_mono (says : Row → Prop) (X Y : Row → Prop) (h : ∀ x, X x → Y x)
    (hm : majority signer l says X) : majority signer l says Y :=
  let ⟨a, ha, hs, hq⟩ := hm
  ⟨a, ha, fun k hk => let ⟨hkl, x, hx, e, s⟩ := hs k hk; ⟨hkl, x, h x hx, e, s⟩, hq⟩

omit [DecidableEq K] in
/-- The count door (the halt fuse): "confirmed" as soon as a strict majority confirms. With
    the majority in the landing's past, a concluded landing stating "confirmed" is honest and
    stands, whatever is concurrent with it. -/
theorem count_door_stands (confirmed : Out)
    (hT : ∀ X, majority signer l yes X → outcome X = confirmed)
    (A : Row → Prop) (p lam : Row) (hl : A lam) (hs : states lam = confirmed)
    (hq : majority signer l yes (pastAns parent answers A p lam)) :
    stands parent answers outcome states A p lam :=
  ⟨⟨hl, (hT _ hq).trans hs.symm⟩,
   (hT _ (majority_mono signer l yes _ _ (fun _ h => Or.inl h) hq)).trans hs.symm⟩

/-- (5c) The reverse-quorum door, quorum closed. The table lands unless a strict majority
    objects. A strict majority has assented in the landing's past and the landing states
    "landed". If it does not stand, some key of `l` has both an assent and an objection among
    the counted answers: by `quorum_intersection`, undoing it takes a key of the assenting
    majority answering both ways. -/
theorem quorum_closed_needs_two_voices (landed : Out)
    (hT : ∀ X, ¬ majority signer l no X → outcome X = landed)
    (A : Row → Prop) (p lam : Row) (hl : A lam) (hs : states lam = landed)
    (hq : majority signer l yes (pastAns parent answers A p lam))
    (hn : ¬ stands parent answers outcome states A p lam) :
    ∃ k x y, k ∈ l ∧ recounted parent answers A p lam x ∧ recounted parent answers A p lam y ∧
      signer x = k ∧ signer y = k ∧ yes x ∧ no y := by
  have hmaj : majority signer l no (recounted parent answers A p lam) :=
    Classical.byContradiction fun hno =>
      hn ⟨⟨hl, (hT _ (fun h => hno (majority_mono signer l no _ _ (fun _ h => Or.inl h) h))).trans
            hs.symm⟩,
          (hT _ hno).trans hs.symm⟩
  have ⟨a, ha, has, hqa⟩ := hq
  have ⟨b, hb, hbs, hqb⟩ := hmaj
  have ⟨k, hka, hkb⟩ := quorum_intersection a b l ha hb
    (fun k hk => (has k hk).1) (fun k hk => (hbs k hk).1) hqa hqb
  have ⟨hkl, x, hx, ex, sx⟩ := has k hka
  have ⟨_, y, hy, ey, sy⟩ := hbs k hkb
  exact ⟨k, x, y, hkl, Or.inl hx, hy, ex, ey, sx, sy⟩

variable (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (C : (Row → Prop) → Row → Prop)
variable (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
    (C S r ↔ C (fun q => S q ∨ q = x) r))
include hfin

omit [DecidableEq K] in
/-- The count door, for ever: a "confirmed" landing with the majority in its past stands at
    every later set. No later row, named or unnamed, undoes it. -/
theorem count_door_final (confirmed : Out)
    (hT : ∀ X, majority signer l yes X → outcome X = confirmed)
    (S : Row → Prop) (p lam : Row) (hk : kept parent wf wellFormed S lam) (hl : C S lam)
    (hs : states lam = confirmed)
    (hq : majority signer l yes (pastAns parent answers (C S) p lam))
    (T : Row → Prop) (hg : Grows S T) :
    stands parent answers outcome states (C T) p lam :=
  count_door_stands parent signer answers outcome states l yes confirmed hT (C T) p lam
    ((concl_grows parent wf wellFormed C hfin S T lam hg hk).1 hl) hs
    (by rw [past_grows parent answers wf wellFormed C hfin S T p lam hg hk]; exact hq)

/-- (5c) The reverse-quorum door, for ever: with a strict majority of assents in its past, a
    "landed" landing stands at every later set in which no key of `l` has answered both
    ways. Its finality is against every key but those. -/
theorem quorum_closed_final (landed : Out)
    (hT : ∀ X, ¬ majority signer l no X → outcome X = landed)
    (S : Row → Prop) (p lam : Row) (hk : kept parent wf wellFormed S lam) (hl : C S lam)
    (hs : states lam = landed)
    (hq : majority signer l yes (pastAns parent answers (C S) p lam))
    (T : Row → Prop) (hg : Grows S T)
    (hone : ∀ x y, recounted parent answers (C T) p lam x →
      recounted parent answers (C T) p lam y → signer x = signer y → yes x → no y → False) :
    stands parent answers outcome states (C T) p lam :=
  Classical.byContradiction fun hn =>
    let ⟨_, x, y, _, hx, hy, ex, ey, sx, sy⟩ :=
      quorum_closed_needs_two_voices parent signer answers outcome states l yes no landed hT
        (C T) p lam ((concl_grows parent wf wellFormed C hfin S T lam hg hk).1 hl) hs
        (by rw [past_grows parent answers wf wellFormed C hfin S T p lam hg hk]; exact hq) hn
    hone x y hx hy (ex.trans ey.symm) sx sy

end Doors

/-! ## Part 7. Three instances on six rows

  `p` opens the window. `rc` is the concluder's receipt of `p`. `a1` and `a2` are answers
  naming `p`. `lam` is the landing: it names `rc` and `a2`, and leaves `a1` unnamed. `a3` is
  an answer that names `p` and the landing. So `a2` is in the landing's past, `a1` is
  concurrent with it, and `a3` is late. Every row is concluded unless said otherwise. -/

namespace RecountRows

inductive R | p | rc | a1 | a2 | lam | a3
  deriving DecidableEq, Repr

inductive Out | landed | refused | lapsed | confirmed | answered | fallback
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | p, rc => true | p, a1 => true | p, a2 => true | p, a3 => true
  | rc, lam => true | a2, lam => true | lam, a3 => true
  | _, _ => false
def parent (q r : R) : Prop := parentB q r = true

/-- The ancestor relation, written out. -/
def ancB : R → R → Bool
  | p, rc => true | p, a1 => true | p, a2 => true | p, a3 => true | p, lam => true
  | rc, lam => true | rc, a3 => true | a2, lam => true | a2, a3 => true | lam, a3 => true
  | _, _ => false

theorem anc_step1 : ∀ a b, parent a b → ancB a b = true := by
  intro a b; cases a <;> cases b <;> simp [parent, parentB, ancB]

theorem anc_step2 : ∀ a b c, ancB a b = true → parent b c → ancB a c = true := by
  intro a b c; cases a <;> cases b <;> cases c <;> simp [parent, parentB, ancB]

theorem anc_sound {a b : R} (h : TransGen parent a b) : ancB a b = true := by
  induction h with
  | single h => exact anc_step1 _ _ h
  | tail _ h ih => exact anc_step2 _ _ _ ih h

def ansB : R → Bool | a1 => true | a2 => true | a3 => true | _ => false
def answers (x q : R) : Prop := ansB x = true ∧ q = p

def All (_ : R) : Prop := True

theorem a1_concurrent : conc parent a1 lam :=
  ⟨fun h => absurd (anc_sound h) (by decide), fun h => absurd (anc_sound h) (by decide),
   by decide⟩

theorem a1_not_past (A : R → Prop) : ¬ pastAns parent answers A p lam a1 :=
  fun h => absurd (anc_sound h.2.2) (by decide)

theorem a3_not_counted (A : R → Prop) : ¬ recounted parent answers A p lam a3 := by
  intro h
  cases h with
  | inl h => exact absurd (anc_sound h.2.2) (by decide)
  | inr h => exact h.2.2.2.1 (TransGen.single rfl)

theorem a2_past : pastAns parent answers All p lam a2 :=
  ⟨trivial, ⟨rfl, rfl⟩, TransGen.single rfl⟩

open Classical in
/-- The self roster of two keys, the thief evicting the owner's device. `a1`, `a3`: the
    owner's objection, signed leaving the landing unnamed, or naming it. `a2`: the thief's own
    assent. One objection is a strict majority of the one other key, and the target has
    answered: the table refuses. -/
noncomputable def evict (X : R → Prop) : Out := if X a1 ∨ X a3 then Out.refused else Out.landed

def saysLanded (_ : R) : Out := Out.landed

/-- (6) The thief's landing is honest: its own past holds no objection. -/
theorem thief_honest (A : R → Prop) (hl : A lam) :
    honest parent answers evict saysLanded A p lam := by
  refine ⟨hl, ?_⟩
  have h : ¬ (pastAns parent answers A p lam a1 ∨ pastAns parent answers A p lam a3) :=
    fun h => h.elim (a1_not_past A) (fun h => a3_not_counted A (Or.inl h))
  unfold evict
  rw [if_neg h]
  rfl

/-- (6) The thief's landing over the owner's unnamed objection does not stand. -/
theorem thief_does_not_stand : ¬ stands parent answers evict saysLanded All p lam := by
  intro hs
  have h : recounted parent answers All p lam a1 ∨ recounted parent answers All p lam a3 :=
    Or.inl (Or.inr ⟨trivial, ⟨rfl, rfl⟩, a1_concurrent⟩)
  have h2 := hs.2
  unfold evict at h2
  rw [if_pos h] at h2
  exact absurd h2 (by decide)

/-- (5a), (5b) on the same rows. While the owner's unnamed objection `a1` is not held, the
    landing stands, and it stands with the owner's objection `a3` that names the landing
    held: the same words signed naming the landing are counted nowhere. -/
theorem thief_stands_until_unnamed_objection :
    stands parent answers evict saysLanded (fun r => r ≠ a1) p lam := by
  refine ⟨thief_honest _ (by decide), ?_⟩
  have h : ¬ (recounted parent answers (fun r => r ≠ a1) p lam a1 ∨
      recounted parent answers (fun r => r ≠ a1) p lam a3) :=
    fun h => h.elim (fun h => h.elim (fun h => h.1 rfl) (fun h => h.1 rfl)) (a3_not_counted _)
  unfold evict
  rw [if_neg h]
  rfl

open Classical in
/-- The halt fuse over three holders. `a2`: the halting holder's own confirmation, in the
    landing's past. `a1`: a second holder's confirmation, which the landing does not name.
    Two of three confirm: confirmed. Otherwise the halt lapses. -/
noncomputable def fuse (X : R → Prop) : Out := if X a1 ∧ X a2 then Out.confirmed else Out.lapsed

def saysConfirmed (_ : R) : Out := Out.confirmed

/-- (6) A holder's "confirmed" landing without the count is dishonest, whichever rows are
    concluded: its own past gives "lapsed". -/
theorem lone_confirmed_dishonest (A : R → Prop) :
    ¬ honest parent answers fuse saysConfirmed A p lam := by
  intro hh
  have h : ¬ (pastAns parent answers A p lam a1 ∧ pastAns parent answers A p lam a2) :=
    fun h => a1_not_past A h.1
  have h2 := hh.2
  unfold fuse at h2
  rw [if_neg h] at h2
  exact absurd h2 (by decide)

/-- (6) So it concludes nothing: it does not stand, at any set of concluded rows. -/
theorem lone_confirmed_never_stands (A : R → Prop) :
    ¬ stands parent answers fuse saysConfirmed A p lam :=
  dishonest_does_not_stand parent answers fuse saysConfirmed A p lam (lone_confirmed_dishonest A)

/-- And this is the honesty clause at work: with the second confirmation concurrent, the
    recount does give "confirmed", the outcome the landing states. The landing still does
    not stand. A landing naming both confirmations would. -/
theorem lone_confirmed_recount_agrees :
    fuse (recounted parent answers All p lam) = saysConfirmed lam := by
  have h : recounted parent answers All p lam a1 ∧ recounted parent answers All p lam a2 :=
    ⟨Or.inr ⟨trivial, ⟨rfl, rfl⟩, a1_concurrent⟩, Or.inl a2_past⟩
  unfold fuse
  rw [if_pos h]
  rfl

open Classical in
/-- The moderation fallback. `a1`: the moderator's ruling. `a2`: the members' act, standing
    for the members' count. A ruling by the moderator answers the report; failing that the
    members' act is the fallback; failing both it lapses. -/
noncomputable def moderation (X : R → Prop) : Out :=
  if X a1 then Out.answered else if X a2 then Out.fallback else Out.lapsed

def saysFallback (_ : R) : Out := Out.fallback

/-- (6) The members' fallback landing is honest: its past holds the members' act and no
    ruling. -/
theorem fallback_honest : honest parent answers moderation saysFallback All p lam := by
  refine ⟨trivial, ?_⟩
  unfold moderation
  rw [if_neg (a1_not_past All), if_pos a2_past]
  rfl

/-- (6) With the present moderator's ruling concurrent with it, it does not stand. -/
theorem fallback_does_not_stand : ¬ stands parent answers moderation saysFallback All p lam := by
  intro hs
  have h : recounted parent answers All p lam a1 := Or.inr ⟨trivial, ⟨rfl, rfl⟩, a1_concurrent⟩
  have h2 := hs.2
  unfold moderation at h2
  rw [if_pos h] at h2
  exact absurd h2 (by decide)

end RecountRows

/-! ## Axioms used -/

#print axioms recounted_iff_notLate
#print axioms stands_iff
#print axioms stands_function
#print axioms stands_perm
#print axioms dishonest_does_not_stand
#print axioms unnamed_gains_nothing
#print axioms honest_stands_iff
#print axioms stands_is_table_over_all_not_late
#print axioms stands_iff_table
#print axioms late_row_concurrent_iff
#print axioms honest_grows
#print axioms dishonest_never_stands
#print axioms notLate_new_row
#print axioms stands_new_row_iff
#print axioms stands_unchanged
#print axioms stands_survives
#print axioms undone_only_by_counted_answer
#print axioms final_against
#print axioms absorbing_honest_stands
#print axioms absorbing_stands_for_ever
#print axioms monotone_cancelled_stands_for_ever
#print axioms unnamed_answer_unseats
#print axioms entitled_key_can_always_unseat
#print axioms naming_answer_changes_nothing
#print axioms count_door_stands
#print axioms quorum_closed_needs_two_voices
#print axioms count_door_final
#print axioms quorum_closed_final
#print axioms RecountRows.thief_honest
#print axioms RecountRows.thief_does_not_stand
#print axioms RecountRows.thief_stands_until_unnamed_objection
#print axioms RecountRows.lone_confirmed_dishonest
#print axioms RecountRows.lone_confirmed_never_stands
#print axioms RecountRows.lone_confirmed_recount_agrees
#print axioms RecountRows.fallback_honest
#print axioms RecountRows.fallback_does_not_stand

end Recount

end Kernel
