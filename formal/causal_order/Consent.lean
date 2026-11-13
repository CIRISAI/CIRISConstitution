/-
  Consent.lean — one act: a voice consents to what binds it

  Seat.lean defines the seat as an offer by a conferrer and an acceptance by the holder. This file
  states the act beneath it and proves the seat is a case of it, not a second object.

  A relation `t` BINDS some voices. A CONSENT to `t` is a row by one voice it binds. The relation
  stands when every voice it binds has a concluded consent, none withdrawn by its own signer, and the
  consents are tied by naming: one is the root and each other one names it.

    one voice bound    one row carries it                         (a permission, a reader's edge)
    two voices bound   two rows, one naming the other             (a seat, in either order)

  The number of voices is not a parameter. It is read off who the relation binds.

  Proved here: nobody is bound by the rows of others; rows by a voice the relation does not bind
  change nothing; any bound voice ends it alone and no one else does; with one voice bound one row is
  enough; with two it is two rows in either order, and with the conferrer's row as the root it is
  exactly `Kernel.seat`. Where a body places the duty, the body is one party and its consent is a
  count of its members' rows: the holder's row is still needed, one voice is never a count of
  two, and a body of one with a count of one is the one-key case.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Seat.lean.
-/

import Seat

namespace Kernel

namespace Consent

open Order Relation Causal

section Act

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (isWd : Row → Prop)
/- `gives r t`: row `r` is a consent to relation `t` that can be a root. `ans a`: row `a` is a
   consent given in answer to another. `binds t k`: `t` binds voice `k`. `ok r t`: the consent is
   its signer's to give (the conferrer may confer; the giver owns what it gives). `cut o t`: a
   counting cut removes the relation rooted at `o`. -/
variable (gives : Row → T → Prop) (ans : Row → Prop) (binds : T → Key → Prop)
variable (ok : Row → T → Prop)

/-- `a` is tied to the root `o`: it is the root, or an answer that names it. This is
    `Kernel.accLink`. -/
def tied (o a : Row) : Prop := (ans a ∧ parent o a) ∨ a = o

/-- Row `a` is voice `k`'s live consent to `t`, tied to root `o`. -/
def consentOf (P W : Row → Prop) (t : T) (o : Row) (k : Key) (a : Row) : Prop :=
  P a ∧ signer a = k ∧ ok a t ∧ tied parent ans o a ∧ ¬ withdrawn parent signer isWd W a

/-- `t` stands on root `o`: the root is a live consent by a bound voice, and every bound voice has
    a live consent tied to it. -/
def standsOn (P W : Row → Prop) (cut : Row → T → Prop) (t : T) (o : Row) : Prop :=
  P o ∧ gives o t ∧ binds t (signer o) ∧ ok o t ∧ ¬ withdrawn parent signer isWd W o ∧
    ¬ cut o t ∧ ∀ k, binds t k → ∃ a, consentOf parent signer isWd ans ok P W t o k a

/-- The relation stands. -/
def stands (P W : Row → Prop) (cut : Row → T → Prop) (t : T) : Prop :=
  ∃ o, standsOn parent signer isWd gives ans binds ok P W cut t o

/-! ### Nobody is bound by the rows of others -/

/-- Every bound voice has signed a concluded row that is its to give. -/
theorem needs_every_bound_voice (P W : Row → Prop) (cut : Row → T → Prop) (t : T)
    (h : stands parent signer isWd gives ans binds ok P W cut t) (k : Key) (hk : binds t k) :
    ∃ a, P a ∧ signer a = k ∧ ok a t :=
  let ⟨_, h⟩ := h
  let ⟨a, ha⟩ := h.2.2.2.2.2.2 k hk
  ⟨a, ha.1, ha.2.1, ha.2.2.1⟩

/-- If one bound voice has signed nothing concluded, the relation does not stand, whatever every
    other key has signed. -/
theorem silent_voice_not_bound (P W : Row → Prop) (cut : Row → T → Prop) (t : T) (k : Key)
    (hk : binds t k) (hs : ∀ a, P a → signer a ≠ k) :
    ¬ stands parent signer isWd gives ans binds ok P W cut t :=
  fun h =>
    let ⟨a, h1, h2, _⟩ :=
      needs_every_bound_voice parent signer isWd gives ans binds ok P W cut t h k hk
    hs a h1 h2

/-! ### Rows by a voice the relation does not bind change nothing -/

/-- Standing reads only rows by bound voices: restrict the positive set and the withdrawal set to
    them and the answer is the same. -/
theorem unbound_rows_change_nothing (P W : Row → Prop) (cut : Row → T → Prop) (t : T) :
    stands parent signer isWd gives ans binds ok P W cut t ↔
    stands parent signer isWd gives ans binds ok (fun r => P r ∧ binds t (signer r))
      (fun r => W r ∧ binds t (signer r)) cut t := by
  constructor
  · intro ⟨o, h1, h2, h3, h4, h5, h6, h7⟩
    refine ⟨o, ⟨h1, h3⟩, h2, h3, h4, fun ⟨w, hw, hW⟩ => h5 ⟨w, hw, hW.1⟩, h6, fun k hk => ?_⟩
    have ⟨a, a1, a2, a3, a4, a5⟩ := h7 k hk
    exact ⟨a, ⟨a1, a2 ▸ hk⟩, a2, a3, a4, fun ⟨w, hw, hW⟩ => a5 ⟨w, hw, hW.1⟩⟩
  · intro ⟨o, h1, h2, h3, h4, h5, h6, h7⟩
    refine ⟨o, h1.1, h2, h3, h4, fun ⟨w, hw, hW⟩ => h5 ⟨w, hw, hW, ?_⟩, h6, fun k hk => ?_⟩
    · have e : signer w = signer o := hw.2.2
      exact e ▸ h3
    · have ⟨a, a1, a2, a3, a4, a5⟩ := h7 k hk
      refine ⟨a, a1.1, a2, a3, a4, fun ⟨w, hw, hW⟩ => a5 ⟨w, hw, hW, ?_⟩⟩
      have e : signer w = signer a := hw.2.2
      exact e ▸ a2 ▸ hk

/-! ### Any bound voice ends it alone, and no one else does -/

/-- A voice's withdrawal of its consent ends that consent. -/
theorem withdrawal_ends (P W : Row → Prop) (t : T) (o : Row) (k : Key) (a w : Row)
    (hw : wdOf parent signer isWd w a) (hW : W w) :
    ¬ consentOf parent signer isWd ans ok P W t o k a :=
  fun h => h.2.2.2.2 ⟨w, hw, hW⟩

/-- The root's own withdrawal ends the relation on that root. -/
theorem root_withdrawal_ends (P W : Row → Prop) (cut : Row → T → Prop) (t : T) (o w : Row)
    (hw : wdOf parent signer isWd w o) (hW : W w) :
    ¬ standsOn parent signer isWd gives ans binds ok P W cut t o :=
  fun h => h.2.2.2.2.1 ⟨w, hw, hW⟩

/-- A withdrawal that ends a consent is signed by the voice that gave it. -/
theorem ending_signer_is_bound (P W : Row → Prop) (t : T) (o : Row) (k : Key) (a w : Row)
    (h : consentOf parent signer isWd ans ok P W t o k a)
    (hw : wdOf parent signer isWd w a) : signer w = k :=
  hw.2.2.trans h.2.1

/-- With no new withdrawal by a bound voice and no new cut, the relation still stands on the same
    root: more rows, by anyone, end nothing. -/
theorem only_bound_voices_end (P P' W W' : Row → Prop) (cut cut' : Row → T → Prop) (t : T)
    (o : Row) (hP : ∀ r, P r → P' r) (hc : cut' o t → cut o t)
    (hW : ∀ w, W' w → binds t (signer w) → W w)
    (h : standsOn parent signer isWd gives ans binds ok P W cut t o) :
    standsOn parent signer isWd gives ans binds ok P' W' cut' t o := by
  have ⟨h1, h2, h3, h4, h5, h6, h7⟩ := h
  refine ⟨hP o h1, h2, h3, h4, fun ⟨w, hw, hW'⟩ => h5 ⟨w, hw, hW w hW' ?_⟩,
    fun c => h6 (hc c), fun k hk => ?_⟩
  · have e : signer w = signer o := hw.2.2
    exact e ▸ h3
  · have ⟨a, a1, a2, a3, a4, a5⟩ := h7 k hk
    refine ⟨a, hP a a1, a2, a3, a4, fun ⟨w, hw, hW'⟩ => a5 ⟨w, hw, hW w hW' ?_⟩⟩
    have e : signer w = signer a := hw.2.2
    exact e ▸ a2 ▸ hk

/-! ### One voice bound: one row -/

/-- When `t` binds one voice, it stands exactly when that voice has one concluded consent that is
    its to give, not withdrawn and not cut. No second voice is asked. -/
theorem one_voice_one_row (P W : Row → Prop) (cut : Row → T → Prop) (t : T) (g : Key)
    (hb : ∀ k, binds t k ↔ k = g) :
    stands parent signer isWd gives ans binds ok P W cut t ↔
    ∃ o, P o ∧ gives o t ∧ signer o = g ∧ ok o t ∧
      ¬ withdrawn parent signer isWd W o ∧ ¬ cut o t := by
  constructor
  · intro ⟨o, h1, h2, h3, h4, h5, h6, _⟩
    exact ⟨o, h1, h2, (hb _).1 h3, h4, h5, h6⟩
  · intro ⟨o, h1, h2, h3, h4, h5, h6⟩
    refine ⟨o, h1, h2, (hb _).2 h3, h4, h5, h6, fun k hk => ?_⟩
    exact ⟨o, h1, h3.trans ((hb k).1 hk).symm, h4, Or.inr rfl, h5⟩

/-! ### Two voices bound: two rows, in either order -/

/-- When `t` binds two different voices, it stands exactly when one of them signed a live root
    and the other a live consent tied to it. Which of the two signed first is not fixed: the
    conferrer may offer and the holder accept, or the holder ask and the conferrer answer. -/
theorem two_voices_two_rows (P W : Row → Prop) (cut : Row → T → Prop) (t : T) (c h : Key)
    (hne : c ≠ h) (hb : ∀ k, binds t k ↔ k = c ∨ k = h) :
    stands parent signer isWd gives ans binds ok P W cut t ↔
    ∃ o a, P o ∧ gives o t ∧ ok o t ∧ ¬ withdrawn parent signer isWd W o ∧ ¬ cut o t ∧
      P a ∧ ans a ∧ parent o a ∧ ok a t ∧ ¬ withdrawn parent signer isWd W a ∧
      ((signer o = c ∧ signer a = h) ∨ (signer o = h ∧ signer a = c)) := by
  constructor
  · intro ⟨o, h1, h2, h3, h4, h5, h6, h7⟩
    cases (hb _).1 h3 with
    | inl ec =>
      have ⟨a, a1, a2, a3, a4, a5⟩ := h7 h ((hb h).2 (Or.inr rfl))
      cases a4 with
      | inl l => exact ⟨o, a, h1, h2, h4, h5, h6, a1, l.1, l.2, a3, a5, Or.inl ⟨ec, a2⟩⟩
      | inr e => exact absurd (ec.symm.trans (e ▸ a2)) hne
    | inr eh =>
      have ⟨a, a1, a2, a3, a4, a5⟩ := h7 c ((hb c).2 (Or.inl rfl))
      cases a4 with
      | inl l => exact ⟨o, a, h1, h2, h4, h5, h6, a1, l.1, l.2, a3, a5, Or.inr ⟨eh, a2⟩⟩
      | inr e => exact absurd ((e ▸ a2 : signer o = c).symm.trans eh) hne
  · intro ⟨o, a, h1, h2, h4, h5, h6, a1, a2, a3, a4, a5, hs⟩
    have ho : binds t (signer o) :=
      (hb _).2 (hs.elim (fun x => Or.inl x.1) (fun x => Or.inr x.1))
    refine ⟨o, h1, h2, ho, h4, h5, h6, fun k hk => ?_⟩
    have root : ∀ k, signer o = k → ∃ a, consentOf parent signer isWd ans ok P W t o k a :=
      fun k e => ⟨o, h1, e, h4, Or.inr rfl, h5⟩
    have other : ∀ k, signer a = k → ∃ a, consentOf parent signer isWd ans ok P W t o k a :=
      fun k e => ⟨a, a1, e, a4, Or.inl ⟨a2, a3⟩, a5⟩
    cases (hb k).1 hk with
    | inl ec => exact hs.elim (fun x => root k (x.1.trans ec.symm)) (fun x => other k (x.2.trans ec.symm))
    | inr eh => exact hs.elim (fun x => other k (x.2.trans eh.symm)) (fun x => root k (x.1.trans eh.symm))

end Act

/-! ### The seat is two consents -/

section IsSeat

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (isWd : Row → Prop)
variable (offer : Row → T → Prop) (isAcc : Row → Prop) (holder : T → Key)

/-- `Kernel.seat`, for a seat whose conferrer is one key `c`, is this act with two voices bound,
    the conferrer and the holder, taken with the conferrer's row as the root. A row is a root
    consent to the seat when it is an offer by a key that may confer it (`V`). -/
theorem seat_is_two_consents (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (c : Key)
    (hV : ∀ o, V o t → signer o = c) :
    seat parent signer isWd offer isAcc holder P W V cut t ↔
    ∃ o, signer o = c ∧
      standsOn parent signer isWd (fun r t => offer r t ∧ V r t) isAcc
        (fun t k => k = c ∨ k = holder t) (fun _ _ => True) P W cut t o := by
  constructor
  · intro ⟨o, a, h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
    have ec := hV o h3
    refine ⟨o, ec, h1, ⟨h2, h3⟩, Or.inl ec, trivial, h7, h9, fun k hk => ?_⟩
    cases hk with
    | inl e => exact ⟨o, h1, ec.trans e.symm, trivial, Or.inr rfl, h7⟩
    | inr e => exact ⟨a, h4, h6.trans e.symm, trivial, h5, h8⟩
  · intro ⟨o, _, h1, h2, _, _, h5, h6, h7⟩
    have ⟨a, a1, a2, _, a4, a5⟩ := h7 (holder t) (Or.inr rfl)
    exact ⟨o, a, h1, h2.1, h2.2, a1, a4, a2, h5, a5, h6⟩

/-- The same seat with the holder's row as the root is the same act: the holder asks, the
    conferrer answers by naming the request. Standing does not depend on who signed first. -/
theorem holder_first_stands (P W : Row → Prop) (cut : Row → T → Prop) (t : T) (c : Key)
    (gives : Row → T → Prop) (ok : Row → T → Prop) (hne : c ≠ holder t) (o a : Row)
    (ho : P o ∧ gives o t ∧ ok o t ∧ signer o = holder t ∧
      ¬ withdrawn parent signer isWd W o ∧ ¬ cut o t)
    (ha : P a ∧ isAcc a ∧ parent o a ∧ ok a t ∧ signer a = c ∧
      ¬ withdrawn parent signer isWd W a) :
    stands parent signer isWd gives isAcc (fun t k => k = c ∨ k = holder t) ok P W cut t :=
  (two_voices_two_rows parent signer isWd gives isAcc (fun t k => k = c ∨ k = holder t) ok
    P W cut t c (holder t) hne (fun _ => Iff.rfl)).2
    ⟨o, a, ho.1, ho.2.1, ho.2.2.1, ho.2.2.2.2.1, ho.2.2.2.2.2, ha.1, ha.2.1, ha.2.2.1,
      ha.2.2.2.1, ha.2.2.2.2.2, Or.inr ⟨ho.2.2.2.1, ha.2.2.2.2.1⟩⟩

end IsSeat

/-! ### A body consents by a count -/

section Counted

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (isWd : Row → Prop)
variable (gives : Row → T → Prop) (ans : Row → Prop)
/- `member t k`: `k` is a voice of the body that places `t`, read at the head the root names.
   `need t`: the count the body's protocol asks. `holder t`: the voice that carries `t`. -/
variable (member : T → Key → Prop) (need : T → Nat) (holder : T → Key)

/-- The body consents on root `o`: at least `need` members, no two the same voice, each with a
    live row tied to the root. The body is one party to the relation and this is its consent. -/
def bodyConsents (P W : Row → Prop) (t : T) (o : Row) : Prop :=
  ∃ l : List Row, l.Pairwise (fun a b => signer a ≠ signer b) ∧ need t ≤ l.length ∧
    ∀ a, a ∈ l → P a ∧ member t (signer a) ∧ tied parent ans o a ∧
      ¬ withdrawn parent signer isWd W a

/-- A duty placed by a body stands on root `o`: the body consents by its count and the holder by
    its own row. Two consents, as for a duty placed by one key; one of them is a count. -/
def standsCounted (P W : Row → Prop) (cut : Row → T → Prop) (t : T) (o : Row) : Prop :=
  P o ∧ gives o t ∧ ¬ cut o t ∧ bodyConsents parent signer isWd ans member need P W t o ∧
    ∃ a, consentOf parent signer isWd ans (fun _ _ => True) P W t o (holder t) a

/-- The holder's own row is needed whatever the count: a body seats nobody by its votes alone. -/
theorem count_needs_holder (P W : Row → Prop) (cut : Row → T → Prop) (t : T) (o : Row)
    (hs : ∀ a, P a → signer a ≠ holder t) :
    ¬ standsCounted parent signer isWd gives ans member need holder P W cut t o :=
  fun h => let ⟨a, a1, a2, _⟩ := h.2.2.2.2; hs a a1 a2

/-- Where the count asks two or more, rows by one voice, in any number, are not the body's
    consent. -/
theorem one_voice_is_not_a_count (P W : Row → Prop) (t : T) (o : Row) (h2 : 2 ≤ need t)
    (h1 : ∀ a b, P a → P b → member t (signer a) → member t (signer b) → signer a = signer b) :
    ¬ bodyConsents parent signer isWd ans member need P W t o := by
  intro ⟨l, hp, hn, hl⟩
  match l, hp, hn, hl with
  | [], _, hn, _ => exact Nat.not_succ_le_zero 1 (Nat.le_trans h2 hn)
  | [_], _, hn, _ => exact Nat.not_succ_le_self 1 (Nat.le_trans h2 hn)
  | a :: b :: _, hp, _, hl =>
    cases hp with
    | cons hab _ =>
      have ha := hl a (List.mem_cons_self _ _)
      have hb := hl b (List.mem_cons_of_mem _ (List.mem_cons_self _ _))
      exact hab b (List.mem_cons_self _ _) (h1 a b ha.1 hb.1 ha.2.1 hb.2.1)

/-- Rows by keys that are not members of the body change nothing in its consent. -/
theorem nonmember_rows_change_nothing (P W : Row → Prop) (t : T) (o : Row) :
    bodyConsents parent signer isWd ans member need P W t o ↔
    bodyConsents parent signer isWd ans member need (fun r => P r ∧ member t (signer r))
      (fun r => W r ∧ member t (signer r)) t o := by
  constructor
  · intro ⟨l, hp, hn, hl⟩
    refine ⟨l, hp, hn, fun a ha => ?_⟩
    have ⟨a1, a2, a3, a4⟩ := hl a ha
    exact ⟨⟨a1, a2⟩, a2, a3, fun ⟨w, hw, hW⟩ => a4 ⟨w, hw, hW.1⟩⟩
  · intro ⟨l, hp, hn, hl⟩
    refine ⟨l, hp, hn, fun a ha => ?_⟩
    have ⟨a1, a2, a3, a4⟩ := hl a ha
    refine ⟨a1.1, a2, a3, fun ⟨w, hw, hW⟩ => a4 ⟨w, hw, hW, ?_⟩⟩
    have e : signer w = signer a := hw.2.2
    exact e ▸ a2

/-- More rows, by anyone, end nothing: the body's consent is lost only through a withdrawal by a
    member of its own row. A cut is separate. -/
theorem only_members_withdraw (P P' W W' : Row → Prop) (t : T) (o : Row)
    (hP : ∀ r, P r → P' r) (hW : ∀ w, W' w → member t (signer w) → W w)
    (h : bodyConsents parent signer isWd ans member need P W t o) :
    bodyConsents parent signer isWd ans member need P' W' t o := by
  have ⟨l, hp, hn, hl⟩ := h
  refine ⟨l, hp, hn, fun a ha => ?_⟩
  have ⟨a1, a2, a3, a4⟩ := hl a ha
  refine ⟨hP a a1, a2, a3, fun ⟨w, hw, hW'⟩ => a4 ⟨w, hw, hW w hW' ?_⟩⟩
  have e : signer w = signer a := hw.2.2
  exact e ▸ a2

/-- A body of one voice with a count of one is the consent of that one key: the counted form
    contains the two-row seat. -/
theorem count_of_one_is_one_row (P W : Row → Prop) (t : T) (o : Row) (c : Key)
    (hm : ∀ k, member t k ↔ k = c) (hn : need t = 1) :
    bodyConsents parent signer isWd ans member need P W t o ↔
    ∃ a, P a ∧ signer a = c ∧ tied parent ans o a ∧ ¬ withdrawn parent signer isWd W a := by
  constructor
  · intro ⟨l, _, hlen, hl⟩
    match l, hlen, hl with
    | [], hlen, _ => exact absurd (by rw [hn] at hlen; exact hlen) (Nat.not_succ_le_zero 0)
    | a :: _, _, hl =>
      have ⟨a1, a2, a3, a4⟩ := hl a (List.mem_cons_self _ _)
      exact ⟨a, a1, (hm _).1 a2, a3, a4⟩
  · intro ⟨a, a1, a2, a3, a4⟩
    refine ⟨[a], List.Pairwise.cons (fun _ h => nomatch h) List.Pairwise.nil, by rw [hn]; exact Nat.le_refl 1, fun b hb => ?_⟩
    have e : b = a := by
      cases hb with
      | head => rfl
      | tail _ h => exact nomatch h
    subst e
    exact ⟨a1, (hm _).2 a2, a3, a4⟩

end Counted

end Consent

#print axioms Consent.needs_every_bound_voice
#print axioms Consent.silent_voice_not_bound
#print axioms Consent.unbound_rows_change_nothing
#print axioms Consent.only_bound_voices_end
#print axioms Consent.one_voice_one_row
#print axioms Consent.two_voices_two_rows
#print axioms Consent.seat_is_two_consents
#print axioms Consent.holder_first_stands
#print axioms Consent.count_needs_holder
#print axioms Consent.one_voice_is_not_a_count
#print axioms Consent.nonmember_rows_change_nothing
#print axioms Consent.only_members_withdraw
#print axioms Consent.count_of_one_is_one_row

end Kernel
