/-
  SeatG.lean — the refined seat of Harden.lean F4, carried through the walk

  `Harden.F4` refines the pair of Seat.lean: an offer conferred by a count is not ended by its
  proposer alone, and the holder may end its own seat by a withdrawal naming the offer. The
  mark `shared o` said which offers. This file

    (1) proves the walk `standsG` monotone in offers and acceptances and antitone in
        withdrawals and cuts (`standsG_mono`, the analogue of `Kernel.stands_mono`);
    (2) relates `seatG` to `seat`: on an offer that is not shared the refined pair is the old
        pair less the holder's withdrawal against the offer (`seatG_le_seat`), and the two
        walks are EQUAL exactly when no such withdrawal is held (`standsG_eq_stands`). The
        equality "seatG = seat when no offer is shared" is false without that proviso
        (`Witness.unshared_not_equal`);
    (3) derives the mark: `sharedK` is the rule of seat.py (`off_ended`, line 180): the offer
        declares a count (conf = group), or seats its own signer. Under the declared
        conferrer rule `confDecl`, an offer that declares a count with need at least two has
        a conferring voice that is not its proposer's (`count_not_sole`), and an offer that
        is not marked is conferred by its signer alone (`unmarked_sole`);
    (4) restates the downstream theorems of Seat.lean for the refined walk: the function
        (`standsG_function`, in Harden.lean), the two-voice floor, either side ends it, no
        third key ends it (the proposer of a shared offer being a third key), and
        `only_withdrawals_and_cuts_endG`;
    (5) carries the refined walk into `Kernel.seated`: `seatedG`, its entitlement
        `entSeatG` is antitone (so the cut's status is defined with it), and `seatedG` is a
        function of the offered set.

  CHOICE. `seatBy` is not restated. The two definitions stay; (2) says exactly where they
  differ, and `Kernel.seated` is the special case `seatedG` with the proviso of (2).

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Harden2.lean.
-/

import Harden2

namespace Kernel

namespace SeatG

open Order Relation Causal Harden

section Rule

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (isWd : Row → Prop)
variable (offer : Row → T → Prop) (isAcc : Row → Prop) (holder : T → Key)
variable (shared : Row → Prop)

/-! ### (1) Monotone in offers and acceptances, antitone in withdrawals and cuts -/

theorem offEnded_mono (W W' : Row → Prop) (hW : ∀ r, W r → W' r) (o : Row) (t : T)
    (h : F4.offEnded parent signer isWd holder shared W o t) :
    F4.offEnded parent signer isWd holder shared W' o t :=
  let ⟨w, h1, h2⟩ := h
  ⟨w, hW w h1, h2⟩

theorem seatByG_mono (P P' W W' : Row → Prop) (V V' cut cut' : Row → T → Prop)
    (hP : ∀ r, P r → P' r) (hW : ∀ r, W' r → W r)
    (hV : ∀ o t, V o t → V' o t) (hc : ∀ o t, cut' o t → cut o t) (t : T) (o a : Row)
    (h : F4.seatByG parent signer isWd offer isAcc holder shared P W V cut t o a) :
    F4.seatByG parent signer isWd offer isAcc holder shared P' W' V' cut' t o a := by
  obtain ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩ := h
  exact ⟨hP o h1, h2, hV o t h3, hP a h4, h5, h6,
    fun he => h7 (offEnded_mono parent signer isWd holder shared W' W hW o t he),
    fun ⟨w, hw, hx⟩ => h8 ⟨w, hw, hW w hx⟩,
    fun hh => h9 (hc o t hh)⟩

theorem seatG_mono (P P' W W' : Row → Prop) (V V' cut cut' : Row → T → Prop)
    (hP : ∀ r, P r → P' r) (hW : ∀ r, W' r → W r)
    (hV : ∀ o t, V o t → V' o t) (hc : ∀ o t, cut' o t → cut o t) (t : T)
    (h : F4.seatG parent signer isWd offer isAcc holder shared P W V cut t) :
    F4.seatG parent signer isWd offer isAcc holder shared P' W' V' cut' t :=
  let ⟨o, a, h⟩ := h
  ⟨o, a, seatByG_mono parent signer isWd offer isAcc holder shared P P' W W' V V' cut cut'
    hP hW hV hc t o a h⟩

variable (conf : (T → Prop) → (Row → Prop) → Row → T → Prop)

/-- (1) `Kernel.stands_mono` for the refined walk. -/
theorem standsG_mono (hconf : ConfMono conf) (P P' W W' : Row → Prop)
    (cut cut' : Row → T → Prop)
    (hP : ∀ r, P r → P' r) (hW : ∀ r, W' r → W r) (hc : ∀ o t, cut' o t → cut o t) :
    ∀ n t, F4.standsG parent signer isWd offer isAcc holder shared conf P W cut n t →
      F4.standsG parent signer isWd offer isAcc holder shared conf P' W' cut' n t := by
  intro n
  induction n with
  | zero =>
    intro t h
    exact seatG_mono parent signer isWd offer isAcc holder shared P P' W W' _ _ cut cut' hP hW
      (fun o t hv => hconf _ _ _ _ (fun _ x => x) hP o t hv) hc t h
  | succ n ih =>
    intro t h
    exact seatG_mono parent signer isWd offer isAcc holder shared P P' W W' _ _ cut cut' hP hW
      (fun o t hv => hconf _ _ _ _ ih hP o t hv) hc t h

/-- A longer chain allows no less. -/
theorem standsG_deeper (hconf : ConfMono conf) (P W : Row → Prop) (cut : Row → T → Prop) :
    ∀ n t, F4.standsG parent signer isWd offer isAcc holder shared conf P W cut n t →
      F4.standsG parent signer isWd offer isAcc holder shared conf P W cut (n + 1) t := by
  intro n
  induction n with
  | zero =>
    intro t h
    exact seatG_mono parent signer isWd offer isAcc holder shared P P W W _ _ cut cut
      (fun _ x => x) (fun _ x => x)
      (fun o t hv => hconf _ _ _ _ (fun _ x => x.elim) (fun _ x => x) o t hv)
      (fun _ _ x => x) t h
  | succ n ih =>
    intro t h
    exact seatG_mono parent signer isWd offer isAcc holder shared P P W W _ _ cut cut
      (fun _ x => x) (fun _ x => x) (fun o t hv => hconf _ _ _ _ ih (fun _ x => x) o t hv)
      (fun _ _ x => x) t h

/-- The shared mark only shields: marking more offers keeps every live pair live. -/
theorem standsG_shared_mono (hconf : ConfMono conf) (shared' : Row → Prop)
    (hs : ∀ o, shared o → shared' o) (P W : Row → Prop) (cut : Row → T → Prop) :
    ∀ n t, F4.standsG parent signer isWd offer isAcc holder shared conf P W cut n t →
      F4.standsG parent signer isWd offer isAcc holder shared' conf P W cut n t := by
  have pair : ∀ (V V' : Row → T → Prop), (∀ o t, V o t → V' o t) → ∀ t,
      F4.seatG parent signer isWd offer isAcc holder shared P W V cut t →
      F4.seatG parent signer isWd offer isAcc holder shared' P W V' cut t := by
    intro V V' hV t ⟨o, a, h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
    exact ⟨o, a, h1, h2, hV o t h3, h4, h5, h6,
      fun ⟨w, hW, hwd, hp, hs'⟩ => h7 ⟨w, hW, hwd, hp,
        hs'.elim Or.inl (fun x => Or.inr ⟨x.1, fun y => x.2 (hs o y)⟩)⟩, h8, h9⟩
  intro n
  induction n with
  | zero => exact pair _ _ (fun _ _ x => x)
  | succ n ih => exact pair _ _ (fun o t hv => hconf _ _ _ _ ih (fun _ x => x) o t hv)

/-! ### (2) The refined seat against the seat of Seat.lean -/

/-- No shared offer, and no withdrawal by a seat's holder naming an offer for that seat that
    the holder did not sign. -/
def NoHolderWdOnOffer (W : Row → Prop) : Prop :=
  ∀ o t w, offer o t → W w → isWd w → parent o w → signer w = holder t → signer w = signer o

/-- On an unshared offer the refined pair is inside the old pair. -/
theorem seatByG_le_seatBy (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a : Row)
    (hns : ¬ shared o)
    (h : F4.seatByG parent signer isWd offer isAcc holder shared P W V cut t o a) :
    seatBy parent signer isWd offer isAcc holder P W V cut t o a :=
  ((F4.unshared_iff parent signer isWd offer isAcc holder shared P W V cut t o a hns).1 h).1

/-- With the proviso they are the same pair. -/
theorem seatByG_iff_seatBy (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a : Row)
    (hns : ¬ shared o) (hno : NoHolderWdOnOffer parent signer isWd offer holder W) :
    F4.seatByG parent signer isWd offer isAcc holder shared P W V cut t o a ↔
      seatBy parent signer isWd offer isAcc holder P W V cut t o a := by
  rw [F4.unshared_iff parent signer isWd offer isAcc holder shared P W V cut t o a hns]
  constructor
  · exact fun h => h.1
  · intro h
    refine ⟨h, fun ⟨w, hW, hwd, hp, hs⟩ => h.2.2.2.2.2.2.1 ⟨w, ⟨hwd, hp, ?_⟩, hW⟩⟩
    exact hno o t w h.2.1 hW hwd hp hs

/-- (2) With no shared offer, every refined standing is a standing of Seat.lean. -/
theorem standsG_le_stands (hconf : ConfMono conf) (hns : ∀ o, ¬ shared o)
    (P W : Row → Prop) (cut : Row → T → Prop) :
    ∀ n t, F4.standsG parent signer isWd offer isAcc holder shared conf P W cut n t →
      stands parent signer isWd offer isAcc holder conf P W cut n t := by
  intro n
  induction n with
  | zero =>
    intro t ⟨o, a, h⟩
    exact ⟨o, a, seatByG_le_seatBy parent signer isWd offer isAcc holder shared P W _ cut t o a
      (hns o) h⟩
  | succ n ih =>
    intro t ⟨o, a, h⟩
    have h' := seatByG_le_seatBy parent signer isWd offer isAcc holder shared P W _ cut t o a
      (hns o) h
    exact ⟨o, a, seatBy_mono parent signer isWd offer isAcc holder P P W W _ _ cut cut
      (fun _ x => x) (fun _ x => x) (fun o t hv => hconf _ _ _ _ ih (fun _ x => x) o t hv)
      (fun _ _ x => x) t o a h'⟩

/-- (2) With no shared offer and the proviso, the two walks are equal at every depth. -/
theorem standsG_eq_stands (hns : ∀ o, ¬ shared o)
    (P W : Row → Prop) (cut : Row → T → Prop)
    (hno : NoHolderWdOnOffer parent signer isWd offer holder W) :
    ∀ n, F4.standsG parent signer isWd offer isAcc holder shared conf P W cut n =
      stands parent signer isWd offer isAcc holder conf P W cut n := by
  intro n
  induction n with
  | zero =>
    funext t
    apply propext
    exact ⟨fun ⟨o, a, h⟩ => ⟨o, a, (seatByG_iff_seatBy parent signer isWd offer isAcc holder
        shared P W _ cut t o a (hns o) hno).1 h⟩,
      fun ⟨o, a, h⟩ => ⟨o, a, (seatByG_iff_seatBy parent signer isWd offer isAcc holder
        shared P W _ cut t o a (hns o) hno).2 h⟩⟩
  | succ n ih =>
    funext t
    apply propext
    show F4.seatG parent signer isWd offer isAcc holder shared P W
        (conf (F4.standsG parent signer isWd offer isAcc holder shared conf P W cut n) P) cut t ↔
      seat parent signer isWd offer isAcc holder P W
        (conf (stands parent signer isWd offer isAcc holder conf P W cut n) P) cut t
    rw [ih]
    exact ⟨fun ⟨o, a, h⟩ => ⟨o, a, (seatByG_iff_seatBy parent signer isWd offer isAcc holder
        shared P W _ cut t o a (hns o) hno).1 h⟩,
      fun ⟨o, a, h⟩ => ⟨o, a, (seatByG_iff_seatBy parent signer isWd offer isAcc holder
        shared P W _ cut t o a (hns o) hno).2 h⟩⟩

/-! ### (4) The downstream theorems of Seat.lean, for the refined pair -/

theorem seatG_needs_offer (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (h : F4.seatG parent signer isWd offer isAcc holder shared P W V cut t) :
    ∃ o, P o ∧ offer o t ∧ V o t :=
  let ⟨o, _, h⟩ := h
  ⟨o, h.1, h.2.1, h.2.2.1⟩

theorem seatG_needs_acceptance (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (h : F4.seatG parent signer isWd offer isAcc holder shared P W V cut t) :
    ∃ a, P a ∧ signer a = holder t :=
  let ⟨_, a, h⟩ := h
  ⟨a, h.2.2.2.1, h.2.2.2.2.2.1⟩

/-- The two-voice floor: offers by keys that may not confer seat no one. -/
theorem no_offer_no_seatG (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (h : ∀ o, P o → offer o t → ¬ V o t) :
    ¬ F4.seatG parent signer isWd offer isAcc holder shared P W V cut t :=
  fun hs =>
    let ⟨o, h1, h2, h3⟩ := seatG_needs_offer parent signer isWd offer isAcc holder shared P W V cut t hs
    h o h1 h2 h3

/-- The two-voice floor: nobody is seated by others alone. -/
theorem no_acceptance_no_seatG (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (h : ∀ a, P a → signer a ≠ holder t) :
    ¬ F4.seatG parent signer isWd offer isAcc holder shared P W V cut t :=
  fun hs =>
    let ⟨a, h1, h2⟩ :=
      seatG_needs_acceptance parent signer isWd offer isAcc holder shared P W V cut t hs
    h a h1 h2

theorem one_row_only_to_selfG (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o : Row)
    (h : F4.seatByG parent signer isWd offer isAcc holder shared P W V cut t o o) :
    signer o = holder t :=
  h.2.2.2.2.2.1

/-- Every depth: a standing has an offer and a row by its holder. -/
theorem standsG_two_voices (P W : Row → Prop) (cut : Row → T → Prop) (n : Nat) (t : T)
    (h : F4.standsG parent signer isWd offer isAcc holder shared conf P W cut n t) :
    (∃ o, P o ∧ offer o t) ∧ ∃ a, P a ∧ signer a = holder t := by
  cases n with
  | zero =>
    obtain ⟨o, a, h1, h2, _, h4, _, h6, _⟩ := h
    exact ⟨⟨o, h1, h2⟩, ⟨a, h4, h6⟩⟩
  | succ n =>
    obtain ⟨o, a, h1, h2, _, h4, _, h6, _⟩ := h
    exact ⟨⟨o, h1, h2⟩, ⟨a, h4, h6⟩⟩

/-- The conferrer's withdrawal ends an unshared offer. -/
theorem offer_withdrawal_endsG (P W : Row → Prop) (V cut : Row → T → Prop) (t : T) (o a w : Row)
    (hns : ¬ shared o) (hw : wdOf parent signer isWd w o) (hW : W w) :
    ¬ F4.seatByG parent signer isWd offer isAcc holder shared P W V cut t o a :=
  fun h => h.2.2.2.2.2.2.1 ⟨w, hW, hw.1, hw.2.1, Or.inr ⟨hw.2.2, hns⟩⟩

/-- A withdrawal that ends a refined pair is signed by the holder, or by the offer's signer
    when the offer is not shared. -/
theorem ending_withdrawal_signerG (P W : Row → Prop) (V cut : Row → T → Prop) (t : T)
    (o a w : Row) (h : F4.seatByG parent signer isWd offer isAcc holder shared P W V cut t o a)
    (hw : (isWd w ∧ parent o w ∧ (signer w = holder t ∨ (signer w = signer o ∧ ¬ shared o))) ∨
      wdOf parent signer isWd w a) :
    signer w = holder t ∨ (signer w = signer o ∧ ¬ shared o) :=
  hw.elim (fun x => x.2.2) (fun x => Or.inl (x.2.2.trans h.2.2.2.2.2.1))

variable (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (C : (Row → Prop) → Row → Prop)
variable (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
variable (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
    (C S r ↔ C (fun q => S q ∨ q = x) r))
include hCk hfin

/-- A refined pair survives the offer of `x` if no withdrawal row that is `x` or waits on `x`
    is one that could end it. -/
theorem pair_survivesG (S : Row → Prop) (x : Row) (hx : ¬ S x) (V V' cut cut' : Row → T → Prop)
    (t : T) (o a : Row)
    (hp : F4.seatByG parent signer isWd offer isAcc holder shared (C S) (C S) V cut t o a)
    (hV : V o t → V' o t) (hcut : cut' o t → cut o t)
    (hw : ∀ w, isWd w → (parent o w ∨ parent a w) → w ≠ x ∧ ¬ TransGen parent x w) :
    F4.seatByG parent signer isWd offer isAcc holder shared (C (fun q => S q ∨ q = x))
      (C (fun q => S q ∨ q = x)) V' cut' t o a := by
  obtain ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩ := hp
  have grow := concl_grows parent wf wellFormed C hCk hfin S x hx
  have back := fun w hwd hp hc =>
    concl_back parent wf wellFormed C hCk hfin S x w hx (hw w hwd hp) hc
  exact ⟨grow o h1, h2, hV h3, grow a h4, h5, h6,
    fun ⟨w, hW, hwd, hpar, hs⟩ => h7 ⟨w, back w hwd (Or.inl hpar) hW, hwd, hpar, hs⟩,
    fun ⟨w, hwd, hW⟩ => h8 ⟨w, hwd, back w hwd.1 (Or.inr hwd.2.1) hW⟩,
    fun hh => h9 (hcut hh)⟩

/-- (4) No third key ends a refined pair without a cut. For an unshared offer the third keys
    are those other than the conferrer and the holder (`Kernel.third_key_cannot_end`); for a
    shared offer, every key but the holder (`Harden.F4.proposer_cannot_end`). -/
theorem third_key_cannot_endG (S : Row → Prop) (x : Row) (hx : ¬ S x)
    (V V' cut cut' : Row → T → Prop) (t : T) (o a : Row)
    (hp : F4.seatByG parent signer isWd offer isAcc holder shared (C S) (C S) V cut t o a)
    (hV : V o t → V' o t) (hcut : cut' o t → cut o t)
    (h3 : ∀ w, isWd w → (w = x ∨ TransGen parent x w) →
      signer w ≠ holder t ∧ (¬ shared o → signer w ≠ signer o)) :
    F4.seatByG parent signer isWd offer isAcc holder shared (C (fun q => S q ∨ q = x))
      (C (fun q => S q ∨ q = x)) V' cut' t o a := by
  obtain ⟨h1, h2, h3', h4, h5, h6, h7, h8, h9⟩ := hp
  have grow := concl_grows parent wf wellFormed C hCk hfin S x hx
  have back : ∀ w, isWd w → (signer w = holder t ∨ (signer w = signer o ∧ ¬ shared o)) →
      C (fun q => S q ∨ q = x) w → C S w := by
    intro w hwd hs hc
    have hn : ∀ e, (w = x ∨ TransGen parent x w) → e → False := by
      intro _ hwx _
      have := h3 w hwd hwx
      exact hs.elim this.1 (fun hs => this.2 hs.2 hs.1)
    exact concl_back parent wf wellFormed C hCk hfin S x w hx
      ⟨fun e => hn True (Or.inl e) trivial, fun ha => hn True (Or.inr ha) trivial⟩ hc
  exact ⟨grow o h1, h2, hV h3', grow a h4, h5, h6,
    fun ⟨w, hW, hwd, hpar, hs⟩ => h7 ⟨w, back w hwd hs hW, hwd, hpar, hs⟩,
    fun ⟨w, hw, hW⟩ => h8 ⟨w, hw, back w hw.1 (Or.inl (hw.2.2.trans h6)) hW⟩,
    fun hh => h9 (hcut hh)⟩

/-- (4) `Kernel.only_withdrawals_and_cuts_end`, refined. A row that is not a withdrawal, with
    no withdrawal waiting on it, and which adds no cut, ends no refined standing at any
    depth. -/
theorem only_withdrawals_and_cuts_endG (hconf : ConfMono conf)
    (S : Row → Prop) (x : Row) (hx : ¬ S x) (cut cut' : Row → T → Prop)
    (hcut : ∀ o t, cut' o t → cut o t)
    (hnw : ∀ w, isWd w → w ≠ x ∧ ¬ TransGen parent x w) :
    ∀ n t, F4.standsG parent signer isWd offer isAcc holder shared conf (C S) (C S) cut n t →
      F4.standsG parent signer isWd offer isAcc holder shared conf (C (fun q => S q ∨ q = x))
        (C (fun q => S q ∨ q = x)) cut' n t := by
  have grow := concl_grows parent wf wellFormed C hCk hfin S x hx
  intro n
  induction n with
  | zero =>
    intro t ⟨o, a, hp⟩
    exact ⟨o, a, pair_survivesG parent signer isWd offer isAcc holder shared wf wellFormed C hCk
      hfin S x hx _ _ cut cut' t o a hp
      (fun hv => hconf _ _ _ _ (fun _ z => z) grow o t hv) (hcut o t)
      (fun w hw _ => hnw w hw)⟩
  | succ n ih =>
    intro t ⟨o, a, hp⟩
    exact ⟨o, a, pair_survivesG parent signer isWd offer isAcc holder shared wf wellFormed C hCk
      hfin S x hx _ _ cut cut' t o a hp
      (fun hv => hconf _ _ _ _ ih grow o t hv) (hcut o t)
      (fun w hw _ => hnw w hw)⟩

end Rule

/-! ### (3) The mark, derived

  seat.py line 180: an offer is ended for the key `k` it seats by a withdrawal naming it that
  is signed by `k`, or by a signer who is not seated by the row when the row does not declare
  `conf = group`. So the mark is: the row declares a count, or the row seats its own signer.
  The declared conferrer rule reads the declaration: a row that declares a count is conferred
  by `confGroup`, and any other row by a rule that names one key (`solo`). -/

section Mark

variable {Row Key T : Type}
variable (signer : Row → Key) (offer : Row → T → Prop) (holder : T → Key)
variable (declGroup : Row → Prop)

/-- The mark of seat.py. -/
def sharedK (o : Row) : Prop := declGroup o ∨ ∃ t, offer o t ∧ holder t = signer o

variable (voice : Row → Row → Prop) (member : T → Row → Prop) (need : T → Nat)
variable (solo : (T → Prop) → (Row → Prop) → Row → T → Prop)

/-- The conferrer rule the row declares. -/
def confDecl (Q : T → Prop) (A : Row → Prop) (o : Row) (t : T) : Prop :=
  (declGroup o ∧ confGroup signer holder voice member need Q A o t) ∨
    (¬ declGroup o ∧ solo Q A o t)

theorem confDecl_mono (hs : ConfMono solo) :
    ConfMono (confDecl signer holder declGroup voice member need solo) :=
  fun Q Q' A A' hQ hA o t h => h.elim
    (fun h => Or.inl ⟨h.1, confGroup_mono signer holder voice member need Q Q' A A' hQ hA o t h.2⟩)
    (fun h => Or.inr ⟨h.1, hs Q Q' A A' hQ hA o t h.2⟩)

/-- (3) THE MARK, DERIVED, for a count. An offer that declares a count, conferred under the
    declared rule with need at least two, has a conferring voice, concluded and seated, whose
    signer is not the offer's signer: the proposer is not its sole conferrer. -/
theorem count_not_sole (Q : T → Prop) (A : Row → Prop) (o : Row) (t : T)
    (hg : declGroup o) (hneed : 2 ≤ need t)
    (h : confDecl signer holder declGroup voice member need solo Q A o t) :
    ∃ v, A v ∧ voice v o ∧ signer v ≠ signer o ∧
      ∃ t', Q t' ∧ holder t' = signer v ∧ member t' o := by
  have hc : confGroup signer holder voice member need Q A o t :=
    h.elim (fun h => h.2) (fun h => absurd hg h.1)
  obtain ⟨l, hp, hn, hv⟩ := hc
  match l, hp, hn, hv with
  | [], _, hn, _ => exact absurd hn (by simp; omega)
  | [_], _, hn, _ => exact absurd hn (by simp; omega)
  | v1 :: v2 :: _, hp, _, hv =>
    have h12 : signer v1 ≠ signer v2 := List.rel_of_pairwise_cons hp (List.mem_cons_self _ _)
    have m1 := hv v1 (List.mem_cons_self _ _)
    have m2 := hv v2 (List.mem_cons_of_mem _ (List.mem_cons_self _ _))
    if e : signer v1 = signer o then
      exact ⟨v2, m2.1, m2.2.1, fun e2 => h12 (e.trans e2.symm), m2.2.2⟩
    else
      exact ⟨v1, m1.1, m1.2.1, e, m1.2.2⟩

/-- So every pair of the refined walk under the declared rule on a row that declares a count
    with need at least two rests on a voice other than the proposer's. -/
theorem count_offer_not_sole {isWd : Row → Prop} {isAcc : Row → Prop} {parent : Row → Row → Prop}
    (P W : Row → Prop) (Q : T → Prop) (cut : Row → T → Prop) (t : T) (o a : Row)
    (hg : declGroup o) (hneed : 2 ≤ need t)
    (h : F4.seatByG parent signer isWd offer isAcc holder (sharedK signer offer holder declGroup)
      P W (confDecl signer holder declGroup voice member need solo Q P) cut t o a) :
    ∃ v, P v ∧ voice v o ∧ signer v ≠ signer o :=
  let ⟨v, h1, h2, h3, _⟩ := count_not_sole signer holder declGroup voice member need solo Q P o t hg
    hneed h.2.2.1
  ⟨v, h1, h2, h3⟩

/-- (3) The other half: an offer that is not marked is conferred by the one-key rule, and it
    seats only keys other than its signer. Its signer is its sole conferrer, as Seat.lean
    has it. -/
theorem unmarked_sole (Q : T → Prop) (A : Row → Prop) (o : Row) (t : T)
    (hns : ¬ sharedK signer offer holder declGroup o)
    (h : confDecl signer holder declGroup voice member need solo Q A o t) :
    solo Q A o t ∧ ∀ t', offer o t' → holder t' ≠ signer o :=
  ⟨h.elim (fun h => absurd (Or.inl h.1) hns) (fun h => h.2),
   fun t' ho e => hns (Or.inr ⟨t', ho, e⟩)⟩

end Mark

/-! ### (5) The refined walk inside the cut: `Kernel.seated`, refined -/

section SeatCutG

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (isWd : Row → Prop)
variable (offer : Row → T → Prop) (isAcc : Row → Prop) (holder : T → Key)
variable (shared : Row → Prop)
variable (conf : (T → Prop) → (Row → Prop) → Row → T → Prop)
variable (cutsSeat : Row → T → Prop) (mayCut : T → Row → Prop)

/-- `Kernel.entSeat` over the refined walk. -/
def entSeatG (n : Nat) (A X : Row → Prop) (c : Row) : Prop :=
  ∃ t, mayCut t c ∧ holder t = signer c ∧
    F4.standsG parent signer isWd offer isAcc holder shared conf
      (fun r => A r ∧ TransGen parent r c) (fun r => A r ∧ TransGen parent r c)
      (cutOut parent cutsSeat (fun x => X x ∧ TransGen parent x c)) n t

theorem entSeatG_anti (hconf : ConfMono conf) (n : Nat) :
    EntAnti (entSeatG parent signer isWd offer isAcc holder shared conf cutsSeat mayCut n) :=
  fun _ _ _ hXY _ ⟨t, h1, h2, h3⟩ =>
    ⟨t, h1, h2, standsG_mono parent signer isWd offer isAcc holder shared conf hconf _ _ _ _ _ _
      (fun _ h => h) (fun _ h => h)
      (fun _ _ ⟨x, hx, hc⟩ => ⟨x, ⟨hXY x hx.1, hx.2⟩, hc⟩) n t h3⟩

variable (isCut : Row → Prop) (clashes overrules : Row → Row → Prop)

/-- `Kernel.seated` over the refined walk. -/
def seatedG (n : Nat) (A : Row → Prop) : T → Prop :=
  F4.standsG parent signer isWd offer isAcc holder shared conf A A
    (cutOut parent cutsSeat (cutCounts parent isCut clashes overrules
      (entSeatG parent signer isWd offer isAcc holder shared conf cutsSeat mayCut n) A)) n

theorem seatedG_function (C : (Row → Prop) → Row → Prop) (n : Nat) (S S' : Row → Prop)
    (h : ∀ r, S r ↔ S' r) :
    seatedG parent signer isWd offer isAcc holder shared conf cutsSeat mayCut isCut clashes
        overrules n (C S)
      = seatedG parent signer isWd offer isAcc holder shared conf cutsSeat mayCut isCut clashes
        overrules n (C S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

/-- The link to `Kernel.seated`. With no shared offer and no holder's withdrawal against an
    offer it did not sign, the refined entitlement, the refined cut status and the refined
    seated set are those of Seat.lean. -/
theorem seatedG_eq_seated (hconf : ConfMono conf) (hns : ∀ o, ¬ shared o) (n : Nat)
    (A : Row → Prop) (hno : NoHolderWdOnOffer parent signer isWd offer holder A) :
    seatedG parent signer isWd offer isAcc holder shared conf cutsSeat mayCut isCut clashes
        overrules n A
      = seated parent signer isWd offer isAcc holder conf cutsSeat mayCut isCut clashes
        overrules n A := by
  have hent : ∀ X c, entSeatG parent signer isWd offer isAcc holder shared conf cutsSeat
      mayCut n A X c ↔ entSeat parent signer isWd offer isAcc holder conf cutsSeat mayCut n A X c := by
    intro X c
    constructor
    · intro ⟨t, h1, h2, h3⟩
      exact ⟨t, h1, h2, standsG_le_stands parent signer isWd offer isAcc holder shared conf
        hconf hns _ _ _ n t h3⟩
    · intro ⟨t, h1, h2, h3⟩
      refine ⟨t, h1, h2, ?_⟩
      have hno' : NoHolderWdOnOffer parent signer isWd offer holder
          (fun r => A r ∧ TransGen parent r c) :=
        fun o t w ho hW hwd hp hs => hno o t w ho hW.1 hwd hp hs
      rw [standsG_eq_stands parent signer isWd offer isAcc holder shared conf hns _ _ _ hno']
      exact h3
  have hT : cutT parent isCut clashes overrules
        (entSeatG parent signer isWd offer isAcc holder shared conf cutsSeat mayCut n) A
      = cutT parent isCut clashes overrules
        (entSeat parent signer isWd offer isAcc holder conf cutsSeat mayCut n) A := by
    funext X c
    apply propext
    exact ⟨fun ⟨a, b, e, d, f⟩ => ⟨a, b, (hent X c).1 e, d, f⟩,
      fun ⟨a, b, e, d, f⟩ => ⟨a, b, (hent X c).2 e, d, f⟩⟩
  have hC : cutCounts parent isCut clashes overrules
        (entSeatG parent signer isWd offer isAcc holder shared conf cutsSeat mayCut n) A
      = cutCounts parent isCut clashes overrules
        (entSeat parent signer isWd offer isAcc holder conf cutsSeat mayCut n) A := by
    unfold cutCounts
    rw [hT]
  unfold seatedG seated
  rw [hC, standsG_eq_stands parent signer isWd offer isAcc holder shared conf hns _ _ _ hno]

end SeatCutG

/-! ### The proviso is needed: a witness -/

namespace Witness

set_option linter.constructorNameAsVariable false

inductive R | o | a | w
  deriving DecidableEq
inductive K | c | h
  deriving DecidableEq

def parent (p r : R) : Prop := (p = R.o ∧ r = R.a) ∨ (p = R.o ∧ r = R.w)
def signer : R → K | R.o => K.c | R.a => K.h | R.w => K.h
def isWd (r : R) : Prop := r = R.w
def offer (o : R) (_ : Unit) : Prop := o = R.o
def isAcc (r : R) : Prop := r = R.a
def holder (_ : Unit) : K := K.h
def All (_ : R) : Prop := True

/-- No offer is shared. The holder `h` withdraws against the offer `o` that `c` signed. The
    pair of Seat.lean stands (that withdrawal is not `o`'s signer's), the refined pair does
    not (it is the holder's own). -/
theorem unshared_not_equal :
    seat parent signer isWd offer isAcc holder All All (fun _ _ => True) (fun _ _ => False) () ∧
      ¬ F4.seatG parent signer isWd offer isAcc holder (fun _ => False) All All
        (fun _ _ => True) (fun _ _ => False) () := by
  constructor
  · refine ⟨R.o, R.a, trivial, rfl, trivial, trivial, Or.inl ⟨rfl, Or.inl ⟨rfl, rfl⟩⟩, rfl,
      ?_, ?_, fun x => x⟩
    · intro ⟨w, ⟨hw, _, hs⟩, _⟩
      cases w <;> simp_all [signer, isWd]
    · intro ⟨w, ⟨_, hp, _⟩, _⟩
      rcases hp with ⟨h1, _⟩ | ⟨h1, _⟩ <;> cases h1
  · intro ⟨o, a, _, ho, _, _, _, _, h7, _, _⟩
    cases ho
    exact h7 ⟨R.w, trivial, rfl, Or.inr ⟨rfl, rfl⟩, Or.inl rfl⟩

end Witness

end SeatG

/-! ## Axioms used -/

#print axioms SeatG.standsG_mono
#print axioms SeatG.standsG_deeper
#print axioms SeatG.standsG_shared_mono
#print axioms SeatG.seatByG_iff_seatBy
#print axioms SeatG.standsG_le_stands
#print axioms SeatG.standsG_eq_stands
#print axioms SeatG.no_offer_no_seatG
#print axioms SeatG.no_acceptance_no_seatG
#print axioms SeatG.standsG_two_voices
#print axioms SeatG.offer_withdrawal_endsG
#print axioms SeatG.third_key_cannot_endG
#print axioms SeatG.only_withdrawals_and_cuts_endG
#print axioms SeatG.count_not_sole
#print axioms SeatG.count_offer_not_sole
#print axioms SeatG.unmarked_sole
#print axioms SeatG.confDecl_mono
#print axioms SeatG.entSeatG_anti
#print axioms SeatG.seatedG_function
#print axioms SeatG.seatedG_eq_seated
#print axioms SeatG.Witness.unshared_not_equal

end Kernel
