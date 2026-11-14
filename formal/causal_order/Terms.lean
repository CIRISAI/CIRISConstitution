/-
  Terms.lean — the cut's three terms, as cut.py gives them, and the iteration's bound

  Seat.lean Part B takes the cut's terms as parameters: what clashes, what overrules, who is
  entitled. Here they are transcribed from formal/causal_kernel/cut.py.

    slots a row is on    its signer's key slot, and any other slot it carries (`onS`)
    slots a row cuts     `cutsS` (a removal of k cuts k's key slot; a deciding row its slot)
    what a cut says      `says`
    rejects              `rejects x r`: `x` names `r` among the rows it voids
    clashes x c          `x` cuts a slot that `c` cuts or that `c` is on (other than `c`'s own
                         key slot), unless the two say the same thing and the slot is one `c`
                         cuts (cut.py `_voided`, as_cut)
    overrules x c        `x` rejects `c`, on a slot `x` cuts that `c` is on or cuts
    hits x r             `x` cuts a slot `r` is on (a row that is not a cut, cut.py `status`)
    entitled             concluded, and at least `need c` voices of `c` by distinct signers,
                         each live (not voided on its key slot) and each signer holding a seat
                         that entitles `c`, standing at the head `c` names (`Kernel.entSeat`,
                         per voice)

  What is proved.
    (1) The terms meet what Part B needs: the entitlement is antitone (`entK_anti`), so the
        status is the alternating fixed point; with one voice and need one it is `entSeat`
        and the voice's liveness (`entK_single`).
    (2) Finality against outsiders from ONE hypothesis: no voice of the row is by a key with
        a live seat entitling it at the head it names (`outsider_changes_no_cutK`); and the
        outsider's own row on a slot never counts (`outsider_row_never_countsK`), with one
        hypothesis on the conclusion layer, stated (`SeatRule`).
    (3) The instances. (a) a removal of a key: it voids the key's concurrent rows, two
        removals of one key do not clash, a removal silences the removed key's concurrent
        cut, and two concurrent removals of each other's signers are both contested.
        (b) a deciding row: two concurrent deciders that pick differently clash both ways and
        are contested; two that pick the same do not clash; a decider voids the claims it
        names and rejects, and the claims concurrent with it.
    (4) The iteration `iter` of Seat.lean reaches `sure` within as many steps as there are
        cuts (`iter_bound`, `cut_iter_bound`).

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Seat.lean.
-/

import Seat

namespace Kernel

namespace Terms

open Order Relation Causal

/-! ## (4) The iteration stops within one step per cut -/

section Bound

variable {α : Type} (T : (α → Prop) → α → Prop)

open Classical in
/-- How many members of `l` satisfy `P`. -/
noncomputable def cnt (P : α → Prop) : List α → Nat
  | [] => 0
  | a :: l => (if P a then 1 else 0) + cnt P l

theorem cnt_le_length (P : α → Prop) : ∀ l : List α, cnt P l ≤ l.length
  | [] => Nat.le_refl 0
  | a :: l => by
    have := cnt_le_length P l
    unfold cnt
    simp only [List.length_cons]
    split <;> omega

theorem cnt_le (P Q : α → Prop) : ∀ l : List α, (∀ r, r ∈ l → P r → Q r) → cnt P l ≤ cnt Q l
  | [] => fun _ => Nat.le_refl 0
  | a :: l => fun h => by
    have ih := cnt_le P Q l (fun r hr => h r (List.mem_cons_of_mem a hr))
    have ha := h a (List.mem_cons_self a l)
    unfold cnt
    by_cases hp : P a
    · rw [if_pos hp, if_pos (ha hp)]; omega
    · rw [if_neg hp]; split <;> omega

theorem cnt_lt (P Q : α → Prop) : ∀ l : List α, (∀ r, r ∈ l → P r → Q r) →
    ∀ x, x ∈ l → Q x → ¬ P x → cnt P l < cnt Q l
  | [] => fun _ x hx => absurd hx (List.not_mem_nil x)
  | a :: l => fun h x hx hq hp => by
    have hle := cnt_le P Q l (fun r hr => h r (List.mem_cons_of_mem a hr))
    have ha := h a (List.mem_cons_self a l)
    unfold cnt
    cases List.mem_cons.1 hx with
    | inl e =>
      subst e
      rw [if_neg hp, if_pos hq]; omega
    | inr hm =>
      have ih := cnt_lt P Q l (fun r hr => h r (List.mem_cons_of_mem a hr)) x hm hq hp
      by_cases hpa : P a
      · rw [if_pos hpa, if_pos (ha hpa)]; omega
      · rw [if_neg hpa]; split <;> omega

variable (hT : Anti T)
include hT

/-- The stages grow. -/
theorem iter_step : ∀ n r, iter T n r → iter T (n + 1) r := by
  intro n
  induction n with
  | zero => exact fun _ h => h.elim
  | succ n ih => exact fun r h => sq_mono T hT _ _ ih r h

theorem iter_le (m : Nat) : ∀ n, m ≤ n → ∀ r, iter T m r → iter T n r := by
  intro n hmn
  induction n with
  | zero =>
    have e : m = 0 := by omega
    subst e; exact fun _ h => h
  | succ n ih =>
    intro r h
    if e : m = n + 1 then (subst e; exact h)
    else exact iter_step T hT n r (ih (by omega) r h)

/-- (4) THE BOUND. If every row the operator can return is in the finite list `l` (the
    concluded cuts), the iteration has reached what counts after `l.length` steps. -/
theorem iter_bound (l : List α) (hl : ∀ X r, T X r → r ∈ l) :
    ∀ r, sure T r ↔ iter T l.length r := by
  have hstop : ∃ k, k ≤ l.length ∧ ∀ r, iter T (k + 1) r → iter T k r := by
    apply Classical.byContradiction
    intro hno
    have grow : ∀ k, k ≤ l.length + 1 → k ≤ cnt (iter T k) l := by
      intro k
      induction k with
      | zero => exact fun _ => Nat.zero_le _
      | succ k ih =>
        intro hk
        have hk' : k ≤ l.length := by omega
        have ⟨r, hr1, hr0⟩ : ∃ r, iter T (k + 1) r ∧ ¬ iter T k r :=
          Classical.byContradiction fun h => hno ⟨k, hk', fun r hr =>
            Classical.byContradiction fun hn => h ⟨r, hr, hn⟩⟩
        have hrl : r ∈ l := hl _ r hr1
        have := cnt_lt (iter T k) (iter T (k + 1)) l (fun q _ hq => iter_step T hT k q hq) r hrl
          hr1 hr0
        have := ih (by omega)
        omega
    have := grow (l.length + 1) (Nat.le_refl _)
    have := cnt_le_length (iter T (l.length + 1)) l
    omega
  obtain ⟨k, hk, hs⟩ := hstop
  intro r
  exact ⟨fun h => iter_le T hT k l.length hk r (iter_stops T k hs r h),
    iter_sub_sure T hT l.length r⟩

/-- Contested-ness on a restricted universe. `mutual_contested` asks its hypotheses for
    every voiding set; here only for sets of rows the operator can return (`U`), which is
    what an instance can check. -/
theorem mutual_contested_within (U : α → Prop) (hU : ∀ X r, T X r → U r) (a b : α)
    (ha : ∀ X : α → Prop, (∀ r, X r → U r) → ¬ X b → T X a)
    (ha' : ∀ X : α → Prop, X b → ¬ T X a)
    (hb : ∀ X : α → Prop, (∀ r, X r → U r) → ¬ X a → T X b)
    (hb' : ∀ X : α → Prop, X a → ¬ T X b) :
    contested T a ∧ contested T b := by
  have hsU : ∀ r, sure T r → U r := fun r h =>
    hU _ r ((sure_iff T hT r).1 h)
  have hP : ∀ r, sure T r → r ≠ a ∧ r ≠ b := by
    apply lfp_least (fun X => T (T X)) (fun r => U r ∧ r ≠ a ∧ r ≠ b) _ |> fun h r hr => (h r hr).2
    intro q hq
    have hTa : T (fun r => U r ∧ r ≠ a ∧ r ≠ b) a := ha _ (fun _ h => h.1) (fun h => h.2.2 rfl)
    have hTb : T (fun r => U r ∧ r ≠ a ∧ r ≠ b) b := hb _ (fun _ h => h.1) (fun h => h.2.1 rfl)
    exact ⟨hU _ q hq, fun e => ha' _ hTb (e ▸ hq), fun e => hb' _ hTa (e ▸ hq)⟩
  have na : ¬ sure T a := fun h => (hP a h).1 rfl
  have nb : ¬ sure T b := fun h => (hP b h).2 rfl
  exact ⟨⟨ha _ hsU nb, na⟩, ⟨hb _ hsU na, nb⟩⟩

end Bound

/-! ## The terms -/

/-- The slot data of cut.py, per row. -/
structure SlotData (Row Key Sl Val : Type) where
  keySlot : Key → Sl
  onS : Row → Sl → Prop
  cutsS : Row → Sl → Prop
  says : Row → Val
  rejects : Row → Row → Prop

section Terms

variable {Row Key Sl Val T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (D : SlotData Row Key Sl Val)

/-- The slots a row is on: its signer's key slot, and the others it carries. -/
def onSlot (r : Row) (s : Sl) : Prop := s = D.keySlot (signer r) ∨ D.onS r s

/-- A cut: a row that cuts a slot. -/
def isCutK (c : Row) : Prop := ∃ s, D.cutsS c s

/-- CLASHES (cut.py `_voided`, as_cut): `x` cuts a slot that `c` cuts, or that `c` is on other
    than `c`'s own key slot; a slot `c` cuts does not count when the two say the same. -/
def clashesK (x c : Row) : Prop :=
  ∃ s, D.cutsS x s ∧ ((D.onS c s ∧ s ≠ D.keySlot (signer c)) ∨ D.cutsS c s) ∧
    ¬ (D.says x = D.says c ∧ D.cutsS c s)

/-- OVERRULES (cut.py, the `rejects` branch): `x` rejects `c` on a slot `x` cuts that `c` is
    on or cuts. That `c` is in `x`'s past is asked by `cutT` and `rowVoided`. -/
def overrulesK (x c : Row) : Prop :=
  D.rejects x c ∧ ∃ s, D.cutsS x s ∧ (onSlot signer D c s ∨ D.cutsS c s)

/-- HITS (cut.py `status`): `x` cuts a slot `r` is on. -/
def hitsK (x r : Row) : Prop := ∃ s, D.cutsS x s ∧ onSlot signer D r s

/-- A voice is hit on its key slot only. -/
def keyHit (x v : Row) : Prop := D.cutsS x (D.keySlot (signer v))

/-- A voice is live under the voiding set `X` (cut.py `_voided(v, {key(signer v)}, X)`). -/
def liveVoice (X : Row → Prop) (v : Row) : Prop :=
  ¬ rowVoided parent (overrulesK signer D) (keyHit signer D) X v

theorem liveVoice_anti (X Y : Row → Prop) (hXY : ∀ r, X r → Y r) (v : Row)
    (h : liveVoice parent signer D Y v) : liveVoice parent signer D X v :=
  fun hv => h (hv.elim (fun ⟨x, hx, h1, h2⟩ => Or.inl ⟨x, hXY x hx, h1, h2⟩)
    (fun ⟨x, hx, h1, h2⟩ => Or.inr ⟨x, hXY x hx, h1, h2⟩))

variable (isWd : Row → Prop) (offer : Row → T → Prop) (isAcc : Row → Prop) (holder : T → Key)
variable (conf : (T → Prop) → (Row → Prop) → Row → T → Prop)
variable (cutsSeat : Row → T → Prop) (entitles : T → Row → Prop)
/- `cosignOf v c`: `v` is a cosignature of the act `c` states. `need c`: distinct signers it
   needs (cut.py default 1). `n`: the walk's depth. -/
variable (cosignOf : Row → Row → Prop) (need : Row → Nat) (n : Nat)

/-- The voices of `c`: itself, and the cosignatures of its act it names. -/
def voiceOf (c v : Row) : Prop := v = c ∨ (cosignOf v c ∧ parent v c)

/-- The key `k` holds a seat entitling `c`, standing at the head `c` names: by the concluded
    rows in `c`'s past, less what the cuts of `X` in `c`'s past remove (`Kernel.entSeat`,
    for any key). -/
def seatedAt (A X : Row → Prop) (c : Row) (k : Key) : Prop :=
  ∃ t, entitles t c ∧ holder t = k ∧
    stands parent signer isWd offer isAcc holder conf
      (fun r => A r ∧ TransGen parent r c) (fun r => A r ∧ TransGen parent r c)
      (cutOut parent cutsSeat (fun x => X x ∧ TransGen parent x c)) n t

/-- ENTITLED: concluded, and `need c` voices of `c` by distinct signers, each concluded, live,
    and seated at the head `c` names. -/
def entK (A X : Row → Prop) (c : Row) : Prop :=
  A c ∧ ∃ l : List Row, l.Pairwise (fun u v => signer u ≠ signer v) ∧ need c ≤ l.length ∧
    ∀ v, v ∈ l → A v ∧ voiceOf parent cosignOf c v ∧ liveVoice parent signer D X v ∧
      seatedAt parent signer isWd offer isAcc holder conf cutsSeat entitles n A X c (signer v)

/-! ### (1) What Part B needs -/

theorem seatedAt_anti (hconf : ConfMono conf) (A X Y : Row → Prop) (hXY : ∀ r, X r → Y r)
    (c : Row) (k : Key)
    (h : seatedAt parent signer isWd offer isAcc holder conf cutsSeat entitles n A Y c k) :
    seatedAt parent signer isWd offer isAcc holder conf cutsSeat entitles n A X c k :=
  let ⟨t, h1, h2, h3⟩ := h
  ⟨t, h1, h2, stands_mono parent signer isWd offer isAcc holder conf hconf _ _ _ _ _ _
    (fun _ h => h) (fun _ h => h) (fun _ _ ⟨x, hx, hc⟩ => ⟨x, ⟨hXY x hx.1, hx.2⟩, hc⟩) n t h3⟩

/-- (1) The entitlement is antitone in the voiding set: `cutT_anti` applies, and the status
    of Part B is defined with these terms. -/
theorem entK_anti (hconf : ConfMono conf) :
    EntAnti (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n) :=
  fun A X Y hXY c ⟨hA, l, hp, hn, hv⟩ =>
    ⟨hA, l, hp, hn, fun v hm =>
      let ⟨a, b, d, e⟩ := hv v hm
      ⟨a, b, liveVoice_anti parent signer D X Y hXY v d,
        seatedAt_anti parent signer isWd offer isAcc holder conf cutsSeat entitles n hconf A X Y
          hXY c _ e⟩⟩

/-- (1) One voice, need one: the entitlement is `Kernel.entSeat` with the cut's own voice
    live. -/
theorem entK_single (A X : Row → Prop) (c : Row) (hone : ∀ v, voiceOf parent cosignOf c v → v = c)
    (hneed : need c = 1) :
    entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n A X c ↔
      (A c ∧ liveVoice parent signer D X c ∧
        entSeat parent signer isWd offer isAcc holder conf cutsSeat entitles n A X c) := by
  constructor
  · intro ⟨hA, l, _, hn, hv⟩
    match l, hn, hv with
    | [], hn, _ => rw [hneed] at hn; exact absurd hn (by simp)
    | v :: _, _, hv =>
      have ⟨_, hvo, hl, hs⟩ := hv v (List.mem_cons_self _ _)
      have e := hone v hvo
      subst e
      exact ⟨hA, hl, hs⟩
  · intro ⟨hA, hl, hs⟩
    exact ⟨hA, [c], List.pairwise_singleton _ _, by rw [hneed]; simp,
      fun v hm => by
        have e : v = c := List.mem_singleton.1 hm
        subst e
        exact ⟨hA, Or.inl rfl, hl, hs⟩⟩

/-! ### (2) Finality against outsiders, from one hypothesis -/

/-- THE ONE HYPOTHESIS. The key `k` holds no seat entitling `x`, standing at the head `x` names,
    by the concluded rows `A`, even with no cut at all. (No seat "at any head" implies it.) -/
def noSeat (A : Row → Prop) (k : Key) (x : Row) : Prop :=
  ∀ m t, entitles t x → holder t = k →
    ¬ stands parent signer isWd offer isAcc holder conf
      (fun r => A r ∧ TransGen parent r x) (fun r => A r ∧ TransGen parent r x)
      (fun _ _ => False) m t

/-- No seat with no cut is no seat under any cut. -/
theorem noSeat_seatedAt (hconf : ConfMono conf) (A X : Row → Prop) (k : Key) (x : Row)
    (h : noSeat parent signer isWd offer isAcc holder conf entitles A k x) :
    ¬ seatedAt parent signer isWd offer isAcc holder conf cutsSeat entitles n A X x k :=
  fun ⟨t, h1, h2, h3⟩ => h n t h1 h2
    (stands_mono parent signer isWd offer isAcc holder conf hconf _ _ _ _ _ _
      (fun _ h => h) (fun _ h => h) (fun _ _ h => h.elim) n t h3)

/-- An outsider's row is entitled to nothing, whatever does the voiding. -/
theorem outsider_not_entitled (hconf : ConfMono conf) (A X : Row → Prop) (x : Row)
    (hneed : 1 ≤ need x)
    (hout : ∀ v, voiceOf parent cosignOf x v →
      noSeat parent signer isWd offer isAcc holder conf entitles A (signer v) x) :
    ¬ entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n A X x := by
  intro ⟨_, l, _, hn, hv⟩
  match l, hn, hv with
  | [], hn, _ => exact absurd hn (by simp; omega)
  | v :: _, _, hv =>
    have ⟨_, hvo, _, hs⟩ := hv v (List.mem_cons_self _ _)
    exact noSeat_seatedAt parent signer isWd offer isAcc holder conf cutsSeat entitles n hconf
      A X (signer v) x (hout v hvo) hs

variable (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (C : (Row → Prop) → Row → Prop)
variable (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
variable (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
    (C S r ↔ C (fun q => S q ∨ q = x) r))
include hCk hfin

/-- Offering `x` changes no other row's entitlement: a concluded row's voices and its past are
    kept before `x`. -/
theorem entK_same_off (S : Row → Prop) (x : Row) (hx : ¬ S x)
    (hnw : ∀ y, S y → ¬ TransGen parent x y) (X : Row → Prop) (r : Row) (hne : r ≠ x) :
    entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n
        (C (fun q => S q ∨ q = x)) X r ↔
      entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n
        (C S) X r := by
  have hA := concl_same_off parent wf wellFormed C hCk hfin S x hx hnw
  have past : C S r → ∀ q, TransGen parent q r →
      (C (fun q => S q ∨ q = x) q ↔ C S q) := by
    intro hr q hq
    have hk := kept_ancestors parent wf wellFormed S q r hq (hCk S r hr)
    exact hA q (new_row_not_ancestor parent wf wellFormed S x q hk hx).1
  have voiceIn : ∀ v, voiceOf parent cosignOf r v → v = r ∨ TransGen parent v r :=
    fun v h => h.elim Or.inl (fun h => Or.inr (TransGen.single h.2))
  constructor
  · intro ⟨hr', l, hp, hn, hv⟩
    have hr : C S r := (hA r hne).1 hr'
    have e : (fun q => C (fun q => S q ∨ q = x) q ∧ TransGen parent q r) =
        (fun q => C S q ∧ TransGen parent q r) :=
      funext fun q => propext ⟨fun h => ⟨(past hr q h.2).1 h.1, h.2⟩,
        fun h => ⟨(past hr q h.2).2 h.1, h.2⟩⟩
    refine ⟨hr, l, hp, hn, fun v hm => ?_⟩
    have ⟨a, b, c, d⟩ := hv v hm
    refine ⟨(voiceIn v b).elim (fun e => e ▸ hr) (fun h => (past hr v h).1 a), b, c, ?_⟩
    unfold seatedAt at d ⊢
    rw [e] at d
    exact d
  · intro ⟨hr, l, hp, hn, hv⟩
    have e : (fun q => C (fun q => S q ∨ q = x) q ∧ TransGen parent q r) =
        (fun q => C S q ∧ TransGen parent q r) :=
      funext fun q => propext ⟨fun h => ⟨(past hr q h.2).1 h.1, h.2⟩,
        fun h => ⟨(past hr q h.2).2 h.1, h.2⟩⟩
    refine ⟨(hA r hne).2 hr, l, hp, hn, fun v hm => ?_⟩
    have ⟨a, b, c, d⟩ := hv v hm
    refine ⟨(voiceIn v b).elim (fun e => e ▸ (hA r hne).2 hr) (fun h => (past hr v h).2 a),
      b, c, ?_⟩
    unfold seatedAt at d ⊢
    rw [e]
    exact d

/-- (2) `Kernel.outsider_changes_no_cut` with its two "outsider" hypotheses DERIVED. The one
    hypothesis: no voice of `x` is by a key holding a seat that entitles `x` at the head `x`
    names (for a cut whose only voice is itself: its signer holds none). `need x ≥ 1` is
    cut.py's default; with need zero any row is entitled. -/
theorem outsider_changes_no_cutK (hconf : ConfMono conf) (isCut : Row → Prop)
    (clashes overrules : Row → Row → Prop)
    (S : Row → Prop) (x : Row) (hx : ¬ S x) (hnw : ∀ y, S y → ¬ TransGen parent x y)
    (hneed : 1 ≤ need x)
    (hout : ∀ v, voiceOf parent cosignOf x v →
      noSeat parent signer isWd offer isAcc holder conf entitles (C (fun q => S q ∨ q = x))
        (signer v) x) :
    cutCounts parent isCut clashes overrules
        (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n)
        (C (fun q => S q ∨ q = x))
      = cutCounts parent isCut clashes overrules
        (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n)
        (C S) ∧
    cutPoss parent isCut clashes overrules
        (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n)
        (C (fun q => S q ∨ q = x))
      = cutPoss parent isCut clashes overrules
        (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n)
        (C S) ∧
    ¬ cutPoss parent isCut clashes overrules
        (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n)
        (C (fun q => S q ∨ q = x)) x :=
  outsider_changes_no_cut parent isCut clashes overrules _ wf wellFormed C hCk hfin S x hx hnw
    (fun X r hne => entK_same_off parent signer D isWd offer isAcc holder conf cutsSeat entitles
      cosignOf need n wf wellFormed C hCk hfin S x hx hnw X r hne)
    (fun X h => outsider_not_entitled parent signer D isWd offer isAcc holder conf cutsSeat
      entitles cosignOf need n hconf _ X x hneed hout h.2.2.1)

omit hCk hfin in
/-- THE HYPOTHESIS ON THE CONCLUSION LAYER. Seat.lean's `hlate` is a property of the opaque
    conclusion rule `C`: a row on a slot a cut cuts concludes only if its signer holds a seat
    entitling it at the head it names. This is the rule cut.py leaves to `causal_kernel`'s
    conclusion layer (the signer's standing at the head the row names). -/
def SeatRule (C : (Row → Prop) → Row → Prop) : Prop :=
  ∀ S r c, C S r → hitsK signer D c r →
    ∃ m t, entitles t r ∧ holder t = signer r ∧
      stands parent signer isWd offer isAcc holder conf
        (fun q => C S q ∧ TransGen parent q r) (fun q => C S q ∧ TransGen parent q r)
        (fun _ _ => False) m t

omit hCk hfin in
/-- Under the rule, a row on a slot by a key with no seat at its head concludes nothing. -/
theorem outsider_concludes_nothing (hrule : SeatRule parent signer D isWd offer isAcc holder conf
      entitles C) (S : Row → Prop) (x c : Row) (hhit : hitsK signer D c x)
    (hout : noSeat parent signer isWd offer isAcc holder conf entitles (C S) (signer x) x) :
    ¬ C S x :=
  fun h => let ⟨m, t, h1, h2, h3⟩ := hrule S x c h hhit; hout m t h1 h2 h3

omit hCk hfin in
/-- (2) `Kernel.outsider_row_never_counts` with `hlate` DERIVED from the same hypothesis and
    `SeatRule`. -/
theorem outsider_row_never_countsK
    (hrule : SeatRule parent signer D isWd offer isAcc holder conf entitles C)
    (S : Row → Prop) (x c : Row)
    (hx : ¬ S x) (hkc : kept parent wf wellFormed S c)
    (hc : cutPoss parent (isCutK D) (clashesK signer D) (overrulesK signer D)
      (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n)
      (C (fun q => S q ∨ q = x)) c)
    (hhit : hitsK signer D c x)
    (hout : noSeat parent signer isWd offer isAcc holder conf entitles
      (C (fun q => S q ∨ q = x)) (signer x) x) :
    ¬ rowCounts parent (isCutK D) (clashesK signer D) (overrulesK signer D)
      (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n)
      (hitsK signer D) (C (fun q => S q ∨ q = x)) x :=
  outsider_row_never_counts parent (isCutK D) (clashesK signer D) (overrulesK signer D) _ wf
    wellFormed C (hitsK signer D) S x c hx hkc hc hhit
    (fun _ => outsider_concludes_nothing parent signer D isWd offer isAcc holder conf entitles C
      hrule _ x c hhit hout)

end Terms

/-! ## (3) The instances -/

section Instances

variable {Row Key Sl Val T : Type}
variable (parent : Row → Row → Prop) (wf : WellFounded parent)
variable (signer : Row → Key) (D : SlotData Row Key Sl Val)

/-- (a) `c` removes `k`: it cuts `k`'s key slot and nothing else, says "out", and carries no
    other slot. -/
def removalOf (out : Val) (c : Row) (k : Key) : Prop :=
  (∀ s, D.cutsS c s ↔ s = D.keySlot k) ∧ D.says c = out ∧ ∀ s, ¬ D.onS c s

/-- (b) `c` decides slot `s0` with pick `p`: it cuts `s0` only, is on `s0`, and says `p`. -/
def deciderOf (c : Row) (s0 : Sl) (p : Val) : Prop :=
  (∀ s, D.cutsS c s ↔ s = s0) ∧ D.onS c s0 ∧ D.says c = p

/-- (a) A counting removal of `k` voids every row of `k` concurrent with it. -/
theorem removal_voids_row (out : Val) (X : Row → Prop) (c r : Row) (k : Key)
    (hc : X c) (hrem : removalOf D out c k) (hconc : conc parent c r) (hs : signer r = k) :
    rowVoided parent (overrulesK signer D) (hitsK signer D) X r :=
  Or.inl ⟨c, hc, hconc, D.keySlot k, (hrem.1 _).2 rfl, Or.inl (by rw [hs])⟩

/-- (a) Two removals of one key say the same and do not clash: both may count. -/
theorem removals_agree (out : Val) (x c : Row) (k : Key)
    (hx : removalOf D out x k) (hc : removalOf D out c k) : ¬ clashesK signer D x c :=
  fun ⟨s, _, hon, hsame⟩ => hon.elim (fun h => hc.2.2 s h.1)
    (fun h => hsame ⟨hx.2.1.trans hc.2.1.symm, h⟩)

/-- (a) A removal of `k` cuts no slot of a cut by `k` that removes another key: it does not
    clash with it. What it takes away is the voice. -/
theorem removal_no_clash_other (out : Val) (hk : ∀ k k', D.keySlot k = D.keySlot k' → k = k')
    (x c : Row) (k k' : Key) (hx : removalOf D out x k) (hc : removalOf D out c k')
    (hne : k ≠ k') : ¬ clashesK signer D x c :=
  fun ⟨s, hxs, hon, _⟩ => hon.elim (fun h => hc.2.2 s h.1)
    (fun h => hne (hk k k' (((hx.1 s).1 hxs).symm.trans ((hc.1 s).1 h))))

/-- (a) A counting removal of `k`, concurrent with a voice signed by `k`, silences that voice. -/
theorem removal_silences (out : Val) (X : Row → Prop) (x v : Row) (k : Key)
    (hx : X x) (hrem : removalOf D out x k) (hconc : conc parent x v) (hs : signer v = k) :
    ¬ liveVoice parent signer D X v :=
  fun h => h (Or.inl ⟨x, hx, hconc, by unfold keyHit; rw [hs]; exact (hrem.1 _).2 rfl⟩)

/-- (b) Two deciders of one slot that pick differently clash. -/
theorem deciders_clash (x c : Row) (s0 : Sl) (p q : Val)
    (hx : deciderOf D x s0 p) (hc : deciderOf D c s0 q) (hpq : p ≠ q) : clashesK signer D x c :=
  ⟨s0, (hx.1 s0).2 rfl, Or.inr ((hc.1 s0).2 rfl),
    fun h => hpq (hx.2.2.symm.trans (h.1.trans hc.2.2))⟩

/-- (b) Two deciders of one slot that pick the same do not clash. -/
theorem deciders_agree (x c : Row) (s0 : Sl) (p : Val)
    (hx : deciderOf D x s0 p) (hc : deciderOf D c s0 p) : ¬ clashesK signer D x c :=
  fun ⟨s, hxs, _, hsame⟩ =>
    have e := (hx.1 s).1 hxs
    hsame ⟨hx.2.2.trans hc.2.2.symm, (hc.1 s).2 e⟩

/-- (b) A counting decider voids a claim on its slot that it names and rejects. -/
theorem decider_voids_named (X : Row → Prop) (d r : Row) (s0 : Sl) (p : Val)
    (hd : X d) (hdec : deciderOf D d s0 p) (hanc : TransGen parent r d)
    (hrej : D.rejects d r) (hon : D.onS r s0) :
    rowVoided parent (overrulesK signer D) (hitsK signer D) X r :=
  Or.inr ⟨d, hd, hanc, hrej, s0, (hdec.1 s0).2 rfl, Or.inl (Or.inr hon)⟩

/-- (b) And a claim on its slot concurrent with it. -/
theorem decider_voids_concurrent (X : Row → Prop) (d r : Row) (s0 : Sl) (p : Val)
    (hd : X d) (hdec : deciderOf D d s0 p) (hconc : conc parent d r) (hon : D.onS r s0) :
    rowVoided parent (overrulesK signer D) (hitsK signer D) X r :=
  Or.inl ⟨d, hd, hconc, s0, (hdec.1 s0).2 rfl, Or.inr hon⟩

variable (isWd : Row → Prop) (offer : Row → T → Prop) (isAcc : Row → Prop) (holder : T → Key)
variable (conf : (T → Prop) → (Row → Prop) → Row → T → Prop)
variable (cutsSeat : Row → T → Prop) (entitles : T → Row → Prop)
variable (cosignOf : Row → Row → Prop) (need : Row → Nat) (n : Nat)

/-- Two cuts whose only voice is themselves, need one, concluded, concurrent, seated at their
    heads whatever concluded cuts count, and the only concluded cuts. -/
structure Pair (A : Row → Prop) (a b : Row) : Prop where
  conc_ab : conc parent a b
  Aa : A a
  Ab : A b
  cut_a : isCutK D a
  cut_b : isCutK D b
  only : ∀ x, A x → isCutK D x → x = a ∨ x = b
  one_a : ∀ v, voiceOf parent cosignOf a v → v = a
  one_b : ∀ v, voiceOf parent cosignOf b v → v = b
  need_a : need a = 1
  need_b : need b = 1
  seat_a : ∀ X, (∀ r, X r → A r ∧ isCutK D r) →
    seatedAt parent signer isWd offer isAcc holder conf cutsSeat entitles n A X a (signer a)
  seat_b : ∀ X, (∀ r, X r → A r ∧ isCutK D r) →
    seatedAt parent signer isWd offer isAcc holder conf cutsSeat entitles n A X b (signer b)

include wf in
/-- (a) MUTUAL REMOVAL. `a` removes `b`'s signer and `b` removes `a`'s, concurrently. Neither
    clashes with the other; each silences the other's only voice. Both are contested. -/
theorem mutual_removal_contested (hconf : ConfMono conf) (out : Val)
    (hk : ∀ k k', D.keySlot k = D.keySlot k' → k = k')
    (A : Row → Prop) (a b : Row)
    (hP : Pair parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n A a b)
    (ha : removalOf D out a (signer b)) (hb : removalOf D out b (signer a))
    (hne : signer a ≠ signer b) :
    contested (cutT parent (isCutK D) (clashesK signer D) (overrulesK signer D)
        (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n) A) a ∧
      contested (cutT parent (isCutK D) (clashesK signer D) (overrulesK signer D)
        (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n) A) b := by
  have hba : conc parent b a := ⟨hP.conc_ab.2.1, hP.conc_ab.1, fun e => hP.conc_ab.2.2 e.symm⟩
  -- the only concluded cut that can void `a`'s voice is `b`, and conversely
  have live : ∀ (X : Row → Prop) (c d : Row), (∀ r, X r → A r ∧ isCutK D r) →
      (∀ r, A r → isCutK D r → r = c ∨ r = d) → ¬ X d → conc parent c d →
      liveVoice parent signer D X c := by
    intro X c d hX honly hd hcd hv
    rcases hv with ⟨x, hx, hc, _⟩ | ⟨x, hx, hanc, _⟩
    · rcases honly x (hX x hx).1 (hX x hx).2 with e | e
      · subst e; exact hc.2.2 rfl
      · subst e; exact hd hx
    · rcases honly x (hX x hx).1 (hX x hx).2 with e | e
      · subst e; exact wf_irrefl (WellFounded.transGen wf) _ hanc
      · subst e; exact hcd.1 hanc
  have noOv : ∀ (X : Row → Prop) (c d : Row), (∀ r, X r → A r ∧ isCutK D r) →
      (∀ r, A r → isCutK D r → r = c ∨ r = d) → conc parent c d →
      ¬ ∃ x, X x ∧ TransGen parent c x ∧ overrulesK signer D x c := by
    intro X c d hX honly hcd ⟨x, hx, hanc, _⟩
    rcases honly x (hX x hx).1 (hX x hx).2 with e | e
    · subst e; exact wf_irrefl (WellFounded.transGen wf) _ hanc
    · subst e; exact hcd.1 hanc
  have noCl : ∀ (X : Row → Prop) (c d : Row), (∀ r, X r → A r ∧ isCutK D r) →
      (∀ r, A r → isCutK D r → r = c ∨ r = d) → ¬ clashesK signer D d c →
      ¬ ∃ x, X x ∧ conc parent x c ∧ clashesK signer D x c := by
    intro X c d hX honly hdc ⟨x, hx, hc, hcl⟩
    rcases honly x (hX x hx).1 (hX x hx).2 with e | e
    · subst e; exact hc.2.2 rfl
    · subst e; exact hdc hcl
  have onlyb : ∀ r, A r → isCutK D r → r = b ∨ r = a :=
    fun r h1 h2 => (hP.only r h1 h2).elim Or.inr Or.inl
  apply mutual_contested_within _ (cutT_anti parent (isCutK D) (clashesK signer D)
    (overrulesK signer D) _ (entK_anti parent signer D isWd offer isAcc holder conf cutsSeat
      entitles cosignOf need n hconf) A)
    (fun r => A r ∧ isCutK D r) (fun _ _ h => ⟨h.1, h.2.1⟩) a b
  · intro X hX hXb
    refine ⟨hP.Aa, hP.cut_a, (entK_single parent signer D isWd offer isAcc holder conf cutsSeat
      entitles cosignOf need n A X a hP.one_a hP.need_a).2
      ⟨hP.Aa, live X a b hX hP.only hXb hP.conc_ab, hP.seat_a X hX⟩,
      noCl X a b hX hP.only (removal_no_clash_other signer D out hk b a _ _ hb ha hne),
      noOv X a b hX hP.only hP.conc_ab⟩
  · intro X hXb h
    have := ((entK_single parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf
      need n A X a hP.one_a hP.need_a).1 h.2.2.1).2.1
    exact removal_silences parent signer D out X b a (signer a) hXb hb hba rfl this
  · intro X hX hXa
    refine ⟨hP.Ab, hP.cut_b, (entK_single parent signer D isWd offer isAcc holder conf cutsSeat
      entitles cosignOf need n A X b hP.one_b hP.need_b).2
      ⟨hP.Ab, live X b a hX onlyb hXa hba, hP.seat_b X hX⟩,
      noCl X b a hX onlyb (removal_no_clash_other signer D out hk a b _ _ ha hb (Ne.symm hne)),
      noOv X b a hX onlyb hba⟩
  · intro X hXa h
    have := ((entK_single parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf
      need n A X b hP.one_b hP.need_b).1 h.2.2.1).2.1
    exact removal_silences parent signer D out X a b (signer b) hXa ha hP.conc_ab rfl this

include wf in
/-- (b) TWO DECIDERS. Two concurrent deciding rows on one slot, not a key slot, that pick
    differently, and are the only concluded cuts: they clash both ways and are both contested.
    A row naming both decides between them (`Kernel.named_and_overruled_void`, with
    `decider_voids_named` for the claims). -/
theorem two_deciders_contested (hconf : ConfMono conf) (A : Row → Prop) (a b : Row)
    (hP : Pair parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n A a b)
    (s0 : Sl) (p q : Val) (ha : deciderOf D a s0 p) (hb : deciderOf D b s0 q) (hpq : p ≠ q)
    (hkey : ∀ k, s0 ≠ D.keySlot k) :
    contested (cutT parent (isCutK D) (clashesK signer D) (overrulesK signer D)
        (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n) A) a ∧
      contested (cutT parent (isCutK D) (clashesK signer D) (overrulesK signer D)
        (entK parent signer D isWd offer isAcc holder conf cutsSeat entitles cosignOf need n) A) b := by
  have hba : conc parent b a := ⟨hP.conc_ab.2.1, hP.conc_ab.1, fun e => hP.conc_ab.2.2 e.symm⟩
  have onlyb : ∀ r, A r → isCutK D r → r = b ∨ r = a :=
    fun r h1 h2 => (hP.only r h1 h2).elim Or.inr Or.inl
  -- a decider's voice is never silenced: no concluded cut cuts a key slot
  have live : ∀ (X : Row → Prop) (c d : Row), (∀ r, X r → A r ∧ isCutK D r) →
      (∀ r, A r → isCutK D r → r = c ∨ r = d) → conc parent c d →
      (∀ s, D.cutsS c s → s = s0) → (∀ s, D.cutsS d s → s = s0) →
      liveVoice parent signer D X c := by
    intro X c d hX honly hcd _ hd hv
    rcases hv with ⟨x, hx, hxc, hk⟩ | ⟨x, hx, hanc, _⟩
    · rcases honly x (hX x hx).1 (hX x hx).2 with e | e
      · subst e; exact hxc.2.2 rfl
      · subst e
        exact hkey _ (hd _ hk).symm
    · rcases honly x (hX x hx).1 (hX x hx).2 with e | e
      · subst e; exact wf_irrefl (WellFounded.transGen wf) _ hanc
      · subst e; exact hcd.1 hanc
  have noOv : ∀ (X : Row → Prop) (c d : Row), (∀ r, X r → A r ∧ isCutK D r) →
      (∀ r, A r → isCutK D r → r = c ∨ r = d) → conc parent c d →
      ¬ ∃ x, X x ∧ TransGen parent c x ∧ overrulesK signer D x c := by
    intro X c d hX honly hcd ⟨x, hx, hanc, _⟩
    rcases honly x (hX x hx).1 (hX x hx).2 with e | e
    · subst e; exact wf_irrefl (WellFounded.transGen wf) _ hanc
    · subst e; exact hcd.1 hanc
  have noCl : ∀ (X : Row → Prop) (c d : Row), (∀ r, X r → A r ∧ isCutK D r) →
      (∀ r, A r → isCutK D r → r = c ∨ r = d) → ¬ X d →
      ¬ ∃ x, X x ∧ conc parent x c ∧ clashesK signer D x c := by
    intro X c d hX honly hd ⟨x, hx, hc, _⟩
    rcases honly x (hX x hx).1 (hX x hx).2 with e | e
    · subst e; exact hc.2.2 rfl
    · subst e; exact hd hx
  have cA : ∀ s, D.cutsS a s → s = s0 := fun s h => (ha.1 s).1 h
  have cB : ∀ s, D.cutsS b s → s = s0 := fun s h => (hb.1 s).1 h
  apply mutual_contested_within _ (cutT_anti parent (isCutK D) (clashesK signer D)
    (overrulesK signer D) _ (entK_anti parent signer D isWd offer isAcc holder conf cutsSeat
      entitles cosignOf need n hconf) A)
    (fun r => A r ∧ isCutK D r) (fun _ _ h => ⟨h.1, h.2.1⟩) a b
  · intro X hX hXb
    exact ⟨hP.Aa, hP.cut_a, (entK_single parent signer D isWd offer isAcc holder conf cutsSeat
      entitles cosignOf need n A X a hP.one_a hP.need_a).2
      ⟨hP.Aa, live X a b hX hP.only hP.conc_ab cA cB, hP.seat_a X hX⟩,
      noCl X a b hX hP.only hXb, noOv X a b hX hP.only hP.conc_ab⟩
  · intro X hXb h
    exact h.2.2.2.1 ⟨b, hXb, hba, deciders_clash signer D b a s0 q p hb ha (Ne.symm hpq)⟩
  · intro X hX hXa
    exact ⟨hP.Ab, hP.cut_b, (entK_single parent signer D isWd offer isAcc holder conf cutsSeat
      entitles cosignOf need n A X b hP.one_b hP.need_b).2
      ⟨hP.Ab, live X b a hX onlyb hba cB cA, hP.seat_b X hX⟩,
      noCl X b a hX onlyb hXa, noOv X b a hX onlyb hba⟩
  · intro X hXa h
    exact h.2.2.2.1 ⟨a, hXa, hP.conc_ab, deciders_clash signer D a b s0 p q ha hb hpq⟩

end Instances

/-! ## (4) for the cut -/

section CutBound

variable {Row : Type} (parent : Row → Row → Prop)
variable (isCut : Row → Prop) (clashes overrules : Row → Row → Prop)
variable (ent : (Row → Prop) → (Row → Prop) → Row → Prop)

/-- (4) The run's `K.fix(T∘T, ∅, len(cuts) + 2)` is enough: if the concluded cuts are in the
    list `l`, the status "counts" is reached in `l.length` rounds of `T ∘ T`. -/
theorem cut_iter_bound (hent : EntAnti ent) (A : Row → Prop) (l : List Row)
    (hl : ∀ c, A c → isCut c → c ∈ l) :
    ∀ c, cutCounts parent isCut clashes overrules ent A c ↔
      iter (cutT parent isCut clashes overrules ent A) l.length c :=
  iter_bound _ (cutT_anti parent isCut clashes overrules ent hent A) l
    (fun _ c h => hl c h.1 h.2.1)

end CutBound

end Terms

/-! ## Axioms used -/

#print axioms Terms.iter_bound
#print axioms Terms.cut_iter_bound
#print axioms Terms.mutual_contested_within
#print axioms Terms.entK_anti
#print axioms Terms.entK_single
#print axioms Terms.outsider_not_entitled
#print axioms Terms.entK_same_off
#print axioms Terms.outsider_changes_no_cutK
#print axioms Terms.outsider_concludes_nothing
#print axioms Terms.outsider_row_never_countsK
#print axioms Terms.removal_voids_row
#print axioms Terms.removals_agree
#print axioms Terms.removal_no_clash_other
#print axioms Terms.removal_silences
#print axioms Terms.mutual_removal_contested
#print axioms Terms.deciders_clash
#print axioms Terms.deciders_agree
#print axioms Terms.decider_voids_named
#print axioms Terms.decider_voids_concurrent
#print axioms Terms.two_deciders_contested

end Kernel
