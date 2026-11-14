/-
  Seat.lean — the seat and the cut

  Causal.lean gives three layers over the rows a node holds: kept, concluded, derived. This file
  adds two derived answers and proves what the run in formal/causal_kernel only executes.

  Part A. THE SEAT. One shape for every standing: a kept, concluded OFFER by a conferrer naming
          the seat, and a kept, concluded ACCEPTANCE by the seat's holder naming that offer,
          neither withdrawn by its own signer, and no counting cut removing the pair. Who may
          confer is a parameter (`conf`), with three instances: the object's own key, a key
          that itself holds a seat that may confer, and a tally of seated voices.
  Part B. THE CUT. Whether a cut counts refers to itself through negation and two concurrent
          cuts may each depend on the other not counting. The status is the well-founded
          (alternating) fixed point of an antitone operator: counts, contested, void. It is
          defined for every antitone operator with no order on the cuts; where the dependency
          between cuts is well-founded it is two-valued and is the only solution.

  The window and the roster tips are in Window.lean.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Causal.lean.
-/

import Causal

namespace Kernel

open Order Relation Causal

/-! ## Part A. The seat -/

section Seat

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (isWd : Row → Prop)
/- `T` is the type of seats: a seat is (key, scope, object). `offer o t` says row `o` is an
   offer naming seat `t`. `holder t` is the key of the seat. `isAcc a` marks an acceptance. -/
variable (offer : Row → T → Prop) (isAcc : Row → Prop) (holder : T → Key)

/-- `e` has a withdrawal in `W`: a row marked a withdrawal, naming `e`, signed by `e`'s own
    signer (`Causal.wdOf`, the house rule). -/
def withdrawn (W : Row → Prop) (e : Row) : Prop :=
  ∃ w, wdOf parent signer isWd w e ∧ W w

/-- `a` answers offer `o`: an acceptance row that names `o`, or `o` itself. The second case
    can only make a seat when the offer's signer is the seat's holder (`one_row_only_to_self`):
    then the two voices the seat needs are one key, and one row carries both. -/
def accLink (o a : Row) : Prop := (isAcc a ∧ parent o a) ∨ a = o

/-- The pair (o, a) seats `t`. `P` is the set of concluded rows read positively (offers,
    acceptances), `W` the set of concluded rows read as withdrawals; the definition in use has
    `P = W = ` the concluded set, and they are separate only so that monotonicity can be
    stated. `V o t` says the offer's conferrer may confer `t`. `cut o t` says a counting cut
    removes the pair whose offer is `o` from seat `t`. -/
def seatBy (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a : Row) : Prop :=
  P o ∧ offer o t ∧ V o t ∧ P a ∧ accLink parent isAcc o a ∧ signer a = holder t ∧
    ¬ withdrawn parent signer isWd W o ∧ ¬ withdrawn parent signer isWd W a ∧ ¬ cut o t

/-- The seat is live. -/
def seat (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) : Prop :=
  ∃ o a, seatBy parent signer isWd offer isAcc holder P W V cut t o a

/-! ### (2) The two-voice floor -/

/-- No seat without an offer by a conferrer who may confer it. -/
theorem seat_needs_offer (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (h : seat parent signer isWd offer isAcc holder P W V cut t) :
    ∃ o, P o ∧ offer o t ∧ V o t :=
  let ⟨o, _, h⟩ := h
  ⟨o, h.1, h.2.1, h.2.2.1⟩

/-- No seat without a row signed by the seat's own holder. -/
theorem seat_needs_acceptance (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (h : seat parent signer isWd offer isAcc holder P W V cut t) :
    ∃ a, P a ∧ signer a = holder t :=
  let ⟨_, a, h⟩ := h
  ⟨a, h.2.2.2.1, h.2.2.2.2.2.1⟩

/-- Offers by keys that may not confer, in any number, with any acceptances, seat no one. -/
theorem no_offer_no_seat (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (h : ∀ o, P o → offer o t → ¬ V o t) :
    ¬ seat parent signer isWd offer isAcc holder P W V cut t :=
  fun hs =>
    let ⟨o, h1, h2, h3⟩ := seat_needs_offer parent signer isWd offer isAcc holder P W V cut t hs
    h o h1 h2 h3

/-- Rows by keys other than the holder, in any number, seat no one: nobody is seated by
    others alone. -/
theorem no_acceptance_no_seat (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (h : ∀ a, P a → signer a ≠ holder t) :
    ¬ seat parent signer isWd offer isAcc holder P W V cut t :=
  fun hs =>
    let ⟨a, h1, h2⟩ :=
      seat_needs_acceptance parent signer isWd offer isAcc holder P W V cut t hs
    h a h1 h2

/-- One row is both voices only when the offer's signer is the holder. -/
theorem one_row_only_to_self (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o : Row)
    (h : seatBy parent signer isWd offer isAcc holder P W V cut t o o) :
    signer o = holder t :=
  h.2.2.2.2.2.1

/-- When the conferrer is not the holder, the seat rests on two rows: the offer, and a
    separate acceptance row that names it. -/
theorem two_rows_unless_self (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a : Row)
    (h : seatBy parent signer isWd offer isAcc holder P W V cut t o a)
    (hne : signer o ≠ holder t) : a ≠ o ∧ isAcc a ∧ parent o a := by
  have hs : signer a = holder t := h.2.2.2.2.2.1
  cases h.2.2.2.2.1 with
  | inl hl => exact ⟨fun e => hne (e ▸ hs), hl.1, hl.2⟩
  | inr e => exact absurd (e ▸ hs) hne

/-! ### (3) Either side ends it, by its own row -/

/-- The conferrer's withdrawal of the offer ends the pair. It is signed by the offer's
    signer (`wdOf`). -/
theorem offer_withdrawal_ends (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a w : Row)
    (hw : wdOf parent signer isWd w o) (hW : W w) :
    ¬ seatBy parent signer isWd offer isAcc holder P W V cut t o a :=
  fun h => h.2.2.2.2.2.2.1 ⟨w, hw, hW⟩

/-- The holder's withdrawal of the acceptance ends the pair. -/
theorem acceptance_withdrawal_ends (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (o a w : Row) (hw : wdOf parent signer isWd w a) (hW : W w) :
    ¬ seatBy parent signer isWd offer isAcc holder P W V cut t o a :=
  fun h => h.2.2.2.2.2.2.2.1 ⟨w, hw, hW⟩

/-- A withdrawal that ends a pair is signed by the conferrer or by the holder. -/
theorem ending_withdrawal_signer (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (o a w : Row) (h : seatBy parent signer isWd offer isAcc holder P W V cut t o a)
    (hw : wdOf parent signer isWd w o ∨ wdOf parent signer isWd w a) :
    signer w = signer o ∨ signer w = holder t :=
  hw.elim (fun x => Or.inl x.2.2) (fun x => Or.inr (x.2.2.trans h.2.2.2.2.2.1))

/-! ### (4) Monotone in offers and acceptances, antitone only in withdrawals and cuts -/

theorem seatBy_mono (P P' W W' : Row → Prop) (V V' cut cut' : Row → T → Prop)
    (hP : ∀ r, P r → P' r) (hW : ∀ r, W' r → W r)
    (hV : ∀ o t, V o t → V' o t) (hc : ∀ o t, cut' o t → cut o t) (t : T) (o a : Row)
    (h : seatBy parent signer isWd offer isAcc holder P W V cut t o a) :
    seatBy parent signer isWd offer isAcc holder P' W' V' cut' t o a := by
  obtain ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩ := h
  exact ⟨hP o h1, h2, hV o t h3, hP a h4, h5, h6,
    fun ⟨w, hw, hx⟩ => h7 ⟨w, hw, hW w hx⟩,
    fun ⟨w, hw, hx⟩ => h8 ⟨w, hw, hW w hx⟩,
    fun hh => h9 (hc o t hh)⟩

theorem seat_mono (P P' W W' : Row → Prop) (V V' cut cut' : Row → T → Prop)
    (hP : ∀ r, P r → P' r) (hW : ∀ r, W' r → W r)
    (hV : ∀ o t, V o t → V' o t) (hc : ∀ o t, cut' o t → cut o t) (t : T)
    (h : seat parent signer isWd offer isAcc holder P W V cut t) :
    seat parent signer isWd offer isAcc holder P' W' V' cut' t :=
  let ⟨o, a, h⟩ := h
  ⟨o, a, seatBy_mono parent signer isWd offer isAcc holder P P' W W' V V' cut cut'
    hP hW hV hc t o a h⟩

/-! ### Who may confer: one parameter, three instances -/

/-- A conferrer rule. `conf Q A o t`: given the seats `Q` already found live (one step nearer
    the root) and the concluded rows `A`, the offer `o` is by a conferrer who may confer `t`.
    The one thing asked of it is that it reads both positively. -/
def ConfMono (conf : (T → Prop) → (Row → Prop) → Row → T → Prop) : Prop :=
  ∀ (Q Q' : T → Prop) (A A' : Row → Prop), (∀ t, Q t → Q' t) → (∀ r, A r → A' r) →
    ∀ o t, conf Q A o t → conf Q' A' o t

variable (objKey : T → Key) (mayConfer : T → T → Prop)
variable (voice : Row → Row → Prop) (member : T → Row → Prop) (need : T → Nat)

/-- Self-rooted (owner, charter): the offer is signed by the key of the seat's own object. -/
def confSelf (_ : T → Prop) (_ : Row → Prop) (o : Row) (t : T) : Prop :=
  signer o = objKey t

/-- Delegation: the offer's signer holds a live seat `t'` that may confer `t`. -/
def confSingle (Q : T → Prop) (_ : Row → Prop) (o : Row) (t : T) : Prop :=
  ∃ t', Q t' ∧ holder t' = signer o ∧ mayConfer t' t

/-- A group: the offer counts when `need t` concluded voices for it, by distinct signers,
    each hold a live seat that is a member seat for this offer (`member t' o` carries the head
    the offer names). -/
def confGroup (Q : T → Prop) (A : Row → Prop) (o : Row) (t : T) : Prop :=
  ∃ l : List Row, l.Pairwise (fun u v => signer u ≠ signer v) ∧ need t ≤ l.length ∧
    ∀ v, v ∈ l → A v ∧ voice v o ∧ ∃ t', Q t' ∧ holder t' = signer v ∧ member t' o

theorem confSelf_mono : ConfMono (confSelf (T := T) signer objKey) :=
  fun _ _ _ _ _ _ _ _ h => h

theorem confSingle_mono : ConfMono (confSingle (Row := Row) signer holder mayConfer) :=
  fun _ _ _ _ hQ _ _ _ ⟨t', h1, h2, h3⟩ => ⟨t', hQ t' h1, h2, h3⟩

theorem confGroup_mono : ConfMono (confGroup signer holder voice member need) :=
  fun _ _ _ _ hQ hA _ _ ⟨l, h1, h2, h3⟩ =>
    ⟨l, h1, h2, fun v hv =>
      let ⟨a, b, t', c, d, e⟩ := h3 v hv
      ⟨hA v a, b, t', hQ t' c, d, e⟩⟩

/-- Any of the three. -/
theorem conf_or_mono (c1 c2 : (T → Prop) → (Row → Prop) → Row → T → Prop)
    (h1 : ConfMono c1) (h2 : ConfMono c2) :
    ConfMono (fun Q A o t => c1 Q A o t ∨ c2 Q A o t) :=
  fun Q Q' A A' hQ hA o t h =>
    h.elim (fun x => Or.inl (h1 Q Q' A A' hQ hA o t x)) (fun x => Or.inr (h2 Q Q' A A' hQ hA o t x))

/-! ### The walk -/

variable (conf : (T → Prop) → (Row → Prop) → Row → T → Prop)

/-- `stands n t`: seat `t` is live through a chain of at most `n` conferring seats below it.
    At depth 0 the conferrer rule sees no seat, so only a rule that needs none (self-rooted)
    seats anyone. -/
def stands (P W : Row → Prop) (cut : Row → T → Prop) : Nat → T → Prop
  | 0 => seat parent signer isWd offer isAcc holder P W (conf (fun _ => False) P) cut
  | n + 1 => seat parent signer isWd offer isAcc holder P W
      (conf (stands P W cut n) P) cut

/-- (4) The walk is monotone in the rows read positively and antitone in withdrawals and in
    cuts, and in nothing else. -/
theorem stands_mono (hconf : ConfMono conf) (P P' W W' : Row → Prop)
    (cut cut' : Row → T → Prop)
    (hP : ∀ r, P r → P' r) (hW : ∀ r, W' r → W r) (hc : ∀ o t, cut' o t → cut o t) :
    ∀ n t, stands parent signer isWd offer isAcc holder conf P W cut n t →
      stands parent signer isWd offer isAcc holder conf P' W' cut' n t := by
  intro n
  induction n with
  | zero =>
    intro t h
    exact seat_mono parent signer isWd offer isAcc holder P P' W W' _ _ cut cut' hP hW
      (fun o t hv => hconf _ _ _ _ (fun _ x => x) hP o t hv) hc t h
  | succ n ih =>
    intro t h
    exact seat_mono parent signer isWd offer isAcc holder P P' W W' _ _ cut cut' hP hW
      (fun o t hv => hconf _ _ _ _ ih hP o t hv) hc t h

/-- A longer chain allows no less. -/
theorem stands_deeper (hconf : ConfMono conf) (P W : Row → Prop) (cut : Row → T → Prop) :
    ∀ n t, stands parent signer isWd offer isAcc holder conf P W cut n t →
      stands parent signer isWd offer isAcc holder conf P W cut (n + 1) t := by
  intro n
  induction n with
  | zero =>
    intro t h
    exact seat_mono parent signer isWd offer isAcc holder P P W W _ _ cut cut (fun _ x => x)
      (fun _ x => x) (fun o t hv => hconf _ _ _ _ (fun _ x => x.elim) (fun _ x => x) o t hv)
      (fun _ _ x => x) t h
  | succ n ih =>
    intro t h
    exact seat_mono parent signer isWd offer isAcc holder P P W W _ _ cut cut (fun _ x => x)
      (fun _ x => x) (fun o t hv => hconf _ _ _ _ ih (fun _ x => x) o t hv)
      (fun _ _ x => x) t h

/-- (1) Standing is a function of the offered set. `C S` is the concluded set for offered
    set `S`; `cutOf S` is the cut relation for `S`. -/
theorem stands_function (C : (Row → Prop) → Row → Prop)
    (cutOf : (Row → Prop) → Row → T → Prop) (S S' : Row → Prop) (h : ∀ r, S r ↔ S' r) :
    stands parent signer isWd offer isAcc holder conf (C S) (C S) (cutOf S)
      = stands parent signer isWd offer isAcc holder conf (C S') (C S') (cutOf S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

/-- (1) Any arrival order. -/
theorem stands_perm (C : (Row → Prop) → Row → Prop)
    (cutOf : (Row → Prop) → Row → T → Prop) (l l' : List Row) (h : l.Perm l') :
    stands parent signer isWd offer isAcc holder conf (C (fun r => r ∈ l))
        (C (fun r => r ∈ l)) (cutOf (fun r => r ∈ l))
      = stands parent signer isWd offer isAcc holder conf (C (fun r => r ∈ l'))
        (C (fun r => r ∈ l')) (cutOf (fun r => r ∈ l')) :=
  stands_function parent signer isWd offer isAcc holder conf C cutOf _ _ (fun _ => h.mem_iff)

/-! ### (3) Exact locality: what a new row can end -/

variable (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (C : (Row → Prop) → Row → Prop)
variable (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
variable (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
    (C S r ↔ C (fun q => S q ∨ q = x) r))
include hCk hfin

/-- A concluded row stays concluded when a row is offered. -/
theorem concl_grows (S : Row → Prop) (x : Row) (hx : ¬ S x) :
    ∀ r, C S r → C (fun q => S q ∨ q = x) r :=
  fun r h => (hfin S x r (hCk S r h) hx).1 h

/-- A row concluded after `x` is offered, that is not `x` and was not waiting on `x`, was
    concluded before. -/
theorem concl_back (S : Row → Prop) (x w : Row) (hx : ¬ S x)
    (hne : w ≠ x ∧ ¬ TransGen parent x w) (hc : C (fun q => S q ∨ q = x) w) : C S w :=
  (hfin S x w ((kept_new_row parent wf wellFormed S x w hne.1 hne.2).2 (hCk _ w hc)) hx).2 hc

/-- A seating pair survives the offer of `x`, provided the conferrer still may confer, no
    cut newly removes the pair, and no withdrawal of the offer or of the acceptance is `x`
    or was waiting on `x`. -/
theorem pair_survives (S : Row → Prop) (x : Row) (hx : ¬ S x) (V V' cut cut' : Row → T → Prop)
    (t : T) (o a : Row)
    (hp : seatBy parent signer isWd offer isAcc holder (C S) (C S) V cut t o a)
    (hV : V o t → V' o t) (hcut : cut' o t → cut o t)
    (hw : ∀ w, (wdOf parent signer isWd w o ∨ wdOf parent signer isWd w a) →
      w ≠ x ∧ ¬ TransGen parent x w) :
    seatBy parent signer isWd offer isAcc holder (C (fun q => S q ∨ q = x))
      (C (fun q => S q ∨ q = x)) V' cut' t o a := by
  obtain ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩ := hp
  exact ⟨concl_grows parent wf wellFormed C hCk hfin S x hx o h1, h2, hV h3,
    concl_grows parent wf wellFormed C hCk hfin S x hx a h4, h5, h6,
    fun ⟨w, hwd, hc⟩ => h7 ⟨w, hwd,
      concl_back parent wf wellFormed C hCk hfin S x w hx (hw w (Or.inl hwd)) hc⟩,
    fun ⟨w, hwd, hc⟩ => h8 ⟨w, hwd,
      concl_back parent wf wellFormed C hCk hfin S x w hx (hw w (Or.inr hwd)) hc⟩,
    fun hh => h9 (hcut hh)⟩

/-- (3) No third key ends a pair without a cut. If every withdrawal row that is `x` or was
    waiting on `x` is signed by a key that is neither the conferrer nor the holder, the pair
    survives (the conferrer's own standing and the cuts being as they were). -/
theorem third_key_cannot_end (S : Row → Prop) (x : Row) (hx : ¬ S x)
    (V V' cut cut' : Row → T → Prop) (t : T) (o a : Row)
    (hp : seatBy parent signer isWd offer isAcc holder (C S) (C S) V cut t o a)
    (hV : V o t → V' o t) (hcut : cut' o t → cut o t)
    (h3 : ∀ w, isWd w → (w = x ∨ TransGen parent x w) →
      signer w ≠ signer o ∧ signer w ≠ holder t) :
    seatBy parent signer isWd offer isAcc holder (C (fun q => S q ∨ q = x))
      (C (fun q => S q ∨ q = x)) V' cut' t o a := by
  apply pair_survives parent signer isWd offer isAcc holder wf wellFormed C hCk hfin S x hx
    V V' cut cut' t o a hp hV hcut
  intro w hw
  have hs := ending_withdrawal_signer parent signer isWd offer isAcc holder _ _ V cut t o a w hp hw
  have hwd : isWd w := hw.elim (fun h => h.1) (fun h => h.1)
  exact ⟨fun e => hs.elim (h3 w hwd (Or.inl e)).1 (h3 w hwd (Or.inl e)).2,
         fun ha => hs.elim (h3 w hwd (Or.inr ha)).1 (h3 w hwd (Or.inr ha)).2⟩

/-- (3), for the whole walk, in the style of `Causal.only_withdrawals_remove`. A row that is
    not a withdrawal, with no withdrawal waiting on it, and which adds no cut, ends no
    standing at any depth. -/
theorem only_withdrawals_and_cuts_end (hconf : ConfMono conf)
    (S : Row → Prop) (x : Row) (hx : ¬ S x) (cut cut' : Row → T → Prop)
    (hcut : ∀ o t, cut' o t → cut o t)
    (hnw : ∀ w, isWd w → w ≠ x ∧ ¬ TransGen parent x w) :
    ∀ n t, stands parent signer isWd offer isAcc holder conf (C S) (C S) cut n t →
      stands parent signer isWd offer isAcc holder conf (C (fun q => S q ∨ q = x))
        (C (fun q => S q ∨ q = x)) cut' n t := by
  have grow := concl_grows parent wf wellFormed C hCk hfin S x hx
  intro n
  induction n with
  | zero =>
    intro t ⟨o, a, hp⟩
    exact ⟨o, a, pair_survives parent signer isWd offer isAcc holder wf wellFormed C hCk hfin
      S x hx _ _ cut cut' t o a hp
      (fun hv => hconf _ _ _ _ (fun _ z => z) grow o t hv) (hcut o t)
      (fun w hw => hnw w (hw.elim (fun h => h.1) (fun h => h.1)))⟩
  | succ n ih =>
    intro t ⟨o, a, hp⟩
    exact ⟨o, a, pair_survives parent signer isWd offer isAcc holder wf wellFormed C hCk hfin
      S x hx _ _ cut cut' t o a hp
      (fun hv => hconf _ _ _ _ ih grow o t hv) (hcut o t)
      (fun w hw => hnw w (hw.elim (fun h => h.1) (fun h => h.1)))⟩

end Seat

/-- (4) Why the house rule. Suppose the holder's withdrawal of its acceptance counted only
    while the holder stands in that seat. With the pair present and the withdrawal present,
    "the seat is live" would have to satisfy `L ↔ ¬ L`: no answer exists. Under the house
    rule a withdrawal counts by its signature alone, the walk reads withdrawals from the
    concluded layer and never from itself, and `stands` is a plain recursion on depth. -/
theorem no_answer_if_withdrawal_needs_standing (pair wd : Prop) (hp : pair) (hw : wd) :
    ¬ ∃ L : Prop, (L ↔ (pair ∧ ¬ (wd ∧ L))) :=
  fun ⟨_, h⟩ =>
    have hn := fun l => (h.1 l).2 ⟨hw, l⟩
    hn (h.2 ⟨hp, fun x => hn x.2⟩)

/-! ### (5) The reader's meaning is the one-row seat -/

section Reader

variable {Row Key : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (names : Row → Option Key)
variable (isWd : Row → Prop) (C : (Row → Prop) → Row → Prop)

/-- The reader's seat. A seat is a pair (s, k): "k, in s's reading". Its object is s's own
    reading, so the object's key and the holder are both `s`; the conferrer rule is the
    self-rooted one. No acceptance rows exist (`isAcc` is empty) and there are no cuts. The
    seat is then live exactly when `Causal.Edge` holds: an edge is a one-row seat. -/
theorem edge_is_one_row_seat (S : Row → Prop) (s k : Key) :
    seat parent signer isWd (fun e (t : Key × Key) => signer e = t.1 ∧ names e = some t.2)
        (fun _ => False) (fun t => t.1) (C S) (C S)
        (confSelf signer (fun t : Key × Key => t.1) (fun _ => False) (C S))
        (fun _ _ => False) (s, k)
      ↔ Edge parent signer names isWd C (fun _ => True) S s k := by
  constructor
  · intro ⟨o, a, h1, ⟨hs, hn⟩, _, _, hl, _, h7, _, _⟩
    cases hl with
    | inl hf => exact hf.1.elim
    | inr _ => exact ⟨o, ⟨h1, ⟨k, hn⟩, fun ⟨w, hw, hc, _⟩ => h7 ⟨w, hw, hc⟩⟩, hs, hn⟩
  · intro ⟨e, ⟨h1, _, h3⟩, h4, h5⟩
    exact ⟨e, e, h1, ⟨h4, h5⟩, h4, h1, Or.inr rfl, h4,
      fun ⟨w, hw, hc⟩ => h3 ⟨w, hw, hc, trivial⟩,
      fun ⟨w, hw, hc⟩ => h3 ⟨w, hw, hc, trivial⟩, fun x => x⟩

/-- (5) `Causal.means` is: concluded, and the reader reaches the signer along one-row seats,
    each signed by the key it leaves from. -/
theorem means_is_seat_walk (depth : Nat) (own : Key) (S : Row → Prop) (r : Row) :
    means parent signer names isWd C depth own S r ↔
      (C S r ∧ reaches (fun s k =>
        seat parent signer isWd (fun e (t : Key × Key) => signer e = t.1 ∧ names e = some t.2)
          (fun _ => False) (fun t => t.1) (C S) (C S)
          (confSelf signer (fun t : Key × Key => t.1) (fun _ => False) (C S))
          (fun _ _ => False) (s, k)) own depth (signer r)) := by
  have e : (fun s k =>
        seat parent signer isWd (fun e (t : Key × Key) => signer e = t.1 ∧ names e = some t.2)
          (fun _ => False) (fun t => t.1) (C S) (C S)
          (confSelf signer (fun t : Key × Key => t.1) (fun _ => False) (C S))
          (fun _ _ => False) (s, k))
      = Edge parent signer names isWd C (fun _ => True) S :=
    funext fun s => funext fun k => propext (edge_is_one_row_seat parent signer names isWd C S s k)
  rw [e]
  exact Iff.rfl

end Reader

/-- (5) Why the one-row seat is not a hole. Whatever any other key signs, a reader reaches
    a key other than itself only if a live edge signed by the reader's own key exists. A
    one-row seat is signed by its own holder and changes that holder's reading and nobody
    else's (`Causal.two_readers`). -/
theorem reach_needs_own_row {Key : Type} (E : Key → Key → Prop) (own : Key) :
    ∀ n k, reaches E own n k → k = own ∨ ∃ t, E own t := by
  intro n
  induction n with
  | zero => exact fun _ h => Or.inl h
  | succ n ih =>
    intro k hk
    cases hk with
    | inl hk => exact ih k hk
    | inr hk =>
      have ⟨m, hm, he⟩ := hk
      cases ih m hm with
      | inl e => exact Or.inr ⟨k, e ▸ he⟩
      | inr h => exact Or.inr h

/-! ## Part B. The cut -/

section Alternating

variable {α : Type}

/-- The least set closed under `F`. -/
def lfp (F : (α → Prop) → α → Prop) (r : α) : Prop :=
  ∀ P : α → Prop, (∀ q, F P q → P q) → P r

theorem lfp_least (F : (α → Prop) → α → Prop) (P : α → Prop) (h : ∀ q, F P q → P q) :
    ∀ r, lfp F r → P r :=
  fun _ hr => hr P h

theorem lfp_pre (F : (α → Prop) → α → Prop)
    (mono : ∀ X Y : α → Prop, (∀ r, X r → Y r) → ∀ r, F X r → F Y r) :
    ∀ r, F (lfp F) r → lfp F r :=
  fun r hr P hP => hP r (mono (lfp F) P (fun _ hq => hq P hP) r hr)

theorem lfp_post (F : (α → Prop) → α → Prop)
    (mono : ∀ X Y : α → Prop, (∀ r, X r → Y r) → ∀ r, F X r → F Y r) :
    ∀ r, lfp F r → F (lfp F) r :=
  fun _ hr => hr (F (lfp F)) (fun q hq => mono _ _ (lfp_pre F mono) q hq)

/-- `T X` is the set that counts if exactly `X` does the voiding. More voiding, less counts. -/
def Anti (T : (α → Prop) → α → Prop) : Prop :=
  ∀ X Y : α → Prop, (∀ r, X r → Y r) → ∀ r, T Y r → T X r

variable (T : (α → Prop) → α → Prop)

/-- COUNTS: counts whatever the undecided ones do. The least fixed point of `T ∘ T`. -/
def sure : α → Prop := lfp (fun X => T (T X))

/-- Counts or contested: not voided by what surely counts. -/
def poss : α → Prop := T (sure T)

def contested (r : α) : Prop := poss T r ∧ ¬ sure T r
def void (r : α) : Prop := ¬ poss T r

variable (hT : Anti T)
include hT

theorem sq_mono : ∀ X Y : α → Prop, (∀ r, X r → Y r) → ∀ r, T (T X) r → T (T Y) r :=
  fun X Y hXY r => hT (T Y) (T X) (hT X Y hXY) r

/-- What counts is what is not voided by anything that may count. -/
theorem sure_iff (r : α) : sure T r ↔ T (poss T) r :=
  ⟨lfp_post _ (sq_mono T hT) r, lfp_pre _ (sq_mono T hT) r⟩

theorem sure_sub_poss : ∀ r, sure T r → poss T r :=
  lfp_least _ (poss T) (fun q hq => hT (sure T) (T (poss T)) (fun r hr => (sure_iff T hT r).1 hr) q hq)

/-- (1) The status is the least answer. Any pair (L, U) that solves the two equations
    "L is what U does not void, U is what L does not void" has `sure ⊆ L` and `U ⊆ poss`:
    it decides everything the status decides, the same way. -/
theorem status_least (L U : α → Prop) (hL : ∀ r, L r ↔ T U r) (hU : ∀ r, U r ↔ T L r) :
    (∀ r, sure T r → L r) ∧ (∀ r, U r → poss T r) := by
  have h1 : ∀ r, sure T r → L r :=
    lfp_least _ L (fun q hq => (hL q).2 (hT U (T L) (fun r hr => (hU r).1 hr) q hq))
  exact ⟨h1, fun r hr => hT (sure T) L h1 r ((hU r).1 hr)⟩

/-- (1) Every two-valued solution lies between: it counts all that surely counts and nothing
    that is void. -/
theorem stable_between (F : α → Prop) (hF : ∀ r, F r ↔ T F r) :
    (∀ r, sure T r → F r) ∧ (∀ r, F r → poss T r) :=
  status_least T hT F F hF hF

/-- (1) Where nothing is contested, the equation `F = T F` has exactly one solution. -/
theorem unique_when_uncontested (hno : ∀ r, poss T r → sure T r)
    (F : α → Prop) (hF : ∀ r, F r ↔ T F r) : ∀ r, F r ↔ sure T r :=
  fun r => ⟨fun h => hno r ((stable_between T hT F hF).2 r h), (stable_between T hT F hF).1 r⟩

/-- (1) What makes it well-founded. If whether `r` counts reads the voiding set only at rows
    `dep`-below `r`, and `dep` is well-founded, nothing is contested. Ancestry is such a
    `dep` when no two concurrent cuts read each other. Two concurrent cuts that do read each
    other are not ordered by any relation on the rows, and there the third value is used. -/
theorem stratified_uncontested (dep : α → α → Prop) (wfd : WellFounded dep)
    (hdep : ∀ r (X Y : α → Prop), (∀ q, dep q r → (X q ↔ Y q)) → (T X r ↔ T Y r)) :
    ∀ r, poss T r ↔ sure T r := by
  intro r
  induction r using WellFounded.induction wfd with | _ r ih => ?_
  exact (hdep r (sure T) (poss T) (fun q hq => (ih q hq).symm)).trans (sure_iff T hT r).symm

/-- The run's iteration (`K.fix` in cut.py): start empty, apply `T ∘ T`. -/
def iter (T : (α → Prop) → α → Prop) : Nat → α → Prop
  | 0 => fun _ => False
  | n + 1 => T (T (iter T n))

/-- Every stage of the iteration is inside what counts. -/
theorem iter_sub_sure : ∀ n r, iter T n r → sure T r := by
  intro n
  induction n with
  | zero => exact fun _ h => h.elim
  | succ n ih => exact fun r h => lfp_pre _ (sq_mono T hT) r (sq_mono T hT _ _ ih r h)

omit hT in
/-- When the iteration stops growing, it is what counts. That it stops within one step per
    cut on a finite set is not proved here. -/
theorem iter_stops (n : Nat) (hstop : ∀ r, iter T (n + 1) r → iter T n r) :
    ∀ r, sure T r → iter T n r :=
  lfp_least _ (iter T n) hstop

omit hT in
/-- Two cuts that each count exactly when the other does not are both contested. Needs
    nothing of `T`. -/
theorem mutual_contested (a b : α)
    (ha : ∀ X : α → Prop, ¬ X b → T X a) (ha' : ∀ X : α → Prop, X b → ¬ T X a)
    (hb : ∀ X : α → Prop, ¬ X a → T X b) (hb' : ∀ X : α → Prop, X a → ¬ T X b) :
    contested T a ∧ contested T b := by
  have hP : ∀ r, sure T r → r ≠ a ∧ r ≠ b := by
    apply lfp_least (fun X => T (T X)) (fun r => r ≠ a ∧ r ≠ b)
    intro q hq
    have hTa : T (fun r => r ≠ a ∧ r ≠ b) a := ha _ (fun h => h.2 rfl)
    have hTb : T (fun r => r ≠ a ∧ r ≠ b) b := hb _ (fun h => h.1 rfl)
    exact ⟨fun e => ha' _ hTb (e ▸ hq), fun e => hb' _ hTa (e ▸ hq)⟩
  have na : ¬ sure T a := fun h => (hP a h).1 rfl
  have nb : ¬ sure T b := fun h => (hP b h).2 rfl
  exact ⟨⟨ha _ nb, na⟩, ⟨hb _ na, nb⟩⟩

omit hT in
/-- A counting row that overrules `a` makes `a` void. -/
theorem overruled_void (d a : α) (hd : sure T d) (hov : ∀ X : α → Prop, X d → ¬ T X a) :
    void T a :=
  fun h => hov (sure T) hd h

/-- And then a cut whose only obstacle was `a` counts. -/
theorem winner_counts (a b : α) (ha : void T a) (hb : ∀ X : α → Prop, ¬ X a → T X b) :
    sure T b :=
  (sure_iff T hT b).2 (hb _ ha)

end Alternating

/-! ### Equivariance of the status -/

section StatusSwap

variable {α : Type} (σ : α → α)

/-- One direction: if `T'` is `T` seen through `σ`, what surely counts under `T'` is carried
    by `σ` into what surely counts under `T`. -/
theorem sure_push (T T' : (α → Prop) → α → Prop) (hT : Anti T)
    (h : ∀ (X : α → Prop) r, T' (fun y => X (σ y)) r ↔ T X (σ r)) :
    ∀ r, sure T' r → sure T (σ r) := by
  apply lfp_least (fun X => T' (T' X)) (fun r => sure T (σ r))
  intro q hq
  have e : T' (fun y => sure T (σ y)) = (fun y => poss T (σ y)) :=
    funext fun y => propext (h (sure T) y)
  have hq' : T' (T' (fun y => sure T (σ y))) q := hq
  rw [e] at hq'
  exact (sure_iff T hT (σ q)).2 ((h (poss T) q).1 hq')

variable (hσ : ∀ x, σ (σ x) = x)
include hσ

theorem sure_swap (T T' : (α → Prop) → α → Prop) (hT : Anti T) (hT' : Anti T')
    (h : ∀ (X : α → Prop) r, T' (fun y => X (σ y)) r ↔ T X (σ r)) :
    ∀ r, sure T' r ↔ sure T (σ r) := by
  have h' : ∀ (X : α → Prop) r, T (fun y => X (σ y)) r ↔ T' X (σ r) := by
    intro X r
    have := h (fun y => X (σ y)) (σ r)
    have e : (fun y => X (σ (σ y))) = X := funext fun y => by rw [hσ]
    rw [e, hσ] at this
    exact this.symm
  intro r
  constructor
  · exact sure_push σ T T' hT h r
  · intro hr
    have := sure_push σ T' T hT' h' (σ r) hr
    rw [hσ] at this
    exact this

theorem poss_swap (T T' : (α → Prop) → α → Prop) (hT : Anti T) (hT' : Anti T')
    (h : ∀ (X : α → Prop) r, T' (fun y => X (σ y)) r ↔ T X (σ r)) :
    ∀ r, poss T' r ↔ poss T (σ r) := by
  intro r
  have e : sure T' = (fun y => sure T (σ y)) :=
    funext fun y => propext (sure_swap σ hσ T T' hT hT' h y)
  show T' (sure T') r ↔ T (sure T) (σ r)
  rw [e]
  exact h (sure T) r

end StatusSwap

/-! ### The cut operator -/

section Cut

variable {Row : Type}
variable (parent : Row → Row → Prop)
/- `isCut c`: `c` carries a slot it cuts. `clashes x c`: `x` and `c` cut a common slot and say
   different things (or `x` cuts a slot `c` is on). `overrules x c`: `x` names `c` among the
   rows it rejects, on a slot they share. `ent A X c`: the signers of `c` hold the seats the
   cut needs, at the head `c` names, when exactly the cuts in `X` do the voiding. -/
variable (isCut : Row → Prop) (clashes overrules : Row → Row → Prop)
variable (ent : (Row → Prop) → (Row → Prop) → Row → Prop)

/-- A cut counts, if exactly `X` does the voiding, iff it is concluded, its signers are
    seated, no cut in `X` that clashes with it is concurrent with it, and no cut in `X` that
    has it in its past overrules it. -/
def cutT (A X : Row → Prop) (c : Row) : Prop :=
  A c ∧ isCut c ∧ ent A X c ∧
    (¬ ∃ x, X x ∧ conc parent x c ∧ clashes x c) ∧
    (¬ ∃ x, X x ∧ TransGen parent c x ∧ overrules x c)

/-- Seats are read against the voiding set negatively only: more cuts, fewer seats. -/
def EntAnti : Prop :=
  ∀ (A X Y : Row → Prop), (∀ r, X r → Y r) → ∀ c, ent A Y c → ent A X c

theorem cutT_anti (hent : EntAnti ent) (A : Row → Prop) :
    Anti (cutT parent isCut clashes overrules ent A) :=
  fun X Y hXY c ⟨h1, h2, h3, h4, h5⟩ =>
    ⟨h1, h2, hent A X Y hXY c h3,
     fun ⟨x, hx, r⟩ => h4 ⟨x, hXY x hx, r⟩, fun ⟨x, hx, r⟩ => h5 ⟨x, hXY x hx, r⟩⟩

/-- A cut COUNTS. -/
def cutCounts (A : Row → Prop) : Row → Prop := sure (cutT parent isCut clashes overrules ent A)

/-- A cut counts or is contested. -/
def cutPoss (A : Row → Prop) : Row → Prop := poss (cutT parent isCut clashes overrules ent A)

/-- A row that is not a cut is voided by the cuts in `X`: one concurrent with it that hits a
    slot it is on, or one that has it in its past and overrules it. -/
def rowVoided (hits : Row → Row → Prop) (X : Row → Prop) (r : Row) : Prop :=
  (∃ x, X x ∧ conc parent x r ∧ hits x r) ∨ (∃ x, X x ∧ TransGen parent r x ∧ overrules x r)

/-- A row counts: concluded, and not voided even by a contested cut (cut.py `status`). -/
def rowCounts (hits : Row → Row → Prop) (A : Row → Prop) (r : Row) : Prop :=
  A r ∧ ¬ rowVoided parent overrules hits (cutPoss parent isCut clashes overrules ent A) r

/-- (1) The status is a function of the offered set. -/
theorem cut_status_function (C : (Row → Prop) → Row → Prop) (S S' : Row → Prop)
    (h : ∀ r, S r ↔ S' r) :
    cutCounts parent isCut clashes overrules ent (C S)
        = cutCounts parent isCut clashes overrules ent (C S') ∧
      cutPoss parent isCut clashes overrules ent (C S)
        = cutPoss parent isCut clashes overrules ent (C S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]
  exact ⟨rfl, rfl⟩

/-- The rule of KERNEL.md 6.4–6.5 on two cuts. Two concluded, seated, concurrent cuts that
    clash, with nothing else that clashes with or overrules either, are both contested. -/
theorem two_cuts_contested (A : Row → Prop) (a b : Row)
    (hAa : A a) (hAb : A b) (hca : isCut a) (hcb : isCut b)
    (hea : ∀ X, ent A X a) (heb : ∀ X, ent A X b)
    (hconc : conc parent a b) (hab : clashes a b) (hba : clashes b a)
    (honly_a : ∀ x, clashes x a → x = b) (honly_b : ∀ x, clashes x b → x = a)
    (hno : ∀ x, ¬ overrules x a ∧ ¬ overrules x b) :
    contested (cutT parent isCut clashes overrules ent A) a ∧
      contested (cutT parent isCut clashes overrules ent A) b := by
  have hconc' : conc parent b a := ⟨hconc.2.1, hconc.1, fun e => hconc.2.2 e.symm⟩
  apply mutual_contested (cutT parent isCut clashes overrules ent A) a b
  · intro X hX
    exact ⟨hAa, hca, hea X, fun ⟨x, hx, _, hc⟩ => hX (honly_a x hc ▸ hx),
      fun ⟨x, _, _, ho⟩ => (hno x).1 ho⟩
  · intro X hX h
    exact h.2.2.2.1 ⟨b, hX, hconc', hba⟩
  · intro X hX
    exact ⟨hAb, hcb, heb X, fun ⟨x, hx, _, hc⟩ => hX (honly_b x hc ▸ hx),
      fun ⟨x, _, _, ho⟩ => (hno x).2 ho⟩
  · intro X hX h
    exact h.2.2.2.1 ⟨a, hX, hconc, hab⟩

/-- ... unless a counting row names both: a counting cut that has `a` in its past and
    overrules it makes `a` void. -/
theorem named_and_overruled_void (A : Row → Prop) (d a : Row)
    (hd : cutCounts parent isCut clashes overrules ent A d)
    (hanc : TransGen parent a d) (hov : overrules d a) :
    void (cutT parent isCut clashes overrules ent A) a :=
  overruled_void _ d a hd (fun _ hX h => h.2.2.2.2 ⟨d, hX, hanc, hov⟩)

/-! ### (2) Equivariance -/

section CutSwap

variable (σ : Row → Row) (hσ : ∀ x, σ (σ x) = x)
variable (hp : ∀ p r, parent (σ p) (σ r) ↔ parent p r)
variable (hcut : ∀ r, isCut (σ r) ↔ isCut r)
variable (hcl : ∀ x c, clashes (σ x) (σ c) ↔ clashes x c)
variable (hov : ∀ x c, overrules (σ x) (σ c) ↔ overrules x c)
variable (hes : ∀ (A X : Row → Prop) c, ent (fun y => A (σ y)) (fun y => X (σ y)) c ↔ ent A X (σ c))

omit parent in
include hσ in
theorem ex_swap (X R R' : Row → Prop) (h : ∀ x, R x ↔ R' (σ x)) :
    (∃ x, X (σ x) ∧ R x) ↔ (∃ x, X x ∧ R' x) :=
  ⟨fun ⟨x, hx, hr⟩ => ⟨σ x, hx, (h x).1 hr⟩,
   fun ⟨x, hx, hr⟩ => ⟨σ x, by rw [hσ]; exact hx, (h (σ x)).2 (by rw [hσ]; exact hr)⟩⟩

include hσ hp hcut hcl hov hes

/-- The operator treats swapped rows alike. -/
theorem cutT_swap (A X : Row → Prop) (c : Row) :
    cutT parent isCut clashes overrules ent (fun y => A (σ y)) (fun y => X (σ y)) c ↔
      cutT parent isCut clashes overrules ent A X (σ c) := by
  have e1 := ex_swap σ hσ X (fun x => conc parent x c ∧ clashes x c)
    (fun x => conc parent x (σ c) ∧ clashes x (σ c))
    (fun x => ⟨fun ⟨a, b⟩ => ⟨(conc_swap parent σ hσ hp x c).2 a, (hcl x c).2 b⟩,
               fun ⟨a, b⟩ => ⟨(conc_swap parent σ hσ hp x c).1 a, (hcl x c).1 b⟩⟩)
  have e2 := ex_swap σ hσ X (fun x => TransGen parent c x ∧ overrules x c)
    (fun x => TransGen parent (σ c) x ∧ overrules x (σ c))
    (fun x => ⟨fun ⟨a, b⟩ => ⟨(anc_swap parent σ hσ hp c x).2 a, (hov x c).2 b⟩,
               fun ⟨a, b⟩ => ⟨(anc_swap parent σ hσ hp c x).1 a, (hov x c).1 b⟩⟩)
  exact ⟨fun ⟨h1, h2, h3, h4, h5⟩ =>
      ⟨h1, (hcut c).2 h2, (hes A X c).1 h3, fun h => h4 (e1.2 h), fun h => h5 (e2.2 h)⟩,
    fun ⟨h1, h2, h3, h4, h5⟩ =>
      ⟨h1, (hcut c).1 h2, (hes A X c).2 h3, fun h => h4 (e1.1 h), fun h => h5 (e2.1 h)⟩⟩

variable (hent : EntAnti ent)
include hent

/-- (2) The status treats swapped rows alike. -/
theorem cutCounts_swap (A : Row → Prop) (x : Row) :
    cutCounts parent isCut clashes overrules ent (fun y => A (σ y)) x ↔
      cutCounts parent isCut clashes overrules ent A (σ x) :=
  sure_swap σ hσ _ _ (cutT_anti parent isCut clashes overrules ent hent A)
    (cutT_anti parent isCut clashes overrules ent hent _)
    (fun X r => cutT_swap parent isCut clashes overrules ent σ hσ hp hcut hcl hov hes A X r) x

theorem cutPoss_swap (A : Row → Prop) (x : Row) :
    cutPoss parent isCut clashes overrules ent (fun y => A (σ y)) x ↔
      cutPoss parent isCut clashes overrules ent A (σ x) :=
  poss_swap σ hσ _ _ (cutT_anti parent isCut clashes overrules ent hent A)
    (cutT_anti parent isCut clashes overrules ent hent _)
    (fun X r => cutT_swap parent isCut clashes overrules ent σ hσ hp hcut hcl hov hes A X r) x

variable (wf : WellFounded parent)
variable (wellFormed : Row → Prop) (hw : ∀ r, wellFormed (σ r) ↔ wellFormed r)
variable (judge : Row → (Row → Prop) → (Row → Prop) → Prop)
variable (hj : ∀ r P C, judge (σ r) P C ↔ judge r (fun q => P (σ q)) (fun q => C (σ q)))
variable (root : Row → Prop) (hroot : ∀ r, root (σ r) ↔ root r)
include hw hj hroot

/-- (2) Two cuts exchanged by a swap the rules and the offered set do not see: both count
    or neither does. From `Causal.holder_both_or_neither`, with "counts" as the holder rule. -/
theorem indistinguishable_cuts_count_alike (S : Row → Prop) (hS : ∀ x, S (σ x) ↔ S x) (a : Row) :
    ¬ ((cutCounts parent isCut clashes overrules ent (concl parent wf judge wellFormed root S) a ∧
          ¬ cutCounts parent isCut clashes overrules ent
            (concl parent wf judge wellFormed root S) (σ a)) ∨
       (¬ cutCounts parent isCut clashes overrules ent
            (concl parent wf judge wellFormed root S) a ∧
          cutCounts parent isCut clashes overrules ent
            (concl parent wf judge wellFormed root S) (σ a))) :=
  holder_both_or_neither parent wf σ hσ hp wellFormed hw judge hj root hroot
    (cutCounts parent isCut clashes overrules ent)
    (cutCounts_swap parent isCut clashes overrules ent σ hσ hp hcut hcl hov hes hent) S hS a

/-- (2) Likewise both are possible or neither is. With the line above: the two have the same
    status, and where they clash (`two_cuts_contested`) it is "contested" for both. -/
theorem indistinguishable_cuts_possible_alike (S : Row → Prop) (hS : ∀ x, S (σ x) ↔ S x)
    (a : Row) :
    ¬ ((cutPoss parent isCut clashes overrules ent (concl parent wf judge wellFormed root S) a ∧
          ¬ cutPoss parent isCut clashes overrules ent
            (concl parent wf judge wellFormed root S) (σ a)) ∨
       (¬ cutPoss parent isCut clashes overrules ent
            (concl parent wf judge wellFormed root S) a ∧
          cutPoss parent isCut clashes overrules ent
            (concl parent wf judge wellFormed root S) (σ a))) :=
  holder_both_or_neither parent wf σ hσ hp wellFormed hw judge hj root hroot
    (cutPoss parent isCut clashes overrules ent)
    (cutPoss_swap parent isCut clashes overrules ent σ hσ hp hcut hcl hov hes hent) S hS a

end CutSwap

/-! ### (3) Finality against outsiders -/

/-- If a new row `x` cannot count as a cut whatever does the voiding, and seats no one else
    (the other cuts' entitlement is as it was), the operator is the same operator. -/
theorem outsider_same_operator (A A' : Row → Prop) (x : Row)
    (hA : ∀ r, r ≠ x → (A' r ↔ A r)) (hAx : ¬ A x)
    (hentx : ∀ X r, r ≠ x → (ent A' X r ↔ ent A X r))
    (hout : ∀ X, ¬ cutT parent isCut clashes overrules ent A' X x) :
    cutT parent isCut clashes overrules ent A' = cutT parent isCut clashes overrules ent A := by
  funext X r
  apply propext
  constructor
  · intro h
    have hne : r ≠ x := fun e => hout X (e ▸ h)
    exact ⟨(hA r hne).1 h.1, h.2.1, (hentx X r hne).1 h.2.2.1, h.2.2.2⟩
  · intro h
    have hne : r ≠ x := fun e => hAx (e ▸ h.1)
    exact ⟨(hA r hne).2 h.1, h.2.1, (hentx X r hne).2 h.2.2.1, h.2.2.2⟩

variable (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (C : (Row → Prop) → Row → Prop)
variable (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
variable (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
    (C S r ↔ C (fun q => S q ∨ q = x) r))
include hCk hfin

omit isCut clashes overrules ent in
/-- Offering `x`, with nothing waiting on it, changes the conclusion about no other row. -/
theorem concl_same_off (S : Row → Prop) (x : Row) (hx : ¬ S x)
    (hnw : ∀ y, S y → ¬ TransGen parent x y) :
    ∀ r, r ≠ x → (C (fun q => S q ∨ q = x) r ↔ C S r) := by
  intro r hne
  constructor
  · intro hc
    have hS : S r := (kept_offered parent wf wellFormed _ r (hCk _ r hc)).elim id
      (fun e => absurd e hne)
    exact (hfin S x r ((kept_new_row parent wf wellFormed S x r hne (hnw r hS)).2
      (hCk _ r hc)) hx).2 hc
  · intro hc
    exact (hfin S x r (hCk S r hc) hx).1 hc

/-- (3) An outsider's row changes no cut's status. `x` is offered after `S`, with nothing in
    `S` waiting on it. "Outsider" is two hypotheses: `x` cannot count as a cut whatever does
    the voiding (`hout`: it is not a cut, or its signer holds no seat that may cut), and `x`
    is in no other cut's tally (`hentx`). Then every row has the status it had, and `x` is
    void as a cut. -/
theorem outsider_changes_no_cut (S : Row → Prop) (x : Row) (hx : ¬ S x)
    (hnw : ∀ y, S y → ¬ TransGen parent x y)
    (hentx : ∀ X r, r ≠ x → (ent (C (fun q => S q ∨ q = x)) X r ↔ ent (C S) X r))
    (hout : ∀ X, ¬ cutT parent isCut clashes overrules ent (C (fun q => S q ∨ q = x)) X x) :
    cutCounts parent isCut clashes overrules ent (C (fun q => S q ∨ q = x))
        = cutCounts parent isCut clashes overrules ent (C S) ∧
      cutPoss parent isCut clashes overrules ent (C (fun q => S q ∨ q = x))
        = cutPoss parent isCut clashes overrules ent (C S) ∧
      ¬ cutPoss parent isCut clashes overrules ent (C (fun q => S q ∨ q = x)) x := by
  have hA := concl_same_off parent wf wellFormed C hCk hfin S x hx hnw
  have hAx : ¬ C S x := fun h => hx (kept_offered parent wf wellFormed S x (hCk S x h))
  have e := outsider_same_operator parent isCut clashes overrules ent (C S)
    (C (fun q => S q ∨ q = x)) x hA hAx hentx hout
  refine ⟨?_, ?_, hout _⟩
  · unfold cutCounts; rw [e]
  · unfold cutPoss; rw [e]

/-- (3) Nor does it change whether any other row counts. -/
theorem outsider_changes_no_other_row (hits : Row → Row → Prop) (S : Row → Prop) (x : Row)
    (hx : ¬ S x) (hnw : ∀ y, S y → ¬ TransGen parent x y)
    (hentx : ∀ X r, r ≠ x → (ent (C (fun q => S q ∨ q = x)) X r ↔ ent (C S) X r))
    (hout : ∀ X, ¬ cutT parent isCut clashes overrules ent (C (fun q => S q ∨ q = x)) X x)
    (r : Row) (hne : r ≠ x) :
    rowCounts parent isCut clashes overrules ent hits (C (fun q => S q ∨ q = x)) r ↔
      rowCounts parent isCut clashes overrules ent hits (C S) r := by
  have e := (outsider_changes_no_cut parent isCut clashes overrules ent wf wellFormed C hCk hfin
    S x hx hnw hentx hout).2.1
  have hA := concl_same_off parent wf wellFormed C hCk hfin S x hx hnw r hne
  unfold rowCounts
  rw [e]
  exact ⟨fun h => ⟨hA.1 h.1, h.2⟩, fun h => ⟨hA.2 h.1, h.2⟩⟩

omit hCk hfin in
/-- (3) And the outsider's row itself does not count on the slot. `c` is a counting cut kept
    in `S`; `x` is offered later and is on a slot `c` cuts (`hits c x`). `x` cannot be in the
    past of `c`. If it is concurrent with `c`, the cut voids it. If it names `c`, it is
    judged at the head it names, and that judgment is the conclusion layer's (`hlate`: a key
    with no seat at that head concludes nothing there). Either way it does not count, so no
    holder rule that reads the counting rows on the slot can be moved by it. -/
theorem outsider_row_never_counts (hits : Row → Row → Prop) (S : Row → Prop) (x c : Row)
    (hx : ¬ S x) (hkc : kept parent wf wellFormed S c)
    (hc : cutPoss parent isCut clashes overrules ent (C (fun q => S q ∨ q = x)) c)
    (hhit : hits c x)
    (hlate : TransGen parent c x → ¬ C (fun q => S q ∨ q = x) x) :
    ¬ rowCounts parent isCut clashes overrules ent hits (C (fun q => S q ∨ q = x)) x := by
  intro ⟨hcx, hnv⟩
  have hn := new_row_not_ancestor parent wf wellFormed S x c hkc hx
  have hna : ¬ TransGen parent c x := fun h => hlate h hcx
  exact hnv (Or.inl ⟨c, hc, ⟨hna, hn.2, hn.1⟩, hhit⟩)

end Cut

/-! ### (4) `Causal.counts` and the cut on a key slot -/

section KeyCut

variable {Row Key : Type}
variable (parent : Row → Row → Prop) (wf : WellFounded parent)
variable (signer : Row → Key) (removes : Row → Key → Prop)

/-- Voided on the key slot: a removal of the row's signer, in the voiding set, concurrent
    with the row. This is `rowVoided` with `hits x r := removes x (signer r)` and nothing
    overruled. -/
def keyVoided (X : Row → Prop) (r : Row) : Prop :=
  ∃ x, X x ∧ conc parent x r ∧ removes x (signer r)

/-- `counts` is the stricter. Whatever set `X` of concluded removals does the voiding, a row
    that counts in the sense of Part H is concluded and not voided on its key slot. -/
theorem counts_then_not_voided (C : (Row → Prop) → Row → Prop) (S : Row → Prop)
    (X : Row → Prop) (hX : ∀ x, X x → C S x) (r : Row)
    (h : counts parent signer removes C S r) :
    C S r ∧ ¬ keyVoided parent signer removes X r :=
  ⟨h.1, fun ⟨x, hx, hc, hr⟩ => hc.2.1 (h.2 x (hX x hx) hr)⟩

/-- Where they agree. If every concluded removal of the row's signer is in the voiding set
    (none is contested or void as a cut), and none of them is the row or in the row's past,
    then "not voided on the key slot" is `counts`. -/
theorem not_voided_then_counts (C : (Row → Prop) → Row → Prop) (S : Row → Prop)
    (X : Row → Prop) (r : Row)
    (hall : ∀ x, C S x → removes x (signer r) → X x)
    (hpast : ∀ x, C S x → removes x (signer r) → x ≠ r ∧ ¬ TransGen parent x r)
    (h : C S r ∧ ¬ keyVoided parent signer removes X r) :
    counts parent signer removes C S r :=
  ⟨h.1, fun x hx hr => Classical.byContradiction fun hn =>
    h.2 ⟨x, hall x hx hr, ⟨(hpast x hx hr).2, hn, (hpast x hx hr).1⟩, hr⟩⟩

include wf in
/-- Where they differ, first: a row that names a removal of its own signer (a row signed
    after re-admission names the head that re-admits, which names the removal). Under
    `counts` it never counts while that removal is concluded. -/
theorem counts_refuses_after_removal (C : (Row → Prop) → Row → Prop) (S : Row → Prop)
    (x r : Row) (hx : C S x) (hr : removes x (signer r)) (hanc : TransGen parent x r) :
    ¬ counts parent signer removes C S r :=
  fun h => wf_asymm (WellFounded.transGen wf) x r hanc (h.2 x hx hr)

/-- Under the cut that removal does not void the row: the row is not concurrent with it, and
    whether it counts is left to the conclusion layer at the head the row names. -/
theorem cut_spares_after_removal (x r : Row) (hanc : TransGen parent x r) :
    ¬ conc parent x r :=
  fun h => h.1 hanc

/-- Where they differ, second: a removal that is concluded but does not count as a cut
    (contested or void). `counts` lets it bind; the cut does not. If the only concluded
    removals of the signer that lack the row in their past are outside the voiding set, the
    row is not voided. -/
theorem contested_removal_does_not_void (X : Row → Prop) (r : Row)
    (h : ∀ x, X x → removes x (signer r) → TransGen parent r x) :
    ¬ keyVoided parent signer removes X r :=
  fun ⟨x, hx, hc, hr⟩ => hc.2.1 (h x hx hr)

end KeyCut

/-! ### Seats and cuts together -/

section SeatCut

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (isWd : Row → Prop)
variable (offer : Row → T → Prop) (isAcc : Row → Prop) (holder : T → Key)
variable (conf : (T → Prop) → (Row → Prop) → Row → T → Prop)
variable (cutsSeat : Row → T → Prop) (mayCut : T → Row → Prop)

/-- A cut in `X` removes the pair whose offer is `o` from seat `t`, unless the offer names
    the cut: an offer made after the cut, knowing it, seats again (re-admission). -/
def cutOut (X : Row → Prop) (o : Row) (t : T) : Prop :=
  ∃ c, X c ∧ cutsSeat c t ∧ ¬ TransGen parent c o

/-- The cut's signer is seated at the head the cut names: a seat that may cut, standing by
    the concluded rows in the cut's past, less what the cuts in `X` that lie in its past
    remove. (A cut concurrent with this one is `clashes`, not this.) -/
def entSeat (n : Nat) (A X : Row → Prop) (c : Row) : Prop :=
  ∃ t, mayCut t c ∧ holder t = signer c ∧
    stands parent signer isWd offer isAcc holder conf
      (fun r => A r ∧ TransGen parent r c) (fun r => A r ∧ TransGen parent r c)
      (cutOut parent cutsSeat (fun x => X x ∧ TransGen parent x c)) n t

/-- Seats give an entitlement that is antitone in the voiding set, so the status of Part B
    is defined with seats inside it: the circle "a cut counts if its signer is seated; a
    seat is live if no counting cut removes it" has the well-founded fixed point as its
    answer, by `cutT_anti` and `stands_mono`. -/
theorem entSeat_anti (hconf : ConfMono conf) (n : Nat) :
    EntAnti (entSeat parent signer isWd offer isAcc holder conf cutsSeat mayCut n) :=
  fun _ _ _ hXY _ ⟨t, h1, h2, h3⟩ =>
    ⟨t, h1, h2, stands_mono parent signer isWd offer isAcc holder conf hconf _ _ _ _ _ _
      (fun _ h => h) (fun _ h => h)
      (fun _ _ ⟨x, hx, hc⟩ => ⟨x, ⟨hXY x hx.1, hx.2⟩, hc⟩) n t h3⟩

variable (isCut : Row → Prop) (clashes overrules : Row → Row → Prop)

/-- The seat, with the cut inside it: standing by the concluded rows, less what the COUNTING
    cuts remove, where a cut counts by the status of Part B with its signer's seat judged by
    `entSeat`. A contested cut removes no one and a void cut removes no one. -/
def seated (n : Nat) (A : Row → Prop) : T → Prop :=
  stands parent signer isWd offer isAcc holder conf A A
    (cutOut parent cutsSeat (cutCounts parent isCut clashes overrules
      (entSeat parent signer isWd offer isAcc holder conf cutsSeat mayCut n) A)) n

/-- (A1, B1) It is a function of the offered set, in every arrival order. -/
theorem seated_function (C : (Row → Prop) → Row → Prop) (n : Nat) (S S' : Row → Prop)
    (h : ∀ r, S r ↔ S' r) :
    seated parent signer isWd offer isAcc holder conf cutsSeat mayCut isCut clashes overrules
        n (C S)
      = seated parent signer isWd offer isAcc holder conf cutsSeat mayCut isCut clashes
        overrules n (C S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

end SeatCut

/-! ## Axioms used -/

#print axioms seat_needs_offer
#print axioms seat_needs_acceptance
#print axioms no_offer_no_seat
#print axioms no_acceptance_no_seat
#print axioms one_row_only_to_self
#print axioms two_rows_unless_self
#print axioms offer_withdrawal_ends
#print axioms acceptance_withdrawal_ends
#print axioms seat_mono
#print axioms confSelf_mono
#print axioms confSingle_mono
#print axioms confGroup_mono
#print axioms conf_or_mono
#print axioms stands_mono
#print axioms stands_deeper
#print axioms stands_function
#print axioms stands_perm
#print axioms pair_survives
#print axioms third_key_cannot_end
#print axioms only_withdrawals_and_cuts_end
#print axioms no_answer_if_withdrawal_needs_standing
#print axioms edge_is_one_row_seat
#print axioms means_is_seat_walk
#print axioms reach_needs_own_row
#print axioms sure_iff
#print axioms sure_sub_poss
#print axioms status_least
#print axioms stable_between
#print axioms unique_when_uncontested
#print axioms stratified_uncontested
#print axioms iter_sub_sure
#print axioms iter_stops
#print axioms mutual_contested
#print axioms overruled_void
#print axioms winner_counts
#print axioms sure_swap
#print axioms poss_swap
#print axioms cutT_anti
#print axioms cut_status_function
#print axioms two_cuts_contested
#print axioms named_and_overruled_void
#print axioms cutCounts_swap
#print axioms indistinguishable_cuts_count_alike
#print axioms indistinguishable_cuts_possible_alike
#print axioms outsider_same_operator
#print axioms outsider_changes_no_cut
#print axioms outsider_changes_no_other_row
#print axioms outsider_row_never_counts
#print axioms counts_then_not_voided
#print axioms not_voided_then_counts
#print axioms counts_refuses_after_removal
#print axioms cut_spares_after_removal
#print axioms contested_removal_does_not_void
#print axioms entSeat_anti
#print axioms seated_function

end Kernel
