/-
  RosterHead.lean — the members at the head a counted row names

  Consent.lean counts a body's consent over `member t k`. Which keys are members at the named
  head is the roster's part, and this file gives it.

  THE ROSTER. A lineage of versions over one object. A version names the heads it extends
  (`hd h v`: `h` is a version and `v` names it). A version with no head is a genesis, and the
  voices of its count are a parameter (`base`). A version STANDS when it carries the signatures
  of the count its protocol asks, by distinct members at the heads it names
  (`Consent.bodyConsents`, with `member` instantiated as "a member at every head named"), and
  the holder's yes is on it or in its past: its signature on the row, or an acceptance the
  version names. The MEMBERS AT a version are the keys it lists, when it stands, less any key
  that has withdrawn from the lineage by its own row in the version's past. A leaving binds by
  causal past, as a removal does (KERNEL.md 6): a version with the leaving in its past does not
  count that key, and one without it still does. Recursion is on
  what rows name (`parent`); no rank, sequence number or instant is introduced, and every
  definition reads a version and its past only.

  Proved here.
   (1) `membersAt_function`, `standing_final`: the members at a head are a function of the
       head, the signatures it carries and its past. No row concurrent with it and no later
       row changes them. A removal is a later standing version and changes the members at that
       version, not at the old head.
   (2) `counted_over_named_head`, `rows_outside_change_nothing`: whether a version stands is
       decided by the members at the heads it names and the signatures on it; rows outside its
       past, by any key, change nothing. Concurrent versions are not decided here: they wait
       as tips (Window.lean, Merge.lean).
   (3) `no_self_admission`, `outsiders_admit_nothing`: a key that is not a member at the heads
       a version names gives no voice to its count, whatever it signs.
   (4) `removed_voice_does_not_count`, `readmission_needed`, `old_head_still_counts`: a key a
       version does not list is no voice of a version naming it; further down it is a member
       only if a version counted without it lists it again; it still counts for a version
       naming an older head.
   (5) `voters_is_common`: a version naming several heads is counted over `Merge.common` of the
       members at those heads.
   (6) `one_signature_never_removes`: where the count asks two or more, a standing version
       leaves out a member of the head it names only by the signatures of two distinct
       members, or because that member withdrew by its own row.
   (7) `leaving_binds_by_past`, `left_head`: a member's own leaving is a fact for the rows that
       have it in their past and for no others.

  THE REJECTED RULE. `Rejected` keeps the rule under which a body's voices were separate rows
  each of which its signer could withdraw (`Consent.Rejected.standsCountedW`), with two models
  of what it allowed: a later withdrawal, outside a head's past, removes every member at the
  head (`Rejected.Model.later_withdrawal_changes_members`), and a withdrawal at the head ends a
  version none of whose own rows is withdrawn (`Rejected.Model.head_withdrawal_ends_version`).
  The text has one signature never remove (CC 3.1.3.2).

  THE SECOND REJECTED RULE. `Retro` keeps the reading of the members at a head through every
  held withdrawal, as `Seat.withdrawn` reads it for whether a seat is live. It agrees with the
  rule taken where every held leaving is in the version's past (`Retro.retro_agrees`), and a
  leaving held after a head changes the members there under it (`Retro.Model.retro_reaches_back`).

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Consent.lean and
  Merge.lean.
-/

import Consent
import Merge

namespace Kernel

namespace RosterHead

open Relation Causal

/-- The data of a lineage. `parent p r`: row `r` names row `p`; well-founded. `isVer`: a
    version of this roster. `isAcc`: an acceptance row. `cosigns v k`: `k`'s signature is
    carried on row `v`. `states v k`: version `v` lists `k`. `base v k`: `k` is a voice of the
    count of `v` when `v` names no head. `need v`: the count `v`'s protocol asks. `holder v`:
    the key whose yes `v` needs (a joiner; for a removal, its proposer). -/
structure Lineage (Row Key : Type) where
  parent : Row → Row → Prop
  wf : WellFounded parent
  signer : Row → Key
  isWd : Row → Prop
  isVer : Row → Prop
  isAcc : Row → Prop
  cosigns : Row → Key → Prop
  states : Row → Key → Prop
  base : Row → Key → Prop
  need : Row → Nat
  holder : Row → Key

variable {Row Key : Type} (L : Lineage Row Key)

/-- `v` names the version `h` as a head. -/
def hd (h v : Row) : Prop := L.isVer h ∧ L.parent h v

/-- `u` is `v` or in its past. -/
def pastOrSelf (u v : Row) : Prop := u = v ∨ TransGen L.parent u v

/-- `k` has withdrawn from the lineage by its own row in `v`'s past: a withdrawal signed by `k`
    naming a version. Only `k` signs it. -/
def left (P : Row → Prop) (v : Row) (k : Key) : Prop :=
  ∃ w, pastOrSelf L w v ∧ P w ∧ L.isWd w ∧ L.signer w = k ∧ ∃ u, L.isVer u ∧ L.parent u w

/-- The holder's yes, on the version or in its past. -/
def holderYes (P : Row → Prop) (v : Row) : Prop :=
  L.cosigns v (L.holder v) ∨ ∃ a, L.parent a v ∧ L.isAcc a ∧ P a ∧ L.signer a = L.holder v

/-- The voices over which `v` is counted, given the members `M` at each version. -/
def votersOf (M : Row → Key → Prop) (v : Row) (k : Key) : Prop :=
  ((∃ h, hd L h v) ∧ ∀ h, hd L h v → M h k) ∨ ((¬ ∃ h, hd L h v) ∧ L.base v k)

/-- Version `v` stands over the voices `M`: a version, carrying the count by distinct members
    (`Consent.bodyConsents`), with the holder's yes. -/
def stV (M : Key → Prop) (P : Row → Prop) (v : Row) : Prop :=
  L.isVer v ∧ Consent.bodyConsents (fun _ k => M k) L.need L.cosigns P v v ∧ holderYes L P v

/-- The members at each version, by recursion on what rows name. -/
noncomputable def mem (P : Row → Prop) : Row → Key → Prop :=
  L.wf.fix (C := fun _ => Key → Prop) (fun v ih k =>
    stV L (fun k' => (((∃ h, hd L h v) ∧ ∀ h (hh : hd L h v), ih h hh.2 k') ∨
      ((¬ ∃ h, hd L h v) ∧ L.base v k')) ∧ ¬ left L P v k') P v ∧ L.states v k ∧
      ¬ left L P v k)

/-- The voices of `v`'s count: members at every head it names that have not withdrawn from
    the lineage in `v`'s own past. A leaving binds by causal past, as a removal does
    (`Causal.only_removals_stop_counting`): a version with it in its past does not count the
    key; one without it does. -/
def voters (P : Row → Prop) (v : Row) (k : Key) : Prop :=
  votersOf L (mem L P) v k ∧ ¬ left L P v k

/-- Version `v` stands. -/
def standsV (P : Row → Prop) (v : Row) : Prop := stV L (voters L P v) P v

/-- The defining equation (by definition). -/
theorem mem_iff (P : Row → Prop) (v : Row) (k : Key) :
    mem L P v k ↔ standsV L P v ∧ L.states v k ∧ ¬ left L P v k := by
  unfold mem
  rw [WellFounded.fix_eq]
  exact Iff.rfl

/-! ### A function of the head and its past -/

theorem pastOrSelf_head {h v u : Row} (hp : L.parent h v) (hu : pastOrSelf L u h) :
    pastOrSelf L u v :=
  Or.inr (hu.elim (fun e => e ▸ TransGen.single hp) (fun t => TransGen.tail t hp))

theorem left_congr (P P' : Row → Prop) (v : Row) (k : Key)
    (hP : ∀ r, pastOrSelf L r v → (P r ↔ P' r)) : left L P v k → left L P' v k :=
  fun ⟨w, hw, h1, h2⟩ => ⟨w, hw, (hP w hw).1 h1, h2⟩

theorem stV_congr (M M' : Key → Prop) (P P' : Row → Prop) (v : Row)
    (hM : ∀ k, M k → M' k) (hP : ∀ r, pastOrSelf L r v → (P r ↔ P' r)) :
    stV L M P v → stV L M' P' v := by
  intro ⟨hv, ⟨h0, l, hnd, hn, hl⟩, hy⟩
  refine ⟨hv, ⟨(hP v (Or.inl rfl)).1 h0, l, hnd, hn, fun k hk => ⟨hM k (hl k hk).1, (hl k hk).2⟩⟩,
    hy.elim Or.inl (fun ⟨a, a1, a2, a3, a4⟩ => Or.inr ⟨a, a1, a2, ?_, a4⟩)⟩
  exact (hP a (Or.inr (TransGen.single a1))).1 a3

theorem votersOf_mono (M M' : Row → Key → Prop) (v : Row) (k : Key)
    (h : ∀ h, hd L h v → M h k → M' h k) : votersOf L M v k → votersOf L M' v k :=
  fun hv => hv.elim (fun ⟨e, a⟩ => Or.inl ⟨e, fun h' hh => h h' hh (a h' hh)⟩) Or.inr

theorem mem_congr (P P' : Row → Prop) :
    ∀ v, (∀ r, pastOrSelf L r v → (P r ↔ P' r)) → ∀ k, mem L P v k → mem L P' v k := by
  intro v
  induction v using WellFounded.induction L.wf with | _ v ih => ?_
  intro hP k hk
  have ⟨hs, hst, hl⟩ := (mem_iff L P v k).1 hk
  refine (mem_iff L P' v k).2 ⟨?_, hst, fun h => hl (left_congr L P' P v k
    (fun r hr => (hP r hr).symm) h)⟩
  refine stV_congr L _ _ P P' v (fun k' hk' => ⟨?_, fun h => hk'.2 (left_congr L P' P v k'
    (fun r hr => (hP r hr).symm) h)⟩) hP hs
  exact votersOf_mono L _ _ v k' (fun h hh => ih h hh.2
    (fun r hr => hP r (pastOrSelf_head L hh.2 hr)) k') hk'.1

/-- (1) THE MEMBERS AT A HEAD. Two sets of rows that agree on the head and its past give it the
    same members. No row concurrent with it and no later row, by any key, changes them. -/
theorem membersAt_function (P P' : Row → Prop) (v : Row)
    (hP : ∀ r, pastOrSelf L r v → (P r ↔ P' r)) (k : Key) :
    mem L P v k ↔ mem L P' v k :=
  ⟨mem_congr L P P' v hP k, mem_congr L P' P v (fun r hr => (hP r hr).symm) k⟩

/-- (2) COUNTED OVER THE NAMED HEAD. Whether a version stands is the same over any two sets of
    rows that agree on it and its past. -/
theorem counted_over_named_head (P P' : Row → Prop) (v : Row)
    (hP : ∀ r, pastOrSelf L r v → (P r ↔ P' r)) :
    standsV L P v ↔ standsV L P' v := by
  have hv : ∀ k, voters L P v k ↔ voters L P' v k := fun k =>
    ⟨fun x => ⟨votersOf_mono L _ _ v k (fun h hh => mem_congr L P P' h
        (fun r hr => hP r (pastOrSelf_head L hh.2 hr)) k) x.1,
       fun h => x.2 (left_congr L P' P v k (fun r hr => (hP r hr).symm) h)⟩,
     fun x => ⟨votersOf_mono L _ _ v k (fun h hh => mem_congr L P' P h
        (fun r hr => (hP r (pastOrSelf_head L hh.2 hr)).symm) k) x.1,
       fun h => x.2 (left_congr L P P' v k hP h)⟩⟩
  exact ⟨stV_congr L _ _ P P' v (fun k => (hv k).1) hP,
    stV_congr L _ _ P' P v (fun k => (hv k).2) (fun r hr => (hP r hr).symm)⟩

/-- (2) Rows added outside a version's past, by any keys and of any kind, withdrawals
    included, change nothing in whether it stands or in its members. -/
theorem rows_outside_change_nothing (P X : Row → Prop) (v : Row)
    (hX : ∀ r, X r → ¬ pastOrSelf L r v) :
    (standsV L P v ↔ standsV L (fun r => P r ∨ X r) v) ∧
      ∀ k, mem L P v k ↔ mem L (fun r => P r ∨ X r) v k :=
  have hP : ∀ r, pastOrSelf L r v → (P r ↔ P r ∨ X r) :=
    fun r hr => ⟨Or.inl, fun h => h.elim id (fun x => absurd hr (hX r x))⟩
  ⟨counted_over_named_head L _ _ v hP, membersAt_function L _ _ v hP⟩

/-- (1) FINAL. Where the held rows have no holes (`Causal.kept_ancestors`) and include `v`,
    holding more rows changes neither whether `v` stands nor its members. -/
theorem standing_final (P P' : Row → Prop) (v : Row)
    (hcl : ∀ p r, L.parent p r → P r → P p) (hPP : ∀ r, P r → P' r) (hv : P v) :
    (standsV L P v ↔ standsV L P' v) ∧ ∀ k, mem L P v k ↔ mem L P' v k := by
  have past : ∀ r, pastOrSelf L r v → P r := by
    intro r hr
    cases hr with
    | inl e => exact e ▸ hv
    | inr t =>
      induction t with
      | single hp => exact hcl _ _ hp hv
      | tail _ hp ih => exact ih (hcl _ _ hp hv)
  have hP : ∀ r, pastOrSelf L r v → (P r ↔ P' r) :=
    fun r hr => ⟨hPP r, fun _ => past r hr⟩
  exact ⟨counted_over_named_head L P P' v hP, membersAt_function L P P' v hP⟩

/-! ### No self-admission -/

/-- (3) NO SELF-ADMISSION. A key that is not a member at the heads `v` names gives no voice to
    `v`'s count: drop its signature and the count is the same. It is the roster's form of
    `Consent.nonmember_rows_change_nothing`, with the members read at the named heads. -/
theorem no_self_admission (P : Row → Prop) (v : Row) (k : Key) (hk : ¬ voters L P v k) :
    Consent.bodyConsents (fun t k => voters L P t k) L.need L.cosigns P v v ↔
      Consent.bodyConsents (fun t k => voters L P t k) L.need
        (fun r k' => L.cosigns r k' ∧ k' ≠ k) P v v := by
  constructor
  · intro ⟨h0, l, hnd, hn, hl⟩
    exact ⟨h0, l, hnd, hn, fun k' hk' =>
      ⟨(hl k' hk').1, (hl k' hk').2, fun e => hk (e ▸ (hl k' hk').1)⟩⟩
  · intro ⟨h0, l, hnd, hn, hl⟩
    exact ⟨h0, l, hnd, hn, fun k' hk' => ⟨(hl k' hk').1, (hl k' hk').2.1⟩⟩

/-- (3) Where no member at the named heads signed the version, it does not stand, whatever
    any number of other keys sign. -/
theorem outsiders_admit_nothing (P : Row → Prop) (v : Row) (hn : 1 ≤ L.need v)
    (ho : ∀ k, L.cosigns v k → ¬ voters L P v k) : ¬ standsV L P v := by
  intro ⟨_, ⟨_, l, _, hlen, hl⟩, _⟩
  match l, hlen, hl with
  | [], hlen, _ => exact absurd (Nat.le_trans hn hlen) (Nat.not_succ_le_zero 0)
  | a :: _, _, hl =>
    have ⟨a1, a2⟩ := hl a (List.mem_cons_self _ _)
    exact ho a a2 a1

/-! ### A removed voice -/

/-- A version that does not list `k` has no member `k` (by definition). -/
theorem not_stated_not_member (P : Row → Prop) (u : Row) (k : Key) (hu : ¬ L.states u k) :
    ¬ mem L P u k :=
  fun h => hu ((mem_iff L P u k).1 h).2.1

/-- A version naming a head at which `k` is not a member does not count `k` (by definition). -/
theorem not_member_at_head (P : Row → Prop) (h w : Row) (k : Key) (hh : hd L h w)
    (hm : ¬ mem L P h k) : ¬ voters L P w k :=
  fun hv => hv.1.elim (fun x => hm (x.2 h hh)) (fun x => x.1 ⟨h, hh⟩)

/-- (4) REMOVED VOICE DOES NOT COUNT. A key that a version `u` does not list is not a voice of
    any version naming `u` as a head: by (3) its signatures give that version nothing. -/
theorem removed_voice_does_not_count (P : Row → Prop) (u v : Row) (k : Key)
    (hu : ¬ L.states u k) (hv : hd L u v) : ¬ voters L P v k :=
  not_member_at_head L P u v k hv (not_stated_not_member L P u k hu)

/-- (4) READMISSION NEEDED. Down a line of heads from `u`, a key `u` does not list is not a
    member at `d` unless some version `w` on the way, naming a head `h` at which `k` is not a
    member, stands and lists `k`. Such a `w` does not count `k` (`not_member_at_head`). -/
theorem readmission_needed (P : Row → Prop) (u d : Row) (k : Key)
    (hu : ¬ L.states u k) (hl : TransGen (hd L) u d)
    (hno : ∀ w h, TransGen (hd L) u w → (w = d ∨ TransGen (hd L) w d) → hd L h w →
      ¬ mem L P h k → ¬ (standsV L P w ∧ L.states w k)) :
    ¬ mem L P d k := by
  revert hno
  induction hl with
  | single hh =>
    exact fun hno hm => hno _ u (TransGen.single hh) (Or.inl rfl) hh
      (not_stated_not_member L P u k hu)
      ⟨((mem_iff L P _ k).1 hm).1, ((mem_iff L P _ k).1 hm).2.1⟩
  | @tail c d' hl' hcd ih =>
    intro hno hm
    have hc : ¬ mem L P c k := ih (fun w h a b => hno w h a
      (Or.inr (b.elim (fun e => e ▸ TransGen.single hcd) (fun t => TransGen.tail t hcd))))
    exact hno d' c (TransGen.tail hl' hcd) (Or.inl rfl) hcd hc
      ⟨((mem_iff L P d' k).1 hm).1, ((mem_iff L P d' k).1 hm).2.1⟩

/-- (4) THE CONCESSION, stated: a key that is a member at an older head `h0` is a voice of a
    version that names only `h0`, whatever versions below `h0` removed it (by definition).
    Those removals are not in that version's past, and by (2) change nothing for it. This is
    "an adversary holding the count of an old head signs a valid version alone"; waiting tips
    and a witnessed lineage answer it, and neither is in this file. -/
theorem old_head_still_counts (P : Row → Prop) (h0 v : Row) (k : Key)
    (hh : hd L h0 v) (honly : ∀ h, hd L h v → h = h0) (hm : mem L P h0 k)
    (hnl : ¬ left L P v k) : voters L P v k :=
  ⟨Or.inl ⟨⟨h0, hh⟩, fun h hh' => honly h hh' ▸ hm⟩, hnl⟩

/-! ### A leaving binds by causal past -/

/-- A LEAVING BINDS BY CAUSAL PAST. A version with `k`'s own withdrawal from the lineage in its
    past does not count `k`, whatever `k` signs on it, and does not have `k` as a member; a
    version naming one head at which `k` is a member, without that withdrawal in its past,
    still counts `k` (by definition, both). -/
theorem leaving_binds_by_past (P : Row → Prop) (h v : Row) (k : Key) :
    (left L P v k → ¬ voters L P v k ∧ ¬ mem L P v k) ∧
      (hd L h v → (∀ h', hd L h' v → h' = h) → mem L P h k → ¬ left L P v k →
        voters L P v k) :=
  ⟨fun hl => ⟨fun hv => hv.2 hl, fun hm => ((mem_iff L P v k).1 hm).2.2 hl⟩,
   fun hh honly hm hnl => old_head_still_counts L P h v k hh honly hm hnl⟩

/-- A key's leaving in a head's past is in the past of every version naming that head. -/
theorem left_head (P : Row → Prop) (h v : Row) (k : Key) (hh : L.parent h v)
    (hl : left L P h k) : left L P v k :=
  let ⟨w, hw, rest⟩ := hl
  ⟨w, pastOrSelf_head L hh hw, rest⟩

/-! ### One signature never removes -/

/-- (6) ONE SIGNATURE NEVER REMOVES. Where the count asks two or more, a standing version that
    does not have `k` as a member, where `k` has not withdrawn by its own row, does not list
    `k` and carries the signatures of two distinct members at the heads it names. -/
theorem one_signature_never_removes (P : Row → Prop) (v : Row) (k : Key)
    (h2 : 2 ≤ L.need v) (hs : standsV L P v) (hn : ¬ mem L P v k) (hnl : ¬ left L P v k) :
    ¬ L.states v k ∧ ∃ k1 k2, k1 ≠ k2 ∧ L.cosigns v k1 ∧ L.cosigns v k2 ∧
      voters L P v k1 ∧ voters L P v k2 := by
  refine ⟨fun hst => hn ((mem_iff L P v k).2 ⟨hs, hst, hnl⟩), ?_⟩
  have ⟨_, ⟨_, l, hnd, hlen, hl⟩, _⟩ := hs
  match l, hnd, hlen, hl with
  | [], _, hlen, _ => exact absurd (Nat.le_trans h2 hlen) (Nat.not_succ_le_zero 1)
  | [_], _, hlen, _ => exact absurd (Nat.le_trans h2 hlen) (Nat.not_succ_le_self 1)
  | a :: b :: _, hnd, _, hl =>
    have ha := hl a (List.mem_cons_self _ _)
    have hb := hl b (List.mem_cons_of_mem _ (List.mem_cons_self _ _))
    exact ⟨a, b, fun e => (List.nodup_cons.1 hnd).1 (e ▸ List.mem_cons_self _ _),
      ha.2, hb.2, ha.1, hb.1⟩

/-- (6) So rows by one key `j` alone, other than `k`'s own withdrawal, never take `k` out:
    if every member signature on `v` is `j`'s, `v` does not stand. -/
theorem one_key_alone_stands_nothing (P : Row → Prop) (v : Row) (j : Key) (h2 : 2 ≤ L.need v)
    (hone : ∀ k', L.cosigns v k' → voters L P v k' → k' = j) : ¬ standsV L P v :=
  fun ⟨_, hb, _⟩ => Consent.one_voice_is_not_a_count (fun t k => voters L P t k) L.need
    L.cosigns P v v h2 (fun k k' hk hk' hc hc' => (hone k hc hk).trans (hone k' hc' hk').symm) hb

/-! ### Several heads -/

/-- (5) A version naming several heads is counted over the members common to them: given a list
    of its heads and a list of the members at each, the voices are `Merge.common` of them. -/
theorem voters_is_common [DecidableEq Key] (P : Row → Prop) (v : Row)
    (hs : List Row) (ml : Row → List Key)
    (hheads : ∀ h, h ∈ hs ↔ hd L h v) (hne : hs ≠ [])
    (hml : ∀ h, hd L h v → ∀ k, k ∈ ml h ↔ mem L P h k) (k : Key) :
    voters L P v k ↔ k ∈ Merge.common ml hs ∧ ¬ left L P v k := by
  rw [Merge.mem_common]
  refine ⟨fun hx => ⟨?_, hx.2⟩, fun hx => ⟨?_, hx.2⟩⟩
  · have h := hx.1
    cases h with
    | inl h => exact ⟨hne, fun h' hm => (hml h' ((hheads h').1 hm) k).2 (h.2 h' ((hheads h').1 hm))⟩
    | inr h =>
      cases hs with
      | nil => exact absurd rfl hne
      | cons x _ => exact absurd ⟨x, (hheads x).1 (List.mem_cons_self _ _)⟩ h.1
  · have ⟨_, h⟩ := hx.1
    cases hs with
    | nil => exact absurd rfl hne
    | cons x _ =>
      exact Or.inl ⟨⟨x, (hheads x).1 (List.mem_cons_self _ _)⟩,
        fun h' hh => (hml h' hh k).1 (h h' ((hheads h').2 hh))⟩

/-! ## The second rejected rule: a leaving that reaches back

  `Seat.withdrawn` and `Consent.holderYes` read every held withdrawal, which is right for the
  derived answer of whether a seat is live (seat.py's `stands`). Read into the members at a head,
  it would let a key's leaving, held after the head, change the members there. The running
  model reads the members at a head from the head's past only (seat.py `members_at`), and that
  is the rule above. The retroactive reading is kept here, with where the two agree and a model
  of where they differ. Seat.lean is not changed. -/

namespace Retro

/-- `k` has withdrawn from the lineage by a row held anywhere. -/
def leftAny (P : Row → Prop) (k : Key) : Prop :=
  ∃ w, P w ∧ L.isWd w ∧ L.signer w = k ∧ ∃ u, L.isVer u ∧ L.parent u w

/-- The retroactive reading of the members at a version. -/
def memRetro (P : Row → Prop) (v : Row) (k : Key) : Prop :=
  standsV L P v ∧ L.states v k ∧ ¬ leftAny L P k

/-- The two agree wherever every leaving of `k` that is held is in the version's past. -/
theorem retro_agrees (P : Row → Prop) (v : Row) (k : Key)
    (hall : ∀ w, P w → L.isWd w → L.signer w = k → (∃ u, L.isVer u ∧ L.parent u w) →
      pastOrSelf L w v) :
    mem L P v k ↔ memRetro L P v k := by
  rw [mem_iff]
  have e : left L P v k ↔ leftAny L P k :=
    ⟨fun ⟨w, _, h1, h2⟩ => ⟨w, h1, h2⟩,
     fun ⟨w, h1, h2, h3, h4⟩ => ⟨w, hall w h1 h2 h3 h4, h1, h2, h3, h4⟩⟩
  exact ⟨fun ⟨a, b, c⟩ => ⟨a, b, fun x => c (e.2 x)⟩, fun ⟨a, b, c⟩ => ⟨a, b, fun x => c (e.1 x)⟩⟩

namespace Model

inductive K | a | b deriving DecidableEq

/-- `h` a genesis version signed by `b`, listing `a` and `b`; `w` `a`'s leaving, naming `h`. -/
inductive R | h | w deriving DecidableEq

def parent (p r : R) : Prop := p = .h ∧ r = .w

def depth : R → Nat
  | .h => 0 | .w => 1

theorem parent_depth : ∀ p r, parent p r → depth p < depth r := by
  intro p r hp
  have ⟨e1, e2⟩ := hp
  subst e1; subst e2
  exact Nat.zero_lt_one

theorem parent_wf : WellFounded parent :=
  Subrelation.wf (fun {p r} h => parent_depth p r h) (InvImage.wf depth Nat.lt_wfRel.wf)

def LM : Lineage R K where
  parent := parent
  wf := parent_wf
  signer := fun | .h => .b | .w => .a
  isWd := fun r => r = .w
  isVer := fun r => r = .h
  isAcc := fun _ => False
  cosigns := fun r k => r = .h ∧ k = .b
  states := fun _ _ => True
  base := fun _ k => k = .b
  need := fun _ => 1
  holder := fun _ => .b

def All (_ : R) : Prop := True

theorem past_h (x : R) (hx : pastOrSelf LM x .h) : x = .h :=
  hx.elim id (fun t => by
    cases t with
    | single hp => exact nomatch hp.2
    | tail _ hp => exact nomatch hp.2)

theorem not_left_h (k : K) : ¬ left LM All .h k :=
  fun ⟨x, hx, _, hw, _⟩ => by rw [past_h x hx] at hw; exact nomatch hw

theorem h_stands : standsV LM All .h := by
  refine ⟨rfl, ⟨trivial, [.b], List.Pairwise.cons (fun _ h => nomatch h) List.Pairwise.nil,
    Nat.le_refl 1, fun k hk => ?_⟩, Or.inl ⟨rfl, rfl⟩⟩
  have e : k = .b := List.mem_singleton.1 hk
  subst e
  exact ⟨show voters LM All .h .b from
    ⟨Or.inr ⟨fun ⟨_, _, hp⟩ => (nomatch hp.2), rfl⟩, not_left_h _⟩, rfl, rfl⟩

/-- `a`'s leaving `w` is not in `h`'s past. The rule taken keeps `a` a member at `h`; the
    retroactive reading takes it out. -/
theorem retro_reaches_back :
    ¬ pastOrSelf LM .w .h ∧ mem LM All .h .a ∧ ¬ memRetro LM All .h .a :=
  ⟨fun hx => (nomatch past_h _ hx),
   (mem_iff LM All .h .a).2 ⟨h_stands, trivial, not_left_h _⟩,
   fun ⟨_, _, hn⟩ => hn ⟨.w, trivial, rfl, rfl, .h, rfl, rfl, rfl⟩⟩

end Model

end Retro

/-! ## The rejected rule, kept to show why

  A body's voices as separate rows tied to the version, each withdrawable by its signer
  (`Consent.Rejected.standsCountedW`). The two models below are what it allowed. Under the rule
  above neither can happen: `w` is in the past of neither head, so by `rows_outside_change_nothing`
  it changes nothing. -/

namespace Rejected

/-- The data of a lineage. `parent p r`: row `r` names row `p`; well-founded. `isVer`: a
    version of this roster. `ans`: a row given in answer to the row it names (a cosignature, the
    holder's acceptance). `states v k`: version `v` lists `k`. `base v k`: `k` is a voice of the
    count of `v` when `v` names no head. `need v`: the count `v`'s protocol asks. `holder v`:
    the key that carries `v` (a joiner, or the proposer). -/
structure LineageW (Row Key : Type) where
  parent : Row → Row → Prop
  wf : WellFounded parent
  signer : Row → Key
  isWd : Row → Prop
  isVer : Row → Prop
  ans : Row → Prop
  states : Row → Key → Prop
  base : Row → Key → Prop
  need : Row → Nat
  holder : Row → Key

variable {Row Key : Type} (L : LineageW Row Key)



/-- `v` names the version `h` as a head. -/
def hdW (h v : Row) : Prop := L.isVer h ∧ L.parent h v

/-- `a` is tied to `o`: `o` itself, or an answer naming it (`Consent.tied`). -/
def tiedToW (o a : Row) : Prop := Consent.tied L.parent L.ans o a

/-- The voices over which `v` is counted, given the members `M` at each version: the keys
    that are members at every head `v` names, or, at a genesis, its `base`. -/
def votersOfW (M : Row → Key → Prop) (v : Row) (k : Key) : Prop :=
  ((∃ h, hdW L h v) ∧ ∀ h, hdW L h v → M h k) ∨ ((¬ ∃ h, hdW L h v) ∧ L.base v k)

/-- Version `v` stands over the voices `M`: it is a version, and `Consent.Rejected.standsCountedW` holds
    with the version as the root, its count over `M` and its holder's own consent. -/
def stVW (M : Key → Prop) (P W : Row → Prop) (cut : Row → Row → Prop) (v : Row) : Prop :=
  L.isVer v ∧ Consent.Rejected.standsCountedW L.parent L.signer L.isWd (fun o t => o = t) L.ans
    (fun _ k => M k) L.need L.holder P W cut v v

/-- The members at each version, by recursion on what rows name. -/
noncomputable def memW (P W : Row → Prop) (cut : Row → Row → Prop) : Row → Key → Prop :=
  L.wf.fix (C := fun _ => Key → Prop) (fun v ih k =>
    stVW L (fun k' => ((∃ h, hdW L h v) ∧ ∀ h (hh : hdW L h v), ih h hh.2 k') ∨
      ((¬ ∃ h, hdW L h v) ∧ L.base v k')) P W cut v ∧ L.states v k)

/-- The voices of `v`'s count. -/
def votersW (P W : Row → Prop) (cut : Row → Row → Prop) (v : Row) (k : Key) : Prop :=
  votersOfW L (memW L P W cut) v k

/-- Version `v` stands. -/
def standsVW (P W : Row → Prop) (cut : Row → Row → Prop) (v : Row) : Prop :=
  stVW L (votersW L P W cut v) P W cut v

/-- The defining equation (by definition). -/
theorem memW_iff (P W : Row → Prop) (cut : Row → Row → Prop) (v : Row) (k : Key) :
    memW L P W cut v k ↔ standsVW L P W cut v ∧ L.states v k := by
  unfold memW
  rw [WellFounded.fix_eq]
  exact Iff.rfl


namespace Model

inductive K | a | b deriving DecidableEq

/-- `h` a genesis version signed by `b`, listing `a` and `b`; `v` a version by `a` naming `h`,
    listing `a`; `w` `b`'s withdrawal of `h`. -/
inductive R | h | v | w deriving DecidableEq

def parentB : R → R → Bool
  | .h, .v => true
  | .h, .w => true
  | _, _ => false

def parent (p r : R) : Prop := parentB p r = true

def depth : R → Nat
  | .h => 0 | .v => 1 | .w => 1

theorem parent_depth : ∀ p r, parent p r → depth p < depth r := by
  intro p r
  cases p <;> cases r <;> simp [parent, parentB, depth]

theorem parent_wf : WellFounded parent :=
  Subrelation.wf (fun {p r} h => parent_depth p r h) (InvImage.wf depth Nat.lt_wfRel.wf)

def LM : LineageW R K where
  parent := parent
  wf := parent_wf
  signer := fun | .h => .b | .v => .a | .w => .b
  isWd := fun r => r = .w
  isVer := fun r => r = .h ∨ r = .v
  ans := fun _ => False
  states := fun | .h => (fun _ => True) | .v => (fun k => k = .a) | .w => (fun _ => False)
  base := fun | .h => (fun k => k = .b) | _ => (fun _ => False)
  need := fun _ => 1
  holder := fun | .h => .b | .v => .a | .w => .b

theorem no_parent_h (c : R) : ¬ parent c .h := by cases c <;> simp [parent, parentB]

theorem not_anc_h (x : R) : ¬ TransGen parent x .h := fun t => by
  cases t with
  | single hp => exact no_parent_h _ hp
  | tail _ hp => exact no_parent_h _ hp

theorem not_anc_wv : ¬ TransGen parent .w .v := fun t => by
  cases t with
  | single hp => exact nomatch hp
  | @tail c _ hc hp =>
    cases c with
    | h => exact not_anc_h _ hc
    | v => exact nomatch hp
    | w => exact nomatch hp

def S1 (r : R) : Prop := r = .h ∨ r = .v
def S2 (_ : R) : Prop := True
def noCut (_ _ : R) : Prop := False

theorem tied_self {o x : R} (h : tiedToW LM o x) : x = o :=
  h.elim (fun x => x.1.elim) id

theorem no_head_h : ¬ ∃ x, hdW LM x .h := fun ⟨x, _, hp⟩ => by cases x <;> exact nomatch hp

theorem hd_v (x : R) : hdW LM x .v ↔ x = .h := by
  constructor
  · intro ⟨_, hp⟩; cases x <;> first | rfl | exact nomatch hp
  · intro e; subst e; exact ⟨Or.inl rfl, rfl⟩

theorem not_wd_S1 (x : R) (_ : S1 x) : ¬ withdrawn LM.parent LM.signer LM.isWd S1 x :=
  fun ⟨y, ⟨hy, _, _⟩, hs⟩ => by
    subst hy; exact hs.elim (fun e => nomatch e) (fun e => nomatch e)

theorem wd_h : withdrawn LM.parent LM.signer LM.isWd S2 .h := ⟨.w, ⟨rfl, rfl, rfl⟩, trivial⟩

theorem h_stands_S1 : standsVW LM S1 S1 noCut .h := by
  refine ⟨Or.inl rfl, Or.inl rfl, rfl, id, ⟨[.h], List.pairwise_singleton _ _, Nat.le_refl 1, ?_⟩,
    ⟨.h, Or.inl rfl, rfl, trivial, Or.inr rfl, not_wd_S1 _ (Or.inl rfl)⟩⟩
  intro x hx
  have e : x = .h := List.mem_singleton.1 hx
  subst e
  exact ⟨Or.inl rfl, Or.inr ⟨no_head_h, rfl⟩, Or.inr rfl, not_wd_S1 _ (Or.inl rfl)⟩

theorem h_falls_S2 : ¬ standsVW LM S2 S2 noCut .h := by
  intro ⟨_, _, _, _, _, ⟨x, _, _, _, hx, hn⟩⟩
  have e := tied_self hx
  subst e
  exact hn wd_h

/-- (a) Members at `h` with and without `w`. `w` names `h` and is not in its past. -/
theorem later_withdrawal_changes_members :
    ¬ TransGen LM.parent .w .h ∧ memW LM S1 S1 noCut .h .b ∧ ¬ memW LM S2 S2 noCut .h .b := by
  exact ⟨not_anc_h _, (memW_iff LM _ _ _ _ _).2 ⟨h_stands_S1, trivial⟩,
    fun hm => h_falls_S2 ((memW_iff LM _ _ _ _ _).1 hm).1⟩

/-- (b) `v` stands without `w` and does not with it. `w` is not in `v`'s past, is tied to no row,
    and its signer `b` signed no row tied to `v`: `w` withdraws a row tied to `v`'s head. -/
theorem head_withdrawal_ends_version :
    ¬ TransGen LM.parent .w .v ∧ (∀ x, tiedToW LM .v x → LM.signer x ≠ .b) ∧
      standsVW LM S1 S1 noCut .v ∧ ¬ standsVW LM S2 S2 noCut .v := by
  refine ⟨not_anc_wv, fun x hx => by rw [tied_self hx]; exact nofun, ?_, ?_⟩
  · refine ⟨Or.inr rfl, Or.inr rfl, rfl, id,
      ⟨[.v], List.pairwise_singleton _ _, Nat.le_refl 1, ?_⟩,
      ⟨.v, Or.inr rfl, rfl, trivial, Or.inr rfl, not_wd_S1 _ (Or.inr rfl)⟩⟩
    intro x hx
    have e : x = .v := List.mem_singleton.1 hx
    subst e
    refine ⟨Or.inr rfl, Or.inl ⟨⟨.h, (hd_v .h).2 rfl⟩, fun y hy => ?_⟩, Or.inr rfl,
      not_wd_S1 _ (Or.inr rfl)⟩
    rw [(hd_v y).1 hy]
    exact (memW_iff LM _ _ _ _ _).2 ⟨h_stands_S1, trivial⟩
  · intro ⟨_, _, _, _, ⟨l, _, hlen, hl⟩, _⟩
    match l, hlen, hl with
    | [], hlen, _ => exact absurd hlen (Nat.not_succ_le_zero 0)
    | x :: _, _, hl =>
      have ⟨_, hv, _⟩ := hl x (List.mem_cons_self _ _)
      cases hv with
      | inl hv => exact h_falls_S2 ((memW_iff LM _ _ _ _ _).1 (hv.2 .h ((hd_v .h).2 rfl))).1
      | inr hv => exact hv.1 ⟨.h, (hd_v .h).2 rfl⟩

end Model

end Rejected

end RosterHead

#print axioms RosterHead.mem_iff
#print axioms RosterHead.mem_congr
#print axioms RosterHead.membersAt_function
#print axioms RosterHead.counted_over_named_head
#print axioms RosterHead.rows_outside_change_nothing
#print axioms RosterHead.standing_final
#print axioms RosterHead.no_self_admission
#print axioms RosterHead.outsiders_admit_nothing
#print axioms RosterHead.not_stated_not_member
#print axioms RosterHead.not_member_at_head
#print axioms RosterHead.removed_voice_does_not_count
#print axioms RosterHead.readmission_needed
#print axioms RosterHead.old_head_still_counts
#print axioms RosterHead.one_signature_never_removes
#print axioms RosterHead.one_key_alone_stands_nothing
#print axioms RosterHead.voters_is_common
#print axioms RosterHead.leaving_binds_by_past
#print axioms RosterHead.left_head
#print axioms RosterHead.Retro.retro_agrees
#print axioms RosterHead.Retro.Model.retro_reaches_back
#print axioms RosterHead.Rejected.Model.later_withdrawal_changes_members
#print axioms RosterHead.Rejected.Model.head_withdrawal_ends_version

end Kernel
