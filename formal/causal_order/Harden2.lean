/-
  Harden2.lean — the hardening rules of KERNEL.md section 8a, rules 5 to 7

    F5  Among several founding keys one founder's unseat concludes nothing, and a founder's
        own offers live only while that founder's seat does.        (F5, Founders, Two)
    F6  A row that names another adds its audience to it only if it is concluded and its
        signer was already in that audience.                        (F6, AudRows)
    F7  The holders of a counted scope are the keys common to the tips.     (F7, TipRows)

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Harden.lean.
-/

import Harden

namespace Kernel

namespace Harden

open Order Relation Causal

/-! ## F5. Several founding keys

  Before the rule, each key that signed a founding row was "the object's own key": its unseat
  of another founder was entitled on its signature alone, and an offer it signed was conferred
  `self` for good. The rule has two halves.

  (a) Ending a founding seat takes its holder's own withdrawal or a count: the entitlement of
      a cut on a founding seat needs two concluded voices by distinct keys (`TwoVoices`).
  (b) A founder's `self` offer over the founded object is conferred under that founder's own
      founding seat, like any delegation: `conf5` has the founding row at the root, and above
      it only `confSingle` and `confGroup`. `confOwn` is the conferrer rule it replaces. -/

namespace F5

section Cut

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key)
variable (isCut : Row → Prop) (clashes overrules : Row → Row → Prop)
variable (ent : (Row → Prop) → (Row → Prop) → Row → Prop)
/- `voice v c`: `v` is a voice for the cut `c` (the cut itself, or a cosignature of it).
   `onF c`: `c` cuts a founding seat. -/
variable (voice : Row → Row → Prop) (onF : Row → Prop)

/-- THE RULE (a), as a property of the cut's entitlement: whatever does the voiding, a cut
    on a founding seat is entitled only with two concluded voices by distinct keys. -/
def TwoVoices : Prop :=
  ∀ (A X : Row → Prop) (c : Row), onF c → ent A X c →
    ∃ l : List Row, l.Pairwise (fun u v => signer u ≠ signer v) ∧ 2 ≤ l.length ∧
      ∀ v, v ∈ l → A v ∧ voice v c

/-- A cut on a founding seat that counts, or is even contested, has two concluded voices by
    two keys. -/
theorem cut_needs_two_voices (h2 : TwoVoices signer ent voice onF) (A : Row → Prop) (c : Row)
    (hc : onF c) (hp : cutPoss parent isCut clashes overrules ent A c) :
    ∃ v1 v2, A v1 ∧ A v2 ∧ voice v1 c ∧ voice v2 c ∧ signer v1 ≠ signer v2 := by
  have he : ent A _ c := hp.2.2.1
  obtain ⟨l, hpw, hn, hv⟩ := h2 A _ c hc he
  match l, hpw, hn, hv with
  | [], _, hn, _ => simp at hn
  | [_], _, hn, _ => simp at hn
  | a :: b :: rest, hpw, _, hv =>
    have ha := hv a (List.mem_cons_self _ _)
    have hb := hv b (List.mem_cons_of_mem _ (List.mem_cons_self _ _))
    exact ⟨a, b, ha.1, hb.1, ha.2, hb.2, (List.pairwise_cons.1 hpw).1 b (List.mem_cons_self _ _)⟩

/-- (i) THE TWO-VOICE FLOOR AT THE ROOT. If every concluded voice for a cut on a founding
    seat is signed by one key, the cut is void: it neither counts nor is contested. However
    many rows one founder signs, it cuts no founding seat. -/
theorem one_key_cuts_nothing (h2 : TwoVoices signer ent voice onF) (A : Row → Prop) (c : Row)
    (k : Key) (hc : onF c) (hone : ∀ v, A v → voice v c → signer v = k) :
    ¬ cutPoss parent isCut clashes overrules ent A c :=
  fun hp =>
    let ⟨v1, v2, a1, a2, b1, b2, hne⟩ :=
      cut_needs_two_voices parent signer isCut clashes overrules ent voice onF h2 A c hc hp
    hne ((hone v1 a1 b1).trans (hone v2 a2 b2).symm)

/-- A cut that counts is concluded. -/
theorem counts_concluded (A : Row → Prop) (c : Row)
    (h : cutCounts parent isCut clashes overrules ent A c) : A c :=
  lfp_least _ A (fun _ hq => hq.1) c h

/-- BEFORE the rule. A concluded cut that nothing clashes with or overrules, and whose signer
    is entitled alone, counts. -/
theorem counts_of_unopposed (A : Row → Prop) (c : Row) (hA : A c) (hcut : isCut c)
    (hent : ∀ X, ent A X c) (hcl : ∀ x, ¬ clashes x c) (hov : ∀ x, ¬ overrules x c) :
    cutCounts parent isCut clashes overrules ent A c :=
  fun _ hP => hP c ⟨hA, hcut, hent _, fun ⟨x, _, _, h⟩ => hcl x h, fun ⟨x, _, _, h⟩ => hov x h⟩

variable (isWd : Row → Prop) (offer : Row → T → Prop) (isAcc : Row → Prop) (holder : T → Key)
variable (shared : Row → Prop) (cutsSeat : Row → T → Prop)

/-- (i), at the seat. The pair (o, a) on a founding row `o` (`shared o`: the row seats its
    own signer among others, so its signer is not its sole conferrer). Its positive part
    holds; the seat's holder has withdrawn neither row; and every concluded voice for a cut
    on this seat is signed by one key `k`. Then the pair is live, against every cut that
    counts or is contested. Nothing is asked of `k`: it may be another founder, with any
    number of rows. -/
theorem no_single_founder_removes (h2 : TwoVoices signer ent voice onF) (A X : Row → Prop)
    (hX : ∀ c, X c → cutPoss parent isCut clashes overrules ent A c)
    (V : Row → T → Prop) (t : T) (o a : Row) (k : Key)
    (hpos : A o ∧ offer o t ∧ V o t ∧ A a ∧ accLink parent isAcc o a ∧ signer a = holder t)
    (hsh : shared o)
    (hstay : ¬ ∃ w, A w ∧ isWd w ∧ (parent o w ∨ parent a w) ∧ signer w = holder t)
    (honF : ∀ c, cutsSeat c t → onF c)
    (hone : ∀ c v, cutsSeat c t → A v → voice v c → signer v = k) :
    F4.seatByG parent signer isWd offer isAcc holder shared A A V (cutOut parent cutsSeat X) t o a :=
  (F4.shared_iff parent signer isWd offer isAcc holder shared A A V _ t o a hsh).2
    ⟨hpos.1, hpos.2.1, hpos.2.2.1, hpos.2.2.2.1, hpos.2.2.2.2.1, hpos.2.2.2.2.2, hstay,
     fun ⟨c, hc, hcs, _⟩ =>
       one_key_cuts_nothing parent signer isCut clashes overrules ent voice onF h2 A c k
         (honF c hcs) (fun v hA hv => hone c v hcs hA hv) (hX c hc)⟩

/-- (iv), first half: THE PRICE WITH TWO FOUNDERS. Suppose the only keys with a concluded
    voice for a cut on seat `t` are `k` and the seat's own holder (two founders), and the
    holder has signed no voice for its own removal. Then no cut removes `t`: with exactly two
    founders neither can remove the other, however hostile the other is. -/
theorem two_founders_neither_removes (h2 : TwoVoices signer ent voice onF) (A X : Row → Prop)
    (hX : ∀ c, X c → cutPoss parent isCut clashes overrules ent A c)
    (V : Row → T → Prop) (t : T) (o a : Row) (k : Key)
    (hpos : A o ∧ offer o t ∧ V o t ∧ A a ∧ accLink parent isAcc o a ∧ signer a = holder t)
    (hsh : shared o)
    (hstay : ¬ ∃ w, A w ∧ isWd w ∧ (parent o w ∨ parent a w) ∧ signer w = holder t)
    (honF : ∀ c, cutsSeat c t → onF c)
    (hfew : ∀ c v, cutsSeat c t → A v → voice v c → signer v = k ∨ signer v = holder t)
    (hself : ∀ c v, cutsSeat c t → A v → voice v c → signer v ≠ holder t) :
    F4.seatByG parent signer isWd offer isAcc holder shared A A V (cutOut parent cutsSeat X) t o a :=
  no_single_founder_removes parent signer isCut clashes overrules ent voice onF isWd offer isAcc
    holder shared cutsSeat h2 A X hX V t o a k hpos hsh hstay honF
    (fun c v hcs hA hv => (hfew c v hcs hA hv).elim id (fun e => absurd e (hself c v hcs hA hv)))

end Cut

section Walk

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (isWd : Row → Prop)
variable (offer : Row → T → Prop) (isAcc : Row → Prop) (holder : T → Key)
variable (shared : Row → Prop)
/- `isRoot o t`: `o` is the founding row of `t`'s object and seats `t`. `isF t`: `t` is a
   founding seat. `mayConfer t' t`: the seat `t'` may confer `t`; a founder's `self` offer is
   conferred under the founder's own founding seat, so it is an instance. -/
variable (isRoot : Row → T → Prop) (mayConfer : T → T → Prop)
variable (voice : Row → Row → Prop) (member : T → Row → Prop) (need : T → Nat)
variable (isF : T → Prop)

/-- THE RULE (b), the conferrer rule over a founded object: the founding row, a seat that may
    confer, or a count. No key is "the object's own key". -/
def conf5 (Q : T → Prop) (A : Row → Prop) (o : Row) (t : T) : Prop :=
  isRoot o t ∨ confSingle signer holder mayConfer Q A o t ∨
    confGroup signer holder voice member need Q A o t

/-- BEFORE the rule: the offer is signed by one of the object's own keys (the signers of its
    founding row), whatever has become of that signer's seat. With one own key this is
    `Kernel.confSelf`. -/
def confOwn (ownKey : T → Key → Prop) (_ : T → Prop) (_ : Row → Prop) (o : Row) (t : T) : Prop :=
  ownKey t (signer o)

theorem conf5_mono : ConfMono (conf5 signer holder isRoot mayConfer voice member need) :=
  fun Q Q' A A' hQ hA o t h =>
    h.elim Or.inl (fun h => Or.inr (h.elim
      (fun x => Or.inl (confSingle_mono signer holder mayConfer Q Q' A A' hQ hA o t x))
      (fun x => Or.inr (confGroup_mono signer holder voice member need Q Q' A A' hQ hA o t x))))

/-- One step of the walk, for one key `k`. -/
theorem step_one (P W : Row → Prop) (cut : Row → T → Prop) (k : Key) (Q : T → Prop)
    (hroot : ∀ t o a, isF t → holder t = k →
      ¬ F4.seatByG parent signer isWd offer isAcc holder shared P W (fun o t => isRoot o t) cut t o a)
    (hF : ∀ t' t, isF t → mayConfer t' t → isF t')
    (hown : ∀ o t, isF t → holder t = k → P o → offer o t → ¬ isRoot o t →
      signer o = k ∧ ∀ Q', ¬ confGroup signer holder voice member need Q' P o t)
    (hQ : ∀ t', isF t' → holder t' = k → ¬ Q t') (t : T) (hFt : isF t) (hk : holder t = k) :
    ¬ F4.seatG parent signer isWd offer isAcc holder shared P W
      (conf5 signer holder isRoot mayConfer voice member need Q P) cut t := by
  intro ⟨o, a, h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
  cases Classical.em (isRoot o t) with
  | inl hr => exact hroot t o a hFt hk ⟨h1, h2, hr, h4, h5, h6, h7, h8, h9⟩
  | inr hnr =>
    have ⟨hs, hng⟩ := hown o t hFt hk h1 h2 hnr
    cases h3 with
    | inl hr => exact hnr hr
    | inr h3 =>
      cases h3 with
      | inl hsg =>
        obtain ⟨t', hq, hh, hm⟩ := hsg
        exact hQ t' (hF t' t hFt hm) (hh.trans hs) hq
      | inr hg => exact hng Q hg

/-- (ii) A REMOVED FOUNDER CANNOT RE-SEAT ITSELF. Let `k`'s founding seats by the founding
    row be ended (`hroot`: by its withdrawal or by a cut, whichever). Suppose a founding seat
    is conferred only under a founding seat (`hF`), and every other offer of a founding seat
    to `k` is signed by `k` itself and is not a count (`hown`). Then no founding seat of `k`
    stands, at any depth. Whatever such offers name is not asked: naming the removal to escape
    the cut gains nothing. -/
theorem removed_cannot_reseat (P W : Row → Prop) (cut : Row → T → Prop) (k : Key)
    (hroot : ∀ t o a, isF t → holder t = k →
      ¬ F4.seatByG parent signer isWd offer isAcc holder shared P W (fun o t => isRoot o t) cut t o a)
    (hF : ∀ t' t, isF t → mayConfer t' t → isF t')
    (hown : ∀ o t, isF t → holder t = k → P o → offer o t → ¬ isRoot o t →
      signer o = k ∧ ∀ Q', ¬ confGroup signer holder voice member need Q' P o t) :
    ∀ n t, isF t → holder t = k →
      ¬ F4.standsG parent signer isWd offer isAcc holder shared
        (conf5 signer holder isRoot mayConfer voice member need) P W cut n t := by
  intro n
  induction n with
  | zero =>
    intro t hFt hk
    exact step_one parent signer isWd offer isAcc holder shared isRoot mayConfer voice member need
      isF P W cut k (fun _ => False) hroot hF hown (fun _ _ _ h => h) t hFt hk
  | succ n ih =>
    intro t hFt hk
    exact step_one parent signer isWd offer isAcc holder shared isRoot mayConfer voice member need
      isF P W cut k _ hroot hF hown ih t hFt hk

/-- (iii) A FOUNDER'S OWN GRANT ENDS WITH ITS SEAT. Let no founding seat of `k` stand. Let
    `t` be a seat every offer of which is signed by `k`, is not a founding row and is not a
    count, and which only a founding seat may confer (a `self` grant by the founder). Then
    `t` does not stand, at any depth. -/
theorem self_grant_falls (P W : Row → Prop) (cut : Row → T → Prop) (k : Key)
    (hdead : ∀ n t', isF t' → holder t' = k →
      ¬ F4.standsG parent signer isWd offer isAcc holder shared
        (conf5 signer holder isRoot mayConfer voice member need) P W cut n t')
    (t : T)
    (hoff : ∀ o, P o → offer o t →
      signer o = k ∧ ¬ isRoot o t ∧ ∀ Q', ¬ confGroup signer holder voice member need Q' P o t)
    (hself : ∀ t', mayConfer t' t → isF t') :
    ∀ n, ¬ F4.standsG parent signer isWd offer isAcc holder shared
      (conf5 signer holder isRoot mayConfer voice member need) P W cut n t := by
  intro n
  cases n with
  | zero =>
    intro ⟨o, a, h1, h2, h3, _⟩
    have ⟨_, hnr, hng⟩ := hoff o h1 h2
    exact h3.elim hnr (fun h => h.elim (fun ⟨_, hq, _, _⟩ => hq) (hng _))
  | succ n =>
    intro ⟨o, a, h1, h2, h3, _⟩
    have ⟨hs, hnr, hng⟩ := hoff o h1 h2
    exact h3.elim hnr (fun h => h.elim
      (fun ⟨t', hq, hh, hm⟩ => hdead n t' (hself t' hm) (hh.trans hs) hq) (hng _))

/-- And so does what was conferred under that grant, link by link: a seat that only a seat
    which never stands may confer, never stands. -/
theorem under_dead_falls (P W : Row → Prop) (cut : Row → T → Prop) (t0 t : T)
    (hdead : ∀ n, ¬ F4.standsG parent signer isWd offer isAcc holder shared
      (conf5 signer holder isRoot mayConfer voice member need) P W cut n t0)
    (hoff : ∀ o, P o → offer o t →
      ¬ isRoot o t ∧ ∀ Q', ¬ confGroup signer holder voice member need Q' P o t)
    (hunder : ∀ t', mayConfer t' t → t' = t0) :
    ∀ n, ¬ F4.standsG parent signer isWd offer isAcc holder shared
      (conf5 signer holder isRoot mayConfer voice member need) P W cut n t := by
  intro n
  cases n with
  | zero =>
    intro ⟨o, a, h1, h2, h3, _⟩
    have ⟨hnr, hng⟩ := hoff o h1 h2
    exact h3.elim hnr (fun h => h.elim (fun ⟨_, hq, _, _⟩ => hq) (hng _))
  | succ n =>
    intro ⟨o, a, h1, h2, h3, _⟩
    have ⟨hnr, hng⟩ := hoff o h1 h2
    exact h3.elim hnr (fun h => h.elim
      (fun ⟨t', hq, _, hm⟩ => hdead n ((hunder t' hm) ▸ hq)) (hng _))

/-- One step of the walk, for all founders. -/
theorem step_all (P W : Row → Prop) (cut : Row → T → Prop) (Q : T → Prop)
    (hroot : ∀ t o a, isF t →
      ¬ F4.seatByG parent signer isWd offer isAcc holder shared P W (fun o t => isRoot o t) cut t o a)
    (hF : ∀ t' t, isF t → mayConfer t' t → isF t')
    (hG : ∀ t' o t, isF t → offer o t → member t' o → isF t')
    (hneed : ∀ t, isF t → 1 ≤ need t)
    (hQ : ∀ t', isF t' → ¬ Q t') (t : T) (hFt : isF t) :
    ¬ F4.seatG parent signer isWd offer isAcc holder shared P W
      (conf5 signer holder isRoot mayConfer voice member need Q P) cut t := by
  intro ⟨o, a, h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
  cases h3 with
  | inl hr => exact hroot t o a hFt ⟨h1, h2, hr, h4, h5, h6, h7, h8, h9⟩
  | inr h3 =>
    cases h3 with
    | inl hsg =>
      obtain ⟨t', hq, _, hm⟩ := hsg
      exact hQ t' (hF t' t hFt hm) hq
    | inr hg =>
      obtain ⟨l, _, hn, hv⟩ := hg
      have h1' := Nat.le_trans (hneed t hFt) hn
      match l, h1', hv with
      | [], h1', _ => simp at h1'
      | v :: _, _, hv =>
        obtain ⟨_, _, t', hq, _, hm⟩ := hv v (List.mem_cons_self _ _)
        exact hQ t' (hG t' o t hFt h2 hm) hq

/-- (iv), second half, at one set: AN EMPTIED FOUNDER SET STAYS EMPTY. Let every founding
    seat's pair on the founding row be ended (`hroot`). A founding seat is otherwise conferred
    only under a founding seat (`hF`) or by a count of founding seats, of at least one
    (`hG`, `hneed`). Then no founding seat stands at any depth, whatever other rows are held:
    offers, acceptances, cosignatures, by anyone, naming anything. -/
theorem emptied_founders_stay_empty (P W : Row → Prop) (cut : Row → T → Prop)
    (hroot : ∀ t o a, isF t →
      ¬ F4.seatByG parent signer isWd offer isAcc holder shared P W (fun o t => isRoot o t) cut t o a)
    (hF : ∀ t' t, isF t → mayConfer t' t → isF t')
    (hG : ∀ t' o t, isF t → offer o t → member t' o → isF t')
    (hneed : ∀ t, isF t → 1 ≤ need t) :
    ∀ n t, isF t → ¬ F4.standsG parent signer isWd offer isAcc holder shared
      (conf5 signer holder isRoot mayConfer voice member need) P W cut n t := by
  intro n
  induction n with
  | zero =>
    intro t hFt
    exact step_all parent signer isWd offer isAcc holder shared isRoot mayConfer voice member need
      isF P W cut (fun _ => False) hroot hF hG hneed (fun _ _ h => h) t hFt
  | succ n ih =>
    intro t hFt
    exact step_all parent signer isWd offer isAcc holder shared isRoot mayConfer voice member need
      isF P W cut _ hroot hF hG hneed ih t hFt

/-- (iv), second half, for ever: NO ROW RESTORES A FOUNDER. Let `g` be the one founding row
    of the object, and at the set `S` let each founding seat be ended by a concluded
    withdrawal against `g` (each founder resigned). Then at every later set `S'`, under every
    cut relation, no founding seat stands at any depth. "At least one founder" is kept by no
    rule: nothing here stops the last two from resigning concurrently
    (`Two.each_alone_leaves_one`, `Two.both_resign_none_for_ever`), and once none is left
    nothing in the kernel brings one back. -/
theorem no_row_restores_a_founder (wf : WellFounded parent) (wellFormed : Row → Prop)
    (C : (Row → Prop) → Row → Prop)
    (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
    (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
      (C S r ↔ C (fun q => S q ∨ q = x) r))
    (S S' : Row → Prop) (hg : Recount.Grows S S') (g : Row)
    (hone : ∀ o t, isF t → isRoot o t → o = g)
    (hres : ∀ t, isF t → F4.offEnded parent signer isWd holder shared (C S) g t)
    (hF : ∀ t' t, isF t → mayConfer t' t → isF t')
    (hG : ∀ t' o t, isF t → offer o t → member t' o → isF t')
    (hneed : ∀ t, isF t → 1 ≤ need t) (cut : Row → T → Prop) :
    ∀ n t, isF t → ¬ F4.standsG parent signer isWd offer isAcc holder shared
      (conf5 signer holder isRoot mayConfer voice member need) (C S') (C S') cut n t :=
  emptied_founders_stay_empty parent signer isWd offer isAcc holder shared isRoot mayConfer voice
    member need isF (C S') (C S') cut
    (fun t o a hFt h => by
      have e : o = g := hone o t hFt h.2.2.1
      obtain ⟨w, hW, r⟩ := hres t hFt
      exact h.2.2.2.2.2.2.1 (e ▸ ⟨w, (Recount.concl_grows parent wf wellFormed C hfin S S' w hg
        (hCk S w hW)).1 hW, r⟩))
    hF hG hneed

end Walk

end F5

/-! ### F5, the witnesses (attacks.py tests 14, 23 and 7)

  `g`: f1, f2, f3 found the group (`a2`, `a3`: the acceptances of f2 and f3). `c3`, `xf`: f2
  and f3 remove f1 by the count. `u2`: f1 alone signs an unseat of f2, naming only `g`. `re`:
  f1 signs itself an offer of the founder's seat, naming the removal. `ds`, `aks`: f1's own
  grant of "moderate" to K, and K's acceptance. -/

namespace Founders

inductive R | g | a2 | a3 | c3 | xf | u2 | re | ds | aks
  deriving DecidableEq, Repr

inductive Key | f1 | f2 | f3 | K
  deriving DecidableEq, Repr

/-- The three founder seats and K's "moderate". -/
inductive T | F1 | F2 | F3 | M
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | g, a2 => true | g, a3 => true | g, c3 => true | g, xf => true | c3, xf => true
  | g, u2 => true | xf, re => true | g, ds => true | ds, aks => true
  | _, _ => false
def parent (a b : R) : Prop := parentB a b = true

def ancB : R → R → Bool
  | g, a2 => true | g, a3 => true | g, c3 => true | g, xf => true | g, u2 => true
  | g, re => true | g, ds => true | g, aks => true
  | c3, xf => true | c3, re => true | xf, re => true | ds, aks => true
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
  | g => Key.f1 | a2 => Key.f2 | a3 => Key.f3 | c3 => Key.f3 | xf => Key.f2 | u2 => Key.f1
  | re => Key.f1 | ds => Key.f1 | aks => Key.K

def holder : T → Key | T.F1 => Key.f1 | T.F2 => Key.f2 | T.F3 => Key.f3 | T.M => Key.K

def isWd (_ : R) : Prop := False
def isAcc (r : R) : Prop := r = a2 ∨ r = a3 ∨ r = aks

def offerB : R → T → Bool
  | g, T.F1 => true | g, T.F2 => true | g, T.F3 => true | re, T.F1 => true | ds, T.M => true
  | _, _ => false
def offer (o : R) (t : T) : Prop := offerB o t = true

def cutsSeatB : R → T → Bool | xf, T.F1 => true | u2, T.F2 => true | _, _ => false
def cutsSeat (c : R) (t : T) : Prop := cutsSeatB c t = true
def isCut (r : R) : Prop := r = xf ∨ r = u2

def voiceB : R → R → Bool | xf, xf => true | c3, xf => true | u2, u2 => true | _, _ => false
def voice (v c : R) : Prop := voiceB v c = true

def none2 (_ _ : R) : Prop := False
def shared (o : R) : Prop := o = g

def isFB : T → Bool | T.M => false | _ => true
def isF (t : T) : Prop := isFB t = true
def isRoot (o : R) (t : T) : Prop := o = g ∧ isF t
/-- A founder's `self` offer over the group is conferred under its founding seat. -/
def mayConfer (t' _ : T) : Prop := isF t'

/-- No offer here is a count. -/
def voiceO (_ _ : R) : Prop := False
def memberO (_ : T) (_ : R) : Prop := True
def needO (_ : T) : Nat := 1

def All (_ : R) : Prop := True
/-- The rows before the removal of f1. -/
abbrev Pre (r : R) : Prop := r ≠ xf

/-- BEFORE: the three signers of the founding row are the object's own keys. -/
def ownKey (_ : T) (k : Key) : Prop := k ≠ Key.K
def entOld (_ _ : R → Prop) (c : R) : Prop := signer c ≠ Key.K

/-- WITH the rule: a cut is entitled by two concluded voices of distinct keys. -/
def entNew (A : R → Prop) (_ : R → Prop) (c : R) : Prop :=
  ∃ l : List R, l.Pairwise (fun u v => signer u ≠ signer v) ∧ 2 ≤ l.length ∧
    ∀ v, v ∈ l → A v ∧ voice v c

def cutOld : R → T → Prop :=
  cutOut parent cutsSeat (cutCounts parent isCut none2 none2 entOld All)
def cutNew (A : R → Prop) : R → T → Prop :=
  cutOut parent cutsSeat (cutCounts parent isCut none2 none2 entNew A)

theorem no_group (Q' : T → Prop) (A : R → Prop) (o : R) (t : T) :
    ¬ confGroup signer holder voiceO memberO needO Q' A o t := by
  intro ⟨l, _, hn, hv⟩
  match l, hn, hv with
  | [], hn, _ => simp [needO] at hn
  | v :: _, _, hv => exact (hv v (List.mem_cons_self _ _)).2.1

/-! WITHOUT the rule. -/

theorem old_u2_counts : cutCounts parent isCut none2 none2 entOld All u2 :=
  F5.counts_of_unopposed parent isCut none2 none2 entOld All u2 trivial (Or.inr rfl)
    (fun _ => by show signer u2 ≠ Key.K; decide) (fun _ h => h) (fun _ h => h)

/-- (i) One founder alone unseats another: f2 has no seat. -/
theorem old_one_founder_removes (Q0 : T → Prop) :
    ¬ seat parent signer isWd offer isAcc holder All All (F5.confOwn signer ownKey Q0 All)
      cutOld T.F2 := by
  intro ⟨o, a, h⟩
  have ho : offerB o T.F2 = true := h.2.1
  have e : o = g := by cases o <;> simp [offerB] at ho <;> rfl
  subst e
  exact h.2.2.2.2.2.2.2.2 ⟨u2, old_u2_counts, rfl, fun ha => absurd (anc_sound ha) (by decide)⟩

/-- (ii) The removed founder seats itself again, by an offer that names its removal. -/
theorem old_removed_reseats (Q0 : T → Prop) :
    seatBy parent signer isWd offer isAcc holder All All (F5.confOwn signer ownKey Q0 All)
      cutOld T.F1 re re := by
  refine ⟨trivial, rfl, by show signer re ≠ Key.K; decide, trivial, Or.inr rfl, rfl,
    fun ⟨_, hw, _⟩ => hw.1, fun ⟨_, hw, _⟩ => hw.1, fun ⟨c, _, hcs, hn⟩ => ?_⟩
  have hcs' : cutsSeatB c T.F1 = true := hcs
  cases c <;> simp [cutsSeatB] at hcs'
  exact hn (TransGen.single rfl)

/-- (iii) The removed founder's grant to K stays live. -/
theorem old_grant_survives (Q0 : T → Prop) :
    seatBy parent signer isWd offer isAcc holder All All (F5.confOwn signer ownKey Q0 All)
      cutOld T.M ds aks := by
  refine ⟨trivial, rfl, by show signer ds ≠ Key.K; decide, trivial,
    Or.inl ⟨Or.inr (Or.inr rfl), rfl⟩, rfl,
    fun ⟨_, hw, _⟩ => hw.1, fun ⟨_, hw, _⟩ => hw.1, fun ⟨c, _, hcs, _⟩ => ?_⟩
  have hcs' : cutsSeatB c T.M = true := hcs
  cases c <;> simp [cutsSeatB] at hcs'

/-! WITH the rule. -/

theorem twoVoices_new : F5.TwoVoices signer entNew voice (fun _ => True) :=
  fun _ _ _ _ h => h

/-- (i) f1's lone unseat of f2 is void. -/
theorem new_u2_void : ¬ cutPoss parent isCut none2 none2 entNew All u2 :=
  F5.one_key_cuts_nothing parent signer isCut none2 none2 entNew voice (fun _ => True)
    twoVoices_new All u2 Key.f1 trivial (fun v _ hv => by
      have h' : voiceB v u2 = true := hv
      cases v <;> simp [voiceB] at h'
      rfl)

/-- (i) f2 keeps its seat, against every cut that counts or is contested. -/
theorem new_f2_keeps_seat :
    F4.seatByG parent signer isWd offer isAcc holder shared All All (fun _ _ => True)
      (cutOut parent cutsSeat (cutPoss parent isCut none2 none2 entNew All)) T.F2 g a2 :=
  F5.no_single_founder_removes parent signer isCut none2 none2 entNew voice (fun _ => True)
    isWd offer isAcc holder shared cutsSeat twoVoices_new All _ (fun _ h => h) _ T.F2 g a2 Key.f1
    ⟨trivial, rfl, trivial, trivial, Or.inl ⟨Or.inl rfl, rfl⟩, rfl⟩ rfl
    (fun ⟨_, _, hwd, _⟩ => hwd) (fun _ _ => trivial)
    (fun c v hcs _ hv => by
      have h1 : cutsSeatB c T.F2 = true := hcs
      have h2 : voiceB v c = true := hv
      cases c <;> simp [cutsSeatB] at h1
      cases v <;> simp [voiceB] at h2
      rfl)

/-- The count's removal of f1 does count: two voices, f2 and f3. -/
theorem new_xf_counts (A : R → Prop) (hx : A xf) (hc : A c3) :
    cutCounts parent isCut none2 none2 entNew A xf :=
  F5.counts_of_unopposed parent isCut none2 none2 entNew A xf hx (Or.inl rfl)
    (fun _ => ⟨[xf, c3], by simp [signer], Nat.le_refl 2, fun v hv => by
      simp only [List.mem_cons, List.mem_singleton, List.not_mem_nil, or_false] at hv
      cases hv with
      | inl e => subst e; exact ⟨hx, rfl⟩
      | inr e => subst e; exact ⟨hc, rfl⟩⟩)
    (fun _ h => h) (fun _ h => h)

/-- (ii) After its removal f1 holds no founder's seat at any depth, with `u2` and `re` held. -/
theorem new_removed_cannot_reseat : ∀ n t, isF t → holder t = Key.f1 →
    ¬ F4.standsG parent signer isWd offer isAcc holder shared
      (F5.conf5 signer holder isRoot mayConfer voiceO memberO needO) All All (cutNew All) n t := by
  apply F5.removed_cannot_reseat parent signer isWd offer isAcc holder shared isRoot mayConfer
    voiceO memberO needO isF All All (cutNew All) Key.f1
  · intro t o a _ hk h
    have e : o = g := h.2.2.1.1
    subst e
    cases t <;> simp [holder] at hk
    exact h.2.2.2.2.2.2.2.2 ⟨xf, new_xf_counts All trivial trivial, rfl,
      fun ha => absurd (anc_sound ha) (by decide)⟩
  · exact fun _ _ _ hm => hm
  · intro o t hFt hk _ ho hnr
    cases t <;> simp [holder] at hk
    have ho' : offerB o T.F1 = true := ho
    cases o <;> simp [offerB] at ho'
    · exact absurd ⟨rfl, hFt⟩ hnr
    · exact ⟨rfl, fun Q' => no_group Q' All re T.F1⟩

/-- (iii) And K's grant from f1 is ended with it. -/
theorem new_grant_falls : ∀ n,
    ¬ F4.standsG parent signer isWd offer isAcc holder shared
      (F5.conf5 signer holder isRoot mayConfer voiceO memberO needO) All All (cutNew All) n T.M := by
  apply F5.self_grant_falls parent signer isWd offer isAcc holder shared isRoot mayConfer
    voiceO memberO needO isF All All (cutNew All) Key.f1 new_removed_cannot_reseat T.M
  · intro o _ ho
    have ho' : offerB o T.M = true := ho
    cases o <;> simp [offerB] at ho'
    exact ⟨rfl, fun h => absurd h.1 (by decide), fun Q' => no_group Q' All ds T.M⟩
  · exact fun _ hm => hm

/-- (iii), the other side: before the removal the grant is live, one link above f1's seat. -/
theorem new_grant_live_before :
    F4.standsG parent signer isWd offer isAcc holder shared
      (F5.conf5 signer holder isRoot mayConfer voiceO memberO needO) Pre Pre (cutNew Pre) 1 T.M := by
  have hf1 : F4.standsG parent signer isWd offer isAcc holder shared
      (F5.conf5 signer holder isRoot mayConfer voiceO memberO needO) Pre Pre (cutNew Pre) 0 T.F1 := by
    refine ⟨g, g, by decide, rfl, Or.inl ⟨rfl, rfl⟩, by decide, Or.inr rfl, rfl,
      fun ⟨_, _, hwd, _⟩ => hwd, fun ⟨_, hw, _⟩ => hw.1, fun ⟨c, hc, hcs, _⟩ => ?_⟩
    have hcs' : cutsSeatB c T.F1 = true := hcs
    cases c <;> simp [cutsSeatB] at hcs'
    exact F5.counts_concluded parent isCut none2 none2 entNew Pre xf hc rfl
  refine ⟨ds, aks, by decide, rfl, Or.inr (Or.inl ⟨T.F1, hf1, rfl, rfl⟩), by decide,
    Or.inl ⟨Or.inr (Or.inr rfl), rfl⟩, rfl,
    fun ⟨_, _, hwd, _⟩ => hwd, fun ⟨_, hw, _⟩ => hw.1, fun ⟨c, _, hcs, _⟩ => ?_⟩
  have hcs' : cutsSeatB c T.M = true := hcs
  cases c <;> simp [cutsSeatB] at hcs'

end Founders

/-! ### F5 (iv), the witness of the price (attacks.py test 17)

  `g`: f1 and f2 found the group (`a2`: f2's acceptance). `w1`: f1 resigns. `w2`: f2 resigns.
  Neither names the other. `re`: f1 then signs itself an offer of the founder's seat. -/

namespace Two

inductive R | g | a2 | w1 | w2 | re
  deriving DecidableEq, Repr

inductive Key | f1 | f2
  deriving DecidableEq, Repr

inductive T | F1 | F2
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | g, a2 => true | g, w1 => true | g, w2 => true | w1, re => true | w2, re => true
  | _, _ => false
def parent (a b : R) : Prop := parentB a b = true

def signer : R → Key | g => Key.f1 | a2 => Key.f2 | w1 => Key.f1 | w2 => Key.f2 | re => Key.f1
def holder : T → Key | T.F1 => Key.f1 | T.F2 => Key.f2

def isWd (r : R) : Prop := r = w1 ∨ r = w2
def isAcc (r : R) : Prop := r = a2
def offerB : R → T → Bool | g, _ => true | re, T.F1 => true | _, _ => false
def offer (o : R) (t : T) : Prop := offerB o t = true
def shared (o : R) : Prop := o = g
def isF (_ : T) : Prop := True
def isRoot (o : R) (_ : T) : Prop := o = g
def mayConfer (_ _ : T) : Prop := True
def voiceO (_ _ : R) : Prop := False
def memberO (_ : T) (_ : R) : Prop := True
def needO (_ : T) : Nat := 1
def noCut (_ : R) (_ : T) : Prop := False

def All (_ : R) : Prop := True
def OnlyW1 (r : R) : Prop := r = g ∨ r = a2 ∨ r = w1
def OnlyW2 (r : R) : Prop := r = g ∨ r = a2 ∨ r = w2

/-- Each resignation alone leaves a founder: after `w1`, f2; after `w2`, f1. -/
theorem each_alone_leaves_one :
    F4.standsG parent signer isWd offer isAcc holder shared
        (F5.conf5 signer holder isRoot mayConfer voiceO memberO needO) OnlyW1 OnlyW1 noCut 0 T.F2 ∧
      F4.standsG parent signer isWd offer isAcc holder shared
        (F5.conf5 signer holder isRoot mayConfer voiceO memberO needO) OnlyW2 OnlyW2 noCut 0 T.F1 := by
  constructor
  · refine ⟨g, a2, by simp [OnlyW1], rfl, Or.inl rfl, by simp [OnlyW1], Or.inl ⟨rfl, rfl⟩, rfl,
      ?_, ?_, fun h => h⟩
    · intro ⟨v, hS, hwd, _, hs⟩
      cases hs with
      | inl hs => cases v <;> simp [OnlyW1] at hS <;> simp [isWd] at hwd <;> simp [signer, holder] at hs
      | inr hs => exact hs.2 rfl
    · intro ⟨v, hw, hS⟩
      have hp : parentB a2 v = true := hw.2.1
      cases v <;> simp [parentB] at hp
  · refine ⟨g, g, by simp [OnlyW2], rfl, Or.inl rfl, by simp [OnlyW2], Or.inr rfl, rfl,
      ?_, ?_, fun h => h⟩
    · intro ⟨v, hS, hwd, _, hs⟩
      cases hs with
      | inl hs => cases v <;> simp [OnlyW2] at hS <;> simp [isWd] at hwd <;> simp [signer, holder] at hs
      | inr hs => exact hs.2 rfl
    · intro ⟨v, hw, hS⟩
      have hwd : isWd v := hw.1
      have hs : signer v = signer g := hw.2.2
      cases v <;> simp [OnlyW2] at hS <;> simp [isWd] at hwd <;> simp [signer] at hs

/-- Both held: no founder, at any depth, with f1's own offer `re` held. -/
theorem both_resign_none_for_ever : ∀ n t, isF t →
    ¬ F4.standsG parent signer isWd offer isAcc holder shared
      (F5.conf5 signer holder isRoot mayConfer voiceO memberO needO) All All noCut n t := by
  apply F5.emptied_founders_stay_empty parent signer isWd offer isAcc holder shared isRoot
    mayConfer voiceO memberO needO isF All All noCut
  · intro t o a _ h
    have e : o = g := h.2.2.1
    subst e
    cases t
    · exact h.2.2.2.2.2.2.1 ⟨w1, trivial, Or.inl rfl, rfl, Or.inl rfl⟩
    · exact h.2.2.2.2.2.2.1 ⟨w2, trivial, Or.inr rfl, rfl, Or.inl rfl⟩
  · exact fun _ _ _ _ => trivial
  · exact fun _ _ _ _ _ _ => trivial
  · exact fun _ _ => Nat.le_refl 1

/-- WITHOUT the rule (a founding signer is the object's own key for good), `re` restores f1. -/
theorem old_rule_restores (Q0 : T → Prop) :
    F4.seatByG parent signer isWd offer isAcc holder shared All All
      (F5.confOwn signer (fun _ _ => True) Q0 All) noCut T.F1 re re := by
  refine ⟨trivial, rfl, trivial, trivial, Or.inr rfl, rfl, ?_, ?_, fun h => h⟩
  · intro ⟨v, _, _, hp, _⟩
    have hp' : parentB re v = true := hp
    cases v <;> simp [parentB] at hp'
  · intro ⟨v, hw, _⟩
    have hp' : parentB re v = true := hw.2.1
    cases v <;> simp [parentB] at hp'

end Two

/-! ## F6. The audience is a least fixed point, and only a key inside it widens it

  `own r k`: `k` is in the audience the row `r` has from its own ancestors (the members at
  its head, its signers, the keys it names). The rule: a row `d` that names `r` adds its
  audience to `r`'s only if `d` is concluded and `d`'s signer is already in `r`'s audience. -/

namespace F6

section Rule

variable {Row Key : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (own : Row → Key → Prop)

/-- THE RULE: the audience, as the least relation closed under the two clauses. `A` is the
    concluded set. -/
inductive Aud (A : Row → Prop) : Row → Key → Prop
  | base {r : Row} {k : Key} : own r k → Aud A r k
  | carry {r d : Row} {k : Key} : parent r d → A d → Aud A r (signer d) → Aud A d k → Aud A r k

/-- BEFORE the rule (KERNEL.md 5 as first written): a row's audience includes the audience
    of every row that names it. -/
inductive Aud0 : Row → Key → Prop
  | base {r : Row} {k : Key} : own r k → Aud0 r k
  | carry {r d : Row} {k : Key} : parent r d → Aud0 d k → Aud0 r k

/-- It is the least: any relation closed under the two clauses contains it. -/
theorem Aud_least (A : Row → Prop) (P : Row → Key → Prop) (hb : ∀ r k, own r k → P r k)
    (hc : ∀ r d k, parent r d → A d → P r (signer d) → P d k → P r k) :
    ∀ r k, Aud parent signer own A r k → P r k := by
  intro r k h
  induction h with
  | base h => exact hb _ _ h
  | carry hp hA _ _ ih1 ih2 => exact hc _ _ _ hp hA ih1 ih2

/-- It is a fixed point. -/
theorem Aud_fix (A : Row → Prop) (r : Row) (k : Key) :
    Aud parent signer own A r k ↔
      (own r k ∨ ∃ d, parent r d ∧ A d ∧ Aud parent signer own A r (signer d) ∧
        Aud parent signer own A d k) := by
  constructor
  · intro h
    cases h with
    | base h => exact Or.inl h
    | carry hp hA h1 h2 => exact Or.inr ⟨_, hp, hA, h1, h2⟩
  · intro h
    cases h with
    | inl h => exact Aud.base h
    | inr h =>
      obtain ⟨d, hp, hA, h1, h2⟩ := h
      exact Aud.carry hp hA h1 h2

theorem Aud_function (C : (Row → Prop) → Row → Prop) (S S' : Row → Prop) (h : ∀ r, S r ↔ S' r) :
    Aud parent signer own (C S) = Aud parent signer own (C S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

/-- It only grows with the concluded set. -/
theorem Aud_mono (A A' : Row → Prop) (hA : ∀ d, A d → A' d) :
    ∀ r k, Aud parent signer own A r k → Aud parent signer own A' r k :=
  Aud_least parent signer own A _ (fun _ _ h => Aud.base h)
    (fun _ _ _ hp ha h1 h2 => Aud.carry hp (hA _ ha) h1 h2)

/-- The rule only narrows: whoever is in the audience now was in it before the rule. -/
theorem Aud_sub_Aud0 (A : Row → Prop) :
    ∀ r k, Aud parent signer own A r k → Aud0 parent own r k :=
  Aud_least parent signer own A _ (fun _ _ h => Aud0.base h)
    (fun _ _ _ hp _ _ h2 => Aud0.carry hp h2)

/-- THE RULE'S THEOREM. Let `A'` be `A` with any number of further concluded rows, all signed
    by one key `k`. Then every key in a row's audience at `A'` was in it at `A`, or `k` was.
    The rows a key signs widen only the audiences that key is already in. -/
theorem rows_of_one_key (A A' : Row → Prop) (k : Key)
    (hnew : ∀ d, A' d → A d ∨ signer d = k) :
    ∀ r k', Aud parent signer own A' r k' →
      Aud parent signer own A r k' ∨ Aud parent signer own A r k := by
  apply Aud_least parent signer own A'
  · exact fun _ _ h => Or.inl (Aud.base h)
  · intro r d k' hp hA' ih1 ih2
    cases ih1 with
    | inr h => exact Or.inr h
    | inl h1 =>
      cases hnew d hA' with
      | inl hA =>
        exact ih2.elim (fun h2 => Or.inl (Aud.carry hp hA h1 h2))
          (fun h2 => Or.inr (Aud.carry hp hA h1 h2))
      | inr e => exact Or.inr (e ▸ h1)

/-- (i) NO SELF-SERVICE. A key enters no audience by any rows it signs itself: if `k` is in
    a row's audience after rows by `k` are added, it was in it before. -/
theorem no_self_service (A A' : Row → Prop) (k : Key)
    (hnew : ∀ d, A' d → A d ∨ signer d = k) (r : Row)
    (h : Aud parent signer own A' r k) : Aud parent signer own A r k :=
  (rows_of_one_key parent signer own A A' k hnew r k h).elim id id

/-- (iii), necessity: WHO CAN WIDEN. If rows signed by `k` bring a key into a row's audience,
    `k` was already in that audience. -/
theorem widen_needs_member (A A' : Row → Prop) (k : Key)
    (hnew : ∀ d, A' d → A d ∨ signer d = k) (r : Row) (k' : Key)
    (h : Aud parent signer own A' r k') (hn : ¬ Aud parent signer own A r k') :
    Aud parent signer own A r k :=
  (rows_of_one_key parent signer own A A' k hnew r k' h).elim (fun x => absurd x hn) id

/-- (iii), sufficiency: CARRIAGE. A key in a row's audience widens it by one concluded row
    that names it: everyone in the new row's own audience enters. -/
theorem member_can_widen (A A' : Row → Prop) (hA : ∀ d, A d → A' d) (r x : Row) (k' : Key)
    (hx : A' x) (hp : parent r x) (hin : Aud parent signer own A r (signer x))
    (hown : own x k') : Aud parent signer own A' r k' :=
  Aud.carry hp hx (Aud_mono parent signer own A A' hA r _ hin) (Aud.base hown)

/-- (i) and (ii), at one set. A row whose own audience lacks `k`, and which no concluded row
    names except rows `k` signed, does not have `k` in its audience. For a removed member
    and a row written after its removal: the row's own audience (the members at its head)
    lacks it, and until a key inside carries it, nothing the removed member signs matters. -/
theorem only_own_rows_name_it (A : Row → Prop) (k : Key) (r : Row) (hown : ¬ own r k)
    (hnamers : ∀ d, parent r d → A d → signer d = k) : ¬ Aud parent signer own A r k := by
  intro h
  have h0 := no_self_service parent signer own (fun d => A d ∧ signer d ≠ k) A k
    (fun d hd => (Classical.em (signer d = k)).elim Or.inr (fun hne => Or.inl ⟨hd, hne⟩)) r h
  cases (Aud_fix parent signer own _ r k).1 h0 with
  | inl h => exact hown h
  | inr h =>
    obtain ⟨d, hp, hA, _, _⟩ := h
    exact hA.2 (hnamers d hp hA.1)

end Rule

end F6

/-! ### F6, the witness (attacks.py test 28)

  `m1`: B's message, before C joined (its own audience is A and B). `rp`: A's reply to it,
  after C joined. `z`: outsider X signs a row naming `m1`. `m5`: B's message after C was
  removed. `zc`: the removed C signs a row naming `m5`. -/

namespace AudRows

inductive R | m1 | rp | z | m5 | zc
  deriving DecidableEq, Repr

inductive Key | A | B | C | X
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool | m1, rp => true | m1, z => true | m5, zc => true | _, _ => false
def parent (a b : R) : Prop := parentB a b = true

def signer : R → Key | m1 => Key.B | rp => Key.A | z => Key.X | m5 => Key.B | zc => Key.C

def ownB : R → Key → Bool
  | m1, Key.A => true | m1, Key.B => true
  | rp, Key.A => true | rp, Key.B => true | rp, Key.C => true
  | z, Key.X => true
  | m5, Key.A => true | m5, Key.B => true
  | zc, Key.A => true | zc, Key.B => true | zc, Key.C => true
  | _, _ => false
def own (r : R) (k : Key) : Prop := ownB r k = true

def All (_ : R) : Prop := True

/-- The audience the rule gives, written out. -/
def audB : R → Key → Bool
  | m1, Key.A => true | m1, Key.B => true | m1, Key.C => true
  | rp, Key.A => true | rp, Key.B => true | rp, Key.C => true
  | z, Key.X => true
  | m5, Key.A => true | m5, Key.B => true
  | zc, Key.A => true | zc, Key.B => true | zc, Key.C => true
  | _, _ => false

theorem aud_table : ∀ r k, F6.Aud parent signer own All r k → audB r k = true := by
  apply F6.Aud_least parent signer own All
  · intro r k; cases r <;> cases k <;> simp [own, ownB, audB]
  · intro r d k; cases r <;> cases d <;> cases k <;> simp [parent, parentB, signer, audB]

/-- WITHOUT the rule. The outsider is in the audience of the message it named, and the
    removed member in the audience of a message written after its removal. -/
theorem without_rule_naming_admits :
    F6.Aud0 parent own m1 Key.X ∧ F6.Aud0 parent own m5 Key.C :=
  ⟨F6.Aud0.carry (d := z) rfl (F6.Aud0.base rfl), F6.Aud0.carry (d := zc) rfl (F6.Aud0.base rfl)⟩

/-- WITH the rule. Neither is. -/
theorem with_rule_naming_admits_no_one :
    ¬ F6.Aud parent signer own All m1 Key.X ∧ ¬ F6.Aud parent signer own All m5 Key.C :=
  ⟨fun h => absurd (aud_table _ _ h) (by decide), fun h => absurd (aud_table _ _ h) (by decide)⟩

/-- WITH the rule, carriage stands: A's reply carries the earlier message to the joiner. -/
theorem with_rule_reply_carries : F6.Aud parent signer own All m1 Key.C :=
  F6.Aud.carry (d := rp) rfl trivial (F6.Aud.base rfl) (F6.Aud.base rfl)

end AudRows

/-! ## F7. The holders of a counted scope are the keys common to the tips

  `act`: the counted acts on an object that count, with its founding row. Their tips
  (`Kernel.tips`, Window.lean, with "names" read as "is in the past of") are the acts no other
  act has in its past. `seenBy v t`: seat `t` is live by the rows in the past of `v`, with
  `v`. `full t`: `t` is live by all the rows held. Before the rule the holders were `full`.
  The rule: while two tips wait, a key holds the scope only if every tip seats it. -/

namespace F7

section Rule

variable {Row T : Type}
variable (parent : Row → Row → Prop)
variable (act : Row → Prop) (seenBy : Row → T → Prop) (full : T → Prop)

/-- Two tips wait. -/
def waiting : Prop :=
  ∃ u v, tips (TransGen parent) act u ∧ tips (TransGen parent) act v ∧ u ≠ v

/-- THE RULE. -/
def holds (t : T) : Prop :=
  full t ∧ (waiting parent act → rosterOf (TransGen parent) seenBy act t)

theorem holds_function (actOf : (Row → Prop) → Row → Prop) (seenOf : (Row → Prop) → Row → T → Prop)
    (fullOf : (Row → Prop) → T → Prop) (S S' : Row → Prop) (h : ∀ r, S r ↔ S' r) :
    holds parent (actOf S) (seenOf S) (fullOf S) = holds parent (actOf S') (seenOf S') (fullOf S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

/-- While tips wait, to hold is to be seated by all the rows and by every tip. -/
theorem waiting_iff (hw : waiting parent act) (t : T) :
    holds parent act seenBy full t ↔
      (full t ∧ ∀ v, tips (TransGen parent) act v → seenBy v t) :=
  ⟨fun h => ⟨h.1, h.2 hw⟩, fun h => ⟨h.1, fun _ => h.2⟩⟩

/-- With one tip, or none, the holders are as before the rule. -/
theorem one_tip_iff (hw : ¬ waiting parent act) (t : T) :
    holds parent act seenBy full t ↔ full t :=
  ⟨fun h => h.1, fun h => ⟨h, fun x => absurd x hw⟩⟩

/-- A seat one waiting tip does not give is not held. -/
theorem not_seen_by_a_tip (hw : waiting parent act) (v : Row)
    (hv : tips (TransGen parent) act v) (t : T) (hn : ¬ seenBy v t) :
    ¬ holds parent act seenBy full t :=
  fun h => hn (h.2 hw v hv)

/-- A counted act naming every tip, which nothing names, ends the wait: it is the one tip
    (`Kernel.merge_one_tip`), and the holders are again those all the rows seat. -/
theorem merge_ends_wait (m : Row)
    (hall : ∀ v, tips (TransGen parent) act v → TransGen parent v m)
    (hfresh : ∀ u, (act u ∨ u = m) → ¬ TransGen parent m u) (t : T) :
    holds parent (fun q => act q ∨ q = m) seenBy full t ↔ full t := by
  apply one_tip_iff
  intro ⟨u, v, hu, hv, hne⟩
  have h := merge_one_tip (TransGen parent) act m hall hfresh
  exact hne (((h u).1 hu).trans ((h v).1 hv).symm)

end Rule

section Seats

variable {Row Key T : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (isWd : Row → Prop)
variable (offer : Row → T → Prop) (isAcc : Row → Prop) (holder : T → Key)
variable (conf : (T → Prop) → (Row → Prop) → Row → T → Prop)

/-- A seat that stands, at any depth, has a concluded offer. -/
theorem stands_needs_offer (P W : Row → Prop) (cut : Row → T → Prop) (n : Nat) (t : T)
    (h : stands parent signer isWd offer isAcc holder conf P W cut n t) :
    ∃ o, P o ∧ offer o t := by
  cases n with
  | zero =>
    have ⟨o, h1, h2, _⟩ := seat_needs_offer parent signer isWd offer isAcc holder P W _ cut t h
    exact ⟨o, h1, h2⟩
  | succ n =>
    have ⟨o, h1, h2, _⟩ := seat_needs_offer parent signer isWd offer isAcc holder P W _ cut t h
    exact ⟨o, h1, h2⟩

/-- The rows a tip sees: itself and its past, among the concluded rows. -/
def view (A : Row → Prop) (v r : Row) : Prop := A r ∧ (r = v ∨ TransGen parent r v)

variable (act : Row → Prop) (full : T → Prop)

/-- THE RULE'S THEOREM: A BACKDATED CONFERRAL SEATS NO ONE WHILE TIPS WAIT. The seat a tip
    gives is the walk of Seat.lean over the rows that tip sees, under whatever cut relation
    `cutAt v` that view has. Let two tips wait, and let `v` be one of them. A seat `t` no
    offer of which is `v` or in the past of `v` is not held: an admission signed beside a
    counted act (with whatever old voices met the count at the old head) seats nobody until
    a counted act names both. -/
theorem backdated_conferral_seats_no_one (A : Row → Prop) (cutAt : Row → Row → T → Prop)
    (n : Nat) (hw : waiting parent act) (v : Row) (hv : tips (TransGen parent) act v) (t : T)
    (hno : ∀ o, A o → offer o t → ¬ (o = v ∨ TransGen parent o v)) :
    ¬ holds parent act
      (fun v t => stands parent signer isWd offer isAcc holder conf (view parent A v)
        (view parent A v) (cutAt v) n t) full t := by
  apply not_seen_by_a_tip parent act _ full hw v hv t
  intro h
  have ⟨o, ho, hoff⟩ := stands_needs_offer parent signer isWd offer isAcc holder conf _ _ _ n t h
  exact hno o ho.1 hoff ho.2

end Seats

end F7

/-! ### F7, the witness (attacks.py test 3)

  `g`: A founds the room with B (`aB`). `w`, `aC`: C is admitted and accepts. `x`: A and B
  remove C, counted over head `w`. `wD`, `aD`: A, with removed C's old voice, admits D on
  the same head `w`, and D accepts. Each of `w`, `x`, `wD` is taken as validly counted at the
  head it names (for `wD` that is so: A and C were two of three at `w`). -/

namespace TipRows

inductive R | g | aB | w | aC | x | wD | aD
  deriving DecidableEq, Repr

inductive Key | A | B | C | D
  deriving DecidableEq, Repr

inductive T | mA | mB | mC | mD
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | g, aB => true | g, w => true | aB, w => true | w, aC => true | w, x => true | w, wD => true
  | wD, aD => true
  | _, _ => false
def parent (a b : R) : Prop := parentB a b = true

def ancB : R → R → Bool
  | g, aB => true | g, w => true | g, aC => true | g, x => true | g, wD => true | g, aD => true
  | aB, w => true | aB, aC => true | aB, x => true | aB, wD => true | aB, aD => true
  | w, aC => true | w, x => true | w, wD => true | w, aD => true
  | wD, aD => true
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
  | g => Key.A | aB => Key.B | w => Key.A | aC => Key.C | x => Key.A | wD => Key.A | aD => Key.D
def holder : T → Key | T.mA => Key.A | T.mB => Key.B | T.mC => Key.C | T.mD => Key.D

def isWd (_ : R) : Prop := False
def isAcc (r : R) : Prop := r = aB ∨ r = aC ∨ r = aD
def offerB : R → T → Bool
  | g, T.mA => true | g, T.mB => true | w, T.mC => true | wD, T.mD => true | _, _ => false
def offer (o : R) (t : T) : Prop := offerB o t = true
def cutsSeat (c : R) (t : T) : Prop := c = x ∧ t = T.mC

/-- The counted acts, with the founding row. -/
def actB : R → Bool | g => true | w => true | x => true | wD => true | _ => false
def act (r : R) : Prop := actB r = true

def All (_ : R) : Prop := True
/-- Each listed act is taken as validly conferred. -/
def conf (_ : T → Prop) (_ : R → Prop) (_ : R) (_ : T) : Prop := True

/-- The cut a view has: the removal `x`, if the view holds it. -/
def cutAt (v : R) : R → T → Prop :=
  cutOut parent cutsSeat (fun c => c = x ∧ (c = v ∨ TransGen parent c v))

def seenBy (v : R) (t : T) : Prop :=
  stands parent signer isWd offer isAcc holder conf (F7.view parent All v) (F7.view parent All v)
    (cutAt v) 0 t

/-- All the rows held, with the removal counting. -/
def full (t : T) : Prop :=
  stands parent signer isWd offer isAcc holder conf All All
    (cutOut parent cutsSeat (fun c => c = x)) 0 t

theorem tip_x : tips (TransGen parent) act x :=
  ⟨rfl, fun ⟨u, _, h⟩ => by
    have := anc_sound h
    cases u <;> simp [ancB] at this⟩

theorem tip_wD : tips (TransGen parent) act wD :=
  ⟨rfl, fun ⟨u, hu, h⟩ => by
    have := anc_sound h
    have hu' : actB u = true := hu
    cases u <;> simp [ancB] at this <;> simp [actB] at hu'⟩

/-- The removal and the backdated admission are two tips. -/
theorem two_tips_wait : F7.waiting parent act := ⟨x, wD, tip_x, tip_wD, by decide⟩

/-- WITHOUT the rule. All the rows held seat D: the admission was validly counted at its
    head, and D accepted. -/
theorem without_rule_D_seated : full T.mD := by
  refine ⟨wD, aD, trivial, rfl, trivial, trivial, Or.inl ⟨Or.inr (Or.inr rfl), rfl⟩, rfl,
    fun ⟨_, hw, _⟩ => hw.1, fun ⟨_, hw, _⟩ => hw.1, fun ⟨_, _, hcs, _⟩ => ?_⟩
  exact absurd hcs.2 (by decide)

/-- WITH the rule. D holds nothing while the two tips wait: the removal's view has no offer
    to D. -/
theorem with_rule_D_not_listed : ¬ F7.holds parent act seenBy full T.mD := by
  apply F7.backdated_conferral_seats_no_one parent signer isWd offer isAcc holder conf act full
    All cutAt 0 two_tips_wait x tip_x T.mD
  intro o _ ho hin
  have ho' : offerB o T.mD = true := ho
  cases o <;> simp [offerB] at ho'
  exact hin.elim (fun e => absurd e (by decide)) (fun h => absurd (anc_sound h) (by decide))

/-- The removed C is not listed either: all the rows held cut its seat. -/
theorem with_rule_C_not_listed : ¬ F7.holds parent act seenBy full T.mC := by
  intro ⟨⟨o, a, h⟩, _⟩
  have ho : offerB o T.mC = true := h.2.1
  have e : o = w := by cases o <;> simp [offerB] at ho <;> rfl
  subst e
  exact h.2.2.2.2.2.2.2.2 ⟨x, rfl, ⟨rfl, rfl⟩, fun ha => absurd (anc_sound ha) (by decide)⟩

theorem g_x : TransGen parent g x := TransGen.tail (b := w) (TransGen.single rfl) rfl
theorem aB_x : TransGen parent aB x := TransGen.tail (b := w) (TransGen.single rfl) rfl
theorem g_wD : TransGen parent g wD := TransGen.tail (b := w) (TransGen.single rfl) rfl
theorem aB_wD : TransGen parent aB wD := TransGen.tail (b := w) (TransGen.single rfl) rfl

theorem every_tip (v : R) (hv : tips (TransGen parent) act v) : v = x ∨ v = wD := by
  have ha : actB v = true := hv.1
  cases v <;> simp [actB] at ha
  · exact absurd ⟨w, rfl, TransGen.single rfl⟩ hv.2
  · exact absurd ⟨x, rfl, TransGen.single rfl⟩ hv.2
  · exact Or.inl rfl
  · exact Or.inr rfl

/-- The members both tips seat are still listed: B holds its seat. -/
theorem with_rule_B_listed : F7.holds parent act seenBy full T.mB := by
  refine ⟨⟨g, aB, trivial, rfl, trivial, trivial, Or.inl ⟨Or.inl rfl, rfl⟩, rfl,
    fun ⟨_, hw, _⟩ => hw.1, fun ⟨_, hw, _⟩ => hw.1,
    fun ⟨_, _, hcs, _⟩ => absurd hcs.2 (by decide)⟩, fun _ v hv => ?_⟩
  cases every_tip v hv with
  | inl e =>
    subst e
    exact ⟨g, aB, ⟨trivial, Or.inr g_x⟩, rfl, trivial,
      ⟨trivial, Or.inr aB_x⟩, Or.inl ⟨Or.inl rfl, rfl⟩, rfl,
      fun ⟨_, hw, _⟩ => hw.1, fun ⟨_, hw, _⟩ => hw.1,
      fun ⟨_, _, hcs, _⟩ => absurd hcs.2 (by decide)⟩
  | inr e =>
    subst e
    exact ⟨g, aB, ⟨trivial, Or.inr g_wD⟩, rfl, trivial,
      ⟨trivial, Or.inr aB_wD⟩, Or.inl ⟨Or.inl rfl, rfl⟩, rfl,
      fun ⟨_, hw, _⟩ => hw.1, fun ⟨_, hw, _⟩ => hw.1,
      fun ⟨_, _, hcs, _⟩ => absurd hcs.2 (by decide)⟩

end TipRows

/-! ## Axioms used -/

#print axioms F5.cut_needs_two_voices
#print axioms F5.one_key_cuts_nothing
#print axioms F5.counts_of_unopposed
#print axioms F5.no_single_founder_removes
#print axioms F5.two_founders_neither_removes
#print axioms F5.conf5_mono
#print axioms F5.removed_cannot_reseat
#print axioms F5.self_grant_falls
#print axioms F5.under_dead_falls
#print axioms F5.emptied_founders_stay_empty
#print axioms F5.no_row_restores_a_founder
#print axioms Founders.old_one_founder_removes
#print axioms Founders.old_removed_reseats
#print axioms Founders.old_grant_survives
#print axioms Founders.new_u2_void
#print axioms Founders.new_f2_keeps_seat
#print axioms Founders.new_removed_cannot_reseat
#print axioms Founders.new_grant_falls
#print axioms Founders.new_grant_live_before
#print axioms Two.each_alone_leaves_one
#print axioms Two.both_resign_none_for_ever
#print axioms Two.old_rule_restores
#print axioms F6.Aud_least
#print axioms F6.Aud_fix
#print axioms F6.Aud_function
#print axioms F6.Aud_mono
#print axioms F6.Aud_sub_Aud0
#print axioms F6.rows_of_one_key
#print axioms F6.no_self_service
#print axioms F6.widen_needs_member
#print axioms F6.member_can_widen
#print axioms F6.only_own_rows_name_it
#print axioms AudRows.without_rule_naming_admits
#print axioms AudRows.with_rule_naming_admits_no_one
#print axioms AudRows.with_rule_reply_carries
#print axioms F7.holds_function
#print axioms F7.waiting_iff
#print axioms F7.one_tip_iff
#print axioms F7.not_seen_by_a_tip
#print axioms F7.merge_ends_wait
#print axioms F7.stands_needs_offer
#print axioms F7.backdated_conferral_seats_no_one
#print axioms TipRows.two_tips_wait
#print axioms TipRows.without_rule_D_seated
#print axioms TipRows.with_rule_D_not_listed
#print axioms TipRows.with_rule_C_not_listed
#print axioms TipRows.with_rule_B_listed

end Harden

end Kernel
