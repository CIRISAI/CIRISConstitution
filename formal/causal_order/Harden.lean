/-
  Harden.lean — the hardening rules of KERNEL.md section 8a, rules 1 to 4

  Each rule is stated over the definitions of Seat.lean, Window.lean and Recount.lean, proved in
  general, and followed by the witness that motivated it: the attack succeeds without the rule
  and fails with it.

    F1  A row of a key whose seat was ended counts in a window only if the ending row has it in
        its past.                                                   (namespace F1, F1Rows)
    F2  A landing that does not stand says nothing against one that does.   (F2, F2Rows)
    F3  A cosignature is a voice only for a row counted over a head the cosignature names.
                                                                    (F3, Room)
    F4  An offer conferred by a count is ended by its holder's withdrawal or by a counted
        unseat, never by its proposer alone.                        (F4, Room)

  Rules 5 to 7 are in Harden2.lean and the checkpoint is in Harden3.lean.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Recount.lean.
-/

import Recount

namespace Kernel

namespace Harden

open Order Relation Causal

/-! ## Two facts about a list of voices by distinct signers -/

section Lists

variable {α β : Type}

/-- In a list whose members have pairwise distinct `f`, two members with one `f` are one
    member. With `f` the signer: one key has one voice in a count. -/
theorem pairwise_inj (f : α → β) : ∀ (l : List α), l.Pairwise (fun u v => f u ≠ f v) →
    ∀ u v, u ∈ l → v ∈ l → f u = f v → u = v
  | [], _, _, _, hu, _, _ => by cases hu
  | a :: l, hp, u, v, hu, hv, e => by
    have hp' := List.pairwise_cons.1 hp
    cases List.mem_cons.1 hu with
    | inl hua =>
      cases List.mem_cons.1 hv with
      | inl hva => exact hua.trans hva.symm
      | inr hvl =>
        subst hua
        exact absurd e (hp'.1 v hvl)
    | inr hul =>
      cases List.mem_cons.1 hv with
      | inl hva =>
        subst hva
        exact absurd e.symm (hp'.1 u hul)
      | inr hvl => exact pairwise_inj f l hp'.2 u v hul hvl e

/-- A list with pairwise distinct `f`, all of whose members have the same `f`, has at most
    one member. With `f` the signer: rows by one key are one voice. -/
theorem lone (f : α → β) (k : β) : ∀ (l : List α), l.Pairwise (fun u v => f u ≠ f v) →
    (∀ v, v ∈ l → f v = k) → l.length ≤ 1
  | [], _, _ => Nat.zero_le _
  | [_], _, _ => Nat.le_refl _
  | a :: b :: l, hp, h => by
    have h1 := (List.pairwise_cons.1 hp).1 b (List.mem_cons_self b l)
    exact absurd ((h a (List.mem_cons_self _ _)).trans
      (h b (List.mem_cons_of_mem _ (List.mem_cons_self _ _))).symm) h1

end Lists

/-! ## F1. Recount with endings

  Recount.lean counts, for a landing, the answers in its past and the answers concurrent with
  it. The rule: a concurrent answer by a key whose seat over the window's object was ended is
  counted only if the ending row has the answer among its ancestors. The answers the landing
  itself names are not filtered: honesty reads the landing's past only and stays final. -/

namespace F1

section Rule

variable {Row Key Out : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key)
variable (answers : Row → Row → Prop)
variable (outcome : (Row → Prop) → Out) (states : Row → Out)
/- `ends e k`: `e` is a row that ends the seat of key `k` over the window's object: an unseat
   of `k`, or a withdrawal of the offer that seated `k`. `E`: the ending rows in force (the
   concluded withdrawals and the unseats that count). Which unseats count is the cut's and is
   a parameter here. -/
variable (ends : Row → Key → Prop)

/-- An ending row in force ends the seat of `x`'s signer and does not have `x` in its past. -/
def endedOut (E : Row → Prop) (x : Row) : Prop :=
  ∃ e, E e ∧ ends e (signer x) ∧ ¬ TransGen parent x e

/-- What is counted under the rule: the answers in the landing's past, and the concurrent
    answers not left behind by an ending of their signer's seat. -/
def countedE (E A : Row → Prop) (p lam x : Row) : Prop :=
  Recount.pastAns parent answers A p lam x ∨
    (Recount.concAns parent answers A p lam x ∧ ¬ endedOut parent signer ends E x)

/-- Recount with endings. -/
def standsE (E A : Row → Prop) (p lam : Row) : Prop :=
  Recount.honest parent answers outcome states A p lam ∧
    outcome (countedE parent signer answers ends E A p lam) = states lam

/-- Still a function of the offered set. `EOf S` is the endings in force at `S`. -/
theorem standsE_function (C EOf : (Row → Prop) → Row → Prop) (S S' : Row → Prop)
    (h : ∀ r, S r ↔ S' r) :
    standsE parent signer answers outcome states ends (EOf S) (C S)
      = standsE parent signer answers outcome states ends (EOf S') (C S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

/-- Any arrival order. -/
theorem standsE_perm (C EOf : (Row → Prop) → Row → Prop) (l l' : List Row) (h : l.Perm l') :
    standsE parent signer answers outcome states ends (EOf (fun r => r ∈ l)) (C (fun r => r ∈ l))
      = standsE parent signer answers outcome states ends (EOf (fun r => r ∈ l'))
          (C (fun r => r ∈ l')) :=
  standsE_function parent signer answers outcome states ends C EOf _ _ (fun _ => h.mem_iff)

/-- What is counted under the rule was counted without it. -/
theorem countedE_sub (E A : Row → Prop) (p lam x : Row)
    (h : countedE parent signer answers ends E A p lam x) :
    Recount.recounted parent answers A p lam x :=
  h.elim Or.inl (fun h => Or.inr h.1)

/-- More endings in force, fewer answers counted. -/
theorem countedE_anti (E E' A : Row → Prop) (hE : ∀ e, E e → E' e) (p lam x : Row)
    (h : countedE parent signer answers ends E' A p lam x) :
    countedE parent signer answers ends E A p lam x :=
  h.elim Or.inl (fun h => Or.inr ⟨h.1, fun ⟨e, he, h1, h2⟩ => h.2 ⟨e, hE e he, h1, h2⟩⟩)

/-- An answer that every ending of its signer's seat has in its past is counted exactly as
    under plain recount. Answers signed before the ending and seen by it are unaffected. -/
theorem seen_counted (E A : Row → Prop) (p lam x : Row)
    (hseen : ∀ e, E e → ends e (signer x) → TransGen parent x e) :
    countedE parent signer answers ends E A p lam x ↔
      Recount.recounted parent answers A p lam x :=
  ⟨countedE_sub parent signer answers ends E A p lam x,
   fun h => h.elim Or.inl (fun h => Or.inr ⟨h, fun ⟨e, he, h1, h2⟩ => h2 (hseen e he h1)⟩)⟩

/-- If every concurrent answer is seen by every ending of its signer's seat, the landing
    stands under the rule exactly when it stands under plain recount. With no ending in
    force this is the general case: the rule changes nothing. -/
theorem all_seen_is_recount (E A : Row → Prop) (p lam : Row)
    (hseen : ∀ x e, Recount.concAns parent answers A p lam x → E e → ends e (signer x) →
      TransGen parent x e) :
    standsE parent signer answers outcome states ends E A p lam ↔
      Recount.stands parent answers outcome states A p lam := by
  have e : countedE parent signer answers ends E A p lam = Recount.recounted parent answers A p lam :=
    funext fun x => propext
      ⟨countedE_sub parent signer answers ends E A p lam x,
       fun h => h.elim Or.inl
         (fun h => Or.inr ⟨h, fun ⟨e, he, h1, h2⟩ => h2 (hseen x e h he h1)⟩)⟩
  unfold standsE Recount.stands
  rw [e]

theorem no_endings_is_recount (A : Row → Prop) (p lam : Row) :
    standsE parent signer answers outcome states ends (fun _ => False) A p lam ↔
      Recount.stands parent answers outcome states A p lam :=
  all_seen_is_recount parent signer answers outcome states ends _ A p lam
    (fun _ _ _ he => he.elim)

/-! ### Rows signed after the ending -/

variable (wf : WellFounded parent) (wellFormed : Row → Prop)

/-- A row first offered after an ending of its signer's seat is kept, and after the landing
    is kept, is counted for that landing at no later set in which the ending is in force.
    "After" is: not in the offered set in which the ending row is kept, hence not in the
    ending row's past. -/
theorem ended_after_never_counted (S : Row → Prop) (e x p lam : Row)
    (hke : kept parent wf wellFormed S e) (hkl : kept parent wf wellFormed S lam)
    (hx : ¬ S x) (hend : ends e (signer x)) (E' A' : Row → Prop) (hE : E' e) :
    ¬ countedE parent signer answers ends E' A' p lam x := by
  intro h
  cases h with
  | inl h => exact (new_row_not_ancestor parent wf wellFormed S x lam hkl hx).2 h.2.2
  | inr h => exact h.2 ⟨e, hE, hend, (new_row_not_ancestor parent wf wellFormed S x e hke hx).2⟩

variable (C : (Row → Prop) → Row → Prop)

/-- THE RULE'S THEOREM. Let the landing be kept at `S` and let `T` be any later set. Suppose
    every concurrent answer concluded at `T` and not at `S` is by a key whose seat is ended by
    a row already kept at `S` and in force at `T` (`hfresh`), and the endings in force treat
    the answers concluded at `S` as before (`hE`: no ending of an older answer's signer was
    added or lifted). Then the landing stands at `T` exactly when it stood at `S`. However
    many rows the ended keys sign, and however they name or do not name the landing, they
    neither unseat a standing landing nor rescue one that does not stand. -/
theorem ended_keys_change_nothing
    (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
    (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
      (C S r ↔ C (fun q => S q ∨ q = x) r))
    (ES ET S T : Row → Prop) (p lam : Row) (hg : Recount.Grows S T)
    (hk : kept parent wf wellFormed S lam)
    (hfresh : ∀ w, Recount.concAns parent answers (C T) p lam w → ¬ C S w →
      ∃ e, kept parent wf wellFormed S e ∧ ET e ∧ ends e (signer w))
    (hE : ∀ w, C S w → (endedOut parent signer ends ET w ↔ endedOut parent signer ends ES w)) :
    standsE parent signer answers outcome states ends ES (C S) p lam ↔
      standsE parent signer answers outcome states ends ET (C T) p lam := by
  have ep := Recount.past_grows parent answers wf wellFormed C hfin S T p lam hg hk
  have e : countedE parent signer answers ends ET (C T) p lam
      = countedE parent signer answers ends ES (C S) p lam := by
    funext w
    apply propext
    constructor
    · intro h
      cases h with
      | inl h => rw [ep] at h; exact Or.inl h
      | inr h =>
        cases Classical.em (C S w) with
        | inl hc => exact Or.inr ⟨⟨hc, h.1.2.1, h.1.2.2⟩, fun he => h.2 ((hE w hc).2 he)⟩
        | inr hn =>
          have ⟨e, hke, hEe, hend⟩ := hfresh w h.1 hn
          exact absurd ⟨e, hEe, hend, fun hwe => hn ((Recount.concl_grows parent wf wellFormed C
            hfin S T w hg (kept_ancestors parent wf wellFormed S w e hwe hke)).2 h.1.1)⟩ h.2
    · intro h
      cases h with
      | inl h => rw [← ep] at h; exact Or.inl h
      | inr h =>
        exact Or.inr ⟨⟨(Recount.concl_grows parent wf wellFormed C hfin S T w hg
          (hCk S w h.1.1)).1 h.1.1, h.1.2.1, h.1.2.2⟩, fun he => h.2 ((hE w h.1.1).1 he)⟩
  have hh := Recount.honest_grows parent answers outcome states wf wellFormed C hfin S T p lam hg hk
  unfold standsE
  rw [e]
  exact ⟨fun h => ⟨hh.1 h.1, h.2⟩, fun h => ⟨hh.2 h.1, h.2⟩⟩

/-- One row. The seat of `x`'s signer was ended by `e`, kept at `S` and in force. `x` is then
    offered, with nothing held waiting on it. Whatever `x` says and whatever it names, the
    landing stands afterwards exactly when it stood before. Compare
    `Recount.unnamed_answer_unseats`: without the rule the same row unseats the landing. -/
theorem ended_key_cannot_unseat
    (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
    (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
      (C S r ↔ C (fun q => S q ∨ q = x) r))
    (E S : Row → Prop) (e x p lam : Row) (hx : ¬ S x)
    (hnew : ∀ w, S w → ¬ TransGen parent x w)
    (hk : kept parent wf wellFormed S lam) (hke : kept parent wf wellFormed S e)
    (hE : E e) (hend : ends e (signer x)) :
    standsE parent signer answers outcome states ends E (C S) p lam ↔
      standsE parent signer answers outcome states ends E (C (fun q => S q ∨ q = x)) p lam := by
  apply ended_keys_change_nothing parent signer answers outcome states ends wf wellFormed C
    hCk hfin E E S _ p lam (Recount.Grows.step x Recount.Grows.refl hx) hk
  · intro w hw hn
    have hoff := kept_offered parent wf wellFormed _ w (hCk _ w hw.1)
    cases hoff with
    | inl hs =>
      have hne : w ≠ x := fun e' => hx (e' ▸ hs)
      exact absurd ((hfin S x w ((kept_new_row parent wf wellFormed S x w hne (hnew w hs)).2
        (hCk _ w hw.1)) hx).2 hw.1) hn
    | inr e' => exact ⟨e, hke, hE, e' ▸ hend⟩
  · exact fun _ _ => Iff.rfl

end Rule

end F1

/-! ### F1, the witness (attacks.py test 1)

  Three holders h1, h2, h3. `p`: h1 halts. `r`, `L`: h3's receipt and landing "lapsed". `xh`:
  the unseat of h2, naming `L` and `c0`. `c2`: h2's "confirm", naming only `p`, signed after
  the removal. `c0`: a "confirm" by h2 that the removal's own past names. The fuse confirms
  when h2 confirms (with the opener that is two of three). -/

namespace F1Rows

inductive R | p | r | L | c0 | xh | c2
  deriving DecidableEq, Repr

inductive Key | h1 | h2 | h3
  deriving DecidableEq, Repr

inductive Out | confirmed | lapsed
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | p, r => true | p, c0 => true | p, c2 => true | r, L => true | L, xh => true | c0, xh => true
  | _, _ => false
def parent (a b : R) : Prop := parentB a b = true

def ancB : R → R → Bool
  | p, r => true | p, c0 => true | p, c2 => true | p, L => true | p, xh => true
  | r, L => true | r, xh => true | L, xh => true | c0, xh => true
  | _, _ => false

theorem anc_step1 : ∀ a b, parent a b → ancB a b = true := by
  intro a b; cases a <;> cases b <;> simp [parent, parentB, ancB]

theorem anc_step2 : ∀ a b c, ancB a b = true → parent b c → ancB a c = true := by
  intro a b c; cases a <;> cases b <;> cases c <;> simp [parent, parentB, ancB]

theorem anc_sound {a b : R} (h : TransGen parent a b) : ancB a b = true := by
  induction h with
  | single h => exact anc_step1 _ _ h
  | tail _ h ih => exact anc_step2 _ _ _ ih h

def signer : R → Key
  | p => Key.h1 | r => Key.h3 | L => Key.h3 | c0 => Key.h2 | xh => Key.h1 | c2 => Key.h2

def ansB : R → Bool | c0 => true | c2 => true | _ => false
def answers (x q : R) : Prop := ansB x = true ∧ q = p

/-- `xh` ends the seat of h2. -/
def ends (e : R) (k : Key) : Prop := e = xh ∧ k = Key.h2
def E (e : R) : Prop := e = xh

open Classical in
noncomputable def fuse (X : R → Prop) : Out := if X c0 ∨ X c2 then Out.confirmed else Out.lapsed

def says (_ : R) : Out := Out.lapsed

def All (_ : R) : Prop := True
/-- The rows without `c0`: the removed holder signed nothing before its removal. -/
abbrev NoC0 (x : R) : Prop := x ≠ c0

theorem c2_conc : conc parent c2 L :=
  ⟨fun h => absurd (anc_sound h) (by decide), fun h => absurd (anc_sound h) (by decide), by decide⟩

theorem c0_conc : conc parent c0 L :=
  ⟨fun h => absurd (anc_sound h) (by decide), fun h => absurd (anc_sound h) (by decide), by decide⟩

theorem no_past (A : R → Prop) :
    ¬ (Recount.pastAns parent answers A p L c0 ∨ Recount.pastAns parent answers A p L c2) :=
  fun h => h.elim (fun h => absurd (anc_sound h.2.2) (by decide))
    (fun h => absurd (anc_sound h.2.2) (by decide))

/-- The lapse is honest: its own past holds no confirmation. -/
theorem lapse_honest (A : R → Prop) (hl : A L) : Recount.honest parent answers fuse says A p L := by
  refine ⟨hl, ?_⟩
  unfold fuse
  rw [if_neg (no_past A)]
  rfl

/-- WITHOUT the rule. The removed holder's late "confirm", naming only the opener, is
    concurrent with the landing and is counted: the lapsed halt no longer stands. -/
theorem without_rule_removed_key_unseats :
    ¬ Recount.stands parent answers fuse says NoC0 p L := by
  intro hs
  have h : Recount.recounted parent answers NoC0 p L c0 ∨ Recount.recounted parent answers NoC0 p L c2 :=
    Or.inr (Or.inr ⟨by decide, ⟨rfl, rfl⟩, c2_conc⟩)
  have h2 := hs.2
  unfold fuse at h2
  rw [if_pos h] at h2
  exact absurd h2 (by decide)

/-- WITH the rule. The unseat `xh` does not have `c2` in its past: `c2` is not counted and the
    lapse stands. -/
theorem with_rule_lapse_stands :
    F1.standsE parent signer answers fuse says ends E NoC0 p L := by
  refine ⟨lapse_honest NoC0 (by decide), ?_⟩
  have h : ¬ (F1.countedE parent signer answers ends E NoC0 p L c0 ∨
      F1.countedE parent signer answers ends E NoC0 p L c2) := by
    intro h
    cases h with
    | inl h =>
      exact h.elim (fun h => no_past NoC0 (Or.inl h)) (fun h => h.1.1 rfl)
    | inr h =>
      exact h.elim (fun h => no_past NoC0 (Or.inr h))
        (fun h => h.2 ⟨xh, rfl, ⟨rfl, rfl⟩, fun h => absurd (anc_sound h) (by decide)⟩)
  unfold fuse
  rw [if_neg h]
  rfl

/-- The contrast. A "confirm" by the same holder that the removal has in its past (`c0`) is
    still counted under the rule, and the lapse does not stand over it. -/
theorem seen_confirm_still_counted :
    ¬ F1.standsE parent signer answers fuse says ends E All p L := by
  intro hs
  have h : F1.countedE parent signer answers ends E All p L c0 ∨
      F1.countedE parent signer answers ends E All p L c2 :=
    Or.inl (Or.inr ⟨⟨trivial, ⟨rfl, rfl⟩, c0_conc⟩, fun ⟨e, he, _, hn⟩ => by
      have he' : e = xh := he
      subst he'
      exact hn (TransGen.single rfl)⟩)
  have h2 := hs.2
  unfold fuse at h2
  rw [if_pos h] at h2
  exact absurd h2 (by decide)

end F1Rows

/-! ## F2. A landing that does not stand says nothing against one that does

  The window's outcome is read over its frontier landings: the concluded landings that no
  concluded landing names. Before the rule every frontier landing had to stand and agree.
  With it, the outcome is the one outcome stated by the frontier landings that stand. -/

namespace F2

section Rule

variable {Row Out : Type}
variable (parent : Row → Row → Prop)
/- `lands lam p`: `lam` is a landing row of window `p`. `St lam`: the landing stands
   (`Recount.stands` or `F1.standsE`, at the concluded set in use). -/
variable (lands : Row → Row → Prop) (states : Row → Out)

/-- A frontier landing: concluded, and named by no concluded landing of the window. -/
def frontier (A : Row → Prop) (p lam : Row) : Prop :=
  A lam ∧ lands lam p ∧ ¬ ∃ l', A l' ∧ lands l' p ∧ TransGen parent lam l'

/-- THE RULE. The outcome is `o`: a frontier landing that stands states `o`, and every
    frontier landing that stands states `o`. Otherwise the window is contested (or open). -/
def outcomeIs (St A : Row → Prop) (p : Row) (o : Out) : Prop :=
  (∃ lam, frontier parent lands A p lam ∧ St lam ∧ states lam = o) ∧
    ∀ lam, frontier parent lands A p lam → St lam → states lam = o

/-- BEFORE the rule. Every frontier landing stands and states `o`. -/
def outcomeAll (St A : Row → Prop) (p : Row) (o : Out) : Prop :=
  (∃ lam, frontier parent lands A p lam) ∧
    ∀ lam, frontier parent lands A p lam → St lam ∧ states lam = o

theorem outcomeIs_function (St : (Row → Prop) → Row → Prop) (C : (Row → Prop) → Row → Prop)
    (S S' : Row → Prop) (h : ∀ r, S r ↔ S' r) :
    outcomeIs parent lands states (St S) (C S) = outcomeIs parent lands states (St S') (C S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

/-- At most one outcome. -/
theorem outcomeIs_unique (St A : Row → Prop) (p : Row) (o o' : Out)
    (h : outcomeIs parent lands states St A p o) (h' : outcomeIs parent lands states St A p o') :
    o = o' :=
  let ⟨lam, hf, hs, e⟩ := h.1
  e.symm.trans (h'.2 lam hf hs)

/-- The rule only adds outcomes: what was an outcome before is one now. -/
theorem outcomeAll_outcomeIs (St A : Row → Prop) (p : Row) (o : Out)
    (h : outcomeAll parent lands states St A p o) : outcomeIs parent lands states St A p o :=
  let ⟨lam, hf⟩ := h.1
  ⟨⟨lam, hf, (h.2 lam hf).1, (h.2 lam hf).2⟩, fun l hl _ => (h.2 l hl).2⟩

/-- BEFORE the rule: the veto. One concluded frontier landing that does not stand leaves the
    window with no outcome, whatever else stands. -/
theorem veto_before (St A : Row → Prop) (p x : Row)
    (hf : frontier parent lands A p x) (hn : ¬ St x) (o : Out) :
    ¬ outcomeAll parent lands states St A p o :=
  fun h => hn (h.2 x hf).1

/-- The outcome reads the frontier landings that stand, and nothing else. -/
theorem outcome_same (St St' A A' : Row → Prop) (p : Row)
    (h : ∀ lam, (frontier parent lands A' p lam ∧ St' lam) ↔ (frontier parent lands A p lam ∧ St lam))
    (o : Out) :
    outcomeIs parent lands states St' A' p o ↔ outcomeIs parent lands states St A p o :=
  ⟨fun ⟨⟨lam, hf, hs, e⟩, hall⟩ =>
      ⟨⟨lam, ((h lam).1 ⟨hf, hs⟩).1, ((h lam).1 ⟨hf, hs⟩).2, e⟩,
       fun l hl hsl => hall l ((h l).2 ⟨hl, hsl⟩).1 ((h l).2 ⟨hl, hsl⟩).2⟩,
   fun ⟨⟨lam, hf, hs, e⟩, hall⟩ =>
      ⟨⟨lam, ((h lam).2 ⟨hf, hs⟩).1, ((h lam).2 ⟨hf, hs⟩).2, e⟩,
       fun l hl hsl => hall l ((h l).1 ⟨hl, hsl⟩).1 ((h l).1 ⟨hl, hsl⟩).2⟩⟩

/-- THE RULE'S THEOREM, abstractly. A row `x` enters the concluded set. Every other row is
    concluded as before and every other landing stands as before; `x` does not stand; `x`
    names no frontier landing that stands. Then the window has the outcome it had, and has
    one exactly when it had one. -/
theorem nonstanding_moves_nothing (St St' A A' : Row → Prop) (p x : Row)
    (hA : ∀ r, r ≠ x → (A' r ↔ A r)) (hAx : ¬ A x)
    (hSt : ∀ lam, lam ≠ x → (St' lam ↔ St lam)) (hnx : ¬ St' x)
    (hbeside : ∀ lam, frontier parent lands A p lam → St lam → ¬ TransGen parent lam x)
    (o : Out) :
    outcomeIs parent lands states St' A' p o ↔ outcomeIs parent lands states St A p o := by
  apply outcome_same
  intro lam
  constructor
  · intro ⟨⟨ha, hl, hfr⟩, hs⟩
    have hne : lam ≠ x := fun e => hnx (e ▸ hs)
    exact ⟨⟨(hA lam hne).1 ha, hl, fun ⟨l', ha', hl', hanc⟩ =>
      hfr ⟨l', (hA l' (fun e => hAx (e ▸ ha'))).2 ha', hl', hanc⟩⟩, (hSt lam hne).1 hs⟩
  · intro ⟨⟨ha, hl, hfr⟩, hs⟩
    have hne : lam ≠ x := fun e => hAx (e ▸ ha)
    refine ⟨⟨(hA lam hne).2 ha, hl, fun ⟨l', ha', hl', hanc⟩ => ?_⟩, (hSt lam hne).2 hs⟩
    cases Classical.em (l' = x) with
    | inl e => exact hbeside lam ⟨ha, hl, hfr⟩ hs (e ▸ hanc)
    | inr hne' => exact hfr ⟨l', (hA l' hne').1 ha', hl', hanc⟩

end Rule

section Recounted

variable {Row Key Out : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key)
variable (answers : Row → Row → Prop)
variable (outcome : (Row → Prop) → Out) (states : Row → Out)
variable (ends : Row → Key → Prop) (lands : Row → Row → Prop)

/-- A row that is not an answer to `p`, entering the concluded set, changes whether no other
    landing of `p` stands. -/
theorem standsE_off (E A A' : Row → Prop) (p x lam : Row)
    (hA : ∀ r, r ≠ x → (A' r ↔ A r)) (hna : ¬ answers x p) (hne : lam ≠ x) :
    F1.standsE parent signer answers outcome states ends E A' p lam ↔
      F1.standsE parent signer answers outcome states ends E A p lam := by
  have e1 : Recount.pastAns parent answers A' p lam = Recount.pastAns parent answers A p lam :=
    funext fun w => propext
      ⟨fun ⟨a, o, h⟩ => ⟨(hA w (fun e => hna (e ▸ o))).1 a, o, h⟩,
       fun ⟨a, o, h⟩ => ⟨(hA w (fun e => hna (e ▸ o))).2 a, o, h⟩⟩
  have e2 : Recount.concAns parent answers A' p lam = Recount.concAns parent answers A p lam :=
    funext fun w => propext
      ⟨fun ⟨a, o, h⟩ => ⟨(hA w (fun e => hna (e ▸ o))).1 a, o, h⟩,
       fun ⟨a, o, h⟩ => ⟨(hA w (fun e => hna (e ▸ o))).2 a, o, h⟩⟩
  unfold F1.standsE F1.countedE Recount.honest
  rw [e1, e2]
  exact ⟨fun h => ⟨⟨(hA lam hne).1 h.1.1, h.1.2⟩, h.2⟩, fun h => ⟨⟨(hA lam hne).2 h.1.1, h.1.2⟩, h.2⟩⟩

variable (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (C : (Row → Prop) → Row → Prop)

/-- THE RULE'S THEOREM, over recount (with endings; take `E` empty for plain recount). A new
    row `x`, with nothing held waiting on it, that is not an answer to `p`, that names no
    frontier landing that stands, and that does not itself stand as a landing of `p`: the
    window's outcome is what it was. One entitled key signing a landing that does not stand
    beside one that does moves nothing. -/
theorem rival_cannot_move
    (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
    (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
      (C S r ↔ C (fun q => S q ∨ q = x) r))
    (E S : Row → Prop) (p x : Row) (hx : ¬ S x) (hnew : ∀ w, S w → ¬ TransGen parent x w)
    (hna : ¬ answers x p)
    (hbeside : ∀ lam, frontier parent lands (C S) p lam →
      F1.standsE parent signer answers outcome states ends E (C S) p lam → ¬ TransGen parent lam x)
    (hns : ¬ F1.standsE parent signer answers outcome states ends E (C (fun q => S q ∨ q = x)) p x)
    (o : Out) :
    outcomeIs parent lands states
        (F1.standsE parent signer answers outcome states ends E (C (fun q => S q ∨ q = x)) p)
        (C (fun q => S q ∨ q = x)) p o ↔
      outcomeIs parent lands states
        (F1.standsE parent signer answers outcome states ends E (C S) p) (C S) p o := by
  have hA := Kernel.concl_same_off parent wf wellFormed C hCk hfin S x hx hnew
  have hAx : ¬ C S x := fun h => hx (kept_offered parent wf wellFormed S x (hCk S x h))
  exact nonstanding_moves_nothing parent lands states _ _ (C S) _ p x hA hAx
    (fun lam hne => standsE_off parent signer answers outcome states ends E (C S) _ p x lam hA hna hne)
    hns hbeside o

end Recounted

end F2

/-! ### F2, the witness (attacks.py test 13)

  `p`: h1 halts. `c2`: h2 confirms. `r`, `L`: h2's receipt and landing "confirmed", naming
  `c2`. `r3`, `L3`: h3's receipt and landing "lapsed", naming only the opener. -/

namespace F2Rows

inductive R | p | c2 | r | L | r3 | L3
  deriving DecidableEq, Repr

inductive Out | confirmed | lapsed
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | p, c2 => true | p, r => true | p, r3 => true | c2, L => true | r, L => true | r3, L3 => true
  | _, _ => false
def parent (a b : R) : Prop := parentB a b = true

def ancB : R → R → Bool
  | p, c2 => true | p, r => true | p, r3 => true | p, L => true | p, L3 => true
  | c2, L => true | r, L => true | r3, L3 => true
  | _, _ => false

theorem anc_step1 : ∀ a b, parent a b → ancB a b = true := by
  intro a b; cases a <;> cases b <;> simp [parent, parentB, ancB]

theorem anc_step2 : ∀ a b c, ancB a b = true → parent b c → ancB a c = true := by
  intro a b c; cases a <;> cases b <;> cases c <;> simp [parent, parentB, ancB]

theorem anc_sound {a b : R} (h : TransGen parent a b) : ancB a b = true := by
  induction h with
  | single h => exact anc_step1 _ _ h
  | tail _ h ih => exact anc_step2 _ _ _ ih h

def ansB : R → Bool | c2 => true | _ => false
def answers (x q : R) : Prop := ansB x = true ∧ q = p

def landB : R → Bool | L => true | L3 => true | _ => false
def lands (lam q : R) : Prop := landB lam = true ∧ q = p

open Classical in
noncomputable def fuse (X : R → Prop) : Out := if X c2 then Out.confirmed else Out.lapsed

def states : R → Out | L => Out.confirmed | _ => Out.lapsed

def All (_ : R) : Prop := True
/-- The rows before the rival landing is signed. -/
abbrev Before (x : R) : Prop := x ≠ L3

theorem c2_past (A : R → Prop) (h : A c2) : Recount.pastAns parent answers A p L c2 :=
  ⟨h, ⟨rfl, rfl⟩, TransGen.single rfl⟩

/-- The confirmed landing stands, with or without the rival. -/
theorem L_stands (A : R → Prop) (hl : A L) (hc : A c2) :
    Recount.stands parent answers fuse states A p L := by
  refine ⟨⟨hl, ?_⟩, ?_⟩
  · unfold fuse
    rw [if_pos (c2_past A hc)]
    rfl
  · have h : Recount.recounted parent answers A p L c2 := Or.inl (c2_past A hc)
    unfold fuse
    rw [if_pos h]
    rfl

/-- The rival is a concluded landing in its own right: its past holds no confirmation and
    the table over its past gives "lapsed". -/
theorem L3_honest : Recount.honest parent answers fuse states All p L3 := by
  refine ⟨trivial, ?_⟩
  have h : ¬ Recount.pastAns parent answers All p L3 c2 :=
    fun h => absurd (anc_sound h.2.2) (by decide)
  unfold fuse
  rw [if_neg h]
  rfl

/-- And it does not stand: the confirmation is concurrent with it. -/
theorem L3_does_not_stand : ¬ Recount.stands parent answers fuse states All p L3 := by
  intro hs
  have h : Recount.recounted parent answers All p L3 c2 :=
    Or.inr ⟨trivial, ⟨rfl, rfl⟩, fun h => absurd (anc_sound h) (by decide),
      fun h => absurd (anc_sound h) (by decide), by decide⟩
  have h2 := hs.2
  unfold fuse at h2
  rw [if_pos h] at h2
  exact absurd h2 (by decide)

theorem L_frontier (A : R → Prop) (hl : A L) : F2.frontier parent lands A p L :=
  ⟨hl, ⟨rfl, rfl⟩, fun ⟨l', _, _, ha⟩ => by
    have := anc_sound ha
    cases l' <;> simp [ancB] at this⟩

theorem L3_frontier : F2.frontier parent lands All p L3 :=
  ⟨trivial, ⟨rfl, rfl⟩, fun ⟨l', _, _, ha⟩ => by
    have := anc_sound ha
    cases l' <;> simp [ancB] at this⟩

/-- Before the rival is signed the halt is confirmed, under the old reading too. -/
theorem before_rival_confirmed :
    F2.outcomeAll parent lands states (Recount.stands parent answers fuse states Before p)
      Before p Out.confirmed := by
  refine ⟨⟨L, L_frontier Before (by decide)⟩, fun lam hf => ?_⟩
  cases lam with
  | L => exact ⟨L_stands Before (by decide) (by decide), rfl⟩
  | L3 => exact absurd rfl hf.1
  | p => exact absurd hf.2.1.1 (by decide)
  | c2 => exact absurd hf.2.1.1 (by decide)
  | r => exact absurd hf.2.1.1 (by decide)
  | r3 => exact absurd hf.2.1.1 (by decide)

/-- WITHOUT the rule. One holder's "lapsed" beside the confirmed landing: the window has no
    outcome. The confirmed halt is vetoed by one key. -/
theorem without_rule_vetoed (o : Out) :
    ¬ F2.outcomeAll parent lands states (Recount.stands parent answers fuse states All p) All p o :=
  F2.veto_before parent lands states _ All p L3 L3_frontier L3_does_not_stand o

/-- WITH the rule. The outcome is "confirmed". -/
theorem with_rule_confirmed :
    F2.outcomeIs parent lands states (Recount.stands parent answers fuse states All p)
      All p Out.confirmed := by
  refine ⟨⟨L, L_frontier All trivial, L_stands All trivial trivial, rfl⟩, fun lam hf hs => ?_⟩
  cases lam with
  | L => rfl
  | L3 => exact absurd hs L3_does_not_stand
  | p => exact absurd hf.2.1.1 (by decide)
  | c2 => exact absurd hf.2.1.1 (by decide)
  | r => exact absurd hf.2.1.1 (by decide)
  | r3 => exact absurd hf.2.1.1 (by decide)

end F2Rows

/-! ## F3. A cosignature is a voice only for a row counted over a head it names

  `confGroup` (Seat.lean) counts voices; what a voice is, is its parameter `voice`. Before the
  rule a cosignature row was a voice for any row that named it and stated the same act. The
  rule adds: and the cosignature names every head that row is counted over. -/

namespace F3

section Rule

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (holder : T → Key)
/- `cosigns c o`: `c` is a cosignature row for the act `o` states (the same content). `head o h`:
   `o` is counted over the head `h`. -/
variable (cosigns : Row → Row → Prop) (head : Row → Row → Prop)

/-- BEFORE the rule: the row itself (its signer's voice), or a cosignature of its act that it
    names. -/
def voice0 (v o : Row) : Prop := v = o ∨ (cosigns v o ∧ parent v o)

/-- THE RULE: and the cosignature names every head the row is counted over. -/
def voice (v o : Row) : Prop :=
  v = o ∨ (cosigns v o ∧ parent v o ∧ ∀ h, head o h → parent h v)

theorem voice_voice0 (v o : Row) (h : voice parent cosigns head v o) : voice0 parent cosigns v o :=
  h.elim Or.inl (fun h => Or.inr ⟨h.1, h.2.1⟩)

/-- A cosignature that is a voice for a row names each head that row is counted over. -/
theorem voice_names_head (v o h : Row) (hv : voice parent cosigns head v o) (hne : v ≠ o)
    (hh : head o h) : parent h v :=
  hv.elim (fun e => absurd e hne) (fun x => x.2.2 h hh)

/-- A cosignature counted for two rows names the heads of both. Whoever signed it chose
    both heads. -/
theorem two_rows_both_heads (c o1 o2 h1 h2 : Row)
    (hv1 : voice parent cosigns head c o1) (hv2 : voice parent cosigns head c o2)
    (hn1 : c ≠ o1) (hn2 : c ≠ o2) (hh1 : head o1 h1) (hh2 : head o2 h2) :
    parent h1 c ∧ parent h2 c :=
  ⟨voice_names_head parent cosigns head c o1 h1 hv1 hn1 hh1,
   voice_names_head parent cosigns head c o2 h2 hv2 hn2 hh2⟩

/-- A cosignature that names one head is never counted for two different heads. -/
theorem one_head_one_count (c o1 o2 h1 h2 : Row)
    (hone : ∀ h h', (∃ o, head o h) → (∃ o, head o h') → parent h c → parent h' c → h = h')
    (hv1 : voice parent cosigns head c o1) (hv2 : voice parent cosigns head c o2)
    (hn1 : c ≠ o1) (hn2 : c ≠ o2) (hh1 : head o1 h1) (hh2 : head o2 h2) : h1 = h2 :=
  let ⟨a, b⟩ := two_rows_both_heads parent cosigns head c o1 o2 h1 h2 hv1 hv2 hn1 hn2 hh1 hh2
  hone h1 h2 ⟨o1, hh1⟩ ⟨o2, hh2⟩ a b

/-- NO REPLAY ACROSS A REMOVAL. A cosignature in the past of a row `x` (a removal, or any
    later head) is no voice for a row counted over `x`. -/
theorem no_replay (wf : WellFounded parent) (c o x : Row) (hpast : TransGen parent c x)
    (hx : head o x) (hne : c ≠ o) : ¬ voice parent cosigns head c o :=
  fun hv => wf_asymm (WellFounded.transGen wf) c x hpast
    (TransGen.single (voice_names_head parent cosigns head c o x hv hne hx))

variable (member : T → Row → Prop) (need : T → Nat)

/-- A row whose only voice is its own signer's does not meet a count of two or more. -/
theorem lone_voice_not_counted (Q : T → Prop) (A : Row → Prop) (o : Row) (t : T)
    (hneed : 2 ≤ need t) (hall : ∀ v, voice parent cosigns head v o → v = o) :
    ¬ confGroup signer holder (voice parent cosigns head) member need Q A o t := by
  intro ⟨l, hp, hn, hv⟩
  have := lone signer (signer o) l hp (fun v hm => by rw [hall v (hv v hm).2.1])
  omega

/-- The replay, at the count. A row counted over `x` whose cosignatures were all given
    before `x` (each is in the past of `x`) does not meet a count of two or more: every one
    of them must be given again, naming `x`. -/
theorem replay_not_counted (wf : WellFounded parent) (Q : T → Prop) (A : Row → Prop)
    (o x : Row) (t : T) (hneed : 2 ≤ need t) (hx : head o x)
    (hold : ∀ c, cosigns c o → parent c o → TransGen parent c x) :
    ¬ confGroup signer holder (voice parent cosigns head) member need Q A o t :=
  lone_voice_not_counted parent signer holder cosigns head member need Q A o t hneed
    (fun v hv => Classical.byContradiction fun hne =>
      no_replay parent cosigns head wf v o x
        (hv.elim (fun e => absurd e hne) (fun h => hold v h.1 h.2.1)) hx hne hv)

end Rule

end F3

/-! ## F4. An offer conferred by a count is not ended by its proposer alone

  `seatBy` (Seat.lean) ends a pair on a withdrawal of the offer by the offer's signer. For an
  offer conferred by one key that is right: the signer is the conferrer. For an offer conferred
  by a count the signer is one voice of several. `shared o` marks an offer whose signer is not
  its sole conferrer; the refined pair `seatByG` ends such an offer on its holder's own
  withdrawal, or on a cut, and on nothing its proposer signs alone. (Rule 5 uses the same mark
  for a founding row that seats its own signer.) -/

namespace F4

section Rule

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (isWd : Row → Prop)
variable (offer : Row → T → Prop) (isAcc : Row → Prop) (holder : T → Key)
variable (shared : Row → Prop)

/-- The offer `o` is ended for seat `t`: a withdrawal row naming `o`, signed by the seat's
    holder (it ends that holder's seat only), or signed by the offer's signer when that signer
    is the sole conferrer. -/
def offEnded (W : Row → Prop) (o : Row) (t : T) : Prop :=
  ∃ w, W w ∧ isWd w ∧ parent o w ∧ (signer w = holder t ∨ (signer w = signer o ∧ ¬ shared o))

/-- The pair (o, a) seats `t`, under the rule. As `seatBy`, with `offEnded` in place of "the
    offer is withdrawn by its signer". -/
def seatByG (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a : Row) : Prop :=
  P o ∧ offer o t ∧ V o t ∧ P a ∧ accLink parent isAcc o a ∧ signer a = holder t ∧
    ¬ offEnded parent signer isWd holder shared W o t ∧ ¬ withdrawn parent signer isWd W a ∧
    ¬ cut o t

def seatG (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) : Prop :=
  ∃ o a, seatByG parent signer isWd offer isAcc holder shared P W V cut t o a

/-- Where the offer's signer is its sole conferrer the refined pair is the pair of Seat.lean,
    less the holder's own withdrawal against the offer (which Seat.lean lets the holder make
    only against its acceptance). -/
theorem unshared_iff (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a : Row)
    (hns : ¬ shared o) :
    seatByG parent signer isWd offer isAcc holder shared P W V cut t o a ↔
      (seatBy parent signer isWd offer isAcc holder P W V cut t o a ∧
        ¬ ∃ w, W w ∧ isWd w ∧ parent o w ∧ signer w = holder t) := by
  constructor
  · intro ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
    exact ⟨⟨h1, h2, h3, h4, h5, h6,
      fun ⟨w, hw, hW⟩ => h7 ⟨w, hW, hw.1, hw.2.1, Or.inr ⟨hw.2.2, hns⟩⟩, h8, h9⟩,
      fun ⟨w, hW, hwd, hp, hs⟩ => h7 ⟨w, hW, hwd, hp, Or.inl hs⟩⟩
  · intro ⟨⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩, hno⟩
    exact ⟨h1, h2, h3, h4, h5, h6,
      fun ⟨w, hW, hwd, hp, hs⟩ => hs.elim (fun hs => hno ⟨w, hW, hwd, hp, hs⟩)
        (fun hs => h7 ⟨w, ⟨hwd, hp, hs.1⟩, hW⟩), h8, h9⟩

/-- BEFORE the rule. The proposer's lone withdrawal of the row it signed ends the seat of
    every key the row seats, whoever conferred it (`Kernel.offer_withdrawal_ends`). -/
theorem before_proposer_ends (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a w : Row)
    (hw : isWd w ∧ parent o w ∧ signer w = signer o) (hW : W w) :
    ¬ seatBy parent signer isWd offer isAcc holder P W V cut t o a :=
  offer_withdrawal_ends parent signer isWd offer isAcc holder P W V cut t o a w hw hW

/-- The holder ends its own seat by withdrawing against the offer. -/
theorem holder_withdrawal_ends (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a w : Row)
    (hW : W w) (hwd : isWd w) (hp : parent o w) (hs : signer w = holder t) :
    ¬ seatByG parent signer isWd offer isAcc holder shared P W V cut t o a :=
  fun h => h.2.2.2.2.2.2.1 ⟨w, hW, hwd, hp, Or.inl hs⟩

/-- Or against its acceptance. -/
theorem acceptance_withdrawal_ends (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (o a w : Row) (hw : wdOf parent signer isWd w a) (hW : W w) :
    ¬ seatByG parent signer isWd offer isAcc holder shared P W V cut t o a :=
  fun h => h.2.2.2.2.2.2.2.1 ⟨w, hw, hW⟩

/-- A counted unseat (a cut) ends it. -/
theorem cut_ends (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a : Row)
    (hc : cut o t) : ¬ seatByG parent signer isWd offer isAcc holder shared P W V cut t o a :=
  fun h => h.2.2.2.2.2.2.2.2 hc

/-- At one set: a pair on a shared offer is live iff its positive part holds, the holder has
    withdrawn neither the offer nor the acceptance, and no cut removes it. No row of the
    proposer's appears. -/
theorem shared_iff (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a : Row)
    (hsh : shared o) :
    seatByG parent signer isWd offer isAcc holder shared P W V cut t o a ↔
      (P o ∧ offer o t ∧ V o t ∧ P a ∧ accLink parent isAcc o a ∧ signer a = holder t ∧
        (¬ ∃ w, W w ∧ isWd w ∧ (parent o w ∨ parent a w) ∧ signer w = holder t) ∧ ¬ cut o t) := by
  constructor
  · intro ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
    refine ⟨h1, h2, h3, h4, h5, h6, fun ⟨w, hW, hwd, hp, hs⟩ => ?_, h9⟩
    cases hp with
    | inl hp => exact h7 ⟨w, hW, hwd, hp, Or.inl hs⟩
    | inr hp => exact h8 ⟨w, ⟨hwd, hp, hs.trans h6.symm⟩, hW⟩
  · intro ⟨h1, h2, h3, h4, h5, h6, h7, h9⟩
    exact ⟨h1, h2, h3, h4, h5, h6,
      fun ⟨w, hW, hwd, hp, hs⟩ => hs.elim (fun hs => h7 ⟨w, hW, hwd, Or.inl hp, hs⟩)
        (fun hs => hs.2 hsh),
      fun ⟨w, hw, hW⟩ => h7 ⟨w, hW, hw.1, Or.inr hw.2.1, hw.2.2.trans h6⟩, h9⟩

variable (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (C : (Row → Prop) → Row → Prop)

/-- THE RULE'S THEOREM: `Kernel.third_key_cannot_end`, refined. For a shared offer the
    proposer is a third key. A pair on a shared offer survives the offer of `x`, provided the
    conferral still holds, no cut newly removes the pair, and no withdrawal row that is `x` or
    was waiting on `x` is signed by the seat's HOLDER. Nothing is asked about the offer's
    signer: `third_key_cannot_end` asks `signer w ≠ signer o` as well. -/
theorem proposer_cannot_end
    (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
    (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
      (C S r ↔ C (fun q => S q ∨ q = x) r))
    (S : Row → Prop) (x : Row) (hx : ¬ S x)
    (V V' cut cut' : Row → T → Prop) (t : T) (o a : Row)
    (hp : seatByG parent signer isWd offer isAcc holder shared (C S) (C S) V cut t o a)
    (hsh : shared o) (hV : V o t → V' o t) (hcut : cut' o t → cut o t)
    (h3 : ∀ w, isWd w → (w = x ∨ TransGen parent x w) → signer w ≠ holder t) :
    seatByG parent signer isWd offer isAcc holder shared (C (fun q => S q ∨ q = x))
      (C (fun q => S q ∨ q = x)) V' cut' t o a := by
  obtain ⟨h1, h2, h3', h4, h5, h6, h7, h8, h9⟩ := hp
  have grow := Kernel.concl_grows parent wf wellFormed C hCk hfin S x hx
  have back : ∀ w, isWd w → signer w = holder t → C (fun q => S q ∨ q = x) w → C S w :=
    fun w hwd hs hc => Kernel.concl_back parent wf wellFormed C hCk hfin S x w hx
      ⟨fun e => h3 w hwd (Or.inl e) hs, fun ha => h3 w hwd (Or.inr ha) hs⟩ hc
  exact ⟨grow o h1, h2, hV h3', grow a h4, h5, h6,
    fun ⟨w, hW, hwd, hpar, hs⟩ => hs.elim
      (fun hs => h7 ⟨w, back w hwd hs hW, hwd, hpar, Or.inl hs⟩) (fun hs => hs.2 hsh),
    fun ⟨w, hw, hW⟩ => h8 ⟨w, hw, back w hw.1 (hw.2.2.trans h6) hW⟩,
    fun hh => h9 (hcut hh)⟩

/-! ### The walk over the refined pair -/

variable (conf : (T → Prop) → (Row → Prop) → Row → T → Prop)

/-- `Kernel.stands`, over the refined pair. -/
def standsG (P W : Row → Prop) (cut : Row → T → Prop) : Nat → T → Prop
  | 0 => seatG parent signer isWd offer isAcc holder shared P W (conf (fun _ => False) P) cut
  | n + 1 => seatG parent signer isWd offer isAcc holder shared P W
      (conf (standsG P W cut n) P) cut

theorem standsG_function (Cc : (Row → Prop) → Row → Prop)
    (cutOf : (Row → Prop) → Row → T → Prop) (S S' : Row → Prop) (h : ∀ r, S r ↔ S' r) :
    standsG parent signer isWd offer isAcc holder shared conf (Cc S) (Cc S) (cutOf S)
      = standsG parent signer isWd offer isAcc holder shared conf (Cc S') (Cc S') (cutOf S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

end Rule

end F4

/-! ### F3 and F4, the witnesses (attacks.py tests 6 and 23)

  One room. `g`: A founds it with B. `cb`: B's cosignature of "admit C", naming the head `g`.
  `w`: A admits C at head `g`, naming `cb`. `ac`: C accepts. `x`: C is removed, counted over
  head `w`. `w2`: after the removal A alone signs "admit C" at head `x`, naming B's OLD
  cosignature `cb`. `cb2`, `w3`: the same with a fresh cosignature that names `x`. `wdw`: A
  alone withdraws the admission `w` it proposed. `wc`: C withdraws its own acceptance. -/

namespace Room

inductive R | g | cb | w | ac | x | w2 | cb2 | w3 | wdw | wc
  deriving DecidableEq, Repr

inductive Key | A | B | C
  deriving DecidableEq, Repr

/-- The member seats. -/
inductive T | mA | mB | mC
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | g, cb => true | g, w => true | cb, w => true | w, ac => true | w, x => true
  | x, w2 => true | cb, w2 => true | x, cb2 => true | x, w3 => true | cb2, w3 => true
  | w, wdw => true | ac, wc => true
  | _, _ => false
def parent (a b : R) : Prop := parentB a b = true

def signer : R → Key
  | g => Key.A | cb => Key.B | w => Key.A | ac => Key.C | x => Key.A | w2 => Key.A
  | cb2 => Key.B | w3 => Key.A | wdw => Key.A | wc => Key.C

def holder : T → Key | T.mA => Key.A | T.mB => Key.B | T.mC => Key.C

/-- `cb` and `cb2` are cosignatures of the one act "admit C", which `w`, `w2` and `w3` state. -/
def cosignsB : R → R → Bool
  | cb, w => true | cb, w2 => true | cb, w3 => true
  | cb2, w => true | cb2, w2 => true | cb2, w3 => true
  | _, _ => false
def cosigns (c o : R) : Prop := cosignsB c o = true

def headB : R → R → Bool
  | w, g => true | x, w => true | w2, x => true | w3, x => true | _, _ => false
def head (o h : R) : Prop := headB o h = true

def All (_ : R) : Prop := True
/-- At the head `x` the members are A and B; the count is two. -/
def Q (t : T) : Prop := t = T.mA ∨ t = T.mB
def member (_ : T) (_ : R) : Prop := True
def need (_ : T) : Nat := 2

/-- F3 WITHOUT the rule. A's replay `w2`, with B's old cosignature, meets the count. -/
theorem without_rule_replay_counts :
    confGroup signer holder (F3.voice0 parent cosigns) member need Q All w2 T.mC :=
  ⟨[w2, cb], by simp [signer], by simp [need], fun v hv => by
    simp only [List.mem_cons, List.mem_singleton, List.not_mem_nil, or_false] at hv
    cases hv with
    | inl e => subst e; exact ⟨trivial, Or.inl rfl, T.mA, Or.inl rfl, rfl, trivial⟩
    | inr e => subst e; exact ⟨trivial, Or.inr ⟨rfl, rfl⟩, T.mB, Or.inr rfl, rfl, trivial⟩⟩

/-- F3 WITH the rule. `cb` does not name `x`, the head `w2` is counted over: `w2` has one
    voice and is not counted. -/
theorem with_rule_replay_not_counted :
    ¬ confGroup signer holder (F3.voice parent cosigns head) member need Q All w2 T.mC := by
  apply F3.lone_voice_not_counted parent signer holder cosigns head member need Q All w2 T.mC
    (Nat.le_refl 2)
  intro v hv
  cases hv with
  | inl e => exact e
  | inr h =>
    have h1 : parentB x v = true := h.2.2 x rfl
    have h2 : parentB v w2 = true := h.2.1
    cases v <;> simp [parentB] at h1 h2

/-- F3, the honest path. With B's fresh cosignature `cb2`, which names `x`, `w3` is counted. -/
theorem with_rule_fresh_counts :
    confGroup signer holder (F3.voice parent cosigns head) member need Q All w3 T.mC :=
  ⟨[w3, cb2], by simp [signer], by simp [need], fun v hv => by
    simp only [List.mem_cons, List.mem_singleton, List.not_mem_nil, or_false] at hv
    cases hv with
    | inl e => subst e; exact ⟨trivial, Or.inl rfl, T.mA, Or.inl rfl, rfl, trivial⟩
    | inr e =>
      subst e
      refine ⟨trivial, Or.inr ⟨rfl, rfl, fun h hh => ?_⟩, T.mB, Or.inr rfl, rfl, trivial⟩
      have hh' : headB w3 h = true := hh
      cases h <;> simp [headB] at hh'
      rfl⟩

/-! F4 on the same room. -/

def isWd (r : R) : Prop := r = wdw ∨ r = wc
def isAcc (r : R) : Prop := r = ac
def offerB : R → T → Bool
  | g, T.mA => true | g, T.mB => true | w, T.mC => true | w2, T.mC => true | w3, T.mC => true
  | _, _ => false
def offer (o : R) (t : T) : Prop := offerB o t = true
/-- `w` was conferred by the count. -/
def shared (o : R) : Prop := o = w
def Vt (_ : R) (_ : T) : Prop := True
def noCut (_ : R) (_ : T) : Prop := False

/-- The room before the removal, with A's lone withdrawal of the admission. -/
def S1 (r : R) : Prop := r = g ∨ r = cb ∨ r = w ∨ r = ac ∨ r = wdw
/-- The same with C's own withdrawal instead. -/
def S2 (r : R) : Prop := r = g ∨ r = cb ∨ r = w ∨ r = ac ∨ r = wc

/-- F4 WITHOUT the rule. A alone withdraws the admission that A and B counted: C has no
    seat, by any pair. -/
theorem without_rule_proposer_removes :
    ¬ seat parent signer isWd offer isAcc holder S1 S1 Vt noCut T.mC := by
  intro ⟨o, a, h⟩
  have ho : offerB o T.mC = true := h.2.1
  have hP : S1 o := h.1
  have e : o = w := by
    cases o <;> simp [offerB] at ho <;> simp [S1] at hP <;> rfl
  subst e
  exact h.2.2.2.2.2.2.1 ⟨wdw, ⟨Or.inl rfl, rfl, rfl⟩, by simp [S1]⟩

/-- F4 WITH the rule. The same rows: C is seated. -/
theorem with_rule_proposer_ends_nothing :
    F4.seatByG parent signer isWd offer isAcc holder shared S1 S1 Vt noCut T.mC w ac := by
  refine ⟨by simp [S1], rfl, trivial, by simp [S1], Or.inl ⟨rfl, rfl⟩, rfl, ?_, ?_, fun h => h⟩
  · intro ⟨v, hS, hwd, hp, hs⟩
    cases hs with
    | inl hs =>
      have hp' : parentB w v = true := hp
      cases v <;> simp [isWd] at hwd <;> simp [parentB] at hp' <;> simp [signer, holder] at hs
    | inr hs => exact hs.2 rfl
  · intro ⟨v, hw, hS⟩
    have hp' : parentB ac v = true := hw.2.1
    cases v <;> simp [parentB] at hp' <;> simp [S1] at hS

/-- F4, the holder's voice. C's own withdrawal still ends C's seat. -/
theorem with_rule_holder_still_ends :
    ¬ F4.seatG parent signer isWd offer isAcc holder shared S2 S2 Vt noCut T.mC := by
  intro ⟨o, a, h⟩
  have ho : offerB o T.mC = true := h.2.1
  have hP : S2 o := h.1
  have e : o = w := by
    cases o <;> simp [offerB] at ho <;> simp [S2] at hP <;> rfl
  subst e
  have hl := h.2.2.2.2.1
  have hs : signer a = Key.C := h.2.2.2.2.2.1
  have ea : a = ac := by
    cases hl with
    | inl hl => exact hl.1
    | inr e => subst e; simp [signer] at hs
  subst ea
  exact h.2.2.2.2.2.2.2.1 ⟨wc, ⟨Or.inr rfl, rfl, rfl⟩, by simp [S2]⟩

end Room

/-! ### F3, the second witness: leave, join, leave (attacks.py test 6, first part)

  `o1`, `a1`: A seats K, K accepts. `wd1`: K withdraws its acceptance. `o2`, `a2`: A offers
  again, naming the withdrawal, and K accepts again. `wd3`: K signs a second withdrawal on the
  old branch, naming only the first acceptance. The second pair is live: a withdrawal ends the
  row it names and no other. This needs none of the seven rules; it is `Kernel.seatBy` as it
  was. -/

namespace Leave

inductive R | o1 | a1 | wd1 | o2 | a2 | wd3
  deriving DecidableEq, Repr

inductive Key | A | K
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | o1, a1 => true | a1, wd1 => true | wd1, o2 => true | o2, a2 => true | a1, wd3 => true
  | _, _ => false
def parent (a b : R) : Prop := parentB a b = true

def signer : R → Key | o1 => Key.A | o2 => Key.A | _ => Key.K
def isWd (r : R) : Prop := r = wd1 ∨ r = wd3
def isAcc (r : R) : Prop := r = a1 ∨ r = a2
def offer (o : R) (_ : Unit) : Prop := o = o1 ∨ o = o2
def holder (_ : Unit) : Key := Key.K
def All (_ : R) : Prop := True
def Vt (_ : R) (_ : Unit) : Prop := True
def noCut (_ : R) (_ : Unit) : Prop := False

/-- The first pair is ended by the first leave. -/
theorem first_pair_ended :
    ¬ seatBy parent signer isWd offer isAcc holder All All Vt noCut () o1 a1 :=
  acceptance_withdrawal_ends parent signer isWd offer isAcc holder All All Vt noCut () o1 a1 wd1
    ⟨Or.inl rfl, rfl, rfl⟩ trivial

/-- The second pair is live, with the late leave on the old branch held. -/
theorem second_pair_live :
    seatBy parent signer isWd offer isAcc holder All All Vt noCut () o2 a2 := by
  refine ⟨trivial, Or.inr rfl, trivial, trivial, Or.inl ⟨Or.inr rfl, rfl⟩, rfl, ?_, ?_, fun h => h⟩
  · intro ⟨v, hw, _⟩
    have hp : parentB o2 v = true := hw.2.1
    have hs : signer v = signer o2 := hw.2.2
    cases v <;> simp [parentB] at hp <;> simp [signer] at hs
  · intro ⟨v, hw, _⟩
    have hp : parentB a2 v = true := hw.2.1
    cases v <;> simp [parentB] at hp

end Leave

/-! ## Axioms used -/

#print axioms pairwise_inj
#print axioms lone
#print axioms F1.standsE_function
#print axioms F1.standsE_perm
#print axioms F1.countedE_anti
#print axioms F1.seen_counted
#print axioms F1.all_seen_is_recount
#print axioms F1.no_endings_is_recount
#print axioms F1.ended_after_never_counted
#print axioms F1.ended_keys_change_nothing
#print axioms F1.ended_key_cannot_unseat
#print axioms F1Rows.without_rule_removed_key_unseats
#print axioms F1Rows.with_rule_lapse_stands
#print axioms F1Rows.seen_confirm_still_counted
#print axioms F2.outcomeIs_function
#print axioms F2.outcomeIs_unique
#print axioms F2.outcomeAll_outcomeIs
#print axioms F2.veto_before
#print axioms F2.outcome_same
#print axioms F2.nonstanding_moves_nothing
#print axioms F2.standsE_off
#print axioms F2.rival_cannot_move
#print axioms F2Rows.L3_honest
#print axioms F2Rows.L3_does_not_stand
#print axioms F2Rows.before_rival_confirmed
#print axioms F2Rows.without_rule_vetoed
#print axioms F2Rows.with_rule_confirmed
#print axioms F3.two_rows_both_heads
#print axioms F3.one_head_one_count
#print axioms F3.no_replay
#print axioms F3.lone_voice_not_counted
#print axioms F3.replay_not_counted
#print axioms Room.without_rule_replay_counts
#print axioms Room.with_rule_replay_not_counted
#print axioms Room.with_rule_fresh_counts
#print axioms F4.unshared_iff
#print axioms F4.before_proposer_ends
#print axioms F4.holder_withdrawal_ends
#print axioms F4.acceptance_withdrawal_ends
#print axioms F4.cut_ends
#print axioms F4.shared_iff
#print axioms F4.proposer_cannot_end
#print axioms F4.standsG_function
#print axioms Room.without_rule_proposer_removes
#print axioms Room.with_rule_proposer_ends_nothing
#print axioms Room.with_rule_holder_still_ends
#print axioms Leave.first_pair_ended
#print axioms Leave.second_pair_live

end Harden

end Kernel
