/-
  Carry.lean — a row leaves its room only by its own signer's act

  Harden2.lean F6 gives the audience as a least fixed point: a row `d` that names `r` adds its
  audience to `r`'s when `d` is concluded and `d`'s signer is already in `r`'s audience. Under
  that rule a member of a room carries another member's signed row to any audience by naming it
  from elsewhere.

  This file narrows the rule. A naming row carries only when it is a row of the same room, or
  is signed by the signer of the row it names. Widening who sees a row is its author's to
  give, and no other member's.

  Proved: the narrowed audience is inside the old one; where no author has named a row of its
  own from another room, no key outside a room's own audiences is in the audience of any of its
  rows; rows by other keys in other rooms change no audience; the author's own naming row from
  another room does carry.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Harden2.lean.
-/

import Harden2

namespace Kernel

namespace Carry

open Harden

section Rule

variable {Row Key Rm : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (own : Row → Key → Prop)
variable (room : Row → Rm)

/-- `d` may carry `r`: it is a row of the same room, or its signer signed `r`. -/
def may (r d : Row) : Prop := room d = room r ∨ signer d = signer r

/-- THE RULE. `A` is the concluded set. -/
inductive AudR (A : Row → Prop) : Row → Key → Prop
  | base {r : Row} {k : Key} : own r k → AudR A r k
  | carry {r d : Row} {k : Key} : parent r d → A d → may signer room r d →
      AudR A r (signer d) → AudR A d k → AudR A r k

/-- The narrowed rule only narrows. -/
theorem AudR_sub_Aud (A : Row → Prop) :
    ∀ r k, AudR parent signer own room A r k → F6.Aud parent signer own A r k := by
  intro r k h
  induction h with
  | base h => exact F6.Aud.base h
  | carry hp hA _ _ _ ih1 ih2 => exact F6.Aud.carry hp hA ih1 ih2

/-- It is a fixed point. -/
theorem AudR_fix (A : Row → Prop) (r : Row) (k : Key) :
    AudR parent signer own room A r k ↔
      (own r k ∨ ∃ d, parent r d ∧ A d ∧ may signer room r d ∧
        AudR parent signer own room A r (signer d) ∧ AudR parent signer own room A d k) := by
  constructor
  · intro h
    cases h with
    | base h => exact Or.inl h
    | carry hp hA hm h1 h2 => exact Or.inr ⟨_, hp, hA, hm, h1, h2⟩
  · intro h
    cases h with
    | inl h => exact AudR.base h
    | inr h =>
      have ⟨_, hp, hA, hm, h1, h2⟩ := h
      exact AudR.carry hp hA hm h1 h2

/-- `k` is in the own audience of some row of room `ρ`: a member at some head of it, a signer
    of one of its rows, or a key one of its rows names. -/
def inRoom (ρ : Rm) (k : Key) : Prop := ∃ r, room r = ρ ∧ own r k

/-- NOTHING LEAVES. Suppose no concluded row names a row of its own signer from another room.
    Then every key in the audience of a row is in the own audience of some row of that row's
    room. No member carries another member's row out. -/
theorem nothing_leaves (A : Row → Prop)
    (hauthor : ∀ r d, parent r d → A d → signer d = signer r → room d = room r) :
    ∀ r k, AudR parent signer own room A r k → inRoom own room (room r) k := by
  intro r k h
  induction h with
  | base h => exact ⟨_, rfl, h⟩
  | carry hp hA hm _ _ _ ih2 =>
    have e := hm.elim id (hauthor _ _ hp hA)
    exact e ▸ ih2

/-- ROWS BY OTHERS ELSEWHERE CHANGE NOTHING. Let `A'` be `A` with further concluded rows, each
    of which, for every row it names, sits in another room and is signed by another key. Then
    every audience at `A'` is the audience at `A`. -/
theorem others_elsewhere_change_nothing (A A' : Row → Prop)
    (hnew : ∀ d, A' d → A d ∨ ∀ r, parent r d → room d ≠ room r ∧ signer d ≠ signer r) :
    ∀ r k, AudR parent signer own room A' r k → AudR parent signer own room A r k := by
  intro r k h
  induction h with
  | base h => exact AudR.base h
  | carry hp hA' hm _ _ ih1 ih2 =>
    cases hnew _ hA' with
    | inl hA => exact AudR.carry hp hA hm ih1 ih2
    | inr hx => exact (hm.elim (hx _ hp).1 (hx _ hp).2).elim

/-- THE AUTHOR CARRIES. A concluded row by `r`'s own signer that names `r`, from any room,
    adds its audience to `r`'s, the signer being in `r`'s own audience. -/
theorem author_carries (A : Row → Prop) (r d : Row) (k : Key) (hp : parent r d) (hA : A d)
    (hs : signer d = signer r) (hown : own r (signer r))
    (hk : AudR parent signer own room A d k) : AudR parent signer own room A r k :=
  AudR.carry hp hA (Or.inr hs) (hs ▸ AudR.base hown) hk

/-- INSIDE ONE ROOM THE RULE IS THE OLD ONE. Where every naming row sits in the room of the row
    it names, the narrowed audience is the audience of Harden2 F6: a reply still carries the row
    it answers, and a joiner keeps its own admission. -/
theorem same_room_unchanged (A : Row → Prop) (hroom : ∀ r d, parent r d → room d = room r) :
    ∀ r k, F6.Aud parent signer own A r k → AudR parent signer own room A r k := by
  intro r k h
  induction h with
  | base h => exact AudR.base h
  | carry hp hA _ _ ih1 ih2 => exact AudR.carry hp hA (Or.inl (hroom _ _ hp)) ih1 ih2

end Rule

end Carry

#print axioms Carry.AudR_sub_Aud
#print axioms Carry.AudR_fix
#print axioms Carry.nothing_leaves
#print axioms Carry.others_elsewhere_change_nothing
#print axioms Carry.author_carries
#print axioms Carry.same_room_unchanged

end Kernel
